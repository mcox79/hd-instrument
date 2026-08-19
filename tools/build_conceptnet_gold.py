"""BUILD AN ADMISSIBLE, NON-WORDNET, NON-LLM MEANING GOLD FROM CONCEPTNET. Provenance-filtered.

WHY. The binding constraint on every supervision and evaluation source in this project is
CIRCULARITY, not performance: the dissociation instrument DEFINES both sides of its labels from
WordNet, so anything derived from WordNet trains on the test. The replacement task -- does the
substrate ground the RIGHT meaning for a term -- needs a gold that is independent of WordNet, of
any LLM, and of our own extractors.

ConceptNet qualifies IF AND ONLY IF it is filtered by provenance, and it carries the field needed
to do that. Measured on an alphabetical prefix of 400,000 English-English edges: 78.2%
`/d/wiktionary/en`, 18.0% `/d/conceptnet/4/en` (crowd), 0.1% `/d/wordnet/3.1`. **This tool walks
the WHOLE file, because that prefix figure was explicitly NOT a file-wide fact and was recorded as
such.**

🪤 AND IT DELIBERATELY DOES NOT USE `data/datasets/conceptnet5_en_100k.jsonl`, which is
pre-extracted, small, fast, and CARRIES NO PROVENANCE FIELD AT ALL -- only subject/predicate/
object. WordNet cannot be excluded from it, so it is inadmissible however convenient. That file is
this project's "way we lose is by trying fancy available tools" rule sitting on disk in one place.

WHAT IT WRITES
  data/conceptnet_gold_v1/edges.jsonl    one row per kept edge: {subj, rel, obj, dataset, weight}
  data/conceptnet_gold_v1/manifest.json  FULL-FILE counts by dataset and relation, what was
                                         dropped and why, and the exclusion list -- so a later
                                         reader can audit admissibility without re-walking 498 MB.

USAGE
  python tools/build_conceptnet_gold.py            # full build (walks ~34M edges)
  python tools/build_conceptnet_gold.py --limit N  # bounded smoke
  python tools/build_conceptnet_gold.py --self-test
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import os
import sys
import time
from typing import Dict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(REPO, "data", "conceptnet", "conceptnet-assertions-5.7.0.csv.gz")
OUT_DIR = os.path.join(REPO, "data", "conceptnet_gold_v1")

# EXCLUDED BY PROVENANCE. Substring match on the `dataset` field, case-insensitive.
EXCLUDE_DATASETS = ("wordnet",)

# Relations that carry MEANING rather than morphology or surface form. `/r/DerivedFrom` is the
# single most common English relation and is deliberately OUT: it relates word FORMS, not senses,
# and a gold built on it would reward our morphology rather than our comprehension.
KEEP_RELS = frozenset((
    "/r/IsA", "/r/DefinedAs", "/r/PartOf", "/r/HasA", "/r/MadeOf", "/r/UsedFor",
    "/r/CapableOf", "/r/AtLocation", "/r/HasProperty", "/r/Causes", "/r/MotivatedByGoal",
    "/r/HasSubevent", "/r/ReceivesAction", "/r/Synonym", "/r/SimilarTo",
))


def _term(uri: str) -> str:
    """`/c/en/dog/n/animal` -> `dog`. Sense and POS suffixes are dropped deliberately: our store
    is keyed by LEMMA and a gold keyed finer than the system under test cannot be scored."""
    parts = uri.split("/")
    return parts[3] if len(parts) > 3 else ""


def build(limit: int = 0) -> dict:
    if not os.path.isfile(SRC):
        raise SystemExit(f"source not found: {SRC}")
    os.makedirs(OUT_DIR, exist_ok=True)
    ds_all: Dict[str, int] = collections.Counter()
    rel_all: Dict[str, int] = collections.Counter()
    ds_kept: Dict[str, int] = collections.Counter()
    rel_kept: Dict[str, int] = collections.Counter()
    n_rows = n_en = n_kept = 0
    n_drop_wordnet = n_drop_rel = 0
    t0 = time.time()

    out_path = os.path.join(OUT_DIR, "edges.jsonl")
    tmp = out_path + ".tmp"
    with gzip.open(SRC, "rt", encoding="utf-8", errors="replace") as fh, \
            open(tmp, "w", encoding="utf-8", newline="") as out:
        for line in fh:
            n_rows += 1
            if limit and n_rows > limit:
                break
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            # STRING FILTER BEFORE JSON PARSE. ~34M rows; parsing meta for non-English edges
            # would dominate the runtime for nothing.
            if not (parts[2].startswith("/c/en/") and parts[3].startswith("/c/en/")):
                continue
            n_en += 1
            rel = parts[1]
            rel_all[rel] += 1
            try:
                meta = json.loads(parts[4])
            except json.JSONDecodeError:
                continue
            dataset = str(meta.get("dataset", "?"))
            ds_all[dataset] += 1
            if any(x in dataset.lower() for x in EXCLUDE_DATASETS):
                n_drop_wordnet += 1
                continue
            if rel not in KEEP_RELS:
                n_drop_rel += 1
                continue
            s, o = _term(parts[2]), _term(parts[3])
            if not s or not o or s == o:
                continue
            out.write(json.dumps({"subj": s, "rel": rel, "obj": o, "dataset": dataset,
                                  "weight": meta.get("weight", 1.0)}, ensure_ascii=True) + "\n")
            n_kept += 1
            ds_kept[dataset] += 1
            rel_kept[rel] += 1
    os.replace(tmp, out_path)

    man = {
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": os.path.relpath(SRC, REPO).replace("\\", "/"),
        "full_file_walk": not bool(limit),
        "rows_scanned": n_rows, "en_en_edges": n_en, "edges_kept": n_kept,
        "dropped_wordnet_provenance": n_drop_wordnet,
        "dropped_relation_not_meaning": n_drop_rel,
        "excluded_datasets": list(EXCLUDE_DATASETS),
        "kept_relations": sorted(KEEP_RELS),
        "deliberately_excluded_relation_note": (
            "/r/DerivedFrom is the most common English relation and is EXCLUDED: it relates word "
            "FORMS, not senses, so a gold built on it would reward our morphology rather than our "
            "comprehension."),
        "admissibility": (
            "No WordNet-provenance edge is present. No LLM was involved. This is an OFFLINE, "
            "STATIC asset, which the owner's 2026-08-16 ruling makes admissible: the invariant is "
            "NO LLM AT INFERENCE, not from-scratch construction."),
        "dataset_counts_en_all": dict(ds_all.most_common(30)),
        "dataset_counts_kept": dict(ds_kept.most_common(30)),
        "relation_counts_en_all": dict(rel_all.most_common(40)),
        "relation_counts_kept": dict(rel_kept.most_common(40)),
        "seconds": round(time.time() - t0, 1),
    }
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(man, fh, indent=2)
    return man


def self_test() -> int:
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    check(_term("/c/en/dog/n/animal") == "dog", "term extraction drops sense and POS suffixes")
    check(_term("/c/en/ice_cream") == "ice_cream", "term extraction keeps a multiword lemma")
    check("/r/DerivedFrom" not in KEEP_RELS,
          "DerivedFrom is EXCLUDED -- it relates word forms, not senses")
    check("/r/IsA" in KEEP_RELS and "/r/DefinedAs" in KEEP_RELS,
          "the meaning relations are kept")
    check(any("wordnet" in x for x in EXCLUDE_DATASETS),
          "wordnet provenance is on the exclusion list")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    man = build(a.limit)
    print(json.dumps({k: v for k, v in man.items()
                      if not k.endswith("_counts_en_all")}, indent=2)[:2600])
    print(f"\n[gold] {man['edges_kept']} edges -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
