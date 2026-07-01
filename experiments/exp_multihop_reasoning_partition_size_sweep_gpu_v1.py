"""multihop_reasoning_partition_size_sweep_gpu_v1.

PART_SIZE-axis extension of exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1.
Purpose: LIFT Atom 11 (Skunkworks 2026-07-01, MM_STANDARD) to CHAIN_GRADE via
CG-expansion criterion (b): "different PART_SIZE at same N=8192".

Sibling cell (exp_multihop_reasoning_scale_invariance_N_axis_gpu_v1) covers
expansion (a) different N at same PART_SIZE=10. This cell covers axis (b).

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01, exp_dev on spawn):
  Q1: "multihop reasoning PART_SIZE 5 20 partition oracle per step accuracy"
      top hit cosine=0.30 (prereg depth_extension_v1; PART_SIZE=10 lineage);
      NO prior cell sweeps PART_SIZE at fixed N=8192
  Q2: "multihop different partition size N=8192 scale invariance"
      top hit cosine=0.30 (scale-invariant differentiators note);
      NO prior cell varies PART_SIZE with fixed V_C=200
  Rediscovery-vs-novel: this cell is GENUINELY NEW along the PART_SIZE axis.
  Reproducer arm PART_SIZE=10 at d=15,30 must reproduce parent REFs.

MEASURED REFERENCES (from parent + ceiling cells; PART_SIZE=10, N=8192):
  parent depth_extension_v1 d=15 (seeds 11,13,19): per_step_mean = 0.8517, 0.857, 0.8427; mean=0.8505
  ceiling_sweep_20_25_30_v1 d=15 (seeds 11,13,19): per_step_mean = 0.853, 0.8697, 0.851; mean=0.858
  ceiling_sweep d=30 (seeds 11,13,19):             per_step_mean = 0.6797, 0.6975, 0.6702; mean=0.682
  Pooled MEASURED@2026-06-27 references (6 values for d=15, 3 values for d=30):
    REF_15HOP = 0.858   (pooled mean; matches sibling N-axis cell REF)
    REF_30HOP = 0.682   (ceiling cell mean; matches sibling N-axis cell REF)

HONEST TRANSCRIPTION NOTE:
  Spawn prompt cited "0.9853" as Atom 11 target. Reading the actual metrics.json,
  per_step_mean = np.mean(per_step_acc) yields the values above (0.858 at d=15,
  0.682 at d=30). The 0.9853 figure appears to reference DERIVED per-hop
  conditional (= top1^(1/depth) geometric mean); e.g., 0.808^(1/15) ~= 0.986.
  This cell uses per_step_mean matching sibling convention (Atom 11 lineage
  metric of record). Both computed + reported per-arm for verification.

CG-EXPANSION AXIS (b): PART_SIZE varies while N=8192 held fixed
  ARMS (6):
    ARM_PART_ORACLE_15HOP_PS5   d=15  PART_SIZE= 5  n_partitions=40  (rail)
    ARM_PART_ORACLE_30HOP_PS5   d=30  PART_SIZE= 5  n_partitions=40  (rail)
    ARM_PART_ORACLE_15HOP_PS10  d=15  PART_SIZE=10  n_partitions=20  (reproducer)
    ARM_PART_ORACLE_30HOP_PS10  d=30  PART_SIZE=10  n_partitions=20  (reproducer)
    ARM_PART_ORACLE_15HOP_PS20  d=15  PART_SIZE=20  n_partitions=10  (rail)
    ARM_PART_ORACLE_30HOP_PS20  d=30  PART_SIZE=20  n_partitions=10  (rail)

CONFOUND NOTE (declared, not hidden):
  V_C=200 is HELD FIXED. PART_SIZE varies -> n_partitions varies as V_C/PART_SIZE.
  n_partitions in {40, 20, 10} means the argmax-cleanup arity varies:
    PART_SIZE= 5 -> argmax over 5 candidates (harder for random; more forgiving of noise)
    PART_SIZE=10 -> argmax over 10 candidates (parent regime)
    PART_SIZE=20 -> argmax over 20 candidates (larger local decision-space)
  This is the EXPECTED confound of the PART_SIZE axis and IS what the spawn asks
  ("different PART_SIZE at same N"). If per-step accuracy holds across all three
  PART_SIZE at the same |per_step - REF| tolerance, scale-invariance strengthens.
  If per-step degrades monotonically with PART_SIZE, that's a MEASURED direction
  (larger local cleanup pool -> more noise wins) informative for future modeling.

CRLB FLOOR (per-arm, meta_rule_9 CRLB gate):
  CRLB_FLOOR_PS5  = 1/5  = 0.200
  CRLB_FLOOR_PS10 = 1/10 = 0.100
  CRLB_FLOOR_PS20 = 1/20 = 0.050
  All measurements at parent REF (per_step_mean 0.68-0.86) far above floors.

DISCRIMINATOR REACHABILITY (both HP + HF sides reachable per PART_SIZE):
  HP band = REF +/- 0.05 -> reachable at parent regime by construction
  HF_SCALE_VARIANCE = |diff| > 0.10 -> reachable if PART_SIZE genuinely shifts
  HF_MECHANISM_DEATH = top1 < 0.10 -> reachable at parent regime for PS20 (floor 0.05
    is below death threshold; mechanism failure would push top1 below 0.10)

VERDICT GATES (LOCKED at module init):
  HP_15_PS<k>   if |per_step_mean_15hop_ps<k> - REF_15HOP| <= HP_TOL
  HP_30_PS<k>   if |per_step_mean_30hop_ps<k> - REF_30HOP| <= HP_TOL
  cv_across_seeds <= CV_CAP required for any HP fire
  HF_SCALE_VARIANCE      if |per_step_mean - REF| > HF_TOL at any PART_SIZE
  HF_MECHANISM_DEATH     if top1 < DEATH_FLOOR at any arm
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H  if observed_n_units < EXPECTED_N_UNITS

VERDICT TIERS:
  CHAIN_GRADE_SCALE_INVARIANT_PS_AXIS  -- all 6 arms HP
  PARTIAL_SCALE_INVARIANT_D15_ONLY     -- all d=15 arms HP; d=30 mixed
  PARTIAL_SCALE_INVARIANT_D30_ONLY     -- all d=30 arms HP; d=15 mixed (unlikely)
  PARTIAL_SCALE_INVARIANT_MIDDLE_PS_ONLY -- only PS10 reproducer HP (rail failure)
  SCALE_VARIANT_PS_AXIS                -- HF_SCALE_VARIANCE fires
  MECHANISM_DEATH                      -- HF_MECHANISM_DEATH fires
  MIDDLE_BAND                          -- inconclusive

INFORMATIONAL FIELDS (reported regardless of verdict):
  per_arm_per_step_mean       (primary metric across seeds)
  per_arm_per_step_geometric  (derived per-hop = top1^(1/depth); Atom 11 spawn's cited form)
  per_arm_top1                (final cumulative accuracy)
  per_arm_cv                  (cv across seeds)

GPU MEMORY BUDGET (THEORETICAL@ formula):
  W at N=8192: 8192^2 * 4 = 268 MB (fp32); one W per seed (max_depth=30 covers
  d=15 slice); peak alloc ~300 MB well under 8GB VRAM.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test
    across all 6 arms per seed; distinct partition boundaries + distinct per_step)
  final_metrics_atomicity: tmp_replace via _seed_checkpoint.write_metrics
  except SystemExit: raise BEFORE except Exception (no BaseException)
  crlb per-arm: 1/PART_SIZE; all in [0.05, 0.20]; REFs above all floors
  baseline_in_band: True; MEASURED@parent REFs 0.85/0.68 in (HP_TOL, 1-HP_TOL)
  discriminator survives scale: smoke does full-N=8192 PART_SIZE=10 preview
    (reproducer arm at full-N gates before dispatch)
  HARD_PASS strictly above floor: HP band +/- 0.05; HF at +/- 0.10 window
  HP_SCOPE declared per-arm (see prereg)
  cardinality_ok: EXPECTED_N_UNITS=3; verdict emits CARDINALITY_BREACH sentinel
  no silent except: all except blocks re-raise or record diagnostic
  calibration_check: default_ok_for_this_regime (parent CG at PART_SIZE=10)

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

ANCHOR_NAME = "multihop_reasoning_partition_size_sweep_gpu_v1"
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
# MEASURED@parent+ceiling cells 2026-06-27; PART_SIZE=10, N=8192; pooled across seeds.
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

# Cell config (V_C held fixed; PART_SIZE varies)
N_DIM_FIXED = 8192
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
MAX_DEPTH = 30  # covers d=15 and d=30 chains via slice; one W per seed per PART_SIZE bank

PART_SIZES = [5, 10, 20]
DEPTHS = [15, 30]

# Locked structural invariants
for ps in PART_SIZES:
    assert V_CONCEPTS % ps == 0, "V_C=%d not divisible by PART_SIZE=%d" % (V_CONCEPTS, ps)
N_PARTITIONS_PER_PS = {ps: V_CONCEPTS // ps for ps in PART_SIZES}  # {5:40, 10:20, 20:10}
assert N_PARTITIONS_PER_PS == {5: 40, 10: 20, 20: 10}

# CRLB floor per PART_SIZE (argmax over PART_SIZE candidates)
CRLB_FLOOR_PER_PS = {ps: round(1.0 / ps, 4) for ps in PART_SIZES}  # {5:0.20, 10:0.10, 20:0.05}
assert CRLB_FLOOR_PER_PS[5] == 0.2 and CRLB_FLOOR_PER_PS[10] == 0.1 and CRLB_FLOOR_PER_PS[20] == 0.05

# Discriminator reachability: HP window (REF +/- 0.05) reachable at parent regime
# by construction (parent CG at PS=10 satisfies both). HF_SCALE_VARIANCE reachable
# if PART_SIZE genuinely shifts per_step_mean by > 0.10 (empirical question).
DISCRIMINATOR_REACHABILITY = True
DISCRIMINATOR_REACH_NOTE = (
    "HP window REF+/-%.2f reachable at parent regime (PS=10 reproducer). "
    "HF_SCALE_VARIANCE (|diff|>%.2f) reachable if PART_SIZE shifts per_step >0.10. "
    "HF_MECHANISM_DEATH reachable at all PART_SIZE (floor 1/PS < 0.10 for PS=20)." % (
        HP_TOL, HF_TOL)
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
ARMS_PER_SEED = len(PART_SIZES) * len(DEPTHS)  # 6

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopPartitionSizeSweepV1: N=%d V_C=%d V_P=%d K=%d "
    "part_sizes=%s n_parts=%s depths=%s max_depth=%d n_chains=%d seeds=%s "
    "mode=%s encoder=%s REF_15=%.4f REF_30=%.4f HP_TOL=%.2f HF_TOL=%.2f "
    "DEATH_FLOOR=%.2f CV_CAP=%.2f crlb_per_ps=%s"
) % (
    N_DIM_FIXED, V_CONCEPTS, V_PRED, K_SET,
    PART_SIZES, list(N_PARTITIONS_PER_PS.values()), DEPTHS,
    MAX_DEPTH, N_CHAINS_LOCAL, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    REF_15HOP, REF_30HOP, HP_TOL, HF_TOL, DEATH_FLOOR, CV_CAP,
    list(CRLB_FLOOR_PER_PS.values()),
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from sibling N-axis + parent cells)
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
    """Partition-oracle routed cleanup at given depth + PART_SIZE."""
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
            "part_size": part_size,
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
# Self-test (formula sanity + regression + partition-size mechanics)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40  # divisible by 5, 10, 20
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at MAX_DEPTH=30
    triples, chains = make_deep_chains(8, V, P, max_depth=MAX_DEPTH,
                                        g=g, disallow_s=set())
    assert len(chains) == 8
    assert len(triples) == 8 * MAX_DEPTH

    # T3: ingest + part_oracle on tiny config
    W = ingest_hebbian_gpu(triples, E, R, sq, n)
    assert W.shape == (n, n)
    assert torch.isfinite(W).all()

    # T4: part_oracle at d=15 and d=30 across three PART_SIZEs (tiny V=40)
    for ps in [2, 4, 8]:  # V=40 divisible; smaller variants than production PART_SIZES
        assert V % ps == 0
        r15 = arm_part_oracle_at_depth(E, R, sq, W, [c[:15] for c in chains],
                                        depth=15, part_size=ps)
        assert 0.0 <= r15["top1"] <= 1.0
        assert len(r15["per_step_acc"]) == 15
        assert r15["n_partitions"] == V // ps
        assert r15["part_size"] == ps
        r30 = arm_part_oracle_at_depth(E, R, sq, W, chains, depth=30,
                                        part_size=ps)
        assert 0.0 <= r30["top1"] <= 1.0
        assert len(r30["per_step_acc"]) == 30

    # T5: bands LOCKED (regression on accidental band drift)
    assert REF_15HOP == 0.858 and REF_30HOP == 0.682
    assert HP_TOL == 0.05 and HF_TOL == 0.10 and DEATH_FLOOR == 0.10
    assert CV_CAP == 0.10
    assert PART_SIZES == [5, 10, 20]
    assert DEPTHS == [15, 30]
    assert V_CONCEPTS == 200
    assert N_DIM_FIXED == 8192

    # T6: partition-size structural invariants
    assert N_PARTITIONS_PER_PS[5] == 40
    assert N_PARTITIONS_PER_PS[10] == 20
    assert N_PARTITIONS_PER_PS[20] == 10
    assert CRLB_FLOOR_PER_PS[5] == 0.20
    assert CRLB_FLOOR_PER_PS[10] == 0.10
    assert CRLB_FLOOR_PER_PS[20] == 0.05

    # T7: LLM call counter = 0
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: arms_must_differ mechanics
    fake = {"a": [0.5, 0.6, 0.7], "b": [0.5, 0.6, 0.7, 0.8]}
    digests = _arms_must_differ(fake)
    assert len(digests) == 2 and digests["a"] != digests["b"]

    # T9: CARDINALITY_OK
    assert CARDINALITY_OK is True
    assert EXPECTED_N_UNITS == len(SEEDS)
    if RUN_MODE != "smoke":
        assert EXPECTED_N_UNITS == 3

    # T10: derived per-hop geometric mean formula sanity
    # top1=0.808, depth=15 -> per_step_geom ~= 0.9858 (Atom 11 spawn-cited form)
    test_r = {"top1": 0.808, "depth": 15}
    geom_expected = 0.808 ** (1.0 / 15.0)
    assert 0.985 < geom_expected < 0.987, geom_expected

    print("[selftest] PASS part_sizes=%s crlb=%s gpu=%s per_step_geom_check=%.4f" % (
        PART_SIZES, list(CRLB_FLOOR_PER_PS.values()), GPU_AVAIL, geom_expected),
        flush=True)


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

    print("  [seed=%d] building E (V_C=%d, N=%d)" % (
        seed, V_CONCEPTS, N), flush=True)
    E = bipolar_gpu(V_CONCEPTS, N, g)
    R = bipolar_gpu(V_PRED, N, g)

    # Build W once at max_depth=30; slice for d=15 arm.
    # NOTE: per-PART_SIZE independent chains would confound seed vs PART_SIZE.
    # We use the SAME chains + W across all PART_SIZEs (only the partition
    # boundary changes) so PART_SIZE is the sole differentiator. Chains are
    # drawn from V_C=200 regardless of PART_SIZE; only the partition granularity
    # differs per arm.
    print("  [seed=%d] building chains + W (max_depth=%d, n_chains=%d)" % (
        seed, MAX_DEPTH, N_CHAINS_LOCAL), flush=True)
    t_ing = time.time()
    triples, chains = make_deep_chains(
        N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
        g=g, disallow_s=set())
    W = ingest_hebbian_gpu(triples, E, R, sq, N)
    print("  [seed=%d] W built (%d triples) t=%.1fs" % (
        seed, len(triples), round(time.time() - t_ing, 2)), flush=True)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N,
        "V_C": V_CONCEPTS, "V_P": V_PRED, "K_set": K_SET,
        "part_sizes": PART_SIZES,
        "n_partitions_per_ps": {str(ps): N_PARTITIONS_PER_PS[ps] for ps in PART_SIZES},
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS, "max_depth": MAX_DEPTH,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL, "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    arm_outputs_for_hash = {}
    for ps in PART_SIZES:
        for depth in DEPTHS:
            t_arm = time.time()
            r = arm_part_oracle_at_depth(
                E, R, sq, W,
                [c[:depth] for c in chains] if depth < MAX_DEPTH else chains,
                depth=depth, part_size=ps)
            r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            r["W_n_bindings"] = len(triples)
            arm_key = "arm_part_oracle_%dhop_ps%d" % (depth, ps)
            out[arm_key] = r
            arm_outputs_for_hash[arm_key] = r["per_step_acc"]
            ref = REF_15HOP if depth == 15 else REF_30HOP
            print("  [seed=%d PS=%d d=%d] top1=%.4f per_step_mean=%.4f "
                  "geom=%.4f (REF=%.4f, |diff|=%.4f) t=%.1fs" % (
                      seed, ps, depth, r["top1"], r["per_step_mean"],
                      r["per_step_geometric"], ref,
                      abs(r["per_step_mean"] - ref),
                      r["elapsed_s_arm"]), flush=True)

    # GPU mem peak
    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        print("  [seed=%d] GPU peak alloc: %.2f MB" % (
            seed, out["gpu_max_mem_alloc_mb"]), flush=True)
        del W, E, R
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
    for ps in PART_SIZES:
        for depth in DEPTHS:
            arm_key = "arm_part_oracle_%dhop_ps%d" % (depth, ps)
            per_arm[arm_key] = {
                "per_step_mean": per_step_mean_across_seeds(arm_key),
                "cv": cv_across_seeds(arm_key),
                "top1_min": top1_min(arm_key),
                "ref": REF_15HOP if depth == 15 else REF_30HOP,
                "part_size": ps, "depth": depth,
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
            return ("SCALE_VARIANT_PS_AXIS",
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
    d15_hp = all(hp_arms["arm_part_oracle_15hop_ps%d" % ps] for ps in PART_SIZES)
    d30_hp = all(hp_arms["arm_part_oracle_30hop_ps%d" % ps] for ps in PART_SIZES)
    ps10_only_hp = (hp_arms["arm_part_oracle_15hop_ps10"]
                    and hp_arms["arm_part_oracle_30hop_ps10"]
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
        # Smoke discriminator: reproducer arms (PS=10) should approximately track REFs;
        # ARMS-MUST-DIFFER hash test already asserted in run_seed. At smoke N_chains=30
        # per_step is noisy; use loose discrimination (mechanism alive at all 6).
        top1s = [per_arm[k]["top1_min"] for k in per_arm.keys()]
        if all(t >= 0.05 for t in top1s):
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at 6 arms; PS ranges probed | " + summ)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at some arm | " + summ)

    # Full-mode tiers
    if all_hp:
        return ("CHAIN_GRADE_SCALE_INVARIANT_PS_AXIS",
                "CHAIN_GRADE_SCALE_INVARIANT_PS_AXIS: all 6 arms HP across "
                "PART_SIZE in %s at N=%d; Atom 11 CG-lift on PS-axis; expansion "
                "criterion (b) satisfied | %s" % (PART_SIZES, N_DIM_FIXED, summ))
    if d15_hp and not d30_hp:
        return ("PARTIAL_SCALE_INVARIANT_D15_ONLY",
                "PARTIAL_SCALE_INVARIANT_D15_ONLY: all d=15 arms HP; d=30 mixed | " + summ)
    if d30_hp and not d15_hp:
        return ("PARTIAL_SCALE_INVARIANT_D30_ONLY",
                "PARTIAL_SCALE_INVARIANT_D30_ONLY: all d=30 arms HP; d=15 mixed | " + summ)
    if ps10_only_hp:
        return ("PARTIAL_SCALE_INVARIANT_MIDDLE_PS_ONLY",
                "PARTIAL_SCALE_INVARIANT_MIDDLE_PS_ONLY: reproducer PS=10 arms "
                "HP but rail PART_SIZE arms not | " + summ)
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
        "crlb_floor_per_ps": CRLB_FLOOR_PER_PS,
        "crlb_formula": "per_hop_random_guess = 1/PART_SIZE",
        "discriminator_reachability": DISCRIMINATOR_REACHABILITY,
        "discriminator_reach_note": DISCRIMINATOR_REACH_NOTE,
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_PARTITION_SIZE_SWEEP: CG-expansion axis (b) for "
            "Atom 11 (Skunkworks 2026-07-01 MM_STANDARD) - varies PART_SIZE in "
            "{5, 10, 20} at fixed N=8192, V_C=200 (n_partitions in {40, 20, 10}). "
            "Sibling cell _N_axis_gpu covers axis (a) different N at same "
            "PART_SIZE=10. HP if |per_step_mean - REF| <= 0.05 AND cv <= 0.10; "
            "HF_SCALE_VARIANCE if |diff| > 0.10 at any PART_SIZE. Verdict tier "
            "CHAIN_GRADE_SCALE_INVARIANT_PS_AXIS lifts Atom 11 to CG on PS-axis; "
            "informational per_step_geometric = top1^(1/depth) reported for the "
            "Atom 11 spawn-cited derived-per-hop form (0.985ish)."
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
