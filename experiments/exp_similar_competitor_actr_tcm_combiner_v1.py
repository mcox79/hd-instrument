"""exp_similar_competitor_actr_tcm_combiner_v1 -- THE BUILD for
retrieval_interference_is_similar_competitor_cue_overload_not_event_count.

BRAIN MECHANISM (PINNED, copy the computation). Pronoun / partial-cue resolution among similar competitors is
cue-based content-addressable retrieval from a memory of partially-active antecedents (Lewis & Vasishth 2005
activation-based ACT-R; Van Dyke & McElree 2006 cue-overload). A candidate antecedent i is retrieved by its
ACTIVATION:
      A_i = B_i + sum_j W_j S_ji            (ACT-R activation equation)
The BASE-LEVEL term B_i = ln sum_k t_k^{-d} FUSES recency and frequency of item i's mentions via power-law
decay -- this is EXACTLY the content x context "combination" the brief calls unbuilt: frequency = more mention
terms in the sum; recency = nearer mentions get a bigger t^{-d}. And the substrate's `graded_temporal_context`
organ (TCM; Howard & Kahana 2002; Shankar & Howard 2012 multi-timescale Laplace bank) is the NEURAL
IMPLEMENTATION of that power-law base level: its contiguity kernel kernel(dt) decays smoothly and heavy-tailed
with the discourse lag (measured on disk: 1.00, 0.78, 0.68, ... 0.12 at lag 144). So we CONSUME the organ's
kernel as the base-level recency weight and let grammatical role enter as per-trace ENCODING SALIENCE (subject
> object > other; Arnold 2010 accessibility; topicality). One brain-faithful equation:

      A_i = ln( sum_{prior mentions m of i}  kernel_TCM(p_sent - m_sent) * g(role_m) )
      predicted antecedent = argmax_i A_i

- kernel_TCM  : consumed from hdlab.graded_temporal_context.GradedTemporalContext (recency, multi-timescale). PINNED.
- g(role)     : per-trace encoding-salience weight (grammatical role). LEARNED on train (Competition Model cue
                weighting; MacWhinney & Bates -- weights are LEARNED, not hand-set). g(OTHER)=1 reference.
- the SUM over mentions  = frequency / base-level accumulation. PINNED (ACT-R base-level learning eq.).
- the kernel timescale (organ min_period/max_mult) = OUR-INVENTION-UNDER-TEST -> swept on train, never adopted.

WHY THIS IS THE COMBINATION, NOT EITHER CUE ALONE. The diagnostic (exp_similar_competitor_pronoun_diagnostic_v1)
showed on the SAME real pronoun population: frequency 0.570, recency 0.642, subject-recency 0.660, but the oracle
(any cue right) = 0.813 -> +0.152 headroom BECAUSE the cues are complementary (recency & frequency disagree 41%,
each right on a distinct chunk). A_i fuses them so it can capture that headroom; either cue alone cannot.

FLOORS (recomputed on the SAME held-out population): FREQUENCY (content-only floor), RECENCY (naive recency --
the documented tie), SUBJECT_REC (the STRONGEST single cue -- we must beat this too, not just the content floor).
INFO-FREE TWINS (must LOSE): SHUFFLE_CTX (permute mention sentences within doc -> destroys temporal contiguity ->
base collapses to frequency); SHUFFLE_ROLE (permute role labels -> destroys the salience cue).

GENERALIZATION: weights are LEARNED on a TRAIN doc split and all headline numbers are on HELD-OUT TEST docs, so
the win is not overfit; reported across competitor-count strata.

NO external LLM. Consumes the built TCM organ (torch). Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_actr_tcm_combiner_v1.py --self-test
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

ANCHOR = "similar_competitor_actr_tcm_combiner_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON_PATH = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")

ROLES = ("SUBJECT", "OBJECT", "OTHER")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------ TCM kernel (consumed from the organ)
def tcm_kernel_table(max_lag, min_period=2.0, max_mult=4.0, horizon=1000.0, d=1024):
    """kernel_TCM[dt] = Re<conj(ctx(0)), ctx(dt)>/d from hdlab.graded_temporal_context, for dt=0..max_lag.
    This CONSUMES the built organ's multi-timescale contiguity kernel (does not rebuild it)."""
    import torch
    from hdlab.graded_temporal_context import GradedTemporalContext
    g = GradedTemporalContext(d=d, min_period=min_period, max_period_mult=max_mult, horizon=horizon)
    c0 = g.ctx(0.0)
    tab = np.empty(max_lag + 1, dtype=np.float64)
    for L in range(max_lag + 1):
        cL = g.ctx(float(L))
        tab[L] = float((torch.conj(c0) * cL).real.mean())
    # base-level weights are non-negative (ACT-R t^{-d} > 0); clip the phasor kernel's far-tail wiggle at 0
    tab = np.clip(tab, 0.0, None)
    return tab


# ------------------------------------------------------------------ data
def load_instances():
    return json.load(open(PRON_PATH, encoding="utf-8"))


def split_docs(insts, test_frac=0.4):
    docs = sorted(set(i["doc"] for i in insts))
    test = set()
    for dnm in docs:
        h = int(hashlib.md5(dnm.encode()).hexdigest(), 16) % 1000 / 1000.0
        if h < test_frac:
            test.add(dnm)
    return test


def prior_mentions(inst):
    """{cand_id: [(sent, role), ...]} keeping ONLY mentions strictly before the pronoun sentence (leak-free)."""
    ps = int(inst["p_sent"])
    out = {}
    for cid, ms in inst["candidates"].items():
        pm = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if pm:
            out[int(cid)] = pm
    return out


def make_queries(insts, shuffle_ctx=False, shuffle_role=False, seed=0):
    """Precompute, per ambiguous instance (>=2 prior candidates), the leak-free prior view + gold.
    Optional info-free twins: shuffle_ctx permutes mention sentences within the doc; shuffle_role permutes
    role labels. Both destroy exactly one signal while leaving the candidate set intact."""
    gen = np.random.default_rng(seed)
    # collect all (sent, role) per doc to build a within-doc permutation for the twins
    per_doc_sents, per_doc_roles = {}, {}
    if shuffle_ctx or shuffle_role:
        for inst in insts:
            d = inst["doc"]
            for cid, ms in inst["candidates"].items():
                for m in ms:
                    per_doc_sents.setdefault(d, []).append(int(m["sent"]))
                    per_doc_roles.setdefault(d, []).append(str(m.get("role") or "OTHER"))
    qs = []
    for inst in insts:
        pv = prior_mentions(inst)
        if len(pv) < 2:
            continue
        ps = int(inst["p_sent"])
        if shuffle_ctx or shuffle_role:
            d = inst["doc"]
            spool = np.array(per_doc_sents[d]); rpool = list(per_doc_roles[d])
            new = {}
            for cid, pm in pv.items():
                nm = []
                for (s, r) in pm:
                    ns = int(gen.choice(spool)) if shuffle_ctx else s
                    nr = str(rpool[int(gen.integers(0, len(rpool)))]) if shuffle_role else r
                    if ns < ps:      # keep leak-free after shuffling sentences
                        nm.append((ns, nr))
                if nm:
                    new[cid] = nm
            pv = new
            if len(pv) < 2:
                continue
        qs.append({"gold": int(inst["gold"]), "p_sent": ps, "pv": pv,
                   "n_cand": len(pv), "gold_prior": int(inst["gold"]) in pv})
    return qs


# ------------------------------------------------------------------ cues + the ACT-R x TCM combiner
def _nearest(pv, cid, ps):
    return ps - max(s for s, _ in pv[cid])


def floor_pred(q, which):
    pv, ps = q["pv"], q["p_sent"]
    cands = sorted(pv.keys())
    if which == "FREQUENCY":
        return max(cands, key=lambda c: (len(pv[c]), -_nearest(pv, c, ps), -c))
    if which == "RECENCY":
        return min(cands, key=lambda c: (_nearest(pv, c, ps), c))
    if which == "SUBJECT_REC":
        def subj_rec(c):
            subj = [s for s, r in pv[c] if r == "SUBJECT"]
            return (ps - max(subj)) if subj else 10 ** 9
        if any(subj_rec(c) < 10 ** 9 for c in cands):
            return min(cands, key=lambda c: (subj_rec(c), c))
        return min(cands, key=lambda c: (_nearest(pv, c, ps), c))
    raise ValueError(which)


def combiner_pred(q, kernel, g):
    """A_i = ln sum_m kernel[dt_m] * g(role_m); argmax. g maps role -> encoding-salience weight.
    Deterministic tie-break: higher activation, then nearer most-recent mention, then lower id."""
    pv, ps = q["pv"], q["p_sent"]
    maxlag = len(kernel) - 1
    scored = []
    for c in sorted(pv.keys()):
        acc = sum((kernel[ps - s] if (ps - s) <= maxlag else 0.0) * g.get(r, g["OTHER"]) for s, r in pv[c])
        scored.append((np.log(acc + 1e-12), -_nearest(pv, c, ps), -c, c))
    scored.sort(reverse=True)
    return scored[0][3]


def acc_of(qs, predfn):
    if not qs:
        return float("nan")
    return float(np.mean([int(predfn(q) == q["gold"]) for q in qs]))


def learn_weights(train_qs, kernel):
    """Learn g(SUBJECT), g(OBJECT) by coordinate ascent on TRAIN hit@1 (g(OTHER)=1 reference). Competition-Model
    cue weighting: the relative pull of a grammatical role is fit to how well it predicts, not hand-set."""
    grid = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 9.0]
    g = {"SUBJECT": 1.0, "OBJECT": 1.0, "OTHER": 1.0}
    best = acc_of(train_qs, lambda q: combiner_pred(q, kernel, g))
    for _ in range(3):
        improved = False
        for role in ("SUBJECT", "OBJECT"):
            for val in grid:
                cand = dict(g); cand[role] = val
                a = acc_of(train_qs, lambda q: combiner_pred(q, kernel, cand))
                if a > best + 1e-9:
                    best, g, improved = a, cand, True
        if not improved:
            break
    return g, best


def paired_delta(qs, pa, pb, gen, n_boot=2000):
    if not qs:
        return {"delta": float("nan"), "band": "NA", "n": 0}
    a = np.array([int(pa(q) == q["gold"]) for q in qs], float)
    b = np.array([int(pb(q) == q["gold"]) for q in qs], float)
    diff = a - b
    n = len(diff)
    idx = gen.integers(0, n, size=(n_boot, n))
    boot = diff[idx].mean(axis=1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    null = np.array([np.abs((diff * gen.choice([-1.0, 1.0], size=n)).mean()) for _ in range(n_boot)])
    p95 = float(np.percentile(null, 95))
    band = "ABOVE" if (lo > 0 and lo > p95) else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": float(diff.mean()), "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0,
            "null_p95": p95, "band": band, "n": n}


def run(n_boot=2000, test_frac=0.4):
    t0 = time.perf_counter()
    insts = load_instances()
    test_docs = split_docs(insts, test_frac)
    train_insts = [i for i in insts if i["doc"] not in test_docs]
    test_insts = [i for i in insts if i["doc"] in test_docs]

    train_qs = make_queries(train_insts)
    test_qs = make_queries(test_insts)
    gen = np.random.default_rng(20260830)

    # sweep the organ kernel timescale on TRAIN (OUR-INVENTION param), pick best-generalizing on train
    best = None
    for (mp, mm) in [(2.0, 4.0), (2.0, 8.0), (3.0, 4.0), (2.0, 2.0)]:
        ker = tcm_kernel_table(400, min_period=mp, max_mult=mm)
        g, tr_acc = learn_weights(train_qs, ker)
        if best is None or tr_acc > best[0]:
            best = (tr_acc, mp, mm, ker, g)
    tr_acc, mp, mm, kernel, g = best
    _log("LEARNED on train: kernel(min_period=%.1f,max_mult=%.1f) g=%s -> train combiner=%.3f"
         % (mp, mm, {k: round(v, 2) for k, v in g.items()}, tr_acc))

    def block(qs, label):
        pf = {w: (lambda q, w=w: floor_pred(q, w)) for w in ("FREQUENCY", "RECENCY", "SUBJECT_REC")}
        comb = lambda q: combiner_pred(q, kernel, g)
        accs = {w: acc_of(qs, pf[w]) for w in pf}
        accs["COMBINER"] = acc_of(qs, comb)
        strongest = max(("FREQUENCY", "RECENCY", "SUBJECT_REC"), key=lambda w: accs[w])
        deltas = {
            "vs_FREQUENCY": paired_delta(qs, comb, pf["FREQUENCY"], gen, n_boot),
            "vs_RECENCY": paired_delta(qs, comb, pf["RECENCY"], gen, n_boot),
            "vs_SUBJECT_REC": paired_delta(qs, comb, pf["SUBJECT_REC"], gen, n_boot),
            "vs_STRONGEST(%s)" % strongest: paired_delta(qs, comb, pf[strongest], gen, n_boot),
        }
        return {"label": label, "n": len(qs), "acc": accs, "strongest_floor": strongest, "deltas": deltas}

    test_block = block(test_qs, "TEST_ambiguous_all")
    test_resolvable = block([q for q in test_qs if q["gold_prior"]], "TEST_resolvable")

    # info-free twins on TEST docs (same learned weights)
    twin_ctx_qs = make_queries(test_insts, shuffle_ctx=True, seed=101)
    twin_role_qs = make_queries(test_insts, shuffle_role=True, seed=202)
    comb = lambda q: combiner_pred(q, kernel, g)
    twin = {
        "COMBINER_test": test_block["acc"]["COMBINER"],
        "COMBINER_shuffle_ctx": acc_of(twin_ctx_qs, comb),
        "COMBINER_shuffle_role": acc_of(twin_role_qs, comb),
        "FREQUENCY_test": test_block["acc"]["FREQUENCY"],
    }
    twin["ctx_twin_loses"] = bool(twin["COMBINER_shuffle_ctx"] < twin["COMBINER_test"])
    twin["role_twin_loses"] = bool(twin["COMBINER_shuffle_role"] < twin["COMBINER_test"])

    # strata on TEST
    strata = {}
    for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 999, "5+")]:
        qs = [q for q in test_qs if lo <= q["n_cand"] <= hi]
        if qs:
            strata[lbl] = {"n": len(qs), "combiner": acc_of(qs, comb),
                           "subject_rec": acc_of(qs, lambda q: floor_pred(q, "SUBJECT_REC")),
                           "frequency": acc_of(qs, lambda q: floor_pred(q, "FREQUENCY"))}

    # verdict on the headline (full ambiguous test subset)
    a = test_block["acc"]
    d_freq = test_block["deltas"]["vs_FREQUENCY"]
    d_rec = test_block["deltas"]["vs_RECENCY"]
    strongest = test_block["strongest_floor"]
    d_strong = test_block["deltas"]["vs_STRONGEST(%s)" % strongest]
    passed = (d_freq["band"] == "ABOVE" and d_freq["delta"] >= 0.10 and
              d_rec["band"] == "ABOVE" and d_strong["band"] == "ABOVE" and
              twin["ctx_twin_loses"])
    verdict = "PASS" if passed else "PARTIAL_OR_FAIL"

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_train_docs": len(set(i["doc"] for i in train_insts)),
           "n_test_docs": len(test_docs), "n_train_q": len(train_qs), "n_test_q": len(test_qs),
           "learned": {"min_period": mp, "max_mult": mm, "g": g, "train_combiner_acc": tr_acc},
           "test": test_block, "test_resolvable": test_resolvable, "twins": twin, "strata": strata,
           "VERDICT": verdict}

    _log("=== TEST (held-out docs, ambiguous subset n=%d) ===" % test_block["n"])
    _log("  FREQUENCY(content floor)=%.3f  RECENCY=%.3f  SUBJECT_REC=%.3f  ||  COMBINER=%.3f"
         % (a["FREQUENCY"], a["RECENCY"], a["SUBJECT_REC"], a["COMBINER"]))
    _log("  COMBINER - FREQUENCY = %+.3f [%.3f,%.3f] %s (need >=+0.10 ABOVE)"
         % (d_freq["delta"], d_freq["lo"], d_freq["hi"], d_freq["band"]))
    _log("  COMBINER - RECENCY   = %+.3f [%.3f,%.3f] %s" % (d_rec["delta"], d_rec["lo"], d_rec["hi"], d_rec["band"]))
    _log("  COMBINER - STRONGEST(%s) = %+.3f [%.3f,%.3f] %s"
         % (strongest, d_strong["delta"], d_strong["lo"], d_strong["hi"], d_strong["band"]))
    _log("  TWIN shuffle-ctx=%.3f (loses=%s)  shuffle-role=%.3f (loses=%s)"
         % (twin["COMBINER_shuffle_ctx"], twin["ctx_twin_loses"],
            twin["COMBINER_shuffle_role"], twin["role_twin_loses"]))
    for lbl, sv in strata.items():
        _log("  competitors=%s n=%d combiner=%.3f subj_rec=%.3f freq=%.3f"
             % (lbl, sv["n"], sv["combiner"], sv["subject_rec"], sv["frequency"]))
    _log("VERDICT: %s (%.1fs)" % (verdict, res["elapsed_s"]))
    return res


def self_test():
    _log("SELF-TEST: kernel decays; combiner fuses recency+frequency+role; twins destroy signal")
    ker = tcm_kernel_table(50)
    assert ker[0] == 1.0 or abs(ker[0] - 1.0) < 1e-9, "kernel(0) should be 1"
    assert ker[1] < ker[0] and ker[10] < ker[1] and (ker >= 0).all(), "kernel must be a non-negative decay"
    g = {"SUBJECT": 3.0, "OBJECT": 1.0, "OTHER": 1.0}
    # entity 1: two mentions (freq) but far; entity 2: one recent SUBJECT mention.
    q = {"gold": 2, "p_sent": 10, "n_cand": 2,
         "pv": {1: [(0, "OTHER"), (1, "OTHER")], 2: [(9, "SUBJECT")]}}
    # recency picks 2 (nearer); frequency picks 1 (2 mentions); combiner with role bonus should pick 2
    assert floor_pred(q, "RECENCY") == 2
    assert floor_pred(q, "FREQUENCY") == 1
    assert combiner_pred(q, ker, g) == 2, "combiner should fuse recency+role to pick the recent subject"
    # with NO role bonus and the far entity mentioned MANY times, frequency+base can win
    q2 = {"gold": 1, "p_sent": 10, "n_cand": 2,
          "pv": {1: [(2, "OTHER"), (3, "OTHER"), (4, "OTHER"), (5, "OTHER")], 2: [(6, "OTHER")]}}
    gflat = {"SUBJECT": 1.0, "OBJECT": 1.0, "OTHER": 1.0}
    assert combiner_pred(q2, ker, gflat) == 1, "accumulated base-level (frequency) should win when roles tie"
    # leak-free twin: shuffling context must not resurrect a pronoun-sentence mention
    insts = load_instances()
    tw = make_queries(insts[:200], shuffle_ctx=True, seed=1)
    for q in tw[:50]:
        assert all(s < q["p_sent"] for pm in q["pv"].values() for s, _ in pm), "twin leaked a >=p_sent mention"
    _log("SELF-TEST PASS")
    return {"kernel0": float(ker[0]), "kernel10": float(ker[10])}


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
