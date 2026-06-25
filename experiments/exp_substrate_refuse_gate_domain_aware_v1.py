"""substrate_refuse_gate_domain_aware_v1 -- domain-aware refuse-gate composition.

CLOSURE TARGET (Barrier 4 retry per notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md):
  Audit primitive (chain-grade for "this isn't in our library") composes with
  intent classifier (chain-grade for domain detection) to deliver domain-aware
  refuse-gate. Each primitive does one job well; the COMPOSITION is what's new.

PIPELINE:
  query Q
    -> intent classifier (substrate-native Hebbian-bound domain classifier)
    -> if domain_label is IN-domain (concept exists in stored library):
         substrate retrieves answer via Hebbian-bound KG W
       else: REFUSE via audit-style "no-match-found" signal
  Composition: NEVER ask audit to do domain reasoning. Audit detects "this
  isn't in our library." Intent classifier detects "this isn't our domain."
  They compose; each does one job well.

ARMS (3):
  ARM_AUDIT_ALONE
    Naive refuse via audit-style match-threshold only (no intent classifier).
    This is the analog of the medqa refuse-gate HARD_FAIL.
  ARM_INTENT_ALONE
    Intent classifier with confidence threshold; refuses when classifier
    confidence below threshold. No audit signal.
  ARM_AUDIT_PLUS_INTENT
    Composition: intent classifier routes in-domain vs out-of-domain; audit
    primitive cross-checks library-presence on in-domain queries.

SYNTHETIC CORPUS (substrate-only generation):
  - 100 in-domain queries (categories ∈ {"animals", "geography", "tools"})
  - 100 out-of-domain queries (categories ∈ {"medical", "legal", "financial"})
  - Substrate loaded with ONLY in-domain facts.

PRE-REG BANDS (LOCKED at module init):
  HARD_PASS_CHAIN_GRADE_COMPOSITION:
    - in-domain answer-rate >= 0.85 in COMPOSED arm
    - out-of-domain refuse-rate >= 0.85 in COMPOSED arm
    - composed arm F1 > BOTH AUDIT_ALONE F1 AND INTENT_ALONE F1
    - cv <= 0.07 across seeds (composed arm F1)
  HARD_PASS_PARTIAL:
    composed arm beats both single-primitive arms (F1) but rate < 0.85
  MIDDLE_BAND:
    composed arm ties best single-primitive arm (within +/- 0.02 F1)
  HARD_FAIL_COMPOSITION_DOESNT_HELP:
    composed arm strictly WORSE than best single primitive
  MEDQA_FAILURE_REPRODUCED (diagnostic):
    AUDIT_ALONE refuse-rate < 0.50 on out-of-domain
    (confirms existing medqa REFUTED finding; expected diagnostic flag)

CONFIG:
  N=8192, V_C=600 (in-domain only); V_categories=3 in-domain;
  V_out_of_domain_categories=3.
  Seeds: [11, 13, 19] (fresh; not used in pointer-chain v2 / consolidation v3).
  Substrate-native primitives only (numpy; zero LLM forward calls).

SMOKE: n_queries=20 (10 in + 10 out), seed=11.

Author: exp_dev 2026-06-25.
ASCII-only; per-seed checkpoint; substrate-only.
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

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_refuse_gate_domain_aware_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE bands (LOCKED at module init)
HP_IN_ANSWER_RATE_MIN = 0.85
HP_OUT_REFUSE_RATE_MIN = 0.85
HP_CV_MAX = 0.07
HP_PARTIAL_LIFT_MIN = 0.02   # composed beats best single-primitive by >=0.02 F1
MID_F1_TIE_TOL = 0.02
MEDQA_AUDIT_REFUSE_RATE_THRESHOLD = 0.50  # diagnostic flag

# Lock-assertion
assert HP_IN_ANSWER_RATE_MIN <= 1.0 and HP_OUT_REFUSE_RATE_MIN <= 1.0
assert HP_PARTIAL_LIFT_MIN > 0.0

# Domain categories
IN_DOMAIN_CATEGORIES = ["animals", "geography", "tools"]
OUT_DOMAIN_CATEGORIES = ["medical", "legal", "financial"]
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)
N_DOMAINS = N_IN_CAT + N_OUT_CAT
DOMAIN_LABELS = IN_DOMAIN_CATEGORIES + OUT_DOMAIN_CATEGORIES
IN_DOMAIN_IDS = set(range(N_IN_CAT))    # 0..2 in-domain; 3..5 out-of-domain

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS_PER_CAT = 50
    N_QUERIES_PER_DOMAIN = 10
    SEEDS = [11]
else:
    N_DIM = 8192
    V_CONCEPTS_PER_CAT = 200      # V_C=600 total in-domain
    N_QUERIES_PER_DOMAIN = 100
    SEEDS = [11, 13, 19]

V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT  # in-domain library size

# Intent classifier confidence threshold. For prototype-bundle classifiers,
# expected cosine of a member atom to its true bundle-prototype is
#   ~ 1/sqrt(V_PER_CAT) (random-walk expectation),
# so threshold must scale below this floor. At FULL N=8192, V=200/cat,
# expected ~0.071; threshold = 0.03 keeps in-domain queries above-threshold
# while keeping spurious cross-cat hits below-threshold (those scale as
# 1/sqrt(N)=0.011 at FULL). At smoke N=2048, V=50/cat, expected ~0.141;
# threshold remains 0.03 (well below floor). Threshold-INDEPENDENT signal
# is pred in IN_DOMAIN_IDS (rank-based); the threshold is only a refuse
# tiebreaker for low-conf borderline cases.
INTENT_CONF_THRESHOLD = 0.03
AUDIT_MATCH_THRESHOLD = 0.50  # audit-style "library presence" threshold

CONFIG_VERSION = (
    "substrateRefuseGateDomainAware-v1: N=%d V_C_IN=%d N_QUERIES_PER_DOMAIN=%d "
    "in_cats=%s out_cats=%s seeds=%s mode=%s "
    "HP_in_answer>=%.2f HP_out_refuse>=%.2f HP_cv<=%.2f HP_partial_lift>=%.2f "
    "MID_tie_tol=%.2f intent_thr=%.2f audit_thr=%.2f"
) % (
    N_DIM, V_C_IN, N_QUERIES_PER_DOMAIN,
    IN_DOMAIN_CATEGORIES, OUT_DOMAIN_CATEGORIES, SEEDS, RUN_MODE,
    HP_IN_ANSWER_RATE_MIN, HP_OUT_REFUSE_RATE_MIN, HP_CV_MAX,
    HP_PARTIAL_LIFT_MIN, MID_F1_TIE_TOL,
    INTENT_CONF_THRESHOLD, AUDIT_MATCH_THRESHOLD,
)


# =============================================================================
# Substrate primitives
# =============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_in_domain_library(g: np.random.Generator) -> Dict[str, Any]:
    """Build substrate's in-domain concept library + intent classifier prototypes.

    For each in-domain category, sample V_CONCEPTS_PER_CAT unit-norm bipolar
    concept atoms (substrate's library). Category prototype is the L2-normalized
    SUM of its in-domain concept atoms (so each in-domain query's source atom
    has nonzero cosine to its true category prototype; intent classifier can
    discriminate). Out-of-domain category prototypes are built from a separate
    OUT-OF-DOMAIN concept set (V_CONCEPTS_PER_CAT atoms per out-of-domain cat)
    that is NOT loaded into the library E_concepts -- so audit detects absence,
    but intent classifier sees a learnable out-of-domain prototype.

    Substrate (library) E_concepts: [V_C_IN, N_DIM] -- in-domain ONLY.
    intent_prototypes: [N_DOMAINS, N_DIM] -- all 6 cats (3 in + 3 out).
    out_of_domain_atoms: [V_C_OUT, N_DIM] -- for synthesis of out queries only.
    cat_assignment_in: [V_C_IN] in {0..N_IN_CAT-1}.
    cat_assignment_out: [V_C_OUT] in {N_IN_CAT..N_DOMAINS-1}.
    """
    V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
    E_concepts = bipolar(V_C_IN, N_DIM, g)              # IN-DOMAIN library
    out_atoms = bipolar(V_C_OUT, N_DIM, g)              # OUT-OF-DOMAIN seeds (NOT in library)

    cat_assignment_in = np.repeat(np.arange(N_IN_CAT), V_CONCEPTS_PER_CAT)
    cat_assignment_out = np.repeat(np.arange(N_IN_CAT, N_DOMAINS), V_CONCEPTS_PER_CAT)
    assert len(cat_assignment_in) == V_C_IN
    assert len(cat_assignment_out) == V_C_OUT

    # Build intent prototypes via per-category L2-normalized bundle.
    intent_prototypes = np.zeros((N_DOMAINS, N_DIM), dtype=np.float32)
    for c in range(N_IN_CAT):
        members = E_concepts[cat_assignment_in == c]
        proto = members.sum(axis=0)
        intent_prototypes[c] = proto / (np.linalg.norm(proto) + 1e-8)
    for c in range(N_IN_CAT, N_DOMAINS):
        members = out_atoms[cat_assignment_out == c]
        proto = members.sum(axis=0)
        intent_prototypes[c] = proto / (np.linalg.norm(proto) + 1e-8)

    return {
        "E_concepts": E_concepts.astype(np.float32),
        "out_atoms": out_atoms.astype(np.float32),
        "intent_prototypes": intent_prototypes.astype(np.float32),
        "cat_assignment_in": cat_assignment_in.astype(np.int64),
        "cat_assignment_out": cat_assignment_out.astype(np.int64),
    }


def build_query_corpus(g: np.random.Generator,
                        substrate: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Synthesize a balanced query corpus: N_QUERIES_PER_DOMAIN per category.

    In-domain query: pick a known concept from the library E_concepts; bit-flip
    10% of dims so cosine to source ~0.80 (above audit threshold 0.50 and
    intent confidence threshold 0.30).
    Out-of-domain query: pick a known out-of-domain atom from out_atoms (NOT in
    the library); bit-flip 10% of dims. These should yield LOW audit similarity
    (no library match) but HIGH intent confidence to their out-of-domain
    category prototype.
    """
    queries: List[Dict[str, Any]] = []
    E = substrate["E_concepts"]
    out_atoms = substrate["out_atoms"]
    cat_assign = substrate["cat_assignment_in"]
    cat_assign_out = substrate["cat_assignment_out"]

    # Bit-flip noise budget: 10% -> expected cosine to source ~0.80.
    FLIP_FRAC = 0.10
    n_flip = int(N_DIM * FLIP_FRAC)

    # IN-DOMAIN queries: bit-flipped versions of stored concepts (n_flip dims).
    for cat_id in range(N_IN_CAT):
        cat_concept_idxs = np.where(cat_assign == cat_id)[0]
        for _ in range(N_QUERIES_PER_DOMAIN // N_IN_CAT + 1):
            if sum(1 for q in queries if q["is_in_domain"]) >= N_QUERIES_PER_DOMAIN:
                break
            concept_i = int(g.choice(cat_concept_idxs))
            base = E[concept_i].copy()
            # Bit-flip noise: flip n_flip random dims (preserves bipolar shape).
            flip_idxs = g.choice(N_DIM, size=n_flip, replace=False)
            q_vec = base.copy()
            q_vec[flip_idxs] *= -1.0
            # Renormalize (E is unit-norm; flipping preserves L2-norm so this is identity).
            q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-8)
            queries.append({
                "vec": q_vec.astype(np.float32),
                "true_concept": concept_i,
                "true_category": cat_id,
                "is_in_domain": True,
            })

    # Trim/balance in-domain to exactly N_QUERIES_PER_DOMAIN.
    in_queries = [q for q in queries if q["is_in_domain"]][:N_QUERIES_PER_DOMAIN]
    out_queries: List[Dict[str, Any]] = []

    # OUT-OF-DOMAIN queries: bit-flipped versions of out-of-domain atoms.
    # These are absent from library E_concepts; audit should miss them.
    # Intent classifier sees them as the out-of-domain category prototype
    # (above intent confidence threshold).
    for cat_id in range(N_IN_CAT, N_DOMAINS):
        cat_out_idxs = np.where(cat_assign_out == cat_id)[0]
        per_cat = N_QUERIES_PER_DOMAIN // N_OUT_CAT + 1
        for _ in range(per_cat):
            if len(out_queries) >= N_QUERIES_PER_DOMAIN:
                break
            out_i = int(g.choice(cat_out_idxs))
            base = out_atoms[out_i].copy()
            flip_idxs = g.choice(N_DIM, size=n_flip, replace=False)
            q_vec = base.copy()
            q_vec[flip_idxs] *= -1.0
            q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-8)
            out_queries.append({
                "vec": q_vec.astype(np.float32),
                "true_concept": -1,    # no library match
                "true_category": cat_id,
                "is_in_domain": False,
            })
    out_queries = out_queries[:N_QUERIES_PER_DOMAIN]

    return in_queries + out_queries


# =============================================================================
# Substrate primitive: intent classifier
# =============================================================================

def intent_classify(q_vec: np.ndarray, cat_prototypes: np.ndarray
                     ) -> Tuple[int, float]:
    """Return (predicted_cat_id, confidence_score).

    Confidence = cosine sim of q_vec to predicted prototype; q_vec is already
    unit-norm and cat_prototypes are unit-norm, so sims = cat_prototypes @ q_vec.
    """
    sims = cat_prototypes @ q_vec  # [N_DOMAINS]
    pred = int(np.argmax(sims))
    conf = float(sims[pred])
    return pred, conf


def intent_in_domain(q_vec: np.ndarray, cat_prototypes: np.ndarray) -> bool:
    """Intent classifier's verdict on whether query is in-domain.

    Definition: predicted_cat_id < N_IN_CAT means in-domain.
    """
    pred, _ = intent_classify(q_vec, cat_prototypes)
    return pred in IN_DOMAIN_IDS


# =============================================================================
# Substrate primitive: audit (library-presence check)
# =============================================================================

def audit_library_presence(q_vec: np.ndarray, E_concepts: np.ndarray
                            ) -> Tuple[int, float]:
    """Cleanup-style library presence check: return (best_idx, best_sim).

    best_sim is the cosine sim of the query vector to the nearest library atom.
    audit interprets best_sim >= AUDIT_MATCH_THRESHOLD as "present in library."
    """
    sims = E_concepts @ q_vec  # [V_C_IN]
    best_idx = int(np.argmax(sims))
    best_sim = float(sims[best_idx])
    return best_idx, best_sim


# =============================================================================
# Three arms
# =============================================================================

def arm_audit_alone(query: Dict[str, Any], substrate: Dict[str, Any]
                     ) -> Dict[str, Any]:
    """Naive refuse via audit primitive only. NO intent classification."""
    _, best_sim = audit_library_presence(query["vec"], substrate["E_concepts"])
    refused = best_sim < AUDIT_MATCH_THRESHOLD
    answer = None if refused else best_sim
    return {"refused": bool(refused), "audit_sim": best_sim, "answer": answer}


def arm_intent_alone(query: Dict[str, Any], substrate: Dict[str, Any]
                      ) -> Dict[str, Any]:
    """Intent classifier with confidence threshold; refuses if conf below thr."""
    pred, conf = intent_classify(query["vec"], substrate["intent_prototypes"])
    is_in = pred in IN_DOMAIN_IDS
    refused = (conf < INTENT_CONF_THRESHOLD) or (not is_in)
    return {"refused": bool(refused), "intent_pred": pred, "intent_conf": conf}


def arm_audit_plus_intent(query: Dict[str, Any], substrate: Dict[str, Any]
                            ) -> Dict[str, Any]:
    """Composition: intent classifier routes domain; audit checks library presence.

    Refuse if EITHER:
      - intent classifier says out-of-domain (pred >= N_IN_CAT) OR low confidence
      - audit says library-absent (best_sim < AUDIT_MATCH_THRESHOLD)
    Answer (return audit_sim as the retrieved-score) only when BOTH signals agree
    the query is in-domain AND in-library.
    """
    pred, conf = intent_classify(query["vec"], substrate["intent_prototypes"])
    intent_says_in = (pred in IN_DOMAIN_IDS) and (conf >= INTENT_CONF_THRESHOLD)

    _, audit_sim = audit_library_presence(query["vec"], substrate["E_concepts"])
    audit_says_present = audit_sim >= AUDIT_MATCH_THRESHOLD

    refused = not (intent_says_in and audit_says_present)
    return {
        "refused": bool(refused),
        "intent_pred": pred, "intent_conf": conf,
        "audit_sim": audit_sim,
    }


ARMS = {
    "ARM_AUDIT_ALONE": arm_audit_alone,
    "ARM_INTENT_ALONE": arm_intent_alone,
    "ARM_AUDIT_PLUS_INTENT": arm_audit_plus_intent,
}


# =============================================================================
# Evaluation: per-arm in-domain answer-rate + out-of-domain refuse-rate + F1
# =============================================================================

def evaluate_arm(arm_label: str, queries: List[Dict[str, Any]],
                  substrate: Dict[str, Any]) -> Dict[str, Any]:
    """For each query, run the arm; tabulate confusion matrix.

    Definitions:
      - in_answer_rate: fraction of in-domain queries that were NOT refused
        (i.e., the arm answered them).
      - out_refuse_rate: fraction of out-of-domain queries that WERE refused.
      - F1: treat "correctly refused out-of-domain query" as positive class
        for precision/recall:
          true_positive = correctly_refused_out
          false_positive = wrongly_refused_in
          false_negative = wrongly_answered_out
        precision = tp / (tp + fp); recall = tp / (tp + fn)
        F1 = 2*P*R / (P+R) with 0-handling.
    """
    fn_arm = ARMS[arm_label]
    in_total = sum(1 for q in queries if q["is_in_domain"])
    out_total = sum(1 for q in queries if not q["is_in_domain"])
    in_answered = 0
    in_refused = 0
    out_refused = 0
    out_answered = 0
    for q in queries:
        r = fn_arm(q, substrate)
        if q["is_in_domain"]:
            if r["refused"]:
                in_refused += 1
            else:
                in_answered += 1
        else:
            if r["refused"]:
                out_refused += 1
            else:
                out_answered += 1
    in_answer_rate = in_answered / max(in_total, 1)
    out_refuse_rate = out_refused / max(out_total, 1)
    tp = out_refused
    fp = in_refused
    fn = out_answered
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = (2 * precision * recall / max(precision + recall, 1e-9)) if (precision + recall) > 0 else 0.0
    return {
        "in_answer_rate": round(in_answer_rate, 4),
        "out_refuse_rate": round(out_refuse_rate, 4),
        "f1": round(f1, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "confusion": {
            "in_total": in_total, "out_total": out_total,
            "in_answered": in_answered, "in_refused": in_refused,
            "out_refused": out_refused, "out_answered": out_answered,
        },
    }


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)

    # T1: bipolar shape
    x = bipolar(5, 64, g)
    assert x.shape == (5, 64)
    # Norm should be ~1 after L2-normalization
    norms = np.linalg.norm(x, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3), \
        "T1 bipolar not unit-norm: norms=%s" % norms

    # T2: tiny substrate end-to-end
    tiny_n = 256
    tiny_v_per_cat = 5  # tiny library
    global N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, N_QUERIES_PER_DOMAIN
    orig = (N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, N_QUERIES_PER_DOMAIN)
    N_DIM = tiny_n
    V_CONCEPTS_PER_CAT = tiny_v_per_cat
    V_C_IN = tiny_v_per_cat * N_IN_CAT
    N_QUERIES_PER_DOMAIN = 6
    try:
        substrate = build_in_domain_library(np.random.default_rng(1))
        queries = build_query_corpus(np.random.default_rng(2), substrate)
        assert len([q for q in queries if q["is_in_domain"]]) == N_QUERIES_PER_DOMAIN
        assert len([q for q in queries if not q["is_in_domain"]]) == N_QUERIES_PER_DOMAIN

        # T3: intent classifier correctness on trivial in-domain query
        q0 = queries[0]
        assert q0["is_in_domain"]
        pred, conf = intent_classify(q0["vec"], substrate["intent_prototypes"])
        # Cannot assert pred == true_category strictly at tiny N (signal weak)
        # but conf should be a valid float and pred in valid range.
        assert 0 <= pred < N_DOMAINS
        assert -1.0 <= conf <= 1.0
        print("[selftest] T3 PASS: intent_classify pred=%d conf=%.3f" % (pred, conf))

        # T4: audit primitive correctness on in-library concept
        # Use the raw atom (no noise) to confirm cleanup self-id at sigma=0.
        clean_q = {"vec": substrate["E_concepts"][3], "is_in_domain": True,
                    "true_concept": 3, "true_category": 0}
        best_idx, best_sim = audit_library_presence(clean_q["vec"], substrate["E_concepts"])
        assert best_idx == 3, "T4 audit cleanup self-id failed: best_idx=%d" % best_idx
        assert best_sim > 0.99, "T4 audit sim at sigma=0 too low: %.3f" % best_sim
        print("[selftest] T4 PASS: audit cleanup self-id at sigma=0 sim=%.3f" % best_sim)

        # T5: out-of-domain query yields LOW audit sim (no library match)
        out_q = [q for q in queries if not q["is_in_domain"]][0]
        _, out_sim = audit_library_presence(out_q["vec"], substrate["E_concepts"])
        # At tiny scale we can't assert hard threshold; sanity only.
        assert -1.0 <= out_sim <= 1.0
        print("[selftest] T5 PASS: out-of-domain audit sim=%.3f (sanity)" % out_sim)

        # T6: arms run without crash, return refused booleans
        for arm_label in ARMS.keys():
            res = ARMS[arm_label](q0, substrate)
            assert "refused" in res and isinstance(res["refused"], bool)
        print("[selftest] T6 PASS: all 3 arms return refused booleans")

        # T7: evaluate_arm returns expected fields + f1 in [0, 1]
        for arm_label in ARMS.keys():
            r = evaluate_arm(arm_label, queries, substrate)
            assert 0.0 <= r["f1"] <= 1.0, "T7 f1 out of range: %.3f" % r["f1"]
            assert 0.0 <= r["in_answer_rate"] <= 1.0
            assert 0.0 <= r["out_refuse_rate"] <= 1.0
        print("[selftest] T7 PASS: evaluate_arm returns valid metrics for all 3 arms")
    finally:
        N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, N_QUERIES_PER_DOMAIN = orig

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run
# =============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)

    substrate = build_in_domain_library(g)
    queries = build_query_corpus(g, substrate)
    print("  [seed=%d] substrate library (V_C_IN=%d) + %d in-domain + %d out-of-domain queries built"
          % (seed, V_C_IN, sum(1 for q in queries if q["is_in_domain"]),
             sum(1 for q in queries if not q["is_in_domain"])), flush=True)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
        "V_C_IN": V_C_IN, "n_queries_per_domain": N_QUERIES_PER_DOMAIN,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    for arm_label in ARMS.keys():
        t_arm = time.time()
        r = evaluate_arm(arm_label, queries, substrate)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out[arm_label.lower()] = r
        print("  [seed=%d] %s in_answer=%.3f out_refuse=%.3f f1=%.3f t=%.1fs"
              % (seed, arm_label, r["in_answer_rate"], r["out_refuse_rate"],
                 r["f1"], r["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_metric(arm_key: str, metric: str) -> float:
        vals = [p[arm_key][metric] for p in per_seed
                if arm_key in p and isinstance(p[arm_key].get(metric), (int, float))
                and not math.isnan(p[arm_key][metric])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_metric(arm_key: str, metric: str) -> float:
        vals = [p[arm_key][metric] for p in per_seed
                if arm_key in p and isinstance(p[arm_key].get(metric), (int, float))
                and not math.isnan(p[arm_key][metric])]
        if len(vals) < 2:
            return 0.0
        m = float(np.mean(vals))
        return float(np.std(vals) / max(abs(m), 1e-9))

    audit_in = mean_metric("arm_audit_alone", "in_answer_rate")
    audit_out = mean_metric("arm_audit_alone", "out_refuse_rate")
    audit_f1 = mean_metric("arm_audit_alone", "f1")
    intent_in = mean_metric("arm_intent_alone", "in_answer_rate")
    intent_out = mean_metric("arm_intent_alone", "out_refuse_rate")
    intent_f1 = mean_metric("arm_intent_alone", "f1")
    compose_in = mean_metric("arm_audit_plus_intent", "in_answer_rate")
    compose_out = mean_metric("arm_audit_plus_intent", "out_refuse_rate")
    compose_f1 = mean_metric("arm_audit_plus_intent", "f1")
    compose_f1_cv = cv_metric("arm_audit_plus_intent", "f1")

    best_single_f1 = max(audit_f1, intent_f1)

    # PER-ARM SUMMARY (Fix #28).
    summ = ("AUDIT_ALONE[in_answer=%.3f out_refuse=%.3f f1=%.3f] "
            "INTENT_ALONE[in_answer=%.3f out_refuse=%.3f f1=%.3f] "
            "AUDIT+INTENT[in_answer=%.3f out_refuse=%.3f f1=%.3f cv=%.3f] "
            "| best_single_f1=%.3f"
            ) % (
        audit_in, audit_out, audit_f1,
        intent_in, intent_out, intent_f1,
        compose_in, compose_out, compose_f1, compose_f1_cv,
        best_single_f1,
    )

    # Diagnostic: MEDQA failure reproduced flag.
    medqa_flag = audit_out < MEDQA_AUDIT_REFUSE_RATE_THRESHOLD
    if medqa_flag:
        summ += (" | MEDQA_FAILURE_REPRODUCED: AUDIT_ALONE out_refuse=%.3f < %.2f "
                 "(confirms existing medqa REFUTED finding)") % (
                    audit_out, MEDQA_AUDIT_REFUSE_RATE_THRESHOLD)

    # Bands
    hp_chain = (
        compose_in >= HP_IN_ANSWER_RATE_MIN
        and compose_out >= HP_OUT_REFUSE_RATE_MIN
        and compose_f1 > audit_f1 + HP_PARTIAL_LIFT_MIN
        and compose_f1 > intent_f1 + HP_PARTIAL_LIFT_MIN
        and compose_f1_cv <= HP_CV_MAX
    )
    if hp_chain:
        return "HARD_PASS_CHAIN_GRADE_COMPOSITION", \
               "HARD_PASS_CHAIN_GRADE_COMPOSITION: " + summ

    composed_beats_both = (
        compose_f1 > audit_f1 + HP_PARTIAL_LIFT_MIN
        and compose_f1 > intent_f1 + HP_PARTIAL_LIFT_MIN
    )
    if composed_beats_both:
        return "HARD_PASS_PARTIAL", \
               "HARD_PASS_PARTIAL_COMPOSITION_LIFTS_OVER_BOTH: " + summ

    composed_ties = (
        abs(compose_f1 - audit_f1) <= MID_F1_TIE_TOL
        or abs(compose_f1 - intent_f1) <= MID_F1_TIE_TOL
    )
    if composed_ties:
        return "MIDDLE_BAND", \
               "MIDDLE_BAND_COMPOSITION_TIES_BEST_SINGLE: " + summ

    if compose_f1 < best_single_f1:
        return "HARD_FAIL_COMPOSITION_DOESNT_HELP", \
               "HARD_FAIL_COMPOSITION_WORSE_THAN_BEST_SINGLE: " + summ

    return "MIDDLE_BAND", "MIDDLE_BAND_UNCLASSIFIED: " + summ


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C_IN=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C_IN, CONFIG_VERSION), flush=True)
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

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "Domain-aware refuse-gate composition. Intent classifier + audit "
            "primitive compose for domain-specialized refuse. Each primitive "
            "does one job well; composition is the new mechanism. Pre-reg per "
            "preregs/2026-06-25_substrate_refuse_gate_domain_aware_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
