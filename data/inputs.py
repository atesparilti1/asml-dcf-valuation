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
    "S9": ("Yahoo Finance monthly and daily prices: ASML.AS and STOXX Europe 600 (^STOXX); regression beta, 52-week range, year-end prices",
           "https://finance.yahoo.com/quote/ASML.AS/history/"),
    "S10": ("ASML 2024 Investor Day: 2030 revenue opportunity EUR 44-60bn, gross margin 56-60%",
            "https://investor.asml.com/news-releases/news-release-details/asml-provides-updated-view-market-opportunities-2024-investor-day-meeting"),
    "S11": ("ASML Q4 2025 press release: 2025 sales EUR 32.7bn, backlog EUR 38.8bn",
            "https://www.asml.com/en/news/press-releases/2026/q4-2025-financial-results"),
    "S12": ("Peer trading data (price, market cap, EV, TTM EBITDA, forward P/E, margins) for AMAT, LRCX, KLAC, Tokyo Electron, ASML, 7-8 Oct 2026, stockanalysis.com",
            "https://stockanalysis.com/stocks/amat/statistics/"),
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
FADE_YEARS = 5                           # FY31-FY35: growth fades linearly from FY30 rate to terminal g; margins held at FY30

# ---------------------------------------------------------------- market & latest balance sheet
MARKET = {
    "price":     (1611.40, "MARKET", "S5", "Closing price Euronext Amsterdam, 7 Oct 2026 (EUR)"),
    "shares":    (384.9, "REPORTED", "S4", "Diluted weighted avg. shares Q2 2026 (m)"),
    "cash":      (7581.5, "REPORTED", "S4", "Cash 6,671.9 + short-term investments 909.6 at 28 Jun 2026"),
    "debt":      (3697.7, "DERIVED", "S1/S4", "FY25 borrowings 4,390.9 (LT 2,709.0 + current 1,681.9 incl. ECP) less H1-26 repayments 693.2"),
    "nonop":     (2310.7, "REPORTED", "S4", "Equity investments 1,324.9 + equity-method investments 985.8 at 28 Jun 2026"),
    "h1_ufcf":   (-1290.9, "DERIVED", "S4", "H1-26 CFO (482.5) - PP&E capex 701.8 - intangibles 106.6; already reflected in 28 Jun cash"),
    "low52":     (813.90, "MARKET", "S9", "52-week low close, Euronext Amsterdam (Oct-25 to Oct-26)"),
    "high52":    (1721.40, "MARKET", "S9", "52-week high close, Euronext Amsterdam (Oct-25 to Oct-26)"),
}

# LTM EBITDA to 28 Jun 2026 = FY25 + H1-26 - H1-25 (REPORTED, S4)
H1 = {"ebit_h1_26": 6613.9, "da_h1_26": 506.3, "ebit_h1_25": 5402.0, "da_h1_25": 496.2}

# ASML year-end closing prices (MARKET, S9) for historical EV/EBITDA
YEAR_END_PRICE = {2021: 706.70, 2022: 503.80, 2023: 681.70, 2024: 678.70, 2025: 921.40}

# Trading comparables (MARKET, S12). EV and EBITDA in billions of local currency; multiples are currency-neutral.
COMPS = [
    # name, ticker, ccy, EV (bn), EBITDA TTM (bn), forward P/E, gross margin, operating margin
    ("Applied Materials", "AMAT", "USD", 411.30, 10.16, 29.56, 0.494, 0.3122),
    ("Lam Research", "LRCX", "USD", 410.90, 8.64, 34.78, 0.5047, 0.3529),
    ("KLA", "KLAC", "USD", 258.11, 6.05, 36.20, 0.613, 0.4169),
    ("Tokyo Electron", "8035.T", "JPY", 27300.0, 778.34, 33.33, 0.4556, 0.2634),
]
ASML_TRADING = {"ev": 607.00, "ebitda": 13.49, "fpe": 32.93, "gm": 0.5273, "om": 0.3542}

WACC_IN = {
    "rf":          (0.0351, "MARKET", "S6", "German 10Y Bund yield 7 Oct 2026; EUR risk-free matching EUR cash flows"),
    "erp":         (0.0423, "MARKET", "S7", "Damodaran implied mature-market ERP, Netherlands CRP = 0"),
    "beta_reg":    (1.79, "DERIVED", "S9", "Regression vs STOXX Europe 600, 60 monthly returns Oct-21 to Sep-26 (R² 0.33, std. error ~0.34): too noisy to use alone"),
    "beta_ind_u":  (1.39, "MARKET", "S8", "Semiconductor equipment unlevered beta, cash-corrected"),
    "beta_w":      (0.0, "ASSUMPTION", "", "0% weight on regression: bottom-up industry beta is used (standard practice when the regression is imprecise)"),
    "spread":      (0.0060, "ASSUMPTION", "S1", "Credit spread for A1/A+ (Moody's/Fitch) EUR corporate issuer"),
    "tax_marg":    (0.258, "ASSUMPTION", "", "Dutch statutory CIT rate 25.8% for the interest tax shield"),
}

# ---------------------------------------------------------------- revenue build (units x ASP), FY26E..FY30E
# FY25 base year (REPORTED, S1 revenue disaggregation). ASP = segment sales / units, EUR m per system.
REV_BASE_2025 = {"nxe_u": 44, "nxe_rev": 10445.8, "exe_u": 4, "exe_rev": 1156.9, "arfi_u": 131, "arfi_rev": 10311.4,
                 "odv": 1735.6, "mi": 824.6, "ib": 8193.0}
# Anchors (S4, Q2-26 release): 2026 low-NA EUV capacity ~65 systems, DUV immersion ~130; +30% planned for 2027,
# a further +30% under investigation for 2028. FY26 calibrated to 2026 guidance of EUR 43-45bn (bear 43, base 44, bull 45).
REV_SEGMENTS = [
    # key, label, kind ("units"/"asp"/"growth"), unit label
    ("nxe_u", "EUV low-NA (NXE) systems", "units", "#"),
    ("nxe_p", "EUV low-NA ASP", "asp", "EUR m"),
    ("exe_u", "EUV High-NA (EXE) systems", "units", "#"),
    ("exe_p", "EUV High-NA ASP", "asp", "EUR m"),
    ("arfi_u", "DUV immersion (ArFi) systems", "units", "#"),
    ("arfi_p", "DUV immersion ASP", "asp", "EUR m"),
    ("odv_g", "Other DUV (dry, KrF, i-line) growth", "growth", "%"),
    ("mi_g", "Metrology & inspection growth", "growth", "%"),
    ("ib_g", "Installed base management growth", "growth", "%"),
]
REV_DRIVERS = {
    "Bear": {"nxe_u": [64, 66, 60, 66, 70], "nxe_p": [252, 250, 252, 255, 258],
             "exe_u": [8, 9, 10, 12, 14], "exe_p": [345, 350, 355, 360, 365],
             "arfi_u": [130, 110, 95, 100, 105], "arfi_p": [84, 84, 84, 85, 86],
             "odv_g": [-0.05, -0.10, -0.10, 0.0, 0.0], "mi_g": [0.10, 0.02, 0.0, 0.03, 0.03], "ib_g": [0.30, 0.04, 0.02, 0.04, 0.04]},
    "Base": {"nxe_u": [65, 75, 82, 86, 88], "nxe_p": [255, 260, 265, 270, 275],
             "exe_u": [8, 10, 14, 18, 22], "exe_p": [350, 360, 370, 380, 390],
             "arfi_u": [130, 145, 150, 145, 140], "arfi_p": [86, 87, 89, 91, 93],
             "odv_g": [0.0, 0.0, 0.0, 0.0, 0.0], "mi_g": [0.20, 0.10, 0.08, 0.06, 0.05], "ib_g": [0.30, 0.12, 0.10, 0.08, 0.07]},
    "Bull": {"nxe_u": [65, 84, 100, 106, 110], "nxe_p": [258, 262, 270, 277, 284],
             "exe_u": [9, 14, 20, 26, 32], "exe_p": [355, 370, 385, 395, 405],
             "arfi_u": [130, 165, 180, 175, 170], "arfi_p": [88, 89, 92, 94, 96],
             "odv_g": [0.02, 0.05, 0.0, 0.0, 0.0], "mi_g": [0.22, 0.14, 0.12, 0.10, 0.08], "ib_g": [0.31, 0.15, 0.13, 0.11, 0.10]},
}
REV_WHY = ("Units are anchored to ASML's stated capacity: ~65 low-NA EUV and ~130 DUV immersion systems in 2026, +30% planned for 2027 and "
           "+30% being studied for 2028. Base runs below full capacity from 2028 (utilisation ~80%). ASPs start from FY25 actuals (NXE EUR 237m, "
           "ArFi EUR 79m) and rise 2%/yr with mix (NXE:3800E, NXT:2100i). High-NA ramps from 4 R&D tools to 22 in 2030. Installed base +30% in "
           "2026 (H1-26: +28%), then grows with the fleet. FY26 total is calibrated to the EUR 43-45bn guidance.")

DRIVERS = {
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
        "label": "Exit EV/EBITDA multiple (on FY35 EBITDA)", "unit": "x",
        "Bear": 15.0, "Base": 20.0, "Bull": 25.0,
        "why": "Applied to FY35 EBITDA, after growth has faded to the terminal rate. ASML's FY21-25 average year-end EV/EBITDA is ~30x and peers trade at "
               "~42x trailing today (Comps tab), but both reflect a high-growth phase. A mature 2035 ASML deserves a discount: 20x is a third below its own average.",
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
    "Base": "2026 guidance is delivered, the backlog converts, and EUV/High-NA adoption in logic and DRAM lift revenue to about EUR 64bn by 2030 (88 low-NA and 22 High-NA EUV systems) "
            "with margins at the 2030 target band.",
    "Bull": "A sustained AI-driven leading-edge build-out plus faster High-NA adoption push EUV shipments to 110 low-NA and 32 High-NA systems and revenue to about EUR 81bn, "
            "with gross margin at 60% and services scaling on the installed base.",
}

# 2030 guidance reference values (S10)
GUIDANCE_2030 = {"rev_low": 44000, "rev_high": 60000, "gm_low": 0.56, "gm_high": 0.60}

# ---------------------------------------------------------------- business mix FY2025 (REPORTED, S1 note 2 & segment note)
BUSINESS_2025 = {
    "technology": [  # net system sales per technology: (label, units, EUR m)
        ("EUV High-NA (EXE)", 4, 1156.9), ("EUV (NXE)", 44, 10445.8), ("DUV ArF immersion", 131, 10311.4),
        ("DUV ArF dry", 16, 427.0), ("DUV KrF", 78, 1001.3), ("DUV i-line", 54, 307.3), ("Metrology & inspection", 208, 824.6),
    ],
    "installed_base": 8193.0,   # net service and field option sales
    "end_use": [("Logic", 16054.1), ("Memory", 8420.2)],
    "region": [("China", 9519.7), ("Taiwan", 8337.9), ("South Korea", 8159.6), ("United States", 4089.1), ("Japan", 1420.9),
               ("Singapore", 608.4), ("EMEA", 524.3), ("Netherlands", 4.7), ("Rest of Asia", 2.7)],
    "largest_customer_pct": 0.239, "top2_pct": 0.380, "top4_pct": 0.612,
    "euv_units": {2024: 44, 2025: 48}, "backlog_eur_bn": 38.8,
}

MILESTONES = [  # company history (ASML corporate history page and annual reports)
    (1984, "Founded", "Joint venture of Philips and ASM International, starting in a shed next to a Philips office in Eindhoven."),
    (1995, "IPO", "Listed on Amsterdam and Nasdaq; full independence funds the R&D race against Nikon and Canon."),
    (2001, "Silicon Valley Group", "Acquisition adds US scale and the step-and-scan know-how behind the TWINSCAN platform."),
    (2010, "First EUV tool", "The NXE:3100 pre-production EUV system ships to a customer research fab after 20+ years of R&D."),
    (2012, "Customers co-invest", "Intel, TSMC and Samsung fund EUV development and take equity stakes, which locks in the ecosystem."),
    (2013, "Cymer", "Acquiring the EUV light-source maker secures the hardest part of the EUV supply chain."),
    (2016, "HMI", "E-beam metrology joins the portfolio and extends holistic lithography beyond the scanner."),
    (2019, "EUV in volume", "The first EUV-made chips reach consumer devices; EUV becomes mandatory below 7nm."),
    (2023, "High-NA", "The first EXE:5000 High-NA EUV system ships, extending the roadmap into the 2030s."),
    (2025, "Record year", "EUR 32.7bn sales, EUR 38.8bn backlog and 48 EUV systems recognised as AI demand broadens."),
]
