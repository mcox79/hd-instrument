"""exp_knowledge_factory_consumer_usage_tweak_v1 -- follow the consumer-usage tweak to the end: does swapping the
LIVE hub consumer's AvgSim (mean-centroid) scoring for MaxSim / top-k nearest-EXEMPLAR help on the task it actually
does (which-argument selection), in the DISTRIBUTIONAL HUB SPACE it actually uses?

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift (owner: look at one
consumer's store usage for a small tweak that makes it cleaner + performs better; follow it to actionable/ideal).

THE CONSUMER: hdlab.composed_hub_predictor -- loads hub_ppmi_svd_200d, scores which argument a verb takes by
cos(candidate, verb-patient CENTROID) (AvgSim). THE TWEAK: score by the candidate's similarity to its NEAREST
patient exemplar (MaxSim / top-k), keeping the INSTANCE distribution instead of a blurry centroid (Erk-Pado 2010).
The parent problem proved exemplar>centroid +0.067 in the GROUNDED space; this tests whether it transfers to the
DISTRIBUTIONAL HUB the live organ uses -- previously UNMEASURED.

TASK: QA-SRL which-argument (data/predict_revise_recall_v1/_population.json), the AMBIGUOUS slice (passive /
non-canonical / gold pre-verbal) where position cannot decide and selectional preference must. Metric = patient
pick accuracy (pick==gold_head). CONTROLS: verb-SHUFFLED-exemplar twin (same candidates, WRONG verb's exemplars ->
must LOSE); floors = POSITION-only (pos_pick) and the LIVE wired reader (wired_pick). Paired item bootstrap.
Glass-box, NO external LLM, deterministic. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_consumer_usage_tweak_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.composed_hub_predictor import HubComposedPredictor

POP = os.path.join(_REPO, "data", "predict_revise_recall_v1", "_population.json")
OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_consumer_usage_tweak_v1")
_EPS = 1e-9


def _n(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + _EPS)


def _pick_centroid(cvs, ex):                       # AvgSim: cos to the mean patient centroid (CURRENT usage)
    c = ex.mean(0); c = c / (np.linalg.norm(c) + _EPS)
    s = [(cv @ c) if cv is not None else -9.0 for cv in cvs]
    return int(np.argmax(s))


def _pick_exemplar(cvs, exn, knn):                 # MaxSim / top-k nearest exemplar (the TWEAK)
    s = []
    for cv in cvs:
        if cv is None:
            s.append(-9.0); continue
        cos = exn @ (cv / (np.linalg.norm(cv) + _EPS))
        k = min(knn, len(cos))
        s.append(float(np.sort(cos)[-k:].mean()))
    return int(np.argmax(s))


def _acc(rows, pickfn):
    ok = np.array([int(r["cand_heads"][pickfn(r)] == r["gold_head"]) for r in rows], float)
    return ok


def _paired(a, b, seed=7, reps=2000):
    d = float(a.mean() - b.mean()); rng = np.random.default_rng(seed); n = len(a)
    boots = [float((a[i] - b[i]).mean()) for i in (rng.integers(0, n, n) for _ in range(reps))]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": round(d, 4), "ci": [round(float(lo), 4), round(float(hi), 4)], "sep": bool(lo > 0)}


def run(smoke=False, knn=3):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    pr = HubComposedPredictor.load(); vec = pr.vec; store = pr.store
    pop = json.load(open(POP))["pop"]
    rng = np.random.default_rng(13)
    store_verbs = list(store.keys())

    rows = []
    for r in pop:
        v = r.get("verb")
        if v not in store or not r.get("gold_in_cands") or len(r.get("cand_heads", [])) < 2:
            continue
        cvs = [vec(h) for h in r["cand_heads"]]
        cvs = [None if (cv is None) else np.asarray(cv, float) for cv in cvs]
        if all(cv is None for cv in cvs) or store[v][0] is None or len(store[v][0]) < 2:
            continue
        r = dict(r); r["_cvs"] = cvs; r["_ex"] = np.asarray(store[v][0], float)
        r["_exn"] = _n(r["_ex"]); r["_shuf_exn"] = _n(np.asarray(store[rng.choice(store_verbs)][0], float))
        rows.append(r)
    if smoke:
        rows = rows[:400]
    amb = [r for r in rows if r.get("voice") == "passive" or r.get("noncanonical") or r.get("gold_preverbal")]
    print("[tweak] eval rows=%d | ambiguous slice=%d (%.0fs)" % (len(rows), len(amb), time.time() - t0), flush=True)

    def evalset(rs, tag):
        cen = _acc(rs, lambda r: _pick_centroid(r["_cvs"], r["_ex"]))
        ex1 = _acc(rs, lambda r: _pick_exemplar(r["_cvs"], r["_exn"], 1))
        exk = _acc(rs, lambda r: _pick_exemplar(r["_cvs"], r["_exn"], knn))
        shf = _acc(rs, lambda r: _pick_exemplar(r["_cvs"], r["_shuf_exn"], knn))
        # chance floor = 1/mean(#candidates) (a real, aligned floor; the stored pos_pick/wired_pick are a different
        # index space in this harness and were dropped rather than reported misleadingly).
        chance = float(np.mean([1.0 / max(1, len(r["cand_heads"])) for r in rs]))
        d = {"n": len(rs), "AvgSim_centroid": round(float(cen.mean()), 4),
             "MaxSim_1nn": round(float(ex1.mean()), 4), "MaxSim_topk": round(float(exk.mean()), 4),
             "verb_shuffled_twin": round(float(shf.mean()), 4), "chance_floor": round(chance, 4),
             "TWEAK_vs_centroid": _paired(exk, cen, 1), "TWEAK_vs_shuffled_twin": _paired(exk, shf, 2)}
        print("[tweak] %-10s n=%d | AvgSim %.4f -> MaxSim-1nn %.4f / topk %.4f (d=%+.4f sep=%s) | twin %.4f | chance %.4f"
              % (tag, d["n"], d["AvgSim_centroid"], d["MaxSim_1nn"], d["MaxSim_topk"],
                 d["TWEAK_vs_centroid"]["delta"], d["TWEAK_vs_centroid"]["sep"], d["verb_shuffled_twin"],
                 d["chance_floor"]), flush=True)
        return d

    res = {"knn": knn, "AMBIGUOUS": evalset(amb, "AMBIGUOUS"), "FULL": evalset(rows, "FULL"),
           "elapsed_s": round(time.time() - t0, 1)}
    a = res["AMBIGUOUS"]
    verdict = ("TWEAK WINS: MaxSim exemplar beats AvgSim centroid CI-sep on the ambiguous slice (twin loses) -> "
               "the usage tweak transfers to the distributional hub -- adopt it (construction-conditionally)."
               if a["TWEAK_vs_centroid"]["sep"] and a["MaxSim_topk"] > a["verb_shuffled_twin"] else
               "TWEAK does NOT beat AvgSim CI-sep in the hub space here -> the exemplar lever is grounded-space-"
               "specific; keep AvgSim for this consumer (located negative for the hub-space tweak).")
    res["VERDICT"] = verdict
    res["headline"] = ("CONSUMER-USAGE TWEAK (ambiguous n=%d): AvgSim %.4f -> MaxSim %.4f (d=%+.4f sep=%s) | "
                       "twin %.4f loses=%s | chance %.4f | %s"
                       % (a["n"], a["AvgSim_centroid"], a["MaxSim_topk"], a["TWEAK_vs_centroid"]["delta"],
                          a["TWEAK_vs_centroid"]["sep"], a["verb_shuffled_twin"],
                          a["MaxSim_topk"] > a["verb_shuffled_twin"], a["chance_floor"], verdict.split(":")[0]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_consumer_usage_tweak_v1", "verdict": "MEASURED",
                   "result": res}, f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # exemplar pick selects the candidate near a real exemplar cluster; centroid picks the average-closest.
    ex = np.array([[1.0, 0, 0], [0, 1.0, 0]])          # two distinct patient clusters
    exn = _n(ex)
    cvs = [np.array([0.98, 0.0, 0.1]), np.array([0.4, 0.4, 0.8])]  # cand0 near cluster-0; cand1 near neither
    assert _pick_exemplar(cvs, exn, 1) == 0, "exemplar picks the candidate nearest a real cluster"
    print("SELFTEST PASS (exemplar pick selects near-cluster candidate)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--knn", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=None)
    a = ap.parse_args(argv)
    if a.self_test:
        return 0 if self_test() else 1
    run(smoke=a.smoke, knn=a.knn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
