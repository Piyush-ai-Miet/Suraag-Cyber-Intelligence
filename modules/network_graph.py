"""
modules/network_graph.py — Suराग PyVis + NetworkX Network Graph
Builds a premium interactive node graph: suspects ↔ destination servers.
Professional forensic-grade visualization with dark theme, glowing nodes,
and intelligent layout.
"""

import os
import tempfile
import math
import networkx as nx
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from config import COLOR_BG, COLOR_ACCENT, COLOR_CRITICAL, COLOR_HIGH, COLOR_CARD, COLOR_BORDER, COLOR_TEXT, COLOR_MUTED

# ── Node Color Palette ────────────────────────────────────
SUSPECT_COLORS = ["#00D4FF", "#FF8C00", "#3FB950", "#E74C3C", "#9B59B6", "#F1C40F", "#1ABC9C", "#E91E63"]
SERVER_COLOR     = "#4A6FA5"   # Steel blue — normal servers
TOR_COLOR        = "#FF4444"   # Red — Tor nodes
FOREIGN_COLOR    = "#FF8C00"   # Orange — foreign servers
SHARED_COLOR     = "#FFFFFF"   # White — shared gang evidence
EDGE_DEFAULT     = "#1E2A3A"


@st.cache_data(show_spinner=False, hash_funcs={set: lambda x: len(x)})
def build_network_graph(df: pd.DataFrame, shared_ips: set = None) -> str:
    """
    Build professional PyVis network graph HTML.
    Suspect nodes are color-coded circles, server nodes are styled by type.
    Edge width = log-scaled data volume.
    Shared IP nodes (across suspects) are highlighted as gang evidence.
    Returns HTML string.
    """
    shared_ips = shared_ips or set()

    # Aggregate edges: (subscriber, dest_ip) → total bytes
    edge_agg = (
        df.groupby(["Subscriber_ID", "Destination_IP"])
        .agg(
            total_bytes  = ("Data_Volume_Bytes", "sum"),
            sessions     = ("Timestamp", "count"),
            is_tor       = ("Is_TOR", "any"),
            is_foreign   = ("Is_Foreign_IP", "any"),
        )
        .reset_index()
    )

    # Subscriber metadata
    sub_meta = df.groupby("Subscriber_ID").agg(
        name=("Subscriber_Name", "first"),
        city=("City", "first"),
        total_sessions=("Timestamp", "count"),
        tor_sessions=("Is_TOR", "sum"),
        foreign_sessions=("Is_Foreign_IP", "sum"),
        total_bytes=("Data_Volume_Bytes", "sum"),
    ).to_dict("index")

    sub_ids = list(sub_meta.keys())

    # Build NetworkX graph
    G = nx.Graph()

    # Add subscriber nodes
    for idx, (sub_id, meta) in enumerate(sub_meta.items()):
        G.add_node(
            sub_id,
            label=meta["name"],
            node_type="subscriber",
            sessions=meta["total_sessions"],
            city=meta["city"],
            tor=int(meta["tor_sessions"]),
            foreign=int(meta["foreign_sessions"]),
            total_bytes=int(meta["total_bytes"]),
            color_idx=idx,
        )

    # Add IP nodes + edges
    for _, row in edge_agg.iterrows():
        dest_ip = row["Destination_IP"]
        if dest_ip not in G:
            G.add_node(
                dest_ip,
                node_type="server",
                is_tor=bool(row["is_tor"]),
                is_foreign=bool(row["is_foreign"]),
            )
        edge_width = max(1.0, math.log1p(row["total_bytes"] / 1e6) * 2.5)
        G.add_edge(row["Subscriber_ID"], dest_ip,
                   weight=edge_width,
                   bytes=int(row["total_bytes"]),
                   sessions=int(row["sessions"]),
                   is_tor=bool(row["is_tor"]),
                   is_foreign=bool(row["is_foreign"]))

    # Degree centrality
    centrality = nx.degree_centrality(G)

    # Pre-compute layout coordinates for perfectly static display
    pos = nx.spring_layout(G, k=0.25, iterations=100, seed=42)

    # Build PyVis network
    net = Network(
        height="640px", width="100%",
        bgcolor="#0A0E14", font_color="#E6EDF3",
        notebook=False,
    )

    # ── Add Nodes ────────────────────────────────────────
    for node_id, attrs in G.nodes(data=True):
        ntype = attrs.get("node_type", "server")
        cent  = centrality.get(node_id, 0)

        if ntype == "subscriber":
            idx = attrs.get("color_idx", 0)
            color = SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]
            size  = 32 + cent * 50
            shape = "dot"
            border_width = 3
            name = attrs.get("label", node_id)
            city = attrs.get("city", "")
            sessions = attrs.get("sessions", 0)
            tor = attrs.get("tor", 0)
            foreign = attrs.get("foreign", 0)
            total_bytes = attrs.get("total_bytes", 0)
            data_mb = total_bytes / 1_048_576

            # Get phone number if available
            phone = ""
            if "Phone_Number" in df.columns:
                phone_data = df[df["Subscriber_ID"] == node_id]["Phone_Number"]
                if len(phone_data) > 0:
                    phone_val = phone_data.iloc[0]
                    phone = f" | 📱 {phone_val}" if pd.notna(phone_val) else ""
            
            # Get device info if available (professional IPDR)
            device_info = ""
            if "device_model" in df.columns:
                device_data = df[df["Subscriber_ID"] == node_id]
                if len(device_data) > 0:
                    device = device_data["device_model"].iloc[0]
                    imei = device_data.get("imei", pd.Series(["UNKNOWN"])).iloc[0]
                    if device != "Unknown Device":
                        device_info = f"📱 Device: {device}\n💾 IMEI: {imei}\n"
            
            # Get top apps if available (professional IPDR)
            apps_info = ""
            if "app_name" in df.columns:
                app_data = df[df["Subscriber_ID"] == node_id]["app_name"]
                top_apps = app_data.value_counts().head(3)
                if len(top_apps) > 0 and top_apps.iloc[0] != "Unknown":
                    apps_list = [f"{app} ({count})" for app, count in top_apps.items() if app != "Unknown"]
                    if apps_list:
                        apps_info = f"📲 Top Apps: {', '.join(apps_list)}\n"
            
            title = (
                f"👤 {name}{phone}\n"
                f"{'─' * 30}\n"
                f"📍 Location: {city}\n"
                f"{device_info}"
                f"{apps_info}"
                f"📊 Total Sessions: {sessions:,}\n"
                f"📦 Data Transferred: {data_mb:.1f} MB\n"
                f"🔴 Tor Sessions: {tor}\n"
                f"🌍 Foreign Connections: {foreign}\n"
                f"{'─' * 30}\n"
                f"Network Centrality: {cent:.3f}"
            )

            x = float(pos[node_id][0]) * 1000
            y = float(pos[node_id][1]) * 1000

            net.add_node(
                node_id,
                label=name,
                x=x, y=y,
                color={"background": color, "border": color,
                       "highlight": {"background": color, "border": "#FFFFFF"}},
                size=size,
                shape=shape,
                title=title,
                borderWidth=border_width,
                shadow={"enabled": True, "color": f"{color}44", "size": 15, "x": 0, "y": 0},
                font={"color": color, "size": 13, "face": "Inter, sans-serif", "bold": True,
                      "strokeWidth": 3, "strokeColor": "#0A0E14"},
            )
        else:
            # Server node
            is_shared = node_id in shared_ips
            is_tor    = attrs.get("is_tor", False)
            is_foreign = attrs.get("is_foreign", False)

            if is_shared:
                color = SHARED_COLOR
                size  = 24 + cent * 45
                shape = "diamond"
                border_width = 3
                glow_color = "#FFFFFF"
                type_label = "⚠️ SHARED (GANG EVIDENCE)"
                type_color = "#FF4444"
            elif is_tor:
                color = TOR_COLOR
                size  = 18 + cent * 30
                shape = "triangle"
                border_width = 2
                glow_color = TOR_COLOR
                type_label = "🔴 TOR EXIT NODE"
                type_color = TOR_COLOR
            elif is_foreign:
                color = FOREIGN_COLOR
                size  = 16 + cent * 25
                shape = "square"
                border_width = 2
                glow_color = FOREIGN_COLOR
                type_label = "🌍 FOREIGN SERVER"
                type_color = FOREIGN_COLOR
            else:
                color = SERVER_COLOR
                size  = 12 + cent * 20
                shape = "dot"
                border_width = 1
                glow_color = SERVER_COLOR
                type_label = "🔵 DOMESTIC SERVER"
                type_color = SERVER_COLOR

            # Find connected suspects
            connected = [n for n in G.neighbors(node_id) if G.nodes[n].get("node_type") == "subscriber"]
            connected_names = [G.nodes[n].get("label", n) for n in connected]
            suspects_html = "".join(
                f"<div style='display:inline-block;background:{SUSPECT_COLORS[sub_ids.index(s) % len(SUSPECT_COLORS)]}22;"
                f"color:{SUSPECT_COLORS[sub_ids.index(s) % len(SUSPECT_COLORS)]};"
                f"border:1px solid {SUSPECT_COLORS[sub_ids.index(s) % len(SUSPECT_COLORS)]}44;"
                f"border-radius:4px;padding:1px 6px;margin:2px;font-size:10px'>"
                f"{G.nodes[s].get('label', s)}</div>"
                for s in connected if s in sub_ids
            )

            # Build connected suspects list
            connected_suspects_list = ', '.join([G.nodes[s].get('label', s) for s in connected if s in sub_ids][:3])
            if len([s for s in connected if s in sub_ids]) > 3:
                connected_suspects_list += f" (+{len([s for s in connected if s in sub_ids]) - 3} more)"
            
            title = (
                f"🌐 {node_id}\n"
                f"{'─' * 30}\n"
                f"Type: {type_label}\n"
                f"{'─' * 30}\n"
                f"Total Connections: {len(connected)}\n"
                f"Network Centrality: {cent:.3f}\n"
                f"{'─' * 30}\n"
                f"Connected Suspects:\n{connected_suspects_list if connected_suspects_list else 'None'}"
            )

            label_text = node_id[:16] + "…" if len(node_id) > 16 else node_id

            x = float(pos[node_id][0]) * 1000
            y = float(pos[node_id][1]) * 1000

            net.add_node(
                node_id,
                label=label_text,
                x=x, y=y,
                color={"background": f"{color}CC", "border": color,
                       "highlight": {"background": color, "border": "#FFFFFF"}},
                size=size,
                shape=shape,
                title=title,
                borderWidth=border_width,
                shadow={"enabled": True, "color": f"{glow_color}33", "size": 10, "x": 0, "y": 0},
                font={"color": f"{color}CC", "size": 10, "face": "JetBrains Mono, monospace",
                      "strokeWidth": 2, "strokeColor": "#0A0E14"},
            )

    # ── Add Edges ────────────────────────────────────────
    for u, v, attrs in G.edges(data=True):
        is_tor_edge = attrs.get("is_tor", False)
        is_foreign_edge = attrs.get("is_foreign", False)
        sessions = attrs.get("sessions", 0)
        data_bytes = attrs.get("bytes", 0)
        data_mb = data_bytes / 1_048_576

        if is_tor_edge:
            edge_color = "#FF444466"
            dashes = True
        elif is_foreign_edge:
            edge_color = "#FF8C0044"
            dashes = [8, 4]
        else:
            edge_color = "#1E3A5F55"
            dashes = False

        # Get suspect color for edge if one end is a subscriber
        u_type = G.nodes[u].get("node_type", "")
        v_type = G.nodes[v].get("node_type", "")
        if u_type == "subscriber" and u in sub_ids:
            idx = sub_ids.index(u)
            edge_color = f"{SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]}44"
        elif v_type == "subscriber" and v in sub_ids:
            idx = sub_ids.index(v)
            edge_color = f"{SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]}44"

        net.add_edge(
            u, v,
            width=attrs.get("weight", 1),
            color={"color": edge_color, "highlight": "#00D4FF88", "hover": "#00D4FF66"},
            title=f"Connection Details\n{'─' * 20}\nSessions: {sessions:,}\nData Volume: {data_mb:.1f} MB",
            smooth={"type": "curvedCW", "roundness": 0.15},
            dashes=dashes,
        )

    # ── Physics + Interaction Settings ───────────────────
    net.set_options("""
    {
      "physics": {
        "enabled": false
      },
      "edges": {
        "smooth": {
          "type": "curvedCW",
          "roundness": 0.15
        },
        "hoverWidth": 2,
        "selectionWidth": 3
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 80,
        "zoomView": true,
        "dragView": true,
        "multiselect": true,
        "dragNodes": true,
        "navigationButtons": true,
        "keyboard": {
          "enabled": true
        }
      },
      "nodes": {
        "borderWidthSelected": 4
      }
    }
    """)

    # Save to a local HTML file and read it back
    output_file = "network_graph_temp.html"
    net.save_graph(output_file)
    
    with open(output_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Clean up
    if os.path.exists(output_file):
        os.unlink(output_file)

    # ── Inject Premium Styling + Legend ───────────────────
    # Build legend HTML
    suspect_legend = ""
    for idx, (sub_id, meta) in enumerate(sub_meta.items()):
        c = SUSPECT_COLORS[idx % len(SUSPECT_COLORS)]
        suspect_legend += (
            f"<div style='display:flex;align-items:center;gap:6px;margin:4px 0'>"
            f"<div style='width:10px;height:10px;border-radius:50%;background:{c};"
            f"box-shadow:0 0 6px {c}88'></div>"
            f"<span style='font-size:11px;color:#E6EDF3'>{meta['name']}</span>"
            f"</div>"
        )

    legend_html = f"""
    <div id="graph-legend" style="
        position:absolute;bottom:16px;left:16px;z-index:1000;
        background:rgba(10,14,20,0.92);backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid #30363D;border-radius:12px;
        padding:14px 18px;font-family:Inter,sans-serif;
        color:#E6EDF3;box-shadow:0 8px 32px rgba(0,0,0,0.5);
        max-width:200px;transition:all 0.3s ease">
        <p style="margin:0 0 10px 0;font-weight:700;font-size:11px;color:#00D4FF;
            text-transform:uppercase;letter-spacing:1px;
            border-bottom:1px solid #30363D;padding-bottom:6px">
            🕸️ Network Legend
        </p>
        <p style="color:#8B949E;font-size:9px;margin:0 0 6px 0;text-transform:uppercase;
            letter-spacing:0.5px">SUSPECTS</p>
        {suspect_legend}
        <div style="margin:8px 0;border-top:1px solid #30363D"></div>
        <p style="color:#8B949E;font-size:9px;margin:0 0 6px 0;text-transform:uppercase;
            letter-spacing:0.5px">SERVERS</p>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:10px;height:10px;border-radius:2px;background:#4A6FA5"></div>
            <span style="font-size:11px">Domestic Server</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:10px;height:10px;border-radius:2px;background:#FF8C00"></div>
            <span style="font-size:11px">Foreign Server</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:0;height:0;border-left:5px solid transparent;
                border-right:5px solid transparent;border-bottom:10px solid #FF4444"></div>
            <span style="font-size:11px">Tor Exit Node</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:10px;height:10px;transform:rotate(45deg);background:#FFFFFF"></div>
            <span style="font-size:11px;color:#FF4444;font-weight:600">Shared IP (Gang)</span>
        </div>
        <div style="margin:8px 0;border-top:1px solid #30363D"></div>
        <p style="color:#8B949E;font-size:9px;margin:0 0 4px 0;text-transform:uppercase;
            letter-spacing:0.5px">EDGES</p>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:20px;height:2px;background:#1E3A5F"></div>
            <span style="font-size:10px">Normal</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:20px;height:2px;background:#FF8C00;
                border-top:2px dashed #FF8C00"></div>
            <span style="font-size:10px">Foreign</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin:3px 0">
            <div style="width:20px;height:2px;background:#FF4444;
                border-top:2px dashed #FF4444"></div>
            <span style="font-size:10px;color:#FF4444">Tor Traffic</span>
        </div>
    </div>
    """

    title_html = """
    <div style="
        position:absolute;top:12px;left:50%;transform:translateX(-50%);z-index:1000;
        background:rgba(10,14,20,0.88);backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(0,212,255,0.25);border-radius:10px;
        padding:6px 18px;font-family:Inter,sans-serif;
        text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.4)">
        <span style="color:#00D4FF;font-size:13px;font-weight:700;letter-spacing:0.5px">
            🕸️ Suspect ↔ Server Connection Map
        </span>
    </div>
    """

    stats_html = f"""
    <div style="
        position:absolute;top:12px;right:16px;z-index:1000;
        background:rgba(10,14,20,0.88);backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid #30363D;border-radius:10px;
        padding:8px 14px;font-family:Inter,sans-serif;
        color:#E6EDF3;font-size:11px;box-shadow:0 4px 20px rgba(0,0,0,0.4)">
        <span style="color:#8B949E">Nodes:</span> <b style="color:#00D4FF">{len(G.nodes)}</b>
        <span style="margin:0 6px;color:#30363D">|</span>
        <span style="color:#8B949E">Edges:</span> <b style="color:#00D4FF">{len(G.edges)}</b>
        <span style="margin:0 6px;color:#30363D">|</span>
        <span style="color:#8B949E">Suspects:</span> <b style="color:#00D4FF">{len(sub_meta)}</b>
    </div>
    """

    # Inject into HTML
    inject_html = legend_html + title_html + stats_html
    html_content = html_content.replace(
        "</body>",
        f"""
        <div style="position:relative">{inject_html}</div>
        <script>
        // Once physics simulation is complete, disable physics so the graph stops moving completely
        if (typeof network !== 'undefined') {{
            network.on("stabilizationIterationsDone", function () {{
                network.setOptions( {{ physics: false }} );
            }});
        }}
        </script>
        <style>
            body {{ margin:0; padding:0; overflow:hidden; }}
            #mynetwork {{
                border: 1px solid #1E3A5F !important;
                border-radius: 12px !important;
                box-shadow: inset 0 0 60px rgba(0,212,255,0.03),
                            0 0 40px rgba(0,0,0,0.3) !important;
            }}
            .vis-navigation .vis-button {{
                background-color: rgba(10,14,20,0.8) !important;
                border: 1px solid #30363D !important;
                border-radius: 6px !important;
            }}
            .vis-navigation .vis-button:hover {{
                background-color: rgba(0,212,255,0.15) !important;
                border-color: #00D4FF !important;
            }}
        </style>
        </body>"""
    )

    return html_content


def render_graph(html_content: str, height: int = 660):
    """Render the PyVis HTML inside Streamlit."""
    # Render directly with components.html
    # The key is to make sure JavaScript executes properly
    components.html(html_content, height=height, scrolling=False)
