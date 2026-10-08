# Interview Preparation - ASML DCF

Numbers to remember: **€935 blended** (Gordon €759 / Exit €1,112) vs **€1,611** market, **(42%)**. Comps **€1,251-1,690**. WACC **9.4%** (beta 1.40), g **2.5%**, exit **20x FY35**. FY25 revenue **€32.7bn** to FY30E **€64bn**: 88 low-NA + 22 High-NA EUV systems. TV = **54%** of EV (Gordon). Reverse DCF: **33x** or **7.1%** g. Bear / Bull: **€478 / €1,587**.

---

## "Walk me through your DCF of ASML." (~80 seconds)

> I valued ASML as of 7 October 2026 with a ten-year unlevered DCF, built in Excel from its SEC filings and cross-checked against trading comps.
>
> History first: revenue grew from €18.6bn to €32.7bn over FY21-25, with EBITDA margins of 34-39% and a 15-19% tax rate. Working capital is negative because customers prepay EUV tools, which makes free cash flow volatile.
>
> I built revenue bottom-up: systems shipped times price for low-NA EUV, High-NA EUV and DUV immersion, plus service. Units are anchored to the capacity ASML announced: about 65 EUV tools in 2026, +30% in 2027. That gives €43.9bn for 2026, inside guidance, and €64bn by 2030. Margins rise to 43% through operating leverage. After 2030 I run a five-year fade where growth steps down to the 2.5% terminal rate.
>
> I discount at a 9.4% WACC: a 3.5% Bund yield, a bottom-up industry beta of 1.40 and a 4.2% ERP. ASML has almost no debt. Gordon gives €759 a share and a 20x exit multiple gives €1,112, so the blend is €935, 42% below the share price.
>
> Peers trade at 35-48x trailing EBITDA, which puts ASML at €1,250-1,690, in line with today's price. So my conclusion is that ASML is priced in line with its sector, but on its own cash flows the price needs 33x 2035 EBITDA or 7% perpetual growth. The market is betting the AI cycle lasts well beyond my forecast.

---

## Q&A

**Why did you choose ASML?**
It is the only EUV supplier and a bottleneck for AI chips, so the business quality is obvious. The valuation question is not: is a €620bn market cap justified? It's also a good modelling case, with negative working capital, published unit and capacity data, a net cash balance sheet and strong cyclicality.

**Why did you use a DCF?**
ASML's cash flows are forecastable: there is guidance, a €39bn backlog and published capacity plans. A DCF values the business on its own fundamentals. I paired it with trading comps because a DCF alone can't tell you whether the whole sector is mispriced or the model is too conservative. Showing both is the honest answer.

**How did you forecast revenue?**
Bottom-up, as units times average selling price for the three main system families. Then other DUV, metrology and installed base grow from their FY25 bases. Units are anchored to ASML's stated capacity (~65 low-NA EUV and ~130 DUV immersion in 2026, +30% for 2027, a further +30% being studied for 2028). A check flags any year above capacity. FY25 prices come from reported sales divided by units (NXE €237m, ArFi €79m), rising about 2% a year with mix. FY26 is calibrated to the €43-45bn guidance.

**How did you calculate WACC?**
CAPM. The risk-free rate is the 10-year Bund at 3.51%, because the cash flows are in euros. For beta I ran a regression against the STOXX Europe 600 and got 1.79, but with an R² of 0.33 and a standard error around 0.34 it's too imprecise. I used the bottom-up semiconductor-equipment beta instead: unlevered 1.39, relevered 1.40. With Damodaran's 4.23% ERP the cost of equity is 9.42%. Debt is 0.6% of capital, so WACC is 9.38%.

**Why did you choose your terminal growth rate?**
At 2.5% the business grows at roughly nominal euro-area GDP forever. It has to sit below long-run GDP and the risk-free rate. The fade period matters as much as g: rather than jumping from 6% growth straight to 2.5%, growth steps down over FY31-35, so the perpetuity starts from a mature business.

**Why use both Gordon Growth and Exit Multiple?**
They cross-check each other. Gordon is intrinsic but sensitive to g and WACC. The exit multiple anchors to market evidence, but today's multiples reflect today's growth. I set 20x for 2035: a third below ASML's 29.8x five-year average, because by then growth has faded. Gordon implies 10.7x and my 20x implies 5.6% perpetual growth, so even 20x still embeds some growth beyond 2035.

**What assumptions have the biggest impact on your valuation?**
How long growth lasts (the fade and terminal assumptions, which are 54-69% of EV), then WACC: ±1pp moves the blended value by about €80-100. Then EUV volumes and margins: +10% shipments lifts it to about €1,007, and 5pp lower margins cut it to €818.

**What are the weaknesses of your DCF?**
(1) Any finite-horizon DCF with a GDP-like terminal rate will undervalue a business that compounds into the 2030s. That's why I show comps alongside. (2) Terminal value is still more than half of EV. (3) The ASP and High-NA ramp are my estimates. (4) Beta is uncertain: the regression says 1.79, the industry says 1.40. (5) Peer EBITDA comes from a data provider, not from filings I recomputed.

**What happens if WACC increases?**
Value falls, and the terminal value falls hardest because it sits furthest out. In Gordon, WACC is also in the denominator (WACC - g), so the effect is non-linear. +1pp takes Gordon from €759 to €667 and Exit from €1,112 to €1,038.

**What happens if margins fall?**
EBITDA, NOPAT and FCF fall every year, and the exit-method terminal value falls one-for-one with FY35 EBITDA. 5pp lower margins take the blended value from €935 to €818 (-13%). The Bear case combines lower margins, lower volumes and higher capex intensity: €478.

---

## Likely follow-ups (one-liners)
* **Why did your value fall from the first version?** The bottom-up beta raised WACC from 8.8% to 9.4%, and the exit multiple now applies to a mature 2035 business. The fade period and bottom-up revenue partly offset this. I'd rather defend 9.4% than 8.8%.
* **Why a fade period?** Without it the model jumps from 6% growth to 2.5% in one year, which understates a compounder and inflates the terminal value's share of EV.
* **Why add equity investments in the bridge?** Their income is outside EBIT, so it isn't in the cash flows.
* **Why exclude leases from debt?** US GAAP operating lease cost is already in EBITDA, so adding lease liabilities would double count.
* **Stub period?** The balance sheet is from June, so I only count FY26 cash flow after June (FY26E minus H1 actual).
* **Model integrity?** There are 27 automatic checks (units within capacity, FY26 inside guidance, bridges reconcile, sensitivity centre = model price), and a Python script recalculates every formula.
