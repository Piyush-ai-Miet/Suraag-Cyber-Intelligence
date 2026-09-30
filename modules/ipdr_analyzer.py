"""
modules/ipdr_analyzer.py — Suराग IPDR Parser & Statistics Engine
Supports real DoT India IPDR format (DS-16/13/2017-DS-III).
Flexible parser accepting both real ISP exports and synthetic data.

Real DoT mandatory fields:
  MSISDN, IMSI, IMEI, Source_IP, Source_Port, Destination_IP,
  Destination_Port, Session_Start_Time, Session_End_Time,
  Uplink_Volume, Downlink_Volume, RAT_Type, Cell_ID, LAC, NAS_IP, Protocol
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import timedelta

IST = timedelta(hours=5, minutes=30)

# ── Known Tor Exit Node IP Prefixes ──────────────────────────────────────────
TOR_IP_PREFIXES = [
    "185.220.", "185.107.", "195.176.", "199.249.", "204.8.156.",
    "162.247.", "51.15.",   "45.142.",  "178.175.", "109.70.",
    "77.109.",  "89.234.",  "94.142.",  "171.25.",  "176.10.",
]

# Tor-specific ports
TOR_PORTS = {9050, 9001, 9030, 9040, 9150}

# Known VPN / Proxy ports
VPN_PROXY_PORTS = {1194, 1723, 500, 4500, 1080, 8080, 3128, 8888}

# Financial fraud related ports / services (OTP, payment gateways)
FINANCIAL_PORTS = {443}  # handled separately via destination IP ranges

# Private/Reserved IP ranges (Indian ISP internal — NOT foreign)
PRIVATE_IP_PREFIXES = [
    "10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
    "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.",
    "127.", "169.254.", "0.",
]

# Indian ISP IP ranges (BSNL, Airtel, Jio, Vi etc.) — NOT foreign
INDIAN_ISP_PREFIXES = [
    "1.6.", "1.7.", "1.22.", "1.23.", "14.139.", "14.140.", "14.141.",
    "27.56.", "27.57.", "43.224.", "43.225.", "45.112.", "45.113.",
    "49.32.", "49.33.", "49.34.", "49.35.", "49.36.", "49.37.",
    "59.88.", "59.89.", "59.90.", "59.91.", "59.92.", "59.93.",
    "61.0.",  "61.1.",  "61.2.",  "61.3.",  "61.4.",  "61.5.",
    "103.1.", "103.2.", "103.3.", "106.0.", "106.51.", "106.76.",
    "115.96.", "115.97.", "117.192.", "117.193.", "117.194.", "117.195.",
    "120.56.", "120.57.", "122.160.", "122.161.", "122.162.", "122.163.",
    "122.164.", "122.165.", "122.166.", "122.167.", "122.168.", "122.169.",
    "122.170.", "122.171.", "122.172.", "122.173.", "122.174.", "122.175.",
    "122.176.", "122.177.", "122.178.", "122.179.", "125.16.", "125.17.",
    "125.18.", "125.19.", "125.20.", "125.21.", "125.22.", "125.23.",
    "182.64.", "182.65.", "182.66.", "182.67.", "182.68.", "182.69.",
    "182.70.", "182.71.", "182.72.", "182.73.", "182.74.", "182.75.",
    "182.76.", "182.77.", "205.174.", "203.74.", "203.75.",
]

# Off-hours window (midnight to 5 AM IST)
OFF_HOURS_START = 0
OFF_HOURS_END   = 5

# ── Column Name Mappings (DoT format + legacy support) ────────────────────────
COLUMN_MAPPINGS = {

    # ── Primary subscriber identifier (phone number) ──
    'msisdn': [
        'msisdn', 'mobile_number', 'mobile no', 'phone_number', 'phone',
        'calling_number', 'subscriber_number', 'mob_no', 'mobile',
    ],

    # ── SIM card identifier ──
    'imsi': [
        'imsi', 'sim_id', 'sim_serial', 'iccid',
    ],

    # ── Device identifier ──
    'imei': [
        'imei', 'device_id', 'device_imei', 'handset_id', 'equipment_id',
    ],

    # ── Legacy subscriber_id fallback ──
    'subscriber_id': [
        'subscriber_id', 'sub_id', 'user_id', 'session_id',
        'subscriber', 'user', 'account_id',
    ],

    'subscriber_name': [
        'subscriber_name', 'name', 'user_name', 'username',
        'account_name', 'suspect_name',
    ],

    # ── IP addresses ──
    'source_ip': [
        'source_ip', 'src_ip', 'sourceip', 'source_address',
        'nas_assigned_ip', 'ue_ip', 'user_ip', 'public_ip',
    ],

    'destination_ip': [
        'destination_ip', 'dest_ip', 'dst_ip', 'destip',
        'destination_address', 'remote_ip', 'server_ip',
    ],

    'source_port': [
        'source_port', 'src_port', 'sport', 'sourceport', 'local_port',
    ],

    'destination_port': [
        'destination_port', 'dest_port', 'dst_port', 'dport',
        'destport', 'remote_port', 'server_port',
    ],

    # ── Timestamps ──
    'timestamp': [
        'timestamp', 'session_start_time', 'start_time', 'datetime',
        'date_time', 'date', 'record_time', 'event_time', 'start_timestamp',
        'session_start', 'call_start_time', 'conn_start_time',
    ],

    'session_end_time': [
        'session_end_time', 'end_time', 'stop_time', 'disconnect_time',
        'session_end', 'end_timestamp',
    ],

    # ── Data volumes (real DoT fields) ──
    'uplink_volume': [
        'uplink_volume', 'uplink_bytes', 'upload_bytes', 'upload_volume',
        'bytes_sent', 'tx_bytes', 'data_volume_uplink', 'up_bytes',
        'data_up', 'upload_data',
    ],

    'downlink_volume': [
        'downlink_volume', 'downlink_bytes', 'download_bytes', 'download_volume',
        'bytes_received', 'rx_bytes', 'data_volume_downlink', 'down_bytes',
        'data_down', 'download_data',
    ],

    # ── Legacy total data volume ──
    'data_volume_bytes': [
        'total_bytes', 'data_volume_bytes', 'bytes', 'data_mb',
        'bytes_transferred', 'data_volume', 'total_data',
    ],

    # ── Network / radio info ──
    'rat_type': [
        'rat_type', 'rat', 'network_type', 'access_type',
        'radio_access_type', 'technology', 'tech_type',
    ],

    'cell_id': [
        'cell_id', 'cell_tower_id', 'cellid', 'tower_id',
        'base_station_id', 'bts_id', 'enodeb_id', 'site_id',
        'cell_tower', 'tower',
    ],

    'lac': [
        'lac', 'location_area_code', 'location_area', 'tac',
        'tracking_area_code',
    ],

    'nas_ip': [
        'nas_ip', 'nas_ip_address', 'gateway_ip', 'router_ip',
        'pgw_ip', 'sgw_ip', 'bng_ip',
    ],

    # ── Protocol ──
    'protocol': [
        'protocol', 'app_protocol', 'l4_protocol', 'service_type',
        'transport_protocol', 'proto',
    ],

    # ── ISP ──
    'isp': [
        'isp', 'operator', 'operator_id', 'circle', 'provider',
        'service_provider', 'telecom_operator',
    ],

    # ── Location ──
    'city': ['city', 'location', 'geo_city', 'location_city'],
    'state': ['state', 'region', 'circle_name'],
    'latitude': ['latitude', 'lat'],
    'longitude': ['longitude', 'lon', 'long'],

    # ── Pre-labelled flags (accepted if present, auto-computed if absent) ──
    'is_foreign_ip':    ['is_foreign_ip', 'foreign_ip', 'is_foreign'],
    'is_tor':           ['is_tor', 'tor', 'is_tor_node'],
    'is_vpn':           ['is_vpn', 'vpn', 'is_vpn_suspected'],
    'is_proxy':         ['is_proxy', 'proxy'],
    'is_off_hours':     ['is_off_hours', 'off_hours'],
    'is_suspicious':    ['is_suspicious', 'suspicious', 'anomaly'],

    # ── App / domain ──
    'app_name': ['app_name', 'app', 'application', 'service_name'],
    'domain':   ['domain', 'website', 'url', 'dns_query', 'sni', 'hostname'],

    # ── Device model ──
    'device_model': ['device_model', 'device', 'handset', 'model'],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_tor_ip(ip: str) -> bool:
    return any(ip.startswith(p) for p in TOR_IP_PREFIXES)

def _is_private_ip(ip: str) -> bool:
    return any(ip.startswith(p) for p in PRIVATE_IP_PREFIXES)

def _is_indian_ip(ip: str) -> bool:
    return any(ip.startswith(p) for p in INDIAN_ISP_PREFIXES)

def _is_foreign_ip(ip: str) -> bool:
    """True if IP is not private and not a known Indian ISP range."""
    if _is_private_ip(ip):
        return False
    if _is_indian_ip(ip):
        return False
    return True  # Unknown = treat as foreign


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to standard format (case-insensitive)."""
    df_norm = df.copy()
    lower_cols = {col.lower().strip(): col for col in df.columns}

    for std_name, aliases in COLUMN_MAPPINGS.items():
        for alias in aliases:
            if alias in lower_cols:
                orig = lower_cols[alias]
                if orig != std_name and std_name not in df_norm.columns:
                    df_norm.rename(columns={orig: std_name}, inplace=True)
                break

    return df_norm


def _auto_compute_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-compute investigation flags from raw data.
    This is the core of real cybercell analysis — flags are derived,
    not trusted from input columns.
    """
    df = df.copy()

    # ── is_tor: Tor IP prefix OR Tor port ──────────────────────────────────
    tor_by_ip   = df['destination_ip'].apply(_is_tor_ip)
    tor_by_port = df['destination_port'].isin(TOR_PORTS)
    df['is_tor'] = tor_by_ip | tor_by_port

    # ── is_foreign_ip ───────────────────────────────────────────────────────
    df['is_foreign_ip'] = df['destination_ip'].apply(_is_foreign_ip)

    # ── is_vpn: VPN/proxy ports ─────────────────────────────────────────────
    df['is_vpn'] = df['destination_port'].isin(VPN_PROXY_PORTS)

    # ── is_off_hours: midnight–5 AM IST ─────────────────────────────────────
    hour = df['timestamp'].dt.hour
    df['is_off_hours'] = hour.between(OFF_HOURS_START, OFF_HOURS_END - 1)

    # ── is_proxy: port 1080 / 3128 / 8080 ───────────────────────────────────
    df['is_proxy'] = df['destination_port'].isin({1080, 3128, 8080, 3129})

    # ── is_suspicious: OR of all flags ──────────────────────────────────────
    df['is_suspicious'] = (
        df['is_tor'] | df['is_foreign_ip'] | df['is_vpn'] | df['is_off_hours']
    )

    return df


def load_and_validate(file_bytes: bytes, filename: str) -> tuple:
    """
    Load and validate an IPDR CSV.
    Supports real DoT India format (MSISDN, IMSI, IMEI, Cell_ID …)
    and legacy formats.
    Returns (DataFrame, error_string). error_string is "" on success.
    """
    try:
        import io
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        return None, f"File could not be read. Ensure it is a valid CSV. ({e})"

    if df.empty:
        return None, "The uploaded file is empty."

    # ── Normalize columns ────────────────────────────────────────────────────
    df = normalize_columns(df)

    # ── Minimum required: source + destination IP ────────────────────────────
    if 'source_ip' not in df.columns or 'destination_ip' not in df.columns:
        return None, (
            "Invalid IPDR format. Required columns missing: Source_IP and Destination_IP. "
            "Please upload a valid IPDR CSV from your ISP."
        )

    if 'timestamp' not in df.columns:
        return None, (
            "Missing timestamp column. Expected: Session_Start_Time, Timestamp, Start_Time, etc."
        )

    # ── Subscriber identity: prefer MSISDN, fall back to subscriber_id ──────
    if 'msisdn' in df.columns:
        df['subscriber_id']   = df['msisdn'].astype(str).str.strip()
        df['subscriber_name'] = df['msisdn'].astype(str).str.strip()
    elif 'subscriber_id' not in df.columns:
        src = df['source_ip'].iloc[0] if len(df) > 0 else 'UNKNOWN'
        df['subscriber_id']   = f"SUBJ-{src}".replace('.', '-')
        df['subscriber_name'] = filename.replace('.csv', '').replace('_', ' ')

    if 'subscriber_name' not in df.columns:
        df['subscriber_name'] = df['subscriber_id']

    # ── IMSI / IMEI defaults ─────────────────────────────────────────────────
    for col, default in [('imsi', 'UNKNOWN'), ('imei', 'UNKNOWN')]:
        if col not in df.columns:
            df[col] = default

    # ── Ports defaults ────────────────────────────────────────────────────────
    if 'source_port' not in df.columns:
        df['source_port'] = 0
    if 'destination_port' not in df.columns:
        df['destination_port'] = 443

    # ── Protocol default ──────────────────────────────────────────────────────
    if 'protocol' not in df.columns:
        df['protocol'] = 'TCP'

    # ── Data volumes ──────────────────────────────────────────────────────────
    # Support both DoT format (uplink + downlink) and legacy (total bytes)
    if 'uplink_volume' not in df.columns:
        df['uplink_volume'] = 0
    if 'downlink_volume' not in df.columns:
        df['downlink_volume'] = 0

    # Compute total if not present
    if 'data_volume_bytes' not in df.columns:
        ul = pd.to_numeric(df['uplink_volume'], errors='coerce').fillna(0)
        dl = pd.to_numeric(df['downlink_volume'], errors='coerce').fillna(0)
        if (ul.sum() + dl.sum()) > 0:
            df['data_volume_bytes'] = (ul + dl).astype(int)
        else:
            df['data_volume_bytes'] = 0
    
    # ── Session end time & duration ───────────────────────────────────────────
    if 'session_end_time' not in df.columns:
        df['session_end_time'] = pd.NaT

    if 'duration' not in df.columns:
        df['duration'] = 0

    # ── Network/radio fields defaults ─────────────────────────────────────────
    for col, default in [
        ('rat_type', 'Unknown'),
        ('cell_id',  'UNKNOWN'),
        ('lac',      'UNKNOWN'),
        ('nas_ip',   'UNKNOWN'),
        ('isp',      'Unknown ISP'),
        ('city',     'Unknown'),
        ('state',    'Unknown'),
    ]:
        if col not in df.columns:
            df[col] = default

    if 'latitude' not in df.columns:
        df['latitude'] = 20.5937   # India center
    if 'longitude' not in df.columns:
        df['longitude'] = 78.9629

    # ── App / domain defaults ─────────────────────────────────────────────────
    if 'app_name' not in df.columns:
        df['app_name'] = 'Unknown'
    if 'domain' not in df.columns:
        df['domain'] = ''
    if 'device_model' not in df.columns:
        df['device_model'] = 'Unknown'

    # ── Session ID ────────────────────────────────────────────────────────────
    if 'session_id' not in df.columns:
        df['session_id'] = 'SID-' + df.index.astype(str)

    # ── Parse timestamps ──────────────────────────────────────────────────────
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        if df.empty:
            return None, "No valid timestamps found in the file."
    except Exception as e:
        return None, f"Timestamp parsing error: {e}"

    # Parse session_end_time if present
    try:
        df['session_end_time'] = pd.to_datetime(df['session_end_time'], errors='coerce')
        # Compute duration from start/end if duration column is 0
        mask = (
            df['duration'] == 0 and
            df['session_end_time'].notna().any()
        )
        if df['duration'].sum() == 0 and df['session_end_time'].notna().any():
            delta = (df['session_end_time'] - df['timestamp']).dt.total_seconds()
            df['duration'] = delta.fillna(0).clip(lower=0).astype(int)
    except Exception:
        pass

    # ── Coerce booleans (if pre-labelled in file) ─────────────────────────────
    bool_cols = ['is_foreign_ip', 'is_tor', 'is_vpn', 'is_proxy', 'is_off_hours', 'is_suspicious']
    for col in bool_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().str.lower()
                .map({'true': True, 'false': False, '1': True, '0': False,
                      'yes': True, 'no': False})
                .fillna(False).astype(bool)
            )

    # ── Coerce numerics ───────────────────────────────────────────────────────
    for col in ['data_volume_bytes', 'uplink_volume', 'downlink_volume',
                'duration', 'source_port', 'destination_port',
                'latitude', 'longitude']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['source_port']       = df['source_port'].astype(int)
    df['destination_port']  = df['destination_port'].astype(int)
    df['data_volume_bytes'] = df['data_volume_bytes'].astype(int)
    df['uplink_volume']     = df['uplink_volume'].astype(int)
    df['downlink_volume']   = df['downlink_volume'].astype(int)
    df['duration']          = df['duration'].astype(int)

    # ── AUTO-COMPUTE all investigation flags from raw data ────────────────────
    # These override any pre-labelled flags for accuracy
    df = _auto_compute_flags(df)

    return df, ""


def add_uppercase_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add uppercase column aliases used throughout the app.
    Call AFTER concatenating multiple DataFrames.
    Also derives Hour_IST, Date, DayOfWeek.
    """
    df = df.copy()

    alias_map = {
        'subscriber_id':    'Subscriber_ID',
        'subscriber_name':  'Subscriber_Name',
        'msisdn':           'MSISDN',
        'imsi':             'IMSI',
        'imei':             'IMEI',
        'source_ip':        'Source_IP',
        'destination_ip':   'Destination_IP',
        'source_port':      'Source_Port',
        'destination_port': 'Destination_Port',
        'timestamp':        'Timestamp',
        'session_end_time': 'Session_End_Time',
        'protocol':         'App_Protocol',
        'data_volume_bytes':'Data_Volume_Bytes',
        'uplink_volume':    'Uplink_Volume',
        'downlink_volume':  'Downlink_Volume',
        'duration':         'Session_Duration_sec',
        'rat_type':         'RAT_Type',
        'cell_id':          'Cell_ID',
        'lac':              'LAC',
        'nas_ip':           'NAS_IP',
        'isp':              'ISP',
        'city':             'City',
        'latitude':         'Latitude',
        'longitude':        'Longitude',
        'is_tor':           'Is_TOR',
        'is_foreign_ip':    'Is_Foreign_IP',
        'is_off_hours':     'Is_Off_Hours',
        'is_vpn':           'Is_VPN_Suspected',
        'is_proxy':         'Is_Proxy',
        'is_suspicious':    'Is_Suspicious',
        'app_name':         'App_Name',
        'domain':           'Domain',
        'imei':             'IMEI',
    }

    for lower, upper in alias_map.items():
        if lower in df.columns and upper not in df.columns:
            df[upper] = df[lower]

    # Derived time columns
    if 'Timestamp' in df.columns:
        if 'Hour_IST' not in df.columns:
            df['Hour_IST']  = df['Timestamp'].dt.hour
        if 'Date' not in df.columns:
            df['Date']      = df['Timestamp'].dt.date
        if 'DayOfWeek' not in df.columns:
            df['DayOfWeek'] = df['Timestamp'].dt.day_name()

    return df


@st.cache_data(show_spinner=False)
def compute_summary_stats(df: pd.DataFrame) -> dict:
    """Compute top-level KPI metrics."""
    total_sessions      = len(df)
    unique_ips          = df["Destination_IP"].nunique()
    suspicious_mask     = df["Is_TOR"] | df["Is_Foreign_IP"] | df["Is_Off_Hours"]
    suspicious_sessions = int(suspicious_mask.sum())
    total_bytes         = int(df["Data_Volume_Bytes"].sum())

    # IMEI / device analysis
    unique_imeis = df["IMEI"].nunique() if "IMEI" in df.columns else 0
    multi_sim_devices = 0
    if "IMEI" in df.columns and "Subscriber_ID" in df.columns:
        subs_per_imei = df.groupby("IMEI")["Subscriber_ID"].nunique()
        multi_sim_devices = int((subs_per_imei > 1).sum())

    # Cell tower analysis
    unique_towers = df["Cell_ID"].nunique() if "Cell_ID" in df.columns else 0

    return {
        "total_sessions":       total_sessions,
        "unique_ips":           unique_ips,
        "suspicious_sessions":  suspicious_sessions,
        "total_bytes":          total_bytes,
        "unique_subscribers":   df["Subscriber_ID"].nunique(),
        "tor_sessions":         int(df["Is_TOR"].sum()),
        "foreign_sessions":     int(df["Is_Foreign_IP"].sum()),
        "off_hours_sessions":   int(df["Is_Off_Hours"].sum()),
        "vpn_sessions":         int(df["Is_VPN_Suspected"].sum()),
        "date_range_start":     df["Timestamp"].min(),
        "date_range_end":       df["Timestamp"].max(),
        "unique_imeis":         unique_imeis,
        "multi_sim_devices":    multi_sim_devices,
        "unique_towers":        unique_towers,
    }


def format_bytes(b: int) -> str:
    if b >= 1_073_741_824:
        return f"{b / 1_073_741_824:.2f} GB"
    elif b >= 1_048_576:
        return f"{b / 1_048_576:.2f} MB"
    elif b >= 1024:
        return f"{b / 1024:.2f} KB"
    return f"{b} B"


def format_indian(n: int) -> str:
    s = str(int(n))
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest  = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return ",".join(groups) + "," + last3


@st.cache_data(show_spinner=False)
def get_suspect_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Per-subscriber aggregated investigation profile."""
    agg = (
        df.groupby(["Subscriber_ID", "Subscriber_Name"])
        .agg(
            total_sessions      = ("Timestamp",          "count"),
            total_bytes         = ("Data_Volume_Bytes",  "sum"),
            uplink_bytes        = ("Uplink_Volume",      "sum"),
            downlink_bytes      = ("Downlink_Volume",    "sum"),
            unique_dest_ips     = ("Destination_IP",     "nunique"),
            tor_sessions        = ("Is_TOR",             "sum"),
            foreign_sessions    = ("Is_Foreign_IP",      "sum"),
            off_hours_sessions  = ("Is_Off_Hours",       "sum"),
            vpn_sessions        = ("Is_VPN_Suspected",   "sum"),
            first_seen          = ("Timestamp",          "min"),
            last_seen           = ("Timestamp",          "max"),
        )
        .reset_index()
    )

    # Peak active hour
    peak_hours = (
        df.groupby(["Subscriber_ID", "Hour_IST"])
        .size().reset_index(name="count")
        .sort_values("count", ascending=False)
        .drop_duplicates("Subscriber_ID")
        .rename(columns={"Hour_IST": "peak_hour"})
    )
    agg = agg.merge(peak_hours[["Subscriber_ID", "peak_hour"]], on="Subscriber_ID", how="left")

    # Top 3 destination IPs
    top_ips = (
        df.groupby(["Subscriber_ID", "Destination_IP"])
        .size().reset_index(name="cnt")
        .sort_values("cnt", ascending=False)
        .groupby("Subscriber_ID").head(3)
        .groupby("Subscriber_ID")["Destination_IP"]
        .apply(list).reset_index(name="top_dest_ips")
    )
    agg = agg.merge(top_ips, on="Subscriber_ID", how="left")

    # IMEI info
    if "IMEI" in df.columns:
        imei_info = (
            df.groupby("Subscriber_ID")["IMEI"]
            .agg(lambda x: list(x.dropna().unique()))
            .reset_index(name="imei_list")
        )
        agg = agg.merge(imei_info, on="Subscriber_ID", how="left")
    else:
        agg["imei_list"] = [[] for _ in range(len(agg))]

    # Cell towers used
    if "Cell_ID" in df.columns:
        tower_info = (
            df.groupby("Subscriber_ID")["Cell_ID"]
            .nunique().reset_index(name="unique_towers")
        )
        agg = agg.merge(tower_info, on="Subscriber_ID", how="left")
    else:
        agg["unique_towers"] = 0

    return agg
