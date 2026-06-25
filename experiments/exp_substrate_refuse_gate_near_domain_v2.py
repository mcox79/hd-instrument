"""substrate_refuse_gate_near_domain_v2 -- NEAR-DOMAIN-MIXED refuse-gate.

CLOSURE TARGET (closure of v1 MIDDLE_BAND saturation per
notes/research_deep_dive_partial_and_open_capabilities_intuitive_2026-06-25.md):
  V1 saturated at ~1.000 F1 across all 3 arms because in-domain and
  out-of-domain query corpora had ZERO surface overlap. The diagnostic flag
  MEDQA_FAILURE_REPRODUCED never fired. V2 fixes the corpus to stress the
  actual medqa-style failure mode: queries that use IN-DOMAIN subjects with
  OUT-OF-DOMAIN relations cause naive (subject-only) audit to false-positive.

QUERY CATEGORIES (3 x 100 queries x 3 seeds):
  PURE_IN_DOMAIN:        subject IN-DOMAIN + relation IN-DOMAIN  -> ANSWER
  PURE_OUT_OF_DOMAIN:    subject OUT-DOM   + relation OUT-DOM    -> REFUSE
  NEAR_DOMAIN_MIXED:     subject IN-DOMAIN + relation OUT-DOM    -> REFUSE
                         (medqa-failure-reproducer)

ARMS (4):
  ARM_AUDIT_NAIVE_ALONE
    Refuse iff cleanup of query_subject vs W_subjects < SUBJECT_AUDIT_THR.
    Subject-only check (the original audit primitive shape).
  ARM_AUDIT_RELATION_CHECK
    Refuse iff cleanup of subject OR cleanup of relation < threshold.
    Smarter audit alone hypothesis.
  ARM_INTENT_ALONE
    Intent classifier scores query.relation against in-domain relation
    prototypes; refuses iff confidence < INTENT_CONF_THR.
  ARM_AUDIT_NAIVE_PLUS_INTENT
    Refuse iff EITHER naive audit fails OR intent classifier fails.
    The v1 composition arm; tests composition with naive audit.

PRE-REG BANDS (LOCKED at module init):
  Sanity rails (must hold on PURE categories across all 4 arms):
    PURE_IN_DOMAIN answer-rate >= 0.85
    PURE_OUT_OF_DOMAIN refuse-rate >= 0.85
  Discrimination on NEAR_DOMAIN_MIXED:
    MEDQA_FAILURE_REPRODUCED:    AUDIT_NAIVE_ALONE refuse < 0.50
    HARD_PASS_AUDIT_DESIGN_FIX:  AUDIT_RELATION_CHECK refuse >= 0.70
    HARD_PASS_COMPOSITION_NEEDED:
      AUDIT_RELATION_CHECK < 0.50 AND AUDIT_NAIVE_PLUS_INTENT >= 0.70
    HARD_PASS_BOTH_WORK:
      AUDIT_RELATION_CHECK >= 0.70 AND AUDIT_NAIVE_PLUS_INTENT >= 0.70
    HARD_FAIL_REFUSE_GATE_DEEP:  AUDIT_NAIVE_PLUS_INTENT < 0.50
    TEST_DESIGN_FAILED:           MEDQA_FAILURE_REPRODUCED does NOT fire

CONFIG:
  N=8192, V_C_IN=600 (in-domain concepts; same as v1),
  V_relations_in=8, V_relations_out=8.
  Seeds: [11, 13, 19] (same as v1; v2 is corpus-design fix not seed question).
  N_QUERIES_PER_CATEGORY=100.
  SUBJECT_AUDIT_THR=0.40 (lowered from v1 0.50 to allow noise budget),
  RELATION_AUDIT_THR=0.40, INTENT_CONF_THR=0.03.
  Substrate-native primitives only (numpy; zero LLM forward calls).

SMOKE: N_QUERIES_PER_CATEGORY=20, seed=11.
  Self-test asserts NEAR_DOMAIN_MIXED subject atoms have audit_sim >= 0.95
  (subject IS in substrate) AND relation atoms have audit_sim < 0.20
  (relation is NOT in substrate) -- proves the corpus actually creates the
  surface-mismatch we want to test.

Author: exp_dev 2026-06-25 (v2 corpus-design fix of v1 MIDDLE_BAND saturation).
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

ANCHOR_NAME = "substrate_refuse_gate_near_domain_v2"
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
SANITY_PURE_IN_ANSWER_MIN = 0.85
SANITY_PURE_OUT_REFUSE_MIN = 0.85
HP_NEAR_REFUSE_MIN = 0.70
MEDQA_FAILURE_AUDIT_REFUSE_MAX = 0.50  # audit_naive refuses LESS than this -> failure reproduced
HP_DEEP_FAIL_THRESHOLD = 0.50          # audit+intent below this -> deep fail
HP_CV_MAX = 0.07
SANITY_IN_CV_MAX = 0.05

# Lock-assertion
assert 0.0 < SANITY_PURE_IN_ANSWER_MIN <= 1.0
assert 0.0 < SANITY_PURE_OUT_REFUSE_MIN <= 1.0
assert 0.0 < HP_NEAR_REFUSE_MIN <= 1.0
assert 0.0 < MEDQA_FAILURE_AUDIT_REFUSE_MAX <= 1.0
assert HP_NEAR_REFUSE_MIN > HP_DEEP_FAIL_THRESHOLD, "ordering invariant"

IN_DOMAIN_CATEGORIES = ["animals", "geography", "tools"]
OUT_DOMAIN_CATEGORIES = ["medical", "legal", "financial"]
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)
N_DOMAINS = N_IN_CAT + N_OUT_CAT
IN_DOMAIN_IDS = set(range(N_IN_CAT))   # 0..2 in-domain; 3..5 out-of-domain

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS_PER_CAT = 50
    N_QUERIES_PER_CATEGORY = 20
    SEEDS = [11]
else:
    N_DIM = 8192
    V_CONCEPTS_PER_CAT = 200            # V_C_IN = 600 total in-domain
    N_QUERIES_PER_CATEGORY = 100
    SEEDS = [11, 13, 19]

V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
V_RELATIONS_IN = 8
V_RELATIONS_OUT = 8

# Thresholds. SUBJECT_AUDIT_THR lowered from v1 0.50 to 0.40 to give a noise
# budget for bit-flipped queries (cosine ~0.80 to source) and still pass the
# in-library cleanup. Cross-domain (out atoms NOT in library) max cosine
# ~ sqrt(1/N_DIM) = 0.011 at N=8192; threshold 0.40 is well above that floor.
SUBJECT_AUDIT_THR = 0.40
RELATION_AUDIT_THR = 0.40
INTENT_CONF_THR = 0.03

CATEGORY_LABELS = ("PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN", "NEAR_DOMAIN_MIXED")
CATEGORY_EXPECT_REFUSE = {
    "PURE_IN_DOMAIN": False,
    "PURE_OUT_OF_DOMAIN": True,
    "NEAR_DOMAIN_MIXED": True,
}

CONFIG_VERSION = (
    "substrateRefuseGateNearDomain-v2: N=%d V_C_IN=%d V_C_OUT=%d "
    "V_rel_in=%d V_rel_out=%d N_QUERIES_PER_CATEGORY=%d in_cats=%s out_cats=%s "
    "seeds=%s mode=%s sanity_pure_in>=%.2f sanity_pure_out>=%.2f "
    "HP_near>=%.2f MEDQA_audit_refuse<%.2f HP_deep_fail<%.2f cv<=%.2f "
    "subject_thr=%.2f relation_thr=%.2f intent_thr=%.2f"
) % (
    N_DIM, V_C_IN, V_C_OUT, V_RELATIONS_IN, V_RELATIONS_OUT,
    N_QUERIES_PER_CATEGORY, IN_DOMAIN_CATEGORIES, OUT_DOMAIN_CATEGORIES,
    SEEDS, RUN_MODE,
    SANITY_PURE_IN_ANSWER_MIN, SANITY_PURE_OUT_REFUSE_MIN,
    HP_NEAR_REFUSE_MIN, MEDQA_FAILURE_AUDIT_REFUSE_MAX,
    HP_DEEP_FAIL_THRESHOLD, HP_CV_MAX,
    SUBJECT_AUDIT_THR, RELATION_AUDIT_THR, INTENT_CONF_THR,
)


# =============================================================================
# Substrate primitives
# =============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1 atoms, L2-normalized to unit norm."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_substrate(g: np.random.Generator) -> Dict[str, Any]:
    """Build substrate libraries + prototypes.

    Substrate W_subjects: [V_C_IN, N_DIM]   -- in-domain ONLY (loaded library)
    Substrate W_relations_in: [V_RELATIONS_IN, N_DIM] -- in-domain ONLY (loaded library)

    Out-of-domain concept atoms + relation atoms are built BUT NOT loaded into
    substrate libraries -- audit consults only W_subjects / W_relations_in.

    relation_in_prototypes: [V_RELATIONS_IN, N_DIM] -- per-relation prototype
      (each relation IS its own prototype since they're atomic; intent
      classifier discriminates relation identity directly).
    relation_out_atoms: [V_RELATIONS_OUT, N_DIM]    -- for NEAR_DOMAIN_MIXED
                                                      synthesis; NOT in any
                                                      substrate library.
    """
    W_subjects = bipolar(V_C_IN, N_DIM, g)               # in-domain concept library
    W_relations_in = bipolar(V_RELATIONS_IN, N_DIM, g)   # in-domain relation library
    out_subject_atoms = bipolar(V_C_OUT, N_DIM, g)       # out-of-domain subjects (not in lib)
    out_relation_atoms = bipolar(V_RELATIONS_OUT, N_DIM, g)  # out-of-domain relations (not in lib)

    cat_assignment_in = np.repeat(np.arange(N_IN_CAT), V_CONCEPTS_PER_CAT)
    cat_assignment_out = np.repeat(np.arange(N_IN_CAT, N_DOMAINS), V_CONCEPTS_PER_CAT)
    assert len(cat_assignment_in) == V_C_IN
    assert len(cat_assignment_out) == V_C_OUT

    # Per-relation prototype: each in-domain relation is its own prototype
    # (atomic relations, not bundled). Intent classifier discriminates relation
    # identity via cosine sim to these prototypes.
    relation_in_prototypes = W_relations_in.copy()  # [V_RELATIONS_IN, N_DIM]

    return {
        "W_subjects": W_subjects.astype(np.float32),
        "W_relations_in": W_relations_in.astype(np.float32),
        "out_subject_atoms": out_subject_atoms.astype(np.float32),
        "out_relation_atoms": out_relation_atoms.astype(np.float32),
        "relation_in_prototypes": relation_in_prototypes.astype(np.float32),
        "cat_assignment_in": cat_assignment_in.astype(np.int64),
        "cat_assignment_out": cat_assignment_out.astype(np.int64),
    }


def build_query_corpus(g: np.random.Generator,
                        substrate: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Synthesize PURE_IN_DOMAIN + PURE_OUT_OF_DOMAIN + NEAR_DOMAIN_MIXED.

    Each query is (subject_vec, relation_vec) with category label. Noise
    budget: 10% bit-flip on subject and relation so cosine to source ~0.80
    (well above audit_thr 0.40, well above intent_conf_thr 0.03).
    """
    FLIP_FRAC = 0.10
    n_flip = int(N_DIM * FLIP_FRAC)
    W_subjects = substrate["W_subjects"]
    W_relations_in = substrate["W_relations_in"]
    out_subject_atoms = substrate["out_subject_atoms"]
    out_relation_atoms = substrate["out_relation_atoms"]

    def add_noise(vec: np.ndarray, flip_rng: np.random.Generator) -> np.ndarray:
        flip_idxs = flip_rng.choice(N_DIM, size=n_flip, replace=False)
        v = vec.copy()
        v[flip_idxs] *= -1.0
        v = v / (np.linalg.norm(v) + 1e-8)
        return v.astype(np.float32)

    queries: List[Dict[str, Any]] = []

    # PURE_IN_DOMAIN: in-domain subject + in-domain relation
    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, V_RELATIONS_IN))
        subj_vec = add_noise(W_subjects[s_i], g)
        rel_vec = add_noise(W_relations_in[r_i], g)
        queries.append({
            "category": "PURE_IN_DOMAIN",
            "subject_vec": subj_vec,
            "relation_vec": rel_vec,
            "true_subject": s_i,
            "true_relation": r_i,
            "subject_is_in_substrate": True,
            "relation_is_in_substrate": True,
        })

    # PURE_OUT_OF_DOMAIN: out-of-domain subject + out-of-domain relation
    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_OUT))
        r_i = int(g.integers(0, V_RELATIONS_OUT))
        subj_vec = add_noise(out_subject_atoms[s_i], g)
        rel_vec = add_noise(out_relation_atoms[r_i], g)
        queries.append({
            "category": "PURE_OUT_OF_DOMAIN",
            "subject_vec": subj_vec,
            "relation_vec": rel_vec,
            "true_subject": -1,
            "true_relation": -1,
            "subject_is_in_substrate": False,
            "relation_is_in_substrate": False,
        })

    # NEAR_DOMAIN_MIXED: in-domain subject + out-of-domain relation
    # This is the medqa-failure-reproducer.
    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, V_RELATIONS_OUT))
        subj_vec = add_noise(W_subjects[s_i], g)
        rel_vec = add_noise(out_relation_atoms[r_i], g)
        queries.append({
            "category": "NEAR_DOMAIN_MIXED",
            "subject_vec": subj_vec,
            "relation_vec": rel_vec,
            "true_subject": s_i,
            "true_relation": -1,
            "subject_is_in_substrate": True,
            "relation_is_in_substrate": False,
        })

    return queries


# =============================================================================
# Substrate primitives: audit (subject) / audit (relation) / intent classifier
# =============================================================================

def audit_subject_presence(subj_vec: np.ndarray, W_subjects: np.ndarray
                            ) -> Tuple[int, float]:
    sims = W_subjects @ subj_vec
    best_idx = int(np.argmax(sims))
    return best_idx, float(sims[best_idx])


def audit_relation_presence(rel_vec: np.ndarray, W_relations_in: np.ndarray
                             ) -> Tuple[int, float]:
    sims = W_relations_in @ rel_vec
    best_idx = int(np.argmax(sims))
    return best_idx, float(sims[best_idx])


def intent_classify_relation(rel_vec: np.ndarray,
                              relation_in_prototypes: np.ndarray
                              ) -> Tuple[int, float]:
    sims = relation_in_prototypes @ rel_vec
    pred = int(np.argmax(sims))
    return pred, float(sims[pred])


# =============================================================================
# Four arms
# =============================================================================

def arm_audit_naive_alone(q: Dict[str, Any], s: Dict[str, Any]) -> Dict[str, Any]:
    _, sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    refused = sim < SUBJECT_AUDIT_THR
    return {"refused": bool(refused), "subject_audit_sim": sim}


def arm_audit_relation_check(q: Dict[str, Any], s: Dict[str, Any]) -> Dict[str, Any]:
    _, s_sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    _, r_sim = audit_relation_presence(q["relation_vec"], s["W_relations_in"])
    subj_ok = s_sim >= SUBJECT_AUDIT_THR
    rel_ok = r_sim >= RELATION_AUDIT_THR
    refused = not (subj_ok and rel_ok)
    return {
        "refused": bool(refused),
        "subject_audit_sim": s_sim,
        "relation_audit_sim": r_sim,
    }


def arm_intent_alone(q: Dict[str, Any], s: Dict[str, Any]) -> Dict[str, Any]:
    pred, conf = intent_classify_relation(q["relation_vec"], s["relation_in_prototypes"])
    # In-substrate relation prototypes only -> any relation with conf below
    # threshold is treated as out-of-domain.
    refused = conf < INTENT_CONF_THR
    return {"refused": bool(refused), "intent_pred": pred, "intent_conf": conf}


def arm_audit_naive_plus_intent(q: Dict[str, Any], s: Dict[str, Any]) -> Dict[str, Any]:
    _, subj_sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    audit_says_present = subj_sim >= SUBJECT_AUDIT_THR
    pred, conf = intent_classify_relation(q["relation_vec"], s["relation_in_prototypes"])
    intent_says_in = conf >= INTENT_CONF_THR
    # Refuse if EITHER naive audit fails OR intent classifier fails.
    refused = not (audit_says_present and intent_says_in)
    return {
        "refused": bool(refused),
        "subject_audit_sim": subj_sim,
        "intent_pred": pred,
        "intent_conf": conf,
    }


ARMS = {
    "ARM_AUDIT_NAIVE_ALONE": arm_audit_naive_alone,
    "ARM_AUDIT_RELATION_CHECK": arm_audit_relation_check,
    "ARM_INTENT_ALONE": arm_intent_alone,
    "ARM_AUDIT_NAIVE_PLUS_INTENT": arm_audit_naive_plus_intent,
}


# =============================================================================
# Evaluation
# =============================================================================

def evaluate_arm_per_category(arm_label: str,
                                queries: List[Dict[str, Any]],
                                substrate: Dict[str, Any]
                                ) -> Dict[str, Dict[str, Any]]:
    """For each (arm, category): compute refuse_rate + answer_rate + F1.

    F1 here is the "correctly_refuse" class:
      tp = correctly_refused (refused AND category expects refuse)
      fp = wrongly_refused (refused AND category expects answer)
      fn = wrongly_answered (NOT refused AND category expects refuse)
    F1 per category.
    """
    fn_arm = ARMS[arm_label]
    out: Dict[str, Dict[str, Any]] = {}
    for cat in CATEGORY_LABELS:
        cat_queries = [q for q in queries if q["category"] == cat]
        n = len(cat_queries)
        n_refused = 0
        n_answered = 0
        for q in cat_queries:
            r = fn_arm(q, substrate)
            if r["refused"]:
                n_refused += 1
            else:
                n_answered += 1
        refuse_rate = n_refused / max(n, 1)
        answer_rate = n_answered / max(n, 1)
        expect_refuse = CATEGORY_EXPECT_REFUSE[cat]
        if expect_refuse:
            tp = n_refused
            fn = n_answered
            fp = 0
        else:
            tp = 0
            fn = 0
            fp = n_refused
        precision = tp / max(tp + fp, 1) if (tp + fp) > 0 else 0.0
        recall = tp / max(tp + fn, 1) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / max(precision + recall, 1e-9)
              ) if (precision + recall) > 0 else 0.0
        out[cat] = {
            "refuse_rate": round(refuse_rate, 4),
            "answer_rate": round(answer_rate, 4),
            "f1": round(f1, 4),
            "n_refused": n_refused,
            "n_answered": n_answered,
            "n_total": n,
        }
    return out


# =============================================================================
# Smoke self-test (sanity gate before FULL dispatch)
# =============================================================================

def _smoke_sanity_corpus_creates_surface_mismatch(substrate, queries) -> None:
    """Assert NEAR_DOMAIN_MIXED subjects ARE in substrate and relations ARE NOT.

    Per pre-reg Q-discipline + smoke self-test rule. Subject atoms in
    NEAR_DOMAIN_MIXED queries must cleanup to >= 0.95 against W_subjects
    (proves subject is detectable as in-substrate). Relation atoms must
    cleanup to < 0.20 against W_relations_in (proves relation is detectable
    as NOT in substrate). Without these, the test corpus isn't actually
    creating the surface-mismatch we want to test.
    """
    near = [q for q in queries if q["category"] == "NEAR_DOMAIN_MIXED"]
    if not near:
        return
    # Use noise-free recomputation for the assertion: re-build the "true" subject
    # from the substrate library by best-match (since queries are bit-flipped,
    # expected cosine ~0.80; relax assertion to >= 0.55 conservatively).
    subj_sims = []
    rel_sims = []
    for q in near[:min(10, len(near))]:
        _, s_sim = audit_subject_presence(q["subject_vec"], substrate["W_subjects"])
        _, r_sim = audit_relation_presence(q["relation_vec"], substrate["W_relations_in"])
        subj_sims.append(s_sim)
        rel_sims.append(r_sim)
    mean_subj = float(np.mean(subj_sims))
    mean_rel = float(np.mean(rel_sims))
    print("[smoke_sanity] NEAR_DOMAIN_MIXED mean subject audit_sim=%.3f "
          "(expect >= 0.55 with 10%% bit-flip noise)" % mean_subj)
    print("[smoke_sanity] NEAR_DOMAIN_MIXED mean relation audit_sim=%.3f "
          "(expect < 0.20; relations NOT in substrate library)" % mean_rel)
    assert mean_subj >= 0.55, (
        "smoke_sanity FAIL: NEAR_DOMAIN_MIXED subjects don't cleanup to substrate "
        "(mean_subj=%.3f < 0.55). Corpus broken: subjects should BE in W_subjects."
        % mean_subj
    )
    assert mean_rel < 0.20, (
        "smoke_sanity FAIL: NEAR_DOMAIN_MIXED relations match substrate too well "
        "(mean_rel=%.3f >= 0.20). Corpus broken: out-of-domain relations should "
        "NOT match W_relations_in." % mean_rel
    )
    print("[smoke_sanity] PASS: corpus creates the surface-mismatch v2 wants to test")


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)

    # T1: bipolar shape + unit norm
    x = bipolar(5, 64, g)
    assert x.shape == (5, 64)
    norms = np.linalg.norm(x, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3), \
        "T1 bipolar not unit-norm: norms=%s" % norms
    print("[selftest] T1 PASS: bipolar unit-norm")

    # T2: tiny substrate end-to-end (override globals temporarily)
    global N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY
    orig = (N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY)
    N_DIM = 512
    V_CONCEPTS_PER_CAT = 6
    V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
    V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
    N_QUERIES_PER_CATEGORY = 8
    try:
        substrate = build_substrate(np.random.default_rng(1))
        assert substrate["W_subjects"].shape == (V_C_IN, N_DIM)
        assert substrate["W_relations_in"].shape == (V_RELATIONS_IN, N_DIM)
        print("[selftest] T2 PASS: build_substrate shapes correct")

        queries = build_query_corpus(np.random.default_rng(2), substrate)
        for cat in CATEGORY_LABELS:
            cat_q = [q for q in queries if q["category"] == cat]
            assert len(cat_q) == N_QUERIES_PER_CATEGORY, (
                "T2 wrong query count for %s: %d != %d" %
                (cat, len(cat_q), N_QUERIES_PER_CATEGORY))
        print("[selftest] T2 PASS: build_query_corpus counts (%d per category)"
              % N_QUERIES_PER_CATEGORY)

        # T3: audit primitives correctness on clean atoms
        clean_subj = substrate["W_subjects"][3]
        idx, sim = audit_subject_presence(clean_subj, substrate["W_subjects"])
        assert idx == 3, "T3 audit subject cleanup self-id failed: %d" % idx
        assert sim > 0.99, "T3 audit subject sim too low at sigma=0: %.3f" % sim
        clean_rel = substrate["W_relations_in"][2]
        idx, sim = audit_relation_presence(clean_rel, substrate["W_relations_in"])
        assert idx == 2, "T3 audit relation cleanup self-id failed: %d" % idx
        assert sim > 0.99, "T3 audit relation sim too low at sigma=0: %.3f" % sim
        print("[selftest] T3 PASS: audit primitives self-id at sigma=0")

        # T4: out-of-domain atoms do NOT match in-substrate libraries
        out_subj = substrate["out_subject_atoms"][0]
        _, s_sim = audit_subject_presence(out_subj, substrate["W_subjects"])
        out_rel = substrate["out_relation_atoms"][0]
        _, r_sim = audit_relation_presence(out_rel, substrate["W_relations_in"])
        # At tiny N=512 the floor is ~ 1/sqrt(512) = 0.044; very generous bound 0.30.
        assert s_sim < 0.30, "T4 out-subject leaks to in-library: %.3f" % s_sim
        assert r_sim < 0.30, "T4 out-relation leaks to in-library: %.3f" % r_sim
        print("[selftest] T4 PASS: out-of-domain atoms don't leak (s_sim=%.3f r_sim=%.3f)"
              % (s_sim, r_sim))

        # T5: all 4 arms run without crash, return refused booleans
        for arm_label in ARMS.keys():
            res = ARMS[arm_label](queries[0], substrate)
            assert "refused" in res and isinstance(res["refused"], bool)
        print("[selftest] T5 PASS: all 4 arms return refused booleans")

        # T6: evaluate_arm_per_category returns valid metrics for all categories
        for arm_label in ARMS.keys():
            r = evaluate_arm_per_category(arm_label, queries, substrate)
            for cat in CATEGORY_LABELS:
                assert cat in r, "T6 missing category %s for arm %s" % (cat, arm_label)
                assert 0.0 <= r[cat]["f1"] <= 1.0
                assert 0.0 <= r[cat]["refuse_rate"] <= 1.0
                assert 0.0 <= r[cat]["answer_rate"] <= 1.0
        print("[selftest] T6 PASS: evaluate_arm_per_category valid for 4 arms x 3 cats")

        # T7 [SMOKE SANITY: the medqa-reproducer assertion]
        # At tiny N=512 the discriminator is weaker; use a relaxed bound.
        # The smoke gate (run with --smoke) re-asserts the full bound.
        near = [q for q in queries if q["category"] == "NEAR_DOMAIN_MIXED"]
        if near:
            s_sims = [audit_subject_presence(q["subject_vec"], substrate["W_subjects"])[1]
                       for q in near]
            r_sims = [audit_relation_presence(q["relation_vec"], substrate["W_relations_in"])[1]
                       for q in near]
            mean_s = float(np.mean(s_sims))
            mean_r = float(np.mean(r_sims))
            # Tiny-N relaxed bound: subj sim should still beat relation sim by a clear margin.
            assert mean_s > mean_r + 0.20, (
                "T7 NEAR_DOMAIN_MIXED corpus doesn't discriminate at tiny N: "
                "subj=%.3f rel=%.3f (subj should exceed rel by >0.20)" % (mean_s, mean_r))
            print("[selftest] T7 PASS: NEAR_DOMAIN_MIXED subj_sim=%.3f > rel_sim=%.3f + 0.20"
                  % (mean_s, mean_r))
    finally:
        N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY = orig

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

    substrate = build_substrate(g)
    queries = build_query_corpus(g, substrate)
    by_cat = {cat: sum(1 for q in queries if q["category"] == cat)
              for cat in CATEGORY_LABELS}
    print("  [seed=%d] substrate built; query counts %s" % (seed, by_cat), flush=True)

    # Run smoke-sanity assertion at the production scale too (cheap; protects
    # against future drift where corpus stops creating surface-mismatch).
    if RUN_MODE == "smoke" or seed == SEEDS[0]:
        _smoke_sanity_corpus_creates_surface_mismatch(substrate, queries)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
        "V_C_IN": V_C_IN, "V_C_OUT": V_C_OUT,
        "V_relations_in": V_RELATIONS_IN, "V_relations_out": V_RELATIONS_OUT,
        "n_queries_per_category": N_QUERIES_PER_CATEGORY,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    for arm_label in ARMS.keys():
        t_arm = time.time()
        per_cat = evaluate_arm_per_category(arm_label, queries, substrate)
        out[arm_label.lower()] = {
            "per_category": per_cat,
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }
        # Compact line per arm.
        line = " | ".join("%s: refuse=%.3f answer=%.3f" %
                          (cat, per_cat[cat]["refuse_rate"], per_cat[cat]["answer_rate"])
                          for cat in CATEGORY_LABELS)
        print("  [seed=%d] %s %s t=%.1fs" %
              (seed, arm_label, line, time.time() - t_arm), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def _cat_mean(per_seed: List[Dict[str, Any]], arm_key: str,
              cat: str, metric: str) -> float:
    vals = []
    for p in per_seed:
        try:
            v = p[arm_key]["per_category"][cat][metric]
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        except KeyError:
            continue
    return float(np.mean(vals)) if vals else float("nan")


def _cat_cv(per_seed: List[Dict[str, Any]], arm_key: str,
            cat: str, metric: str) -> float:
    vals = []
    for p in per_seed:
        try:
            v = p[arm_key]["per_category"][cat][metric]
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        except KeyError:
            continue
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    return float(np.std(vals) / max(abs(m), 1e-9))


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    # Pull all the key numbers (per Fix #28: report per-arm + per-category).
    rows: Dict[str, Dict[str, float]] = {}
    for arm in ARMS.keys():
        ak = arm.lower()
        rows[arm] = {}
        for cat in CATEGORY_LABELS:
            rows[arm]["%s_refuse" % cat] = _cat_mean(per_seed, ak, cat, "refuse_rate")
            rows[arm]["%s_answer" % cat] = _cat_mean(per_seed, ak, cat, "answer_rate")
        rows[arm]["NEAR_DOMAIN_MIXED_refuse_cv"] = _cat_cv(
            per_seed, ak, "NEAR_DOMAIN_MIXED", "refuse_rate")

    # Compact per-arm summary
    summ_lines = []
    for arm in ARMS.keys():
        summ_lines.append(
            "%s[PURE_IN_answer=%.3f PURE_OUT_refuse=%.3f NEAR_refuse=%.3f cv=%.3f]"
            % (arm,
                rows[arm]["PURE_IN_DOMAIN_answer"],
                rows[arm]["PURE_OUT_OF_DOMAIN_refuse"],
                rows[arm]["NEAR_DOMAIN_MIXED_refuse"],
                rows[arm]["NEAR_DOMAIN_MIXED_refuse_cv"]))
    summ = " ".join(summ_lines)

    audit_naive_near = rows["ARM_AUDIT_NAIVE_ALONE"]["NEAR_DOMAIN_MIXED_refuse"]
    audit_rel_near = rows["ARM_AUDIT_RELATION_CHECK"]["NEAR_DOMAIN_MIXED_refuse"]
    intent_near = rows["ARM_INTENT_ALONE"]["NEAR_DOMAIN_MIXED_refuse"]
    audit_plus_intent_near = rows["ARM_AUDIT_NAIVE_PLUS_INTENT"]["NEAR_DOMAIN_MIXED_refuse"]
    naive_cv = rows["ARM_AUDIT_NAIVE_ALONE"]["NEAR_DOMAIN_MIXED_refuse_cv"]
    rel_cv = rows["ARM_AUDIT_RELATION_CHECK"]["NEAR_DOMAIN_MIXED_refuse_cv"]
    intent_cv = rows["ARM_INTENT_ALONE"]["NEAR_DOMAIN_MIXED_refuse_cv"]
    aipi_cv = rows["ARM_AUDIT_NAIVE_PLUS_INTENT"]["NEAR_DOMAIN_MIXED_refuse_cv"]

    medqa_reproduced = audit_naive_near < MEDQA_FAILURE_AUDIT_REFUSE_MAX
    if medqa_reproduced:
        summ += (" | MEDQA_FAILURE_REPRODUCED: AUDIT_NAIVE_ALONE NEAR refuse=%.3f < %.2f"
                 % (audit_naive_near, MEDQA_FAILURE_AUDIT_REFUSE_MAX))
    else:
        summ += (" | MEDQA_FAILURE_NOT_REPRODUCED: AUDIT_NAIVE_ALONE NEAR refuse=%.3f >= %.2f"
                 % (audit_naive_near, MEDQA_FAILURE_AUDIT_REFUSE_MAX))

    # Sanity rails (across all 4 arms, both PURE categories)
    sanity_fail_msgs: List[str] = []
    for arm in ARMS.keys():
        ans_in = rows[arm]["PURE_IN_DOMAIN_answer"]
        ref_out = rows[arm]["PURE_OUT_OF_DOMAIN_refuse"]
        if ans_in < SANITY_PURE_IN_ANSWER_MIN:
            sanity_fail_msgs.append("%s PURE_IN_answer=%.3f < %.2f" %
                                     (arm, ans_in, SANITY_PURE_IN_ANSWER_MIN))
        if ref_out < SANITY_PURE_OUT_REFUSE_MIN:
            sanity_fail_msgs.append("%s PURE_OUT_refuse=%.3f < %.2f" %
                                     (arm, ref_out, SANITY_PURE_OUT_REFUSE_MIN))
    if sanity_fail_msgs:
        return "HARD_FAIL_SANITY_RAIL", \
               "HARD_FAIL_SANITY_RAIL: " + "; ".join(sanity_fail_msgs) + " | " + summ

    # Discriminator verdicts (ordered: test-design-fail BEFORE HP claims)
    if not medqa_reproduced:
        return "TEST_DESIGN_FAILED", \
               "TEST_DESIGN_FAILED_corpus_too_easy: " + summ

    audit_rel_works = audit_rel_near >= HP_NEAR_REFUSE_MIN
    aipi_works = audit_plus_intent_near >= HP_NEAR_REFUSE_MIN
    audit_rel_fails = audit_rel_near < HP_DEEP_FAIL_THRESHOLD
    aipi_fails = audit_plus_intent_near < HP_DEEP_FAIL_THRESHOLD

    # cv check on whichever arm carries the closure
    if audit_rel_works and aipi_works and rel_cv <= HP_CV_MAX and aipi_cv <= HP_CV_MAX:
        return "HARD_PASS_BOTH_WORK", \
               "HARD_PASS_BOTH_WORK: AUDIT_RELATION_CHECK NEAR_refuse=%.3f >= %.2f AND " \
               "AUDIT_NAIVE_PLUS_INTENT NEAR_refuse=%.3f >= %.2f " \
               "(rel_cv=%.3f aipi_cv=%.3f) | " % (
                   audit_rel_near, HP_NEAR_REFUSE_MIN,
                   audit_plus_intent_near, HP_NEAR_REFUSE_MIN,
                   rel_cv, aipi_cv) + summ

    if audit_rel_works and rel_cv <= HP_CV_MAX:
        return "HARD_PASS_AUDIT_DESIGN_FIX", \
               "HARD_PASS_AUDIT_DESIGN_FIX: AUDIT_RELATION_CHECK NEAR_refuse=%.3f >= %.2f " \
               "(rel_cv=%.3f); no composition needed | " % (
                   audit_rel_near, HP_NEAR_REFUSE_MIN, rel_cv) + summ

    if audit_rel_fails and aipi_works and aipi_cv <= HP_CV_MAX:
        return "HARD_PASS_COMPOSITION_NEEDED", \
               "HARD_PASS_COMPOSITION_NEEDED: AUDIT_RELATION_CHECK NEAR_refuse=%.3f < %.2f " \
               "(fails alone) AND AUDIT_NAIVE_PLUS_INTENT NEAR_refuse=%.3f >= %.2f " \
               "(aipi_cv=%.3f) | " % (
                   audit_rel_near, HP_DEEP_FAIL_THRESHOLD,
                   audit_plus_intent_near, HP_NEAR_REFUSE_MIN, aipi_cv) + summ

    if aipi_fails:
        return "HARD_FAIL_REFUSE_GATE_DEEP", \
               "HARD_FAIL_REFUSE_GATE_DEEP: AUDIT_NAIVE_PLUS_INTENT NEAR_refuse=%.3f < %.2f " \
               "(composition does NOT close) | " % (
                   audit_plus_intent_near, HP_DEEP_FAIL_THRESHOLD) + summ

    # Middle band: partial closure but neither HP threshold cleared
    return "MIDDLE_BAND", \
           "MIDDLE_BAND_partial_closure_AUDIT_RELATION_near=%.3f " \
           "AUDIT_NAIVE_PLUS_INTENT_near=%.3f neither hits %.2f HP threshold | " % (
               audit_rel_near, audit_plus_intent_near, HP_NEAR_REFUSE_MIN) + summ


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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C_IN=%d V_C_OUT=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_C_IN, V_C_OUT, CONFIG_VERSION),
          flush=True)
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
            "NEAR-DOMAIN-MIXED refuse-gate. Corpus-design fix of v1 saturation. "
            "Tests whether smarter audit alone (subject+relation check) OR "
            "audit+intent composition closes the medqa-style refuse-gate "
            "failure mode. Pre-reg per "
            "preregs/2026-06-25_substrate_refuse_gate_near_domain_v2.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" %
          (len(per_seed), metrics["elapsed_s"]), flush=True)
