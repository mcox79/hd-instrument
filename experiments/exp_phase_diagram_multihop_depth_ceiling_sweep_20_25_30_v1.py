"""phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.

USER directive 2026-06-26: phase-diagram extension of multi-hop chain-grade beyond
depth 15. Prior cell `phase_diagram_multihop_depth_extension_via_partition_oracle_v1`
chain-graded depth=15 at PART_15HOP=0.8083 cv=0.024 (per-step ~0.95-0.99). USER
requests depths {20, 25, 30} to map the depth ceiling.

PROMOTION CONTEXT: brain handles 10+ steps for reasoning. Substrate's per-step
accuracy at depth=15 is 0.95-0.99 -> at depth=30, 0.97^30 = 0.40, 0.95^30 = 0.21.
Is partition-oracle routing enough to push the depth ceiling further, or does it
cliff between 15 and 30?

DESIGN: partition-oracle routed multi-hop at depths {20, 25, 30} on three Ws
(one per max-depth regime). Sanity rail: ARM_DEPTH_15 reproduces 0.808+/-0.05 from
prior cell, using the same W_pointer_v2-style construction (max_depth=15).

ARMS (4):
  ARM_PART_ORACLE_15HOP      sanity rail; must reproduce 0.808 within +/-0.05
  ARM_PART_ORACLE_20HOP      novel phase point on W_max_depth=20 (4000 bindings)
  ARM_PART_ORACLE_25HOP      novel phase point on W_max_depth=25 (5000 bindings)
  ARM_PART_ORACLE_30HOP      novel phase point on W_max_depth=30 (6000 bindings)

PRE-REG BANDS (LOCKED at module init; derived from 0.97-per-step compounding):
  Sanity rail (verdict pre-emption on majority-seed breach):
    RAIL_DEPTH_15            PART_15HOP NOT in [0.758, 0.858] -> SANITY_BREACH
                             (0.808 +/- 0.05; allows seed variance)
  Phase points (per-arm; PASS/FAIL):
    20HOP: HARD_PASS if mean >= 0.55   HARD_FAIL if mean < 0.30
    25HOP: HARD_PASS if mean >= 0.40   HARD_FAIL if mean < 0.18
    30HOP: HARD_PASS if mean >= 0.30   HARD_FAIL if mean < 0.12
  Stability:
    cv across seeds <= 0.10 for HARD_PASS claim

VERDICTS (LOCKED at module init):
  CHAIN_GRADE_DEPTH_CEILING_30:    rail PASS + all 3 (20/25/30) HARD_PASS
                                    -> deep reasoning scales to 30 hops
  PARTIAL_DEPTH_CEILING_25:        rail + 20+25 HARD_PASS, 30 below
                                    -> cliff between 25 and 30
  PARTIAL_DEPTH_CEILING_20:        rail + 20 HARD_PASS, 25 below
                                    -> cliff between 20 and 25
  DEPTH_15_IS_CEILING:             rail only; 20+25+30 all fail
                                    -> prior chain-grade was the limit
  SANITY_BREACH:                    rail breach majority of seeds -> setup broken
  MIDDLE_BAND:                      mixed phase points (above HF, below HP)

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_d15, W_d20, W_d25, W_d30) built on torch.cuda via batched
    outer-product accumulation; E, R kept on GPU throughout.
  - Argmax cleanup is torch.argmax(E @ (W @ key)) on GPU.
  - Per-W memory at N=8192: 1 W = 268MB; 4 Ws = ~1.1GB resident; fits 8GB GPU
    with cleared cache between seeds.

ASCII-only; per-seed checkpoint; atexit synthesizer; zero-LLM-call assert.
Author: exp_dev 2026-06-26 (USER-directed phase-diagram extension).
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
import math
import os
import time
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
          "Smoke OK; full dispatch MUST be GPU per Fix #24.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1"
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
# Sanity rail: depth-15 reproduce (0.808 +/- 0.05)
RAIL_15_TARGET = 0.808
RAIL_15_LO = 0.758
RAIL_15_HI = 0.858

# Phase points (per-depth; predicted by 0.97-per-step on partition-oracle)
HP_20HOP = 0.55
HF_20HOP = 0.30
HP_25HOP = 0.40
HF_25HOP = 0.18
HP_30HOP = 0.30
HF_30HOP = 0.12
PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HARD_PASS claim

# Locked invariants
assert RAIL_15_LO < RAIL_15_TARGET < RAIL_15_HI
assert HP_20HOP > HF_20HOP and HP_25HOP > HF_25HOP and HP_30HOP > HF_30HOP
assert HP_25HOP < HP_20HOP and HP_30HOP < HP_25HOP, "HP should monotone decrease"
# Compounding-prediction sanity: bands within 0.97-per-step bound (allow up to 0.99)
assert HP_20HOP <= 0.99 ** 20 + 0.01
assert HP_25HOP <= 0.99 ** 25 + 0.01
assert HP_30HOP <= 0.99 ** 30 + 0.01

# Cell config (per directive; inherits depth-extension v1 envelope)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20

# Phase point depths
DEPTHS = [15, 20, 25, 30]
MAX_DEPTH = 30

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the FOUR Ws (depth-extension naming: W_max_depth_<D>)
D15_REGIME_MAX_DEPTH = 15  # W_d15: 200*15 = 3000 bindings (rail reproduce)
D20_REGIME_MAX_DEPTH = 20  # W_d20: 200*20 = 4000 bindings
D25_REGIME_MAX_DEPTH = 25  # W_d25: 200*25 = 5000 bindings
D30_REGIME_MAX_DEPTH = 30  # W_d30: 200*30 = 6000 bindings

if RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [11]
    N_CHAINS_LOCAL = 25       # 25 chains for smoke (lighter than full)
else:
    N_DIM = 8192
    SEEDS = [11, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagramMultihopDepthCeilingV1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_d15=%d W_d20=%d W_d25=%d W_d30=%d "
    "seeds=%s mode=%s encoder=%s "
    "rail_15=[%.3f,%.3f] target=%.4f "
    "HP_20=%.2f HF_20=%.2f HP_25=%.2f HF_25=%.2f HP_30=%.2f HF_30=%.2f "
    "phase_cv_max=%.2f"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    D15_REGIME_MAX_DEPTH, D20_REGIME_MAX_DEPTH,
    D25_REGIME_MAX_DEPTH, D30_REGIME_MAX_DEPTH,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    RAIL_15_LO, RAIL_15_HI, RAIL_15_TARGET,
    HP_20HOP, HF_20HOP, HP_25HOP, HF_25HOP, HP_30HOP, HF_30HOP,
    PHASE_CV_MAX,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from depth-extension v1)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    """Bipolar bit vectors on GPU; row-normalized."""
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator,
                      disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                  List[List[Tuple[int, int, int]]]]:
    """VERBATIM port of depth-extension v1's make_deep_chains."""
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


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                        E: torch.Tensor, R: torch.Tensor,
                        sq: float, n_dim: int,
                        batch: int = 1000) -> torch.Tensor:
    """Batched outer-product Hebbian ingest on GPU. VERBATIM port."""
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
        K = E[s_slice] * R[p_slice] * sq  # (B, N)
        V_ = E[o_slice]                    # (B, N)
        W = W + (V_.T @ K) / n_dim
    return W


def arm_part_oracle_at_depth(E: torch.Tensor, R: torch.Tensor, sq: float,
                               W: torch.Tensor,
                               chains_test: List[List[Tuple[int, int, int]]],
                               depth: int,
                               part_size: int) -> Dict[str, Any]:
    """Partition-oracle routed cleanup at given depth. VERBATIM port from v1."""
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
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "part_size": part_size,
            "mechanism": "partition_oracle_per_hop_gpu"}


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

    # T2: chain construction at all four depths
    triples15, chains15 = make_deep_chains(8, V, P, max_depth=15, g=g,
                                              disallow_s=set())
    assert len(chains15) == 8 and len(triples15) == 8 * 15

    triples20, chains20 = make_deep_chains(8, V, P, max_depth=20, g=g,
                                              disallow_s=set())
    assert len(chains20) == 8 and len(triples20) == 8 * 20

    triples25, chains25 = make_deep_chains(8, V, P, max_depth=25, g=g,
                                              disallow_s=set())
    assert len(chains25) == 8 and len(triples25) == 8 * 25

    triples30, chains30 = make_deep_chains(8, V, P, max_depth=30, g=g,
                                              disallow_s=set())
    assert len(chains30) == 8 and len(triples30) == 8 * 30

    # T3: ingest tiny config
    W15 = ingest_hebbian_gpu(triples15, E, R, sq, n)
    W30 = ingest_hebbian_gpu(triples30, E, R, sq, n)
    assert W15.shape == (n, n) and W30.shape == (n, n)
    assert torch.isfinite(W15).all() and torch.isfinite(W30).all()

    # T4: part_oracle at each depth on tiny config
    n_parts_test = 4
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    r15 = arm_part_oracle_at_depth(E, R, sq, W15, chains15, depth=15,
                                      part_size=part_sz_test)
    assert 0.0 <= r15["top1"] <= 1.0
    assert len(r15["per_step_acc"]) == 15

    r20 = arm_part_oracle_at_depth(E, R, sq, W30, [c[:20] for c in chains30],
                                      depth=20, part_size=part_sz_test)
    assert 0.0 <= r20["top1"] <= 1.0
    assert len(r20["per_step_acc"]) == 20

    r25 = arm_part_oracle_at_depth(E, R, sq, W30, [c[:25] for c in chains30],
                                      depth=25, part_size=part_sz_test)
    assert 0.0 <= r25["top1"] <= 1.0
    assert len(r25["per_step_acc"]) == 25

    r30 = arm_part_oracle_at_depth(E, R, sq, W30, chains30, depth=30,
                                      part_size=part_sz_test)
    assert 0.0 <= r30["top1"] <= 1.0
    assert len(r30["per_step_acc"]) == 30

    # T5: bands LOCKED (regression on accidental band drift)
    assert HP_20HOP == 0.55 and HF_20HOP == 0.30
    assert HP_25HOP == 0.40 and HF_25HOP == 0.18
    assert HP_30HOP == 0.30 and HF_30HOP == 0.12
    assert RAIL_15_LO == 0.758 and RAIL_15_HI == 0.858
    assert RAIL_15_TARGET == 0.808

    # T6: PHASE_CV_MAX in (0, 0.20]
    assert 0.0 < PHASE_CV_MAX <= 0.20

    # T7: LLM call counter = 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: GPU presence asserted for non-smoke mode (smoke OK on CPU)
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    print("[selftest] PASS part15=%.3f part20=%.3f part25=%.3f part30=%.3f gpu=%s"
          % (r15["top1"], r20["top1"], r25["top1"], r30["top1"], GPU_AVAIL),
          flush=True)


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
    sq = math.sqrt(N_DIM)

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    print("  [seed=%d] building E (V_C=%d, N=%d)" % (
        seed, V_CONCEPTS, N_DIM), flush=True)
    E = bipolar_gpu(V_CONCEPTS, N_DIM, g)
    R = bipolar_gpu(V_PRED, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "K_set": K_SET, "n_partitions": N_PARTITIONS,
        "part_size": PART_SIZE,
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Build all four Ws.  We use ONE W per max-depth regime (each W ingested
    # from chains at that exact max_depth, ensuring chains exist for the test).
    Ws = {}
    for label, depth_max in [("d15", D15_REGIME_MAX_DEPTH),
                              ("d20", D20_REGIME_MAX_DEPTH),
                              ("d25", D25_REGIME_MAX_DEPTH),
                              ("d30", D30_REGIME_MAX_DEPTH)]:
        t_arm = time.time()
        triples, chains = make_deep_chains(
            N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=depth_max,
            g=g, disallow_s=set())
        W = ingest_hebbian_gpu(triples, E, R, sq, N_DIM)
        Ws[label] = (W, triples, chains, depth_max)
        print("  [seed=%d] W_%s built (%d triples, max_depth=%d) t=%.1fs" % (
            seed, label, len(triples), depth_max,
            round(time.time() - t_arm, 2)), flush=True)

    # ===== ARM_PART_ORACLE_15HOP (sanity rail; reproduces prior 0.808) =====
    t_arm = time.time()
    W_d15, _, chains_d15, _ = Ws["d15"]
    r_part15 = arm_part_oracle_at_depth(E, R, sq, W_d15, chains_d15, depth=15,
                                          part_size=PART_SIZE)
    r_part15["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part15["W_n_bindings"] = len(Ws["d15"][1])
    r_part15["W_regime"] = "d15_max_depth_15"
    out["arm_part_oracle_15hop"] = r_part15
    rail_ok = (RAIL_15_LO <= r_part15["top1"] <= RAIL_15_HI)
    out["rail_15_ok"] = rail_ok
    print("  [seed=%d] PART_ORACLE_15HOP top1=%.4f per_step=%s "
          "(rail_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part15["top1"], r_part15["per_step_acc"],
              rail_ok, RAIL_15_LO, RAIL_15_HI, RAIL_15_TARGET,
              r_part15["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_20HOP =====
    t_arm = time.time()
    W_d20, _, chains_d20, _ = Ws["d20"]
    r_part20 = arm_part_oracle_at_depth(E, R, sq, W_d20, chains_d20, depth=20,
                                          part_size=PART_SIZE)
    r_part20["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part20["W_n_bindings"] = len(Ws["d20"][1])
    r_part20["W_regime"] = "d20_max_depth_20"
    out["arm_part_oracle_20hop"] = r_part20
    print("  [seed=%d] PART_ORACLE_20HOP top1=%.4f per_step=%s "
          "(HP=%.2f HF=%.2f) t=%.1fs" % (
              seed, r_part20["top1"], r_part20["per_step_acc"],
              HP_20HOP, HF_20HOP, r_part20["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_25HOP =====
    t_arm = time.time()
    W_d25, _, chains_d25, _ = Ws["d25"]
    r_part25 = arm_part_oracle_at_depth(E, R, sq, W_d25, chains_d25, depth=25,
                                          part_size=PART_SIZE)
    r_part25["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part25["W_n_bindings"] = len(Ws["d25"][1])
    r_part25["W_regime"] = "d25_max_depth_25"
    out["arm_part_oracle_25hop"] = r_part25
    print("  [seed=%d] PART_ORACLE_25HOP top1=%.4f per_step=%s "
          "(HP=%.2f HF=%.2f) t=%.1fs" % (
              seed, r_part25["top1"], r_part25["per_step_acc"],
              HP_25HOP, HF_25HOP, r_part25["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_30HOP =====
    t_arm = time.time()
    W_d30, _, chains_d30, _ = Ws["d30"]
    r_part30 = arm_part_oracle_at_depth(E, R, sq, W_d30, chains_d30, depth=30,
                                          part_size=PART_SIZE)
    r_part30["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part30["W_n_bindings"] = len(Ws["d30"][1])
    r_part30["W_regime"] = "d30_max_depth_30"
    out["arm_part_oracle_30hop"] = r_part30
    print("  [seed=%d] PART_ORACLE_30HOP top1=%.4f per_step=%s "
          "(HP=%.2f HF=%.2f) t=%.1fs" % (
              seed, r_part30["top1"], r_part30["per_step_acc"],
              HP_30HOP, HF_30HOP, r_part30["elapsed_s_arm"]), flush=True)

    # GPU mem peak
    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        print("  [seed=%d] GPU peak alloc: %.2f MB" % (
            seed, out["gpu_max_mem_alloc_mb"]), flush=True)
        for label in list(Ws.keys()):
            del Ws[label]
        torch.cuda.empty_cache()
    else:
        out["gpu_max_mem_alloc_mb"] = 0.0

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    part15 = mean_top1("arm_part_oracle_15hop")
    part20 = mean_top1("arm_part_oracle_20hop")
    part25 = mean_top1("arm_part_oracle_25hop")
    part30 = mean_top1("arm_part_oracle_30hop")

    cv15 = cv_top1("arm_part_oracle_15hop")
    cv20 = cv_top1("arm_part_oracle_20hop")
    cv25 = cv_top1("arm_part_oracle_25hop")
    cv30 = cv_top1("arm_part_oracle_30hop")

    rail_breached = sum(1 for p in per_seed if not p.get("rail_15_ok", False))

    summ = (
        "PART_15HOP=%.4f (cv=%.3f, rail_breach=%d/%d; target=%.4f) "
        "PART_20HOP=%.4f (cv=%.3f) "
        "PART_25HOP=%.4f (cv=%.3f) "
        "PART_30HOP=%.4f (cv=%.3f)"
    ) % (
        part15, cv15, rail_breached, len(per_seed), RAIL_15_TARGET,
        part20, cv20, part25, cv25, part30, cv30,
    )

    half = max(1, (len(per_seed) + 1) // 2)

    # Sanity pre-emption: rail breach majority (skip in smoke; smoke at smaller
    # N over-performs by design and cannot reproduce the FULL N=8192 rail at
    # 0.808; smoke verdict is mechanism end-to-end check only)
    if RUN_MODE != "smoke" and rail_breached >= half:
        return "SANITY_BREACH", "SANITY_BREACH_RAIL_15HOP_OUT_OF_BAND: " + summ

    # Smoke mode: PASS verdict if mechanism end-to-end works at all depths
    if RUN_MODE == "smoke":
        any_mech_ok = all(not math.isnan(v) and v >= 0.10
                            for v in [part15, part20, part25, part30])
        if any_mech_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(rail band [%.3f,%.3f] not applicable to smaller N) | %s" % (
                        RAIL_15_LO, RAIL_15_HI, summ))
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | " + summ)

    # Phase-point classification
    def hp_at_depth(mean_val: float, cv_val: float, hp: float) -> bool:
        if math.isnan(mean_val):
            return False
        cv_ok = math.isnan(cv_val) or cv_val <= PHASE_CV_MAX
        return (mean_val >= hp) and cv_ok

    def hf_at_depth(mean_val: float, hf: float) -> bool:
        return (not math.isnan(mean_val)) and (mean_val < hf)

    rail_pass = (not math.isnan(part15)) and (RAIL_15_LO <= part15 <= RAIL_15_HI)
    pass20 = hp_at_depth(part20, cv20, HP_20HOP)
    pass25 = hp_at_depth(part25, cv25, HP_25HOP)
    pass30 = hp_at_depth(part30, cv30, HP_30HOP)

    fail20 = hf_at_depth(part20, HF_20HOP)
    fail25 = hf_at_depth(part25, HF_25HOP)
    fail30 = hf_at_depth(part30, HF_30HOP)

    if rail_pass and pass20 and pass25 and pass30:
        return ("CHAIN_GRADE_DEPTH_CEILING_30",
                "CHAIN_GRADE_DEPTH_CEILING_30_ALL_PHASE_POINTS_HARD_PASS: " + summ)
    if rail_pass and pass20 and pass25 and fail30:
        return ("PARTIAL_DEPTH_CEILING_25",
                "PARTIAL_DEPTH_CEILING_25_CLIFF_BETWEEN_25_AND_30: " + summ)
    if rail_pass and pass20 and not pass25 and not pass30:
        return ("PARTIAL_DEPTH_CEILING_20",
                "PARTIAL_DEPTH_CEILING_20_CLIFF_BETWEEN_20_AND_25: " + summ)
    if rail_pass and (fail20 or not pass20) and (fail25 or not pass25) \
            and (fail30 or not pass30):
        return ("DEPTH_15_IS_CEILING",
                "DEPTH_15_IS_CEILING_PRIOR_CHAIN_GRADE_WAS_THE_LIMIT: " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_MIXED_PHASE_POINTS: " + summ)


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
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
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
            "gpu_avail": GPU_AVAIL,
            "gpu_name": GPU_NAME,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d gpu=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, GPU_AVAIL, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

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
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "DESIGN_NOTE": (
            "PHASE_DIAGRAM_DEPTH_CEILING_SWEEP: prior cell depth-extension-v1 "
            "chain-graded depths 5/7/10/15 via partition-oracle routed cleanup "
            "(PART_15HOP=0.8083 cv=0.024). USER 2026-06-26 directive: extend to "
            "depths 20/25/30 to find the depth ceiling. Sanity rail reproduces "
            "depth-15 within +/-0.05. Bands derived from 0.97-per-step compounding. "
            "Verdict tiers the depth ceiling: CHAIN_GRADE_DEPTH_CEILING_30 / "
            "PARTIAL_DEPTH_CEILING_25 / PARTIAL_DEPTH_CEILING_20 / "
            "DEPTH_15_IS_CEILING. GPU-required at full per Fix #24."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
