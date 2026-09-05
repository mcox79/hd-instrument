"""exp_knowledge_factory_gap_analysis_v1 -- transform the frozen knowledge base into a ranked "WHAT TO LEARN"
acquisition backlog: pinpoint the gaps so the step-2 learner reads TARGETED material instead of everything.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift

WHY (owner 2026-09-04): "transform this KB to see what gaps you have and indicate what you need to learn to
improve optimally... knowing what to look for is a big key." The decisive representation test showed the meaning
ceiling is a DATA GAP (no post-hoc transform beats keep-all; sibling-minus-random cosine 0.027), so the lever is
TARGETED ACQUISITION. This produces the acquisition list.

THREE GAP DETECTORS (research-grounded literature drill 2026-09-04):
  1. DISCRIMINABILITY gaps -- the collapsed sibling sense-pairs (highest pairwise cosine): the reader literally
     cannot separate these; "what to learn" = discriminative features/contexts for them. (intrinsic, no labels.)
  2. COVERAGE gaps -- Good-Turing/Chao1 flavour: synsets whose curated bag is THIN (few associates, gloss-only),
     weighted by how often the reader meets that word -> under-covered frequent senses. (intrinsic, no labels.)
  3. EMPIRICAL CONFUSION -- run the readout on held-out text; the low-margin/wrong items and the sense-pairs they
     confuse (uncertainty sampling / expected-error-reduction target). (uses the eval as the corpus proxy.)
The union, ranked, is the "what to look for" backlog -> the active-learning target set for step-2 growth.

Reuses the meaning-store builder + the live hdlab readout. Glass-box, NO external LLM. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_gap_analysis_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse
from collections import defaultdict, Counter

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_knowledge_factory_meaning_store_v1 as M
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_gap_analysis_v1")


def discriminability_gaps(prep, sig_by_syn, top_n=25):
    """Collapsed sibling sense-pairs: for each lemma with >=2 senses, the pairwise cosine of their signatures.
    Return the most-collapsed pairs (highest cosine) -> the reader cannot tell these apart -> acquire
    discriminative knowledge for them."""
    from nltk.corpus import wordnet as wn
    by_lemma = defaultdict(list)
    for syn in prep["syns"]:
        v = sig_by_syn.get(syn)
        if v is None:
            continue
        try:
            s = wn.synset(syn); by_lemma[(s.lemmas()[0].name(), s.pos())].append((syn, v))
        except Exception:
            continue
    pairs = []
    for (lem, pos), items in by_lemma.items():
        if len(items) < 2:
            continue
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                c = float(np.dot(items[i][1].astype(np.float32), items[j][1].astype(np.float32)))
                pairs.append({"lemma": lem, "pos": pos, "sense_a": items[i][0], "sense_b": items[j][0],
                              "cosine": round(c, 4)})
    pairs.sort(key=lambda p: -p["cosine"])
    return pairs[:top_n]


def coverage_gaps(prep, cand_freq, top_n=25):
    """Thin-bag synsets weighted by how often the reader meets them. gap_score = freq / (1 + n_associates):
    frequent word + thin curated bag = the biggest coverage hole. Reports gloss-only senses too."""
    rows = []
    for s in prep["syns"]:
        na = len(prep["assoc"][s]); f = cand_freq.get(s, 0)
        if f == 0:
            continue
        rows.append({"synset": s, "freq": int(f), "n_associates": int(na),
                     "gloss_only": bool(na == 0), "gap_score": round(f / (1.0 + na), 3)})
    rows.sort(key=lambda r: -r["gap_score"])
    return rows[:top_n]


def empirical_confusion(recs, idxs, sig_by_syn, Ctx, top_n=25):
    """Run the readout; collect WRONG or LOW-MARGIN items and the (predicted, gold) sense-pair they confuse.
    The most-frequent confused pairs are the uncertainty/expected-error-reduction acquisition targets."""
    conf = Counter(); n_low = 0; n_scored = 0; margins = []
    zero = np.zeros(M.EMB_DIM, np.float32)
    for i in idxs:
        C = Ctx[i]
        if C is None:
            continue
        tn = recs[i]["tn"]
        G = np.stack([sig_by_syn.get(s) if sig_by_syn.get(s) is not None else zero for s in tn]).astype(np.float64)
        if not np.any(G):
            continue
        sc = diagnostic_context_scores(C, G)
        order = np.argsort(-sc)
        pred = tn[int(order[0])]; n_scored += 1
        margin = float(sc[order[0]] - sc[order[1]]) if len(order) > 1 else 1.0
        margins.append(margin)
        if pred != recs[i]["gold"]:
            conf[tuple(sorted((pred, recs[i]["gold"])))] += 1
        if margin < 0.02:
            n_low += 1
    top = [{"confused_pair": list(k), "count": int(v)} for k, v in conf.most_common(top_n)]
    return {"n_scored": n_scored, "n_low_margin": n_low,
            "mean_margin": round(float(np.mean(margins)), 4) if margins else None, "top_confusions": top}


def run(level=3, smoke=False, top_n=25):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = M._load_eval()
    if smoke:
        dev = dev[:400]; test = test[:400]; top_n = 10
    cand = set(); cand_freq = Counter()
    for i in dev + test:
        for s in recs[i]["tn"]:
            cand.add(s)
        cand_freq[recs[i]["gold"]] += 1
    prep = M.prep_bags(cand, mat, w2i, level)
    sig = M.sigs_at(prep, mat, w2i, None)
    Ctx = G1.precompute_ctx(recs, test, mat, w2i)

    disc = discriminability_gaps(prep, sig, top_n)
    cov = coverage_gaps(prep, cand_freq, top_n)
    emp = empirical_confusion(recs, test, sig, Ctx, top_n)

    n_gloss_only = sum(1 for s in prep["syns"] if len(prep["assoc"][s]) == 0)
    res = {"level": level, "n_candidates": len(cand),
           "summary": {"n_collapsed_pairs_ge_0_95": sum(1 for p in
                       discriminability_gaps(prep, sig, 10 ** 9) if p["cosine"] >= 0.95),
                       "n_gloss_only_synsets": int(n_gloss_only),
                       "mean_readout_margin": emp["mean_margin"], "n_low_margin": emp["n_low_margin"],
                       "n_scored": emp["n_scored"]},
           "discriminability_gaps_top": disc, "coverage_gaps_top": cov,
           "empirical_confusion": emp, "elapsed_s": round(time.time() - t0, 1)}
    res["headline"] = ("GAP MAP: %d sense-pairs collapsed>=0.95 | %d gloss-only synsets | readout mean-margin "
                       "%.4f (%d/%d low-margin) -> targeted-acquisition backlog written (top %d each)"
                       % (res["summary"]["n_collapsed_pairs_ge_0_95"], n_gloss_only,
                          emp["mean_margin"] or -1, emp["n_low_margin"], emp["n_scored"], top_n))
    with open(os.path.join(OUT_DIR, "acquisition_backlog_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_gap_analysis_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    if disc:
        print("  worst collapsed pairs:", ", ".join("%s(%s/%s cos=%.2f)"
              % (p["lemma"], p["sense_a"].split(".")[-1], p["sense_b"].split(".")[-1], p["cosine"])
              for p in disc[:5]), flush=True)
    return res


def self_test():
    # discriminability_gaps ranks a collapsed pair above a separated one.
    rng = np.random.default_rng(0)
    a = G1._unit(rng.standard_normal(M.EMB_DIM))
    prep = {"syns": ["bank.n.01", "bank.n.09", "dog.n.01"]}
    sig = {"bank.n.01": a, "bank.n.09": a * 0.99 + 0.01 * G1._unit(rng.standard_normal(M.EMB_DIM)),
           "dog.n.01": G1._unit(rng.standard_normal(M.EMB_DIM))}
    g = discriminability_gaps(prep, sig, 10)
    assert g and g[0]["lemma"] == "bank" and g[0]["cosine"] > 0.9, "collapsed bank pair ranks first: %s" % g[:1]
    print("SELFTEST PASS (gap map ranks the collapsed bank sense-pair first, cos=%.3f)" % g[0]["cosine"], flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--top-n", type=int, default=25)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(level=args.level, smoke=args.smoke, top_n=args.top_n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
