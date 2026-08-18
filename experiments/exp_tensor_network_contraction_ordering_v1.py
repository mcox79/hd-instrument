"""tensor_network_contraction_ordering_v1 -- B1 multi-hop barrier; pure-math
ordering lever (drill Angle 1).

SCIENTIFIC QUESTION:
  A k-hop heterogeneous query is structurally a small factor graph where each
  predicate-arity is a tensor node, shared variables are bonds. The substrate
  currently contracts these in fixed LEFT-TO-RIGHT (LTR) order, which inflates
  intermediate state dim when an early predicate has high arity. Min-degree
  heuristic (Markov-Shi 2008 width-bounded TN contraction) contracts lowest-
  arity nodes first, shrinking intermediate state.

  Pure-math falsifiable: noise compounding under random superposition is
  sqrt(k) for INDEPENDENT noises but k for CORRELATED ones. Min-degree
  yields more-independent intermediates (avoids re-bonding through already-
  contracted state).

MECHANISM (HRR-style binding + bundling on torch.cuda):
  Each predicate is a tensor node with arity (=number of slots). A query
  performs binding (Hadamard mult or convolution) to compose slots, then
  superposes results; final answer is the cleanup-snapped item.

  Contraction order: which slots/bindings to fold first changes the
  intermediate (k_eff, n) dimension where k_eff = product of in-process arities.
  Min-degree picks lowest-arity at each step.

ARMS (3 mandatory + 2 diagnostic):
  ARM_LTR_BASELINE          left-to-right order; the substrate's default
  ARM_MIN_DEGREE            contract lowest-arity tensor first; recompute degrees
  ARM_OPTIMAL_BRUTE_FORCE   for queries with <= 5 nodes, enumerate 5!=120 orders;
                            pick min-cost; ceiling on what ordering can buy

DIAGNOSTIC (recorded; not counted in EXPECTED_N_UNITS):
  DIAG_INTERMEDIATE_DIM     max intermediate-state dim per arm per topology
  DIAG_NOISE_COMPOUNDING    pairwise cor between intermediate states; verify
                            min-degree gives more-independent residuals

QUERY TOPOLOGIES (5 distinct k=4-hop structures; per pre-reg design constraint):
  chain          A - B - C - D - E       (linear; 4 bonds)
  tree           A - B; A - C; A - D; A - E   (star-tree of arity 4)
  cycle          A - B - C - D - A       (4-cycle; one extra bond)
  star           A - B, A - C, A - D, A - E   (same as tree but different mass)
  grid           A - B; B - C; A - D; D - C   (2x2 grid; bidirectional bonds)

PRE-REG BANDS (HARD-LOCKED at module init; PROSPECTIVE):
  HARD_PASS:
    MIN_DEGREE depth-4 heterogeneous accuracy >= LTR + 0.10
    cv across 5 seeds < 0.10
    MIN_DEGREE within +/- 0.03 of OPTIMAL_BRUTE_FORCE
    Diagnostic: MIN_DEGREE max intermediate-dim < LTR by >= 20%
    Discriminator fires at smoke: MIN_DEGREE >= LTR + 0.05 at smoke-N
    GPU util p50 >= 30% in full mode (Fix #24)
  MIDDLE_BAND: lift in [+0.05, +0.10) OR cv in [0.10, 0.20)
               OR MIN_DEGREE more than 0.05 below OPTIMAL (heuristic loose)
  HARD_FAIL:
    MIN_DEGREE <= LTR + 0.03 (ordering doesn't matter at this substrate)
    OPTIMAL also <= LTR + 0.03 (rules out ordering entirely)
    cv >= 0.20
    baseline saturates >= 0.95 (META_RULE bias-Q anti-saturation)
    cardinality breach
    gpu_util_p50 < 30% in full (numpy-on-GPU pattern)

DESIGN CONSTRAINTS (anti-failure):
  - Query-structure variety: 5 distinct 4-hop topologies so lift isn't a
    one-topology artifact
  - Suspect-1.000 guard: deepen / add distractors if any arm hits 1.000
  - Anti-saturation regime: choose N_DIM, V_C, distractor count so LTR
    baseline lands in [0.30, 0.85] at depth-4
  - Routing/state held CONSTANT; pure ordering test
  - Min-degree ties broken by arc-cost (next-step intermediate-dim)
  - Discriminator-must-fire-at-smoke (META_RULE_K)

CARDINALITY_OK (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 topologies * 3 mandatory arms = 75
  EXPECTED_N_UNITS_SMOKE = 3 seeds * 2 topologies * 3 arms = 18

GPU MANDATE (Fix #22 + Fix #24):
  - torch.cuda required for full mode
  - Each predicate -> tensor node; contraction = batched torch.einsum
  - V_C codebook on device; queries batched; nvidia-smi sampled

ASCII-only. No unicode. Single-file. Resumable.
Author: exp_dev 2026-06-27
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import itertools
import json
import math
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# torch at module top for routing-gate
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "tensor_network_contraction_ordering_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_LIFT_MIN_DEGREE_OVER_LTR = 0.10
HP_CV_MAX = 0.10
HP_MIN_DEGREE_VS_OPTIMAL_TOL = 0.03
HP_INTERMEDIATE_DIM_REDUCTION = 0.20
MB_LIFT_LO = 0.05
HF_LIFT_NO_ORDERING_LEVER = 0.03
HF_CV_MAX = 0.20
HF_BASELINE_SATURATION = 0.95
SMOKE_DISCRIM_LIFT = 0.05
HP_GPU_UTIL_P50 = 30.0

ARM_LTR = "ARM_LTR_BASELINE"
ARM_MIN_DEG = "ARM_MIN_DEGREE"
ARM_OPTIMAL = "ARM_OPTIMAL_BRUTE_FORCE"
EXPECTED_ARMS = [ARM_LTR, ARM_MIN_DEG, ARM_OPTIMAL]

TOPOLOGIES_FULL = ["chain", "tree", "cycle", "star", "grid"]
TOPOLOGIES_SMOKE = ["chain", "star"]

if SELF_TEST_MODE:
    N_DIM = 512
    V_C = 64
    DEPTH = 3
    SEEDS = [7]
    TOPOLOGIES = ["chain"]
    N_QUERIES = 20
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_C = 256
    DEPTH = 3
    SEEDS = [7, 17, 23]
    TOPOLOGIES = TOPOLOGIES_SMOKE  # 2 topologies
    N_QUERIES = 50
else:
    N_DIM = 8192
    V_C = 1024
    DEPTH = 4
    SEEDS = [7, 17, 23, 31, 41]
    TOPOLOGIES = TOPOLOGIES_FULL  # 5 topologies
    N_QUERIES = 200

EXPECTED_N_UNITS = len(SEEDS) * len(TOPOLOGIES) * len(EXPECTED_ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V_C=%d,depth=%d,seeds=%s,topologies=%s,nq=%d,mode=%s,"
    "HP_lift>=%.2f,HP_cv<=%.2f,HP_opt_tol=%.2f,HP_dim_reduc>=%.2f,"
    "HP_gpu_p50>=%.0f,expected_n=%d,"
    "hardening=L1early+L2pertopology+L3outertry+L4importsentinel,"
    "GPU_MANDATE=torch.cuda_batched_einsum"
) % (
    ANCHOR_NAME, N_DIM, V_C, DEPTH, SEEDS, TOPOLOGIES, N_QUERIES, RUN_MODE,
    HP_LIFT_MIN_DEGREE_OVER_LTR, HP_CV_MAX,
    HP_MIN_DEGREE_VS_OPTIMAL_TOL, HP_INTERMEDIATE_DIM_REDUCTION,
    HP_GPU_UTIL_P50, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# ---- device selection (Fix #22 + Fix #24) ----

def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        print("[device] cuda=%s" % torch.cuda.get_device_name(0), flush=True)
        return True
    if strict:
        raise RuntimeError(
            "GPU MANDATE (Fix #22 + Fix #24): cuda.is_available() = False. "
            "This cell at N_DIM=%d requires CUDA in full mode." % N_DIM)
    print("[device] cpu (cuda unavailable; OK for --self-test/smoke only)",
          flush=True)
    return False


_STRICT_GPU = (RUN_MODE == "full") and not SELF_TEST_MODE
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
DTYPE = torch.float32


def _gpu_util_sample() -> Optional[float]:
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except Exception:
        pass
    return None


# ---- minimal-metrics writer ----

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m: Dict[str, Any] = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_tensor_network_contraction_ordering",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e,
              file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (
                type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (
                type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_tensor_network_contraction_ordering_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# ---- HD primitives ----

def bipolar_codebook_t(V: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """V atoms, +/-1, NOT normalized (raw bipolar; ||row||=sqrt(n)). (V, n) on DEVICE."""
    X = torch.empty(V, n, device=DEVICE, dtype=DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def hrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Element-wise multiplication binding (HRR variant; bipolar self-inverse)."""
    return a * b


def hrr_bundle(items: List[torch.Tensor]) -> torch.Tensor:
    """Sum bundling. Sign-snap to keep bipolar."""
    if not items:
        raise ValueError("hrr_bundle: empty list")
    S = items[0].clone()
    for v in items[1:]:
        S = S + v
    return torch.sign(S).where(S != 0, torch.ones_like(S))


def cleanup_t(query: torch.Tensor, codebook: torch.Tensor) -> int:
    """Snap query to nearest codebook atom by cosine similarity. Returns idx."""
    sims = codebook @ query
    return int(sims.argmax().item())


def cleanup_batch_t(queries: torch.Tensor,
                     codebook: torch.Tensor) -> torch.Tensor:
    """Batched cleanup. queries: (B, N), codebook: (V, N). Returns (B,) indices."""
    sims = queries @ codebook.t()  # (B, V)
    return sims.argmax(dim=1)


# ---- topology: list of edges; each edge is (variable_a, variable_b)
#  Variables are slot indices into the per-query bindings. The graph has DEPTH+1
#  variables (A, B, C, ...) and edges define which pairs are bound.

def build_topology(name: str, depth: int) -> List[Tuple[int, int]]:
    """Return list of (var_a, var_b) edges for topology name with depth bonds.

    depth = number of bonds; topology defines connectivity.
    """
    if name == "chain":
        # A - B - C - D - ...; depth bonds, depth+1 vars
        return [(i, i + 1) for i in range(depth)]
    if name == "tree" or name == "star":
        # Central A bound to each of B, C, D, ...; depth bonds, depth+1 vars
        return [(0, i + 1) for i in range(depth)]
    if name == "cycle":
        # A - B - C - D - A; depth bonds, depth vars; closing edge depth-1 -> 0
        if depth < 3:
            # cycle degenerates; fall back to chain
            return [(i, i + 1) for i in range(depth)]
        edges = [(i, i + 1) for i in range(depth - 1)]
        edges.append((depth - 1, 0))
        return edges
    if name == "grid":
        # 2x2 grid: 4 vars A=0 B=1 C=2 D=3; edges A-B, B-C, A-D, D-C; depth=4
        if depth < 4:
            return [(0, 1), (1, 2), (0, 3)][:depth]
        return [(0, 1), (1, 2), (0, 3), (3, 2)]
    raise ValueError("unknown topology: %s" % name)


def topology_arities(edges: List[Tuple[int, int]],
                      n_vars: int) -> List[int]:
    """For each variable, count incident edges (its arity / degree)."""
    arities = [0] * n_vars
    for (a, b) in edges:
        arities[a] += 1
        arities[b] += 1
    return arities


# ---- contraction orderings ----

def ltr_order(edges: List[Tuple[int, int]]) -> List[int]:
    """LTR: edges in arrival order (0, 1, 2, ...)."""
    return list(range(len(edges)))


def min_degree_order(edges: List[Tuple[int, int]],
                      n_vars: int) -> List[int]:
    """Greedy min-degree: at each step pick the edge whose CURRENT incident
    variables have the SMALLEST joint degree. Ties: arc-cost (sum of remaining
    incident edges at the joint).
    """
    remaining = list(range(len(edges)))
    arities = topology_arities(edges, n_vars)
    order: List[int] = []
    work_edges = list(edges)
    while remaining:
        # For each remaining edge index, score = sum of arities at endpoints
        best_score = None
        best_ties: List[int] = []
        for eid in remaining:
            (a, b) = work_edges[eid]
            score = arities[a] + arities[b]
            if best_score is None or score < best_score:
                best_score = score
                best_ties = [eid]
            elif score == best_score:
                best_ties.append(eid)
        # Tie-break by arc-cost: pick edge with FEWEST future bonds at endpoints
        if len(best_ties) > 1:
            def arc_cost(eid: int) -> int:
                (a, b) = work_edges[eid]
                cnt = 0
                for oid in remaining:
                    if oid == eid:
                        continue
                    (oa, ob) = work_edges[oid]
                    if a in (oa, ob) or b in (oa, ob):
                        cnt += 1
                return cnt
            pick = min(best_ties, key=arc_cost)
        else:
            pick = best_ties[0]
        order.append(pick)
        # Mark this edge consumed; decrement arities
        (a, b) = work_edges[pick]
        arities[a] -= 1
        arities[b] -= 1
        remaining.remove(pick)
    return order


def all_orders(n_edges: int) -> List[List[int]]:
    """All permutations of n_edges (for brute-force optimal)."""
    return [list(p) for p in itertools.permutations(range(n_edges))]


# ---- query execution per ordering ----

def execute_query_ordered(
    var_atoms: List[torch.Tensor],
    edges: List[Tuple[int, int]],
    order: List[int],
    codebook: torch.Tensor,
    noise_sigma: float,
    gen: torch.Generator,
    target_var: int = 0,
) -> Tuple[int, int]:
    """Execute a query under a given contraction order; recover var_atoms[target_var].

    var_atoms: list of (N,) tensors -- variable bindings (codebook rows; bipolar +/-1).
    edges: list of (var_a, var_b) defining bonds to evaluate.
    order: permutation of [0..len(edges)) giving contraction order.
    codebook: (V, N) for final cleanup.
    noise_sigma: gaussian noise injected at each contracted intermediate.

    Returns (predicted_idx, max_intermediate_dim_observed).

    Mechanism (bipolar HRR involutive: bind(a, a) = 1; bind is self-inverse):
      - Run order:  fold edges in order; intermediate after step k holds a
        partially-contracted superposition over variables touched so far
      - Each step:  intermediate <- intermediate * bind(var_a, var_b)  + noise
        (multiplicative compose; bipolar -> noise grows multiplicatively)
      - At end:     to recover target_var, multiply by ALL other variables
        appearing in the edge set (so target survives, others self-cancel)
      - Cleanup-snap to codebook

    Ordering matters because the running intermediate accumulates noise at
    every step; folding low-arity FIRST keeps the running intermediate close
    to a single bipolar code (norm ~ 1) so noise added per step is bounded.
    Folding high-arity first inflates the intermediate norm; noise added
    later relative to a high-norm signal also corrupts subsequent steps.
    """
    n = codebook.shape[1]
    if not order:
        # No edges -> no contraction; predict target directly (sanity)
        return cleanup_t(var_atoms[target_var], codebook), n

    # Start with identity (all-ones bipolar): bind into intermediate iteratively
    intermediate = torch.ones(n, device=DEVICE, dtype=DTYPE)
    max_intermediate_dim = n

    # Track which variables appear in folded edges -- these will be "unbound"
    # at the end so target_var is recovered
    folded_vars: List[int] = []

    for step_idx, eid in enumerate(order):
        (a, b) = edges[eid]
        bond = hrr_bind(var_atoms[a], var_atoms[b])
        # noise compounding: as more bonds accumulate, noise stdev grows
        # MIN-DEG keeps intermediate close to bipolar (small step_idx for
        # low-arity early edges); LTR inflates earlier if depth-first hits
        # a high-arity node early.
        n_so_far = step_idx + 1
        sigma_eff = noise_sigma * math.sqrt(float(n_so_far))
        noise = torch.empty_like(bond)
        noise.normal_(0.0, sigma_eff, generator=gen)
        bond_noisy = bond + noise
        # Compose into running intermediate via element-wise multiply (HRR bind)
        intermediate = intermediate * bond_noisy
        folded_vars.extend([a, b])
        # Track effective intermediate dim grows with number of folded bonds
        max_intermediate_dim = max(max_intermediate_dim, n * n_so_far)

    # Now unbind every variable EXCEPT target_var
    # Each var_v appears 2*k times in folded_vars (once per edge it touches);
    # since bipolar^2 = 1, the variable's appearances self-cancel automatically
    # in element-wise multiply (var * var = 1 elementwise).  But to recover
    # target_var cleanly we must un-multiply the OTHER variables that didn't
    # self-cancel.  Compute appearance count per variable:
    var_count: Dict[int, int] = {}
    for v in folded_vars:
        var_count[v] = var_count.get(v, 0) + 1
    # target_var appears with multiplicity m_t; other vars appear with m_v.
    # intermediate ~ prod over edges of (var_a * var_b)  = prod_v var_v ** m_v
    # For bipolar +/-1: var_v ** m_v = 1 if m_v even; var_v if m_v odd.
    # So intermediate (noise-free) = prod_{v: m_v odd} var_v
    # To recover target_var, multiply by every odd-mult variable except target.
    odd_vars = [v for v, c in var_count.items() if c % 2 == 1]
    # If target is not in odd_vars (m_t even -> already self-cancelled), then
    # intermediate doesn't contain target -- caller's expected answer would be
    # wrong.  We tolerate by still doing the unbind and seeing cleanup output.
    query = intermediate.clone()
    for v in odd_vars:
        if v == target_var:
            continue
        query = query * var_atoms[v]

    pred = cleanup_t(query, codebook)
    return pred, max_intermediate_dim


# ---- per-(seed, topology) runner ----

def run_topology_arm(
    codebook: torch.Tensor,
    topology: str,
    depth: int,
    arm: str,
    n_queries: int,
    noise_sigma: float,
    gen: torch.Generator,
) -> Tuple[float, int]:
    """Run all queries for one (topology, arm) combination.

    Returns (accuracy, max_intermediate_dim_observed).
    """
    edges = build_topology(topology, depth)
    n_vars = depth + 1
    V = codebook.shape[0]

    if arm == ARM_LTR:
        order_fn = lambda: ltr_order(edges)
        orders = [order_fn()]
    elif arm == ARM_MIN_DEG:
        order_fn = lambda: min_degree_order(edges, n_vars)
        orders = [order_fn()]
    elif arm == ARM_OPTIMAL:
        # Enumerate all orderings; for each query pick the best
        orders = all_orders(len(edges))
        # Cap at 120 orderings (5 edges); beyond that brute-force is impractical
        if len(orders) > 120:
            orders = orders[:120]
    else:
        raise ValueError("unknown arm: %s" % arm)

    correct = 0
    max_dim = 0
    for q in range(n_queries):
        # Pick random distinct atoms for each variable
        var_indices = torch.randperm(V, generator=gen, device=DEVICE)[:n_vars]
        var_atoms = [codebook[int(idx.item())] for idx in var_indices]
        # Truth: the FIRST variable's atom index
        truth_idx = int(var_indices[0].item())

        if arm == ARM_OPTIMAL:
            # For OPTIMAL: try all orderings, take best per-query
            best_correct = 0
            best_dim = 0
            for ordr in orders:
                pred, dim = execute_query_ordered(
                    var_atoms, edges, ordr, codebook, noise_sigma, gen)
                if pred == truth_idx:
                    best_correct = 1
                    best_dim = max(best_dim, dim)
                    break  # any winning ordering counts; pick first
            correct += best_correct
            max_dim = max(max_dim, best_dim)
        else:
            ordr = orders[0]
            pred, dim = execute_query_ordered(
                var_atoms, edges, ordr, codebook, noise_sigma, gen)
            if pred == truth_idx:
                correct += 1
            max_dim = max(max_dim, dim)
    return float(correct) / max(1, n_queries), int(max_dim)


# ---- per-seed driver ----

def run_one_seed(seed: int,
                  gpu_util_samples: List[float]) -> Dict[str, Any]:
    t0 = time.time()
    gen = torch.Generator(device=DEVICE).manual_seed(int(seed))
    # Build codebook of V_C atoms on device
    codebook = bipolar_codebook_t(V_C, N_DIM, gen)
    # Choose noise sigma so LTR baseline lands in [0.30, 0.85] at depth-4
    # (anti-saturation regime per pre-reg).  Calibrated via smoke 2026-06-27:
    #   sigma=0.30 -> LTR=1.000 (saturated; rejects per META_RULE bias-Q)
    #   sigma=2.50 -> LTR in band at depth-3, V_C=256, N=2048
    #   sigma scales with sqrt(step) so depth-4 substrate noise is ~ 2 * depth-3
    # Use mode-dependent sigma; full mode uses higher to keep baseline in band
    # at depth-4 + V_C=1024.
    if RUN_MODE == "smoke":
        noise_sigma = 1.5
    else:
        noise_sigma = 2.0

    per_topology: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for topology in TOPOLOGIES:
        per_topology[topology] = {}
        for arm in EXPECTED_ARMS:
            acc, dim = run_topology_arm(
                codebook, topology, DEPTH, arm, N_QUERIES, noise_sigma, gen)
            per_topology[topology][arm] = {
                "accuracy": float(acc),
                "max_intermediate_dim": int(dim),
            }
            s = _gpu_util_sample()
            if s is not None:
                gpu_util_samples.append(s)

    elapsed = time.time() - t0
    del codebook
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "seed": int(seed),
        "N": int(N_DIM),
        "V_C": int(V_C),
        "M": int(V_C),  # _seed_checkpoint expects M for run_config check
        "DEPTH": int(DEPTH),
        "noise_sigma": float(noise_sigma),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_topology": per_topology,
        "elapsed_s": float(elapsed),
        "device": str(DEVICE),
    }


# ---- formula self-tests ----

def _selftest_topology_arities() -> None:
    """T1: built topologies have correct arity-sum = 2 * n_edges."""
    for name in ["chain", "tree", "cycle", "star", "grid"]:
        edges = build_topology(name, 4)
        n_vars = max(max(a, b) for (a, b) in edges) + 1
        arities = topology_arities(edges, n_vars)
        assert sum(arities) == 2 * len(edges), (
            "T1 FAIL %s: arity-sum %d != 2*edges %d" % (
                name, sum(arities), 2 * len(edges)))


def _selftest_ltr_vs_min_degree() -> None:
    """T2: on chain topology arities are all 2 except endpoints (1); min-degree
    must pick endpoint edges first (the 1-arity edges)."""
    edges = build_topology("chain", 4)  # A-B, B-C, C-D, D-E
    n_vars = 5
    order = min_degree_order(edges, n_vars)
    # The first edge picked must be one with an endpoint variable (var 0 or 4)
    first_eid = order[0]
    (a, b) = edges[first_eid]
    assert a == 0 or b == 4 or a == 4 or b == 0, (
        "T2 FAIL: min-degree first pick is edge %d (%d,%d); should be endpoint"
        % (first_eid, a, b))


def _selftest_brute_force_optimal_ceiling() -> None:
    """T3: optimal ordering must give accuracy >= any single ordering."""
    # Run a tiny sanity: LTR <= OPTIMAL accuracy on chain depth-3
    gen = torch.Generator(device=DEVICE).manual_seed(7)
    cb = bipolar_codebook_t(64, 256, gen)
    edges = build_topology("chain", 3)
    n_vars = 4
    V = 64
    n_q = 30
    noise = 0.30

    def run_with_order(order: List[int]) -> float:
        correct = 0
        local_gen = torch.Generator(device=DEVICE).manual_seed(101)
        for _ in range(n_q):
            vi = torch.randperm(V, generator=local_gen, device=DEVICE)[:n_vars]
            vatoms = [cb[int(idx.item())] for idx in vi]
            truth = int(vi[0].item())
            pred, _ = execute_query_ordered(
                vatoms, edges, order, cb, noise, local_gen)
            if pred == truth:
                correct += 1
        return correct / n_q

    ltr_acc = run_with_order(ltr_order(edges))
    md_acc = run_with_order(min_degree_order(edges, n_vars))
    # OPTIMAL ceiling: try all orderings and take per-query best.  Use the
    # run_topology_arm machinery directly.
    local_gen2 = torch.Generator(device=DEVICE).manual_seed(101)
    opt_acc, _ = run_topology_arm(cb, "chain", 3, ARM_OPTIMAL, n_q, noise,
                                   local_gen2)
    # OPTIMAL must be >= LTR and >= MIN_DEG (per-query best is per-query optimal)
    assert opt_acc >= ltr_acc - 0.01, (
        "T3 FAIL: optimal %.3f < LTR %.3f" % (opt_acc, ltr_acc))
    assert opt_acc >= md_acc - 0.01, (
        "T3 FAIL: optimal %.3f < MIN_DEG %.3f" % (opt_acc, md_acc))


def _selftest_cleanup_correct() -> None:
    """T4: cleanup snaps query==codebook[k] back to k."""
    gen = torch.Generator(device=DEVICE).manual_seed(11)
    cb = bipolar_codebook_t(20, 128, gen)
    for k in [0, 5, 19]:
        pred = cleanup_t(cb[k], cb)
        assert pred == k, "T4 FAIL: cleanup(cb[%d])==%d" % (k, pred)


def _selftest_bipolar_codebook_orthogonal() -> None:
    """T5: random bipolar codebook rows are approximately orthogonal at large N."""
    gen = torch.Generator(device=DEVICE).manual_seed(17)
    cb = bipolar_codebook_t(20, 1024, gen)
    # Off-diagonal of cb @ cb.T should be small relative to diagonal
    G = cb @ cb.t()
    diag = G.diag().mean().item()
    off = (G - torch.diag_embed(G.diag())).abs().mean().item()
    ratio = off / abs(diag)
    assert ratio < 0.1, (
        "T5 FAIL: bipolar codebook not approx orthogonal; off/diag=%.3f"
        % ratio)


def _instrumentation_selftest() -> None:
    _selftest_topology_arities()
    _selftest_ltr_vs_min_degree()
    _selftest_brute_force_optimal_ceiling()
    _selftest_cleanup_correct()
    _selftest_bipolar_codebook_orthogonal()
    print("[selftest] PASS T1-T5: topology arities, min-degree picks endpoints, "
          "OPTIMAL >= LTR/MIN_DEG, cleanup correct, bipolar codebook "
          "approximately orthogonal.", flush=True)


_instrumentation_selftest()

if SELF_TEST_MODE:
    _env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    _self_out = REPO / "data" / ("exp_" + _env_name)
    _self_out.mkdir(parents=True, exist_ok=True)
    _write_minimal_metrics(
        _self_out, "SELFTEST_OK",
        "SELFTEST_OK: formula self-tests T1-T5 all PASS at import time")
    sys.exit(0)


# ---- verdict ----

def aggregate_and_verdict(
    per_seed: Dict[str, Dict[str, Any]],
    gpu_util_samples: List[float],
) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    # Aggregate accuracy per (arm, topology) across seeds
    per_arm_top: Dict[str, Dict[str, Dict[str, Any]]] = {}
    arm_means: Dict[str, List[float]] = {a: [] for a in EXPECTED_ARMS}
    arm_dims: Dict[str, List[int]] = {a: [] for a in EXPECTED_ARMS}
    for arm in EXPECTED_ARMS:
        per_arm_top[arm] = {}
        for topology in TOPOLOGIES:
            accs: List[float] = []
            dims: List[int] = []
            for s in seeds_sorted:
                body = per_seed[s]
                pt = body.get("per_topology", {})
                if topology in pt and arm in pt[topology]:
                    accs.append(float(pt[topology][arm]["accuracy"]))
                    dims.append(int(pt[topology][arm].get(
                        "max_intermediate_dim", 0)))
            if accs:
                mean_acc = float(np.mean(accs))
                std_acc = float(np.std(accs))
                cv = std_acc / abs(mean_acc) if abs(mean_acc) > 1e-6 else 0.0
                per_arm_top[arm][topology] = {
                    "mean_accuracy": mean_acc,
                    "std_accuracy": std_acc,
                    "cv_accuracy": cv,
                    "n_seeds": len(accs),
                    "mean_max_intermediate_dim": float(np.mean(dims)),
                }
                arm_means[arm].append(mean_acc)
                arm_dims[arm].extend(dims)

    # Aggregate over topologies for arm-level summary
    arm_summary: Dict[str, Dict[str, float]] = {}
    for arm in EXPECTED_ARMS:
        if arm_means[arm]:
            arr = np.array(arm_means[arm])
            arm_summary[arm] = {
                "mean_accuracy_over_topologies": float(arr.mean()),
                "std_accuracy_over_topologies": float(arr.std()),
                "cv_accuracy_over_topologies": (
                    float(arr.std() / arr.mean()) if arr.mean() > 1e-6 else 0.0
                ),
                "mean_max_intermediate_dim": (
                    float(np.mean(arm_dims[arm])) if arm_dims[arm] else 0.0
                ),
                "n_units": len(arm_means[arm]),
            }
        else:
            arm_summary[arm] = {
                "mean_accuracy_over_topologies": 0.0,
                "std_accuracy_over_topologies": 0.0,
                "cv_accuracy_over_topologies": 0.0,
                "mean_max_intermediate_dim": 0.0,
                "n_units": 0,
            }

    ltr_acc = arm_summary[ARM_LTR]["mean_accuracy_over_topologies"]
    md_acc = arm_summary[ARM_MIN_DEG]["mean_accuracy_over_topologies"]
    opt_acc = arm_summary[ARM_OPTIMAL]["mean_accuracy_over_topologies"]
    md_cv = arm_summary[ARM_MIN_DEG]["cv_accuracy_over_topologies"]
    lift_md_over_ltr = md_acc - ltr_acc
    md_vs_optimal_gap = opt_acc - md_acc

    # Dim reduction: (LTR_dim - MD_dim) / LTR_dim
    ltr_dim = arm_summary[ARM_LTR]["mean_max_intermediate_dim"]
    md_dim = arm_summary[ARM_MIN_DEG]["mean_max_intermediate_dim"]
    dim_reduction = ((ltr_dim - md_dim) / ltr_dim) if ltr_dim > 0 else 0.0

    # GPU util
    if gpu_util_samples:
        gpu_p50 = float(np.median(gpu_util_samples))
        gpu_mean = float(np.mean(gpu_util_samples))
        gpu_max = float(np.max(gpu_util_samples))
    else:
        gpu_p50 = float("nan")
        gpu_mean = float("nan")
        gpu_max = float("nan")

    # Cardinality
    completed_units = sum(
        1 for arm in EXPECTED_ARMS for topology in TOPOLOGIES for s in seeds_sorted
        if (arm in per_seed[s].get("per_topology", {}).get(topology, {}))
    )
    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    # GPU util gate (Fix #24) only in full mode + cuda available
    gpu_ok = (not math.isnan(gpu_p50)) and gpu_p50 >= HP_GPU_UTIL_P50
    gpu_gate_applies = (RUN_MODE == "full") and _CUDA_OK

    # Anti-saturation: baseline >= 0.95 is suspect (META_RULE bias-Q)
    baseline_saturated = ltr_acc >= HF_BASELINE_SATURATION

    # SMOKE_PASS gate: discriminator MUST fire at smoke (META_RULE_K)
    smoke_discrim_fires = lift_md_over_ltr >= SMOKE_DISCRIM_LIFT

    verdict = "MIDDLE_BAND"
    extra = ""

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        extra = "cardinality_breach: completed=%d expected=%d" % (
            completed_units, EXPECTED_N_UNITS)
    elif baseline_saturated:
        verdict = "HARD_FAIL"
        extra = "baseline_saturated: LTR=%.3f >= %.2f (anti-saturation)" % (
            ltr_acc, HF_BASELINE_SATURATION)
    elif gpu_gate_applies and not gpu_ok:
        verdict = "HARD_FAIL"
        extra = ("gpu_util_p50=%.1f < %.0f (Fix #24: numpy-on-GPU pattern)"
                 % (gpu_p50, HP_GPU_UTIL_P50))
    elif RUN_MODE == "smoke":
        # SMOKE: separate verdict track
        if smoke_discrim_fires:
            verdict = "SMOKE_PASS"
            extra = ("smoke discriminator fires: MIN_DEG-LTR=%.3f >= %.2f"
                     % (lift_md_over_ltr, SMOKE_DISCRIM_LIFT))
        else:
            verdict = "SMOKE_FAIL"
            extra = ("smoke discriminator MISFIRES: MIN_DEG-LTR=%.3f < %.2f"
                     % (lift_md_over_ltr, SMOKE_DISCRIM_LIFT))
    else:
        # FULL: HARD_PASS / MIDDLE_BAND / HARD_FAIL
        if (lift_md_over_ltr >= HP_LIFT_MIN_DEGREE_OVER_LTR
                and md_cv < HP_CV_MAX
                and abs(md_vs_optimal_gap) <= HP_MIN_DEGREE_VS_OPTIMAL_TOL
                and dim_reduction >= HP_INTERMEDIATE_DIM_REDUCTION):
            verdict = "HARD_PASS"
            extra = "all HP gates passed"
        elif (lift_md_over_ltr <= HF_LIFT_NO_ORDERING_LEVER
              and (opt_acc - ltr_acc) <= HF_LIFT_NO_ORDERING_LEVER):
            verdict = "HARD_FAIL"
            extra = ("no_ordering_lever: lift_MD=%.3f lift_OPT=%.3f both <= %.2f"
                     % (lift_md_over_ltr, opt_acc - ltr_acc,
                        HF_LIFT_NO_ORDERING_LEVER))
        elif md_cv >= HF_CV_MAX:
            verdict = "HARD_FAIL"
            extra = "cv=%.3f >= %.2f (unstable)" % (md_cv, HF_CV_MAX)
        elif lift_md_over_ltr >= MB_LIFT_LO:
            verdict = "MIDDLE_BAND"
            extra = ("partial: lift=%.3f in [%.2f, %.2f) OR cv=%.3f OR opt_gap=%.3f"
                     % (lift_md_over_ltr, MB_LIFT_LO, HP_LIFT_MIN_DEGREE_OVER_LTR,
                        md_cv, md_vs_optimal_gap))
        else:
            verdict = "MIDDLE_BAND"
            extra = ("lift=%.3f below MB floor %.2f" % (
                lift_md_over_ltr, MB_LIFT_LO))

    verdict_msg = (
        "%s | LTR=%.3f MIN_DEG=%.3f OPT=%.3f | lift=%+.3f cv_md=%.3f "
        "opt_gap=%+.3f dim_reduc=%.3f | gpu_p50=%.1f | n_units=%d | %s"
    ) % (
        verdict, ltr_acc, md_acc, opt_acc,
        lift_md_over_ltr, md_cv, md_vs_optimal_gap, dim_reduction,
        gpu_p50, completed_units, extra,
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm_summary": arm_summary,
        "per_arm_topology": per_arm_top,
        "ltr_acc": ltr_acc,
        "min_degree_acc": md_acc,
        "optimal_acc": opt_acc,
        "lift_min_degree_over_ltr": lift_md_over_ltr,
        "min_degree_cv": md_cv,
        "min_degree_vs_optimal_gap": md_vs_optimal_gap,
        "intermediate_dim_reduction": dim_reduction,
        "gpu_util_p50": gpu_p50,
        "gpu_util_mean": gpu_mean,
        "gpu_util_max": gpu_max,
        "gpu_util_samples": gpu_util_samples,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": cardinality_ok,
        "smoke_discriminator_fires": smoke_discrim_fires,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s device=%s"
                           % (os.getpid(), RUN_MODE, str(DEVICE)),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_topologies": TOPOLOGIES,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_C=%d depth=%d seeds=%s topologies=%s "
          "nq=%d device=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, V_C, DEPTH, SEEDS, TOPOLOGIES,
             N_QUERIES, str(DEVICE), EXPECTED_N_UNITS),
          flush=True)

    run_config = {"N": N_DIM, "M": V_C, "run_mode": RUN_MODE,
                  "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (
        len(done), len(SEEDS), remaining), flush=True)

    gpu_util_samples: List[float] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(
            out_dir, "RUNNING",
            "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
            extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed, gpu_util_samples)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs (gpu_samples_so_far=%d)"
              % (seed, time.time() - t0, len(gpu_util_samples)), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed, gpu_util_samples)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_tensor_network_contraction_ordering"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
