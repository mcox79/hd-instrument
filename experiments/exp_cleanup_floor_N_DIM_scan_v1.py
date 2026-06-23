"""cleanup_floor_N_DIM_scan_v1 -- N_DIM-dependence of Shannon-floor cleanup-ceiling META.

INFORMER for META atom: T3/META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0
(cert ledger row 675; Skunkworks tiered MEASURED_MECHANISM 2026-06-23 because 3 branches remain
untested). This cell closes BRANCH #1: N_DIM-scan at M=200 sigma in {1.0, 1.5, 2.0}.

Branch #2 (M-scan) just closed: META_DECISION_M_INDEPENDENT at sigma=1.5 (recall stays flat-low
across M_sweep). Branch #3 (learned-encoder keys) remains open.

Hypothesis (concentration of measure): in higher N, random vectors are nearer-orthogonal AND
per-direction noise contribution to similarity scales as 1/sqrt(N). So a naive N_DIM lift
should raise argmax recall mechanically. Prior ENC1 cell tested N=4096 at M=200 only and
ARM_DENSE_N4096 was 0.027 (still below HARD_PASS=0.20). This cell extends to N=8192 and
N=16384 and characterizes the N-knee.

Question: does cleanup-floor break at some larger N_DIM? At what N/M scaling regime?

Decision rules (cell informs META tier; doesn't have HP/HF on itself):
- N_DIM_DEPENDENT (downgrade META): recall(N>=8192 OR N=16384, sigma=1.5) >= 0.20
   -> high-N regime breaks the floor; META downgrades to "M=200 N=512 specific".
- N_INDEPENDENT (strengthen META): recall(N=16384, sigma=1.5) < 0.10
   -> Shannon-floor is N-independent at this M+sigma; only branch #3 remains.
- N_KNEE_MIDDLE: characterize the N-knee; deliverable is substrate-operating-map.

NOT a chain-grade-candidate cell. META-informer only. status_log importance MEDIUM.

DESIGN: 1 arm (ARGMAX_BASELINE) x 6 N_DIM x 3 sigma x 3 seeds x N_EVAL=200.
M=200 fixed. Random bipolar codebook L2-normalized.

PRE-REG bands (this cell informs META; doesn't HARD_PASS/HARD_FAIL on itself):
- DECISION_N_DIM_DEPENDENT: recall(N=8192 OR N=16384, sigma=1.5) >= 0.20
- DECISION_N_INDEPENDENT: recall(N=16384, sigma=1.5) < 0.10
- DECISION_N_KNEE_MIDDLE: between the two; emit recall(N, sigma) map.

Sanity self-test: at sigma=0.0 ANY N_DIM: recall=1.000 (clean cue = atom-recovery by construction).

Compute: largest cell is N=16384 M=200 sigma=2.0 seed=23 = one 200x200 matmul of (200,16384)
times (16384,200). Pure numpy. Total wall <10min.

Substrate-only by construction (no encoder; HD codebook generated). ASCII-only.
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

ANCHOR_NAME = "cleanup_floor_N_DIM_scan_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
M = 200  # fixed; matches parent rejection regime
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM_SWEEP = [512, 1024, 2048, 4096, 8192, 16384]
    SIGMA_SWEEP = [1.0, 1.5, 2.0]
    N_EVAL = 200
    SANITY_SIGMA_ZERO = True
else:
    # Smoke: small subset, fast.
    SEEDS = [0]
    N_DIM_SWEEP = [512, 2048]
    SIGMA_SWEEP = [1.0, 1.5]
    N_EVAL = 40
    SANITY_SIGMA_ZERO = True

DISCRIMINATOR_SIGMA = 1.5
N_DIM_HIGH_A = 8192   # decision N used in N_DIM_DEPENDENT rule (either of N_HIGH_A / N_HIGH_B)
N_DIM_HIGH_B = 16384  # decision N used in N_DIM_DEPENDENT and N_INDEPENDENT rules

CONFIG_VERSION = ("cleanup_floor_N_DIM_scan_v1; M=%d N_EVAL=%d N_DIM_sweep=%s sigma_sweep=%s "
                  "seeds=%s mode=%s") % (M, N_EVAL, N_DIM_SWEEP, SIGMA_SWEEP, SEEDS, RUN_MODE)


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
    print("  [seed=%d] N_DIM_sweep=%s sigma_sweep=%s M=%d N_EVAL=%d" % (
        seed, N_DIM_SWEEP, SIGMA_SWEEP, M, N_EVAL), flush=True)
    grid = {}  # grid[str(N_DIM)][str(sigma)] = recall
    sanity = {}  # sanity[str(N_DIM)] = recall_at_sigma_0
    for N_loc in N_DIM_SWEEP:
        t_N = time.time()
        cb = _build_bipolar_codebook(seed, M, N_loc)
        n_q = min(N_EVAL, M)
        q_idx = g.choice(M, size=n_q, replace=False)
        per_sigma = {}
        for sig in SIGMA_SWEEP:
            r = argmax_recall(cb, q_idx, sig, seed, arm_tag="ARGMAX_BASELINE")
            per_sigma[str(sig)] = round(r, 4)
        # sanity: sigma=0.0 must give recall=1.000
        if SANITY_SIGMA_ZERO:
            r0 = argmax_recall(cb, q_idx, 0.0, seed, arm_tag="ARGMAX_BASELINE_SANITY")
            sanity[str(N_loc)] = round(r0, 4)
        grid[str(N_loc)] = per_sigma
        print("    [seed=%d N_DIM=%d N_EVAL=%d] sigmas=%s sanity_sigma_0=%s (wall=%.1fs)" % (
            seed, N_loc, n_q, per_sigma, sanity.get(str(N_loc), "N/A"), time.time() - t_N), flush=True)
    return {
        "seed": seed,
        "grid": grid,
        "sanity_sigma_0": sanity,
        "M": M,
        "N_DIM_sweep": N_DIM_SWEEP,
        "sigma_sweep": SIGMA_SWEEP,
        "N_EVAL": N_EVAL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results", {})

    # Aggregate across seeds: mean and std at each (N_DIM, sigma)
    N_keys = [str(n) for n in N_DIM_SWEEP]
    sigma_keys = [str(s) for s in SIGMA_SWEEP]
    agg = {}  # agg[N][sigma] = {"mean": x, "std": y, "cv": z}
    for Nk in N_keys:
        agg[Nk] = {}
        for sk in sigma_keys:
            vals = [u["grid"][Nk][sk] for u in units]
            m = float(np.mean(vals))
            s = float(np.std(vals))
            cv = s / max(m, 1e-6)
            agg[Nk][sk] = {"mean": round(m, 4), "std": round(s, 4), "cv": round(cv, 4),
                            "per_seed": [round(v, 4) for v in vals]}

    # Sanity check: sigma=0.0 must give recall=1.000 for ALL N_DIM
    sanity_violations = []
    for u in units:
        for Nk, r0 in u.get("sanity_sigma_0", {}).items():
            if r0 < 0.99:
                sanity_violations.append((u["seed"], Nk, r0))

    sigma_disc = str(DISCRIMINATOR_SIGMA)
    recall_at_N_high_a = agg.get(str(N_DIM_HIGH_A), {}).get(sigma_disc, {}).get("mean", -1.0)
    recall_at_N_high_b = agg.get(str(N_DIM_HIGH_B), {}).get(sigma_disc, {}).get("mean", -1.0)
    decision_Ns_in_sweep = (N_DIM_HIGH_A in N_DIM_SWEEP) and (N_DIM_HIGH_B in N_DIM_SWEEP)

    # Build N-knee map: smallest N where recall@sigma_disc crosses 0.20 (cleanup-ceiling)
    knee_N_at_0p20 = None
    knee_recall_at_0p20 = None
    for Nk in N_keys:
        rec = agg[Nk][sigma_disc]["mean"]
        if rec >= 0.20:
            knee_N_at_0p20 = int(Nk)
            knee_recall_at_0p20 = rec
            break
    # cv max across all (N_DIM, sigma) cells (excluding sanity)
    all_cv = [agg[Nk][sk]["cv"] for Nk in N_keys for sk in sigma_keys]
    max_cv = float(np.max(all_cv)) if all_cv else 0.0

    detail = {
        "agg": agg,
        "n_seeds": len(units),
        "M": M,
        "N_DIM_sweep": N_DIM_SWEEP,
        "sigma_sweep": SIGMA_SWEEP,
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "N_DIM_high_a": N_DIM_HIGH_A,
        "N_DIM_high_b": N_DIM_HIGH_B,
        "recall_at_N_high_a_disc": recall_at_N_high_a,
        "recall_at_N_high_b_disc": recall_at_N_high_b,
        "knee_N_at_recall_0p20": knee_N_at_0p20,
        "knee_recall_at_knee_N": knee_recall_at_0p20,
        "max_cv_across_cells": round(max_cv, 4),
        "sanity_violations": sanity_violations,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("META-INFORMER for Shannon-floor cleanup-ceiling atom (cert row 675). "
                         "M=%d N_DIM_sweep=%s sigma_sweep=%s N_EVAL=%d seeds=%s. Random bipolar "
                         "codebook L2-normalized. ARGMAX_BASELINE arm only (noise-floor "
                         "characterization, not mechanism comparison). Not a chain-grade "
                         "candidate; informs META-tiering only. Branch #1 of 3 (N_DIM-scan); "
                         "branch #2 (M-scan) just closed META_DECISION_M_INDEPENDENT; branch #3 "
                         "(learned-encoder keys) remains.") % (
                         M, N_DIM_SWEEP, SIGMA_SWEEP, N_EVAL, [u["seed"] for u in units]),
        "cites": [
            "cert_ledger_row_675_meta_cleanup_ceiling_shannon_floor_2026-06-23",
            "skunkworks_tiering_measured_mechanism_2026-06-23",
            "cleanup_floor_M_scan_v1_META_DECISION_M_INDEPENDENT_branch2_closed",
            "ENC1_N4096_M200_argmax_0p027_prior_data_point",
        ],
    }

    if sanity_violations:
        msg = ("HARD_FAIL_SANITY: sigma=0 sanity violated in %d cells (clean-cue recall<0.99); "
               "implementation bug -- bipolar codebook L2-norm or argmax broken. "
               "Sample: %s") % (len(sanity_violations), sanity_violations[:3])
        return ("HARD_FAIL", msg, detail)

    summary = ("N-SCAN DECISION @ sigma=%.2f: recall(N=%d)=%.4f recall(N=%d)=%.4f knee_N_at_0p20=%s "
               "max_cv=%.3f sigma_0_sanity=PASS M=%d seeds=%d") % (
                DISCRIMINATOR_SIGMA, N_DIM_HIGH_A, recall_at_N_high_a,
                N_DIM_HIGH_B, recall_at_N_high_b,
                str(knee_N_at_0p20), max_cv, M, len(units))

    # Decision rule (no HARD_PASS / HARD_FAIL on own merits; informer).
    if not decision_Ns_in_sweep:
        return ("META_DECISION_SMOKE_PARTIAL",
                ("META_DECISION_SMOKE_PARTIAL: smoke N_DIM_sweep=%s lacks N_HIGH_A=%d and/or N_HIGH_B=%d; "
                 "decision rule not evaluable (this is OK -- smoke is a gate-only run). "
                 "sigma_0_sanity=PASS. " % (N_DIM_SWEEP, N_DIM_HIGH_A, N_DIM_HIGH_B) + summary),
                detail)
    # DECISION_N_DIM_DEPENDENT: META downgrade candidate (either N_HIGH_A or N_HIGH_B >= 0.20)
    if recall_at_N_high_a >= 0.20 or recall_at_N_high_b >= 0.20:
        return ("META_DECISION_N_DIM_DEPENDENT",
                ("META_DECISION_N_DIM_DEPENDENT: Shannon-floor is N_DIM-specific -- substrate "
                 "operates fine at higher N_DIM. recall(N=%d, sigma=%.1f)=%.4f OR "
                 "recall(N=%d, sigma=%.1f)=%.4f (>= 0.20); knee_N=%s. "
                 "RECOMMENDATION: downgrade META framing to 'M=200 at N=512 specific'. " % (
                 N_DIM_HIGH_A, DISCRIMINATOR_SIGMA, recall_at_N_high_a,
                 N_DIM_HIGH_B, DISCRIMINATOR_SIGMA, recall_at_N_high_b,
                 str(knee_N_at_0p20)) + summary),
                detail)
    # DECISION_N_INDEPENDENT: META strengthens (branch #1 closes; 1 branch remains)
    if recall_at_N_high_b < 0.10:
        return ("META_DECISION_N_INDEPENDENT",
                ("META_DECISION_N_INDEPENDENT: Shannon-floor is N-INDEPENDENT at sigma=%.1f. "
                 "recall(N=%d)=%.4f (< 0.10). Combined with branch #2 (M-INDEPENDENT), only "
                 "branch #3 (learned-encoder keys) remains untested. "
                 "RECOMMENDATION: strengthen META toward chain-grade tier (2 of 3 branches closed). " % (
                 DISCRIMINATOR_SIGMA, N_DIM_HIGH_B, recall_at_N_high_b) + summary),
                detail)
    # N-KNEE-MIDDLE: recall(N=16384) in [0.10, 0.20) -- characterize the knee
    return ("META_DECISION_N_KNEE_MIDDLE",
            ("META_DECISION_N_KNEE_MIDDLE: N-knee characterized; recall(N=%d)=%.4f in [0.10, 0.20); "
             "recall(N=%d)=%.4f; knee_N_at_0p20=%s. "
             "RECOMMENDATION: ingest recall-vs-N-DIM map as substrate-product-knowledge atom. " % (
             N_DIM_HIGH_B, recall_at_N_high_b, N_DIM_HIGH_A, recall_at_N_high_a,
             str(knee_N_at_0p20)) + summary),
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
            "M": M,
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
    # T1: clean cue (sigma=0.0) MUST recover, ANY N_DIM
    for N_loc in (64, 256):
        cb = _build_bipolar_codebook(seed=0, M_loc=16, D_loc=N_loc)
        qidx = np.arange(8)
        r = argmax_recall(cb, qidx, 0.0, seed=1, arm_tag="selftest_T1")
        assert r >= 0.99, "T1 zero-noise N=%d recall=%.3f" % (N_loc, r)

    # T2: very high noise (sigma=20) approx random (1/M)
    cb = _build_bipolar_codebook(seed=2, M_loc=32, D_loc=64)
    qidx = np.arange(8)
    r_hi = argmax_recall(cb, qidx, 20.0, seed=2, arm_tag="selftest_T2")
    assert r_hi <= 0.5, "T2 high-noise recall=%.3f; should be << 0.5" % r_hi

    # T3: codebook L2-norm correct
    cb = _build_bipolar_codebook(seed=3, M_loc=8, D_loc=16)
    norms = np.linalg.norm(cb, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-4), "T3 codebook not L2-normalized: norms=%s" % norms

    # T4: compute_verdict runs on synthetic 3-seed. Selftest only valid if both
    # N_DIM_HIGH_A and N_DIM_HIGH_B are in the active N_DIM_SWEEP (FULL mode).
    # Build a profile that yields N_DIM_DEPENDENT: at low N (<=4096) recall low,
    # at N=8192 OR 16384 recall >= 0.20.
    if N_DIM_HIGH_A in N_DIM_SWEEP and N_DIM_HIGH_B in N_DIM_SWEEP:
        def _profile_dep(N_val, sig):
            # Designed so N=8192 sigma=1.5 ~ 0.30 (>=0.20); N=512 sigma=1.5 ~ 0.02
            base = min(1.0, max(0.001, N_val / 32768.0))   # increases with N
            sigfac = max(0.001, 1.0 - 0.3 * sig)           # decreases with sigma
            return round(min(1.0, base * sigfac * 1.5), 4)
        fake_units = []
        for sd in (7, 17, 23):
            grid = {str(N_val): {str(sig): _profile_dep(N_val, sig)
                                  for sig in SIGMA_SWEEP}
                    for N_val in N_DIM_SWEEP}
            sanity = {str(N_val): 1.0 for N_val in N_DIM_SWEEP}
            fake_units.append({
                "seed": sd, "grid": grid, "sanity_sigma_0": sanity,
                "M": 200, "N_DIM_sweep": N_DIM_SWEEP, "sigma_sweep": SIGMA_SWEEP,
                "N_EVAL": 200, "run_mode": "selftest", "config_version": "selftest",
            })
        v, m, d = compute_verdict(fake_units)
        assert v in ("META_DECISION_N_DIM_DEPENDENT", "META_DECISION_N_INDEPENDENT",
                      "META_DECISION_N_KNEE_MIDDLE", "HARD_FAIL"), "unexpected verdict %s" % v
        # Sanity-check the profile produced the expected band on the active N_DIM_SWEEP
        r_high_a = d["recall_at_N_high_a_disc"]
        r_high_b = d["recall_at_N_high_b_disc"]
        if r_high_a >= 0.20 or r_high_b >= 0.20:
            assert v == "META_DECISION_N_DIM_DEPENDENT", (
                "expected N_DIM_DEPENDENT given r_high_a=%.4f r_high_b=%.4f; got %s" % (
                    r_high_a, r_high_b, v))

    # T5: synthetic N-independent (flat-low at all N)
    def _profile_flat_low(N_val, sig):
        return round(max(0.001, 0.05 - 0.005 * sig), 4)
    fake_units2 = []
    for sd in (7, 17, 23):
        grid = {str(N_val): {str(sig): _profile_flat_low(N_val, sig)
                              for sig in SIGMA_SWEEP}
                for N_val in N_DIM_SWEEP}
        sanity = {str(N_val): 1.0 for N_val in N_DIM_SWEEP}
        fake_units2.append({
            "seed": sd, "grid": grid, "sanity_sigma_0": sanity,
            "M": 200, "N_DIM_sweep": N_DIM_SWEEP, "sigma_sweep": SIGMA_SWEEP,
            "N_EVAL": 200, "run_mode": "selftest", "config_version": "selftest",
        })
    v2, _, d2 = compute_verdict(fake_units2)
    if N_DIM_HIGH_B in N_DIM_SWEEP:
        # N=16384 will be flat-low (~0.04) -> expect INDEPENDENT
        assert v2 == "META_DECISION_N_INDEPENDENT", (
            "expected INDEPENDENT on flat synthetic; got %s (r_high_b=%.4f)" % (
                v2, d2.get("recall_at_N_high_b_disc", -1)))

    # T6: sanity-violation triggers HARD_FAIL
    bad_unit = {
        "seed": 99,
        "grid": {str(N_val): {str(sig): 0.5 for sig in SIGMA_SWEEP} for N_val in N_DIM_SWEEP},
        "sanity_sigma_0": {str(N_DIM_SWEEP[0]): 0.50},  # bad
        "M": 200, "N_DIM_sweep": N_DIM_SWEEP, "sigma_sweep": SIGMA_SWEEP, "N_EVAL": 200,
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
    print("[config] %s mode=%s M=%d N_DIM_sweep=%s sigma_sweep=%s N_EVAL=%d seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, M, N_DIM_SWEEP, SIGMA_SWEEP, N_EVAL, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "M": M,
               "schema": "cleanup-floor-N-DIM-scan-v1"}
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
        "M": M,
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
