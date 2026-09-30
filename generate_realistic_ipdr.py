"""
generate_realistic_ipdr.py — Generate realistic IPDR sample data
in the real DoT India format (DS-16/13/2017-DS-III).

Generates:
  - Single suspect IPDR (for single analysis demo)
  - Multi-suspect IPDR with gang connections (for correlation demo)

Output files saved to data/ folder.
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ── Indian cell tower IDs (realistic format) ──────────────────────────────────
CELL_TOWERS_DELHI = [
    "DL-RCH-001", "DL-RCH-002", "DL-DWK-001", "DL-DWK-002",
    "DL-SHD-001", "DL-SHD-002", "DL-NHD-001", "DL-GTB-001",
]
CELL_TOWERS_GURGAON = [
    "HR-GGN-001", "HR-GGN-002", "HR-GGN-003", "HR-GGN-004",
    "HR-GGN-005", "HR-GGN-006",
]
CELL_TOWERS_NOIDA = [
    "UP-NOD-001", "UP-NOD-002", "UP-NOD-003", "UP-NOD-004",
]

# ── ISPs ──────────────────────────────────────────────────────────────────────
ISPS = ["Reliance Jio", "Airtel", "BSNL", "Vi (Vodafone Idea)", "ACT Fibernet"]

# ── RAT types ─────────────────────────────────────────────────────────────────
RAT_TYPES = ["4G", "5G", "4G", "4G", "3G", "5G"]

# ── Known suspicious IPs (for demo) ──────────────────────────────────────────
TOR_EXIT_IPS = [
    "185.220.101.45", "185.220.102.8", "185.107.47.215",
    "195.176.3.19",   "199.249.230.87",
]
FOREIGN_IPS = [
    "104.21.44.1", "172.67.181.2", "13.107.42.14",
    "52.114.128.10", "34.117.59.81", "157.240.22.35",
    "74.125.130.95", "31.13.72.36",  "91.108.4.12",
]
INDIAN_IPS = [
    "49.36.72.15",  "49.36.72.16",  "49.36.72.17",
    "122.160.36.1", "122.160.36.2", "103.1.201.11",
    "59.90.125.10", "14.139.60.10", "182.74.162.9",
    "1.22.140.255", "27.57.65.200",
]
PAYMENT_IPS = [
    "103.139.60.101",   # UPI gateway (demo)
    "182.71.203.55",    # Payment processor (demo)
    "49.205.153.90",    # Bank server (demo)
]


def make_msisdn() -> str:
    """Generate realistic Indian mobile number."""
    prefixes = ["9", "8", "7", "6"]
    return random.choice(prefixes) + "".join([str(random.randint(0, 9)) for _ in range(9)])


def make_imsi(msisdn: str) -> str:
    """Generate IMSI from MSISDN (404 = India MCC, 10/20 = Airtel/Jio MNC)."""
    mnc = random.choice(["10", "20", "86", "01"])
    return f"404{mnc}{msisdn}"


def make_imei() -> str:
    """Generate realistic IMEI (15 digits)."""
    tac = random.choice(["35742106", "35874907", "86803804", "35403110"])
    serial = "".join([str(random.randint(0, 9)) for _ in range(6)])
    luhn   = str(random.randint(0, 9))
    return tac + serial + luhn


def make_session(
    msisdn: str,
    imsi: str,
    imei: str,
    start_dt: datetime,
    isp: str,
    cell_towers: list,
    profile: str = "normal",
) -> dict:
    """
    Generate a single IPDR session record.

    Profiles:
      normal      — everyday browsing
      suspicious  — off-hours, foreign, VPN
      fraud       — Tor, RAT ports, SMPP
      gang_shared — uses shared criminal IP
    """
    duration = random.randint(10, 3600)
    end_dt   = start_dt + timedelta(seconds=duration)

    if profile == "fraud":
        dest_ip   = random.choice(TOR_EXIT_IPS + FOREIGN_IPS)
        dest_port = random.choice([9050, 9001, 5900, 4444, 2775, 22, 3389])
        ul = random.randint(500_000, 5_000_000)
        dl = random.randint(100_000, 500_000)   # High upload = exfiltration
        protocol  = "TCP"
    elif profile == "suspicious":
        dest_ip   = random.choice(FOREIGN_IPS)
        dest_port = random.choice([443, 80, 1194, 1080])
        ul = random.randint(50_000, 500_000)
        dl = random.randint(200_000, 2_000_000)
        protocol  = random.choice(["TCP", "UDP"])
    elif profile == "gang_shared":
        dest_ip   = "185.220.101.45"   # Shared Tor exit = shared criminal server
        dest_port = random.choice([9050, 443, 80])
        ul = random.randint(10_000, 100_000)
        dl = random.randint(10_000, 100_000)
        protocol  = "TCP"
    else:
        dest_ip   = random.choice(INDIAN_IPS + PAYMENT_IPS + FOREIGN_IPS[:3])
        dest_port = random.choice([443, 80, 443, 443, 53])
        ul = random.randint(1_000, 100_000)
        dl = random.randint(10_000, 2_000_000)
        protocol  = random.choice(["TCP", "UDP", "TCP", "TCP"])

    source_ip   = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    source_port = random.randint(1024, 65535)

    return {
        "MSISDN":             msisdn,
        "IMSI":               imsi,
        "IMEI":               imei,
        "Source_IP":          source_ip,
        "Source_Port":        source_port,
        "Destination_IP":     dest_ip,
        "Destination_Port":   dest_port,
        "Session_Start_Time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Session_End_Time":   end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Uplink_Volume":      ul,
        "Downlink_Volume":    dl,
        "Protocol":           protocol,
        "RAT_Type":           random.choice(RAT_TYPES),
        "Cell_ID":            random.choice(cell_towers),
        "LAC":                random.choice(["4201", "4202", "4203", "4204"]),
        "NAS_IP":             f"203.{random.randint(100,200)}.{random.randint(0,255)}.1",
        "ISP":                isp,
    }


def generate_suspect(
    name: str,
    num_sessions: int = 80,
    fraud_ratio: float = 0.2,
    suspicious_ratio: float = 0.3,
    cell_towers: list = None,
    shared_imei: str = None,
    gang_shared_ratio: float = 0.0,
) -> pd.DataFrame:
    """Generate IPDR records for one suspect."""
    if cell_towers is None:
        cell_towers = CELL_TOWERS_DELHI

    msisdn = make_msisdn()
    imsi   = make_imsi(msisdn)
    imei   = shared_imei if shared_imei else make_imei()
    isp    = random.choice(ISPS)

    # Date range: last 30 days
    base_date = datetime(2026, 8, 15, 0, 0, 0)
    records   = []

    for _ in range(num_sessions):
        rand_val = random.random()

        # Determine time: suspicious = off-hours (0-5 AM)
        if rand_val < fraud_ratio + suspicious_ratio:
            hour   = random.randint(0, 4)   # off-hours
        else:
            hour   = random.randint(8, 22)  # normal hours

        day    = random.randint(0, 29)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt     = base_date + timedelta(days=day, hours=hour, minutes=minute, seconds=second)

        if rand_val < fraud_ratio:
            profile = "fraud"
        elif rand_val < fraud_ratio + gang_shared_ratio:
            profile = "gang_shared"
        elif rand_val < fraud_ratio + gang_shared_ratio + suspicious_ratio:
            profile = "suspicious"
        else:
            profile = "normal"

        rec = make_session(msisdn, imsi, imei, dt, isp, cell_towers, profile)
        rec["Subscriber_Name"] = name
        records.append(rec)

    return pd.DataFrame(records).sort_values("Session_Start_Time").reset_index(drop=True)


def main():
    os.makedirs("data", exist_ok=True)

    # ── 1. Single suspect — financial fraud case ──────────────────────────────
    print("Generating single suspect IPDR (financial fraud case)...")
    df_single = generate_suspect(
        name="Rahul Sharma",
        num_sessions=120,
        fraud_ratio=0.35,
        suspicious_ratio=0.25,
        cell_towers=CELL_TOWERS_DELHI,
    )
    df_single.to_csv("data/suspect_rahul_sharma_ipdr.csv", index=False)
    print(f"  → data/suspect_rahul_sharma_ipdr.csv ({len(df_single)} sessions)")

    # ── 2. Gang case — 3 suspects with shared IMEI + shared IPs ──────────────
    print("\nGenerating gang IPDR (3 suspects, shared IMEI + shared infrastructure)...")

    # Shared IMEI — proves they share a device (SIM swap / gang coordination)
    gang_imei = make_imei()

    df_gang1 = generate_suspect(
        name="Vikram Tomar",
        num_sessions=100,
        fraud_ratio=0.30,
        suspicious_ratio=0.20,
        gang_shared_ratio=0.15,
        cell_towers=CELL_TOWERS_GURGAON,
        shared_imei=gang_imei,
    )
    df_gang2 = generate_suspect(
        name="Deepak Rawat",
        num_sessions=90,
        fraud_ratio=0.25,
        suspicious_ratio=0.25,
        gang_shared_ratio=0.15,
        cell_towers=CELL_TOWERS_GURGAON + CELL_TOWERS_DELHI[:2],
        shared_imei=gang_imei,   # Same IMEI as Vikram
    )
    df_gang3 = generate_suspect(
        name="Priya Mehta",
        num_sessions=80,
        fraud_ratio=0.20,
        suspicious_ratio=0.30,
        gang_shared_ratio=0.10,
        cell_towers=CELL_TOWERS_NOIDA,
        # Different IMEI but shares destination IPs via gang_shared profile
    )

    df_gang1.to_csv("data/suspect_vikram_tomar_ipdr.csv", index=False)
    df_gang2.to_csv("data/suspect_deepak_rawat_ipdr.csv", index=False)
    df_gang3.to_csv("data/suspect_priya_mehta_ipdr.csv", index=False)

    print(f"  → data/suspect_vikram_tomar_ipdr.csv  ({len(df_gang1)} sessions)")
    print(f"  → data/suspect_deepak_rawat_ipdr.csv  ({len(df_gang2)} sessions)")
    print(f"  → data/suspect_priya_mehta_ipdr.csv   ({len(df_gang3)} sessions)")
    print(f"  → Shared IMEI: {gang_imei} (Vikram ↔ Deepak)")

    print("\n✅ All sample IPDR files generated in data/ folder.")
    print("\nColumns in each file:")
    print("  MSISDN, IMSI, IMEI, Source_IP, Source_Port,")
    print("  Destination_IP, Destination_Port, Session_Start_Time, Session_End_Time,")
    print("  Uplink_Volume, Downlink_Volume, Protocol, RAT_Type,")
    print("  Cell_ID, LAC, NAS_IP, ISP, Subscriber_Name")


if __name__ == "__main__":
    main()
