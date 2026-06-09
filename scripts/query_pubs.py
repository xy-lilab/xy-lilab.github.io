#!/usr/bin/env python3
"""Query the lab publication library (papers.bib) by author role or research field.

Usage:
  python scripts/query_pubs.py author "Ji Li"        # 某人 第一/通讯/参与 各几篇
  python scripts/query_pubs.py field rosacea          # 某领域(category/subcategory/题名关键词) 几篇
  python scripts/query_pubs.py summary                # 全员第一/通讯统计 + 各领域统计
  python scripts/query_pubs.py author "Ji Li" --list  # 附逐篇清单

Roles are read from the first_author / corresponding_author tags (支持共一/共通讯,分号分隔).
"""
import re, sys
from pathlib import Path
from collections import Counter, defaultdict

BIB = Path(__file__).parent.parent / "_bibliography" / "papers.bib"

def parse():
    txt = BIB.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r'@article\{([^,]+),(.*?)\n\}', txt, re.S):
        body = m.group(2)
        def f(name):
            mm = re.search(r'\b' + name + r'\s*=\s*\{(.*?)\}', body, re.S)
            return mm.group(1).strip() if mm else ""
        out.append({
            "key": m.group(1).strip(), "title": f("title"), "year": f("year"),
            "journal": f("journal"),
            "first": [x.strip() for x in re.split(r'[;]', f("first_author")) if x.strip()],
            "corr": [x.strip() for x in re.split(r'[;]', f("corresponding_author")) if x.strip()],
            "category": f("category"), "subcategory": f("subcategory"),
            "ptype": f("publication_type"), "if": f("impact_factor"),
        })
    return out

def norm(n): return re.sub(r'[^a-z]', '', n.lower())

def match(name, lst):
    nn = norm(name)
    for x in lst:
        nx = norm(x)
        if nn == nx or nn in nx or nx in nn:
            return True
    return False

def author_query(name, show_list=False):
    pubs = parse()
    first = [p for p in pubs if match(name, p["first"])]
    corr = [p for p in pubs if match(name, p["corr"])]
    lead = [p for p in pubs if match(name, p["first"]) or match(name, p["corr"])]
    print(f'【{name}】在论文库({len(pubs)}篇)中:')
    print(f'  第一/共一作者:  {len(first)} 篇')
    print(f'  通讯/共通讯作者: {len(corr)} 篇')
    print(f'  第一或通讯(牵头) 去重: {len(lead)} 篇')
    if show_list:
        for p in sorted(lead, key=lambda x: x["year"], reverse=True):
            role = ("一作" if match(name, p["first"]) else "") + ("/通讯" if match(name, p["corr"]) else "")
            print(f'    {p["year"]} [{role.strip("/"):7}] {p["journal"][:24]:24} {p["title"][:55]}')

def field_query(kw):
    pubs = parse()
    k = kw.lower()
    hit = [p for p in pubs if k in p["category"].lower() or k in p["subcategory"].lower() or k in p["title"].lower()]
    print(f'领域/关键词「{kw}」: {len(hit)} 篇')
    for p in sorted(hit, key=lambda x: x["year"], reverse=True):
        print(f'  {p["year"]} | {p["category"]}/{p["subcategory"]} | {p["title"][:60]}')

def summary():
    pubs = parse()
    print(f'论文库共 {len(pubs)} 篇\n')
    fc, cc = Counter(), Counter()
    for p in pubs:
        for a in p["first"]: fc[a] += 1
        for a in p["corr"]: cc[a] += 1
    print('=== 各成员 第一/共一 篇数(Top) ===')
    for a, n in fc.most_common(20): print(f'  {n:3}  {a}')
    print('\n=== 各成员 通讯/共通讯 篇数(Top) ===')
    for a, n in cc.most_common(20): print(f'  {n:3}  {a}')
    print('\n=== 各领域(category/subcategory)篇数 ===')
    cat = Counter(f'{p["category"]}/{p["subcategory"]}' for p in pubs)
    for c, n in cat.most_common(): print(f'  {n:3}  {c}')

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "summary": summary()
    elif a[0] == "author" and len(a) > 1: author_query(a[1], "--list" in a)
    elif a[0] == "field" and len(a) > 1: field_query(a[1])
    else: print(__doc__)
