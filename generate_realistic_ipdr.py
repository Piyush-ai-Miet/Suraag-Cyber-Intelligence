#!/usr/bin/env python3
"""
Generate realistic IPDR data based on the sample format shown in image
Format: Record,Version,Record_Type,Timestamp,Source_IP_Address,Destination_IP_Address,Protocol,Source_Port,Destination_Port,Service_Type,Session_Duration,Bytes_Transferred
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Realistic configurations
PROTOCOLS = ['TCP', 'UDP', 'ICMP']
SERVICE_TYPES = [
    'Web Browsing', 'VoIP', 'Network Monitoring', 'Web Browsing (HTTPS)',
    'File Transfer', 'Email', 'Video Streaming', 'Social Media', 
    'Gaming', 'P2P', 'Cloud Storage', 'VPN', 'Tor'
]

# Common ports mapping
PORT_SERVICE_MAP = {
    80: 'Web Browsing',
    443: 'Web Browsing (HTTPS)',
    5000: 'VoIP',
    8080: 'Web Browsing',
    21: 'File Transfer',
    25: 'Email',
    443: 'Video Streaming',
    9050: 'Tor',
    1194: 'VPN',
}

# Suspicious indicators
TOR_IPS = ['10.1.1.1', '8.8.4.4']
FOREIGN_COUNTRIES = ['US', 'CN', 'RU', 'PK']

def generate_source_ip():
    """Generate realistic source IP (ISP assigned)"""
    return f"192.168.{random.randint(1,10)}.{random.randint(10,100)}"

def generate_destination_ip():
    """Generate realistic destination IP"""
    # Mix of common services and random IPs
    common_ips = [
        '8.8.8.8',  # Google DNS
        '1.1.1.1',  # Cloudflare
        '10.0.0.2', # Local
        '172.16.1.1', # Private
        '10.1.1.1', # TOR
    ]
    
    if random.random() < 0.3:  # 30% common IPs
        return random.choice(common_ips)
    else:  # 70% random IPs
        return fake.ipv4()

def generate_session_duration():
    """Generate realistic session duration in HH:MM:SS format"""
    hours = random.choices([0, 1, 2], weights=[70, 20, 10])[0]
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_bytes_transferred(service_type):
    """Generate realistic bytes based on service type"""
    if 'Browsing' in service_type:
        return random.randint(50000, 5000000)  # 50KB to 5MB
    elif 'Video' in service_type or 'Streaming' in service_type:
        return random.randint(5000000, 500000000)  # 5MB to 500MB
    elif 'VoIP' in service_type:
        return random.randint(100000, 2000000)  # 100KB to 2MB
    elif 'File Transfer' in service_type or 'P2P' in service_type:
        return random.randint(10000000, 1000000000)  # 10MB to 1GB
    elif 'Tor' in service_type or 'VPN' in service_type:
        return random.randint(1000000, 50000000)  # 1MB to 50MB
    else:
        return random.randint(10000, 1000000)  # 10KB to 1MB

def generate_timestamp(base_date, hour_range=None):
    """Generate realistic timestamp"""
    if hour_range:
        hour = random.randint(hour_range[0], hour_range[1])
    else:
        hour = random.randint(0, 23)
    
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    timestamp = base_date.replace(hour=hour, minute=minute, second=second)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def generate_ipdr_records(num_records=500, suspicious_percentage=20):
    """Generate IPDR records with realistic data"""
    
    records = []
    base_date = datetime(2024, 6, 1)
    
    # Generate records
    for i in range(1, num_records + 1):
        # Determine if this is a suspicious record
        is_suspicious = random.random() < (suspicious_percentage / 100)
        
        # Base record
        record = {
            'Record': i,
            'Version': 10,
            'Record_Type': 'N/A' if random.random() < 0.7 else 'Start of Session',
        }
        
        # Timestamp (more suspicious activity at night)
        if is_suspicious and random.random() < 0.6:
            timestamp = generate_timestamp(base_date, hour_range=(0, 5))  # Night time
        else:
            timestamp = generate_timestamp(base_date)
        
        record['Timestamp'] = timestamp
        
        # IPs
        record['Source_IP_Address'] = generate_source_ip()
        
        if is_suspicious and random.random() < 0.4:
            # Suspicious: Tor or foreign IP
            record['Destination_IP_Address'] = random.choice(TOR_IPS) if random.random() < 0.5 else fake.ipv4()
        else:
            record['Destination_IP_Address'] = generate_destination_ip()
        
        # Protocol
        record['Protocol'] = random.choices(PROTOCOLS, weights=[70, 25, 5])[0]
        
        # Ports and Service
        if is_suspicious and random.random() < 0.3:
            # Suspicious ports
            record['Source_Port'] = random.randint(40000, 65000)
            record['Destination_Port'] = random.choice([9050, 1194, 8080, 4444, 6667])
            record['Service_Type'] = random.choice(['Tor', 'VPN', 'P2P', 'Unknown'])
        else:
            # Normal ports
            dest_port = random.choice(list(PORT_SERVICE_MAP.keys()))
            record['Source_Port'] = random.randint(49152, 65535)
            record['Destination_Port'] = dest_port
            record['Service_Type'] = PORT_SERVICE_MAP[dest_port]
        
        # Session details
        record['Session_Duration'] = generate_session_duration()
        record['Bytes_Transferred'] = generate_bytes_transferred(record['Service_Type'])
        
        records.append(record)
    
    return records

# Generate data
print("🔧 Generating realistic IPDR data...")
ipdr_data = generate_ipdr_records(num_records=1000, suspicious_percentage=25)

# Save to CSV
output_file = 'data/realistic_ipdr_sample.csv'
fieldnames = [
    'Record', 'Version', 'Record_Type', 'Timestamp', 
    'Source_IP_Address', 'Destination_IP_Address', 'Protocol',
    'Source_Port', 'Destination_Port', 'Service_Type',
    'Session_Duration', 'Bytes_Transferred'
]

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ipdr_data)

print(f"✅ Generated {len(ipdr_data)} IPDR records")
print(f"📁 Saved to: {output_file}")
print(f"\n📊 Sample records:")
print(f"   - Total Records: {len(ipdr_data)}")
print(f"   - Suspicious Activities: ~{int(len(ipdr_data) * 0.25)}")
print(f"   - Time Range: 2024-06-01 (24 hours)")
print(f"   - Services: Web, VoIP, Tor, VPN, Streaming, etc.")
print(f"\n🚀 Ready to upload to your Suराग tool!")