"""multihop_reasoning_scale_invariance_N_axis_gpu_v1.

Direct N-axis extension of exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.
Purpose: LIFT Atom 11 (Skunkworks 2026-07-01, MM_STANDARD) to CHAIN_GRADE by adding
independent per-step accuracy measurements at N != 8192 at the same PART_SIZE=10 regime.

Parent Ns tested at PART_SIZE=10, V_C=200:
  N=8192 (Landing 6+10 family): per-step at d=15 mean=0.858, at d=30 mean=0.682 (MEASURED)

This cell sweeps N in {4096, 16384} at fixed:
  V_C=200, PART_SIZE=10, K_set=20, n_partitions=20, n_chains=200, seeds=[7,13,19]

Arms (4):
  ARM_PART_ORACLE_15HOP_N4096
  ARM_PART_ORACLE_30HOP_N4096
  ARM_PART_ORACLE_15HOP_N16384
  ARM_PART_ORACLE_30HOP_N16384

Reference targets (per-step accuracy CENTER of HP band; MEASURED @ N=8192, PART_SIZE=10):
  REF_15HOP = 0.858  (pooled ext + ceiling cells)
  REF_30HOP = 0.682

Verdict gates (LOCKED at module init):
  HP if |per_step_mean - REF| <= 0.05 AND cv_across_seeds <= 0.10
  HF_SCALE_VARIANCE if |per_step_mean - REF| > 0.10
  HF_MECHANISM_DEATH if top1 < 0.10 at any arm

Verdict tiers:
  CHAIN_GRADE_SCALE_INVARIANT_N_AXIS -- all 4 arms HP
  PARTIAL_SCALE_INVARIANT_D15_ONLY   -- d=15 arms HP, d=30 arms not
  PARTIAL_SCALE_INVARIANT_D30_ONLY   -- d=30 arms HP, d=15 arms not (unlikely)
  SCALE_VARIANT_N_AXIS               -- HF_SCALE_VARIANCE fires
  MECHANISM_DEATH                    -- HF_MECHANISM_DEATH fires
  MIDDLE_BAND                        -- inconclusive

GPU MEMORY BUDGET (THEORETICAL@ formula):
  W at N=4096:  4096^2 * 4 = 67 MB (fp32)
  W at N=16384: 16384^2 * 4 = 1073 MB (fp32)
  Per seed: only one W (max_depth=30 covers both d=15 and d=30 chains via slice)
  Peak per seed at N=16384: ~1.1 GB -> fits 8GB VRAM comfortably

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
  final_metrics_atomicity: tmp_replace (META_RULE_AH; via _seed_checkpoint.write_metrics)
  except SystemExit: raise BEFORE except Exception (no BaseException)
  crlb_n/a: partition-oracle argmax over 10 candidates; floor=0.10 far below measured 0.85
  baseline_in_band: True (parent MEASURED refs 0.858/0.682 are 0.05 < ref < 0.95)
  discriminator survives scale: smoke does full-N (4096 + 16384) preview
  HARD_PASS strictly above floor: ± 0.05 window; HF at ± 0.10 window
  HP_SCOPE declared per-arm (see prereg)
  cardinality_ok: EXPECTED_N_UNITS declared; verdict emits BREACH sentinel
  per-unit failure-class instrumentation: try/except Exception; NO bare/BaseException
  calibration_check: default_ok_for_this_regime
  all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only; per-seed checkpoint; atexit synthesizer; zero-LLM-call assert.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# ----------------------------------------------------------------------------
# GPU GUARD (Fix #24: GPU dispatch must actually use GPU)
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed; cannot run experiment.", flush=True)
    sys.exit(1)

GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("[GPU] device=%s name=%s total_mem=%.1fGB" % (
        DEVICE, GPU_NAME, GPU_MAX_MEM_GB), flush=True)
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0
    print("[GPU] WARN: cuda not available; running on CPU. "
          "Smoke OK; full dispatch should be GPU.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)
from experiments._cell_heartbeat import CellHeartbeat

ANCHOR_NAME = "multihop_reasoning_scale_invariance_N_axis_gpu_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ----------------------------------------------------------------------------
# PRE-REG BANDS (LOCKED at module init)
# ----------------------------------------------------------------------------
# Reference per-step accuracy at N=8192, PART_SIZE=10 (MEASURED @ parent metrics.json)
REF_15HOP = 0.858  # MEASURED@parent_ext + ceiling cells; pooled mean over 90 values
REF_30HOP = 0.682  # MEASURED@ceiling cell; 90 values

# HARD_PASS: |per_step_mean - REF| <= HP_TOL
HP_TOL = 0.05
# HARD_FAIL_SCALE_VARIANCE: |per_step_mean - REF| > HF_TOL
HF_TOL = 0.10
# HARD_FAIL_MECHANISM_DEATH: top1 < DEATH_FLOOR
DEATH_FLOOR = 0.10
# cv cap for HARD_PASS claim
CV_CAP = 0.10

# Locked invariants
assert 0.0 < HP_TOL < HF_TOL < 1.0
assert 0.0 < DEATH_FLOOR < 0.5
assert 0.0 < CV_CAP <= 0.20
assert 0.5 < REF_15HOP < 1.0 and 0.5 < REF_30HOP < 1.0

# Cell config (holds fixed across arms)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20
MAX_DEPTH = 30  # covers d=15 and d=30 chains from one W per seed per N

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# N axis (the sweep)
N_VALUES = [4096, 16384]
DEPTHS = [15, 30]

# Seeds
if RUN_MODE == "smoke":
    SEEDS = [7]
    N_CHAINS_LOCAL = 30  # smoke chains
else:
    SEEDS = [7, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200

EXPECTED_N_UNITS = len(SEEDS)  # per-seed cardinality; each seed produces all 4 arms
ARMS_PER_SEED = len(N_VALUES) * len(DEPTHS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopScaleInvarianceNaxisV1: V_C=%d V_P=%d K=%d N_PARTS=%d PART_SIZE=%d "
    "depths=%s N_values=%s max_depth=%d n_chains=%d seeds=%s mode=%s encoder=%s "
    "REF_15=%.4f REF_30=%.4f HP_TOL=%.2f HF_TOL=%.2f DEATH_FLOOR=%.2f CV_CAP=%.2f"
) % (
    V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, N_VALUES, MAX_DEPTH, N_CHAINS_LOCAL, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    REF_15HOP, REF_30HOP, HP_TOL, HF_TOL, DEATH_FLOOR, CV_CAP,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from parent partition_oracle cell)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    """Bipolar bit vectors on GPU; row-normalized."""
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set):
    """VERBATIM port of Cell B v2 make_deep_chains."""
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError("make_deep_chains: only %d/%d at max_depth=%d"
                            % (len(chain_queries), n_chains, max_depth))
    return all_triples, chain_queries


def ingest_hebbian_gpu(triples, E, R, sq, n_dim, batch=1000):
    """Batched outer-product Hebbian ingest on GPU."""
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    if not triples:
        return W
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    p_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    n_total = len(tr)
    for b in range(0, n_total, batch):
        e = min(b + batch, n_total)
        s_slice = s_idx[b:e]
        p_slice = p_idx[b:e]
        o_slice = o_idx[b:e]
        K = E[s_slice] * R[p_slice] * sq
        V_ = E[o_slice]
        W = W + (V_.T @ K) / n_dim
    return W


def arm_part_oracle_at_depth(E, R, sq, W, chains_test, depth, part_size):
    """Partition-oracle routed cleanup at given depth (VERBATIM port from parent)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = E[s] * R[p] * sq
            state = W @ key
            scores = E_parts[target_part] @ state
            local_idx = int(torch.argmax(scores).item())
            s_pred = target_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "per_step_mean": round(float(np.mean(per_step_acc)), 4),
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "part_size": part_size,
            "mechanism": "partition_oracle_per_hop_gpu"}


# ----------------------------------------------------------------------------
# ARMS-MUST-DIFFER hash test (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ(arm_outputs: Dict[str, list]) -> Dict[str, str]:
    """Compute SHA256 of per-step accuracy tuple per arm; assert distinct."""
    digests = {}
    for name, per_step in arm_outputs.items():
        b = json.dumps(per_step, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()[:16]
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], (
            "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s); "
            "arm-implementation bug" % (a, b, digests[a]))
    return digests


# ----------------------------------------------------------------------------
# Self-test (formula sanity check on tiny config)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at max_depth=MAX_DEPTH=30
    triples, chains = make_deep_chains(8, V, P, max_depth=MAX_DEPTH,
                                        g=g, disallow_s=set())
    assert len(chains) == 8
    assert len(triples) == 8 * MAX_DEPTH

    # T3: ingest + part_oracle on tiny config
    W = ingest_hebbian_gpu(triples, E, R, sq, n)
    assert W.shape == (n, n)
    assert torch.isfinite(W).all()

    # T4: part_oracle at d=15 and d=30 slicing shared W
    n_parts_test = 4
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test
    r15 = arm_part_oracle_at_depth(E, R, sq, W, [c[:15] for c in chains],
                                    depth=15, part_size=part_sz_test)
    assert 0.0 <= r15["top1"] <= 1.0
    assert len(r15["per_step_acc"]) == 15
    r30 = arm_part_oracle_at_depth(E, R, sq, W, chains, depth=30,
                                    part_size=part_sz_test)
    assert 0.0 <= r30["top1"] <= 1.0
    assert len(r30["per_step_acc"]) == 30

    # T5: bands LOCKED (regression on accidental band drift)
    assert REF_15HOP == 0.858 and REF_30HOP == 0.682
    assert HP_TOL == 0.05 and HF_TOL == 0.10 and DEATH_FLOOR == 0.10
    assert CV_CAP == 0.10

    # T6: LLM call counter = 0
    assert _LLM_CALL_COUNTER[0] == 0

    # T7: N_VALUES + DEPTHS locked
    assert N_VALUES == [4096, 16384]
    assert DEPTHS == [15, 30]
    assert PART_SIZE == 10
    assert V_CONCEPTS == 200

    # T8: arms_must_differ mechanics
    fake = {"a": [0.5, 0.6, 0.7], "b": [0.5, 0.6, 0.7, 0.8]}
    digests = _arms_must_differ(fake)
    assert len(digests) == 2 and digests["a"] != digests["b"]

    # T9: GPU presence NOT required for smoke (self-test always runs before GPU check)
    print("[selftest] PASS r15_top1=%.3f r30_top1=%.3f gpu=%s" % (
        r15["top1"], r30["top1"], GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)

    out = {
        "seed": seed, "run_mode": RUN_MODE,
        "V_C": V_CONCEPTS, "V_P": V_PRED, "K_set": K_SET,
        "n_partitions": N_PARTITIONS, "part_size": PART_SIZE,
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS, "N_values": N_VALUES,
        "max_depth": MAX_DEPTH,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Per-N processing (build W once at each N; extract d=15 slice + d=30 full)
    arm_outputs_for_hash = {}
    for N in N_VALUES:
        if GPU_AVAIL:
            torch.cuda.reset_peak_memory_stats(DEVICE)
        sq = math.sqrt(N)
        print("  [seed=%d N=%d] building E (V_C=%d)" % (seed, N, V_CONCEPTS),
              flush=True)
        E = bipolar_gpu(V_CONCEPTS, N, g)
        R = bipolar_gpu(V_PRED, N, g)

        t_ing = time.time()
        triples, chains = make_deep_chains(
            N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
            g=g, disallow_s=set())
        W = ingest_hebbian_gpu(triples, E, R, sq, N)
        print("  [seed=%d N=%d] W built (%d triples, max_depth=%d) t=%.1fs" % (
            seed, N, len(triples), MAX_DEPTH, round(time.time() - t_ing, 2)),
            flush=True)

        # ARM_PART_ORACLE_15HOP_N{N}
        t_arm = time.time()
        r15 = arm_part_oracle_at_depth(E, R, sq, W, [c[:15] for c in chains],
                                        depth=15, part_size=PART_SIZE)
        r15["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r15["N"] = N
        r15["W_n_bindings"] = len(triples)
        arm_key_15 = "arm_part_oracle_15hop_n%d" % N
        out[arm_key_15] = r15
        arm_outputs_for_hash[arm_key_15] = r15["per_step_acc"]
        print("  [seed=%d N=%d] PART_ORACLE_15HOP top1=%.4f per_step_mean=%.4f "
              "(REF=%.4f, |diff|=%.4f) t=%.1fs" % (
                  seed, N, r15["top1"], r15["per_step_mean"],
                  REF_15HOP, abs(r15["per_step_mean"] - REF_15HOP),
                  r15["elapsed_s_arm"]), flush=True)

        # ARM_PART_ORACLE_30HOP_N{N}
        t_arm = time.time()
        r30 = arm_part_oracle_at_depth(E, R, sq, W, chains, depth=30,
                                        part_size=PART_SIZE)
        r30["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r30["N"] = N
        r30["W_n_bindings"] = len(triples)
        arm_key_30 = "arm_part_oracle_30hop_n%d" % N
        out[arm_key_30] = r30
        arm_outputs_for_hash[arm_key_30] = r30["per_step_acc"]
        print("  [seed=%d N=%d] PART_ORACLE_30HOP top1=%.4f per_step_mean=%.4f "
              "(REF=%.4f, |diff|=%.4f) t=%.1fs" % (
                  seed, N, r30["top1"], r30["per_step_mean"],
                  REF_30HOP, abs(r30["per_step_mean"] - REF_30HOP),
                  r30["elapsed_s_arm"]), flush=True)

        # GPU mem peak per N
        if GPU_AVAIL:
            peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
            out["gpu_max_mem_alloc_mb_n%d" % N] = round(peak_bytes / 1e6, 2)
            print("  [seed=%d N=%d] GPU peak alloc: %.2f MB" % (
                seed, N, out["gpu_max_mem_alloc_mb_n%d" % N]), flush=True)
            del W, E, R
            torch.cuda.empty_cache()

    # META_RULE_AF: ARMS-MUST-DIFFER
    digests = _arms_must_differ(arm_outputs_for_hash)
    out["_arm_output_digests"] = digests
    out["arms_differ_verified"] = True

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]):
    def per_step_mean_across_seeds(arm_key: str) -> float:
        vals = [p[arm_key]["per_step_mean"] for p in per_seed if arm_key in p
                and isinstance(p[arm_key].get("per_step_mean"), (int, float))
                and not math.isnan(p[arm_key]["per_step_mean"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_across_seeds(arm_key: str) -> float:
        vals = [p[arm_key]["per_step_mean"] for p in per_seed if arm_key in p
                and isinstance(p[arm_key].get("per_step_mean"), (int, float))
                and not math.isnan(p[arm_key]["per_step_mean"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    def top1_min(arm_key: str) -> float:
        vals = [p[arm_key]["top1"] for p in per_seed if arm_key in p
                and isinstance(p[arm_key].get("top1"), (int, float))
                and not math.isnan(p[arm_key]["top1"])]
        return float(np.min(vals)) if vals else float("nan")

    # META_RULE_H: CARDINALITY_OK
    observed_n_units = len(per_seed)
    if observed_n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "CARDINALITY_BREACH: expected %d seeds, observed %d" % (
                    EXPECTED_N_UNITS, observed_n_units))

    arm_15_n4096 = "arm_part_oracle_15hop_n4096"
    arm_30_n4096 = "arm_part_oracle_30hop_n4096"
    arm_15_n16384 = "arm_part_oracle_15hop_n16384"
    arm_30_n16384 = "arm_part_oracle_30hop_n16384"

    m15_4 = per_step_mean_across_seeds(arm_15_n4096)
    m30_4 = per_step_mean_across_seeds(arm_30_n4096)
    m15_16 = per_step_mean_across_seeds(arm_15_n16384)
    m30_16 = per_step_mean_across_seeds(arm_30_n16384)

    cv15_4 = cv_across_seeds(arm_15_n4096)
    cv30_4 = cv_across_seeds(arm_30_n4096)
    cv15_16 = cv_across_seeds(arm_15_n16384)
    cv30_16 = cv_across_seeds(arm_30_n16384)

    top1_min_all = min(
        top1_min(arm_15_n4096), top1_min(arm_30_n4096),
        top1_min(arm_15_n16384), top1_min(arm_30_n16384))

    summ = (
        "N=4096 d=15 per_step=%.4f (cv=%.3f, |diff|=%.4f) "
        "N=4096 d=30 per_step=%.4f (cv=%.3f, |diff|=%.4f) "
        "N=16384 d=15 per_step=%.4f (cv=%.3f, |diff|=%.4f) "
        "N=16384 d=30 per_step=%.4f (cv=%.3f, |diff|=%.4f) "
        "top1_min=%.4f REF_15=%.4f REF_30=%.4f HP_TOL=%.2f HF_TOL=%.2f"
    ) % (
        m15_4, cv15_4, abs(m15_4 - REF_15HOP) if not math.isnan(m15_4) else float('nan'),
        m30_4, cv30_4, abs(m30_4 - REF_30HOP) if not math.isnan(m30_4) else float('nan'),
        m15_16, cv15_16, abs(m15_16 - REF_15HOP) if not math.isnan(m15_16) else float('nan'),
        m30_16, cv30_16, abs(m30_16 - REF_30HOP) if not math.isnan(m30_16) else float('nan'),
        top1_min_all, REF_15HOP, REF_30HOP, HP_TOL, HF_TOL,
    )

    # HF_MECHANISM_DEATH pre-emption
    if not math.isnan(top1_min_all) and top1_min_all < DEATH_FLOOR:
        return ("MECHANISM_DEATH",
                "MECHANISM_DEATH_TOP1_BELOW_%.2f: %s" % (DEATH_FLOOR, summ))

    def is_hp(m: float, ref: float, cv: float) -> bool:
        if math.isnan(m):
            return False
        cv_ok = math.isnan(cv) or cv <= CV_CAP
        return (abs(m - ref) <= HP_TOL) and cv_ok

    def is_hf_variance(m: float, ref: float) -> bool:
        return (not math.isnan(m)) and (abs(m - ref) > HF_TOL)

    hp_15_4 = is_hp(m15_4, REF_15HOP, cv15_4)
    hp_30_4 = is_hp(m30_4, REF_30HOP, cv30_4)
    hp_15_16 = is_hp(m15_16, REF_15HOP, cv15_16)
    hp_30_16 = is_hp(m30_16, REF_30HOP, cv30_16)

    hf_15_4 = is_hf_variance(m15_4, REF_15HOP)
    hf_30_4 = is_hf_variance(m30_4, REF_30HOP)
    hf_15_16 = is_hf_variance(m15_16, REF_15HOP)
    hf_30_16 = is_hf_variance(m30_16, REF_30HOP)

    any_hf = hf_15_4 or hf_30_4 or hf_15_16 or hf_30_16

    if hp_15_4 and hp_30_4 and hp_15_16 and hp_30_16:
        return ("CHAIN_GRADE_SCALE_INVARIANT_N_AXIS",
                "CHAIN_GRADE_SCALE_INVARIANT_N_AXIS_ALL_4_ARMS_HP: " + summ)
    if hp_15_4 and hp_15_16 and (not hp_30_4 or not hp_30_16):
        return ("PARTIAL_SCALE_INVARIANT_D15_ONLY",
                "PARTIAL_SCALE_INVARIANT_D15_ONLY_D30_BREAKS: " + summ)
    if hp_30_4 and hp_30_16 and (not hp_15_4 or not hp_15_16):
        return ("PARTIAL_SCALE_INVARIANT_D30_ONLY",
                "PARTIAL_SCALE_INVARIANT_D30_ONLY_D15_BREAKS: " + summ)
    if any_hf:
        return ("SCALE_VARIANT_N_AXIS",
                "SCALE_VARIANT_N_AXIS_HF_SCALE_VARIANCE_FIRED: " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_MIXED_ARMS: " + summ)


# ----------------------------------------------------------------------------
# Crash diagnostic helper (META_RULE §13.C)
# ----------------------------------------------------------------------------

def _write_crash_metrics(output_dir: Path, anchor_name: str, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": ("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        "summary": ("CELL_CRASHED: %s" % type(exc).__name__),
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


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


# ----------------------------------------------------------------------------
# atexit synthesizer + main
# ----------------------------------------------------------------------------

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def main() -> None:
    print("[config] anchor=%s mode=%s seeds=%s Ns=%s depths=%s gpu=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_VALUES, DEPTHS, GPU_AVAIL, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    # META_RULE §13.B: start-marker
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {"run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    # META_RULE §13.D: heartbeat context manager
    with CellHeartbeat(out_dir, total_units=len(SEEDS), interval_s=30) as hb:
        for idx, s in enumerate(remaining):
            rec = run_seed(s)
            write_partial_key(out_dir, s, rec)
            hb.tick(idx, extra={"seed": s,
                                 "elapsed_s_seed": rec.get("elapsed_s")})

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": len(per_seed) == EXPECTED_N_UNITS,
        "DESIGN_NOTE": (
            "N_AXIS_SCALE_INVARIANCE: sweeps N in {4096, 16384} at fixed "
            "PART_SIZE=10, V_C=200, K=20, n_partitions=20, n_chains=200, "
            "max_depth=30 (shared W; d=15 arm uses chains[:15] slice). Tests "
            "whether partition-oracle per-step accuracy at d=15 (REF=0.858) and "
            "d=30 (REF=0.682) at N=8192 REPRODUCES at N=4096 and N=16384. "
            "CHAIN_GRADE_SCALE_INVARIANT_N_AXIS -> Atom 11 MM_STANDARD lifts to "
            "CG. GPU-preferred at full; smoke fits on CPU."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        od = _RESULTS_HOLDER.get("out_dir")
        if od is not None:
            _write_crash_metrics(od, ANCHOR_NAME, e)
        raise
