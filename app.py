"""
app.py — Suराग: Cyber Intelligence & IPDR Analysis Platform
Main Streamlit application with sidebar navigation.
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import time

from config import (
    APP_NAME, APP_TAGLINE, APP_ORG, APP_ADVISOR,
    COLOR_BG, COLOR_CARD, COLOR_BORDER, COLOR_ACCENT,
    COLOR_TEXT, COLOR_MUTED, COLOR_CRITICAL, COLOR_HIGH,
)

# ── Page config MUST be first ─────────────────────────────
st.set_page_config(
    page_title="Suराग — Cyber Investigation",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS (Modern Neon Theme - Optimized) ────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── CSS Variables (EXACT from zip file) ─────────────────────────── */
:root {{
    --bg-900: hsl(220, 14%, 4%);
    --surface-800: hsl(215, 48%, 10%);
    --muted-700: hsl(212, 33%, 13%);
    --muted-text: hsl(215, 14%, 65%);
    --accent-1: hsl(158, 100%, 50%);
    --accent-2: hsl(193, 100%, 67%);
    --accent-3: hsl(256, 100%, 65%);
    --foreground: hsl(210, 40%, 98%);
    --border: hsl(215, 28%, 17%);
}}

/* ── Keyframe Animations (Simplified) ─────────────────────────── */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}

/* ── Body & Root Styling (EXACT from zip) ─────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg-900) !important;
    color: var(--foreground) !important;
}}

/* ── Main Background with Grid ─────────────────────────────────── */
.main {{
    background: var(--bg-900) !important;
    position: relative;
}}

.main::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        linear-gradient(to right, hsl(158, 100%, 50%, 0.1) 1px, transparent 1px),
        linear-gradient(to bottom, hsl(158, 100%, 50%, 0.1) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse 80% 50% at 50% 0%, #000 70%, transparent 100%);
    z-index: -1;
    pointer-events: none;
}}

/* ── Sidebar (EXACT from zip file) ─────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: var(--surface-800) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{
    color: var(--foreground) !important;
}}
[data-testid="stSidebar"] > div {{
    background: var(--surface-800) !important;
}}

/* ── Main Content Area (EXACT from zip) ───────────────────────────────────── */
.main .block-container {{
    background: transparent !important;
    padding: 1rem 1.5rem !important;
    max-width: none !important;
}}

.stApp {{
    background: var(--bg-900) !important;
}}

/* ── Buttons (EXACT from zip) ─────────────────────────────────── */
.stButton > button {{
    background: var(--accent-1) !important;
    color: var(--bg-900) !important;
    border: none !important;
    border-radius: 0.375rem !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background: hsl(158, 100%, 45%) !important;
    transform: translateY(-1px) !important;
}}

/* ── File Uploader (Exact Zip Style) ───────────────────────────── */
[data-testid="stFileUploader"] {{
    background: hsl(215, 48%, 10%);
    border: 2px dashed hsl(215, 28%, 17%);
    border-radius: 0.5rem;
    padding: 2rem;
    transition: all 0.3s ease;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: hsl(215, 28%, 25%);
    transform: translateY(-1px);
}}
[data-testid="stFileUploader"] > div {{
    background: transparent !important;
}}
[data-testid="stFileUploader"] label {{
    color: hsl(215, 14%, 65%) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
[data-testid="stFileUploader"] button {{
    background: hsl(158, 100%, 50%) !important;
    color: hsl(220, 14%, 4%) !important;
    border: none !important;
    border-radius: 0.375rem !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"] button:hover {{
    background: hsl(158, 100%, 45%) !important;
    transform: translateY(-1px) !important;
}}

/* ── Glass Morphism Expanders ───────────────────────────── */
[data-testid="stExpander"] {{
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.8), rgba(13, 17, 23, 0.6));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    margin-bottom: 16px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.6s ease-out both;
    position: relative;
    overflow: hidden;
}}
[data-testid="stExpander"]:hover {{
    border-color: rgba(0, 255, 148, 0.4);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 255, 148, 0.1);
    transform: translateY(-2px);
}}
[data-testid="stExpander"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-neon), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}}
[data-testid="stExpander"]:hover::before {{
    opacity: 1;
}}
[data-testid="stExpander"] summary {{
    color: var(--text-primary) !important;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}}

/* ── Enhanced Metric Cards ────────────────────────────────── */
[data-testid="stMetric"] {{
    background: linear-gradient(135deg, var(--surface-800), var(--muted-700));
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.7s ease-out both;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(15px);
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 255, 148, 0.15);
    border-color: rgba(0, 255, 148, 0.3);
}}
[data-testid="stMetric"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-neon), var(--accent-cyan));
    transform: scaleX(0);
    transition: transform 0.3s;
}}
[data-testid="stMetric"]:hover::before {{
    transform: scaleX(1);
}}
[data-testid="stMetricLabel"] {{
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'monospace', monospace;
}}
[data-testid="stMetricValue"] {{
    color: var(--text-primary) !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    font-family: 'Inter', sans-serif;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}}

/* ── Modern Alert Styling ──────────────────────────────────── */
.stAlert {{
    border-radius: 16px;
    border: none;
    animation: fadeInUp 0.5s ease-out both;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}}

/* ── Enhanced Input Fields ─────────────────────────────────── */
.stTextInput > div > div > input {{
    background: linear-gradient(135deg, var(--surface-800), var(--muted-700));
    color: var(--text-primary);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    font-family: 'Inter', sans-serif;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}}
.stTextInput > div > div > input:focus {{
    border-color: var(--accent-neon);
    box-shadow: 0 0 0 3px rgba(0, 255, 148, 0.2), 0 0 20px rgba(0, 255, 148, 0.1);
    background: linear-gradient(135deg, var(--muted-700), var(--surface-800));
}}

/* ── Select Box Enhancement ──────────────────────────────── */
.stSelectbox > div > div {{
    background: linear-gradient(135deg, var(--surface-800), var(--muted-700));
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    color: var(--text-primary);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}}
.stSelectbox > div > div:hover {{
    border-color: rgba(0, 255, 148, 0.4);
}}

/* ── Enhanced DataFrames ──────────────────────────────────── */
.stDataFrame {{
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    overflow: hidden;
    animation: fadeInUp 0.6s ease-out both;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
}}

/* ── Neon Spinner ─────────────────────────────────────────── */
.stSpinner > div {{
    border-top-color: var(--accent-neon) !important;
    animation: neonPulse 1.5s ease-in-out infinite;
}}

/* ── Stylized Dividers ────────────────────────────────────── */
hr {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-neon), transparent);
    opacity: 0.6;
    margin: 2rem 0;
    box-shadow: 0 0 10px var(--accent-neon);
}}

/* ── Enhanced Tabs ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: linear-gradient(135deg, var(--surface-800), var(--muted-700));
    border-radius: 16px;
    padding: 8px;
    border: 1px solid var(--border-subtle);
    gap: 6px;
    backdrop-filter: blur(15px);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 12px;
    color: var(--text-muted);
    font-weight: 600;
    transition: all 0.3s ease;
    font-family: 'Inter', sans-serif;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(0, 255, 148, 0.2), rgba(139, 92, 246, 0.1));
    color: var(--accent-neon) !important;
    box-shadow: 0 4px 12px rgba(0, 255, 148, 0.2);
    border: 1px solid rgba(0, 255, 148, 0.3);
}}

/* ── Radio Buttons ───────────────────────────────────────── */
.stRadio > div > label {{
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif;
}}

/* ── Enhanced Labels ──────────────────────────────────────── */
.stSelectbox label, .stTextInput label, .stFileUploader label {{
    color: var(--text-muted) !important;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'monospace', monospace;
}}

/* ── Neon Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ 
    background: var(--bg-primary); 
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb {{ 
    background: linear-gradient(180deg, var(--accent-neon), var(--accent-cyan)); 
    border-radius: 4px;
    box-shadow: 0 0 10px rgba(0, 255, 148, 0.5);
}}
::-webkit-scrollbar-thumb:hover {{ 
    background: linear-gradient(180deg, var(--accent-cyan), var(--accent-violet));
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.7);
}}

/* ── Enhanced Plotly Charts ───────────────────────────────── */
.js-plotly-plot {{
    border-radius: 16px;
    overflow: hidden;
    animation: fadeInUp 0.8s ease-out both;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border: 1px solid var(--border-subtle);
}}

/* ── Glassmorphism Card Class ─────────────────────────────── */
.glass-card {{
    background: linear-gradient(135deg, rgba(22, 27, 34, 0.9), rgba(13, 17, 23, 0.8));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 24px 28px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.6s ease-out both;
    position: relative;
    overflow: hidden;
}}
.glass-card:hover {{
    border-color: rgba(0, 255, 148, 0.4);
    box-shadow: 0 16px 60px rgba(0, 0, 0, 0.4), 0 0 30px rgba(0, 255, 148, 0.1);
    transform: translateY(-4px);
}}
.glass-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-neon), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}}
.glass-card:hover::before {{
    opacity: 1;
}}

/* ── Animated Stagger for Metric Cards ───────────── */
[data-testid="column"]:nth-child(1) [data-testid="stMetric"] {{ animation-delay: 0.1s; }}
[data-testid="column"]:nth-child(2) [data-testid="stMetric"] {{ animation-delay: 0.2s; }}
[data-testid="column"]:nth-child(3) [data-testid="stMetric"] {{ animation-delay: 0.3s; }}
[data-testid="column"]:nth-child(4) [data-testid="stMetric"] {{ animation-delay: 0.4s; }}

/* ── Enhanced Section Header ──────────────────────────────── */
.section-hdr {{
    position: relative;
    overflow: hidden;
    border-radius: 16px;
}}
.section-hdr::after {{
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 148, 0.1), transparent);
    animation: scanline 6s linear infinite;
    pointer-events: none;
    z-index: 1;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HELPER UI COMPONENTS
# ══════════════════════════════════════════════════════════

def card(content_html: str, padding: str = "1.2rem 1.5rem"):
    """Render content inside a dark card."""
    st.markdown(
        f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
        border-radius:12px;padding:{padding};margin-bottom:12px">
        {content_html}</div>""",
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a premium section header with glassmorphism and animated scanline."""
    icon_html = f"<span style='font-size:24px;margin-right:10px'>{icon}</span>" if icon else ""
    sub = f"<p style='color:{COLOR_MUTED};font-size:12px;margin:8px 0 0 0;font-weight:400;line-height:1.5'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""<div class="section-hdr" style="margin:32px 0 18px 0;padding:18px 24px;
        background:linear-gradient(135deg, {COLOR_ACCENT}0D, {COLOR_CARD}CC, {COLOR_BG});
        backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
        border-left:4px solid {COLOR_ACCENT};border:1px solid {COLOR_ACCENT}18;
        border-left:4px solid {COLOR_ACCENT};border-radius:12px;
        box-shadow:0 4px 20px rgba(0,0,0,0.2);
        animation:fadeInUp 0.5s ease-out both">
        <div style="display:flex;align-items:center">
        {icon_html}
        <h3 style="color:{COLOR_ACCENT};font-size:20px;font-weight:800;margin:0;
        letter-spacing:-0.3px;text-shadow:0 0 20px {COLOR_ACCENT}33">{title}</h3>
        </div>
        {sub}</div>""",
        unsafe_allow_html=True,
    )


def plain_english_box(text: str, icon: str = "💡"):
    """Render a plain-English summary box for non-technical officers."""
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,rgba(27, 79, 114, 0.2),rgba(0, 212, 255, 0.1));
        border:1px solid rgba(0, 212, 255, 0.4);border-radius:10px;
        padding:12px 16px;margin:8px 0 16px 0">
        <span style="font-size:16px">{icon}</span>
        <span style="color:#E6EDF3;font-size:13px;line-height:1.6;margin-left:8px">
        {text}</span></div>""",
        unsafe_allow_html=True,
    )


def risk_badge(score: int, size: str = "normal") -> str:
    """Return HTML for a colored risk score badge."""
    if score >= 80:
        color, label = COLOR_CRITICAL, "CRITICAL"
    elif score >= 60:
        color, label = COLOR_HIGH, "HIGH"
    elif score >= 40:
        color, label = "#FFD700", "MEDIUM"
    else:
        color, label = "#3FB950", "LOW"

    fs = "16px" if size == "large" else "12px"
    px = "6px 12px" if size == "large" else "3px 8px"
    return (
        f"<span style='background:{color}22;color:{color};border:1px solid {color};"
        f"border-radius:6px;padding:{px};font-weight:700;font-size:{fs};font-family:Inter,sans-serif'>"
        f"{score}/100 {label}</span>"
    )


def mitre_chip(level: str, text: str) -> str:
    colors_map = {"CRITICAL": COLOR_CRITICAL, "HIGH": COLOR_HIGH, "MEDIUM": "#FFD700", "LOW": "#3FB950"}
    c = colors_map.get(level.upper(), COLOR_MUTED)
    return (
        f"<span style='background:{c}22;color:{c};border:1px solid {c}44;"
        f"border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;"
        f"margin:2px;display:inline-block'>{text}</span>"
    )


def empty_state(message: str, icon: str = "📂"):
    st.markdown(
        f"""<div style="text-align:center;padding:60px 20px;background:#161B22;
        border:2px dashed #21262D;border-radius:16px;margin:20px 0">
        <div style="font-size:48px;margin-bottom:12px">{icon}</div>
        <p style="color:#7D8590;font-size:15px;max-width:400px;margin:0 auto;line-height:1.6">
        {message}</p></div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════

with st.sidebar:
    # Simple Clean Professional Logo
    logo_html = """<div style="padding: 1.5rem 1rem 1rem 1rem; border-bottom: 1px solid hsl(215, 28%, 17%); text-align: center;">
<div style="width: 80px; height: 80px; margin: 0 auto 1rem auto; background: linear-gradient(135deg, hsl(158, 100%, 50%, 0.2), hsl(193, 100%, 67%, 0.2)); border: 3px solid hsl(158, 100%, 50%); border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; box-shadow: 0 0 20px hsl(158, 100%, 50%, 0.5);">
<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="hsl(158, 100%, 50%)" stroke-width="2.5">
<circle cx="11" cy="11" r="8"/>
<path d="m21 21-4.35-4.35"/>
</svg>
</div>
<h1 style="font-size: 2.5rem; font-weight: 800; color: hsl(158, 100%, 50%); margin: 0 0 0.5rem 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; text-shadow: 0 0 20px hsl(158, 100%, 50%, 0.5), 0 0 40px hsl(158, 100%, 50%, 0.3); letter-spacing: 1px;">suराग</h1>
<p style="font-size: 0.8rem; color: hsl(215, 14%, 65%); margin: 0 0 0.75rem 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">"Woh dekho jo data chhupata hai"</p>
<div style="display: inline-block; padding: 0.25rem 0.75rem; background: hsl(158, 100%, 50%, 0.1); border: 1px solid hsl(158, 100%, 50%, 0.3); border-radius: 12px;">
<p style="font-size: 0.625rem; color: hsl(158, 100%, 50%); margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">IPDR Investigation</p>
</div>
</div>"""
    
    st.markdown(logo_html, unsafe_allow_html=True)

    # Navigation Menu (with Dashboard and History sections)
    nav_html = """<div style="padding: 0.5rem;">
<div style="margin-bottom: 0.25rem;">
<a href="#dashboard" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 0.375rem; background: hsl(215, 28%, 17%); color: hsl(210, 40%, 98%); text-decoration: none; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 500; font-size: 0.875rem; transition: all 0.2s ease;">
<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
<polyline points="9 22 9 12 15 12 15 22"/>
</svg>
<span>Dashboard</span>
</a>
</div>
<div style="margin-bottom: 0.25rem;">
<a href="#history" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 0.375rem; background: transparent; color: hsl(215, 14%, 65%); text-decoration: none; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 500; font-size: 0.875rem; transition: all 0.2s ease;">
<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
<circle cx="12" cy="12" r="10"/>
<polyline points="12 6 12 12 16 14"/>
</svg>
<span>History</span>
</a>
</div>
</div>"""
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Old radio buttons (hidden but functional)
    st.markdown(
        """<style>
        div[data-testid="stRadio"] {
            display: none !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    page = st.radio(
        "Navigation",
        ["📊 IPDR Forensic Analyzer", "🔗 Gang Correlation Analysis", "🌐 Web Analysis Tools"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    
    # Sidebar Separator
    st.markdown('<div style="height: 1px; background: hsl(215, 28%, 17%); margin: 1rem 0;"></div>', unsafe_allow_html=True)
    
    # Recent Reports Section Header
    recent_header_html = """<div style="padding: 0 0.5rem; margin-bottom: 0.5rem;">
<h2 style="font-size: 0.875rem; font-weight: 600; color: hsl(215, 14%, 65%); margin: 0; display: flex; align-items: center; gap: 0.5rem; font-family: 'Fira Code', monospace; text-transform: uppercase; letter-spacing: 0.05em;">
<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
<rect width="18" height="18" x="3" y="3" rx="2"/>
<path d="M3 9h18"/>
<path d="M9 21V9"/>
</svg>
Recent Reports
</h2>
</div>"""
    
    st.markdown(recent_header_html, unsafe_allow_html=True)
    
    # Empty State (when no files uploaded)
    empty_state_html = """<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1rem; margin: 0 0.5rem; margin-top: 1rem; border-radius: 0.5rem; background: hsl(215, 28%, 17%, 0.5); text-align: center; border: 1px dashed hsl(215, 28%, 17%);">
<svg width="40" height="40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="color: hsl(158, 100%, 50%); margin-bottom: 0.75rem;">
<path d="M3 3v16a2 2 0 0 0 2 2h16"/>
<path d="m19 9-5 5-4-4-3 3"/>
</svg>
<h3 style="margin: 0 0 0.25rem 0; font-size: 0.875rem; font-weight: 600; color: hsl(210, 40%, 98%); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">Ready for Analysis</h3>
<p style="margin: 0 0 1rem 0; font-size: 0.75rem; color: hsl(215, 14%, 65%, 0.7); font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">Upload a file to generate and view your first graph report.</p>
</div>"""
    
    st.markdown(empty_state_html, unsafe_allow_html=True)
    
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # Confidential Warning
    warning_html = f"""<div style="text-align:center; padding:16px; background:linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 127, 0.05)); border:2px solid #EF4444; border-radius:12px; backdrop-filter:blur(10px); box-shadow:0 0 30px rgba(239, 68, 68, 0.2)">
<div style="display:flex; align-items:center; justify-content:center; margin-bottom:6px">
<span style="font-size:16px; margin-right:8px">⚠️</span>
<p style='color:#EF4444; font-size:11px; font-weight:700; margin:0; letter-spacing:1px; font-family:"Inter",sans-serif'>CONFIDENTIAL</p>
</div>
<p style='color:var(--text-muted); font-size:9px; margin:0; font-family:"monospace",monospace'>LAW ENFORCEMENT USE ONLY</p>
</div>"""
    
    st.markdown(warning_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 1: IPDR ANALYZER
# ══════════════════════════════════════════════════════════

if page == "📊 IPDR Forensic Analyzer":

    # Exact Dashboard from zip file
    st.markdown(
        """
        <h1 style="
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 700;
            font-size: 1.875rem;
            color: #F0F6FC;
            margin: 0 0 1.5rem 0;
            line-height: 1.2;
        ">Dashboard</h1>
        """,
        unsafe_allow_html=True,
    )
    
    # New Analysis Card (exact from zip)
    st.markdown(
        """
        <div style="
            background: hsl(215, 48%, 10%);
            border: 1px solid hsl(215, 28%, 17%);
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        ">
            <div style="padding: 1.5rem 1.5rem 0 1.5rem;">
                <h2 style="
                    font-size: 1.5rem;
                    font-weight: 600;
                    line-height: 1;
                    color: hsl(210, 40%, 98%);
                    margin: 0 0 0.375rem 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">New Analysis</h2>
                <p style="
                    font-size: 0.875rem;
                    color: hsl(215, 14%, 65%);
                    margin: 0;
                    line-height: 1.5;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Upload one or more IPDR log files to begin analysis and visualization. Multiple files will be automatically combined.</p>
            </div>
            <div style="padding: 1.5rem;">
        """,
        unsafe_allow_html=True,
    )

    # File uploader - MULTIPLE FILES SUPPORT
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["csv"],
        help="Drag and drop one or more IPDR files here",
        key="ipdr_upload_dashboard",
        label_visibility="collapsed",
        accept_multiple_files=True
    )
    
    # Combine multiple files into one dataframe
    uploaded_file = None
    if uploaded_files:
        if len(uploaded_files) == 1:
            uploaded_file = uploaded_files[0]
        else:
            # Multiple files - combine them
            st.markdown(
                f"""<div style="background: hsl(158, 100%, 50%, 0.1); border: 1px solid hsl(158, 100%, 50%, 0.3); 
                border-radius: 0.375rem; padding: 0.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg width="20" height="20" fill="none" stroke="hsl(158, 100%, 50%)" viewBox="0 0 24 24" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span style="color: hsl(158, 100%, 50%); font-size: 0.875rem; font-weight: 600; font-family: 'Inter', sans-serif;">
                {len(uploaded_files)} files uploaded - Combining data...</span>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Combine all CSV files
            combined_dfs = []
            for idx, file in enumerate(uploaded_files):
                try:
                    df = pd.read_csv(file)
                    combined_dfs.append(df)
                    st.markdown(
                        f"""<div style="color: hsl(215, 14%, 65%); font-size: 0.75rem; padding: 0.25rem 0; 
                        font-family: 'Inter', sans-serif;">✓ {file.name} ({len(df)} rows)</div>""",
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
            
            if combined_dfs:
                # Create a combined dataframe
                combined_df = pd.concat(combined_dfs, ignore_index=True)
                
                # Store in session state to use later
                if 'combined_ipdr_data' not in st.session_state:
                    st.session_state.combined_ipdr_data = combined_df
                else:
                    st.session_state.combined_ipdr_data = combined_df
                
                st.markdown(
                    f"""<div style="background: hsl(215, 48%, 10%); border: 1px solid hsl(158, 100%, 50%, 0.3); 
                    border-radius: 0.375rem; padding: 0.75rem; margin-top: 0.5rem;">
                    <span style="color: hsl(158, 100%, 50%); font-size: 0.875rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                    Combined Total: {len(combined_df)} rows</span>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Create a dummy uploaded_file object for compatibility
                class DummyFile:
                    def __init__(self, name, df):
                        self.name = name
                        self._df = df
                    def getvalue(self):
                        return self._df.to_csv(index=False).encode()
                
                uploaded_file = DummyFile(f"Combined_{len(uploaded_files)}_files.csv", combined_df)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

    if uploaded_file is None:
        # How It Works Card (exact from zip)
        st.markdown(
            """
            <div style="
                background: hsl(215, 48%, 10%);
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
            ">
                <div style="padding: 1.5rem 1.5rem 0 1.5rem;">
                    <h2 style="
                        font-size: 1.5rem;
                        font-weight: 600;
                        line-height: 1;
                        color: hsl(210, 40%, 98%);
                        margin: 0 0 0.375rem 0;
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    ">How It Works</h2>
                    <p style="
                        font-size: 0.875rem;
                        color: hsl(215, 14%, 65%);
                        margin: 0;
                        line-height: 1.5;
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    ">A simple, powerful three-step process.</p>
                </div>
                <div style="
                    padding: 1.5rem;
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 1.5rem;
                ">
            """,
            unsafe_allow_html=True,
        )
        
        # Step 1
        st.markdown(
            """
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 1rem;
                border-radius: 0.5rem;
                background: hsl(215, 28%, 17%, 0.5);
            ">
                <div style="
                    display: flex;
                    height: 4rem;
                    width: 4rem;
                    margin-bottom: 1rem;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: hsl(158, 100%, 50%, 0.1);
                    color: hsl(158, 100%, 50%);
                    box-shadow: 0 0 20px hsl(158, 100%, 50%, 0.5), inset 0 0 8px hsl(158, 100%, 50%, 0.3);
                ">
                    <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                    </svg>
                </div>
                <h3 style="
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin: 0 0 0.5rem 0;
                    color: hsl(210, 40%, 98%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">1. Upload File</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    line-height: 1.5;
                    margin: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Upload single or multiple IPDR files. The system automatically combines them for comprehensive analysis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Step 2  
        st.markdown(
            """
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 1rem;
                border-radius: 0.5rem;
                background: hsl(215, 28%, 17%, 0.5);
            ">
                <div style="
                    display: flex;
                    height: 4rem;
                    width: 4rem;
                    margin-bottom: 1rem;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: hsl(158, 100%, 50%, 0.1);
                    color: hsl(158, 100%, 50%);
                    box-shadow: 0 0 20px hsl(158, 100%, 50%, 0.5), inset 0 0 8px hsl(158, 100%, 50%, 0.3);
                ">
                    <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/>
                        <path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>
                    </svg>
                </div>
                <h3 style="
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin: 0 0 0.5rem 0;
                    color: hsl(210, 40%, 98%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">2. AI Analysis</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    line-height: 1.5;
                    margin: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Our backend maps connections and uses an AI model to detect anomalous sessions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Step 3
        st.markdown(
            """
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 1rem;
                border-radius: 0.5rem;
                background: hsl(215, 28%, 17%, 0.5);
            ">
                <div style="
                    display: flex;
                    height: 4rem;
                    width: 4rem;
                    margin-bottom: 1rem;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: hsl(158, 100%, 50%, 0.1);
                    color: hsl(158, 100%, 50%);
                    box-shadow: 0 0 20px hsl(158, 100%, 50%, 0.5), inset 0 0 8px hsl(158, 100%, 50%, 0.3);
                ">
                    <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
                    </svg>
                </div>
                <h3 style="
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin: 0 0 0.5rem 0;
                    color: hsl(210, 40%, 98%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">3. Interactive Graph</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    line-height: 1.5;
                    margin: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Explore your data in an interactive 2D/3D graph. Click to investigate findings.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        from modules.ipdr_analyzer import (
            load_and_validate, compute_summary_stats,
            get_suspect_profiles, format_bytes, format_indian,
        )
        from modules.mitre_mapper import run_mitre_mapping, get_risk_color as mitre_risk_color, get_mitre_summary_text
        from modules.risk_scorer import compute_risk_scores, get_risk_color, get_overall_risk_score
        from modules.traffic_patterns import build_hourly_timeline, build_heatmap, get_peak_hour_summary
        from modules.geo_mapper import build_geo_map
        from modules.network_graph import build_network_graph, render_graph
        from modules.chatbot import render_chatbot
        from modules.report_gen import generate_pdf

        # Load and validate
        with st.spinner("📥 Loading and validating IPDR data..."):
            df, error = load_and_validate(uploaded_file.getvalue(), uploaded_file.name)

        if error:
            st.error(f"❌ **File Error:** {error}")
            st.stop()

        # Extract phone numbers from Subscriber_ID
        df['Phone_Number'] = df['Subscriber_ID'].str.extract(r'(\d{10})$')[0]
        
        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Store original dataframe
        df_original = df.copy()

        # ── ADVANCED SEARCH/FILTER SECTION ────────────────────
        section_header(
            "🔍 Advanced Search & Filters",
            "Search and filter IPDR data by phone number, IP address, location, ports, date range, or suspect name",
            "🔎"
        )
        
        with st.expander("📱 Search & Filter Options", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**📞 Phone Number**")
                phone_search = st.text_input(
                    "Enter 10-digit number",
                    placeholder="e.g., 9876543210",
                    key="phone_search",
                    label_visibility="collapsed"
                )
                
                st.markdown("**🌐 IP Address**")
                ip_search = st.text_input(
                    "Source or Destination IP",
                    placeholder="e.g., 182.68.16.18",
                    key="ip_search",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**🏙️ City Filter (Multi-Select)**")
                
                # Comprehensive list of Indian cities with states
                all_indian_cities = {
                    'Mumbai': 'Maharashtra',
                    'Delhi': 'Delhi',
                    'Bangalore': 'Karnataka',
                    'Hyderabad': 'Telangana',
                    'Ahmedabad': 'Gujarat',
                    'Chennai': 'Tamil Nadu',
                    'Kolkata': 'West Bengal',
                    'Pune': 'Maharashtra',
                    'Jaipur': 'Rajasthan',
                    'Surat': 'Gujarat',
                    'Lucknow': 'Uttar Pradesh',
                    'Kanpur': 'Uttar Pradesh',
                    'Nagpur': 'Maharashtra',
                    'Indore': 'Madhya Pradesh',
                    'Thane': 'Maharashtra',
                    'Bhopal': 'Madhya Pradesh',
                    'Visakhapatnam': 'Andhra Pradesh',
                    'Pimpri-Chinchwad': 'Maharashtra',
                    'Patna': 'Bihar',
                    'Vadodara': 'Gujarat',
                    'Ghaziabad': 'Uttar Pradesh',
                    'Ludhiana': 'Punjab',
                    'Agra': 'Uttar Pradesh',
                    'Nashik': 'Maharashtra',
                    'Faridabad': 'Haryana',
                    'Meerut': 'Uttar Pradesh',
                    'Rajkot': 'Gujarat',
                    'Kalyan-Dombivali': 'Maharashtra',
                    'Vasai-Virar': 'Maharashtra',
                    'Varanasi': 'Uttar Pradesh',
                    'Srinagar': 'Jammu and Kashmir',
                    'Aurangabad': 'Maharashtra',
                    'Dhanbad': 'Jharkhand',
                    'Amritsar': 'Punjab',
                    'Navi Mumbai': 'Maharashtra',
                    'Allahabad': 'Uttar Pradesh',
                    'Ranchi': 'Jharkhand',
                    'Howrah': 'West Bengal',
                    'Coimbatore': 'Tamil Nadu',
                    'Jabalpur': 'Madhya Pradesh',
                    'Gwalior': 'Madhya Pradesh',
                    'Vijayawada': 'Andhra Pradesh',
                    'Jodhpur': 'Rajasthan',
                    'Madurai': 'Tamil Nadu',
                    'Raipur': 'Chhattisgarh',
                    'Kota': 'Rajasthan',
                    'Chandigarh': 'Chandigarh',
                    'Guwahati': 'Assam',
                    'Solapur': 'Maharashtra',
                    'Hubli-Dharwad': 'Karnataka',
                    'Mysore': 'Karnataka',
                    'Tiruchirappalli': 'Tamil Nadu',
                    'Bareilly': 'Uttar Pradesh',
                    'Aligarh': 'Uttar Pradesh',
                    'Tiruppur': 'Tamil Nadu',
                    'Moradabad': 'Uttar Pradesh',
                    'Jalandhar': 'Punjab',
                    'Bhubaneswar': 'Odisha',
                    'Salem': 'Tamil Nadu',
                    'Warangal': 'Telangana',
                    'Mira-Bhayandar': 'Maharashtra',
                    'Thiruvananthapuram': 'Kerala',
                    'Bhiwandi': 'Maharashtra',
                    'Saharanpur': 'Uttar Pradesh',
                    'Guntur': 'Andhra Pradesh',
                    'Amravati': 'Maharashtra',
                    'Bikaner': 'Rajasthan',
                    'Noida': 'Uttar Pradesh',
                    'Jamshedpur': 'Jharkhand',
                    'Bhilai': 'Chhattisgarh',
                    'Cuttack': 'Odisha',
                    'Firozabad': 'Uttar Pradesh',
                    'Kochi': 'Kerala',
                    'Nellore': 'Andhra Pradesh',
                    'Bhavnagar': 'Gujarat',
                    'Dehradun': 'Uttarakhand',
                    'Durgapur': 'West Bengal',
                    'Asansol': 'West Bengal',
                    'Rourkela': 'Odisha',
                    'Nanded': 'Maharashtra',
                    'Kolhapur': 'Maharashtra',
                    'Ajmer': 'Rajasthan',
                    'Akola': 'Maharashtra',
                    'Gulbarga': 'Karnataka',
                    'Jamnagar': 'Gujarat',
                    'Ujjain': 'Madhya Pradesh',
                    'Loni': 'Uttar Pradesh',
                    'Siliguri': 'West Bengal',
                    'Jhansi': 'Uttar Pradesh',
                    'Ulhasnagar': 'Maharashtra',
                    'Jammu': 'Jammu and Kashmir',
                    'Sangli-Miraj': 'Maharashtra',
                    'Mangalore': 'Karnataka',
                    'Erode': 'Tamil Nadu',
                    'Belgaum': 'Karnataka',
                    'Ambattur': 'Tamil Nadu',
                    'Tirunelveli': 'Tamil Nadu',
                    'Malegaon': 'Maharashtra',
                    'Gaya': 'Bihar',
                    'Jalgaon': 'Maharashtra',
                    'Udaipur': 'Rajasthan',
                    'Maheshtala': 'West Bengal',
                }
                
                # Get cities available in IPDR data
                cities_in_data = set(df['City'].unique().tolist())
                states_in_data = set(df['State'].unique().tolist()) if 'State' in df.columns else set()
                
                # Create options: Available cities first (with state), then all other cities
                available_options = []
                other_options = []
                
                # Add available cities from data (prioritize)
                for city in sorted(cities_in_data):
                    if city and city != 'Unknown':
                        state = all_indian_cities.get(city, 'Unknown State')
                        if 'State' in df.columns:
                            # Get state from data if available
                            state_from_data = df[df['City'] == city]['State'].iloc[0] if len(df[df['City'] == city]) > 0 else state
                            if state_from_data and state_from_data != 'Unknown':
                                state = state_from_data
                        available_options.append(f"✓ {city}, {state}")
                
                # Add all other major cities
                for city, state in sorted(all_indian_cities.items()):
                    if city not in cities_in_data:
                        other_options.append(f"{city}, {state}")
                
                # Combine: available first, then divider, then others
                all_options = available_options
                if available_options and other_options:
                    all_options.append("─" * 30)  # Divider
                all_options.extend(other_options)
                
                selected_city_options = st.multiselect(
                    "Select Cities",
                    all_options,
                    key="city_filter",
                    label_visibility="collapsed",
                    placeholder="All Cities"
                )
                
                st.markdown("**� State Filter (Multi-Select)**")
                
                # Build state options with cities count
                state_to_cities = {}
                for city, state in all_indian_cities.items():
                    if state not in state_to_cities:
                        state_to_cities[state] = []
                    state_to_cities[state].append(city)
                
                # Get available states from data
                available_state_options = []
                other_state_options = []
                
                for state in sorted(state_to_cities.keys()):
                    cities_list = state_to_cities[state]
                    cities_in_this_state = [c for c in cities_list if c in cities_in_data]
                    
                    if cities_in_this_state:
                        # State has data - show at top with checkmark and cities
                        cities_str = ', '.join(cities_in_this_state[:3])
                        if len(cities_in_this_state) > 3:
                            cities_str += f" +{len(cities_in_this_state)-3}"
                        available_state_options.append(f"✓ {state} ({cities_str})")
                    else:
                        other_state_options.append(f"{state}")
                
                # Combine state options
                all_state_options = available_state_options
                if available_state_options and other_state_options:
                    all_state_options.append("─" * 30)
                all_state_options.extend(other_state_options)
                
                selected_state_options = st.multiselect(
                    "Select States",
                    all_state_options,
                    key="state_filter",
                    label_visibility="collapsed",
                    placeholder="All States"
                )
            
            with col3:
                st.markdown("**� Suspect Name**")
                all_names = ['All'] + sorted(df['Subscriber_Name'].unique().tolist())
                name_filter = st.selectbox(
                    "Select Name",
                    all_names,
                    key="name_filter",
                    label_visibility="collapsed"
                )
                
                st.markdown("**�🔌 Port Filter (Multi-Select)**")
                port_options = {
                    'Tor SOCKS (9050)': 9050,
                    'SSH (22)': 22,
                    'Telnet (23)': 23,
                    'SMTP (25)': 25,
                    'DNS (53)': 53,
                    'HTTP (80)': 80,
                    'HTTPS (443)': 443,
                    'SMB (445)': 445,
                    'SOCKS Proxy (1080)': 1080,
                    'MySQL (3306)': 3306,
                    'RDP (3389)': 3389,
                    'PostgreSQL (5432)': 5432,
                    'VNC (5900)': 5900,
                    'HTTP Alt (8080)': 8080,
                    'HTTPS Alt (8443)': 8443,
                    'Tor Dir (9030)': 9030,
                    'Proxy (3128)': 3128,
                    'FTP (21)': 21,
                    'SFTP (22)': 22,
                    'IMAP (143)': 143,
                }
                selected_ports = st.multiselect(
                    "Select Ports",
                    list(port_options.keys()),
                    key="port_filter",
                    label_visibility="collapsed",
                    placeholder="All Ports"
                )
                
                st.markdown("**📊 Data Volume Filter**")
                data_filter_options = ['All', 'High Volume (>100MB)', 'Very High (>500MB)', 'Low (<10MB)']
                data_filter = st.selectbox(
                    "Filter by Data",
                    data_filter_options,
                    key="data_filter",
                    label_visibility="collapsed"
                )
            
            with col4:
                st.markdown("**📅 Date Range**")
                min_date = df['Timestamp'].min().date()
                max_date = df['Timestamp'].max().date()
                
                date_from = st.date_input(
                    "From Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="date_from"
                )
                
                date_to = st.date_input(
                    "To Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="date_to"
                )
            
            # Apply filters button
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                apply_filters = st.button("🔍 Apply Filters", type="primary", use_container_width=True)
            with col_btn2:
                reset_filters = st.button("🔄 Reset", use_container_width=True)
        
        # Apply filters logic
        if reset_filters:
            df = df_original.copy()
            st.rerun()
        
        if apply_filters or phone_search or ip_search:
            df_filtered = df_original.copy()
            
            # Phone number filter
            if phone_search and phone_search.strip():
                df_filtered = df_filtered[df_filtered['Phone_Number'].str.contains(phone_search.strip(), na=False)]
            
            # IP address filter
            if ip_search and ip_search.strip():
                df_filtered = df_filtered[
                    (df_filtered['Source_IP'].str.contains(ip_search.strip(), na=False)) |
                    (df_filtered['Destination_IP'].str.contains(ip_search.strip(), na=False))
                ]
            
            # City filter (multi-select with state)
            if selected_city_options:
                # Extract city names from "City, State" or "✓ City, State" format
                selected_cities = []
                for option in selected_city_options:
                    if option.startswith("─"):  # Skip divider
                        continue
                    # Remove checkmark and extract city name
                    city_part = option.replace("✓ ", "").split(",")[0].strip()
                    selected_cities.append(city_part)
                
                if selected_cities:
                    df_filtered = df_filtered[df_filtered['City'].isin(selected_cities)]
            
            # State filter (multi-select)
            if selected_state_options:
                # Extract state names from options
                selected_states = []
                for option in selected_state_options:
                    if option.startswith("─"):  # Skip divider
                        continue
                    # Remove checkmark and extract state name (before parenthesis)
                    state_part = option.replace("✓ ", "").split("(")[0].strip()
                    selected_states.append(state_part)
                
                if selected_states and 'State' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['State'].isin(selected_states)]
            
            # Name filter
            if name_filter != 'All':
                df_filtered = df_filtered[df_filtered['Subscriber_Name'] == name_filter]
            
            # Port filter (multi-select for both source and destination)
            if selected_ports:
                selected_port_nums = [port_options[p] for p in selected_ports]
                df_filtered = df_filtered[
                    (df_filtered['Source_Port'].isin(selected_port_nums)) |
                    (df_filtered['Destination_Port'].isin(selected_port_nums))
                ]
            
            # Data volume filter
            if data_filter == 'High Volume (>100MB)':
                df_filtered = df_filtered[df_filtered['Data_Volume_Bytes'] > 100 * 1024 * 1024]
            elif data_filter == 'Very High (>500MB)':
                df_filtered = df_filtered[df_filtered['Data_Volume_Bytes'] > 500 * 1024 * 1024]
            elif data_filter == 'Low (<10MB)':
                df_filtered = df_filtered[df_filtered['Data_Volume_Bytes'] < 10 * 1024 * 1024]
            
            # Date range filter
            df_filtered = df_filtered[
                (df_filtered['Timestamp'].dt.date >= date_from) &
                (df_filtered['Timestamp'].dt.date <= date_to)
            ]
            
            if len(df_filtered) == 0:
                st.warning("⚠️ No results found with current filters. Try adjusting your search criteria.")
                df = df_original.copy()
            else:
                df = df_filtered.copy()
                st.success(f"✅ Found **{len(df):,}** records matching your filters (from {len(df_original):,} total)")
                
                # === FILTERED SUMMARY SECTION ===
                st.markdown("---")
                section_header(
                    "📊 Filtered Results - Complete Analysis",
                    "Comprehensive breakdown of all IPDR data for filtered results",
                    "🔍"
                )
                
                # Overall Summary Cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    unique_suspects = df['Subscriber_Name'].nunique()
                    st.metric("👤 Suspects", unique_suspects)
                
                with col2:
                    unique_ips = df['Destination_IP'].nunique()
                    st.metric("🌐 Unique IPs", unique_ips)
                
                with col3:
                    unique_isps = df['ISP'].nunique() if 'ISP' in df.columns else 0
                    st.metric("📡 ISPs", unique_isps)
                
                with col4:
                    date_range_days = (df['Timestamp'].max() - df['Timestamp'].min()).days + 1
                    st.metric("📅 Date Span", f"{date_range_days} days")
                
                # Per-Suspect Detailed Analysis
                for suspect_name in df['Subscriber_Name'].unique():
                    suspect_df = df[df['Subscriber_Name'] == suspect_name]
                    phone_num = suspect_df['Phone_Number'].iloc[0] if 'Phone_Number' in suspect_df.columns else "N/A"
                    
                    with st.expander(f"👤 **{suspect_name}** | 📱 {phone_num} | {len(suspect_df)} Sessions", expanded=False):
                        
                        # === RISK ASSESSMENT ===
                        tor_sessions = int(suspect_df['Is_TOR'].sum())
                        foreign_sessions = int(suspect_df['Is_Foreign_IP'].sum())
                        off_hours = int(suspect_df['Is_Off_Hours'].sum()) if 'Is_Off_Hours' in suspect_df.columns else 0
                        
                        # Suspicious port detection
                        suspicious_ports_list = [9050, 22, 23, 3389, 445, 1080, 8080, 8443, 5900, 3128, 9030]
                        suspicious_port_sessions = len(suspect_df[
                            (suspect_df['Destination_Port'].isin(suspicious_ports_list)) |
                            (suspect_df['Source_Port'].isin(suspicious_ports_list))
                        ])
                        
                        # Large uploads
                        if 'Upload_Bytes' in suspect_df.columns:
                            large_uploads = len(suspect_df[suspect_df['Upload_Bytes'] > 100 * 1024 * 1024])
                        else:
                            large_uploads = 0
                        
                        # Port scanning
                        port_scan_ips = suspect_df.groupby('Destination_IP')['Destination_Port'].nunique()
                        potential_port_scans = len(port_scan_ips[port_scan_ips > 10])
                        
                        # Risk scoring
                        risk_score = 0
                        risk_factors = []
                        
                        if tor_sessions > 0:
                            risk_score += tor_sessions * 3
                            risk_factors.append(f"🔴 Tor usage ({tor_sessions} sessions)")
                        if foreign_sessions > 5:
                            risk_score += foreign_sessions
                            risk_factors.append(f"🌍 Foreign connections ({foreign_sessions} sessions)")
                        if off_hours > 10:
                            risk_score += off_hours * 2
                            risk_factors.append(f"🌙 Off-hours activity ({off_hours} sessions)")
                        if suspicious_port_sessions > 0:
                            risk_score += suspicious_port_sessions * 2
                            risk_factors.append(f"⚠️ Suspicious ports ({suspicious_port_sessions} sessions)")
                        if large_uploads > 0:
                            risk_score += large_uploads * 5
                            risk_factors.append(f"📤 Large uploads ({large_uploads} files)")
                        if potential_port_scans > 0:
                            risk_score += potential_port_scans * 10
                            risk_factors.append(f"🔍 Port scanning ({potential_port_scans} IPs)")
                        
                        # Risk level
                        if risk_score > 100:
                            risk_level = "🔴 CRITICAL"
                            risk_color = "#FF4444"
                        elif risk_score > 50:
                            risk_level = "🟠 HIGH"
                            risk_color = "#FF8C00"
                        elif risk_score > 20:
                            risk_level = "🟡 MEDIUM"
                            risk_color = "#F1C40F"
                        else:
                            risk_level = "🟢 LOW"
                            risk_color = "#3FB950"
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, {risk_color}22, {risk_color}11); 
                        border-left: 4px solid {risk_color}; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: {risk_color}; font-size: 1rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                            {risk_level} | Risk Score: {risk_score}
                            </span>
                        </div>
                        <div style="color: hsl(215, 14%, 65%); font-size: 0.75rem; font-family: 'Inter', sans-serif; line-height: 1.8;">
                        <strong style="color: hsl(210, 40%, 98%);">Detected Risk Factors:</strong><br/>
                        {('<br/>• '.join(risk_factors)) if risk_factors else '✓ No significant risk factors'}
                        </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # === COMPACT IPDR FIELDS ===
                        st.markdown("#### 📋 Complete IPDR Data")
                        
                        # Device Info (if available)
                        if 'imei' in suspect_df.columns:
                            with st.expander("📱 Device Information"):
                                device_info = suspect_df.iloc[0]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**IMEI:** {device_info.get('imei', 'N/A')}")
                                    st.markdown(f"**Device:** {device_info.get('device_model', 'Unknown')}")
                                    st.markdown(f"**OS:** {device_info.get('os_version', 'Unknown')}")
                                with col2:
                                    st.markdown(f"**IMSI:** {device_info.get('IMSI', 'N/A')}")
                                    st.markdown(f"**Subscriber ID:** {device_info.get('Subscriber_ID', 'N/A')}")
                        
                        # Connection Summary
                        with st.expander("🌐 Connection Summary", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Sessions", f"{len(suspect_df):,}")
                                st.metric("Unique IPs", suspect_df['Destination_IP'].nunique())
                            with col2:
                                total_data = suspect_df['Data_Volume_Bytes'].sum() / (1024**3)
                                st.metric("Total Data", f"{total_data:.2f} GB")
                                avg_session = suspect_df['Session_Duration_sec'].mean() if 'Session_Duration_sec' in suspect_df.columns else 0
                                st.metric("Avg Session", f"{int(avg_session)}s")
                            with col3:
                                st.metric("🔴 Tor", tor_sessions)
                                st.metric("🌍 Foreign", foreign_sessions)
                        
                        # Top Apps Used
                        if 'app_name' in suspect_df.columns:
                            top_apps = suspect_df['app_name'].value_counts().head(10)
                            if len(top_apps) > 0 and top_apps.iloc[0] != 'Unknown':
                                with st.expander("📲 Top Applications Used"):
                                    for app, count in top_apps.items():
                                        if app != 'Unknown':
                                            st.markdown(f"- **{app}**: {count} sessions")
                        
                        # Top Domains/Websites
                        if 'domain' in suspect_df.columns:
                            top_domains = suspect_df['domain'].value_counts().head(10)
                            if len(top_domains) > 0 and top_domains.iloc[0] != 'unknown.com':
                                with st.expander("🌐 Top Domains Accessed"):
                                    for domain, count in top_domains.items():
                                        if domain != 'unknown.com':
                                            st.markdown(f"- **{domain}**: {count} requests")
                        
                        # Location Data
                        with st.expander("📍 Location Analysis"):
                            locations = suspect_df.groupby('City').size().sort_values(ascending=False)
                            for city, count in locations.head(10).items():
                                st.markdown(f"- **{city}**: {count} sessions")
                        
                        # Top Connected IPs with Ports
                        with st.expander("🔗 Top 10 Connected IPs", expanded=True):
                            top_ips = (
                                suspect_df.groupby('Destination_IP')
                                .agg({
                                    'Timestamp': 'count',
                                    'Data_Volume_Bytes': 'sum',
                                    'ISP': 'first',
                                    'Is_TOR': 'any',
                                    'Is_Foreign_IP': 'any',
                                    'Destination_Port': lambda x: ', '.join(sorted(set([str(p) for p in x.unique()[:5]]))),
                                    'app_name': lambda x: ', '.join(x.dropna().unique()[:3]) if 'app_name' in suspect_df.columns else 'N/A',
                                    'protocol': lambda x: ', '.join(x.dropna().unique()[:3]) if 'protocol' in suspect_df.columns else 'N/A'
                                })
                                .rename(columns={'Timestamp': 'Sessions', 'Data_Volume_Bytes': 'Total_Bytes'})
                                .sort_values('Sessions', ascending=False)
                                .head(10)
                            )
                            
                            display_data = []
                            for ip, row in top_ips.iterrows():
                                flag = "🔴 TOR" if row['Is_TOR'] else ("🌍 Foreign" if row['Is_Foreign_IP'] else "🔵 Domestic")
                                
                                # Detect suspicious ports
                                ports_str = row['Destination_Port']
                                suspicious_marks = []
                                if '9050' in ports_str:
                                    suspicious_marks.append('🔴9050')
                                if '22' in ports_str:
                                    suspicious_marks.append('⚠️22')
                                if '3389' in ports_str:
                                    suspicious_marks.append('⚠️3389')
                                if '1080' in ports_str or '8080' in ports_str:
                                    suspicious_marks.append('⚠️Proxy')
                                
                                port_display = ports_str if not suspicious_marks else f"{ports_str} [{', '.join(suspicious_marks)}]"
                                
                                row_data = {
                                    "IP": str(ip),
                                    "Type": flag,
                                    "Ports": port_display,
                                    "Protocol": row.get('protocol', 'N/A'),
                                    "Sessions": f"{int(row['Sessions']):,}",
                                    "Data (MB)": f"{row['Total_Bytes'] / 1_048_576:.2f}",
                                    "ISP": row['ISP']
                                }
                                
                                if 'app_name' in top_ips.columns and row['app_name'] != 'N/A' and row['app_name'] != 'Unknown':
                                    row_data["Apps"] = row['app_name']
                                
                                display_data.append(row_data)
                            
                            if display_data:
                                result_df = pd.DataFrame(display_data)
                                st.dataframe(result_df, use_container_width=True, hide_index=True)
                        
                        # Protocol Usage
                        if 'protocol' in suspect_df.columns:
                            with st.expander("🔐 Protocol Usage"):
                                protocol_usage = suspect_df['protocol'].value_counts().head(10)
                                for proto, count in protocol_usage.items():
                                    st.markdown(f"- **{proto}**: {count} sessions")
                        
                        # Port Analysis
                        with st.expander("🔌 Port Analysis"):
                            port_usage = suspect_df['Destination_Port'].value_counts().head(15)
                            for port, count in port_usage.items():
                                port_name = ""
                                if port == 9050:
                                    port_name = "🔴 Tor SOCKS"
                                elif port == 22:
                                    port_name = "⚠️ SSH"
                                elif port == 443:
                                    port_name = "HTTPS"
                                elif port == 80:
                                    port_name = "HTTP"
                                elif port == 3389:
                                    port_name = "⚠️ RDP"
                                elif port == 8080:
                                    port_name = "⚠️ HTTP Alt"
                                elif port == 445:
                                    port_name = "⚠️ SMB"
                                st.markdown(f"- **Port {port}** {port_name}: {count} connections")
                        
                        # Timeline
                        with st.expander("📅 Activity Timeline"):
                            date_activity = suspect_df.groupby(suspect_df['Timestamp'].dt.date).size()
                            st.line_chart(date_activity)
                        
                        # Behavior Metrics Summary
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        with col_b1:
                            st.metric("🔴 Tor", tor_sessions)
                        with col_b2:
                            st.metric("🌍 Foreign", foreign_sessions)
                        with col_b3:
                            st.metric("🌙 Off-Hours", off_hours)
                        with col_b4:
                            st.metric("⚠️ Sus Ports", suspicious_port_sessions)
                
                st.markdown("---")

        # Compute all analyses
        with st.spinner("🔬 Running forensic analysis..."):
            stats       = compute_summary_stats(df)
            risk_scores = compute_risk_scores(df)
            mitre_df    = run_mitre_mapping(df)
            profiles    = get_suspect_profiles(df)
            overall_risk = get_overall_risk_score(risk_scores)

        st.success(f"✅ Analysis complete — {format_indian(stats['total_sessions'])} sessions loaded from **{uploaded_file.name}**")

        # ── 4 METRIC CARDS (Enhanced Professional Design) ────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""<div style="background:linear-gradient(135deg, {COLOR_CARD}, {COLOR_BG});
                border:1px solid {COLOR_BORDER};border-left:3px solid {COLOR_ACCENT};
                border-radius:12px;padding:18px 16px;box-shadow:0 4px 12px {COLOR_BG}88">
                <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.8px;margin:0">📊 Total Sessions</p>
                <p style="color:{COLOR_ACCENT};font-size:28px;font-weight:700;margin:8px 0 0 0;line-height:1">
                {format_indian(stats["total_sessions"])}</p>
                <p style="color:{COLOR_MUTED};font-size:9px;margin:4px 0 0 0">Internet connections analyzed</p>
                </div>""",
                unsafe_allow_html=True,
            )
        
        with c2:
            st.markdown(
                f"""<div style="background:linear-gradient(135deg, {COLOR_CARD}, {COLOR_BG});
                border:1px solid {COLOR_BORDER};border-left:3px solid #3FB950;
                border-radius:12px;padding:18px 16px;box-shadow:0 4px 12px {COLOR_BG}88">
                <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.8px;margin:0">🌐 Unique IPs</p>
                <p style="color:#3FB950;font-size:28px;font-weight:700;margin:8px 0 0 0;line-height:1">
                {format_indian(stats["unique_ips"])}</p>
                <p style="color:{COLOR_MUTED};font-size:9px;margin:4px 0 0 0">Destination servers contacted</p>
                </div>""",
                unsafe_allow_html=True,
            )
        
        with c3:
            susp_pct = stats['suspicious_sessions']/max(stats['total_sessions'],1)*100
            st.markdown(
                f"""<div style="background:linear-gradient(135deg, {COLOR_CARD}, {COLOR_BG});
                border:1px solid {COLOR_HIGH}44;border-left:3px solid {COLOR_HIGH};
                border-radius:12px;padding:18px 16px;box-shadow:0 4px 12px {COLOR_HIGH}22">
                <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.8px;margin:0">⚠️ Suspicious</p>
                <p style="color:{COLOR_HIGH};font-size:28px;font-weight:700;margin:8px 0 0 0;line-height:1">
                {format_indian(stats["suspicious_sessions"])}</p>
                <p style="color:{COLOR_HIGH};font-size:10px;margin:4px 0 0 0;font-weight:600">
                ▲ {susp_pct:.1f}% of total sessions</p>
                </div>""",
                unsafe_allow_html=True,
            )
        
        with c4:
            risk_color = "#3FB950" if overall_risk < 40 else ("#FFD700" if overall_risk < 60 else (COLOR_HIGH if overall_risk < 80 else COLOR_CRITICAL))
            risk_emoji = "🟢" if overall_risk < 40 else ("🟡" if overall_risk < 60 else ("🟠" if overall_risk < 80 else "🔴"))
            risk_label = "LOW" if overall_risk < 40 else ("MEDIUM" if overall_risk < 60 else ("HIGH" if overall_risk < 80 else "CRITICAL"))
            
            st.markdown(
                f"""<div style="background:linear-gradient(135deg, {risk_color}11, {COLOR_BG});
                border:2px solid {risk_color};border-radius:12px;padding:18px 16px;
                box-shadow:0 4px 16px {risk_color}44">
                <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;text-transform:uppercase;
                letter-spacing:0.8px;margin:0">🎯 Overall Risk</p>
                <p style="color:{risk_color};font-size:32px;font-weight:700;margin:8px 0 0 0;line-height:1">
                {overall_risk}<span style="font-size:18px">/100</span></p>
                <p style="color:{risk_color};font-size:11px;margin:4px 0 0 0;font-weight:700">
                {risk_emoji} {risk_label} THREAT</p>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Enhanced Quick Stats Card
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, {COLOR_CARD}, #0A0E12);
            border:1px solid {COLOR_BORDER};border-radius:12px;padding:20px 24px;
            box-shadow:0 4px 16px {COLOR_BG}cc">
            <p style="color:{COLOR_ACCENT};font-size:11px;font-weight:700;margin:0 0 12px 0;
            text-transform:uppercase;letter-spacing:1px">📈 Quick Statistics</p>
            <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:20px">
                <div style="text-align:center">
                    <p style="color:{COLOR_CRITICAL};font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['tor_sessions'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">🔴 TOR Sessions</p>
                </div>
                <div style="text-align:center">
                    <p style="color:{COLOR_HIGH};font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['foreign_sessions'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">🌍 Foreign IPs</p>
                </div>
                <div style="text-align:center">
                    <p style="color:#FFD700;font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['off_hours_sessions'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">🌙 Off-Hours</p>
                </div>
                <div style="text-align:center">
                    <p style="color:{COLOR_ACCENT};font-size:24px;font-weight:700;margin:0">
                    {format_bytes(stats['total_bytes'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">📦 Data Volume</p>
                </div>
                <div style="text-align:center">
                    <p style="color:{COLOR_TEXT};font-size:24px;font-weight:700;margin:0">
                    {stats['unique_subscribers']}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">👤 Suspects</p>
                </div>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # ── MITRE ATT&CK TABLE ────────────────────────────
        section_header(
            "MITRE ATT&CK Threat Detection",
            "Automatically identifies known cyber-criminal attack patterns in the IPDR data",
            "🎯"
        )
        plain_english_box(
            "MITRE ATT&CK is the global framework used by cybersecurity investigators to identify attack patterns. "
            "The table below lists criminal techniques detected in this IPDR data, automatically matched against "
            "known threat patterns.",
            icon="ℹ️",
        )

        if mitre_df.empty:
            st.info("No MITRE ATT&CK patterns detected in this dataset.")
        else:
            with st.expander(f"📋 View Full MITRE ATT&CK Table ({len(mitre_df)} patterns detected)", expanded=True):
                for _, row in mitre_df.iterrows():
                    risk_c = mitre_risk_color(row["Risk Level"])
                    st.markdown(
                        f"""<div style="display:flex;align-items:center;gap:12px;
                        background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                        border-left:4px solid {risk_c};border-radius:8px;
                        padding:10px 14px;margin-bottom:6px">
                        <div style="flex:2">
                        <span style="color:{COLOR_TEXT};font-weight:600;font-size:13px">
                        {row['Pattern Detected']}</span><br>
                        <span style="color:{COLOR_MUTED};font-size:11px">{row['Plain Description']}</span>
                        </div>
                        <div style="flex:1;text-align:center">
                        <span style="color:{COLOR_MUTED};font-size:11px">Tactic</span><br>
                        <span style="color:{COLOR_TEXT};font-size:12px;font-weight:500">{row['MITRE Tactic']}</span>
                        </div>
                        <div style="flex:0.8;text-align:center">
                        <span style="color:{COLOR_MUTED};font-size:11px">Technique</span><br>
                        <span style="color:{COLOR_ACCENT};font-size:12px;font-family:monospace">{row['Technique ID']}</span>
                        </div>
                        <div style="flex:0.6;text-align:center">
                        <span style="color:{risk_c};background:{risk_c}22;
                        border:1px solid {risk_c}44;border-radius:6px;
                        padding:2px 8px;font-size:11px;font-weight:700">{row['Risk Level']}</span>
                        </div>
                        <div style="flex:0.6;text-align:center">
                        <span style="color:{COLOR_MUTED};font-size:11px">Sessions</span><br>
                        <span style="color:{COLOR_TEXT};font-size:14px;font-weight:600">
                        {format_indian(row['Sessions Affected'])}</span>
                        </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            plain_english_box(get_mitre_summary_text(mitre_df), icon="⚠️")

        # ── RISK SCORING ──────────────────────────────────
        section_header(
            "Suspect Risk Scores",
            "Each suspect is scored 0–100 based on how suspicious their internet activity is",
            "🔴"
        )
        plain_english_box(
            "A risk score of 0 means the person appears innocent. A score of 80 or above means there is "
            "strong evidence of criminal activity. Below, each suspect's score is shown with the top reasons "
            "in simple language.",
            icon="📊",
        )

        for _, row in risk_scores.iterrows():
            risk_c = get_risk_color(row["Risk_Score"])
            with st.expander(
                f"{'🔴' if row['Risk_Score']>=80 else '🟠' if row['Risk_Score']>=60 else '🟡' if row['Risk_Score']>=40 else '🟢'} "
                f"{row['Subscriber_Name']} — Score: {row['Risk_Score']}/100 [{row['Risk_Level']}]",
                expanded=row["Risk_Score"] >= 60,
            ):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(
                        f"<p style='color:{COLOR_MUTED};font-size:12px;margin:0'>Subscriber ID</p>"
                        f"<p style='color:{COLOR_TEXT};font-size:14px;font-weight:600;margin:0 0 12px 0'>{row['Subscriber_ID']}</p>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<p style='color:#8B949E;font-size:12px;font-weight:600;text-transform:uppercase'>Top Risk Reasons:</p>", unsafe_allow_html=True)
                    for reason in row.get("Top_Reasons", []):
                        st.markdown(f"<p style='color:{COLOR_TEXT};font-size:13px;margin:4px 0'>▸ {reason}</p>", unsafe_allow_html=True)

                with col_b:
                    st.markdown(
                        f"""<div style="text-align:center;background:{risk_c}11;
                        border:2px solid {risk_c}44;border-radius:12px;padding:16px">
                        <p style="color:{COLOR_MUTED};font-size:11px;margin:0;text-transform:uppercase">Risk Score</p>
                        <p style="color:{risk_c};font-size:40px;font-weight:700;margin:4px 0;line-height:1">{row['Risk_Score']}</p>
                        <p style="color:{risk_c};font-size:13px;font-weight:700;margin:0">{row['Risk_Level']}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    st.markdown(
                        f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Sessions: <b style='color:{COLOR_TEXT}'>{format_indian(row['Total_Sessions'])}</b></p>"
                        f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Data: <b style='color:{COLOR_TEXT}'>{format_bytes(row['Total_Bytes'])}</b></p>"
                        f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Tor: <b style='color:{COLOR_CRITICAL}'>{row['TOR_Sessions']}</b> sessions</p>"
                        f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Foreign: <b style='color:{COLOR_HIGH}'>{row['Foreign_Sessions']}</b> sessions</p>"
                        f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Off-Hours: <b style='color:#FFD700'>{row['Off_Hours_Sessions']}</b> sessions</p>",
                        unsafe_allow_html=True,
                    )

        # ── GEO MAP ───────────────────────────────────────
        section_header(
            "Geolocation Intelligence Map",
            "Interactive map showing suspect locations, destination servers, and connection links — toggle layers to explore",
            "🗺️"
        )
        plain_english_box(
            "👤 <b>Cyan circles</b> = Suspect locations  |  "
            "🔵 <b>Blue pins</b> = Indian servers (normal)  |  "
            "🔴 <b>Red pins</b> = Foreign servers  |  "
            "🟠 <b>Orange pins</b> = Tor/Proxy nodes  |  "
            "🔗 <b>Lines</b> = Connection links (color-coded by suspect). "
            "Use the layer control (top-right) to toggle connections and shared IPs. "
            "Click any marker for forensic details.",
            icon="🗺️",
        )

        with st.spinner("📍 Geolocating IP addresses (this may take a moment for large files)..."):
            try:
                geo_map, geo_summary = build_geo_map(df)
                
                # Enhanced geo metrics
                col_g1, col_g2, col_g3, col_g4 = st.columns(4)
                with col_g1:
                    st.markdown(
                        f"""<div style="background:linear-gradient(135deg,{COLOR_CARD},#0A0E12);
                        border:1px solid #3388ff44;border-left:3px solid #3388ff;
                        border-radius:12px;padding:14px;text-align:center;
                        animation:fadeInUp 0.4s ease-out both">
                        <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;margin:0;
                        text-transform:uppercase;letter-spacing:0.8px">🔵 Indian IPs</p>
                        <p style="color:#3388ff;font-size:26px;font-weight:800;margin:6px 0 0 0">{geo_summary['indian']}</p></div>""",
                        unsafe_allow_html=True,
                    )
                with col_g2:
                    st.markdown(
                        f"""<div style="background:linear-gradient(135deg,{COLOR_CARD},#0A0E12);
                        border:1px solid {COLOR_CRITICAL}44;border-left:3px solid {COLOR_CRITICAL};
                        border-radius:12px;padding:14px;text-align:center;
                        animation:fadeInUp 0.5s ease-out both">
                        <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;margin:0;
                        text-transform:uppercase;letter-spacing:0.8px">🔴 Foreign IPs</p>
                        <p style="color:{COLOR_CRITICAL};font-size:26px;font-weight:800;margin:6px 0 0 0">{geo_summary['foreign']}</p></div>""",
                        unsafe_allow_html=True,
                    )
                with col_g3:
                    st.markdown(
                        f"""<div style="background:linear-gradient(135deg,{COLOR_CARD},#0A0E12);
                        border:1px solid #FF8C0044;border-left:3px solid #FF8C00;
                        border-radius:12px;padding:14px;text-align:center;
                        animation:fadeInUp 0.6s ease-out both">
                        <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;margin:0;
                        text-transform:uppercase;letter-spacing:0.8px">🟠 Tor/Proxy</p>
                        <p style="color:#FF8C00;font-size:26px;font-weight:800;margin:6px 0 0 0">{geo_summary['tor']}</p></div>""",
                        unsafe_allow_html=True,
                    )
                with col_g4:
                    st.markdown(
                        f"""<div style="background:linear-gradient(135deg,{COLOR_CARD},#0A0E12);
                        border:1px solid {COLOR_ACCENT}44;border-left:3px solid {COLOR_ACCENT};
                        border-radius:12px;padding:14px;text-align:center;
                        animation:fadeInUp 0.7s ease-out both">
                        <p style="color:{COLOR_MUTED};font-size:10px;font-weight:600;margin:0;
                        text-transform:uppercase;letter-spacing:0.8px">📍 Total IPs</p>
                        <p style="color:{COLOR_ACCENT};font-size:26px;font-weight:800;margin:6px 0 0 0">{geo_summary['total']}</p></div>""",
                        unsafe_allow_html=True,
                    )

                from streamlit_folium import folium_static
                folium_static(geo_map, width=None, height=600)
            except Exception as e:
                st.warning(f"⚠️ Map could not be rendered: {e}. Check your internet connection for IP geolocation.")

        # ── CONNECTION DATA SUMMARY ───────────────────────
        section_header(
            "Connection Analysis",
            "See who connected where - detailed breakdown of suspect connections",
            "📊"
        )
        
        # Build connection summary
        connection_summary = []
        for sub_id in df["Subscriber_ID"].unique():
            sub_df = df[df["Subscriber_ID"] == sub_id]
            if len(sub_df) == 0:
                continue
            
            suspect_name = sub_df["Subscriber_Name"].iloc[0]
            suspect_city = sub_df["City"].iloc[0] if "City" in sub_df.columns else "Unknown"
            
            # Get unique destinations
            dest_ips = sub_df["Destination_IP"].unique()
            total_sessions = len(sub_df)
            total_data_mb = sub_df["Data_Volume_Bytes"].sum() / 1_048_576
            tor_count = int(sub_df["Is_TOR"].sum())
            foreign_count = int(sub_df["Is_Foreign_IP"].sum())
            
            # Top 5 destinations
            top_dests = (
                sub_df.groupby("Destination_IP")
                .agg({"Timestamp": "count", "Data_Volume_Bytes": "sum"})
                .sort_values("Timestamp", ascending=False)
                .head(5)
            )
            
            connection_summary.append({
                "suspect_name": suspect_name,
                "suspect_city": suspect_city,
                "total_ips": len(dest_ips),
                "total_sessions": total_sessions,
                "total_data_mb": total_data_mb,
                "tor_count": tor_count,
                "foreign_count": foreign_count,
                "top_destinations": top_dests
            })
        
        # Display connection cards
        for idx, conn in enumerate(connection_summary):
            with st.expander(f"👤 {conn['suspect_name']} - {conn['suspect_city']} ({conn['total_sessions']:,} sessions)", expanded=(idx==0)):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Unique IPs", f"{conn['total_ips']}")
                with col2:
                    st.metric("Total Data", f"{conn['total_data_mb']:.1f} MB")
                with col3:
                    st.metric("🔴 Tor Sessions", f"{conn['tor_count']}", 
                             delta=None if conn['tor_count'] == 0 else f"{(conn['tor_count']/conn['total_sessions']*100):.1f}%")
                with col4:
                    st.metric("🌍 Foreign IPs", f"{conn['foreign_count']}", 
                             delta=None if conn['foreign_count'] == 0 else f"{(conn['foreign_count']/conn['total_sessions']*100):.1f}%")
                
                st.markdown("**Top 5 Connected IPs:**")
                
                top_dest_data = []
                for ip, row in conn['top_destinations'].iterrows():
                    sessions = int(row['Timestamp'])
                    data_mb = row['Data_Volume_Bytes'] / 1_048_576
                    
                    # Check if Tor or Foreign
                    ip_df = df[(df["Subscriber_ID"] == df[df["Subscriber_Name"] == conn['suspect_name']]["Subscriber_ID"].iloc[0]) & 
                              (df["Destination_IP"] == ip)]
                    is_tor = ip_df["Is_TOR"].any() if len(ip_df) > 0 else False
                    is_foreign = ip_df["Is_Foreign_IP"].any() if len(ip_df) > 0 else False
                    
                    flag = ""
                    if is_tor:
                        flag = "🔴 TOR"
                    elif is_foreign:
                        flag = "🌍 Foreign"
                    else:
                        flag = "🔵 Domestic"
                    
                    top_dest_data.append({
                        "IP Address": str(ip),
                        "Type": flag,
                        "Sessions": f"{sessions:,}",
                        "Data (MB)": f"{data_mb:.2f}"
                    })
                
                if top_dest_data:
                    dest_df = pd.DataFrame(top_dest_data)
                    st.dataframe(dest_df, use_container_width=True, hide_index=True)

        # ── SUSPICIOUS CONNECTIONS FLAGGING ─────────────────────────────────
        section_header(
            "🚨 Suspicious Connection Alerts",
            "Automated flagging of high-risk connections based on cybercrime investigation patterns",
            "⚠️"
        )
        plain_english_box(
            "This section automatically flags suspicious connections using patterns from cybercrime investigations: "
            "<b>Tor/Proxy ports (9050, 1080, 8080)</b>, <b>SSH/RDP remote access (22, 3389)</b>, "
            "<b>Port scanning behavior</b>, <b>Large data exfiltration</b>, and <b>Off-hours foreign connections</b>.",
            icon="🔍",
        )
        
        # Create flagged connections dataframe
        flagged_connections = []
        
        for idx, row in df.iterrows():
            flags = []
            risk_score = 0
            
            # Port-based flags
            if row['Destination_Port'] == 9050 or row['Source_Port'] == 9050:
                flags.append("🔴 Tor SOCKS Proxy (Port 9050)")
                risk_score += 10
            if row['Destination_Port'] == 22 or row['Source_Port'] == 22:
                flags.append("⚠️ SSH Remote Access (Port 22)")
                risk_score += 7
            if row['Destination_Port'] == 3389 or row['Source_Port'] == 3389:
                flags.append("⚠️ RDP Remote Desktop (Port 3389)")
                risk_score += 8
            if row['Destination_Port'] in [1080, 8080, 8443] or row['Source_Port'] in [1080, 8080, 8443]:
                flags.append("⚠️ Proxy Port Detected")
                risk_score += 5
            if row['Destination_Port'] == 445 or row['Source_Port'] == 445:
                flags.append("🔴 SMB File Sharing (Port 445)")
                risk_score += 9
            
            # Behavioral flags
            if row['Is_TOR']:
                flags.append("🔴 Tor Network Connection")
                risk_score += 10
            if row['Is_Foreign_IP']:
                flags.append("🌍 Foreign IP Connection")
                risk_score += 3
            if row.get('Is_Off_Hours', False):
                flags.append("🌙 Off-Hours Activity (2AM-6AM)")
                risk_score += 4
            if row.get('Is_VPN_Suspected', False) or row.get('Is_VPN', False):
                flags.append("🔒 VPN/Proxy Detected")
                risk_score += 3
            
            # Data volume flags
            if row['Data_Volume_Bytes'] > 500 * 1024 * 1024:  # >500MB
                flags.append("📤 Very Large Data Transfer (>500MB)")
                risk_score += 6
            elif row['Data_Volume_Bytes'] > 100 * 1024 * 1024:  # >100MB
                flags.append("📤 Large Data Transfer (>100MB)")
                risk_score += 3
            
            # Only add if flags exist
            if flags:
                flagged_connections.append({
                    'Timestamp': row['Timestamp'],
                    'Subscriber': row['Subscriber_Name'],
                    'Phone': row.get('Phone_Number', 'N/A'),
                    'Destination_IP': row['Destination_IP'],
                    'Port': row['Destination_Port'],
                    'Data_MB': f"{row['Data_Volume_Bytes'] / (1024*1024):.2f}",
                    'Risk_Score': risk_score,
                    'Flags': ' | '.join(flags)
                })
        
        if flagged_connections:
            flagged_df = pd.DataFrame(flagged_connections)
            flagged_df = flagged_df.sort_values('Risk_Score', ascending=False)
            
            # Show summary
            total_flagged = len(flagged_df)
            critical = len(flagged_df[flagged_df['Risk_Score'] >= 15])
            high = len(flagged_df[(flagged_df['Risk_Score'] >= 10) & (flagged_df['Risk_Score'] < 15)])
            medium = len(flagged_df[(flagged_df['Risk_Score'] >= 5) & (flagged_df['Risk_Score'] < 10)])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🚨 Total Flagged", f"{total_flagged:,}")
            with col2:
                st.metric("🔴 Critical", f"{critical:,}")
            with col3:
                st.metric("🟠 High", f"{high:,}")
            with col4:
                st.metric("🟡 Medium", f"{medium:,}")
            
            # Show top flagged connections
            with st.expander(f"⚠️ View Top {min(50, total_flagged)} Flagged Connections", expanded=True):
                display_df = flagged_df.head(50).copy()
                display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No suspicious connection patterns detected in this dataset.")

        # ── NETWORK GRAPH ─────────────────────────────────
        section_header(
            "Suspect ↔ Server Connection Map",
            "Interactive forensic network graph — drag, zoom, and click nodes to explore suspect-server relationships",
            "🕸️"
        )
        plain_english_box(
            "🔵 <b>Colored circles</b> = Suspects (each suspect has a unique color)  |  "
            "◼ <b>Blue squares</b> = Domestic servers  |  "
            "◼ <b>Orange squares</b> = Foreign servers  |  "
            "▲ <b>Red triangles</b> = Tor exit nodes  |  "
            "◆ <b>White diamonds</b> = Shared IPs (gang evidence). "
            "Thicker lines = more data transferred. Use mouse to drag, scroll to zoom, "
            "and click nodes for detailed forensic info.",
            icon="🕸️",
        )

        with st.spinner("🔄 Building network graph..."):
            try:
                graph_html = build_network_graph(df)
                render_graph(graph_html, height=660)
            except Exception as e:
                st.warning(f"⚠️ Network graph could not be rendered: {e}")

        # ── TRAFFIC TIMELINE ──────────────────────────────
        section_header(
            "Traffic Timeline & Heatmap",
            "See when suspects were most active — the red zone (midnight to 5 AM) is the criminal fraud window",
            "⏱️"
        )

        with st.spinner("📈 Building timeline..."):
            try:
                fig_hourly  = build_hourly_timeline(df)
                fig_heatmap = build_heatmap(df)

                st.plotly_chart(fig_hourly,  use_container_width=True)
                plain_english_box(get_peak_hour_summary(df), icon="⏰")
                st.plotly_chart(fig_heatmap, use_container_width=True)
                plain_english_box(
                    "The heatmap above shows activity across days and hours. Darker cyan cells = more activity. "
                    "Any dark activity in the 00:00–05:00 columns (far left) is highly suspicious.",
                    icon="🗓️",
                )
            except Exception as e:
                st.warning(f"⚠️ Timeline could not be rendered: {e}")

        # ── SUSPECT PROFILE CARDS ─────────────────────────
        section_header(
            "Detailed Suspect Profiles",
            "Complete profile for each individual in the IPDR data",
            "👤"
        )

        for _, profile in profiles.iterrows():
            sub_risk = risk_scores[risk_scores["Subscriber_ID"] == profile["Subscriber_ID"]]
            risk_score_val = int(sub_risk["Risk_Score"].iloc[0]) if not sub_risk.empty else 0
            risk_c = get_risk_color(risk_score_val)

            sub_mitre = mitre_df  # All MITRE detections (per-suspect filtering is complex without flags)
            top_ips_list = profile.get("top_dest_ips") or []

            with st.expander(f"👤 {profile['Subscriber_Name']} — {profile['Subscriber_ID']}", expanded=False):
                p1, p2 = st.columns([3, 1])
                with p1:
                    st.markdown(
                        f"<p style='color:{COLOR_MUTED};font-size:12px;margin:0 0 8px 0'>SUBSCRIBER DETAILS</p>",
                        unsafe_allow_html=True,
                    )
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.markdown(
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Total Sessions</p>"
                            f"<p style='color:{COLOR_TEXT};font-size:16px;font-weight:700;margin:0 0 8px 0'>{format_indian(profile['total_sessions'])}</p>"
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Data Transferred</p>"
                            f"<p style='color:{COLOR_TEXT};font-size:16px;font-weight:700;margin:0 0 8px 0'>{format_bytes(profile['total_bytes'])}</p>"
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Peak Active Hour</p>"
                            f"<p style='color:{COLOR_ACCENT};font-size:16px;font-weight:700;margin:0 0 8px 0'>{int(profile.get('peak_hour',0)):02d}:00 IST</p>",
                            unsafe_allow_html=True,
                        )
                    with col_y:
                        st.markdown(
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Tor Sessions</p>"
                            f"<p style='color:{COLOR_CRITICAL};font-size:16px;font-weight:700;margin:0 0 8px 0'>{format_indian(profile['tor_sessions'])}</p>"
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Foreign Sessions</p>"
                            f"<p style='color:{COLOR_HIGH};font-size:16px;font-weight:700;margin:0 0 8px 0'>{format_indian(profile['foreign_sessions'])}</p>"
                            f"<p style='color:{COLOR_MUTED};font-size:11px;margin:2px 0'>Off-Hours Sessions</p>"
                            f"<p style='color:#FFD700;font-size:16px;font-weight:700;margin:0 0 8px 0'>{format_indian(profile['off_hours_sessions'])}</p>",
                            unsafe_allow_html=True,
                        )

                    if top_ips_list:
                        st.markdown(f"<p style='color:{COLOR_MUTED};font-size:11px;margin:8px 0 4px 0'>Top Destination IPs</p>", unsafe_allow_html=True)
                        for ip in top_ips_list[:3]:
                            st.markdown(f"<code style='background:{COLOR_CARD};color:{COLOR_ACCENT};padding:2px 6px;border-radius:4px;font-size:12px'>{ip}</code> ", unsafe_allow_html=True)

                with p2:
                    st.markdown(
                        f"""<div style="text-align:center;background:{risk_c}11;
                        border:2px solid {risk_c}44;border-radius:12px;padding:16px;margin-top:16px">
                        <p style="color:{COLOR_MUTED};font-size:10px;margin:0">RISK SCORE</p>
                        <p style="color:{risk_c};font-size:38px;font-weight:700;margin:4px 0;line-height:1">{risk_score_val}</p>
                        <p style="color:{risk_c};font-size:12px;font-weight:700;margin:0">
                        {'CRITICAL' if risk_score_val>=80 else 'HIGH' if risk_score_val>=60 else 'MEDIUM' if risk_score_val>=40 else 'LOW'}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        # ── PDF REPORT BUTTON ─────────────────────────────
        st.markdown("---")
        section_header("Generate Court-Ready Report", "Download a comprehensive PDF report for legal proceedings", "📄")

        col_ref, col_off, col_station = st.columns(3)
        with col_ref:
            case_ref = st.text_input("Case/FIR Number", value="GPCSSI-2026-001", key="case_ref_p1")
        with col_off:
            officer_name = st.text_input("Investigating Officer", value="", placeholder="Full name with rank", key="officer_p1")
        with col_station:
            station_name = st.text_input("Police Station/Unit", value="", placeholder="e.g., Cyber Crime Cell", key="station_p1")
        
        col_fir, col_court = st.columns(2)
        with col_fir:
            fir_number = st.text_input("FIR Number (if different)", value="", placeholder="Optional", key="fir_p1")
        with col_court:
            court_name = st.text_input("Court Name", value="", placeholder="e.g., District Court", key="court_p1")

        if st.button("📄 Generate Court-Ready PDF Report", key="pdf_btn_p1", use_container_width=True):
            with st.spinner("🖨️ Generating comprehensive legal PDF report..."):
                try:
                    analysis_state_for_pdf = {
                        "loaded": True,
                        "stats": stats,
                        "risk_scores": risk_scores,
                        "mitre_results": mitre_df,
                        "df": df,
                    }
                    pdf_bytes = generate_pdf(
                        stats=stats,
                        risk_scores=risk_scores,
                        mitre_results=mitre_df,
                        df=df,
                        case_ref=case_ref,
                        officer_name=officer_name,
                        station_name=station_name,
                        fir_number=fir_number or case_ref,
                        court_name=court_name,
                    )
                    st.download_button(
                        label="⬇️ Download PDF Report (Court Submission)",
                        data=pdf_bytes,
                        file_name=f"SURAAG_Report_{case_ref.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ Court-ready report generated successfully. Click above to download.")
                except Exception as e:
                    st.error(f"❌ Could not generate report: {e}")

        # ── CHATBOT ───────────────────────────────────────
        analysis_state = {
            "loaded":       True,
            "stats":        stats,
            "risk_scores":  risk_scores,
            "mitre_results":mitre_df,
            "df":           df,
        }
        render_chatbot(analysis_state, chat_key="chat_page1")


# ══════════════════════════════════════════════════════════
# PAGE 2: MULTI-IPDR CORRELATION
# ══════════════════════════════════════════════════════════

elif page == "🔗 Gang Correlation Analysis":

    # Page header with classification
    st.markdown(
        f"""<div style="background:linear-gradient(135deg, {COLOR_CRITICAL}22, {COLOR_HIGH}11);
        border-left:4px solid {COLOR_CRITICAL};padding:12px 20px;border-radius:8px;margin-bottom:20px">
        <p style="color:{COLOR_CRITICAL};font-size:11px;font-weight:700;margin:0;text-transform:uppercase;letter-spacing:1px">
        ⚠ CONFIDENTIAL — LAW ENFORCEMENT USE ONLY</p>
        <p style="color:{COLOR_MUTED};font-size:9px;margin:4px 0 0 0">
        IT Act 2000 Section 67C, 120B IPC (Criminal Conspiracy) | Indian Evidence Act 1872 Section 65B</p>
        </div>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        f"""<div style="border-bottom:2px solid {COLOR_ACCENT};padding-bottom:16px;margin-bottom:24px">
        <h1 style="color:{COLOR_TEXT};font-size:28px;font-weight:700;margin:0">
        🔗 Gang Correlation & Multi-Suspect Analysis</h1>
        <p style="color:{COLOR_MUTED};font-size:14px;margin:6px 0 0 0">
        Upload IPDR records from 2–6 different suspects to detect organized criminal gangs, shared infrastructure, 
        and coordinated cyber operations. Evidence suitable for IPC 120B (Criminal Conspiracy) charges.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    plain_english_box(
        "This tool looks for connections between multiple suspects' internet records. "
        "If two suspects visited the same secret server, or were active at the exact same time, "
        "this tool will find it — and score how likely they are to be working together as a gang.",
        icon="🕵️",
    )

    # ── MULTI-FILE UPLOAD ─────────────────────────────────
    uploaded_files = st.file_uploader(
        "Upload 2–6 IPDR CSV Files (one per suspect)",
        type=["csv"],
        accept_multiple_files=True,
        key="ipdr_upload_p2",
        help="Upload separate IPDR CSV files for each suspect. Files will be labeled Suspect A, B, C...",
    )

    if not uploaded_files or len(uploaded_files) < 2:
        empty_state(
            "Upload at least <b>2 IPDR CSV files</b> (one per suspect) to begin correlation analysis.<br><br>"
            "The tool will automatically detect shared servers, synchronized activity, and gang patterns.",
            icon="🔗",
        )
        if uploaded_files and len(uploaded_files) == 1:
            st.warning("⚠️ Please upload at least 2 files to run correlation analysis.")

    else:
        from modules.ipdr_analyzer import (
            load_and_validate, compute_summary_stats,
            format_bytes, format_indian,
        )
        from modules.risk_scorer import compute_risk_scores, get_risk_color
        from modules.correlation_engine import correlate_ipdrs
        from modules.traffic_patterns import build_subscriber_timeline
        from modules.network_graph import build_network_graph, render_graph
        from modules.chatbot import render_chatbot
        from modules.report_gen import generate_pdf

        if len(uploaded_files) > 6:
            st.warning("⚠️ Maximum 6 files supported. Only the first 6 will be analyzed.")
            uploaded_files = uploaded_files[:6]

        labels_alpha = list("ABCDEFGHIJ")
        labels = [f"Suspect {labels_alpha[i]}" for i in range(len(uploaded_files))]

        # Load all files
        dfs = []
        load_errors = []

        with st.spinner("📥 Loading all IPDR files..."):
            for i, uf in enumerate(uploaded_files):
                df_i, err = load_and_validate(uf.getvalue(), uf.name)
                if err:
                    load_errors.append(f"**{labels[i]}** ({uf.name}): {err}")
                else:
                    dfs.append(df_i)

        if load_errors:
            for e in load_errors:
                st.error(f"❌ {e}")
            st.stop()

        # Per-suspect summary cards
        st.markdown(f"<h3 style='color:{COLOR_ACCENT};font-size:16px;margin:16px 0 10px 0'>Suspect Summaries</h3>", unsafe_allow_html=True)

        suspect_cols = st.columns(len(dfs))
        for i, (df_i, label, uf) in enumerate(zip(dfs, labels, uploaded_files)):
            stats_i = compute_summary_stats(df_i)
            risk_i  = compute_risk_scores(df_i)
            risk_score_i = int(risk_i["Risk_Score"].max()) if not risk_i.empty else 0
            risk_c = get_risk_color(risk_score_i)
            name_i = df_i["Subscriber_Name"].iloc[0] if len(df_i) > 0 else "Unknown"

            with suspect_cols[i]:
                st.markdown(
                    f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                    border-top:3px solid {risk_c};border-radius:12px;padding:14px;text-align:center">
                    <p style="color:{COLOR_ACCENT};font-size:13px;font-weight:700;margin:0">{label}</p>
                    <p style="color:{COLOR_TEXT};font-size:14px;font-weight:600;margin:4px 0">{name_i}</p>
                    <p style="color:{COLOR_MUTED};font-size:11px;margin:0">{uf.name}</p>
                    <hr style="border-color:{COLOR_BORDER};margin:8px 0">
                    <p style="color:{COLOR_MUTED};font-size:11px;margin:2px 0">Sessions: 
                    <b style="color:{COLOR_TEXT}">{format_indian(stats_i['total_sessions'])}</b></p>
                    <p style="color:{COLOR_MUTED};font-size:11px;margin:2px 0">Risk Score: 
                    <b style="color:{risk_c}">{risk_score_i}/100</b></p>
                    <p style="color:{COLOR_MUTED};font-size:11px;margin:2px 0">Tor: 
                    <b style="color:{COLOR_CRITICAL}">{stats_i['tor_sessions']}</b></p>
                    </div>""",
                    unsafe_allow_html=True,
                )

        # ── RUN CORRELATION ───────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        with st.spinner("🔬 Running gang correlation analysis..."):
            try:
                result = correlate_ipdrs(tuple(dfs), tuple(labels))
                combined_df  = result["combined_df"]
                shared_ips   = result["shared_ips"]
                sync_windows = result["sync_windows"]
                shared_infra = result["shared_infra"]
                gang_score   = result["gang_score"]
                verdict      = result["verdict"]
                evidence     = result["evidence_points"]
            except Exception as e:
                st.error(f"❌ Correlation analysis failed: {e}")
                st.stop()

        # ── GANG DETECTION SCORE ──────────────────────────
        section_header("🎯 Gang Detection Verdict", "Overall assessment of whether these suspects are operating as an organized group")
        verdict_color = verdict["color"]
        st.markdown(
            f"""<div style="background:{verdict_color}11;border:2px solid {verdict_color}44;
            border-radius:16px;padding:24px;text-align:center;margin-bottom:16px">
            <p style="color:{COLOR_MUTED};font-size:13px;margin:0 0 4px 0">Gang Probability Score</p>
            <p style="color:{verdict_color};font-size:56px;font-weight:700;margin:0;line-height:1">{gang_score}%</p>
            <p style="color:{verdict_color};font-size:18px;font-weight:700;margin:8px 0 0 0">
            {verdict['emoji']} {verdict['label']}</p>
            <p style="color:{COLOR_TEXT};font-size:13px;margin:8px 0 0 0;max-width:500px;margin-left:auto;margin-right:auto">
            {verdict['description']}</p>
            </div>""",
            unsafe_allow_html=True,
        )

        # Evidence points
        st.markdown(f"<p style='color:{COLOR_MUTED};font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px 0'>Top Evidence Points</p>", unsafe_allow_html=True)
        for ev in evidence:
            st.markdown(
                f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                border-left:3px solid {verdict_color};border-radius:8px;
                padding:10px 14px;margin-bottom:6px;color:{COLOR_TEXT};font-size:13px">
                ▸ {ev}</div>""",
                unsafe_allow_html=True,
            )

        # ── SHARED IP DETECTION ───────────────────────────
        section_header("🔴 Shared IP Addresses", "IP addresses found in multiple suspect records — the strongest gang evidence")

        if shared_ips.empty:
            st.info("No shared IP addresses found across the uploaded files.")
        else:
            plain_english_box(
                f"{len(shared_ips)} IP address(es) were found in records from more than one suspect. "
                "This means multiple suspects contacted the same server — strong evidence of coordinated activity.",
                icon="🔗",
            )
            with st.expander(f"📋 View Shared IPs Table ({len(shared_ips)} IPs)", expanded=True):
                for _, row in shared_ips.iterrows():
                    count = row["Suspect_Count"]
                    rc = COLOR_CRITICAL if count == len(dfs) else (COLOR_HIGH if count >= 3 else "#FFD700")
                    st.markdown(
                        f"""<div style="display:flex;align-items:center;gap:16px;
                        background:{COLOR_CARD};border:1px solid {rc}44;
                        border-left:4px solid {rc};border-radius:8px;
                        padding:10px 14px;margin-bottom:6px">
                        <div style="flex:1.5">
                        <code style="color:{COLOR_ACCENT};font-size:14px">{row['IP_Address']}</code>
                        </div>
                        <div style="flex:2">
                        <span style="color:{COLOR_MUTED};font-size:11px">Found In</span><br>
                        <span style="color:{COLOR_TEXT};font-size:13px;font-weight:500">{row['Found_In_Suspects']}</span>
                        </div>
                        <div style="flex:0.8;text-align:center">
                        <span style="color:{COLOR_MUTED};font-size:11px">Sessions</span><br>
                        <span style="color:{COLOR_TEXT};font-size:14px;font-weight:600">{int(row.get('Total_Sessions',0)):,}</span>
                        </div>
                        <div style="flex:0.8;text-align:center">
                        <span style="color:{rc};background:{rc}22;border:1px solid {rc}44;
                        border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700">{row['Risk_Level']}</span>
                        </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        # ── TIME WINDOW OVERLAP ───────────────────────────
        section_header("⏱️ Synchronized Activity Windows", "Periods when multiple suspects were online at the exact same time")

        if sync_windows.empty:
            st.info("No synchronized time windows detected.")
        else:
            plain_english_box(
                f"{len(sync_windows)} time window(s) found where multiple suspects were active simultaneously. "
                "Synchronized online activity — especially at night — is a strong sign of coordinated criminal operation.",
                icon="⏱️",
            )

            with st.expander(f"📋 View Synchronized Windows ({len(sync_windows)} found)", expanded=False):
                st.dataframe(
                    sync_windows.rename(columns={
                        "Window_Start": "Time Window",
                        "Suspects_Active": "Suspects Online",
                        "Suspect_Count": "Count",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )

            with st.spinner("📈 Building combined timeline..."):
                try:
                    fig_combined = build_subscriber_timeline(combined_df)
                    st.plotly_chart(fig_combined, use_container_width=True)
                    plain_english_box(
                        "The chart above shows when each suspect was active during the day. "
                        "Peaks that overlap (same hour, different suspects) indicate coordinated activity.",
                        icon="📈",
                    )
                except Exception as e:
                    st.warning(f"⚠️ Timeline could not be rendered: {e}")

        # ── SHARED INFRASTRUCTURE ─────────────────────────
        section_header("🏗️ Shared Infrastructure", "Same servers, ports, and ISPs used by multiple suspects")

        infra_table = shared_infra.get("infra_table")
        if infra_table is not None and not infra_table.empty:
            with st.expander("📋 Shared Infrastructure Details", expanded=False):
                st.dataframe(infra_table, use_container_width=True, hide_index=True)
        else:
            st.info("No shared infrastructure detected.")

        # ── COMBINED NETWORK GRAPH ────────────────────────
        section_header("🕸️ Combined Network Graph", "All suspects and all servers in one view — shared servers appear as large white nodes")
        plain_english_box(
            "The large white squares are servers used by multiple suspects — they form the core link between gang members. "
            "Different colored circles represent different suspects. Thick lines = more data transferred.",
            icon="🕸️",
        )

        with st.spinner("🔄 Building combined network graph..."):
            try:
                shared_ip_set = set(shared_ips["IP_Address"].tolist()) if not shared_ips.empty else set()
                combined_html = build_network_graph(combined_df, shared_ips=shared_ip_set)
                render_graph(combined_html, height=650)
            except Exception as e:
                st.warning(f"⚠️ Combined network graph could not be rendered: {e}")

        # ── PDF REPORT (Page 2) ───────────────────────────
        st.markdown("---")
        section_header("📄 Generate Court-Ready Report", "Download a comprehensive PDF report covering all suspects")

        col_ref2, col_off2, col_station2 = st.columns(3)
        with col_ref2:
            case_ref2 = st.text_input("Case/FIR Number", value="GPCSSI-2026-001", key="case_ref_p2")
        with col_off2:
            officer_name2 = st.text_input("Investigating Officer", value="", placeholder="Full name with rank", key="officer_p2")
        with col_station2:
            station_name2 = st.text_input("Police Station/Unit", value="", placeholder="e.g., Cyber Crime Cell", key="station_p2")
        
        col_fir2, col_court2 = st.columns(2)
        with col_fir2:
            fir_number2 = st.text_input("FIR Number (if different)", value="", placeholder="Optional", key="fir_p2")
        with col_court2:
            court_name2 = st.text_input("Court Name", value="", placeholder="e.g., District Court", key="court_p2")

        if st.button("📄 Generate Gang Correlation PDF Report", key="pdf_btn_p2", use_container_width=True):
            with st.spinner("🖨️ Generating comprehensive gang analysis PDF report..."):
                try:
                    all_stats   = compute_summary_stats(combined_df)
                    all_risks   = compute_risk_scores(combined_df)
                    from modules.mitre_mapper import run_mitre_mapping
                    all_mitre   = run_mitre_mapping(combined_df)

                    pdf_bytes2 = generate_pdf(
                        stats=all_stats,
                        risk_scores=all_risks,
                        mitre_results=all_mitre,
                        df=combined_df,
                        correlation=result,
                        case_ref=case_ref2,
                        officer_name=officer_name2,
                        station_name=station_name2,
                        fir_number=fir_number2 or case_ref2,
                        court_name=court_name2,
                    )
                    st.download_button(
                        label="⬇️ Download Gang Correlation PDF Report",
                        data=pdf_bytes2,
                        file_name=f"SURAAG_Gang_Report_{case_ref2.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ Gang correlation report generated. Click above to download.")
                except Exception as e:
                    st.error(f"❌ Could not generate report: {e}")

        # ── CHATBOT ───────────────────────────────────────
        corr_analysis_state = {
            "loaded":      True,
            "stats":       compute_summary_stats(combined_df),
            "risk_scores": compute_risk_scores(combined_df),
            "df":          combined_df,
            "correlation": result,
        }
        render_chatbot(corr_analysis_state, chat_key="chat_page2")


# ══════════════════════════════════════════════════════════
# PAGE 3: WEB ANALYSIS TOOLS
# ══════════════════════════════════════════════════════════

elif page == "🌐 Web Analysis Tools":
    import os
    
    st.markdown(
        """
        <h1 style="
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 700;
            font-size: 1.875rem;
            color: #F0F6FC;
            margin: 0 0 1.5rem 0;
            line-height: 1.2;
        ">Web Analysis Tools</h1>
        """,
        unsafe_allow_html=True,
    )
    
    # Description
    st.markdown(
        """
        <div style="
            background: hsl(215, 48%, 10%);
            border: 1px solid hsl(215, 28%, 17%);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <p style="
                font-size: 1rem;
                color: hsl(215, 14%, 65%);
                margin: 0;
                line-height: 1.6;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            ">
                Access powerful browser-based analysis tools. No installation required - works directly in your browser with full offline support.
                All data processing happens locally on your machine for maximum security.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Tools Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, hsl(215, 48%, 10%), hsl(212, 33%, 13%));
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 1rem;
                padding: 2rem;
                height: 100%;
                transition: all 0.3s ease;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                <h3 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: hsl(210, 40%, 98%);
                    margin-bottom: 0.75rem;
                    font-family: 'Inter', sans-serif;
                ">CDR Analysis</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                ">
                    Call Detail Record analysis with network mapping and communication pattern detection.
                </p>
                <ul style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    list-style: none;
                    padding: 0;
                    margin-bottom: 1.5rem;
                ">
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Contact network visualization
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Communication patterns
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Timeline analysis
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        100% client-side
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        cdr_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "CDR_Analysis_Tool_v2.html")
        if os.path.exists(cdr_path):
            if st.button("🚀 Launch CDR Tool", key="cdr_launch", use_container_width=True):
                os.system(f'open "{cdr_path}"')
                st.success("✅ CDR Analysis Tool opened in your browser!")
        else:
            st.warning("⚠️ CDR tool not found. Please check installation.")
    
    with col2:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, hsl(215, 48%, 10%), hsl(212, 33%, 13%));
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 1rem;
                padding: 2rem;
                height: 100%;
                transition: all 0.3s ease;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🌐</div>
                <h3 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: hsl(210, 40%, 98%);
                    margin-bottom: 0.75rem;
                    font-family: 'Inter', sans-serif;
                ">IPDR Analysis</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                ">
                    Internet Protocol Detail Record analysis with geographic mapping.
                </p>
                <ul style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    list-style: none;
                    padding: 0;
                    margin-bottom: 1.5rem;
                ">
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Traffic pattern detection
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Geographic visualization
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        VPN/Proxy detection
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Social media tracking
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        ipdr_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "IPDR_Analysis_Tool_v5.html")
        if os.path.exists(ipdr_path):
            if st.button("🚀 Launch IPDR Tool", key="ipdr_launch", use_container_width=True):
                os.system(f'open "{ipdr_path}"')
                st.success("✅ IPDR Analysis Tool opened in your browser!")
        else:
            st.warning("⚠️ IPDR tool not found. Please check installation.")
    
    with col3:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, hsl(215, 48%, 10%), hsl(212, 33%, 13%));
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 1rem;
                padding: 2rem;
                height: 100%;
                transition: all 0.3s ease;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
                <h3 style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: hsl(210, 40%, 98%);
                    margin-bottom: 0.75rem;
                    font-family: 'Inter', sans-serif;
                ">All Tools</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-bottom: 1.5rem;
                ">
                    Access the complete toolkit with documentation and guides.
                </p>
                <ul style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    list-style: none;
                    padding: 0;
                    margin-bottom: 1.5rem;
                ">
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        CDR & IPDR tools
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Documentation
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Quick start guides
                    </li>
                    <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: hsl(158, 100%, 50%); font-weight: 700;">✓</span>
                        Sample data
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        index_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "index.html")
        if os.path.exists(index_path):
            if st.button("🌐 Open Full Portal", key="portal_launch", use_container_width=True):
                os.system(f'open "{index_path}"')
                st.success("✅ Full portal opened in your browser!")
        else:
            st.warning("⚠️ Portal not found. Please check installation.")
    
    # Features Section
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("✨ Key Features", "Advanced capabilities available in these tools")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown(
            """
            <div style="
                background: hsl(215, 48%, 10%);
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📊</div>
                <h4 style="color: hsl(210, 40%, 98%); margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;">
                    Data Analysis
                </h4>
                <p style="color: hsl(215, 14%, 65%); font-size: 0.875rem; line-height: 1.5;">
                    Comprehensive analysis with automated pattern detection and statistical insights.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with feat_col2:
        st.markdown(
            """
            <div style="
                background: hsl(215, 48%, 10%);
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🗺️</div>
                <h4 style="color: hsl(210, 40%, 98%); margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;">
                    Geographic Mapping
                </h4>
                <p style="color: hsl(215, 14%, 65%); font-size: 0.875rem; line-height: 1.5;">
                    Interactive maps showing connection locations and movement patterns.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with feat_col3:
        st.markdown(
            """
            <div style="
                background: hsl(215, 48%, 10%);
                border: 1px solid hsl(215, 28%, 17%);
                border-radius: 0.75rem;
                padding: 1.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🔒</div>
                <h4 style="color: hsl(210, 40%, 98%); margin-bottom: 0.5rem; font-family: 'Inter', sans-serif;">
                    Privacy First
                </h4>
                <p style="color: hsl(215, 14%, 65%); font-size: 0.875rem; line-height: 1.5;">
                    100% client-side processing - your data never leaves your machine.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Info Box
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("""
    ℹ️ **How to Use These Tools:**
    
    1. Click the launch button for your desired tool
    2. The tool will open in your default browser
    3. Upload your CSV files directly in the tool
    4. All analysis happens locally on your machine
    5. Export reports when analysis is complete
    
    **No internet connection required** - these tools work completely offline!
    """)
    
    # Documentation Links
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📖 Documentation & Support", "Learn more about using these tools")
    
    doc_col1, doc_col2, doc_col3 = st.columns(3)
    
    with doc_col1:
        readme_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "README.md")
        if os.path.exists(readme_path):
            if st.button("📄 Main Documentation", use_container_width=True):
                os.system(f'open "{readme_path}"')
    
    with doc_col2:
        quick_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "QUICK_START.md")
        if os.path.exists(quick_path):
            if st.button("🚀 Quick Start Guide", use_container_width=True):
                os.system(f'open "{quick_path}"')
    
    with doc_col3:
        ipdr_readme_path = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr", "IPDR_ANALYSIS_README.md")
        if os.path.exists(ipdr_readme_path):
            if st.button("📚 IPDR Guide", use_container_width=True):
                os.system(f'open "{ipdr_readme_path}"')
    
    # Folder Access
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("📁 Direct Access", "Open tools folder in Finder")
    
    cdr_folder = os.path.join(os.path.dirname(__file__), "cdr-and-ipdr")
    if os.path.exists(cdr_folder):
        if st.button("📂 Open Tools Folder", use_container_width=False):
            os.system(f'open "{cdr_folder}"')
            st.success(f"✅ Folder opened: {cdr_folder}")
    else:
        st.error("""
        ⚠️ **Tools folder not found!**
        
        Please make sure the `cdr-and-ipdr` folder is in the same directory as this application.
        
        Expected location: `{}`
        """.format(cdr_folder))
