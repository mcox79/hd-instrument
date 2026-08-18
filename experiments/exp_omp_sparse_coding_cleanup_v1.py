"""OMP SPARSE-CODING CLEANUP v1 -- structurally orthogonal revival of att1 HARD_FAIL.

Post att1 v1 (Ramsauer) + v2 (Krotov) HARD_FAIL, this cell tests OMP greedy sparse
recovery as a STRUCTURALLY ORTHOGONAL cleanup mechanism. att1 was softmax-fixed-point
dynamics on the same energy landscape (stayed in codebook-span); OMP explicitly tracks
a shrinking residual via least-squares projection (different operator class).

DESIGN (4 arms x 5 sigmas x 3 seeds at N=512, M=200):
  ARM ARGMAX_BASELINE: single-step argmax over D @ y (substrate baseline)
  ARM OMP_K1: OMP greedy with 1 step (should approx= argmax at sigma=0; sanity check)
  ARM OMP_K2: OMP greedy with 2 steps (k-sparse decomposition)
  ARM OMP_K4: OMP greedy with 4 steps (substrate compositional cue regime)

SIGMAS: [0.0, 0.5, 1.0, 1.5, 2.0] with discriminator at sigma=1.5

PRE-REG (from notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md):
  HARD_PASS: best_omp_lift >= +0.05 at sigma=1.5, CV <= 0.30, frac_converged = 1.0 across 3 seeds
  HARD_FAIL: best_omp_lift <= -0.005 at sigma=1.5 OR frac_converged < 0.8
  MIDDLE_BAND: lift in (-0.005, +0.05) -> route to multi-bump CAN ensemble

SANITY: OMP_K1 must match argmax within +/- 0.01 at sigma=0 (CONFOUND_FAIL otherwise).

SUBSTRATE-ONLY: n_llm_calls = 0 (HD codebook generated; no encoder).

Cites:
  - notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md
  - Tropp & Gilbert 2007 (OMP under RIP)
  - Mallat-Zhang 1993 (OMP original)
  - exp_att1_iterative_attractor_cleanup_v1 (predecessor; HARD_FAIL 2026-06-22)

Skunkworks structural blockers:
  #3 _LLM_CALL_COUNTER = [0] (substrate-only; no encoder)
  #1 per_unit per seed
  #2 cv across seeds in compute_verdict
"""
from __future__ import annotations
import sys, os, argparse, time, signal, atexit
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "omp_sparse_coding_cleanup_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (CPU-only; numpy-only)
N_DIM = 512
M = 200
N_EVAL = 200
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5
# Arms: (label, k_steps); k=0 -> argmax baseline
ARMS = [
    ("ARGMAX_BASELINE", 0),
    ("OMP_K1",          1),
    ("OMP_K2",          2),
    ("OMP_K4",          4),
]
OMP_LABELS = [a[0] for a in ARMS if a[1] > 0]
ARGMAX_LABEL = "ARGMAX_BASELINE"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    SEEDS = [0]
    N_EVAL = 50

CONFIG_VERSION = ("omp_sparse_coding_cleanup_v1; N_DIM=%d M=%d N_EVAL=%d sigmas=%s arms=%s "
                  "discriminator_sigma=%.2f seeds=%s mode=%s") % (
                      N_DIM, M, N_EVAL, SIGMA_SWEEP, [(a[0], a[1]) for a in ARMS],
                      DISCRIMINATOR_SIGMA, SEEDS, RUN_MODE)


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _build_codebook(seed, M_loc, D_loc):
    """Random Gaussian HD codebook; L2-normalized; rows = atoms."""
    g = np.random.default_rng(seed)
    cb = g.standard_normal((M_loc, D_loc)).astype(np.float32)
    return _l2_normalize(cb).astype(np.float32)


def _argmax_cleanup_batch(cues, codebook):
    """Single-step argmax over D @ y. cues: (B, D), codebook: (M, D). Return (B,) idx."""
    cb = _l2_normalize(codebook)
    cues = _l2_normalize(cues)
    scores = cues @ cb.T   # (B, M)
    return np.argmax(scores, axis=1).astype(np.int64)


def _omp_cleanup_batch(cues, codebook, k_steps):
    """OMP greedy sparse recovery; fixed-budget k_steps.

    cues: (B, D)  -- raw, NOT pre-normalized (OMP works in raw signal space)
    codebook: (M, D)  -- L2-normalized
    Returns:
        argmax_idx: (B,) int64 -- top-coefficient atom in recovered support
        frac_finite: float -- fraction of cues whose LS solve produced finite output
        residual_trace_first: list[float] -- per-step mean residual norm (for selftest)
    """
    B, D = cues.shape
    M_loc = codebook.shape[0]
    cb = _l2_normalize(codebook)            # (M, D)
    # State: residual r (B, D), selected support (B, k), coeffs x (B, k)
    r = cues.astype(np.float32).copy()
    # Track final argmax over k_steps: for each batch row we pick the support-index
    # whose absolute coefficient is largest at termination. Initialize at the first
    # selected column (matches argmax-equivalent for k=1).
    support = np.full((B, k_steps), -1, dtype=np.int64)
    coeffs = np.zeros((B, k_steps), dtype=np.float32)
    finite_mask = np.ones(B, dtype=bool)
    trace = []
    for t in range(k_steps):
        # Correlation of residual with every codebook atom: (B, M)
        corr = r @ cb.T
        # Mask out already-selected atoms so OMP picks NEW atoms
        if t > 0:
            for b in range(B):
                already = support[b, :t]
                already = already[already >= 0]
                if len(already) > 0:
                    corr[b, already] = 0.0
        new_sel = np.argmax(np.abs(corr), axis=1).astype(np.int64)  # (B,)
        support[:, t] = new_sel
        # LS-project y onto span of selected support per row.
        # Row-by-row because supports differ. With small B,k this is cheap.
        for b in range(B):
            S = support[b, : t + 1]
            S = S[S >= 0]
            if len(S) == 0:
                finite_mask[b] = False
                continue
            A = cb[S, :].T              # (D, k)
            y = cues[b]                 # (D,)
            try:
                x_b, *_ = np.linalg.lstsq(A, y, rcond=None)
            except (np.linalg.LinAlgError, ValueError):
                finite_mask[b] = False
                continue
            if not np.all(np.isfinite(x_b)):
                finite_mask[b] = False
                continue
            recon = A @ x_b            # (D,)
            r[b] = y - recon
            # store coeffs aligned with support[b, :t+1]
            for j, _idx in enumerate(S):
                coeffs[b, j] = float(x_b[j])
        mean_rnorm = float(np.mean(np.linalg.norm(r, axis=1)))
        trace.append(mean_rnorm)
    # Pick top-coefficient atom from each row's support (in abs-coeff terms)
    out_idx = np.zeros(B, dtype=np.int64)
    for b in range(B):
        S = support[b]
        valid = S >= 0
        if not valid.any() or not finite_mask[b]:
            # Fallback: argmax over correlation with original cue
            out_idx[b] = int(np.argmax(cues[b] @ cb.T))
            continue
        S_valid = S[valid]
        c_valid = coeffs[b, : len(S_valid)]
        out_idx[b] = int(S_valid[int(np.argmax(np.abs(c_valid)))])
    frac_finite = float(np.sum(finite_mask)) / max(B, 1)
    return out_idx, frac_finite, trace


def _run_arm(arm_label, k_steps, codebook, query_indices, sigma, seed):
    """Run one arm at one sigma. Returns dict."""
    g = np.random.default_rng(seed * 1000 + int(sigma * 10000) + hash(arm_label) % 1000)
    D_loc = codebook.shape[1]
    cues_clean = codebook[query_indices]
    cues = cues_clean + sigma * g.standard_normal((len(query_indices), D_loc)).astype(np.float32)
    if k_steps == 0:
        pred = _argmax_cleanup_batch(cues, codebook)
        frac_finite = 1.0
    else:
        pred, frac_finite, _trace = _omp_cleanup_batch(cues, codebook, k_steps)
    n_correct = int((pred == query_indices).sum())
    return {
        "recall_at_1": float(n_correct) / max(len(query_indices), 1),
        "frac_converged": frac_finite,
        "k_steps": k_steps,
    }


def _basin_per_arm(arm_label, k_steps, codebook, target_indices, sigmas, seed):
    out = {}
    for sig in sigmas:
        r = _run_arm(arm_label, k_steps, codebook, target_indices, sig, seed)
        out[float(sig)] = r["recall_at_1"]
    return out


def run_unit(seed):
    g = np.random.default_rng(seed)
    print("  [seed=%d] building HD codebook M=%d D=%d (substrate-native)..." % (seed, M, N_DIM), flush=True)
    t_cb = time.time()
    codebook = _build_codebook(seed, M, N_DIM)
    print("  [seed=%d] codebook built in %.2fs" % (seed, time.time() - t_cb), flush=True)
    query_idx = g.choice(M, size=min(N_EVAL, M), replace=False)
    by_arm = {}
    for arm_label, k_steps in ARMS:
        print("  [seed=%d arm=%s k_steps=%d]" % (seed, arm_label, k_steps), flush=True)
        t_arm = time.time()
        # Discriminator: sigma = DISCRIMINATOR_SIGMA
        disc = _run_arm(arm_label, k_steps, codebook, query_idx, DISCRIMINATOR_SIGMA, seed)
        # Basin: full sweep on smaller subset for speed
        basin_subset = query_idx[: min(50, len(query_idx))]
        basin = _basin_per_arm(arm_label, k_steps, codebook, basin_subset, SIGMA_SWEEP, seed)
        by_arm[arm_label] = {
            "k_steps": k_steps,
            "recall_at_1_discriminator": round(disc["recall_at_1"], 4),
            "frac_converged_discriminator": round(disc["frac_converged"], 4),
            "basin_robustness": {str(k): round(v, 4) for k, v in basin.items()},
            "wall_s": round(time.time() - t_arm, 2),
        }
        a = by_arm[arm_label]
        print("    [seed=%d arm=%s] disc=%.3f conv=%.3f basin_0=%.3f basin_1.5=%.3f (wall=%.2fs)" % (
            seed, arm_label, a["recall_at_1_discriminator"], a["frac_converged_discriminator"],
            a["basin_robustness"].get("0.0", 0.0), a["basin_robustness"].get("1.5", 0.0),
            a["wall_s"]), flush=True)
    return {
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "M": M,
        "N_EVAL": N_EVAL,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_arm_agg = {}
    arm_labels = list(units[0]["by_arm"].keys())
    for arm_label in arm_labels:
        disc_vals = [u["by_arm"][arm_label]["recall_at_1_discriminator"] for u in units]
        conv_vals = [u["by_arm"][arm_label]["frac_converged_discriminator"] for u in units]
        sigma_keys = list(units[0]["by_arm"][arm_label]["basin_robustness"].keys())
        basin_agg = {}
        for sk in sigma_keys:
            vals = [u["by_arm"][arm_label]["basin_robustness"].get(sk, 0.0) for u in units]
            basin_agg[sk] = round(float(np.mean(vals)), 4)
        dm = float(np.mean(disc_vals))
        ds = float(np.std(disc_vals))
        cv = ds / max(dm, 1e-6)
        by_arm_agg[arm_label] = {
            "recall_discriminator_mean": round(dm, 4),
            "recall_discriminator_std": round(ds, 4),
            "recall_discriminator_cv": round(cv, 4),
            "frac_converged_mean": round(float(np.mean(conv_vals)), 4),
            "basin_robustness_mean": basin_agg,
        }
    argmax_recall = by_arm_agg[ARGMAX_LABEL]["recall_discriminator_mean"]
    best_omp_arm = None
    best_omp_recall = -1.0
    best_omp_lift = -999.0
    best_omp_cv = 0.0
    best_omp_conv = 0.0
    for al in OMP_LABELS:
        rec = by_arm_agg[al]["recall_discriminator_mean"]
        lift = rec - argmax_recall
        if rec > best_omp_recall:
            best_omp_recall = rec
            best_omp_arm = al
            best_omp_lift = lift
            best_omp_cv = by_arm_agg[al]["recall_discriminator_cv"]
            best_omp_conv = by_arm_agg[al]["frac_converged_mean"]
    # OMP_K1 vs argmax at sigma=0 sanity (CONFOUND_FAIL detector)
    omp_k1_basin_0 = by_arm_agg["OMP_K1"]["basin_robustness_mean"].get("0.0", -1.0)
    argmax_basin_0 = by_arm_agg[ARGMAX_LABEL]["basin_robustness_mean"].get("0.0", -1.0)
    sanity_delta = abs(omp_k1_basin_0 - argmax_basin_0)
    sanity_ok = sanity_delta <= 0.01

    detail = {
        "by_arm_agg": by_arm_agg,
        "argmax_recall_discriminator": argmax_recall,
        "best_omp_arm": best_omp_arm,
        "best_omp_recall_discriminator": round(best_omp_recall, 4),
        "best_omp_lift_over_argmax": round(best_omp_lift, 4),
        "best_omp_cv": round(best_omp_cv, 4),
        "best_omp_frac_converged": round(best_omp_conv, 4),
        "discriminator_sigma": DISCRIMINATOR_SIGMA,
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "sanity_omp_k1_vs_argmax_at_sigma0_delta": round(sanity_delta, 4),
        "sanity_omp_k1_vs_argmax_sigma0_ok": sanity_ok,
        "honest_scope": ("HD-substrate-native OMP sparse-coding cleanup; N_DIM=%d, M=%d; "
                         "4 arms x 5 sigmas x %d seeds; cleanup-only (no encoder)" % (N_DIM, M, len(units))),
        "cites": [
            "notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md",
            "Tropp_Gilbert_2007_OMP_under_RIP",
            "Mallat_Zhang_1993_matching_pursuit",
            "exp_att1_iterative_attractor_cleanup_v1 (HARD_FAIL predecessor)",
        ],
    }
    summary = ("DISCRIMINATOR @ sigma=%.2f: argmax=%.3f | best_omp=%s recall=%.3f lift=%+.3f cv=%.3f conv=%.3f "
               "| sanity OMP_K1 vs argmax at sigma=0: delta=%.4f (ok=%s)" % (
                   DISCRIMINATOR_SIGMA, argmax_recall, best_omp_arm, best_omp_recall, best_omp_lift,
                   best_omp_cv, best_omp_conv, sanity_delta, sanity_ok))
    # CONFOUND check first
    if not sanity_ok:
        return ("CONFOUND_FAIL",
                "CONFOUND_FAIL: OMP_K1 at sigma=0 differs from argmax by %.4f > 0.01; implementation bug suspected, "
                "NOT mechanism rejection. " % sanity_delta + summary,
                detail)
    # PRE-REG bands
    if best_omp_lift >= 0.05 and best_omp_cv <= 0.30 and best_omp_conv >= 1.0 - 1e-6:
        return ("HARD_PASS",
                "DISCRIMINATOR HARD_PASS: OMP sparse-coding cleanup unblocks argmax bottleneck at sigma=%.2f; "
                "best arm %s recall=%.3f vs argmax=%.3f (lift=%+.3f >= 0.05 bar); CV=%.3f <= 0.30; "
                "frac_converged=%.3f (= 1.0 required); 3 seeds. META primitive READY for hdlab.omp_cleanup ship "
                "+ n4/n9/n10/p1 swap-in next cycle. " % (
                    DISCRIMINATOR_SIGMA, best_omp_arm, best_omp_recall, argmax_recall, best_omp_lift,
                    best_omp_cv, best_omp_conv) + summary,
                detail)
    if best_omp_lift <= -0.005 or best_omp_conv < 0.8:
        reason = "best_omp_lift <= -0.005 at sigma=%.2f (no benefit OR regression)" % DISCRIMINATOR_SIGMA \
                 if best_omp_lift <= -0.005 else "frac_converged=%.3f < 0.8 (numerical instability)" % best_omp_conv
        return ("HARD_FAIL",
                "DISCRIMINATOR HARD_FAIL: OMP sparse-coding does NOT unlock argmax cleanup; %s. "
                "Combined with att1 v1+v2 HARD_FAIL: cleanup-mechanism family REJECTED as a class for substrate "
                "regime. Pivot to encoder-side upstream (whitening / N=4096 lift). " % reason + summary,
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: OMP sparse-coding partial mechanism; best_omp_lift=%+.3f at sigma=%.2f "
            "(-0.005 < lift < +0.05 OR CV > 0.30); MEASURED_MECHANISM; route to multi-bump CAN ensemble "
            "as orthogonal-axis follow-up. " % (best_omp_lift, DISCRIMINATOR_SIGMA) + summary,
            detail)


# atexit synthesize metrics from partials
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
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT", "atexit synthesize: compute_verdict failed: %s" % e,
                                    {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "M": M,
            "N_EVAL": N_EVAL,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_omp_sparse_coding_cleanup_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


def _selftest():
    """Mechanism selftest: identity, sanity OMP_K1 vs argmax at sigma=0, residual contraction,
    LS-projection idempotency, batched shape, compute_verdict on synthetic unit."""
    g = np.random.default_rng(0)
    D_test, M_test = 64, 40
    cb = _l2_normalize(g.standard_normal((M_test, D_test)).astype(np.float32))
    # T1: zero-noise argmax recovers identity
    qidx = np.arange(8)
    cues = cb[qidx]
    pred = _argmax_cleanup_batch(cues, cb)
    assert (pred == qidx).all(), "T1 argmax zero-noise failed: %s" % pred
    # T2: zero-noise OMP_K1 must MATCH argmax exactly
    pred_omp, fc, _ = _omp_cleanup_batch(cues, cb, 1)
    pred_argmax = _argmax_cleanup_batch(cues, cb)
    delta = float(np.mean(pred_omp != pred_argmax))
    assert delta == 0.0, "T2 OMP_K1 at sigma=0 != argmax: delta=%.4f" % delta
    assert fc == 1.0, "T2 fc not 1.0: %.4f" % fc
    # T3: residual monotonically non-increasing across OMP steps
    cues_noisy = cb[qidx] + 0.3 * g.standard_normal((len(qidx), D_test)).astype(np.float32)
    _, _, trace = _omp_cleanup_batch(cues_noisy, cb, 4)
    assert len(trace) == 4
    for t in range(1, len(trace)):
        assert trace[t] <= trace[t - 1] + 1e-5, "T3 residual not contracting at step %d: %.6f -> %.6f" % (
            t, trace[t - 1], trace[t])
    # T4: LS-projection idempotency: re-project on same support yields same reconstruction
    S = np.array([3, 7], dtype=np.int64)
    A = cb[S, :].T
    y = cues_noisy[0]
    x1, *_ = np.linalg.lstsq(A, y, rcond=None)
    recon1 = A @ x1
    x2, *_ = np.linalg.lstsq(A, recon1, rcond=None)
    recon2 = A @ x2
    assert np.allclose(recon1, recon2, atol=1e-5), "T4 LS idempotency failed"
    # T5: batched shape sanity
    B = 12
    cues_b = cb[:B] + 0.1 * g.standard_normal((B, D_test)).astype(np.float32)
    pred_b, fc_b, _ = _omp_cleanup_batch(cues_b, cb, 2)
    assert pred_b.shape == (B,), "T5 shape %s" % (pred_b.shape,)
    assert fc_b > 0.5, "T5 fc too low: %.3f" % fc_b
    # T6: compute_verdict on synthetic unit (HARD_PASS shape)
    def _mk_arm(disc, conv, basin0, basin15):
        return {"k_steps": 1, "recall_at_1_discriminator": disc, "frac_converged_discriminator": conv,
                "basin_robustness": {"0.0": basin0, "0.5": basin0 - 0.05, "1.0": basin0 - 0.20,
                                     "1.5": basin15, "2.0": basin15 - 0.10},
                "wall_s": 0.01}
    u = {
        "seed": 0,
        "by_arm": {
            "ARGMAX_BASELINE": _mk_arm(0.30, 1.0, 1.0, 0.30),
            "OMP_K1":          _mk_arm(0.30, 1.0, 1.0, 0.30),  # sanity preserved
            "OMP_K2":          _mk_arm(0.42, 1.0, 1.0, 0.42),  # lift +0.12
            "OMP_K4":          _mk_arm(0.40, 1.0, 1.0, 0.40),
        },
        "N_DIM": D_test, "M": M_test, "N_EVAL": 8, "run_mode": "smoke",
        "config_version": "selftest",
    }
    v, m, d = compute_verdict([u, u, u])
    assert v == "HARD_PASS", "T6 expected HARD_PASS got %s msg=%s" % (v, m[:200])
    # T7: compute_verdict CONFOUND_FAIL when OMP_K1 sigma=0 differs from argmax
    u_bad = {
        "seed": 0,
        "by_arm": {
            "ARGMAX_BASELINE": _mk_arm(0.30, 1.0, 1.0, 0.30),
            "OMP_K1":          _mk_arm(0.30, 1.0, 0.50, 0.30),  # sanity broken: 1.0 vs 0.50
            "OMP_K2":          _mk_arm(0.45, 1.0, 1.0, 0.45),
            "OMP_K4":          _mk_arm(0.40, 1.0, 1.0, 0.40),
        },
        "N_DIM": D_test, "M": M_test, "N_EVAL": 8, "run_mode": "smoke",
        "config_version": "selftest",
    }
    v, m, d = compute_verdict([u_bad, u_bad, u_bad])
    assert v == "CONFOUND_FAIL", "T7 expected CONFOUND_FAIL got %s" % v
    # T8: compute_verdict HARD_FAIL on no-lift
    u_fail = {
        "seed": 0,
        "by_arm": {
            "ARGMAX_BASELINE": _mk_arm(0.30, 1.0, 1.0, 0.30),
            "OMP_K1":          _mk_arm(0.29, 1.0, 1.0, 0.29),
            "OMP_K2":          _mk_arm(0.28, 1.0, 1.0, 0.28),
            "OMP_K4":          _mk_arm(0.25, 1.0, 1.0, 0.25),
        },
        "N_DIM": D_test, "M": M_test, "N_EVAL": 8, "run_mode": "smoke",
        "config_version": "selftest",
    }
    v, m, d = compute_verdict([u_fail, u_fail, u_fail])
    assert v == "HARD_FAIL", "T8 expected HARD_FAIL got %s" % v
    print("[selftest] PASS: T1 argmax-identity + T2 OMP_K1==argmax@sigma=0 + T3 residual-contraction + "
          "T4 LS-idempotent + T5 batched-shape + T6 HARD_PASS + T7 CONFOUND_FAIL + T8 HARD_FAIL OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d M=%d N_EVAL=%d arms=%s sigmas=%s seeds=%s | name_says_smoke=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, N_EVAL, [a[0] for a in ARMS], SIGMA_SWEEP, SEEDS,
        _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N_DIM": N_DIM, "M": M, "N_EVAL": N_EVAL,
               "arms": [a[0] for a in ARMS], "sigmas": SIGMA_SWEEP,
               "schema": "omp-sparse-coding-cleanup-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "M": M,
        "N_EVAL": N_EVAL,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_omp_sparse_coding_cleanup_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native OMP cleanup; no encoder)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
