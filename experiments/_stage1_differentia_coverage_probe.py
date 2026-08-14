"""STAGE-1 COVERAGE PRE-FLIGHT for the differentia-feature-supply cell.

Read-only. Enumerates every definitional fact store found on disk, counts distinct defined
terms, measures SimLex-999 coverage (words AND both-covered pairs), and samples 30 facts to
check whether a differentia can be cleanly separated from the genus.

Nothing under hdlab/ is modified. ASCII-only.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import csv
import json
import random
import re

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.thematic_role_labeler import lemma_word            # noqa: E402
from hdlab.closed_class_lexicon import is_closed_class        # noqa: E402

SIMLEX_PATH = os.path.join(REPO_ROOT, "data", "encoder_eval_benchmarks", "simlex999.txt")

# Every store enumerated by a CONTENT grep for definiendum_surface over data/**/*.jsonl
# (not a name search), plus the provenance store JSON.
STORES = [
    ("v3_definitional", "data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl"),
    ("v4_parsefix", "data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl"),
    ("v5_termboundary", "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl"),
    ("predicate_v6", "data/exp_definitional_predicate_v6/predicate_facts_v6.jsonl"),
    ("isa_v6", "data/exp_definitional_predicate_v6/isa_facts_unchanged_v6.jsonl"),
    ("predicate_v61", "data/exp_definitional_predicate_v61/predicate_facts_v61.jsonl"),
    ("predicate_v62", "data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl"),
    ("provenance_v62_ledger", "data/foundation_provenance_v1/definitional_predicate_v62_ledger.jsonl"),
    ("called_boundary_v7_smoke", "data/exp_called_boundary_v7_smoke/called_facts_v7.jsonl"),
    ("director_kb_entities", "data/substrate_director_kb_v1/entities.jsonl"),
]
STORE_JSON = [
    ("provenance_store_facts", "data/foundation_provenance_v1/store/store_facts.json"),
]

_WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def norm_term(s: str) -> str:
    return (s or "").strip().lower()


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main():
    report = {}

    # ---------- (a) distinct defined terms per store ----------
    per_store = {}
    all_terms = set()
    all_terms_with_definiens = set()
    all_facts = []
    for name, rel in STORES:
        p = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(p):
            per_store[name] = {"path": rel, "exists": False}
            continue
        rows = load_jsonl(p)
        terms = set()
        terms_with_definiens = set()
        defn_rows = 0
        for r in rows:
            # SCHEMA-TOLERANT: a definitional record is one carrying a definiendum surface OR
            # the (subject, GROUNDED_MEANING, object) genus schema of isa_facts_unchanged_v6.
            has_surface = "definiendum_surface" in r
            has_genus_schema = (r.get("relation") == "GROUNDED_MEANING"
                                and "object" in r and "pattern" in r)
            if not (has_surface or has_genus_schema):
                continue
            defn_rows += 1
            t = norm_term(r.get("subject") or r.get("definiendum_surface"))
            if t:
                terms.add(t)
                if r.get("definiens_surface"):
                    terms_with_definiens.add(t)
            all_facts.append((name, r))
        per_store[name] = {"path": rel, "exists": True, "n_rows": len(rows),
                           "n_definitional_rows": defn_rows, "n_distinct_terms": len(terms),
                           "n_terms_with_definiens_surface": len(terms_with_definiens)}
        all_terms |= terms
        all_terms_with_definiens |= terms_with_definiens

    for name, rel in STORE_JSON:
        p = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(p):
            per_store[name] = {"path": rel, "exists": False}
            continue
        with open(p, encoding="utf-8") as f:
            rows = json.load(f)
        terms = set()
        by_pipeline = {}
        for r in rows:
            pl = r.get("pipeline", "?")
            by_pipeline[pl] = by_pipeline.get(pl, 0) + 1
            if pl == "DEFINITIONAL_EXTRACTOR":
                t = norm_term(r.get("subject"))
                if t:
                    terms.add(t)
        per_store[name] = {"path": rel, "exists": True, "n_rows": len(rows),
                           "n_definitional_rows": by_pipeline.get("DEFINITIONAL_EXTRACTOR", 0),
                           "n_distinct_terms": len(terms),
                           "pipelines": dict(sorted(by_pipeline.items(), key=lambda kv: -kv[1])[:10])}
        all_terms |= terms

    report["per_store"] = per_store
    report["n_distinct_defined_terms_union"] = len(all_terms)
    report["n_distinct_terms_with_definiens_surface"] = len(all_terms_with_definiens)

    # single-word terms only -- SimLex is single words, multiword terms can never match
    single = sorted(t for t in all_terms if " " not in t and "-" not in t)
    report["n_distinct_single_word_terms"] = len(single)

    # ---------- (b) SimLex-999 coverage ----------
    pairs = []
    with open(SIMLEX_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            pairs.append((row["word1"], row["word2"], float(row["SimLex999"])))
    vocab = sorted({w for p in pairs for w in p[:2]})
    report["simlex_n_pairs"] = len(pairs)
    report["simlex_n_distinct_words"] = len(vocab)

    # exact surface match, and lemma-normalized match (the generous reading)
    term_set = set(all_terms)
    term_lemmas = set()
    for t in single:
        term_lemmas.add(t)
        try:
            term_lemmas.add(lemma_word(t))
        except Exception:
            pass

    cov_exact = sorted(w for w in vocab if w.lower() in term_set)
    cov_lemma = sorted(w for w in vocab
                       if w.lower() in term_lemmas or lemma_word(w.lower()) in term_lemmas)
    report["simlex_words_covered_exact"] = len(cov_exact)
    report["simlex_words_covered_lemma"] = len(cov_lemma)
    report["simlex_words_covered_lemma_frac"] = round(len(cov_lemma) / len(vocab), 4)
    report["simlex_covered_word_sample"] = cov_lemma[:60]

    ce = set(cov_exact)
    cl = set(cov_lemma)
    p_exact = [p for p in pairs if p[0] in ce and p[1] in ce]
    p_lemma = [p for p in pairs if p[0] in cl and p[1] in cl]
    report["simlex_pairs_both_covered_exact"] = len(p_exact)
    report["simlex_pairs_both_covered_lemma"] = len(p_lemma)
    report["simlex_pairs_both_covered_lemma_frac"] = round(len(p_lemma) / len(pairs), 4)
    report["simlex_covered_pair_sample"] = [(a, b, g) for a, b, g in p_lemma[:40]]

    # ARM-A-RELEVANT coverage: a DIFFERENTIA needs a definiens surface to extract from.
    # Genus-only records (isa_facts / provenance) can serve Arm B but NOT Arm A.
    cd = {w for w in vocab if w.lower() in all_terms_with_definiens}
    p_diff = [p for p in pairs if p[0] in cd and p[1] in cd]
    report["simlex_words_covered_with_definiens"] = len(cd)
    report["simlex_pairs_both_covered_with_definiens"] = len(p_diff)
    report["simlex_pairs_both_covered_with_definiens_frac"] = round(len(p_diff) / len(pairs), 4)
    report["simlex_differentia_pair_sample"] = [(a, b, g) for a, b, g in p_diff[:40]]

    # ---------- (c) differentia separability, 30-fact sample ----------
    rng = random.Random(20260813)
    cand = [(n, r) for n, r in all_facts if r.get("definiens_surface")]
    sample = rng.sample(cand, min(30, len(cand)))
    sep = []
    n_usable = 0
    for name, r in sample:
        definiens = r.get("definiens_surface") or ""
        genus = norm_term(r.get("object") or "")
        toks = [t.lower() for t in _WORD.findall(definiens)]
        genus_l = lemma_word(genus) if genus else ""
        diff = []
        for t in toks:
            if is_closed_class(t):
                continue
            tl = lemma_word(t)
            if genus_l and (tl == genus_l or t == genus):
                continue
            diff.append(tl)
        diff = sorted(set(diff))
        usable = len(diff) >= 1
        if usable:
            n_usable += 1
        sep.append({"store": name, "term": r.get("subject"), "genus": genus,
                    "definiens": definiens[:120], "differentia": diff, "usable": usable})
    report["differentia_sample_n"] = len(sample)
    report["differentia_sample_usable"] = n_usable
    report["differentia_sample"] = sep

    print(json.dumps(report, indent=2)[:20000])
    out = os.path.join(REPO_ROOT, "data", "_stage1_differentia_coverage_probe.json")
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    os.replace(out + ".tmp", out)
    print("\nWROTE %s" % out)


if __name__ == "__main__":
    main()
