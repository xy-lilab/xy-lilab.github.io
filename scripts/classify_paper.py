#!/usr/bin/env python3
"""
Keyword-based classifier for Li Lab publications.

Assigns (category, subcategory) by scanning title + abstract for disease
keywords. Designed to match the category taxonomy already used in papers.bib.

Known (category, subcategory) pairs from existing data:
  pilosebaceous/rosacea, pilosebaceous/hair_disorders, pilosebaceous/acne
  aging/skin_aging, aging/systemic_aging, aging/wound_healing
  other_dermatology/{psoriasis, atopic_dermatitis, vitiligo, skin_cancer, other}
"""

import re

# (category, subcategory) -> list of regex patterns (case-insensitive)
# Specificity matters: first-match-wins semantics handled by ordering in CLASSIFIERS.
KEYWORDS = {
    ("pilosebaceous", "rosacea"): [
        r"\brosacea\b", r"\bflush(ing|ed)?\b", r"\btelangiectas",
        r"persistent (facial|erythema)", r"\berythemato?telang",
        r"papulopustular", r"demodex",
    ],
    ("pilosebaceous", "hair_disorders"): [
        r"\balopecia\b", r"\bhair loss\b", r"\bhair (growth|follicle|shaft|graying|greying|pigmentation|regeneration|regrowth)\b",
        r"androgenetic", r"\bhair cycle\b", r"dermal papilla", r"trichology",
        r"\bscalp\b", r"piebaldism", r"melanocyte (stem|progenitor)",
        r"\bbald(ing|ness)\b",
    ],
    ("pilosebaceous", "acne"): [
        r"\bacne\b(?! rosacea)", r"sebaceous gland", r"\bsebum\b",
        r"hidradenitis suppurativa", r"\bHS\b",
        r"seborrh[eo]{1,2}ic dermatitis",
    ],
    ("aging", "skin_aging"): [
        r"\bskin aging\b", r"\bphotoaging\b", r"photo[- ]?aged",
        r"fibroblast senescence", r"dermal aging", r"\bwrinkle",
        r"UV[- ]induced aging", r"cutaneous aging",
    ],
    ("aging", "systemic_aging"): [
        r"aging biomarker", r"biological age", r"\blongevity\b",
        r"\bcentenarian", r"healthy aging", r"organ aging",
        r"\bfrailty\b", r"senolytic", r"cellular senescence(?! in skin| in fibroblast)",
        r"aging clock", r"lifespan",
    ],
    ("aging", "wound_healing"): [
        r"wound healing", r"\bulcer(ation)?\b", r"\bscar(ring)?\b",
        r"tissue regeneration", r"skin repair",
    ],
    ("other_dermatology", "psoriasis"): [
        r"\bpsoriasis\b", r"\bpsoriatic\b",
    ],
    ("other_dermatology", "atopic_dermatitis"): [
        r"atopic dermatitis", r"\beczema\b", r"\bAD\b(?= pathogen| patient)",
    ],
    ("other_dermatology", "vitiligo"): [
        r"\bvitiligo\b", r"\bdepigmentation\b", r"leukoderma",
    ],
    ("other_dermatology", "skin_cancer"): [
        r"\bmelanoma\b", r"squamous cell carcinoma", r"\bSCC\b",
        r"basal cell carcinoma", r"\bBCC\b", r"skin cancer",
        r"cutaneous (lymphoma|tumor|neoplasm)",
    ],
}

# Ordered list for priority (more specific first). Most papers get 1 clear winner
# but in ambiguous cases, earlier entries win ties.
PRIORITY = [
    ("pilosebaceous", "rosacea"),
    ("pilosebaceous", "hair_disorders"),
    ("pilosebaceous", "acne"),
    ("aging", "skin_aging"),
    ("aging", "systemic_aging"),
    ("aging", "wound_healing"),
    ("other_dermatology", "psoriasis"),
    ("other_dermatology", "atopic_dermatitis"),
    ("other_dermatology", "vitiligo"),
    ("other_dermatology", "skin_cancer"),
]

FALLBACK = ("other_dermatology", "other")


def classify(title, abstract=""):
    """Return (category, subcategory) for a paper."""
    text = f"{title}\n{abstract}".lower()
    scores = {}
    for pair in PRIORITY:
        patterns = KEYWORDS[pair]
        hits = sum(len(re.findall(pat, text, re.IGNORECASE)) for pat in patterns)
        if hits > 0:
            scores[pair] = hits
    if not scores:
        return FALLBACK
    # Highest score wins; ties broken by PRIORITY order
    max_score = max(scores.values())
    for pair in PRIORITY:
        if scores.get(pair) == max_score:
            return pair
    return FALLBACK


# ── Paper type classification ──

# Ordered by specificity — first match wins.
TYPE_PATTERNS = [
    ("guideline", [r"\bguidelin[es]", r"consensus (statement|document|recommendation)"]),
    ("correction", [r"^correction(?: to|:)", r"\berratum\b", r"\bcorrigendum\b", r"\bauthor correction"]),
    ("editorial", [r"^editorial(?:[:\s]|$)", r"commentary on\b"]),
    ("letter", [r"^response to", r"^reply to", r"^letter to the editor", r"^correspondence"]),
    ("case_report", [r"\bcase report\b", r"\bcase series\b"]),
    ("meta_analysis", [r"meta[- ]analysis", r"systematic review"]),
    ("clinical_trial", [
        r"randomi[sz]ed(?:[,\s]*(?:double|single|triple)-?blind)?",
        r"\bplacebo[- ]controlled", r"clinical trial", r"\bRCT\b",
        r"phase [I1234]+ (trial|study)",
    ]),
    ("observational", [r"\bcohort study\b", r"observational study", r"cross[- ]sectional study"]),
]


def classify_type(title, abstract=""):
    """Return one of: clinical_trial, observational, case_report, meta_analysis,
    guideline, letter, correction, editorial, original (default)."""
    text = f"{title}\n{abstract}".lower()
    for type_name, patterns in TYPE_PATTERNS:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return type_name
    return "original"


# ── Clinical vs basic research classification ──

CLINICAL_KEYWORDS = [
    r"\bpatient[s]?\b", r"\bclinical\b", r"\bcohort\b", r"retrospective",
    r"prospective", r"real[- ]world", r"randomi[sz]ed", r"placebo",
    r"clinical trial", r"\bRCT\b", r"double[- ]blind",
    r"\bquestionnaire\b", r"\bsurvey\b", r"\bUK biobank\b",
    r"\bepidemiolog", r"case[- ]control",
]

BASIC_KEYWORDS = [
    r"single[- ]cell", r"\btranscriptom", r"\bproteom", r"\bmetabolom",
    r"\bgenom(e|ics)\b", r"\borganoid", r"\bmouse model", r"\bknockout\b",
    r"\bknockdown\b", r"CRISPR", r"\bin vitro\b", r"\bin vivo\b",
    r"cryo[- ]?EM", r"\bsignaling pathway", r"\bmechanism",
    r"gene expression", r"flow cytometry", r"immunohistochem",
    r"Western blot", r"\bRNA[- ]seq\b", r"\bChIP[- ]seq\b",
    r"differentially expressed", r"molecular mechanism",
]


NON_RESEARCH_TYPES = {"letter", "correction", "editorial", "guideline"}


def classify_clinical_basic(title, abstract="", paper_type="original"):
    """Return (is_clinical, is_basic) tuple — a paper can be both.
    Letter/correction/editorial/guideline return (False, False)."""
    if paper_type in NON_RESEARCH_TYPES:
        return False, False
    text = f"{title}\n{abstract}".lower()
    clin = any(re.search(p, text, re.IGNORECASE) for p in CLINICAL_KEYWORDS)
    basic = any(re.search(p, text, re.IGNORECASE) for p in BASIC_KEYWORDS)
    return clin, basic


# ── Test on the 2 unclassified papers ──
if __name__ == "__main__":
    tests = [
        {
            "key": "yang2026jdermatolo_physical",
            "title": "Physical activity as a potential nonpharmacologic strategy to prevent seborrheic dermatitis: a cohort study in the UK biobank",
            "abstract": "Seborrheic dermatitis (SD) is a chronic inflammatory skin disease with limited long-term treatment options. The association between physical activity and incident SD, as well as the potential mediating role of depressive symptoms, remains unclear.",
        },
        {
            "key": "huang2026jamacadder_response",
            "title": 'Response to comments on "Proteomic profiling reveals distinct inflammatory and neurogenic endotypes in rosacea"',
            "abstract": "",
        },
    ]

    for t in tests:
        cat = classify(t["title"], t["abstract"])
        typ = classify_type(t["title"], t["abstract"])
        clin, basic = classify_clinical_basic(t["title"], t["abstract"], typ)
        print(f"[{t['key']}]")
        print(f"  category/subcategory: {cat}")
        print(f"  type: {typ}")
        print(f"  clinical: {clin}   basic: {basic}")
        print()
