"""
Independent verification of ASML_DCF_Model.xlsx.
1. Recalculates every Excel formula with the `formulas` engine (no Excel needed).
2. Compares key outputs against the pure-Python model (model.py) for all three scenarios
   by flipping the scenario selector.
3. Confirms all integrity checks return PASS/INFO.
4. Scans calculation sheets for hard-coded numbers (only Assumptions/Historical may hold inputs).
Run:  python verify_model.py
"""
import re
import sys
from pathlib import Path

import formulas
import openpyxl

import model as M

ROOT = Path(__file__).parent
XL = ROOT / "ASML_DCF_Model.xlsx"
TOL = 0.01


def key(sheet, cell):
    return f"'[{XL.name}]{sheet.upper()}'!{cell}"


def find(ws, label, col="B"):
    for row in ws.iter_rows(min_col=2, max_col=2):
        if row[0].value == label:
            return row[0].row
    raise KeyError(label)


wb = openpyxl.load_workbook(XL)
dcf, sc, a, ck = wb["DCF"], wb["Scenarios"], wb["Assumptions"], wb["Checks"]
r_price = find(dcf, "Implied share price (EUR)")
r_ev = find(dcf, "Enterprise value")
scen_row = find(a, "Scenario selector (1 Bear, 2 Base, 3 Bull)")

xl = formulas.ExcelModel().loads(str(XL)).finish(circular=False)
fails = 0


def val(sol, sheet, cell):
    v = sol[key(sheet, cell)].value
    v = v[0][0] if hasattr(v, "__getitem__") and not isinstance(v, str) else v
    return v


for idx, case in enumerate(M.CASES, start=1):
    sol = xl.calculate(inputs={key("Assumptions", f"C{scen_row}"): idx})
    py = M.run_case(case)
    pairs = [("Gordon price", val(sol, "DCF", f"C{r_price}"), py["gordon"]["price"]),
             ("Exit price", val(sol, "DCF", f"D{r_price}"), py["exit"]["price"]),
             ("Blended price", val(sol, "DCF", f"E{r_price}"), py["blend"]["price"]),
             ("EV Gordon", val(sol, "DCF", f"C{r_ev}"), py["gordon"]["ev"])]
    for lbl, xv, pv in pairs:
        ok = abs(float(xv) - pv) < TOL * max(1, abs(pv)) / 100
        fails += not ok
        print(f"[{case:4s}] {lbl:14s} Excel {float(xv):12.2f}  Python {pv:12.2f}  {'OK' if ok else 'MISMATCH'}")
    status = []
    for r in range(7, ck.max_row + 1):
        if ck[f"B{r}"].value:
            s = val(sol, "Checks", f"D{r}")
            status.append(s)
            if s not in ("PASS", "INFO"):
                fails += 1
                print(f"   CHECK failed: {ck[f'B{r}'].value} -> {val(sol, 'Checks', f'C{r}')}")
    print(f"[{case:4s}] checks: {status.count('PASS')} PASS, {status.count('INFO')} INFO, {status.count('CHECK')} CHECK, overall {val(sol, 'Checks', 'C4')}")

# hard-code scan
num = re.compile(r"^-?\d+(\.\d+)?$")
for name in ["Forecast", "WACC", "DCF", "Scenarios", "Dashboard", "Checks"]:
    ws = wb[name]
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, (int, float)) and not isinstance(c.value, bool):
                # allowed: zero placeholders in DCF stub row
                if not (name == "DCF" and c.value == 0):
                    print(f"   hard-coded number on {name}!{c.coordinate}: {c.value}")
                    fails += 1
print("\nRESULT:", "ALL VERIFIED" if fails == 0 else f"{fails} issue(s)")
sys.exit(1 if fails else 0)
