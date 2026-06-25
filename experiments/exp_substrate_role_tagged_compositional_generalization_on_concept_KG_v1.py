"""substrate_role_tagged_compositional_generalization_on_concept_KG_v1.

USER course-correction (Wave E retry; supersedes original Cell B on text8).

text8 LM has no labels / no grammatical structure / no concept categories.
Testing role-tagged context on text8 = labeling primitive on unlabeled corpus.
Redirect: extend SEMANTIC battery v2 chain-grade A3 generalization=1.000 into
a stricter compositional regime.

Substrate sees:
  (king, R_subj_of, ruling_action)
  (queen, R_subj_of, ruling_action)
But for heldout 'prince' (in same category 'royal'):
  only (prince, is_a, royal) is in train -- NEVER (prince, R_subj_of, ...).
Can substrate predict (prince, R_subj_of, ?) -> ruling_action via category
structure transfer?

Arms (5):
  ARM_NO_ROLES                       control; no role binding.
  ARM_ROLES_ORTHOGONAL_RANDOM        Plate canonical: GS-orthogonal sparse-bipolar.
  ARM_ROLES_SEMANTICALLY_CLUSTERED   R_subj_of ~ R_agent close; R_pos1/2/3 close.
  ARM_GRAMMATICAL_ROLE_BINDING       full triple binding (subj+verb+obj).
  ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS  ARM_4 + label-driven concept anisotropy.

Bands (heldout-subject role-tagged query top1):
  HP_CHAIN_GRADE: best >= 0.85 AND beats NO_ROLES by >= 0.20 AND cv <= 0.05.
  HP:             best >= 0.70 AND beats NO_ROLES by >= 0.15.
  HARD_FAIL:      all role arms within +/- 0.05 of NO_ROLES.

Verify-referent:
  - SEMANTIC_concept_learner_battery_v2_FULL: verdict=HARD_PASS, A3 heldout
    top1=1.000 (cv=0.000), A4 compose top1=0.708. EXACT.

ASCII only; pure numpy; per-seed checkpoint; atexit synthesizer.
"""
from __future__ import annotations

import argparse
import atexit
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_role_tagged_compositional_generalization_on_concept_KG_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE) else os.environ.get(
    "HDLAB_RUN_MODE", "full"
).lower()
if _ARGS.self_test:
    RUN_MODE = "smoke"

# Bands
HP_CHAIN_GRADE_TOP1 = 0.85
HP_CHAIN_GRADE_LIFT = 0.20
HP_CV = 0.05
HP_TOP1 = 0.70
HP_LIFT = 0.15
HF_TOL = 0.05

# Config
V_CATEGORIES = 4
V_INSTANCES_PER_CAT = 8
V_INSTANCES = V_CATEGORIES * V_INSTANCES_PER_CAT  # 32
V_ROLES = 6   # R_subj_of, R_obj_of, R_property_of, R_pos1, R_pos2, R_pos3
V_PREDICATES = 8  # action / predicate types
N_HELDOUT_INSTANCES = 8  # 2 per category

if RUN_MODE == "smoke":
    N_DIM = 1024
    SEEDS = [7]
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23]

ARMS = [
    "ARM_NO_ROLES",
    "ARM_ROLES_ORTHOGONAL_RANDOM",
    "ARM_ROLES_SEMANTICALLY_CLUSTERED",
    "ARM_GRAMMATICAL_ROLE_BINDING",
    "ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS",
]

CONFIG_VERSION = (
    "subRT_compgen-v1: 5 arms x role-codebook constructions on concept-KG; "
    "V_cat=%d V_inst_per_cat=%d V_roles=%d V_preds=%d heldout=%d N=%d seeds=%s mode=%s; "
    "bands HP_CG_top1=%.2f HP_CG_lift=%.2f HP_top1=%.2f HP_lift=%.2f cv_max=%.2f HF_tol=%.2f"
) % (
    V_CATEGORIES, V_INSTANCES_PER_CAT, V_ROLES, V_PREDICATES, N_HELDOUT_INSTANCES,
    N_DIM, SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_TOP1, HP_CHAIN_GRADE_LIFT, HP_TOP1, HP_LIFT, HP_CV, HF_TOL,
)


# ============================================================================
# HRR / bipolar utilities
# ============================================================================

def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def bipolar_random(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return _l2_normalize_np(X)


def hrr_bind(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Circular convolution (HRR bind). Works on (n,) or (M, n)."""
    if A.ndim == 1:
        Fa = np.fft.rfft(A)
        Fb = np.fft.rfft(B)
        return np.fft.irfft(Fa * Fb, n=A.shape[0]).astype(np.float32)
    Fa = np.fft.rfft(A, axis=-1)
    Fb = np.fft.rfft(B, axis=-1)
    return np.fft.irfft(Fa * Fb, n=A.shape[-1], axis=-1).astype(np.float32)


def _category_of(inst_idx: int) -> int:
    return inst_idx // V_INSTANCES_PER_CAT


# ============================================================================
# Role codebook constructions
# ============================================================================

def role_codebook_orthogonal_random(n_dim: int, g: np.random.Generator,
                                       sparse_f: float = 0.02) -> np.ndarray:
    """Plate canonical: GS-orthogonal sparse-bipolar."""
    raw = (g.integers(0, 2, size=(V_ROLES, n_dim)) * 2 - 1).astype(np.float32)
    raw = _l2_normalize_np(raw)
    # Sparsify (top-k abs)
    k = max(1, int(round(sparse_f * n_dim)))
    sparse = np.zeros_like(raw)
    for i in range(V_ROLES):
        idx = np.argpartition(np.abs(raw[i]), -k)[-k:]
        sparse[i, idx] = np.sign(raw[i, idx])
        sparse[i] = _l2_normalize_np(sparse[i])
    # GS orthogonalize
    R = np.zeros_like(sparse)
    for i in range(V_ROLES):
        v = sparse[i].copy()
        for j in range(i):
            v = v - (R[j] @ v) * R[j]
        nm = np.linalg.norm(v)
        if nm < 1e-9:
            v = sparse[i].copy()
            nm = np.linalg.norm(v) + 1e-12
        R[i] = v / nm
    return R


def role_codebook_semantically_clustered(n_dim: int, g: np.random.Generator,
                                            cluster_overlap: float = 0.6) -> np.ndarray:
    """Construct role atoms so R_subj_of and R_obj_of are close (both 'argument-of-action'),
    and R_pos1/2/3 are close to each other (positional roles cluster together).

    Strategy: 2 base random unit vectors (semantic clusters); each role = base + perpendicular noise.
    cluster_overlap controls how close roles within a cluster are. Higher = tighter cluster.

    Role indices: 0=R_subj_of, 1=R_obj_of, 2=R_property_of, 3=R_pos1, 4=R_pos2, 5=R_pos3.
    Cluster A (argument roles): 0, 1, 2.
    Cluster B (positional roles): 3, 4, 5.
    """
    base = g.standard_normal(size=(2, n_dim)).astype(np.float32)
    base = _l2_normalize_np(base)
    # Make base[0] and base[1] orthogonal
    base[1] = base[1] - (base[0] @ base[1]) * base[0]
    base[1] = _l2_normalize_np(base[1])
    R = np.zeros((V_ROLES, n_dim), dtype=np.float32)
    cluster_assignment = [0, 0, 0, 1, 1, 1]
    for i in range(V_ROLES):
        c = cluster_assignment[i]
        noise = g.standard_normal(size=n_dim).astype(np.float32)
        # Project noise off both base vectors -> stays orthogonal to both clusters
        noise = noise - (base[0] @ noise) * base[0]
        noise = noise - (base[1] @ noise) * base[1]
        noise = _l2_normalize_np(noise)
        v = cluster_overlap * base[c] + (1.0 - cluster_overlap) * noise
        R[i] = _l2_normalize_np(v)
    return R


# ============================================================================
# Concept encoder (anisotropic per Cell D for HYBRID arm)
# ============================================================================

def concept_encoder_random(n_dim: int, g: np.random.Generator) -> np.ndarray:
    return bipolar_random(V_INSTANCES, n_dim, g)


def concept_encoder_label_driven(n_dim: int, g: np.random.Generator,
                                    within_cat_spread: float = 0.5) -> np.ndarray:
    """Gram-Schmidt category basis + within-cat variation (a la Cell D)."""
    raw = g.standard_normal(size=(V_CATEGORIES, n_dim)).astype(np.float32)
    B = np.zeros_like(raw)
    for i in range(V_CATEGORIES):
        v = raw[i].copy()
        for j in range(i):
            v = v - (B[j] @ v) * B[j]
        nm = np.linalg.norm(v)
        if nm < 1e-9:
            v = raw[i].copy()
            nm = np.linalg.norm(v) + 1e-12
        B[i] = v / nm
    E = np.zeros((V_INSTANCES, n_dim), dtype=np.float32)
    for i in range(V_INSTANCES):
        c = _category_of(i)
        side = g.standard_normal(size=n_dim).astype(np.float32)
        for j in range(V_CATEGORIES):
            side = side - (B[j] @ side) * B[j]
        nm = np.linalg.norm(side)
        if nm > 1e-9:
            side = side / nm
        v = B[c] + within_cat_spread * side
        E[i] = v
    return _l2_normalize_np(E)


# ============================================================================
# Training-graph construction
# ============================================================================

def build_training_graph(g: np.random.Generator, heldout_instances: List[int]
                          ) -> Tuple[List[Tuple[int, int, int]],
                                      List[Tuple[int, int]],
                                      Dict[int, int]]:
    """Build training KG.

    For each TRAINED instance i:
      - (i, R_subj_of, action_for_category_of(i))
      - For some i: also (i, R_property_of, attribute) to give substrate richer structure.
    For each HELDOUT instance h:
      - ONLY (h, is_a, category) atom -- NEVER under R_subj_of.

    Returns:
      role_triples: List of (instance, R_role_idx, action_idx) -- the role-tagged training.
      isa_pairs:    List of (heldout_instance, category_idx) -- the is_a label-only training.
      cat_action:   Mapping category -> canonical action index (so substrate has a clear target).
    """
    # canonical action per category: cat c -> action c (% V_PREDICATES)
    cat_action = {c: c % V_PREDICATES for c in range(V_CATEGORIES)}
    role_triples: List[Tuple[int, int, int]] = []
    isa_pairs: List[Tuple[int, int]] = []
    R_subj = 0   # role index 0 = R_subj_of
    R_prop = 2   # role index 2 = R_property_of
    # All trained instances get R_subj_of binding to their cat's action
    for i in range(V_INSTANCES):
        if i in heldout_instances:
            isa_pairs.append((i, _category_of(i)))
            continue
        c = _category_of(i)
        a = cat_action[c]
        role_triples.append((i, R_subj, a))
        # 50% also get a property binding for richer training
        if g.random() < 0.5:
            attr_idx = (c + i) % V_PREDICATES  # uses predicate-space as attribute-space for simplicity
            role_triples.append((i, R_prop, attr_idx))
    return role_triples, isa_pairs, cat_action


# ============================================================================
# Substrate: ingest + query
# ============================================================================

def ingest_no_roles(role_triples, isa_pairs, E_inst, R_action, E_category, n_dim):
    """ARM_NO_ROLES: store role-triples as raw (s, p, o) Hebbian without role-binding.

    src = E_inst[s] * E_action[p] (rank-1 Hebb)
    tgt = E_action[o]   -- but for is_a pairs, tgt = E_category[c].

    For simplicity in NO_ROLES baseline, every triple becomes (s, p=R_role_idx_used_directly, o).
    Substrate uses E_inst[s] directly as src (no role binding); W = sum outer(target, src).
    For is_a pairs: tgt = E_category[c], src = E_inst[h].

    Query at retrieval: pred = E_inst[query_s] @ W.T; return argmax over action+category space.
    """
    sq = math.sqrt(n_dim)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    # For role triples: src = E_inst[s] (no role binding); tgt = E_action[action_o].
    for (s, r, a) in role_triples:
        src = E_inst[s] * sq
        tgt = E_action[a]
        W += np.outer(tgt, src) / n_dim
    for (h, c) in isa_pairs:
        src = E_inst[h] * sq
        tgt = E_category[c]
        W += np.outer(tgt, src) / n_dim
    return W


def ingest_role_orthogonal(role_triples, isa_pairs, E_inst, R_role, E_action,
                              E_category, R_isa, n_dim):
    """ARM_ROLES_ORTHOGONAL_RANDOM and ARM_ROLES_SEMANTICALLY_CLUSTERED:
    src = bind(E_inst[s], R_role[r]); tgt = E_action[a].
    For is_a: src = bind(E_inst[h], R_isa); tgt = E_category[c].
    """
    sq = math.sqrt(n_dim)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for (s, r, a) in role_triples:
        key = hrr_bind(E_inst[s], R_role[r]) * sq
        tgt = E_action[a]
        W += np.outer(tgt, key) / n_dim
    for (h, c) in isa_pairs:
        key = hrr_bind(E_inst[h], R_isa) * sq
        tgt = E_category[c]
        W += np.outer(tgt, key) / n_dim
    return W


def ingest_grammatical(role_triples, isa_pairs, E_inst, R_role, E_action,
                          E_category, R_isa, n_dim):
    """ARM_GRAMMATICAL_ROLE_BINDING: store FULL triple as bind(subj, R_subj) + bind(R_verb, action).

    For (i, R_subj, a) train atom:
      key = bind(E_inst[i], R_role[R_subj])
      structural_pack = bind(R_role[R_verb_pos=R_pos1], E_action[a])  # encode the action with a 'verb' role
      We store: W += outer(tgt_action_a, key)   -- same as orthogonal arm for retrieval.
      AND     W += outer(E_action[a], structural_pack)  -- creates a second associative path.

    The intention: substrate has TWO paths to retrieve action for a heldout subject:
      (1) direct: query (h, R_subj) -> if heldout shares category with trained, lift.
      (2) via verb-role: if structural_pack atoms accumulate per category, they reinforce.
    """
    sq = math.sqrt(n_dim)
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    R_verb = 3  # use R_pos1 as 'verb role' slot
    for (s, r, a) in role_triples:
        key = hrr_bind(E_inst[s], R_role[r]) * sq
        tgt = E_action[a]
        W += np.outer(tgt, key) / n_dim
        # Structural verb-role binding (only for R_subj triples)
        if r == 0:
            verb_pack = hrr_bind(R_role[R_verb], E_action[a]) * sq
            # Tie action to verb_pack via outer
            W += 0.5 * np.outer(tgt, verb_pack) / n_dim
    for (h, c) in isa_pairs:
        key = hrr_bind(E_inst[h], R_isa) * sq
        tgt = E_category[c]
        W += np.outer(tgt, key) / n_dim
    return W


def query_arm_no_roles(W, E_inst, E_action, query_instance: int, n_dim: int) -> int:
    sq = math.sqrt(n_dim)
    src = E_inst[query_instance] * sq
    pred = W @ src
    scores = E_action @ pred
    return int(scores.argmax())


def query_arm_with_roles(W, E_inst, R_role, E_action, query_instance: int,
                            role_idx: int, n_dim: int) -> int:
    sq = math.sqrt(n_dim)
    key = hrr_bind(E_inst[query_instance], R_role[role_idx]) * sq
    pred = W @ key
    scores = E_action @ pred
    return int(scores.argmax())


# ============================================================================
# Arm runners
# ============================================================================

def run_arm_no_roles(seed, heldout, cat_action) -> Dict[str, Any]:
    g = np.random.default_rng(seed * 2 + 1)
    E_inst = concept_encoder_random(N_DIM, g)
    E_action = bipolar_random(V_PREDICATES, N_DIM, g)
    E_cat = bipolar_random(V_CATEGORIES, N_DIM, g)
    role_triples, isa_pairs, _ = build_training_graph(g, heldout)
    W = ingest_no_roles(role_triples, isa_pairs, E_inst, E_action, E_cat, N_DIM)
    # Eval: trained-instance R_subj_of recovery + heldout R_subj_of generalization
    trained = [i for i in range(V_INSTANCES) if i not in heldout]
    train_hits = 0
    for i in trained:
        a_true = cat_action[_category_of(i)]
        a_pred = query_arm_no_roles(W, E_inst, E_action, i, N_DIM)
        if a_pred == a_true:
            train_hits += 1
    train_top1 = train_hits / max(len(trained), 1)
    held_hits = 0
    for h in heldout:
        a_true = cat_action[_category_of(h)]
        a_pred = query_arm_no_roles(W, E_inst, E_action, h, N_DIM)
        if a_pred == a_true:
            held_hits += 1
    held_top1 = held_hits / max(len(heldout), 1)
    return {"trained_top1": round(train_top1, 4),
            "heldout_top1": round(held_top1, 4),
            "n_trained": len(trained), "n_heldout": len(heldout)}


def run_arm_role(arm_label: str, seed: int, heldout, cat_action) -> Dict[str, Any]:
    g = np.random.default_rng(seed * 2 + 1)
    if arm_label == "ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS":
        E_inst = concept_encoder_label_driven(N_DIM, g)
    else:
        E_inst = concept_encoder_random(N_DIM, g)
    E_action = bipolar_random(V_PREDICATES, N_DIM, g)
    E_cat = bipolar_random(V_CATEGORIES, N_DIM, g)

    if arm_label == "ARM_ROLES_SEMANTICALLY_CLUSTERED":
        R_role = role_codebook_semantically_clustered(N_DIM, g)
    else:
        R_role = role_codebook_orthogonal_random(N_DIM, g)
    R_isa = bipolar_random(1, N_DIM, g)[0]

    role_triples, isa_pairs, _ = build_training_graph(g, heldout)
    if arm_label == "ARM_GRAMMATICAL_ROLE_BINDING" or arm_label == "ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS":
        W = ingest_grammatical(role_triples, isa_pairs, E_inst, R_role, E_action,
                                E_cat, R_isa, N_DIM)
    else:
        W = ingest_role_orthogonal(role_triples, isa_pairs, E_inst, R_role, E_action,
                                     E_cat, R_isa, N_DIM)

    # Eval
    trained = [i for i in range(V_INSTANCES) if i not in heldout]
    R_SUBJ = 0
    train_hits = 0
    for i in trained:
        a_true = cat_action[_category_of(i)]
        a_pred = query_arm_with_roles(W, E_inst, R_role, E_action, i, R_SUBJ, N_DIM)
        if a_pred == a_true:
            train_hits += 1
    train_top1 = train_hits / max(len(trained), 1)
    held_hits = 0
    held_top3 = 0
    for h in heldout:
        a_true = cat_action[_category_of(h)]
        sq = math.sqrt(N_DIM)
        key = hrr_bind(E_inst[h], R_role[R_SUBJ]) * sq
        pred = W @ key
        scores = E_action @ pred
        a_pred = int(scores.argmax())
        if a_pred == a_true:
            held_hits += 1
        top3 = set(np.argpartition(scores, -3)[-3:].tolist())
        if a_true in top3:
            held_top3 += 1
    held_top1 = held_hits / max(len(heldout), 1)
    held_top3_acc = held_top3 / max(len(heldout), 1)
    return {"trained_top1": round(train_top1, 4),
            "heldout_top1": round(held_top1, 4),
            "heldout_top3": round(held_top3_acc, 4),
            "n_trained": len(trained), "n_heldout": len(heldout),
            "role_inner_products": _role_inner_products_summary(R_role)}


def _role_inner_products_summary(R_role: np.ndarray) -> Dict[str, float]:
    """Reported for arm-vs-arm comparison: are roles really clustered?"""
    G = R_role @ R_role.T
    # Cluster A = (R_subj, R_obj, R_property) = indices 0,1,2
    # Cluster B = (R_pos1, R_pos2, R_pos3) = indices 3,4,5
    within_a = [G[i, j] for i in [0, 1, 2] for j in [0, 1, 2] if i != j]
    within_b = [G[i, j] for i in [3, 4, 5] for j in [3, 4, 5] if i != j]
    cross = [G[i, j] for i in [0, 1, 2] for j in [3, 4, 5]]
    return {"mean_within_cluster_A": round(float(np.mean(within_a)), 4),
            "mean_within_cluster_B": round(float(np.mean(within_b)), 4),
            "mean_cross_cluster": round(float(np.mean(cross)), 4)}


# ============================================================================
# Self-test
# ============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)
    # Use n=2048 for selftest so GS-orthogonal sparse codebook (sparse_f=0.02 -> k=41)
    # doesn't degenerate (at n=256 + sparse_f=0.02 -> only k=5 entries, GS goes degenerate).
    n = 2048
    # Role codebooks
    R1 = role_codebook_orthogonal_random(n, g)
    G1 = R1 @ R1.T
    off1 = G1 - np.eye(V_ROLES)
    # GS over sparse bipolar isn't perfectly orthogonal; tolerance 0.4 is generous
    # for production N=8192, but at n=2048 we may see slightly larger residuals.
    assert float(np.abs(off1).max()) < 0.5, "orthogonal codebook poor (n=%d): max_off=%.3f" % (
        n, float(np.abs(off1).max()))
    R2 = role_codebook_semantically_clustered(n, g, cluster_overlap=0.7)
    # Check clustering: within-A mean > cross-A-to-B mean
    s = _role_inner_products_summary(R2)
    assert s["mean_within_cluster_A"] > s["mean_cross_cluster"], \
        "cluster A not above cross: %s" % s
    # Encoder shapes
    E1 = concept_encoder_random(n, g)
    assert E1.shape == (V_INSTANCES, n)
    E2 = concept_encoder_label_driven(n, g)
    assert E2.shape == (V_INSTANCES, n)
    # HRR bind preserves shape
    bound = hrr_bind(E1[0], R1[0])
    assert bound.shape == (n,)
    # End-to-end: ingest + query small
    heldout = [0, 8, 16, 24]
    cat_action = {c: c % V_PREDICATES for c in range(V_CATEGORIES)}
    g2 = np.random.default_rng(0)
    role_triples, isa_pairs, _ = build_training_graph(g2, heldout)
    E_action = bipolar_random(V_PREDICATES, n, g2)
    E_cat = bipolar_random(V_CATEGORIES, n, g2)
    R_isa = bipolar_random(1, n, g2)[0]
    W = ingest_role_orthogonal(role_triples, isa_pairs, E1, R1, E_action, E_cat, R_isa, n)
    assert W.shape == (n, n)
    # Query a trained subject
    trained = [i for i in range(V_INSTANCES) if i not in heldout][0]
    a_pred = query_arm_with_roles(W, E1, R1, E_action, trained, 0, n)
    assert 0 <= a_pred < V_PREDICATES
    print("[selftest] PASS role_codebook_ok clustering={A=%.3f B=%.3f X=%.3f} encoder_ok ingest_ok query_ok"
          % (s["mean_within_cluster_A"], s["mean_within_cluster_B"], s["mean_cross_cluster"]),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] passed; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    # Heldout: 2 per category
    heldout: List[int] = []
    for c in range(V_CATEGORIES):
        start = c * V_INSTANCES_PER_CAT
        # take first 2 instances of each cat as heldout (deterministic per seed via permute)
        perm = g.permutation(V_INSTANCES_PER_CAT)
        heldout.extend([start + int(perm[0]), start + int(perm[1])])
    cat_action = {c: c % V_PREDICATES for c in range(V_CATEGORIES)}
    print("[seed=%d] N=%d V_inst=%d V_roles=%d heldout=%s" % (
        seed, N_DIM, V_INSTANCES, V_ROLES, heldout), flush=True)

    out = {"seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
           "config_version": CONFIG_VERSION,
           "heldout_instances": heldout,
           "cat_action_map": {str(c): int(a) for c, a in cat_action.items()}}
    arms_data: Dict[str, Any] = {}
    # ARM_NO_ROLES
    t0 = time.time()
    r = run_arm_no_roles(seed, heldout, cat_action)
    r["elapsed_s_arm"] = round(time.time() - t0, 2)
    arms_data["ARM_NO_ROLES"] = r
    print("  [seed=%d arm=ARM_NO_ROLES] train_top1=%.3f heldout_top1=%.3f" % (
        seed, r["trained_top1"], r["heldout_top1"]), flush=True)
    # Role arms
    for arm in ARMS:
        if arm == "ARM_NO_ROLES":
            continue
        t0 = time.time()
        r = run_arm_role(arm, seed, heldout, cat_action)
        r["elapsed_s_arm"] = round(time.time() - t0, 2)
        arms_data[arm] = r
        print("  [seed=%d arm=%s] train_top1=%.3f heldout_top1=%.3f top3=%.3f roles={A=%.3f B=%.3f X=%.3f}" % (
            seed, arm, r["trained_top1"], r["heldout_top1"], r["heldout_top3"],
            r["role_inner_products"]["mean_within_cluster_A"],
            r["role_inner_products"]["mean_within_cluster_B"],
            r["role_inner_products"]["mean_cross_cluster"]), flush=True)
    out["arms"] = arms_data
    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_held_top1(arm: str) -> Tuple[float, float]:
        vals = [p["arms"][arm]["heldout_top1"] for p in per_seed if arm in p["arms"]]
        if not vals:
            return float("nan"), float("nan")
        m = float(np.mean(vals))
        cv = float(np.std(vals) / max(m, 1e-9))
        return m, cv

    arm_metrics = {a: arm_held_top1(a) for a in ARMS}
    no_roles, no_roles_cv = arm_metrics["ARM_NO_ROLES"]
    role_arms = {k: v for k, v in arm_metrics.items() if k != "ARM_NO_ROLES"}
    best_label, (best_top1, best_cv) = max(role_arms.items(), key=lambda kv: kv[1][0])
    lift = best_top1 - no_roles

    train_min = min(p["arms"]["ARM_NO_ROLES"]["trained_top1"] for p in per_seed)

    chance = 1.0 / V_PREDICATES
    rails: List[str] = []
    if train_min < 0.70:
        rails.append("STORAGE_PRIMITIVE_WEAK(no_roles_train_min=%.3f < 0.70)" % train_min)
    if best_top1 - chance < 0.02:
        rails.append("AT_CHANCE(best=%.3f vs chance=%.3f)" % (best_top1, chance))

    # Discriminator: orthogonal vs clustered
    ortho_top1 = arm_metrics["ARM_ROLES_ORTHOGONAL_RANDOM"][0]
    clust_top1 = arm_metrics["ARM_ROLES_SEMANTICALLY_CLUSTERED"][0]
    cluster_discriminator = clust_top1 - ortho_top1

    summ = ("NO_ROLES=%.3f | ORTHO=%.3f | CLUSTERED=%.3f | GRAMMATICAL=%.3f | HYBRID=%.3f "
            "| best=%s(%.3f cv=%.3f) | lift_vs_no_roles=%.3f "
            "| clustered_vs_ortho=%.3f | train_no_roles=%.3f chance=%.3f rails=%s") % (
        no_roles, arm_metrics["ARM_ROLES_ORTHOGONAL_RANDOM"][0],
        arm_metrics["ARM_ROLES_SEMANTICALLY_CLUSTERED"][0],
        arm_metrics["ARM_GRAMMATICAL_ROLE_BINDING"][0],
        arm_metrics["ARM_HYBRID_ROLE_PLUS_CONCEPT_LABELS"][0],
        best_label, best_top1, best_cv, lift, cluster_discriminator,
        train_min, chance, rails)

    if best_top1 >= HP_CHAIN_GRADE_TOP1 and lift >= HP_CHAIN_GRADE_LIFT and best_cv <= HP_CV:
        return "HARD_PASS_CHAIN_GRADE", "HARD_PASS_CHAIN_GRADE: " + summ
    if best_top1 >= HP_TOP1 and lift >= HP_LIFT:
        return "HARD_PASS", "HARD_PASS: " + summ
    # HARD_FAIL: all role arms within +/- HF_TOL of no_roles
    if all(abs(v[0] - no_roles) <= HF_TOL for v in role_arms.values()):
        return "HARD_FAIL", "HARD_FAIL: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND: " + summ


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
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "DESIGN_NOTE": ("USER course-correction 2026-06-24 (Cell B redirect): "
                         "compositional generalization (heldout subject in known "
                         "role) on substrate-native concept-KG. NOT text8. "
                         "Lane 1; ARM_NO_ROLES baseline + 4 role variants; "
                         "discriminator = orthogonal vs semantically-clustered roles."),
    }
    write_metrics(out_dir, metrics, results=per_seed)
