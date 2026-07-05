"""pfc_gate_branching_depth_entropy_grid_v1 -- does a HIERARCHICAL-OPTIONS gate recover the
FLAT Go/NoGo control gate's depth-6 HIGH-branching collapse, and does the benefit track
decision-entropy (log2(n_ops)*depth) across an n_ops x depth grid?

WHY (Director steer 2026-07-05):
  The deeper-regime cell's OWN smoke falsifies its headline (longer SR horizon / gamma) and
  confirms a BRANCHING-factor story:
  MEASURED@data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json (N=2048, 3 seeds):
    op4_V300_d6 gonogo g0.85 = 0.10417 == g0.95 = 0.10417  (gamma bit-identical -> inert)
    op2_V300_d6 gonogo g0.85 = 0.38889  (branching 4->2 at fixed depth-6 -> ~3.7x closure)
    horizon_attributable = -0.008, horizon_is_the_lever = False.
  v2 FULL (MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json): flat gate PROVEN at
  depth-4 (V1200_d4 closure=0.661) but COLLAPSES to gonogo=0.075 (closure=0.073) at depth-6.

  Brain-literature convergence (independent lit-scan, generic terms):
  CITED@Redgrave-Prescott-Gurney 1999 (BG selection = arbitration among competing channels);
  Hick 1952 (RT/accuracy ~ log2(N-alternatives)); Usher-McClelland 2001 (multi-alternative
  LCA). SEPARATELY the options / temporal-abstraction lineage says the fix for DEPTH is
  HIERARCHY, not a bigger buffer: CITED@Sutton-Precup-Singh 1999 (options / SMDP);
  Botvinick-Niv-Barto 2009 (HRL); Frank-Badre corticostriatal HRL. So: chunk the deep /
  high-branching decision into low-horizon sub-goals (options) so every gating decision faces
  a NEAR target where the trained SR reach is accurate.

MECHANISM UNDER TEST (NOT assumed):
  A HIERARCHICAL-OPTIONS gate. The depth-d op-chain is decomposed into ceil(d/SEG_LEN)
  segments. At each segment boundary the arm re-anchors its goal to the NEXT sub-goal
  (waypoint) instead of the far final goal; within a segment the SAME flat Go/NoGo gate runs
  but toward a target <= SEG_LEN hops away, where the trained SR reach is informative. This
  bounds the per-decision REACH HORIZON to SEG_LEN, sidestepping the far-goal reach starvation
  that sinks the flat gate at depth-6 -- WITHOUT touching gamma (which smoke showed is inert:
  extending M's horizon fails because M cannot represent 6-hop-distant successor features; but
  re-anchoring to a NEAR waypoint keeps every reach evaluation in M's accurate short range).

  SUB-GOAL SOURCE (declared oracle-assist, scoped honestly): the waypoint STATES at segment
  boundaries are the true intermediate states of the chain (an assumed-optimal top-level
  option policy). The arm is NOT handed the OPS -- it must still SELECT ops via the gate to
  reach each waypoint. The scientific claim is therefore scoped: "GIVEN a sub-goal
  decomposition, does per-segment low-horizon gating recover the flat collapse?" Autonomous
  waypoint DISCOVERY is an explicit FOLLOW-ON, not claimed here. Two rails keep it honest:
    (1) hier_shuffled NEGATIVE CONTROL: identical segment structure + waypoint SCHEDULE, but
        waypoints drawn from a DIFFERENT chain (wrong decomposition). If hier's win over flat
        were merely "extra reach score helps," shuffled would win too. HP requires
        hier_options >> hier_shuffled -> the CORRECT decomposition is load-bearing.
    (2) reach_tcos_corr < 0.85 (trained-M reach is not target-cosine in disguise; reused).

ARMS (paired -- share E, W_ops, M, and the SAME test chains per (regime,seed)):
  v1_no_goal            goal-blind manifold reference
  additive_baseline     static additive goal-bias, alpha tuned on train (fair-regime labeler)
  flat_control_identity flat gate with reach:=target-cosine (M=identity); anti-tautology foil
  oracle                applies the true op_seq (ceiling)
  flat_gonogo           FLAT SR Go/NoGo gate toward the FINAL goal (the arm that COLLAPSES)
  hier_options          HIERARCHICAL-OPTIONS gate (the fix; correct waypoints)
  hier_shuffled         hier structure with WRONG (other-chain) waypoints (neg control)

GRID: n_ops in {2,3,4} (BRANCHING) x depth in {4,6,8} (DEPTH). entropy = log2(n_ops)*depth
  (Hick-generalized decision-entropy). gamma FIXED 0.85 (smoke proved it inert). Reports the
  entropy surface: where does flat collapse, and where does hierarchy help most?

PRIMARY DISCRIMINATOR (per regime; FLAT-referenced, so it survives additive-floor at op4_d6):
  headroom_flat = oracle - flat_gonogo
  hier_closure  = (hier_options - flat_gonogo) / headroom_flat   (fraction of flat->oracle gap closed)
  hier_lift     = hier_options - flat_gonogo
  shuf_gap      = hier_options - hier_shuffled   (correct-decomposition load-bearingness)
  entropy       = log2(n_ops) * depth
FOCUS regime = highest-entropy regime with oracle>=0.90 AND headroom_flat>=0.10 (the HIGH-
  branching deep regime where flat collapses; op4_d6 for smoke).

CONTRACT (Director 2026-07-05):
  HARD_PASS : at the FOCUS (high-branching deep) regime, hier_closure >= 0.25 AND
              hier_lift > 0.05 AND shuf_gap > 0.10 (hier > shuffled) AND reach_tcos_corr < 0.85
              AND sign_p(hier vs flat) < 0.05 AND reach_rank > 1/n_ops + 0.05 AND oracle >= 0.90
              AND cv(hier) < 0.10 (FULL only) AND no af_collision.
              => hierarchical decomposition EXTENDS control past the flat depth-6 collapse; the
                 branching/decision-entropy lever is real and hierarchy is the fix.
  HARD_FAIL : at the focus regime, hier_lift <= 0.05 (hierarchy does NOT beat flat) OR
              shuf_gap <= 0.05 (correct decomposition adds nothing beyond arbitrary waypoint
              bias) => branching-reduction-via-hierarchy is NOT the lever (an honest bound).
  MIDDLE_BAND: hierarchy helps (hier_lift>0.05) but hier_closure in [0.05,0.25), OR clears 25%
              but shuf_gap/cv/anti-tautology fails.
  INCONCLUSIVE_NO_DISCRIMINATING_REGIME: no regime has oracle>=0.90 AND headroom_flat>=0.10.
  Reported REGARDLESS: full entropy surface (flat_gonogo, hier_options, hier_lift, hier_closure
  per (n_ops,depth,entropy)); spearman(hier_lift, entropy); spearman(flat, -entropy) vs
  spearman(flat, -depth) (does decision-entropy predict flat collapse better than depth alone);
  op2_d8-vs-op4_d4 iso-entropy cross-over (if present in grid); hier_extends_depth flag.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hier_options vs flat_gonogo and vs
#   hier_shuffled op-trace hash per seed; exempt when best_w_reach==0 legitimate reduction)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor; reachability
#   by feasibility (v2 measured flat closure=0.66 at fair d4; op2_d6 gonogo=0.39 shows the gate
#   works when per-decision complexity is low -- hierarchy manufactures that low-complexity regime)
# - baseline_in_band at smoke (META_RULE_AG): reported per-regime for the ADDITIVE reference, but
#   the HIER discriminator is FLAT-referenced (headroom_flat), which is measurable even where
#   additive floors (op4_d6). Fair-for-hier gate = oracle>=0.90 AND headroom_flat>=0.10.
# - discriminator survives scale: smoke holds N/V == FULL AND includes the focus op4_d6 at
#   IDENTICAL depth -> per-hop cleanup difficulty + depth-dependence match FULL (option C preview)
# - HARD_PASS strictly at/above contract floor hier_closure>=0.25 (META_RULE_L)
# - HP_SCOPE: HP gates apply ONLY to hier_options vs flat_gonogo at the FOCUS regime; oracle_rail
#   (>=0.90) applies to ORACLE; shuf_gap applies to hier_options vs hier_shuffled
# - cardinality_ok: EXPECTED_N_UNITS = n_arms * n_seeds * n_regimes
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank +
#   shuffled-control gates)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Compute architecture: (a) batched-GPU. SR-TD training (gamma=0.85 fixed), operator application,
cleanup, reach = batched matmuls on cuda-if-available. Chains batched; within-chain hops are
sequential (genuine dependency). SR trained once per (V,n_ops) group and shared across depths.
FULL strongly prefers overnight_queue (GPU). Storage strategy: sharded (each operator its own W
matrix; M a learned value operator, not an item store). No bundled store.
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress line +
per (seed,V,n_ops) heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-05 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-05_pfc_gate_branching_depth_entropy_grid_v1.md
Cites:
  data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json (branching-not-horizon evidence)
  data/exp_pfc_gate_cfrpe_trained_v2/metrics.json (v2 FULL: d4 proven, d6 collapse)
  experiments/exp_pfc_gate_cfrpe_deeper_regime_v1.py (trainer/harness reused verbatim)
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

ANCHOR_NAME = "pfc_gate_branching_depth_entropy_grid_v1"

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
HP_CLOSURE_FLOOR = 0.25            # contract: hier closes >= 25% of the flat->oracle headroom
HP_HIER_LIFT_MIN = 0.05           # hier must measurably beat flat
HP_SHUF_GAP_MIN = 0.10            # correct-decomposition load-bearing (hier >> shuffled)
HP_REACH_TARGETCOS_CORR_MAX = 0.85  # reach must NOT be target-cosine in disguise
HP_CV_MAX = 0.10                  # cross-seed cv on hier_options at focus (FULL only)
HP_SIGN_TEST_P = 0.05
HP_REACH_RANK_MARGIN = 0.05       # mechanism-fires: reach_rank > 1/n_ops + margin
HF_HIER_LIFT_CEIL = 0.05          # HARD_FAIL: hier <= flat + 0.05 at focus
HF_SHUF_GAP_CEIL = 0.05           # HARD_FAIL: decomposition adds nothing beyond arbitrary bias
ORACLE_RAIL_MIN = 0.90
HEADROOM_FLAT_MIN = 0.10          # fair-for-hier: oracle - flat must leave measurable room
ENTROPY_MODEL_MARGIN = 0.15       # entropy predicts flat collapse better than depth by this rho
BASELINE_IN_BAND_LO = 0.05        # META_RULE_AG additive-reference reporting band
BASELINE_IN_BAND_HI = 0.95

DENSITY = 0.21                     # n_train_triples_per_op / V (matches v2/deeper)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2

GAMMA = 0.85                       # FIXED (smoke proved gamma inert at d6)
ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]
SEG_LEN = 2                        # hierarchical segment length (per-decision reach horizon cap)

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, dd). n_ops is the BRANCHING axis; dd is the DEPTH axis. SR M is trained
# once per unique (V,n_ops) group at GAMMA and shared across depths. SMOKE holds N/V == FULL and
# includes the focus op4_d6 at IDENTICAL depth -> matched per-hop difficulty + depth-dependence.
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
    # op4_V300_d6 (flat collapses; hier must beat) at matched N/V + depth (option C preview).
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

ARMS = ["v1_no_goal", "additive_baseline", "flat_control_identity", "oracle",
        "flat_gonogo", "hier_options", "hier_shuffled"]
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


def reach_rank_chance(n_ops: int) -> float:
    return 1.0 / float(n_ops)


def decision_entropy(n_ops: int, dd: int) -> float:
    return float(math.log2(n_ops) * dd)


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_ops_set=%s,depth_set=%s,seeds=%s,gamma=%.2f,seg_len=%d,regimes=%s,"
    "density=%.3f,sr_steps=%d,sr_batch=%d,rollout_per_V=%d,lr=%.2f,lr_decay_end=%.2f,alphas=%s,"
    "w_reach=%s,n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_closure>=%.2f,shuf_gap>%.2f,cv<%.2f,corr<%.2f,sign_p<%.2f,reach_rank_margin=%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS_SET, DEPTH_SET, SEEDS, GAMMA, SEG_LEN, REGIME_KEYS, DENSITY,
    SR_STEPS, SR_BATCH, ROLLOUT_PER_V, SR_LR, LR_DECAY_END, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_CLOSURE_FLOOR, HP_SHUF_GAP_MIN, HP_CV_MAX, HP_REACH_TARGETCOS_CORR_MAX, HP_SIGN_TEST_P,
    HP_REACH_RANK_MARGIN,
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
# primitives (torch, batched, device-agnostic) -- reused verbatim from deeper cell
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
# KB + chains (exact-length paths; train and test disjoint chain sets)
# ============================================================================
def make_kb_and_chains(n_ops: int, V: int, density: float,
                       n_train_chains: int, n_test_chains: int,
                       depths: List[int], g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]]]:
    """Returns (per_op_triples, train_chains_by_depth, test_chains_by_depth). Each chain is
    (start, op_seq[len==depth], target) with a guaranteed exact-length path. Train/test are
    distinct draws over the SAME operator graph."""
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
# cfrpe-trained SR transport M (TD(0); gamma FIXED). reused verbatim from deeper cell.
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
# arms (batched across chains; hops are sequential within a chain)
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
    """FLAT batched op-selection arm. mode in {v1, additive, gonogo, gonogo_control}. Reaches
    toward the FINAL goal every hop (full reach horizon = depth-1). Returns (correct[n], op_trace[n,depth])."""
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
            if mode == "v1":
                sc = manifold
            elif mode == "additive":
                sc = alpha * goal_sim + w_manifold * manifold
            elif mode == "gonogo":
                reach = reach_value(cleaned, goal_E, M)
                sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach
            elif mode == "gonogo_control":
                reach = reach_control_targetcos(cleaned, goal_E)
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


def oracle_trajectory_idx(chains, W_ops: List[torch.Tensor], E: torch.Tensor, depth: int
                          ) -> torch.Tensor:
    """Per-hop cleaned-state INDICES along the true (oracle) trajectory -> [n_chains, depth+1].
    Column 0 = start; column depth is FORCED to the declared target (exact goal)."""
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
    traj[:, depth] = targets   # exact goal at the final boundary
    return traj


def build_waypoint_idx(traj_idx: torch.Tensor, seg_len: int, depth: int, shuffle: bool
                       ) -> torch.Tensor:
    """Waypoint (sub-goal) state index PER HOP -> [n_chains, depth]. For hop h the sub-goal is the
    trajectory state at the next segment boundary min((h//seg_len+1)*seg_len, depth). If shuffle,
    each chain uses ANOTHER chain's trajectory+target (roll by +1) -> wrong decomposition."""
    src = torch.roll(traj_idx, shifts=1, dims=0) if shuffle else traj_idx
    wp_hop = [min(((h // seg_len) + 1) * seg_len, depth) for h in range(depth)]
    wp_hop_t = torch.tensor(wp_hop, dtype=torch.long, device=DEVICE)
    return src[:, wp_hop_t]   # [n_chains, depth]


def run_hier_arm(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                 M: torch.Tensor, depth: int, seg_len: int, alpha: float, w_reach: float
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """HIERARCHICAL-OPTIONS arm. mode in {hier, hier_shuffled}. Re-anchors the goal to the current
    segment's sub-goal (waypoint) so the per-decision reach horizon is bounded by seg_len. The arm
    still SELECTS ops via the flat Go/NoGo gate (toward the near sub-goal). Correctness measured
    against the arm's OWN declared target. Returns (correct[n], op_trace[n,depth])."""
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    traj_idx = oracle_trajectory_idx(chains, W_ops, E, depth)
    wp_idx = build_waypoint_idx(traj_idx, seg_len, depth, shuffle=(mode == "hier_shuffled"))
    wp_E_all = E[wp_idx]   # [n_chains, depth, n_dim]
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


def reach_rank_acc(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                   M: torch.Tensor, depth: int) -> float:
    """Mechanism-fires probe: along the TRUE trajectory, does argmax_op reach == the true op?
    Chance = 1/n_ops. Reach toward the FINAL goal (the flat gate's target)."""
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


def reach_vs_targetcos_corr(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                            M: torch.Tensor, depth: int) -> float:
    """Anti-tautology guard: Pearson corr between learned-M reach and raw target-cosine across
    candidate ops along the true trajectory. Near 1.0 => reach IS target-cosine in disguise."""
    starts, targets, op_seqs = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()
    goal_E = E[targets]
    n_ops = len(W_ops)
    op_seq_t = torch.tensor(op_seqs, dtype=torch.long, device=DEVICE)
    reach_vals: List[float] = []
    tcos_vals: List[float] = []
    for hop in range(depth):
        cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            cand_idx_all[:, op] = idx
            reach_vals.extend(reach_value(cleaned, goal_E, M).detach().cpu().tolist())
            tcos_vals.extend(reach_control_targetcos(cleaned, goal_E).detach().cpu().tolist())
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx_all[row, op_seq_t[:, hop]]
        state = E[new_idx]
    a = np.asarray(reach_vals, dtype=np.float64)
    b = np.asarray(tcos_vals, dtype=np.float64)
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


# ============================================================================
# stats
# ============================================================================
def binom_two_sided_p(k: int, n: int, p: float = 0.5) -> float:
    """Two-sided binomial p-value for k successes in n trials. Exact for small n."""
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
    """Average-rank of x (ties -> mean rank)."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[order] = np.arange(1, len(x) + 1, dtype=np.float64)
    # average ties
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts), dtype=np.float64)
    for i in range(len(x)):
        sums[inv[i]] += ranks[i]
    avg = sums / counts
    return avg[inv]


def _spearman(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation. Returns 0.0 if <3 points or a variable is constant."""
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
def _tune_wreach_flat(mode: str, train_c, W_ops, E, M, dd, alpha) -> Tuple[float, float]:
    best_wr, best_acc = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm(mode, train_c, W_ops, E, M, dd, alpha, wr)[0].mean()
        if acc > best_acc:
            best_acc, best_wr = acc, wr
    return best_wr, float(best_acc)


def _tune_wreach_hier(mode: str, train_c, W_ops, E, M, dd, seg_len, alpha) -> Tuple[float, float]:
    best_wr, best_acc = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_hier_arm(mode, train_c, W_ops, E, M, dd, seg_len, alpha, wr)[0].mean()
        if acc > best_acc:
            best_acc, best_wr = acc, wr
    return best_wr, float(best_acc)


def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, train_by_d, test_by_d) -> Dict[str, Any]:
    """Tune on train, evaluate all arms on test (paired). One seed, gamma fixed."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    # tune alpha (additive; reach-independent) on train
    best_alpha, best_add_train = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_arm("additive", train_c, W_ops, E, M, dd, a, 0.0)[0].mean()
        if acc > best_add_train:
            best_add_train, best_alpha = acc, a

    # tune w_reach on train for each reach-using arm (steelman each)
    best_wr_flat, flat_train = _tune_wreach_flat("gonogo", train_c, W_ops, E, M, dd, best_alpha)
    best_wr_ctrl, ctrl_train = _tune_wreach_flat("gonogo_control", train_c, W_ops, E, M, dd, best_alpha)
    best_wr_hier, hier_train = _tune_wreach_hier("hier", train_c, W_ops, E, M, dd, SEG_LEN, best_alpha)
    best_wr_shuf, shuf_train = _tune_wreach_hier("hier_shuffled", train_c, W_ops, E, M, dd, SEG_LEN, best_alpha)

    # eval on TEST (paired base)
    v1_c, v1_tr = run_selection_arm("v1", test_c, W_ops, E, M, dd, 0.0, 0.0)
    add_c, add_tr = run_selection_arm("additive", test_c, W_ops, E, M, dd, best_alpha, 0.0)
    ctrl_c, ctrl_tr = run_selection_arm("gonogo_control", test_c, W_ops, E, M, dd, best_alpha, best_wr_ctrl)
    flat_c, flat_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr_flat)
    hier_c, hier_tr = run_hier_arm("hier", test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, best_wr_hier)
    shuf_c, shuf_tr = run_hier_arm("hier_shuffled", test_c, W_ops, E, M, dd, SEG_LEN, best_alpha, best_wr_shuf)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)

    arms: Dict[str, float] = {
        "v1_no_goal": float(v1_c.mean()),
        "additive_baseline": float(add_c.mean()),
        "flat_control_identity": float(ctrl_c.mean()),
        "oracle": float(orc_c.mean()),
        "flat_gonogo": float(flat_c.mean()),
        "hier_options": float(hier_c.mean()),
        "hier_shuffled": float(shuf_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "v1_no_goal": hashlib.sha256(v1_tr.tobytes()).hexdigest()[:16],
        "additive_baseline": hashlib.sha256(add_tr.tobytes()).hexdigest()[:16],
        "flat_control_identity": hashlib.sha256(ctrl_tr.tobytes()).hexdigest()[:16],
        "oracle": "oracle_true_seq",
        "flat_gonogo": hashlib.sha256(flat_tr.tobytes()).hexdigest()[:16],
        "hier_options": hashlib.sha256(hier_tr.tobytes()).hexdigest()[:16],
        "hier_shuffled": hashlib.sha256(shuf_tr.tobytes()).hexdigest()[:16],
    }

    rr_test = reach_rank_acc(test_c, W_ops, E, M, dd)
    rr_train = reach_rank_acc(train_c, W_ops, E, M, dd)
    rtc_test = reach_vs_targetcos_corr(test_c, W_ops, E, M, dd)

    # paired hier vs flat + hier vs shuffled (on the SAME test chains)
    paired = {
        "n_hier_only": int(((hier_c) & (~flat_c)).sum()),
        "n_flat_only": int(((flat_c) & (~hier_c)).sum()),
        "n_both": int((hier_c & flat_c).sum()),
        "n_neither": int(((~hier_c) & (~flat_c)).sum()),
        "n_hier_over_shuf": int(((hier_c) & (~shuf_c)).sum()),
        "n_shuf_over_hier": int(((shuf_c) & (~hier_c)).sum()),
        "n_test": int(len(hier_c)),
    }

    return {
        "n_ops": n_ops, "V": V, "dd": dd,
        "entropy": decision_entropy(n_ops, dd),
        "arms": arms,
        "op_trace_hashes": op_trace_hashes,
        "best_alpha": float(best_alpha),
        "best_w_reach_flat": float(best_wr_flat),
        "best_w_reach_ctrl": float(best_wr_ctrl),
        "best_w_reach_hier": float(best_wr_hier),
        "best_w_reach_shuf": float(best_wr_shuf),
        "additive_train_acc": float(best_add_train),
        "flat_train_acc": float(flat_train),
        "hier_train_acc": float(hier_train),
        "reach_rank_chance": reach_rank_chance(n_ops),
        "reach_rank_test": float(rr_test),
        "reach_rank_train": float(rr_train),
        "reach_tcos_corr_test": float(rtc_test),
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
        print("[seed=%d op%d V=%d] SR: err %s->%s M_norm=%.3f n_trans=%d clamp=%d"
              % (seed, n_ops, V, sr_diag["err_first"], sr_diag["err_last"],
                 sr_diag["final_M_norm"], sr_diag["n_transitions"],
                 sr_diag["n_clamped_steps"]), flush=True)

        for dd in depths_needed:
            rec = _eval_regime(n_ops, V, dd, E, W_ops, M, train_by_d, test_by_d)
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(n_ops, V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s ent=%.2f] V1=%.3f ADD=%.3f CTRL=%.3f ORC=%.3f | "
                  "FLAT=%.3f HIER=%.3f SHUF=%.3f (a=%.2f wrH=%.1f rr=%.3f)"
                  % (seed, key, rec["entropy"], a["v1_no_goal"], a["additive_baseline"],
                     a["flat_control_identity"], a["oracle"], a["flat_gonogo"],
                     a["hier_options"], a["hier_shuffled"], rec["best_alpha"],
                     rec["best_w_reach_hier"], rec["reach_rank_test"]), flush=True)

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

        arm_means, arm_cvs, arm_stds = {}, {}, {}
        for arm in ARMS:
            vals = _arm_col(rk, arm)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                arm_means[arm] = m; arm_stds[arm] = sd
                arm_cvs[arm] = float(sd / m) if m > 1e-6 else 0.0
            else:
                arm_means[arm] = 0.0; arm_stds[arm] = 0.0; arm_cvs[arm] = 0.0

        add = arm_means["additive_baseline"]
        ctrl = arm_means["flat_control_identity"]
        orc = arm_means["oracle"]
        flat = arm_means["flat_gonogo"]
        hier = arm_means["hier_options"]
        shuf = arm_means["hier_shuffled"]

        headroom_flat = orc - flat
        headroom_add = orc - add
        hier_closure = ((hier - flat) / headroom_flat) if headroom_flat > 1e-6 else 0.0
        hier_lift = hier - flat
        shuf_gap = hier - shuf
        flat_closure_vs_add = ((flat - add) / headroom_add) if headroom_add > 1e-6 else 0.0
        baseline_in_band = (BASELINE_IN_BAND_LO < add < BASELINE_IN_BAND_HI)
        rr_chance = reach_rank_chance(r["n_ops"])
        rr_min = rr_chance + HP_REACH_RANK_MARGIN
        rr_test = _mean(_field_col(rk, "reach_rank_test"))
        rtc = _mean(_field_col(rk, "reach_tcos_corr_test"))
        entropy = decision_entropy(r["n_ops"], r["dd"])

        # pooled paired sign-test across seeds (hier vs flat)
        n_hier_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_hier_only"]) for k in present)
        n_flat_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_flat_only"]) for k in present)
        n_disc = n_hier_only + n_flat_only
        sign_p = binom_two_sided_p(n_hier_only, n_disc, 0.5) if n_disc > 0 else 1.0
        n_hier_over_shuf = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_hier_over_shuf"]) for k in present)
        n_shuf_over_hier = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_shuf_over_hier"]) for k in present)

        # arms-differ (META_RULE_AF): hier vs flat AND hier vs shuffled op-traces per seed,
        # unless the hier w_reach was legitimately tuned to 0 (reduces to flat/additive form).
        af_collision = False
        for k in present:
            rr = per_seed[k]["regime_results"][rk]
            wr_h = rr["best_w_reach_hier"]
            h_hash = rr["op_trace_hashes"]["hier_options"]
            f_hash = rr["op_trace_hashes"]["flat_gonogo"]
            s_hash = rr["op_trace_hashes"]["hier_shuffled"]
            if wr_h > 1e-9:
                if h_hash == f_hash or h_hash == s_hash:
                    af_collision = True

        oracle_rail_ok = bool(orc >= ORACLE_RAIL_MIN)
        headroom_ok = bool(headroom_flat >= HEADROOM_FLAT_MIN)
        hier_cv = arm_cvs["hier_options"]

        hp_ok = (oracle_rail_ok and headroom_ok
                 and hier_closure >= HP_CLOSURE_FLOOR
                 and hier_lift > HP_HIER_LIFT_MIN
                 and shuf_gap > HP_SHUF_GAP_MIN
                 and rtc < HP_REACH_TARGETCOS_CORR_MAX
                 and sign_p < HP_SIGN_TEST_P
                 and (hier_cv < HP_CV_MAX or RUN_MODE != "full")
                 and rr_test > rr_min
                 and not af_collision)

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "entropy": entropy,
            "arm_means": arm_means, "arm_cvs": arm_cvs, "arm_stds": arm_stds,
            "additive": add, "control_identity": ctrl, "oracle": orc,
            "flat_gonogo": flat, "hier_options": hier, "hier_shuffled": shuf,
            "headroom_flat": float(headroom_flat), "headroom_add": float(headroom_add),
            "hier_closure": float(hier_closure), "hier_lift": float(hier_lift),
            "shuf_gap": float(shuf_gap), "flat_closure_vs_add": float(flat_closure_vs_add),
            "baseline_in_band": bool(baseline_in_band),
            "reach_rank_chance": float(rr_chance), "reach_rank_min": float(rr_min),
            "reach_rank_test": float(rr_test), "reach_tcos_corr_test": float(rtc),
            "sign_test_p": float(sign_p),
            "n_hier_only": int(n_hier_only), "n_flat_only": int(n_flat_only),
            "n_hier_over_shuf": int(n_hier_over_shuf), "n_shuf_over_hier": int(n_shuf_over_hier),
            "oracle_rail_ok": oracle_rail_ok, "headroom_ok": headroom_ok,
            "hier_cv": float(hier_cv), "af_collision": bool(af_collision),
            "hp_ok": bool(hp_ok),
        }

    # ---- entropy surface + models (reported regardless of verdict) ----
    grid_ents, grid_flat, grid_hier, grid_lift, grid_depth = [], [], [], [], []
    for rk, v in per_regime.items():
        if v["n_seeds"] > 0:
            grid_ents.append(v["entropy"]); grid_flat.append(v["flat_gonogo"])
            grid_hier.append(v["hier_options"]); grid_lift.append(v["hier_lift"])
            grid_depth.append(float(v["dd"]))
    spearman_hier_lift_vs_entropy = _spearman(grid_lift, grid_ents)
    spearman_flat_vs_entropy = _spearman(grid_flat, grid_ents)
    spearman_flat_vs_depth = _spearman(grid_flat, grid_depth)
    entropy_beats_depth = bool(abs(spearman_flat_vs_entropy) - abs(spearman_flat_vs_depth)
                               >= ENTROPY_MODEL_MARGIN)

    # iso-entropy cross-over: op2_d8 (low branch, high depth) vs op4_d4 (high branch, low depth)
    crossover = {}
    op2d8 = next((v for v in per_regime.values() if v["n_ops"] == 2 and v["dd"] == 8), None)
    op4d4 = next((v for v in per_regime.values() if v["n_ops"] == 4 and v["dd"] == 4), None)
    if op2d8 is not None and op4d4 is not None:
        crossover = {
            "op2_d8_flat": op2d8["flat_gonogo"], "op4_d4_flat": op4d4["flat_gonogo"],
            "op2_d8_entropy": op2d8["entropy"], "op4_d4_entropy": op4d4["entropy"],
            "iso_entropy_flat_gap": op2d8["flat_gonogo"] - op4d4["flat_gonogo"],
        }

    # ---- focus = highest-entropy discriminating regime (oracle ok + measurable headroom) ----
    cardinality_ok = completed_units >= EXPECTED_N_UNITS
    discriminating = {rk: v for rk, v in per_regime.items()
                      if v["oracle_rail_ok"] and v["headroom_ok"] and v["n_seeds"] > 0}

    focus_rk = None
    if discriminating:
        focus_rk = max(discriminating.keys(),
                       key=lambda rk: (per_regime[rk]["entropy"], per_regime[rk]["n_ops"],
                                       per_regime[rk]["dd"]))
    fv = per_regime[focus_rk] if focus_rk is not None else None

    # hier_extends_depth: at the focus (deep, high-branch), does hier recover a closure at least
    # as good as the FLAT gate's own low-depth (d4) closure at the same n_ops (native envelope)?
    hier_extends_depth = None
    if fv is not None:
        d4_rk = regime_key(fv["n_ops"], fv["V"], 4)
        if d4_rk in per_regime and per_regime[d4_rk]["n_seeds"] > 0:
            flat_d4_closure = per_regime[d4_rk]["flat_closure_vs_add"]
            hier_extends_depth = bool(fv["hier_closure"] >= max(0.0, flat_d4_closure) * 0.8)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif fv is None:
        verdict = "INCONCLUSIVE_NO_DISCRIMINATING_REGIME"
    elif fv["hp_ok"]:
        verdict = "HARD_PASS"
    elif fv["hier_lift"] <= HF_HIER_LIFT_CEIL or fv["shuf_gap"] <= HF_SHUF_GAP_CEIL:
        verdict = "HARD_FAIL_HIERARCHY_NOT_THE_LEVER"
    else:
        # helps but sub-threshold: classify the miss
        if fv["hier_closure"] < HP_CLOSURE_FLOOR:
            verdict = "MIDDLE_BAND_HELPS_BELOW_25"
        elif fv["shuf_gap"] <= HP_SHUF_GAP_MIN:
            verdict = "MIDDLE_BAND_SHUF_GAP_TOO_SMALL"
        elif fv["reach_tcos_corr_test"] >= HP_REACH_TARGETCOS_CORR_MAX:
            verdict = "MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE"
        elif RUN_MODE == "full" and fv["hier_cv"] >= HP_CV_MAX:
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        elif fv["sign_test_p"] >= HP_SIGN_TEST_P:
            verdict = "MIDDLE_BAND_SIGN_TEST_NS"
        else:
            verdict = "MIDDLE_BAND_HELPS_SUBTHRESHOLD"

    # per-regime compact map for verdict_msg
    grid_str = " ".join(
        "%s(e%.1f:F%.2f/H%.2f/dH%.2f)" % (rk, per_regime[rk]["entropy"],
                                          per_regime[rk]["flat_gonogo"],
                                          per_regime[rk]["hier_options"],
                                          per_regime[rk]["hier_lift"])
        for rk in REGIME_KEYS if rk in per_regime and per_regime[rk]["n_seeds"] > 0)

    if fv is not None:
        head = ("%s | FOCUS=%s(ent=%.1f) FLAT=%.3f HIER=%.3f SHUF=%.3f ORACLE=%.3f | "
                "hier_closure=%.3f hier_lift=%.3f shuf_gap=%.3f | reach_tcos_corr=%.3f "
                "sign_p=%.4g reach_rank=%.3f(min=%.3f) cv=%.3f oracle_rail=%s headroom=%.3f "
                "af=%s hier_extends_depth=%s | ENTROPY spr(lift,ent)=%.3f spr(flat,ent)=%.3f "
                "spr(flat,depth)=%.3f entropy_beats_depth=%s | GRID [%s] n_seeds=%d") % (
            verdict, focus_rk, fv["entropy"], fv["flat_gonogo"], fv["hier_options"],
            fv["hier_shuffled"], fv["oracle"], fv["hier_closure"], fv["hier_lift"],
            fv["shuf_gap"], fv["reach_tcos_corr_test"], fv["sign_test_p"], fv["reach_rank_test"],
            fv["reach_rank_min"], fv["hier_cv"], fv["oracle_rail_ok"], fv["headroom_flat"],
            fv["af_collision"], hier_extends_depth, spearman_hier_lift_vs_entropy,
            spearman_flat_vs_entropy, spearman_flat_vs_depth, entropy_beats_depth,
            grid_str, len(keys))
    else:
        head = "%s | no discriminating regime | GRID [%s] n_seeds=%d" % (verdict, grid_str, len(keys))

    verdict_msg = head

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_regime": per_regime,
        "focus_regime": focus_rk,
        "focus_hier_closure": (fv["hier_closure"] if fv else None),
        "focus_hier_lift": (fv["hier_lift"] if fv else None),
        "focus_shuf_gap": (fv["shuf_gap"] if fv else None),
        "focus_flat_gonogo": (fv["flat_gonogo"] if fv else None),
        "focus_hier_options": (fv["hier_options"] if fv else None),
        "clears_25pct_headroom": bool(fv["hier_closure"] >= HP_CLOSURE_FLOOR) if fv else False,
        "hier_extends_depth": hier_extends_depth,
        "spearman_hier_lift_vs_entropy": spearman_hier_lift_vs_entropy,
        "spearman_flat_vs_entropy": spearman_flat_vs_entropy,
        "spearman_flat_vs_depth": spearman_flat_vs_depth,
        "entropy_beats_depth": entropy_beats_depth,
        "iso_entropy_crossover": crossover,
        "discriminating_regime_keys": list(discriminating.keys()),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok),
        "cv_gate_enforced": bool(RUN_MODE == "full"),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gamma=%.2f seg_len=%d" % (DEVICE, GAMMA, SEG_LEN), flush=True)
    # ST1: cfrpe SR-TD delta-rule shrinks the TD prediction error over steps
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    E = make_bipolar_E(12, 128, gen)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5, gamma=0.8, gen=gen)
    assert diag["err_last"] is not None and diag["err_first"] is not None
    assert diag["err_last"] < diag["err_first"], (
        "ST1 cfrpe TD failed to shrink error %s->%s" % (diag["err_first"], diag["err_last"]))
    assert float(M.norm()) > 1e-4, "ST1 M is ~zero"
    print("[selftest] ST1 cfrpe TD shrinks RPE: %.4f -> %.4f OK"
          % (diag["err_first"], diag["err_last"]), flush=True)

    # ST2: adaptive per-sample LR ordering (high-error -> higher clamped LR)
    err = torch.tensor([[5.0], [0.1]], device=DEVICE) * torch.ones(2, 16, device=DEVICE)
    e_norm = err.norm(dim=1) / math.sqrt(16.0)
    med = float(torch.median(e_norm)); med = med if med > 1e-8 else 1e-8
    ratio_c = torch.clamp(e_norm / med, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
    assert float(ratio_c[0]) > float(ratio_c[1]), "ST2 adaptive LR ordering wrong"
    print("[selftest] ST2 adaptive LR ordering OK (hi=%.3f lo=%.3f)"
          % (float(ratio_c[0]), float(ratio_c[1])), flush=True)

    # ST3: Go/NoGo competition selects argmax
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]], device=DEVICE)
    assert int(scores.argmax(dim=1)[0]) == 1, "ST3 argmax competition wrong"
    print("[selftest] ST3 Go/NoGo argmax competition OK", flush=True)

    # ST4 (MECHANISM-FIRES): trained reach ranks ON-PATH node above OFF-PATH for the goal.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(3)
    Vt, Nt = 8, 512
    Et = make_bipolar_E(Vt, Nt, gen4)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)
    toy_trans = np.concatenate([np.tile(chainA, (30, 1)), np.tile(chainB, (30, 1))], axis=0)
    Mt, _ = train_sr_transport(Et, toy_trans, Nt, steps=600, batch=16, base_lr=0.5, gamma=0.8, gen=gen4)
    goal = Et[3:4]
    reach_on = float(reach_value(Et[1:2], goal, Mt)[0])
    reach_off = float(reach_value(Et[4:5], goal, Mt)[0])
    assert reach_on > reach_off, (
        "ST4 MECHANISM-FIRES FAIL: reach on-path=%.4f !> off-path=%.4f" % (reach_on, reach_off))
    print("[selftest] ST4 mechanism-fires: reach on-path=%.4f > off-path=%.4f OK"
          % (reach_on, reach_off), flush=True)

    # ST5 (ANTI-TAUTOLOGY): identity-reach control is UNINFORMATIVE where trained M is.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    trained_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert trained_sep > control_sep + 0.05, (
        "ST5 ANTI-TAUTOLOGY FAIL: trained-sep=%.4f not clearly > control-sep=%.4f"
        % (trained_sep, control_sep))
    print("[selftest] ST5 anti-tautology: trained-sep=%.4f >> control-sep=%.4f OK"
          % (trained_sep, control_sep), flush=True)

    # ST6 (WAYPOINT BUILD): waypoint index at hop h == boundary state; shuffled differs.
    traj = torch.tensor([[0, 1, 2, 3, 4, 5, 6],
                         [10, 11, 12, 13, 14, 15, 16]], dtype=torch.long, device=DEVICE)
    wp = build_waypoint_idx(traj, seg_len=2, depth=6, shuffle=False)
    # hop 0,1 -> boundary 2 (state idx 2); hop 2,3 -> boundary 4; hop 4,5 -> boundary 6
    exp0 = torch.tensor([2, 2, 4, 4, 6, 6], dtype=torch.long, device=DEVICE)
    assert bool((wp[0] == exp0).all()), "ST6 waypoint schedule wrong: %s" % wp[0].tolist()
    wp_s = build_waypoint_idx(traj, seg_len=2, depth=6, shuffle=True)
    assert not bool((wp_s[0] == wp[0]).all()), "ST6 shuffled waypoints did not differ"
    assert bool((wp_s[0] == torch.tensor([12, 12, 14, 14, 16, 16], device=DEVICE)).all()), \
        "ST6 shuffle roll wrong: %s" % wp_s[0].tolist()
    print("[selftest] ST6 waypoint build + shuffle roll OK", flush=True)

    # ST7 (HIER MECHANISM-FIRES): correct-waypoint hier arm beats wrong-waypoint (shuffled) arm
    # on a deterministic 2-op graph. This is the load-bearing hierarchical discriminator.
    gen7 = torch.Generator(device=DEVICE); gen7.manual_seed(9)
    Vh, Nh = 12, 1024
    Eh = make_bipolar_E(Vh, Nh, gen7)
    # op0 path: 0->1->2->3->4 ; op1 path: 5->6->7->8->9 (disjoint linear chains)
    op0 = [(0, 1), (1, 2), (2, 3), (3, 4)]
    op1 = [(5, 6), (6, 7), (7, 8), (8, 9)]
    Wh = [hebbian_W(op0, Eh, Nh), hebbian_W(op1, Eh, Nh)]
    tr0 = np.tile(np.array(op0, dtype=np.int64), (40, 1))
    tr1 = np.tile(np.array(op1, dtype=np.int64), (40, 1))
    Mh, _ = train_sr_transport(Eh, np.concatenate([tr0, tr1], axis=0), Nh, steps=1500,
                               batch=16, base_lr=0.5, gamma=GAMMA, gen=gen7)
    # two 4-hop chains: A uses op0 all the way (0->4); B uses op1 all the way (5->9)
    chA = (0, [0, 0, 0, 0], 4)
    chB = (5, [1, 1, 1, 1], 9)
    chains = [chA, chB]
    hier_c, _ = run_hier_arm("hier", chains, Wh, Eh, Mh, 4, SEG_LEN, alpha=0.2, w_reach=2.0)
    shuf_c, _ = run_hier_arm("hier_shuffled", chains, Wh, Eh, Mh, 4, SEG_LEN, alpha=0.2, w_reach=2.0)
    assert hier_c.mean() >= shuf_c.mean(), (
        "ST7 HIER FAIL: correct-waypoint acc=%.3f !>= shuffled acc=%.3f"
        % (hier_c.mean(), shuf_c.mean()))
    assert hier_c.mean() >= 0.5, "ST7 HIER hier arm too low on toy (%.3f)" % hier_c.mean()
    print("[selftest] ST7 hier mechanism-fires: correct-wp=%.3f >= shuffled-wp=%.3f OK"
          % (hier_c.mean(), shuf_c.mean()), flush=True)

    # ST8 (CLOSURE FORMULAS): flat-referenced hier closure + additive-referenced flat closure
    hier_, flat_, orc_, add_ = 0.40, 0.10, 0.92, 0.05
    hc = (hier_ - flat_) / (orc_ - flat_)
    fc = (flat_ - add_) / (orc_ - add_)
    assert abs(hc - 0.36585) < 1e-3, "ST8 hier closure off: %.5f" % hc
    assert abs(fc - 0.05747) < 1e-3, "ST8 flat closure off: %.5f" % fc
    print("[selftest] ST8 closure formulas OK (hier_closure=%.3f flat_closure=%.3f)" % (hc, fc), flush=True)

    # ST9 (SPEARMAN + ENTROPY): monotone rank corr = 1.0; entropy = log2(n_ops)*depth
    assert abs(_spearman([1.0, 2.0, 3.0, 4.0], [10.0, 20.0, 30.0, 40.0]) - 1.0) < 1e-9, "ST9 spearman mono"
    assert abs(_spearman([1.0, 2.0, 3.0, 4.0], [40.0, 30.0, 20.0, 10.0]) + 1.0) < 1e-9, "ST9 spearman anti"
    assert abs(decision_entropy(4, 6) - 12.0) < 1e-9, "ST9 entropy op4_d6 != 12"
    assert abs(decision_entropy(2, 8) - 8.0) < 1e-9, "ST9 entropy op2_d8 != 8"
    print("[selftest] ST9 spearman + entropy(op4_d6=12, op2_d8=8) OK", flush=True)

    # ST10: binom p symmetric + bounded
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0, "ST10 binom p out of range"
    assert abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST10 not symmetric"
    print("[selftest] ST10 binom two-sided p(8/10)=%.4f OK" % p, flush=True)

    # ST11: full pipeline single-seed structural (all 7 arms + entropy field present)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_branching")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST11 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST11 missing arm %s" % arm
    assert "entropy" in r["regime_results"][rk0], "ST11 missing entropy"
    orc = r["regime_results"][rk0]["arms"]["oracle"]
    assert orc >= 0.5, "ST11 oracle too low (%.3f) on toy self-test" % orc
    print("[selftest] ST11 pipeline OK regimes=%s arms=%d oracle=%.3f"
          % (REGIME_KEYS, len(ARMS), orc), flush=True)

    # ST12 (VERDICT WIRING): synthetic per_seed -> HARD_PASS (hier closes>=25% + shuf_gap large at
    # focus) and HARD_FAIL (hier ~= flat) and INCONCLUSIVE (no oracle-rail regime).
    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    def _mk_regime(n_ops, V, dd, add, orc, ctrl, v1, flat, hier, shuf, rr, wr=2.0):
        n_hier_only = 45 if hier > flat + 0.1 else 1
        n_flat_only = 2
        n_h_over_s = 40 if hier > shuf + 0.1 else 2
        arms = {"v1_no_goal": v1, "additive_baseline": add, "flat_control_identity": ctrl,
                "oracle": orc, "flat_gonogo": flat, "hier_options": hier, "hier_shuffled": shuf}
        oth = {"v1_no_goal": "a", "additive_baseline": "b", "flat_control_identity": "c",
               "oracle": "oracle_true_seq", "flat_gonogo": "f", "hier_options": "h",
               "hier_shuffled": "s"}
        return {"n_ops": n_ops, "V": V, "dd": dd, "entropy": decision_entropy(n_ops, dd),
                "arms": arms, "op_trace_hashes": oth, "best_alpha": 0.2,
                "best_w_reach_flat": 1.0, "best_w_reach_ctrl": 1.0, "best_w_reach_hier": wr,
                "best_w_reach_shuf": wr, "additive_train_acc": add, "flat_train_acc": flat,
                "hier_train_acc": hier, "reach_rank_chance": 1.0 / n_ops,
                "reach_rank_test": rr, "reach_rank_train": rr, "reach_tcos_corr_test": -0.05,
                "paired": {"n_hier_only": n_hier_only, "n_flat_only": n_flat_only,
                           "n_both": 10, "n_neither": 10, "n_hier_over_shuf": n_h_over_s,
                           "n_shuf_over_hier": 2, "n_test": 60}}

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    reg_lo = regime_key(4, 1200, 4)   # low entropy (8)
    reg_hi = regime_key(4, 1200, 6)   # high entropy (12) -> focus
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4}, {"n_ops": 4, "V": 1200, "dd": 6}]
    REGIME_KEYS = [reg_lo, reg_hi]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    try:
        # HARD_PASS: at focus (op4_d6) hier=0.40 flat=0.10 oracle=0.92 -> closure=0.366>=0.25,
        #   shuf=0.12 -> shuf_gap=0.28>0.10, rr=0.75>0.30.
        ps = {}
        for s in ["7", "17", "23"]:
            ps[s] = {"regime_results": {
                reg_lo: _mk_regime(4, 1200, 4, add=0.20, orc=0.95, ctrl=0.24, v1=0.05,
                                   flat=0.26, hier=0.30, shuf=0.24, rr=0.70),
                reg_hi: _mk_regime(4, 1200, 6, add=0.01, orc=0.92, ctrl=0.11, v1=0.0,
                                   flat=0.10, hier=0.40, shuf=0.12, rr=0.75),
            }}
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "ST12 expected HARD_PASS got %s" % out["verdict"]
        assert out["focus_regime"] == reg_hi, "ST12 focus should be high-entropy regime"
        # HARD_FAIL: hier ~= flat at focus
        for s in ps:
            ps[s]["regime_results"][reg_hi] = _mk_regime(4, 1200, 6, add=0.01, orc=0.92, ctrl=0.11,
                                                         v1=0.0, flat=0.10, hier=0.11, shuf=0.10, rr=0.75)
        out2 = aggregate_and_verdict(ps)
        assert out2["verdict"] == "HARD_FAIL_HIERARCHY_NOT_THE_LEVER", \
            "ST12 expected HARD_FAIL got %s" % out2["verdict"]
        # INCONCLUSIVE: no oracle-rail-ok regime
        for s in ps:
            for rk in (reg_lo, reg_hi):
                ps[s]["regime_results"][rk]["arms"]["oracle"] = 0.50
        out3 = aggregate_and_verdict(ps)
        assert out3["verdict"] == "INCONCLUSIVE_NO_DISCRIMINATING_REGIME", \
            "ST12 expected INCONCLUSIVE got %s" % out3["verdict"]
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST12 verdict wiring OK (HARD_PASS focus-hi; HARD_FAIL hier~flat; "
          "INCONCLUSIVE no-oracle-rail)", flush=True)


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
                "verdict_msg": "SELFTEST_OK: ST1-ST12 (cfrpe-TD shrink, adaptive LR, Go/NoGo "
                               "argmax, mechanism-fires reach, anti-tautology, waypoint build+shuffle, "
                               "hier>=shuffled mechanism, closure formulas, spearman+entropy, binom, "
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
