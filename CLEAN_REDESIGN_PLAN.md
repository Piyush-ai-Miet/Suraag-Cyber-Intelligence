# Clean Multiple IPDR Redesign

## Concept
- **1 IPDR File = 1 Suspect/Person**
- File ka naam = Suspect ka naam
- Each file has that person's internet activity

## Structure

### Single IPDR (1 file)
```
1. Dashboard
   - Total sessions
   - Unique IPs contacted
   - Data volume
   - Suspicious flags (Tor, Foreign, Off-hours)

2. MITRE ATT&CK
   - Attack patterns detected

3. Map
   - Show all destination IPs on map
   
4. Connection Graph
   - Suspect → All IPs contacted

5. AI Chatbot
   - Ask questions about this person's activity
```

### Multiple IPDR (2+ files)
```
1. Dashboard
   - Per-suspect stats
   - Comparison view

2. Common IPs Section
   - Which IPs were contacted by multiple suspects?
   - PRIMARY evidence of connection

3. MITRE ATT&CK
   - Combined threats

4. Map
   - Show all suspects + destinations
   - Highlight shared IPs

5. Connection Graph
   - Suspects → IPs
   - Show shared connections

6. AI Bot
   - Analyze connections
   - Explain why suspects might be related
```

## Simple Gang Detection Logic

```python
shared_ips = find_common_ips(file1, file2)

if len(shared_ips) > 0:
    print(f"Connection Found!")
    print(f"Both suspects contacted {len(shared_ips)} same IPs")
    
    if any_tor_ips(shared_ips):
        print("CRITICAL: Shared Tor/Proxy usage")
    
    if same_time_window(file1, file2, shared_ips):
        print("COORDINATED: Same IPs within 30 minutes")
else:
    print("No connection detected")
```

## Implementation Steps

1. Keep existing dashboard
2. Simplify gang analysis (just show shared IPs)
3. Keep MITRE, Map, Graph as-is
4. AI bot explains findings in plain English
