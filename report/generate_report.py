"""
SAMA Counter Fraud Data Quality Report Generator
Author: Gayasuddin
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import json, os

# Load scorecard
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(f'{base}/report/dq_scorecard.json') as f:
    sc = json.load(f)

doc = SimpleDocTemplate(
    f'{base}/report/SAMA_Fraud_DQ_Report_Gayasuddin.pdf',
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

# Colors
DARK_NAVY  = colors.HexColor('#0d1b2e')
MID_BLUE   = colors.HexColor('#1a3a5c')
ACCENT_BLUE= colors.HexColor('#1e88e5')
RED_ALERT  = colors.HexColor('#c62828')
GREEN_OK   = colors.HexColor('#2e7d32')
YELLOW_W   = colors.HexColor('#f9a825')
LIGHT_GRAY = colors.HexColor('#f5f7fa')
MED_GRAY   = colors.HexColor('#e0e0e0')
WHITE      = colors.white
TEXT_DARK  = colors.HexColor('#1a1a2e')

styles = getSampleStyleSheet()
story  = []

def h1(text):
    return Paragraph(text, ParagraphStyle('H1', fontSize=20, fontName='Helvetica-Bold',
        textColor=WHITE, spaceAfter=4, spaceBefore=4, alignment=TA_CENTER))

def h2(text):
    return Paragraph(text, ParagraphStyle('H2', fontSize=13, fontName='Helvetica-Bold',
        textColor=DARK_NAVY, spaceAfter=6, spaceBefore=12,
        borderPad=4, leftIndent=0))

def h3(text):
    return Paragraph(text, ParagraphStyle('H3', fontSize=10, fontName='Helvetica-Bold',
        textColor=MID_BLUE, spaceAfter=4, spaceBefore=8))

def body(text):
    return Paragraph(text, ParagraphStyle('Body', fontSize=9, fontName='Helvetica',
        textColor=TEXT_DARK, spaceAfter=4, leading=14))

def section_divider():
    return HRFlowable(width='100%', thickness=1, color=MED_GRAY, spaceAfter=8, spaceBefore=4)

# ── COVER ────────────────────────────────────────────────────
cover_table = Table([[
    Paragraph('<b>🛡️ SAMA Counter Fraud</b>', ParagraphStyle('CT', fontSize=22,
        fontName='Helvetica-Bold', textColor=WHITE, alignment=TA_CENTER)),
]], colWidths=[17*cm])
cover_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), DARK_NAVY),
    ('TOPPADDING', (0,0), (-1,-1), 30),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('ROUNDEDCORNERS', [8]),
]))
story.append(cover_table)
story.append(Spacer(1, 0.3*cm))

sub_table = Table([[
    Paragraph('Data Quality & Fraud Analytics Report', ParagraphStyle('ST', fontSize=14,
        fontName='Helvetica', textColor=MID_BLUE, alignment=TA_CENTER)),
]], colWidths=[17*cm])
sub_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
]))
story.append(sub_table)
story.append(Spacer(1, 0.3*cm))

meta_data = [
    ['Report Date:', sc['report_date'],    'Prepared by:', 'Gayasuddin'],
    ['Dataset Period:', '2024-01-01 – 2024-12-30', 'Role Target:', 'Counter Fraud – Data Quality Specialist'],
    ['Institution:', 'Saudi Digital Bank (Simulated)', 'Regulation:', 'SAMA Counter Fraud Framework'],
]
meta_table = Table(meta_data, colWidths=[4*cm, 6*cm, 3.5*cm, 3.5*cm])
meta_table.setStyle(TableStyle([
    ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE',    (0,0), (-1,-1), 8.5),
    ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',    (2,0), (2,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR',   (0,0), (0,-1), MID_BLUE),
    ('TEXTCOLOR',   (2,0), (2,-1), MID_BLUE),
    ('GRID',        (0,0), (-1,-1), 0.5, MED_GRAY),
    ('BACKGROUND',  (0,0), (-1,-1), LIGHT_GRAY),
    ('TOPPADDING',  (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(meta_table)
story.append(Spacer(1, 0.4*cm))

# ── SECTION 1: EXECUTIVE SUMMARY ─────────────────────────────
story.append(h2("1. Executive Summary"))
story.append(section_divider())

story.append(body(
    "This report presents a comprehensive fraud data quality assessment for a Saudi digital banking institution. "
    "The analysis covers 50,000 transactions across full-year 2024, applying SAMA-aligned validation, "
    "deduplication, anomaly detection, and regulatory reporting frameworks. "
    "The overall Data Quality Score is <b>98.1%</b>, with key action items identified."
))

# KPI Cards
kpi_data = [
    ['Total Records', 'Fraud Cases', 'DQ Score', 'Unreported (SAMA)'],
    [f"{sc['total_records']:,}", f"1,750 (3.5%)", f"98.1%", f"{sc['unreported_to_sama']}"],
    ['', '', '🟢 Acceptable', '⚠ Action Required'],
    ['Duplicates Found', 'Null Account Nos', 'Anomalies (Z>3σ)', 'Mule Flags'],
    [f"{sc['duplicate_records']:,} (1.0%)", f"{sc['null_account_numbers']:,} (1.6%)",
     f"{sc['anomalous_transactions']}", f"{sc['mule_account_flags']}"],
    ['🟡 Medium Risk', '🔴 High Risk', '🟡 Investigate', '🔴 Escalate'],
]
kpi_table = Table(kpi_data, colWidths=[4.25*cm]*4)
kpi_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE',     (0,0), (-1,-1), 8.5),
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',     (0,3), (-1,3), 'Helvetica-Bold'),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('TEXTCOLOR',    (0,3), (-1,3), WHITE),
    ('BACKGROUND',   (0,0), (-1,0), DARK_NAVY),
    ('BACKGROUND',   (0,3), (-1,3), MID_BLUE),
    ('BACKGROUND',   (0,1), (-1,2), LIGHT_GRAY),
    ('BACKGROUND',   (0,4), (-1,5), colors.HexColor('#eef2f7')),
    ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('TOPPADDING',   (0,0), (-1,-1), 7),
    ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ('FONTSIZE',     (0,1), (-1,1), 12),
    ('FONTNAME',     (0,1), (-1,1), 'Helvetica-Bold'),
    ('TEXTCOLOR',    (0,1), (-1,1), DARK_NAVY),
    ('FONTSIZE',     (0,4), (-1,4), 12),
    ('FONTNAME',     (0,4), (-1,4), 'Helvetica-Bold'),
    ('TEXTCOLOR',    (0,4), (-1,4), DARK_NAVY),
]))
story.append(kpi_table)
story.append(Spacer(1, 0.4*cm))

# ── SECTION 2: DATA QUALITY FINDINGS ─────────────────────────
story.append(h2("2. Data Quality Assessment"))
story.append(section_divider())

story.append(h3("2.1 Completeness Analysis"))
story.append(body("Null/missing value audit across all 16 fields in the fraud transaction dataset:"))

completeness_data = [
    ['Field', 'Null Count', 'Null %', 'Severity', 'Recommended Action'],
    ['fraud_type', '48,250', '96.5%', 'INFO', 'Expected (non-fraud records only)'],
    ['device_id', '2,581', '5.16%', 'MEDIUM', 'Enhance mobile event capture'],
    ['ip_address', '1,957', '3.91%', 'MEDIUM', 'Mandatory for CNP transactions'],
    ['merchant_category', '1,000', '2.00%', 'HIGH', 'Required for typology mapping'],
    ['account_number', '800', '1.60%', 'HIGH', 'Critical – mandatory for SAMA reporting'],
]
comp_table = Table(completeness_data, colWidths=[3.8*cm, 2.2*cm, 1.8*cm, 2.2*cm, 7*cm])
comp_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 8),
    ('BACKGROUND',   (0,0), (-1,0), MID_BLUE),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('ALIGN',        (2,0), (3,-1), 'CENTER'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING',  (0,0), (-1,-1), 6),
    ('TEXTCOLOR',    (3,2), (3,3), YELLOW_W),
    ('TEXTCOLOR',    (3,4), (3,5), RED_ALERT),
    ('FONTNAME',     (3,2), (3,-1), 'Helvetica-Bold'),
]))
story.append(comp_table)
story.append(Spacer(1, 0.3*cm))

story.append(h3("2.2 Deduplication Results"))
dedup_data = [
    ['Metric', 'Count', 'Rate', 'Status'],
    ['Total Records Ingested', '50,000', '100%', '—'],
    ['Exact Duplicate Transaction IDs', '499', '1.00%', '🟡 Flagged'],
    ['Near-Duplicates (Same Cust+Amt, <60s)', '0', '0%', '🟢 Clean'],
    ['Records After Deduplication', '49,501', '99.0%', '🟢 Clean'],
]
dedup_table = Table(dedup_data, colWidths=[7*cm, 2.8*cm, 2.8*cm, 4.4*cm])
dedup_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 8.5),
    ('BACKGROUND',   (0,0), (-1,0), MID_BLUE),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('ALIGN',        (1,0), (-1,-1), 'CENTER'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',   (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING',  (0,0), (-1,-1), 6),
]))
story.append(dedup_table)
story.append(Spacer(1, 0.3*cm))

# ── SECTION 3: FRAUD ANALYTICS ───────────────────────────────
story.append(h2("3. Fraud Analytics & Trend Analysis"))
story.append(section_divider())

story.append(h3("3.1 Fraud Typology Breakdown (SAMA Categories)"))
typology_data = [
    ['Fraud Typology', 'Cases', 'Total Value (SAR)', 'Avg Value (SAR)', 'Share %'],
    ['Card-Not-Present (CNP)', '374', '1,227,721', '3,283', '21.4%'],
    ['Account Takeover (ATO)', '362', '720,937', '1,992', '20.7%'],
    ['Identity Theft', '334', '1,307,345', '3,914', '19.1%'],
    ['Mule Account Activity', '334', '1,007,461', '3,016', '19.1%'],
    ['Phishing', '346', '708,796', '2,049', '19.7%'],
    ['TOTAL', '1,750', '4,972,260', '2,841', '100%'],
]
typ_table = Table(typology_data, colWidths=[4.5*cm, 2*cm, 3.5*cm, 3.5*cm, 2.5*cm])
typ_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',     (0,-1), (-1,-1), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 8.5),
    ('BACKGROUND',   (0,0), (-1,0), DARK_NAVY),
    ('BACKGROUND',   (0,-1), (-1,-1), colors.HexColor('#e8eaf6')),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('ALIGN',        (1,0), (-1,-1), 'CENTER'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-2), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',   (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING',  (0,0), (-1,-1), 6),
]))
story.append(typ_table)
story.append(Spacer(1, 0.3*cm))

story.append(h3("3.2 Anomaly Detection – Z-Score Analysis"))
story.append(body(
    "Statistical anomaly detection was applied using Z-Score on completed transaction amounts. "
    "Transactions with |Z| > 3σ were flagged as anomalous. "
    "<b>94 anomalous transactions</b> were identified with a combined value of <b>SAR 27.9M</b>. "
    "The fraud rate among anomalies (7.4%) is 2x the baseline rate (3.5%), validating this approach."
))

anomaly_data = [
    ['Metric', 'Value'],
    ['Mean Transaction Amount', 'SAR 2,477.55'],
    ['Standard Deviation', 'SAR 19,945.06'],
    ['Anomaly Threshold', '|Z-Score| > 3σ'],
    ['Anomalous Transactions', '94'],
    ['Fraud Among Anomalies', '7 cases (7.4% — 2x baseline)'],
    ['Total Anomaly Value', 'SAR 27,917,671.68'],
    ['Recommendation', 'Auto-route to manual review queue'],
]
anom_table = Table(anomaly_data, colWidths=[6*cm, 11*cm])
anom_table.setStyle(TableStyle([
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8.5),
    ('BACKGROUND',  (0,0), (-1,0), MID_BLUE),
    ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
    ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR',   (0,1), (0,-1), MID_BLUE),
    ('GRID',        (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',  (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(anom_table)
story.append(Spacer(1, 0.3*cm))

# ── SECTION 4: SAMA REGULATORY ───────────────────────────────
story.append(h2("4. SAMA Regulatory Reporting"))
story.append(section_divider())

alert_table = Table([[
    Paragraph('⚠ REGULATORY ACTION REQUIRED', ParagraphStyle('Alert', fontSize=10,
        fontName='Helvetica-Bold', textColor=WHITE)),
    Paragraph(
        f'<b>{sc["unreported_to_sama"]} confirmed fraud cases</b> (SAR 939,088.87) have not been reported to SAMA. '
        'Per SAMA Counter Fraud Framework, these must be submitted within the <b>72-hour mandatory window</b>.',
        ParagraphStyle('AlertBody', fontSize=8.5, fontName='Helvetica', textColor=WHITE, leading=13))
]], colWidths=[5*cm, 12*cm])
alert_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), RED_ALERT),
    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 10),
    ('BOTTOMPADDING',(0,0), (-1,-1), 10),
    ('LEFTPADDING',(0,0), (-1,-1), 10),
    ('ROUNDEDCORNERS', [4]),
]))
story.append(alert_table)
story.append(Spacer(1, 0.3*cm))

story.append(h3("4.1 Monthly Fraud Report (SAMA Format)"))
monthly_data = [
    ['Month', 'Total Txns', 'Fraud Cases', 'Fraud Value (SAR)', 'Fraud Rate', 'SAMA Reported'],
    ['Jan 2024', '4,161', '147', '419,077', '3.53%', '110 (75%)'],
    ['Feb 2024', '4,089', '145', '190,521', '3.55%', '109 (75%)'],
    ['Mar 2024', '4,151', '132', '786,201', '3.18%', '99 (75%)'],
    ['Apr 2024', '4,003', '128', '126,308', '3.20%', '96 (75%)'],
    ['May 2024', '4,195', '136', '180,633', '3.24%', '102 (75%)'],
    ['Jun 2024', '4,118', '148', '170,740', '3.59%', '111 (75%)'],
    ['Jul 2024', '4,123', '139', '152,096', '3.37%', '104 (75%)'],
    ['Aug 2024', '4,259', '152', '604,242', '3.57%', '114 (75%)'],
    ['Sep 2024', '4,130', '146', '532,809', '3.54%', '110 (75%)'],
    ['Oct 2024', '4,247', '152', '485,009', '3.58%', '114 (75%)'],
    ['Nov 2024', '4,039', '147', '178,156', '3.64%', '110 (75%)'],
    ['Dec 2024', '3,986', '160', '1,132,782', '4.01%', '120 (75%)'],
    ['TOTAL',    '49,501', '1,732', '4,958,574', '3.50%', '1,299 (75%)'],
]
monthly_table = Table(monthly_data, colWidths=[2.8*cm, 2.5*cm, 2.5*cm, 3.5*cm, 2.5*cm, 3.2*cm])
monthly_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',     (0,-1), (-1,-1), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 7.5),
    ('BACKGROUND',   (0,0), (-1,0), DARK_NAVY),
    ('BACKGROUND',   (0,-1), (-1,-1), colors.HexColor('#e8eaf6')),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('ALIGN',        (1,0), (-1,-1), 'CENTER'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-2), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
]))
story.append(monthly_table)
story.append(Spacer(1, 0.4*cm))

# ── SECTION 5: RECOMMENDATIONS ───────────────────────────────
story.append(h2("5. Recommendations & Action Plan"))
story.append(section_divider())

rec_data = [
    ['Priority', 'Issue', 'Recommended Action', 'Owner', 'Timeline'],
    ['🔴 HIGH', 'SAMA Unreported Fraud', 'Submit 430 cases via SAMA portal immediately', 'Compliance/MLRO', '72 hrs'],
    ['🔴 HIGH', 'Missing account numbers', 'Add mandatory field validation at source', 'Data Engineering', '1 week'],
    ['🟡 MED', 'Duplicate tx records', 'Implement dedup at ETL ingestion layer', 'Data Management', '2 weeks'],
    ['🟡 MED', 'Missing IP/device data', 'Enforce capture in mobile SDK & API gateway', 'Engineering', '2 weeks'],
    ['🟡 MED', 'High-risk non-fraud records', 'Review risk scoring model threshold calibration', 'Fraud Analytics', '1 month'],
    ['🟢 LOW', 'Anomaly routing', 'Auto-flag |Z|>3σ transactions to manual review', 'Fraud Ops', '1 month'],
    ['🟢 LOW', 'Mule detection', 'Implement network graph analysis for linked accounts', 'Data Science', '2 months'],
]
rec_table = Table(rec_data, colWidths=[1.8*cm, 4*cm, 5.5*cm, 2.7*cm, 2.5*cm])
rec_table.setStyle(TableStyle([
    ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',     (0,0), (-1,-1), 7.5),
    ('BACKGROUND',   (0,0), (-1,0), DARK_NAVY),
    ('TEXTCOLOR',    (0,0), (-1,0), WHITE),
    ('ALIGN',        (0,0), (0,-1), 'CENTER'),
    ('ALIGN',        (3,0), (-1,-1), 'CENTER'),
    ('GRID',         (0,0), (-1,-1), 0.5, MED_GRAY),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING',  (0,0), (-1,-1), 5),
    ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(rec_table)

# ── FOOTER ───────────────────────────────────────────────────
story.append(Spacer(1, 0.5*cm))
footer_table = Table([[
    Paragraph('Prepared by: <b>Gayasuddin</b> | Counter Fraud – Data Quality Portfolio Project',
              ParagraphStyle('Footer', fontSize=8, fontName='Helvetica', textColor=colors.gray, alignment=TA_CENTER)),
]], colWidths=[17*cm])
footer_table.setStyle(TableStyle([
    ('TOPBORDER',    (0,0), (-1,-1), 1, MED_GRAY),
    ('TOPPADDING',   (0,0), (-1,-1), 8),
]))
story.append(footer_table)

doc.build(story)
print("✓ PDF Report generated: report/SAMA_Fraud_DQ_Report_Gayasuddin.pdf")
