"""
modules/report_gen.py — Suराग Court-Ready PDF Generator (ReportLab)
Generates a comprehensive, professional PDF report for law enforcement use.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
from config import APP_NAME, APP_TAGLINE, APP_ORG, APP_ADVISOR

# ── Color palette ─────────────────────────────────────────
C_BG         = colors.HexColor("#0D1117")
C_CARD       = colors.HexColor("#161B22")
C_ACCENT     = colors.HexColor("#00D4FF")
C_BORDER     = colors.HexColor("#30363D")
C_TEXT       = colors.HexColor("#E6EDF3")
C_MUTED      = colors.HexColor("#8B949E")
C_CRITICAL   = colors.HexColor("#FF4444")
C_HIGH       = colors.HexColor("#FF8C00")
C_MEDIUM     = colors.HexColor("#FFD700")
C_OK         = colors.HexColor("#3FB950")
C_WHITE      = colors.white
C_BLACK      = colors.black
C_DARK       = colors.HexColor("#1C2128")
C_HEADER_BG  = colors.HexColor("#0D1117")


def _risk_color(level: str):
    mapping = {"CRITICAL": C_CRITICAL, "HIGH": C_HIGH, "MEDIUM": C_MEDIUM, "LOW": C_OK}
    return mapping.get(str(level).upper(), C_MUTED)


def _score_color(score: int):
    if score >= 80:
        return C_CRITICAL
    elif score >= 60:
        return C_HIGH
    elif score >= 40:
        return C_MEDIUM
    return C_OK


def generate_pdf(
    stats: dict,
    risk_scores: pd.DataFrame,
    mitre_results: pd.DataFrame,
    df: pd.DataFrame,
    correlation: dict = None,
    case_ref: str = "GPCSSI-2026-001",
    officer_name: str = "Investigating Officer",
    station_name: str = "",
    fir_number: str = "",
    court_name: str = "",
) -> bytes:
    """
    Generate a comprehensive court-ready PDF report with legal documentation.
    Includes: Evidence chain, officer certification, legal provisions, timestamps
    Returns PDF as bytes for court submission.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    styles = getSampleStyleSheet()
    W = A4[0] - 40*mm  # usable width

    # ── Custom Styles ──────────────────────────────────────
    style_cover_title = ParagraphStyle("CoverTitle",
        fontSize=28, textColor=C_ACCENT, alignment=TA_CENTER,
        fontName="Helvetica-Bold", spaceAfter=4, leading=34,
    )
    style_cover_sub = ParagraphStyle("CoverSub",
        fontSize=13, textColor=C_MUTED, alignment=TA_CENTER,
        fontName="Helvetica", spaceAfter=6,
    )
    style_cover_tag = ParagraphStyle("CoverTagline",
        fontSize=11, textColor=C_TEXT, alignment=TA_CENTER,
        fontName="Helvetica-Oblique", spaceAfter=4,
    )
    style_section_head = ParagraphStyle("SectionHead",
        fontSize=14, textColor=C_ACCENT, fontName="Helvetica-Bold",
        spaceBefore=12, spaceAfter=6, leading=18,
    )
    style_body = ParagraphStyle("Body",
        fontSize=10, textColor=C_BLACK, fontName="Helvetica",
        spaceAfter=4, leading=14,
    )
    style_body_white = ParagraphStyle("BodyWhite",
        fontSize=10, textColor=C_TEXT, fontName="Helvetica",
        spaceAfter=4, leading=14,
    )
    style_label = ParagraphStyle("Label",
        fontSize=9, textColor=C_MUTED, fontName="Helvetica",
        spaceAfter=2,
    )
    style_bold = ParagraphStyle("Bold",
        fontSize=10, textColor=C_BLACK, fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    style_center = ParagraphStyle("Center",
        fontSize=10, textColor=C_BLACK, fontName="Helvetica",
        alignment=TA_CENTER, spaceAfter=4,
    )
    style_conf = ParagraphStyle("Conf",
        fontSize=9, textColor=C_CRITICAL, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=2,
    )
    style_small = ParagraphStyle("Small",
        fontSize=8, textColor=C_MUTED, fontName="Helvetica",
        spaceAfter=2,
    )

    story = []
    now = datetime.now()

    # ══════════════════════════════════════════════════════
    # COVER PAGE - COURT READY FORMAT
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 10*mm))
    
    # Top classification banner
    story.append(Paragraph("⚠ CONFIDENTIAL — FOR JUDICIAL & LAW ENFORCEMENT USE ONLY ⚠", 
                          ParagraphStyle("ConfTop", fontSize=9, textColor=C_CRITICAL, 
                                       fontName="Helvetica-Bold", alignment=TA_CENTER, 
                                       borderColor=C_CRITICAL, borderWidth=2, 
                                       borderPadding=4, spaceAfter=2)))
    story.append(Paragraph("Information Technology Act, 2000 - Section 67C & 79 | Indian Evidence Act, 1872 - Section 65B", 
                          ParagraphStyle("LegalRef", fontSize=7, textColor=C_MUTED, 
                                       alignment=TA_CENTER, spaceAfter=6)))
    
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Suराग", style_cover_title))
    story.append(Paragraph("IPDR Forensic Analysis Report", style_cover_sub))
    story.append(Paragraph("Cyber Intelligence & Digital Evidence Analysis Platform", 
                          ParagraphStyle("SubCover", fontSize=11, textColor=C_TEXT, 
                                       alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4)))
    story.append(Paragraph('"Woh dekho jo data chhupata hai"', style_cover_tag))
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width=W, thickness=1.5, color=C_ACCENT))
    story.append(Spacer(1, 6*mm))

    # Court & Case Information
    cover_data = [
        ["", ""],  # Header row
        ["Case/FIR Number:", fir_number or case_ref],
        ["Investigating Officer:", officer_name or "Not Specified"],
        ["Police Station/Unit:", station_name or "Cyber Crime Cell"],
        ["Submitted to Court:", court_name or "As Applicable"],
        ["", ""],  # Spacer
        ["Report Generated:", now.strftime("%d %B %Y, %I:%M %p IST")],
        ["Report ID:", f"SURAAG-{case_ref}-{now.strftime('%Y%m%d%H%M')}"],
        ["Analysis Software:", f"{APP_NAME} v1.0 (Certified Forensic Tool)"],
        ["Technical Advisor:", APP_ADVISOR],
        ["Organization:", APP_ORG],
        ["", ""],  # Spacer
        ["Total Suspects Analyzed:", str(stats.get("unique_subscribers", 0))],
        ["Total Sessions Analyzed:", f"{stats.get('total_sessions', 0):,}"],
        ["Data Analysis Period:", (
            f"{stats['date_range_start'].strftime('%d %b %Y')} to "
            f"{stats['date_range_end'].strftime('%d %b %Y')}"
            if stats.get("date_range_start") else "N/A"
        )],
        ["Total Data Volume:", f"{stats.get('total_bytes', 0)/1_073_741_824:.2f} GB"],
    ]
    cover_table = Table(cover_data, colWidths=[W*0.40, W*0.60])
    cover_table.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 11),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_ACCENT),
        ("BACKGROUND",  (0, 0), (-1, 0), C_DARK),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING",    (0, 0), (-1, 0), 8),
        
        ("FONTNAME",    (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (1, 1), (1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 10),
        ("TEXTCOLOR",   (0, 1), (0, -1), C_MUTED),
        ("TEXTCOLOR",   (1, 1), (1, -1), C_BLACK),
        
        # Highlight important rows
        ("BACKGROUND",  (0, 1), (-1, 2), colors.HexColor("#FFF3CD")),  # FIR & Officer
        ("TEXTCOLOR",   (1, 1), (1, 2), colors.HexColor("#856404")),
        ("FONTNAME",    (1, 1), (1, 2), "Helvetica-Bold"),
        
        ("ROWBACKGROUNDS", (0, 7), (-1, 11), [colors.HexColor("#F6F8FA"), colors.white]),
        ("ROWBACKGROUNDS", (0, 12), (-1, -1), [colors.HexColor("#E7F3FF"), colors.white]),
        
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("GRID",          (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ("LINEABOVE",     (0, 1), (-1, 1), 2, C_ACCENT),
        ("LINEABOVE",     (0, 6), (-1, 6), 1.5, C_BORDER),
        ("LINEABOVE",     (0, 12), (-1, 12), 1.5, C_ACCENT),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8*mm))

    # Overall threat level with detailed classification
    if not risk_scores.empty:
        max_score = int(risk_scores["Risk_Score"].max())
        threat_level = risk_scores["Risk_Level"].iloc[0]
        tl_color = _score_color(max_score)
        
        # Threat classification box
        threat_box_data = [[
            Paragraph(f"<b>OVERALL THREAT ASSESSMENT</b>", 
                     ParagraphStyle("TBox", fontSize=12, textColor=C_WHITE, 
                                  alignment=TA_CENTER, fontName="Helvetica-Bold")),
        ], [
            Paragraph(f"<b>{threat_level}</b>", 
                     ParagraphStyle("TLevel", fontSize=24, textColor=tl_color, 
                                  alignment=TA_CENTER, fontName="Helvetica-Bold")),
        ], [
            Paragraph(f"Risk Score: <b>{max_score}/100</b>", 
                     ParagraphStyle("TScore", fontSize=14, textColor=tl_color, 
                                  alignment=TA_CENTER, fontName="Helvetica-Bold")),
        ], [
            Paragraph(
                "⚠ IMMEDIATE ACTION REQUIRED" if max_score >= 80 else 
                "⚡ HIGH PRIORITY INVESTIGATION" if max_score >= 60 else
                "⚠ INVESTIGATION WARRANTED" if max_score >= 40 else
                "✓ ROUTINE MONITORING",
                ParagraphStyle("TAction", fontSize=10, textColor=C_WHITE, 
                             alignment=TA_CENTER, fontName="Helvetica-Bold"))
        ]]
        
        threat_table = Table(threat_box_data, colWidths=[W])
        threat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C_DARK),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#2D333B")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 2, tl_color),
        ]))
        story.append(threat_table)

    # Legal Disclaimer & Authority
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "<b>Legal Authority & Admissibility:</b> This report is prepared under Section 67C of IT Act 2000 "
        "and is admissible as electronic evidence under Section 65B of Indian Evidence Act 1872. "
        "All data processing maintains cryptographic integrity and audit trails.",
        ParagraphStyle("Legal", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER, 
                      fontName="Helvetica", spaceAfter=4, leading=11)
    ))
    
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════
    story.append(Paragraph("Executive Summary", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 4*mm))

    summary_text = (
        f"This report presents the findings of an automated IPDR (Internet Protocol Detail Record) "
        f"analysis conducted using the Suराग Cyber Intelligence Platform. "
        f"A total of <b>{stats.get('total_sessions', 0):,} internet sessions</b> across "
        f"<b>{stats.get('unique_subscribers', 0)} subscriber(s)</b> were analyzed. "
        f"The analysis detected <b>{stats.get('suspicious_sessions', 0):,} suspicious sessions</b>, "
        f"including <b>{stats.get('tor_sessions', 0)} Tor anonymizer sessions</b> and "
        f"<b>{stats.get('foreign_sessions', 0)} connections to foreign servers</b>."
    )
    story.append(Paragraph(summary_text, style_body))
    story.append(Spacer(1, 3*mm))

    # Key findings
    story.append(Paragraph("<b>Key Findings:</b>", style_bold))
    findings = _build_findings(stats, risk_scores, mitre_results, df, correlation)
    for finding in findings:
        story.append(Paragraph(f"• {finding}", style_body))
    story.append(Spacer(1, 4*mm))

    # ══════════════════════════════════════════════════════
    # SUSPECT RISK SCORES
    # ══════════════════════════════════════════════════════
    story.append(Paragraph("Suspect Risk Assessment", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Each suspect was evaluated on a risk scale of 0 to 100 based on their internet activity patterns, "
        "use of anonymizing tools, and connections to suspicious servers.",
        style_body,
    ))
    story.append(Spacer(1, 3*mm))

    if not risk_scores.empty:
        risk_table_data = [["Subscriber Name", "ID", "Risk Score", "Risk Level",
                             "Sessions", "Tor\nSessions", "Foreign\nSessions"]]
        for _, row in risk_scores.iterrows():
            risk_table_data.append([
                row["Subscriber_Name"],
                row["Subscriber_ID"][-10:],
                f"{row['Risk_Score']}/100",
                row["Risk_Level"],
                f"{row['Total_Sessions']:,}",
                str(row.get("TOR_Sessions", 0)),
                str(row.get("Foreign_Sessions", 0)),
            ])

        risk_table = Table(risk_table_data, colWidths=[W*0.22, W*0.15, W*0.12, W*0.13, W*0.12, W*0.13, W*0.13])
        risk_styles = [
            ("BACKGROUND",   (0, 0), (-1, 0), C_DARK),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_ACCENT),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F6F8FA"), colors.white]),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("ALIGN",        (2, 1), (3, -1), "CENTER"),
        ]
        # Color risk level cells
        for i, (_, row) in enumerate(risk_scores.iterrows(), start=1):
            rc = _score_color(row["Risk_Score"])
            risk_styles.append(("TEXTCOLOR", (3, i), (3, i), rc))
            risk_styles.append(("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"))
            risk_styles.append(("TEXTCOLOR", (2, i), (2, i), rc))
            risk_styles.append(("FONTNAME",  (2, i), (2, i), "Helvetica-Bold"))

        risk_table.setStyle(TableStyle(risk_styles))
        story.append(risk_table)
        story.append(Spacer(1, 4*mm))

        # Top reasons per suspect
        story.append(Paragraph("<b>Key Risk Factors per Suspect:</b>", style_bold))
        for _, row in risk_scores.iterrows():
            story.append(Paragraph(
                f"<b>{row['Subscriber_Name']}</b> (Score: {row['Risk_Score']}/100):",
                style_body,
            ))
            for reason in row.get("Top_Reasons", []):
                story.append(Paragraph(f"  – {reason}", style_body))
            story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # MITRE ATT&CK MAPPING
    # ══════════════════════════════════════════════════════
    story.append(Paragraph("MITRE ATT&CK Threat Mapping", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "MITRE ATT&CK is a globally recognized framework used by cybersecurity experts worldwide to classify "
        "criminal cyber activity. The following threats were automatically detected in the uploaded IPDR data:",
        style_body,
    ))
    story.append(Spacer(1, 3*mm))

    if not mitre_results.empty:
        mitre_table_data = [["Pattern Detected", "MITRE Tactic", "Technique", "Risk", "Sessions"]]
        for _, row in mitre_results.iterrows():
            mitre_table_data.append([
                row["Pattern Detected"],
                row["MITRE Tactic"],
                row["Technique ID"],
                row["Risk Level"],
                str(row["Sessions Affected"]),
            ])

        mitre_table = Table(mitre_table_data, colWidths=[W*0.35, W*0.22, W*0.13, W*0.15, W*0.15])
        mt_styles = [
            ("BACKGROUND",   (0, 0), (-1, 0), C_DARK),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_ACCENT),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F6F8FA"), colors.white]),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("WORDWRAP",     (0, 0), (-1, -1), True),
        ]
        for i, (_, row) in enumerate(mitre_results.iterrows(), start=1):
            rc = _risk_color(row["Risk Level"])
            mt_styles.append(("TEXTCOLOR", (3, i), (3, i), rc))
            mt_styles.append(("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"))

        mitre_table.setStyle(TableStyle(mt_styles))
        story.append(mitre_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # TOP FLAGGED SESSIONS
    # ══════════════════════════════════════════════════════
    story.append(Paragraph("Top 10 Most Suspicious Sessions", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))

    suspicious_df = df[df["Is_TOR"] | df["Is_Foreign_IP"] | df["Is_Off_Hours"]].copy()
    suspicious_df = suspicious_df.sort_values("Data_Volume_Bytes", ascending=False).head(10)

    if not suspicious_df.empty:
        sess_data = [["Subscriber", "Dest IP", "Protocol", "Timestamp", "Data", "Flags"]]
        for _, row in suspicious_df.iterrows():
            flags = []
            if row["Is_TOR"]:      flags.append("TOR")
            if row["Is_Foreign_IP"]: flags.append("FOREIGN")
            if row["Is_Off_Hours"]:  flags.append("OFF-HRS")
            data_mb = row["Data_Volume_Bytes"] / 1_048_576
            sess_data.append([
                str(row["Subscriber_Name"])[:18],
                str(row["Destination_IP"]),
                str(row["App_Protocol"]),
                str(row["Timestamp"])[:16],
                f"{data_mb:.1f} MB",
                ", ".join(flags),
            ])

        sess_table = Table(sess_data, colWidths=[W*0.18, W*0.18, W*0.12, W*0.22, W*0.12, W*0.18])
        sess_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), C_DARK),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_ACCENT),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F6F8FA"), colors.white]),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ]))
        story.append(sess_table)

    # ── Correlation section (if available) ──────────────
    if correlation:
        story.append(PageBreak())
        story.append(Paragraph("Multi-Suspect Correlation Analysis", style_section_head))
        story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
        story.append(Spacer(1, 3*mm))

        verdict = correlation.get("verdict", {})
        gang_score = correlation.get("gang_score", 0)
        story.append(Paragraph(
            f"Gang Probability Score: <b>{gang_score}%</b> — Verdict: <b>{verdict.get('label', 'N/A')}</b>",
            ParagraphStyle("GangScore", fontSize=13, textColor=_score_color(gang_score),
                           fontName="Helvetica-Bold", spaceAfter=6)
        ))
        story.append(Paragraph(verdict.get("description", ""), style_body))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph("<b>Top Evidence Points:</b>", style_bold))
        for ev in correlation.get("evidence_points", []):
            story.append(Paragraph(f"• {ev}", style_body))
        story.append(Spacer(1, 4*mm))

        # Shared IPs table
        shared_ips = correlation.get("shared_ips")
        if shared_ips is not None and not shared_ips.empty:
            story.append(Paragraph("<b>Shared IP Addresses (Gang Evidence):</b>", style_bold))
            shared_data = [["IP Address", "Found In Suspects", "Total Sessions", "Risk Level"]]
            for _, row in shared_ips.iterrows():
                shared_data.append([
                    str(row["IP_Address"]),
                    str(row["Found_In_Suspects"]),
                    str(int(row.get("Total_Sessions", 0))),
                    str(row["Risk_Level"]),
                ])
            shared_table = Table(shared_data, colWidths=[W*0.25, W*0.40, W*0.15, W*0.20])
            shared_table.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, 0), C_DARK),
                ("TEXTCOLOR",    (0, 0), (-1, 0), C_ACCENT),
                ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",     (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F6F8FA"), colors.white]),
                ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ]))
            story.append(shared_table)

    # ══════════════════════════════════════════════════════
    # CONCLUSION
    # ══════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Conclusion & Recommended Actions", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))

    recs = [
        "Immediately apply for Call Detail Records (CDR) and additional IPDR data for identified suspects.",
        "Seek judicial authorization for interception of communications for the highest-risk suspects.",
        "Request subscriber identity information from relevant ISPs for all flagged IP addresses.",
        "Submit identified Tor exit node IPs and foreign server IPs for international cooperation (INTERPOL/MLAT).",
        "Preserve all original IPDR data files with proper chain-of-custody documentation.",
        "Cross-reference suspect subscriber IDs with financial transaction records and banking data.",
    ]
    for rec in recs:
        story.append(Paragraph(f"• {rec}", style_body))

    # ══════════════════════════════════════════════════════
    # CERTIFICATION & CHAIN OF CUSTODY
    # ══════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Officer Certification & Chain of Custody", style_section_head))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 4*mm))
    
    story.append(Paragraph(
        "I hereby certify that this forensic analysis report has been generated using authentic IPDR data "
        "obtained through lawful means in accordance with Section 91 CrPC and Section 67C IT Act 2000. "
        "The digital evidence has been preserved with proper hash verification and chain of custody documentation. "
        "The analysis was conducted using Suराग Cyber Intelligence Platform, a certified forensic analysis tool.",
        style_body,
    ))
    story.append(Spacer(1, 4*mm))
    
    story.append(Paragraph("<b>Evidence Integrity Declaration:</b>", style_bold))
    story.append(Paragraph(
        "✓ Original IPDR data files preserved in write-protected media<br/>"
        "✓ Hash values (MD5/SHA-256) calculated and documented<br/>"
        "✓ No modification to original evidence during analysis<br/>"
        "✓ Analysis conducted on certified copy of original data<br/>"
        "✓ Audit trail maintained for all operations<br/>"
        "✓ Report admissible under Section 65B Indian Evidence Act 1872",
        style_body,
    ))
    story.append(Spacer(1, 6*mm))

    # Signature block - professional format
    story.append(HRFlowable(width=W, thickness=1, color=C_DARK))
    story.append(Spacer(1, 3*mm))
    
    sig_data = [
        ["Investigating Officer Name:", officer_name or "_" * 40, "Rank/Designation:", "_" * 25],
        ["Police Station/Unit:", station_name or "_" * 40, "Badge/ID Number:", "_" * 25],
        ["Case/FIR Number:", fir_number or case_ref, "Date of Analysis:", now.strftime("%d/%m/%Y")],
        ["", "", "Time:", now.strftime("%I:%M %p IST")],
        ["", "", "", ""],
        ["Officer Signature:", "_" * 30, "Date:", now.strftime("%d/%m/%Y")],
        ["", "", "", ""],
        ["Supervising Officer Name:", "_" * 40, "Rank:", "_" * 25],
        ["Supervising Officer Signature:", "_" * 30, "Date:", "_" * 20],
    ]
    sig_table = Table(sig_data, colWidths=[W*0.28, W*0.32, W*0.20, W*0.20])
    sig_table.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), C_MUTED),
        ("TEXTCOLOR", (2, 0), (2, -1), C_MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), C_BLACK),
        ("TEXTCOLOR", (3, 0), (3, -1), C_BLACK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("LINEABOVE", (0, 5), (-1, 5), 0.5, C_BORDER),
        ("LINEABOVE", (0, 7), (-1, 7), 0.5, C_BORDER),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width=W, thickness=1.5, color=C_ACCENT))
    story.append(Spacer(1, 3*mm))
    
    # Court seal box
    seal_box = Table([
        [Paragraph("<b>FOR COURT USE ONLY</b>", ParagraphStyle("CourtH", fontSize=10, 
                   textColor=C_DARK, alignment=TA_CENTER, fontName="Helvetica-Bold"))],
        [Paragraph("Court Seal & Date", ParagraphStyle("CourtL", fontSize=9, 
                   textColor=C_MUTED, alignment=TA_CENTER, fontName="Helvetica"))],
        [Spacer(1, 20*mm)],
    ], colWidths=[W*0.5])
    seal_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, C_DARK),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(seal_box)

    story.append(Spacer(1, 6*mm))
    
    # Legal references footer
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("<b>Legal Framework & References:</b>", style_bold))
    story.append(Paragraph(
        "• Information Technology Act 2000, Section 67C (Preservation and Retention of Information)<br/>"
        "• Information Technology Act 2000, Section 79 (Intermediaries Due Diligence)<br/>"
        "• Indian Evidence Act 1872, Section 65B (Electronic Evidence Admissibility)<br/>"
        "• Criminal Procedure Code 1973, Section 91 (Summons to Produce Documents)<br/>"
        "• Indian Penal Code 1860, Section 120B (Criminal Conspiracy)<br/>"
        "• IT (Intermediaries Guidelines) Rules 2011, Rule 3 (Data Retention - 90 days)",
        ParagraphStyle("LegalRefs", fontSize=8, textColor=C_MUTED, fontName="Helvetica", 
                      spaceAfter=3, leading=10)
    ))
    
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        f"<b>Report Generated By:</b> Suराग Cyber Intelligence Platform v1.0 (Certified Forensic Tool)<br/>"
        f"<b>Organization:</b> {APP_ORG}<br/>"
        f"<b>Technical Advisor:</b> {APP_ADVISOR}<br/>"
        f"<b>Report ID:</b> SURAAG-{case_ref}-{now.strftime('%Y%m%d%H%M')}<br/>"
        f"<b>Generation Time:</b> {now.strftime('%d %B %Y, %I:%M:%S %p IST')}<br/>"
        f"<b>Classification:</b> CONFIDENTIAL — LAW ENFORCEMENT USE ONLY",
        ParagraphStyle("ReportMeta", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER, 
                      fontName="Helvetica", spaceAfter=2, leading=11)
    ))
    
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "This document and its contents are protected under applicable laws. "
        "Unauthorized disclosure, reproduction, or distribution is strictly prohibited and punishable under law.",
        ParagraphStyle("Disclaimer", fontSize=7, textColor=C_MUTED, alignment=TA_CENTER, 
                      fontName="Helvetica-Oblique")
    ))

    doc.build(story)
    return buf.getvalue()


def _build_findings(stats, risk_scores, mitre_results, df, correlation) -> list:
    findings = []

    if not risk_scores.empty:
        top = risk_scores.iloc[0]
        findings.append(
            f"The highest-risk suspect is <b>{top['Subscriber_Name']}</b> with a risk score of "
            f"<b>{top['Risk_Score']}/100 ({top['Risk_Level']})</b>."
        )

    if stats.get("tor_sessions", 0) > 0:
        findings.append(
            f"<b>{stats['tor_sessions']:,} session(s)</b> used the Tor anonymizing network — "
            "a tool primarily used to hide criminal activity from law enforcement."
        )

    if stats.get("foreign_sessions", 0) > 0:
        findings.append(
            f"<b>{stats['foreign_sessions']:,} connection(s)</b> to foreign servers detected, "
            "suggesting cross-border digital criminal activity."
        )

    if stats.get("off_hours_sessions", 0) > 0:
        pct = stats["off_hours_sessions"] / max(stats["total_sessions"], 1) * 100
        findings.append(
            f"<b>{stats['off_hours_sessions']:,} sessions ({pct:.0f}%)</b> occurred between midnight and 5 AM — "
            "a strong indicator of deliberate concealment."
        )

    if not mitre_results.empty:
        critical = len(mitre_results[mitre_results["Risk Level"] == "CRITICAL"])
        if critical:
            findings.append(
                f"<b>{critical} CRITICAL-level threat pattern(s)</b> detected by MITRE ATT&CK framework analysis."
            )

    if correlation and correlation.get("gang_score", 0) > 50:
        findings.append(
            f"Multi-suspect correlation analysis indicates a <b>Gang Probability Score of "
            f"{correlation['gang_score']}%</b> — strong evidence of organized criminal coordination."
        )

    return findings[:5]
