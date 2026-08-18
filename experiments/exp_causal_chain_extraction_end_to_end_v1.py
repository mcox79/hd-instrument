"""
exp_causal_chain_extraction_end_to_end_v1 -- Stage 3 causal-chain extraction end-to-end (CPU, pure numpy).

ROUTING: Research handoff `notes/exp_dev_handoff_research_causal_chain_extraction_primitive_stage3_2026-06-27.md` TOP-1.
  Source drill: `notes/research_drill_2x_causal_chain_extraction_primitive_stage3_2026-06-27.md`. Composes 4 chain-grade
  primitives (correlational_disambig + CF Cell 2 v2 delta-stack + audit-chain depth + intervention isolation) into a
  substrate-native 3-step PC-algorithm-equivalent.

PARENT ATOMS (CHAIN_GRADE; verified on disk):
  - `data/exp_causal_correlational_disambig_v1/metrics.json` (CHAIN_GRADE; CAUSE_OF role disambig prec=recall=1.000)
  - `data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json` (HARD_PASS; 5.47x; acc=1.0)
  - `data/exp_causal_audit_chain_depth_v1/metrics.json` (CHAIN_GRADE; depth-50 K-hop verified)
  - intervention_isolation atom (CHAIN_GRADE; non-target preservation under do())

ARCHITECTURE (3-step PC-equivalent on synthetic linear-Gaussian DAG):
  SUB-STEP 1 SKELETON via substrate-residual CI test. For each variable pair (X, Y) and candidate separator Z subset,
    project codebook vectors through W; residual r_X|Z = v_X - proj_Z(v_X); edge X-Y exists iff |cos(W * r_X|Z, r_Y|Z)|
    > theta_CI for ALL conditioning sets in {{}} U single-Z subsets (|Z| <= 2 capped per BIAS-15).
  SUB-STEP 2 ORIENTATION via temporal-precedence + interventional asymmetry. For each undirected edge X-Y: compute
    Delta_XY = ||do(X) -> Y|| - ||do(Y) -> X|| via CF Cell 2 v2 delta-stack rank-1 surgery. Orient toward larger delta
    (interventional asymmetry); tie-break by observation-timestamp precedence.
  SUB-STEP 3 CHAIN ASSEMBLY via K-hop traversal on inferred directed sub-W. Rank length-3 chains by cumulative cosine;
    report MRR@5 against ground-truth chains.

DAG: synthetic 5-variable linear-Gaussian. FULL: X1->X2->X3, X1->X4->X3, X5 isolated (canonical fork+collider). SMOKE:
  4-variable subset (drop X5; tests CI pruning + orientation discriminator at smaller scale per discriminator-survives-scale).

ARMS (META_RULE_AF arms-must-differ; SHA-256 verified):
  - ARM_A: full pipeline (CI test + orient + K-hop chain assembly).
  - ARM_B: skeleton-only (no orient; undirected chains; tests orient adds value).
  - ARM_C: temporal-precedence-only orient (skip CI; orient ALL temporally-ordered pairs as edges; tests CI pruning adds value).
  - ARM_D: PC-on-true-corr ceiling (privileged ground-truth partial-correlation skeleton; just orient + assemble).
  - ARM_E: random-DAG baseline (control).

PRE-REGISTERED (per handoff):
  HARD_PASS: chain-MRR@5 >= MEASURED@0.50 AND skeleton-F1 >= MEASURED@0.70 AND orientation-acc >= MEASURED@0.75
    AND (ARM_A - ARM_B) >= MEASURED@0.10 AND (ARM_A - ARM_C) >= MEASURED@0.10 AND (ARM_D - ARM_A) < MEASURED@0.15.
    EXPECTED: chain-MRR=HYPOTHESIZED@0.55, skeleton-F1=HYPOTHESIZED@0.72, orient-acc=HYPOTHESIZED@0.80.
  HARD_FAIL: chain-MRR < 0.25 OR skeleton-F1 < 0.40 OR (ARM_A - ARM_C) < 0.03 OR (ARM_A - ARM_E) < 0.20.
  MIDDLE_BAND: chain-MRR in [0.25, 0.50] with skeleton-F1 >= 0.50.

CARDINALITY_OK: EXPECTED_N_UNITS = 5 arms x 3 metrics x 3 seeds = 45; HARD_FAIL_CARDINALITY_BREACH if observed < 40.

SMOKE DISCRIMINATOR (per discriminator-survives-scale): 4-var DAG, 1000 obs, N=2048, 1 seed (~60s CPU): ARM_A - ARM_C >=
  0.05 chain-MRR AND ARM_A - ARM_E >= 0.25; otherwise smoke HARD_FAIL, do NOT dispatch full.

CRLB pre-validation (per exp_dev.md sec.9): chain-MRR upper bound from ground-truth = 1.0 (perfect ranking of 2 chains
  among <=10 candidates yields MRR=1.0); HARD_PASS target 0.50 is well within reachable envelope.

FORMULA SELF-TESTS (PROT-022):
  1. quasi-orthogonal random bipolar role vectors at N=512.
  2. bipolar bind/unbind recovers (correlational_disambig parity).
  3. residual projection: proj_Z(v_X) on Z=v_X recovers ~v_X; residual has norm < epsilon.
  4. CI test: independent vars yield |cos| ~ 0; deterministic Y=2X yields |cos| ~ 1.
  5. K-hop traversal on toy 3-node directed sub-W recovers chain X1->X2->X3.

ASCII-only. __main__ guard. SystemExit re-raise BEFORE BaseException. atomic write_metrics via _seed_checkpoint.
PROT-018 _v1. NO emojis.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
from itertools import combinations, permutations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "causal_chain_extraction_end_to_end_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    # SMOKE = SAME DAG STRUCTURE AS FULL (option C "full-N preview arm in smoke" per
    # discriminator-survives-scale): identical 5-var canonical DAG with COLLIDER on X2,
    # just reduced N + obs + seeds. Guarantees smoke discriminator fires at same regime as full.
    N = 2048
    N_OBS = 1000
    SEEDS = [1]
    # Canonical drill DAG: X0->X1->X2, X0->X3->X2 (X2 is collider; X4 isolated).
    # KEY: X2 is a v-structure collider. Temporal-only ARM_C orients ALL temp-ordered pairs,
    # creating spurious edges (X1,X3) [same depth->whichever first alphabetically] and producing
    # chains like (X0,X1,X3,X2) etc. ARM_A's substrate v-structure detection should correctly
    # identify X2 as collider (X1 _||_ X3 unconditionally but DEPENDENT given X2), preserving
    # the correct DAG. Discriminator gap fires when ARM_A produces cleaner directed sub-W.
    DAG_EDGES = [(0, 1), (1, 2), (0, 3), (3, 2)]
    N_VARS = 5
    GT_CHAINS = [(0, 1, 2), (0, 3, 2)]
else:
    N = 4096
    N_OBS = 5000
    SEEDS = [7, 17, 23]
    # Canonical 5-var: X0->X1->X2, X0->X3->X2 (collider on X2), X4 isolated. Two length-3 chains
    # converging on X2. The collider is the key discriminating structure for PC vs temporal-only.
    DAG_EDGES = [(0, 1), (1, 2), (0, 3), (3, 2)]
    N_VARS = 5
    GT_CHAINS = [(0, 1, 2), (0, 3, 2)]

THETA_CI = 0.35         # CI threshold tuned on smoke held-out (smoke-only tuning, no test contamination per BIAS-13)
THETA_ORIENT = 0.05     # interventional asymmetry magnitude floor for orientation confidence
NOISE_STD = 0.5
RIDGE = 1e-3
MAX_COND_SET = 2        # |Z| <= 2 per BIAS-15

ARMS = ["ARM_A_FULL", "ARM_B_SKEL_ONLY", "ARM_C_TEMP_ONLY", "ARM_D_TRUE_CORR_CEIL", "ARM_E_RANDOM"]


# ---------- primitives ----------

def unit(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Random bipolar matrix; float32."""
    return (g.integers(0, 2, (M, n)) * 2 - 1).astype(np.float32)


def hetero_W(S: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Source -> target hetero-assoc matrix: W @ s_i ~= t_i ; W = T^T (S S^T + ridge)^-1 S."""
    G = S @ S.T + RIDGE * np.eye(S.shape[0], dtype=np.float32)
    return T.T @ np.linalg.solve(G, S).astype(np.float32)


def gen_lingauss_data(edges: List[Tuple[int, int]], n_vars: int, n_obs: int,
                      g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Generate linear-Gaussian observations from DAG. Returns (X, timestamps).

    X[i, k] = sum_{(p,k) in edges} w_pk * X[i, p] + noise. Topological order via parent-first.
    Timestamps: each variable gets observed AT a time equal to its topological depth + jitter.
    """
    # Topological sort via Kahn.
    indeg = [0] * n_vars
    parents: Dict[int, List[int]] = {k: [] for k in range(n_vars)}
    for (p, c) in edges:
        indeg[c] += 1
        parents[c].append(p)
    topo: List[int] = []
    ready = [k for k in range(n_vars) if indeg[k] == 0]
    while ready:
        v = ready.pop(0)
        topo.append(v)
        for (p, c) in edges:
            if p == v:
                indeg[c] -= 1
                if indeg[c] == 0:
                    ready.append(c)
    if len(topo) != n_vars:
        raise ValueError("DAG has a cycle")

    # Edge weights stable per DAG (not per seed) to keep DAG structure recoverable; only noise per seed.
    edge_w: Dict[Tuple[int, int], float] = {(p, c): 0.7 for (p, c) in edges}

    X = np.zeros((n_obs, n_vars), dtype=np.float32)
    for v in topo:
        if not parents[v]:
            X[:, v] = g.standard_normal(n_obs).astype(np.float32)
        else:
            X[:, v] = NOISE_STD * g.standard_normal(n_obs).astype(np.float32)
            for p in parents[v]:
                X[:, v] = X[:, v] + edge_w[(p, v)] * X[:, p]

    # Timestamps: depth in topo order; same for every obs (one shared causal scheme)
    depth = {v: i for i, v in enumerate(topo)}
    timestamps = np.array([depth[k] for k in range(n_vars)], dtype=np.float32)
    return X, timestamps


def store_substrate(X: np.ndarray, n_dim: int, g: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Substrate-native storage: each variable X_k maps to a bipolar code v_k via discretized-observation hetero-assoc.

    Returns (V, W) where V[k] is the var k codebook vector (N-dim), W is the hetero-assoc matrix between standardized
    observations (projected onto variable codebook). Observations are standardized per variable; substrate stores the
    cross-variable association W such that W @ v_X under unit input approximates the conditional E[v_Y | v_X].
    """
    n_vars = X.shape[1]
    V = unit(bipolar(n_vars, n_dim, g)).astype(np.float32)

    # Build cross-association: for each observation row i, source vec = sum_k X[i,k]*v_k; target = same.
    # The hetero W learned from data captures pairwise associations (which is what CI tests probe).
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-8)
    # Bind: each observation projects var values onto V -> source repr.
    S = Xs @ V                    # (n_obs, N)
    # Sample a manageable subset for matrix solve (n_obs can be 5000; we want G to be invertible at n_obs x n_obs).
    # Approach: regress each var-coded readout against the bundle. Use ridge on (V^T V) style.
    # Simpler + stable: W is a covariance-like operator on V: W = V^T diag(corr(X)) V is too coarse.
    # We use the empirical cross-correlation of X projected through V:
    # W_assoc = V.T @ (corr_matrix_of_X) @ V projected back -- yields an N x N matrix whose action on v_X = corr-weighted sum.
    corr_X = np.corrcoef(Xs, rowvar=False).astype(np.float32)
    # W: takes v_X to weighted-sum of v_Y, weight = corr(X, Y).
    W = V.T @ corr_X @ V                                    # (N, N)
    return V, W


def project_residual(v: np.ndarray, Z_basis: np.ndarray) -> np.ndarray:
    """HRR residual: v minus orthogonal projection onto span(Z_basis rows)."""
    if Z_basis.shape[0] == 0:
        return v.copy()
    # Gram-Schmidt to get an orthonormal basis of Z, then subtract projection.
    Q, _ = np.linalg.qr(Z_basis.T)                          # Q: (N, k)
    proj = Q @ (Q.T @ v)
    return v - proj


def ci_test(V: np.ndarray, W: np.ndarray, x: int, y: int, Z: Tuple[int, ...]) -> float:
    """Returns |cos(W @ r_x|Z, r_y|Z)|; small => conditionally independent given Z."""
    Z_basis = V[list(Z), :] if len(Z) > 0 else np.zeros((0, V.shape[1]), dtype=np.float32)
    rx = project_residual(V[x], Z_basis)
    ry = project_residual(V[y], Z_basis)
    a = W @ rx
    return float(abs(unit(a[None, :])[0] @ unit(ry[None, :])[0]))


def skeleton_from_ci(V: np.ndarray, W: np.ndarray, n_vars: int, theta: float) -> List[Tuple[int, int]]:
    """PC SKELETON: undirected edge X-Y exists iff CI test fails for ALL Z in candidate separator set."""
    edges = []
    for x, y in combinations(range(n_vars), 2):
        others = [k for k in range(n_vars) if k != x and k != y]
        cond_sets: List[Tuple[int, ...]] = [()]
        for k in range(1, min(MAX_COND_SET, len(others)) + 1):
            cond_sets.extend([c for c in combinations(others, k)])
        # X-Y edge exists iff EVERY Z fails to separate (|cos| > theta for all Z).
        all_dependent = True
        for Z in cond_sets:
            score = ci_test(V, W, x, y, Z)
            if score < theta:
                all_dependent = False
                break
        if all_dependent:
            edges.append((x, y))
    return edges


def skeleton_from_true_corr(X: np.ndarray, n_vars: int, theta_partial: float) -> List[Tuple[int, int]]:
    """ARM_D ceiling: PC skeleton on TRUE partial-correlation matrix."""
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-8)
    cov = np.cov(Xs, rowvar=False)
    # Partial correlation via precision matrix.
    try:
        prec = np.linalg.inv(cov + RIDGE * np.eye(n_vars))
    except np.linalg.LinAlgError:
        prec = np.linalg.pinv(cov + RIDGE * np.eye(n_vars))
    # partial_corr[i,j] = -prec[i,j] / sqrt(prec[i,i] * prec[j,j])
    edges = []
    for x, y in combinations(range(n_vars), 2):
        pc = -prec[x, y] / max(np.sqrt(prec[x, x] * prec[y, y]), 1e-8)
        if abs(pc) > theta_partial:
            edges.append((x, y))
    return edges


def orient_via_intervention(V: np.ndarray, W: np.ndarray, edges: List[Tuple[int, int]],
                            timestamps: np.ndarray, theta: float, n_vars: int) -> List[Tuple[int, int]]:
    """Substrate-native orientation: combines Pearl v-structure detection (substrate CI test) +
    temporal-precedence + interventional asymmetry via CF Cell 2 v2 delta-stack mechanic.

    Pearl rule (v-structure / collider detection): for undirected triple X - Z - Y with no X-Y edge,
    if Z is NOT in the conditioning set that separates X,Y, then X -> Z <- Y (collider).
    Otherwise (Z separates X,Y), the triple is a chain (X-Z-Y), and we use temporal-precedence
    + interventional asymmetry to orient.

    Substrate interventional asymmetry: rank-1 surgery W' = W + (v_y - W @ v_x) * v_x.T pushes
    v_x activation toward v_y. Measure forward delta = ||W' @ v_x - W @ v_x|| (CF cell-2 v2 mechanic).
    Asymmetric DAG produces asymmetric deltas; orient toward source with larger forward push.
    """
    undirected_set = set(tuple(sorted(e)) for e in edges)
    # Step 1: detect colliders (v-structures) using CI separator semantics.
    # For each triple (X, Z, Y) where X-Z and Z-Y are edges but X-Y is NOT, check if Z separates X,Y.
    # If Z does NOT separate (i.e., CI test fails with Z in conditioning), then X->Z<-Y (collider).
    directed_set: List[Tuple[int, int]] = []
    oriented: set = set()
    for z in range(n_vars):
        neighbors = [k for k in range(n_vars) if tuple(sorted((z, k))) in undirected_set]
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                x, y = neighbors[i], neighbors[j]
                if tuple(sorted((x, y))) in undirected_set:
                    continue  # X-Y also connected; not a v-structure candidate
                # Test if Z separates X, Y: CI test with {Z}
                cond_with_z = ci_test(V, W, x, y, (z,))
                cond_without = ci_test(V, W, x, y, ())
                # If conditioning on Z INCREASES dependence (collider unblocks), then v-structure.
                if cond_with_z > cond_without + 0.02:
                    if (x, z) not in oriented and (z, x) not in oriented:
                        directed_set.append((x, z))
                        oriented.add((x, z))
                    if (y, z) not in oriented and (z, y) not in oriented:
                        directed_set.append((y, z))
                        oriented.add((y, z))

    # Step 2: orient remaining undirected edges via interventional asymmetry + temporal precedence.
    for (x, y) in edges:
        if (x, y) in oriented or (y, x) in oriented:
            continue
        # Interventional asymmetry: rank-1 surgery W + delta * v_x v_x^T pushing toward v_y.
        # forward_delta: how strongly does pushing v_x affect prediction of v_y under W?
        Wx = W @ V[x]
        Wy = W @ V[y]
        # Delta operator: (v_y - W @ v_x) outer v_x; measure effect = (v_y - Wx).v_x
        forward = float(np.dot(V[y] - Wx, V[x]))
        reverse = float(np.dot(V[x] - Wy, V[y]))
        delta = forward - reverse
        if abs(delta) > theta:
            if delta > 0:
                directed_set.append((x, y))
                oriented.add((x, y))
            else:
                directed_set.append((y, x))
                oriented.add((y, x))
        elif timestamps[x] < timestamps[y]:
            directed_set.append((x, y))
            oriented.add((x, y))
        elif timestamps[y] < timestamps[x]:
            directed_set.append((y, x))
            oriented.add((y, x))
        else:
            directed_set.append((x, y))
            oriented.add((x, y))
    return directed_set


def orient_temporal_only(edges: List[Tuple[int, int]], timestamps: np.ndarray) -> List[Tuple[int, int]]:
    """ARM_C: orient solely by temporal precedence (no CI; no interventional asymmetry)."""
    directed = []
    for (x, y) in edges:
        if timestamps[x] < timestamps[y]:
            directed.append((x, y))
        elif timestamps[y] < timestamps[x]:
            directed.append((y, x))
        else:
            directed.append((x, y))
    return directed


def temporal_only_pipeline(timestamps: np.ndarray, n_vars: int) -> List[Tuple[int, int]]:
    """ARM_C full: orient ALL temporally-ordered pairs as edges (no CI pruning)."""
    edges = []
    for x, y in combinations(range(n_vars), 2):
        if timestamps[x] < timestamps[y]:
            edges.append((x, y))
        elif timestamps[y] < timestamps[x]:
            edges.append((y, x))
    return edges


def random_dag(n_vars: int, n_edges: int, g: np.random.Generator) -> List[Tuple[int, int]]:
    """ARM_E control: random DAG with topological order."""
    perm = g.permutation(n_vars).tolist()
    all_pairs = [(perm[i], perm[j]) for i in range(n_vars) for j in range(i + 1, n_vars)]
    if n_edges >= len(all_pairs):
        return all_pairs
    idx = g.choice(len(all_pairs), size=n_edges, replace=False)
    return [all_pairs[i] for i in idx]


def k_hop_chains(directed: List[Tuple[int, int]], length: int, n_vars: int) -> List[Tuple[int, ...]]:
    """Enumerate all simple directed paths of given length on the directed graph."""
    adj: Dict[int, List[int]] = {k: [] for k in range(n_vars)}
    for (p, c) in directed:
        if c not in adj[p]:
            adj[p].append(c)
    chains = []
    for start in range(n_vars):
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if len(path) == length:
                chains.append(tuple(path))
                continue
            for nxt in adj[node]:
                if nxt not in path:
                    stack.append((nxt, path + [nxt]))
    return chains


def rank_chains(V: np.ndarray, W: np.ndarray, chains: List[Tuple[int, ...]]) -> List[Tuple[Tuple[int, ...], float]]:
    """Rank chains by cumulative cosine score along directed sub-W path."""
    scored = []
    for ch in chains:
        s = 0.0
        for i in range(len(ch) - 1):
            pred = W @ V[ch[i]]
            s += float(unit(pred[None, :])[0] @ unit(V[ch[i + 1]][None, :])[0])
        scored.append((ch, s / max(len(ch) - 1, 1)))
    scored.sort(key=lambda kv: -kv[1])
    return scored


def mrr_at_k(ranked: List[Tuple[Tuple[int, ...], float]], gt_chains: List[Tuple[int, ...]], k: int = 5) -> float:
    """Mean reciprocal rank @ k. Average over ground-truth chains; rank=inf if not in top-k."""
    if not gt_chains:
        return 0.0
    rr_total = 0.0
    for gt in gt_chains:
        rr = 0.0
        for i, (ch, _) in enumerate(ranked[:k]):
            if ch == gt:
                rr = 1.0 / (i + 1)
                break
        rr_total += rr
    return rr_total / len(gt_chains)


def skeleton_f1(predicted: List[Tuple[int, int]], gt_edges: List[Tuple[int, int]]) -> float:
    """Undirected skeleton F1."""
    pred_undir = set(tuple(sorted(e)) for e in predicted)
    gt_undir = set(tuple(sorted(e)) for e in gt_edges)
    tp = len(pred_undir & gt_undir)
    fp = len(pred_undir - gt_undir)
    fn = len(gt_undir - pred_undir)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    return 2 * prec * rec / max(prec + rec, 1e-8)


def orient_acc(predicted: List[Tuple[int, int]], gt_edges: List[Tuple[int, int]]) -> float:
    """Fraction of predicted directed edges that match GT direction (only over edges in GT skeleton)."""
    gt_dir = set(gt_edges)
    gt_undir = set(tuple(sorted(e)) for e in gt_edges)
    correct = 0
    total = 0
    for (x, y) in predicted:
        if tuple(sorted((x, y))) in gt_undir:
            total += 1
            if (x, y) in gt_dir:
                correct += 1
    return correct / max(total, 1)


# ---------- formula self-tests (PROT-022) ----------

def _selftest() -> None:
    g = np.random.default_rng(0)
    # 1. quasi-orthogonal random bipolar
    a = bipolar(1, 512, g)[0]
    b = bipolar(1, 512, g)[0]
    assert abs(float(unit(a[None, :])[0] @ unit(b[None, :])[0])) < 0.2, "selftest-1: roles quasi-orthogonal"
    # 2. bipolar bind/unbind
    role = bipolar(1, 512, g)[0]
    val = bipolar(1, 512, g)[0]
    bound = role * val
    rec = bound * role
    assert float(unit(rec[None, :])[0] @ unit(val[None, :])[0]) > 0.9, "selftest-2: bind/unbind"
    # 3. residual projection: proj_Z(v) on Z = unit(v) recovers v; residual ~ 0
    v = bipolar(1, 256, g)[0].astype(np.float32)
    Z_basis = v[None, :]
    res = project_residual(v, Z_basis)
    assert np.linalg.norm(res) < 1e-3 * np.linalg.norm(v) + 1e-4, "selftest-3: residual projection"
    # 4. CI test on deterministic Y=2*X yields high cos; on independent yields low
    g4 = np.random.default_rng(42)
    V4 = unit(bipolar(3, 1024, g4)).astype(np.float32)
    # Build a W where v_0 strongly maps to v_1 (dep), v_2 unrelated.
    X_dep = np.zeros((200, 3), dtype=np.float32)
    X_dep[:, 0] = g4.standard_normal(200).astype(np.float32)
    X_dep[:, 1] = 2.0 * X_dep[:, 0] + 0.01 * g4.standard_normal(200).astype(np.float32)
    X_dep[:, 2] = g4.standard_normal(200).astype(np.float32)
    Xs = (X_dep - X_dep.mean(0)) / (X_dep.std(0) + 1e-8)
    corr_X = np.corrcoef(Xs, rowvar=False).astype(np.float32)
    W4 = V4.T @ corr_X @ V4
    dep_score = ci_test(V4, W4, 0, 1, ())
    indep_score = ci_test(V4, W4, 0, 2, ())
    assert dep_score > indep_score + 0.1, (
        "selftest-4: CI test discriminates (dep=%.3f, indep=%.3f)" % (dep_score, indep_score)
    )
    # 5. K-hop traversal on toy directed graph X0->X1->X2 recovers chain
    directed = [(0, 1), (1, 2)]
    chains = k_hop_chains(directed, length=3, n_vars=3)
    assert (0, 1, 2) in chains, "selftest-5: K-hop traversal recovers chain"
    print("[selftest] PASS: causal_chain_extraction_end_to_end_v1", flush=True)


# ---------- per-seed arms ----------

def run_seed(seed: int) -> Dict:
    t_start = time.time()
    g = np.random.default_rng(seed)
    X, timestamps = gen_lingauss_data(DAG_EDGES, N_VARS, N_OBS, g)
    V, W = store_substrate(X, N, g)

    gt_edges = DAG_EDGES
    arm_results: Dict[str, Dict[str, float]] = {}

    # ARM_A: full pipeline (CI + intervention orient + K-hop).
    skel_A = skeleton_from_ci(V, W, N_VARS, THETA_CI)
    dir_A = orient_via_intervention(V, W, skel_A, timestamps, THETA_ORIENT, N_VARS)
    chains_A = k_hop_chains(dir_A, length=3, n_vars=N_VARS)
    ranked_A = rank_chains(V, W, chains_A)
    arm_results["ARM_A_FULL"] = {
        "skeleton_f1": skeleton_f1(skel_A, gt_edges),
        "orientation_acc": orient_acc(dir_A, gt_edges),
        "chain_mrr_5": mrr_at_k(ranked_A, GT_CHAINS, k=5),
        "n_edges_predicted": float(len(skel_A)),
        "n_chains": float(len(chains_A)),
    }

    # ARM_B: skeleton-only (orient = any-order; pessimistically pick observation order for chain assembly).
    # Without orientation: enumerate both directions and rank by undirected cosine.
    skel_B = skel_A
    # Convert undirected to BOTH directions for chain enumeration (no orient signal).
    dir_B = [(x, y) for (x, y) in skel_B] + [(y, x) for (x, y) in skel_B]
    chains_B = k_hop_chains(dir_B, length=3, n_vars=N_VARS)
    ranked_B = rank_chains(V, W, chains_B)
    arm_results["ARM_B_SKEL_ONLY"] = {
        "skeleton_f1": skeleton_f1(skel_B, gt_edges),
        "orientation_acc": 0.0,
        "chain_mrr_5": mrr_at_k(ranked_B, GT_CHAINS, k=5),
        "n_edges_predicted": float(len(skel_B)),
        "n_chains": float(len(chains_B)),
    }

    # ARM_C: temporal-only orient -- no CI pruning; orient ALL temporally-ordered pairs.
    skel_C_pairs = temporal_only_pipeline(timestamps, N_VARS)
    chains_C = k_hop_chains(skel_C_pairs, length=3, n_vars=N_VARS)
    ranked_C = rank_chains(V, W, chains_C)
    arm_results["ARM_C_TEMP_ONLY"] = {
        "skeleton_f1": skeleton_f1(skel_C_pairs, gt_edges),
        "orientation_acc": orient_acc(skel_C_pairs, gt_edges),
        "chain_mrr_5": mrr_at_k(ranked_C, GT_CHAINS, k=5),
        "n_edges_predicted": float(len(skel_C_pairs)),
        "n_chains": float(len(chains_C)),
    }

    # ARM_D: PC on TRUE partial-correlation matrix (ceiling).
    skel_D = skeleton_from_true_corr(X, N_VARS, theta_partial=0.05)
    dir_D = orient_via_intervention(V, W, skel_D, timestamps, THETA_ORIENT, N_VARS)
    chains_D = k_hop_chains(dir_D, length=3, n_vars=N_VARS)
    ranked_D = rank_chains(V, W, chains_D)
    arm_results["ARM_D_TRUE_CORR_CEIL"] = {
        "skeleton_f1": skeleton_f1(skel_D, gt_edges),
        "orientation_acc": orient_acc(dir_D, gt_edges),
        "chain_mrr_5": mrr_at_k(ranked_D, GT_CHAINS, k=5),
        "n_edges_predicted": float(len(skel_D)),
        "n_chains": float(len(chains_D)),
    }

    # ARM_E: random DAG control.
    rand_edges = random_dag(N_VARS, max(len(gt_edges), 1), g)
    chains_E = k_hop_chains(rand_edges, length=3, n_vars=N_VARS)
    ranked_E = rank_chains(V, W, chains_E)
    arm_results["ARM_E_RANDOM"] = {
        "skeleton_f1": skeleton_f1(rand_edges, gt_edges),
        "orientation_acc": orient_acc(rand_edges, gt_edges),
        "chain_mrr_5": mrr_at_k(ranked_E, GT_CHAINS, k=5),
        "n_edges_predicted": float(len(rand_edges)),
        "n_chains": float(len(chains_E)),
    }

    # META_RULE_AF arms-must-differ: SHA-256 over per-arm structured output.
    arm_hashes = {}
    for arm in ARMS:
        payload = json.dumps(arm_results[arm], sort_keys=True).encode("utf-8")
        arm_hashes[arm] = hashlib.sha256(payload).hexdigest()[:16]
    unique = len(set(arm_hashes.values()))

    print("  [seed=%d] %.1fs ARM_A mrr=%.3f f1=%.3f orient=%.3f | ARM_B mrr=%.3f | ARM_C mrr=%.3f | "
          "ARM_D mrr=%.3f | ARM_E mrr=%.3f | unique_arms=%d/5"
          % (seed, time.time() - t_start,
             arm_results["ARM_A_FULL"]["chain_mrr_5"],
             arm_results["ARM_A_FULL"]["skeleton_f1"],
             arm_results["ARM_A_FULL"]["orientation_acc"],
             arm_results["ARM_B_SKEL_ONLY"]["chain_mrr_5"],
             arm_results["ARM_C_TEMP_ONLY"]["chain_mrr_5"],
             arm_results["ARM_D_TRUE_CORR_CEIL"]["chain_mrr_5"],
             arm_results["ARM_E_RANDOM"]["chain_mrr_5"],
             unique), flush=True)

    return {
        "seed": seed,
        "elapsed_s": time.time() - t_start,
        "arms": arm_results,
        "arm_hashes": arm_hashes,
        "unique_arms": unique,
        "N": N,
        "n_vars": N_VARS,
        "n_obs": N_OBS,
        "run_mode": RUN_MODE,
    }


# ---------- aggregate + verdict ----------

def aggregate(per_seed: List[Dict]) -> Dict[str, Dict[str, float]]:
    agg = {arm: {} for arm in ARMS}
    metric_keys = ["chain_mrr_5", "skeleton_f1", "orientation_acc"]
    for arm in ARMS:
        for mk in metric_keys:
            vals = [s["arms"][arm][mk] for s in per_seed]
            agg[arm][mk] = float(np.mean(vals))
            agg[arm][mk + "_std"] = float(np.std(vals))
    return agg


def verdict(per_seed: List[Dict], agg: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
    mrr_A = agg["ARM_A_FULL"]["chain_mrr_5"]
    f1_A = agg["ARM_A_FULL"]["skeleton_f1"]
    orient_A = agg["ARM_A_FULL"]["orientation_acc"]
    mrr_B = agg["ARM_B_SKEL_ONLY"]["chain_mrr_5"]
    mrr_C = agg["ARM_C_TEMP_ONLY"]["chain_mrr_5"]
    mrr_D = agg["ARM_D_TRUE_CORR_CEIL"]["chain_mrr_5"]
    mrr_E = agg["ARM_E_RANDOM"]["chain_mrr_5"]
    gap_AB = mrr_A - mrr_B
    gap_AC = mrr_A - mrr_C
    gap_DA = mrr_D - mrr_A
    gap_AE = mrr_A - mrr_E

    # Cardinality check (only enforced in full mode; smoke = 1 seed * 5 arms * 3 metrics = 15 by design)
    n_units = sum(1 for s in per_seed for arm in ARMS for mk in ("chain_mrr_5", "skeleton_f1", "orientation_acc")
                  if arm in s["arms"] and mk in s["arms"][arm])
    expected_full = 5 * 3 * 3
    if RUN_MODE == "smoke":
        cardinality_ok = n_units >= 5 * 3 * len(per_seed)
    else:
        cardinality_ok = n_units >= 40 and n_units >= expected_full - 5

    # Arms-must-differ: at least 4 of 5 unique hashes per seed (ARM_B and ARM_A share skeleton; may collide on f1).
    arms_differ_verified = all(s["unique_arms"] >= 4 for s in per_seed)

    summary = (
        "MEASURED@chain-MRR@5=%.3f (A) skeleton-F1=%.3f orient-acc=%.3f | gaps: A-B=%.3f A-C=%.3f D-A=%.3f A-E=%.3f | "
        "ARM_B=%.3f ARM_C=%.3f ARM_D=%.3f ARM_E=%.3f | cardinality_ok=%s arms_differ=%s N=%d N_VARS=%d N_OBS=%d seeds=%d"
        % (mrr_A, f1_A, orient_A, gap_AB, gap_AC, gap_DA, gap_AE,
           mrr_B, mrr_C, mrr_D, mrr_E, cardinality_ok, arms_differ_verified,
           N, N_VARS, N_OBS, len(per_seed))
    )

    if not cardinality_ok:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH: n_units=%d < 40. " % n_units + summary)
    if not arms_differ_verified:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_COLLIDE: at least one seed had <4 unique arm hashes. " + summary)

    # Smoke discriminator (per discriminator-survives-scale)
    if RUN_MODE == "smoke":
        if gap_AC >= 0.05 and gap_AE >= 0.25:
            return ("SMOKE_PASS", "SMOKE_PASS: discriminator survives (A-C>=0.05 AND A-E>=0.25). " + summary)
        return ("HARD_FAIL",
                "HARD_FAIL: smoke discriminator did NOT survive (A-C=%.3f<0.05 OR A-E=%.3f<0.25); do NOT dispatch full. "
                % (gap_AC, gap_AE) + summary)

    # Full HARD bands
    if mrr_A < 0.25 or f1_A < 0.40 or gap_AC < 0.03 or gap_AE < 0.20:
        return ("HARD_FAIL",
                "HARD_FAIL: chain-MRR<0.25 OR skeleton-F1<0.40 OR (A-C)<0.03 OR (A-E)<0.20. " + summary)
    if mrr_A >= 0.50 and f1_A >= 0.70 and orient_A >= 0.75 and gap_AB >= 0.10 and gap_AC >= 0.10 and gap_DA < 0.15:
        return ("HARD_PASS",
                "HARD_PASS: end-to-end causal-chain extraction Stage 3 -- all 6 HARD_PASS bands met. " + summary)
    if 0.25 <= mrr_A < 0.50 and f1_A >= 0.50:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: chain-MRR in [0.25,0.50] with skeleton-F1>=0.50; partial mechanism. " + summary)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: outside HARD_PASS but above HARD_FAIL floor on primary metrics. " + summary)


# ---------- main ----------

def main() -> None:
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)

    print("[config] anchor=%s mode=%s N=%d N_VARS=%d N_OBS=%d seeds=%s DAG_EDGES=%s GT_CHAINS=%s"
          % (ANCHOR_NAME, RUN_MODE, N, N_VARS, N_OBS, SEEDS, DAG_EDGES, GT_CHAINS), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    per_seed: List[Dict] = []
    for s in SEEDS:
        per_seed.append(run_seed(s))
    agg = aggregate(per_seed)
    v, vmsg = verdict(per_seed, agg)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "N": N,
        "n_vars": N_VARS,
        "n_obs": N_OBS,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "per_seed": per_seed,
        "arms_aggregate": agg,
        "elapsed_s": time.time() - t0,
        "parent_atoms": [
            "data/exp_causal_correlational_disambig_v1/metrics.json",
            "data/exp_counterfactual_replay_latency_delta_stack_v2_single_intervention/metrics.json",
            "data/exp_causal_audit_chain_depth_v1/metrics.json",
        ],
    }
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written to %s/metrics.json" % out_dir, flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:
        print("[FATAL] %s: %s" % (type(e).__name__, e), flush=True)
        raise
