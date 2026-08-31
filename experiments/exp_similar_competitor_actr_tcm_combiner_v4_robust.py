"""exp_similar_competitor_actr_tcm_combiner_v4_robust -- FINALIZE + CROSS-SPLIT ROBUSTNESS for
retrieval_interference_is_similar_competitor_cue_overload_not_event_count.

STATE COMING IN (from v1/v2/v3, all on disk):
 - Diagnostic: real LitBank pronoun coref, ambiguous subset; floors freq 0.570 / recency 0.642 / subj-rec 0.660;
   oracle-any-cue 0.813 -> +0.152 headroom (the experiment CAN succeed; the cues are complementary).
 - v1 single fused base-level sum: 0.562 (below recency) -- accumulates frequency, weights the wrong cue.
 - v2/v3 cue combination: the RELIABILITY / cue-overload gate (my proposed refinement, Van Dyke & McElree) did
   NOT help -- the ablation refuted it (linear 0.650 > reliability 0.639). Cue-validity (no-fit) weighting also
   fails (0.574). The honest winner is an ADDITIVE ACT-R activation with weights FIT on train (as real ACT-R
   models are fit): recency (TCM organ) + subject-recency + a little frequency.

THIS CELL locks the honest headline arm and tests whether its margins are ROBUST or a lucky split:
  ARM = additive ACT-R cue activation, weights coord-ascent-fit on TRAIN, evaluated on HELD-OUT TEST.
        score_i = sum_cue W_cue * p_cue(i);  p_cue = within-query softmax of z-scored cue value.
  CUES = RECENCY, BASE, SUBJREC (subject-recency w/ recency fallback), FREQ, FIRST -- all PINNED accessibility
         cues; the TCM organ (graded_temporal_context, CONSUMED) supplies the temporal kernel.
  FLOORS (recomputed per split, same population): FREQUENCY (content-only), RECENCY (naive), SUBJ_REC_FALLBACK
         (STRONGEST accessibility heuristic).
  TWINS (must LOSE) on the headline arm: SHUFFLE_CTX (kills temporal context), SHUFFLE_ROLE (kills salience).
  ROBUSTNESS: refit + re-evaluate across N independent doc splits (different hash salts). Report mean +/- std of
         (combiner - content_floor) and (combiner - strongest_floor), and how many splits clear each bar.

BAR (from PROBLEM.md, verbatim): "the content x TCM-context-reinstatement cue beats the content-only floor by
>= +0.10 hit@1, CI-separated ..., with the info-free twin ... LOSING, AND it beats naive-recency-alone".
We ALSO hold ourselves to the discipline's strongest-floor rule (beat subject-recency-fallback), and report it
even where it is only marginal -- honesty over a green check.

NO external LLM. Consumes the TCM organ (torch). Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_actr_tcm_combiner_v4_robust.py --self-test
     ...                                                                                       --full
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

ANCHOR = "similar_competitor_actr_tcm_combiner_v4_robust"
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
    out = set()
    for d in sorted(set(i["doc"] for i in insts)):
        h = int(hashlib.md5((salt + d).encode()).hexdigest(), 16) % 1000 / 1000.0
        if h < test_frac:
            out.add(d)
    return out


def prior_mentions(inst):
    ps = int(inst["p_sent"])
    out = {}
    for cid, ms in inst["candidates"].items():
        pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if pm:
            out[int(cid)] = pm
    return out


def build_queries(insts, shuffle_ctx=False, shuffle_role=False, seed=0):
    gen = np.random.default_rng(seed)
    doc_sents, doc_roles = {}, {}
    if shuffle_ctx or shuffle_role:
        for inst in insts:
            d = inst["doc"]
            for ms in inst["candidates"].values():
                for m in ms:
                    doc_sents.setdefault(d, []).append(int(m["sent"]))
                    doc_roles.setdefault(d, []).append(str(m.get("role") or "OTHER"))
    qs = []
    for inst in insts:
        pv = prior_mentions(inst)
        if len(pv) < 2:
            continue
        ps = int(inst["p_sent"])
        if shuffle_ctx or shuffle_role:
            d = inst["doc"]; spool = np.array(doc_sents[d]); rpool = doc_roles[d]
            new = {}
            for cid, pm in pv.items():
                nm = []
                for (s, r) in pm:
                    ns = int(gen.choice(spool)) if shuffle_ctx else s
                    nr = str(rpool[int(gen.integers(0, len(rpool)))]) if shuffle_role else r
                    if ns < ps:
                        nm.append((ns, nr))
                if nm:
                    new[cid] = nm
            pv = new
            if len(pv) < 2:
                continue
        qs.append({"gold": int(inst["gold"]), "p_sent": ps, "pv": pv, "n_cand": len(pv)})
    return qs


def cue_values(q, kernel):
    pv, ps = q["pv"], q["p_sent"]
    maxlag = len(kernel) - 1
    cands = sorted(pv.keys())

    def kern(dt):
        return kernel[dt] if 0 <= dt <= maxlag else 0.0

    rec, base, subjrec, freq, firstm = [], [], [], [], []
    intro = {c: min(s for s, _ in pv[c]) for c in cands}
    earliest = min(intro.values())
    any_subject = any(any(r == "SUBJECT" for _, r in pv[c]) for c in cands)
    for c in cands:
        dts = [ps - s for s, _ in pv[c]]
        rec.append(kern(min(dts)))
        base.append(sum(kern(d) for d in dts))
        subj_dts = [ps - s for s, r in pv[c] if r == "SUBJECT"]
        subjrec.append((kern(min(subj_dts)) if subj_dts else 0.0) if any_subject else kern(min(dts)))
        freq.append(np.log1p(len(pv[c])))
        firstm.append(1.0 if intro[c] == earliest else 0.0)
    return cands, {"RECENCY": np.array(rec), "BASE": np.array(base), "SUBJREC": np.array(subjrec),
                   "FREQ": np.array(freq), "FIRST": np.array(firstm)}


def _softmax_z(v):
    v = np.asarray(v, float)
    if len(v) == 1:
        return np.array([1.0])
    sd = v.std()
    z = (v - v.mean()) / sd if sd > 1e-12 else np.zeros_like(v)
    e = np.exp(z - z.max())
    return e / e.sum()


def precompute(qs, kernel):
    pre = []
    for q in qs:
        cands, vals = cue_values(q, kernel)
        gi = cands.index(q["gold"]) if q["gold"] in cands else -1
        P = {cue: _softmax_z(vals[cue]) for cue in CUES}
        pre.append({"gold_idx": gi, "P": P, "n_cand": len(cands), "vals": vals})
    return pre


def cue_argmax_acc(pre, cue):
    return float(np.mean([int(np.argmax(p["vals"][cue]) == p["gold_idx"]) for p in pre])) if pre else float("nan")


def combine_idx(p, w):
    score = np.zeros(p["n_cand"])
    for cue in CUES:
        score = score + w[cue] * p["P"][cue]
    return int(np.argmax(score))


def combiner_acc(pre, w):
    return float(np.mean([int(combine_idx(p, w) == p["gold_idx"]) for p in pre])) if pre else float("nan")


def learn_coord_ascent(pre):
    grid = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    w = {c: (1.0 if c in ("RECENCY", "SUBJREC") else 0.0) for c in CUES}
    best = combiner_acc(pre, w)
    for _ in range(4):
        improved = False
        for cue in CUES:
            for val in grid:
                cand = dict(w); cand[cue] = val
                a = combiner_acc(pre, cand)
                if a > best + 1e-9:
                    best, w, improved = a, cand, True
        if not improved:
            break
    return w, best


def correct_vec(pre, fn):
    return np.array([int(fn(p) == p["gold_idx"]) for p in pre], float)


def paired_delta(a, b, gen, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); diff = a - b; n = len(diff)
    if n == 0:
        return {"delta": float("nan"), "band": "NA", "n": 0}
    idx = gen.integers(0, n, size=(n_boot, n)); boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    p95 = float(np.percentile(np.abs((diff[None, :] * signs).mean(axis=1)), 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0,
            "null_p95": p95, "band": band, "n": n}


def eval_split(insts, kernel, salt, gen, n_boot=2000, want_twins=False):
    test_docs = split_docs(insts, salt=salt)
    tr = [i for i in insts if i["doc"] not in test_docs]
    te = [i for i in insts if i["doc"] in test_docs]
    pre_tr = precompute(build_queries(tr), kernel)
    pre_te = precompute(build_queries(te), kernel)
    w, tr_acc = learn_coord_ascent(pre_tr)
    acc = {"FREQUENCY": cue_argmax_acc(pre_te, "FREQ"), "RECENCY": cue_argmax_acc(pre_te, "RECENCY"),
           "SUBJ_REC_FALLBACK": cue_argmax_acc(pre_te, "SUBJREC"), "COMBINER": combiner_acc(pre_te, w)}
    strongest = max(("FREQUENCY", "RECENCY", "SUBJ_REC_FALLBACK"), key=lambda k: acc[k])
    out = {"salt": salt, "n_test_q": len(pre_te), "n_test_docs": len(test_docs), "w": w,
           "train_acc": tr_acc, "acc": acc, "strongest": strongest,
           "d_content": acc["COMBINER"] - acc["FREQUENCY"],
           "d_recency": acc["COMBINER"] - acc["RECENCY"],
           "d_strongest": acc["COMBINER"] - acc[strongest]}
    if want_twins:
        cv = correct_vec(pre_te, lambda p: combine_idx(p, w))
        fmap = {"FREQ": "FREQUENCY", "RECENCY": "RECENCY", "SUBJREC": "SUBJ_REC_FALLBACK"}
        out["deltas"] = {fmap[c]: paired_delta(cv, correct_vec(pre_te, lambda p, c=c: int(np.argmax(p["vals"][c]))),
                                               gen, n_boot) for c in fmap}
        tw_ctx = precompute(build_queries(te, shuffle_ctx=True, seed=101), kernel)
        tw_role = precompute(build_queries(te, shuffle_role=True, seed=202), kernel)
        out["twins"] = {"combiner": acc["COMBINER"], "shuffle_ctx": combiner_acc(tw_ctx, w),
                        "shuffle_role": combiner_acc(tw_role, w)}
        out["twins"]["ctx_loses"] = bool(out["twins"]["shuffle_ctx"] < acc["COMBINER"])
        out["twins"]["role_loses"] = bool(out["twins"]["shuffle_role"] < acc["COMBINER"])
        # strata
        strata = {}
        for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 999, "5+")]:
            sub = [p for p in pre_te if lo <= p["n_cand"] <= hi]
            if sub:
                strata[lbl] = {"n": len(sub), "combiner": combiner_acc(sub, w),
                               "subjrec": cue_argmax_acc(sub, "SUBJREC"), "freq": cue_argmax_acc(sub, "FREQ")}
        out["strata"] = strata
    return out


def run(n_boot=2000):
    t0 = time.perf_counter()
    insts = load_instances()
    gen = np.random.default_rng(20260830)
    kernel = tcm_kernel_table(400, min_period=2.0, max_mult=2.0)

    primary = eval_split(insts, kernel, salt="", gen=gen, n_boot=n_boot, want_twins=True)
    salts = ["s1", "s2", "s3", "s4", "s5"]
    robust = [eval_split(insts, kernel, salt=s, gen=gen, n_boot=0) for s in salts]
    all_runs = [primary] + robust

    dc = np.array([r["d_content"] for r in all_runs]); dsg = np.array([r["d_strongest"] for r in all_runs])
    dr = np.array([r["d_recency"] for r in all_runs])
    combv = np.array([r["acc"]["COMBINER"] for r in all_runs])
    n_beats_content_010 = int(np.sum(dc >= 0.10)); n_beats_strong = int(np.sum(dsg > 0)); n_beats_rec = int(np.sum(dr > 0))

    pd = primary["deltas"]; tw = primary["twins"]
    literal_pass = (pd["FREQUENCY"]["band"] == "ABOVE" and pd["FREQUENCY"]["delta"] >= 0.10 and
                    pd["RECENCY"]["band"] == "ABOVE" and tw["ctx_loses"])
    strong_pass = pd[primary["strongest"]]["band"] == "ABOVE"

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "kernel": {"min_period": 2.0, "max_mult": 2.0}, "primary": primary,
           "robust_runs": robust,
           "robustness": {"n_splits": len(all_runs), "combiner_mean": float(combv.mean()), "combiner_std": float(combv.std()),
                          "d_content_mean": float(dc.mean()), "d_content_std": float(dc.std()),
                          "d_recency_mean": float(dr.mean()), "d_recency_std": float(dr.std()),
                          "d_strongest_mean": float(dsg.mean()), "d_strongest_std": float(dsg.std()),
                          "splits_beating_content_by_010": n_beats_content_010,
                          "splits_beating_recency": n_beats_rec, "splits_beating_strongest": n_beats_strong},
           "LITERAL_BAR_PASS": bool(literal_pass), "STRONGEST_FLOOR_PASS": bool(strong_pass)}

    _log("PRIMARY split: n_test=%d docs=%d  FREQ=%.3f RECENCY=%.3f SUBJ_REC=%.3f || COMBINER=%.3f"
         % (primary["n_test_q"], primary["n_test_docs"], primary["acc"]["FREQUENCY"], primary["acc"]["RECENCY"],
            primary["acc"]["SUBJ_REC_FALLBACK"], primary["acc"]["COMBINER"]))
    _log("  weights=%s (train=%.3f)" % ({k: round(v, 2) for k, v in primary["w"].items()}, primary["train_acc"]))
    for k in ("FREQUENCY", "RECENCY", "SUBJ_REC_FALLBACK"):
        d = pd[k]
        _log("  COMBINER - %-17s = %+.3f [%.3f,%.3f] %s (hw=%.3f null_p95=%.3f)"
             % (k, d["delta"], d["lo"], d["hi"], d["band"], d["half_width"], d["null_p95"]))
    _log("  TWINS: shuffle-ctx=%.3f(loses=%s) shuffle-role=%.3f(loses=%s)"
         % (tw["shuffle_ctx"], tw["ctx_loses"], tw["shuffle_role"], tw["role_loses"]))
    for lbl, sv in primary["strata"].items():
        _log("  competitors=%s n=%d combiner=%.3f subjrec=%.3f freq=%.3f"
             % (lbl, sv["n"], sv["combiner"], sv["subjrec"], sv["freq"]))
    rb = res["robustness"]
    _log("ROBUSTNESS across %d splits: combiner=%.3f+/-%.3f | d_content=%.3f+/-%.3f | d_recency=%.3f+/-%.3f | d_strongest=%.3f+/-%.3f"
         % (rb["n_splits"], rb["combiner_mean"], rb["combiner_std"], rb["d_content_mean"], rb["d_content_std"],
            rb["d_recency_mean"], rb["d_recency_std"], rb["d_strongest_mean"], rb["d_strongest_std"]))
    _log("  splits beating content-by-0.10: %d/%d | beating recency: %d/%d | beating strongest(subj-rec): %d/%d"
         % (rb["splits_beating_content_by_010"], rb["n_splits"], rb["splits_beating_recency"], rb["n_splits"],
            rb["splits_beating_strongest"], rb["n_splits"]))
    _log("LITERAL_BAR_PASS=%s  STRONGEST_FLOOR_PASS=%s (%.1fs)" % (literal_pass, strong_pass, res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: kernel decay; SUBJREC fallback; combiner runs; twin leak-free")
    ker = tcm_kernel_table(50)
    assert abs(ker[0] - 1.0) < 1e-9 and ker[5] < ker[1] and (ker >= 0).all()
    q = {"gold": 1, "p_sent": 10, "n_cand": 2, "pv": {1: [(3, "SUBJECT")], 2: [(9, "OTHER")]}}
    c, v = cue_values(q, ker)
    assert np.argmax(v["SUBJREC"]) == c.index(1) and np.argmax(v["RECENCY"]) == c.index(2)
    pre = precompute([q], ker)
    w = {cc: 1.0 for cc in CUES}
    assert 0 <= combine_idx(pre[0], w) < 2
    insts = load_instances()
    tw = build_queries(insts[:200], shuffle_ctx=True, seed=1)
    for x in tw[:50]:
        assert all(s < x["p_sent"] for pm in x["pv"].values() for s, _ in pm)
    _log("SELF-TEST PASS")
    return {"kernel0": float(ker[0])}


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
