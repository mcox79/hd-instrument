"""control_branching_depth_chain_survival_self_margin_v1 -- does the chain-survival ORDER-
STATISTIC self-margin predict the FLAT control-gate's branching-depth collapse, from a SHALLOW
anchor, and does it BEAT the Hick-entropy first-order predictor?

WHY (Director drill 2026-07-06; extends the self-margin frontier from decode/reasoning/language
to CONTROL):
  The landed cell exp_pfc_gate_branching_depth_entropy_grid_v1 (FULL=HARD_PASS) shows a FLAT
  Go/NoGo control gate COLLAPSES with decision-entropy log2(n_ops)*depth across an
  n_ops in {2,3,4} x depth in {4,6,8} grid; hierarchical (bounded-horizon) decomposition recovers
  it. Per-gate decision = argmax over n_ops competing operators. A depth-d control chain SURVIVES
  only if ALL d gating decisions are correct, so the natural model is series-reliability over an
  extreme-value order statistic (the SAME GH64 kernel already CHAIN_GRADE for RNS decode / FHRR
  capacity / reasoning-depth):
     P_chain(n_ops, d) = prod_{r=1}^{d} P_gate(n_ops, mu(r)),   P_gate = E_z[ Phi(mu+z)^(n_ops-1) ]
  where r is the per-hop REMAINING HORIZON (distance to the final goal) and mu(r) is the per-gate
  SR-reachability margin at horizon r. The Hick decision-entropy predictor -ln(survival) ~
  d*log2(n_ops) is the first-order shadow of this exact chain-survival order statistic.

WHY MM NOT CG (the honest bound; the cell declares crlb_n/a):
  The per-gate margin mu(r) is a LEARNED successor-representation (SR) reachability, NOT a clean
  closed-form codebook decode margin. It has NO closed form and, critically, it DEGRADES with
  horizon r (reach starvation toward a receding goal -- exactly the failure hierarchy fixes). So
  this is SEMI-EMPIRICAL: MEASURE mu(r) at SHALLOW horizons, PROJECT to the deep grid, TEST whether
  the projection predicts the observed collapse. Expected tier: MEASURED_MECHANISM.

  Off-disk recon vs the LANDED N=8192 grid (MEASURED@data/exp_pfc_gate_branching_depth_entropy_grid
  _v1/metrics.json:per_regime.*.flat_gonogo) already establishes the KEY honest fact this cell
  builds on: the LITERAL constant-margin projection P_gate(mu_hat)^depth (a SINGLE per-gate margin)
  does NOT predict the flat collapse -- it OVER-predicts survival (held-out d6,d8 RMSE ~0.34-0.41)
  because the effective per-gate margin DROPS with depth (n_ops=2: mu_hat 2.78@d4 -> 1.85@d6 ->
  1.29@d8). The collapse is SUPER-GEOMETRIC. Therefore the constant-margin member is a DOCUMENTED
  BOUND (retained as a control arm), and the mechanism under test is the HORIZON-AWARE member
  (margin decays with remaining horizon), which has the structural DOF to capture super-geometric
  collapse. (NOTE: the landed grid TUNED w_reach PER DEPTH, so it is NOT a single fixed gate; a
  clean fit-shallow-project-deep test REQUIRES a single fixed gate, which this cell constructs by
  tuning the gate ONCE on the shallow anchor and freezing it across depths. This cell therefore
  GENERATES its own commensurate grid rather than scoring the per-depth-tuned landed grid; the
  landed grid is a QUALITATIVE super-geometric-shape cross-check only, declared SHAPE_DRIFT.)

MECHANISM UNDER TEST (NOT assumed): the HORIZON-AWARE chain-survival order-statistic self-margin.
  From end-to-end FLAT-gate accuracy at SHALLOW anchor depths {1,2,3,4} (a SINGLE frozen gate),
  reconstruct the per-horizon per-gate survival q(r) = flat(r)/flat(r-1) (r=1..4; the chain-
  survival product law flat(d)=prod_{r<=d} q(r)), invert to the order-statistic margin mu(r), fit a
  horizon-linear margin mu(r)=mu0 - beta*(r-1) SHARED across n_ops (the branching factor enters
  ONLY via the order statistic's competitor count), then PROJECT to the deep grid and PREDICT the
  HELD-OUT flat accuracy at depth {6,8}. Compare to observed. Two retained controls + one firing
  control keep it honest:
    (C1) CONST-margin (the note's literal P_gate(mu_hat)^d): a SINGLE frozen margin -> geometric
         projection. Expected to OVER-predict (super-geometric collapse) -> the documented bound.
    (C2) HICK first-order: -ln(survival)=C*log2(n_ops)*d (the entropy predictor the landed cell
         used). The first-order shadow to BEAT.
    (F)  FIRING CONTROL: SHUFFLE the per-op gate scores before argmax -> selection is uniform ->
         per-gate survival -> 1/n_ops -> the fitted margin mu0 COLLAPSES to ~0. The margin (not a
         generic depth-monotone artifact) must be load-bearing: real mu0 >> shuffled mu0.

DESIGN CHOICES that make the order-statistic claim clean:
  - V FIXED across n_ops (isolate the BRANCHING factor; codebook difficulty held constant so a
    SHARED mu(r) curve across n_ops is a principled claim -- n_ops enters only via P_gate).
  - Gate FROZEN: alpha + w_reach tuned ONCE on the shallow anchor (d=4 train), applied to ALL
    depths. Tests a SINGLE gate's per-horizon margin decay (not per-depth re-tuning).
  - Anchor depths {1,2,3,4}; VALIDATION report at d=4 (deepest anchor); HELD-OUT gate at {6,8}.

ARMS / MEASUREMENTS (per (n_ops, seed), V fixed, gamma fixed; paired by identical test chains):
  flat_obs(n_ops, d)      end-to-end FROZEN flat gonogo gate accuracy, d in {1,2,3,4,6,8} [MEASURE]
  q_tf(n_ops, r)          teacher-forced per-horizon gate-correct along the TRUE trajectory, r=1..4
                          -- validates the chain-survival PRODUCT LAW vs ratio-reconstruction [X-CHK]
  flat_shuf(n_ops, d)     SHUFFLED-score gate accuracy (firing control) [CTL]
  PREDICTORS (fit on anchor d<=4, predict held-out d in {6,8}):
    pred_horizon(n_ops,d)  HORIZON-AWARE order-statistic (mu0,beta shared)          [MECHANISM]
    pred_const(n_ops,d)    CONST-margin geometric = flat(4)^(d/4)                   [CONTROL/BOUND]
    pred_hick1(n_ops,d)    HICK first-order exp(-C*log2(n_ops)*d)                    [CONTROL]
    pred_hickp(n_ops,d)    HICK power exp(-C*log2(n_ops)*d^p) (equal-DOF fairness)   [CONTROL/report]

PRIMARY DISCRIMINATOR (held-out d in {6,8} x n_ops = 6 points; RMSE vs observed flat):
  rmse_horizon  <= observed collapse well  (the mechanism predicts the deep collapse)
  const_gap = rmse_const - rmse_horizon    (horizon-dependence is load-bearing; const over-predicts)
  hick_gap  = rmse_hick1  - rmse_horizon    (order statistic beats the first-order entropy shadow)
  mu0_real vs mu0_shuf                      (firing: shuffle destroys the margin)

CONTRACT (pre-registered BEFORE running; no-smoke bands):
  HARD_PASS (chain-survival self-margin EXTENDS to CONTROL, MM-grade):
    rmse_horizon <= HP_RMSE (0.12) AND const_gap >= HP_CONST_GAP (0.10) AND hick_gap >= HP_HICK_GAP
    (0.03) AND firing (mu0_real >= MU_REAL_MIN 0.5 AND mu0_shuf <= MU_SHUF_MAX 0.20) AND collapse
    fires (flat_obs(op4,d8) <= COLLAPSE_MAX 0.35 AND every flat_obs(n_ops,d1) in (0.50,0.995)) AND
    product-law X-check (mean|q_tf - q_ratio| <= TF_TOL 0.15 over anchor r) AND cross-seed
    cv(rmse_horizon) <= HP_CV (0.40).
  HARD_FAIL (honest ACCEPT-boundary -- chain-survival order statistic does NOT extend to the flat
    control gate): rmse_horizon > HF_RMSE (0.22) OR rmse_horizon > rmse_hick1 + 0.05 (fails to beat
    even the first-order Hick shadow).
  MIDDLE_BAND: horizon-aware helps (const_gap>0) with rmse_horizon in (0.12,0.22], OR beats Hick-
    first but not the equal-DOF Hick-power, OR misses exactly one HARD_PASS sub-gate.
  INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE: no observed collapse (flat_obs(op4,d8) > COLLAPSE_MAX) or
    shallow gate already broken (some flat_obs(n_ops,d1) <= 0.50) -> respec regime, NOT a refutation.
  Reported REGARDLESS: full per-(n_ops,d) observed + predicted surface; mu(r) fit (mu0,beta);
  per-seed rmse; the super-geometric SHAPE cross-check vs the landed N=8192 grid (SHAPE_DRIFT).

FRAMING (USER-LOCKED): monitor-not-control. The self-margin PREDICTS the substrate's OWN usable
  control depth (from shallow measurement, how deep before the flat gate collapses); it NEVER edits
  the gate. Narrow glass-box MONITOR step. re-encode HELD.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): pred_horizon vs pred_const vs pred_hick1 prediction
#   surfaces hash-distinct; flat_obs vs flat_shuf hash-distinct.
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json) + per-seed resumable partials.
# - except SystemExit: raise BEFORE except Exception (no BaseException in main).
# - crlb_n/a: the per-gate margin mu(r) is a LEARNED SR reachability with NO closed-form noise floor
#   (SEMI-EMPIRICAL; declared MM not CG). Discriminator reachability by feasibility: the LANDED
#   N=8192 grid MEASURES the flat collapse (flat op4_d8=0.082) and the constant-margin OVER-predict
#   (RMSE~0.34-0.41 off-disk), so the collapse-to-predict and the const-fail bound both exist.
# - baseline_in_band (AG): shallow flat_obs(n_ops,d1) must be in (0.50,0.995) (gate works shallow)
#   AND flat_obs(op4,d8) must collapse (<=0.35); asserted as the discriminator-fires gate.
# - discriminator survives scale: this is a PREDICTION-MATCH test with a shallow->deep held-out
#   split; smoke fires the SAME collapse (op4 depth-8 flat collapse) at reduced N as a full-N
#   preview (option C). The const-margin FAILS and horizon-aware structure is what differs.
# - HARD_PASS strictly above floor: rmse_horizon <= 0.12 AND >= 0.10 tighter than const AND
#   >= 0.03 tighter than Hick (META_RULE_L strict bands, not >= floors).
# - HP_SCOPE: HARD_PASS RMSE/gap gates apply to pred_horizon (MECHANISM); collapse-fires gate
#   applies to flat_obs; firing gate applies to flat_shuf; product-law X-check applies to q_tf.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (per-seed unit; each unit spans all n_ops x depths).
# - per-unit failure-class instrumentation (no bare except; per-seed fatal-flag + failure_class).
# - calibration_check: adaptive_with_discriminator_gate (gate alpha+w_reach tuned on shallow anchor;
#   discriminator = collapse-fires + const-fail + firing all still measured and gated).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.

Compute architecture: (b) sequential-CPU with justification. SR-TD training + gate scoring are
  batched matmuls, but chains are evaluated with genuine sequential within-chain hop dependencies
  and the cell runs at REDUCED N (self-contained shallow+deep grid, NOT the landed N=8192) so CPU
  wall stays bounded; remote_cpu_queue per Director. GPU not required (reduced N; the mechanism is
  the shallow->deep PROJECTION, scale-invariant given a collapsing gate). Storage strategy:
  no_storage (learned operator matrices W_op + SR M; no item store; no bundled superposition).
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line +
  per-(seed,n_ops) heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-06 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-06_control_branching_depth_chain_survival_self_margin_v1.md
Reuses primitives + SR trainer + flat gonogo gate VERBATIM from
  experiments/exp_pfc_gate_branching_depth_entropy_grid_v1.py
Reuses the GH64 order-statistic kernel pattern from
  experiments/exp_reasoning_depth_exact_order_statistic_self_margin_v1.py
Cites: data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json (landed flat collapse grid)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import hashlib
import json
import math
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials, get_output_dir,
)

ANCHOR_NAME = "control_branching_depth_chain_survival_self_margin_v1"

# --------------------------- CLI / run-mode ---------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else ("selftest" if _ARGS.self_test
                  else os.environ.get("HDLAB_RUN_MODE", "full").lower()))
SELF_TEST_MODE = bool(_ARGS.self_test)

# CPU cell (reduced-N self-contained grid; remote_cpu_queue). Default cpu; use cuda only if the
# runner explicitly provides it AND allows (this cell is CPU-designed so we force cpu unless a
# smoke/full override). Runner does not pass argv; default cpu is the defensive choice.
_FORCE_CPU = os.environ.get("HDLAB_FORCE_CPU", "1") != "0"
DEVICE = torch.device("cpu") if _FORCE_CPU else torch.device(
    "cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float32

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
HP_RMSE = 0.12              # horizon-aware held-out RMSE must be <= this
HP_CONST_GAP = 0.10        # rmse_const - rmse_horizon (const over-predicts; horizon-dep load-bearing)
HP_HICK_GAP = 0.03         # rmse_hick1 - rmse_horizon (beat the first-order entropy shadow)
HF_RMSE = 0.22             # HARD_FAIL if horizon-aware RMSE exceeds this
HF_HICK_MARGIN = 0.05      # HARD_FAIL if horizon fails to beat Hick even by this margin
MU_REAL_MIN = 0.50         # firing: real fitted margin intercept must exceed this
MU_SHUF_MAX = 0.20         # firing: shuffled fitted margin intercept must be at/below chance (~0)
COLLAPSE_MAX = 0.35        # discriminator-fires: op4 depth-8 flat must collapse below this
SHALLOW_LO = 0.50          # discriminator-fires: shallow (d=1) flat must be above this (gate WORKS)
# NOTE: a SATURATED shallow gate (d1 ~ 1.0) is the HEALTHY expected case, NOT a discriminator
# failure -- the fit already EXCLUDES saturated anchor points (mu clamped at MU_CEIL) and the
# collapse is measured across depths. The discriminator-fires condition is therefore: deep collapse
# present (flat op_max d8 <= COLLAPSE_MAX) AND shallow gate works (d1 > SHALLOW_LO) AND the anchor
# carries measurable decay (deepest-anchor flat < ANCHOR_DECAY_MAX for the max n_ops). No upper cap
# on d1 (smoke revealed n_ops=4 d1 saturates at reduced N/V; META_RULE_AG saturation is expected,
# not a failure -- FULL uses larger V which de-saturates).
ANCHOR_DECAY_MAX = 0.90    # deepest-anchor (d=TUNE_DEPTH) flat for the MAX n_ops must show decay
TF_TOL = 0.15              # product-law X-check: |teacher-forced q - ratio-reconstructed q|
HP_CV_MAX = 0.40           # cross-seed cv on rmse_horizon (RMSE is noisy; lenient)
MB_RMSE_HI = 0.22          # MIDDLE_BAND upper rmse (== HF_RMSE)

# margin inversion clamps (P_gate range is [1/n_ops, 1])
MU_FLOOR = -3.0
MU_CEIL = 12.0

# --------------------------- gate hyperparameters (frozen from shallow) ----------
GAMMA = 0.85                       # FIXED (smoke of the landed cell proved gamma inert at depth)
DENSITY = 0.21                     # n_train_triples_per_op / V (matches landed)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]
TUNE_DEPTH = 4                     # freeze the gate by tuning on this (deepest anchor) depth's train

ANCHOR_DEPTHS = [1, 2, 3, 4]
HELDOUT_DEPTHS = [6, 8]
DEPTHS_ALL = [1, 2, 3, 4, 6, 8]

# --------------------------- config (selftest / smoke / full) --------------------
# V is FIXED across n_ops (isolate the branching factor). n_ops in {2,3,4}.
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_OPS_SET = [2, 4]
    V_FIXED = 40
    N_TRAIN_CHAINS = 16
    N_TEST_CHAINS = 12
    SR_STEPS = 150
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # multi-seed (3). Fires the collapse at reduced N (op4 depth-8 must collapse) as a full-N
    # preview (option C). Verifies shallow gate in-band + const-fail + firing.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    N_OPS_SET = [2, 3, 4]
    V_FIXED = 300
    N_TRAIN_CHAINS = 64
    N_TEST_CHAINS = 96
    SR_STEPS = 900
    SR_BATCH = 96
    SR_LR = 0.5
    ROLLOUT_PER_V = 12
else:  # full
    N_DIM = 4096
    SEEDS = [7, 17, 23, 31, 41]
    N_OPS_SET = [2, 3, 4]
    V_FIXED = 700
    N_TRAIN_CHAINS = 200
    N_TEST_CHAINS = 200
    SR_STEPS = 2000            # > smoke (900) for cleaner SR; bounded for CPU wall (~15min/seed)
    SR_BATCH = 160
    SR_LR = 0.5
    ROLLOUT_PER_V = 40

ROLLOUT_CAP = 4000 if RUN_MODE in ("smoke", "selftest") else 120000

EXPECTED_N_UNITS = len(SEEDS)     # one resumable unit per seed (each spans all n_ops x depths)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_ops_set=%s,V=%d,seeds=%s,gamma=%.2f,depths=%s,anchor_d=%s,heldout_d=%s,"
    "density=%.3f,sr_steps=%d,sr_batch=%d,rollout_per_V=%d,lr=%.2f,tune_depth=%d,alphas=%s,"
    "w_reach=%s,n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_RMSE<=%.2f,const_gap>=%.2f,hick_gap>=%.2f,mu_real>=%.2f,mu_shuf<=%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS_SET, V_FIXED, SEEDS, GAMMA, DEPTHS_ALL, ANCHOR_DEPTHS, HELDOUT_DEPTHS,
    DENSITY, SR_STEPS, SR_BATCH, ROLLOUT_PER_V, SR_LR, TUNE_DEPTH, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_RMSE, HP_CONST_GAP, HP_HICK_GAP, MU_REAL_MIN, MU_SHUF_MAX,
)

_T0 = time.time()


# ============================================================================
# GH64 order-statistic kernel (probabilists' Hermite): P_gate = E_z[Phi(mu+z)^(n_ops-1)]
# ============================================================================
def _phi_cdf(x: np.ndarray) -> np.ndarray:
    """Standard normal CDF via erf (no scipy dependency at runtime)."""
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


# hermegauss(64): nodes/weights for weight exp(-x^2/2); normalize to expectation over N(0,1)
def _hermegauss64() -> Tuple[np.ndarray, np.ndarray]:
    try:
        from numpy.polynomial.hermite_e import hermegauss
        x, w = hermegauss(64)
        return x.astype(np.float64), (w / math.sqrt(2.0 * math.pi)).astype(np.float64)
    except Exception:
        # Fallback: fine trapezoid over +-9 sigma (never expected; keeps cell robust)
        z = np.linspace(-9.0, 9.0, 4001)
        wz = np.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
        wz = wz / wz.sum()
        return z, wz


_GHX, _GHW = _hermegauss64()


def p_gate(n_ops: int, mu: float) -> float:
    """Order-statistic per-gate survival: E_z[ Phi(mu+z)^(n_ops-1) ], z~N(0,1)."""
    cdf = _phi_cdf(mu + _GHX)
    return float(np.sum(_GHW * np.power(cdf, n_ops - 1)))


def mu_from_pgate(n_ops: int, q: float) -> float:
    """Invert p_gate(n_ops, mu) = q for mu, via monotone bisection. Clamped to [MU_FLOOR,MU_CEIL]."""
    lo_q = 1.0 / float(n_ops)
    q = min(max(q, lo_q + 1e-9), 1.0 - 1e-9)
    f_lo = p_gate(n_ops, MU_FLOOR) - q
    f_hi = p_gate(n_ops, MU_CEIL) - q
    if f_lo >= 0:
        return MU_FLOOR
    if f_hi <= 0:
        return MU_CEIL
    lo, hi = MU_FLOOR, MU_CEIL
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if p_gate(n_ops, mid) - q > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ============================================================================
# defensive-error-checking helpers (start marker / crash diag / heartbeat)
# ============================================================================
def _write_start_marker(out_dir: Path) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS,
        "host": platform.node(),
        "device": str(DEVICE),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _atomic_write_metrics(out_dir: Path, payload: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": round(time.time() - _T0, 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }
    try:
        _atomic_write_metrics(out_dir, diag)
    except Exception as e:
        print("[_write_crash_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _heartbeat(out_dir: Path, unit_idx: int, total: int, note: str = "") -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(),
               "unit_idx": unit_idx, "total_units": total,
               "elapsed_s": round(time.time() - _T0, 1), "note": note}
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ============================================================================
# primitives (torch, batched) -- reused verbatim from the landed branching-depth cell
# ============================================================================
def _norm_rows(X: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return X / (X.norm(dim=-1, keepdim=True) + eps)


def make_bipolar_E(V: int, n: int, gen: torch.Generator) -> torch.Tensor:
    X = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE, dtype=DTYPE) * 2 - 1)
    return _norm_rows(X)


def cleanup_batched(vecs: torch.Tensor, E: torch.Tensor
                    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    vn = _norm_rows(vecs)
    sims = vn @ E.transpose(0, 1)
    manifold, idx = sims.max(dim=1)
    return idx, E[idx], manifold


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


def reach_rank_chance(n_ops: int) -> float:
    return 1.0 / float(n_ops)


# ============================================================================
# KB + chains (exact-length paths; train and test disjoint) -- reused verbatim
# ============================================================================
def make_kb_and_chains(n_ops: int, V: int, density: float,
                       n_train_chains: int, n_test_chains: int,
                       depths: List[int], g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]]]:
    n_train_triples = n_triples_per_op(V)
    per_op: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    for _ in range(n_train_triples * n_ops):
        s = int(g.integers(0, V)); o = int(g.integers(0, V))
        op = int(g.integers(0, n_ops))
        if s != o:
            per_op[op].append((s, o))

    def _grow_chain(depth: int) -> Tuple[int, List[int], int]:
        s = int(g.integers(0, V))
        cur = s
        op_seq: List[int] = []
        for _ in range(depth):
            op = int(g.integers(0, n_ops))
            cands = [o for (ss, o) in per_op[op] if ss == cur]
            if not cands:
                new_o = int(g.integers(0, V))
                while new_o == cur:
                    new_o = int(g.integers(0, V))
                per_op[op].append((cur, new_o))
                cur = new_o
            else:
                cur = int(cands[g.integers(0, len(cands))])
            op_seq.append(op)
        return (s, op_seq, cur)

    train_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    test_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    for depth in depths:
        train_by_d[depth] = [_grow_chain(depth) for _ in range(n_train_chains)]
        test_by_d[depth] = [_grow_chain(depth) for _ in range(n_test_chains)]
    return per_op, train_by_d, test_by_d


def build_adjacency(per_op: List[List[Tuple[int, int]]], n_ops: int
                    ) -> List[Dict[int, List[int]]]:
    adj: List[Dict[int, List[int]]] = [dict() for _ in range(n_ops)]
    for op in range(n_ops):
        for (s, o) in per_op[op]:
            adj[op].setdefault(s, []).append(o)
    return adj


def collect_rollout_transitions(adj: List[Dict[int, List[int]]], n_ops: int, V: int,
                                n_transitions: int, max_len: int,
                                g: np.random.Generator) -> np.ndarray:
    out: List[Tuple[int, int]] = []
    guard = 0
    while len(out) < n_transitions and guard < n_transitions * 50:
        guard += 1
        cur = int(g.integers(0, V))
        for _ in range(max_len):
            ops_avail = [op for op in range(n_ops) if cur in adj[op] and adj[op][cur]]
            if not ops_avail:
                break
            op = int(ops_avail[g.integers(0, len(ops_avail))])
            outs = adj[op][cur]
            nxt = int(outs[g.integers(0, len(outs))])
            out.append((cur, nxt))
            cur = nxt
            if len(out) >= n_transitions:
                break
    if not out:
        return np.zeros((0, 2), dtype=np.int64)
    return np.asarray(out, dtype=np.int64)


def build_W_ops(per_op: List[List[Tuple[int, int]]], E: torch.Tensor, n: int, n_ops: int
                ) -> List[torch.Tensor]:
    W_ops: List[torch.Tensor] = []
    for op in range(n_ops):
        triples = per_op[op]
        if not triples:
            W_ops.append(torch.zeros((n, n), dtype=DTYPE, device=DEVICE))
            continue
        arr = torch.tensor(triples, dtype=torch.long, device=DEVICE)
        S = E[arr[:, 0]]
        O = E[arr[:, 1]]
        W_ops.append((S.transpose(0, 1) @ O) / float(n))
    return W_ops


# ============================================================================
# cfrpe-trained SR transport M (TD(0); gamma FIXED) -- reused verbatim
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> torch.Tensor:
    M = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    K = transitions.shape[0]
    if K < 2:
        return M
    cur_t = torch.tensor(transitions[:, 0], dtype=torch.long, device=DEVICE)
    nxt_t = torch.tensor(transitions[:, 1], dtype=torch.long, device=DEVICE)
    sqrt_n = math.sqrt(float(n))
    for step in range(steps):
        decay = 1.0 - (1.0 - LR_DECAY_END) * (step / max(1, steps - 1))
        st = torch.randint(0, K, (batch,), generator=gen, device=DEVICE)
        Ecur = E[cur_t[st]]
        Enxt = E[nxt_t[st]]
        pred = Ecur @ M
        with torch.no_grad():
            boot = Enxt + gamma * (Enxt @ M)
        error = boot - pred
        e_norm = error.norm(dim=1) / sqrt_n
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_c = torch.clamp(ratio, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
        lr_per = base_lr * decay * ratio_c
        dM = (Ecur.transpose(0, 1) @ (error * lr_per.unsqueeze(1))) / float(batch)
        M = M + dM
    return M


def reach_value(cand_E: torch.Tensor, goal_E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


# ============================================================================
# FLAT gonogo gate -- frozen (alpha,w_reach); supports normal + shuffled-score firing control
# ============================================================================
def _chain_tensors(chains: List[Tuple[int, List[int], int]]
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)
    return starts, targets, op_seqs


def run_flat_gate(chains, W_ops: List[torch.Tensor], E: torch.Tensor, M: torch.Tensor,
                  depth: int, alpha: float, w_reach: float, shuffle_scores: bool,
                  gen: torch.Generator) -> np.ndarray:
    """End-to-end FLAT gonogo gate toward the FINAL goal. If shuffle_scores (FIRING CONTROL), the
    per-op gate scores are DESTROYED: the chosen op is drawn UNIFORMLY at random per (chain,hop)
    instead of by argmax over the margin -> per-gate survival collapses to chance 1/n_ops. This
    decouples the winning op from its gate score (the faithful 'shuffle the scores' null); simply
    co-permuting scores+cand_idx would be a no-op because argmax preserves the score/candidate
    pairing. Returns correct[n_chains] (bool)."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    row = torch.arange(n_chains, device=DEVICE)
    for _hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * _norm_rows(goal_E)).sum(dim=1)
            reach = reach_value(cleaned, goal_E, M)
            scores[:, op] = w_manifold * manifold + alpha * goal_sim + w_reach * reach
        if shuffle_scores:
            # margin destroyed -> uniform-random op selection (chance gate)
            chosen = torch.randint(0, n_ops, (n_chains,), generator=gen, device=DEVICE)
        else:
            chosen = scores.argmax(dim=1)
        new_idx = cand_idx[row, chosen]
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool)


def teacher_forced_per_horizon(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                               M: torch.Tensor, depth: int, alpha: float, w_reach: float
                               ) -> Dict[int, Tuple[int, int]]:
    """Along the TRUE trajectory (teacher-forced), does the frozen gate pick the true op at each
    hop? Bin by remaining horizon r = depth-hop. Returns {r: (hits, total)}. This measures the
    per-horizon per-gate survival q(r) independent of error propagation -> validates the product
    law flat(d)=prod_r q(r)."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    out: Dict[int, Tuple[int, int]] = {}
    for hop in range(depth):
        r = depth - hop  # remaining horizon at this hop (goal is r hops away)
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            outv = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(outv, E)
            cand_idx[:, op] = idx
            outv_n = _norm_rows(outv)
            goal_sim = (outv_n * _norm_rows(goal_E)).sum(dim=1)
            reach = reach_value(cleaned, goal_E, M)
            scores[:, op] = w_manifold * manifold + alpha * goal_sim + w_reach * reach
        pred_op = scores.argmax(dim=1)
        true_op = op_seq_t[:, hop]
        hits = int((pred_op == true_op).sum().item())
        h0, t0 = out.get(r, (0, 0))
        out[r] = (h0 + hits, t0 + n_chains)
        # advance along TRUE trajectory
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, true_op]
        state = E[new_idx]
    return out


# ============================================================================
# model fitting (numpy; order-statistic self-margin)
# ============================================================================
def reconstruct_q(flat_by_depth: Dict[int, float], n_ops: int) -> Dict[int, float]:
    """q(r) = flat(r)/flat(r-1) for r in ANCHOR_DEPTHS (flat(0)=1). Clamp to (1/n_ops, 1)."""
    lo = 1.0 / float(n_ops)
    q: Dict[int, float] = {}
    prev = 1.0
    for r in ANCHOR_DEPTHS:
        fr = flat_by_depth.get(r, None)
        if fr is None:
            continue
        ratio = fr / max(prev, 1e-6)
        q[r] = float(min(max(ratio, lo + 1e-6), 1.0 - 1e-6))
        prev = fr
    return q


def fit_horizon_margin(q_points: List[Tuple[int, int, float]]) -> Tuple[float, float]:
    """Fit SHARED mu(r) = mu0 - beta*(r-1) across all (n_ops, r) anchor points via LS on the
    inverted margins. q_points: list of (n_ops, r, q). Returns (mu0, beta)."""
    rows = []
    ys = []
    for (n_ops, r, q) in q_points:
        mu = mu_from_pgate(n_ops, q)
        # exclude saturated/degenerate clamps from the linear fit (uninformative)
        if mu <= MU_FLOOR + 1e-6 or mu >= MU_CEIL - 1e-6:
            continue
        rows.append([1.0, -(r - 1.0)])
        ys.append(mu)
    if len(rows) < 2:
        # fallback: constant margin from mean of available
        allmu = [mu_from_pgate(n, q) for (n, r, q) in q_points]
        return (float(np.mean(allmu)) if allmu else 0.0), 0.0
    A = np.asarray(rows, dtype=np.float64)
    b = np.asarray(ys, dtype=np.float64)
    coef, *_ = np.linalg.lstsq(A, b, rcond=None)
    mu0, beta = float(coef[0]), float(coef[1])
    return mu0, beta


def fit_const_margin(q_points: List[Tuple[int, int, float]]) -> float:
    mus = []
    for (n_ops, r, q) in q_points:
        mu = mu_from_pgate(n_ops, q)
        if MU_FLOOR + 1e-6 < mu < MU_CEIL - 1e-6:
            mus.append(mu)
    return float(np.mean(mus)) if mus else 0.0


def fit_hick(anchor_flat: List[Tuple[int, int, float]], power: bool) -> Tuple[float, float]:
    """Fit -ln(flat) = C*log2(n_ops)*d^p on anchor points. If not power, p fixed at 1.
    anchor_flat: list of (n_ops, d, flat). Returns (C, p)."""
    xs = []
    ys = []
    for (n_ops, d, flat) in anchor_flat:
        ys.append(-math.log(max(flat, 1e-6)))
        xs.append((math.log2(n_ops), float(d)))
    ys = np.asarray(ys, dtype=np.float64)
    if not power:
        # y = C * (log2n * d)  -> 1 param LS
        feat = np.asarray([lx * dd for (lx, dd) in xs], dtype=np.float64)
        denom = float(np.dot(feat, feat))
        C = float(np.dot(feat, ys) / denom) if denom > 1e-12 else 0.0
        return C, 1.0

    # y = C * log2n * d^p ; grid-search p, LS on C
    best = (1e18, 0.0, 1.0)
    for p in np.linspace(0.6, 2.6, 41):
        feat = np.asarray([lx * (dd ** p) for (lx, dd) in xs], dtype=np.float64)
        denom = float(np.dot(feat, feat))
        C = float(np.dot(feat, ys) / denom) if denom > 1e-12 else 0.0
        resid = ys - C * feat
        sse = float(np.dot(resid, resid))
        if sse < best[0]:
            best = (sse, C, float(p))
    return best[1], best[2]


def predict_horizon(n_ops: int, d: int, mu0: float, beta: float) -> float:
    prod = 1.0
    for r in range(1, d + 1):
        prod *= p_gate(n_ops, mu0 - beta * (r - 1))
    return prod


def predict_const_geom(n_ops: int, d: int, flat4: float) -> float:
    """CONST-margin geometric projection anchored on shallow: flat(4)^(d/4) (the note's literal
    single-margin P_gate(mu_hat)^d). flat4 is the measured shallow flat at TUNE_DEPTH."""
    if flat4 <= 1e-6:
        return 0.0
    return float(flat4 ** (d / float(TUNE_DEPTH)))


def predict_hick(n_ops: int, d: int, C: float, p: float) -> float:
    return float(math.exp(-C * math.log2(n_ops) * (d ** p)))


# ============================================================================
# per-seed runner
# ============================================================================
def _tune_gate(train_c, W_ops, E, M, gen) -> Tuple[float, float]:
    """Freeze the gate by tuning alpha then w_reach on the shallow TUNE_DEPTH train chains."""
    best_alpha, best_acc = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_flat_gate(train_c, W_ops, E, M, TUNE_DEPTH, a, 0.0, False, gen).mean()
        if acc > best_acc:
            best_acc, best_alpha = acc, a
    best_wr, best_acc2 = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_flat_gate(train_c, W_ops, E, M, TUNE_DEPTH, best_alpha, wr, False, gen).mean()
        if acc > best_acc2:
            best_acc2, best_wr = acc, wr
    return float(best_alpha), float(best_wr)


def run_one_seed(seed: int, out_dir: Path, unit_idx: int) -> Dict[str, Any]:
    t_seed = time.time()
    g_np = np.random.default_rng(seed)
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 100003 + 17)

    per_nops: Dict[int, Dict[str, Any]] = {}
    q_points: List[Tuple[int, int, float]] = []          # (n_ops, r, q) anchor
    anchor_flat_points: List[Tuple[int, int, float]] = []  # (n_ops, d, flat) anchor d<=4
    tf_check: List[float] = []                            # |q_tf - q_ratio| at anchor r

    for n_ops in N_OPS_SET:
        E = make_bipolar_E(V_FIXED, N_DIM, gen)
        per_op, train_by_d, test_by_d = make_kb_and_chains(
            n_ops, V_FIXED, DENSITY, N_TRAIN_CHAINS, N_TEST_CHAINS, DEPTHS_ALL, g_np)
        W_ops = build_W_ops(per_op, E, N_DIM, n_ops)
        adj = build_adjacency(per_op, n_ops)
        n_trans = min(ROLLOUT_CAP, ROLLOUT_PER_V * V_FIXED)
        transitions = collect_rollout_transitions(adj, n_ops, V_FIXED, n_trans, max(DEPTHS_ALL), g_np)
        M = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, gen)

        alpha, w_reach = _tune_gate(train_by_d[TUNE_DEPTH], W_ops, E, M, gen)

        flat_obs: Dict[int, float] = {}
        flat_shuf: Dict[int, float] = {}
        for d in DEPTHS_ALL:
            flat_obs[d] = float(run_flat_gate(
                test_by_d[d], W_ops, E, M, d, alpha, w_reach, False, gen).mean())
            flat_shuf[d] = float(run_flat_gate(
                test_by_d[d], W_ops, E, M, d, alpha, w_reach, True, gen).mean())

        # teacher-forced per-horizon q(r) on the deepest test chains (covers r=1..max),
        # but only anchor r<=TUNE_DEPTH are used in the product-law X-check
        tf_counts: Dict[int, Tuple[int, int]] = {}
        for d in ANCHOR_DEPTHS:
            part = teacher_forced_per_horizon(test_by_d[d], W_ops, E, M, d, alpha, w_reach)
            for r, (h, t) in part.items():
                h0, t0 = tf_counts.get(r, (0, 0))
                tf_counts[r] = (h0 + h, t0 + t)
        q_tf = {r: (h / max(1, t)) for r, (h, t) in tf_counts.items()}

        q_ratio = reconstruct_q(flat_obs, n_ops)
        for r in ANCHOR_DEPTHS:
            if r in q_ratio:
                q_points.append((n_ops, r, q_ratio[r]))
            if r in q_ratio and r in q_tf:
                tf_check.append(abs(q_tf[r] - q_ratio[r]))
        for d in ANCHOR_DEPTHS:
            anchor_flat_points.append((n_ops, d, flat_obs[d]))

        per_nops[n_ops] = {
            "alpha": alpha, "w_reach": w_reach,
            "flat_obs": flat_obs, "flat_shuf": flat_shuf,
            "q_ratio": q_ratio, "q_tf": q_tf,
            "reach_rank_chance": reach_rank_chance(n_ops),
        }
        _heartbeat(out_dir, unit_idx, EXPECTED_N_UNITS,
                   note="seed=%d n_ops=%d alpha=%.2f wr=%.2f flat_d1=%.3f flat_d8=%.3f" %
                   (seed, n_ops, alpha, w_reach, flat_obs.get(1, -1), flat_obs.get(8, -1)))
        print("[seed %d] n_ops=%d alpha=%.2f w_reach=%.2f flat=%s shuf_d8=%.3f" %
              (seed, n_ops, alpha, w_reach,
               {d: round(flat_obs[d], 3) for d in DEPTHS_ALL}, flat_shuf.get(8, -1)), flush=True)

    # ---- fit models on the anchor (this seed) ----
    mu0, beta = fit_horizon_margin(q_points)
    mu_const = fit_const_margin(q_points)
    C1, _p1 = fit_hick(anchor_flat_points, power=False)
    Cp, pp = fit_hick(anchor_flat_points, power=True)

    # shuffled-anchor margin fit (firing control): reconstruct q from flat_shuf at anchor
    q_points_shuf: List[Tuple[int, int, float]] = []
    for n_ops in N_OPS_SET:
        q_s = reconstruct_q(per_nops[n_ops]["flat_shuf"], n_ops)
        for r in ANCHOR_DEPTHS:
            if r in q_s:
                q_points_shuf.append((n_ops, r, q_s[r]))
    mu0_shuf, beta_shuf = fit_horizon_margin(q_points_shuf)

    # ---- predict held-out d in {6,8} and compute RMSE ----
    pred_surface: Dict[str, Dict[str, float]] = {}
    err_h, err_c, err_h1, err_hp, err_shuf_null = [], [], [], [], []
    for n_ops in N_OPS_SET:
        flat_obs = per_nops[n_ops]["flat_obs"]
        flat4 = flat_obs.get(TUNE_DEPTH, 1e-6)
        for d in HELDOUT_DEPTHS:
            obs = flat_obs[d]
            ph = predict_horizon(n_ops, d, mu0, beta)
            pc = predict_const_geom(n_ops, d, flat4)
            p1 = predict_hick(n_ops, d, C1, 1.0)
            pP = predict_hick(n_ops, d, Cp, pp)
            pn = (1.0 / n_ops) ** d
            key = "op%d_d%d" % (n_ops, d)
            pred_surface[key] = {"obs": obs, "horizon": ph, "const": pc,
                                 "hick1": p1, "hickp": pP, "shuffle_null": pn}
            err_h.append(ph - obs); err_c.append(pc - obs)
            err_h1.append(p1 - obs); err_hp.append(pP - obs); err_shuf_null.append(pn - obs)

    def _rmse(e):
        a = np.asarray(e, dtype=np.float64)
        return float(np.sqrt(np.mean(a * a))) if len(a) else float("nan")

    rmse_horizon = _rmse(err_h)
    rmse_const = _rmse(err_c)
    rmse_hick1 = _rmse(err_h1)
    rmse_hickp = _rmse(err_hp)
    rmse_shuf_null = _rmse(err_shuf_null)

    mu0_real_bar = mu0
    tf_check_mean = float(np.mean(tf_check)) if tf_check else float("nan")

    result = {
        "seed": seed,
        "N": N_DIM, "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_nops": {str(k): v for k, v in per_nops.items()},
        "fit": {"mu0": mu0, "beta": beta, "mu_const": mu_const,
                "hick_C1": C1, "hick_Cp": Cp, "hick_p": pp,
                "mu0_shuf": mu0_shuf, "beta_shuf": beta_shuf},
        "pred_surface": pred_surface,
        "rmse_horizon": rmse_horizon, "rmse_const": rmse_const,
        "rmse_hick1": rmse_hick1, "rmse_hickp": rmse_hickp, "rmse_shuffle_null": rmse_shuf_null,
        "const_gap": rmse_const - rmse_horizon,
        "hick_gap": rmse_hick1 - rmse_horizon,
        "hickp_gap": rmse_hickp - rmse_horizon,
        "mu0_real": mu0_real_bar, "tf_check_mean": tf_check_mean,
        "elapsed_s": round(time.time() - t_seed, 2),
    }
    return result


# ============================================================================
# verdict
# ============================================================================
def _agg(per_seed: Dict[str, Dict[str, Any]], key: str) -> Tuple[float, float]:
    vals = [float(v[key]) for v in per_seed.values() if v.get(key) is not None
            and not (isinstance(v[key], float) and math.isnan(v[key]))]
    if not vals:
        return float("nan"), float("nan")
    m = float(np.mean(vals))
    s = float(np.std(vals))
    return m, s


def build_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    n_done = len(per_seed)
    # cardinality gate
    if n_done < EXPECTED_N_UNITS:
        return {"verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "verdict_msg": "cardinality: %d of %d seeds complete" % (n_done, EXPECTED_N_UNITS),
                "n_done": n_done}

    rmse_h_m, rmse_h_s = _agg(per_seed, "rmse_horizon")
    rmse_c_m, _ = _agg(per_seed, "rmse_const")
    rmse_h1_m, _ = _agg(per_seed, "rmse_hick1")
    rmse_hp_m, _ = _agg(per_seed, "rmse_hickp")
    const_gap_m, _ = _agg(per_seed, "const_gap")
    hick_gap_m, _ = _agg(per_seed, "hick_gap")
    hickp_gap_m, _ = _agg(per_seed, "hickp_gap")
    mu0_real_m, _ = _agg(per_seed, "mu0_real")
    tf_m, _ = _agg(per_seed, "tf_check_mean")

    # mu0_shuf, collapse-fires, shallow-gate-works, anchor-decay from per-seed per_nops
    mu0_shuf_vals, flat_op4_d8, anchor_decay_vals = [], [], []
    shallow_works_all = True
    max_nops = max(N_OPS_SET)
    for v in per_seed.values():
        mu0_shuf_vals.append(float(v["fit"]["mu0_shuf"]))
        pn = v["per_nops"]
        fo = pn[str(max_nops)]["flat_obs"]
        flat_op4_d8.append(float(fo.get("8", fo.get(8, 1.0))))
        anchor_decay_vals.append(float(fo.get(str(TUNE_DEPTH), fo.get(TUNE_DEPTH, 1.0))))
        for nk in N_OPS_SET:
            f1 = pn[str(nk)]["flat_obs"]
            v1 = float(f1.get("1", f1.get(1, 0.0)))
            if v1 <= SHALLOW_LO:            # gate must WORK shallow (no upper cap; saturation OK)
                shallow_works_all = False
    mu0_shuf_m = float(np.mean(mu0_shuf_vals))
    flat_op4_d8_m = float(np.mean(flat_op4_d8))
    anchor_decay_m = float(np.mean(anchor_decay_vals))

    cv_h = (rmse_h_s / rmse_h_m) if rmse_h_m > 1e-9 else 0.0

    # discriminator-fires: deep collapse AND shallow gate works AND anchor carries measurable decay
    collapse_fires = ((flat_op4_d8_m <= COLLAPSE_MAX) and shallow_works_all
                      and (anchor_decay_m <= ANCHOR_DECAY_MAX))
    firing_ok = (mu0_real_m >= MU_REAL_MIN) and (mu0_shuf_m <= MU_SHUF_MAX)
    product_law_ok = (not math.isnan(tf_m)) and (tf_m <= TF_TOL)

    gates = {
        "rmse_horizon_le_HP": bool(rmse_h_m <= HP_RMSE),
        "const_gap_ge_HP": bool(const_gap_m >= HP_CONST_GAP),
        "hick_gap_ge_HP": bool(hick_gap_m >= HP_HICK_GAP),
        "firing_ok": bool(firing_ok),
        "collapse_fires": bool(collapse_fires),
        "product_law_ok": bool(product_law_ok),
        "cv_ok": bool(cv_h <= HP_CV_MAX),
    }
    all_hp = all(gates.values())

    if not collapse_fires:
        verdict = "INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE"
    elif rmse_h_m > HF_RMSE or (rmse_h_m > rmse_h1_m + HF_HICK_MARGIN):
        verdict = "HARD_FAIL"
    elif all_hp:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    msg = ("%s | HELD-OUT rmse: horizon=%.3f const=%.3f hick1=%.3f hickp=%.3f shuf_null=%.3f | "
           "const_gap=%.3f hick_gap=%.3f hickp_gap=%.3f | fit mu0=%.3f mu0_shuf=%.3f | "
           "collapse op%d_d8=%.3f(<=%.2f) shallow_works=%s anchor_decay_d%d=%.3f(<=%.2f) | "
           "firing(mu0>=%.2f=%s,shuf<=%.2f=%s) | "
           "product_law tf_dev=%.3f(<=%.2f) | cv_h=%.3f n_seeds=%d | gates=%s") % (
        verdict, rmse_h_m, rmse_c_m, rmse_h1_m, rmse_hp_m,
        _agg(per_seed, "rmse_shuffle_null")[0],
        const_gap_m, hick_gap_m, hickp_gap_m, mu0_real_m, mu0_shuf_m,
        max_nops, flat_op4_d8_m, COLLAPSE_MAX, shallow_works_all, TUNE_DEPTH, anchor_decay_m,
        ANCHOR_DECAY_MAX,
        MU_REAL_MIN, bool(mu0_real_m >= MU_REAL_MIN), MU_SHUF_MAX, bool(mu0_shuf_m <= MU_SHUF_MAX),
        tf_m, TF_TOL, cv_h, n_done, gates)

    return {
        "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "rmse_horizon": rmse_h_m, "rmse_horizon_std": rmse_h_s,
        "rmse_const": rmse_c_m, "rmse_hick1": rmse_h1_m, "rmse_hickp": rmse_hp_m,
        "const_gap": const_gap_m, "hick_gap": hick_gap_m, "hickp_gap": hickp_gap_m,
        "mu0_real": mu0_real_m, "mu0_shuf": mu0_shuf_m,
        "flat_op_max_d8": flat_op4_d8_m, "shallow_works": shallow_works_all,
        "anchor_decay": anchor_decay_m,
        "collapse_fires": collapse_fires, "firing_ok": firing_ok,
        "product_law_tf_dev": tf_m, "cv_horizon": cv_h,
        "gates": gates, "n_done": n_done,
    }


# ============================================================================
# formula self-test (assert measured == expected BEFORE dispatch)
# ============================================================================
def formula_selftest() -> None:
    print("[selftest] GH64 order-statistic kernel", flush=True)
    # 1. p_gate(mu=0) == 1/n_ops (uniform among n_ops symmetric competitors)
    for n in (2, 3, 4, 6):
        pg = p_gate(n, 0.0)
        assert abs(pg - 1.0 / n) < 1e-6, "p_gate(0,%d)=%.8f != %.8f" % (n, pg, 1.0 / n)
    # 2. monotone increasing in mu; p_gate -> 1 as mu large
    for n in (2, 3, 4):
        seq = [p_gate(n, m) for m in (-2, -1, 0, 1, 2, 4, 8)]
        for a, b in zip(seq, seq[1:]):
            assert b >= a - 1e-9, "p_gate not monotone for n=%d: %s" % (n, seq)
        assert p_gate(n, 12.0) > 0.999, "p_gate(12,%d)=%.6f not ~1" % (n, p_gate(n, 12.0))
    # 3. inversion round-trips
    for n in (2, 3, 4):
        for mu in (0.3, 1.0, 2.0, 3.5):
            q = p_gate(n, mu)
            mu_rt = mu_from_pgate(n, q)
            assert abs(mu_rt - mu) < 5e-3, "invert n=%d mu=%.3f -> %.3f (q=%.5f)" % (n, mu, mu_rt, q)
    # 4. chain-survival product law + shallow->deep recovery on a SYNTHETIC planted margin.
    #    Plant mu(r)=mu0-beta*(r-1); flat(d)=prod_{r<=d} p_gate(n, mu(r)). Reconstruct q from
    #    consecutive flats, refit (mu0,beta), and predict deep -> must match to tight tol.
    n_ops = 3
    mu0_true, beta_true = 2.4, 0.35
    flat_by_d = {}
    prod = 1.0
    for d in range(1, 9):
        prod *= p_gate(n_ops, mu0_true - beta_true * (d - 1))
        flat_by_d[d] = prod
    q_rec = reconstruct_q(flat_by_d, n_ops)  # r=1..4
    # ratio-reconstructed q must equal the planted per-hop survival
    for r in ANCHOR_DEPTHS:
        q_true = p_gate(n_ops, mu0_true - beta_true * (r - 1))
        assert abs(q_rec[r] - q_true) < 1e-4, "product-law q(%d)=%.6f != %.6f" % (r, q_rec[r], q_true)
    qpts = [(n_ops, r, q_rec[r]) for r in ANCHOR_DEPTHS]
    mu0_fit, beta_fit = fit_horizon_margin(qpts)
    assert abs(mu0_fit - mu0_true) < 0.05 and abs(beta_fit - beta_true) < 0.05, \
        "margin refit off: mu0=%.3f beta=%.3f" % (mu0_fit, beta_fit)
    for d in HELDOUT_DEPTHS:
        pred = predict_horizon(n_ops, d, mu0_fit, beta_fit)
        assert abs(pred - flat_by_d[d]) < 5e-3, \
            "held-out synth pred d=%d: %.5f != %.5f" % (d, pred, flat_by_d[d])
    # 5. const-margin OVER-predicts a super-geometric planted collapse (documented-bound sanity)
    flat4 = flat_by_d[TUNE_DEPTH]
    pred_const_d8 = predict_const_geom(n_ops, 8, flat4)
    assert pred_const_d8 > flat_by_d[8] + 0.02, \
        "const should over-predict super-geometric: const=%.4f obs=%.4f" % (pred_const_d8, flat_by_d[8])
    # 6. Hick fit + predict runs and is finite
    aflat = [(n_ops, d, flat_by_d[d]) for d in ANCHOR_DEPTHS]
    C1, p1 = fit_hick(aflat, power=False)
    Cp, pp = fit_hick(aflat, power=True)
    for d in HELDOUT_DEPTHS:
        assert 0.0 <= predict_hick(n_ops, d, C1, 1.0) <= 1.0
        assert 0.0 <= predict_hick(n_ops, d, Cp, pp) <= 1.0
    # 7. shuffled-gate limit: q -> 1/n_ops -> mu -> ~0 (margin destroyed)
    q_chance = [(n, r, 1.0 / n) for n in (2, 3, 4) for r in ANCHOR_DEPTHS]
    mu0_ch, beta_ch = fit_horizon_margin(q_chance)
    assert abs(mu0_ch) < 0.15, "shuffled-limit mu0 should be ~0, got %.4f" % mu0_ch
    print("[selftest] ALL formula self-tests PASS", flush=True)


# ============================================================================
# main
# ============================================================================
def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir)

    print("[main] anchor=%s run_mode=%s N=%d V=%d n_ops=%s seeds=%s device=%s expected_units=%d" %
          (ANCHOR_NAME, RUN_MODE, N_DIM, V_FIXED, N_OPS_SET, SEEDS, DEVICE, EXPECTED_N_UNITS),
          flush=True)

    # ALWAYS run formula self-tests first (cheap, catches kernel regressions)
    formula_selftest()

    if SELF_TEST_MODE:
        # exercise one seed end-to-end at tiny scale to prove all code paths run
        res = run_one_seed(SEEDS[0], out_dir, 0)
        payload = {
            "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS formula+pipeline (seed=%d rmse_horizon=%.3f "
                           "rmse_const=%.3f rmse_hick1=%.3f)" %
                           (SEEDS[0], res["rmse_horizon"], res["rmse_const"], res["rmse_hick1"]),
            "summary": "SELFTEST_PASS", "elapsed_s": round(time.time() - _T0, 2),
            "run_mode": "selftest", "config_version": CONFIG_VERSION,
            "selftest_seed_result": {k: res[k] for k in
                                     ("rmse_horizon", "rmse_const", "rmse_hick1", "fit")},
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        _atomic_write_metrics(out_dir, payload)
        print("[selftest] wrote %s" % (out_dir / "metrics.json"), flush=True)
        return

    # FULL / SMOKE: per-seed resumable
    run_config = {"N": N_DIM, "run_mode": ("smoke" if RUN_MODE == "smoke" else "full"),
                  "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s" %
          (len(done), len(SEEDS), remaining), flush=True)

    fatal_seed_errors: List[str] = []
    for i, seed in enumerate(remaining):
        try:
            res = run_one_seed(seed, out_dir, len(done) + i)
            body = dict(res)
            body["N"] = N_DIM
            body["run_mode"] = ("smoke" if RUN_MODE == "smoke" else "full")
            body["config_version"] = CONFIG_VERSION
            write_partial_key(out_dir, seed, body)
            print("[seed %d] DONE rmse_horizon=%.3f const=%.3f hick1=%.3f (%.1fs)" %
                  (seed, res["rmse_horizon"], res["rmse_const"], res["rmse_hick1"],
                   res["elapsed_s"]), flush=True)
        except Exception as e:  # per-seed failure-class instrumentation (no bare except)
            fc = type(e).__name__
            fatal_seed_errors.append("seed=%d failure_class=%s: %s" % (seed, fc, str(e)[:200]))
            print("[seed %d] FAILED failure_class=%s: %s" % (seed, fc, e), file=sys.stderr,
                  flush=True)
            traceback.print_exc()

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    verdict = build_verdict(per_seed)
    payload = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict["verdict"],
        "verdict_msg": verdict["verdict_msg"],
        "summary": verdict.get("summary", verdict["verdict_msg"]),
        "elapsed_s": round(time.time() - _T0, 1),
        "run_mode": RUN_MODE,
        "N": N_DIM, "V": V_FIXED, "n_ops_set": N_OPS_SET,
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": verdict["n_done"],
        "cardinality_ok": bool(verdict["n_done"] >= EXPECTED_N_UNITS),
        "n_seeds_complete": verdict["n_done"],
        "aggregate": {k: verdict[k] for k in verdict if k not in
                      ("verdict", "verdict_msg", "summary", "gates", "n_done")},
        "gates": verdict.get("gates", {}),
        "fatal_seed_errors": fatal_seed_errors,
        "per_seed": {s: {kk: per_seed[s][kk] for kk in
                         ("rmse_horizon", "rmse_const", "rmse_hick1", "rmse_hickp",
                          "rmse_shuffle_null", "const_gap", "hick_gap", "mu0_real",
                          "tf_check_mean", "pred_surface", "fit", "per_nops")}
                     for s in per_seed},
        "config_version": CONFIG_VERSION,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "device": str(DEVICE),
    }
    _atomic_write_metrics(out_dir, payload)
    print("[main] verdict=%s" % verdict["verdict"], flush=True)
    print("[main] %s" % verdict["verdict_msg"], flush=True)
    print("[main] wrote %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out, e)
        raise
