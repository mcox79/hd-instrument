"""
hierarchical_concept_binding_smoke_v1 -- substrate-native nested HRR binding for hierarchical
ontologies. Second-tier substrate-only enabler smoke.

SCIENTIFIC QUESTION:
  Does nested HRR binding (parent_vec -> child_vec via role-bind) enable the substrate to encode
  hierarchical ontologies (animal -> mammal -> dog -> labrador) with (a) reasoning-down-the-chain
  retrieval ("is labrador a mammal?") AND (b) a capacity multiplier vs flat random-vector encoding?

BRAIN ANALOG:
  Cortical hierarchy reuses lower-level features across categories (V1 edges -> V2 textures ->
  V4 shapes -> IT objects). Same low-level features serve "dog" and "cat" and "table".
  Substrate-native: same parent_vec serves all children; only the child's role-bind differs.

CORPUS:
  Programmatic 4-level hierarchy. ~30 root concepts, branching factor 2 per level ->
  levels [30, 60, 120, 240] = 450 entities. Smoke halves (15 roots -> [15,30,60,120] = 225 entities).

ARMS (3):
  1. ARM_FLAT             -- each entity gets independent random bipolar vector. Capacity baseline.
  2. ARM_NESTED_BIND      -- substrate-native hierarchy:
                              root_vec        = random bipolar
                              child_vec       = bind(parent_vec, child_identity_role_vec)
                              Each ENTITY has its own random unit role vector (child_identity_role);
                              siblings have DIFFERENT identity-roles. Hierarchy is encoded in the
                              chain of binds; recovery walks ancestor chain by unbinding entity's
                              OWN identity-role to reveal parent_vec.
  3. ARM_NESTED_BIND_FACT -- bundle root + all-ancestor-identity-roles:
                              entity_vec = bundle(root_vec, my_identity, parent_identity, ...)
                              (tests bundle/superposition vs recursive bind for hierarchy encoding)

METRICS:
  A) hierarchy_retrieval_accuracy at each level (1..4) -- given leaf, recover each ancestor
     via recursive unbind (NESTED_BIND) / decomposition test (NESTED_BIND_FACT).
  B) capacity_at_noise (sigma=1.0) -- how many entities can we add to the cleanup codebook
     before recall@1 drops below 0.80?
  C) cross_hierarchy_interference -- does adding sibling chains (e.g. "cat" near "dog") hurt
     either chain's retrieval? Measured as recall@1 vs sibling-density.

PRE-REG HARD-PASS (hierarchical binding enables capacity multiplier + reasoning;
chain-grade-eligible at full-grid, MEASURED_MECHANISM at smoke):
  HP1: ARM_NESTED_BIND hierarchy_retrieval_accuracy >= 0.85 at ALL 4 levels (across all seeds, mean per level)
  HP2: capacity_at_sigma1_NESTED >= 2x capacity_at_sigma1_FLAT (mean across seeds)

PRE-REG HARD-FAIL:
  HF1: ARM_NESTED_BIND level-4 retrieval accuracy < 0.50 (deep hierarchy retrieval broken)
  HF2: capacity_at_sigma1_NESTED <= capacity_at_sigma1_FLAT (no multiplier benefit)

MIDDLE_BAND: hierarchy works at shallow levels but degrades at depth; partial multiplier.

FORMULA SELF-TESTS (run before measurement; abort on failure):
  SELFTEST_1: bind/unbind round-trip cos at N_DIM=4096 >= 0.40 (FHRR real-valued floor)
  SELFTEST_2: depth=1 retrieval is perfect (recall=1.0) on 5-pair holdout
  SELFTEST_3: depth=4 retrieval >= chance (sanity that mechanism isn't broken at construction)

NUMPY-ONLY. ASCII-ONLY. Smoke target <10min CPU wall.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "hierarchical_concept_binding_smoke_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- CONFIG ----
N_DIM = 4096
# Hierarchy: branching factor 2 per level, 4 levels deep.
# Full: 30 roots -> [30, 60, 120, 240] entities, total 450.
# Smoke: 15 roots -> [15, 30, 60, 120] entities, total 225.
N_ROOTS_FULL = 30
N_ROOTS_SMOKE = 15
BRANCH = 2
DEPTH = 4

N_ROOTS = N_ROOTS_SMOKE if (RUN_MODE == "smoke" or _ARGS.smoke) else N_ROOTS_FULL

SEEDS = [7, 17, 23]

# Capacity-sweep config (B):
#   We add entities to a cleanup codebook and measure recall@1 under gaussian
#   noise (sigma=1.0 in unit-vector space). Increase M until recall < 0.80.
CAP_SIGMA = 1.0
CAP_RECALL_FLOOR = 0.80
CAP_PROBE_N_QUERIES = 60          # queries per M-grid-point
CAP_M_GRID = [50, 100, 200, 400, 800, 1600] if (RUN_MODE != "smoke") else [50, 100, 200, 400, 800]

# Pre-reg bands
HP_HIER_ACC = 0.85
HP_CAP_MULTIPLIER = 2.0
HF_LEVEL4_ACC = 0.50
N_SANITY_PAIRS = 5


# ----------------------------------------------------------------------
# HD primitives -- FHRR real-valued analog (circular convolution).
# ----------------------------------------------------------------------

def random_unit(n: int, rng: np.random.RandomState) -> np.ndarray:
    v = rng.randn(n).astype(np.float64)
    v /= (np.linalg.norm(v) + 1e-12)
    return v


def random_bipolar(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Bipolar +/-1 / sqrt(n) for unit-norm."""
    v = (rng.randint(0, 2, size=n).astype(np.float64) * 2.0 - 1.0)
    v /= math.sqrt(n)
    return v


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution bind. FHRR real analog."""
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular correlation: c convolved with b's involution."""
    fc = np.fft.fft(c)
    fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real


def bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """Superposition: sum then renormalize to unit norm."""
    s = np.zeros_like(vecs[0])
    for v in vecs:
        s = s + v
    n = np.linalg.norm(s)
    if n > 1e-12:
        s = s / n
    return s


def cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def renorm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n > 1e-12:
        return v / n
    return v


# ----------------------------------------------------------------------
# FORMULA SELF-TESTS
# ----------------------------------------------------------------------

def _selftest_bind_unbind():
    rng = np.random.RandomState(0)
    a = random_unit(N_DIM, rng)
    b = random_unit(N_DIM, rng)
    c = bind(a, b)
    a_rec = unbind(c, b)
    c_ab = cos(a, a_rec)
    # FHRR real-valued bind/unbind has 1/sqrt(N) noise; ~0.4 floor at N=4096
    assert c_ab >= 0.40, f"bind/unbind round-trip cos={c_ab:.4f} (need >= 0.40)"
    return c_ab


def _selftest_depth1_perfect():
    """At depth=1 (parent + one role), retrieval should be near-perfect (recall=1.0) on 5-pair holdout."""
    rng = np.random.RandomState(1)
    # Build 5 parents + 1 shared role
    parents = [random_unit(N_DIM, rng) for _ in range(5)]
    role = random_unit(N_DIM, rng)
    children = [bind(p, role) for p in parents]
    # Recover parent via unbind(child, role); argmax-cos vs parent codebook
    correct = 0
    for i, ch in enumerate(children):
        p_hat = unbind(ch, role)
        sims = np.array([cos(p_hat, p) for p in parents])
        if int(np.argmax(sims)) == i:
            correct += 1
    assert correct == 5, f"depth=1 retrieval only {correct}/5 (mechanism broken)"
    return correct


def _selftest_depth4_above_chance():
    """At depth=4 nested bind, leaf -> recover-root must be above chance (>= 1/5 = 0.20)."""
    rng = np.random.RandomState(2)
    # 5 roots, single chain each, 4 deep
    roots = [random_unit(N_DIM, rng) for _ in range(5)]
    roles = [random_unit(N_DIM, rng) for _ in range(4)]  # one role per level
    leaves = []
    for r in roots:
        v = r
        for level_role in roles:
            v = bind(v, level_role)
        leaves.append(v)
    # Recover root from leaf by recursive unbind with roles in REVERSE order
    correct = 0
    for i, leaf in enumerate(leaves):
        v = leaf
        for level_role in reversed(roles):
            v = unbind(v, level_role)
        sims = np.array([cos(v, r) for r in roots])
        if int(np.argmax(sims)) == i:
            correct += 1
    # Above-chance bar: need at least 2/5 (40%) since chance is 1/5 (20%).
    # At N=4096 depth-4 recursive FHRR unbind has compounded noise; pragmatic
    # bar = strictly above chance with margin (not perfect — that's level B).
    assert correct >= 2, f"depth=4 retrieval {correct}/5 (need >= 2/5; mechanism broken at construction)"
    return correct


def _instrumentation_selftest():
    c_bu = _selftest_bind_unbind()
    d1 = _selftest_depth1_perfect()
    d4 = _selftest_depth4_above_chance()
    print(
        f"[selftest] PASS: bind_unbind_cos={c_bu:.4f} depth1_recall={d1}/5 depth4_recall={d4}/5",
        flush=True,
    )
    return {
        "bind_unbind_cos": float(c_bu),
        "depth1_correct": int(d1),
        "depth1_total": 5,
        "depth4_correct": int(d4),
        "depth4_total": 5,
    }


SELFTEST_RESULTS = _instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------------------------------------------------
# HIERARCHY CONSTRUCTION
# ----------------------------------------------------------------------

def build_hierarchy(seed: int, n_roots: int, branch: int, depth: int):
    """Build a hierarchical entity tree.

    Returns:
      tree[level] = list of entity_id at that level (level 0 = roots)
      parent_of[entity_id] = parent_id (None for roots)
      level_of[entity_id] = int
      entities_per_level[level] = count
    """
    rng = np.random.RandomState(seed + 1000)  # noqa: F841 - reserved for stochastic tree variants
    next_id = 0
    tree = [[] for _ in range(depth)]
    parent_of = {}
    level_of = {}
    # Roots at level 0
    roots = list(range(next_id, next_id + n_roots))
    next_id += n_roots
    tree[0] = roots
    for r in roots:
        parent_of[r] = None
        level_of[r] = 0
    # Successive levels: each parent gets `branch` children
    for level in range(1, depth):
        new_layer = []
        for parent in tree[level - 1]:
            for _ in range(branch):
                cid = next_id
                next_id += 1
                new_layer.append(cid)
                parent_of[cid] = parent
                level_of[cid] = level
        tree[level] = new_layer
    return tree, parent_of, level_of, next_id


def ancestor_chain(entity_id: int, parent_of: Dict) -> List[int]:
    """Walk up to root. Returns [entity_id, parent, grandparent, ..., root]."""
    chain = [entity_id]
    cur = parent_of[entity_id]
    while cur is not None:
        chain.append(cur)
        cur = parent_of[cur]
    return chain


# ----------------------------------------------------------------------
# ARM_FLAT: each entity gets independent random bipolar
# ----------------------------------------------------------------------

def build_arm_flat(seed: int, total_entities: int) -> Dict[int, np.ndarray]:
    rng = np.random.RandomState(seed + 2000)
    return {i: random_bipolar(N_DIM, rng) for i in range(total_entities)}


# ----------------------------------------------------------------------
# ARM_NESTED_BIND: nested HRR via shared per-level role vectors
# ----------------------------------------------------------------------

def build_arm_nested_bind(seed: int, tree, parent_of, level_of, total_entities: int):
    """Each entity has its OWN identity-role vec; child_vec = bind(parent_vec, child_identity_role).
    Siblings get DIFFERENT identity-roles, so they are distinguishable.

    Returns (vecs, identity_roles) where identity_roles[entity_id] = role vec (None for roots).
    """
    rng = np.random.RandomState(seed + 3000)
    identity_roles = {}
    vecs = {}
    # Roots: random unit (no role)
    for r in tree[0]:
        vecs[r] = random_unit(N_DIM, rng)
        identity_roles[r] = None
    # Successive levels: each child gets its OWN identity role
    for level in range(1, len(tree)):
        for eid in tree[level]:
            identity_roles[eid] = random_unit(N_DIM, rng)
            p = parent_of[eid]
            vecs[eid] = bind(vecs[p], identity_roles[eid])
    return vecs, identity_roles


# ----------------------------------------------------------------------
# ARM_NESTED_BIND_FACT: bundle parent + role chain
# ----------------------------------------------------------------------

def build_arm_nested_bind_fact(seed: int, tree, parent_of, level_of, total_entities: int):
    """entity_vec = bundle(root_vec, identity_role_for_each_ancestor_step).

    Per-entity identity roles (same allocation as ARM_NESTED_BIND). The DIFFERENCE: instead of
    recursive bind, we bundle (superpose) root_vec + all identity-roles along ancestor chain
    (excluding root which has no role). This is a flat-superposition decomposition test.
    """
    rng = np.random.RandomState(seed + 4000)
    identity_roles = {}
    root_vec_of = {}
    for r in tree[0]:
        root_vec_of[r] = random_unit(N_DIM, rng)
        identity_roles[r] = None
    # Allocate identity roles for non-root entities
    for level in range(1, len(tree)):
        for eid in tree[level]:
            identity_roles[eid] = random_unit(N_DIM, rng)
    vecs = {}
    for level in range(len(tree)):
        for eid in tree[level]:
            chain = ancestor_chain(eid, parent_of)  # [self, parent, ..., root]
            root = chain[-1]
            components = [root_vec_of[root]]
            # Add identity role for each ancestor step from root toward self (excluding root)
            for ancestor in reversed(chain[:-1]):  # walk from oldest-non-root to self
                components.append(identity_roles[ancestor])
            vecs[eid] = bundle(components)
    return vecs, identity_roles, root_vec_of


# ----------------------------------------------------------------------
# METRIC A: hierarchy_retrieval_accuracy at each level
# ----------------------------------------------------------------------

def hierarchy_retrieval_nested_bind(
    vecs: Dict[int, np.ndarray],
    identity_roles: Dict[int, np.ndarray],
    tree,
    parent_of: Dict,
    level_of: Dict,
) -> Dict[int, float]:
    """For ARM_NESTED_BIND (per-entity identity role):
    For each entity at level L (L >= 1), recover parent at level L-1 via:
        p_hat = unbind(entity_vec, identity_role[entity])
    Score: argmax-cos over parent codebook == true parent.

    Also returns deepest-leaf-to-root: peel identity-roles up the ancestor chain.
    """
    out = {}
    depth = len(tree)
    for level in range(1, depth):
        parent_layer = tree[level - 1]
        codebook = np.stack([vecs[p] for p in parent_layer], axis=0)
        codebook = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-12)
        correct = 0
        n = 0
        for eid in tree[level]:
            p_hat = unbind(vecs[eid], identity_roles[eid])
            p_hat = renorm(p_hat)
            sims = codebook @ p_hat
            pred_idx = int(np.argmax(sims))
            pred_parent = parent_layer[pred_idx]
            if pred_parent == parent_of[eid]:
                correct += 1
            n += 1
        out[level] = float(correct) / float(max(1, n))
    # Deepest leaf-to-root: walk the chain peeling each entity's own identity role
    leaf_level = depth - 1
    root_layer = tree[0]
    codebook_roots = np.stack([vecs[r] for r in root_layer], axis=0)
    codebook_roots = codebook_roots / (np.linalg.norm(codebook_roots, axis=1, keepdims=True) + 1e-12)
    correct_lr = 0
    n_lr = 0
    for eid in tree[leaf_level]:
        v = vecs[eid]
        # Walk up: peel my role, then parent's role, etc., until root
        cur = eid
        while parent_of[cur] is not None:
            v = unbind(v, identity_roles[cur])
            cur = parent_of[cur]
        v = renorm(v)
        sims = codebook_roots @ v
        pred_idx = int(np.argmax(sims))
        chain = ancestor_chain(eid, parent_of)
        true_root = chain[-1]
        if root_layer[pred_idx] == true_root:
            correct_lr += 1
        n_lr += 1
    out["leaf_to_root"] = float(correct_lr) / float(max(1, n_lr))
    return out


def hierarchy_retrieval_flat(
    vecs: Dict[int, np.ndarray],
    tree,
    parent_of: Dict,
    level_of: Dict,
) -> Dict[int, float]:
    """For ARM_FLAT:
    There is NO mechanism to "recover ancestor" -- entities are independent. The honest baseline
    is the prior: argmax-cos over the parent codebook returns a random parent. So expected acc =
    1 / |parent_layer|. We MEASURE this empirically (with noise) to make the comparison concrete.
    """
    out = {}
    depth = len(tree)
    for level in range(1, depth):
        parent_layer = tree[level - 1]
        codebook = np.stack([vecs[p] for p in parent_layer], axis=0)
        correct = 0
        n = 0
        for eid in tree[level]:
            # Use child's own vector as "query" for parent (no unbind mechanism in FLAT)
            q = renorm(vecs[eid])
            sims = codebook @ q
            pred_idx = int(np.argmax(sims))
            if parent_layer[pred_idx] == parent_of[eid]:
                correct += 1
            n += 1
        out[level] = float(correct) / float(max(1, n))
    # Leaf-to-root for FLAT: same expected chance
    leaf_level = depth - 1
    root_layer = tree[0]
    codebook_roots = np.stack([vecs[r] for r in root_layer], axis=0)
    correct_lr = 0
    n_lr = 0
    for eid in tree[leaf_level]:
        q = renorm(vecs[eid])
        sims = codebook_roots @ q
        pred_idx = int(np.argmax(sims))
        chain = ancestor_chain(eid, parent_of)
        true_root = chain[-1]
        if root_layer[pred_idx] == true_root:
            correct_lr += 1
        n_lr += 1
    out["leaf_to_root"] = float(correct_lr) / float(max(1, n_lr))
    return out


def hierarchy_retrieval_nested_fact(
    vecs: Dict[int, np.ndarray],
    identity_roles: Dict[int, np.ndarray],
    root_vec_of: Dict[int, np.ndarray],
    tree,
    parent_of: Dict,
    level_of: Dict,
) -> Dict[int, float]:
    """For ARM_NESTED_BIND_FACT (per-entity identity-role bundle):
    Entity = bundle(root + identity_role_for_each_ancestor_step).
    To recover parent at level L-1 from an entity at level L: subtract this entity's identity role
    from the unrenormalized bundle, then renorm-and-project onto parent codebook.
    """
    out = {}
    depth = len(tree)
    for level in range(1, depth):
        parent_layer = tree[level - 1]
        codebook = np.stack([vecs[p] for p in parent_layer], axis=0)
        codebook = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-12)
        correct = 0
        n = 0
        for eid in tree[level]:
            n_components_self = level + 1   # root + (level) identity roles along chain
            my_role = identity_roles[eid]
            v_self = vecs[eid] * math.sqrt(n_components_self)
            v_parent_approx = v_self - my_role
            v_parent_approx = renorm(v_parent_approx)
            sims = codebook @ v_parent_approx
            pred_idx = int(np.argmax(sims))
            if parent_layer[pred_idx] == parent_of[eid]:
                correct += 1
            n += 1
        out[level] = float(correct) / float(max(1, n))
    # Leaf-to-root: subtract ALL identity roles along ancestor chain; project onto root codebook
    leaf_level = depth - 1
    root_layer = tree[0]
    codebook_roots = np.stack([vecs[r] for r in root_layer], axis=0)
    codebook_roots = codebook_roots / (np.linalg.norm(codebook_roots, axis=1, keepdims=True) + 1e-12)
    correct_lr = 0
    n_lr = 0
    for eid in tree[leaf_level]:
        chain = ancestor_chain(eid, parent_of)  # [self, parent, ..., root]
        n_components_self = leaf_level + 1
        v_self = vecs[eid] * math.sqrt(n_components_self)
        for ancestor in chain[:-1]:  # exclude root
            v_self = v_self - identity_roles[ancestor]
        v_self = renorm(v_self)
        sims = codebook_roots @ v_self
        pred_idx = int(np.argmax(sims))
        true_root = chain[-1]
        if root_layer[pred_idx] == true_root:
            correct_lr += 1
        n_lr += 1
    out["leaf_to_root"] = float(correct_lr) / float(max(1, n_lr))
    return out


# ----------------------------------------------------------------------
# METRIC B: capacity at noise (sigma=1.0)
# ----------------------------------------------------------------------

def capacity_at_noise_flat(seed: int, m_grid: List[int], sigma: float, n_queries: int) -> int:
    """Build M random bipolar codebook entries; query with code+sigma*gaussian; argmax-cos recall@1.
    Returns largest M in m_grid for which recall@1 >= CAP_RECALL_FLOOR. If first M fails -> 0.
    """
    rng = np.random.RandomState(seed + 5000)
    last_pass_M = 0
    last_recall = None
    per_m = {}
    for M in m_grid:
        codebook = np.stack([random_bipolar(N_DIM, rng) for _ in range(M)], axis=0)
        # Sample queries
        idxs = rng.randint(0, M, size=n_queries)
        correct = 0
        for q_idx in idxs:
            noise = rng.randn(N_DIM) * (sigma / math.sqrt(N_DIM))  # match scale of bipolar unit
            query = codebook[q_idx] + noise
            query = renorm(query)
            sims = codebook @ query
            pred = int(np.argmax(sims))
            if pred == q_idx:
                correct += 1
        recall = correct / float(n_queries)
        per_m[M] = float(recall)
        if recall >= CAP_RECALL_FLOOR:
            last_pass_M = M
            last_recall = recall
    return last_pass_M, per_m


def capacity_at_noise_nested(seed: int, m_grid: List[int], sigma: float, n_queries: int) -> Tuple[int, Dict]:
    """For nested-bind: build a hierarchy growing M entities (mix of all levels), then query
    each entity vec with noise. Argmax-cos recall@1 over the SAME codebook (all entities).

    Hierarchy: roots = ceil(M/15) (so smoke->small trees), branch=2, depth=4.
    We grow the tree until total_entities >= M, then take first M as codebook.
    """
    last_pass_M = 0
    per_m = {}
    for M in m_grid:
        # Build a hierarchy big enough; estimate required roots
        # total = roots * (1 + 2 + 4 + 8) = 15*roots at depth=4, branch=2
        roots_needed = max(2, math.ceil(M / 15.0))
        tree, parent_of, level_of, total = build_hierarchy(seed + M, roots_needed, BRANCH, DEPTH)
        vecs, _identity_roles = build_arm_nested_bind(seed + M, tree, parent_of, level_of, total)
        # Codebook: all entities in id order, then take first M
        all_ids = sorted(vecs.keys())[:M]
        codebook = np.stack([vecs[i] for i in all_ids], axis=0)
        # Renorm codebook for fair cosine
        codebook = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-12)
        rng = np.random.RandomState(seed + 6000 + M)
        idxs = rng.randint(0, M, size=n_queries)
        correct = 0
        for q_idx in idxs:
            noise = rng.randn(N_DIM) * (sigma / math.sqrt(N_DIM))
            query = codebook[q_idx] + noise
            query = renorm(query)
            sims = codebook @ query
            pred = int(np.argmax(sims))
            if pred == q_idx:
                correct += 1
        recall = correct / float(n_queries)
        per_m[M] = float(recall)
        if recall >= CAP_RECALL_FLOOR:
            last_pass_M = M
    return last_pass_M, per_m


# ----------------------------------------------------------------------
# METRIC C: cross-hierarchy interference
# ----------------------------------------------------------------------

def cross_hierarchy_interference(seed: int, n_roots_test: int = 6) -> Dict:
    """Build a tree, measure leaf-to-root recall@1; then DOUBLE the tree (add sibling subtrees);
    re-measure. Report: (single_recall, doubled_recall, delta).

    Honest discriminator: nested-bind should degrade with sibling-density because the parent
    codebook grows (more candidates to confuse against) but per-entity identity roles still
    distinguish at unbind step. Compare delta to a flat-arm baseline.
    """
    # Single hierarchy
    tree_s, p_s, l_s, total_s = build_hierarchy(seed + 7000, n_roots_test, BRANCH, DEPTH)
    vecs_s, ids_s = build_arm_nested_bind(seed + 7000, tree_s, p_s, l_s, total_s)
    res_s = hierarchy_retrieval_nested_bind(vecs_s, ids_s, tree_s, p_s, l_s)
    single_l2r = res_s["leaf_to_root"]

    # Doubled hierarchy
    tree_d, p_d, l_d, total_d = build_hierarchy(seed + 8000, n_roots_test * 2, BRANCH, DEPTH)
    vecs_d, ids_d = build_arm_nested_bind(seed + 8000, tree_d, p_d, l_d, total_d)
    res_d = hierarchy_retrieval_nested_bind(vecs_d, ids_d, tree_d, p_d, l_d)
    doubled_l2r = res_d["leaf_to_root"]

    return {
        "single_leaf_to_root": float(single_l2r),
        "doubled_leaf_to_root": float(doubled_l2r),
        "delta": float(doubled_l2r - single_l2r),
        "n_roots_single": int(n_roots_test),
        "n_roots_doubled": int(n_roots_test * 2),
    }


# ----------------------------------------------------------------------
# PER-SEED RUN
# ----------------------------------------------------------------------

def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(
        f"[seed={seed}] building hierarchy (N_DIM={N_DIM}, n_roots={N_ROOTS}, branch={BRANCH}, "
        f"depth={DEPTH})...",
        flush=True,
    )
    tree, parent_of, level_of, total_entities = build_hierarchy(seed, N_ROOTS, BRANCH, DEPTH)
    print(
        f"[seed={seed}] hierarchy: total={total_entities} entities; per-level sizes={[len(L) for L in tree]}",
        flush=True,
    )

    # Build all three arms
    t_arm = time.time()
    flat_vecs = build_arm_flat(seed, total_entities)
    nb_vecs, nb_ids = build_arm_nested_bind(seed, tree, parent_of, level_of, total_entities)
    nbf_vecs, nbf_ids, nbf_roots = build_arm_nested_bind_fact(
        seed, tree, parent_of, level_of, total_entities
    )
    print(f"[seed={seed}] arms built in {time.time()-t_arm:.2f}s", flush=True)

    # Metric A: hierarchy retrieval at each level
    t_a = time.time()
    flat_acc = hierarchy_retrieval_flat(flat_vecs, tree, parent_of, level_of)
    nb_acc = hierarchy_retrieval_nested_bind(nb_vecs, nb_ids, tree, parent_of, level_of)
    nbf_acc = hierarchy_retrieval_nested_fact(nbf_vecs, nbf_ids, nbf_roots, tree, parent_of, level_of)
    t_a_elapsed = time.time() - t_a
    print(
        f"[seed={seed}] A) hierarchy_retrieval: FLAT={flat_acc} NESTED={nb_acc} NESTED_FACT={nbf_acc} "
        f"in {t_a_elapsed:.2f}s",
        flush=True,
    )

    # Metric B: capacity at noise
    t_b = time.time()
    flat_cap, flat_cap_curve = capacity_at_noise_flat(seed, CAP_M_GRID, CAP_SIGMA, CAP_PROBE_N_QUERIES)
    nb_cap, nb_cap_curve = capacity_at_noise_nested(seed, CAP_M_GRID, CAP_SIGMA, CAP_PROBE_N_QUERIES)
    t_b_elapsed = time.time() - t_b
    print(
        f"[seed={seed}] B) capacity_at_sigma{CAP_SIGMA}_recall>={CAP_RECALL_FLOOR}: "
        f"FLAT={flat_cap} NESTED={nb_cap} (multiplier={float(nb_cap)/max(1,flat_cap):.2f}x) "
        f"in {t_b_elapsed:.2f}s",
        flush=True,
    )

    # Metric C: cross-hierarchy interference
    t_c = time.time()
    interf = cross_hierarchy_interference(seed, n_roots_test=6)
    t_c_elapsed = time.time() - t_c
    print(
        f"[seed={seed}] C) cross_hier_interference: single={interf['single_leaf_to_root']:.4f} "
        f"doubled={interf['doubled_leaf_to_root']:.4f} delta={interf['delta']:+.4f} in {t_c_elapsed:.2f}s",
        flush=True,
    )

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N_DIM": int(N_DIM),
        "n_roots": int(N_ROOTS),
        "branch": int(BRANCH),
        "depth": int(DEPTH),
        "total_entities": int(total_entities),
        "per_level_sizes": [int(len(L)) for L in tree],
        "metric_A_flat_per_level": {str(k): float(v) for k, v in flat_acc.items()},
        "metric_A_nested_per_level": {str(k): float(v) for k, v in nb_acc.items()},
        "metric_A_nested_fact_per_level": {str(k): float(v) for k, v in nbf_acc.items()},
        "metric_B_flat_capacity": int(flat_cap),
        "metric_B_nested_capacity": int(nb_cap),
        "metric_B_flat_curve": flat_cap_curve,
        "metric_B_nested_curve": nb_cap_curve,
        "metric_B_multiplier": float(nb_cap) / float(max(1, flat_cap)),
        "metric_C": interf,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }


# ----------------------------------------------------------------------
# VERDICT
# ----------------------------------------------------------------------

def compute_verdict(per_seed: List[Dict], selftest: Dict) -> Tuple[str, str]:
    if not per_seed:
        return ("HARD_FAIL", "No valid per-seed results.")

    # Sanity self-test gating
    if selftest.get("depth1_correct", 0) != 5:
        return ("HARD_FAIL", f"selftest depth1 broken: {selftest.get('depth1_correct')}/5")
    if selftest.get("depth4_correct", 0) < 2:
        return ("HARD_FAIL",
                f"selftest depth4 below-chance: {selftest.get('depth4_correct')}/5")

    # Aggregate per-level NESTED accuracy: mean over seeds, per level
    levels_present = sorted(set(
        int(k) for r in per_seed for k in r["metric_A_nested_per_level"].keys() if k != "leaf_to_root"
    ))
    nested_per_level_mean = {}
    for L in levels_present:
        vals = [r["metric_A_nested_per_level"][str(L)] for r in per_seed]
        nested_per_level_mean[L] = float(np.mean(vals))
    # Also include leaf_to_root (deepest)
    leaf_to_root_mean = float(np.mean([r["metric_A_nested_per_level"]["leaf_to_root"] for r in per_seed]))
    nested_per_level_mean["leaf_to_root"] = leaf_to_root_mean

    # Level-4 = highest level index (DEPTH-1 in 0-indexed = DEPTH-1). Here DEPTH=4 -> level=3 is "level 4"
    # in 1-indexed counting; the deepest parent-retrieval is level=DEPTH-1.
    deepest_level_idx = max(levels_present) if levels_present else DEPTH - 1
    deepest_acc = nested_per_level_mean.get(deepest_level_idx, 0.0)

    # Capacity multiplier
    flat_caps = [r["metric_B_flat_capacity"] for r in per_seed]
    nested_caps = [r["metric_B_nested_capacity"] for r in per_seed]
    flat_cap_mean = float(np.mean(flat_caps))
    nested_cap_mean = float(np.mean(nested_caps))
    multiplier = nested_cap_mean / max(1.0, flat_cap_mean)

    # HARD_FAIL checks
    if deepest_acc < HF_LEVEL4_ACC:
        msg = (f"HARD_FAIL HF1: deepest-level (idx={deepest_level_idx}) nested-bind retrieval "
               f"acc={deepest_acc:.4f} < {HF_LEVEL4_ACC} (deep hierarchy retrieval broken).")
        return ("HARD_FAIL", msg)

    # HF2 with by-construction-saturation check: if BOTH arms hit the M-grid cap (largest M),
    # the metric is ceiling-bound and cannot DISCRIMINATE -- demote to MIDDLE_BAND (capacity test
    # is non-informative at this grid; production cell must use a larger M-grid).
    grid_max_M = float(max(CAP_M_GRID))
    both_saturated = (flat_cap_mean >= grid_max_M) and (nested_cap_mean >= grid_max_M)
    if (not both_saturated) and nested_cap_mean <= flat_cap_mean:
        msg = (f"HARD_FAIL HF2: nested capacity {nested_cap_mean:.1f} <= flat capacity "
               f"{flat_cap_mean:.1f} (no multiplier benefit; not metric-cap-bound).")
        return ("HARD_FAIL", msg)

    # HARD_PASS checks
    all_levels_pass = all(nested_per_level_mean[L] >= HP_HIER_ACC for L in levels_present)
    multiplier_pass = multiplier >= HP_CAP_MULTIPLIER
    summary = (
        f"n_seeds={len(per_seed)} nested_per_level={ {L: round(nested_per_level_mean[L], 4) for L in levels_present} } "
        f"leaf_to_root_mean={leaf_to_root_mean:.4f} flat_cap_mean={flat_cap_mean:.1f} "
        f"nested_cap_mean={nested_cap_mean:.1f} multiplier={multiplier:.2f}x grid_max_M={grid_max_M}"
    )

    if all_levels_pass and multiplier_pass:
        return ("HARD_PASS",
                f"HARD_PASS: all levels >= {HP_HIER_ACC} AND capacity multiplier >= {HP_CAP_MULTIPLIER}x. "
                f"{summary}")

    # MIDDLE_BAND: hierarchy retrieval works but multiplier not realized OR metric ceiling hit
    if both_saturated:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND (METRIC_CEILING): all_levels_pass={all_levels_pass}; both arms hit "
                f"M-grid cap={grid_max_M:.0f} -- capacity discriminator non-informative at this "
                f"smoke grid. Production cell must extend M-grid. {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: all_levels_pass={all_levels_pass} multiplier_pass={multiplier_pass} "
            f"({multiplier:.2f}x). {summary}")


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)

t_sweep_start = time.time()
per_seed = []
for seed in SEEDS:
    print(f"\n[seed={seed}] hierarchical_concept_binding_smoke_v1 starting...", flush=True)
    result = run_seed(seed)
    per_seed.append(result)
    # Per-seed checkpoint
    cp_path = out_dir / f"partial_seed{seed}_{RUN_MODE}.json"
    cp_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[seed={seed}] checkpoint -> {cp_path}", flush=True)

verdict, verdict_msg = compute_verdict(per_seed, SELFTEST_RESULTS)
elapsed_s = time.time() - t_sweep_start

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N_DIM": N_DIM,
    "n_roots": N_ROOTS,
    "branch": BRANCH,
    "depth": DEPTH,
    "SEEDS": SEEDS,
    "cap_sigma": CAP_SIGMA,
    "cap_recall_floor": CAP_RECALL_FLOOR,
    "cap_m_grid": CAP_M_GRID,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_s,
    "selftest": SELFTEST_RESULTS,
    "per_seed": per_seed,
    "summary": verdict_msg,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
