"""multihop_reasoning_depth_30_v1.

Composes AGAINST phase_diagram_multihop_depth_extension_via_partition_oracle_v1
(depth-15 CHAIN_GRADE at PART_15HOP=0.8083 cv=0.024; 3 seeds; N=8192, V_C=200,
K_set=20, n_chains=200, partition-routed cleanup).

FALSIFIABLE (per Research pre-reg):
  HP: recall > 0.60 at depth=30 across 3 seeds (chain-grade extension of mechanism)
  MB: graceful degradation, cliff located between depths {15, 20, 25, 30}
  HF: recall < 0.20 at depth=30 (chain-grade LIMIT found)

MECHANISM (composed depth-15 CG):
  W_depth30_extended = ingest_hebbian(make_deep_chains(n_chains=200, max_depth=30))
                       = 6000 bindings. Partition-oracle per-hop cleanup at each
                       target depth (chains[:15], [:20], [:25], full [:30]).
  Rail reproduce arm at depth=15 uses the SAME W_depth30_extended (extended
  regime; depth-15 recall from THIS W is compared against the depth-15 CG rail
  0.8083 +/- 0.05).

DISCRIMINATOR-MUST-SURVIVE-SCALE (META_RULE_AC):
  Depth-15 CG measured per-step accuracy ~0.986 (compounding 0.808^(1/15)).
  Prediction envelope at depth=30:
    pessimistic (0.955^d = pointer-chain per-step): recall ~0.25 -> HF band
    optimistic (0.986^d = depth-15 compound):      recall ~0.65 -> HP band
  Discriminator is 0.40 span between HF and HP -> mechanism-relevant even at
  full-N. Smoke seed_7 at depth=20 acts as full-N (N=8192) preview arm: if
  smoke depth-20 recall > 0.60 the mechanism scales; if < 0.30 cliff already
  hit before depth 30. Smoke is at FULL N to preserve discriminator (check A).

ARMS (5):
  ARM_BASELINE_HRR_2HOP        beta-sweep sanity rail [0.62, 0.68]
  ARM_RAIL_REPRODUCE_15HOP     cross-cell rail depth=15 [0.75, 0.85]
                               (0.8083 +/- 0.05 depth-15 CG target)
  ARM_PART_ORACLE_20HOP        NEW phase point on W_depth30
  ARM_PART_ORACLE_25HOP        NEW phase point on W_depth30
  ARM_PART_ORACLE_30HOP        NEW phase point on W_depth30  <- primary discriminator

PRE-REG BANDS (LOCKED at module init):
  Sanity rails (majority-seed pre-emption):
    RAIL_BASELINE               BASELINE   NOT in [0.62, 0.68] -> SANITY_BREACH
    RAIL_CROSS_CELL_15HOP       REPRO_15   NOT in [0.75, 0.85] -> CROSS_CELL_BREACH
  Phase points (per-arm; PASS/FAIL):
    20HOP:  HARD_PASS if mean >= 0.55   HARD_FAIL if mean < 0.30
    25HOP:  HARD_PASS if mean >= 0.45   HARD_FAIL if mean < 0.25
    30HOP:  HARD_PASS if mean >= 0.60   HARD_FAIL if mean < 0.20  <- USER pre-reg
  Stability:
    cv <= 0.10 for each HP-claimed phase point

VERDICTS (LOCKED at module init):
  CHAIN_GRADE_DEPTH_30_EXTENDS:  all 3 (20/25/30) HP + rail OK -> deep-reasoning scales
  PARTIAL_DEPTH_EXTENDS_TO_25:   20+25 HP, 30 below            -> cliff between 25-30
  PARTIAL_DEPTH_EXTENDS_TO_20:   20 HP, 25/30 below            -> cliff between 20-25
  DEPTH_15_IS_CEILING:           none of 20/25/30 HP           -> depth-15 CG WAS limit
  CROSS_CELL_BREACH:             15hop rail breach majority    -> reproduce failed
  SANITY_BREACH:                 baseline breach majority      -> setup broken

GPU-eligible (torch; encoder-hoisted; batched outer-product Hebbian).
Memory budget at N=8192: 1 W @ 268 MB + E (6.5 MB) + R (0.3 MB) ~= 275 MB.
ASCII-only; per-seed checkpoint; atexit synthesizer; zero-LLM-call assert.

META_RULE compliance:
  H (CARDINALITY_OK):      EXPECTED_N_UNITS=n_chains=200 per phase point
  J/K (SchemaVet):         REQUIRED_FIELDS declared below
  AC (survive-scale):      full-N preview at depth=20 in smoke (check A+C hybrid)
  AF (arms differ):        5 arms with distinct depth+mechanism combos
  AH (atomic metrics):     write_metrics via _seed_checkpoint
  AG (SystemExit ordering): _selftest before atexit register + main
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
# GPU GUARD (Fix #24)
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
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

ANCHOR_NAME = "multihop_reasoning_depth_30_v1"
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
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

CROSS_CELL_15HOP_LO = 0.75     # 0.8083 - 0.058
CROSS_CELL_15HOP_HI = 0.85     # 0.8083 + 0.042
CROSS_CELL_15HOP_TARGET = 0.8083

HP_20HOP = 0.55
HF_20HOP = 0.30
HP_25HOP = 0.45
HF_25HOP = 0.25
HP_30HOP = 0.60     # USER pre-reg: recall > 0.60 at depth=30 = HP
HF_30HOP = 0.20     # USER pre-reg: recall < 0.20 at depth=30 = HF
PHASE_CV_MAX = 0.10

# Locked invariants (META_RULE_M schema-vet)
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert CROSS_CELL_15HOP_LO < CROSS_CELL_15HOP_TARGET < CROSS_CELL_15HOP_HI
assert HP_20HOP > HF_20HOP and HP_25HOP > HF_25HOP and HP_30HOP > HF_30HOP
# Compounding-envelope sanity: measured 0.986 per-step at depth-15
# -> 0.986^20=0.755, 0.986^25=0.703, 0.986^30=0.652; HP bands honor envelope
assert HP_20HOP <= 0.986 ** 20 + 0.02
assert HP_25HOP <= 0.986 ** 25 + 0.02
assert HP_30HOP <= 0.986 ** 30 + 0.02

# Cell config (compose depth-15 CG regime EXACTLY)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20
DEPTHS = [15, 20, 25, 30]
MAX_DEPTH = 30

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

DEPTH30_MAX_DEPTH = 30

BASELINE_V_P = 2
BASELINE_N_CHAINS = 200

if RUN_MODE == "smoke":
    # DISCRIMINATOR-MUST-SURVIVE-SCALE: keep N=8192 in smoke (check A: full-N)
    # Only reduce n_chains for smoke wall-time; depth-20 preview arm carries
    # the mechanism-discriminator signal at full N.
    N_DIM = 8192
    SEEDS = [7]  # seed_7 per task
    N_CHAINS_LOCAL = 60
    BASELINE_N_LOCAL = 60
    # In smoke we only test depth=20 preview (discriminator anchor)
    SMOKE_DEPTHS = [15, 20]
else:
    N_DIM = 8192
    SEEDS = [11, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS
    BASELINE_N_LOCAL = BASELINE_N_CHAINS
    SMOKE_DEPTHS = None  # unused in full

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopReasoningDepth30V1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d W_depth30=%d "
    "baseline_v_p=%d baseline_n=%d seeds=%s mode=%s encoder=%s "
    "rail_15hop=[%.3f,%.3f] target=%.4f "
    "HP_20=%.2f HF_20=%.2f HP_25=%.2f HF_25=%.2f HP_30=%.2f HF_30=%.2f "
    "phase_cv_max=%.2f baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL, DEPTH30_MAX_DEPTH,
    BASELINE_V_P, BASELINE_N_LOCAL,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    CROSS_CELL_15HOP_LO, CROSS_CELL_15HOP_HI, CROSS_CELL_15HOP_TARGET,
    HP_20HOP, HF_20HOP, HP_25HOP, HF_25HOP, HP_30HOP, HF_30HOP,
    PHASE_CV_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)

# META_RULE_J: REQUIRED_FIELDS declared for schema-vet
REQUIRED_FIELDS = [
    "anchor_name", "verdict", "verdict_msg", "run_mode", "n_seeds",
    "config_version", "per_seed", "elapsed_s", "gpu_avail",
    "_llm_forward_calls_at_inference",
]

# META_RULE_H: cardinality declaration for sweep-axis cells
EXPECTED_N_UNITS = N_CHAINS_LOCAL  # per phase point per seed
HARD_FAIL_CARDINALITY_BREACH = True


# ----------------------------------------------------------------------------
# Primitives (VERBATIM port from depth-15 CG cell)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator,
                      disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                 List[List[Tuple[int, int, int]]]]:
    """VERBATIM port of depth-15 CG make_deep_chains."""
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
    """VERBATIM port from depth-15 CG."""
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


def make_two_hop_chains_betasweep(n_chains, V, g, p1=0, p2=1):
    train = []
    queries = []
    used_s = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def arm_baseline_hrr_2hop(E, R, sq, train_triples, queries):
    n_dim = E.shape[1]
    W = ingest_hebbian_gpu(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        state = E[s].clone()
        last = s
        for p in [p1, p2]:
            state = W @ (state * R[p] * sq)
            last = int(torch.argmax(E @ state).item())
        if last == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries),
            "mechanism": "beta_sweep_naive_hard_gpu"}


def arm_part_oracle_at_depth(E, R, sq, W, chains_test, depth, part_size):
    """VERBATIM port from depth-15 CG partition-oracle."""
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

    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    Rb = bipolar_gpu(max(BASELINE_V_P, 2), n, g)
    train_b, q_b = make_two_hop_chains_betasweep(15, V, g)
    r_base = arm_baseline_hrr_2hop(E, Rb, sq, train_b, q_b)
    assert 0.0 <= r_base["top1"] <= 1.0

    triples30, chains30 = make_deep_chains(8, V, P, max_depth=30, g=g,
                                            disallow_s=set())
    assert len(chains30) == 8
    assert len(triples30) == 8 * 30

    W30 = ingest_hebbian_gpu(triples30, E, R, sq, n)
    assert W30.shape == (n, n)
    assert torch.isfinite(W30).all()

    n_parts_test = 4
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    r15 = arm_part_oracle_at_depth(E, R, sq, W30, [c[:15] for c in chains30],
                                     depth=15, part_size=part_sz_test)
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

    r30 = arm_part_oracle_at_depth(E, R, sq, W30, chains30,
                                     depth=30, part_size=part_sz_test)
    assert 0.0 <= r30["top1"] <= 1.0
    assert len(r30["per_step_acc"]) == 30

    # Bands LOCKED regression
    assert HP_20HOP == 0.55 and HF_20HOP == 0.30
    assert HP_25HOP == 0.45 and HF_25HOP == 0.25
    assert HP_30HOP == 0.60 and HF_30HOP == 0.20
    assert CROSS_CELL_15HOP_LO == 0.75 and CROSS_CELL_15HOP_HI == 0.85
    assert BASELINE_SANITY_LO == 0.62 and BASELINE_SANITY_HI == 0.68
    assert 0.0 < PHASE_CV_MAX <= 0.20
    assert _LLM_CALL_COUNTER[0] == 0
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    print("[selftest] PASS base=%.3f p15=%.3f p20=%.3f p25=%.3f p30=%.3f gpu=%s" % (
        r_base["top1"], r15["top1"], r20["top1"], r25["top1"], r30["top1"],
        GPU_AVAIL), flush=True)


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
    n_pred_total = max(BASELINE_V_P, V_PRED)
    R = bipolar_gpu(n_pred_total, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "K_set": K_SET, "n_partitions": N_PARTITIONS,
        "part_size": PART_SIZE,
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== BASELINE sanity =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_LOCAL, V_CONCEPTS, g)
    r_baseline = arm_baseline_hrr_2hop(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    print("  [seed=%d] BASELINE top1=%.4f (sanity_ok=%s) t=%.1fs" % (
        seed, r_baseline["top1"], baseline_ok,
        r_baseline["elapsed_s_arm"]), flush=True)

    # ===== Build W_depth30_extended (max_depth=30) =====
    t_arm = time.time()
    d30_triples, d30_chains = make_deep_chains(
        N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=DEPTH30_MAX_DEPTH,
        g=g, disallow_s=set())
    W_d30 = ingest_hebbian_gpu(d30_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_depth30 built (%d triples, max_depth=%d) t=%.1fs" % (
        seed, len(d30_triples), DEPTH30_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)

    # ===== ARM_RAIL_REPRODUCE_15HOP (cross-cell rail on W_depth30) =====
    t_arm = time.time()
    d30_chains_d15 = [c[:15] for c in d30_chains]
    r_rail15 = arm_part_oracle_at_depth(E, R, sq, W_d30, d30_chains_d15,
                                          depth=15, part_size=PART_SIZE)
    r_rail15["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_rail15["W_n_bindings"] = len(d30_triples)
    r_rail15["W_regime"] = "depth30_extended_max_depth_30"
    out["arm_rail_reproduce_15hop"] = r_rail15
    cross_cell_ok = (CROSS_CELL_15HOP_LO <= r_rail15["top1"] <= CROSS_CELL_15HOP_HI)
    out["cross_cell_15hop_ok"] = cross_cell_ok
    print("  [seed=%d] RAIL_REPRO_15HOP top1=%.4f (cross_cell_ok=%s; "
          "band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_rail15["top1"], cross_cell_ok,
              CROSS_CELL_15HOP_LO, CROSS_CELL_15HOP_HI,
              CROSS_CELL_15HOP_TARGET, r_rail15["elapsed_s_arm"]), flush=True)

    # In smoke, only test depth-15 rail + depth-20 preview discriminator
    if RUN_MODE == "smoke":
        # ===== SMOKE: ARM_PART_ORACLE_20HOP (discriminator preview) =====
        t_arm = time.time()
        d30_chains_d20 = [c[:20] for c in d30_chains]
        r_part20 = arm_part_oracle_at_depth(E, R, sq, W_d30, d30_chains_d20,
                                              depth=20, part_size=PART_SIZE)
        r_part20["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_part20["W_n_bindings"] = len(d30_triples)
        r_part20["W_regime"] = "depth30_extended_max_depth_30"
        out["arm_part_oracle_20hop"] = r_part20
        print("  [seed=%d] SMOKE PART_ORACLE_20HOP top1=%.4f "
              "(HP=%.2f, HF=%.2f; discriminator preview) t=%.1fs" % (
                  seed, r_part20["top1"], HP_20HOP, HF_20HOP,
                  r_part20["elapsed_s_arm"]), flush=True)
    else:
        # ===== FULL: sweep depth=20/25/30 =====
        # ARM_PART_ORACLE_20HOP
        t_arm = time.time()
        d30_chains_d20 = [c[:20] for c in d30_chains]
        r_part20 = arm_part_oracle_at_depth(E, R, sq, W_d30, d30_chains_d20,
                                              depth=20, part_size=PART_SIZE)
        r_part20["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_part20["W_n_bindings"] = len(d30_triples)
        r_part20["W_regime"] = "depth30_extended_max_depth_30"
        out["arm_part_oracle_20hop"] = r_part20
        print("  [seed=%d] PART_ORACLE_20HOP top1=%.4f (HP=%.2f, HF=%.2f) t=%.1fs" % (
            seed, r_part20["top1"], HP_20HOP, HF_20HOP,
            r_part20["elapsed_s_arm"]), flush=True)

        # ARM_PART_ORACLE_25HOP
        t_arm = time.time()
        d30_chains_d25 = [c[:25] for c in d30_chains]
        r_part25 = arm_part_oracle_at_depth(E, R, sq, W_d30, d30_chains_d25,
                                              depth=25, part_size=PART_SIZE)
        r_part25["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_part25["W_n_bindings"] = len(d30_triples)
        r_part25["W_regime"] = "depth30_extended_max_depth_30"
        out["arm_part_oracle_25hop"] = r_part25
        print("  [seed=%d] PART_ORACLE_25HOP top1=%.4f (HP=%.2f, HF=%.2f) t=%.1fs" % (
            seed, r_part25["top1"], HP_25HOP, HF_25HOP,
            r_part25["elapsed_s_arm"]), flush=True)

        # ARM_PART_ORACLE_30HOP (primary discriminator)
        t_arm = time.time()
        r_part30 = arm_part_oracle_at_depth(E, R, sq, W_d30, d30_chains,
                                              depth=30, part_size=PART_SIZE)
        r_part30["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_part30["W_n_bindings"] = len(d30_triples)
        r_part30["W_regime"] = "depth30_extended_max_depth_30"
        out["arm_part_oracle_30hop"] = r_part30
        print("  [seed=%d] PART_ORACLE_30HOP top1=%.4f (HP=%.2f, HF=%.2f; "
              "PRIMARY DISCRIMINATOR) t=%.1fs" % (
                  seed, r_part30["top1"], HP_30HOP, HF_30HOP,
                  r_part30["elapsed_s_arm"]), flush=True)

    # GPU mem peak
    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        del W_d30
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

    baseline = mean_top1("arm_baseline_hrr_2hop")
    rail15 = mean_top1("arm_rail_reproduce_15hop")
    part20 = mean_top1("arm_part_oracle_20hop")
    part25 = mean_top1("arm_part_oracle_25hop")
    part30 = mean_top1("arm_part_oracle_30hop")

    cv20 = cv_top1("arm_part_oracle_20hop")
    cv25 = cv_top1("arm_part_oracle_25hop")
    cv30 = cv_top1("arm_part_oracle_30hop")

    sanity_breached = sum(1 for p in per_seed
                            if not p.get("baseline_sanity_ok", False))
    cross_cell_breached = sum(1 for p in per_seed
                                if not p.get("cross_cell_15hop_ok", False))

    summ = (
        "BASELINE=%.4f (sanity_breach=%d/%d) "
        "RAIL_15HOP=%.4f (cross_cell_breach=%d/%d; target=%.4f) "
        "PART_20HOP=%.4f (cv=%.3f) "
        "PART_25HOP=%.4f (cv=%.3f) "
        "PART_30HOP=%.4f (cv=%.3f)"
    ) % (
        baseline, sanity_breached, len(per_seed),
        rail15, cross_cell_breached, len(per_seed), CROSS_CELL_15HOP_TARGET,
        part20, cv20, part25, cv25, part30, cv30,
    )

    half = max(1, (len(per_seed) + 1) // 2)

    if sanity_breached >= half:
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ
    if cross_cell_breached >= half:
        return "CROSS_CELL_BREACH", "CROSS_CELL_BREACH_RAIL_15HOP_OUT_OF_BAND: " + summ

    def hp_at_depth(mean_val, cv_val, hp):
        if math.isnan(mean_val):
            return False
        cv_ok = math.isnan(cv_val) or cv_val <= PHASE_CV_MAX
        return (mean_val >= hp) and cv_ok

    def hf_at_depth(mean_val, hf):
        return (not math.isnan(mean_val)) and (mean_val < hf)

    pass20 = hp_at_depth(part20, cv20, HP_20HOP)
    pass25 = hp_at_depth(part25, cv25, HP_25HOP)
    pass30 = hp_at_depth(part30, cv30, HP_30HOP)

    fail20 = hf_at_depth(part20, HF_20HOP)
    fail25 = hf_at_depth(part25, HF_25HOP)
    fail30 = hf_at_depth(part30, HF_30HOP)

    if pass20 and pass25 and pass30:
        return ("CHAIN_GRADE_DEPTH_30_EXTENDS",
                "CHAIN_GRADE_DEPTH_30_EXTENDS_ALL_3_PHASE_POINTS_HARD_PASS: " + summ)
    if pass20 and pass25 and not pass30:
        return ("PARTIAL_DEPTH_EXTENDS_TO_25",
                "PARTIAL_DEPTH_EXTENDS_TO_25_CLIFF_BETWEEN_25_AND_30: " + summ)
    if pass20 and not pass25 and not pass30:
        return ("PARTIAL_DEPTH_EXTENDS_TO_20",
                "PARTIAL_DEPTH_EXTENDS_TO_20_CLIFF_BETWEEN_20_AND_25: " + summ)
    if fail20 and fail25 and fail30:
        return ("DEPTH_15_IS_CEILING",
                "DEPTH_15_IS_CEILING_MECHANISM_DID_NOT_EXTEND: " + summ)
    return ("MIDDLE_BAND", "MIDDLE_BAND_MIXED_PHASE_POINTS: " + summ)


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
            "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
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

    # META_RULE_H cardinality verify
    for p in per_seed:
        rail_n = p.get("arm_rail_reproduce_15hop", {}).get("n_queries", 0)
        if rail_n < EXPECTED_N_UNITS and HARD_FAIL_CARDINALITY_BREACH:
            print("[CARDINALITY_BREACH] rail_15hop n_queries=%d < expected=%d "
                  "(seed=%s)" % (rail_n, EXPECTED_N_UNITS, p.get("seed")),
                  flush=True)

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
        "COMPOSED_AGAINST": "phase_diagram_multihop_depth_extension_via_partition_oracle_v1",
        "COMPOSED_METRIC": "PART_15HOP=0.8083 cv=0.024 (depth-15 CHAIN_GRADE)",
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_DEPTH_30: extends depth-15 CG (0.808 recall) to "
            "depth {15,20,25,30} sweep on W_depth30_extended. Discriminator: "
            "does per-step accuracy 0.986 hold at depth=30? "
            "USER pre-reg: HP=0.60 HF=0.20 at depth=30. Envelope predicts "
            "0.986^30=0.652 (optimistic) or 0.955^30=0.251 (pessimistic per-step "
            "from pointer-chain baseline). Smoke seed_7 at depth=20 (full N=8192) "
            "acts as scale-preserving discriminator preview. GPU-required at full."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
