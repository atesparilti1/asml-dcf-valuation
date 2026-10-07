"""
Pure-Python mirror of the Excel DCF. Used to (1) cross-check every Excel formula
in verify_model.py and (2) export base outputs for the web app tests.
Logic must stay identical to build_model.py formulas.
"""
from datetime import date
from data import inputs as I

CASES = ["Bear", "Base", "Bull"]
FY = [2026, 2027, 2028, 2029, 2030]


def hist_calcs():
    H = I.HIST
    out = {}
    for y in range(2021, 2026):
        rev = H["revenue"][y]
        ebit = H["ebit"][y]
        da = H["da"][y]
        etr = H["tax"][y] / H["pretax"][y]
        capex = H["capex_ppe"][y] + H["capex_intang"][y]
        out[y] = dict(revenue=rev, growth=rev / H["revenue"][y - 1] - 1,
                      gm=H["gross_profit"][y] / rev, ebitda=ebit + da, ebitda_m=(ebit + da) / rev,
                      da=da, da_pct=da / rev, ebit=ebit, ebit_m=ebit / rev, etr=etr,
                      taxes=ebit * etr, nopat=ebit * (1 - etr), capex=capex, capex_pct=capex / rev)
    for y in range(2020, 2026):
        nwc = (H["current_assets"][y] - H["cash"][y] - H["sti"][y] - H["loans_rec_cur"][y]) \
            - (H["current_liab"][y] - H["debt_current"][y]) - H["contract_liab_nc"][y]
        out.setdefault(y, {})["nwc"] = nwc
    for y in range(2021, 2026):
        d = out[y]
        d["nwc_pct"] = d["nwc"] / d["revenue"]
        d["dnwc"] = d["nwc"] - out[y - 1]["nwc"]
        d["ufcf"] = d["nopat"] + d["da"] - d["capex"] - d["dnwc"]
    return out


def wacc_pre():
    w = {k: v[0] for k, v in I.WACC_IN.items()}
    m = {k: v[0] for k, v in I.MARKET.items()}
    mcap = m["price"] * m["shares"]
    de = m["debt"] / mcap
    beta_ind_l = w["beta_ind_u"] * (1 + (1 - w["tax_marg"]) * de)
    beta = w["beta_w"] * w["beta_reg"] + (1 - w["beta_w"]) * beta_ind_l
    ke = w["rf"] + beta * w["erp"]
    kd = w["rf"] + w["spread"]
    kd_at = kd * (1 - w["tax_marg"])
    E, D = mcap / (mcap + m["debt"]), m["debt"] / (mcap + m["debt"])
    return dict(mcap=mcap, de=de, beta_ind_l=beta_ind_l, beta=beta, ke=ke, kd=kd, kd_at=kd_at,
                we=E, wd=D, wacc=E * ke + D * kd_at)


def periods(mid=I.MID_YEAR):
    val = date(*I.VALUATION_DATE)
    yf = [(date(y, 12, 31) - val).days / 365 for y in FY]
    # Excel: E5=(FYend-val)/365, F5=E5+1 ...
    yf = [yf[0] + i for i in range(5)]
    disc = [yf[0] / 2 if mid else yf[0]] + [(t - 0.5 if mid else t) for t in yf[1:]]
    return yf, disc


def run_case(case, overrides=None):
    o = overrides or {}
    D = {k: list(v[case]) for k, v in I.DRIVERS.items()}
    S = {k: v[case] for k, v in I.SCALARS.items()}
    D.update({k: v for k, v in o.items() if k in D})
    S.update({k: v for k, v in o.items() if k in S})
    h = hist_calcs()
    m = {k: v[0] for k, v in I.MARKET.items()}
    rev, prev, prev_nwc = [], I.HIST["revenue"][2025], h[2025]["nwc"]
    rows = []
    for i in range(5):
        r = prev * (1 + D["growth"][i])
        ebitda = r * D["ebitda_m"][i]
        da = r * D["da_pct"][i]
        ebit = ebitda - da
        tax = ebit * D["tax"][i]
        nopat = ebit - tax
        capex = r * D["capex_pct"][i]
        nwc = r * D["nwc_pct"][i]
        dnwc = nwc - prev_nwc
        ufcf = nopat + da - capex - dnwc
        rows.append(dict(revenue=r, gp=r * D["gm"][i], ebitda=ebitda, da=da, ebit=ebit, taxes=tax,
                         nopat=nopat, capex=capex, nwc=nwc, dnwc=dnwc, ufcf=ufcf))
        prev, prev_nwc = r, nwc
    wp = wacc_pre()
    wacc = o.get("wacc", wp["wacc"] + S["wacc_adj"])
    g, mult = S["g"], S["exit"]
    yf, disc = periods()
    cf = [rows[0]["ufcf"] - m["h1_ufcf"]] + [r["ufcf"] for r in rows[1:]]
    pv = [c / (1 + wacc) ** t for c, t in zip(cf, disc)]
    sum_pv = sum(pv)
    tn = yf[-1]
    tv_g = rows[-1]["ufcf"] * (1 + g) / (wacc - g)
    tv_x = rows[-1]["ebitda"] * mult
    bridge = m["cash"] - m["debt"] + m["nonop"]
    res = {}
    for k, tv in (("gordon", tv_g), ("exit", tv_x)):
        pv_tv = tv / (1 + wacc) ** tn
        ev = sum_pv + pv_tv
        eq = ev + bridge
        res[k] = dict(tv=tv, pv_tv=pv_tv, ev=ev, tv_share=pv_tv / ev, equity=eq,
                      price=eq / m["shares"], upside=eq / m["shares"] / m["price"] - 1)
    w = I.GORDON_WEIGHT
    res["blend"] = {k: w * res["gordon"][k] + (1 - w) * res["exit"][k] for k in ("ev", "equity", "price")}
    res["blend"]["upside"] = res["blend"]["price"] / m["price"] - 1
    res.update(rows=rows, cf=cf, pv=pv, sum_pv=sum_pv, wacc=wacc, g=g, exit_mult=mult, yf=yf, disc=disc,
               cagr=(rows[-1]["revenue"] / I.HIST["revenue"][2025]) ** (1 / 5) - 1,
               avg_ebitda_m=sum(D["ebitda_m"]) / 5, avg_capex=sum(D["capex_pct"]) / 5,
               implied_exit=tv_g / rows[-1]["ebitda"],
               implied_g=(tv_x * wacc - rows[-1]["ufcf"]) / (tv_x + rows[-1]["ufcf"]))
    return res


def price_at(case, wacc, g=None, mult=None, method="gordon"):
    o = {"wacc": wacc}
    if g is not None:
        o["g"] = g
    if mult is not None:
        o["exit"] = mult
    return run_case(case, o)[method]["price"]


if __name__ == "__main__":
    for c in CASES:
        r = run_case(c)
        print(f"{c:5s} WACC {r['wacc']:.2%}  Gordon {r['gordon']['price']:8.1f}  Exit {r['exit']['price']:8.1f}  "
              f"Blend {r['blend']['price']:8.1f} ({r['blend']['upside']:+.1%})  TV% {r['gordon']['tv_share']:.0%}/{r['exit']['tv_share']:.0%}  "
              f"impl.mult {r['implied_exit']:.1f}x impl.g {r['implied_g']:.2%}  CAGR {r['cagr']:.1%}")
    h = hist_calcs()
    for y in range(2021, 2026):
        d = h[y]
        print(y, {k: round(v, 3) if abs(v) < 5 else round(v) for k, v in d.items()})
    print(wacc_pre())
