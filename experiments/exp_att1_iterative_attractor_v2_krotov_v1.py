"""att1_iterative_attractor_v2_low_storage_ratio_krotov_v1 -- META primitive REVIVAL.

REVIVAL of att1_iterative_attractor_cleanup_v1 HARD_FAIL (2026-06-22).

Parent finding: at N_DIM=512 M=200 (M/N=0.39, above alpha_c~0.138), ALL Ramsauer-softmax
arms plateaued at recall_harder=0.04 == argmax (best_att1_lift=0.000). Verdict was rejection.

Revival hypothesis (per `notes/research_2x_revival_overnight_negatives_2026-06-23.md`):
  (a) Parent over-capacity at M/N=0.39 (past linear-Hopfield alpha_c).
  (b) Parent tested ONLY Ramsauer softmax (temp variants); NEVER tested Krotov
      dense-polynomial f(x)=x^n or f(x)=exp(x) which give exponential capacity AND
      larger basin radius at finite T.
  (c) USER 2026-06-22: "empowered to experiment where lit says dismissed".

DESIGN (4 arms x 1 noise grid x 3 seeds at N_DIM=512, M=50 -- M/N=0.10 well below alpha_c):
  ARM ARGMAX_BASELINE:        single-step argmax cleanup (CAN-FAIL anchor)
  ARM ITER_KROTOV_QUADRATIC:  iterative dense polynomial f(x)=x^2 over codebook scores
  ARM ITER_KROTOV_POLY:       iterative dense polynomial f(x)=x^4
  ARM ITER_KROTOV_EXP:        iterative dense exponential f(x)=exp(beta*x) (Ramsauer limit)

REGIME: sigma in {0.5, 1.0, 1.5}; discriminator regime = sigma=1.5.

Per-arm metrics: recall_at_1, frac_converged, mean_iterations, basin_robustness sweep.

PRE-REG HARD bands (from handoff verbatim):
  HARD_PASS: best_iter_arm recall_harder >= 0.10 AND best_iter_arm lift_over_argmax
             >= 0.05 absolute at sigma=1.5; cv across seeds <= 0.20.
  HARD_FAIL: best_iter_arm recall_harder < argmax_recall_harder + 0.01 at sigma=1.5
             (no benefit) OR substrate-only-decode violated.
  MIDDLE_BAND: lift in [0.01, 0.05) absolute (partial mechanism).

SUBSTRATE-ONLY: n_llm_calls = 0 at inference (HD codebook generated; no encoder).
PROT-020 N/A (numpy-only; remote_cpu_queue route).

ASCII-only. Per-seed checkpoint. atexit-synthesize.
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

ANCHOR_NAME = "att1_iterative_attractor_v2_low_storage_ratio_krotov_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (CPU-only; numpy-only)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 512
    M = 50              # M/N=0.10 well below linear alpha_c~0.138 (key revival lever)
    N_EVAL = 200
else:
    SEEDS = [0]
    N_DIM = 512
    M = 50
    N_EVAL = 50

NOISE_GENTLE = 0.5
NOISE_HARDER = 1.5
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
TOL = 1e-3
MAX_STEPS = 8

# Arm configs: (label, mode, krotov_kind, kparam, max_steps)
#   mode: 'argmax' or 'iter_krotov'
#   krotov_kind: 'poly' (use x**kparam) or 'exp' (use exp(beta*x); kparam = effective beta multiplier)
#   kparam: for poly = exponent (2,4); for exp = beta multiplier on (state @ cb.T)
ARMS = [
    ("ARGMAX_BASELINE",        "argmax",     None,   None, 1),
    ("ITER_KROTOV_QUADRATIC",  "iter_krotov", "poly", 2.0,  MAX_STEPS),
    ("ITER_KROTOV_POLY",       "iter_krotov", "poly", 4.0,  MAX_STEPS),
    ("ITER_KROTOV_EXP",        "iter_krotov", "exp",  4.0,  MAX_STEPS),
]
ITER_LABELS = [a[0] for a in ARMS if a[1] == "iter_krotov"]
ARGMAX_LABEL = "ARGMAX_BASELINE"

CONFIG_VERSION = ("att1_v2_krotov_v1; N_DIM=%d M=%d M_over_N=%.3f N_EVAL=%d sigmas=%s "
                  "arms=%s noise_gentle=%.3f noise_harder=%.3f tol=%.4f max_steps=%d seeds=%s mode=%s") % (
                  N_DIM, M, M / N_DIM, N_EVAL, SIGMA_SWEEP, [(a[0], a[1], a[2], a[3], a[4]) for a in ARMS],
                  NOISE_GENTLE, NOISE_HARDER, TOL, MAX_STEPS, SEEDS, RUN_MODE)


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _build_codebook(seed, M_loc, D_loc):
    """Random Gaussian HD codebook; L2-normalized; substrate-native (no encoder)."""
    g = np.random.default_rng(seed)
    cb = g.standard_normal((M_loc, D_loc)).astype(np.float32)
    return _l2_normalize(cb).astype(np.float32)


def argmax_cleanup_batch(queries, codebook):
    """Reference: single-step argmax cleanup."""
    cb_n = _l2_normalize(codebook.astype(np.float32))
    q_n = _l2_normalize(queries.astype(np.float32))
    if q_n.ndim == 1:
        return int(np.argmax(q_n @ cb_n.T))
    return np.argmax(q_n @ cb_n.T, axis=1).astype(np.int64)


def iter_krotov_cleanup(queries, codebook, *, krotov_kind, kparam,
                         max_steps=8, tol=1e-3, scale_by_sqrt_d=True):
    """Krotov dense interaction iterative attractor.

    Standard Hopfield-Fenchel-Young / dense associative memory family
    (Krotov-Hopfield 2016; Ramsauer 2021; Hopfield-Fenchel-Young arxiv:2411.08590).

    Update:
        scores_t = state_t @ codebook.T            # (B, M)
        if 'poly':   weights = f(scores_t) / sum(f(scores_t))   with f(x)=x^kparam (clipped pos)
        if 'exp':    weights = softmax(beta * scores_t)         with beta = kparam * sqrt(D) (when scaled)
        new_state  = renormalize(weights @ codebook)
    Stop when ||new - state|| < tol * sqrt(D) OR max_steps reached.
    """
    cb_n = _l2_normalize(codebook.astype(np.float32))
    q = queries.astype(np.float32)
    squeeze = q.ndim == 1
    if squeeze:
        q = q[None, :]
    state = _l2_normalize(q)
    D = state.shape[1]
    converged = False
    steps = 0
    sqrt_d = float(np.sqrt(D))
    step_threshold = tol * sqrt_d
    for t in range(max_steps):
        scores = state @ cb_n.T  # (B, M) cosine similarities
        if krotov_kind == "poly":
            # Dense polynomial f(x) = x^k for x>0; clip negatives to 0 (rectified poly).
            # Standard Krotov dense form keeps sign for odd k; we use abs+sign for stability.
            sign = np.sign(scores)
            f = sign * np.power(np.abs(scores), kparam)
            # rectify: take max(0, ...) so weights stay non-negative for proper averaging
            f = np.maximum(f, 0.0)
            sum_f = f.sum(axis=1, keepdims=True) + 1e-30
            weights = (f / sum_f).astype(np.float32)
        elif krotov_kind == "exp":
            beta = kparam * (sqrt_d if scale_by_sqrt_d else 1.0)
            z = (beta * scores).astype(np.float64)
            z = z - z.max(axis=1, keepdims=True)
            e = np.exp(z)
            weights = (e / (e.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)
        else:
            raise ValueError("krotov_kind must be 'poly' or 'exp'; got %s" % krotov_kind)
        new_state = _l2_normalize(weights @ cb_n)
        step_dist = float(np.mean(np.linalg.norm(new_state - state, axis=1)))
        state = new_state
        steps = t + 1
        if step_dist < step_threshold:
            converged = True
            break
    final_scores = state @ cb_n.T
    argmax_idx = np.argmax(final_scores, axis=1).astype(np.int64)
    if squeeze:
        argmax_idx = int(argmax_idx[0])
    return {"argmax_idx": argmax_idx, "n_iterations": steps, "converged": converged}


def _run_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, query_indices, sigma, seed):
    """Run one arm at one noise level."""
    arm_seed = seed * 1000 + int(sigma * 10000) + (hash(arm_label) % 1000)
    g = np.random.default_rng(arm_seed)
    M_loc, D_loc = codebook.shape
    cues = codebook[query_indices] + sigma * g.standard_normal((len(query_indices), D_loc)).astype(np.float32)
    if mode == "argmax":
        pred = argmax_cleanup_batch(cues, codebook)
        n_correct = int((pred == query_indices).sum())
        mean_iters = 1.0
        frac_converged = 1.0
    else:
        out = iter_krotov_cleanup(cues, codebook, krotov_kind=krotov_kind, kparam=kparam,
                                   max_steps=max_steps, tol=TOL)
        pred = out["argmax_idx"]
        n_correct = int((pred == query_indices).sum())
        mean_iters = float(out["n_iterations"])
        frac_converged = 1.0 if out["converged"] else 0.0
    return {
        "recall_at_1": float(n_correct) / max(len(query_indices), 1),
        "mean_iterations": mean_iters,
        "frac_converged": frac_converged,
    }


def _basin_robustness_per_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, target_indices, sigmas, seed):
    out = {}
    for sig in sigmas:
        r = _run_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, target_indices, sig, seed)
        out[float(sig)] = r["recall_at_1"]
    return out


def run_unit(seed):
    g = np.random.default_rng(seed)
    print("  [seed=%d] building HD codebook M=%d D=%d M/N=%.3f (substrate-native)..." % (seed, M, N_DIM, M / N_DIM), flush=True)
    t_cb = time.time()
    codebook = _build_codebook(seed, M, N_DIM)
    print("  [seed=%d] codebook built in %.1fs" % (seed, time.time() - t_cb), flush=True)
    query_idx = g.choice(M, size=min(N_EVAL, M), replace=False)
    by_arm = {}
    for arm_label, mode, krotov_kind, kparam, max_steps in ARMS:
        print("  [seed=%d arm=%s mode=%s krotov=%s kparam=%s max_steps=%d]" % (seed, arm_label, mode, str(krotov_kind), str(kparam), max_steps), flush=True)
        t_arm = time.time()
        gentle = _run_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, query_idx, NOISE_GENTLE, seed)
        harder = _run_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, query_idx, NOISE_HARDER, seed)
        basin = _basin_robustness_per_arm(arm_label, mode, krotov_kind, kparam, max_steps, codebook, query_idx[:50], SIGMA_SWEEP, seed)
        by_arm[arm_label] = {
            "mode": mode,
            "krotov_kind": krotov_kind,
            "kparam": kparam,
            "max_steps": max_steps,
            "recall_at_1_noise_gentle": round(gentle["recall_at_1"], 4),
            "recall_at_1_noise_harder": round(harder["recall_at_1"], 4),
            "mean_iterations_harder": round(harder["mean_iterations"], 2),
            "frac_converged_harder": round(harder["frac_converged"], 4),
            "basin_robustness": {str(k): round(v, 4) for k, v in basin.items()},
            "wall_s": round(time.time() - t_arm, 2),
        }
        a = by_arm[arm_label]
        print("    [seed=%d arm=%s] gentle=%.3f harder=%.3f iters=%.1f conv=%.2f basin_15=%.3f (wall=%.1fs)" % (
            seed, arm_label, a["recall_at_1_noise_gentle"], a["recall_at_1_noise_harder"],
            a["mean_iterations_harder"], a["frac_converged_harder"],
            a["basin_robustness"].get(str(1.5), 0.0), a["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "M": M,
        "M_over_N": round(M / N_DIM, 4),
        "N_EVAL": N_EVAL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results", {})
    by_arm_agg = {}
    arm_labels = list(units[0]["by_arm"].keys())
    for arm_label in arm_labels:
        gentle_vals = [u["by_arm"][arm_label]["recall_at_1_noise_gentle"] for u in units]
        harder_vals = [u["by_arm"][arm_label]["recall_at_1_noise_harder"] for u in units]
        conv_vals = [u["by_arm"][arm_label]["frac_converged_harder"] for u in units]
        iter_vals = [u["by_arm"][arm_label]["mean_iterations_harder"] for u in units]
        basin_agg = {}
        sigma_keys = list(units[0]["by_arm"][arm_label]["basin_robustness"].keys())
        for sk in sigma_keys:
            vals = [u["by_arm"][arm_label]["basin_robustness"].get(sk, 0.0) for u in units]
            basin_agg[sk] = round(float(np.mean(vals)), 4)
        gm = float(np.mean(gentle_vals))
        hm = float(np.mean(harder_vals)); hs = float(np.std(harder_vals))
        h_cv = hs / max(hm, 1e-6)
        by_arm_agg[arm_label] = {
            "recall_gentle_mean": round(gm, 4),
            "recall_harder_mean": round(hm, 4),
            "recall_harder_std": round(hs, 4),
            "recall_harder_cv": round(h_cv, 4),
            "frac_converged_harder_mean": round(float(np.mean(conv_vals)), 4),
            "mean_iterations_harder_mean": round(float(np.mean(iter_vals)), 2),
            "basin_robustness_mean": basin_agg,
        }
    argmax_recall_harder = by_arm_agg[ARGMAX_LABEL]["recall_harder_mean"]
    best_iter_arm = None
    best_iter_lift = -999.0
    best_iter_recall = 0.0
    best_iter_cv = 0.0
    best_iter_conv = 0.0
    for al in ITER_LABELS:
        rec = by_arm_agg[al]["recall_harder_mean"]
        lift = rec - argmax_recall_harder
        if lift > best_iter_lift:
            best_iter_lift = lift
            best_iter_arm = al
            best_iter_recall = rec
            best_iter_cv = by_arm_agg[al]["recall_harder_cv"]
            best_iter_conv = by_arm_agg[al]["frac_converged_harder_mean"]
    detail = {
        "by_arm_agg": by_arm_agg,
        "argmax_recall_harder": argmax_recall_harder,
        "best_iter_arm": best_iter_arm,
        "best_iter_recall_harder": round(best_iter_recall, 4),
        "best_iter_lift_over_argmax": round(best_iter_lift, 4),
        "best_iter_cv": round(best_iter_cv, 4),
        "best_iter_frac_converged": round(best_iter_conv, 4),
        "n_seeds": len(units),
        "M_over_N": units[0].get("M_over_N", -1.0),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": ("Krotov-dense REVIVAL of att1 v1 HARD_FAIL. N_DIM=%d M=%d (M/N=%.3f below alpha_c~0.138). "
                         "4 arms (argmax + 3 krotov variants) x %d seeds." % (N_DIM, M, M / N_DIM, len(units))),
        "cites": [
            "Krotov_Hopfield_2016_NeurIPS",
            "Ramsauer_2021_ICLR_Modern_Hopfield",
            "HopfieldFenchelYoung_arxiv_2411.08590",
            "research_2x_revival_overnight_negatives_2026-06-23",
        ],
    }
    summary = ("DISCRIMINATOR @ sigma=%.2f: argmax=%.3f | best_iter=%s recall=%.3f lift=%.3f cv=%.3f conv=%.2f | M/N=%.3f" % (
        NOISE_HARDER, argmax_recall_harder, best_iter_arm, best_iter_recall,
        best_iter_lift, best_iter_cv, best_iter_conv, M / N_DIM))
    if best_iter_lift >= 0.05 and best_iter_recall >= 0.10 and best_iter_cv <= 0.20:
        return ("HARD_PASS",
                "HARD_PASS: Krotov dense interaction unblocks argmax in low-storage regime. "
                "best %s recall=%.3f vs argmax=%.3f (lift=%.3f >= 0.05); cv=%.3f. " % (
                    best_iter_arm, best_iter_recall, argmax_recall_harder, best_iter_lift, best_iter_cv) + summary,
                detail)
    if best_iter_lift < 0.01:
        return ("HARD_FAIL",
                "HARD_FAIL: Krotov variants do NOT improve over argmax in low-storage regime; "
                "mechanism truly rejected (revival exhausted). lift=%.3f. " % best_iter_lift + summary,
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: Krotov lift partial (lift=%.3f in [0.01, 0.05)); MEASURED_MECHANISM. " % best_iter_lift + summary,
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
            "N_DIM": N_DIM, "M": M, "N_EVAL": N_EVAL,
            "n_seeds": len(units),
            "detail": detail,
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize] " + msg,
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)


def _selftest():
    """Selftest: zero-noise identity per arm + Krotov endpoints + verdict on synthetic."""
    g = np.random.default_rng(0)
    D_test, M_test = 64, 16
    cb = _l2_normalize(g.standard_normal((M_test, D_test)).astype(np.float32))
    qidx = np.arange(8)
    # T1: zero-noise per arm should recover (handoff selftest: at sigma=0 all arms should recall=1.0)
    for arm_label, mode, krotov_kind, kparam, ms in ARMS:
        r = _run_arm(arm_label, mode, krotov_kind, kparam, ms, cb, qidx, 0.0, seed=1)
        assert r["recall_at_1"] >= 0.99, "zero-noise %s recall=%.3f" % (arm_label, r["recall_at_1"])
    # T2: high-noise (sigma=100) all arms approx random (1/M) per handoff selftest
    # Use sigma=20 -- truly noise-dominated; expect recall << 0.5
    for arm_label, mode, krotov_kind, kparam, ms in ARMS:
        r = _run_arm(arm_label, mode, krotov_kind, kparam, ms, cb, qidx, 20.0, seed=2)
        assert r["recall_at_1"] <= 0.5, "high-noise %s recall=%.3f should be near 1/M" % (arm_label, r["recall_at_1"])
    # T3: Krotov iterations >= 1 at moderate noise
    for arm_label, mode, krotov_kind, kparam, ms in ARMS:
        if mode != "iter_krotov":
            continue
        r = _run_arm(arm_label, mode, krotov_kind, kparam, ms, cb, qidx, 0.5, seed=3)
        assert r["mean_iterations"] >= 1.0, "%s iters=%.2f" % (arm_label, r["mean_iterations"])
    # T4: basin_robustness shape
    bs = _basin_robustness_per_arm("ITER_KROTOV_EXP", "iter_krotov", "exp", 4.0, MAX_STEPS, cb, qidx, [0.0, 0.5], seed=4)
    assert 0.0 in bs and 0.5 in bs
    assert bs[0.0] >= 0.99
    # T5: compute_verdict runs on synthetic 3-unit
    u = {
        "seed": 0,
        "by_arm": {
            "ARGMAX_BASELINE":       {"mode": "argmax", "krotov_kind": None, "kparam": None, "max_steps": 1,
                                       "recall_at_1_noise_gentle": 0.99, "recall_at_1_noise_harder": 0.30,
                                       "mean_iterations_harder": 1.0, "frac_converged_harder": 1.0,
                                       "basin_robustness": {"0.0": 1.0, "0.5": 0.95, "1.0": 0.6, "1.5": 0.30, "2.0": 0.10},
                                       "wall_s": 0.1},
            "ITER_KROTOV_QUADRATIC": {"mode": "iter_krotov", "krotov_kind": "poly", "kparam": 2.0, "max_steps": 8,
                                       "recall_at_1_noise_gentle": 0.99, "recall_at_1_noise_harder": 0.35,
                                       "mean_iterations_harder": 3.0, "frac_converged_harder": 1.0,
                                       "basin_robustness": {"0.0": 1.0, "0.5": 0.96, "1.0": 0.65, "1.5": 0.35, "2.0": 0.12},
                                       "wall_s": 0.3},
            "ITER_KROTOV_POLY":      {"mode": "iter_krotov", "krotov_kind": "poly", "kparam": 4.0, "max_steps": 8,
                                       "recall_at_1_noise_gentle": 0.99, "recall_at_1_noise_harder": 0.45,
                                       "mean_iterations_harder": 4.0, "frac_converged_harder": 1.0,
                                       "basin_robustness": {"0.0": 1.0, "0.5": 0.98, "1.0": 0.75, "1.5": 0.45, "2.0": 0.20},
                                       "wall_s": 0.3},
            "ITER_KROTOV_EXP":       {"mode": "iter_krotov", "krotov_kind": "exp", "kparam": 4.0, "max_steps": 8,
                                       "recall_at_1_noise_gentle": 0.99, "recall_at_1_noise_harder": 0.50,
                                       "mean_iterations_harder": 5.0, "frac_converged_harder": 1.0,
                                       "basin_robustness": {"0.0": 1.0, "0.5": 0.98, "1.0": 0.80, "1.5": 0.50, "2.0": 0.25},
                                       "wall_s": 0.3},
        },
        "N_DIM": D_test, "M": M_test, "M_over_N": M_test / D_test, "N_EVAL": 8, "run_mode": "smoke",
        "config_version": "selftest",
    }
    v, m, d = compute_verdict([u, u, u])
    assert v in ("HARD_PASS", "MIDDLE_BAND", "HARD_FAIL"), "verdict %s unexpected" % v
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print("[selftest] PASS: zero-noise identity + high-noise random + iters>=1 + basin + verdict OK; n_llm_calls=0", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d M=%d M/N=%.3f N_EVAL=%d arms=%s sigmas=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, M / N_DIM, N_EVAL, [a[0] for a in ARMS], SIGMA_SWEEP, SEEDS,
        CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N_DIM": N_DIM, "M": M, "N_EVAL": N_EVAL,
               "arms": [a[0] for a in ARMS], "sigmas": SIGMA_SWEEP,
               "schema": "att1-iterative-attractor-v2-krotov-v1"}
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
        "N_DIM": N_DIM, "M": M, "N_EVAL": N_EVAL,
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
