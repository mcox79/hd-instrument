"""substrate_label_driven_anisotropic_encoder_v1 -- USER directive (Barrier 4 alt).

Construct anisotropy directly from concept-KG labels instead of learning it
unsupervised (hub-spoke v3 path). Substrate encoder is the load-bearing
bottleneck; if labels exist, USE them.

Arms (4):
  ARM_RANDOM_BIPOLAR_BASELINE      isotropic control (no label info).
  ARM_LABEL_DRIVEN_AXIS_PROJECTION concept embeddings in category-subspace + noise.
  ARM_LABEL_DRIVEN_GRAM_SCHMIDT    orthonormal cat-basis; concepts = linear combos.
  ARM_HUB_SPOKE_LABEL_BASELINE     concept = hub_cat + spoke_inst (sum).

Tasks A1-A6 (mini SEMANTIC battery):
  A1 1hop recall, A2 within-cat discrimination, A3 heldout-concept generalization,
  A4 compositional s+p generalization, A5 cross-cat structural sanity (FLOOR),
  A6 untaught predicate sanity (FLOOR).

Bands:
  HP_CHAIN_GRADE: best LABEL_DRIVEN A3 >= 0.85 AND A4 >= 0.50 AND beats RANDOM
                  by >= 0.15 on either.
  HP:             best LABEL_DRIVEN A3 >= 0.70 AND beats RANDOM by >= 0.10 on A3.
  HARD_FAIL:      ALL label arms <= RANDOM on both A3 and A4.

Verify-referent:
  - concept_kg_storage_retrieval_v1 verdict=MIDDLE_BAND (NOT chain-grade);
    USER citation of "top1=1.0" is from SEMANTIC battery, not concept_kg.
    Flagged. We use the A3/A4 task SHAPE as evaluator, not its claimed verdict.

ASCII only; pure numpy; per-seed checkpoint; atexit synthesizer.
"""
from __future__ import annotations

import argparse
import atexit
import json
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

ANCHOR_NAME = "substrate_label_driven_anisotropic_encoder_v1"

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

# Pre-reg HARD bands
HP_CHAIN_GRADE_A3 = 0.85
HP_CHAIN_GRADE_A4 = 0.50
HP_CHAIN_GRADE_LIFT = 0.15
HP_A3 = 0.70
HP_A3_LIFT = 0.10
# HARD_FAIL: all label arms <= random on BOTH A3 and A4
A5_SANITY_TOP1 = 0.20
A6_SANITY_TOP5 = 0.30
RANDOM_A3_BAND_LO = 0.30
RANDOM_A3_BAND_HI = 0.95

if RUN_MODE == "smoke":
    N_DIM = 1024
    SEEDS = [7]
    M_TRAIN = 80
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23]
    M_TRAIN = 300

V_CATEGORIES = 4
V_CONCEPTS_PER_CAT = 3
V_CONCEPTS = V_CATEGORIES * V_CONCEPTS_PER_CAT   # 12
V_PREDICATES = 6
N_HELDOUT_CONCEPTS = 2

CONFIG_VERSION = (
    "sublabAnis-v1: random vs axis-proj vs gram-schmidt vs hub-spoke; "
    "V_C=%d (cat=%d x %d) V_P=%d M=%d N=%d seeds=%s mode=%s; "
    "bands HP_CG_A3=%.2f HP_CG_A4=%.2f HP_lift=%.2f HP_A3=%.2f HP_A3_lift=%.2f"
) % (
    V_CONCEPTS, V_CATEGORIES, V_CONCEPTS_PER_CAT, V_PREDICATES, M_TRAIN, N_DIM,
    SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_A3, HP_CHAIN_GRADE_A4, HP_CHAIN_GRADE_LIFT, HP_A3, HP_A3_LIFT,
)


def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def bipolar_random(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return _l2_normalize_np(X)


def _category_of(concept_idx: int) -> int:
    return concept_idx // V_CONCEPTS_PER_CAT


# ============================================================================
# Encoder constructions
# ============================================================================

def encoder_random_bipolar(n_dim: int, g: np.random.Generator) -> np.ndarray:
    """Isotropic dense bipolar baseline."""
    return bipolar_random(V_CONCEPTS, n_dim, g)


def encoder_axis_projection(n_dim: int, g: np.random.Generator,
                              noise_scale: float = 0.05) -> np.ndarray:
    """Concept embeddings live in category-subspace.

    Allocate n_dim into V_CATEGORIES contiguous bands; each concept_i in category c
    has non-zero entries ONLY in band(c) (random bipolar within), plus small
    global noise everywhere.
    """
    band_size = n_dim // V_CATEGORIES
    E = np.zeros((V_CONCEPTS, n_dim), dtype=np.float32)
    # global noise
    noise = (g.integers(0, 2, size=(V_CONCEPTS, n_dim)) * 2 - 1).astype(np.float32) * noise_scale
    for i in range(V_CONCEPTS):
        c = _category_of(i)
        lo = c * band_size
        hi = lo + band_size
        E[i, lo:hi] = (g.integers(0, 2, size=band_size) * 2 - 1).astype(np.float32)
    E = E + noise
    return _l2_normalize_np(E)


def encoder_gram_schmidt(n_dim: int, g: np.random.Generator,
                           within_cat_spread: float = 0.5) -> np.ndarray:
    """Build orthonormal category basis B[V_CAT, n_dim]; each concept_i = linear
    combination of B[cat(i)] plus a small within-category variation vector.
    """
    # Build V_CATEGORIES random vectors then GS orthonormalize
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
    # Concepts: each = unit-mix of category-basis + within-cat random variation
    E = np.zeros((V_CONCEPTS, n_dim), dtype=np.float32)
    for i in range(V_CONCEPTS):
        c = _category_of(i)
        # within-cat: random unit-norm orthogonal to B[c], scaled by within_cat_spread
        side = g.standard_normal(size=n_dim).astype(np.float32)
        # project off all category basis vectors -> stay in the V-dim subspace EXCEPT B[c]'s axis
        for j in range(V_CATEGORIES):
            side = side - (B[j] @ side) * B[j]
        side_nm = np.linalg.norm(side)
        if side_nm > 1e-9:
            side = side / side_nm
        # main + side (controlled mix)
        v = B[c] + within_cat_spread * side
        E[i] = v
    return _l2_normalize_np(E)


def encoder_hub_spoke(n_dim: int, g: np.random.Generator) -> np.ndarray:
    """concept_i = hub_cat(i) + spoke_inst(i). Both random bipolar; sum (NOT bind)."""
    hubs = bipolar_random(V_CATEGORIES, n_dim, g)
    spokes = bipolar_random(V_CONCEPTS, n_dim, g)
    E = np.zeros((V_CONCEPTS, n_dim), dtype=np.float32)
    for i in range(V_CONCEPTS):
        c = _category_of(i)
        E[i] = hubs[c] + spokes[i]
    return _l2_normalize_np(E)


# ============================================================================
# KG construction + tasks
# ============================================================================

def make_train_kg(M: int, g: np.random.Generator,
                   heldout_concepts: List[int]) -> List[Tuple[int, int, int]]:
    """Make M (s, p, o) triples. SKIP heldout concepts entirely from train."""
    eligible = [c for c in range(V_CONCEPTS) if c not in heldout_concepts]
    triples: List[Tuple[int, int, int]] = []
    for _ in range(M):
        s = int(g.choice(eligible))
        p = int(g.integers(0, V_PREDICATES))
        o = int(g.choice(eligible))
        triples.append((s, p, o))
    return triples


def ingest_W(triples, E, R, n_dim, batch: int = 1024) -> np.ndarray:
    sq = math.sqrt(n_dim)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def scores(E, W, keys):
    if keys.shape[0] == 0:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    return (E @ (W @ keys.T)).T


def build_keys_arr(E, R, sp_pairs, n_dim):
    if not sp_pairs:
        return np.zeros((0, n_dim), dtype=np.float32)
    sq = math.sqrt(n_dim)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    return (E[s] * R[p] * sq).astype(np.float32)


def task_a1_1hop_recall(E, R, W, triples, n_dim):
    """Recall@1 on training (s, p, ?)."""
    sp = [(s, p) for (s, p, _) in triples]
    keys = build_keys_arr(E, R, sp, n_dim)
    S = scores(E, W, keys)
    o_true = np.array([o for (_, _, o) in triples])
    top1 = float((S.argmax(axis=1) == o_true).mean())
    top5 = float(np.mean([o_true[j] in set(np.argpartition(S[j], -5)[-5:].tolist())
                          for j in range(len(triples))]))
    return {"top1": round(top1, 4), "top5": round(top5, 4), "n": len(triples)}


def task_a2_within_cat_discrimination(E, R, W, triples, n_dim, g):
    """For each train triple (s,p,o), check whether substrate prefers o over OTHER
    instances of the SAME category as o. Pure encoder anisotropy test.
    """
    if not triples:
        return {"top1": float("nan"), "n": 0}
    sp = [(s, p) for (s, p, _) in triples]
    keys = build_keys_arr(E, R, sp, n_dim)
    S = scores(E, W, keys)
    hits = 0; total = 0
    for j, (s, p, o) in enumerate(triples):
        c = _category_of(o)
        siblings = [k for k in range(V_CONCEPTS) if _category_of(k) == c]
        if len(siblings) < 2:
            continue
        # top1 over sibling restriction
        sub_scores = S[j, siblings]
        am = siblings[int(np.argmax(sub_scores))]
        if am == o:
            hits += 1
        total += 1
    return {"top1": round(hits / max(total, 1), 4), "n": total}


def task_a3_heldout_generalization(E, R, W, triples_train, heldout_concepts, n_dim, g):
    """For each heldout concept h: pick a predicate p that appears in training,
    ask (h, p, ?). Substrate should structurally prefer concepts SHARING category
    of h's typical training partners. We measure top5_in_correct_category as the
    PRIMARY metric (structural generalization).
    """
    if not heldout_concepts:
        return {"top1": float("nan"), "top5_in_cat": float("nan"), "n": 0}
    predicates_used = sorted({p for (_, p, _) in triples_train})
    hits_top5_cat = 0; total = 0
    top1_hits = 0
    for h in heldout_concepts:
        for p in predicates_used:
            keys = build_keys_arr(E, R, [(h, p)], n_dim)
            S = scores(E, W, keys)[0]
            top5 = set(np.argpartition(S, -5)[-5:].tolist())
            # Category preference: count whether ANY top5 result is in same category as h
            same_cat_top5 = any(_category_of(k) == _category_of(h) for k in top5)
            if same_cat_top5:
                hits_top5_cat += 1
            # top1 sanity: did argmax come from same category as h?
            if _category_of(int(S.argmax())) == _category_of(h):
                top1_hits += 1
            total += 1
    return {"top1": round(top1_hits / max(total, 1), 4),
            "top5_in_cat": round(hits_top5_cat / max(total, 1), 4),
            "n": total}


def task_a4_compositional(E, R, W, triples_train, n_dim):
    """For (s,p) NEVER seen as combo in train (but s and p individually seen):
    substrate should return some unstored o; measure top5_in_same_cat_as_typical_o.
    """
    seen_sp = set((s, p) for (s, p, _) in triples_train)
    typical_o_cat: Dict[int, List[int]] = {}
    for (s, p, o) in triples_train:
        typical_o_cat.setdefault(p, []).append(_category_of(o))
    unseen_sp: List[Tuple[int, int]] = []
    all_s = sorted({s for (s, _, _) in triples_train})
    all_p = sorted({p for (_, p, _) in triples_train})
    for s in all_s:
        for p in all_p:
            if (s, p) not in seen_sp:
                unseen_sp.append((s, p))
    if not unseen_sp:
        return {"top5_in_typical_cat": float("nan"), "n": 0}
    hits = 0; total = 0
    for (s, p) in unseen_sp[:80]:   # cap eval
        if p not in typical_o_cat:
            continue
        keys = build_keys_arr(E, R, [(s, p)], n_dim)
        S = scores(E, W, keys)[0]
        top5 = set(np.argpartition(S, -5)[-5:].tolist())
        typical = set(typical_o_cat[p])
        if any(_category_of(k) in typical for k in top5):
            hits += 1
        total += 1
    return {"top5_in_typical_cat": round(hits / max(total, 1), 4), "n": total}


def task_a5_cross_cat_sanity(E, R, W, triples_train, n_dim):
    """For each (s,p,o) in train: ASK (s, p_NEW, ?) where p_NEW was never used
    with s. Substrate should NOT confidently retrieve any trained o.
    top1 on substrate output -- want LOW (close to chance).
    """
    seen_sp = set((s, p) for (s, p, _) in triples_train)
    if not seen_sp:
        return {"top1": float("nan"), "top5": float("nan"), "n": 0}
    by_s: Dict[int, set] = {}
    for (s, p, _) in triples_train:
        by_s.setdefault(s, set()).add(p)
    test_pairs: List[Tuple[int, int]] = []
    for s, used_ps in by_s.items():
        unused = [p for p in range(V_PREDICATES) if p not in used_ps]
        if unused:
            test_pairs.append((s, unused[0]))
    if not test_pairs:
        return {"top1": float("nan"), "top5": float("nan"), "n": 0}
    keys = build_keys_arr(E, R, test_pairs, n_dim)
    S = scores(E, W, keys)
    chance = 1.0 / V_CONCEPTS
    # Substrate should look "random" -- mean argmax frequency on trained tail concepts low
    # We report top1_random_rate: how often argmax lands on a CONCEPT that was actually
    # trained as o for that s under SOME predicate (a false retrieval).
    trained_o_for_s: Dict[int, set] = {}
    for (s, _, o) in triples_train:
        trained_o_for_s.setdefault(s, set()).add(o)
    bad_hits = 0; bad_top5 = 0
    for j, (s, p) in enumerate(test_pairs):
        am = int(S[j].argmax())
        top5 = set(np.argpartition(S[j], -5)[-5:].tolist())
        if am in trained_o_for_s.get(s, set()):
            bad_hits += 1
        if top5 & trained_o_for_s.get(s, set()):
            bad_top5 += 1
    return {"top1": round(bad_hits / len(test_pairs), 4),
            "top5": round(bad_top5 / len(test_pairs), 4),
            "n": len(test_pairs)}


def task_a6_untaught_predicate(E, R, W, triples_train, n_dim, g):
    """Build a NEW predicate vector R_new NOT used in train. Ask (s, R_new, ?) for
    each train s. Want top5 distribution near chance (no spurious retrieval).
    """
    used_p = sorted({p for (_, p, _) in triples_train})
    new_p_idx = V_PREDICATES + 0
    # Build a fresh R atom not in R
    R_new = bipolar_random(1, n_dim, g)[0]
    R_extended = np.concatenate([R, R_new[None, :]], axis=0).astype(np.float32)
    all_s = sorted({s for (s, _, _) in triples_train})
    if not all_s:
        return {"top5_overlap_trained_o": float("nan"), "n": 0}
    test_pairs = [(s, new_p_idx) for s in all_s]
    keys = build_keys_arr(E, R_extended, test_pairs, n_dim)
    S = scores(E, W, keys)
    trained_o = {o for (_, _, o) in triples_train}
    bad = 0
    for j in range(len(test_pairs)):
        top5 = set(np.argpartition(S[j], -5)[-5:].tolist())
        if top5 & trained_o:
            bad += 1
    return {"top5_overlap_trained_o": round(bad / len(test_pairs), 4),
            "n": len(test_pairs)}


def _build_R(g, n_dim) -> np.ndarray:
    return bipolar_random(V_PREDICATES, n_dim, g)


def run_arm(arm_label: str, seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    heldout_concepts = list(g.permutation(V_CONCEPTS)[:N_HELDOUT_CONCEPTS])
    # Encoder
    if arm_label == "ARM_RANDOM_BIPOLAR_BASELINE":
        E = encoder_random_bipolar(N_DIM, g)
    elif arm_label == "ARM_LABEL_DRIVEN_AXIS_PROJECTION":
        E = encoder_axis_projection(N_DIM, g)
    elif arm_label == "ARM_LABEL_DRIVEN_GRAM_SCHMIDT":
        E = encoder_gram_schmidt(N_DIM, g)
    elif arm_label == "ARM_HUB_SPOKE_LABEL_BASELINE":
        E = encoder_hub_spoke(N_DIM, g)
    else:
        raise ValueError(arm_label)
    R = _build_R(g, N_DIM)
    triples = make_train_kg(M_TRAIN, g, heldout_concepts)
    W = ingest_W(triples, E, R, N_DIM)
    a1 = task_a1_1hop_recall(E, R, W, triples, N_DIM)
    a2 = task_a2_within_cat_discrimination(E, R, W, triples, N_DIM, g)
    a3 = task_a3_heldout_generalization(E, R, W, triples, heldout_concepts, N_DIM, g)
    a4 = task_a4_compositional(E, R, W, triples, N_DIM)
    a5 = task_a5_cross_cat_sanity(E, R, W, triples, N_DIM)
    a6 = task_a6_untaught_predicate(E, R, W, triples, N_DIM, g)
    return {"arm": arm_label, "seed": seed,
            "heldout_concepts": [int(x) for x in heldout_concepts],
            "a1": a1, "a2": a2, "a3": a3, "a4": a4, "a5": a5, "a6": a6}


def _selftest() -> None:
    """1-second mechanism check: each encoder gives valid V x N matrix, KG ingests, tasks run."""
    g = np.random.default_rng(0)
    n = 256
    for ctor in [encoder_random_bipolar, encoder_axis_projection,
                 encoder_gram_schmidt, encoder_hub_spoke]:
        E = ctor(n, g)
        assert E.shape == (V_CONCEPTS, n), "shape: %s" % str(E.shape)
        norms = np.linalg.norm(E, axis=1)
        assert all(abs(nm - 1.0) < 1e-3 for nm in norms), "%s norms: %s" % (ctor.__name__, norms)
    # ingest + tasks run on a tiny instance
    g = np.random.default_rng(1)
    E = encoder_gram_schmidt(n, g)
    R = bipolar_random(V_PREDICATES, n, g)
    heldout = [0, 1]
    triples = make_train_kg(50, g, heldout)
    W = ingest_W(triples, E, R, n)
    a1 = task_a1_1hop_recall(E, R, W, triples, n)
    a3 = task_a3_heldout_generalization(E, R, W, triples, heldout, n, g)
    assert 0.0 <= a1["top1"] <= 1.0
    assert 0.0 <= a3["top5_in_cat"] <= 1.0
    print("[selftest] PASS encoders=4 a1=%.3f a3_top5_in_cat=%.3f" % (
        a1["top1"], a3["top5_in_cat"]), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] passed; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    print("[seed=%d] N=%d V_C=%d V_cat=%d V_P=%d M=%d" % (
        seed, N_DIM, V_CONCEPTS, V_CATEGORIES, V_PREDICATES, M_TRAIN), flush=True)
    out = {"seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "M": M_TRAIN,
           "V_C": V_CONCEPTS, "V_cat": V_CATEGORIES, "V_P": V_PREDICATES,
           "config_version": CONFIG_VERSION}
    arms_data: Dict[str, Any] = {}
    for arm in ["ARM_RANDOM_BIPOLAR_BASELINE",
                "ARM_LABEL_DRIVEN_AXIS_PROJECTION",
                "ARM_LABEL_DRIVEN_GRAM_SCHMIDT",
                "ARM_HUB_SPOKE_LABEL_BASELINE"]:
        t_arm = time.time()
        r = run_arm(arm, seed)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        arms_data[arm] = r
        print("  [seed=%d arm=%s] a1=%.3f a3_top1=%.3f a3_top5_cat=%.3f a4=%.3f a5_top1=%.3f a6_top5=%.3f" % (
            seed, arm, r["a1"]["top1"], r["a3"]["top1"], r["a3"]["top5_in_cat"],
            r["a4"]["top5_in_typical_cat"], r["a5"]["top1"],
            r["a6"]["top5_overlap_trained_o"]), flush=True)
    out["arms"] = arms_data
    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_metric_mean(arm: str, key1: str, key2: str) -> float:
        vals = [p["arms"][arm][key1][key2] for p in per_seed if arm in p["arms"]]
        vals = [v for v in vals if isinstance(v, (int, float)) and not math.isnan(v)]
        if not vals:
            return float("nan")
        return float(np.mean(vals))

    random_a3 = arm_metric_mean("ARM_RANDOM_BIPOLAR_BASELINE", "a3", "top5_in_cat")
    random_a4 = arm_metric_mean("ARM_RANDOM_BIPOLAR_BASELINE", "a4", "top5_in_typical_cat")

    label_arms = {
        "AXIS_PROJ": ("ARM_LABEL_DRIVEN_AXIS_PROJECTION",
                      arm_metric_mean("ARM_LABEL_DRIVEN_AXIS_PROJECTION", "a3", "top5_in_cat"),
                      arm_metric_mean("ARM_LABEL_DRIVEN_AXIS_PROJECTION", "a4", "top5_in_typical_cat")),
        "GRAM_SCH":  ("ARM_LABEL_DRIVEN_GRAM_SCHMIDT",
                      arm_metric_mean("ARM_LABEL_DRIVEN_GRAM_SCHMIDT", "a3", "top5_in_cat"),
                      arm_metric_mean("ARM_LABEL_DRIVEN_GRAM_SCHMIDT", "a4", "top5_in_typical_cat")),
        "HUB_SPOKE": ("ARM_HUB_SPOKE_LABEL_BASELINE",
                      arm_metric_mean("ARM_HUB_SPOKE_LABEL_BASELINE", "a3", "top5_in_cat"),
                      arm_metric_mean("ARM_HUB_SPOKE_LABEL_BASELINE", "a4", "top5_in_typical_cat")),
    }
    label_driven = ["AXIS_PROJ", "GRAM_SCH"]
    # PRIMARY: best of axis_proj / gram_sch on A3
    best_label_label = max(label_driven, key=lambda k: label_arms[k][1] if not math.isnan(label_arms[k][1]) else -1.0)
    _, best_label_a3, best_label_a4 = label_arms[best_label_label]

    a5_max = max(p["arms"][a]["a5"]["top1"] for p in per_seed for a in p["arms"])
    a6_max = max(p["arms"][a]["a6"]["top5_overlap_trained_o"] for p in per_seed for a in p["arms"])

    rails: List[str] = []
    if not (RANDOM_A3_BAND_LO <= random_a3 <= RANDOM_A3_BAND_HI):
        rails.append("RANDOM_A3_OOB(%.3f not in [%.2f,%.2f])"
                     % (random_a3, RANDOM_A3_BAND_LO, RANDOM_A3_BAND_HI))
    if a5_max > A5_SANITY_TOP1:
        rails.append("A5_FLOOR_BUSTED(max=%.3f > %.2f)" % (a5_max, A5_SANITY_TOP1))
    if a6_max > A6_SANITY_TOP5:
        rails.append("A6_FLOOR_BUSTED(max=%.3f > %.2f)" % (a6_max, A6_SANITY_TOP5))

    chance = 1.0 / V_CONCEPTS
    summ = ("RANDOM: a3=%.3f a4=%.3f | AXIS: a3=%.3f a4=%.3f | GRAM_SCH: a3=%.3f a4=%.3f | "
            "HUB_SPOKE: a3=%.3f a4=%.3f | best_label=%s a3=%.3f a4=%.3f | "
            "lift_vs_random_a3=%.3f a4=%.3f | chance=%.3f a5_max=%.3f a6_max=%.3f rails=%s") % (
        random_a3, random_a4,
        label_arms["AXIS_PROJ"][1], label_arms["AXIS_PROJ"][2],
        label_arms["GRAM_SCH"][1], label_arms["GRAM_SCH"][2],
        label_arms["HUB_SPOKE"][1], label_arms["HUB_SPOKE"][2],
        best_label_label, best_label_a3, best_label_a4,
        best_label_a3 - random_a3, best_label_a4 - random_a4,
        chance, a5_max, a6_max, rails)

    lift_a3 = best_label_a3 - random_a3
    lift_a4 = best_label_a4 - random_a4

    if (best_label_a3 >= HP_CHAIN_GRADE_A3 and best_label_a4 >= HP_CHAIN_GRADE_A4
            and (lift_a3 >= HP_CHAIN_GRADE_LIFT or lift_a4 >= HP_CHAIN_GRADE_LIFT)):
        return "HARD_PASS_CHAIN_GRADE", "HARD_PASS_CHAIN_GRADE: " + summ
    if best_label_a3 >= HP_A3 and lift_a3 >= HP_A3_LIFT:
        return "HARD_PASS", "HARD_PASS: " + summ
    # HARD_FAIL: all label arms <= random on BOTH A3 and A4
    all_label_below = all(
        (label_arms[k][1] <= random_a3 + 1e-9 and label_arms[k][2] <= random_a4 + 1e-9)
        for k in label_arms
    )
    if all_label_below:
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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, CONFIG_VERSION), flush=True)
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
        "DESIGN_NOTE": ("USER directive 2026-06-24 (Barrier 4 alt): label-driven "
                         "anisotropic encoder construction; A1-A6 mini SEMANTIC "
                         "battery. Lane 1; random-bipolar isotropic baseline + "
                         "intra-arm sanity floors (A5, A6)."),
    }
    write_metrics(out_dir, metrics, results=per_seed)
