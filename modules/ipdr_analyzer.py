"""
modules/ipdr_analyzer.py — Suराग IPDR CSV Parser & Statistics Engine
Handles CSV loading, validation, cleaning, and basic statistical profiling.
Flexible parser that accepts any IPDR format (similar to zip file logic).
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import timezone, timedelta

IST = timedelta(hours=5, minutes=30)

# Column name mappings (lowercase for case-insensitive matching)
COLUMN_MAPPINGS = {
    # Phone numbers
    'phone': ['msisdn', 'phone_number', 'phone', 'subscriber_phone', 'mobile', 'mobile_number'],
    'subscriber_name': ['subscriber_name', 'name', 'user_name', 'username'],
    'subscriber_id': ['subscriber_id', 'sub_id', 'user_id', 'imsi'],
    
    # IP addresses
    'source_ip': ['source_ip', 'src_ip', 'source', 'src'],
    'destination_ip': ['destination_ip', 'dest_ip', 'dst_ip', 'destination', 'dest', 'dst'],
    'source_port': ['source_port', 'src_port'],
    'destination_port': ['destination_port', 'dest_port', 'dst_port'],
    
    # Timestamp
    'timestamp': ['timestamp', 'session_start_time', 'start_time', 'datetime', 'date_time', 'date'],
    'session_end_time': ['session_end_time', 'end_time'],
    
    # Protocol
    'protocol': ['protocol', 'app_protocol', 'l4_protocol', 'service_type'],
    
    # Data volume
    'data_volume_bytes': ['total_bytes', 'data_volume_bytes', 'bytes', 'data_mb', 'upload_bytes', 'download_bytes'],
    
    # Session info
    'session_id': ['session_id', 'session', 'sid'],
    'duration': ['duration', 'session_duration_sec', 'session_duration_sec', 'duration_sec'],
    
    # Location
    'city': ['city', 'location', 'geo_city'],
    'state': ['state', 'region'],
    'latitude': ['latitude', 'lat'],
    'longitude': ['longitude', 'lon', 'long'],
    
    # ISP
    'isp': ['isp', 'operator', 'operator_id', 'circle'],
    
    # Behavioral flags
    'is_foreign_ip': ['is_foreign_ip', 'foreign_ip', 'is_foreign'],
    'is_tor': ['is_tor', 'tor', 'is_tor_node'],
    'is_vpn': ['is_vpn', 'vpn', 'is_vpn_suspected'],
    'is_proxy': ['is_proxy', 'proxy'],
    'is_off_hours': ['is_off_hours', 'off_hours'],
    'is_suspicious': ['is_suspicious', 'suspicious', 'anomaly'],
    
    # App/Website info
    'app_name': ['app_name', 'app', 'application'],
    'domain': ['domain', 'website', 'url', 'dns_query', 'sni'],
    
    # Device info
    'imei': ['imei', 'device_id'],
    'device_model': ['device_model', 'device'],
    'os_version': ['os_version', 'os'],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to standard format using flexible mapping.
    Case-insensitive matching.
    """
    df_normalized = df.copy()
    lower_cols = {col.lower(): col for col in df.columns}
    
    for standard_name, possible_names in COLUMN_MAPPINGS.items():
        for possible in possible_names:
            if possible in lower_cols:
                original_col = lower_cols[possible]
                if original_col != standard_name:
                    df_normalized.rename(columns={original_col: standard_name}, inplace=True)
                break
    
    return df_normalized


@st.cache_data(show_spinner=False)
def load_and_validate(file_bytes: bytes, filename: str) -> tuple[pd.DataFrame | None, str]:
    """
    Load CSV from bytes with flexible validation.
    Accepts ANY IPDR format - similar to zip file logic.
    Returns (DataFrame, error_message). error_message is "" on success.
    """
    try:
        import io
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        return None, f"Could not read the file. Please ensure it is a valid CSV. ({e})"
    
    if df.empty:
        return None, "The uploaded file is empty."
    
    # Normalize column names
    df = normalize_columns(df)
    
    # Check for MINIMUM required fields (at least one source and one destination identifier)
    has_source = any(col in df.columns for col in ['source_ip', 'phone', 'subscriber_id'])
    has_dest = any(col in df.columns for col in ['destination_ip'])
    
    if not (has_source and has_dest):
        return None, (
            "The uploaded file must contain at least source and destination identifiers. "
            "Expected columns like: Source_IP, Destination_IP or MSISDN/Phone"
        )
    
    # === CREATE MISSING COLUMNS WITH DEFAULTS ===
    
    # Phone number (extract from MSISDN or Subscriber_ID)
    if 'phone' not in df.columns:
        if 'subscriber_id' in df.columns:
            # Extract last 10 digits from subscriber_id
            df['phone'] = df['subscriber_id'].astype(str).str.extract(r'(\d{10})$')[0]
        else:
            df['phone'] = 'UNKNOWN'
    
    # Subscriber ID
    if 'subscriber_id' not in df.columns:
        if 'phone' in df.columns:
            df['subscriber_id'] = 'SUB-' + df['phone'].astype(str)
        else:
            df['subscriber_id'] = 'SUB-UNKNOWN'
    
    # Subscriber name
    if 'subscriber_name' not in df.columns:
        df['subscriber_name'] = 'Suspect ' + df.get('phone', df.get('subscriber_id', 'Unknown')).astype(str)
    
    # Timestamp
    if 'timestamp' not in df.columns:
        return None, "Missing timestamp column (expected: Timestamp, Session_Start_Time, or similar)"
    
    # Protocol
    if 'protocol' not in df.columns:
        df['protocol'] = 'HTTPS'
    
    # Data volume
    if 'data_volume_bytes' not in df.columns:
        df['data_volume_bytes'] = 0
    
    # Duration
    if 'duration' not in df.columns:
        df['duration'] = 0
    
    # ISP
    if 'isp' not in df.columns:
        df['isp'] = 'Unknown ISP'
    
    # Location
    if 'city' not in df.columns:
        df['city'] = 'Unknown'
    if 'state' not in df.columns:
        df['state'] = 'Unknown'
    if 'latitude' not in df.columns:
        df['latitude'] = 20.5937  # India center
    if 'longitude' not in df.columns:
        df['longitude'] = 78.9629
    
    # Ports (default if missing)
    if 'source_port' not in df.columns:
        df['source_port'] = 0
    if 'destination_port' not in df.columns:
        df['destination_port'] = 443
    
    # Session ID
    if 'session_id' not in df.columns:
        df['session_id'] = 'SID-' + df.index.astype(str)
    
    # Behavioral flags
    if 'is_foreign_ip' not in df.columns:
        df['is_foreign_ip'] = False
    if 'is_tor' not in df.columns:
        df['is_tor'] = False
    if 'is_vpn' not in df.columns:
        df['is_vpn'] = False
    if 'is_proxy' not in df.columns:
        df['is_proxy'] = False
    if 'is_off_hours' not in df.columns:
        df['is_off_hours'] = False
    if 'is_suspicious' not in df.columns:
        df['is_suspicious'] = False
    
    # App/Website info
    if 'app_name' not in df.columns:
        df['app_name'] = 'Unknown'
    if 'domain' not in df.columns:
        df['domain'] = 'unknown.com'
    
    # Device info
    if 'imei' not in df.columns:
        df['imei'] = 'UNKNOWN'
    if 'device_model' not in df.columns:
        df['device_model'] = 'Unknown Device'

    # === PARSE DATA TYPES ===
    
    # Parse timestamps → datetime
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        # Drop rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        if df.empty:
            return None, "No valid timestamps found in the file."
    except Exception as e:
        return None, f"The 'timestamp' column could not be parsed: {e}"

    # Coerce boolean columns
    bool_cols = ['is_foreign_ip', 'is_tor', 'is_vpn', 'is_proxy', 'is_off_hours', 'is_suspicious']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower().map(
                {'true': True, 'false': False, '1': True, '0': False, 'yes': True, 'no': False}
            ).fillna(False).astype(bool)

    # Coerce numeric columns
    numeric_cols = ['data_volume_bytes', 'duration', 'source_port', 'destination_port', 'latitude', 'longitude']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Ensure integers for ports, bytes, duration
    df['source_port'] = df['source_port'].astype(int)
    df['destination_port'] = df['destination_port'].astype(int)
    df['data_volume_bytes'] = df['data_volume_bytes'].astype(int)
    df['duration'] = df['duration'].astype(int)
    
    # === CREATE UPPERCASE ALIASES FOR BACKWARD COMPATIBILITY ===
    # Many downstream functions expect uppercase column names
    df['Subscriber_ID'] = df['subscriber_id']
    df['Subscriber_Name'] = df['subscriber_name']
    df['Phone_Number'] = df['phone']
    df['Source_IP'] = df['source_ip']
    df['Destination_IP'] = df['destination_ip']
    df['Source_Port'] = df['source_port']
    df['Destination_Port'] = df['destination_port']
    df['Timestamp'] = df['timestamp']
    df['App_Protocol'] = df['protocol']
    df['Data_Volume_Bytes'] = df['data_volume_bytes']
    df['Session_Duration_sec'] = df['duration']
    df['ISP'] = df['isp']
    df['City'] = df['city']
    df['Latitude'] = df['latitude']
    df['Longitude'] = df['longitude']
    df['Is_TOR'] = df['is_tor']
    df['Is_Foreign_IP'] = df['is_foreign_ip']
    df['Is_Off_Hours'] = df['is_off_hours']
    df['Is_VPN_Suspected'] = df['is_vpn']

    # Derive time-based columns (IST hour)
    df['Hour_IST'] = df['Timestamp'].dt.hour
    df['Date'] = df['Timestamp'].dt.date
    df['DayOfWeek'] = df['Timestamp'].dt.day_name()

    return df, ""


@st.cache_data(show_spinner=False)
def compute_summary_stats(df: pd.DataFrame) -> dict:
    """Compute top-level KPI metrics for the 4 header cards."""
    total_sessions = len(df)
    unique_ips      = df["Destination_IP"].nunique()

    suspicious_mask = (
        df["Is_TOR"] | df["Is_Foreign_IP"] | df["Is_Off_Hours"]
    )
    suspicious_sessions = int(suspicious_mask.sum())

    # Data volume
    total_bytes = df["Data_Volume_Bytes"].sum()

    return {
        "total_sessions":      total_sessions,
        "unique_ips":          unique_ips,
        "suspicious_sessions": suspicious_sessions,
        "total_bytes":         total_bytes,
        "unique_subscribers":  df["Subscriber_ID"].nunique(),
        "tor_sessions":        int(df["Is_TOR"].sum()),
        "foreign_sessions":    int(df["Is_Foreign_IP"].sum()),
        "off_hours_sessions":  int(df["Is_Off_Hours"].sum()),
        "date_range_start":    df["Timestamp"].min(),
        "date_range_end":      df["Timestamp"].max(),
    }


def format_bytes(b: int) -> str:
    """Convert bytes to human-readable string."""
    if b >= 1_073_741_824:
        return f"{b / 1_073_741_824:.2f} GB"
    elif b >= 1_048_576:
        return f"{b / 1_048_576:.2f} MB"
    elif b >= 1024:
        return f"{b / 1024:.2f} KB"
    return f"{b} B"


def format_indian(n: int) -> str:
    """Format number in Indian numbering system (1,23,456)."""
    s = str(int(n))
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest   = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return ",".join(groups) + "," + last3


@st.cache_data(show_spinner=False)
def get_suspect_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-subscriber aggregated statistics."""
    agg = (
        df.groupby(["Subscriber_ID", "Subscriber_Name"])
        .agg(
            total_sessions    = ("Timestamp",          "count"),
            total_bytes       = ("Data_Volume_Bytes",  "sum"),
            unique_dest_ips   = ("Destination_IP",     "nunique"),
            tor_sessions      = ("Is_TOR",             "sum"),
            foreign_sessions  = ("Is_Foreign_IP",      "sum"),
            off_hours_sessions= ("Is_Off_Hours",       "sum"),
            vpn_sessions      = ("Is_VPN_Suspected",   "sum"),
            first_seen        = ("Timestamp",          "min"),
            last_seen         = ("Timestamp",          "max"),
        )
        .reset_index()
    )

    # Peak active hour per subscriber
    peak_hours = (
        df.groupby(["Subscriber_ID", "Hour_IST"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .drop_duplicates("Subscriber_ID")
        .rename(columns={"Hour_IST": "peak_hour"})
    )
    agg = agg.merge(peak_hours[["Subscriber_ID", "peak_hour"]], on="Subscriber_ID", how="left")

    # Top 3 destination IPs per subscriber
    top_ips = (
        df.groupby(["Subscriber_ID", "Destination_IP"])
        .size()
        .reset_index(name="cnt")
        .sort_values("cnt", ascending=False)
        .groupby("Subscriber_ID")
        .head(3)
        .groupby("Subscriber_ID")["Destination_IP"]
        .apply(list)
        .reset_index(name="top_dest_ips")
    )
    agg = agg.merge(top_ips, on="Subscriber_ID", how="left")

    return agg
