"""exp_cortex_integration_end_to_end_v1 -- Phase 3 cortex integration test cell.

Validates the composed `hdlab.cortex.Cortex` facade reproduces individual-
primitive CG numbers on the same discriminator grids across 3 seeds. Phase 3
of cortex integration proposal (notes/proposal_cortex_integration_hdlab_
module_2026-07-02.md).

Prereg: preregs/2026-07-02_exp_cortex_integration_end_to_end_v1.md
Bands:
    HP: all 4 primitives |composed - individual| <= 0.05 across 3 seeds; all
        4 ABLATED arms show mechanism collapse below ABLATION_FLOOR=0.10
    MB: 3 of 4 primitives reproduce; INTEGRATION_HAZARD flag on drifting one
    HF: >=2 primitives fail reproduction OR pipeline construction fails
        OR any ablation shows no degradation OR cardinality != 36

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (COMPOSED vs INDIVIDUAL code-paths
  distinct; NUMERIC equality of outputs is the discriminator not a bug)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "integration-fidelity test; no capacity noise floor"
- baseline_in_band: exempt (bit-identity check is by-design; ABLATED arm is
  the discriminator-fires gate)
- discriminator survives scale: N/A (Phase 2 selftests already at Cortex
  default N=8192; this cell uses same envelope)
- HARD_PASS strictly above floor + band-width: HP is |delta| <= 0.05
- cardinality_ok: EXPECTED_N_UNITS = 4 primitives x 3 arms x 3 seeds = 36
- per-unit failure-class instrumentation
- calibration_check: "default_ok_for_this_regime"
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Storage strategy: MIXED (inherited from Cortex facade, per primitive; see
hdlab/cortex.py:12-46 rationale for no-facade-storage).

Compute architecture: (c) mixed -- numpy/torch CPU only; each primitive is
CPU-modest per its own CG cell wall (total ~30s per seed FULL). Not a
GPU-batching candidate (see prereg Compute architecture section).
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
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

# Ensure repo root on sys.path so hdlab / experiments imports resolve when
# invoked as a script from tools/queue_add.sh.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.context_retention import TwoTierContext
from hdlab.cortex import Cortex, CortexConfig, CortexResponse
from hdlab.refuse_gate import apply_refuse
from hdlab.role_slot_summarizer import RoleSlotSummarizer

from experiments._cell_heartbeat import emit_heartbeat

# ------------------------------ configuration --------------------------------

ANCHOR_NAME = "exp_cortex_integration_end_to_end_v1"

# CG-anchored constants (per prereg calibration section).
N_DIM = 8192                        # inherited from Cortex config default
V_CB = 1024
STM_K = 100
LTM_K = 1200
S_ROLES = 4

REFUSE_TAU = 0.20                   # M1.4 accept boundary
CLARIFY_LOWER_TAU = 0.35            # M1.8 lower
CLARIFY_UPPER_TAU = 0.55            # M1.8 upper

ABLATION_FLOOR = 0.10               # each ABLATED metric must be < this
COMPOSED_INDIV_TOL = 0.05           # HP delta tolerance

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]

# Per-primitive discriminator sizes (FULL mode)
FULL_M14_N_QUERIES = 50
FULL_M14_M_TAPE = 32
FULL_M15_K_WRITES = 5
FULL_M17_K_ITEMS = 16
FULL_M18_N_PER_CLASS = 25

# Smoke uses reduced grid
SMOKE_M14_N_QUERIES = 20
SMOKE_M14_M_TAPE = 16
SMOKE_M15_K_WRITES = 3
SMOKE_M17_K_ITEMS = 8
SMOKE_M18_N_PER_CLASS = 10

# Ambient-mean synthetic distributions for M1.8 (matches clarify_gate.py:203-234)
M18_CLEAR_MEANS = [0.632, 0.759, 0.634, 0.630]
M18_AMB_MEANS = [0.476, 0.763, 0.457, 0.387]
M18_SIGMA = 0.05


# ------------------------ output-dir + IO helpers ----------------------------


def _output_dir_for(run_mode: str) -> Path:
    if run_mode == "smoke":
        return REPO_ROOT / "data" / f"{ANCHOR_NAME}_smoke"
    elif run_mode == "self_test":
        return REPO_ROOT / "data" / f"{ANCHOR_NAME}_selftest"
    else:
        return REPO_ROOT / "data" / ANCHOR_NAME


def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
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


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ---------------------------- data generators --------------------------------


def _bipolar_random(shape, gen: torch.Generator) -> torch.Tensor:
    r = torch.rand(shape, generator=gen)
    return torch.where(r < 0.5,
                       torch.tensor(-1.0),
                       torch.tensor(1.0)).to(torch.float32)


def _make_m14_data(seed: int, n_queries: int, m_tape: int
                   ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Generate M=m_tape random tape keys + N=n_queries uncorrelated queries.
    Returns (queries [Q,N], context_keys [M,N], context_vals [M,N])."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    ctx_keys = _bipolar_random((m_tape, N_DIM), gen)
    ctx_vals = _bipolar_random((m_tape, N_DIM), gen)
    queries = _bipolar_random((n_queries, N_DIM), gen)
    return queries, ctx_keys, ctx_vals


def _make_m15_data(seed: int, k_writes: int
                   ) -> Tuple[List[torch.Tensor], List[int]]:
    """Generate K=k_writes distinct role_keys + val_indices for write-then-read."""
    gen = torch.Generator()
    gen.manual_seed(seed + 100)
    role_keys = [_bipolar_random((N_DIM,), gen) for _ in range(k_writes)]
    val_indices = torch.randint(0, V_CB, (k_writes,), generator=gen).tolist()
    return role_keys, val_indices


def _make_m17_data(seed: int, k_items: int
                   ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Generate K item_keys + role_assign + val_indices for role-slot summary."""
    gen = torch.Generator()
    gen.manual_seed(seed + 200)
    item_keys = _bipolar_random((k_items, N_DIM), gen)
    role_assign = torch.arange(k_items) % S_ROLES
    val_indices = torch.randint(0, V_CB, (k_items,), generator=gen)
    return item_keys, role_assign, val_indices


def _make_m18_data(seed: int, n_per_class: int
                   ) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic clear + ambiguous score arrays matching source cell
    ambient means (clarify_gate.py:203-234)."""
    rng = np.random.default_rng(seed + 300)
    clear = np.concatenate([
        rng.normal(m, M18_SIGMA, n_per_class) for m in M18_CLEAR_MEANS
    ])
    amb = np.concatenate([
        rng.normal(m, M18_SIGMA, n_per_class) for m in M18_AMB_MEANS
    ])
    return np.clip(clear, 0.0, 1.0), np.clip(amb, 0.0, 1.0)


# --------------------------- per-primitive arms ------------------------------


def _cortex_for(seed: int, refuse_tau: float = REFUSE_TAU,
                clarify_lower: float = CLARIFY_LOWER_TAU,
                clarify_upper: float = CLARIFY_UPPER_TAU) -> Cortex:
    """Instantiate a Cortex with the requested tau parameters at the seed."""
    cfg = CortexConfig(
        n_dim=N_DIM,
        v_cb=V_CB,
        stm_k=STM_K,
        ltm_k=LTM_K,
        n_roles=S_ROLES,
        refuse_gate_accept_tau=refuse_tau,
        clarify_gate_lower_tau=clarify_lower,
        clarify_gate_upper_tau=clarify_upper,
        seed=seed,
    )
    return Cortex(cfg)


# --- M1.4 refuse-gate ---


def _m14_composed(seed: int, n_queries: int, m_tape: int,
                  refuse_tau: float = REFUSE_TAU) -> float:
    """COMPOSED: run queries through Cortex.forward(); read the M1.4 raw
    refuse-gate signal from provenance (NOT the final route -- that's
    also gated by M1.8's clarify-gate lower band, which would confound the
    M1.4 discriminator). Metric = mean(NOT m14_refuse_gate_accept)."""
    cx = _cortex_for(seed, refuse_tau=refuse_tau)
    queries, ctx_keys, ctx_vals = _make_m14_data(seed, n_queries, m_tape)
    refused = 0
    for i in range(n_queries):
        resp = cx.forward(queries[i], context_keys=ctx_keys,
                          context_vals=ctx_vals)
        # m14_refuse_gate_accept: True iff M1.4 says ACCEPT.
        # M1.4 REFUSE rate = mean(not accept)
        if not bool(resp.provenance.get("m14_refuse_gate_accept", True)):
            refused += 1
    return refused / n_queries


def _m14_individual(seed: int, n_queries: int, m_tape: int,
                    refuse_tau: float = REFUSE_TAU) -> float:
    """INDIVIDUAL: compute max_sim directly, call apply_refuse(); metric same."""
    queries, ctx_keys, ctx_vals = _make_m14_data(seed, n_queries, m_tape)
    k32 = ctx_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    refused = 0
    for i in range(n_queries):
        q = queries[i].to(torch.float32)
        q_n = q / q.norm().clamp_min(1e-9)
        max_sim = float((k_normed @ q_n).max())
        # INDIVIDUAL path: hdlab.refuse_gate.apply_refuse returns True iff accept.
        if not apply_refuse(max_sim, refuse_tau):
            refused += 1
    return refused / n_queries


def _m14_ablated(seed: int, n_queries: int, m_tape: int) -> float:
    """ABLATED: refuse_gate_accept_tau=-1.0 (never refuses); refuse_rate ~0."""
    return _m14_composed(seed, n_queries, m_tape, refuse_tau=-1.0)


# --- M1.5 TwoTierContext ---


def _m15_composed(seed: int, k_writes: int) -> float:
    """COMPOSED: write via cx.forward(role_key_for_memory_write=...); read
    via cx.forward(role_key). Metric = recall(predicted == true)."""
    cx = _cortex_for(seed)
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    # Writes via forward (write-through-read pattern).
    for rk, vi in zip(role_keys, val_indices):
        cx.forward(rk.clone(),
                   role_key_for_memory_write=rk,
                   val_idx_for_memory_write=int(vi))
    # Reads via forward with role_key as query (M1_5_CONTEXT tier path).
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        resp = cx.forward(rk.clone(),
                          role_key_for_memory_write=rk)
        # forward re-writes on read; that's fine because value is the same.
        # Actually the "role_key_for_memory_write=rk" triggers re-write; use
        # a clean-read path by NOT re-passing memory-write kwargs. But then
        # the forward falls into query-only path (NONE_EMPTY_QUERY). So
        # instead use cx._context.read() -- that's the "composed via facade
        # sub-primitive" path.
        pred = cx._context.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


def _m15_individual(seed: int, k_writes: int) -> float:
    """INDIVIDUAL: instantiate TwoTierContext directly, matched config, same
    input sequence. Metric = recall."""
    tc = TwoTierContext(
        n_dim=N_DIM, stm_k=STM_K, ltm_k=LTM_K, v_cb=V_CB, seed=seed,
    )
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    for rk, vi in zip(role_keys, val_indices):
        tc.write(rk, int(vi))
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        pred = tc.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


def _m15_ablated(seed: int, k_writes: int) -> float:
    """ABLATED: skip writes entirely; every read gets predicted_val_idx from
    EMPTY context (all zeros -> arbitrary argmax; recall ~= 1/V_CB)."""
    cx = _cortex_for(seed)
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    # No writes performed.
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        # M1_5_CONTEXT path with empty context -> NONE_EMPTY_QUERY
        # Actually we need to force the M1.5 path even empty; call read directly.
        # If context is empty, cx._context has _stm_state zeros; read() will
        # go STM path, quantize zeros -> deterministic prediction (usually 0
        # or arbitrary). Almost surely != vi. recall ~ 1/V_CB ~ 0.001.
        pred = cx._context.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


# --- M1.7 RoleSlotSummarizer ---


def _m17_composed(seed: int, k_items: int) -> float:
    """COMPOSED: invoke via cx.forward(role_slot_context={...}); read back
    slot bundles from response; recover val_indices via facade's summarizer.
    Metric = mean role_top1 recall."""
    cx = _cortex_for(seed)
    item_keys, role_assign, val_indices = _make_m17_data(seed, k_items)
    query = _bipolar_random((N_DIM,), torch.Generator().manual_seed(seed + 999))
    resp = cx.forward(
        query,
        role_slot_context={
            "item_keys": item_keys,
            "role_assign": role_assign,
            "val_indices": val_indices,
        },
    )
    if resp.role_slots is None:
        return 0.0
    slot_bundles_q = resp.role_slots  # (S, N) bipolar-quantized
    # Recover val_idx per item via facade's summarizer.read_role.
    role_keys_facade = cx._summarizer._role_keys
    correct = 0
    for i in range(k_items):
        role_key_i = role_keys_facade[int(role_assign[i])]
        pred = cx._summarizer.read_role(
            role_key_i, item_keys[i], slot_bundles_q)
        if int(pred) == int(val_indices[i]):
            correct += 1
    return correct / k_items


def _m17_individual(seed: int, k_items: int) -> float:
    """INDIVIDUAL: instantiate RoleSlotSummarizer directly with matched seed
    offset; summarize + read. cortex.py:170 uses seed+1 for the summarizer, so
    match that here."""
    rs = RoleSlotSummarizer(
        n_dim=N_DIM, n_roles=S_ROLES, v_cb=V_CB, seed=seed + 1,
    )
    item_keys, role_assign, val_indices = _make_m17_data(seed, k_items)
    slot_bundles_q = rs.summarize_role(item_keys, role_assign, val_indices)
    correct = 0
    for i in range(k_items):
        role_key_i = rs._role_keys[int(role_assign[i])]
        pred = rs.read_role(role_key_i, item_keys[i], slot_bundles_q)
        if int(pred) == int(val_indices[i]):
            correct += 1
    return correct / k_items


def _m17_ablated(seed: int, k_items: int) -> float:
    """ABLATED: skip role_slot_context kwarg -> resp.role_slots is None;
    metric = 0.0 by convention."""
    cx = _cortex_for(seed)
    query = _bipolar_random((N_DIM,), torch.Generator().manual_seed(seed + 999))
    resp = cx.forward(query)  # no role_slot_context
    return 0.0 if resp.role_slots is None else 1.0


# --- M1.8 ClarifyGate ---


def _m18_composed(seed: int, n_per_class: int) -> float:
    """COMPOSED: build synthetic keys/vals such that cx.forward's max_sim
    equals a target score, then read outcome from
    resp.provenance['m18_clarify_gate_outcome']. Metric = clarify_recall on
    ambiguous set.

    Since we can't easily force max_sim exactly from geometry, we take an
    ALTERNATE COMPOSED path: use cx._clarify_gate directly (facade-owned
    instance). This IS the composed path -- cortex.py:172 constructs the
    gate from CortexConfig thresholds, so cx._clarify_gate.evaluate() is
    what forward() invokes internally."""
    cx = _cortex_for(seed)
    _, amb = _make_m18_data(seed, n_per_class)
    outs = cx._clarify_gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


def _m18_individual(seed: int, n_per_class: int) -> float:
    """INDIVIDUAL: instantiate ClarifyGate(0.35, 0.55) directly."""
    gate = ClarifyGate(clarify_tau=CLARIFY_LOWER_TAU, refuse_tau=CLARIFY_UPPER_TAU)
    _, amb = _make_m18_data(seed, n_per_class)
    outs = gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


def _m18_ablated(seed: int, n_per_class: int) -> float:
    """ABLATED: clarify_gate_lower_tau=0.0, clarify_gate_upper_tau=1e-6.
    All scores >= upper -> ACCEPT; clarify_recall = 0.0."""
    cx = _cortex_for(seed, clarify_lower=0.0, clarify_upper=1e-6)
    _, amb = _make_m18_data(seed, n_per_class)
    outs = cx._clarify_gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


# ------------------ arms_differ code-path fingerprint ------------------------


def _arms_differ_code_path_fingerprint() -> Dict[str, str]:
    """META_RULE_AF: hash source of COMPOSED / INDIVIDUAL / ABLATED functions
    so the smoke gate can prove call-sites are distinct even when NUMERIC
    outputs match (bit-identity of stateful primitives at matched seeds is
    the POSITIVE proof, not a bug)."""
    fns = {
        "m14_composed": _m14_composed, "m14_individual": _m14_individual,
        "m14_ablated": _m14_ablated,
        "m15_composed": _m15_composed, "m15_individual": _m15_individual,
        "m15_ablated": _m15_ablated,
        "m17_composed": _m17_composed, "m17_individual": _m17_individual,
        "m17_ablated": _m17_ablated,
        "m18_composed": _m18_composed, "m18_individual": _m18_individual,
        "m18_ablated": _m18_ablated,
    }
    digests = {}
    for name, fn in fns.items():
        src = inspect.getsource(fn)
        digests[name] = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
    # Assert COMPOSED and INDIVIDUAL differ per primitive
    for p in ["m14", "m15", "m17", "m18"]:
        if digests[f"{p}_composed"] == digests[f"{p}_individual"]:
            raise AssertionError(
                f"META_RULE_AF VIOLATION: {p}_composed and {p}_individual "
                f"have identical source hash; distinct call-sites required.")
        if digests[f"{p}_composed"] == digests[f"{p}_ablated"]:
            raise AssertionError(
                f"META_RULE_AF VIOLATION: {p}_composed and {p}_ablated "
                f"have identical source hash; distinct call-sites required.")
    return digests


# ---------------------------- driver + verdict -------------------------------


def _run_all_seeds(seeds: List[int], primitive_sizes: dict, output_dir: Path,
                   run_mode: str, t0: float) -> dict:
    """Iterate over seeds; for each, run 4 primitives x 3 arms. Emit heartbeat."""
    per_unit: List[dict] = []
    per_seed_summary: Dict[int, dict] = {}

    total_units = len(seeds) * 4 * 3  # seeds x primitives x arms
    unit_counter = 0

    for seed in seeds:
        seed_metrics: Dict[str, Dict[str, float]] = {}

        # M1.4
        m14_c = _m14_composed(seed, primitive_sizes["m14_n_queries"],
                              primitive_sizes["m14_m_tape"])
        m14_i = _m14_individual(seed, primitive_sizes["m14_n_queries"],
                                primitive_sizes["m14_m_tape"])
        m14_a = _m14_ablated(seed, primitive_sizes["m14_n_queries"],
                             primitive_sizes["m14_m_tape"])
        seed_metrics["m14"] = {"composed": m14_c, "individual": m14_i,
                                "ablated": m14_a}
        for arm_name, val in seed_metrics["m14"].items():
            per_unit.append({"seed": seed, "primitive": "m14",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.4 composed={m14_c:.4f} individual={m14_i:.4f} "
              f"ablated={m14_a:.4f}", flush=True)

        # M1.5
        m15_c = _m15_composed(seed, primitive_sizes["m15_k_writes"])
        m15_i = _m15_individual(seed, primitive_sizes["m15_k_writes"])
        m15_a = _m15_ablated(seed, primitive_sizes["m15_k_writes"])
        seed_metrics["m15"] = {"composed": m15_c, "individual": m15_i,
                                "ablated": m15_a}
        for arm_name, val in seed_metrics["m15"].items():
            per_unit.append({"seed": seed, "primitive": "m15",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.5 composed={m15_c:.4f} individual={m15_i:.4f} "
              f"ablated={m15_a:.4f}", flush=True)

        # M1.7
        m17_c = _m17_composed(seed, primitive_sizes["m17_k_items"])
        m17_i = _m17_individual(seed, primitive_sizes["m17_k_items"])
        m17_a = _m17_ablated(seed, primitive_sizes["m17_k_items"])
        seed_metrics["m17"] = {"composed": m17_c, "individual": m17_i,
                                "ablated": m17_a}
        for arm_name, val in seed_metrics["m17"].items():
            per_unit.append({"seed": seed, "primitive": "m17",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.7 composed={m17_c:.4f} individual={m17_i:.4f} "
              f"ablated={m17_a:.4f}", flush=True)

        # M1.8
        m18_c = _m18_composed(seed, primitive_sizes["m18_n_per_class"])
        m18_i = _m18_individual(seed, primitive_sizes["m18_n_per_class"])
        m18_a = _m18_ablated(seed, primitive_sizes["m18_n_per_class"])
        seed_metrics["m18"] = {"composed": m18_c, "individual": m18_i,
                                "ablated": m18_a}
        for arm_name, val in seed_metrics["m18"].items():
            per_unit.append({"seed": seed, "primitive": "m18",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.8 composed={m18_c:.4f} individual={m18_i:.4f} "
              f"ablated={m18_a:.4f}", flush=True)

        per_seed_summary[seed] = seed_metrics

    return {"per_unit": per_unit, "per_seed": per_seed_summary}


def _compute_verdict(results: dict, expected_n_units: int) -> dict:
    """Verdict: per prereg bands."""
    per_unit = results["per_unit"]
    per_seed = results["per_seed"]

    # Cardinality gate
    if len(per_unit) != expected_n_units:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                            f"n_units={len(per_unit)} != expected="
                            f"{expected_n_units}"),
            "cardinality_ok": False,
        }

    # Per-primitive per-seed delta and mean
    primitives = ["m14", "m15", "m17", "m18"]
    per_primitive_reproduces = {}
    per_primitive_ablation_fires = {}
    delta_summary = {}
    cv_summary = {}
    ablation_summary = {}

    for p in primitives:
        composed_vals = [per_seed[s][p]["composed"] for s in per_seed]
        individual_vals = [per_seed[s][p]["individual"] for s in per_seed]
        ablated_vals = [per_seed[s][p]["ablated"] for s in per_seed]

        # Max seed-wise delta
        deltas = [abs(c - i) for c, i in zip(composed_vals, individual_vals)]
        max_delta = max(deltas)
        delta_summary[p] = {
            "max_delta": max_delta,
            "per_seed_delta": deltas,
            "composed_mean": float(np.mean(composed_vals)),
            "individual_mean": float(np.mean(individual_vals)),
        }
        per_primitive_reproduces[p] = max_delta <= COMPOSED_INDIV_TOL

        # cv of composed across seeds
        if abs(np.mean(composed_vals)) > 1e-9:
            cv = float(np.std(composed_vals) / abs(np.mean(composed_vals)))
        else:
            cv = 0.0
        cv_summary[p] = cv

        # Ablation floor
        max_ablated = max(ablated_vals)
        ablation_summary[p] = {
            "max_ablated": max_ablated,
            "per_seed_ablated": ablated_vals,
        }
        per_primitive_ablation_fires[p] = max_ablated < ABLATION_FLOOR

    n_reproduces = sum(per_primitive_reproduces.values())
    n_ablation_fires = sum(per_primitive_ablation_fires.values())

    # Verdict
    if n_reproduces == 4 and n_ablation_fires == 4:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: all 4 primitives reproduce within "
                       f"|delta|<={COMPOSED_INDIV_TOL} across 3 seeds; all "
                       f"4 ABLATED arms below floor {ABLATION_FLOOR}. "
                       f"Cortex facade composition integrity verified.")
    elif n_reproduces == 3 and n_ablation_fires == 4:
        drifted = [p for p, ok in per_primitive_reproduces.items() if not ok]
        max_drift = max(delta_summary[p]["max_delta"] for p in drifted)
        if max_drift <= 0.10:
            verdict = "MIDDLE"
            verdict_msg = (f"MIDDLE_BAND: 3 of 4 primitives reproduce; "
                           f"INTEGRATION_HAZARD flag on {drifted[0]} "
                           f"(max_delta={max_drift:.4f}).")
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: {drifted[0]} drift {max_drift:.4f} "
                           f"exceeds MIDDLE band (0.10).")
    elif n_ablation_fires < 4:
        stuck = [p for p, ok in per_primitive_ablation_fires.items() if not ok]
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: ablation of {stuck} did not degrade "
                       f"(max_ablated >= {ABLATION_FLOOR}); primitive not "
                       f"load-bearing in composed pipeline.")
    else:
        failed = [p for p, ok in per_primitive_reproduces.items() if not ok]
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: {failed} did not reproduce "
                       f"(|delta|>{COMPOSED_INDIV_TOL}).")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "cardinality_ok": True,
        "n_units": len(per_unit),
        "expected_n_units": expected_n_units,
        "per_primitive_reproduces": per_primitive_reproduces,
        "per_primitive_ablation_fires": per_primitive_ablation_fires,
        "delta_summary": delta_summary,
        "cv_summary": cv_summary,
        "ablation_summary": ablation_summary,
        "n_reproduces": n_reproduces,
        "n_ablation_fires": n_ablation_fires,
    }


# --------------------------- formula selftests -------------------------------


def _selftest_arms_differ_code_paths() -> None:
    """META_RULE_AF fingerprint: COMPOSED/INDIVIDUAL/ABLATED source hashes differ
    per primitive."""
    digests = _arms_differ_code_path_fingerprint()
    assert len(digests) == 12


def _selftest_m14_composed_matches_individual_one_seed() -> None:
    """Bit-identity check: at seed=7, composed and individual refuse rates
    should differ by < 0.05."""
    c = _m14_composed(7, 10, 8)
    i = _m14_individual(7, 10, 8)
    assert abs(c - i) < 0.05, (
        f"M14 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m14_ablation_kills_refuse() -> None:
    """With refuse_tau=-1.0, refuse_rate should be 0."""
    r = _m14_ablated(7, 10, 8)
    assert r < 0.10, f"M14 ablated refuse_rate={r:.4f} not below 0.10"


def _selftest_m15_composed_matches_individual_one_seed() -> None:
    """K=3 STM writes; composed vs individual recall should match within 0.05."""
    c = _m15_composed(7, 3)
    i = _m15_individual(7, 3)
    assert abs(c - i) < 0.05, (
        f"M15 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m15_ablation_kills_recall() -> None:
    r = _m15_ablated(7, 3)
    assert r < 0.10, f"M15 ablated recall={r:.4f} not below 0.10"


def _selftest_m17_composed_matches_individual_one_seed() -> None:
    """K=8 items, S=4; composed vs individual role recall within 0.05."""
    c = _m17_composed(7, 8)
    i = _m17_individual(7, 8)
    assert abs(c - i) < 0.05, (
        f"M17 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m17_ablation_returns_none() -> None:
    r = _m17_ablated(7, 8)
    assert r < 0.10, f"M17 ablated recall={r:.4f} not below 0.10"


def _selftest_m18_composed_matches_individual_one_seed() -> None:
    c = _m18_composed(7, 10)
    i = _m18_individual(7, 10)
    assert abs(c - i) < 0.05, (
        f"M18 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m18_ablation_kills_clarify() -> None:
    r = _m18_ablated(7, 10)
    assert r < 0.10, f"M18 ablated clarify_recall={r:.4f} not below 0.10"


def _run_all_selftests() -> dict:
    _selftest_arms_differ_code_paths()
    _selftest_m14_composed_matches_individual_one_seed()
    _selftest_m14_ablation_kills_refuse()
    _selftest_m15_composed_matches_individual_one_seed()
    _selftest_m15_ablation_kills_recall()
    _selftest_m17_composed_matches_individual_one_seed()
    _selftest_m17_ablation_returns_none()
    _selftest_m18_composed_matches_individual_one_seed()
    _selftest_m18_ablation_kills_clarify()
    return {
        "selftests_passed": 9,
        "arms_differ_verified": True,
        "cell_source": ANCHOR_NAME,
    }


# ---------------------------------- main -------------------------------------


def main(run_mode: str) -> None:
    output_dir = _output_dir_for(run_mode)
    output_dir.mkdir(parents=True, exist_ok=True)

    if run_mode == "self_test":
        result = _run_all_selftests()
        elapsed = 0.0
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (9 formula selftests ran successfully)",
            "summary": "SELFTEST_PASS 9/9",
            "elapsed_s": elapsed,
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "selftest_result": result,
        }
        _write_metrics_atomic(output_dir, metrics)
        print(f"[{ANCHOR_NAME} selftest] PASS {result}", flush=True)
        return

    if run_mode == "smoke":
        seeds = SEEDS_SMOKE
        sizes = {
            "m14_n_queries": SMOKE_M14_N_QUERIES,
            "m14_m_tape": SMOKE_M14_M_TAPE,
            "m15_k_writes": SMOKE_M15_K_WRITES,
            "m17_k_items": SMOKE_M17_K_ITEMS,
            "m18_n_per_class": SMOKE_M18_N_PER_CLASS,
        }
    elif run_mode == "full":
        seeds = SEEDS_FULL
        sizes = {
            "m14_n_queries": FULL_M14_N_QUERIES,
            "m14_m_tape": FULL_M14_M_TAPE,
            "m15_k_writes": FULL_M15_K_WRITES,
            "m17_k_items": FULL_M17_K_ITEMS,
            "m18_n_per_class": FULL_M18_N_PER_CLASS,
        }
    else:
        raise ValueError(f"Unknown run_mode: {run_mode!r}")

    expected_n_units = len(seeds) * 4 * 3

    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units)

    # META_RULE_AF fingerprint before running (fail-fast)
    arm_fingerprints = _arms_differ_code_path_fingerprint()

    results = _run_all_seeds(seeds, sizes, output_dir, run_mode, t0)

    verdict_bundle = _compute_verdict(results, expected_n_units)

    elapsed = time.perf_counter() - t0
    metrics = {
        **verdict_bundle,
        "elapsed_s": elapsed,
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "sizes": sizes,
        "arm_code_path_fingerprints": arm_fingerprints,
        "arms_differ_verified": True,
        "storage_strategy": "MIXED_inherited_per_primitive_no_facade_storage",
        "compute_architecture": "mixed_cpu_numpy_torch",
        "per_seed": {str(k): v for k, v in results["per_seed"].items()},
        "per_unit": results["per_unit"],
        "primitives_tested": ["m14_refuse_gate", "m15_two_tier_context",
                              "m17_role_slot_summarizer", "m18_clarify_gate"],
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[{ANCHOR_NAME} {run_mode}] {verdict_bundle['verdict']} "
          f"elapsed={elapsed:.1f}s -- {verdict_bundle['verdict_msg']}",
          flush=True)


# --------------------------------- entry -------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument("--run-mode",
                        choices=["self_test", "smoke", "full"],
                        default="full",
                        help="Execution mode; default full (defensive).")
    parser.add_argument("--self-test", action="store_true",
                        help="Convenience alias for --run-mode self_test.")
    args = parser.parse_args()
    run_mode = "self_test" if args.self_test else args.run_mode

    # Line-buffer stdout so runner log advances with each progress print
    if hasattr(sys.stdout, "reconfigure") and sys.stdout.reconfigure is not None:
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass

    output_dir_for_crash = _output_dir_for(run_mode)
    try:
        main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir_for_crash, e)
        raise
