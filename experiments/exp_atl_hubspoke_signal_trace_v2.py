"""exp_atl_hubspoke_signal_trace_v2 -- RE-TRACE the signal loss with CHANCE CONTROLS to answer the decisive question:
is the static-embedding rare-sense loss an EXTRACTION limit (diagnostic signal present in the frozen context, we fail
to aggregate it) or a REPRESENTATION limit (the signal isn't there -- static vectors are near-MFS by nature)?

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

The prior "ORACLE_single 0.868 => the cue is in the context" claim is SUSPECT: with ~3 senses x ~10 context words,
chance that SOME word argmaxes to a SPECIFIC sense is ~0.98 -- ORACLE_single may be pure combinatorics. This cell
chance-controls it and measures the genuine per-token diagnostic signal density.

DIAGNOSTICS (strict doc-disjoint SemCor subordinate, n=2676; rich-atom keys; frozen w2v):
  per context word c: a(c)=argmax_s cos(c,key_s), margin(c)=top1-top2.
  - point_gold / point_dom / chance(1/S): fraction of context words whose argmax is gold / dominant / chance.
  - ORACLE_any_gold vs ORACLE_any_dom vs ORACLE_any_random: does SOME word point to gold MORE than to the dominant
    or a random non-gold sense? (if gold~=dom~=random, ORACLE_single is combinatorics = NO per-word gold signal.)
  - signed tilt: mean_c [cos(c,gold_key)-cos(c,dom_key)] -- is the context on average tilted toward gold? (0 = none)
  - concentration: does point_gold RISE among high-margin (confident) words? (signal concentrates) or stay at chance?
  - knowledge-free aggregation ceilings: plurality-vote and margin-weighted-vote a_s (no averaging, no knowledge).
  - MFS baseline (always pick dominant) for reference.

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
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_signal_trace_v2")


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
    rng = np.random.default_rng(20260904)

    P = {k: [] for k in ["S", "chance", "point_gold", "point_dom", "point_rand",
                         "orc_gold", "orc_dom", "orc_rand", "tilt_gold_dom", "tilt_gold_rand",
                         "point_gold_hi_margin", "point_gold_lo_margin",
                         "hit_plurality", "hit_marginvote", "hit_mfs"]}
    for i in test_idx:
        r = recs[i]; tn = r["tn"]; gold = r["gold"]
        if gold not in tn or len(tn) < 2:
            continue
        ctxw = [x for x in r["ctx"] if x in w2i]
        if not ctxw:
            continue
        C = np.stack([_unit(mat[w2i[x]]) for x in ctxw])
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            continue
        S = len(tn); gi = tn.index(gold)
        prior = np.asarray(r["prior"], float)[:S]; di = int(np.argmax(prior)); di = di if di != gi else int(np.argsort(-prior)[1])
        ri = int(rng.choice([j for j in range(S) if j != gi]))    # a random non-gold sense
        sim = C @ G.T                                             # (W,S)
        a = np.argmax(sim, axis=1)                               # each word's argmax sense
        srt = np.sort(sim, axis=1)[:, ::-1]
        margin = srt[:, 0] - srt[:, 1]
        P["S"].append(S); P["chance"].append(1.0 / S)
        P["point_gold"].append(float(np.mean(a == gi)))
        P["point_dom"].append(float(np.mean(a == di)))
        P["point_rand"].append(float(np.mean(a == ri)))
        P["orc_gold"].append(int(np.any(a == gi)))
        P["orc_dom"].append(int(np.any(a == di)))
        P["orc_rand"].append(int(np.any(a == ri)))
        P["tilt_gold_dom"].append(float(np.mean(sim[:, gi] - sim[:, di])))
        P["tilt_gold_rand"].append(float(np.mean(sim[:, gi] - sim[:, ri])))
        hi = margin >= np.median(margin)
        P["point_gold_hi_margin"].append(float(np.mean(a[hi] == gi)) if hi.any() else np.nan)
        P["point_gold_lo_margin"].append(float(np.mean(a[~hi] == gi)) if (~hi).any() else np.nan)
        # knowledge-free aggregation ceilings
        votes = np.bincount(a, minlength=S); P["hit_plurality"].append(int(np.argmax(votes) == gi))
        mv = np.zeros(S)
        for wi in range(len(ctxw)):
            mv[a[wi]] += margin[wi]
        P["hit_marginvote"].append(int(np.argmax(mv) == gi))
        P["hit_mfs"].append(int(di == gi))                       # MFS never right on subordinate (sanity: ~0)

    def m(k):
        v = np.asarray(P[k], float); v = v[~np.isnan(v)]
        return round(float(v.mean()), 4) if len(v) else None
    res = {
        "n_scored": len(P["S"]), "mean_S": m("S"), "chance_1_over_S": m("chance"),
        "per_word_pointing": {"gold": m("point_gold"), "dominant": m("point_dom"), "random_nongold": m("point_rand"),
                              "gold_minus_chance": round((m("point_gold") or 0) - (m("chance") or 0), 4),
                              "gold_minus_random": round((m("point_gold") or 0) - (m("point_rand") or 0), 4)},
        "oracle_single": {"gold": m("orc_gold"), "dominant": m("orc_dom"), "random_nongold": m("orc_rand"),
                          "gold_minus_random": round((m("orc_gold") or 0) - (m("orc_rand") or 0), 4)},
        "signed_tilt": {"gold_vs_dominant": m("tilt_gold_dom"), "gold_vs_random": m("tilt_gold_rand")},
        "margin_concentration": {"point_gold_high_margin": m("point_gold_hi_margin"),
                                 "point_gold_low_margin": m("point_gold_lo_margin")},
        "knowledge_free_ceilings": {"plurality_vote": m("hit_plurality"), "margin_weighted_vote": m("hit_marginvote"),
                                    "mfs_on_subordinate": m("hit_mfs")},
        "elapsed_s": round(time.time() - t0, 1),
    }
    # verdict: extraction (signal present above chance) vs representation (signal ~chance) limit
    gmc = res["per_word_pointing"]["gold_minus_chance"]; gmr_o = res["oracle_single"]["gold_minus_random"]
    res["verdict"] = ("EXTRACTION-LIMITED (per-word gold signal ABOVE chance/random; the info is present, we fail to "
                      "aggregate it)" if (gmc > 0.02 and gmr_o > 0.03) else
                      "REPRESENTATION-LIMITED (per-word gold signal ~= chance/random; ORACLE_single is combinatorics; "
                      "the diagnostic signal is NOT in the static context vectors)")
    res["headline"] = ("SIGNAL TRACE v2 | S=%.2f chance=%.3f | point: gold=%.3f dom=%.3f rand=%.3f (gold-chance=%+.3f "
                       "gold-rand=%+.3f) | ORACLE_single gold=%.3f rand=%.3f (d=%+.3f) | tilt gold-dom=%+.4f "
                       "gold-rand=%+.4f | margin-conc hi=%.3f lo=%.3f | plurality=%.3f marginvote=%.3f || %s"
                       % (res["mean_S"], res["chance_1_over_S"], res["per_word_pointing"]["gold"],
                          res["per_word_pointing"]["dominant"], res["per_word_pointing"]["random_nongold"],
                          gmc, res["per_word_pointing"]["gold_minus_random"], res["oracle_single"]["gold"],
                          res["oracle_single"]["random_nongold"], gmr_o, res["signed_tilt"]["gold_vs_dominant"],
                          res["signed_tilt"]["gold_vs_random"], res["margin_concentration"]["point_gold_high_margin"],
                          res["margin_concentration"]["point_gold_low_margin"],
                          res["knowledge_free_ceilings"]["plurality_vote"],
                          res["knowledge_free_ceilings"]["margin_weighted_vote"], res["verdict"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_signal_trace_v2", "verdict": "MEASURED", "result": res}, f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (signal-trace v2 imports)", flush=True)
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
