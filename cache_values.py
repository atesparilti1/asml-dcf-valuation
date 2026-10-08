"""
Writes calculated values into an openpyxl-generated workbook.

openpyxl saves formulas without results, so file previews (email, phone, GitHub)
show empty cells until Excel recalculates. This computes every formula with the
`formulas` engine and inserts each result as the cell's cached <v> value.
Excel still recalculates on open (fullCalcOnLoad), so the model stays live.
"""
import os
import re
import shutil
import tempfile
import zipfile
from html import escape
from pathlib import Path

import formulas
import numpy as np

CELL = re.compile(r'<c r="([A-Z]+\d+)"([^>]*)><f>(.*?)</f><v\s*/></c>', re.S)


def _scalar(v):
    v = getattr(v, "value", v)
    if isinstance(v, np.ndarray):
        v = v.ravel()[0] if v.size else None
    if isinstance(v, (list, tuple)):
        v = v[0][0] if v and isinstance(v[0], (list, tuple)) else (v[0] if v else None)
    if isinstance(v, np.generic):
        v = v.item()
    return v


def cache_values(path) -> int:
    path = Path(path)
    sol = formulas.ExcelModel().loads(str(path)).finish(circular=False).calculate()
    vals = {}
    for k, v in sol.items():
        m = re.match(r"'\[(.+?)\](.+?)'!([A-Z]+\d+)$", k)
        if m:
            vals[(m.group(2).upper(), m.group(3))] = _scalar(v)

    zin = zipfile.ZipFile(path)
    wb = zin.read("xl/workbook.xml").decode()
    rels = zin.read("xl/_rels/workbook.xml.rels").decode()
    target = {}
    for rel in re.findall(r"<Relationship [^>]*/>", rels):
        rid = re.search(r'Id="([^"]+)"', rel).group(1)
        tgt = re.search(r'Target="([^"]+)"', rel).group(1)
        target[rid] = tgt.lstrip("/") if tgt.startswith("/") else "xl/" + tgt
    sheet_file = {}
    for s in re.findall(r"<sheet [^>]*/>", wb):
        nm = re.search(r'name="([^"]+)"', s).group(1)
        rid = re.search(r'r:id="([^"]+)"', s).group(1)
        sheet_file[target[rid]] = nm.upper()

    count = 0

    def fill(sheet):
        def rep(m):
            nonlocal count
            ref, attrs, f = m.groups()
            v = vals.get((sheet, ref))
            if v is None or isinstance(v, str) and v.startswith("#") or type(v).__name__ in ("XlError", "Error"):
                return m.group(0)
            if isinstance(v, bool):
                count += 1
                return f'<c r="{ref}"{attrs} t="b"><f>{f}</f><v>{int(v)}</v></c>'
            if isinstance(v, (int, float)):
                if v != v or v in (float("inf"), float("-inf")):
                    return m.group(0)
                count += 1
                return f'<c r="{ref}"{attrs}><f>{f}</f><v>{repr(float(v))}</v></c>'
            count += 1
            return f'<c r="{ref}"{attrs} t="str"><f>{f}</f><v>{escape(str(v), quote=False)}</v></c>'
        return rep

    fd, tmp = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    tmp = Path(tmp)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in sheet_file:
                data = CELL.sub(fill(sheet_file[item.filename]), data.decode()).encode()
            zout.writestr(item, data)
    zin.close()
    shutil.move(tmp, path)
    return count
