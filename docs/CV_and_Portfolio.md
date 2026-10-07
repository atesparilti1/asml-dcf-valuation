# CV bullets and portfolio description

## CV bullets (Projects section)

**ASML Holding N.V. - DCF Valuation** | Excel, Python, React | Oct 2026
- Built a fully formula-driven DCF of ASML in Excel from 5 years of US GAAP filings (SEC XBRL). It includes a 5-year driver-based forecast of revenue, margins, capex and working capital, unlevered FCF, and a CAPM-based WACC (8.8%).
- Valued the equity using Gordon Growth and Exit Multiple terminal values and an EV-to-equity bridge (€1,103 blended vs €1,611 market). A reverse DCF showed the market price implies a ~29x exit multiple.
- Stress-tested the result with 9x9 WACC/growth/multiple sensitivity tables, Bear/Base/Bull scenarios (€543-€1,718) and 21 automated integrity checks. A Python script independently verifies every formula.

*Shorter variant (if space is tight):*
- Built a 10-tab Excel DCF of ASML from SEC filings, with a 5-year forecast, WACC, two terminal value methods, sensitivity tables, scenario analysis and automated audit checks; estimated value of €1,103 per share vs €1,611 market.

---

## Portfolio description (~110 words)

**ASML: Discounted Cash Flow Valuation**

I built a complete DCF valuation of ASML, the sole supplier of EUV lithography. Starting from five years of reported US GAAP financials, I analysed growth, margins, tax, capex and ASML's unusual negative working capital. I then built a five-year operating forecast anchored on company guidance. I calculated WACC with CAPM and estimated terminal value using both the Gordon Growth and Exit Multiple methods. An EV-to-equity bridge produces an implied share price. Sensitivity tables, Bear/Base/Bull scenarios and a reverse DCF test what the market price assumes. The full model is in Excel, verified by Python, and published as an interactive web page where every assumption can be changed live.
