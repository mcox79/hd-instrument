"""exp_similar_competitor_actr_tcm_combiner_v2 -- THE BUILD (v2, cue-combination form) for
retrieval_interference_is_similar_competitor_cue_overload_not_event_count.

WHY v2. v1 used a single fused base-level sum  A_i = ln sum_m kernel(dt)*g(role). On held-out pronoun data it
scored 0.562 -- BELOW naive recency (0.609) and subject-recency (0.620). Diagnosed cause (not a ceiling, a
mis-specified mechanism): the single sum ACCUMULATES FREQUENCY, so a heavily-mentioned protagonist wins even when
the true antecedent is a recent LOCAL mention -- but the diagnostic proved recency (0.642) >> frequency (0.570)
for pronouns. v1 weighted the wrong cue.

v2 is FAITHFUL TO THE FULL ACT-R ACTIVATION EQUATION, which is a weighted sum of SEPARATE cues, not one conflated
base-level:
      A_i = B_i + sum_j W_j S_ji            (Lewis & Vasishth 2005; Anderson ACT-R)
The cues here are the PINNED accessibility cues for anaphora (Arnold 2010; Competition Model, MacWhinney & Bates):
      RECENCY   f_rec(i)  = kernel_TCM(nearest prior mention)          -- temporal-context reinstatement (organ)
      BASE      f_base(i) = sum_m kernel_TCM(dt_m)                      -- multi-timescale base level (recency+freq)
      SUBJ      f_subj(i) = sum_m kernel_TCM(dt_m)*[role==SUBJECT]      -- grammatical salience / topicality
      FREQ      f_freq(i) = log(1 + n_prior_mentions)                   -- raw frequency / repetition
      FIRST     f_first(i)= 1 if earliest-introduced candidate else 0   -- primacy / protagonist (topic)
Each cue is turned into a within-query preference p_cue(i) = softmax over candidates of the z-scored cue value, and
combined with LEARNED weights:
      score_i = sum_cue  w_cue * p_cue(i);   predicted antecedent = argmax_i score_i
Weights are LEARNED on a TRAIN doc split. Two learners, both reported:
  (A) CUE-VALIDITY (Competition Model, overfit-proof, NO search): w_cue = train hit@1 of that cue used alone.
  (B) COORDINATE-ASCENT on train hit@1 (a reference upper bound; more prone to overfit).
The kernel timescale (organ min_period/max_mult) is OUR-INVENTION-UNDER-TEST -> swept on train.

kernel_TCM is CONSUMED from hdlab.graded_temporal_context (the built TCM organ), not rebuilt.

FLOORS (recomputed on the SAME held-out population): FREQUENCY (content-only floor -- the brief's named floor),
RECENCY (naive recency -- the documented tie), SUBJECT_REC (the STRONGEST single cue -- must beat this too).
INFO-FREE TWINS (must LOSE): SHUFFLE_CTX (permute mention sentences -> kills temporal context -> recency/base
collapse), SHUFFLE_ROLE (permute role labels -> kills the salience cue).
GENERALIZATION: weights learned on TRAIN docs; all headline numbers on HELD-OUT TEST docs; reported across strata.

NO external LLM. Consumes the TCM organ (torch). Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_actr_tcm_combiner_v2.py --self-test
     ...                                                                               --full
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

ANCHOR = "similar_competitor_actr_tcm_combiner_v2"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON_PATH = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")

CUES = ("RECENCY", "BASE", "SUBJ", "FREQ", "FIRST")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def tcm_kernel_table(max_lag, min_period=2.0, max_mult=4.0, horizon=1000.0, d=1024):
    """kernel_TCM[dt] from the built hdlab.graded_temporal_context organ (CONSUMED, not rebuilt)."""
    import torch
    from hdlab.graded_temporal_context import GradedTemporalContext
    g = GradedTemporalContext(d=d, min_period=min_period, max_period_mult=max_mult, horizon=horizon)
    c0 = g.ctx(0.0)
    tab = np.empty(max_lag + 1, dtype=np.float64)
    for L in range(max_lag + 1):
        tab[L] = float((torch.conj(c0) * g.ctx(float(L))).real.mean())
    return np.clip(tab, 0.0, None)  # base-level weights are non-negative


def load_instances():
    return json.load(open(PRON_PATH, encoding="utf-8"))


def split_docs(insts, test_frac=0.4):
    test = set()
    for dnm in sorted(set(i["doc"] for i in insts)):
        if (int(hashlib.md5(dnm.encode()).hexdigest(), 16) % 1000) / 1000.0 < test_frac:
            test.add(dnm)
    return test


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
        qs.append({"gold": int(inst["gold"]), "p_sent": ps, "pv": pv,
                   "n_cand": len(pv), "gold_prior": int(inst["gold"]) in pv, "doc": inst["doc"]})
    return qs


def cue_features(q, kernel):
    """Return (cand_ids, {cue: np.array over cands}) of raw cue values (higher = more accessible)."""
    pv, ps = q["pv"], q["p_sent"]
    maxlag = len(kernel) - 1
    cands = sorted(pv.keys())

    def kern(dt):
        return kernel[dt] if dt <= maxlag else 0.0

    rec, base, subj, freq, firstm = [], [], [], [], []
    intro = {c: min(s for s, _ in pv[c]) for c in cands}
    earliest = min(intro.values())
    for c in cands:
        dts = [ps - s for s, _ in pv[c]]
        rec.append(kern(min(dts)))                                             # nearest mention
        base.append(sum(kern(d) for d in dts))                                 # multi-timescale base level
        subj.append(sum(kern(ps - s) for s, r in pv[c] if r == "SUBJECT"))     # subject-weighted recency
        freq.append(np.log1p(len(pv[c])))                                       # raw frequency
        firstm.append(1.0 if intro[c] == earliest else 0.0)                    # primacy / protagonist
    feats = {"RECENCY": np.array(rec), "BASE": np.array(base), "SUBJ": np.array(subj),
             "FREQ": np.array(freq), "FIRST": np.array(firstm)}
    return cands, feats


def _softmax_z(v):
    """z-score within the candidate set, then softmax -> a within-query preference distribution."""
    v = np.asarray(v, dtype=np.float64)
    if len(v) == 1:
        return np.array([1.0])
    sd = v.std()
    z = (v - v.mean()) / sd if sd > 1e-12 else np.zeros_like(v)
    e = np.exp(z - z.max())
    return e / e.sum()


def precompute(qs, kernel):
    """Per query: cand list, gold index, and p_cue(i) for each cue (within-query softmax of z-scored feature)."""
    pre = []
    for q in qs:
        cands, feats = cue_features(q, kernel)
        gi = cands.index(q["gold"]) if q["gold"] in cands else -1
        P = {cue: _softmax_z(feats[cue]) for cue in CUES}
        pre.append({"cands": cands, "gold_idx": gi, "P": P, "n_cand": len(cands),
                    "gold_prior": q["gold_prior"]})
    return pre


def cue_alone_acc(pre, cue):
    if not pre:
        return float("nan")
    return float(np.mean([int(np.argmax(p["P"][cue]) == p["gold_idx"]) for p in pre]))


def combine_pred_idx(p, w):
    score = np.zeros(p["n_cand"])
    for cue in CUES:
        score = score + w[cue] * p["P"][cue]
    return int(np.argmax(score))


def combiner_acc(pre, w, mask=None):
    rows = pre if mask is None else [p for p, m in zip(pre, mask) if m]
    if not rows:
        return float("nan")
    return float(np.mean([int(combine_pred_idx(p, w) == p["gold_idx"]) for p in rows]))


def learn_cue_validity(pre):
    """Competition Model: weight each cue by its stand-alone train accuracy (cue validity). Overfit-proof."""
    return {cue: cue_alone_acc(pre, cue) for cue in CUES}


def learn_coord_ascent(pre, init):
    grid = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    w = dict(init)
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


def floor_acc(pre, cue):
    return cue_alone_acc(pre, cue)


def paired_delta(pre_a_correct, pre_b_correct, gen, n_boot=2000):
    a = np.asarray(pre_a_correct, float); b = np.asarray(pre_b_correct, float)
    diff = a - b; n = len(diff)
    if n == 0:
        return {"delta": float("nan"), "band": "NA", "n": 0}
    idx = gen.integers(0, n, size=(n_boot, n))
    boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    signs = gen.choice([-1.0, 1.0], size=(n_boot, n))
    null = np.abs((diff[None, :] * signs).mean(axis=1))
    p95 = float(np.percentile(null, 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0,
            "null_p95": p95, "band": band, "n": n}


def correct_vec(pre, predfn):
    return np.array([int(predfn(p) == p["gold_idx"]) for p in pre], float)


def run(n_boot=2000, test_frac=0.4):
    t0 = time.perf_counter()
    insts = load_instances()
    test_docs = split_docs(insts, test_frac)
    train_insts = [i for i in insts if i["doc"] not in test_docs]
    test_insts = [i for i in insts if i["doc"] in test_docs]
    gen = np.random.default_rng(20260830)

    # sweep kernel timescale on TRAIN; learn cue-validity weights; keep the best-train config
    best = None
    for (mp, mm) in [(2.0, 4.0), (2.0, 8.0), (3.0, 4.0), (2.0, 2.0), (4.0, 4.0)]:
        ker = tcm_kernel_table(400, min_period=mp, max_mult=mm)
        pre_tr = precompute(build_queries(train_insts), ker)
        wv = learn_cue_validity(pre_tr)
        acc_v = combiner_acc(pre_tr, wv)
        if best is None or acc_v > best[0]:
            best = (acc_v, mp, mm, ker)
    _, mp, mm, kernel = best
    pre_tr = precompute(build_queries(train_insts), kernel)
    w_valid = learn_cue_validity(pre_tr)
    w_coord, tr_coord = learn_coord_ascent(pre_tr, w_valid)
    tr_valid = combiner_acc(pre_tr, w_valid)
    _log("LEARNED kernel(min_period=%.1f,max_mult=%.1f)" % (mp, mm))
    _log("  cue-validity w=%s -> train=%.3f" % ({k: round(v, 3) for k, v in w_valid.items()}, tr_valid))
    _log("  coord-ascent w=%s -> train=%.3f" % ({k: round(v, 2) for k, v in w_coord.items()}, tr_coord))

    pre_te = precompute(build_queries(test_insts), kernel)

    def report(pre, w, label):
        accs = {cue: floor_acc(pre, cue) for cue in ("FREQ", "RECENCY", "SUBJ")}
        comb = combiner_acc(pre, w)
        cv = correct_vec(pre, lambda p: combine_pred_idx(p, w))
        floors = {
            "FREQUENCY": (accs["FREQ"], correct_vec(pre, lambda p: int(np.argmax(p["P"]["FREQ"])))),
            "RECENCY": (accs["RECENCY"], correct_vec(pre, lambda p: int(np.argmax(p["P"]["RECENCY"])))),
            "SUBJECT_REC": (accs["SUBJ"], correct_vec(pre, lambda p: int(np.argmax(p["P"]["SUBJ"])))),
        }
        strongest = max(floors, key=lambda k: floors[k][0])
        deltas = {k: paired_delta(cv, fv, gen, n_boot) for k, (fa, fv) in floors.items()}
        deltas["STRONGEST=%s" % strongest] = deltas[strongest]
        return {"label": label, "n": len(pre), "combiner": comb,
                "floors": {k: v[0] for k, v in floors.items()}, "strongest": strongest, "deltas": deltas}

    rep_valid = report(pre_te, w_valid, "TEST cue-validity")
    rep_coord = report(pre_te, w_coord, "TEST coord-ascent")

    # info-free twins (same learned validity weights)
    pre_tw_ctx = precompute(build_queries(test_insts, shuffle_ctx=True, seed=101), kernel)
    pre_tw_role = precompute(build_queries(test_insts, shuffle_role=True, seed=202), kernel)
    twins = {"combiner_test": rep_valid["combiner"],
             "shuffle_ctx": combiner_acc(pre_tw_ctx, w_valid),
             "shuffle_role": combiner_acc(pre_tw_role, w_valid)}
    twins["ctx_loses"] = bool(twins["shuffle_ctx"] < twins["combiner_test"])
    twins["role_loses"] = bool(twins["shuffle_role"] < twins["combiner_test"])

    # strata on TEST (cue-validity combiner)
    strata = {}
    for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 999, "5+")]:
        sub = [p for p in pre_te if lo <= p["n_cand"] <= hi]
        if sub:
            strata[lbl] = {"n": len(sub), "combiner": combiner_acc(sub, w_valid),
                           "subj": cue_alone_acc(sub, "SUBJ"), "rec": cue_alone_acc(sub, "RECENCY"),
                           "freq": cue_alone_acc(sub, "FREQ")}

    def verdict_of(rep):
        df = rep["deltas"]["FREQUENCY"]; dr = rep["deltas"]["RECENCY"]; ds = rep["deltas"][rep["strongest"]]
        return "PASS" if (df["band"] == "ABOVE" and df["delta"] >= 0.10 and dr["band"] == "ABOVE"
                          and ds["band"] == "ABOVE" and twins["ctx_loses"]) else "PARTIAL_OR_FAIL"
    v_valid = verdict_of(rep_valid); v_coord = verdict_of(rep_coord)

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_train_docs": len(set(i["doc"] for i in train_insts)), "n_test_docs": len(test_docs),
           "n_train_q": len(pre_tr), "n_test_q": len(pre_te),
           "kernel": {"min_period": mp, "max_mult": mm}, "w_valid": w_valid, "w_coord": w_coord,
           "TEST_cue_validity": rep_valid, "TEST_coord_ascent": rep_coord,
           "twins": twins, "strata": strata,
           "VERDICT_cue_validity": v_valid, "VERDICT_coord_ascent": v_coord}

    for rep, vv in ((rep_valid, v_valid), (rep_coord, v_coord)):
        _log("=== %s (held-out n=%d) ===" % (rep["label"], rep["n"]))
        _log("  FREQ=%.3f RECENCY=%.3f SUBJECT_REC=%.3f || COMBINER=%.3f"
             % (rep["floors"]["FREQUENCY"], rep["floors"]["RECENCY"], rep["floors"]["SUBJECT_REC"], rep["combiner"]))
        for k in ("FREQUENCY", "RECENCY", rep["strongest"]):
            d = rep["deltas"][k]
            _log("  COMBINER - %-12s = %+.3f [%.3f,%.3f] %s" % (k, d["delta"], d["lo"], d["hi"], d["band"]))
        _log("  VERDICT=%s" % vv)
    _log("TWINS: shuffle-ctx=%.3f (loses=%s)  shuffle-role=%.3f (loses=%s)  vs combiner=%.3f"
         % (twins["shuffle_ctx"], twins["ctx_loses"], twins["shuffle_role"], twins["role_loses"], twins["combiner_test"]))
    for lbl, sv in strata.items():
        _log("  competitors=%s n=%d combiner=%.3f subj=%.3f rec=%.3f freq=%.3f"
             % (lbl, sv["n"], sv["combiner"], sv["subj"], sv["rec"], sv["freq"]))
    return res


def self_test():
    _log("SELF-TEST: kernel decays; cues computed from organ; recency and frequency dissociate; twins leak-free")
    ker = tcm_kernel_table(50)
    assert abs(ker[0] - 1.0) < 1e-9 and ker[5] < ker[1] and (ker >= 0).all()
    q = {"gold": 2, "p_sent": 10, "n_cand": 2, "gold_prior": True,
         "pv": {1: [(0, "OTHER"), (1, "OTHER")], 2: [(9, "SUBJECT")]}}
    cands, feats = cue_features(q, ker)
    i2 = cands.index(2)
    assert np.argmax(feats["RECENCY"]) == i2, "recency should favour the recent entity 2"
    assert np.argmax(feats["FREQ"]) == cands.index(1), "frequency should favour the twice-mentioned entity 1"
    assert np.argmax(feats["SUBJ"]) == i2, "subject cue should favour the subject mention (entity 2)"
    # a validity-weighted combiner that trusts recency+subj should pick entity 2
    w = {"RECENCY": 0.6, "BASE": 0.5, "SUBJ": 0.6, "FREQ": 0.5, "FIRST": 0.1}
    p = precompute([q], ker)[0]
    assert p["cands"][combine_pred_idx(p, w)] == 2
    insts = load_instances()
    tw = build_queries(insts[:200], shuffle_ctx=True, seed=1)
    for x in tw[:50]:
        assert all(s < x["p_sent"] for pm in x["pv"].values() for s, _ in pm), "twin leaked a mention >= p_sent"
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
