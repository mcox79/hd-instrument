"""Grow the selectional (verb -> role -> filler) store FROM THE SUBSTRATE'S OWN READING CHAIN -- no external parser.

WHY (2026-09-12, upstream BF pass): the heads rung's semantic-bootstrapping teacher (attachment_arm.SemanticBootstrapTeacher)
reads verb-noun plausibility from hdlab.typed_selectional_preference, whose store data/selectional_preferences_v1/
selectional_slots_v1.pkl was EXTRACTED in August with a UD-shaped parser -- the last non-brain-foundational dependency of
the rung. The brain grows that knowledge from its own comprehension: structure and meaning co-develop (semantic bootstrapping
+ syntactic bootstrapping, Pinker 1984 / Gleitman 1990). This tool closes the loop: categories from reading
(reading-induced inventory, or the supervised tagger as the NOT_BF reference), heads from the attachment arm, roles from the
role competition, and the resulting SUBJ / OBJ / obl:<prep> fillers are accrued into a store with the SAME shape the typed
preference organ fits (keys (verb_surface, role) -> {filler: count}).

Output: data/selectional_preferences_bf_v1/selectional_slots_bf_v1.pkl (+ a JSON report). Then:
  python -m hdlab.typed_selectional_preference build --store <that pkl> --out data/frontend_assets/typed_selectional_preference_bf_v1.json
  python tools/build_attachment_validities.py --tsp-asset data/frontend_assets/typed_selectional_preference_bf_v1.json --cap 1500 --eval
Usage: python tools/grow_selectional_store_bf.py --lines 30000 [--categories data/frontend_assets/induced_categories_simplewiki_1m_k68.json | --tagger]
Glass-box, numpy only; NO spaCy / nltk / LLM on the path. Cap cores: OMP_NUM_THREADS etc. are set to 3 by default here.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse
import json
import pickle
import re
import sys
import time
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

CORPUS = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
OUT_DIR = os.path.join(REPO, "data", "selectional_preferences_bf_v1")
OUT_PKL = os.path.join(OUT_DIR, "selectional_slots_bf_v1.pkl")
_TOK = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\sA-Za-z0-9]")


def tokenize(line: str):
    return _TOK.findall(line)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=30000)
    ap.add_argument("--skip", type=int, default=0, help="skip the first N lines (e.g. to avoid the categories' own slice)")
    ap.add_argument("--categories", default=os.path.join(REPO, "data", "frontend_assets", "induced_categories_simplewiki_1m_k68.json"))
    ap.add_argument("--tagger", action="store_true", help="use the supervised tagger (NOT_BF reference) instead of induced categories")
    ap.add_argument("--maxlen", type=int, default=40)
    ap.add_argument("--out", default=OUT_PKL)
    a = ap.parse_args(argv)
    t0 = time.time()
    from hdlab import attachment_arm as AA
    from hdlab.graded_role_assigner import coarse_roles, load_coarse_validities, NOMINAL
    from tools.build_attachment_validities import induced_categorizer
    table = AA.load_attachment_validities(); rtab = load_coarse_validities()
    if a.tagger:
        from hdlab.pos_tagger import PosTagger  # NOT_BF reference only
        from hdlab.situation_reader import _FRONTEND_POS_ASSET
        tg = PosTagger.load(_FRONTEND_POS_ASSET)
        categorize = lambda toks: list(tg.tag(toks))
        cat_source = "supervised tagger (NOT_BF reference)"
    else:
        categorize = induced_categorizer(a.categories)
        cat_source = "reading-induced categories (%s)" % os.path.basename(a.categories)
    slot = defaultdict(Counter); roles_hist = Counter(); n_seen = n_used = 0
    with open(CORPUS, encoding="utf-8") as f:
        for li, line in enumerate(f):
            if li < a.skip:
                continue
            if n_seen >= a.lines:
                break
            n_seen += 1
            toks = tokenize(line.strip())
            if not (3 <= len(toks) <= a.maxlen):
                continue
            cats = categorize(toks)
            if "VERB" not in cats or not any(c in NOMINAL for c in cats):
                continue
            heads = AA.heads(toks, cats, table)
            deps = coarse_roles(toks, cats, heads, rtab)
            n_used += 1
            for i, dep in deps.items():
                h = heads.get(i, 0)
                if h <= 0 or cats[h - 1] != "VERB":
                    continue
                verb = toks[h - 1].lower(); filler = toks[i - 1].lower()
                if dep == "nsubj":
                    role = "SUBJ"
                elif dep in ("obj", "nsubj:pass"):          # the undergoer slot (passive subject IS the object filler)
                    role = "OBJ"
                elif dep == "iobj":
                    role = "IOBJ"
                elif dep in ("obl", "obl:agent"):
                    # the preposition governing this nominal (case convention: ADP -> NP head), else bare obl
                    prep = next((toks[k - 1].lower() for k in range(1, len(toks) + 1) if heads.get(k) == i and cats[k - 1] == "ADP"), None)
                    role = "obl:%s" % prep if prep else "obl:_"
                    if dep == "obl:agent":
                        role = "obl:by"
                else:
                    continue
                slot[(verb, role)][filler] += 1; roles_hist[role.split(":")[0] if role.startswith("obl") else role] += 1
            if n_used % 2000 == 0:
                print("[grow] %d lines seen, %d used, %d slots, %.0fs" % (n_seen, n_used, len(slot), time.time() - t0), flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    store = {"extractor_version": "selectional_bf_v1.0 (own chain: %s -> attachment_arm -> coarse_roles)" % cat_source,
             "corpus": CORPUS, "lines_seen": n_seen, "lines_used": n_used,
             "slot_filler": {k: dict(v) for k, v in slot.items()}, "word_cooc": {},
             "stats": {"n_seen": n_seen, "n_parsed": n_used, "n_slot_observations": int(sum(roles_hist.values()))},
             "role_histogram": dict(roles_hist), "n_slots": len(slot), "elapsed_s": round(time.time() - t0, 1)}
    with open(a.out, "wb") as f:
        pickle.dump(store, f)
    rep = {k: v for k, v in store.items() if k not in ("slot_filler", "word_cooc")}
    rep["example_slots"] = {"%s/%s" % k: v.most_common(6) for k, v in list(sorted(slot.items(), key=lambda kv: -sum(kv[1].values())))[:8]}
    with open(a.out.replace(".pkl", "_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    print("wrote", a.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
