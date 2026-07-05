"""pfc_gate_cfrpe_trained_v1 -- RPE-trained Go/NoGo gate vs static additive-bias gate.

STRATEGIC RATIONALE (brain-component-driven-development thrust, 2026-07-05):
  The PFC-BG goal-conditioned gate is a MEASURED-WEAK component. v3 (additive-bias)
  landed HARD_FAIL: static goal-sim bias only helps on the LAST hop (goal-sim is
  ~random on early hops of a multi-hop chain), so it closes only ~7 of the ~64
  points of ORACLE headroom.
  MEASURED@d:/AI/hd-instrument/data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only/metrics.json:
    V1=0.352  ADD(best a=0.2)=0.420 (add_lift=+0.068)  WM=0.396  ORACLE=0.994  headroom=0.642
  Brain claim (PBWM / Frank-O'Reilly 2004/2006; Schultz 1997): the BG Go/NoGo gate
  is not a static rule -- it is TRAINED by a dopaminergic reward-prediction-error
  (RPE) signal that performs TEMPORAL CREDIT ASSIGNMENT (propagates goal-value
  backward through the chain). That is exactly the missing capability: an early-hop
  signal of "does this candidate move me toward the goal".

MECHANISM (substrate-native; composes two already-proven primitives, no new
representational machinery):
  - cfrpe RPE signal = the substrate's error-driven delta-rule outer-product update
    (borrowed EXACTLY from exp_substrate_adaptive_cfrpe_x_k2_compose_v1: adaptive
    per-sample LR clamp error/median in [0.25, 4.0]).
  - We train a SUCCESSOR-FEATURE transport matrix M (Dayan-1993 SR / Stachenfeld-2017
    hippocampal-striatal SR) by TD(0): the TD-error IS the canonical reward-prediction
    error. M is learned so E[x] @ M approximates the discounted successor features of
    x under exploration rollouts. reach(cand; goal) = cos(E[cand]@M, E[goal]) is high
    iff goal is reachable (few discounted hops) from cand -- the early-hop signal.
  - Go/NoGo competition (the actor): each operator i gets a Go-value
      Go_i = w_manifold*manifold_i + w_goal*goal_sim_i + w_reach*reach_i
    and the gate selects argmax_i Go_i (winner-take-all; non-winners = NoGo).
    w_reach is tuned on TRAIN rollouts only (train/test hygiene); w_reach==0 reduces
    GONOGO exactly to the ADDITIVE_BASELINE (so any lift is attributable to the
    RPE-trained reach value, and a null result is a clean w_reach==0 reduction).

ANTI-TAUTOLOGY (VET steer 2026-07-05): v3's HARD_FAIL was partly TAUTOLOGICAL --
its WM and additive arms were the same target-cosine signal, so "combined" was
byte-identical to WM. To be decisive, the RPE-trained reach signal must carry
information INDEPENDENT of raw target-cosine. Structural guarantee: M is trained on
exploration-rollout DYNAMICS (TD target E[nxt]+gamma*E[nxt]@M), never on the goal.
Made FALSIFIABLE by (a) an identity-reach CONTROL arm (M:=identity collapses reach
to target-cosine), (b) a reach-vs-targetcosine correlation guard, (c) ST7 proving the
control is uninformative exactly where the trained M is informative. The number to
beat is the FULL residual headroom 0.642 (oracle 0.994 - v1 0.352); the best
cosine-heuristic (additive) captured only ~11% of it -- large room for a genuinely
different (dynamics) signal.

ARMS (paired -- all share E, W_ops, and the SAME test chains per seed):
  ARM_V1_NO_GOAL              goal-blind manifold reference (rail ~0.35)
  ARM_ADDITIVE_BASELINE       static additive goal-bias, alpha tuned on train (rail lift +0.03..0.10)
  ARM_CFRPE_CONTROL_IDENTITY  gonogo with reach:=target-cosine (M=identity); anti-tautology foil
  ARM_CFRPE_TRAINED_GONOGO    SR/TD-transport Go/NoGo trained by the cfrpe delta-rule (THE TEST)
  ARM_ORACLE                  applies the true op_seq (rail >= 0.90; ceiling ~0.99)

PRIMARY DISCRIMINATOR (paired, decision_depth=6):
  gonogo_lift  = ARM_CFRPE_TRAINED_GONOGO - ARM_ADDITIVE_BASELINE   (does RPE-training help?)
  dynamics_lift= ARM_CFRPE_TRAINED_GONOGO - ARM_CFRPE_CONTROL_IDENTITY (is the win from LEARNED
                 dynamics, not target-cosine in disguise?)
  HARD_PASS : gonogo_lift >= 0.155 (strict floor per META_RULE_L; closes >=~25% of the
              additive->oracle headroom) AND dynamics_lift > 0.05 (real M beats identity-reach)
              AND reach-vs-targetcos corr < 0.85 (reach is NOT target-cosine) AND cv(gonogo)<0.10
              AND paired sign-test p<0.05 AND mechanism-fires (reach_rank_acc_test>0.30)
              AND rails OK AND arms differ
  HARD_FAIL : gonogo_lift <= 0.05 (RPE training adds nothing beyond the static rule)
  MIDDLE_BAND: gonogo_lift in (0.05, 0.155), OR gonogo_lift>=0.155 but dynamics_lift<=0.05
               (a win that is not attributable to learned dynamics is NOT chain-grade)

The discriminator can fire IN BOTH DIRECTIONS by construction:
  - PASS-able: additive=0.42, oracle=0.99 => 0.57 of headroom is reachable (a +0.155
    lift lands at ~0.575, well inside feasibility). discriminator_reachability=True.
  - FAIL-able: if the SR value does not GENERALIZE from exploration rollouts to
    held-out (start,goal) chains, w_reach tunes toward 0 and gonogo ~ additive => lift ~0.
  - NON-TAUTOLOGY-able: if reach is secretly target-cosine, the identity-reach control
    matches it (dynamics_lift ~0) => demoted to MIDDLE_BAND, not a false HARD_PASS.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-chain op-trace hash-test; exempt when w_reach==0)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-lift discriminator has no single closed-form noise floor;
#   reachability declared via additive->oracle headroom feasibility (0.57 >> 0.155)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < additive_acc < 0.95)
# - discriminator survives scale: informational (early-hop reachability), not capacity-limited;
#   smoke holds N/V ratio ~3.4 constant with FULL; gap direction previewed by reach_rank_acc
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L): 0.15 + 0.05*0.10 = 0.155
# - HP_SCOPE: HARD_PASS gates apply ONLY to ARM_CFRPE_TRAINED_GONOGO vs ARM_ADDITIVE_BASELINE;
#   rails apply to V1/ADDITIVE/ORACLE
# - cardinality_ok: EXPECTED_N_UNITS = n_arms * n_seeds * n_depths
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank gate logged)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Compute architecture: (a) batched-GPU. Every heavy op (SR-TD training, operator
application, cleanup, reach) is a batched matmul over torch tensors on
cuda-if-available. Per-hop op-selection is batched ACROSS chains (chains are
independent; only the within-chain hops are sequential). FULL strongly prefers
overnight_queue (GPU); remote CPU is feasible but slow for SR training.
Storage strategy: sharded (each operator is its own W matrix; no bundled item store).
M is a learned value operator, not an item store.

Author: exp_dev 2026-07-05 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md
Cites:
  data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only/metrics.json (v3 rails)
  experiments/exp_pfc_goal_conditioned_gate_v3_wm_additive_only.py (harness heritage)
  experiments/exp_substrate_adaptive_cfrpe_x_k2_compose_v1.py (cfrpe adaptive delta-rule)
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

ANCHOR_NAME = "pfc_gate_cfrpe_trained_v1"

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
HP_GONOGO_LIFT_FLOOR = 0.155        # META_RULE_L strict: 0.15 + 0.05*(0.15-0.05)
HP_DYNAMICS_LIFT_MIN = 0.05         # real M must beat identity-reach control (anti-tautology)
HP_REACH_TARGETCOS_CORR_MAX = 0.85  # reach must NOT be target-cosine in disguise
HP_CV_MAX = 0.10
HP_SIGN_TEST_P = 0.05
HP_REACH_RANK_MIN = 0.30            # mechanism-fires (held-out reach informativeness > chance 0.25)
HF_GONOGO_LIFT_CEIL = 0.05
MB_GONOGO_LIFT_LOW = 0.05           # MB in (0.05, 0.155)
ADDITIVE_RAIL_LO = 0.03            # additive lift band (sanity vs v3 +0.068)
ADDITIVE_RAIL_HI = 0.10
ORACLE_RAIL_MIN = 0.90
BASELINE_IN_BAND_LO = 0.05         # META_RULE_AG additive acc must be measurable
BASELINE_IN_BAND_HI = 0.95
DECISION_DEPTH = 6

ALPHA_SWEEP = [0.1, 0.2, 0.5]       # additive goal-bias alpha, tuned on train
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]  # gonogo/control reach weight, tuned on train
GAMMA = 0.85                        # SR discount
ADAPT_LR_FLOOR = 0.25              # cfrpe adaptive LR clamp (from source cell)
ADAPT_LR_CEIL = 4.0

ARMS = ["v1_no_goal", "additive_baseline", "cfrpe_control_identity",
        "cfrpe_trained_gonogo", "oracle"]

# --------------------------- config (selftest / smoke / full) --------------------
if SELF_TEST_MODE:
    N_DIM = 256
    V_ENTITIES = 40
    N_OPS = 4
    SEEDS = [7]
    HOP_DEPTHS = [4]
    N_TRAIN_TRIPLES_PER_OP = 20
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    N_ROLLOUT_TRANSITIONS = 800
elif RUN_MODE == "smoke":
    # must fit under ~180s on laptop CPU; 3 seeds (multi-seed gate). Smoke is a
    # SMALLER-SCALE proxy: shallower decision depth (4) + easier cleanup (N/V high)
    # so the ORACLE rail holds and the additive baseline lands in the measurable
    # band while the discriminator (gonogo vs additive/control) still fires.
    N_DIM = 2048
    V_ENTITIES = 200
    N_OPS = 4
    SEEDS = [7, 17, 23]
    HOP_DEPTHS = [3, 4]
    N_TRAIN_TRIPLES_PER_OP = 42        # density 42/200=0.21 ~= v3's 500/2400=0.208
    N_TRAIN_CHAINS = 40
    N_TEST_CHAINS = 32
    SR_STEPS = 400
    SR_BATCH = 64
    SR_LR = 0.5
    N_ROLLOUT_TRANSITIONS = 6000
else:  # full
    N_DIM = 8192
    V_ENTITIES = 2400            # N/V = 3.41 (matches v3 8192/2400)
    N_OPS = 4
    SEEDS = [7, 17, 23, 31, 41]
    HOP_DEPTHS = [6, 8]
    N_TRAIN_TRIPLES_PER_OP = 500
    N_TRAIN_CHAINS = 240
    N_TEST_CHAINS = 120
    SR_STEPS = 3000
    SR_BATCH = 128
    SR_LR = 0.5
    N_ROLLOUT_TRANSITIONS = 40000

EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(HOP_DEPTHS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,N_OPS=%d,seeds=%s,depths=%s,dec_depth=%d,"
    "n_train_triples=%d,n_train_chains=%d,n_test_chains=%d,sr_steps=%d,sr_batch=%d,"
    "gamma=%.2f,alphas=%s,w_reach=%s,mode=%s,device=%s,expected_n=%d,"
    "HP_lift>=%.3f,cv<%.2f,sign_p<%.2f,reach_rank>%.2f"
) % (
    ANCHOR_NAME, N_DIM, V_ENTITIES, N_OPS, SEEDS, HOP_DEPTHS, DECISION_DEPTH,
    N_TRAIN_TRIPLES_PER_OP, N_TRAIN_CHAINS, N_TEST_CHAINS, SR_STEPS, SR_BATCH,
    GAMMA, ALPHA_SWEEP, W_REACH_SWEEP, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_GONOGO_LIFT_FLOOR, HP_CV_MAX, HP_SIGN_TEST_P, HP_REACH_RANK_MIN,
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
# primitives (torch, batched, device-agnostic)
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
    sims = vn @ E.transpose(0, 1)          # [B, V]
    manifold, idx = sims.max(dim=1)
    return idx, E[idx], manifold


# ============================================================================
# KB + chains (exact-length paths; train and test disjoint chain sets)
# ============================================================================
def make_kb_and_chains(n_ops: int, V: int, n_train_triples: int,
                       n_train_chains: int, n_test_chains: int,
                       depths: List[int], g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]]]:
    """Returns (per_op_triples, train_chains_by_depth, test_chains_by_depth).

    Each chain is (start, op_seq[len==depth], target) with a guaranteed exact-length
    path (missing edges are created into the KB). Train and test chains are distinct
    draws over the SAME operator graph (model-based / held-out-query hygiene).
    """
    per_op: List[List[Tuple[int, int]]] = [[] for _ in range(n_ops)]
    # seed background triples per op
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
# cfrpe-trained SR transport M (TD(0); TD-error == reward-prediction-error)
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features).

    Update = the cfrpe delta-rule with adaptive per-sample LR (error/median clamp).
    Returns (M, diag). diag includes err_first/err_last (must shrink) and clamp counts.
    """
    M = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    K = transitions.shape[0]
    diag = {"n_transitions": int(K), "n_clamped_steps": 0,
            "err_first": None, "err_last": None, "final_M_norm": 0.0}
    if K < 2:
        return M, diag
    cur_t = torch.tensor(transitions[:, 0], dtype=torch.long, device=DEVICE)
    nxt_t = torch.tensor(transitions[:, 1], dtype=torch.long, device=DEVICE)
    sqrt_n = math.sqrt(float(n))
    for step in range(steps):
        st = torch.randint(0, K, (batch,), generator=gen, device=DEVICE)
        Ecur = E[cur_t[st]]                       # [b, n]
        Enxt = E[nxt_t[st]]                        # [b, n]
        pred = Ecur @ M                            # [b, n]  (E[cur]@M)
        with torch.no_grad():
            boot = Enxt + gamma * (Enxt @ M)       # TD target (bootstrap)
        error = boot - pred                        # TD-error == RPE   [b, n]
        e_norm = error.norm(dim=1) / sqrt_n        # per-sample RMS error
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_c = torch.clamp(ratio, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            diag["n_clamped_steps"] += 1
        lr_per = base_lr * ratio_c                 # [b]
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
    """Anti-tautology control: reach with M:=identity == raw target-cosine cos(E[cand],E[goal]).
    Carries NO dynamics info; used to prove the trained-M win is not target-cosine in disguise."""
    return (_norm_rows(cand_E) * _norm_rows(goal_E)).sum(dim=1)


# ============================================================================
# arms (batched across chains; hops are sequential within a chain)
# ============================================================================
def _chain_tensors(chains: List[Tuple[int, List[int], int]]
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)  # [n_chains, depth]
    return starts, targets, op_seqs


def run_selection_arm(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                      M: torch.Tensor, depth: int,
                      alpha: float, w_reach: float
                      ) -> Tuple[np.ndarray, np.ndarray]:
    """Batched op-selection arm. mode in {v1, additive, gonogo}.

    Returns (correct_bool[n_chains], op_trace[n_chains, depth]).
    additive     : sc = alpha*goal_sim + (1-alpha)*manifold
    gonogo       : sc = (1-alpha)*manifold + alpha*goal_sim + w_reach*reach   (learned-M dynamics)
    gonogo_control: sc = (1-alpha)*manifold + alpha*goal_sim + w_reach*targetcos (identity reach)
    v1           : sc = manifold
    """
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()                      # [n, n_dim]
    goal_E = E[targets]                            # [n, n_dim]
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    for hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        cand_E_by_op: List[torch.Tensor] = []
        for op in range(n_ops):
            out = state @ W_ops[op]                # [n, n_dim]
            idx, cleaned, manifold = cleanup_batched(out, E)
            cand_idx[:, op] = idx
            cand_E_by_op.append(cleaned)
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
        chosen = scores.argmax(dim=1)              # [n]  Go/NoGo winner-take-all
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


def reach_rank_acc(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                   M: torch.Tensor, depth: int) -> float:
    """Mechanism-fires probe: along the TRUE (oracle) trajectory, does argmax_op reach
    == the true op? Chance = 1/n_ops. Measures reach-value informativeness directly."""
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
        cand_E_all: List[torch.Tensor] = []
        cand_idx_all = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]
            idx, cleaned, _ = cleanup_batched(out, E)
            cand_E_all.append(cleaned)
            cand_idx_all[:, op] = idx
            reach_scores[:, op] = reach_value(cleaned, goal_E, M)
        pred_op = reach_scores.argmax(dim=1)
        true_op = op_seq_t[:, hop]
        hits += int((pred_op == true_op).sum().item())
        total += n_chains
        # advance along TRUE trajectory
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx_all[row, true_op]
        state = E[new_idx]
    return float(hits) / float(max(1, total))


def reach_vs_targetcos_corr(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                            M: torch.Tensor, depth: int) -> float:
    """Anti-tautology guard: Pearson corr between learned-M reach and raw target-cosine
    across all candidate ops along the true trajectory. corr near 1.0 => reach IS
    target-cosine in disguise (v3 tautology). Low corr => reach carries dynamics info."""
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
        p_two = 2.0 * tail
        return float(min(1.0, p_two))
    # normal approx with continuity correction
    mu = n * p
    sd = math.sqrt(n * p * (1 - p))
    z = (abs(k - mu) - 0.5) / (sd + 1e-12)
    # 2*(1 - Phi(z))
    return float(min(1.0, 2.0 * 0.5 * math.erfc(z / math.sqrt(2.0))))


# ============================================================================
# per-seed runner
# ============================================================================
def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    tgen = torch.Generator(device=DEVICE)
    tgen.manual_seed(int(seed))

    E = make_bipolar_E(V_ENTITIES, N_DIM, tgen)
    per_op, train_by_d, test_by_d = make_kb_and_chains(
        N_OPS, V_ENTITIES, N_TRAIN_TRIPLES_PER_OP, N_TRAIN_CHAINS, N_TEST_CHAINS,
        HOP_DEPTHS, g)
    W_ops = [hebbian_W(per_op[i], E, N_DIM) for i in range(N_OPS)]
    adj = build_adjacency(per_op, N_OPS)

    # ---- train SR transport M via cfrpe delta-rule (exploration rollouts only) ----
    max_len = max(HOP_DEPTHS) + 2
    transitions = collect_rollout_transitions(
        adj, N_OPS, V_ENTITIES, N_ROLLOUT_TRANSITIONS, max_len, g)
    sr_gen = torch.Generator(device=DEVICE)
    sr_gen.manual_seed(int(seed) * 7919 + 13)
    M, sr_diag = train_sr_transport(
        E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
    print("[seed=%d] SR trained: err %s->%s M_norm=%.3f n_trans=%d clamp=%d"
          % (seed, sr_diag["err_first"], sr_diag["err_last"], sr_diag["final_M_norm"],
             sr_diag["n_transitions"], sr_diag["n_clamped_steps"]), flush=True)

    # ---- tune alpha (additive) + w_reach (gonogo) on TRAIN chains (decision depth) --
    dd = DECISION_DEPTH if DECISION_DEPTH in HOP_DEPTHS else max(HOP_DEPTHS)
    train_dd = train_by_d[dd]
    v1_train = run_selection_arm("v1", train_dd, W_ops, E, M, dd, 0.0, 0.0)[0].mean()
    best_alpha, best_add_train = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_arm("additive", train_dd, W_ops, E, M, dd, a, 0.0)[0].mean()
        if acc > best_add_train:
            best_add_train, best_alpha = acc, a
    best_wr, best_go_train = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo", train_dd, W_ops, E, M, dd, best_alpha, wr)[0].mean()
        if acc > best_go_train:
            best_go_train, best_wr = acc, wr
    # tune identity-reach CONTROL independently on train (steelman the foil)
    best_wr_ctrl, best_ctrl_train = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo_control", train_dd, W_ops, E, M, dd,
                                best_alpha, wr)[0].mean()
        if acc > best_ctrl_train:
            best_ctrl_train, best_wr_ctrl = acc, wr

    # ---- mechanism-fires probe + anti-tautology corr (train + held-out) ----
    reach_rank_train = reach_rank_acc(train_dd, W_ops, E, M, dd)
    reach_rank_test = reach_rank_acc(test_by_d[dd], W_ops, E, M, dd)
    reach_tcos_corr_test = reach_vs_targetcos_corr(test_by_d[dd], W_ops, E, M, dd)

    # ---- evaluate all arms on TEST chains, per depth (paired) ----
    per_depth: Dict[str, Dict[str, Any]] = {}
    op_trace_hashes: Dict[str, Dict[str, str]] = {arm: {} for arm in ARMS}
    paired_dd = {}
    for depth in HOP_DEPTHS:
        d = str(depth)
        test_c = test_by_d[depth]
        v1_c, v1_tr = run_selection_arm("v1", test_c, W_ops, E, M, depth, 0.0, 0.0)
        add_c, add_tr = run_selection_arm("additive", test_c, W_ops, E, M, depth, best_alpha, 0.0)
        ctrl_c, ctrl_tr = run_selection_arm("gonogo_control", test_c, W_ops, E, M, depth,
                                            best_alpha, best_wr_ctrl)
        go_c, go_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, depth, best_alpha, best_wr)
        orc_c = run_oracle_arm(test_c, W_ops, E, depth)
        per_depth[d] = {
            "v1_no_goal": float(v1_c.mean()),
            "additive_baseline": float(add_c.mean()),
            "cfrpe_control_identity": float(ctrl_c.mean()),
            "cfrpe_trained_gonogo": float(go_c.mean()),
            "oracle": float(orc_c.mean()),
        }
        op_trace_hashes["v1_no_goal"][d] = hashlib.sha256(v1_tr.tobytes()).hexdigest()[:16]
        op_trace_hashes["additive_baseline"][d] = hashlib.sha256(add_tr.tobytes()).hexdigest()[:16]
        op_trace_hashes["cfrpe_control_identity"][d] = hashlib.sha256(ctrl_tr.tobytes()).hexdigest()[:16]
        op_trace_hashes["cfrpe_trained_gonogo"][d] = hashlib.sha256(go_tr.tobytes()).hexdigest()[:16]
        op_trace_hashes["oracle"][d] = "oracle_true_seq"
        if depth == dd:
            # paired discordance: gonogo vs additive, and gonogo vs identity-control
            paired_dd = {
                "n_gonogo_only": int(((go_c) & (~add_c)).sum()),
                "n_additive_only": int(((add_c) & (~go_c)).sum()),
                "n_both": int((go_c & add_c).sum()),
                "n_neither": int(((~go_c) & (~add_c)).sum()),
                "n_test": int(len(go_c)),
                "n_gonogo_over_ctrl": int(((go_c) & (~ctrl_c)).sum()),
                "n_ctrl_over_gonogo": int(((ctrl_c) & (~go_c)).sum()),
            }

    return {
        "seed": int(seed),
        "N": N_DIM, "V": V_ENTITIES, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "per_depth": per_depth,
        "best_alpha": float(best_alpha), "best_w_reach": float(best_wr),
        "best_w_reach_ctrl": float(best_wr_ctrl),
        "v1_train_acc": float(v1_train),
        "additive_train_acc": float(best_add_train),
        "gonogo_train_acc": float(best_go_train),
        "control_train_acc": float(best_ctrl_train),
        "reach_rank_train": float(reach_rank_train),
        "reach_rank_test": float(reach_rank_test),
        "reach_tcos_corr_test": float(reach_tcos_corr_test),
        "sr_diag": sr_diag,
        "op_trace_hashes": op_trace_hashes,
        "paired_dd": paired_dd,
        "decision_depth": int(dd),
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)
    dd = per_seed[keys[0]]["decision_depth"]
    dds = str(dd)

    def _col(arm, d):
        return [float(per_seed[k]["per_depth"][d][arm]) for k in keys
                if d in per_seed[k]["per_depth"]]

    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        per_arm_summary[arm] = {}
        for depth in HOP_DEPTHS:
            d = str(depth)
            vals = _col(arm, d)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                per_arm_summary[arm][d] = {
                    "mean": m, "std": sd,
                    "cv": float(sd / m) if m > 1e-6 else 0.0, "n": len(vals),
                    "per_seed": {keys[i]: vals[i] for i in range(len(vals))}}
            else:
                per_arm_summary[arm][d] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}

    v1 = per_arm_summary["v1_no_goal"][dds]["mean"]
    add = per_arm_summary["additive_baseline"][dds]["mean"]
    ctrl = per_arm_summary["cfrpe_control_identity"][dds]["mean"]
    go = per_arm_summary["cfrpe_trained_gonogo"][dds]["mean"]
    orc = per_arm_summary["oracle"][dds]["mean"]
    go_cv = per_arm_summary["cfrpe_trained_gonogo"][dds]["cv"]

    gonogo_lift = go - add
    dynamics_lift = go - ctrl          # win attributable to LEARNED dynamics (anti-tautology)
    additive_lift = add - v1
    headroom = orc - v1
    reach_tcos_corr = float(np.mean([per_seed[k]["reach_tcos_corr_test"] for k in keys]))
    corr_ok = reach_tcos_corr < HP_REACH_TARGETCOS_CORR_MAX
    dynamics_attributable = dynamics_lift > HP_DYNAMICS_LIFT_MIN

    # paired sign-test pooled across seeds (decision depth)
    n_go_only = sum(int(per_seed[k]["paired_dd"].get("n_gonogo_only", 0)) for k in keys)
    n_add_only = sum(int(per_seed[k]["paired_dd"].get("n_additive_only", 0)) for k in keys)
    n_disc = n_go_only + n_add_only
    sign_p = binom_two_sided_p(n_go_only, n_disc, 0.5) if n_disc > 0 else 1.0

    reach_rank_test = float(np.mean([per_seed[k]["reach_rank_test"] for k in keys]))
    reach_rank_train = float(np.mean([per_seed[k]["reach_rank_train"] for k in keys]))
    best_wr_vals = [per_seed[k]["best_w_reach"] for k in keys]
    all_wr_zero = all(abs(w) < 1e-9 for w in best_wr_vals)

    # arms-differ (META_RULE_AF): gonogo vs additive op-trace hashes must differ
    # at decision depth UNLESS w_reach==0 (legitimate reduction -> exempt).
    af_collision = False
    for k in keys:
        h = per_seed[k]["op_trace_hashes"]
        if per_seed[k]["best_w_reach"] > 1e-9:
            if h["cfrpe_trained_gonogo"].get(dds) == h["additive_baseline"].get(dds):
                af_collision = True
    arms_differ_ok = (not af_collision)
    arms_differ_exempted = all_wr_zero

    rails_ok = (orc >= ORACLE_RAIL_MIN
                and BASELINE_IN_BAND_LO < add < BASELINE_IN_BAND_HI
                and additive_lift > 0.0)
    additive_rail_in_band = (ADDITIVE_RAIL_LO <= additive_lift <= ADDITIVE_RAIL_HI)
    mechanism_fires = reach_rank_test > HP_REACH_RANK_MIN

    completed = sum(1 for arm in ARMS for depth in HOP_DEPTHS
                    if per_arm_summary[arm][str(depth)]["n"] > 0) * len(keys)
    cardinality_ok = completed >= EXPECTED_N_UNITS

    # verdict priority
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif orc < ORACLE_RAIL_MIN:
        verdict = "HARD_FAIL_ORACLE_RAIL"
    elif not (BASELINE_IN_BAND_LO < add < BASELINE_IN_BAND_HI) or additive_lift <= 0.0:
        verdict = "HARD_FAIL_ADDITIVE_RAIL"
    elif af_collision:
        verdict = "HARD_FAIL_AF_TRACE_COLLISION"
    elif gonogo_lift <= HF_GONOGO_LIFT_CEIL:
        verdict = "HARD_FAIL_RPE_NO_HELP"
    elif (gonogo_lift >= HP_GONOGO_LIFT_FLOOR and dynamics_attributable and corr_ok
          and go_cv < HP_CV_MAX and sign_p < HP_SIGN_TEST_P
          and mechanism_fires and rails_ok):
        verdict = "HARD_PASS"
    elif gonogo_lift >= HP_GONOGO_LIFT_FLOOR and not (dynamics_attributable and corr_ok):
        # a big lift that is NOT attributable to learned dynamics == tautology risk
        verdict = "MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | dec_depth=%d | V1=%.3f ADD(a=%.2f)=%.3f CTRL=%.3f GONOGO(wr=%s)=%.3f ORACLE=%.3f | "
        "gonogo_lift=%.3f dynamics_lift=%.3f additive_lift=%.3f headroom=%.3f | "
        "reach_tcos_corr=%.3f(corr_ok=%s) cv=%.3f sign_p=%.4f (go_only=%d add_only=%d) "
        "reach_rank_test=%.3f mech_fires=%s rails_ok=%s add_rail_in_band=%s "
        "arms_differ=%s(exempt=%s) n_seeds=%d"
    ) % (verdict, dd, v1,
         float(np.mean([per_seed[k]["best_alpha"] for k in keys])), add, ctrl,
         "/".join("%.1f" % w for w in best_wr_vals), go, orc,
         gonogo_lift, dynamics_lift, additive_lift, headroom,
         reach_tcos_corr, corr_ok, go_cv, sign_p, n_go_only, n_add_only,
         reach_rank_test, mechanism_fires, rails_ok, additive_rail_in_band,
         arms_differ_ok, arms_differ_exempted, len(keys))

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm_summary": per_arm_summary,
        "decision_depth": dd,
        "gonogo_lift": float(gonogo_lift),
        "dynamics_lift": float(dynamics_lift),
        "additive_lift": float(additive_lift),
        "oracle_headroom": float(headroom),
        "reach_tcos_corr_test": float(reach_tcos_corr),
        "corr_ok": bool(corr_ok),
        "dynamics_attributable": bool(dynamics_attributable),
        "gonogo_cv": float(go_cv),
        "sign_test_p": float(sign_p),
        "n_gonogo_only": int(n_go_only),
        "n_additive_only": int(n_add_only),
        "reach_rank_test": reach_rank_test,
        "reach_rank_train": reach_rank_train,
        "best_w_reach_per_seed": {keys[i]: best_wr_vals[i] for i in range(len(keys))},
        "all_w_reach_zero": bool(all_wr_zero),
        "additive_rail_in_band": bool(additive_rail_in_band),
        "mechanism_fires": bool(mechanism_fires),
        "rails_ok": bool(rails_ok),
        "arms_differ_ok": bool(arms_differ_ok),
        "arms_differ_exempted": bool(arms_differ_exempted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": int(completed),
        "cardinality_ok": bool(cardinality_ok),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s" % DEVICE, flush=True)
    # ST1: cfrpe SR-TD delta-rule shrinks the TD prediction error over steps
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)
    E = make_bipolar_E(12, 128, gen)
    trans = np.array([[i, i + 1] for i in range(10)], dtype=np.int64)
    M, diag = train_sr_transport(E, trans, 128, steps=200, batch=8, base_lr=0.5,
                                 gamma=0.8, gen=gen)
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

    # ST3: Go/NoGo competition selects argmax Go-value
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]], device=DEVICE)
    assert int(scores.argmax(dim=1)[0]) == 1, "ST3 argmax competition wrong"
    print("[selftest] ST3 Go/NoGo argmax competition OK", flush=True)

    # ST4 (MECHANISM-FIRES): two LIVE branches from 0. Branch A 0->1->2->3 (goal=3);
    #   branch B 0->4->5->6 (leads away). Both 1 and 4 are non-terminal (trained as
    #   sources). Trained reach ranks ON-PATH node 1 above OFF-PATH node 4 for goal 3.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(3)
    Vt, Nt = 8, 512
    Et = make_bipolar_E(Vt, Nt, gen4)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)   # to goal 3
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)   # away from goal
    toy_trans = np.concatenate([np.tile(chainA, (30, 1)),
                                np.tile(chainB, (30, 1))], axis=0)
    Mt, _ = train_sr_transport(Et, toy_trans, Nt, steps=600, batch=16, base_lr=0.5,
                               gamma=0.8, gen=gen4)
    goal = Et[3:4]
    reach_on = float(reach_value(Et[1:2], goal, Mt)[0])   # on-path: 1 -> ... -> 3
    reach_off = float(reach_value(Et[4:5], goal, Mt)[0])  # off-path: 4 -> ... -> 6
    assert reach_on > reach_off, (
        "ST4 MECHANISM-FIRES FAIL: reach on-path=%.4f !> off-path=%.4f"
        % (reach_on, reach_off))
    print("[selftest] ST4 mechanism-fires: reach on-path=%.4f > off-path=%.4f OK"
          % (reach_on, reach_off), flush=True)

    # ST7 (ANTI-TAUTOLOGY): the identity-reach CONTROL (target-cosine) is UNINFORMATIVE
    #   exactly where trained M is informative. On-path(1) and off-path(4) are both
    #   ~orthogonal to goal(3) in raw cosine, so the control cannot separate them, but
    #   trained M can. This proves reach is NOT target-cosine in disguise.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    trained_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert trained_sep > control_sep + 0.05, (
        "ST7 ANTI-TAUTOLOGY FAIL: trained-sep=%.4f not clearly > control-sep=%.4f"
        % (trained_sep, control_sep))
    print("[selftest] ST7 anti-tautology: trained-sep=%.4f >> control(targetcos)-sep=%.4f OK"
          % (trained_sep, control_sep), flush=True)

    # ST5: full pipeline single-seed structural + arms present + oracle high
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_gate")
    for arm in ARMS:
        assert arm in r["per_depth"][str(HOP_DEPTHS[0])], "ST5 missing arm %s" % arm
    orc = r["per_depth"][str(r["decision_depth"])]["oracle"]
    assert orc >= 0.5, "ST5 oracle too low (%.3f) on toy self-test" % orc
    print("[selftest] ST5 pipeline OK arms=%s oracle=%.3f reach_rank_test=%.3f"
          % (ARMS, orc, r["reach_rank_test"]), flush=True)

    # ST6: binomial p symmetric + bounded
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0, "ST6 binom p out of range"
    assert abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST6 not symmetric"
    print("[selftest] ST6 binom two-sided p(8/10)=%.4f OK" % p, flush=True)
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

    print("[%s] mode=%s device=%s N=%d V=%d ops=%d seeds=%s depths=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, V_ENTITIES, N_OPS, SEEDS,
             HOP_DEPTHS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST7 (cfrpe-TD shrink, adaptive LR, "
                               "Go/NoGo argmax, mechanism-fires reach ranking, pipeline, "
                               "binom, anti-tautology control uninformative)",
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

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
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
                "per_depth": {}, "paired_dd": {}, "op_trace_hashes": {},
                "decision_depth": DECISION_DEPTH, "reach_rank_test": 0.0,
                "reach_rank_train": 0.0, "best_alpha": 0.0, "best_w_reach": 0.0})
            print("[seed=%d] FATAL %s: %s" % (seed, fc, e), file=sys.stderr, flush=True)
            continue
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs (dd acc: v1=%.3f add=%.3f gonogo=%.3f orc=%.3f)"
              % (seed, time.time() - t0,
                 result["per_depth"][str(result["decision_depth"])]["v1_no_goal"],
                 result["per_depth"][str(result["decision_depth"])]["additive_baseline"],
                 result["per_depth"][str(result["decision_depth"])]["cfrpe_trained_gonogo"],
                 result["per_depth"][str(result["decision_depth"])]["oracle"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    # drop failed partials (no per_depth) from verdict aggregation but record them
    good = {k: v for k, v in per_seed.items() if v.get("per_depth")}
    final = aggregate_and_verdict(good)
    if fatal_seed_errors:
        final["fatal_seed_errors"] = fatal_seed_errors
        if final.get("verdict") == "HARD_PASS":
            final["verdict"] = "MIDDLE_BAND"  # do not claim HP if any seed crashed
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
