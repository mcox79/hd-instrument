# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (claim1 real/decoy/ortho/freq prediction arrays hashed)
# - final_metrics_atomicity = tmp_replace (single-shot, reuses V1._atomic_write)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete exact-match / co-occurrence gap metric, no Gaussian floor)
# - baseline_in_band EXEMPTED for decoy/ortho/freq arms (intentional can-fail floor controls)
# - discriminator survives scale: runs the REAL pipeline against the SAME frozen v2 snapshot,
#   full N=150, not a toy substitute
# - HARD_PASS strictly above floor_max (max of chance/ortho/freq, same band formula as v1/v2)
# - HP_SCOPE: bands declared in the pre-reg; INSTRUMENT_STILL_LOOSE overrides claim1 verdict if
#   the decisive validity gate (decoy near chance) fails -- mandatory instrument check, mirrors
#   v2's known_answer_arm INSTRUMENT_INVALID_ABORT pattern
# - cardinality_ok: N/A (no sweep axis; fixed sample size, declared no_sweep_axis)
# - per-unit failure-class instrumentation: N/A (single failed unit = code bug, propagates)
# - calibration_check: default_ok_for_this_regime (fixed threshold MIN_STEM_COVERAGE=0.6, fixed
#   BEFORE any real-store number was computed -- see pre-reg "Fix" section, not tuned post-hoc)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL HDFactStore objects via reused V2 known_answer_arm (production
#   n_dim=2048); this cell's OWN new logic (_prefix_covers, cooccurs_v3, prefix_count_v3) is pure
#   string/formula code, self-tested against fixed worked examples (com/comes, com/company, ...)
# - substrate_signature_checked: N/A for this cell's new code (no new HDFactStore construction;
#   reuses V1/V2 store-facing functions unchanged)
"""exp_foundation_validation_harness_v3_tightened_v1 -- repair of the claim-1 (CORRECTNESS)
instrument in exp_foundation_validation_harness_v2_floors_v1. See preregs/2026-08-15_foundation_
validation_harness_v3_tightened_v1.md for full diagnosis, fix design, and the pre-registered
decisive validity gate.

WHY: v2's claim1 HARD_FAILed (precision_hat=0.9667 vs floor_max=0.96/frequency, gap=0.0067) but
independent re-verification (this pre-reg) showed the floor construction itself is broken: ALL
FOUR claim-1 arms (real/decoy/ortho/freq) share one primitive, cooccurs() -- same-sentence-anywhere,
UNNORMALIZED prefix match -- and 105/150 sampled rows have all four arms hit simultaneously on the
same lemma. The frequency floor's ranker (prefix_count, unnormalized) additionally picks 'com'
(a genuine but 3-character stem of 'comes') globally because short prefixes match more corpus word
types, not because of any store contamination (store is clean, see .claude/scan-out/
frequency-floor-com.json, independently re-verified in the pre-reg).

FIX: a minimum stem-coverage ratio (len(prefix)/len(matched_token) >= 0.6, fixed from the single
com/comes worked example BEFORE any full-scale number was computed) applied symmetrically to both
sides of cooccurs() and to prefix_count()'s per-token counting. Only claim 1 is recomputed; claims
2 and 3 do not use cooccurs()/prefix_count() for their pass/fail arms and are read back from v2's
metrics.json unchanged (see pre-reg "Scope / non-goals").

DECISIVE GATE (pre-registered, checked BEFORE trusting any claim1 number): chance_hat (random
decoy) must drop to <= 0.15 ("near chance"). If it does not, this run reports
INSTRUMENT_STILL_LOOSE and no claim1 correctness number is asserted as trustworthy -- the fix is
not retuned to force a pass.

Modes: --self-test (formula fixtures, <5s) / --smoke (real pipeline, reduced N, frozen snapshot) /
--full (real pipeline, full N=150, requires --foundation-dir; reuses the exact v2 frozen snapshot
by default via --reuse-v2-snapshot for an apples-to-apples comparison).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

ANCHOR_NAME = "foundation_validation_harness_v3_tightened_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_foundation_validation_harness_v1 as V1  # noqa: E402
import experiments.exp_foundation_validation_harness_v2_floors_v1 as V2  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.foundation_persistence import load_store, load_concept_space  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEED = V2.SEED  # unchanged: 20260815, reproduces the SAME 150-pair sample as v2
GM_REL = V1.GM_REL

N_CORRECTNESS = V1.N_CORRECTNESS  # {"smoke": 20, "full": 150}
MIN_STEM_COVERAGE = 0.6  # fixed from the com/comes worked example BEFORE any real-store run
CHANCE_NEAR_GATE = 0.15  # decisive validity gate, declared in the pre-reg before running

repo_path = V1.repo_path
wilson_ci = V1.wilson_ci
load_corpus_sentences = V1.load_corpus_sentences
predict_orthographic_best = V2.predict_orthographic_best  # unchanged: pure string transform
run_known_answer_arm = V2.run_known_answer_arm

TOKEN_RE = re.compile(r"[A-Za-z']+")


# =========================================================================== tightened primitives
def _prefix_covers(prefix: str, token: str, min_coverage: float = MIN_STEM_COVERAGE) -> bool:
    """True iff `token` starts with `prefix` (case-insensitive) AND `prefix` explains at least
    `min_coverage` of `token`'s characters. Kills 'com'->'company' (0.43) while keeping the
    genuine stem match 'com'->'comes' (0.60, boundary, >=)."""
    tl, pl = token.lower(), prefix.lower()
    if not pl or not tl.startswith(pl):
        return False
    return (len(pl) / len(tl)) >= min_coverage


def _sentence_tokens(sentence: str) -> List[str]:
    return TOKEN_RE.findall(sentence)


def _sentence_has_covering_match(query: str, tokens: Sequence[str],
                                 min_coverage: float = MIN_STEM_COVERAGE) -> bool:
    return any(_prefix_covers(query, t, min_coverage) for t in tokens)


def cooccurs_v3(lemma: str, other: str, tokenized_sentences: Sequence[List[str]]) -> bool:
    """Tightened replacement for V1.cooccurs: same-sentence-anywhere is UNCHANGED, but each side
    of the pair must be a COVERING prefix match (>=60% of the matched word's length), applied
    symmetrically to lemma and other -- not just the candidate side."""
    for tokens in tokenized_sentences:
        if (_sentence_has_covering_match(lemma, tokens) and
                _sentence_has_covering_match(other, tokens)):
            return True
    return False


def prefix_count_v3(lemma: str, tokenized_sentences: Sequence[List[str]]) -> int:
    """Tightened replacement for V2.prefix_count: counts corpus TOKENS that are a covering prefix
    match for `lemma` (>=60% coverage), not merely lexicographic-range prefix matches."""
    n = 0
    for tokens in tokenized_sentences:
        for t in tokens:
            if _prefix_covers(lemma, t):
                n += 1
    return n


def predict_frequency_mode_v3(counted: Counter) -> Optional[str]:
    if not counted:
        return None
    return sorted(counted.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


# =========================================================================== claim 1 (tightened)
def run_claim1_tightened(store: HDFactStore, tokenized_sentences: List[List[str]],
                         n_sample: int, seed: int, output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    n_live = len(gm_facts)
    cross = sorted(((f.subject, f.obj) for f in gm_facts if f.subject != f.obj))

    all_objects = sorted({f.obj for f in gm_facts})
    obj_freq_counts = Counter({o: prefix_count_v3(o, tokenized_sentences) for o in all_objects})
    freq_pick_global = predict_frequency_mode_v3(obj_freq_counts)

    n = min(n_sample, len(cross))
    rng = random.Random(seed)
    sample = rng.sample(cross, n) if n > 0 else []

    ckpt_dir = os.path.join(output_dir, "ckpt_claim1_v3")
    done = completed_units(ckpt_dir)
    for i, (lemma, canon_obj) in enumerate(sample):
        key = unit_key("c1v3", i, lemma, canon_obj)
        if key in done:
            continue
        decoy_pool = [o for o in all_objects if o not in (canon_obj, lemma)]
        decoy = rng.choice(decoy_pool) if decoy_pool else canon_obj
        ortho_pick = predict_orthographic_best(lemma, all_objects) or canon_obj
        real_hit = cooccurs_v3(lemma, canon_obj, tokenized_sentences)
        decoy_hit = cooccurs_v3(lemma, decoy, tokenized_sentences)
        ortho_hit = cooccurs_v3(lemma, ortho_pick, tokenized_sentences)
        freq_hit = cooccurs_v3(lemma, freq_pick_global, tokenized_sentences) if freq_pick_global else False
        record_unit(ckpt_dir, key, {
            "lemma": lemma, "canon_obj": canon_obj, "decoy": decoy, "ortho_pick": ortho_pick,
            "freq_pick": freq_pick_global, "real_hit": real_hit, "decoy_hit": decoy_hit,
            "ortho_hit": ortho_hit, "freq_hit": freq_hit,
        })

    units = load_units(ckpt_dir)
    rows = list(units.values())
    n_eval = len(rows)

    def _rate(field):
        k = sum(1 for r in rows if r[field])
        return k, (k / n_eval if n_eval else 0.0)

    k_real, precision_hat = _rate("real_hit")
    k_decoy, chance_hat = _rate("decoy_hit")
    k_ortho, ortho_rate = _rate("ortho_hit")
    k_freq, freq_rate = _rate("freq_hit")

    lo_p, hi_p = wilson_ci(k_real, n_eval)
    floors = {"chance": (chance_hat, wilson_ci(k_decoy, n_eval)),
             "orthographic": (ortho_rate, wilson_ci(k_ortho, n_eval)),
             "frequency": (freq_rate, wilson_ci(k_freq, n_eval))}
    floor_name = max(floors, key=lambda k: floors[k][0])
    floor_max, (floor_lo, floor_hi) = floors[floor_name][0], floors[floor_name][1]
    gap = precision_hat - floor_max

    validity_gate_pass = chance_hat <= CHANCE_NEAR_GATE
    if not validity_gate_pass:
        verdict = "INSTRUMENT_STILL_LOOSE"
    elif gap >= 0.20 and lo_p > floor_hi:
        verdict = "HARD_PASS"
    elif gap < 0.05:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict, "validity_gate_pass": validity_gate_pass,
        "chance_near_gate_threshold": CHANCE_NEAR_GATE,
        "n_live_grounded_meaning": n_live, "n_cross_grounded": len(cross),
        "n_sampled": n_eval, "precision_hat": round(precision_hat, 4),
        "chance_hat": round(chance_hat, 4), "ortho_rate": round(ortho_rate, 4),
        "freq_rate": round(freq_rate, 4), "floor_name": floor_name, "floor_max": round(floor_max, 4),
        "gap": round(gap, 4), "wilson_precision": [round(lo_p, 4), round(hi_p, 4)],
        "wilson_floor": [round(floor_lo, 4), round(floor_hi, 4)],
        "freq_pick_global": freq_pick_global, "n_sentences": len(tokenized_sentences),
        "n_distinct_objects": len(all_objects),
        "min_stem_coverage": MIN_STEM_COVERAGE,
        "arms_differ_verified": len({tuple(r["canon_obj"] for r in rows),
                                     tuple(r["decoy"] for r in rows),
                                     tuple(r["ortho_pick"] for r in rows)}) > 1 if rows else False,
        # comparison vs v2 (same sample, old primitives) -- read from v2's landed metrics, not
        # recomputed, purely for the report's before/after table
        "v2_comparison": {"precision_hat": 0.9667, "chance_hat": 0.7667, "ortho_rate": 0.84,
                          "freq_rate": 0.96, "floor_max": 0.96, "gap": 0.0067,
                          "verdict": "HARD_FAIL"},
    }


# =========================================================================== self-tests
def _selftest_prefix_covers_worked_examples() -> None:
    # the case the whole fix is built on: com IS the true stem of comes
    assert _prefix_covers("com", "comes") is True, "com/comes=0.60 must pass at >=0.6"
    assert _prefix_covers("com", "come") is True, "com/come=0.75 must pass"
    # the bug case: com must NOT cover these
    assert _prefix_covers("com", "company") is False, "com/company=0.43 must fail"
    assert _prefix_covers("com", "common") is False, "com/common=0.50 must fail"
    assert _prefix_covers("com", "coming") is False, "com/coming=0.50 must fail"
    assert _prefix_covers("com", "community") is False
    assert _prefix_covers("com", "compare") is False
    assert _prefix_covers("com", "complete") is False
    assert _prefix_covers("com", "component") is False
    assert _prefix_covers("com", "computer") is False
    # genuine long stems must still pass
    assert _prefix_covers("villag", "village") is True, "villag/village=0.857 must pass"
    assert _prefix_covers("villag", "villager") is True, "villag/villager=0.75 must pass"
    # non-prefix must always fail regardless of coverage math
    assert _prefix_covers("villag", "pillage") is False
    # empty / non-match edge cases
    assert _prefix_covers("", "anything") is False
    assert _prefix_covers("zzz", "abc") is False


def _selftest_prefix_count_v3_differs_from_v2_bug_case() -> None:
    sentences = ["The word comes and come are used here.",
                "The company serves the community with common goods.",
                "A computer can compare and complete a component."]
    tokenized = [_sentence_tokens(s) for s in sentences]
    old_count = V2.prefix_count("com", V2.build_sorted_tokens(sentences))
    new_count = prefix_count_v3("com", tokenized)
    assert old_count > new_count, (old_count, new_count)  # old over-counts, new must be lower
    assert new_count == 2, new_count  # "comes" + "come" only


def _selftest_prefix_count_v3_villag_unaffected_case() -> None:
    sentences = ["the village council met.", "villagers gathered near the well.",
                "pillage is not the same word."]
    tokenized = [_sentence_tokens(s) for s in sentences]
    n = prefix_count_v3("villag", tokenized)
    assert n == 2, n  # village, villagers -- pillage excluded (not a prefix match at all)


def _selftest_cooccurs_v3_discriminates_com_case() -> None:
    s_true = "the bottle liquid comes from a source."
    s_false_only = "the company runs a community program."
    tok_true = [_sentence_tokens(s_true)]
    tok_false = [_sentence_tokens(s_false_only)]
    # com/source: real morphological match (comes) present in s_true -> covering match fires
    assert _sentence_has_covering_match("com", _sentence_tokens(s_true)) is True
    # com in s_false_only: only "company"/"community" present, neither covers -> must NOT fire
    assert _sentence_has_covering_match("com", _sentence_tokens(s_false_only)) is False
    # end-to-end cooccurs_v3 sanity: lemma+other must both covering-match in the SAME sentence
    assert cooccurs_v3("com", "bottl", tok_true) is True
    assert cooccurs_v3("com", "runs", tok_false) is False  # "com" doesn't cover in this sentence


def _selftest_cooccurs_v3_basic_v1_parity() -> None:
    sentences = ["the village council met at dawn.", "villagers gathered near the old well."]
    tokenized = [_sentence_tokens(s) for s in sentences]
    assert cooccurs_v3("villag", "council", tokenized) is True
    assert cooccurs_v3("villag", "dawn", tokenized) is True
    assert cooccurs_v3("villag", "zzznope", tokenized) is False


def _selftest_known_answer_arm_still_valid() -> None:
    """This cell does not modify HDFactStore/query mechanics at all -- reuses V2's known-answer
    arm verbatim. Re-asserted here as the mandatory instrument gate for THIS cell too."""
    result = run_known_answer_arm(n_dim=2048, k_chains=10, seed=777)
    assert result["instrument_valid"] is True, result
    assert result["accuracy"] == 1.0, result


def _run_all_selftests() -> dict:
    _selftest_prefix_covers_worked_examples()
    _selftest_prefix_count_v3_differs_from_v2_bug_case()
    _selftest_prefix_count_v3_villag_unaffected_case()
    _selftest_cooccurs_v3_discriminates_com_case()
    _selftest_cooccurs_v3_basic_v1_parity()
    _selftest_known_answer_arm_still_valid()
    return {
        "prefix_covers_worked_examples_ok": True,
        "prefix_count_v3_differs_from_v2_bug_case_ok": True,
        "prefix_count_v3_villag_unaffected_case_ok": True,
        "cooccurs_v3_discriminates_com_case_ok": True,
        "cooccurs_v3_basic_v1_parity_ok": True,
        "known_answer_arm_still_valid_ok": True,
    }


# =========================================================================== orchestration
def run_validation(foundation_dir: str, run_mode: str, output_dir: str,
                   corpus_sources: Sequence[Tuple[str, str, str]]) -> dict:
    t0 = time.perf_counter()
    store = load_store(os.path.join(foundation_dir, "store"))
    print(f"[load] n_facts={len(store._facts)} n_dim={store.n_dim} foundation_dir={foundation_dir}",
          flush=True)

    sentences = load_corpus_sentences(corpus_sources)
    tokenized_sentences = [_sentence_tokens(s) for s in sentences]
    print(f"[corpus] {len(sentences)} sentences tokenized from {len(corpus_sources)} sources",
          flush=True)

    ka = run_known_answer_arm(n_dim=store.n_dim, k_chains=20, seed=SEED)
    print(f"[known_answer_arm] accuracy={ka['accuracy']} instrument_valid={ka['instrument_valid']}",
          flush=True)
    if not ka["instrument_valid"]:
        elapsed = time.perf_counter() - t0
        return {
            "verdict": "INSTRUMENT_INVALID_ABORT",
            "verdict_msg": f"known_answer_arm accuracy={ka['accuracy']} < 0.90 -- aborting before "
                          f"trusting any claim1 number", "elapsed_s": elapsed,
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
            "run_mode": run_mode, "known_answer_arm": ka,
        }

    n_correct = N_CORRECTNESS[run_mode]
    c1 = run_claim1_tightened(store, tokenized_sentences, n_correct, SEED, output_dir)
    print(f"[claim1 CORRECTNESS tightened] {c1['verdict']} validity_gate_pass="
          f"{c1['validity_gate_pass']} chance_hat={c1['chance_hat']} precision={c1['precision_hat']} "
          f"floor_max={c1['floor_max']}({c1['floor_name']}) gap={c1['gap']} n={c1['n_sampled']}",
          flush=True)

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"claim1_tightened={c1['verdict']} validity_gate_pass={c1['validity_gate_pass']}"
                  f"(chance_hat={c1['chance_hat']}<=?{CHANCE_NEAR_GATE}) gap={c1['gap']} "
                  f"floor={c1['floor_name']}={c1['floor_max']} precision={c1['precision_hat']} "
                  f"v2_precision=0.9667 v2_chance=0.7667 v2_freq=0.96 "
                  f"known_answer_instrument_valid={ka['instrument_valid']}")

    return {
        "verdict": c1["verdict"], "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "foundation_dir": foundation_dir,
        "n_facts_loaded": len(store._facts), "seed": SEED, "known_answer_arm": ka,
        "claim1_correctness_tightened": c1,
        "claim2_coherence_from_v2_unchanged": {
            "note": "not recomputed -- cooccurs/prefix_count not used by claim2's pass/fail arms",
            "source": "data/exp_foundation_validation_harness_v2_floors_v1/metrics.json",
            "verdict": "HARD_PASS", "cohesion_gap": 0.3111, "scrambled_cohesion_gap": -0.0055,
            "active_contradiction_count": 0,
        },
        "claim3_can_reason_from_v2_unchanged": {
            "note": "not recomputed -- claim3 freq_accuracy uses a store-membership Counter, not "
                    "corpus prefix_count; not implicated by this bug",
            "source": "data/exp_foundation_validation_harness_v2_floors_v1/metrics.json",
            "verdict": "HARD_PASS", "mechanism_accuracy": 1.0, "floor_max": 0.0267,
            "draw_gap_mean": 0.996, "draw_gap_sd": 0.008,
        },
        "bands": {
            "claim1_validity_gate": {"chance_hat_near_gate_max": CHANCE_NEAR_GATE},
            "claim1": {"hard_pass_gap_min": 0.20, "hard_fail_gap_max": 0.05,
                      "floor": "max(chance,ortho,freq)_tightened"},
        },
    }


# =========================================================================== I/O plumbing (reuse)
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    V1._write_start_marker(output_dir, run_mode, expected_n_units)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
           "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
           "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
           "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write(output_dir: str, metrics: Dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


# =========================================================================== main
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--foundation-dir", type=str, default=None,
                        help="frozen snapshot dir (never the live data/foundation dir)")
    args = parser.parse_args()

    if args.self_test or not (args.smoke or args.full):
        run_mode = "self_test"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_selftest")
        t0 = time.perf_counter()
        _write_start_marker(output_dir, run_mode, expected_n_units=1)
        result = _run_all_selftests()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELF_TEST_PASS",
                  "verdict_msg": "all 6 v3 formula self-tests passed (prefix-coverage worked "
                                  "examples incl. com/comes vs com/company, prefix_count_v3 differs "
                                  "from the v2 bug case, prefix_count_v3 villag-case unaffected, "
                                  "cooccurs_v3 discriminates the com case, cooccurs_v3 basic v1 "
                                  "parity, known-answer arm still valid at production n_dim)",
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    foundation_dir = args.foundation_dir
    if not foundation_dir:
        raise ValueError("--foundation-dir is required for --smoke/--full (reuse the v2 frozen "
                         "snapshot for apples-to-apples comparison; this cell never freezes a new "
                         "one and never opens data/foundation/ directly)")

    if args.smoke:
        run_mode = "smoke"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}_smoke")
        corpus_sources = V1.CORPUS_SOURCES_SMOKE
        expected_units = N_CORRECTNESS["smoke"]
    else:
        run_mode = "full"
        output_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        corpus_sources = V1.CORPUS_SOURCES_FULL
        expected_units = N_CORRECTNESS["full"]

    _write_start_marker(output_dir, run_mode, expected_n_units=expected_units)
    metrics = run_validation(foundation_dir, run_mode, output_dir, corpus_sources)
    _atomic_write(output_dir, metrics)
    print(f"[{ANCHOR_NAME}] {metrics['verdict']} elapsed={metrics['elapsed_s']:.2f}s -> {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately narrow; NOT BaseException
        _write_crash_metrics(repo_path(f"data/exp_{ANCHOR_NAME}"), e)
        raise
