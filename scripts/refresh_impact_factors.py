#!/usr/bin/env python3
"""Bulk-refresh impact_factor / jcr_quartile / sort_if in papers.bib from the
committed Clarivate JCR data (via jcr_lookup; source scripts/data/jcr_2025.json).

papers.bib stores no ISSN, so journals match by name / abbreviation. The
quartile reflects the best across the journal's categories (baked into the
data file). cas_quartile is not part of the schema. Run dry first, then
--apply (writes a timestamped .bak).

  python scripts/refresh_impact_factors.py            # dry run (default)
  python scripts/refresh_impact_factors.py --apply    # write papers.bib (+ .bak)

When a new JCR table is released: rebuild the data file first
(scripts/build_jcr_data.py <xlsx>), then run this.
"""
import sys
import re
import shutil
import datetime
from collections import Counter
from pathlib import Path

import jcr_lookup

REPO = Path(__file__).resolve().parent.parent
BIB = REPO / "_bibliography" / "papers.bib"


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
    apply = "--apply" in sys.argv
    text = BIB.read_text(encoding="utf-8")
    spans = split_entries(text)
    print(f"bib: {len(spans)} entries")

    out, last = [], 0
    stats = {"matched": 0, "unmatched": 0, "if_changed": 0, "q_changed": 0, "if_gained": 0}
    unmatched, diffs = [], []

    for s, e in spans:
        out.append(text[last:s])
        block = text[s:e]
        last = e
        journal = field(block, "journal")
        rec = jcr_lookup.lookup(name=journal) if journal else {}
        if not rec:
            if journal:
                stats["unmatched"] += 1
                unmatched.append(journal)
            out.append(block)
            continue
        stats["matched"] += 1
        old_if, old_q = field(block, "impact_factor"), field(block, "jcr_quartile")
        new_if = rec["impact_factor"]
        new_q = rec["jcr_quartile"] or old_q
        if old_if is None:
            stats["if_gained"] += 1
        elif old_if != new_if:
            stats["if_changed"] += 1
        if old_q != new_q:
            stats["q_changed"] += 1
        if old_if != new_if or old_q != new_q:
            diffs.append((journal, old_if, new_if, old_q, new_q))

        nb = block
        sort_if = f"{float(new_if):06.2f}"
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
    print(f"\n=== UNMATCHED ({len(set(unmatched))} distinct, kept as-is) ===")
    for j, c in Counter(unmatched).most_common():
        print(f"  {c:>3}  {j}")
    print(f"\n=== DIFFS (up to 60 of {len(diffs)}) ===")
    for journal, oi, ni, oq, nq in diffs[:60]:
        print(f"  {journal:<34} IF {str(oi):>6} -> {ni:<6}  Q {str(oq):>3} -> {nq}")

    if apply:
        bak = BIB.with_suffix(f".bib.bak-if-{datetime.date(2026, 6, 17).isoformat()}")
        shutil.copy2(BIB, bak)
        BIB.write_text(new_text, encoding="utf-8")
        print(f"\nAPPLIED. backup -> {bak.name}")
    else:
        print("\n(dry run — no files written; pass --apply to write)")


if __name__ == "__main__":
    main()
