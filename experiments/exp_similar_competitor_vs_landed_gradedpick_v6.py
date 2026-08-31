"""exp_similar_competitor_vs_landed_gradedpick_v6 -- THE FAIR TEST against the ALREADY-LANDED organ.

PRIOR-WORK RECKONING. before_you_start flagged, and hdlab confirms, that graded cue-based antecedent retrieval is
ALREADY LANDED: hdlab.graded_coref_pick.graded_antecedent_pick (from the integrated
`coreference_is_capped_at_065_on_real_narrative`, SOLVED/EXCELLENT, owner-DONE) -- recency + subjecthood + ACT-R
base-level + Cb + parallelism, softmax-combined, beating the hard subject-first tier +0.172 CI-sep on real
narrative. So the "content x context combination beats content-only" result is NOT novel; my v1-v5 independently
re-derived it.

THE ONLY QUESTION THIS BRIEF ADDS: does the brief's SPECIFIC new proposal -- the MULTI-TIMESCALE TCM organ
(hdlab.graded_temporal_context) as a context-reinstatement cue -- add anything OVER the landed picker's
single-timescale ACT-R recency? This cell answers it on the real pronoun-coref population:

  ARMS (all on the SAME held-out candidate sets; candidate_priors = [(sent, role)] per candidate):
    HARD_TIER      : the incumbent rigid subject-first pick (graded_coref_pick.hard_tier_pick)   [floor]
    LANDED         : graded_antecedent_pick with its shipped TUNED_WEIGHTS (the current substrate state)
    LANDED+TCM     : the landed graded competition with ONE extra cue = a multi-timescale TCM base-level
                     activation computed from graded_temporal_context (the brief's proposed context cue), weight
                     DEV-tuned on TRAIN alongside the others
    RECENCY_ONLY   : naive recency (content-blind order floor)
    FREQ_ONLY      : frequency (content-only floor)
    TWIN           : LANDED+TCM on shuffled discourse context (must LOSE)

  PASS for the BRIEF's proposal = LANDED+TCM beats LANDED by >= +0.02 hit@1 CI-separated on held-out docs.
  RIGOROUS NEGATIVE (also a full pass per the brief) = it does NOT -> the multi-timescale TCM organ adds nothing
  over the landed single-timescale recency for linear-order antecedent retrieval; report why + the residual axis.

Consumes the LANDED hdlab organs directly (graded_coref_pick, graded_temporal_context). NO external LLM.
Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_vs_landed_gradedpick_v6.py --self-test
     ...                                                                                   --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import graded_coref_pick as GCP
from hdlab.graded_competition import graded_pick

ANCHOR = "similar_competitor_vs_landed_gradedpick_v6"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def tcm_kernel(max_lag, min_period=2.0, max_mult=2.0):
    import torch
    from hdlab.graded_temporal_context import GradedTemporalContext
    g = GradedTemporalContext(d=1024, min_period=min_period, max_period_mult=max_mult, horizon=1000.0)
    c0 = g.ctx(0.0)
    return np.clip(np.array([float((torch.conj(c0) * g.ctx(float(L))).real.mean()) for L in range(max_lag + 1)]), 0.0, None)


def load():
    return json.load(open(PRON, encoding="utf-8"))


def split_docs(insts, frac=0.4, salt=""):
    return set(d for d in sorted(set(i["doc"] for i in insts))
               if (int(hashlib.md5((salt + d).encode()).hexdigest(), 16) % 1000) / 1000.0 < frac)


def cand_priors(inst, shuffle_ctx=False, gen=None):
    """List (per candidate) of prior (sent, role) tuples, leak-free (< p_sent). Returns (priors, gold_index)."""
    ps = int(inst["p_sent"])
    items = []
    for cid, ms in inst["candidates"].items():
        pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if pm:
            items.append((int(cid), pm))
    if shuffle_ctx and items and gen is not None:
        alls = np.array([s for _c, pm in items for s, _ in pm])
        new = []
        for cid, pm in items:
            nm = [(int(gen.choice(alls)), r) for (_s, r) in pm]
            nm = [(s, r) for s, r in nm if s < ps]
            if nm:
                new.append((cid, nm))
        items = new
    if len(items) < 2:
        return None
    cids = [c for c, _ in items]
    priors = [pm for _, pm in items]
    gi = cids.index(int(inst["gold"])) if int(inst["gold"]) in cids else -1
    return priors, gi, ps


def _zscore(v):
    s = v.std()
    return (v - v.mean()) / s if s > 1e-12 else np.zeros_like(v)


def _base_cues(priors, ps, d=GCP.DEFAULT_ACTR_D):
    """Reproduce the landed graded_antecedent_pick's z-scored cue supports (so LANDED+TCM shares them exactly)."""
    prev_sent = max((s for pri in priors for (s, _r) in pri if s < ps), default=None)
    earliest = [min(s for s, _r in pri) for pri in priors]
    first_sent = min(earliest)
    rec, subj, cb, freq, first, par, actr = [], [], [], [], [], [], []
    for i, pri in enumerate(priors):
        nearest = min(GCP._dt(ps, s) for s, _r in pri)
        rec.append(1.0 / nearest)
        subj.append(max(GCP.ROLE_W.get(r, 1.0) for _s, r in pri))
        cb.append(1.0 if any(s == prev_sent and r == "SUBJECT" for s, r in pri) else 0.0)
        freq.append(math.log1p(len(pri)))
        first.append(1.0 if earliest[i] == first_sent else 0.0)
        last_role = max(pri, key=lambda sr: sr[0])[1]
        par.append(1.0 if last_role == "OTHER" else 0.0)  # pron_role defaults OTHER (as live reader default)
        s = sum(GCP.ROLE_W.get(r, 1.0) * (GCP._dt(ps, sent) ** (-d)) for sent, r in pri)
        actr.append(math.log(s) if s > 0 else -1e9)
    return {"recency": _zscore(np.array(rec)), "subject": _zscore(np.array(subj)),
            "cb": _zscore(np.array(cb)), "freq": _zscore(np.array(freq)),
            "first": _zscore(np.array(first)), "parallel": _zscore(np.array(par)),
            "actr": _zscore(np.array(actr))}


def _tcm_cue(priors, ps, kernel):
    """The brief's proposed cue: multi-timescale TCM base-level activation = ln sum_m kernel(dt_m)*role_w."""
    ml = len(kernel) - 1
    out = []
    for pri in priors:
        acc = sum((kernel[ps - s] if 0 <= ps - s <= ml else 0.0) * GCP.ROLE_W.get(r, 1.0) for s, r in pri)
        out.append(math.log(acc) if acc > 0 else -1e9)
    return _zscore(np.array(out))


def landed_pick(priors, ps):
    return GCP.graded_antecedent_pick(priors, ps)["pick"]


def landed_tcm_pick(sup, tcm, w, gain=GCP.DEFAULT_GAIN):
    z = dict(sup); z["tcm"] = tcm
    return int(graded_pick(z, w, gain=gain)["win"])


def recency_pick(priors, ps):
    return int(max(range(len(priors)), key=lambda i: max(s for s, _ in priors[i])))


def freq_pick(priors, ps):
    return int(max(range(len(priors)), key=lambda i: (len(priors[i]), max(s for s, _ in priors[i]))))


def acc(rows, predfn):
    return float(np.mean([int(predfn(r) == r["gi"]) for r in rows])) if rows else float("nan")


def paired(a, b, gen, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a - b; n = len(diff)
    idx = gen.integers(0, n, size=(n_boot, n)); boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    p95 = float(np.percentile(np.abs((diff[None, :] * signs).mean(axis=1)), 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "band": band, "n": n}


def prep(insts, kernel, shuffle_ctx=False, seed=7):
    gen = np.random.default_rng(seed)
    rows = []
    for inst in insts:
        cp = cand_priors(inst, shuffle_ctx=shuffle_ctx, gen=gen)
        if cp is None:
            continue
        priors, gi, ps = cp
        rows.append({"priors": priors, "gi": gi, "ps": ps,
                     "sup": _base_cues(priors, ps), "tcm": _tcm_cue(priors, ps, kernel)})
    return rows


def tune_tcm_weight(rows):
    """DEV-tune the TCM cue weight added onto the landed TUNED_WEIGHTS (coordinate search on train hit@1)."""
    base = dict(GCP.TUNED_WEIGHTS)
    best_w, best = None, -1
    for wt in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]:
        w = dict(base); w["tcm"] = wt
        a = acc(rows, lambda r, w=w: landed_tcm_pick(r["sup"], r["tcm"], w))
        if a > best:
            best, best_w = a, w
    return best_w, best


def run(n_boot=2000):
    t0 = time.perf_counter()
    insts = load()
    kernel = tcm_kernel(400)
    gen = np.random.default_rng(20260830)
    test_docs = split_docs(insts)
    tr = prep([i for i in insts if i["doc"] not in test_docs], kernel)
    te = prep([i for i in insts if i["doc"] in test_docs], kernel)

    w_tcm, tr_acc = tune_tcm_weight(tr)
    _log("DEV-tuned TCM weight added to landed weights: tcm=%.2f (train acc=%.3f)" % (w_tcm["tcm"], tr_acc))

    a_hard = acc(te, lambda r: GCP.hard_tier_pick(r["priors"], r["ps"]))
    a_rec = acc(te, lambda r: recency_pick(r["priors"], r["ps"]))
    a_freq = acc(te, lambda r: freq_pick(r["priors"], r["ps"]))
    a_landed = acc(te, lambda r: landed_pick(r["priors"], r["ps"]))
    a_ltcm = acc(te, lambda r: landed_tcm_pick(r["sup"], r["tcm"], w_tcm))

    cv_landed = np.array([int(landed_pick(r["priors"], r["ps"]) == r["gi"]) for r in te], float)
    cv_ltcm = np.array([int(landed_tcm_pick(r["sup"], r["tcm"], w_tcm) == r["gi"]) for r in te], float)
    cv_hard = np.array([int(GCP.hard_tier_pick(r["priors"], r["ps"]) == r["gi"]) for r in te], float)
    cv_freq = np.array([int(freq_pick(r["priors"], r["ps"]) == r["gi"]) for r in te], float)

    d_tcm_vs_landed = paired(cv_ltcm, cv_landed, gen, n_boot)
    d_landed_vs_hard = paired(cv_landed, cv_hard, gen, n_boot)
    d_landed_vs_freq = paired(cv_landed, cv_freq, gen, n_boot)

    # twin: LANDED+TCM on shuffled context
    te_tw = prep([i for i in insts if i["doc"] in test_docs], kernel, shuffle_ctx=True, seed=101)
    a_twin = acc(te_tw, lambda r: landed_tcm_pick(r["sup"], r["tcm"], w_tcm))

    tcm_helps = (d_tcm_vs_landed["band"] == "ABOVE" and d_tcm_vs_landed["delta"] >= 0.02)
    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_test": len(te), "n_train": len(tr), "tcm_weight": w_tcm["tcm"],
           "acc": {"HARD_TIER": a_hard, "FREQ_ONLY": a_freq, "RECENCY_ONLY": a_rec,
                   "LANDED": a_landed, "LANDED_plus_TCM": a_ltcm, "TWIN_shuffle_ctx": a_twin},
           "delta_TCM_vs_LANDED": d_tcm_vs_landed, "delta_LANDED_vs_HARD": d_landed_vs_hard,
           "delta_LANDED_vs_FREQ": d_landed_vs_freq, "twin_loses": bool(a_twin < a_ltcm),
           "BRIEF_TCM_PROPOSAL": "SUPPORTED" if tcm_helps else "RIGOROUS_NEGATIVE"}
    _log("=== held-out TEST (n=%d) ===" % len(te))
    _log("  FREQ_ONLY(content)=%.3f  RECENCY_ONLY=%.3f  HARD_TIER=%.3f" % (a_freq, a_rec, a_hard))
    _log("  LANDED graded_antecedent_pick=%.3f  LANDED+TCM=%.3f  TWIN(shuffle-ctx)=%.3f" % (a_landed, a_ltcm, a_twin))
    _log("  LANDED - HARD_TIER = %+.3f [%.3f,%.3f] %s (reproduces the landed +0.172-style win?)"
         % (d_landed_vs_hard["delta"], d_landed_vs_hard["lo"], d_landed_vs_hard["hi"], d_landed_vs_hard["band"]))
    _log("  LANDED - FREQ(content) = %+.3f [%.3f,%.3f] %s"
         % (d_landed_vs_freq["delta"], d_landed_vs_freq["lo"], d_landed_vs_freq["hi"], d_landed_vs_freq["band"]))
    _log("  LANDED+TCM - LANDED = %+.3f [%.3f,%.3f] %s  <-- the brief's proposal"
         % (d_tcm_vs_landed["delta"], d_tcm_vs_landed["lo"], d_tcm_vs_landed["hi"], d_tcm_vs_landed["band"]))
    _log("BRIEF TCM-PROPOSAL VERDICT: %s (twin loses=%s) (%.1fs)"
         % (res["BRIEF_TCM_PROPOSAL"], res["twin_loses"], res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: landed organs importable; cue supports built; TCM cue added to graded_pick")
    ker = tcm_kernel(30)
    priors = [[(2, "SUBJECT")], [(8, "OTHER"), (9, "OTHER")]]
    sup = _base_cues(priors, 10)
    assert "actr" in sup and len(sup["actr"]) == 2
    tcm = _tcm_cue(priors, 10, ker)
    w = dict(GCP.TUNED_WEIGHTS); w["tcm"] = 1.0
    pk = landed_tcm_pick(sup, tcm, w)
    assert pk in (0, 1)
    # landed picker returns a valid index
    assert GCP.graded_antecedent_pick(priors, 10)["pick"] in (0, 1)
    _log("SELF-TEST PASS")
    return {"ok": True}


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
