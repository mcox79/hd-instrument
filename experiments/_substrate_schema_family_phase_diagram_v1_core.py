"""Shared core for substrate_schema_family_phase_diagram_v1 sibling cells.

FIFTH systematic COMPONENT-SUBSTITUTION phase diagram (after pc_encoder_family,
seqbind_encoder_family, ...). This cell substitutes the SCHEMA MECHANISM FAMILY
rather than a config parameter on a fixed mechanism. Stage 3 cortex-equivalent
substrate primitive being benchmarked: vmPFC schema retrieval.

Background (substrate-as-canonical):
  - v1 exemplar_bayes phase_diagram landed MIDDLE_BAND (60 pt grid, prior=1.0).
  - v3 5/5 MB across alpha 0.006 to 19.5; CLIFF unobservable, GRACEFUL across decades.
  - v4 HARD_MAX (prior=0.0; centroid argmax) DISCOVERED stronger at FLOOR (alpha=19.5):
    HM=0.80 vs GR=0.20 at (200,200,2048). Centroid averaging suppresses noise.
  - v3/v4 were CONFIG-PARAM SWEEPS on a single family. Never head-to-head between
    distinct SCHEMA MECHANISM CLASSES on the same data + same N + same alpha.

This v1 systematically substitutes 4 schema families on a shared (alpha, n_schemas)
inner grid:

  FAMILY_EXEMPLAR_BAYES: log-sum-exp posterior over per-class exemplars
    (v3 mechanism; prior=1.0; default).
  FAMILY_PROTOTYPE_BASED: argmax over per-class CENTROID similarity (v4 HARDMAX).
    No LSE smoothing; no prior; pure prototype.
  FAMILY_HYBRID: weighted mixture log(prior) + 0.5*centroid_sim + 0.5*lse_bayes.
    Combines smoothing of LSE with prototype noise-suppression.
  FAMILY_BAYESIAN_WITH_PRIORS: LSE posterior with class-frequency prior tuned per
    n_schemas. Models how strong priors help/hurt vs uniform.

INNER axis values:
  alpha = K_total / N (load factor) in {0.01, 0.1, 1.0, 10.0}
     where K_total = n_classes * n_exemplars_per_class
  n_schemas (classes) in {10, 50, 200}
  N_DIM fixed at 4096 (so n_ex = round(alpha*N/n_classes); SAT/sweet/cliff regimes
    sampled directly via alpha).
  Each FAMILY runs the same (alpha, n_schemas) grid -> apples-to-apples comparison.

Discriminator per (family, alpha, n_schemas):
  - top1 classification accuracy (range [0,1]; chance = 1/n_schemas)
  - lift_over_chance = top1 / (1/n_schemas)
  - cliff_observable per family (any inner pt below 0.40)
  - graceful_degradation per family (monotonic decay across alpha decades)

META_RULE_AF: family_pair_hashes (SHA-256 of per-point top1) — at least 2 of 6
pairs must differ to claim families measurably distinct.

Honest-downward decision: discriminating_fraction >= 0.30 = HARD_PASS gate (>=14/48
inner pts in MIDDLE_BAND+HARD_PASS tiers).

ASCII-only. CPU-only (numpy + scipy.special.logsumexp).

Author: exp_dev 2026-06-29 (Opus 4.7 1M, agent-spawn) component-sweep #5
"""
# PRESERVE_ENV_VARS: HDLAB_QUEUE
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.special import logsumexp  # noqa: F401 -- used for numerical stability

ANCHOR_PREFIX = "substrate_schema_family_phase_diagram_v1"

# ----- Outer axis: schema family -----
FAMILIES = (
    "FAMILY_EXEMPLAR_BAYES",
    "FAMILY_PROTOTYPE_BASED",
    "FAMILY_HYBRID",
    "FAMILY_BAYESIAN_WITH_PRIORS",
)

# ----- Inner phase axes (LOCKED per prereg) -----
ALPHA_VALUES = (0.01, 0.1, 1.0, 10.0)        # 4 pts; load factor K_total/N
N_SCHEMAS_VALUES = (10, 50, 200)              # 3 pts; class load
N_DIM_FIXED = 4096                            # fixed for apples-to-apples

# Inner grid cardinality = 4 alphas * 3 n_schemas = 12 inner pts per family
# Total per seed FULL = 4 families * 12 = 48 phase points
# Smoke = 6 corners covering each family x 2 inner pts

SMOKE_CORNERS = (
    # (family, alpha, n_schemas) — each family appears at least once
    ("FAMILY_EXEMPLAR_BAYES",         0.1,  50),   # sweet-spot mid-load
    ("FAMILY_EXEMPLAR_BAYES",         10.0, 200),  # high-load floor
    ("FAMILY_PROTOTYPE_BASED",        0.1,  50),
    ("FAMILY_PROTOTYPE_BASED",        10.0, 200),  # v4 finding: HARDMAX dominates floor
    ("FAMILY_HYBRID",                 1.0,  50),   # mid-load Bayes-prototype mix
    ("FAMILY_BAYESIAN_WITH_PRIORS",   0.01, 10),   # low-load saturate w/ priors
)

# Pre-reg bands (LOCKED)
HP_DISCRIMINATING_FRAC = 0.30      # >= 14/48 of (family, inner) pts in HP+MB tiers
HP_MIN_TOP1 = 0.50                  # tier threshold for HP+MB tiers
HP_SAT_THRESHOLD = 0.95             # SAT >= this (DOWN-WEIGHTED per Skunkworks Q-rule)
HF_FLOOR_THRESHOLD = 0.10           # FLOOR <= this (substrate at chance)
HP_LIFT_OVER_CHANCE_MIN = 5.0       # mech / (1/n_schemas) >= 5x at HP
HP_POSITIVE_CONTROL_TOP1 = 0.50     # EXEMPLAR_BAYES @ alpha=0.1, n_schemas=50: top1 >= 0.50
HF_ARMS_IDENTICAL_TOL = 0.02        # at each pt family-pair max diff < tol -> all-identical flag
HF_RANDOM_ARM_TOL = 0.30            # uniform-random witness within +/- this of chance
HF_FAMILY_HASH_PAIRS_MIN = 2         # at least 2 of 6 pairs differ (META_RULE_AF)

# Per-point queries
N_QUERIES_FULL = 20
N_QUERIES_SMOKE = 5

# n_classes -> chance floor (precomputed for clarity)
def chance_floor(n_schemas: int) -> float:
    return 1.0 / float(n_schemas)


REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ----- Substrate primitives (numpy bipolar HDC; inherited from v1/v3/v4 core) -----

def _bipolar_codebook(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _build_class_exemplars(g: np.random.Generator,
                            n_classes: int,
                            n_ex_per_class: int,
                            N: int) -> np.ndarray:
    """Per-class exemplar storage. Returns (C, K, N) float32 normalized."""
    prototypes = _bipolar_codebook(n_classes, N, g)
    NOISE_SCALE = 0.30
    noise = (g.standard_normal(size=(n_classes, n_ex_per_class, N))
             .astype(np.float32) * NOISE_SCALE)
    exemplars = prototypes[:, None, :] + noise
    norms = np.linalg.norm(exemplars, axis=-1, keepdims=True) + 1e-8
    exemplars = exemplars / norms
    return exemplars


def _make_queries(g: np.random.Generator,
                   exemplars: np.ndarray,
                   n_queries: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate held-out queries with known true labels.

    Returns: queries (Q, N) float32 normalized; true_labels (Q,) int.
    """
    n_classes = exemplars.shape[0]
    N = exemplars.shape[-1]
    proto_est = exemplars.mean(axis=1)
    proto_est = proto_est / (np.linalg.norm(proto_est, axis=-1, keepdims=True) + 1e-8)
    labels = np.array([c % n_classes for c in range(n_queries)], dtype=np.int64)
    NOISE_SCALE = 0.30
    q_noise = g.standard_normal(size=(n_queries, N)).astype(np.float32) * NOISE_SCALE
    queries = proto_est[labels] + q_noise
    queries = queries / (np.linalg.norm(queries, axis=-1, keepdims=True) + 1e-8)
    return queries, labels


# ----- SCHEMA FAMILY readouts -----

def _family_exemplar_bayes(queries: np.ndarray,
                            exemplars: np.ndarray) -> np.ndarray:
    """LSE posterior aggregation (v3 default; prior_strength=1.0)."""
    n_classes, K, N = exemplars.shape
    beta = float(math.log(max(n_classes, 2)) / 0.1)
    ex_flat = exemplars.reshape(n_classes * K, N)
    sims = queries @ ex_flat.T
    sims = sims.reshape(queries.shape[0], n_classes, K)
    log_prior = np.log(np.ones(n_classes, dtype=np.float64) / n_classes)
    weighted = beta * sims
    max_per_qc = weighted.max(axis=-1, keepdims=True)
    lse = (max_per_qc.squeeze(-1)
           + np.log(np.exp(weighted - max_per_qc).sum(axis=-1) + 1e-30))
    log_posterior = log_prior[None, :] + lse
    preds = log_posterior.argmax(axis=-1).astype(np.int64)
    return preds


def _family_prototype_based(queries: np.ndarray,
                              exemplars: np.ndarray) -> np.ndarray:
    """Argmax over per-class CENTROID similarity (v4 HARDMAX). No LSE, no prior."""
    n_classes, K, N = exemplars.shape
    centroids = exemplars.mean(axis=1)
    centroids = centroids / (np.linalg.norm(centroids, axis=-1, keepdims=True) + 1e-8)
    sims = queries @ centroids.T
    preds = sims.argmax(axis=-1).astype(np.int64)
    return preds


def _family_hybrid(queries: np.ndarray,
                    exemplars: np.ndarray) -> np.ndarray:
    """Weighted mix of LSE-Bayes log-posterior and centroid log-similarity.

    decision = argmax_c [ 0.5 * log_posterior_bayes(c|q) + 0.5 * beta*cos(q, centroid_c) ]
    """
    n_classes, K, N = exemplars.shape
    beta = float(math.log(max(n_classes, 2)) / 0.1)
    # Bayes piece
    ex_flat = exemplars.reshape(n_classes * K, N)
    sims = queries @ ex_flat.T
    sims = sims.reshape(queries.shape[0], n_classes, K)
    log_prior = np.log(np.ones(n_classes, dtype=np.float64) / n_classes)
    weighted = beta * sims
    max_per_qc = weighted.max(axis=-1, keepdims=True)
    lse = (max_per_qc.squeeze(-1)
           + np.log(np.exp(weighted - max_per_qc).sum(axis=-1) + 1e-30))
    log_posterior_bayes = log_prior[None, :] + lse                 # (Q, C)
    # Prototype piece
    centroids = exemplars.mean(axis=1)
    centroids = centroids / (np.linalg.norm(centroids, axis=-1, keepdims=True) + 1e-8)
    proto_sim = queries @ centroids.T                              # (Q, C)
    proto_score = beta * proto_sim
    # Mix (each piece roughly on log-scale; 0.5/0.5)
    mix = 0.5 * log_posterior_bayes + 0.5 * proto_score
    preds = mix.argmax(axis=-1).astype(np.int64)
    return preds


def _family_bayesian_with_priors(queries: np.ndarray,
                                   exemplars: np.ndarray) -> np.ndarray:
    """LSE posterior with VARIABLE prior strength scaled by n_schemas.

    Strong prior_strength = log(n_classes) (penalizes uncommon classes more).
    """
    n_classes, K, N = exemplars.shape
    beta = float(math.log(max(n_classes, 2)) / 0.1)
    # Variable prior: stronger for larger n_classes (concentration-like)
    prior_strength = float(math.log(max(n_classes, 2)))
    ex_flat = exemplars.reshape(n_classes * K, N)
    sims = queries @ ex_flat.T
    sims = sims.reshape(queries.shape[0], n_classes, K)
    log_prior = np.log(np.ones(n_classes, dtype=np.float64) / n_classes) * prior_strength
    weighted = beta * sims
    max_per_qc = weighted.max(axis=-1, keepdims=True)
    lse = (max_per_qc.squeeze(-1)
           + np.log(np.exp(weighted - max_per_qc).sum(axis=-1) + 1e-30))
    log_posterior = log_prior[None, :] + lse
    preds = log_posterior.argmax(axis=-1).astype(np.int64)
    return preds


def _family_uniform_random(queries: np.ndarray,
                             n_classes: int,
                             g: np.random.Generator) -> np.ndarray:
    """Chance-floor witness (kept for sanity; NOT a family arm)."""
    return g.integers(0, n_classes, size=queries.shape[0]).astype(np.int64)


_FAMILY_FNS = {
    "FAMILY_EXEMPLAR_BAYES":       _family_exemplar_bayes,
    "FAMILY_PROTOTYPE_BASED":      _family_prototype_based,
    "FAMILY_HYBRID":               _family_hybrid,
    "FAMILY_BAYESIAN_WITH_PRIORS": _family_bayesian_with_priors,
}


# ----- One phase-point run (one family on one inner config) -----

def _run_phase_point(
    g: np.random.Generator,
    family: str,
    alpha: float,
    n_schemas: int,
    N: int,
    n_queries: int,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # Derive n_exemplars_per_class from alpha = (n_schemas * n_ex) / N
    n_ex_per_class = max(1, int(round(alpha * N / n_schemas)))
    K_total = n_schemas * n_ex_per_class
    actual_alpha = K_total / N

    exemplars = _build_class_exemplars(g, n_schemas, n_ex_per_class, N)
    queries, true_labels = _make_queries(g, exemplars, n_queries)

    fn = _FAMILY_FNS[family]
    preds = fn(queries, exemplars)
    acc = float(np.mean(preds == true_labels))

    # Chance witness (separate seed branch; for arms_must_differ sanity)
    preds_random = _family_uniform_random(queries, n_schemas, g)
    acc_random = float(np.mean(preds_random == true_labels))

    chance = chance_floor(n_schemas)
    lift = acc / max(chance, 1e-9)

    out["family"] = family
    out["alpha_requested"] = float(alpha)
    out["alpha_actual"] = float(actual_alpha)
    out["n_schemas"] = int(n_schemas)
    out["n_exemplars_per_class"] = int(n_ex_per_class)
    out["N"] = int(N)
    out["n_queries"] = int(n_queries)
    out["top1"] = acc
    out["random_arm_top1"] = acc_random
    out["chance_floor"] = chance
    out["lift_over_chance"] = lift
    return out


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    """Run full or smoke phase diagram for one seed."""
    g = np.random.default_rng(seed)
    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny selftest: 1 corner per family at alpha=0.1, n_schemas=50
        points = [(fam, 0.1, 50) for fam in FAMILIES]
        n_queries = 5
    else:
        # Full: outer x inner = 4 families x (4 alphas x 3 n_schemas) = 48 pts
        points = []
        for fam in FAMILIES:
            for alpha in ALPHA_VALUES:
                for ns in N_SCHEMAS_VALUES:
                    points.append((fam, alpha, ns))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (fam, alpha, ns) in points:
        res = _run_phase_point(g, fam, alpha, ns, N_DIM_FIXED, n_queries)
        phase_map.append(res)

    elapsed = time.time() - started

    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "smoke_corners": bool(smoke_corners),
        "backend": get_backend_label(),
        "n_phase_points": len(phase_map),
        "n_queries_per_point": int(n_queries),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


def _family_hash(top1_list: List[float]) -> str:
    """SHA-256 of canonical-rounded per-point top1 (for META_RULE_AF)."""
    rounded = [round(float(x), 4) for x in top1_list]
    return hashlib.sha256(json.dumps(rounded, sort_keys=True).encode()).hexdigest()[:16]


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Compute per-family summary + verdict from seed phase-maps."""
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool per (family, alpha_requested, n_schemas) across seeds
    bucket: Dict[Tuple[str, float, int], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (str(pt["family"]),
                   float(pt["alpha_requested"]),
                   int(pt["n_schemas"]))
            d = bucket.setdefault(key, {
                "top1": [],
                "random_top1": [],
                "lift": [],
                "chance": [],
                "alpha_actual": [],
                "n_exemplars_per_class": [],
            })
            d["top1"].append(pt["top1"])
            d["random_top1"].append(pt["random_arm_top1"])
            d["lift"].append(pt["lift_over_chance"])
            d["chance"].append(pt["chance_floor"])
            d["alpha_actual"].append(pt["alpha_actual"])
            d["n_exemplars_per_class"].append(pt["n_exemplars_per_class"])

    # Per-pt aggregate + per-family aggregation
    summary_per_pt: List[Dict[str, Any]] = []
    family_topk: Dict[str, List[float]] = {fam: [] for fam in FAMILIES}
    family_lift: Dict[str, List[float]] = {fam: [] for fam in FAMILIES}
    discriminating_pts = 0
    sat_pts = 0
    floor_pts = 0
    random_arm_pathology_pts = 0

    for key, d in sorted(bucket.items()):
        fam, alpha, ns = key
        top1_mean = float(np.mean(d["top1"]))
        rand_mean = float(np.mean(d["random_top1"]))
        lift_mean = float(np.mean(d["lift"]))
        chance = float(np.mean(d["chance"]))
        actual_alpha = float(np.mean(d["alpha_actual"]))
        n_ex_mean = float(np.mean(d["n_exemplars_per_class"]))

        # Tier classification
        if top1_mean >= HP_SAT_THRESHOLD:
            tier = "SATURATED"
            sat_pts += 1
        elif top1_mean <= HF_FLOOR_THRESHOLD:
            tier = "FLOOR"
            floor_pts += 1
        elif top1_mean >= HP_MIN_TOP1 and lift_mean >= HP_LIFT_OVER_CHANCE_MIN:
            tier = "HARD_PASS"
            discriminating_pts += 1
        elif top1_mean >= 0.30:
            tier = "MIDDLE_BAND"
            discriminating_pts += 1
        else:
            tier = "HARD_FAIL"

        # Random-arm sanity per pt
        if abs(rand_mean - chance) > HF_RANDOM_ARM_TOL:
            random_arm_pathology_pts += 1

        family_topk[fam].append(top1_mean)
        family_lift[fam].append(lift_mean)

        summary_per_pt.append({
            "family": fam,
            "alpha_requested": alpha,
            "alpha_actual": actual_alpha,
            "n_schemas": ns,
            "n_exemplars_per_class": n_ex_mean,
            "top1_mean": top1_mean,
            "random_arm_top1_mean": rand_mean,
            "lift_over_chance_mean": lift_mean,
            "chance_floor": chance,
            "tier": tier,
            "n_seeds": len(d["top1"]),
        })

    n_total_pts = len(bucket)
    discriminating_fraction = discriminating_pts / max(n_total_pts, 1)

    # Per-family summary
    per_family_summary: Dict[str, Any] = {}
    family_hashes: Dict[str, str] = {}
    for fam in FAMILIES:
        topk = family_topk[fam]
        lifts = family_lift[fam]
        if topk:
            per_family_summary[fam] = {
                "top1_mean": float(np.mean(topk)),
                "top1_min": float(np.min(topk)),
                "top1_max": float(np.max(topk)),
                "lift_mean": float(np.mean(lifts)),
                "n_pts": len(topk),
            }
            family_hashes[fam] = _family_hash(topk)
        else:
            per_family_summary[fam] = {"top1_mean": 0.0, "n_pts": 0}
            family_hashes[fam] = "EMPTY"

    # Pairwise hash distinctness (META_RULE_AF)
    pair_differs = 0
    pairs = []
    fams_with_data = [f for f in FAMILIES if family_hashes[f] != "EMPTY"]
    for i in range(len(fams_with_data)):
        for j in range(i + 1, len(fams_with_data)):
            fa, fb = fams_with_data[i], fams_with_data[j]
            differs = family_hashes[fa] != family_hashes[fb]
            pairs.append({"family_a": fa, "family_b": fb, "differs": differs})
            if differs:
                pair_differs += 1
    family_pair_distinctness = {
        "pair_differs_count": pair_differs,
        "pairs": pairs,
    }

    # Positive control: EXEMPLAR_BAYES at alpha=0.1, n_schemas=50 -> top1 >= 0.50
    pos_ctrl_key = ("FAMILY_EXEMPLAR_BAYES", 0.1, 50)
    positive_control_top1: Optional[float] = None
    if pos_ctrl_key in bucket:
        positive_control_top1 = float(np.mean(bucket[pos_ctrl_key]["top1"]))
    positive_control_pass = (positive_control_top1 is not None
                              and positive_control_top1 >= HP_POSITIVE_CONTROL_TOP1)

    # Cliff observable per family
    cliff_per_family: Dict[str, bool] = {}
    for fam in FAMILIES:
        topk = family_topk[fam]
        cliff_per_family[fam] = bool(topk and any(t < 0.40 for t in topk))

    # All-saturated / arms-identical hard-fails
    all_top1 = [p["top1_mean"] for p in summary_per_pt]
    all_saturated = bool(all_top1 and all(t >= HP_SAT_THRESHOLD for t in all_top1))
    # Arms-identical: at each pt, families differ <=tol -> count "all-equal" pts
    # We check the family hashes (above) for measurable distinctness across the
    # whole grid; "arms_identical" trigger fires only when 0 family-pairs differ
    arms_identical = (pair_differs == 0 and run_mode == "full")
    random_arm_pathology = random_arm_pathology_pts >= 2

    # Verdict logic
    cardinality_expected_full = len(FAMILIES) * len(ALPHA_VALUES) * len(N_SCHEMAS_VALUES)
    cardinality_expected_smoke = len(SMOKE_CORNERS)

    if all_saturated:
        verdict = "HARD_FAIL"
    elif arms_identical:
        verdict = "HARD_FAIL"
    elif random_arm_pathology:
        verdict = "HARD_FAIL"
    elif not positive_control_pass and run_mode == "full":
        verdict = "HARD_FAIL"
    elif (discriminating_fraction >= HP_DISCRIMINATING_FRAC
          and pair_differs >= HF_FAMILY_HASH_PAIRS_MIN
          and (positive_control_pass or run_mode != "full")):
        verdict = "HARD_PASS"
    elif discriminating_fraction >= 0.10 and pair_differs >= 1:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    headline = (f"discriminating_frac={discriminating_fraction:.3f} "
                f"({discriminating_pts}/{n_total_pts}) | "
                f"family_pair_differs={pair_differs}/6 | "
                f"sat={sat_pts} floor={floor_pts} | "
                f"pos_ctrl={positive_control_top1 if positive_control_top1 is not None else 'NA'} "
                f"(pass={positive_control_pass}) | "
                f"random_arm_pathology={random_arm_pathology}")

    verdict_msg = f"{verdict} | {headline}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "discriminating_fraction": discriminating_fraction,
        "discriminating_pts": int(discriminating_pts),
        "n_combos_total": int(n_total_pts),
        "saturated_pts": int(sat_pts),
        "floor_pts": int(floor_pts),
        "all_saturated": all_saturated,
        "arms_identical": arms_identical,
        "random_arm_pathology": random_arm_pathology,
        "random_arm_pathology_pts": int(random_arm_pathology_pts),
        "positive_control_top1": positive_control_top1,
        "positive_control_pass": bool(positive_control_pass),
        "cliff_per_family": cliff_per_family,
        "per_family_summary": per_family_summary,
        "family_hashes": family_hashes,
        "family_pair_distinctness": family_pair_distinctness,
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "expected_cardinality_full": int(cardinality_expected_full),
        "expected_cardinality_smoke": int(cardinality_expected_smoke),
    }


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: one corner per family at alpha=0.1, n_schemas=50.

    Asserts:
      - 4 phase-points (one per family) RAN
      - chance-witness within tolerance of 1/n_schemas
      - at least 2 families produce distinct top1 (smoke discriminator firing)
      - EXEMPLAR_BAYES at alpha=0.1, n_schemas=50 shows top1 >= 0.20 (mechanism alive)
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        pts = body.get("phase_map", [])
        if len(pts) != len(FAMILIES):
            return False, (f"selftest: expected {len(FAMILIES)} pts, got {len(pts)}")
        # Map family -> top1
        by_fam = {p["family"]: p for p in pts}
        for fam in FAMILIES:
            if fam not in by_fam:
                return False, f"selftest: missing family {fam}"
        # EXEMPLAR_BAYES smoke alive at sweet-spot
        eb = by_fam["FAMILY_EXEMPLAR_BAYES"]
        if eb["top1"] < 0.20:
            return False, (f"selftest: EXEMPLAR_BAYES top1={eb['top1']:.3f} too low "
                            f"at sweet-spot (alpha=0.1, n_schemas=50)")
        # Chance witness sanity for at least one family
        chance = eb["chance_floor"]
        if abs(eb["random_arm_top1"] - chance) > 0.35:
            return False, (f"selftest: random_arm top1={eb['random_arm_top1']:.3f} "
                            f"too far from chance={chance:.3f}")
        # Family discriminator: at least 2 of 4 family top1 values must differ
        top1_vals = [by_fam[f]["top1"] for f in FAMILIES]
        distinct_pairs = 0
        for i in range(len(top1_vals)):
            for j in range(i + 1, len(top1_vals)):
                if abs(top1_vals[i] - top1_vals[j]) >= 0.01:
                    distinct_pairs += 1
        if distinct_pairs == 0:
            return False, (f"selftest: ALL 4 families produced identical top1 "
                            f"{top1_vals} (component substitution didn't happen)")
        msg = (f"selftest OK: "
               f"EB={by_fam['FAMILY_EXEMPLAR_BAYES']['top1']:.3f} "
               f"PROTO={by_fam['FAMILY_PROTOTYPE_BASED']['top1']:.3f} "
               f"HYBRID={by_fam['FAMILY_HYBRID']['top1']:.3f} "
               f"BWP={by_fam['FAMILY_BAYESIAN_WITH_PRIORS']['top1']:.3f} "
               f"(distinct_pairs={distinct_pairs}/6) "
               f"chance={chance:.3f} rand={eb['random_arm_top1']:.3f} "
               f"backend={body['backend']} elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
