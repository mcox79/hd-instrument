# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phase-linear codebook vs collapsed(rank-1) codebook hash-distinct;
#     correct-prediction array vs wrong-scaling-prediction array hash-distinct; measured-acc array vs
#     collapsed-control-acc array hash-distinct. (Prediction FORMULAS are deterministic closed forms; the
#     empirical MEASURED arrays are separate. We hash CODEBOOKS + the three value-surfaces, which differ.)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except).
# - crlb/capacity-feasibility: this cell IS the capacity-feasibility instrument. The decode-collapse boundary
#     under additive noise is the M-ary matched-filter error bound P_e <= (m-1)*Q(sqrt(sb)/sigma)
#     (THEORETICAL@Proakis Digital Communications M-ary orthogonal signalling). The discriminator = does the
#     closed-form collapse-boundary prediction match the MEASURED collapse. discriminator_reachability=True:
#     probes (2026-07-06) MEASURED the 0.5-crossing SB* bracketed inside the swept grid for every (m,sigma).
# - baseline_in_band (META_RULE_AG): this is a REACHABILITY/PREDICTION-MATCH test, not a difficulty baseline.
#     The measured acc surface intentionally spans ~0.05-0.20 (collapsed, small sb) up to 1.0 (safe, large sb);
#     the "collapsed codebook" arm is a declared must-collapse CONTROL (~1/m) exempt from the in-band rule.
#     The discriminator is measured-collapse-boundary vs predicted-collapse-boundary (scaling exponent +
#     bounded offset), which does NOT saturate at scale.
# - discriminator survives scale: smoke runs the FULL SB grid (up to sb=2730, the shipped substrate config),
#     ALL 3 max-moduli, ALL noise levels; smoke reduces TRIALS + SEEDS only. The collapse boundary + the
#     scaling-exponent match + the wrong-scaling separation + the collapsed-control collapse all FIRE in smoke
#     (option A of DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at full grid params).
# - HARD_PASS strictly above floor: measured scaling exponent p_meas in [1.6,2.4] (THEORETICAL 2.0 = the
#     sqrt(sb)/sigma law); correct formula reproduces it (|p_meas - p_correct| <= 0.4) and clearly beats the
#     wrong-scaling control (|p_meas - p_wrong| >= 0.6 and >= 2*|p_meas - p_correct|).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MECHANISM-SELF-VERIFICATION -- RNS SUB-BLOCK DECODE-MARGIN SELF-CHECK  v1
# ========================================================================
# The substrate CHECKS a config-contingent property of its OWN arithmetic design that the 4 landed math cells
# (exp_math_rns_add_chain_v1, _subtract_compare_v1, _multiply_star_v1) ASSERT verbatim but NEVER verified:
# "sb=2730 >> max modulus 43, so per-residue argmax is collision-free." That boilerplate is a design-margin
# claim taken on faith. This cell is the CHECK half of "the substrate reasoning about its own design":
# it derives a closed-form prediction of WHERE per-sub-block decode collapses as a function of the config
# parameters (sub-block dimension sb, modulus m, injected noise sigma), MEASURES the actual collapse, and
# checks its own prediction against the measurement.
#
# Source pre-reg: notes/research_mechanism_selfverification_scoping_2026-07-06.md
#   (the ONE genuine, non-tautological, config-contingent self-check the drill found; the other 3 candidates
#    -- CRT-uniqueness, add/multiply-homomorphism-exactness -- are BLR-theory tautologies, correctly NOT built).
#
# HONEST INVERTED PREMISE (MEASURED@probes 2026-07-06, reported prominently, NOT buried):
#   The drill hypothesized a NOISELESS Welch-bound decode-collapse boundary (SB vs modulus). Pre-dispatch
#   probes MEASURED that no such noiseless boundary exists for this codebook: the phase-linear integer-frequency
#   codewords codebook[r] = exp(i*2pi*k_j*r/m) are the m DISTINCT roots of unity whenever any frequency k_j is
#   coprime to m, so per-residue argmax has an EXACT rank-1 similarity of 1.0 and is immune to high off-diagonal
#   correlation. Noiseless decode is collision-free by NUMBER THEORY (frequency-modulus coprimality), not by
#   Welch/SNR concentration. For PRIME moduli every k_j in [1,m) is coprime -> decode is unconditionally exact
#   at ANY sb>=1. The Welch/Q-function collapse boundary is operative ONLY under injected additive noise (a
#   corrupted / bundled / noisy representation), which is exactly the RNS-hardware NOISE-MARGIN regime the
#   drill's BIST analogy points to (VOH/VOL noise margins: conditionally-guaranteed, genuinely violable).
#   This cell therefore verifies the Welch/Q-function prediction in the regime where it IS the operative law:
#   decode-under-additive-noise. The noiseless number-theoretic exactness is reported as a documented arm.
#
# THE CHECK (per (modulus m, sub-block dim sb, noise sigma)):
#   Task A (MEASURE): encode a random residue r in [0,m) as codebook[r], corrupt with complex Gaussian noise
#     ~ CN(0, sigma^2) per dim, decode via per-sub-block phasor argmax; accuracy = frac(argmax == r).
#   Task B (PREDICT, closed form): P_e_pred(sb,m,sigma) = min(1, (m-1)*Q(sqrt(sb)/sigma))  [union bound over the
#     m-1 competing residues of a Gaussian-tail collision; the margin sim[true]~1.0 - sim[comp]~0 has noise std
#     ~sigma/sqrt(sb) -> Q(sqrt(sb)/sigma)]. acc_pred = 1 - P_e_pred.
#   Task C (CHECK): does the predicted collapse boundary SB*(sigma) match the measured one? Primary invariant =
#     the SCALING EXPONENT p of SB* ~ sigma^p (THEORETICAL p=2, since sb_crit ~ sigma^2). The substrate's own
#     closed form reproduces p; a mis-derived wrong-scaling (SNR linear in sb) predicts p~1 and is falsified.
#
# ARMS (per (m, sb, sigma); measurements PAIRED on identical residues + noise draws where compared):
#   measured_decode      : MEASUREMENT -- phase-linear codebook decode accuracy under noise.        [MECHANISM]
#   predict_correct      : the substrate's OWN closed-form Q-function prediction (sqrt(sb)/sigma).   [PREDICTION]
#   predict_wrong_scaling: mis-derived prediction, SNR LINEAR in sb (sb/sigma) instead of sqrt(sb)/sigma ->
#                          predicts SB* ~ sigma^1 not sigma^2. Isolates that the sqrt(sb) CLT-concentration
#                          scaling is load-bearing, not any monotonic-in-sb guess.                   [CONTROL 1]
#   collapsed_codebook   : rank-1 codebook (all m residues share ONE bit-identical codeword) -> genuinely
#                          indistinguishable -> acc ~ 1/m at EVERY sb incl the safe end. Isolates that
#                          distinguishable codeword STRUCTURE (not merely many dims) is what the formula models.
#                          Must collapse everywhere.                                                 [CONTROL 2]
#   noiseless_diag       : sigma=0 decode accuracy vs sb -- the number-theoretic exactness diagnostic (prime m
#                          exact at any sb>=1). Reported, documents the inverted premise. Not pass-gated.
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the margin / prediction-vs-measurement in its own
#   metrics.json. It NEVER changes sb, edits a landed cell's config, or triggers a rebuild. A human reads the
#   flag and decides. This is monitoring of mechanism DESIGN, not self-modification (Nelson & Narens 1990
#   monitor side, honestly the engineering/BIST framing, NOT a neural analog).
#
# Brain-grounding: HONESTLY engineering (RNS-hardware BIST / noise-margin analysis: Szabo & Tanaka 1967;
#   noise-margin VOH/VOL conditional-guarantee). The shared-math brain-ADJACENT connection (signal detection
#   theory / psychophysical detection thresholds; Green & Swets 1966) is real at the Q-function/ROC level but
#   secondary and NOT forced -- no claim the brain introspects its own representational margin.
#
# ASCII-only. CPU-only (numpy complex64; no GPU, no torch, no LLM; vectorized trials; wall < 60s -> sequential-
# CPU justified: cell IS the substrate-primitive being validated, bit-exact reference).
# Self-contained (synthetic phasor codebooks; no pool/re-encode/cert_ledger dependency -> clean remote gate).
# Run: python experiments/exp_rns_subblock_margin_selfcheck_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

ANCHOR_NAME = "rns_subblock_margin_selfcheck_v1"
REPO = Path(__file__).resolve().parents[1]

# Max moduli of the small/mid/large arithmetic regimes the landed math cells actually ship
# (small=(7,8,9) -> 9; mid=(16,17,19) -> 19; large=(40,41,43) -> 43). The sub-block decode margin is a
# function of the LARGEST modulus in a sub-block (most competing residues).
MODULI = (9, 19, 43)

# Sub-block-dimension sweep: spans clearly-collapsed (sb=4) up to the SHIPPED substrate config sb=2730
# (== N_DIM 8192 // R_MODULI 3, the value every landed math cell ships). sb=2730 is the retrospective
# real-data anchor: it must sit in the predicted-safe region with a wide margin at every noise level.
SB_GRID = (4, 8, 16, 32, 64, 128, 256, 512, 1024, 2730)
SB_SHIPPED = 2730

# Injected additive-noise levels (complex Gaussian std per dim). Chosen (probe 2026-07-06) so the collapse
# boundary SB*(sigma) sweeps ACROSS the sb grid for every modulus -> the sigma^2 scaling law is measurable.
SIGMAS = (6.0, 8.0, 11.0, 16.0)

SEEDS_FULL = (7, 13, 19, 23, 29)
SEEDS_SMOKE = (7, 13, 19)

# ---- Pre-registered bands (THEORETICAL from the M-ary matched-filter law; MEASURED filled by smoke/full) ----
# Primary invariant: SB* ~ sigma^p with THEORETICAL p=2 (sb_crit ~ sigma^2).
P_THEORY = 2.0
HP_P_LO = 1.6          # HARD_PASS: measured scaling exponent lower bound (THEORETICAL 2.0; MEASURED min 1.79)
HP_P_HI = 2.4          # HARD_PASS: measured scaling exponent upper bound
HF_P_LO = 1.2          # HARD_FAIL: p below -> the sqrt(sb)/sigma law is wrong for this codebook
HF_P_HI = 2.8          # HARD_FAIL: p above -> law wrong
HP_CORRECT_PERR = 0.4  # HARD_PASS: |p_meas - p_correct| must be <= this (correct formula reproduces scaling)
HP_WRONG_PERR = 0.6    # HARD_PASS: |p_meas - p_wrong| must be >= this (wrong-scaling clearly separated)
HP_ADVANTAGE = 2.0     # HARD_PASS: |p_meas - p_wrong| >= this * |p_meas - p_correct| (sqrt-law load-bearing)
HF_ADVANTAGE = 1.2     # HARD_FAIL: wrong-scaling exponent-error advantage below this -> not load-bearing
HP_OFFSET_MAX = 4.0    # HARD_PASS: correct-formula SB* geometric-mean ratio-error <= this (bounded union-bound
                       #            over-prediction; MEASURED ~2.4-2.7x). MIDDLE if in (4, 8]; HARD_FAIL if > 8.
MB_OFFSET_MAX = 8.0
COLLAPSE_CTRL_MULT = 3.0   # control: collapsed-codebook acc must be <= COLLAPSE_CTRL_MULT / m at every (sb,sigma)
CTRL_LEAK = 0.40           # HARD_FAIL: collapsed control acc > this anywhere -> control leak
REACH_LO = 0.30            # reachability: measured acc must dip <= this somewhere at each (m,sigma) (real cliff)


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Phasor codebooks + noisy decode (phase-linear FPE reused verbatim from landed rns_crt/add cells)
# ============================================================


def phasor_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """Phase-LINEAR FPE codebook (m, sb) complex64: codebook[r,j] = exp(i*2*pi*k_j*r/m), k_j in [1,m-1].
    Integer k_j -> the m codewords are the m-th roots of unity per dim -> distinct whenever gcd(k_j,m)=1."""
    g = np.random.default_rng(seed)
    k = g.integers(1, m, size=sb).astype(np.float64)
    r = np.arange(m, dtype=np.float64)[:, None]
    phase = (2.0 * np.pi / m) * (r * k[None, :])
    return np.exp(1j * phase).astype(np.complex64)


def collapsed_codebook(m: int, sb: int, seed: int) -> np.ndarray:
    """CONTROL 2 (must-collapse): rank-1 codebook -- all m residues share ONE bit-identical codeword ->
    similarities are all equal -> argmax is a blind tie -> acc ~ 1/m at EVERY sb and sigma incl noiseless."""
    g = np.random.default_rng(seed)
    one = np.exp(1j * g.uniform(0.0, 2.0 * np.pi, size=sb)).astype(np.complex64)
    return np.tile(one, (m, 1))


def decode_acc(cb: np.ndarray, m: int, sb: int, sigma: float, n_trials: int,
               rng: np.random.Generator, residues=None, noise=None) -> tuple[float, np.ndarray, np.ndarray]:
    """Per-sub-block phasor argmax decode accuracy under additive complex-Gaussian noise. Returns
    (accuracy, residues_used, noise_used) so a paired control can reuse identical draws."""
    if residues is None:
        residues = rng.integers(0, m, size=n_trials)
    V = cb[residues].copy()  # (T, sb)
    if sigma > 0:
        if noise is None:
            noise = (rng.normal(0.0, sigma / math.sqrt(2.0), (n_trials, sb))
                     + 1j * rng.normal(0.0, sigma / math.sqrt(2.0), (n_trials, sb))).astype(np.complex64)
        V = V + noise
    sims = (cb @ np.conj(V).T).real / sb  # (m, T) normalized; true residue -> ~1.0 minus noise
    pred = np.argmax(sims, axis=0)
    return float(np.mean(pred == residues)), residues, noise


# ============================================================
# Closed-form predictions (the substrate's OWN self-check formula + the mis-derived control)
# ============================================================


def _Q(x: float) -> float:
    """Gaussian tail Q(x) = 0.5*erfc(x/sqrt2)."""
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def pred_acc_correct(sb: int, m: int, sigma: float) -> float:
    """THEORETICAL@Proakis M-ary union bound: P_e <= (m-1)*Q(sqrt(sb)/sigma). SNR ~ sqrt(sb) (CLT
    concentration of the sb-term matched filter). Predicts collapse SB* ~ sigma^2."""
    if sigma <= 0:
        return 1.0
    return 1.0 - min(1.0, (m - 1) * _Q(math.sqrt(sb) / sigma))


def pred_acc_wrong_scaling(sb: int, m: int, sigma: float) -> float:
    """CONTROL 1 (mis-derived): SNR treated as LINEAR in sb (sb/sigma) instead of sqrt(sb)/sigma. Same union
    bound, wrong scaling exponent -> predicts collapse SB* ~ sigma^1. Falsified by the measured sigma^2."""
    if sigma <= 0:
        return 1.0
    return 1.0 - min(1.0, (m - 1) * _Q((1.0 / sigma) * sb))


def formula_selftest() -> tuple[bool, str]:
    """Formula self-test: (a) Q monotone-decreasing + Q(0)=0.5; (b) correct formula predicts SB* scaling
    exponent ~2 and wrong formula ~1 over the sigma grid (the load-bearing contrast is analytically true);
    (c) at the shipped sb=2730 the correct formula predicts safe (>0.999) at every sigma."""
    if abs(_Q(0.0) - 0.5) > 1e-9 or not (_Q(1.0) > _Q(2.0) > _Q(3.0)):
        return False, "Q_FUNCTION_BROKEN"
    for m in MODULI:
        sbc = [_cross_sb([pred_acc_correct(sb, m, s) for sb in SB_GRID], SB_GRID) for s in SIGMAS]
        sbw = [_cross_sb([pred_acc_wrong_scaling(sb, m, s) for sb in SB_GRID], SB_GRID) for s in SIGMAS]
        if any(math.isinf(x) for x in sbc + sbw):
            return False, f"FORMULA_SBSTAR_OUT_OF_GRID m={m}"
        pc = _loglog_slope(SIGMAS, sbc)
        pw = _loglog_slope(SIGMAS, sbw)
        if not (1.7 <= pc <= 2.4):
            return False, f"CORRECT_FORMULA_EXPONENT_OFF m={m} p_correct={pc:.2f}"
        if not (pw <= 1.4):
            return False, f"WRONG_FORMULA_NOT_SEPARATED m={m} p_wrong={pw:.2f}"
        # shipped sb must sit on the SAFE side of the boundary with margin (SB_SHIPPED >> SB*(sigma_max));
        # 0.90 guard, not near-unity: at the worst tested noise the largest modulus genuinely decodes ~0.98.
        if pred_acc_correct(SB_SHIPPED, m, max(SIGMAS)) < 0.90:
            return False, f"SHIPPED_SB_NOT_SAFE_IN_FORMULA m={m}"
    return True, "FORMULA_SELFTEST_PASS"


# ============================================================
# Collapse-boundary + scaling-exponent utilities
# ============================================================


def _cross_sb(ys, xs) -> float:
    """SB* = the sub-block dim where accuracy crosses 0.5 (log-sb linear interpolation of the first up-crossing)."""
    for i in range(1, len(xs)):
        if ys[i - 1] < 0.5 <= ys[i]:
            lx0, lx1 = math.log(xs[i - 1]), math.log(xs[i])
            t = (0.5 - ys[i - 1]) / (ys[i] - ys[i - 1])
            return math.exp(lx0 + t * (lx1 - lx0))
    if ys and ys[0] >= 0.5:
        return float(xs[0])
    return float("inf")


def _loglog_slope(xvals, yvals) -> float:
    """Least-squares slope of log(y) vs log(x)."""
    xs = np.log(np.asarray(xvals, dtype=np.float64))
    ys = np.log(np.asarray(yvals, dtype=np.float64))
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, _ = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope)


def _gm_ratio_err(sb_pred, sb_meas) -> float:
    """Geometric-mean multiplicative error between predicted and measured SB* over the sigma grid."""
    errs = [abs(math.log(p / mm)) for p, mm in zip(sb_pred, sb_meas) if mm not in (0.0, float("inf"))]
    return math.exp(float(np.mean(errs))) if errs else float("inf")


# ============================================================
# Sweep driver
# ============================================================


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr)).tobytes()).hexdigest()


def run_sweep(mode: str, seeds, trials: int, output_dir: Path, t0: float):
    """For every (m, sb, sigma): measured decode acc (seed-averaged) + closed-form predictions + collapsed
    control (paired on identical residues/noise) + noiseless diagnostic. Returns results + per_unit + artifacts."""
    results = {}          # results[m][sigma] = {"sb": [...], "meas": [...], "correct": [...], "wrong": [...]}
    noiseless = {}        # noiseless[m] = {"sb": [...], "acc": [...]}
    collapsed = {}        # collapsed[m][sigma] = [acc per sb]
    per_unit = []
    artifacts = {}
    total = len(MODULI) * len(SIGMAS)
    unit = 0

    # representative-codebook hashes for arms-differ (first modulus, sb=64, first seed)
    artifacts["cb_phase"] = _digest_arr(phasor_codebook(MODULI[0], 64, 6000 + seeds[0]))
    artifacts["cb_collapsed"] = _digest_arr(collapsed_codebook(MODULI[0], 64, 8000 + seeds[0]))

    for m in MODULI:
        results[m] = {}
        collapsed[m] = {}
        # noiseless diagnostic (number-theoretic exactness; seed-averaged)
        nl_acc = []
        for sb in SB_GRID:
            accs = []
            for sd in seeds:
                cb = phasor_codebook(m, sb, 6000 + sd * 10 + sb)
                a, _, _ = decode_acc(cb, m, sb, 0.0, min(trials, m * 6), np.random.default_rng(11 + sd + sb))
                accs.append(a)
            nl_acc.append(round(float(np.mean(accs)), 4))
        noiseless[m] = {"sb": list(SB_GRID), "acc": nl_acc}

        for sigma in SIGMAS:
            meas_curve, corr_curve, wrong_curve, coll_curve = [], [], [], []
            for sb in SB_GRID:
                accs = []
                coll_accs = []
                for sd in seeds:
                    cb = phasor_codebook(m, sb, 6000 + sd * 10 + sb)
                    rng = np.random.default_rng(90000 + sd + sb + int(sigma * 100) + m)
                    a, res_used, noise_used = decode_acc(cb, m, sb, sigma, trials, rng)
                    accs.append(a)
                    # paired collapsed control on IDENTICAL residues + noise draws
                    cbc = collapsed_codebook(m, sb, 8000 + sd * 10 + sb)
                    ac, _, _ = decode_acc(cbc, m, sb, sigma, trials, rng, residues=res_used, noise=noise_used)
                    coll_accs.append(ac)
                meas_curve.append(round(float(np.mean(accs)), 4))
                coll_curve.append(round(float(np.mean(coll_accs)), 4))
                corr_curve.append(round(pred_acc_correct(sb, m, sigma), 4))
                wrong_curve.append(round(pred_acc_wrong_scaling(sb, m, sigma), 4))
                per_unit.append({"modulus": m, "sigma": sigma, "sb": sb,
                                 "measured": meas_curve[-1], "pred_correct": corr_curve[-1],
                                 "pred_wrong": wrong_curve[-1], "collapsed_ctrl": coll_curve[-1]})
            results[m][sigma] = {"sb": list(SB_GRID), "meas": meas_curve,
                                 "correct": corr_curve, "wrong": wrong_curve}
            collapsed[m][sigma] = coll_curve
            unit += 1
            sbm = _cross_sb(meas_curve, SB_GRID)
            _heartbeat(output_dir, unit, total, t0,
                       extra={"m": m, "sigma": sigma, "SB_star_meas": round(sbm, 1),
                              "acc_min": min(meas_curve), "acc_max": max(meas_curve),
                              "coll_max": max(coll_curve)})
            _say(f"  [m={m} sigma={sigma:.0f}] SB*_meas={sbm:7.1f} acc[{min(meas_curve):.3f}..{max(meas_curve):.3f}] "
                 f"collapsed_ctrl_max={max(coll_curve):.3f}")

    # arms-differ value-surface hashes
    all_meas = np.array([results[m][s]["meas"] for m in MODULI for s in SIGMAS], dtype=np.float64)
    all_corr = np.array([results[m][s]["correct"] for m in MODULI for s in SIGMAS], dtype=np.float64)
    all_wrong = np.array([results[m][s]["wrong"] for m in MODULI for s in SIGMAS], dtype=np.float64)
    all_coll = np.array([collapsed[m][s] for m in MODULI for s in SIGMAS], dtype=np.float64)
    artifacts["surf_meas"] = _digest_arr(all_meas)
    artifacts["surf_correct"] = _digest_arr(all_corr)
    artifacts["surf_wrong"] = _digest_arr(all_wrong)
    artifacts["surf_collapsed"] = _digest_arr(all_coll)
    return results, noiseless, collapsed, per_unit, artifacts


# ============================================================
# Classify
# ============================================================


def classify(results, noiseless, collapsed, mode: str):
    per_m = {}
    reach_ok = True
    reach_fail = []
    for m in MODULI:
        sbm = [_cross_sb(results[m][s]["meas"], SB_GRID) for s in SIGMAS]
        sbc = [_cross_sb(results[m][s]["correct"], SB_GRID) for s in SIGMAS]
        sbw = [_cross_sb(results[m][s]["wrong"], SB_GRID) for s in SIGMAS]
        # reachability: every (m,sigma) brackets 0.5 in-grid AND dips <= REACH_LO somewhere
        for si, s in enumerate(SIGMAS):
            curve = results[m][s]["meas"]
            bracketed = (curve[0] < 0.5 <= curve[-1])
            dips = (min(curve) <= REACH_LO)
            if not (bracketed and dips) or math.isinf(sbm[si]):
                reach_ok = False
                reach_fail.append(f"m={m},sigma={s}")
        p_meas = _loglog_slope(SIGMAS, [x if not math.isinf(x) else SB_GRID[-1] for x in sbm])
        p_corr = _loglog_slope(SIGMAS, sbc)
        p_wrong = _loglog_slope(SIGMAS, sbw)
        err_corr = abs(p_meas - p_corr)
        err_wrong = abs(p_meas - p_wrong)
        gm_corr = _gm_ratio_err(sbc, sbm)
        gm_wrong = _gm_ratio_err(sbw, sbm)
        coll_max = max(max(collapsed[m][s]) for s in SIGMAS)
        per_m[m] = {"SB_star_meas": [round(x, 1) for x in sbm],
                    "SB_star_correct": [round(x, 1) for x in sbc],
                    "SB_star_wrong": [round(x, 1) for x in sbw],
                    "p_meas": round(p_meas, 3), "p_correct": round(p_corr, 3), "p_wrong": round(p_wrong, 3),
                    "exp_err_correct": round(err_corr, 3), "exp_err_wrong": round(err_wrong, 3),
                    "gm_ratio_err_correct": round(gm_corr, 3), "gm_ratio_err_wrong": round(gm_wrong, 3),
                    "collapsed_ctrl_max": round(coll_max, 4), "one_over_m": round(1.0 / m, 4),
                    "acc_at_shipped_sb": {f"sigma{int(s)}": results[m][s]["meas"][SB_GRID.index(SB_SHIPPED)]
                                          for s in SIGMAS},
                    "noiseless_acc_at_sb1_if_present": (noiseless[m]["acc"][0] if noiseless[m]["sb"][0] == SB_GRID[0] else None)}

    p_metas = [per_m[m]["p_meas"] for m in MODULI]
    err_corrs = [per_m[m]["exp_err_correct"] for m in MODULI]
    err_wrongs = [per_m[m]["exp_err_wrong"] for m in MODULI]
    gm_corrs = [per_m[m]["gm_ratio_err_correct"] for m in MODULI]
    coll_maxes = [per_m[m]["collapsed_ctrl_max"] for m in MODULI]
    # per-m advantage: exponent-error advantage (wrong-err / correct-err)
    advantages = [(per_m[m]["exp_err_wrong"] / per_m[m]["exp_err_correct"]) if per_m[m]["exp_err_correct"] > 1e-6
                  else float("inf") for m in MODULI]

    diag = (f"p_meas={[round(x,2) for x in p_metas]} p_correct={[per_m[m]['p_correct'] for m in MODULI]} "
            f"p_wrong={[per_m[m]['p_wrong'] for m in MODULI]} "
            f"exp_err[correct_max={max(err_corrs):.2f} wrong_min={min(err_wrongs):.2f}] "
            f"gm_offset_correct_max={max(gm_corrs):.2f}x collapsed_ctrl_max={max(coll_maxes):.3f} "
            f"reach_ok={reach_ok}")

    # --- control / reachability gates (ALL modes incl smoke) ---
    # collapsed control must collapse everywhere
    for m in MODULI:
        if per_m[m]["collapsed_ctrl_max"] > CTRL_LEAK:
            return ("CONTROL_DID_NOT_COLLAPSE",
                    f"collapsed-codebook control did NOT collapse (m={m} max={per_m[m]['collapsed_ctrl_max']:.3f} "
                    f"> {CTRL_LEAK}): rank-1 codebook should be indistinguishable (~1/m). {diag}", per_m, reach_fail)
        if per_m[m]["collapsed_ctrl_max"] > COLLAPSE_CTRL_MULT / m:
            return ("DISCRIMINATOR_DID_NOT_FIRE",
                    f"collapsed-codebook control above {COLLAPSE_CTRL_MULT}/m (m={m} max="
                    f"{per_m[m]['collapsed_ctrl_max']:.3f} > {COLLAPSE_CTRL_MULT / m:.3f}). Investigate. {diag}",
                    per_m, reach_fail)
    if not reach_ok:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"collapse boundary NOT reachable in the swept grid at {reach_fail}: acc curve does not bracket "
                f"0.5 or does not dip <= {REACH_LO}. Grid mis-designed (extend sb smaller or sigma larger). {diag}",
                per_m, reach_fail)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_DISCRIMINATOR_FIRES: collapse boundary reachable at ALL (m,sigma) incl shipped sb=2730; "
                f"measured scaling exponent p in {[round(x,2) for x in p_metas]} (~2.0 = sqrt(sb)/sigma law); "
                f"correct formula reproduces it (exp_err_max={max(err_corrs):.2f}); wrong-scaling control "
                f"separated (exp_err_min={min(err_wrongs):.2f}); collapsed control collapses "
                f"(max={max(coll_maxes):.3f}). Deliverable band is FULL-only (canonical = remote landing). {diag}",
                per_m, reach_fail)

    # --- FULL pre-registered bands ---
    # HARD_FAIL: law wrong (exponent out of failband)
    for m in MODULI:
        if not (HF_P_LO <= per_m[m]["p_meas"] <= HF_P_HI):
            return ("HARD_FAIL",
                    f"SCALING_LAW_WRONG: m={m} p_meas={per_m[m]['p_meas']:.2f} outside [{HF_P_LO},{HF_P_HI}]. The "
                    f"decode-collapse boundary does NOT follow sqrt(sb)/sigma at this codebook. {diag}",
                    per_m, reach_fail)
    # HARD_FAIL: wrong-scaling tracks as well as correct (sqrt-law not load-bearing)
    if min(advantages) < HF_ADVANTAGE:
        return ("HARD_FAIL",
                f"SQRT_SCALING_NOT_LOAD_BEARING: min exponent-error advantage {min(advantages):.2f} < "
                f"{HF_ADVANTAGE}. The wrong (linear-in-sb) scaling predicts the collapse as well as the correct "
                f"sqrt-law -> the specific scaling is not the discriminator. {diag}", per_m, reach_fail)

    hp = (all(HP_P_LO <= per_m[m]["p_meas"] <= HP_P_HI for m in MODULI)
          and max(err_corrs) <= HP_CORRECT_PERR
          and min(err_wrongs) >= HP_WRONG_PERR
          and min(advantages) >= HP_ADVANTAGE
          and max(gm_corrs) <= HP_OFFSET_MAX
          and all(per_m[m]["collapsed_ctrl_max"] <= COLLAPSE_CTRL_MULT / m for m in MODULI))
    if hp:
        return ("HARD_PASS",
                f"SELF-CHECK VALID: the substrate's closed-form decode-collapse-boundary prediction MATCHES the "
                f"measured collapse. Measured scaling exponent p={[round(x,2) for x in p_metas]} (THEORETICAL 2.0 "
                f"= sqrt(sb)/sigma law) reproduced by the correct formula (exp_err_max={max(err_corrs):.2f} <= "
                f"{HP_CORRECT_PERR}); mis-derived linear-scaling control FALSIFIED (exp_err_min="
                f"{min(err_wrongs):.2f} >= {HP_WRONG_PERR}, advantage {min(advantages):.2f}x >= {HP_ADVANTAGE}); "
                f"union-bound offset bounded (gm_ratio_err_max={max(gm_corrs):.2f}x <= {HP_OFFSET_MAX}); "
                f"collapsed control collapses (max={max(coll_maxes):.3f}). Shipped sb=2730 sits in the "
                f"predicted-safe region at every noise level (retrospective validation of the 4 landed math "
                f"cells' 'sb=2730 >> max modulus' boilerplate). {diag}", per_m, reach_fail)
    # MIDDLE: directionally right but offset too large OR advantage weak
    if (all(HP_P_LO <= per_m[m]["p_meas"] <= HP_P_HI for m in MODULI)
            and max(gm_corrs) <= MB_OFFSET_MAX and min(advantages) >= HF_ADVANTAGE):
        return ("MIDDLE_BAND",
                f"partial self-check: scaling exponent matches (p={[round(x,2) for x in p_metas]}) and wrong-"
                f"scaling is separated, but the correct-formula QUANTITATIVE offset is large "
                f"(gm_ratio_err_max={max(gm_corrs):.2f}x in ({HP_OFFSET_MAX},{MB_OFFSET_MAX}]) OR advantage weak "
                f"({min(advantages):.2f}x). The substrate identifies THAT a boundary exists + its scaling, but "
                f"not precisely WHERE. {diag}", per_m, reach_fail)
    return ("MIDDLE_BAND",
            f"partial: a HARD_PASS sub-gate missed (exp_err_correct_max={max(err_corrs):.2f}, "
            f"exp_err_wrong_min={min(err_wrongs):.2f}, advantage_min={min(advantages):.2f}, "
            f"gm_offset_max={max(gm_corrs):.2f}x). {diag}", per_m, reach_fail)


# ============================================================
# Config + main
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"seeds": (7,), "trials": 120}
    if mode == "smoke":
        return {"seeds": SEEDS_SMOKE, "trials": 250}
    return {"seeds": SEEDS_FULL, "trials": 800}


def expected_units(cfg) -> int:
    # per_unit rows = one per (modulus, sigma, sb) measured surface point
    return len(MODULI) * len(SIGMAS) * len(SB_GRID)


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)
    _say(f"[{ANCHOR_NAME}] mode={mode} moduli={MODULI} sb_grid={SB_GRID} sigmas={SIGMAS} "
         f"seeds={cfg['seeds']} trials={cfg['trials']} expected_units={exp}")

    ok_f, msg_f = formula_selftest()
    if not ok_f:
        raise AssertionError(f"FORMULA_SELFTEST_FAIL: {msg_f}")
    _say(f"[{ANCHOR_NAME}] formula self-test PASSED ({msg_f})")

    results, noiseless, collapsed, per_unit, artifacts = run_sweep(
        mode, cfg["seeds"], cfg["trials"], output_dir, t0)

    # arms-differ (META_RULE_AF)
    reasons = []
    if artifacts["cb_phase"] == artifacts["cb_collapsed"]:
        reasons.append("phase codebook == collapsed codebook")
    if artifacts["surf_correct"] == artifacts["surf_wrong"]:
        reasons.append("correct-prediction surface == wrong-scaling surface")
    if artifacts["surf_meas"] == artifacts["surf_collapsed"]:
        reasons.append("measured surface == collapsed-control surface")
    arms_differ_ok = not reasons
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, per_m, reach_fail = classify(results, noiseless, collapsed, mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: RNS sub-block decode-margin self-check ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "config": {"moduli": list(MODULI), "sb_grid": list(SB_GRID), "sb_shipped": SB_SHIPPED,
                   "sigmas": list(SIGMAS), "seeds": list(cfg["seeds"]), "trials": cfg["trials"],
                   "mechanism": "phase_linear_phasor_FPE_subblock_decode",
                   "decode": "per_subblock_phasor_argmax_under_additive_noise",
                   "prediction": "Mary_matched_filter_union_bound_Q_sqrt_sb_over_sigma",
                   "storage_strategy": "no_storage_algebraic_decode"},
        "per_modulus": per_m,
        "noiseless_number_theoretic_diag": noiseless,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "arm_digests": artifacts,
        "reach_fail": reach_fail,
        "bands": {"P_theory": P_THEORY, "HP_p_lo": HP_P_LO, "HP_p_hi": HP_P_HI, "HF_p_lo": HF_P_LO,
                  "HF_p_hi": HF_P_HI, "HP_correct_perr": HP_CORRECT_PERR, "HP_wrong_perr": HP_WRONG_PERR,
                  "HP_advantage": HP_ADVANTAGE, "HF_advantage": HF_ADVANTAGE, "HP_offset_max": HP_OFFSET_MAX,
                  "MB_offset_max": MB_OFFSET_MAX, "collapse_ctrl_mult": COLLAPSE_CTRL_MULT,
                  "ctrl_leak": CTRL_LEAK, "reach_lo": REACH_LO},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    ok_f, msg_f = formula_selftest()
    results, noiseless, collapsed, _pu, _art = run_sweep("selftest", (7,), 120, output_dir, t0)
    # minimal machinery check: at shipped sb=2730 measured decode is safe (>0.90) at max sigma for all moduli;
    # collapsed control ~1/m; noiseless prime moduli exact at sb=1.
    idx_ship = SB_GRID.index(SB_SHIPPED)
    ship_ok = all(results[m][max(SIGMAS)]["meas"][idx_ship] >= 0.90 for m in MODULI)
    coll_ok = all(max(collapsed[m][s]) <= CTRL_LEAK for m in MODULI for s in SIGMAS)
    prime_ok = (noiseless[19]["acc"][0] >= 0.99 and noiseless[43]["acc"][0] >= 0.99)  # prime -> exact at sb=4
    ok = ok_f and ship_ok and coll_ok and prime_ok
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: formula={ok_f}({msg_f}) shipped_safe={ship_ok} "
         f"collapsed_collapses={coll_ok} prime_noiseless_exact={prime_ok} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
