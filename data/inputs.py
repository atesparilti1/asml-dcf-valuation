"""
Sourced inputs for the ASML DCF model. Single source of truth for the Excel
workbook (build_model.py), the Python check model (model.py) and the web app
(web/src/model/inputs.json, exported by build_model.py).

Every number is tagged:
  REPORTED   - taken from ASML filings (US GAAP), EUR millions unless noted
  MARKET     - market data observed at / near the valuation date
  DERIVED    - arithmetic on reported figures, method stated
  ASSUMPTION - analyst judgement, rationale stated
"""

# ---------------------------------------------------------------- sources
SOURCES = {
    "S1": ("ASML Form 20-F / Annual Report 2025 (US GAAP), filed 25 Feb 2026, incl. XBRL data",
           "https://www.sec.gov/Archives/edgar/data/937966/000162828026011378/asml-20251231.htm"),
    "S2": ("SEC EDGAR XBRL company facts for ASML (20-F filings FY2020-FY2025)",
           "https://data.sec.gov/api/xbrl/companyfacts/CIK0000937966.json"),
    "S3": ("ASML Financial Statements US GAAP Q4 2025 (Form 6-K, 28 Jan 2026)",
           "https://www.sec.gov/Archives/edgar/data/937966/000162828026003701/"),
    "S4": ("ASML Q2 2026 press release and Financial Statements US GAAP (Form 6-K, 15 Jul 2026)",
           "https://www.sec.gov/Archives/edgar/data/0000937966/000162828026048235/pressreleasefinancialresul.htm"),
    "S5": ("ASML (Euronext Amsterdam: ASML) closing price 7 Oct 2026, via stockanalysis.com",
           "https://stockanalysis.com/quote/ams/ASML/history/"),
    "S6": ("Germany 10Y Bund yield, 7 Oct 2026, Trading Economics",
           "https://tradingeconomics.com/germany/government-bond-yield"),
    "S7": ("A. Damodaran, Country risk premiums (Jan 2026): Netherlands total ERP 4.23%, CRP 0%",
           "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html"),
    "S8": ("A. Damodaran, Betas by sector (Jan 2026): Semiconductor Equip unlevered beta corrected for cash 1.39",
           "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html"),
    "S9": ("Yahoo Finance, ASML Beta (5Y monthly) 1.12",
           "https://finance.yahoo.com/quote/ASML/"),
    "S10": ("ASML 2024 Investor Day: 2030 revenue opportunity EUR 44-60bn, gross margin 56-60%",
            "https://investor.asml.com/news-releases/news-release-details/asml-provides-updated-view-market-opportunities-2024-investor-day-meeting"),
    "S11": ("ASML Q4 2025 press release: 2025 sales EUR 32.7bn, backlog EUR 38.8bn",
            "https://www.asml.com/en/news/press-releases/2026/q4-2025-financial-results"),
}

# ---------------------------------------------------------------- historicals (REPORTED, EUR m)
YEARS_HIST = [2020, 2021, 2022, 2023, 2024, 2025]   # FY2020 only used as NWC opening balance

HIST = {
    # income statement (S2; FY2024-25 cross-checked to S3)
    "revenue":        {2020: 13978.5, 2021: 18611.0, 2022: 21173.4, 2023: 27558.5, 2024: 28262.9, 2025: 32667.3},
    "cogs":           {2021: 8802.0, 2022: 10473.3, 2023: 13422.4, 2024: 13770.9, 2025: 15409.3},
    "gross_profit":   {2021: 9809.0, 2022: 10700.1, 2023: 14136.1, 2024: 14492.0, 2025: 17258.0},
    "rnd":            {2021: 2547.0, 2022: 3253.5, 2023: 3980.6, 2024: 4303.7, 2025: 4698.8},
    "sga":            {2021: 725.6, 2022: 945.9, 2023: 1113.2, 2024: 1165.7, 2025: 1257.8},
    "ebit":           {2021: 6750.1, 2022: 6500.7, 2023: 9042.3, 2024: 9022.6, 2025: 11301.4},
    "pretax":         {2021: 6705.5, 2022: 6456.1, 2023: 9083.5, 2024: 9042.4, 2025: 11406.1},
    "tax":            {2021: 1021.4, 2022: 969.9, 2023: 1435.8, 2024: 1680.6, 2025: 2013.4},
    "net_income":     {2021: 5883.2, 2022: 5624.2, 2023: 7839.0, 2024: 7571.6, 2025: 9609.4},
    # cash flow statement
    "da":             {2021: 471.0, 2022: 583.6, 2023: 739.8, 2024: 918.6, 2025: 1025.9},
    "capex_ppe":      {2021: 900.7, 2022: 1281.8, 2023: 2155.6, 2024: 2067.2, 2025: 1573.6},
    "capex_intang":   {2021: 39.6, 2022: 37.5, 2023: 40.6, 2024: 15.9, 2025: 57.6},
    "cfo":            {2021: 10845.8, 2022: 8486.8, 2023: 5443.4, 2024: 11166.2, 2025: 12658.5},
    # balance sheet (Dec 31)
    "cash":           {2020: 6049.4, 2021: 6951.8, 2022: 7268.3, 2023: 7004.7, 2024: 12735.9, 2025: 12916.0},
    "sti":            {2020: 1302.2, 2021: 638.5, 2022: 107.7, 2023: 5.4, 2024: 5.4, 2025: 405.9},
    "current_assets": {2020: 15930.0, 2021: 18190.2, 2022: 23064.9, 2023: 24393.9, 2024: 30737.4, 2025: 30616.1},
    # current loans receivable: new line from FY2025 (S3 shows '-' for FY2024); none in earlier balance sheets
    "loans_rec_cur":  {2020: 0.0, 2021: 0.0, 2022: 0.0, 2023: 0.0, 2024: 0.0, 2025: 266.1},
    "current_liab":   {2020: 6603.5, 2021: 12298.0, 2022: 17983.6, 2023: 16274.7, 2024: 20051.4, 2025: 24263.9},
    # current debt incl. commercial paper (FY2025: 990.2 bonds + 691.7 ECP, S1)
    "debt_current":   {2020: 15.4, 2021: 509.1, 2022: 746.2, 2023: 0.1, 2024: 1010.3, 2025: 1681.9},
    "debt_noncurrent": {2021: 4075.0, 2022: 3514.2, 2023: 4631.5, 2024: 3677.3, 2025: 2709.0},
    "contract_liab_nc": {2020: 1639.9, 2021: 3225.7, 2022: 5269.9, 2023: 4825.5, 2024: 5625.4, 2025: 3366.3},
    "diluted_shares": {2021: 410.4, 2022: 398.0, 2023: 394.1, 2024: 393.6, 2025: 388.9},
}

# ---------------------------------------------------------------- general
VALUATION_DATE = (2026, 10, 7)
BALANCE_SHEET_DATE = (2026, 6, 28)       # latest reported balance sheet (Q2 2026, S4)
FY1_END = (2026, 12, 31)
SCENARIO = 2                             # 1 Bear, 2 Base, 3 Bull
MID_YEAR = 1                             # 1 = mid-year discounting convention
GORDON_WEIGHT = 0.5                      # weight of Gordon Growth in blended DCF price
ANALYST = "Ates Parilti"

# ---------------------------------------------------------------- market & latest balance sheet
MARKET = {
    "price":     (1611.40, "MARKET", "S5", "Closing price Euronext Amsterdam, 7 Oct 2026 (EUR)"),
    "shares":    (384.9, "REPORTED", "S4", "Diluted weighted avg. shares Q2 2026 (m)"),
    "cash":      (7581.5, "REPORTED", "S4", "Cash 6,671.9 + short-term investments 909.6 at 28 Jun 2026"),
    "debt":      (3697.7, "DERIVED", "S1/S4", "FY25 borrowings 4,390.9 (LT 2,709.0 + current 1,681.9 incl. ECP) less H1-26 repayments 693.2"),
    "nonop":     (2310.7, "REPORTED", "S4", "Equity investments 1,324.9 + equity-method investments 985.8 at 28 Jun 2026"),
    "h1_ufcf":   (-1290.9, "DERIVED", "S4", "H1-26 CFO (482.5) - PP&E capex 701.8 - intangibles 106.6; already reflected in 28 Jun cash"),
}

WACC_IN = {
    "rf":          (0.0351, "MARKET", "S6", "German 10Y Bund yield 7 Oct 2026; EUR risk-free matching EUR cash flows"),
    "erp":         (0.0423, "MARKET", "S7", "Damodaran implied mature-market ERP, Netherlands CRP = 0"),
    "beta_reg":    (1.12, "MARKET", "S9", "Regression beta, 5Y monthly"),
    "beta_ind_u":  (1.39, "MARKET", "S8", "Semiconductor equipment unlevered beta, cash-corrected"),
    "beta_w":      (0.50, "ASSUMPTION", "", "Equal weight regression vs bottom-up: regression is noisy, industry beta captures cyclicality"),
    "spread":      (0.0060, "ASSUMPTION", "S1", "Credit spread for A1/A+ (Moody's/Fitch) EUR corporate issuer"),
    "tax_marg":    (0.258, "ASSUMPTION", "", "Dutch statutory CIT rate 25.8% for the interest tax shield"),
}

# ---------------------------------------------------------------- scenario drivers (ASSUMPTION), FY26E..FY30E
# FY26 growth anchored to 2026 guidance EUR 43-45bn (S4): bear 43.0bn, base 44.0bn, bull 45.0bn
def _g(target):
    return round(target / HIST["revenue"][2025] - 1, 4)

DRIVERS = {
    "growth": {
        "label": "Revenue growth", "unit": "%",
        "Bear": [_g(43000), 0.04, -0.03, 0.04, 0.04],
        "Base": [_g(44000), 0.16, 0.10, 0.07, 0.05],
        "Bull": [_g(45000), 0.24, 0.15, 0.10, 0.08],
        "why": "FY26 = 2026 guidance EUR 43-45bn (Q2-26). FY27 reflects record backlog and AI-driven capacity adds, then growth fades to "
               "~5% as the cycle normalises. Base FY30 revenue sits just above the 2030 range of EUR 44-60bn because FY26 already exceeds its low end.",
    },
    "gm": {
        "label": "Gross margin", "unit": "%",
        "Bear": [0.540, 0.510, 0.500, 0.510, 0.520],
        "Base": [0.550, 0.560, 0.565, 0.570, 0.570],
        "Bull": [0.555, 0.570, 0.580, 0.590, 0.600],
        "why": "FY26 guide 54-56%. Base trends to 57%, inside ASML's 2030 target band of 56-60% (EUV mix, High-NA maturing, services).",
    },
    "ebitda_m": {
        "label": "EBITDA margin", "unit": "%",
        "Bear": [0.395, 0.360, 0.345, 0.355, 0.365],
        "Base": [0.410, 0.420, 0.425, 0.430, 0.430],
        "Bull": [0.415, 0.435, 0.450, 0.460, 0.465],
        "why": "FY25A 37.7%, H1-26 op. margin 36.6% with H2 guided higher. Opex (R&D ~14% of sales) grows slower than revenue = operating leverage. "
               "Bear shows a downturn with R&D held flat in absolute terms.",
    },
    "da_pct": {
        "label": "D&A % revenue", "unit": "%",
        "Bear": [0.028, 0.030, 0.030, 0.030, 0.030],
        "Base": [0.028, 0.028, 0.028, 0.028, 0.028],
        "Bull": [0.028, 0.027, 0.027, 0.027, 0.027],
        "why": "FY21-25 range 2.5-3.3%, FY25 3.1%. The new capacity build-out lifts the absolute D&A level.",
    },
    "capex_pct": {
        "label": "CapEx % revenue", "unit": "%",
        "Bear": [0.060, 0.065, 0.065, 0.060, 0.060],
        "Base": [0.055, 0.055, 0.055, 0.055, 0.055],
        "Bull": [0.050, 0.050, 0.050, 0.050, 0.050],
        "why": "FY21-25 average 6.4% (peak 8.0% in FY23 capacity expansion, 5.0% in FY25). Base 5.5% as capex normalises but EUV/High-NA capacity is still added.",
    },
    "nwc_pct": {
        "label": "Net working capital % revenue", "unit": "%",
        "Bear": [-0.080, -0.060, -0.060, -0.060, -0.060],
        "Base": [-0.120, -0.120, -0.120, -0.120, -0.120],
        "Bull": [-0.150, -0.150, -0.150, -0.150, -0.150],
        "why": "ASML runs negative NWC because customers pay EUV down payments (contract liabilities). It was -27% in FY25 but fell to about -7% of LTM sales by Jun-26 "
               "as down payments were consumed. Base normalises to -12%, below the FY21-25 average.",
    },
    "tax": {
        "label": "Tax rate on EBIT", "unit": "%",
        "Bear": [0.180, 0.180, 0.180, 0.180, 0.180],
        "Base": [0.175, 0.175, 0.175, 0.175, 0.175],
        "Bull": [0.170, 0.170, 0.170, 0.170, 0.170],
        "why": "Effective tax rate FY21-25 15.0-18.6% (Dutch innovation box), FY25 17.7%. Pillar Two 15% minimum is not binding.",
    },
}

SCALARS = {
    "g": {
        "label": "Terminal growth rate", "unit": "%",
        "Bear": 0.020, "Base": 0.025, "Bull": 0.030,
        "why": "Long-run nominal growth: euro-area inflation ~2% + modest real growth in semiconductor content. It is kept below the risk-free rate (3.5%) and nominal GDP.",
    },
    "exit": {
        "label": "Exit EV/EBITDA multiple", "unit": "x",
        "Bear": 18.0, "Base": 25.0, "Bull": 30.0,
        "why": "ASML's 5-yr average EV/EBITDA is ~30x (35x forward in Aug-26). 25x applies a discount because growth has decelerated by FY30. "
               "Semi-equipment peers (AMAT, LRCX, KLAC) have traded at ~18-25x.",
    },
    "wacc_adj": {
        "label": "WACC adjustment vs. CAPM WACC", "unit": "%",
        "Bear": 0.005, "Base": 0.000, "Bull": -0.005,
        "why": "Bear prices extra risk for export-control and cyclical exposure. Bull assumes a lower risk premium for a structural AI capex cycle.",
    },
}

SCENARIO_STORY = {
    "Bear": "AI capex digestion in 2027-28 coincides with tighter China export controls (DUV immersion and servicing). "
            "Customers push out EUV orders, the down-payment float shrinks and margins compress as fixed R&D is held.",
    "Base": "2026 guidance is delivered, the backlog converts, and EUV/High-NA adoption in logic and DRAM grows revenue to about EUR 63bn by 2030 "
            "with margins at the 2030 target band.",
    "Bull": "A sustained AI-driven leading-edge build-out plus faster High-NA adoption push revenue beyond the 2030 range, "
            "with gross margin at 60% and services scaling on the installed base.",
}

# 2030 guidance reference values (S10)
GUIDANCE_2030 = {"rev_low": 44000, "rev_high": 60000, "gm_low": 0.56, "gm_high": 0.60}
