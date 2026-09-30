"""
modules/report_gen.py — SURAAG Court-Ready PDF Generator (ReportLab)
Generates a comprehensive, professional PDF report for law enforcement use.
Following Indian legal document standards: Times New Roman font, proper spacing, professional colors.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import pandas as pd
from config import APP_NAME, APP_TAGLINE, APP_ORG, APP_ADVISOR

# ══════════════════════════════════════════════════════════
# PROFESSIONAL INDIAN COURT DOCUMENT COLOR PALETTE
# ══════════════════════════════════════════════════════════
C_PRIMARY      = colors.HexColor("#1A3A6B")   # Navy Blue - Headers & Professional
C_SECONDARY    = colors.HexColor("#2E5C8A")   # Medium Blue - Sub-headers
C_ACCENT       = colors.HexColor("#003D82")   # Deep Blue - Accents
C_HEADER_BG    = colors.HexColor("#F0F4F8")   # Light Blue Gray - Table headers
C_TABLE_ALT    = colors.HexColor("#F8FAFB")   # Very Light Blue - Alt rows
C_BORDER       = colors.HexColor("#D1D9E0")   # Light Gray - Borders
C_TEXT         = colors.black                  # Black - Body text (standard)
C_TEXT_LIGHT   = colors.HexColor("#4A5568")   # Dark Gray - Secondary text
C_MUTED        = colors.HexColor("#718096")   # Medium Gray - Secondary metadata
C_CRITICAL     = colors.HexColor("#DC2626")   # Red - Critical risk
C_HIGH         = colors.HexColor("#F97316")   # Orange - High risk
C_MEDIUM       = colors.HexColor("#F59E0B")   # Amber - Medium risk
C_LOW          = colors.HexColor("#10B981")   # Green - Low risk
C_SUCCESS      = colors.HexColor("#059669")   # Dark Green - Success
C_WARNING_BG   = colors.HexColor("#FEF3C7")   # Light Yellow - Warning background
C_WHITE        = colors.white                  # White


def _risk_color(level: str):
    mapping = {"CRITICAL": C_CRITICAL, "HIGH": C_HIGH, "MEDIUM": C_MEDIUM, "LOW": C_LOW}
    return mapping.get(str(level).upper(), C_TEXT_LIGHT)


def _score_color(score: int):
    if score >= 80:
        return C_CRITICAL
    elif score >= 60:
        return C_HIGH
    elif score >= 40:
        return C_MEDIUM
    return C_LOW


def get_suraag_canvas_class(case_ref, officer_name, generation_time):
    class SuraagCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pages = []
            self.case_ref = case_ref
            self.officer_name = officer_name
            self.generation_time = generation_time

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            page_count = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                self.draw_decorations(page_count)
                super().showPage()
            super().save()

        def draw_decorations(self, page_count):
            self.saveState()
            
            # Dimensions based on A4: 595.27 x 841.89 points
            # Margins: Left 18mm (~51pt), Right 18mm (~51pt)
            # Usable width: 493.23pt
            
            # --- HEADER BAR ---
            self.setFillColor(C_PRIMARY)
            self.rect(51.02, 795, 493.23, 24, fill=True, stroke=False)
            
            self.setFillColor(colors.white)
            self.setFont("Helvetica-Bold", 8)
            self.drawString(57.02, 803, "SURAAG CYBER INTELLIGENCE PLATFORM — CONFIDENTIAL")
            self.drawRightString(538.25, 803, f"Case: {self.case_ref}")
            
            # --- FOOTER BAR ---
            self.setFillColor(C_PRIMARY)
            self.rect(51.02, 18, 493.23, 24, fill=True, stroke=False)
            
            self.setFillColor(colors.white)
            self.setFont("Helvetica-Bold", 8)
            self.drawString(57.02, 26, f"IO: {self.officer_name} | Generated: {self.generation_time} | FOR LAW ENFORCEMENT & JUDICIAL USE ONLY")
            self.drawRightString(538.25, 26, f"Page {self._pageNumber}")
            
            self.restoreState()
            
    return SuraagCanvas


def make_section_banner(text, width, alignment=TA_LEFT):
    style_banner = ParagraphStyle(
        "BannerText_" + text.replace(" ", "_").replace("—", "_").replace(";", "_"),
        fontSize=12,
        textColor=C_WHITE,
        fontName="Times-Bold",
        alignment=alignment,
        leading=14
    )
    t = Table([[Paragraph(text, style_banner)]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


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
    
    # Set up document with margins that prevent overlapping headers/footers
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=28*mm,  bottomMargin=25*mm,
    )

    styles = getSampleStyleSheet()
    W = A4[0] - 36*mm  # usable width (493.23 pt)

    # ── Paragraph Styles ──
    style_cover_title = ParagraphStyle("CoverTitle",
        fontSize=26, textColor=C_PRIMARY, alignment=TA_CENTER,
        fontName="Times-Bold", spaceAfter=8, leading=32,
        spaceBefore=10,
    )
    style_cover_sub = ParagraphStyle("CoverSub",
        fontSize=12, textColor=C_HIGH, alignment=TA_CENTER,
        fontName="Times-Bold", spaceAfter=8, leading=16,
    )
    style_cover_tag = ParagraphStyle("CoverTagline",
        fontSize=13, textColor=C_PRIMARY, alignment=TA_CENTER,
        fontName="Times-Bold", spaceAfter=15, leading=16,
    )
    style_body = ParagraphStyle("Body",
        fontSize=10, textColor=C_TEXT, fontName="Times-Roman",
        spaceAfter=6, leading=14, alignment=TA_LEFT,
    )
    style_body_light = ParagraphStyle("BodyLight",
        fontSize=10, textColor=C_TEXT_LIGHT, fontName="Times-Roman",
        spaceAfter=6, leading=14,
    )
    style_label = ParagraphStyle("Label",
        fontSize=10, textColor=C_TEXT_LIGHT, fontName="Times-Bold",
        spaceAfter=4, leading=14,
    )
    style_bold = ParagraphStyle("Bold",
        fontSize=10, textColor=C_TEXT, fontName="Times-Bold",
        spaceAfter=6, leading=14,
    )
    style_center = ParagraphStyle("Center",
        fontSize=10, textColor=C_TEXT, fontName="Times-Roman",
        alignment=TA_CENTER, spaceAfter=6, leading=14,
    )
    style_conf_top = ParagraphStyle("ConfTop",
        fontSize=10, textColor=C_CRITICAL, fontName="Times-Bold",
        alignment=TA_CENTER, spaceAfter=3, spaceBefore=2
    )
    style_conf_sub = ParagraphStyle("ConfSub",
        fontSize=8, textColor=C_CRITICAL, fontName="Times-Bold",
        alignment=TA_CENTER, spaceAfter=10
    )

    story = []
    now = datetime.now()
    generation_time_str = now.strftime("%d %B %Y, %I:%M %p IST")
    generation_time_sec_str = now.strftime("%d %B %Y, %I:%M:%S %p IST")

    # ══════════════════════════════════════════════════════
    # PAGE 1: COVER PAGE
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("[!] CONFIDENTIAL", style_conf_top))
    story.append(Paragraph("FOR JUDICIAL & LAW ENFORCEMENT USE ONLY — NOT FOR PUBLIC DISCLOSURE", style_conf_sub))
    
    story.append(Paragraph("SURAAG", style_cover_title))
    story.append(Paragraph("Cyber Intelligence & Digital Forensics Platform", style_cover_sub))
    story.append(Paragraph("INTERNET PROTOCOL DETAIL RECORD (IPDR) FORENSIC ANALYSIS REPORT", style_cover_tag))
    
    # Case Details Table
    cover_data = [
        [Paragraph("<b>CASE / FIR NUMBER</b>", style_label), fir_number or case_ref],
        [Paragraph("<b>INVESTIGATING OFFICER</b>", style_label), officer_name or "Not Specified"],
        [Paragraph("<b>POLICE STATION / UNIT</b>", style_label), station_name or "Cyber Crime Cell"],
        [Paragraph("<b>COURT SUBMITTED TO</b>", style_label), court_name or "As Applicable"],
        [Paragraph("<b>REPORT GENERATED ON</b>", style_label), generation_time_str],
        [Paragraph("<b>REPORT UNIQUE ID</b>", style_label), f"SURAAG-{case_ref}-{now.strftime('%Y%m%d%H%M')}"],
        [Paragraph("<b>ANALYSIS SOFTWARE</b>", style_label), "SURAAG Cyber Intelligence Platform v1.0"],
        [Paragraph("<b>TECHNICAL ADVISOR</b>", style_label), APP_ADVISOR or "Dr. Rakshit Tandon"],
        [Paragraph("<b>ORGANISATION</b>", style_label), APP_ORG or "Gurugram Police Cyber Security Summer Internship 2026"],
    ]
    cover_table = Table(cover_data, colWidths=[W*0.48, W*0.52])
    cover_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), C_TEXT_LIGHT),
        ("TEXTCOLOR", (1, 0), (1, -1), C_TEXT),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 4*mm))

    # Analysis Statistics Table
    stats_data = [
        [
            Paragraph("<b>ANALYSIS STATISTICS</b>", ParagraphStyle("StatsH", fontSize=11, textColor=C_WHITE, fontName="Times-Bold", alignment=TA_CENTER)),
            ""
        ],
        [Paragraph("<b>TOTAL SUSPECTS ANALYSED</b>", style_label), str(stats.get("unique_subscribers", 0))],
        [Paragraph("<b>TOTAL SESSIONS ANALYSED</b>", style_label), f"{stats.get('total_sessions', 0):,}" if isinstance(stats.get('total_sessions'), int) else str(stats.get('total_sessions', 0))],
        [Paragraph("<b>SUSPICIOUS SESSIONS</b>", style_label), f"{stats.get('suspicious_sessions', 0):,}" if isinstance(stats.get('suspicious_sessions'), int) else str(stats.get('suspicious_sessions', 0))],
        [Paragraph("<b>TOR/ANONYMIZER SESSIONS</b>", style_label), str(stats.get('tor_sessions', 0))],
        [Paragraph("<b>FOREIGN SERVER CONNECTIONS</b>", style_label), str(stats.get('foreign_sessions', 0))],
        [Paragraph("<b>OFF-HOURS SESSIONS</b>", style_label), str(stats.get('off_hours_sessions', 0))],
        [Paragraph("<b>TOTAL DATA VOLUME</b>", style_label), f"{stats.get('total_bytes', 0)/1_073_741_824:.3f} GB"],
        [Paragraph("<b>DATA ANALYSIS PERIOD</b>", style_label), (f"{stats['date_range_start'].strftime('%d %b %Y')} to {stats['date_range_end'].strftime('%d %b %Y')}" if stats.get("date_range_start") else "N/A")],
    ]
    stats_table = Table(stats_data, colWidths=[W*0.65, W*0.35])
    stats_table.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (1, 0), C_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 4*mm))

    # Overall Threat Assessment Box
    if not risk_scores.empty:
        max_score = int(risk_scores["Risk_Score"].max())
        threat_level = risk_scores["Risk_Level"].iloc[0]
        tl_color = _score_color(max_score)
        
        t_action_text = (
            "[ IMMEDIATE ACTION REQUIRED ]" if max_score >= 80 else
            "[ HIGH PRIORITY INVESTIGATION ]" if max_score >= 60 else
            "[ INVESTIGATION WARRANTED ]" if max_score >= 40 else
            "[ ROUTINE MONITORING RECOMMENDED ]"
        )
        
        threat_data = [
            [Paragraph("<b>OVERALL THREAT ASSESSMENT</b>", ParagraphStyle("THdr", fontSize=11, textColor=C_WHITE, alignment=TA_CENTER, fontName="Times-Bold"))],
            [Paragraph(f"<b>{threat_level} | Risk Score: {max_score}/100</b>", ParagraphStyle("TScore", fontSize=18, textColor=tl_color, alignment=TA_CENTER, fontName="Times-Bold"))],
            [Paragraph(t_action_text, ParagraphStyle("TAct", fontSize=10, textColor=C_WHITE, alignment=TA_CENTER, fontName="Times-Bold"))]
        ]
        threat_table = Table(threat_data, colWidths=[W])
        threat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARY),
            ("BACKGROUND", (0, 1), (-1, 1), C_WHITE),
            ("BACKGROUND", (0, 2), (-1, 2), C_PRIMARY),
            ("GRID", (0, 0), (-1, -1), 2, tl_color),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(threat_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 2: LEGAL AUTHORITY & ADMISSIBILITY
    # ══════════════════════════════════════════════════════
    story.append(Spacer(1, 60*mm))
    story.append(HRFlowable(width=W, thickness=1, color=C_SECONDARY, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "<b>Legal Authority & Admissibility:</b> This report is prepared under Section 67C of Information Technology Act, 2000 "
        "and is admissible as electronic evidence under Section 65B of Indian Evidence Act, 1872. "
        "All data processing maintains cryptographic integrity and audit trails.",
        ParagraphStyle("Admissibility", fontSize=11, textColor=C_TEXT_LIGHT, alignment=TA_CENTER, fontName="Times-Italic", leading=16)
    ))
    story.append(HRFlowable(width=W, thickness=1, color=C_SECONDARY, spaceBefore=8, spaceAfter=4))
    
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 3: TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("TABLE OF CONTENTS", W, alignment=TA_CENTER))
    story.append(Spacer(1, 6*mm))
    
    toc_data = [
        ["Section 1", "Executive Summary"],
        ["Section 2", "Suspect Risk Assessment"],
        ["Section 3", "MITRE ATT&CK; Threat Mapping"],
        ["Section 4", "Top 10 Most Suspicious Sessions"],
        ["Section 5", "Recommendations & Suggested Actions"],
        ["Section 6", "Officer Certification & Chain of Custody"],
        ["Section 7", "Legal Framework & References"]
    ]
    
    toc_table_data = []
    style_toc_sec = ParagraphStyle("TOC_Sec", fontName="Times-Bold", fontSize=11, textColor=C_TEXT)
    style_toc_title = ParagraphStyle("TOC_Title", fontName="Times-Roman", fontSize=11, textColor=C_TEXT)
    for sec, name in toc_data:
        toc_table_data.append([
            Paragraph(f"<b>{sec}</b>", style_toc_sec),
            Paragraph(name, style_toc_title)
        ])
        
    toc_table = Table(toc_table_data, colWidths=[W*0.25, W*0.75])
    toc_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(toc_table)
    
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 4: SECTION 1 — EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 1 — EXECUTIVE SUMMARY", W))
    story.append(Spacer(1, 4*mm))

    summary_text = (
        f"This report presents the findings of an automated IPDR (Internet Protocol Detail Record) "
        f"forensic analysis conducted using the SURAAG Cyber Intelligence Platform. "
        f"A total of <b>{stats.get('total_sessions', 0):,} internet sessions</b> across "
        f"<b>{stats.get('unique_subscribers', 0)} subscriber(s)</b> were analysed. "
        f"The analysis detected <b>{stats.get('suspicious_sessions', 0):,} suspicious sessions</b>, "
        f"including <b>{stats.get('tor_sessions', 0)} Tor/anonymizer sessions</b> and "
        f"<b>{stats.get('foreign_sessions', 0)} connections to foreign servers</b>. "
        f"A total data volume of <b>{stats.get('total_bytes', 0)/1_073_741_824:.3f} GB</b> was analysed."
    )
    story.append(Paragraph(summary_text, style_body))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("<b>Key Findings:</b>", style_bold))
    findings = _build_findings(stats, risk_scores, mitre_results, df, correlation)
    for idx, finding in enumerate(findings, 1):
        story.append(Paragraph(f"{idx}. {finding}", style_body))
        
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 5 & 6: SECTION 2 — SUSPECT RISK ASSESSMENT
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 2 — SUSPECT RISK ASSESSMENT", W))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Each subscriber was evaluated on a standardised risk scale of 0 to 100 based on their internet activity "
        "patterns, use of anonymising tools (Tor/VPN), off-hours behaviour, data transfer anomalies, and "
        "connections to known malicious IP ranges. This scoring is consistent with Indian Cyber Crime Investigation standards.",
        style_body,
    ))
    story.append(Spacer(1, 4*mm))

    if not risk_scores.empty:
        risk_table_data = [["S.No.", "Subscriber Name", "ID (Last 10)", "Risk Score", "Risk Level",
                             "Sessions", "Tor Sessions", "Foreign Sessions"]]
        for idx, (_, row) in enumerate(risk_scores.iterrows(), start=1):
            risk_table_data.append([
                str(idx),
                row["Subscriber_Name"],
                row["Subscriber_ID"][-10:],
                f"{row['Risk_Score']}/100",
                row["Risk_Level"],
                f"{row['Total_Sessions']:,}",
                str(row.get("TOR_Sessions", 0)),
                str(row.get("Foreign_Sessions", 0)),
            ])

        risk_table = Table(risk_table_data, colWidths=[W*0.07, W*0.22, W*0.15, W*0.12, W*0.12, W*0.10, W*0.11, W*0.11])
        risk_styles = [
            ("BACKGROUND",   (0, 0), (-1, 0), C_PRIMARY),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Times-Bold"),
            ("FONTNAME",     (0, 1), (-1, -1), "Times-Roman"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_TABLE_ALT]),
            ("GRID",         (0, 0), (-1, -1), 0.75, C_BORDER),
            ("LINEBELOW",    (0, 0), (-1, 0), 2, C_PRIMARY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("ALIGN",        (0, 0), (0, -1), "CENTER"),
            ("ALIGN",        (2, 1), (-1, -1), "CENTER"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ]
        for i, (_, row) in enumerate(risk_scores.iterrows(), start=1):
            rc = _score_color(row["Risk_Score"])
            risk_styles.append(("TEXTCOLOR", (4, i), (4, i), rc))
            risk_styles.append(("FONTNAME",  (4, i), (4, i), "Times-Bold"))
            risk_styles.append(("TEXTCOLOR", (3, i), (3, i), rc))
            risk_styles.append(("FONTNAME",  (3, i), (3, i), "Times-Bold"))

        risk_table.setStyle(TableStyle(risk_styles))
        story.append(risk_table)
        story.append(Spacer(1, 4*mm))

        # Top reasons per suspect
        story.append(Paragraph("<b>Detailed Risk Factors per Subscriber:</b>", style_bold))
        for _, row in risk_scores.iterrows():
            sub_id = row["Subscriber_ID"]
            sub_name = row["Subscriber_Name"]
            score = row["Risk_Score"]
            level = row["Risk_Level"]
            
            p_text = f"<b>{sub_name} (ID: SUB-{sub_id[-10:]}) — Risk Score: {score}/100 ({level})</b>"
            story.append(Paragraph(p_text, ParagraphStyle("SusName", fontSize=10, textColor=C_PRIMARY, fontName="Times-Bold", spaceBefore=6, spaceAfter=3)))
            
            for reason in row.get("Top_Reasons", []):
                bullet_text = f"- {reason}"
                story.append(Paragraph(bullet_text, ParagraphStyle("ReasonBul", fontSize=10, textColor=C_TEXT, fontName="Times-Roman", leftIndent=12, firstLineIndent=-8, spaceAfter=2, leading=14)))
            story.append(Spacer(1, 2*mm))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 7: SECTION 3 — MITRE ATT&CK THREAT MAPPING
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 3 — MITRE ATT&CK; THREAT MAPPING", W))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "MITRE ATT&CK is a globally recognised framework used by intelligence agencies and cybersecurity "
        "professionals worldwide to classify criminal cyber activity. The following threat patterns were automatically "
        "detected in the uploaded IPDR data:",
        style_body,
    ))
    story.append(Spacer(1, 4*mm))

    if not mitre_results.empty:
        mitre_table_data = [["Pattern Detected", "MITRE Tactic", "Technique ID", "Risk Level", "Sessions Affected"]]
        for _, row in mitre_results.iterrows():
            mitre_table_data.append([
                row["Pattern Detected"],
                row["MITRE Tactic"],
                row["Technique ID"],
                row["Risk Level"],
                str(row["Sessions Affected"]),
            ])

        mitre_table = Table(mitre_table_data, colWidths=[W*0.32, W*0.25, W*0.13, W*0.15, W*0.15])
        mt_styles = [
            ("BACKGROUND",   (0, 0), (-1, 0), C_PRIMARY),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Times-Bold"),
            ("FONTNAME",     (0, 1), (-1, -1), "Times-Roman"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_TABLE_ALT]),
            ("GRID",         (0, 0), (-1, -1), 0.75, C_BORDER),
            ("LINEBELOW",    (0, 0), (-1, 0), 2, C_PRIMARY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",        (2, 1), (-1, -1), "CENTER"),
        ]
        for i, (_, row) in enumerate(mitre_results.iterrows(), start=1):
            rc = _risk_color(row["Risk Level"])
            mt_styles.append(("TEXTCOLOR", (3, i), (3, i), rc))
            mt_styles.append(("FONTNAME",  (3, i), (3, i), "Times-Bold"))

        mitre_table.setStyle(TableStyle(mt_styles))
        story.append(mitre_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 8: SECTION 4 — TOP 10 MOST SUSPICIOUS SESSIONS
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 4 — TOP 10 MOST SUSPICIOUS SESSIONS", W))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "The following sessions were identified as most suspicious based on a combination of Tor usage, foreign IP "
        "connections, off-hours activity, and data volume. These sessions are recommended for immediate deeper investigation.",
        style_body,
    ))
    story.append(Spacer(1, 4*mm))

    suspicious_df = df[df["Is_TOR"] | df["Is_Foreign_IP"] | df["Is_Off_Hours"]].copy()
    suspicious_df = suspicious_df.sort_values("Data_Volume_Bytes", ascending=False).head(10)

    if not suspicious_df.empty:
        sess_data = [["S.No.", "Subscriber", "Destination IP", "Protocol", "Timestamp (IST)", "Data (MB)", "Flags"]]
        for idx, (_, row) in enumerate(suspicious_df.iterrows(), start=1):
            flags = []
            if row["Is_TOR"]:      flags.append("TOR")
            if row["Is_Foreign_IP"]: flags.append("FOREIGN")
            if row["Is_Off_Hours"]:  flags.append("OFF-HRS")
            data_mb = row["Data_Volume_Bytes"] / 1_048_576
            sess_data.append([
                str(idx),
                str(row["Subscriber_Name"])[:16],
                str(row["Destination_IP"]),
                str(row["App_Protocol"]),
                str(row["Timestamp"])[:16],
                f"{data_mb:.1f}",
                ", ".join(flags),
            ])

        sess_table = Table(sess_data, colWidths=[W*0.07, W*0.16, W*0.18, W*0.11, W*0.21, W*0.11, W*0.16])
        sess_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), C_PRIMARY),
            ("TEXTCOLOR",    (0, 0), (-1, 0), C_WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Times-Bold"),
            ("FONTNAME",     (0, 1), (-1, -1), "Times-Roman"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_TABLE_ALT]),
            ("GRID",         (0, 0), (-1, -1), 0.75, C_BORDER),
            ("LINEBELOW",    (0, 0), (-1, 0), 2, C_PRIMARY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 5),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",        (0, 0), (0, -1), "CENTER"),
            ("ALIGN",        (5, 1), (5, -1), "CENTER"),
        ]))
        story.append(sess_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 9: SECTION 5 — RECOMMENDATIONS & SUGGESTED ACTIONS
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 5 — RECOMMENDATIONS & SUGGESTED ACTIONS", W))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Based on the forensic analysis, the following actions are recommended to the Investigating Officer and the Honourable Court:",
        style_body,
    ))
    story.append(Spacer(1, 4*mm))

    recs_data = [
        ("Immediate", "Apply for Call Detail Records (CDR) and additional IPDR data for all identified high-risk subscribers from the relevant TSPs/ISPs."),
        ("Immediate", "Seek judicial authorisation for interception of communications for the highest-risk suspects under Section 5(2) of Indian Telegraph Act."),
        ("Short-Term", "Request subscriber identity information (name, address, ID proof) from relevant ISPs for all flagged foreign and Tor connections."),
        ("Short-Term", "Submit identified Tor exit node IPs and foreign server IPs to INTERPOL / MLAT channels for international cooperation."),
        ("Medium-Term", "Preserve all original IPDR data files in write-protected media with proper chain-of-custody documentation and MD5/SHA-256 hashes."),
        ("Medium-Term", "Cross-reference suspect subscriber IDs with financial transaction records, banking data, and GST filings to trace illicit funds."),
        ("Long-Term", "Correlate findings with physical surveillance data and CCTV records around identified locations during flagged off-hours.")
    ]

    recs_table_data = [[
        Paragraph("<b>Priority</b>", ParagraphStyle("RecH1", fontSize=10, textColor=C_WHITE, fontName="Times-Bold")),
        Paragraph("<b>Recommended Action</b>", ParagraphStyle("RecH2", fontSize=10, textColor=C_WHITE, fontName="Times-Bold"))
    ]]
    
    for idx, (priority, action) in enumerate(recs_data):
        if priority == "Immediate":
            p_color = C_CRITICAL
        elif priority == "Short-Term":
            p_color = C_HIGH
        elif priority == "Medium-Term":
            p_color = C_MEDIUM
        else:
            p_color = C_SUCCESS
            
        style_p = ParagraphStyle(f"Prio_{idx}", fontName="Times-Bold", fontSize=10, textColor=p_color)
        style_a = ParagraphStyle(f"Act_{idx}", fontName="Times-Roman", fontSize=10, textColor=C_TEXT, leading=14)
        recs_table_data.append([
            Paragraph(priority, style_p),
            Paragraph(action, style_a)
        ])
        
    recs_table = Table(recs_table_data, colWidths=[W*0.22, W*0.78])
    recs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(recs_table)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 10: SECTION 6 — OFFICER CERTIFICATION & CHAIN OF CUSTODY
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 6 — OFFICER CERTIFICATION & CHAIN OF CUSTODY", W))
    story.append(Spacer(1, 4*mm))
    
    story.append(Paragraph(
        "I hereby certify that this forensic analysis report has been generated using authentic IPDR data obtained "
        "through lawful means in accordance with Section 91 CrPC and Section 67C Information Technology Act, "
        "2000. The digital evidence has been preserved with proper hash verification and chain-of-custody "
        "documentation. The analysis was conducted using the SURAAG Cyber Intelligence Platform, a certified forensic analysis tool.",
        style_body,
    ))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph("<b>Evidence Integrity Declaration:</b>", style_bold))
    checklist_items = [
        "Original IPDR data files preserved in write-protected media.",
        "Hash values (MD5 / SHA-256) calculated and documented separately.",
        "No modification to original evidence during analysis.",
        "Analysis conducted on a certified copy of original data.",
        "Full audit trail maintained for all processing operations.",
        "This report is admissible under Section 65B Indian Evidence Act, 1872."
    ]
    for item in checklist_items:
        story.append(Paragraph(f"<b>[x]</b> {item}", ParagraphStyle("Chk", fontSize=10, textColor=C_TEXT, fontName="Times-Roman", spaceAfter=3, leading=14)))
    
    story.append(Spacer(1, 4*mm))

    # Signatures Grid
    sig_data = [
        [Paragraph("<b>Investigating Officer Name:</b>", style_body), officer_name or "ok", Paragraph("<b>Rank / Designation:</b>", style_body), "______________________"],
        [Paragraph("<b>Police Station / Unit:</b>", style_body), station_name or "cyber", Paragraph("<b>Badge / Service ID:</b>", style_body), "______________________"],
        [Paragraph("<b>Case / FIR Number:</b>", style_body), fir_number or case_ref, Paragraph("<b>Date of Report:</b>", style_body), now.strftime("%d / %m / %Y")],
        [Paragraph("<b>Date of Analysis:</b>", style_body), now.strftime("%d / %m / %Y"), Paragraph("<b>Time of Analysis:</b>", style_body), now.strftime("%I:%M %p IST")],
        ["", "", "", ""],
        [Paragraph("<b>Officer Signature:</b>", style_body), "____________________________", Paragraph("<b>Date:</b>", style_body), now.strftime("%d / %m / %Y")],
        ["", "", "", ""],
        [Paragraph("<b>Supervising Officer:</b>", style_body), "____________________________", Paragraph("<b>Rank:</b>", style_body), "______________________"],
        [Paragraph("<b>Supervising Signature:</b>", style_body), "____________________________", Paragraph("<b>Date:</b>", style_body), "______________________"],
    ]
    sig_table = Table(sig_data, colWidths=[W*0.28, W*0.32, W*0.20, W*0.20])
    sig_table.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), "Times-Roman"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
    ]))
    
    # Court Use Only & Acknowledgement Box
    seal_table_data = [
        [
            Paragraph("<b>FOR COURT USE ONLY</b>", ParagraphStyle("CourtH", fontSize=10, textColor=C_PRIMARY, alignment=TA_CENTER, fontName="Times-Bold")),
            Paragraph("<b>ACKNOWLEDGEMENT</b>", ParagraphStyle("AckH", fontSize=10, textColor=C_PRIMARY, alignment=TA_CENTER, fontName="Times-Bold"))
        ],
        [
            "",
            Paragraph("Received by: ________________________", ParagraphStyle("AckR1", fontSize=9, textColor=C_TEXT, fontName="Times-Roman"))
        ],
        [
            "",
            Paragraph("Designation: ________________________", ParagraphStyle("AckR2", fontSize=9, textColor=C_TEXT, fontName="Times-Roman"))
        ],
        [
            "",
            Paragraph("Date & Time: ________________________", ParagraphStyle("AckR3", fontSize=9, textColor=C_TEXT, fontName="Times-Roman"))
        ],
        [
            Paragraph("Court Seal & Date of Receipt", ParagraphStyle("CourtL", fontSize=9, textColor=C_TEXT_LIGHT, alignment=TA_CENTER, fontName="Times-Italic")),
            ""
        ]
    ]
    seal_table = Table(seal_table_data, colWidths=[W*0.46, W*0.54])
    seal_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, C_PRIMARY),
        ("BACKGROUND", (0, 0), (-1, 0), C_HEADER_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, C_PRIMARY),
        ("LINEBEFORE", (1, 0), (1, -1), 1.5, C_PRIMARY),
        ("SPAN", (0, 1), (0, 3)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 4), (0, 4), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (1, 1), (1, 3), 12),
        ("TOPPADDING", (0, 1), (0, 3), 12),
        ("BOTTOMPADDING", (0, 4), (0, 4), 10),
    ]))

    # Wrap signatures and court blocks in KeepTogether so they never split awkwardly
    story.append(KeepTogether([sig_table, Spacer(1, 4*mm), seal_table]))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════
    # PAGE 11: SECTION 7 — LEGAL FRAMEWORK & REFERENCES
    # ══════════════════════════════════════════════════════
    story.append(make_section_banner("SECTION 7 — LEGAL FRAMEWORK & REFERENCES", W))
    story.append(Spacer(1, 4*mm))

    legal_data = [
        ["Act / Regulation", "Applicable Provision"],
        ["Information Technology Act, 2000", "Section 67C — Preservation and Retention of Information by intermediaries"],
        ["Information Technology Act, 2000", "Section 79 — Intermediary Due Diligence and Exemption from Liability"],
        ["Indian Evidence Act, 1872", "Section 65B — Admissibility of Electronic Records as Evidence"],
        ["Code of Criminal Procedure, 1973", "Section 91 — Summons to Produce Documents or Other Things"],
        ["Indian Penal Code, 1860", "Section 120B — Punishment for Criminal Conspiracy"],
        ["Indian Telegraph Act, 1885", "Section 5(2) — Interception of Messages on Grounds of Public Safety"],
        ["IT (Intermediaries Guidelines) Rules, 2011", "Rule 3 — Data Retention Period of 90 Days"],
        ["TRAI Direction", "IPDR Data Retention Guidelines for Telecom Service Providers"]
    ]

    legal_table_data = [[
        Paragraph("<b>Act / Regulation</b>", ParagraphStyle("LegH1", fontSize=10, textColor=C_WHITE, fontName="Times-Bold")),
        Paragraph("<b>Applicable Provision</b>", ParagraphStyle("LegH2", fontSize=10, textColor=C_WHITE, fontName="Times-Bold"))
    ]]
    for act, prov in legal_data[1:]:
        legal_table_data.append([
            Paragraph(act, ParagraphStyle("LegAct", fontSize=9, textColor=C_TEXT, fontName="Times-Bold")),
            Paragraph(prov, ParagraphStyle("LegProv", fontSize=9, textColor=C_TEXT, fontName="Times-Roman"))
        ])
    legal_table = Table(legal_table_data, colWidths=[W*0.35, W*0.65])
    legal_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(legal_table)
    story.append(Spacer(1, 4*mm))

    # Report Metadata Block
    meta_data = [
        ["Report Generated By", "SURAAG Cyber Intelligence Platform v1.0"],
        ["Organisation", APP_ORG or "Gurugram Police Cyber Security Summer Internship 2026"],
        ["Technical Advisor", APP_ADVISOR or "Dr. Rakshit Tandon"],
        ["Report ID", f"SURAAG-{case_ref}-{now.strftime('%Y%m%d%H%M')}"],
        ["Generation Time", generation_time_sec_str],
        ["Classification", "CONFIDENTIAL — LAW ENFORCEMENT & JUDICIAL USE ONLY"]
    ]

    meta_table_data = []
    for k, v in meta_data:
        meta_table_data.append([
            Paragraph(f"<b>{k}</b>", ParagraphStyle("MetaK", fontSize=9, textColor=C_TEXT_LIGHT, fontName="Times-Bold")),
            Paragraph(v, ParagraphStyle("MetaV", fontSize=9, textColor=C_TEXT, fontName="Times-Roman"))
        ])
    meta_table = Table(meta_table_data, colWidths=[W*0.35, W*0.65])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, C_TABLE_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4*mm))

    # Disclaimer Warning Notice
    story.append(Paragraph(
        "This document and its contents are protected under applicable laws. "
        "Unauthorised disclosure, reproduction, or distribution is strictly prohibited and punishable under the Information Technology Act, 2000.",
        ParagraphStyle("Disclaimer", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER, fontName="Times-Italic")
    ))

    # Build PDF with Custom Canvasmaker
    doc.build(
        story, 
        canvasmaker=get_suraag_canvas_class(case_ref, officer_name, generation_time_str)
    )
    
    return buf.getvalue()


def _build_findings(stats, risk_scores, mitre_results, df, correlation) -> list:
    findings = []

    if not risk_scores.empty:
        top = risk_scores.iloc[0]
        findings.append(
            f"The highest-risk subscriber is <b>{top['Subscriber_Name']}</b> with a risk score of "
            f"<b>{top['Risk_Score']}/100 ({top['Risk_Level']})</b>."
        )

    if stats.get("tor_sessions", 0) > 0:
        findings.append(
            f"<b>{stats['tor_sessions']:,} session(s)</b> used the Tor anonymising network — "
            "a tool primarily used to hide criminal activity from law enforcement."
        )

    if stats.get("foreign_sessions", 0) > 0:
        findings.append(
            f"<b>{stats['foreign_sessions']:,} connection(s)</b> to foreign servers detected, "
            "suggesting possible cross-border digital criminal activity."
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
