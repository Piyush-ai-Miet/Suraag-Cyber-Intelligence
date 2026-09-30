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

    # Navigation Menu - 4 options
    query_params = st.query_params
    page_param = query_params.get("page", "multiple")
    
    is_multiple = "background: hsl(215, 28%, 17%); color: hsl(210, 40%, 98%);" if page_param == "multiple" else "background: transparent; color: hsl(215, 14%, 65%);"
    is_ipdr = "background: hsl(215, 28%, 17%); color: hsl(210, 40%, 98%);" if page_param == "ipdr" else "background: transparent; color: hsl(215, 14%, 65%);"
    is_cdr = "background: hsl(215, 28%, 17%); color: hsl(210, 40%, 98%);" if page_param == "cdr" else "background: transparent; color: hsl(215, 14%, 65%);"

    nav_html = f"""<div style="padding: 0.5rem;">
<div style="margin-bottom: 0.25rem;">
<a href="?page=multiple" target="_self" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 0.375rem; {is_multiple} text-decoration: none; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 500; font-size: 0.875rem; transition: all 0.2s ease;">
<span>📊</span>
<span>Multiple IPDR Connection</span>
</a>
</div>
<div style="margin-bottom: 0.25rem;">
<a href="?page=ipdr" target="_blank" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 0.375rem; {is_ipdr} text-decoration: none; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 500; font-size: 0.875rem; transition: all 0.2s ease;">
<span>🌐</span>
<span>IPDR Analysis Tool</span>
</a>
</div>
<div style="margin-bottom: 0.25rem;">
<a href="?page=cdr" target="_blank" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 0.375rem; {is_cdr} text-decoration: none; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 500; font-size: 0.875rem; transition: all 0.2s ease;">
<span>📱</span>
<span>CDR Analysis Tool</span>
</a>
</div>
</div>"""
    
    st.markdown(nav_html, unsafe_allow_html=True)

    # Map query param to page name
    page_map = {
        "multiple": "📊 Multiple IPDR Connection",
        "ipdr": "🌐 IPDR Analysis Tool",
        "cdr": "📱 CDR Analysis Tool"
    }
    page = page_map.get(page_param, "📊 Multiple IPDR Connection")

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
    
    # Set default API key globally behind the scenes
    DEFAULT_API_KEY = "AQ.Ab8RN6Jz62xrnUISZ02gKoSlnJXWhvAJnO-5e1iLoz3-yQCP2Q"
    if "gemini_api_key" not in st.session_state or not st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = DEFAULT_API_KEY

    # Professional Developer Credits
    credits_html = """
    <div style="
        text-align: center;
        padding: 14px 12px;
        margin: 8px 4px;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(22, 27, 34, 0.6) 100%);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        font-family: 'Inter', sans-serif;
    ">
        <p style="
            font-size: 0.65rem;
            color: #8B949E;
            margin: 0 0 6px 0;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
        ">
            DEVELOPED BY
        </p>
        <p style="
            font-size: 0.85rem;
            background: linear-gradient(90deg, #00D4FF 0%, #0077FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            font-weight: 800;
            letter-spacing: 0.5px;
        ">
            Piyush & Kush
        </p>
    </div>
    """
    st.markdown(credits_html, unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
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
# PAGE 1: MULTIPLE IPDR CONNECTION
# ══════════════════════════════════════════════════════════

if page == "📊 Multiple IPDR Connection":

    # Law Enforcement Notice
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 127, 0.08));
            border: 2px solid #EF4444;
            border-left: 4px solid #EF4444;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span style="font-size: 1.25rem;">⚠️</span>
                <p style="
                    color: #EF4444;
                    font-size: 0.75rem;
                    font-weight: 700;
                    margin: 0;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">RESTRICTED ACCESS — LAW ENFORCEMENT ONLY</p>
            </div>
            <p style="
                color: hsl(215, 14%, 75%);
                font-size: 0.6875rem;
                margin: 0;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            ">Authorized personnel only. Unauthorized access is prohibited and punishable under IT Act 2000.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dashboard Header
    st.markdown(
        """
        <h1 style="
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 700;
            font-size: 1.875rem;
            color: #F0F6FC;
            margin: 0 0 0.5rem 0;
            line-height: 1.2;
        ">Multiple IPDR Connection Analysis</h1>
        <p style="
            font-size: 0.875rem;
            color: hsl(215, 14%, 65%);
            margin: 0 0 1.5rem 0;
            line-height: 1.5;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        ">Analyze and correlate multiple IPDR records simultaneously to detect coordinated criminal activity, shared infrastructure, and network patterns across suspects.</p>
        """,
        unsafe_allow_html=True,
    )
    
    # New Analysis Card
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
                ">Upload IPDR Files</h2>
                <p style="
                    font-size: 0.875rem;
                    color: hsl(215, 14%, 65%);
                    margin: 0;
                    line-height: 1.5;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Upload multiple IPDR CSV files to begin comprehensive analysis. All files will be automatically combined and analyzed for connections, patterns, and suspicious activities.</p>
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
    
    # Combine multiple files into one dataframe with proper suspect labeling
    uploaded_file = None
    suspect_files = []  # Store individual labeled dataframes
    suspect_labels = []  # Store suspect names
    
    # Clear previous multi-file session state when new files are uploaded
    if uploaded_files:
        if 'is_multi_file' in st.session_state:
            del st.session_state['is_multi_file']
        if 'multi_file_df' in st.session_state:
            del st.session_state['multi_file_df']
    
    if uploaded_files:
        if len(uploaded_files) == 1:
            # Single file - normal flow
            uploaded_file = uploaded_files[0]
        else:
            # Multiple files - PROPER GANG ANALYSIS with suspect labels
            st.markdown(
                f"""<div style="background: hsl(158, 100%, 50%, 0.1); border: 1px solid hsl(158, 100%, 50%, 0.3); 
                border-radius: 0.375rem; padding: 0.75rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg width="20" height="20" fill="none" stroke="hsl(158, 100%, 50%)" viewBox="0 0 24 24" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span style="color: hsl(158, 100%, 50%); font-size: 0.875rem; font-weight: 600; font-family: 'Inter', sans-serif;">
                {len(uploaded_files)} files uploaded - Preparing gang analysis...</span>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Process each file with suspect labeling
            from modules.ipdr_analyzer import load_and_validate, add_uppercase_aliases
            
            for idx, file in enumerate(uploaded_files):
                try:
                    # Load and validate each file
                    df_raw, error = load_and_validate(file.getvalue(), file.name)
                    
                    if error:
                        st.error(f"❌ {file.name}: {error}")
                        continue
                    
                    # Add uppercase aliases to individual file
                    # This is needed because suspect_files list is used later in Multiple IPDR section
                    df_raw = add_uppercase_aliases(df_raw)
                    
                    # Assign suspect label based on file name or auto-generate
                    if len(uploaded_files) <= 26:
                        suspect_label = f"Suspect_{chr(65+idx)}"  # A, B, C...
                    else:
                        suspect_label = f"Suspect_{idx+1}"
                    
                    # Clean filename for display
                    display_name = file.name.replace('.csv', '')[:30]
                    
                    # Add suspect label column
                    df_raw["_suspect_label"] = suspect_label
                    df_raw["_file_name"] = display_name
                    
                    suspect_files.append(df_raw)
                    suspect_labels.append(suspect_label)
                    
                    st.markdown(
                        f"""<div style="color: hsl(215, 14%, 65%); font-size: 0.75rem; padding: 0.25rem 0; 
                        font-family: 'Inter', sans-serif;">✓ {display_name} → {suspect_label} ({len(df_raw)} rows)</div>""",
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Error reading {file.name}: {str(e)}")
            
            if not suspect_files:
                st.error("No valid files could be processed.")
                st.stop()
            
            # Store for correlation analysis
            if 'suspect_files_tuple' not in st.session_state:
                st.session_state.suspect_files_tuple = tuple(suspect_files)
                st.session_state.suspect_labels_tuple = tuple(suspect_labels)
            else:
                st.session_state.suspect_files_tuple = tuple(suspect_files)
                st.session_state.suspect_labels_tuple = tuple(suspect_labels)
            
            # Create combined dataframe for display
            # Note: Each suspect_file already has uppercase aliases, so concat will merge them properly
            combined_df = pd.concat(suspect_files, ignore_index=True)
            
            # No need to call add_uppercase_aliases here since each file already has them
            # This avoids potential duplicate column issues during concat
            
            st.markdown(
                f"""<div style="background: hsl(215, 48%, 10%); border: 1px solid hsl(158, 100%, 50%, 0.3); 
                border-radius: 0.375rem; padding: 0.75rem; margin-top: 0.5rem;">
                <span style="color: hsl(158, 100%, 50%); font-size: 0.875rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                ✅ Ready for Gang Analysis: {len(suspect_files)} suspects, {len(combined_df)} total records</span>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Store the combined dataframe directly instead of wrapping in DummyFile
            # This avoids re-parsing through load_and_validate which could cause duplicate column errors
            st.session_state['multi_file_df'] = combined_df
            st.session_state['is_multi_file'] = True
            
            # Create a dummy uploaded_file object for compatibility with downstream code
            class DummyFile:
                def __init__(self, name):
                    self.name = name
            
            uploaded_file = DummyFile(f"Combined_{len(uploaded_files)}_suspects.csv")
    
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
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                    </svg>
                </div>
                <h3 style="
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin: 0 0 0.5rem 0;
                    color: hsl(210, 40%, 98%);
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">3. Smart Insights</h3>
                <p style="
                    color: hsl(215, 14%, 65%);
                    font-size: 0.875rem;
                    line-height: 1.5;
                    margin: 0;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                ">Query the Gemini-powered chatbot for forensic summaries and export PDF reports.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        from modules.ipdr_analyzer import (
            load_and_validate, compute_summary_stats,
            get_suspect_profiles, format_bytes, format_indian,
        )
        from modules.correlation_engine import correlate_ipdrs
        from modules.ai_multi_ipdr_analyzer import analyze_connections_with_ai, identify_unique_subscribers
        from modules.mitre_mapper import run_mitre_mapping, get_risk_color as mitre_risk_color, get_mitre_summary_text
        from modules.risk_scorer import compute_risk_scores, get_risk_color, get_overall_risk_score
        from modules.traffic_patterns import build_subscriber_timeline
        from modules.geo_mapper import build_geo_map
        from modules.network_graph import build_network_graph, render_graph
        from modules.chatbot import render_chatbot
        from modules.report_gen import generate_pdf

        # Load and validate
        with st.spinner("📥 Loading and validating IPDR data..."):
            # Check if this is a multi-file upload (dataframe already prepared)
            if st.session_state.get('is_multi_file', False) and 'multi_file_df' in st.session_state:
                df = st.session_state['multi_file_df']
                error = ""
            else:
                # Single file - load and validate normally
                df, error = load_and_validate(uploaded_file.getvalue(), uploaded_file.name)
                # Add uppercase aliases for single file
                if not error:
                    from modules.ipdr_analyzer import add_uppercase_aliases
                    df = add_uppercase_aliases(df)

        if error:
            st.error(f"❌ **File Error:** {error}")
            st.stop()
        
        # Store original dataframe
        df_original = df.copy()

        # ── ADVANCED SEARCH/FILTER SECTION ────────────────────
        section_header(
            "🔍 Advanced Search & Filters",
            "Filter IPDR data by Source/Destination IP, Protocol, Service Type, Destination Port, Bytes Transferred, and Date Range",
            "🔎"
        )
        
        with st.expander("🔎 Search & Filter Options", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**🌐 Source IP Address**")
                source_ip_search = st.text_input(
                    "Enter Source IP",
                    placeholder="e.g., 192.168.1.10",
                    key="source_ip_search",
                    label_visibility="collapsed"
                )
                
                st.markdown("**🌐 Destination IP Address**")
                dest_ip_search = st.text_input(
                    "Enter Destination IP",
                    placeholder="e.g., 8.8.8.8",
                    key="dest_ip_search",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**🔗 Protocol Filter**")
                protocol_options = ['All', 'TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']
                protocol_filter = st.selectbox(
                    "Select Protocol",
                    protocol_options,
                    key="protocol_filter",
                    label_visibility="collapsed"
                )
                
                st.markdown("**⚙️ Service Type Filter**")
                service_options = ['All', 'Web Browsing', 'HTTPS', 'VoIP', 'Email', 'FTP', 'SSH', 'DNS', 'Network Monitoring']
                service_filter = st.selectbox(
                    "Select Service",
                    service_options,
                    key="service_filter",
                    label_visibility="collapsed"
                )
            
            with col3:
                st.markdown("**🔌 Destination Port Filter (Multi-Select)**")
                unique_ports = sorted(df['Destination_Port'].dropna().unique().tolist())
                unique_ports = [int(p) for p in unique_ports]
                port_filter = st.multiselect(
                    "Select Ports",
                    unique_ports,
                    key="port_filter",
                    label_visibility="collapsed",
                    placeholder="All Ports"
                )
                
                st.markdown("**📊 Bytes Transferred Filter**")
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
        
        if apply_filters or source_ip_search or dest_ip_search:
            df_filtered = df_original.copy()
            
            # Source IP filter
            if source_ip_search and source_ip_search.strip():
                df_filtered = df_filtered[df_filtered['Source_IP'].str.contains(source_ip_search.strip(), na=False)]
            
            # Destination IP filter
            if dest_ip_search and dest_ip_search.strip():
                df_filtered = df_filtered[df_filtered['Destination_IP'].str.contains(dest_ip_search.strip(), na=False)]
            
            # Protocol Filter
            if protocol_filter != 'All':
                df_filtered = df_filtered[df_filtered['App_Protocol'].str.upper() == protocol_filter.upper()]
            
            # Service Type Filter
            if service_filter != 'All':
                service_map = {
                    'Web Browsing': ['HTTP', 'HTTPS'],
                    'HTTPS': ['HTTPS'],
                    'VoIP': ['SIP', 'RTP'],
                    'Email': ['SMTP', 'IMAP', 'POP3'],
                    'FTP': ['FTP'],
                    'SSH': ['SSH'],
                    'DNS': ['DNS'],
                    'Network Monitoring': ['SNMP', 'ICMP']
                }
                if service_filter in service_map:
                    df_filtered = df_filtered[df_filtered['App_Protocol'].str.upper().isin([p.upper() for p in service_map[service_filter]])]
            
            # Port filter (Destination Port)
            if port_filter:
                df_filtered = df_filtered[df_filtered['Destination_Port'].isin(port_filter)]
            
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
                    subscriber_id = suspect_df['Subscriber_ID'].iloc[0] if 'Subscriber_ID' in suspect_df.columns else "N/A"
                    
                    with st.expander(f"👤 **{suspect_name}** | 🆔 {subscriber_id} | {len(suspect_df)} Sessions", expanded=False):
                        
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
                        # Generate factors string
                        risk_factors_str = ('<br/>• ' + '<br/>• '.join(risk_factors)) if risk_factors else '✓ No significant risk factors'
                        risk_bg = f"linear-gradient(135deg, {risk_color}22, {risk_color}11)"
                        
                        risk_html = f"""
                        <div style="background: {risk_bg}; 
                        border-left: 4px solid {risk_color}; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: {risk_color}; font-size: 1rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                            {risk_level} | Risk Score: {risk_score}
                            </span>
                        </div>
                        <div style="color: hsl(215, 14%, 65%); font-size: 0.75rem; font-family: 'Inter', sans-serif; line-height: 1.8;">
                        <strong style="color: hsl(210, 40%, 98%);">Detected Risk Factors:</strong><br/>
                        {risk_factors_str}
                        </div>
                        </div>
                        """
                        st.markdown(risk_html, unsafe_allow_html=True)
                        
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
            
            # OVERRIDE suspect count for single file case
            # 1 File = 1 Suspect (regardless of Subscriber_Name in data)
            if len(suspect_files) < 2:
                stats['unique_subscribers'] = 1
            else:
                # Multiple files - count based on number of files uploaded
                stats['unique_subscribers'] = len(suspect_files)
            
            mitre_df    = run_mitre_mapping(df)
            
            # For single file, treat entire dataset as ONE suspect
            if len(suspect_files) >= 2:
                # Multiple files - compute per Subscriber_Name
                risk_scores = compute_risk_scores(df)
                profiles    = get_suspect_profiles(df)
            else:
                # Single file - treat all as ONE suspect
                # Temporarily set all Subscriber_Name to file name for risk calculation
                df_temp = df.copy()
                df_temp['Subscriber_Name'] = uploaded_file.name.replace('.csv', '')
                df_temp['Subscriber_ID'] = 'SINGLE_SUBJECT'
                risk_scores = compute_risk_scores(df_temp)
                profiles    = get_suspect_profiles(df_temp)
            
            overall_risk = get_overall_risk_score(risk_scores)
            
            # Detect investigation mode based on NUMBER OF FILES, not subscribers in file
            if len(suspect_files) >= 2:
                # Multiple files uploaded - Multi-Subject Investigation
                investigation_info = {
                    "mode": "MULTI_SUBJECT",
                    "description": "Multi Subject Correlation",
                    "unique_count": len(suspect_files),
                    "identifier_type": "Files Uploaded",
                    "subscriber_list": suspect_labels,
                    "focus_areas": [
                        "Common Destinations",
                        "Shared Infrastructure",
                        "Coordinated Activity",
                        "Network Clusters",
                        "Temporal Correlation",
                        "Central Nodes",
                        "Hidden Relationships"
                    ]
                }
            else:
                # Single file - Single Subject Investigation
                investigation_info = {
                    "mode": "SINGLE_SUBJECT",
                    "description": "Single Subject Investigation",
                    "unique_count": 1,
                    "identifier_type": "File",
                    "subscriber_list": [uploaded_file.name],
                    "focus_areas": [
                        "Timeline Analysis",
                        "Destination Patterns",
                        "VPN/TOR Usage",
                        "Suspicious Infrastructure",
                        "Behavioral Anomalies"
                    ]
                }
            
            # Note: Gang analysis will run in the display section below
            # using the new multi_ipdr_analyzer module
            
            overall_risk = get_overall_risk_score(risk_scores)
        
        st.success(f"✅ Analysis complete — {format_indian(stats['total_sessions'])} sessions | **{investigation_info['description']}** ({investigation_info['unique_count']} entities)")
        
        # === INVESTIGATION MODE BANNER ===
        mode_color = "#FF8C00" if investigation_info['mode'] == "MULTI_SUBJECT" else "#3FB950"
        mode_icon = "👥" if investigation_info['mode'] == "MULTI_SUBJECT" else "👤"
        
        st.markdown(
            f"""<div style="background: linear-gradient(135deg, {mode_color}22, {mode_color}11); 
            border-left: 4px solid {mode_color}; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">{mode_icon}</span>
                <span style="color: {mode_color}; font-size: 1rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                {investigation_info['description'].upper()}</span>
            </div>
            <div style="color: hsl(215, 14%, 65%); font-size: 0.75rem; font-family: 'Inter', sans-serif;">
                <strong>Entities Detected:</strong> {investigation_info['unique_count']} ({investigation_info['identifier_type']})<br>
                <strong>Focus Areas:</strong> {', '.join(investigation_info['focus_areas'][:5])}
            </div>
            </div>""",
            unsafe_allow_html=True
        )

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

        # Enhanced Quick Stats Card (matching IPDR HTML tool logic)
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, {COLOR_CARD}, #0A0E12);
            border:1px solid {COLOR_BORDER};border-radius:12px;padding:20px 24px;
            box-shadow:0 4px 16px {COLOR_BG}cc">
            <p style="color:{COLOR_ACCENT};font-size:11px;font-weight:700;margin:0 0 12px 0;
            text-transform:uppercase;letter-spacing:1px">📈 Quick Statistics</p>
            <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:16px">
                <div style="text-align:center">
                    <p style="color:{COLOR_ACCENT};font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['total_sessions'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">📊 Total Sessions</p>
                </div>
                <div style="text-align:center">
                    <p style="color:#FF8C00;font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['unique_ips'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">🌐 Unique IPs</p>
                </div>
                <div style="text-align:center">
                    <p style="color:{COLOR_CRITICAL};font-size:24px;font-weight:700;margin:0">
                    {format_indian(stats['tor_sessions'])}</p>
                    <p style="color:{COLOR_MUTED};font-size:10px;margin:4px 0 0 0">🔴 Tor Sessions</p>
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
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # ══════════════════════════════════════════════════════════
        # MULTIPLE IPDR CONNECTION ANALYSIS (Only for 2+ files)
        # ══════════════════════════════════════════════════════════
        if len(suspect_files) >= 2:
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            
            section_header(
                "🔗 Multiple IPDR Connection Analysis",
                f"Analyzing {len(suspect_files)} suspects to detect shared connections and coordinated activity",
                "👥"
            )
            
            plain_english_box(
                f"📁 <b>{len(suspect_files)} IPDR files uploaded.</b> Each file represents ONE suspect's internet activity. "
                "The system will check if these suspects contacted the <b>same destination IPs</b> - "
                "this is PRIMARY evidence of gang connection or coordinated criminal activity.",
                icon="ℹ️"
            )
            
            # === PER-SUSPECT SUMMARY ===
            st.markdown("### 👥 Suspect Overview")
            
            cols = st.columns(min(len(suspect_files), 4))
            for idx, label in enumerate(suspect_labels):
                suspect_df = suspect_files[idx]
                file_name = suspect_df['_file_name'].iloc[0] if '_file_name' in suspect_df.columns else label
                
                with cols[idx % 4]:
                    total_sessions = len(suspect_df)
                    unique_ips = suspect_df['Destination_IP'].nunique()
                    tor_count = int(suspect_df['Is_TOR'].sum()) if 'Is_TOR' in suspect_df.columns else 0
                    
                    st.markdown(
                        f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                        border-radius:8px;padding:16px;text-align:center">
                        <p style="color:{COLOR_ACCENT};font-size:16px;font-weight:700;margin:0 0 8px 0">{label}</p>
                        <p style="color:{COLOR_MUTED};font-size:10px;margin:0">{file_name}</p>
                        <hr style="margin:8px 0;opacity:0.3">
                        <p style="color:{COLOR_TEXT};font-size:24px;font-weight:700;margin:4px 0">{format_indian(total_sessions)}</p>
                        <p style="color:{COLOR_MUTED};font-size:10px;margin:0">Sessions</p>
                        <p style="color:{COLOR_TEXT};font-size:18px;font-weight:600;margin:8px 0">{format_indian(unique_ips)}</p>
                        <p style="color:{COLOR_MUTED};font-size:10px;margin:0">Unique IPs</p>
                        {f'<p style="color:{COLOR_CRITICAL};font-size:14px;font-weight:600;margin:8px 0">🔴 {tor_count} Tor</p>' if tor_count > 0 else ''}
                        </div>""",
                        unsafe_allow_html=True
                    )
            
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            
            # === SHARED IPs ANALYSIS (PRIMARY EVIDENCE) ===
            st.markdown("### 🌐 Shared Destination IPs - PRIMARY EVIDENCE")
            
            # Find shared IPs
            suspect_ip_map = {}
            for idx, label in enumerate(suspect_labels):
                suspect_df = suspect_files[idx]
                if 'Destination_IP' in suspect_df.columns:
                    suspect_ip_map[label] = set(suspect_df['Destination_IP'].dropna().unique())
            
            # Find IPs contacted by 2+ suspects
            all_ips = set()
            for ips in suspect_ip_map.values():
                all_ips.update(ips)
            
            shared_ip_data = []
            for ip in all_ips:
                suspects_with_ip = [label for label, ips in suspect_ip_map.items() if ip in ips]
                if len(suspects_with_ip) >= 2:
                    # Get details
                    total_sessions = 0
                    is_tor = False
                    is_foreign = False
                    
                    for idx, label in enumerate(suspect_labels):
                        if label in suspects_with_ip:
                            suspect_df = suspect_files[idx]
                            ip_sessions = suspect_df[suspect_df['Destination_IP'] == ip]
                            total_sessions += len(ip_sessions)
                            if 'Is_TOR' in suspect_df.columns:
                                is_tor = is_tor or ip_sessions['Is_TOR'].any()
                            if 'Is_Foreign_IP' in suspect_df.columns:
                                is_foreign = is_foreign or ip_sessions['Is_Foreign_IP'].any()
                    
                    shared_ip_data.append({
                        'IP Address': ip,
                        'Contacted By': ', '.join(suspects_with_ip),
                        '# Suspects': len(suspects_with_ip),
                        'Total Sessions': total_sessions,
                        'Type': '🔴 TOR' if is_tor else ('🌍 FOREIGN' if is_foreign else '🔵 NORMAL')
                    })
            
            if shared_ip_data:
                shared_df = pd.DataFrame(shared_ip_data).sort_values('# Suspects', ascending=False)
                
                # Connection verdict
                critical_count = len([x for x in shared_ip_data if x['Type'] == '🔴 TOR'])
                
                if len(shared_ip_data) >= 10 or critical_count >= 3:
                    verdict = "🔴 STRONG CONNECTION DETECTED"
                    verdict_color = COLOR_CRITICAL
                    verdict_msg = f"Suspects shared {len(shared_ip_data)} destination IPs. This indicates organized criminal activity."
                elif len(shared_ip_data) >= 5:
                    verdict = "🟠 PROBABLE CONNECTION"
                    verdict_color = COLOR_HIGH
                    verdict_msg = f"Suspects shared {len(shared_ip_data)} IPs. Significant evidence of coordination."
                elif len(shared_ip_data) >= 2:
                    verdict = "🟡 POSSIBLE CONNECTION"
                    verdict_color = "#FFD700"
                    verdict_msg = f"Suspects shared {len(shared_ip_data)} IPs. Minor overlaps detected."
                else:
                    verdict = "🟢 WEAK CONNECTION"
                    verdict_color = "#3FB950"
                    verdict_msg = f"Only {len(shared_ip_data)} shared IP. May be coincidental."
                
                st.markdown(
                    f"""<div style="background:{verdict_color}11;border-left:4px solid {verdict_color};
                    border-radius:8px;padding:16px;margin:16px 0">
                    <p style="color:{verdict_color};font-size:18px;font-weight:800;margin:0 0 8px 0">
                    {verdict}</p>
                    <p style="color:{COLOR_TEXT};font-size:13px;margin:0">{verdict_msg}</p>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                st.dataframe(
                    shared_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                if critical_count > 0:
                    st.error(f"⚠️ {critical_count} shared IPs are Tor/Proxy nodes - CRITICAL evidence of anonymization!")
                
            else:
                st.success("✅ No shared destination IPs found. Suspects appear to be independent.")
            
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════
        # GO STRAIGHT TO MITRE - Skip all single subject sections
        # ══════════════════════════════════════════════════════════

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

        # Initialize session state for map loading
        if "geo_map_loaded" not in st.session_state:
            st.session_state["geo_map_loaded"] = False

        # Show button to load map
        if not st.session_state["geo_map_loaded"]:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("🗺️ Generate Geolocation Map", width="stretch", type="primary"):
                    st.session_state["geo_map_loaded"] = True
                    st.rerun()
        
        # Load map only after button is clicked
        if st.session_state["geo_map_loaded"]:
            with st.spinner("📍 Geolocating IP addresses..."):
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
                    
                    # Success message after map is rendered
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        st.markdown(
                            f"""<div style="background:linear-gradient(135deg, rgba(0, 255, 148, 0.1), rgba(0, 212, 255, 0.05));
                            border:1px solid {COLOR_ACCENT}44;border-radius:12px;padding:16px;text-align:center;
                            animation:fadeInUp 0.8s ease-out both;box-shadow:0 4px 20px rgba(0,255,148,0.15)">
                            <p style="color:{COLOR_ACCENT};font-size:14px;font-weight:700;margin:0;
                            display:flex;align-items:center;justify-content:center;gap:8px">
                            <span>✅</span> <span>Geolocation Map Successfully Generated</span>
                            </p>
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:8px 0 0 0">
                            All IP addresses have been geolocated and visualized on the interactive map above
                            </p>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                            
                except Exception as e:
                    st.warning(f"⚠️ Map could not be rendered: {e}. Check your internet connection for IP geolocation.")

        # ── CONNECTION DATA SUMMARY ───────────────────────
        section_header(
            "Connection Analysis",
            "Detailed breakdown of connections - who connected where, when, and how much data transferred",
            "📊"
        )
        
        # Check if single or multi subject
        if len(suspect_files) < 2:
            # SINGLE SUBJECT - Show comprehensive connection view
            plain_english_box(
                f"📍 Analyzing {format_indian(len(df))} total connections from <b>{uploaded_file.name.replace('.csv', '')}</b>. "
                f"Contacted {df['Destination_IP'].nunique()} unique servers across "
                f"{pd.to_datetime(df['Timestamp']).dt.date.nunique()} days.",
                icon="📈"
            )
            
            # Top Destination IPs
            st.markdown("**🎯 Top 10 Most Contacted Servers**")
            top_dests = df.groupby('Destination_IP').agg({
                'Timestamp': 'count',
                'Data_Volume_Bytes': 'sum',
                'Is_TOR': 'any',
                'Is_Foreign_IP': 'any',
                'Destination_Port': lambda x: ', '.join(map(str, sorted(set(x))[:3]))
            }).reset_index()
            top_dests.columns = ['IP Address', 'Sessions', 'Data Volume', 'Is Tor', 'Is Foreign', 'Ports']
            top_dests = top_dests.sort_values('Sessions', ascending=False).head(10)
            
            # Add flags
            top_dests['Status'] = top_dests.apply(
                lambda x: "🔴 TOR" if x['Is Tor'] else ("🌍 FOREIGN" if x['Is Foreign'] else "🔵 DOMESTIC"),
                axis=1
            )
            top_dests['Data (MB)'] = (top_dests['Data Volume'] / 1_048_576).round(2)
            
            st.dataframe(
                top_dests[['IP Address', 'Sessions', 'Data (MB)', 'Ports', 'Status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Connection distribution by protocol
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📡 Protocol Distribution**")
                proto_dist = df['App_Protocol'].value_counts().head(8)
                st.bar_chart(proto_dist, height=220)
            
            with col2:
                st.markdown("**🌍 Geographic Distribution**")
                geo_dist = df.groupby('Is_Foreign_IP').size()
                geo_labels = {True: 'Foreign', False: 'Domestic'}
                geo_data = pd.DataFrame({
                    'Type': [geo_labels.get(k, 'Unknown') for k in geo_dist.index],
                    'Count': geo_dist.values
                })
                st.bar_chart(geo_data.set_index('Type'), height=220)
        
        else:
            # MULTI SUBJECT - Show per-suspect breakdown
            plain_english_box(
                f"📍 Analyzing {len(suspect_files)} suspects with {format_indian(len(df))} total connections. "
                f"Comparing activity patterns across all subjects.",
                icon="👥"
            )
            
            # Build connection summary per suspect
            connection_summary = []
            for label in suspect_labels:
                sub_df = df[df["_suspect_label"] == label]
                if len(sub_df) == 0:
                    continue
                
                file_name = sub_df["_file_name"].iloc[0] if "_file_name" in sub_df.columns else label
                
                # Get stats
                dest_ips = sub_df["Destination_IP"].nunique()
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
                    "label": label,
                    "file_name": file_name,
                    "total_ips": dest_ips,
                    "total_sessions": total_sessions,
                    "total_data_mb": total_data_mb,
                    "tor_count": tor_count,
                    "foreign_count": foreign_count,
                    "top_destinations": top_dests
                })
            
            # Display connection cards
            for idx, conn in enumerate(connection_summary):
                with st.expander(
                    f"{'🔴' if conn['tor_count'] > 5 else '🟠' if conn['foreign_count'] > 10 else '🔵'} "
                    f"{conn['label']} - {conn['file_name']} ({format_indian(conn['total_sessions'])} sessions)",
                    expanded=(idx==0)
                ):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🌐 Unique IPs", format_indian(conn['total_ips']))
                    with col2:
                        st.metric("📦 Total Data", f"{conn['total_data_mb']:.1f} MB")
                    with col3:
                        tor_pct = (conn['tor_count']/conn['total_sessions']*100) if conn['total_sessions'] > 0 else 0
                        st.metric("🔴 Tor", format_indian(conn['tor_count']), 
                                 delta=f"{tor_pct:.1f}%" if conn['tor_count'] > 0 else None)
                    with col4:
                        foreign_pct = (conn['foreign_count']/conn['total_sessions']*100) if conn['total_sessions'] > 0 else 0
                        st.metric("🌍 Foreign", format_indian(conn['foreign_count']), 
                                 delta=f"{foreign_pct:.1f}%" if conn['foreign_count'] > 0 else None)
                    
                    st.markdown("**🎯 Top 5 Connected Servers:**")
                    
                    top_dest_data = []
                    for ip, row in conn['top_destinations'].iterrows():
                        sessions = int(row['Timestamp'])
                        data_mb = row['Data_Volume_Bytes'] / 1_048_576
                        
                        # Check flags
                        ip_df = df[(df["_suspect_label"] == conn['label']) & (df["Destination_IP"] == ip)]
                        is_tor = ip_df["Is_TOR"].any() if len(ip_df) > 0 else False
                        is_foreign = ip_df["Is_Foreign_IP"].any() if len(ip_df) > 0 else False
                        
                        flag = "🔴 TOR" if is_tor else ("🌍 FOREIGN" if is_foreign else "🔵 DOMESTIC")
                        
                        top_dest_data.append({
                            "IP Address": str(ip),
                            "Type": flag,
                            "Sessions": format_indian(sessions),
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
                    'Subscriber_ID': row.get('Subscriber_ID', 'N/A'),
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
                # For multi-subject, pass shared IPs to highlight gang connections
                shared_ip_set = set()
                if len(suspect_files) >= 2:
                    # Get shared IPs from multi-IPDR analysis results if available
                    if 'gang_results' in locals():
                        shared_ips_df = gang_results.get('shared_ips', pd.DataFrame())
                        if not shared_ips_df.empty:
                            shared_ip_set = set(shared_ips_df['Destination_IP'].tolist())
                
                graph_html = build_network_graph(df, shared_ips=shared_ip_set)
                render_graph(graph_html, height=660)
            except Exception as e:
                st.warning(f"⚠️ Network graph could not be rendered: {e}")

        # ── PDF REPORT GENERATION ─────────────────────────────
        st.markdown("---")
        
        # Professional Report Header
        st.markdown(
            f"""<div style="background:linear-gradient(135deg,{COLOR_CARD},{COLOR_BG});
            border:2px solid {COLOR_ACCENT};border-radius:12px;padding:24px;margin-bottom:24px;
            box-shadow:0 8px 32px rgba(0,0,0,0.3)">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="font-size:32px">📋</div>
            <div>
            <h2 style="color:{COLOR_ACCENT};font-size:22px;font-weight:800;margin:0;
            font-family:'Inter',sans-serif;letter-spacing:-0.5px">COURT SUBMISSION REPORT</h2>
            <p style="color:{COLOR_MUTED};font-size:13px;margin:4px 0 0 0;font-family:'Inter',sans-serif">
            Section 65B Indian Evidence Act 1872 Compliant • Electronic Record Certificate</p>
            </div>
            </div>
            <div style="background:rgba(0,229,255,0.08);border-left:3px solid #00E5FF;
            padding:12px 16px;border-radius:6px">
            <p style="color:{COLOR_TEXT};font-size:12px;margin:0;line-height:1.6;font-family:'Inter',sans-serif">
            <b>Legal Compliance:</b> This comprehensive IPDR analysis report contains digital evidence admissible 
            under Section 65B of the Indian Evidence Act 1872, suitable for submission to courts of law. 
            The report includes technical analysis, risk assessments, MITRE ATT&CK framework mappings, 
            and network intelligence findings.</p>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Report Form - Professional Layout
        st.markdown(
            f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
            border-radius:10px;padding:20px;margin-bottom:20px">
            <p style="color:{COLOR_ACCENT};font-size:13px;font-weight:700;margin:0 0 16px 0;
            text-transform:uppercase;letter-spacing:1.5px;font-family:'Inter',sans-serif">
            📝 REPORT DOCUMENTATION DETAILS</p>
            </div>""",
            unsafe_allow_html=True,
        )
        
        # Case Information
        col1, col2, col3 = st.columns(3)
        with col1:
            case_ref = st.text_input(
                "Case Number / Reference ID",
                value="",
                placeholder="e.g., FIR-2026/CC/0123",
                key="case_ref_p1",
                help="Official case or FIR reference number"
            )
        with col2:
            officer_name = st.text_input(
                "Investigating Officer",
                value="",
                placeholder="e.g., Inspector Rajesh Kumar",
                key="officer_p1",
                help="Name with rank of investigating officer"
            )
        with col3:
            report_date = st.date_input(
                "Report Date",
                value=pd.Timestamp.now(),
                key="report_date_p1",
                help="Date of report generation"
            )
        
        # Organization Details
        col4, col5 = st.columns(2)
        with col4:
            station_name = st.text_input(
                "Investigating Agency / Police Station",
                value="",
                placeholder="e.g., Cyber Crime Cell, Delhi Police",
                key="station_p1",
                help="Name of investigating organization or police station"
            )
        with col5:
            court_name = st.text_input(
                "Court / Authority (Optional)",
                value="",
                placeholder="e.g., District Court, Patiala House",
                key="court_p1",
                help="Court or legal authority for submission"
            )
        
        # Additional Information
        st.markdown(f"<div style='height:12px'></div>", unsafe_allow_html=True)
        
        col6, col7 = st.columns(2)
        with col6:
            case_type = st.selectbox(
                "Case Type",
                ["Cyber Crime Investigation", "Financial Fraud", "Data Breach", "Unauthorized Access", 
                 "Cyber Terrorism", "Online Harassment", "Identity Theft", "Other"],
                key="case_type_p1",
                help="Nature of the investigation"
            )
        with col7:
            sections_applied = st.text_input(
                "Legal Sections Applied (Optional)",
                value="",
                placeholder="e.g., IT Act Sec 66, 66C; IPC 420",
                key="sections_p1",
                help="Relevant IPC/IT Act sections"
            )

        # Report Summary
        report_summary = st.text_area(
            "Investigation Summary / Background (Optional)",
            value="",
            placeholder="Brief description of the case, investigation objectives, and key findings...",
            height=100,
            key="summary_p1",
            help="Executive summary of the investigation"
        )

        # Certificate Declaration
        st.markdown(
            f"""<div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.3);
            border-left:3px solid #8B5CF6;border-radius:8px;padding:14px 18px;margin:20px 0">
            <p style="color:#A78BFA;font-size:11px;font-weight:700;margin:0 0 8px 0;
            text-transform:uppercase;letter-spacing:1px">⚖️ SECTION 65B CERTIFICATE</p>
            <p style="color:{COLOR_MUTED};font-size:11px;margin:0;line-height:1.6;font-family:'Inter',sans-serif">
            By generating this report, the investigating officer certifies that the electronic records 
            contained herein were produced by a computer during the regular course of investigation, 
            and that the information contained is derived from proper information sources in accordance 
            with Section 65B of the Indian Evidence Act, 1872.</p>
            </div>""",
            unsafe_allow_html=True,
        )

        # Generate Button
        if st.button("📄 GENERATE COURT-READY REPORT", key="pdf_btn_p1", use_container_width=True, type="primary"):
            # Validation
            if not case_ref or not officer_name or not station_name:
                st.error("❌ Please fill mandatory fields: Case Number, Investigating Officer, and Agency/Station.")
            else:
                with st.spinner("⚙️ Generating comprehensive court-ready report with digital evidence..."):
                    try:
                        # Prepare comprehensive officer name with additional info
                        full_officer = f"{officer_name}"
                        if sections_applied:
                            full_officer += f" | Sections: {sections_applied}"
                        
                        # Generate PDF
                        pdf_bytes = generate_pdf(
                            stats=stats,
                            risk_scores=risk_scores,
                            mitre_results=mitre_df,
                            df=df,
                            case_ref=case_ref,
                            officer_name=full_officer,
                            station_name=station_name,
                            fir_number=case_ref,
                            court_name=court_name or "For Official Investigation",
                        )
                        
                        # Success Message with Certificate Badge
                        st.markdown(
                            f"""<div style="background:linear-gradient(135deg,rgba(0,255,136,0.12),rgba(0,229,255,0.08));
                            border:2px solid #00FF88;border-radius:10px;padding:18px 24px;margin:16px 0;
                            box-shadow:0 4px 20px rgba(0,255,136,0.2)">
                            <div style="display:flex;align-items:center;gap:12px">
                            <div style="font-size:28px">✅</div>
                            <div>
                            <p style="color:#00FF88;font-size:14px;font-weight:800;margin:0 0 4px 0;
                            text-transform:uppercase;letter-spacing:1px">REPORT GENERATED SUCCESSFULLY</p>
                            <p style="color:{COLOR_TEXT};font-size:12px;margin:0;line-height:1.5">
                            Your court-ready IPDR analysis report with Section 65B certificate is ready for download.</p>
                            </div>
                            </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        
                        # Download Button
                        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"Court_Report_{case_ref.replace(' ', '_').replace('/', '-')}_{timestamp}.pdf"
                        
                        st.download_button(
                            label="⬇️ DOWNLOAD OFFICIAL REPORT (PDF)",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        
                        # Report Details Info
                        st.markdown(
                            f"""<div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                            border-radius:8px;padding:14px 18px;margin-top:12px">
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:0 0 8px 0;
                            font-weight:600;text-transform:uppercase;letter-spacing:0.5px">REPORT DETAILS</p>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:0">
                            <b>Case:</b> {case_ref}</p>
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:0">
                            <b>Officer:</b> {officer_name}</p>
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:0">
                            <b>Date:</b> {report_date.strftime('%d %B %Y')}</p>
                            <p style="color:{COLOR_MUTED};font-size:11px;margin:0">
                            <b>Type:</b> {case_type}</p>
                            </div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Report generation failed: {e}")
                        st.info("💡 Please verify all inputs and try again. Contact technical support if the issue persists.")

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

# ══════════════════════════════════════════════════════════
# PAGE 3: WEB ANALYSIS TOOLS
# ══════════════════════════════════════════════════════════

elif page == "🌐 IPDR Analysis Tool":
    import os
    import streamlit.components.v1 as components
    
    # Full page mode - hide everything including sidebar
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .main > div {padding: 0 !important;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    iframe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    ipdr_path = os.path.join(base_dir, "IPDR_Analysis_Tool_v5.html")
    if not os.path.exists(ipdr_path):
        ipdr_path = os.path.join(base_dir, "cdr-and-ipdr", "IPDR_Analysis_Tool_v5.html")
    
    if os.path.exists(ipdr_path):
        with open(ipdr_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        components.html(html_content, height=1200, scrolling=True)
    else:
        st.error(f"❌ IPDR Analysis Tool not found at: {ipdr_path}")

elif page == "📱 CDR Analysis Tool":
    import os
    import streamlit.components.v1 as components
    
    # Full page mode - hide everything including sidebar
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .main > div {padding: 0 !important;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    iframe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    cdr_path = os.path.join(base_dir, "CDR_Analysis_Tool_v2.html")
    if not os.path.exists(cdr_path):
        cdr_path = os.path.join(base_dir, "cdr-and-ipdr", "CDR_Analysis_Tool_v2.html")
    
    if os.path.exists(cdr_path):
        with open(cdr_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        components.html(html_content, height=1200, scrolling=True)
    else:
        st.error(f"❌ CDR Analysis Tool not found at: {cdr_path}")
