"""exp_atl_hubspoke_signal_loss_ladder_v1 -- LOCATE the largest recoverable signal loss on THIS harness, then set up
the attack. The prior decomposition (parent break_the_contextual...) said 100% of the loss is the context QUERY and an
oracle that knew the diagnostic context word would reach ~0.85 -- i.e. the cue is in the frozen context, we just can't
identify it. This cell re-measures that oracle on OUR harness and shows how much each realistic diagnostic-word
identifier recovers -- so the attack targets a sized, real opportunity.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

LADDER (strict doc-disjoint SemCor subordinate, n=2676; keys = rich atoms; frozen w2v context):
  full_bag         -- flat context mean query (the topical blur)                        ~0.28
  precision        -- diagnosticity-weighted (this problem's Cell B)                    ~0.334
  specificity      -- weight context words by ACT-R fan-specificity (few-sense = weigh more)
  spec_topk        -- keep only the k most-SPECIFIC context words (concentrate the query)
  ORACLE_single    -- CEILING: pick the ONE context word (if we knew which) whose w2v picks gold via the keys
  ORACLE_signed    -- CEILING: pick the ONE context word that maximally separates gold from its dominant competitor
Reports the recoverable headroom (realistic -> oracle) = the size of the diagnostic-word-identification opportunity.

Glass-box, frozen w2v, NO external LLM. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import math
import pickle
import argparse
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_signal_loss_ladder_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        test_idx = test_idx[:400]
    cand = set()
    for i in test_idx:
        cand.update(recs[i]["tn"])
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in sorted(cand)}

    # global sense-fan per word (how many distinct GOLD senses a word co-occurs with) for specificity weighting
    w_fan = defaultdict(set)
    for i in range(len(recs)):
        r = recs[i]
        for x in r["ctx"]:
            if x in w2i:
                w_fan[x].add(r["gold"])

    arms = {k: [] for k in ["full_bag", "precision", "specificity", "spec_topk3",
                            "ORACLE_single", "ORACLE_signed", "oracle_single_exists"]}
    for i in test_idx:
        r = recs[i]; tn = r["tn"]; gold = r["gold"]
        ctxw = [x for x in r["ctx"] if x in w2i]
        if not ctxw or gold not in tn:
            continue
        C = np.stack([_unit(mat[w2i[x]]) for x in ctxw])
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            continue
        gi = tn.index(gold)
        prior = np.asarray(r["prior"], float)[:len(tn)]
        dom = int(np.argmax(prior)); dom = dom if dom != gi else int(np.argsort(-prior)[1]) if len(tn) > 1 else gi
        sim = C @ G.T                                     # (W, S) cos(context word, sense key)

        # full bag
        q = _unit(C.mean(0)); arms["full_bag"].append(int(np.argmax(G @ q) == gi))
        # precision (diagnosticity gamma=3, top-5)
        diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        thr = np.sort(diag)[-5] if len(diag) > 5 else diag.min()
        wq = np.where(diag >= thr, diag, 0.0) ** 3.0
        qp = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else q
        arms["precision"].append(int(np.argmax(G @ qp) == gi))
        # specificity (ACT-R fan): few-sense words weigh more
        spec = np.array([1.0 / (1.0 + math.log(1.0 + len(w_fan.get(x, ())))) for x in ctxw])
        qs = _unit((spec[:, None] * C).sum(0)) if spec.sum() > 1e-9 else q
        arms["specificity"].append(int(np.argmax(G @ qs) == gi))
        # spec_topk3: keep only the 3 most-specific context words
        k = min(3, len(ctxw)); keep = np.argsort(-spec)[:k]
        qk = _unit(C[keep].mean(0)); arms["spec_topk3"].append(int(np.argmax(G @ qk) == gi))
        # ORACLE_single: is there ONE context word whose key-argmax == gold? (upper bound for diagnostic-word ID)
        picks = np.argmax(sim, axis=1)                    # each context word's argmax sense
        exists = bool(np.any(picks == gi))
        arms["oracle_single_exists"].append(int(exists))
        arms["ORACLE_single"].append(int(exists))         # if we could pick the right word, we'd get gold
        # ORACLE_signed: the context word that maximally separates gold from the dominant competitor
        sep = sim[:, gi] - sim[:, dom]
        best_w = int(np.argmax(sep))
        arms["ORACLE_signed"].append(int(np.argmax(G @ _unit(C[best_w])) == gi))

    def m(x):
        return round(float(np.mean(x)), 4) if len(x) else None
    A = {k: m(v) for k, v in arms.items()}
    res = {
        "n_test": len(test_idx), "arms": A,
        "recoverable_headroom": {
            "precision_to_oracle_single": round((A["ORACLE_single"] or 0) - (A["precision"] or 0), 4),
            "precision_to_oracle_signed": round((A["ORACLE_signed"] or 0) - (A["precision"] or 0), 4),
            "specificity_gain_over_precision": round((A["specificity"] or 0) - (A["precision"] or 0), 4),
            "spec_topk_gain_over_precision": round((A["spec_topk3"] or 0) - (A["precision"] or 0), 4)},
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("SIGNAL-LOSS LADDER | full_bag=%.4f precision=%.4f specificity=%.4f spec_topk3=%.4f || "
                       "ORACLE_single=%.4f (exists=%.4f) ORACLE_signed=%.4f | recoverable headroom precision->oracle=%+.4f"
                       % (A["full_bag"], A["precision"], A["specificity"], A["spec_topk3"], A["ORACLE_single"],
                          A["oracle_single_exists"], A["ORACLE_signed"], res["recoverable_headroom"]["precision_to_oracle_signed"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_signal_loss_ladder_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (signal-loss ladder cell imports)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
