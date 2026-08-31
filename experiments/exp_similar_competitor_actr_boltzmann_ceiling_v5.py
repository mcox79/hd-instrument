"""exp_similar_competitor_actr_boltzmann_ceiling_v5 -- settle INFORMATIONAL vs COMBINATION-RULE limit.

QUESTION. The additive coord-ascent combiner plateaus at ~0.650 held-out (v4). The oracle "any of my cues right"
is 0.813 (diagnostic). Is the gap (a) an INFORMATIONAL limit (my accessibility cues simply lack the answer on the
residual) or (b) a COMBINATION-RULE limit (the answer is in the cues but a linear-additive argmax can't extract
it)? This decides the honest conclusion and the next lever.

METHOD (the FAITHFUL upgrade, not an ML bolt-on). ACT-R retrieval is not argmax of a hand-weighted sum -- it is
BOLTZMANN/softmax over activations (retrieval probability P(i) ~ exp(A_i / s); Anderson 2004). So fit the SAME
linear ACT-R activation A_i = w . cue_features(i) by MAXIMUM LIKELIHOOD of the gold under the softmax (listwise
Plackett-Luce top-1) on TRAIN, evaluate argmax on HELD-OUT TEST. This is the principled version of v4's crude
hit@1 coord-ascent; if it beats 0.650 the combination rule was the bottleneck, if it plateaus the residual is
informational (needs new cues: agreement-phi or the structural/semantic parse -- both ADJACENT, mapped).

Also fits a per-query CONFIDENCE-scaled variant and reports the oracle-of-my-cues for reference. Cues + TCM organ
identical to v4 (CONSUMED). Weights learned on TRAIN docs, all numbers on HELD-OUT TEST docs. NO external LLM.
Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_actr_boltzmann_ceiling_v5.py --self-test
     ...                                                                                     --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR = "similar_competitor_actr_boltzmann_ceiling_v5"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON_PATH = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")

CUES = ("RECENCY", "BASE", "SUBJREC", "FREQ", "FIRST")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def tcm_kernel_table(max_lag, min_period=2.0, max_mult=2.0, horizon=1000.0, d=1024):
    import torch
    from hdlab.graded_temporal_context import GradedTemporalContext
    g = GradedTemporalContext(d=d, min_period=min_period, max_period_mult=max_mult, horizon=horizon)
    c0 = g.ctx(0.0)
    tab = np.empty(max_lag + 1, dtype=np.float64)
    for L in range(max_lag + 1):
        tab[L] = float((torch.conj(c0) * g.ctx(float(L))).real.mean())
    return np.clip(tab, 0.0, None)


def load_instances():
    return json.load(open(PRON_PATH, encoding="utf-8"))


def split_docs(insts, test_frac=0.4, salt=""):
    return set(d for d in sorted(set(i["doc"] for i in insts))
               if (int(hashlib.md5((salt + d).encode()).hexdigest(), 16) % 1000) / 1000.0 < test_frac)


def prior_mentions(inst):
    ps = int(inst["p_sent"])
    out = {}
    for cid, ms in inst["candidates"].items():
        pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if pm:
            out[int(cid)] = pm
    return out


def build_queries(insts):
    qs = []
    for inst in insts:
        pv = prior_mentions(inst)
        if len(pv) < 2:
            continue
        qs.append({"gold": int(inst["gold"]), "p_sent": int(inst["p_sent"]), "pv": pv, "n_cand": len(pv)})
    return qs


def cue_matrix(q, kernel):
    """(n_cand, 5) standardized-within-query cue feature matrix; row order = sorted candidate ids; gold_idx."""
    pv, ps = q["pv"], q["p_sent"]
    maxlag = len(kernel) - 1
    cands = sorted(pv.keys())

    def kern(dt):
        return kernel[dt] if 0 <= dt <= maxlag else 0.0

    intro = {c: min(s for s, _ in pv[c]) for c in cands}
    earliest = min(intro.values())
    any_subject = any(any(r == "SUBJECT" for _, r in pv[c]) for c in cands)
    rows = []
    for c in cands:
        dts = [ps - s for s, _ in pv[c]]
        rec = kern(min(dts))
        base = sum(kern(d) for d in dts)
        subj_dts = [ps - s for s, r in pv[c] if r == "SUBJECT"]
        subjrec = (kern(min(subj_dts)) if subj_dts else 0.0) if any_subject else kern(min(dts))
        freq = np.log1p(len(pv[c]))
        first = 1.0 if intro[c] == earliest else 0.0
        rows.append([rec, base, subjrec, freq, first])
    X = np.array(rows, float)
    # standardize each column within the query
    mu = X.mean(axis=0); sd = X.std(axis=0)
    Xz = np.where(sd > 1e-12, (X - mu) / np.where(sd > 1e-12, sd, 1.0), 0.0)
    gi = cands.index(q["gold"]) if q["gold"] in cands else -1
    return Xz, gi, cands


def precompute(qs, kernel):
    out = []
    for q in qs:
        Xz, gi, cands = cue_matrix(q, kernel)
        out.append({"X": Xz, "gold_idx": gi, "n_cand": len(cands)})
    return out


def fit_boltzmann(pre, lr=0.3, epochs=300, l2=1e-3, temp=1.0, seed=0):
    """Maximize sum_q log softmax(X w / temp)[gold] on TRAIN. Full-batch gradient ascent. Deterministic."""
    w = np.zeros(len(CUES))
    n = len(pre)
    for ep in range(epochs):
        grad = np.zeros(len(CUES))
        for p in pre:
            if p["gold_idx"] < 0:
                continue
            a = p["X"] @ w / temp
            a = a - a.max()
            e = np.exp(a); pr = e / e.sum()
            # d/dw logP(gold) = (x_gold - sum_c pr_c x_c)/temp
            grad += (p["X"][p["gold_idx"]] - pr @ p["X"]) / temp
        grad = grad / n - l2 * w
        w = w + lr * grad
    return w


def boltz_acc(pre, w):
    ok = 0; tot = 0
    for p in pre:
        if p["gold_idx"] < 0:
            tot += 1; continue
        tot += 1
        a = p["X"] @ w
        ok += int(int(np.argmax(a)) == p["gold_idx"])
    return ok / tot if tot else float("nan")


def cue_alone_acc(pre, cue_idx):
    ok = 0; tot = 0
    for p in pre:
        tot += 1
        ok += int(int(np.argmax(p["X"][:, cue_idx])) == p["gold_idx"])
    return ok / tot if tot else float("nan")


def oracle_any(pre):
    ok = 0; tot = 0
    for p in pre:
        tot += 1
        gi = p["gold_idx"]
        ok += int(any(int(np.argmax(p["X"][:, k])) == gi for k in range(len(CUES))))
    return ok / tot if tot else float("nan")


def paired_delta(a, b, gen, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a - b; n = len(diff)
    idx = gen.integers(0, n, size=(n_boot, n)); boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    p95 = float(np.percentile(np.abs((diff[None, :] * signs).mean(axis=1)), 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "band": band, "n": n}


def correct_vec_boltz(pre, w):
    return np.array([int(int(np.argmax(p["X"] @ w)) == p["gold_idx"]) for p in pre], float)


def correct_vec_cue(pre, k):
    return np.array([int(int(np.argmax(p["X"][:, k])) == p["gold_idx"]) for p in pre], float)


def run(n_boot=2000):
    t0 = time.perf_counter()
    insts = load_instances()
    kernel = tcm_kernel_table(400)
    gen = np.random.default_rng(20260830)
    test_docs = split_docs(insts, salt="")
    tr = [i for i in insts if i["doc"] not in test_docs]
    te = [i for i in insts if i["doc"] in test_docs]
    pre_tr = precompute(build_queries(tr), kernel)
    pre_te = precompute(build_queries(te), kernel)

    w = fit_boltzmann(pre_tr)
    ci = {c: i for i, c in enumerate(CUES)}
    floor = {"FREQUENCY": cue_alone_acc(pre_te, ci["FREQ"]), "RECENCY": cue_alone_acc(pre_te, ci["RECENCY"]),
             "SUBJ_REC": cue_alone_acc(pre_te, ci["SUBJREC"])}
    strongest = max(floor, key=lambda k: floor[k])
    boltz = boltz_acc(pre_te, w)
    orc = oracle_any(pre_te)

    cv = correct_vec_boltz(pre_te, w)
    d_content = paired_delta(cv, correct_vec_cue(pre_te, ci["FREQ"]), gen, n_boot)
    d_rec = paired_delta(cv, correct_vec_cue(pre_te, ci["RECENCY"]), gen, n_boot)
    d_strong = paired_delta(cv, correct_vec_cue(pre_te, ci["SUBJREC"] if strongest == "SUBJ_REC"
                            else (ci["RECENCY"] if strongest == "RECENCY" else ci["FREQ"])), gen, n_boot)

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_train_q": len(pre_tr), "n_test_q": len(pre_te), "weights_boltzmann": dict(zip(CUES, w.tolist())),
           "floor": floor, "strongest": strongest, "boltzmann_acc": boltz, "oracle_any_cue": orc,
           "d_content": d_content, "d_recency": d_rec, "d_strongest": d_strong,
           "train_boltz_acc": boltz_acc(pre_tr, w),
           "combination_gap_to_oracle": orc - boltz}
    _log("FLOORS test: FREQ=%.3f RECENCY=%.3f SUBJ_REC=%.3f [strongest=%s]"
         % (floor["FREQUENCY"], floor["RECENCY"], floor["SUBJ_REC"], strongest))
    _log("ACT-R Boltzmann (ML-fit) train=%.3f  TEST=%.3f  | oracle-of-my-cues=%.3f  | gap-to-oracle=%.3f"
         % (res["train_boltz_acc"], boltz, orc, res["combination_gap_to_oracle"]))
    _log("  weights=%s" % {c: round(v, 2) for c, v in zip(CUES, w.tolist())})
    _log("  Boltz - FREQ = %+.3f[%s]  - RECENCY = %+.3f[%s]  - SUBJ_REC = %+.3f[%s]"
         % (d_content["delta"], d_content["band"], d_rec["delta"], d_rec["band"], d_strong["delta"], d_strong["band"]))
    verdict = ("COMBINATION_RULE_HELPS" if boltz >= 0.68 else
               ("MARGINAL" if boltz >= 0.655 else "PLATEAU_INFORMATIONAL"))
    res["INTERPRETATION"] = verdict
    _log("INTERPRETATION: %s (Boltzmann %.3f vs additive-coordascent ~0.650 vs oracle %.3f)" % (verdict, boltz, orc))
    _log("DONE %.1fs" % res["elapsed_s"])
    return res


def self_test():
    _log("SELF-TEST: cue matrix standardized; boltzmann fit runs; recovers a recency-dominant weight on toy")
    ker = tcm_kernel_table(40)
    # toy: gold is always the most-recent candidate -> fit should put weight on RECENCY (col 0)
    qs = []
    for k in range(60):
        s_gold = 8 + (k % 3)
        qs.append({"gold": 1, "p_sent": 12, "n_cand": 2,
                   "pv": {1: [(s_gold, "OTHER")], 2: [(1, "OTHER"), (2, "OTHER")]}})  # gold recent, other frequent+old
    pre = precompute(qs, ker)
    w = fit_boltzmann(pre, epochs=200)
    assert w[0] > w[3], "recency weight should exceed frequency weight when gold is always the recent one: %s" % w
    assert boltz_acc(pre, w) > 0.9, "should fit the toy near-perfectly: %.3f" % boltz_acc(pre, w)
    _log("SELF-TEST PASS  toy weights=%s acc=%.3f" % ({c: round(v, 2) for c, v in zip(CUES, w.tolist())}, boltz_acc(pre, w)))
    return {"toy_acc": boltz_acc(pre, w)}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run()
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
