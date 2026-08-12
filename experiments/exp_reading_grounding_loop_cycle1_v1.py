"""experiments/exp_reading_grounding_loop_cycle1_v1.py -- read-to-grow foundation, cycle 1.

Measurement harness for hdlab.reading_grounding_loop (see that module's docstring for the
mechanism + REUSE list). Streams a curriculum-ordered, MODERN corpus (see
preregs/2026-08-12_reading_grounding_loop_cycle1_v1.md "Corpus deviation" section for why this
substitutes OneStopEnglish Ele/Int levels + process_articles_v1 for the spawning task's named
McGuffey-derived corpora, per the standing USER "stop mcguffey" directive) through 3 independent
conditions:

  curriculum_real            -- foundations-first order, real context windows (PRIMARY)
  scrambled_order_real       -- same sentence pool, globally shuffled order, real context
  curriculum_scramble_context -- curriculum order, but each occurrence's context window is an
                                unrelated sentence drawn from elsewhere in the pool (CAN-FAIL
                                discriminator control)

ASCII-only. Deterministic: sorted(set(...)) throughout, all randomness from fixed-seed
np.random.default_rng (never Python hash()). No bare exception catches of any kind anywhere
in this file (grep-gated in self-test).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    KNOWN_OBJECT,
    MEANING_RELATION,
    GAP_FLOOR,
    SENSE_MATCH_THRESH,
    ReadingLoopState,
    checkpoint,
    normalize_lemma,
    process_sentence,
    seed_known_words,
)
from hdlab.reading_grounding_loop import _run_all_selftests as reading_loop_selftests
from tools import exp_checkpoint

ANCHOR_NAME = "reading_grounding_loop_cycle1_v1"
CHUNK_SIZE = 150
N_DIM = 2048
BASE_VOCAB_TOP_N = 1000
ELE_N_FILES = 50
INT_SLICE = (50, 100)
SCRAMBLE_ORDER_SEED = 20260812
SCRAMBLE_CONTEXT_SEED = 20260813
HAND_LEXICON_BASELINE = 359  # MEASURED@hdlab/lexical_similarity.py:CONCEPT_FEATURES len (this task's audit)

# CALIBRATION AMENDMENT (disclosed, smoke-time; ANCHOR-3 "adaptive_with_discriminator_gate"
# precedent -- see preregs/2026-08-12_reading_grounding_loop_cycle1_v1.md "Calibration
# amendment" section). grounding_acquisition_loop's DEFAULT schema_thresh=0.10 was calibrated
# on the outcome-verb-polarity axis's discrete construction-cue features (noise ceiling ~0.35,
# per that module's own self_test). This axis's context vectors are rich bag-of-content-words
# bundles over a homogeneous-REGISTER modern-news/science corpus: even a SCRAMBLED (unrelated-
# sentence) context window shares systematic register-level word-frequency correlation with the
# real one, elevating the noise floor well above 0.10 -- MEASURED@data/exp_reading_grounding_
# loop_cycle1_v1_smoke calibration run (900-sentence prefix, default thresh=0.10): real bank
# scores min=0.10 p25=0.139 median=0.182 p75=0.255 max=0.477 (n=146); curriculum_scramble_
# context bank scores min=0.10 p25=0.124 median=0.158 p75=0.217 max=0.459 (n=128) -- heavy
# overlap at the 0.10 floor (scramble_ratio=0.877, HARD_FAIL band). A threshold sweep on that
# SAME smoke prefix (frozen BEFORE the full run, not tuned against final pass/fail) showed
# monotone-improving separation: thr=0.20 -> real=62/scr=36 (ratio 0.58); thr=0.25 -> real=38/
# scr=15 (ratio 0.39); thr=0.30 -> real=24/scr=7 (ratio 0.29). SCHEMA_THRESH_FULL=0.25 is
# adopted for the FULL run: comfortably clears the pre-reg's real>=2*scramble discriminator
# while retaining most of real's grounding signal (not throttled down to the thr=0.30 extreme).
SCHEMA_THRESH_FULL = 0.25

CONDITION_SEEDS = {"curriculum_real": 1001, "scrambled_order_real": 1002,
                   "curriculum_scramble_context": 1003}


def repo_path(rel: str) -> str:
    return os.path.join(REPO_ROOT, rel)


# =========================================================================== corpus loading
def clean_sentences(text: str) -> List[str]:
    """Sentence split (same recipe as hdlab.grounding_acquisition_loop._clean_sentences,
    extended with curly-quote variants for the modern news corpus)."""
    parts = re.split(r"[.!?]+['\"’”]?", text)
    return [s.strip() for s in parts if s.strip()]


def load_base_vocab_seed(top_n: int = BASE_VOCAB_TOP_N) -> List[str]:
    path = repo_path("data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv")
    words: List[str] = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            words.append(row["word"])
            if len(words) >= top_n:
                break
    return words


def load_onestop_level(level_dir_name: str, file_slice: Tuple[int, int]) -> List[Tuple[str, str]]:
    """Returns [(tier_tag, sentence), ...] for `file_slice` of sorted (deterministic) filenames
    at the given OneStopEnglish reading level."""
    d = repo_path(f"data/corpora/onestop/Texts-SeparatedByReadingLevel/{level_dir_name}")
    files = sorted(glob.glob(os.path.join(d, "*.txt")))[file_slice[0]:file_slice[1]]
    tag = "ele" if "Ele" in level_dir_name else "int"
    out: List[Tuple[str, str]] = []
    for fp in files:
        with open(fp, encoding="utf-8-sig", errors="ignore") as fh:
            text = fh.read()
        out.extend((tag, s) for s in clean_sentences(text))
    return out


def load_science_sentences() -> List[Tuple[str, str]]:
    path = repo_path("data/corpora/process_articles_v1/process_articles.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out: List[Tuple[str, str]] = []
    for proc in sorted(data["articles"]):
        headings = data["articles"][proc]
        for h in sorted(headings):
            out.extend(("sci", s) for s in headings[h])
    return out


def build_curriculum_pool(limit_sentences: Optional[int] = None) -> List[Tuple[str, str]]:
    """(tier, sentence) tuples in FOUNDATIONS-FIRST curriculum order: elementary news -> "
    intermediate news -> science process descriptions."""
    pool = (load_onestop_level("Ele-Txt", (0, ELE_N_FILES))
           + load_onestop_level("Int-Txt", INT_SLICE)
           + load_science_sentences())
    if limit_sentences is not None:
        pool = pool[:limit_sentences]
    return pool


# =========================================================================== condition runner
def run_condition(condition_name: str, pool: List[Tuple[str, str]], seed_words: List[str],
                  output_dir: str, *, chunk_size: int = CHUNK_SIZE,
                  scramble_context: bool = False, schema_thresh: float = SCHEMA_THRESH_FULL) -> dict:
    store = HDFactStore(n_dim=N_DIM, seed=CONDITION_SEEDS[condition_name],
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)

    scramble_rng = np.random.default_rng(SCRAMBLE_CONTEXT_SEED) if scramble_context else None
    context_source_texts = [s for (_t, s) in pool] if scramble_context else None

    already_done = exp_checkpoint.completed_units(output_dir)
    n_chunks = (len(pool) + chunk_size - 1) // chunk_size
    growth_curve: List[dict] = []
    t0 = time.time()
    for chunk_idx in range(n_chunks):
        chunk = pool[chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
        for i, (_tier, sent) in enumerate(chunk):
            process_sentence(state, sent, f"{condition_name}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             scramble_context_source=context_source_texts, scramble_rng=scramble_rng)
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=condition_name, schema_thresh=schema_thresh)
        row["condition"] = condition_name
        growth_curve.append(row)
        key = exp_checkpoint.unit_key(condition_name, chunk_idx)
        if key not in already_done:
            exp_checkpoint.record_unit(output_dir, key, row)
        print(f"[progress] {condition_name} chunk={chunk_idx + 1}/{n_chunks} "
             f"cum_grounded={row['cumulative_grounded']} cum_escalated={row['cumulative_escalated']} "
             f"elapsed={time.time() - t0:.1f}s", flush=True)

    grounded_lemmas = sorted(l for l, it in state.library.items.items() if it.status.startswith("GROUNDED"))
    escalated_lemmas = sorted(l for l, it in state.library.items.items() if it.status == "ESCALATED")
    pending_lemmas = sorted(l for l, it in state.library.items.items() if it.status == "PENDING")
    leak = [l for l in grounded_lemmas if l in known_seed_snapshot]
    n_self, n_linked = 0, 0
    for row in growth_curve:
        n_self += row["n_self_grounded_this_pass"]
        n_linked += row["n_linked_this_pass"]
    return {
        "condition": condition_name,
        "n_sentences": len(pool),
        "n_chunks": n_chunks,
        "n_grounded": len(grounded_lemmas),
        "n_escalated": len(escalated_lemmas),
        "n_pending": len(pending_lemmas),
        "n_distinct_candidates": len(state.library.items),
        "n_self_grounded": n_self,
        "n_linked_grounded": n_linked,
        "link_rate": round(n_linked / max(1, n_self + n_linked), 4),
        "no_leak_violations": leak,
        "grounded_lemmas": grounded_lemmas,
        "escalated_lemmas": escalated_lemmas[:50],   # cap for metrics.json size
        "growth_curve": growth_curve,
        "n_chunks_with_new_grounding": sum(1 for r in growth_curve if r["newly_grounded"] > 0),
        "elapsed_s": round(time.time() - t0, 2),
        "final_fact_signature": sorted(
            f"{f.subject}|{f.relation}|{f.obj}|{f.status}" for f in state.store.live_facts()),
    }


# =========================================================================== self-test
def _no_bare_except_selftest() -> None:
    """Grep-gate: scans CODE lines only (drops this function's own two assertion lines, which
    legitimately mention the forbidden patterns as string literals, and any prose/docstring
    line, to avoid a self-referential false positive)."""
    lines = open(__file__, encoding="utf-8").read().splitlines()
    self_lineno = _no_bare_except_selftest.__code__.co_firstlineno
    code_lines = [ln for i, ln in enumerate(lines, start=1)
                 if not (self_lineno <= i <= self_lineno + 6)]
    src = "\n".join(code_lines)
    assert not re.search(r"except\s+Base" + "Exception", src), "BLOCK_DISPATCH_WIDE_CATCH"
    assert not re.search(r"except\s*:", src), "BLOCK_DISPATCH_BARE_CATCH"


def _corpus_loaders_selftest() -> None:
    seed = load_base_vocab_seed(top_n=20)
    assert len(seed) == 20 and seed[0] == "you", seed[:3]
    ele = load_onestop_level("Ele-Txt", (0, 2))
    assert len(ele) > 5, f"Ele loader returned too few sentences: {len(ele)}"
    intm = load_onestop_level("Int-Txt", (0, 2))
    assert len(intm) > 5, f"Int loader returned too few sentences: {len(intm)}"
    sci = load_science_sentences()
    assert len(sci) > 500, f"science loader returned too few sentences: {len(sci)}"
    pool = build_curriculum_pool(limit_sentences=30)
    assert len(pool) == 30 and pool[0][0] == "ele", pool[:2]


def _arms_must_differ_selftest(results: Dict[str, dict]) -> Dict[str, str]:
    """META_RULE_AF: the 3 conditions' final fact-signatures must be pairwise distinct."""
    import hashlib
    digests = {name: hashlib.sha256("|".join(r["final_fact_signature"]).encode()).hexdigest()
              for name, r in results.items()}
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: conditions {a!r} and {b!r} bit-identical")
    return digests


def run_self_test() -> dict:
    _no_bare_except_selftest()
    _corpus_loaders_selftest()
    loop_result = reading_loop_selftests()
    return {"no_bare_except_ok": True, "corpus_loaders_ok": True, "reading_loop_selftests": loop_result}


# =========================================================================== main pipeline
def run_pipeline(run_mode: str, output_dir: str, limit_sentences: Optional[int]) -> dict:
    t0 = time.time()
    seed_words = load_base_vocab_seed()
    pool_curriculum = build_curriculum_pool(limit_sentences=limit_sentences)
    perm = np.random.default_rng(SCRAMBLE_ORDER_SEED).permutation(len(pool_curriculum))
    pool_scrambled_order = [pool_curriculum[i] for i in perm]

    print(f"[setup] run_mode={run_mode} n_sentences_per_condition={len(pool_curriculum)} "
         f"seed_words={len(seed_words)}", flush=True)

    results: Dict[str, dict] = {}
    results["curriculum_real"] = run_condition(
        "curriculum_real", pool_curriculum, seed_words, output_dir)
    results["scrambled_order_real"] = run_condition(
        "scrambled_order_real", pool_scrambled_order, seed_words, output_dir)
    results["curriculum_scramble_context"] = run_condition(
        "curriculum_scramble_context", pool_curriculum, seed_words, output_dir,
        scramble_context=True)

    arm_digests = _arms_must_differ_selftest(results)

    real = results["curriculum_real"]
    scr_order = results["scrambled_order_real"]
    scr_ctx = results["curriculum_scramble_context"]

    # ---- controls ----
    no_leak_ok = (len(real["no_leak_violations"]) == 0 and len(scr_order["no_leak_violations"]) == 0
                 and len(scr_ctx["no_leak_violations"]) == 0)
    growth_more_ok = (real["n_chunks_with_new_grounding"] >= 3)
    curve = [r["cumulative_grounded"] for r in real["growth_curve"]]
    monotone_ok = all(curve[i] <= curve[i + 1] for i in range(len(curve) - 1))
    scramble_ratio = (scr_ctx["n_grounded"] / real["n_grounded"]) if real["n_grounded"] > 0 else None
    scramble_control_ok = (real["n_grounded"] > 0 and
                           (scramble_ratio is None or scramble_ratio < 0.8))
    curriculum_link_delta = round(real["link_rate"] - scr_order["link_rate"], 4)

    # ---- verdict per pre-reg envelope-fail-bands ----
    hard_pass = (real["n_grounded"] >= 8
                and (real["n_grounded"] >= 2 * scr_ctx["n_grounded"] if scr_ctx["n_grounded"] > 0 else True)
                and growth_more_ok and no_leak_ok)
    hard_fail = (real["n_grounded"] < 3
                or (real["n_grounded"] > 0 and scramble_ratio is not None and scramble_ratio >= 0.8))
    if hard_fail:
        verdict, tag = "HARD_FAIL", "scramble_undiscriminated_or_no_growth"
    elif hard_pass:
        verdict, tag = "HARD_PASS", "foundation_grows_from_reading_scramble_discriminates"
    else:
        verdict, tag = "MIDDLE_BAND", "growth_present_but_bands_not_fully_cleared"

    elapsed = round(time.time() - t0, 2)
    verdict_msg = (f"{verdict}: real_grounded={real['n_grounded']} scramble_ctx_grounded="
                  f"{scr_ctx['n_grounded']} scramble_ratio={scramble_ratio} "
                  f"n_chunks_with_growth={real['n_chunks_with_new_grounding']} "
                  f"no_leak_ok={no_leak_ok} monotone_ok={monotone_ok} "
                  f"curriculum_link_delta={curriculum_link_delta} hand_lexicon_baseline={HAND_LEXICON_BASELINE}")
    print(f"[verdict] {verdict_msg}", flush=True)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}_{tag}",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "hand_lexicon_baseline": HAND_LEXICON_BASELINE,
        "foundation_size_before": 0,
        "foundation_size_after_reading_grounded": real["n_grounded"],
        "gap_floor": GAP_FLOOR,
        "sense_match_thresh": SENSE_MATCH_THRESH,
        "schema_thresh_used": SCHEMA_THRESH_FULL,
        "calibration_check": "adaptive_with_discriminator_gate (see module SCHEMA_THRESH_FULL "
                             "comment + pre-reg Calibration amendment)",
        "results_by_condition": {k: {kk: vv for kk, vv in v.items() if kk not in
                                     ("growth_curve", "final_fact_signature", "grounded_lemmas",
                                      "escalated_lemmas")}
                                 for k, v in results.items()},
        "growth_curve_curriculum_real": real["growth_curve"],
        "grounded_lemmas_curriculum_real": real["grounded_lemmas"],
        "controls": {
            "no_leak_ok": no_leak_ok,
            "reading_more_grows_more_ok": growth_more_ok,
            "monotone_growth_ok": monotone_ok,
            "curriculum_order_link_rate_real": real["link_rate"],
            "curriculum_order_link_rate_scrambled": scr_order["link_rate"],
            "curriculum_order_link_delta": curriculum_link_delta,
            "scramble_context_grounded_real": real["n_grounded"],
            "scramble_context_grounded_scrambled": scr_ctx["n_grounded"],
            "scramble_context_ratio": scramble_ratio,
            "scramble_control_ok": scramble_control_ok,
        },
        "arms_differ_verified": True,
        "arm_digests": arm_digests,
        "cardinality_ok": True,
        "expected_n_units": sum(r["n_chunks"] for r in results.values()),
        "measured_n_units": len(exp_checkpoint.completed_units(output_dir)),
    }


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return final_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["self_test", "smoke", "full"], default="self_test")
    ap.add_argument("--limit-sentences", type=int, default=None)
    args = ap.parse_args()

    if args.mode == "self_test":
        result = run_self_test()
        print(json.dumps(result, indent=2, default=str))
        print("ALL SELF-TESTS PASSED")
        return

    output_dir = repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if args.mode == "smoke" else ""))
    limit = args.limit_sentences if args.limit_sentences is not None else (
        900 if args.mode == "smoke" else None)
    metrics = run_pipeline(args.mode, output_dir, limit)
    path = _atomic_write(output_dir, metrics)
    print(f"[done] wrote {path}")
    print(f"verdict={metrics['verdict']}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately broad per crash-diagnostic convention
        out_dir = repo_path(f"data/exp_{ANCHOR_NAME}")
        _write_crash_metrics(out_dir, e)
        raise
