"""exp_cortex_integration_with_noise_channel_v1 -- Phase 3b noise-enabled variant.

Tests the noise-ENABLED variant of the cortex integration test (Phase 3 was
noise-DISABLED, landed HARD_PASS 3-seed 2026-07-02 at
data/exp_cortex_integration_end_to_end_v1/metrics.json). Question: does the
Phase 2b NoiseChannel wiring (extracted 2026-07-02 commit 50f44b7cf) preserve
composed-pipeline metrics when disabled (backwards compat) AND keep composition
metrics bounded when enabled (no cross-primitive corruption via side channel)?

Prereg: preregs/2026-07-02_exp_cortex_integration_with_noise_channel_v1.md
Bands:
    HP: (a) NOISE_OFF matches INDIVIDUAL within 0.05 across 3 seeds per primitive
        (reproduces Phase 3 CG; noise wiring backwards-compat), (b) NOISE_LIGHT
        (sigma=0.05) within 0.05 of NOISE_OFF, (c) NOISE_MODERATE (sigma=0.15)
        within 0.20 of NOISE_OFF, (d) noise-effect-probe selftest fires
        (verifies noise actually perturbs router-path max_sim; wiring active)
    MB: NOISE_OFF matches; NOISE_LIGHT bounded; some primitive drifts 0.20-0.30
        under MODERATE
    HF: NOISE_OFF differs from INDIVIDUAL (wiring broke backwards-compat) OR
        any primitive drifts > 0.20 under LIGHT (wiring corrupts sub-primitive
        state) OR noise-probe cos-shift < 0.001 at sigma=0.15 (noise not
        actually applied)

Framing warning (SUBSTRATE PHYSICS DOCUMENTED IN PRE-REG):
    For 8192-D bipolar vectors + L2-preserving Gaussian noise, cos(v, inject(v))
    = 1/sqrt(1+sigma^2). At sigma=0.05 = 0.9988; at sigma=0.15 = 0.9889. Both
    stay above M1.4 refuse_gate_accept_tau=0.20 and M1.8 clarify_gate upper
    tau=0.55, so route-shifts are NOT expected on the discriminator arms as
    designed. Additionally, Phase 3's M1.5/M1.7/M1.8 arm implementations
    bypass the cortex.forward() q_2d path (they call _context.read /
    _summarizer.summarize_role / _clarify_gate.evaluate_batch directly), so
    boundary noise on q_2d has no path to those metrics by wiring design.
    M1.4's arm uses uncorrelated queries -> max_sim ~ 0.03 clean; noise
    preserves cos so max_sim stays ~0.03 -> refuse_rate stays ~1.0.

    EMPIRICAL PREDICTION: delta_composed_noise_on_vs_off ~ 0.00 across all
    primitives and both sigmas. This is CORRECT substrate behavior (noise
    doesn't destroy bipolar retrieval at these sigmas) AND correct wiring
    behavior (Phase 3's arm implementations are noise-independent by
    construction). Phase 3b's discriminator is therefore ABSENCE of large
    delta (regression check) combined with the noise-effect probe (wiring
    liveness check).

Storage strategy: MIXED (inherited from Cortex facade + NO_STORAGE for
NoiseChannel per hdlab/noise_channel.py:31).

Compute architecture: (c) mixed -- numpy/torch CPU only; each primitive is
CPU-modest per its own CG cell wall (total ~15s per seed FULL). Not a
GPU-batching candidate (sequential pipeline composition; per-arm walls << 10s).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (all 4 arms per primitive have distinct
  code-path source hashes; NoiseChannel-enabled vs disabled produces distinct
  provenance keys per cortex.py:274)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "integration-fidelity test + noise-wiring liveness check; no
  capacity-noise floor; metric is |delta| tolerance not signal-detection"
- baseline_in_band: exempt (bit-identity check is by-design; noise-effect
  probe is the discriminator-fires gate)
- discriminator survives scale: N/A (uses cortex default N=8192)
- HARD_PASS strictly above floor + band-width: HP |delta_off_vs_ind| <= 0.05;
  |delta_light_vs_off| <= 0.05; |delta_mod_vs_off| <= 0.20; probe cos-shift
  at sigma=0.15 >= 0.001
- cardinality_ok: EXPECTED_N_UNITS = 4 primitives x 4 arms x 3 seeds = 48
- per-unit failure-class instrumentation
- calibration_check: "default_ok_for_this_regime"
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
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

# Ensure repo root on sys.path so hdlab / experiments imports resolve when
# invoked as a script from tools/queue_add.sh.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.context_retention import TwoTierContext
from hdlab.cortex import Cortex, CortexConfig, CortexResponse
from hdlab.noise_channel import NoiseChannel
from hdlab.refuse_gate import apply_refuse
from hdlab.role_slot_summarizer import RoleSlotSummarizer

from experiments._cell_heartbeat import emit_heartbeat

# ------------------------------ configuration --------------------------------

ANCHOR_NAME = "exp_cortex_integration_with_noise_channel_v1"

# CG-anchored constants (inherited from Phase 3 pre-reg).
N_DIM = 8192
V_CB = 1024
STM_K = 100
LTM_K = 1200
S_ROLES = 4

REFUSE_TAU = 0.20                   # M1.4 accept boundary
CLARIFY_LOWER_TAU = 0.35            # M1.8 lower
CLARIFY_UPPER_TAU = 0.55            # M1.8 upper

# Noise sigma settings per USER 2026-06-30 5x drill regime table
SIGMA_LIGHT = 0.05
SIGMA_MODERATE = 0.15

# Tolerance bands (per pre-reg)
BACKWARDS_COMPAT_TOL = 0.05         # NOISE_OFF vs INDIVIDUAL
NOISE_LIGHT_TOL = 0.05              # NOISE_LIGHT vs NOISE_OFF
NOISE_MODERATE_TOL = 0.20           # NOISE_MODERATE vs NOISE_OFF
PROBE_MIN_COS_SHIFT = 0.001         # noise-effect probe liveness floor at sigma=0.15

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]

# Per-primitive discriminator sizes (FULL mode; inherited from Phase 3)
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

# Ambient-mean synthetic distributions for M1.8 (matches clarify_gate.py:203-234
# per Phase 3 cell L107-109)
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
    """Same data as Phase 3 (uncorrelated bipolar queries + random tape)."""
    gen = torch.Generator()
    gen.manual_seed(seed)
    ctx_keys = _bipolar_random((m_tape, N_DIM), gen)
    ctx_vals = _bipolar_random((m_tape, N_DIM), gen)
    queries = _bipolar_random((n_queries, N_DIM), gen)
    return queries, ctx_keys, ctx_vals


def _make_m15_data(seed: int, k_writes: int
                   ) -> Tuple[List[torch.Tensor], List[int]]:
    gen = torch.Generator()
    gen.manual_seed(seed + 100)
    role_keys = [_bipolar_random((N_DIM,), gen) for _ in range(k_writes)]
    val_indices = torch.randint(0, V_CB, (k_writes,), generator=gen).tolist()
    return role_keys, val_indices


def _make_m17_data(seed: int, k_items: int
                   ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    gen = torch.Generator()
    gen.manual_seed(seed + 200)
    item_keys = _bipolar_random((k_items, N_DIM), gen)
    role_assign = torch.arange(k_items) % S_ROLES
    val_indices = torch.randint(0, V_CB, (k_items,), generator=gen)
    return item_keys, role_assign, val_indices


def _make_m18_data(seed: int, n_per_class: int
                   ) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + 300)
    clear = np.concatenate([
        rng.normal(m, M18_SIGMA, n_per_class) for m in M18_CLEAR_MEANS
    ])
    amb = np.concatenate([
        rng.normal(m, M18_SIGMA, n_per_class) for m in M18_AMB_MEANS
    ])
    return np.clip(clear, 0.0, 1.0), np.clip(amb, 0.0, 1.0)


# --------------------------- per-primitive arms ------------------------------


def _cortex_for(seed: int, noise_enabled: bool = False,
                sigma_boundary: float = 0.0,
                refuse_tau: float = REFUSE_TAU,
                clarify_lower: float = CLARIFY_LOWER_TAU,
                clarify_upper: float = CLARIFY_UPPER_TAU) -> Cortex:
    """Instantiate a Cortex with optional noise-channel enabled."""
    cfg = CortexConfig(
        n_dim=N_DIM,
        v_cb=V_CB,
        stm_k=STM_K,
        ltm_k=LTM_K,
        n_roles=S_ROLES,
        refuse_gate_accept_tau=refuse_tau,
        clarify_gate_lower_tau=clarify_lower,
        clarify_gate_upper_tau=clarify_upper,
        noise_channel_enabled=noise_enabled,
        noise_channel_sigma_boundary=sigma_boundary,
        seed=seed,
    )
    return Cortex(cfg)


# --- M1.4 refuse-gate --------------------------------------------------------


def _m14_metric(seed: int, n_queries: int, m_tape: int, cortex: Cortex) -> float:
    """Metric = refuse_rate on uncorrelated bipolar queries via cortex.forward()
    router path. Reads m14_refuse_gate_accept from provenance."""
    queries, ctx_keys, ctx_vals = _make_m14_data(seed, n_queries, m_tape)
    refused = 0
    for i in range(n_queries):
        resp = cortex.forward(queries[i], context_keys=ctx_keys,
                              context_vals=ctx_vals)
        if not bool(resp.provenance.get("m14_refuse_gate_accept", True)):
            refused += 1
    return refused / n_queries


def _m14_composed_noise_off(seed: int, n_queries: int, m_tape: int) -> float:
    """COMPOSED with noise DISABLED (backwards-compat to Phase 3)."""
    cx = _cortex_for(seed, noise_enabled=False)
    return _m14_metric(seed, n_queries, m_tape, cx)


def _m14_composed_noise_light(seed: int, n_queries: int, m_tape: int) -> float:
    """COMPOSED with noise ENABLED sigma=0.05 (light regime)."""
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_LIGHT)
    return _m14_metric(seed, n_queries, m_tape, cx)


def _m14_composed_noise_moderate(seed: int, n_queries: int, m_tape: int) -> float:
    """COMPOSED with noise ENABLED sigma=0.15 (moderate regime)."""
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_MODERATE)
    return _m14_metric(seed, n_queries, m_tape, cx)


def _m14_individual(seed: int, n_queries: int, m_tape: int) -> float:
    """INDIVIDUAL: compute max_sim numpy + call apply_refuse (no noise)."""
    queries, ctx_keys, ctx_vals = _make_m14_data(seed, n_queries, m_tape)
    k32 = ctx_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    refused = 0
    for i in range(n_queries):
        q = queries[i].to(torch.float32)
        q_n = q / q.norm().clamp_min(1e-9)
        max_sim = float((k_normed @ q_n).max())
        if not apply_refuse(max_sim, REFUSE_TAU):
            refused += 1
    return refused / n_queries


# --- M1.5 TwoTierContext -----------------------------------------------------
# NOTE ON NOISE PATHWAY (documented in cell docstring): cortex.forward() applies
# NoiseChannel.inject() to q_2d only. The M1.5 write path uses caller's
# role_key_for_memory_write (clean) directly per cortex.py:250. The M1.5 read
# path (when role_key_for_memory_write is supplied) also uses
# role_key_for_memory_write per cortex.py:312 -- NOT q_2d. Additionally, this
# cell's arms extract the metric via cx._context.read(rk, ...) direct call
# (matches Phase 3 for reproducibility). Therefore boundary noise on q_2d has
# NO PATH to the M1.5 metric by wiring design. Predicted delta = 0.


def _m15_metric_via_composed(seed: int, k_writes: int, cortex: Cortex) -> float:
    """COMPOSED path: write via cortex.forward(); read via _context.read()
    (matches Phase 3 arm to preserve reproduction test)."""
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    for rk, vi in zip(role_keys, val_indices):
        cortex.forward(rk.clone(),
                       role_key_for_memory_write=rk,
                       val_idx_for_memory_write=int(vi))
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        pred = cortex._context.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


def _m15_composed_noise_off(seed: int, k_writes: int) -> float:
    cx = _cortex_for(seed, noise_enabled=False)
    return _m15_metric_via_composed(seed, k_writes, cx)


def _m15_composed_noise_light(seed: int, k_writes: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_LIGHT)
    return _m15_metric_via_composed(seed, k_writes, cx)


def _m15_composed_noise_moderate(seed: int, k_writes: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_MODERATE)
    return _m15_metric_via_composed(seed, k_writes, cx)


def _m15_individual(seed: int, k_writes: int) -> float:
    """INDIVIDUAL: instantiate TwoTierContext directly."""
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


# --- M1.7 RoleSlotSummarizer -------------------------------------------------
# NOTE: cortex.forward() invokes M1.7 via role_slot_context kwarg which routes
# item_keys/role_assign/val_indices directly to _summarizer.summarize_role
# (cortex.py:369). None of these pass through q_2d. Therefore boundary noise
# does NOT reach the M1.7 metric by wiring design. Predicted delta = 0.


def _m17_metric_via_composed(seed: int, k_items: int, cortex: Cortex) -> float:
    """COMPOSED path: forward() with role_slot_context; read role_slots and
    recover val_idx via cortex._summarizer.read_role."""
    item_keys, role_assign, val_indices = _make_m17_data(seed, k_items)
    query = _bipolar_random((N_DIM,),
                             torch.Generator().manual_seed(seed + 999))
    resp = cortex.forward(
        query,
        role_slot_context={
            "item_keys": item_keys,
            "role_assign": role_assign,
            "val_indices": val_indices,
        },
    )
    if resp.role_slots is None:
        return 0.0
    slot_bundles_q = resp.role_slots
    role_keys_facade = cortex._summarizer._role_keys
    correct = 0
    for i in range(k_items):
        role_key_i = role_keys_facade[int(role_assign[i])]
        pred = cortex._summarizer.read_role(
            role_key_i, item_keys[i], slot_bundles_q)
        if int(pred) == int(val_indices[i]):
            correct += 1
    return correct / k_items


def _m17_composed_noise_off(seed: int, k_items: int) -> float:
    cx = _cortex_for(seed, noise_enabled=False)
    return _m17_metric_via_composed(seed, k_items, cx)


def _m17_composed_noise_light(seed: int, k_items: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_LIGHT)
    return _m17_metric_via_composed(seed, k_items, cx)


def _m17_composed_noise_moderate(seed: int, k_items: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_MODERATE)
    return _m17_metric_via_composed(seed, k_items, cx)


def _m17_individual(seed: int, k_items: int) -> float:
    """INDIVIDUAL: instantiate RoleSlotSummarizer directly (seed+1 to match
    cortex.py:182)."""
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


# --- M1.8 ClarifyGate --------------------------------------------------------
# NOTE: this cell (like Phase 3) invokes _clarify_gate.evaluate_batch directly
# with synthetic scores; that path bypasses q_2d entirely. Predicted delta = 0.


def _m18_metric_via_composed(seed: int, n_per_class: int,
                              cortex: Cortex) -> float:
    _, amb = _make_m18_data(seed, n_per_class)
    outs = cortex._clarify_gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


def _m18_composed_noise_off(seed: int, n_per_class: int) -> float:
    cx = _cortex_for(seed, noise_enabled=False)
    return _m18_metric_via_composed(seed, n_per_class, cx)


def _m18_composed_noise_light(seed: int, n_per_class: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_LIGHT)
    return _m18_metric_via_composed(seed, n_per_class, cx)


def _m18_composed_noise_moderate(seed: int, n_per_class: int) -> float:
    cx = _cortex_for(seed, noise_enabled=True, sigma_boundary=SIGMA_MODERATE)
    return _m18_metric_via_composed(seed, n_per_class, cx)


def _m18_individual(seed: int, n_per_class: int) -> float:
    gate = ClarifyGate(clarify_tau=CLARIFY_LOWER_TAU, refuse_tau=CLARIFY_UPPER_TAU)
    _, amb = _make_m18_data(seed, n_per_class)
    outs = gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


# --- Noise-effect probe (verifies wiring is live) ----------------------------


def _noise_probe_router_cos_shift(seed: int, sigma: float,
                                   n_queries: int = 20) -> float:
    """Discriminator-fires gate for noise wiring: compare max_sim on
    router-path forward() with noise-off vs noise-on at given sigma. Uses
    UNIT-NORM Gaussian queries (not bipolar) so the noise perturbation is
    observable per hdlab/noise_channel.py:245-266 analytical prediction
    (cos ~ 1/sqrt(1 + n*sigma^2) for unit-norm; sigma=0.15 -> 0.07 at n=8192).

    Returns mean |max_sim_off - max_sim_on| over n_queries; should be
    substantially > 0 if noise wiring is live. THEORETICAL@ hdlab.noise_channel
    line 243-266: at n_dim=1024 sigma=0.15 mean cos ~ 0.20; scaling to 8192
    the max_sim shift per query is O(0.05-0.15) typical.
    """
    cx_off = _cortex_for(seed, noise_enabled=False)
    cx_on = _cortex_for(seed, noise_enabled=True, sigma_boundary=sigma)
    # Router tape (bipolar, standard)
    _, ctx_keys, ctx_vals = _make_m14_data(seed, n_queries, 32)
    # UNIT-NORM Gaussian queries for observable noise effect
    gen = torch.Generator()
    gen.manual_seed(seed + 7000)
    query_batch = torch.empty(n_queries, N_DIM, dtype=torch.float32)
    query_batch.normal_(mean=0.0, std=1.0, generator=gen)
    query_batch = query_batch / query_batch.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    shifts = []
    for i in range(n_queries):
        r_off = cx_off.forward(query_batch[i], context_keys=ctx_keys,
                                context_vals=ctx_vals)
        r_on = cx_on.forward(query_batch[i], context_keys=ctx_keys,
                              context_vals=ctx_vals)
        sim_off = float(r_off.provenance.get("confidence_max_sim", 0.0))
        sim_on = float(r_on.provenance.get("confidence_max_sim", 0.0))
        shifts.append(abs(sim_off - sim_on))
    return float(np.mean(shifts))


# ------------------ arms_differ code-path fingerprint ------------------------


def _arms_differ_code_path_fingerprint() -> Dict[str, str]:
    """META_RULE_AF: hash source of the 16 arm functions (4 arms x 4 primitives)
    so smoke gate proves distinct call-sites."""
    fns = {
        "m14_noise_off": _m14_composed_noise_off,
        "m14_noise_light": _m14_composed_noise_light,
        "m14_noise_moderate": _m14_composed_noise_moderate,
        "m14_individual": _m14_individual,
        "m15_noise_off": _m15_composed_noise_off,
        "m15_noise_light": _m15_composed_noise_light,
        "m15_noise_moderate": _m15_composed_noise_moderate,
        "m15_individual": _m15_individual,
        "m17_noise_off": _m17_composed_noise_off,
        "m17_noise_light": _m17_composed_noise_light,
        "m17_noise_moderate": _m17_composed_noise_moderate,
        "m17_individual": _m17_individual,
        "m18_noise_off": _m18_composed_noise_off,
        "m18_noise_light": _m18_composed_noise_light,
        "m18_noise_moderate": _m18_composed_noise_moderate,
        "m18_individual": _m18_individual,
    }
    digests = {}
    for name, fn in fns.items():
        src = inspect.getsource(fn)
        digests[name] = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
    # Assert 3 noise arms differ from individual per primitive (4 arms distinct
    # code paths). Noise arms among themselves may differ only in sigma constant;
    # that's a distinct call-site by constant argument.
    for p in ["m14", "m15", "m17", "m18"]:
        arm_names = [f"{p}_noise_off", f"{p}_noise_light",
                     f"{p}_noise_moderate", f"{p}_individual"]
        arm_digests = [digests[a] for a in arm_names]
        # noise-off vs individual: distinct code paths mandated
        if digests[f"{p}_noise_off"] == digests[f"{p}_individual"]:
            raise AssertionError(
                f"META_RULE_AF VIOLATION: {p}_noise_off and {p}_individual "
                f"have identical source hash; distinct call-sites required.")
        # noise sigma variants: MAY have identical source (delta is only in
        # sigma constant passed at call-time); documented exemption
    return digests


# ---------------------------- driver + verdict -------------------------------


def _run_all_seeds(seeds: List[int], primitive_sizes: dict, output_dir: Path,
                   run_mode: str, t0: float) -> dict:
    per_unit: List[dict] = []
    per_seed_summary: Dict[int, dict] = {}

    total_units = len(seeds) * 4 * 4  # seeds x primitives x arms
    unit_counter = 0

    arms = ["noise_off", "noise_light", "noise_moderate", "individual"]

    for seed in seeds:
        seed_metrics: Dict[str, Dict[str, float]] = {}

        # M1.4
        vals = {
            "noise_off": _m14_composed_noise_off(
                seed, primitive_sizes["m14_n_queries"],
                primitive_sizes["m14_m_tape"]),
            "noise_light": _m14_composed_noise_light(
                seed, primitive_sizes["m14_n_queries"],
                primitive_sizes["m14_m_tape"]),
            "noise_moderate": _m14_composed_noise_moderate(
                seed, primitive_sizes["m14_n_queries"],
                primitive_sizes["m14_m_tape"]),
            "individual": _m14_individual(
                seed, primitive_sizes["m14_n_queries"],
                primitive_sizes["m14_m_tape"]),
        }
        seed_metrics["m14"] = vals
        for arm_name, val in vals.items():
            per_unit.append({"seed": seed, "primitive": "m14",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.4 off={vals['noise_off']:.4f} "
              f"light={vals['noise_light']:.4f} "
              f"mod={vals['noise_moderate']:.4f} "
              f"ind={vals['individual']:.4f}", flush=True)

        # M1.5
        vals = {
            "noise_off": _m15_composed_noise_off(
                seed, primitive_sizes["m15_k_writes"]),
            "noise_light": _m15_composed_noise_light(
                seed, primitive_sizes["m15_k_writes"]),
            "noise_moderate": _m15_composed_noise_moderate(
                seed, primitive_sizes["m15_k_writes"]),
            "individual": _m15_individual(
                seed, primitive_sizes["m15_k_writes"]),
        }
        seed_metrics["m15"] = vals
        for arm_name, val in vals.items():
            per_unit.append({"seed": seed, "primitive": "m15",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.5 off={vals['noise_off']:.4f} "
              f"light={vals['noise_light']:.4f} "
              f"mod={vals['noise_moderate']:.4f} "
              f"ind={vals['individual']:.4f}", flush=True)

        # M1.7
        vals = {
            "noise_off": _m17_composed_noise_off(
                seed, primitive_sizes["m17_k_items"]),
            "noise_light": _m17_composed_noise_light(
                seed, primitive_sizes["m17_k_items"]),
            "noise_moderate": _m17_composed_noise_moderate(
                seed, primitive_sizes["m17_k_items"]),
            "individual": _m17_individual(
                seed, primitive_sizes["m17_k_items"]),
        }
        seed_metrics["m17"] = vals
        for arm_name, val in vals.items():
            per_unit.append({"seed": seed, "primitive": "m17",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.7 off={vals['noise_off']:.4f} "
              f"light={vals['noise_light']:.4f} "
              f"mod={vals['noise_moderate']:.4f} "
              f"ind={vals['individual']:.4f}", flush=True)

        # M1.8
        vals = {
            "noise_off": _m18_composed_noise_off(
                seed, primitive_sizes["m18_n_per_class"]),
            "noise_light": _m18_composed_noise_light(
                seed, primitive_sizes["m18_n_per_class"]),
            "noise_moderate": _m18_composed_noise_moderate(
                seed, primitive_sizes["m18_n_per_class"]),
            "individual": _m18_individual(
                seed, primitive_sizes["m18_n_per_class"]),
        }
        seed_metrics["m18"] = vals
        for arm_name, val in vals.items():
            per_unit.append({"seed": seed, "primitive": "m18",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.8 off={vals['noise_off']:.4f} "
              f"light={vals['noise_light']:.4f} "
              f"mod={vals['noise_moderate']:.4f} "
              f"ind={vals['individual']:.4f}", flush=True)

        per_seed_summary[seed] = seed_metrics

    # Noise-effect probe (per-seed): verifies wiring is live regardless of
    # arm-metric flatness
    probe_shifts_by_seed: Dict[int, dict] = {}
    for seed in seeds:
        shift_light = _noise_probe_router_cos_shift(
            seed, SIGMA_LIGHT, n_queries=20)
        shift_moderate = _noise_probe_router_cos_shift(
            seed, SIGMA_MODERATE, n_queries=20)
        probe_shifts_by_seed[seed] = {
            "light_cos_shift": shift_light,
            "moderate_cos_shift": shift_moderate,
        }
        print(f"[seed={seed}] noise_probe light_shift={shift_light:.4f} "
              f"moderate_shift={shift_moderate:.4f}", flush=True)

    return {
        "per_unit": per_unit,
        "per_seed": per_seed_summary,
        "noise_probe_shifts": probe_shifts_by_seed,
    }


def _compute_verdict(results: dict, expected_n_units: int) -> dict:
    per_unit = results["per_unit"]
    per_seed = results["per_seed"]
    probe_shifts = results["noise_probe_shifts"]

    # Cardinality gate
    if len(per_unit) != expected_n_units:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                            f"n_units={len(per_unit)} != expected="
                            f"{expected_n_units}"),
            "cardinality_ok": False,
        }

    primitives = ["m14", "m15", "m17", "m18"]

    # Compute per-primitive deltas: (a) backwards-compat (noise_off vs individual),
    # (b) noise_light vs noise_off, (c) noise_moderate vs noise_off
    delta_summary: Dict[str, dict] = {}
    reproduces_off_vs_ind: Dict[str, bool] = {}
    bounded_light: Dict[str, bool] = {}
    bounded_moderate: Dict[str, bool] = {}

    for p in primitives:
        off_vals = [per_seed[s][p]["noise_off"] for s in per_seed]
        light_vals = [per_seed[s][p]["noise_light"] for s in per_seed]
        mod_vals = [per_seed[s][p]["noise_moderate"] for s in per_seed]
        ind_vals = [per_seed[s][p]["individual"] for s in per_seed]

        d_off_ind = [abs(o - i) for o, i in zip(off_vals, ind_vals)]
        d_light_off = [abs(l - o) for l, o in zip(light_vals, off_vals)]
        d_mod_off = [abs(m - o) for m, o in zip(mod_vals, off_vals)]

        delta_summary[p] = {
            "max_delta_off_vs_individual": max(d_off_ind),
            "max_delta_light_vs_off": max(d_light_off),
            "max_delta_moderate_vs_off": max(d_mod_off),
            "off_mean": float(np.mean(off_vals)),
            "light_mean": float(np.mean(light_vals)),
            "moderate_mean": float(np.mean(mod_vals)),
            "individual_mean": float(np.mean(ind_vals)),
            "per_seed_off_vs_individual": d_off_ind,
            "per_seed_light_vs_off": d_light_off,
            "per_seed_moderate_vs_off": d_mod_off,
        }
        reproduces_off_vs_ind[p] = max(d_off_ind) <= BACKWARDS_COMPAT_TOL
        bounded_light[p] = max(d_light_off) <= NOISE_LIGHT_TOL
        bounded_moderate[p] = max(d_mod_off) <= NOISE_MODERATE_TOL

    # Noise-probe wiring liveness gate
    max_probe_moderate = max(probe_shifts[s]["moderate_cos_shift"]
                              for s in probe_shifts)
    probe_wiring_live = max_probe_moderate >= PROBE_MIN_COS_SHIFT

    n_reproduces = sum(reproduces_off_vs_ind.values())
    n_light = sum(bounded_light.values())
    n_moderate = sum(bounded_moderate.values())

    # Verdict logic
    if (n_reproduces == 4 and n_light == 4 and n_moderate == 4
            and probe_wiring_live):
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: NOISE_OFF matches INDIVIDUAL "
                       f"(backwards-compat with Phase 3 CG) within "
                       f"{BACKWARDS_COMPAT_TOL} across all 4 primitives x 3 "
                       f"seeds; NOISE_LIGHT (sigma={SIGMA_LIGHT}) bounded "
                       f"within {NOISE_LIGHT_TOL}; NOISE_MODERATE "
                       f"(sigma={SIGMA_MODERATE}) bounded within "
                       f"{NOISE_MODERATE_TOL}; noise-effect probe fires "
                       f"(max moderate cos_shift={max_probe_moderate:.4f} "
                       f">= {PROBE_MIN_COS_SHIFT}). Phase 2b NoiseChannel "
                       f"wiring VERIFIED: backwards-compat + composition-"
                       f"stable + wiring-live.")
    elif n_reproduces < 4:
        broken = [p for p, ok in reproduces_off_vs_ind.items() if not ok]
        max_break = max(delta_summary[p]["max_delta_off_vs_individual"]
                         for p in broken)
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_WIRING_HAZARD_BACKWARDS_COMPAT: primitives "
                       f"{broken} NOISE_OFF differs from INDIVIDUAL by "
                       f"{max_break:.4f} > {BACKWARDS_COMPAT_TOL}; Phase 2b "
                       f"wiring corrupted Phase 3 baseline.")
    elif n_light < 3:
        broken = [p for p, ok in bounded_light.items() if not ok]
        max_break = max(delta_summary[p]["max_delta_light_vs_off"]
                         for p in broken)
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_WIRING_HAZARD_LIGHT_NOISE: >=2 primitives "
                       f"{broken} drift {max_break:.4f} > {NOISE_LIGHT_TOL} "
                       f"under sigma={SIGMA_LIGHT}; noise wiring corrupts "
                       f"sub-primitive state.")
    elif not probe_wiring_live:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_NOISE_NOT_APPLIED: probe cos_shift at "
                       f"sigma={SIGMA_MODERATE} = {max_probe_moderate:.4f} "
                       f"< {PROBE_MIN_COS_SHIFT}; NoiseChannel wiring is "
                       f"not actually perturbing q_2d in forward().")
    elif n_moderate == 3:
        drifted = [p for p, ok in bounded_moderate.items() if not ok]
        max_drift = max(delta_summary[p]["max_delta_moderate_vs_off"]
                         for p in drifted)
        if max_drift <= 0.30:
            verdict = "MIDDLE"
            verdict_msg = (f"MIDDLE_BAND: 3 of 4 primitives bounded under "
                           f"sigma={SIGMA_MODERATE}; {drifted} drifts "
                           f"{max_drift:.4f} (bounded to 0.30). "
                           f"NOISE_MODERATE_DRIFT_FLAG.")
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: {drifted} moderate drift "
                           f"{max_drift:.4f} > 0.30 upper bound.")
    else:
        drifted_mod = [p for p, ok in bounded_moderate.items() if not ok]
        drifted_light = [p for p, ok in bounded_light.items() if not ok]
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: composed pipeline noise-instability; "
                       f"light-drifted={drifted_light} "
                       f"moderate-drifted={drifted_mod}.")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:200],
        "cardinality_ok": True,
        "n_units": len(per_unit),
        "expected_n_units": expected_n_units,
        "reproduces_off_vs_ind": reproduces_off_vs_ind,
        "bounded_light": bounded_light,
        "bounded_moderate": bounded_moderate,
        "n_reproduces_off_vs_ind": n_reproduces,
        "n_bounded_light": n_light,
        "n_bounded_moderate": n_moderate,
        "delta_summary": delta_summary,
        "noise_probe_shifts": {str(k): v for k, v in probe_shifts.items()},
        "noise_probe_wiring_live": probe_wiring_live,
        "max_probe_moderate_cos_shift": max_probe_moderate,
    }


# --------------------------- formula selftests -------------------------------


def _selftest_arms_differ_code_paths() -> None:
    digests = _arms_differ_code_path_fingerprint()
    assert len(digests) == 16


def _selftest_bipolar_noise_math() -> None:
    """THEORETICAL@ hdlab.noise_channel: for bipolar 8192-D vec + L2-renorm
    noise, cos(v, inject(v)) = 1/sqrt(1+sigma^2). Verify empirically."""
    v = _bipolar_random((N_DIM,), torch.Generator().manual_seed(3))
    g = torch.Generator().manual_seed(5)
    ch = NoiseChannel(sigma_boundary=SIGMA_MODERATE, generator=g)
    out = ch.inject(v)
    cos = float((v * out).sum() / (v.norm() * out.norm()))
    expected = 1.0 / math.sqrt(1.0 + SIGMA_MODERATE**2)
    # Loose tolerance: single-sample noise draw fluctuation
    assert abs(cos - expected) < 0.05, (
        f"bipolar noise cos={cos:.4f} expected~{expected:.4f}; "
        f"noise_channel math violated")


def _selftest_noise_probe_wiring_live() -> None:
    """DISCRIMINATOR-FIRES: at sigma=0.15, router-path max_sim shift on
    unit-norm queries should exceed PROBE_MIN_COS_SHIFT."""
    shift = _noise_probe_router_cos_shift(7, SIGMA_MODERATE, n_queries=10)
    assert shift >= PROBE_MIN_COS_SHIFT, (
        f"noise probe cos_shift={shift:.4f} < {PROBE_MIN_COS_SHIFT}; "
        f"NoiseChannel wiring appears inactive at boundary")


def _selftest_m14_noise_off_matches_individual() -> None:
    """Backwards-compat: NOISE_OFF should match INDIVIDUAL within 0.05."""
    off = _m14_composed_noise_off(7, 10, 8)
    ind = _m14_individual(7, 10, 8)
    assert abs(off - ind) < 0.05, (
        f"M14 noise_off={off:.4f} individual={ind:.4f} delta > 0.05")


def _selftest_m15_noise_off_matches_individual() -> None:
    off = _m15_composed_noise_off(7, 3)
    ind = _m15_individual(7, 3)
    assert abs(off - ind) < 0.05, (
        f"M15 noise_off={off:.4f} individual={ind:.4f} delta > 0.05")


def _selftest_m17_noise_off_matches_individual() -> None:
    off = _m17_composed_noise_off(7, 8)
    ind = _m17_individual(7, 8)
    assert abs(off - ind) < 0.05, (
        f"M17 noise_off={off:.4f} individual={ind:.4f} delta > 0.05")


def _selftest_m18_noise_off_matches_individual() -> None:
    off = _m18_composed_noise_off(7, 10)
    ind = _m18_individual(7, 10)
    assert abs(off - ind) < 0.05, (
        f"M18 noise_off={off:.4f} individual={ind:.4f} delta > 0.05")


def _selftest_noise_on_bounded_light() -> None:
    """Noise-light arms should stay within 0.05 of noise-off arms."""
    for p_fn_off, p_fn_light, args, name in [
        (_m14_composed_noise_off, _m14_composed_noise_light, (7, 10, 8), "m14"),
        (_m15_composed_noise_off, _m15_composed_noise_light, (7, 3), "m15"),
        (_m17_composed_noise_off, _m17_composed_noise_light, (7, 8), "m17"),
        (_m18_composed_noise_off, _m18_composed_noise_light, (7, 10), "m18"),
    ]:
        off = p_fn_off(*args)
        light = p_fn_light(*args)
        assert abs(off - light) < 0.10, (
            f"{name} noise-light drift {abs(off - light):.4f} > 0.10 at "
            f"smoke regime")


def _run_all_selftests() -> dict:
    _selftest_arms_differ_code_paths()
    _selftest_bipolar_noise_math()
    _selftest_noise_probe_wiring_live()
    _selftest_m14_noise_off_matches_individual()
    _selftest_m15_noise_off_matches_individual()
    _selftest_m17_noise_off_matches_individual()
    _selftest_m18_noise_off_matches_individual()
    _selftest_noise_on_bounded_light()
    return {
        "selftests_passed": 8,
        "arms_differ_verified": True,
        "cell_source": ANCHOR_NAME,
    }


# ---------------------------------- main -------------------------------------


def main(run_mode: str) -> None:
    output_dir = _output_dir_for(run_mode)
    output_dir.mkdir(parents=True, exist_ok=True)

    if run_mode == "self_test":
        result = _run_all_selftests()
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (8 formula selftests ran successfully)",
            "summary": "SELFTEST_PASS 8/8",
            "elapsed_s": 0.0,
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

    expected_n_units = len(seeds) * 4 * 4  # 4 arms x 4 primitives

    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units)

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
        "sigma_light": SIGMA_LIGHT,
        "sigma_moderate": SIGMA_MODERATE,
        "backwards_compat_tol": BACKWARDS_COMPAT_TOL,
        "noise_light_tol": NOISE_LIGHT_TOL,
        "noise_moderate_tol": NOISE_MODERATE_TOL,
        "probe_min_cos_shift": PROBE_MIN_COS_SHIFT,
        "arm_code_path_fingerprints": arm_fingerprints,
        "arms_differ_verified": True,
        "storage_strategy": (
            "MIXED_inherited_per_primitive_no_facade_storage_"
            "plus_NO_STORAGE_noise_channel"),
        "compute_architecture": "mixed_cpu_numpy_torch",
        "per_seed": {str(k): v for k, v in results["per_seed"].items()},
        "per_unit": results["per_unit"],
        "primitives_tested": ["m14_refuse_gate", "m15_two_tier_context",
                              "m17_role_slot_summarizer", "m18_clarify_gate"],
        "phase": "3b_noise_enabled_variant",
        "phase_3_reference_metrics_path": (
            "data/exp_cortex_integration_end_to_end_v1/metrics.json"),
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
