<div align="center">

```
███████╗██╗   ██╗██████╗  █████╗  █████╗  ██████╗
██╔════╝██║   ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
███████╗██║   ██║██████╔╝███████║███████║██║  ███╗
╚════██║██║   ██║██╔══██╗██╔══██║██╔══██║██║   ██║
███████║╚██████╔╝██║  ██║██║  ██║██║  ██║╚██████╔╝
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
```

# सुराग — Cyber Intelligence Platform

**वो देखो जो data छुपाता है**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-00D4FF?style=for-the-badge)](LICENSE)

> Built during **Gurugram Police Cyber Security Summer Internship 2026**  
> Under the guidance of **Dr. Rakshit Tandon**

</div>

---

## 🔍 What is Suराग?

**Suराग** (Hindi: *clue/evidence*) is a cyber investigation platform designed for law enforcement to analyze **IPDR** (Internet Protocol Detail Records) and **CDR** (Call Detail Records). It helps investigators uncover hidden connections, detect suspicious patterns, and generate actionable intelligence reports — powered by AI.

---

## ✨ Features

### 📡 IPDR Analysis (Streamlit App)
| Feature | Description |
|---|---|
| **Single Suspect Analysis** | Full breakdown of one person's internet activity |
| **Multi-Suspect Correlation** | Compare multiple IPDRs to find connections & shared IPs |
| **MITRE ATT&CK Mapping** | Auto-detect attack techniques from traffic patterns |
| **Geo Intelligence Map** | Visualize all destination IPs on an interactive world map |
| **Network Graph** | See who connected to what — suspect → IP relationship graph |
| **AI Chatbot** | Ask natural language questions about the data |
| **PDF Report Generator** | One-click forensic report export |
| **Risk Scoring** | Automated threat level calculation per suspect |

### 📞 CDR Analysis (Standalone HTML Tool)
- Call pattern timeline visualization
- Frequent contact detection
- Location tower mapping
- Duration & frequency analysis
- No installation required — runs directly in browser

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
pip
```

### Installation
```bash
# Clone the repo
git clone https://github.com/Piyush-ai-Miet/Suraag-Cyber-Intelligence.git
cd Suraag-Cyber-Intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure API Keys
```bash
# Copy example env file
cp .env.example .env

# Add your keys in .env
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### Run
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🛠️ Tech Stack

```
Frontend       →  Streamlit + Custom CSS (Neon Dark Theme)
AI Engine      →  Google Gemini 2.0 Flash / OpenRouter / DeepSeek
Maps           →  Folium + Leaflet.js
Graphs         →  Pyvis + NetworkX + Plotly
CDR Tool       →  Vanilla HTML/JS (Chart.js + Leaflet)
Reports        →  ReportLab PDF
Data           →  Pandas + NumPy
```

---

## 📁 Project Structure

```
Suraag-Cyber-Intelligence/
│
├── app.py                          # Main Streamlit application
├── config.py                       # App config & environment loader
├── requirements.txt                # Python dependencies
│
├── modules/
│   ├── ipdr_analyzer.py            # Core IPDR parsing & analysis
│   ├── multi_ipdr_analyzer.py      # Multi-suspect correlation engine
│   ├── ai_multi_ipdr_analyzer.py   # AI-powered multi-IPDR analysis
│   ├── chatbot.py                  # AI chatbot module
│   ├── correlation_engine.py       # Gang/connection detection
│   ├── geo_mapper.py               # Geographic IP mapping
│   ├── network_graph.py            # Relationship graph builder
│   ├── mitre_mapper.py             # MITRE ATT&CK framework mapper
│   ├── risk_scorer.py              # Threat risk scoring
│   ├── traffic_patterns.py         # Traffic behavior analysis
│   └── report_gen.py               # PDF report generation
│
├── CDR_Analysis_Tool_v2.html       # Standalone CDR analysis tool
├── IPDR_Analysis_Tool_v5.html      # Standalone IPDR HTML tool
│
└── data/
    └── *.csv                       # Sample IPDR datasets
```

---

## 🔬 How It Works

```
Upload IPDR CSV(s)
        ↓
   Parse & Clean Data
        ↓
   ┌────────────────────────────┐
   │  Single File?              │
   │  → Individual Analysis     │
   │                            │
   │  Multiple Files?           │
   │  → Find Shared IPs         │
   │  → Check Time Correlation  │
   │  → Detect Gang Connections │
   └────────────────────────────┘
        ↓
   Map + Graph + MITRE
        ↓
   AI Chatbot for Q&A
        ↓
   Generate PDF Report
```

---

## 🧪 Sample Data

Sample IPDR CSV files are included in the `data/` folder to test the platform without real data.

```bash
# Generate your own synthetic IPDR data
python generate_realistic_ipdr.py
```

---

---

## 👨‍💻 Author

**Piyush**  
Cyber Security Intern — Gurugram Police GPCSSI 2026  
Mentor: **Dr. Rakshit Tandon**

---

<div align="center">

*Built with ❤️ for law enforcement — to find the clues data hides*

**सुराग — वो देखो जो data छुपाता है**

</div>
