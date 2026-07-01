"""multihop_reasoning_vc_axis_sweep_gpu_v1.

V_C-axis extension of exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.
Purpose: probe scale-invariance of per-step multihop accuracy across the vocabulary-size
axis V_C in {100, 200, 400} at fixed N=8192, PART_SIZE=10. Orthogonal to sibling cells:
  - _scale_invariance_N_axis (N axis; PART_SIZE=10 fixed)
  - _partition_size_sweep    (PART_SIZE axis; V_C=200 fixed; Wave 14 SCALE_VARIANT)
This is the V_C axis (V_C varies; PART_SIZE=10 fixed) - third orthogonal
characterization for Atom 11 multihop phase-diagram.

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01):
  Q: "multihop V_C vocabulary size axis scale invariance"
    top hits at cosine=0.28 (below 0.30 novelty threshold):
      1. Multihop notes/orchestrator results summary 2026-06-09
      2. Vocabulary size + Zipf coverage note
      3. Variant 3: Larger concept vocabulary (V_C sweep) — earlier design variant
    Novelty verdict: GENUINELY NEW — no prior cell sweeps V_C at fixed
    N=8192, PART_SIZE=10 as multihop per-step probe. The Landing-21 LLN OOD-leak
    cell showed V_C-axis effect for a DIFFERENT mechanism (OOD leak floor scales
    as sqrt(2 log V_C / N)); this cell probes chain-cleanup at fixed PART_SIZE
    argmax arity, so LLN floor is not the mechanism under test.

MEASURED REFERENCES (from parent + ceiling cells; PART_SIZE=10, N=8192, V_C=200):
  parent depth_extension_v1 d=15 (seeds 11,13,19): per_step_mean = 0.8517, 0.857, 0.8427; mean=0.8505
  ceiling_sweep_20_25_30_v1 d=15 (seeds 11,13,19): per_step_mean = 0.853, 0.8697, 0.851; mean=0.858
  ceiling_sweep d=30 (seeds 11,13,19):             per_step_mean = 0.6797, 0.6975, 0.6702; mean=0.682
  Pooled MEASURED@2026-06-27 references at V_C=200 (the reproducer arm):
    REF_15HOP = 0.858
    REF_30HOP = 0.682

CG-EXPANSION AXIS (V_C-axis): V_C varies while N=8192, PART_SIZE=10 held fixed
  ARMS (6):
    ARM_D15_VC100  d=15  V_C=100  n_partitions=10  (V_C rail; smaller vocab)
    ARM_D30_VC100  d=30  V_C=100  n_partitions=10  (V_C rail; smaller vocab)
    ARM_D15_VC200  d=15  V_C=200  n_partitions=20  (reproducer; parent regime)
    ARM_D30_VC200  d=30  V_C=200  n_partitions=20  (reproducer; parent regime)
    ARM_D15_VC400  d=15  V_C=400  n_partitions=40  (V_C rail; larger vocab)
    ARM_D30_VC400  d=30  V_C=400  n_partitions=40  (V_C rail; larger vocab)

CONFOUND NOTE (declared, not hidden):
  PART_SIZE=10 is HELD FIXED. V_C varies -> n_partitions = V_C/PART_SIZE varies as
  V_C changes. CRLB floor 1/PART_SIZE=0.10 is CONSTANT across all 6 arms (this is
  the design purpose: hold argmax-cleanup arity fixed while V_C varies).
  What varies:
    - Total concept vocabulary count (100 vs 200 vs 400 encoders in E)
    - Number of partitions (10 vs 20 vs 40 partitions)
    - Total binding density in W (chain construction samples s,o from V_C so
      different V_C means different fraction of vocabulary bound per chain)
  n_chains and PART_SIZE (local decision-space arity) are HELD FIXED. The pure
  V_C-scaling effect is: does per_step_accuracy depend on how many concepts
  exist total, given fixed local-cleanup arity?
  Prediction (informative, not verdict-forcing): if chain-cleanup is
  PART_SIZE-limited (as PS-axis Wave 14 suggested), per-step should be
  V_C-INVARIANT here (constant PART_SIZE = constant cleanup difficulty).
  If per-step degrades with V_C at fixed PART_SIZE, that's a MEASURED direction
  informative for capacity modeling.

CRLB FLOOR (per-arm, meta_rule_9 CRLB gate):
  All 6 arms: CRLB_FLOOR = 1/PART_SIZE = 1/10 = 0.10 (constant; PART_SIZE fixed)
  Measurements at parent REF (per_step_mean 0.68-0.86) far above floor.

DISCRIMINATOR REACHABILITY (both HP + HF sides reachable per V_C):
  HP band = REF +/- 0.05 -> reachable at V_C=200 reproducer arm by construction
  HF_SCALE_VARIANCE = |diff| > 0.10 -> reachable if V_C genuinely shifts per_step
  HF_MECHANISM_DEATH = top1 < 0.10 -> reachable at all V_C (floor 0.10 crlb)

VERDICT GATES (LOCKED at module init):
  HP_15_VC<v>   if |per_step_mean_15hop_vc<v> - REF_15HOP| <= HP_TOL
  HP_30_VC<v>   if |per_step_mean_30hop_vc<v> - REF_30HOP| <= HP_TOL
  cv_across_seeds <= CV_CAP required for any HP fire
  HF_SCALE_VARIANCE      if |per_step_mean - REF| > HF_TOL at any V_C
  HF_MECHANISM_DEATH     if top1 < DEATH_FLOOR at any arm
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H  if observed_n_units < EXPECTED_N_UNITS

VERDICT TIERS:
  CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS  -- all 6 arms HP
  PARTIAL_SCALE_INVARIANT_D15_ONLY     -- all d=15 arms HP; d=30 mixed
  PARTIAL_SCALE_INVARIANT_D30_ONLY     -- all d=30 arms HP; d=15 mixed (unlikely)
  PARTIAL_SCALE_INVARIANT_MIDDLE_VC_ONLY -- only VC=200 reproducer HP (rail failure)
  SCALE_VARIANT_VC_AXIS                -- HF_SCALE_VARIANCE fires
  MECHANISM_DEATH                      -- HF_MECHANISM_DEATH fires
  MIDDLE_BAND                          -- inconclusive

INFORMATIONAL FIELDS (reported regardless of verdict):
  per_arm_per_step_mean       (primary metric across seeds)
  per_arm_per_step_geometric  (derived per-hop = top1^(1/depth); Atom 11 spawn's cited form)
  per_arm_top1                (final cumulative accuracy)
  per_arm_cv                  (cv across seeds)

GPU MEMORY BUDGET (THEORETICAL@ formula):
  W at N=8192: 8192^2 * 4 = 268 MB (fp32); one W per (seed, V_C) since chains
  differ per V_C (V_C is chain-construction parameter). 3 V_C values x 1 W each
  at any time (reuse across depths via slicing) => sequential build; peak ~300 MB
  well under 8GB VRAM.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test
    across all 6 arms per seed; distinct V_C -> distinct chains + W -> distinct per_step)
  final_metrics_atomicity: tmp_replace via _seed_checkpoint.write_metrics
  except SystemExit: raise BEFORE except Exception (no BaseException)
  crlb per-arm: 1/PART_SIZE = 0.10 constant; REFs above floor
  baseline_in_band: True; MEASURED@parent REFs 0.85/0.68 in (HP_TOL, 1-HP_TOL)
  discriminator survives scale: smoke does full-N=8192 V_C=200 preview
    (reproducer arm at full-N gates before dispatch)
  HARD_PASS strictly above floor: HP band +/- 0.05; HF at +/- 0.10 window
  HP_SCOPE declared per-arm (see prereg)
  cardinality_ok: EXPECTED_N_UNITS=3; verdict emits CARDINALITY_BREACH sentinel
  no silent except: all except blocks re-raise or record diagnostic
  calibration_check: default_ok_for_this_regime (parent CG at V_C=200, PS=10)

ASCII-only; per-seed checkpoint; atexit synthesizer; zero-LLM-call assert.
Author: exp_dev 2026-07-01.
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

ANCHOR_NAME = "multihop_reasoning_vc_axis_sweep_gpu_v1"
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
# MEASURED@parent+ceiling cells 2026-06-27; PART_SIZE=10, N=8192, V_C=200 (reproducer arm).
REF_15HOP = 0.858
REF_30HOP = 0.682

# HARD_PASS: |per_step_mean - REF| <= HP_TOL
HP_TOL = 0.05
# HARD_FAIL_SCALE_VARIANCE: |per_step_mean - REF| > HF_TOL
HF_TOL = 0.10
# HARD_FAIL_MECHANISM_DEATH: top1 < DEATH_FLOOR
DEATH_FLOOR = 0.10
# cv across seeds cap for HARD_PASS claim
CV_CAP = 0.10

# Locked invariants
assert 0.0 < HP_TOL < HF_TOL < 1.0
assert 0.0 < DEATH_FLOOR < 0.5
assert 0.0 < CV_CAP <= 0.20
assert 0.5 < REF_15HOP < 1.0 and 0.5 < REF_30HOP < 1.0

# Cell config (PART_SIZE held fixed; V_C varies)
N_DIM_FIXED = 8192
V_C_VALUES = [100, 200, 400]
V_PRED = 10
K_SET = 20
N_CHAINS = 200
MAX_DEPTH = 30  # covers d=15 and d=30 chains via slice
PART_SIZE_FIXED = 10
DEPTHS = [15, 30]

# Locked structural invariants
for vc in V_C_VALUES:
    assert vc % PART_SIZE_FIXED == 0, "V_C=%d not divisible by PART_SIZE=%d" % (vc, PART_SIZE_FIXED)
N_PARTITIONS_PER_VC = {vc: vc // PART_SIZE_FIXED for vc in V_C_VALUES}  # {100:10, 200:20, 400:40}
assert N_PARTITIONS_PER_VC == {100: 10, 200: 20, 400: 40}

# CRLB floor per V_C (constant since PART_SIZE fixed)
CRLB_FLOOR_CONST = round(1.0 / PART_SIZE_FIXED, 4)  # 0.10
assert CRLB_FLOOR_CONST == 0.10
CRLB_FLOOR_PER_VC = {vc: CRLB_FLOOR_CONST for vc in V_C_VALUES}

# Discriminator reachability: HP window (REF +/- 0.05) reachable at V_C=200
# reproducer by construction. HF_SCALE_VARIANCE reachable if V_C shifts per_step_mean
# by > 0.10 (empirical question - hypothesis is INVARIANT under fixed PART_SIZE).
DISCRIMINATOR_REACHABILITY = True
DISCRIMINATOR_REACH_NOTE = (
    "HP window REF+/-%.2f reachable at V_C=200 reproducer arm (parent regime CG). "
    "HF_SCALE_VARIANCE (|diff|>%.2f) reachable if V_C shifts per_step >0.10. "
    "HF_MECHANISM_DEATH reachable at all V_C (crlb floor 0.10 < death 0.10 boundary; "
    "mechanism failure pushes top1 below 0.10)." % (HP_TOL, HF_TOL)
)

# CARDINALITY
if RUN_MODE == "smoke":
    SEEDS = [7]
    N_CHAINS_LOCAL = 30
else:
    SEEDS = [7, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200

EXPECTED_N_UNITS = len(SEEDS)
CARDINALITY_OK = True
ARMS_PER_SEED = len(V_C_VALUES) * len(DEPTHS)  # 6

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopVcAxisSweepV1: N=%d part_size=%d v_c_values=%s n_parts=%s V_P=%d "
    "K=%d depths=%s max_depth=%d n_chains=%d seeds=%s mode=%s encoder=%s "
    "REF_15=%.4f REF_30=%.4f HP_TOL=%.2f HF_TOL=%.2f DEATH_FLOOR=%.2f "
    "CV_CAP=%.2f crlb_floor=%.4f"
) % (
    N_DIM_FIXED, PART_SIZE_FIXED, V_C_VALUES, list(N_PARTITIONS_PER_VC.values()),
    V_PRED, K_SET, DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL, SEEDS, RUN_MODE,
    ENCODER_PROVENANCE, REF_15HOP, REF_30HOP, HP_TOL, HF_TOL, DEATH_FLOOR,
    CV_CAP, CRLB_FLOOR_CONST,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from sibling N-axis + PS-axis cells)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    """Bipolar bit vectors on GPU; row-normalized."""
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set):
    """VERBATIM port of parent make_deep_chains."""
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
    """Partition-oracle routed cleanup at given depth + PART_SIZE.

    NOTE: V_effective is E.shape[0]; here V_effective == V_C for the arm's V_C.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    V_effective = E.shape[0]
    assert V_effective % part_size == 0, (
        "V_effective=%d not divisible by part_size=%d" % (V_effective, part_size))
    n_partitions = V_effective // part_size
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
    top1 = round(hits / max(n, 1), 4)
    per_step_mean = round(float(np.mean(per_step_acc)), 4)
    # Derived per-hop geometric mean (Atom 11 spawn-prompt-cited form)
    if top1 > 0 and depth > 0:
        per_step_geom = round(top1 ** (1.0 / depth), 4)
    else:
        per_step_geom = 0.0
    return {"top1": top1,
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "per_step_mean": per_step_mean,
            "per_step_geometric": per_step_geom,
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "part_size": part_size, "V_C": V_effective,
            "mechanism": "partition_oracle_per_hop_gpu"}


# ----------------------------------------------------------------------------
# ARMS-MUST-DIFFER hash test (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ(arm_outputs: Dict[str, list]) -> Dict[str, str]:
    """SHA256 of per-step accuracy tuple per arm; assert distinct."""
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
# Self-test (formula sanity + regression + V_C mechanics)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    P = 4
    sq = math.sqrt(n)

    # T1: bipolar shapes + norm across three tiny V_C values divisible by ps=2
    for V_tiny in [20, 40, 80]:
        E_t = bipolar_gpu(V_tiny, n, g)
        assert E_t.shape == (V_tiny, n)
        assert abs(float(E_t[0].norm()) - 1.0) < 1e-4
    R = bipolar_gpu(P, n, g)
    assert R.shape == (P, n)

    # T2: chain construction at MAX_DEPTH=30 at V_tiny (must have V > max_depth+1
    # to avoid disallow-set exhaustion; MAX_DEPTH=30 needs V >= 31)
    for V_tiny in [40, 80]:
        E_t = bipolar_gpu(V_tiny, n, g)
        triples, chains = make_deep_chains(8, V_tiny, P, max_depth=MAX_DEPTH,
                                            g=g, disallow_s=set())
        assert len(chains) == 8
        assert len(triples) == 8 * MAX_DEPTH
        # Test W + arm at this tiny V
        W = ingest_hebbian_gpu(triples, E_t, R, sq, n)
        assert W.shape == (n, n)
        assert torch.isfinite(W).all()
        # part_size=2 divides V_tiny=40 and V_tiny=80
        r15 = arm_part_oracle_at_depth(E_t, R, sq, W, [c[:15] for c in chains],
                                        depth=15, part_size=2)
        assert 0.0 <= r15["top1"] <= 1.0
        assert len(r15["per_step_acc"]) == 15
        assert r15["n_partitions"] == V_tiny // 2
        assert r15["V_C"] == V_tiny
        assert r15["part_size"] == 2
        r30 = arm_part_oracle_at_depth(E_t, R, sq, W, chains, depth=30, part_size=2)
        assert 0.0 <= r30["top1"] <= 1.0
        assert len(r30["per_step_acc"]) == 30

    # T3: bands LOCKED (regression on accidental band drift)
    assert REF_15HOP == 0.858 and REF_30HOP == 0.682
    assert HP_TOL == 0.05 and HF_TOL == 0.10 and DEATH_FLOOR == 0.10
    assert CV_CAP == 0.10
    assert V_C_VALUES == [100, 200, 400]
    assert DEPTHS == [15, 30]
    assert PART_SIZE_FIXED == 10
    assert N_DIM_FIXED == 8192

    # T4: V_C structural invariants
    assert N_PARTITIONS_PER_VC[100] == 10
    assert N_PARTITIONS_PER_VC[200] == 20
    assert N_PARTITIONS_PER_VC[400] == 40
    assert CRLB_FLOOR_CONST == 0.10
    for vc in V_C_VALUES:
        assert CRLB_FLOOR_PER_VC[vc] == 0.10

    # T5: LLM call counter = 0
    assert _LLM_CALL_COUNTER[0] == 0

    # T6: arms_must_differ mechanics
    fake = {"a": [0.5, 0.6, 0.7], "b": [0.5, 0.6, 0.7, 0.8]}
    digests = _arms_must_differ(fake)
    assert len(digests) == 2 and digests["a"] != digests["b"]
    # ARMS-MUST-DIFFER should FIRE on identical per_step
    try:
        _arms_must_differ({"a": [0.5, 0.6], "b": [0.5, 0.6]})
        raise RuntimeError("META_RULE_AF: identical arms should have raised AssertionError")
    except AssertionError:
        pass

    # T7: CARDINALITY_OK
    assert CARDINALITY_OK is True
    assert EXPECTED_N_UNITS == len(SEEDS)
    if RUN_MODE != "smoke":
        assert EXPECTED_N_UNITS == 3

    # T8: derived per-hop geometric mean formula sanity
    # top1=0.808, depth=15 -> per_step_geom ~= 0.9858 (Atom 11 spawn-cited form)
    geom_expected = 0.808 ** (1.0 / 15.0)
    assert 0.985 < geom_expected < 0.987, geom_expected

    # T9: production V_C values divisible by production PART_SIZE
    for vc in V_C_VALUES:
        assert vc % PART_SIZE_FIXED == 0

    print("[selftest] PASS v_c_values=%s n_parts=%s crlb=%.2f gpu=%s "
          "per_step_geom_check=%.4f" % (
            V_C_VALUES, list(N_PARTITIONS_PER_VC.values()), CRLB_FLOOR_CONST,
            GPU_AVAIL, geom_expected), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# Defensive error-checking helpers
# ----------------------------------------------------------------------------

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
    os.makedirs(output_dir, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, anchor_name: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    N = N_DIM_FIXED
    sq = math.sqrt(N)

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    # V_P encoder is shared across all V_C arms (P is a relation vocabulary,
    # independent of concept vocab size); build once per seed.
    print("  [seed=%d] building R (V_P=%d, N=%d)" % (seed, V_PRED, N), flush=True)
    R = bipolar_gpu(V_PRED, N, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N,
        "V_C_values": V_C_VALUES, "V_P": V_PRED, "K_set": K_SET,
        "part_size": PART_SIZE_FIXED,
        "n_partitions_per_vc": {str(vc): N_PARTITIONS_PER_VC[vc] for vc in V_C_VALUES},
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS, "max_depth": MAX_DEPTH,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    arm_outputs_for_hash = {}
    peak_alloc_mb = 0.0

    for vc in V_C_VALUES:
        # Fresh E, chains, W per V_C (V_C is chain-construction parameter)
        print("  [seed=%d V_C=%d] building E + chains + W (max_depth=%d, n_chains=%d)" % (
            seed, vc, MAX_DEPTH, N_CHAINS_LOCAL), flush=True)
        t_ing = time.time()
        E = bipolar_gpu(vc, N, g)
        triples, chains = make_deep_chains(
            N_CHAINS_LOCAL, vc, V_PRED, max_depth=MAX_DEPTH,
            g=g, disallow_s=set())
        W = ingest_hebbian_gpu(triples, E, R, sq, N)
        print("  [seed=%d V_C=%d] W built (%d triples) t=%.1fs" % (
            seed, vc, len(triples), round(time.time() - t_ing, 2)), flush=True)

        for depth in DEPTHS:
            t_arm = time.time()
            r = arm_part_oracle_at_depth(
                E, R, sq, W,
                [c[:depth] for c in chains] if depth < MAX_DEPTH else chains,
                depth=depth, part_size=PART_SIZE_FIXED)
            r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            r["W_n_bindings"] = len(triples)
            arm_key = "arm_d%d_vc%d" % (depth, vc)
            out[arm_key] = r
            arm_outputs_for_hash[arm_key] = r["per_step_acc"]
            ref = REF_15HOP if depth == 15 else REF_30HOP
            print("  [seed=%d V_C=%d d=%d] top1=%.4f per_step_mean=%.4f "
                  "geom=%.4f (REF=%.4f, |diff|=%.4f) t=%.1fs" % (
                      seed, vc, depth, r["top1"], r["per_step_mean"],
                      r["per_step_geometric"], ref,
                      abs(r["per_step_mean"] - ref),
                      r["elapsed_s_arm"]), flush=True)

        # Track GPU peak, then free E+W before next V_C to keep VRAM bounded
        if GPU_AVAIL:
            peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
            peak_alloc_mb = max(peak_alloc_mb, round(peak_bytes / 1e6, 2))
            del W, E
            torch.cuda.empty_cache()

    if GPU_AVAIL:
        out["gpu_max_mem_alloc_mb"] = peak_alloc_mb
        print("  [seed=%d] GPU peak alloc across V_C: %.2f MB" % (
            seed, peak_alloc_mb), flush=True)
        del R
        torch.cuda.empty_cache()
    else:
        out["gpu_max_mem_alloc_mb"] = 0.0

    # META_RULE_AF: ARMS-MUST-DIFFER
    digests = _arms_must_differ(arm_outputs_for_hash)
    out["_arm_output_digests"] = digests
    out["arms_differ_verified"] = True

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
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

    # Gather per-arm metrics
    per_arm = {}
    for vc in V_C_VALUES:
        for depth in DEPTHS:
            arm_key = "arm_d%d_vc%d" % (depth, vc)
            per_arm[arm_key] = {
                "per_step_mean": per_step_mean_across_seeds(arm_key),
                "cv": cv_across_seeds(arm_key),
                "top1_min": top1_min(arm_key),
                "ref": REF_15HOP if depth == 15 else REF_30HOP,
                "V_C": vc, "depth": depth,
            }

    # HARD_FAIL_MECHANISM_DEATH first (applies in both smoke + full modes)
    death_arms = [k for k, v in per_arm.items()
                   if not math.isnan(v["top1_min"]) and v["top1_min"] < DEATH_FLOOR]
    if death_arms:
        return ("MECHANISM_DEATH",
                "HF_MECHANISM_DEATH: arms %s at top1_min < %.2f" % (
                    death_arms, DEATH_FLOOR))

    # HARD_FAIL_SCALE_VARIANCE: any arm |diff| > HF_TOL
    # Skip in smoke mode: smoke uses reduced n_chains (30 vs 200) which lowers
    # binding-count interference in W, inflating top1 well above parent REF.
    # This is an EXPECTED smoke-mode noise artifact, not a scale-variance signal.
    # Full-mode gates the actual scale-invariance claim.
    if RUN_MODE != "smoke":
        variance_arms = [k for k, v in per_arm.items()
                          if not math.isnan(v["per_step_mean"])
                          and abs(v["per_step_mean"] - v["ref"]) > HF_TOL]
        if variance_arms:
            summ = " | ".join("%s: ps_mean=%.4f ref=%.4f |diff|=%.4f" % (
                k, per_arm[k]["per_step_mean"], per_arm[k]["ref"],
                abs(per_arm[k]["per_step_mean"] - per_arm[k]["ref"]))
                for k in variance_arms)
            return ("SCALE_VARIANT_VC_AXIS",
                    "HF_SCALE_VARIANCE: |diff|>%.2f at arms %s | %s" % (
                        HF_TOL, variance_arms, summ))

    # HARD_PASS classification: arm HP if |diff| <= HP_TOL AND cv <= CV_CAP
    def arm_hp(arm_key: str) -> bool:
        v = per_arm[arm_key]
        if math.isnan(v["per_step_mean"]):
            return False
        if abs(v["per_step_mean"] - v["ref"]) > HP_TOL:
            return False
        if not math.isnan(v["cv"]) and v["cv"] > CV_CAP:
            return False
        return True

    hp_arms = {k: arm_hp(k) for k in per_arm.keys()}
    all_hp = all(hp_arms.values())
    d15_hp = all(hp_arms["arm_d15_vc%d" % vc] for vc in V_C_VALUES)
    d30_hp = all(hp_arms["arm_d30_vc%d" % vc] for vc in V_C_VALUES)
    vc200_only_hp = (hp_arms["arm_d15_vc200"]
                     and hp_arms["arm_d30_vc200"]
                     and not all_hp)

    # Build summary string
    lines = []
    for k in sorted(per_arm.keys()):
        v = per_arm[k]
        lines.append("%s: ps_mean=%.4f cv=%.3f ref=%.4f |diff|=%.4f HP=%s" % (
            k, v["per_step_mean"], v["cv"], v["ref"],
            abs(v["per_step_mean"] - v["ref"]) if not math.isnan(v["per_step_mean"]) else float("nan"),
            hp_arms[k]))
    summ = " | ".join(lines)

    # Smoke mode: PASS if mechanism operates end-to-end at all 6 arms
    if RUN_MODE == "smoke":
        vals = [per_arm[k]["per_step_mean"] for k in per_arm.keys()]
        any_nan = any(math.isnan(v) for v in vals)
        if any_nan:
            return ("HARD_FAIL",
                    "SMOKE_FAIL: missing per_step_mean at some arm | " + summ)
        # Smoke discriminator: reproducer arms (V_C=200) should approximately track REFs;
        # ARMS-MUST-DIFFER hash test already asserted in run_seed. At smoke N_chains=30
        # per_step is noisy; use loose discrimination (mechanism alive at all 6).
        top1s = [per_arm[k]["top1_min"] for k in per_arm.keys()]
        if all(t >= 0.05 for t in top1s):
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at 6 arms; V_C ranges probed | " + summ)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at some arm | " + summ)

    # Full-mode tiers
    if all_hp:
        return ("CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS",
                "CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS: all 6 arms HP across "
                "V_C in %s at N=%d PART_SIZE=%d; Atom 11 CG-lift on V_C-axis; "
                "PART_SIZE-limited-cleanup hypothesis SUPPORTED | %s" % (
                    V_C_VALUES, N_DIM_FIXED, PART_SIZE_FIXED, summ))
    if d15_hp and not d30_hp:
        return ("PARTIAL_SCALE_INVARIANT_D15_ONLY",
                "PARTIAL_SCALE_INVARIANT_D15_ONLY: all d=15 arms HP; d=30 mixed | " + summ)
    if d30_hp and not d15_hp:
        return ("PARTIAL_SCALE_INVARIANT_D30_ONLY",
                "PARTIAL_SCALE_INVARIANT_D30_ONLY: all d=30 arms HP; d=15 mixed | " + summ)
    if vc200_only_hp:
        return ("PARTIAL_SCALE_INVARIANT_MIDDLE_VC_ONLY",
                "PARTIAL_SCALE_INVARIANT_MIDDLE_VC_ONLY: reproducer V_C=200 arms "
                "HP but rail V_C arms not | " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial HP; hp_arms=%s | %s" % (hp_arms, summ))


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
                                  run_config={"N": N_DIM_FIXED, "run_mode": RUN_MODE})
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
    print("[config] anchor=%s mode=%s seeds=%s N=%d gpu=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM_FIXED, GPU_AVAIL, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE,
                          expected_n_units=len(SEEDS))

    run_config = {"N": N_DIM_FIXED, "run_mode": RUN_MODE}
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
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "cardinality_ok": CARDINALITY_OK,
        "expected_n_units": EXPECTED_N_UNITS,
        "crlb_floor_per_vc": CRLB_FLOOR_PER_VC,
        "crlb_formula": "per_hop_random_guess = 1/PART_SIZE (constant across V_C)",
        "discriminator_reachability": DISCRIMINATOR_REACHABILITY,
        "discriminator_reach_note": DISCRIMINATOR_REACH_NOTE,
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_V_C_AXIS_SWEEP: third orthogonal phase-diagram "
            "characterization for Atom 11 - varies V_C in {100, 200, 400} at "
            "fixed N=8192, PART_SIZE=10 (n_partitions in {10, 20, 40}, "
            "crlb_floor=0.10 constant). Sibling cells cover N-axis "
            "(_scale_invariance_N_axis) and PART_SIZE-axis (_partition_size_sweep "
            "- Wave 14 SCALE_VARIANT). V_C-axis tests hypothesis that "
            "chain-cleanup is PART_SIZE-limited (not V_C-limited): if per_step "
            "invariant across V_C at fixed PART_SIZE, hypothesis supported. "
            "HP if |per_step_mean - REF| <= 0.05 AND cv <= 0.10; HF_SCALE_VARIANCE "
            "if |diff| > 0.10 at any V_C. Verdict tier "
            "CHAIN_GRADE_SCALE_INVARIANT_VC_AXIS lifts Atom 11 to CG on V_C-axis; "
            "informational per_step_geometric = top1^(1/depth) reported for "
            "Atom 11 spawn-cited derived-per-hop form."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)


if __name__ == "__main__":
    _OUT_DIR_FOR_CRASH = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT_DIR_FOR_CRASH, ANCHOR_NAME, e)
        raise
