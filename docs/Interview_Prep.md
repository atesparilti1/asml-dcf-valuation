# Interview Preparation - ASML DCF

Numbers to remember: **€1,103 blended** (Gordon €776 / Exit €1,430) vs **€1,611** market, **(32%)**. WACC **8.8%**, g **2.5%**, exit **25x**. FY25 revenue **€32.7bn** to FY30E **€63bn** (14% CAGR). EBITDA margin **38% to 43%**. TV = **76%** of EV (Gordon). Reverse DCF: **~29x** or **6.1%** g. Bear / Bull: **€543 / €1,718**.

---

## "Walk me through your DCF of ASML." (~75 seconds)

> I valued ASML as of 7 October 2026 using an unlevered DCF built in Excel from its US GAAP filings.
>
> I started with five years of history. Revenue grew from €18.6bn to €32.7bn, EBITDA margins were 34-39%, and the tax rate was a low 15-19%. Working capital is negative because customers prepay EUV tools, which makes free cash flow volatile.
>
> For the forecast I anchored FY26 on ASML's raised guidance of €44bn. Growth then fades from 16% to 5% by 2030, reaching €63bn. EBITDA margins rise to 43% through operating leverage, in line with the company's 2030 gross-margin target. Unlevered FCF is EBIT after tax, plus D&A, minus capex at 5.5% of sales, minus the change in working capital.
>
> I discounted at an 8.8% WACC, which is basically the cost of equity: a 3.5% Bund yield, a beta of 1.26 and a 4.2% ERP. ASML has almost no debt. I used the June balance sheet, so I only counted the second-half 2026 cash flow, with mid-year discounting.
>
> For terminal value, Gordon Growth at 2.5% gives €776 a share and a 25x exit multiple gives €1,430. I blend them to €1,103, about 32% below the €1,611 share price. A reverse DCF shows the market needs a ~29x terminal multiple or growth well beyond 2030. So my conclusion is that on base-case assumptions the stock looks overvalued, even though it is an outstanding business. Only my Bull case, at €1,718, clears today's price.

---

## Q&A

**Why did you choose ASML?**
It is a European company with a unique position: the only EUV lithography supplier, which makes it a bottleneck for AI chips. The valuation question is genuinely interesting: the business quality is obvious, but the market price embeds very long-duration growth. It is also a good modelling case because of its negative working capital, cyclicality and net cash balance sheet.

**Why did you use a DCF?**
ASML has stable, cash-generative economics, low leverage and visible near-term demand (guidance plus a €39bn backlog), so its cash flows can be forecast reasonably. A DCF values the business on its own fundamentals rather than on where peers trade. I still use the exit multiple to anchor the terminal value to market evidence.

**How did you forecast revenue?**
Top-down growth rates, anchored to evidence. FY26 is the midpoint of the company's €43-45bn guidance. FY27 is +16%, reflecting the record backlog and AI-driven capacity. Then I fade growth to 5% by FY30 because semiconductor capex is cyclical and FY24 showed it can stall. I sense-checked FY30 at €63bn against ASML's 2030 range of €44-60bn. Being slightly above it is defensible because 2026 already sits at the bottom of that range. With more time I would build it bottom-up from EUV/DUV units times average selling price plus installed-base growth.

**How did you calculate WACC?**
CAPM for the cost of equity. The risk-free rate is the 10-year Bund (3.51%), because the cash flows are in euros. Beta is 1.26: a 50/50 blend of the 1.12 regression beta and the 1.40 relevered semiconductor-equipment industry beta, because single-stock regressions are noisy. The ERP is Damodaran's 4.23%. That gives a cost of equity of 8.83%. Debt is about 0.6% of capital at an after-tax 3.05%, so WACC is 8.80%. I use market values for the weights.

**Why did you choose your terminal growth rate?**
At 2.5% the business grows at roughly nominal euro-area GDP in perpetuity: about 2% inflation plus a little real growth. It must stay below the risk-free rate and long-run GDP, or the company would eventually become larger than the economy. I sensitise 1.5-3.5%.

**Why use both Gordon Growth and Exit Multiple?**
They cross-check each other. Gordon is intrinsic but very sensitive to g and WACC. The exit multiple is market-based but imports today's market sentiment into 2030. Here they disagree sharply: my Gordon value implies only 11.7x EBITDA, while my 25x multiple implies 5.7% perpetual growth. That gap tells me the market is paying for growth beyond my explicit forecast. I show both and blend 50/50.

**What assumptions have the biggest impact on your valuation?**
The terminal assumptions, because 76-87% of EV is terminal value. Then WACC: ±1pp moves the blended value by about €75-95. After that, post-2026 growth and the EBITDA margin: a 5pp lower margin in every year cuts the blended value from €1,103 to about €968. Working capital has a big effect on single years but a small one on value.

**What are the weaknesses of your DCF?**
(1) A five-year horizon for a company that may compound beyond 2030, so the jump from 5% growth to 2.5% perpetual growth may be too abrupt; a longer fade period would help. (2) The value is dominated by terminal value. (3) Growth is forecast top-down rather than from units and prices. (4) The beta and ERP are estimates with wide ranges. (5) The blend weighting is a judgement call. (6) There is no explicit modelling of share buybacks or dilution, beyond using diluted shares.

**What happens if WACC increases?**
Value falls, because every future cash flow is discounted more heavily, and the terminal value is hit hardest because it sits furthest out. In the Gordon formula WACC is also in the denominator (WACC - g), which makes the effect non-linear. From 8.8% to 9.8%, the Gordon value drops from €776 to €675 (-13%) and the exit value from €1,430 to €1,380 (-3.5%).

**What happens if margins fall?**
EBITDA falls, so NOPAT and FCF fall in every forecast year. Under the exit method the terminal value falls one-for-one with FY30 EBITDA. A 5pp lower EBITDA margin across all years cuts the blended value by about 12%, to €968. Margins also feed through capex intensity, which my Bear case adds on top: 36% margins and 6% capex give €543.

---

## Likely follow-ups (one-liners)
* **Why unlevered FCF?** It is the cash available to all capital providers, so it is discounted at WACC to give enterprise value. Capital structure is handled separately in the bridge.
* **Why add equity investments in the bridge?** Their income is outside EBIT, so it is not in the cash flows. Leaving them out would undervalue the company.
* **Why exclude leases from debt?** Under US GAAP operating lease cost is already in EBITDA. Adding lease liabilities would double count.
* **Stub period?** The valuation date is October and the balance sheet is from June, so I count only FY26 cash flow after June (FY26E minus H1 actual). That way the cash already received is not counted twice.
* **Mid-year convention?** Cash arrives through the year, not on 31 December, so each year is discounted from its midpoint.
* **Model integrity?** There are 21 automatic checks, and a Python script recalculates every Excel formula and matches it to an independent model.
