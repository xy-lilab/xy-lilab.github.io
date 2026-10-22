#!/usr/bin/env python3
"""Refresh a separate WoS Core Collection snapshot in Actions or locally.

Usage: python3 scripts/update_wos_citations.py [--evidence-dir /outside/repo/path]
Authentication uses WOS_API_KEY or the configured local Keychain.
The existing OpenAlex cache and bibliography are not modified.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

from update_citations import extract_dois_from_bib
from wos_client import query_documents


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "_data" / "wos_citations.yml"
BATCH_SIZE = 20
PAGE_SIZE = 50


def normalize_doi(value):
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()


def doi_query(entries):
    dois = [normalize_doi(entry["doi"]) for entry in entries]
    if any(not re.fullmatch(r'10\.\d{4,9}/[^\s"\\]+', doi) for doi in dois):
        raise ValueError("Invalid bibliography DOI; refusing to build a query")
    return "DO=(" + " OR ".join(f'"{doi}"' for doi in dois) + ")"


def fetch_batch(entries, cli=None, evidence_dir=None, batch_number=1):
    query = doi_query(entries)
    hits = []
    total = None
    page = 1
    while total is None or len(hits) < total:
        if cli:
            result = subprocess.run(
                [cli, "--query", query, "--limit", str(PAGE_SIZE), "--page", str(page)],
                check=True, capture_output=True, text=True, timeout=120,
            )
            data = json.loads(result.stdout)
        else:
            data = query_documents(query, PAGE_SIZE, page)
        if data.get("_request", {}).get("database") != "WOS":
            raise ValueError("The local CLI must query the WOS database")
        count = data["metadata"]["total"]
        batch_hits = data["hits"]
        if type(count) is not int or count < 0 or not isinstance(batch_hits, list):
            raise ValueError("Invalid WoS result structure")
        if total is not None and count != total:
            raise ValueError("WoS result count changed during pagination; retry")
        total = count
        if len(batch_hits) != min(PAGE_SIZE, total - len(hits)):
            raise ValueError("Incomplete WoS result page; existing snapshot preserved")
        hits.extend(batch_hits)
        if len({hit["uid"] for hit in hits}) != len(hits):
            raise ValueError("Duplicate WoS result across pages; retry")
        if evidence_dir:
            (evidence_dir / f"batch-{batch_number:03d}-page-{page:03d}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
            )
        page += 1
        time.sleep(0.25)
    return hits


def resolve_early_access_duplicate(matches):
    """Choose one final issue record only when identity and counts agree."""
    titles = {re.sub(r"\W+", "", html.unescape(re.sub(r"<[^>]+>", "", h.get("title", ""))).lower())
              for h in matches}
    authors = {tuple(a.get("wosStandard") or a.get("displayName", "")
                     for a in h.get("names", {}).get("authors", [])) for h in matches}
    counts = [[c.get("count") for c in h.get("citations", []) if c.get("db") == "WOS"]
              for h in matches]
    if (len(titles) != 1 or "" in titles or len(authors) != 1 or not all(authors)
            or any(not name for names in authors for name in names)):
        return None
    if any(len(c) != 1 or type(c[0]) is not int or c[0] < 0 for c in counts):
        return None
    if len({c[0] for c in counts}) != 1:
        return None
    final = [h for h in matches if "Early Access" not in h.get("types", [])]
    if len(final) != 1:
        return None
    source = final[0].get("source", {})
    if not source.get("volume") or not source.get("pages", {}).get("range"):
        return None
    return final[0]


def match_records(entries, hits):
    """Use exact DOI matches and WOS counts only; absence is never zero."""
    by_doi = {}
    for hit in hits:
        doi = normalize_doi(hit.get("identifiers", {}).get("doi", ""))
        by_doi.setdefault(doi, {})[hit["uid"]] = hit
    records = {}
    for entry in entries:
        matches = list(by_doi.get(normalize_doi(entry["doi"]), {}).values())
        record = {"doi": entry["doi"], "status": "unmatched"}
        if len(matches) > 1:
            final = resolve_early_access_duplicate(matches)
            if final:
                record["alternate_uids"] = sorted(h["uid"] for h in matches if h["uid"] != final["uid"])
                record["resolution"] = "final_issue_record_with_identical_title_authors_and_citation_count"
                matches = [final]
        if len(matches) > 1:
            record.update(status="ambiguous", candidate_uids=sorted(hit["uid"] for hit in matches))
        elif matches:
            hit = matches[0]
            record.update(status="count_unavailable", uid=hit["uid"])
            if hit.get("links", {}).get("record"):
                record["record_url"] = hit["links"]["record"]
            counts = [c["count"] for c in hit.get("citations", []) if c.get("db") == "WOS"]
            if len(counts) == 1:
                count = counts[0]
                if type(count) is not int or count < 0:
                    raise ValueError("Invalid WoS citation count; existing snapshot preserved")
                record.update(status="matched", citations=count)
        records[entry["key"]] = record
    return records


def write_snapshot(records, retrieved_at, output=OUTPUT):
    # JSON scalars are valid YAML; no extra serialization dependency is needed.
    dump = lambda value: json.dumps(value, ensure_ascii=False)
    lines = ["# Auto-generated by scripts/update_wos_citations.py; independent of OpenAlex.",
             'source: "Web of Science Core Collection"', 'database: "WOS"',
             f"retrieved_at: {dump(retrieved_at)}", "records:"]
    for key, record in records.items():
        lines.append(f"  {dump(key)}:")
        lines.extend(f"    {field}: {dump(value)}" for field, value in record.items())
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         prefix=".wos-citations-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write("\n".join(lines) + "\n")
        temporary.replace(output)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wos-cli", help="Optional external WoS CLI override")
    parser.add_argument("--evidence-dir", type=Path, help="Save raw responses outside this repository")
    args = parser.parse_args()
    if args.evidence_dir:
        args.evidence_dir = args.evidence_dir.expanduser().resolve()
        if args.evidence_dir.is_relative_to(REPO_ROOT):
            parser.error("Raw evidence must be saved outside the public repository")
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    entries = extract_dois_from_bib()
    if not entries or len({e["key"] for e in entries}) != len(entries):
        raise ValueError("Empty bibliography or duplicate bibliography keys")
    records = {}
    for start in range(0, len(entries), BATCH_SIZE):
        batch = entries[start:start + BATCH_SIZE]
        number = start // BATCH_SIZE + 1
        hits = fetch_batch(batch, args.wos_cli, args.evidence_dir, number)
        records.update(match_records(batch, hits))
        print(f"Checked {min(start + BATCH_SIZE, len(entries))}/{len(entries)} DOIs", flush=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    write_snapshot(records, retrieved_at)
    statuses = Counter(record["status"] for record in records.values())
    total = sum(record.get("citations", 0) for record in records.values())
    print(json.dumps({"records": len(records), "statuses": dict(statuses),
                      "matched_record_citations": total, "retrieved_at": retrieved_at}))


if __name__ == "__main__":
    main()
