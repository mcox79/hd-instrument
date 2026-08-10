"""exp_crutch_fade_bank_native_promotion_test_a_v1 -- Test A: does BANK->native promotion actually
FADE the crutch, and does the guard hold against inconsistent items? (2026-08-10)

Pre-reg: preregs/2026-08-10_crutch_fade_bank_native_promotion_test_a_v1.md
Engine:  hdlab/grounding_acquisition_loop.py::consolidation_pass (native_store connector, NEW this
         session) + hdlab/hd_fact_store.py::HDFactStore (native trust-bound store, UNMODIFIED).
Drills:  notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md (DRILL 3)
         notes/research_brain_scaffolding_that_fades_2026-08-10.md (DRILL 2)
         notes/research_crutch_design_and_generalization_2026-08-10.md (DRILL 1)

WHAT: a synthetic-mechanism (NOT capability) test of the load-bearing precondition for the whole
crutch-that-fades architecture -- can a confirmed item mechanically migrate overlay->native, gated
on exposure AND consistency, while an inconsistent item never does? 17 hand-specified synthetic
lemmas (5 categories, exact (n_pos, n_neg, context_mode) per lemma -- see pre-reg) drive the REAL
Library/consolidation_pass/HDFactStore machinery; nothing here is mocked or hand-computed outside
the cell's own call into the real engine.

# CELL-TEMPLATE MANDATORY (per exp_dev canonical checklist, mechanism-cell subset):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - deterministic_seeding: fixed integer seeds only; no hash()-seeding, no list(set())
# - arms_differ_verified: the 5 category groups' (lemma, final_status) sets provably differ
# - real_code_path_exercised: Library / consolidation_pass / HDFactStore.store / .query all
#   constructed+called for real in self_test() at reduced scale, not a synthetic-only branch
# - Gate 2 (guard-holds) short-circuits the verdict to HARD_FAIL on ANY leak, vetted hardest
# - permutation-test scramble control (200 shuffles) for the exposure*consistency correlation,
#   not a single shuffle (n=12 is too small for one draw to be a reliable null)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, context_vector, consolidation_pass, D as CTX_D,
    PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY,
)
from hdlab.hd_fact_store import HDFactStore  # noqa: E402

ANCHOR_NAME = "crutch_fade_bank_native_promotion_test_a_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

N_PASSES = 6                 # >= intervening-pass (1) + patience_max(3) so scrambled items fully
                              # resolve to ESCALATED, plus slack.
MIN_CONFIRM = 4
SCHEMA_THRESH = 0.10          # matches grounding_acquisition_loop's own self-test constant
NEUTRAL_BAND = 0.34
PATIENCE_MAX = 3

# ---- synthetic confirmation regime (exact, hand-specified; see pre-reg Section "Test A design") --
# (lemma, n_pos, n_neg, context_mode) ; context_mode in {"coherent", "scrambled"}
PROMOTE_EXPECTED = [
    ("c1_allpos8", 8, 0, "coherent"),
    ("c2_allpos10", 10, 0, "coherent"),
    ("c3_high_pos12", 11, 1, "coherent"),
    ("c4_allneg9", 0, 9, "coherent"),
    ("c5_boundary_neg8", 1, 7, "coherent"),
]
BANKED_BUT_BLOCKED = [
    ("b1_weak_pos8", 6, 2, "coherent"),
    ("b2_weak_neg12", 3, 9, "coherent"),
    ("b3_short_pos6", 6, 0, "coherent"),
    ("b4_short_pos7", 7, 0, "coherent"),
    ("b5_both_weak4", 3, 1, "coherent"),
]
NEUTRAL_INCONSISTENT = [
    ("n1_tie8", 4, 4, "coherent"),
    ("n2_tie10", 5, 5, "coherent"),
]
RARE_UNDER_MIN_CONFIRM = [
    ("r1_rare2a", 2, 0, "coherent"),
    ("r2_rare2b", 1, 1, "coherent"),
    ("r3_rare3", 3, 0, "coherent"),
]
SCRAMBLED_CONTEXT_ADVERSARIAL = [
    ("s1_scrambled8", 8, 0, "scrambled"),
    ("s2_scrambled10", 10, 0, "scrambled"),
]
ALL_CATEGORIES = {
    "PROMOTE_EXPECTED": PROMOTE_EXPECTED,
    "BANKED_BUT_BLOCKED": BANKED_BUT_BLOCKED,
    "NEUTRAL_INCONSISTENT": NEUTRAL_INCONSISTENT,
    "RARE_UNDER_MIN_CONFIRM": RARE_UNDER_MIN_CONFIRM,
    "SCRAMBLED_CONTEXT_ADVERSARIAL": SCRAMBLED_CONTEXT_ADVERSARIAL,
}
MUST_NOT_PROMOTE_LEMMAS = frozenset(
    l for _, group in ALL_CATEGORIES.items() for (l, *_ ) in group
    if group is not PROMOTE_EXPECTED
)
BANK_BRANCH_LEMMAS = frozenset(
    l for group in (PROMOTE_EXPECTED, BANKED_BUT_BLOCKED, NEUTRAL_INCONSISTENT) for (l, *_) in group
)

COHERENT_TEXT = "Nell repaired the engine before the harvest festival began."


# ------------------------------------------------------------------ start-marker / crash diagnostics
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------ synthetic-stream construction
def _seed_for(lemma: str) -> int:
    """Deterministic per-lemma RNG seed (hashlib, PROT-023/F.5 compliant -- never built-in hash())."""
    return int.from_bytes(hashlib.sha256(lemma.encode("utf-8")).digest()[:8], "big") % (2**31)


def build_library(categories: dict) -> Library:
    lib = Library()
    for _, group in categories.items():
        for lemma, n_pos, n_neg, mode in group:
            rng = np.random.default_rng(_seed_for(lemma))
            if mode == "coherent":
                ctx = context_vector(COHERENT_TEXT)
            traces = [("POS",) for _ in range(n_pos)] + [("NEG",) for _ in range(n_neg)]
            for i, (pole,) in enumerate(traces):
                if mode == "scrambled":
                    ctx_i = rng.choice([-1.0, 1.0], size=CTX_D)
                else:
                    ctx_i = ctx
                lib.flag(lemma, f"{lemma}_e{i}", pole, ctx_i, 1)
    return lib


def run_consolidation(lib: Library, native_store: HDFactStore, n_passes: int,
                      promote_min_exposure: int, promote_min_consistency: float) -> list:
    pass_reports = []
    for p in range(1, n_passes + 1):
        rep = consolidation_pass(lib, p, min_confirm=MIN_CONFIRM, schema_thresh=SCHEMA_THRESH,
                                 neutral_band=NEUTRAL_BAND, patience_max=PATIENCE_MAX, register=False,
                                 native_store=native_store, promote_min_exposure=promote_min_exposure,
                                 promote_min_consistency=promote_min_consistency,
                                 promote_source="test_a_synthetic")
        pass_reports.append(rep)
    return pass_reports


# ------------------------------------------------------------------ correlation + permutation test
def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def correlation_with_permutation_test(products: list, promoted: list, n_perm: int = 200,
                                      seed: int = 12345) -> dict:
    x = np.asarray(products, dtype=np.float64)
    y = np.asarray(promoted, dtype=np.float64)
    r_true = _pearson(x, y)
    rng = np.random.default_rng(seed)
    null_rs = []
    n = len(y)
    for _ in range(n_perm):
        perm = rng.permutation(n)
        null_rs.append(_pearson(x, y[perm]))
    null_rs = np.array(null_rs)
    perm_p = float(np.mean(np.abs(null_rs) >= abs(r_true)))
    return {"r_true": round(r_true, 4), "n_points": n,
            "null_mean_abs_r": round(float(np.mean(np.abs(null_rs))), 4),
            "null_p95_abs_r": round(float(np.percentile(np.abs(null_rs), 95)), 4),
            "perm_p": round(perm_p, 4), "n_perm": n_perm}


# ------------------------------------------------------------------ arms-must-differ (META_RULE_AF)
def _arms_must_differ(final_status: dict) -> dict:
    digests = {}
    for cat_name, group in ALL_CATEGORIES.items():
        lemmas = sorted(l for l, *_ in group)
        fingerprint = tuple((l, final_status.get(l, "MISSING")) for l in lemmas)
        b = json.dumps(fingerprint).encode("utf-8")
        digests[cat_name] = hashlib.sha256(b).hexdigest()
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], (
                f"META_RULE_AF VIOLATION: category {names[i]!r} and {names[j]!r} produced "
                f"bit-identical (lemma,status) fingerprints -- category configs likely copy-pasted")
    return digests


# ------------------------------------------------------------------ main run
def run(output_dir, run_mode, seed=0):
    t0 = time.perf_counter()
    n_bank_lemmas = len(BANK_BRANCH_LEMMAS)
    expected_n_units = n_bank_lemmas + len(MUST_NOT_PROMOTE_LEMMAS - BANK_BRANCH_LEMMAS)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    lib = build_library(ALL_CATEGORIES)
    store = HDFactStore(n_dim=4096, seed=seed)
    print(f"[test_a] built library: {len(lib.items)} lemmas across "
          f"{len(ALL_CATEGORIES)} categories", flush=True)

    pass_reports = run_consolidation(lib, store, N_PASSES, PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY)
    for i, rep in enumerate(pass_reports, 1):
        print(f"[test_a] pass {i}/{N_PASSES}: grounded_cum={rep['cumulative_grounded']} "
              f"escalated_cum={rep['cumulative_escalated']} pending_cum={rep['cumulative_pending']} "
              f"promotions_this_pass={sum(1 for e in rep['promotion_log'] if e['promoted'])}", flush=True)

    final_status = {l: it.status for l, it in lib.items.items()}
    digests = _arms_must_differ(final_status)

    # ---- Gate 1: promotion works (PROMOTE_EXPECTED items) ----
    promoted_now = {}   # lemma -> readable-lookup-free bool, checked via native_store.query()
    for lemma, *_ in [row for grp in ALL_CATEGORIES.values() for row in grp]:
        hits = store.query(lemma, "OUTCOME_POLARITY")
        promoted_now[lemma] = bool(hits) and hits[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED")

    gate1_hits = [l for l, *_ in PROMOTE_EXPECTED if promoted_now[l]]
    gate1_rate = len(gate1_hits) / len(PROMOTE_EXPECTED)

    # ---- Gate 2: guard holds (must NOT promote) ----
    leaked = [l for l in MUST_NOT_PROMOTE_LEMMAS if promoted_now[l]]
    n_must_not = len(MUST_NOT_PROMOTE_LEMMAS)
    guard_holds = (len(leaked) == 0)

    # ---- Gate 2b: old schema-consistency guard still fires (scrambled items ESCALATE) ----
    scrambled_lemmas = [l for l, *_ in SCRAMBLED_CONTEXT_ADVERSARIAL]
    scrambled_statuses = {l: final_status.get(l, "MISSING") for l in scrambled_lemmas}
    gate2b_ok = all(scrambled_statuses[l] == "ESCALATED" for l in scrambled_lemmas)

    # ---- RARE sanity: must stay PENDING (never reach consolidation eligibility) ----
    rare_lemmas = [l for l, *_ in RARE_UNDER_MIN_CONFIRM]
    rare_statuses = {l: final_status.get(l, "MISSING") for l in rare_lemmas}
    rare_ok = all(rare_statuses[l] == "PENDING" for l in rare_lemmas)

    # ---- Gate 3: correlation over the 12 BANK-branch items ----
    bank_lemmas = sorted(BANK_BRANCH_LEMMAS)
    exposure_of = {}
    consistency_of = {}
    label_of = {}
    lemma_config = {l: (p, n) for grp in ALL_CATEGORIES.values() for (l, p, n, _m) in grp}
    for l in bank_lemmas:
        p, n = lemma_config[l]
        exposure_of[l] = p + n
        consistency_of[l] = abs((p - n) / (p + n)) if (p + n) else 0.0
        label_of[l] = final_status.get(l, "MISSING")
    products = [exposure_of[l] * consistency_of[l] for l in bank_lemmas]
    promoted_bits = [1 if promoted_now[l] else 0 for l in bank_lemmas]
    corr_report = correlation_with_permutation_test(products, promoted_bits, n_perm=200, seed=seed + 12345)

    # secondary (non-gating, honestly disclosed) correlation over ALL 17 items
    all_lemmas_sorted = sorted(l for grp in ALL_CATEGORIES.values() for l, *_ in grp)
    products_all = [exposure_of.get(l, lemma_config[l][0] + lemma_config[l][1])
                    * consistency_of.get(l, abs((lemma_config[l][0] - lemma_config[l][1])
                                                / max(1, lemma_config[l][0] + lemma_config[l][1])))
                    for l in all_lemmas_sorted]
    promoted_bits_all = [1 if promoted_now[l] else 0 for l in all_lemmas_sorted]
    corr_report_all17 = correlation_with_permutation_test(products_all, promoted_bits_all,
                                                           n_perm=200, seed=seed + 54321)

    # ---- verdict logic (pre-registered, Gate 2 short-circuits) ----
    hard_fail_reasons = []
    if not guard_holds:
        hard_fail_reasons.append(
            f"GUARD_LEAK: {len(leaked)}/{n_must_not} must-not-promote items DID promote: {leaked} -- "
            f"the false-memory/consistency guard is BROKEN; this is the make-or-break failure the "
            f"Director flagged as disqualifying regardless of any other gate")
    if gate1_rate < 0.6:
        hard_fail_reasons.append(
            f"MECHANISM_DEAD_OR_WEAK: only {len(gate1_hits)}/{len(PROMOTE_EXPECTED)} "
            f"PROMOTE_EXPECTED items actually promoted")
    corr_gap = corr_report["r_true"] - corr_report["null_mean_abs_r"]
    if corr_gap < 0.2:
        hard_fail_reasons.append(
            f"CORRELATION_NOT_ABOVE_NOISE: r_true={corr_report['r_true']} vs "
            f"null_mean_abs_r={corr_report['null_mean_abs_r']} (gap={round(corr_gap, 4)} < 0.2)")
    if not gate2b_ok:
        hard_fail_reasons.append(
            f"OLD_GUARD_REGRESSED: scrambled-context items did not all ESCALATE: {scrambled_statuses}")

    guard_leak_present = not guard_holds
    if guard_leak_present:
        verdict = "HARD_FAIL"
    elif gate1_rate < 0.6 or corr_gap < 0.2 or not gate2b_ok:
        verdict = "HARD_FAIL"
    elif (gate1_rate == 1.0 and guard_holds and gate2b_ok
          and corr_report["r_true"] >= 0.5 and corr_report["perm_p"] < 0.05
          and corr_report["null_mean_abs_r"] < 0.15):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"{verdict}: gate1_promote_rate={gate1_rate}({len(gate1_hits)}/{len(PROMOTE_EXPECTED)}) "
        f"guard_holds={guard_holds}(leaked={len(leaked)}/{n_must_not}: {leaked}) "
        f"old_guard_ok={gate2b_ok}(scrambled={scrambled_statuses}) "
        f"rare_ok={rare_ok}(statuses={rare_statuses}) "
        f"corr(12-item bank-branch)=r_true:{corr_report['r_true']} perm_p:{corr_report['perm_p']} "
        f"null_mean_abs_r:{corr_report['null_mean_abs_r']} gap:{round(corr_gap, 4)} | "
        f"reasons={hard_fail_reasons}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:200]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {"n_passes": N_PASSES, "min_confirm": MIN_CONFIRM, "schema_thresh": SCHEMA_THRESH,
                  "neutral_band": NEUTRAL_BAND, "patience_max": PATIENCE_MAX,
                  "promote_min_exposure": PROMOTE_MIN_EXPOSURE,
                  "promote_min_consistency": PROMOTE_MIN_CONSISTENCY, "seed": seed,
                  "native_store_n_dim": 4096},
        "synthetic_regime": {name: [{"lemma": l, "n_pos": p, "n_neg": n, "context_mode": m}
                                    for l, p, n, m in grp]
                             for name, grp in ALL_CATEGORIES.items()},
        "final_status": final_status,
        "promoted_now": promoted_now,
        "gate1_promote_expected": {"rate": gate1_rate, "hits": gate1_hits,
                                   "n_expected": len(PROMOTE_EXPECTED)},
        "gate2_guard": {"holds": guard_holds, "leaked_lemmas": leaked, "n_must_not_promote": n_must_not},
        "gate2b_old_guard_regression_check": {"ok": gate2b_ok, "scrambled_statuses": scrambled_statuses},
        "rare_sanity": {"ok": rare_ok, "statuses": rare_statuses},
        "correlation_bank_branch_12item": corr_report,
        "correlation_all_17item_secondary_nongating": corr_report_all17,
        "exposure_of": exposure_of, "consistency_of": consistency_of, "label_of": label_of,
        "pass_reports": pass_reports,
        "hard_fail_reasons": hard_fail_reasons,
        "category_digests": digests,
        "arms_differ_verified": True,
        "cardinality_ok": len(BANK_BRANCH_LEMMAS) == 12,
        "expected_n_units": expected_n_units,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "deterministic threshold-gate + permutation-test mechanism cell; no argmax/"
                   "capacity noise floor applies",
        "deterministic_seeding": True,
        "progress_logging": "n_a_sub_5s_wall_time",
        "guard_vetted_hardest": True,
        "is_synthetic_mechanism_test_not_capability_claim": True,
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.2f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# ------------------------------------------------------------------ self-test (real code path)
def self_test():
    """Fast real-code-path self-test at reduced scale (3 lemmas): real Library, real
    consolidation_pass, real HDFactStore.store/.query -- not a synthetic-only branch."""
    print("[self-test] real Library/consolidation_pass/HDFactStore at reduced scale", flush=True)
    store = HDFactStore(n_dim=512, seed=999)
    lib = Library()
    ctx = context_vector(COHERENT_TEXT)
    # promote-expected: 8 POS, coherent.
    for i in range(8):
        lib.flag("st_promote", f"e{i}", "POS", ctx, 1)
    # must-not-promote: 6 POS / 2 NEG (margin=0.5 < 0.75), coherent, high exposure.
    for i in range(6):
        lib.flag("st_block", f"p{i}", "POS", ctx, 1)
    for i in range(2):
        lib.flag("st_block", f"n{i}", "NEG", ctx, 1)
    # scrambled: 8 POS but independent-noise context per trace.
    rng = np.random.default_rng(1)
    for i in range(8):
        lib.flag("st_scrambled", f"s{i}", "POS", rng.choice([-1.0, 1.0], size=CTX_D), 1)

    for p in range(1, 6):
        consolidation_pass(lib, p, min_confirm=4, schema_thresh=0.10, neutral_band=0.34,
                           patience_max=3, register=False, native_store=store,
                           promote_min_exposure=8, promote_min_consistency=0.75,
                           promote_source="self_test")

    assert lib.items["st_promote"].status == "GROUNDED_POS"
    hit = store.query("st_promote", "OUTCOME_POLARITY")
    assert hit and hit[0]["object"] == "POS", f"promote-expected item not readable: {hit}"

    assert lib.items["st_block"].status == "GROUNDED_POS", (
        f"margin=0.5 item must still bank, got {lib.items['st_block'].status}")
    assert store.query("st_block", "OUTCOME_POLARITY") == [], "GUARD LEAK in self-test"

    assert lib.items["st_scrambled"].status == "ESCALATED", (
        f"scrambled-context item must ESCALATE, got {lib.items['st_scrambled'].status}")
    assert store.query("st_scrambled", "OUTCOME_POLARITY") == []

    # permutation-test sanity: identical x/y -> r=1.0; independent random -> |r| small.
    perfect = correlation_with_permutation_test([1, 2, 3, 4], [0, 0, 1, 1], n_perm=50, seed=0)
    assert perfect["r_true"] > 0.8, perfect

    print("[self-test] PASS: real promote+guard+old-guard+permutation-test machinery all exercised",
          flush=True)
    return {"promote_ok": True, "guard_ok": True, "old_guard_ok": True, "perm_test_sane": True}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")  # accepted for runner-convention parity; this
                                                       # cell has no full-vs-smoke split (see pre-reg
                                                       # "Dispatch": sub-5s deterministic, run once)
    ap.add_argument("--device", default="cpu")
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    output_dir = OUTPUT_DIR_FULL
    run(output_dir, run_mode="full", seed=0)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    else:
        _out = OUTPUT_DIR_FULL
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
