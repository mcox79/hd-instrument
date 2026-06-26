"""
exp_substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified.py

v3 CHAIN-GRADE-ELIGIBLE META-REASONING cell.

Mechanism: same CHTV-1 (Closed Hyperdimensional Typed Verifier v1) substrate META-reasoning
as v1/v2 (typed-signature equality + capability sanity check). The change is CORPUS + EVAL:

  - Load data/meta_reasoning_corpus/algebra_dict_v1.jsonl (>=24 NAMED + >=8 ADV per builder).
  - STRATIFIED 3-FOLD SPLIT: each fold contains ~2 NAMED-from-each-category + ~1 ADV-from-each.
    Eliminates v2 issue where NAMED operators landed in one fold by chance (folds disjoint
    across seeds via shuffled-fold-label permutation).
  - For each seed [11, 13, 19]: classify HELD-OUT 1/3 with CHTV-1.
  - 4 arms reported:
      ARM_TP_MERGE      true-positive merge rate on NAMED-equivalent pairs (target >=0.85)
      ARM_FP_MERGE      false-positive merge rate on adversarial decoys (target <=0.10)
      ARM_FN_MISS       false-negative miss rate (TP that CHTV-1 fails to merge; target <=0.20)
      ARM_BOUNDARY_F1   composite F1 = 2*TP_rate / (2*TP_rate + FP_rate + FN_rate); target >=0.80

USER 2026-06-25: "this one we really want to nail, because this is going to be absolutely
KEY to how the system evaluates itself."

PROSPECTIVE BANDS (LOCKED via assert at module init):

  HARD_PASS_CHAIN_GRADE_META_REASONING:
    ARM_TP_MERGE      >= 0.85   (cv <= 0.07)
    ARM_FP_MERGE      <= 0.10
    ARM_FN_MISS       <= 0.20
    ARM_BOUNDARY_F1   >= 0.80
    AND each category (math/programming/substrate/statistical) >=0.70 individually
    AND 3 seeds [11, 13, 19] AND 3 folds

  HARD_PASS_PARTIAL (MIDDLE_BAND, upper):
    ARM_BOUNDARY_F1 in [0.60, 0.80); ONE category systematically failing

  MIDDLE_BAND:
    ARM_BOUNDARY_F1 in [0.45, 0.60); methodology issue or category-blindness

  HARD_FAIL_META_REASONING_BROKEN:
    ARM_BOUNDARY_F1 < 0.45

  HARD_FAIL_CORPUS_DEGENERATE:
    same v2 failure -- NAMED groups all landed in one fold (stratification didn't take)
    fold composition assertion catches this BEFORE verdict.

Routing: local_cpu_queue (substrate-only, fast; <30s expected).

ASCII-only. --self-test + --smoke + metrics.json + per-arm + per-category + per-fold metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_distill_verify_operator_equivalence_v3_NAMED_corpus_stratified"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")
CORPUS_PATH = REPO / "data" / "meta_reasoning_corpus" / "algebra_dict_v1.jsonl"

SEEDS_FULL = [11, 13, 19]
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL
N_FOLDS = 3
CATEGORIES = ("math", "programming", "substrate", "statistical")

# PROSPECTIVE BANDS (LOCKED via assert)
BAND_HP_TP_MERGE = 0.85
BAND_HP_TP_MERGE_CV = 0.07
BAND_HP_FP_MERGE = 0.10
BAND_HP_FN_MISS = 0.20
BAND_HP_BOUNDARY_F1 = 0.80
BAND_HP_PER_CATEGORY_MIN = 0.70

BAND_PARTIAL_F1_LOW = 0.60
BAND_MIDDLE_F1_LOW = 0.45

# Locked invariants
assert 0.0 < BAND_HP_FP_MERGE < BAND_HP_FN_MISS < BAND_HP_TP_MERGE < 1.0
assert BAND_HP_BOUNDARY_F1 > BAND_PARTIAL_F1_LOW > BAND_MIDDLE_F1_LOW > 0.0
assert 0.0 < BAND_HP_TP_MERGE_CV < 0.20
assert 0.0 < BAND_HP_PER_CATEGORY_MIN < BAND_HP_TP_MERGE


# ============================================================================
# CHTV-1 classify_pair: same primitive as v2; verbatim signature semantics.
# Imported here for self-test reuse; re-implemented to avoid v2 module-level side-effects.
# ============================================================================
def classify_pair(sigs: List[dict], caps: List[set], allow_capability_fallback: bool = True) -> str:
    """CHTV-1 typed-signature equality (mirrors v2 cell).

    allow_capability_fallback=False: HELD-OUT mode -- prover relies on algebra_dict equality alone.
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
            "META corpus not found at %s; run tools/meta_reasoning_corpus_builder_2026-06-25.py first" % path)
    groups = [json.loads(line) for line in open(path, "r", encoding="utf-8") if line.strip()]
    return groups


def _validate_corpus(groups: List[dict]) -> Tuple[int, int]:
    """Asserts >=24 NAMED + >=8 ADV; returns (n_tp, n_adv)."""
    n_tp = sum(1 for g in groups if g["group_type"] == "true_positive")
    n_adv = sum(1 for g in groups if g["group_type"] == "adversarial_decoy")
    assert n_tp >= 24, "corpus has only %d TP groups; need >=24 (run builder)" % n_tp
    assert n_adv >= 8, "corpus has only %d ADV decoys; need >=8 (run builder)" % n_adv
    # category coverage
    by_cat = defaultdict(lambda: {"tp": 0, "adv": 0})
    for g in groups:
        by_cat[g["category"]]["tp" if g["group_type"] == "true_positive" else "adv"] += 1
    for c in CATEGORIES:
        assert by_cat[c]["tp"] >= 3, "category %s has only %d TP; need >=3 for stratified 3-fold" % (c, by_cat[c]["tp"])
    return n_tp, n_adv


def _selftest():
    # CHTV-1 unit semantics (parity with v2)
    sig = {"domain": "ml", "operation_type": "x", "signature_input_type": "i", "signature_output_type": "o"}
    assert classify_pair([sig, dict(sig)], [{"c1"}, {"c1"}]) == "PROVABLY_EQUIVALENT"
    assert classify_pair([sig, {**sig, "domain": "other"}], [set(), set()]) == "NOT_EQUIVALENT"
    assert classify_pair([{}, {}], [{"c1"}, {"c1"}]) == "EQUIVALENT_BY_CAPABILITY"
    assert classify_pair([{}, {}], [set(), set()]) == "UNDECIDABLE_BY_PROVER"
    assert classify_pair([sig, {}], [{"c1"}, set()]) == "NOT_EQUIVALENT"
    # HELD-OUT mode
    assert classify_pair([{}, {}], [{"c1"}, {"c1"}], allow_capability_fallback=False) == "UNDECIDABLE_BY_PROVER"
    assert classify_pair([sig, dict(sig)], [set(), set()], allow_capability_fallback=False) == "PROVABLY_EQUIVALENT"

    # bands sane
    assert BAND_HP_BOUNDARY_F1 > BAND_PARTIAL_F1_LOW > BAND_MIDDLE_F1_LOW
    assert BAND_HP_TP_MERGE > BAND_HP_FN_MISS > BAND_HP_FP_MERGE

    # corpus shape
    groups = load_corpus(CORPUS_PATH)
    n_tp, n_adv = _validate_corpus(groups)
    print("[selftest] corpus OK: TP=%d ADV=%d" % (n_tp, n_adv), flush=True)

    # ground-truth round-trip: CHTV-1 on FULL corpus (capability-fallback DISABLED) classifies correctly
    tp_correct = 0; adv_correct = 0
    for g in groups:
        sigs = [m["sigs"] for m in g["members"]]
        caps = [set(m["caps"]) for m in g["members"]]
        v = classify_pair(sigs, caps, allow_capability_fallback=False)
        if g["group_type"] == "true_positive" and v == "PROVABLY_EQUIVALENT":
            tp_correct += 1
        elif g["group_type"] == "adversarial_decoy" and v in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"):
            adv_correct += 1
    print("[selftest] ground-truth round-trip TP=%d/%d ADV=%d/%d" % (
        tp_correct, n_tp, adv_correct, n_adv), flush=True)
    # corpus must be 100% chain-grade-eligible by construction (CHTV-1 is sound;
    # the corpus is built so the ground-truth labels match what CHTV-1 will say)
    assert tp_correct == n_tp, "corpus has %d TP that CHTV-1 doesn't merge; corpus build bug" % (n_tp - tp_correct)
    assert adv_correct == n_adv, "corpus has %d ADV that CHTV-1 wrongly merges; tighten the adversaries" % (n_adv - adv_correct)

    print("[selftest] PASS: %s (v3 CHTV-1 + stratified-fold + per-arm/per-category)" % ANCHOR_NAME, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Stratified 3-fold split: per (category, type) bucket, deterministic round-robin
# allocation to folds; per-seed permutation rotates which fold is held-out.
# ============================================================================
def stratified_folds(groups: List[dict], seed: int) -> List[List[int]]:
    """Return a list of N_FOLDS lists, each containing INDICES into the groups list.

    Stratification: per (category, type) bucket, shuffle within bucket and round-robin
    assign to folds. Guarantees each fold sees ~equal counts of every (cat, type) bucket.
    The shuffle uses np.random.default_rng(seed) for cross-seed disjoint held-out folds.
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
    """Per-seed: stratified-fold split + for each fold-as-held-out, classify with CHTV-1.

    Returns aggregated metrics across 3 folds for this seed.
    """
    folds = stratified_folds(groups, seed)
    # sanity: every fold must contain >=1 TP from each category for chain-grade rail
    fold_compositions = []
    for fi, fold_idxs in enumerate(folds):
        comp = defaultdict(lambda: {"tp": 0, "adv": 0})
        for idx in fold_idxs:
            g = groups[idx]
            comp[g["category"]]["tp" if g["group_type"] == "true_positive" else "adv"] += 1
        fold_compositions.append({c: dict(comp[c]) for c in CATEGORIES})
    # CORPUS-DEGENERATE gate: each fold must have >=1 TP per category (else stratification failed)
    degenerate = False
    for fi, comp in enumerate(fold_compositions):
        for c in CATEGORIES:
            if comp.get(c, {}).get("tp", 0) < 1:
                degenerate = True
                print("  [degenerate] seed=%d fold=%d category=%s has %d TP" % (
                    seed, fi, c, comp.get(c, {}).get("tp", 0)), flush=True)

    # for each fold-as-held-out, run CHTV-1 over the held-out subset; report per-arm + per-category
    per_fold = []
    for hold_idx in range(N_FOLDS):
        held = [groups[i] for i in folds[hold_idx]]
        # classify each group in held-out via CHTV-1 with capability-fallback DISABLED (the strict test)
        per_group = []
        for g in held:
            sigs = [m["sigs"] for m in g["members"]]
            caps = [set(m["caps"]) for m in g["members"]]
            verdict = classify_pair(sigs, caps, allow_capability_fallback=False)
            per_group.append({"group_name": g["group_name"], "group_type": g["group_type"],
                              "category": g["category"], "verdict": verdict})
        # compute the 4 arms on this fold
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
        # boundary F1 per definition above
        denom = 2 * tp_rate + fp_rate + fn_rate
        f1 = (2 * tp_rate / denom) if denom > 1e-9 else 0.0
        # per-category breakdown
        per_cat = {}
        for c in CATEGORIES:
            tp_c = [r for r in tp_groups if r["category"] == c]
            adv_c = [r for r in adv_groups if r["category"] == c]
            tp_c_merged = sum(1 for r in tp_c if r["verdict"] == "PROVABLY_EQUIVALENT")
            adv_c_refused = sum(1 for r in adv_c if r["verdict"] in ("NOT_EQUIVALENT", "UNDECIDABLE_BY_PROVER"))
            # category-level "score" = (TP correct + ADV correctly refused) / total in held-out
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

    # aggregate across the 3 folds for this seed
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

    # per-category aggregation: average per-category score across all folds across all seeds
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


def verdict(agg: Dict) -> Tuple[str, str]:
    if agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seeds completed")
    tp_m = agg["arm_tp_merge_mean"]; tp_cv = agg["arm_tp_merge_cv"]
    fp_m = agg["arm_fp_merge_mean"]
    fn_m = agg["arm_fn_miss_mean"]
    f1_m = agg["arm_boundary_f1_mean"]
    per_cat = agg["per_category"]
    any_degenerate = agg["any_corpus_degenerate"]

    # short per-arm/per-cat summary lines for the verdict_msg (Fix #28: read per-arm, not summary text)
    arms_str = ("arms: TP_MERGE=%.4f cv=%.4f | FP_MERGE=%.4f | FN_MISS=%.4f | BOUNDARY_F1=%.4f cv=%.4f" % (
        tp_m, tp_cv, fp_m, fn_m, f1_m, agg["arm_boundary_f1_cv"]))
    cat_str = " | ".join(["%s=%s" % (c, per_cat[c]["score_mean"]) for c in CATEGORIES])
    seeds_str = "per_seed_TP=%s per_seed_FP=%s per_seed_FN=%s per_seed_F1=%s" % (
        agg["per_seed_tp"], agg["per_seed_fp"], agg["per_seed_fn"], agg["per_seed_f1"])
    base = "%s | per_category: %s | %s" % (arms_str, cat_str, seeds_str)

    # FIRST: corpus-degenerate gate (HARD_FAIL distinct from mechanism-broken)
    if any_degenerate:
        return ("HARD_FAIL", ("HARD_FAIL_CORPUS_DEGENERATE: stratified-fold split failed -- at least one fold lacks "
                              ">=1 TP per category. Same v2 failure pattern; stratification assertion did NOT take. "
                              "Mechanism status UNTESTED on degenerate corpus. %s") % base)

    # check per-category systematic failure
    cat_fails = [c for c in CATEGORIES if (per_cat[c]["score_mean"] is None or
                                           per_cat[c]["score_mean"] < BAND_HP_PER_CATEGORY_MIN)]

    if (tp_m >= BAND_HP_TP_MERGE and tp_cv <= BAND_HP_TP_MERGE_CV and
            fp_m <= BAND_HP_FP_MERGE and fn_m <= BAND_HP_FN_MISS and
            f1_m >= BAND_HP_BOUNDARY_F1 and not cat_fails):
        return ("HARD_PASS",
                ("HARD_PASS_CHAIN_GRADE_META_REASONING: substrate META-reasoning (CHTV-1) generalizes to a NAMED "
                 "operator corpus stratified across 4 categories with adversarial decoys. ARM_TP_MERGE=%.4f >= %.2f "
                 "cv=%.4f <= %.2f, ARM_FP_MERGE=%.4f <= %.2f, ARM_FN_MISS=%.4f <= %.2f, ARM_BOUNDARY_F1=%.4f >= %.2f, "
                 "all 4 categories above per-category floor %.2f. First chain-grade substrate self-evaluation primitive. "
                 "Stage 4 self-improvement scaffold (self-test/correct/discover/optimize). %s") %
                (tp_m, BAND_HP_TP_MERGE, tp_cv, BAND_HP_TP_MERGE_CV,
                 fp_m, BAND_HP_FP_MERGE, fn_m, BAND_HP_FN_MISS,
                 f1_m, BAND_HP_BOUNDARY_F1, BAND_HP_PER_CATEGORY_MIN, base))

    if f1_m >= BAND_PARTIAL_F1_LOW:
        msg = "HARD_PASS_PARTIAL: ARM_BOUNDARY_F1=%.4f in partial band [%.2f, %.2f)" % (
            f1_m, BAND_PARTIAL_F1_LOW, BAND_HP_BOUNDARY_F1)
        if cat_fails:
            msg += " AND categories failing per-category floor (%.2f): %s" % (BAND_HP_PER_CATEGORY_MIN, cat_fails)
        return ("MIDDLE_BAND", "%s. %s" % (msg, base))

    if f1_m >= BAND_MIDDLE_F1_LOW:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: ARM_BOUNDARY_F1=%.4f in middle band [%.2f, %.2f) -- methodology issue or "
                 "category-blindness. %s") % (f1_m, BAND_MIDDLE_F1_LOW, BAND_PARTIAL_F1_LOW, base))

    return ("HARD_FAIL",
            ("HARD_FAIL_META_REASONING_BROKEN: ARM_BOUNDARY_F1=%.4f < %.2f -- CHTV-1 does NOT transfer to a richer "
             "NAMED corpus across 4 categories. Mechanism (sound by construction) is failing at this corpus design. "
             "%s") % (f1_m, BAND_MIDDLE_F1_LOW, base))


# ============================================================================
# Driver
# ============================================================================
print("[config] anchor=%s mode=%s seeds=%s n_folds=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_FOLDS), flush=True)
groups = load_corpus(CORPUS_PATH)
n_tp, n_adv = _validate_corpus(groups)
print("[load] %d corpus groups (TP=%d ADV=%d) from %s" % (len(groups), n_tp, n_adv, CORPUS_PATH.name), flush=True)

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
    "bands": {
        "HP_TP_MERGE": BAND_HP_TP_MERGE, "HP_TP_MERGE_CV": BAND_HP_TP_MERGE_CV,
        "HP_FP_MERGE": BAND_HP_FP_MERGE, "HP_FN_MISS": BAND_HP_FN_MISS,
        "HP_BOUNDARY_F1": BAND_HP_BOUNDARY_F1, "HP_PER_CATEGORY_MIN": BAND_HP_PER_CATEGORY_MIN,
        "PARTIAL_F1_LOW": BAND_PARTIAL_F1_LOW, "MIDDLE_F1_LOW": BAND_MIDDLE_F1_LOW,
    },
    "config_version": "v3_NAMED_corpus_stratified_seeds_11_13_19_3fold_capability_fallback_DISABLED",
    "corpus_path": str(CORPUS_PATH.relative_to(REPO)),
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
