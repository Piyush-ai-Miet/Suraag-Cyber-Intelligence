"""
modules/correlation_engine.py — Suराग Multi-IPDR Gang Detection Engine
Real cybercell correlation logic for linking suspects.

Evidence hierarchy (strongest to weakest):
  1. Shared IMEI              → Same physical device = definitive link
  2. Shared Cell Tower        → Same physical location
  3. Shared Destination IP    → Same criminal server/infrastructure
  4. Synchronized Activity    → Same time window = coordinated operation
  5. Shared ISP / Port        → Shared tools/setup
"""

import pandas as pd
import numpy as np
import streamlit as st
from config import COLOR_CRITICAL, COLOR_HIGH, COLOR_OK

SYNC_WINDOW_MINUTES = 15


@st.cache_data(show_spinner=False)
def correlate_ipdrs(dfs: tuple, labels: tuple) -> dict:
    """
    Main correlation engine.
    Takes N DataFrames (as tuple for Streamlit caching).
    Returns full correlation results dict.
    """
    tagged = []
    for df, label in zip(dfs, labels):
        d = df.copy()
        d["_suspect_label"] = label
        tagged.append(d)
    combined = pd.concat(tagged, ignore_index=True)

    shared_imei    = _find_shared_imei(combined, labels)
    shared_towers  = _find_shared_cell_towers(combined, labels)
    shared_ips     = _find_shared_ips(combined, labels)
    sync_windows   = _find_sync_windows(combined, labels)
    shared_infra   = _find_shared_infrastructure(combined, labels)
    gang_score     = _compute_gang_score(
        shared_imei, shared_towers, shared_ips,
        sync_windows, shared_infra, len(labels)
    )

    return {
        "combined_df":     combined,
        "shared_imei":     shared_imei,
        "shared_towers":   shared_towers,
        "shared_ips":      shared_ips,
        "sync_windows":    sync_windows,
        "shared_infra":    shared_infra,
        "gang_score":      gang_score,
        "verdict":         _get_verdict(gang_score),
        "evidence_points": _build_evidence(
            shared_imei, shared_towers, shared_ips,
            sync_windows, shared_infra, labels
        ),
    }


def _find_shared_imei(df: pd.DataFrame, labels: tuple) -> pd.DataFrame:
    """
    STRONGEST LINK: Same physical device (IMEI) used by multiple suspects.
    This is definitive proof of connection — same hardware = same gang.
    """
    if "IMEI" not in df.columns:
        return pd.DataFrame(columns=["IMEI", "Used_By", "Suspect_Count", "Sessions", "Risk"])

    valid = df[df["IMEI"].astype(str).str.upper() != "UNKNOWN"].copy()
    if valid.empty:
        return pd.DataFrame(columns=["IMEI", "Used_By", "Suspect_Count", "Sessions", "Risk"])

    agg = (
        valid.groupby("IMEI")
        .agg(
            Used_By    = ("_suspect_label", lambda x: ", ".join(sorted(set(x)))),
            Suspects   = ("_suspect_label", lambda x: sorted(set(x))),
            Sessions   = ("_suspect_label", "count"),
        )
        .reset_index()
    )
    agg["Suspect_Count"] = agg["Suspects"].apply(len)
    shared = agg[agg["Suspect_Count"] >= 2].copy()
    shared["Risk"] = "CRITICAL"   # Shared IMEI is always CRITICAL
    return shared[["IMEI", "Used_By", "Suspect_Count", "Sessions", "Risk"]].sort_values(
        "Suspect_Count", ascending=False
    ).reset_index(drop=True)


def _find_shared_cell_towers(df: pd.DataFrame, labels: tuple) -> pd.DataFrame:
    """
    STRONG LINK: Multiple suspects using the same cell tower.
    Means they were physically at the same location.
    """
    if "Cell_ID" not in df.columns:
        return pd.DataFrame(columns=["Cell_ID", "LAC", "Used_By", "Suspect_Count", "Sessions"])

    valid = df[df["Cell_ID"].astype(str).str.upper() != "UNKNOWN"].copy()
    if valid.empty:
        return pd.DataFrame(columns=["Cell_ID", "LAC", "Used_By", "Suspect_Count", "Sessions"])

    group_cols = ["Cell_ID"]
    if "LAC" in df.columns:
        group_cols = ["Cell_ID", "LAC"]

    agg = (
        valid.groupby(group_cols)
        .agg(
            Used_By  = ("_suspect_label", lambda x: ", ".join(sorted(set(x)))),
            Suspects = ("_suspect_label", lambda x: sorted(set(x))),
            Sessions = ("_suspect_label", "count"),
        )
        .reset_index()
    )
    agg["Suspect_Count"] = agg["Suspects"].apply(len)
    shared = agg[agg["Suspect_Count"] >= 2].copy()
    if "LAC" not in shared.columns:
        shared["LAC"] = "N/A"
    return shared[["Cell_ID", "LAC", "Used_By", "Suspect_Count", "Sessions"]].sort_values(
        "Suspect_Count", ascending=False
    ).reset_index(drop=True)


def _find_shared_ips(df: pd.DataFrame, labels: tuple) -> pd.DataFrame:
    """
    Shared destination IPs across suspects.
    Same criminal server contacted = shared infrastructure.
    """
    agg = (
        df.groupby("Destination_IP")
        .agg(
            Found_In_Suspects = ("_suspect_label", lambda x: ", ".join(sorted(set(x)))),
            Suspects          = ("_suspect_label", lambda x: sorted(set(x))),
            Total_Sessions    = ("_suspect_label", "count"),
        )
        .reset_index()
    )
    agg["Suspect_Count"] = agg["Suspects"].apply(len)
    shared = agg[agg["Suspect_Count"] >= 2].copy()

    # Risk level based on suspect count and Tor
    tor_prefixes = [
        "185.220.", "185.107.", "195.176.", "199.249.",
        "204.8.156.", "162.247.",
    ]
    def _risk(row):
        ip = row["Destination_IP"]
        if any(ip.startswith(p) for p in tor_prefixes):
            return "CRITICAL"
        if row["Suspect_Count"] == len(labels):
            return "CRITICAL"
        if row["Suspect_Count"] >= 3:
            return "HIGH"
        return "MEDIUM"

    shared["Risk_Level"] = shared.apply(_risk, axis=1)
    return shared[
        ["Destination_IP", "Found_In_Suspects", "Suspect_Count", "Total_Sessions", "Risk_Level"]
    ].sort_values(["Suspect_Count", "Total_Sessions"], ascending=False).reset_index(drop=True)


def _find_sync_windows(df: pd.DataFrame, labels: tuple) -> pd.DataFrame:
    """
    Synchronized activity windows: 2+ suspects active in same 15-min window.
    Coordinated operations = planned criminal activity.
    """
    temp = df.copy()
    temp["Window"] = temp["Timestamp"].dt.floor(f"{SYNC_WINDOW_MINUTES}min")

    agg = (
        temp.groupby("Window")
        .agg(
            Suspects_Active = ("_suspect_label", lambda x: ", ".join(sorted(set(x)))),
            Suspect_Count   = ("_suspect_label", lambda x: len(set(x))),
        )
        .reset_index()
    )
    synced = agg[agg["Suspect_Count"] >= 2].copy()
    synced["Window_Start"] = synced["Window"].dt.strftime("%Y-%m-%d %H:%M IST")
    return synced[["Window_Start", "Suspects_Active", "Suspect_Count"]].sort_values(
        "Suspect_Count", ascending=False
    ).head(20).reset_index(drop=True)


def _find_shared_infrastructure(df: pd.DataFrame, labels: tuple) -> dict:
    """Find shared servers, ports, ISPs across suspects."""
    results = {}

    def _shared_count(col):
        if col not in df.columns:
            return 0, []
        agg = (
            df.groupby(col)["_suspect_label"]
            .apply(lambda x: sorted(set(x)))
            .reset_index()
        )
        agg["cnt"] = agg["_suspect_label"].apply(len)
        s = agg[agg["cnt"] >= 2]
        return len(s), s[col].tolist()

    results["shared_servers_count"], results["shared_servers"] = _shared_count("Destination_IP")
    results["shared_ports_count"],   results["shared_ports"]   = _shared_count("Destination_Port")
    results["shared_isps_count"],    results["shared_isps"]    = _shared_count("ISP")

    # Build summary table
    rows = []
    for ip in results["shared_servers"][:10]:
        subs = df[df["Destination_IP"] == ip]["_suspect_label"].unique()
        rows.append({"Type": "Destination Server", "Value": ip,
                     "Suspects": ", ".join(sorted(subs)), "Overlap Count": len(subs)})
    for port in results["shared_ports"][:5]:
        subs = df[df["Destination_Port"] == port]["_suspect_label"].unique()
        rows.append({"Type": "Shared Port", "Value": str(port),
                     "Suspects": ", ".join(sorted(subs)), "Overlap Count": len(subs)})
    for isp in results["shared_isps"][:5]:
        subs = df[df["ISP"] == isp]["_suspect_label"].unique()
        rows.append({"Type": "Shared ISP", "Value": str(isp),
                     "Suspects": ", ".join(sorted(subs)), "Overlap Count": len(subs)})

    results["infra_table"] = pd.DataFrame(rows)
    return results


def _compute_gang_score(
    shared_imei: pd.DataFrame,
    shared_towers: pd.DataFrame,
    shared_ips: pd.DataFrame,
    sync_windows: pd.DataFrame,
    shared_infra: dict,
    n_suspects: int,
) -> int:
    """
    Gang probability score 0–100.

    Evidence weights (real cybercell hierarchy):
      Shared IMEI     → 50 pts max  (definitive physical link)
      Shared Tower    → 20 pts max  (same location)
      Shared IPs      → 15 pts max  (same infrastructure)
      Sync Windows    → 10 pts max  (coordinated timing)
      Shared Infra    →  5 pts max  (shared tools)
    """
    score = 0

    # Shared IMEI (strongest — each shared device = 25 pts, max 50)
    if not shared_imei.empty:
        score += min(len(shared_imei) * 25, 50)

    # Shared Cell Tower (each = 5 pts, max 20)
    if not shared_towers.empty:
        score += min(len(shared_towers) * 5, 20)

    # Shared IPs (each = 3 pts, max 15; CRITICAL IPs = 5 pts)
    if not shared_ips.empty:
        critical_ips = len(shared_ips[shared_ips["Risk_Level"] == "CRITICAL"])
        normal_ips   = len(shared_ips) - critical_ips
        score += min(critical_ips * 5 + normal_ips * 3, 15)

    # Sync windows (each = 1 pt, max 10)
    score += min(len(sync_windows), 10)

    # Shared infra (max 5)
    infra_count = (
        shared_infra.get("shared_servers_count", 0) +
        shared_infra.get("shared_ports_count", 0)
    )
    score += min(infra_count, 5)

    return min(score, 100)


def _get_verdict(score: int) -> dict:
    if score >= 50:
        return {
            "label": "CONFIRMED GANG CONNECTION",
            "color": COLOR_CRITICAL,
            "emoji": "🔴",
            "description": (
                "Strong forensic evidence links these suspects. "
                "Shared device (IMEI), common infrastructure, or synchronized activity detected. "
                "Recommend joint investigation and coordinated arrest."
            ),
        }
    elif score >= 25:
        return {
            "label": "PROBABLE ASSOCIATION",
            "color": COLOR_HIGH,
            "emoji": "🟠",
            "description": (
                "Multiple indicators suggest coordination between suspects. "
                "Shared servers or activity patterns found. "
                "Further surveillance and call record analysis recommended."
            ),
        }
    else:
        return {
            "label": "NO CONFIRMED LINK",
            "color": "#3FB950",
            "emoji": "🟢",
            "description": (
                "No strong forensic evidence of connection found. "
                "Suspects appear to be operating independently. "
                "Individual investigation recommended."
            ),
        }


def _build_evidence(
    shared_imei: pd.DataFrame,
    shared_towers: pd.DataFrame,
    shared_ips: pd.DataFrame,
    sync_windows: pd.DataFrame,
    shared_infra: dict,
    labels: tuple,
) -> list:
    """Top 6 plain-English evidence statements for court submission."""
    evidence = []

    # IMEI evidence (strongest)
    if not shared_imei.empty:
        row = shared_imei.iloc[0]
        evidence.append(
            f"🔴 CRITICAL: Device with IMEI {row['IMEI']} was used by {row['Suspect_Count']} "
            f"different suspects ({row['Used_By']}). Same physical device = definitive connection. "
            "This is the strongest possible evidence of gang association."
        )

    # Cell tower evidence
    if not shared_towers.empty:
        row = shared_towers.iloc[0]
        evidence.append(
            f"🟠 Cell Tower {row['Cell_ID']} (LAC: {row.get('LAC', 'N/A')}) was used by "
            f"{row['Suspect_Count']} suspects ({row['Used_By']}). "
            "Physical co-location at same tower confirms they were present at the same place."
        )

    # Shared IP evidence
    if not shared_ips.empty:
        top = shared_ips.iloc[0]
        evidence.append(
            f"Server {top['Destination_IP']} was contacted by {top['Suspect_Count']} suspects "
            f"({top['Found_In_Suspects']}). "
            f"Total {len(shared_ips)} shared server(s) detected — common criminal infrastructure."
        )

    # Sync window evidence
    if not sync_windows.empty:
        evidence.append(
            f"{len(sync_windows)} time window(s) found where multiple suspects were "
            "simultaneously active — coordinated criminal operation detected."
        )

    # Infra evidence
    if shared_infra.get("shared_ports_count", 0) > 0:
        ports = ", ".join(str(p) for p in shared_infra.get("shared_ports", [])[:3])
        evidence.append(
            f"Same ports ({ports}) used by multiple suspects — "
            "consistent tool usage indicates shared criminal infrastructure."
        )

    if shared_infra.get("shared_isps_count", 0) > 0:
        isps = ", ".join(str(i) for i in shared_infra.get("shared_isps", [])[:2])
        evidence.append(
            f"Same ISP ({isps}) used by multiple suspects — "
            "possible use of same physical location or coordinated SIM procurement."
        )

    if not evidence:
        evidence.append(
            "No strong links detected between suspects. "
            "They appear to be operating independently."
        )

    return evidence[:6]
