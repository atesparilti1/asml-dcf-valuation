"""
Builds ASML_DCF_Model.xlsx: a fully formula-driven DCF of ASML Holding N.V.
Only the Assumptions and Historical tabs contain hard-coded inputs (blue);
every other number is an Excel formula, so changing any assumption flows through
forecast -> WACC -> DCF -> sensitivity -> scenarios -> dashboard -> checks.

Run:  python build_model.py
"""
import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.properties import PageSetupProperties

from data import inputs as I
import model as M

ROOT = Path(__file__).parent
OUT = ROOT / "ASML_DCF_Model.xlsx"

# ------------------------------------------------------------------ styles
NAVY, BLUE_IN, GREEN_LINK = "0B1F3A", "0000FF", "007A33"
F_TITLE = Font(name="Calibri", size=18, bold=True, color=NAVY)
F_SUB = Font(name="Calibri", size=10, italic=True, color="595959")
F_HDR = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
F_SEC = Font(name="Calibri", size=11, bold=True, color=NAVY)
F_B = Font(name="Calibri", size=10, bold=True)
F_N = Font(name="Calibri", size=10)
F_IN = Font(name="Calibri", size=10, color=BLUE_IN)
F_LINK = Font(name="Calibri", size=10, color=GREEN_LINK)
F_NOTE = Font(name="Calibri", size=9, italic=True, color="595959")
FILL_HDR = PatternFill("solid", fgColor=NAVY)
FILL_HIST = PatternFill("solid", fgColor="7F7F7F")
FILL_FC = PatternFill("solid", fgColor="2B4BFF")
FILL_IN = PatternFill("solid", fgColor="FFF2CC")
FILL_OUT = PatternFill("solid", fgColor="E2EFDA")
FILL_SEC = PatternFill("solid", fgColor="E7ECF5")
FILL_BASE = PatternFill("solid", fgColor="FFD966")
THIN = Side(style="thin", color="BFBFBF")
MED = Side(style="medium", color=NAVY)
B_TOP = Border(top=THIN)
B_TOTAL = Border(top=Side(style="thin", color="000000"), bottom=Side(style="double", color="000000"))
B_BOX = Border(left=MED, right=MED, top=MED, bottom=MED)

NUM = '#,##0;(#,##0);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT2 = '0.00%;(0.00%);"-"'
MULT = '0.0"x"'
EUR = '"€"#,##0.00'
EUR0 = '"€"#,##0'
DATE = 'dd-mmm-yyyy'
YRS = '0.000'

YEARS_F = M.FY                       # 2026..2030
FC = ["E", "F", "G", "H", "I"]       # forecast columns on Assumptions / DCF / Scenarios


def put(ws, ref, value, font=F_N, fmt=None, fill=None, bold=False, align=None, border=None):
    c = ws[ref]
    c.value = value
    c.font = font
    if bold:
        c.font = Font(name=font.name, size=font.size, bold=True, color=font.color, italic=font.italic)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = Alignment(horizontal=align, vertical="center")
    if border:
        c.border = border
    return c


def inp(ws, ref, value, fmt=None):
    """Hard-coded input: blue font, yellow fill."""
    return put(ws, ref, value, F_IN, fmt, FILL_IN)


def hdr_row(ws, row, c1, c2, fill=FILL_HDR):
    for c in range(c1, c2 + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = fill
        cell.font = F_HDR
        cell.alignment = Alignment(horizontal="center" if c > c1 else "left", vertical="center")


def section(ws, row, text, c1=2, c2=12):
    for c in range(c1, c2 + 1):
        ws.cell(row=row, column=c).fill = FILL_SEC
    put(ws, f"{CL(c1)}{row}", text, F_SEC)


def title(ws, text, sub):
    put(ws, "B1", text, F_TITLE)
    put(ws, "B2", sub, F_SUB)
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 2


def widths(ws, d):
    for k, v in d.items():
        ws.column_dimensions[k].width = v


# ================================================================== workbook
wb = Workbook()
ws_cover = wb.active
ws_cover.title = "Cover"
ws_a = wb.create_sheet("Assumptions")
ws_h = wb.create_sheet("Historical")
ws_f = wb.create_sheet("Forecast")
ws_w = wb.create_sheet("WACC")
ws_d = wb.create_sheet("DCF")
ws_s = wb.create_sheet("Sensitivity")
ws_sc = wb.create_sheet("Scenarios")
ws_db = wb.create_sheet("Dashboard")
ws_ck = wb.create_sheet("Checks")

for ws, color in [(ws_cover, NAVY), (ws_a, "FFC000"), (ws_h, "7F7F7F"), (ws_f, "2B4BFF"), (ws_w, "2B4BFF"),
                  (ws_d, "2B4BFF"), (ws_s, "2B4BFF"), (ws_sc, "2B4BFF"), (ws_db, "007A33"), (ws_ck, "C00000")]:
    ws.sheet_properties.tabColor = color

A = {}   # name -> absolute reference (e.g. "Assumptions!$C$5")


def name(key, ws, ref):
    col = "".join(ch for ch in ref if ch.isalpha())
    row = "".join(ch for ch in ref if ch.isdigit())
    A[key] = f"{ws.title}!${col}${row}"


# ================================================================== ASSUMPTIONS
ws = ws_a
title(ws, "Assumptions", "All model inputs live here. Blue on yellow = hard-coded input; black = formula. EUR millions unless stated.")
widths(ws, {"B": 38, "C": 14, "D": 9, "E": 11, "F": 11, "G": 11, "H": 11, "I": 11, "J": 14, "K": 110})

r = 4
section(ws, r, "General", 2, 11)
gen = [
    ("val_date", "Valuation date", datetime(*I.VALUATION_DATE), DATE, "date", "Pricing date for market data"),
    ("bs_date", "Latest balance sheet date", datetime(*I.BALANCE_SHEET_DATE), DATE, "date", "Q2 2026 balance sheet (S4); cash flows after this date are valued"),
    ("fy1_end", "FY2026 year end", datetime(*I.FY1_END), DATE, "date", "ASML fiscal year = calendar year"),
    ("scen", "Scenario selector (1 Bear, 2 Base, 3 Bull)", I.SCENARIO, "0", "#", "Drives the live model (Forecast, DCF, Sensitivity)"),
]
for i, (k, lbl, v, fmt, unit, note) in enumerate(gen):
    rr = r + 1 + i
    put(ws, f"B{rr}", lbl)
    inp(ws, f"C{rr}", v, fmt)
    put(ws, f"D{rr}", unit, F_NOTE)
    put(ws, f"K{rr}", note, F_NOTE)
    name(k, ws, f"C{rr}")
rr = r + 5
put(ws, f"B{rr}", "Active scenario")
put(ws, f"C{rr}", f'=CHOOSE({A["scen"]},"Bear","Base","Bull")', F_B, align="right")
name("scen_name", ws, f"C{rr}")
rr += 1
put(ws, f"B{rr}", "Mid-year discounting (1 = on, 0 = off)")
inp(ws, f"C{rr}", I.MID_YEAR, "0")
put(ws, f"K{rr}", "Cash flows assumed to arrive evenly through each year (standard banking convention)", F_NOTE)
name("mid", ws, f"C{rr}")
rr += 1
put(ws, f"B{rr}", "Weight of Gordon Growth in blended price")
inp(ws, f"C{rr}", I.GORDON_WEIGHT, PCT)
put(ws, f"K{rr}", "Blended DCF price = weight x Gordon + (1 - weight) x Exit Multiple", F_NOTE)
name("gw", ws, f"C{rr}")

r = rr + 2
section(ws, r, "Market data & latest balance sheet", 2, 11)
put(ws, f"J{r}", "Type", F_SEC)
put(ws, f"K{r}", "Source / note", F_SEC)
mk = [("price", "Current share price (EUR)", EUR), ("shares", "Diluted shares outstanding (m)", NUM1),
      ("cash", "Cash & short-term investments", NUM1), ("debt", "Total debt (bonds + commercial paper)", NUM1),
      ("nonop", "Non-operating investments", NUM1), ("h1_ufcf", "H1-2026 actual unlevered FCF", NUM1)]
for i, (k, lbl, fmt) in enumerate(mk):
    rr = r + 1 + i
    v, typ, src, note = I.MARKET[k]
    put(ws, f"B{rr}", lbl)
    inp(ws, f"C{rr}", v, fmt)
    put(ws, f"J{rr}", typ, F_NOTE)
    put(ws, f"K{rr}", f"[{src}] {note}", F_NOTE)
    name(k, ws, f"C{rr}")

r = rr + 2
section(ws, r, "Cost of capital inputs", 2, 11)
wk = [("rf", "Risk-free rate (10Y Bund)", PCT2), ("erp", "Equity risk premium", PCT2), ("beta_reg", "Regression beta (5Y monthly)", "0.00"),
      ("beta_ind_u", "Industry unlevered beta (semi equipment)", "0.00"), ("beta_w", "Weight on regression beta", PCT),
      ("spread", "Credit spread over risk-free (A1/A+)", PCT2), ("tax_marg", "Marginal tax rate (debt tax shield)", PCT)]
for i, (k, lbl, fmt) in enumerate(wk):
    rr = r + 1 + i
    v, typ, src, note = I.WACC_IN[k]
    put(ws, f"B{rr}", lbl)
    inp(ws, f"C{rr}", v, fmt)
    put(ws, f"J{rr}", typ, F_NOTE)
    put(ws, f"K{rr}", (f"[{src}] " if src else "") + note, F_NOTE)
    name(k, ws, f"C{rr}")

r = rr + 2
section(ws, r, "Scenario drivers (FY2026E - FY2030E)", 2, 11)
r += 1
for j, t in enumerate(["Driver", "Case", "Unit"] + [f"FY{y % 100}E" for y in YEARS_F] + ["Average", "Rationale"]):
    put(ws, f"{CL(2 + j)}{r}", t)
hdr_row(ws, r, 2, 11)
r += 1
DRV = {}  # key -> {"Bear": row, ..., "Live": row}
for k, d in I.DRIVERS.items():
    rows = {}
    for ci, case in enumerate(M.CASES + ["Live"]):
        rr = r + ci
        rows[case] = rr
        put(ws, f"B{rr}", d["label"] if ci == 0 else "", F_B if ci == 0 else F_N)
        put(ws, f"C{rr}", case if case != "Live" else "Live ►", F_B if case == "Live" else F_N)
        put(ws, f"D{rr}", d["unit"], F_NOTE)
        for yi, col in enumerate(FC):
            if case == "Live":
                put(ws, f"{col}{rr}", f"=CHOOSE({A['scen']},{col}{r},{col}{r + 1},{col}{r + 2})", F_B, PCT, FILL_OUT)
            else:
                inp(ws, f"{col}{rr}", d[case][yi], PCT)
        put(ws, f"J{rr}", f"=AVERAGE(E{rr}:I{rr})", F_N, PCT)
    put(ws, f"K{r}", d["why"], F_NOTE)
    ws[f"K{r}"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 40
    DRV[k] = rows
    r += 5
SCL = {}
for k, d in I.SCALARS.items():
    rows = {}
    fmt = MULT if d["unit"] == "x" else PCT2
    for ci, case in enumerate(M.CASES + ["Live"]):
        rr = r + ci
        rows[case] = rr
        put(ws, f"B{rr}", d["label"] if ci == 0 else "", F_B if ci == 0 else F_N)
        put(ws, f"C{rr}", case if case != "Live" else "Live ►", F_B if case == "Live" else F_N)
        put(ws, f"D{rr}", d["unit"], F_NOTE)
        if case == "Live":
            put(ws, f"E{rr}", f"=CHOOSE({A['scen']},E{r},E{r + 1},E{r + 2})", F_B, fmt, FILL_OUT)
        else:
            inp(ws, f"E{rr}", d[case], fmt)
    put(ws, f"K{r}", d["why"], F_NOTE)
    ws[f"K{r}"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 40
    SCL[k] = rows
    name(k, ws, f"E{rows['Live']}")
    r += 5
r += 1
section(ws, r, "Scenario narrative", 2, 11)
for i, case in enumerate(M.CASES):
    put(ws, f"B{r + 1 + i}", case, F_B)
    put(ws, f"C{r + 1 + i}", I.SCENARIO_STORY[case], F_NOTE)
ws.freeze_panes = "C4"


def drv(key, case, yi):
    return f"Assumptions!${FC[yi]}${DRV[key][case]}"


def scl(key, case):
    return f"Assumptions!$E${SCL[key][case]}"


# ================================================================== HISTORICAL
ws = ws_h
title(ws, "Historical Financials", "Reported US GAAP figures (blue) from ASML 20-F filings via SEC XBRL [S1, S2, S3]; ratios and FCF are calculated (black). EUR millions.")
widths(ws, {"B": 44, "C": 11, "D": 11, "E": 11, "F": 11, "G": 11, "H": 11, "I": 12, "J": 70})
HC = {2020: "C", 2021: "D", 2022: "E", 2023: "F", 2024: "G", 2025: "H"}
put(ws, "B4", "EUR m, fiscal year ending 31 Dec")
for y, c in HC.items():
    put(ws, f"{c}4", f"FY{y % 100}A" + (" (ref)" if y == 2020 else ""))
put(ws, "I4", "Type")
put(ws, "J4", "Source / definition")
hdr_row(ws, 4, 2, 10, FILL_HIST)
HR = {}
rep = [("revenue", "Total net sales"), ("cogs", "Cost of sales"), ("gross_profit", "Gross profit"), ("rnd", "Research & development"),
       ("sga", "Selling, general & administrative"), ("ebit", "Income from operations (EBIT)"),
       ("da", "Depreciation & amortization (cash flow statement)"), ("pretax", "Income before income taxes"),
       ("tax", "Income tax expense"), ("net_income", "Net income"), ("capex_ppe", "Purchase of PP&E"),
       ("capex_intang", "Purchase of intangible assets"), ("cfo", "Net cash from operating activities"),
       ("cash", "Cash & cash equivalents"), ("sti", "Short-term investments"), ("current_assets", "Total current assets"),
       ("loans_rec_cur", "Loans receivable, current (non-operating)"), ("current_liab", "Total current liabilities"),
       ("debt_current", "Current debt incl. commercial paper"), ("debt_noncurrent", "Long-term debt"),
       ("contract_liab_nc", "Contract liabilities, non-current"), ("diluted_shares", "Diluted weighted avg. shares (m)")]
r = 5
section(ws, r, "Reported (US GAAP)", 2, 10)
for k, lbl in rep:
    r += 1
    HR[k] = r
    put(ws, f"B{r}", lbl)
    for y, c in HC.items():
        v = I.HIST[k].get(y)
        if v is not None:
            inp(ws, f"{c}{r}", v, NUM1)
    put(ws, f"I{r}", "REPORTED", F_NOTE)
    put(ws, f"J{r}", "[S2] XBRL 20-F" + ("; FY25 current debt = bonds 990.2 + ECP 691.7 [S1]" if k == "debt_current" else
                                          "; new line in FY25 [S3]" if k == "loans_rec_cur" else ""), F_NOTE)
r += 2
section(ws, r, "Calculated", 2, 10)
calc = [
    ("growth", "Revenue growth %", PCT, lambda c, p: f"={c}{HR['revenue']}/{p}{HR['revenue']}-1", "Revenue / prior-year revenue - 1"),
    ("gm", "Gross margin %", PCT, lambda c, p: f"={c}{HR['gross_profit']}/{c}{HR['revenue']}", "Gross profit / revenue"),
    ("ebitda", "EBITDA", NUM, lambda c, p: f"={c}{HR['ebit']}+{c}{HR['da']}", "EBIT + D&A"),
    ("ebitda_m", "EBITDA margin %", PCT, lambda c, p: f"={c}{{ebitda}}/{c}{HR['revenue']}", "EBITDA / revenue"),
    ("ebit_m", "EBIT margin %", PCT, lambda c, p: f"={c}{HR['ebit']}/{c}{HR['revenue']}", "EBIT / revenue"),
    ("da_pct", "D&A % revenue", PCT, lambda c, p: f"={c}{HR['da']}/{c}{HR['revenue']}", "D&A / revenue"),
    ("rnd_pct", "R&D % revenue", PCT, lambda c, p: f"={c}{HR['rnd']}/{c}{HR['revenue']}", "R&D / revenue"),
    ("etr", "Effective tax rate", PCT, lambda c, p: f"={c}{HR['tax']}/{c}{HR['pretax']}", "Income tax expense / income before taxes"),
    ("taxes", "Taxes on EBIT", NUM, lambda c, p: f"={c}{HR['ebit']}*{c}{{etr}}", "EBIT x effective tax rate (unlevered taxes)"),
    ("nopat", "NOPAT", NUM, lambda c, p: f"={c}{HR['ebit']}-{c}{{taxes}}", "EBIT - taxes on EBIT"),
    ("capex", "Total CapEx (PP&E + intangibles)", NUM, lambda c, p: f"={c}{HR['capex_ppe']}+{c}{HR['capex_intang']}", ""),
    ("capex_pct", "CapEx % revenue", PCT, lambda c, p: f"={c}{{capex}}/{c}{HR['revenue']}", ""),
    ("nwc", "Operating net working capital", NUM, None,
     "(Current assets - cash - STI - current loans rec.) - (current liabilities - current debt) - non-current contract liabilities"),
    ("nwc_pct", "NWC % revenue", PCT, lambda c, p: f"={c}{{nwc}}/{c}{HR['revenue']}", "Negative = customers pre-fund ASML via EUV down payments"),
    ("dnwc", "Change in NWC (increase = cash outflow)", NUM, lambda c, p: f"={c}{{nwc}}-{p}{{nwc}}", ""),
    ("ufcf", "Unlevered free cash flow", NUM, lambda c, p: f"={c}{{nopat}}+{c}{HR['da']}-{c}{{capex}}-{c}{{dnwc}}", "NOPAT + D&A - CapEx - change in NWC"),
    ("ufcf_m", "UFCF margin %", PCT, lambda c, p: f"={c}{{ufcf}}/{c}{HR['revenue']}", ""),
    ("cash_conv", "UFCF / NOPAT (cash conversion)", PCT, lambda c, p: f"={c}{{ufcf}}/{c}{{nopat}}", ""),
    ("total_debt", "Total debt", NUM, lambda c, p: f"={c}{HR['debt_current']}+{c}{HR['debt_noncurrent']}", ""),
    ("net_cash", "Net cash (cash + STI - debt)", NUM, lambda c, p: f"={c}{HR['cash']}+{c}{HR['sti']}-{c}{{total_debt}}", ""),
    ("gp_check", "Check: gross profit - (sales - COGS)", NUM1, lambda c, p: f"={c}{HR['gross_profit']}-({c}{HR['revenue']}-{c}{HR['cogs']})", "Should be 0"),
]
for k, lbl, fmt, _, _ in calc:
    r += 1
    HR[k] = r
for k, lbl, fmt, fn, note in calc:
    rr = HR[k]
    put(ws, f"B{rr}", lbl, F_B if k in ("ebitda", "nopat", "ufcf", "nwc") else F_N)
    put(ws, f"J{rr}", note, F_NOTE)
    years = range(2020, 2026) if k == "nwc" else range(2021, 2026)
    for y in years:
        c = HC[y]
        p = HC.get(y - 1)
        if k == "nwc":
            f = (f"=({c}{HR['current_assets']}-{c}{HR['cash']}-{c}{HR['sti']}-{c}{HR['loans_rec_cur']})"
                 f"-({c}{HR['current_liab']}-{c}{HR['debt_current']})-{c}{HR['contract_liab_nc']}")
        else:
            f = fn(c, p).replace("{ebitda}", str(HR["ebitda"])).replace("{etr}", str(HR["etr"])) \
                .replace("{taxes}", str(HR["taxes"])).replace("{capex}", str(HR["capex"])).replace("{nwc}", str(HR["nwc"])) \
                .replace("{nopat}", str(HR["nopat"])).replace("{dnwc}", str(HR["dnwc"])).replace("{ufcf}", str(HR["ufcf"])) \
                .replace("{total_debt}", str(HR["total_debt"]))
        put(ws, f"{c}{rr}", f, F_B if k in ("ebitda", "nopat", "ufcf") else F_N, fmt)
    put(ws, f"I{rr}", "CALCULATED", F_NOTE)
    if k in ("ebitda", "nopat", "ufcf"):
        for c in "CDEFGH":
            ws[f"{c}{rr}"].border = B_TOP
# 5-year averages / CAGR
r = HR["gp_check"] + 2
section(ws, r, "Summary FY21-FY25", 2, 10)
summ = [("Revenue CAGR FY20-FY25", f"=(H{HR['revenue']}/C{HR['revenue']})^(1/5)-1", PCT),
        ("Average gross margin", f"=AVERAGE(D{HR['gm']}:H{HR['gm']})", PCT),
        ("Average EBITDA margin", f"=AVERAGE(D{HR['ebitda_m']}:H{HR['ebitda_m']})", PCT),
        ("Average effective tax rate", f"=AVERAGE(D{HR['etr']}:H{HR['etr']})", PCT),
        ("Average CapEx % revenue", f"=AVERAGE(D{HR['capex_pct']}:H{HR['capex_pct']})", PCT),
        ("Average NWC % revenue", f"=AVERAGE(D{HR['nwc_pct']}:H{HR['nwc_pct']})", PCT),
        ("Cumulative UFCF FY21-FY25", f"=SUM(D{HR['ufcf']}:H{HR['ufcf']})", NUM)]
for i, (lbl, f, fmt) in enumerate(summ):
    put(ws, f"B{r + 1 + i}", lbl)
    put(ws, f"C{r + 1 + i}", f, F_B, fmt)
    HR["sum_" + str(i)] = r + 1 + i
r = r + len(summ) + 2
section(ws, r, "Trend analysis: what matters for the forecast", 2, 10)
h = M.hist_calcs()
trend = [
    f"1. Growth is strong but cyclical: revenue rose from EUR 18.6bn (FY21) to EUR 32.7bn (FY25), a {((I.HIST['revenue'][2025] / I.HIST['revenue'][2020]) ** 0.2 - 1):.0%} CAGR since FY20, "
    f"but FY24 grew only {h[2024]['growth']:.1%} (a digestion year). The forecast must therefore fade growth rather than extrapolate it.",
    f"2. Margins expand with EUV mix and scale: gross margin {h[2022]['gm']:.1%} (FY22) to {h[2025]['gm']:.1%} (FY25); EBITDA margin {h[2022]['ebitda_m']:.1%} to {h[2025]['ebitda_m']:.1%}. "
    "R&D stays at ~14-15% of sales, so operating leverage drives the margin path.",
    f"3. The tax rate is low and stable: ETR {min(h[y]['etr'] for y in range(2021, 2026)):.1%}-{max(h[y]['etr'] for y in range(2021, 2026)):.1%} thanks to the Dutch innovation box.",
    f"4. Capex is light but lumpy: {min(h[y]['capex_pct'] for y in range(2021, 2026)):.1%}-{max(h[y]['capex_pct'] for y in range(2021, 2026)):.1%} of sales; the FY23-24 capacity build (EUV, High-NA) has now normalised.",
    f"5. Working capital is the swing factor: NWC is negative ({h[2025]['nwc_pct']:.0%} of FY25 sales) because customers prepay EUV systems. Swings of EUR 2-5bn a year "
    "(e.g. a FY23 outflow when down payments were consumed) make reported FCF far more volatile than NOPAT.",
    "6. The balance sheet is net cash, and buybacks plus dividends (EUR 8.5bn in FY25) return most FCF, so the EV-to-equity bridge is small relative to EV.",
]
for i, t in enumerate(trend):
    put(ws, f"B{r + 1 + i}", t, F_N)
ws.freeze_panes = "C5"

# ================================================================== FORECAST
ws = ws_f
title(ws, "Operating Forecast", "FY21A-FY25A linked from Historical (green); FY26E-FY30E driven by the live scenario on Assumptions. EUR millions.")
widths(ws, {"B": 36, **{CL(c): 11 for c in range(3, 13)}, "M": 60})
HCOL = ["C", "D", "E", "F", "G"]          # FY21..FY25
FCOL = ["H", "I", "J", "K", "L"]          # FY26..FY30
ALLC = HCOL + FCOL
yrs = list(range(2021, 2031))
put(ws, "B4", "EUR m")
for c, y in zip(ALLC, yrs):
    put(ws, f"{c}4", f"FY{y % 100}{'A' if y <= 2025 else 'E'}")
put(ws, "M4", "Logic")
hdr_row(ws, 4, 2, 13)
for c in HCOL:
    ws[f"{c}4"].fill = FILL_HIST
for c in FCOL:
    ws[f"{c}4"].fill = FILL_FC
put(ws, "B5", "Scenario:", F_NOTE)
put(ws, "C5", f"={A['scen_name']}", F_B)
FR = {}
lines = ["revenue", "growth", None, "gp", "gm", None, "ebitda", "ebitda_m", None, "da", "da_pct", None, "ebit", "ebit_m", None,
         "taxes", "tax", "nopat", None, "capex", "capex_pct", None, "nwc", "nwc_pct", "dnwc", None, "ufcf", "ufcf_m", None, "opex_pct"]
r = 6
for k in lines:
    r += 1
    if k:
        FR[k] = r
labels = {"revenue": ("Revenue", NUM), "growth": ("  Revenue growth %", PCT), "gp": ("Gross profit", NUM), "gm": ("  Gross margin %", PCT),
          "ebitda": ("EBITDA", NUM), "ebitda_m": ("  EBITDA margin %", PCT), "da": ("Depreciation & amortization", NUM),
          "da_pct": ("  D&A % revenue", PCT), "ebit": ("EBIT", NUM), "ebit_m": ("  EBIT margin %", PCT), "taxes": ("Taxes on EBIT", NUM),
          "tax": ("  Tax rate", PCT), "nopat": ("NOPAT", NUM), "capex": ("Capital expenditures", NUM), "capex_pct": ("  CapEx % revenue", PCT),
          "nwc": ("Net working capital", NUM), "nwc_pct": ("  NWC % revenue", PCT), "dnwc": ("Change in NWC (increase = outflow)", NUM),
          "ufcf": ("Unlevered free cash flow", NUM), "ufcf_m": ("  UFCF margin %", PCT), "opex_pct": ("Memo: implied opex % (GM - EBIT margin)", PCT)}
logic = {"revenue": "Prior year x (1 + growth)", "gp": "Revenue x gross margin", "ebitda": "Revenue x EBITDA margin", "da": "Revenue x D&A %",
         "ebit": "EBITDA - D&A", "taxes": "EBIT x tax rate", "nopat": "EBIT - taxes", "capex": "Revenue x CapEx %",
         "nwc": "Revenue x NWC %", "dnwc": "NWC - prior NWC", "ufcf": "NOPAT + D&A - CapEx - change in NWC",
         "opex_pct": "Sanity check: R&D + SG&A ~ 16-19% historically"}
hist_link = {"revenue": "revenue", "growth": "growth", "gp": "gross_profit", "gm": "gm", "ebitda": "ebitda", "ebitda_m": "ebitda_m", "da": "da",
             "da_pct": "da_pct", "ebit": "ebit", "ebit_m": "ebit_m", "taxes": "taxes", "tax": "etr", "nopat": "nopat", "capex": "capex",
             "capex_pct": "capex_pct", "nwc": "nwc", "nwc_pct": "nwc_pct", "dnwc": "dnwc", "ufcf": "ufcf", "ufcf_m": "ufcf_m"}
drv_map = {"growth": "growth", "gm": "gm", "ebitda_m": "ebitda_m", "da_pct": "da_pct", "tax": "tax", "capex_pct": "capex_pct", "nwc_pct": "nwc_pct"}
for k, rr in FR.items():
    lbl, fmt = labels[k]
    bold = k in ("revenue", "ebitda", "ebit", "nopat", "ufcf")
    put(ws, f"B{rr}", lbl, F_B if bold else F_N)
    put(ws, f"M{rr}", logic.get(k, ""), F_NOTE)
    for i, (c, y) in enumerate(zip(ALLC, yrs)):
        if y <= 2025:
            if k == "opex_pct":
                f = f"={c}{FR['gm']}-{c}{FR['ebit_m']}"
                put(ws, f"{c}{rr}", f, F_N, fmt)
            else:
                put(ws, f"{c}{rr}", f"=Historical!{HC[y]}{HR[hist_link[k]]}", F_LINK, fmt)
            continue
        yi = y - 2026
        p = ALLC[i - 1]
        f = {
            "revenue": f"={p}{FR['revenue']}*(1+{c}{FR['growth']})",
            "gp": f"={c}{FR['revenue']}*{c}{FR['gm']}",
            "ebitda": f"={c}{FR['revenue']}*{c}{FR['ebitda_m']}",
            "da": f"={c}{FR['revenue']}*{c}{FR['da_pct']}",
            "ebit": f"={c}{FR['ebitda']}-{c}{FR['da']}",
            "ebit_m": f"={c}{FR['ebit']}/{c}{FR['revenue']}",
            "taxes": f"={c}{FR['ebit']}*{c}{FR['tax']}",
            "nopat": f"={c}{FR['ebit']}-{c}{FR['taxes']}",
            "capex": f"={c}{FR['revenue']}*{c}{FR['capex_pct']}",
            "nwc": f"={c}{FR['revenue']}*{c}{FR['nwc_pct']}",
            "dnwc": f"={c}{FR['nwc']}-{p}{FR['nwc']}",
            "ufcf": f"={c}{FR['nopat']}+{c}{FR['da']}-{c}{FR['capex']}-{c}{FR['dnwc']}",
            "ufcf_m": f"={c}{FR['ufcf']}/{c}{FR['revenue']}",
            "opex_pct": f"={c}{FR['gm']}-{c}{FR['ebit_m']}",
        }.get(k)
        if f is None:
            put(ws, f"{c}{rr}", f"=Assumptions!{FC[yi]}{DRV[drv_map[k]]['Live']}", F_LINK, fmt)
        else:
            put(ws, f"{c}{rr}", f, F_B if bold else F_N, fmt)
    if k in ("ebitda", "nopat"):
        for c in ALLC:
            ws[f"{c}{rr}"].border = B_TOP
    if k == "ufcf":
        for c in ALLC:
            ws[f"{c}{rr}"].border = B_TOTAL
r = FR["opex_pct"] + 2
put(ws, f"B{r}", "Revenue CAGR FY25A-FY30E", F_B)
put(ws, f"C{r}", f"=(L{FR['revenue']}/G{FR['revenue']})^(1/5)-1", F_B, PCT)
FR["cagr"] = r
put(ws, f"B{r + 1}", "Average forecast EBITDA margin", F_B)
put(ws, f"C{r + 1}", f"=AVERAGE(H{FR['ebitda_m']}:L{FR['ebitda_m']})", F_B, PCT)
FR["avg_m"] = r + 1
put(ws, f"B{r + 2}", "FY30E revenue vs 2030 company range (EUR 44-60bn) [S10]", F_N)
put(ws, f"C{r + 2}", f'=IF(L{FR["revenue"]}>{I.GUIDANCE_2030["rev_high"]},"Above range",IF(L{FR["revenue"]}<{I.GUIDANCE_2030["rev_low"]},"Below range","Within range"))', F_B)
ws.freeze_panes = "C5"

# ================================================================== WACC
ws = ws_w
title(ws, "Weighted Average Cost of Capital", "CAPM cost of equity, market-value weights. Inputs are linked from Assumptions (green).")
widths(ws, {"B": 44, "C": 14, "D": 80})
W = {}
rows_w = [
    ("sec", "Cost of equity"),
    ("rf", "Risk-free rate", f"={A['rf']}", PCT2, "10Y German Bund: EUR, long-duration, matches EUR cash flows"),
    ("beta_reg", "Regression beta (5Y monthly)", f"={A['beta_reg']}", "0.00", "Observed vs. market index; noisy for a single stock"),
    ("beta_u", "Industry unlevered beta", f"={A['beta_ind_u']}", "0.00", "Semiconductor equipment peers, cash-corrected (Damodaran)"),
    ("de", "ASML market D/E", "=C{debt}/C{mcap}", PCT2, "Debt / market capitalisation"),
    ("beta_l", "Relevered industry beta", "=C{beta_u}*(1+(1-C{tax})*C{de})", "0.00", "Hamada: Bu x (1 + (1 - t) x D/E)"),
    ("beta_w", "Weight on regression beta", f"={A['beta_w']}", PCT, ""),
    ("beta", "Selected beta", "=C{beta_w}*C{beta_reg}+(1-C{beta_w})*C{beta_l}", "0.00", "Blend of regression and bottom-up beta"),
    ("erp", "Equity risk premium", f"={A['erp']}", PCT2, "Implied mature-market ERP; Netherlands has no country premium"),
    ("ke", "Cost of equity (CAPM)", "=C{rf}+C{beta}*C{erp}", PCT2, "Rf + beta x ERP"),
    ("sec", "Cost of debt"),
    ("rf2", "Risk-free rate", "=C{rf}", PCT2, ""),
    ("spread", "Credit spread (A1 / A+)", f"={A['spread']}", PCT2, "Spread for single-A EUR corporate bonds"),
    ("kd", "Pre-tax cost of debt", "=C{rf2}+C{spread}", PCT2, "Rf + spread"),
    ("tax", "Tax rate (statutory)", f"={A['tax_marg']}", PCT, "Interest is deductible at the Dutch statutory rate"),
    ("kd_at", "After-tax cost of debt", "=C{kd}*(1-C{tax})", PCT2, "Kd x (1 - t)"),
    ("sec", "Capital structure (market values)"),
    ("price", "Share price (EUR)", f"={A['price']}", EUR, ""),
    ("shares", "Diluted shares (m)", f"={A['shares']}", NUM1, ""),
    ("mcap", "Market value of equity (E)", "=C{price}*C{shares}", NUM, "Price x diluted shares"),
    ("debt", "Debt (D)", f"={A['debt']}", NUM, "Book value used as proxy for market value (fair value ~ book for A1 issuer)"),
    ("cap", "Total capital (D + E)", "=C{mcap}+C{debt}", NUM, ""),
    ("we", "Equity weight E / (D + E)", "=C{mcap}/C{cap}", PCT2, ""),
    ("wd", "Debt weight D / (D + E)", "=C{debt}/C{cap}", PCT2, ""),
    ("sec", "WACC"),
    ("wacc_pre", "WACC (CAPM)", "=C{we}*C{ke}+C{wd}*C{kd_at}", PCT2, "E/(D+E) x Ke + D/(D+E) x Kd x (1 - t)"),
    ("adj", "Scenario adjustment", f"={A['wacc_adj']}", PCT2, "0 in Base; +/-0.5% in Bear/Bull"),
    ("wacc", "WACC applied in DCF", "=C{wacc_pre}+C{adj}", PCT2, ""),
]
r = 3
for item in rows_w:
    r += 1
    if item[0] == "sec":
        r += 1
        section(ws, r, item[1], 2, 4)
        continue
    W[item[0]] = r
r = 3
for item in rows_w:
    r += 1
    if item[0] == "sec":
        r += 1
        continue
    k, lbl, f, fmt, note = item
    for kk, vv in W.items():
        f = f.replace("{" + kk + "}", str(vv))
    is_link = f.startswith("=Assumptions")
    bold = k in ("ke", "kd_at", "wacc", "wacc_pre", "beta")
    put(ws, f"B{r}", lbl, F_B if bold else F_N)
    put(ws, f"C{r}", f, F_LINK if is_link else (F_B if bold else F_N), fmt)
    put(ws, f"D{r}", note, F_NOTE)
ws[f"C{W['wacc']}"].fill = FILL_OUT
ws[f"C{W['wacc']}"].border = B_BOX
A["wacc"] = f"WACC!$C${W['wacc']}"
A["wacc_pre"] = f"WACC!$C${W['wacc_pre']}"

# ================================================================== DCF
ws = ws_d
title(ws, "Discounted Cash Flow", "Valuation at the valuation date using the 28-Jun-26 balance sheet; FY26 counts only H2 cash flows (stub). EUR millions.")
widths(ws, {"B": 44, "C": 15, "D": 15, "E": 13, "F": 13, "G": 13, "H": 13, "I": 13, "J": 60})
put(ws, "B4", "EUR m")
for c, y in zip(FC, YEARS_F):
    put(ws, f"{c}4", f"FY{y % 100}E")
hdr_row(ws, 4, 2, 9)
for c in FC:
    ws[f"{c}4"].fill = FILL_FC
D = {}
put(ws, "B5", "Period end")
for i, c in enumerate(FC):
    put(ws, f"{c}5", f"={A['fy1_end']}" if i == 0 else f"=DATE(YEAR({FC[i - 1]}5)+1,12,31)", F_N, DATE)
put(ws, "B6", "Years from valuation date to period end")
for i, c in enumerate(FC):
    put(ws, f"{c}6", f"=({c}5-{A['val_date']})/365" if i == 0 else f"={FC[i - 1]}6+1", F_N, YRS)
put(ws, "B7", "Discount period (mid-year if switched on)")
for i, c in enumerate(FC):
    put(ws, f"{c}7", f"=IF({A['mid']}=1,{c}6/2,{c}6)" if i == 0 else f"=IF({A['mid']}=1,{c}6-0.5,{c}6)", F_N, YRS)
put(ws, "J7", "FY26 stub: mid-point of remaining period; later years: mid-year", F_NOTE)
put(ws, "B9", "Unlevered free cash flow", F_B)
for i, c in enumerate(FC):
    put(ws, f"{c}9", f"=Forecast!{FCOL[i]}{FR['ufcf']}", F_LINK, NUM)
put(ws, "B10", "Less: H1-26 actual UFCF (already in 28-Jun cash)")
put(ws, "E10", f"=-{A['h1_ufcf']}", F_LINK, NUM)
for c in FC[1:]:
    put(ws, f"{c}10", 0, F_N, NUM)
put(ws, "J10", "Avoids double counting: H1 cash flows are in the balance sheet already", F_NOTE)
put(ws, "B11", "Cash flow to discount", F_B)
for c in FC:
    put(ws, f"{c}11", f"={c}9+{c}10", F_B, NUM, border=B_TOP)
put(ws, "B12", "WACC")
for c in FC:
    put(ws, f"{c}12", f"={A['wacc']}", F_LINK, PCT2)
put(ws, "B13", "Discount factor")
for c in FC:
    put(ws, f"{c}13", f"=1/(1+{c}12)^{c}7", F_N, "0.0000")
put(ws, "B14", "PV of cash flow", F_B)
for c in FC:
    put(ws, f"{c}14", f"={c}11*{c}13", F_B, NUM)
put(ws, "B15", "Sum of PV of forecast cash flows", F_B)
put(ws, "C15", "=SUM(E14:I14)", F_B, NUM, border=B_TOTAL)
D["sum_pv"] = 15

r = 17
for j, t in enumerate(["Valuation", "Gordon Growth", "Exit Multiple", "Blended"]):
    put(ws, f"{CL(2 + j)}{r}", t)
hdr_row(ws, r, 2, 5)
dl = [
    ("tfcf", "Terminal-year UFCF (FY30E)", "=I9", "", NUM),
    ("g", "Terminal growth rate", f"={A['g']}", "", PCT2),
    ("tebitda", "Terminal-year EBITDA (FY30E)", "", f"=Forecast!L{FR['ebitda']}", NUM),
    ("mult", "Exit EV/EBITDA multiple", "", f"={A['exit']}", MULT),
    ("tv", "Terminal value at end FY30", "=C{tfcf}*(1+C{g})/(" + A["wacc"] + "-C{g})", "=D{tebitda}*D{mult}", NUM),
    ("tn", "Discount period for terminal value", "=$I$6", "=$I$6", YRS),
    ("pv_tv", "PV of terminal value", "=C{tv}/(1+" + A["wacc"] + ")^C{tn}", "=D{tv}/(1+" + A["wacc"] + ")^D{tn}", NUM),
    ("pv_fcf", "PV of forecast cash flows", "=$C$15", "=$C$15", NUM),
    ("ev", "Enterprise value", "=C{pv_fcf}+C{pv_tv}", "=D{pv_fcf}+D{pv_tv}", NUM),
    ("tv_share", "Terminal value % of EV", "=C{pv_tv}/C{ev}", "=D{pv_tv}/D{ev}", PCT),
    ("cash", "Plus: cash & short-term investments", f"={A['cash']}", f"={A['cash']}", NUM),
    ("debt", "Less: total debt", f"={A['debt']}", f"={A['debt']}", NUM),
    ("nonop", "Plus: non-operating investments", f"={A['nonop']}", f"={A['nonop']}", NUM),
    ("equity", "Equity value", "=C{ev}+C{cash}-C{debt}+C{nonop}", "=D{ev}+D{cash}-D{debt}+D{nonop}", NUM),
    ("shares", "Diluted shares (m)", f"={A['shares']}", f"={A['shares']}", NUM1),
    ("price", "Implied share price (EUR)", "=C{equity}/C{shares}", "=D{equity}/D{shares}", EUR),
    ("cur", "Current share price (EUR)", f"={A['price']}", f"={A['price']}", EUR),
    ("upside", "Upside / (downside)", "=C{price}/C{cur}-1", "=D{price}/D{cur}-1", PCT),
    ("impl", "Cross-check: implied exit multiple / implied g", "=C{tv}/D{tebitda}", "=(D{tv}*" + A["wacc"] + "-C{tfcf})/(D{tv}+C{tfcf})", None),
    ("rev_mult", "Reverse DCF: exit multiple implied by market price", "", "=((C{cur}*C{shares}-C{cash}+C{debt}-C{nonop}-C{pv_fcf})*(1+" + A["wacc"] + ")^D{tn})/D{tebitda}", MULT),
    ("rev_g", "Reverse DCF: perpetual growth implied by market price", "", "", PCT2),
]
r = 17
for k, *_ in dl:
    r += 1
    D[k] = r
for k, lbl, fc, fd, fmt in dl:
    rr = D[k]
    sub = lambda s: s and s.format(**{kk: vv for kk, vv in D.items()})
    bold = k in ("ev", "equity", "price", "upside", "tv")
    put(ws, f"B{rr}", lbl, F_B if bold else F_N)
    if fc:
        put(ws, f"C{rr}", sub(fc), F_LINK if fc.startswith("=Assumptions") else (F_B if bold else F_N), fmt)
    if fd:
        put(ws, f"D{rr}", sub(fd), F_LINK if fd.startswith("=Assumptions") else (F_B if bold else F_N), fmt)
ws[f"C{D['impl']}"].number_format = MULT
ws[f"D{D['impl']}"].number_format = PCT2
# reverse-DCF perpetual growth: solve TV needed, then g = (TV*W - FCF)/(TV + FCF)
rr = D["rev_g"]
need_tv = f"((C{D['cur']}*C{D['shares']}-C{D['cash']}+C{D['debt']}-C{D['nonop']}-C{D['pv_fcf']})*(1+{A['wacc']})^C{D['tn']})"
put(ws, f"C{rr}", f"=({need_tv}*{A['wacc']}-C{D['tfcf']})/({need_tv}+C{D['tfcf']})", F_N, PCT2)
ws[f"D{rr}"].value = None
# blended column
for k in ("ev", "equity", "price"):
    put(ws, f"E{D[k]}", f"={A['gw']}*C{D[k]}+(1-{A['gw']})*D{D[k]}", F_B, EUR if k == "price" else NUM)
put(ws, f"E{D['cur']}", f"={A['price']}", F_LINK, EUR)
put(ws, f"E{D['upside']}", f"=E{D['price']}/E{D['cur']}-1", F_B, PCT)
for k in ("ev", "equity"):
    for c in "CDE":
        ws[f"{c}{D[k]}"].border = B_TOP
for c in "CDE":
    ws[f"{c}{D['price']}"].fill = FILL_OUT
    ws[f"{c}{D['price']}"].border = B_BOX
notes = {
    "tv": "Gordon: FCF30 x (1 + g) / (WACC - g).  Exit: EBITDA30 x multiple",
    "tn": "Both terminal values discounted from end of FY30 (conservative)",
    "debt": "Bonds + commercial paper; US GAAP operating leases excluded (lease cost already in EBITDA)",
    "nonop": "Equity stakes (e.g. Mistral AI) and equity-method investments; their income is not in EBIT",
    "impl": "Gordon TV / EBITDA (x)  |  g implied by exit TV",
    "rev_mult": "Multiple needed in the Exit method to justify today's price",
    "rev_g": "Perpetual growth needed in the Gordon method to justify today's price",
}
for k, t in notes.items():
    put(ws, f"F{D[k]}", t, F_NOTE)
A.update({"ev_g": f"DCF!$C${D['ev']}", "ev_x": f"DCF!$D${D['ev']}", "ev_b": f"DCF!$E${D['ev']}",
          "eq_g": f"DCF!$C${D['equity']}", "eq_x": f"DCF!$D${D['equity']}", "eq_b": f"DCF!$E${D['equity']}",
          "p_g": f"DCF!$C${D['price']}", "p_x": f"DCF!$D${D['price']}", "p_b": f"DCF!$E${D['price']}",
          "up_b": f"DCF!$E${D['upside']}", "up_g": f"DCF!$C${D['upside']}", "up_x": f"DCF!$D${D['upside']}"})

# ================================================================== SENSITIVITY
ws = ws_s
title(ws, "Sensitivity Analysis", "Implied share price (EUR). Every cell is a live closed-form DCF; the grid re-centres on the live WACC, g and multiple. Base case boxed and shaded.")
widths(ws, {"B": 20, **{CL(c): 11 for c in range(3, 12)}, "L": 4, "M": 22, "N": 10})
put(ws, "M4", "Grid steps", F_SEC)
put(ws, "M5", "WACC step")
inp(ws, "N5", 0.005, PCT2)
put(ws, "M6", "Terminal growth step")
inp(ws, "N6", 0.0025, PCT2)
put(ws, "M7", "Exit multiple step")
inp(ws, "N7", 2.0, MULT)
BR = f"(DCF!$C${D['cash']}-DCF!$C${D['debt']}+DCF!$C${D['nonop']})"
SH = f"DCF!$C${D['shares']}"
PVF = "SUMPRODUCT(DCF!$E$11:$I$11,1/(1+{w})^DCF!$E$7:$I$7)"
GCOLS = [CL(c) for c in range(3, 12)]   # C..K


def grid(top, label_rows, row_fmt, center_ref, step_ref, cell_formula, base_row_ref):
    put(ws, f"B{top}", "", F_N)
    put(ws, f"C{top - 1}", "WACC →", F_B)
    put(ws, f"B{top}", label_rows, F_HDR, fill=FILL_HDR)
    for j, c in enumerate(GCOLS):
        f = f"={A['wacc']}" if j == 4 else f"=$G${top}+({j - 4})*$N$5"
        put(ws, f"{c}{top}", f, F_HDR, PCT2, FILL_HDR, align="center")
    for i in range(9):
        rr = top + 1 + i
        f = f"={center_ref}" if i == 4 else f"=$B${top + 5}+({i - 4})*{step_ref}"
        put(ws, f"B{rr}", f, F_B, row_fmt, FILL_SEC, align="center")
        for j, c in enumerate(GCOLS):
            put(ws, f"{c}{rr}", cell_formula(f"{c}${top}", f"$B{rr}"), F_N, EUR0, align="center")
    rng = f"C{top + 1}:K{top + 9}"
    ws.conditional_formatting.add(rng, ColorScaleRule(start_type="min", start_color="F8696B", mid_type="percentile", mid_value=50,
                                                      mid_color="FFFFFF", end_type="max", end_color="63BE7B"))
    base = ws[f"G{top + 5}"]
    base.border = B_BOX
    base.font = Font(name="Calibri", size=10, bold=True)
    base.fill = FILL_BASE
    # mark cells at / above current price
    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThanOrEqual", formula=[A["price"]], font=Font(bold=True, underline="single")))
    return top + 5


put(ws, "B4", "Table 1: WACC vs terminal growth (Gordon Growth method)", F_SEC)
t1 = grid(6, "g ↓  /  WACC →", PCT2, A["g"], "$N$6",
          lambda w, g: f"=({PVF.format(w=w)}+DCF!$I$9*(1+{g})/({w}-{g})/(1+{w})^DCF!$I$6+{BR})/{SH}", None)
put(ws, "B17", "Table 2: WACC vs exit EV/EBITDA multiple (Exit Multiple method)", F_SEC)
t2 = grid(19, "Multiple ↓  /  WACC →", MULT, A["exit"], "$N$7",
          lambda w, m: f"=({PVF.format(w=w)}+Forecast!$L${FR['ebitda']}*{m}/(1+{w})^DCF!$I$6+{BR})/{SH}", None)
put(ws, "B30", "Reading the tables: shaded cell = live base case and equals the DCF tab price. Bold underlined = implied price at or above today's share price.", F_NOTE)
put(ws, "B31", "Table 3: Blended price, WACC vs terminal growth (multiple held at base)", F_SEC)
t3 = grid(33, "g ↓  /  WACC →", PCT2, A["g"], "$N$6",
          lambda w, g: (f"={A['gw']}*(({PVF.format(w=w)}+DCF!$I$9*(1+{g})/({w}-{g})/(1+{w})^DCF!$I$6+{BR})/{SH})"
                        f"+(1-{A['gw']})*(({PVF.format(w=w)}+Forecast!$L${FR['ebitda']}*{A['exit']}/(1+{w})^DCF!$I$6+{BR})/{SH})"), None)
A["sens1_c"] = f"Sensitivity!$G${t1}"
A["sens2_c"] = f"Sensitivity!$G${t2}"
A["sens3_c"] = f"Sensitivity!$G${t3}"

# ================================================================== SCENARIOS
ws = ws_sc
title(ws, "Scenario Analysis", "Each case is a self-contained 5-year build off its own Assumptions row, so Bear, Base and Bull compute side by side regardless of the selector.")
widths(ws, {"B": 40, "C": 14, "D": 14, "E": 14, "F": 14, "G": 14, "H": 14, "I": 14, "J": 4, "K": 90})
# summary table
put(ws, "B4", "Summary")
for j, case in enumerate(M.CASES):
    put(ws, f"{CL(3 + j)}4", case)
hdr_row(ws, 4, 2, 5)
SUMROWS = ["cagr", "avg_m", "avg_capex", "wacc", "g", "mult", "ev_g", "ev_x", "ev_b", "eq_b", "p_g", "p_x", "p_b", "up_b"]
SUMLBL = {"cagr": ("Revenue CAGR FY25A-FY30E", PCT), "avg_m": ("Average EBITDA margin FY26-30", PCT),
          "avg_capex": ("Average CapEx % revenue", PCT), "wacc": ("WACC", PCT2), "g": ("Terminal growth", PCT2),
          "mult": ("Exit EV/EBITDA", MULT), "ev_g": ("Enterprise value (Gordon)", NUM), "ev_x": ("Enterprise value (Exit)", NUM),
          "ev_b": ("Enterprise value (blended)", NUM), "eq_b": ("Equity value (blended)", NUM), "p_g": ("Implied price, Gordon (EUR)", EUR),
          "p_x": ("Implied price, Exit (EUR)", EUR), "p_b": ("Implied price, blended (EUR)", EUR), "up_b": ("Upside / (downside), blended", PCT)}
SR = {k: 5 + i for i, k in enumerate(SUMROWS)}
for k, rr in SR.items():
    put(ws, f"B{rr}", SUMLBL[k][0], F_B if k.startswith("p_") or k == "up_b" else F_N)
put(ws, f"B{SR['up_b'] + 1}", "Current share price (EUR)")
put(ws, f"C{SR['up_b'] + 1}", f"={A['price']}", F_LINK, EUR)
r0 = SR["up_b"] + 3
section(ws, r0, "What drives each case", 2, 11)
for i, case in enumerate(M.CASES):
    put(ws, f"B{r0 + 1 + i}", case, F_B)
    put(ws, f"C{r0 + 1 + i}", I.SCENARIO_STORY[case], F_NOTE)
blk_start = r0 + 5
SC = {}
nwc25 = f"Historical!$H${HR['nwc']}"
rev25 = f"Historical!$H${HR['revenue']}"
for ci, case in enumerate(M.CASES):
    top = blk_start + ci * 22
    section(ws, top, f"{case} case build", 2, 11)
    put(ws, f"B{top + 1}", "EUR m")
    for c, y in zip(FC, YEARS_F):
        put(ws, f"{c}{top + 1}", f"FY{y % 100}E")
    hdr_row(ws, top + 1, 2, 9)
    rws = {k: top + 2 + i for i, k in enumerate(["revenue", "ebitda", "da", "ebit", "nopat", "capex", "nwc", "dnwc", "ufcf", "cf", "df", "pv"])}
    lb = {"revenue": "Revenue", "ebitda": "EBITDA", "da": "D&A", "ebit": "EBIT", "nopat": "NOPAT", "capex": "CapEx", "nwc": "NWC",
          "dnwc": "Change in NWC", "ufcf": "Unlevered FCF", "cf": "Cash flow to discount (FY26 net of H1 actual)", "df": "Discount factor", "pv": "PV of cash flow"}
    for k, rr in rws.items():
        put(ws, f"B{rr}", lb[k], F_B if k in ("ufcf", "pv", "revenue") else F_N)
        for yi, c in enumerate(FC):
            p = FC[yi - 1] if yi else None
            f = {
                "revenue": f"={(rev25 if yi == 0 else p + str(rr))}*(1+{drv('growth', case, yi)})",
                "ebitda": f"={c}{rws['revenue']}*{drv('ebitda_m', case, yi)}",
                "da": f"={c}{rws['revenue']}*{drv('da_pct', case, yi)}",
                "ebit": f"={c}{rws['ebitda']}-{c}{rws['da']}",
                "nopat": f"={c}{rws['ebit']}*(1-{drv('tax', case, yi)})",
                "capex": f"={c}{rws['revenue']}*{drv('capex_pct', case, yi)}",
                "nwc": f"={c}{rws['revenue']}*{drv('nwc_pct', case, yi)}",
                "dnwc": f"={c}{rws['nwc']}-{(nwc25 if yi == 0 else p + str(rws['nwc']))}",
                "ufcf": f"={c}{rws['nopat']}+{c}{rws['da']}-{c}{rws['capex']}-{c}{rws['dnwc']}",
                "cf": f"={c}{rws['ufcf']}" + (f"-{A['h1_ufcf']}" if yi == 0 else ""),
                "df": f"=1/(1+$C${top + 15})^DCF!{c}$7",
                "pv": f"={c}{rws['cf']}*{c}{rws['df']}",
            }[k]
            put(ws, f"{c}{rr}", f, F_B if k in ("ufcf", "pv") else F_N, "0.0000" if k == "df" else NUM)
    vr = top + 15
    vals = [
        ("wacc", "WACC", f"={A['wacc_pre']}+{scl('wacc_adj', case)}", PCT2),
        ("g", "Terminal growth", f"={scl('g', case)}", PCT2),
        ("mult", "Exit multiple", f"={scl('exit', case)}", MULT),
        ("sum_pv", "Sum PV of cash flows", f"=SUM(E{rws['pv']}:I{rws['pv']})", NUM),
        ("pv_tv_g", "PV terminal value (Gordon)", f"=I{rws['ufcf']}*(1+C{vr + 1})/(C{vr}-C{vr + 1})/(1+C{vr})^DCF!$I$6", NUM),
        ("pv_tv_x", "PV terminal value (Exit)", f"=I{rws['ebitda']}*C{vr + 2}/(1+C{vr})^DCF!$I$6", NUM),
    ]
    V = {}
    for i, (k, lbl, f, fmt) in enumerate(vals):
        V[k] = vr + i
        put(ws, f"B{vr + i}", lbl)
        put(ws, f"C{vr + i}", f, F_LINK if f.startswith("=Assumptions") else F_N, fmt)
    # outputs into summary
    col = CL(3 + ci)
    out = {
        "cagr": f"=(I{rws['revenue']}/{rev25})^(1/5)-1",
        "avg_m": f"=AVERAGE(Assumptions!$E${DRV['ebitda_m'][case]}:$I${DRV['ebitda_m'][case]})",
        "avg_capex": f"=AVERAGE(Assumptions!$E${DRV['capex_pct'][case]}:$I${DRV['capex_pct'][case]})",
        "wacc": f"=C{V['wacc']}", "g": f"=C{V['g']}", "mult": f"=C{V['mult']}",
        "ev_g": f"=C{V['sum_pv']}+C{V['pv_tv_g']}", "ev_x": f"=C{V['sum_pv']}+C{V['pv_tv_x']}",
        "ev_b": f"={A['gw']}*{col}{SR['ev_g']}+(1-{A['gw']})*{col}{SR['ev_x']}",
        "eq_b": f"={col}{SR['ev_b']}+{BR}",
        "p_g": f"=({col}{SR['ev_g']}+{BR})/{SH}", "p_x": f"=({col}{SR['ev_x']}+{BR})/{SH}",
        "p_b": f"={col}{SR['eq_b']}/{SH}", "up_b": f"={col}{SR['p_b']}/{A['price']}-1",
    }
    for k, f in out.items():
        put(ws, f"{col}{SR[k]}", f, F_B if k.startswith("p_") or k == "up_b" else F_N, SUMLBL[k][1])
    SC[case] = col
for k in ("p_b",):
    for case in M.CASES:
        ws[f"{SC[case]}{SR[k]}"].fill = FILL_OUT
ws.conditional_formatting.add(f"C{SR['up_b']}:E{SR['up_b']}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000", bold=True)))
ws.conditional_formatting.add(f"C{SR['up_b']}:E{SR['up_b']}", CellIsRule(operator="greaterThanOrEqual", formula=["0"], font=Font(color="007A33", bold=True)))
ws.freeze_panes = "C5"
A.update({f"sc_{k}_{c}": f"Scenarios!${SC[c]}${SR[k]}" for k in SR for c in M.CASES})

# ================================================================== DASHBOARD
ws = ws_db
title(ws, "ASML Holding N.V. | Valuation Dashboard", "Live summary of the model. Change inputs on Assumptions; everything here updates.")
widths(ws, {"B": 34, "C": 15, "D": 3, "E": 34, "F": 15, "G": 3, "H": 14, "I": 14, "J": 14, "K": 14, "L": 14, "M": 14, "N": 14, "O": 14})
kp = [
    ("Current share price", f"={A['price']}", EUR), ("DCF price, blended (headline)", f"={A['p_b']}", EUR),
    ("DCF price, Gordon Growth", f"={A['p_g']}", EUR), ("DCF price, Exit Multiple", f"={A['p_x']}", EUR),
    ("Potential upside / (downside)", f"={A['up_b']}", PCT), ("Bear case price (blended)", f"={A['sc_p_b_Bear']}", EUR),
    ("Base case price (blended)", f"={A['sc_p_b_Base']}", EUR), ("Bull case price (blended)", f"={A['sc_p_b_Bull']}", EUR),
]
kp2 = [
    ("Enterprise value (blended, EUR m)", f"={A['ev_b']}", NUM), ("Equity value (blended, EUR m)", f"={A['eq_b']}", NUM),
    ("WACC", f"={A['wacc']}", PCT2), ("Terminal growth rate", f"={A['g']}", PCT2),
    ("Exit EV/EBITDA", f"={A['exit']}", MULT), ("5-yr revenue CAGR FY25-30", f"=Forecast!$C${FR['cagr']}", PCT),
    ("Average forecast EBITDA margin", f"=Forecast!$C${FR['avg_m']}", PCT), ("Model checks", "=Checks!$C$4", None),
]
put(ws, "B4", "Valuation", F_SEC)
put(ws, "E4", "Model drivers", F_SEC)
put(ws, "B5", "Scenario shown:", F_NOTE)
put(ws, "C5", f"={A['scen_name']}", F_B)
for i, (lbl, f, fmt) in enumerate(kp):
    put(ws, f"B{6 + i}", lbl, F_B if i in (1, 4) else F_N)
    put(ws, f"C{6 + i}", f, F_B, fmt, FILL_OUT if i in (1, 4) else None, align="right")
for i, (lbl, f, fmt) in enumerate(kp2):
    put(ws, f"E{6 + i}", lbl)
    put(ws, f"F{6 + i}", f, F_B, fmt, align="right")
ws.conditional_formatting.add("C10", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000", bold=True)))
ws.conditional_formatting.add("C10", CellIsRule(operator="greaterThanOrEqual", formula=["0"], font=Font(color="007A33", bold=True)))
ws.conditional_formatting.add("F13", FormulaRule(formula=['$F$13="ALL PASS"'], font=Font(color="007A33", bold=True)))
ws.conditional_formatting.add("F13", FormulaRule(formula=['$F$13<>"ALL PASS"'], font=Font(color="C00000", bold=True)))
put(ws, "B14", "Verdict", F_B)
put(ws, "C14", f'=IF({A["up_b"]}>0.15,"Undervalued",IF({A["up_b"]}<-0.15,"Overvalued","Fairly valued"))', F_B, align="right")
put(ws, "B15", "Verdict band: more than +/-15% from market price", F_NOTE)
# chart data block
put(ws, "B17", "Chart data (linked)", F_SEC)
cd = 18
put(ws, f"B{cd}", "Year")
put(ws, f"B{cd + 1}", "Revenue (EUR m)")
put(ws, f"B{cd + 2}", "EBITDA margin")
put(ws, f"B{cd + 3}", "Unlevered FCF (EUR m)")
for i, (c, y) in enumerate(zip(ALLC, yrs)):
    col = CL(3 + i)
    put(ws, f"{col}{cd}", f"FY{y % 100}{'A' if y <= 2025 else 'E'}", F_B, align="center")
    put(ws, f"{col}{cd + 1}", f"=Forecast!{c}{FR['revenue']}", F_LINK, NUM)
    put(ws, f"{col}{cd + 2}", f"=Forecast!{c}{FR['ebitda_m']}", F_LINK, PCT)
    put(ws, f"{col}{cd + 3}", f"=Forecast!{c}{FR['ufcf']}", F_LINK, NUM)
widths(ws, {CL(3 + i): 15 for i in range(10)})
vr0 = cd + 5
put(ws, f"B{vr0}", "Valuation range (EUR / share)", F_B)
vrange = [("Current market price", f"={A['price']}"), ("Bear (blended)", f"={A['sc_p_b_Bear']}"), ("Base (blended)", f"={A['sc_p_b_Base']}"),
          ("Bull (blended)", f"={A['sc_p_b_Bull']}"), ("DCF Gordon Growth", f"={A['p_g']}"), ("DCF Exit Multiple", f"={A['p_x']}")]
for i, (lbl, f) in enumerate(vrange):
    put(ws, f"B{vr0 + 1 + i}", lbl)
    put(ws, f"C{vr0 + 1 + i}", f, F_LINK, EUR0)


def style_chart(ch, t, ytitle, w=17, h=8.5):
    ch.title = t
    ch.y_axis.title = ytitle
    ch.width, ch.height = w, h
    ch.legend = None
    ch.y_axis.majorGridlines = None
    ch.x_axis.delete = False
    ch.y_axis.delete = False


ch = BarChart()
ch.add_data(Reference(ws, min_col=2, max_col=12, min_row=cd + 1), titles_from_data=True, from_rows=True)
ch.set_categories(Reference(ws, min_col=3, max_col=12, min_row=cd))
style_chart(ch, "Revenue: FY21A-FY25A and FY26E-FY30E", "EUR m")
ch.series[0].graphicalProperties.solidFill = "2B4BFF"
ws.add_chart(ch, "H4")
ch = LineChart()
ch.add_data(Reference(ws, min_col=2, max_col=12, min_row=cd + 2), titles_from_data=True, from_rows=True)
ch.set_categories(Reference(ws, min_col=3, max_col=12, min_row=cd))
style_chart(ch, "EBITDA margin", "%")
ch.series[0].graphicalProperties.line.solidFill = "0B1F3A"
ch.series[0].graphicalProperties.line.width = 28000
ch.y_axis.number_format = "0%"
ws.add_chart(ch, "H22")
ch = BarChart()
ch.add_data(Reference(ws, min_col=2, max_col=12, min_row=cd + 3), titles_from_data=True, from_rows=True)
ch.set_categories(Reference(ws, min_col=3, max_col=12, min_row=cd))
style_chart(ch, "Unlevered free cash flow", "EUR m")
ch.series[0].graphicalProperties.solidFill = "0B1F3A"
ws.add_chart(ch, "B31")
ch = BarChart()
ch.type = "bar"
ch.add_data(Reference(ws, min_col=3, min_row=vr0 + 1, max_row=vr0 + 6), titles_from_data=False)
ch.set_categories(Reference(ws, min_col=2, min_row=vr0 + 1, max_row=vr0 + 6))
style_chart(ch, "Valuation range vs market price (EUR / share)", "EUR")
ch.series[0].graphicalProperties.solidFill = "2B4BFF"
ch.dataLabels = DataLabelList()
ch.dataLabels.showVal = True
ch.y_axis.number_format = "#,##0"
ws.add_chart(ch, "H40")

# ================================================================== CHECKS
ws = ws_ck
title(ws, "Model Integrity Checks", "Automatic tests. PASS = test met; CHECK = review the inputs. INFO = reported for judgement, not a pass/fail test.")
widths(ws, {"B": 62, "C": 16, "D": 12, "E": 70})
put(ws, "B4", "Overall status", F_B)
for j, t in enumerate(["Test", "Value", "Status", "What it guards against"]):
    put(ws, f"{CL(2 + j)}6", t)
hdr_row(ws, 6, 2, 5)
tol = 0.01
checks = [
    ("WACC > terminal growth (live)", f"={A['wacc']}-{A['g']}", f"=IF(C{{r}}>0,\"PASS\",\"CHECK\")", PCT2, "Gordon formula explodes / turns negative if g >= WACC"),
    ("WACC > terminal growth in every scenario", f"=MIN({A['sc_wacc_Bear']}-{A['sc_g_Bear']},{A['sc_wacc_Base']}-{A['sc_g_Base']},{A['sc_wacc_Bull']}-{A['sc_g_Bull']})",
     "=IF(C{r}>0,\"PASS\",\"CHECK\")", PCT2, "Same test for Bear / Base / Bull"),
    ("EV reconciles: EV - (sum PV FCF + PV TV), Gordon", f"={A['ev_g']}-(SUMPRODUCT(DCF!E11:I11,DCF!E13:I13)+DCF!C{D['pv_tv']})",
     f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", NUM1, "Independent recomputation of EV"),
    ("EV reconciles, Exit", f"={A['ev_x']}-(SUMPRODUCT(DCF!E11:I11,DCF!E13:I13)+DCF!D{D['pv_tv']})",
     f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", NUM1, ""),
    ("Equity bridge: equity - (EV + cash - debt + investments)", f"={A['eq_g']}-({A['ev_g']}+{A['cash']}-{A['debt']}+{A['nonop']})",
     f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", NUM1, "Bridge items applied once with correct signs"),
    ("Forecast UFCF = NOPAT + D&A - CapEx - change in NWC (sum of errors)",
     f"=SUMPRODUCT(ABS(Forecast!H{FR['ufcf']}:L{FR['ufcf']}-(Forecast!H{FR['nopat']}:L{FR['nopat']}+Forecast!H{FR['da']}:L{FR['da']}-Forecast!H{FR['capex']}:L{FR['capex']}-Forecast!H{FR['dnwc']}:L{FR['dnwc']})))",
     f"=IF(C{{r}}<{tol},\"PASS\",\"CHECK\")", NUM1, "Formula consistency across forecast years"),
    ("Historical gross profit ties to sales - COGS", f"=SUMPRODUCT(ABS(Historical!D{HR['gp_check']}:H{HR['gp_check']}))",
     "=IF(C{r}<0.5,\"PASS\",\"CHECK\")", NUM1, "Data entry errors in reported figures"),
    ("Forecast EBITDA margin < gross margin (all years)",
     f"=SUMPRODUCT(--(Forecast!H{FR['ebitda_m']}:L{FR['ebitda_m']}>=Forecast!H{FR['gm']}:L{FR['gm']}))",
     "=IF(C{r}=0,\"PASS\",\"CHECK\")", "0", "Opex cannot be negative"),
    ("EBITDA margins between 25% and 55% (economic realism)",
     f"=SUMPRODUCT((Forecast!H{FR['ebitda_m']}:L{FR['ebitda_m']}<0.25)+(Forecast!H{FR['ebitda_m']}:L{FR['ebitda_m']}>0.55))",
     "=IF(C{r}=0,\"PASS\",\"CHECK\")", "0", "Outside ASML's FY21-25 range of 34-39% plus headroom"),
    ("Implied opex % within 10-25% of revenue",
     f"=SUMPRODUCT((Forecast!H{FR['opex_pct']}:L{FR['opex_pct']}<0.10)+(Forecast!H{FR['opex_pct']}:L{FR['opex_pct']}>0.25))",
     "=IF(C{r}=0,\"PASS\",\"CHECK\")", "0", "Gross margin and EBITDA margin assumptions are mutually consistent"),
    ("Terminal value share of EV (Gordon) below 85%", f"=DCF!C{D['tv_share']}", "=IF(C{r}<0.85,\"PASS\",\"CHECK\")", PCT,
     "Valuation not dominated by the perpetuity"),
    ("Terminal value share of EV (Exit)", f"=DCF!D{D['tv_share']}", "=\"INFO\"", PCT, "High by construction for a growth company; see sensitivity"),
    ("Capital structure weights sum to 100%", f"=WACC!C{W['we']}+WACC!C{W['wd']}-1", f"=IF(ABS(C{{r}})<0.000001,\"PASS\",\"CHECK\")", PCT2, ""),
    ("Sensitivity table 1 centre = DCF Gordon price", f"={A['sens1_c']}-{A['p_g']}", f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", EUR,
     "Closed-form grid formula matches the full DCF"),
    ("Sensitivity table 2 centre = DCF Exit price", f"={A['sens2_c']}-{A['p_x']}", f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", EUR, ""),
    ("Sensitivity table 3 centre = DCF blended price", f"={A['sens3_c']}-{A['p_b']}", f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", EUR, ""),
    ("Selected scenario on Scenarios tab = main DCF (blended price)",
     f"=CHOOSE({A['scen']},{A['sc_p_b_Bear']},{A['sc_p_b_Base']},{A['sc_p_b_Bull']})-{A['p_b']}",
     f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", EUR, "Scenario engine and main model use identical logic"),
    ("Scenario ordering: Bear < Base < Bull", f"=AND({A['sc_p_b_Bear']}<{A['sc_p_b_Base']},{A['sc_p_b_Base']}<{A['sc_p_b_Bull']})",
     "=IF(C{r},\"PASS\",\"CHECK\")", None, "Output moves logically with assumptions"),
    ("Price falls when WACC rises (sensitivity row monotonic)", f"=AND(Sensitivity!C{t1}>Sensitivity!G{t1},Sensitivity!G{t1}>Sensitivity!K{t1})",
     "=IF(C{r},\"PASS\",\"CHECK\")", None, "Direction of WACC effect"),
    ("Price rises with terminal growth (sensitivity column monotonic)", f"=AND(Sensitivity!G{t1 - 4}<Sensitivity!G{t1},Sensitivity!G{t1}<Sensitivity!G{t1 + 4})",
     "=IF(C{r},\"PASS\",\"CHECK\")", None, "Direction of g effect"),
    ("No double counting: FY26 cash flow excludes H1 actual (stub)", f"=DCF!E11-(DCF!E9-{A['h1_ufcf']})", f"=IF(ABS(C{{r}})<{tol},\"PASS\",\"CHECK\")", NUM1,
     "H1-26 cash flows sit in the 28-Jun cash balance"),
    ("Balance-sheet date precedes valuation date", f"={A['val_date']}-{A['bs_date']}", "=IF(C{r}>0,\"PASS\",\"CHECK\")", "0", ""),
    ("Gordon implied exit multiple (for judgement)", f"=DCF!C{D['impl']}", "=\"INFO\"", MULT, "Compare with the exit multiple assumption"),
    ("Exit-method implied perpetual growth (for judgement)", f"=DCF!D{D['impl']}", "=IF(C{r}<" + A["wacc"] + ",\"INFO\",\"CHECK\")", PCT2,
     "Above long-run GDP growth = exit multiple embeds growth beyond FY30"),
]
r = 6
first = r + 1
for lbl, fv, fs, fmt, note in checks:
    r += 1
    put(ws, f"B{r}", lbl)
    put(ws, f"C{r}", fv, F_N, fmt, align="right")
    put(ws, f"D{r}", fs.replace("{r}", str(r)), F_B, align="center")
    put(ws, f"E{r}", note, F_NOTE)
last = r
put(ws, "C4", f'=IF(COUNTIF(D{first}:D{last},"CHECK")=0,"ALL PASS","REVIEW")', F_B, align="center", border=B_BOX)
ws.conditional_formatting.add(f"D{first}:D{last}", FormulaRule(formula=[f'D{first}="PASS"'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(color="006100", bold=True)))
ws.conditional_formatting.add(f"D{first}:D{last}", FormulaRule(formula=[f'D{first}="CHECK"'], fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(color="9C0006", bold=True)))
ws.conditional_formatting.add("C4", FormulaRule(formula=['$C$4="ALL PASS"'], fill=PatternFill("solid", fgColor="C6EFCE"), font=Font(color="006100", bold=True)))
ws.conditional_formatting.add("C4", FormulaRule(formula=['$C$4<>"ALL PASS"'], fill=PatternFill("solid", fgColor="FFC7CE"), font=Font(color="9C0006", bold=True)))
A["checks"] = "Checks!$C$4"

# ================================================================== COVER
ws = ws_cover
ws.sheet_view.showGridLines = False
widths(ws, {"A": 3, "B": 30, "C": 70})
put(ws, "B3", "ASML Holding N.V.", Font(name="Calibri", size=28, bold=True, color=NAVY))
put(ws, "B5", "Discounted Cash Flow Valuation", Font(name="Calibri", size=16, color="2B4BFF"))
meta = [("Ticker", "ASML (Euronext Amsterdam) / ASML (Nasdaq)"), ("Valuation date", f"={A['val_date']}"), ("Currency", "EUR, millions unless stated"),
        ("Analyst", I.ANALYST), ("Active scenario", f"={A['scen_name']}"), ("DCF price (blended)", f"={A['p_b']}"),
        ("Current share price", f"={A['price']}"), ("Upside / (downside)", f"={A['up_b']}"), ("Model checks", f"={A['checks']}")]
for i, (k, v) in enumerate(meta):
    put(ws, f"B{8 + i}", k, F_B)
    c = put(ws, f"C{8 + i}", v, F_N, align="left")
    if k == "Valuation date":
        c.number_format = DATE
    if "price" in k:
        c.number_format = EUR
    if "Upside" in k:
        c.number_format = PCT
put(ws, "B18", "Company", F_SEC)
put(ws, "C19", "ASML designs and builds the lithography systems that print circuit patterns onto silicon wafers. It is the sole supplier of EUV "
               "lithography, which every leading-edge logic and DRAM fab depends on. Revenue comes from system sales (EUV, DUV, metrology & inspection) "
               "and a growing, recurring installed-base business (service and upgrades).", F_N)
put(ws, "B24", "How to use", F_SEC)
howto = ["1. Change inputs only on Assumptions (blue on yellow). The scenario selector switches Bear / Base / Bull.",
         "2. Forecast, WACC, DCF, Sensitivity, Scenarios and Dashboard are 100% formulas.",
         "3. Checks tests the model; the status is shown above and on the Dashboard.",
         "Colour code: blue = hard-coded input; black = formula; green = link to another sheet; grey header = historical; blue header = forecast."]
for i, t in enumerate(howto):
    put(ws, f"B{25 + i}", t, F_N)
put(ws, "B30", "Sources", F_SEC)
for i, (k, (t, u)) in enumerate(I.SOURCES.items()):
    put(ws, f"B{31 + i}", f"[{k}] {t}", F_NOTE)
    put(ws, f"C{31 + i}", u, F_NOTE)
put(ws, f"B{32 + len(I.SOURCES)}", "For educational purposes only. Not investment advice.", F_NOTE)
ws["C19"].alignment = Alignment(wrap_text=True, vertical="top")
ws.row_dimensions[19].height = 75
ws.conditional_formatting.add("C16", FormulaRule(formula=['$C$16="ALL PASS"'], font=Font(color="007A33", bold=True)))

# print setup
for s in wb.worksheets:
    s.page_setup.orientation = "landscape"
    s.page_setup.fitToWidth = 1
    s.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("saved", OUT)

# ------------------------------------------------------------------ export for web app
web_dir = ROOT / "web" / "src" / "model"
web_dir.mkdir(parents=True, exist_ok=True)
hc = M.hist_calcs()
base = {c: M.run_case(c) for c in M.CASES}
export = {
    "meta": {"valuationDate": "%04d-%02d-%02d" % I.VALUATION_DATE, "balanceSheetDate": "%04d-%02d-%02d" % I.BALANCE_SHEET_DATE,
             "fy1End": "%04d-%02d-%02d" % I.FY1_END, "midYear": I.MID_YEAR, "gordonWeight": I.GORDON_WEIGHT, "analyst": I.ANALYST},
    "market": {k: v[0] for k, v in I.MARKET.items()},
    "waccInputs": {k: v[0] for k, v in I.WACC_IN.items()},
    "drivers": {k: {c: v[c] for c in M.CASES} for k, v in I.DRIVERS.items()},
    "driverWhy": {k: v["why"] for k, v in {**I.DRIVERS, **I.SCALARS}.items()},
    "scalars": {k: {c: v[c] for c in M.CASES} for k, v in I.SCALARS.items()},
    "story": I.SCENARIO_STORY,
    "hist": {str(y): {k: round(v, 4) for k, v in hc[y].items()} for y in range(2021, 2026)},
    "nwc2025": hc[2025]["nwc"],
    "revenue2025": I.HIST["revenue"][2025],
    "histRaw": {k: {str(y): v for y, v in d.items()} for k, d in I.HIST.items()},
    "sources": {k: {"title": t, "url": u} for k, (t, u) in I.SOURCES.items()},
    "expected": {c: {"gordon": base[c]["gordon"]["price"], "exit": base[c]["exit"]["price"], "blend": base[c]["blend"]["price"],
                     "wacc": base[c]["wacc"]} for c in M.CASES},
}
(web_dir / "inputs.json").write_text(json.dumps(export, indent=1), encoding="utf-8")
print("exported", web_dir / "inputs.json")
