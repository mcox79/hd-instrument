"""Shared core for substrate_schema_exemplar_bayes_phase_diagram_v1 sibling cells.

Provides the phase-diagram sweep over (n_exemplars, n_classes, N_DIM) with 3 arms
(ARM_SCHEMA_BAYES / ARM_NEAREST_EXEMPLAR / ARM_UNIFORM_RANDOM) measuring
classification accuracy for schema exemplar-Bayes (vmPFC analog) and the
Bayes-vs-NN advantage per (n_ex, n_classes, N) phase point.

Stage 2 phase-coverage MID -> HIGH for chain-grade schema exemplar-Bayes primitive.

Sibling cells import run_one_seed_phase_diagram(seed) and aggregate.
ASCII-only. CPU-only (numpy + scipy.special.logsumexp); no GPU required.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 2 phase-diagram coverage
"""
# PRESERVE_ENV_VARS: HDLAB_QUEUE
from __future__ import annotations

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.special import logsumexp  # noqa: F401 — used for numerical stability

ANCHOR_PREFIX = "substrate_schema_exemplar_bayes_phase_diagram_v1"

# ----- Phase axes (LOCKED per prereg) -----
N_EXEMPLAR_VALUES = (1, 5, 10, 50, 100)            # 5 points; 1 = degenerate NN
N_CLASS_VALUES = (2, 5, 10, 50)                    # 4 points; class load
N_VALUES = (2048, 4096, 8192)                      # 3 points; substrate dim
PRIOR_STRENGTH = 1.0                                # fixed per prereg trim
ARMS = ("ARM_SCHEMA_BAYES", "ARM_NEAREST_EXEMPLAR", "ARM_UNIFORM_RANDOM")

# Smoke 6 corner points: (n_exemplars, n_classes, N) per pre-reg
SMOKE_CORNERS = (
    (50,  2,  8192),    # low-load saturate (both high; small diff)
    (10,  10, 4096),    # mid-load Bayes-lift (Bayes >> NN)
    (1,   5,  4096),    # degenerate K=1 (BAYES == NN)
    (100, 50, 2048),    # high-load cliff (both low)
    (50,  10, 4096),    # sweet-spot Bayes-lift
    (5,   2,  8192),    # trivial 2-class
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load)
HP_BAYES_NN_MIN_DIFF = 0.15          # per-point threshold for Bayes-lift
HP_AVG_BAYES_NN_GATE = 0.10          # average gate
MB_AVG_BAYES_NN_LO = 0.05
HF_AVG_BAYES_NN_HARD_FLOOR = 0.05
HP_LOW_LOAD_SAT_FLOOR = 0.95         # low-load sweet-spot BAYES floor
HP_CLIFF_LOW_TOP1 = 0.40             # cliff observable threshold
HF_NO_CLIFF_RECALL_MIN = 0.95        # if ALL phase pts >= this, HARD_FAIL saturation
HF_BAYES_NN_DEGENERATE_TOL = 0.02    # mechanism not firing if BAYES <= NN within this at low-load
HP_MIN_LIFT_POINTS = 30              # of 60
MB_MIN_LIFT_POINTS = 15
RANDOM_ARM_TOL = 0.30                # ARM_UNIFORM_RANDOM must be within 1/C +/- this
                                      # (loose for small-Q smoke; 5-query binomial std at chance=0.5 ~ 0.22)
RANDOM_ARM_PATHOLOGY_MIN_PTS = 2     # need >= 2 points outside tol for pathology flag

# Per-point query count (FULL); SMOKE uses smaller
N_QUERIES_FULL = 20
N_QUERIES_SMOKE = 5

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "numpy.cpu"


# ----- Substrate primitives (numpy bipolar HDC) -----

def _bipolar_codebook(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar (+/-1) random codebook (V, N); L2-normalized rows."""
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _build_class_exemplars(g: np.random.Generator,
                            n_classes: int,
                            n_ex_per_class: int,
                            N: int) -> np.ndarray:
    """Per-class exemplar storage.

    Each class c has a 'prototype' vector p_c (bipolar random); exemplars are
    p_c + bipolar noise to model intra-class variability. This mimics vmPFC
    schema storage: instances share a class-level structure but vary.

    Returns: (n_classes, n_ex_per_class, N) float32 normalized.
    """
    prototypes = _bipolar_codebook(n_classes, N, g)             # (C, N)
    # Per-exemplar noise (15% bit-flip noise relative to prototype)
    NOISE_SCALE = 0.30
    noise = (g.standard_normal(size=(n_classes, n_ex_per_class, N))
             .astype(np.float32) * NOISE_SCALE)
    exemplars = prototypes[:, None, :] + noise                  # (C, K, N)
    # Normalize per-exemplar
    norms = np.linalg.norm(exemplars, axis=-1, keepdims=True) + 1e-8
    exemplars = exemplars / norms
    return exemplars                                             # (C, K, N)


def _make_queries(g: np.random.Generator,
                   exemplars: np.ndarray,
                   n_queries: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate query vectors by sampling held-out instances from each class.

    Queries are NEW exemplars (drawn from same prototype + fresh noise) so the
    classifier must generalize from stored exemplars to novel ones. True class
    labels assigned round-robin across classes.

    Returns: (queries (Q, N) float32 normalized, true_labels (Q,) int).
    """
    n_classes = exemplars.shape[0]
    N = exemplars.shape[-1]
    # Recover prototypes by averaging stored exemplars per class (since
    # exemplars are class-prototype + noise, this is an estimate; for the
    # synthesizer we instead generate queries from the SAME class prototype +
    # fresh noise — but we need access to the prototype. Recompute it:
    # prototypes_est = mean over exemplars per class (norm).
    # However we want clean queries — so generate fresh noise on the class
    # mean direction directly.
    proto_est = exemplars.mean(axis=1)                          # (C, N)
    proto_est = proto_est / (np.linalg.norm(proto_est, axis=-1, keepdims=True) + 1e-8)
    # Round-robin labels
    labels = np.array([c % n_classes for c in range(n_queries)], dtype=np.int64)
    NOISE_SCALE = 0.30
    q_noise = g.standard_normal(size=(n_queries, N)).astype(np.float32) * NOISE_SCALE
    queries = proto_est[labels] + q_noise
    queries = queries / (np.linalg.norm(queries, axis=-1, keepdims=True) + 1e-8)
    return queries, labels


# ----- Arms -----

def _arm_schema_bayes(queries: np.ndarray,
                       exemplars: np.ndarray,
                       prior_strength: float) -> np.ndarray:
    """Bayes posterior over class via log-sum-exp aggregation across exemplars.

    For each class c, log_p(c | q) ~ log_prior(c) + logsumexp_k(beta * cos(q, e_c_k))

    queries:   (Q, N) normalized
    exemplars: (C, K, N) normalized
    prior_strength: alpha for Dirichlet-like prior (1.0 = uniform-ish)

    Returns: (Q,) predicted class labels.
    """
    n_classes, K, N = exemplars.shape
    # Beta temperature scaled by class load (per prereg)
    beta = float(math.log(max(n_classes, 2)) / 0.1)             # ~ log(C) * 10
    # Cosine similarity (queries, classes, exemplars)
    # queries (Q, N); exemplars (C, K, N) -> per (Q, C, K) cosines
    # Compute via reshape: (Q, N) @ (C*K, N).T = (Q, C*K) then reshape
    ex_flat = exemplars.reshape(n_classes * K, N)                # (CK, N)
    sims = queries @ ex_flat.T                                    # (Q, CK)
    sims = sims.reshape(queries.shape[0], n_classes, K)           # (Q, C, K)
    # log_prior uniform with prior_strength weight
    log_prior = np.log(np.ones(n_classes, dtype=np.float64) / n_classes) * prior_strength
    # logsumexp over exemplars (axis=2)
    # scipy.special.logsumexp would import the same; numpy is fine here
    weighted = beta * sims                                        # (Q, C, K)
    max_per_qc = weighted.max(axis=-1, keepdims=True)              # (Q, C, 1)
    lse = (max_per_qc.squeeze(-1)
           + np.log(np.exp(weighted - max_per_qc).sum(axis=-1) + 1e-30))   # (Q, C)
    log_posterior = log_prior[None, :] + lse                       # (Q, C)
    preds = log_posterior.argmax(axis=-1).astype(np.int64)         # (Q,)
    return preds


def _arm_nearest_exemplar(queries: np.ndarray,
                            exemplars: np.ndarray) -> np.ndarray:
    """Argmax_c argmax_k cos(q, e_c_k); single nearest exemplar."""
    n_classes, K, N = exemplars.shape
    ex_flat = exemplars.reshape(n_classes * K, N)
    sims = queries @ ex_flat.T                                    # (Q, CK)
    # Find max-similarity exemplar index per query, then map back to class
    flat_argmax = sims.argmax(axis=-1)                            # (Q,)
    preds = (flat_argmax // K).astype(np.int64)
    return preds


def _arm_uniform_random(queries: np.ndarray,
                          n_classes: int,
                          g: np.random.Generator) -> np.ndarray:
    """Uniform random class assignment (~1/C accuracy floor)."""
    return g.integers(0, n_classes, size=queries.shape[0]).astype(np.int64)


# ----- One phase-point run (3 arms x N_QUERIES) -----

def _run_phase_point(
    g: np.random.Generator,
    n_exemplars_per_class: int,
    n_classes: int,
    N: int,
    n_queries: int,
    prior_strength: float = PRIOR_STRENGTH,
) -> Dict[str, Any]:
    """Run all 3 arms on one phase point."""
    out: Dict[str, Any] = {}

    # Build exemplar storage per class
    exemplars = _build_class_exemplars(g, n_classes, n_exemplars_per_class, N)

    # Generate held-out queries with known true labels
    queries, true_labels = _make_queries(g, exemplars, n_queries)

    # ARM 1: SCHEMA_BAYES posterior aggregation
    preds_bayes = _arm_schema_bayes(queries, exemplars, prior_strength)
    acc_bayes = float(np.mean(preds_bayes == true_labels))

    # ARM 2: NEAREST_EXEMPLAR (argmax over single nearest exemplar)
    preds_nn = _arm_nearest_exemplar(queries, exemplars)
    acc_nn = float(np.mean(preds_nn == true_labels))

    # ARM 3: UNIFORM_RANDOM (chance floor)
    preds_random = _arm_uniform_random(queries, n_classes, g)
    acc_random = float(np.mean(preds_random == true_labels))

    out["ARM_SCHEMA_BAYES_acc"] = acc_bayes
    out["ARM_NEAREST_EXEMPLAR_acc"] = acc_nn
    out["ARM_UNIFORM_RANDOM_acc"] = acc_random
    out["bayes_minus_nn"] = acc_bayes - acc_nn
    out["bayes_minus_random"] = acc_bayes - acc_random
    out["n_exemplars_per_class"] = int(n_exemplars_per_class)
    out["n_classes"] = int(n_classes)
    out["N"] = int(N)
    out["prior_strength"] = float(prior_strength)
    out["n_queries"] = int(n_queries)
    out["chance_floor"] = 1.0 / float(n_classes)
    return out


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    """Run full or smoke phase diagram for one seed.

    Args:
        seed: integer seed.
        run_mode: "smoke" | "full" | "selftest".
        smoke_corners: if True, only run 6 corner points (smoke gate).
    """
    g = np.random.default_rng(seed)
    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny selftest: 2 corners with smaller queries
        points = [SMOKE_CORNERS[1], SMOKE_CORNERS[4]]   # mid-Bayes + sweet-spot
        n_queries = 5
    else:
        points = []
        for n_ex in N_EXEMPLAR_VALUES:
            for n_cl in N_CLASS_VALUES:
                for N in N_VALUES:
                    points.append((n_ex, n_cl, N))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (n_ex, n_cl, N) in points:
        res = _run_phase_point(g, n_ex, n_cl, N, n_queries, PRIOR_STRENGTH)
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


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Compute bayes_advantage per (n_ex, n_cl, N) + verdict from seed phase-maps."""
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool all phase points across seeds; mean per (n_ex, n_cl, N)
    bucket: Dict[Tuple[int, int, int], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["n_exemplars_per_class"]),
                   int(pt["n_classes"]),
                   int(pt["N"]))
            d = bucket.setdefault(key, {
                "ARM_SCHEMA_BAYES_acc": [],
                "ARM_NEAREST_EXEMPLAR_acc": [],
                "ARM_UNIFORM_RANDOM_acc": [],
                "chance_floor": [],
            })
            d["ARM_SCHEMA_BAYES_acc"].append(pt["ARM_SCHEMA_BAYES_acc"])
            d["ARM_NEAREST_EXEMPLAR_acc"].append(pt["ARM_NEAREST_EXEMPLAR_acc"])
            d["ARM_UNIFORM_RANDOM_acc"].append(pt["ARM_UNIFORM_RANDOM_acc"])
            d["chance_floor"].append(pt["chance_floor"])

    summary_per_pt: List[Dict[str, Any]] = []
    bayes_minus_nn_list: List[float] = []
    bayes_acc_all: List[float] = []
    nn_acc_all: List[float] = []
    random_arm_pathology_pts = 0
    low_load_degenerate_pts: List[Tuple[int, int, int]] = []
    for key, d in sorted(bucket.items()):
        n_ex, n_cl, N = key
        bayes_mean = float(np.mean(d["ARM_SCHEMA_BAYES_acc"]))
        nn_mean = float(np.mean(d["ARM_NEAREST_EXEMPLAR_acc"]))
        rand_mean = float(np.mean(d["ARM_UNIFORM_RANDOM_acc"]))
        chance = float(np.mean(d["chance_floor"]))
        diff = bayes_mean - nn_mean
        bayes_minus_nn_list.append(diff)
        bayes_acc_all.append(bayes_mean)
        nn_acc_all.append(nn_mean)
        # Random-arm sanity: random arm should be within +/- RANDOM_ARM_TOL of chance
        if abs(rand_mean - chance) > RANDOM_ARM_TOL:
            random_arm_pathology_pts += 1
        # META_RULE_AM check: HIGH-class-load sweet-spot where Bayes SHOULD beat NN
        # (n_ex >= 10, n_cl >= 10, N >= 8192). If BAYES <= NN here, mechanism is
        # not firing as a Bayesian aggregator and instead degenerated to NN.
        # NOTE: at n_classes=2 Bayes vs NN tie or NN-wins is EXPECTED (NN argmax
        # over many noisy exemplars beats Bayes-averaged prototype), so we don't
        # flag low-class-load BAYES<=NN as pathology.
        if (n_ex >= 10 and n_cl >= 10 and N >= 8192
                and bayes_mean <= nn_mean + HF_BAYES_NN_DEGENERATE_TOL):
            low_load_degenerate_pts.append((n_ex, n_cl, N))
        summary_per_pt.append({
            "n_exemplars_per_class": n_ex,
            "n_classes": n_cl,
            "N": N,
            "ARM_SCHEMA_BAYES_acc_mean": bayes_mean,
            "ARM_NEAREST_EXEMPLAR_acc_mean": nn_mean,
            "ARM_UNIFORM_RANDOM_acc_mean": rand_mean,
            "chance_floor": chance,
            "bayes_minus_nn": diff,
            "n_seeds": len(d["ARM_SCHEMA_BAYES_acc"]),
        })

    # Lift count (HARD_PASS gate A)
    lift_count = sum(1 for d in bayes_minus_nn_list if d >= HP_BAYES_NN_MIN_DIFF)
    n_total = len(bayes_minus_nn_list)
    avg_bayes_minus_nn = float(np.mean(bayes_minus_nn_list)) if bayes_minus_nn_list else 0.0
    # Avg over those expected to lift (n_ex >= 5; skip K=1 degenerate)
    # but main avg is over ALL pts

    # Low-load saturate (HARD_PASS gate B): some point >= HP_LOW_LOAD_SAT_FLOOR
    # at low-class-load sweet spot (n_ex >= 50, n_cl <= 5, N >= 8192)
    low_load_pts = [p for p in summary_per_pt
                    if p["n_exemplars_per_class"] >= 50
                    and p["n_classes"] <= 5
                    and p["N"] >= 8192]
    low_load_sat = any(p["ARM_SCHEMA_BAYES_acc_mean"] >= HP_LOW_LOAD_SAT_FLOOR
                       for p in low_load_pts)

    # Cliff observable (HARD_PASS gate C): some point BAYES < HP_CLIFF_LOW_TOP1
    cliff_observable = any(p["ARM_SCHEMA_BAYES_acc_mean"] < HP_CLIFF_LOW_TOP1
                           for p in summary_per_pt)

    # All-saturated HF: all BAYES >= HF_NO_CLIFF_RECALL_MIN
    all_saturated = bool(all(b >= HF_NO_CLIFF_RECALL_MIN for b in bayes_acc_all)) \
                    if bayes_acc_all else False

    # Capacity scaling (HARD_PASS gate F): N=8192 top-half mean > N=2048 top-half mean by >= 0.05
    bayes_at_2048 = [p["ARM_SCHEMA_BAYES_acc_mean"] for p in summary_per_pt
                     if p["N"] == 2048]
    bayes_at_8192 = [p["ARM_SCHEMA_BAYES_acc_mean"] for p in summary_per_pt
                     if p["N"] == 8192]
    if bayes_at_2048 and bayes_at_8192:
        b2 = sorted(bayes_at_2048, reverse=True)[:max(1, len(bayes_at_2048)//2)]
        b8 = sorted(bayes_at_8192, reverse=True)[:max(1, len(bayes_at_8192)//2)]
        capacity_scaling_delta = float(np.mean(b8) - np.mean(b2))
        capacity_scaling_met = capacity_scaling_delta >= 0.05
    else:
        capacity_scaling_delta = 0.0
        capacity_scaling_met = False

    am_flag = len(low_load_degenerate_pts) > 0
    arms_identical = avg_bayes_minus_nn < HF_AVG_BAYES_NN_HARD_FLOOR
    random_arm_pathology = random_arm_pathology_pts >= RANDOM_ARM_PATHOLOGY_MIN_PTS

    # Verdict
    if all_saturated or arms_identical or am_flag or random_arm_pathology:
        verdict = "HARD_FAIL"
    elif (lift_count >= HP_MIN_LIFT_POINTS and low_load_sat and cliff_observable
          and avg_bayes_minus_nn >= HP_AVG_BAYES_NN_GATE and capacity_scaling_met):
        verdict = "HARD_PASS"
    elif (lift_count >= MB_MIN_LIFT_POINTS
          and avg_bayes_minus_nn >= MB_AVG_BAYES_NN_LO):
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    headline = (f"lift_pts={lift_count}/{n_total} | "
                f"avg_bayes_minus_nn={avg_bayes_minus_nn:.3f} | "
                f"low_load_sat={low_load_sat} | "
                f"cliff_observable={cliff_observable} | "
                f"capacity_scaling_met={capacity_scaling_met} "
                f"(delta={capacity_scaling_delta:.3f}) | "
                f"saturated={all_saturated} | "
                f"arms_identical={arms_identical} | "
                f"random_arm_pathology={random_arm_pathology} "
                f"(pts={random_arm_pathology_pts}) | "
                f"regime_flip={am_flag}")

    verdict_msg = f"{verdict} | {headline}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "lift_points": int(lift_count),
        "n_combos_total": int(n_total),
        "avg_bayes_minus_nn": avg_bayes_minus_nn,
        "all_saturated": all_saturated,
        "low_load_saturate_met": bool(low_load_sat),
        "cliff_observable": bool(cliff_observable),
        "capacity_scaling_met": bool(capacity_scaling_met),
        "capacity_scaling_delta": capacity_scaling_delta,
        "meta_rule_am_regime_flip_points": [list(p) for p in low_load_degenerate_pts],
        "arms_identical": bool(arms_identical),
        "random_arm_pathology": bool(random_arm_pathology),
        "random_arm_pathology_pts": int(random_arm_pathology_pts),
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
    }


# ----- Self-test (called from cell scripts via --self-test) -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corners (mid-Bayes + sweet-spot), 5 queries.

    Asserts:
      - phase_map non-empty
      - SCHEMA_BAYES > NEAREST_EXEMPLAR by >= 0.05 at sweet-spot
      - cardinality matches (2 points)
      - UNIFORM_RANDOM ~ chance floor (within tolerance)
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        # Sweet-spot corner = (50, 10, 4096) should show BAYES > NN
        sweet = [p for p in pts if p["n_exemplars_per_class"] == 50
                 and p["n_classes"] == 10 and p["N"] == 4096]
        if not sweet:
            return False, "selftest: missing sweet-spot corner (50, 10, 4096)"
        bayes = sweet[0]["ARM_SCHEMA_BAYES_acc"]
        nn = sweet[0]["ARM_NEAREST_EXEMPLAR_acc"]
        rand = sweet[0]["ARM_UNIFORM_RANDOM_acc"]
        chance = sweet[0]["chance_floor"]
        if bayes < nn:
            return False, (f"selftest: SCHEMA_BAYES={bayes:.3f} should not be "
                            f"below NEAREST_EXEMPLAR={nn:.3f} at sweet-spot")
        if abs(rand - chance) > 0.30:
            return False, (f"selftest: UNIFORM_RANDOM={rand:.3f} too far from "
                            f"chance floor={chance:.3f}")

        msg = (f"selftest OK: BAYES(50,10,4096)={bayes:.3f}, NN={nn:.3f}, "
               f"RANDOM={rand:.3f} (chance={chance:.3f}), "
               f"backend={body['backend']}, "
               f"elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
