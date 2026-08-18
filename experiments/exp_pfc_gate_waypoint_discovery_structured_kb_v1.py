"""pfc_gate_waypoint_discovery_structured_kb_v1 -- does the substrate's already-certified SR
self-discover a useful sub-goal decomposition WHEN the environment has real room/door bottleneck
structure (a stochastic-block-model KB) instead of the uniform-random Erdos-Renyi KB that the parent
cell used?

WHY (Director steer 2026-07-08; brain-first negative-revival drill):
  The parent cell exp_pfc_gate_autonomous_waypoint_discovery_v1 already BUILT and RAN the SR-eigenoption
  / spectral-bottleneck subgoal-discovery mechanism (spectral_candidate_mask / cluster_candidate_mask ->
  wp_bisect_spectral / wp_bisect_cluster_exit). On its uniform-random KB the spectral/cluster restriction
  slightly UNDERPERFORMED open bisection:
    MEASURED@data/exp_pfc_gate_autonomous_waypoint_discovery_v1/metrics.json:per_regime.op4_V1200_d8
      flat_gonogo=0.0775 oracle_exec=0.9342 hier_oracle=0.9283 wp_bisect_open=0.0658
      spectral_minus_open=-0.0417 cluster_minus_open=-0.0400  -> VERDICT HARD_FAIL_SR_CANNOT_SELF_DISCOVER.
  Solway et al. 2014 (PLoS Comp Biol) formalizes subgoal discovery as a k-way normalized MIN-CUT: subgoals
  live on edges cut by the lowest-frequency eigenvector BETWEEN separable clusters. An Erdos-Renyi/expander
  graph provably has NO small cuts, so the spectral eigenvector carries no bottleneck signal -- the negative
  sign matches theory exactly. CITED@notes/research_hierarchical_subgoal_discovery_sr_eigenoption_brain_first_2026-07-08.md.

  THIS cell changes the ONE confounded variable the parent's own docstring flagged: the synthetic KB
  GENERATOR. Uniform-random -> STOCHASTIC-BLOCK-MODEL room graph (K rooms = dense within-block, doors =
  a few sparse between-block edges = the bottleneck states the eigenvector should cut). EVERY certified /
  mechanism primitive is REUSED VERBATIM by IMPORT from the parent module (make_bipolar_E, hebbian_W,
  cleanup_batched, train_sr_transport, reach_value, build_reach_matrix, spectral_candidate_mask,
  cluster_candidate_mask, _discover_bisect_boundaries, run_hier_arm_wp, oracle_trajectory_idx,
  discovery_diagnostics, reach_rank_acc, the tuning helpers, ...). ZERO new gate/mechanism math -- the
  spectral/cluster discovery still has ZERO oracle access. The ONLY new code is: (1) the SBM KB generator,
  (2) generator-level graph-structure metrics (modularity / within:between ratio -- a saturation-vacuous
  GUARD on the generator so a green result cannot be on a secretly-uniform graph), (3) the spec-vs-open /
  clus-vs-open paired per-chain sign counts (the parent measured best_wp-vs-flat, not spec-vs-open), and
  (4) the verdict re-centered on the SIGN-FLIP headline.

HEADLINE DISCRIMINATOR (per FOCUS regime):
  best_signflip = max(spectral_minus_open, cluster_minus_open).
  Does spectral/cluster candidate-restriction FLIP SIGN POSITIVE on the SBM graph (now that there ARE real
  cuts to find)? On the ER graph best_signflip < 0 (measured). On the SBM graph, if the door states ARE the
  spectral sign-boundary states, restricting the bisection argmax to them should BEAT open bisection.

ARMS (identical 9-arm paired set as the parent; share E/W_ops/M/R/test-chains per (regime,seed)):
  flat_gonogo, oracle_exec, hier_oracle, hier_shuffled, wp_bisect_open, wp_bisect_spectral,
  wp_bisect_cluster_exit, wp_random_state, wp_index_midpoint  -- run on the NEW SBM KB only.

RAILS (discriminator MUST fire; enforced at smoke via assert_discriminator_fires + VacuousSmokeError):
  - hier_oracle MUST SUCCEED (>= HIER_MUST_SUCCEED_MIN): proves the SBM task IS solvable given the true
    decomposition (parent measured ~0.93; the SBM swap must not break the given-decomposition envelope).
  - flat_gonogo MUST FAIL (< FLAT_MUST_FAIL_CEIL): proves the corner is still genuinely hard without
    hierarchy (parent measured ~0.08), so any spectral lift is real, not a saturated easy task.
  - oracle_exec >= 0.90: perfect-execution ceiling reachable (FOCUS gate).
  - SBM MODULARITY GATE: the generated graph MUST have real modular structure (modularity Q >= Q_MIN AND
    within:between edge ratio >= RATIO_MIN), else the whole test is vacuous (a green result would be on a
    graph that is secretly still uniform). This is the saturation-vacuous guard on the GENERATOR.

HARD_PASS (locked; best_signflip at FOCUS): best_signflip >= HP_SIGNFLIP_MARGIN AND signflip_sign_p < 0.05
  AND rails hold AND SBM structure gate holds AND the ORIGINAL absolute bars clear on best_wp = max(open,
  spectral, cluster): lift_flat(best_wp) > 0.05, lift_random(best_wp) > 0.10, recovery_ratio(best_wp) >=
  0.20, index_artifact_gap < 0.05, anti_tautology_corr < 0.85, degenerate_rate < 0.10, cv < 0.10 (FULL).
  => the substrate's certified SR CAN self-discover a useful subgoal decomposition GIVEN real bottleneck
  structure; closes the parent HARD_FAIL as a test-harness domain-fit artifact.
MIDDLE_BAND: best_signflip > 0 AND signflip_sign_p < 0.05 (real sign flip, mechanism fires) but misses
  HP_SIGNFLIP_MARGIN or one of the harder absolute bars -- a genuine positive that needs honest bar
  re-calibration (the original bars were calibrated for the wrong domain), NOT retroactive loosening.
HARD_FAIL_SR_CANNOT_DETECT_BOTTLENECK_EVEN_WITH_STRUCTURE: best_signflip <= 0 OR signflip_sign_p >= 0.05
  EVEN with genuine SBM room/door structure -- a MUCH stronger negative than the parent's (the reach matrix
  cannot detect a bottleneck that demonstrably exists), worth escalating not re-drilling.
HARD_FAIL_SBM_NO_STRUCTURE_GENERATOR_VACUOUS: modularity gate failed (generator did not produce structure)
  -> the test was never valid; fix the generator, do not interpret arms.
INCONCLUSIVE_*: no discriminating regime (rails not met) OR genuine chain-generation index-order leak.
Reported REGARDLESS: full grid for every arm; spec-open / clus-open + paired sign p at FOCUS; modularity /
  within:between ratio / reach-matrix spectral gap per group.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor): identical disciplines as the parent.
# - arms_differ_verified at smoke gate (AF): best_wp vs flat vs random op-trace hash per seed; hier_oracle
#   vs hier_shuffled. (Reuses parent op_trace_hashes.)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
# - except SystemExit: raise BEFORE except Exception (no BaseException in main).
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor; reachability by
#   feasibility (parent hier_oracle=0.928 at op4_V1200_d8 proves the given-decomposition envelope on ER;
#   the SBM swap re-proves it as a rail; the open question is whether spectral RESTRICTION now helps).
# - baseline_in_band (AG): FOCUS gate requires oracle_exec>=0.90 AND flat collapsed (<FLAT_MUST_FAIL_CEIL)
#   AND hier_oracle succeeded (>HIER_MUST_SUCCEED_MIN) AND SBM modularity gate -> measurable + non-vacuous.
# - discriminator survives scale: smoke holds op4 focus at V=300/N=2048 depth{6,8} K=4; the SIGN of
#   spec-open + the rails + the modularity are reported at smoke; FULL scales V(300->1200) N(2048->8192)
#   K(4 and 8) seeds(3->5). At larger N the SR reach is SHARPER so bottleneck detection should IMPROVE or
#   hold; flat does not recover -> the sign-flip discriminator survives-or-grows (option C preview at smoke).
# - HARD_PASS strictly above floor: best_signflip>=0.05 + sign_p<0.05 (META_RULE_L).
# - HP_SCOPE: signflip gate applies to best(spectral,cluster) vs open at FOCUS; absolute bars to best_wp vs
#   flat/random; oracle rail to oracle_exec; modularity gate to the FOCUS group's generated graph.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(9) * n_seeds * n_regimes.
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash).
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR inherited from the certified
#   train_sr_transport; wp_random floor + wp_index structural-leak guard + anti_tautology_corr +
#   degenerate_rate all logged; SBM modularity logged as the generator-honesty gate).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.

Compute architecture: (a) batched-GPU. All mechanism primitives are the parent's batched matmul / one-eigh-
per-group torch ops on cuda-if-available. SBM KB generation is light numpy (edge sampling) done once per
(V,n_ops,K) group. Chains batched; within-chain hops sequential (genuine dependency). Storage strategy:
sharded (each operator its own W matrix; M a learned value operator; R a derived reach matrix). No bundled
store. FULL strongly prefers overnight_queue (GPU): matmul-heavy SR-TD + eigh per group.
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line + per
(seed,V,n_ops,K) heartbeat; FULL timeout_s >= 1800).

USER-LOCKED FRAMING: NARROW glass-box sub-goal-discovery PRIMITIVE step. A HARD_PASS means only "given a
trained SR over a small known state space WITH room/door structure, the substrate can propose its own
waypoints." Honest tier throughout; no smoke; deflate claims not ambition.

Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-08_pfc_gate_waypoint_discovery_structured_kb_v1.md
Cites:
  data/exp_pfc_gate_autonomous_waypoint_discovery_v1/metrics.json (parent ER HARD_FAIL; rails; measured signs)
  experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py (ALL mechanism primitives, imported verbatim)
  notes/research_hierarchical_subgoal_discovery_sr_eigenoption_brain_first_2026-07-08.md (grounding + SBM fix)
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
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
    assert_discriminator_fires, VacuousSmokeError,
)

# ---- MECHANISM PRIMITIVES: imported VERBATIM from the parent (byte-identical; zero mechanism change) ----
from experiments.exp_pfc_gate_autonomous_waypoint_discovery_v1 import (
    DEVICE, DTYPE, SEG_LEN, CAND_FRAC, GAMMA,
    make_bipolar_E, hebbian_W, cleanup_batched,
    build_adjacency, collect_rollout_transitions,
    train_sr_transport, reach_value, build_reach_matrix, codebook_selfcos,
    spectral_candidate_mask, cluster_candidate_mask,
    oracle_trajectory_idx, build_waypoint_idx,
    _chain_tensors, run_selection_arm, run_oracle_arm, run_hier_arm_wp,
    wp_hops_open, wp_hops_masked, wp_hops_random, wp_hops_index, wp_hops_oracle,
    discovery_diagnostics, reach_rank_acc,
    binom_two_sided_p, _spearman, decision_entropy, n_boundaries,
    _tune_alpha_hier_oracle, _tune_wreach_flat, _tune_wreach_hier_wp,
)

ANCHOR_NAME = "pfc_gate_waypoint_discovery_structured_kb_v1"

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

# --------------------------- pre-reg bands (LOCKED at import; PROSPECTIVE) --------
# HEADLINE sign-flip band (the load-bearing new discriminator):
HP_SIGNFLIP_MARGIN = 0.05         # HARD_PASS: best(spec,clus) beats open by >= 5 points
HP_SIGNFLIP_SIGN_P = 0.05         # paired per-chain sign test of that arm vs open significant
# ORIGINAL absolute bars (inherited from parent, applied to best_wp = max(open,spec,clus)):
HP_RECOVERY_RATIO_FLOOR = 0.20    # best_wp recovers >= 20% of the oracle-DECOMPOSITION benefit
HP_LIFT_FLAT_MIN = 0.05           # real lift over no-hierarchy flat
HP_LIFT_RANDOM_MIN = 0.10         # real lift over a noise waypoint (mechanism-fires gate)
HP_INDEX_GAP_MAX = 0.05           # no structural index-order leak
HP_ANTI_TAUT_CORR_MAX = 0.85      # balance score is dynamics, not target-cosine in disguise
HP_DEGENERATE_MAX = 0.10          # bisection does not degenerate to picking start/goal
HP_CV_MAX = 0.10                  # cross-seed cv on best_wp at focus (FULL only)
INDEX_LEAK_GAP = 0.10             # INCONCLUSIVE: index beats random by > this ...
INDEX_LEAK_P = 0.05               # ... with paired sign p < this
# RAILS (discriminator-fires; smoke-enforced):
ORACLE_RAIL_MIN = 0.90            # FOCUS: perfect-execution ceiling reachable
FLAT_MUST_FAIL_CEIL = 0.50        # discriminator-fires: flat MUST collapse below this at FOCUS
HIER_MUST_SUCCEED_MIN = 0.55      # discriminator-fires: hier_oracle MUST succeed above this at FOCUS
HEADROOM_EXEC_MIN = 0.10          # FOCUS: flat->perfect gap measurable
HEADROOM_DECOMP_MIN = 0.10        # FOCUS: oracle-decomposition benefit measurable
# SBM GENERATOR structure gate (saturation-vacuous guard ON THE GENERATOR):
Q_MIN = 0.20                      # modularity Q of the generated state graph (block partition)
RATIO_MIN = 5.0                   # within:between edge ratio (the 5-10x the drill specified)

# --------------------------- SBM generator params --------------------------
DENSITY = 0.21                    # bulk triples per op = round(DENSITY * V) (IDENTICAL to parent)
P_WITHIN = 0.90                   # fraction of bulk edges that stay WITHIN a room (the rest = doors)
DOOR_PER_ROOM = 3                 # few door states per room -> a SHARP min-cut / bottleneck
N_CROSS = 2                       # each chain crosses up to this many room boundaries (>=1 forced)

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, K, dd). SR M + R + spectral/cluster masks + graph metrics built once per
# (V,n_ops,K) group; shared across depths. FULL FOCUS = op4_V1200_K4_d8 (matches the parent FOCUS
# corner op4_V1200_d8 with K=4 rooms added; the like-for-like before/after).
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    REGIMES = [{"n_ops": 4, "V": 40, "K": 2, "dd": 4}]
    N_TRAIN_CHAINS = 16
    N_TEST_CHAINS = 12
    SR_STEPS = 150
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 30
elif RUN_MODE == "smoke":
    # multi-seed (3). op4 focus, V=300, K=4 rooms, depth {6,8}. Fires the rails (flat collapses;
    # hier_oracle strong) + reports the SIGN of spec-open + the SBM modularity at matched op/K.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    REGIMES = [{"n_ops": 4, "V": 300, "K": 4, "dd": 6},
               {"n_ops": 4, "V": 300, "K": 4, "dd": 8}]   # FOCUS: high-branch deep, flat collapses
    N_TRAIN_CHAINS = 64
    N_TEST_CHAINS = 64
    SR_STEPS = 400
    SR_BATCH = 64
    SR_LR = 0.5
    ROLLOUT_PER_V = 12
else:  # full
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"n_ops": 4, "V": 1200, "K": 4, "dd": 6}, {"n_ops": 4, "V": 1200, "K": 4, "dd": 8},
               {"n_ops": 4, "V": 1200, "K": 8, "dd": 6}, {"n_ops": 4, "V": 1200, "K": 8, "dd": 8}]
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000

# SR-budget probe overrides (defaults leave every canonical config UNCHANGED).
SR_STEPS = int(os.environ.get("HDLAB_SR_STEPS", str(SR_STEPS)))
ROLLOUT_PER_V = int(os.environ.get("HDLAB_ROLLOUT_PER_V", str(ROLLOUT_PER_V)))
ROLLOUT_CAP = int(os.environ.get("HDLAB_ROLLOUT_CAP", str(ROLLOUT_CAP)))

ARMS = ["flat_gonogo", "oracle_exec", "hier_oracle", "hier_shuffled",
        "wp_bisect_open", "wp_bisect_spectral", "wp_bisect_cluster_exit",
        "wp_random_state", "wp_index_midpoint"]
WP_BISECT_ARMS = ["wp_bisect_open", "wp_bisect_spectral", "wp_bisect_cluster_exit"]


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


def regime_key(n_ops: int, V: int, K: int, dd: int) -> str:
    return "op%d_V%d_K%d_d%d" % (n_ops, V, K, dd)


def group_key(n_ops: int, V: int, K: int) -> str:
    return "op%d_V%d_K%d" % (n_ops, V, K)


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["K"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,seeds=%s,gamma=%.2f,seg_len=%d,cand_frac=%.2f,regimes=%s,density=%.3f,"
    "p_within=%.2f,door_per_room=%d,n_cross=%d,sr_steps=%d,sr_batch=%d,rollout_per_V=%d,lr=%.2f,"
    "n_train=%d,n_test=%d,mode=%s,device=%s,expected_n=%d,HP_signflip>=%.2f,sign_p<%.2f,"
    "HP_recov>=%.2f,lift_flat>%.2f,lift_rand>%.2f,Q_min>=%.2f,ratio_min>=%.1f"
) % (
    ANCHOR_NAME, N_DIM, SEEDS, GAMMA, SEG_LEN, CAND_FRAC, REGIME_KEYS, DENSITY,
    P_WITHIN, DOOR_PER_ROOM, N_CROSS, SR_STEPS, SR_BATCH, ROLLOUT_PER_V, SR_LR,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_SIGNFLIP_MARGIN, HP_SIGNFLIP_SIGN_P, HP_RECOVERY_RATIO_FLOOR, HP_LIFT_FLAT_MIN,
    HP_LIFT_RANDOM_MIN, Q_MIN, RATIO_MIN,
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
        "elapsed_s": round(time.time() - _T0, 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }
    try:
        _atomic_write_metrics(out_dir, diag)
    except Exception as e:
        print("[_write_crash_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _heartbeat(out_dir: Path, unit_idx: int, total: int, note: str = "") -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
               "total_units": total, "elapsed_s": round(time.time() - _T0, 1), "note": note}
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ============================================================================
# NEW: stochastic-block-model (room + door) KB generator + graph structure metrics
# ============================================================================
def _block_of(s: int, room_size: int, K: int) -> int:
    b = s // room_size
    return b if b < K else K - 1


def make_kb_and_chains_sbm(n_ops: int, V: int, K_rooms: int,
                           n_train_chains: int, n_test_chains: int,
                           depths: List[int], g: np.random.Generator
                           ) -> Tuple[List[List[Tuple[int, int]]],
                                      Dict[int, List[Tuple[int, List[int], int]]],
                                      Dict[int, List[Tuple[int, List[int], int]]]]:
    """SBM room-graph KB. Rooms are a LINE 0-1-...-(K-1); most edges stay WITHIN a room (dense),
    a small door-set (DOOR_PER_ROOM states) per room carries the sparse between-room ("door") edges
    between adjacent rooms -- the min-cut bottleneck states the low-frequency eigenvector should cut.
    Chains are constructed to SPAN rooms (start room != goal room), crossing only through doors, so the
    door state IS the natural subgoal. Same signature/consumption contract as the parent make_kb_and_chains
    (returns per_op_triples, train_by_depth, test_by_depth) so ALL downstream primitives are reused verbatim.
    """
    room_size = max(1, V // K_rooms)

    def blk(s: int) -> int:
        return _block_of(s, room_size, K_rooms)

    # door states: first DOOR_PER_ROOM states of each room
    doors: Dict[int, List[int]] = {}
    for r in range(K_rooms):
        lo = r * room_size
        hi = min((r + 1) * room_size, V)
        dp = min(DOOR_PER_ROOM, max(1, hi - lo))
        doors[r] = list(range(lo, lo + dp))

    per_op: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]

    # 1) bulk edges: within-room dense (P_WITHIN) + sparse door edges to an adjacent room.
    n_bulk = n_triples_per_op(V)
    for op in range(n_ops):
        for _ in range(n_bulk):
            s = int(g.integers(0, V))
            r = blk(s)
            if g.random() < P_WITHIN:
                lo = r * room_size
                hi = min((r + 1) * room_size, V)
                o = int(g.integers(lo, hi))
            else:
                # cross to an adjacent room via doors (route both endpoints through door-sets)
                if r == 0:
                    nr = 1 if K_rooms > 1 else 0
                elif r == K_rooms - 1:
                    nr = K_rooms - 2
                else:
                    nr = r + 1 if g.random() < 0.5 else r - 1
                if nr == r:
                    continue
                s = int(g.choice(doors[r]))
                o = int(g.choice(doors[nr]))
            if s != o:
                per_op[op].append((s, o))

    def _grow_chain(depth: int) -> Tuple[int, List[int], int]:
        # start in a room with forward headroom so the chain can cross at least one boundary
        r0 = int(g.integers(0, max(1, K_rooms - 1)))
        lo0 = r0 * room_size
        hi0 = min((r0 + 1) * room_size, V)
        s = int(g.integers(lo0, hi0))
        cur = s
        room = r0
        max_cross = min(N_CROSS, K_rooms - 1 - r0)
        n_c = int(g.integers(1, max_cross + 1)) if max_cross >= 1 else 0
        if n_c > 0 and depth > 0:
            n_c = min(n_c, depth)
            cross_hops = set(int(x) for x in g.choice(depth, size=n_c, replace=False))
        else:
            cross_hops = set()
        op_seq: List[int] = []
        for h in range(depth):
            op = int(g.integers(0, n_ops))
            if h in cross_hops and room < K_rooms - 1:
                o = int(g.choice(doors[room + 1]))
                if o == cur:
                    o = int(g.choice(doors[room + 1]))
                per_op[op].append((cur, o))          # door edge (records cur as an effective door)
                cur = o
                room = room + 1
            else:
                cands = [o for (ss, o) in per_op[op] if ss == cur and blk(o) == room]
                if cands:
                    cur = int(cands[g.integers(0, len(cands))])
                else:
                    lo = room * room_size
                    hi = min((room + 1) * room_size, V)
                    new_o = int(g.integers(lo, hi))
                    tries = 0
                    while new_o == cur and tries < 6:
                        new_o = int(g.integers(lo, hi))
                        tries += 1
                    per_op[op].append((cur, new_o))
                    cur = new_o
            op_seq.append(op)
        return (s, op_seq, cur)

    train_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    test_by_d: Dict[int, List[Tuple[int, List[int], int]]] = {}
    for depth in depths:
        train_by_d[depth] = [_grow_chain(depth) for _ in range(n_train_chains)]
        test_by_d[depth] = [_grow_chain(depth) for _ in range(n_test_chains)]
    return per_op, train_by_d, test_by_d


def graph_structure_metrics(per_op: List[List[Tuple[int, int]]], V: int, K_rooms: int
                            ) -> Dict[str, float]:
    """Generator-level saturation-vacuous GUARD: Newman modularity Q of the generated state graph under
    the room-block partition + within:between DENSITY ratio. Treats the union of all operator (s,o) edges
    as an undirected multigraph. The DENSITY ratio (per-eligible-pair edge probability within vs between
    rooms) is the theoretically meaningful "5-10x" quantity from the drill/Solway -- it normalizes for the
    fact that cross-room ordered pairs vastly outnumber within-room pairs (a uniform-random ER graph has
    density_ratio == 1.0 and Q ~ 0). High Q + high density_ratio == the generator produced real room/door
    structure; a green arm result on a low-Q graph is on a secretly-uniform graph and must be rejected."""
    room_size = max(1, V // K_rooms)
    # actual per-room sizes (last room absorbs the remainder)
    sizes = np.zeros(K_rooms, dtype=np.float64)
    for s in range(V):
        sizes[_block_of(s, room_size, K_rooms)] += 1.0

    def blk(s: int) -> int:
        return _block_of(s, room_size, K_rooms)

    m = 0
    L_within = 0
    L_between = 0
    D_c = np.zeros(K_rooms, dtype=np.float64)
    L_cc = np.zeros(K_rooms, dtype=np.float64)
    for op_edges in per_op:
        for (s, o) in op_edges:
            if s == o:
                continue
            cs = blk(s)
            co = blk(o)
            D_c[cs] += 1.0
            D_c[co] += 1.0
            m += 1
            if cs == co:
                L_within += 1
                L_cc[cs] += 1.0
            else:
                L_between += 1
    if m == 0:
        return {"modularity": 0.0, "within_between_density_ratio": 0.0, "within_between_count_ratio": 0.0,
                "n_edges": 0, "n_within": 0, "n_between": 0, "K_rooms": int(K_rooms)}
    two_m = 2.0 * m
    Q = 0.0
    for c in range(K_rooms):
        Q += (L_cc[c] / m) - (D_c[c] / two_m) ** 2
    # eligible ordered-pair counts within vs between rooms
    within_pairs = float(np.sum(sizes * (sizes - 1.0)))
    total_pairs = float(V) * float(V - 1)
    between_pairs = max(1.0, total_pairs - within_pairs)
    within_pairs = max(1.0, within_pairs)
    within_density = float(L_within) / within_pairs
    between_density = float(L_between) / between_pairs
    density_ratio = within_density / max(1e-12, between_density)
    count_ratio = float(L_within) / float(max(1, L_between))
    return {"modularity": float(Q), "within_between_density_ratio": float(density_ratio),
            "within_between_count_ratio": float(count_ratio), "within_density": float(within_density),
            "between_density": float(between_density), "n_edges": int(m), "n_within": int(L_within),
            "n_between": int(L_between), "K_rooms": int(K_rooms)}


def reach_spectral_gap(R: torch.Tensor, K_rooms: int) -> float:
    """SBM recovery diagnostic (Massoulie 2014; Mossel-Neeman-Sly 2015): gap between the K-th and
    (K+1)-th top eigenvalues of the symmetrized reach affinity. A clean K-block structure shows a gap."""
    try:
        S = 0.5 * (R + R.transpose(0, 1))
        evals = torch.linalg.eigvalsh(S)            # ascending
        ev = evals.detach().cpu().numpy()[::-1]     # descending
        if len(ev) <= K_rooms:
            return 0.0
        return float(ev[K_rooms - 1] - ev[K_rooms])
    except Exception:
        return 0.0


# ============================================================================
# per-regime eval (arm execution primitives imported verbatim; only spec/clus paired
# sign counts are new bookkeeping)
# ============================================================================
def _eval_regime_sbm(n_ops: int, V: int, K: int, dd: int, E: torch.Tensor,
                     W_ops: List[torch.Tensor], M: torch.Tensor, R: torch.Tensor, C: torch.Tensor,
                     spec_mask: torch.Tensor, clus_mask: torch.Tensor,
                     train_by_d, test_by_d, g: np.random.Generator) -> Dict[str, Any]:
    """Tune on train, evaluate all 9 arms on test (paired). One seed, gamma fixed. Mirrors the parent's
    _eval_regime but adds paired per-chain spec-vs-open / clus-vs-open sign counts (the headline)."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    best_alpha, _ = _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd)

    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    wp_shuf_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=True)
    wp_open_tr = wp_hops_open(train_c, R, dd)

    wr_flat, _ = _tune_wreach_flat(train_c, W_ops, E, M, dd, best_alpha)
    wr_oracle, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_oracle_tr)
    wr_shuf, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_shuf_tr)
    wr_open, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_open_tr)

    wp_oracle_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=False)
    wp_shuf_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=True)
    wp_open_te = wp_hops_open(test_c, R, dd)
    wp_spec_te = wp_hops_masked(test_c, R, dd, spec_mask)
    wp_clus_te = wp_hops_masked(test_c, R, dd, clus_mask)
    wp_rand_te = wp_hops_random(test_c, V, dd, g)
    wp_idx_te = wp_hops_index(test_c, V, dd)

    flat_c, flat_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, wr_flat)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)
    ho_c, ho_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_oracle, wp_oracle_te)
    hs_c, hs_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_shuf, wp_shuf_te)
    op_c, op_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_open_te)
    sp_c, sp_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_spec_te)
    cl_c, cl_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_clus_te)
    rd_c, rd_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_rand_te)
    ix_c, ix_tr = run_hier_arm_wp(test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, wr_open, wp_idx_te)

    arms: Dict[str, float] = {
        "flat_gonogo": float(flat_c.mean()), "oracle_exec": float(orc_c.mean()),
        "hier_oracle": float(ho_c.mean()), "hier_shuffled": float(hs_c.mean()),
        "wp_bisect_open": float(op_c.mean()), "wp_bisect_spectral": float(sp_c.mean()),
        "wp_bisect_cluster_exit": float(cl_c.mean()), "wp_random_state": float(rd_c.mean()),
        "wp_index_midpoint": float(ix_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "flat_gonogo": hashlib.sha256(flat_tr.tobytes()).hexdigest()[:16],
        "oracle_exec": "oracle_true_seq",
        "hier_oracle": hashlib.sha256(ho_tr.tobytes()).hexdigest()[:16],
        "hier_shuffled": hashlib.sha256(hs_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_open": hashlib.sha256(op_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_spectral": hashlib.sha256(sp_tr.tobytes()).hexdigest()[:16],
        "wp_bisect_cluster_exit": hashlib.sha256(cl_tr.tobytes()).hexdigest()[:16],
        "wp_random_state": hashlib.sha256(rd_tr.tobytes()).hexdigest()[:16],
        "wp_index_midpoint": hashlib.sha256(ix_tr.tobytes()).hexdigest()[:16],
    }

    diag = discovery_diagnostics(test_c, R, C, dd, W_ops, E, SEG_LEN)
    rr_test = reach_rank_acc(test_c, W_ops, E, M, dd)

    bisect_means = {a: arms[a] for a in WP_BISECT_ARMS}
    best_wp_arm = max(bisect_means, key=lambda k: bisect_means[k])
    best_c = {"wp_bisect_open": op_c, "wp_bisect_spectral": sp_c, "wp_bisect_cluster_exit": cl_c}[best_wp_arm]

    paired = {
        "n_bwp_only_vs_flat": int((best_c & (~flat_c)).sum()),
        "n_flat_only_vs_bwp": int((flat_c & (~best_c)).sum()),
        "n_bwp_only_vs_rand": int((best_c & (~rd_c)).sum()),
        "n_rand_only_vs_bwp": int((rd_c & (~best_c)).sum()),
        "n_idx_only_vs_rand": int((ix_c & (~rd_c)).sum()),
        "n_rand_only_vs_idx": int((rd_c & (~ix_c)).sum()),
        # NEW: headline paired sign counts (spectral vs open, cluster vs open)
        "n_spec_only_vs_open": int((sp_c & (~op_c)).sum()),
        "n_open_only_vs_spec": int((op_c & (~sp_c)).sum()),
        "n_clus_only_vs_open": int((cl_c & (~op_c)).sum()),
        "n_open_only_vs_clus": int((op_c & (~cl_c)).sum()),
        "n_test": int(len(best_c)),
    }

    return {
        "n_ops": n_ops, "V": V, "K": K, "dd": dd,
        "entropy": decision_entropy(n_ops, dd), "arms": arms,
        "op_trace_hashes": op_trace_hashes, "best_wp_arm": best_wp_arm,
        "best_alpha": float(best_alpha), "wr_flat": float(wr_flat), "wr_oracle": float(wr_oracle),
        "wr_shuf": float(wr_shuf), "wr_open": float(wr_open),
        "reach_rank_chance": 1.0 / float(n_ops), "reach_rank_test": float(rr_test),
        "degenerate_rate": float(diag["degenerate_rate"]),
        "anti_tautology_corr": float(diag["anti_tautology_corr"]),
        "exact_match_rate": float(diag["exact_match_rate"]), "paired": paired,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    by_group: Dict[Tuple[int, int, int], List[int]] = {}
    for r in REGIMES:
        by_group.setdefault((r["V"], r["n_ops"], r["K"]), []).append(r["dd"])

    regime_results: Dict[str, Any] = {}
    sr_diag_by_group: Dict[str, Any] = {}
    graph_metrics_by_group: Dict[str, Any] = {}
    for (V, n_ops, K) in sorted(by_group.keys()):
        depths_needed = sorted(set(by_group[(V, n_ops, K)]))
        tgen = torch.Generator(device=DEVICE)
        tgen.manual_seed(int(seed) * 100003 + int(V) * 31 + int(n_ops) * 7 + int(K))
        E = make_bipolar_E(V, N_DIM, tgen)
        per_op, train_by_d, test_by_d = make_kb_and_chains_sbm(
            n_ops, V, K, N_TRAIN_CHAINS, N_TEST_CHAINS, depths_needed, g)
        W_ops = [hebbian_W(per_op[i], E, N_DIM) for i in range(n_ops)]
        adj = build_adjacency(per_op, n_ops)

        gmet = graph_structure_metrics(per_op, V, K)
        graph_metrics_by_group[group_key(n_ops, V, K)] = gmet

        max_len = max(depths_needed) + 2
        transitions = collect_rollout_transitions(adj, n_ops, V, rollout_count(V), max_len, g)

        sr_gen = torch.Generator(device=DEVICE)
        sr_gen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3 + int(K) * 5)
        M, sr_diag = train_sr_transport(E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
        sr_diag_by_group[group_key(n_ops, V, K)] = sr_diag

        R = build_reach_matrix(E, M)
        C = codebook_selfcos(E)
        gmet["reach_spectral_gap"] = reach_spectral_gap(R, K)
        try:
            spec_mask = spectral_candidate_mask(R, CAND_FRAC)
            clus_mask = cluster_candidate_mask(R, K, CAND_FRAC)
        except Exception as e:
            print("[seed=%d op%d V=%d K=%d] SPECTRAL_MASK_FAIL %s: %s -> fallback all-True"
                  % (seed, n_ops, V, K, type(e).__name__, e), file=sys.stderr, flush=True)
            spec_mask = torch.ones(V, dtype=torch.bool, device=DEVICE)
            clus_mask = torch.ones(V, dtype=torch.bool, device=DEVICE)
            sr_diag["spectral_mask_failure_class"] = type(e).__name__

        print("[seed=%d op%d V=%d K=%d] SR: err %s->%s M_norm=%.3f n_trans=%d | Q=%.3f dratio=%.2f "
              "cratio=%.2f n_edges=%d (within=%d between=%d) specgap=%.4f spec_k=%d clus_k=%d"
              % (seed, n_ops, V, K, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
                 sr_diag["n_transitions"], gmet["modularity"], gmet["within_between_density_ratio"],
                 gmet["within_between_count_ratio"], gmet["n_edges"], gmet["n_within"], gmet["n_between"],
                 gmet["reach_spectral_gap"], int(spec_mask.sum()), int(clus_mask.sum())), flush=True)

        for dd in depths_needed:
            rec = _eval_regime_sbm(n_ops, V, K, dd, E, W_ops, M, R, C, spec_mask, clus_mask,
                                   train_by_d, test_by_d, g)
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(n_ops, V, K, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s ent=%.2f] FLAT=%.3f OEXEC=%.3f HORC=%.3f SHUF=%.3f | "
                  "OPEN=%.3f SPEC=%.3f CLUS=%.3f RAND=%.3f IDX=%.3f (spec-open=%.3f clus-open=%.3f "
                  "degen=%.3f taut=%.3f exact=%.3f best=%s)"
                  % (seed, key, rec["entropy"], a["flat_gonogo"], a["oracle_exec"], a["hier_oracle"],
                     a["hier_shuffled"], a["wp_bisect_open"], a["wp_bisect_spectral"],
                     a["wp_bisect_cluster_exit"], a["wp_random_state"], a["wp_index_midpoint"],
                     a["wp_bisect_spectral"] - a["wp_bisect_open"],
                     a["wp_bisect_cluster_exit"] - a["wp_bisect_open"], rec["degenerate_rate"],
                     rec["anti_tautology_corr"], rec["exact_match_rate"], rec["best_wp_arm"]), flush=True)

    return {
        "seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "regime_results": regime_results, "sr_diag_by_group": sr_diag_by_group,
        "graph_metrics_by_group": graph_metrics_by_group,
    }


# ============================================================================
# aggregate + verdict (sign-flip headline + SBM structure gate + rails)
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
        return [float(per_seed[k]["regime_results"][rk][field]) for k in _present(rk)]

    def _pair_sum(rk, present, fld):
        return sum(int(per_seed[k]["regime_results"][rk]["paired"][fld]) for k in present)

    def _group_gmet(n_ops, V, K, field):
        gk = group_key(n_ops, V, K)
        vals = [per_seed[k]["graph_metrics_by_group"][gk][field]
                for k in keys if gk in per_seed[k].get("graph_metrics_by_group", {})
                and field in per_seed[k]["graph_metrics_by_group"][gk]]
        return _mean([float(v) for v in vals]) if vals else 0.0

    per_regime: Dict[str, Any] = {}
    completed_units = 0
    for r in REGIMES:
        rk = regime_key(r["n_ops"], r["V"], r["K"], r["dd"])
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
        open_m = arm_means["wp_bisect_open"]
        spec_m = arm_means["wp_bisect_spectral"]
        clus_m = arm_means["wp_bisect_cluster_exit"]

        bisect = {a: arm_means[a] for a in WP_BISECT_ARMS}
        best_wp_arm = max(bisect, key=lambda k: bisect[k])
        best_wp = bisect[best_wp_arm]

        headroom_exec = oexec - flat
        headroom_decomp = horc - flat
        recovery_ratio = ((best_wp - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        autonomous_closure = ((best_wp - flat) / headroom_exec) if headroom_exec > 1e-6 else 0.0
        lift_flat = best_wp - flat
        lift_random = best_wp - rand
        index_artifact_gap = idxm - rand
        spectral_minus_open = spec_m - open_m
        cluster_minus_open = clus_m - open_m

        # headline sign-flip: the better of the two restricted arms over open
        if spectral_minus_open >= cluster_minus_open:
            signflip_arm = "wp_bisect_spectral"
            best_signflip = spectral_minus_open
        else:
            signflip_arm = "wp_bisect_cluster_exit"
            best_signflip = cluster_minus_open

        degen = _mean(_field_col(rk, "degenerate_rate"))
        anti_taut = _mean(_field_col(rk, "anti_tautology_corr"))
        exact = _mean(_field_col(rk, "exact_match_rate"))
        rr_test = _mean(_field_col(rk, "reach_rank_test"))
        entropy = decision_entropy(r["n_ops"], r["dd"])

        # pooled paired sign tests
        n_bwp_only = _pair_sum(rk, present, "n_bwp_only_vs_flat")
        n_flat_only = _pair_sum(rk, present, "n_flat_only_vs_bwp")
        n_disc = n_bwp_only + n_flat_only
        sign_p_bwp_flat = binom_two_sided_p(n_bwp_only, n_disc, 0.5) if n_disc > 0 else 1.0

        n_spec_only = _pair_sum(rk, present, "n_spec_only_vs_open")
        n_open_only_s = _pair_sum(rk, present, "n_open_only_vs_spec")
        n_disc_spec = n_spec_only + n_open_only_s
        sign_p_spec = binom_two_sided_p(n_spec_only, n_disc_spec, 0.5) if n_disc_spec > 0 else 1.0

        n_clus_only = _pair_sum(rk, present, "n_clus_only_vs_open")
        n_open_only_c = _pair_sum(rk, present, "n_open_only_vs_clus")
        n_disc_clus = n_clus_only + n_open_only_c
        sign_p_clus = binom_two_sided_p(n_clus_only, n_disc_clus, 0.5) if n_disc_clus > 0 else 1.0

        signflip_sign_p = sign_p_spec if signflip_arm == "wp_bisect_spectral" else sign_p_clus

        n_idx_only = _pair_sum(rk, present, "n_idx_only_vs_rand")
        n_rand_only_idx = _pair_sum(rk, present, "n_rand_only_vs_idx")
        n_disc_idx = n_idx_only + n_rand_only_idx
        idx_sign_p = binom_two_sided_p(n_idx_only, n_disc_idx, 0.5) if n_disc_idx > 0 else 1.0

        # arms-differ (AF)
        af_collision = False
        for k in present:
            rr = per_seed[k]["regime_results"][rk]
            h = rr["op_trace_hashes"]
            bwp = rr["best_wp_arm"]
            if h[bwp] == h["flat_gonogo"] or h[bwp] == h["wp_random_state"]:
                af_collision = True
            if h["hier_oracle"] == h["hier_shuffled"]:
                af_collision = True

        # SBM structure gate (generator-level; averaged across seeds)
        modularity = _group_gmet(r["n_ops"], r["V"], r["K"], "modularity")
        wb_ratio = _group_gmet(r["n_ops"], r["V"], r["K"], "within_between_density_ratio")
        wb_count_ratio = _group_gmet(r["n_ops"], r["V"], r["K"], "within_between_count_ratio")
        spec_gap = _group_gmet(r["n_ops"], r["V"], r["K"], "reach_spectral_gap")
        sbm_ok = bool(modularity >= Q_MIN and wb_ratio >= RATIO_MIN)

        oracle_rail_ok = bool(oexec >= ORACLE_RAIL_MIN)
        flat_collapsed = bool(flat < FLAT_MUST_FAIL_CEIL)
        hier_succeeded = bool(horc > HIER_MUST_SUCCEED_MIN)
        headroom_exec_ok = bool(headroom_exec >= HEADROOM_EXEC_MIN)
        headroom_decomp_ok = bool(headroom_decomp >= HEADROOM_DECOMP_MIN)
        bwp_cv = arm_cvs[best_wp_arm]

        # absolute (original) bars on best_wp
        abs_bars_ok = (recovery_ratio >= HP_RECOVERY_RATIO_FLOOR
                       and lift_flat > HP_LIFT_FLAT_MIN and lift_random > HP_LIFT_RANDOM_MIN
                       and index_artifact_gap < HP_INDEX_GAP_MAX and anti_taut < HP_ANTI_TAUT_CORR_MAX
                       and degen < HP_DEGENERATE_MAX and (bwp_cv < HP_CV_MAX or RUN_MODE != "full")
                       and not af_collision)
        signflip_ok = bool(best_signflip >= HP_SIGNFLIP_MARGIN and signflip_sign_p < HP_SIGNFLIP_SIGN_P)
        rails_ok = bool(oracle_rail_ok and flat_collapsed and hier_succeeded
                        and headroom_exec_ok and headroom_decomp_ok)

        hp_ok = bool(rails_ok and sbm_ok and signflip_ok and abs_bars_ok)
        index_leak = bool(index_artifact_gap > INDEX_LEAK_GAP and idx_sign_p < INDEX_LEAK_P)

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "K": r["K"], "dd": r["dd"], "n_seeds": n_present,
            "entropy": entropy, "arm_means": arm_means, "arm_cvs": arm_cvs,
            "flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
            "wp_random_state": rand, "wp_index_midpoint": idxm,
            "wp_bisect_open": open_m, "wp_bisect_spectral": spec_m, "wp_bisect_cluster_exit": clus_m,
            "best_wp_arm": best_wp_arm, "best_wp": float(best_wp),
            "signflip_arm": signflip_arm, "best_signflip": float(best_signflip),
            "signflip_sign_p": float(signflip_sign_p),
            "spectral_minus_open": float(spectral_minus_open),
            "cluster_minus_open": float(cluster_minus_open),
            "sign_p_spec": float(sign_p_spec), "sign_p_clus": float(sign_p_clus),
            "headroom_exec": float(headroom_exec), "headroom_decomp": float(headroom_decomp),
            "autonomous_closure": float(autonomous_closure), "recovery_ratio": float(recovery_ratio),
            "lift_flat": float(lift_flat), "lift_random": float(lift_random),
            "index_artifact_gap": float(index_artifact_gap),
            "degenerate_rate": float(degen), "anti_tautology_corr": float(anti_taut),
            "exact_match_rate": float(exact), "reach_rank_test": float(rr_test),
            "sign_test_p_bwp_flat": float(sign_p_bwp_flat), "idx_sign_p": float(idx_sign_p),
            "modularity": float(modularity), "within_between_ratio": float(wb_ratio),
            "within_between_count_ratio": float(wb_count_ratio),
            "reach_spectral_gap": float(spec_gap), "sbm_ok": sbm_ok,
            "oracle_rail_ok": oracle_rail_ok, "flat_collapsed": flat_collapsed,
            "hier_succeeded": hier_succeeded, "headroom_exec_ok": headroom_exec_ok,
            "headroom_decomp_ok": headroom_decomp_ok, "rails_ok": rails_ok, "bwp_cv": float(bwp_cv),
            "af_collision": bool(af_collision), "index_leak": index_leak,
            "signflip_ok": signflip_ok, "abs_bars_ok": bool(abs_bars_ok), "hp_ok": hp_ok,
        }

    # focus = highest-entropy regime with rails held
    cardinality_ok = completed_units >= EXPECTED_N_UNITS
    discriminating = {rk: v for rk, v in per_regime.items() if v["rails_ok"] and v["n_seeds"] > 0}
    focus_rk = None
    if discriminating:
        focus_rk = max(discriminating.keys(),
                       key=lambda rk: (per_regime[rk]["entropy"], per_regime[rk]["V"],
                                       per_regime[rk]["dd"]))
    fv = per_regime[focus_rk] if focus_rk is not None else None

    hp_ok_keys = [rk for rk, v in per_regime.items() if v["hp_ok"] and v["n_seeds"] > 0]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif fv is None:
        verdict = "INCONCLUSIVE_NO_DISCRIMINATING_REGIME"
    elif not fv["sbm_ok"]:
        verdict = "HARD_FAIL_SBM_NO_STRUCTURE_GENERATOR_VACUOUS"
    elif fv["index_leak"]:
        verdict = "INCONCLUSIVE_INDEX_ORDER_LEAK"
    elif fv["hp_ok"]:
        verdict = "HARD_PASS"
    elif fv["best_signflip"] > 0.0 and fv["signflip_sign_p"] < HP_SIGNFLIP_SIGN_P:
        verdict = "MIDDLE_BAND_SIGNFLIP_MISSES_FULL_BARS"
    else:
        verdict = "HARD_FAIL_SR_CANNOT_DETECT_BOTTLENECK_EVEN_WITH_STRUCTURE"

    grid_str = " ".join(
        "%s(e%.1f:F%.2f/HO%.2f/OPEN%.2f/SPEC%.2f/CLUS%.2f/RAND%.2f Q%.2f)" % (
            rk, per_regime[rk]["entropy"], per_regime[rk]["flat_gonogo"], per_regime[rk]["hier_oracle"],
            per_regime[rk]["wp_bisect_open"], per_regime[rk]["wp_bisect_spectral"],
            per_regime[rk]["wp_bisect_cluster_exit"], per_regime[rk]["wp_random_state"],
            per_regime[rk]["modularity"])
        for rk in REGIME_KEYS if rk in per_regime and per_regime[rk]["n_seeds"] > 0)

    if fv is not None:
        head = ("%s | FOCUS=%s(ent=%.1f) FLAT=%.3f OEXEC=%.3f HIER_ORACLE=%.3f RAND=%.3f | "
                "OPEN=%.3f SPEC=%.3f CLUS=%.3f | best_signflip=%s=%.3f sign_p=%.4g | "
                "recovery=%.3f lift_flat=%.3f lift_random=%.3f | Q=%.3f ratio=%.2f specgap=%.4f | "
                "degen=%.3f taut=%.3f rails_ok=%s sbm_ok=%s | GRID [%s] n_seeds=%d n_hp_ok=%d") % (
            verdict, focus_rk, fv["entropy"], fv["flat_gonogo"], fv["oracle_exec"], fv["hier_oracle"],
            fv["wp_random_state"], fv["wp_bisect_open"], fv["wp_bisect_spectral"],
            fv["wp_bisect_cluster_exit"], fv["signflip_arm"], fv["best_signflip"], fv["signflip_sign_p"],
            fv["recovery_ratio"], fv["lift_flat"], fv["lift_random"], fv["modularity"],
            fv["within_between_ratio"], fv["reach_spectral_gap"], fv["degenerate_rate"],
            fv["anti_tautology_corr"], fv["rails_ok"], fv["sbm_ok"], grid_str, len(keys), len(hp_ok_keys))
    else:
        head = "%s | no discriminating regime | GRID [%s] n_seeds=%d" % (verdict, grid_str, len(keys))

    return {
        "verdict": verdict, "verdict_msg": head, "summary": head,
        "per_regime": per_regime, "focus_regime": focus_rk,
        "focus_signflip_arm": (fv["signflip_arm"] if fv else None),
        "focus_best_signflip": (fv["best_signflip"] if fv else None),
        "focus_signflip_sign_p": (fv["signflip_sign_p"] if fv else None),
        "focus_spectral_minus_open": (fv["spectral_minus_open"] if fv else None),
        "focus_cluster_minus_open": (fv["cluster_minus_open"] if fv else None),
        "focus_recovery_ratio": (fv["recovery_ratio"] if fv else None),
        "focus_lift_flat": (fv["lift_flat"] if fv else None),
        "focus_lift_random": (fv["lift_random"] if fv else None),
        "focus_modularity": (fv["modularity"] if fv else None),
        "focus_within_between_ratio": (fv["within_between_ratio"] if fv else None),
        "focus_flat_gonogo": (fv["flat_gonogo"] if fv else None),
        "focus_hier_oracle": (fv["hier_oracle"] if fv else None),
        "focus_oracle_exec": (fv["oracle_exec"] if fv else None),
        "sign_flips_positive": bool(fv["best_signflip"] > 0.0) if fv else False,
        "rails_hold": bool(fv["rails_ok"]) if fv else False,
        "sbm_structure_ok": bool(fv["sbm_ok"]) if fv else False,
        "n_regimes_hp_ok": len(hp_ok_keys), "hp_ok_regime_keys": hp_ok_keys,
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "cv_gate_enforced": bool(RUN_MODE == "full"),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# smoke discriminator-fires gate (rails + SBM structure MUST fire at smoke)
# ============================================================================
def _smoke_discriminator_gate(final: Dict[str, Any]) -> None:
    """MANDATORY at smoke/selftest: the rails MUST fire (flat collapses, hier_oracle succeeds, oracle rail,
    SBM modularity) or the smoke is vacuous. Raises VacuousSmokeError loudly (no green on a dead test)."""
    fv_rk = final.get("focus_regime")
    per_regime = final.get("per_regime", {})
    if fv_rk is None or fv_rk not in per_regime:
        raise VacuousSmokeError(
            "VACUOUS SMOKE: no discriminating regime (rails not met at any regime). "
            "Remedy: raise smoke V/N or fix the SBM generator so flat collapses AND hier_oracle succeeds.")
    fv = per_regime[fv_rk]
    # flat MUST fail (control that must not solve)
    assert_discriminator_fires(
        bool(fv["flat_gonogo"] >= FLAT_MUST_FAIL_CEIL), control_name="flat_gonogo",
        headline_name="solve-the-deep-chain", run_mode=RUN_MODE,
        extra="flat_gonogo=%.3f must be < %.2f (collapse) at FOCUS %s" % (
            fv["flat_gonogo"], FLAT_MUST_FAIL_CEIL, fv_rk))
    # hier_oracle MUST succeed (task solvable given true decomposition)
    if not (fv["hier_oracle"] > HIER_MUST_SUCCEED_MIN):
        raise VacuousSmokeError(
            "VACUOUS SMOKE: hier_oracle=%.3f did not exceed %.2f at FOCUS %s -- the SBM task is not "
            "solvable-with-decomposition at this scale, so any spectral lift is meaningless. Remedy: raise "
            "smoke V/N or reduce depth." % (fv["hier_oracle"], HIER_MUST_SUCCEED_MIN, fv_rk))
    # oracle rail
    if not (fv["oracle_exec"] >= ORACLE_RAIL_MIN):
        raise VacuousSmokeError(
            "VACUOUS SMOKE: oracle_exec=%.3f below rail %.2f at FOCUS %s -- perfect execution unreachable; "
            "the SBM Hebbian recovery is too noisy. Remedy: lower within-room out-degree / raise N."
            % (fv["oracle_exec"], ORACLE_RAIL_MIN, fv_rk))
    # SBM structure gate on the GENERATOR
    if not fv["sbm_ok"]:
        raise VacuousSmokeError(
            "VACUOUS SMOKE (GENERATOR): modularity=%.3f (need>=%.2f) within:between=%.2f (need>=%.1f) at "
            "FOCUS %s -- the SBM generator produced no room/door structure, so a green arm result would be "
            "on a secretly-uniform graph. Remedy: raise P_WITHIN / lower DOOR_PER_ROOM."
            % (fv["modularity"], Q_MIN, fv["within_between_ratio"], RATIO_MIN, fv_rk))
    print("[smoke-gate] rails+structure FIRE at FOCUS %s: flat=%.3f<%.2f hier_oracle=%.3f>%.2f "
          "oracle_exec=%.3f>=%.2f Q=%.3f>=%.2f ratio=%.2f>=%.1f | best_signflip=%.3f (sign_p=%.4g)"
          % (fv_rk, fv["flat_gonogo"], FLAT_MUST_FAIL_CEIL, fv["hier_oracle"], HIER_MUST_SUCCEED_MIN,
             fv["oracle_exec"], ORACLE_RAIL_MIN, fv["modularity"], Q_MIN, fv["within_between_ratio"],
             RATIO_MIN, fv["best_signflip"], fv["signflip_sign_p"]), flush=True)


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gamma=%.2f seg_len=%d cand_frac=%.2f (mechanism imported verbatim)"
          % (DEVICE, GAMMA, SEG_LEN, CAND_FRAC), flush=True)

    # ST_SBM1: SBM generator produces REAL modular structure; chains span rooms
    g = np.random.default_rng(1)
    per_op, tr, te = make_kb_and_chains_sbm(4, 200, 4, 48, 24, [6], g)
    gm = graph_structure_metrics(per_op, 200, 4)
    assert gm["modularity"] >= Q_MIN, "ST_SBM1 modularity too low: %.3f" % gm["modularity"]
    assert gm["within_between_density_ratio"] >= RATIO_MIN, \
        "ST_SBM1 density ratio too low: %.2f" % gm["within_between_density_ratio"]
    room_size = 200 // 4
    span = sum(1 for (s, seq, o) in te[6] if _block_of(s, room_size, 4) != _block_of(o, room_size, 4))
    assert span >= int(0.6 * len(te[6])), "ST_SBM1 chains do not span rooms: %d/%d" % (span, len(te[6]))
    print("[selftest] ST_SBM1 SBM structure OK: Q=%.3f density_ratio=%.2f count_ratio=%.2f "
          "cross_room_chains=%d/%d" % (gm["modularity"], gm["within_between_density_ratio"],
                                       gm["within_between_count_ratio"], span, len(te[6])), flush=True)

    # ST_SBM2: a uniform-random (ER) graph yields LOW modularity (discriminates the metric)
    g2 = np.random.default_rng(2)
    per_op_er = [[] for _ in range(4)]
    for op in range(4):
        for _ in range(int(round(DENSITY * 120))):
            s = int(g2.integers(0, 120)); o = int(g2.integers(0, 120))
            if s != o:
                per_op_er[op].append((s, o))
    gm_er = graph_structure_metrics(per_op_er, 120, 4)
    assert gm_er["modularity"] < 0.15, "ST_SBM2 ER modularity unexpectedly high: %.3f" % gm_er["modularity"]
    print("[selftest] ST_SBM2 ER control low-Q OK: Q_er=%.3f (< 0.15) vs Q_sbm=%.3f"
          % (gm_er["modularity"], gm["modularity"]), flush=True)

    # ST_SBM3: modularity formula sanity on a hand graph (2 disjoint blocks, all-within == Q -> 0.5)
    hand = [[(0, 1), (1, 0), (2, 3), (3, 2)]]   # 2 blocks {0,1},{2,3}, room_size=2, K=2
    gh = graph_structure_metrics(hand, 4, 2)
    assert abs(gh["modularity"] - 0.5) < 1e-6, "ST_SBM3 hand modularity != 0.5: %.4f" % gh["modularity"]
    assert gh["n_between"] == 0, "ST_SBM3 disjoint blocks should have 0 between edges"
    print("[selftest] ST_SBM3 modularity formula OK (disjoint 2-block Q=0.5)", flush=True)

    # ST_VERDICT: verdict wiring for the sign-flip headline
    _verdict_selftest()

    # ST_PIPE: full pipeline single-seed structural (all 9 arms + graph metrics + oracle sane)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_structured_kb")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST_PIPE missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST_PIPE missing arm %s" % arm
    for fld in ("n_spec_only_vs_open", "n_open_only_vs_spec", "n_clus_only_vs_open"):
        assert fld in r["regime_results"][rk0]["paired"], "ST_PIPE missing paired field %s" % fld
    assert r["graph_metrics_by_group"], "ST_PIPE missing graph metrics"
    print("[selftest] ST_PIPE pipeline OK arms=%d groups=%d"
          % (len(ARMS), len(r["graph_metrics_by_group"])), flush=True)
    return 0


def _verdict_selftest() -> None:
    def _mk(n_ops, V, K, dd, flat, oexec, horc, open_a, spec_a, clus_a, rand, idxm,
            degen=0.02, taut=0.10, exact=0.20, rr=0.60,
            n_spec_only=None, n_open_only_s=2, n_idx_only=2, n_rand_only_idx=2):
        best = max(open_a, spec_a, clus_a)
        bwp_arm = ("wp_bisect_open" if open_a == best else
                   ("wp_bisect_spectral" if spec_a == best else "wp_bisect_cluster_exit"))
        if n_spec_only is None:
            n_spec_only = 40 if spec_a > open_a + 0.03 else 3
        arms = {"flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc, "hier_shuffled": 0.02,
                "wp_bisect_open": open_a, "wp_bisect_spectral": spec_a,
                "wp_bisect_cluster_exit": clus_a, "wp_random_state": rand, "wp_index_midpoint": idxm}
        oth = {"flat_gonogo": "f", "oracle_exec": "oracle_true_seq", "hier_oracle": "ho",
               "hier_shuffled": "hs", "wp_bisect_open": "op", "wp_bisect_spectral": "sp",
               "wp_bisect_cluster_exit": "cl", "wp_random_state": "rd", "wp_index_midpoint": "ix"}
        return {"n_ops": n_ops, "V": V, "K": K, "dd": dd, "entropy": decision_entropy(n_ops, dd),
                "arms": arms, "op_trace_hashes": oth, "best_wp_arm": bwp_arm, "best_alpha": 0.2,
                "wr_flat": 1.0, "wr_oracle": 1.0, "wr_shuf": 1.0, "wr_open": 1.0,
                "reach_rank_chance": 1.0 / n_ops, "reach_rank_test": rr, "degenerate_rate": degen,
                "anti_tautology_corr": taut, "exact_match_rate": exact,
                "paired": {"n_bwp_only_vs_flat": 45, "n_flat_only_vs_bwp": 2, "n_bwp_only_vs_rand": 40,
                           "n_rand_only_vs_bwp": 2, "n_idx_only_vs_rand": n_idx_only,
                           "n_rand_only_vs_idx": n_rand_only_idx, "n_spec_only_vs_open": n_spec_only,
                           "n_open_only_vs_spec": n_open_only_s, "n_clus_only_vs_open": 3,
                           "n_open_only_vs_clus": 30, "n_test": 60}}

    def _gm(Q, ratio):
        return {"modularity": Q, "within_between_density_ratio": ratio,
                "within_between_count_ratio": ratio, "n_edges": 1000,
                "n_within": 900, "n_between": 100, "reach_spectral_gap": 0.1}

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    reg_lo = regime_key(4, 1200, 4, 6)
    reg_hi = regime_key(4, 1200, 4, 8)
    gk = group_key(4, 1200, 4)
    REGIMES = [{"n_ops": 4, "V": 1200, "K": 4, "dd": 6}, {"n_ops": 4, "V": 1200, "K": 4, "dd": 8}]
    REGIME_KEYS = [reg_lo, reg_hi]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    try:
        # HARD_PASS: spectral flips positive by >=0.05, sign-significant, rails+structure+abs bars hold.
        #   spec=0.45 open=0.38 -> signflip=+0.07>=0.05; best_wp=spec=0.45; flat=0.08 horc=0.90
        #   recovery=(0.45-0.08)/0.82=0.451>=0.20; lift_flat=0.37; lift_random=0.33; Q=0.5 ratio=9.
        def mkseeds(hi_rec):
            return {s: {"regime_results": {reg_lo: _mk(4, 1200, 4, 6, 0.30, 0.95, 0.90, 0.40, 0.44, 0.42,
                                                       0.25, 0.26), reg_hi: hi_rec},
                        "graph_metrics_by_group": {gk: _gm(0.50, 9.0)}} for s in ["7", "17", "23"]}
        ps = mkseeds(_mk(4, 1200, 4, 8, flat=0.08, oexec=0.94, horc=0.90, open_a=0.38, spec_a=0.45,
                         clus_a=0.40, rand=0.12, idxm=0.13))
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "STV expected HARD_PASS got %s" % out["verdict"]
        assert out["focus_regime"] == reg_hi, "STV focus should be high-entropy"
        assert out["focus_signflip_arm"] == "wp_bisect_spectral", "STV signflip arm should be spectral"

        # HARD_FAIL: no sign flip (spec <= open even with structure)
        ps2 = mkseeds(_mk(4, 1200, 4, 8, flat=0.08, oexec=0.94, horc=0.90, open_a=0.40, spec_a=0.36,
                          clus_a=0.35, rand=0.12, idxm=0.13, n_spec_only=3, n_open_only_s=30))
        out2 = aggregate_and_verdict(ps2)
        assert out2["verdict"] == "HARD_FAIL_SR_CANNOT_DETECT_BOTTLENECK_EVEN_WITH_STRUCTURE", \
            "STV expected HARD_FAIL got %s" % out2["verdict"]

        # MIDDLE_BAND: sign flips positive + significant but below the 0.05 margin (misses full bars)
        ps3 = mkseeds(_mk(4, 1200, 4, 8, flat=0.08, oexec=0.94, horc=0.90, open_a=0.38, spec_a=0.41,
                          clus_a=0.39, rand=0.12, idxm=0.13, n_spec_only=40, n_open_only_s=8))
        out3 = aggregate_and_verdict(ps3)
        assert out3["verdict"] == "MIDDLE_BAND_SIGNFLIP_MISSES_FULL_BARS", \
            "STV expected MIDDLE got %s" % out3["verdict"]

        # HARD_FAIL_SBM_NO_STRUCTURE: generator produced low modularity (vacuous)
        ps4 = {s: {"regime_results": ps[s]["regime_results"],
                   "graph_metrics_by_group": {gk: _gm(0.05, 1.1)}} for s in ps}
        out4 = aggregate_and_verdict(ps4)
        assert out4["verdict"] == "HARD_FAIL_SBM_NO_STRUCTURE_GENERATOR_VACUOUS", \
            "STV expected SBM_NO_STRUCTURE got %s" % out4["verdict"]

        # INCONCLUSIVE: rails not met (flat did not collapse)
        ps5 = mkseeds(_mk(4, 1200, 4, 8, flat=0.70, oexec=0.94, horc=0.90, open_a=0.38, spec_a=0.45,
                          clus_a=0.40, rand=0.12, idxm=0.13))
        # also break the low regime rails so no discriminating regime exists
        for s in ps5:
            ps5[s]["regime_results"][reg_lo]["arms"]["flat_gonogo"] = 0.70
        out5 = aggregate_and_verdict(ps5)
        assert out5["verdict"] == "INCONCLUSIVE_NO_DISCRIMINATING_REGIME", \
            "STV expected INCONCLUSIVE got %s" % out5["verdict"]
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST_VERDICT wiring OK (HARD_PASS signflip; HARD_FAIL no-flip; MIDDLE below-margin; "
          "HARD_FAIL_SBM_NO_STRUCTURE; INCONCLUSIVE rails-not-met)", flush=True)


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

    print("[%s] mode=%s device=%s N=%d seeds=%s gamma=%.2f seg_len=%d regimes=%s expected_n=%d "
          "P_within=%.2f door_per_room=%d n_cross=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, SEEDS, GAMMA, SEG_LEN, REGIME_KEYS,
             EXPECTED_N_UNITS, P_WITHIN, DOOR_PER_ROOM, N_CROSS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST_SBM1-3 (SBM structure, ER control, modularity formula), "
                               "ST_VERDICT (signflip wiring), ST_PIPE (pipeline + paired sign counts)",
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
                "seed": int(seed), "run_mode": RUN_MODE, "N": N_DIM, "anchor_name": ANCHOR_NAME,
                "config_version": CONFIG_VERSION, "failure_class": fc, "error": str(e)[:400],
                "traceback": traceback.format_exc()[:3000], "regime_results": {},
                "sr_diag_by_group": {}, "graph_metrics_by_group": {}})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        _heartbeat(out_dir, i + 1, len(remaining), "seed_done=%d dt=%.1f" % (seed, time.time() - t0))
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    good = {k: v for k, v in per_seed.items() if v.get("regime_results")}
    final = aggregate_and_verdict(good)

    # smoke discriminator-fires gate (rails + SBM structure MUST fire; loud VacuousSmokeError otherwise)
    if RUN_MODE in ("smoke", "selftest"):
        _smoke_discriminator_gate(final)

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
