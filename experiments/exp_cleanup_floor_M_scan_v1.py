"""cleanup_floor_M_scan_v1 -- M-dependence of Shannon-floor cleanup-ceiling META.

INFORMER for META atom: T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0
(cert ledger row 675; Skunkworks tiered MEASURED_MECHANISM 2026-06-23 because 3 branches remain
untested). This cell closes BRANCH #2 (M-scan at sigma=1.5).

Question: where does the cleanup-ceiling regime begin as M increases?
- Parent N_DIM=512 M=200 sigma=1.5 found argmax recall=0.023 (Shannon-floor regime).
- att1_v2_krotov at M=50 sigma=1.5 found argmax=0.093 (4x lift over M=200).
- So the floor IS M-dependent at low M. THIS CELL characterizes the knee.

Decision rules:
- M-STRONG-DEP (downgrade META):  recall(M=50, sigma=1.5) >= 0.30 AND recall(M=200, sigma=1.5) <= 0.05
- M-INDEP    (strengthen META):   recall(M=50, sigma=1.5) <= 0.10 (similar to M=200)
- KNEE-CHARACTERIZED (middle):    alpha-c-for-cleanup map is the deliverable

NOT a chain-grade-candidate cell. META-informer only. status_log importance MEDIUM.

DESIGN: 1 arm (ARGMAX_BASELINE) x 5 M x 3 sigma x 3 seeds x N_EVAL=200.
N_DIM=512 fixed.  Random bipolar codebook L2-normalized.

PRE-REG bands (this cell informs META; doesn't HARD_PASS/HARD_FAIL on itself):
- DECISION_M_STRONG_DEP: recall(M=50, sigma=1.5) >= 0.30 AND recall(M=200, sigma=1.5) <= 0.05
- DECISION_M_INDEPENDENT: recall(M=50, sigma=1.5) <= 0.10
- DECISION_KNEE_MIDDLE: between the two; emit alpha_c_for_cleanup map.

Sanity self-test: at sigma=0.0 ANY M: recall=1.000 (clean cue = atom-recovery by construction).

Substrate-only by construction (no encoder; HD codebook generated).  ASCII-only.
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "cleanup_floor_M_scan_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 512
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    M_SWEEP = [25, 50, 100, 200, 400]
    SIGMA_SWEEP = [1.0, 1.5, 2.0]
    N_EVAL = 200
    SANITY_SIGMA_ZERO = True
else:
    # Smoke: small subset, fast.
    SEEDS = [0]
    M_SWEEP = [25, 100]
    SIGMA_SWEEP = [1.0, 1.5]
    N_EVAL = 40
    SANITY_SIGMA_ZERO = True

DISCRIMINATOR_SIGMA = 1.5
M_LOW = 50    # decision M used in M-STRONG-DEP / M-INDEP rules
M_HIGH = 200  # decision M used in M-STRONG-DEP rule

CONFIG_VERSION = ("cleanup_floor_M_scan_v1; N_DIM=%d N_EVAL=%d M_sweep=%s sigma_sweep=%s "
                  "seeds=%s mode=%s") % (N_DIM, N_EVAL, M_SWEEP, SIGMA_SWEEP, SEEDS, RUN_MODE)


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _build_bipolar_codebook(seed, M_loc, D_loc):
    """Random bipolar codebook (+/-1); L2-normalized to unit norm."""
    g = np.random.default_rng(seed)
    cb = g.choice([-1.0, 1.0], size=(M_loc, D_loc)).astype(np.float32)
    return _l2_normalize(cb).astype(np.float32)


def argmax_recall(codebook, query_indices, sigma, seed, arm_tag):
    """ARGMAX_BASELINE: single-step cosine argmax over noised cue."""
    arm_seed = int(seed) * 1000 + int(sigma * 10000) + (hash(arm_tag) % 1000)
    g = np.random.default_rng(arm_seed)
    M_loc, D_loc = codebook.shape
    cb_n = _l2_normalize(codebook.astype(np.float32))
    cues = codebook[query_indices] + sigma * g.standard_normal((len(query_indices), D_loc)).astype(np.float32)
    cues_n = _l2_normalize(cues)
    pred = np.argmax(cues_n @ cb_n.T, axis=1).astype(np.int64)
    n_correct = int((pred == query_indices).sum())
    return float(n_correct) / max(len(query_indices), 1)


def run_unit(seed):
    g = np.random.default_rng(seed)
    print("  [seed=%d] M_sweep=%s sigma_sweep=%s N_EVAL=%d" % (seed, M_SWEEP, SIGMA_SWEEP, N_EVAL), flush=True)
    grid = {}  # grid[str(M)][str(sigma)] = recall
    sanity = {}  # sanity[str(M)] = recall_at_sigma_0
    for M_loc in M_SWEEP:
        t_M = time.time()
        cb = _build_bipolar_codebook(seed, M_loc, N_DIM)
        n_q = min(N_EVAL, M_loc)
        q_idx = g.choice(M_loc, size=n_q, replace=False)
        per_sigma = {}
        for sig in SIGMA_SWEEP:
            r = argmax_recall(cb, q_idx, sig, seed, arm_tag="ARGMAX_BASELINE")
            per_sigma[str(sig)] = round(r, 4)
        # sanity: sigma=0.0 must give recall=1.000
        if SANITY_SIGMA_ZERO:
            r0 = argmax_recall(cb, q_idx, 0.0, seed, arm_tag="ARGMAX_BASELINE_SANITY")
            sanity[str(M_loc)] = round(r0, 4)
        grid[str(M_loc)] = per_sigma
        print("    [seed=%d M=%d N_EVAL=%d] sigmas=%s sanity_sigma_0=%s (wall=%.1fs)" % (
            seed, M_loc, n_q, per_sigma, sanity.get(str(M_loc), "N/A"), time.time() - t_M), flush=True)
    return {
        "seed": seed,
        "grid": grid,
        "sanity_sigma_0": sanity,
        "N_DIM": N_DIM,
        "M_sweep": M_SWEEP,
        "sigma_sweep": SIGMA_SWEEP,
        "N_EVAL": N_EVAL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results", {})

    # Aggregate across seeds: mean and std at each (M, sigma)
    M_keys = [str(m) for m in M_SWEEP]
    sigma_keys = [str(s) for s in SIGMA_SWEEP]
    agg = {}  # agg[M][sigma] = {"mean": x, "std": y, "cv": z}
    for Mk in M_keys:
        agg[Mk] = {}
        for sk in sigma_keys:
            vals = [u["grid"][Mk][sk] for u in units]
            m = float(np.mean(vals))
            s = float(np.std(vals))
            cv = s / max(m, 1e-6)
            agg[Mk][sk] = {"mean": round(m, 4), "std": round(s, 4), "cv": round(cv, 4),
                            "per_seed": [round(v, 4) for v in vals]}

    # Sanity check: sigma=0.0 must give recall=1.000 for ALL M
    sanity_violations = []
    for u in units:
        for Mk, r0 in u.get("sanity_sigma_0", {}).items():
            if r0 < 0.99:
                sanity_violations.append((u["seed"], Mk, r0))

    sigma_disc = str(DISCRIMINATOR_SIGMA)
    recall_at_M_low = agg.get(str(M_LOW), {}).get(sigma_disc, {}).get("mean", -1.0)
    recall_at_M_high = agg.get(str(M_HIGH), {}).get(sigma_disc, {}).get("mean", -1.0)
    decision_Ms_in_sweep = (M_LOW in M_SWEEP) and (M_HIGH in M_SWEEP)

    # Build alpha_c_for_cleanup map: smallest M where recall@sigma_disc drops below 0.05
    knee_M = None
    knee_recall = None
    for Mk in M_keys:
        rec = agg[Mk][sigma_disc]["mean"]
        if rec <= 0.05:
            knee_M = int(Mk)
            knee_recall = rec
            break
    # cv max across all (M, sigma) cells (excluding sanity)
    all_cv = [agg[Mk][sk]["cv"] for Mk in M_keys for sk in sigma_keys]
    max_cv = float(np.max(all_cv)) if all_cv else 0.0

    detail = {
        "agg": agg,
        "n_seeds": len(units),
        "M_sweep": M_SWEEP,
        "sigma_sweep": SIGMA_SWEEP,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "M_low": M_LOW,
        "M_high": M_HIGH,
        "recall_at_M_low_disc": recall_at_M_low,
        "recall_at_M_high_disc": recall_at_M_high,
        "knee_M_for_cleanup_at_disc_sigma": knee_M,
        "knee_recall_at_knee_M": knee_recall,
        "max_cv_across_cells": round(max_cv, 4),
        "sanity_violations": sanity_violations,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("META-INFORMER for Shannon-floor cleanup-ceiling atom (cert row 675). "
                         "N_DIM=%d M_sweep=%s sigma_sweep=%s N_EVAL=%d seeds=%s. Random bipolar "
                         "codebook L2-normalized. ARGMAX_BASELINE arm only (noise-floor "
                         "characterization, not mechanism comparison). Not a chain-grade "
                         "candidate; informs META-tiering only.") % (
                         N_DIM, M_SWEEP, SIGMA_SWEEP, N_EVAL, [u["seed"] for u in units]),
        "cites": [
            "cert_ledger_row_675_meta_cleanup_ceiling_shannon_floor_2026-06-23",
            "skunkworks_tiering_measured_mechanism_2026-06-23",
            "att1_v2_krotov_v1_M50_sigma1p5_argmax_0p093_2026-06-23",
        ],
    }

    if sanity_violations:
        msg = ("HARD_FAIL_SANITY: sigma=0 sanity violated in %d cells (clean-cue recall<0.99); "
               "implementation bug -- bipolar codebook L2-norm or argmax broken. "
               "Sample: %s") % (len(sanity_violations), sanity_violations[:3])
        return ("HARD_FAIL", msg, detail)

    summary = ("M-SCAN DECISION @ sigma=%.2f: recall(M=%d)=%.4f recall(M=%d)=%.4f knee_M=%s "
               "max_cv=%.3f sigma_0_sanity=PASS N_DIM=%d seeds=%d") % (
                DISCRIMINATOR_SIGMA, M_LOW, recall_at_M_low, M_HIGH, recall_at_M_high,
                str(knee_M), max_cv, N_DIM, len(units))

    # Decision rule (no HARD_PASS / HARD_FAIL on own merits; informer).
    # In smoke mode the decision Ms (M_LOW=50, M_HIGH=200) may not be in M_SWEEP;
    # emit MIDDLE_SMOKE rather than misclassifying.
    if not decision_Ms_in_sweep:
        return ("META_DECISION_SMOKE_PARTIAL",
                ("META_DECISION_SMOKE_PARTIAL: smoke M_sweep=%s lacks M_LOW=%d and/or M_HIGH=%d; "
                 "decision rule not evaluable (this is OK -- smoke is a gate-only run). "
                 "sigma_0_sanity=PASS. " % (M_SWEEP, M_LOW, M_HIGH) + summary),
                detail)
    if recall_at_M_low >= 0.30 and recall_at_M_high <= 0.05:
        # DECISION_M_STRONG_DEP: META downgrade candidate
        return ("META_DECISION_M_STRONG_DEP",
                ("META_DECISION_M_STRONG_DEP: Shannon-floor is M-specific -- substrate operates "
                 "fine at lower M. recall(M=%d, sigma=%.1f)=%.4f (>= 0.30) and "
                 "recall(M=%d, sigma=%.1f)=%.4f (<= 0.05); knee_M=%s. "
                 "RECOMMENDATION: downgrade META framing to '9-family-at-M=200-and-up'. " % (
                 M_LOW, DISCRIMINATOR_SIGMA, recall_at_M_low,
                 M_HIGH, DISCRIMINATOR_SIGMA, recall_at_M_high, str(knee_M)) + summary),
                detail)
    if recall_at_M_low <= 0.10:
        # DECISION_M_INDEPENDENT: META strengthens toward chain-grade candidate (1 branch closed)
        return ("META_DECISION_M_INDEPENDENT",
                ("META_DECISION_M_INDEPENDENT: Shannon-floor is M-INDEPENDENT at sigma=%.1f. "
                 "recall(M=%d)=%.4f (<= 0.10) similar to recall(M=%d)=%.4f. "
                 "RECOMMENDATION: strengthen META toward chain-grade tier (1 of 3 branches closed). " % (
                 DISCRIMINATOR_SIGMA, M_LOW, recall_at_M_low,
                 M_HIGH, recall_at_M_high) + summary),
                detail)
    # KNEE-MIDDLE: alpha_c map is the deliverable
    return ("META_DECISION_KNEE_MIDDLE",
            ("META_DECISION_KNEE_MIDDLE: M-knee characterized; recall(M=%d)=%.4f in (0.10, 0.30); "
             "recall(M=%d)=%.4f; knee_M_for_cleanup_at_sigma_%.1f=%s. "
             "RECOMMENDATION: ingest alpha_c-for-cleanup map as substrate-product-knowledge atom. " % (
             M_LOW, recall_at_M_low, M_HIGH, recall_at_M_high,
             DISCRIMINATOR_SIGMA, str(knee_M)) + summary),
            detail)


_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            v, msg, detail = compute_verdict(units)
        except Exception as e:
            v, msg, detail = ("PARTIAL_TIMEOUT", "atexit synthesize: %s" % e, {})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if v != "PARTIAL_TIMEOUT" else v,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "n_seeds": len(units),
            "detail": detail,
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize] " + msg,
            "substrate_only_decode_gate": "TRUE (HD codebook; no encoder)",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)


def _selftest():
    """Selftest: clean-cue identity + high-noise random + verdict on synthetic."""
    # T1: clean cue (sigma=0.0) MUST recover, ANY M
    for M_loc in (16, 32):
        cb = _build_bipolar_codebook(seed=0, M_loc=M_loc, D_loc=64)
        qidx = np.arange(min(8, M_loc))
        r = argmax_recall(cb, qidx, 0.0, seed=1, arm_tag="selftest_T1")
        assert r >= 0.99, "T1 zero-noise M=%d recall=%.3f" % (M_loc, r)

    # T2: very high noise (sigma=20) approx random (1/M)
    cb = _build_bipolar_codebook(seed=2, M_loc=32, D_loc=64)
    qidx = np.arange(8)
    r_hi = argmax_recall(cb, qidx, 20.0, seed=2, arm_tag="selftest_T2")
    assert r_hi <= 0.5, "T2 high-noise recall=%.3f; should be << 0.5" % r_hi

    # T3: codebook L2-norm correct
    cb = _build_bipolar_codebook(seed=3, M_loc=8, D_loc=16)
    norms = np.linalg.norm(cb, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-4), "T3 codebook not L2-normalized: norms=%s" % norms

    # T4: compute_verdict runs on synthetic 3-seed. Build grids keyed by the ACTIVE M_SWEEP
    # / SIGMA_SWEEP so the test works under both smoke and full RUN_MODE.
    # Map M (any value) -> recall@sigma with a piecewise profile that yields STRONG_DEP:
    # at low M (<=50): high recall; at high M (>=200): near zero. M_LOW=50 / M_HIGH=200
    # are the decision Ms; selftest only valid if both in M_SWEEP.
    if M_LOW in M_SWEEP and M_HIGH in M_SWEEP:
        def _profile_strong_dep(M_val, sig):
            # Designed so M=50 sigma=1.5 ~ 0.40 (>=0.30); M=200 sigma=1.5 ~ 0.03 (<=0.05)
            base = max(0.001, 1.0 - 0.005 * M_val)        # decreases with M
            sigfac = max(0.001, 1.0 - 0.3 * sig)          # decreases with sigma
            return round(min(1.0, base * sigfac), 4)
        fake_units = []
        for sd in (7, 17, 23):
            grid = {str(M_val): {str(sig): _profile_strong_dep(M_val, sig)
                                  for sig in SIGMA_SWEEP}
                    for M_val in M_SWEEP}
            sanity = {str(M_val): 1.0 for M_val in M_SWEEP}
            fake_units.append({
                "seed": sd, "grid": grid, "sanity_sigma_0": sanity,
                "N_DIM": 512, "M_sweep": M_SWEEP, "sigma_sweep": SIGMA_SWEEP,
                "N_EVAL": 200, "run_mode": "selftest", "config_version": "selftest",
            })
        v, m, d = compute_verdict(fake_units)
        assert v in ("META_DECISION_M_STRONG_DEP", "META_DECISION_M_INDEPENDENT",
                      "META_DECISION_KNEE_MIDDLE", "HARD_FAIL"), "unexpected verdict %s" % v
        # Sanity-check the profile produced the expected band on the active M_SWEEP
        r_low = d["recall_at_M_low_disc"]
        r_high = d["recall_at_M_high_disc"]
        if r_low >= 0.30 and r_high <= 0.05:
            assert v == "META_DECISION_M_STRONG_DEP", (
                "expected STRONG_DEP given r_low=%.4f r_high=%.4f; got %s" % (r_low, r_high, v))

    # T5: synthetic M-independent at all M
    def _profile_flat_low(M_val, sig):
        return round(max(0.001, 0.05 - 0.005 * sig), 4)
    fake_units2 = []
    for sd in (7, 17, 23):
        grid = {str(M_val): {str(sig): _profile_flat_low(M_val, sig)
                              for sig in SIGMA_SWEEP}
                for M_val in M_SWEEP}
        sanity = {str(M_val): 1.0 for M_val in M_SWEEP}
        fake_units2.append({
            "seed": sd, "grid": grid, "sanity_sigma_0": sanity,
            "N_DIM": 512, "M_sweep": M_SWEEP, "sigma_sweep": SIGMA_SWEEP,
            "N_EVAL": 200, "run_mode": "selftest", "config_version": "selftest",
        })
    v2, _, d2 = compute_verdict(fake_units2)
    if M_LOW in M_SWEEP:
        # M_LOW will be flat-low (~0.04) -> expect INDEPENDENT
        assert v2 == "META_DECISION_M_INDEPENDENT", (
            "expected INDEPENDENT on flat synthetic; got %s (r_low=%.4f)" % (
                v2, d2.get("recall_at_M_low_disc", -1)))

    # T6: sanity-violation triggers HARD_FAIL
    bad_unit = {
        "seed": 99,
        "grid": {str(M_val): {str(sig): 0.5 for sig in SIGMA_SWEEP} for M_val in M_SWEEP},
        "sanity_sigma_0": {str(M_SWEEP[0]): 0.50},  # bad
        "N_DIM": 512, "M_sweep": M_SWEEP, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": 200,
        "run_mode": "selftest", "config_version": "selftest",
    }
    v3, _, _ = compute_verdict([bad_unit])
    assert v3 == "HARD_FAIL", "expected HARD_FAIL on sanity-violation; got %s" % v3

    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print("[selftest] PASS: clean-cue identity + high-noise random + L2 norm + verdict triplet + "
          "sanity-gate + n_llm_calls=0", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d M_sweep=%s sigma_sweep=%s N_EVAL=%d seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M_SWEEP, SIGMA_SWEEP, N_EVAL, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "cleanup-floor-M-scan-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    v, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD codebook; no encoder)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
