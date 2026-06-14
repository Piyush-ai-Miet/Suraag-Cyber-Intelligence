"""
generate_professional_ipdr.py — Complete Professional IPDR Format
Generates 500 records with ALL fields used by Cyber Crime Investigators

Run: python generate_professional_ipdr.py
Output: data/professional_ipdr.csv

IPDR Fields (As per DoT/LEA Standards):
- Subscriber Info (MSISDN, IMEI, IMSI)
- Network Data (IPs, Ports, Protocol)
- Data Usage (Upload/Download/Total bytes)
- Location (Cell ID, LAC, Lat/Long, City, State)
- App/Website Info (Domain, App Name, Service Type)
- Session Info (Start/End time, Duration)
- Device Info (Device model, OS, Browser)
- Behavioral Flags (VPN, Tor, Proxy, Encryption)
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker

# Initialize
fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

os.makedirs("data", exist_ok=True)

# ── Real App Names & Websites ────────────────────────────
APPS = [
    ("WhatsApp", "whatsapp.com", "Messaging", 5222),
    ("Instagram", "instagram.com", "Social Media", 443),
    ("Facebook", "facebook.com", "Social Media", 443),
    ("Telegram", "telegram.org", "Messaging", 443),
    ("YouTube", "youtube.com", "Video Streaming", 443),
    ("Netflix", "netflix.com", "Video Streaming", 443),
    ("Amazon", "amazon.in", "E-Commerce", 443),
    ("Flipkart", "flipkart.com", "E-Commerce", 443),
    ("Paytm", "paytm.com", "Payment", 443),
    ("PhonePe", "phonepe.com", "Payment", 443),
    ("Google Pay", "pay.google.com", "Payment", 443),
    ("Gmail", "gmail.com", "Email", 443),
    ("Twitter", "twitter.com", "Social Media", 443),
    ("LinkedIn", "linkedin.com", "Professional", 443),
    ("TikTok", "tiktok.com", "Social Media", 443),
    ("Snapchat", "snapchat.com", "Social Media", 443),
    ("Discord", "discord.com", "Messaging", 443),
    ("Signal", "signal.org", "Messaging", 443),
    ("Zoom", "zoom.us", "Video Call", 443),
    ("Google Meet", "meet.google.com", "Video Call", 443),
]

# ── Tor & VPN Services ───────────────────────────────────
TOR_EXITS = [
    "185.220.101.45", "185.220.101.47", "185.220.102.8",
    "199.249.230.87", "204.8.156.142", "162.247.74.27"
]

VPN_SERVICES = [
    ("NordVPN", "nordvpn.com"),
    ("ExpressVPN", "expressvpn.com"),
    ("ProtonVPN", "protonvpn.com"),
    ("TunnelBear", "tunnelbear.com"),
]

# ── Device Models ────────────────────────────────────────
DEVICES = [
    ("Samsung Galaxy S21", "Android 12", "Chrome Mobile"),
    ("iPhone 13 Pro", "iOS 16.2", "Safari"),
    ("OnePlus 9", "Android 11", "Chrome Mobile"),
    ("Xiaomi Redmi Note 10", "Android 11", "Chrome Mobile"),
    ("Realme 8 Pro", "Android 11", "Chrome Mobile"),
    ("Vivo V21", "Android 11", "Chrome Mobile"),
    ("Oppo F19", "Android 11", "Chrome Mobile"),
    ("iPhone 12", "iOS 15.5", "Safari"),
    ("Samsung Galaxy A52", "Android 11", "Samsung Internet"),
    ("Google Pixel 6", "Android 13", "Chrome Mobile"),
]

# ── ISP & Cell Tower Data ────────────────────────────────
ISP_DATA = [
    {"isp": "Jio", "operator_id": "40411", "circle": "Delhi"},
    {"isp": "Airtel", "operator_id": "40410", "circle": "Delhi"},
    {"isp": "Vi (Vodafone Idea)", "operator_id": "40405", "circle": "Mumbai"},
    {"isp": "BSNL", "operator_id": "40401", "circle": "Karnataka"},
]

# ── Cities with Tower Data ───────────────────────────────
CITIES = [
    {"city": "Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "lac": 2001, "cell_id_start": 10001},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "lac": 2002, "cell_id_start": 20001},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "lac": 2003, "cell_id_start": 30001},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "lac": 2004, "cell_id_start": 40001},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "lac": 2005, "cell_id_start": 50001},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "lac": 2006, "cell_id_start": 60001},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "lac": 2007, "cell_id_start": 70001},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "lac": 2008, "cell_id_start": 80001},
]

# ── Suspects (Gang Members) ──────────────────────────────
SUSPECTS = [
    {"phone": "9876543210", "name": "Rahul Sharma", "city": "Delhi", "imei": "356789012345670", "imsi": "404110123456789"},
    {"phone": "9812345670", "name": "Raj Kumar", "city": "Mumbai", "imei": "356789012345671", "imsi": "404050123456780"},
    {"phone": "9834567890", "name": "Amit Verma", "city": "Kolkata", "imei": "356789012345672", "imsi": "404110123456791"},
    {"phone": "9856789010", "name": "Vikash Singh", "city": "Patna", "imei": "356789012345673", "imsi": "404010123456792"},
    {"phone": "9845678901", "name": "Sumit Nair", "city": "Chennai", "imei": "356789012345674", "imsi": "404050123456793"},
]

BASE_DATE = datetime(2024, 3, 1)


def generate_imei():
    """Generate valid IMEI (15 digits)"""
    return f"35{random.randint(100000000000, 999999999999)}"


def generate_imsi(operator_id):
    """Generate IMSI: MCC(404) + MNC + MSIN"""
    msin = random.randint(1000000000, 9999999999)
    return f"404{operator_id}{msin}"


def random_timestamp(base_date, is_suspicious=False):
    """Generate timestamp"""
    days_offset = random.randint(0, 29)
    if is_suspicious and random.random() < 0.6:  # Night activity
        hour = random.randint(0, 4)
    else:
        hour = random.randint(6, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)


def generate_ipdr_record(suspect, record_num):
    """Generate one complete IPDR record"""
    
    # Basic subscriber info
    msisdn = suspect["phone"]
    imei = suspect["imei"]
    imsi = suspect["imsi"]
    subscriber_name = suspect["name"]
    
    # Timestamps
    session_start = random_timestamp(BASE_DATE, is_suspicious=(record_num % 3 == 0))
    duration_sec = random.randint(10, 3600)
    session_end = session_start + timedelta(seconds=duration_sec)
    
    # Location & Network
    city_data = next((c for c in CITIES if c["city"] == suspect["city"]), CITIES[0])
    isp_data = random.choice(ISP_DATA)
    cell_id = city_data["cell_id_start"] + random.randint(1, 100)
    lac = city_data["lac"]
    
    # IP Addresses
    source_ip = f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    # App/Website selection
    use_tor = random.random() < 0.15
    use_vpn = random.random() < 0.10
    
    if use_tor:
        dest_ip = random.choice(TOR_EXITS)
        app_name = "Tor Browser"
        domain = "tor.project.org"
        service_type = "Proxy/Anonymizer"
        dest_port = 9050
        is_tor = True
        is_encrypted = True
    else:
        app_name, domain, service_type, dest_port = random.choice(APPS)
        dest_ip = f"{random.randint(1, 223)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        is_tor = False
        is_encrypted = (dest_port == 443)
    
    # Ports
    source_port = random.randint(10000, 65535)
    
    # Protocol
    if dest_port == 443:
        protocol = "HTTPS"
        l4_protocol = "TCP"
    elif dest_port == 80:
        protocol = "HTTP"
        l4_protocol = "TCP"
    elif dest_port == 53:
        protocol = "DNS"
        l4_protocol = "UDP"
    else:
        protocol = app_name
        l4_protocol = "TCP"
    
    # Data volumes
    upload_bytes = int(np.random.lognormal(mean=10, sigma=2))
    download_bytes = int(np.random.lognormal(mean=12, sigma=2))
    total_bytes = upload_bytes + download_bytes
    
    # Device info
    device_model, os_version, browser = random.choice(DEVICES)
    
    # Behavioral flags
    is_vpn = use_vpn
    is_foreign = random.random() < 0.2
    is_off_hours = (session_start.hour >= 0 and session_start.hour < 5)
    is_proxy = use_tor or use_vpn
    
    # NAT IP (for CGNAT)
    nat_ip = f"100.{random.randint(64, 127)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    # DNS queries
    dns_query = domain if protocol != "DNS" else f"query{random.randint(1000, 9999)}.example.com"
    
    # Session ID
    session_id = f"SES{fake.uuid4()[:8].upper()}"
    
    # Connection type
    conn_type = random.choice(["4G", "4G", "4G", "5G", "3G", "WiFi"])
    
    # Return complete record
    return {
        # === SUBSCRIBER INFO ===
        "MSISDN": msisdn,
        "Subscriber_Name": subscriber_name,
        "IMEI": imei,
        "IMSI": imsi,
        "Subscriber_ID": f"SUB-{msisdn}",
        
        # === TIMESTAMP INFO ===
        "Session_Start_Time": session_start.strftime("%Y-%m-%d %H:%M:%S"),
        "Session_End_Time": session_end.strftime("%Y-%m-%d %H:%M:%S"),
        "Session_Duration_Sec": duration_sec,
        "Session_ID": session_id,
        
        # === NETWORK INFO ===
        "Source_IP": source_ip,
        "Source_Port": source_port,
        "NAT_IP": nat_ip,
        "Destination_IP": dest_ip,
        "Destination_Port": dest_port,
        "Protocol": protocol,
        "L4_Protocol": l4_protocol,
        
        # === DATA VOLUME ===
        "Upload_Bytes": upload_bytes,
        "Download_Bytes": download_bytes,
        "Total_Bytes": total_bytes,
        "Upload_MB": round(upload_bytes / 1_048_576, 2),
        "Download_MB": round(download_bytes / 1_048_576, 2),
        "Total_MB": round(total_bytes / 1_048_576, 2),
        
        # === LOCATION INFO ===
        "City": city_data["city"],
        "State": city_data["state"],
        "Latitude": city_data["lat"],
        "Longitude": city_data["lon"],
        "Cell_ID": cell_id,
        "LAC": lac,
        "Cell_Tower_ID": f"TW{lac}{cell_id}",
        
        # === ISP/OPERATOR INFO ===
        "ISP": isp_data["isp"],
        "Operator_ID": isp_data["operator_id"],
        "Circle": isp_data["circle"],
        "Connection_Type": conn_type,
        
        # === APP/WEBSITE INFO ===
        "App_Name": app_name,
        "Domain": domain,
        "Service_Type": service_type,
        "DNS_Query": dns_query,
        "SNI": domain if is_encrypted else "",
        
        # === DEVICE INFO ===
        "Device_Model": device_model,
        "OS_Version": os_version,
        "Browser_UserAgent": browser,
        
        # === BEHAVIORAL FLAGS ===
        "Is_TOR": is_tor,
        "Is_VPN": is_vpn,
        "Is_Proxy": is_proxy,
        "Is_Foreign_IP": is_foreign,
        "Is_Encrypted": is_encrypted,
        "Is_Off_Hours": is_off_hours,
        "Is_Suspicious": (is_tor or is_vpn or is_off_hours),
        
        # === ADDITIONAL FORENSIC DATA ===
        "Packet_Count": random.randint(10, 1000),
        "RTT_ms": random.randint(5, 200),
        "Packet_Loss_Percent": round(random.uniform(0, 5), 2),
        "HTTP_Method": random.choice(["GET", "POST", "PUT", "DELETE"]) if protocol in ["HTTP", "HTTPS"] else "",
        "HTTP_Status_Code": random.choice([200, 201, 301, 302, 404, 500]) if protocol in ["HTTP", "HTTPS"] else "",
    }


def main():
    """Generate 500 professional IPDR records"""
    print("🔍 Generating Professional IPDR Data (500 records)...")
    print("=" * 60)
    
    records = []
    records_per_suspect = 100
    
    for suspect in SUSPECTS:
        print(f"📱 Generating {records_per_suspect} records for {suspect['name']} ({suspect['phone']})")
        for i in range(records_per_suspect):
            record = generate_ipdr_record(suspect, i)
            records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Sort by timestamp
    df = df.sort_values("Session_Start_Time").reset_index(drop=True)
    
    # Save to CSV
    output_path = os.path.join("data", "professional_ipdr.csv")
    df.to_csv(output_path, index=False)
    
    print("=" * 60)
    print(f"✅ Generated {len(df)} IPDR records")
    print(f"📁 Saved to: {output_path}")
    print(f"📊 Total columns: {len(df.columns)}")
    print("\n📋 Columns included:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print("\n📈 Statistics:")
    print(f"   - Total suspects: {len(SUSPECTS)}")
    print(f"   - Tor usage: {df['Is_TOR'].sum()} sessions ({df['Is_TOR'].sum()/len(df)*100:.1f}%)")
    print(f"   - VPN usage: {df['Is_VPN'].sum()} sessions ({df['Is_VPN'].sum()/len(df)*100:.1f}%)")
    print(f"   - Off-hours: {df['Is_Off_Hours'].sum()} sessions ({df['Is_Off_Hours'].sum()/len(df)*100:.1f}%)")
    print(f"   - Suspicious: {df['Is_Suspicious'].sum()} sessions ({df['Is_Suspicious'].sum()/len(df)*100:.1f}%)")
    
    print("\n✅ Done! Use this file for cyber crime investigation analysis.")


if __name__ == "__main__":
    main()
