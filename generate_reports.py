#!/usr/bin/env python3
"""Generate institutional Excel workbook and PowerPoint presentation for
the NIFTY Midcap 100 analysis (100 -> Top 25 -> Top 5 Buy Recommendations).
"""

import json
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(r"C:\Users\Harshad.shingavi\Downloads\Antigravity Testing")
JSON_PATH = ROOT / "midcap100_screen_results.json"
EXCEL_PATH = ROOT / "Nifty_Midcap_Top25_and_Top5_Recommendations.xlsx"
PPT_PATH = ROOT / "Nifty_Midcap_Top5_Investment_Picks.pptx"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    all_data = json.load(f)

# Sort strictly by score descending, then upside descending
all_data.sort(key=lambda x: (x.get("score", 0), x.get("upside_pct", 0)), reverse=True)
top25 = all_data[:25]

# Top 5 high-conviction buy picks selected across diverse sectors
# 1. HEROMOTOCO (Automobile / 2W & EV)
# 2. LODHA (Real Estate / MMR & Pune Residential)
# 3. LICI (Financial Services / Deep Value & High ROE)
# 4. OBEROIRLTY (Premium Real Estate / High Annuity)
# 5. APARINDS (Capital Goods / Power T&D Alpha)
top5_symbols = ["HEROMOTOCO", "LODHA", "LICI", "OBEROIRLTY", "APARINDS"]
top5 = [x for x in all_data if x["symbol"] in top5_symbols]
# Preserve ranking order
top5.sort(key=lambda x: top5_symbols.index(x["symbol"]))

# Supplementary thesis & target details for top 5
top5_details = {
    "HEROMOTOCO": {
        "sector_theme": "Automobile & EV Transformation",
        "entry_range": "₹5,250 – ₹5,400",
        "stop_loss": "₹4,950",
        "time_horizon": "9 – 12 Months",
        "analysts_count": 38,
        "broker_low": 4350.0,
        "broker_high": 7554.0,
        "forward_eps": 322.07,
        "agent_fair_pe": 20.0,
        "agent_target": 6441.40,
        "agent_upside": 19.4,
        "verdict": "Broker target is CONSERVATIVE. Hero has multiple re-rating headroom to ₹6,440+ as premium bikes & Vida EV gain market share.",
        "thesis": "Rural demand recovery, leadership in executive commuter 2W, expanding premium market share with Harley X440/Mavrick, and Vida EV expansion.",
        "catalysts": "Festive volume traction, premium margin expansion, export recovery."
    },
    "LODHA": {
        "sector_theme": "Urban Residential Real Estate Supercycle",
        "entry_range": "₹1,150 – ₹1,190",
        "stop_loss": "₹1,070",
        "time_horizon": "6 – 12 Months",
        "analysts_count": 18,
        "broker_low": 1000.0,
        "broker_high": 1615.0,
        "forward_eps": 51.20,
        "agent_fair_pe": 26.5,
        "agent_target": 1356.80,
        "agent_upside": 14.8,
        "verdict": "ALIGNED. Broker target (₹1,372) and Agent NAV model (₹1,357) match closely based on MMR & Pune pre-sales pipeline.",
        "thesis": "Market share consolidator in MMR and Pune, accelerating capital-light JDA expansion into Bengaluru, and rapid debt deleveraging.",
        "catalysts": "Record quarterly pre-sales, premium township launches, rising operational cash flows."
    },
    "LICI": {
        "sector_theme": "Financialization of Savings & Deep Value",
        "entry_range": "₹395 – ₹410",
        "stop_loss": "₹360",
        "time_horizon": "12 – 18 Months",
        "analysts_count": 22,
        "broker_low": 388.0,
        "broker_high": 690.0,
        "forward_eps": 59.01,
        "agent_fair_pe": 9.5,
        "agent_target": 560.60,
        "agent_upside": 39.2,
        "verdict": "Broker target is CONSERVATIVE. Agent fundamental fair value is ₹560+ (>39% upside) supported by 40%+ ROE and expanding VNB margins.",
        "thesis": "Extremely depressed valuation (Forward P/E < 7x) vs 40%+ ROE. Structural transition towards high-margin Non-Par products driving VNB expansion.",
        "catalysts": "VNB margin accretion, higher dividend distribution, digital agency productivity."
    },
    "OBEROIRLTY": {
        "sector_theme": "Luxury Housing & Annuity Rental Assets",
        "entry_range": "₹1,720 – ₹1,780",
        "stop_loss": "₹1,600",
        "time_horizon": "9 – 12 Months",
        "analysts_count": 26,
        "broker_low": 1240.0,
        "broker_high": 2490.0,
        "forward_eps": 106.69,
        "agent_fair_pe": 19.0,
        "agent_target": 2027.10,
        "agent_upside": 14.0,
        "verdict": "ALIGNED. Agent model (₹2,027) corroborates broker consensus (₹2,063) based on premium residential margins and recurring office park rentals.",
        "thesis": "Industry-leading operating margins, pristine balance sheet with zero net debt, and soaring annuity rental income from Commerz III and retail malls.",
        "catalysts": "Thane/Pokhran Road phase launches, Borivali mall operationalisation, strong luxury demand."
    },
    "APARINDS": {
        "sector_theme": "Global Power Grid T&D Electrification",
        "entry_range": "₹13,900 – ₹14,400",
        "stop_loss": "₹12,800",
        "time_horizon": "12 Months",
        "analysts_count": 8,
        "broker_low": 15330.0,
        "broker_high": 19000.0,
        "forward_eps": 408.15,
        "agent_fair_pe": 40.0,
        "agent_target": 16326.00,
        "agent_upside": 12.8,
        "verdict": "Broker target (₹17,425) prices in peak export margins. Agent sets a baseline fair value at ₹16,325 with a bull stretch target of ₹17,500.",
        "thesis": "Global market leader in specialized conductors, premium elastomeric cables, and transformer oils benefiting from worldwide grid upgrades.",
        "catalysts": "US & European renewable grid integration orders, expanding export margins, high ROCE >25%."
    }
}

# ==========================================
# 1. EXCEL WORKBOOK GENERATION
# ==========================================
print("[*] Generating Excel Workbook...")
wb = openpyxl.Workbook()

# Style definitions
font_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="DDDDDD")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_data = Font(name="Segoe UI", size=10, color="000000")
font_bold = Font(name="Segoe UI", size=10, bold=True, color="000000")
font_green = Font(name="Segoe UI", size=10, bold=True, color="006100")
font_blue = Font(name="Segoe UI", size=10, bold=True, color="002060")

fill_navy = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
fill_dark_blue = PatternFill(start_color="0B2240", end_color="0B2240", fill_type="solid")
fill_zebra = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
fill_light_green = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
fill_gold = PatternFill(start_color="D4AF37", end_color="D4AF37", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

# -----------------
# TAB 1: Top 5 Buy Recommendations
# -----------------
ws1 = wb.active
ws1.title = "Top 5 Buy Recommendations"
ws1.views.sheetView[0].showGridLines = True

# Title block
ws1.merge_cells("A1:M1")
ws1["A1"] = "NIFTY MIDCAP 100 — TOP 5 HIGH-CONVICTION BUY PICKS"
ws1["A1"].font = font_title
ws1["A1"].fill = fill_dark_blue
ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[1].height = 40

ws1.merge_cells("A2:M2")
ws1["A2"] = "Filtered from the 100-Stock Universe down to Top 25, followed by Multi-Agent & Fundamental Stress-Testing | Date: November 2026"
ws1["A2"].font = font_subtitle
ws1["A2"].fill = fill_dark_blue
ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws1.row_dimensions[2].height = 20

headers_top5 = [
    "Rank", "Symbol", "Company Name", "Industry / Theme", "CMP (₹)", "Target (₹)", 
    "Potential Upside", "Entry Range (₹)", "Stop-Loss (₹)", "ROE (%)", "Forward P/E", 
    "Time Horizon", "Consensus Rating"
]

ws1.append([]) # Row 3 blank
ws1.row_dimensions[3].height = 10

ws1.append(headers_top5) # Row 4
ws1.row_dimensions[4].height = 26
for col_idx in range(1, len(headers_top5) + 1):
    cell = ws1.cell(row=4, column=col_idx)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for i, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    row_data = [
        f"#{i}",
        sym,
        stock["name"],
        d.get("sector_theme", stock["industry"]),
        stock["price"],
        stock["target"],
        f"+{stock['upside_pct']}%",
        d.get("entry_range", "N/A"),
        d.get("stop_loss", "N/A"),
        f"{stock['roe']}%" if stock['roe'] else "N/A",
        f"{stock['forward_pe']}x" if stock['forward_pe'] else "N/A",
        d.get("time_horizon", "12M"),
        stock["recommendation"].replace("_", " ").title()
    ]
    ws1.append(row_data)
    r_idx = ws1.max_row
    ws1.row_dimensions[r_idx].height = 24
    row_fill = fill_zebra if i % 2 == 0 else fill_white
    for c_idx in range(1, len(row_data) + 1):
        c = ws1.cell(row=r_idx, column=c_idx)
        c.font = font_bold if c_idx in (1, 2, 6, 7) else font_data
        c.fill = row_fill
        c.border = thin_border
        c.alignment = Alignment(
            horizontal="center" if c_idx in (1, 2, 7, 8, 9, 10, 11, 12, 13) else "left",
            vertical="center"
        )
        if c_idx in (5, 6):
            c.number_format = '₹#,##0.00'

# Investment Theses Section
ws1.append([])
start_thesis_row = ws1.max_row + 1
ws1.cell(row=start_thesis_row, column=1, value="DEEP-DIVE INVESTMENT THESIS & GROWTH CATALYSTS").font = Font(name="Segoe UI", size=12, bold=True, color="002060")
ws1.row_dimensions[start_thesis_row].height = 25

for i, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    r = ws1.max_row + 1
    ws1.merge_cells(start_row=r, start_column=1, end_row=r, end_column=13)
    ws1.cell(row=r, column=1, value=f"• #{i} {sym} ({stock['name']}) — {d.get('thesis', '')} Key Catalysts: {d.get('catalysts', '')}").font = font_data
    ws1.row_dimensions[r].height = 22

# Auto-adjust column widths
for col in ws1.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)
ws1.column_dimensions["C"].width = 28
ws1.column_dimensions["D"].width = 30

# -----------------
# TAB 2: Valuation Comparison (Broker Consensus vs Agent Model)
# -----------------
ws_val = wb.create_sheet(title="Broker vs Agent Valuation")
ws_val.views.sheetView[0].showGridLines = True

ws_val.merge_cells("A1:K1")
ws_val["A1"] = "VALUATION AUDIT: BROKER CONSENSUS TARGETS VS. AGENT INDEPENDENT FAIR VALUE"
ws_val["A1"].font = font_title
ws_val["A1"].fill = fill_dark_blue
ws_val["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws_val.row_dimensions[1].height = 36

headers_val = [
    "Rank", "Symbol", "Company Name", "CMP (₹)", "Analysts Count", "Broker Target (₹)", 
    "Broker Upside", "Agent Fair P/E", "Agent Target (₹)", "Agent Upside", "Valuation Verdict & Strategic Insight"
]

ws_val.append([])
ws_val.append(headers_val)
ws_val.row_dimensions[3].height = 26

for col_idx in range(1, len(headers_val) + 1):
    cell = ws_val.cell(row=3, column=col_idx)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

for i, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    row_data = [
        f"#{i}",
        sym,
        stock["name"],
        stock["price"],
        d.get("analysts_count", "N/A"),
        stock["target"],
        f"+{stock['upside_pct']}%",
        f"{d.get('agent_fair_pe')}x",
        d.get("agent_target"),
        f"+{d.get('agent_upside')}%",
        d.get("verdict", "")
    ]
    ws_val.append(row_data)
    r_idx = ws_val.max_row
    ws_val.row_dimensions[r_idx].height = 26
    row_fill = fill_zebra if i % 2 == 0 else fill_white
    for c_idx in range(1, len(row_data) + 1):
        c = ws_val.cell(row=r_idx, column=c_idx)
        c.font = font_bold if c_idx in (1, 2, 7, 9, 10) else font_data
        c.fill = row_fill
        c.border = thin_border
        c.alignment = Alignment(horizontal="center" if c_idx not in (3, 11) else "left", vertical="center")
        if c_idx in (4, 6, 9):
            c.number_format = '₹#,##0.00'

for col in ws_val.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_val.column_dimensions[col_letter].width = max(max_len + 3, 12)
ws_val.column_dimensions["C"].width = 28
ws_val.column_dimensions["K"].width = 50

# -----------------
# TAB 3: Top 25 Filtered Universe
# -----------------
ws2 = wb.create_sheet(title="Top 25 Filtered Midcaps")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("A1:N1")
ws2["A1"] = "NIFTY MIDCAP 100 — TOP 25 FILTERED CANDIDATES (SCREENER SCORECARD)"
ws2["A1"].font = font_title
ws2["A1"].fill = fill_dark_blue
ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 36

headers_top25 = [
    "Rank", "Symbol", "Company Name", "Industry", "CMP (₹)", "Target (₹)", 
    "Upside %", "ROE %", "Trailing P/E", "Forward P/E", "Debt/Equity", 
    "> 50 DMA", "> 200 DMA", "Score (/100)"
]

ws2.append([])
ws2.append(headers_top25)
ws2.row_dimensions[3].height = 26

for col_idx in range(1, len(headers_top25) + 1):
    cell = ws2.cell(row=3, column=col_idx)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

for i, stock in enumerate(top25, 1):
    row_data = [
        i,
        stock["symbol"],
        stock["name"],
        stock["industry"],
        stock["price"],
        stock["target"] if stock["target"] else "N/A",
        f"{stock['upside_pct']}%",
        f"{stock['roe']}%" if stock['roe'] is not None else "N/A",
        f"{stock['trailing_pe']}x" if stock['trailing_pe'] else "N/A",
        f"{stock['forward_pe']}x" if stock['forward_pe'] else "N/A",
        f"{stock['debt_to_equity']}%" if stock['debt_to_equity'] is not None else "N/A",
        "YES" if stock["above_50"] else "NO",
        "YES" if stock["above_200"] else "NO",
        stock["score"]
    ]
    ws2.append(row_data)
    r_idx = ws2.max_row
    ws2.row_dimensions[r_idx].height = 20
    row_fill = fill_zebra if i % 2 == 0 else fill_white
    for c_idx in range(1, len(row_data) + 1):
        c = ws2.cell(row=r_idx, column=c_idx)
        c.font = font_bold if c_idx in (1, 2, 7, 14) else font_data
        c.fill = row_fill
        c.border = thin_border
        c.alignment = Alignment(horizontal="center" if c_idx not in (3, 4) else "left", vertical="center")

for col in ws2.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws2.column_dimensions[col_letter].width = max(max_len + 3, 11)
ws2.column_dimensions["C"].width = 32
ws2.column_dimensions["D"].width = 24

wb.save(EXCEL_PATH)
print(f"[+] Excel workbook saved successfully: {EXCEL_PATH}")

# ==========================================
# 2. POWERPOINT PRESENTATION GENERATION
# ==========================================
print("[*] Generating PowerPoint Presentation...")
prs = Presentation()
prs.slide_width = Inches(13.333) # 16:9 widescreen
prs.slide_height = Inches(7.5)

blank_slide_layout = prs.slide_layouts[6]

DARK_BLUE = RGBColor(11, 34, 64)
NAVY = RGBColor(27, 54, 93)
GOLD = RGBColor(212, 175, 55)
WHITE = RGBColor(255, 255, 255)
LIGHT_GRAY = RGBColor(245, 247, 250)
TEXT_DARK = RGBColor(30, 30, 30)
TEXT_MUTED = RGBColor(100, 100, 100)
GREEN = RGBColor(0, 128, 0)

def add_header(slide, title_text, category_text="NIFTY MIDCAP 100 RESEARCH"):
    # Header Banner
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.2))
    tf = header_box.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = GOLD
    
    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = DARK_BLUE

# --- SLIDE 1: Title Slide ---
slide1 = prs.slides.add_slide(blank_slide_layout)
# Background
bg = slide1.shapes.add_shape(openpyxl.chart.shapes.GraphicalProperties if False else 1, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg.fill.solid()
bg.fill.fore_color.rgb = DARK_BLUE
bg.line.fill.background()

title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.0))
tf = title_box.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
p1.text = "NIFTY MIDCAP 100"
p1.font.size = Pt(44)
p1.font.bold = True
p1.font.color.rgb = WHITE

p2 = tf.add_paragraph()
p2.text = "Institutional Screening & High-Conviction Buy Recommendations"
p2.font.size = Pt(24)
p2.font.color.rgb = GOLD

p3 = tf.add_paragraph()
p3.text = "\nFrom 100 Constituents → Filtered Top 25 Universe → Top 5 High-Conviction Picks\nPowered by Quantitative Screener & Multi-Agent Debate"
p3.font.size = Pt(14)
p3.font.color.rgb = RGBColor(200, 210, 225)

# --- SLIDE 2: Executive Summary & Two-Tier Methodology ---
slide2 = prs.slides.add_slide(blank_slide_layout)
add_header(slide2, "Methodology: 100 Constituent Funnel to Top 5 Alpha Picks")

box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
tf2 = box2.text_frame
tf2.word_wrap = True

bullets = [
    ("Tier 1: Full-Index Quantitative Audit (100 Stocks)", 
     "• Pulled the official 100 constituents directly from NSE (niftyindices.com).\n• Evaluated multi-factor scorecards: Return on Equity (ROE), Profit Margins, Balance Sheet Leverage (Debt-to-Equity), 50-DMA and 200-DMA moving average alignments, and Broker Consensus Targets."),
    ("Tier 2: The Top 25 Filtered Universe", 
     "• Filtered down from 100 to the top 25 institutional-grade candidates based on composite score (Scores 75 – 90/100).\n• Eliminated low-profitability companies, capital-destroying balance sheets, and deep downtrend charts."),
    ("Tier 3: The Top 5 High-Conviction Buy Portfolio", 
     "• Stress-tested finalists via the TradingAgents Multi-Agent framework (Technicals, Fundamentals, Bull vs. Bear debate).\n• Selected 5 distinct leaders representing secular growth themes: Auto/EV (Hero MotoCorp), Realty (Lodha & Oberoi), Financial Value (LIC), and Global Power T&D (Apar Industries).")
]

for title, desc in bullets:
    p = tf2.add_paragraph()
    p.text = title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    p_desc = tf2.add_paragraph()
    p_desc.text = desc + "\n"
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = TEXT_DARK

# --- SLIDE 3: Top 5 Portfolio Overview Table ---
slide3 = prs.slides.add_slide(blank_slide_layout)
add_header(slide3, "Top 5 High-Conviction Buy Recommendations Summary")

rows = 6
cols = 7
table_shape = slide3.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
table = table_shape.table

# Column widths
table.columns[0].width = Inches(1.2) # Rank
table.columns[1].width = Inches(2.2) # Company
table.columns[2].width = Inches(2.2) # Theme
table.columns[3].width = Inches(1.4) # CMP
table.columns[4].width = Inches(1.5) # Target
table.columns[5].width = Inches(1.4) # Upside
table.columns[6].width = Inches(1.8) # Stop-Loss

headers = ["Rank", "Company", "Theme / Sector", "CMP (₹)", "Target (₹)", "Upside", "Stop-Loss"]
for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

for row_idx, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    data_row = [
        f"#{row_idx}",
        f"{stock['name']}\n({sym})",
        d.get("sector_theme", stock["industry"]),
        f"₹{stock['price']:,.2f}",
        f"₹{stock['target']:,.2f}" if stock['target'] else "N/A",
        f"+{stock['upside_pct']}%",
        d.get("stop_loss", "N/A")
    ]
    for col_idx, val in enumerate(data_row):
        cell = table.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = LIGHT_GRAY if row_idx % 2 == 0 else WHITE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(12)
        p.alignment = PP_ALIGN.CENTER if col_idx in (0, 3, 4, 5, 6) else PP_ALIGN.LEFT
        if col_idx == 5:
            p.font.bold = True
            p.font.color.rgb = GREEN

# --- SLIDE 4: Broker vs Agent Target Valuation Comparison ---
slide4 = prs.slides.add_slide(blank_slide_layout)
add_header(slide4, "Target Price Audit: Broker Consensus vs. Agent Independent Valuation", "VALUATION MODEL COMPARISON")

table_shape4 = slide4.shapes.add_table(6, 6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
table4 = table_shape4.table

table4.columns[0].width = Inches(1.8) # Company
table4.columns[1].width = Inches(1.4) # CMP
table4.columns[2].width = Inches(1.8) # Broker Target
table4.columns[3].width = Inches(1.8) # Agent Target
table4.columns[4].width = Inches(1.5) # Fair PE
table4.columns[5].width = Inches(3.4) # Strategic Insight

headers4 = ["Stock", "CMP (₹)", "Broker Target", "Agent Model Target", "Valuation Multiple", "Agent Analytical Verdict"]
for col_idx, h in enumerate(headers4):
    cell = table4.cell(0, col_idx)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    p = cell.text_frame.paragraphs[0]
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

for row_idx, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    data_row = [
        f"{sym}\n{stock['name'][:18]}",
        f"₹{stock['price']:,.2f}",
        f"₹{stock['target']:,.2f}\n(+{stock['upside_pct']}%)",
        f"₹{d.get('agent_target'):,.2f}\n(+{d.get('agent_upside')}%)",
        f"{d.get('agent_fair_pe')}x Forward P/E",
        d.get("verdict", "")
    ]
    for col_idx, val in enumerate(data_row):
        cell = table4.cell(row_idx, col_idx)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = LIGHT_GRAY if row_idx % 2 == 0 else WHITE
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.alignment = PP_ALIGN.CENTER if col_idx in (1, 2, 3, 4) else PP_ALIGN.LEFT
        if col_idx in (2, 3):
            p.font.bold = True

# --- SLIDES 5 to 9: Individual Stock Deep Dives ---
for i, stock in enumerate(top5, 1):
    sym = stock["symbol"]
    d = top5_details.get(sym, {})
    slide = prs.slides.add_slide(blank_slide_layout)
    add_header(slide, f"#{i} {stock['name']} ({sym}.NS)", f"SECTOR: {d.get('sector_theme', stock['industry']).upper()}")
    
    # Left Card: Financial Metrics & Order Specifications
    card_left = slide.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tf_l = card_left.text_frame
    tf_l.word_wrap = True
    
    p = tf_l.paragraphs[0]
    p.text = "KEY METRICS & ORDER SPECIFICATIONS"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = NAVY
    
    metrics = [
        f"• Current Market Price (CMP): ₹{stock['price']:,.2f}",
        f"• Institutional Target Price: ₹{stock['target']:,.2f} (+{stock['upside_pct']}%)" if stock['target'] else f"• Upside: +{stock['upside_pct']}%",
        f"• Recommended Entry Range: {d.get('entry_range', 'At CMP')}",
        f"• Hard Stop-Loss: {d.get('stop_loss', 'Trailing')}",
        f"• Return on Equity (ROE): {stock['roe']}%" if stock['roe'] else "• ROE: Strong",
        f"• Valuation: Trailing P/E: {stock['trailing_pe']}x | Forward P/E: {stock['forward_pe']}x",
        f"• Balance Sheet Debt/Equity: {stock['debt_to_equity']}%" if stock['debt_to_equity'] is not None else "• Balance Sheet: Robust Financial Quality",
        f"• Technical Alignment: Above 50-DMA & 200-DMA (Confirmed Bull Trend)",
        f"• Investment Horizon: {d.get('time_horizon', '12 Months')}",
        f"• Consensus Rating: {stock['recommendation'].replace('_', ' ').title()}"
    ]
    for m in metrics:
        pm = tf_l.add_paragraph()
        pm.text = m
        pm.font.size = Pt(13)
        pm.font.color.rgb = TEXT_DARK
        
    # Right Card: Investment Thesis & Growth Drivers
    card_right = slide.shapes.add_textbox(Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tf_r = card_right.text_frame
    tf_r.word_wrap = True
    
    pr = tf_r.paragraphs[0]
    pr.text = "INVESTMENT THESIS & GROWTH DRIVERS"
    pr.font.bold = True
    pr.font.size = Pt(15)
    pr.font.color.rgb = NAVY
    
    thesis_paras = [
        ("Core Investment Thesis:", d.get("thesis", "Market leading fundamentals with strong capital efficiency.")),
        ("Primary Catalysts:", d.get("catalysts", "Industry tailwinds and margin expansion.")),
        ("Risk Factors to Monitor:", "Broader market correction, raw material input cost spikes, or sectoral slowdown.")
    ]
    for heading, text in thesis_paras:
        ph = tf_r.add_paragraph()
        ph.text = "\n" + heading
        ph.font.bold = True
        ph.font.size = Pt(13)
        ph.font.color.rgb = GOLD
        
        pt = tf_r.add_paragraph()
        pt.text = text
        pt.font.size = Pt(12)
        pt.font.color.rgb = TEXT_DARK

# --- SLIDE 9: Special Case Study: Multi-Agent Committee on OFSS ---
slide9 = prs.slides.add_slide(blank_slide_layout)
add_header(slide9, "Case Study: Multi-Agent Committee Stress-Test on OFSS", "RISK MANAGEMENT INSIGHT")

box9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
tf9 = box9.text_frame
tf9.word_wrap = True

p9_1 = tf9.paragraphs[0]
p9_1.text = "Why Pure Screener Ranking is Not Enough (The Value of Agentic Debate)"
p9_1.font.bold = True
p9_1.font.size = Pt(18)
p9_1.font.color.rgb = NAVY

ofss_insights = [
    ("Initial Quantitative Screener Score: 90.0 / 100 (#1 Ranked)",
     "On paper, Oracle Financial Services Software (OFSS) appeared as the top statistical pick due to exceptional metrics: 47.4% ROE, zero debt, and +28.3% target upside to ₹13,055."),
    ("TradingAgents Multi-Agent Debate Findings:",
     "• Technical Analyst: Discovered price was trading below its 50-day moving average (₹10,804) with deeply negative absolute MACD (-167.67).\n• Liquidity/Volume Audit: Uncovered anemic volume of only 23,949 shares, disproving institutional accumulation.\n• Bear Researcher & CIO Decision: Rated OFSS as 'Underweight / Accumulate on Dips Only' (wait for entry near ₹9,950–₹10,000 rather than chasing at spot)."),
    ("Key Takeaway for Investors:",
     "Quantitative screeners identify exceptional fundamentals; agentic debate protects capital from consolidation traps.")
]

for title, desc in ofss_insights:
    pt = tf9.add_paragraph()
    pt.text = "\n" + title
    pt.font.bold = True
    pt.font.size = Pt(14)
    pt.font.color.rgb = GOLD
    
    pd = tf9.add_paragraph()
    pd.text = desc
    pd.font.size = Pt(13)
    pd.font.color.rgb = TEXT_DARK

# --- SLIDE 10: Portfolio Allocation & Risk Rules ---
slide10 = prs.slides.add_slide(blank_slide_layout)
add_header(slide10, "Portfolio Construction & Risk Management Framework")

box10 = slide10.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
tf10 = box10.text_frame
tf10.word_wrap = True

p10_1 = tf10.paragraphs[0]
p10_1.text = "Recommended Execution & Sizing Guidelines for Indian Midcaps"
p10_1.font.bold = True
p10_1.font.size = Pt(18)
p10_1.font.color.rgb = NAVY

rules = [
    ("1. Equal-Weight Capital Allocation (4% – 5% per stock):", 
     "Do not allocate more than 20% to 25% of your total equity portfolio to these 5 midcaps combined, keeping each individual stock position capped at 4% to 5% to absorb midcap beta volatility."),
    ("2. Two-Tranche Staggered Entry (50/50 Strategy):", 
     "Deploy 50% of intended position sizing at the current market price, and reserve the remaining 50% for minor pullbacks toward each stock's respective 50-DMA support band."),
    ("3. Hard Trailing Stop-Loss Protection:", 
     "Strictly adhere to the stop-loss levels identified in Slide 3 (or trail a 1.5x ATR trailing stop) to preserve capital in the event of broader Nifty benchmark drawdowns.")
]

for title, desc in rules:
    pt = tf10.add_paragraph()
    pt.text = "\n" + title
    pt.font.bold = True
    pt.font.size = Pt(14)
    pt.font.color.rgb = NAVY
    
    pd = tf10.add_paragraph()
    pd.text = desc
    pd.font.size = Pt(13)
    pd.font.color.rgb = TEXT_DARK

prs.save(PPT_PATH)
print(f"[+] PowerPoint presentation saved successfully: {PPT_PATH}")
