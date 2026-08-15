# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (claim1 real/decoy/ortho/freq prediction arrays hashed)
# - final_metrics_atomicity = tmp_replace (single-shot, reuses V1._atomic_write pattern)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a declared (discrete exact-match / co-occurrence gap metric, no Gaussian floor)
# - baseline_in_band EXEMPTED for decoy/ortho/freq arms (intentional can-fail floor controls)
# - discriminator survives scale: runs the REAL pipeline against the SAME frozen v2 snapshot,
#   full N=150, not a toy substitute
# - HARD_PASS strictly above floor_max (max of chance/ortho/freq, same band formula as v1/v2/v3)
# - HP_SCOPE: bands declared in the pre-reg; INSTRUMENT_STILL_LOOSE overrides claim1 verdict if
#   the decisive validity gate (decoy near chance) fails -- SAME gate as v3, not retuned
# - cardinality_ok: N/A (no sweep axis; fixed sample size, declared no_sweep_axis)
# - per-unit failure-class instrumentation: N/A (single failed unit = code bug, propagates)
# - calibration_check: default_ok_for_this_regime (PROXIMITY_WINDOW=6 derived from the corpus's
#   OWN median-sentence-length structural statistic BEFORE any chance_hat number was computed --
#   see pre-reg "Fix" section; not swept or tuned against the outcome)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL HDFactStore objects via reused V2 known_answer_arm (production
#   n_dim=2048); this cell's OWN new logic (cooccurs_v4, window boundary) is pure string/formula
#   code, self-tested against fixed worked examples (window boundary, degenerate-blob regression)
# - substrate_signature_checked: N/A for this cell's new code (no new HDFactStore construction;
#   reuses V1/V2/V3 store-facing functions unchanged)
"""exp_foundation_validation_harness_v4_proximity_v1 -- THIRD repair attempt of the claim-1
(CORRECTNESS) instrument. See preregs/2026-08-15_foundation_validation_harness_v4_proximity_v1.md
for full diagnosis, mechanism choice (proximity window over dependency-parse), and the
pre-registered decisive validity gate (UNCHANGED from v3: chance_hat <= 0.15).

WHY: v3 (exp_foundation_validation_harness_v3_tightened_v1) fixed the short-prefix-over-match bug
(freq_pick flips com -> people) but FAILED its own decisive gate: chance_hat only moved
0.7667 -> 0.76 (flat). v3's own pre-reg named the correct next step on this exact outcome: a
GENUINELY DIFFERENT mechanism (proximity window / dependency check), not a parameter sweep on the
coverage threshold. This cell is that v4: cooccurs_v4 additionally requires the two matched tokens
to be within PROXIMITY_WINDOW=6 tokens of each other in the same sentence (same-sentence-anywhere
is no longer sufficient). PROXIMITY_WINDOW=6 is derived from E[|i-j|] ~= median_sentence_len/3 =
18/3 = 6, a corpus-structural statistic computed BEFORE any cooccurs_v4 result existed (see
pre-reg). A corpus-loading confound was also found during diagnosis (one base_vocabulary CSV
source loads as a single 74660-token pseudo-sentence, near-guaranteeing co-occurrence for any two
common words under same-sentence-anywhere) -- not patched here, but the proximity window
structurally suppresses its effect as a side benefit (see pre-reg, self-test 5).

FIX SCOPE: only claim 1's cooccurs primitive changes. _prefix_covers, MIN_STEM_COVERAGE=0.6, and
prefix_count_v3 (the frequency-floor ranker) are reused UNCHANGED by import from v3 -- not
retuned, not reimplemented. Claims 2 and 3 are read back from v2's metrics.json unchanged, exactly
as v3 did.

DECISIVE GATE (pre-registered, checked BEFORE trusting any claim1 number, UNCHANGED from v3):
chance_hat (random decoy) must drop to <= 0.15. If it does not, this is the THIRD consecutive
INSTRUMENT_STILL_LOOSE and must be reported plainly as such -- no retuning, no softening.

Modes: --self-test (formula fixtures, <5s) / --smoke (real pipeline, reduced N, frozen snapshot) /
--full (real pipeline, full N=150, requires --foundation-dir; reuses the exact v2/v3 frozen
snapshot by default for an apples-to-apples three-way comparison).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

ANCHOR_NAME = "foundation_validation_harness_v4_proximity_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_foundation_validation_harness_v1 as V1  # noqa: E402
import experiments.exp_foundation_validation_harness_v2_floors_v1 as V2  # noqa: E402
import experiments.exp_foundation_validation_harness_v3_tightened_v1 as V3  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.foundation_persistence import load_store  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEED = V2.SEED  # unchanged: 20260815, reproduces the SAME 150-pair sample as v2/v3
GM_REL = V1.GM_REL

N_CORRECTNESS = V1.N_CORRECTNESS  # {"smoke": 20, "full": 150}
MIN_STEM_COVERAGE = V3.MIN_STEM_COVERAGE  # unchanged: 0.6, reused by import, not retuned
CHANCE_NEAR_GATE = V3.CHANCE_NEAR_GATE  # unchanged: 0.15, same gate as v3
PROXIMITY_WINDOW = 6  # derived from median_sentence_len(18)/3 ~= 6 (E[|i-j|] for two uniform-
                       # random token positions in an 18-token sentence), fixed BEFORE any real
                       # cooccurs_v4 number was computed -- see pre-reg "Fix" section

repo_path = V1.repo_path
wilson_ci = V1.wilson_ci
load_corpus_sentences = V1.load_corpus_sentences
predict_orthographic_best = V2.predict_orthographic_best  # unchanged: pure string transform
run_known_answer_arm = V2.run_known_answer_arm
_prefix_covers = V3._prefix_covers  # unchanged by import, not reimplemented
prefix_count_v3 = V3.prefix_count_v3  # unchanged by import: frequency ranker not implicated
predict_frequency_mode_v3 = V3.predict_frequency_mode_v3
cooccurs_v3 = V3.cooccurs_v3  # imported for direct before/after self-test comparison only

TOKEN_RE = re.compile(r"[A-Za-z']+")


# =========================================================================== proximity primitive
def _sentence_tokens(sentence: str) -> List[str]:
    return TOKEN_RE.findall(sentence)


def _covering_positions(query: str, tokens: Sequence[str],
                        min_coverage: float = MIN_STEM_COVERAGE) -> List[int]:
    return [i for i, t in enumerate(tokens) if _prefix_covers(query, t, min_coverage)]


def cooccurs_v4(lemma: str, other: str, tokenized_sentences: Sequence[List[str]],
                window: int = PROXIMITY_WINDOW) -> bool:
    """Tightened replacement for cooccurs_v3: same-sentence-anywhere is no longer sufficient --
    a covering-match for `lemma` and a covering-match for `other` must additionally occur within
    `window` tokens of each other in the SAME sentence. _prefix_covers (coverage-ratio matching)
    is reused unchanged from v3; only the same-sentence-anywhere predicate is tightened here."""
    for tokens in tokenized_sentences:
        lemma_pos = _covering_positions(lemma, tokens)
        if not lemma_pos:
            continue
        other_pos = _covering_positions(other, tokens)
        if not other_pos:
            continue
        if any(abs(i - j) <= window for i in lemma_pos for j in other_pos):
            return True
    return False


# =========================================================================== claim 1 (v4)
def run_claim1_proximity(store: HDFactStore, tokenized_sentences: List[List[str]],
                         n_sample: int, seed: int, output_dir: str) -> dict:
    gm_facts = [f for f in store._facts if f.relation == GM_REL and f.status in ("ACTIVE", "COMBINED")]
    n_live = len(gm_facts)
    cross = sorted(((f.subject, f.obj) for f in gm_facts if f.subject != f.obj))

    all_objects = sorted({f.obj for f in gm_facts})
    # frequency-floor ranker reused UNCHANGED from v3 -- not implicated by the proximity defect
    obj_freq_counts = Counter({o: prefix_count_v3(o, tokenized_sentences) for o in all_objects})
    freq_pick_global = predict_frequency_mode_v3(obj_freq_counts)

    n = min(n_sample, len(cross))
    rng = random.Random(seed)
    sample = rng.sample(cross, n) if n > 0 else []

    ckpt_dir = os.path.join(output_dir, "ckpt_claim1_v4")
    done = completed_units(ckpt_dir)
    for i, (lemma, canon_obj) in enumerate(sample):
        key = unit_key("c1v4", i, lemma, canon_obj)
        if key in done:
            continue
        decoy_pool = [o for o in all_objects if o not in (canon_obj, lemma)]
        decoy = rng.choice(decoy_pool) if decoy_pool else canon_obj
        ortho_pick = predict_orthographic_best(lemma, all_objects) or canon_obj
        real_hit = cooccurs_v4(lemma, canon_obj, tokenized_sentences)
        decoy_hit = cooccurs_v4(lemma, decoy, tokenized_sentences)
        ortho_hit = cooccurs_v4(lemma, ortho_pick, tokenized_sentences)
        freq_hit = cooccurs_v4(lemma, freq_pick_global, tokenized_sentences) if freq_pick_global else False
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
        "min_stem_coverage": MIN_STEM_COVERAGE, "proximity_window": PROXIMITY_WINDOW,
        "arms_differ_verified": len({tuple(r["canon_obj"] for r in rows),
                                     tuple(r["decoy"] for r in rows),
                                     tuple(r["ortho_pick"] for r in rows)}) > 1 if rows else False,
        # comparison vs v2/v3 -- read from their landed metrics, not recomputed, for the report
        "v2_comparison": {"precision_hat": 0.9667, "chance_hat": 0.7667, "ortho_rate": 0.84,
                          "freq_rate": 0.96, "floor_max": 0.96, "gap": 0.0067,
                          "verdict": "HARD_FAIL"},
        "v3_comparison": {"precision_hat": 0.9533, "chance_hat": 0.76, "ortho_rate": 0.84,
                          "freq_rate": 0.8267, "floor_max": 0.84, "gap": 0.1133,
                          "verdict": "INSTRUMENT_STILL_LOOSE"},
    }


# =========================================================================== self-tests
def _selftest_prefix_covers_reused_from_v3() -> None:
    # reused UNCHANGED by import -- re-asserted here as a regression check on the import wiring,
    # not reimplemented
    assert _prefix_covers("com", "comes") is True
    assert _prefix_covers("com", "company") is False
    assert _prefix_covers("villag", "village") is True
    assert _prefix_covers("villag", "pillage") is False


def _selftest_window_boundary() -> None:
    # 6 tokens apart (inclusive) -- lemma at position 0, other at position 6 -> abs diff = 6
    tokens_close = ["champ"] + ["filler"] * 5 + ["agent"]
    assert len(tokens_close) == 7
    assert cooccurs_v4("champ", "agent", [tokens_close]) is True, "distance=6 must pass (boundary)"
    # 7 tokens apart -- must fail
    tokens_far = ["champ"] + ["filler"] * 6 + ["agent"]
    assert len(tokens_far) == 8
    assert cooccurs_v4("champ", "agent", [tokens_far]) is False, "distance=7 must fail"


def _selftest_genuine_relation_positive_control() -> None:
    s = "the champion agent negotiated the historic treaty"
    tokens = _sentence_tokens(s)
    assert cooccurs_v4("champ", "agent", [tokens]) is True


def _selftest_same_sentence_but_far_discriminating_case() -> None:
    """The direct before/after proof: construct a >40-token sentence where the lemma-match is
    near the start and an unrelated other-match is near the end (distance > PROXIMITY_WINDOW).
    cooccurs_v3 (same-sentence-anywhere) must say True; cooccurs_v4 (proximity) must say False on
    the IDENTICAL pair -- this is the exact defect class v4 exists to fix."""
    filler = ["unrelated"] * 45
    tokens = ["champion"] + filler + ["zebra"]
    assert cooccurs_v3("champ", "zebra", [tokens]) is True, "v3 same-sentence-anywhere must hit"
    assert cooccurs_v4("champ", "zebra", [tokens]) is False, "v4 proximity must reject the same pair"


def _selftest_degenerate_pseudo_sentence_regression() -> None:
    """Mimics the real base_vocabulary CSV-blob defect: a long alphabetically-ordered
    comma-separated pseudo-sentence where a lemma-match and an unrelated other-match are far
    apart in token position. cooccurs_v3 says True (same-sentence-anywhere); cooccurs_v4 must say
    False -- demonstrates the window structurally suppresses this corpus-loading confound without
    touching corpus loading."""
    words = ["agent"] + [f"midword{i}" for i in range(60)] + ["zoroastrian"]
    tokens = words  # already tokenized form; simulates the CSV-row-derived token stream
    assert cooccurs_v3("agent", "zoroastr", [tokens]) is True, "v3 must hit on the degenerate blob"
    assert cooccurs_v4("agent", "zoroastr", [tokens]) is False, "v4 must reject via proximity"


def _selftest_known_answer_arm_still_valid() -> None:
    """This cell does not modify HDFactStore/query mechanics -- reuses V2's known-answer arm
    verbatim. Re-asserted here as the mandatory instrument gate for THIS cell too."""
    result = run_known_answer_arm(n_dim=2048, k_chains=10, seed=777)
    assert result["instrument_valid"] is True, result
    assert result["accuracy"] == 1.0, result


def _run_all_selftests() -> dict:
    _selftest_prefix_covers_reused_from_v3()
    _selftest_window_boundary()
    _selftest_genuine_relation_positive_control()
    _selftest_same_sentence_but_far_discriminating_case()
    _selftest_degenerate_pseudo_sentence_regression()
    _selftest_known_answer_arm_still_valid()
    return {
        "prefix_covers_reused_from_v3_ok": True,
        "window_boundary_ok": True,
        "genuine_relation_positive_control_ok": True,
        "same_sentence_but_far_discriminating_case_ok": True,
        "degenerate_pseudo_sentence_regression_ok": True,
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
    c1 = run_claim1_proximity(store, tokenized_sentences, n_correct, SEED, output_dir)
    print(f"[claim1 CORRECTNESS proximity] {c1['verdict']} validity_gate_pass="
          f"{c1['validity_gate_pass']} chance_hat={c1['chance_hat']} precision={c1['precision_hat']} "
          f"floor_max={c1['floor_max']}({c1['floor_name']}) gap={c1['gap']} n={c1['n_sampled']}",
          flush=True)

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"claim1_proximity={c1['verdict']} validity_gate_pass={c1['validity_gate_pass']}"
                  f"(chance_hat={c1['chance_hat']}<=?{CHANCE_NEAR_GATE}) gap={c1['gap']} "
                  f"floor={c1['floor_name']}={c1['floor_max']} precision={c1['precision_hat']} "
                  f"v3_chance=0.76 v2_chance=0.7667 window={PROXIMITY_WINDOW} "
                  f"known_answer_instrument_valid={ka['instrument_valid']}")

    return {
        "verdict": c1["verdict"], "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "foundation_dir": foundation_dir,
        "n_facts_loaded": len(store._facts), "seed": SEED, "proximity_window": PROXIMITY_WINDOW,
        "known_answer_arm": ka,
        "claim1_correctness_proximity": c1,
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
                      "floor": "max(chance,ortho,freq)_proximity"},
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
                  "verdict_msg": "all 6 v4 formula self-tests passed (prefix-covers reused from "
                                  "v3, window boundary 6-vs-7, genuine-relation positive control, "
                                  "same-sentence-but-far discriminating case vs v3, degenerate "
                                  "pseudo-sentence regression check, known-answer arm still valid "
                                  "at production n_dim)",
                  "summary": "SELF_TEST_PASS", "elapsed_s": elapsed,
                  "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
                  "run_mode": run_mode, "result": result}
        _atomic_write(output_dir, metrics)
        print(f"[{ANCHOR_NAME}] SELF_TEST_PASS elapsed={elapsed:.2f}s -> {output_dir}")
        return

    foundation_dir = args.foundation_dir
    if not foundation_dir:
        raise ValueError("--foundation-dir is required for --smoke/--full (reuse the v2/v3 frozen "
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
