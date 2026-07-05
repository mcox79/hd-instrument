"""pfc_gate_cfrpe_trained_v2 -- FAIR-REGIME, better-trained-SR RPE Go/NoGo gate.

WHY v2 (VET steer 2026-07-05, atom commit f144563ee):
  v1 FULL landed HARD_FAIL_ADDITIVE_RAIL, but the landed-VET proved it was a
  BROKEN-RAIL TEST-DESIGN FAILURE, not a structural collapse. At the v1 FULL regime
  (N=8192, V=2400 => N/V=3.41, decision_depth=6) EVERY arm floored:
    MEASURED@data/exp_pfc_gate_cfrpe_trained_v1/metrics.json:per_arm_summary:
      V1=0.013  ADD(a=0.14)=0.015  CTRL=0.018  GONOGO=0.100  ORACLE=0.958
  The additive BASELINE (0.015) fell BELOW its 0.05 measurability floor, so the
  rail-priority branch fired HARD_FAIL_ADDITIVE_RAIL before the gonogo comparison
  was even reached. The RPE mechanism itself is ALIVE and scale-robust:
    MEASURED@..._v1/metrics.json: gonogo/additive ratio ~6.7x@d6; paired sign_p=1.2e-14
      (go_only=52 add_only=1); reach_rank_test=0.495 (>0.25 chance);
      reach_tcos_corr=-0.045 (target-cosine INDEPENDENT).
  And the v1 SMOKE (a FAIR regime: N=2048, V=200 => N/V=10.24, dd=4) already fires
  the discriminator cleanly:
    MEASURED@data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json:
      V1=0.042  ADD(a=0.37)=0.115(IN BAND)  GONOGO=0.479  ORACLE=0.969
      closure=(0.479-0.115)/(0.969-0.115)=0.426  reach_rank_test=0.576  cv=0.187
    (cv=0.187 is dominated by n_test=32 sampling noise: sampling std at p=0.48 is
     sqrt(0.48*0.52/32)=0.088 ~= the whole observed std; FULL n_test=240 cuts it to
     sqrt(0.48*0.52/240)=0.032, so the cv<0.10 HP gate is FULL-scale-reachable.)

  DIAGNOSIS: the fair regime is SHALLOWER decision depth + HIGHER N/V. At depth 6
  the compounding (chain acc = per_hop^depth) starves the ABSOLUTE gonogo-additive
  gap AND floors the baseline; at depth 4-5 with N/V ~ 7-10 the baseline lands in
  band and the mechanism advantage survives.

TWO FIXES (this is the whole point of v2):
  FIX 1 (FAIR REGIME): sweep V (the lever that reliably moves the baseline back into
    band) at decision_depth in {4,5}, holding density constant. Each regime carries an
    EXPLICIT baseline_in_band gate (0.05 < additive < 0.95). A regime whose baseline
    floors or saturates is declared NOT-FAIR and CANNOT be read as a structural
    verdict -- this is the exact META_RULE the VET atomized (a floored baseline must
    not masquerade as a mechanism verdict via a rail-trip). The V=2400 regime is kept
    as an in-cell POSITIVE CONTROL reproducing the v1 floored-baseline condition
    (Gate D: reproduce prior result at test regime).
  FIX 2 (BETTER-TRAINED SR): v1's SR-TD error barely shrank (0.0221->0.0186 = M
    under-trained). v2 boosts rollout coverage (~50*V transitions), SR steps
    (3000->8000), batch (128->256), and adds a linear LR decay schedule so late
    training refines rather than oscillates. Since capability=(per-hop reach)^depth,
    small per-hop gains compound; target per-hop reach_rank_test > ~0.50 at fair regimes.

MECHANISM (unchanged from v1; composes two already-proven substrate primitives):
  - cfrpe RPE signal = the substrate error-driven delta-rule outer-product update
    (adaptive per-sample LR clamp error/median in [0.25, 4.0]).
  - SR transport matrix M trained by TD(0) on exploration rollouts (TD-error == RPE):
    E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted successor features / Dayan-1993
    SR, Stachenfeld-2017 hippocampal-striatal). reach(cand;goal)=cos(E[cand]@M,E[goal])
    is the early-hop "does this candidate move toward the goal" signal.
  - Go/NoGo actor: Go_i = w_manifold*manifold_i + w_goal*goal_sim_i + w_reach*reach_i;
    gate = argmax_i Go_i (winner-take-all). w_reach tuned on TRAIN rollouts only;
    w_reach==0 reduces GONOGO exactly to ADDITIVE_BASELINE (clean null reduction).

ARMS (paired -- all share E, W_ops, and the SAME test chains per (regime,seed)):
  ARM_V1_NO_GOAL              goal-blind manifold reference
  ARM_ADDITIVE_BASELINE       static additive goal-bias, alpha tuned on train
  ARM_CFRPE_CONTROL_IDENTITY  gonogo with reach:=target-cosine (M=identity); anti-tautology foil
  ARM_CFRPE_TRAINED_GONOGO    SR/TD-transport Go/NoGo trained by cfrpe delta-rule (THE TEST)
  ARM_ORACLE                  applies the true op_seq (ceiling)

PRIMARY DISCRIMINATOR (per regime, at that regime's decision_depth):
  headroom       = oracle - additive
  closure        = (gonogo - additive) / headroom      (fraction of headroom closed)
  gonogo_lift    = gonogo - additive                    (absolute lift)
  dynamics_lift  = gonogo - control_identity            (win attributable to LEARNED dynamics)

CONTRACT (VET 2026-07-05):
  HARD_PASS : EXISTS a FAIR regime (0.05 < additive < 0.95) where
              closure >= 0.25 AND cv(gonogo) < 0.10 AND reach_tcos_corr < 0.85
              (+ v1-consistent anti-tautology/significance guards: dynamics_lift>0.05,
               sign_p<0.05, mechanism_fires reach_rank_test>0.30, oracle>=0.90).
  HARD_FAIL : fair regime(s) exist AND at ALL of them gonogo_lift <= 0.05
              (mechanism genuinely does not help when the test IS fair).
  MIDDLE_BAND: fair regime helps (gonogo_lift>0.05) but no fair regime clears the
               full HP bar (closure<0.25, OR cv>=0.10, OR not dynamics-attributable).
  INCONCLUSIVE_NO_FAIR_REGIME: NO regime lands the baseline in band (all floored or
               saturated) -- a REGIME-MISS, reported explicitly, NOT a structural
               verdict. This is the META_RULE guard so a rail-trip cannot masquerade.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-regime gonogo/additive op-trace
#   hash-test; exempt when w_reach==0 legitimate reduction)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor;
#   reachability declared via feasibility (v1 SMOKE already measured closure=0.426 at a
#   fair regime, well above the 0.25 HP floor)
# - baseline_in_band at smoke (META_RULE_AG; explicit per-regime 0.05 < additive < 0.95)
# - discriminator survives scale: informational (early-hop reachability); smoke holds N/V
#   ratio identical to FULL per regime (V scaled with N), so per-hop cleanup difficulty
#   matches; smoke is a discriminator-PREVIEW at matched N/V (option C)
# - HARD_PASS strictly at/above contract floor closure>=0.25 (META_RULE_L)
# - HP_SCOPE: HP gates apply ONLY to ARM_CFRPE_TRAINED_GONOGO vs ARM_ADDITIVE_BASELINE
#   at a FAIR regime; rails (oracle>=0.90) apply to ORACLE
# - cardinality_ok: EXPECTED_N_UNITS = n_arms * n_seeds * n_regimes
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank gate)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Compute architecture: (a) batched-GPU. SR-TD training, operator application, cleanup,
reach are batched matmuls on cuda-if-available. Chains batched; within-chain hops are
sequential (genuine dependency). FULL strongly prefers overnight_queue (GPU).
Storage strategy: sharded (each operator its own W matrix; M is a learned value operator,
not an item store). No bundled store.
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress
line + per-regime heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-05 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-05_pfc_gate_cfrpe_trained_v2.md
Cites:
  data/exp_pfc_gate_cfrpe_trained_v1/metrics.json (v1 FULL floored-rail)
  data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json (v1 SMOKE fair-regime closure=0.426)
  experiments/exp_pfc_gate_cfrpe_trained_v1.py (v1 cell heritage; primitives reused)
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

ANCHOR_NAME = "pfc_gate_cfrpe_trained_v2"

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
HP_CLOSURE_FLOOR = 0.25             # contract: gonogo closes >= 25% of headroom
HP_DYNAMICS_LIFT_MIN = 0.05         # real M must beat identity-reach control (anti-tautology)
HP_REACH_TARGETCOS_CORR_MAX = 0.85  # reach must NOT be target-cosine in disguise
HP_CV_MAX = 0.10                    # cross-seed cv on the gonogo arm at the fair regime
HP_SIGN_TEST_P = 0.05
HP_REACH_RANK_MIN = 0.30            # mechanism-fires (held-out reach informativeness > chance 0.25)
HF_GONOGO_LIFT_CEIL = 0.05          # HARD_FAIL: gonogo <= additive + 0.05 at all fair regimes
ORACLE_RAIL_MIN = 0.90
BASELINE_IN_BAND_LO = 0.05         # META_RULE_AG additive acc must be measurable
BASELINE_IN_BAND_HI = 0.95

DENSITY = 0.21                      # n_train_triples_per_op / V (matches v1: 500/2400=0.208)
GAMMA = 0.85                        # SR discount
ADAPT_LR_FLOOR = 0.25              # cfrpe adaptive LR clamp (from source cell)
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2                 # FIX 2: linear LR decay to 0.2*base over training

ALPHA_SWEEP = [0.1, 0.2, 0.5]       # additive goal-bias alpha, tuned on train
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]  # gonogo/control reach weight, tuned on train

ARMS = ["v1_no_goal", "additive_baseline", "cfrpe_control_identity",
        "cfrpe_trained_gonogo", "oracle"]

# --------------------------- config (selftest / smoke / full) --------------------
# Regimes are (V, decision_depth) pairs. N is fixed per mode; V is swept so N/V (the
# cleanup-fidelity lever) brackets the fairness band. SMOKE V's are chosen so smoke N/V
# ratios EQUAL the FULL N/V ratios per regime -> matched per-hop difficulty (scale preview).
if SELF_TEST_MODE:
    N_DIM = 256
    N_OPS = 4
    SEEDS = [7]
    REGIMES = [{"V": 40, "dd": 4}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20                 # transitions ~= ROLLOUT_PER_V * V
elif RUN_MODE == "smoke":
    # must fit under the 180s gate cap. 3 seeds (multi-seed). V's give N/V in
    # {10.24, 6.83, 3.41} == FULL N/V, so per-hop difficulty matches FULL.
    N_DIM = 2048
    N_OPS = 4
    SEEDS = [7, 17, 23]
    # 2 regimes = the N/V bracket ends (keeps SR/tuning/eval cost under the 180s gate cap;
    # the FULL run adds the middle V + dd=5 floored anchor). N/V here == FULL N/V per regime.
    REGIMES = [{"V": 200, "dd": 4},    # N/V=10.24 (fair, matches v1 smoke)
               {"V": 600, "dd": 4}]    # N/V=3.41 (low-N/V bracket end; still fair at dd=4)
    N_TRAIN_CHAINS = 36
    N_TEST_CHAINS = 36
    SR_STEPS = 400                     # trimmed for comfortable margin under 180s gate cap
    SR_BATCH = 64
    SR_LR = 0.5
    ROLLOUT_PER_V = 8                  # capped below; keeps python-loop rollout bounded
else:  # full
    N_DIM = 8192
    N_OPS = 4
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"V": 800, "dd": 4},    # N/V=10.24 (fair, primary)
               {"V": 1200, "dd": 4},   # N/V=6.83  (fair, moderate)
               {"V": 2400, "dd": 4},   # N/V=3.41  (fair candidate at shallow depth)
               {"V": 800, "dd": 5},    # deeper fair candidate
               {"V": 1200, "dd": 5},
               {"V": 2400, "dd": 5},   # deeper; may be marginal
               {"V": 2400, "dd": 6}]   # GATE-D POSITIVE CONTROL: reproduces the v1 FULL
    #   floored condition (N=8192,V=2400,dd=6). Expected additive ~0.015 (floored) -> the
    #   baseline_in_band gate marks it UNFAIR and EXCLUDES it from the verdict, demonstrating
    #   in-cell that a floored baseline does NOT rail-trip into a false structural verdict
    #   (the exact META_RULE the VET atomized). SR is shared with the other V=2400 regimes.
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240               # tames cv: sampling std at p=0.48 -> 0.032
    SR_STEPS = 8000                   # FIX 2: 3000 -> 8000
    SR_BATCH = 256                    # FIX 2: 128 -> 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50                # FIX 2: ~50*V transitions (v1 was ~16.7*V)

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000


def rollout_count(V: int) -> int:
    return int(min(ROLLOUT_CAP, ROLLOUT_PER_V * V))


def n_triples_per_op(V: int) -> int:
    return max(4, int(round(DENSITY * V)))


def regime_key(V: int, dd: int) -> str:
    return "V%d_d%d" % (V, dd)


REGIME_KEYS = [regime_key(r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,N_OPS=%d,seeds=%s,regimes=%s,density=%.3f,sr_steps=%d,sr_batch=%d,"
    "rollout_per_V=%d,gamma=%.2f,lr=%.2f,lr_decay_end=%.2f,alphas=%s,w_reach=%s,"
    "n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_closure>=%.2f,cv<%.2f,corr<%.2f,sign_p<%.2f,reach_rank>%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS, SEEDS, REGIME_KEYS, DENSITY, SR_STEPS, SR_BATCH,
    ROLLOUT_PER_V, GAMMA, SR_LR, LR_DECAY_END, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_CLOSURE_FLOOR, HP_CV_MAX, HP_REACH_TARGETCOS_CORR_MAX, HP_SIGN_TEST_P,
    HP_REACH_RANK_MIN,
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
# primitives (torch, batched, device-agnostic) -- reused verbatim from v1
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
def make_kb_and_chains(n_ops: int, V: int, density: float,
                       n_train_chains: int, n_test_chains: int,
                       depths: List[int], g: np.random.Generator
                       ) -> Tuple[List[List[Tuple[int, int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]],
                                  Dict[int, List[Tuple[int, List[int], int]]]]:
    """Returns (per_op_triples, train_chains_by_depth, test_chains_by_depth).

    Each chain is (start, op_seq[len==depth], target) with a guaranteed exact-length
    path. Train and test chains are distinct draws over the SAME operator graph
    (model-based / held-out-query hygiene). n_train_triples_per_op = round(density*V).
    """
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
# cfrpe-trained SR transport M (TD(0); TD-error == reward-prediction-error)
# FIX 2: linear LR decay schedule + boosted budget (steps/batch/rollout at config).
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features).

    Update = the cfrpe delta-rule with adaptive per-sample LR (error/median clamp) times
    a global linear decay schedule (1.0 -> LR_DECAY_END). Returns (M, diag). diag includes
    err_first/err_last (must shrink) and clamp counts.
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
        decay = 1.0 - (1.0 - LR_DECAY_END) * (step / max(1, steps - 1))  # 1.0 -> LR_DECAY_END
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
        lr_per = base_lr * decay * ratio_c         # [b]
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
    Carries NO dynamics info; proves the trained-M win is not target-cosine in disguise."""
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
    """Batched op-selection arm. mode in {v1, additive, gonogo, gonogo_control}.

    Returns (correct_bool[n_chains], op_trace[n_chains, depth]).
    additive      : sc = alpha*goal_sim + (1-alpha)*manifold
    gonogo        : sc = (1-alpha)*manifold + alpha*goal_sim + w_reach*reach   (learned-M dynamics)
    gonogo_control: sc = (1-alpha)*manifold + alpha*goal_sim + w_reach*targetcos (identity reach)
    v1            : sc = manifold
    """
    starts, targets, _ = _chain_tensors(chains)
    n_chains = starts.shape[0]
    state = E[starts].clone()                      # [n, n_dim]
    goal_E = E[targets]                            # [n, n_dim]
    op_trace = np.zeros((n_chains, depth), dtype=np.int64)
    n_ops = len(W_ops)
    w_manifold = max(0.0, 1.0 - alpha)
    final_idx = starts
    for hop in range(depth):
        scores = torch.empty((n_chains, n_ops), dtype=DTYPE, device=DEVICE)
        cand_idx = torch.empty((n_chains, n_ops), dtype=torch.long, device=DEVICE)
        for op in range(n_ops):
            out = state @ W_ops[op]                # [n, n_dim]
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
    """Anti-tautology guard: Pearson corr between learned-M reach and raw target-cosine
    across all candidate ops along the true trajectory. corr near 1.0 => reach IS
    target-cosine in disguise. Low corr => reach carries dynamics info."""
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
    mu = n * p
    sd = math.sqrt(n * p * (1 - p))
    z = (abs(k - mu) - 0.5) / (sd + 1e-12)
    return float(min(1.0, 2.0 * 0.5 * math.erfc(z / math.sqrt(2.0))))


# ============================================================================
# per-seed runner (loops over regimes; SR trained once per unique V)
# ============================================================================
def _eval_regime(V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, train_by_d, test_by_d) -> Dict[str, Any]:
    """Tune on train, evaluate all arms on test, return per-regime record for one seed."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    # tune alpha (additive) on train
    best_alpha, best_add_train = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_arm("additive", train_c, W_ops, E, M, dd, a, 0.0)[0].mean()
        if acc > best_add_train:
            best_add_train, best_alpha = acc, a
    # tune w_reach (gonogo) on train, holding best_alpha
    best_wr, best_go_train = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo", train_c, W_ops, E, M, dd, best_alpha, wr)[0].mean()
        if acc > best_go_train:
            best_go_train, best_wr = acc, wr
    # tune identity-reach CONTROL independently (steelman the foil)
    best_wr_ctrl, best_ctrl_train = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm("gonogo_control", train_c, W_ops, E, M, dd,
                                best_alpha, wr)[0].mean()
        if acc > best_ctrl_train:
            best_ctrl_train, best_wr_ctrl = acc, wr

    # mechanism-fires probe + anti-tautology corr (train + held-out)
    reach_rank_train = reach_rank_acc(train_c, W_ops, E, M, dd)
    reach_rank_test = reach_rank_acc(test_c, W_ops, E, M, dd)
    reach_tcos_corr_test = reach_vs_targetcos_corr(test_c, W_ops, E, M, dd)

    # evaluate all arms on TEST chains (paired)
    v1_c, v1_tr = run_selection_arm("v1", test_c, W_ops, E, M, dd, 0.0, 0.0)
    add_c, add_tr = run_selection_arm("additive", test_c, W_ops, E, M, dd, best_alpha, 0.0)
    ctrl_c, ctrl_tr = run_selection_arm("gonogo_control", test_c, W_ops, E, M, dd,
                                        best_alpha, best_wr_ctrl)
    go_c, go_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)

    paired = {
        "n_gonogo_only": int(((go_c) & (~add_c)).sum()),
        "n_additive_only": int(((add_c) & (~go_c)).sum()),
        "n_both": int((go_c & add_c).sum()),
        "n_neither": int(((~go_c) & (~add_c)).sum()),
        "n_test": int(len(go_c)),
        "n_gonogo_over_ctrl": int(((go_c) & (~ctrl_c)).sum()),
        "n_ctrl_over_gonogo": int(((ctrl_c) & (~go_c)).sum()),
    }
    return {
        "V": V, "dd": dd,
        "arms": {
            "v1_no_goal": float(v1_c.mean()),
            "additive_baseline": float(add_c.mean()),
            "cfrpe_control_identity": float(ctrl_c.mean()),
            "cfrpe_trained_gonogo": float(go_c.mean()),
            "oracle": float(orc_c.mean()),
        },
        "op_trace_hashes": {
            "v1_no_goal": hashlib.sha256(v1_tr.tobytes()).hexdigest()[:16],
            "additive_baseline": hashlib.sha256(add_tr.tobytes()).hexdigest()[:16],
            "cfrpe_control_identity": hashlib.sha256(ctrl_tr.tobytes()).hexdigest()[:16],
            "cfrpe_trained_gonogo": hashlib.sha256(go_tr.tobytes()).hexdigest()[:16],
            "oracle": "oracle_true_seq",
        },
        "best_alpha": float(best_alpha),
        "best_w_reach": float(best_wr),
        "best_w_reach_ctrl": float(best_wr_ctrl),
        "additive_train_acc": float(best_add_train),
        "gonogo_train_acc": float(best_go_train),
        "control_train_acc": float(best_ctrl_train),
        "reach_rank_train": float(reach_rank_train),
        "reach_rank_test": float(reach_rank_test),
        "reach_tcos_corr_test": float(reach_tcos_corr_test),
        "paired": paired,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    # group regimes by V so SR / KB / E are built once per unique V
    by_V: Dict[int, List[int]] = {}
    for r in REGIMES:
        by_V.setdefault(r["V"], []).append(r["dd"])

    regime_results: Dict[str, Any] = {}
    sr_diag_by_V: Dict[str, Any] = {}
    for V in sorted(by_V.keys()):
        depths_needed = sorted(set(by_V[V]))
        tgen = torch.Generator(device=DEVICE)
        tgen.manual_seed(int(seed) * 100003 + int(V))
        E = make_bipolar_E(V, N_DIM, tgen)
        per_op, train_by_d, test_by_d = make_kb_and_chains(
            N_OPS, V, DENSITY, N_TRAIN_CHAINS, N_TEST_CHAINS, depths_needed, g)
        W_ops = [hebbian_W(per_op[i], E, N_DIM) for i in range(N_OPS)]
        adj = build_adjacency(per_op, N_OPS)

        # train SR transport M via cfrpe delta-rule (exploration rollouts only)
        max_len = max(depths_needed) + 2
        transitions = collect_rollout_transitions(
            adj, N_OPS, V, rollout_count(V), max_len, g)
        sr_gen = torch.Generator(device=DEVICE)
        sr_gen.manual_seed(int(seed) * 7919 + int(V))
        M, sr_diag = train_sr_transport(
            E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, GAMMA, sr_gen)
        sr_diag_by_V[str(V)] = sr_diag
        print("[seed=%d V=%d] SR trained: err %s->%s M_norm=%.3f n_trans=%d clamp=%d"
              % (seed, V, sr_diag["err_first"], sr_diag["err_last"],
                 sr_diag["final_M_norm"], sr_diag["n_transitions"],
                 sr_diag["n_clamped_steps"]), flush=True)

        for dd in depths_needed:
            rec = _eval_regime(V, dd, E, W_ops, M, train_by_d, test_by_d)
            rec["sr_err_first"] = sr_diag["err_first"]
            rec["sr_err_last"] = sr_diag["err_last"]
            key = regime_key(V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            print("[seed=%d %s] V1=%.3f ADD=%.3f CTRL=%.3f GONOGO=%.3f ORC=%.3f "
                  "(a=%.2f wr=%.1f reach_rank_test=%.3f)"
                  % (seed, key, a["v1_no_goal"], a["additive_baseline"],
                     a["cfrpe_control_identity"], a["cfrpe_trained_gonogo"],
                     a["oracle"], rec["best_alpha"], rec["best_w_reach"],
                     rec["reach_rank_test"]), flush=True)

    return {
        "seed": int(seed),
        "N": N_DIM, "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME, "config_version": CONFIG_VERSION,
        "regime_results": regime_results,
        "sr_diag_by_V": sr_diag_by_V,
    }


# ============================================================================
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_regime": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _arm_col(rk, arm):
        return [float(per_seed[k]["regime_results"][rk]["arms"][arm]) for k in keys
                if rk in per_seed[k].get("regime_results", {})]

    def _scalar_col(rk, field):
        return [float(per_seed[k]["regime_results"][rk][field]) for k in keys
                if rk in per_seed[k].get("regime_results", {})]

    per_regime: Dict[str, Any] = {}
    completed_units = 0
    for r in REGIMES:
        rk = regime_key(r["V"], r["dd"])
        arm_means = {}
        arm_cvs = {}
        arm_stds = {}
        n_present = 0
        for arm in ARMS:
            vals = _arm_col(rk, arm)
            if vals:
                m = float(np.mean(vals)); sd = float(np.std(vals))
                arm_means[arm] = m
                arm_stds[arm] = sd
                arm_cvs[arm] = float(sd / m) if m > 1e-6 else 0.0
                n_present = len(vals)
            else:
                arm_means[arm] = 0.0; arm_stds[arm] = 0.0; arm_cvs[arm] = 0.0
        completed_units += n_present * len(ARMS)

        add = arm_means["additive_baseline"]
        go = arm_means["cfrpe_trained_gonogo"]
        ctrl = arm_means["cfrpe_control_identity"]
        orc = arm_means["oracle"]
        v1 = arm_means["v1_no_goal"]
        headroom = orc - add
        closure = ((go - add) / headroom) if headroom > 1e-6 else 0.0
        gonogo_lift = go - add
        dynamics_lift = go - ctrl
        additive_lift = add - v1
        baseline_in_band = (BASELINE_IN_BAND_LO < add < BASELINE_IN_BAND_HI)

        reach_rank_test = float(np.mean(_scalar_col(rk, "reach_rank_test"))) if keys else 0.0
        reach_tcos_corr = float(np.mean(_scalar_col(rk, "reach_tcos_corr_test"))) if keys else 0.0
        best_wr_vals = _scalar_col(rk, "best_w_reach")
        all_wr_zero = all(abs(w) < 1e-9 for w in best_wr_vals) if best_wr_vals else True

        # paired sign-test pooled across seeds at this regime
        n_go_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_gonogo_only"])
                        for k in keys if rk in per_seed[k].get("regime_results", {}))
        n_add_only = sum(int(per_seed[k]["regime_results"][rk]["paired"]["n_additive_only"])
                         for k in keys if rk in per_seed[k].get("regime_results", {}))
        n_disc = n_go_only + n_add_only
        sign_p = binom_two_sided_p(n_go_only, n_disc, 0.5) if n_disc > 0 else 1.0

        # arms-differ (META_RULE_AF): gonogo vs additive op-trace hashes must differ per
        # seed at this regime UNLESS w_reach==0 (legitimate reduction -> exempt)
        af_collision = False
        for k in keys:
            if rk not in per_seed[k].get("regime_results", {}):
                continue
            rr = per_seed[k]["regime_results"][rk]
            if rr["best_w_reach"] > 1e-9:
                if rr["op_trace_hashes"]["cfrpe_trained_gonogo"] == \
                   rr["op_trace_hashes"]["additive_baseline"]:
                    af_collision = True

        per_regime[rk] = {
            "V": r["V"], "dd": r["dd"], "n_seeds": len(best_wr_vals),
            "arm_means": arm_means, "arm_cvs": arm_cvs, "arm_stds": arm_stds,
            "additive": add, "gonogo": go, "control_identity": ctrl, "oracle": orc,
            "v1_no_goal": v1,
            "headroom": float(headroom), "closure": float(closure),
            "gonogo_lift": float(gonogo_lift), "dynamics_lift": float(dynamics_lift),
            "additive_lift": float(additive_lift),
            "gonogo_cv": arm_cvs["cfrpe_trained_gonogo"],
            "baseline_in_band": bool(baseline_in_band),
            "reach_rank_test": reach_rank_test,
            "reach_tcos_corr_test": reach_tcos_corr,
            "sign_test_p": float(sign_p),
            "n_gonogo_only": int(n_go_only), "n_additive_only": int(n_add_only),
            "best_w_reach_per_seed": {keys[i]: best_wr_vals[i] for i in range(len(best_wr_vals))},
            "all_w_reach_zero": bool(all_wr_zero),
            "af_collision": bool(af_collision),
            "oracle_rail_ok": bool(orc >= ORACLE_RAIL_MIN),
        }

    # ---- fair-regime selection + verdict ----
    fair = {rk: v for rk, v in per_regime.items() if v["baseline_in_band"]}
    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    # cv<0.10 is a FULL-scale cross-seed stability gate: at smoke n_test (<=48) the
    # per-seed accuracy sampling std (~sqrt(p(1-p)/n_test)) dominates cv, so cv is NOT
    # fairly evaluable in smoke (documented; matches v1-smoke cv=0.187 n_test=32 note).
    # Enforce cv ONLY at full; in smoke it is reported but does not block discriminator-fires.
    CV_GATE_ENFORCED = (RUN_MODE == "full")

    # HP candidate: fair regime meeting the full contract
    def _hp_ok(v):
        return (v["closure"] >= HP_CLOSURE_FLOOR
                and (v["gonogo_cv"] < HP_CV_MAX or not CV_GATE_ENFORCED)
                and v["reach_tcos_corr_test"] < HP_REACH_TARGETCOS_CORR_MAX
                and v["dynamics_lift"] > HP_DYNAMICS_LIFT_MIN
                and v["sign_test_p"] < HP_SIGN_TEST_P
                and v["reach_rank_test"] > HP_REACH_RANK_MIN
                and v["oracle_rail_ok"]
                and not v["af_collision"])

    hp_regimes = {rk: v for rk, v in fair.items() if _hp_ok(v)}
    # best fair regime = max closure among fair (for reporting)
    best_fair_rk = max(fair, key=lambda k: fair[k]["closure"]) if fair else None
    best_hp_rk = max(hp_regimes, key=lambda k: hp_regimes[k]["closure"]) if hp_regimes else None

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not fair:
        # META_RULE guard: no fair regime -> cannot render a structural verdict
        verdict = "INCONCLUSIVE_NO_FAIR_REGIME"
    elif hp_regimes:
        verdict = "HARD_PASS"
    elif all(v["gonogo_lift"] <= HF_GONOGO_LIFT_CEIL for v in fair.values()):
        verdict = "HARD_FAIL_RPE_NO_HELP"
    else:
        # helps at a fair regime but does not clear the full HP bar
        bf = fair[best_fair_rk]
        if bf["closure"] >= HP_CLOSURE_FLOOR and not (
                bf["dynamics_lift"] > HP_DYNAMICS_LIFT_MIN
                and bf["reach_tcos_corr_test"] < HP_REACH_TARGETCOS_CORR_MAX):
            verdict = "MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE"
        elif bf["closure"] >= HP_CLOSURE_FLOOR and bf["gonogo_cv"] >= HP_CV_MAX:
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        else:
            verdict = "MIDDLE_BAND_HELPS_BELOW_25"

    # report focus = best HP regime if any, else best fair regime, else first regime
    focus_rk = best_hp_rk or best_fair_rk or REGIME_KEYS[0]
    fr = per_regime[focus_rk]
    in_band_summary = ",".join(
        "%s:%.3f%s" % (rk, per_regime[rk]["additive"],
                       "(FAIR)" if per_regime[rk]["baseline_in_band"] else "(unfair)")
        for rk in REGIME_KEYS)

    verdict_msg = (
        "%s | n_fair=%d/%d focus=%s | ADD=%.3f GONOGO=%.3f CTRL=%.3f ORACLE=%.3f | "
        "closure=%.3f gonogo_lift=%.3f dynamics_lift=%.3f headroom=%.3f | "
        "baseline_in_band=%s cv=%.3f reach_tcos_corr=%.3f sign_p=%.4f "
        "(go_only=%d add_only=%d) reach_rank_test=%.3f oracle_rail=%s | "
        "additive_per_regime=[%s] n_seeds=%d"
    ) % (
        verdict, len(fair), len(REGIMES), focus_rk,
        fr["additive"], fr["gonogo"], fr["control_identity"], fr["oracle"],
        fr["closure"], fr["gonogo_lift"], fr["dynamics_lift"], fr["headroom"],
        fr["baseline_in_band"], fr["gonogo_cv"], fr["reach_tcos_corr_test"],
        fr["sign_test_p"], fr["n_gonogo_only"], fr["n_additive_only"],
        fr["reach_rank_test"], fr["oracle_rail_ok"], in_band_summary, len(keys),
    )

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_regime": per_regime,
        "fair_regime_keys": list(fair.keys()),
        "hp_regime_keys": list(hp_regimes.keys()),
        "focus_regime": focus_rk,
        "focus_closure": fr["closure"],
        "focus_gonogo_lift": fr["gonogo_lift"],
        "focus_baseline_in_band": fr["baseline_in_band"],
        "focus_reach_rank_test": fr["reach_rank_test"],
        "focus_gonogo_cv": fr["gonogo_cv"],
        "focus_reach_tcos_corr": fr["reach_tcos_corr_test"],
        "clears_25pct_headroom": bool(fr["closure"] >= HP_CLOSURE_FLOOR
                                      and fr["baseline_in_band"]),
        "cv_gate_enforced": bool(CV_GATE_ENFORCED),
        "focus_cv_meets_full_gate": bool(fr["gonogo_cv"] < HP_CV_MAX),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": int(completed_units),
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

    # ST2b: LR decay schedule monotone-decreasing 1.0 -> LR_DECAY_END
    steps = 100
    decays = [1.0 - (1.0 - LR_DECAY_END) * (s / max(1, steps - 1)) for s in range(steps)]
    assert abs(decays[0] - 1.0) < 1e-9, "ST2b decay start != 1.0"
    assert abs(decays[-1] - LR_DECAY_END) < 1e-9, "ST2b decay end != LR_DECAY_END"
    assert all(decays[i] >= decays[i + 1] - 1e-12 for i in range(steps - 1)), "ST2b not monotone"
    print("[selftest] ST2b LR decay %.2f->%.2f monotone OK" % (decays[0], decays[-1]), flush=True)

    # ST3: Go/NoGo competition selects argmax Go-value
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]], device=DEVICE)
    assert int(scores.argmax(dim=1)[0]) == 1, "ST3 argmax competition wrong"
    print("[selftest] ST3 Go/NoGo argmax competition OK", flush=True)

    # ST4 (MECHANISM-FIRES): branch A 0->1->2->3 (goal=3); branch B 0->4->5->6 (away).
    #   Trained reach ranks ON-PATH node 1 above OFF-PATH node 4 for goal 3.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(3)
    Vt, Nt = 8, 512
    Et = make_bipolar_E(Vt, Nt, gen4)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)
    toy_trans = np.concatenate([np.tile(chainA, (30, 1)), np.tile(chainB, (30, 1))], axis=0)
    Mt, _ = train_sr_transport(Et, toy_trans, Nt, steps=600, batch=16, base_lr=0.5,
                               gamma=0.8, gen=gen4)
    goal = Et[3:4]
    reach_on = float(reach_value(Et[1:2], goal, Mt)[0])
    reach_off = float(reach_value(Et[4:5], goal, Mt)[0])
    assert reach_on > reach_off, (
        "ST4 MECHANISM-FIRES FAIL: reach on-path=%.4f !> off-path=%.4f" % (reach_on, reach_off))
    print("[selftest] ST4 mechanism-fires: reach on-path=%.4f > off-path=%.4f OK"
          % (reach_on, reach_off), flush=True)

    # ST7 (ANTI-TAUTOLOGY): identity-reach CONTROL (target-cosine) is UNINFORMATIVE
    #   exactly where trained M is informative.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    trained_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert trained_sep > control_sep + 0.05, (
        "ST7 ANTI-TAUTOLOGY FAIL: trained-sep=%.4f not clearly > control-sep=%.4f"
        % (trained_sep, control_sep))
    print("[selftest] ST7 anti-tautology: trained-sep=%.4f >> control-sep=%.4f OK"
          % (trained_sep, control_sep), flush=True)

    # ST5: full pipeline single-seed structural (regime sweep) + arms present + oracle high
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_gate_v2")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST5 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST5 missing arm %s" % arm
    orc = r["regime_results"][rk0]["arms"]["oracle"]
    assert orc >= 0.5, "ST5 oracle too low (%.3f) on toy self-test" % orc
    print("[selftest] ST5 pipeline OK regimes=%s oracle=%.3f reach_rank_test=%.3f"
          % (REGIME_KEYS, orc, r["regime_results"][rk0]["reach_rank_test"]), flush=True)

    # ST6: binomial p symmetric + bounded
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0, "ST6 binom p out of range"
    assert abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST6 not symmetric"
    print("[selftest] ST6 binom two-sided p(8/10)=%.4f OK" % p, flush=True)

    # ST8 (CLOSURE FORMULA): closure = (gonogo-additive)/(oracle-additive)
    go_, add_, orc_ = 0.479, 0.115, 0.969
    cl = (go_ - add_) / (orc_ - add_)
    assert abs(cl - 0.42623) < 1e-3, "ST8 closure formula off: %.5f" % cl
    print("[selftest] ST8 closure formula OK (v1-smoke fair regime closure=%.3f)" % cl, flush=True)
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

    print("[%s] mode=%s device=%s N=%d ops=%d seeds=%s regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS, SEEDS,
             REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST8 (cfrpe-TD shrink, adaptive LR, LR "
                               "decay monotone, Go/NoGo argmax, mechanism-fires reach, "
                               "anti-tautology control, regime-sweep pipeline, binom, "
                               "closure formula)",
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
                "regime_results": {}, "sr_diag_by_V": {}})
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
