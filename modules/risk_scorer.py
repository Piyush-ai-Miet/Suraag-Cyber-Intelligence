"""
modules/risk_scorer.py — Suराग Weighted Risk Scoring Engine
Real cybercell investigation scoring using DoT IPDR fields.

Scoring factors (0-100 each), weighted:
  1. Tor / VPN / Proxy usage          25%
  2. Off-hours + foreign activity     20%
  3. IMEI / SIM anomaly               20%
  4. Data exfiltration patterns       15%
  5. Dangerous port activity          10%
  6. C2 / Beaconing behaviour         10%
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import (
    COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM, COLOR_OK,
    RISK_CRITICAL_MIN, RISK_HIGH_MIN, RISK_MEDIUM_MIN,
)

# ── Weights ────────────────────────────────────────────────────────────────────
WEIGHTS = {
    "tor_vpn":        0.25,
    "offhours_foreign": 0.20,
    "imei_sim":       0.20,
    "data_exfil":     0.15,
    "dangerous_ports": 0.10,
    "c2_beacon":      0.10,
}

# Dangerous ports for investigation
RAT_PORTS    = {5900, 5901, 3389, 22, 23, 4444, 5555, 7777, 8888, 9999, 1337}
C2_PORTS     = {6667, 6668, 6669, 31337, 1234, 12345}
TOR_PORTS    = {9050, 9001, 9030, 9040, 9150}
SMPP_PORTS   = {2775, 2776, 2777}   # OTP bypass
CRYPTO_PORTS = {8333, 18333}

ALL_DANGEROUS_PORTS = RAT_PORTS | C2_PORTS | TOR_PORTS | SMPP_PORTS | CRYPTO_PORTS

# Known bad IP prefixes
BAD_IP_PREFIXES = [
    "185.220.", "185.107.", "195.176.", "199.249.", "204.8.156.",
    "162.247.", "51.15.",   "45.142.",  "178.175.", "109.70.",
]


# ── Sub-scorers ────────────────────────────────────────────────────────────────

def _score_tor_vpn(df_sub: pd.DataFrame) -> float:
    """Score 0-100 based on Tor/VPN/Proxy usage proportion."""
    total = len(df_sub)
    if total == 0:
        return 0.0
    tor_count  = int(df_sub["Is_TOR"].sum())
    vpn_count  = int(df_sub["Is_VPN_Suspected"].sum())
    # Tor is more serious than VPN
    score = (tor_count * 2 + vpn_count) / (total * 2)
    return min(score * 150, 100.0)


def _score_offhours_foreign(df_sub: pd.DataFrame) -> float:
    """
    Score 0-100 based on off-hours activity and foreign IP access.
    Combined score because both together = highest risk.
    """
    total = len(df_sub)
    if total == 0:
        return 0.0
    off_count     = int(df_sub["Is_Off_Hours"].sum())
    foreign_count = int(df_sub["Is_Foreign_IP"].sum())
    # Both together is most dangerous
    both_count    = int((df_sub["Is_Off_Hours"] & df_sub["Is_Foreign_IP"]).sum())

    off_ratio     = off_count / total
    foreign_ratio = foreign_count / total
    both_ratio    = both_count / total

    score = (off_ratio * 80) + (foreign_ratio * 60) + (both_ratio * 100)
    return min(score / 3, 100.0)


def _score_imei_sim(df_sub: pd.DataFrame, full_df: pd.DataFrame) -> float:
    """
    Score 0-100 based on IMEI/SIM anomalies.
    - Multiple SIMs on same IMEI (SIM swap fraud)
    - Multiple IMEIs for same subscriber (device sharing)
    - Impossible cell tower jumps
    """
    score = 0.0

    if "IMEI" not in df_sub.columns:
        return 0.0

    # Multiple IMEIs for this subscriber
    unique_imeis = df_sub["IMEI"].astype(str)
    unique_imeis = unique_imeis[unique_imeis.str.upper() != "UNKNOWN"]
    if unique_imeis.nunique() > 1:
        score += 40.0  # Using multiple devices

    # Check if any of this subscriber's IMEIs are shared with other subscribers
    if "IMEI" in full_df.columns and "Subscriber_ID" in full_df.columns:
        my_imeis = set(unique_imeis.unique())
        for imei in my_imeis:
            subs_using = full_df[
                (full_df["IMEI"].astype(str) == str(imei)) &
                (full_df["IMEI"].astype(str).str.upper() != "UNKNOWN")
            ]["Subscriber_ID"].nunique()
            if subs_using > 1:
                score += 60.0  # SIM swap indicator
                break

    # Cell tower jumping (impossible travel)
    if "Cell_ID" in df_sub.columns and df_sub["Cell_ID"].astype(str).ne("UNKNOWN").any():
        sub_sorted = df_sub.sort_values("Timestamp")
        towers = sub_sorted["Cell_ID"].astype(str).values
        times  = sub_sorted["Timestamp"].values
        for i in range(1, len(towers)):
            if towers[i] != towers[i-1]:
                diff_min = (times[i] - times[i-1]) / np.timedelta64(1, 'm')
                if 0 < diff_min < 2:
                    score += 50.0
                    break

    return min(score, 100.0)


def _score_data_exfil(df_sub: pd.DataFrame) -> float:
    """
    Score 0-100 based on data exfiltration patterns.
    - High uplink vs downlink ratio (sending more than receiving)
    - Large data spikes off-hours
    - Total data volume anomaly
    """
    total = len(df_sub)
    if total == 0:
        return 0.0

    score = 0.0

    # Uplink >> Downlink anomaly
    if "Uplink_Volume" in df_sub.columns and "Downlink_Volume" in df_sub.columns:
        ul = pd.to_numeric(df_sub["Uplink_Volume"], errors="coerce").fillna(0).sum()
        dl = pd.to_numeric(df_sub["Downlink_Volume"], errors="coerce").fillna(0).sum()
        total_vol = ul + dl
        if total_vol > 1_000_000:  # > 1MB total
            ul_ratio = ul / max(total_vol, 1)
            if ul_ratio > 0.7:    # Uploading > 70%
                score += 60.0
            elif ul_ratio > 0.5:  # Uploading > 50%
                score += 30.0

    # Off-hours large transfers
    off_hours_data = df_sub[df_sub["Is_Off_Hours"]]["Data_Volume_Bytes"].sum()
    total_data     = df_sub["Data_Volume_Bytes"].sum()
    if total_data > 0:
        off_ratio = off_hours_data / total_data
        score += off_ratio * 40.0

    return min(score, 100.0)


def _score_dangerous_ports(df_sub: pd.DataFrame) -> float:
    """Score 0-100 based on connections to dangerous ports."""
    total = len(df_sub)
    if total == 0:
        return 0.0
    dangerous = df_sub["Destination_Port"].isin(ALL_DANGEROUS_PORTS).sum()
    # RAT and SMPP are more serious
    rat_hits   = df_sub["Destination_Port"].isin(RAT_PORTS).sum()
    smpp_hits  = df_sub["Destination_Port"].isin(SMPP_PORTS).sum()

    score = (dangerous / total) * 80
    score += min(rat_hits  * 10, 20)
    score += min(smpp_hits * 15, 30)
    return min(score, 100.0)


def _score_c2_beacon(df_sub: pd.DataFrame) -> float:
    """
    Score 0-100 based on C2/beaconing behaviour.
    - Repeated connections to same foreign IP
    - Known bad IP prefix connections
    """
    score = 0.0
    total = len(df_sub)
    if total == 0:
        return 0.0

    # Beaconing: same foreign IP contacted 5+ times
    foreign_df = df_sub[df_sub["Is_Foreign_IP"]]
    if not foreign_df.empty:
        max_repeat = foreign_df.groupby("Destination_IP").size().max()
        if max_repeat >= 10:
            score += 70.0
        elif max_repeat >= 5:
            score += 40.0

    # Known bad IP prefixes
    bad_hits = df_sub["Destination_IP"].apply(
        lambda ip: any(ip.startswith(p) for p in BAD_IP_PREFIXES)
    ).sum()
    score += min(bad_hits / max(total, 1) * 200, 40.0)

    return min(score, 100.0)


def _build_reasons(scores: dict, df_sub: pd.DataFrame) -> list:
    """Generate top 3 plain-English investigation reasons."""
    reasons = []

    if scores["tor_vpn"] > 40:
        tor_c = int(df_sub["Is_TOR"].sum())
        vpn_c = int(df_sub["Is_VPN_Suspected"].sum())
        reasons.append(
            f"Used Tor in {tor_c} session(s) and VPN in {vpn_c} session(s) — "
            "deliberately hiding identity from law enforcement."
        )

    if scores["imei_sim"] > 40:
        if "IMEI" in df_sub.columns:
            unique_imeis = df_sub["IMEI"].astype(str)
            unique_imeis = unique_imeis[unique_imeis.str.upper() != "UNKNOWN"].nunique()
            if unique_imeis > 1:
                reasons.append(
                    f"Used {unique_imeis} different devices (IMEIs) — "
                    "device swapping to evade tracking."
                )
            else:
                reasons.append(
                    "IMEI/SIM anomaly detected — possible SIM swap fraud or cloned SIM."
                )

    if scores["offhours_foreign"] > 40:
        off_c     = int(df_sub["Is_Off_Hours"].sum())
        foreign_c = int(df_sub["Is_Foreign_IP"].sum())
        reasons.append(
            f"{off_c} off-hours sessions (12 AM–5 AM), {foreign_c} foreign IP connections — "
            "suspicious late-night activity with overseas servers."
        )

    if scores["data_exfil"] > 40:
        if "Uplink_Volume" in df_sub.columns:
            ul = pd.to_numeric(df_sub["Uplink_Volume"], errors="coerce").fillna(0).sum()
            dl = pd.to_numeric(df_sub["Downlink_Volume"], errors="coerce").fillna(0).sum()
            reasons.append(
                f"Uploaded {ul/1e6:.1f} MB vs downloaded {dl/1e6:.1f} MB — "
                "abnormally high upload suggests data exfiltration."
            )
        else:
            reasons.append("Unusual data transfer pattern detected — possible bulk data theft.")

    if scores["dangerous_ports"] > 40:
        rat_c  = int(df_sub["Destination_Port"].isin(RAT_PORTS).sum())
        smpp_c = int(df_sub["Destination_Port"].isin(SMPP_PORTS).sum())
        if smpp_c > 0:
            reasons.append(
                f"SMPP ports (OTP bypass) accessed {smpp_c} time(s) — "
                "strong indicator of UPI/banking fraud via OTP interception."
            )
        elif rat_c > 0:
            reasons.append(
                f"Remote access tool ports accessed {rat_c} time(s) — "
                "possible device hijacking / cyber fraud call center activity."
            )

    if scores["c2_beacon"] > 40:
        reasons.append(
            "Repeated connections to same foreign server — malware beacon or "
            "criminal C2 communication detected."
        )

    if not reasons:
        reasons.append("Multiple low-level anomalies detected — further investigation advised.")

    return reasons[:3]


@st.cache_data(show_spinner=False)
def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-subscriber risk scores (0–100) with weighted formula.
    Returns DataFrame sorted by risk score (highest first).
    """
    rows = []
    for sub_id, df_sub in df.groupby("Subscriber_ID"):
        name = df_sub["Subscriber_Name"].iloc[0] if "Subscriber_Name" in df_sub.columns else sub_id

        raw_scores = {
            "tor_vpn":           _score_tor_vpn(df_sub),
            "offhours_foreign":  _score_offhours_foreign(df_sub),
            "imei_sim":          _score_imei_sim(df_sub, df),
            "data_exfil":        _score_data_exfil(df_sub),
            "dangerous_ports":   _score_dangerous_ports(df_sub),
            "c2_beacon":         _score_c2_beacon(df_sub),
        }

        weighted = sum(raw_scores[k] * WEIGHTS[k] for k in raw_scores)
        final    = min(round(weighted), 100)

        # IMEI info
        imei_list = []
        if "IMEI" in df_sub.columns:
            imei_list = [
                i for i in df_sub["IMEI"].astype(str).unique()
                if i.upper() != "UNKNOWN"
            ]

        rows.append({
            "Subscriber_ID":      sub_id,
            "Subscriber_Name":    name,
            "MSISDN":             df_sub.get("MSISDN", pd.Series([sub_id])).iloc[0]
                                  if "MSISDN" in df_sub.columns else sub_id,
            "Risk_Score":         final,
            "Risk_Level":         get_risk_level(final),
            "Total_Sessions":     len(df_sub),
            "Total_Bytes":        int(df_sub["Data_Volume_Bytes"].sum()),
            "TOR_Sessions":       int(df_sub["Is_TOR"].sum()),
            "Foreign_Sessions":   int(df_sub["Is_Foreign_IP"].sum()),
            "Off_Hours_Sessions": int(df_sub["Is_Off_Hours"].sum()),
            "VPN_Sessions":       int(df_sub["Is_VPN_Suspected"].sum()),
            "IMEI_List":          imei_list,
            "Top_Reasons":        _build_reasons(raw_scores, df_sub),
            "Raw_Scores":         raw_scores,
        })

    return (
        pd.DataFrame(rows)
        .sort_values("Risk_Score", ascending=False)
        .reset_index(drop=True)
    )


def get_risk_level(score: int) -> str:
    if score >= RISK_CRITICAL_MIN:
        return "CRITICAL"
    elif score >= RISK_HIGH_MIN:
        return "HIGH"
    elif score >= RISK_MEDIUM_MIN:
        return "MEDIUM"
    return "LOW"


def get_risk_color(score: int) -> str:
    return {
        "CRITICAL": COLOR_CRITICAL,
        "HIGH":     COLOR_HIGH,
        "MEDIUM":   "#FFD700",
        "LOW":      COLOR_OK,
    }.get(get_risk_level(score), "#8B949E")


def get_overall_risk_score(risk_df: pd.DataFrame) -> int:
    if risk_df.empty:
        return 0
    return min(round(0.6 * risk_df["Risk_Score"].max() + 0.4 * risk_df["Risk_Score"].mean()), 100)
