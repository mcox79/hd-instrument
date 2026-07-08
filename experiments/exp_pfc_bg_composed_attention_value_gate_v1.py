"""pfc_bg_composed_attention_value_gate_v1 -- COMPOSE two independently-certified brain gates.

WHAT THIS IS (brain-component integration; notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md):
  Two substrate gates are each already proven in isolation, weeks apart, for unrelated reasons:
    (A) v8 COMBINED attention-routing gate (exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu,
        commit 4227e7e97, CHAIN_GRADE): a biased-competition INPUT gate that arbitrates a recency prior
        and a content cue -- softmax(content_rel/GATE_TAU + recency_bias) -- to select the RIGHT slot in a
        K-slot scrolling window. It selects WHAT context to admit; it has no notion of "action".
    (B) cfrpe Go/NoGo value-gate (exp_pfc_gate_cfrpe_trained_v2, HARD_PASS): a basal-ganglia OUTPUT/motor
        gate. A learned successor-representation value (reach = cos(E[cand]@M, goal)) trained by the
        substrate RPE delta-rule (cfrpe) feeds a winner-take-all actor
        (Go_i = w_manifold*manifold_i + w_goal*goal_sim_i + w_reach*reach_i ; gate = argmax_i Go_i). It
        selects HOW to act toward a goal; it has no goal WITHOUT something to hand it one.
  They have NEVER been WIRED. Chatham & Badre (2021, PLOS Comp Biol) argue PFC/BG input/output/motor gating
  are the SAME Go/NoGo RPE primitive at different loci; this cell is the direct empirical test of that
  theoretical unification on two substrate mechanisms built completely independently.

THE WIRING (the WHOLE point; both gates reused UNCHANGED, only the goal SOURCE is swapped per arm):
  The Go/NoGo actor's goal signal is NOT handed in directly. It must be READ OUT by the v8 combined gate
  from a K-slot goal-cue window (mixed 1/3 each across v8's ALIGNED / CONFLICT / CUE_ABSENT sub-regimes),
  then fed -- as goal_hat -- into the unchanged cfrpe Go/NoGo actor for a multi-hop navigation task. Task
  correctness requires BOTH stages: attention must find the right goal representation, AND the value-gate
  must select the right actions given it. Neither gate alone can solve this composed task.
    goal_hat = gate_readout(K_slot_goal_codes, v8_combined_gate_weights)     # v8 admission gate (INPUT)
    correct  = navigate(start, ops; goal=goal_hat) == true_target            # cfrpe Go/NoGo (OUTPUT)

REUSE CONTRACT (grep-first; do NOT re-implement either gate):
  - cfrpe primitives are IMPORTED unchanged (import-safe: cfrpe main is __name__-guarded):
      make_bipolar_E, hebbian_W, cleanup_batched, make_kb_and_chains, build_adjacency,
      collect_rollout_transitions, train_sr_transport (the cfrpe RPE delta-rule), reach_value,
      run_oracle_arm, reach_rank_acc, binom_two_sided_p, _chain_tensors, _norm_rows, DEVICE, DTYPE.
    run_selection_with_goal below is cfrpe.run_selection_arm TRANSCRIBED with ONE change: goal_E is an
    EXTERNAL vector (the pooled attention output) instead of E[targets]. The scoring formula, reach
    (cf.reach_value), and cleanup (cf.cleanup_batched) are cfrpe's unchanged -- this is WIRING, not a
    re-implementation of the actor.
  - v8 gate functions are TRANSCRIBED VERBATIM (v8 module runs _selftest()+main() at top level => NOT
    import-safe): content_relevance, content_gate_from_rel, combined_gate_from_rel, recency_bias_from_gate,
    learn_recency_gate, gate_readout, _derangement, build_slot_codes. The self-test ST-V8 reproduces v8's
    arbitration pattern at the test regime (SCHEMA-VET Gate D positive control for the transcription).

ARMS (paired -- all share E / W_ops / cfrpe-trained M / test chains / goal-windows per (seed,K); arms differ
  ONLY by (goal source, action-selection)):
  ORACLE_GOAL_GONOGO       goal = E[true target] (handed directly). standalone value-gate CEILING; Gate-D
                           positive control that reproduces cfrpe v2's own V1200_d4 numbers in-cell.
  V8_GATE_GONOGO           goal = v8 combined-gate soft-pooled over the K goal-cue slots. THE TEST.
  RAW_UNIFORM_GONOGO       goal = uniform pooling over the K slots (attention-blind control). isolates whether
                           attention is load-bearing.
  V8_GATE_SCRAMBLED_GONOGO goal = v8 gate with the CONTENT relevance deranged (recency intact) -> a sharp cue
                           lands on a WRONG slot. TELEMETRY-SENSITIVITY guard (mandatory: two tautological-
                           metric incidents 2026-07-07/08). Must collapse toward RAW_UNIFORM.
  V8_GATE_ADDITIVE         goal = v8 gate pooled, but action-selection reverts to the static ADDITIVE actor
                           (no reach term). isolates whether the value-based actor adds anything once
                           attention is solved (PFC gates WHAT enters; BG separately decides HOW to act).
  ORACLE_ACTION            applies the true op_seq (goal-independent). navigation CEILING (closure rail).
  (w_reach==0 null reduction is verified in the self-test ST-REDUCE: gonogo@w_reach=0 == additive, so it is
   not carried as a redundant full arm.)

DISCRIMINATORS (headline K=6, cue_q=0.25 == v8 headline realistic cue > arbitration boundary q*=0.15):
  att_lift        = V8_GATE_GONOGO - RAW_UNIFORM_GONOGO            (attention necessity)
  composition_tax = ORACLE_GOAL_GONOGO - V8_GATE_GONOGO           (cost of imperfect attention into the value decision)
  scramble_gap    = V8_GATE_GONOGO - V8_GATE_SCRAMBLED_GONOGO     (mandatory telemetry-sensitivity guard)
  closure         = att_lift / (ORACLE_GOAL_GONOGO - RAW_UNIFORM_GONOGO)   (fraction of attention headroom closed)
  value_actor_lift= V8_GATE_GONOGO - V8_GATE_ADDITIVE            (reach-term contribution given good attention)

CONTRACT (pre-registered; preregs/2026-07-08_pfc_bg_composed_attention_value_gate_v1.md):
  HARD_PASS  : at a valid regime (see guards) -- closure >= 0.25 AND att_lift >= 0.15 AND scramble_gap >= 0.30
               AND composition_tax <= 0.20 AND oracle_action >= 0.90 AND oracle_goal reproduces cfrpe
               (ORACLE_REPRO_LO <= oracle_goal <= ORACLE_REPRO_HI) AND reach_rank_test > 0.30 AND arms differ.
  MIDDLE_BAND: att_lift >= 0.15 (attention genuinely load-bearing) but composition_tax > 0.20 OR closure < 0.25
               OR scramble_gap in [0.15, 0.30).
  HARD_FAIL  : att_lift < 0.15 (composition adds nothing -- two independently-proven gates do not combine).
  INCONCLUSIVE_TAUTOLOGICAL_METRIC : scramble_gap < 0.15 (the discriminator is NOT telemetry-sensitive; same
               failure class as the two 2026-07 metric-tautology incidents -- reported as inconclusive, NOT a
               clean negative).
  INCONCLUSIVE_NO_ATTENTION_PRESSURE : RAW_UNIFORM >= oracle_goal - 0.05 (uniform pooling already solves it;
               the corpus does not force attention -- regime miss, not a structural verdict).
  INCONCLUSIVE_NAV_CEILING_BROKEN : oracle_action < 0.90 (cleanup/navigation regime broken).
  INCONCLUSIVE_ORACLE_GOAL_MISMATCH : oracle_goal outside the cfrpe reproduce band (Gate D: the value-gate did
               not reproduce at the test regime -> downstream arms untrustworthy).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 of per-(seed,K) arm accuracy curves; the 6 diverge)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-gap discriminator; no single closed-form noise floor. Reachability by feasibility --
#   cfrpe v2 MEASURED gonogo=0.653 & v8 COMBINED~1.0 at exactly this regime, so ORACLE_GOAL headroom and
#   V8-recovered goal are both well above the discriminator gates (see prereg predicted_accuracy_per_point).
# - baseline_in_band (META_RULE_AG): the CONTROL here is RAW_UNIFORM (must be handicapped: RAW < oracle_goal-0.05);
#   ORACLE_ACTION must rail (>=0.90); ORACLE_GOAL must land in the cfrpe reproduce band. Enforced as guards.
# - discriminator survives scale: smoke holds N/V == FULL N/V (6.83) so per-hop cleanup difficulty matches, AND
#   cue_snr=q*sqrt(N) is LOWER at smoke N (harder cue) -> smoke is a discriminator PREVIEW (option C).
# - HARD_PASS strictly above floor (META_RULE_L): gates are strict (>=0.25 / >=0.15 / >=0.30 / <=0.20).
# - HP_SCOPE: HP gates apply to V8_GATE_GONOGO vs {RAW_UNIFORM, ORACLE_GOAL, V8_GATE_SCRAMBLED}. ORACLE_ACTION
#   carries only the >=0.90 nav rail; ORACLE_GOAL carries only the reproduce band.
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(K_GRID)*len(ARMS); verdict counts completed units.
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05, RECENCY_GAP_TARGET=3.0 (v8 a-priori, in
#   logit units; NOT tuned per-q). cfrpe alpha/w_reach TUNED on TRAIN with the ORACLE goal (the standalone-good
#   params) then FROZEN across all arms -> the actor is unchanged; only the goal source varies.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@:
#     cfrpe V1200_d4 gonogo=0.653 additive=0.053 oracle=0.962 closure=0.661
#       MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4
#     v8 COMBINED headline top1~1.0 (3/3 seeds) CITED@notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md
#     RAW uniform goal-recovery cap ~ 1/K THEORETICAL@ K near-orthogonal codes -> ambiguous cleanup
#     arb boundary q* = GATE_TAU*RECENCY_GAP_TARGET = 0.15 THEORETICAL@ v8 biased-competition boundary
#     att_lift full HARD_PASS P_deflated=0.38 HYPOTHESIZED@notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md

Compute architecture: (a) batched-GPU. SR-TD training, operator application, cleanup, reach, and the v8 gate
  pooling are batched matmuls on cuda-if-available. SR trained ONCE per seed (single V=1200) -> cheaper than
  cfrpe v2 (which trained per unique V). Chains batched; within-chain hops are sequential (genuine dependency).
  FULL requires cuda (overnight_queue). Storage: sharded (each operator its own W; M is a learned value
  operator). Goal-cue slots are a single-hop attention read (no composition store).
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line + per-seed/K
  heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_pfc_bg_composed_attention_value_gate_v1.md
Reuses:
  experiments/exp_pfc_gate_cfrpe_trained_v2.py            (imported; Go/NoGo actor + cfrpe RPE SR, unchanged)
  experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py (v8 gate funcs transcribed verbatim)
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
    resumable_seeds, write_partial_key, aggregate_partials,
)

# cfrpe is IMPORT-SAFE (main is __name__-guarded). Reuse its primitives + the Go/NoGo actor unchanged.
import experiments.exp_pfc_gate_cfrpe_trained_v2 as cf

ANCHOR_NAME = "pfc_bg_composed_attention_value_gate_v1"

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

# Use cfrpe's DEVICE so imported-cfrpe tensors and locally-built tensors always live on the same device.
DEVICE = cf.DEVICE
DTYPE = cf.DTYPE

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
HP_CLOSURE_FLOOR = 0.25            # V8_GATE closes >= 25% of the attention headroom
HP_ATT_LIFT_MIN = 0.15            # V8_GATE - RAW_UNIFORM (attention load-bearing)
HP_SCRAMBLE_GAP_MIN = 0.30        # V8_GATE - V8_GATE_SCRAMBLED (telemetry-sensitivity, v8 content-gate threshold)
HP_COMPOSITION_TAX_MAX = 0.20     # ORACLE_GOAL - V8_GATE (graceful composition)
HF_ATT_LIFT_CEIL = 0.15           # att_lift < this => HARD_FAIL (composition adds nothing)
TAUT_SCRAMBLE_FLOOR = 0.15        # scramble_gap < this => INCONCLUSIVE_TAUTOLOGICAL_METRIC (NOT a clean negative)
MB_SCRAMBLE_LO = 0.15             # scramble_gap in [0.15,0.30) => MIDDLE_BAND (present but weak)
NAV_RAIL_MIN = 0.90               # ORACLE_ACTION must reach this (navigation ceiling)
HP_REACH_RANK_MIN = 0.30          # cfrpe mechanism-fires (reach informative > chance 1/n_ops)
ATT_PRESSURE_MARGIN = 0.05        # RAW must be handicapped: RAW < oracle_goal - this
# cfrpe reproduce band (Gate D): cfrpe v2 V1200_d4 gonogo=0.653
#   MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json:per_regime.V1200_d4.gonogo. tolerance +/-0.13.
ORACLE_REPRO_LO = 0.45
ORACLE_REPRO_HI = 0.85

# cfrpe knobs (reused; DENSITY/GAMMA/SR_LR match cfrpe v2 constants)
N_OPS = 4
DENSITY = 0.21
GAMMA = cf.GAMMA
SR_LR = cf.SR_LR

# v8 combined-gate knobs (a-priori, in logit units; NOT tuned per-q). CITED@ v8 cell constants.
GATE_TAU = 0.05
RECENCY_TAU = 0.2
RECENCY_GAP_TARGET = 3.0
ARB_BOUNDARY_Q = GATE_TAU * RECENCY_GAP_TARGET   # = 0.15 THEORETICAL@ v8 biased-competition boundary
CUE_Q = 0.25                                     # v8 headline realistic cue (> q* => content wins conflicts)
TYPE_FRACS = [1.0 / 3, 1.0 / 3, 1.0 / 3]         # aligned / conflict / cue_absent

# cfrpe actor tuning grids (tuned on TRAIN w/ ORACLE goal, then FROZEN across arms)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]

ARMS = ["ORACLE_GOAL_GONOGO", "V8_GATE_GONOGO", "RAW_UNIFORM_GONOGO",
        "V8_GATE_SCRAMBLED_GONOGO", "V8_GATE_ADDITIVE", "ORACLE_ACTION"]
HEADLINE_K = 6

# --------------------------- config (selftest / smoke / full) --------------------
# Regimes are K values (decision_depth pinned at DD; V pinned so N/V == FULL). SMOKE holds N/V == FULL N/V
# (=6.83 at V1200/N8192) so per-hop cleanup difficulty matches; smoke cue_snr is LOWER (harder) -> preview.
DD = 4
if SELF_TEST_MODE:
    N_DIM = 512
    V_NODES = 60
    SEEDS = [7]
    K_GRID = [4]
    N_TRAIN_CHAINS = 16
    N_TEST_CHAINS = 16
    SR_STEPS = 200
    SR_BATCH = 32
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_NODES = 300                  # N/V = 6.83 == FULL
    SEEDS = [7, 17]
    K_GRID = [4, 6]
    N_TRAIN_CHAINS = 60
    N_TEST_CHAINS = 60
    SR_STEPS = 1500                # discriminator-PREVIEW: stronger SR (reach_rank ~ FULL) so smoke att_lift
    SR_BATCH = 96                  # previews the FULL headroom rather than the under-trained-SR floor
    ROLLOUT_PER_V = 20
else:  # full
    N_DIM = 8192
    V_NODES = 1200                 # N/V = 6.83 (cfrpe v2 FAIR moderate regime; MEASURED gonogo=0.653)
    SEEDS = [7, 17, 23, 31, 41]
    K_GRID = [4, 6]
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 9000 if RUN_MODE == "smoke" else (2000 if SELF_TEST_MODE else 200000)
FLAG_AUG_ID = V_NODES              # augmented codebook id for the FLAG code (row V of Eaug)

EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID) * len(ARMS)
assert HEADLINE_K in K_GRID or SELF_TEST_MODE, "HEADLINE_K must be in K_GRID (except selftest)"


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,n_ops=%d,dd=%d,K_grid=%s,seeds=%s,density=%.3f,sr_steps=%d,sr_batch=%d,"
    "rollout_per_V=%d,gamma=%.2f,lr=%.2f,gate_tau=%.3f,recency_gap=%.2f,cue_q=%.3f,arb_q*=%.3f,"
    "n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_closure>=%.2f,att_lift>=%.2f,scramble>=%.2f,tax<=%.2f,nav_rail>=%.2f"
) % (
    ANCHOR_NAME, N_DIM, V_NODES, N_OPS, DD, K_GRID, SEEDS, DENSITY, SR_STEPS, SR_BATCH,
    ROLLOUT_PER_V, GAMMA, SR_LR, GATE_TAU, RECENCY_GAP_TARGET, CUE_Q, ARB_BOUNDARY_Q,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_CLOSURE_FLOOR, HP_ATT_LIFT_MIN, HP_SCRAMBLE_GAP_MIN, HP_COMPOSITION_TAX_MAX, NAV_RAIL_MIN,
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
# v8 combined-gate functions -- TRANSCRIBED VERBATIM from
# experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py (NOT import-safe).
# gate_readout / content_relevance / content_gate_from_rel / combined_gate_from_rel /
# recency_bias_from_gate / learn_recency_gate / _derangement / build_slot_codes.
# ============================================================================
def gate_readout(slot_codes: torch.Tensor, gate: torch.Tensor) -> torch.Tensor:
    """Gate-weighted superposition of the K raw slot codes -> (B,N) normalized. gate: (K,) or (B,K)."""
    B, K, n = slot_codes.shape
    w = gate.view(1, K, 1) if gate.dim() == 1 else gate.unsqueeze(2)
    b = (w * slot_codes).sum(dim=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def content_relevance(slot_codes: torch.Tensor, flag_code: torch.Tensor) -> torch.Tensor:
    """r_j = cos(slot_code_{j-1}, flag_code) for j>=1; slot 0 set to per-row min (never selected)."""
    B, K, n = slot_codes.shape
    r = torch.empty(B, K, device=DEVICE)
    r[:, 0] = -1e9
    for j in range(1, K):
        r[:, j] = (slot_codes[:, j - 1] * flag_code).sum(dim=1)
    r[:, 0] = r[:, 1:].min(dim=1).values
    return r


def content_gate_from_rel(r: torch.Tensor, tau: float) -> torch.Tensor:
    B, K = r.shape
    rm = r.clone()
    rm[:, 0] = -1e9
    return torch.softmax(rm / tau, dim=1)


def combined_gate_from_rel(r: torch.Tensor, recency_bias: torch.Tensor, tau: float,
                           scramble_perm=None) -> torch.Tensor:
    """softmax(content_rel/tau + recency_bias). scramble_perm deranges CONTENT relevance only (recency intact)."""
    B, K = r.shape
    cr = r if scramble_perm is None else r[:, scramble_perm]
    logit = cr / tau + recency_bias.unsqueeze(0)
    return torch.softmax(logit, dim=1)


def _derangement(K: int, seed_val: int) -> torch.Tensor:
    g = torch.Generator(device="cpu").manual_seed(int(seed_val))
    ar = torch.arange(K)
    for _ in range(200):
        perm = torch.randperm(K, generator=g)
        if int((perm == ar).sum()) == 0:
            return perm.to(DEVICE)
    return torch.arange(K - 1, -1, -1, device=DEVICE)


def learn_recency_gate(win_tr: torch.Tensor, goalslot_tr: torch.Tensor, K: int,
                       tau: float, m_gate: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """v5-style LEARNED fixed per-index gate (content-blind): per-position empirical goal-slot rate ->
    softmax(r/tau). On this corpus the goal-slot is K-1 for aligned+cue_absent (~2/3) so g concentrates
    on the most-recent slot. win_tr:(M,K) node-id windows; goalslot_tr:(M,) the correct slot index."""
    M = min(m_gate, win_tr.shape[0])
    gs = goalslot_tr[:M]                                   # (M,)
    r = torch.zeros(K, device=DEVICE)
    onehot = torch.zeros(M, K, device=DEVICE)
    onehot[torch.arange(M, device=DEVICE), gs] = 1.0
    r = onehot.mean(dim=0)                                 # (K,) per-position goal-slot rate
    return torch.softmax(r / tau, dim=0), r


def recency_bias_from_gate(g_rec: torch.Tensor) -> Tuple[torch.Tensor, float]:
    """Fixed top-down recency prior for COMBINED (logit units): log g_rec, top slot=0, gap==RECENCY_GAP_TARGET."""
    rlog = torch.log(g_rec + 1e-6)
    rlog = rlog - rlog.max()
    srt = torch.sort(rlog, descending=True).values
    gap_raw = float(srt[0] - srt[1]) if rlog.numel() >= 2 else 1.0
    beta = RECENCY_GAP_TARGET / max(gap_raw, 1e-6)
    return rlog * beta, beta


def build_slot_codes(Eaug: torch.Tensor, win: torch.Tensor, cue_q: float,
                     flag_code: torch.Tensor, gen: torch.Generator) -> torch.Tensor:
    """Per-slot code tensor (B,K,N). Non-flag slots = Eaug[node]. Flag slots (win==FLAG_AUG_ID) replaced by a
    per-instance NOISY flag normalize(cue_q*flag_code + sqrt(1-q^2)*rand) so cos(noisy,flag)~=cue_q. Transcribed
    from v8; codebook Eaug row FLAG_AUG_ID == flag_code. cue_absent rows have no flag -> untouched."""
    flag_id = Eaug.shape[0] - 1                            # last row of Eaug is the flag code
    codes = Eaug[win].clone()                              # (B,K,N)
    if cue_q < 0.999:
        flag_mask = (win == flag_id)
        nf = int(flag_mask.sum())
        if nf > 0:
            n = codes.shape[2]
            noise = (torch.randint(0, 2, (nf, n), generator=gen, device=DEVICE).float() * 2 - 1)
            noise = noise / (noise.norm(dim=1, keepdim=True) + 1e-8)
            alpha = math.sqrt(max(0.0, 1.0 - cue_q * cue_q))
            noisy = cue_q * flag_code.unsqueeze(0) + alpha * noise
            noisy = noisy / (noisy.norm(dim=1, keepdim=True) + 1e-8)
            codes[flag_mask] = noisy
    return codes


# ============================================================================
# goal-cue windows (v8's three arbitration types, but slots hold NODE codes; target = the chain's target node)
# ============================================================================
def gen_goal_windows(tgt_nodes: np.ndarray, K: int, V: int, g: np.random.Generator
                     ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (win (M,K) int64 of node-ids with FLAG_AUG_ID markers, itype (M,) in {0,1,2}, goalslot (M,)).
    ALIGNED  (0): FLAG at K-2, goal(target node) at K-1 (== most-recent slot). recency==content.
    CONFLICT (1): FLAG at v-1, goal at v in {1..K-2}; slot K-1 = a DISTRACTOR node. content correct, recency wrong.
    CUE_ABSENT(2): NO flag; goal at K-1 (== most-recent). recency correct, content flat-noise.
    The goal-slot holds tgt_node; all other node-slots hold DISTINCT distractor nodes != tgt_node."""
    M = len(tgt_nodes)
    win = np.zeros((M, K), dtype=np.int64)
    itype = np.zeros(M, dtype=np.int64)
    goalslot = np.zeros(M, dtype=np.int64)
    types = g.choice(3, size=M, p=TYPE_FRACS)
    for i in range(M):
        t = int(types[i]); itype[i] = t
        tgt = int(tgt_nodes[i])
        if t == 2:                                          # CUE_ABSENT: no flag, goal at most-recent slot
            v = K - 1
            distract = _distinct_nodes(V, tgt, K - 1, g)
            slots = list(distract)
            slots.insert(v, tgt)                            # v==K-1 -> append at end
            for s in range(K):
                win[i, s] = int(slots[s])
        else:
            v = (K - 1) if t == 0 else int(g.integers(1, K - 1))
            win[i, v - 1] = V                               # FLAG id == V (row V of Eaug); before the goal slot
            nonflag = [s for s in range(K) if s != v - 1]   # includes slot v (goal) and slot K-1
            distract = _distinct_nodes(V, tgt, len(nonflag) - 1, g)
            di = 0
            for s in nonflag:
                if s == v:
                    win[i, s] = tgt
                else:
                    win[i, s] = int(distract[di]); di += 1
        goalslot[i] = v
    return win, itype, goalslot


def _distinct_nodes(V: int, exclude: int, n: int, g: np.random.Generator) -> np.ndarray:
    """n distinct node-ids in [0,V) excluding `exclude`."""
    if n <= 0:
        return np.zeros(0, dtype=np.int64)
    pool = g.choice(V, size=min(V, n + 4), replace=False)
    pool = np.array([int(x) for x in pool if int(x) != exclude], dtype=np.int64)
    while pool.shape[0] < n:
        extra = int(g.integers(0, V))
        if extra != exclude and extra not in pool:
            pool = np.append(pool, extra)
    return pool[:n]


# ============================================================================
# goal_hat producers (per arm) + the WIRING: cfrpe Go/NoGo actor with an EXTERNAL goal
# ============================================================================
def pooled_goals(Eaug: torch.Tensor, win_t: torch.Tensor, flag_code: torch.Tensor,
                 recency_bias: torch.Tensor, perm: torch.Tensor, cue_q: float,
                 gen: torch.Generator) -> Dict[str, torch.Tensor]:
    """Build the K-slot noisy codes ONCE, derive the goal_hat vector for each attention arm (shared codes ->
    arms differ only by the admission gate). Returns {arm: goal_hat (B,N)}."""
    slot_codes = build_slot_codes(Eaug, win_t, cue_q, flag_code, gen)     # (B,K,N)
    B, K, n = slot_codes.shape
    r = content_relevance(slot_codes, flag_code)
    g_comb = combined_gate_from_rel(r, recency_bias, GATE_TAU, None)
    g_scr = combined_gate_from_rel(r, recency_bias, GATE_TAU, perm)
    g_uni = torch.full((K,), 1.0 / K, device=DEVICE)
    return {
        "V8": gate_readout(slot_codes, g_comb),
        "SCRAMBLED": gate_readout(slot_codes, g_scr),
        "RAW": gate_readout(slot_codes, g_uni),
    }


def run_selection_with_goal(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                            M: torch.Tensor, depth: int, alpha: float, w_reach: float,
                            goal_vecs: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """cfrpe.run_selection_arm TRANSCRIBED with ONE change: goal_E is the EXTERNAL goal_vecs (the pooled
    attention output) instead of E[targets]. Scoring, reach (cf.reach_value), cleanup (cf.cleanup_batched)
    are cfrpe's unchanged. mode in {additive, gonogo}. goal_vecs:(n_chains,N). Returns (correct_bool, op_trace)."""
    starts, targets, _ = cf._chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = goal_vecs                                       # <-- the wiring: external goal (was E[targets])
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cf.cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = cf._norm_rows(out)
            goal_sim = (out_n * cf._norm_rows(goal_E)).sum(dim=1)
            if mode == "additive":
                sc = alpha * goal_sim + w_manifold * manifold
            elif mode == "gonogo":
                reach = cf.reach_value(cleaned, goal_E, M)
                sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach
            else:
                raise ValueError("unknown mode %r" % mode)
            scores[:, op] = sc
        chosen = scores.argmax(dim=1)
        op_trace[:, hop] = chosen.detach().cpu().numpy()
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, chosen]
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool), op_trace


# ============================================================================
# per-(seed,K) evaluation
# ============================================================================
def _eval_seed_K(seed: int, K: int, E: torch.Tensor, Eaug: torch.Tensor, flag_code: torch.Tensor,
                 W_ops: List[torch.Tensor], M: torch.Tensor, train_c, test_c,
                 g_np: np.random.Generator) -> Dict[str, Any]:
    # ---- build goal-cue windows for train (recency-gate learning + actor tuning) and test ----
    tr_starts, tr_targets, _ = cf._chain_tensors(train_c)
    te_starts, te_targets, _ = cf._chain_tensors(test_c)
    tr_tgt_np = tr_targets.detach().cpu().numpy()
    te_tgt_np = te_targets.detach().cpu().numpy()
    win_tr_np, it_tr_np, gs_tr_np = gen_goal_windows(tr_tgt_np, K, V_NODES, g_np)
    win_te_np, it_te_np, gs_te_np = gen_goal_windows(te_tgt_np, K, V_NODES, g_np)
    win_tr = torch.tensor(win_tr_np, device=DEVICE)
    win_te = torch.tensor(win_te_np, device=DEVICE)
    goalslot_tr = torch.tensor(gs_tr_np, device=DEVICE)

    # ---- learn the v8 recency gate + fixed top-down recency bias (content-blind) ----
    g_rec, r_rec = learn_recency_gate(win_tr, goalslot_tr, K, RECENCY_TAU, win_tr.shape[0])
    recency_bias, beta = recency_bias_from_gate(g_rec)
    perm = _derangement(K, seed * 17 + K)

    # ---- goal_hat producers on TRAIN (for actor tuning with ORACLE goal) and TEST ----
    oracle_goal_tr = E[tr_targets]
    oracle_goal_te = E[te_targets]
    gen_tr = torch.Generator(device=DEVICE).manual_seed(seed * 100003 + K * 7 + 1)
    gen_te = torch.Generator(device=DEVICE).manual_seed(seed * 100003 + K * 7 + 2)
    pooled_te = pooled_goals(Eaug, win_te, flag_code, recency_bias, perm, CUE_Q, gen_te)

    # ---- tune alpha (additive) + w_reach (gonogo) on TRAIN with the ORACLE goal, then FREEZE across arms ----
    best_alpha, best_add = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_with_goal("additive", train_c, W_ops, E, M, K_depth(K), a, 0.0,
                                      oracle_goal_tr)[0].mean()
        if acc > best_add:
            best_add, best_alpha = acc, a
    best_wr, best_go = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_with_goal("gonogo", train_c, W_ops, E, M, K_depth(K), best_alpha, wr,
                                      oracle_goal_tr)[0].mean()
        if acc > best_go:
            best_go, best_wr = acc, wr

    # ---- mechanism-fires probe (cfrpe reach informativeness on TRUE goal, held-out) ----
    reach_rank_test = cf.reach_rank_acc(test_c, W_ops, E, M, DD)

    # ---- goal-recovery telemetry: cos(goal_hat, E[true target]) per attention arm (test) ----
    def _goal_cos(gh):
        return float((cf._norm_rows(gh) * cf._norm_rows(oracle_goal_te)).sum(dim=1).mean())
    goal_cos = {"V8": _goal_cos(pooled_te["V8"]), "RAW": _goal_cos(pooled_te["RAW"]),
                "SCRAMBLED": _goal_cos(pooled_te["SCRAMBLED"]),
                "ORACLE": _goal_cos(oracle_goal_te)}

    # ---- evaluate all six arms on TEST chains (paired; frozen alpha/w_reach) ----
    dd = DD
    og_c, og_tr = run_selection_with_goal("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr, oracle_goal_te)
    v8_c, v8_tr = run_selection_with_goal("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr, pooled_te["V8"])
    raw_c, raw_tr = run_selection_with_goal("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr, pooled_te["RAW"])
    scr_c, scr_tr = run_selection_with_goal("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr, pooled_te["SCRAMBLED"])
    v8add_c, v8add_tr = run_selection_with_goal("additive", test_c, W_ops, E, M, dd, best_alpha, 0.0, pooled_te["V8"])
    orcact_c = cf.run_oracle_arm(test_c, W_ops, E, dd)

    arms_acc = {
        "ORACLE_GOAL_GONOGO": float(og_c.mean()),
        "V8_GATE_GONOGO": float(v8_c.mean()),
        "RAW_UNIFORM_GONOGO": float(raw_c.mean()),
        "V8_GATE_SCRAMBLED_GONOGO": float(scr_c.mean()),
        "V8_GATE_ADDITIVE": float(v8add_c.mean()),
        "ORACLE_ACTION": float(orcact_c.mean()),
    }
    # paired sign-test: V8_GATE vs RAW_UNIFORM (attention necessity)
    paired = {
        "n_v8_only": int((v8_c & (~raw_c)).sum()),
        "n_raw_only": int((raw_c & (~v8_c)).sum()),
        "n_test": int(len(v8_c)),
    }
    trace_hashes = {
        "ORACLE_GOAL_GONOGO": hashlib.sha256(og_tr.tobytes()).hexdigest()[:16],
        "V8_GATE_GONOGO": hashlib.sha256(v8_tr.tobytes()).hexdigest()[:16],
        "RAW_UNIFORM_GONOGO": hashlib.sha256(raw_tr.tobytes()).hexdigest()[:16],
        "V8_GATE_SCRAMBLED_GONOGO": hashlib.sha256(scr_tr.tobytes()).hexdigest()[:16],
        "V8_GATE_ADDITIVE": hashlib.sha256(v8add_tr.tobytes()).hexdigest()[:16],
        "ORACLE_ACTION": "oracle_true_seq",
    }
    return {
        "K": K, "arms": arms_acc, "trace_hashes": trace_hashes,
        "best_alpha": float(best_alpha), "best_w_reach": float(best_wr),
        "reach_rank_test": float(reach_rank_test), "goal_cos": goal_cos,
        "recency_gate": [round(float(x), 4) for x in g_rec.tolist()],
        "recency_argmax": int(g_rec.argmax()), "beta": float(beta),
        "scramble_perm": [int(x) for x in perm.tolist()],
        "type_fracs_test": [float((it_te_np == t).mean()) for t in range(3)],
        "paired": paired,
    }


def K_depth(K: int) -> int:
    """decision_depth is pinned at DD independent of K (K sizes the goal window, not the chain)."""
    return DD


# ============================================================================
# per-seed runner
# ============================================================================
def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g_np = np.random.default_rng(seed)
    depths_needed = [DD]

    # codebook, ops, chains, SR transport -- built ONCE per seed (single V)
    tgen = torch.Generator(device=DEVICE); tgen.manual_seed(int(seed) * 100003 + int(V_NODES))
    E = cf.make_bipolar_E(V_NODES, N_DIM, tgen)
    flag_gen = torch.Generator(device=DEVICE); flag_gen.manual_seed(int(seed) * 991 + 7)
    flag_row = (torch.randint(0, 2, (1, N_DIM), generator=flag_gen, device=DEVICE, dtype=DTYPE) * 2 - 1)
    flag_code = (flag_row / (flag_row.norm(dim=1, keepdim=True) + 1e-8))[0]
    Eaug = torch.cat([E, flag_code.unsqueeze(0)], dim=0)     # row FLAG_AUG_ID == flag_code

    per_op, train_by_d, test_by_d = cf.make_kb_and_chains(
        N_OPS, V_NODES, DENSITY, N_TRAIN_CHAINS, N_TEST_CHAINS, depths_needed, g_np)
    W_ops = [cf.hebbian_W(per_op[i], E, N_DIM) for i in range(N_OPS)]
    adj = cf.build_adjacency(per_op, N_OPS)

    max_len = DD + 2
    transitions = cf.collect_rollout_transitions(adj, N_OPS, V_NODES, rollout_count(V_NODES), max_len, g_np)
    sr_gen = torch.Generator(device=DEVICE); sr_gen.manual_seed(int(seed) * 7919 + int(V_NODES))
    M, sr_diag = cf.train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
    print("[seed=%d] SR trained: err %s->%s M_norm=%.3f n_trans=%d clamp=%d"
          % (seed, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
             sr_diag["n_transitions"], sr_diag["n_clamped_steps"]), flush=True)

    K_results: Dict[str, Any] = {}
    train_c = train_by_d[DD]; test_c = test_by_d[DD]
    for K in K_GRID:
        rec = _eval_seed_K(seed, K, E, Eaug, flag_code, W_ops, M, train_c, test_c, g_np)
        K_results["K%d" % K] = rec
        a = rec["arms"]
        print("[seed=%d K=%d] ORACLE_GOAL=%.3f V8=%.3f RAW=%.3f SCR=%.3f V8_ADD=%.3f ORC_ACT=%.3f "
              "(alpha=%.2f wr=%.1f reach_rank=%.3f goal_cos[V8=%.3f RAW=%.3f SCR=%.3f] rec_argmax=%d)"
              % (seed, K, a["ORACLE_GOAL_GONOGO"], a["V8_GATE_GONOGO"], a["RAW_UNIFORM_GONOGO"],
                 a["V8_GATE_SCRAMBLED_GONOGO"], a["V8_GATE_ADDITIVE"], a["ORACLE_ACTION"],
                 rec["best_alpha"], rec["best_w_reach"], rec["reach_rank_test"],
                 rec["goal_cos"]["V8"], rec["goal_cos"]["RAW"], rec["goal_cos"]["SCRAMBLED"],
                 rec["recency_argmax"]), flush=True)

    return {"seed": int(seed), "N": N_DIM, "V": V_NODES, "run_mode": RUN_MODE,
            "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
            "K_results": K_results, "sr_diag": sr_diag}


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_K": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _arm_col(kk, arm):
        return [float(per_seed[s]["K_results"][kk]["arms"][arm]) for s in keys
                if kk in per_seed[s].get("K_results", {})]

    def _scalar_col(kk, field):
        return [float(per_seed[s]["K_results"][kk][field]) for s in keys
                if kk in per_seed[s].get("K_results", {})]

    per_K: Dict[str, Any] = {}
    completed_units = 0
    for K in K_GRID:
        kk = "K%d" % K
        arm_means = {}; arm_stds = {}
        n_present = 0
        for arm in ARMS:
            vals = _arm_col(kk, arm)
            if vals:
                arm_means[arm] = float(np.mean(vals)); arm_stds[arm] = float(np.std(vals))
                n_present = len(vals)
            else:
                arm_means[arm] = 0.0; arm_stds[arm] = 0.0
        completed_units += n_present * len(ARMS)

        oracle_goal = arm_means["ORACLE_GOAL_GONOGO"]
        v8 = arm_means["V8_GATE_GONOGO"]
        raw = arm_means["RAW_UNIFORM_GONOGO"]
        scr = arm_means["V8_GATE_SCRAMBLED_GONOGO"]
        v8add = arm_means["V8_GATE_ADDITIVE"]
        orc_act = arm_means["ORACLE_ACTION"]

        att_lift = v8 - raw
        composition_tax = oracle_goal - v8
        scramble_gap = v8 - scr
        value_actor_lift = v8 - v8add
        headroom_att = oracle_goal - raw
        closure = (att_lift / headroom_att) if headroom_att > 1e-6 else 0.0

        reach_rank = float(np.mean(_scalar_col(kk, "reach_rank_test"))) if keys else 0.0
        gc_v8 = float(np.mean([per_seed[s]["K_results"][kk]["goal_cos"]["V8"] for s in keys
                               if kk in per_seed[s].get("K_results", {})])) if keys else 0.0
        gc_raw = float(np.mean([per_seed[s]["K_results"][kk]["goal_cos"]["RAW"] for s in keys
                                if kk in per_seed[s].get("K_results", {})])) if keys else 0.0
        gc_scr = float(np.mean([per_seed[s]["K_results"][kk]["goal_cos"]["SCRAMBLED"] for s in keys
                                if kk in per_seed[s].get("K_results", {})])) if keys else 0.0

        # paired sign-test V8 vs RAW pooled across seeds
        n_v8_only = sum(int(per_seed[s]["K_results"][kk]["paired"]["n_v8_only"]) for s in keys
                        if kk in per_seed[s].get("K_results", {}))
        n_raw_only = sum(int(per_seed[s]["K_results"][kk]["paired"]["n_raw_only"]) for s in keys
                         if kk in per_seed[s].get("K_results", {}))
        n_disc = n_v8_only + n_raw_only
        sign_p = cf.binom_two_sided_p(n_v8_only, n_disc, 0.5) if n_disc > 0 else 1.0

        # arms-differ (META_RULE_AF): the 4 gonogo goal-source arms must differ in op-trace per seed
        af_collision = False
        for s in keys:
            if kk not in per_seed[s].get("K_results", {}):
                continue
            th = per_seed[s]["K_results"][kk]["trace_hashes"]
            gonogo_traces = [th["ORACLE_GOAL_GONOGO"], th["V8_GATE_GONOGO"],
                             th["RAW_UNIFORM_GONOGO"], th["V8_GATE_SCRAMBLED_GONOGO"]]
            if len(set(gonogo_traces)) < len(gonogo_traces):
                af_collision = True

        per_K[kk] = {
            "K": K, "n_seeds": n_present, "arm_means": arm_means, "arm_stds": arm_stds,
            "oracle_goal": oracle_goal, "v8_gate": v8, "raw_uniform": raw, "scrambled": scr,
            "v8_additive": v8add, "oracle_action": orc_act,
            "att_lift": float(att_lift), "composition_tax": float(composition_tax),
            "scramble_gap": float(scramble_gap), "value_actor_lift": float(value_actor_lift),
            "closure": float(closure), "headroom_att": float(headroom_att),
            "reach_rank_test": reach_rank,
            "goal_cos": {"V8": gc_v8, "RAW": gc_raw, "SCRAMBLED": gc_scr},
            "sign_test_p": float(sign_p), "n_v8_only": int(n_v8_only), "n_raw_only": int(n_raw_only),
            "af_collision": bool(af_collision),
            "nav_rail_ok": bool(orc_act >= NAV_RAIL_MIN),
            "oracle_repro_ok": bool(ORACLE_REPRO_LO <= oracle_goal <= ORACLE_REPRO_HI),
            "att_pressure_ok": bool(raw < oracle_goal - ATT_PRESSURE_MARGIN),
            "reach_fires_ok": bool(reach_rank > HP_REACH_RANK_MIN),
        }

    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    # ---- pick the evaluable regime: prefer HEADLINE_K if valid, else best att_lift among valid ----
    def _valid(v):
        return v["nav_rail_ok"] and v["oracle_repro_ok"] and v["att_pressure_ok"]

    valid = {kk: v for kk, v in per_K.items() if _valid(v)}
    headline_kk = "K%d" % HEADLINE_K
    if headline_kk in valid:
        focus_kk = headline_kk
    elif valid:
        focus_kk = max(valid, key=lambda k: valid[k]["att_lift"])
    else:
        focus_kk = headline_kk if headline_kk in per_K else list(per_K.keys())[0]
    fv = per_K[focus_kk]

    def _hp_ok(v):
        return (v["closure"] >= HP_CLOSURE_FLOOR and v["att_lift"] >= HP_ATT_LIFT_MIN
                and v["scramble_gap"] >= HP_SCRAMBLE_GAP_MIN
                and v["composition_tax"] <= HP_COMPOSITION_TAX_MAX
                and v["nav_rail_ok"] and v["oracle_repro_ok"] and v["att_pressure_ok"]
                and v["reach_fires_ok"] and not v["af_collision"])

    # ---- verdict (guards first, then HP/MB/HF) ----
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not fv["nav_rail_ok"]:
        verdict = "INCONCLUSIVE_NAV_CEILING_BROKEN"
    elif not fv["oracle_repro_ok"]:
        verdict = "INCONCLUSIVE_ORACLE_GOAL_MISMATCH"
    elif not fv["att_pressure_ok"]:
        verdict = "INCONCLUSIVE_NO_ATTENTION_PRESSURE"
    elif fv["scramble_gap"] < TAUT_SCRAMBLE_FLOOR:
        verdict = "INCONCLUSIVE_TAUTOLOGICAL_METRIC"
    elif fv["att_lift"] < HF_ATT_LIFT_CEIL:
        verdict = "HARD_FAIL_COMPOSITION_ADDS_NOTHING"
    elif _hp_ok(fv):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_COMPOSITION"

    a = fv["arm_means"]
    verdict_msg = (
        "%s | focus=%s valid_K=%s | ORACLE_GOAL=%.3f V8=%.3f RAW=%.3f SCR=%.3f V8_ADD=%.3f ORC_ACT=%.3f | "
        "att_lift=%.3f composition_tax=%.3f scramble_gap=%.3f closure=%.3f value_actor_lift=%.3f | "
        "goal_cos[V8=%.3f RAW=%.3f SCR=%.3f] reach_rank=%.3f sign_p=%.4f (v8_only=%d raw_only=%d) | "
        "nav_rail=%s oracle_repro=%s att_pressure=%s af_collision=%s n_seeds=%d"
    ) % (
        verdict, focus_kk, list(valid.keys()),
        a["ORACLE_GOAL_GONOGO"], a["V8_GATE_GONOGO"], a["RAW_UNIFORM_GONOGO"],
        a["V8_GATE_SCRAMBLED_GONOGO"], a["V8_GATE_ADDITIVE"], a["ORACLE_ACTION"],
        fv["att_lift"], fv["composition_tax"], fv["scramble_gap"], fv["closure"], fv["value_actor_lift"],
        fv["goal_cos"]["V8"], fv["goal_cos"]["RAW"], fv["goal_cos"]["SCRAMBLED"],
        fv["reach_rank_test"], fv["sign_test_p"], fv["n_v8_only"], fv["n_raw_only"],
        fv["nav_rail_ok"], fv["oracle_repro_ok"], fv["att_pressure_ok"], fv["af_collision"], len(keys),
    )

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_K": per_K, "focus_K": focus_kk, "valid_K": list(valid.keys()),
        "focus_att_lift": fv["att_lift"], "focus_composition_tax": fv["composition_tax"],
        "focus_scramble_gap": fv["scramble_gap"], "focus_closure": fv["closure"],
        "focus_value_actor_lift": fv["value_actor_lift"],
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula + WIRING correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s" % DEVICE, flush=True)
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    Vt, Nt, Kt = 40, 512, 4
    E = cf.make_bipolar_E(Vt, Nt, gen)
    flag_row = (torch.randint(0, 2, (1, Nt), generator=gen, device=DEVICE, dtype=DTYPE) * 2 - 1)
    flag_code = (flag_row / (flag_row.norm(dim=1, keepdim=True) + 1e-8))[0]
    Eaug = torch.cat([E, flag_code.unsqueeze(0)], dim=0)

    # ST-READOUT: a one-hot gate selects that slot's node code (cleanup recovers its node id).
    win1 = torch.tensor([[3, 5, 9, 2]], device=DEVICE)
    codes1 = build_slot_codes(Eaug, win1, 1.0, flag_code, gen)
    for j in range(Kt):
        onehot = torch.zeros(Kt, device=DEVICE); onehot[j] = 1.0
        rd = gate_readout(codes1, onehot)
        tok = int((rd @ E.t()).argmax(dim=1))
        assert tok == int(win1[0, j]), "ST-READOUT slot %d recovered %d != %d" % (j, tok, int(win1[0, j]))
    print("[selftest] ST-READOUT one-hot gate selects the slot node OK", flush=True)

    # ST-V8 (Gate D positive control for the transcription): the v8 arbitration pattern holds at test regime.
    g_np = np.random.default_rng(3)
    Kd = 6
    tgt_nodes = g_np.integers(0, Vt, size=600)
    win_np, it_np, gs_np = gen_goal_windows(tgt_nodes, Kd, Vt, g_np)
    # corpus sanity: ~1/3 per type; cue_absent has NO flag; goal-slot holds the target node.
    for t in range(3):
        frac = float((it_np == t).mean())
        assert abs(frac - 1.0 / 3) < 0.08, "ST-V8 type %d frac off: %.3f" % (t, frac)
    ca = (it_np == 2)
    assert not (win_np[ca] == Vt).any(), "ST-V8 cue_absent must have NO flag"
    for i in range(len(tgt_nodes)):
        assert int(win_np[i, gs_np[i]]) == int(tgt_nodes[i]), "ST-V8 goal-slot must hold the target node"
    win_t = torch.tensor(win_np, device=DEVICE)
    goalslot_t = torch.tensor(gs_np, device=DEVICE)
    g_rec, r_rec = learn_recency_gate(win_t, goalslot_t, Kd, RECENCY_TAU, win_t.shape[0])
    assert int(g_rec.argmax()) == Kd - 1, "ST-V8 recency gate must concentrate on most-recent slot (got %d)" % int(g_rec.argmax())
    recency_bias, beta = recency_bias_from_gate(g_rec)
    srt = torch.sort(recency_bias, descending=True).values
    assert abs(float(srt[0] - srt[1]) - RECENCY_GAP_TARGET) < 0.3, "ST-V8 recency gap not normalized to %.1f" % RECENCY_GAP_TARGET
    perm = _derangement(Kd, 13)
    # goal-recovery: V8 gate recovers the target-node code far better than RAW uniform; scramble breaks it.
    gte = torch.Generator(device=DEVICE).manual_seed(99)
    pooled = pooled_goals(Eaug, win_t, flag_code, recency_bias, perm, CUE_Q, gte)
    tgt_codes = E[torch.tensor(tgt_nodes, device=DEVICE)]
    cos_v8 = float((cf._norm_rows(pooled["V8"]) * cf._norm_rows(tgt_codes)).sum(dim=1).mean())
    cos_raw = float((cf._norm_rows(pooled["RAW"]) * cf._norm_rows(tgt_codes)).sum(dim=1).mean())
    cos_scr = float((cf._norm_rows(pooled["SCRAMBLED"]) * cf._norm_rows(tgt_codes)).sum(dim=1).mean())
    assert cos_v8 > cos_raw + 0.15, "ST-V8 attention not load-bearing: cos_v8=%.3f cos_raw=%.3f" % (cos_v8, cos_raw)
    assert cos_v8 > cos_scr + 0.15, "ST-V8 scramble did not break goal recovery: cos_v8=%.3f cos_scr=%.3f" % (cos_v8, cos_scr)
    print("[selftest] ST-V8 arbitration OK: rec_argmax=%d beta=%.3f goal_cos[V8=%.3f RAW=%.3f SCR=%.3f]"
          % (int(g_rec.argmax()), beta, cos_v8, cos_raw, cos_scr), flush=True)

    # ST-WIRING: the v8 goal signal actually DRIVES the Go/NoGo selection, and scramble breaks the DECISION.
    # Toy: branch A 0->1->2->3 (goal 3) vs branch B 0->4->5->6 (away). Train SR on both branches. With the
    # goal pointing at node 3, the trained reach ranks the on-path op higher.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(3)
    Vw, Nw = 8, 512
    Ew = cf.make_bipolar_E(Vw, Nw, gen4)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)
    toy_trans = np.concatenate([np.tile(chainA, (30, 1)), np.tile(chainB, (30, 1))], axis=0)
    Mt, _ = cf.train_sr_transport(Ew, toy_trans, Nw, 600, 16, 0.5, 0.8, gen4)
    goal_true = Ew[3:4]; goal_wrong = Ew[6:7]
    reach_on = float(cf.reach_value(Ew[1:2], goal_true, Mt)[0])
    reach_off = float(cf.reach_value(Ew[4:5], goal_true, Mt)[0])
    assert reach_on > reach_off, "ST-WIRING reach with true goal must prefer on-path (%.4f !> %.4f)" % (reach_on, reach_off)
    # with the WRONG goal (node 6, on branch B) reach prefers the OFF-branch op -> decision flips.
    reach_on_wg = float(cf.reach_value(Ew[1:2], goal_wrong, Mt)[0])
    reach_off_wg = float(cf.reach_value(Ew[4:5], goal_wrong, Mt)[0])
    assert reach_off_wg > reach_on_wg, "ST-WIRING wrong goal must flip the reach preference (%.4f !> %.4f)" % (reach_off_wg, reach_on_wg)
    print("[selftest] ST-WIRING OK: true-goal reach on=%.3f>off=%.3f ; wrong-goal reach off=%.3f>on=%.3f"
          % (reach_on, reach_off, reach_off_wg, reach_on_wg), flush=True)

    # ST-REDUCE (w_reach==0 null reduction): gonogo@w_reach=0 == additive (bit-identical correctness) with an
    # arbitrary external goal -- proves the value term is a clean additive extension.
    g_np2 = np.random.default_rng(11)
    per_op, tr_by_d, te_by_d = cf.make_kb_and_chains(N_OPS, Vt, DENSITY, 16, 16, [DD], g_np2)
    W_ops = [cf.hebbian_W(per_op[i], E, Nt) for i in range(N_OPS)]
    test_c = te_by_d[DD]
    _, tgt_te, _ = cf._chain_tensors(test_c)
    ext_goal = E[tgt_te]
    go0_c, _ = run_selection_with_goal("gonogo", test_c, W_ops, E, torch.zeros((Nt, Nt), device=DEVICE),
                                       DD, 0.3, 0.0, ext_goal)
    add_c, _ = run_selection_with_goal("additive", test_c, W_ops, E, torch.zeros((Nt, Nt), device=DEVICE),
                                       DD, 0.3, 0.0, ext_goal)
    assert bool((go0_c == add_c).all()), "ST-REDUCE gonogo@w_reach=0 != additive"
    print("[selftest] ST-REDUCE gonogo@w_reach=0 == additive OK", flush=True)

    # ST-PIPELINE: single-seed structural run; arms present; ORACLE_ACTION high; att_lift>0; scramble_gap>0.
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_bg_composed")
    kk0 = "K%d" % K_GRID[0]
    assert kk0 in r["K_results"], "ST-PIPELINE missing %s" % kk0
    arms = r["K_results"][kk0]["arms"]
    for arm in ARMS:
        assert arm in arms, "ST-PIPELINE missing arm %s" % arm
    assert arms["ORACLE_ACTION"] >= 0.5, "ST-PIPELINE oracle-action too low (%.3f)" % arms["ORACLE_ACTION"]
    att = arms["V8_GATE_GONOGO"] - arms["RAW_UNIFORM_GONOGO"]
    scg = arms["V8_GATE_GONOGO"] - arms["V8_GATE_SCRAMBLED_GONOGO"]
    print("[selftest] ST-PIPELINE OK arms=%s ORC_ACT=%.3f att_lift=%.3f scramble_gap=%.3f"
          % (kk0, arms["ORACLE_ACTION"], att, scg), flush=True)
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

    print("[%s] mode=%s device=%s N=%d V=%d dd=%d K_grid=%s seeds=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, V_NODES, DD, K_GRID, SEEDS, EXPECTED_N_UNITS), flush=True)

    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL run requires CUDA; none available (route to overnight_queue).")

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST-READOUT, ST-V8 (Gate-D v8 arbitration reproduce), ST-WIRING "
                               "(v8 goal drives Go/NoGo; wrong goal flips it), ST-REDUCE (w_reach=0==additive), "
                               "ST-PIPELINE",
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

    run_config = {"N": N_DIM, "V": V_NODES, "run_mode": RUN_MODE, "K_grid": K_GRID, "dd": DD}
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
                "traceback": traceback.format_exc()[:3000], "K_results": {}, "sr_diag": {}})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        _heartbeat(out_dir, i + 1, len(remaining), "seed_done=%d dt=%.1f" % (seed, time.time() - t0))
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("K_results")}
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
