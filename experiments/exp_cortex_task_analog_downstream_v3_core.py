"""exp_cortex_task_analog_downstream_v3 CORE -- higher-noise regime revival.

REGIME-EXTENSION of v2b (commit 7345bbbbe) frozen infra. SOLE DIFF vs v2b =
raise NOISY_FLIP_FRAC 0.35 -> 0.45. Revival at high-noise regime per v2b
Skunkworks VET LOCKED revival criterion.

v1 (commit 1ae012b60): H3_gap = -0.167 MB (utility-artifact diagnosis).
v2 (commit ac201f6a6): CLARIFY=0.65 principled credit; predicted +0.08 to
    +0.12; actual -0.058 HARD_FAIL.
v2b (commit 7345bbbbe): multi-round empirical DV; predicted >= +0.05; actual
    -0.033 HARD_FAIL -> atom
    CORTEX_TASK_ANALOG_DOWNSTREAM_v2b_SMOKE_HONEST_NEGATIVE_MM_TENTATIVE.

v2b Skunkworks VET (task a1940529089318a75) LOCKED revival criterion:
    Revival requires: (a) higher-noise regime (flip >= 0.45), OR (b) new
    task class where CLARIFY adds value beyond argmax-restart.

v3 scope: option (a) -- higher-noise regime. ONE param change: bit-flip P
0.35 -> 0.45. All other params bit-identical to v2b.

Skunkworks Monte-Carlo prediction from v2b VET:
    At bit-flip P=0.45 -> cos = 1 - 2*0.45 = 0.10; SNR ~ 2.1-2.7x (down
    from v2b's ~8x at P=0.35).
    Prediction: INDIV argmax degrades MEANINGFULLY at this SNR; cortex
    CLARIFY-then-Round2 recovers where INDIV argmax fails.

Round-2 mechanics at v3 regime (THEORETICAL):
    remaining_flips = 0.45 * (1 - 0.30) = 0.315
    expected_cos(q_hint, target) = 1 - 2 * 0.315 = 0.37
    random-baseline (M=300, N=8192): sqrt(2*ln(300)/8192) ~ 0.037
    SNR at Round 2: 0.37 / 0.037 ~ 10.0x (down from v2b's 13.8x but
    still comfortably reliable at M=300).

Predict-then-check binding (PRE-COMMITTED; anti-drift):
    PREDICT: H3_gap >= +0.05 AND H3_gap / SEM >= +2.0 (positive sign flip
             vs v2b's -0.033).
    PASS -> candidate atom
        EMPIRICAL_CORTEX_COMPOSITION_HELPS_AT_HIGH_NOISE_REGIME_v3_MM_TENTATIVE
        (single-task arc REOPENS under noise-regime-conditional atom).
    MB   -> H3_gap in [+0.02, +0.05); inconclusive; needs FULL 3-seed cv.
    FAIL -> DEFINITIVE_NEGATIVE atom
        CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_EVEN_AT_HIGH_NOISE
        _v3_MM_STANDARD_close_arc.

Prereg: preregs/2026-07-04_exp_cortex_task_analog_downstream_v3.md

Anti-drift discipline (per today's 28+ Fix#28 hits):
    - ONLY parameter changed is bit-flip P (0.35 -> 0.45).
    - NO other tuning (utility function, Round-2 hint frac, tau values
      all v1-frozen bit-identical).
    - Prediction pre-committed BEFORE running.
    - If FAIL: honest-negative escalation atom, no re-tune.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    Identical rules to v2b (see v2b core module docstring). New v3 config
    invariants asserted in selftest: NOISY_FLIP_FRAC == 0.45.

Storage strategy: SHARDED (each M=300 KB item has its own key vector).

Compute architecture: (b) sequential-CPU with justification (per-query
cortex.forward pipeline; ~1-2s per arm at N=8192 M=300 30-query; total
wall <30s SMOKE).

ASCII-only. Windowless subprocess. Wrappers (_s7) dispatch single-seed runs
per chunked architecture Sec 13.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

from hdlab.cortex import Cortex, CortexConfig, CortexResponse
from hdlab.refuse_gate import apply_refuse

try:
    from experiments._cell_heartbeat import emit_heartbeat
except Exception:
    def emit_heartbeat(*args, **kwargs):
        return None


# ------------------------------ configuration --------------------------------

ANCHOR_BASE = "exp_cortex_task_analog_downstream_v3"

# CG-anchored constants (v1/v2/v2b-frozen; do NOT re-tune per anti-drift).
N_DIM = 8192                    # CITED@ hdlab/cortex.py:74 (CG floor).
V_CB = 1024
STM_K = 100
LTM_K = 1200
S_ROLES = 4
M_ITEMS = 300                   # HYPOTHESIZED@ v1 prereg (M/N=0.037 << 0.138).

REFUSE_TAU = 0.15               # v1-frozen a-priori.
CLARIFY_LOWER_TAU = 0.18
CLARIFY_UPPER_TAU = 0.42

# v3 SOLE DIFF vs v2b: raise NOISY_FLIP_FRAC 0.35 -> 0.45.
# At P=0.45: cos(query, target) = 1 - 2*0.45 = 0.10.
# random-baseline at M=300, N=8192: sqrt(2*ln(300)/8192) ~ 0.037.
# SNR at INDIV argmax: 0.10 / 0.037 ~ 2.7x (down from v2b's ~8.1x at P=0.35).
NOISY_FLIP_FRAC = 0.45          # v3 revival regime per Skunkworks VET.

# v2b-frozen Round-2 hint mechanics (unchanged).
# THEORETICAL@ under 45% flip + 30% flip-restoration:
#   remaining_flips = 0.45 * (1 - 0.30) = 0.315
#   expected_cos(q_hint, target) = 1 - 2 * 0.315 = 0.37
# vs random-baseline (M=300, N=8192): sqrt(2*ln(300)/8192) ~ 0.037
# Signal-to-noise at Round 2: 0.37 / 0.037 ~ 10.0x -> argmax should
# still reliably recover target item at M=300 at v3 regime.
ROUND2_HINT_FRAC_OF_FLIPPED = 0.30

# Query intent mix (v2b-frozen).
FULL_N_CLEAN = 30
FULL_N_NOISY = 30
FULL_N_OOB = 40
SMOKE_N_CLEAN = 10
SMOKE_N_NOISY = 10
SMOKE_N_OOB = 10

# v2b-frozen utility function (empirical multi-round; see module docstring).
UTIL_ACCEPT_CORRECT = 1.0
UTIL_ACCEPT_WRONG = 0.0
UTIL_CLARIFY_ROUND2_CORRECT = 0.9   # 10% retry cost
UTIL_CLARIFY_ROUND2_WRONG = 0.0
UTIL_REFUSE_TERMINAL = 0.0

ARMS = ["ARM_CORTEX_ON", "ARM_CORTEX_OFF", "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION"]


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


# ---------------------------- data generators --------------------------------


def _bipolar_random(shape, gen: torch.Generator) -> torch.Tensor:
    r = torch.rand(shape, generator=gen)
    return torch.where(r < 0.5,
                       torch.tensor(-1.0),
                       torch.tensor(1.0)).to(torch.float32)


def build_kb(seed: int, m_items: int
             ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build (kb_keys[M,N], kb_vals[M,N], kb_val_indices[M])."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    keys = _bipolar_random((m_items, N_DIM), gen)
    val_indices = torch.arange(m_items) % V_CB
    val_indices = val_indices[torch.randperm(m_items, generator=gen)]
    vals = _bipolar_random((m_items, N_DIM), gen)
    return keys, vals, val_indices


def build_queries(seed: int, kb_keys: torch.Tensor, kb_val_indices: torch.Tensor,
                  n_clean: int, n_noisy: int, n_oob: int
                  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor,
                             torch.Tensor]:
    """Build (queries[Q,N], intent_class[Q], true_val[Q], target_kb_idx[Q]).

    v2b/v3 target_kb_idx: index into kb_keys for the target item (-1 for OOB).
    Required for Round-2 hint reconstruction (partial-mask reveal).

    intent_class: 0=CLEAN, 1=NOISY, 2=OOB.
    """
    m_items = kb_keys.shape[0]
    gen = torch.Generator()
    gen.manual_seed(seed + 500)

    q_total = n_clean + n_noisy + n_oob
    queries = torch.zeros(q_total, N_DIM, dtype=torch.float32)
    intent = torch.zeros(q_total, dtype=torch.long)
    true_val = torch.full((q_total,), -1, dtype=torch.long)
    target_kb_idx = torch.full((q_total,), -1, dtype=torch.long)

    # CLEAN: sample n_clean items at random; queries = keys[items].
    clean_items = torch.randperm(m_items, generator=gen)[:n_clean]
    for i, idx in enumerate(clean_items.tolist()):
        queries[i] = kb_keys[idx]
        intent[i] = 0
        true_val[i] = int(kb_val_indices[idx])
        target_kb_idx[i] = idx

    # NOISY: sample n_noisy items; flip NOISY_FLIP_FRAC of coordinates.
    noisy_items = torch.randperm(m_items, generator=gen)[:n_noisy]
    for i, idx in enumerate(noisy_items.tolist()):
        q = kb_keys[idx].clone()
        n_flip = int(NOISY_FLIP_FRAC * N_DIM)
        flip_idx = torch.randperm(N_DIM, generator=gen)[:n_flip]
        q[flip_idx] = -q[flip_idx]
        queries[n_clean + i] = q
        intent[n_clean + i] = 1
        true_val[n_clean + i] = int(kb_val_indices[idx])
        target_kb_idx[n_clean + i] = idx

    # OOB: random bipolar queries; no target.
    for i in range(n_oob):
        queries[n_clean + n_noisy + i] = _bipolar_random((N_DIM,), gen)
        intent[n_clean + n_noisy + i] = 2
        true_val[n_clean + n_noisy + i] = -1
        target_kb_idx[n_clean + n_noisy + i] = -1

    return queries, intent, true_val, target_kb_idx


# --------------------------- Round-2 mechanics (v2b-frozen) ------------------


def _round2_hint_argmax(q0: torch.Tensor, target_key: torch.Tensor,
                        kb_keys_normed: torch.Tensor,
                        hint_frac_of_flipped: float,
                        gen: torch.Generator) -> int:
    """Round-2 retrieval with partial-mask hint (v2b mechanics; unchanged).

    Reveal hint_frac_of_flipped fraction of positions where q0 disagrees
    with target_key; set those positions to target's value. Argmax over
    kb_keys_normed with the corrected query. Returns predicted kb_item idx.
    """
    disagree = (q0 != target_key).nonzero(as_tuple=True)[0]
    n_disagree = int(disagree.shape[0])
    if n_disagree == 0:
        q_hint = q0
    else:
        n_reveal = max(1, int(round(hint_frac_of_flipped * n_disagree)))
        perm = torch.randperm(n_disagree, generator=gen)[:n_reveal]
        reveal_pos = disagree[perm]
        q_hint = q0.clone()
        q_hint[reveal_pos] = target_key[reveal_pos]

    q_n = q_hint / q_hint.norm().clamp_min(1e-9)
    sims = kb_keys_normed @ q_n
    return int(torch.argmax(sims).item())


# ------------------------ per-arm implementation -----------------------------


def _cortex_for(seed: int) -> Cortex:
    cfg = CortexConfig(
        n_dim=N_DIM,
        v_cb=V_CB,
        stm_k=STM_K,
        ltm_k=LTM_K,
        n_roles=S_ROLES,
        refuse_gate_accept_tau=REFUSE_TAU,
        clarify_gate_lower_tau=CLARIFY_LOWER_TAU,
        clarify_gate_upper_tau=CLARIFY_UPPER_TAU,
        enable_role_slot_summary=False,
        noise_channel_enabled=False,
        seed=seed,
    )
    return Cortex(cfg)


def run_arm_cortex_on(seed: int, queries: torch.Tensor,
                      kb_keys: torch.Tensor, kb_vals: torch.Tensor,
                      kb_val_indices: torch.Tensor,
                      intent: torch.Tensor, true_val: torch.Tensor,
                      target_kb_idx: torch.Tensor
                      ) -> Dict[str, object]:
    """ARM_CORTEX_ON: full cortex.forward pipeline + Round-2 on CLARIFY."""
    cx = _cortex_for(seed)
    q_total = queries.shape[0]

    k32 = kb_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    r2_gen = torch.Generator()
    r2_gen.manual_seed(seed + 9001)

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    per_query_round2_success = []
    retrieval_bytes = bytearray()

    n_clarify_round2_correct = 0
    n_clarify_round2_wrong = 0
    n_clarify_total = 0

    for i in range(q_total):
        resp = cx.forward(queries[i], context_keys=kb_keys, context_vals=kb_vals)
        pred_item = resp.predicted_val_idx
        if 0 <= pred_item < kb_val_indices.shape[0]:
            pred_val = int(kb_val_indices[pred_item])
        else:
            pred_val = -1

        round2_success = 0
        util = 0.0

        route = resp.route
        if route == "ACCEPT":
            if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
                util = UTIL_ACCEPT_CORRECT
            else:
                util = UTIL_ACCEPT_WRONG
            round2_success = -1
        elif route == "CLARIFY":
            n_clarify_total += 1
            tgt_idx = int(target_kb_idx[i])
            if tgt_idx < 0:
                util = UTIL_CLARIFY_ROUND2_WRONG
                round2_success = 0
                n_clarify_round2_wrong += 1
            else:
                target_key = kb_keys[tgt_idx]
                r2_pred_item = _round2_hint_argmax(
                    queries[i], target_key, k_normed,
                    ROUND2_HINT_FRAC_OF_FLIPPED, r2_gen)
                r2_pred_val = int(kb_val_indices[r2_pred_item])
                if r2_pred_val == int(true_val[i]):
                    util = UTIL_CLARIFY_ROUND2_CORRECT
                    round2_success = 1
                    n_clarify_round2_correct += 1
                else:
                    util = UTIL_CLARIFY_ROUND2_WRONG
                    round2_success = 0
                    n_clarify_round2_wrong += 1
        else:  # REFUSE
            util = UTIL_REFUSE_TERMINAL
            round2_success = -1

        per_query_util.append(util)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(float(resp.confidence))
        per_query_round2_success.append(round2_success)
        retrieval_bytes.extend(
            f"{route}|{pred_val}|{round2_success}|".encode("utf-8"))

    n_accept = sum(1 for r in per_query_route if r == "ACCEPT")
    n_clarify = sum(1 for r in per_query_route if r == "CLARIFY")
    n_refuse = sum(1 for r in per_query_route if r == "REFUSE")

    return {
        "arm": "ARM_CORTEX_ON",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": n_accept,
        "n_clarify": n_clarify,
        "n_refuse": n_refuse,
        "n_clarify_round2_correct": n_clarify_round2_correct,
        "n_clarify_round2_wrong": n_clarify_round2_wrong,
        "clarify_round2_success_rate":
            float(n_clarify_round2_correct) / max(1, n_clarify_total),
        "confidence_mean": float(np.mean(per_query_conf)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "per_query_round2_success": per_query_round2_success,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


def run_arm_cortex_off(seed: int, queries: torch.Tensor,
                       kb_keys: torch.Tensor, kb_vals: torch.Tensor,
                       kb_val_indices: torch.Tensor,
                       intent: torch.Tensor, true_val: torch.Tensor,
                       target_kb_idx: torch.Tensor
                       ) -> Dict[str, object]:
    """ARM_CORTEX_OFF: raw argmax; ALWAYS ACCEPT (no gates; no Round 2)."""
    q_total = queries.shape[0]
    k32 = kb_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    retrieval_bytes = bytearray()

    for i in range(q_total):
        q = queries[i].to(torch.float32)
        q_n = q / q.norm().clamp_min(1e-9)
        sims = k_normed @ q_n
        pred_item = int(torch.argmax(sims).item())
        max_sim = float(sims.max())
        pred_val = int(kb_val_indices[pred_item])
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
        "arm": "ARM_CORTEX_OFF",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": q_total,
        "n_clarify": 0,
        "n_refuse": 0,
        "confidence_mean": float(np.mean(per_query_conf)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


def run_arm_individual_no_composition(
        seed: int, queries: torch.Tensor,
        kb_keys: torch.Tensor, kb_vals: torch.Tensor,
        kb_val_indices: torch.Tensor,
        intent: torch.Tensor, true_val: torch.Tensor,
        target_kb_idx: torch.Tensor) -> Dict[str, object]:
    """ARM_INDIV: argmax + apply_refuse only. No CLARIFY, no Round 2."""
    q_total = queries.shape[0]
    k32 = kb_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    retrieval_bytes = bytearray()

    for i in range(q_total):
        q = queries[i].to(torch.float32)
        q_n = q / q.norm().clamp_min(1e-9)
        sims = k_normed @ q_n
        pred_item = int(torch.argmax(sims).item())
        max_sim = float(sims.max())
        pred_val = int(kb_val_indices[pred_item])
        accept = apply_refuse(max_sim, REFUSE_TAU)
        route = "ACCEPT" if accept else "REFUSE"
        if route == "ACCEPT":
            if int(pred_val) == int(true_val[i]) and int(true_val[i]) >= 0:
                util = UTIL_ACCEPT_CORRECT
            else:
                util = UTIL_ACCEPT_WRONG
        else:
            util = UTIL_REFUSE_TERMINAL
        per_query_util.append(util)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(max_sim)
        retrieval_bytes.extend(f"{route}|{pred_val}|-1|".encode("utf-8"))

    n_accept = sum(1 for r in per_query_route if r == "ACCEPT")
    n_refuse = sum(1 for r in per_query_route if r == "REFUSE")

    return {
        "arm": "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": float(np.mean(per_query_util)),
        "n_accept": n_accept,
        "n_clarify": 0,
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

    kb_keys, kb_vals, kb_val_indices = build_kb(seed, M_ITEMS)
    queries, intent, true_val, target_kb_idx = build_queries(
        seed, kb_keys, kb_val_indices, n_clean, n_noisy, n_oob)

    print(f"[seed={seed}] arms starting, n_queries={queries.shape[0]} "
          f"({n_clean}/{n_noisy}/{n_oob}) flip_frac={NOISY_FLIP_FRAC}",
          flush=True)

    per_arm_results = {}
    per_arm_failure = {}
    for arm_idx, arm_name in enumerate(ARMS):
        try:
            if arm_name == "ARM_CORTEX_ON":
                r = run_arm_cortex_on(seed, queries, kb_keys, kb_vals,
                                      kb_val_indices, intent, true_val,
                                      target_kb_idx)
            elif arm_name == "ARM_CORTEX_OFF":
                r = run_arm_cortex_off(seed, queries, kb_keys, kb_vals,
                                       kb_val_indices, intent, true_val,
                                       target_kb_idx)
            else:
                r = run_arm_individual_no_composition(
                    seed, queries, kb_keys, kb_vals, kb_val_indices,
                    intent, true_val, target_kb_idx)
            per_arm_results[arm_name] = r
            emit_heartbeat(output_dir, unit_idx=arm_idx, total_units=len(ARMS),
                           elapsed_s=time.perf_counter() - t0)
            r2_str = ""
            if "clarify_round2_success_rate" in r:
                r2_str = (f" r2_success={r.get('n_clarify_round2_correct',0)}/"
                          f"{r.get('n_clarify_round2_correct',0)+r.get('n_clarify_round2_wrong',0)}")
            print(f"[seed={seed}] {arm_name} norm_util={r['utility_norm']:.4f} "
                  f"n_accept={r['n_accept']} n_clarify={r['n_clarify']} "
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


def compute_verdict(per_seed: Dict[int, dict], run_mode: str) -> Dict[str, object]:
    """Predict-then-check verdict on H3_gap at higher-noise regime.

    PRE-COMMITTED prediction: H3_gap >= +0.05 AND H3_gap / SEM >= +2.0.
    (Same numeric band as v2b; v3 tests it AT HIGHER-NOISE regime.)
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

    on_util = per_arm_agg["ARM_CORTEX_ON"]["mean"]
    off_util = per_arm_agg["ARM_CORTEX_OFF"]["mean"]
    indiv_util = per_arm_agg["ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION"]["mean"]

    h1_gap = on_util - off_util
    h3_gap = on_util - indiv_util
    on_cv = per_arm_agg["ARM_CORTEX_ON"]["cv"]

    on_per_query = []
    indiv_per_query = []
    for s in seeds:
        r_on = per_seed[s].get("per_arm", {}).get("ARM_CORTEX_ON")
        r_i = per_seed[s].get("per_arm", {}).get(
            "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION")
        if r_on is not None and r_i is not None:
            on_per_query.extend(r_on.get("per_query_util", []))
            indiv_per_query.extend(r_i.get("per_query_util", []))
    if on_per_query and indiv_per_query and len(on_per_query) == len(indiv_per_query):
        diffs = np.array(on_per_query) - np.array(indiv_per_query)
        if len(diffs) > 1:
            gap_sem = float(np.std(diffs, ddof=1) / np.sqrt(len(diffs)))
        else:
            gap_sem = float("nan")
    else:
        gap_sem = float("nan")

    gap_over_sem = h3_gap / gap_sem if gap_sem and gap_sem > 0 else float("nan")

    arms_differ_all = all(per_seed[s].get("arms_differ_verified", False)
                          for s in seeds)

    baseline_in_band = 0.05 < off_util < 0.95
    on_in_band = 0.05 < on_util < 0.95

    reasons = []
    verdict = "HARD_PASS"

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
            f"META_RULE_AG: baseline off_util={off_util:.4f} outside [0.05, 0.95]")

    # PRIMARY predict-then-check gate: H3_gap band (v3 binding; same as v2b).
    # PASS: H3_gap >= +0.05 AND gap/SEM >= +2.0
    # MB:   +0.02 <= H3_gap < +0.05
    # FAIL: H3_gap < +0.02  OR  (H3_gap >= +0.05 AND gap/SEM < +2.0)
    if h3_gap < 0.02:
        verdict = "HARD_FAIL"
        reasons.append(
            f"H3_gap={h3_gap:.4f} < +0.02 (composition does not help even at "
            f"high-noise regime P=0.45; predict-then-check FAIL; "
            f"DEFINITIVE_NEGATIVE close-arc candidate)")
    elif h3_gap < 0.05:
        if verdict == "HARD_PASS":
            verdict = "MIDDLE_BAND"
        reasons.append(
            f"H3_gap={h3_gap:.4f} in MB band [+0.02, +0.05); marginal cortex "
            f"advantage insufficient for predict-then-check PASS")
    else:
        if not np.isnan(gap_over_sem) and gap_over_sem < 2.0:
            verdict = "HARD_FAIL"
            reasons.append(
                f"H3_gap={h3_gap:.4f} passes point but gap/SEM={gap_over_sem:.2f} "
                f"< 2.0 (not statistically distinguishable from 0)")

    reasons.append(
        f"H1_gap={h1_gap:.4f} (secondary; not a v3 gate)")

    if run_mode == "full":
        if on_cv >= 0.30:
            verdict = "HARD_FAIL"
            reasons.append(f"cortex_on cv={on_cv:.4f} >= 0.30")
        elif on_cv >= 0.20:
            if verdict == "HARD_PASS":
                verdict = "MIDDLE_BAND"
            reasons.append(f"cortex_on cv={on_cv:.4f} in MB band [0.20, 0.30]")

    verdict_msg = (
        f"{verdict} | H3_gap={h3_gap:.4f} gap/SEM={gap_over_sem:.2f} | "
        f"H1_gap={h1_gap:.4f} (secondary) | "
        f"ON={on_util:.4f} OFF={off_util:.4f} INDIV={indiv_util:.4f} | "
        f"cv_ON={on_cv:.4f} | arms_differ={arms_differ_all} | "
        f"cardinality={completed_arms}/{expected_n_units} | "
        f"flip_frac={NOISY_FLIP_FRAC} | "
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
        "cortex_on_in_band": on_in_band,
        "reasons": reasons,
    }


# ------------------------------ main entrypoint -----------------------------


def _run_one_seed_wrapper(seed: int, run_mode: str, anchor_name: str) -> int:
    output_dir = _output_dir_for(anchor_name, run_mode)
    t0 = time.perf_counter()
    try:
        _write_start_marker(output_dir, anchor_name, run_mode,
                            expected_n_units=len(ARMS))
        per_seed_result = run_one_seed(seed, run_mode, output_dir, t0)
        elapsed = time.perf_counter() - t0
        verdict_info = compute_verdict({seed: per_seed_result}, run_mode)
        metrics = {
            "anchor_name": anchor_name,
            "run_mode": run_mode,
            "seed": seed,
            "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "host": platform.node(),
            "config": {
                "N_DIM": N_DIM, "V_CB": V_CB, "M_ITEMS": M_ITEMS,
                "STM_K": STM_K, "LTM_K": LTM_K, "S_ROLES": S_ROLES,
                "REFUSE_TAU": REFUSE_TAU,
                "CLARIFY_LOWER_TAU": CLARIFY_LOWER_TAU,
                "CLARIFY_UPPER_TAU": CLARIFY_UPPER_TAU,
                "NOISY_FLIP_FRAC": NOISY_FLIP_FRAC,
                "ROUND2_HINT_FRAC_OF_FLIPPED": ROUND2_HINT_FRAC_OF_FLIPPED,
                "UTIL_ACCEPT_CORRECT": UTIL_ACCEPT_CORRECT,
                "UTIL_ACCEPT_WRONG": UTIL_ACCEPT_WRONG,
                "UTIL_CLARIFY_ROUND2_CORRECT": UTIL_CLARIFY_ROUND2_CORRECT,
                "UTIL_CLARIFY_ROUND2_WRONG": UTIL_CLARIFY_ROUND2_WRONG,
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
            "cortex_on_in_band": verdict_info["cortex_on_in_band"],
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
    """v3 import-level selftest. Asserts:
      - v3 SOLE DIFF: NOISY_FLIP_FRAC == 0.45.
      - v2b-frozen utility + Round-2 hint frac + tau values.
      - v1-frozen base config invariants.
      - 3 arms; anchor is v3.
      - Tiny pipeline runs; utilities in [0, 1].
      - Round-2 hint mechanics: 45% flip + 30% flip-restoration recovers
        target at M=20 (still SNR-safe at v3 regime).
    Fast (<5s)."""
    # v3 SOLE DIFF: raise flip fraction.
    assert NOISY_FLIP_FRAC == 0.45, \
        f"SELFTEST_FAIL: NOISY_FLIP_FRAC={NOISY_FLIP_FRAC} v3 requires 0.45 " \
        "(v3 revival regime per v2b Skunkworks VET)"
    # v2b-frozen invariants: multi-round empirical utility function.
    assert UTIL_ACCEPT_CORRECT == 1.0, \
        f"SELFTEST_FAIL: UTIL_ACCEPT_CORRECT={UTIL_ACCEPT_CORRECT} v3 requires 1.0"
    assert UTIL_ACCEPT_WRONG == 0.0, \
        f"SELFTEST_FAIL: UTIL_ACCEPT_WRONG={UTIL_ACCEPT_WRONG} v3 requires 0.0"
    assert UTIL_CLARIFY_ROUND2_CORRECT == 0.9, \
        f"SELFTEST_FAIL: UTIL_CLARIFY_ROUND2_CORRECT={UTIL_CLARIFY_ROUND2_CORRECT} v3 requires 0.9"
    assert UTIL_CLARIFY_ROUND2_WRONG == 0.0, \
        f"SELFTEST_FAIL: UTIL_CLARIFY_ROUND2_WRONG={UTIL_CLARIFY_ROUND2_WRONG} v3 requires 0.0"
    assert UTIL_REFUSE_TERMINAL == 0.0, \
        f"SELFTEST_FAIL: UTIL_REFUSE_TERMINAL={UTIL_REFUSE_TERMINAL} v3 requires 0.0"
    assert ROUND2_HINT_FRAC_OF_FLIPPED == 0.30, \
        f"SELFTEST_FAIL: ROUND2_HINT_FRAC_OF_FLIPPED={ROUND2_HINT_FRAC_OF_FLIPPED} v3 requires 0.30 (frozen a-priori)"
    # v1-frozen invariants: nothing else re-tuned.
    _frozen = {
        "N_DIM": (N_DIM, 8192),
        "M_ITEMS": (M_ITEMS, 300),
        "REFUSE_TAU": (REFUSE_TAU, 0.15),
        "CLARIFY_LOWER_TAU": (CLARIFY_LOWER_TAU, 0.18),
        "CLARIFY_UPPER_TAU": (CLARIFY_UPPER_TAU, 0.42),
        "V_CB": (V_CB, 1024),
        "STM_K": (STM_K, 100),
        "LTM_K": (LTM_K, 1200),
        "S_ROLES": (S_ROLES, 4),
    }
    for name, (got, want) in _frozen.items():
        assert got == want, \
            f"SELFTEST_FAIL: v1-frozen invariant {name}={got} but v3 requires {want}"
    assert len(ARMS) == 3 and \
        ARMS[0] == "ARM_CORTEX_ON" and \
        ARMS[1] == "ARM_CORTEX_OFF" and \
        ARMS[2] == "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION", \
        f"SELFTEST_FAIL: ARMS mismatch: {ARMS}"
    assert ANCHOR_BASE == "exp_cortex_task_analog_downstream_v3", \
        f"SELFTEST_FAIL: ANCHOR_BASE={ANCHOR_BASE} but v3 requires " \
        "'exp_cortex_task_analog_downstream_v3'"

    # Tiny pipeline run.
    seed = 7
    kb_keys, kb_vals, kb_val_indices = build_kb(seed, 20)
    queries, intent, true_val, target_kb_idx = build_queries(
        seed, kb_keys, kb_val_indices, 3, 3, 4)
    r_on = run_arm_cortex_on(seed, queries, kb_keys, kb_vals,
                             kb_val_indices, intent, true_val, target_kb_idx)
    r_off = run_arm_cortex_off(seed, queries, kb_keys, kb_vals,
                               kb_val_indices, intent, true_val, target_kb_idx)
    r_indiv = run_arm_individual_no_composition(
        seed, queries, kb_keys, kb_vals, kb_val_indices, intent, true_val,
        target_kb_idx)
    assert r_on["retrieval_sha256"] != r_off["retrieval_sha256"], \
        "META_RULE_AF: ON and OFF route+pred sequence identical"
    for r in (r_on, r_off, r_indiv):
        assert 0.0 <= r["utility_norm"] <= 1.0, \
            f"utility_norm {r['utility_norm']} outside [0,1] for {r['arm']}"

    # Round-2 hint recovery sanity at v3 regime: 45% flip + 30% hint restore.
    # THEORETICAL@ expected_cos = 1 - 2*(0.45*0.7) = 0.37; at M=20 N=8192
    # random-baseline cos ~ 0.027; SNR ~ 13.7x -> still reliable.
    tgt_idx = 5
    target_key = kb_keys[tgt_idx]
    n_flip = int(NOISY_FLIP_FRAC * N_DIM)
    gen = torch.Generator()
    gen.manual_seed(999)
    flip_pos = torch.randperm(N_DIM, generator=gen)[:n_flip]
    q0 = target_key.clone()
    q0[flip_pos] = -q0[flip_pos]
    k_normed = kb_keys / kb_keys.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    r2_gen = torch.Generator()
    r2_gen.manual_seed(1234)
    r2_pred = _round2_hint_argmax(q0, target_key, k_normed,
                                  ROUND2_HINT_FRAC_OF_FLIPPED, r2_gen)
    assert r2_pred == tgt_idx, \
        f"SELFTEST_FAIL: Round-2 hint retrieval predicted item {r2_pred} " \
        f"but target was {tgt_idx} (M=20 N=8192 45% flip + 30% hint-restore; " \
        f"expected reliable recovery at SNR ~13.7x)"


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
