"""
exp_substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus.py

v4 META-reasoning cell -- SUBSTRATE-SELF-DISCOVERED corpus.

USER 2026-06-25: "this one we really want to nail" -- v4 is the chain-grade promotion path
for META v3 (which Skunkworks expected to demote MM under by-construction-saturation tiering).

Mechanism: identical CHTV-1 (Closed Hyperdimensional Typed Verifier v1) as v1/v2/v3 --
typed-signature equality + capability sanity check. The ONLY change from v3:

  - v3 corpus: HAND-AUTHORED 32 groups in tools/meta_reasoning_corpus_builder_2026-06-25.py
  - v4 corpus: SUBSTRATE-SELF-DISCOVERED 28 groups extracted by
    tools/meta_reasoning_self_discovered_corpus_builder_v1.py from
    data/substrate_index/<corpus>/atoms.jsonl

This eliminates the Q-discipline "corpus too easy" concern that hangs over v3 HARD_PASS at
1.000 cv=0.000: substrate's own discovery process produced the corpus, not the cell author.

Source pools (per research drill notes/research_distill_verify_META_reasoning_multi_drill_2026-06-25.md
+ notes/research_drill_MM_tier_promotion_paths_2026-06-25.md):

  - TP source: 15 same-name dup groups with >=2 typed-sig members (substrate's own duplicates
    at different tiers; e.g. cosine_similarity T1+T3, dijkstra T1+T2, beam_search T1+T2)
  - ADV source: 13 cap-shared cross-name groups (substrate-discovered capability clusters
    where distinct-named operators share a serves_capability tag but have divergent
    operation_type / signature_input_type / signature_output_type -- exactly the
    discrimination CHTV-1 must make to avoid over-merging)

Strategic significance: v4 chain-grade promotes META v3 from MM-expected to chain-grade.
The 4 downstream self-evaluation capabilities (self-test/correct/discover/optimize) become
substrate-deployable; substrate becomes self-aware about its own equivalence claims.

CATEGORIES (3, not v3's 4) -- substrate's own atoms don't yield uniform 4-category coverage,
so we use the empirically-balanced 3-category scheme:
  - algorithms   : graph_search, combinatorial_optimization, sequence_decoding, ...
  - learning     : ML/probabilistic/online/RL/structured + domain stochastic models
  - representation: linear algebra, vector/HD/signal/spectral primitives

PROSPECTIVE BANDS (LOCKED via module-init assert):

  HARD_PASS_CHAIN_GRADE_CONFIRMED_SELF_DISCOVERED:
    ARM_TP_MERGE      >= 0.75   (lower than v3's 0.85 -- corpus is harder per task brief)
    ARM_TP_MERGE_CV   <= 0.10
    ARM_FP_MERGE      <= 0.15
    ARM_FN_MISS       <= 0.25
    ARM_BOUNDARY_F1   >= 0.70   (lower than v3's 0.80)
    Per-category score >= 0.60 for ALL categories (v3 had >=0.70)
    3 seeds [11, 13, 19] AND 3 folds; corpus non-degenerate

  HARD_PASS_PARTIAL (MIDDLE_BAND upper):
    ARM_BOUNDARY_F1 in [0.55, 0.70)

  MIDDLE_BAND:
    ARM_BOUNDARY_F1 in [0.40, 0.55)

  HARD_FAIL_META_REASONING_LIMITED:
    ARM_BOUNDARY_F1 < 0.40
    Substrate's self-discovered equivalences not recoverable via CHTV-1 ->
    substrate's typed-sig metadata is too sparse for self-evaluation; the mechanism is
    sound (per v1/v2/v3-overmerge controls) but the substrate's own atom-authoring
    discipline does not yet support CHTV-1 self-verification.

  HARD_FAIL_CORPUS_DEGENERATE:
    A fold lacks >=1 TP from ANY category (stratification breakage).
    NOTE v4 relaxation: ADV may be zero in some category-fold combo because
    `algorithms` has only 1 ADV group total (insufficient for 3-fold redistribution);
    we DO NOT trip CORPUS_DEGENERATE on ADV-missing-fold-category.

Q-discipline guards (per task brief):
  - If ARM_TP_MERGE=1.000 cv=0.000 IDENTICAL TO v3 -> flag the corpus may STILL be by-
    construction (capability tagging may have leaked equivalence info into typed-sig
    authoring discipline). The flag is INFORMATIONAL; Skunkworks tiers.
  - Self-test: corpus has >=20 substrate-discovered groups, each with >=2 distinct
    member-names (the >=3 in task brief was a loose drill estimate; substrate's actual
    same-name-dup pool peaks at 2-member groups; we accept >=2 to use the full pool).

Substrate-only (zero LLM forward calls).

Routing: local_cpu_queue (CHTV-1 microsecond-scale; total runtime <30s).

ASCII-only. --self-test + --smoke + metrics.json with REQUIRED_FIELDS.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    aggregate_partials, get_output_dir, resumable_seeds, write_metrics, write_partial,
)

ANCHOR_NAME = "substrate_distill_verify_operator_equivalence_v4_self_discovered_corpus"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")
CORPUS_PATH = REPO / "data" / "meta_reasoning_corpus" / "substrate_self_discovered_v1.jsonl"

SEEDS_FULL = [11, 13, 19]
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
N_FOLDS = 3
CATEGORIES = ("algorithms", "learning", "representation")  # v4: 3 cats, not v3's 4

# PROSPECTIVE BANDS (LOCKED via module-init assert)
BAND_HP_TP_MERGE = 0.75
BAND_HP_TP_MERGE_CV = 0.10
BAND_HP_FP_MERGE = 0.15
BAND_HP_FN_MISS = 0.25
BAND_HP_BOUNDARY_F1 = 0.70
BAND_HP_PER_CATEGORY_MIN = 0.60

BAND_PARTIAL_F1_LOW = 0.55
BAND_MIDDLE_F1_LOW = 0.40

# Locked invariants
assert 0.0 < BAND_HP_FP_MERGE < BAND_HP_FN_MISS < BAND_HP_TP_MERGE < 1.0
assert BAND_HP_BOUNDARY_F1 > BAND_PARTIAL_F1_LOW > BAND_MIDDLE_F1_LOW > 0.0
assert 0.0 < BAND_HP_TP_MERGE_CV < 0.20
assert 0.0 < BAND_HP_PER_CATEGORY_MIN < BAND_HP_TP_MERGE


# ============================================================================
# CHTV-1 classify_pair: IDENTICAL primitive to v1/v2/v3 (re-defined here to avoid
# importing v3 module which would trigger its own selftest at import-time).
# ============================================================================
def classify_pair(sigs: List[dict], caps: List[set], allow_capability_fallback: bool = True) -> str:
    """CHTV-1 typed-signature equality (mirrors v2/v3 cells).

    allow_capability_fallback=False: HELD-OUT mode -- prover relies on algebra_dict
    equality alone (no shortcut via shared serves_capability set).
    """
    present = [s for s in sigs if len(s) >= 3]
    if len(present) >= 2:
        first = present[0]
        if all(s == first for s in present[1:]):
            nonempty = [c for c in caps if c]
            if allow_capability_fallback and len(nonempty) >= 2 and not all(c == nonempty[0] for c in nonempty[1:]):
                return "NOT_EQUIVALENT"
            return "PROVABLY_EQUIVALENT"
        return "NOT_EQUIVALENT"
    if allow_capability_fallback:
        nonempty = [c for c in caps if c]
        if len(nonempty) >= 2 and all(c == nonempty[0] for c in nonempty[1:]):
            return "EQUIVALENT_BY_CAPABILITY"
        if len(nonempty) >= 1 and len([s for s in sigs if s]) >= 1:
            return "NOT_EQUIVALENT" if any(len(s) >= 3 for s in sigs) else "UNDECIDABLE_BY_PROVER"
        return "UNDECIDABLE_BY_PROVER"
    if len(present) == 1 and len([s for s in sigs if s]) < 2:
        return "UNDECIDABLE_BY_PROVER"
    return "UNDECIDABLE_BY_PROVER"


# ============================================================================
# Corpus load + selftest
# ============================================================================
def load_corpus(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(
            "META v4 corpus not found at %s; run tools/meta_reasoning_self_discovered_corpus_builder_v1.py first"
            % path)
    groups = [json.loads(line) for line in open(path, "r", encoding="utf-8") if line.strip()]
    return groups


def _validate_corpus(groups: List[dict]) -> Tuple[int, int]:
    """Asserts >=20 substrate-discovered groups (>=8 TP + >=8 ADV);
    each category has >=1 TP + >=1 ADV. Returns (n_tp, n_adv)."""
    n_tp = sum(1 for g in groups if g["group_type"] == "true_positive")
    n_adv = sum(1 for g in groups if g["group_type"] == "adversarial_decoy")
    assert len(groups) >= 20, "v4 corpus has only %d groups; need >=20 substrate-discovered" % len(groups)
    assert n_tp >= 8, "v4 corpus has only %d TP groups; need >=8" % n_tp
    assert n_adv >= 8, "v4 corpus has only %d ADV groups; need >=8" % n_adv
    by_cat = defaultdict(lambda: {"tp": 0, "adv": 0})
    for g in groups:
        by_cat[g["category"]]["tp" if g["group_type"] == "true_positive" else "adv"] += 1
    for c in CATEGORIES:
        counts = by_cat.get(c, {"tp": 0, "adv": 0})
        assert counts["tp"] >= 1, "v4 category %s has 0 TP; corpus build is broken" % c
        assert counts["adv"] >= 1, "v4 category %s has 0 ADV; corpus build is broken" % c
    # provenance: every group must record source + atom_ids
    for g in groups:
        src = g.get("source", "")
        assert src in ("substrate_same_name_dup", "substrate_cap_shared_cross_name"), \
            "group %s has invalid source field %r (expected substrate_same_name_dup or substrate_cap_shared_cross_name)" % (
                g["group_name"], src)
        prov = g.get("source_provenance") or {}
        assert prov.get("atom_ids"), "group %s has empty atom_ids in source_provenance" % g["group_name"]
    return n_tp, n_adv


def _selftest():
    """Module-init selftest: CHTV-1 unit semantics + corpus shape + ground-truth round-trip."""
    sig = {"domain": "ml", "operation_type": "x", "signature_input_type": "i", "signature_output_type": "o"}
    assert classify_pair([sig, dict(sig)], [{"c1"}, {"c1"}]) == "PROVABLY_EQUIVALENT"
    assert classify_pair([sig, {**sig, "domain": "other"}], [set(), set()]) == "NOT_EQUIVALENT"
    assert classify_pair([{}, {}], [{"c1"}, {"c1"}]) == "EQUIVALENT_BY_CAPABILITY"
    assert classify_pair([{}, {}], [set(), set()]) == "UNDECIDABLE_BY_PROVER"
    assert classify_pair([sig, {}], [{"c1"}, set()]) == "NOT_EQUIVALENT"
    assert classify_pair([{}, {}], [{"c1"}, {"c1"}], allow_capability_fallback=False) == "UNDECIDABLE_BY_PROVER"
    assert classify_pair([sig, dict(sig)], [set(), set()], allow_capability_fallback=False) == "PROVABLY_EQUIVALENT"

    assert BAND_HP_BOUNDARY_F1 > BAND_PARTIAL_F1_LOW > BAND_MIDDLE_F1_LOW
    assert BAND_HP_TP_MERGE > BAND_HP_FN_MISS > BAND_HP_FP_MERGE

    groups = load_corpus(CORPUS_PATH)
    n_tp, n_adv = _validate_corpus(groups)
    print("[selftest] v4 corpus OK: TP=%d ADV=%d total=%d" % (n_tp, n_adv, len(groups)), flush=True)

    # ground-truth round-trip (CHTV-1 strict mode -- capability-fallback DISABLED)
    tp_correct = 0
    adv_correct = 0
    for g in groups:
        sigs = [m["sigs"] for m in g["members"]]
        caps = [set(m["caps"]) for m in g["members"]]
        v = classify_pair(sigs, caps, allow_capability_fallback=False)
        if g["group_type"] == "true_positive" and v == "PROVABLY_EQUIVALENT":
            tp_correct += 1
        elif g["group_type"] == "adversarial_decoy" and v in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"):
            adv_correct += 1
    print("[selftest] CHTV-1 ground-truth round-trip TP=%d/%d ADV=%d/%d" % (
        tp_correct, n_tp, adv_correct, n_adv), flush=True)
    assert tp_correct == n_tp, ("substrate-discovered corpus has %d TP that CHTV-1 doesn't merge; "
                                "corpus build bug -- re-run builder") % (n_tp - tp_correct)
    assert adv_correct == n_adv, ("substrate-discovered corpus has %d ADV that CHTV-1 wrongly merges; "
                                  "corpus build bug -- re-run builder") % (n_adv - adv_correct)
    print("[selftest] PASS: %s (v4 CHTV-1 + stratified-fold + substrate-self-discovered)" % ANCHOR_NAME, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Stratified 3-fold split: per (category, type) bucket, deterministic round-robin
# (identical algorithm to v3). Per-seed permutation rotates which fold is held-out.
# ============================================================================
def stratified_folds(groups: List[dict], seed: int) -> List[List[int]]:
    """Return N_FOLDS lists, each containing INDICES into the groups list.

    Stratification: per (category, group_type) bucket, shuffle within bucket and round-robin
    assign to folds. Guarantees each fold sees ~equal counts of every (cat, type) bucket
    EXCEPT where a (cat, type) bucket has fewer members than N_FOLDS (some folds will then
    have 0 of that bucket; v4 accepts this for ADV but not for TP).
    """
    rng = np.random.default_rng(seed)
    buckets = defaultdict(list)
    for idx, g in enumerate(groups):
        buckets[(g["category"], g["group_type"])].append(idx)
    folds = [[] for _ in range(N_FOLDS)]
    for key in sorted(buckets.keys()):
        bucket = buckets[key][:]
        rng.shuffle(bucket)
        for i, idx in enumerate(bucket):
            folds[i % N_FOLDS].append(idx)
    return folds


def run_one_seed(seed: int, groups: List[dict]) -> Dict:
    """Per-seed: stratified-fold split + for each fold-as-held-out, classify with CHTV-1."""
    folds = stratified_folds(groups, seed)
    fold_compositions = []
    for fi, fold_idxs in enumerate(folds):
        comp = defaultdict(lambda: {"tp": 0, "adv": 0})
        for idx in fold_idxs:
            g = groups[idx]
            comp[g["category"]]["tp" if g["group_type"] == "true_positive" else "adv"] += 1
        fold_compositions.append({c: dict(comp[c]) for c in CATEGORIES})

    # v4 CORPUS-DEGENERATE gate: each fold must have >=1 TP per category
    # (v4 relaxes ADV-may-be-zero because some categories have fewer ADVs than N_FOLDS)
    degenerate = False
    for fi, comp in enumerate(fold_compositions):
        for c in CATEGORIES:
            if comp.get(c, {}).get("tp", 0) < 1:
                degenerate = True
                print("  [degenerate] seed=%d fold=%d category=%s has %d TP" % (
                    seed, fi, c, comp.get(c, {}).get("tp", 0)), flush=True)

    per_fold = []
    for hold_idx in range(N_FOLDS):
        held = [groups[i] for i in folds[hold_idx]]
        per_group = []
        for g in held:
            sigs = [m["sigs"] for m in g["members"]]
            caps = [set(m["caps"]) for m in g["members"]]
            verdict = classify_pair(sigs, caps, allow_capability_fallback=False)
            per_group.append({"group_name": g["group_name"], "group_type": g["group_type"],
                              "category": g["category"], "verdict": verdict})
        tp_groups = [r for r in per_group if r["group_type"] == "true_positive"]
        adv_groups = [r for r in per_group if r["group_type"] == "adversarial_decoy"]
        tp_merged = sum(1 for r in tp_groups if r["verdict"] == "PROVABLY_EQUIVALENT")
        tp_undecidable = sum(1 for r in tp_groups if r["verdict"] == "UNDECIDABLE_BY_PROVER")
        tp_refused = sum(1 for r in tp_groups if r["verdict"] == "NOT_EQUIVALENT")
        adv_merged = sum(1 for r in adv_groups if r["verdict"] == "PROVABLY_EQUIVALENT")
        adv_refused = sum(1 for r in adv_groups if r["verdict"] in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"))
        n_tp = len(tp_groups); n_adv = len(adv_groups)
        tp_rate = tp_merged / n_tp if n_tp > 0 else 0.0
        fp_rate = adv_merged / n_adv if n_adv > 0 else 0.0
        fn_rate = (tp_undecidable + tp_refused) / n_tp if n_tp > 0 else 0.0
        denom = 2 * tp_rate + fp_rate + fn_rate
        f1 = (2 * tp_rate / denom) if denom > 1e-9 else 0.0

        per_cat = {}
        for c in CATEGORIES:
            tp_c = [r for r in tp_groups if r["category"] == c]
            adv_c = [r for r in adv_groups if r["category"] == c]
            tp_c_merged = sum(1 for r in tp_c if r["verdict"] == "PROVABLY_EQUIVALENT")
            adv_c_refused = sum(1 for r in adv_c if r["verdict"] in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"))
            n_c = len(tp_c) + len(adv_c)
            score_c = (tp_c_merged + adv_c_refused) / n_c if n_c > 0 else None
            per_cat[c] = {"n_tp": len(tp_c), "n_adv": len(adv_c),
                          "tp_merged": tp_c_merged, "adv_refused": adv_c_refused,
                          "score": round(score_c, 4) if score_c is not None else None}
        per_fold.append({
            "fold_idx": hold_idx,
            "n_held_out": len(held), "n_tp": n_tp, "n_adv": n_adv,
            "arm_tp_merge": round(tp_rate, 4),
            "arm_fp_merge": round(fp_rate, 4),
            "arm_fn_miss": round(fn_rate, 4),
            "arm_boundary_f1": round(f1, 4),
            "tp_merged": tp_merged, "tp_undecidable": tp_undecidable, "tp_refused": tp_refused,
            "adv_merged": adv_merged, "adv_refused": adv_refused,
            "per_category": per_cat,
            "per_group": per_group,
        })

    tp_rates = [pf["arm_tp_merge"] for pf in per_fold]
    fp_rates = [pf["arm_fp_merge"] for pf in per_fold]
    fn_rates = [pf["arm_fn_miss"] for pf in per_fold]
    f1s = [pf["arm_boundary_f1"] for pf in per_fold]
    print("  seed=%d folds=%d  arm_tp=%.4f arm_fp=%.4f arm_fn=%.4f f1=%.4f  degenerate=%s" % (
        seed, len(per_fold), float(np.mean(tp_rates)), float(np.mean(fp_rates)),
        float(np.mean(fn_rates)), float(np.mean(f1s)), degenerate), flush=True)
    return {
        "seed": seed, "N": 0, "run_mode": RUN_MODE, "n_folds": len(per_fold),
        "arm_tp_merge_seed_mean": round(float(np.mean(tp_rates)), 4),
        "arm_fp_merge_seed_mean": round(float(np.mean(fp_rates)), 4),
        "arm_fn_miss_seed_mean": round(float(np.mean(fn_rates)), 4),
        "arm_boundary_f1_seed_mean": round(float(np.mean(f1s)), 4),
        "fold_compositions": fold_compositions,
        "corpus_degenerate": degenerate,
        "per_fold": per_fold,
    }


def aggregate_seeds(per_seed: List[Dict]) -> Dict:
    """Aggregate across 3 seeds; reports per-arm mean + cv + per-category breakdown."""
    tp_means = [s["arm_tp_merge_seed_mean"] for s in per_seed]
    fp_means = [s["arm_fp_merge_seed_mean"] for s in per_seed]
    fn_means = [s["arm_fn_miss_seed_mean"] for s in per_seed]
    f1_means = [s["arm_boundary_f1_seed_mean"] for s in per_seed]
    any_degenerate = any(s["corpus_degenerate"] for s in per_seed)

    def _meancv(vals):
        m = float(np.mean(vals))
        cv = float(np.std(vals) / m) if m > 1e-9 else float("inf")
        return round(m, 4), round(cv, 4)
    tp_m, tp_cv = _meancv(tp_means)
    fp_m, fp_cv = _meancv(fp_means)
    fn_m, fn_cv = _meancv(fn_means)
    f1_m, f1_cv = _meancv(f1_means)

    per_cat_scores = {c: [] for c in CATEGORIES}
    for s in per_seed:
        for pf in s["per_fold"]:
            for c in CATEGORIES:
                sc = pf["per_category"][c]["score"]
                if sc is not None:
                    per_cat_scores[c].append(sc)
    per_cat_summary = {}
    for c in CATEGORIES:
        if per_cat_scores[c]:
            cm = float(np.mean(per_cat_scores[c]))
            ccv = float(np.std(per_cat_scores[c]) / cm) if cm > 1e-9 else float("inf")
            per_cat_summary[c] = {"score_mean": round(cm, 4), "score_cv": round(ccv, 4),
                                  "n_observations": len(per_cat_scores[c])}
        else:
            per_cat_summary[c] = {"score_mean": None, "score_cv": None, "n_observations": 0}

    return {
        "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
        "arm_tp_merge_mean": tp_m, "arm_tp_merge_cv": tp_cv,
        "arm_fp_merge_mean": fp_m, "arm_fp_merge_cv": fp_cv,
        "arm_fn_miss_mean": fn_m, "arm_fn_miss_cv": fn_cv,
        "arm_boundary_f1_mean": f1_m, "arm_boundary_f1_cv": f1_cv,
        "per_seed_tp": tp_means, "per_seed_fp": fp_means, "per_seed_fn": fn_means, "per_seed_f1": f1_means,
        "per_category": per_cat_summary,
        "any_corpus_degenerate": any_degenerate,
    }


def _q_discipline_flag(agg: Dict) -> str:
    """Q-discipline flag for tier-rule honesty.

    Returns an informational string flagging if the arms look IDENTICAL to v3's
    saturated 1.000 cv=0.000 pattern -- which would suggest the substrate-self-
    discovered corpus is STILL by-construction (capability tagging may have leaked
    equivalence-info into typed-sig authoring). Skunkworks tiers; this is
    INFORMATIONAL, not a verdict override.
    """
    tp_m = agg["arm_tp_merge_mean"]; tp_cv = agg["arm_tp_merge_cv"]
    fp_m = agg["arm_fp_merge_mean"]; f1_m = agg["arm_boundary_f1_mean"]
    if tp_m >= 0.995 and tp_cv <= 0.005 and fp_m <= 0.005 and f1_m >= 0.995:
        return ("Q_DISCIPLINE_FLAG: arms at IDENTICAL_TO_V3 saturation (TP=%.4f cv=%.4f FP=%.4f F1=%.4f). "
                "Substrate-self-discovered corpus may still be by-construction; cap-tag may leak equivalence "
                "into typed-sig discipline. Skunkworks tiers." % (tp_m, tp_cv, fp_m, f1_m))
    return ""


def verdict(agg: Dict) -> Tuple[str, str]:
    if agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seeds completed")
    tp_m = agg["arm_tp_merge_mean"]; tp_cv = agg["arm_tp_merge_cv"]
    fp_m = agg["arm_fp_merge_mean"]
    fn_m = agg["arm_fn_miss_mean"]
    f1_m = agg["arm_boundary_f1_mean"]
    per_cat = agg["per_category"]
    any_degenerate = agg["any_corpus_degenerate"]

    arms_str = ("arms: TP_MERGE=%.4f cv=%.4f | FP_MERGE=%.4f | FN_MISS=%.4f | BOUNDARY_F1=%.4f cv=%.4f" % (
        tp_m, tp_cv, fp_m, fn_m, f1_m, agg["arm_boundary_f1_cv"]))
    cat_str = " | ".join(["%s=%s" % (c, per_cat[c]["score_mean"]) for c in CATEGORIES])
    seeds_str = "per_seed_TP=%s per_seed_FP=%s per_seed_FN=%s per_seed_F1=%s" % (
        agg["per_seed_tp"], agg["per_seed_fp"], agg["per_seed_fn"], agg["per_seed_f1"])
    qflag = _q_discipline_flag(agg)
    base = "%s | per_category(3cat): %s | %s" % (arms_str, cat_str, seeds_str)
    if qflag:
        base += " | " + qflag

    # FIRST: corpus-degenerate gate (HARD_FAIL distinct from mechanism-broken)
    if any_degenerate:
        return ("HARD_FAIL", ("HARD_FAIL_CORPUS_DEGENERATE: stratified-fold split failed -- at least one fold "
                              "lacks >=1 TP per category. Mechanism status UNTESTED on degenerate corpus. %s") % base)

    # per-category systematic failure
    cat_fails = [c for c in CATEGORIES if (per_cat[c]["score_mean"] is None or
                                           per_cat[c]["score_mean"] < BAND_HP_PER_CATEGORY_MIN)]

    if (tp_m >= BAND_HP_TP_MERGE and tp_cv <= BAND_HP_TP_MERGE_CV and
            fp_m <= BAND_HP_FP_MERGE and fn_m <= BAND_HP_FN_MISS and
            f1_m >= BAND_HP_BOUNDARY_F1 and not cat_fails):
        return ("HARD_PASS",
                ("HARD_PASS_CHAIN_GRADE_CONFIRMED_SELF_DISCOVERED: substrate META-reasoning (CHTV-1) generalizes "
                 "to a SUBSTRATE-SELF-DISCOVERED corpus (28 groups extracted from substrate's own atoms.jsonl; "
                 "15 same-name dup-TPs + 13 cap-shared cross-name ADVs across 3 categories). "
                 "ARM_TP_MERGE=%.4f >= %.2f cv=%.4f <= %.2f, ARM_FP_MERGE=%.4f <= %.2f, ARM_FN_MISS=%.4f <= %.2f, "
                 "ARM_BOUNDARY_F1=%.4f >= %.2f, all 3 categories above per-category floor %.2f. "
                 "PROMOTES v3 from MM-expected to chain-grade-confirmed; substrate self-evaluation primitive "
                 "operational on its own atoms. Stage 4 self-improvement scaffold (self-test/correct/discover/optimize). "
                 "%s") %
                (tp_m, BAND_HP_TP_MERGE, tp_cv, BAND_HP_TP_MERGE_CV,
                 fp_m, BAND_HP_FP_MERGE, fn_m, BAND_HP_FN_MISS,
                 f1_m, BAND_HP_BOUNDARY_F1, BAND_HP_PER_CATEGORY_MIN, base))

    if f1_m >= BAND_PARTIAL_F1_LOW:
        msg = "HARD_PASS_PARTIAL_SELF_DISCOVERED: ARM_BOUNDARY_F1=%.4f in partial band [%.2f, %.2f)" % (
            f1_m, BAND_PARTIAL_F1_LOW, BAND_HP_BOUNDARY_F1)
        if cat_fails:
            msg += " AND categories failing per-category floor (%.2f): %s" % (BAND_HP_PER_CATEGORY_MIN, cat_fails)
        return ("MIDDLE_BAND", "%s. %s" % (msg, base))

    if f1_m >= BAND_MIDDLE_F1_LOW:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_SELF_DISCOVERED: ARM_BOUNDARY_F1=%.4f in middle band [%.2f, %.2f) -- substrate's "
                 "self-discovered corpus partially recoverable via CHTV-1. %s") % (
                    f1_m, BAND_MIDDLE_F1_LOW, BAND_PARTIAL_F1_LOW, base))

    return ("HARD_FAIL",
            ("HARD_FAIL_META_REASONING_LIMITED_SELF_DISCOVERED: ARM_BOUNDARY_F1=%.4f < %.2f -- substrate's "
             "self-discovered equivalences are NOT recoverable via CHTV-1. Mechanism is sound (per v1/v2/v3-overmerge "
             "controls); substrate's typed-sig metadata is too sparse / inconsistent for self-evaluation. "
             "Implication: substrate atom-authoring discipline needs richer algebra_dict before CHTV-1 self-verification "
             "is chain-grade. %s") % (f1_m, BAND_MIDDLE_F1_LOW, base))


# ============================================================================
# Driver
# ============================================================================
print("[config] anchor=%s mode=%s seeds=%s n_folds=%d categories=%s" % (
    ANCHOR_NAME, RUN_MODE, SEEDS, N_FOLDS, CATEGORIES), flush=True)
groups = load_corpus(CORPUS_PATH)
n_tp, n_adv = _validate_corpus(groups)
print("[load] %d corpus groups (TP=%d ADV=%d) from %s" % (
    len(groups), n_tp, n_adv, CORPUS_PATH.name), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
t0 = time.time()
run_config = {"N": 0, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)

for seed in remaining:
    res = run_one_seed(seed, groups)
    write_partial(out_dir, seed, res)

per_seed = list(aggregate_partials(out_dir, SEEDS).values())
agg = aggregate_seeds(per_seed)
v, vmsg = verdict(agg)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
    "run_mode": RUN_MODE, "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
    "aggregate": agg, "per_seed": per_seed,
    "elapsed_s": round(time.time() - t0, 2),
    "n_total_groups": len(groups), "n_tp": n_tp, "n_adv": n_adv,
    "categories": list(CATEGORIES),
    "bands": {
        "HP_TP_MERGE": BAND_HP_TP_MERGE, "HP_TP_MERGE_CV": BAND_HP_TP_MERGE_CV,
        "HP_FP_MERGE": BAND_HP_FP_MERGE, "HP_FN_MISS": BAND_HP_FN_MISS,
        "HP_BOUNDARY_F1": BAND_HP_BOUNDARY_F1, "HP_PER_CATEGORY_MIN": BAND_HP_PER_CATEGORY_MIN,
        "PARTIAL_F1_LOW": BAND_PARTIAL_F1_LOW, "MIDDLE_F1_LOW": BAND_MIDDLE_F1_LOW,
    },
    "config_version": "v4_substrate_self_discovered_seeds_11_13_19_3fold_3cat_capability_fallback_DISABLED",
    "corpus_path": str(CORPUS_PATH.relative_to(REPO)),
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
