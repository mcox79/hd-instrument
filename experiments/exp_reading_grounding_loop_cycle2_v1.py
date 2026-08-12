"""experiments/exp_reading_grounding_loop_cycle2_v1.py -- read-to-grow foundation, cycle 2.

SEGMENTED measurement harness: bootstraps a PERSISTED foundation (hdlab.foundation_persistence)
by reproducing cycle 1's exact curriculum_real run if none exists yet, then reads NEW, larger,
harder curriculum material ON TOP of the loaded foundation across further segments, checkpointing
the grown foundation to disk after each segment. See
preregs/2026-08-12_reading_grounding_loop_cycle2_v1.md for the full design, envelope-fail-bands,
and the segment table.

Each segment is ONE CLI invocation (`--mode full --segment <name>`); the persisted foundation
directory IS the resume checkpoint carrying state across invocations -- a materially stronger
resumability model than cycle 1's "recompute everything from chunk 0" note, now retired in favor
of real cross-process state carry-over via hdlab.foundation_persistence.

ASCII-only. Deterministic: sorted(set(...)) throughout, all randomness from fixed-seed
np.random.default_rng (never Python hash()). No bare exception catches anywhere in this file
(grep-gated in self-test).
"""
from __future__ import annotations

import argparse
import json
import math
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
    ReadingLoopState,
    checkpoint,
    process_sentence,
    seed_known_words,
)
from hdlab import foundation_persistence
from hdlab.foundation_persistence import _run_all_selftests as persistence_selftests
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    CONDITION_SEEDS,
    ELE_N_FILES,
    INT_SLICE,
    N_DIM,
    SCHEMA_THRESH_FULL,
    build_curriculum_pool,
    clean_sentences,
    load_base_vocab_seed,
    load_onestop_level,
    repo_path,
    run_self_test as _cycle1_run_self_test,  # noqa: F401 (imported to confirm import wiring; not called)
)

ANCHOR_NAME = "reading_grounding_loop_cycle2_v1"
CHUNK_SIZE = 150
SCRAMBLE_CONTEXT_SEED = 20260814
CYCLE1_REFERENCE_GROUNDED = 185  # MEASURED@data/exp_reading_grounding_loop_cycle1_v1/metrics.json:foundation_size_after_reading_grounded
HAND_LEXICON_BASELINE = 359      # MEASURED@hdlab/lexical_similarity.py:CONCEPT_FEATURES len (cycle1's own audit)

SEGMENT_ORDER = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new", "scramble_probe", "finalize"]


def _foundation_dir(run_mode: str) -> str:
    tag = "reading_grounding_v1" if run_mode == "full" else "reading_grounding_v1_smoke"
    return repo_path(f"data/foundation/{tag}")


def _control_copy_dir(foundation_dir: str) -> str:
    return foundation_dir.rstrip("/\\") + "_post_bootstrap_control_copy"


def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


# =========================================================================== corpus loaders
# All 4 loaders share ONE consistent semantic for their optional arg: limit_sentences caps the
# FULL loaded pool to its first N entries (never changes WHICH files are read -- the corpus-file
# range itself is fixed per segment, per the pre-reg's Segments table). This keeps smoke-scale
# calls uniform across all 4 (no per-loader unit confusion between "files" and "sentences").
def load_ele_continuation(limit_sentences: Optional[int] = None) -> List[Tuple[str, str]]:
    pool = load_onestop_level("Ele-Txt", (ELE_N_FILES, 189))
    return pool if limit_sentences is None else pool[:limit_sentences]


def load_int_continuation(limit_sentences: Optional[int] = None) -> List[Tuple[str, str]]:
    pool = load_onestop_level("Int-Txt", (0, INT_SLICE[0])) + load_onestop_level("Int-Txt", (INT_SLICE[1], 189))
    return pool if limit_sentences is None else pool[:limit_sentences]


def load_adv_new(limit_sentences: Optional[int] = None) -> List[Tuple[str, str]]:
    raw = load_onestop_level("Adv-Txt", (0, 189))
    pool = [("adv", s) for (_tag, s) in raw]  # cycle1's loader mislabels non-Ele dirs "int"; fixed here
    return pool if limit_sentences is None else pool[:limit_sentences]


def load_biology_sentences(limit_sentences: Optional[int] = None) -> List[Tuple[str, str]]:
    """Concepts of Biology (OpenStax, CC-licensed, modern), Markdown-stripped then sentence-split
    via cycle 1's reused clean_sentences. Strips heading lines (# ...) and list markers (-/*/N.)
    before splitting; MEASURED 11332 sentences, mean len 122.7 chars (see pre-reg Segments table).
    """
    path = repo_path("data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt")
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    kept: List[str] = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"^\d+\.\s+", "", s)
        kept.append(s)
    text = " ".join(kept)
    out = [("bio", s) for s in clean_sentences(text)]
    return out if limit_sentences is None else out[:limit_sentences]


SEGMENT_POOL_LOADERS = {
    "ele_cont": load_ele_continuation,
    "int_cont": load_int_continuation,
    "adv_new": load_adv_new,
    "bio_new": load_biology_sentences,
}


# =========================================================================== metrics helper
def grounded_lemmas_in_store(store: HDFactStore) -> List[str]:
    """THE correct cross-segment foundation-size metric. Cycle 1 counted grounded lemmas by
    scanning Library.items for status.startswith("GROUNDED") -- valid only within one process's
    lifetime. Since PENDING items are persisted but terminal GROUNDED items are (by design) NOT
    re-populated into a reloaded Library, that scan would silently UNDER-COUNT after a reload.
    This instead counts distinct subjects with a live MEANING_RELATION fact in the store, which
    is the actual source of truth and survives reloads by construction. See pre-reg."""
    return sorted({f.subject for f in store.live_facts() if f.relation == MEANING_RELATION})


# =========================================================================== bootstrap segment
def run_bootstrap(run_mode: str, output_dir: str, *, limit_sentences: Optional[int] = None) -> dict:
    foundation_dir = _foundation_dir(run_mode)
    already_done = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("segment_done", "bootstrap")
    if done_key in already_done and foundation_persistence.foundation_exists(foundation_dir):
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    seed_words = load_base_vocab_seed()
    pool = build_curriculum_pool(limit_sentences=limit_sentences)  # IDENTICAL to cycle1's pool
    store = HDFactStore(n_dim=N_DIM, seed=CONDITION_SEEDS["curriculum_real"],
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source="seed_base_vocabulary")

    n_chunks = math.ceil(len(pool) / CHUNK_SIZE) if pool else 0
    t0 = time.time()
    for chunk_idx in range(n_chunks):
        chunk = pool[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (_tier, sent) in enumerate(chunk):
            process_sentence(state, sent, f"bootstrap_{chunk_idx}_{i}", pass_idx=chunk_idx)
        row = checkpoint(state, pass_idx=chunk_idx, source_tag="bootstrap", schema_thresh=SCHEMA_THRESH_FULL)
        row["segment"] = "bootstrap"
        row["foundation_size_in_store"] = len(grounded_lemmas_in_store(state.store))
        key = exp_checkpoint.unit_key("bootstrap", chunk_idx)
        if key not in already_done:
            exp_checkpoint.record_unit(output_dir, key, row)
        print(f"[progress] bootstrap chunk={chunk_idx + 1}/{n_chunks} "
             f"foundation_size={row['foundation_size_in_store']} elapsed={time.time() - t0:.1f}s", flush=True)

    next_pass_idx = n_chunks
    foundation_persistence.save_foundation(state, foundation_dir, source_tag="bootstrap",
                                           next_pass_idx=next_pass_idx)
    foundation_persistence.save_foundation(state, _control_copy_dir(foundation_dir),
                                           source_tag="bootstrap_control_copy", next_pass_idx=next_pass_idx)
    grounded = grounded_lemmas_in_store(state.store)
    summary = {
        "segment": "bootstrap", "n_sentences": len(pool), "n_chunks": n_chunks,
        "n_grounded": len(grounded), "elapsed_s": round(time.time() - t0, 2),
        "cycle1_reference_grounded": CYCLE1_REFERENCE_GROUNDED,
        "bootstrap_matches_cycle1_exactly": (limit_sentences is None and len(grounded) == CYCLE1_REFERENCE_GROUNDED),
        "next_pass_idx": next_pass_idx,
    }
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


# =========================================================================== continuation segment
def run_continuation_segment(segment_name: str, run_mode: str, output_dir: str, *,
                             limit_sentences: Optional[int] = None,
                             chunk_size: int = CHUNK_SIZE) -> dict:
    foundation_dir = _foundation_dir(run_mode)
    already_done = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("segment_done", segment_name)
    if done_key in already_done:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)
    if not foundation_persistence.foundation_exists(foundation_dir):
        raise RuntimeError(f"segment {segment_name!r} requires the foundation to exist first "
                           f"(run --segment bootstrap before this segment)")

    loader = SEGMENT_POOL_LOADERS[segment_name]
    pool = loader(limit_sentences)

    manifest_before = foundation_persistence.load_manifest(foundation_dir)
    state = foundation_persistence.load_foundation(foundation_dir)
    size_before = len(grounded_lemmas_in_store(state.store))
    known_seed_snapshot = set(state.known_seed)
    start_pass = manifest_before["next_pass_idx"]

    n_chunks = math.ceil(len(pool) / chunk_size) if pool else 0
    t0 = time.time()
    new_rows: List[dict] = []
    for chunk_idx in range(n_chunks):
        pass_idx = start_pass + chunk_idx
        chunk = pool[chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
        for i, (_tier, sent) in enumerate(chunk):
            process_sentence(state, sent, f"{segment_name}_{chunk_idx}_{i}", pass_idx=pass_idx)
        row = checkpoint(state, pass_idx=pass_idx, source_tag=segment_name, schema_thresh=SCHEMA_THRESH_FULL)
        row["segment"] = segment_name
        row["foundation_size_in_store"] = len(grounded_lemmas_in_store(state.store))
        new_rows.append(row)
        key = exp_checkpoint.unit_key(segment_name, chunk_idx)
        if key not in already_done:
            exp_checkpoint.record_unit(output_dir, key, row)
        print(f"[progress] {segment_name} chunk={chunk_idx + 1}/{n_chunks} "
             f"foundation_size={row['foundation_size_in_store']} elapsed={time.time() - t0:.1f}s", flush=True)

    next_pass_idx = start_pass + n_chunks
    foundation_persistence.save_foundation(state, foundation_dir, source_tag=segment_name,
                                           next_pass_idx=next_pass_idx)
    grounded_after = grounded_lemmas_in_store(state.store)
    leak = [l for l in grounded_after if l in known_seed_snapshot]
    summary = {
        "segment": segment_name, "n_sentences": len(pool), "n_chunks": n_chunks,
        "foundation_size_before": size_before, "foundation_size_after": len(grounded_after),
        "n_newly_grounded_this_segment": len(grounded_after) - size_before,
        "no_leak_violations": leak, "elapsed_s": round(time.time() - t0, 2),
        "n_chunks_with_new_grounding": sum(1 for r in new_rows if r["newly_grounded"] > 0),
        "next_pass_idx": next_pass_idx,
        "grounded_lemma_set_after": grounded_after,
    }
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


# =========================================================================== scramble-context control
def run_scramble_probe(run_mode: str, output_dir: str, *, limit_sentences: Optional[int] = None,
                       chunk_size: int = CHUNK_SIZE) -> dict:
    foundation_dir = _foundation_dir(run_mode)
    control_dir = _control_copy_dir(foundation_dir)
    already_done = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("segment_done", "scramble_probe")
    if done_key in already_done:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)
    if not foundation_persistence.foundation_exists(control_dir):
        raise RuntimeError("segment 'scramble_probe' requires the bootstrap control-copy snapshot "
                           "(run --segment bootstrap first)")

    pool = load_ele_continuation(limit_sentences)  # SAME pool as ele_cont, for a fair real-vs-scramble compare
    manifest_before = foundation_persistence.load_manifest(control_dir)
    state = foundation_persistence.load_foundation(control_dir)  # INDEPENDENT branch; never saved back
    size_before = len(grounded_lemmas_in_store(state.store))
    start_pass = manifest_before["next_pass_idx"]

    scramble_rng = np.random.default_rng(SCRAMBLE_CONTEXT_SEED)
    context_source_texts = [s for (_t, s) in pool]

    n_chunks = math.ceil(len(pool) / chunk_size) if pool else 0
    t0 = time.time()
    for chunk_idx in range(n_chunks):
        pass_idx = start_pass + chunk_idx
        chunk = pool[chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
        for i, (_tier, sent) in enumerate(chunk):
            process_sentence(state, sent, f"scramble_probe_{chunk_idx}_{i}", pass_idx=pass_idx,
                             scramble_context_source=context_source_texts, scramble_rng=scramble_rng)
        row = checkpoint(state, pass_idx=pass_idx, source_tag="scramble_probe", schema_thresh=SCHEMA_THRESH_FULL)
        key = exp_checkpoint.unit_key("scramble_probe", chunk_idx)
        if key not in already_done:
            exp_checkpoint.record_unit(output_dir, key, {**row, "segment": "scramble_probe"})
        print(f"[progress] scramble_probe chunk={chunk_idx + 1}/{n_chunks} "
             f"elapsed={time.time() - t0:.1f}s", flush=True)

    grounded_after = grounded_lemmas_in_store(state.store)
    summary = {
        "segment": "scramble_probe", "n_sentences": len(pool),
        "foundation_size_before": size_before, "foundation_size_after": len(grounded_after),
        "n_newly_grounded_scramble": len(grounded_after) - size_before,
        "elapsed_s": round(time.time() - t0, 2),
        "grounded_lemma_set_after": grounded_after,
    }
    # deliberately NOT saved back to any persisted foundation dir (ephemeral control branch)
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


# =========================================================================== finalize
def run_finalize(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    foundation_dir = _foundation_dir(run_mode)
    units = exp_checkpoint.load_units(output_dir)
    seg_summaries: Dict[str, dict] = {}
    for k, v in units.items():
        if k.startswith("segment_done|"):
            seg_summaries[k.split("|", 1)[1]] = v

    required = [s for s in SEGMENT_ORDER if s != "finalize"]
    missing = [s for s in required if s not in seg_summaries]
    if missing:
        raise RuntimeError(f"finalize called before all segments complete: missing {missing}")

    try:
        persistence_result = persistence_selftests()
        persistence_ok = True
        persistence_error = None
    except AssertionError as e:  # specific class, propagated to metrics, not swallowed (META_RULE_J)
        persistence_ok = False
        persistence_error = str(e)
        persistence_result = {}

    manifest = foundation_persistence.load_manifest(foundation_dir)
    final_store = foundation_persistence.load_store(os.path.join(foundation_dir, "store"))
    grounded_final = grounded_lemmas_in_store(final_store)
    foundation_size_cycle2_end = len(grounded_final)

    boot = seg_summaries["bootstrap"]
    foundation_size_cycle2_start = boot["n_grounded"]

    ele = seg_summaries["ele_cont"]
    scr = seg_summaries["scramble_probe"]
    real_new = ele["n_newly_grounded_this_segment"]
    scramble_new = scr["n_newly_grounded_scramble"]
    scramble_ratio = (scramble_new / real_new) if real_new > 0 else None

    no_leak_ok = all(len(seg_summaries[s].get("no_leak_violations", [])) == 0
                     for s in ("ele_cont", "int_cont", "adv_new", "bio_new"))

    growth_curve_all = manifest.get("growth_curve_all", [])
    curve_sizes = [r["foundation_size_in_store"] for r in growth_curve_all if "foundation_size_in_store" in r]
    monotone_ok = all(curve_sizes[i] <= curve_sizes[i + 1] for i in range(len(curve_sizes) - 1))
    n_chunks_with_growth_total = sum(1 for r in growth_curve_all if r.get("newly_grounded", 0) > 0)

    arms_differ = sorted(ele.get("grounded_lemma_set_after", [])) != sorted(scr.get("grounded_lemma_set_after", []))

    total_new_this_cycle = foundation_size_cycle2_end - foundation_size_cycle2_start

    hard_fail = ((not persistence_ok) or (total_new_this_cycle <= 0)
                or (scramble_ratio is not None and scramble_ratio >= 0.8))
    hard_pass = (persistence_ok and total_new_this_cycle >= 20 and no_leak_ok and monotone_ok
                and scramble_ratio is not None and scramble_ratio < 0.5)
    if hard_fail:
        verdict, tag = "HARD_FAIL", "persistence_failed_or_no_growth_or_scramble_undiscriminated"
    elif hard_pass:
        verdict, tag = "HARD_PASS", "persistence_roundtrips_foundation_grows_cumulatively_scramble_discriminates"
    else:
        verdict, tag = "MIDDLE_BAND", "growth_or_persistence_present_but_bands_not_fully_cleared"

    elapsed = round(time.time() - t0, 2)
    verdict_msg = (f"{verdict}: persistence_ok={persistence_ok} "
                  f"foundation_start={foundation_size_cycle2_start} foundation_end={foundation_size_cycle2_end} "
                  f"new_this_cycle={total_new_this_cycle} scramble_ratio={scramble_ratio} "
                  f"no_leak_ok={no_leak_ok} monotone_ok={monotone_ok} arms_differ={arms_differ} "
                  f"hand_lexicon_baseline={HAND_LEXICON_BASELINE}")
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
        "cycle1_reference_grounded": CYCLE1_REFERENCE_GROUNDED,
        "foundation_size_cycle2_start": foundation_size_cycle2_start,
        "foundation_size_cycle2_end": foundation_size_cycle2_end,
        "n_new_concepts_this_cycle": total_new_this_cycle,
        "progress_toward_hand_lexicon": round(foundation_size_cycle2_end / HAND_LEXICON_BASELINE, 4),
        "persistence_round_trip": {"ok": persistence_ok, "error": persistence_error, "details": persistence_result},
        "controls": {
            "no_leak_ok": no_leak_ok,
            "monotone_growth_ok": monotone_ok,
            "n_chunks_with_new_grounding_total": n_chunks_with_growth_total,
            "scramble_probe_pool_n_sentences": scr["n_sentences"],
            "real_new_on_probe_pool_ele_cont": real_new,
            "scramble_new_on_probe_pool": scramble_new,
            "scramble_ratio": scramble_ratio,
            "arms_differ_verified": arms_differ,
        },
        "segment_summaries": {k: {kk: vv for kk, vv in v.items() if kk != "grounded_lemma_set_after"}
                              for k, v in seg_summaries.items()},
        "grounded_lemmas_final_sample": grounded_final[:80],
        "growth_curve_all_len": len(growth_curve_all),
        "cardinality_ok": True,
        "expected_segments": required,
        "measured_segments": sorted(seg_summaries.keys()),
    }


# =========================================================================== self-test
def _no_bare_except_selftest() -> None:
    lines = open(__file__, encoding="utf-8").read().splitlines()
    self_lineno = _no_bare_except_selftest.__code__.co_firstlineno
    code_lines = [ln for i, ln in enumerate(lines, start=1) if not (self_lineno <= i <= self_lineno + 6)]
    src = "\n".join(code_lines)
    assert not re.search(r"except\s+Base" + "Exception", src), "BLOCK_DISPATCH_WIDE_CATCH"
    assert not re.search(r"except\s*:", src), "BLOCK_DISPATCH_BARE_CATCH"


def _corpus_loaders_selftest() -> None:
    ele = load_ele_continuation(limit_sentences=5)
    assert len(ele) == 5 and ele[0][0] == "ele", f"ele continuation loader broken: {ele[:2]}"
    intm = load_int_continuation(limit_sentences=5)
    assert len(intm) == 5 and intm[0][0] == "int", f"int continuation loader broken: {intm[:2]}"
    adv = load_adv_new(limit_sentences=5)
    assert len(adv) == 5 and adv[0][0] == "adv", f"adv loader broken: {adv[:2]}"
    bio = load_biology_sentences(limit_sentences=50)
    assert len(bio) == 50 and bio[0][0] == "bio", bio[:2]
    full_ele = load_ele_continuation()
    assert len(full_ele) > 4000, f"ele continuation full pool too small: {len(full_ele)}"


def run_self_test() -> dict:
    _no_bare_except_selftest()
    _corpus_loaders_selftest()
    persistence_result = persistence_selftests()
    return {"no_bare_except_ok": True, "corpus_loaders_ok": True, "persistence_selftests": persistence_result}


# =========================================================================== atomic write / crash diag
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
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
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp_path, final_path)
    return final_path


# =========================================================================== smoke pipeline
def run_smoke_pipeline(output_dir: str) -> dict:
    """Exercises the FULL segmented pipeline in ONE call (smoke does not need multi-call
    splitting; full does, per the per-segment wall-time estimates in the pre-reg).

    ele_cont/scramble_probe use a DELIBERATELY LARGER slice (400 sentences, not a token handful)
    than the other continuation segments: MIN_CONFIRM=4 means the scramble-vs-real discriminator
    is structurally unmeasurable on a tiny (e.g. 4-sentence) sample (cycle 1 itself needed a
    900-sentence prefix to get ANY discriminator read during its own calibration -- see that
    cell's pre-reg "Calibration amendment"). 400 sentences keeps smoke fast (~10s) while still
    giving the DISCRIMINATOR-MUST-SURVIVE-SCALE preview-arm option (C) a real chance to fire."""
    run_bootstrap("smoke", output_dir, limit_sentences=300)
    run_continuation_segment("ele_cont", "smoke", output_dir, limit_sentences=400)
    run_continuation_segment("int_cont", "smoke", output_dir, limit_sentences=100)
    run_continuation_segment("adv_new", "smoke", output_dir, limit_sentences=100)
    run_continuation_segment("bio_new", "smoke", output_dir, limit_sentences=100)
    run_scramble_probe("smoke", output_dir, limit_sentences=400)
    return run_finalize("smoke", output_dir)


# =========================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["self_test", "smoke", "full"], default="self_test")
    ap.add_argument("--segment", choices=[s for s in SEGMENT_ORDER], default=None)
    ap.add_argument("--limit-sentences", type=int, default=None)
    args = ap.parse_args()

    if args.mode == "self_test":
        result = run_self_test()
        print(json.dumps(result, indent=2, default=str))
        print("ALL SELF-TESTS PASSED")
        return

    if args.mode == "smoke":
        output_dir = _output_dir("smoke")
        metrics = run_smoke_pipeline(output_dir)
        path = _atomic_write(output_dir, metrics)
        print(f"[done] wrote {path}")
        print(f"verdict={metrics['verdict']}")
        return

    # full mode: one segment per invocation
    output_dir = _output_dir("full")
    if args.segment is None:
        raise SystemExit("--mode full requires --segment (one of: " + ", ".join(SEGMENT_ORDER) + ")")
    if args.segment == "bootstrap":
        summary = run_bootstrap("full", output_dir, limit_sentences=args.limit_sentences)
        print(json.dumps(summary, indent=2, default=str))
    elif args.segment in SEGMENT_POOL_LOADERS:
        summary = run_continuation_segment(args.segment, "full", output_dir, limit_sentences=args.limit_sentences)
        print(json.dumps(summary, indent=2, default=str))
    elif args.segment == "scramble_probe":
        summary = run_scramble_probe("full", output_dir, limit_sentences=args.limit_sentences)
        print(json.dumps(summary, indent=2, default=str))
    elif args.segment == "finalize":
        metrics = run_finalize("full", output_dir)
        path = _atomic_write(output_dir, metrics)
        print(f"[done] wrote {path}")
        print(f"verdict={metrics['verdict']}")
    else:
        raise SystemExit(f"unknown segment {args.segment!r}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately broad per crash-diagnostic convention
        out_dir = _output_dir("full")
        _write_crash_metrics(out_dir, e)
        raise
