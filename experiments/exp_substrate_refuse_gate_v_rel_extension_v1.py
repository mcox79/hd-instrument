"""substrate_refuse_gate_v_rel_extension_v1 -- V_REL envelope extension of v2 (chain-grade at V_REL=8 rail).

PROMOTION CONTEXT (USER + Research DRILL 1 ITEM 8, 2026-06-25):
  v2 (`exp_substrate_refuse_gate_near_domain_v2`) chain-grade-CONFIRMED HARD_PASS_BOTH_WORK at
  V_REL_IN=V_REL_OUT=8 (envelope rail). DRILL 1 ranks this Tier S #1 by P=0.65 / wall ~1h CPU /
  closes a load-bearing Stage 3 envelope. Cleanup envelope says N=8192 chain-grades V<=4000 so
  V_REL extension SHOULD chain-grade trivially to 500-1000; cliff at 2000+ when cleanup ratio drops.

v1 DESIGN (envelope-extension sweep, single mechanism):
  Same NEAR-DOMAIN-MIXED 3-arm discriminator as v2 (NAIVE_ALONE / RELATION_CHECK / NAIVE_PLUS_INTENT)
  Sweep V_REL ∈ {8 (rail), 16, 32, 64, 128, 256, 512} -- 7 V_REL points
  V_REL_IN = V_REL_OUT for each point (symmetric scaling)
  All other config matched to v2 (N=8192, V_C_IN=600, N_QUERIES_PER_CATEGORY=100, seeds [11,13,19])
  At each V_REL: ARM_AUDIT_RELATION_CHECK is the chain-grade mechanism under test

EXPECTED OUTCOMES per DRILL 1 P=0.65:
  HARD_PASS_V_REL_EXTENSION (chain-grade at V_REL=256+):
    at V_REL=256: in_answer >= 0.85 AND near_refuse >= 0.85 AND cv <= 0.05 (RELATION_CHECK arm)
  CHAIN_GRADE_AT_CLIFF_X:
    passes at one of {64, 128} cliffs at higher (envelope extends but bounded)
  HARD_FAIL_V_REL_CLIFF_AT_64:
    doesn't extend past V_REL=64 (relation cleanup degrades earlier than predicted)

META_M6: NAIVE_ALONE baseline DERIVED in-cell at SAME V_REL (not copied from v2's V_REL=8 baseline)
META_M7: smoke matches full on N + V_C_IN + N_QUERIES (capacity-sensitive); only SEEDS reduce
Q-discipline guard: if RELATION_CHECK saturates >= 0.995 at ALL V_REL up to 512, BIAS-Q flag fires
  (corpus regime too easy; recommend V_REL=1000+ extension)

CONFIG (matched to v2 envelope):
  N_DIM = 8192 (matches v2)
  V_CONCEPTS_PER_CAT = 200 (V_C_IN = 600 in-domain total; same as v2)
  N_QUERIES_PER_CATEGORY = 100 (matches v2)
  Seeds [11, 13, 19] (matches v2; cross-cell consistent)
  V_REL_SWEEP = [8, 16, 32, 64, 128, 256, 512]
  SUBJECT_AUDIT_THR=0.40 RELATION_AUDIT_THR=0.40 INTENT_CONF_THR=0.03 (matches v2)
  Substrate-native primitives only (numpy; zero LLM forward calls)

SMOKE: N=2048, V_CONCEPTS_PER_CAT=50, N_QUERIES=20, seeds=[11], V_REL_SWEEP=[8, 64, 256] (3 points only)
  Self-test asserts T1-T7 from v2 + T8 (V_REL=64 smoke shows RELATION_CHECK >= 0.70 at smoke scale)

Author: exp_dev 2026-06-25 (v1 envelope extension from v2 chain-grade rail).
ASCII-only; per-(seed,V_REL) checkpoint; substrate-only.
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
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_refuse_gate_v_rel_extension_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)
SANITY_PURE_IN_ANSWER_MIN = 0.85
SANITY_PURE_OUT_REFUSE_MIN = 0.85
HP_NEAR_REFUSE_MIN = 0.85          # chain-grade floor at V_REL=256 (matches drill spec)
HP_CV_MAX = 0.05                    # tighter than v2's 0.07 (envelope-extension is harder)
HP_PARTIAL_NEAR_REFUSE_MIN = 0.70   # MIDDLE_BAND floor (v2's pass threshold)
Q_SUSPECT_SATURATION = 0.995

# Lock-assertions
assert 0.0 < SANITY_PURE_IN_ANSWER_MIN <= 1.0
assert 0.0 < SANITY_PURE_OUT_REFUSE_MIN <= 1.0
assert 0.0 < HP_NEAR_REFUSE_MIN <= 1.0
assert HP_NEAR_REFUSE_MIN > HP_PARTIAL_NEAR_REFUSE_MIN, "ordering invariant"
assert HP_PARTIAL_NEAR_REFUSE_MIN > 0.5, "partial band above coin-flip"

IN_DOMAIN_CATEGORIES = ["animals", "geography", "tools"]
OUT_DOMAIN_CATEGORIES = ["medical", "legal", "financial"]
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)
N_DOMAINS = N_IN_CAT + N_OUT_CAT
IN_DOMAIN_IDS = set(range(N_IN_CAT))

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS_PER_CAT = 50
    N_QUERIES_PER_CATEGORY = 20
    SEEDS = [11]
    V_REL_SWEEP = [8, 64, 256]  # 3 points: rail + mid + frontier
else:
    N_DIM = 8192
    V_CONCEPTS_PER_CAT = 200            # V_C_IN = 600 total (matches v2)
    N_QUERIES_PER_CATEGORY = 100
    SEEDS = [11, 13, 19]
    V_REL_SWEEP = [8, 16, 32, 64, 128, 256, 512]  # 7 points (rail + 6 extension)

V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT

# Thresholds (matched to v2)
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
    "substrateRefuseGateVrelExtension-v1: N=%d V_C_IN=%d V_C_OUT=%d "
    "V_REL_SWEEP=%s N_QUERIES_PER_CATEGORY=%d seeds=%s mode=%s "
    "sanity_in>=%.2f sanity_out>=%.2f HP_near>=%.2f HP_partial>=%.2f cv<=%.2f "
    "subject_thr=%.2f relation_thr=%.2f intent_thr=%.2f"
) % (
    N_DIM, V_C_IN, V_C_OUT, V_REL_SWEEP, N_QUERIES_PER_CATEGORY,
    SEEDS, RUN_MODE,
    SANITY_PURE_IN_ANSWER_MIN, SANITY_PURE_OUT_REFUSE_MIN,
    HP_NEAR_REFUSE_MIN, HP_PARTIAL_NEAR_REFUSE_MIN, HP_CV_MAX,
    SUBJECT_AUDIT_THR, RELATION_AUDIT_THR, INTENT_CONF_THR,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_substrate(g: np.random.Generator, v_rel_in: int, v_rel_out: int) -> Dict[str, Any]:
    W_subjects = bipolar(V_C_IN, N_DIM, g)
    W_relations_in = bipolar(v_rel_in, N_DIM, g)
    out_subject_atoms = bipolar(V_C_OUT, N_DIM, g)
    out_relation_atoms = bipolar(v_rel_out, N_DIM, g)

    cat_assignment_in = np.repeat(np.arange(N_IN_CAT), V_CONCEPTS_PER_CAT)
    cat_assignment_out = np.repeat(np.arange(N_IN_CAT, N_DOMAINS), V_CONCEPTS_PER_CAT)

    relation_in_prototypes = W_relations_in.copy()

    return {
        "W_subjects": W_subjects.astype(np.float32),
        "W_relations_in": W_relations_in.astype(np.float32),
        "out_subject_atoms": out_subject_atoms.astype(np.float32),
        "out_relation_atoms": out_relation_atoms.astype(np.float32),
        "relation_in_prototypes": relation_in_prototypes.astype(np.float32),
        "cat_assignment_in": cat_assignment_in.astype(np.int64),
        "cat_assignment_out": cat_assignment_out.astype(np.int64),
        "V_RELATIONS_IN": v_rel_in,
        "V_RELATIONS_OUT": v_rel_out,
    }


def build_query_corpus(g: np.random.Generator,
                        substrate: Dict[str, Any]) -> List[Dict[str, Any]]:
    FLIP_FRAC = 0.10
    n_flip = int(N_DIM * FLIP_FRAC)
    W_subjects = substrate["W_subjects"]
    W_relations_in = substrate["W_relations_in"]
    out_subject_atoms = substrate["out_subject_atoms"]
    out_relation_atoms = substrate["out_relation_atoms"]
    v_rel_in = substrate["V_RELATIONS_IN"]
    v_rel_out = substrate["V_RELATIONS_OUT"]

    def add_noise(vec: np.ndarray, flip_rng: np.random.Generator) -> np.ndarray:
        flip_idxs = flip_rng.choice(N_DIM, size=n_flip, replace=False)
        v = vec.copy()
        v[flip_idxs] *= -1.0
        v = v / (np.linalg.norm(v) + 1e-8)
        return v.astype(np.float32)

    queries: List[Dict[str, Any]] = []

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, v_rel_in))
        queries.append({
            "category": "PURE_IN_DOMAIN",
            "subject_vec": add_noise(W_subjects[s_i], g),
            "relation_vec": add_noise(W_relations_in[r_i], g),
            "subject_is_in_substrate": True,
            "relation_is_in_substrate": True,
        })

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_OUT))
        r_i = int(g.integers(0, v_rel_out))
        queries.append({
            "category": "PURE_OUT_OF_DOMAIN",
            "subject_vec": add_noise(out_subject_atoms[s_i], g),
            "relation_vec": add_noise(out_relation_atoms[r_i], g),
            "subject_is_in_substrate": False,
            "relation_is_in_substrate": False,
        })

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, v_rel_out))
        queries.append({
            "category": "NEAR_DOMAIN_MIXED",
            "subject_vec": add_noise(W_subjects[s_i], g),
            "relation_vec": add_noise(out_relation_atoms[r_i], g),
            "subject_is_in_substrate": True,
            "relation_is_in_substrate": False,
        })

    return queries


def audit_subject_presence(subj_vec, W_subjects):
    sims = W_subjects @ subj_vec
    best_idx = int(np.argmax(sims))
    return best_idx, float(sims[best_idx])


def audit_relation_presence(rel_vec, W_relations_in):
    sims = W_relations_in @ rel_vec
    best_idx = int(np.argmax(sims))
    return best_idx, float(sims[best_idx])


def intent_classify_relation(rel_vec, relation_in_prototypes):
    sims = relation_in_prototypes @ rel_vec
    pred = int(np.argmax(sims))
    return pred, float(sims[pred])


def arm_audit_naive_alone(q, s):
    _, sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    return {"refused": bool(sim < SUBJECT_AUDIT_THR), "subject_audit_sim": sim}


def arm_audit_relation_check(q, s):
    _, s_sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    _, r_sim = audit_relation_presence(q["relation_vec"], s["W_relations_in"])
    subj_ok = s_sim >= SUBJECT_AUDIT_THR
    rel_ok = r_sim >= RELATION_AUDIT_THR
    return {"refused": bool(not (subj_ok and rel_ok)),
            "subject_audit_sim": s_sim, "relation_audit_sim": r_sim}


def arm_audit_naive_plus_intent(q, s):
    _, subj_sim = audit_subject_presence(q["subject_vec"], s["W_subjects"])
    audit_says_present = subj_sim >= SUBJECT_AUDIT_THR
    pred, conf = intent_classify_relation(q["relation_vec"], s["relation_in_prototypes"])
    intent_says_in = conf >= INTENT_CONF_THR
    return {"refused": bool(not (audit_says_present and intent_says_in)),
            "subject_audit_sim": subj_sim, "intent_pred": pred, "intent_conf": conf}


ARMS = {
    "ARM_AUDIT_NAIVE_ALONE": arm_audit_naive_alone,
    "ARM_AUDIT_RELATION_CHECK": arm_audit_relation_check,
    "ARM_AUDIT_NAIVE_PLUS_INTENT": arm_audit_naive_plus_intent,
}


def evaluate_arm_per_category(arm_label, queries, substrate):
    fn_arm = ARMS[arm_label]
    out = {}
    for cat in CATEGORY_LABELS:
        cat_queries = [q for q in queries if q["category"] == cat]
        n = len(cat_queries)
        n_refused = 0
        for q in cat_queries:
            r = fn_arm(q, substrate)
            if r["refused"]:
                n_refused += 1
        n_answered = n - n_refused
        refuse_rate = n_refused / max(n, 1)
        answer_rate = n_answered / max(n, 1)
        out[cat] = {
            "refuse_rate": round(refuse_rate, 4),
            "answer_rate": round(answer_rate, 4),
            "n_refused": n_refused, "n_answered": n_answered, "n_total": n,
        }
    return out


def _selftest():
    g = np.random.default_rng(0)
    x = bipolar(5, 64, g)
    assert x.shape == (5, 64)
    norms = np.linalg.norm(x, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3), "T1 bipolar norm"
    print("[selftest] T1 PASS: bipolar unit-norm")

    # T2: build substrate at small V_REL works
    global N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY
    orig = (N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY)
    N_DIM = 512
    V_CONCEPTS_PER_CAT = 6
    V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
    V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
    N_QUERIES_PER_CATEGORY = 8
    try:
        sub = build_substrate(np.random.default_rng(1), v_rel_in=8, v_rel_out=8)
        assert sub["W_subjects"].shape == (V_C_IN, N_DIM)
        assert sub["W_relations_in"].shape == (8, N_DIM)
        print("[selftest] T2 PASS: build_substrate shapes correct at V_REL=8")

        # T3: build substrate at LARGE V_REL works (envelope extension test)
        sub_big = build_substrate(np.random.default_rng(2), v_rel_in=256, v_rel_out=256)
        assert sub_big["W_relations_in"].shape == (256, N_DIM)
        print("[selftest] T3 PASS: build_substrate scales to V_REL=256")

        # T4: query corpus has correct counts per category
        queries = build_query_corpus(np.random.default_rng(3), sub)
        for cat in CATEGORY_LABELS:
            cat_q = [q for q in queries if q["category"] == cat]
            assert len(cat_q) == N_QUERIES_PER_CATEGORY, (
                "T4 wrong query count for %s" % cat)
        print("[selftest] T4 PASS: query counts correct (%d per category)" %
              N_QUERIES_PER_CATEGORY)

        # T5: audit + intent primitives self-id at sigma=0
        clean_subj = sub["W_subjects"][3]
        idx, sim = audit_subject_presence(clean_subj, sub["W_subjects"])
        assert idx == 3 and sim > 0.99, "T5 subject audit self-id"
        clean_rel = sub["W_relations_in"][2]
        idx, sim = audit_relation_presence(clean_rel, sub["W_relations_in"])
        assert idx == 2 and sim > 0.99, "T5 relation audit self-id"
        print("[selftest] T5 PASS: audit primitives self-id at sigma=0")

        # T6: out-of-domain atoms don't leak
        out_subj = sub["out_subject_atoms"][0]
        _, s_sim = audit_subject_presence(out_subj, sub["W_subjects"])
        out_rel = sub["out_relation_atoms"][0]
        _, r_sim = audit_relation_presence(out_rel, sub["W_relations_in"])
        assert s_sim < 0.30 and r_sim < 0.30, "T6 leak (s=%.3f r=%.3f)" % (s_sim, r_sim)
        print("[selftest] T6 PASS: out-of-domain atoms do not leak")

        # T7: all 3 arms run + return refused boolean
        for label in ARMS:
            r = ARMS[label](queries[0], sub)
            assert "refused" in r and isinstance(r["refused"], bool)
        print("[selftest] T7 PASS: all 3 arms return refused booleans")

        # T8: at V_REL_in=8, NEAR_DOMAIN_MIXED relation does not fit in 8-relation library
        # (out-of-domain relations sampled from a separate distribution; max-cos against
        # in-library should be below sqrt(2/N) + slack)
        near_q = [q for q in queries if q["category"] == "NEAR_DOMAIN_MIXED"][:5]
        for q in near_q:
            _, r_sim = audit_relation_presence(q["relation_vec"], sub["W_relations_in"])
            # at noise=10%, signal cos ~0.80 BUT relation is NOT in lib; mean leak should
            # stay below RELATION_AUDIT_THR
            assert r_sim < RELATION_AUDIT_THR + 0.20, (
                "T8 relation leak at V_REL=8: r_sim=%.3f >= 0.60" % r_sim)
        print("[selftest] T8 PASS: NEAR relation does NOT cleanup to V_REL=8 substrate")

        # T9: bands locked
        assert HP_NEAR_REFUSE_MIN == 0.85
        assert HP_NEAR_REFUSE_MIN > HP_PARTIAL_NEAR_REFUSE_MIN
        print("[selftest] T9 PASS: bands locked")

        # T10: substrate-only gate
        assert _LLM_CALL_COUNTER[0] == 0
        print("[selftest] T10 PASS: LLM counter = 0")
    finally:
        N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY = orig

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed_v_rel(seed: int, v_rel: int) -> Dict[str, Any]:
    """Run one (seed, V_REL) unit: V_REL_in = V_REL_out = v_rel."""
    t = time.time()
    g = np.random.default_rng(seed * 100003 + v_rel * 31)

    substrate = build_substrate(g, v_rel_in=v_rel, v_rel_out=v_rel)
    queries = build_query_corpus(g, substrate)

    out: Dict[str, Any] = {
        "seed": seed, "v_rel": v_rel, "run_mode": RUN_MODE,
        "N": N_DIM, "V_C_IN": V_C_IN, "V_C_OUT": V_C_OUT,
        "V_RELATIONS_IN": v_rel, "V_RELATIONS_OUT": v_rel,
        "n_queries_per_category": N_QUERIES_PER_CATEGORY,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    for arm_label in ARMS.keys():
        t_arm = time.time()
        per_cat = evaluate_arm_per_category(arm_label, queries, substrate)
        out[arm_label.lower()] = {
            "per_category": per_cat,
            "elapsed_s_arm": round(time.time() - t_arm, 3),
        }
        line = " | ".join("%s: refuse=%.3f answer=%.3f" %
                          (cat, per_cat[cat]["refuse_rate"], per_cat[cat]["answer_rate"])
                          for cat in CATEGORY_LABELS)
        print("  [seed=%d V_REL=%d] %s %s t=%.2fs" %
              (seed, v_rel, arm_label, line, time.time() - t_arm), flush=True)

    out["elapsed_s_unit"] = round(time.time() - t, 2)
    return out


def _arm_cat_mean_at_v_rel(units, v_rel, arm_key, cat, metric):
    vals = []
    for u in units:
        if u.get("v_rel") != v_rel:
            continue
        try:
            v = u[arm_key]["per_category"][cat][metric]
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        except KeyError:
            continue
    return float(np.mean(vals)) if vals else float("nan"), vals


def _cv(vals):
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    return float(np.std(vals) / max(abs(m), 1e-9))


def compute_verdict(units: List[Dict[str, Any]]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no units")

    # Per-V_REL aggregation
    by_v_rel = {}
    for v_rel in V_REL_SWEEP:
        d = {}
        for arm in ARMS.keys():
            ak = arm.lower()
            for cat in CATEGORY_LABELS:
                m_refuse, _ = _arm_cat_mean_at_v_rel(units, v_rel, ak, cat, "refuse_rate")
                m_answer, _ = _arm_cat_mean_at_v_rel(units, v_rel, ak, cat, "answer_rate")
                _, raw = _arm_cat_mean_at_v_rel(units, v_rel, ak, cat, "refuse_rate")
                d["%s_%s_refuse" % (arm, cat)] = round(m_refuse, 4)
                d["%s_%s_answer" % (arm, cat)] = round(m_answer, 4)
                d["%s_%s_refuse_cv" % (arm, cat)] = round(_cv(raw), 4)
        by_v_rel[v_rel] = d

    # Pull RELATION_CHECK arm + NAIVE_PLUS_INTENT (the chain-grade-eligible arms)
    REL = "ARM_AUDIT_RELATION_CHECK"
    AIP = "ARM_AUDIT_NAIVE_PLUS_INTENT"

    summary_rows = []
    chain_grade_v_rels = []
    middle_band_v_rels = []
    sanity_fails = []
    sat_flags = []

    for v_rel in V_REL_SWEEP:
        d = by_v_rel[v_rel]
        # Sanity rails (per arm at this V_REL)
        for arm in ARMS.keys():
            in_ans = d["%s_PURE_IN_DOMAIN_answer" % arm]
            out_ref = d["%s_PURE_OUT_OF_DOMAIN_refuse" % arm]
            if in_ans < SANITY_PURE_IN_ANSWER_MIN:
                sanity_fails.append("V_REL=%d %s PURE_IN_answer=%.3f<%.2f" %
                                     (v_rel, arm, in_ans, SANITY_PURE_IN_ANSWER_MIN))
            if out_ref < SANITY_PURE_OUT_REFUSE_MIN:
                sanity_fails.append("V_REL=%d %s PURE_OUT_refuse=%.3f<%.2f" %
                                     (v_rel, arm, out_ref, SANITY_PURE_OUT_REFUSE_MIN))
        # Chain-grade gate (RELATION_CHECK arm)
        in_ans_rel = d["%s_PURE_IN_DOMAIN_answer" % REL]
        near_ref_rel = d["%s_NEAR_DOMAIN_MIXED_refuse" % REL]
        near_cv_rel = d["%s_NEAR_DOMAIN_MIXED_refuse_cv" % REL]
        near_ref_aip = d["%s_NEAR_DOMAIN_MIXED_refuse" % AIP]
        near_cv_aip = d["%s_NEAR_DOMAIN_MIXED_refuse_cv" % AIP]

        is_chain = (in_ans_rel >= SANITY_PURE_IN_ANSWER_MIN
                     and near_ref_rel >= HP_NEAR_REFUSE_MIN
                     and near_cv_rel <= HP_CV_MAX)
        is_partial = (in_ans_rel >= SANITY_PURE_IN_ANSWER_MIN
                       and near_ref_rel >= HP_PARTIAL_NEAR_REFUSE_MIN
                       and near_cv_rel <= HP_CV_MAX)

        if is_chain:
            chain_grade_v_rels.append(v_rel)
        elif is_partial:
            middle_band_v_rels.append(v_rel)

        # Q-discipline: relation_check saturation at this V_REL
        if near_ref_rel >= Q_SUSPECT_SATURATION:
            sat_flags.append(v_rel)

        summary_rows.append(
            "V_REL=%d REL[in_ans=%.3f near_ref=%.3f cv=%.3f] "
            "AIP[near_ref=%.3f cv=%.3f]" % (
                v_rel, in_ans_rel, near_ref_rel, near_cv_rel,
                near_ref_aip, near_cv_aip))

    summ = " | ".join(summary_rows)
    if sat_flags:
        summ += " | [Q-DISCIPLINE: RELATION_CHECK >= %.3f at V_REL=%s; suspect saturation]" % (
            Q_SUSPECT_SATURATION, sat_flags)

    # Rail breach -> fail first
    if sanity_fails:
        return ("HARD_FAIL_SANITY_RAIL",
                "HARD_FAIL_SANITY_RAIL: " + "; ".join(sanity_fails[:5]) +
                ("; +%d more" % (len(sanity_fails) - 5) if len(sanity_fails) > 5 else "") +
                " | " + summ)

    # Verdict ladder per pre-reg
    # HARD_PASS_V_REL_EXTENSION: chain-grade at V_REL=256
    if 256 in chain_grade_v_rels:
        return ("HARD_PASS",
                "HARD_PASS_V_REL_EXTENSION: RELATION_CHECK chain-grades at V_REL=256 "
                "(extension confirmed; envelope chain-grades at %s) | %s" % (
                    chain_grade_v_rels, summ))

    # CHAIN_GRADE_AT_CLIFF_X: passes at one of {64, 128} but not 256
    if any(v in chain_grade_v_rels for v in (64, 128)) and 256 not in chain_grade_v_rels:
        cliff_at = next(v for v in (256, 128, 64) if v not in chain_grade_v_rels and v > min(chain_grade_v_rels))
        return ("HARD_PASS",
                "CHAIN_GRADE_AT_CLIFF_X: RELATION_CHECK extends to V_REL=%d but cliffs at "
                "V_REL=%d (chain_grade_set=%s) | %s" % (
                    max(chain_grade_v_rels), cliff_at, chain_grade_v_rels, summ))

    # HARD_FAIL_V_REL_CLIFF_AT_64: chain-grades at <=32 only (envelope doesn't extend past v2's 8)
    if chain_grade_v_rels and max(chain_grade_v_rels) <= 32:
        return ("HARD_FAIL",
                "HARD_FAIL_V_REL_CLIFF_AT_LOW: RELATION_CHECK only chain-grades at V_REL<=32 "
                "(chain_grade_set=%s); envelope does NOT extend past v2's rail+small | %s" % (
                    chain_grade_v_rels, summ))

    # Chain-grade rail (V_REL=8) but not at 16/32/64 -> envelope didn't extend
    if chain_grade_v_rels == [8]:
        return ("HARD_FAIL",
                "HARD_FAIL_V_REL_CLIFF_AT_RAIL: RELATION_CHECK chain-grades ONLY at v2 rail "
                "V_REL=8; envelope does NOT extend | %s" % summ)

    # No chain-grade but partial coverage
    if middle_band_v_rels:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_V_REL_EXTENSION: RELATION_CHECK in [%.2f, %.2f) at "
                "V_REL=%s; full chain-grade not reached | %s" % (
                    HP_PARTIAL_NEAR_REFUSE_MIN, HP_NEAR_REFUSE_MIN,
                    middle_band_v_rels, summ))

    return ("HARD_FAIL",
            "HARD_FAIL_NO_V_REL_HOLDS: RELATION_CHECK fails NEAR refuse band at ALL V_REL "
            "in %s | %s" % (V_REL_SWEEP, summ))


_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        keys = ["seed%d_vrel%d" % (s, v) for s in SEEDS for v in V_REL_SWEEP]
        agg = aggregate_partials(od, seeds=keys, run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        units = [agg[k] for k in sorted(agg.keys())]
        if not units:
            return
        v, vmsg = compute_verdict(units)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_units": len(units),
            "config_version": CONFIG_VERSION, "per_unit": units,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "V_REL_SWEEP": V_REL_SWEEP, "seeds": SEEDS,
        }
        write_metrics(od, metrics, results=units)
        print("[atexit] wrote synth metrics.json (%d units)" % len(units), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_REL_SWEEP=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_REL_SWEEP, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    keys = ["seed%d_vrel%d" % (s, v) for s in SEEDS for v in V_REL_SWEEP]
    existing = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    done_keys = set(existing.keys())
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(keys)), flush=True)

    for s in SEEDS:
        for v in V_REL_SWEEP:
            key = "seed%d_vrel%d" % (s, v)
            if key in done_keys:
                continue
            rec = run_seed_v_rel(s, v)
            write_partial_key(out_dir, key, rec)

    agg = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    units = [agg[k] for k in keys if k in agg]
    if not units:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero"

    v, vmsg = compute_verdict(units)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_units": len(units),
        "config_version": CONFIG_VERSION, "per_unit": units,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "V_REL_SWEEP": V_REL_SWEEP, "seeds": SEEDS,
        "DESIGN_NOTE": (
            "V_REL envelope extension from v2's chain-grade rail V_REL=8. Sweep "
            "V_REL in {8,16,32,64,128,256,512} with all other config matched to v2. "
            "Tests how far the NEAR-DOMAIN-MIXED refuse-gate scales as the audit "
            "relation library grows. Pre-reg per "
            "preregs/2026-06-25_substrate_refuse_gate_v_rel_extension_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
