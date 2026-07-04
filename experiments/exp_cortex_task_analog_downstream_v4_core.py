"""exp_cortex_task_analog_downstream_v4 CORE -- theory-grounded revival.

REVIVAL of v3 (commit-frozen; -0.058 HARD_FAIL at N=8192 M=300 flip=0.45)
per LDPC-Maxwell / Sharp-Capacity-Thresholds research drill
(notes/research_drill_LDPC_Maxwell_construction_VSA_multi_round_analog_2026-07-04.md).

v1 (commit 1ae012b60): H3_gap=-0.167 MB. HARD_FAIL utility-artifact.
v2 (commit ac201f6a6): H3_gap=-0.058 HARD_FAIL. CLARIFY tier gained nothing.
v2b (commit 7345bbbbe): H3_gap=-0.033 HARD_FAIL. Multi-round oracle-leak.
v3 (commit tbd): H3_gap negative HARD_FAIL. High-noise regime; argmax-then-argmax.

THEORETICAL DIAGNOSIS (per drill 2026-07-04):
    v1/v2/v2b/v3 all ran at N=8192, M=300 -> d^2/(n log n) = 8192^2/(300*5.7)
    = 39000, i.e. FAR ABOVE listwise-dominance-corridor upper bound of 2.
    Sharp Capacity Thresholds in Linear Associative Memory (arxiv 2605.05189):
    listwise (multi-round soft-evidence) strictly dominates argmax ONLY in
    corridor n <= d^2 <= 2*n*log(n). Above corridor: argmax cheaper and equally
    good. v3's regime is far above corridor -> theory predicts negative result
    (empirically confirmed).

v4 THEORY-CLEAN DESIGN:
    Step 1 (PRE-FLIGHT CORRIDOR TEST):
        Compute d^2/(n log n) at intended regime; require in [1/log n, 2].
        If FAIL: abort with regime-not-in-corridor sentinel.
    Step 2 (LISTWISE SOFT-EVIDENCE ROUND 2, no oracle leak):
        v2b/v3 used partial-mask hint reveal via ground-truth target_key
        (oracle leak). v4 uses TRUE listwise: logsumexp over top-K item
        similarities per value class. No ground-truth needed.
    Step 3 (CORRIDOR-ENTERING PARAMETERS):
        N_DIM=512, M_ITEMS=20000, V_CB=32. d^2/(n log n)=1.32 IN CORRIDOR.
        Kill-switch cascade: (N=400,M=10000) or (N=300,M=6000).

SUBSTRATE-ENVELOPE CAVEAT (transparency):
    hdlab.cortex.CortexConfig envelope declares N_DIM >= 8192 (M1.5+M1.7
    inherited). v4 uses N_DIM=512 which BREAKS that envelope; therefore v4
    CANNOT use cortex.forward. v4 instead implements the LISTWISE MECHANISM
    CONCEPT directly (argmax + logsumexp value-marginalization over top-K).
    v4 is a THEORY-CONCEPT VALIDATION of listwise-dominance-in-corridor, NOT
    a test of the cortex facade code. Pre-reg is explicit about this scope
    change from v1/v2/v2b/v3.

ARM STRUCTURE (v4 supersedes v3 3-arm structure with 3 direct-comparison arms):
    ARM_LISTWISE_ROUND2 (listwise multi-round soft-evidence):
        Round 1: argmax over sims -> top-1; compute log-margin = sims[top_1] -
                 sims[top_2].
        If log-margin < MARGIN_TAU: enter Round 2 (listwise).
        Round 2: logsumexp over top-K items per value class; argmax over value
                 classes. Answer = argmax_v logsumexp_{i in top_K, val[i]==v} sims[i].
        If log-margin >= MARGIN_TAU: accept Round 1 answer = val[top_1].
    ARM_ARGMAX_SINGLESHOT (single-round argmax, no refuse):
        Answer = val[argmax over sims]. Always accept.
    ARM_ARGMAX_WITH_REFUSE (argmax + refuse gate; v3 INDIV analog):
        If sims[top_1] >= REFUSE_TAU: answer = val[top_1]. Else REFUSE.

PRIMARY DISCRIMINATOR: H3_gap = util(ARM_LISTWISE_ROUND2) - util(ARM_ARGMAX_WITH_REFUSE).
Secondary: H1_gap = util(ARM_LISTWISE) - util(ARM_ARGMAX_SINGLESHOT).

PRE-COMMITTED PREDICTION (per drill 2026-07-04):
    PASS: H3_gap >= +0.05 AND gap/SEM >= +2.0
        -> atom LISTWISE_STRICTLY_DOMINATES_ARGMAX_IN_CORRIDOR_v4_MM_TENTATIVE
        -> single-task arc REOPENS at corridor-scoped atom.
    MB:   +0.02 <= H3_gap < +0.05 (marginal; needs 3-seed CV)
    FAIL: H3_gap < +0.02 OR gap/SEM < +2.0
        -> DEFINITIVE atom NO_LISTWISE_ADVANTAGE_EVEN_IN_THEORY_OPTIMAL_CORRIDOR_v4
        -> single-task arc CLOSES at MM_STANDARD.

Anti-drift discipline:
    - Corridor test PRE-COMPUTED + gated at cell-init BEFORE running.
    - Soft-evidence semantics fixed: logsumexp per value-class over top-K.
    - Prediction pre-committed BEFORE running (numeric band frozen).
    - If FAIL: honest-negative escalation; NO re-tune of thresholds.
    - Kill-switch cascade documented in pre-reg (regime only, not mechanism).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified: per-arm retrieval SHA256 hashes.
    - final_metrics_atomicity: tmp_replace.
    - except SystemExit: raise BEFORE except Exception.
    - crlb_n/a: N/A (utility-metric cell; corridor-position is capacity proxy).
    - baseline_in_band: check argmax_singleshot util in [0.05, 0.95].
    - discriminator survives scale: analytical (LDPC drill; in-corridor prediction).
    - HARD_PASS strictly above floor +0.02 (predict +0.05).
    - cardinality_ok: 3 arms x 1 seed = 3.
    - per-unit failure-class in metrics (no bare except).
    - calibration_check: default_ok_for_this_regime (fixed thresholds; theory-grounded).
    - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.

Storage strategy: SHARDED (each M=20000 KB item has its own key vector).

Compute architecture: (b) sequential-CPU with justification (per-query direct
matmul + softmax; ~1-3s per arm at N=512 M=20000 30-query; total wall <30s SMOKE).

ASCII-only. Windowless subprocess. Wrapper (_s7) dispatches single-seed run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from experiments._cell_heartbeat import emit_heartbeat
except Exception:
    def emit_heartbeat(*args, **kwargs):
        return None


# ------------------------------ configuration --------------------------------

ANCHOR_BASE = "exp_cortex_task_analog_downstream_v4"

# v4 SOLE STRUCTURAL DIFF vs v3: corridor-entering regime per LDPC drill.
# THEORETICAL@ notes/research_drill_LDPC_Maxwell_construction_VSA_multi_round_analog_2026-07-04.md
# Sharp Capacity Thresholds in Linear Associative Memory, arxiv 2605.05189.
# Listwise strictly dominates argmax in corridor n <= d^2 <= 2*n*log(n).
# At (N=512, M=20000): d^2/(n log n) = 262144 / (20000 * 9.90) = 1.32.
# corridor bounds in d^2/(n log n) space: [1/ln(20000), 2] = [0.101, 2.0].
# 1.32 in [0.101, 2.0] -> IN CORRIDOR (comfortable margin).
N_DIM = 512
M_ITEMS = 20000
V_CB = 32                       # M/V_CB = 625 items/class enables listwise pooling.

# v4 SOLE MECHANISM DIFF vs v3: bit-flip P relaxed from v3's 0.45 to 0.35
# (task-directive per larger M gives more candidates + higher listwise pooling).
NOISY_FLIP_FRAC = 0.35

# Listwise Round-2 mechanics (logsumexp per value class over top-K).
# THEORETICAL@ K = 2*log(M) ~ 20 for M=20000 (rule-of-thumb top-list size
# per LDPC drill). Provides sufficient class-multiplicity: E[items/class in
# top-K] = K * (1/V_CB) = 20 * (1/32) = 0.625 per class on average -> most
# classes have 0-1 items; correct class benefits from any additional in-class
# item's evidence.
ROUND2_TOP_K = 20

# Margin threshold gating Round-1 -> Round-2. Log-margin = sims[top_1] - sims[top_2].
# ADAPTIVE per-batch design: MARGIN_TAU_ADAPTIVE_QUANTILE = 0.50 (median of
# log-margins over ACCEPTED (non-refused) queries in current batch). Ensures
# ~50% of accepted queries route through Round 2 -> mechanism fires by design
# per META_RULE_K "SMOKE MUST FIRE THE DISCRIMINATOR". Design choice is on
# MARGIN (input) not CORRECTNESS (output) -> not p-hacking; declared as
# calibration_check: "adaptive_with_discriminator_gate".
# Fallback fixed cap: MARGIN_TAU_FIXED_CAP (upper bound on adaptive threshold).
MARGIN_TAU_ADAPTIVE_QUANTILE = 0.50
MARGIN_TAU_FIXED_CAP = 0.50

# Refuse gate for ARM_ARGMAX_WITH_REFUSE. Set above noise floor.
# THEORETICAL@ random-baseline sim = sqrt(2 ln M / N) = sqrt(2*9.90/512) = 0.197.
# Set REFUSE_TAU = 0.25 (above random-max, below signal at flip=0.35 which gives
# expected cos = 1 - 2*0.35 = 0.30).
REFUSE_TAU = 0.25

# Query intent mix (v3-frozen counts for comparability).
FULL_N_CLEAN = 30
FULL_N_NOISY = 30
FULL_N_OOB = 40
SMOKE_N_CLEAN = 10
SMOKE_N_NOISY = 10
SMOKE_N_OOB = 10

# v3-frozen utility function.
UTIL_ACCEPT_CORRECT = 1.0
UTIL_ACCEPT_WRONG = 0.0
UTIL_LISTWISE_ROUND2_CORRECT = 0.9   # 10% retry cost (mirrors v3's UTIL_CLARIFY).
UTIL_LISTWISE_ROUND2_WRONG = 0.0
UTIL_REFUSE_TERMINAL = 0.0

ARMS = ["ARM_LISTWISE_ROUND2", "ARM_ARGMAX_SINGLESHOT", "ARM_ARGMAX_WITH_REFUSE"]


# ------------------------ output-dir + IO helpers ----------------------------


def _output_dir_for(anchor_name: str, run_mode: str) -> Path:
    if run_mode == "smoke":
        return REPO_ROOT / "data" / f"{anchor_name}_smoke"
    elif run_mode == "self_test":
        return REPO_ROOT / "data" / f"{anchor_name}_selftest"
    else:
        return REPO_ROOT / "data" / anchor_name


def _write_start_marker(output_dir: Path, anchor_name: str, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, anchor_name: str,
                         exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
        "failure_class": type(exc).__name__,
    }
    _write_metrics_atomic(output_dir, diag)


# ---------------------------- corridor pre-flight ----------------------------


def compute_corridor_position(n_dim: int, m_items: int) -> Dict[str, float]:
    """Compute d^2/n and d^2/(n log n) plus corridor bounds.

    Per LDPC-Maxwell / Sharp-Capacity-Thresholds drill:
        Listwise strictly dominates argmax iff n <= d^2 <= 2 n log n.
        Equivalent (dividing by n log n):
            1/log n <= d^2/(n log n) <= 2.
    """
    d2 = float(n_dim * n_dim)
    n = float(m_items)
    lnn = math.log(n)
    ratio_dn = d2 / n
    ratio_dnlogn = d2 / (n * lnn)
    lower_dnlogn = 1.0 / lnn
    upper_dnlogn = 2.0
    lower_dn = 1.0
    upper_dn = 2.0 * lnn
    in_corridor = (lower_dnlogn <= ratio_dnlogn <= upper_dnlogn)
    return {
        "d2_over_n": ratio_dn,
        "d2_over_n_logn": ratio_dnlogn,
        "corridor_lower_dnlogn": lower_dnlogn,
        "corridor_upper_dnlogn": upper_dnlogn,
        "corridor_lower_dn": lower_dn,
        "corridor_upper_dn": upper_dn,
        "in_corridor": bool(in_corridor),
    }


# ---------------------------- data generators --------------------------------


def _bipolar_random(shape, gen: torch.Generator) -> torch.Tensor:
    r = torch.rand(shape, generator=gen)
    return torch.where(r < 0.5,
                       torch.tensor(-1.0),
                       torch.tensor(1.0)).to(torch.float32)


def build_kb(seed: int, m_items: int
             ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Build (kb_keys[M,N], kb_val_indices[M])."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    keys = _bipolar_random((m_items, N_DIM), gen)
    val_indices = torch.arange(m_items) % V_CB
    val_indices = val_indices[torch.randperm(m_items, generator=gen)]
    return keys, val_indices


def build_queries(seed: int, kb_keys: torch.Tensor, kb_val_indices: torch.Tensor,
                  n_clean: int, n_noisy: int, n_oob: int
                  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build (queries[Q,N], intent_class[Q], true_val[Q]).

    intent_class: 0=CLEAN, 1=NOISY, 2=OOB.

    NOTE v4: no target_kb_idx; v4 mechanism is fully oracle-free (no ground-truth
    reveal in Round 2). This is the theory-clean design per drill.
    """
    m_items = kb_keys.shape[0]
    gen = torch.Generator()
    gen.manual_seed(seed + 500)

    q_total = n_clean + n_noisy + n_oob
    queries = torch.zeros(q_total, N_DIM, dtype=torch.float32)
    intent = torch.zeros(q_total, dtype=torch.long)
    true_val = torch.full((q_total,), -1, dtype=torch.long)

    clean_items = torch.randperm(m_items, generator=gen)[:n_clean]
    for i, idx in enumerate(clean_items.tolist()):
        queries[i] = kb_keys[idx]
        intent[i] = 0
        true_val[i] = int(kb_val_indices[idx])

    noisy_items = torch.randperm(m_items, generator=gen)[:n_noisy]
    for i, idx in enumerate(noisy_items.tolist()):
        q = kb_keys[idx].clone()
        n_flip = int(NOISY_FLIP_FRAC * N_DIM)
        flip_idx = torch.randperm(N_DIM, generator=gen)[:n_flip]
        q[flip_idx] = -q[flip_idx]
        queries[n_clean + i] = q
        intent[n_clean + i] = 1
        true_val[n_clean + i] = int(kb_val_indices[idx])

    for i in range(n_oob):
        queries[n_clean + n_noisy + i] = _bipolar_random((N_DIM,), gen)
        intent[n_clean + n_noisy + i] = 2
        true_val[n_clean + n_noisy + i] = -1

    return queries, intent, true_val


# ------------------------ per-arm implementation -----------------------------


def _compute_sims(q: torch.Tensor,
                  kb_keys_normed: torch.Tensor) -> torch.Tensor:
    """Cosine similarities: (M,) tensor."""
    q_n = q / q.norm().clamp_min(1e-9)
    return kb_keys_normed @ q_n


def _listwise_round2_value_marginalization(
        sims: torch.Tensor,
        kb_val_indices: torch.Tensor,
        top_k: int) -> int:
    """LISTWISE ROUND 2: logsumexp per value class over top-K items.

    v4 theory-clean Round 2 per LDPC drill: no oracle leak; uses only sims
    distribution + kb_val_indices metadata.

    Returns predicted value class.
    """
    top_vals, top_idx = torch.topk(sims, k=top_k, largest=True)
    # Build per-value-class logsumexp over top-K items.
    val_of_top = kb_val_indices[top_idx]  # (top_k,)
    unique_vals = torch.unique(val_of_top).tolist()
    best_v = -1
    best_score = float("-inf")
    for v in unique_vals:
        mask = (val_of_top == v)
        # logsumexp over sims (which are already in a suitable log-domain scale).
        contrib = top_vals[mask]
        score = float(torch.logsumexp(contrib, dim=0))
        if score > best_score:
            best_score = score
            best_v = int(v)
    return best_v


def run_arm_listwise_round2(seed: int, queries: torch.Tensor,
                            kb_keys: torch.Tensor,
                            kb_val_indices: torch.Tensor,
                            intent: torch.Tensor,
                            true_val: torch.Tensor) -> Dict[str, object]:
    """ARM_LISTWISE_ROUND2: multi-round with soft-evidence Round 2.

    Two-pass adaptive threshold design:
      Pass 1: compute all sims + top-1/top-2 margins + refuse decisions.
      Adaptive threshold: MARGIN_TAU = quantile(non-refused margins,
                          MARGIN_TAU_ADAPTIVE_QUANTILE) capped by
                          MARGIN_TAU_FIXED_CAP.
      Pass 2: for each accepted query, route via margin < adaptive_tau to
              LISTWISE Round 2, else accept Round 1.
    """
    q_total = queries.shape[0]
    k_normed = kb_keys / kb_keys.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    # Pass 1: compute per-query sims, top-1/2, margins, refuse decisions.
    sims_list = []
    top1_sim_list = []
    top1_idx_list = []
    margin_list = []
    refuse_list = []
    for i in range(q_total):
        sims = _compute_sims(queries[i], k_normed)
        sims_list.append(sims)
        top2 = torch.topk(sims, k=2, largest=True)
        top1_sim = float(top2.values[0])
        top2_sim = float(top2.values[1])
        top1_idx = int(top2.indices[0])
        margin = top1_sim - top2_sim
        top1_sim_list.append(top1_sim)
        top1_idx_list.append(top1_idx)
        margin_list.append(margin)
        refuse_list.append(top1_sim < REFUSE_TAU)

    # Adaptive threshold: quantile over non-refused margins.
    nonrefuse_margins = [m for m, r in zip(margin_list, refuse_list) if not r]
    if nonrefuse_margins:
        adaptive_tau = float(np.quantile(
            nonrefuse_margins, MARGIN_TAU_ADAPTIVE_QUANTILE))
    else:
        adaptive_tau = 0.0
    margin_tau_used = min(adaptive_tau, MARGIN_TAU_FIXED_CAP)

    # Pass 2: decide route + compute util per query.
    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_round2_success = []
    retrieval_bytes = bytearray()

    n_r2_correct = 0
    n_r2_wrong = 0
    n_r2_total = 0
    n_accept = 0
    n_refuse = 0

    for i in range(q_total):
        sims = sims_list[i]
        top1_idx = top1_idx_list[i]
        margin = margin_list[i]
        pred_val_r1 = int(kb_val_indices[top1_idx])
        round2_success = -1

        if refuse_list[i]:
            route = "REFUSE"
            n_refuse += 1
            util = UTIL_REFUSE_TERMINAL
            pred_val = -1
        elif margin < margin_tau_used:
            route = "LISTWISE_R2"
            n_r2_total += 1
            pred_val_r2 = _listwise_round2_value_marginalization(
                sims, kb_val_indices, top_k=ROUND2_TOP_K)
            pred_val = pred_val_r2
            if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
                util = UTIL_LISTWISE_ROUND2_CORRECT
                round2_success = 1
                n_r2_correct += 1
            else:
                util = UTIL_LISTWISE_ROUND2_WRONG
                round2_success = 0
                n_r2_wrong += 1
        else:
            route = "ACCEPT_R1"
            pred_val = pred_val_r1
            n_accept += 1
            if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
                util = UTIL_ACCEPT_CORRECT
            else:
                util = UTIL_ACCEPT_WRONG

        per_query_util.append(util)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_round2_success.append(round2_success)
        retrieval_bytes.extend(
            f"{route}|{pred_val}|{round2_success}|".encode("utf-8"))

    return {
        "arm": "ARM_LISTWISE_ROUND2",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": n_accept,
        "n_listwise_r2": n_r2_total,
        "n_refuse": n_refuse,
        "n_r2_correct": n_r2_correct,
        "n_r2_wrong": n_r2_wrong,
        "r2_success_rate":
            float(n_r2_correct) / max(1, n_r2_total),
        "margin_mean": float(np.mean(margin_list)),
        "margin_p25": float(np.percentile(margin_list, 25)),
        "margin_tau_used": margin_tau_used,
        "adaptive_tau_raw": adaptive_tau,
        "confidence_mean": float(np.mean(margin_list)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "per_query_round2_success": per_query_round2_success,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


def run_arm_argmax_singleshot(seed: int, queries: torch.Tensor,
                              kb_keys: torch.Tensor,
                              kb_val_indices: torch.Tensor,
                              intent: torch.Tensor,
                              true_val: torch.Tensor) -> Dict[str, object]:
    """ARM_ARGMAX_SINGLESHOT: argmax over sims; always accept; no refuse."""
    q_total = queries.shape[0]
    k_normed = kb_keys / kb_keys.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    retrieval_bytes = bytearray()

    for i in range(q_total):
        sims = _compute_sims(queries[i], k_normed)
        top1_idx = int(torch.argmax(sims).item())
        max_sim = float(sims.max())
        pred_val = int(kb_val_indices[top1_idx])
        route = "ACCEPT"
        if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
            util = UTIL_ACCEPT_CORRECT
        else:
            util = UTIL_ACCEPT_WRONG
        per_query_util.append(util)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(max_sim)
        retrieval_bytes.extend(f"{route}|{pred_val}|-1|".encode("utf-8"))

    return {
        "arm": "ARM_ARGMAX_SINGLESHOT",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": q_total,
        "n_listwise_r2": 0,
        "n_refuse": 0,
        "confidence_mean": float(np.mean(per_query_conf)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


def run_arm_argmax_with_refuse(seed: int, queries: torch.Tensor,
                               kb_keys: torch.Tensor,
                               kb_val_indices: torch.Tensor,
                               intent: torch.Tensor,
                               true_val: torch.Tensor) -> Dict[str, object]:
    """ARM_ARGMAX_WITH_REFUSE: argmax + refuse-gate (analog of v3 INDIV)."""
    q_total = queries.shape[0]
    k_normed = kb_keys / kb_keys.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    retrieval_bytes = bytearray()
    n_accept = 0
    n_refuse = 0

    for i in range(q_total):
        sims = _compute_sims(queries[i], k_normed)
        top1_idx = int(torch.argmax(sims).item())
        max_sim = float(sims.max())
        pred_val = int(kb_val_indices[top1_idx])
        if max_sim >= REFUSE_TAU:
            route = "ACCEPT"
            n_accept += 1
            if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
                util = UTIL_ACCEPT_CORRECT
            else:
                util = UTIL_ACCEPT_WRONG
        else:
            route = "REFUSE"
            n_refuse += 1
            util = UTIL_REFUSE_TERMINAL
            pred_val = -1
        per_query_util.append(util)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(max_sim)
        retrieval_bytes.extend(f"{route}|{pred_val}|-1|".encode("utf-8"))

    return {
        "arm": "ARM_ARGMAX_WITH_REFUSE",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": n_accept,
        "n_listwise_r2": 0,
        "n_refuse": n_refuse,
        "confidence_mean": float(np.mean(per_query_conf)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


# ------------------------------ run one seed --------------------------------


def run_one_seed(seed: int, run_mode: str, output_dir: Path,
                 t0: float) -> Dict[str, object]:
    if run_mode == "smoke" or run_mode == "self_test":
        n_clean, n_noisy, n_oob = SMOKE_N_CLEAN, SMOKE_N_NOISY, SMOKE_N_OOB
    else:
        n_clean, n_noisy, n_oob = FULL_N_CLEAN, FULL_N_NOISY, FULL_N_OOB

    kb_keys, kb_val_indices = build_kb(seed, M_ITEMS)
    queries, intent, true_val = build_queries(
        seed, kb_keys, kb_val_indices, n_clean, n_noisy, n_oob)

    print(f"[seed={seed}] arms starting, n_queries={queries.shape[0]} "
          f"({n_clean}/{n_noisy}/{n_oob}) flip_frac={NOISY_FLIP_FRAC} "
          f"N={N_DIM} M={M_ITEMS} V_CB={V_CB} top_K={ROUND2_TOP_K}",
          flush=True)

    per_arm_results = {}
    per_arm_failure = {}
    for arm_idx, arm_name in enumerate(ARMS):
        try:
            if arm_name == "ARM_LISTWISE_ROUND2":
                r = run_arm_listwise_round2(seed, queries, kb_keys,
                                            kb_val_indices, intent, true_val)
            elif arm_name == "ARM_ARGMAX_SINGLESHOT":
                r = run_arm_argmax_singleshot(seed, queries, kb_keys,
                                              kb_val_indices, intent, true_val)
            else:
                r = run_arm_argmax_with_refuse(seed, queries, kb_keys,
                                                kb_val_indices, intent, true_val)
            per_arm_results[arm_name] = r
            emit_heartbeat(output_dir, unit_idx=arm_idx, total_units=len(ARMS),
                           elapsed_s=time.perf_counter() - t0)
            r2_str = ""
            if "r2_success_rate" in r:
                r2_str = (f" r2_success={r.get('n_r2_correct',0)}/"
                          f"{r.get('n_r2_correct',0)+r.get('n_r2_wrong',0)}")
            print(f"[seed={seed}] {arm_name} norm_util={r['utility_norm']:.4f} "
                  f"n_accept={r['n_accept']} n_r2={r['n_listwise_r2']} "
                  f"n_refuse={r['n_refuse']}{r2_str} "
                  f"conf_mean={r['confidence_mean']:.4f}",
                  flush=True)
        except Exception as e:
            per_arm_failure[arm_name] = {
                "failure_class": type(e).__name__,
                "msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            print(f"[seed={seed}] {arm_name} FAILED: {type(e).__name__}: {e}",
                  flush=True)

    hashes = {a: per_arm_results[a]["retrieval_sha256"]
              for a in per_arm_results}
    arms_differ = True
    diff_report = {}
    hash_pairs = [(a, b) for a in hashes for b in hashes if a < b]
    for a, b in hash_pairs:
        eq = (hashes[a] == hashes[b])
        diff_report[f"{a}__vs__{b}"] = "IDENTICAL" if eq else "DIFFER"
        if eq:
            arms_differ = False

    return {
        "seed": seed,
        "n_queries_total": int(queries.shape[0]),
        "intent_split": {"clean": n_clean, "noisy": n_noisy, "oob": n_oob},
        "per_arm": per_arm_results,
        "per_arm_failure": per_arm_failure,
        "arms_differ_verified": arms_differ,
        "arms_differ_report": diff_report,
    }


# ------------------------------ verdict logic -------------------------------


def compute_verdict(per_seed: Dict[int, dict], run_mode: str,
                    corridor_info: Dict[str, float]) -> Dict[str, object]:
    """Predict-then-check verdict on H3_gap in corridor regime.

    PRE-COMMITTED (per drill 2026-07-04):
        PASS: H3_gap >= +0.05 AND gap/SEM >= +2.0
        MB:   +0.02 <= H3_gap < +0.05
        FAIL: H3_gap < +0.02 OR gap/SEM < +2.0
    """
    seeds = sorted(per_seed.keys())
    n_seeds = len(seeds)
    n_arms = len(ARMS)
    expected_n_units = n_arms * n_seeds

    completed_arms = sum(
        1 for s in seeds for a in ARMS
        if a in per_seed[s].get("per_arm", {}))
    cardinality_ok = (completed_arms == expected_n_units)

    per_arm_agg = {}
    for arm in ARMS:
        vals = []
        for s in seeds:
            r = per_seed[s].get("per_arm", {}).get(arm)
            if r is not None:
                vals.append(r["utility_norm"])
        if vals:
            m = float(np.mean(vals))
            sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            cv = sd / max(abs(m), 1e-9) if m != 0 else 0.0
        else:
            m, sd, cv = float("nan"), float("nan"), float("nan")
        per_arm_agg[arm] = {"mean": m, "sd": sd, "cv": cv, "n_seeds": len(vals)}

    listwise_util = per_arm_agg["ARM_LISTWISE_ROUND2"]["mean"]
    singleshot_util = per_arm_agg["ARM_ARGMAX_SINGLESHOT"]["mean"]
    refuse_util = per_arm_agg["ARM_ARGMAX_WITH_REFUSE"]["mean"]

    h1_gap = listwise_util - singleshot_util
    h3_gap = listwise_util - refuse_util  # PRIMARY discriminator
    listwise_cv = per_arm_agg["ARM_LISTWISE_ROUND2"]["cv"]

    # Per-query gap SEM.
    listwise_per_query = []
    refuse_per_query = []
    for s in seeds:
        r_l = per_seed[s].get("per_arm", {}).get("ARM_LISTWISE_ROUND2")
        r_r = per_seed[s].get("per_arm", {}).get("ARM_ARGMAX_WITH_REFUSE")
        if r_l is not None and r_r is not None:
            listwise_per_query.extend(r_l.get("per_query_util", []))
            refuse_per_query.extend(r_r.get("per_query_util", []))
    if (listwise_per_query and refuse_per_query
            and len(listwise_per_query) == len(refuse_per_query)):
        diffs = np.array(listwise_per_query) - np.array(refuse_per_query)
        if len(diffs) > 1:
            gap_sem = float(np.std(diffs, ddof=1) / np.sqrt(len(diffs)))
        else:
            gap_sem = float("nan")
    else:
        gap_sem = float("nan")

    gap_over_sem = h3_gap / gap_sem if gap_sem and gap_sem > 0 else float("nan")

    arms_differ_all = all(per_seed[s].get("arms_differ_verified", False)
                          for s in seeds)

    baseline_in_band = 0.05 < refuse_util < 0.95
    listwise_in_band = 0.05 < listwise_util < 0.95

    reasons = []
    verdict = "HARD_PASS"

    if not corridor_info["in_corridor"]:
        verdict = "HARD_FAIL_REGIME_NOT_IN_CORRIDOR_v4_META_RULE_L"
        reasons.append(
            f"CORRIDOR_GATE_FAIL: d^2/(n log n)="
            f"{corridor_info['d2_over_n_logn']:.3f} not in "
            f"[{corridor_info['corridor_lower_dnlogn']:.3f}, "
            f"{corridor_info['corridor_upper_dnlogn']:.1f}]; "
            f"listwise not theory-predicted to dominate argmax")

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        reasons.append(f"cardinality {completed_arms}/{expected_n_units}")

    if not arms_differ_all:
        verdict = "HARD_FAIL"
        reasons.append("META_RULE_AF violation: arm retrievals bit-identical")

    if not baseline_in_band:
        if verdict == "HARD_PASS":
            verdict = "MIDDLE_BAND"
        reasons.append(
            f"META_RULE_AG: baseline refuse_util={refuse_util:.4f} outside "
            f"[0.05, 0.95]")

    # PRIMARY predict-then-check gate: H3_gap band (v4 corridor prediction).
    if h3_gap < 0.02:
        verdict = "HARD_FAIL"
        reasons.append(
            f"H3_gap={h3_gap:.4f} < +0.02 (LISTWISE_NOT_DOMINANT_EVEN_IN_CORRIDOR; "
            f"DEFINITIVE close-arc candidate)")
    elif h3_gap < 0.05:
        if verdict == "HARD_PASS":
            verdict = "MIDDLE_BAND"
        reasons.append(
            f"H3_gap={h3_gap:.4f} in MB band [+0.02, +0.05); marginal advantage")
    else:
        if not np.isnan(gap_over_sem) and gap_over_sem < 2.0:
            verdict = "HARD_FAIL"
            reasons.append(
                f"H3_gap={h3_gap:.4f} passes point but gap/SEM={gap_over_sem:.2f} "
                f"< 2.0 (not statistically distinguishable from 0)")

    reasons.append(
        f"H1_gap={h1_gap:.4f} (secondary; listwise vs no-refuse-argmax)")

    if run_mode == "full":
        if listwise_cv >= 0.30:
            verdict = "HARD_FAIL"
            reasons.append(f"listwise cv={listwise_cv:.4f} >= 0.30")
        elif listwise_cv >= 0.20:
            if verdict == "HARD_PASS":
                verdict = "MIDDLE_BAND"
            reasons.append(f"listwise cv={listwise_cv:.4f} in MB [0.20, 0.30]")

    verdict_msg = (
        f"{verdict} | H3_gap={h3_gap:.4f} gap/SEM={gap_over_sem:.2f} | "
        f"H1_gap={h1_gap:.4f} (secondary) | "
        f"LISTWISE={listwise_util:.4f} SINGLESHOT={singleshot_util:.4f} "
        f"REFUSE={refuse_util:.4f} | "
        f"cv_LISTWISE={listwise_cv:.4f} | arms_differ={arms_differ_all} | "
        f"cardinality={completed_arms}/{expected_n_units} | "
        f"corridor=d2/(n*lnn)={corridor_info['d2_over_n_logn']:.3f}_"
        f"IN={corridor_info['in_corridor']} | "
        f"flip_frac={NOISY_FLIP_FRAC} N={N_DIM} M={M_ITEMS} V_CB={V_CB} | "
        f"reasons={'; '.join(reasons) if reasons else 'all_gates_pass'}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "per_arm_agg": per_arm_agg,
        "h1_gap": h1_gap,
        "h3_gap": h3_gap,
        "h3_gap_sem": gap_sem,
        "h3_gap_over_sem": gap_over_sem,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "completed_units": completed_arms,
        "arms_differ_verified": arms_differ_all,
        "baseline_in_band": baseline_in_band,
        "listwise_in_band": listwise_in_band,
        "corridor_info": corridor_info,
        "reasons": reasons,
    }


# ------------------------------ main entrypoint -----------------------------


def _run_one_seed_wrapper(seed: int, run_mode: str, anchor_name: str) -> int:
    output_dir = _output_dir_for(anchor_name, run_mode)
    t0 = time.perf_counter()
    corridor_info = compute_corridor_position(N_DIM, M_ITEMS)
    try:
        _write_start_marker(output_dir, anchor_name, run_mode,
                            expected_n_units=len(ARMS))
        # Corridor pre-flight: refuse to run if regime not in dominance corridor.
        # Test discipline per drill: if regime not in corridor, theory predicts
        # null; running the cell is a waste of compute.
        if not corridor_info["in_corridor"]:
            metrics = {
                "anchor_name": anchor_name,
                "run_mode": run_mode,
                "seed": seed,
                "elapsed_s": time.perf_counter() - t0,
                "ts_iso": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "host": platform.node(),
                "verdict": "HARD_FAIL_REGIME_NOT_IN_CORRIDOR_v4_META_RULE_L",
                "verdict_msg":
                    f"HARD_FAIL_REGIME_NOT_IN_CORRIDOR | "
                    f"d^2/(n log n)={corridor_info['d2_over_n_logn']:.3f} "
                    f"not in [{corridor_info['corridor_lower_dnlogn']:.3f}, "
                    f"{corridor_info['corridor_upper_dnlogn']:.1f}]; "
                    f"per LDPC drill listwise NOT theory-predicted to dominate; "
                    f"cell aborted before running",
                "summary":
                    f"HARD_FAIL_REGIME_NOT_IN_CORRIDOR "
                    f"d2/(n*lnn)={corridor_info['d2_over_n_logn']:.3f}",
                "corridor_info": corridor_info,
                "config": {
                    "N_DIM": N_DIM, "M_ITEMS": M_ITEMS, "V_CB": V_CB,
                    "NOISY_FLIP_FRAC": NOISY_FLIP_FRAC,
                    "ROUND2_TOP_K": ROUND2_TOP_K,
                    "MARGIN_TAU_ADAPTIVE_QUANTILE": MARGIN_TAU_ADAPTIVE_QUANTILE,
                    "MARGIN_TAU_FIXED_CAP": MARGIN_TAU_FIXED_CAP,
                    "REFUSE_TAU": REFUSE_TAU,
                },
            }
            _write_metrics_atomic(output_dir, metrics)
            print(f"[abort] REGIME_NOT_IN_CORRIDOR: "
                  f"d^2/(n log n)={corridor_info['d2_over_n_logn']:.3f}",
                  flush=True)
            return 0

        per_seed_result = run_one_seed(seed, run_mode, output_dir, t0)
        elapsed = time.perf_counter() - t0
        verdict_info = compute_verdict({seed: per_seed_result}, run_mode,
                                        corridor_info)
        metrics = {
            "anchor_name": anchor_name,
            "run_mode": run_mode,
            "seed": seed,
            "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "host": platform.node(),
            "config": {
                "N_DIM": N_DIM, "M_ITEMS": M_ITEMS, "V_CB": V_CB,
                "NOISY_FLIP_FRAC": NOISY_FLIP_FRAC,
                "ROUND2_TOP_K": ROUND2_TOP_K,
                "MARGIN_TAU_ADAPTIVE_QUANTILE": MARGIN_TAU_ADAPTIVE_QUANTILE,
                "MARGIN_TAU_FIXED_CAP": MARGIN_TAU_FIXED_CAP,
                "REFUSE_TAU": REFUSE_TAU,
                "UTIL_ACCEPT_CORRECT": UTIL_ACCEPT_CORRECT,
                "UTIL_ACCEPT_WRONG": UTIL_ACCEPT_WRONG,
                "UTIL_LISTWISE_ROUND2_CORRECT": UTIL_LISTWISE_ROUND2_CORRECT,
                "UTIL_LISTWISE_ROUND2_WRONG": UTIL_LISTWISE_ROUND2_WRONG,
                "UTIL_REFUSE_TERMINAL": UTIL_REFUSE_TERMINAL,
            },
            "per_seed": {str(seed): per_seed_result},
            "verdict": verdict_info["verdict"],
            "verdict_msg": verdict_info["verdict_msg"],
            "summary": verdict_info["summary"],
            "per_arm_agg": verdict_info["per_arm_agg"],
            "h1_gap": verdict_info["h1_gap"],
            "h3_gap": verdict_info["h3_gap"],
            "h3_gap_sem": verdict_info["h3_gap_sem"],
            "h3_gap_over_sem": verdict_info["h3_gap_over_sem"],
            "cardinality_ok": verdict_info["cardinality_ok"],
            "expected_n_units": verdict_info["expected_n_units"],
            "arms_differ_verified": verdict_info["arms_differ_verified"],
            "baseline_in_band": verdict_info["baseline_in_band"],
            "listwise_in_band": verdict_info["listwise_in_band"],
            "corridor_info": verdict_info["corridor_info"],
            "reasons": verdict_info["reasons"],
        }
        _write_metrics_atomic(output_dir, metrics)
        print(f"[done] {verdict_info['verdict_msg']}", flush=True)
        return 0
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, anchor_name, e)
        raise


def _selftest_basic_pipeline() -> None:
    """v4 import-level selftest. Asserts:
      - v4 corridor-in regime: N=512, M=20000, V_CB=32.
      - d^2/(n log n) IN CORRIDOR ~ 1.32.
      - NOISY_FLIP_FRAC=0.35 (v4 relaxed from v3's 0.45).
      - listwise Round-2 mechanism operational.
      - Arms produce DIFFERENT retrieval sequences (META_RULE_AF).
    Fast (<10s)."""
    # v4 regime invariants.
    _frozen = {
        "N_DIM": (N_DIM, 512),
        "M_ITEMS": (M_ITEMS, 20000),
        "V_CB": (V_CB, 32),
        "NOISY_FLIP_FRAC": (NOISY_FLIP_FRAC, 0.35),
        "ROUND2_TOP_K": (ROUND2_TOP_K, 20),
        "MARGIN_TAU_ADAPTIVE_QUANTILE": (MARGIN_TAU_ADAPTIVE_QUANTILE, 0.50),
        "MARGIN_TAU_FIXED_CAP": (MARGIN_TAU_FIXED_CAP, 0.50),
        "REFUSE_TAU": (REFUSE_TAU, 0.25),
        "UTIL_ACCEPT_CORRECT": (UTIL_ACCEPT_CORRECT, 1.0),
        "UTIL_LISTWISE_ROUND2_CORRECT": (UTIL_LISTWISE_ROUND2_CORRECT, 0.9),
    }
    for name, (got, want) in _frozen.items():
        assert got == want, \
            f"SELFTEST_FAIL: v4-frozen invariant {name}={got} but v4 requires {want}"
    assert len(ARMS) == 3, f"SELFTEST_FAIL: ARMS len {len(ARMS)} != 3"
    assert ARMS[0] == "ARM_LISTWISE_ROUND2"
    assert ARMS[1] == "ARM_ARGMAX_SINGLESHOT"
    assert ARMS[2] == "ARM_ARGMAX_WITH_REFUSE"
    assert ANCHOR_BASE == "exp_cortex_task_analog_downstream_v4", \
        f"SELFTEST_FAIL: ANCHOR_BASE={ANCHOR_BASE}"

    # Corridor test: at N=512, M=20000: d^2/(n log n) = 1.32 (IN CORRIDOR).
    corr = compute_corridor_position(N_DIM, M_ITEMS)
    expected_ratio = (N_DIM * N_DIM) / (M_ITEMS * math.log(M_ITEMS))
    assert abs(corr["d2_over_n_logn"] - expected_ratio) < 1e-6, \
        f"SELFTEST_FAIL: corridor arithmetic wrong: computed " \
        f"{corr['d2_over_n_logn']} vs manual {expected_ratio}"
    assert corr["in_corridor"], \
        f"SELFTEST_FAIL: v4 regime NOT in corridor: " \
        f"d^2/(n log n)={corr['d2_over_n_logn']:.3f}"
    # Expected corridor position ~ 1.32 (per drill arithmetic).
    assert 1.30 <= corr["d2_over_n_logn"] <= 1.35, \
        f"SELFTEST_FAIL: expected d^2/(n log n) ~ 1.32; got " \
        f"{corr['d2_over_n_logn']:.3f}"

    # Tiny pipeline run (M=200 for quick selftest; still corridor-in with
    # M=200 since d^2/n = 512^2/200 = 1310 and 2 log M = 10.6, so ABOVE
    # corridor -- but we're only testing PIPELINE MECHANICS not corridor here).
    seed = 7
    _global_M = M_ITEMS
    _global_topk = ROUND2_TOP_K
    # Directly build tiny KB without changing globals.
    gen = torch.Generator()
    gen.manual_seed(seed)
    kb_keys = _bipolar_random((200, N_DIM), gen)
    kb_val_indices = torch.arange(200) % V_CB
    kb_val_indices = kb_val_indices[torch.randperm(200, generator=gen)]

    q_total = 6
    queries = torch.zeros(q_total, N_DIM, dtype=torch.float32)
    intent = torch.zeros(q_total, dtype=torch.long)
    true_val = torch.full((q_total,), -1, dtype=torch.long)
    # 2 clean + 2 noisy + 2 OOB.
    for i, idx in enumerate([3, 7]):
        queries[i] = kb_keys[idx]
        true_val[i] = int(kb_val_indices[idx])
    for i, idx in enumerate([11, 17]):
        q = kb_keys[idx].clone()
        n_flip = int(NOISY_FLIP_FRAC * N_DIM)
        flip_idx = torch.randperm(N_DIM, generator=gen)[:n_flip]
        q[flip_idx] = -q[flip_idx]
        queries[2 + i] = q
        intent[2 + i] = 1
        true_val[2 + i] = int(kb_val_indices[idx])
    for i in range(2):
        queries[4 + i] = _bipolar_random((N_DIM,), gen)
        intent[4 + i] = 2

    r_l = run_arm_listwise_round2(seed, queries, kb_keys, kb_val_indices,
                                  intent, true_val)
    r_s = run_arm_argmax_singleshot(seed, queries, kb_keys, kb_val_indices,
                                    intent, true_val)
    r_r = run_arm_argmax_with_refuse(seed, queries, kb_keys, kb_val_indices,
                                     intent, true_val)
    assert r_l["retrieval_sha256"] != r_s["retrieval_sha256"], \
        "META_RULE_AF: LISTWISE and SINGLESHOT bit-identical"
    assert r_l["retrieval_sha256"] != r_r["retrieval_sha256"], \
        "META_RULE_AF: LISTWISE and REFUSE bit-identical"
    for r in (r_l, r_s, r_r):
        assert 0.0 <= r["utility_norm"] <= 1.0, \
            f"utility_norm {r['utility_norm']} outside [0,1] for {r['arm']}"

    # Listwise value-marginalization sanity: given known sims + val_indices,
    # verify logsumexp per-class result.
    sims_test = torch.tensor([2.0, 1.5, 1.0, 0.5, 0.1])
    val_test = torch.tensor([0, 1, 0, 2, 1])
    pred_v = _listwise_round2_value_marginalization(
        sims_test, val_test, top_k=5)
    # Class 0: logsumexp(2.0, 1.0) = log(e^2+e^1) = log(10.11) = 2.313
    # Class 1: logsumexp(1.5, 0.1) = log(e^1.5+e^0.1) = log(5.59) = 1.720
    # Class 2: logsumexp(0.5) = 0.5
    # -> class 0 wins.
    assert pred_v == 0, \
        f"SELFTEST_FAIL: listwise value-marg pred={pred_v}; expected 0"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=ANCHOR_BASE)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--run-mode", choices=["smoke", "full", "self_test"],
                   default="smoke")
    p.add_argument("--anchor-name", type=str, default=ANCHOR_BASE)
    p.add_argument("--self-test", action="store_true",
                   help="Run import-level selftest only; no dispatch.")
    args = p.parse_args(argv)

    if args.self_test:
        _selftest_basic_pipeline()
        print("SELFTEST_OK", flush=True)
        return 0

    return _run_one_seed_wrapper(args.seed, args.run_mode, args.anchor_name)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            od = _output_dir_for(ANCHOR_BASE, "smoke")
            _write_crash_metrics(od, ANCHOR_BASE, e)
        except Exception:
            pass
        raise
