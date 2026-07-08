"""substrate_acc_evc_adaptive_halting_v1 -- make the FROZEN hop-depth knob ADAPTIVE (ACC/EVC dial).

WHAT THIS IS (self-manager channel #1; notes/research_neuromodulatory_self_manager_controller_2026-07-08.md sec5):
  The certified composed value-gate (exp_pfc_bg_composed_attention_value_gate_v1 / exp_pfc_gate_cfrpe_trained_v2)
  runs a Go/NoGo actor for a FIXED number of hops DD, hand-set a priori and frozen for the whole run. That is
  exactly the "fixed knob picks ONE point on a per-instance-varying tradeoff" failure mode the ACC/EVC channel
  (Shenhav/Botvinick/Cohen expected-value-of-control) is a documented fix for: always-fixed-DD OVER-computes on
  easy (short) items and UNDER-computes on hard (long) items, under an UNKNOWN per-instance difficulty
  distribution. This cell layers a CONTENT-FREE SCALAR controller OVER the unchanged value-gate: a per-item
  LOCAL reflex (parameter-free -- halt once arrival-confidence crosses a threshold) whose single aggregate knob
  (the acceptance threshold theta) is tuned on an aggregate marginal-value/marginal-cost statistic. NO stored
  per-item map (USER: not brain-like), NO new learned weights, NO change to reach_value/cleanup/Hebbian-W.

WHY HALTING HAS SOMETHING TO REALLOCATE (the regime that forces the mechanism):
  The parent cell only ever runs chains whose true length L == DD (homogeneous), so a fixed depth is trivially
  right and there is nothing to reallocate. Here the corpus is HETEROGENEOUS: true chain length L is drawn
  uniform over L_SUPPORT (mean == FROZEN_DD), so NO single fixed depth can be right for all items. The Go/NoGo
  actor has no STAY action -- once it lands on the goal it must keep moving, drifting AWAY. So a fixed-DD policy
  that over-runs a short chain drifts PAST a goal it already reached (reached-then-drifted = wrong), and one that
  under-runs a long chain never arrives. Making the frozen knob adaptive recovers the reached-then-drifted items
  by STOPPING once arrival-confidence is high -- reallocating effort (fewer hops on short items, more on long),
  not merely trimming.

HALT SIGNAL (content-free scalar telemetry; LOCAL reflex, parameter-free per item):
  arrival-confidence a_t = cos(current_state, goal_code)  (goal_sim; already computed inside the actor).
  Reflex: halt (accept current node, take no further hop) once a_t >= theta. Once arrived, EVC marginal value of
  another hop is negative (any move leaves the goal), so halting is the marginal-cost=marginal-benefit crossing.
  theta is the ONE aggregate scalar the controller sets: on TRAIN it sweeps a small theta grid and picks
  theta* = argmax accuracy-per-compute (== value-per-effort, the EVC objective), then FREEZES it for TEST. This
  is aggregate (batch statistic) and scalar -- not a per-item lookup.

ARMS (6; paired -- all share E / W_ops / cfrpe-trained M / goal=E[true target] / test chains per seed; arms
  differ ONLY by the halting policy, NOT by the actor):
  FIXED_DD          run exactly FROZEN_DD hops, never early-halt. THE named baseline (the current frozen value).
  FIXED_DD_CEIL     run exactly D_MAX hops, never early-halt. Shows fixed-HIGH also fails (over-run drift).
  ADAPTIVE_EVC      per-item halt once a_t >= theta* (theta* tuned on TRAIN by acc-per-compute, then frozen). THE DIAL.
  RANDOM_DEPTH      per-item depth drawn uniform over [D_MIN,D_MAX] independent of telemetry. Controls for
                    "does depth VARIANCE alone help" -- isolates whether the arrival SIGNAL is load-bearing.
  SCRAMBLED_HALT    identical to ADAPTIVE but the arrival-confidence a_t is SHUFFLED across items per hop
                    (matched scale, chain-arrival correspondence destroyed). TELEMETRY-SENSITIVITY guard
                    (mandatory): must collapse toward RANDOM_DEPTH; if it does not, the discriminator is
                    analytically pinned, not reading the signal (reported INCONCLUSIVE, not a clean negative).
  ORACLE_HALT       halt at the first hop where current node == true target (ground-truth). PERFECT-halting
                    ceiling + closure denominator + nav rail. (ADAPTIVE approximates this; near-identity is the
                    success signal, hence the (ADAPTIVE,ORACLE_HALT) arms-differ exemption below.)

DISCRIMINATORS (headline; accpc == accuracy / mean_hops_used == accuracy-per-compute):
  adaptive_vs_fixed_rel  = accpc(ADAPTIVE)/accpc(FIXED_DD) - 1        (reallocation win over the frozen value)
  adaptive_vs_random_rel = accpc(ADAPTIVE)/accpc(RANDOM_DEPTH) - 1    (arrival SIGNAL load-bearing, not variance)
  scramble_rel_gap       = 1 - accpc(SCRAMBLED_HALT)/accpc(ADAPTIVE)  (telemetry-sensitivity; scramble collapses)
  realloc_corr           = pearson(hops_used(ADAPTIVE), hops_used(ORACLE_HALT))  (halt tracks true arrival; scramble kills it.
                           NB reach-guided nav arrives along its own policy-path length, NOT the corpus label L, so
                           corr-vs-true_L ~ 0 even when halting is perfect; corr-vs-oracle-arrival is the right signal.)
  hop_spread             = std(hops_used(ADAPTIVE))                   (genuine reallocation, not collapse-to-fixed)
  closure                = (accpc(ADAPTIVE)-accpc(FIXED_DD)) / (accpc(ORACLE_HALT)-accpc(FIXED_DD))

CONTRACT (pre-registered; preregs/2026-07-08_substrate_acc_evc_adaptive_halting_v1.md):
  HARD_PASS  : adaptive_vs_fixed_rel >= 0.15 AND adaptive_vs_random_rel >= 0.10 AND scramble_rel_gap >= 0.15
               AND realloc_corr >= 0.30 AND (realloc_corr - scramble_corr) >= 0.20 AND hop_spread >= 0.5
               AND acc(ADAPTIVE) >= acc(FIXED_DD) - 0.02 (quality matched-or-better) AND reach_rank > 0.30
               AND guards (nav rail, baseline in band, halting pressure, oracle-reproduce) AND arms differ.
  MIDDLE_BAND: adaptive_vs_fixed_rel in [0.05,0.15) OR (adaptive beats fixed >=0.15 but adaptive_vs_random_rel
               < 0.10) OR scramble_rel_gap in [0.05,0.15).
  HARD_FAIL_ADDS_NOTHING          : |adaptive_vs_fixed_rel| < 0.05 (dial adds nothing over the frozen value).
  HARD_FAIL_SIGNAL_NOT_LOADBEARING: accpc(ADAPTIVE) <= accpc(RANDOM_DEPTH) (variance alone matched it).
  HARD_FAIL_COLLAPSED_TO_FIXED    : hop_spread < 0.5 (adaptive matched fixed only by collapsing to it -- no reallocation).
  INCONCLUSIVE_TAUTOLOGICAL_METRIC   : scramble_rel_gap < 0.05 (scramble did NOT collapse -> not telemetry-sensitive).
  INCONCLUSIVE_NAV_BROKEN            : acc(ORACLE_HALT) < NAV_RAIL_MIN (routing itself broken; halting untestable).
  INCONCLUSIVE_NO_HALTING_PRESSURE   : accpc(ORACLE_HALT) <= accpc(FIXED_DD)*1.10 (perfect halting cannot beat the
                                       frozen value -> corpus does not force halting; regime miss, not a verdict).
  INCONCLUSIVE_BASELINE_OOB          : FIXED_DD acc outside (0.05,0.95) (baseline saturated/floored; META_RULE_AG).
  INCONCLUSIVE_ORACLE_REPRO_MISMATCH : FIXED_DD acc on the L==FROZEN_DD subset outside the cfrpe reproduce band
                                       (Gate D: the value-gate did not reproduce at the test regime).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 of per-arm (correct,hops_used) vectors). The
#   load-bearing contrasts ADAPTIVE vs {FIXED_DD, FIXED_DD_CEIL, RANDOM_DEPTH, SCRAMBLED_HALT} MUST differ.
#   arms_differ_exempted: [(ADAPTIVE_EVC, ORACLE_HALT)] -- clean-state arrival detection approximates the
#   ground-truth arrival oracle; near-identical is the SUCCESS signal, not an implementation bug (distinct code
#   paths: cos-threshold vs node-equality). Both still hashed + logged.
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
# - except SystemExit: raise BEFORE except Exception (no BaseException in main / __main__).
# - crlb_n/a: accuracy-per-compute gap discriminator; no single closed-form noise floor. Reachability by
#   feasibility -- cfrpe v2 MEASURED gonogo=0.653 at V1200_d4 and reach_rank>1/n_ops at this regime, so the
#   value-gate routes through the goal often enough for arrival-halting to have signal (see prereg predicted band).
# - baseline_in_band (META_RULE_AG): the CONTROL/baseline is FIXED_DD (must be 0.05<acc<0.95 under heterogeneous
#   L); ORACLE_HALT must rail (nav >= NAV_RAIL_MIN); FIXED_DD@(L==FROZEN_DD) must land in the cfrpe reproduce band.
# - discriminator survives scale: smoke holds N/V == FULL N/V (6.83) so per-hop cleanup difficulty matches, AND
#   smoke trains SR to near-FULL informativeness (discriminator PREVIEW, option C) rather than under-trained SR.
# - HARD_PASS strictly above floor (META_RULE_L): gates are strict (>=0.15 / >=0.10 / >=0.15 / >=0.30 / >=0.5).
# - HP_SCOPE: HP relative-gates apply to ADAPTIVE_EVC vs {FIXED_DD, RANDOM_DEPTH, SCRAMBLED_HALT}. ORACLE_HALT
#   carries ONLY the nav rail + the closure/pressure denominator. FIXED_DD carries the baseline-in-band + Gate-D
#   reproduce. FIXED_DD_CEIL carries no gate (diagnostic: fixed-high also fails).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS); verdict counts completed (seed x arm) units.
# - per-unit failure-class instrumentation (no bare except; per-seed fatal-flag -> demote HP).
# - calibration_check: adaptive_with_discriminator_gate -- theta* is tuned on TRAIN by acc-per-compute (principled,
#   the EVC objective), and the discriminator STILL fires (scramble collapses + random beaten); theta*, the
#   theta->{acc,mean_hops} curve, and both correlations are logged. Honest adaptive calibration, not p-hacking.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@:
#     cfrpe V1200_d4 gonogo=0.653  MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4.gonogo
#     non-goal cos ~ N(0, 1/N): std ~ 1/sqrt(N) = 0.011 at N=8192 THEORETICAL@ random-bipolar inner product
#     ACC/EVC marginal-cost=marginal-benefit halting CITED@Shenhav/Botvinick/Cohen 2013 (research note sec1/5)
#     adaptive_vs_fixed_rel HARD_PASS P_deflated=0.40 HYPOTHESIZED@notes/research_neuromodulatory_self_manager_controller_2026-07-08.md sec5
#     PRIOR pfc_controller_depth_adaptive_argmax_v3 = adaptive TEMPERATURE at FIXED depth (softmax sharpness),
#       NOT adaptive halting (hop budget); distinct mechanism CITED@data/exp_pfc_controller_depth_adaptive_argmax_v3/metrics.json

Compute architecture: (a) batched-GPU. SR-TD training, operator application, cleanup, reach, and goal_sim are
  batched matmuls on cuda-if-available; the per-item halt mask is a cheap elementwise op inside the batched hop
  loop (within-chain hops are a genuine sequential dependency). SR trained ONCE per seed (single V). FULL requires
  cuda (overnight_queue). Storage: sharded (each operator its own W; M is a learned value operator). No composition store.
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line + per-seed/arm
  heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_substrate_acc_evc_adaptive_halting_v1.md
Reuses (imported unchanged; cfrpe main is __name__-guarded => import-safe):
  experiments/exp_pfc_gate_cfrpe_trained_v2.py  (Go/NoGo actor primitives + cfrpe RPE SR, unchanged)
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
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

# cfrpe is IMPORT-SAFE (main is __name__-guarded). Reuse its primitives + Go/NoGo actor unchanged.
import experiments.exp_pfc_gate_cfrpe_trained_v2 as cf

ANCHOR_NAME = "substrate_acc_evc_adaptive_halting_v1"

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

DEVICE = cf.DEVICE
DTYPE = cf.DTYPE

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
HP_ADAPT_VS_FIXED_REL = 0.15     # accpc(ADAPTIVE)/accpc(FIXED_DD)-1 >= this
HP_ADAPT_VS_RANDOM_REL = 0.10    # accpc(ADAPTIVE)/accpc(RANDOM)-1 >= this (signal, not variance)
HP_SCRAMBLE_REL_GAP = 0.15       # 1 - accpc(SCRAMBLED)/accpc(ADAPTIVE) >= this (telemetry-sensitivity)
HP_REALLOC_CORR_MIN = 0.30       # pearson(hops_adaptive, true_L) >= this
HP_REALLOC_CORR_MARGIN = 0.20    # corr_adaptive - corr_scrambled >= this (scramble kills correlation)
HP_HOP_SPREAD_MIN = 0.5          # std(hops_adaptive) >= this (reallocation, not collapse-to-fixed)
HP_QUALITY_TOL = 0.02            # acc(ADAPTIVE) >= acc(FIXED_DD) - this (matched-or-better quality)
HP_REACH_RANK_MIN = 0.30         # reach informative > chance (1/n_ops)
TAUT_SCRAMBLE_FLOOR = 0.05       # scramble_rel_gap < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC
MB_ADAPT_VS_FIXED_LO = 0.05      # adaptive_vs_fixed_rel in [0.05,0.15) => MIDDLE_BAND
HF_ADDS_NOTHING = 0.05           # |adaptive_vs_fixed_rel| < this => HARD_FAIL_ADDS_NOTHING
NAV_RAIL_MIN = 0.55              # ORACLE_HALT acc must reach this (routing works => halting testable)
PRESSURE_MARGIN = 1.10           # accpc(ORACLE_HALT) > accpc(FIXED_DD)*this (halting headroom exists)
BASELINE_LO, BASELINE_HI = 0.05, 0.95
# cfrpe reproduce band (Gate D): FIXED_DD acc restricted to L==FROZEN_DD subset (== gonogo@dDD, oracle goal).
# cfrpe v2 V1200_d4 gonogo=0.653 MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4.gonogo
# Widened +/-0.20 (heterogeneous corpus + per-arm subset variance) => [0.35, 0.90].
REPRO_LO, REPRO_HI = 0.35, 0.90

# cfrpe knobs (reused; match cfrpe v2 constants)
N_OPS = 4
DENSITY = 0.21
GAMMA = cf.GAMMA
SR_LR = cf.SR_LR

# actor tuning grids (tuned on TRAIN w/ ORACLE goal at FROZEN_DD, then FROZEN across arms -- actor unchanged)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]

# EVC controller: the ONE scalar knob (arrival-confidence acceptance threshold). Tuned on TRAIN by acc-per-compute.
THETA_GRID = [0.15, 0.25, 0.35, 0.45, 0.55]

ARMS = ["FIXED_DD", "FIXED_DD_CEIL", "ADAPTIVE_EVC", "RANDOM_DEPTH", "SCRAMBLED_HALT", "ORACLE_HALT"]

# --------------------------- config (selftest / smoke / full) --------------------
# Heterogeneous true chain length L ~ uniform(L_SUPPORT); mean(L_SUPPORT) == FROZEN_DD so the frozen value is the
# mean-optimal fixed choice (strongest possible baseline). D_MAX == max(L_SUPPORT); D_MIN == min(L_SUPPORT).
FROZEN_DD = 4
MIN_HOPS = 1                     # must take >= 1 move before any early halt
if SELF_TEST_MODE:
    N_DIM = 1024
    V_NODES = 40
    SEEDS = [7]
    L_SUPPORT = [2, 4, 6]
    N_CHAINS_PER_L_TRAIN = 30
    N_CHAINS_PER_L_TEST = 30
    SR_STEPS = 900
    SR_BATCH = 48
    ROLLOUT_PER_V = 40
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_NODES = 300                # N/V = 6.83 == FULL
    SEEDS = [7, 17]
    L_SUPPORT = [2, 3, 4, 5, 6]
    N_CHAINS_PER_L_TRAIN = 24    # train pool 120
    N_CHAINS_PER_L_TEST = 24     # test pool 120
    SR_STEPS = 1500              # discriminator PREVIEW: SR near-FULL informative (reach_rank ~ FULL)
    SR_BATCH = 96
    ROLLOUT_PER_V = 30
else:  # full
    N_DIM = 8192
    V_NODES = 1200               # N/V = 6.83 (cfrpe v2 FAIR moderate regime; MEASURED gonogo=0.653)
    SEEDS = [7, 17, 23, 31, 41]
    L_SUPPORT = [2, 3, 4, 5, 6]
    N_CHAINS_PER_L_TRAIN = 60    # train pool 300
    N_CHAINS_PER_L_TEST = 48     # test pool 240
    SR_STEPS = 8000
    SR_BATCH = 256
    ROLLOUT_PER_V = 50

D_MAX = max(L_SUPPORT)
D_MIN = min(L_SUPPORT)
ROLLOUT_CAP = 9000 if RUN_MODE == "smoke" else (2000 if SELF_TEST_MODE else 200000)
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)
assert FROZEN_DD in L_SUPPORT, "FROZEN_DD must be a valid length in L_SUPPORT"
assert abs(float(np.mean(L_SUPPORT)) - FROZEN_DD) < 1e-6, "L_SUPPORT must be mean-centered on FROZEN_DD"


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,n_ops=%d,frozen_dd=%d,L_support=%s,d_min=%d,d_max=%d,seeds=%s,density=%.3f,"
    "sr_steps=%d,sr_batch=%d,rollout_per_V=%d,gamma=%.2f,lr=%.2f,theta_grid=%s,min_hops=%d,"
    "n_train_per_L=%d,n_test_per_L=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_af>=%.2f,HP_ar>=%.2f,HP_scr>=%.2f,HP_corr>=%.2f,HP_spread>=%.2f,nav_rail>=%.2f"
) % (
    ANCHOR_NAME, N_DIM, V_NODES, N_OPS, FROZEN_DD, L_SUPPORT, D_MIN, D_MAX, SEEDS, DENSITY,
    SR_STEPS, SR_BATCH, ROLLOUT_PER_V, GAMMA, SR_LR, THETA_GRID, MIN_HOPS,
    N_CHAINS_PER_L_TRAIN, N_CHAINS_PER_L_TEST, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_ADAPT_VS_FIXED_REL, HP_ADAPT_VS_RANDOM_REL, HP_SCRAMBLE_REL_GAP, HP_REALLOC_CORR_MIN,
    HP_HOP_SPREAD_MIN, NAV_RAIL_MIN,
)

_T0 = time.time()


# ============================================================================
# defensive-error-checking helpers (start marker / crash diag / heartbeat)
# ============================================================================
def _write_start_marker(out_dir: Path) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(), "device": str(DEVICE)}
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
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": round(time.time() - _T0, 1), "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
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
# heterogeneous-length corpus (pool chains over L_SUPPORT; tag each with its true L)
# ============================================================================
def make_hetero_chains(seed: int, g_np: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  List[Tuple[int, List[int], int]], np.ndarray,
                                  List[Tuple[int, List[int], int]], np.ndarray]:
    """Returns (per_op, train_chains, train_L, test_chains, test_L). Chains from make_kb_and_chains pooled over
    all depths in L_SUPPORT so true length L is heterogeneous; the operator graph (per_op) is shared."""
    per_op, train_by_d, test_by_d = cf.make_kb_and_chains(
        N_OPS, V_NODES, DENSITY, N_CHAINS_PER_L_TRAIN, N_CHAINS_PER_L_TEST, L_SUPPORT, g_np)
    train_chains: List[Tuple[int, List[int], int]] = []
    train_L: List[int] = []
    test_chains: List[Tuple[int, List[int], int]] = []
    test_L: List[int] = []
    for L in L_SUPPORT:
        for c in train_by_d[L]:
            train_chains.append(c); train_L.append(L)
        for c in test_by_d[L]:
            test_chains.append(c); test_L.append(L)
    return (per_op, train_chains, np.asarray(train_L, dtype=np.int64),
            test_chains, np.asarray(test_L, dtype=np.int64))


# ============================================================================
# Go/NoGo hop kernel + per-item halting nav core (actor UNCHANGED; only the halt policy varies)
# ============================================================================
def _start_target(chains) -> Tuple[torch.Tensor, torch.Tensor]:
    """(starts, targets) tensors WITHOUT stacking op_seqs -- cf._chain_tensors stacks op_seqs and so requires
    equal chain lengths; our pooled corpus is heterogeneous-length, so we extract start/target only."""
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    return starts, targets


def _go_hop(state: torch.Tensor, goal_E: torch.Tensor, W_ops: List[torch.Tensor], E: torch.Tensor,
            M: torch.Tensor, alpha: float, w_reach: float
            ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """One batched Go/NoGo scoring step. Returns (chosen_next_idx[n], chosen_next_gsim[n], nothing-else-needed).
    Scoring is cfrpe's gonogo formula UNCHANGED: sc = (1-alpha)*manifold + alpha*goal_sim + w_reach*reach."""
    n = state.shape[0]
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    scores = torch.empty((n, n_ops), dtype=DTYPE, device=DEVICE)
    cand_idx = torch.empty((n, n_ops), dtype=torch.long, device=DEVICE)
    gsim = torch.empty((n, n_ops), dtype=DTYPE, device=DEVICE)
    gn = cf._norm_rows(goal_E)
    for op in range(n_ops):
        out = state @ W_ops[op]
        idx, cleaned, manifold = cf.cleanup_batched(out, E)
        cand_idx[:, op] = idx
        out_n = cf._norm_rows(out)
        goal_sim = (out_n * gn).sum(dim=1)
        reach = cf.reach_value(cleaned, goal_E, M)
        scores[:, op] = w_manifold * manifold + alpha * goal_sim + w_reach * reach
        gsim[:, op] = (cf._norm_rows(E[idx]) * gn).sum(dim=1)   # cos(clean next node, goal) -- arrival confidence
    row = torch.arange(n, device=DEVICE)
    chosen = scores.argmax(dim=1)
    return cand_idx[row, chosen], gsim[row, chosen], row


def _nav_core(chains, W_ops: List[torch.Tensor], E: torch.Tensor, M: torch.Tensor,
              goal_E: torch.Tensor, alpha: float, w_reach: float, d_max: int, min_hops: int,
              decider: Callable[[int, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor], torch.Tensor]
              ) -> Tuple[np.ndarray, np.ndarray]:
    """Batched Go/NoGo navigation up to d_max hops with a per-item HALT decider.
    decider(hop, hops_used, cur_gsim, cur_node, targets, active) -> bool halt-mask[n] (halt == accept current
    node, take NO further hop). min_hops moves are forced before any early halt. Returns (correct[n], hops_used[n])."""
    starts, targets = _start_target(chains)
    n = starts.shape[0]
    state = E[starts].clone()
    cur_node = starts.clone()
    final_idx = starts.clone()
    hops_used = torch.zeros(n, dtype=torch.long, device=DEVICE)
    active = torch.ones(n, dtype=torch.bool, device=DEVICE)
    gn = cf._norm_rows(goal_E)
    for hop in range(d_max):
        cur_gsim = (cf._norm_rows(state) * gn).sum(dim=1)
        halt = decider(hop, hops_used, cur_gsim, cur_node, targets, active)
        if hop < min_hops:
            halt = torch.zeros(n, dtype=torch.bool, device=DEVICE)
        take = active & (~halt)
        nxt_idx, _, _ = _go_hop(state, goal_E, W_ops, E, M, alpha, w_reach)
        # apply the chosen move only where we continue
        state = torch.where(take.unsqueeze(1), E[nxt_idx], state)
        cur_node = torch.where(take, nxt_idx, cur_node)
        final_idx = torch.where(take, nxt_idx, final_idx)
        hops_used = hops_used + take.long()
        active = active & (~(active & halt))
        if not bool(active.any()):
            break
    correct = (final_idx == targets).detach().cpu().numpy().astype(bool)
    return correct, hops_used.detach().cpu().numpy()


# --- decider factories (the ONLY thing that differs across arms) ---
def _decider_never():
    def d(hop, hops_used, cur_gsim, cur_node, targets, active):
        return torch.zeros_like(active)
    return d


def _decider_adaptive(theta: float):
    def d(hop, hops_used, cur_gsim, cur_node, targets, active):
        return cur_gsim >= theta                       # arrived: accept, stop
    return d


def _decider_scrambled(theta: float, gen: torch.Generator):
    def d(hop, hops_used, cur_gsim, cur_node, targets, active):
        n = cur_gsim.shape[0]
        perm = torch.randperm(n, generator=gen, device=DEVICE)
        return cur_gsim[perm] >= theta                 # arrival signal shuffled across items (matched scale)
    return d


def _decider_target_depth(td: torch.Tensor):
    def d(hop, hops_used, cur_gsim, cur_node, targets, active):
        return hops_used >= td                         # halt once the preset per-item depth is reached
    return d


def _decider_oracle():
    def d(hop, hops_used, cur_gsim, cur_node, targets, active):
        return cur_node == targets                     # perfect arrival (ground-truth node identity)
    return d


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    if x.size < 2 or np.std(x) < 1e-9 or np.std(y) < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _accpc(correct: np.ndarray, hops: np.ndarray) -> float:
    mh = float(np.mean(hops))
    return float(np.mean(correct)) / mh if mh > 1e-9 else 0.0


# ============================================================================
# per-seed evaluation
# ============================================================================
def _eval_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g_np = np.random.default_rng(seed)
    tgen = torch.Generator(device=DEVICE); tgen.manual_seed(int(seed) * 100003 + int(V_NODES))
    E = cf.make_bipolar_E(V_NODES, N_DIM, tgen)

    per_op, train_c, train_L, test_c, test_L = make_hetero_chains(seed, g_np)
    W_ops = [cf.hebbian_W(per_op[i], E, N_DIM) for i in range(N_OPS)]
    adj = cf.build_adjacency(per_op, N_OPS)
    max_len = D_MAX + 2
    transitions = cf.collect_rollout_transitions(adj, N_OPS, V_NODES, rollout_count(V_NODES), max_len, g_np)
    sr_gen = torch.Generator(device=DEVICE); sr_gen.manual_seed(int(seed) * 7919 + int(V_NODES))
    M, sr_diag = cf.train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
    print("[seed=%d] SR trained: err %s->%s M_norm=%.3f n_trans=%d"
          % (seed, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
             sr_diag["n_transitions"]), flush=True)

    _, tr_targets = _start_target(train_c)
    _, te_targets = _start_target(test_c)
    goal_tr = E[tr_targets]
    goal_te = E[te_targets]

    # ---- tune the actor (alpha, w_reach) on TRAIN with the ORACLE goal at FROZEN_DD, then FREEZE ----
    best_alpha, best_add = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        c, h = _nav_core(train_c, W_ops, E, M, goal_tr, a, 0.0, FROZEN_DD, MIN_HOPS, _decider_never())
        if float(np.mean(c)) > best_add:
            best_add, best_alpha = float(np.mean(c)), a
    best_wr, best_go = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        c, h = _nav_core(train_c, W_ops, E, M, goal_tr, best_alpha, wr, FROZEN_DD, MIN_HOPS, _decider_never())
        if float(np.mean(c)) > best_go:
            best_go, best_wr = float(np.mean(c)), wr

    # ---- EVC controller: tune theta* on TRAIN by acc-per-compute (aggregate scalar), then FREEZE ----
    theta_curve = []
    best_theta, best_accpc_tr = THETA_GRID[0], -1.0
    for th in THETA_GRID:
        c, h = _nav_core(train_c, W_ops, E, M, goal_tr, best_alpha, best_wr, D_MAX, MIN_HOPS,
                         _decider_adaptive(th))
        apc = _accpc(c, h)
        theta_curve.append({"theta": th, "acc": float(np.mean(c)), "mean_hops": float(np.mean(h)), "accpc": apc})
        if apc > best_accpc_tr:
            best_accpc_tr, best_theta = apc, th

    # ---- mechanism-fires probe (reach informativeness on TRUE trajectory; homogeneous L==FROZEN_DD subset,
    #      since reach_rank_acc walks a fixed-length op_seq) ----
    test_atDD = [c for c, L in zip(test_c, test_L) if int(L) == FROZEN_DD]
    reach_rank = cf.reach_rank_acc(test_atDD, W_ops, E, M, FROZEN_DD) if test_atDD else 0.0

    # ---- random-depth + scramble generators (seeded, reproducible) ----
    rd_gen = torch.Generator(device=DEVICE); rd_gen.manual_seed(int(seed) * 51001 + 3)
    td = torch.randint(D_MIN, D_MAX + 1, (len(test_c),), generator=rd_gen, device=DEVICE)
    scr_gen = torch.Generator(device=DEVICE); scr_gen.manual_seed(int(seed) * 51001 + 7)

    # ---- evaluate all six arms on TEST (paired; frozen alpha/w_reach/theta) ----
    runs: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    runs["FIXED_DD"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, FROZEN_DD, MIN_HOPS, _decider_never())
    runs["FIXED_DD_CEIL"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, D_MAX, MIN_HOPS, _decider_never())
    runs["ADAPTIVE_EVC"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, D_MAX, MIN_HOPS, _decider_adaptive(best_theta))
    runs["RANDOM_DEPTH"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, D_MAX, MIN_HOPS, _decider_target_depth(td))
    runs["SCRAMBLED_HALT"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, D_MAX, MIN_HOPS, _decider_scrambled(best_theta, scr_gen))
    runs["ORACLE_HALT"] = _nav_core(test_c, W_ops, E, M, goal_te, best_alpha, best_wr, D_MAX, MIN_HOPS, _decider_oracle())

    arms: Dict[str, Any] = {}
    trace_hashes: Dict[str, str] = {}
    for name, (c, h) in runs.items():
        arms[name] = {"acc": float(np.mean(c)), "mean_hops": float(np.mean(h)), "accpc": _accpc(c, h)}
        payload = c.astype(np.int8).tobytes() + h.astype(np.int64).tobytes()
        trace_hashes[name] = hashlib.sha256(payload).hexdigest()[:16]

    # per-L accuracy breakdown (Gate D reproduce uses FIXED_DD on the L==FROZEN_DD subset)
    acc_by_L: Dict[str, Dict[str, float]] = {}
    for name, (c, h) in runs.items():
        acc_by_L[name] = {}
        for L in L_SUPPORT:
            mask = (test_L == L)
            acc_by_L[name][str(L)] = float(np.mean(c[mask])) if bool(mask.any()) else 0.0
    repro_fixed_atDD = acc_by_L["FIXED_DD"][str(FROZEN_DD)]

    # reallocation correlations + hop spread. NOTE: reach-guided navigation reaches the goal along its OWN
    # policy-path length, not the corpus label L, so corr(hops, true_L) ~ 0 even when halting is perfect. The
    # signal-specificity check is instead corr(adaptive halt-hops, ORACLE arrival-hops): adaptive should track
    # true arrival (~1.0), and SCRAMBLED should NOT (~0) -- scramble erasing this correlation is the guard.
    oracle_hops = runs["ORACLE_HALT"][1]
    corr_adaptive = _pearson(runs["ADAPTIVE_EVC"][1], oracle_hops)
    corr_scrambled = _pearson(runs["SCRAMBLED_HALT"][1], oracle_hops)
    hop_spread_adaptive = float(np.std(runs["ADAPTIVE_EVC"][1]))

    rec = {
        "seed": int(seed), "N": N_DIM, "V": V_NODES, "run_mode": RUN_MODE, "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION, "arms": arms, "acc_by_L": acc_by_L, "trace_hashes": trace_hashes,
        "best_alpha": float(best_alpha), "best_w_reach": float(best_wr), "theta_star": float(best_theta),
        "theta_curve": theta_curve, "reach_rank_test": float(reach_rank),
        "repro_fixed_atDD": float(repro_fixed_atDD),
        "corr_adaptive": float(corr_adaptive), "corr_scrambled": float(corr_scrambled),
        "hop_spread_adaptive": float(hop_spread_adaptive), "sr_diag": sr_diag,
        "n_test": int(len(test_c)),
    }
    print("[seed=%d] FIXED=%.3f(h%.2f) CEIL=%.3f(h%.2f) ADAPT=%.3f(h%.2f) RAND=%.3f(h%.2f) SCR=%.3f(h%.2f) ORC=%.3f(h%.2f)"
          " | theta*=%.2f accpc[F=%.4f A=%.4f R=%.4f S=%.4f O=%.4f] corr[A=%.3f S=%.3f] spread=%.2f reach_rank=%.3f repro@DD=%.3f"
          % (seed, arms["FIXED_DD"]["acc"], arms["FIXED_DD"]["mean_hops"],
             arms["FIXED_DD_CEIL"]["acc"], arms["FIXED_DD_CEIL"]["mean_hops"],
             arms["ADAPTIVE_EVC"]["acc"], arms["ADAPTIVE_EVC"]["mean_hops"],
             arms["RANDOM_DEPTH"]["acc"], arms["RANDOM_DEPTH"]["mean_hops"],
             arms["SCRAMBLED_HALT"]["acc"], arms["SCRAMBLED_HALT"]["mean_hops"],
             arms["ORACLE_HALT"]["acc"], arms["ORACLE_HALT"]["mean_hops"],
             best_theta, arms["FIXED_DD"]["accpc"], arms["ADAPTIVE_EVC"]["accpc"], arms["RANDOM_DEPTH"]["accpc"],
             arms["SCRAMBLED_HALT"]["accpc"], arms["ORACLE_HALT"]["accpc"],
             corr_adaptive, corr_scrambled, hop_spread_adaptive, reach_rank, repro_fixed_atDD), flush=True)
    return rec


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    return _eval_seed(seed, out_dir)


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)
    n_seeds = len(keys)

    def _arm_mean(arm, field):
        return float(np.mean([per_seed[s]["arms"][arm][field] for s in keys]))

    def _scalar_mean(field):
        return float(np.mean([per_seed[s][field] for s in keys]))

    arm_means = {arm: {f: _arm_mean(arm, f) for f in ("acc", "mean_hops", "accpc")} for arm in ARMS}
    completed_units = sum(len([a for a in ARMS if a in per_seed[s]["arms"]]) for s in keys)

    fixed_accpc = arm_means["FIXED_DD"]["accpc"]
    adapt_accpc = arm_means["ADAPTIVE_EVC"]["accpc"]
    rand_accpc = arm_means["RANDOM_DEPTH"]["accpc"]
    scr_accpc = arm_means["SCRAMBLED_HALT"]["accpc"]
    oracle_accpc = arm_means["ORACLE_HALT"]["accpc"]

    adaptive_vs_fixed_rel = (adapt_accpc / fixed_accpc - 1.0) if fixed_accpc > 1e-9 else 0.0
    adaptive_vs_random_rel = (adapt_accpc / rand_accpc - 1.0) if rand_accpc > 1e-9 else 0.0
    scramble_rel_gap = (1.0 - scr_accpc / adapt_accpc) if adapt_accpc > 1e-9 else 0.0
    closure = ((adapt_accpc - fixed_accpc) / (oracle_accpc - fixed_accpc)) if (oracle_accpc - fixed_accpc) > 1e-9 else 0.0

    corr_adaptive = _scalar_mean("corr_adaptive")
    corr_scrambled = _scalar_mean("corr_scrambled")
    hop_spread = _scalar_mean("hop_spread_adaptive")
    reach_rank = _scalar_mean("reach_rank_test")
    repro_fixed_atDD = _scalar_mean("repro_fixed_atDD")

    fixed_acc = arm_means["FIXED_DD"]["acc"]
    adapt_acc = arm_means["ADAPTIVE_EVC"]["acc"]
    oracle_acc = arm_means["ORACLE_HALT"]["acc"]

    # arms-differ (META_RULE_AF): load-bearing contrasts must differ; (ADAPTIVE,ORACLE) pair exempted.
    LOADBEARING = ["FIXED_DD", "FIXED_DD_CEIL", "ADAPTIVE_EVC", "RANDOM_DEPTH", "SCRAMBLED_HALT"]
    af_collision = False
    for s in keys:
        th = per_seed[s]["trace_hashes"]
        hs = [th[a] for a in LOADBEARING]
        if len(set(hs)) < len(hs):
            af_collision = True

    nav_rail_ok = bool(oracle_acc >= NAV_RAIL_MIN)
    baseline_in_band = bool(BASELINE_LO < fixed_acc < BASELINE_HI)
    pressure_ok = bool(oracle_accpc > fixed_accpc * PRESSURE_MARGIN)
    repro_ok = bool(REPRO_LO <= repro_fixed_atDD <= REPRO_HI)
    reach_fires_ok = bool(reach_rank > HP_REACH_RANK_MIN)
    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    def _hp_ok():
        return (adaptive_vs_fixed_rel >= HP_ADAPT_VS_FIXED_REL
                and adaptive_vs_random_rel >= HP_ADAPT_VS_RANDOM_REL
                and scramble_rel_gap >= HP_SCRAMBLE_REL_GAP
                and corr_adaptive >= HP_REALLOC_CORR_MIN
                and (corr_adaptive - corr_scrambled) >= HP_REALLOC_CORR_MARGIN
                and hop_spread >= HP_HOP_SPREAD_MIN
                and adapt_acc >= fixed_acc - HP_QUALITY_TOL
                and reach_fires_ok and nav_rail_ok and baseline_in_band and pressure_ok
                and repro_ok and not af_collision)

    # ---- verdict ladder (guards -> integrity -> HF -> HP -> MB) ----
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not nav_rail_ok:
        verdict = "INCONCLUSIVE_NAV_BROKEN"
    elif not baseline_in_band:
        verdict = "INCONCLUSIVE_BASELINE_OOB"
    elif not repro_ok:
        verdict = "INCONCLUSIVE_ORACLE_REPRO_MISMATCH"
    elif not pressure_ok:
        verdict = "INCONCLUSIVE_NO_HALTING_PRESSURE"
    elif hop_spread < HP_HOP_SPREAD_MIN:
        verdict = "HARD_FAIL_COLLAPSED_TO_FIXED"
    elif scramble_rel_gap < TAUT_SCRAMBLE_FLOOR:
        verdict = "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
    elif adapt_accpc <= rand_accpc:
        verdict = "HARD_FAIL_SIGNAL_NOT_LOADBEARING"
    elif abs(adaptive_vs_fixed_rel) < HF_ADDS_NOTHING:
        verdict = "HARD_FAIL_ADDS_NOTHING"
    elif _hp_ok():
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_HALTING"

    verdict_msg = (
        "%s | accpc[FIXED=%.4f ADAPT=%.4f RAND=%.4f SCR=%.4f ORC=%.4f] | "
        "adapt_vs_fixed=%.3f adapt_vs_random=%.3f scramble_gap=%.3f closure=%.3f | "
        "acc[FIXED=%.3f ADAPT=%.3f ORC=%.3f] hops[FIXED=%.2f ADAPT=%.2f] | "
        "corr[A=%.3f S=%.3f] spread=%.2f reach_rank=%.3f repro@DD=%.3f | "
        "nav_rail=%s baseline_band=%s pressure=%s repro=%s af_collision=%s n_seeds=%d"
    ) % (
        verdict, fixed_accpc, adapt_accpc, rand_accpc, scr_accpc, oracle_accpc,
        adaptive_vs_fixed_rel, adaptive_vs_random_rel, scramble_rel_gap, closure,
        fixed_acc, adapt_acc, oracle_acc, arm_means["FIXED_DD"]["mean_hops"], arm_means["ADAPTIVE_EVC"]["mean_hops"],
        corr_adaptive, corr_scrambled, hop_spread, reach_rank, repro_fixed_atDD,
        nav_rail_ok, baseline_in_band, pressure_ok, repro_ok, af_collision, n_seeds,
    )
    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "arm_means": arm_means,
        "adaptive_vs_fixed_rel": float(adaptive_vs_fixed_rel),
        "adaptive_vs_random_rel": float(adaptive_vs_random_rel),
        "scramble_rel_gap": float(scramble_rel_gap), "closure": float(closure),
        "corr_adaptive": float(corr_adaptive), "corr_scrambled": float(corr_scrambled),
        "hop_spread": float(hop_spread), "reach_rank": float(reach_rank),
        "repro_fixed_atDD": float(repro_fixed_atDD),
        "nav_rail_ok": nav_rail_ok, "baseline_in_band": baseline_in_band, "pressure_ok": pressure_ok,
        "repro_ok": repro_ok, "reach_fires_ok": reach_fires_ok, "af_collision": bool(af_collision),
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "n_seeds_complete": n_seeds,
    }


# ============================================================================
# self-test (formula + halting-mechanism + telemetry-sensitivity; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s N=%d V=%d L_support=%s frozen_dd=%d d_max=%d"
          % (DEVICE, N_DIM, V_NODES, L_SUPPORT, FROZEN_DD, D_MAX), flush=True)
    seed = SEEDS[0]
    g_np = np.random.default_rng(seed)
    tgen = torch.Generator(device=DEVICE); tgen.manual_seed(int(seed) * 100003 + int(V_NODES))
    E = cf.make_bipolar_E(V_NODES, N_DIM, tgen)
    per_op, train_c, train_L, test_c, test_L = make_hetero_chains(seed, g_np)
    W_ops = [cf.hebbian_W(per_op[i], E, N_DIM) for i in range(N_OPS)]
    adj = cf.build_adjacency(per_op, N_OPS)
    transitions = cf.collect_rollout_transitions(adj, N_OPS, V_NODES, rollout_count(V_NODES), D_MAX + 2, g_np)
    sr_gen = torch.Generator(device=DEVICE); sr_gen.manual_seed(int(seed) * 7919 + int(V_NODES))
    M, _ = cf.train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
    _, te_targets = _start_target(test_c)
    goal_te = E[te_targets]

    # ST-CORPUS: heterogeneous L present, mean-centered on FROZEN_DD.
    for L in L_SUPPORT:
        assert int((test_L == L).sum()) > 0, "ST-CORPUS missing length %d" % L
    assert abs(float(np.mean(test_L)) - FROZEN_DD) < 0.6, "ST-CORPUS mean L off frozen_dd"
    print("[selftest] ST-CORPUS OK: L counts=%s meanL=%.2f"
          % ({int(L): int((test_L == L).sum()) for L in L_SUPPORT}, float(np.mean(test_L))), flush=True)

    # ST-ARRIVAL: on a CLEAN state == goal node, arrival confidence cos==1; on a different node ~ 0.
    gnode = int(te_targets[0])
    a_self = float((cf._norm_rows(E[gnode:gnode + 1]) * cf._norm_rows(E[gnode:gnode + 1])).sum())
    other = (gnode + 1) % V_NODES
    a_other = float((cf._norm_rows(E[other:other + 1]) * cf._norm_rows(E[gnode:gnode + 1])).sum())
    assert a_self > 0.95 and abs(a_other) < 0.20, "ST-ARRIVAL cos separation failed self=%.3f other=%.3f" % (a_self, a_other)
    print("[selftest] ST-ARRIVAL OK: cos(goal,goal)=%.3f cos(other,goal)=%.3f" % (a_self, a_other), flush=True)

    # tune actor + theta quickly (reuse the real pipeline on this small regime)
    _, tr_targets = _start_target(train_c)
    goal_tr = E[tr_targets]
    alpha, wr = 0.2, 1.0
    best_theta, best_apc = THETA_GRID[0], -1.0
    for th in THETA_GRID:
        c, h = _nav_core(train_c, W_ops, E, M, goal_tr, alpha, wr, D_MAX, MIN_HOPS, _decider_adaptive(th))
        apc = _accpc(c, h)
        if apc > best_apc:
            best_apc, best_theta = apc, th

    rd_gen = torch.Generator(device=DEVICE); rd_gen.manual_seed(123)
    td = torch.randint(D_MIN, D_MAX + 1, (len(test_c),), generator=rd_gen, device=DEVICE)
    scr_gen = torch.Generator(device=DEVICE); scr_gen.manual_seed(321)

    fixed = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, FROZEN_DD, MIN_HOPS, _decider_never())
    ceil = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, D_MAX, MIN_HOPS, _decider_never())
    adapt = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, D_MAX, MIN_HOPS, _decider_adaptive(best_theta))
    rand = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, D_MAX, MIN_HOPS, _decider_target_depth(td))
    scr = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, D_MAX, MIN_HOPS, _decider_scrambled(best_theta, scr_gen))
    orc = _nav_core(test_c, W_ops, E, M, goal_te, alpha, wr, D_MAX, MIN_HOPS, _decider_oracle())

    apc = {"fixed": _accpc(*fixed), "ceil": _accpc(*ceil), "adapt": _accpc(*adapt),
           "rand": _accpc(*rand), "scr": _accpc(*scr), "orc": _accpc(*orc)}
    corr_a = _pearson(adapt[1], orc[1])
    corr_s = _pearson(scr[1], orc[1])
    spread = float(np.std(adapt[1]))
    print("[selftest] acc[F=%.3f CEIL=%.3f A=%.3f R=%.3f S=%.3f O=%.3f] accpc[F=%.4f A=%.4f R=%.4f S=%.4f O=%.4f]"
          " corr[A=%.3f S=%.3f] spread=%.2f theta*=%.2f"
          % (np.mean(fixed[0]), np.mean(ceil[0]), np.mean(adapt[0]), np.mean(rand[0]), np.mean(scr[0]), np.mean(orc[0]),
             apc["fixed"], apc["adapt"], apc["rand"], apc["scr"], apc["orc"], corr_a, corr_s, spread, best_theta), flush=True)

    # ST-MECHANISM: adaptive halting beats the frozen value on acc-per-compute, and matches-or-beats accuracy.
    assert apc["adapt"] > apc["fixed"] * 1.05, "ST-MECHANISM adaptive did not beat fixed accpc (A=%.4f F=%.4f)" % (apc["adapt"], apc["fixed"])
    assert np.mean(adapt[0]) >= np.mean(fixed[0]) - 0.02, "ST-MECHANISM adaptive quality below fixed"
    # ST-SIGNAL: adaptive beats random-depth (arrival signal load-bearing, not mere depth variance).
    assert apc["adapt"] > apc["rand"], "ST-SIGNAL adaptive did not beat random-depth (A=%.4f R=%.4f)" % (apc["adapt"], apc["rand"])
    # ST-TELEMETRY-SENSITIVITY (MANDATORY): scrambling the arrival signal collapses the gain toward random.
    assert apc["scr"] < apc["adapt"] * 0.90, "ST-TELEMETRY scramble did not collapse (S=%.4f A=%.4f)" % (apc["scr"], apc["adapt"])
    assert corr_a > 0.30 and (corr_a - corr_s) > 0.20, "ST-TELEMETRY corr not signal-specific (A=%.3f S=%.3f)" % (corr_a, corr_s)
    # ST-REALLOCATION: adaptive genuinely varies its depth (not collapsed to a single fixed value).
    assert spread >= 0.5, "ST-REALLOCATION hop spread too small (%.2f) -- collapsed to fixed" % spread
    # ST-DRIFT: fixed-HIGH over-runs short chains (fixed_ceil worse than adaptive on the shortest-L subset).
    shortL = min(L_SUPPORT)
    m = (test_L == shortL)
    assert float(np.mean(adapt[0][m])) > float(np.mean(ceil[0][m])) - 1e-9, "ST-DRIFT adaptive not better than ceil on short chains"
    # ST-ARMS-DIFFER: load-bearing arms produce distinct (correct,hops) vectors.
    def _hsh(r):
        return hashlib.sha256(r[0].astype(np.int8).tobytes() + r[1].astype(np.int64).tobytes()).hexdigest()[:16]
    lb = {"FIXED_DD": _hsh(fixed), "FIXED_DD_CEIL": _hsh(ceil), "ADAPTIVE_EVC": _hsh(adapt),
          "RANDOM_DEPTH": _hsh(rand), "SCRAMBLED_HALT": _hsh(scr)}
    assert len(set(lb.values())) == len(lb), "ST-ARMS-DIFFER load-bearing arms collided: %s" % lb
    print("[selftest] ST-MECHANISM/SIGNAL/TELEMETRY/REALLOCATION/DRIFT/ARMS-DIFFER OK", flush=True)

    # ST-PIPELINE: full per-seed record has all arms + fields.
    r = run_one_seed(seed, REPO / "data" / "exp_selftest_tmp_acc_evc_halting")
    for arm in ARMS:
        assert arm in r["arms"], "ST-PIPELINE missing arm %s" % arm
    assert "theta_star" in r and "corr_adaptive" in r, "ST-PIPELINE missing fields"
    print("[selftest] ST-PIPELINE OK theta*=%.2f reach_rank=%.3f" % (r["theta_star"], r["reach_rank_test"]), flush=True)
    return 0


# ============================================================================
# main
# ============================================================================
def main() -> int:
    global _T0
    _T0 = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir)

    print("[%s] mode=%s device=%s N=%d V=%d frozen_dd=%d L_support=%s d_max=%d seeds=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, V_NODES, FROZEN_DD, L_SUPPORT, D_MAX, SEEDS, EXPECTED_N_UNITS), flush=True)

    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL run requires CUDA; none available (route to overnight_queue).")

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST-CORPUS, ST-ARRIVAL, ST-MECHANISM (adaptive>fixed accpc), "
                               "ST-SIGNAL (adaptive>random), ST-TELEMETRY (scramble collapses + signal-specific "
                               "corr), ST-REALLOCATION (hop spread), ST-DRIFT (fixed-high over-runs), "
                               "ST-ARMS-DIFFER, ST-PIPELINE",
                "summary": "SELFTEST_OK", "elapsed_s": round(time.time() - _T0, 1),
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
                "run_mode": "selftest", "config_version": CONFIG_VERSION})
            print("[selftest] ALL OK", flush=True)
            return rc
        except SystemExit:
            raise
        except Exception as e:
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_FAIL",
                "verdict_msg": "SELFTEST_FAIL: %s" % e, "summary": "SELFTEST_FAIL",
                "elapsed_s": round(time.time() - _T0, 1),
                "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
                "run_mode": "selftest", "traceback": traceback.format_exc()[:4000]})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            traceback.print_exc()
            return 1

    run_config = {"N": N_DIM, "V": V_NODES, "run_mode": RUN_MODE, "frozen_dd": FROZEN_DD, "L_support": L_SUPPORT}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    fatal_seed_errors: List[str] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        _heartbeat(out_dir, i, len(remaining), "seed_start=%d" % seed)
        try:
            result = run_one_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as e:
            fc = type(e).__name__
            fatal_seed_errors.append("seed=%d %s: %s" % (seed, fc, str(e)[:200]))
            write_partial_key(out_dir, seed, {
                "seed": int(seed), "run_mode": RUN_MODE, "N": N_DIM, "V": V_NODES,
                "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
                "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000], "arms": {}})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        _heartbeat(out_dir, i + 1, len(remaining), "seed_done=%d dt=%.1f" % (seed, time.time() - t0))
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("arms")}
    final = aggregate_and_verdict(good)
    if fatal_seed_errors:
        final["fatal_seed_errors"] = fatal_seed_errors
        if final.get("verdict") == "HARD_PASS":
            final["verdict"] = "MIDDLE_BAND"
            final["verdict_msg"] = "DEMOTED_FROM_HP_DUE_TO_SEED_CRASH | " + final["verdict_msg"]
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _T0, 1)
    final["ts_iso"] = datetime.now(timezone.utc).isoformat()
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["device"] = str(DEVICE)
    _atomic_write_metrics(out_dir, final)
    print("[%s] DONE: %s" % (ANCHOR_NAME, final.get("verdict_msg", "")), flush=True)
    return 0


if __name__ == "__main__":
    _env = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    _od = REPO / "data" / ("exp_" + _env)
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
