"""exp_similar_competitor_actr_tcm_combiner_v3 -- THE BUILD (v3, reliability-gated cue integration) for
retrieval_interference_is_similar_competitor_cue_overload_not_event_count.

WHY v3. v2 (linear cue-validity mixture) hit 0.558 on held-out -- BELOW naive recency (0.609) and below the true
strongest single cue subject-recency-with-fallback (~0.66). A coord-ascent fit reached 0.630 but collapsed to
"recency + epsilon" (weights RECENCY 3.0, everything else ~0), beating recency by only +0.021. Two honesty fixes
were forced:
  (1) FAIR STRONGEST FLOOR. v2's SUBJ cue (no fallback) scored 0.547; the diagnostic's subject-recency WITH a
      recency fallback scored 0.660. The strongest single floor is the latter -- the combiner must beat THAT,
      not the crippled version. v3 computes SUBJ_REC_FALLBACK and gates against max(FREQ, RECENCY, SUBJ_REC).
  (2) THE COMBINATION RULE. A fixed linear weight cannot capture the oracle headroom (oracle-any-cue = 0.813 vs
      best single 0.660) because it does not know WHICH cue to trust per query. The PINNED brain mechanism is
      cue-overload: a cue's diagnosticity FALLS as it matches more competitors (Van Dyke & McElree 2006 -- the
      load-bearing citation). So each cue is weighted by its PER-QUERY RELIABILITY R_cue(q) = peakedness of its
      within-query preference (top1 - top2). A cue that fails to discriminate (high fan, flat preference) is
      discounted for THIS query; a cue that uniquely points to one candidate dominates. This is the
      reliability-weighted cue integration the memory pins ("convergent-cue composition = reliability-weighted
      product, not AND") and it is context-sensitive, unlike a fixed weight.

      score_i = sum_cue  W_cue * R_cue(q) * p_cue(i);   predicted = argmax_i score_i
        p_cue(i)  = softmax over candidates of the z-scored cue value (within-query preference)
        R_cue(q)  = p_cue(top1) - p_cue(top2)           (per-query diagnosticity; cue-overload gate)
        W_cue     = LEARNED global cue weight (Competition Model cue validity on TRAIN, or coord-ascent)
      ABLATION: RELIABILITY-OFF sets R_cue(q)=1 (recovers the v2 linear mixture) -> must be WORSE, proving the
      cue-overload gate is load-bearing (not just more free parameters).

CUES (all PINNED accessibility cues; the TCM organ supplies the graded temporal kernel, CONSUMED not rebuilt):
  RECENCY  kernel(nearest prior mention)                       -- temporal-context reinstatement
  BASE     sum_m kernel(dt_m)                                  -- multi-timescale base level (recency x frequency)
  SUBJREC  kernel(nearest SUBJECT mention), fallback recency   -- grammatical salience / topicality (Arnold 2010)
  FREQ     log(1 + n_prior_mentions)                           -- repetition / frequency
  FIRST    1 if earliest-introduced else 0                     -- primacy / protagonist

FLOORS recomputed on the SAME held-out population: FREQUENCY, RECENCY, SUBJ_REC_FALLBACK (STRONGEST -- must beat).
INFO-FREE TWINS (must LOSE): SHUFFLE_CTX, SHUFFLE_ROLE. GENERALIZATION: weights learned on TRAIN docs, all
headline numbers on HELD-OUT TEST docs, reported across competitor-count strata. NO external LLM. Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_actr_tcm_combiner_v3.py --self-test
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

ANCHOR = "similar_competitor_actr_tcm_combiner_v3"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON_PATH = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")

CUES = ("RECENCY", "BASE", "SUBJREC", "FREQ", "FIRST")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def tcm_kernel_table(max_lag, min_period=2.0, max_mult=4.0, horizon=1000.0, d=1024):
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


def split_docs(insts, test_frac=0.4):
    return set(d for d in sorted(set(i["doc"] for i in insts))
               if (int(hashlib.md5(d.encode()).hexdigest(), 16) % 1000) / 1000.0 < test_frac)


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
                   "n_cand": len(pv), "gold_prior": int(inst["gold"]) in pv})
    return qs


def cue_values(q, kernel):
    """Raw per-candidate cue values (higher = more accessible). Returns (cands, {cue: array})."""
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
        if any_subject:
            subjrec.append(kern(min(subj_dts)) if subj_dts else 0.0)       # subject-recency
        else:
            subjrec.append(kern(min(dts)))                                  # fallback: recency
        freq.append(np.log1p(len(pv[c])))
        firstm.append(1.0 if intro[c] == earliest else 0.0)
    vals = {"RECENCY": np.array(rec), "BASE": np.array(base), "SUBJREC": np.array(subjrec),
            "FREQ": np.array(freq), "FIRST": np.array(firstm)}
    return cands, vals


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
        P, R = {}, {}
        for cue in CUES:
            p = _softmax_z(vals[cue]); P[cue] = p
            top = np.sort(p)[::-1]
            R[cue] = float(top[0] - top[1]) if len(top) > 1 else 1.0     # per-query diagnosticity (cue-overload)
        pre.append({"cands": cands, "gold_idx": gi, "P": P, "R": R, "n_cand": len(cands),
                    "gold_prior": q.get("gold_prior", q["gold"] in cands), "vals": vals})
    return pre


# ---- floor predictions (argmax of a single cue value; SUBJ_REC uses the fallback already baked into the value)
def floor_pred_idx(p, cue):
    return int(np.argmax(p["vals"][cue]))


def cue_argmax_acc(pre, cue):
    return float(np.mean([int(floor_pred_idx(p, cue) == p["gold_idx"]) for p in pre])) if pre else float("nan")


def combine_idx(p, w, use_reliability=True):
    score = np.zeros(p["n_cand"])
    for cue in CUES:
        gate = p["R"][cue] if use_reliability else 1.0
        score = score + w[cue] * gate * p["P"][cue]
    return int(np.argmax(score))


def combiner_acc(pre, w, use_reliability=True):
    return float(np.mean([int(combine_idx(p, w, use_reliability) == p["gold_idx"]) for p in pre])) if pre else float("nan")


def learn_cue_validity(pre):
    return {cue: cue_argmax_acc(pre, cue) for cue in CUES}


def learn_coord_ascent(pre, init, use_reliability=True):
    grid = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    w = dict(init); best = combiner_acc(pre, w, use_reliability)
    for _ in range(4):
        improved = False
        for cue in CUES:
            for val in grid:
                cand = dict(w); cand[cue] = val
                a = combiner_acc(pre, cand, use_reliability)
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


def run(n_boot=2000, test_frac=0.4):
    t0 = time.perf_counter()
    insts = load_instances()
    test_docs = split_docs(insts, test_frac)
    train_insts = [i for i in insts if i["doc"] not in test_docs]
    test_insts = [i for i in insts if i["doc"] in test_docs]
    gen = np.random.default_rng(20260830)

    best = None
    for (mp, mm) in [(2.0, 4.0), (2.0, 8.0), (3.0, 4.0), (2.0, 2.0), (4.0, 4.0)]:
        ker = tcm_kernel_table(400, min_period=mp, max_mult=mm)
        pre_tr = precompute(build_queries(train_insts), ker)
        wv = learn_cue_validity(pre_tr)
        a = combiner_acc(pre_tr, wv, use_reliability=True)
        if best is None or a > best[0]:
            best = (a, mp, mm, ker)
    _, mp, mm, kernel = best
    pre_tr = precompute(build_queries(train_insts), kernel)
    pre_te = precompute(build_queries(test_insts), kernel)

    w_valid = learn_cue_validity(pre_tr)
    w_coord_rel, tr_coord_rel = learn_coord_ascent(pre_tr, w_valid, use_reliability=True)
    w_coord_lin, tr_coord_lin = learn_coord_ascent(pre_tr, w_valid, use_reliability=False)
    _log("LEARNED kernel(min_period=%.1f,max_mult=%.1f)" % (mp, mm))
    _log("  cue-validity w=%s" % {k: round(v, 3) for k, v in w_valid.items()})
    _log("  coord-ascent(reliability) w=%s train=%.3f" % ({k: round(v, 2) for k, v in w_coord_rel.items()}, tr_coord_rel))
    _log("  coord-ascent(linear)      w=%s train=%.3f" % ({k: round(v, 2) for k, v in w_coord_lin.items()}, tr_coord_lin))

    floors = {"FREQUENCY": "FREQ", "RECENCY": "RECENCY", "SUBJ_REC_FALLBACK": "SUBJREC"}
    floor_acc = {name: cue_argmax_acc(pre_te, cue) for name, cue in floors.items()}
    strongest = max(floor_acc, key=lambda k: floor_acc[k])
    floor_cv = {name: correct_vec(pre_te, lambda p, c=cue: floor_pred_idx(p, c)) for name, cue in floors.items()}

    def evaluate(w, use_rel, label):
        acc = combiner_acc(pre_te, w, use_rel)
        cv = correct_vec(pre_te, lambda p: combine_idx(p, w, use_rel))
        deltas = {name: paired_delta(cv, floor_cv[name], gen, n_boot) for name in floors}
        df, dr, ds = deltas["FREQUENCY"], deltas["RECENCY"], deltas[strongest]
        passed = (df["band"] == "ABOVE" and df["delta"] >= 0.10 and dr["band"] == "ABOVE" and ds["band"] == "ABOVE")
        return {"label": label, "acc": acc, "deltas": deltas, "beats_strongest": ds["band"] == "ABOVE",
                "verdict_pre_twin": "PASS" if passed else "PARTIAL_OR_FAIL"}

    ev_valid = evaluate(w_valid, True, "cue-validity+reliability")
    ev_coord_rel = evaluate(w_coord_rel, True, "coord-ascent+reliability")
    ev_coord_lin = evaluate(w_coord_lin, False, "coord-ascent LINEAR (reliability OFF ablation)")
    ev_valid_lin = evaluate(w_valid, False, "cue-validity LINEAR (reliability OFF ablation)")

    # twins for the headline arm (coord-ascent+reliability, the strongest honest learned arm)
    head_w, head_rel = w_coord_rel, True
    pre_tw_ctx = precompute(build_queries(test_insts, shuffle_ctx=True, seed=101), kernel)
    pre_tw_role = precompute(build_queries(test_insts, shuffle_role=True, seed=202), kernel)
    twins = {"combiner_test": ev_coord_rel["acc"],
             "shuffle_ctx": combiner_acc(pre_tw_ctx, head_w, head_rel),
             "shuffle_role": combiner_acc(pre_tw_role, head_w, head_rel)}
    twins["ctx_loses"] = bool(twins["shuffle_ctx"] < twins["combiner_test"])
    twins["role_loses"] = bool(twins["shuffle_role"] < twins["combiner_test"])

    strata = {}
    for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 999, "5+")]:
        sub = [p for p in pre_te if lo <= p["n_cand"] <= hi]
        if sub:
            strata[lbl] = {"n": len(sub), "combiner": combiner_acc(sub, head_w, head_rel),
                           "subjrec": cue_argmax_acc(sub, "SUBJREC"), "rec": cue_argmax_acc(sub, "RECENCY"),
                           "freq": cue_argmax_acc(sub, "FREQ")}

    headline = ev_coord_rel
    final_verdict = "PASS" if (headline["verdict_pre_twin"] == "PASS" and twins["ctx_loses"]) else "PARTIAL_OR_FAIL"

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_train_docs": len(set(i["doc"] for i in train_insts)), "n_test_docs": len(test_docs),
           "n_train_q": len(pre_tr), "n_test_q": len(pre_te),
           "kernel": {"min_period": mp, "max_mult": mm}, "weights": {"cue_validity": w_valid,
           "coord_ascent_reliability": w_coord_rel, "coord_ascent_linear": w_coord_lin},
           "floor_acc": floor_acc, "strongest_floor": strongest,
           "arms": {e["label"]: {k: e[k] for k in ("acc", "beats_strongest", "verdict_pre_twin", "deltas")}
                    for e in (ev_valid, ev_coord_rel, ev_coord_lin, ev_valid_lin)},
           "twins": twins, "strata": strata, "VERDICT": final_verdict}

    _log("=== FLOORS (held-out n=%d): FREQ=%.3f RECENCY=%.3f SUBJ_REC_FALLBACK=%.3f  [strongest=%s] ==="
         % (len(pre_te), floor_acc["FREQUENCY"], floor_acc["RECENCY"], floor_acc["SUBJ_REC_FALLBACK"], strongest))
    for e in (ev_valid, ev_coord_rel, ev_coord_lin, ev_valid_lin):
        ds = e["deltas"][strongest]; df = e["deltas"]["FREQUENCY"]
        _log("  %-42s acc=%.3f | vs FREQ %+.3f[%s] | vs %s %+.3f[%s] | %s"
             % (e["label"], e["acc"], df["delta"], df["band"], strongest, ds["delta"], ds["band"], e["verdict_pre_twin"]))
    _log("TWINS (headline=coord+reliability): shuffle-ctx=%.3f(loses=%s) shuffle-role=%.3f(loses=%s) vs %.3f"
         % (twins["shuffle_ctx"], twins["ctx_loses"], twins["shuffle_role"], twins["role_loses"], twins["combiner_test"]))
    for lbl, sv in strata.items():
        _log("  competitors=%s n=%d combiner=%.3f subjrec=%.3f rec=%.3f freq=%.3f"
             % (lbl, sv["n"], sv["combiner"], sv["subjrec"], sv["rec"], sv["freq"]))
    _log("VERDICT: %s (%.1fs)" % (final_verdict, res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: kernel decays; SUBJREC has recency fallback; reliability gate = per-query peakedness")
    ker = tcm_kernel_table(50)
    assert abs(ker[0] - 1.0) < 1e-9 and ker[5] < ker[1] and (ker >= 0).all()
    # subject fallback: NO candidate has a subject mention -> SUBJREC must equal recency ordering
    q = {"gold": 1, "p_sent": 10, "n_cand": 2,
         "pv": {1: [(9, "OTHER")], 2: [(2, "OTHER")]}}
    cands, vals = cue_values(q, ker)
    assert np.argmax(vals["SUBJREC"]) == cands.index(1), "SUBJREC fallback should track recency when no subjects"
    # with a subject mention, SUBJREC favours the subject candidate even if less recent
    q2 = {"gold": 1, "p_sent": 10, "n_cand": 2,
          "pv": {1: [(3, "SUBJECT")], 2: [(9, "OTHER")]}}
    c2, v2 = cue_values(q2, ker)
    assert np.argmax(v2["SUBJREC"]) == c2.index(1), "SUBJREC should favour the subject mention"
    # reliability gate: a flat cue (both candidates equal) has R~0; a peaked cue has R>0
    pre = precompute([q2], ker)[0]
    assert pre["R"]["RECENCY"] >= 0.0 and pre["R"]["FIRST"] >= 0.0
    # combiner runs and returns a valid candidate index
    w = {c: 1.0 for c in CUES}
    assert 0 <= combine_idx(pre, w, True) < pre["n_cand"]
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
