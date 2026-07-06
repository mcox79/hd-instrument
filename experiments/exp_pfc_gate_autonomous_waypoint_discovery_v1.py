"""pfc_gate_autonomous_waypoint_discovery_v1 -- can the substrate DISCOVER its own sub-goal
decomposition (waypoints) from its already-trained SR transport M, with NO oracle trajectory?

WHY (Director steer 2026-07-05, follow-on to control-depth-solved):
  The ancestor cell PROVED hierarchical control is HARD_PASS at FULL *given a correct
  decomposition* (oracle waypoints = true intermediate chain states):
  MEASURED@data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json
    FOCUS=op4_V1200_d8(ent=16) FLAT=0.082 HIER_ORACLE=0.861 SHUF=0.000 ORACLE_EXEC=0.938
    hier_closure=0.910 (fraction of flat->oracle_exec gap the oracle-waypoint hierarchy closes).
  The ancestor's waypoints were oracle_trajectory_idx(...) -- the TRUE intermediate states, an
  assumed-optimal top-level option policy handed to the arm (declared oracle-assist, scoped
  honestly; docstring lines 34-39 there: "Autonomous waypoint DISCOVERY is an explicit FOLLOW-ON,
  not claimed here"). THIS cell answers that follow-on: can the substrate supply its OWN
  decomposition from what it already learned (E, W_ops, trained M), with no oracle trajectory?

MECHANISM UNDER TEST (NOT assumed):
  A new near-zero-cost primitive: the state-by-state REACH MATRIX built from the already-trained
  SR transport M:
    Efwd = normalize_rows(E @ M)             # [V, n_dim]
    R    = Efwd @ normalize_rows(E).T        # [V, V], R[i,j] == reach_value(E[i], E[j], M)
  built once per (seed, V, n_ops) group, same cadence/cost class as M itself.

  PRIMARY arm = sequential greedy BISECTION over R (candidate b, MPNet-style learned-midpoint
  proposal + recurse; bidirectional meet-in-the-middle depth-reduction; Stachenfeld-2017 SR
  predictive-map grounding, honestly-scoped as a computational metaphor, not confirmed neural algo):
    for each interior segment boundary (in hop order): anchor = prev waypoint (start for the first);
    wp = argmax_{c not in {start,goal,already-chosen}} min(R[anchor,c], R[c,goal]) over ALL V states.
  SECONDARY arms restrict that SAME argmax to a spectrally/cluster-privileged candidate subset
  (eigenoption sign-boundary states / PCCA+-lite low-cluster-margin states) -- Candidates (a)/(c).
  DOMAIN-FIT hypothesis (from the drill, NOT assumed): the substrate's operator-chain graphs are
  Erdos-Renyi-like random directed multigraphs at DENSITY=0.21 and likely LACK true community /
  bottleneck structure, so spectral/cluster RESTRICTION is expected NEUTRAL-to-HARMFUL vs open
  bisection. A negative (spectral/cluster <= open) is itself a CLEAN, informative confirmation.

  Waypoint SOURCE is the ONLY thing that differs across wp_* arms; the per-segment low-horizon
  hierarchical EXECUTION loop (run_hier_arm_wp) is identical for every arm and identical to the
  ancestor's run_hier_arm. oracle_trajectory_idx is still computed (for hier_oracle / hier_shuffled
  and the exact_match diagnostic) but is NOT visible to any wp_* arm's decomposition logic.

ARMS (paired -- share E, W_ops, M, R and the SAME test chains per (regime,seed)):
  flat_gonogo          FLAT SR Go/NoGo gate toward the FINAL goal (the collapse; FLOOR)
  oracle_exec          applies the true op_seq (perfect execution; absolute ceiling / FOCUS rail)
  hier_oracle          hierarchical arm with ORACLE waypoints (given-decomposition CEILING)
  hier_shuffled        hier structure with WRONG (other-chain) oracle waypoints (neg control)
  wp_bisect_open       PRIMARY autonomous: open sequential bisection over R
  wp_bisect_spectral   autonomous, candidate set = eigenoption sign-boundary states of R
  wp_bisect_cluster_exit autonomous, candidate set = low-cluster-margin (PCCA+-lite) states of R
  wp_random_state      autonomous FLOOR: uniform random codebook waypoints (is discovery > noise?)
  wp_index_midpoint    STRUCTURAL-ARTIFACT GUARD: index-interpolated waypoints (raw codebook index).
                       Codebook indices carry NO order by construction; if this beats random the
                       chain-generation leaks index order and ALL comparisons are invalid.

DISCRIMINATORS (per regime; FOCUS = highest-entropy regime with oracle_exec>=0.90 AND
headroom_exec>=0.10 AND headroom_decomp>=0.10; best_wp = max(open,spectral,cluster)):
  headroom_exec        = oracle_exec - flat_gonogo         (flat->perfect gap)
  headroom_decomp      = hier_oracle - flat_gonogo         (what a CORRECT decomposition buys)
  autonomous_closure(a)= (a - flat) / headroom_exec        (frac of flat->perfect closed; cf ancestor 0.910)
  recovery_ratio(a)    = (a - flat) / headroom_decomp      (frac of the ORACLE-decomp benefit recovered)
  lift_flat(a)         = a - flat                          (real lift over no-hierarchy)
  lift_random(a)       = a - wp_random_state               (real lift over a noise waypoint)
  index_artifact_gap   = wp_index_midpoint - wp_random_state  (structural leak guard)
  degenerate_rate      = P(UNMASKED bisection argmax == start OR goal)  (honesty guard)
  anti_tautology_corr  = corr(balance_score, raw target-cosine-to-goal-only) over candidates
  exact_match_rate     = P(discovered wp idx == true oracle-trajectory wp idx)  DIAGNOSTIC ONLY
  spectral_minus_open  = wp_bisect_spectral - wp_bisect_open   (domain-fit sub-result)
  cluster_minus_open   = wp_bisect_cluster_exit - wp_bisect_open

NOTE on the two closure metrics (author reconciliation, autonomy over exact bands): the drill's
formula line wrote autonomous_closure with a hier_oracle denominator and a separate recovery_ratio
divided by the ancestor closure, which is redundant. I define the two metrics with DISTINCT,
well-posed denominators: autonomous_closure references the PERFECT-execution ceiling (oracle_exec,
directly comparable to the ancestor's published hier_closure=0.910) and recovery_ratio references
the ORACLE-DECOMPOSITION ceiling (hier_oracle, the product-facing "recovers X% of a hand-given
plan"). Both HP thresholds (0.15 and 0.20) apply as the drill specified.

HARD_PASS (locked; best_wp at FOCUS): autonomous_closure(best_wp) >= 0.15 AND recovery_ratio(best_wp)
  >= 0.20 AND lift_flat(best_wp) > 0.05 AND lift_random(best_wp) > 0.10 AND index_artifact_gap < 0.05
  AND anti_tautology_corr < 0.85 AND degenerate_rate < 0.10 AND sign_p(best_wp vs flat) < 0.05 AND
  cv(best_wp) < 0.10 (FULL only) AND oracle_exec >= 0.90 AND headroom gates.
  => the substrate can discover a partially-useful decomposition from its own trained SR, no oracle.
HARD_FAIL (locked): lift_flat(best_wp) <= 0.05 OR lift_random(best_wp) <= 0.05
  => control is solvable GIVEN a correct decomposition (proven) but the substrate's own learned SR
  does not carry enough info to supply that decomposition -- a real, informative, structural bound.
MIDDLE_BAND: beats flat AND random by the required margins but recovery_ratio < 0.20, OR any honesty
  guard (index_artifact_gap, anti_tautology_corr, degenerate_rate) fails while accuracy margins pass.
INCONCLUSIVE: no discriminating regime, OR index_artifact_gap > 0.10 with sign_p(index vs random) <
  0.05 (genuine chain-generation structural leak -- comparisons invalid until fixed).
Reported REGARDLESS: full entropy-grid table for every wp_* arm; spearman(recovery_ratio, entropy);
  spectral_minus_open / cluster_minus_open at FOCUS (domain-fit); exact_match_rate.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): wp_bisect_open vs wp_random_state vs flat_gonogo AND
#   hier_oracle vs hier_shuffled op-trace hash per seed (exempt only if waypoints bit-identical).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json).
# - except SystemExit: raise BEFORE except Exception (no BaseException in main).
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor; reachability by
#   feasibility (ancestor hier_oracle=0.861 at op4_d8 proves the given-decomposition envelope; the
#   open question is how much of that headroom autonomous discovery recovers -- 0-1 achievable range).
# - baseline_in_band (AG): the discriminator is FLAT-referenced (headroom); FOCUS gate requires
#   oracle_exec>=0.90 AND headroom_exec>=0.10 AND headroom_decomp>=0.10 (measurable room).
# - discriminator survives scale: smoke holds N/V==FULL AND includes focus op4_d6 at IDENTICAL depth;
#   at N=8192 SR reach is SHARPER (ancestor reach_rank 0.40->0.69, N2048->8192) so discovery reach
#   should IMPROVE or hold; flat does not recover -> best_wp-vs-flat gap survives-or-grows (option C).
# - HARD_PASS strictly above floor: recovery_ratio>=0.20, autonomous_closure>=0.15 (META_RULE_L).
# - HP_SCOPE: HP gates apply to best_wp vs flat_gonogo/wp_random_state at FOCUS; oracle_rail (>=0.90)
#   to oracle_exec; recovery_ratio references hier_oracle; index guard to wp_index vs wp_random.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(9) * n_seeds * n_regimes.
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash).
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + wp_random floor +
#   wp_index structural-leak guard + anti_tautology_corr + degenerate_rate all logged).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.

Compute architecture: (a) batched-GPU. SR-TD training (gamma=0.85 fixed), operator application,
cleanup, reach, R build, bisection argmax, eigh = batched matmuls / one eigh per group on
cuda-if-available. Chains batched; within-chain hops sequential (genuine dependency). SR + R + masks
computed once per (V,n_ops) group and shared across depths. Storage strategy: sharded (each operator
its own W matrix; M a learned value operator, R a derived reach matrix). No bundled store. FULL
strongly prefers overnight_queue (GPU).
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line +
per (seed,V,n_ops) heartbeat; FULL timeout_s >= 1800).

USER-LOCKED FRAMING: NARROW glass-box sub-goal-discovery PRIMITIVE step. NOT autonomous planning,
NOT self-improvement. A HARD_PASS means only "given a trained SR over a small known state space, the
substrate can propose its own waypoints for control tasks in that space." Honest tier throughout.

Author: exp_dev 2026-07-05 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-05_pfc_gate_autonomous_waypoint_discovery_v1.md
Cites:
  data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json (ancestor FULL HARD_PASS ceiling)
  experiments/exp_pfc_gate_branching_depth_entropy_grid_v1.py (primitives reused verbatim)
  experiments/exp_pfc_gate_cfrpe_trained_v2.py (trained-SR machinery ancestor)
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
)

ANCHOR_NAME = "pfc_gate_autonomous_waypoint_discovery_v1"

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
HP_AUTON_CLOSURE_FLOOR = 0.15     # best_wp closes >= 15% of flat->perfect(oracle_exec) gap
HP_RECOVERY_RATIO_FLOOR = 0.20    # best_wp recovers >= 20% of the oracle-DECOMPOSITION benefit
HP_LIFT_FLAT_MIN = 0.05           # real lift over no-hierarchy flat
HP_LIFT_RANDOM_MIN = 0.10         # real lift over a noise waypoint (mechanism-fires gate)
HP_INDEX_GAP_MAX = 0.05           # no structural index-order leak
HP_ANTI_TAUT_CORR_MAX = 0.85      # balance score is dynamics, not target-cosine in disguise
HP_DEGENERATE_MAX = 0.10          # bisection does not degenerate to picking start/goal
HP_SIGN_TEST_P = 0.05             # paired best_wp vs flat significant
HP_CV_MAX = 0.10                  # cross-seed cv on best_wp at focus (FULL only)
HF_LIFT_FLAT_CEIL = 0.05          # HARD_FAIL: best_wp <= flat + 0.05
HF_LIFT_RANDOM_CEIL = 0.05        # HARD_FAIL: best_wp indistinguishable from a noise waypoint
INDEX_LEAK_GAP = 0.10             # INCONCLUSIVE: index beats random by > this ...
INDEX_LEAK_P = 0.05               # ... with paired sign p < this
ORACLE_RAIL_MIN = 0.90            # FOCUS: perfect-execution ceiling must be reachable
HEADROOM_EXEC_MIN = 0.10          # FOCUS: flat->perfect gap measurable
HEADROOM_DECOMP_MIN = 0.10        # FOCUS: oracle-decomposition benefit measurable (room to recover)

DENSITY = 0.21                     # n_train_triples_per_op / V (matches ancestor/v2/deeper)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2

GAMMA = 0.85                       # FIXED (ancestor smoke proved gamma inert at d6)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]
SEG_LEN = 2                        # hierarchical segment length (per-decision reach horizon cap)
CAND_FRAC = 0.10                   # spectral/cluster candidate-subset fraction of V
NEG_HARD = -1.0e9                  # exclude start/goal/already-chosen from bisection argmax
NEG_SOFT = -1.0e4                  # de-prioritize non-candidate states (graceful, not absolute)

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, dd). SR M + R + spectral/cluster masks trained/built once per (V,n_ops) group
# at GAMMA and shared across depths. SMOKE holds N/V == FULL and includes the focus op4_d6 at
# IDENTICAL depth -> matched per-hop difficulty + depth-dependence (option C preview).
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    REGIMES = [{"n_ops": 4, "V": 40, "dd": 4}, {"n_ops": 2, "V": 40, "dd": 4}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # multi-seed (3). 2x2 grid {n_ops 2,4} x {depth 4,6}. Fires the discriminator at the focus
    # op4_V300_d6 (flat collapses; hier_oracle strong; autonomous must beat flat + random) at
    # matched N/V + depth. Multi-seed smoke satisfies the continuous-score variance gate.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    REGIMES = [{"n_ops": 2, "V": 300, "dd": 4},
               {"n_ops": 2, "V": 300, "dd": 6},
               {"n_ops": 4, "V": 300, "dd": 4},
               {"n_ops": 4, "V": 300, "dd": 6}]   # FOCUS: high-branch deep, flat collapses
    N_TRAIN_CHAINS = 48
    N_TEST_CHAINS = 48
    SR_STEPS = 250
    SR_BATCH = 64
    SR_LR = 0.5
    ROLLOUT_PER_V = 8
else:  # full
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"n_ops": 2, "V": 800, "dd": 4},  {"n_ops": 2, "V": 800, "dd": 6},  {"n_ops": 2, "V": 800, "dd": 8},
               {"n_ops": 3, "V": 1000, "dd": 4}, {"n_ops": 3, "V": 1000, "dd": 6}, {"n_ops": 3, "V": 1000, "dd": 8},
               {"n_ops": 4, "V": 1200, "dd": 4}, {"n_ops": 4, "V": 1200, "dd": 6}, {"n_ops": 4, "V": 1200, "dd": 8}]
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000

# FIX-2 SR-BUDGET PROBE overrides (defaults leave every canonical config UNCHANGED). Lets a
# local better-SR retest disambiguate "SR undertrained at this budget" from "mechanism class dead"
# per the drill's 2x-before-closure candidate, without a new cell. Only active if env var is set.
SR_STEPS = int(os.environ.get("HDLAB_SR_STEPS", str(SR_STEPS)))
ROLLOUT_PER_V = int(os.environ.get("HDLAB_ROLLOUT_PER_V", str(ROLLOUT_PER_V)))
ROLLOUT_CAP = int(os.environ.get("HDLAB_ROLLOUT_CAP", str(ROLLOUT_CAP)))

ARMS = ["flat_gonogo", "oracle_exec", "hier_oracle", "hier_shuffled",
        "wp_bisect_open", "wp_bisect_spectral", "wp_bisect_cluster_exit",
        "wp_random_state", "wp_index_midpoint"]
WP_BISECT_ARMS = ["wp_bisect_open", "wp_bisect_spectral", "wp_bisect_cluster_exit"]
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


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_ops_set=%s,depth_set=%s,seeds=%s,gamma=%.2f,seg_len=%d,cand_frac=%.2f,"
    "regimes=%s,density=%.3f,sr_steps=%d,sr_batch=%d,rollout_per_V=%d,lr=%.2f,alphas=%s,w_reach=%s,"
    "n_train=%d,n_test=%d,mode=%s,device=%s,expected_n=%d,HP_auton>=%.2f,HP_recov>=%.2f,"
    "lift_flat>%.2f,lift_rand>%.2f,idx_gap<%.2f,anti_taut<%.2f,degen<%.2f,sign_p<%.2f,cv<%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA, SEG_LEN, CAND_FRAC, REGIME_KEYS,
    DENSITY, SR_STEPS, SR_BATCH, ROLLOUT_PER_V, SR_LR, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_AUTON_CLOSURE_FLOOR, HP_RECOVERY_RATIO_FLOOR, HP_LIFT_FLAT_MIN, HP_LIFT_RANDOM_MIN,
    HP_INDEX_GAP_MAX, HP_ANTI_TAUT_CORR_MAX, HP_DEGENERATE_MAX, HP_SIGN_TEST_P, HP_CV_MAX,
)

_T0 = time.time()


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
# primitives (torch, batched, device-agnostic) -- reused VERBATIM from ancestor
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
    """Returns (per_op_triples, train_chains_by_depth, test_chains_by_depth)."""
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
    """Random-walk exploration over the operator graph. Returns [K, 2] (cur, nxt) idx."""
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


# ============================================================================
# cfrpe-trained SR transport M (TD(0); gamma FIXED) -- reused VERBATIM
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features)."""
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


def reach_value(cand_E: torch.Tensor, goal_E: torch.Tensor, M: torch.Tensor
                ) -> torch.Tensor:
    """cos(E[cand] @ M, E[goal]) per row -- learned-dynamics reach. cand_E,goal_E: [B,n]."""
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


def reach_control_targetcos(cand_E: torch.Tensor, goal_E: torch.Tensor) -> torch.Tensor:
    """Anti-tautology control: reach with M:=identity == raw target-cosine cos(E[cand],E[goal])."""
    return (_norm_rows(cand_E) * _norm_rows(goal_E)).sum(dim=1)


# ============================================================================
# NEW primitive: reach matrix R + codebook self-cosine C
# ============================================================================
def build_reach_matrix(E: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
    """R [V,V], R[i,j] == reach_value(E[i], E[j], M) == cos(E[i]@M, E[j]). One matmul per group."""
    Efwd = _norm_rows(E @ M)
    En = _norm_rows(E)
    return Efwd @ En.transpose(0, 1)


def codebook_selfcos(E: torch.Tensor) -> torch.Tensor:
    """C [V,V], C[i,j] == cos(E[i], E[j]) (raw target-cosine matrix; anti-tautology reference)."""
    En = _norm_rows(E)
    return En @ En.transpose(0, 1)


# ============================================================================
# NEW: candidate-subset masks for the spectral / cluster (bottleneck-restriction) arms
# ============================================================================
def spectral_candidate_mask(R: torch.Tensor, frac: float) -> torch.Tensor:
    """Eigenoption sign-boundary candidate set: states with SMALL magnitude on the 2nd/3rd top
    eigenvectors of the symmetrized reach affinity (near the sign boundary between metastable
    clusters). Candidate (a). Returns bool mask [V]."""
    V = R.shape[0]
    S = 0.5 * (R + R.transpose(0, 1))
    evals, evecs = torch.linalg.eigh(S)   # ascending; top (smoothest) = last columns
    v2 = evecs[:, -2] if V >= 2 else evecs[:, -1]
    v3 = evecs[:, -3] if V >= 3 else v2
    mag = v2.abs() + v3.abs()
    k = max(2, int(round(frac * V)))
    k = min(k, V)
    idx = torch.argsort(mag)[:k]
    mask = torch.zeros(V, dtype=torch.bool, device=DEVICE)
    mask[idx] = True
    return mask


def cluster_candidate_mask(R: torch.Tensor, n_clusters: int, frac: float,
                           iters: int = 8) -> torch.Tensor:
    """PCCA+-lite low-cluster-margin candidate set: k-means on the top-d eigenvector embedding of
    the symmetrized reach affinity; states with LOW margin (ambiguous membership) are cluster-exit /
    boundary candidates. Candidate (c). Returns bool mask [V]."""
    V = R.shape[0]
    S = 0.5 * (R + R.transpose(0, 1))
    evals, evecs = torch.linalg.eigh(S)
    d = min(4, V)
    X = _norm_rows(evecs[:, V - d:])          # [V, d] top-d eigenvectors
    k = min(max(2, n_clusters), V)
    init = torch.linspace(0, V - 1, k).long().to(DEVICE)
    C = X[init].clone()
    for _ in range(iters):
        d2 = torch.cdist(X, C)                 # [V, k]
        assign = d2.argmin(dim=1)
        for c in range(k):
            m = (assign == c)
            if bool(m.any()):
                C[c] = X[m].mean(dim=0)
    d2 = torch.cdist(X, C)
    srt, _ = torch.sort(d2, dim=1)
    margin = (srt[:, 1] - srt[:, 0]) if k >= 2 else srt[:, 0]
    kk = max(2, int(round(frac * V)))
    kk = min(kk, V)
    idx = torch.argsort(margin)[:kk]          # low margin = boundary
    mask = torch.zeros(V, dtype=torch.bool, device=DEVICE)
    mask[idx] = True
    return mask


# ============================================================================
# NEW: waypoint DISCOVERY (boundary states -> per-hop schedule)
# ============================================================================
def _discover_bisect_boundaries(starts: torch.Tensor, targets: torch.Tensor, R: torch.Tensor,
                                seg_len: int, depth: int,
                                cand_mask: Optional[torch.Tensor]) -> torch.Tensor:
    """Sequential greedy bisection over R. Interior boundary wp = argmax_c min(R[anchor,c],R[c,goal])
    excluding start/goal/already-chosen; anchor = prev wp (start for first). Optional cand_mask
    restricts the argmax to a privileged subset (soft-penalizes the rest). Returns boundary_states
    [n_chains, n_bnd], last column = targets (the final boundary IS the goal)."""
    n_chains = starts.shape[0]
    n_bnd = n_boundaries(depth, seg_len)
    rowar = torch.arange(n_chains, device=DEVICE)
    rg = R.index_select(1, targets).transpose(0, 1)         # [n_chains, V], rg[i,c] = R[c, goal_i]
    anchor = starts.clone()
    chosen_cols: List[torch.Tensor] = []
    for _ in range(n_bnd - 1):
        ra = R.index_select(0, anchor)                       # [n_chains, V], ra[i,c] = R[anchor_i,c]
        balance = torch.minimum(ra, rg).clone()
        if cand_mask is not None:
            balance = balance + NEG_SOFT * (~cand_mask).to(DTYPE).unsqueeze(0)
        balance[rowar, starts] = NEG_HARD
        balance[rowar, targets] = NEG_HARD
        for prev in chosen_cols:
            balance[rowar, prev] = NEG_HARD
        wp = balance.argmax(dim=1)
        chosen_cols.append(wp)
        anchor = wp
    cols = chosen_cols + [targets]
    return torch.stack(cols, dim=1)                          # [n_chains, n_bnd]


def _discover_random_boundaries(starts: torch.Tensor, targets: torch.Tensor, V: int,
                                seg_len: int, depth: int, g: np.random.Generator) -> torch.Tensor:
    """Uniform random codebook waypoints (not balance-scored); avoid start/goal. TRUE floor."""
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
    """Structural-artifact guard: interpolate the waypoint by RAW CODEBOOK INDEX between start and
    goal at each boundary's fractional depth (reduces to floor((start+goal)/2) at a single interior
    boundary). Codebook indices carry NO order by construction, so if this beats random the chain
    generation leaks index order. Deterministic; avoid start/goal by nudging."""
    n_chains = starts.shape[0]
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
    """Map boundary states [n_chains, n_bnd] to a per-hop waypoint schedule [n_chains, depth].
    hop h uses the boundary at array-index h//seg_len (== the ancestor build_waypoint_idx schedule:
    boundary at position min((h//seg_len+1)*seg_len, depth))."""
    n_bnd = boundary_states.shape[1]
    hop_to_bnd = [min(h // seg_len, n_bnd - 1) for h in range(depth)]
    idx = torch.tensor(hop_to_bnd, dtype=torch.long, device=DEVICE)
    return boundary_states.index_select(1, idx)


def oracle_trajectory_idx(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int
                          ) -> torch.Tensor:
    """Per-hop cleaned-state INDICES along the true (oracle) trajectory -> [n_chains, depth+1].
    Column 0 = start; column depth is FORCED to the declared target. reused VERBATIM."""
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
    """Oracle/shuffled per-hop waypoint index [n_chains, depth]. reused VERBATIM from ancestor."""
    src = torch.roll(traj_idx, shifts=1, dims=0) if shuffle else traj_idx
    wp_hop = [min(((h // seg_len) + 1) * seg_len, depth) for h in range(depth)]
    wp_hop_t = torch.tensor(wp_hop, dtype=torch.long, device=DEVICE)
    return src[:, wp_hop_t]


# ============================================================================
# arms (batched across chains; hops sequential within a chain)
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
    """FLAT batched op-selection arm toward the FINAL goal every hop. reused VERBATIM."""
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


def run_oracle_arm(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int
                   ) -> np.ndarray:
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
    """HIERARCHICAL-OPTIONS execution given an EXTERNAL per-hop waypoint schedule wp_idx
    [n_chains, depth]. Identical to the ancestor run_hier_arm except waypoints are supplied (the
    ONLY thing that differs across wp_* / hier_oracle / hier_shuffled arms). Correctness measured
    against the arm's OWN declared final target."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    wp_E_all = E[wp_idx]                                      # [n_chains, depth, n_dim]
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


# ---- per-arm waypoint hop-schedules (discovery wrappers) ----
def wp_hops_open(chains, R, depth) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_bisect_boundaries(starts, targets, R, SEG_LEN, depth, None)
    return _boundaries_to_hops(b, SEG_LEN, depth)


def wp_hops_masked(chains, R, depth, cand_mask) -> torch.Tensor:
    starts, targets, _ = _chain_tensors(chains)
    b = _discover_bisect_boundaries(starts, targets, R, SEG_LEN, depth, cand_mask)
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


# ---- discovery honesty diagnostics (computed on the OPEN arm's shared balance signal) ----
def discovery_diagnostics(chains, R: torch.Tensor, C: torch.Tensor, depth: int,
                          W_ops, E, seg_len: int) -> Dict[str, float]:
    """degenerate_rate (P unmasked bisection argmax lands on start/goal), anti_tautology_corr
    (Pearson corr of the balance score vs raw goal-cosine over candidates at the first interior
    boundary), exact_match_rate (P discovered interior boundary == oracle-trajectory boundary)."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    rg = R.index_select(1, targets).transpose(0, 1)          # [n_chains, V] R[c,goal]
    ra0 = R.index_select(0, starts)                          # [n_chains, V] R[start,c]
    balance0 = torch.minimum(ra0, rg)                        # [n_chains, V]
    # UNMASKED argmax degenerate tendency
    um = balance0.argmax(dim=1)
    degenerate = ((um == starts) | (um == targets)).float().mean().item()
    # anti-tautology: balance vs raw goal-cosine over all candidates
    raw0 = C.index_select(1, targets).transpose(0, 1)        # [n_chains, V] cos(E[c],E[goal])
    a = balance0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    b = raw0.reshape(-1).detach().cpu().numpy().astype(np.float64)
    if a.std() < 1e-9 or b.std() < 1e-9:
        anti_taut = 0.0
    else:
        anti_taut = float(np.corrcoef(a, b)[0, 1])
    # exact-match of discovered interior boundaries vs oracle trajectory boundaries (DIAGNOSTIC)
    b_open = _discover_bisect_boundaries(starts, targets, R, seg_len, depth, None)  # [n_chains,n_bnd]
    traj = oracle_trajectory_idx(chains, W_ops, E, depth)                            # [n_chains,depth+1]
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
    """Mechanism-fires probe: along the TRUE trajectory, does argmax_op reach == the true op?
    Chance = 1/n_ops. Reach toward the FINAL goal. reused VERBATIM."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    hits = 0
    total = 0
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    for hop in range(depth):
        reach_scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            cand_idx_all[:, op] = idx
            reach_scores[:, op] = reach_value(cleaned, goal_E, M)
        pred_op = reach_scores.argmax(dim=1)
        true_op = op_seq_t[:, hop]
        hits += int((pred_op == true_op).sum().item())
        total += n_chains
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx_all[row, true_op]
        state = E[new_idx]
    return float(hits) / float(max(1, total))


# ============================================================================
# stats -- reused VERBATIM
# ============================================================================
def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    if n == 0:
        return 1.0
    if n <= 1000:
        from math import comb
        obs = min(k, n - k)

        def _pmf(i):
            return comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
        tail = 0.0
        for i in range(0, obs + 1):
            tail += _pmf(i)
        return float(min(1.0, 2.0 * tail))
    mu = n * p
    sd = math.sqrt(n * p * (1 - p))
    z = (abs(k - mu) - 0.5) / (sd + 1e-12)
    return float(min(1.0, 2.0 * 0.5 * math.erfc(z / math.sqrt(2.0))))


def _rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[order] = np.arange(1, len(x) + 1, dtype=np.float64)
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts), dtype=np.float64)
    for i in range(len(x)):
        sums[inv[i]] += ranks[i]
    avg = sums / counts
    return avg[inv]


def _spearman(x: List[float], y: List[float]) -> float:
    a = np.asarray(x, dtype=np.float64); b = np.asarray(y, dtype=np.float64)
    if len(a) < 3 or a.std() < 1e-12 or b.std() < 1e-12:
        return 0.0
    ra = _rankdata(a); rb = _rankdata(b)
    if ra.std() < 1e-12 or rb.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


# ============================================================================
# per-seed runner
# ============================================================================
def _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd) -> Tuple[float, float]:
    """Tune alpha on the ORACLE-waypoint hierarchical arm (neutral reference) at w_reach=1.0."""
    wp = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    best_a, best = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_hier_arm_wp(train_c, W_ops, E, M, dd, SEG_LEN, a, 1.0, wp)[0].mean()
        if acc > best:
            best, best_a = acc, a
    return best_a, float(best)


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


def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, R: torch.Tensor, C: torch.Tensor,
                 spec_mask: torch.Tensor, clus_mask: torch.Tensor,
                 train_by_d, test_by_d, g: np.random.Generator) -> Dict[str, Any]:
    """Tune on train, evaluate all 9 arms on test (paired). One seed, gamma fixed."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    # alpha tuned once on the neutral oracle-waypoint hier arm; fixed for ALL arms.
    best_alpha, _hier_oracle_train = _tune_alpha_hier_oracle(train_c, W_ops, E, M, dd)

    # train waypoint schedules
    wp_oracle_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=False)
    wp_shuf_tr = wp_hops_oracle(train_c, W_ops, E, dd, shuffle=True)
    wp_open_tr = wp_hops_open(train_c, R, dd)

    # w_reach tuned per arm on train (flat, hier_oracle, hier_shuffled, wp_open). The restricted /
    # random / index wp arms REUSE wp_open's tuned w_reach (same execution; shared, documented).
    wr_flat, _ = _tune_wreach_flat(train_c, W_ops, E, M, dd, best_alpha)
    wr_oracle, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_oracle_tr)
    wr_shuf, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_shuf_tr)
    wr_open, _ = _tune_wreach_hier_wp(train_c, W_ops, E, M, dd, best_alpha, wp_open_tr)

    # test waypoint schedules (discovery uses only start/goal + R; never the oracle trajectory)
    wp_oracle_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=False)
    wp_shuf_te = wp_hops_oracle(test_c, W_ops, E, dd, shuffle=True)
    wp_open_te = wp_hops_open(test_c, R, dd)
    wp_spec_te = wp_hops_masked(test_c, R, dd, spec_mask)
    wp_clus_te = wp_hops_masked(test_c, R, dd, clus_mask)
    wp_rand_te = wp_hops_random(test_c, V, dd, g)
    wp_idx_te = wp_hops_index(test_c, V, dd)

    # eval on TEST (paired)
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
        "flat_gonogo": float(flat_c.mean()),
        "oracle_exec": float(orc_c.mean()),
        "hier_oracle": float(ho_c.mean()),
        "hier_shuffled": float(hs_c.mean()),
        "wp_bisect_open": float(op_c.mean()),
        "wp_bisect_spectral": float(sp_c.mean()),
        "wp_bisect_cluster_exit": float(cl_c.mean()),
        "wp_random_state": float(rd_c.mean()),
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

    # best_wp per-chain correctness (max over the three bisect arms by mean acc)
    bisect_means = {"wp_bisect_open": arms["wp_bisect_open"],
                    "wp_bisect_spectral": arms["wp_bisect_spectral"],
                    "wp_bisect_cluster_exit": arms["wp_bisect_cluster_exit"]}
    best_wp_arm = max(bisect_means, key=lambda k: bisect_means[k])
    best_c = {"wp_bisect_open": op_c, "wp_bisect_spectral": sp_c,
              "wp_bisect_cluster_exit": cl_c}[best_wp_arm]

    # paired counts: best_wp vs flat, best_wp vs random, index vs random (per-chain)
    paired = {
        "n_bwp_only_vs_flat": int((best_c & (~flat_c)).sum()),
        "n_flat_only_vs_bwp": int((flat_c & (~best_c)).sum()),
        "n_bwp_only_vs_rand": int((best_c & (~rd_c)).sum()),
        "n_rand_only_vs_bwp": int((rd_c & (~best_c)).sum()),
        "n_idx_only_vs_rand": int((ix_c & (~rd_c)).sum()),
        "n_rand_only_vs_idx": int((rd_c & (~ix_c)).sum()),
        "n_test": int(len(best_c)),
    }

    return {
        "n_ops": n_ops, "V": V, "dd": dd,
        "entropy": decision_entropy(n_ops, dd),
        "arms": arms,
        "op_trace_hashes": op_trace_hashes,
        "best_wp_arm": best_wp_arm,
        "best_alpha": float(best_alpha),
        "wr_flat": float(wr_flat), "wr_oracle": float(wr_oracle),
        "wr_shuf": float(wr_shuf), "wr_open": float(wr_open),
        "reach_rank_chance": 1.0 / float(n_ops),
        "reach_rank_test": float(rr_test),
        "degenerate_rate": float(diag["degenerate_rate"]),
        "anti_tautology_corr": float(diag["anti_tautology_corr"]),
        "exact_match_rate": float(diag["exact_match_rate"]),
        "paired": paired,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

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
        transitions = collect_rollout_transitions(
            adj, n_ops, V, rollout_count(V), max_len, g)

        sr_gen = torch.Generator(device=DEVICE)
        sr_gen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3)
        M, sr_diag = train_sr_transport(
            E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
        sr_diag_by_group[group_key(n_ops, V)] = sr_diag

        # NEW: reach matrix + self-cosine + spectral / cluster candidate masks (once per group)
        R = build_reach_matrix(E, M)
        C = codebook_selfcos(E)
        try:
            spec_mask = spectral_candidate_mask(R, CAND_FRAC)
            clus_mask = cluster_candidate_mask(R, n_ops, CAND_FRAC)
        except Exception as e:
            # eigh should not fail on a well-formed symmetric matrix; if it does, fall back to
            # open (all-True mask) and record the failure class so the arm degrades to open, loud.
            print("[seed=%d op%d V=%d] SPECTRAL_MASK_FAIL %s: %s -> fallback all-True"
                  % (seed, n_ops, V, type(e).__name__, e), file=sys.stderr, flush=True)
            spec_mask = torch.ones(V, dtype=torch.bool, device=DEVICE)
            clus_mask = torch.ones(V, dtype=torch.bool, device=DEVICE)
            sr_diag["spectral_mask_failure_class"] = type(e).__name__

        print("[seed=%d op%d V=%d] SR: err %s->%s M_norm=%.3f n_trans=%d clamp=%d "
              "R_mean=%.3f spec_k=%d clus_k=%d"
              % (seed, n_ops, V, sr_diag["err_first"], sr_diag["err_last"],
                 sr_diag["final_M_norm"], sr_diag["n_transitions"], sr_diag["n_clamped_steps"],
                 float(R.mean()), int(spec_mask.sum()), int(clus_mask.sum())), flush=True)

        for dd in depths_needed:
            rec = _eval_regime(n_ops, V, dd, E, W_ops, M, R, C, spec_mask, clus_mask,
                               train_by_d, test_by_d, g)
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(n_ops, V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s ent=%.2f] FLAT=%.3f OEXEC=%.3f HORC=%.3f SHUF=%.3f | "
                  "OPEN=%.3f SPEC=%.3f CLUS=%.3f RAND=%.3f IDX=%.3f (a=%.2f wrO=%.1f "
                  "rr=%.3f degen=%.3f taut=%.3f exact=%.3f best=%s)"
                  % (seed, key, rec["entropy"], a["flat_gonogo"], a["oracle_exec"],
                     a["hier_oracle"], a["hier_shuffled"], a["wp_bisect_open"],
                     a["wp_bisect_spectral"], a["wp_bisect_cluster_exit"], a["wp_random_state"],
                     a["wp_index_midpoint"], rec["best_alpha"], rec["wr_open"],
                     rec["reach_rank_test"], rec["degenerate_rate"], rec["anti_tautology_corr"],
                     rec["exact_match_rate"], rec["best_wp_arm"]), flush=True)

    return {
        "seed": int(seed),
        "N": N_DIM, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "regime_results": regime_results,
        "sr_diag_by_group": sr_diag_by_group,
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
        return [float(per_seed[k]["regime_results"][rk][field]) for k in _present(rk)]

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

        # best_wp by mean over the three bisect arms
        bisect = {a: arm_means[a] for a in WP_BISECT_ARMS}
        best_wp_arm = max(bisect, key=lambda k: bisect[k])
        best_wp = bisect[best_wp_arm]

        headroom_exec = oexec - flat
        headroom_decomp = horc - flat
        autonomous_closure = ((best_wp - flat) / headroom_exec) if headroom_exec > 1e-6 else 0.0
        recovery_ratio = ((best_wp - flat) / headroom_decomp) if headroom_decomp > 1e-6 else 0.0
        lift_flat = best_wp - flat
        lift_random = best_wp - rand
        index_artifact_gap = idxm - rand
        spectral_minus_open = arm_means["wp_bisect_spectral"] - arm_means["wp_bisect_open"]
        cluster_minus_open = arm_means["wp_bisect_cluster_exit"] - arm_means["wp_bisect_open"]

        degen = _mean(_field_col(rk, "degenerate_rate"))
        anti_taut = _mean(_field_col(rk, "anti_tautology_corr"))
        exact = _mean(_field_col(rk, "exact_match_rate"))
        rr_test = _mean(_field_col(rk, "reach_rank_test"))
        entropy = decision_entropy(r["n_ops"], r["dd"])

        # pooled paired sign-test across seeds: best_wp vs flat, index vs random
        n_bwp_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_bwp_only_vs_flat"]) for k in present)
        n_flat_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_flat_only_vs_bwp"]) for k in present)
        n_disc = n_bwp_only + n_flat_only
        sign_p = binom_two_sided_p(n_bwp_only, n_disc, 0.5) if n_disc > 0 else 1.0
        n_idx_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_idx_only_vs_rand"]) for k in present)
        n_rand_only_idx = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_rand_only_vs_idx"]) for k in present)
        n_disc_idx = n_idx_only + n_rand_only_idx
        idx_sign_p = binom_two_sided_p(n_idx_only, n_disc_idx, 0.5) if n_disc_idx > 0 else 1.0

        # arms-differ (AF): best_wp trace vs flat AND vs random per seed (unless w_reach makes the
        # execution collapse; waypoints differ by construction so a collision flags an impl bug).
        af_collision = False
        for k in present:
            rr = per_seed[k]["regime_results"][rk]
            h = rr["op_trace_hashes"]
            bwp = rr["best_wp_arm"]
            if h[bwp] == h["flat_gonogo"] or h[bwp] == h["wp_random_state"]:
                af_collision = True
            if h["hier_oracle"] == h["hier_shuffled"]:
                af_collision = True

        oracle_rail_ok = bool(oexec >= ORACLE_RAIL_MIN)
        headroom_exec_ok = bool(headroom_exec >= HEADROOM_EXEC_MIN)
        headroom_decomp_ok = bool(headroom_decomp >= HEADROOM_DECOMP_MIN)
        bwp_cv = arm_cvs[best_wp_arm]

        hp_ok = (oracle_rail_ok and headroom_exec_ok and headroom_decomp_ok
                 and autonomous_closure >= HP_AUTON_CLOSURE_FLOOR
                 and recovery_ratio >= HP_RECOVERY_RATIO_FLOOR
                 and lift_flat > HP_LIFT_FLAT_MIN
                 and lift_random > HP_LIFT_RANDOM_MIN
                 and index_artifact_gap < HP_INDEX_GAP_MAX
                 and anti_taut < HP_ANTI_TAUT_CORR_MAX
                 and degen < HP_DEGENERATE_MAX
                 and sign_p < HP_SIGN_TEST_P
                 and (bwp_cv < HP_CV_MAX or RUN_MODE != "full")
                 and not af_collision)

        index_leak = bool(index_artifact_gap > INDEX_LEAK_GAP and idx_sign_p < INDEX_LEAK_P)

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "entropy": entropy, "arm_means": arm_means, "arm_cvs": arm_cvs,
            "flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
            "wp_random_state": rand, "wp_index_midpoint": idxm,
            "best_wp_arm": best_wp_arm, "best_wp": float(best_wp),
            "headroom_exec": float(headroom_exec), "headroom_decomp": float(headroom_decomp),
            "autonomous_closure": float(autonomous_closure), "recovery_ratio": float(recovery_ratio),
            "lift_flat": float(lift_flat), "lift_random": float(lift_random),
            "index_artifact_gap": float(index_artifact_gap),
            "spectral_minus_open": float(spectral_minus_open),
            "cluster_minus_open": float(cluster_minus_open),
            "degenerate_rate": float(degen), "anti_tautology_corr": float(anti_taut),
            "exact_match_rate": float(exact), "reach_rank_test": float(rr_test),
            "sign_test_p": float(sign_p), "idx_sign_p": float(idx_sign_p),
            "n_bwp_only": int(n_bwp_only), "n_flat_only": int(n_flat_only),
            "oracle_rail_ok": oracle_rail_ok, "headroom_exec_ok": headroom_exec_ok,
            "headroom_decomp_ok": headroom_decomp_ok, "bwp_cv": float(bwp_cv),
            "af_collision": bool(af_collision), "index_leak": index_leak, "hp_ok": bool(hp_ok),
        }

    # ---- reported regardless: entropy relationship of recovery_ratio ----
    grid_ents, grid_recov = [], []
    for rk, v in per_regime.items():
        if v["n_seeds"] > 0 and v["headroom_decomp"] > 1e-6:
            grid_ents.append(v["entropy"]); grid_recov.append(v["recovery_ratio"])
    spearman_recovery_vs_entropy = _spearman(grid_recov, grid_ents)

    # ---- focus = highest-entropy discriminating regime ----
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

    # ---- reported REGARDLESS: autonomous-capability depth frontier (honest enrichment; does NOT
    # move the locked primary-verdict goalposts, which stay gated on the strict highest-entropy
    # FOCUS). Captures the depth-bounded-capability finding: how far up the entropy ladder does
    # autonomous discovery clear the FULL HP bar per-regime? ----
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
    elif fv["hp_ok"]:
        verdict = "HARD_PASS"
    elif fv["lift_flat"] <= HF_LIFT_FLAT_CEIL or fv["lift_random"] <= HF_LIFT_RANDOM_CEIL:
        verdict = "HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION"
    else:
        # helps but sub-threshold or a guard failed
        if fv["index_artifact_gap"] >= HP_INDEX_GAP_MAX:
            verdict = "MIDDLE_BAND_INDEX_ARTIFACT_GUARD"
        elif fv["anti_tautology_corr"] >= HP_ANTI_TAUT_CORR_MAX:
            verdict = "MIDDLE_BAND_ANTI_TAUTOLOGY_GUARD"
        elif fv["degenerate_rate"] >= HP_DEGENERATE_MAX:
            verdict = "MIDDLE_BAND_DEGENERATE_GUARD"
        elif fv["recovery_ratio"] < HP_RECOVERY_RATIO_FLOOR:
            verdict = "MIDDLE_BAND_RECOVERY_BELOW_20"
        elif fv["autonomous_closure"] < HP_AUTON_CLOSURE_FLOOR:
            verdict = "MIDDLE_BAND_CLOSURE_BELOW_15"
        elif fv["sign_test_p"] >= HP_SIGN_TEST_P:
            verdict = "MIDDLE_BAND_SIGN_TEST_NS"
        elif RUN_MODE == "full" and fv["bwp_cv"] >= HP_CV_MAX:
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        else:
            verdict = "MIDDLE_BAND_SUBTHRESHOLD"

    grid_str = " ".join(
        "%s(e%.1f:F%.2f/O%.2f/OPEN%.2f/RAND%.2f)" % (
            rk, per_regime[rk]["entropy"], per_regime[rk]["flat_gonogo"],
            per_regime[rk]["hier_oracle"], per_regime[rk]["arm_means"]["wp_bisect_open"],
            per_regime[rk]["wp_random_state"])
        for rk in REGIME_KEYS if rk in per_regime and per_regime[rk]["n_seeds"] > 0)

    if fv is not None:
        head = ("%s | FOCUS=%s(ent=%.1f) FLAT=%.3f OEXEC=%.3f HIER_ORACLE=%.3f RAND=%.3f IDX=%.3f | "
                "best_wp=%s=%.3f auton_closure=%.3f recovery_ratio=%.3f lift_flat=%.3f "
                "lift_random=%.3f | index_gap=%.3f anti_taut=%.3f degen=%.3f exact=%.3f "
                "sign_p=%.4g rr=%.3f cv=%.3f | spec-open=%.3f clus-open=%.3f "
                "spr(recovery,ent)=%.3f | GRID [%s] n_seeds=%d") % (
            verdict, focus_rk, fv["entropy"], fv["flat_gonogo"], fv["oracle_exec"],
            fv["hier_oracle"], fv["wp_random_state"], fv["wp_index_midpoint"], fv["best_wp_arm"],
            fv["best_wp"], fv["autonomous_closure"], fv["recovery_ratio"], fv["lift_flat"],
            fv["lift_random"], fv["index_artifact_gap"], fv["anti_tautology_corr"],
            fv["degenerate_rate"], fv["exact_match_rate"], fv["sign_test_p"], fv["reach_rank_test"],
            fv["bwp_cv"], fv["spectral_minus_open"], fv["cluster_minus_open"],
            spearman_recovery_vs_entropy, grid_str, len(keys))
    else:
        head = "%s | no discriminating regime | GRID [%s] n_seeds=%d" % (verdict, grid_str, len(keys))

    head = head + (" | CAP_FRONTIER=%s(maxE=%s) n_hp_ok=%d/%d"
                   % (capability_frontier, max_entropy_hp_ok, n_regimes_hp_ok, len(per_regime)))

    return {
        "verdict": verdict, "verdict_msg": head, "summary": head,
        "per_regime": per_regime, "focus_regime": focus_rk,
        "focus_best_wp_arm": (fv["best_wp_arm"] if fv else None),
        "focus_best_wp": (fv["best_wp"] if fv else None),
        "focus_autonomous_closure": (fv["autonomous_closure"] if fv else None),
        "focus_recovery_ratio": (fv["recovery_ratio"] if fv else None),
        "focus_lift_flat": (fv["lift_flat"] if fv else None),
        "focus_lift_random": (fv["lift_random"] if fv else None),
        "focus_index_artifact_gap": (fv["index_artifact_gap"] if fv else None),
        "focus_spectral_minus_open": (fv["spectral_minus_open"] if fv else None),
        "focus_cluster_minus_open": (fv["cluster_minus_open"] if fv else None),
        "beats_flat_and_random": bool(fv["lift_flat"] > HP_LIFT_FLAT_MIN
                                      and fv["lift_random"] > HP_LIFT_RANDOM_MIN) if fv else False,
        "spearman_recovery_vs_entropy": spearman_recovery_vs_entropy,
        "discriminating_regime_keys": list(discriminating.keys()),
        "n_regimes_hp_ok": int(n_regimes_hp_ok), "hp_ok_regime_keys": hp_ok_keys,
        "autonomous_capability_frontier": capability_frontier,
        "max_entropy_hp_ok": (float(max_entropy_hp_ok) if max_entropy_hp_ok is not None else None),
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok), "cv_gate_enforced": bool(RUN_MODE == "full"),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gamma=%.2f seg_len=%d cand_frac=%.2f"
          % (DEVICE, GAMMA, SEG_LEN, CAND_FRAC), flush=True)

    # ST1: cfrpe SR-TD delta-rule shrinks the TD prediction error over steps
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    E = make_bipolar_E(12, 128, gen)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5, gamma=0.8, gen=gen)
    assert diag["err_last"] is not None and diag["err_first"] is not None
    assert diag["err_last"] < diag["err_first"], "ST1 TD failed to shrink"
    assert float(M.norm()) > 1e-4, "ST1 M is ~zero"
    print("[selftest] ST1 cfrpe TD shrinks RPE: %.4f -> %.4f OK"
          % (diag["err_first"], diag["err_last"]), flush=True)

    # ST2: Go/NoGo argmax competition
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]], device=DEVICE)
    assert int(scores.argmax(dim=1)[0]) == 1, "ST2 argmax wrong"
    print("[selftest] ST2 Go/NoGo argmax OK", flush=True)

    # ST3 (REACH MATRIX): R[i,j] == reach_value(E[i], E[j], M) for sampled pairs
    gen3 = torch.Generator(device=DEVICE); gen3.manual_seed(3)
    E3 = make_bipolar_E(20, 512, gen3)
    tr3 = np.array([[i, (i + 1) % 20] for i in range(20)] * 3, dtype=np.int64)
    M3, _ = train_sr_transport(E3, tr3, 512, steps=300, batch=16, base_lr=0.5, gamma=GAMMA, gen=gen3)
    R3 = build_reach_matrix(E3, M3)
    for (i, j) in [(0, 5), (3, 3), (7, 12), (19, 1)]:
        rv = float(reach_value(E3[i:i + 1], E3[j:j + 1], M3)[0])
        assert abs(R3[i, j].item() - rv) < 1e-4, ("ST3 R[%d,%d]=%.5f != reach=%.5f"
                                                  % (i, j, R3[i, j].item(), rv))
    print("[selftest] ST3 reach matrix R[i,j]==reach_value(E[i],E[j],M) OK", flush=True)

    # ST4 (BISECTION MECHANISM-FIRES): on a chain 0->1->2->3->4 (linear), the open bisection from
    # start=0 to goal=4 discovers an INTERIOR node (not start/goal), and its balance-score midpoint
    # is a real interior state. Also confirm the toy true midpoint (2) is among discovered picks.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(11)
    Vt, Nt = 24, 1024
    Et = make_bipolar_E(Vt, Nt, gen4)
    chain = [(k, k + 1) for k in range(0, 8)]
    trt = np.tile(np.array(chain, dtype=np.int64), (60, 1))
    Mt, _ = train_sr_transport(Et, trt, Nt, steps=1500, batch=16, base_lr=0.5, gamma=GAMMA, gen=gen4)
    Rt = build_reach_matrix(Et, Mt)
    starts = torch.tensor([0], dtype=torch.long, device=DEVICE)
    goals = torch.tensor([4], dtype=torch.long, device=DEVICE)
    bnd = _discover_bisect_boundaries(starts, goals, Rt, seg_len=2, depth=4, cand_mask=None)
    # depth 4, seg 2 -> 2 boundaries: 1 interior + goal. interior must not be start/goal.
    interior = int(bnd[0, 0].item())
    assert interior not in (0, 4), "ST4 bisect interior degenerate: %d" % interior
    assert int(bnd[0, -1].item()) == 4, "ST4 last boundary must be goal"
    # the true geodesic midpoint of 0->4 is node 2; a working reach should rank it near the top
    ra = Rt.index_select(0, starts); rg = Rt.index_select(1, goals).transpose(0, 1)
    bal = torch.minimum(ra, rg)[0]
    bal[0] = NEG_HARD; bal[4] = NEG_HARD
    rank_of_2 = int((bal > bal[2]).sum().item())
    assert rank_of_2 <= 3, "ST4 true midpoint node 2 ranked too low (%d) by balance score" % rank_of_2
    print("[selftest] ST4 bisection fires: interior=%d (nondegenerate), midpoint-2 rank=%d OK"
          % (interior, rank_of_2), flush=True)

    # ST5 (DEGENERATE MASKING): discovered interior boundaries never == start or goal (multi-chain)
    starts5 = torch.tensor([0, 3, 6], dtype=torch.long, device=DEVICE)
    goals5 = torch.tensor([5, 8, 1], dtype=torch.long, device=DEVICE)
    bnd5 = _discover_bisect_boundaries(starts5, goals5, Rt, seg_len=2, depth=6, cand_mask=None)
    n_bnd5 = bnd5.shape[1]
    for j in range(n_bnd5 - 1):
        col = bnd5[:, j]
        assert not bool(((col == starts5) | (col == goals5)).any()), \
            "ST5 masking failed at boundary %d: %s" % (j, col.tolist())
    # already-chosen exclusion: interior boundaries distinct within a chain
    if n_bnd5 - 1 >= 2:
        assert int(bnd5[0, 0].item()) != int(bnd5[0, 1].item()), "ST5 already-chosen not excluded"
    print("[selftest] ST5 bisection masking (no start/goal, distinct interior) OK", flush=True)

    # ST6 (INDEX MIDPOINT): single interior boundary reduces to floor-ish midpoint; multi interpolates
    st6 = torch.tensor([10, 100], dtype=torch.long, device=DEVICE)
    tg6 = torch.tensor([30, 200], dtype=torch.long, device=DEVICE)
    ib4 = _discover_index_boundaries(st6, tg6, 300, seg_len=2, depth=4)   # 1 interior at t=0.5
    assert abs(int(ib4[0, 0].item()) - 20) <= 1, "ST6 idx midpoint chain0 != ~20: %d" % int(ib4[0, 0])
    assert abs(int(ib4[1, 0].item()) - 150) <= 1, "ST6 idx midpoint chain1 != ~150: %d" % int(ib4[1, 0])
    ib6 = _discover_index_boundaries(st6, tg6, 300, seg_len=2, depth=6)   # interiors t=1/3, 2/3
    # chain0: 10 + 1/3*20=16.67->17, 10+2/3*20=23.33->23
    assert abs(int(ib6[0, 0].item()) - 17) <= 1 and abs(int(ib6[0, 1].item()) - 23) <= 1, \
        "ST6 idx interpolation wrong: %s" % ib6[0].tolist()
    assert int(ib6[0, -1].item()) == 30 and int(ib4[0, -1].item()) == 30, "ST6 last must be goal"
    print("[selftest] ST6 index-midpoint interpolation OK", flush=True)

    # ST7 (RANDOM WAYPOINT): random boundaries avoid start/goal and (typically) differ from bisection
    g7 = np.random.default_rng(7)
    rb = _discover_random_boundaries(starts5, goals5, 24, seg_len=6, depth=6, g=g7)
    for j in range(rb.shape[1] - 1):
        col = rb[:, j]
        assert not bool(((col == starts5) | (col == goals5)).any()), "ST7 random hit start/goal"
    assert int(rb[0, -1].item()) == 5, "ST7 random last must be goal"
    print("[selftest] ST7 random waypoints avoid start/goal OK", flush=True)

    # ST8 (SPECTRAL/CLUSTER MASKS): eigh runs; masks non-empty, ~CAND_FRAC size, bool
    sm = spectral_candidate_mask(Rt, 0.10)
    cm = cluster_candidate_mask(Rt, 2, 0.10)
    assert sm.dtype == torch.bool and cm.dtype == torch.bool, "ST8 mask dtype"
    assert 2 <= int(sm.sum()) <= Vt and 2 <= int(cm.sum()) <= Vt, "ST8 mask size out of range"
    print("[selftest] ST8 spectral/cluster masks OK (spec_k=%d clus_k=%d of V=%d)"
          % (int(sm.sum()), int(cm.sum()), Vt), flush=True)

    # ST9 (BOUNDARIES->HOPS SCHEDULE): matches the ancestor build_waypoint_idx schedule
    bstate = torch.tensor([[100, 200, 300]], dtype=torch.long, device=DEVICE)  # 3 boundaries d6 s2
    hops = _boundaries_to_hops(bstate, seg_len=2, depth=6)
    exp = torch.tensor([100, 100, 200, 200, 300, 300], dtype=torch.long, device=DEVICE)
    assert bool((hops[0] == exp).all()), "ST9 hop schedule wrong: %s" % hops[0].tolist()
    print("[selftest] ST9 boundaries->hops schedule OK", flush=True)

    # ST10 (CLOSURE + RECOVERY FORMULAS)
    flat_, oexec_, horc_, bwp_ = 0.08, 0.94, 0.86, 0.30
    ac = (bwp_ - flat_) / (oexec_ - flat_)
    rr = (bwp_ - flat_) / (horc_ - flat_)
    assert abs(ac - 0.25581) < 1e-3, "ST10 auton_closure off: %.5f" % ac
    assert abs(rr - 0.28205) < 1e-3, "ST10 recovery_ratio off: %.5f" % rr
    print("[selftest] ST10 closure=%.3f recovery=%.3f formulas OK" % (ac, rr), flush=True)

    # ST11 (spearman + entropy + binom)
    assert abs(_spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) - 1.0) < 1e-9, "ST11 spearman"
    assert abs(decision_entropy(4, 6) - 12.0) < 1e-9, "ST11 entropy op4_d6"
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0 and abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST11 binom"
    print("[selftest] ST11 spearman + entropy + binom OK", flush=True)

    # ST12 (FULL PIPELINE single-seed structural: all 9 arms + diagnostics present; oracle sane)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_waypoint_discovery")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST12 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST12 missing arm %s" % arm
    for fld in ("degenerate_rate", "anti_tautology_corr", "exact_match_rate", "best_wp_arm"):
        assert fld in r["regime_results"][rk0], "ST12 missing field %s" % fld
    oexec = r["regime_results"][rk0]["arms"]["oracle_exec"]
    assert oexec >= 0.5, "ST12 oracle_exec too low (%.3f)" % oexec
    print("[selftest] ST12 pipeline OK arms=%d oracle_exec=%.3f" % (len(ARMS), oexec), flush=True)

    # ST13 (VERDICT WIRING)
    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    def _mk(n_ops, V, dd, flat, oexec, horc, open_a, spec_a, clus_a, rand, idxm,
            degen=0.02, taut=0.10, exact=0.20, rr=0.60,
            n_bwp_only=None, n_idx_only=2, n_rand_only_idx=2):
        best = max(open_a, spec_a, clus_a)
        bwp_arm = ("wp_bisect_open" if open_a == best else
                   ("wp_bisect_spectral" if spec_a == best else "wp_bisect_cluster_exit"))
        if n_bwp_only is None:
            n_bwp_only = 45 if best > flat + 0.1 else 1
        arms = {"flat_gonogo": flat, "oracle_exec": oexec, "hier_oracle": horc,
                "hier_shuffled": 0.02, "wp_bisect_open": open_a, "wp_bisect_spectral": spec_a,
                "wp_bisect_cluster_exit": clus_a, "wp_random_state": rand,
                "wp_index_midpoint": idxm}
        oth = {"flat_gonogo": "f", "oracle_exec": "oracle_true_seq", "hier_oracle": "ho",
               "hier_shuffled": "hs", "wp_bisect_open": "op", "wp_bisect_spectral": "sp",
               "wp_bisect_cluster_exit": "cl", "wp_random_state": "rd", "wp_index_midpoint": "ix"}
        return {"n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
                "arms": arms, "op_trace_hashes": oth, "best_wp_arm": bwp_arm, "best_alpha": 0.2,
                "wr_flat": 1.0, "wr_oracle": 1.0, "wr_shuf": 1.0, "wr_open": 1.0,
                "reach_rank_chance": 1.0 / n_ops, "reach_rank_test": rr,
                "degenerate_rate": degen, "anti_tautology_corr": taut, "exact_match_rate": exact,
                "paired": {"n_bwp_only_vs_flat": n_bwp_only, "n_flat_only_vs_bwp": 2,
                           "n_bwp_only_vs_rand": 40, "n_rand_only_vs_bwp": 2,
                           "n_idx_only_vs_rand": n_idx_only, "n_rand_only_vs_idx": n_rand_only_idx,
                           "n_test": 60}}

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    reg_lo = regime_key(4, 1200, 4)
    reg_hi = regime_key(4, 1200, 6)
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4}, {"n_ops": 4, "V": 1200, "dd": 6}]
    REGIME_KEYS = [reg_lo, reg_hi]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    try:
        # HARD_PASS: focus op4_d6, best_wp(open)=0.40, flat=0.08, oexec=0.94, horc=0.86, rand=0.12,
        #   idx=0.13 -> auton_closure=(0.40-0.08)/0.86=0.372>=0.15; recovery=(0.40-0.08)/0.78=0.410
        #   >=0.20; lift_flat=0.32>0.05; lift_random=0.28>0.10; index_gap=0.01<0.05; guards clean.
        ps = {}
        for s in ["7", "17", "23"]:
            ps[s] = {"regime_results": {
                reg_lo: _mk(4, 1200, 4, flat=0.30, oexec=0.95, horc=0.90, open_a=0.55,
                            spec_a=0.50, clus_a=0.48, rand=0.25, idxm=0.26),
                reg_hi: _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86, open_a=0.40,
                            spec_a=0.33, clus_a=0.31, rand=0.12, idxm=0.13),
            }}
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "ST13 expected HARD_PASS got %s" % out["verdict"]
        assert out["focus_regime"] == reg_hi, "ST13 focus should be high-entropy"
        assert out["focus_best_wp_arm"] == "wp_bisect_open", "ST13 best_wp should be open"

        # HARD_FAIL: best_wp ~= flat (no lift)
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86,
                                                  open_a=0.11, spec_a=0.10, clus_a=0.09,
                                                  rand=0.10, idxm=0.10, n_bwp_only=1)
        out2 = aggregate_and_verdict(ps)
        assert out2["verdict"] == "HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION", \
            "ST13 expected HARD_FAIL got %s" % out2["verdict"]

        # HARD_FAIL via indistinguishable-from-random: best_wp beats flat but not random
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86,
                                                  open_a=0.30, spec_a=0.28, clus_a=0.27,
                                                  rand=0.28, idxm=0.29)
        out2b = aggregate_and_verdict(ps)
        assert out2b["verdict"] == "HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION", \
            "ST13 expected HARD_FAIL(random) got %s" % out2b["verdict"]

        # MIDDLE_BAND: beats flat+random by margins but recovery_ratio < 0.20
        #   best_wp=0.20, flat=0.08, horc=0.86 -> recovery=(0.20-0.08)/0.78=0.154<0.20; lift_random
        #   =0.20-0.09=0.11>0.10; lift_flat=0.12>0.05.
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86,
                                                  open_a=0.20, spec_a=0.18, clus_a=0.17,
                                                  rand=0.09, idxm=0.10)
        out3 = aggregate_and_verdict(ps)
        assert out3["verdict"] == "MIDDLE_BAND_RECOVERY_BELOW_20", \
            "ST13 expected MIDDLE recovery got %s" % out3["verdict"]

        # MIDDLE via degenerate guard: strong accuracy but degenerate_rate high
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86,
                                                  open_a=0.40, spec_a=0.33, clus_a=0.31,
                                                  rand=0.12, idxm=0.13, degen=0.25)
        out4 = aggregate_and_verdict(ps)
        assert out4["verdict"] == "MIDDLE_BAND_DEGENERATE_GUARD", \
            "ST13 expected MIDDLE degenerate got %s" % out4["verdict"]

        # INCONCLUSIVE index-order leak: index >> random with significance
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk(4, 1200, 6, flat=0.08, oexec=0.94, horc=0.86,
                                                  open_a=0.40, spec_a=0.33, clus_a=0.31,
                                                  rand=0.12, idxm=0.40, n_idx_only=40, n_rand_only_idx=2)
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
    print("[selftest] ST13 verdict wiring OK (HARD_PASS; HARD_FAIL flat+random; MIDDLE recovery+"
          "degenerate; INCONCLUSIVE leak+no-regime)", flush=True)


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

    print("[%s] mode=%s device=%s N=%d n_ops=%s depths=%s seeds=%s gamma=%.2f seg_len=%d "
          "regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA, SEG_LEN,
             REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST13 (TD shrink, argmax, reach-matrix identity, "
                               "bisection-fires, degenerate-masking, index interpolation, random "
                               "waypoint, spectral/cluster masks, hop schedule, closure/recovery "
                               "formulas, spearman/entropy/binom, pipeline, verdict wiring)",
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
