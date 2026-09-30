# 📊 Multiple IPDR Connection Analysis - Logic Explained

## 🎯 Overview
Yeh system multiple IPDR files ko analyze karke **criminal gang connections** detect karta hai. Matlab agar 2 ya zyada suspects ek saath kaam kar rahe hain, toh yeh tool unko identify karega.

---

## 🔍 Kaise Connections Identify Hote Hain?

### **1️⃣ Shared IP Addresses (40% weightage)**

**Logic:**
```python
# Agar same destination IP address multiple suspects use kar rahe hain
# Toh wo same server/website/service access kar rahe hain

Example:
- Suspect A → connects to 192.168.1.100
- Suspect B → connects to 192.168.1.100  
- Suspect C → connects to 192.168.1.100

Result: YEH STRONG EVIDENCE HAI gang connection ka!
```

**Kyu Important Hai?**
- Same server ka matlab = same criminal infrastructure
- Same dark web site access kar rahe hain
- Same C2 (Command & Control) server use kar rahe hain

**Score Calculation:**
```
IP Score = min(Shared_IPs_Count × 15, 100)
- 1 shared IP  = 15 points
- 7 shared IPs = 100 points (maximum)
```

---

### **2️⃣ Synchronized Time Windows (30% weightage)**

**Logic:**
```python
# Agar multiple suspects same time window (15 minutes ke andar) 
# active hote hain, toh coordinated activity hai

Example:
- Suspect A: Active at 2:10 PM - 2:25 PM
- Suspect B: Active at 2:15 PM - 2:30 PM
- Suspect C: Active at 2:12 PM - 2:27 PM

Result: 15-minute overlap = SYNCHRONIZED ACTIVITY!
```

**Kyu Important Hai?**
- Planned operations mein timing match hoti hai
- Group chat/call ke during internet use hota hai
- Cyber attacks coordinated hote hain (same time)

**Score Calculation:**
```
Sync Score = min(Sync_Windows_Count × 5, 100)
- 5 sync windows  = 25 points
- 20 sync windows = 100 points (maximum)
```

---

### **3️⃣ Shared Infrastructure (30% weightage)**

**Logic:**
```python
# Same ports, ISPs, servers use kar rahe hain?

Components:
A) Shared Destination Servers
B) Shared Ports (e.g., 9050 = Tor, 1194 = VPN)
C) Shared ISPs
```

**Example:**
```
- All suspects using Port 9050 (Tor)
- All suspects using Port 4444 (Metasploit)
- Same VPN provider (ISP)

Result: SAME TOOLS & INFRASTRUCTURE = Gang connection!
```

**Score Calculation:**
```
Infra Score = min(
    (Shared_Servers × 10) + (Shared_Ports × 5),
    100
)
```

---

## 🎲 Final Gang Probability Score Formula

```python
Final Score = (IP_Score × 40%) + (Sync_Score × 30%) + (Infra_Score × 30%)

Range: 0 - 100
```

---

## 📊 Verdict Categories

### 🟢 **ISOLATED INCIDENTS (0-30)**
```
- Suspects independent hain
- Koi connection nahi
- Coincidence ho sakta hai
```

### 🟠 **POSSIBLY LINKED (31-65)**
```
- Kuch patterns match kar rahe hain
- Weak connection hai
- Further investigation needed
```

### 🔴 **ORGANIZED SYNDICATE (66-100)**
```
- Strong gang evidence
- Coordinated criminal activity
- Immediate action required
```

---

## 💡 Real-World Example

### Case: 3 Suspects ka Analysis

**Input Files:**
- suspect_A_ipdr.csv
- suspect_B_ipdr.csv  
- suspect_C_ipdr.csv

**Analysis Process:**

#### Step 1: Shared IPs Found
```
IP: 45.67.89.100
- Used by: Suspect A, Suspect B, Suspect C
- Sessions: 127 total
- Risk: CRITICAL

IP: 123.45.67.89
- Used by: Suspect A, Suspect B
- Sessions: 45 total  
- Risk: HIGH
```
**Score: 30 points** (2 shared IPs × 15)

#### Step 2: Sync Windows Found
```
Window: 2024-06-01 14:15 IST
- Active: Suspect A, Suspect B, Suspect C

Window: 2024-06-01 18:30 IST
- Active: Suspect A, Suspect C

Window: 2024-06-01 22:00 IST
- Active: Suspect B, Suspect C
```
**Score: 15 points** (3 windows × 5)

#### Step 3: Shared Infrastructure
```
Shared Ports:
- Port 9050 (Tor): All 3 suspects
- Port 1194 (VPN): Suspect A, B

Shared Servers:
- 5 destination servers common

ISP Overlap:
- 2 suspects same ISP
```
**Score: 70 points** (5 servers × 10 + 4 ports × 5)

#### Final Calculation:
```
Gang Score = (30 × 40%) + (15 × 30%) + (70 × 30%)
           = 12 + 4.5 + 21
           = 37.5
           = 38/100
```

**Verdict:** 🟠 **POSSIBLY LINKED**

---

## 🔐 Evidence Generation

Tool automatically generates plain-English evidence:

```
✓ IP 45.67.89.100 was contacted by 3 different suspects 
  (Suspect A, Suspect B, Suspect C) — same server is 
  strongest gang link.

✓ 3 time windows found where multiple suspects were 
  online simultaneously — coordinated operations detected.

✓ 5 destination servers shared across suspects — 
  shared infrastructure indicates organized group.

✓ Same ports (9050, 1194, 4444) used by multiple suspects —
  same criminal tools being used.
```

---

## 🚀 Technical Implementation

### File Upload & Combine
```python
# Multiple files upload
uploaded_files = st.file_uploader(accept_multiple_files=True)

# Combine all DataFrames
combined_df = pd.concat([pd.read_csv(f) for f in uploaded_files])
```

### Correlation Analysis
```python
# Tag each file with suspect label
df["_suspect_label"] = "Suspect A"

# Find shared IPs
shared_ips = df.groupby("Destination_IP")["_suspect_label"]
              .apply(lambda x: list(set(x)))
              .reset_index()

# Keep only IPs used by 2+ suspects
shared_ips = shared_ips[shared_ips["count"] >= 2]
```

### Time Window Synchronization
```python
# Round timestamps to 15-minute windows
df["Window"] = df["Timestamp"].dt.floor("15min")

# Find windows with 2+ suspects active
sync_windows = df.groupby("Window")["_suspect_label"]
                .nunique()

sync_windows = sync_windows[sync_windows >= 2]
```

---

## ✅ Benefits

1. **Automatic Gang Detection**: Manual checking nahi karna padta
2. **Evidence-Based**: Clear proof with numbers
3. **Scalable**: 100+ files bhi handle kar sakta hai
4. **Visual Insights**: Graphs aur tables se samajhna easy
5. **Confidence Score**: 0-100 scale pe clarity

---

## 🎯 Use Cases

### ✓ Drug Trafficking Networks
- Multiple dealers sharing same supply chain servers
- Coordinated delivery timings

### ✓ Cyber Crime Syndicates
- Phishing gang using same C2 servers
- DDoS attacks from coordinated IPs

### ✓ Terrorist Communication
- Same encrypted messaging servers
- Synchronized activity before events

### ✓ Money Laundering Networks
- Multiple accounts, same banking servers
- Coordinated transaction timings

---

## 🔧 Configuration

**Sync Window**: 15 minutes (adjustable)
```python
SYNC_WINDOW_MINUTES = 15
```

**Gang Thresholds**:
```python
GANG_THRESHOLDS = {
    "isolated":   (0,  30),   # No connection
    "linked":     (31, 65),   # Possible gang
    "syndicate":  (66, 100),  # Strong gang evidence
}
```

---

## 📝 Summary

**Multiple IPDR Connection Analysis yeh detect karta hai:**

1. ✅ Shared IP addresses (same servers)
2. ✅ Synchronized activity (same time)
3. ✅ Shared infrastructure (same tools)
4. ✅ Gang probability score (0-100)
5. ✅ Evidence-based verdict
6. ✅ Plain-English explanation

**Result:** Officer ko clear picture milta hai ki suspects ek saath kaam kar rahe hain ya nahi!

---

**Developed by:** Piyush & Kush
**For:** Gurugram Police Cyber Security Summer Internship 2026