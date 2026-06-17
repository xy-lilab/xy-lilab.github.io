#!/usr/bin/env python3
"""Build scripts/data/jcr_2025.json from a Clarivate JCR .xlsx export.

Run this (manually) whenever Clarivate releases a new JCR table:

    python scripts/build_jcr_data.py "科睿唯安 2026 年度 JCR 分区表(1).xlsx"

Then commit the regenerated scripts/data/jcr_2025.json. The big source .xlsx
is NOT committed (it is gitignored); only this slim derived file is. Needs
openpyxl (a build-time dep, not required at lookup time).
"""
import sys
import json
from pathlib import Path

import openpyxl

from jcr_lookup import best_quartile  # same directory

OUT = Path(__file__).resolve().parent / "data" / "jcr_2025.json"


def main():
    if len(sys.argv) < 2:
        print("usage: build_jcr_data.py <clarivate_jcr.xlsx>")
        sys.exit(1)
    xlsx = sys.argv[1]
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["Journals"]
    rows = ws.iter_rows(values_only=True)
    h = list(next(rows))
    i = {k: n for n, k in enumerate(h)}
    NAME, ABBR, ISSN, EISSN, JIF, QCOL, JS = (
        i["Journal name"], i["Abbreviated journal"], i["ISSN"], i["eISSN"],
        i["2025 JIF"], i["JIF quartile"], i["Category quartiles JSON"],
    )
    journals = []
    for r in rows:
        try:
            f = round(float(r[JIF]), 1)
        except (TypeError, ValueError):
            continue  # journals without a numeric JIF are not useful here
        journals.append({
            "n": r[NAME], "a": r[ABBR],
            "i": r[ISSN], "e": r[EISSN],
            "f": f, "q": best_quartile(r[JS], r[QCOL]),
        })
    out = {
        "meta": {
            "source": "Clarivate JCR (2025 JIF)",
            "source_file": Path(xlsx).name,
            "count": len(journals),
        },
        "journals": journals,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parents[2])}  ({len(journals)} journals, {OUT.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
