"""pfc_gate_cfrpe_deeper_regime_v1 -- does a LONGER-HORIZON SR restore the RPE Go/NoGo
control gate at DEPTH-6, and WHY does the v2 gate degrade past depth-4?

WHY v1-deeper (Director steer 2026-07-05):
  v2 FULL proved the cf-RPE-trained Go/NoGo gate at a FAIR depth-4 regime
  (MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json):
    V1200_d4: ADD=0.053 GONOGO=0.653 ORACLE=0.962 closure=0.661 reach_rank_test=0.690
  but the SAME gate DEGRADES to gonogo=0.075 (closure=0.073) at depth-6:
    V2400_d6: ADD=0.007 GONOGO=0.075 ORACLE=0.945 reach_rank_test=0.509
  The mechanism signal (reach_rank_test = along-true-trajectory op-selection by the reach
  value; chance=1/n_ops=0.25) traces the collapse (MEASURED@..._v2/metrics.json):
    d4: 0.686/0.690/0.649   d5: 0.615/0.610/0.564   d6: 0.509
  reach_rank falls ~26% d4->d6 (still above chance, but the per-hop reach edge erodes,
  and capability = per_hop_reach^depth compounds the erosion catastrophically).

MECHANISM HYPOTHESIS (tested here, NOT assumed):
  The SR transport M is trained by TD(0) with discount gamma=0.85 -> effective horizon
  ~ 1/(1-gamma) = 6.7 steps. reach(cand;goal) = cos(E[cand]@M, E[goal]); E[cand]@M is the
  discounted successor-feature bundle sum_k gamma^k E[state_k]. At depth d the goal is up
  to d-1 hops beyond a candidate, weighted gamma^(d-1) inside the SR bundle:
    gamma=0.85: goal 5 hops out weighted 0.85^5 = 0.44 THEORETICAL@geometric-SR-horizon
    gamma=0.95: goal 5 hops out weighted 0.95^5 = 0.77 THEORETICAL@geometric-SR-horizon
  So at depth-6 the goal sits near/past the gamma=0.85 horizon and the reach signal
  starves. FIX = a LONGER-HORIZON SR (higher gamma). Brain-grounded:
  CITED@notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md:chunk019
  "hippocampus implements a bank of SR at different temporal scales (different gamma) ...
   dorsal=small fields=short gamma; ventral=large fields=long gamma" (Stachenfeld-2017).

THE TEST (controlled horizon comparison):
  Train the SR transport M at multiple gammas on the SAME rollout transitions (identical
  minibatch draws -> only gamma differs). Compare, per depth {4,6}:
    BASELINE-SR  gamma=0.85 (the v2 value)
    DEEPER-SR    gamma=0.95, 0.99 (the fix)
  Primary mechanism signal (fairness-INDEPENDENT): reach_rank_test(depth, gamma). Does a
  deeper horizon lift reach_rank at d6 back toward its d4 value?

FAIRNESS (branching lever, analogous to v2's V lever):
  At n_ops=4, N=8192 the additive baseline FLOORS at d6 for every V tested in v2 (all
  additive <= 0.016) -> NO fair d6 regime exists there (a REGIME-MISS, not a structural
  result -- the exact META_RULE v2 atomized). Per-hop additive ~0.48 -> 0.48^6=0.012.
  Lowering branching n_ops raises per-hop additive (fewer wrong ops to beat), pushing the
  compounded baseline back into band at d6. So n_ops is swept {2,4}: n_ops=4 is the HARD
  diagnosis regime (reproduces the v2 d6 floor -- Gate-D positive control); n_ops=2 is the
  FAIR-d6 CANDIDATE where the closure contract can actually render.

ARMS (paired -- share E, W_ops, and the SAME test chains per (regime,seed)):
  v1_no_goal              goal-blind manifold reference
  additive_baseline       static additive goal-bias, alpha tuned on train (SR-independent)
  cfrpe_control_identity  gonogo with reach:=target-cosine (M=identity); anti-tautology foil
  oracle                  applies the true op_seq (ceiling)
  gonogo_g0.85            SR/TD Go/NoGo, gamma=0.85  (BASELINE-SR = v2's)
  gonogo_g0.95            SR/TD Go/NoGo, gamma=0.95  (DEEPER-SR fix)
  gonogo_g0.99            SR/TD Go/NoGo, gamma=0.99  (DEEPER-SR fix, longest horizon)

PRIMARY DISCRIMINATOR (per regime, at that regime's decision_depth, per gamma):
  headroom      = oracle - additive
  closure[g]    = (gonogo[g] - additive) / headroom
  gonogo_lift[g]= gonogo[g] - additive
  dynamics_lift[g] = gonogo[g] - control_identity
  reach_rank[g] = along-true-trajectory reach op-selection acc (chance 1/n_ops)

CONTRACT (Director 2026-07-05):
  HARD_PASS : EXISTS a FAIR depth-6 regime (0.05 < additive < 0.95) where a DEEPER-SR
              (gamma > 0.85) closes closure[g] >= 0.25 AND gonogo_lift[g] > 0.05 AND
              reach_tcos_corr[g] < 0.85 (anti-tautology) AND dynamics_lift[g] > 0.05 AND
              sign_p[g] < 0.05 AND reach_rank[g] > 1/n_ops + 0.05 AND oracle >= 0.90.
              => control EXTENDS past depth-4 (the mechanism is not a shallow-only device).
  HARD_FAIL : fair depth-6 regime(s) exist AND at ALL of them, EVERY gamma (baseline AND
              deeper) has gonogo_lift <= 0.05 => the fix cannot extend control past depth-4
              at a fair regime (control is genuinely a shallow-depth mechanism -- an honest,
              useful bound).
  MIDDLE_BAND: fair depth-6 helps (some gamma gonogo_lift>0.05) but no deeper-SR clears the
              full HP bar at a fair d6 regime.
  INCONCLUSIVE_NO_FAIR_REGIME: NO depth-6 regime lands the baseline in band -- a REGIME-MISS,
              reported explicitly with the reach_rank mechanism signal still surfaced.
  Reported REGARDLESS of verdict (the requested mechanism deliverable):
    reach_rank_test at d4 vs d6 for baseline-SR AND deeper-SR, per (V,n_ops) group; plus
    horizon_attributable = closure[best_deep] - closure[baseline] at the focus fair d6.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-regime per-gamma gonogo op-trace
#   hash-test vs additive; exempt when best_w_reach==0 legitimate reduction)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: accuracy-closure discriminator has no single closed-form noise floor;
#   reachability declared via feasibility (v2 FULL measured closure=0.66 at a fair d4 regime,
#   and reach_rank>chance at d6 -- the signal is present, the question is whether horizon
#   extension restores it at a FAIR d6 regime)
# - baseline_in_band at smoke (META_RULE_AG; explicit per-regime 0.05 < additive < 0.95;
#   the n_ops=2 d6 candidate is the fairness preview)
# - discriminator survives scale: smoke holds N/V ratio == FULL per (V,n_ops) and IDENTICAL
#   decision depths {4,6} -> per-hop cleanup difficulty AND the depth-dependence match FULL;
#   smoke is a discriminator PREVIEW at matched N/V + matched depth (option C)
# - HARD_PASS strictly at/above contract floor closure>=0.25 (META_RULE_L)
# - HP_SCOPE: HP gates apply ONLY to gonogo_g0.95/g0.99 (deeper-SR) vs additive at a FAIR d6
#   regime; oracle_rail (>=0.90) applies to ORACLE
# - cardinality_ok: EXPECTED_N_UNITS = n_arms * n_seeds * n_regimes
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank gate)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Compute architecture: (a) batched-GPU. SR-TD training (per gamma), operator application,
cleanup, reach are batched matmuls on cuda-if-available. Chains batched; within-chain hops
are sequential (genuine dependency). FULL strongly prefers overnight_queue (GPU).
Storage strategy: sharded (each operator its own W matrix; M is a learned value operator,
not an item store). No bundled store.
progress_logging: print_flush_true (line-buffered stdout + flush=True on every progress
line + per (seed,V,n_ops,gamma) heartbeat; FULL timeout_s >= 1800).

Author: exp_dev 2026-07-05 (Opus 4.8 1M, agent-spawn)
Prereg: d:/AI/hd-instrument/preregs/2026-07-05_pfc_gate_cfrpe_deeper_regime_v1.md
Cites:
  data/exp_pfc_gate_cfrpe_trained_v2/metrics.json (v2 FULL: d4 pass, d6 degrade)
  experiments/exp_pfc_gate_cfrpe_trained_v2.py (v2 cell; primitives reused verbatim)
  notes/research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md (multi-scale SR)
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

ANCHOR_NAME = "pfc_gate_cfrpe_deeper_regime_v1"

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
HP_CLOSURE_FLOOR = 0.25             # contract: deeper-SR closes >= 25% of headroom
HP_DYNAMICS_LIFT_MIN = 0.05         # real M must beat identity-reach control (anti-tautology)
HP_REACH_TARGETCOS_CORR_MAX = 0.85  # reach must NOT be target-cosine in disguise
HP_CV_MAX = 0.10                    # cross-seed cv on the deeper-SR gonogo arm at fair d6
HP_SIGN_TEST_P = 0.05
HP_REACH_RANK_MARGIN = 0.05         # mechanism-fires: reach_rank > 1/n_ops + margin
HF_GONOGO_LIFT_CEIL = 0.05          # HARD_FAIL: gonogo <= additive + 0.05 at all fair d6 (all gammas)
ORACLE_RAIL_MIN = 0.90
BASELINE_IN_BAND_LO = 0.05         # META_RULE_AG additive acc must be measurable
BASELINE_IN_BAND_HI = 0.95

DENSITY = 0.21                      # n_train_triples_per_op / V (matches v2: 500/2400=0.208)
ADAPT_LR_FLOOR = 0.25              # cfrpe adaptive LR clamp (from source cell)
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2                 # linear LR decay to 0.2*base over training

BASELINE_GAMMA = 0.85              # the v2 SR discount (short horizon)
ALPHA_SWEEP = [0.1, 0.2, 0.5]       # additive goal-bias alpha, tuned on train
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]  # gonogo/control reach weight, tuned on train

# --------------------------- config (selftest / smoke / full) --------------------
# Regime = (n_ops, V, dd). n_ops is the BRANCHING/fairness lever (lower -> higher per-hop
# additive -> baseline survives depth-6 compounding into band). SR M is trained per unique
# (V,n_ops) and shared across depths at that group AND swept over GAMMA_SWEEP (the horizon
# fix). SMOKE holds N/V == FULL and IDENTICAL depths {4,6} -> matched per-hop difficulty AND
# matched depth-dependence (discriminator preview, option C).
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    GAMMA_SWEEP = [0.85, 0.95]
    REGIMES = [{"n_ops": 4, "V": 40, "dd": 4}, {"n_ops": 2, "V": 40, "dd": 4}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # multi-seed (3). 2 gammas (baseline + one deeper) to fit the 180s gate. Regimes cover
    # the 3 discriminators: (a) reach_rank d4-vs-d6 degradation at n_ops=4;
    # (b) deeper-SR effect at d6; (c) additive in-band at the n_ops=2 d6 FAIR candidate.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    GAMMA_SWEEP = [0.85, 0.95]
    REGIMES = [{"n_ops": 4, "V": 300, "dd": 4},   # N/V=6.83; reach_rank d4 baseline
               {"n_ops": 4, "V": 300, "dd": 6},   # N/V=6.83; reach_rank d6 degradation
               {"n_ops": 2, "V": 300, "dd": 6}]   # N/V=6.83; FAIR-d6 candidate preview
    N_TRAIN_CHAINS = 48
    N_TEST_CHAINS = 48
    SR_STEPS = 300                     # trimmed for margin under the 180s gate cap
    SR_BATCH = 64
    SR_LR = 0.5
    ROLLOUT_PER_V = 8
else:  # full
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    GAMMA_SWEEP = [0.85, 0.95, 0.99]   # baseline + two deeper horizons (fix trend)
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4},  # Gate-D repro of v2 fair d4
               {"n_ops": 4, "V": 1200, "dd": 6},  # HARD d6 (reproduces v2 floor; diagnosis)
               {"n_ops": 2, "V": 800, "dd": 4},   # narrow-branch d4 (headroom sanity)
               {"n_ops": 2, "V": 800, "dd": 6},   # FAIR-d6 candidate A (high N/V=10.24)
               {"n_ops": 2, "V": 1200, "dd": 4},  # narrow-branch d4
               {"n_ops": 2, "V": 1200, "dd": 6}]  # FAIR-d6 candidate B (N/V=6.83)
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240               # tames cv: sampling std at p=0.5 -> ~0.032
    SR_STEPS = 8000                   # matches v2 baseline budget (same for all gammas -> controlled)
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50                # ~50*V transitions (v2 FULL value)

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000

GAMMA_KEYS = ["g%.2f" % g for g in GAMMA_SWEEP]
DEEP_GAMMAS = [g for g in GAMMA_SWEEP if g > BASELINE_GAMMA + 1e-9]
DEEP_GAMMA_KEYS = ["g%.2f" % g for g in DEEP_GAMMAS]
BASELINE_GAMMA_KEY = "g%.2f" % BASELINE_GAMMA
GONOGO_ARMS = ["gonogo_" + gk for gk in GAMMA_KEYS]
BASE_ARMS = ["v1_no_goal", "additive_baseline", "cfrpe_control_identity", "oracle"]
ARMS = BASE_ARMS + GONOGO_ARMS
N_OPS_SET = sorted(set(r["n_ops"] for r in REGIMES))


def gamma_of_key(gk: str) -> float:
    return float(gk[1:])


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


REGIME_KEYS = [regime_key(r["n_ops"], r["V"], r["dd"]) for r in REGIMES]
EXPECTED_N_UNITS = len(ARMS) * len(SEEDS) * len(REGIMES)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,n_ops_set=%s,seeds=%s,gammas=%s,regimes=%s,density=%.3f,sr_steps=%d,"
    "sr_batch=%d,rollout_per_V=%d,baseline_gamma=%.2f,lr=%.2f,lr_decay_end=%.2f,alphas=%s,"
    "w_reach=%s,n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_closure>=%.2f,cv<%.2f,corr<%.2f,sign_p<%.2f,reach_rank_margin=%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS_SET, SEEDS, GAMMA_SWEEP, REGIME_KEYS, DENSITY, SR_STEPS,
    SR_BATCH, ROLLOUT_PER_V, BASELINE_GAMMA, SR_LR, LR_DECAY_END, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_CLOSURE_FLOOR, HP_CV_MAX, HP_REACH_TARGETCOS_CORR_MAX, HP_SIGN_TEST_P,
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
# primitives (torch, batched, device-agnostic) -- reused verbatim from v2
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
# gamma is the HORIZON parameter under test. linear LR decay + boosted budget at config.
# ============================================================================
def train_sr_transport(E: torch.Tensor, transitions: np.ndarray, n: int,
                       steps: int, batch: int, base_lr: float, gamma: float,
                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """Learn M [n,n] s.t. E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M) (discounted SR features).

    Update = cfrpe delta-rule with adaptive per-sample LR (error/median clamp) times a
    global linear decay schedule (1.0 -> LR_DECAY_END). gamma sets the SR horizon
    (~1/(1-gamma) steps). Returns (M, diag) with err_first/err_last + clamp counts.
    """
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
# per-seed runner (loops over (V,n_ops) groups; SR trained per gamma on shared rollouts)
# ============================================================================
def _tune_wreach(mode: str, train_c, W_ops, E, M, dd, alpha) -> Tuple[float, float]:
    best_wr, best_acc = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        acc = run_selection_arm(mode, train_c, W_ops, E, M, dd, alpha, wr)[0].mean()
        if acc > best_acc:
            best_acc, best_wr = acc, wr
    return best_wr, float(best_acc)


def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M_by_gamma: Dict[float, torch.Tensor], train_by_d, test_by_d) -> Dict[str, Any]:
    """Tune on train, evaluate all arms (incl per-gamma gonogo) on test. One seed."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]
    M0 = M_by_gamma[BASELINE_GAMMA]  # any M works for M-independent arms; identity/none used

    # tune alpha (additive; SR-independent) on train
    best_alpha, best_add_train = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_arm("additive", train_c, W_ops, E, M0, dd, a, 0.0)[0].mean()
        if acc > best_add_train:
            best_add_train, best_alpha = acc, a

    # tune identity-reach CONTROL (SR-independent; steelman the anti-tautology foil)
    best_wr_ctrl, best_ctrl_train = _tune_wreach("gonogo_control", train_c, W_ops, E, M0,
                                                 dd, best_alpha)

    # SR-independent arm evals on TEST (paired base)
    v1_c, v1_tr = run_selection_arm("v1", test_c, W_ops, E, M0, dd, 0.0, 0.0)
    add_c, add_tr = run_selection_arm("additive", test_c, W_ops, E, M0, dd, best_alpha, 0.0)
    ctrl_c, ctrl_tr = run_selection_arm("gonogo_control", test_c, W_ops, E, M0, dd,
                                        best_alpha, best_wr_ctrl)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)

    arms: Dict[str, float] = {
        "v1_no_goal": float(v1_c.mean()),
        "additive_baseline": float(add_c.mean()),
        "cfrpe_control_identity": float(ctrl_c.mean()),
        "oracle": float(orc_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "v1_no_goal": hashlib.sha256(v1_tr.tobytes()).hexdigest()[:16],
        "additive_baseline": hashlib.sha256(add_tr.tobytes()).hexdigest()[:16],
        "cfrpe_control_identity": hashlib.sha256(ctrl_tr.tobytes()).hexdigest()[:16],
        "oracle": "oracle_true_seq",
    }

    # per-gamma gonogo (the horizon comparison)
    gamma_records: Dict[str, Any] = {}
    for gk in GAMMA_KEYS:
        g = gamma_of_key(gk)
        M = M_by_gamma[g]
        best_wr, best_go_train = _tune_wreach("gonogo", train_c, W_ops, E, M, dd, best_alpha)
        go_c, go_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr)
        rr_train = reach_rank_acc(train_c, W_ops, E, M, dd)
        rr_test = reach_rank_acc(test_c, W_ops, E, M, dd)
        rtc_test = reach_vs_targetcos_corr(test_c, W_ops, E, M, dd)
        paired = {
            "n_gonogo_only": int(((go_c) & (~add_c)).sum()),
            "n_additive_only": int(((add_c) & (~go_c)).sum()),
            "n_both": int((go_c & add_c).sum()),
            "n_neither": int(((~go_c) & (~add_c)).sum()),
            "n_test": int(len(go_c)),
            "n_gonogo_over_ctrl": int(((go_c) & (~ctrl_c)).sum()),
            "n_ctrl_over_gonogo": int(((ctrl_c) & (~go_c)).sum()),
        }
        arms["gonogo_" + gk] = float(go_c.mean())
        op_trace_hashes["gonogo_" + gk] = hashlib.sha256(go_tr.tobytes()).hexdigest()[:16]
        gamma_records[gk] = {
            "gamma": float(g),
            "acc": float(go_c.mean()),
            "best_w_reach": float(best_wr),
            "gonogo_train_acc": float(best_go_train),
            "reach_rank_train": float(rr_train),
            "reach_rank_test": float(rr_test),
            "reach_tcos_corr_test": float(rtc_test),
            "paired": paired,
        }

    return {
        "n_ops": n_ops, "V": V, "dd": dd,
        "arms": arms,
        "op_trace_hashes": op_trace_hashes,
        "best_alpha": float(best_alpha),
        "best_w_reach_ctrl": float(best_wr_ctrl),
        "additive_train_acc": float(best_add_train),
        "control_train_acc": float(best_ctrl_train),
        "reach_rank_chance": reach_rank_chance(n_ops),
        "gamma_records": gamma_records,
    }


def run_one_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    g = np.random.default_rng(seed)

    # group regimes by (V, n_ops) so SR / KB / E built once; M swept over gamma
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

        # exploration rollouts (shared across gammas -> controlled horizon comparison)
        max_len = max(depths_needed) + 2
        transitions = collect_rollout_transitions(
            adj, n_ops, V, rollout_count(V), max_len, g)

        M_by_gamma: Dict[float, torch.Tensor] = {}
        sr_diag_g: Dict[str, Any] = {}
        for gk in GAMMA_KEYS:
            gval = gamma_of_key(gk)
            sr_gen = torch.Generator(device=DEVICE)
            # SAME seed for all gammas -> identical minibatch draws (isolate gamma)
            sr_gen.manual_seed(int(seed) * 7919 + int(V) * 17 + int(n_ops) * 3)
            M, sr_diag = train_sr_transport(
                E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, gval, sr_gen)
            M_by_gamma[gval] = M
            sr_diag_g[gk] = sr_diag
            print("[seed=%d op%d V=%d %s] SR: err %s->%s M_norm=%.3f n_trans=%d clamp=%d"
                  % (seed, n_ops, V, gk, sr_diag["err_first"], sr_diag["err_last"],
                     sr_diag["final_M_norm"], sr_diag["n_transitions"],
                     sr_diag["n_clamped_steps"]), flush=True)
        sr_diag_by_group[group_key(n_ops, V)] = sr_diag_g

        for dd in depths_needed:
            rec = _eval_regime(n_ops, V, dd, E, W_ops, M_by_gamma, train_by_d, test_by_d)
            rec["sr_err_last_by_gamma"] = {gk: sr_diag_g[gk]["err_last"] for gk in GAMMA_KEYS}
            key = regime_key(n_ops, V, dd)
            regime_results[key] = rec
            a = rec["arms"]
            gk_str = " ".join(
                "%s=%.3f(rr=%.3f)" % (gk, rec["gamma_records"][gk]["acc"],
                                      rec["gamma_records"][gk]["reach_rank_test"])
                for gk in GAMMA_KEYS)
            print("[seed=%d %s] V1=%.3f ADD=%.3f CTRL=%.3f ORC=%.3f (a=%.2f) | %s"
                  % (seed, key, a["v1_no_goal"], a["additive_baseline"],
                     a["cfrpe_control_identity"], a["oracle"], rec["best_alpha"],
                     gk_str), flush=True)

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

    def _gr_col(rk, gk, field):
        return [float(per_seed[k]["regime_results"][rk]["gamma_records"][gk][field])
                for k in _present(rk)]

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
        ctrl = arm_means["cfrpe_control_identity"]
        orc = arm_means["oracle"]
        v1 = arm_means["v1_no_goal"]
        headroom = orc - add
        baseline_in_band = (BASELINE_IN_BAND_LO < add < BASELINE_IN_BAND_HI)
        rr_chance = reach_rank_chance(r["n_ops"])
        rr_min = rr_chance + HP_REACH_RANK_MARGIN

        gamma_stats: Dict[str, Any] = {}
        for gk in GAMMA_KEYS:
            go = arm_means["gonogo_" + gk]
            closure = ((go - add) / headroom) if headroom > 1e-6 else 0.0
            gonogo_lift = go - add
            dynamics_lift = go - ctrl
            gonogo_cv = arm_cvs["gonogo_" + gk]
            rr_test = _mean(_gr_col(rk, gk, "reach_rank_test"))
            rr_train = _mean(_gr_col(rk, gk, "reach_rank_train"))
            rtc = _mean(_gr_col(rk, gk, "reach_tcos_corr_test"))
            wr_vals = _gr_col(rk, gk, "best_w_reach")
            # pooled paired sign-test across seeds (gonogo[gk] vs additive)
            n_go_only = sum(int(per_seed[k]["regime_results"][rk]["gamma_records"][gk]
                                ["paired"]["n_gonogo_only"]) for k in present)
            n_add_only = sum(int(per_seed[k]["regime_results"][rk]["gamma_records"][gk]
                                 ["paired"]["n_additive_only"]) for k in present)
            n_disc = n_go_only + n_add_only
            sign_p = binom_two_sided_p(n_go_only, n_disc, 0.5) if n_disc > 0 else 1.0
            # arms-differ (META_RULE_AF): gonogo[gk] vs additive op-trace per seed, unless wr==0
            af_collision = False
            for k in present:
                rr = per_seed[k]["regime_results"][rk]
                grk = rr["gamma_records"][gk]
                if grk["best_w_reach"] > 1e-9:
                    if rr["op_trace_hashes"]["gonogo_" + gk] == \
                       rr["op_trace_hashes"]["additive_baseline"]:
                        af_collision = True
            all_wr_zero = all(abs(w) < 1e-9 for w in wr_vals) if wr_vals else True

            hp_ok = (baseline_in_band and r["dd"] == 6
                     and gk in DEEP_GAMMA_KEYS
                     and closure >= HP_CLOSURE_FLOOR
                     and (gonogo_cv < HP_CV_MAX or RUN_MODE != "full")
                     and rtc < HP_REACH_TARGETCOS_CORR_MAX
                     and dynamics_lift > HP_DYNAMICS_LIFT_MIN
                     and sign_p < HP_SIGN_TEST_P
                     and rr_test > rr_min
                     and gonogo_lift > HF_GONOGO_LIFT_CEIL
                     and orc >= ORACLE_RAIL_MIN
                     and not af_collision)

            gamma_stats[gk] = {
                "gamma": gamma_of_key(gk), "gonogo": go, "closure": float(closure),
                "gonogo_lift": float(gonogo_lift), "dynamics_lift": float(dynamics_lift),
                "gonogo_cv": float(gonogo_cv),
                "reach_rank_test": float(rr_test), "reach_rank_train": float(rr_train),
                "reach_tcos_corr_test": float(rtc),
                "sign_test_p": float(sign_p),
                "n_gonogo_only": int(n_go_only), "n_additive_only": int(n_add_only),
                "best_w_reach_per_seed": {present[i]: wr_vals[i] for i in range(len(wr_vals))},
                "all_w_reach_zero": bool(all_wr_zero),
                "af_collision": bool(af_collision),
                "is_deep": bool(gk in DEEP_GAMMA_KEYS),
                "hp_ok": bool(hp_ok),
            }

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "arm_means": arm_means, "arm_cvs": arm_cvs, "arm_stds": arm_stds,
            "additive": add, "control_identity": ctrl, "oracle": orc, "v1_no_goal": v1,
            "headroom": float(headroom),
            "baseline_in_band": bool(baseline_in_band),
            "reach_rank_chance": float(rr_chance), "reach_rank_min": float(rr_min),
            "oracle_rail_ok": bool(orc >= ORACLE_RAIL_MIN),
            "gamma": gamma_stats,
        }

    # ---- mechanism signal: reach_rank_test at d4 vs d6 per (V,n_ops) group per gamma ----
    reach_rank_by_group: Dict[str, Any] = {}
    for r in REGIMES:
        gkey = group_key(r["n_ops"], r["V"])
        reach_rank_by_group.setdefault(gkey, {"n_ops": r["n_ops"], "V": r["V"], "by_depth": {}})
        rk = regime_key(r["n_ops"], r["V"], r["dd"])
        if rk in per_regime:
            reach_rank_by_group[gkey]["by_depth"][str(r["dd"])] = {
                gk: per_regime[rk]["gamma"][gk]["reach_rank_test"] for gk in GAMMA_KEYS}
    # per-group reach_rank d4->d6 delta for baseline vs deepest gamma
    for gkey, gg in reach_rank_by_group.items():
        bd = gg["by_depth"]
        if "4" in bd and "6" in bd:
            gg["baseline_reach_rank_d4"] = bd["4"][BASELINE_GAMMA_KEY]
            gg["baseline_reach_rank_d6"] = bd["6"][BASELINE_GAMMA_KEY]
            gg["baseline_degradation_d4_to_d6"] = bd["4"][BASELINE_GAMMA_KEY] - bd["6"][BASELINE_GAMMA_KEY]
            if DEEP_GAMMA_KEYS:
                deepest = DEEP_GAMMA_KEYS[-1]
                gg["deep_gamma_key"] = deepest
                gg["deep_reach_rank_d4"] = bd["4"][deepest]
                gg["deep_reach_rank_d6"] = bd["6"][deepest]
                gg["deep_degradation_d4_to_d6"] = bd["4"][deepest] - bd["6"][deepest]
                gg["deep_minus_baseline_reach_rank_d6"] = bd["6"][deepest] - bd["6"][BASELINE_GAMMA_KEY]
                gg["deep_minus_baseline_reach_rank_d4"] = bd["4"][deepest] - bd["4"][BASELINE_GAMMA_KEY]

    # ---- fair-regime selection + verdict ----
    cardinality_ok = completed_units >= EXPECTED_N_UNITS
    d6_regimes = {rk: v for rk, v in per_regime.items() if v["dd"] == 6}
    fair_d6 = {rk: v for rk, v in d6_regimes.items() if v["baseline_in_band"]}

    # HP candidates: (rk, gk) over fair d6 with a DEEP gamma clearing the full bar
    hp_pairs = [(rk, gk) for rk, v in fair_d6.items() for gk in DEEP_GAMMA_KEYS
                if v["gamma"][gk]["hp_ok"]]

    def _closure_of(rk, gk):
        return per_regime[rk]["gamma"][gk]["closure"]

    best_hp = max(hp_pairs, key=lambda p: _closure_of(*p)) if hp_pairs else None
    # best fair d6 by max closure across ALL gammas (for reporting / MB path)
    fair_pairs = [(rk, gk) for rk in fair_d6 for gk in GAMMA_KEYS]
    best_fair = max(fair_pairs, key=lambda p: _closure_of(*p)) if fair_pairs else None

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not fair_d6:
        verdict = "INCONCLUSIVE_NO_FAIR_REGIME"
    elif best_hp is not None:
        verdict = "HARD_PASS"
    elif all(max(v["gamma"][gk]["gonogo_lift"] for gk in GAMMA_KEYS) <= HF_GONOGO_LIFT_CEIL
             for v in fair_d6.values()):
        verdict = "HARD_FAIL_FIX_CANT_EXTEND_PAST_D4"
    else:
        # helps at a fair d6 regime but no deeper-SR clears full HP bar
        rk_bf, gk_bf = best_fair
        vbf = per_regime[rk_bf]["gamma"][gk_bf]
        if vbf["closure"] >= HP_CLOSURE_FLOOR and not (
                vbf["dynamics_lift"] > HP_DYNAMICS_LIFT_MIN
                and vbf["reach_tcos_corr_test"] < HP_REACH_TARGETCOS_CORR_MAX):
            verdict = "MIDDLE_BAND_NOT_DYNAMICS_ATTRIBUTABLE"
        elif vbf["closure"] >= HP_CLOSURE_FLOOR and vbf["gonogo_cv"] >= HP_CV_MAX \
                and RUN_MODE == "full":
            verdict = "MIDDLE_BAND_CV_TOO_HIGH"
        elif gk_bf == BASELINE_GAMMA_KEY and vbf["closure"] >= HP_CLOSURE_FLOOR:
            verdict = "MIDDLE_BAND_EXTENDS_VIA_BRANCHING_NOT_HORIZON"
        else:
            verdict = "MIDDLE_BAND_HELPS_BELOW_25"

    # focus = best HP (rk,gk) else best fair else the n_ops=4 d6 diagnosis regime else regime0
    if best_hp is not None:
        focus_rk, focus_gk = best_hp
    elif best_fair is not None:
        focus_rk, focus_gk = best_fair
    else:
        diag_rk = regime_key(4, REGIMES[0]["V"], 6)
        focus_rk = diag_rk if diag_rk in per_regime else REGIME_KEYS[0]
        focus_gk = DEEP_GAMMA_KEYS[-1] if DEEP_GAMMA_KEYS else BASELINE_GAMMA_KEY
    fr = per_regime[focus_rk]
    fg = fr["gamma"][focus_gk]

    # horizon attribution at focus regime: is the DEEPER-HORIZON fix (not branching) the
    # lever? deep-SR must BEAT baseline-SR closure at the same fair regime by > the margin.
    horizon_attributable = fg["closure"] - fr["gamma"][BASELINE_GAMMA_KEY]["closure"]
    HORIZON_LEVER_MARGIN = 0.05
    horizon_is_the_lever = bool(focus_gk in DEEP_GAMMA_KEYS
                                and horizon_attributable > HORIZON_LEVER_MARGIN)
    # If HARD_PASS but the deeper-horizon fix did NOT beat baseline-SR, the extension is
    # attributable to reduced branching, NOT the horizon fix -- mark it LOUDLY so the verdict
    # cannot be misread as "the deeper-horizon fix is proven."
    if verdict == "HARD_PASS" and not horizon_is_the_lever:
        verdict = "HARD_PASS"  # keep contract verdict (control DOES extend to fair d6)
        _extend_marker = "[EXTENDS_VIA_BRANCHING_horizon_attributable=%.3f_NOT_the_lever]" % horizon_attributable
    elif verdict == "HARD_PASS":
        _extend_marker = "[HORIZON_IS_THE_LEVER_attributable=%.3f]" % horizon_attributable
    else:
        _extend_marker = ""

    in_band_summary = ",".join(
        "%s:add=%.3f%s" % (rk, per_regime[rk]["additive"],
                           "(FAIR)" if per_regime[rk]["baseline_in_band"] else "(unfair)")
        for rk in REGIME_KEYS)

    # compact mechanism-signal string for the diagnosis group (n_ops=4)
    diag_gkey = group_key(4, REGIMES[0]["V"])
    mech_str = ""
    if diag_gkey in reach_rank_by_group and "baseline_degradation_d4_to_d6" in reach_rank_by_group[diag_gkey]:
        gg = reach_rank_by_group[diag_gkey]
        mech_str = ("[%s] baseSR rr d4=%.3f d6=%.3f (degr=%.3f)" %
                    (diag_gkey, gg.get("baseline_reach_rank_d4", 0.0),
                     gg.get("baseline_reach_rank_d6", 0.0),
                     gg.get("baseline_degradation_d4_to_d6", 0.0)))
        if "deep_reach_rank_d6" in gg:
            mech_str += (" deepSR(%s) rr d4=%.3f d6=%.3f | deep-base@d6=%.3f" %
                         (gg["deep_gamma_key"], gg.get("deep_reach_rank_d4", 0.0),
                          gg.get("deep_reach_rank_d6", 0.0),
                          gg.get("deep_minus_baseline_reach_rank_d6", 0.0)))

    verdict_msg = (
        "%s %s| n_fair_d6=%d/%d focus=%s@%s | ADD=%.3f GONOGO=%.3f CTRL=%.3f ORACLE=%.3f | "
        "closure=%.3f gonogo_lift=%.3f dynamics_lift=%.3f horizon_attributable=%.3f "
        "horizon_is_the_lever=%s | baseline_in_band=%s cv=%.3f reach_tcos_corr=%.3f "
        "sign_p=%.4g reach_rank=%.3f (min=%.3f) oracle_rail=%s | MECH %s | "
        "per_regime=[%s] n_seeds=%d"
    ) % (
        verdict, (_extend_marker + " " if _extend_marker else ""),
        len(fair_d6), len(d6_regimes), focus_rk, focus_gk,
        fr["additive"], fg["gonogo"], fr["control_identity"], fr["oracle"],
        fg["closure"], fg["gonogo_lift"], fg["dynamics_lift"], horizon_attributable,
        horizon_is_the_lever,
        fr["baseline_in_band"], fg["gonogo_cv"], fg["reach_tcos_corr_test"],
        fg["sign_test_p"], fg["reach_rank_test"], fr["reach_rank_min"], fr["oracle_rail_ok"],
        mech_str, in_band_summary, len(keys),
    )

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_regime": per_regime,
        "reach_rank_by_group": reach_rank_by_group,
        "d6_regime_keys": list(d6_regimes.keys()),
        "fair_d6_regime_keys": list(fair_d6.keys()),
        "hp_pairs": [{"regime": rk, "gamma": gk, "closure": _closure_of(rk, gk)}
                     for rk, gk in hp_pairs],
        "focus_regime": focus_rk, "focus_gamma": focus_gk,
        "focus_closure": fg["closure"], "focus_gonogo_lift": fg["gonogo_lift"],
        "focus_baseline_in_band": fr["baseline_in_band"],
        "focus_reach_rank_test": fg["reach_rank_test"],
        "focus_gonogo_cv": fg["gonogo_cv"],
        "focus_reach_tcos_corr": fg["reach_tcos_corr_test"],
        "horizon_attributable_at_focus": float(horizon_attributable),
        "horizon_is_the_lever": bool(horizon_is_the_lever),
        "clears_25pct_headroom": bool(fg["closure"] >= HP_CLOSURE_FLOOR
                                      and fr["baseline_in_band"] and fr["dd"] == 6),
        "cv_gate_enforced": bool(RUN_MODE == "full"),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": int(completed_units),
        "cardinality_ok": bool(cardinality_ok),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gammas=%s" % (DEVICE, GAMMA_SWEEP), flush=True)
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

    # ST4 (MECHANISM-FIRES): trained reach ranks ON-PATH node above OFF-PATH for the goal.
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

    # ST7 (ANTI-TAUTOLOGY): identity-reach control is UNINFORMATIVE where trained M is.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    trained_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert trained_sep > control_sep + 0.05, (
        "ST7 ANTI-TAUTOLOGY FAIL: trained-sep=%.4f not clearly > control-sep=%.4f"
        % (trained_sep, control_sep))
    print("[selftest] ST7 anti-tautology: trained-sep=%.4f >> control-sep=%.4f OK"
          % (trained_sep, control_sep), flush=True)

    # ST9 (HORIZON MECHANISM -- THE FIX): on a long linear chain 0->1->..->6 with a FAR goal,
    #   a longer-horizon SR (higher gamma) yields a STRONGER reach to the distant goal than a
    #   short-horizon SR. This validates the load-bearing hypothesis of the whole cell.
    gen9 = torch.Generator(device=DEVICE); gen9.manual_seed(11)
    Vc, Nc = 8, 1024
    Ec = make_bipolar_E(Vc, Nc, gen9)
    lin = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]], dtype=np.int64)
    lin_trans = np.tile(lin, (60, 1))
    g_short_gen = torch.Generator(device=DEVICE); g_short_gen.manual_seed(5)
    g_long_gen = torch.Generator(device=DEVICE); g_long_gen.manual_seed(5)  # SAME draws -> isolate gamma
    M_short, _ = train_sr_transport(Ec, lin_trans, Nc, steps=1200, batch=16, base_lr=0.5,
                                    gamma=0.60, gen=g_short_gen)
    M_long, _ = train_sr_transport(Ec, lin_trans, Nc, steps=1200, batch=16, base_lr=0.5,
                                   gamma=0.95, gen=g_long_gen)
    far_goal = Ec[5:6]                    # goal 4 hops beyond node 1
    reach_short = float(reach_value(Ec[1:2], far_goal, M_short)[0])
    reach_long = float(reach_value(Ec[1:2], far_goal, M_long)[0])
    assert reach_long > reach_short, (
        "ST9 HORIZON FAIL: long-gamma reach-to-far-goal=%.4f !> short-gamma=%.4f "
        "(the deeper-horizon fix should strengthen the distant-goal signal)"
        % (reach_long, reach_short))
    print("[selftest] ST9 horizon: reach-to-far-goal long(g0.95)=%.4f > short(g0.60)=%.4f OK"
          % (reach_long, reach_short), flush=True)

    # ST5: full pipeline single-seed structural (regime + gamma sweep) + arms present
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_deeper")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST5 missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST5 missing arm %s" % arm
    for gk in GAMMA_KEYS:
        assert gk in r["regime_results"][rk0]["gamma_records"], "ST5 missing gamma %s" % gk
    orc = r["regime_results"][rk0]["arms"]["oracle"]
    assert orc >= 0.5, "ST5 oracle too low (%.3f) on toy self-test" % orc
    print("[selftest] ST5 pipeline OK regimes=%s gammas=%s oracle=%.3f"
          % (REGIME_KEYS, GAMMA_KEYS, orc), flush=True)

    # ST6: binomial p symmetric + bounded
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0, "ST6 binom p out of range"
    assert abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST6 not symmetric"
    print("[selftest] ST6 binom two-sided p(8/10)=%.4f OK" % p, flush=True)

    # ST8 (CLOSURE FORMULA): closure = (gonogo-additive)/(oracle-additive)
    go_, add_, orc_ = 0.653, 0.053, 0.962
    cl = (go_ - add_) / (orc_ - add_)
    assert abs(cl - 0.65934) < 1e-3, "ST8 closure formula off: %.5f" % cl
    print("[selftest] ST8 closure formula OK (v2 fair d4 closure=%.3f)" % cl, flush=True)

    # ST10 (VERDICT WIRING): synth per_seed with a FAIR d6 regime where deep-SR clears the
    #   bar -> HARD_PASS; and a floored-baseline case -> INCONCLUSIVE.
    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    """Feed hand-built per-seed dicts through aggregate_and_verdict to lock verdict wiring."""
    def _mk_regime(n_ops, V, dd, add, orc, ctrl, v1, gonogo_by_gk, rr_by_gk, wr=1.0):
        gr = {}
        for gk in GAMMA_KEYS:
            n_go_only = 50 if gonogo_by_gk[gk] > add + 0.1 else 1
            gr[gk] = {
                "gamma": gamma_of_key(gk), "acc": gonogo_by_gk[gk], "best_w_reach": wr,
                "gonogo_train_acc": gonogo_by_gk[gk], "reach_rank_train": rr_by_gk[gk],
                "reach_rank_test": rr_by_gk[gk], "reach_tcos_corr_test": -0.05,
                "paired": {"n_gonogo_only": n_go_only, "n_additive_only": 1, "n_both": 5,
                           "n_neither": 5, "n_test": 60, "n_gonogo_over_ctrl": n_go_only,
                           "n_ctrl_over_gonogo": 1},
            }
        arms = {"v1_no_goal": v1, "additive_baseline": add,
                "cfrpe_control_identity": ctrl, "oracle": orc}
        oth = {"v1_no_goal": "a", "additive_baseline": "b", "cfrpe_control_identity": "c",
               "oracle": "oracle_true_seq"}
        for gk in GAMMA_KEYS:
            arms["gonogo_" + gk] = gonogo_by_gk[gk]
            oth["gonogo_" + gk] = "go_" + gk
        return {"n_ops": n_ops, "V": V, "dd": dd, "arms": arms, "op_trace_hashes": oth,
                "best_alpha": 0.2, "best_w_reach_ctrl": 1.0, "additive_train_acc": add,
                "control_train_acc": ctrl, "reach_rank_chance": 1.0 / n_ops,
                "gamma_records": gr}

    # deep gamma (last key) high; baseline (first key) modest -> deep clears bar at fair d6
    deep = GAMMA_KEYS[-1]; base = BASELINE_GAMMA_KEY
    hi = {gk: (0.40 if gk == deep else 0.20) for gk in GAMMA_KEYS}
    rr_hi = {gk: (0.75 if gk == deep else 0.60) for gk in GAMMA_KEYS}
    # fair d6 at n_ops=2 (additive in band); build 3 seeds identical
    reg_fair = regime_key(2, 800, 6)
    reg_diag = regime_key(4, 1200, 6)
    lo = {gk: 0.05 for gk in GAMMA_KEYS}
    rr_lo = {gk: (0.52 if gk == deep else 0.50) for gk in GAMMA_KEYS}
    ps = {}
    for s in ["7", "17", "23"]:
        ps[s] = {"regime_results": {
            reg_fair: _mk_regime(2, 800, 6, add=0.10, orc=0.95, ctrl=0.11, v1=0.05,
                                 gonogo_by_gk=hi, rr_by_gk=rr_hi),
            reg_diag: _mk_regime(4, 1200, 6, add=0.01, orc=0.95, ctrl=0.02, v1=0.005,
                                 gonogo_by_gk=lo, rr_by_gk=rr_lo),
        }}
    # temporarily override REGIMES/ARMS-derived expectations for this synthetic check
    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)
    REGIMES = [{"n_ops": 2, "V": 800, "dd": 6}, {"n_ops": 4, "V": 1200, "dd": 6}]
    REGIME_KEYS = [reg_fair, reg_diag]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    try:
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "ST10 expected HARD_PASS got %s" % out["verdict"]
        # now floor the fair regime's baseline -> no fair d6 -> INCONCLUSIVE
        for s in ps:
            ps[s]["regime_results"][reg_fair]["arms"]["additive_baseline"] = 0.005
        out2 = aggregate_and_verdict(ps)
        assert out2["verdict"] == "INCONCLUSIVE_NO_FAIR_REGIME", \
            "ST10 expected INCONCLUSIVE got %s" % out2["verdict"]
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST10 verdict wiring OK (HARD_PASS on fair-d6 deep-SR; "
          "INCONCLUSIVE on floored baseline)", flush=True)


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

    print("[%s] mode=%s device=%s N=%d n_ops_set=%s seeds=%s gammas=%s regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS_SET, SEEDS, GAMMA_SWEEP,
             REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1-ST10 (cfrpe-TD shrink, adaptive LR, LR decay "
                               "monotone, Go/NoGo argmax, mechanism-fires reach, anti-tautology "
                               "control, HORIZON-fix reach mono, regime+gamma pipeline, binom, "
                               "closure formula, verdict wiring)",
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
