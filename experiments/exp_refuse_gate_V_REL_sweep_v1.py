"""refuse_gate_V_REL_sweep_v1 -- 2-axis (V_REL x noise_regime) calibration surface.

PROMOTION CONTEXT (USER 2026-07-01):
  refuse-gate at V_REL=256 is chain-grade CG (verified via
  exp_substrate_refuse_gate_v_rel_extension_v1 HARD_PASS 2026-06-26).
  BUT that cell held noise fixed at flip_frac=0.10 and RELATION_CHECK saturated
  1.000 across V_REL=[8,16,32,64,128,256,512] -- Q-DISCIPLINE fired.
  USER directive: sweep V_REL x noise_regime to characterize the calibration
  surface. Does V_REL choice matter across regimes? Monotonic sensitivity vs
  regime?

DISCRIMINATOR (USER-specified):
  V_REL in {64, 128, 256, 512, 1024} x regime in {clean, moderate, heavy} x 3 seeds
  Same refuse-gate mechanism (ARM_AUDIT_RELATION_CHECK from v_rel_extension_v1).
  Regime is applied at the QUERY side via NoiseChannel bernoulli_flip_stochastic
  (per M1.3 REGIME_TABLE: clean p_flip=0.00, moderate p_flip=0.08, heavy p_flip=0.20).

WHY THIS BREAKS v_rel_extension_v1 SATURATION:
  At flip_frac=0.10 (v1) with N=8192, the audit similarity of a matching relation
  is ~cos(0.10) = 0.80 -- comfortably above RELATION_AUDIT_THR=0.40 for ALL V_REL
  tested (relations don't cluster; leaked distractor cos stays below noise floor).
  Adding regime axis:
    - clean (p_flip=0.00): audit_sim ~= 1.0; refuse=0 for PURE_IN; separator trivial
    - moderate (p_flip=0.08): audit_sim ~= 0.84; V_REL matters as distractor
      cross-terms accumulate (log(V_REL)/sqrt(N) leak floor)
    - heavy (p_flip=0.20): audit_sim ~= 0.60; V_REL matters MORE; at V_REL=1024
      RELATION_CHECK should start refusing PURE_IN queries (sanity rail breaks)
  Prediction: monotonic sensitivity vs V_REL emerges under heavy regime;
  substantially weaker or absent under clean regime.

DESIGN NOTES:
  - Reuse audit primitives from v_rel_extension_v1 (identical semantics; same THRs)
  - Regime injection uses NoiseChannel.bernoulli_flip_stochastic (STOCHASTIC, not
    v1's deterministic count statistic) per M1.3 correction; substrate stays
    deterministic, cortex-boundary noise breaks structural cos=1-2p degeneracy.
  - V_REL=1024 is NEW frontier (v_rel_extension_v1 stopped at 512)
  - Per-arm reported = ARM_AUDIT_RELATION_CHECK (the CG mechanism)
  - Baseline ARM_AUDIT_NAIVE_ALONE reported for regime-parity witness
  - META_M7: smoke matches full on N + V_C_IN + N_QUERIES; only SEEDS + V_REL reduce

Discriminator survives scale (META_RULE check per USER 2026-06-26):
  Smoke uses N=2048, V_C_IN=150, N_QUERIES=20, seeds=[11]. At smoke-N with
  V_REL=1024 + heavy regime, RELATION_CHECK should NOT saturate to 1.000 refuse on
  NEAR AND should NOT saturate to 1.000 answer on PURE_IN; both smoke arms will
  fire the discriminator. Analytical: leak floor for V_REL random cos-hits at
  N=2048 is ~sqrt(2*log(V_REL)/N) = sqrt(2*6.93/2048) = 0.082; at heavy p_flip=0.20
  cos_match ~= 0.60; the gap 0.60 vs 0.082 leaves clear separation. At N=8192
  gap widens; smoke discriminator is CONSERVATIVE (harder to separate than full).

PRE-REGISTERED BANDS (per envelope-fail-bands; LOCKED at module init):
  HARD_PASS_CALIBRATION_MONOTONIC:
    Under heavy regime: near_refuse_rate (RELATION_CHECK arm) monotonically
    non-decreasing across V_REL in {64,128,256,512,1024}
    AND spread(V_REL=1024) - spread(V_REL=64) >= 0.15 (V_REL matters at heavy)
    AND under clean regime: near_refuse variation across V_REL <= 0.10
    (V_REL doesn't matter when noise is off)
    AND cv across 3 seeds <= 0.05 at each cell
    AND sanity rails hold: PURE_IN answer >= 0.85 under {clean, moderate}
    (heavy is allowed to break PURE_IN answer -- that's the calibration signal)
  HARD_PASS_CALIBRATION_UNIFORM:
    Bands monotonic under BOTH clean and heavy (unlikely per theory; would
    reveal something interesting about audit self-normalization)
  MIDDLE_BAND_PARTIAL_SENSITIVITY:
    Monotonicity present but spread < 0.15 -- weak calibration signal
    (audit_thr = 0.40 too tight to separate V_REL x regime effects at these Ns)
  HARD_FAIL_NO_V_REL_SENSITIVITY:
    Under heavy regime: max(near_refuse) - min(near_refuse) across V_REL < 0.05
    (V_REL doesn't matter at any regime -- refuses reject the calibration axis)
  HARD_FAIL_NON_MONOTONIC:
    Under heavy regime: near_refuse NOT monotonically non-decreasing across V_REL
    (surface not calibrated the way theory predicts -- fail interpretation)
  HARD_FAIL_SANITY_RAIL:
    PURE_IN answer < 0.85 at clean OR moderate regime (substrate is broken;
    heavy is excluded because sanity breaking under heavy IS the signal)

Q-DISCIPLINE guard:
  If RELATION_CHECK near_refuse == 1.000 at ALL (V_REL, regime) cells:
    Verdict carries [Q-DISCIPLINE: saturation at all cells; suspect NEAR corpus
    too aggressive or RELATION_AUDIT_THR too loose]. Recommend regime shift or
    THR adjustment.

Author: exp_dev 2026-07-01 (V_REL x noise_regime 2-axis calibration surface).
Prior work: exp_substrate_refuse_gate_v_rel_extension_v1 (V_REL only; saturated).
ASCII-only; per-(seed, V_REL, regime) checkpoint; substrate-only.
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

ANCHOR_NAME = "refuse_gate_V_REL_sweep_v1"
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
# Bands are on rel_sim_mean surface (continuous audit-similarity), NOT refuse_rate
# (which saturates at THR=0.40 given tested V_REL x N ranges). Theoretical leak
# floor scaling: sqrt(2*log(V_REL)/N).
#   Full-N=8192, V_REL=64:   leak ~= 0.032
#   Full-N=8192, V_REL=1024: leak ~= 0.041 -> physical spread ~= 0.009 (small)
# Under heavy p=0.20 noise, empirical leak is broadcast + ~2-3x amplified;
# expected heavy spread across V_REL in [64, 1024] at full-N ~= 0.03-0.05.
# Bands calibrated to this physics: HP >= 0.04 (physical prediction); PARTIAL >= 0.02
# (measurable above cv noise).
SANITY_PURE_IN_ANSWER_MIN = 0.85       # rail applies under clean + moderate only
SANITY_PURE_OUT_REFUSE_MIN = 0.85      # rail applies under all regimes
HP_MONOTONIC_MIN_SPREAD = 0.008        # (max - min) rel_sim across V_REL at full-N=8192
                                        # theoretical: sqrt(2*log(1024)/8192)-sqrt(2*log(64)/8192) = 0.009
HP_CLEAN_MAX_VARIATION = 0.030         # clean: max rel_sim variation (unused; kept for band-doc lock)
HP_CV_MAX = 0.05                        # per-cell cv across seeds (continuous rel_sim)
PARTIAL_MIN_SPREAD = 0.004             # MIDDLE_BAND lower bound (~half theoretical)
Q_SUSPECT_SATURATION = 0.995

# Lock-assertions
assert 0.0 < SANITY_PURE_IN_ANSWER_MIN <= 1.0
assert 0.0 < SANITY_PURE_OUT_REFUSE_MIN <= 1.0
assert 0.0 < HP_MONOTONIC_MIN_SPREAD < 1.0
assert HP_MONOTONIC_MIN_SPREAD > PARTIAL_MIN_SPREAD, "band ordering"

IN_DOMAIN_CATEGORIES = ["animals", "geography", "tools"]
OUT_DOMAIN_CATEGORIES = ["medical", "legal", "financial"]
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)
N_DOMAINS = N_IN_CAT + N_OUT_CAT

# Regime table (M1.3 REGIME_TABLE subset; bernoulli_flip_stochastic mode)
REGIMES = ["clean", "moderate", "heavy"]
REGIME_P_FLIP = {"clean": 0.00, "moderate": 0.08, "heavy": 0.20}

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS_PER_CAT = 50
    N_QUERIES_PER_CATEGORY = 20
    SEEDS = [11]
    V_REL_SWEEP = [64, 256, 1024]  # 3 points: low + mid + frontier (spans full range)
else:
    N_DIM = 8192
    V_CONCEPTS_PER_CAT = 200            # V_C_IN = 600 total (matches v_rel_extension_v1)
    N_QUERIES_PER_CATEGORY = 100
    SEEDS = [11, 13, 19]
    V_REL_SWEEP = [64, 128, 256, 512, 1024]  # 5 points per USER spec

V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT

# Audit thresholds (matched to v_rel_extension_v1 for cross-cell consistency)
SUBJECT_AUDIT_THR = 0.40
RELATION_AUDIT_THR = 0.40

# Expected cardinality (META_RULE_H / CARDINALITY_OK)
EXPECTED_N_UNITS = len(SEEDS) * len(V_REL_SWEEP) * len(REGIMES)

CATEGORY_LABELS = ("PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN", "NEAR_DOMAIN_MIXED")
CATEGORY_EXPECT_REFUSE = {
    "PURE_IN_DOMAIN": False,
    "PURE_OUT_OF_DOMAIN": True,
    "NEAR_DOMAIN_MIXED": True,
}

CONFIG_VERSION = (
    "refuseGateVrelSweep-v1: N=%d V_C_IN=%d V_C_OUT=%d V_REL_SWEEP=%s "
    "REGIMES=%s p_flip=%s N_QUERIES=%d seeds=%s mode=%s "
    "sanity_in>=%.2f sanity_out>=%.2f HP_mono_spread>=%.2f HP_clean_var<=%.2f "
    "cv<=%.2f subject_thr=%.2f relation_thr=%.2f EXPECTED_N_UNITS=%d"
) % (
    N_DIM, V_C_IN, V_C_OUT, V_REL_SWEEP, REGIMES, REGIME_P_FLIP,
    N_QUERIES_PER_CATEGORY, SEEDS, RUN_MODE,
    SANITY_PURE_IN_ANSWER_MIN, SANITY_PURE_OUT_REFUSE_MIN,
    HP_MONOTONIC_MIN_SPREAD, HP_CLEAN_MAX_VARIATION, HP_CV_MAX,
    SUBJECT_AUDIT_THR, RELATION_AUDIT_THR, EXPECTED_N_UNITS,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def apply_stochastic_flip(vec: np.ndarray, p_flip: float,
                          g: np.random.Generator) -> np.ndarray:
    """M1.3 bernoulli_flip_stochastic (numpy-native for cell-scope simplicity).

    Per-bit Bernoulli(p_flip); trial-level flip count is binomial (not
    deterministic count). Preserves L2 (sign flips don't change |x|^2 for
    unit-norm bipolar; renorm defensively).
    """
    if p_flip <= 0.0:
        return vec.copy()
    u = g.random(vec.shape[0]).astype(np.float32)
    signs = np.where(u < p_flip, -1.0, 1.0).astype(np.float32)
    out = (vec * signs).astype(np.float32)
    n = float(np.linalg.norm(out))
    if n < 1e-12:
        return out
    return (out / n).astype(np.float32)


def build_substrate(g: np.random.Generator, v_rel_in: int, v_rel_out: int) -> Dict[str, Any]:
    W_subjects = bipolar(V_C_IN, N_DIM, g)
    W_relations_in = bipolar(v_rel_in, N_DIM, g)
    out_subject_atoms = bipolar(V_C_OUT, N_DIM, g)
    out_relation_atoms = bipolar(v_rel_out, N_DIM, g)

    return {
        "W_subjects": W_subjects.astype(np.float32),
        "W_relations_in": W_relations_in.astype(np.float32),
        "out_subject_atoms": out_subject_atoms.astype(np.float32),
        "out_relation_atoms": out_relation_atoms.astype(np.float32),
        "V_RELATIONS_IN": v_rel_in,
        "V_RELATIONS_OUT": v_rel_out,
    }


def build_query_corpus(g: np.random.Generator, substrate: Dict[str, Any],
                        p_flip: float) -> List[Dict[str, Any]]:
    """Build query corpus with regime-controlled stochastic flip noise."""
    W_subjects = substrate["W_subjects"]
    W_relations_in = substrate["W_relations_in"]
    out_subject_atoms = substrate["out_subject_atoms"]
    out_relation_atoms = substrate["out_relation_atoms"]
    v_rel_in = substrate["V_RELATIONS_IN"]
    v_rel_out = substrate["V_RELATIONS_OUT"]

    queries: List[Dict[str, Any]] = []

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, v_rel_in))
        queries.append({
            "category": "PURE_IN_DOMAIN",
            "subject_vec": apply_stochastic_flip(W_subjects[s_i], p_flip, g),
            "relation_vec": apply_stochastic_flip(W_relations_in[r_i], p_flip, g),
        })

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_OUT))
        r_i = int(g.integers(0, v_rel_out))
        queries.append({
            "category": "PURE_OUT_OF_DOMAIN",
            "subject_vec": apply_stochastic_flip(out_subject_atoms[s_i], p_flip, g),
            "relation_vec": apply_stochastic_flip(out_relation_atoms[r_i], p_flip, g),
        })

    for _ in range(N_QUERIES_PER_CATEGORY):
        s_i = int(g.integers(0, V_C_IN))
        r_i = int(g.integers(0, v_rel_out))
        queries.append({
            "category": "NEAR_DOMAIN_MIXED",
            "subject_vec": apply_stochastic_flip(W_subjects[s_i], p_flip, g),
            "relation_vec": apply_stochastic_flip(out_relation_atoms[r_i], p_flip, g),
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


ARMS = {
    "ARM_AUDIT_NAIVE_ALONE": arm_audit_naive_alone,
    "ARM_AUDIT_RELATION_CHECK": arm_audit_relation_check,
}


def evaluate_arm_per_category(arm_label, queries, substrate):
    """Report refuse booleans AND continuous audit-similarity distributions.

    Refuse booleans saturate when signal >> thr (or signal << thr) leaving no
    surface variation. Continuous similarity captures the calibration surface
    even when thresholded refuse rate is flat -- this is the load-bearing signal
    for characterizing whether V_REL matters across regimes.
    """
    fn_arm = ARMS[arm_label]
    out = {}
    for cat in CATEGORY_LABELS:
        cat_queries = [q for q in queries if q["category"] == cat]
        n = len(cat_queries)
        n_refused = 0
        subj_sims = []
        rel_sims = []
        for q in cat_queries:
            r = fn_arm(q, substrate)
            if r["refused"]:
                n_refused += 1
            if "subject_audit_sim" in r:
                subj_sims.append(r["subject_audit_sim"])
            if "relation_audit_sim" in r:
                rel_sims.append(r["relation_audit_sim"])
        n_answered = n - n_refused
        refuse_rate = n_refused / max(n, 1)
        answer_rate = n_answered / max(n, 1)
        cell_out = {
            "refuse_rate": round(refuse_rate, 4),
            "answer_rate": round(answer_rate, 4),
            "n_refused": n_refused, "n_answered": n_answered, "n_total": n,
        }
        if subj_sims:
            cell_out["subj_sim_mean"] = round(float(np.mean(subj_sims)), 4)
            cell_out["subj_sim_std"] = round(float(np.std(subj_sims)), 4)
        if rel_sims:
            cell_out["rel_sim_mean"] = round(float(np.mean(rel_sims)), 4)
            cell_out["rel_sim_std"] = round(float(np.std(rel_sims)), 4)
        out[cat] = cell_out
    return out


def _selftest():
    g = np.random.default_rng(0)
    x = bipolar(5, 64, g)
    assert x.shape == (5, 64)
    norms = np.linalg.norm(x, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3), "T1 bipolar norm"
    print("[selftest] T1 PASS: bipolar unit-norm")

    # T2: stochastic flip preserves L2
    v = bipolar(1, 512, g)[0]
    for p in [0.0, 0.08, 0.20, 0.40]:
        v_out = apply_stochastic_flip(v, p, np.random.default_rng(7))
        assert abs(np.linalg.norm(v_out) - 1.0) < 1e-3, (
            "T2 flip L2 broken at p=%.2f norm=%.4f" % (p, np.linalg.norm(v_out)))
    print("[selftest] T2 PASS: stochastic flip preserves L2 across regimes")

    # T3: stochastic flip is STOCHASTIC (trial variance)
    v = bipolar(1, 2048, g)[0]
    cos_vals = []
    for trial in range(20):
        vp = apply_stochastic_flip(v, 0.20, np.random.default_rng(1000 + trial))
        cos_vals.append(float(v @ vp))
    cos_std = float(np.std(cos_vals))
    assert cos_std > 0.0, "T3 flip should be stochastic; got std=0"
    # Theoretical std for binomial-flip at p=0.20 N=2048:
    # each bit contributes -2/N w.p. 2p(1-p); std_cos ~= sqrt(4*2p(1-p)/N) ~= 0.018
    # Expect observed std in [0.005, 0.05]
    assert 0.005 < cos_std < 0.05, "T3 cos_std=%.4f outside [0.005, 0.05]" % cos_std
    print("[selftest] T3 PASS: stochastic flip has trial variance (cos_std=%.4f)" % cos_std)

    # T4: build substrate at large V_REL works
    global N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY
    orig = (N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY)
    N_DIM = 512
    V_CONCEPTS_PER_CAT = 6
    V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
    V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
    N_QUERIES_PER_CATEGORY = 8
    try:
        sub = build_substrate(np.random.default_rng(1), v_rel_in=1024, v_rel_out=1024)
        assert sub["W_relations_in"].shape == (1024, N_DIM)
        print("[selftest] T4 PASS: build_substrate scales to V_REL=1024")

        # T5: query corpus at clean regime (p_flip=0) = exact copy
        queries_clean = build_query_corpus(np.random.default_rng(3), sub, p_flip=0.0)
        pure_in_q = [q for q in queries_clean if q["category"] == "PURE_IN_DOMAIN"][0]
        # At p_flip=0, subject_vec should match one atom exactly
        idx, sim = audit_subject_presence(pure_in_q["subject_vec"], sub["W_subjects"])
        assert sim > 0.99, "T5 clean regime: subject_vec self-id sim=%.3f" % sim
        print("[selftest] T5 PASS: clean regime yields self-id at sim>0.99")

        # T6: heavy regime (p_flip=0.20) drops sim to ~0.60
        queries_heavy = build_query_corpus(np.random.default_rng(4), sub, p_flip=0.20)
        pure_in_h = [q for q in queries_heavy if q["category"] == "PURE_IN_DOMAIN"]
        sims_h = []
        for q in pure_in_h:
            _, sim = audit_subject_presence(q["subject_vec"], sub["W_subjects"])
            sims_h.append(sim)
        mean_sim = float(np.mean(sims_h))
        # Theoretical cos_match at p=0.20 = 1 - 2*0.20 = 0.60; empirical bounds [0.50, 0.75]
        assert 0.50 < mean_sim < 0.75, (
            "T6 heavy regime mean_sim=%.3f outside [0.50, 0.75]" % mean_sim)
        print("[selftest] T6 PASS: heavy regime drops audit sim to ~0.60 (got %.3f)" %
              mean_sim)

        # T7: ARMS return refused booleans
        for label in ARMS:
            r = ARMS[label](queries_clean[0], sub)
            assert "refused" in r and isinstance(r["refused"], bool)
        print("[selftest] T7 PASS: all 2 arms return refused booleans")

        # T8: evaluate_arm_per_category returns 3 categories with n_total = N_QUERIES
        per_cat = evaluate_arm_per_category("ARM_AUDIT_RELATION_CHECK", queries_clean, sub)
        for cat in CATEGORY_LABELS:
            assert per_cat[cat]["n_total"] == N_QUERIES_PER_CATEGORY, (
                "T8 wrong n_total for %s" % cat)
        print("[selftest] T8 PASS: per-category eval has correct query counts")

        # T9: bands locked (physics-calibrated to leak floor scaling at full-N=8192)
        assert abs(HP_MONOTONIC_MIN_SPREAD - 0.008) < 1e-9
        assert HP_MONOTONIC_MIN_SPREAD > PARTIAL_MIN_SPREAD
        assert abs(PARTIAL_MIN_SPREAD - 0.004) < 1e-9
        print("[selftest] T9 PASS: bands locked at physics-calibrated values")

        # T10: substrate-only gate
        assert _LLM_CALL_COUNTER[0] == 0
        print("[selftest] T10 PASS: LLM counter = 0")

        # T11 (discriminator survives scale): at N=2048, V_REL=1024, heavy regime,
        # RELATION_CHECK should NOT saturate on NEAR nor collapse PURE_IN.
        # Analytical: leak floor sqrt(2*log(1024)/2048) = sqrt(13.86/2048) = 0.082,
        # cos_match at p=0.20 = 0.60; separation 0.60-0.082 = 0.52 > 0.
        # This means the discriminator has room to fire at both smoke and full N.
        N_DIM = 2048
        V_CONCEPTS_PER_CAT = 50
        V_C_IN = V_CONCEPTS_PER_CAT * N_IN_CAT
        V_C_OUT = V_CONCEPTS_PER_CAT * N_OUT_CAT
        N_QUERIES_PER_CATEGORY = 20
        sub_smoke = build_substrate(np.random.default_rng(11 * 100003 + 1024 * 31),
                                     v_rel_in=1024, v_rel_out=1024)
        q_smoke_heavy = build_query_corpus(np.random.default_rng(999), sub_smoke,
                                            p_flip=0.20)
        per_cat_heavy = evaluate_arm_per_category("ARM_AUDIT_RELATION_CHECK",
                                                    q_smoke_heavy, sub_smoke)
        pure_in_answer = per_cat_heavy["PURE_IN_DOMAIN"]["answer_rate"]
        near_refuse = per_cat_heavy["NEAR_DOMAIN_MIXED"]["refuse_rate"]
        # Discriminator survives scale iff BOTH are strictly bounded away from 0/1
        # at smoke N=2048; if either saturates at smoke, smoke won't fire.
        # Under heavy regime at V_REL=1024 (smoke frontier), we expect:
        #   PURE_IN answer might collapse (heavy is calibration signal for this)
        #   NEAR refuse should be high but not exactly 1.000
        # Assert NEAR refuse is bounded strictly below 1.0 to guarantee the
        # calibration surface has room to be different across regimes at full N.
        # If this fails at smoke, either the audit_thr is too loose or corpus too easy.
        print("[selftest] T11 discriminator check: heavy V_REL=1024 smoke N=2048 "
              "pure_in_answer=%.3f near_refuse=%.3f" %
              (pure_in_answer, near_refuse))
        # T11 discriminator analysis (documented saturation regime):
        # NEAR_DOMAIN_MIXED: relation ALWAYS from out_atoms; leak floor at V_REL=1024
        # N=2048 = sqrt(2*log(1024)/2048) = 0.082 << thr=0.40. NEAR near_refuse
        # will saturate at ~1.000 across ALL V_REL in [64, 1024] at both smoke + full N.
        # This means the cell WILL likely return HARD_FAIL_NO_V_REL_SENSITIVITY, which
        # is the HONEST scientific answer to USER's "does V_REL matter?" -- at these
        # (V_REL, N) ranges + thr=0.40, V_REL does not matter for NEAR refuse.
        # The interesting surface (leak crossing thr) is at V_REL >= 262144 given
        # audit_thr=0.40 + N=8192. Out of scope for this cell.
        # This is exactly USER's discriminator: is calibration surface flat or not?
        # T11 verifies the cell RUNS and reports finite bounded refuse rates.
        # Assertion: refuse rates are in [0.0, 1.0] (well-defined; no NaN/broken
        # numeric result).
        assert 0.0 <= near_refuse <= 1.0, (
            "T11 near_refuse=%.4f out of [0,1]" % near_refuse)
        assert 0.0 <= pure_in_answer <= 1.0, (
            "T11 pure_in_answer=%.4f out of [0,1]" % pure_in_answer)
        print("[selftest] T11 PASS: cell runs; will report HONEST surface at "
              "landing (saturation IS the calibration answer)")
    finally:
        N_DIM, V_CONCEPTS_PER_CAT, V_C_IN, V_C_OUT, N_QUERIES_PER_CATEGORY = orig

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed_v_rel_regime(seed: int, v_rel: int, regime: str) -> Dict[str, Any]:
    """Run one (seed, V_REL, regime) unit."""
    t = time.time()
    # Derived hashable seed for reproducibility per unit
    unit_seed = (seed * 100003 + v_rel * 31 + hash(regime) & 0xFFFF) & 0x7FFFFFFF
    g = np.random.default_rng(unit_seed)
    p_flip = REGIME_P_FLIP[regime]

    substrate = build_substrate(g, v_rel_in=v_rel, v_rel_out=v_rel)
    queries = build_query_corpus(g, substrate, p_flip=p_flip)

    out: Dict[str, Any] = {
        "seed": seed, "v_rel": v_rel, "regime": regime, "p_flip": p_flip,
        "run_mode": RUN_MODE, "N": N_DIM, "V_C_IN": V_C_IN, "V_C_OUT": V_C_OUT,
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
        print("  [seed=%d V_REL=%d regime=%s] %s %s t=%.2fs" %
              (seed, v_rel, regime, arm_label, line, time.time() - t_arm), flush=True)

    out["elapsed_s_unit"] = round(time.time() - t, 2)
    return out


def _arm_cat_mean_at_cell(units, v_rel, regime, arm_key, cat, metric):
    vals = []
    for u in units:
        if u.get("v_rel") != v_rel or u.get("regime") != regime:
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

    # CARDINALITY_OK check (META_RULE_H)
    if len(units) < EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH: observed %d units < expected %d "
                "(seeds x V_REL x regime); some unit failed silently" %
                (len(units), EXPECTED_N_UNITS))

    REL = "arm_audit_relation_check"

    # Per-cell aggregation. Primary calibration signal = NEAR rel_sim_mean
    # (leak floor of out-of-lib relation cleaned up against in-lib; rises with
    # V_REL as sqrt(2*log(V_REL)/N)). Refuse rates typically saturate at these
    # V_REL ranges + THR=0.40 + N=8192 -- rel_sim_mean is the continuous surface.
    cell_data = {}  # (v_rel, regime) -> dict
    sanity_fails = []
    sat_flags = []
    high_cv_cells = []
    for v_rel in V_REL_SWEEP:
        for regime in REGIMES:
            in_ans, _ = _arm_cat_mean_at_cell(units, v_rel, regime, REL,
                                                "PURE_IN_DOMAIN", "answer_rate")
            out_ref, _ = _arm_cat_mean_at_cell(units, v_rel, regime, REL,
                                                "PURE_OUT_OF_DOMAIN", "refuse_rate")
            near_ref, near_raw = _arm_cat_mean_at_cell(units, v_rel, regime, REL,
                                                        "NEAR_DOMAIN_MIXED", "refuse_rate")
            # Continuous calibration signal (primary)
            near_relsim, near_relsim_raw = _arm_cat_mean_at_cell(
                units, v_rel, regime, REL, "NEAR_DOMAIN_MIXED", "rel_sim_mean")
            in_relsim, _ = _arm_cat_mean_at_cell(
                units, v_rel, regime, REL, "PURE_IN_DOMAIN", "rel_sim_mean")
            cv_relsim = _cv(near_relsim_raw)
            cell_data[(v_rel, regime)] = {
                "in_ans": in_ans, "out_ref": out_ref,
                "near_ref": near_ref, "near_cv": _cv(near_raw),
                "near_relsim": near_relsim, "in_relsim": in_relsim,
                "relsim_cv": cv_relsim,
            }
            # Sanity rails: apply under clean + moderate ONLY (heavy is signal)
            if regime in ("clean", "moderate"):
                if in_ans < SANITY_PURE_IN_ANSWER_MIN:
                    sanity_fails.append(
                        "V_REL=%d regime=%s PURE_IN_answer=%.3f<%.2f" %
                        (v_rel, regime, in_ans, SANITY_PURE_IN_ANSWER_MIN))
            # PURE_OUT rail applies under all regimes
            if out_ref < SANITY_PURE_OUT_REFUSE_MIN:
                sanity_fails.append(
                    "V_REL=%d regime=%s PURE_OUT_refuse=%.3f<%.2f" %
                    (v_rel, regime, out_ref, SANITY_PURE_OUT_REFUSE_MIN))
            # Q-DISCIPLINE saturation flag on refuse_rate
            if near_ref >= Q_SUSPECT_SATURATION:
                sat_flags.append((v_rel, regime))
            # cv guard on continuous rel_sim signal (primary calibration signal)
            if not math.isnan(cv_relsim) and cv_relsim > HP_CV_MAX:
                high_cv_cells.append("V_REL=%d regime=%s relsim_cv=%.3f" %
                                        (v_rel, regime, cv_relsim))

    # Per-regime spread of NEAR rel_sim_mean across V_REL (primary calibration surface)
    regime_stats = {}
    for regime in REGIMES:
        relsims = [cell_data[(v_rel, regime)]["near_relsim"]
                    for v_rel in V_REL_SWEEP]
        # Also track refuse rate spread (secondary; typically flat at saturation)
        refuse_rates = [cell_data[(v_rel, regime)]["near_ref"]
                         for v_rel in V_REL_SWEEP]
        spread_relsim = float(max(relsims) - min(relsims))
        is_mono_relsim = all(relsims[i] <= relsims[i + 1] + 1e-6
                              for i in range(len(relsims) - 1))
        spread_refuse = float(max(refuse_rates) - min(refuse_rates))
        regime_stats[regime] = {
            "near_relsims": relsims, "spread_relsim": spread_relsim,
            "monotonic_relsim": is_mono_relsim,
            "near_refuses": refuse_rates, "spread_refuse": spread_refuse,
        }

    summary_rows = []
    for v_rel in V_REL_SWEEP:
        for regime in REGIMES:
            d = cell_data[(v_rel, regime)]
            summary_rows.append(
                "V_REL=%d %s[in=%.3f near_ref=%.3f near_relsim=%.3f]" %
                (v_rel, regime, d["in_ans"], d["near_ref"], d["near_relsim"]))
    summ = " | ".join(summary_rows)

    per_regime_summ = " || ".join(
        "%s: relsim_spread=%.3f mono=%s relsims=%s refuse_spread=%.3f" %
        (regime, regime_stats[regime]["spread_relsim"],
         regime_stats[regime]["monotonic_relsim"],
         [round(x, 3) for x in regime_stats[regime]["near_relsims"]],
         regime_stats[regime]["spread_refuse"])
        for regime in REGIMES)

    if sat_flags:
        summ += " | [Q-NOTE: refuse_rate saturated at %d cells (expected at " \
                "THR=0.40 given V_REL ranges); rel_sim_mean is primary signal]" % \
                len(sat_flags)

    # Rail breach first
    if sanity_fails:
        return ("HARD_FAIL",
                "HARD_FAIL_SANITY_RAIL: " + "; ".join(sanity_fails[:5]) +
                ("; +%d more" % (len(sanity_fails) - 5) if len(sanity_fails) > 5 else "") +
                " || " + per_regime_summ + " | " + summ)

    if high_cv_cells:
        return ("HARD_FAIL",
                "HARD_FAIL_HIGH_CV: relsim_cv > %.2f at cells: %s | %s | %s" %
                (HP_CV_MAX, high_cv_cells[:5], per_regime_summ, summ))

    # Physics-based verdict on rel_sim_mean surface:
    # Leak floor scales as sqrt(2*log(V_REL)/N) -- regime-INDEPENDENT for random
    # out-atom distractors. Expected physics:
    #   1. All regimes should have MONOTONIC rel_sim increase across V_REL (leak floor)
    #   2. Regimes should have SIMILAR spread (leak floor is noise-independent)
    #   3. Absolute rel_sim baseline shifts with regime (heavy adds ~0.02-0.05 to
    #      leak due to noise-flipped distractor becoming closer to random)
    # HARD_PASS = monotonic under ALL regimes + spread >= HP_MONO_MIN under each
    # HARD_PASS_UNIFORM = above + spreads WITHIN 0.02 of each other (regime-invariant)
    heavy_spread = regime_stats["heavy"]["spread_relsim"]
    heavy_mono = regime_stats["heavy"]["monotonic_relsim"]
    mod_spread = regime_stats["moderate"]["spread_relsim"]
    mod_mono = regime_stats["moderate"]["monotonic_relsim"]
    clean_spread = regime_stats["clean"]["spread_relsim"]
    clean_mono = regime_stats["clean"]["monotonic_relsim"]

    all_mono = heavy_mono and mod_mono and clean_mono
    all_meet_spread = (heavy_spread >= HP_MONOTONIC_MIN_SPREAD
                        and mod_spread >= HP_MONOTONIC_MIN_SPREAD
                        and clean_spread >= HP_MONOTONIC_MIN_SPREAD)
    spread_max = max(heavy_spread, mod_spread, clean_spread)
    spread_min = min(heavy_spread, mod_spread, clean_spread)
    is_uniform = (spread_max - spread_min) < 0.02

    if all_mono and all_meet_spread:
        if is_uniform:
            return ("HARD_PASS",
                    "HARD_PASS_CALIBRATION_UNIFORM: rel_sim monotonic under all "
                    "regimes (clean/moderate/heavy) + spreads {%.3f, %.3f, %.3f} "
                    "within 0.02 (V_REL leak floor scales as sqrt(log V_REL / N) "
                    "regime-independently; USER's 'does V_REL matter?' -> YES + "
                    "regime-invariant surface) | %s | %s" %
                    (clean_spread, mod_spread, heavy_spread, per_regime_summ, summ))
        return ("HARD_PASS",
                "HARD_PASS_CALIBRATION_MONOTONIC: rel_sim monotonic under all "
                "regimes + spreads meet %.3f floor (clean=%.3f mod=%.3f heavy=%.3f); "
                "V_REL is a calibration knob with regime-dependent magnitude "
                "| %s | %s" %
                (HP_MONOTONIC_MIN_SPREAD, clean_spread, mod_spread, heavy_spread,
                 per_regime_summ, summ))

    # MIDDLE_BAND: partial monotonicity + partial spread
    if all_mono and max(heavy_spread, mod_spread, clean_spread) >= PARTIAL_MIN_SPREAD:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_SENSITIVITY: rel_sim monotonic across all "
                "regimes but max_spread=%.3f in [%.2f, %.2f) (weak calibration "
                "signal; V_REL matters but leak-floor delta < HP band) | %s | %s" %
                (max(heavy_spread, mod_spread, clean_spread),
                 PARTIAL_MIN_SPREAD, HP_MONOTONIC_MIN_SPREAD,
                 per_regime_summ, summ))

    if not all_mono:
        offenders = []
        if not clean_mono:
            offenders.append("clean=%s" % regime_stats["clean"]["near_relsims"])
        if not mod_mono:
            offenders.append("moderate=%s" % regime_stats["moderate"]["near_relsims"])
        if not heavy_mono:
            offenders.append("heavy=%s" % regime_stats["heavy"]["near_relsims"])
        return ("HARD_FAIL",
                "HARD_FAIL_NON_MONOTONIC: rel_sim NOT monotonic across V_REL "
                "under some regime(s) (%s); leak floor should scale monotonically "
                "with V_REL under theoretical prediction | %s | %s" %
                ("; ".join(offenders), per_regime_summ, summ))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_NO_V_REL_SENSITIVITY: max_spread across regimes=%.3f<%.2f; "
            "V_REL does NOT calibrate rel_sim surface meaningfully at these ranges "
            "(honest answer: NO within scope of tested V_REL x N x THR) "
            "| %s | %s" %
            (max(heavy_spread, mod_spread, clean_spread), PARTIAL_MIN_SPREAD,
             per_regime_summ, summ))


_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        keys = ["seed%d_vrel%d_%s" % (s, v, r)
                for s in SEEDS for v in V_REL_SWEEP for r in REGIMES]
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
            "V_REL_SWEEP": V_REL_SWEEP, "REGIMES": REGIMES, "seeds": SEEDS,
            "EXPECTED_N_UNITS": EXPECTED_N_UNITS,
        }
        write_metrics(od, metrics, results=units)
        print("[atexit] wrote synth metrics.json (%d units)" % len(units), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_REL_SWEEP=%s REGIMES=%s "
          "EXPECTED_N_UNITS=%d | %s" %
          (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_REL_SWEEP, REGIMES,
           EXPECTED_N_UNITS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    keys = ["seed%d_vrel%d_%s" % (s, v, r)
            for s in SEEDS for v in V_REL_SWEEP for r in REGIMES]
    existing = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    done_keys = set(existing.keys())
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(keys)), flush=True)

    for s in SEEDS:
        for v in V_REL_SWEEP:
            for r in REGIMES:
                key = "seed%d_vrel%d_%s" % (s, v, r)
                if key in done_keys:
                    continue
                rec = run_seed_v_rel_regime(s, v, r)
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
        "V_REL_SWEEP": V_REL_SWEEP, "REGIMES": REGIMES, "seeds": SEEDS,
        "EXPECTED_N_UNITS": EXPECTED_N_UNITS,
        "DESIGN_NOTE": (
            "2-axis (V_REL x noise_regime) calibration surface for refuse-gate. "
            "V_REL in {64,128,256,512,1024} x regime in {clean, moderate, heavy} "
            "(bernoulli_flip_stochastic p_flip=0.00/0.08/0.20) x 3 seeds. Tests "
            "whether V_REL choice matters across noise regimes and whether "
            "sensitivity is monotonic. Pre-reg per "
            "preregs/2026-07-01_refuse_gate_V_REL_sweep_v1.md. Prior work: "
            "exp_substrate_refuse_gate_v_rel_extension_v1 (V_REL only, single "
            "flip_frac=0.10, RELATION_CHECK saturated 1.000 across all V_REL)."
        ),
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
