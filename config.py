"""
config.py — Suराग Configuration Loader
Loads environment variables and provides app-wide constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── App Metadata ──────────────────────────────────────────
APP_NAME        = "Suराग"
APP_TAGLINE     = "Woh dekho jo data chhupata hai"
APP_SUBTITLE    = "Cyber Intelligence & IPDR Analysis Platform"
APP_VERSION     = "1.0.0"
APP_ORG         = "Gurugram Police Cyber Security Summer Internship 2026"
APP_ADVISOR     = "Dr. Rakshit Tandon"

# ── Design Tokens ─────────────────────────────────────────
COLOR_BG        = "#0D1117"
COLOR_CARD      = "#161B22"
COLOR_BORDER    = "#30363D"
COLOR_ACCENT    = "#00D4FF"
COLOR_TEXT      = "#E6EDF3"
COLOR_MUTED     = "#8B949E"
COLOR_CRITICAL  = "#FF4444"
COLOR_HIGH      = "#FF8C00"
COLOR_MEDIUM    = "#FFD700"
COLOR_LOW       = "#00D4FF"
COLOR_OK        = "#3FB950"

# ── Risk Score Thresholds ─────────────────────────────────
RISK_CRITICAL_MIN = 80
RISK_HIGH_MIN     = 60
RISK_MEDIUM_MIN   = 40

# ── Off-Hours Window (IST) ────────────────────────────────
OFF_HOURS_START = 0   # 12 AM
OFF_HOURS_END   = 5   # 5 AM

# ── Geolocation API ───────────────────────────────────────
GEO_API_URL     = "http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,lat,lon,proxy,hosting"
GEO_BATCH_SIZE  = 50  # IPs per batch

# ── Known Suspicious Port Ranges ─────────────────────────
SUSPICIOUS_PORTS = {
    22:   "SSH (Remote Access)",
    23:   "Telnet (Unencrypted Remote)",
    445:  "SMB (File Sharing Exploit)",
    3389: "RDP (Remote Desktop)",
    4444: "Metasploit Default",
    6667: "IRC (Botnet C2)",
    9050: "Tor SOCKS Proxy",
    9001: "Tor OR Port",
    1080: "SOCKS Proxy",
}
