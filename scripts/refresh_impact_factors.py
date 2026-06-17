#!/usr/bin/env python3
"""Refresh impact_factor + jcr_quartile in papers.bib from a Clarivate JCR xlsx.

papers.bib stores no ISSN, so journals are matched by normalized name /
abbreviation against the table's "Journal name" and "Abbreviated journal"
columns. JCR-only source: cas_quartile is never touched. sort_if is
recomputed from the new IF so list ordering stays correct.

Usage:
  python scripts/refresh_impact_factors.py "<xlsx>"            # dry run (default)
  python scripts/refresh_impact_factors.py "<xlsx>" --apply    # write papers.bib (+ .bak)
"""
import sys, re, json, shutil, datetime
from pathlib import Path
import openpyxl

REPO = Path(__file__).resolve().parent.parent
BIB = REPO / "_bibliography" / "papers.bib"

# Manual bridges for journals whose PubMed name doesn't normalize to the
# Clarivate name (acronym-style Clarivate titles). Keyed by norm(bib journal)
# -> norm(correct Clarivate journal name).
ALIASES = {
    "BMJ": "BMJ BRITISH MEDICAL JOURNAL",
    "QJM": "QJM AN INTERNATIONAL JOURNAL OF MEDICINE",
    "PSORIASIS": "PSORIASIS TARGETS AND THERAPY",
}


def clean_journal(s):
    """Reduce a PubMed-style journal name toward the Clarivate form:
    drop parentheticals, cut at ' : <abbrev>' / ' = <alt name>', strip leading 'The'."""
    if not s:
        return ""
    s = re.sub(r"\(.*?\)", " ", str(s))      # drop parentheticals
    s = re.split(r"\s[:=]\s", s)[0]          # cut at ' : ' or ' = '
    s = re.sub(r"^\s*the\s+", "", s, flags=re.I)  # leading 'The'
    return s


def norm(s):
    if not s:
        return ""
    s = clean_journal(s).upper()
    s = re.sub(r"[.,&\-:/]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def best_quartile(json_str, col_q):
    qs = []
    try:
        for c in json.loads(json_str or "[]"):
            q = c.get("quartile")
            if q and re.match(r"^Q[1-4]$", str(q)):
                qs.append(str(q))
    except Exception:
        pass
    if col_q and re.match(r"^Q[1-4]$", str(col_q)):
        qs.append(str(col_q))
    return min(qs) if qs else None  # Q1 < Q2 < ... -> best = min


def load_table(xlsx):
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["Journals"]
    rows = ws.iter_rows(values_only=True)
    header = list(next(rows))
    i = {h: n for n, h in enumerate(header)}
    NAME, ABBR, JIF, QCOL, JS = (i["Journal name"], i["Abbreviated journal"],
                                 i["2025 JIF"], i["JIF quartile"], i["Category quartiles JSON"])
    lut = {}
    for r in rows:
        name, abbr, jif, qcol, js = r[NAME], r[ABBR], r[JIF], r[QCOL], r[JS]
        try:
            jif_val = float(jif)
        except (TypeError, ValueError):
            jif_val = None
        rec = {"jif": jif_val, "quartile": best_quartile(js, qcol), "name": name}
        for k in (norm(name), norm(abbr)):
            if k:
                lut.setdefault(k, rec)
    return lut


def split_entries(text):
    """Yield (start, end) spans of each @...{...} entry by brace matching."""
    spans = []
    for m in re.finditer(r"@\w+\s*\{", text):
        depth, j = 0, m.end() - 1
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((m.start(), j + 1))
                    break
            j += 1
    return spans


def field(block, name):
    m = re.search(r"(?m)^\s*" + name + r"\s*=\s*\{(.*?)\}\s*,?\s*$", block)
    return m.group(1).strip() if m else None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    if not args:
        print("usage: refresh_impact_factors.py <xlsx> [--apply]")
        sys.exit(1)
    xlsx = args[0]
    lut = load_table(xlsx)
    print(f"table: {len(lut)} journal keys loaded")

    text = BIB.read_text(encoding="utf-8")
    spans = split_entries(text)
    print(f"bib: {len(spans)} entries")

    out = []
    last = 0
    stats = {"matched": 0, "unmatched": 0, "if_changed": 0, "q_changed": 0, "if_gained": 0}
    unmatched, diffs = [], []

    for s, e in spans:
        out.append(text[last:s])
        block = text[s:e]
        last = e
        journal = field(block, "journal")
        key = norm(journal) if journal else ""
        rec = lut.get(key) or (lut.get(ALIASES[key]) if key in ALIASES else None)
        if not journal:
            out.append(block); continue
        if not rec or rec["jif"] is None:
            stats["unmatched"] += 1
            unmatched.append(journal)
            out.append(block); continue
        stats["matched"] += 1
        old_if = field(block, "impact_factor")
        old_q = field(block, "jcr_quartile")
        new_if = f"{rec['jif']:.1f}"
        new_q = rec["quartile"] or old_q
        if old_if is None:
            stats["if_gained"] += 1
        elif old_if != new_if:
            stats["if_changed"] += 1
        if old_q != new_q:
            stats["q_changed"] += 1
        if (old_if != new_if) or (old_q != new_q):
            diffs.append((journal, old_if, new_if, old_q, new_q))

        # rewrite fields in-place
        nb = block
        sort_if = f"{rec['jif']:06.2f}"
        if re.search(r"(?m)^\s*impact_factor\s*=", nb):
            nb = re.sub(r"(?m)^(\s*impact_factor\s*=\s*\{).*?(\}\s*,?\s*)$", rf"\g<1>{new_if}\g<2>", nb)
        else:
            nb = re.sub(r"(?m)^(\s*journal\s*=.*\n)", rf"\g<1>  impact_factor={{{new_if}}},\n", nb, count=1)
        if new_q:
            if re.search(r"(?m)^\s*jcr_quartile\s*=", nb):
                nb = re.sub(r"(?m)^(\s*jcr_quartile\s*=\s*\{).*?(\}\s*,?\s*)$", rf"\g<1>{new_q}\g<2>", nb)
            else:
                nb = re.sub(r"(?m)^(\s*impact_factor\s*=.*\n)", rf"\g<1>  jcr_quartile={{{new_q}}},\n", nb, count=1)
        if re.search(r"(?m)^\s*sort_if\s*=", nb):
            nb = re.sub(r"(?m)^(\s*sort_if\s*=\s*\{).*?(\}\s*,?\s*)$", rf"\g<1>{sort_if}\g<2>", nb)
        out.append(nb)

    out.append(text[last:])
    new_text = "".join(out)

    print("\n=== STATS ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    from collections import Counter
    print(f"\n=== UNMATCHED journals ({len(set(unmatched))} distinct) ===")
    for j, c in Counter(unmatched).most_common():
        print(f"  {c:>3}  {j}")
    print(f"\n=== DIFFS (showing up to 60 of {len(diffs)}) ===")
    for journal, oi, ni, oq, nq in diffs[:60]:
        print(f"  {journal:<34} IF {str(oi):>6} -> {ni:<6}  Q {str(oq):>3} -> {nq}")

    if apply:
        ts = datetime.date(2026, 6, 17).isoformat()
        bak = BIB.with_suffix(f".bib.bak-if-{ts}")
        shutil.copy2(BIB, bak)
        BIB.write_text(new_text, encoding="utf-8")
        print(f"\nAPPLIED. backup -> {bak.name}")
    else:
        print("\n(dry run — no files written; pass --apply to write)")


if __name__ == "__main__":
    main()
