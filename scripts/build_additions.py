#!/usr/bin/env python3
"""One-off: build tagged bib entries for the curated add-list (Li Ji catalog gaps).

- Metadata from PubMed via the existing pipeline (extract_paper_data + IF + classify).
- first_author / corresponding_author OVERRIDDEN from the colleague-doc # / * markers
  (true co-first / co-corresponding), mapped to PubMed full names by surname+initial.
- Inclusion: lead (Li Ji first/corr) force-included; 挂名 included iff a members.yml
  member is among the corresponding (*) authors.
- Pre-2020 tagged web_show={false} (kept in bib, hidden from site).
Outputs _bibliography/_additions_pending.bib + a decision report (stdout).
NO modification of papers.bib, NO push.
"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import fetch_publications as fp

CAND = json.load(open('/tmp/liji_candidates_pmid.json'))          # 80, with role/pmid/doi/title/year
VER  = {(r.get('doi') or '').lower().rstrip('.'): r for r in json.load(open('/tmp/liji_all_verified.json'))}
CIT  = {}
for line in open('/tmp/liji_entries_indexed.jsonl'):
    o = json.loads(line); CIT[o['idx']] = o['citation']
MEMBERS = fp.load_member_names()

# New 2025-26 papers: CURATED corresponding authors (read from catalog verification, exact).
# DOI -> lab-member corresponding-author names (include). Absent/empty -> external corr -> skip.
NEW_INCLUDE = {
    '10.1111/ijd.70516':            'Yan Tang; Wei Shi',
    '10.2340/actadv.v106.adv-2025-0060': 'Yan Tang',
    '10.1080/07853890.2026.2663263':'Dan Jian',
    '10.1177/12034754261431757':    'Wei Shi; Fangfen Liu',
    '10.1093/qjmed/hcaf221':        'Wei Shi',
    '10.1016/j.bbrc.2025.153208':   'Dan Jian',
    '10.1016/j.jaad.2025.12.020':   'Fangfen Liu; Wei Shi',
    '10.1111/1346-8138.17527':      'Yan Tang',
    '10.1016/j.jdermsci.2025.05.005':'Dan Jian',
    '10.1016/j.xcrm.2026.102767':   'Ji Li',                  # LEAD co-corr
    '10.2147/ijn.s499289':          'Ben Wang; Ji Li',        # LEAD co-corr
    '10.1080/14728214.2026.2655714':'Ji Li; Ben Wang',        # LEAD co-corr (review)
}
def new_corr_members(doi):
    s = NEW_INCLUDE.get(doi.lower().rstrip('.'))
    return [x.strip() for x in s.split(';')] if s else []

def norm(d): return (d or '').strip().lower().rstrip('.').replace('https://doi.org/', '')

def doc_citation(doi):
    v = VER.get(norm(doi))
    return CIT.get(v['idx']) if v and v.get('idx') is not None else None

def marked_authors(cit):
    """Return (cofirst_tokens, cocorr_tokens) as 'Surname Initial' strings."""
    if not cit: return [], []
    # author block = up to the title (first '. ' after a marker or long run). Use whole string; markers only on names.
    first, corr = [], []
    for m in re.finditer(r'([A-Z][a-zA-Z]+(?:[,]?\s+[A-Za-z][a-zA-Z\.]*)?)\s*([#*]{1,2})', cit):
        name, mk = m.group(1).strip().rstrip(','), m.group(2)
        if '#' in mk: first.append(name)
        if '*' in mk: corr.append(name)
    return first, corr

import urllib.request, urllib.parse
def robust_fetch(pmid, tries=4):
    for k in range(tries):
        try:
            root = fp.pubmed_fetch([pmid])
            art = root.find('.//PubmedArticle')
            if art is not None:
                return fp.extract_paper_data(art)
        except Exception:
            pass
        time.sleep(0.6 * (k + 1))
    return None

def doi_to_pmid(doi):
    try:
        u = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=' + urllib.parse.quote(doi + '[doi]')
        d = json.load(urllib.request.urlopen(u, timeout=20))
        ids = d.get('esearchresult', {}).get('idlist', [])
        return ids[0] if ids else ''
    except Exception:
        return ''

def si(tok):
    """surname, initial from 'Shi W' / 'Jian Dan' / 'Wei Shi'(member full)."""
    p = [x for x in re.split(r'[\s,\.]+', tok.strip()) if x]
    if len(p) >= 2:
        if len(p[-1]) <= 2 and p[-1][0].isupper():   # 'Shi W'
            return p[0].lower(), p[-1][0].lower()
        return p[0].lower(), p[-1][0].lower()         # 'Jian Dan' -> surname first
    return (p[0].lower(), '') if p else ('', '')

def member_si():
    out = set()
    for n in MEMBERS:
        p = n.split()
        if len(p) >= 2: out.add((p[-1].lower(), p[0][0].lower()))
    return out
MEM_SI = member_si()

def match_fullname(tok, authors):
    """Map a 'Surname Initial' doc token to a PubMed full name 'Fore Last'."""
    s, i = si(tok)
    for a in authors:
        if a['last'].lower() == s and (not i or (a['fore'] or a['initials'] or ' ')[0].lower() == i):
            fore = a['fore'] or a['initials']
            return f"{fore} {a['last']}".strip()
    return tok  # fallback: keep token

def minimal_entry(c, cofirst_t, cocorr_t, li_role):
    """Build a minimal hand entry from our catalog data (no PubMed)."""
    doi = c['doi']; yr = c['year']
    key = re.sub(r'[^a-z]', '', (cocorr_t[-1].split()[0] if cocorr_t else 'li').lower())[:6] + str(yr) + re.sub(r'[^a-z]', '', c['title'].lower())[:6]
    L = [f'@article{{{key},',
         f"  title={{{c['title']}}},",
         f"  first_author={{{'; '.join(cofirst_t)}}}," if cofirst_t else "  first_author={},",
         f"  corresponding_author={{{'; '.join(cocorr_t)}}}," if cocorr_t else "  corresponding_author={},",
         f"  journal={{{c.get('journal','')}}},",
         f"  year={{{yr}}},",
         f"  doi={{{doi}}},",
         f"  li_role={{{li_role}}},",
         "  publication_type={original},",
         "  language={en},",
         "  bibtex_show={true},",
         "  author_verified={catalog_manual},",
         "  needs_enrichment={true},"]
    if str(yr).isdigit() and int(yr) < 2020:
        L.append("  web_show={false},")
    L.append("}")
    return '\n'.join(L)

pending, report = [], []
for c in CAND:
    role = c['role']; doi = c['doi']
    cit = doc_citation(doi)
    cofirst_t, cocorr_t = marked_authors(cit)
    is_lead = role in ('一作/共一', '通讯/共通讯')
    li_role = (VER.get(norm(doi)) or {}).get('liji_actual_role', '')
    if role == '未定':
        report.append((False, 'skip(团体/共识)', c['year'], role, c['title'][:46], doi, '')); continue

    pmid = c.get('pmid') or doi_to_pmid(doi)
    paper = robust_fetch(pmid) if pmid else None
    if pmid: time.sleep(0.34)

    # corresponding-author member check: doc-* markers OR PubMed last author OR new-paper verification note
    corr_member = any(si(t) in MEM_SI for t in cocorr_t)
    last_full = (paper or {}).get('corresponding_authors', '')   # last author (pipeline)
    if last_full and si(last_full.split(';')[-1].strip()) in MEM_SI:
        corr_member = True
    note_corr = new_corr_members(doi)
    if note_corr:
        corr_member = True
        if not cocorr_t:                      # use note members as corr names for tagging
            cocorr_t = note_corr
    include = is_lead or (role == '挂名(中间)' and corr_member)
    dec = 'LEAD' if is_lead else ('挂名→incl(corr=本室)' if include else '挂名→skip(corr=外部)')

    if not include:
        report.append((False, dec, c['year'], role, c['title'][:46], doi, ';'.join(cocorr_t)[:28])); continue

    if paper:
        entry = fp.format_bibtex_entry(paper)
        if cofirst_t:
            fa = '; '.join(dict.fromkeys(match_fullname(t, paper['authors']) for t in cofirst_t))
            entry = re.sub(r'  first_author=\{[^}]*\},', '  first_author={%s},' % fa, entry)
        if cocorr_t:
            ca = '; '.join(dict.fromkeys(match_fullname(t, paper['authors']) for t in cocorr_t))
            entry = re.sub(r'  corresponding_author=\{[^}]*\},', '  corresponding_author={%s},' % ca, entry)
        entry = entry.replace('  author_verified={pubmed_auto},',
                              f'  li_role={{{li_role}}},\n  author_verified={{catalog_verified}},')
        yr = int(paper['year']) if paper['year'].isdigit() else 9999
        if yr < 2020:
            entry = entry.replace('  bibtex_show={true},', '  bibtex_show={true},\n  web_show={false},')
        src = 'pubmed'
    else:
        entry = minimal_entry(c, cofirst_t, cocorr_t, li_role); src = 'minimal'
    pending.append(entry)
    report.append((True, dec + ('' if src == 'pubmed' else ' [minimal·待补全]'), c['year'], role, c['title'][:46], doi, ';'.join(cocorr_t)[:28]))

Path('/Users/wuzzz/xy-lilab.github.io/_bibliography/_additions_pending.bib').write_text('\n\n'.join(pending), encoding='utf-8')
inc = sum(1 for r in report if r[0])
print(f'GENERATED {len(pending)} entries (included {inc}; skipped {len(report)-inc}) -> _additions_pending.bib')
print('\n=== DECISIONS ===')
for include, dec, yr, role, title, doi, corr in sorted(report, key=lambda x: (not x[0], str(x[2]))):
    print(f'  [{"ADD " if include else "skip"}] {yr} {dec:26} | corr*={corr:28} | {title}')
