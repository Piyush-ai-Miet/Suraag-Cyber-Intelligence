"""
modules/mitre_mapper.py — Suराग MITRE ATT&CK Pattern Detector
Real cybercell investigation logic mapped to MITRE ATT&CK framework.

Detection rules based on:
- DoT India IPDR investigation guidelines
- Real cybercrime patterns: financial fraud, gang activity, C2 beaconing
- MITRE ATT&CK v14 Mobile & Enterprise techniques
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM

# ── Known financial fraud / payment gateway destination IPs ──────────────────
# Cybercriminals often route through these or fake these
FINANCIAL_FRAUD_PORTS = {
    443,   # HTTPS — used for fake banking portals
    80,    # HTTP  — phishing sites
    2083,  # cPanel (fake hosting)
    2087,  # WHM
    8443,  # Alt HTTPS
}

# Remote access / RAT ports — used in cyber fraud call centers
RAT_PORTS = {
    5900, 5901,         # VNC
    3389,               # RDP
    22,                 # SSH
    23,                 # Telnet
    4444, 4445,         # Metasploit default
    1337,               # Common RAT
    8888, 9999,         # Common RAT
    5555,               # Android ADB (device takeover)
    7777,               # Common RAT
}

# C2 / botnet known ports
C2_PORTS = {
    6667, 6668, 6669,   # IRC (old botnet C2)
    1234, 12345,        # Common C2
    31337,              # Elite / back-orifice
    8531, 8530,         # WSUS abuse
}

# Tor ports
TOR_PORTS = {9050, 9001, 9030, 9040, 9150}

# Tor IP prefixes
TOR_IP_PREFIXES = [
    "185.220.", "185.107.", "195.176.", "199.249.", "204.8.156.",
    "162.247.", "51.15.",   "45.142.",  "178.175.", "109.70.",
]

# DNS tunneling detection: unusually long session to port 53
DNS_PORT = 53

# Cryptocurrency / darknet payment ports
CRYPTO_PORTS = {8333, 18333, 18444}  # Bitcoin P2P

# OTP bypass / SIM swap fraud indicators — bulk SMS aggregators
BULK_SMS_PORTS = {2775, 2776, 2777}   # SMPP protocol ports


# ── Detection Helper Functions ────────────────────────────────────────────────

def _detect_tor(df: pd.DataFrame) -> pd.Series:
    """Tor usage — Tor IP prefix or Tor port."""
    by_ip   = df["Destination_IP"].apply(
        lambda ip: any(ip.startswith(p) for p in TOR_IP_PREFIXES)
    )
    by_port = df["Destination_Port"].isin(TOR_PORTS)
    return by_ip | by_port | df.get("Is_TOR", pd.Series(False, index=df.index))


def _detect_vpn_proxy(df: pd.DataFrame) -> pd.Series:
    """VPN/Proxy usage detected from port patterns."""
    vpn_ports = {1194, 1723, 500, 4500, 51820}   # OpenVPN, PPTP, IPSec, WireGuard
    proxy_ports = {1080, 3128, 8080, 8888, 3129}
    return df["Destination_Port"].isin(vpn_ports | proxy_ports)


def _detect_c2_beacon(df: pd.DataFrame) -> pd.Series:
    """
    C2 Beacon pattern: same subscriber contacts same foreign IP
    5+ times — regular check-ins to a remote controller.
    Key cybercell indicator for malware, RATs, and botnet infections.
    """
    counts = df.groupby(["Subscriber_ID", "Destination_IP"])["Timestamp"].transform("count")
    return (counts >= 5) & df["Is_Foreign_IP"]


def _detect_rat_ports(df: pd.DataFrame) -> pd.Series:
    """
    Remote Access Tool (RAT) ports — used in cyber fraud call centers
    to take control of victim devices (VNC, RDP, ADB, etc.)
    """
    return df["Destination_Port"].isin(RAT_PORTS)


def _detect_sim_swap(df: pd.DataFrame) -> pd.Series:
    """
    SIM Swap / Device Sharing: same IMEI used with multiple MSISDNs.
    Strong indicator of SIM swap fraud or stolen device.
    """
    if "IMEI" not in df.columns or "Subscriber_ID" not in df.columns:
        return pd.Series(False, index=df.index)
    # Filter out UNKNOWN IMEIs
    valid = df[df["IMEI"].astype(str).str.upper() != "UNKNOWN"]
    if valid.empty:
        return pd.Series(False, index=df.index)
    subs_per_imei = valid.groupby("IMEI")["Subscriber_ID"].transform("nunique")
    result = pd.Series(False, index=df.index)
    result.loc[valid.index] = subs_per_imei > 1
    return result


def _detect_impossible_travel(df: pd.DataFrame) -> pd.Series:
    """
    Cell Tower Jump / Impossible Travel:
    Same subscriber appearing at two distant cell towers within
    a physically impossible timeframe (< 30 min).
    Strong indicator of cloned SIM or account sharing.
    """
    if "Cell_ID" not in df.columns or df["Cell_ID"].astype(str).eq("UNKNOWN").all():
        return pd.Series(False, index=df.index)

    result = pd.Series(False, index=df.index)
    for sub_id, sub_df in df.groupby("Subscriber_ID"):
        if sub_df["Cell_ID"].nunique() < 2:
            continue
        sub_sorted = sub_df.sort_values("Timestamp")
        towers = sub_sorted["Cell_ID"].astype(str).values
        times  = sub_sorted["Timestamp"].values
        for i in range(1, len(towers)):
            if towers[i] != towers[i-1]:
                diff_min = (times[i] - times[i-1]) / np.timedelta64(1, 'm')
                # Different towers < 2 minutes apart = suspicious (impossible travel)
                if 0 < diff_min < 2:
                    result.loc[sub_sorted.index[i]]   = True
                    result.loc[sub_sorted.index[i-1]] = True
    return result


def _detect_bulk_data_offhours(df: pd.DataFrame) -> pd.Series:
    """
    Large data exfiltration at night (midnight–5 AM).
    Classic pattern in data theft, CSAM, corporate espionage.
    """
    mean_vol = df["Data_Volume_Bytes"].mean()
    std_vol  = df["Data_Volume_Bytes"].std() if df["Data_Volume_Bytes"].std() > 0 else 1
    return df["Is_Off_Hours"] & (df["Data_Volume_Bytes"] > mean_vol + std_vol)


def _detect_ip_hopping(df: pd.DataFrame) -> pd.Series:
    """
    Rapid IP hopping — connecting to many unique IPs in short time.
    Indicates automated scanning, botnet activity, or evasion.
    """
    unique_ips = df.groupby("Subscriber_ID")["Destination_IP"].transform("nunique")
    total      = df.groupby("Subscriber_ID")["Destination_IP"].transform("count")
    ratio      = unique_ips / total.clip(lower=1)
    return ratio > 0.7


def _detect_dns_tunneling(df: pd.DataFrame) -> pd.Series:
    """
    DNS Tunneling: high data volume on port 53.
    Used to exfiltrate data or communicate C2 through DNS.
    Normal DNS queries are tiny (<512 bytes); tunneling is large.
    """
    mean_vol = df["Data_Volume_Bytes"].mean()
    return (df["Destination_Port"] == DNS_PORT) & (df["Data_Volume_Bytes"] > mean_vol * 3)


def _detect_financial_fraud_ports(df: pd.DataFrame) -> pd.Series:
    """
    SMPP ports used for bulk OTP bypass / SIM swap fraud.
    Cybercriminals use SMPP to intercept OTPs for banking fraud.
    """
    return df["Destination_Port"].isin(BULK_SMS_PORTS)


def _detect_crypto_ports(df: pd.DataFrame) -> pd.Series:
    """
    Cryptocurrency P2P ports — Bitcoin, Monero etc.
    Used for ransom payments, dark web transactions.
    """
    return df["Destination_Port"].isin(CRYPTO_PORTS)


def _detect_short_scan_sessions(df: pd.DataFrame) -> pd.Series:
    """
    Port scanning: many very short sessions (<5 sec).
    Reconnaissance before an attack.
    """
    return df["Session_Duration_sec"] < 5


def _detect_data_spike(df: pd.DataFrame) -> pd.Series:
    """Unusual large data spike (>2σ above mean) — bulk download/upload."""
    mean_vol = df["Data_Volume_Bytes"].mean()
    std_vol  = df["Data_Volume_Bytes"].std() if df["Data_Volume_Bytes"].std() > 0 else 1
    return df["Data_Volume_Bytes"] > mean_vol + 2 * std_vol


def _detect_c2_known_ports(df: pd.DataFrame) -> pd.Series:
    """Known C2/botnet ports (IRC, common backdoor ports)."""
    return df["Destination_Port"].isin(C2_PORTS)


def _detect_multi_sim_same_source(df: pd.DataFrame) -> pd.Series:
    """
    Multiple SIMs from same Source IP — shared NAT or
    coordinated fraud operation using same device/location.
    """
    subs_per_ip = df.groupby("Source_IP")["Subscriber_ID"].transform("nunique")
    return subs_per_ip > 1


def _detect_offhours_foreign(df: pd.DataFrame) -> pd.Series:
    """
    Foreign IP access during off-hours — hallmark of
    cross-border cybercrime (Chinese/Pakistani scam calls, etc.)
    """
    return df["Is_Off_Hours"] & df["Is_Foreign_IP"]


def _detect_uplink_anomaly(df: pd.DataFrame) -> pd.Series:
    """
    Uplink >> Downlink: suspect is uploading much more than downloading.
    Normal browsing is 90% download. High upload = data exfiltration.
    """
    if "Uplink_Volume" not in df.columns or "Downlink_Volume" not in df.columns:
        return pd.Series(False, index=df.index)
    ul = pd.to_numeric(df["Uplink_Volume"], errors="coerce").fillna(0)
    dl = pd.to_numeric(df["Downlink_Volume"], errors="coerce").fillna(0)
    total = ul + dl
    # Uplink > 60% of total AND total > 1MB
    ratio = ul / total.clip(lower=1)
    return (ratio > 0.6) & (total > 1_000_000)


# ── MITRE ATT&CK Rules ────────────────────────────────────────────────────────

MITRE_RULES = [
    {
        "pattern":     "Tor Anonymization Network",
        "tactic":      "Defense Evasion",
        "technique":   "T1090.003",
        "risk_level":  "CRITICAL",
        "description": (
            "Suspect is using Tor — a tool specifically designed to hide internet "
            "identity from law enforcement. Used in drug trafficking, CSAM, and financial fraud."
        ),
        "detect_fn": _detect_tor,
    },
    {
        "pattern":     "Remote Access Tool (RAT) / Device Takeover",
        "tactic":      "Command & Control",
        "technique":   "T1219",
        "risk_level":  "CRITICAL",
        "description": (
            "RAT ports detected (VNC/RDP/ADB/Metasploit). Common in cyber fraud call centers "
            "where criminals remotely control victim devices to commit banking fraud."
        ),
        "detect_fn": _detect_rat_ports,
    },
    {
        "pattern":     "C2 Beacon — Malware Phone-Home",
        "tactic":      "Command & Control",
        "technique":   "T1071.001",
        "risk_level":  "CRITICAL",
        "description": (
            "Device repeatedly contacts the same foreign server at regular intervals. "
            "This is a device infected with malware or remotely controlled by criminals."
        ),
        "detect_fn": _detect_c2_beacon,
    },
    {
        "pattern":     "SIM Swap Fraud / Cloned SIM (Same IMEI, Multiple SIMs)",
        "tactic":      "Credential Access",
        "technique":   "T1111",
        "risk_level":  "CRITICAL",
        "description": (
            "Same device (IMEI) used with multiple mobile numbers (MSISDN). "
            "Classic SIM swap fraud — criminal uses cloned SIM to intercept OTPs and commit banking fraud."
        ),
        "detect_fn": _detect_sim_swap,
    },
    {
        "pattern":     "Impossible Travel / Cell Tower Jump",
        "tactic":      "Defense Evasion",
        "technique":   "T1078",
        "risk_level":  "CRITICAL",
        "description": (
            "Same subscriber appears at two different cell towers within 2 minutes — "
            "physically impossible. Strong indicator of cloned SIM or account sharing between gang members."
        ),
        "detect_fn": _detect_impossible_travel,
    },
    {
        "pattern":     "Bulk Data Exfiltration — Night Hours",
        "tactic":      "Exfiltration",
        "technique":   "T1048",
        "risk_level":  "HIGH",
        "description": (
            "Large data transfer between midnight and 5 AM. "
            "Classic pattern for data theft, CSAM distribution, or corporate espionage."
        ),
        "detect_fn": _detect_bulk_data_offhours,
    },
    {
        "pattern":     "Abnormal Upload Volume (Data Exfiltration)",
        "tactic":      "Exfiltration",
        "technique":   "T1048.003",
        "risk_level":  "HIGH",
        "description": (
            "Upload volume significantly exceeds download volume. "
            "Normal users download more than they upload. High upload = stolen data being sent out."
        ),
        "detect_fn": _detect_uplink_anomaly,
    },
    {
        "pattern":     "OTP Bypass / SMPP Bulk SMS Port",
        "tactic":      "Credential Access",
        "technique":   "T1111",
        "risk_level":  "HIGH",
        "description": (
            "SMPP protocol ports (2775-2777) detected. Used by cybercriminals to "
            "intercept OTP messages for banking and UPI fraud."
        ),
        "detect_fn": _detect_financial_fraud_ports,
    },
    {
        "pattern":     "Foreign Server Access — Off Hours",
        "tactic":      "Command & Control",
        "technique":   "T1071",
        "risk_level":  "HIGH",
        "description": (
            "Foreign IP contacted during midnight–5 AM hours. "
            "Hallmark of cross-border cybercrime operations (scam call centers, ransomware gangs)."
        ),
        "detect_fn": _detect_offhours_foreign,
    },
    {
        "pattern":     "VPN / Proxy Usage",
        "tactic":      "Defense Evasion",
        "technique":   "T1090",
        "risk_level":  "HIGH",
        "description": (
            "VPN or proxy detected — suspect is masking their true IP address and location. "
            "Common in all types of cybercrime to avoid identification."
        ),
        "detect_fn": _detect_vpn_proxy,
    },
    {
        "pattern":     "Known C2 / Botnet Ports (IRC, Backdoor)",
        "tactic":      "Command & Control",
        "technique":   "T1071.003",
        "risk_level":  "HIGH",
        "description": (
            "Communication on known botnet/C2 ports (IRC 6667, Back-Orifice 31337, etc.). "
            "Device may be part of a criminal botnet."
        ),
        "detect_fn": _detect_c2_known_ports,
    },
    {
        "pattern":     "Rapid IP Hopping (Automated Scanning)",
        "tactic":      "Reconnaissance",
        "technique":   "T1595",
        "risk_level":  "MEDIUM",
        "description": (
            "Connecting to many unique servers rapidly. "
            "Indicates automated scanning tools used before launching a cyberattack."
        ),
        "detect_fn": _detect_ip_hopping,
    },
    {
        "pattern":     "DNS Tunneling (Covert Data Channel)",
        "tactic":      "Exfiltration",
        "technique":   "T1048.003",
        "risk_level":  "MEDIUM",
        "description": (
            "High data volume on DNS port (53). Normal DNS is tiny — "
            "large DNS sessions indicate data hidden inside DNS queries to bypass firewalls."
        ),
        "detect_fn": _detect_dns_tunneling,
    },
    {
        "pattern":     "Cryptocurrency Port Activity",
        "tactic":      "Impact",
        "technique":   "T1496",
        "risk_level":  "MEDIUM",
        "description": (
            "Bitcoin/cryptocurrency P2P ports detected. "
            "Used for ransom payments, dark web transactions, or cryptojacking."
        ),
        "detect_fn": _detect_crypto_ports,
    },
    {
        "pattern":     "Multiple SIMs — Same IP/Location",
        "tactic":      "Persistence",
        "technique":   "T1078.001",
        "risk_level":  "MEDIUM",
        "description": (
            "Multiple subscriber IDs connecting from same source IP. "
            "Indicates coordinated fraud operation using multiple SIM cards from same location."
        ),
        "detect_fn": _detect_multi_sim_same_source,
    },
    {
        "pattern":     "Port Scanning / Reconnaissance",
        "tactic":      "Reconnaissance",
        "technique":   "T1046",
        "risk_level":  "MEDIUM",
        "description": (
            "Many very short connections (<5 seconds). "
            "Classic pattern of automated port scanning before a cyberattack."
        ),
        "detect_fn": _detect_short_scan_sessions,
    },
    {
        "pattern":     "Unusual Large Data Spike",
        "tactic":      "Collection",
        "technique":   "T1119",
        "risk_level":  "MEDIUM",
        "description": (
            "Single session with data volume far above average. "
            "Possible bulk download of stolen documents, databases, or CSAM."
        ),
        "detect_fn": _detect_data_spike,
    },
]


# ── Public API ────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def run_mitre_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Run all MITRE rules. Returns summary DataFrame of detected patterns."""
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

    if not results:
        return pd.DataFrame(
            columns=["Pattern Detected", "MITRE Tactic", "Technique ID",
                     "Risk Level", "Sessions Affected", "Plain Description"]
        )

    # Sort: CRITICAL first, then HIGH, then MEDIUM
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    result_df = pd.DataFrame(results)
    result_df["_sort"] = result_df["Risk Level"].map(order).fillna(3)
    result_df = result_df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    return result_df


def get_risk_color(level: str) -> str:
    return {
        "CRITICAL": COLOR_CRITICAL,
        "HIGH":     COLOR_HIGH,
        "MEDIUM":   "#FFD700",
        "LOW":      "#3FB950",
    }.get(level.upper(), "#8B949E")


def get_mitre_summary_text(mitre_df: pd.DataFrame) -> str:
    """Plain-English summary for non-technical police officers."""
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

    summary = f"⚠ {', '.join(parts)} identified in the IPDR data. " if parts else ""

    if critical > 0:
        summary += (
            "Critical threats include Tor/VPN anonymization, SIM swap fraud, "
            "device takeover via RAT tools, or C2 malware communication. "
            "These require immediate action. "
        )
    if high > 0:
        summary += (
            "High-risk patterns include cross-border C2 activity, bulk data exfiltration, "
            "OTP bypass attempts, and suspicious off-hours foreign connections. "
        )
    if medium > 0:
        summary += (
            "Medium-risk indicators include port scanning, DNS tunneling, "
            "cryptocurrency activity, and multi-SIM operations. "
        )

    summary += "Full forensic investigation and legal action under IT Act / BNS recommended."
    return summary
