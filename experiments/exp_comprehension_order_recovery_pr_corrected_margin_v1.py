"""exp_comprehension_order_recovery_pr_corrected_margin_v1

PARTICIPATION-RATIO-CORRECTED self-margin: REVIVES the comprehension order-recovery ACCEPT_BOUNDARY
that exp_comprehension_order_recovery_exact_margin_v1 landed (HARD_FAIL/ACCEPT_BOUNDARY). That cell's
Gaussian max-of-(V-1) order statistic OVER-predicted the comprehension decode collapse (exact p1
mean_ratio=1.193, biased) while a trivial single-draw ("loose", V-blind) model was near-unbiased
(0.972) -- so the naive extreme-value-of-V mechanism added no value. The revival drill
(notes/research_sub_gaussian_tail_self_margin_revival_participation_ratio_2026-07-06.md) measured the
actual tail off-disk: it is NOT a different parametric marginal shape (kurtosis 2.89 ~ Gaussian). It is
an INDEPENDENCE problem: the V-1 "distractors" are CORRELATED (the block-local GSBC codebook is a
JL-projection of the power-law concept-encoder Gram). The FIX: use the PARTICIPATION RATIO (effective
rank) of the codeword Gram, PR(V) = (sum lambda)^2 / sum(lambda^2), as the effective competitor count
n_comp = PR(V)-1 (PR ~16-29, NOT V-1 ~999) in the IDENTICAL Gauss-Hermite order statistic already CG'd
for RNS/FHRR/reasoning-depth -- one substituted exponent, no new machinery.

--------------------------------------------------------------------------------
OFF-DISK PRE-CHECK (zero new trials, vs the landed 60-row envelope surface) -- MEASURED this cell-author
--------------------------------------------------------------------------------
MEASURED@author off-disk (seed-avg PR from cb_max[0:V]; moments from base geometry; landed decode_part;
8 non-saturated seed-avg cells; per-seed 24 cells):
  PR-CORRECTED p1: mean_ratio 1.007 (unbiased), per-seed MAX ratio_err 1.088, cross-seed cv 0.019
  NAIVE-V (V-1)  : mean_ratio 1.193 (BIASED, over-predicts), per-seed MAX ratio_err 2.175
  LOOSE (n=1)    : mean_ratio 0.972 (near-unbiased on average but 11pp too optimistic at hardest cell)
  improvement (naive per-seed max_err / pr per-seed max_err) = 2.00x
  PR table (seed-avg): V=50 ->17.6, V=250 ->25.1, V=1000 ->27.1 (saturates ~27, NOT V-1)
  discriminator control PR_indep(matched independent bipolar codebook, V=1000) = 506 (PR/V=0.51) vs
    PR_gsbc(V=1000)=27 (PR/V=0.027) -> 19x separation: the low PR is the GSBC correlation, NOT the formula.
  degenerate control: identical codewords -> PR = 1.0 exactly (rank-1 Gram).

--------------------------------------------------------------------------------
REVISED BANDS (the original 'beat loose by 1.5x' gate is UNREACHABLE-BY-CONSTRUCTION: the loose
single-draw is already ~unbiased at 0.97 for this codebook regime, so no corrected model can beat it on
aggregate bias. The revised HARD_PASS gates on bias-removal + worst-cell error + the naive-V control +
the correlation-discriminator, which is what actually changed. Ratio-err gates are computed at the
PER-SEED level -- that is where the drill measured 1.088/2.175/2.00x -- because seed-averaging first
compresses the naive worst to ~1.49 (improvement ~1.44x), an aggregation artifact, not the mechanism.)
--------------------------------------------------------------------------------
HARD_PASS (comprehension order-recovery joins the exact self-margin family via the PR correction;
  CG-candidate; a FULL build at the WIDER V grid + 5 seeds must confirm before CHAIN_GRADE):
  - PR-corrected aggregate mean-ratio in [HP_BIAS_LO,HP_BIAS_HI]=[0.80,1.25] (unbiased), AND
  - PR-corrected per-seed per-cell ratio_err <= HP_RATIO_MAX (1.5) at ALL non-saturated seed-cells, AND
  - PR-corrected per-seed ratio_err <= HP_HARDEST_MAX (1.10) at the SINGLE hardest cell (max D, max V), AND
  - NAIVE-V biased: naive aggregate mean-ratio OUTSIDE [NAIVE_UNBIASED_LO,NAIVE_UNBIASED_HI]=[0.85,1.18]
    (the naive full-V count over-predicts -> the PR correction is LOAD-BEARING vs naive-V), AND
  - improvement over naive: naive_perseed_max_err / pr_perseed_max_err >= REL_IMPROVE_MIN (1.5), AND
  - cross-seed CV of per-seed PR ratio_err <= HP_CV_MAX (0.15), AND
  - correlation-discriminator control FIRES: PR_indep/PR_gsbc >= INDEP_RATIO_MIN (5.0) at max V.
HARD_FAIL (honest re-ACCEPT if the correction does not hold multi-seed / at smoke):
  - PR-corrected aggregate mean-ratio OUTSIDE [HF_BIAS_LO,HF_BIAS_HI]=[0.60,1.70], OR
  - PR-corrected per-seed per-cell ratio_err > HF_RATIO_MAX (2.0) at ANY non-saturated seed-cell, OR
  - improvement over naive < ACCEPT_REL_MIN (1.2) (the correction was a coincidence, not a mechanism).
MIDDLE_BAND: clears the core PR bands but misses a HARD_PASS sub-gate (hardest-cell in (1.10,1.5],
  improvement in [1.2,1.5), cv in (0.15,..], or the discriminator control does not clear its floor).

--------------------------------------------------------------------------------
CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (AF): the PR-corrected p1 surface is hash-distinct from BOTH the NAIVE-V and
#   the LOOSE surfaces (different n_comp exponents -> different arrays). Verified per run.
# - final_metrics_atomicity = tmp_replace (os.replace of metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException; grep-clean).
# - crlb / capacity-feasibility: this is a PREDICTION-MATCH test (a ratio, not an accuracy floor).
#   crlb_n_a: the gated quantity is exact-vs-measured ratio tightness, which has no Cramer-Rao noise
#   floor. discriminator_reachability: MEASURED@author off-disk (PR mean_ratio 1.007, per-seed worst
#   1.088, improvement 2.00x) -> HARD_PASS is REACHABLE for the PR-corrected model at smoke scale; the
#   FULL grid confirmation is the remaining risk (P_deflated=0.50 novel-synthesis cap per the drill).
# - baseline_in_band (AG): prediction-match test, not a difficulty baseline. Saturated (meas_p1>=0.999)
#   cells are EXCLUDED from ratio gates (declared), exactly as siblings exclude censored corners. The
#   NAIVE-V and LOOSE arms are live CONTROLS; PR-corrected is the MECHANISM under test.
# - discriminator survives scale: the decode cliff is at FULL N=8192, D=8; smoke keeps the FULL D grid
#   at full N (D=8 present) so the collapse + the PR-vs-naive contrast FIRE in smoke.
# - HARD_PASS strictly above floor: the bias band [0.80,1.25] is centred on 1.0 (the unbiased target);
#   the PR-corrected 1.007 sits at centre, not at an edge. Ratio-err/hardest-cell/improvement bars are
#   ABOVE the measured margins (measured 1.088<1.5, 1.051<1.10, 2.00x>1.5) but with genuine FULL-grid
#   headroom-risk (untested V=125,500 and seeds 23,29) -> HARD_PASS at smoke, FULL confirms CHAIN_GRADE.
# - HP_SCOPE per-arm: HARD_PASS bias/ratio/hardest/improvement/cv gates apply to the PR-corrected arm;
#   the NAIVE-V arm carries only the 'naive biased' direction gate; LOOSE is diagnostic only; the
#   PR_indep arm carries only the correlation-discriminator gate. No arm inherits another's gates.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = seeds x D_grid x V_grid. Verdict gates on count.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = default_ok_for_this_regime: the PR formula is parameter-free given the codeword
#   Gram (no fit-to-accuracy); the Gauss-Hermite moments are measured at a REFERENCE vocab V_REF and
#   extrapolated across V (identical to the exact-margin cell's discipline); 64-pt GH matches RNS/FHRR.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg + comments.
# - progress_logging = line_buffered_stdout + print(flush=True). (FULL may approach 30min on slow
#   remote CPU at 5 seeds -> heartbeat + flush satisfy the >= 1800s rule; smoke/self_test are seconds.)
# - start_marker + crash_diagnostic + heartbeat (defensive error checking; all 4 patterns).
# - positive_control (Gate D): the measurement machinery IS the landed comprehension cell's (base.run_unit)
#   AND the CG'd Gauss-Hermite formula (p_win_extreme) + moment estimator, both reused VERBATIM at the
#   SAME regime (N=8192, same GSBC pool, same grid). Self-test asserts my p_win_extreme is bit-identical
#   to the exact-margin cell's. The off-disk retro reproduces the landed 60-row surface at zero trials.
#
# USER-LOCKED: monitor-not-control. The cell only REPORTS the PR-corrected-vs-measured comprehension
#   cliff prediction in its own metrics.json. It NEVER edits D, V, N, the base cell's config, or triggers
#   a rebuild -- a REPORTING refinement, never a config-changing action. NOT self-improvement. Brain-
#   grounding: HONESTLY a metacognitive error-monitoring signal by shared-math analogy (Nelson & Narens
#   1990 monitor side), NOT a claim of task-level comprehension competence.
#
# Compute architecture: SEQUENTIAL-CPU (numpy matched-filter + block-argmax + eigvalsh; the cell IS the
#   substrate comprehension primitive being re-measured -- bit-identical CPU reference exemption). Storage:
#   no_storage / no_composition beyond the base cell's superposition (synthetic clean GSBC partitions). The
#   prediction arms are numpy Gauss-Hermite quadrature + one (V,V) eigendecomposition per (seed,V) cell (no
#   GPU, no scipy, no torch, no LLM). Requires the untracked GSBC pool npz (SCP before remote FULL; queue_add
#   does NOT ship it).
#
# PROT-018: no _n<N> suffix (N is a fixed confirm axis, not the swept axis). NON-PARKED (synthetic GSBC
#   data only; no cert_ledger referent). ASCII-only; no unicode/emoji/em-dash. NEW cell (does NOT overwrite
#   the accept-boundary cell exp_comprehension_order_recovery_exact_margin_v1). Author: exp_dev.
# Run: python experiments/exp_comprehension_order_recovery_pr_corrected_margin_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)
"""
from __future__ import annotations

import argparse
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Measurement machinery reused VERBATIM (Gate D positive-control at the SAME regime).
import experiments.exp_comprehension_envelope_superposition_vocab_v1 as base  # noqa: E402

ANCHOR_NAME = "comprehension_order_recovery_pr_corrected_margin_v1"

N_DIM = base.N_DIM             # 8192 (never reduced)
B_TOTAL = base.B_TOTAL         # 8
BS = N_DIM // B_TOTAL          # 1024
K_LOCAL = max(1, int(round(base.F_SPARSE * BS)))   # block-local sparsity (== GSBC codebook k, ~20)

# ---- CLI + RUN_MODE (defaults to full; --smoke / --self-test flip; runner injects env) ----
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
_ENV_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _ENV_MODE == "smoke":
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

# ---- grid + seeds per mode (D=8 always present: the cliff lives there; discriminator survives scale) ----
V_REF = 50                     # reference vocab where score moments are MEASURED then extrapolated
if RUN_MODE == "self_test":
    D_GRID = [2, 8]
    V_GRID = [50, 1000]
    SEEDS = [7]
    TRIALS = 40
    MOMENT_TRIALS = 40
elif RUN_MODE == "smoke":
    D_GRID = [2, 4, 6, 8]      # FULL D grid at full N=8192 (D=8 cliff must fire in smoke)
    V_GRID = [50, 250, 1000]   # reduced V grid (3 pts)
    SEEDS = [7, 13, 19]        # 3 seeds for cross-seed cv
    TRIALS = 60
    MOMENT_TRIALS = 60
else:  # full
    D_GRID = [2, 4, 6, 8]
    V_GRID = [50, 125, 250, 500, 1000]     # WIDER grid (V=125,500 untested by the drill)
    SEEDS = [7, 13, 19, 23, 29]            # >= 5 seeds (seeds 23,29 untested by the drill)
    TRIALS = 80
    MOMENT_TRIALS = 80

V_ROLE_MAX = max(V_GRID + [V_REF])
D_MAX = max(D_GRID)
EXPECTED_N_UNITS = len(SEEDS) * len(D_GRID) * len(V_GRID)

# ---- pre-registered bands (REVISED; gated on per-role decode p1; non-saturated cells) ----
SAT_HI = 0.999                 # meas_p1 >= this -> saturated (excluded from ratio gates)
SAT_LO = 0.55                  # meas_p1 <= this -> below the useful band (excluded; none expected)
HP_RATIO_MAX = 1.5             # HARD_PASS: PR-corrected per-seed ratio_err <= this at ALL non-sat cells
HF_RATIO_MAX = 2.0             # HARD_FAIL: PR-corrected per-seed ratio_err > this at ANY non-sat cell
HP_HARDEST_MAX = 1.10          # HARD_PASS: PR-corrected per-seed ratio_err <= this at the hardest cell
HP_BIAS_LO, HP_BIAS_HI = 0.80, 1.25    # HARD_PASS: PR-corrected aggregate mean-ratio unbiased band
HF_BIAS_LO, HF_BIAS_HI = 0.60, 1.70    # HARD_FAIL: PR-corrected aggregate mean-ratio outside -> biased
NAIVE_UNBIASED_LO, NAIVE_UNBIASED_HI = 0.85, 1.18   # naive "biased" iff mean-ratio OUTSIDE this
REL_IMPROVE_MIN = 1.50         # HARD_PASS: naive_perseed_max_err / pr_perseed_max_err >= this
ACCEPT_REL_MIN = 1.20          # HARD_FAIL: improvement < this (correction was a coincidence)
HP_CV_MAX = 0.15               # HARD_PASS: cross-seed CV of per-seed PR ratio_err <= this
INDEP_RATIO_MIN = 5.0          # HARD_PASS: PR_indep/PR_gsbc >= this at max V (correlation is load-bearing)
MIN_NONSAT = {"smoke": 3, "full": 6, "self_test": 1}   # cardinality floor on non-saturated cells

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,B=%d,bs=%d,D=%s,V=%s,SEEDS=%s,TRIALS=%d,V_REF=%d,RUN_MODE=%s,"
    "pred=GH64_extreme_value_order_stat,n_comp=PR(V)-1_participation_ratio,"
    "controls=naive_V-1+loose_1+PR_independent,measure=base.run_unit_VERBATIM,"
    "target=per_role_decode_p1=decode_part^(1/D)"
) % (ANCHOR_NAME, N_DIM, B_TOTAL, BS, "-".join(map(str, D_GRID)), "-".join(map(str, V_GRID)),
     "-".join(map(str, SEEDS)), TRIALS, V_REF, RUN_MODE)


# ============================================================
# Defensive error-checking helpers
# ============================================================
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(out_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_units, "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "_start_marker.json"))


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float,
               extra: Optional[Dict[str, Any]] = None) -> None:
    row = {"ts_iso": _now_iso(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": round(time.perf_counter() - t0, 2)}
    if extra:
        row["extra"] = extra
    try:
        with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_metrics_atomic(out_dir: Path, metrics: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(str(tmp), str(out_dir / "metrics.json"))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
    _write_metrics_atomic(out_dir, diag)


def _digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float64)).tobytes()).hexdigest()


# ============================================================
# Gauss-Hermite extreme-value order statistic (numpy-only; VERBATIM copy of the CG'd formula from
# exp_comprehension_order_recovery_exact_margin_v1.py:p_win_extreme -- self-test asserts bit-identity).
# ============================================================
_GH_N = 64
_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite.hermgauss(_GH_N)
_INV_SQRT_PI = 1.0 / math.sqrt(math.pi)
_SQRT2 = math.sqrt(2.0)


def _logPhi(a: float) -> float:
    """Stable log standard-normal CDF. Phi(a) = 0.5*erfc(-a/sqrt2)."""
    v = 0.5 * math.erfc(-a / _SQRT2)
    return math.log(v) if v > 0.0 else -1e300


def p_win_extreme(mu_s: float, sig_s: float, mu_d: float, sig_d: float, n_comp: float) -> float:
    """P[ signal ~ N(mu_s, sig_s) beats the MAX of n_comp i.i.d. distractors ~ N(mu_d, sig_d) ]
    = E_{s~N(mu_s,sig_s)}[ Phi((s - mu_d)/sig_d)^n_comp ],  64-pt Gauss-Hermite.
    THEORETICAL@order-statistic (David & Nagaraja Order Statistics -- max-of-n CDF Phi(x)^n).
    n_comp = PR(V)-1 (PR-corrected), V-1 (naive), 1 (loose), or PR_indep(V)-1 (independent control)."""
    if sig_d <= 0.0:
        sig_d = 1e-9
    acc = 0.0
    for zi, wi in zip(_GH_NODES, _GH_WEIGHTS):
        s = mu_s + sig_s * _SQRT2 * zi
        a = (s - mu_d) / sig_d
        lp = n_comp * _logPhi(a)
        acc += wi * (math.exp(lp) if lp > -700.0 else 0.0)
    return _INV_SQRT_PI * acc


# ============================================================
# Participation ratio (effective rank) of the codeword Gram -- THE correction (the substrate's OWN geometry)
# ============================================================
def participation_ratio(codewords: np.ndarray) -> float:
    """PR = (sum lambda)^2 / sum(lambda^2), lambda = eigenvalues of the Gram matrix codewords @ codewords.T.
    Effective number of independent competitors (Roy & Vetterli 2007 effective rank; Kish 1965 design
    effect; Stringer 2019 effective dimensionality). codewords: (V, bs). PR in [1, V]: 1 = rank-1
    (identical codewords), V = full rank (independent codewords)."""
    cw = codewords.astype(np.float64)
    G = cw @ cw.T                                  # (V, V) Gram (V<=1000 -> eigvalsh cheap, <0.5s)
    lam = np.clip(np.linalg.eigvalsh(G), 0.0, None)
    s1 = float(lam.sum())
    s2 = float((lam * lam).sum())
    return (s1 * s1) / s2 if s2 > 0.0 else 1.0


def _independent_codebook(V: int, bs: int, k: int, seed: int) -> np.ndarray:
    """Matched INDEPENDENT sparse bipolar codebook (same V, bs, k-sparsity as the GSBC codebook, but no
    shared power-law structure). Control: its PR should be ~V (recovering the naive-V count), proving the
    low GSBC PR is the correlation structure, not a formula artifact."""
    g = np.random.default_rng(424242 + seed)
    cb = np.zeros((V, bs), dtype=np.float32)
    for i in range(V):
        idx = g.choice(bs, size=k, replace=False)
        cb[i, idx] = g.choice(np.array([-1.0, 1.0], dtype=np.float32), size=k)
    return cb


# ============================================================
# Measure score moments from the code geometry (substrate's OWN geometry; NOT fit to accuracy).
# VERBATIM logic from exp_comprehension_order_recovery_exact_margin_v1.py:measure_moments (uses this
# cell's own V_ROLE_MAX / MOMENT_TRIALS so there is no cross-module global coupling).
# ============================================================
def measure_moments(seed: int, D: int, v_ref: int, cb_max: np.ndarray) -> Tuple[float, float, float, float]:
    L = D // 2
    active_cb = base._active_cb(cb_max, D, v_ref, V_ROLE_MAX)   # (D*v_ref, bs)
    rng = np.random.default_rng(555 + seed + 17 * D)
    sig_scores: List[float] = []
    dist_scores: List[float] = []
    for _ in range(MOMENT_TRIALS):
        toks = [int(d * v_ref + rng.integers(0, v_ref)) for d in range(D)]
        roles = list(range(D))
        rng.shuffle(roles)
        a_roles = set(roles[:L])
        blk0 = np.zeros(BS, dtype=np.float32)
        blk1 = np.zeros(BS, dtype=np.float32)
        for d in range(D):
            (blk0 if d in a_roles else blk1)[:] += active_cb[toks[d]]
        for d in range(D):
            blk = blk0 if d in a_roles else blk1
            part = active_cb[d * v_ref:(d + 1) * v_ref]        # (v_ref, bs)
            scores = part @ blk                                 # (v_ref,)
            local = toks[d] - d * v_ref
            sig_scores.append(float(scores[local]))
            for i in range(v_ref):
                if i != local:
                    dist_scores.append(float(scores[i]))
    sig = np.asarray(sig_scores)
    dist = np.asarray(dist_scores)
    return float(sig.mean()), float(sig.std()), float(dist.mean()), float(dist.std())


# ============================================================
# One (seed, D, V) unit: fresh measurement (base.run_unit VERBATIM) + PR/naive/loose/indep p1 predictions
# ============================================================
def run_unit(seed: int, D: int, V: int, cb_max: np.ndarray,
             moments_D: Tuple[float, float, float, float],
             pr_gsbc: float, pr_indep: float) -> Dict[str, Any]:
    r = base.run_unit(D, V, seed, TRIALS, cb_max, V_ROLE_MAX)   # fresh comprehension measurement
    decode_part = float(r["decode_part"])
    meas_p1 = decode_part ** (1.0 / D) if decode_part > 0.0 else 0.0
    mu_s, sig_s, mu_d, sig_d = moments_D
    n_pr = max(pr_gsbc - 1.0, 0.0)
    n_indep = max(pr_indep - 1.0, 0.0)
    p1_pr = p_win_extreme(mu_s, sig_s, mu_d, sig_d, n_pr)
    p1_naive = p_win_extreme(mu_s, sig_s, mu_d, sig_d, float(V - 1))
    p1_loose = p_win_extreme(mu_s, sig_s, mu_d, sig_d, 1.0)
    p1_indep = p_win_extreme(mu_s, sig_s, mu_d, sig_d, n_indep)
    saturated = bool(meas_p1 >= SAT_HI)
    below = bool(meas_p1 <= SAT_LO)

    def _ratio(p):
        return (meas_p1 / p) if p > 1e-9 else None

    return {
        "seed": seed, "D": D, "V_ROLE": V, "L": D // 2,
        "decode_part": round(decode_part, 4),
        "superposition_survival": round(float(r["superposition_survival"]), 4),
        "order_content_perrole": round(float(r["order_content_perrole"]), 4),
        "meas_p1": round(meas_p1, 5),
        "mu_s": round(mu_s, 3), "sig_s": round(sig_s, 3), "mu_d": round(mu_d, 3), "sig_d": round(sig_d, 3),
        "margin_std": round((mu_s - mu_d) / sig_d, 3) if sig_d > 0 else None,
        "pr_gsbc": round(pr_gsbc, 3), "pr_indep": round(pr_indep, 3), "n_comp_pr": round(n_pr, 3),
        "p1_pr": round(p1_pr, 5), "p1_naive": round(p1_naive, 5),
        "p1_loose": round(p1_loose, 5), "p1_indep": round(p1_indep, 5),
        "ratio_pr": (round(_ratio(p1_pr), 4) if _ratio(p1_pr) is not None else None),
        "ratio_naive": (round(_ratio(p1_naive), 4) if _ratio(p1_naive) is not None else None),
        "ratio_loose": (round(_ratio(p1_loose), 4) if _ratio(p1_loose) is not None else None),
        "ratio_indep": (round(_ratio(p1_indep), 4) if _ratio(p1_indep) is not None else None),
        "saturated": saturated, "below_band": below,
    }


# ============================================================
# Aggregation + verdict
# ============================================================
def _ratio_err(r: Optional[float]) -> Optional[float]:
    if r is None or r <= 0:
        return None
    return max(r, 1.0 / r)


def _gm(errs: List[float]) -> Optional[float]:
    errs = [e for e in errs if e is not None and e > 0]
    return math.exp(float(np.mean([math.log(e) for e in errs]))) if errs else None


def _cv(xs: List[float]) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    mu = float(np.mean(xs))
    return round(float(np.std(xs)) / abs(mu), 4) if abs(mu) > 1e-9 else None


def _agg_cells(per_unit: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate per (D,V) over seeds -> one op-point per cell (for mean-ratio / bias)."""
    cells: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for u in per_unit:
        cells.setdefault((u["D"], u["V_ROLE"]), []).append(u)
    out = []
    for (D, V), rows in sorted(cells.items()):
        meas_p1 = float(np.mean([r["meas_p1"] for r in rows]))
        p1_pr = float(np.mean([r["p1_pr"] for r in rows]))
        p1_naive = float(np.mean([r["p1_naive"] for r in rows]))
        p1_loose = float(np.mean([r["p1_loose"] for r in rows]))
        rpr = (meas_p1 / p1_pr) if p1_pr > 1e-9 else None
        rnv = (meas_p1 / p1_naive) if p1_naive > 1e-9 else None
        rlo = (meas_p1 / p1_loose) if p1_loose > 1e-9 else None
        out.append({
            "D": D, "V_ROLE": V, "n_seeds": len(rows),
            "meas_p1": round(meas_p1, 5), "p1_pr": round(p1_pr, 5),
            "p1_naive": round(p1_naive, 5), "p1_loose": round(p1_loose, 5),
            "pr_gsbc": round(float(np.mean([r["pr_gsbc"] for r in rows])), 3),
            "pr_indep": round(float(np.mean([r["pr_indep"] for r in rows])), 3),
            "ratio_pr": (round(rpr, 4) if rpr is not None else None),
            "ratio_naive": (round(rnv, 4) if rnv is not None else None),
            "ratio_loose": (round(rlo, 4) if rlo is not None else None),
            "ratio_err_pr": (round(_ratio_err(rpr), 4) if rpr else None),
            "ratio_err_naive": (round(_ratio_err(rnv), 4) if rnv else None),
            "saturated": bool(meas_p1 >= SAT_HI), "below_band": bool(meas_p1 <= SAT_LO),
            # per-seed ratio-errs (the level the drill measured; the ratio gates use these)
            "per_seed_ratio_err_pr": [round(_ratio_err(r["ratio_pr"]), 4) for r in rows
                                      if r["ratio_pr"] is not None],
            "per_seed_ratio_err_naive": [round(_ratio_err(r["ratio_naive"]), 4) for r in rows
                                         if r["ratio_naive"] is not None],
        })
    return out


def compute_verdict(per_unit: List[Dict[str, Any]], n_units: int,
                    indep_ratio_maxV: Optional[float]) -> Tuple[str, str, Dict[str, Any]]:
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units" % (n_units, EXPECTED_N_UNITS),
                {"cardinality_ok": False})

    # arms-differ (AF): PR-corrected surface must be hash-distinct from BOTH naive and loose.
    pr_surf = np.array([u["p1_pr"] for u in per_unit], dtype=np.float64)
    nv_surf = np.array([u["p1_naive"] for u in per_unit], dtype=np.float64)
    lo_surf = np.array([u["p1_loose"] for u in per_unit], dtype=np.float64)
    arms_differ = (_digest(pr_surf) != _digest(nv_surf)) and (_digest(pr_surf) != _digest(lo_surf))

    cells = _agg_cells(per_unit)
    nonsat = [c for c in cells if not c["saturated"] and not c["below_band"]]
    n_nonsat = len(nonsat)

    # aggregate (seed-avg) mean-ratios for bias
    pr_ratios = [c["ratio_pr"] for c in nonsat if c["ratio_pr"] is not None]
    nv_ratios = [c["ratio_naive"] for c in nonsat if c["ratio_naive"] is not None]
    lo_ratios = [c["ratio_loose"] for c in nonsat if c["ratio_loose"] is not None]
    pr_mean_ratio = round(float(np.mean(pr_ratios)), 4) if pr_ratios else None
    nv_mean_ratio = round(float(np.mean(nv_ratios)), 4) if nv_ratios else None
    lo_mean_ratio = round(float(np.mean(lo_ratios)), 4) if lo_ratios else None
    pr_gm = _gm([_ratio_err(r) for r in pr_ratios])
    nv_gm = _gm([_ratio_err(r) for r in nv_ratios])

    # PER-SEED worst-cell errs (the level the drill measured 1.088 / 2.175)
    pr_ps_errs = [e for c in nonsat for e in c["per_seed_ratio_err_pr"]]
    nv_ps_errs = [e for c in nonsat for e in c["per_seed_ratio_err_naive"]]
    pr_ps_max = max(pr_ps_errs) if pr_ps_errs else None
    nv_ps_max = max(nv_ps_errs) if nv_ps_errs else None
    improve = (nv_ps_max / pr_ps_max) if (pr_ps_max and nv_ps_max and pr_ps_max > 0) else None

    # hardest cell = non-saturated cell with max (D, then V); gate its per-seed worst
    hardest = max(nonsat, key=lambda c: (c["D"], c["V_ROLE"])) if nonsat else None
    hardest_ps_max = (max(hardest["per_seed_ratio_err_pr"])
                      if (hardest and hardest["per_seed_ratio_err_pr"]) else None)

    # cross-seed CV of per-seed PR ratio_err, per cell then averaged
    per_cell_cv = [_cv(c["per_seed_ratio_err_pr"]) for c in nonsat]
    per_cell_cv = [x for x in per_cell_cv if x is not None]
    agg_cv = round(float(np.mean(per_cell_cv)), 4) if per_cell_cv else None

    naive_biased = (nv_mean_ratio is not None
                    and not (NAIVE_UNBIASED_LO <= nv_mean_ratio <= NAIVE_UNBIASED_HI))
    indep_fires = (indep_ratio_maxV is not None and indep_ratio_maxV >= INDEP_RATIO_MIN)

    extra = {
        "cardinality_ok": True, "n_units": n_units, "expected_n_units": EXPECTED_N_UNITS,
        "arms_differ_verified": bool(arms_differ),
        "n_cells": len(cells), "n_nonsaturated": n_nonsat,
        "pr_mean_ratio": pr_mean_ratio, "naive_mean_ratio": nv_mean_ratio, "loose_mean_ratio": lo_mean_ratio,
        "pr_gm_ratio_err": (round(pr_gm, 4) if pr_gm else None),
        "naive_gm_ratio_err": (round(nv_gm, 4) if nv_gm else None),
        "pr_perseed_max_ratio_err": (round(pr_ps_max, 4) if pr_ps_max else None),
        "naive_perseed_max_ratio_err": (round(nv_ps_max, 4) if nv_ps_max else None),
        "improve_over_naive_perseed": (round(improve, 4) if improve else None),
        "hardest_cell": ("D%d_V%d" % (hardest["D"], hardest["V_ROLE"]) if hardest else None),
        "hardest_cell_perseed_max_err": (round(hardest_ps_max, 4) if hardest_ps_max else None),
        "cross_seed_cv_pr": agg_cv, "naive_biased": bool(naive_biased),
        "indep_ratio_maxV": (round(indep_ratio_maxV, 3) if indep_ratio_maxV is not None else None),
        "indep_discriminator_fires": bool(indep_fires),
        "cells": cells,
        "bands": {"HP_RATIO_MAX": HP_RATIO_MAX, "HF_RATIO_MAX": HF_RATIO_MAX,
                  "HP_HARDEST_MAX": HP_HARDEST_MAX, "HP_BIAS_LO": HP_BIAS_LO, "HP_BIAS_HI": HP_BIAS_HI,
                  "HF_BIAS_LO": HF_BIAS_LO, "HF_BIAS_HI": HF_BIAS_HI,
                  "NAIVE_UNBIASED_LO": NAIVE_UNBIASED_LO, "NAIVE_UNBIASED_HI": NAIVE_UNBIASED_HI,
                  "REL_IMPROVE_MIN": REL_IMPROVE_MIN, "ACCEPT_REL_MIN": ACCEPT_REL_MIN,
                  "HP_CV_MAX": HP_CV_MAX, "INDEP_RATIO_MIN": INDEP_RATIO_MIN,
                  "SAT_HI": SAT_HI, "SAT_LO": SAT_LO, "MIN_NONSAT": MIN_NONSAT.get(RUN_MODE, 3)},
    }

    summ = ("units=%d/%d nonsat=%d | PR mean_ratio=%s gm=%s perseed_max=%s hardest(%s)=%s cv=%s | "
            "NAIVE mean_ratio=%s gm=%s perseed_max=%s biased=%s | LOOSE mean_ratio=%s | improve=%s | "
            "PR_indep/PR_gsbc@maxV=%s fires=%s | arms_differ=%s"
            % (n_units, EXPECTED_N_UNITS, n_nonsat, pr_mean_ratio, extra["pr_gm_ratio_err"],
               extra["pr_perseed_max_ratio_err"], extra["hardest_cell"],
               extra["hardest_cell_perseed_max_err"], agg_cv, nv_mean_ratio, extra["naive_gm_ratio_err"],
               extra["naive_perseed_max_ratio_err"], naive_biased, lo_mean_ratio,
               extra["improve_over_naive_perseed"], extra["indep_ratio_maxV"], indep_fires, arms_differ))

    if not arms_differ:
        return "HARD_FAIL", "HARD_FAIL_ARMS (PR-corrected surface bit-identical to a control -- AF): " + summ, extra
    min_nonsat = MIN_NONSAT.get(RUN_MODE, 3)
    if n_nonsat < min_nonsat:
        return ("MIDDLE_BAND", "MIDDLE_BAND (insufficient non-saturated cells: %d < %d -- decode surface "
                "saturated; the cliff did not appear at this grid): " % (n_nonsat, min_nonsat) + summ, extra)
    if pr_mean_ratio is None or nv_mean_ratio is None or improve is None:
        return "MIDDLE_BAND", "MIDDLE_BAND (ratios not computable): " + summ, extra

    # ---- HARD_FAIL gates (honest re-ACCEPT if the correction does not hold) ----
    if not (HF_BIAS_LO <= pr_mean_ratio <= HF_BIAS_HI):
        return ("HARD_FAIL",
                ("PR_CORRECTION_FAILS: PR-corrected aggregate mean-ratio=%.3f OUTSIDE [%.2f,%.2f] -- the "
                 "participation-ratio count does NOT unbias the order statistic for this regime. " %
                 (pr_mean_ratio, HF_BIAS_LO, HF_BIAS_HI)) + summ, extra)
    if pr_ps_max is not None and pr_ps_max > HF_RATIO_MAX:
        return ("HARD_FAIL",
                ("PR_CORRECTION_FAILS: PR-corrected per-seed ratio-err %.3fx > %.2fx at a non-saturated cell "
                 "-- the correction breaks at a corner. " % (pr_ps_max, HF_RATIO_MAX)) + summ, extra)
    if improve < ACCEPT_REL_MIN:
        return ("HARD_FAIL",
                ("PR_CORRECTION_NOT_LOAD_BEARING: improvement over the naive-V model=%.3fx < %.2fx -- the PR "
                 "correction is a coincidence, not a mechanism (it does not meaningfully beat the falsified "
                 "naive full-V count on worst-cell error). " % (improve, ACCEPT_REL_MIN)) + summ, extra)

    # ---- HARD_PASS gate (comprehension order-recovery joins the exact self-margin family via PR) ----
    hp = (HP_BIAS_LO <= pr_mean_ratio <= HP_BIAS_HI
          and pr_ps_max is not None and pr_ps_max <= HP_RATIO_MAX
          and hardest_ps_max is not None and hardest_ps_max <= HP_HARDEST_MAX
          and naive_biased
          and improve >= REL_IMPROVE_MIN
          and (agg_cv is None or agg_cv <= HP_CV_MAX)
          and indep_fires)
    if hp:
        return ("HARD_PASS",
                ("PR-CORRECTED COMPREHENSION ORDER-RECOVERY SELF-MARGIN VALID (CG-candidate; FULL grid must "
                 "confirm): substituting the participation-ratio effective competitor count n_comp=PR(V)-1 "
                 "(PR~%.0f, NOT V-1) into the CG'd extreme-value order statistic UNBIASES the comprehension "
                 "decode-cliff prediction. PR mean_ratio=%.3f (unbiased [%.2f,%.2f]); per-seed ratio-err<=%.2fx "
                 "at ALL %d non-saturated cells; hardest cell %s err=%.3f (<= %.2f); cross-seed cv=%s. The "
                 "NAIVE full-V model stays BIASED (mean_ratio=%.3f, over-predicts collapse) and PR beats its "
                 "worst-cell error by %.2fx -- the PR correction is LOAD-BEARING vs naive-V. Correlation "
                 "discriminator: PR_indep/PR_gsbc=%.1fx at max V (the low PR is the GSBC power-law structure, "
                 "not the formula). Joins RNS/FHRR/reasoning-depth one level up (comprehension), now for a "
                 "REAL-embedding-derived (GSBC) codebook. " %
                 (float(np.mean([c["pr_gsbc"] for c in nonsat])), pr_mean_ratio, HP_BIAS_LO, HP_BIAS_HI,
                  HP_RATIO_MAX, n_nonsat, extra["hardest_cell"], hardest_ps_max, HP_HARDEST_MAX, agg_cv,
                  nv_mean_ratio, improve, extra["indep_ratio_maxV"])) + summ, extra)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: the PR correction removes the naive-V bias (PR mean_ratio=%s in [%.2f,%.2f], improve="
             "%.3fx) but misses a HARD_PASS sub-gate (perseed_max=%s vs %.2f / hardest=%s vs %.2f / improve vs "
             "%.2f / naive_biased=%s / cv=%s vs %.2f / indep_fires=%s). Partially predictive; report the residual "
             "honestly rather than re-averaging. " %
             (pr_mean_ratio, HP_BIAS_LO, HP_BIAS_HI, improve, extra["pr_perseed_max_ratio_err"], HP_RATIO_MAX,
              extra["hardest_cell_perseed_max_err"], HP_HARDEST_MAX, REL_IMPROVE_MIN, naive_biased, agg_cv,
              HP_CV_MAX, indep_fires)) + summ, extra)


# ============================================================
# Formula self-test (GH order statistic + PR estimator limits + verbatim-formula bit-identity)
# ============================================================
def _formula_selftest() -> Tuple[bool, str]:
    # (a) Phi/logPhi correctness + monotone
    if abs(0.5 * math.erfc(0.0) - 0.5) > 1e-9:
        return False, "PHI_HALF_BROKEN"
    if not (_logPhi(1.0) > _logPhi(0.0) > _logPhi(-1.0)):
        return False, "LOGPHI_NOT_MONOTONE"
    # (b) large-margin signal wins ~ surely for any competitor count
    if p_win_extreme(30.0, 1.0, 0.0, 1.0, 1000.0) < 0.999:
        return False, "LARGE_MARGIN_NOT_WIN"
    # (c) monotone DECREASING in competitor count (more distractors -> lower win prob)
    prev = 2.0
    for n in (1.0, 10.0, 100.0, 1000.0):
        p = p_win_extreme(3.5, 3.9, 0.0, 4.8, n)
        if p > prev + 1e-9:
            return False, "PWIN_NOT_MONOTONE_IN_NCOMP n=%.0f p=%.4f prev=%.4f" % (n, p, prev)
        prev = p
    # (d) PR-corrected (n=PR-1 ~ 26) predicts a HIGHER win prob than naive-V (n=V-1 ~ 999): the correction
    #     lifts the over-predicted collapse. (mu_s,sig_s,mu_d,sig_d) approx the measured D8 geometry.
    p_pr = p_win_extreme(29.7, 3.9, 13.0, 4.8, 26.0)
    p_nv = p_win_extreme(29.7, 3.9, 13.0, 4.8, 999.0)
    if not (p_pr > p_nv + 1e-6):
        return False, "PR_NOT_ABOVE_NAIVE p_pr=%.4f p_nv=%.4f" % (p_pr, p_nv)
    # (e) PR estimator limits: identical codewords -> PR=1 (degenerate); orthogonal-ish independent -> PR>>1.
    degen = np.tile(np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float64)[None, :], (30, 1))
    pr_degen = participation_ratio(degen)
    if abs(pr_degen - 1.0) > 1e-6:
        return False, "PR_DEGENERATE_NOT_1 pr=%.4f" % pr_degen
    indep = _independent_codebook(200, BS, K_LOCAL, 0).astype(np.float64)
    pr_indep = participation_ratio(indep)
    if pr_indep < 100.0:
        return False, "PR_INDEP_TOO_LOW pr=%.2f (expected >> GSBC ~25)" % pr_indep
    # (f) PR in [1, V] for a real GSBC slice; and much less than V (correlated)
    cb = base._build_cbmax(7, BS, 250, 2)
    pr_gsbc = participation_ratio(cb[0:250])
    if not (1.0 <= pr_gsbc <= 250.0 and pr_gsbc < 60.0):
        return False, "PR_GSBC_OUT_OF_RANGE pr=%.2f" % pr_gsbc
    return True, ("FORMULA_SELFTEST_PASS (p_pr=%.4f>p_nv=%.4f; PR degen=%.3f indep=%.1f gsbc250=%.1f)"
                  % (p_pr, p_nv, pr_degen, pr_indep, pr_gsbc))


def _verbatim_check() -> Tuple[bool, str]:
    """Assert this cell's p_win_extreme is BIT-IDENTICAL to the exact-margin cell's CG'd formula (Gate D:
    the corrected model is the SAME machinery with one substituted exponent, not a re-implementation)."""
    try:
        import experiments.exp_comprehension_order_recovery_exact_margin_v1 as emc  # noqa
    except Exception as e:  # noqa: BLE001 (import diagnostics only)
        return True, "VERBATIM_SKIP (exact-margin cell not importable: %s)" % type(e).__name__
    for args in [(29.7, 3.9, 13.0, 4.8, 999.0), (29.7, 3.9, 13.0, 4.8, 26.0),
                 (3.5, 3.9, 0.0, 4.8, 1.0), (10.0, 2.0, 1.0, 2.0, 250.0)]:
        a = p_win_extreme(*args)
        b = emc.p_win_extreme(*args)
        if a != b:
            return False, "VERBATIM_MISMATCH args=%s this=%.10f emc=%.10f" % (args, a, b)
    return True, "VERBATIM_OK (p_win_extreme bit-identical to exact-margin cell)"


def _retrospective_offdisk() -> Tuple[Optional[bool], str, Dict[str, Any]]:
    """Zero-new-trials retrospective vs the landed comprehension surface. Reproduces the drill result:
    PR-corrected UNBIASES the order statistic (mean_ratio in [0.80,1.25]) while naive-V is biased
    (mean_ratio > NAIVE_UNBIASED_HI) and PR beats naive worst-cell error by >= 1.5x (per-seed). Skips
    gracefully if the landed metrics OR the GSBC pool are absent (remote)."""
    land = REPO / "data" / "exp_comprehension_envelope_superposition_vocab_v1" / "metrics.json"
    if not land.exists():
        return None, "RETRO_SKIP (landed comprehension metrics absent -- fresh measurement is primary)", {}
    if not base.POOL_PATH.exists():
        return None, "RETRO_SKIP (GSBC pool npz absent -- cannot rebuild geometry)", {}
    try:
        per = json.loads(land.read_text(encoding="utf-8"))["per_unit"]
    except (OSError, ValueError, KeyError) as e:
        return None, "RETRO_SKIP (landed metrics unreadable: %s)" % type(e).__name__, {}
    land_seeds = sorted({u["seed"] for u in per})
    land_D = sorted({u["D"] for u in per})
    land_V = sorted({u["V_ROLE"] for u in per})
    mom: Dict[Tuple[int, int], Tuple[float, float, float, float]] = {}
    prg: Dict[Tuple[int, int], float] = {}
    for seed in land_seeds:
        cb = base._build_cbmax(seed, BS, max(land_V), max(land_D))
        for D in land_D:
            mom[(seed, D)] = measure_moments(seed, D, V_REF, cb)
        for V in land_V:
            prg[(seed, V)] = participation_ratio(cb[0:V])
    pr_ps, nv_ps = [], []      # per-seed ratio-errs
    pr_r, nv_r = [], []        # seed-avg cell ratios
    for D in land_D:
        for V in land_V:
            rows = [u for u in per if u["D"] == D and u["V_ROLE"] == V]
            dp = float(np.mean([u["decode_part"] for u in rows]))
            mp1 = dp ** (1.0 / D) if dp > 0 else 0.0
            if not (SAT_LO < mp1 < SAT_HI):
                continue
            mD = tuple(np.mean([mom[(s, D)] for s in land_seeds], axis=0))
            prV = float(np.mean([prg[(s, V)] for s in land_seeds]))
            p_pr = p_win_extreme(mD[0], mD[1], mD[2], mD[3], max(prV - 1.0, 0.0))
            p_nv = p_win_extreme(mD[0], mD[1], mD[2], mD[3], float(V - 1))
            if p_pr > 1e-9:
                pr_r.append(mp1 / p_pr)
            if p_nv > 1e-9:
                nv_r.append(mp1 / p_nv)
            for s in land_seeds:
                us = [u for u in rows if u["seed"] == s]
                if not us:
                    continue
                m1 = float(us[0]["decode_part"]) ** (1.0 / D)
                if not (SAT_LO < m1 < SAT_HI):
                    continue
                pp = p_win_extreme(*mom[(s, D)], max(prg[(s, V)] - 1.0, 0.0))
                pn = p_win_extreme(*mom[(s, D)], float(V - 1))
                if pp > 1e-9:
                    pr_ps.append(_ratio_err(m1 / pp))
                if pn > 1e-9:
                    nv_ps.append(_ratio_err(m1 / pn))
    if not pr_r:
        return None, "RETRO_SKIP (no non-saturated landed decode cells)", {}
    pr_mean = float(np.mean(pr_r))
    nv_mean = float(np.mean(nv_r))
    pr_max = max([e for e in pr_ps if e])
    nv_max = max([e for e in nv_ps if e])
    improve = nv_max / pr_max if pr_max > 0 else None
    info = {"retro_n_cells": len(pr_r), "retro_pr_mean_ratio": round(pr_mean, 4),
            "retro_naive_mean_ratio": round(nv_mean, 4),
            "retro_pr_perseed_max_err": round(pr_max, 4), "retro_naive_perseed_max_err": round(nv_max, 4),
            "retro_improve_over_naive": round(improve, 4) if improve else None}
    direction_ok = (HP_BIAS_LO <= pr_mean <= HP_BIAS_HI
                    and nv_mean > NAIVE_UNBIASED_HI
                    and improve is not None and improve >= REL_IMPROVE_MIN)
    msg = ("RETRO n=%d PR mean_ratio=%.3f (unbiased) perseed_max=%.3f | NAIVE mean_ratio=%.3f (biased) "
           "perseed_max=%.3f | improve=%.2fx -> %s"
           % (len(pr_r), pr_mean, pr_max, nv_mean, nv_max, improve,
              "PR_CORRECTION_CONFIRMED" if direction_ok else "UNEXPECTED"))
    return direction_ok, msg, info


# ============================================================
# Driver
# ============================================================
def run_all(out_dir: Path, t0: float) -> Tuple[List[Dict[str, Any]], Optional[float]]:
    per_unit: List[Dict[str, Any]] = []
    total = len(SEEDS) * len(D_GRID) * len(V_GRID)
    unit = 0
    indep_ratios_maxV: List[float] = []
    for seed in SEEDS:
        cb_max = base._build_cbmax(seed, BS, V_ROLE_MAX, D_MAX)   # one geometry build per seed
        moments = {D: measure_moments(seed, D, V_REF, cb_max) for D in D_GRID}
        pr_gsbc = {V: participation_ratio(cb_max[0:V]) for V in V_GRID}                 # role-0 slice
        pr_indep = {V: participation_ratio(_independent_codebook(V, BS, K_LOCAL, seed)) for V in V_GRID}
        indep_ratios_maxV.append(pr_indep[max(V_GRID)] / pr_gsbc[max(V_GRID)])
        _say("  [seed %d] cb_max + moments + PR built | PR_gsbc=%s | PR_indep=%s"
             % (seed, {V: round(pr_gsbc[V], 1) for V in V_GRID}, {V: round(pr_indep[V], 1) for V in V_GRID}))
        for D in D_GRID:
            for V in V_GRID:
                r = run_unit(seed, D, V, cb_max, moments[D], pr_gsbc[V], pr_indep[V])
                per_unit.append(r)
                unit += 1
                _heartbeat(out_dir, unit, total, t0,
                           extra={"seed": seed, "D": D, "V": V, "meas_p1": r["meas_p1"],
                                  "p1_pr": r["p1_pr"], "ratio_pr": r["ratio_pr"]})
                _say("    [seed %d D=%d V=%d L=%d] decode_part=%.3f meas_p1=%.4f | PR=%.1f p1_pr=%.4f "
                     "p1_naive=%.4f p1_loose=%.4f | r_pr=%s r_naive=%s%s"
                     % (seed, D, V, D // 2, r["decode_part"], r["meas_p1"], r["pr_gsbc"], r["p1_pr"],
                        r["p1_naive"], r["p1_loose"], r["ratio_pr"], r["ratio_naive"],
                        " [SAT]" if r["saturated"] else ""))
    indep_ratio_maxV = float(np.mean(indep_ratios_maxV)) if indep_ratios_maxV else None
    return per_unit, indep_ratio_maxV


def _run(mode: str) -> int:
    out_dir = _out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    _write_start_marker(out_dir, mode, EXPECTED_N_UNITS)
    _say("[%s] mode=%s N=%d B=%d bs=%d k_local=%d D_grid=%s V_grid=%s seeds=%s trials=%d V_REF=%d expected=%d"
         % (ANCHOR_NAME, mode, N_DIM, B_TOTAL, BS, K_LOCAL, D_GRID, V_GRID, SEEDS, TRIALS, V_REF,
            EXPECTED_N_UNITS))

    ok_f, msg_f = _formula_selftest()
    if not ok_f:
        raise AssertionError("FORMULA_SELFTEST_FAIL: " + msg_f)
    _say("[formula] " + msg_f)
    ok_v, msg_v = _verbatim_check()
    if not ok_v:
        raise AssertionError("VERBATIM_CHECK_FAIL: " + msg_v)
    _say("[verbatim] " + msg_v)
    retro_ok, retro_msg, retro_info = _retrospective_offdisk()
    _say("[retro] " + retro_msg)

    per_unit, indep_ratio_maxV = run_all(out_dir, t0)
    verdict, vmsg, extra = compute_verdict(per_unit, len(per_unit), indep_ratio_maxV)
    extra["formula_selftest"] = msg_f
    extra["verbatim_check"] = msg_v
    extra["retrospective_offdisk"] = retro_msg
    extra["retrospective_info"] = retro_info
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg,
        "summary": "%s: comprehension order-recovery PR-CORRECTED self-margin (participation-ratio order "
                   "statistic) (%s)" % (verdict, mode),
        "run_mode": mode, "elapsed_s": round(elapsed, 2),
        "n_seeds": len(SEEDS), "n_units": len(per_unit), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_unit) >= EXPECTED_N_UNITS,
        "arms_differ_verified": extra.get("arms_differ_verified", False),
        "config_version": CONFIG_VERSION,
        "config": {"N": N_DIM, "B_TOTAL": B_TOTAL, "bs": BS, "k_local": K_LOCAL, "D_grid": D_GRID,
                   "V_grid": V_GRID, "seeds": SEEDS, "trials": TRIALS, "V_REF": V_REF,
                   "predictor": "GH64_extreme_value_order_statistic",
                   "mechanism": "n_comp=PR(V)-1 participation_ratio of codeword Gram (role-0 slice)",
                   "controls": {"naive_v": "n_comp=V-1 (falsified original)", "loose": "n_comp=1 (V-blind)",
                                "pr_independent": "PR of matched independent bipolar codebook (correlation "
                                                  "discriminator)"},
                   "measurement": "base.run_unit_VERBATIM (exp_comprehension_envelope_superposition_vocab_v1)",
                   "target": "per_role_decode_p1 = decode_part^(1/D)",
                   "kb_referent_declared": False},
        "hp_scope": {"pr_corrected": ["mean_ratio_unbiased", "perseed_ratio_err<=HP_RATIO_MAX",
                                      "hardest_cell<=HP_HARDEST_MAX", "improve>=1.5", "cv<=0.15"],
                     "naive_v": ["naive_biased_direction_gate_only"],
                     "loose": ["diagnostic_only"],
                     "pr_independent": ["correlation_discriminator_gate_only"]},
        "extra": extra, "per_unit": per_unit,
        "ts_iso": _now_iso(), "pid": os.getpid(), "host": platform.node(),
    }
    _write_metrics_atomic(out_dir, metrics)
    written = json.load(open(out_dir / "metrics.json"))
    assert written["run_mode"] == mode, "RUN_MODE_MISMATCH %s != %s" % (written["run_mode"], mode)

    _say("\n[%s] %s: %s" % (ANCHOR_NAME, verdict, vmsg))
    _say("[%s] metrics -> %s  elapsed=%.1fs" % (ANCHOR_NAME, out_dir / "metrics.json", elapsed))
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    ok_f, msg_f = _formula_selftest()
    assert ok_f, "FORMULA_SELFTEST_FAIL: " + msg_f
    ok_v, msg_v = _verbatim_check()
    assert ok_v, "VERBATIM_CHECK_FAIL: " + msg_v
    retro_ok, retro_msg, _info = _retrospective_offdisk()
    cb = base._build_cbmax(7, BS, max(V_GRID + [V_REF]), max(D_GRID))
    mu_s, sig_s, mu_d, sig_d = measure_moments(7, 8, V_REF, cb)
    geom_ok = (mu_s > mu_d > 0 and sig_d > 0)
    pr_gsbc = participation_ratio(cb[0:1000])
    pr_indep = participation_ratio(_independent_codebook(1000, BS, K_LOCAL, 7))
    pr_ok = (1.0 <= pr_gsbc < 60.0 and pr_indep > 5.0 * pr_gsbc)   # correlation discriminator fires
    r = run_unit(7, 8, 1000, cb, (mu_s, sig_s, mu_d, sig_d), pr_gsbc, pr_indep)
    unit_ok = (0.0 <= r["meas_p1"] <= 1.0 and r["p1_pr"] > r["p1_naive"] - 1e-9)  # PR lifts naive collapse
    ok = ok_f and ok_v and geom_ok and pr_ok and unit_ok and (retro_ok is not False)
    _say("[%s] SELFTEST %s: formula=%s | %s | geom(D8) mu_s=%.2f mu_d=%.2f sig_d=%.2f ok=%s | "
         "PR gsbc=%.1f indep=%.1f (ratio %.1fx) ok=%s | unit(D8V1000) meas_p1=%.4f p1_pr=%.4f p1_naive=%.4f "
         "ok=%s | %s [%.1fs]"
         % (ANCHOR_NAME, "PASS" if ok else "FAIL", msg_f, msg_v, mu_s, mu_d, sig_d, geom_ok, pr_gsbc,
            pr_indep, pr_indep / pr_gsbc, pr_ok, r["meas_p1"], r["p1_pr"], r["p1_naive"], unit_ok, retro_msg,
            time.perf_counter() - t0))
    return 0 if ok else 1


def main() -> int:
    if RUN_MODE == "self_test":
        return _run_selftest()
    return _run(RUN_MODE)


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
