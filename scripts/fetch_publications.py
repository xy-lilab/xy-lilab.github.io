#!/usr/bin/env python3
"""
Refresh publication metadata and fetch new PubMed papers for the Li Lab.

Before the new-paper search, missing abstracts on existing public entries are
backfilled from PubMed, PMC, OpenAlex, then Semantic Scholar. Abstracts are
never generated.

Filters:
  1. Affiliation: Xiangya Hospital OR Central South University
  2. Lab members must be first author OR corresponding (last) author
  3. Only papers from 2020 onwards
  4. Skips papers already in the .bib file (by PMID)

Output:
  - Backfills authoritative abstracts on existing BibTeX entries
  - Appends new BibTeX entries to _bibliography/papers.bib
  - Prints a summary of new papers found
  - Exits with code 0 if no new papers, 1 if new papers added (for CI notification)
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from classify_paper import (
    classify as classify_paper,
    classify_type,
    classify_clinical_basic,
)

try:
    import jcr_lookup
except Exception:
    jcr_lookup = None


def lookup_journal_metrics(issn, eissn, journal_name, journal_abbrev):
    """Resolve JCR impact factor + quartile from the committed Clarivate JCR
    data (scripts/data/jcr_2025.json, 2025 JIF), matching by ISSN then by
    journal name / abbreviation. Returns {} when the journal is not in JCR.
    """
    if jcr_lookup is None:
        return {}
    return jcr_lookup.lookup(issn, eissn, journal_name, journal_abbrev)

# ── Configuration ──

REPO_ROOT = Path(__file__).resolve().parent.parent
BIB_FILE = REPO_ROOT / "_bibliography" / "papers.bib"
MEMBERS_FILE = REPO_ROOT / "_data" / "members.yml"

PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DOI_BIBTEX_URL = "https://doi.org/"
OPENALEX_WORKS = "https://api.openalex.org/works"
OPENALEX_EMAIL = "liji_xy@csu.edu.cn"
SEMANTIC_SCHOLAR_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch"

# Affiliation terms to match
AFFILIATIONS = [
    "Xiangya Hospital",
    "Central South University",
]

MIN_YEAR = 2026
WEB_MIN_YEAR = 2020
SECONDARY_INDEX_EXCLUDED_PUBLICATION_TYPES = {
    "case_report",
    "correction",
    "editorial",
    "letter",
}
INVALID_ABSTRACT_PUBLICATION_TYPES = {"correction", "editorial", "letter"}
INVALID_ABSTRACT_PATTERNS = (
    ("correction notice", r"^\[?(?:this )?(?:corrects?|correction|erratum|corrigendum)\b"),
    ("letter body", r"^(?:dear editor|to the editor|dear sir)\b"),
    ("editorial body", r"^editorial on\b"),
    ("data-availability statement", r"^(?:data availability|the data (?:that )?support|data (?:are|is) available)\b"),
    ("publisher disclaimer", r"publisher is not responsible for the content or functionality"),
)


# ── Helpers ──

def load_member_names():
    """Load lab member English names from members.yml (simple YAML parse)."""
    text = MEMBERS_FILE.read_text(encoding="utf-8")
    names = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("name_en:"):
            name = line.split(":", 1)[1].strip().strip('"').strip("'")
            if name:
                names.append(name)
    return names


def load_existing_ids():
    """Extract all PMIDs and DOIs already in the .bib file."""
    text = BIB_FILE.read_text(encoding="utf-8")
    pmids = set(re.findall(r"pmid\s*=\s*\{(\d+)\}", text))
    dois = set(d.lower() for d in re.findall(r"doi\s*=\s*\{([^}]+)\}", text))
    return pmids, dois


def pubmed_search(query, retmax=2000):
    """Search PubMed and return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
        "sort": "date",
    })
    url = f"{PUBMED_ESEARCH}?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("esearchresult", {}).get("idlist", [])


def pubmed_fetch(pmids):
    """Fetch full records from PubMed for given PMIDs. Returns XML root."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    })
    url = f"{PUBMED_EFETCH}?{params}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return ET.fromstring(resp.read())


def normalize_text(value):
    """Collapse metadata whitespace and remove any residual markup."""
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_abstract_text(parent):
    """Join every labelled PubMed AbstractText section into one abstract."""
    sections = []
    for element in parent.findall(".//AbstractText"):
        text = normalize_text("".join(element.itertext()))
        if not text:
            continue
        label = normalize_text(element.get("Label", ""))
        if label and not text.upper().startswith(f"{label.upper()}:"):
            text = f"{label}: {text}"
        sections.append(text)
    return " ".join(sections)


def fetch_pmc_abstract(pmcid):
    """Fetch an abstract from a PMC full-text XML record."""
    params = urllib.parse.urlencode({
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml",
    })
    try:
        with urllib.request.urlopen(f"{PUBMED_EFETCH}?{params}", timeout=30) as resp:
            root = ET.fromstring(resp.read())
    except Exception as exc:
        print(f"    Warning: PMC abstract lookup failed for {pmcid}: {exc}")
        return ""

    for abstract in root.findall(".//article-meta/abstract"):
        if abstract.get("abstract-type") in {"toc", "graphical", "executive-summary"}:
            continue
        parts = []
        title = normalize_text("".join(abstract.find("title").itertext())) if abstract.find("title") is not None else ""
        for paragraph in abstract.findall(".//p"):
            text = normalize_text("".join(paragraph.itertext()))
            if text:
                parts.append(text)
        result = " ".join(parts)
        if title and result and not result.upper().startswith(f"{title.upper()}:"):
            result = f"{title}: {result}"
        if result:
            return result
    return ""


def decode_openalex_abstract(inverted_index):
    """Reconstruct OpenAlex's position-indexed abstract representation."""
    if not inverted_index:
        return ""
    positioned_words = []
    for word, positions in inverted_index.items():
        positioned_words.extend((position, word) for position in positions)
    return normalize_text(" ".join(word for _, word in sorted(positioned_words)))


def fetch_openalex_abstract(doi):
    """Fetch an abstract from OpenAlex by exact DOI."""
    url = f"{OPENALEX_WORKS}/https://doi.org/{urllib.parse.quote(doi, safe='')}"
    if OPENALEX_EMAIL:
        url += f"?mailto={urllib.parse.quote(OPENALEX_EMAIL)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        return decode_openalex_abstract(data.get("abstract_inverted_index"))
    except Exception as exc:
        print(f"    Warning: OpenAlex abstract lookup failed for {doi}: {exc}")
        return ""


def secondary_index_fallback_allowed(entry):
    """Use secondary indexes only where their text is reliably abstract-like."""
    return (
        bool(entry["doi"])
        and entry["publication_type"] not in SECONDARY_INDEX_EXCLUDED_PUBLICATION_TYPES
    )


def abstract_rejection_reason(entry, abstract):
    """Explain why indexed text is not a genuine scholarly abstract."""
    publication_type = entry.get("publication_type", "").lower()
    if publication_type in INVALID_ABSTRACT_PUBLICATION_TYPES:
        return f"{publication_type} records do not carry formal abstracts"
    text = normalize_text(abstract)
    if not text:
        return "empty text"
    for reason, pattern in INVALID_ABSTRACT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return reason
    return ""


def add_valid_abstract(abstracts, sources, entry, abstract, source):
    """Add only genuine abstracts; log rejected indexing fragments."""
    if not abstract:
        return False
    reason = abstract_rejection_reason(entry, abstract)
    if reason:
        print(f"    Skipped {entry['key']} {source} text: {reason}")
        return False
    abstracts[entry["key"]] = abstract
    sources[entry["key"]] = source
    return True


def is_publication_output(paper):
    """Exclude maintenance notices that are not lab research outputs."""
    return classify_type(paper["title"], paper.get("abstract", "")) != "correction"


def semantic_scholar_abstracts_from_records(records):
    """Map Semantic Scholar batch results by DOI, independent of result order."""
    abstracts = {}
    for record in records or []:
        if not record:
            continue
        doi = (record.get("externalIds") or {}).get("DOI", "").lower()
        abstract = normalize_text(record.get("abstract", ""))
        abstract = re.sub(r"^Abstract\s*:?\s*", "", abstract, flags=re.IGNORECASE)
        if doi and abstract:
            abstracts[doi] = abstract
    return abstracts


def fetch_semantic_scholar_abstracts(entries):
    """Fetch DOI-keyed abstracts in one rate-limit-friendly batch request."""
    eligible = [entry for entry in entries if secondary_index_fallback_allowed(entry)]
    if not eligible:
        return {}
    query = urllib.parse.urlencode({
        "fields": "abstract,externalIds",
    })
    payload = json.dumps({
        "ids": [f"DOI:{entry['doi']}" for entry in eligible],
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{SEMANTIC_SCHOLAR_BATCH}?{query}",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "xy-lilab-publication-refresh/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            records = json.loads(resp.read())
        return semantic_scholar_abstracts_from_records(records)
    except Exception as exc:
        print(f"    Warning: Semantic Scholar batch lookup failed: {exc}")
        return {}


def get_author_list(article):
    """Extract (last_name, first_name, initials, is_first, is_last) for each author."""
    author_list = article.find(".//AuthorList")
    if author_list is None:
        return []
    authors = []
    items = list(author_list.findall("Author"))
    for i, author in enumerate(items):
        last = author.findtext("LastName", "")
        fore = author.findtext("ForeName", "")
        initials = author.findtext("Initials", "")
        # Collect affiliation info for this author
        affil_parts = []
        for ai in author.findall("AffiliationInfo"):
            affil_parts.append(ai.findtext("Affiliation", ""))
        authors.append({
            "last": last,
            "fore": fore,
            "initials": initials,
            "is_first": i == 0,
            "is_last": i == len(items) - 1,
            "affiliations": " ".join(affil_parts).lower(),
        })
    return authors


def normalize_name(name):
    """Normalize a name for comparison: lowercase, strip accents, etc."""
    return re.sub(r"[^a-z]", "", name.lower())


# Affiliation patterns that confirm the author belongs to our lab.
# At least one must match. Each pattern is a list of terms that must ALL appear.
LAB_AFFILIATION_PATTERNS = [
    ["hunan key laboratory", "aging biology"],      # 重点实验室
    ["dermatol", "xiangya"],                         # 湘雅皮肤科
]


def member_is_key_author(authors, member_name):
    """Check if a lab member is first or last (corresponding) author,
    AND their affiliation matches our lab (dermatology/aging)."""
    parts = member_name.strip().split()
    if len(parts) < 2:
        return False
    member_last = normalize_name(parts[-1])
    member_first = normalize_name(parts[0])

    for author in authors:
        if not (author["is_first"] or author["is_last"]):
            continue
        author_last = normalize_name(author["last"])
        author_fore = normalize_name(author["fore"])
        if author_last == member_last and (
            author_fore.startswith(member_first) or member_first.startswith(author_fore)
        ):
            # Verify affiliation matches our lab specifically
            affil = author.get("affiliations", "")
            if affil:
                for pattern in LAB_AFFILIATION_PATTERNS:
                    if all(term in affil for term in pattern):
                        return True
                # Affiliation exists but doesn't match our lab — skip
                continue
            # No affiliation data — skip (too risky for common names)
            continue
    return False


def extract_paper_data(pubmed_article):
    """Extract structured data from a PubMed XML PubmedArticle element."""
    # PMID is at the MedlineCitation level, not inside Article
    pmid = pubmed_article.findtext(".//MedlineCitation/PMID", "")
    article = pubmed_article.find(".//Article")
    title = article.findtext(".//ArticleTitle", "")
    abstract = extract_abstract_text(article)
    journal = article.findtext(".//Journal/Title", "")
    journal_abbrev = article.findtext(".//Journal/ISOAbbreviation", "")
    issn = ""
    eissn = ""
    for issn_el in article.findall(".//Journal/ISSN"):
        if issn_el.get("IssnType") == "Electronic":
            eissn = issn_el.text or ""
        else:
            issn = issn_el.text or ""
    year = article.findtext(".//Journal/JournalIssue/PubDate/Year", "")
    month = article.findtext(".//Journal/JournalIssue/PubDate/Month", "")
    volume = article.findtext(".//Journal/JournalIssue/Volume", "")
    issue = article.findtext(".//Journal/JournalIssue/Issue", "")
    pages = article.findtext(".//Pagination/MedlinePgn", "")

    # DOI
    doi = ""
    for eid in article.findall(".//ELocationID"):
        if eid.get("EIdType") == "doi":
            doi = eid.text or ""
            break
    if not doi:
        for aid in article.findall(".//ArticleId"):
            if aid.get("IdType") == "doi":
                doi = aid.text or ""
                break

    # Authors
    authors = get_author_list(article)
    author_str = " and ".join(
        f"{a['last']}, {a['initials']}." for a in authors
    )

    # First and corresponding authors
    first_authors = [f"{a['fore']} {a['last']}" for a in authors if a["is_first"]]
    corresponding_authors = [f"{a['fore']} {a['last']}" for a in authors if a["is_last"]]

    return {
        "pmid": pmid,
        "title": title.rstrip("."),
        "abstract": abstract or "",
        "journal": journal,
        "journal_abbrev": journal_abbrev,
        "issn": issn,
        "eissn": eissn,
        "year": year,
        "month": month,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "author_str": author_str,
        "first_authors": "; ".join(first_authors),
        "corresponding_authors": "; ".join(corresponding_authors),
        "authors": authors,
    }


def generate_bib_key(paper):
    """Generate a BibTeX key like 'li2026natcommun'."""
    first_last = ""
    if paper["authors"]:
        first_last = paper["authors"][0]["last"].lower()
    year = paper["year"]
    journal_word = re.sub(r"[^a-z]", "", paper["journal_abbrev"].lower())[:10]
    # Take first meaningful word from title
    title_words = re.sub(r"[^a-z\s]", "", paper["title"].lower()).split()
    skip = {"a", "an", "the", "of", "in", "for", "and", "with", "by", "on", "to", "from", "is", "are"}
    title_word = ""
    for w in title_words:
        if w not in skip and len(w) > 2:
            title_word = w[:8]
            break
    return f"{first_last}{year}{journal_word}_{title_word}"


def escape_bibtex(text):
    """Escape special characters for BibTeX."""
    return text.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")


def bib_field(entry, name):
    """Read a simple braced field from one BibTeX entry."""
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s*=\s*\{{([^}}]*)\}}", entry)
    return match.group(1).strip() if match else ""


def missing_abstract_entries(bib_content):
    """Return public 2020+ entries whose bibliography data lacks an abstract."""
    entries = []
    pattern = re.compile(r"(?m)^@\w+\{([^,]+),(.*?)(?=^@\w+\{|\Z)", re.DOTALL)
    for match in pattern.finditer(bib_content):
        key, body = match.group(1), match.group(2)
        year = bib_field(body, "year")
        if not year.isdigit() or int(year) < WEB_MIN_YEAR:
            continue
        if bib_field(body, "web_show").lower() == "false":
            continue
        if re.search(r"(?m)^\s*abstract\s*=\s*\{", body):
            continue
        entries.append({
            "key": key,
            "pmid": bib_field(body, "pmid"),
            "doi": bib_field(body, "doi"),
            "publication_type": bib_field(body, "publication_type").lower(),
        })
    return entries


def insert_abstracts(bib_content, abstracts):
    """Insert verified abstracts after PMID (or DOI) without rewriting entries."""
    for key, abstract in abstracts.items():
        entry_pattern = re.compile(
            rf"(?m)^@\w+\{{{re.escape(key)},.*?(?=^@\w+\{{|\Z)",
            re.DOTALL,
        )
        match = entry_pattern.search(bib_content)
        if not match or re.search(r"(?m)^\s*abstract\s*=", match.group(0)):
            continue
        entry = match.group(0)
        lines = entry.splitlines(keepends=True)
        insert_at = None
        for field_name in ("pmid", "doi", "year"):
            for index, line in enumerate(lines):
                if re.match(rf"\s*{field_name}\s*=", line):
                    insert_at = index + 1
                    break
            if insert_at is not None:
                break
        if insert_at is None:
            continue
        lines.insert(insert_at, f"  abstract={{{escape_bibtex(abstract)}}},\n")
        replacement = "".join(lines)
        bib_content = bib_content[:match.start()] + replacement + bib_content[match.end():]
    return bib_content


def backfill_missing_abstracts():
    """Backfill existing entries from PubMed, PMC, then OpenAlex."""
    bib_content = BIB_FILE.read_text(encoding="utf-8")
    entries = missing_abstract_entries(bib_content)
    print(f"\nExisting public papers missing abstracts: {len(entries)}")
    if not entries:
        return 0

    by_pmid = {entry["pmid"]: entry for entry in entries if entry["pmid"]}
    pubmed_records = {}
    pmcids = {}
    pmids = list(by_pmid)
    for index in range(0, len(pmids), 50):
        root = pubmed_fetch(pmids[index:index + 50])
        for record in root.findall(".//PubmedArticle"):
            pmid = record.findtext("./MedlineCitation/PMID", "")
            article = record.find("./MedlineCitation/Article")
            pubmed_records[pmid] = extract_abstract_text(article) if article is not None else ""
            for article_id in record.findall("./PubmedData/ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "pmc" and article_id.text:
                    pmcids[pmid] = article_id.text
                    break
        time.sleep(0.4)

    abstracts = {}
    sources = {}
    for entry in entries:
        abstract = pubmed_records.get(entry["pmid"], "")
        add_valid_abstract(abstracts, sources, entry, abstract, "PubMed")

    for entry in entries:
        if entry["key"] in abstracts:
            continue
        pmcid = pmcids.get(entry["pmid"], "")
        if pmcid:
            abstract = fetch_pmc_abstract(pmcid)
            add_valid_abstract(abstracts, sources, entry, abstract, "PMC")
            time.sleep(0.2)

    for entry in entries:
        if entry["key"] in abstracts or not secondary_index_fallback_allowed(entry):
            continue
        abstract = fetch_openalex_abstract(entry["doi"])
        add_valid_abstract(abstracts, sources, entry, abstract, "OpenAlex")
        time.sleep(0.12)

    unresolved_entries = [entry for entry in entries if entry["key"] not in abstracts]
    semantic_scholar_abstracts = fetch_semantic_scholar_abstracts(unresolved_entries)
    for entry in unresolved_entries:
        abstract = semantic_scholar_abstracts.get(entry["doi"].lower(), "")
        add_valid_abstract(abstracts, sources, entry, abstract, "Semantic Scholar")

    if not abstracts:
        print("No authoritative abstracts are currently available for backfill.")
        return 0

    updated_content = insert_abstracts(bib_content, abstracts)
    BIB_FILE.write_text(updated_content, encoding="utf-8")
    for key in abstracts:
        print(f"  + {key}: abstract from {sources[key]}")
    unresolved = len(entries) - len(abstracts)
    print(f"Backfilled {len(abstracts)} abstract(s); {unresolved} remain unavailable upstream.")
    return len(abstracts)


def format_bibtex_entry(paper):
    """Format a paper as a BibTeX entry."""
    key = generate_bib_key(paper)
    abstract = paper.get("abstract", "")
    category, subcategory = classify_paper(paper["title"], abstract)
    paper_type = classify_type(paper["title"], abstract)
    lines = [f"@article{{{key},"]
    lines.append(f"  title={{{escape_bibtex(paper['title'])}}},")
    lines.append(f"  author={{{escape_bibtex(paper['author_str'])}}},")
    lines.append(f"  first_author={{{paper['first_authors']}}},")
    lines.append(f"  corresponding_author={{{paper['corresponding_authors']}}},")
    lines.append(f"  journal={{{paper['journal']}}},")
    lines.append(f"  year={{{paper['year']}}},")
    if paper["month"]:
        lines.append(f"  month={{{paper['month']}}},")
    if paper["doi"]:
        lines.append(f"  doi={{{paper['doi']}}},")
    if paper["volume"]:
        lines.append(f"  volume={{{paper['volume']}}},")
    if paper["issue"]:
        lines.append(f"  number={{{paper['issue']}}},")
    if paper["pages"]:
        lines.append(f"  pages={{{paper['pages']}}},")
    lines.append(f"  pmid={{{paper['pmid']}}},")
    if not abstract_rejection_reason({"publication_type": paper_type}, abstract):
        lines.append(f"  abstract={{{escape_bibtex(abstract)}}},")
    is_clinical, is_basic = classify_clinical_basic(
        paper["title"], paper.get("abstract", ""), paper_type
    )
    metrics = lookup_journal_metrics(
        paper.get("issn", ""), paper.get("eissn", ""),
        paper.get("journal", ""), paper.get("journal_abbrev", ""),
    )
    paper["_metrics"] = metrics  # stash for summary output
    paper["_classification"] = {
        "category": category, "subcategory": subcategory,
        "publication_type": paper_type,
        "clinical": is_clinical, "basic": is_basic,
    }
    if "impact_factor" in metrics:
        lines.append(f"  impact_factor={{{metrics['impact_factor']}}},")
    if "jcr_quartile" in metrics:
        lines.append(f"  jcr_quartile={{{metrics['jcr_quartile']}}},")
    # zero-padded IF for jekyll-scholar string-based sort (string sort == numeric sort)
    try:
        sort_if_val = f"{float(metrics.get('impact_factor', 0) or 0):06.2f}"
    except (TypeError, ValueError):
        sort_if_val = "000.00"
    lines.append(f"  sort_if={{{sort_if_val}}},")
    lines.append(f"  category={{{category}}},")
    lines.append(f"  subcategory={{{subcategory}}},")
    lines.append(f"  publication_type={{{paper_type}}},")
    if is_clinical:
        lines.append(f"  clinical={{true}},")
    if is_basic:
        lines.append(f"  basic={{true}},")
    lines.append(f"  language={{en}},")
    lines.append(f"  bibtex_show={{true}},")
    lines.append(f"  author_verified={{pubmed_auto}},")
    lines.append("}")
    return "\n".join(lines)


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backfill-only",
        action="store_true",
        help="Backfill missing abstracts without searching for new publications.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Li Lab Publication Fetcher")
    print("=" * 60)

    backfill_missing_abstracts()
    if args.backfill_only:
        return 0

    # Load data
    members = load_member_names()
    existing_pmids, existing_dois = load_existing_ids()
    print(f"\nLab members: {len(members)}")
    print(f"Existing papers in .bib: {len(existing_pmids)} PMIDs, {len(existing_dois)} DOIs")

    # Build PubMed query
    affil_query = " OR ".join(f'"{a}"[Affiliation]' for a in AFFILIATIONS)
    date_filter = f"{MIN_YEAR}:3000[Date - Publication]"
    query = f"({affil_query}) AND ({date_filter})"
    print(f"\nPubMed query: {query}")

    # Search PubMed
    print("\nSearching PubMed...")
    all_pmids = pubmed_search(query)
    print(f"Found {len(all_pmids)} total results")

    # Filter out already-known papers
    new_pmids = [p for p in all_pmids if p not in existing_pmids]
    print(f"New (not in .bib): {len(new_pmids)}")

    if not new_pmids:
        print("\nNo new papers to process.")
        return 0

    # Fetch details in batches of 50
    new_papers = []
    for i in range(0, len(new_pmids), 50):
        batch = new_pmids[i:i+50]
        print(f"\nFetching details for batch {i//50 + 1} ({len(batch)} papers)...")
        root = pubmed_fetch(batch)
        time.sleep(0.5)  # Be nice to NCBI

        for pubmed_article in root.findall(".//PubmedArticle"):
            paper = extract_paper_data(pubmed_article)

            if not is_publication_output(paper):
                print(f"  - Skipping bibliographic maintenance notice: {paper['title'][:80]}")
                continue

            # Skip if DOI already exists in .bib (catches papers added without PMID)
            if paper["doi"] and paper["doi"].lower() in existing_dois:
                continue

            # Filter: lab member must be first or corresponding author
            matched_member = None
            for member in members:
                if member_is_key_author(paper["authors"], member):
                    matched_member = member
                    break

            if matched_member:
                paper["matched_member"] = matched_member
                new_papers.append(paper)

    print(f"\nPapers with lab member as first/corresponding author: {len(new_papers)}")

    if not new_papers:
        print("No qualifying new papers found.")
        return 0

    # Append to .bib file
    bib_content = BIB_FILE.read_text(encoding="utf-8")
    additions = []
    for paper in new_papers:
        entry = format_bibtex_entry(paper)
        additions.append(entry)
        print(f"\n  + [{paper['year']}] {paper['title'][:80]}...")
        print(f"    {paper['journal']}")
        print(f"    Key author: {paper['matched_member']}")
        print(f"    PMID: {paper['pmid']}, DOI: {paper['doi']}")

    # Append new entries
    separator = "\n\n% ---- Auto-fetched papers ----\n\n"
    if "Auto-fetched papers" not in bib_content:
        bib_content += separator
    bib_content += "\n\n".join(additions) + "\n"
    BIB_FILE.write_text(bib_content, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"Added {len(new_papers)} new paper(s) to {BIB_FILE.name}")
    print(f"{'=' * 60}")

    # Write summary for GitHub Actions
    summary_file = REPO_ROOT / "scripts" / "new_papers_summary.md"
    lines = [f"# New Publications Found ({len(new_papers)})\n"]
    for paper in new_papers:
        m = paper.get("_metrics", {})
        c = paper.get("_classification", {})
        metrics_bits = []
        if "impact_factor" in m: metrics_bits.append(f"IF {m['impact_factor']}")
        if "jcr_quartile" in m: metrics_bits.append(f"JCR {m['jcr_quartile']}")
        class_bits = []
        if c.get("category"): class_bits.append(c["category"])
        if c.get("subcategory") and c["subcategory"] != "other":
            class_bits.append(c["subcategory"])
        if c.get("publication_type"): class_bits.append(c["publication_type"])
        if c.get("clinical"): class_bits.append("clinical")
        if c.get("basic"): class_bits.append("basic")

        lines.append(f"## {paper['title']}\n")
        lines.append(f"- **Journal**: {paper['journal']}" + (
            f" — {' · '.join(metrics_bits)}" if metrics_bits else " — *metrics not found*"))
        lines.append(f"- **Year**: {paper['year']}")
        lines.append(f"- **Key author**: {paper['matched_member']}")
        lines.append(f"- **Classification**: {' · '.join(class_bits) if class_bits else '-'}")
        lines.append(f"- **DOI**: {paper['doi']}")
        lines.append(f"- **PMID**: {paper['pmid']}")
        lines.append("")
    summary_file.write_text("\n".join(lines), encoding="utf-8")

    return 1  # Signal: new papers found


if __name__ == "__main__":
    sys.exit(main())
