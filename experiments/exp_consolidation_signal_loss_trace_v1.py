"""exp_consolidation_signal_loss_trace_v1 -- WHERE does the reading-derived knowledge lose signal?

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

The consolidation chain is: READING co-occurrence -> ATTRIBUTE to a sense -> CONSOLIDATE (keep recurring/clean)
-> INTEGRATE into the sense signature -> diagnostic READOUT. This cell swaps each stage for an ORACLE and
measures a_s (strict doc-disjoint SemCor subordinate, odd docs) so we localize the leak -- exactly the parent's
oracle-ablation method, applied to the knowledge-growth stage.

ORACLE ARMS (all vs the same gloss baseline; scored mean-pool AND top-k/exemplar):
  A0 GLOSS               sense signature = WordNet gloss/hypernym seeds only (no reading knowledge).
  A2 ORACLE-ATTRIBUTION  the reading co-occurrence with PERFECT sense attribution: built from SemCor's OWN
                         GOLD sense tags on the EVEN (train) docs -- i.e. "if the reader disambiguated every
                         occurrence correctly, on in-domain text, how much would sense-attributed co-occurrence
                         help?" Document-disjoint (even build / odd test). Consolidated (recurrence + cap).
  A3 CURATED (SyntagNet) the human-disambiguated syntagmatic associations = the clean ceiling.
INTEGRATION axis: MEAN-pool signature (the wired readout) vs TOP-K/exemplar best-match (non-diluting).

READS THE SIGNAL-LOSS LEDGER off the gaps:
  A2 - A0  = value of reading co-occurrence WITH perfect attribution (isolates the SOURCE + ATTRIBUTION stages).
  A3 - A2  = value curation adds BEYOND perfect attribution (manual pair-selection / cross-corpus quality).
  topk - mean (per arm) = the INTEGRATION/representation loss (prototype-averaging dilution).
Compared against our ACTUAL glass-box result (from exp_consolidation_gate_readbind_v1 metrics), this says whether
our leak is ATTRIBUTION (A2>>ours), CONSOLIDATION-QUALITY (A3>>A2), INTEGRATION (topk>>mean), or the SOURCE
itself (A2 ~ A0 -> reading co-occurrence carries little rare-sense signal even perfectly attributed).

Glass-box, frozen w2v, NO external LLM. A2 uses gold ONLY as a diagnostic oracle (allowed), never at inference.
ASCII-only. Own data dir.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import sys
import json
import time
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_signal_loss_trace_v1")


def _consolidate_recur(agg, cap, K):
    """recurrence >= K, top-cap by (recur*ppmi). agg: {w: (support, recur, ppmi)}."""
    words = [(w, rc * (pp if pp > 0 else 0.01)) for w, (sup, rc, pp) in agg.items() if rc >= K]
    words.sort(key=lambda x: -x[1])
    return [w for w, _ in words[:cap]]


def run(cap, K_oracle, smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:300]
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in cand}

    # ---- A2 ORACLE-ATTRIBUTION: sense->context co-occurrence from SemCor GOLD tags on EVEN (train) docs ----
    ocooc = defaultdict(Counter); osel = Counter(); ouni = Counter(); oN = 0
    for i, r in enumerate(recs):
        if doc[i] % 2 == 0:                       # EVEN = train (document-disjoint from odd test)
            g = r["gold"]; ctx = set(x for x in r["ctx"] if x in w2i)
            if not ctx:
                continue
            ocooc[g].update(ctx); osel[g] += 1
            for x in ctx:
                ouni[x] += 1
            oN += 1
    def oracle_agg(s):
        c = ocooc.get(s, {}); ns = osel.get(s, 0); agg = {}
        for w, cnt in c.items():
            agg[w] = (1, cnt, G1._ppmi(cnt, ns, ouni.get(w, 0), max(1, oN)))
        return agg
    oracle_assoc = {s: _consolidate_recur(oracle_agg(s), cap, K_oracle) for s in cand}

    # ---- arms ----
    gloss_assoc = {s: [] for s in cand}
    syntag_assoc = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    arms = {"A0_gloss": gloss_assoc, "A2_oracle_attribution": oracle_assoc, "A3_curated_syntagnet": syntag_assoc}

    Ctx = G1.precompute_ctx(recs, test_idx, mat, w2i)
    res = {"n_test_sub": len(test_idx), "cap": cap, "K_oracle": K_oracle,
           "oracle_train_instances": oN, "oracle_senses_covered": len(ocooc),
           "a_s": {}, "paired_vs_gloss": {}, "mean_assoc": {}}
    oks = {}
    for name, assoc in arms.items():
        mean_sig = G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i)
        ok_mean = G1.score(recs, test_idx, mean_sig, Ctx)
        sw = {s: list(seeds_by_syn[s]) + list(assoc.get(s, [])) for s in cand}
        ok_topk = G1.score_topk(recs, test_idx, sw, mean_sig, Ctx, mat, w2i, k=3)
        oks[(name, "mean")] = ok_mean; oks[(name, "topk")] = ok_topk
        res["a_s"][name] = {"mean": round(float(ok_mean.mean()), 4), "topk": round(float(ok_topk.mean()), 4)}
        res["mean_assoc"][name] = round(float(np.mean([len(assoc[s]) for s in cand])), 2)
        print("[arm] %-24s a_s mean=%.4f  topk=%.4f  (assoc/sense=%.1f, %.0fs)"
              % (name, res["a_s"][name]["mean"], res["a_s"][name]["topk"], res["mean_assoc"][name],
                 time.time() - t0), flush=True)

    gmean = oks[("A0_gloss", "mean")]; gtopk = oks[("A0_gloss", "topk")]
    for name in arms:
        if name == "A0_gloss":
            continue
        res["paired_vs_gloss"][name] = {
            "mean": G1._paired(oks[(name, "mean")], gmean, 301),
            "topk": G1._paired(oks[(name, "topk")], gtopk, 302)}
    # integration loss: topk vs mean on each arm
    res["integration_topk_minus_mean"] = {
        name: round(res["a_s"][name]["topk"] - res["a_s"][name]["mean"], 4) for name in arms}
    # the ledger
    a2m, a3m = res["a_s"]["A2_oracle_attribution"]["mean"], res["a_s"]["A3_curated_syntagnet"]["mean"]
    a0m = res["a_s"]["A0_gloss"]["mean"]
    res["LEDGER"] = {
        "source+attribution_gain (A2-A0, mean)": round(a2m - a0m, 4),
        "curation_beyond_attribution (A3-A2, mean)": round(a3m - a2m, 4),
        "best_topk": max(res["a_s"][n]["topk"] for n in arms),
    }
    res["headline"] = (
        "SIGNAL-LOSS TRACE (n=%d) | gloss=%.3f/%.3f | ORACLE-ATTR=%.3f/%.3f (sep_mean=%s) | "
        "CURATED=%.3f/%.3f (sep_mean=%s) | A2-A0=%+.3f A3-A2=%+.3f | topk-mean(oracle)=%+.3f"
        % (len(test_idx), a0m, res["a_s"]["A0_gloss"]["topk"], a2m, res["a_s"]["A2_oracle_attribution"]["topk"],
           res["paired_vs_gloss"]["A2_oracle_attribution"]["mean"]["sep"], a3m,
           res["a_s"]["A3_curated_syntagnet"]["topk"], res["paired_vs_gloss"]["A3_curated_syntagnet"]["mean"]["sep"],
           a2m - a0m, a3m - a2m, res["integration_topk_minus_mean"]["A2_oracle_attribution"]))
    res["elapsed_s"] = round(time.time() - t0, 1)
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_signal_loss_trace_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    agg = {"river": (1, 5, 2.0), "the": (1, 1, 0.0)}
    out = _consolidate_recur(agg, 5, 2)
    assert out == ["river"], "recurrence gate keeps river (5>=2), drops the (1<2)"
    print("SELFTEST PASS", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--K-oracle", type=int, default=2)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(args.cap, args.K_oracle, smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
