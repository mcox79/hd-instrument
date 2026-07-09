"""pfc_gate_waypoint_rescue_replay_bidirectional_v1 -- REVIVE the autonomous-waypoint deep-corner
HARD_FAIL with a BRAIN-FIRST, INFORMATIONALLY-INDEPENDENT correction: replay-generate-then-select.

WHY (Director steer 2026-07-08; brain-first drill
notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md):
  Two ML-precedented single-channel fixes ALREADY FAILED on this exact regime (coarse-to-fine +
  verify-gate), each returning ~zero lift over the already-failed open bisection:
    MEASURED@data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json:per_regime
      op4_V1200_d8 flat=0.081 oracle_exec=0.918 hier_oracle=0.906 wp_bisect_open=0.097
      wp_bisect_verify=0.096 -> recovery_verify=0.0182 (verdict HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL)
      op4_V1200_d4 wp_bisect_verify=0.823 -> recovery_verify=0.7029 (shallow already solved).
  The brain-first drill's HEADLINE diagnosis: both failed fixes share ONE structural property the
  brain's error-bounding mechanisms lack -- they correct a noisy estimate using MORE OF THE SAME noisy
  estimate (verify checks a candidate against the same SR-derived R that produced it; coarse-to-fine
  re-derives from the same M/R at a different gamma). Every brain mechanism that actually caps drift
  (grid-cell boundary reset, redundant grid modules, bidirectional hippocampal replay) draws its
  correcting signal from a source INFORMATIONALLY INDEPENDENT of the accumulator. CITED@Pfeiffer-Foster
  2013 (full-path composition pre-commitment); CITED@Foster-Wilson 2006 (reverse replay); CITED@Ross-
  Bagnell 2010 (O(T^2) compounding). This is a REVIVAL of a CONFIRMED-genuine negative with a
  structurally-distinct, brain-precedented mechanism -- NOT a re-run of a self-referential fix.

MECHANISM UNDER TEST (additive to both ancestors; NOT assumed to work; P_deflated ~0.25-0.30 any real
lift over verify, ~0.15-0.20 full HARD-PASS, per the drill's sobering two-prior-failures update):
  REPLAY-GENERATE-THEN-SELECT (bidirectional full-candidate scoring), rank-1 in the drill:
  (1) GENERATE n_cand COMPLETE candidate trajectories (never a greedy per-hop commit). Candidate 0 =
      the unperturbed open bisection (so the open pick is always in the pool -> selection can only help
      or match, never harm, modulo the scorer). Candidates 1..n_cand-1 = the SAME open bisection with
      independently-perturbed argmax tie-breaks (gaussian noise scaled by per-row balance std; cheap,
      NO retrain). At deep corners the balance signal is flat/noisy (WHY open fails) so perturbation
      yields genuinely diverse whole candidates; at shallow corners the signal is peaked so candidates
      converge to the good pick (replay must NOT harm shallow).
  (2) TRAIN a REVERSE SR: M_rev / R_rev via train_sr_transport on the SAME transitions with cur/nxt
      COLUMNS SWAPPED (reverse dynamics). R_rev[a,b] = reach a->b under reverse dynamics = "b typically
      precedes a" forward -- an INFORMATIONALLY-INDEPENDENT second channel (a separate learned operator,
      reverse-direction), NOT a re-check of the forward R against itself.
  (3) SCORE each COMPLETE candidate by FORWARD-vs-REVERSE AGREEMENT: harmonic mean of the mean forward
      leg reach (start->...->goal over R_fwd) and the mean reverse leg reach (goal->...->start over
      R_rev), each cosine mapped to [0,1]. Harmonic mean penalizes candidates where the two independent
      directions DISAGREE (a parity/consistency check across independent channels).
  (4) COMMIT the single best-scoring WHOLE candidate. Execution loop run_hier_arm_wp is IDENTICAL to
      both ancestors for EVERY arm -- the waypoint SOURCE is the only thing that differs.

  Optional rank-1+rank-3 combined arm (wp_replay_generate_select over chunked, k>1-hop segments) is
  DEFERRED to a follow-up per the drill ("only if smoke shows the replay arm alone clears MIDDLE-band").

ARMS (11; paired -- share E, W_ops, M, M_long, M_rev, R_short, R_long, R_rev and the SAME test chains
per (regime,seed)):
  flat_gonogo            FLAT SR Go/NoGo toward the FINAL goal (the collapse; FLOOR)
  oracle_exec            true op_seq perfect execution (ceiling / rail)
  hier_oracle            hierarchical with ORACLE waypoints (given-decomposition CEILING)
  hier_shuffled          hier with WRONG (other-chain) oracle waypoints (neg control)
  wp_bisect_open         PARENT autonomous baseline (the FAILING sequential bisection)
  wp_bisect_verify       ALREADY-FAILED SELF-REFERENTIAL control (THE KEY COMPARATOR / the bar)
  wp_bisect_coarse2fine  ALREADY-FAILED self-referential control (re-run for paired continuity)
  wp_bisect_combo        ALREADY-FAILED self-referential control (re-run for paired continuity)
  wp_replay_generate_select  NEW brain-first independent-signal mechanism (rank 1; under test)  <-- new
  wp_random_state        autonomous FLOOR: uniform random codebook waypoints
  wp_index_midpoint      STRUCTURAL-ARTIFACT GUARD: index-interpolated waypoints

DISCRIMINATORS (per regime; FOCUS = op4_V1200_d8, chain_steps=3; best_rescue = wp_replay_generate_select
FIXED, NOT a max-over-arms):
  headroom_exec        = oracle_exec - flat ; headroom_decomp = hier_oracle - flat
  recovery_ratio(a)    = (a - flat) / headroom_decomp   (frac of ORACLE-decomp benefit recovered)
  delta_recovery       = recovery(replay) - recovery(wp_bisect_verify)   <-- KEY (drill kill-test:
                         vs the already-failed SELF-REFERENTIAL control, NOT vs open)
  flatness_ratio       = recovery(replay, FOCUS chain_steps=3) / recovery(replay, op4_V*_d4 chain_steps=1)
                         (direct operationalization of "stays flat vs hop-depth where baseline decays")
  bidirectional_agreement = mean score_bidirectional of the SELECTED candidate vs mean over all n_cand
                         (reported REGARDLESS: high agreement + no recovery lift is itself informative --
                         bidirectional agreement possible but not predictive of correctness at depth)
  autonomous_closure, lift_flat, lift_random, lift_open (of replay); index_artifact_gap;
  anti_tautology_corr; degenerate_rate; sign_test_p (paired replay vs wp_bisect_verify); cv(replay) (FULL).

HARD_PASS (locked per drill (c); best_rescue=replay at FOCUS -- independent-signal hypothesis confirmed):
  recovery(replay) >= 0.20 AND delta_recovery >= 0.15 AND flatness_ratio >= 0.5 AND lift_flat > 0.05 AND
  lift_random > 0.10 AND index_artifact_gap < 0.05 AND anti_tautology_corr < 0.85 AND degenerate_rate <
  0.10 AND sign_p(replay vs wp_bisect_verify) < 0.05 AND cv(replay) < 0.15 (FULL only) AND oracle_exec
  >= 0.90 AND headroom gates.
  => the compounding-error bound was an artifact of SELF-REFERENTIAL correction specifically; a brain-
     first informationally-independent (bidirectional) signal recovers real autonomous-decomposition
     capability where two ML-precedented single-channel fixes could not.
HARD_FAIL (locked -- the bound survives even independent-signal correction, doubly confirmed structural):
  delta_recovery <= 0.05  (i.e. recovery(replay) <= recovery_verify + 0.05, ~0.068 at FOCUS: no material
  lift over the already-failed self-referential control despite an independent, brain-precedented signal)
  OR flatness_ratio < 0.2  (still an accelerating, not bounded, collapse).
  => strongest honest stopping point: the bound is insensitive to WHETHER the correction is self-
     referential or genuinely independent -> accept as fundamental for this domain/training-budget;
     redirect replay/cerebellar build effort to the GENERAL reasoning loop, keep deployment chains SHORT.
MIDDLE_BAND: delta_recovery in [0.05, 0.15) (real but partial), OR flatness_ratio in [0.2, 0.5), OR any
  honesty guard fails while accuracy margins pass, OR delta>=0.15 & flatness>=0.5 but recovery<0.20.
INCONCLUSIVE: no discriminating regime, OR index_artifact_gap > 0.10 with sign_p(index vs random) < 0.05.
Reported REGARDLESS: full grid for every arm; recovery(open/verify/replay) per regime; delta_recovery;
  flatness_ratio; bidirectional_agreement; sign_p; positive-control reproduce-check of wp_bisect_open/
  verify/flat/hier_oracle vs the ancestor (same E/M/R/seeds by construction).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): replay trace vs wp_bisect_verify/open/flat/random op-trace
#   hash per seed AND hier_oracle vs hier_shuffled (exempt only if bit-identical).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
# - except SystemExit: raise BEFORE except Exception (no BaseException in main).
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor; reachability by
#   feasibility (ancestor hier_oracle=0.906 at op4_d8 proves the given-decomposition envelope; open+
#   verify collapse to ~flat -> the open question is how much of the 0.906 headroom the INDEPENDENT-
#   signal replay recovers; HP bar recovery>=0.20 AND flatness>=0.5 sit inside that envelope).
# - baseline_in_band (AG): the KEY baseline is wp_bisect_verify (the already-failed self-referential
#   control), collapsed to ~flat at FOCUS (0.096 vs flat 0.081); discriminator = replay-vs-verify,
#   both measurable; oracle_exec>=0.90 rail + headroom>=0.10 gates ensure room to recover.
# - discriminator survives scale: smoke holds op4 x {d4,d6,d8} at V=300; smoke reach at N=2048 is
#   BLUNTER than FULL N=8192, so a POSITIVE replay-minus-verify lift at smoke is a LOWER bound on FULL
#   (option C directional preview). Smoke that shows open+verify collapse + oracle success + any
#   positive replay-minus-verify + replay trace differs gates the GPU FULL.
# - HARD_PASS strictly above floor: recovery>=0.20 + delta>=0.15 + flatness>=0.5 (META_RULE_L).
# - HP_SCOPE: HP gates apply to replay vs wp_bisect_verify at FOCUS; oracle_rail(>=0.90) to oracle_exec;
#   recovery references hier_oracle; index guard to wp_index vs wp_random.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(11) * n_seeds * n_regimes.
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash).
# - calibration_check: adaptive_with_discriminator_gate (verify-gate tau = 70th-pctl of R off-diag;
#   replay perturbation = PERTURB_FRAC * per-row balance std, principled + n_cand fixed; discriminator =
#   delta-over-verify + flatness, not tuned-for-PASS).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.

Compute architecture: (a) batched-GPU. SR-TD training (M @ 0.85, M_long @ 0.95, M_rev @ 0.85 on
reversed transitions), operator application, cleanup, reach, R build, bisection + perturbed candidate
generation + bidirectional scoring = batched matmuls / gathers / argmax on cuda-if-available. Chains
batched; within-chain hops sequential (genuine dependency). M/M_long/M_rev/R_* computed once per
(V,n_ops) group and shared across depths. Storage strategy: sharded (each operator its own W matrix;
M/M_long/M_rev learned operators; R_* derived reach matrices). No bundled store. FULL strongly prefers
overnight_queue (GPU). Extra cost vs coarse2fine ancestor: one 3rd SR train (M_rev, same cost class as
M/M_long) + n_cand=5 cheap re-bisections (reuse argmax machinery) + one vectorized scoring pass; linear
in n_cand, no quadratic blowup.
progress_logging: print_flush_true (flush=True on every progress line + per (seed,V,n_ops) heartbeat;
FULL timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1.py (and its
ancestors exp_pfc_gate_autonomous_waypoint_discovery_v1.py / _branching_depth_entropy_grid_v1.py):
make_bipolar_E, hebbian_W, cleanup_batched, make_kb_and_chains, build_adjacency,
collect_rollout_transitions, train_sr_transport, reach_value, build_reach_matrix, codebook_selfcos,
offdiag_quantile, _discover_bisect_boundaries, _pick_balanced_verify, _discover_verify_boundaries,
_discover_coarse2fine_boundaries, _discover_random_boundaries, _discover_index_boundaries,
_boundaries_to_hops, oracle_trajectory_idx, build_waypoint_idx, _chain_tensors, run_selection_arm,
run_oracle_arm, run_hier_arm_wp, discovery_diagnostics, reach_rank_acc, binom/spearman/rankdata, the
alpha/w_reach tuners, and the defensive start-marker / crash-diag / heartbeat / atomic-write scaffolding.
NEW (additive): _discover_bisect_perturbed, generate_candidates, score_bidirectional,
wp_replay_generate_select, wp_hops_replay, the replay arm + the replay-vs-verify + flatness verdict.
"""

import os
import sys
import argparse
import hashlib
import json
import math
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "pfc_gate_waypoint_rescue_replay_bidirectional_v1"
PARENT_ANCHOR = "pfc_gate_waypoint_rescue_coarse2fine_verify_v1"

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

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DTYPE = torch.float32

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
# KEY comparator is wp_bisect_verify (the already-failed SELF-REFERENTIAL control), NOT open.
HP_RECOVERY_RATIO_FLOOR = 0.20    # replay recovers >= 20% of the oracle-DECOMPOSITION benefit
HP_DELTA_RECOVERY_MIN = 0.15      # recovery(replay) - recovery(wp_bisect_verify) >= 0.15 (decisive)
HP_FLATNESS_MIN = 0.50            # recovery(replay,FOCUS d8)/recovery(replay,d4) >= 0.5 (stays flat)
HP_LIFT_FLAT_MIN = 0.05           # real lift over no-hierarchy flat
HP_LIFT_RANDOM_MIN = 0.10         # real lift over a noise waypoint
HP_INDEX_GAP_MAX = 0.05           # no structural index-order leak
HP_ANTI_TAUT_CORR_MAX = 0.85      # balance score is dynamics, not target-cosine in disguise
HP_DEGENERATE_MAX = 0.10          # bisection does not degenerate to picking start/goal
HP_SIGN_TEST_P = 0.05             # paired replay vs wp_bisect_verify significant
HP_CV_MAX = 0.15                  # cross-seed cv on replay at focus (FULL only; loosened doc'd)
HF_DELTA_RECOVERY_CEIL = 0.05     # HARD_FAIL: recovery(replay) <= recovery_verify + 0.05 (no lift)
HF_FLATNESS_CEIL = 0.20           # HARD_FAIL: flatness_ratio < 0.2 (accelerating collapse)
MIDDLE_DELTA_MIN = 0.05           # MIDDLE lower edge (real partial lift over verify)
INDEX_LEAK_GAP = 0.10             # INCONCLUSIVE: index beats random by > this ...
INDEX_LEAK_P = 0.05               # ... with paired sign p < this
ORACLE_RAIL_MIN = 0.90            # FOCUS: perfect-execution ceiling must be reachable
HEADROOM_EXEC_MIN = 0.10          # FOCUS: flat->perfect gap measurable
HEADROOM_DECOMP_MIN = 0.10        # FOCUS: oracle-decomposition benefit measurable (room to recover)
N_CAND = 5                        # replay: number of complete candidate trajectories generated
PERTURB_FRAC = 0.60               # replay: gaussian tie-break noise = this * per-row balance std
BIDIR_EPS = 1e-6                  # harmonic-mean denominator epsilon

DENSITY = 0.21                     # n_train_triples_per_op / V (matches parent)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2

GAMMA_SHORT = 0.85                 # parent's fixed SR gamma (effective horizon 1/(1-g)=6.67 hops)
GAMMA_LONG = 0.95                  # coarse-pick long-horizon SR (effective horizon ~20 hops)
SPAN_LONG_THRESH = 5               # use GAMMA_LONG when a pick spans > this many hops
VERIFY_TAU_PCTL = 0.70             # verify-gate threshold = this percentile of R off-diagonal
MAX_VERIFY_RETRY = 5               # verify-gate retries before random fallback
GAMMA = GAMMA_SHORT                # alias (reach_rank / diagnostics use the short SR)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]
SEG_LEN = 2                        # hierarchical segment length (per-decision reach horizon cap)
NEG_HARD = -1.0e9                  # exclude start/goal/already-chosen from bisection argmax
NEG_SOFT = -1.0e4                  # (unused here; retained for parity with parent primitive shapes)

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, dd). SR M + M_long + R trained/built once per (V,n_ops) group and shared
# across depths. SMOKE = op4 x {d4,d6,d8} at V=300 (open works at d4, collapses at d6/d8 -> fires the
# rescue discriminator; deepest corner op4_d8 included as directional preview at BLUNTER N=2048 reach).
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    REGIMES = [{"n_ops": 4, "V": 40, "dd": 4}, {"n_ops": 4, "V": 40, "dd": 8}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # multi-seed (3). op4 x {d4,d6,d8}. d4 = open already works (rescue must NOT harm); d6/d8 = the
    # collapse corners (rescue must lift over open). Blunter N=2048 reach = lower bound on FULL.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    REGIMES = [{"n_ops": 4, "V": 300, "dd": 4},
               {"n_ops": 4, "V": 300, "dd": 6},
               {"n_ops": 4, "V": 300, "dd": 8}]   # FOCUS: deepest corner (chain_steps=3)
    N_TRAIN_CHAINS = 48
    N_TEST_CHAINS = 48
    SR_STEPS = 2500        # trained-enough SR so reach fires the discovery discriminator at smoke
    SR_BATCH = 64          # scale (reach_rank d4~0.38 usable, d8~0.27 collapsed -> room to rescue);
    SR_LR = 0.5            # blunter than FULL N=8192 (reach_rank d8=0.445) so smoke lift is a lower bound
    ROLLOUT_PER_V = 15
else:  # full
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4},   # easy: open recovers 0.690 (rescue must not harm)
               {"n_ops": 4, "V": 1200, "dd": 6},   # collapse begins (chain_steps=2)
               {"n_ops": 4, "V": 1200, "dd": 8},   # FOCUS: the exact parent HARD_FAIL corner (steps=3)
               {"n_ops": 3, "V": 1000, "dd": 8},   # frontier
               {"n_ops": 2, "V": 800, "dd": 8}]    # matched-entropy(=8) chain_steps=3 dissociation
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000
SR_STEPS = int(os.environ.get("HDLAB_SR_STEPS", str(SR_STEPS)))
ROLLOUT_PER_V = int(os.environ.get("HDLAB_ROLLOUT_PER_V", str(ROLLOUT_PER_V)))
ROLLOUT_CAP = int(os.environ.get("HDLAB_ROLLOUT_CAP", str(ROLLOUT_CAP)))

ARMS = ["flat_gonogo", "oracle_exec", "hier_oracle", "hier_shuffled",
        "wp_bisect_open", "wp_bisect_coarse2fine", "wp_bisect_verify", "wp_bisect_combo",
        "wp_replay_generate_select", "wp_random_state", "wp_index_midpoint"]
RESCUE_ARM = "wp_replay_generate_select"   # the NEW mechanism under test (fixed, not a max-over-arms)
KEY_COMPARATOR = "wp_bisect_verify"        # the already-failed SELF-REFERENTIAL control (the bar)
N_OPS_SET = sorted(set(r["n_ops"] for r in REGIMES))
DEPTH_SET = sorted(set(r["dd"] for r in REGIMES))


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


def regime_key(n_ops: int, V: int, dd: int) -> str:
    return "op%d_V%d_d%d" % (n_ops, V, dd)


def group_key(n_ops: int, V: int) -> str:
    return "op%d_V%d" % (n_ops, V)


def decision_entropy(n_ops: int, dd: int) -> float:
    return float(math.log2(n_ops) * dd)


def n_boundaries(depth: int, seg_len: int) -> int:
    return (depth + seg_len - 1) // seg_len


def gamma_for_span(span: int) -> float:
    """Long-horizon SR (gamma=0.95, eff horizon ~20) for coarse picks spanning beyond gamma=0.85's
    effective horizon (1/(1-0.85)=6.67 hops); short SR otherwise. THEORETICAL@Sutton TD eff-horizon."""
    return GAMMA_LONG if span > SPAN_LONG_THRESH else GAMMA_SHORT


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,parent=%s,N=%d,n_ops_set=%s,depth_set=%s,seeds=%s,gS=%.2f,gL=%.2f,span_thr=%d,"
    "tau_pctl=%.2f,max_retry=%d,seg_len=%d,regimes=%s,density=%.3f,sr_steps=%d,sr_batch=%d,"
    "rollout_per_V=%d,lr=%.2f,alphas=%s,w_reach=%s,n_train=%d,n_test=%d,mode=%s,device=%s,"
    "expected_n=%d,rescue=%s,keycmp=%s,n_cand=%d,perturb=%.2f,HP_recov>=%.2f,HP_delta>=%.2f,"
    "HP_flat>=%.2f,HF_delta<=%.2f,HF_flat<%.2f,lift_flat>%.2f,lift_rand>%.2f,"
    "idx_gap<%.2f,anti_taut<%.2f,degen<%.2f,sign_p<%.2f,cv<%.2f"
) % (
    ANCHOR_NAME, PARENT_ANCHOR, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA_SHORT, GAMMA_LONG,
    SPAN_LONG_THRESH, VERIFY_TAU_PCTL, MAX_VERIFY_RETRY, SEG_LEN, REGIME_KEYS, DENSITY, SR_STEPS,
    SR_BATCH, ROLLOUT_PER_V, SR_LR, ALPHA_SWEEP, W_REACH_SWEEP, N_TRAIN_CHAINS, N_TEST_CHAINS,
    RUN_MODE, str(DEVICE), EXPECTED_N_UNITS, RESCUE_ARM, KEY_COMPARATOR, N_CAND, PERTURB_FRAC,
    HP_RECOVERY_RATIO_FLOOR, HP_DELTA_RECOVERY_MIN, HP_FLATNESS_MIN,
    HF_DELTA_RECOVERY_CEIL, HF_FLATNESS_CEIL, HP_LIFT_FLAT_MIN, HP_LIFT_RANDOM_MIN, HP_INDEX_GAP_MAX,
    HP_ANTI_TAUT_CORR_MAX, HP_DEGENERATE_MAX, HP_SIGN_TEST_P, HP_CV_MAX,
)

_T0 = time.time()


# ============================================================================
# defensive-error-checking helpers (start marker / crash diag / heartbeat)
# ============================================================================
def _write_start_marker(out_dir: Path) -> None:
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(), "device": str(DEVICE),
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
        "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": round(time.time() - _T0, 1), "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
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
# primitives (torch, batched, device-agnostic) -- reused VERBATIM from parent
# ============================================================================
def _norm_rows(X: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return X / (X.norm(dim=-1, keepdim=True) + eps)


def make_bipolar_E(V: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """[V, n] row-normalized bipolar codebook."""
    X = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE, dtype=DTYPE) * 2 - 1)
    return _norm_rows(X)


def hebbian_W(triples: List[Tuple[int, int]], E: torch.Tensor, n: int) -> torch.Tensor:
    """W = sum_s E[s]^T E[o] / n ; out = state @ W ~= E[o] for matching triple."""
    if not triples:
        return torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    arr = torch.tensor(triples, dtype=torch.long, device=DEVICE)
    S = E[arr[:, 0]]
    O = E[arr[:, 1]]
    return (S.transpose(0, 1) @ O) / float(n)


def cleanup_batched(vecs: torch.Tensor, E: torch.Tensor
                    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """vecs [B, n] -> (idx [B], cleaned E[idx] [B, n], manifold_max_sim [B])."""
    vn = _norm_rows(vecs)
    sims = vn @ E.transpose(0, 1)
    manifold, idx = sims.max(dim=1)
    return idx, E[idx], manifold


# ============================================================================
# KB + chains (exact-length paths; train and test disjoint chain sets) -- VERBATIM
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
    """Random-walk (cur, nxt) transitions over the union multigraph for SR-TD training. VERBATIM."""
    out: List[Tuple[int, int]] = []
    if all(len(a) == 0 for a in adj):
        return np.zeros((0, 2), dtype=np.int64)
    while len(out) < n_transitions:
        cur = int(g.integers(0, V))
        for _ in range(max_len):
            op = int(g.integers(0, n_ops))
            nbrs = adj[op].get(cur)
            if not nbrs:
                break
            nxt = int(nbrs[g.integers(0, len(nbrs))])
            out.append((cur, nxt))
            cur = nxt
            if len(out) >= n_transitions:
                break
    return np.asarray(out, dtype=np.int64)


def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features). VERBATIM."""
    M = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    K = transitions.shape[0]
    diag = {"gamma": float(gamma), "n_transitions": int(K), "n_clamped_steps": 0,
            "err_first": None, "err_last": None, "final_M_norm": 0.0}
    if K < 2:
        return M, diag
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
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            diag["n_clamped_steps"] += 1
        lr_per = base_lr * decay * ratio_c
        dM = (Ecur.transpose(0, 1) @ (error * lr_per.unsqueeze(1))) / float(batch)
        M = M + dM
        e_mean = float(e_norm.mean())
        if step == 0:
            diag["err_first"] = round(e_mean, 6)
        diag["err_last"] = round(e_mean, 6)
    diag["final_M_norm"] = round(float(M.norm()), 4)
    return M, diag


def reach_value(cand_E: torch.Tensor, goal_E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    """cos(E[cand] @ M, E[goal]) per row -- learned-dynamics reach. VERBATIM."""
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


def build_reach_matrix(E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    """R [V,V], R[i,j] == reach_value(E[i], E[j], M) == cos(E[i]@M, E[j]). VERBATIM."""
    Efwd = _norm_rows(E @ M)
    En = _norm_rows(E)
    return Efwd @ En.transpose(0, 1)


def codebook_selfcos(E: torch.Tensor) -> torch.Tensor:
    """C [V,V], C[i,j] == cos(E[i], E[j]) (anti-tautology reference). VERBATIM."""
    En = _norm_rows(E)
    return En @ En.transpose(0, 1)


def offdiag_quantile(R: torch.Tensor, q: float) -> float:
    """q-th quantile of R's off-diagonal entries -- the verify-gate threshold tau. Adaptive but
    principled (candidate must reach as well as a typical state-pair does)."""
    V = R.shape[0]
    mask = ~torch.eye(V, dtype=torch.bool, device=DEVICE)
    vals = R[mask]
    if vals.numel() > 4_000_000:                 # torch.quantile input cap; subsample deterministically
        vals = vals[:: (vals.numel() // 4_000_000) + 1]
    return float(torch.quantile(vals, q))


# ============================================================================
# waypoint DISCOVERY: parent baselines (VERBATIM) + NEW rescue mechanisms
# ============================================================================
def _discover_bisect_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                seg_len: int, depth: int) -> torch.Tensor:
    """PARENT wp_bisect_open baseline: sequential greedy bisection. anchor=prev wp (start first);
    wp = argmax_c min(R[anchor,c], R[c,goal]) excluding start/goal/chosen. The FAILING mechanism.
    Returns boundary_states [n_chains, n_bnd], last column = targets. VERBATIM (cand_mask dropped)."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)         # [n_chains, V], rg[i,c] = R[c, goal_i]
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        ra = R.index_select(0, anchor)                       # [n_chains, V], ra[i,c] = R[anchor_i,c]
        balance = torch.minimum(ra, rg).clone()
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        wp = balance.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def _pick_balanced_verify(anchor: torch.Tensor, goal: torch.Tensor, R: torch.Tensor,
                          tau: float, excl_cols: List[torch.Tensor], use_verify: bool,
                          gen_np: np.random.Generator,
                          stats: Optional[Dict[str, int]]) -> torch.Tensor:
    """Pick wp = argmax_c min(R[anchor,c], R[c,goal]) excluding anchor/goal/excl_cols. If use_verify,
    a candidate must clear R[anchor,c]>=tau AND R[c,goal]>=tau; else exclude it and retry the argmax
    (capped at MAX_VERIFY_RETRY); on total exhaustion, uniform-random valid fallback (logged). Returns
    chosen [n_chains]. Vectorized across chains."""
    nc = anchor.shape[0]
    row = torch.arange(nc, device=DEVICE)
    ra = R.index_select(0, anchor)                          # [nc, V]
    rg = R.index_select(1, goal).transpose(0, 1)            # [nc, V]
    balance = torch.minimum(ra, rg).clone()
    balance[row, anchor] = NEG_HARD
    balance[row, goal] = NEG_HARD
    for c in excl_cols:
        balance[row, c] = NEG_HARD
    if not use_verify:
        wp = balance.argmax(dim=1)
        if stats is not None:
            stats["n_picks"] += nc
        return wp
    passv = (ra >= tau) & (rg >= tau)                       # [nc, V]
    work = balance.clone()
    chosen = torch.full((nc,), -1, dtype=torch.long, device=DEVICE)
    retried = torch.zeros(nc, dtype=torch.long, device=DEVICE)
    for _attempt in range(MAX_VERIFY_RETRY + 1):
        cand = work.argmax(dim=1)
        valid = work[row, cand] > (NEG_HARD * 0.5)          # not fully excluded
        ok = passv[row, cand] & valid & (chosen < 0)
        chosen = torch.where(ok, cand, chosen)
        need = (chosen < 0)
        if not bool(need.any()):
            break
        work[row[need], cand[need]] = NEG_HARD              # exclude this candidate; retry
        retried = retried + need.long()
    unresolved = (chosen < 0)
    n_fallback = int(unresolved.sum())
    if n_fallback > 0:
        V = R.shape[0]
        anc_np = anchor.detach().cpu().numpy()
        goal_np = goal.detach().cpu().numpy()
        excl_np = [c.detach().cpu().numpy() for c in excl_cols]
        for ii in torch.where(unresolved)[0].tolist():
            bad = {int(anc_np[ii]), int(goal_np[ii])}
            for c in excl_np:
                bad.add(int(c[ii]))
            r = int(gen_np.integers(0, V)); tries = 0
            while r in bad and tries < 12:
                r = int(gen_np.integers(0, V)); tries += 1
            chosen[ii] = r
    if stats is not None:
        stats["n_picks"] += nc
        stats["n_retry"] += int((retried > 0).sum())
        stats["n_fallback"] += n_fallback
    return chosen


def _discover_verify_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                tau: float, seg_len: int, depth: int,
                                gen_np: np.random.Generator,
                                stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """RESCUE (b): parent SEQUENTIAL bisection + verify-gate (single gamma=short). Same left-to-right
    anchor-advance as wp_bisect_open, but each pick must clear the verify-gate."""
    n_bnd = n_boundaries(depth, seg_len)
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        wp = _pick_balanced_verify(anchor, targets, R, tau, chosen_cols, True, gen_np, stats)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def _discover_coarse2fine_boundaries(starts: torch.Tensor, targets: torch.Tensor,
                                     R_short: torch.Tensor, R_long: torch.Tensor,
                                     tau_short: float, tau_long: float, seg_len: int, depth: int,
                                     use_verify: bool, gen_np: np.random.Generator,
                                     stats: Optional[Dict[str, int]] = None) -> torch.Tensor:
    """RESCUE (a)+(c) [+ (b) if use_verify]: recursive MIDPOINT-FIRST bisection. Fill the interior
    boundary nearest the midpoint of the current [lo,hi] interval FIRST (both endpoints determined:
    ground-truth at the root), then recurse into each half. Long-horizon SR for spans > SPAN_LONG_THRESH.
    The recursion tree has height ~log(T) so error does not compound through a length-T running anchor."""
    n_bnd = n_boundaries(depth, seg_len)
    n_interior = n_bnd - 1
    interior_pos = [(j + 1) * seg_len for j in range(n_interior)]
    determined: Dict[int, torch.Tensor] = {0: starts.clone(), depth: targets.clone()}
    det_interior_cols: List[torch.Tensor] = []              # already-chosen interior states (exclude)

    def fill(lo: int, hi: int) -> None:
        inside = [p for p in interior_pos if lo < p < hi and p not in determined]
        if not inside:
            return
        mid = 0.5 * (lo + hi)
        p = min(inside, key=lambda x: (abs(x - mid), x))     # midpoint-first, ties -> lower index
        span = hi - lo
        long = span > SPAN_LONG_THRESH
        R = R_long if long else R_short
        tau = tau_long if long else tau_short
        wp = _pick_balanced_verify(determined[lo], determined[hi], R, tau,
                                   det_interior_cols, use_verify, gen_np, stats)
        determined[p] = wp
        det_interior_cols.append(wp)
        fill(lo, p)
        fill(p, hi)

    fill(0, depth)
    cols = [determined[(j + 1) * seg_len] for j in range(n_interior)] + [targets]
    return torch.stack(cols, dim=1)


def _discover_random_boundaries(starts: torch.Tensor, targets: torch.Tensor, V: int,
                                seg_len: int, depth: int, g: np.random.Generator) -> torch.Tensor:
    """Uniform random codebook waypoints; avoid start/goal. TRUE floor. VERBATIM."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    st = starts.detach().cpu().numpy()
    tg = targets.detach().cpu().numpy()
    cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        r = g.integers(0, V, size=n_chains)
        for _try in range(6):
            bad = (r == st) | (r == tg)
            if not bad.any():
                break
            r = np.where(bad, g.integers(0, V, size=n_chains), r)
        cols.append(torch.tensor(r, dtype=torch.long, device=DEVICE))
    cols.append(targets)
    return torch.stack(cols, dim=1)


def _discover_index_boundaries(starts: torch.Tensor, targets: torch.Tensor, V: int,
                               seg_len: int, depth: int) -> torch.Tensor:
    """Structural-artifact guard: interpolate wp by RAW CODEBOOK INDEX. VERBATIM."""
    n_bnd = n_boundaries(depth, seg_len)
    st = starts.to(DTYPE)
    tg = targets.to(DTYPE)
    cols: List[torch.Tensor] = []
    for j in range(n_bnd - 1):
        pos = min((j + 1) * seg_len, depth)
        t = pos / float(depth)
        wp = torch.round(st * (1.0 - t) + tg * t).long().clamp_(0, V - 1)
        coll = (wp == starts) | (wp == targets)
        wp = torch.where(coll, (wp + 1).clamp_(0, V - 1), wp)
        coll2 = (wp == starts) | (wp == targets)
        wp = torch.where(coll2, (wp - 2).clamp_(0, V - 1), wp)
        cols.append(wp)
    cols.append(targets)
    return torch.stack(cols, dim=1)


def _boundaries_to_hops(boundary_states: torch.Tensor, seg_len: int, depth: int) -> torch.Tensor:
    """Map boundary states [n_chains, n_bnd] -> per-hop waypoint schedule [n_chains, depth]. VERBATIM."""
    n_bnd = boundary_states.shape[1]
    hop_to_bnd = [min(h // seg_len, n_bnd - 1) for h in range(depth)]
    idx = torch.tensor(hop_to_bnd, dtype=torch.long, device=DEVICE)
    return boundary_states.index_select(1, idx)


def oracle_trajectory_idx(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int
                          ) -> torch.Tensor:
    """Per-hop cleaned-state INDICES along the true (oracle) trajectory -> [n_chains, depth+1]. VERBATIM."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    traj = torch.empty((n_chains, depth + 1), dtype=torch.long, device=DEVICE)
    traj[:, 0] = starts
    state = E[starts].clone()
    for hop in range(depth):
        ops_h = op_seq_t[:, hop]
        new_idx = torch.empty(n_chains, dtype=torch.long, device=DEVICE)
        for op in range(len(W_ops)):
            mask = (ops_h == op)
            if not bool(mask.any()):
                continue
            out = state[mask] @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            new_idx[mask] = idx
        traj[:, hop + 1] = new_idx
        state = E[new_idx]
    traj[:, depth] = targets
    return traj


def build_waypoint_idx(traj_idx: torch.Tensor, seg_len: int, depth: int, shuffle: bool
                       ) -> torch.Tensor:
    """Oracle/shuffled per-hop waypoint index [n_chains, depth]. VERBATIM."""
    src = torch.roll(traj_idx, shifts=1, dims=0) if shuffle else traj_idx
    wp_hop = [min(((h // seg_len) + 1) * seg_len, depth) for h in range(depth)]
    wp_hop_t = torch.tensor(wp_hop, dtype=torch.long, device=DEVICE)
    return src[:, wp_hop_t]


# ============================================================================
# arms (batched across chains; hops sequential within a chain) -- VERBATIM
# ============================================================================
def _chain_tensors(chains: List[Tuple[int, List[int], int]]
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)
    return starts, targets, op_seqs


def run_selection_arm(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                      M: torch.Tensor, depth: int, alpha: float, w_reach: float
                      ) -> Tuple[np.ndarray, np.ndarray]:
    """FLAT batched op-selection arm toward the FINAL goal every hop. VERBATIM."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * _norm_rows(goal_E)).sum(dim=1)
            if mode == "gonogo":
                reach = reach_value(cleaned, goal_E, M)
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


def run_oracle_arm(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int) -> np.ndarray:
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    final_idx = starts
    for hop in range(depth):
        ops_h = op_seq_t[:, hop]
        new_idx = torch.empty(n_chains, dtype=torch.long, device=DEVICE)
        for op in range(len(W_ops)):
            mask = (ops_h == op)
            if not bool(mask.any()):
                continue
            out = state[mask] @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            new_idx[mask] = idx
        state = E[new_idx]
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool)


def run_hier_arm_wp(chains, W_ops: List[torch.Tensor], E: torch.Tensor, M: torch.Tensor,
                    depth: int, seg_len: int, alpha: float, w_reach: float,
                    wp_idx: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """HIERARCHICAL-OPTIONS execution given an EXTERNAL per-hop waypoint schedule wp_idx. The waypoint
    SOURCE is the ONLY thing that differs across all wp_* / hier_* arms. VERBATIM."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    wp_E_all = E[wp_idx]
    state = E[starts].clone()
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        wp = wp_E_all[:, hop, :]
        wp_n = _norm_rows(wp)
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            out_n = _norm_rows(out)
            goal_sim = (out_n * wp_n).sum(dim=1)
            reach = reach_value(cleaned, wp, M)
            sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach
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
# NEW: replay-generate-then-select (bidirectional full-candidate scoring; rank-1 brain-first)
# ============================================================================
def _discover_bisect_perturbed(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                               seg_len: int, depth: int, tgen: torch.Generator,
                               perturb_frac: float) -> torch.Tensor:
    """ONE complete candidate trajectory = the parent open bisection with gaussian tie-break noise
    added to the balance signal before each argmax (noise sd = perturb_frac * per-row balance std).
    perturb_frac==0 reproduces _discover_bisect_boundaries EXACTLY (candidate 0). start/goal/chosen
    hard-masks are applied AFTER the noise so they can never be selected. Returns [n_chains, n_bnd]."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)          # [n_chains, V], rg[i,c] = R[c, goal_i]
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        ra = R.index_select(0, anchor)                       # [n_chains, V], ra[i,c] = R[anchor_i,c]
        balance = torch.minimum(ra, rg).clone()
        if perturb_frac > 0.0:
            sd = balance.std(dim=1, keepdim=True)            # [n_chains, 1] per-row scale
            noise = torch.randn(balance.shape, generator=tgen, device=DEVICE, dtype=DTYPE)
            balance = balance + (perturb_frac * sd) * noise
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        wp = balance.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)


def generate_candidates(starts: torch.Tensor, targets: torch.Tensor, R_fwd: torch.Tensor,
                        seg_len: int, depth: int, n_cand: int, tgen: torch.Generator,
                        perturb_frac: float) -> torch.Tensor:
    """n_cand COMPLETE candidate boundary trajectories. Candidate 0 = unperturbed open pick (the open
    baseline is always in the pool); candidates 1..n_cand-1 = independently-perturbed argmax tie-breaks.
    Returns [n_cand, n_chains, n_bnd]. No retraining -- reuses the open bisection machinery."""
    cands = [_discover_bisect_perturbed(starts, targets, R_fwd, seg_len, depth, tgen, 0.0)]
    for _ in range(n_cand - 1):
        cands.append(_discover_bisect_perturbed(starts, targets, R_fwd, seg_len, depth, tgen,
                                                perturb_frac))
    return torch.stack(cands, dim=0)


def _to_unit(x: torch.Tensor) -> torch.Tensor:
    """Map cosine reach in [-1,1] to [0,1] so the harmonic mean stays well-defined and positive."""
    return (x + 1.0) * 0.5


def score_bidirectional(boundaries: torch.Tensor, starts: torch.Tensor,
                        R_fwd: torch.Tensor, R_rev: torch.Tensor) -> torch.Tensor:
    """Score a COMPLETE candidate by FORWARD-vs-REVERSE agreement. boundaries [n_chains, n_bnd] with
    last col = goal. The full state sequence is [start] + boundaries. Forward leg reach traverses
    start->...->goal over R_fwd; reverse leg reach traverses goal->...->start over R_rev (the
    INDEPENDENT second channel: R_rev[y,x] high iff x typically precedes y forward). Returns the
    harmonic mean of the mean forward-leg unit-reach and the mean reverse-leg unit-reach [n_chains]."""
    n_chains = boundaries.shape[0]
    seq = torch.cat([starts.view(n_chains, 1), boundaries], dim=1)   # [n_chains, n_bnd+1]
    n_legs = seq.shape[1] - 1
    fwd_acc = torch.zeros(n_chains, dtype=DTYPE, device=DEVICE)
    rev_acc = torch.zeros(n_chains, dtype=DTYPE, device=DEVICE)
    for i in range(n_legs):
        x = seq[:, i]
        y = seq[:, i + 1]
        fwd_acc = fwd_acc + _to_unit(R_fwd[x, y])           # x -> y forward
        rev_acc = rev_acc + _to_unit(R_rev[y, x])           # y -> x under reverse dynamics
    fwd = fwd_acc / float(n_legs)
    rev = rev_acc / float(n_legs)
    return 2.0 * fwd * rev / (fwd + rev + BIDIR_EPS)


def wp_replay_generate_select(starts: torch.Tensor, targets: torch.Tensor, R_fwd: torch.Tensor,
                              R_rev: torch.Tensor, seg_len: int, depth: int, n_cand: int,
                              tgen: torch.Generator, perturb_frac: float
                              ) -> Tuple[torch.Tensor, Dict[str, float]]:
    """GENERATE n_cand complete candidates, SCORE each by bidirectional agreement, COMMIT the best
    WHOLE candidate per chain. Returns (selected_boundaries [n_chains, n_bnd], agreement diagnostics)."""
    cands = generate_candidates(starts, targets, R_fwd, seg_len, depth, n_cand, tgen, perturb_frac)
    n_c, n_chains, n_bnd = cands.shape
    scores = torch.empty((n_c, n_chains), dtype=DTYPE, device=DEVICE)
    for c in range(n_c):
        scores[c] = score_bidirectional(cands[c], starts, R_fwd, R_rev)
    best = scores.argmax(dim=0)                              # [n_chains]
    row = torch.arange(n_chains, device=DEVICE)
    selected = cands[best, row, :]                           # [n_chains, n_bnd]
    sel_score = scores[best, row]
    agree = {
        "mean_selected_score": float(sel_score.mean()),
        "mean_all_cand_score": float(scores.mean()),
        "mean_open_cand_score": float(scores[0].mean()),    # candidate 0 == unperturbed open pick
        "frac_selected_not_open": float((best != 0).float().mean()),
    }
    return selected, agree


# ---- per-arm waypoint hop-schedules (discovery wrappers) ----
def wp_hops_replay(chains, R_fwd, R_rev, depth, tgen, agree_out=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b, agree = wp_replay_generate_select(starts, targets, R_fwd, R_rev, SEG_LEN, depth, N_CAND,
                                         tgen, PERTURB_FRAC)
    if agree_out is not None:
        agree_out.update(agree)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_open(chains, R, depth) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_bisect_boundaries(starts, targets, R, SEG_LEN, depth)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_coarse2fine(chains, R_short, R_long, tau_short, tau_long, depth, use_verify, gen_np,
                        stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_coarse2fine_boundaries(starts, targets, R_short, R_long, tau_short, tau_long,
                                         SEG_LEN, depth, use_verify, gen_np, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_verify(chains, R_short, tau_short, depth, gen_np, stats=None) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_verify_boundaries(starts, targets, R_short, tau_short, SEG_LEN, depth, gen_np, stats)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_random(chains, V, depth, g) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_random_boundaries(starts, targets, V, SEG_LEN, depth, g)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_index(chains, V, depth) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_index_boundaries(starts, targets, V, SEG_LEN, depth)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_oracle(chains, W_ops, E, depth, shuffle) -> torch.Tensor:
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)
    return build_waypoint_idx(traj, SEG_LEN, depth, shuffle=shuffle)


# ---- discovery honesty diagnostics (on the OPEN arm's shared balance signal) -- VERBATIM ----
def discovery_diagnostics(chains, R: torch.Tensor, C: torch.Tensor, depth: int,
                          W_ops, E, seg_len: int) -> Dict[str, float]:
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    rg = R.index_select(1, targets).transpose(0, 1)
    ra0 = R.index_select(0, starts)
    balance0 = torch.minimum(ra0, rg)
    um = balance0.argmax(dim=1)
    degenerate = ((um == starts) | (um == targets)).float().mean().item()
    raw0 = C.index_select(1, targets).transpose(0, 1)
    a = balance0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    b = raw0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    if a.std() < 1e-9 or b.std() < 1e-9:
        anti_taut = 0.0
    else:
        anti_taut = float(np.corrcoef(a, b)[0, 1])
    b_open = _discover_bisect_boundaries(starts, targets, R, seg_len, depth)
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)
    n_bnd = b_open.shape[1]
    matches = 0
    total = 0
    for j in range(n_bnd - 1):
        pos = min((j + 1) * seg_len, depth)
        oracle_bnd = traj[:, pos]
        matches += int((b_open[:, j] == oracle_bnd).sum().item())
        total += n_chains
    exact = float(matches) / float(max(1, total))
    return {"degenerate_rate": degenerate, "anti_tautology_corr": anti_taut,
            "exact_match_rate": exact}


def reach_rank_acc(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                   M: torch.Tensor, depth: int) -> float:
    """P(argmax-reach over the true-next candidates picks the true op at hop 0) -- per-hop reach
    signal quality diagnostic. VERBATIM."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    reach_scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
    cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
    for op in range(n_ops):
        out = state @ W_ops[op]
        idx, cleaned, _ = cleanup_batched(out, E)
        cand_idx_all[:, op] = idx
        reach_scores[:, op] = reach_value(cleaned, goal_E, M)
    picked = reach_scores.argmax(dim=1)
    true_op = op_seq_t[:, 0]
    return float((picked == true_op).float().mean().item())


# ============================================================================
# stats helpers -- VERBATIM
# ============================================================================
def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    if n <= 0:
        return 1.0
    from math import comb
    def pmf(kk):
        return comb(n, kk) * (p ** kk) * ((1 - p) ** (n - kk))
    p_obs = pmf(k)
    tot = 0.0
    for kk in range(n + 1):
        if pmf(kk) <= p_obs + 1e-12:
            tot += pmf(kk)
    return float(min(1.0, tot))


def _rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(x) + 1, dtype=np.float64)
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    csum = np.cumsum(counts)
    start = csum - counts
    avg = (start + csum - 1) / 2.0 + 1.0
    return avg[inv]


def _spearman(x: List[float], y: List[float]) -> float:
    if len(x) < 2:
        return 0.0
    ax = _rankdata(np.asarray(x, dtype=np.float64))
    ay = _rankdata(np.asarray(y, dtype=np.float64))
    if ax.std() < 1e-12 or ay.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(ax, ay)[0, 1])


# ============================================================================
# per-arm w_reach / alpha tuners -- VERBATIM shape
# ============================================================================
def _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd) -> Tuple[float, float]:
    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    best_alpha, best = ALPHA_SWEEP[0], -1.0
    for alpha in ALPHA_SWEEP:
        acc = run_hier_arm_wp(train_c, W_ops, E, M, dd, SEG_LEN, alpha, 1.0, wp_oracle_tr)[0].mean()
        if acc > best:
            best, best_alpha = acc, alpha
    return best_alpha, float(best)


def _tune_wreach_flat(train_c, W_ops, E, M, dd, alpha) -> Tuple[float, float]:
    best_wr, best = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo", train_c, W_ops, E, M, dd, alpha, wr)[0].mean()
        if acc > best:
            best, best_wr = acc, wr
    return best_wr, float(best)


def _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, alpha, wp_idx) -> Tuple[float, float]:
    best_wr, best = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_hier_arm_wp(train_c, W_ops, E, M, dd, SEG_LEN, alpha, wr, wp_idx)[0].mean()
        if acc > best:
            best, best_wr = acc, wr
    return best_wr, float(best)


# ============================================================================
# per-regime eval
# ============================================================================
def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, M_long: torch.Tensor, M_rev: torch.Tensor,
                 R_short: torch.Tensor, R_long: torch.Tensor, R_rev: torch.Tensor,
                 C: torch.Tensor, tau_short: float, tau_long: float,
                 train_by_d, test_by_d, g: np.random.Generator,
                 disc_gen: np.random.Generator, rgen: torch.Generator) -> Dict[str, Any]:
    """Tune on train, evaluate all 11 arms on test (paired). One seed. KEY comparator = verify."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    best_alpha, _ = _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd)

    # train waypoint schedules (discovery uses only start/goal + R; never the oracle trajectory)
    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    wp_shuf_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=True)
    wp_open_tr = wp_hops_open(train_c, R_short, dd)
    wp_c2f_tr = wp_hops_coarse2fine(train_c, R_short, R_long, tau_short, tau_long, dd, False, disc_gen)
    wp_ver_tr = wp_hops_verify(train_c, R_short, tau_short, dd, disc_gen)
    wp_combo_tr = wp_hops_coarse2fine(train_c, R_short, R_long, tau_short, tau_long, dd, True, disc_gen)
    wp_replay_tr = wp_hops_replay(train_c, R_short, R_rev, dd, rgen)

    wr_flat, _ = _tune_wreach_flat(train_c, W_ops, E, M, dd, best_alpha)
    wr_oracle, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_oracle_tr)
    wr_shuf, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_shuf_tr)
    wr_open, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_open_tr)
    wr_c2f, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_c2f_tr)
    wr_ver, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_ver_tr)
    wr_combo, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_combo_tr)
    wr_replay, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_replay_tr)

    # test waypoint schedules (discovery on test start/goal only; capture retry stats + agreement)
    stats_ver = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    stats_combo = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    agree = {}
    wp_oracle_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=False)
    wp_shuf_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=True)
    wp_open_te = wp_hops_open(test_c, R_short, dd)
    wp_c2f_te = wp_hops_coarse2fine(test_c, R_short, R_long, tau_short, tau_long, dd, False, disc_gen)
    wp_ver_te = wp_hops_verify(test_c, R_short, tau_short, dd, disc_gen, stats_ver)
    wp_combo_te = wp_hops_coarse2fine(test_c, R_short, R_long, tau_short, tau_long, dd, True, disc_gen,
                                      stats_combo)
    wp_replay_te = wp_hops_replay(test_c, R_short, R_rev, dd, rgen, agree)
    wp_rand_te = wp_hops_random(test_c, V, dd, g)
    wp_idx_te = wp_hops_index(test_c, V, dd)

    # eval on TEST (paired)
    flat_c, flat_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, wr_flat)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)
    ho_c, ho_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_oracle, wp_oracle_te)
    hs_c, hs_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_shuf, wp_shuf_te)
    op_c, op_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_open_te)
    c2f_c, c2f_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_c2f, wp_c2f_te)
    ver_c, ver_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_ver, wp_ver_te)
    cmb_c, cmb_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_combo, wp_combo_te)
    rp_c, rp_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_replay, wp_replay_te)
    rd_c, rd_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_rand_te)
    ix_c, ix_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_idx_te)

    arms: Dict[str, float] = {
        "flat_gonogo": float(flat_c.mean()), "oracle_exec": float(orc_c.mean()),
        "hier_oracle": float(ho_c.mean()), "hier_shuffled": float(hs_c.mean()),
        "wp_bisect_open": float(op_c.mean()), "wp_bisect_coarse2fine": float(c2f_c.mean()),
        "wp_bisect_verify": float(ver_c.mean()), "wp_bisect_combo": float(cmb_c.mean()),
        "wp_replay_generate_select": float(rp_c.mean()),
        "wp_random_state": float(rd_c.mean()), "wp_index_midpoint": float(ix_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "flat_gonogo": hashlib.sha256(flat_tr.tobytes()).hexdigest()[:16],
        "oracle_exec": "oracle_true_seq",
        "hier_oracle": hashlib.sha256(ho_tr.tobytes()).hexdigest()[:16],
        "hier_shuffled": hashlib.sha256(hs_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_open": hashlib.sha256(op_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_coarse2fine": hashlib.sha256(c2f_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_verify": hashlib.sha256(ver_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_combo": hashlib.sha256(cmb_tr.tobytes()).hexdigest()[:16],
        "wp_replay_generate_select": hashlib.sha256(rp_tr.tobytes()).hexdigest()[:16],
        "wp_random_state": hashlib.sha256(rd_tr.tobytes()).hexdigest()[:16],
        "wp_index_midpoint": hashlib.sha256(ix_tr.tobytes()).hexdigest()[:16],
    }

    diag = discovery_diagnostics(test_c, R_short, C, dd, W_ops, E, SEG_LEN)
    rr_test = reach_rank_acc(test_c, W_ops, E, M, dd)

    # best_rescue = replay (FIXED, the new mechanism); KEY comparator = verify (already-failed control)
    best_rescue_arm = RESCUE_ARM
    best_c = rp_c

    # paired counts: replay vs verify (KEY), vs open, vs flat, vs random; index vs random (per-chain)
    paired = {
        "n_rescue_only_vs_verify": int((best_c & (~ver_c)).sum()),
        "n_verify_only_vs_rescue": int((ver_c & (~best_c)).sum()),
        "n_rescue_only_vs_open": int((best_c & (~op_c)).sum()),
        "n_open_only_vs_rescue": int((op_c & (~best_c)).sum()),
        "n_rescue_only_vs_flat": int((best_c & (~flat_c)).sum()),
        "n_flat_only_vs_rescue": int((flat_c & (~best_c)).sum()),
        "n_rescue_only_vs_rand": int((best_c & (~rd_c)).sum()),
        "n_rand_only_vs_rescue": int((rd_c & (~best_c)).sum()),
        "n_idx_only_vs_rand": int((ix_c & (~rd_c)).sum()),
        "n_rand_only_vs_idx": int((rd_c & (~ix_c)).sum()),
        "n_test": int(len(best_c)),
    }
    rr_combo = (float(stats_combo["n_retry"]) / float(max(1, stats_combo["n_picks"])))
    rr_verify = (float(stats_ver["n_retry"]) / float(max(1, stats_ver["n_picks"])))
    fb_combo = (float(stats_combo["n_fallback"]) / float(max(1, stats_combo["n_picks"])))

    return {
        "n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
        "arms": arms, "op_trace_hashes": op_trace_hashes, "best_rescue_arm": best_rescue_arm,
        "best_alpha": float(best_alpha), "wr_open": float(wr_open), "wr_c2f": float(wr_c2f),
        "wr_ver": float(wr_ver), "wr_combo": float(wr_combo), "wr_replay": float(wr_replay),
        "reach_rank_chance": 1.0 / float(n_ops), "reach_rank_test": float(rr_test),
        "degenerate_rate": float(diag["degenerate_rate"]),
        "anti_tautology_corr": float(diag["anti_tautology_corr"]),
        "exact_match_rate": float(diag["exact_match_rate"]),
        "retry_rate_combo": rr_combo, "retry_rate_verify": rr_verify, "fallback_rate_combo": fb_combo,
        "bidir_mean_selected": float(agree.get("mean_selected_score", 0.0)),
        "bidir_mean_all_cand": float(agree.get("mean_all_cand_score", 0.0)),
        "bidir_mean_open_cand": float(agree.get("mean_open_cand_score", 0.0)),
        "frac_selected_not_open": float(agree.get("frac_selected_not_open", 0.0)),
        "paired": paired,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    disc_gen = np.random.default_rng(seed * 6364136223846793005 % (2 ** 63) + 1442695040888963407 % (2 ** 63))

    by_group: Dict[Tuple[int, int], List[int]] = {}
    for r in REGIMES:
        by_group.setdefault((r["V"], r["n_ops"]), []).append(r["dd"])

    regime_results: Dict[str, Any] = {}
    sr_diag_by_group: Dict[str, Any] = {}
    for (V, n_ops) in sorted(by_group.keys()):
        depths_needed = sorted(set(by_group[(V, n_ops)]))
        tgen = torch.Generator(device=DEVICE)
        tgen.manual_seed(int(seed) * 100003 + int(V) * 31 + int(n_ops))
        E = make_bipolar_E(V, N_DIM, tgen)
        per_op, train_by_d, test_by_d = make_kb_and_chains(
            n_ops, V, DENSITY, N_TRAIN_CHAINS, N_TEST_CHAINS, depths_needed, g)
        W_ops = [hebbian_W(per_op[i], E, N_DIM) for i in range(n_ops)]
        adj = build_adjacency(per_op, n_ops)

        max_len = max(depths_needed) + 2
        transitions = collect_rollout_transitions(adj, n_ops, V, rollout_count(V), max_len, g)

        # M (short, gamma=0.85) trained FIRST with the parent's exact sr_gen seed -> reproduces the
        # parent's M / R / wp_bisect_open / flat / hier_oracle by construction (positive control).
        sr_gen = torch.Generator(device=DEVICE)
        sr_gen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3)
        M, sr_diag = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                        GAMMA_SHORT, sr_gen)
        # M_long (gamma=0.95) trained SECOND with a distinct generator -> does not perturb M.
        sr_gen_long = torch.Generator(device=DEVICE)
        sr_gen_long.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 104729)
        M_long, sr_diag_long = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                                  GAMMA_LONG, sr_gen_long)
        # M_rev (gamma=0.85, REVERSED transitions cur<->nxt) -> INFORMATIONALLY-INDEPENDENT reverse
        # channel for bidirectional replay scoring. Distinct generator -> does not perturb M / M_long.
        sr_gen_rev = torch.Generator(device=DEVICE)
        sr_gen_rev.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 224737)
        transitions_rev = (transitions[:, ::-1].copy() if transitions.shape[0] > 0
                           else transitions)
        M_rev, sr_diag_rev = train_sr_transport(E, transitions_rev, N_DIM, SR_STEPS, SR_BATCH, SR_LR,
                                                GAMMA_SHORT, sr_gen_rev)

        R_short = build_reach_matrix(E, M)
        R_long = build_reach_matrix(E, M_long)
        R_rev = build_reach_matrix(E, M_rev)
        C = codebook_selfcos(E)
        tau_short = offdiag_quantile(R_short, VERIFY_TAU_PCTL)
        tau_long = offdiag_quantile(R_long, VERIFY_TAU_PCTL)

        # replay perturbation generator: deterministic per (seed, V, n_ops); advanced across regimes.
        rgen = torch.Generator(device=DEVICE)
        rgen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + 314159)

        sr_diag["gamma_long_err_first"] = sr_diag_long["err_first"]
        sr_diag["gamma_long_err_last"] = sr_diag_long["err_last"]
        sr_diag["gamma_long_M_norm"] = sr_diag_long["final_M_norm"]
        sr_diag["gamma_rev_err_first"] = sr_diag_rev["err_first"]
        sr_diag["gamma_rev_err_last"] = sr_diag_rev["err_last"]
        sr_diag["gamma_rev_M_norm"] = sr_diag_rev["final_M_norm"]
        sr_diag["tau_short"] = tau_short
        sr_diag["tau_long"] = tau_long
        sr_diag_by_group[group_key(n_ops, V)] = sr_diag

        print("[seed=%d op%d V=%d] SR_short err %s->%s Mn=%.3f | SR_long err %s->%s Mn=%.3f | "
              "SR_rev err %s->%s Mn=%.3f | R_s=%.3f R_l=%.3f R_r=%.3f tau_s=%.3f tau_l=%.3f n_trans=%d"
              % (seed, n_ops, V, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
                 sr_diag_long["err_first"], sr_diag_long["err_last"], sr_diag_long["final_M_norm"],
                 sr_diag_rev["err_first"], sr_diag_rev["err_last"], sr_diag_rev["final_M_norm"],
                 float(R_short.mean()), float(R_long.mean()), float(R_rev.mean()), tau_short, tau_long,
                 sr_diag["n_transitions"]), flush=True)

        for dd in depths_needed:
            rec = _eval_regime(n_ops, V, dd, E, W_ops, M, M_long, M_rev, R_short, R_long, R_rev, C,
                               tau_short, tau_long, train_by_d, test_by_d, g, disc_gen, rgen)
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(n_ops, V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s ent=%.2f] FLAT=%.3f OEXEC=%.3f HORC=%.3f | OPEN=%.3f VER=%.3f "
                  "C2F=%.3f CMB=%.3f REPLAY=%.3f RAND=%.3f IDX=%.3f (a=%.2f rr=%.3f degen=%.3f "
                  "taut=%.3f exact=%.3f bidir_sel=%.3f bidir_all=%.3f fracNotOpen=%.3f best=%s)"
                  % (seed, key, rec["entropy"], a["flat_gonogo"], a["oracle_exec"], a["hier_oracle"],
                     a["wp_bisect_open"], a["wp_bisect_verify"], a["wp_bisect_coarse2fine"],
                     a["wp_bisect_combo"], a["wp_replay_generate_select"], a["wp_random_state"],
                     a["wp_index_midpoint"], rec["best_alpha"], rec["reach_rank_test"],
                     rec["degenerate_rate"], rec["anti_tautology_corr"], rec["exact_match_rate"],
                     rec["bidir_mean_selected"], rec["bidir_mean_all_cand"],
                     rec["frac_selected_not_open"], rec["best_rescue_arm"]), flush=True)

    return {
        "seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "regime_results": regime_results, "sr_diag_by_group": sr_diag_by_group,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def _mean(xs: List[float]) -> float:
    return float(np.mean(xs)) if xs else 0.0


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_regime": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _present(rk):
        return [k for k in keys if rk in per_seed[k].get("regime_results", {})]

    def _arm_col(rk, arm):
        return [float(per_seed[k]["regime_results"][rk]["arms"][arm]) for k in _present(rk)]

    def _field_col(rk, field):
        return [float(per_seed[k]["regime_results"][rk].get(field, 0.0)) for k in _present(rk)]

    per_regime: Dict[str, Any] = {}
    completed_units = 0
    for r in REGIMES:
        rk = regime_key(r["n_ops"], r["V"], r["dd"])
        present = _present(rk)
        n_present = len(present)
        completed_units += n_present * len(ARMS)

        arm_means, arm_cvs = {}, {}
        for arm in ARMS:
            vals = _arm_col(rk, arm)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                arm_means[arm] = m
                arm_cvs[arm] = float(sd / m) if m > 1e-6 else 0.0
            else:
                arm_means[arm] = 0.0; arm_cvs[arm] = 0.0

        flat = arm_means["flat_gonogo"]
        oexec = arm_means["oracle_exec"]
        horc = arm_means["hier_oracle"]
        rand = arm_means["wp_random_state"]
        idxm = arm_means["wp_index_midpoint"]
        open_a = arm_means["wp_bisect_open"]
        verify_a = arm_means["wp_bisect_verify"]        # KEY comparator (already-failed self-ref)

        best_rescue_arm = RESCUE_ARM                     # replay (FIXED, not a max-over-arms)
        best_rescue = arm_means[RESCUE_ARM]

        headroom_exec = oexec - flat
        headroom_decomp = horc - flat
        recovery_open = ((open_a - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        recovery_verify = ((verify_a - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        recovery_rescue = ((best_rescue - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        delta_recovery = recovery_rescue - recovery_verify   # KEY: vs the self-referential control
        delta_recovery_vs_open = recovery_rescue - recovery_open
        autonomous_closure = ((best_rescue - flat) / headroom_exec) if headroom_exec > 1e-6 else 0.0
        lift_flat = best_rescue - flat
        lift_random = best_rescue - rand
        lift_open = best_rescue - open_a
        lift_verify = best_rescue - verify_a
        index_artifact_gap = idxm - rand
        chain_steps = n_boundaries(r["dd"], SEG_LEN) - 1

        degen = _mean(_field_col(rk, "degenerate_rate"))
        anti_taut = _mean(_field_col(rk, "anti_tautology_corr"))
        exact = _mean(_field_col(rk, "exact_match_rate"))
        rr_test = _mean(_field_col(rk, "reach_rank_test"))
        retry_combo = _mean(_field_col(rk, "retry_rate_combo"))
        fb_combo = _mean(_field_col(rk, "fallback_rate_combo"))
        bidir_sel = _mean(_field_col(rk, "bidir_mean_selected"))
        bidir_all = _mean(_field_col(rk, "bidir_mean_all_cand"))
        bidir_open = _mean(_field_col(rk, "bidir_mean_open_cand"))
        frac_not_open = _mean(_field_col(rk, "frac_selected_not_open"))
        entropy = decision_entropy(r["n_ops"], r["dd"])

        # pooled paired sign-test: replay vs verify (KEY), index vs random
        n_res_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_rescue_only_vs_verify"]) for k in present)
        n_ver_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_verify_only_vs_rescue"]) for k in present)
        n_disc = n_res_only + n_ver_only
        sign_p = binom_two_sided_p(n_res_only, n_disc, 0.5) if n_disc > 0 else 1.0
        n_idx_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_idx_only_vs_rand"]) for k in present)
        n_rand_only_idx = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_rand_only_vs_idx"]) for k in present)
        n_disc_idx = n_idx_only + n_rand_only_idx
        idx_sign_p = binom_two_sided_p(n_idx_only, n_disc_idx, 0.5) if n_disc_idx > 0 else 1.0

        # arms-differ (AF): replay trace vs verify/open/flat/random per seed; hier_oracle vs shuffled
        af_collision = False
        for k in present:
            rr = per_seed[k]["regime_results"][rk]
            h = rr["op_trace_hashes"]
            brs = rr["best_rescue_arm"]
            if h[brs] in (h["wp_bisect_verify"], h["wp_bisect_open"], h["flat_gonogo"],
                          h["wp_random_state"]):
                af_collision = True
            if h["hier_oracle"] == h["hier_shuffled"]:
                af_collision = True

        oracle_rail_ok = bool(oexec >= ORACLE_RAIL_MIN)
        headroom_exec_ok = bool(headroom_exec >= HEADROOM_EXEC_MIN)
        headroom_decomp_ok = bool(headroom_decomp >= HEADROOM_DECOMP_MIN)
        brs_cv = arm_cvs[best_rescue_arm]

        index_leak = bool(index_artifact_gap > INDEX_LEAK_GAP and idx_sign_p < INDEX_LEAK_P)

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "entropy": entropy, "chain_steps": int(chain_steps),
            "arm_means": arm_means, "arm_cvs": arm_cvs,
            "flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
            "wp_bisect_open": open_a, "wp_bisect_verify": verify_a,
            "wp_random_state": rand, "wp_index_midpoint": idxm,
            "best_rescue_arm": best_rescue_arm, "best_rescue": float(best_rescue),
            "headroom_exec": float(headroom_exec), "headroom_decomp": float(headroom_decomp),
            "recovery_open": float(recovery_open), "recovery_verify": float(recovery_verify),
            "recovery_rescue": float(recovery_rescue),
            "delta_recovery": float(delta_recovery),
            "delta_recovery_vs_open": float(delta_recovery_vs_open),
            "autonomous_closure": float(autonomous_closure),
            "lift_flat": float(lift_flat), "lift_random": float(lift_random),
            "lift_open": float(lift_open), "lift_verify": float(lift_verify),
            "index_artifact_gap": float(index_artifact_gap),
            "degenerate_rate": float(degen), "anti_tautology_corr": float(anti_taut),
            "exact_match_rate": float(exact), "reach_rank_test": float(rr_test),
            "retry_rate_combo": float(retry_combo), "fallback_rate_combo": float(fb_combo),
            "bidir_mean_selected": float(bidir_sel), "bidir_mean_all_cand": float(bidir_all),
            "bidir_mean_open_cand": float(bidir_open), "frac_selected_not_open": float(frac_not_open),
            "sign_test_p": float(sign_p), "idx_sign_p": float(idx_sign_p),
            "n_rescue_only": int(n_res_only), "n_verify_only": int(n_ver_only),
            "oracle_rail_ok": oracle_rail_ok, "headroom_exec_ok": headroom_exec_ok,
            "headroom_decomp_ok": headroom_decomp_ok, "brs_cv": float(brs_cv),
            "af_collision": bool(af_collision), "index_leak": index_leak,
            "flatness_ratio": 0.0, "hp_ok": False,   # filled in second pass (needs d4 sibling)
        }

    # ---- second pass: flatness_ratio (needs the chain_steps==1 sibling) + hp_ok ----
    def _shallow_ref(v):
        """recovery_rescue at the matching chain_steps==1 (dd=4) regime with same n_ops & V."""
        for rk2, v2 in per_regime.items():
            if (v2["n_ops"] == v["n_ops"] and v2["V"] == v["V"]
                    and v2["chain_steps"] == 1 and v2["n_seeds"] > 0):
                return v2["recovery_rescue"]
        return None

    for rk, v in per_regime.items():
        ref = _shallow_ref(v)
        if ref is not None and ref > 1e-6:
            v["flatness_ratio"] = float(v["recovery_rescue"] / ref)
        else:
            v["flatness_ratio"] = 0.0        # no positive shallow reference -> flatness undefined -> 0
        hp_ok = (v["oracle_rail_ok"] and v["headroom_exec_ok"] and v["headroom_decomp_ok"]
                 and v["recovery_rescue"] >= HP_RECOVERY_RATIO_FLOOR
                 and v["delta_recovery"] >= HP_DELTA_RECOVERY_MIN
                 and v["flatness_ratio"] >= HP_FLATNESS_MIN
                 and v["lift_flat"] > HP_LIFT_FLAT_MIN
                 and v["lift_random"] > HP_LIFT_RANDOM_MIN
                 and v["index_artifact_gap"] < HP_INDEX_GAP_MAX
                 and v["anti_tautology_corr"] < HP_ANTI_TAUT_CORR_MAX
                 and v["degenerate_rate"] < HP_DEGENERATE_MAX
                 and v["sign_test_p"] < HP_SIGN_TEST_P
                 and (v["brs_cv"] < HP_CV_MAX or RUN_MODE != "full")
                 and not v["af_collision"])
        v["hp_ok"] = bool(hp_ok)

    # ---- reported regardless: entropy relationship of delta_recovery ----
    grid_ents, grid_delta = [], []
    for rk, v in per_regime.items():
        if v["n_seeds"] > 0 and v["headroom_decomp"] > 1e-6:
            grid_ents.append(v["entropy"]); grid_delta.append(v["delta_recovery"])
    spearman_delta_vs_entropy = _spearman(grid_delta, grid_ents)

    # ---- focus = highest-entropy discriminating regime (op4_V1200_d8 in FULL) ----
    cardinality_ok = completed_units >= EXPECTED_N_UNITS
    discriminating = {rk: v for rk, v in per_regime.items()
                      if v["oracle_rail_ok"] and v["headroom_exec_ok"]
                      and v["headroom_decomp_ok"] and v["n_seeds"] > 0}
    focus_rk = None
    if discriminating:
        focus_rk = max(discriminating.keys(),
                       key=lambda rk: (per_regime[rk]["entropy"], per_regime[rk]["n_ops"],
                                       per_regime[rk]["dd"]))
    fv = per_regime[focus_rk] if focus_rk is not None else None

    # ---- reported REGARDLESS: rescue depth-frontier (does NOT move locked FOCUS goalposts) ----
    hp_ok_keys = [rk for rk, v in per_regime.items() if v["hp_ok"] and v["n_seeds"] > 0]
    n_regimes_hp_ok = len(hp_ok_keys)
    capability_frontier = None
    max_entropy_hp_ok = None
    if hp_ok_keys:
        capability_frontier = max(hp_ok_keys,
                                  key=lambda rk: (per_regime[rk]["entropy"],
                                                  per_regime[rk]["n_ops"], per_regime[rk]["dd"]))
        max_entropy_hp_ok = per_regime[capability_frontier]["entropy"]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif fv is None:
        verdict = "INCONCLUSIVE_NO_DISCRIMINATING_REGIME"
    elif fv["index_leak"]:
        verdict = "INCONCLUSIVE_INDEX_ORDER_LEAK"
    elif fv["delta_recovery"] <= HF_DELTA_RECOVERY_CEIL:
        # no material lift over the already-failed SELF-REFERENTIAL control (verify) despite an
        # informationally-independent, brain-precedented correction signal -> bound doubly confirmed.
        verdict = "HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL"
    elif fv["flatness_ratio"] < HF_FLATNESS_CEIL:
        verdict = "HARD_FAIL_ACCELERATING_COLLAPSE"     # still an accelerating, not bounded, collapse
    elif fv["hp_ok"]:
        verdict = "HARD_PASS"
    else:
        # replay helps over verify (delta > 0.05, flatness >= 0.2) but sub-threshold or a guard failed
        if fv["index_artifact_gap"] >= HP_INDEX_GAP_MAX:
            verdict = "MIDDLE_BAND_INDEX_ARTIFACT_GUARD"
        elif fv["anti_tautology_corr"] >= HP_ANTI_TAUT_CORR_MAX:
            verdict = "MIDDLE_BAND_ANTI_TAUTOLOGY_GUARD"
        elif fv["degenerate_rate"] >= HP_DEGENERATE_MAX:
            verdict = "MIDDLE_BAND_DEGENERATE_GUARD"
        elif fv["lift_random"] <= HP_LIFT_RANDOM_MIN:
            verdict = "MIDDLE_BAND_LIFT_RANDOM_BELOW"
        elif fv["delta_recovery"] < HP_DELTA_RECOVERY_MIN:
            verdict = "MIDDLE_BAND_PARTIAL_RESCUE_DELTA_BELOW_15"
        elif fv["flatness_ratio"] < HP_FLATNESS_MIN:
            verdict = "MIDDLE_BAND_FLATNESS_BELOW_50"
        elif fv["recovery_rescue"] < HP_RECOVERY_RATIO_FLOOR:
            verdict = "MIDDLE_BAND_RECOVERY_BELOW_20"
        elif fv["sign_test_p"] >= HP_SIGN_TEST_P:
            verdict = "MIDDLE_BAND_SIGN_TEST_NS"
        elif RUN_MODE == "full" and fv["brs_cv"] >= HP_CV_MAX:
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        else:
            verdict = "MIDDLE_BAND_SUBTHRESHOLD"

    grid_str = " ".join(
        "%s(e%.1f:F%.2f/O%.2f/OPEN%.2f/VER%.2f/REPLAY%.2f/RAND%.2f)" % (
            rk, per_regime[rk]["entropy"], per_regime[rk]["flat_gonogo"],
            per_regime[rk]["hier_oracle"], per_regime[rk]["wp_bisect_open"],
            per_regime[rk]["wp_bisect_verify"],
            per_regime[rk]["arm_means"]["wp_replay_generate_select"], per_regime[rk]["wp_random_state"])
        for rk in REGIME_KEYS if rk in per_regime and per_regime[rk]["n_seeds"] > 0)

    if fv is not None:
        head = ("%s | FOCUS=%s(ent=%.1f steps=%d) FLAT=%.3f OEXEC=%.3f HIER_ORACLE=%.3f | OPEN=%.3f "
                "VERIFY=%.3f REPLAY=%.3f recov_ver=%.3f recov_replay=%.3f DELTA(vs_ver)=%.3f "
                "flatness=%.3f | lift_flat=%.3f lift_random=%.3f lift_verify=%.3f | index_gap=%.3f "
                "anti_taut=%.3f degen=%.3f sign_p=%.4g rr=%.3f cv=%.3f | bidir_sel=%.3f bidir_all=%.3f "
                "fracNotOpen=%.3f | spr(delta,ent)=%.3f | GRID [%s] n_seeds=%d") % (
            verdict, focus_rk, fv["entropy"], fv["chain_steps"], fv["flat_gonogo"], fv["oracle_exec"],
            fv["hier_oracle"], fv["wp_bisect_open"], fv["wp_bisect_verify"], fv["best_rescue"],
            fv["recovery_verify"], fv["recovery_rescue"], fv["delta_recovery"], fv["flatness_ratio"],
            fv["lift_flat"], fv["lift_random"], fv["lift_verify"], fv["index_artifact_gap"],
            fv["anti_tautology_corr"], fv["degenerate_rate"], fv["sign_test_p"], fv["reach_rank_test"],
            fv["brs_cv"], fv["bidir_mean_selected"], fv["bidir_mean_all_cand"],
            fv["frac_selected_not_open"], spearman_delta_vs_entropy, grid_str, len(keys))
    else:
        head = "%s | no discriminating regime | GRID [%s] n_seeds=%d" % (verdict, grid_str, len(keys))

    head = head + (" | CAP_FRONTIER=%s(maxE=%s) n_hp_ok=%d/%d"
                   % (capability_frontier, max_entropy_hp_ok, n_regimes_hp_ok, len(per_regime)))

    return {
        "verdict": verdict, "verdict_msg": head, "summary": head,
        "per_regime": per_regime, "focus_regime": focus_rk,
        "focus_best_rescue_arm": (fv["best_rescue_arm"] if fv else None),
        "focus_best_rescue": (fv["best_rescue"] if fv else None),
        "focus_wp_bisect_open": (fv["wp_bisect_open"] if fv else None),
        "focus_wp_bisect_verify": (fv["wp_bisect_verify"] if fv else None),
        "focus_recovery_open": (fv["recovery_open"] if fv else None),
        "focus_recovery_verify": (fv["recovery_verify"] if fv else None),
        "focus_recovery_rescue": (fv["recovery_rescue"] if fv else None),
        "focus_delta_recovery": (fv["delta_recovery"] if fv else None),
        "focus_delta_recovery_vs_open": (fv["delta_recovery_vs_open"] if fv else None),
        "focus_flatness_ratio": (fv["flatness_ratio"] if fv else None),
        "focus_lift_flat": (fv["lift_flat"] if fv else None),
        "focus_lift_random": (fv["lift_random"] if fv else None),
        "focus_lift_open": (fv["lift_open"] if fv else None),
        "focus_lift_verify": (fv["lift_verify"] if fv else None),
        "focus_bidir_mean_selected": (fv["bidir_mean_selected"] if fv else None),
        "focus_bidir_mean_all_cand": (fv["bidir_mean_all_cand"] if fv else None),
        "focus_frac_selected_not_open": (fv["frac_selected_not_open"] if fv else None),
        "focus_index_artifact_gap": (fv["index_artifact_gap"] if fv else None),
        "rescue_beats_verify": bool(fv["delta_recovery"] > MIDDLE_DELTA_MIN) if fv else False,
        "spearman_delta_vs_entropy": spearman_delta_vs_entropy,
        "discriminating_regime_keys": list(discriminating.keys()),
        "n_regimes_hp_ok": int(n_regimes_hp_ok), "hp_ok_regime_keys": hp_ok_keys,
        "rescue_capability_frontier": capability_frontier,
        "max_entropy_hp_ok": (float(max_entropy_hp_ok) if max_entropy_hp_ok is not None else None),
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "cv_gate_enforced": bool(RUN_MODE == "full"),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gS=%.2f gL=%.2f span_thr=%d tau_pctl=%.2f seg_len=%d"
          % (DEVICE, GAMMA_SHORT, GAMMA_LONG, SPAN_LONG_THRESH, VERIFY_TAU_PCTL, SEG_LEN), flush=True)

    # ST1: SR-TD delta-rule shrinks the TD prediction error over steps
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    E = make_bipolar_E(12, 128, gen)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5, gamma=0.8, gen=gen)
    assert diag["err_last"] is not None and diag["err_last"] < diag["err_first"], "ST1 TD not shrink"
    assert float(M.norm()) > 1e-4, "ST1 M ~zero"
    print("[selftest] ST1 TD shrinks RPE %.4f->%.4f OK" % (diag["err_first"], diag["err_last"]), flush=True)

    # ST2: reach matrix identity R[i,j]==reach_value(E[i],E[j],M)
    gen3 = torch.Generator(device=DEVICE); gen3.manual_seed(3)
    E3 = make_bipolar_E(20, 512, gen3)
    tr3 = np.array([[i, (i + 1) % 20] for i in range(20)] * 3, dtype=np.int64)
    M3, _ = train_sr_transport(E3, tr3, 512, steps=300, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen3)
    R3 = build_reach_matrix(E3, M3)
    for (i, j) in [(0, 5), (3, 3), (7, 12), (19, 1)]:
        rv = float(reach_value(E3[i:i + 1], E3[j:j + 1], M3)[0])
        assert abs(R3[i, j].item() - rv) < 1e-4, "ST2 R[%d,%d] mismatch" % (i, j)
    print("[selftest] ST2 reach matrix identity OK", flush=True)

    # ST3: gamma_for_span uses long horizon only beyond the threshold
    assert gamma_for_span(8) == GAMMA_LONG and gamma_for_span(6) == GAMMA_LONG, "ST3 long span"
    assert gamma_for_span(5) == GAMMA_SHORT and gamma_for_span(4) == GAMMA_SHORT, "ST3 short span"
    assert gamma_for_span(2) == GAMMA_SHORT, "ST3 tiny span"
    print("[selftest] ST3 gamma_for_span: span6/8->%.2f span4/5->%.2f OK" % (GAMMA_LONG, GAMMA_SHORT),
          flush=True)

    # ST4: build a toy R with a KNOWN good midpoint; open bisection + verify + c2f all fire & are
    #      non-degenerate (interior != start/goal), last boundary == goal, interiors distinct.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(11)
    Vt, Nt = 24, 1024
    Et = make_bipolar_E(Vt, Nt, gen4)
    chain = [(k, k + 1) for k in range(0, 8)]
    trt = np.tile(np.array(chain, dtype=np.int64), (60, 1))
    Mt, _ = train_sr_transport(Et, trt, Nt, steps=1500, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen4)
    Mt_l, _ = train_sr_transport(Et, trt, Nt, steps=1500, batch=16, base_lr=0.5, gamma=GAMMA_LONG, gen=gen4)
    Rt = build_reach_matrix(Et, Mt)
    Rt_l = build_reach_matrix(Et, Mt_l)
    tau_s = offdiag_quantile(Rt, VERIFY_TAU_PCTL)
    tau_l = offdiag_quantile(Rt_l, VERIFY_TAU_PCTL)
    dgen = np.random.default_rng(4)
    st = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gl = torch.tensor([8], dtype=torch.long, device=DEVICE)
    for label, b in [
        ("open", _discover_bisect_boundaries(st, gl, Rt, 2, 8)),
        ("verify", _discover_verify_boundaries(st, gl, Rt, tau_s, 2, 8, dgen)),
        ("c2f", _discover_coarse2fine_boundaries(st, gl, Rt, Rt_l, tau_s, tau_l, 2, 8, False, dgen)),
        ("combo", _discover_coarse2fine_boundaries(st, gl, Rt, Rt_l, tau_s, tau_l, 2, 8, True, dgen)),
    ]:
        assert int(b[0, -1].item()) == 8, "ST4 %s last boundary must be goal" % label
        interior = b[0, :-1].tolist()
        assert all(x not in (0, 8) for x in interior), "ST4 %s interior degenerate: %s" % (label, interior)
        assert len(set(interior)) == len(interior), "ST4 %s interiors not distinct: %s" % (label, interior)
    print("[selftest] ST4 open/verify/c2f/combo all non-degenerate, distinct, goal-terminated OK",
          flush=True)

    # ST5: coarse-to-fine picks the MIDDLE first from GROUND-TRUTH endpoints. Construct an R where the
    #      true middle node (4) balances start(0)/goal(8) far better than any other; c2f must select it
    #      at the center boundary (array index 1 for d8 seg2: interiors at pos 2,4,6).
    Vm = 12
    Rm = torch.full((Vm, Vm), 0.05, device=DEVICE, dtype=DTYPE)
    Rm.fill_diagonal_(1.0)
    # make node 4 strongly reachable-from-0 and reaching-8 (the ideal center); nodes 2/6 moderate.
    Rm[0, 4] = 0.9; Rm[4, 8] = 0.9
    Rm[0, 2] = 0.6; Rm[2, 8] = 0.6
    Rm[4, 6] = 0.6; Rm[6, 8] = 0.6
    Rm[0, 6] = 0.3; Rm[6, 8] = max(float(Rm[6, 8]), 0.6)
    Rm[4, 2] = 0.6
    st1 = torch.tensor([0], dtype=torch.long, device=DEVICE)
    gl1 = torch.tensor([8], dtype=torch.long, device=DEVICE)
    tau_m = offdiag_quantile(Rm, VERIFY_TAU_PCTL)
    bm = _discover_coarse2fine_boundaries(st1, gl1, Rm, Rm, tau_m, tau_m, 2, 8, False, np.random.default_rng(1))
    # center boundary is array index 1 (pos 4). It is picked FIRST from (start=0, goal=8); node 4 wins.
    assert int(bm[0, 1].item()) == 4, "ST5 c2f center pick should be node 4, got %d" % int(bm[0, 1])
    print("[selftest] ST5 coarse-to-fine center pick from ground-truth endpoints = node 4 OK", flush=True)

    # ST6: verify-gate = commit-only-if-strong. The AND-of-two-legs threshold (R[a,c]>=tau AND
    #      R[c,g]>=tau) is exactly balance=min(legs)>=tau, so a STRONG top pick (balance>=tau) is
    #      committed identically to open (verify agrees with the unverified argmax when the pick is
    #      well-connected). Node 3 has balance 0.9 >= tau=0.5 -> both open and verify pick it.
    Vv = 8
    Rv = torch.full((Vv, Vv), 0.10, device=DEVICE, dtype=DTYPE)
    Rv.fill_diagonal_(1.0)
    Rv[0, 3] = 0.90; Rv[3, 7] = 0.90       # node 3: balance 0.90 >= tau -> passes verify AND is argmax
    stv = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glv = torch.tensor([7], dtype=torch.long, device=DEVICE)
    tau_v = 0.5
    p_open = _pick_balanced_verify(stv, glv, Rv, tau_v, [], False, np.random.default_rng(2), None)
    p_ver = _pick_balanced_verify(stv, glv, Rv, tau_v, [], True, np.random.default_rng(2), None)
    assert int(p_open[0].item()) == 3, "ST6 open argmax should be node 3, got %d" % int(p_open[0])
    assert int(p_ver[0].item()) == 3, "ST6 verify (strong pick) should agree w/ open (node 3), got %d" % int(p_ver[0])
    print("[selftest] ST6 verify-gate commits a strong pick identically to open (node 3) OK", flush=True)

    # ST7: verify-gate REFUSES a weak pick. When open's argmax pick has balance < tau (no candidate is
    #      well-connected), verify does NOT commit it -> falls back to a valid random state (!= start/goal,
    #      logged). This is the don't-chain-a-weak-waypoint behavior; the discriminator vs open.
    Rlow = torch.full((6, 6), 0.10, device=DEVICE, dtype=DTYPE); Rlow.fill_diagonal_(1.0)
    stf = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glf = torch.tensor([5], dtype=torch.long, device=DEVICE)
    p_open_w = _pick_balanced_verify(stf, glf, Rlow, 0.5, [], False, np.random.default_rng(3), None)
    assert int(p_open_w[0].item()) not in (0, 5), "ST7 open pick landed on start/goal"
    stats_f = {"n_picks": 0, "n_retry": 0, "n_fallback": 0}
    pf = _pick_balanced_verify(stf, glf, Rlow, 0.9, [], True, np.random.default_rng(3), stats_f)
    assert int(pf[0].item()) not in (0, 5), "ST7 fallback landed on start/goal"
    assert stats_f["n_fallback"] == 1, "ST7 fallback not counted (%d)" % stats_f["n_fallback"]
    assert stats_f["n_retry"] >= 1, "ST7 weak pick should register retries before fallback"
    print("[selftest] ST7 verify-gate refuses weak pick -> valid random fallback, counted OK", flush=True)

    # ST8: index-midpoint interpolation (structural guard) VERBATIM behavior
    st6 = torch.tensor([10, 100], dtype=torch.long, device=DEVICE)
    tg6 = torch.tensor([30, 200], dtype=torch.long, device=DEVICE)
    ib4 = _discover_index_boundaries(st6, tg6, 300, 2, 4)
    assert abs(int(ib4[0, 0].item()) - 20) <= 1 and abs(int(ib4[1, 0].item()) - 150) <= 1, "ST8 idx mid"
    assert int(ib4[0, -1].item()) == 30, "ST8 idx last must be goal"
    print("[selftest] ST8 index-midpoint interpolation OK", flush=True)

    # ST9: boundaries->hops schedule matches the ancestor build_waypoint_idx schedule
    bstate = torch.tensor([[100, 200, 300]], dtype=torch.long, device=DEVICE)
    hops = _boundaries_to_hops(bstate, 2, 6)
    exp = torch.tensor([100, 100, 200, 200, 300, 300], dtype=torch.long, device=DEVICE)
    assert bool((hops[0] == exp).all()), "ST9 hop schedule wrong"
    print("[selftest] ST9 boundaries->hops schedule OK", flush=True)

    # ST9b: REVERSE SR -- training on cur<->nxt swapped transitions makes R_rev[nxt,cur] large (the
    #       reverse channel: "cur typically precedes nxt"). On a fwd chain 0->1->...->k, R_rev[j+1,j]
    #       (predecessor reach) should exceed R_rev[j,j+1] (successor reach) on average.
    gen9 = torch.Generator(device=DEVICE); gen9.manual_seed(21)
    Vr, Nr = 20, 512
    Er = make_bipolar_E(Vr, Nr, gen9)
    fwd_tr = np.array([[i, (i + 1) % Vr] for i in range(Vr)] * 4, dtype=np.int64)
    rev_tr = fwd_tr[:, ::-1].copy()
    Mrev, _ = train_sr_transport(Er, rev_tr, Nr, steps=800, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen9)
    Rrev = build_reach_matrix(Er, Mrev)
    pred_reach = float(np.mean([Rrev[(i + 1) % Vr, i].item() for i in range(Vr)]))   # predecessor
    succ_reach = float(np.mean([Rrev[i, (i + 1) % Vr].item() for i in range(Vr)]))   # successor
    assert pred_reach > succ_reach, "ST9b reverse SR: predecessor reach %.3f !> successor %.3f" % (
        pred_reach, succ_reach)
    print("[selftest] ST9b reverse SR predecessor=%.3f > successor=%.3f OK" % (pred_reach, succ_reach),
          flush=True)

    # ST9c: generate_candidates -- candidate 0 == unperturbed open pick (perturb_frac=0 identity);
    #       all candidates goal-terminated + non-degenerate; perturbation yields >=1 distinct candidate
    #       when the balance signal is not perfectly peaked.
    gen9c = torch.Generator(device=DEVICE); gen9c.manual_seed(33)
    Vc, Nc = 24, 1024
    Ec = make_bipolar_E(Vc, Nc, gen9c)
    ch = [(k, k + 1) for k in range(0, 8)]
    trc = np.tile(np.array(ch, dtype=np.int64), (60, 1))
    Mc, _ = train_sr_transport(Ec, trc, Nc, steps=1200, batch=16, base_lr=0.5, gamma=GAMMA_SHORT, gen=gen9c)
    Rc = build_reach_matrix(Ec, Mc)
    stc = torch.tensor([0], dtype=torch.long, device=DEVICE)
    glc = torch.tensor([8], dtype=torch.long, device=DEVICE)
    rgen_t = torch.Generator(device=DEVICE); rgen_t.manual_seed(7)
    cands = generate_candidates(stc, glc, Rc, 2, 8, 5, rgen_t, 0.60)
    open_b = _discover_bisect_boundaries(stc, glc, Rc, 2, 8)
    assert cands.shape[0] == 5, "ST9c wrong n_cand"
    assert bool((cands[0] == open_b).all()), "ST9c candidate 0 must equal unperturbed open pick"
    for c in range(cands.shape[0]):
        assert int(cands[c, 0, -1].item()) == 8, "ST9c cand %d not goal-terminated" % c
        interior = cands[c, 0, :-1].tolist()
        assert all(x not in (0, 8) for x in interior), "ST9c cand %d degenerate: %s" % (c, interior)
        assert len(set(interior)) == len(interior), "ST9c cand %d interiors not distinct" % c
    n_distinct = len({tuple(cands[c, 0].tolist()) for c in range(cands.shape[0])})
    assert n_distinct >= 2, "ST9c perturbation produced no candidate diversity (n_distinct=%d)" % n_distinct
    print("[selftest] ST9c generate_candidates: cand0==open, all goal-term+non-degen, diversity=%d OK"
          % n_distinct, flush=True)

    # ST9d: score_bidirectional -- a candidate through a KNOWN-good midpoint (fwd AND rev agree) scores
    #       higher than one through a bad midpoint (directions disagree). Construct explicit R_fwd/R_rev.
    Vg = 6
    Rf = torch.full((Vg, Vg), 0.05, device=DEVICE, dtype=DTYPE); Rf.fill_diagonal_(1.0)
    Rr = torch.full((Vg, Vg), 0.05, device=DEVICE, dtype=DTYPE); Rr.fill_diagonal_(1.0)
    # good path 0->2->5: fwd strong (0->2, 2->5) AND rev strong (5->2, 2->0)
    Rf[0, 2] = 0.9; Rf[2, 5] = 0.9; Rr[5, 2] = 0.9; Rr[2, 0] = 0.9
    # bad path 0->3->5: fwd ok (0->3, 3->5) but rev DISAGREES (5->3, 3->0 weak)
    Rf[0, 3] = 0.9; Rf[3, 5] = 0.9; Rr[5, 3] = 0.05; Rr[3, 0] = 0.05
    st_g = torch.tensor([0], dtype=torch.long, device=DEVICE)
    good = torch.tensor([[2, 5]], dtype=torch.long, device=DEVICE)   # [mid, goal]
    bad = torch.tensor([[3, 5]], dtype=torch.long, device=DEVICE)
    s_good = float(score_bidirectional(good, st_g, Rf, Rr)[0])
    s_bad = float(score_bidirectional(bad, st_g, Rf, Rr)[0])
    assert s_good > s_bad, "ST9d bidirectional score: good %.3f !> bad %.3f" % (s_good, s_bad)
    print("[selftest] ST9d score_bidirectional good=%.3f > bad=%.3f (fwd-rev agreement) OK"
          % (s_good, s_bad), flush=True)

    # ST9e: wp_replay_generate_select COMMITS the agreeing candidate. With the good/bad R above and both
    #       candidates in the pool (candidate 0 = whichever open picks; force a 2-candidate pool by
    #       explicit generation), the selected interior must be the fwd-rev-agreeing node 2, not node 3.
    pool = torch.stack([good, bad], dim=0)          # [2, 1, 2]
    scores = torch.stack([score_bidirectional(pool[i], st_g, Rf, Rr) for i in range(2)], dim=0)
    sel = int(pool[scores.argmax(dim=0)[0], 0, 0].item())
    assert sel == 2, "ST9e replay-select should commit the agreeing node 2, got %d" % sel
    print("[selftest] ST9e replay-select commits fwd-rev-agreeing candidate (node 2) OK", flush=True)

    # ST10: recovery / delta(vs verify) / flatness formulas (grounded on the ancestor FOCUS numbers)
    flat_, oexec_, horc_, verify_, replay_ = 0.081, 0.918, 0.906, 0.096, 0.35
    hd = horc_ - flat_
    rv = (verify_ - flat_) / hd                       # recovery_verify (MEASURED ancestor ~0.0182)
    rr = (replay_ - flat_) / hd                       # recovery_replay
    delta = rr - rv
    assert abs(rv - 0.018182) < 1e-3, "ST10 recovery_verify off: %.5f" % rv
    assert abs(rr - 0.326061) < 1e-3, "ST10 recovery_replay off: %.5f" % rr
    assert abs(delta - 0.307879) < 1e-3, "ST10 delta(vs verify) off: %.5f" % delta
    # flatness: FOCUS recovery / shallow (d4) recovery. shallow replay recovery ~0.65 -> flatness ~0.50
    shallow_flat, shallow_horc, shallow_replay = 0.515, 0.953, 0.80
    shd = shallow_horc - shallow_flat
    shallow_rec = (shallow_replay - shallow_flat) / shd
    flatness = rr / shallow_rec
    assert abs(shallow_rec - 0.650685) < 1e-3, "ST10 shallow recovery off: %.5f" % shallow_rec
    assert abs(flatness - 0.501258) < 1e-3, "ST10 flatness off: %.5f" % flatness
    print("[selftest] ST10 recovery_verify=%.3f recovery_replay=%.3f delta=%.3f flatness=%.3f OK"
          % (rv, rr, delta, flatness), flush=True)

    # ST11: spearman + entropy + binom
    assert abs(_spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) - 1.0) < 1e-9, "ST11 spearman"
    assert abs(decision_entropy(4, 8) - 16.0) < 1e-9, "ST11 entropy op4_d8"
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0 and abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST11 binom"
    print("[selftest] ST11 spearman + entropy + binom OK", flush=True)

    # ST12: full pipeline single-seed structural (all 11 arms + diagnostics present; oracle sane;
    #       positive-control: wp_replay trace differs from open/verify)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_waypoint_rescue")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST12 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST12 missing arm %s" % arm
    for fld in ("degenerate_rate", "anti_tautology_corr", "best_rescue_arm", "retry_rate_combo"):
        assert fld in r["regime_results"][rk0], "ST12 missing field %s" % fld
    oexec = r["regime_results"][rk0]["arms"]["oracle_exec"]
    assert oexec >= 0.5, "ST12 oracle_exec too low (%.3f)" % oexec
    print("[selftest] ST12 pipeline OK arms=%d oracle_exec=%.3f" % (len(ARMS), oexec), flush=True)

    # ST13: verdict wiring (HARD_PASS; HARD_FAIL no-lift; MIDDLE partial; INCONCLUSIVE)
    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    def _mk(n_ops, V, dd, flat, oexec, horc, open_a, ver, replay, rand, idxm,
            degen=0.02, taut=0.10, exact=0.20, rr=0.60,
            n_res_only=None, n_idx_only=2, n_rand_only_idx=2):
        # rescue arm = replay (FIXED); KEY comparator = verify. paired KEY = replay-vs-verify.
        if n_res_only is None:
            n_res_only = 45 if replay > ver + 0.1 else 1
        arms = {"flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
                "hier_shuffled": 0.02, "wp_bisect_open": open_a, "wp_bisect_coarse2fine": ver,
                "wp_bisect_verify": ver, "wp_bisect_combo": ver,
                "wp_replay_generate_select": replay, "wp_random_state": rand,
                "wp_index_midpoint": idxm}
        oth = {"flat_gonogo": "f", "oracle_exec": "oracle_true_seq", "hier_oracle": "ho",
               "hier_shuffled": "hs", "wp_bisect_open": "op", "wp_bisect_coarse2fine": "c2",
               "wp_bisect_verify": "vf", "wp_bisect_combo": "cb", "wp_replay_generate_select": "rp",
               "wp_random_state": "rd", "wp_index_midpoint": "ix"}
        return {"n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
                "arms": arms, "op_trace_hashes": oth, "best_rescue_arm": RESCUE_ARM, "best_alpha": 0.2,
                "wr_open": 1.0, "wr_c2f": 1.0, "wr_ver": 1.0, "wr_combo": 1.0, "wr_replay": 1.0,
                "reach_rank_chance": 1.0 / n_ops, "reach_rank_test": rr, "degenerate_rate": degen,
                "anti_tautology_corr": taut, "exact_match_rate": exact, "retry_rate_combo": 0.1,
                "retry_rate_verify": 0.1, "fallback_rate_combo": 0.0,
                "bidir_mean_selected": 0.7, "bidir_mean_all_cand": 0.5, "bidir_mean_open_cand": 0.5,
                "frac_selected_not_open": 0.6,
                "paired": {"n_rescue_only_vs_verify": n_res_only, "n_verify_only_vs_rescue": 2,
                           "n_rescue_only_vs_open": n_res_only, "n_open_only_vs_rescue": 2,
                           "n_rescue_only_vs_flat": 40, "n_flat_only_vs_rescue": 2,
                           "n_rescue_only_vs_rand": 40, "n_rand_only_vs_rescue": 2,
                           "n_idx_only_vs_rand": n_idx_only, "n_rand_only_vs_idx": n_rand_only_idx,
                           "n_test": 60}}

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    reg_lo = regime_key(4, 1200, 4)     # chain_steps=1 (flatness reference)
    reg_hi = regime_key(4, 1200, 8)     # chain_steps=3 (FOCUS)
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4}, {"n_ops": 4, "V": 1200, "dd": 8}]
    REGIME_KEYS = [reg_lo, reg_hi]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    try:
        # HARD_PASS: FOCUS d8 flat=0.081 oexec=0.918 horc=0.906 (hd=0.825); verify=0.096
        #  (recovery_verify=0.0182); replay=0.36 -> recovery_replay=0.338>=0.20; delta=0.320>=0.15.
        #  d4 flat=0.515 horc=0.953 (hd=0.438); replay_d4=0.72 -> recovery_d4=0.468;
        #  flatness=0.338/0.468=0.722>=0.5; lift_flat=0.279 lift_random=0.34; guards clean; sign_p<<0.05.
        ps = {}
        for s in ["7", "17", "23"]:
            ps[s] = {"regime_results": {
                reg_lo: _mk(4, 1200, 4, flat=0.515, oexec=0.957, horc=0.953, open_a=0.823,
                            ver=0.823, replay=0.72, rand=0.09, idxm=0.10),
                reg_hi: _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906, open_a=0.097,
                            ver=0.096, replay=0.36, rand=0.02, idxm=0.02),
            }}
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "ST13 expected HARD_PASS got %s" % out["verdict"]
        assert out["focus_regime"] == reg_hi, "ST13 focus should be high-entropy op4_d8"
        assert out["focus_best_rescue_arm"] == "wp_replay_generate_select", "ST13 best_rescue=replay"

        # HARD_FAIL bound-real: delta <= 0.05. replay=0.10 (~verify 0.096) -> recovery_replay=0.023;
        #  delta=0.023-0.0182=0.0048 <= 0.05.
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.10,
                                                  rand=0.02, idxm=0.02, n_res_only=3)
        out2 = aggregate_and_verdict(ps)
        assert out2["verdict"] == "HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL", \
            "ST13 expected HARD_FAIL bound-real got %s" % out2["verdict"]

        # HARD_FAIL accelerating collapse: delta>0.05 but flatness<0.2. replay_d8=0.15 ->
        #  recovery=0.0836; delta=0.0655>0.05; with d4 recovery 0.468 -> flatness=0.179<0.2.
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.15,
                                                  rand=0.02, idxm=0.02, n_res_only=30)
        out2b = aggregate_and_verdict(ps)
        assert out2b["verdict"] == "HARD_FAIL_ACCELERATING_COLLAPSE", \
            "ST13 expected HARD_FAIL accelerating got %s" % out2b["verdict"]

        # MIDDLE partial (delta in [0.05,0.15), flatness>=0.2): d8 replay=0.18 -> recovery=0.120,
        #  delta=0.102; d4 replay=0.646 -> recovery_d4=0.30 -> flatness=0.40 in [0.2,0.5) but delta<0.15
        #  fires FIRST -> DELTA_BELOW_15.
        for s in ps:
            ps[s]["regime_results"][reg_lo] = _mk(4, 1200, 4, flat=0.515, oexec=0.957, horc=0.953,
                                                  open_a=0.823, ver=0.823, replay=0.646,
                                                  rand=0.09, idxm=0.10)
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.18,
                                                  rand=0.02, idxm=0.02, n_res_only=30)
        out3 = aggregate_and_verdict(ps)
        assert out3["verdict"] == "MIDDLE_BAND_PARTIAL_RESCUE_DELTA_BELOW_15", \
            "ST13 expected MIDDLE partial-delta got %s" % out3["verdict"]

        # MIDDLE flatness-below-50 (delta>=0.15 but flatness in [0.2,0.5)): d8 replay=0.287 ->
        #  recovery=0.250, delta=0.232>=0.15; d4 replay=0.778 -> recovery_d4=0.60 -> flatness=0.417.
        for s in ps:
            ps[s]["regime_results"][reg_lo] = _mk(4, 1200, 4, flat=0.515, oexec=0.957, horc=0.953,
                                                  open_a=0.823, ver=0.823, replay=0.778,
                                                  rand=0.09, idxm=0.10)
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.287,
                                                  rand=0.02, idxm=0.02, n_res_only=40)
        out3b = aggregate_and_verdict(ps)
        assert out3b["verdict"] == "MIDDLE_BAND_FLATNESS_BELOW_50", \
            "ST13 expected MIDDLE flatness-below-50 got %s" % out3b["verdict"]

        # MIDDLE recovery-below-20 despite delta>=0.15 & flatness>=0.5: verify BELOW flat so
        #  recovery_verify<0. verify=0.04 -> recovery_verify=-0.0497; d8 replay=0.205 -> recovery=0.150;
        #  delta=0.200>=0.15; recovery 0.150<0.20; d4 replay=0.625 -> recovery_d4=0.251 -> flatness=0.60.
        for s in ps:
            ps[s]["regime_results"][reg_lo] = _mk(4, 1200, 4, flat=0.515, oexec=0.957, horc=0.953,
                                                  open_a=0.823, ver=0.823, replay=0.625,
                                                  rand=0.09, idxm=0.10)
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.040, replay=0.205,
                                                  rand=0.02, idxm=0.02, n_res_only=40)
        out3c = aggregate_and_verdict(ps)
        assert out3c["verdict"] == "MIDDLE_BAND_RECOVERY_BELOW_20", \
            "ST13 expected MIDDLE recovery-below-20 got %s" % out3c["verdict"]

        # MIDDLE via degenerate guard: HARD_PASS-worthy replay but degenerate_rate high
        for s in ps:
            ps[s]["regime_results"][reg_lo] = _mk(4, 1200, 4, flat=0.515, oexec=0.957, horc=0.953,
                                                  open_a=0.823, ver=0.823, replay=0.72,
                                                  rand=0.09, idxm=0.10)
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.36,
                                                  rand=0.02, idxm=0.02, degen=0.25)
        out4 = aggregate_and_verdict(ps)
        assert out4["verdict"] == "MIDDLE_BAND_DEGENERATE_GUARD", \
            "ST13 expected MIDDLE degenerate got %s" % out4["verdict"]

        # INCONCLUSIVE index-order leak: index >> random with significance (fires before delta HF)
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 8, flat=0.081, oexec=0.918, horc=0.906,
                                                  open_a=0.097, ver=0.096, replay=0.36,
                                                  rand=0.02, idxm=0.30, n_idx_only=40, n_rand_only_idx=2)
        out5 = aggregate_and_verdict(ps)
        assert out5["verdict"] == "INCONCLUSIVE_INDEX_ORDER_LEAK", \
            "ST13 expected INCONCLUSIVE leak got %s" % out5["verdict"]

        # INCONCLUSIVE no discriminating regime (oracle_exec below rail)
        for s in ps:
            for rk in (reg_lo, reg_hi):
                ps[s]["regime_results"][rk]["arms"]["oracle_exec"] = 0.50
        out6 = aggregate_and_verdict(ps)
        assert out6["verdict"] == "INCONCLUSIVE_NO_DISCRIMINATING_REGIME", \
            "ST13 expected INCONCLUSIVE no-regime got %s" % out6["verdict"]
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST13 verdict wiring OK (HARD_PASS; HARD_FAIL bound-real+accelerating; MIDDLE "
          "partial-delta+flatness+recovery+degenerate; INCONCLUSIVE leak+no-regime)", flush=True)


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

    print("[%s] mode=%s device=%s N=%d n_ops=%s depths=%s seeds=%s gS=%.2f gL=%.2f seg_len=%d "
          "regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA_SHORT,
             GAMMA_LONG, SEG_LEN, REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST13 (TD shrink, reach-matrix identity, gamma_for_span, "
                               "open/verify/c2f/combo non-degenerate, c2f center-pick, verify-gate "
                               "reject+fallback, index interp, hop schedule, reverse-SR, "
                               "generate_candidates, score_bidirectional, replay-select, "
                               "recovery/delta-vs-verify/flatness formulas, spearman/entropy/binom, "
                               "pipeline, verdict wiring)",
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

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "regimes": REGIME_KEYS}
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
                "seed": int(seed), "run_mode": RUN_MODE, "N": N_DIM,
                "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
                "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000],
                "regime_results": {}, "sr_diag_by_group": {}})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        _heartbeat(out_dir, i + 1, len(remaining), "seed_done=%d dt=%.1f" % (seed, time.time() - t0))
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("regime_results")}
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
