"""
modules/mitre_mapper.py — Suराग MITRE ATT&CK Pattern Detector
Automatically maps IPDR patterns to MITRE ATT&CK tactics and techniques.
All helper functions defined before the rules list to avoid forward-reference errors.
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM

# ── Detection Helper Functions (defined BEFORE the rules list) ────────────────

def _detect_c2_beacon(df: pd.DataFrame) -> pd.Series:
    """Detect repetitive connections to the same foreign IP (beacon pattern)."""
    counts = df.groupby(["Subscriber_ID", "Destination_IP"])["Timestamp"].transform("count")
    return (counts >= 5) & df["Is_Foreign_IP"]


def _detect_bulk_off_hours(df: pd.DataFrame) -> pd.Series:
    """Large data transfer (>1 std above mean) during off-hours."""
    mean_vol = df["Data_Volume_Bytes"].mean()
    std_vol  = df["Data_Volume_Bytes"].std()
    return df["Is_Off_Hours"] & (df["Data_Volume_Bytes"] > mean_vol + std_vol)


def _detect_ip_hopping(df: pd.DataFrame) -> pd.Series:
    """Detect subscribers connecting to many unique IPs relative to total sessions."""
    unique_ips_per_sub = df.groupby("Subscriber_ID")["Destination_IP"].transform("nunique")
    total_per_sub      = df.groupby("Subscriber_ID")["Destination_IP"].transform("count")
    ratio = unique_ips_per_sub / total_per_sub.clip(lower=1)
    return ratio > 0.6


def _detect_multi_sim(df: pd.DataFrame) -> pd.Series:
    """Detect source IPs associated with multiple subscriber IDs (shared device)."""
    subs_per_src = df.groupby("Source_IP")["Subscriber_ID"].transform("nunique")
    return subs_per_src > 1


def _detect_data_spike(df: pd.DataFrame) -> pd.Series:
    """Flag sessions with data volume > 2 std deviations above mean."""
    mean_vol  = df["Data_Volume_Bytes"].mean()
    std_vol   = df["Data_Volume_Bytes"].std()
    threshold = mean_vol + 2 * std_vol
    return df["Data_Volume_Bytes"] > threshold


def _detect_tor(df: pd.DataFrame) -> pd.Series:
    return df["Is_TOR"]


def _detect_dark_web(df: pd.DataFrame) -> pd.Series:
    return df["Destination_Port"].isin([9050, 9001]) & df["Is_TOR"]


def _detect_foreign_c2(df: pd.DataFrame) -> pd.Series:
    return df["Is_Foreign_IP"] & ~df["App_Protocol"].isin(
        ["HTTPS", "HTTP", "DNS", "WhatsApp", "Telegram", "Paytm"]
    )


def _detect_remote_ports(df: pd.DataFrame) -> pd.Series:
    return df["Destination_Port"].isin([22, 3389, 445, 23])


def _detect_vpn(df: pd.DataFrame) -> pd.Series:
    return df["Is_VPN_Suspected"]


def _detect_short_sessions(df: pd.DataFrame) -> pd.Series:
    return df["Session_Duration_sec"] < 5


# ── MITRE ATT&CK Rules List ───────────────────────────────────────────────────

MITRE_RULES = [
    {
        "pattern":    "Tor / VPN Exit Node Traffic",
        "tactic":     "Defense Evasion",
        "technique":  "T1090.003",
        "risk_level": "CRITICAL",
        "description": "Suspect is using Tor — a tool specifically designed to hide internet activity from law enforcement.",
        "detect_fn":  _detect_tor,
    },
    {
        "pattern":    "Dark Web (.onion) / Tor Port Access",
        "tactic":     "Defense Evasion",
        "technique":  "T1090.003",
        "risk_level": "CRITICAL",
        "description": "Access to hidden dark-web servers (.onion) — used for illegal marketplaces, drug sales, and crime forums.",
        "detect_fn":  _detect_dark_web,
    },
    {
        "pattern":    "C2 Beacon Pattern (Repetitive Outbound)",
        "tactic":     "Command & Control",
        "technique":  "T1071.001",
        "risk_level": "CRITICAL",
        "description": "Device is sending regular, repeated signals to a remote server — a sign the device may be remotely controlled by criminals.",
        "detect_fn":  _detect_c2_beacon,
    },
    {
        "pattern":    "Known Malicious / Foreign C2 Server",
        "tactic":     "Command & Control",
        "technique":  "T1071",
        "risk_level": "CRITICAL",
        "description": "Communication with foreign servers known to host malicious software or criminal infrastructure.",
        "detect_fn":  _detect_foreign_c2,
    },
    {
        "pattern":    "SSH / RDP / SMB Port Access",
        "tactic":     "Initial Access",
        "technique":  "T1190",
        "risk_level": "HIGH",
        "description": "Attempted connections to remote access ports (SSH, RDP, SMB) — commonly used to break into computers.",
        "detect_fn":  _detect_remote_ports,
    },
    {
        "pattern":    "Bulk Data Transfer Off-Hours",
        "tactic":     "Exfiltration",
        "technique":  "T1048",
        "risk_level": "HIGH",
        "description": "Large amounts of data were sent in the middle of the night — a strong sign of secret data theft or illegal uploads.",
        "detect_fn":  _detect_bulk_off_hours,
    },
    {
        "pattern":    "Rapid IP Hopping (Same Device)",
        "tactic":     "Defense Evasion",
        "technique":  "T1036",
        "risk_level": "HIGH",
        "description": "The same device connected to many different servers very quickly — a technique used to evade detection.",
        "detect_fn":  _detect_ip_hopping,
    },
    {
        "pattern":    "Same Device, Multiple SIM / Accounts",
        "tactic":     "Persistence",
        "technique":  "T1078",
        "risk_level": "HIGH",
        "description": "The same physical device was used with more than one SIM card — commonly done to avoid being tracked.",
        "detect_fn":  _detect_multi_sim,
    },
    {
        "pattern":    "Multiple Short / Failed Connections",
        "tactic":     "Reconnaissance",
        "technique":  "T1595",
        "risk_level": "MEDIUM",
        "description": "Many very short connections detected — this pattern suggests the suspect was scanning for open systems to attack.",
        "detect_fn":  _detect_short_sessions,
    },
    {
        "pattern":    "Unusual Large Data Spike",
        "tactic":     "Collection",
        "technique":  "T1119",
        "risk_level": "MEDIUM",
        "description": "One or more sessions transferred an unusually large volume of data — possible bulk download of stolen documents.",
        "detect_fn":  _detect_data_spike,
    },
    {
        "pattern":    "VPN / Proxy Usage",
        "tactic":     "Defense Evasion",
        "technique":  "T1090",
        "risk_level": "HIGH",
        "description": "A VPN or proxy was used to mask the true location and identity of the suspect.",
        "detect_fn":  _detect_vpn,
    },
]


# ── Public API ────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def run_mitre_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all MITRE rules against the DataFrame.
    Returns a summary DataFrame of detected patterns.
    """
    results = []
    for rule in MITRE_RULES:
        try:
            mask  = rule["detect_fn"](df)
            count = int(mask.sum())
            if count > 0:
                results.append({
                    "Pattern Detected":  rule["pattern"],
                    "MITRE Tactic":      rule["tactic"],
                    "Technique ID":      rule["technique"],
                    "Risk Level":        rule["risk_level"],
                    "Sessions Affected": count,
                    "Plain Description": rule["description"],
                })
        except Exception:
            continue

    return pd.DataFrame(results) if results else pd.DataFrame(
        columns=["Pattern Detected", "MITRE Tactic", "Technique ID",
                 "Risk Level", "Sessions Affected", "Plain Description"]
    )


def get_risk_color(level: str) -> str:
    """Return hex color for a MITRE risk level string."""
    mapping = {
        "CRITICAL": COLOR_CRITICAL,
        "HIGH":     COLOR_HIGH,
        "MEDIUM":   "#FFD700",
        "LOW":      "#3FB950",
    }
    return mapping.get(level.upper(), "#8B949E")


def get_mitre_summary_text(mitre_df: pd.DataFrame) -> str:
    """Generate a plain-English summary paragraph for non-technical officers."""
    if mitre_df.empty:
        return "No suspicious patterns detected in this IPDR dataset."

    critical = len(mitre_df[mitre_df["Risk Level"] == "CRITICAL"])
    high     = len(mitre_df[mitre_df["Risk Level"] == "HIGH"])
    medium   = len(mitre_df[mitre_df["Risk Level"] == "MEDIUM"])

    parts = []
    if critical:
        parts.append(f"{critical} Critical-level threat(s)")
    if high:
        parts.append(f"{high} High-risk pattern(s)")
    if medium:
        parts.append(f"{medium} Medium-risk indicator(s)")

    summary = f"⚠ {', '.join(parts)} identified in the data. " if parts else ""
    
    # More natural, professional explanation
    if critical > 0:
        summary += (
            "Critical threats indicate use of anonymization tools (Tor/VPN), dark web access, "
            "or command-and-control activity. "
        )
    if high > 0:
        summary += (
            "High-risk patterns include suspicious data transfers, remote access attempts, "
            "or evasive behavior. "
        )
    if medium > 0:
        summary += "Medium-risk indicators suggest reconnaissance or data collection activity. "
    
    summary += "Further investigation and technical analysis recommended."
    
    return summary
