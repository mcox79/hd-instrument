# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: phasor book vs degenerate(rank-1) book hash-distinct; measured-Kcrit
#     surface vs exact-prediction surface vs asymptotic-prediction surface vs wrong-scaling surface all
#     hash-distinct; normal-book pointwise recall curve vs degenerate-book pointwise recall curve hash-distinct.
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except).
# - crlb/capacity-feasibility: this cell IS the capacity-feasibility instrument. The bundle-cleanup decode-collapse
#     boundary K_crit (largest K with recall@1>=0.9) is the M-ary-orthogonal-signaling order-statistic detection
#     threshold. The 3 LANDED cells self-predict it via the LOOSE N/(2 ln N) asymptotic (Plate-1995-style), which
#     is 15-58% off (MEASURED@data/exp_bundle_capacity_{theory_cpu,largeN_gpu}_v1/metrics.json). This cell adds the
#     EXACT order-statistic member of the SAME family: P_correct = E_x[ Phi(x/sqrt(N*K/2))^(V-1) ], x ~ N(N,
#     N*(K-1)/2) (THEORETICAL@notes/research_codebook_design_space_generalization_2026-07-06.md Sec.1/4, derived
#     from the bind/unbind arithmetic). discriminator_reachability=True: K_crit is bracketed inside [10, 0.2*N] at
#     every N (retrospective K_crit 81-1298 < 0.2*16384=3276). Pre-dispatch cheap decisive test (this cell's
#     author, zero new trials): exact K_crit dev vs 3 landed metrics = 2.35%(N1024) 0.61%(N2048) 0.30%(N8192)
#     0.15%(N16384); cliff pointwise RMS 0.0015; asymptotic dev 15-58% -- MEASURED@author recompute vs landed.
# - baseline_in_band (META_RULE_AG): this is a PREDICTION-MATCH test, not a difficulty baseline. The measured
#     recall curve intentionally spans ~chance (large K, degenerate book) up to 1.0 (small K); the degenerate
#     (rank-1) book arm is a declared must-collapse CONTROL (~1/V) exempt from the in-band rule. The asymptotic
#     N/(2 ln N) arm is a live CONTROL/BASELINE (loose 15-58%); the exact arm is the new MECHANISM. The
#     discriminator (exact-Kcrit vs asymptotic-Kcrit tightness) does NOT saturate at scale -- it WIDENS with N
#     (asymptotic 15% at N=1024 -> 58% at N=16384).
# - discriminator survives scale: smoke fires the discriminator at N={1024,2048} (exact <=5% vs asymptotic
#     >=10%, rel_improve >=3x, wrong-scaling clearly separated ~88-93%, degenerate book collapses). The exact/
#     asymptotic/wrong PREDICTIONS are DETERMINISTIC closed forms; only the MEASURED K_crit carries seed noise.
#     Scale survival is DISCRIMINATOR-MUST-SURVIVE-SCALE option (B): the exact formula is EXACT by derivation and
#     already verified against the LANDED large-N (8192,16384) measured data at 0.15-0.30% dev (author recompute,
#     reproduced this cell's construction). The asymptotic law's looseness GROWS with N, so the discriminator is
#     strongest at the large-N points re-measured fresh in FULL.
# - HARD_PASS strictly above floor: exact-arm K_crit deviation <= 5% at EVERY N (a deflated bar above the
#     0.15-3.0% retrospective, leaving margin for fresh-seed + integer-granularity noise), AND >= 3x tighter than
#     the asymptotic arm at N>=8192, AND cliff-style pointwise RMS <= 1% at N=4096, AND both controls fire.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# MECHANISM-SELF-VERIFICATION -- FHRR/HRR BUNDLE-CAPACITY EXACT ORDER-STATISTIC MARGIN  v1
# =========================================================================================
# NEW standalone cell (does NOT overwrite the 3 landed bundle-capacity cells; monitor-not-control, never edits a
# landed cell's config/artifacts). EXTENDS the just-landed RNS exact-prefactor self-margin CG candidate
# (exp_rns_subblock_margin_exact_prefactor_v2) to a SECOND codebook family: the FHRR/HRR superposition-bundle
# cleanup memory (the substrate's single most load-bearing codebook -- underlies binding/memory/multi_hop/
# generation). The 3 landed cells (exp_bundle_capacity_theory_cpu_v1 HARD_PASS-smoke, exp_bundle_capacity_
# largeN_gpu_v1 MIDDLE_BAND@production-N, exp_bundle_capacity_cliff_gpu_v1 HARD_FAIL-vs-over-optimistic-threshold)
# self-predict their own K_crit via the LOOSE N/(2 ln N) asymptotic (15-58% off). This cell RE-MEASURES the bundle
# capacity FRESH (measurement machinery -- cphasor/bundle/unbind/argmax-cleanup/binary-search -- reused VERBATIM
# from the landed cells) and adds the EXACT order-statistic prediction that fits to <5%.
#
# Derivation (from the bind/unbind arithmetic; notes/research_codebook_design_space_generalization_2026-07-06.md
# Sec.1 Family B): bundle B = sum_k roles_k * book[fidx_k]; unbind rec = B * conj(roles_q) = book[fidx_q] +
# crosstalk (sum of K-1 iid unit-random-phase vectors). Scoring rec against the book of V iid codewords:
#   sc[true]       ~ N(N,     N*(K-1)/2)   (self inner-product N + projected crosstalk)
#   sc[competitor] ~ N(0,     N*K/2)       iid across the V-1 non-true book entries
# -> P_correct = E_x[ Phi(x/sqrt(N*K/2))^(V-1) ], x ~ N(N, N*(K-1)/2). K_crit(N,V) = largest K with P>=0.9.
# This is the IDENTICAL "elevated-mean true vs iid zero-mean competitors" order-statistic structure as the RNS
# codebook, with (mean=N, var_true=N(K-1)/2, var_comp=NK/2, n_comp=V-1) substituted -- a genuinely NEW derivation
# for THIS family (different mean/variance terms, derived not asserted), not a copy of the RNS formula.
#
# ARMS (per N; predictions are deterministic closed forms, measurement is fresh):
#   measured           : MEASUREMENT -- fresh empirical K_crit (recall@1>=0.9 binary search, verbatim machinery). [MECHANISM]
#   theory_exact       : NEW -- exact order statistic kcrit_exact(N,V). The genuine new discriminator; the substrate
#                        predicts its OWN bundle K_crit EXACTLY.                                                 [PREDICTION]
#   theory_asymptotic  : the landed cells' N/(2*ln(N)) law, KEPT as a live CONTROL/BASELINE -- must stay loose
#                        (15-58% off; MEASURED@landed).                                                          [CONTROL/BASELINE]
#   wrong_scaling      : mis-derived -- crosstalk summed COHERENTLY (amplitudes) not INCOHERENTLY (power) -> noise
#                        variance ~K^2 not ~K -> predicts K_crit ~ sqrt(N). Isolates the incoherent-crosstalk
#                        (power-summation) scaling is load-bearing.                                              [CONTROL 1]
#   degenerate_book    : rank-1 book (all V rows share ONE bit-identical codeword) -> cleanup argmax degenerate ->
#                        recall ~ 1/V at every K. Isolates distinguishable book STRUCTURE (not merely N dims).   [CONTROL 2, must-collapse]
#   pointwise (N=4096) : cliff-style K-sweep recall@1 vs pred_acc_exact -- pointwise-curve discriminator (RMS).   [DIAGNOSTIC + pointwise]
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the exact margin / prediction-vs-measurement in its own
#   metrics.json. It NEVER changes N/K/V, edits a landed cell's config, or triggers a rebuild. A REPORTING
#   refinement (a tighter number), never a config-changing action. NOT self-improvement. Brain-grounding: HONESTLY
#   engineering (BIST / noise-margin analysis -- conservative margin BOUND -> tight margin PREDICTION).
#
# ASCII-only. Measurement: torch, DEV=cuda if available else cpu (SAME code path both; smoke runs torch-CPU
#   locally, FULL runs torch-CUDA on the overnight GPU queue). Predictions: numpy Gauss-Hermite 64pt + stdlib
#   math.erfc (NO scipy). Self-contained (synthetic phasor codebooks; no pool/re-encode/cert_ledger dependency ->
#   clean remote gate, NON-PARKED, zero referent).
# Run: python experiments/exp_fhrr_bundle_capacity_exact_margin_v1.py [--self-test | --smoke]
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

ANCHOR_NAME = "fhrr_bundle_capacity_exact_margin_v1"
REPO = Path(__file__).resolve().parents[1]

# Fixed competitor-book size (matches landed cliff_gpu V=5000; exact prediction uses the SAME V for a fair match).
V_BOOK = 5000

# N grid: production-scale span matching the 3 landed cells (1024-16384). Smoke = the two small N (torch-CPU local).
N_GRID_FULL = (1024, 2048, 4096, 8192, 16384)
N_GRID_SMOKE = (1024, 2048)

# Pointwise cliff-style K-sweep at a fixed N (mirrors exp_bundle_capacity_cliff_gpu_v1 regime, N=4096).
POINTWISE_N = 4096
POINTWISE_KS_FULL = (50, 100, 200, 400, 600, 800)
POINTWISE_KS_SMOKE = (50, 200, 400)

RECALL_THRESH = 0.9        # K_crit = largest K with recall@1 >= this (verbatim from landed cells)
HI_FRAC = 0.2              # binary-search upper bound int(HI_FRAC*N) (verbatim from landed theory_cpu)

# ---- Pre-registered bands (deviation = |measured - prediction| / measured, normalized by ground-truth measured) ----
HP_EXACT_DEV = 0.05        # HARD_PASS: exact-arm K_crit deviation <= this at EVERY N. THEORETICAL@order statistic;
                           #   MEASURED@author-recompute-vs-landed 0.0015-0.0235 (leaves margin for fresh-seed +
                           #   integer-granularity noise).
MB_EXACT_DEV = 0.15        # MIDDLE ceiling: exact dev in (0.05, 0.15] at some N -> tighter than asymptotic, not <=5%.
HF_EXACT_DEV = 0.15        # HARD_FAIL: exact dev > this at ANY N (exact no better than the loose asymptotic).
REL_IMPROVE_MIN = 3.0      # HARD_PASS + control: asymptotic_dev / exact_dev >= this at N>=8192 (the exact treatment
                           #   does genuine work). MEASURED@author-recompute >100x at N>=8192.
LARGE_N = 8192             # N threshold for the relative-improvement gate.
WRONG_SEP_MIN = 0.20       # control: wrong-scaling K_crit dev must be >= this at some N (clearly separated ->
                           #   power-summation scaling load-bearing). MEASURED@author-recompute 0.88-0.97.
DEGEN_RECALL_MAX = 0.02    # degenerate-book recall must be <= this at every pointwise K. Absolute ceiling ~100x
                           #   above chance (1/V~2e-4) yet ~40x below any real recall (0.79-1.0) -> robust to the
                           #   finite-sample noise of a near-zero binomial (smoke tr_point=10) while cleanly
                           #   isolating that distinguishable book STRUCTURE (not merely N dims) is load-bearing.
POINTWISE_RMS_MAX = 0.01   # HARD_PASS: pointwise recall-curve RMS(measured, pred_exact) <= this at N=4096.
# Smoke discriminator-fires bands (loosened vs the FULL canonical bars to tolerate smoke's reduced-trial noise AND
# the physics that the exact-vs-asymptotic separation is WEAKEST at the small smoke-N -- it WIDENS with N, so the
# canonical >=3x bar is applied FULL-only at N>=8192 where the asymptotic is 45-58% off):
SMOKE_EXACT_DEV = 0.05     # smoke: exact dev <= this at both smoke N (exact is tight -> fires).
SMOKE_ASYMPT_MIN = 0.10    # smoke: asymptotic dev >= this at both smoke N (baseline is loose -> contrast exists).
SMOKE_REL_MIN = 2.5        # smoke: asymptotic_dev / exact_dev >= this at both smoke N (exact demonstrably tighter;
                           #   MEASURED@smoke 2.8x@N1024 10.2x@N2048 -- modest at the smallest N by construction).
SMOKE_POINTWISE_RMS = 0.02 # smoke: pointwise RMS <= this (looser than the FULL 0.01 canonical bar).

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
# Closed-form predictions: EXACT order statistic (new) + asymptotic law (landed baseline) + wrong-scaling control
# numpy Gauss-Hermite 64pt (mirrors the RNS sibling; NO scipy).
# ============================================================

_GH_N = 64
_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite.hermgauss(_GH_N)
_INV_SQRT_PI = 1.0 / math.sqrt(math.pi)
_SQRT2 = math.sqrt(2.0)


def _logPhi(a: float) -> float:
    """Stable log standard-normal CDF. Phi(a) = 0.5*erfc(-a/sqrt2)."""
    v = 0.5 * math.erfc(-a / _SQRT2)
    return math.log(v) if v > 0.0 else -1e300


def _order_stat(mean: float, s_true: float, s_comp: float, ncomp: int) -> float:
    """E_x[ Phi(x/s_comp)^ncomp ], x ~ N(mean, s_true^2), via 64-pt Gauss-Hermite. x = mean + sqrt(2)*s_true*node."""
    acc = 0.0
    for zi, wi in zip(_GH_NODES, _GH_WEIGHTS):
        x = mean + _SQRT2 * s_true * zi if s_true > 0.0 else mean
        lp = _logPhi(x / s_comp)
        acc += wi * (math.exp(ncomp * lp) if ncomp * lp > -700.0 else 0.0)
    return _INV_SQRT_PI * acc


def pred_acc_exact(N: int, K: int, V: int) -> float:
    """NEW -- EXACT bundle-cleanup order statistic. P_correct = E_x[ Phi(x/sqrt(N*K/2))^(V-1) ],
    x ~ N(N, N*(K-1)/2). Derived from the bind/unbind arithmetic (crosstalk = K-1 iid unit-random-phase vectors
    summed INCOHERENTLY -> variance ~K). THEORETICAL@notes/research_codebook_design_space_generalization_2026-07-06.md."""
    if K <= 0:
        return 1.0
    s_true = math.sqrt(N * max(K - 1, 0) / 2.0)
    s_comp = math.sqrt(N * K / 2.0)
    return min(1.0, max(0.0, _order_stat(float(N), s_true, s_comp, V - 1)))


def pred_acc_wrong(N: int, K: int, V: int) -> float:
    """CONTROL 1 (mis-derived): crosstalk summed COHERENTLY (amplitudes add) not INCOHERENTLY (power adds) ->
    std ~ (K-1) not sqrt(K-1); variance quadratic in K. Predicts K_crit ~ sqrt(N) (falsified by measured ~N/lnN)."""
    if K <= 0:
        return 1.0
    s_true = math.sqrt(N * max(K - 1, 0) ** 2 / 2.0)
    s_comp = math.sqrt(N * K ** 2 / 2.0)
    return min(1.0, max(0.0, _order_stat(float(N), s_true, s_comp, V - 1)))


def kcrit_asymptotic(N: int) -> float:
    """CONTROL/BASELINE -- the landed cells' loose Plate-1995-style law N/(2 ln N)."""
    return N / (2.0 * math.log(N))


def kcrit_pred(fn, N: int, V: int, thresh: float = RECALL_THRESH) -> int:
    """Binary search on K for a closed-form predictor fn(N,K,V) >= thresh. lo=1 (predictions unfloored)."""
    lo, hi, best = 1, int(HI_FRAC * N), 1
    while lo <= hi:
        K = (lo + hi) // 2
        if fn(N, K, V) >= thresh:
            best = K
            lo = K + 1
        else:
            hi = K - 1
    return best


def formula_selftest() -> tuple[bool, str]:
    """Analytical self-test (self-contained -- no landed-metrics dependency):
    (a) erfc/Phi correctness; (b) exact monotone-decreasing in K; (c) near-noiseless at K=1 (>0.999);
    (d) exact log-log slope of K_crit vs N ~1.0 (linear) while wrong ~0.5 (sqrt); (e) wrong-scaling K_crit
    clearly BELOW exact at every N (control separation)."""
    if abs(0.5 * math.erfc(0.0) - 0.5) > 1e-9:
        return False, "PHI_HALF_BROKEN"
    if not (_logPhi(1.0) > _logPhi(0.0) > _logPhi(-1.0)):
        return False, "LOGPHI_NOT_MONOTONE"
    # (b) monotone decreasing in K
    prev = 2.0
    for K in (1, 10, 50, 100, 200, 400, 800, 1200):
        p = pred_acc_exact(4096, K, V_BOOK)
        if p > prev + 1e-9:
            return False, f"EXACT_NOT_MONOTONE_IN_K K={K} p={p:.4f} prev={prev:.4f}"
        prev = p
    # (c) near-noiseless at K=1
    for N in N_GRID_FULL:
        if pred_acc_exact(N, 1, V_BOOK) < 0.999:
            return False, f"EXACT_NOT_NEAR1_AT_K1 N={N} p={pred_acc_exact(N,1,V_BOOK):.5f}"
    # (d) log-log slopes: exact ~1.0, wrong ~0.5
    kc_e = [kcrit_pred(pred_acc_exact, N, V_BOOK) for N in N_GRID_FULL]
    kc_w = [kcrit_pred(pred_acc_wrong, N, V_BOOK) for N in N_GRID_FULL]
    lnN = np.log(np.asarray(N_GRID_FULL, dtype=np.float64))
    A = np.vstack([lnN, np.ones_like(lnN)]).T
    slope_e = float(np.linalg.lstsq(A, np.log(kc_e), rcond=None)[0][0])
    slope_w = float(np.linalg.lstsq(A, np.log(kc_w), rcond=None)[0][0])
    if not (0.85 <= slope_e <= 1.15):
        return False, f"EXACT_SLOPE_OFF slope={slope_e:.3f} (expect ~1.0 linear-in-N)"
    if slope_w > 0.7:
        return False, f"WRONG_SLOPE_NOT_SEPARATED slope={slope_w:.3f} (expect ~0.5 sqrt-N)"
    # (e) wrong clearly below exact at every N
    for i, N in enumerate(N_GRID_FULL):
        if kc_w[i] >= 0.6 * kc_e[i]:
            return False, f"WRONG_NOT_BELOW_EXACT N={N} wrong={kc_w[i]} exact={kc_e[i]}"
    return True, "FORMULA_SELFTEST_PASS"


# ============================================================
# Measurement machinery (VERBATIM from the landed bundle cells; torch, DEV=cuda if available else cpu)
# ============================================================


def _import_torch():
    import torch
    return torch


def cphasor(torch, m: int, d: int, g, dev):
    """Unit-magnitude complex FHRR phasors, uniform random phase per dim (VERBATIM from landed cells)."""
    ang = (torch.rand(m, d, generator=g, device=dev) * 2 - 1) * math.pi
    return torch.complex(torch.cos(ang), torch.sin(ang))


def measure_recall(torch, N: int, K: int, V: int, TR: int, book, g, dev, degenerate: bool = False) -> float:
    """Fresh empirical recall@1 for K role-filler pairs bundled + unbound + argmax-cleanup against `book`.
    VERBATIM bind/unbind/cleanup from the landed cells. If degenerate, cleanup against a rank-1 (all-same) book."""
    clean_book = book
    if degenerate:
        clean_book = book[0:1].expand(V, N)  # rank-1: all V rows identical -> argmax degenerate
    hit = 0
    tot = 0
    for _ in range(TR):
        roles = cphasor(torch, K, N, g, dev)
        fidx = torch.randperm(V, generator=g, device=dev)[:K]
        B = (roles * book[fidx]).sum(0)
        rec = B.unsqueeze(0) * roles.conj()          # [K, N]
        sc = (rec @ clean_book.conj().T).real        # [K, V]
        pred = torch.argmax(sc, dim=1)
        hit += int((pred == fidx).sum())
        tot += K
    return hit / tot


def measure_kcrit(torch, N: int, V: int, TR: int, book, g, dev) -> int:
    """Binary search K_crit (recall@1 >= RECALL_THRESH). VERBATIM structure from the landed cells (lo=10)."""
    lo, hi, best = 10, int(HI_FRAC * N), 10
    while lo <= hi:
        K = (lo + hi) // 2
        r = measure_recall(torch, N, K, V, TR, book, g, dev)
        if r >= RECALL_THRESH:
            best = K
            lo = K + 1
        else:
            hi = K - 1
    return best


# ============================================================
# Sweep driver
# ============================================================


def _digest(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float64)).tobytes()).hexdigest()


def run_sweep(torch, mode: str, N_grid, pointwise_ks, tr_kcrit: int, tr_point: int, seed: int,
              output_dir: Path, t0: float, dev):
    """K_crit-vs-N sweep (measured/exact/asymptotic/wrong) + pointwise cliff-style K-sweep (normal + degenerate)."""
    per_n = {}
    per_unit = []
    total = len(N_grid) + len(pointwise_ks)
    unit = 0

    # --- K_crit vs N ---
    for N in N_grid:
        V = min(V_BOOK, 4 * N)   # book cap VERBATIM from landed theory_cpu (min(V,4*N)); exact pred uses SAME V
        g = torch.Generator(device=dev).manual_seed(seed + N)
        book = cphasor(torch, V, N, g, dev)
        kc_meas = measure_kcrit(torch, N, V, tr_kcrit, book, g, dev)
        kc_exact = kcrit_pred(pred_acc_exact, N, V)
        kc_asy = kcrit_asymptotic(N)
        kc_wrong = kcrit_pred(pred_acc_wrong, N, V)
        dev_exact = abs(kc_meas - kc_exact) / kc_meas if kc_meas else float("inf")
        dev_asy = abs(kc_meas - kc_asy) / kc_meas if kc_meas else float("inf")
        dev_wrong = abs(kc_meas - kc_wrong) / kc_meas if kc_meas else float("inf")
        rel_improve = (dev_asy / dev_exact) if dev_exact > 1e-9 else float("inf")
        per_n[N] = {"measured": kc_meas, "exact": kc_exact, "asymptotic": round(kc_asy, 1), "wrong": kc_wrong,
                    "V": V, "dev_exact": round(dev_exact, 4), "dev_asymptotic": round(dev_asy, 4),
                    "dev_wrong": round(dev_wrong, 4), "rel_improve_asy_over_exact": round(rel_improve, 2)}
        per_unit.append({"kind": "kcrit_vs_N", "N": N, "V": V, "measured_kcrit": kc_meas,
                         "exact_kcrit": kc_exact, "asymptotic_kcrit": round(kc_asy, 1), "wrong_kcrit": kc_wrong,
                         "dev_exact": round(dev_exact, 4), "dev_asymptotic": round(dev_asy, 4),
                         "dev_wrong": round(dev_wrong, 4)})
        unit += 1
        _heartbeat(output_dir, unit, total, t0,
                   extra={"N": N, "kc_meas": kc_meas, "kc_exact": kc_exact, "dev_exact": round(dev_exact, 4)})
        _say(f"  [N={N:5d}] K_crit meas={kc_meas:5d} exact={kc_exact:5d} (dev={dev_exact*100:5.2f}%) "
             f"asympt={kc_asy:7.1f} (dev={dev_asy*100:5.2f}%) wrong={kc_wrong:4d} (dev={dev_wrong*100:5.2f}%) "
             f"rel_improve={rel_improve:.1f}x")

    # --- pointwise cliff-style K-sweep at POINTWISE_N (normal + degenerate control) ---
    Vp = min(V_BOOK, 4 * POINTWISE_N)   # = 5000 at N=4096 (matches landed cliff_gpu V=5000)
    gp = torch.Generator(device=dev).manual_seed(seed + 777)
    pbook = cphasor(torch, Vp, POINTWISE_N, gp, dev)
    pw_meas, pw_pred, pw_degen = {}, {}, {}
    sq = []
    for K in pointwise_ks:
        rm = measure_recall(torch, POINTWISE_N, K, Vp, tr_point, pbook, gp, dev, degenerate=False)
        rd = measure_recall(torch, POINTWISE_N, K, Vp, tr_point, pbook, gp, dev, degenerate=True)
        pe = pred_acc_exact(POINTWISE_N, K, Vp)
        pw_meas[K] = round(rm, 4)
        pw_pred[K] = round(pe, 4)
        pw_degen[K] = round(rd, 4)
        sq.append((rm - pe) ** 2)
        per_unit.append({"kind": "pointwise", "N": POINTWISE_N, "K": K, "measured_recall": round(rm, 4),
                         "pred_exact_recall": round(pe, 4), "degenerate_recall": round(rd, 4)})
        unit += 1
        _heartbeat(output_dir, unit, total, t0, extra={"K": K, "meas": round(rm, 4), "pred": round(pe, 4)})
        _say(f"  [pointwise N={POINTWISE_N} K={K:4d}] meas={rm:.4f} pred_exact={pe:.4f} "
             f"absdiff={abs(rm-pe):.4f} degenerate={rd:.5f}")
    pointwise_rms = math.sqrt(sum(sq) / len(sq)) if sq else float("inf")
    degen_max = max(pw_degen.values()) if pw_degen else 1.0

    # --- arms-differ surfaces (META_RULE_AF) ---
    arts = {}
    arts["surf_measured"] = _digest([per_n[N]["measured"] for N in N_grid])
    arts["surf_exact"] = _digest([per_n[N]["exact"] for N in N_grid])
    arts["surf_asymptotic"] = _digest([per_n[N]["asymptotic"] for N in N_grid])
    arts["surf_wrong"] = _digest([per_n[N]["wrong"] for N in N_grid])
    arts["curve_pw_normal"] = _digest([pw_meas[K] for K in pointwise_ks])
    arts["curve_pw_degenerate"] = _digest([pw_degen[K] for K in pointwise_ks])

    pointwise = {"N": POINTWISE_N, "V": Vp, "ks": list(pointwise_ks), "measured": pw_meas, "pred_exact": pw_pred,
                 "degenerate": pw_degen, "rms": round(pointwise_rms, 5), "degen_max": round(degen_max, 6)}
    return per_n, per_unit, pointwise, arts


# ============================================================
# Classify
# ============================================================


def classify(per_n, pointwise, N_grid, mode: str):
    devs_exact = {N: per_n[N]["dev_exact"] for N in N_grid}
    devs_asy = {N: per_n[N]["dev_asymptotic"] for N in N_grid}
    devs_wrong = {N: per_n[N]["dev_wrong"] for N in N_grid}
    rms = pointwise["rms"]
    degen_max = pointwise["degen_max"]
    max_exact = max(devs_exact.values())
    large_ns = [N for N in N_grid if N >= LARGE_N]
    rel_ok_large = all((devs_asy[N] / devs_exact[N] if devs_exact[N] > 1e-9 else float("inf")) >= REL_IMPROVE_MIN
                       for N in large_ns) if large_ns else False
    wrong_sep = max(devs_wrong.values()) >= WRONG_SEP_MIN
    degen_collapsed = degen_max <= DEGEN_RECALL_MAX

    diag = (f"dev_exact={ {N: round(devs_exact[N],4) for N in N_grid} } "
            f"dev_asymptotic={ {N: round(devs_asy[N],3) for N in N_grid} } "
            f"dev_wrong_max={max(devs_wrong.values()):.2f} pointwise_rms={rms:.4f} "
            f"degen_recall_max={degen_max:.5f} (chance~{1.0/V_BOOK:.5f})")

    # --- controls fire (ALL modes) ---
    if not wrong_sep:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"WRONG_SCALING_NOT_SEPARATED: max wrong-scaling K_crit dev {max(devs_wrong.values()):.2f} < "
                f"{WRONG_SEP_MIN} -- the incoherent (power) crosstalk-summation scaling is NOT load-bearing. {diag}",
                diag)
    if not degen_collapsed:
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"DEGENERATE_BOOK_DID_NOT_COLLAPSE: rank-1 book recall max {degen_max:.5f} > "
                f"{DEGEN_RECALL_MAX} -- cleanup should be near chance (~1/V) with a degenerate book. {diag}",
                diag)

    if mode == "smoke":
        smoke_fires = (max_exact <= SMOKE_EXACT_DEV
                       and all(devs_asy[N] >= SMOKE_ASYMPT_MIN for N in N_grid)
                       and all((devs_asy[N] / devs_exact[N] if devs_exact[N] > 1e-9 else float("inf")) >= SMOKE_REL_MIN
                               for N in N_grid)
                       and rms <= SMOKE_POINTWISE_RMS)
        if not smoke_fires:
            return ("DISCRIMINATOR_DID_NOT_FIRE",
                    f"SMOKE_EXACT_ARM_DID_NOT_FIRE: exact_dev_max={max_exact:.4f} (<= {SMOKE_EXACT_DEV}) OR an "
                    f"asymptotic dev < {SMOKE_ASYMPT_MIN} OR a rel_improve < {SMOKE_REL_MIN}x OR pointwise "
                    f"rms={rms:.4f} > {SMOKE_POINTWISE_RMS}. Exact prefactor not demonstrably tighter. {diag}",
                    diag)
        return ("HARD_PASS",
                f"SMOKE_DISCRIMINATOR_FIRES: exact K_crit dev <= {SMOKE_EXACT_DEV} at both smoke N "
                f"(max={max_exact:.4f}) while asymptotic stays loose (>= {SMOKE_ASYMPT_MIN}); "
                f"rel_improve >= {SMOKE_REL_MIN}x; wrong-scaling clearly separated; degenerate book collapses; "
                f"pointwise rms={rms:.4f}. Canonical <=5% at ALL N + >=3x-tighter-at-N>=8192 bars are FULL-only "
                f"(remote GPU landing). {diag}", diag)

    # --- FULL pre-registered bands ---
    if max_exact > HF_EXACT_DEV:
        worst = max(N_grid, key=lambda N: devs_exact[N])
        return ("HARD_FAIL",
                f"EXACT_PREFACTOR_NO_TIGHTER: exact K_crit dev {devs_exact[worst]:.3f} > {HF_EXACT_DEV} at N={worst} "
                f"-- the exact order statistic does NOT predict the measured bundle K_crit to <15%; the "
                f"iid-crosstalk independence assumption did not generalize to fresh seeds/this V. Keep the looser "
                f"already-validated asymptotic law for FHRR-bundle capacity claims. {diag}", diag)
    if not rel_ok_large:
        return ("HARD_FAIL",
                f"EXACT_NOT_RELATIVELY_BETTER: exact arm not >= {REL_IMPROVE_MIN}x tighter than the asymptotic law "
                f"at N>=8192 -- the exact treatment is not doing genuine work over the loose baseline. {diag}", diag)

    if max_exact <= HP_EXACT_DEV and rel_ok_large and rms <= POINTWISE_RMS_MAX:
        return ("HARD_PASS",
                f"EXACT ORDER-STATISTIC SELF-MARGIN VALID: the substrate predicts its OWN FHRR bundle capacity "
                f"K_crit EXACTLY. Exact-arm K_crit dev <= {HP_EXACT_DEV} at ALL N (max={max_exact:.4f}) while the "
                f"loose N/(2 ln N) asymptotic stays {min(devs_asy.values())*100:.0f}-{max(devs_asy.values())*100:.0f}% "
                f"off -- exact is >= {REL_IMPROVE_MIN}x tighter at N>=8192. Cliff-style pointwise recall RMS={rms:.4f} "
                f"<= {POINTWISE_RMS_MAX}. Wrong-scaling (coherent-crosstalk) control clearly separated; degenerate "
                f"(rank-1) book collapses to chance. Promotes the landed bundle-capacity self-prediction from a "
                f"loose asymptotic to an exact prediction across the substrate's most load-bearing codebook family. "
                f"{diag}", diag)
    # MIDDLE: exact beats asymptotic (rel_improve holds) but does not reach <=5% at every N
    return ("MIDDLE_BAND",
            f"partial exact-margin: exact arm relatively tighter than the asymptotic law (rel_improve holds at "
            f"N>=8192) but exact_dev_max={max_exact:.4f} in ({HP_EXACT_DEV},{MB_EXACT_DEV}] at some N, OR "
            f"pointwise rms={rms:.4f} > {POINTWISE_RMS_MAX}. Tighter, but not yet exact self-prediction. {diag}",
            diag)


# ============================================================
# Config + main
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"N_grid": N_GRID_SMOKE, "pointwise_ks": POINTWISE_KS_SMOKE, "tr_kcrit": 4, "tr_point": 6, "seed": 7}
    if mode == "smoke":
        return {"N_grid": N_GRID_SMOKE, "pointwise_ks": POINTWISE_KS_SMOKE, "tr_kcrit": 6, "tr_point": 10, "seed": 11}
    return {"N_grid": N_GRID_FULL, "pointwise_ks": POINTWISE_KS_FULL, "tr_kcrit": 12, "tr_point": 30, "seed": 21}


def expected_units(cfg) -> int:
    return len(cfg["N_grid"]) + len(cfg["pointwise_ks"])


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    exp = expected_units(cfg)
    _write_start_marker(output_dir, mode, exp)

    ok_f, msg_f = formula_selftest()
    if not ok_f:
        raise AssertionError(f"FORMULA_SELFTEST_FAIL: {msg_f}")
    _say(f"[{ANCHOR_NAME}] formula self-test PASSED ({msg_f})")

    torch = _import_torch()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dev_name = (torch.cuda.get_device_name(0) if dev.type == "cuda" else "cpu")
    if mode == "full" and dev.type != "cuda":
        _say(f"[{ANCHOR_NAME}] WARN: FULL requested but CUDA not available -- running torch-CPU "
             f"(numerically identical, slower at large N).")
    _say(f"[{ANCHOR_NAME}] mode={mode} device={dev.type} ({dev_name}) N_grid={cfg['N_grid']} "
         f"pointwise_ks={cfg['pointwise_ks']} V={V_BOOK} tr_kcrit={cfg['tr_kcrit']} tr_point={cfg['tr_point']} "
         f"seed={cfg['seed']} expected_units={exp}")

    per_n, per_unit, pointwise, arts = run_sweep(
        torch, mode, cfg["N_grid"], cfg["pointwise_ks"], cfg["tr_kcrit"], cfg["tr_point"], cfg["seed"],
        output_dir, t0, dev)

    # arms-differ (META_RULE_AF)
    reasons = []
    if arts["surf_measured"] == arts["surf_exact"]:
        reasons.append("measured surface == exact-prediction surface")
    if arts["surf_exact"] == arts["surf_asymptotic"]:
        reasons.append("exact-prediction surface == asymptotic surface")
    if arts["surf_asymptotic"] == arts["surf_wrong"]:
        reasons.append("asymptotic surface == wrong-scaling surface")
    if arts["curve_pw_normal"] == arts["curve_pw_degenerate"]:
        reasons.append("normal pointwise curve == degenerate pointwise curve")
    arms_differ_ok = not reasons
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, diag = classify(per_n, pointwise, list(cfg["N_grid"]), mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: FHRR bundle-capacity EXACT order-statistic self-margin ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": 1,
        "n_units": len(per_unit),
        "expected_n_units": exp,
        "cardinality_ok": len(per_unit) >= exp,
        "device": dev.type,
        "config": {"N_grid": list(cfg["N_grid"]), "V_book_cap": V_BOOK, "V_eff_rule": "min(V_book_cap, 4*N)",
                   "pointwise_N": POINTWISE_N,
                   "pointwise_ks": list(cfg["pointwise_ks"]), "tr_kcrit": cfg["tr_kcrit"],
                   "tr_point": cfg["tr_point"], "seed": cfg["seed"], "recall_thresh": RECALL_THRESH,
                   "mechanism": "fhrr_superposition_bundle_cleanup_kcrit",
                   "decode": "bind_bundle_unbind_argmax_cleanup",
                   "prediction_exact": "bundle_order_statistic_E_Phi_x_over_sqrt_NK2_pow_Vminus1_x_N_mean_var_NKm1_2",
                   "prediction_asymptotic": "plate_N_over_2_lnN",
                   "prediction_wrong": "coherent_crosstalk_amplitude_summation_variance_quadratic_in_K",
                   "quadrature": f"gauss_hermite_{_GH_N}pt_numpy_no_scipy",
                   "storage_strategy": "bundled_capacity_characterization",
                   "extends": "rns_subblock_margin_exact_prefactor_v2 (same order-statistic family, new codebook)"},
        "per_n": {str(N): per_n[N] for N in cfg["N_grid"]},
        "pointwise": pointwise,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "arm_digests": arts,
        "bands": {"HP_exact_dev": HP_EXACT_DEV, "MB_exact_dev": MB_EXACT_DEV, "HF_exact_dev": HF_EXACT_DEV,
                  "rel_improve_min": REL_IMPROVE_MIN, "large_N": LARGE_N, "wrong_sep_min": WRONG_SEP_MIN,
                  "degen_recall_max": DEGEN_RECALL_MAX, "pointwise_rms_max": POINTWISE_RMS_MAX,
                  "smoke_exact_dev": SMOKE_EXACT_DEV, "smoke_asympt_min": SMOKE_ASYMPT_MIN,
                  "smoke_rel_min": SMOKE_REL_MIN, "smoke_pointwise_rms": SMOKE_POINTWISE_RMS},
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
    ok_f, msg_f = formula_selftest()
    # retrospective anchor: exact reproduces the landed-metrics deviations (author-verified, THEORETICAL constants)
    retro_ok = True
    for N, meas, V in [(1024, 85, 4096), (2048, 163, 5000), (8192, 662, 4000), (16384, 1330, 4000)]:
        pred = kcrit_pred(pred_acc_exact, N, V)
        if abs(pred - meas) / meas > 0.05:
            retro_ok = False
    ok = ok_f and retro_ok
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: formula={ok_f}({msg_f}) "
         f"retro_landed_exact_within_5pct={retro_ok} [{time.perf_counter()-t0:.2f}s]")
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
