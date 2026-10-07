# ASML Holding N.V. - Discounted Cash Flow Valuation

A complete, formula-driven DCF valuation of ASML (Euronext: ASML), valued as of **7 October 2026**, with an interactive web version of the same model.

| | |
|---|---|
| **Base case value (blended DCF)** | **€1,103 per share** |
| Current share price (7 Oct 2026 close) | €1,611.40 |
| Upside / (downside) | **(31.6%)** |
| Range: Gordon Growth / Exit Multiple | €776 / €1,430 |
| Scenarios: Bear / Base / Bull | €543 / €1,103 / €1,718 |
| WACC / terminal growth / exit multiple | 8.80% / 2.50% / 25.0x EBITDA |
| Conclusion | Overvalued on base-case assumptions; the price needs a ~29x exit multiple or growth well beyond 2030 |

---

## Project overview
This project values ASML from first principles. It takes reported US GAAP filings and builds a 5-year operating forecast, unlevered free cash flows, WACC, terminal value (two methods), the EV-to-equity bridge and an implied share price. It then stress-tests the result with sensitivity tables and Bear/Base/Bull scenarios.

## Objective
To estimate ASML's intrinsic value per share and judge whether the market price is supported by defensible assumptions. The model is transparent enough that every number can be traced and explained in an interview.

## Company overview
ASML is the world's only supplier of EUV lithography systems, which every leading-edge logic and DRAM fab depends on. In FY2025 it reported **€32.7bn** of revenue, a **52.8%** gross margin and **€9.6bn** of net income. EUV made up 47% of system sales, and the installed-base business (service and upgrades) contributed **€8.2bn**. Four customers made up 61% of sales; China, Taiwan and South Korea together were 80%.

## Methodology
```
Reported financials (SEC XBRL)  ->  Historical ratios  ->  5-yr driver-based forecast
        -> UFCF = EBIT x (1 - t) + D&A - CapEx - change in NWC
        -> discount at WACC (CAPM, market-value weights, mid-year convention)
        -> terminal value: Gordon Growth and Exit Multiple (blended 50/50)
        -> EV + cash - debt + non-operating investments = equity value
        -> / diluted shares = implied price  ->  sensitivity, scenarios, checks
```
**Timing.** Valuation date 7 Oct 2026; balance sheet at 28 Jun 2026 (latest reported). FY2026 only counts the H2 cash flow (FY26E UFCF minus H1-26 actual), which avoids double counting cash already on the balance sheet.

## Historical analysis (FY2021-FY2025, € m)
| | FY21 | FY22 | FY23 | FY24 | FY25 |
|---|---:|---:|---:|---:|---:|
| Revenue | 18,611 | 21,173 | 27,559 | 28,263 | 32,667 |
| Growth | 33.1% | 13.8% | 30.2% | 2.6% | 15.6% |
| Gross margin | 52.7% | 50.5% | 51.3% | 51.3% | 52.8% |
| EBITDA margin | 38.8% | 33.5% | 35.5% | 35.2% | 37.7% |
| Effective tax rate | 15.2% | 15.0% | 15.8% | 18.6% | 17.7% |
| CapEx % revenue | 5.1% | 6.2% | 8.0% | 7.4% | 5.0% |
| NWC % revenue | (23.7%) | (32.2%) | (13.5%) | (23.6%) | (27.3%) |
| Unlevered FCF | 10,018 | 7,192 | 3,055 | 9,135 | 10,951 |

Key takeaways: growth is strong but cyclical (FY24 +2.6%), and margins expand with EUV mix. Working capital is negative because customers prepay EUV systems, and it is the main swing factor in free cash flow.

## Forecast assumptions (Base case)
| | FY26E | FY27E | FY28E | FY29E | FY30E |
|---|---:|---:|---:|---:|---:|
| Revenue growth | 34.7% | 16.0% | 10.0% | 7.0% | 5.0% |
| Revenue (€ m) | 44,000 | 51,040 | 56,143 | 60,074 | 63,077 |
| EBITDA margin | 41.0% | 42.0% | 42.5% | 43.0% | 43.0% |
| CapEx % revenue | 5.5% | 5.5% | 5.5% | 5.5% | 5.5% |
| NWC % revenue | (12%) | (12%) | (12%) | (12%) | (12%) |
| Tax rate | 17.5% | 17.5% | 17.5% | 17.5% | 17.5% |
| Unlevered FCF (€ m) | 9,038 | 15,973 | 17,485 | 18,773 | 19,577 |

FY26 is anchored on ASML's raised 2026 guidance of €43-45bn (Q2-26 results). Growth then fades toward the cycle average. Margins move toward the 2030 target band (gross margin 56-60%).

## WACC
| Input | Value | Source |
|---|---:|---|
| Risk-free rate (10Y Bund) | 3.51% | Trading Economics, 7 Oct 2026 |
| Beta (50% regression 1.12 / 50% relevered industry 1.40) | 1.26 | Yahoo Finance; Damodaran |
| Equity risk premium | 4.23% | Damodaran, Jan 2026 |
| Cost of equity | 8.83% | CAPM |
| After-tax cost of debt | 3.05% | Rf + 0.60% A-rated spread, 25.8% tax |
| Equity / debt weights | 99.4% / 0.6% | Market values |
| **WACC** | **8.80%** | |

## Terminal value
| | Gordon Growth | Exit Multiple |
|---|---:|---:|
| Assumption | g = 2.5% | 25.0x FY30 EBITDA |
| PV of FY26-30 FCF (€ bn) | 69.6 | 69.6 |
| PV of terminal value (€ bn) | 223.0 | 474.5 |
| Enterprise value (€ bn) | 292.6 | 544.1 |
| Terminal value share of EV | 76% | 87% |
| Implied price | €776 | €1,430 |
| Cross-check | implies 11.7x EBITDA | implies 5.7% perpetual g |

The two methods disagree, and that disagreement is the main finding. A reverse DCF shows the market price needs a **28.7x** exit multiple or **6.1%** perpetual growth.

## Sensitivity analysis
* WACC 6.8-10.8% x g 1.5-3.5% (Gordon): €550 - €1,412. No cell reaches the market price.
* WACC 6.8-10.8% x 17-33x EBITDA (Exit): €967 - €1,964. 24 of 81 cells reach the market price.

## Scenario analysis
| | Bear | Base | Bull |
|---|---:|---:|---:|
| Revenue CAGR FY25-30 | 7.5% | 14.1% | 18.5% |
| Avg EBITDA margin | 36.4% | 42.3% | 44.5% |
| WACC / g / multiple | 9.3% / 2.0% / 18x | 8.8% / 2.5% / 25x | 8.3% / 3.0% / 30x |
| Enterprise value (blended, € bn) | 202.8 | 418.3 | 655.2 |
| Implied price (blended) | €543 | €1,103 | €1,718 |
| Upside / (downside) | (66.3%) | (31.6%) | +6.6% |

## Key results
On base-case assumptions ASML looks **overvalued**: the blended DCF value of €1,103 is 32% below the market price. The business quality is not in question. The issue is that the market price only works with a high terminal multiple or with strong growth that continues well past 2030. Only the Bull case clears today's price.

## Files included
| File | Purpose |
|---|---|
| `ASML_DCF_Model.xlsx` | Main deliverable: 10-tab formula-driven model (Cover, Assumptions, Historical, Forecast, WACC, DCF, Sensitivity, Scenarios, Dashboard, Checks) |
| `data/inputs.py` | Every input with its type (Reported / Market / Derived / Assumption) and source |
| `build_model.py` | Generates the workbook from the inputs; exports data for the web app |
| `model.py` | Independent Python implementation of the same model |
| `verify_model.py` | Recalculates every Excel formula, matches it to `model.py` in all 3 scenarios, and scans for hard-coded outputs |
| `web/` | Interactive single-page version (React, Motion, Tailwind) with live sliders and the same model in TypeScript |
| `docs/ASML_Valuation_Report.md` | Full write-up: company, history, assumptions, valuation, conclusion, sources |
| `docs/Interview_Prep.md` | 60-90 second walkthrough and Q&A |
| `docs/CV_and_Portfolio.md` | CV bullets and portfolio description |

**Reproduce:** `pip install openpyxl formulas` then `python build_model.py && python verify_model.py`. For the web app: `cd web && npm install && npm run dev` (`npm test` checks parity with Excel).

### Model integrity
The Checks tab runs 24 automatic tests (21 PASS/FAIL tests plus 3 for information). They cover WACC > g in every scenario, EV and equity bridge reconciliation, UFCF formula consistency, historical data ties, margin realism, TV share of EV, sensitivity centre = model price, scenario engine = main model, monotonic responses to WACC and g, and no double counting of H1-26 cash flow. All pass in Bear, Base and Bull.

## Skills demonstrated
Financial statement analysis (US GAAP), driver-based forecasting, unlevered FCF, CAPM/WACC, Gordon Growth and exit-multiple terminal values, EV-to-equity bridge, stub-period and mid-year discounting, reverse DCF, sensitivity and scenario analysis, Excel model design (inputs vs formulas, audit checks, dashboard), Python automation, and React data visualisation.

## Disclaimer
Educational project. Not investment advice. Historical figures come from ASML's public filings. Forecasts and the valuation are the author's own assumptions and may be wrong.
