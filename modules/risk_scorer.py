"""
modules/risk_scorer.py — Suराग Weighted Risk Scoring Engine
Calculates a 0–100 risk score per suspect using 5 weighted factors.
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import (
    COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM, COLOR_OK,
    RISK_CRITICAL_MIN, RISK_HIGH_MIN, RISK_MEDIUM_MIN,
)

# ── Weight Configuration ──────────────────────────────────
WEIGHTS = {
    "mitre_severity":    0.30,
    "off_hours":         0.15,
    "vpn_tor":           0.25,
    "data_anomaly":      0.15,
    "ip_reputation":     0.15,
}

# Known suspicious IP prefixes (C2, botnets, known bad actors)
BAD_IP_PREFIXES = [
    "185.220.",   # Tor exits
    "185.107.",   # Tor exits
    "195.176.",   # Tor exits
    "199.249.",   # Tor exits
    "103.21.58.", # Gang shared IPs (from demo data)
    "49.36.72.",  # Gang shared IPs (from demo data)
    "204.8.156.", # Tor exits
    "162.247.",   # Tor exits
]


def _score_mitre(df_sub: pd.DataFrame) -> float:
    """
    Score 0–100 based on worst MITRE detection in this subscriber's sessions.
    Approximated from flag combinations.
    """
    if df_sub["Is_TOR"].any():
        return 100.0
    if df_sub["Is_Foreign_IP"].any() and df_sub["Is_Off_Hours"].any():
        return 80.0
    if df_sub["Is_Foreign_IP"].any():
        return 55.0
    if df_sub["Destination_Port"].isin([22, 3389, 445]).any():
        return 60.0
    return 20.0


def _score_off_hours(df_sub: pd.DataFrame) -> float:
    """Score 0–100 based on % of sessions in off-hours window (12AM–5AM)."""
    total = len(df_sub)
    if total == 0:
        return 0.0
    off_count = int(df_sub["Is_Off_Hours"].sum())
    ratio = off_count / total
    return min(ratio * 200, 100.0)  # 50%+ off-hours → 100


def _score_vpn_tor(df_sub: pd.DataFrame) -> float:
    """Score 0–100 based on VPN/Tor usage proportion."""
    total = len(df_sub)
    if total == 0:
        return 0.0
    suspicious = int((df_sub["Is_TOR"] | df_sub["Is_VPN_Suspected"]).sum())
    ratio = suspicious / total
    return min(ratio * 150, 100.0)


def _score_data_anomaly(df_sub: pd.DataFrame, global_mean: float, global_std: float) -> float:
    """Score 0–100 based on data transfer anomaly (sessions > 2σ above mean)."""
    if global_std == 0:
        return 0.0
    threshold = global_mean + 2 * global_std
    anomalous = int((df_sub["Data_Volume_Bytes"] > threshold).sum())
    ratio = anomalous / max(len(df_sub), 1)
    return min(ratio * 200, 100.0)


def _score_ip_reputation(df_sub: pd.DataFrame) -> float:
    """Score 0–100 based on connections to known bad IP ranges."""
    bad_count = df_sub["Destination_IP"].apply(
        lambda ip: any(ip.startswith(pfx) for pfx in BAD_IP_PREFIXES)
    ).sum()
    ratio = bad_count / max(len(df_sub), 1)
    return min(ratio * 200, 100.0)


def _build_reasons(scores_dict: dict, df_sub: pd.DataFrame) -> list[str]:
    """Generate top 3 plain-English reasons for the risk score."""
    reasons = []

    if scores_dict["vpn_tor"] > 50:
        tor_count = int(df_sub["Is_TOR"].sum())
        vpn_count = int(df_sub["Is_VPN_Suspected"].sum())
        reasons.append(
            f"Used Tor anonymizing network in {tor_count} session(s) and "
            f"suspected VPN in {vpn_count} session(s) — deliberately hiding identity."
        )

    if scores_dict["off_hours"] > 40:
        off_count = int(df_sub["Is_Off_Hours"].sum())
        reasons.append(
            f"{off_count} session(s) occurred between midnight and 5 AM — "
            "unusual activity hours suggesting deliberate concealment."
        )

    if scores_dict["mitre_severity"] > 60:
        reasons.append(
            "Multiple high-severity threat patterns detected (C2 beacons, "
            "port scanning, or dark-web access)."
        )

    if scores_dict["ip_reputation"] > 40:
        bad_ips = df_sub["Destination_IP"].apply(
            lambda ip: any(ip.startswith(pfx) for pfx in BAD_IP_PREFIXES)
        ).sum()
        reasons.append(
            f"Connected to {int(bad_ips)} known suspicious or criminal IP address(es)."
        )

    if scores_dict["data_anomaly"] > 40:
        reasons.append(
            "Transferred unusually large volumes of data in some sessions — "
            "possible bulk data theft or illegal uploads."
        )

    if not reasons:
        reasons.append("Low-level anomalies detected; no single dominant indicator.")

    return reasons[:3]


@st.cache_data(show_spinner=False)
def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-subscriber risk scores (0–100) with weighted formula.
    Returns DataFrame with one row per subscriber.
    """
    global_mean = df["Data_Volume_Bytes"].mean()
    global_std  = df["Data_Volume_Bytes"].std()

    rows = []
    for sub_id, df_sub in df.groupby("Subscriber_ID"):
        name = df_sub["Subscriber_Name"].iloc[0]

        raw_scores = {
            "mitre_severity": _score_mitre(df_sub),
            "off_hours":      _score_off_hours(df_sub),
            "vpn_tor":        _score_vpn_tor(df_sub),
            "data_anomaly":   _score_data_anomaly(df_sub, global_mean, global_std),
            "ip_reputation":  _score_ip_reputation(df_sub),
        }

        weighted_score = sum(
            raw_scores[k] * WEIGHTS[k] for k in raw_scores
        )
        final_score = min(round(weighted_score), 100)

        rows.append({
            "Subscriber_ID":       sub_id,
            "Subscriber_Name":     name,
            "Risk_Score":          final_score,
            "Risk_Level":          get_risk_level(final_score),
            "Total_Sessions":      len(df_sub),
            "Total_Bytes":         int(df_sub["Data_Volume_Bytes"].sum()),
            "TOR_Sessions":        int(df_sub["Is_TOR"].sum()),
            "Foreign_Sessions":    int(df_sub["Is_Foreign_IP"].sum()),
            "Off_Hours_Sessions":  int(df_sub["Is_Off_Hours"].sum()),
            "VPN_Sessions":        int(df_sub["Is_VPN_Suspected"].sum()),
            "Top_Reasons":         _build_reasons(raw_scores, df_sub),
            "Raw_Scores":          raw_scores,
        })

    result = pd.DataFrame(rows).sort_values("Risk_Score", ascending=False).reset_index(drop=True)
    return result


def get_risk_level(score: int) -> str:
    if score >= RISK_CRITICAL_MIN:
        return "CRITICAL"
    elif score >= RISK_HIGH_MIN:
        return "HIGH"
    elif score >= RISK_MEDIUM_MIN:
        return "MEDIUM"
    return "LOW"


def get_risk_color(score: int) -> str:
    level = get_risk_level(score)
    return {
        "CRITICAL": COLOR_CRITICAL,
        "HIGH":     COLOR_HIGH,
        "MEDIUM":   "#FFD700",
        "LOW":      COLOR_OK,
    }.get(level, "#8B949E")


def get_overall_risk_score(risk_df: pd.DataFrame) -> int:
    """Compute an overall dataset risk score (weighted by max + avg)."""
    if risk_df.empty:
        return 0
    max_score = risk_df["Risk_Score"].max()
    avg_score = risk_df["Risk_Score"].mean()
    return min(round(0.6 * max_score + 0.4 * avg_score), 100)
