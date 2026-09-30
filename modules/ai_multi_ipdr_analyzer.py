"""
modules/ai_multi_ipdr_analyzer.py — AI-Powered Multiple IPDR Connection Analysis
Expert Cyber Crime IPDR Analyst - Identifies investigation mode and correlates patterns.
Uses Gemini AI to detect suspicious patterns, connections, and provide intelligent insights.
"""

import pandas as pd
import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


def identify_unique_subscribers(df: pd.DataFrame) -> dict:
    """
    Step 1: Identify unique subscribers/entities across all uploaded files.
    Returns investigation mode and subscriber info.
    """
    # Possible subscriber identifier columns
    identifier_cols = [
        'Subscriber_ID', 'subscriber_id', 
        'MSISDN', 'msisdn',
        'IMSI', 'imsi',
        'Customer_ID', 'customer_id',
        'User_ID', 'user_id',
        'Account_ID', 'account_id',
        'Subscriber_Name', 'subscriber_name'
    ]
    
    # Find which identifier column exists
    found_col = None
    for col in identifier_cols:
        if col in df.columns:
            found_col = col
            break
    
    if not found_col:
        # Fallback: use Source_IP as identifier
        unique_subscribers = df['Source_IP'].nunique()
        subscriber_list = df['Source_IP'].unique().tolist()
        identifier_type = 'Source_IP'
    else:
        unique_subscribers = df[found_col].nunique()
        subscriber_list = df[found_col].unique().tolist()
        identifier_type = found_col
    
    # Determine investigation mode
    if unique_subscribers == 1:
        mode = "SINGLE_SUBJECT"
        description = "Single Subject Investigation"
    else:
        mode = "MULTI_SUBJECT"
        description = "Multi Subject Correlation"
    
    return {
        "mode": mode,
        "description": description,
        "unique_count": unique_subscribers,
        "identifier_type": identifier_type,
        "subscriber_list": subscriber_list[:10],  # Max 10 for display
        "focus_areas": get_focus_areas(mode)
    }


def get_focus_areas(mode: str) -> list:
    """Return analysis focus areas based on investigation mode."""
    if mode == "SINGLE_SUBJECT":
        return [
            "Timeline Analysis",
            "Destination Patterns",
            "VPN/TOR Usage",
            "Repeated Contacts",
            "Suspicious Infrastructure",
            "Behavioral Anomalies",
            "High-Risk Connections"
        ]
    else:  # MULTI_SUBJECT
        return [
            "Common Destinations",
            "Shared Infrastructure",
            "Coordinated Activity",
            "Network Clusters",
            "Temporal Correlation",
            "Central Nodes",
            "Hidden Relationships"
        ]


def generate_ipdr_summary(df: pd.DataFrame, suspect_count: int) -> str:
    """Generate concise summary of IPDR data for AI analysis."""
    
    summary = {
        "total_records": len(df),
        "suspects": suspect_count,
        "unique_destination_ips": df['Destination_IP'].nunique(),
        "date_range": f"{df['Timestamp'].min()} to {df['Timestamp'].max()}",
        "tor_sessions": int(df['Is_TOR'].sum()),
        "foreign_connections": int(df['Is_Foreign_IP'].sum()),
        "off_hours_activity": int(df['Is_Off_Hours'].sum()),
        "total_data_gb": round(df['Data_Volume_Bytes'].sum() / (1024**3), 2),
    }
    
    # Top destination IPs
    top_dest_ips = df['Destination_IP'].value_counts().head(10).to_dict()
    
    # Suspicious ports
    suspicious_ports = [9050, 22, 23, 3389, 445, 1080, 8080, 4444, 5900, 3128]
    sus_port_activity = df[df['Destination_Port'].isin(suspicious_ports)]['Destination_Port'].value_counts().to_dict()
    
    # Protocol distribution
    protocols = df['App_Protocol'].value_counts().head(5).to_dict()
    
    # Per-suspect activity
    suspect_stats = []
    for suspect in df['Subscriber_Name'].unique():
        s_df = df[df['Subscriber_Name'] == suspect]
        suspect_stats.append({
            "name": suspect,
            "source_ip": s_df['Source_IP'].iloc[0],
            "sessions": len(s_df),
            "unique_destinations": s_df['Destination_IP'].nunique(),
            "tor_usage": int(s_df['Is_TOR'].sum()),
            "foreign_ips": int(s_df['Is_Foreign_IP'].sum()),
        })
    
    return {
        "summary": summary,
        "top_destinations": top_dest_ips,
        "suspicious_ports": sus_port_activity,
        "protocols": protocols,
        "suspects": suspect_stats,
    }


def analyze_connections_with_ai(df: pd.DataFrame, correlation_data: dict = None) -> dict:
    """
    Expert Cyber Crime IPDR Analyst AI.
    Analyzes IPDR records and detects patterns based on investigation mode.
    Returns professional investigator-grade analysis.
    """
    
    try:
        # Step 1: Identify unique subscribers and investigation mode
        investigation_info = identify_unique_subscribers(df)
        mode = investigation_info['mode']
        unique_count = investigation_info['unique_count']
        
        # Generate data summary
        data_summary = generate_ipdr_summary(df, unique_count)
        
        # Build AI prompt based on investigation mode
        if mode == "SINGLE_SUBJECT":
            prompt = build_single_subject_prompt(investigation_info, data_summary)
        else:
            prompt = build_multi_subject_prompt(investigation_info, data_summary, correlation_data)
        
        # Call Gemini AI
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse AI response
        ai_text = response.text
        
        # Extract structured findings
        findings = parse_findings(ai_text)
        
        return {
            "success": True,
            "investigation_mode": investigation_info,
            "findings": findings,
            "raw_response": ai_text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "investigation_mode": {"mode": "UNKNOWN", "description": "Analysis failed"},
            "findings": generate_fallback_findings(df)
        }


def build_single_subject_prompt(investigation_info: dict, data_summary: dict) -> str:
    """Build AI prompt for single subject investigation."""
    
    return f"""You are an expert Cyber Crime IPDR Analyst conducting a SINGLE SUBJECT INVESTIGATION.

**INVESTIGATION DETAILS:**
- Mode: {investigation_info['description']}
- Unique Subscribers Found: {investigation_info['unique_count']}
- Identifier Type: {investigation_info['identifier_type']}
- Total Records: {data_summary['summary']['total_records']:,}
- Date Range: {data_summary['summary']['date_range']}

**IPDR DATA SUMMARY:**
- Unique Destination IPs: {data_summary['summary']['unique_destination_ips']}
- Tor Sessions: {data_summary['summary']['tor_sessions']}
- Foreign Connections: {data_summary['summary']['foreign_connections']}
- Off-Hours Activity: {data_summary['summary']['off_hours_activity']}
- Total Data Transferred: {data_summary['summary']['total_data_gb']} GB

**Top Destination IPs (Most Contacted):**
{chr(10).join([f"- {ip}: {count} connections" for ip, count in list(data_summary['top_destinations'].items())[:10]])}

**Suspicious Port Activity:**
{chr(10).join([f"- Port {port}: {count} times" for port, count in data_summary['suspicious_ports'].items()]) if data_summary['suspicious_ports'] else "None detected"}

**Protocol Distribution:**
{chr(10).join([f"- {proto}: {count} sessions" for proto, count in list(data_summary['protocols'].items())[:5]])}

**ANALYSIS FOCUS AREAS:**
{chr(10).join([f"- {area}" for area in investigation_info['focus_areas']])}

**YOUR TASK:**
As a Cyber Crime IPDR Analyst, analyze this single subject's internet activity and identify:

**FINDINGS (Use this exact format for each finding):**

FINDING #1
Type: [Connection Pattern / Suspicious Infrastructure / VPN-TOR Usage / Repeated Contact / Behavioral Anomaly]
Severity: [LOW / MEDIUM / HIGH / CRITICAL]
Confidence: [LOW / MEDIUM / HIGH]

Evidence:
- IPs involved: [list specific IPs]
- Time range: [specific dates/times]
- Frequency: [number of connections]

Assessment:
[Explain why this pattern is relevant from investigator perspective]

Risk Score: [0-100]

---

**ALSO PROVIDE:**

**EXECUTIVE SUMMARY:**
[2-3 sentences overview of subject's internet behavior]

**KEY FINDINGS:**
[List top 5 most important discoveries]

**TIMELINE ANALYSIS:**
[Notable temporal patterns or activity clusters]

**INVESTIGATION LEADS:**
[Specific actionable items for investigator]

**RECOMMENDED NEXT STEPS:**
[Concrete actions investigator should take]

**OVERALL RISK ASSESSMENT:**
Subject Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]
Overall Risk Score: [0-100]

**IMPORTANT:**
- Do NOT make accusations
- Report only observable technical correlations
- Use evidence-based observations only
- Maintain professional investigator tone"""


def build_multi_subject_prompt(investigation_info: dict, data_summary: dict, correlation_data: dict) -> str:
    """Build AI prompt for multi-subject correlation analysis."""
    
    subjects_info = "\n".join([
        f"- {s['name']} (Source IP: {s['source_ip']}): {s['sessions']} sessions, {s['unique_destinations']} unique IPs"
        for s in data_summary['suspects'][:10]
    ])
    
    correlation_summary = ""
    if correlation_data:
        correlation_summary = f"""
**CORRELATION ANALYSIS RESULTS:**
- Gang Probability Score: {correlation_data.get('gang_score', 0)}/100
- Shared IPs Found: {len(correlation_data.get('shared_ips', []))}
- Synchronized Windows: {len(correlation_data.get('sync_windows', []))}
- Shared Infrastructure: {correlation_data.get('shared_infra', {}).get('shared_servers_count', 0)} servers
"""
    
    return f"""You are an expert Cyber Crime IPDR Analyst conducting a MULTI-SUBJECT CORRELATION INVESTIGATION.

**INVESTIGATION DETAILS:**
- Mode: {investigation_info['description']}
- Unique Subscribers Found: {investigation_info['unique_count']}
- Identifier Type: {investigation_info['identifier_type']}
- Total Records: {data_summary['summary']['total_records']:,}
- Date Range: {data_summary['summary']['date_range']}

**SUBJECTS IDENTIFIED:**
{subjects_info}

{correlation_summary}

**AGGREGATE STATISTICS:**
- Unique Destination IPs: {data_summary['summary']['unique_destination_ips']}
- Tor Sessions (Total): {data_summary['summary']['tor_sessions']}
- Foreign Connections (Total): {data_summary['summary']['foreign_connections']}
- Off-Hours Activity: {data_summary['summary']['off_hours_activity']}

**Top Shared Destination IPs:**
{chr(10).join([f"- {ip}: {count} total connections" for ip, count in list(data_summary['top_destinations'].items())[:10]])}

**ANALYSIS FOCUS AREAS:**
{chr(10).join([f"- {area}" for area in investigation_info['focus_areas']])}

**YOUR TASK:**
As a Cyber Crime IPDR Analyst, analyze these multiple subjects and identify correlations:

**FINDINGS (Use this exact format for each finding):**

FINDING #1
Type: [Common Destination / Shared Infrastructure / Coordinated Activity / Network Cluster / Temporal Correlation / Central Node]
Severity: [LOW / MEDIUM / HIGH / CRITICAL]
Confidence: [LOW / MEDIUM / HIGH]

Evidence:
- IPs involved: [list specific IPs]
- Subscribers involved: [list subjects]
- Time range: [specific correlation windows]
- Pattern: [describe the correlation]

Assessment:
[Explain why this correlation may indicate coordinated activity or shared infrastructure]

Risk Score: [0-100]

---

**ALSO PROVIDE:**

**EXECUTIVE SUMMARY:**
[Overview of relationships and correlations found between subjects]

**KEY FINDINGS:**
[Top 5 most significant correlations or patterns]

**CORRELATION MATRIX:**
[Describe strength of relationships between subjects]

**NETWORK CLUSTERS:**
[Identify groups of subjects with strong connections]

**INVESTIGATION LEADS:**
[Specific actionable items for multi-subject investigation]

**RECOMMENDED NEXT STEPS:**
[Concrete actions for investigating subject relationships]

**OVERALL RISK ASSESSMENT:**
Investigation Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]
Coordination Score: [0-100]

**IMPORTANT:**
- Do NOT make accusations
- Report only observable technical correlations between subjects
- Use evidence-based observations only
- Identify patterns that may indicate coordinated activity
- Maintain professional investigator tone"""


def parse_findings(ai_text: str) -> dict:
    """Parse AI response into structured findings format."""
    
    findings_list = []
    sections = {
        "executive_summary": "",
        "key_findings": [],
        "correlation_matrix": "",
        "network_clusters": "",
        "timeline_analysis": "",
        "investigation_leads": [],
        "recommended_steps": [],
        "risk_assessment": "",
        "overall_risk_score": 0
    }
    
    lines = ai_text.split('\n')
    current_section = None
    current_finding = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect finding blocks
        if line.startswith('FINDING #'):
            if current_finding:
                findings_list.append(current_finding)
            current_finding = {
                "number": line.replace('FINDING #', '').strip(),
                "type": "",
                "severity": "",
                "confidence": "",
                "evidence": [],
                "assessment": "",
                "risk_score": 0
            }
            continue
        
        # Parse finding details
        if current_finding:
            if line.startswith('Type:'):
                current_finding['type'] = line.replace('Type:', '').strip()
            elif line.startswith('Severity:'):
                current_finding['severity'] = line.replace('Severity:', '').strip()
            elif line.startswith('Confidence:'):
                current_finding['confidence'] = line.replace('Confidence:', '').strip()
            elif line.startswith('Evidence:'):
                current_section = 'evidence'
            elif line.startswith('Assessment:'):
                current_section = 'assessment'
            elif line.startswith('Risk Score:'):
                score_text = line.replace('Risk Score:', '').strip()
                try:
                    current_finding['risk_score'] = int(score_text.split('/')[0])
                except:
                    current_finding['risk_score'] = 0
                current_section = None
            elif current_section == 'evidence' and line.startswith('-'):
                current_finding['evidence'].append(line.lstrip('- '))
            elif current_section == 'assessment':
                current_finding['assessment'] += line + " "
        
        # Parse other sections
        if 'EXECUTIVE SUMMARY' in line.upper():
            current_section = 'executive_summary'
            current_finding = None
        elif 'KEY FINDINGS' in line.upper():
            current_section = 'key_findings'
            current_finding = None
        elif 'CORRELATION MATRIX' in line.upper():
            current_section = 'correlation_matrix'
            current_finding = None
        elif 'NETWORK CLUSTERS' in line.upper():
            current_section = 'network_clusters'
            current_finding = None
        elif 'TIMELINE ANALYSIS' in line.upper():
            current_section = 'timeline_analysis'
            current_finding = None
        elif 'INVESTIGATION LEADS' in line.upper():
            current_section = 'investigation_leads'
            current_finding = None
        elif 'RECOMMENDED NEXT STEPS' in line.upper() or 'RECOMMENDED STEPS' in line.upper():
            current_section = 'recommended_steps'
            current_finding = None
        elif 'OVERALL RISK ASSESSMENT' in line.upper() or 'RISK ASSESSMENT' in line.upper():
            current_section = 'risk_assessment'
            current_finding = None
        elif current_section and not current_finding:
            if current_section in ['executive_summary', 'correlation_matrix', 'network_clusters', 'timeline_analysis', 'risk_assessment']:
                if not line.startswith('**') and not line.startswith('#'):
                    sections[current_section] += line + " "
            elif current_section in ['key_findings', 'investigation_leads', 'recommended_steps']:
                if line.startswith('-') or line.startswith('*') or line[0].isdigit():
                    sections[current_section].append(line.lstrip('-*123456789. '))
    
    # Add last finding if exists
    if current_finding:
        findings_list.append(current_finding)
    
    # Extract overall risk score
    risk_text = sections['risk_assessment']
    if 'Score:' in risk_text or 'score:' in risk_text.lower():
        try:
            score_part = risk_text.split('Score:')[-1] if 'Score:' in risk_text else risk_text.split('score:')[-1]
            sections['overall_risk_score'] = int(''.join(filter(str.isdigit, score_part.split()[0])))
        except:
            sections['overall_risk_score'] = 50
    
    sections['findings'] = findings_list
    sections['full_analysis'] = ai_text
    
    return sections


def generate_fallback_findings(df: pd.DataFrame) -> dict:
    """Generate basic findings when AI fails."""
    
    investigation_info = identify_unique_subscribers(df)
    
    findings = {
        "executive_summary": f"Analysis of {len(df)} IPDR records. Investigation mode: {investigation_info['description']}.",
        "key_findings": [
            f"Tor usage detected: {int(df['Is_TOR'].sum())} sessions" if int(df['Is_TOR'].sum()) > 0 else None,
            f"Foreign connections: {int(df['Is_Foreign_IP'].sum())} sessions" if int(df['Is_Foreign_IP'].sum()) > 0 else None,
        ],
        "findings": [],
        "investigation_leads": ["Manual review required - AI analysis unavailable"],
        "recommended_steps": ["Configure Gemini API key for detailed AI analysis"],
        "risk_assessment": "Unable to perform automated risk assessment",
        "overall_risk_score": 50
    }
    
    return findings
    """Generate automatic suspicious activity flags without AI (fast fallback)."""
    
    flags = []
    
    # Tor usage
    tor_count = int(df['Is_TOR'].sum())
    if tor_count > 0:
        flags.append({
            "emoji": "🔴",
            "name": "TOR NETWORK USAGE",
            "severity": "CRITICAL",
            "description": f"{tor_count} sessions using Tor network detected. Indicates attempt to hide identity.",
            "count": tor_count
        })
    
    # Foreign IPs
    foreign_count = int(df['Is_Foreign_IP'].sum())
    if foreign_count > 10:
        flags.append({
            "emoji": "🌍",
            "name": "FOREIGN IP CONNECTIONS",
            "severity": "HIGH",
            "description": f"{foreign_count} connections to foreign IP addresses detected.",
            "count": foreign_count
        })
    
    # Off-hours activity
    off_hours = int(df['Is_Off_Hours'].sum())
    if off_hours > 20:
        flags.append({
            "emoji": "🌙",
            "name": "OFF-HOURS ACTIVITY",
            "severity": "MEDIUM",
            "description": f"{off_hours} sessions during unusual hours (12 AM - 6 AM).",
            "count": off_hours
        })
    
    # Suspicious ports
    suspicious_ports = [9050, 22, 23, 3389, 445, 1080, 8080, 4444, 5900, 3128]
    sus_port_count = len(df[df['Destination_Port'].isin(suspicious_ports)])
    if sus_port_count > 0:
        ports_used = df[df['Destination_Port'].isin(suspicious_ports)]['Destination_Port'].unique()
        flags.append({
            "emoji": "⚠️",
            "name": "SUSPICIOUS PORT USAGE",
            "severity": "HIGH",
            "description": f"{sus_port_count} connections using suspicious ports: {', '.join(map(str, ports_used[:5]))}",
            "count": sus_port_count
        })
    
    # Port scanning detection
    port_scan_ips = df.groupby('Destination_IP')['Destination_Port'].nunique()
    potential_scans = len(port_scan_ips[port_scan_ips > 10])
    if potential_scans > 0:
        flags.append({
            "emoji": "🔍",
            "name": "PORT SCANNING ACTIVITY",
            "severity": "CRITICAL",
            "description": f"{potential_scans} destination IPs contacted on 10+ different ports. Indicates reconnaissance.",
            "count": potential_scans
        })
    
    # Large data transfers
    large_transfers = len(df[df['Data_Volume_Bytes'] > 100 * 1024 * 1024])
    if large_transfers > 5:
        flags.append({
            "emoji": "📤",
            "name": "LARGE DATA TRANSFERS",
            "severity": "HIGH",
            "description": f"{large_transfers} sessions with >100MB data transfer. Possible data exfiltration.",
            "count": large_transfers
        })
    
    # VPN usage
    vpn_count = int(df['Is_VPN_Suspected'].sum()) if 'Is_VPN_Suspected' in df.columns else 0
    if vpn_count > 5:
        flags.append({
            "emoji": "🔒",
            "name": "VPN/PROXY USAGE",
            "severity": "MEDIUM",
            "description": f"{vpn_count} sessions using VPN or proxy services.",
            "count": vpn_count
        })
    
    return flags


def generate_ai_flags(df: pd.DataFrame) -> list:
    """Generate automatic suspicious activity flags without AI (fast fallback)."""
    
    flags = []
    
    # Tor usage
    tor_count = int(df['Is_TOR'].sum())
    if tor_count > 0:
        flags.append({
            "emoji": "🔴",
            "name": "TOR NETWORK USAGE",
            "severity": "CRITICAL",
            "description": f"{tor_count} sessions using Tor network detected. Indicates attempt to hide identity.",
            "count": tor_count
        })
    
    # Foreign IPs
    foreign_count = int(df['Is_Foreign_IP'].sum())
    if foreign_count > 10:
        flags.append({
            "emoji": "🌍",
            "name": "FOREIGN IP CONNECTIONS",
            "severity": "HIGH",
            "description": f"{foreign_count} connections to foreign IP addresses detected.",
            "count": foreign_count
        })
    
    # Off-hours activity
    off_hours = int(df['Is_Off_Hours'].sum())
    if off_hours > 20:
        flags.append({
            "emoji": "🌙",
            "name": "OFF-HOURS ACTIVITY",
            "severity": "MEDIUM",
            "description": f"{off_hours} sessions during unusual hours (12 AM - 6 AM).",
            "count": off_hours
        })
    
    # Suspicious ports
    suspicious_ports = [9050, 22, 23, 3389, 445, 1080, 8080, 4444, 5900, 3128]
    sus_port_count = len(df[df['Destination_Port'].isin(suspicious_ports)])
    if sus_port_count > 0:
        ports_used = df[df['Destination_Port'].isin(suspicious_ports)]['Destination_Port'].unique()
        flags.append({
            "emoji": "⚠️",
            "name": "SUSPICIOUS PORT USAGE",
            "severity": "HIGH",
            "description": f"{sus_port_count} connections using suspicious ports: {', '.join(map(str, ports_used[:5]))}",
            "count": sus_port_count
        })
    
    # Port scanning detection
    port_scan_ips = df.groupby('Destination_IP')['Destination_Port'].nunique()
    potential_scans = len(port_scan_ips[port_scan_ips > 10])
    if potential_scans > 0:
        flags.append({
            "emoji": "🔍",
            "name": "PORT SCANNING ACTIVITY",
            "severity": "CRITICAL",
            "description": f"{potential_scans} destination IPs contacted on 10+ different ports. Indicates reconnaissance.",
            "count": potential_scans
        })
    
    # Large data transfers
    large_transfers = len(df[df['Data_Volume_Bytes'] > 100 * 1024 * 1024])
    if large_transfers > 5:
        flags.append({
            "emoji": "📤",
            "name": "LARGE DATA TRANSFERS",
            "severity": "HIGH",
            "description": f"{large_transfers} sessions with >100MB data transfer. Possible data exfiltration.",
            "count": large_transfers
        })
    
    # VPN usage
    vpn_count = int(df['Is_VPN_Suspected'].sum()) if 'Is_VPN_Suspected' in df.columns else 0
    if vpn_count > 5:
        flags.append({
            "emoji": "🔒",
            "name": "VPN/PROXY USAGE",
            "severity": "MEDIUM",
            "description": f"{vpn_count} sessions using VPN or proxy services.",
            "count": vpn_count
        })
    
    return flags
