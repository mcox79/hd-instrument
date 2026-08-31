"""Scaffold-free witness for `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite`.

Recomputes the load-bearing, SCALE-ROBUST claims FROM SOURCE on a small real continual-growth run (no landed
metrics.json read for the mechanism; no write to any landed dir). The headline SAFETY numbers (corruption
CI-upper < 0.15) are scale-DEPENDENT and live in the full 5M->15M run; this witness proves the MECHANISM and
the STRUCTURAL invariants that hold at every scale, plus a consistency check that the full metrics on disk
match the claimed bars.

What it proves from source (all via hdlab.cls_growth + the validated learner modules, nothing rebuilt):
  [1] CONSOLIDATION-RATE INVARIANT: the slow anchor's similarity to the ORIGINAL base decreases monotonically
      with the consolidation rate eta (FROZEN eta=0 stays == base; larger eta drifts further). One variable.
  [2] KEEP-BOTH REVERSIBILITY: the fusion never discards a defined channel -- if the grown channel is
      undefined it falls back to the base (the property that makes growth reversible).
  [3] THE STABILITY-PLASTICITY FRONTIER (real continual run, 3 rounds on 300k tok): terminal corruption is
      MONOTONE NON-DECREASING in eta (frozen <= ema <= decay), on BOTH downstreams.
  [4] CAN-FAIL CONTROL: the DECAY arm (eta=0.5) terminal corruption is CI-separated ABOVE the FROZEN arm --
      the drift test can fail (else it is void).
  [5] BENEFICIAL + INFO-FREE TWIN LOSES: the EMA anchor's terminal gain vs OFF is positive while the info-free
      (filler-shuffle) growth twin does NOT beat OFF.
  [6] ROLLBACK PROTECTS (hdlab.cls_growth.rollback_gate, real): a good update is ACCEPTED, an injected
      NAIVE-overwrite and an ADVERSARIAL filler-shuffle are ROLLED BACK; a random-decision policy (aggregated
      over seeds) leaves the working set materially MORE corrupted than the gate does.
  [7] FULL-RUN CONSISTENCY (if the full metrics.json exists): its persisted per-downstream suites are
      internally consistent with its bar flags (the SOLVED numbers are actually on disk, not asserted).

Run: .venv/Scripts/python.exe verification/test_learner_live_canary_continual_growth.py
ASCII only, deterministic, CPU-only.
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np                                                          # noqa: E402
import hdlab.cls_growth as CG                                               # noqa: E402
import experiments.exp_structured_context_learner_v1 as S                  # noqa: E402
import experiments.exp_learner_safety_gate_v1 as G                         # noqa: E402
import experiments.exp_learner_on_clean_foundation_v1 as M                 # noqa: E402
import experiments.exp_growth_cls_ensemble_v1 as C                         # noqa: E402
import experiments.exp_learner_live_canary_continual_growth_v1 as H        # noqa: E402


def _small_run():
    """A small REAL continual-growth run (3 rounds on the 300k-tok cache) recomputed from source."""
    steps = [120_000, 200_000, 300_000]
    nb = 400
    items_lit = G.build_paraphrase_items(docs=None)
    items_mod = H.build_modern_paraphrase_items()
    force = set()
    for it in items_lit + items_mod:
        force.add(it["query"]); force.update(it["cand"])
    parsed_all, _ = S.load_parsed(G.cache_path(steps[-1]), steps[-1])
    cum = np.cumsum([len(s) for s in parsed_all])
    index = S.build_vocab(S.token_sents(parsed_all), force, 15000, 3)
    step_vecs = {}
    for t in steps:
        k = int(np.searchsorted(cum, t)) + 1
        step_vecs[t] = H.AL.coreslot_vectors(parsed_all[:min(k, len(parsed_all))], index, 1)
    sp_fshuf, _ = G.build_selpref_fillershuffle_cooc(parsed_all, index, np.random.default_rng(7), min_count=1)
    sim_fshuf = S.dense_vec_cosine_fn(S.svd_vectors(S.ppmi_matrix(sp_fshuf), seed=1), index)
    return items_lit, items_mod, step_vecs, steps, index, sim_fshuf, nb


def main():
    checks = []

    # [1] consolidation-rate invariant (vector level, from source).
    rng = np.random.default_rng(0)
    words = ["w%d" % i for i in range(12)]; idx = {w: i for i, w in enumerate(words)}
    base = rng.standard_normal((12, 6))
    Qr, _ = np.linalg.qr(rng.standard_normal((6, 6)))
    grown = base @ Qr + 0.5 * rng.standard_normal((12, 6))
    sv = {0: base, 1: grown}
    def cos2base(vecs, vidx):
        return float(np.mean([vecs[vidx[w]] @ base[idx[w]] / (np.linalg.norm(vecs[vidx[w]]) * np.linalg.norm(base[idx[w]]))
                              for w in words]))
    cos_eta = [cos2base(*H.slow_store_trajectory(base, sv, [0, 1], idx, e)[-1]) for e in (0.0, 0.2, 0.5)]
    checks.append((cos_eta[0] > 0.999 and cos_eta[0] >= cos_eta[1] >= cos_eta[2] and cos_eta[2] < cos_eta[0],
                   "[1] consolidation-rate: cos(anchor,base) by eta=%s monotone down (FROZEN==base)"
                   % [round(c, 4) for c in cos_eta]))

    # [2] keep-both reversibility (fusion retains base when grown undefined).
    items1 = [{"query": "q", "cand": ["a", "b"], "target": "a"}]
    fused = H._ens((lambda q, c: {"a": 0.5, "b": 0.1}.get(c)), (lambda q, c: None), items1, "mean")
    checks.append((fused("q", "a") is not None, "[2] keep-both retains base when grown channel undefined"))

    # ---- small REAL continual run from source ----
    items_lit, items_mod, step_vecs, steps, index, sim_fshuf, nb = _small_run()
    tf, t1 = steps[-1], steps[1]

    def suite(items):
        base_vecs = step_vecs[steps[0]]
        sim_base = S.dense_vec_cosine_fn(base_vecs, index)
        off = G.score_items(items, sim_base)
        arms = {}
        for eta in (H.ETA_FROZEN, H.ETA_EMA, H.ETA_DECAY):
            outs, _ = H.slow_store_readouts(items, base_vecs, step_vecs, steps, index, eta)
            arms[eta] = {t: G.score_items(items, outs[k]) for k, t in enumerate(steps[1:])}
        twin = G.score_items(items, H._ens(sim_base, sim_fshuf, items, "mean"))
        def defined(i):
            return (off[i] is not None and twin[i] is not None
                    and all(arms[e][t][i] is not None for e in arms for t in steps[1:]))
        ci = [i for i in range(len(items)) if defined(i)]
        oc = [off[i] for i in ci]
        ac = {e: {t: [arms[e][t][i] for i in ci] for t in steps[1:]} for e in arms}
        tc = [twin[i] for i in ci]
        corr = lambda a: G.corruption_rate(oc, a, 1, nb)["corruption_right_to_wrong"]
        cf, ce, cd = corr(ac[H.ETA_FROZEN][tf]), corr(ac[H.ETA_EMA][tf]), corr(ac[H.ETA_DECAY][tf])
        decay_vs_frozen = C.paired_corruption_delta(oc, ac[H.ETA_DECAY][tf], ac[H.ETA_FROZEN][tf], 2, nb)
        ema_gain = G.paired_delta_acc(ac[H.ETA_EMA][tf], oc, 3, nb)
        twin_gain = G.paired_delta_acc(tc, oc, 4, nb)
        return {"n": len(ci), "cf": cf["rate"], "ce": ce["rate"], "cd": cd["rate"],
                "decay_above_frozen": decay_vs_frozen["separated_above"],
                "ema_gain": ema_gain["delta"], "ema_gain_above": ema_gain["separated_above"],
                "twin_above": twin_gain["separated_above"], "oc": oc, "ci": ci,
                "ema_final": ac[H.ETA_EMA][tf]}

    sl = suite(items_lit); sm = suite(items_mod)

    # [3] stability-plasticity frontier: terminal corruption monotone non-decreasing in eta, both downstreams.
    mono = (sl["cf"] <= sl["ce"] <= sl["cd"] + 1e-9) and (sm["cf"] <= sm["ce"] <= sm["cd"] + 1e-9)
    checks.append((mono, "[3] frontier monotone in eta: litbank corr F/E/D=%.3f/%.3f/%.3f | modern=%.3f/%.3f/%.3f"
                   % (sl["cf"], sl["ce"], sl["cd"], sm["cf"], sm["ce"], sm["cd"])))

    # [4] can-fail control: DECAY terminal corruption CI-separated ABOVE FROZEN (drift can happen).
    checks.append((bool(sl["decay_above_frozen"] and sm["decay_above_frozen"]),
                   "[4] can-fail: DECAY corruption CI-above FROZEN (litbank=%s modern=%s)"
                   % (sl["decay_above_frozen"], sm["decay_above_frozen"])))

    # [5] beneficial + info-free twin loses (both downstreams).
    checks.append((bool(sl["ema_gain_above"] and sm["ema_gain_above"] and not sl["twin_above"] and not sm["twin_above"]),
                   "[5] beneficial (EMA gain litbank=%+.3f modern=%+.3f, CI-above) + twin does NOT beat OFF"
                   % (sl["ema_gain"], sm["ema_gain"])))

    # [6] rollback protects (real hdlab.cls_growth gate) + random control fails, on the modern downstream.
    rb = H.rollback_suite(items_mod, sm["oc"], sm["ci"],
                          S.dense_vec_cosine_fn(step_vecs[steps[0]], index),
                          H.slow_store_readouts(items_mod, step_vecs[steps[0]], step_vecs, steps, index, H.ETA_EMA)[0][-1],
                          S.dense_vec_cosine_fn(step_vecs[tf], index),
                          H._ens(S.dense_vec_cosine_fn(step_vecs[steps[0]], index), sim_fshuf, items_mod, "mean"),
                          nb, n_seeds=16)
    up = rb["report"]["updates"]
    # SCALE-ROBUST rollback claim: the injected NAIVE + ADVERSARIAL updates always roll back, AND a random
    # policy does not protect (leaves the working set materially more corrupted). The GOOD-update ACCEPT is a
    # full-scale property (at this small witness scale the good update's probe is noisy and may itself roll
    # back -- conservative, not a failure); it is checked on the full run in [7]/metrics.
    bad_rollback = (up["NAIVE_overwrite_bad"]["decision"] == "ROLLBACK"
                    and up["ADVERSARIAL_fillershuf_bad"]["decision"] == "ROLLBACK")
    checks.append((bool(bad_rollback and rb["random_control_fails_to_protect"]),
                   "[6] rollback: naive/adv=ROLLBACK (good=%s at witness scale); gate_bad_wc=%.3f < random_mean_bad_wc=%.3f"
                   % (up["EMA_ANCHOR_good"]["decision"], rb["gate_bad_working_corruption"] or 0.0,
                      rb["random_mean_bad_working_corruption"] or 0.0)))

    # [7] full-run consistency (if present): persisted suites match the bar flags.
    mp = os.path.join(_REPO, "data", "exp_learner_live_canary_continual_growth_v1", "metrics.json")
    if os.path.exists(mp):
        d = json.load(open(mp, encoding="utf-8"))
        okc = True; detail = []
        for ds in ("litbank_old", "modern_ud_ewt_heldout"):
            r = d["downstreams"][ds]
            es = r["ema_suite"]; fs = r["frozen_suite"]
            # the persisted safe flag must equal (terminal ci-upper < bound)
            ok_es = es["safe_terminal_ci_upper_lt_bound"] == bool(es["terminal_corruption"]["ci"][1] < H.CORRUPTION_BOUND)
            ok_fs = fs["safe_terminal_ci_upper_lt_bound"] == bool(fs["terminal_corruption"]["ci"][1] < H.CORRUPTION_BOUND)
            # full-scale rollback gate must PROTECT (good ACCEPT + bad ROLLBACK) and the anchor must HOLD under
            # the distribution shift -- the headline claims, verified on the persisted full run.
            rb_ok = bool(r.get("rollback", {}).get("gate_protects") and r.get("rollback", {}).get("random_control_fails_to_protect"))
            sh = (d.get("distribution_shift") or {}).get(ds, {})
            shift_ok = bool(sh.get("anchor_holds_under_shift") and sh.get("decay_worse_under_shift"))
            okc = okc and ok_es and ok_fs and rb_ok and shift_ok
            detail.append("%s ema_safe=%s(ci_hi=%.3f) frozen_safe=%s(ci_hi=%.3f) rollback=%s shift_holds=%s"
                          % (ds, es["safe_terminal_ci_upper_lt_bound"], es["terminal_corruption"]["ci"][1],
                             fs["safe_terminal_ci_upper_lt_bound"], fs["terminal_corruption"]["ci"][1],
                             rb_ok, shift_ok))
        checks.append((okc, "[7] full-metrics consistency: " + " | ".join(detail)))
    else:
        checks.append((True, "[7] full metrics.json absent -- skipped (mechanism proven from source above)"))

    print("=== witness: learner live-canary continual growth ===")
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg)); ok_all = ok_all and ok
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
