"""
generate_ipdr.py — Suराग Synthetic IPDR Data Generator
Run: python generate_ipdr.py
Output: data/sample_ipdr.csv (500 records)

Creates a realistic demo dataset with:
- 4 gang members (high-risk, coordinated activity)
- 2 innocent users (normal activity)
- Shared gang IPs across multiple suspects
- Tor exits, foreign IPs, off-hours activity
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Setup ─────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

os.makedirs("data", exist_ok=True)

# ── Suspects ──────────────────────────────────────────────
GANG_SUSPECTS = [
    {"id": "SUB-9876543210", "name": "Rahul Sharma",  "city": "Delhi",   "lat": 28.6139, "lon": 77.2090},
    {"id": "SUB-9812345670", "name": "Raj Kumar",     "city": "Mumbai",  "lat": 19.0760, "lon": 72.8777},
    {"id": "SUB-9834567890", "name": "Amit Verma",    "city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"id": "SUB-9856789010", "name": "Vikash Singh",  "city": "Patna",   "lat": 25.5941, "lon": 85.1376},
]

INNOCENT_USERS = [
    {"id": "SUB-9800001111", "name": "Priya Gupta",   "city": "Pune",    "lat": 18.5204, "lon": 73.8567},
    {"id": "SUB-9800002222", "name": "Suresh Nair",   "city": "Chennai", "lat": 13.0827, "lon": 80.2707},
]

# ── Shared Gang IPs (forensic evidence) ──────────────────
GANG_SHARED_IPS = {
    "103.21.58.12": ["SUB-9876543210", "SUB-9812345670", "SUB-9856789010"],  # Rahul + Raj + Vikash
    "103.21.58.14": ["SUB-9876543210", "SUB-9834567890"],                    # Rahul + Amit
    "49.36.72.11":  ["SUB-9812345670", "SUB-9834567890"],                    # Raj + Amit
}

# ── Tor Exit Nodes ────────────────────────────────────────
TOR_EXIT_NODES = [
    "185.220.101.45", "185.220.101.47", "185.220.102.8",
    "185.107.57.66",  "195.176.3.20",   "199.249.230.87",
    "204.8.156.142",  "162.247.74.27",
]

# ── Foreign C2 Servers ────────────────────────────────────
FOREIGN_IPS = [
    ("45.33.32.156",  "Cloudflare",    "USA",       37.7749, -122.4194),
    ("104.21.56.78",  "DigitalOcean",  "Germany",   52.5200,  13.4050),
    ("178.62.52.230", "Linode",        "Netherlands", 52.3676, 4.9041),
    ("91.108.56.179", "Telegram",      "Singapore", 1.3521,   103.8198),
    ("157.240.8.18",  "Facebook/Meta", "USA",       37.3861, -122.0839),
    ("172.217.14.206","Google",        "USA",       37.4419, -122.1430),
]

# ── Indian ISP IPs ────────────────────────────────────────
INDIAN_ISP_IPS = [
    ("122.177.14.5",   "Jio",         "Delhi",    28.6139, 77.2090),
    ("103.31.72.14",   "Airtel",      "Mumbai",   19.0760, 72.8777),
    ("14.139.34.5",    "BSNL",        "Bangalore", 12.9716, 77.5946),
    ("182.68.16.18",   "Vi",          "Hyderabad", 17.3850, 78.4867),
    ("59.144.122.45",  "ACT Fibernet","Pune",     18.5204, 73.8567),
    ("103.5.134.12",   "Hathway",     "Chennai",  13.0827, 80.2707),
    ("117.247.115.20", "Jio",         "Kolkata",  22.5726, 88.3639),
    ("49.207.48.22",   "Airtel",      "Patna",    25.5941, 85.1376),
]

# ── Protocols and Ports ───────────────────────────────────
PROTOCOLS = [
    ("HTTPS",     443,  "web"),
    ("HTTP",      80,   "web"),
    ("WhatsApp",  5222, "messaging"),
    ("Telegram",  443,  "messaging"),
    ("DNS",       53,   "dns"),
    ("SSH",       22,   "remote"),
    ("RDP",       3389, "remote"),
    ("SMB",       445,  "fileshare"),
    ("Tor",       9050, "proxy"),
    ("Paytm",     443,  "payment"),
]

BASE_DATE = datetime(2024, 3, 1, tzinfo=None)


def random_timestamp(is_gang: bool, gang_window: bool = False) -> datetime:
    """Generate timestamp — gang active 1AM–4AM, innocents normal hours."""
    days_offset = random.randint(0, 29)
    if is_gang and gang_window:
        hour = random.randint(1, 4)
    else:
        hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return BASE_DATE + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)


def is_off_hours(ts: datetime) -> bool:
    return 0 <= ts.hour < 5


def build_gang_record(suspect: dict, shared_ip_prob: float = 0.4) -> dict:
    """Build one IPDR row for a gang member."""
    ts = random_timestamp(is_gang=True, gang_window=random.random() < 0.7)

    use_tor     = random.random() < 0.3
    use_foreign = random.random() < 0.35
    use_shared  = random.random() < shared_ip_prob

    # Destination IP selection
    if use_shared:
        candidate_shared = [ip for ip, subs in GANG_SHARED_IPS.items() if suspect["id"] in subs]
        if candidate_shared:
            dest_ip = random.choice(candidate_shared)
            dest_city, dest_isp = "Unknown", "Unknown"
            dest_lat, dest_lon = 0.0, 0.0
            is_foreign = True
        else:
            use_shared = False

    if use_tor and not use_shared:
        dest_ip   = random.choice(TOR_EXIT_NODES)
        dest_city = "Tor Network"
        dest_isp  = "Tor Exit Node"
        dest_lat, dest_lon = random.uniform(-60, 60), random.uniform(-180, 180)
        is_foreign = True
    elif use_foreign and not use_shared:
        f = random.choice(FOREIGN_IPS)
        dest_ip, dest_isp, dest_city, dest_lat, dest_lon = f
        is_foreign = True
    elif not use_shared:
        i = random.choice(INDIAN_ISP_IPS)
        dest_ip, dest_isp, dest_city, dest_lat, dest_lon = i
        is_foreign = False

    proto, port, _ = random.choice(PROTOCOLS)
    if use_tor:
        proto, port = "Tor", 9050

    data_bytes = int(np.random.lognormal(mean=13, sigma=2))  # Skewed towards large

    # Source IP (suspect's device)
    src_ip_pool = [entry[0] for entry in INDIAN_ISP_IPS]
    src_ip = random.choice(src_ip_pool)

    return {
        "Subscriber_ID":       suspect["id"],
        "Subscriber_Name":     suspect["name"],
        "Source_IP":           src_ip,
        "Source_Port":         random.randint(1024, 65535),
        "Destination_IP":      dest_ip,
        "Destination_Port":    port,
        "App_Protocol":        proto,
        "Timestamp":           ts.strftime("%Y-%m-%d %H:%M:%S"),
        "Data_Volume_Bytes":   data_bytes,
        "ISP":                 random.choice(["Jio", "Airtel", "BSNL", "Vi"]),
        "City":                suspect["city"],
        "Latitude":            suspect["lat"],
        "Longitude":           suspect["lon"],
        "Is_Foreign_IP":       is_foreign,
        "Is_TOR":              use_tor or dest_ip in TOR_EXIT_NODES,
        "Is_Off_Hours":        is_off_hours(ts),
        "Is_VPN_Suspected":    random.random() < 0.2,
        "Session_Duration_sec": random.randint(10, 3600),
    }


def build_innocent_record(user: dict) -> dict:
    """Build one IPDR row for an innocent user — normal daytime activity."""
    ts = random_timestamp(is_gang=False)

    i = random.choice(INDIAN_ISP_IPS)
    dest_ip, dest_isp, dest_city, dest_lat, dest_lon = i

    proto, port, _ = random.choice([
        ("HTTPS", 443, "web"), ("HTTP", 80, "web"),
        ("WhatsApp", 5222, "messaging"), ("DNS", 53, "dns"),
        ("Paytm", 443, "payment"),
    ])

    return {
        "Subscriber_ID":       user["id"],
        "Subscriber_Name":     user["name"],
        "Source_IP":           random.choice([entry[0] for entry in INDIAN_ISP_IPS]),
        "Source_Port":         random.randint(1024, 65535),
        "Destination_IP":      dest_ip,
        "Destination_Port":    port,
        "App_Protocol":        proto,
        "Timestamp":           ts.strftime("%Y-%m-%d %H:%M:%S"),
        "Data_Volume_Bytes":   random.randint(1000, 500000),
        "ISP":                 random.choice(["Jio", "Airtel", "ACT Fibernet", "Hathway"]),
        "City":                user["city"],
        "Latitude":            user["lat"],
        "Longitude":           user["lon"],
        "Is_Foreign_IP":       False,
        "Is_TOR":              False,
        "Is_Off_Hours":        is_off_hours(ts),
        "Is_VPN_Suspected":    False,
        "Session_Duration_sec": random.randint(30, 1800),
    }


def main():
    records = []

    # 100 records per gang member (400 total)
    for suspect in GANG_SUSPECTS:
        for _ in range(100):
            records.append(build_gang_record(suspect))

    # 50 records per innocent user (100 total)
    for user in INNOCENT_USERS:
        for _ in range(50):
            records.append(build_innocent_record(user))

    df = pd.DataFrame(records)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp").reset_index(drop=True)

    output_path = os.path.join("data", "sample_ipdr.csv")
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated {len(df)} IPDR records -> {output_path}")
    print(f"\nSuspects breakdown:")
    for s in GANG_SUSPECTS:
        count = len(df[df["Subscriber_ID"] == s["id"]])
        print(f"   [HIGH RISK] {s['name']} ({s['id']}): {count} records")
    for u in INNOCENT_USERS:
        count = len(df[df["Subscriber_ID"] == u["id"]])
        print(f"   [INNOCENT]  {u['name']} ({u['id']}): {count} records")

    print(f"\nShared gang IPs embedded:")
    for ip, subs in GANG_SHARED_IPS.items():
        count = len(df[df["Destination_IP"] == ip])
        print(f"   {ip} -> found in {count} sessions across {len(subs)} suspects")


if __name__ == "__main__":
    main()
