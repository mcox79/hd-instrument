"""experiments/exp_reading_grounding_loop_cycle3_groundingfix_v1.py

Re-runs the reading-grounding loop over the SAME corpus segments as cycle 2, with the 2026-08-12
grounding-quality fix active (tautology refusal + closed-class refusal + per-fact provenance), into
a NEW foundation directory. The cycle-2 store data/foundation/reading_grounding_v1 is EVIDENCE and
is never read-write opened, never overwritten, never mutated by this cell -- it is opened READ-ONLY
in finalize() purely to recompute the BEFORE numbers.

Pre-reg: preregs/2026-08-12_grounding_quality_fix_v1.md
Design + pre-registered bands: notes/grounding_quality_fix_2026-08-12.md (written before the fix)

# CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except (grep-gated)
# - start_marker_written / crash_diagnostic_present / per-chunk progress flush
# - cardinality_ok: EXPECTED_SEGMENTS = 5; finalize refuses a verdict if any is missing
# - crlb_n/a: metrics are rates over discrete stored facts + a human-bucketed sample, not an
#   estimator against a Cramer-Rao bound
# - all numbers in this file's comments are tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - real_code_path: this cell drives the REAL ReadingLoopState / checkpoint / HDFactStore /
#   foundation_persistence objects; verification/test_grounding_refusal.py does the same at N~16

ASCII-only. Deterministic (fixed seeds; sorted(set(...)) throughout; no built-in hash()).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    ReadingLoopState,
    checkpoint,
    process_sentence,
    seed_known_words,
)
from hdlab import foundation_persistence
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    CONDITION_SEEDS, N_DIM, SCHEMA_THRESH_FULL, build_curriculum_pool, load_base_vocab_seed,
    repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, SEGMENT_POOL_LOADERS, grounded_lemmas_in_store,
)

ANCHOR_NAME = "reading_grounding_loop_cycle3_groundingfix_v1"
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]   # cardinality_ok gate
EXPECTED_N_SEGMENTS = len(SEGMENTS)

EVIDENCE_FOUNDATION = "data/foundation/reading_grounding_v1"    # READ-ONLY (cycle-2 evidence store)

# BEFORE baselines, all MEASURED@data/foundation/reading_grounding_v1 under the fixed code
# (recomputed live in finalize(); these constants exist only to make the pre-reg bands legible).
BEFORE_N_GM_FACTS = 3544
BEFORE_TAUTOLOGY_RATE = 0.6569
BEFORE_CLOSED_CLASS_OBJ_SHARE = 0.0401
BEFORE_N_GROUNDED = 3544
# B3 bucket baselines CITED@notes/foundation_grounding_sample_2026-08-12.md
B3_MIXED_BASELINE = {"MEANINGFUL": 0.04, "RELATED": 0.06, "NOISE": 0.90}
B3_CROSS_BASELINE = {"MEANINGFUL": 0.35, "RELATED": 0.25, "NOISE": 0.40}


def _foundation_dir(run_mode: str) -> str:
    tag = "reading_grounding_v2_qualityfix" if run_mode == "full" else "reading_grounding_v2_qualityfix_smoke"
    return repo_path(f"data/foundation/{tag}")


def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir: str, run_mode: str, segment: Optional[str]) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "segment": segment,
              "expected_n_units": EXPECTED_N_SEGMENTS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


# =========================================================================== segment drivers
def run_segment(segment: str, run_mode: str, output_dir: str, *,
                limit_sentences: Optional[int] = None, chunk_size: int = CHUNK_SIZE) -> dict:
    """One segment. `bootstrap` builds a fresh store from cycle 1's exact curriculum pool; every
    other segment loads the persisted foundation and reads its own pool on top of it."""
    foundation_dir = _foundation_dir(run_mode)
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("segment_done", segment)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    t0 = time.time()
    if segment == "bootstrap":
        pool = build_curriculum_pool(limit_sentences=limit_sentences)
        store = HDFactStore(n_dim=N_DIM, seed=CONDITION_SEEDS["curriculum_real"],
                            relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                                  MEANING_RELATION: "FUNCTIONAL"},
                            use_index=True)
        state = ReadingLoopState(store=store)
        seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")
        start_pass = 0
        size_before = 0
    else:
        if not foundation_persistence.foundation_exists(foundation_dir):
            raise RuntimeError(f"segment {segment!r} requires the foundation (run bootstrap first)")
        pool = SEGMENT_POOL_LOADERS[segment](limit_sentences)
        manifest_before = foundation_persistence.load_manifest(foundation_dir)
        state = foundation_persistence.load_foundation(foundation_dir)
        start_pass = manifest_before["next_pass_idx"]
        size_before = len(grounded_lemmas_in_store(state.store))
    known_seed_snapshot = set(state.known_seed)

    n_chunks = math.ceil(len(pool) / chunk_size) if pool else 0
    for chunk_idx in range(n_chunks):
        pass_idx = start_pass + chunk_idx
        chunk = pool[chunk_idx * chunk_size:(chunk_idx + 1) * chunk_size]
        for i, (_tier, sent) in enumerate(chunk):
            process_sentence(state, sent, f"{segment}_{chunk_idx}_{i}", pass_idx=pass_idx)
        row = checkpoint(state, pass_idx=pass_idx, source_tag=segment,
                         schema_thresh=SCHEMA_THRESH_FULL)          # refuse_non_groundings=True
        row["segment"] = segment
        row["foundation_size_in_store"] = len(grounded_lemmas_in_store(state.store))
        key = exp_checkpoint.unit_key(segment, chunk_idx)
        if key not in already:
            exp_checkpoint.record_unit(output_dir, key, row)
        print(f"[progress] {segment} chunk={chunk_idx + 1}/{n_chunks} "
              f"grounded={row['foundation_size_in_store']} refused={row['n_refused_cumulative']} "
              f"elapsed={time.time() - t0:.1f}s", flush=True)

    next_pass_idx = start_pass + n_chunks
    foundation_persistence.save_foundation(state, foundation_dir, source_tag=segment,
                                           next_pass_idx=next_pass_idx)
    grounded_after = grounded_lemmas_in_store(state.store)
    summary = {
        "segment": segment, "n_sentences": len(pool), "n_chunks": n_chunks,
        "foundation_size_before": size_before, "foundation_size_after": len(grounded_after),
        "n_newly_grounded_this_segment": len(grounded_after) - size_before,
        "n_refusals_cumulative": len(state.refusals),
        "no_leak_violations": [l for l in grounded_after if l in known_seed_snapshot],
        "elapsed_s": round(time.time() - t0, 2), "next_pass_idx": next_pass_idx,
    }
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


# =========================================================================== band measurement
def measure_store_bands(store: HDFactStore, provenance: List[dict]) -> dict:
    """B1 / B2 / B4 / B5 on ONE store. Identical code path is applied to the BEFORE (v1) and AFTER
    (v2) stores in finalize(), so the comparison cannot drift between arms."""
    gm = [f for f in store._facts if f.relation == MEANING_RELATION]
    live_gm = [f for f in store.live_facts() if f.relation == MEANING_RELATION]
    n = len(gm)
    taut = sum(1 for f in gm if f.subject == f.obj)
    cc_obj = sum(1 for f in gm if is_closed_class(f.obj))
    cc_sub = sum(1 for f in gm if is_closed_class(f.subject))
    prov_fids = {r.get("fid") for r in provenance}
    covered = sum(1 for f in live_gm if f.fid in prov_fids)
    with_sentences = sum(1 for r in provenance
                         if r.get("evidence") and all(e.get("sentence") for e in r["evidence"]))
    return {
        "n_grounded_meaning_facts": n,
        "n_grounded_concepts": len(sorted({f.subject for f in live_gm})),
        "B1_tautology_rate": round(taut / n, 6) if n else 0.0,
        "n_tautologies": taut,
        "B2_closed_class_object_share": round(cc_obj / n, 6) if n else 0.0,
        "n_closed_class_objects": cc_obj,
        "closed_class_subject_share": round(cc_sub / n, 6) if n else 0.0,
        "B5_provenance_coverage": round(covered / len(live_gm), 6) if live_gm else 0.0,
        "n_provenance_rows": len(provenance),
        "n_provenance_rows_with_full_sentences": with_sentences,
    }


def sample_pairs_for_audit(store: HDFactStore, provenance: List[dict], k: int = 50,
                           seed: int = 42) -> List[dict]:
    """Draw the B3 audit sample by the SAME procedure and seed as the prior audit
    (CITED@notes/foundation_grounding_sample_2026-08-12.md): random.seed(42) then
    random.sample(range(len(gm_facts)), 50) over GROUNDED_MEANING facts in fid order."""
    gm = [f for f in store._facts if f.relation == MEANING_RELATION]
    if not gm:
        return []
    prov_by_fid = {r.get("fid"): r for r in provenance}
    random.seed(seed)
    idx = random.sample(range(len(gm)), min(k, len(gm)))
    rows = []
    for i in idx:
        f = gm[i]
        p = prov_by_fid.get(f.fid, {})
        rows.append({
            "subject": f.subject, "object": f.obj, "self": f.subject == f.obj,
            "segment": p.get("segment"), "best_cos": p.get("best_cos"),
            "n_exp": p.get("n_exposures"), "schema_score": p.get("schema_score"),
            "source_sentences": [e.get("sentence") for e in p.get("evidence", [])][:3],
        })
    return rows


def run_finalize(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    foundation_dir = _foundation_dir(run_mode)
    units = exp_checkpoint.load_units(output_dir)
    seg = {k.split("|", 1)[1]: v for k, v in units.items() if k.startswith("segment_done|")}
    missing = [s for s in SEGMENTS if s not in seg]
    if missing:
        raise RuntimeError(f"HARD_FAIL_CARDINALITY_BREACH: finalize before segments {missing}")

    after_state = foundation_persistence.load_foundation(foundation_dir)
    after = measure_store_bands(after_state.store, after_state.provenance)

    before_state = foundation_persistence.load_foundation(repo_path(EVIDENCE_FOUNDATION))
    before = measure_store_bands(before_state.store, before_state.provenance)
    b6_ok = len(before_state.store._facts) == 7966 and before["n_grounded_meaning_facts"] == 3544

    b1_pass = after["B1_tautology_rate"] == 0.0
    b2_pass = after["B2_closed_class_object_share"] == 0.0
    n_after = after["n_grounded_concepts"]
    b4_pass = 300 <= n_after <= 1400
    b4_fail = (n_after == 0) or (n_after >= 3000)
    b5_pass = after["B5_provenance_coverage"] == 1.0

    sample = sample_pairs_for_audit(after_state.store, after_state.provenance)
    sample_path = os.path.join(output_dir, "b3_audit_sample.json")
    with open(sample_path + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"rubric": "MEANINGFUL / RELATED / NOISE per notes/foundation_grounding_sample_"
                             "2026-08-12.md; sampling random.seed(42) over GROUNDED_MEANING fid order",
                   "mixed_baseline": B3_MIXED_BASELINE, "cross_baseline": B3_CROSS_BASELINE,
                   "rows": sample}, f, indent=2)
    os.replace(sample_path + ".tmp", sample_path)

    structural_pass = b1_pass and b2_pass and b5_pass and b6_ok and not b4_fail
    if not structural_pass:
        verdict = "HARD_FAIL"
    elif b4_pass:
        verdict = "STRUCTURAL_PASS_PENDING_B3"
    else:
        verdict = "MIDDLE_BAND"
    verdict_msg = (f"{verdict}: B1_taut {before['B1_tautology_rate']}->{after['B1_tautology_rate']} "
                   f"B2_cc_obj {before['B2_closed_class_object_share']}->{after['B2_closed_class_object_share']} "
                   f"B4_grounded {before['n_grounded_concepts']}->{n_after} "
                   f"B5_prov {before['B5_provenance_coverage']}->{after['B5_provenance_coverage']} "
                   f"B6_v1_loads={b6_ok}. B3 requires the human-bucketed 50-pair audit at "
                   f"{sample_path} -- NOT auto-scored, NOT claimed here.")
    print(f"[verdict] {verdict_msg}", flush=True)
    return {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}_grounding_quality_fix", "elapsed_s": round(time.time() - t0, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "before_v1": before, "after_v2": after,
        "bands": {"B1_pass": b1_pass, "B2_pass": b2_pass, "B4_pass": b4_pass, "B4_fail": b4_fail,
                  "B5_pass": b5_pass, "B6_pass": b6_ok,
                  "B3_pass": None, "B3_note": "human-bucketed; see b3_audit_sample.json"},
        "b4_interpretation": ("A LARGE DROP IS THE EXPECTED CORRECTION, NOT A REGRESSION: the v1 "
                              "count of 3544 included 2328 tautologies asserting nothing plus "
                              f"{before['n_closed_class_objects']} function-word objects."),
        "n_refusals_total": len(after_state.refusals),
        "refusal_reason_counts": _reason_counts(after_state.refusals),
        "segment_summaries": seg, "expected_segments": SEGMENTS,
        "measured_segments": sorted(seg.keys()), "cardinality_ok": True,
        "b3_audit_sample_path": sample_path,
    }


def _reason_counts(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return dict(sorted(out.items()))


# =========================================================================== self-test
def _no_bare_except_selftest() -> None:
    lines = open(__file__, encoding="utf-8").read().splitlines()
    start = _no_bare_except_selftest.__code__.co_firstlineno
    src = "\n".join(ln for i, ln in enumerate(lines, 1) if not (start <= i <= start + 7))
    assert not re.search(r"except\s+Base" + "Exception", src), "BLOCK_DISPATCH_WIDE_CATCH"
    assert not re.search(r"except\s*:", src), "BLOCK_DISPATCH_BARE_CATCH"


def _selftest_real_code_path_tiny() -> None:
    """Constructs the REAL substrate objects this cell drives at full scale (HDFactStore,
    ReadingLoopState, seed_known_words, process_sentence, checkpoint, save/load_foundation) at
    N~16, so a signature/API drift fails HERE in seconds rather than mid-run."""
    import tempfile
    exercised = set()
    store = HDFactStore(n_dim=512, seed=3, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                                                MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    exercised.add("HDFactStore")
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["boat", "storm", "harbor"], "selftest")
    exercised.add("seed_known_words")
    for i, s in enumerate([
            "Owen moored the flimzat boat before the storm reached the harbor.",
            "The crew moored a flimzat boat before every storm hit the harbor.",
            "Sailors always moor the flimzat boat before a storm nears the harbor.",
            "They moored the old flimzat boat before the storm entered the harbor."]):
        process_sentence(state, s, f"s{i}", pass_idx=0)
    exercised.add("process_sentence")
    checkpoint(state, pass_idx=0, source_tag="selftest", schema_thresh=SCHEMA_THRESH_FULL)
    checkpoint(state, pass_idx=1, source_tag="selftest", schema_thresh=SCHEMA_THRESH_FULL)
    exercised.add("checkpoint")
    with tempfile.TemporaryDirectory() as tmp:
        foundation_persistence.save_foundation(state, tmp, source_tag="selftest", next_pass_idx=2)
        back = foundation_persistence.load_foundation(tmp)
        exercised.add("save_foundation")
        exercised.add("load_foundation")
        bands = measure_store_bands(back.store, back.provenance)
    assert bands["B1_tautology_rate"] == 0.0, bands
    assert bands["B2_closed_class_object_share"] == 0.0, bands
    if bands["n_grounded_concepts"]:
        assert bands["B5_provenance_coverage"] == 1.0, bands
    required = {"HDFactStore", "seed_known_words", "process_sentence", "checkpoint",
                "save_foundation", "load_foundation"}
    assert required <= exercised, f"real_code_path incomplete: {required - exercised}"


def _selftest_evidence_store_is_readonly_and_loads() -> None:
    """B6 gate + the do-not-mutate-the-evidence invariant: the v1 store loads unchanged, and this
    cell's foundation directory is a DIFFERENT path from the evidence store."""
    ev = repo_path(EVIDENCE_FOUNDATION)
    assert os.path.abspath(_foundation_dir("full")) != os.path.abspath(ev)
    assert os.path.abspath(_foundation_dir("smoke")) != os.path.abspath(ev)
    if foundation_persistence.foundation_exists(ev):
        st = foundation_persistence.load_store(os.path.join(ev, "store"))
        assert len(st._facts) == 7966, f"v1 evidence store changed: {len(st._facts)} facts"


def run_self_test() -> dict:
    _no_bare_except_selftest()
    _selftest_real_code_path_tiny()
    _selftest_evidence_store_is_readonly_and_loads()
    return {"no_bare_except_ok": True, "real_code_path_ok": True,
            "evidence_store_readonly_ok": True}


# =========================================================================== io / main
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["self_test", "smoke", "full"], default="self_test")
    ap.add_argument("--segment", choices=SEGMENTS + ["finalize", "all"], default=None)
    ap.add_argument("--limit-sentences", type=int, default=None)
    args = ap.parse_args()

    if args.mode == "self_test":
        print(json.dumps(run_self_test(), indent=2))
        print("ALL SELF-TESTS PASSED")
        return

    output_dir = _output_dir(args.mode)
    _write_start_marker(output_dir, args.mode, args.segment)

    if args.mode == "smoke":
        run_segment("bootstrap", "smoke", output_dir, limit_sentences=300)
        run_segment("ele_cont", "smoke", output_dir, limit_sentences=400)
        run_segment("int_cont", "smoke", output_dir, limit_sentences=200)
        run_segment("adv_new", "smoke", output_dir, limit_sentences=200)
        run_segment("bio_new", "smoke", output_dir, limit_sentences=200)
        metrics = run_finalize("smoke", output_dir)
        print(f"[done] wrote {_atomic_write(output_dir, metrics)} verdict={metrics['verdict']}")
        return

    if args.segment is None:
        raise SystemExit("--mode full requires --segment (" + ", ".join(SEGMENTS + ["finalize", "all"]) + ")")
    if args.segment == "all":
        for s in SEGMENTS:
            print(json.dumps(run_segment(s, "full", output_dir,
                                         limit_sentences=args.limit_sentences), indent=2), flush=True)
        metrics = run_finalize("full", output_dir)
        print(f"[done] wrote {_atomic_write(output_dir, metrics)} verdict={metrics['verdict']}")
    elif args.segment == "finalize":
        metrics = run_finalize("full", output_dir)
        print(f"[done] wrote {_atomic_write(output_dir, metrics)} verdict={metrics['verdict']}")
    else:
        print(json.dumps(run_segment(args.segment, "full", output_dir,
                                     limit_sentences=args.limit_sentences), indent=2))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir("full"), e)
        raise
