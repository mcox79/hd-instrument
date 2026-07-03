"""exp_cortex_task_analog_downstream_v2 CORE -- principled CLARIFY credit fork.

REGIME-EXTENSION of v1 (commit 1ae012b60 frozen config). SOLE DIFF vs v1 =
UTIL_CLARIFY payoff: 0.0 -> 0.65 (PRINCIPLED_CLARIFY_CREDIT).

Derivation (from Research 2x-drill 2026-07-03 authority note
notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md):
    U(CLARIFY) = P(correct|retry) * payoff_retry - retry_cost
               = 0.85 * 1.0 - 0.20 = +0.65
    (P_retry=0.85 CITED@ SpeakRL/ClarEval hint-augmented retry empirics;
     retry_cost=0.20 CITED@ production dialogue turn-cost calibration 15-25%.)

v1 CLARIFY=0.0 was decision-theoretically zero-credited under a confusable-
argmax regime -> biases against CLARIFY-emitting arms (Skunkworks
VET a9c698659626b3521 utility-artifact diagnosis). v2 credits CLARIFY at
principled Bayesian value-of-information rate.

Claim class: SEPARATE task-utility claim under corrected payoff. The
integration-fidelity CG at atom #51 (composed pipeline reproduces primitive
numbers) stands UNCHANGED. This cell only tests: does the composed pipeline
deliver marginal task-utility lift on THIS utility function shape.

Prereg: preregs/2026-07-04_exp_cortex_task_analog_downstream_v2.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate via SHA256 hash of per-query retrieval
  vectors across arms (META_RULE_AF)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "gating-utility metric; no capacity noise floor at this M/N"
- baseline_in_band verified at smoke: 0.05 < ARM_CORTEX_OFF norm_util < 0.95
- discriminator survives scale: smoke at FULL N_DIM=8192 M=300 with reduced
  N_queries=30; discriminator is per-query gating (scale-invariant in queries)
- HARD_PASS strictly above floor + 5% band-width: HP gap >= 0.10 (5% band = 0.005)
- HP_SCOPE: {ARM_CORTEX_ON: [FR1-4], ARM_CORTEX_OFF: [FR2-baseline-refutation],
  ARM_INDIV: [FR3-composition-partial]}
- cardinality_ok: EXPECTED_N_UNITS = n_arms * n_seeds
- per-unit failure-class instrumentation (specific exception class + failure_class)
- calibration_check: default_ok_for_this_regime (fixed a-priori tau values)
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Storage strategy: SHARDED (inherited from M1.6 chunked_attention_readout;
each of M=300 KB items has its own key vector).

Compute architecture: (b) sequential-CPU with justification (task IS cortex
forward pipeline; ~5s per arm-seed; wall <60s total; under batching threshold).

ASCII-only. Windowless subprocess. Wrappers (`_s7`, `_s13`, `_s19`) dispatch
single-seed runs per chunked architecture §13.
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

ANCHOR_BASE = "exp_cortex_task_analog_downstream_v2"

# CG-anchored constants
N_DIM = 8192                    # CITED@ hdlab/cortex.py:74 (CG floor)
V_CB = 1024
STM_K = 100
LTM_K = 1200
S_ROLES = 4
M_ITEMS = 300                   # HYPOTHESIZED@ prereg (M/N=0.037 << 0.138)

REFUSE_TAU = 0.15               # HYPOTHESIZED@ prereg (fixed a-priori)
CLARIFY_LOWER_TAU = 0.18
CLARIFY_UPPER_TAU = 0.42
# NOISY_FLIP_FRAC: fraction of bipolar coordinates to flip. cos = 1 - 2*P.
# P=0.35 -> cos=0.30 (center of CLARIFY zone [0.18, 0.42]). Chosen to make
# noisy queries land in CLARIFY zone so composition-lift (H3) can fire.
NOISY_FLIP_FRAC = 0.35          # HYPOTHESIZED@ prereg (cos=0.30 target)

# Query intent mix
FULL_N_CLEAN = 30
FULL_N_NOISY = 30
FULL_N_OOB = 40
SMOKE_N_CLEAN = 10
SMOKE_N_NOISY = 10
SMOKE_N_OOB = 10

# Task utility payoff
UTIL_ACCEPT_CORRECT = 1.0
UTIL_ACCEPT_WRONG = -1.0
UTIL_REFUSE_OOB = 0.5
UTIL_REFUSE_INKB = -0.5
# PRINCIPLED_CLARIFY_CREDIT (v2 sole diff vs v1):
# U(CLARIFY) = P(correct|retry) * payoff_retry - retry_cost
#            = 0.85 * 1.0 - 0.20 = +0.65
# Derivation cited in module docstring + prereg. DO NOT TUNE: predict-then-check
# discipline requires this constant frozen at derivation value; changing it
# invalidates the pre-committed prediction band.
UTIL_CLARIFY = 0.65

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
    """Build (kb_keys[M,N], kb_vals[M,N], kb_val_indices[M]) KB tape.

    - Each of M items has a random bipolar key and a distinct val_idx in [0,V_CB).
      HYPOTHESIZED: substrate-KB-analog where each stored fact has a role-cue
      (key) and answer-index (val_idx into codebook).
    """
    gen = torch.Generator()
    gen.manual_seed(seed)
    keys = _bipolar_random((m_items, N_DIM), gen)
    # val_indices: distinct integers into V_CB (with wrap if m_items > V_CB)
    val_indices = torch.arange(m_items) % V_CB
    val_indices = val_indices[torch.randperm(m_items, generator=gen)]
    # kb_vals: distinct bipolar vectors per item (codebook-space readout)
    vals = _bipolar_random((m_items, N_DIM), gen)
    return keys, vals, val_indices


def build_queries(seed: int, kb_keys: torch.Tensor, kb_val_indices: torch.Tensor,
                  n_clean: int, n_noisy: int, n_oob: int
                  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build (queries[Q,N], intent_class[Q], true_val_idx[Q]).

    intent_class: 0=CLEAN, 1=NOISY, 2=OOB.
    true_val_idx: for CLEAN/NOISY = kb_val_indices[matched item];
                  for OOB       = -1 (no correct answer).
    """
    m_items = kb_keys.shape[0]
    gen = torch.Generator()
    gen.manual_seed(seed + 500)

    q_total = n_clean + n_noisy + n_oob
    queries = torch.zeros(q_total, N_DIM, dtype=torch.float32)
    intent = torch.zeros(q_total, dtype=torch.long)
    true_val = torch.full((q_total,), -1, dtype=torch.long)

    # CLEAN: sample n_clean items at random; queries = keys[items] (exact match)
    clean_items = torch.randperm(m_items, generator=gen)[:n_clean]
    for i, idx in enumerate(clean_items.tolist()):
        queries[i] = kb_keys[idx]
        intent[i] = 0
        true_val[i] = int(kb_val_indices[idx])

    # NOISY: sample n_noisy items; flip NOISY_FLIP_FRAC of coordinates.
    # This yields cosine ~ 1 - 2 * NOISY_FLIP_FRAC (deterministic geometry
    # landing in CLARIFY zone; Gaussian sigma-based degradation does NOT push
    # cosine below CLARIFY_UPPER at practical sigma per prior smoke iter).
    noisy_items = torch.randperm(m_items, generator=gen)[:n_noisy]
    for i, idx in enumerate(noisy_items.tolist()):
        q = kb_keys[idx].clone()
        n_flip = int(NOISY_FLIP_FRAC * N_DIM)
        flip_idx = torch.randperm(N_DIM, generator=gen)[:n_flip]
        q[flip_idx] = -q[flip_idx]
        queries[n_clean + i] = q
        intent[n_clean + i] = 1
        true_val[n_clean + i] = int(kb_val_indices[idx])

    # OOB: random bipolar queries; no match in KB
    for i in range(n_oob):
        queries[n_clean + n_noisy + i] = _bipolar_random((N_DIM,), gen)
        intent[n_clean + n_noisy + i] = 2
        true_val[n_clean + n_noisy + i] = -1

    return queries, intent, true_val


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


def _score_utility(route: str, predicted_val: int, true_val: int,
                   intent_class: int) -> float:
    """Task utility per query given a (route, predicted_val, true_val, intent)."""
    is_oob = (intent_class == 2)
    if route == "ACCEPT":
        if is_oob:
            return UTIL_ACCEPT_WRONG            # OOB accepted = always wrong
        if int(predicted_val) == int(true_val):
            return UTIL_ACCEPT_CORRECT
        return UTIL_ACCEPT_WRONG
    if route == "REFUSE":
        if is_oob:
            return UTIL_REFUSE_OOB              # correct refusal
        return UTIL_REFUSE_INKB                 # wrongly refused an in-KB query
    # CLARIFY
    return UTIL_CLARIFY


def run_arm_cortex_on(seed: int, queries: torch.Tensor,
                      kb_keys: torch.Tensor, kb_vals: torch.Tensor,
                      kb_val_indices: torch.Tensor,
                      intent: torch.Tensor, true_val: torch.Tensor
                      ) -> Dict[str, object]:
    """ARM_CORTEX_ON: full cortex.forward pipeline."""
    cx = _cortex_for(seed)
    q_total = queries.shape[0]

    per_query_util = []
    per_query_route = []
    per_query_pred = []
    per_query_conf = []
    retrieval_bytes = bytearray()

    for i in range(q_total):
        resp = cx.forward(queries[i], context_keys=kb_keys, context_vals=kb_vals)
        # Map predicted_val_idx (into M-item tape) to true val-codebook idx
        # via kb_val_indices
        pred_item = resp.predicted_val_idx
        if 0 <= pred_item < kb_val_indices.shape[0]:
            pred_val = int(kb_val_indices[pred_item])
        else:
            pred_val = -1
        u = _score_utility(resp.route, pred_val, int(true_val[i]), int(intent[i]))
        per_query_util.append(u)
        per_query_route.append(resp.route)
        per_query_pred.append(pred_val)
        per_query_conf.append(float(resp.confidence))
        # AF-discriminator bytes: (route, pred_val) tuple per query. This is
        # the arm's actual decision signal; retrieval vector alone can collide
        # across arms that share argmax logic but differ in gating.
        retrieval_bytes.extend(f"{resp.route}|{pred_val}|".encode("utf-8"))

    n_accept = sum(1 for r in per_query_route if r == "ACCEPT")
    n_clarify = sum(1 for r in per_query_route if r == "CLARIFY")
    n_refuse = sum(1 for r in per_query_route if r == "REFUSE")

    return {
        "arm": "ARM_CORTEX_ON",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": (float(np.mean(per_query_util)) + 1.0) / 2.0,
        "n_accept": n_accept,
        "n_clarify": n_clarify,
        "n_refuse": n_refuse,
        "confidence_mean": float(np.mean(per_query_conf)),
        "per_query_route": per_query_route,
        "per_query_util": per_query_util,
        "retrieval_sha256": hashlib.sha256(bytes(retrieval_bytes)).hexdigest(),
    }


def run_arm_cortex_off(seed: int, queries: torch.Tensor,
                       kb_keys: torch.Tensor, kb_vals: torch.Tensor,
                       kb_val_indices: torch.Tensor,
                       intent: torch.Tensor, true_val: torch.Tensor
                       ) -> Dict[str, object]:
    """ARM_CORTEX_OFF: raw argmax retrieval; ALWAYS ACCEPT (no gates)."""
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
        route = "ACCEPT"                        # baseline always accepts
        u = _score_utility(route, pred_val, int(true_val[i]), int(intent[i]))
        per_query_util.append(u)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(max_sim)
        # AF-discriminator bytes: (route, pred_val) tuple per query
        retrieval_bytes.extend(f"{route}|{pred_val}|".encode("utf-8"))

    return {
        "arm": "ARM_CORTEX_OFF",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": (float(np.mean(per_query_util)) + 1.0) / 2.0,
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
        intent: torch.Tensor, true_val: torch.Tensor) -> Dict[str, object]:
    """ARM_INDIV: argmax retrieval + apply_refuse standalone (no clarify-gate,
    no facade composition). Isolates: composition of gates > single gate."""
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
        # INDIVIDUAL primitive: only refuse-gate, no clarify-gate composition
        accept = apply_refuse(max_sim, REFUSE_TAU)
        route = "ACCEPT" if accept else "REFUSE"
        u = _score_utility(route, pred_val, int(true_val[i]), int(intent[i]))
        per_query_util.append(u)
        per_query_route.append(route)
        per_query_pred.append(pred_val)
        per_query_conf.append(max_sim)
        # AF-discriminator bytes: (route, pred_val) tuple per query
        retrieval_bytes.extend(f"{route}|{pred_val}|".encode("utf-8"))

    n_accept = sum(1 for r in per_query_route if r == "ACCEPT")
    n_refuse = sum(1 for r in per_query_route if r == "REFUSE")

    return {
        "arm": "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION",
        "utility_mean": float(np.mean(per_query_util)),
        "utility_norm": (float(np.mean(per_query_util)) + 1.0) / 2.0,
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
    """Run all 3 arms for one seed. Returns dict with per-arm results."""
    if run_mode == "smoke" or run_mode == "self_test":
        n_clean, n_noisy, n_oob = SMOKE_N_CLEAN, SMOKE_N_NOISY, SMOKE_N_OOB
    else:
        n_clean, n_noisy, n_oob = FULL_N_CLEAN, FULL_N_NOISY, FULL_N_OOB

    kb_keys, kb_vals, kb_val_indices = build_kb(seed, M_ITEMS)
    queries, intent, true_val = build_queries(
        seed, kb_keys, kb_val_indices, n_clean, n_noisy, n_oob)

    print(f"[seed={seed}] arms starting, n_queries={queries.shape[0]} "
          f"({n_clean}/{n_noisy}/{n_oob})", flush=True)

    per_arm_results = {}
    per_arm_failure = {}
    for arm_idx, arm_name in enumerate(ARMS):
        try:
            if arm_name == "ARM_CORTEX_ON":
                r = run_arm_cortex_on(seed, queries, kb_keys, kb_vals,
                                      kb_val_indices, intent, true_val)
            elif arm_name == "ARM_CORTEX_OFF":
                r = run_arm_cortex_off(seed, queries, kb_keys, kb_vals,
                                       kb_val_indices, intent, true_val)
            else:
                r = run_arm_individual_no_composition(
                    seed, queries, kb_keys, kb_vals, kb_val_indices,
                    intent, true_val)
            per_arm_results[arm_name] = r
            emit_heartbeat(output_dir, unit_idx=arm_idx, total_units=len(ARMS),
                           elapsed_s=time.perf_counter() - t0)
            print(f"[seed={seed}] {arm_name} norm_util={r['utility_norm']:.4f} "
                  f"n_accept={r['n_accept']} n_clarify={r['n_clarify']} "
                  f"n_refuse={r['n_refuse']} conf_mean={r['confidence_mean']:.4f}",
                  flush=True)
        except Exception as e:
            per_arm_failure[arm_name] = {
                "failure_class": type(e).__name__,
                "msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            print(f"[seed={seed}] {arm_name} FAILED: {type(e).__name__}: {e}",
                  flush=True)

    # META_RULE_AF: arms-must-differ via retrieval sha256
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
    """Compute HP/MB/HF verdict from per-seed results."""
    seeds = sorted(per_seed.keys())
    n_seeds = len(seeds)
    n_arms = len(ARMS)
    expected_n_units = n_arms * n_seeds

    completed_arms = sum(
        1 for s in seeds for a in ARMS
        if a in per_seed[s].get("per_arm", {}))
    cardinality_ok = (completed_arms == expected_n_units)

    # Per-arm mean + cv across seeds
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
            cv = sd / max(abs(m), 1e-9)
        else:
            m, sd, cv = float("nan"), float("nan"), float("nan")
        per_arm_agg[arm] = {"mean": m, "sd": sd, "cv": cv, "n_seeds": len(vals)}

    on_util = per_arm_agg["ARM_CORTEX_ON"]["mean"]
    off_util = per_arm_agg["ARM_CORTEX_OFF"]["mean"]
    indiv_util = per_arm_agg["ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION"]["mean"]

    h1_gap = on_util - off_util
    h3_gap = on_util - indiv_util
    on_cv = per_arm_agg["ARM_CORTEX_ON"]["cv"]

    # arms_differ across all seeds
    arms_differ_all = all(per_seed[s].get("arms_differ_verified", False)
                          for s in seeds)

    # META_RULE_AG baseline_in_band check
    baseline_in_band = 0.05 < off_util < 0.95
    on_in_band = 0.05 < on_util < 0.95

    # SMOKE-mode thresholds vs FULL-mode thresholds
    hp_gap_h1 = 0.10
    hp_gap_h3 = 0.05
    hp_cv = 0.20

    reasons = []
    verdict = "HARD_PASS"

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        reasons.append(f"cardinality {completed_arms}/{expected_n_units}")

    if not arms_differ_all:
        verdict = "HARD_FAIL"
        reasons.append("META_RULE_AF violation: arm retrievals bit-identical")

    if not baseline_in_band:
        verdict = "MIDDLE_BAND"
        reasons.append(
            f"META_RULE_AG: baseline off_util={off_util:.4f} outside [0.05, 0.95]")

    if h1_gap < 0.05:
        verdict = "HARD_FAIL"
        reasons.append(f"H1 gap={h1_gap:.4f} < 0.05 (near-tie or cortex hurts)")
    elif h1_gap < hp_gap_h1:
        if verdict == "HARD_PASS":
            verdict = "MIDDLE_BAND"
        reasons.append(f"H1 gap={h1_gap:.4f} in MB band [0.05, 0.10)")

    if run_mode == "full":
        if on_cv >= 0.30:
            verdict = "HARD_FAIL"
            reasons.append(f"cortex_on cv={on_cv:.4f} >= 0.30")
        elif on_cv >= hp_cv:
            if verdict == "HARD_PASS":
                verdict = "MIDDLE_BAND"
            reasons.append(f"cortex_on cv={on_cv:.4f} in MB band [0.20, 0.30]")

    if h3_gap < hp_gap_h3:
        reasons.append(
            f"H3 composition-gap={h3_gap:.4f} < 0.05 (composition doesn't help)")

    verdict_msg = (
        f"{verdict} | H1_gap={h1_gap:.4f} H3_gap={h3_gap:.4f} | "
        f"ON={on_util:.4f} OFF={off_util:.4f} INDIV={indiv_util:.4f} | "
        f"cv_ON={on_cv:.4f} | arms_differ={arms_differ_all} | "
        f"cardinality={completed_arms}/{expected_n_units} | "
        f"reasons={'; '.join(reasons) if reasons else 'all_gates_pass'}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "per_arm_agg": per_arm_agg,
        "h1_gap": h1_gap,
        "h3_gap": h3_gap,
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
    """Wrapper called by seed-specific launcher scripts. Returns exit code."""
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
            },
            "per_seed": {str(seed): per_seed_result},
            "verdict": verdict_info["verdict"],
            "verdict_msg": verdict_info["verdict_msg"],
            "summary": verdict_info["summary"],
            "per_arm_agg": verdict_info["per_arm_agg"],
            "h1_gap": verdict_info["h1_gap"],
            "h3_gap": verdict_info["h3_gap"],
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
    """Import-level selftest: build tiny KB + run all 3 arms; verify utilities
    differ (META_RULE_AF proxy). Also asserts v2-specific invariants:
      - UTIL_CLARIFY == 0.65 exactly (principled-credit constant frozen).
      - 3 arms present (ARM_CORTEX_ON/OFF/INDIV).
      - v1-frozen config invariants preserved (N_DIM/M_ITEMS/NOISY_FLIP_FRAC/
        REFUSE_TAU/CLARIFY_LOWER_TAU/CLARIFY_UPPER_TAU/V_CB/STM_K/LTM_K/S_ROLES).
      - Anchor is v2 (guards against wrapper-vs-core mismatch).
    Fast (<5s)."""
    # v2 sole-diff invariant: CLARIFY payoff = 0.65 exactly.
    assert UTIL_CLARIFY == 0.65, \
        f"SELFTEST_FAIL: UTIL_CLARIFY={UTIL_CLARIFY} but v2 requires exactly 0.65 " \
        "(principled Bayesian VOI credit; changing it invalidates the pre-committed " \
        "prediction band)"
    # v1-frozen invariants: nothing else re-tuned.
    _frozen = {
        "N_DIM": (N_DIM, 8192),
        "M_ITEMS": (M_ITEMS, 300),
        "NOISY_FLIP_FRAC": (NOISY_FLIP_FRAC, 0.35),
        "REFUSE_TAU": (REFUSE_TAU, 0.15),
        "CLARIFY_LOWER_TAU": (CLARIFY_LOWER_TAU, 0.18),
        "CLARIFY_UPPER_TAU": (CLARIFY_UPPER_TAU, 0.42),
        "V_CB": (V_CB, 1024),
        "STM_K": (STM_K, 100),
        "LTM_K": (LTM_K, 1200),
        "S_ROLES": (S_ROLES, 4),
        "UTIL_ACCEPT_CORRECT": (UTIL_ACCEPT_CORRECT, 1.0),
        "UTIL_ACCEPT_WRONG": (UTIL_ACCEPT_WRONG, -1.0),
        "UTIL_REFUSE_OOB": (UTIL_REFUSE_OOB, 0.5),
        "UTIL_REFUSE_INKB": (UTIL_REFUSE_INKB, -0.5),
    }
    for name, (got, want) in _frozen.items():
        assert got == want, \
            f"SELFTEST_FAIL: v1-frozen invariant {name}={got} but v2 requires {want} " \
            "(v1 config must be preserved -- only CLARIFY payoff changes in v2)"
    # 3-arms invariant.
    assert len(ARMS) == 3 and \
        ARMS[0] == "ARM_CORTEX_ON" and \
        ARMS[1] == "ARM_CORTEX_OFF" and \
        ARMS[2] == "ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION", \
        f"SELFTEST_FAIL: ARMS mismatch: {ARMS}"
    # v2 anchor guard.
    assert ANCHOR_BASE == "exp_cortex_task_analog_downstream_v2", \
        f"SELFTEST_FAIL: ANCHOR_BASE={ANCHOR_BASE} but v2 requires " \
        "'exp_cortex_task_analog_downstream_v2'"

    seed = 7
    kb_keys, kb_vals, kb_val_indices = build_kb(seed, 20)
    queries, intent, true_val = build_queries(
        seed, kb_keys, kb_val_indices, 3, 3, 4)
    r_on = run_arm_cortex_on(seed, queries, kb_keys, kb_vals,
                             kb_val_indices, intent, true_val)
    r_off = run_arm_cortex_off(seed, queries, kb_keys, kb_vals,
                               kb_val_indices, intent, true_val)
    r_indiv = run_arm_individual_no_composition(
        seed, queries, kb_keys, kb_vals, kb_val_indices, intent, true_val)
    # ON and OFF should differ on route-signature (OFF always ACCEPT; ON may
    # REFUSE/CLARIFY on OOB/noisy). AF check by route+pred sequence hash.
    assert r_on["retrieval_sha256"] != r_off["retrieval_sha256"], \
        "META_RULE_AF: ON and OFF route+pred sequence identical"
    # v2 utility bounds: with CLARIFY=+0.65 raw the per-query util range is
    # [-1.0, +1.0] unchanged (max ACCEPT_CORRECT still = 1.0, min ACCEPT_WRONG
    # still = -1.0), so normalization (mean+1)/2 stays in [0,1].
    for r in (r_on, r_off, r_indiv):
        assert 0.0 <= r["utility_norm"] <= 1.0, \
            f"utility_norm {r['utility_norm']} outside [0,1] for {r['arm']}"


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
        # Best-effort crash write when args don't parse yet.
        try:
            od = _output_dir_for(ANCHOR_BASE, "smoke")
            _write_crash_metrics(od, ANCHOR_BASE, e)
        except Exception:
            pass
        raise
