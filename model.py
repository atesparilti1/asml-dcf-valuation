"""
Pure-Python mirror of the Excel DCF. Used to (1) cross-check every Excel formula
in verify_model.py and (2) export base outputs for the web app tests.
Logic must stay identical to build_model.py formulas.

Structure: FY26-FY30 explicit forecast (revenue built from units x ASP),
FY31-FY35 fade period (growth fades linearly to terminal g, margins held),
terminal value at end FY35.
"""
from datetime import date
from statistics import median

from data import inputs as I

CASES = ["Bear", "Base", "Bull"]
FY = [2026, 2027, 2028, 2029, 2030]
FADE = [2031, 2032, 2033, 2034, 2035]
ALL = FY + FADE


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
        mcap = I.YEAR_END_PRICE[y] * H["diluted_shares"][y]
        ev = mcap + H["debt_current"][y] + H["debt_noncurrent"][y] - H["cash"][y] - H["sti"][y]
        d["ev_ebitda"] = ev / d["ebitda"]
    return out


def wacc_pre(o=None):
    o = o or {}
    w = {k: v[0] for k, v in I.WACC_IN.items()}
    m = {k: v[0] for k, v in I.MARKET.items()}
    rf = o.get("rf", w["rf"])
    erp = o.get("erp", w["erp"])
    mcap = m["price"] * m["shares"]
    de = m["debt"] / mcap
    beta_ind_l = w["beta_ind_u"] * (1 + (1 - w["tax_marg"]) * de)
    beta = o.get("beta", w["beta_w"] * w["beta_reg"] + (1 - w["beta_w"]) * beta_ind_l)
    ke = rf + beta * erp
    kd = rf + w["spread"]
    kd_at = kd * (1 - w["tax_marg"])
    E, D = mcap / (mcap + m["debt"]), m["debt"] / (mcap + m["debt"])
    return dict(mcap=mcap, de=de, beta_ind_l=beta_ind_l, beta=beta, ke=ke, kd=kd, kd_at=kd_at,
                we=E, wd=D, wacc=E * ke + D * kd_at)


def periods(mid=I.MID_YEAR):
    val = date(*I.VALUATION_DATE)
    y0 = (date(*I.FY1_END) - val).days / 365
    yf = [y0 + i for i in range(len(ALL))]
    disc = [yf[0] / 2 if mid else yf[0]] + [(t - 0.5 if mid else t) for t in yf[1:]]
    return yf, disc


def revenue_build(case, volume_shift=0.0):
    """Segment revenue FY26-FY30. volume_shift scales units and non-unit system segments (web slider)."""
    R, B = I.REV_DRIVERS[case], I.REV_BASE_2025
    v = 1 + volume_shift
    prev = {"odv": B["odv"], "mi": B["mi"], "ib": B["ib"]}
    out = []
    for i in range(5):
        seg = {
            "nxe": R["nxe_u"][i] * v * R["nxe_p"][i],
            "exe": R["exe_u"][i] * v * R["exe_p"][i],
            "arfi": R["arfi_u"][i] * v * R["arfi_p"][i],
        }
        # other segments grow on their own (unshifted) prior-year base; the shift scales the level
        lvl = {k: prev[k] * (1 + R[k + "_g"][i]) for k in ("odv", "mi", "ib")}
        prev = lvl
        seg["odv"], seg["mi"], seg["ib"] = lvl["odv"] * v, lvl["mi"] * v, lvl["ib"]
        seg["total"] = sum(seg.values())
        out.append(seg)
    return out


def ltm_ebitda():
    h = I.H1
    return hist_calcs()[2025]["ebitda"] + h["ebit_h1_26"] + h["da_h1_26"] - h["ebit_h1_25"] - h["da_h1_25"]


def comps():
    mult = [ev / e for _, _, _, ev, e, *_ in I.COMPS]
    m = {k: v[0] for k, v in I.MARKET.items()}
    e = ltm_ebitda()
    bridge = m["cash"] - m["debt"] + m["nonop"]
    px = lambda x: (x * e + bridge) / m["shares"]
    lo, md, hi = min(mult), median(mult), max(mult)
    return dict(multiples=mult, low=lo, median=md, high=hi, ltm_ebitda=e,
                p_low=px(lo), p_med=px(md), p_high=px(hi), fpe_median=median(c[5] for c in I.COMPS))


def run_case(case, overrides=None):
    o = overrides or {}
    D = {k: list(v[case]) for k, v in I.DRIVERS.items()}
    S = {k: v[case] for k, v in I.SCALARS.items()}
    if "marginShift" in o:
        D["ebitda_m"] = [x + o["marginShift"] for x in D["ebitda_m"]]
        D["gm"] = [x + o["marginShift"] for x in D["gm"]]
    S.update({k: v for k, v in o.items() if k in S})
    h = hist_calcs()
    m = {k: v[0] for k, v in I.MARKET.items()}
    wp = wacc_pre(o)
    wacc = o.get("wacc", wp["wacc"] + S["wacc_adj"])
    g, mult = S["g"], S["exit"]
    rb = revenue_build(case, o.get("volumeShift", 0.0))

    rows, prev, prev_nwc = [], I.HIST["revenue"][2025], h[2025]["nwc"]
    for i, y in enumerate(ALL):
        if i < 5:
            r = rb[i]["total"]
            gr = r / prev - 1
            em, gm_, da_p, cx, nw, tx = (D["ebitda_m"][i], D["gm"][i], D["da_pct"][i], D["capex_pct"][i],
                                         D["nwc_pct"][i], D["tax"][i])
        else:  # fade: growth steps linearly from FY30 growth to g; other ratios held at FY30
            k = i - 4
            gr = rows[4]["growth"] + (g - rows[4]["growth"]) * k / I.FADE_YEARS
            r = prev * (1 + gr)
            em, gm_, da_p, cx, nw, tx = (D["ebitda_m"][4], D["gm"][4], D["da_pct"][4], D["capex_pct"][4],
                                         D["nwc_pct"][4], D["tax"][4])
        ebitda = r * em
        da = r * da_p
        ebit = ebitda - da
        tax = ebit * tx
        nopat = ebit - tax
        capex = r * cx
        nwc = r * nw
        dnwc = nwc - prev_nwc
        ufcf = nopat + da - capex - dnwc
        rows.append(dict(year=y, revenue=r, growth=gr, gp=r * gm_, ebitda=ebitda, ebitda_m=em, da=da, ebit=ebit,
                         taxes=tax, nopat=nopat, capex=capex, nwc=nwc, dnwc=dnwc, ufcf=ufcf))
        prev, prev_nwc = r, nwc

    yf, disc = periods()
    cf = [rows[0]["ufcf"] - m["h1_ufcf"]] + [r["ufcf"] for r in rows[1:]]
    pv = [c / (1 + wacc) ** t for c, t in zip(cf, disc)]
    sum_pv = sum(pv)
    sum_pv_explicit = sum(pv[:5])
    tn = yf[-1]
    last = rows[-1]
    tv_g = last["ufcf"] * (1 + g) / (wacc - g)
    tv_x = last["ebitda"] * mult
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
    res.update(rows=rows, rev_build=rb, cf=cf, pv=pv, sum_pv=sum_pv, sum_pv_explicit=sum_pv_explicit, wacc=wacc, g=g,
               exit_mult=mult, yf=yf, disc=disc, tn=tn, wacc_parts=wp,
               cagr=(rows[4]["revenue"] / I.HIST["revenue"][2025]) ** (1 / 5) - 1,
               avg_ebitda_m=sum(D["ebitda_m"]) / 5, avg_capex=sum(D["capex_pct"]) / 5,
               implied_exit=tv_g / last["ebitda"],
               implied_g=(tv_x * wacc - last["ufcf"]) / (tv_x + last["ufcf"]))
    need = (m["price"] * m["shares"] - bridge - sum_pv) * (1 + wacc) ** tn
    res["reverse"] = dict(multiple=need / last["ebitda"], g=(need * wacc - last["ufcf"]) / (need + last["ufcf"]))
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
              f"impl.mult {r['implied_exit']:.1f}x impl.g {r['implied_g']:.2%}  CAGR {r['cagr']:.1%}  FY30 rev {r['rows'][4]['revenue']:,.0f}  "
              f"rev {r['reverse']['multiple']:.1f}x/{r['reverse']['g']:.2%}")
    print("FY26 revenue by case:", {c: round(run_case(c)["rows"][0]["revenue"]) for c in CASES})
    print("comps", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in comps().items()})
    h = hist_calcs()
    print("hist EV/EBITDA", {y: round(h[y]["ev_ebitda"], 1) for y in range(2021, 2026)},
          "avg", round(sum(h[y]["ev_ebitda"] for y in range(2021, 2026)) / 5, 1))
    print(wacc_pre())
    b = run_case("Base")
    for r in b["rows"]:
        print(r["year"], round(r["revenue"]), f"{r['growth']:.1%}", round(r["ebitda"]), round(r["ufcf"]))
