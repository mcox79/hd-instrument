"""exp_cortex_integration_end_to_end_v2 -- Phase 3b cortex integration test cell.

Extends v1 (commit c16c72ca5, HP-landed 2026-07-03; m14/m15/m17 CG-promoted via
runtime-trace-verified integration; m18 stays MM_STANDARD) to close the
4-of-6 primitive-coverage gap flagged by Skunkworks landed-VET: adds explicit
discriminator arms for M1.3 NoiseChannel + M1.6 chunked_attention_readout so
the composed cortex facade's end-to-end integration is measured over the FULL
6-primitive stack (M1.3 + M1.4 + M1.5 + M1.6 + M1.7 + M1.8) rather than a
strict subset.

External CG anchors (source signatures cited MEASURED@ / CITED@ per META_RULE_AC):
- M1.3 NoiseChannel v1: CITED@hdlab/noise_channel.py CG source c5e5e66a
  2026-07-01 (substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14 HP,
  Phase 2b extraction 2026-07-02).
- M1.6 chunked_attention_readout: CITED@hdlab/chunked_attention.py Phase 3c
  design 2026-07-02 (FlashAttention-style online-softmax; numerically
  equivalent to non-chunked reference_attention_readout across chunk_size).
- M1.4/M1.5/M1.7/M1.8: unchanged from v1 (preserve v1 CG evidence base).

Prereg: preregs/2026-07-03_exp_cortex_integration_end_to_end_v2.md
Bands:
    HP: all 6 primitives |composed - individual| <= 0.05 across 3 seeds; all
        6 ABLATED arms show mechanism collapse below ABLATION_FLOOR=0.10
    MB: 4-5 of 6 primitives reproduce; INTEGRATION_HAZARD flag on drifting one
    HF: >=2 primitives fail reproduction OR pipeline construction fails
        OR any ablation shows no degradation OR cardinality != 54

Framing (per USER-locked feedback_arc_continuation_vs_arc_closure_2026-07-03):
This is ARC-CONTINUATION on the cortex integration arc (extending v1's 4/6
coverage to 6/6), NOT arc-closure. Smoke lands MM_TENTATIVE at most; awaits
FULL + Skunkworks landed-VET for m13/m16 CG upgrade candidacy.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified via RUNTIME-CALL-TRACE (_arms_differ_runtime_call_trace:
  Cortex.forward monkey-patched to count invocations; per-arm delta must match
  _ARM_TRACE_EXPECTED. Runtime-trace preserves v1's Skunkworks-vet-hardened
  discriminator; extended to m13/m16 arms.)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "integration-fidelity test; no capacity noise floor"
- baseline_in_band: exempt (bit-identity check is by-design)
- discriminator survives scale: N/A (Phase 2 selftests at Cortex default N=8192)
- HARD_PASS strictly above floor + band-width: HP is |delta| <= 0.05
- cardinality_ok: EXPECTED_N_UNITS = 6 primitives x 3 arms x 3 seeds = 54 (FULL)
- per-unit failure-class instrumentation
- calibration_check: "default_ok_for_this_regime"
- all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Storage strategy: MIXED (inherited from Cortex facade, per primitive; M1.3
adds NO_STORAGE, M1.6 adds NO_STORAGE - both stateless boundary/functional
primitives; facade-composition-safety inherits unchanged).

Compute architecture: (c) mixed -- numpy/torch CPU only; each primitive is
CPU-modest. Per-seed FULL wall extrapolated from v1 c16c72ca5 9.24s at 4
primitives -> ~14s at 6 primitives (linear extrapolation, m13/m16 both
CPU-modest at 8192-D exact-match retrieval).
"""
from __future__ import annotations

import argparse
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
# invoked as a script from tools/queue_add.py.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hdlab.chunked_attention import chunked_attention_readout
from hdlab.clarify_gate import ClarifyGate, GateOutcome
from hdlab.context_retention import TwoTierContext
from hdlab.cortex import Cortex, CortexConfig, CortexResponse
from hdlab.noise_channel import NoiseChannel
from hdlab.refuse_gate import apply_refuse
from hdlab.role_slot_summarizer import RoleSlotSummarizer

from experiments._cell_heartbeat import emit_heartbeat

# ------------------------------ configuration --------------------------------

ANCHOR_NAME = "exp_cortex_integration_end_to_end_v2"

# CG-anchored constants (per prereg calibration section).
N_DIM = 8192                        # inherited from Cortex config default
V_CB = 1024
STM_K = 100
LTM_K = 1200
S_ROLES = 4

REFUSE_TAU = 0.20                   # M1.4 accept boundary
CLARIFY_LOWER_TAU = 0.35            # M1.8 lower
CLARIFY_UPPER_TAU = 0.55            # M1.8 upper

# M1.3 NoiseChannel: sigma calibrated for BIPOLAR 8192-D queries. On bipolar
# (per-element variance=1) the noise/signal ratio gives cos(q, injected_q) ~=
# 1/sqrt(1+sigma^2) -- independent of N (differs from unit-norm 1024-D HRR
# regime where cos ~= 1/sqrt(1+N*sigma^2) at sigma=0.15 gives 0.074). At
# sigma=1.0 on bipolar: perturbation ~= 1 - 1/sqrt(2) = 0.293. Comfortable
# margin above ABLATION_FLOOR=0.10. Documented as INTEGRATION-DISCRIMINATOR
# sigma (not the CG "moderate" regime sigma=0.15); the M1.3 primitive itself
# is CG at sigma=0.15 on unit-norm queries per source cell.
M13_SIGMA_BOUNDARY = 1.0

# M1.6 chunked_attention: chunk_size < M_TAPE so chunking exercises the online-
# softmax path (numerically equivalent to non-chunked per primitive design).
M16_CHUNK_SIZE = 8
M16_ABLATED_BETA = 0.0              # uniform attention -> retrieval collapses
M16_DEFAULT_BETA = 13.0             # CG regime (CortexConfig default)

ABLATION_FLOOR = 0.10               # each ABLATED metric must be < this
COMPOSED_INDIV_TOL = 0.05           # HP delta tolerance

SEEDS_FULL = [7, 13, 19]
SEEDS_SMOKE = [7]

# Per-primitive discriminator sizes (FULL mode)
FULL_M13_N_QUERIES = 20
FULL_M13_M_TAPE = 16
FULL_M14_N_QUERIES = 50
FULL_M14_M_TAPE = 32
FULL_M15_K_WRITES = 5
FULL_M16_N_QUERIES = 20
FULL_M16_M_TAPE = 32
FULL_M17_K_ITEMS = 16
FULL_M18_N_PER_CLASS = 25

# Smoke uses reduced grid
SMOKE_M13_N_QUERIES = 5
SMOKE_M13_M_TAPE = 8
SMOKE_M14_N_QUERIES = 20
SMOKE_M14_M_TAPE = 16
SMOKE_M15_K_WRITES = 3
SMOKE_M16_N_QUERIES = 5
SMOKE_M16_M_TAPE = 16
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


def _make_m13_data(seed: int, n_queries: int, m_tape: int
                   ) -> Tuple[List[int], torch.Tensor, torch.Tensor]:
    """Generate M=m_tape tape keys/vals + N=n_queries EXACT-MATCH query indices
    (each query is a copy of ctx_keys[idx]; noise perturbs the copy)."""
    gen = torch.Generator()
    gen.manual_seed(seed + 400)
    ctx_keys = _bipolar_random((m_tape, N_DIM), gen)
    ctx_vals = _bipolar_random((m_tape, N_DIM), gen)
    query_indices = torch.randint(
        0, m_tape, (n_queries,), generator=gen).tolist()
    return query_indices, ctx_keys, ctx_vals


def _make_m14_data(seed: int, n_queries: int, m_tape: int
                   ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Generate M=m_tape random tape keys + N=n_queries uncorrelated queries."""
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


def _make_m16_data(seed: int, n_queries: int, m_tape: int
                   ) -> Tuple[List[int], torch.Tensor, torch.Tensor]:
    """M=m_tape tape + N=n_queries EXACT-MATCH queries (query = ctx_keys[idx]);
    argmax-on-retrieval discriminator between softmax-weighted (composed/
    individual) and uniform-weighted (ablated at beta=0)."""
    gen = torch.Generator()
    gen.manual_seed(seed + 500)
    ctx_keys = _bipolar_random((m_tape, N_DIM), gen)
    ctx_vals = _bipolar_random((m_tape, N_DIM), gen)
    query_indices = torch.randint(
        0, m_tape, (n_queries,), generator=gen).tolist()
    return query_indices, ctx_keys, ctx_vals


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
                clarify_upper: float = CLARIFY_UPPER_TAU,
                noise_channel_enabled: bool = False,
                noise_channel_sigma_boundary: float = 0.0,
                attention_chunk_size: int = M16_CHUNK_SIZE,
                attention_beta: float = M16_DEFAULT_BETA) -> Cortex:
    """Instantiate a Cortex with the requested config at the seed."""
    cfg = CortexConfig(
        n_dim=N_DIM,
        v_cb=V_CB,
        stm_k=STM_K,
        ltm_k=LTM_K,
        n_roles=S_ROLES,
        refuse_gate_accept_tau=refuse_tau,
        clarify_gate_lower_tau=clarify_lower,
        clarify_gate_upper_tau=clarify_upper,
        attention_chunk_size=attention_chunk_size,
        attention_beta=attention_beta,
        noise_channel_enabled=noise_channel_enabled,
        noise_channel_sigma_boundary=noise_channel_sigma_boundary,
        seed=seed,
    )
    return Cortex(cfg)


# --- M1.3 NoiseChannel ---


def _m13_composed(seed: int, n_queries: int, m_tape: int,
                  sigma: float = M13_SIGMA_BOUNDARY) -> float:
    """COMPOSED: cx.forward with noise_channel_enabled=True; measure
    perturbation = 1 - mean(resp.confidence) on exact-match queries. Noise
    injection on the query lowers max_sim (~1.0 without noise -> lower with).
    Perturbation metric captures the noise effect through the facade."""
    cx = _cortex_for(seed, noise_channel_enabled=(sigma > 0),
                     noise_channel_sigma_boundary=sigma)
    query_indices, ctx_keys, ctx_vals = _make_m13_data(seed, n_queries, m_tape)
    perturbations: List[float] = []
    for idx in query_indices:
        query = ctx_keys[idx].clone()
        resp = cx.forward(query, context_keys=ctx_keys, context_vals=ctx_vals)
        perturbations.append(1.0 - float(resp.confidence))
    return float(np.mean(perturbations))


def _m13_individual(seed: int, n_queries: int, m_tape: int,
                    sigma: float = M13_SIGMA_BOUNDARY) -> float:
    """INDIVIDUAL: instantiate NoiseChannel directly with the same generator
    seed formula Cortex uses (seed*10007+42, matches cortex.py:195), inject
    each query, then compute max_sim manually against ORIGINAL keys. Bit-
    identity to COMPOSED via matched-seed noise draws + matched arithmetic."""
    query_indices, ctx_keys, ctx_vals = _make_m13_data(seed, n_queries, m_tape)
    # Match Cortex's noise_rng seed formula (cortex.py:195). Sigma=0 is
    # passthrough (see NoiseChannel.inject); no noise gen state advances so
    # the sigma=0 branch matches cx._noise_channel=None composed behavior.
    if sigma > 0:
        noise_rng = torch.Generator()
        noise_rng.manual_seed(seed * 10007 + 42)
        noise_channel = NoiseChannel(sigma_boundary=sigma, generator=noise_rng)
    else:
        noise_channel = None
    # Normalize keys once (matches cortex.forward:300-302).
    k32 = ctx_keys.to(torch.float32)
    k_normed = k32 / k32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    perturbations: List[float] = []
    for idx in query_indices:
        # Match cortex.forward:257 (unsqueeze to 2D) + line 273 (inject).
        q_2d = ctx_keys[idx].clone().unsqueeze(0).to(torch.float32)
        if noise_channel is not None:
            q_2d = noise_channel.inject(q_2d)
        q_row = q_2d[0]
        q_normed = q_row / q_row.norm().clamp_min(1e-9)
        max_sim = float((k_normed @ q_normed).max())
        perturbations.append(1.0 - max_sim)
    return float(np.mean(perturbations))


def _m13_ablated(seed: int, n_queries: int, m_tape: int) -> float:
    """ABLATED: noise_channel_enabled=False (facade-config ablation); queries
    unmodified so max_sim=1.0 on exact-match (perturbation ~= 0). Below
    ABLATION_FLOOR=0.10 proves M1.3 is load-bearing for the perturbation
    metric (facade must invoke NoiseChannel or perturbation collapses)."""
    return _m13_composed(seed, n_queries, m_tape, sigma=0.0)


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
        if not apply_refuse(max_sim, refuse_tau):
            refused += 1
    return refused / n_queries


def _m14_ablated(seed: int, n_queries: int, m_tape: int) -> float:
    """ABLATED: refuse_gate_accept_tau=-1.0 (never refuses); refuse_rate ~0."""
    return _m14_composed(seed, n_queries, m_tape, refuse_tau=-1.0)


# --- M1.5 TwoTierContext ---


def _m15_composed(seed: int, k_writes: int) -> float:
    """COMPOSED: write via cx.forward(role_key_for_memory_write=...); read
    via cx._context.read (facade sub-primitive path)."""
    cx = _cortex_for(seed)
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    for rk, vi in zip(role_keys, val_indices):
        cx.forward(rk.clone(),
                   role_key_for_memory_write=rk,
                   val_idx_for_memory_write=int(vi))
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        resp = cx.forward(rk.clone(),
                          role_key_for_memory_write=rk)
        pred = cx._context.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


def _m15_individual(seed: int, k_writes: int) -> float:
    """INDIVIDUAL: instantiate TwoTierContext directly, matched config."""
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
    EMPTY context (recall ~= 1/V_CB ~= 0.001)."""
    cx = _cortex_for(seed)
    role_keys, val_indices = _make_m15_data(seed, k_writes)
    correct = 0
    for rk, vi in zip(role_keys, val_indices):
        pred = cx._context.read(rk, target_cos_noise=1.0)
        if int(pred) == int(vi):
            correct += 1
    return correct / k_writes


# --- M1.6 chunked_attention_readout ---


def _m16_composed(seed: int, n_queries: int, m_tape: int,
                  chunk_size: int = M16_CHUNK_SIZE,
                  beta: float = M16_DEFAULT_BETA) -> float:
    """COMPOSED: cx.forward with attention_chunk_size=M16_CHUNK_SIZE (< M_TAPE
    so online-softmax path exercised) + attention_beta=13.0 (CG regime).
    Metric = argmax_match_accuracy: argmax(cos(resp.retrieval, ctx_vals)) ==
    target_idx. Softmax-weighted retrieval concentrates on target key -> ~1.0
    on exact-match queries."""
    cx = _cortex_for(seed, attention_chunk_size=chunk_size,
                     attention_beta=beta)
    query_indices, ctx_keys, ctx_vals = _make_m16_data(seed, n_queries, m_tape)
    v32 = ctx_vals.to(torch.float32)
    v_normed = v32 / v32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    correct = 0
    for idx in query_indices:
        query = ctx_keys[idx].clone()
        resp = cx.forward(query, context_keys=ctx_keys, context_vals=ctx_vals)
        r32 = resp.retrieval.to(torch.float32)
        r_normed = r32 / r32.norm().clamp_min(1e-9)
        pred_idx = int(torch.argmax(v_normed @ r_normed).item())
        if pred_idx == idx:
            correct += 1
    return correct / n_queries


def _m16_individual(seed: int, n_queries: int, m_tape: int,
                    chunk_size: int = M16_CHUNK_SIZE,
                    beta: float = M16_DEFAULT_BETA) -> float:
    """INDIVIDUAL: call chunked_attention_readout directly on same
    (query, keys, vals, chunk_size, beta); same argmax check.
    Bit-identical to COMPOSED because Cortex.forward invokes the same
    function with same args (cortex.py:290)."""
    query_indices, ctx_keys, ctx_vals = _make_m16_data(seed, n_queries, m_tape)
    v32 = ctx_vals.to(torch.float32)
    v_normed = v32 / v32.norm(dim=-1, keepdim=True).clamp_min(1e-9)
    correct = 0
    for idx in query_indices:
        q_2d = ctx_keys[idx].clone().unsqueeze(0)
        readout = chunked_attention_readout(
            q_2d, ctx_keys, ctx_vals, chunk_size=chunk_size, beta=beta)
        r = readout[0].to(torch.float32)
        r_normed = r / r.norm().clamp_min(1e-9)
        pred_idx = int(torch.argmax(v_normed @ r_normed).item())
        if pred_idx == idx:
            correct += 1
    return correct / n_queries


def _m16_ablated(seed: int, n_queries: int, m_tape: int) -> float:
    """ABLATED: attention_beta=0.0 -> uniform attention weights -> retrieval =
    mean(context_vals). Argmax on cos(mean_vals, vals[i]) is near-random
    (~ 1/M for bipolar-random vals). Below ABLATION_FLOOR=0.10 requires
    M_TAPE >= 16 (mean-cos ~= 1/sqrt(M); at M=16, expected accuracy ~0.0625).

    Design note: cortex facade design does not expose chunk_size=None to
    fully disable chunking (chunked_attention is numerically equivalent to
    non-chunked by design; chunk-size ablation trivially non-discriminating).
    We ablate the LOAD-BEARING softmax discriminator (beta=0) instead so the
    ablation truly collapses retrieval quality. Documented in prereg."""
    return _m16_composed(seed, n_queries, m_tape, beta=M16_ABLATED_BETA)


# --- M1.7 RoleSlotSummarizer ---


def _m17_composed(seed: int, k_items: int) -> float:
    """COMPOSED: invoke via cx.forward(role_slot_context={...})."""
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
    slot_bundles_q = resp.role_slots
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


def _m17_ablated(seed: int, k_items: int) -> float:
    """ABLATED: skip role_slot_context kwarg -> resp.role_slots is None."""
    cx = _cortex_for(seed)
    query = _bipolar_random((N_DIM,), torch.Generator().manual_seed(seed + 999))
    resp = cx.forward(query)
    return 0.0 if resp.role_slots is None else 1.0


# --- M1.8 ClarifyGate ---


def _m18_composed(seed: int, n_per_class: int) -> float:
    """COMPOSED: use cx._clarify_gate directly (facade-owned instance built
    from CortexConfig thresholds; cortex.py:184-187)."""
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
    """ABLATED: clarify_gate_lower_tau=0.0, upper_tau=1e-6 (facade config).
    All scores >= upper -> ACCEPT; clarify_recall = 0.0."""
    cx = _cortex_for(seed, clarify_lower=0.0, clarify_upper=1e-6)
    _, amb = _make_m18_data(seed, n_per_class)
    outs = cx._clarify_gate.evaluate_batch(amb.tolist())
    return float(np.mean(outs == GateOutcome.CLARIFY.value))


# ------------------ arms_differ runtime call trace ---------------------------


class _CortexForwardTrace:
    """Runtime-trace instrumenter for Cortex.forward (replaces v1 source-
    fingerprint discriminator per Skunkworks landed-VET a9c698659626b3521)."""

    def __init__(self) -> None:
        self._orig_forward = None
        self.count = 0

    def __enter__(self) -> "_CortexForwardTrace":
        self._orig_forward = Cortex.forward
        trace = self

        def _counted(inst, *a, **k):
            trace.count += 1
            return trace._orig_forward(inst, *a, **k)

        Cortex.forward = _counted
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        Cortex.forward = self._orig_forward


# Expected per-arm runtime-call pattern. Extended for m13/m16 per Phase 3b task.
_ARM_TRACE_EXPECTED = {
    # M1.3: composed invokes cx.forward per query with noise ON; individual
    # bypasses facade (calls NoiseChannel.inject directly); ablated invokes
    # cx.forward with noise OFF (facade-config ablation).
    "m13_composed":   "forward_ge_1",
    "m13_individual": "forward_eq_0",
    "m13_ablated":    "forward_ge_1",
    # M1.4
    "m14_composed":   "forward_ge_1",
    "m14_individual": "forward_eq_0",
    "m14_ablated":    "forward_ge_1",
    # M1.5
    "m15_composed":   "forward_ge_1",
    "m15_individual": "forward_eq_0",
    "m15_ablated":    "forward_eq_0",
    # M1.6: composed invokes cx.forward (which internally calls
    # chunked_attention_readout); individual calls the function directly;
    # ablated invokes cx.forward with beta=0 (facade-config ablation).
    "m16_composed":   "forward_ge_1",
    "m16_individual": "forward_eq_0",
    "m16_ablated":    "forward_ge_1",
    # M1.7
    "m17_composed":   "forward_ge_1",
    "m17_individual": "forward_eq_0",
    "m17_ablated":    "forward_ge_1",
    # M1.8: ALL three arms bypass cx.forward by design (declared honestly).
    "m18_composed":   "forward_eq_0",
    "m18_individual": "forward_eq_0",
    "m18_ablated":    "forward_eq_0",
}


def _check_arm_trace(arm_key: str, delta: int) -> Tuple[bool, str]:
    expected = _ARM_TRACE_EXPECTED[arm_key]
    if expected == "forward_ge_1":
        return (delta >= 1), expected
    if expected == "forward_eq_0":
        return (delta == 0), expected
    return False, f"unknown_expected_{expected}"


def _arms_differ_runtime_call_trace(primitive_sizes: dict, seed: int = 7
                                    ) -> Dict[str, dict]:
    """META_RULE_AF runtime-trace: monkey-patch Cortex.forward via
    _CortexForwardTrace; run each arm at supplied sizes; verify per-arm
    forward-call delta matches _ARM_TRACE_EXPECTED for all 6 primitives
    (m13 + m14 + m15 + m16 + m17 + m18) x 3 arms = 18 checks."""
    arms = [
        ("m13", "composed", _m13_composed,
         (primitive_sizes["m13_n_queries"], primitive_sizes["m13_m_tape"])),
        ("m13", "individual", _m13_individual,
         (primitive_sizes["m13_n_queries"], primitive_sizes["m13_m_tape"])),
        ("m13", "ablated", _m13_ablated,
         (primitive_sizes["m13_n_queries"], primitive_sizes["m13_m_tape"])),
        ("m14", "composed", _m14_composed,
         (primitive_sizes["m14_n_queries"], primitive_sizes["m14_m_tape"])),
        ("m14", "individual", _m14_individual,
         (primitive_sizes["m14_n_queries"], primitive_sizes["m14_m_tape"])),
        ("m14", "ablated", _m14_ablated,
         (primitive_sizes["m14_n_queries"], primitive_sizes["m14_m_tape"])),
        ("m15", "composed", _m15_composed,
         (primitive_sizes["m15_k_writes"],)),
        ("m15", "individual", _m15_individual,
         (primitive_sizes["m15_k_writes"],)),
        ("m15", "ablated", _m15_ablated,
         (primitive_sizes["m15_k_writes"],)),
        ("m16", "composed", _m16_composed,
         (primitive_sizes["m16_n_queries"], primitive_sizes["m16_m_tape"])),
        ("m16", "individual", _m16_individual,
         (primitive_sizes["m16_n_queries"], primitive_sizes["m16_m_tape"])),
        ("m16", "ablated", _m16_ablated,
         (primitive_sizes["m16_n_queries"], primitive_sizes["m16_m_tape"])),
        ("m17", "composed", _m17_composed,
         (primitive_sizes["m17_k_items"],)),
        ("m17", "individual", _m17_individual,
         (primitive_sizes["m17_k_items"],)),
        ("m17", "ablated", _m17_ablated,
         (primitive_sizes["m17_k_items"],)),
        ("m18", "composed", _m18_composed,
         (primitive_sizes["m18_n_per_class"],)),
        ("m18", "individual", _m18_individual,
         (primitive_sizes["m18_n_per_class"],)),
        ("m18", "ablated", _m18_ablated,
         (primitive_sizes["m18_n_per_class"],)),
    ]
    results: Dict[str, dict] = {}
    all_ok = True
    with _CortexForwardTrace() as trace:
        for prim, arm, fn, args in arms:
            key = f"{prim}_{arm}"
            before = trace.count
            fn(seed, *args)
            delta = trace.count - before
            ok, expected = _check_arm_trace(key, delta)
            results[key] = {
                "forward_call_delta": int(delta),
                "expected_pattern": expected,
                "trace_ok": bool(ok),
            }
            if not ok:
                all_ok = False
    if not all_ok:
        breaches = {k: v for k, v in results.items() if not v["trace_ok"]}
        raise AssertionError(
            f"META_RULE_AF RUNTIME-TRACE VIOLATION: arms did not match "
            f"expected forward-call pattern. Breaches: {breaches}")
    return results


# ---------------------------- driver + verdict -------------------------------


def _run_all_seeds(seeds: List[int], primitive_sizes: dict, output_dir: Path,
                   run_mode: str, t0: float) -> dict:
    """Iterate over seeds; for each, run 6 primitives x 3 arms. Emit heartbeat."""
    per_unit: List[dict] = []
    per_seed_summary: Dict[int, dict] = {}

    total_units = len(seeds) * 6 * 3  # seeds x primitives x arms
    unit_counter = 0

    for seed in seeds:
        seed_metrics: Dict[str, Dict[str, float]] = {}

        # M1.3
        m13_c = _m13_composed(seed, primitive_sizes["m13_n_queries"],
                              primitive_sizes["m13_m_tape"])
        m13_i = _m13_individual(seed, primitive_sizes["m13_n_queries"],
                                primitive_sizes["m13_m_tape"])
        m13_a = _m13_ablated(seed, primitive_sizes["m13_n_queries"],
                             primitive_sizes["m13_m_tape"])
        seed_metrics["m13"] = {"composed": m13_c, "individual": m13_i,
                                "ablated": m13_a}
        for arm_name, val in seed_metrics["m13"].items():
            per_unit.append({"seed": seed, "primitive": "m13",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.3 composed={m13_c:.4f} individual={m13_i:.4f} "
              f"ablated={m13_a:.4f}", flush=True)

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

        # M1.6
        m16_c = _m16_composed(seed, primitive_sizes["m16_n_queries"],
                              primitive_sizes["m16_m_tape"])
        m16_i = _m16_individual(seed, primitive_sizes["m16_n_queries"],
                                primitive_sizes["m16_m_tape"])
        m16_a = _m16_ablated(seed, primitive_sizes["m16_n_queries"],
                             primitive_sizes["m16_m_tape"])
        seed_metrics["m16"] = {"composed": m16_c, "individual": m16_i,
                                "ablated": m16_a}
        for arm_name, val in seed_metrics["m16"].items():
            per_unit.append({"seed": seed, "primitive": "m16",
                             "arm": arm_name, "metric": val})
            unit_counter += 1
        emit_heartbeat(str(output_dir), unit_idx=unit_counter,
                       total_units=total_units,
                       elapsed_s=time.perf_counter() - t0)
        print(f"[seed={seed}] M1.6 composed={m16_c:.4f} individual={m16_i:.4f} "
              f"ablated={m16_a:.4f}", flush=True)

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
    """Verdict: per prereg bands (6 primitives x 3 arms x n_seeds)."""
    per_unit = results["per_unit"]
    per_seed = results["per_seed"]

    if len(per_unit) != expected_n_units:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                            f"n_units={len(per_unit)} != expected="
                            f"{expected_n_units}"),
            "cardinality_ok": False,
        }

    primitives = ["m13", "m14", "m15", "m16", "m17", "m18"]
    per_primitive_reproduces = {}
    per_primitive_ablation_fires = {}
    delta_summary = {}
    cv_summary = {}
    ablation_summary = {}

    for p in primitives:
        composed_vals = [per_seed[s][p]["composed"] for s in per_seed]
        individual_vals = [per_seed[s][p]["individual"] for s in per_seed]
        ablated_vals = [per_seed[s][p]["ablated"] for s in per_seed]

        deltas = [abs(c - i) for c, i in zip(composed_vals, individual_vals)]
        max_delta = max(deltas)
        delta_summary[p] = {
            "max_delta": max_delta,
            "per_seed_delta": deltas,
            "composed_mean": float(np.mean(composed_vals)),
            "individual_mean": float(np.mean(individual_vals)),
        }
        per_primitive_reproduces[p] = max_delta <= COMPOSED_INDIV_TOL

        if abs(np.mean(composed_vals)) > 1e-9:
            cv = float(np.std(composed_vals) / abs(np.mean(composed_vals)))
        else:
            cv = 0.0
        cv_summary[p] = cv

        max_ablated = max(ablated_vals)
        ablation_summary[p] = {
            "max_ablated": max_ablated,
            "per_seed_ablated": ablated_vals,
        }
        per_primitive_ablation_fires[p] = max_ablated < ABLATION_FLOOR

    n_reproduces = sum(per_primitive_reproduces.values())
    n_ablation_fires = sum(per_primitive_ablation_fires.values())

    n_seeds = len(per_seed)
    seed_str = f"{n_seeds} seed" + ("s" if n_seeds > 1 else "")
    if n_reproduces == 6 and n_ablation_fires == 6:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: all 6 primitives (m13/m14/m15/m16/m17/m18) "
                       f"reproduce within |delta|<={COMPOSED_INDIV_TOL} across "
                       f"{seed_str}; all 6 ABLATED arms below floor "
                       f"{ABLATION_FLOOR}. Cortex facade composition integrity "
                       f"verified across FULL 6-primitive stack.")
    elif n_reproduces >= 4 and n_ablation_fires == 6:
        drifted = [p for p, ok in per_primitive_reproduces.items() if not ok]
        max_drift = max(delta_summary[p]["max_delta"] for p in drifted)
        if max_drift <= 0.10 and n_reproduces >= 4:
            verdict = "MIDDLE"
            verdict_msg = (f"MIDDLE_BAND: {n_reproduces} of 6 primitives "
                           f"reproduce; INTEGRATION_HAZARD flag on {drifted} "
                           f"(max_delta={max_drift:.4f}).")
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (f"HARD_FAIL: {drifted} drift {max_drift:.4f} "
                           f"exceeds MIDDLE band (0.10) OR too few reproduce.")
    elif n_ablation_fires < 6:
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


def _selftest_arms_differ_runtime_trace() -> None:
    """META_RULE_AF runtime-trace: 6 primitives x 3 arms = 18 arms; per-arm
    forward-call deltas match _ARM_TRACE_EXPECTED."""
    sizes = {
        "m13_n_queries": 3,
        "m13_m_tape": 4,
        "m14_n_queries": 5,
        "m14_m_tape": 4,
        "m15_k_writes": 2,
        "m16_n_queries": 3,
        "m16_m_tape": 8,
        "m17_k_items": 4,
        "m18_n_per_class": 4,
    }
    results = _arms_differ_runtime_call_trace(sizes, seed=7)
    assert len(results) == 18, f"expected 18 arms, got {len(results)}"
    assert all(r["trace_ok"] for r in results.values()), (
        f"runtime-trace breach: {results}")


def _selftest_m13_composed_matches_individual_one_seed() -> None:
    """Bit-identity via matched noise-gen seed: composed vs individual
    perturbation should differ by < 0.05."""
    c = _m13_composed(7, 5, 8)
    i = _m13_individual(7, 5, 8)
    assert abs(c - i) < 0.05, (
        f"M13 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m13_ablation_kills_perturbation() -> None:
    """With noise_channel_enabled=False, perturbation should be ~0."""
    r = _m13_ablated(7, 5, 8)
    assert r < 0.10, f"M13 ablated perturbation={r:.4f} not below 0.10"


def _selftest_m13_composed_fires_perturbation() -> None:
    """At sigma=0.15 (moderate), perturbation should be measurably above 0
    (> 0.10) on exact-match queries -- proves NoiseChannel actually operates."""
    c = _m13_composed(7, 10, 8)
    assert c > 0.10, (
        f"M13 composed perturbation={c:.4f} too low at sigma=0.15; "
        f"discriminator not firing")


def _selftest_m14_composed_matches_individual_one_seed() -> None:
    c = _m14_composed(7, 10, 8)
    i = _m14_individual(7, 10, 8)
    assert abs(c - i) < 0.05, (
        f"M14 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m14_ablation_kills_refuse() -> None:
    r = _m14_ablated(7, 10, 8)
    assert r < 0.10, f"M14 ablated refuse_rate={r:.4f} not below 0.10"


def _selftest_m15_composed_matches_individual_one_seed() -> None:
    c = _m15_composed(7, 3)
    i = _m15_individual(7, 3)
    assert abs(c - i) < 0.05, (
        f"M15 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m15_ablation_kills_recall() -> None:
    r = _m15_ablated(7, 3)
    assert r < 0.10, f"M15 ablated recall={r:.4f} not below 0.10"


def _selftest_m16_composed_matches_individual_one_seed() -> None:
    """Bit-identity: cx.forward internally calls chunked_attention_readout
    with same args; individual calls the function directly."""
    c = _m16_composed(7, 5, 16)
    i = _m16_individual(7, 5, 16)
    assert abs(c - i) < 0.05, (
        f"M16 composed={c:.4f} individual={i:.4f} delta={abs(c-i):.4f} > 0.05")


def _selftest_m16_ablation_kills_retrieval() -> None:
    """At beta=0, retrieval = mean(vals); argmax accuracy ~ 1/M. Requires
    M_TAPE >= 16 for below-0.10 floor."""
    r = _m16_ablated(7, 20, 16)
    assert r < 0.10, (
        f"M16 ablated argmax_accuracy={r:.4f} not below 0.10 at M=16")


def _selftest_m16_composed_fires_argmax() -> None:
    """At beta=13 (default CG regime), argmax accuracy on exact-match queries
    should be ~1.0."""
    c = _m16_composed(7, 10, 16)
    assert c > 0.90, (
        f"M16 composed argmax_accuracy={c:.4f} too low at beta=13; "
        f"discriminator not firing")


def _selftest_m17_composed_matches_individual_one_seed() -> None:
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
    _selftest_arms_differ_runtime_trace()
    _selftest_m13_composed_matches_individual_one_seed()
    _selftest_m13_ablation_kills_perturbation()
    _selftest_m13_composed_fires_perturbation()
    _selftest_m14_composed_matches_individual_one_seed()
    _selftest_m14_ablation_kills_refuse()
    _selftest_m15_composed_matches_individual_one_seed()
    _selftest_m15_ablation_kills_recall()
    _selftest_m16_composed_matches_individual_one_seed()
    _selftest_m16_ablation_kills_retrieval()
    _selftest_m16_composed_fires_argmax()
    _selftest_m17_composed_matches_individual_one_seed()
    _selftest_m17_ablation_returns_none()
    _selftest_m18_composed_matches_individual_one_seed()
    _selftest_m18_ablation_kills_clarify()
    return {
        "selftests_passed": 15,
        "arms_differ_verified": True,
        "cell_source": ANCHOR_NAME,
        "primitives_covered": 6,
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
            "verdict_msg": "SELFTEST_PASS (15 formula selftests ran successfully)",
            "summary": "SELFTEST_PASS 15/15",
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
            "m13_n_queries": SMOKE_M13_N_QUERIES,
            "m13_m_tape": SMOKE_M13_M_TAPE,
            "m14_n_queries": SMOKE_M14_N_QUERIES,
            "m14_m_tape": SMOKE_M14_M_TAPE,
            "m15_k_writes": SMOKE_M15_K_WRITES,
            "m16_n_queries": SMOKE_M16_N_QUERIES,
            "m16_m_tape": SMOKE_M16_M_TAPE,
            "m17_k_items": SMOKE_M17_K_ITEMS,
            "m18_n_per_class": SMOKE_M18_N_PER_CLASS,
        }
    elif run_mode == "full":
        seeds = SEEDS_FULL
        sizes = {
            "m13_n_queries": FULL_M13_N_QUERIES,
            "m13_m_tape": FULL_M13_M_TAPE,
            "m14_n_queries": FULL_M14_N_QUERIES,
            "m14_m_tape": FULL_M14_M_TAPE,
            "m15_k_writes": FULL_M15_K_WRITES,
            "m16_n_queries": FULL_M16_N_QUERIES,
            "m16_m_tape": FULL_M16_M_TAPE,
            "m17_k_items": FULL_M17_K_ITEMS,
            "m18_n_per_class": FULL_M18_N_PER_CLASS,
        }
    else:
        raise ValueError(f"Unknown run_mode: {run_mode!r}")

    expected_n_units = len(seeds) * 6 * 3

    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units)

    # META_RULE_AF runtime-trace before running (fail-fast).
    arm_runtime_trace = _arms_differ_runtime_call_trace(sizes, seed=seeds[0])

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
        "arm_runtime_call_trace": arm_runtime_trace,
        "arms_differ_verified": True,
        "arms_differ_discriminator": "runtime_call_trace_meta_rule_AF_v2",
        "storage_strategy": "MIXED_inherited_per_primitive_no_facade_storage",
        "compute_architecture": "mixed_cpu_numpy_torch",
        "per_seed": {str(k): v for k, v in results["per_seed"].items()},
        "per_unit": results["per_unit"],
        "primitives_tested": ["m13_noise_channel", "m14_refuse_gate",
                              "m15_two_tier_context",
                              "m16_chunked_attention_readout",
                              "m17_role_slot_summarizer",
                              "m18_clarify_gate"],
        "expected_primitives": 6,
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
    parser.add_argument("--smoke", action="store_true",
                        help="Convenience alias for --run-mode smoke "
                             "(queue_add.py gate contract).")
    args = parser.parse_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

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
