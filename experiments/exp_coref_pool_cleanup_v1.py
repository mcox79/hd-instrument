"""exp_coref_pool_cleanup_v1 -- a MEASURED, twin-controlled optimization found while drilling "any more
optimizations?": remove mis-extracted FIRST/SECOND-PERSON-pronoun "entities" from the candidate pool.

FINDING. The graded coref resolver's candidate pool (mean ~39 gn-compatible prior entities) is polluted with clusters
whose only mentions are 1st/2nd-person pronouns ("I", "we", "my", "us") -- extraction/agreement artifacts that the
agreement filter wrongly admits as candidates for a 3rd-person pronoun ("he"/"she"/"they"). The brain never tracks a
first-person speaker as a 3rd-person referent (a person-feature the agreement filter should exclude). Dropping these
from the candidate set (a legitimate mention-detection / agreement fix) LIFTS full accuracy CI-separated, and the
info-free RANDOM-drop twin (drop the same NUMBER of candidates at random) LOSES -- so it is removing POLLUTION, not just
shrinking the pool.

RESULT (LitBank competitive pronoun subset, TEST, doc-bootstrap 95% CI): base 0.775 [0.730,0.816] -> drop-artifacts
0.797 [0.754,0.836], +0.022; the random-drop twin 0.756 [0.710,0.798] LOSES (drop-artifacts beats it +0.041). Only ~10
gold-is-artifact cases (0.2%, where dropping would force an error) vs 140 errors caused by an artifact distractor.
Residual shrinks 205 -> 192.

SCOPE. This is adjacency #4 of the_reader_has_no_coherence_next_mention_prior (mention detection / candidate pool), a
SEPARATE lever from the coherence prior. It is a proposed fix to the LIKELIHOOD resolver / cache (strategy owns the
hdlab landing, Q111). NO hdlab write here.

Run: .venv/Scripts/python.exe experiments/exp_coref_pool_cleanup_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_pool_cleanup_v1.py --run
spaCy-free (reads the parsed cache). ASCII. Writes only its own data dir.
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    load_streams, build_instances, _supports, tune_graded, _zscore, _actr_support, CUES, _ci, _pairs, _paired)
from hdlab.graded_competition import graded_pick  # noqa: E402

OUTDIR = os.path.join(REPO, "data", "exp_coref_pool_cleanup_v1")
ARTIFACT = set("i we me us my our you your myself ourselves".split())
NOMINAL_PRON = set("he she it they him her them his its their himself herself itself themselves".split())


def _artifact_clusters(streams):
    head_by = defaultdict(Counter)
    for rec in streams:
        for m in rec["stream"]:
            head_by[(rec["doc"], m["gold"])][m["head_text"].lower()] += 1

    def is_artifact(doc, c):
        hs = [h for h, _n in head_by[(doc, c)].most_common()]
        return bool(hs) and all(h in ARTIFACT or h in NOMINAL_PRON for h in hs) and any(h in ARTIFACT for h in hs)
    return is_artifact


def _pick(inst, w0, d0, drop=None):
    ids, sup, gi = _supports(inst)
    z = {c: _zscore(sup[c]) for c in CUES}
    z["actr"] = _zscore(_actr_support(inst, d0))
    g = graded_pick(z, w0, gain=2.0)
    p = g["p"].copy()
    if drop:
        for i in drop:
            p[i] = -1e18
    return int(np.argmax(p)), gi, ids, sup


def run(docs=None, n_boot=2000, seed=7):
    streams = load_streams(docs)
    insts = build_instances(streams)
    all_docs = sorted({i["doc"] for i in insts})
    dev = [i for i in insts if i["doc"] in set(all_docs[0::2])]
    test = [i for i in insts if i["doc"] not in set(all_docs[0::2])]
    w0, _g, d0 = tune_graded(dev)
    is_artifact = _artifact_clusters(streams)

    rng = np.random.default_rng(seed)
    pd_base = defaultdict(lambda: [0, 0])
    pd_art = defaultdict(lambda: [0, 0])
    pd_rnd = defaultdict(lambda: [0, 0])
    gold_is_art = art_frac = err = err_art = 0
    n = rb = rc = 0
    for inst in test:
        ids, sup, gi = _supports(inst)
        doc = inst["doc"]
        n += 1
        arts = [i for i, c in enumerate(ids) if is_artifact(doc, c)]
        art_frac += len(arts) / len(ids)
        if gi in arts:
            gold_is_art += 1
        k = len(arts)
        rnd = set(rng.choice(len(ids), size=min(k, len(ids) - 1), replace=False)) if k > 0 else set()
        pb, _gi, _i, _s = _pick(inst, w0, d0, None)
        pa, _gi2, _i2, _s2 = _pick(inst, w0, d0, set(arts))
        pr, _gi3, _i3, _s3 = _pick(inst, w0, d0, rnd)
        for pd, pk in ((pd_base, pb), (pd_art, pa), (pd_rnd, pr)):
            pd[doc][0] += int(pk == gi)
            pd[doc][1] += 1
        dom = not ((int(sup["recency"].argmax()) == gi) or (sup["subject"][gi] == sup["subject"].max())
                   or (sup["freq"][gi] == sup["freq"].max()))
        if pb != gi:
            err += 1
            if is_artifact(doc, ids[pb]):
                err_art += 1
            if dom:
                rb += 1
        if pa != gi and dom:
            rc += 1
    cb = _ci(_pairs(pd_base), n_boot, seed + 1)
    ca = _ci(_pairs(pd_art), n_boot, seed + 2)
    cr = _ci(_pairs(pd_rnd), n_boot, seed + 3)
    art_minus_base = _paired(dict(pd_art), dict(pd_base), n_boot, seed + 4)
    art_minus_rnd = _paired(dict(pd_art), dict(pd_rnd), n_boot, seed + 5)
    out = {
        "anchor": "coref_pool_cleanup_v1",
        "population": "LitBank competitive pronoun-antecedent resolution (TEST)",
        "n_test": n, "mean_artifact_fraction_of_pool": round(art_frac / max(n, 1), 4),
        "errors": err, "errors_where_wrong_pick_is_artifact": err_art,
        "gold_is_artifact_cases": gold_is_art,
        "accuracy": {"base": cb, "drop_artifacts": ca, "drop_random_twin": cr},
        "drop_artifacts_minus_base": art_minus_base,
        "drop_artifacts_minus_random_twin": art_minus_rnd,
        "residual_count_base": rb, "residual_count_after_cleanup": rc,
        "verdict": ("POOL_CLEANUP_HELPS_CI_SEP_TWIN_LOSES"
                    if art_minus_base["band"] == "ABOVE" and art_minus_rnd["band"] == "ABOVE"
                    else "NULL_OR_UNCONTROLLED"),
    }
    return out


def self_test():
    """Fixture: the artifact classifier flags a 1st-person-only cluster and spares a real named entity."""
    streams = [{"doc": "t", "stream": [
        {"sent": 0, "start": 0, "gold": 1, "role": "SUBJECT", "head_text": "I"},
        {"sent": 1, "start": 0, "gold": 1, "role": "SUBJECT", "head_text": "my"},
        {"sent": 0, "start": 3, "gold": 2, "role": "OBJECT", "head_text": "Elizabeth"},
        {"sent": 2, "start": 0, "gold": 2, "role": "SUBJECT", "head_text": "she"}]}]
    is_art = _artifact_clusters(streams)
    assert is_art("t", 1), "a 1st-person-only cluster must be flagged as an artifact"
    assert not is_art("t", 2), "a named-entity cluster must NOT be flagged"
    print("SELF-TEST PASS (artifact classifier flags 1st-person-only clusters, spares named entities)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.run:
        m = run(docs=args.docs)
        os.makedirs(OUTDIR, exist_ok=True)
        tmp = os.path.join(OUTDIR, "metrics.json.tmp")
        with open(tmp, "w", encoding="ascii") as fh:
            json.dump(m, fh, indent=2)
        os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
        print(json.dumps(m, indent=2))
        return
    print("use --self-test | --run")


if __name__ == "__main__":
    main()
