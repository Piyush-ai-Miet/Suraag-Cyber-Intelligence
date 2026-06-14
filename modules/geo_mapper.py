"""
modules/geo_mapper.py — Suराग IP Geolocation & Folium Map
Uses ip-api.com (free, no key) to geolocate IPs and render Folium maps.
Enhanced with: dark tiles, connection lines, suspect-IP linking, legend.
"""

import time
import requests
import pandas as pd
import folium
import streamlit as st
from folium.plugins import MarkerCluster, AntPath
from config import GEO_API_URL, COLOR_ACCENT, COLOR_CRITICAL

# ── Known private/local IP prefixes to skip ──────────────
SKIP_PREFIXES = ["10.", "192.168.", "172.", "127.", "0.", "::1"]

# ── Suspect color palette for connection lines ───────────
SUSPECT_COLORS = [
    "#00D4FF",  # Cyan
    "#FF8C00",  # Orange
    "#3FB950",  # Green
    "#FF4444",  # Red
    "#9B59B6",  # Purple
    "#E74C3C",  # Crimson
    "#F1C40F",  # Gold
    "#1ABC9C",  # Teal
]


def is_private_ip(ip: str) -> bool:
    """Check if IP is private/local. Handles both string and float/numeric IPs."""
    # Convert to string if it's a number
    ip_str = str(ip) if not isinstance(ip, str) else ip
    return any(ip_str.startswith(p) for p in SKIP_PREFIXES)


@st.cache_data(show_spinner=False, ttl=3600)
def geolocate_ips(ip_list: tuple) -> dict:
    """
    Geolocate a tuple of unique IPs using ip-api.com.
    Returns dict: {ip: {country, city, isp, lat, lon, is_proxy, is_hosting}}
    Results are cached for 1 hour.
    """
    results = {}
    # Convert all IPs to strings
    ips_to_query = [str(ip) for ip in ip_list if not is_private_ip(str(ip))]

    for ip in ips_to_query:
        if ip in results:
            continue
        try:
            url = GEO_API_URL.format(ip=ip)
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    results[ip] = {
                        "country":     data.get("country", "Unknown"),
                        "region":      data.get("regionName", ""),
                        "city":        data.get("city", "Unknown"),
                        "isp":         data.get("isp", "Unknown"),
                        "lat":         data.get("lat", 0.0),
                        "lon":         data.get("lon", 0.0),
                        "is_proxy":    data.get("proxy", False),
                        "is_hosting":  data.get("hosting", False),
                    }
                else:
                    results[ip] = None
            time.sleep(0.05)  # Rate limit: max 1000 req/min
        except Exception:
            results[ip] = None

    return results


def _get_pin_color(row: pd.Series, geo_data: dict) -> str:
    """
    Determine map pin color:
    Red    = Foreign server
    Orange = Tor exit node / proxy
    Blue   = Normal Indian IP
    """
    ip = str(row["Destination_IP"])  # Ensure IP is string
    is_tor = bool(row.get("Is_TOR", False))
    is_foreign = bool(row.get("Is_Foreign_IP", False))
    geo = geo_data.get(ip)

    if is_tor or (geo and (geo.get("is_proxy") or geo.get("is_hosting"))):
        return "orange"
    if is_foreign or (geo and geo.get("country") != "India"):
        return "red"
    return "blue"


def _build_legend_html() -> str:
    """Build a professional HTML legend overlay for the map."""
    return """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid rgba(0, 212, 255, 0.6);
        border-radius: 12px;
        padding: 14px 18px;
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        max-width: 220px;
    ">
        <p style="margin:0 0 10px 0;font-weight:700;font-size:12px;color:#00A8CC;
                  text-transform:uppercase;letter-spacing:1px;
                  border-bottom:2px solid #00D4FF;padding-bottom:6px">
            🗺️ Map Legend
        </p>
        <div style="display:flex;align-items:center;margin:6px 0">
            <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                        background:#3388ff;margin-right:8px;border:2px solid #5599ff"></span>
            <span style="font-size:11px;color:#2c3e50">Indian Server (Normal)</span>
        </div>
        <div style="display:flex;align-items:center;margin:6px 0">
            <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                        background:#FF4444;margin-right:8px;border:2px solid #FF6666"></span>
            <span style="font-size:11px;color:#2c3e50">Foreign Server</span>
        </div>
        <div style="display:flex;align-items:center;margin:6px 0">
            <span style="display:inline-block;width:14px;height:14px;border-radius:50%;
                        background:#FF8C00;margin-right:8px;border:2px solid #FFAA33"></span>
            <span style="font-size:11px;color:#2c3e50">Tor / Proxy Node</span>
        </div>
        <div style="display:flex;align-items:center;margin:6px 0">
            <span style="display:inline-block;width:14px;height:14px;border-radius:3px;
                        background:#00D4FF;margin-right:8px;border:2px solid #33DDFF"></span>
            <span style="font-size:11px;color:#2c3e50">Suspect Location</span>
        </div>
        <div style="display:flex;align-items:center;margin:6px 0">
            <span style="display:inline-block;width:20px;height:3px;
                        background:linear-gradient(90deg,#00D4FF,#FF4444);
                        margin-right:8px;border-radius:2px"></span>
            <span style="font-size:11px;color:#2c3e50">Connection Link</span>
        </div>
    </div>
    """


@st.cache_data(show_spinner=False)
def build_geo_map(df: pd.DataFrame) -> tuple:
    """
    Build Folium map with colored markers, suspect nodes, and connection lines.
    Shows how suspects are linked to destination IPs via animated arcs.
    Returns (folium.Map, summary_dict).
    """
    try:
        # Validate DataFrame
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None")
        
        # Check required columns
        required_cols = ["Destination_IP", "Subscriber_ID", "Subscriber_Name"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure Destination_IP is string type
        df = df.copy()
        df["Destination_IP"] = df["Destination_IP"].astype(str)
        
        # Get unique IPs
        unique_ips = tuple(df["Destination_IP"].unique().tolist())
        if len(unique_ips) == 0:
            raise ValueError("No valid IP addresses found")
            
        geo_data   = geolocate_ips(unique_ips)
    except Exception as e:
        st.error(f"Error initializing map data: {str(e)}")
        # Return a simple default map
        m = folium.Map(location=[22.5, 78.9629], zoom_start=5)
        return m, {"indian": 0, "foreign": 0, "tor": 0, "total": 0}

    # Aggregate per IP
    try:
        ip_agg = (
            df.groupby("Destination_IP")
            .agg(
                sessions     = ("Timestamp",        "count"),
                total_bytes  = ("Data_Volume_Bytes", "sum"),
                is_tor       = ("Is_TOR",            "any"),
                is_foreign   = ("Is_Foreign_IP",     "any"),
            )
            .reset_index()
        )
        
        if ip_agg.empty:
            raise ValueError("IP aggregation resulted in empty DataFrame")
    except Exception as e:
        st.error(f"Error aggregating IP data: {str(e)}")
        m = folium.Map(location=[22.5, 78.9629], zoom_start=5)
        return m, {"indian": 0, "foreign": 0, "tor": 0, "total": 0}

    # ── Build suspect location mapping ───────────────────
    suspect_locs = {}
    for sub_id in df["Subscriber_ID"].unique():
        sub_df = df[df["Subscriber_ID"] == sub_id]
        
        # Check if sub_df is not empty before accessing
        if sub_df.empty:
            continue
            
        name = sub_df["Subscriber_Name"].iloc[0] if len(sub_df) > 0 else "Unknown"
        city = sub_df["City"].iloc[0] if "City" in sub_df.columns and len(sub_df) > 0 else "Unknown"
        lat  = sub_df["Latitude"].iloc[0] if "Latitude" in sub_df.columns and len(sub_df) > 0 else 20.5937
        lon  = sub_df["Longitude"].iloc[0] if "Longitude" in sub_df.columns and len(sub_df) > 0 else 78.9629
        
        # Convert to float safely
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            lat, lon = 20.5937, 78.9629
        
        suspect_locs[sub_id] = {
            "name": name, "city": city,
            "lat": lat, "lon": lon,
        }

    # ── Build suspect → IP edges (aggregated) ────────────
    try:
        edges = (
            df.groupby(["Subscriber_ID", "Destination_IP"])
            .agg(
                sessions    = ("Timestamp",        "count"),
                total_bytes = ("Data_Volume_Bytes", "sum"),
                is_tor      = ("Is_TOR",            "any"),
                is_foreign  = ("Is_Foreign_IP",     "any"),
            )
            .reset_index()
        )
    except Exception as e:
        st.warning(f"Could not build connection edges: {str(e)}")
        edges = pd.DataFrame()

    # Create map centered on India with realistic Google-style tiles
    m = folium.Map(
        location=[22.5, 78.9629],
        zoom_start=5,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
        control_scale=True,
    )
    
    # Add alternative tile layers for user to switch between
    # Satellite view (Google Satellite)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="🛰️ Satellite View",
        overlay=False,
        control=True
    ).add_to(m)
    
    # Hybrid view (Satellite + Roads/Labels)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Hybrid",
        name="🗺️ Hybrid (Satellite + Roads)",
        overlay=False,
        control=True
    ).add_to(m)
    
    # Terrain view
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr="Google Terrain",
        name="⛰️ Terrain View",
        overlay=False,
        control=True
    ).add_to(m)
    
    # Traffic Layer (optional overlay)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=h,traffic&x={x}&y={y}&z={z}",
        attr="Google Traffic",
        name="🚦 Traffic Overlay",
        overlay=True,
        control=True,
        opacity=0.6
    ).add_to(m)

    # ── Add Suspect Location Markers (cyan pulsing) ──────
    suspects_group = folium.FeatureGroup(name="👤 Suspect Locations", show=True)
    sub_ids = list(suspect_locs.keys())

    for idx, (sub_id, info) in enumerate(suspect_locs.items()):
        color = SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]
        total_sessions = len(df[df["Subscriber_ID"] == sub_id])
        tor_count = int(df[df["Subscriber_ID"] == sub_id]["Is_TOR"].sum())
        foreign_count = int(df[df["Subscriber_ID"] == sub_id]["Is_Foreign_IP"].sum())

        # Pulsing circle for suspect
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=14,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.3,
            weight=3,
            popup=folium.Popup(f"""
            <div style="font-family:Inter,sans-serif;min-width:220px;background:#0D1117;
                        color:#E6EDF3;border-radius:10px;padding:14px;border:1px solid #30363D">
                <div style="display:flex;align-items:center;margin-bottom:8px">
                    <span style="font-size:20px;margin-right:8px">👤</span>
                    <b style="color:{color};font-size:15px">{info['name']}</b>
                </div>
                <hr style="border-color:#30363D;margin:6px 0">
                <table style="width:100%;font-size:12px;color:#E6EDF3">
                    <tr><td style="color:#8B949E;padding:3px 0">ID</td>
                        <td style="text-align:right"><code style="color:#00D4FF">{sub_id[-12:]}</code></td></tr>
                    <tr><td style="color:#8B949E;padding:3px 0">City</td>
                        <td style="text-align:right">{info['city']}</td></tr>
                    <tr><td style="color:#8B949E;padding:3px 0">Sessions</td>
                        <td style="text-align:right;font-weight:700">{total_sessions:,}</td></tr>
                    <tr><td style="color:#FF8C00;padding:3px 0">Tor Sessions</td>
                        <td style="text-align:right;color:#FF8C00;font-weight:700">{tor_count}</td></tr>
                    <tr><td style="color:#FF4444;padding:3px 0">Foreign IPs</td>
                        <td style="text-align:right;color:#FF4444;font-weight:700">{foreign_count}</td></tr>
                </table>
            </div>
            """, max_width=280),
            tooltip=f"👤 {info['name']} — {info['city']}",
        ).add_to(suspects_group)

        # Pulsing outer ring (animation effect via larger circle)
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=22,
            color=color,
            fill=False,
            weight=1,
            opacity=0.4,
        ).add_to(suspects_group)

    suspects_group.add_to(m)

    # ── Add IP Destination Markers (clustered) ───────────
    ip_cluster = MarkerCluster(name="🌐 Destination IPs", show=True).add_to(m)

    indian_count  = 0
    foreign_count = 0
    tor_count     = 0
    ip_locations  = {}  # Store IP → (lat, lon) for line drawing

    for _, row in ip_agg.iterrows():
        ip  = row["Destination_IP"]
        geo = geo_data.get(ip)

        if geo is None:
            lat, lon = 20.5937, 78.9629
            city, isp, country = "Unknown", "Unknown", "Unknown"
        else:
            lat     = geo["lat"]
            lon     = geo["lon"]
            city    = geo["city"]
            isp     = geo["isp"]
            country = geo["country"]

        ip_locations[ip] = (lat, lon)
        color = _get_pin_color(row, geo_data)

        if color == "orange":
            tor_count += 1
        elif color == "red":
            foreign_count += 1
        else:
            indian_count += 1

        sessions_fmt  = f"{int(row['sessions']):,}"
        bytes_mb      = row["total_bytes"] / 1_048_576

        # Find which suspects connect to this IP
        suspects_using = df[df["Destination_IP"] == ip]["Subscriber_Name"].unique().tolist()
        suspects_html = "".join(
            f"<span style='display:inline-block;background:#00D4FF22;color:#00D4FF;"
            f"border:1px solid #00D4FF44;border-radius:4px;padding:1px 6px;"
            f"margin:2px;font-size:10px'>{s}</span>"
            for s in suspects_using
        )

        # Risk indicator
        risk_icon = "⚠️" if color == "orange" else ("🌍" if color == "red" else "✅")
        risk_label = "TOR/PROXY" if color == "orange" else ("FOREIGN" if color == "red" else "DOMESTIC")
        risk_color = "#FF8C00" if color == "orange" else ("#FF4444" if color == "red" else "#3FB950")

        popup_html = f"""
        <div style="font-family:Inter,sans-serif;min-width:240px;background:#0D1117;
                    color:#E6EDF3;border-radius:10px;padding:14px;border:1px solid #30363D">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <b style="color:#00D4FF;font-size:14px">{ip}</b>
                <span style="background:{risk_color}22;color:{risk_color};
                      border:1px solid {risk_color}44;border-radius:4px;
                      padding:2px 6px;font-size:9px;font-weight:700">{risk_icon} {risk_label}</span>
            </div>
            <hr style="border-color:#30363D;margin:8px 0">
            <table style="width:100%;font-size:12px;color:#E6EDF3">
                <tr><td style="color:#8B949E;padding:3px 0">Location</td>
                    <td style="text-align:right">{city}, {country}</td></tr>
                <tr><td style="color:#8B949E;padding:3px 0">ISP</td>
                    <td style="text-align:right">{isp}</td></tr>
                <tr><td style="color:#8B949E;padding:3px 0">Sessions</td>
                    <td style="text-align:right;font-weight:700">{sessions_fmt}</td></tr>
                <tr><td style="color:#8B949E;padding:3px 0">Data</td>
                    <td style="text-align:right">{bytes_mb:.1f} MB</td></tr>
            </table>
            <hr style="border-color:#30363D;margin:8px 0">
            <p style="color:#8B949E;font-size:10px;margin:0 0 4px 0;text-transform:uppercase;
                      letter-spacing:0.5px">Connected Suspects:</p>
            <div>{suspects_html}</div>
        </div>
        """

        icon_color = {"red": "red", "orange": "orange", "blue": "blue"}.get(color, "blue")
        icon_name  = "exclamation-sign" if color != "blue" else "info-sign"

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{ip} — {city}, {country}",
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix="glyphicon"),
        ).add_to(ip_cluster)

    # ── Draw Connection Lines (Suspect → IP) ─────────────
    connections_group = folium.FeatureGroup(name="🔗 Connection Links", show=True)

    if not edges.empty:
        for idx, (sub_id, info) in enumerate(suspect_locs.items()):
            color = SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]
            sub_edges = edges[edges["Subscriber_ID"] == sub_id]

            for _, edge_row in sub_edges.iterrows():
                dest_ip = str(edge_row["Destination_IP"])
                if dest_ip not in ip_locations:
                    continue

                ip_lat, ip_lon = ip_locations[dest_ip]

                # Skip if same location (would create a zero-length line)
                if abs(info["lat"] - ip_lat) < 0.01 and abs(info["lon"] - ip_lon) < 0.01:
                    continue

                sessions = int(edge_row["sessions"])
                is_tor_edge = bool(edge_row["is_tor"])
                is_foreign_edge = bool(edge_row["is_foreign"])

                # Line weight based on session count
                weight = max(1, min(sessions / 5, 6))

                # Line color: red for Tor, orange for foreign, suspect color for normal
                if is_tor_edge:
                    line_color = "#FF4444"
                    dash_array = "8 6"
                elif is_foreign_edge:
                    line_color = "#FF8C00"
                    dash_array = "6 4"
                else:
                    line_color = color
                    dash_array = None

                line_opts = {
                    "locations": [[info["lat"], info["lon"]], [ip_lat, ip_lon]],
                    "color": line_color,
                    "weight": weight,
                    "opacity": 0.45,
                    "tooltip": f"{info['name']} → {dest_ip} ({sessions} sessions)",
                }
                if dash_array:
                    line_opts["dash_array"] = dash_array

                folium.PolyLine(**line_opts).add_to(connections_group)

    connections_group.add_to(m)

    # ── Draw Shared IP Highlights (IPs used by 2+ suspects) ──
    shared_group = folium.FeatureGroup(name="⚠️ Shared IPs (Gang Evidence)", show=True)

    ip_to_suspects = (
        df.groupby("Destination_IP")["Subscriber_ID"]
        .apply(lambda x: list(set(x)))
        .to_dict()
    )

    for ip, subs in ip_to_suspects.items():
        if len(subs) < 2:
            continue
        if ip not in ip_locations:
            continue

        ip_lat, ip_lon = ip_locations[ip]
        geo = geo_data.get(ip)
        city = geo["city"] if geo else "Unknown"
        country = geo["country"] if geo else "Unknown"

        suspect_names = [suspect_locs[s]["name"] for s in subs if s in suspect_locs]

        # Pulsing red circle around shared IP
        folium.CircleMarker(
            location=[ip_lat, ip_lon],
            radius=18,
            color="#FF4444",
            fill=True,
            fill_color="#FF4444",
            fill_opacity=0.15,
            weight=3,
            tooltip=f"⚠️ SHARED IP: {ip} — Used by {', '.join(suspect_names)}",
            popup=folium.Popup(f"""
            <div style="font-family:Inter,sans-serif;min-width:220px;background:#0D1117;
                        color:#E6EDF3;border-radius:10px;padding:14px;
                        border:2px solid #FF4444">
                <p style="color:#FF4444;font-size:13px;font-weight:700;margin:0 0 6px 0">
                    ⚠️ SHARED GANG IP</p>
                <b style="color:#00D4FF;font-size:14px">{ip}</b><br>
                <span style="color:#8B949E;font-size:12px">{city}, {country}</span>
                <hr style="border-color:#30363D;margin:8px 0">
                <p style="color:#FF4444;font-size:11px;margin:0 0 4px 0">
                    Used by {len(subs)} suspects:</p>
                {"".join(f"<p style='color:#E6EDF3;font-size:12px;margin:2px 0'>▸ {n}</p>" for n in suspect_names)}
                <hr style="border-color:#30363D;margin:8px 0">
                <p style="color:#FF4444;font-size:10px;font-weight:600;margin:0">
                    🔗 STRONG GANG LINK EVIDENCE</p>
            </div>
            """, max_width=280),
        ).add_to(shared_group)

        # Outer glow ring
        folium.CircleMarker(
            location=[ip_lat, ip_lon],
            radius=28,
            color="#FF4444",
            fill=False,
            weight=1,
            opacity=0.25,
        ).add_to(shared_group)

    shared_group.add_to(m)

    # ── Layer Control & Legend ────────────────────────────
    folium.LayerControl(collapsed=False).add_to(m)

    # Add legend
    legend_element = folium.Element(_build_legend_html())
    m.get_root().html.add_child(legend_element)

    # ── Title overlay ────────────────────────────────────
    title_html = """
    <div style="
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid rgba(0, 212, 255, 0.6);
        border-radius: 10px;
        padding: 10px 24px;
        font-family: 'Inter', sans-serif;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    ">
        <span style="color:#00A8CC;font-size:16px;font-weight:700;letter-spacing:0.5px;text-shadow:0 2px 4px rgba(0,0,0,0.1)">
            🔍 Suराग — IP Geolocation Intelligence Map
        </span>
    </div>
    """
    title_element = folium.Element(title_html)
    m.get_root().html.add_child(title_element)

    summary = {
        "indian":  indian_count,
        "foreign": foreign_count,
        "tor":     tor_count,
        "total":   indian_count + foreign_count + tor_count,
    }
    return m, summary
