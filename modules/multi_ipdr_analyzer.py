"""
Multi-IPDR Connection Analyzer
Complete module for analyzing connections between multiple IPDR files
Designed for cyber investigation - gang detection, shared infrastructure, coordinated activity
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import streamlit as st


def analyze_multi_ipdr_connections(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> Dict[str, Any]:
    """
    Main function to analyze connections between multiple IPDR files.
    
    Args:
        suspect_files: List of DataFrames, one per suspect
        suspect_labels: List of suspect identifiers (e.g., "Suspect_A", "Suspect_B")
    
    Returns:
        Dictionary containing all analysis results
    """
    
    results = {
        "summary": {},
        "shared_ips": pd.DataFrame(),
        "shared_infrastructure": pd.DataFrame(),
        "temporal_correlations": [],
        "coordinated_activity": [],
        "gang_score": 0,
        "verdict": "",
        "key_findings": [],
        "ai_insights": "",
        "connection_matrix": pd.DataFrame(),
        "suspect_profiles": []
    }
    
    # 1. Basic Summary
    results["summary"] = {
        "total_suspects": len(suspect_files),
        "total_records": sum(len(df) for df in suspect_files),
        "suspect_labels": suspect_labels,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # 2. Shared IP Analysis
    results["shared_ips"] = detect_shared_ips(suspect_files, suspect_labels)
    
    # 3. Shared Infrastructure (ISP, Cell Towers, Regions)
    results["shared_infrastructure"] = detect_shared_infrastructure(suspect_files, suspect_labels)
    
    # 4. Temporal Correlation (same IPs contacted within time windows)
    results["temporal_correlations"] = detect_temporal_correlations(suspect_files, suspect_labels)
    
    # 5. Coordinated Activity Detection
    results["coordinated_activity"] = detect_coordinated_activity(suspect_files, suspect_labels)
    
    # 6. Gang Score Calculation
    results["gang_score"], results["verdict"] = calculate_gang_score(results)
    
    # 7. Key Findings Summary
    results["key_findings"] = generate_key_findings(results)
    
    # 8. Connection Matrix (who shares what with whom)
    results["connection_matrix"] = build_connection_matrix(suspect_files, suspect_labels)
    
    # 9. Per-Suspect Profiles
    results["suspect_profiles"] = build_suspect_profiles(suspect_files, suspect_labels)
    
    return results


def detect_shared_ips(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> pd.DataFrame:
    """
    Detect destination IPs contacted by multiple suspects.
    This is PRIMARY evidence of gang connection.
    """
    
    # Collect all destination IPs per suspect
    suspect_ip_map = {}
    for idx, df in enumerate(suspect_files):
        label = suspect_labels[idx]
        if 'Destination_IP' in df.columns:
            suspect_ip_map[label] = set(df['Destination_IP'].dropna().unique())
    
    # Find shared IPs
    shared_data = []
    all_ips = set()
    for ips in suspect_ip_map.values():
        all_ips.update(ips)
    
    for ip in all_ips:
        suspects_with_ip = [label for label, ips in suspect_ip_map.items() if ip in ips]
        if len(suspects_with_ip) >= 2:
            # Get additional details
            total_sessions = 0
            is_tor = False
            is_foreign = False
            
            for idx, df in enumerate(suspect_files):
                if suspect_labels[idx] in suspects_with_ip:
                    ip_sessions = df[df['Destination_IP'] == ip]
                    total_sessions += len(ip_sessions)
                    if 'Is_TOR' in df.columns:
                        is_tor = is_tor or ip_sessions['Is_TOR'].any()
                    if 'Is_Foreign_IP' in df.columns:
                        is_foreign = is_foreign or ip_sessions['Is_Foreign_IP'].any()
            
            shared_data.append({
                'Destination_IP': ip,
                'Shared_By': ', '.join(suspects_with_ip),
                'Suspect_Count': len(suspects_with_ip),
                'Total_Sessions': total_sessions,
                'Is_TOR': is_tor,
                'Is_Foreign': is_foreign,
                'Risk_Level': 'CRITICAL' if is_tor else ('HIGH' if is_foreign else 'MEDIUM')
            })
    
    shared_df = pd.DataFrame(shared_data)
    if not shared_df.empty:
        shared_df = shared_df.sort_values('Suspect_Count', ascending=False)
    
    return shared_df


def detect_shared_infrastructure(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> pd.DataFrame:
    """
    Detect shared infrastructure: ISPs, Cell Towers, Cities, Ports
    """
    
    infra_data = []
    
    # Check for shared ISPs
    isps_by_suspect = {}
    for idx, df in enumerate(suspect_files):
        if 'ISP' in df.columns:
            isps_by_suspect[suspect_labels[idx]] = set(df['ISP'].dropna().unique())
    
    # Find shared ISPs
    all_isps = set()
    for isps in isps_by_suspect.values():
        all_isps.update(isps)
    
    for isp in all_isps:
        suspects = [label for label, isps in isps_by_suspect.items() if isp in isps]
        if len(suspects) >= 2:
            infra_data.append({
                'Type': 'ISP',
                'Value': isp,
                'Shared_By': ', '.join(suspects),
                'Suspect_Count': len(suspects),
                'Risk': 'MEDIUM'
            })
    
    # Check for shared Cell Towers
    towers_by_suspect = {}
    for idx, df in enumerate(suspect_files):
        if 'Cell_Tower_ID' in df.columns:
            towers_by_suspect[suspect_labels[idx]] = set(df['Cell_Tower_ID'].dropna().unique())
    
    all_towers = set()
    for towers in towers_by_suspect.values():
        all_towers.update(towers)
    
    for tower in all_towers:
        suspects = [label for label, towers in towers_by_suspect.items() if tower in towers]
        if len(suspects) >= 2:
            infra_data.append({
                'Type': 'Cell Tower',
                'Value': str(tower),
                'Shared_By': ', '.join(suspects),
                'Suspect_Count': len(suspects),
                'Risk': 'HIGH'
            })
    
    # Check for shared Cities (possible same location)
    cities_by_suspect = {}
    for idx, df in enumerate(suspect_files):
        if 'City' in df.columns:
            cities_by_suspect[suspect_labels[idx]] = set(df['City'].dropna().unique())
    
    all_cities = set()
    for cities in cities_by_suspect.values():
        all_cities.update(cities)
    
    for city in all_cities:
        suspects = [label for label, cities in cities_by_suspect.items() if city in cities]
        if len(suspects) >= 2:
            infra_data.append({
                'Type': 'City/Location',
                'Value': city,
                'Shared_By': ', '.join(suspects),
                'Suspect_Count': len(suspects),
                'Risk': 'MEDIUM'
            })
    
    infra_df = pd.DataFrame(infra_data)
    if not infra_df.empty:
        infra_df = infra_df.sort_values('Suspect_Count', ascending=False)
    
    return infra_df


def detect_temporal_correlations(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str],
    time_window_minutes: int = 30
) -> List[Dict[str, Any]]:
    """
    Detect when multiple suspects contacted the same IP within a short time window.
    This indicates coordinated activity.
    """
    
    correlations = []
    
    # Get shared IPs first
    shared_ips = detect_shared_ips(suspect_files, suspect_labels)
    if shared_ips.empty:
        return correlations
    
    # For each shared IP, check temporal proximity
    for _, row in shared_ips.iterrows():
        ip = row['Destination_IP']
        suspects_list = row['Shared_By'].split(', ')
        
        # Collect all timestamps for this IP across suspects
        timestamps_by_suspect = {}
        for idx, df in enumerate(suspect_files):
            label = suspect_labels[idx]
            if label in suspects_list and 'Timestamp' in df.columns:
                ip_sessions = df[df['Destination_IP'] == ip]
                if not ip_sessions.empty:
                    timestamps_by_suspect[label] = pd.to_datetime(ip_sessions['Timestamp']).tolist()
        
        # Check for temporal overlaps
        if len(timestamps_by_suspect) >= 2:
            suspect_pairs = []
            for i, (label1, times1) in enumerate(timestamps_by_suspect.items()):
                for label2, times2 in list(timestamps_by_suspect.items())[i+1:]:
                    # Check if any timestamps are within time window
                    for t1 in times1:
                        for t2 in times2:
                            time_diff = abs((t1 - t2).total_seconds() / 60)
                            if time_diff <= time_window_minutes:
                                correlations.append({
                                    'IP': ip,
                                    'Suspect_1': label1,
                                    'Suspect_2': label2,
                                    'Time_1': t1.strftime('%Y-%m-%d %H:%M:%S'),
                                    'Time_2': t2.strftime('%Y-%m-%d %H:%M:%S'),
                                    'Time_Diff_Minutes': round(time_diff, 2),
                                    'Risk': 'CRITICAL' if time_diff < 5 else 'HIGH'
                                })
                                break
                        if correlations and correlations[-1]['IP'] == ip:
                            break
    
    return correlations


def detect_coordinated_activity(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> List[Dict[str, Any]]:
    """
    Detect patterns suggesting coordinated criminal activity:
    - Same ports used by multiple suspects
    - Similar app usage patterns
    - Same suspicious behaviors (Tor, VPN, etc.)
    """
    
    coordinated = []
    
    # 1. Tor/VPN usage correlation
    tor_users = []
    for idx, df in enumerate(suspect_files):
        if 'Is_TOR' in df.columns and df['Is_TOR'].sum() > 0:
            tor_users.append(suspect_labels[idx])
    
    if len(tor_users) >= 2:
        coordinated.append({
            'Pattern': 'Tor Browser Usage',
            'Suspects': ', '.join(tor_users),
            'Suspect_Count': len(tor_users),
            'Description': f'{len(tor_users)} suspects used Tor for anonymization',
            'Risk': 'CRITICAL'
        })
    
    # 2. Off-hours activity correlation
    offhours_users = []
    for idx, df in enumerate(suspect_files):
        if 'Is_Off_Hours' in df.columns and df['Is_Off_Hours'].sum() > 10:
            offhours_users.append(suspect_labels[idx])
    
    if len(offhours_users) >= 2:
        coordinated.append({
            'Pattern': 'Late Night Activity',
            'Suspects': ', '.join(offhours_users),
            'Suspect_Count': len(offhours_users),
            'Description': f'{len(offhours_users)} suspects active during suspicious hours (11 PM - 6 AM)',
            'Risk': 'HIGH'
        })
    
    # 3. Port 9050 (Tor SOCKS) usage
    tor_port_users = []
    for idx, df in enumerate(suspect_files):
        if 'Destination_Port' in df.columns:
            if (df['Destination_Port'] == 9050).sum() > 0:
                tor_port_users.append(suspect_labels[idx])
    
    if len(tor_port_users) >= 2:
        coordinated.append({
            'Pattern': 'Tor SOCKS Port (9050)',
            'Suspects': ', '.join(tor_port_users),
            'Suspect_Count': len(tor_port_users),
            'Description': f'{len(tor_port_users)} suspects used Tor SOCKS proxy (port 9050)',
            'Risk': 'CRITICAL'
        })
    
    return coordinated


def calculate_gang_score(results: Dict[str, Any]) -> Tuple[int, str]:
    """
    Calculate gang connection score (0-100) based on evidence.
    """
    
    score = 0
    
    # Shared IPs (most important)
    if not results["shared_ips"].empty:
        num_shared = len(results["shared_ips"])
        score += min(num_shared * 5, 40)  # Max 40 points
        
        # Bonus for critical IPs (Tor, Foreign)
        critical_ips = results["shared_ips"][results["shared_ips"]['Risk_Level'] == 'CRITICAL']
        score += len(critical_ips) * 5
    
    # Shared Infrastructure
    if not results["shared_infrastructure"].empty:
        num_infra = len(results["shared_infrastructure"])
        score += min(num_infra * 3, 20)  # Max 20 points
    
    # Temporal Correlations
    if results["temporal_correlations"]:
        num_temporal = len(results["temporal_correlations"])
        score += min(num_temporal * 5, 20)  # Max 20 points
    
    # Coordinated Activity
    if results["coordinated_activity"]:
        num_coord = len(results["coordinated_activity"])
        score += min(num_coord * 5, 20)  # Max 20 points
    
    # Cap at 100
    score = min(score, 100)
    
    # Verdict
    if score >= 80:
        verdict = "STRONG GANG CONNECTION - High confidence of organized criminal activity"
    elif score >= 60:
        verdict = "PROBABLE GANG CONNECTION - Significant evidence of coordination"
    elif score >= 40:
        verdict = "POSSIBLE CONNECTION - Some suspicious overlaps detected"
    elif score >= 20:
        verdict = "WEAK CONNECTION - Minor overlaps, may be coincidental"
    else:
        verdict = "NO SIGNIFICANT CONNECTION - Suspects appear independent"
    
    return score, verdict


def generate_key_findings(results: Dict[str, Any]) -> List[str]:
    """
    Generate plain English summary of key findings.
    """
    
    findings = []
    
    # Shared IPs
    if not results["shared_ips"].empty:
        num_shared = len(results["shared_ips"])
        critical_shared = len(results["shared_ips"][results["shared_ips"]['Risk_Level'] == 'CRITICAL'])
        findings.append(
            f"🔴 {num_shared} destination IPs contacted by multiple suspects"
            + (f" ({critical_shared} CRITICAL - Tor/Proxy)" if critical_shared > 0 else "")
        )
    
    # Temporal correlations
    if results["temporal_correlations"]:
        num_temporal = len(results["temporal_correlations"])
        findings.append(
            f"⏰ {num_temporal} instances of suspects contacting same IP within 30 minutes (coordinated activity)"
        )
    
    # Coordinated patterns
    if results["coordinated_activity"]:
        for pattern in results["coordinated_activity"]:
            findings.append(f"🚨 {pattern['Description']} ({pattern['Risk']} risk)")
    
    # Shared infrastructure
    if not results["shared_infrastructure"].empty:
        cell_towers = results["shared_infrastructure"][results["shared_infrastructure"]['Type'] == 'Cell Tower']
        if not cell_towers.empty:
            findings.append(f"📡 {len(cell_towers)} shared cell towers (suspects in same physical area)")
    
    return findings


def build_connection_matrix(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> pd.DataFrame:
    """
    Build a matrix showing connection strength between each pair of suspects.
    """
    
    n = len(suspect_labels)
    matrix = pd.DataFrame(0, index=suspect_labels, columns=suspect_labels)
    
    # Count shared IPs between each pair
    for i in range(n):
        ips_i = set(suspect_files[i]['Destination_IP'].dropna().unique())
        for j in range(i+1, n):
            ips_j = set(suspect_files[j]['Destination_IP'].dropna().unique())
            shared_count = len(ips_i & ips_j)
            matrix.loc[suspect_labels[i], suspect_labels[j]] = shared_count
            matrix.loc[suspect_labels[j], suspect_labels[i]] = shared_count
    
    return matrix


def build_suspect_profiles(
    suspect_files: List[pd.DataFrame],
    suspect_labels: List[str]
) -> List[Dict[str, Any]]:
    """
    Build individual profile for each suspect.
    """
    
    profiles = []
    
    for idx, df in enumerate(suspect_files):
        label = suspect_labels[idx]
        
        profile = {
            'label': label,
            'file_name': df['_file_name'].iloc[0] if '_file_name' in df.columns else label,
            'total_sessions': len(df),
            'unique_ips': df['Destination_IP'].nunique() if 'Destination_IP' in df.columns else 0,
            'total_data_mb': (df['Data_Volume_Bytes'].sum() / 1_048_576) if 'Data_Volume_Bytes' in df.columns else 0,
            'tor_sessions': int(df['Is_TOR'].sum()) if 'Is_TOR' in df.columns else 0,
            'foreign_sessions': int(df['Is_Foreign_IP'].sum()) if 'Is_Foreign_IP' in df.columns else 0,
            'off_hours': int(df['Is_Off_Hours'].sum()) if 'Is_Off_Hours' in df.columns else 0,
            'date_range': f"{df['Timestamp'].min()} to {df['Timestamp'].max()}" if 'Timestamp' in df.columns else "Unknown"
        }
        
        profiles.append(profile)
    
    return profiles
