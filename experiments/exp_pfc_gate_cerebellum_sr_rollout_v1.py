"""pfc_gate_cerebellum_sr_rollout_v1 -- does a CEREBELLAR-STYLE anticipatory forward-model
(SR-rollout bias BEFORE committing) recover the PFC-BG gate's depth-4-to-depth-6 collapse,
and is the recovery specifically ANTICIPATORY (not just "any correction helps")?

WHY (Director/Research steer 2026-07-07, brain-component-driven-development "prove a consumer
BEFORE building" discipline; see
notes/research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md):
  The already-BUILT, HARD_PASS-at-depth-4 PFC-BG gate
  (MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json: V1200_d4 gonogo_lift=0.600,
  closure=0.661) DEGRADES with depth (V800:0.603->0.301; V1200:0.600->0.281;
  V2400:0.468->0.204->0.068 at d4/d5/d6). A prior smoke tested WIDENING the SR horizon
  (higher gamma) as the fix and found it is NOT the lever
  (MEASURED@data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json:
  horizon_attributable=-0.008). THIS cell tests a DIFFERENT, genuinely novel lever: does a
  MULTI-HOP-AHEAD SR-ROLLOUT (predict the successor state K virtual hops out, using the
  ALREADY-TRAINED SR transport M as a forward-dynamics operator) restore the gate's
  discriminating power at depth-6, and does it matter WHEN the rollout information is used
  (before committing = anticipatory/cerebellar-style, vs after committing = generic
  denoiser)? Fixed gamma=0.85 throughout (the horizon axis is NOT re-tested here -- already
  falsified as the lever; conflating it here would confound the new mechanism).

PRIOR-WORK CHECK (substrate-KB concept-query, 2026-07-07): top hit cosine=0.3643
(notes/research_gap1_multihop_5x_drill_2026-06-26.md N3 "CEREBELLAR FORWARD-MODEL
CORRECTION" -- a proposed SUPERVISED forward-model comparator, P_deflated=0.30, never
built). Second/third hits (MOSAIC, Stream H) explicitly DEFER cerebellum because "substrate
doesn't have ground truth per hop" for a supervised comparator. THIS cell resolves that
exact blocker by reusing the UNSUPERVISED TD-bootstrap-trained SR matrix M (verbatim from
exp_pfc_gate_cfrpe_trained_v2.py / exp_pfc_gate_cfrpe_deeper_regime_v1.py) as the rollout
operator, rather than training a new supervised comparator. Genuinely novel: first actual
build/test of any cerebellar-forward-model variant in this program (N3 was proposed, never
implemented; only unrelated exp_substrate_cerebellar_random_expansion_write_v1.py exists on
disk, a granule-cell random-expansion-coding mechanism).

MECHANISM (the ONLY new primitive is `rollout_forward`; NO new representational machinery):
  rollout_forward(state, M, E, k): forward-simulate k virtual hops via the EXISTING SR
  transport M (state @ M) each followed by the EXISTING cleanup_batched (project back onto
  the codebook manifold) -- a genuine multi-step lookahead ("hypothesized future state"),
  distinct from the existing one-step reach_value(cleaned, goal, M) read (which is a raw
  SR-bundle cosine, no intermediate cleanup/re-snap). K_ROLLOUT=2 fixed a priori
  (HYPOTHESIZED per "multi-hop-ahead" framing; NOT tuned against the outcome).

ARMS (paired -- share E, W_ops, M, and the SAME test chains per (regime,seed)):
  v1_no_goal              goal-blind manifold reference
  additive_baseline       static additive goal-bias, alpha tuned on train (SR-independent)
  cfrpe_control_identity  gonogo with reach:=target-cosine (M=identity); anti-tautology foil
  oracle                  applies the true op_seq (ceiling)
  no_correction           EXISTING mechanism: one-step SR reach (== v2/deeper_regime's
                          gonogo_g0.85), measured FRESH here (paired Gate-D positive control)
  feedback_only_reactive  decision = additive score ONLY (no SR at decision time); AFTER
                          committing, apply K-step rollout_forward as a POST-HOC state
                          correction feeding the next hop. Isolates "does ANY correction
                          help" from anticipation.
  gonogo_sr_rollout_anticipatory  decision score includes a K-step rollout_forward-projected
                          reach BEFORE committing (predict-then-bias). State fed to next hop
                          is the RAW chosen candidate (no post-hoc correction) -- isolates the
                          DECISION-TIME-BIAS property from post-hoc correction.

PRIMARY DISCRIMINATOR (matched-group op4 d4-vs-d6, best-controlled -- see prereg for full
refinement rationale vs the drill's literal FULL-scale-anchored absolute-number bands):
  gap = d4_lift[no_correction] - d6_lift[no_correction]     (the collapse, measured IN THIS RUN)
  recovered_frac[arm] = (d6_lift[arm] - d6_lift[no_correction]) / gap
  anticipatory_minus_reactive_d6 = d6_lift[anticipatory] - d6_lift[reactive]

CONTRACT (Director/Research 2026-07-07; refined per prereg -- relative not absolute, same
percentages/margins as the drill's literal bands):
  HARD_PASS : gap>0.02 AND recovered_frac[anticipatory]>=0.40 AND
              anticipatory_minus_reactive_d6>=0.10 AND cv[anticipatory@d6]<0.15 AND
              oracle@d6>=0.90 AND mechanism-fires AND no arms-differ collision.
  HARD_FAIL_NO_CEREBELLAR_CONSUMER : recovered_frac[anticipatory]<=0.05 OR
              anticipatory_minus_reactive_d6<=0.0 OR cv[anticipatory@d6]>=0.25.
  MIDDLE_BAND_PARTIAL_RECOVERY: real lift (>0.05) but recovered_frac<0.40.
  MIDDLE_BAND_MECHANISM_DOES_NOT_FIRE: rollout_reach_rank_acc <= chance+0.05 at d4.
  INCONCLUSIVE_GAP_TOO_SMALL_TO_MEASURE: gap<=0.02 at this scale (regime-miss).
  Reported regardless: rollout_reach_rank_acc (mechanism-fires probe), secondary FAIR-regime
  closure comparison (context, not gating).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (op-trace hash pairwise; exempt at w_reach==0)
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException in main)
# - crlb_n/a: no closed-form noise floor; reachability via in-run feasibility (gap measured
#   directly, not asserted)
# - baseline_in_band at smoke (META_RULE_AG; reused verbatim from deeper_regime's own grid)
# - discriminator survives scale: smoke matches deeper_regime's own matched-N/V grid
#   (discriminator PREVIEW, option C); caveat carried: cleanup-noise-limited at N=2048
# - HARD_PASS strictly above floor (recovered_frac>=0.40, not >=0.35-with-rounding)
# - HP_SCOPE: HP gates apply to gonogo_sr_rollout_anticipatory vs no_correction/
#   feedback_only_reactive at the matched op4 group; oracle_rail (>=0.90) applies to ORACLE
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(7) * n_seeds * n_regimes
# - per-unit failure-class instrumentation (no bare except; fatal-flag on per-seed crash)
# - calibration_check: default_ok_for_this_regime (K_ROLLOUT=2 fixed a priori, not tuned)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in prereg + docstring

Compute architecture: (a) batched-GPU-capable, CPU-first (smoke local; FULL remote_cpu_queue
per RESOURCE RULES -- remote compute only for FULLs). SR-TD training (1 gamma, no sweep),
operator application, cleanup, rollout are batched matmuls, device-agnostic. Chains batched;
within-chain hops AND rollout's K virtual hops are genuinely sequential (real dependency).
Storage strategy: sharded (each op its own W matrix; M a learned value operator, not an item
store). No bundled store.
progress_logging: print_flush_true (line-buffered stdout + flush=True + per-seed heartbeat;
FULL timeout_s >= 1800).

Author: exp_dev (Sonnet 5, agent-spawn) 2026-07-07
Prereg: d:/AI/hd-instrument/preregs/2026-07-07_pfc_gate_cerebellum_sr_rollout_v1.md
Cites:
  data/exp_pfc_gate_cfrpe_trained_v2/metrics.json (HARD_PASS d4; degrades with depth)
  data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json (horizon NOT the lever)
  experiments/exp_pfc_gate_cfrpe_deeper_regime_v1.py (harness reused verbatim: E/W_ops/M/
    train_sr_transport/cleanup_batched/chains -- the ONLY new code is rollout_forward + the
    2 new arm runners + the refined verdict logic)
  notes/research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md
    (the drill: 3-arm spec + bands + consumer evidence)
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

ANCHOR_NAME = "pfc_gate_cerebellum_sr_rollout_v1"

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
HP_RECOVERED_FRAC_FLOOR = 0.40
HP_ANTIC_MINUS_REACT_MARGIN = 0.10
HP_CV_MAX = 0.15
HF_RECOVERED_FRAC_CEIL = 0.05
HF_ANTIC_MINUS_REACT_MIN = 0.0
HF_CV_MIN = 0.25
GAP_MIN_MEASURABLE = 0.02
ORACLE_RAIL_MIN = 0.90
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.95
MECH_FIRES_MARGIN = 0.05
MIDDLE_BAND_LIFT_FLOOR = 0.05

K_ROLLOUT = 2                       # fixed a priori (HYPOTHESIZED; NOT tuned against outcome)
BASELINE_GAMMA = 0.85               # fixed; horizon axis already tested + rejected as lever

DENSITY = 0.21
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0
LR_DECAY_END = 0.2

ALPHA_SWEEP = [0.1, 0.2, 0.5]
W_REACH_SWEEP = [0.0, 0.5, 1.0, 2.0]

# --------------------------- config (selftest / smoke / full) --------------------
if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    REGIMES = [{"n_ops": 4, "V": 40, "dd": 4}, {"n_ops": 4, "V": 40, "dd": 6}]
    N_TRAIN_CHAINS = 12
    N_TEST_CHAINS = 8
    SR_STEPS = 120
    SR_BATCH = 32
    SR_LR = 0.5
    ROLLOUT_PER_V = 20
elif RUN_MODE == "smoke":
    # IDENTICAL grid to exp_pfc_gate_cfrpe_deeper_regime_v1's own smoke (per drill's
    # instruction to reuse the existing smoke grid). 3 seeds.
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    REGIMES = [{"n_ops": 4, "V": 300, "dd": 4},   # matched-group d4 reference
               {"n_ops": 4, "V": 300, "dd": 6},   # matched-group d6 (PRIMARY diagnosis)
               {"n_ops": 2, "V": 300, "dd": 6}]   # FAIR-in-band d6 (SECONDARY reporting)
    N_TRAIN_CHAINS = 48
    N_TEST_CHAINS = 48
    SR_STEPS = 300
    SR_BATCH = 64
    SR_LR = 0.5
    ROLLOUT_PER_V = 8
else:  # full
    # IDENTICAL grid to exp_pfc_gate_cfrpe_deeper_regime_v1's own staged FULL config.
    # Single gamma (no 3-gamma sweep) -> cheaper per-seed than deeper_regime's FULL despite
    # the added rollout overhead on 2 new arms.
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    REGIMES = [{"n_ops": 4, "V": 1200, "dd": 4},
               {"n_ops": 4, "V": 1200, "dd": 6},
               {"n_ops": 2, "V": 800, "dd": 4},
               {"n_ops": 2, "V": 800, "dd": 6},
               {"n_ops": 2, "V": 1200, "dd": 4},
               {"n_ops": 2, "V": 1200, "dd": 6}]
    N_TRAIN_CHAINS = 300
    N_TEST_CHAINS = 240
    SR_STEPS = 8000
    SR_BATCH = 256
    SR_LR = 0.5
    ROLLOUT_PER_V = 50

ROLLOUT_CAP = 4000 if RUN_MODE == "smoke" else 200000

ARMS = ["v1_no_goal", "additive_baseline", "cfrpe_control_identity", "oracle",
        "no_correction", "feedback_only_reactive", "gonogo_sr_rollout_anticipatory"]
N_OPS_SET = sorted(set(r["n_ops"] for r in REGIMES))


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
    "ANCHOR=%s,N=%d,n_ops_set=%s,seeds=%s,gamma=%.2f,k_rollout=%d,regimes=%s,density=%.3f,"
    "sr_steps=%d,sr_batch=%d,rollout_per_V=%d,lr=%.2f,lr_decay_end=%.2f,alphas=%s,w_reach=%s,"
    "n_train_chains=%d,n_test_chains=%d,mode=%s,device=%s,expected_n=%d,"
    "HP_recovered_frac>=%.2f,anticipatory_beats_reactive>=%.2f,cv<%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_OPS_SET, SEEDS, BASELINE_GAMMA, K_ROLLOUT, REGIME_KEYS, DENSITY,
    SR_STEPS, SR_BATCH, ROLLOUT_PER_V, SR_LR, LR_DECAY_END, ALPHA_SWEEP, W_REACH_SWEEP,
    N_TRAIN_CHAINS, N_TEST_CHAINS, RUN_MODE, str(DEVICE), EXPECTED_N_UNITS,
    HP_RECOVERED_FRAC_FLOOR, HP_ANTIC_MINUS_REACT_MARGIN, HP_CV_MAX,
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
# primitives (torch, batched, device-agnostic) -- reused VERBATIM from v2/deeper_regime
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
# KB + chains (exact-length paths; train and test disjoint chain sets) -- verbatim
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
# cfrpe-trained SR transport M (TD(0)) -- reused VERBATIM (gamma fixed this cell)
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
    """cos(E[cand] @ M, E[goal]) per row -- one-step learned-dynamics reach (existing)."""
    fwd = _norm_rows(cand_E @ M)
    return (fwd * _norm_rows(goal_E)).sum(dim=1)


def reach_control_targetcos(cand_E: torch.Tensor, goal_E: torch.Tensor) -> torch.Tensor:
    """Anti-tautology control: reach with M:=identity == raw target-cosine."""
    return (_norm_rows(cand_E) * _norm_rows(goal_E)).sum(dim=1)


# ============================================================================
# NEW PRIMITIVE: rollout_forward -- the ONLY new representational machinery in this cell.
# Composes two EXISTING primitives (matmul against M; cleanup_batched) K times: a genuine
# multi-step lookahead ("hypothesized future state"), distinct from the one-step reach_value
# raw-SR-bundle-cosine read above.
# ============================================================================
def rollout_forward(state: torch.Tensor, M: torch.Tensor, E: torch.Tensor, k: int
                    ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Forward-simulate k virtual hops via M, re-cleaning onto the codebook manifold after
    each step. state: [B,n] (need not already be a cleaned E-row). Returns (final_idx [B],
    final_cleaned_E [B,n]) after k virtual hops. k=0 degenerates to cleaning up `state` as-is
    (used only in self-test edge cases)."""
    cur = state
    idx = None
    for _ in range(max(0, k)):
        raw = cur @ M
        idx, cur, _ = cleanup_batched(raw, E)
    if idx is None:
        idx, cur, _ = cleanup_batched(cur, E)
    return idx, cur


# ============================================================================
# arms (batched across chains; hops sequential within a chain -- genuine dependency)
# ============================================================================
def _chain_tensors(chains: List[Tuple[int, List[int], int]]
                   ) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    starts = torch.tensor([c[0] for c in chains], dtype=torch.long, device=DEVICE)
    targets = torch.tensor([c[2] for c in chains], dtype=torch.long, device=DEVICE)
    op_seqs = np.asarray([c[1] for c in chains], dtype=np.int64)
    return starts, targets, op_seqs


def run_selection_arm(mode: str, chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                      M: torch.Tensor, depth: int,
                      alpha: float, w_reach: float
                      ) -> Tuple[np.ndarray, np.ndarray]:
    """Baseline/no_correction arm runner (verbatim structure from v2/deeper_regime).
    mode in {v1, additive, gonogo, gonogo_control}. gonogo == no_correction (one-step reach)."""
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


def run_selection_arm_anticipatory(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                                   M: torch.Tensor, depth: int, alpha: float,
                                   w_reach: float, k_rollout: int
                                   ) -> Tuple[np.ndarray, np.ndarray]:
    """CEREBELLAR-ANTICIPATORY arm: score uses a K-STEP SR-ROLLOUT reach (forward-simulate
    k virtual hops from the candidate's cleaned state via M+cleanup, THEN cosine to goal) to
    bias the argmax BEFORE committing. State fed to next hop is the RAW (uncorrected)
    candidate -- isolates the decision-time-bias property from post-hoc correction (see
    run_selection_arm_reactive)."""
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
            _, rolled = rollout_forward(cleaned, M, E, k_rollout)
            reach_antic = (_norm_rows(rolled) * _norm_rows(goal_E)).sum(dim=1)
            sc = w_manifold * manifold + alpha * goal_sim + w_reach * reach_antic
            scores[:, op] = sc
        chosen = scores.argmax(dim=1)
        op_trace[:, hop] = chosen.detach().cpu().numpy()
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, chosen]
        state = E[new_idx]                  # RAW candidate; no post-hoc correction
        final_idx = new_idx
    correct = (final_idx == targets).detach().cpu().numpy()
    return correct.astype(bool), op_trace


def run_selection_arm_reactive(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                               M: torch.Tensor, depth: int, alpha: float, k_rollout: int
                               ) -> Tuple[np.ndarray, np.ndarray]:
    """FEEDBACK-ONLY REACTIVE control: choose each hop via the ADDITIVE score alone (NO SR
    signal at decision time -- identical selection rule to additive_baseline), THEN apply the
    SAME K-step rollout_forward as a POST-HOC state correction (denoise the landed state
    before it feeds the next hop / final correctness check). Isolates whether "any
    correction" (not specifically anticipation) accounts for the benefit."""
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
            sc = alpha * goal_sim + w_manifold * manifold      # NO SR signal at decision time
            scores[:, op] = sc
        chosen = scores.argmax(dim=1)
        op_trace[:, hop] = chosen.detach().cpu().numpy()
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx[row, chosen]
        landed = E[new_idx]
        corrected_idx, corrected_state = rollout_forward(landed, M, E, k_rollout)  # post-hoc
        state = corrected_state
        final_idx = corrected_idx
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
    """One-step mechanism-fires probe (existing): along the TRUE trajectory, does argmax_op
    one-step reach == the true op? Chance = 1/n_ops."""
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


def rollout_reach_rank_acc(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                           M: torch.Tensor, depth: int, k_rollout: int) -> float:
    """Mechanism-fires probe for the ANTICIPATORY signal specifically: along the TRUE
    trajectory, does argmax_op(K-step-rollout reach) == the true op? Chance = 1/n_ops."""
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
            _, rolled = rollout_forward(cleaned, M, E, k_rollout)
            reach_scores[:, op] = (_norm_rows(rolled) * _norm_rows(goal_E)).sum(dim=1)
        pred_op = reach_scores.argmax(dim=1)
        true_op = op_seq_t[:, hop]
        hits += int((pred_op == true_op).sum().item())
        total += n_chains
        row = torch.arange(n_chains, device=DEVICE)
        new_idx = cand_idx_all[row, true_op]
        state = E[new_idx]
    return float(hits) / float(max(1, total))


def rollout_reach_vs_targetcos_corr(chains, W_ops: List[torch.Tensor], E: torch.Tensor,
                                    M: torch.Tensor, depth: int, k_rollout: int) -> float:
    """Anti-tautology guard for the rollout signal: Pearson corr between K-step-rollout
    reach and raw target-cosine across all candidate ops along the true trajectory."""
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
            _, rolled = rollout_forward(cleaned, M, E, k_rollout)
            reach_vals.extend((_norm_rows(rolled) * _norm_rows(goal_E)).sum(dim=1)
                               .detach().cpu().tolist())
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


def _hash(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


def _mean(xs: List[float]) -> float:
    return float(np.mean(xs)) if xs else 0.0


# ============================================================================
# per-seed runner (loops over (V,n_ops) groups; single gamma=0.85 SR per group)
# ============================================================================
def _tune_wreach_mode(mode: str, train_c, W_ops, E, M, dd, alpha,
                      k_rollout: int = 0) -> Tuple[float, float]:
    best_wr, best_acc = W_REACH_SWEEP[0], -1.0
    for wr in W_REACH_SWEEP:
        if mode == "anticipatory":
            acc = run_selection_arm_anticipatory(train_c, W_ops, E, M, dd, alpha, wr,
                                                 k_rollout)[0].mean()
        else:
            acc = run_selection_arm(mode, train_c, W_ops, E, M, dd, alpha, wr)[0].mean()
        if acc > best_acc:
            best_acc, best_wr = acc, wr
    return best_wr, float(best_acc)


def _eval_regime(n_ops: int, V: int, dd: int, E: torch.Tensor, W_ops: List[torch.Tensor],
                 M: torch.Tensor, train_by_d, test_by_d) -> Dict[str, Any]:
    """Tune on train, evaluate all 7 arms on test. One seed."""
    train_c = train_by_d[dd]
    test_c = test_by_d[dd]

    best_alpha, best_add_train = ALPHA_SWEEP[0], -1.0
    for a in ALPHA_SWEEP:
        acc = run_selection_arm("additive", train_c, W_ops, E, M, dd, a, 0.0)[0].mean()
        if acc > best_add_train:
            best_add_train, best_alpha = acc, a

    best_wr_ctrl, best_ctrl_train = _tune_wreach_mode("gonogo_control", train_c, W_ops, E, M,
                                                      dd, best_alpha)
    best_wr_nc, best_nc_train = _tune_wreach_mode("gonogo", train_c, W_ops, E, M, dd,
                                                  best_alpha)
    best_wr_ant, best_ant_train = _tune_wreach_mode("anticipatory", train_c, W_ops, E, M, dd,
                                                    best_alpha, K_ROLLOUT)

    v1_c, v1_tr = run_selection_arm("v1", test_c, W_ops, E, M, dd, 0.0, 0.0)
    add_c, add_tr = run_selection_arm("additive", test_c, W_ops, E, M, dd, best_alpha, 0.0)
    ctrl_c, ctrl_tr = run_selection_arm("gonogo_control", test_c, W_ops, E, M, dd, best_alpha,
                                        best_wr_ctrl)
    orc_c = run_oracle_arm(test_c, W_ops, E, dd)
    nc_c, nc_tr = run_selection_arm("gonogo", test_c, W_ops, E, M, dd, best_alpha, best_wr_nc)
    ant_c, ant_tr = run_selection_arm_anticipatory(test_c, W_ops, E, M, dd, best_alpha,
                                                   best_wr_ant, K_ROLLOUT)
    react_c, react_tr = run_selection_arm_reactive(test_c, W_ops, E, M, dd, best_alpha,
                                                   K_ROLLOUT)

    arms: Dict[str, float] = {
        "v1_no_goal": float(v1_c.mean()),
        "additive_baseline": float(add_c.mean()),
        "cfrpe_control_identity": float(ctrl_c.mean()),
        "oracle": float(orc_c.mean()),
        "no_correction": float(nc_c.mean()),
        "feedback_only_reactive": float(react_c.mean()),
        "gonogo_sr_rollout_anticipatory": float(ant_c.mean()),
    }
    op_trace_hashes: Dict[str, str] = {
        "v1_no_goal": _hash(v1_tr), "additive_baseline": _hash(add_tr),
        "cfrpe_control_identity": _hash(ctrl_tr), "oracle": "oracle_true_seq",
        "no_correction": _hash(nc_tr), "feedback_only_reactive": _hash(react_tr),
        "gonogo_sr_rollout_anticipatory": _hash(ant_tr),
    }

    rr_1step_test = reach_rank_acc(test_c, W_ops, E, M, dd)
    rr_rollout_train = rollout_reach_rank_acc(train_c, W_ops, E, M, dd, K_ROLLOUT)
    rr_rollout_test = rollout_reach_rank_acc(test_c, W_ops, E, M, dd, K_ROLLOUT)
    rtc_rollout_test = rollout_reach_vs_targetcos_corr(test_c, W_ops, E, M, dd, K_ROLLOUT)

    paired_ant_vs_nc = {
        "n_ant_only": int(((ant_c) & (~nc_c)).sum()),
        "n_nc_only": int(((nc_c) & (~ant_c)).sum()),
    }
    paired_ant_vs_react = {
        "n_ant_only": int(((ant_c) & (~react_c)).sum()),
        "n_react_only": int(((react_c) & (~ant_c)).sum()),
    }

    return {
        "n_ops": n_ops, "V": V, "dd": dd,
        "arms": arms, "op_trace_hashes": op_trace_hashes,
        "best_alpha": float(best_alpha),
        "best_w_reach_ctrl": float(best_wr_ctrl),
        "best_w_reach_nc": float(best_wr_nc),
        "best_w_reach_ant": float(best_wr_ant),
        "additive_train_acc": float(best_add_train),
        "reach_rank_chance": reach_rank_chance(n_ops),
        "rr_1step_test": float(rr_1step_test),
        "rr_rollout_train": float(rr_rollout_train),
        "rr_rollout_test": float(rr_rollout_test),
        "rtc_rollout_test": float(rtc_rollout_test),
        "paired_ant_vs_nc": paired_ant_vs_nc,
        "paired_ant_vs_react": paired_ant_vs_react,
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
            E, transitions, N_DIM, SR_STEPS, SR_BATCH, SR_LR, BASELINE_GAMMA, sr_gen)
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
            print("[seed=%d %s] V1=%.3f ADD=%.3f CTRL=%.3f ORC=%.3f NC=%.3f REACT=%.3f "
                  "ANT=%.3f (a=%.2f wr_nc=%.1f wr_ant=%.1f rr_roll=%.3f)"
                  % (seed, key, a["v1_no_goal"], a["additive_baseline"],
                     a["cfrpe_control_identity"], a["oracle"], a["no_correction"],
                     a["feedback_only_reactive"], a["gonogo_sr_rollout_anticipatory"],
                     rec["best_alpha"], rec["best_w_reach_nc"], rec["best_w_reach_ant"],
                     rec["rr_rollout_test"]), flush=True)

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
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_regime": {}}
    keys = sorted(per_seed.keys(), key=lambda s: int(s) if str(s).isdigit() else 0)

    def _present(rk):
        return [k for k in keys if rk in per_seed[k].get("regime_results", {})]

    def _arm_col(rk, arm):
        return [float(per_seed[k]["regime_results"][rk]["arms"][arm]) for k in _present(rk)]

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

        test_arms = ["no_correction", "feedback_only_reactive", "gonogo_sr_rollout_anticipatory"]
        gonogo_lift = {arm: arm_means[arm] - add for arm in test_arms}
        closure = {arm: ((arm_means[arm] - add) / headroom) if headroom > 1e-6 else 0.0
                   for arm in test_arms}
        dynamics_lift = {arm: arm_means[arm] - ctrl for arm in test_arms}

        rr_rollout_test = _mean([float(per_seed[k]["regime_results"][rk]["rr_rollout_test"])
                                  for k in present]) if present else 0.0
        rtc_rollout_test = _mean([float(per_seed[k]["regime_results"][rk]["rtc_rollout_test"])
                                   for k in present]) if present else 0.0
        rr_chance = reach_rank_chance(r["n_ops"])

        af_collision_pairs: List[str] = []
        for k in present:
            oth = per_seed[k]["regime_results"][rk]["op_trace_hashes"]
            wr_nc = per_seed[k]["regime_results"][rk]["best_w_reach_nc"]
            wr_ant = per_seed[k]["regime_results"][rk]["best_w_reach_ant"]
            pairs = [("no_correction", "additive_baseline", wr_nc > 1e-9),
                     ("gonogo_sr_rollout_anticipatory", "additive_baseline", wr_ant > 1e-9),
                     ("gonogo_sr_rollout_anticipatory", "feedback_only_reactive", True),
                     ("no_correction", "gonogo_sr_rollout_anticipatory", True)]
            for a1, a2, must_differ in pairs:
                if must_differ and oth[a1] == oth[a2]:
                    af_collision_pairs.append("%s:%s==%s" % (k, a1, a2))

        per_regime[rk] = {
            "n_ops": r["n_ops"], "V": r["V"], "dd": r["dd"], "n_seeds": n_present,
            "arm_means": arm_means, "arm_cvs": arm_cvs, "arm_stds": arm_stds,
            "additive": add, "control_identity": ctrl, "oracle": orc, "v1_no_goal": v1,
            "headroom": float(headroom), "baseline_in_band": bool(baseline_in_band),
            "gonogo_lift": gonogo_lift, "closure": closure, "dynamics_lift": dynamics_lift,
            "rr_rollout_test": float(rr_rollout_test), "rtc_rollout_test": float(rtc_rollout_test),
            "reach_rank_chance": float(rr_chance),
            "oracle_rail_ok": bool(orc >= ORACLE_RAIL_MIN),
            "af_collision_pairs": af_collision_pairs,
        }

    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    # ---- PRIMARY leg: matched-group (op4, group's own V) d4-vs-d6 gap-recovery ----
    diag_group_V = REGIMES[0]["V"]
    rk_d4 = regime_key(4, diag_group_V, 4)
    rk_d6 = regime_key(4, diag_group_V, 6)
    primary_available = rk_d4 in per_regime and rk_d6 in per_regime
    primary: Dict[str, Any] = {}
    if primary_available:
        d4 = per_regime[rk_d4]; d6 = per_regime[rk_d6]
        d4_lift_nc = d4["gonogo_lift"]["no_correction"]
        d6_lift_nc = d6["gonogo_lift"]["no_correction"]
        d6_lift_react = d6["gonogo_lift"]["feedback_only_reactive"]
        d6_lift_ant = d6["gonogo_lift"]["gonogo_sr_rollout_anticipatory"]
        gap = d4_lift_nc - d6_lift_nc
        gap_measurable = gap > GAP_MIN_MEASURABLE
        recovered_frac_ant = ((d6_lift_ant - d6_lift_nc) / gap) if gap_measurable else 0.0
        recovered_frac_react = ((d6_lift_react - d6_lift_nc) / gap) if gap_measurable else 0.0
        ant_minus_react_d6 = d6_lift_ant - d6_lift_react
        cv_ant_d6 = per_regime[rk_d6]["arm_cvs"]["gonogo_sr_rollout_anticipatory"]
        primary = {
            "rk_d4": rk_d4, "rk_d6": rk_d6,
            "d4_lift_no_correction": float(d4_lift_nc),
            "d6_lift_no_correction": float(d6_lift_nc),
            "d6_lift_feedback_only_reactive": float(d6_lift_react),
            "d6_lift_gonogo_sr_rollout_anticipatory": float(d6_lift_ant),
            "gap": float(gap), "gap_measurable": bool(gap_measurable),
            "recovered_frac_anticipatory": float(recovered_frac_ant),
            "recovered_frac_reactive": float(recovered_frac_react),
            "anticipatory_minus_reactive_d6": float(ant_minus_react_d6),
            "cv_anticipatory_d6": float(cv_ant_d6),
            "oracle_d6": float(d6["oracle"]),
        }

    # ---- SECONDARY leg: FAIR in-band d6 regime (reporting; not gating) ----
    fair_d6_regimes = {rk: v for rk, v in per_regime.items()
                       if v["dd"] == 6 and v["baseline_in_band"]}
    secondary: Dict[str, Any] = {}
    if fair_d6_regimes:
        best_rk = max(fair_d6_regimes.keys(),
                     key=lambda rk: per_regime[rk]["closure"]["gonogo_sr_rollout_anticipatory"])
        v = per_regime[best_rk]
        secondary = {
            "rk": best_rk,
            "closure_no_correction": v["closure"]["no_correction"],
            "closure_feedback_only_reactive": v["closure"]["feedback_only_reactive"],
            "closure_gonogo_sr_rollout_anticipatory": v["closure"]["gonogo_sr_rollout_anticipatory"],
        }

    mech_fires = False
    if primary_available:
        rr_d4 = per_regime[rk_d4]["rr_rollout_test"]
        chance_d4 = per_regime[rk_d4]["reach_rank_chance"]
        mech_fires = rr_d4 > (chance_d4 + MECH_FIRES_MARGIN)

    af_collision_any = any(per_regime[rk]["af_collision_pairs"] for rk in per_regime)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not primary_available:
        verdict = "INCONCLUSIVE_NO_MATCHED_GROUP_REGIME"
    elif not primary["gap_measurable"]:
        verdict = "INCONCLUSIVE_GAP_TOO_SMALL_TO_MEASURE"
    elif not mech_fires:
        verdict = "MIDDLE_BAND_MECHANISM_DOES_NOT_FIRE"
    elif af_collision_any:
        verdict = "MIDDLE_BAND_ARM_COLLISION"
    elif (primary["recovered_frac_anticipatory"] >= HP_RECOVERED_FRAC_FLOOR
          and primary["anticipatory_minus_reactive_d6"] >= HP_ANTIC_MINUS_REACT_MARGIN
          and primary["cv_anticipatory_d6"] < HP_CV_MAX
          and primary["oracle_d6"] >= ORACLE_RAIL_MIN):
        verdict = "HARD_PASS"
    elif (primary["recovered_frac_anticipatory"] <= HF_RECOVERED_FRAC_CEIL
          or primary["anticipatory_minus_reactive_d6"] <= HF_ANTIC_MINUS_REACT_MIN
          or primary["cv_anticipatory_d6"] >= HF_CV_MIN):
        verdict = "HARD_FAIL_NO_CEREBELLAR_CONSUMER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RECOVERY"

    verdict_msg = (
        "%s | primary=%s->%s gap=%.3f(measurable=%s) | "
        "d6_lift NC=%.3f REACT=%.3f ANT=%.3f | recovered_frac ANT=%.3f REACT=%.3f | "
        "ant_minus_react=%.3f cv_ant=%.3f oracle_d6=%.3f | mech_fires=%s "
        "(rr_rollout=%.3f/chance=%.3f) | af_collision=%s | secondary_fair=%s | "
        "cardinality=%d/%d n_seeds=%d"
    ) % (
        verdict, rk_d4 if primary_available else "N/A", rk_d6 if primary_available else "N/A",
        primary.get("gap", 0.0), primary.get("gap_measurable", False),
        primary.get("d6_lift_no_correction", 0.0),
        primary.get("d6_lift_feedback_only_reactive", 0.0),
        primary.get("d6_lift_gonogo_sr_rollout_anticipatory", 0.0),
        primary.get("recovered_frac_anticipatory", 0.0),
        primary.get("recovered_frac_reactive", 0.0),
        primary.get("anticipatory_minus_reactive_d6", 0.0),
        primary.get("cv_anticipatory_d6", 0.0), primary.get("oracle_d6", 0.0),
        mech_fires, per_regime.get(rk_d4, {}).get("rr_rollout_test", 0.0),
        per_regime.get(rk_d4, {}).get("reach_rank_chance", 0.0),
        af_collision_any, secondary.get("rk", "NONE"),
        completed_units, EXPECTED_N_UNITS, len(keys),
    )

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_regime": per_regime, "primary": primary, "secondary": secondary,
        "mech_fires": bool(mech_fires), "af_collision_any": bool(af_collision_any),
        "cardinality_ok": bool(cardinality_ok),
        "expected_n_units": EXPECTED_N_UNITS, "completed_units": int(completed_units),
        "n_seeds_complete": len(keys),
    }


# ============================================================================
# self-test (formula correctness; MANDATORY pre-dispatch)
# ============================================================================
def _selftest() -> int:
    print("[selftest] device=%s gamma=%.2f k_rollout=%d" % (DEVICE, BASELINE_GAMMA, K_ROLLOUT),
          flush=True)

    # ST1: cfrpe SR-TD delta-rule shrinks the TD prediction error over steps (verbatim check)
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

    # ST3: Go/NoGo competition selects argmax Go-value
    scores = torch.tensor([[0.1, 0.9, 0.3, 0.2]], device=DEVICE)
    assert int(scores.argmax(dim=1)[0]) == 1, "ST3 argmax competition wrong"
    print("[selftest] ST3 Go/NoGo argmax competition OK", flush=True)

    # ST_ROLLOUT (MECHANISM-FIRES): a K=2-step rollout from an ON-PATH node (2 hops from
    # goal) should predict the goal better than from an OFF-PATH node (2 hops from a
    # DIFFERENT endpoint). Toy fixture identical to v2/deeper_regime's ST4.
    gen4 = torch.Generator(device=DEVICE); gen4.manual_seed(3)
    Vt, Nt = 8, 512
    Et = make_bipolar_E(Vt, Nt, gen4)
    chainA = np.array([[0, 1], [1, 2], [2, 3]], dtype=np.int64)   # goal reached at node 3
    chainB = np.array([[0, 4], [4, 5], [5, 6]], dtype=np.int64)   # off-path, ends at node 6
    toy_trans = np.concatenate([np.tile(chainA, (40, 1)), np.tile(chainB, (40, 1))], axis=0)
    Mt, _ = train_sr_transport(Et, toy_trans, Nt, steps=800, batch=16, base_lr=0.5,
                               gamma=0.8, gen=gen4)
    goal = Et[3:4]
    _, rolled_on = rollout_forward(Et[1:2], Mt, Et, K_ROLLOUT)     # node 1 -> 2 hops -> node 3
    _, rolled_off = rollout_forward(Et[4:5], Mt, Et, K_ROLLOUT)    # node 4 -> 2 hops -> node 6
    reach_on = float((_norm_rows(rolled_on) * _norm_rows(goal)).sum(dim=1)[0])
    reach_off = float((_norm_rows(rolled_off) * _norm_rows(goal)).sum(dim=1)[0])
    assert reach_on > reach_off, (
        "ST_ROLLOUT MECHANISM-FIRES FAIL: rollout reach on-path=%.4f !> off-path=%.4f"
        % (reach_on, reach_off))
    print("[selftest] ST_ROLLOUT mechanism-fires: rollout reach on-path=%.4f > off-path=%.4f OK"
          % (reach_on, reach_off), flush=True)

    # ST_ANTI_TAUTOLOGY: the rollout-based separation must exceed the RAW (non-rolled)
    # target-cosine separation of the ORIGINAL (un-rolled) candidate states -- proves the
    # rollout carries genuine multi-step dynamics info, not just raw target-cosine in disguise.
    ctrl_on = float(reach_control_targetcos(Et[1:2], goal)[0])
    ctrl_off = float(reach_control_targetcos(Et[4:5], goal)[0])
    rollout_sep = reach_on - reach_off
    control_sep = abs(ctrl_on - ctrl_off)
    assert rollout_sep > control_sep + 0.05, (
        "ST_ANTI_TAUTOLOGY FAIL: rollout-sep=%.4f not clearly > control-sep=%.4f"
        % (rollout_sep, control_sep))
    print("[selftest] ST_ANTI_TAUTOLOGY: rollout-sep=%.4f >> control-sep=%.4f OK"
          % (rollout_sep, control_sep), flush=True)

    # ST_ROLLOUT_SHAPES: rollout_forward returns valid (idx,cleaned) shapes for k=0,1,2 and
    # k=0 degenerates to a plain cleanup of the input (no crash on the edge case).
    batch_state = Et[[1, 4, 2]]
    for kk in (0, 1, 2):
        idx_kk, cleaned_kk = rollout_forward(batch_state, Mt, Et, kk)
        assert idx_kk.shape == (3,), "ST_ROLLOUT_SHAPES bad idx shape k=%d: %s" % (kk, idx_kk.shape)
        assert cleaned_kk.shape == (3, Nt), (
            "ST_ROLLOUT_SHAPES bad cleaned shape k=%d: %s" % (kk, cleaned_kk.shape))
    idx0, cleaned0 = rollout_forward(batch_state, Mt, Et, 0)
    idx0_direct, _, _ = cleanup_batched(batch_state, Et)
    assert bool((idx0 == idx0_direct).all()), "ST_ROLLOUT_SHAPES k=0 must equal plain cleanup"
    print("[selftest] ST_ROLLOUT_SHAPES OK (k=0,1,2 all valid; k=0 == plain cleanup)", flush=True)

    # ST_PIPELINE: full single-seed structural check (regime + all 7 arms present, incl. the
    # 2 NEW arms feedback_only_reactive / gonogo_sr_rollout_anticipatory wired through the
    # real _eval_regime/run_one_seed path -- not just unit-tested in isolation)
    r = run_one_seed(SEEDS[0], REPO / "data" / "exp_selftest_tmp_pfc_cerebellum")
    rk0 = REGIME_KEYS[0]
    assert rk0 in r["regime_results"], "ST_PIPELINE missing regime %s" % rk0
    for arm in ARMS:
        assert arm in r["regime_results"][rk0]["arms"], "ST_PIPELINE missing arm %s" % arm
        av = r["regime_results"][rk0]["arms"][arm]
        assert 0.0 <= av <= 1.0, "ST_PIPELINE arm %s out of [0,1]: %.3f" % (arm, av)
        assert arm in r["regime_results"][rk0]["op_trace_hashes"], (
            "ST_PIPELINE missing op_trace_hash for %s" % arm)
    orc = r["regime_results"][rk0]["arms"]["oracle"]
    assert orc >= 0.5, "ST_PIPELINE oracle too low (%.3f) on toy self-test" % orc
    assert "rr_rollout_test" in r["regime_results"][rk0], "ST_PIPELINE missing rr_rollout_test"
    print("[selftest] ST_PIPELINE OK regimes=%s arms=%s oracle=%.3f rr_rollout=%.3f"
          % (REGIME_KEYS, ARMS, orc, r["regime_results"][rk0]["rr_rollout_test"]), flush=True)

    # ST_BINOM: binomial p symmetric + bounded
    p = binom_two_sided_p(8, 10, 0.5)
    assert 0.0 <= p <= 1.0, "ST_BINOM p out of range"
    assert abs(binom_two_sided_p(8, 10) - binom_two_sided_p(2, 10)) < 1e-9, "ST_BINOM not symmetric"
    print("[selftest] ST_BINOM two-sided p(8/10)=%.4f OK" % p, flush=True)

    # ST_CLOSURE_FORMULA: closure = (score-additive)/(oracle-additive)
    go_, add_, orc_ = 0.653, 0.053, 0.962
    cl = (go_ - add_) / (orc_ - add_)
    assert abs(cl - 0.65934) < 1e-3, "ST_CLOSURE_FORMULA off: %.5f" % cl
    print("[selftest] ST_CLOSURE_FORMULA OK (v2 fair d4 closure=%.3f)" % cl, flush=True)

    # ST_GAP_RECOVERY_FORMULA: hand-computed recovered_frac sanity
    d4_lift_, d6_lift_nc_, d6_lift_ant_ = 0.20, 0.05, 0.11
    gap_ = d4_lift_ - d6_lift_nc_
    recovered_ = (d6_lift_ant_ - d6_lift_nc_) / gap_
    assert abs(recovered_ - 0.40) < 1e-6, "ST_GAP_RECOVERY_FORMULA off: %.5f" % recovered_
    print("[selftest] ST_GAP_RECOVERY_FORMULA OK (recovered_frac=%.3f)" % recovered_, flush=True)

    _verdict_selftest()
    return 0


def _verdict_selftest() -> None:
    """Feed hand-built per-seed dicts through aggregate_and_verdict to lock verdict wiring."""
    def _mk_regime(n_ops, V, dd, add, orc, ctrl, v1, nc, react, ant, rr_rollout=0.60, wr_nc=1.0,
                  wr_ant=1.0):
        arms = {"v1_no_goal": v1, "additive_baseline": add, "cfrpe_control_identity": ctrl,
                "oracle": orc, "no_correction": nc, "feedback_only_reactive": react,
                "gonogo_sr_rollout_anticipatory": ant}
        oth = {"v1_no_goal": "a", "additive_baseline": "b", "cfrpe_control_identity": "c",
               "oracle": "oracle_true_seq", "no_correction": "nc", "feedback_only_reactive": "fr",
               "gonogo_sr_rollout_anticipatory": "ga"}
        return {"n_ops": n_ops, "V": V, "dd": dd, "arms": arms, "op_trace_hashes": oth,
                "best_alpha": 0.2, "best_w_reach_ctrl": 1.0, "best_w_reach_nc": wr_nc,
                "best_w_reach_ant": wr_ant, "additive_train_acc": add,
                "reach_rank_chance": 1.0 / n_ops, "rr_1step_test": rr_rollout,
                "rr_rollout_train": rr_rollout, "rr_rollout_test": rr_rollout,
                "rtc_rollout_test": -0.05,
                "paired_ant_vs_nc": {"n_ant_only": 10, "n_nc_only": 1},
                "paired_ant_vs_react": {"n_ant_only": 8, "n_react_only": 1}}

    global REGIMES, REGIME_KEYS, EXPECTED_N_UNITS
    saved = (REGIMES, REGIME_KEYS, EXPECTED_N_UNITS)

    # Case 1: HARD_PASS -- d4 no_correction lift=0.20, d6 no_correction lift=0.05 (gap=0.15),
    # anticipatory d6 lift = 0.05 + 0.45*0.15 = 0.1175 (>=40% recovery), reactive d6 lift=0.06
    # (anticipatory beats reactive by 0.0575 -- need >=0.10 margin, so raise anticipatory)
    rk_d4 = regime_key(4, 300, 4)
    rk_d6 = regime_key(4, 300, 6)
    REGIMES = [{"n_ops": 4, "V": 300, "dd": 4}, {"n_ops": 4, "V": 300, "dd": 6}]
    REGIME_KEYS = [rk_d4, rk_d6]
    EXPECTED_N_UNITS = len(ARMS) * 3 * len(REGIMES)
    ps = {}
    for s in ["7", "17", "23"]:
        ps[s] = {"regime_results": {
            rk_d4: _mk_regime(4, 300, 4, add=0.10, orc=0.95, ctrl=0.11, v1=0.05,
                              nc=0.30, react=0.11, ant=0.12, rr_rollout=0.60),
            rk_d6: _mk_regime(4, 300, 6, add=0.05, orc=0.92, ctrl=0.06, v1=0.02,
                              nc=0.10, react=0.11, ant=0.22, rr_rollout=0.40),
        }}
    try:
        out = aggregate_and_verdict(ps)
        assert out["verdict"] == "HARD_PASS", "ST_VERDICT case1 expected HARD_PASS got %s: %s" % (
            out["verdict"], out["verdict_msg"])

        # Case 2: HARD_FAIL -- anticipatory ties no_correction at d6 (no material lift)
        for s in ps:
            ps[s]["regime_results"][rk_d6]["arms"]["gonogo_sr_rollout_anticipatory"] = 0.052
        out2 = aggregate_and_verdict(ps)
        assert out2["verdict"] == "HARD_FAIL_NO_CEREBELLAR_CONSUMER", (
            "ST_VERDICT case2 expected HARD_FAIL got %s" % out2["verdict"])

        # Case 3: INCONCLUSIVE -- gap too small (no_correction barely changes d4->d6; d4
        # lift=0.20 fixed above, so d6 no_correction score=0.24 -> d6 lift=0.19 -> gap=0.01)
        for s in ps:
            ps[s]["regime_results"][rk_d6]["arms"]["no_correction"] = 0.24
            ps[s]["regime_results"][rk_d6]["arms"]["gonogo_sr_rollout_anticipatory"] = 0.25
        out3 = aggregate_and_verdict(ps)
        assert out3["verdict"] == "INCONCLUSIVE_GAP_TOO_SMALL_TO_MEASURE", (
            "ST_VERDICT case3 expected INCONCLUSIVE got %s" % out3["verdict"])
    finally:
        REGIMES, REGIME_KEYS, EXPECTED_N_UNITS = saved
    print("[selftest] ST_VERDICT_WIRING OK (HARD_PASS / HARD_FAIL_NO_CEREBELLAR_CONSUMER / "
          "INCONCLUSIVE_GAP_TOO_SMALL_TO_MEASURE all wired correctly)", flush=True)


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

    print("[%s] mode=%s device=%s N=%d n_ops_set=%s seeds=%s gamma=%.2f k_rollout=%d "
          "regimes=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_OPS_SET, SEEDS, BASELINE_GAMMA,
             K_ROLLOUT, REGIME_KEYS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            rc = _selftest()
            _atomic_write_metrics(out_dir, {
                "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_OK",
                "verdict_msg": "SELFTEST_OK: ST1 (cfrpe-TD shrink), ST3 (Go/NoGo argmax), "
                               "ST_ROLLOUT (mechanism-fires), ST_ANTI_TAUTOLOGY, ST_PIPELINE "
                               "(regime+arms), ST_BINOM, ST_CLOSURE_FORMULA, "
                               "ST_GAP_RECOVERY_FORMULA, ST_VERDICT_WIRING (3 cases)",
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
