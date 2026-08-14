"""exp_differentia_simplewiki_extract_v1 -- STEP 1 of Stage 2: build the differentia feature
supply by running the UNMODIFIED definitional extractor over the FULL Simple English Wikipedia.

PRE-REG: preregs/2026-08-13_differentia_feature_supply.md AMENDMENT A1 (commit 64a4ea4c2, filed
BEFORE this cell ran and BEFORE any correlation was computed).

THE PATTERN RESTRICTION IS FROZEN IN ADVANCE (A1.1):
    TREATMENT SUPPLY = COPULA and GLOSSARY_COLON ONLY.
    CALLED, REFERS_TO and APPOSITIVE are FORBIDDEN and are NEVER PERSISTED to the treatment
    store, so no downstream treatment arm can reach them even by mistake. Their counts ARE
    recorded, because the per-pattern mix is what decides the synonym-leak confound (pre-reg 4.1).

NO FILE UNDER hdlab/ IS MODIFIED. `hdlab.definitional_extraction.extract_definitions` is imported
and called unmodified, exactly as the Stage-1 yield probe called it.

The store is written to a NEW directory. It is NOT written into any foundation store and is NOT
banked into the canonical fact store. This is measurement supply, not a foundation commit.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - per-unit checkpoint/resume via tools/exp_checkpoint.py (units = 200k-line blocks)
# - start marker + heartbeat + crash diagnostic (section 13)
# - deterministic: single pass in file order; sorted(set()) only; no builtin hash()
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede any numpy import (pools are sized at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.definitional_extraction import PATTERNS, extract_definitions        # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

ANCHOR_NAME = "exp_differentia_simplewiki_extract_v1"
PREREG_PATH = "preregs/2026-08-13_differentia_feature_supply.md"

CORPUS = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

# FROZEN IN ADVANCE (pre-reg A1.1). Not revisited after any number was seen.
TREATMENT_PATTERNS = ("COPULA", "GLOSSARY_COLON")
FORBIDDEN_PATTERNS = ("CALLED", "REFERS_TO", "APPOSITIVE")

BLOCK_LINES = 200000          # one checkpoint unit; 2,779,032 lines -> 14 units
MAX_SENT_CHARS = 600          # matches the Stage-1 yield probe exactly
SMOKE_BLOCKS = 1              # smoke reads the first block only, to a SEPARATE dir


# ---------------------------------------------------------------------------------------------
# Durability plumbing (section 13)
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _heartbeat(output_dir: str, unit_idx: int, total_units: int, elapsed_s: float,
               extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)          # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash", "failure_class": type(exc).__name__,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------------------------
def _shard_path(output_dir: str, block_idx: int) -> str:
    return os.path.join(output_dir, "facts_block_%03d.jsonl" % block_idx)


def extract_block(lines: List[str], first_line_no: int, output_dir: str,
                  block_idx: int) -> dict:
    """Run the UNMODIFIED extractor over one block. Persist ONLY treatment-pattern facts;
    count every pattern. Written tmp-then-replace so a resumed run never sees a partial shard."""
    counts: Dict[str, int] = {p: 0 for p in PATTERNS}
    kept = 0
    n_sent = 0
    tmp = _shard_path(output_dir, block_idx) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as out:
        for off, raw in enumerate(lines):
            s = raw.strip()
            if not s or len(s) > MAX_SENT_CHARS:
                continue
            n_sent += 1
            for d in extract_definitions(s):
                counts[d.pattern] = counts.get(d.pattern, 0) + 1
                if d.pattern not in TREATMENT_PATTERNS:
                    continue        # FORBIDDEN patterns are never persisted (pre-reg A1.1)
                row = {"term": d.term, "term_type": d.term_type,
                       "definiendum": d.definiendum, "definiendum_lemma": d.definiendum_lemma,
                       "definiens": d.definiens, "pattern": d.pattern, "head": d.head,
                       "definiens_lemmas": d.definiens_lemmas,
                       "line_no": first_line_no + off, "sentence": d.sentence}
                out.write(json.dumps(row, ensure_ascii=True) + "\n")
                kept += 1
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp, _shard_path(output_dir, block_idx))
    return {"block_idx": block_idx, "first_line_no": first_line_no,
            "n_lines": len(lines), "n_sentences_processed": n_sent,
            "pattern_counts_all": counts, "n_facts_kept": kept,
            "shard": os.path.basename(_shard_path(output_dir, block_idx)),
            "failure_class": None}


def _iter_blocks(max_blocks: Optional[int]):
    """Yield (block_idx, first_line_no, lines). Single pass in file order -> deterministic."""
    buf: List[str] = []
    first = 1
    idx = 0
    with open(CORPUS, encoding="utf-8", errors="replace") as f:
        for line in f:
            buf.append(line)
            if len(buf) >= BLOCK_LINES:
                yield idx, first, buf
                idx += 1
                first += len(buf)
                buf = []
                if max_blocks is not None and idx >= max_blocks:
                    return
        if buf:
            yield idx, first, buf


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- module scope, before any sweep)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    """Assert the extractor is live, that the treatment filter passes >= 1 item at tiny scale,
    and that the FORBIDDEN patterns are (a) reachable by the extractor and (b) removed by the
    filter -- a filter that never removes anything is not a filter."""
    t0 = time.time()
    res: dict = {}
    assert os.path.exists(CORPUS), "corpus missing: %s" % CORPUS
    res["corpus_bytes"] = os.path.getsize(CORPUS)

    copula = "A nephron is the functional unit of the kidney."
    ds = extract_definitions(copula)
    pats = sorted({d.pattern for d in ds})
    assert "COPULA" in pats, "extractor produced no COPULA on a canonical copula sentence: %r" % pats
    d0 = [d for d in ds if d.pattern == "COPULA"][0]
    assert d0.definiens and d0.head, "COPULA definition has empty definiens/head: %r" % d0.to_dict()
    assert d0.definiens_lemmas, "definiens_lemmas empty -- differentia would be empty by construction"
    res["selftest_copula"] = {"term": d0.term, "head": d0.head,
                              "n_definiens_lemmas": len(d0.definiens_lemmas)}

    # A FORBIDDEN pattern must be REACHABLE (so the filter is doing real work) and REMOVED.
    called = "This structure is called the nephron."
    dc = extract_definitions(called)
    assert any(d.pattern in FORBIDDEN_PATTERNS for d in dc), (
        "no FORBIDDEN-pattern definition produced on a canonical CALLED sentence; the pattern "
        "filter would be vacuous")
    n_before = len(dc)
    n_after = len([d for d in dc if d.pattern in TREATMENT_PATTERNS])
    assert n_after < n_before, "treatment filter removed nothing (%d -> %d)" % (n_before, n_after)
    res["selftest_filter_removes"] = {"before": n_before, "after": n_after}

    # The block writer must produce a non-empty shard with ONLY treatment patterns.
    probe_dir = OUT_SELFTEST
    os.makedirs(probe_dir, exist_ok=True)
    r = extract_block([copula + "\n", called + "\n"], 1, probe_dir, 999)
    assert r["n_facts_kept"] >= 1, "block writer kept 0 facts at self-test scale"
    with open(_shard_path(probe_dir, 999), encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    assert rows, "self-test shard is empty"
    got = sorted({x["pattern"] for x in rows})
    assert all(p in TREATMENT_PATTERNS for p in got), "FORBIDDEN pattern reached the store: %r" % got
    res["selftest_shard_rows"] = len(rows)
    res["selftest_shard_patterns"] = got
    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_blocks: Optional[int]) -> dict:
    t0 = time.time()
    total_lines = 2779032          # MEASURED@this cell 2026-08-13 (wc over the corpus)
    expected_units = (min(max_blocks, (total_lines + BLOCK_LINES - 1) // BLOCK_LINES)
                      if max_blocks is not None
                      else (total_lines + BLOCK_LINES - 1) // BLOCK_LINES)
    _write_start_marker(output_dir, run_mode, expected_units)
    done = completed_units(output_dir)
    prior = load_units(output_dir)

    for idx, first, lines in _iter_blocks(max_blocks):
        key = unit_key("block", idx)
        if key in done:
            print("[block %03d] resumed (%d facts)" % (idx, prior[key]["n_facts_kept"]), flush=True)
            continue
        r = extract_block(lines, first, output_dir, idx)
        record_unit(output_dir, key, r)
        _heartbeat(output_dir, idx + 1, expected_units, time.time() - t0,
                   {"facts": r["n_facts_kept"], "sentences": r["n_sentences_processed"]})
        print("[block %03d] lines=%d sentences=%d facts_kept=%d elapsed=%.1fs"
              % (idx, r["n_lines"], r["n_sentences_processed"], r["n_facts_kept"],
                 time.time() - t0), flush=True)

    units = load_units(output_dir)
    counts_all: Dict[str, int] = {p: 0 for p in PATTERNS}
    n_lines = n_sent = n_facts = 0
    for u in units.values():
        for p, c in u["pattern_counts_all"].items():
            counts_all[p] = counts_all.get(p, 0) + c
        n_lines += u["n_lines"]
        n_sent += u["n_sentences_processed"]
        n_facts += u["n_facts_kept"]

    # ---- THE FROZEN ASSERTION (pre-reg A1.1), evaluated over the PERSISTED store -------------
    persisted_patterns = set()
    terms = set()
    for u in sorted(units.values(), key=lambda x: x["block_idx"]):
        with open(os.path.join(output_dir, u["shard"]), encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                persisted_patterns.add(row["pattern"])
                if row["term"]:
                    terms.add(row["term"].lower())
    forbidden_present = sorted(persisted_patterns & set(FORBIDDEN_PATTERNS))
    if forbidden_present:
        raise AssertionError("FORBIDDEN PATTERN IN TREATMENT STORE: %r" % forbidden_present)
    assert persisted_patterns, "treatment store is empty"
    assert persisted_patterns <= set(TREATMENT_PATTERNS), (
        "unexpected pattern in treatment store: %r" % sorted(persisted_patterns))

    cardinality_ok = len(units) >= expected_units
    verdict = "EXTRACTION_OK" if cardinality_ok else "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    msg = ("simplewiki FULL: %d lines, %d sentences, %d treatment facts (%s), %d distinct terms; "
           "per-pattern ALL=%s; FORBIDDEN {CALLED,REFERS_TO,APPOSITIVE} persisted=0 (asserted)"
           % (n_lines, n_sent, n_facts, "+".join(sorted(persisted_patterns)), len(terms),
              json.dumps(counts_all, sort_keys=True)))
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "differentia supply extraction from full Simple English Wikipedia",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_units": len(units), "expected_n_units": expected_units,
        "cardinality_ok": cardinality_ok,
        "corpus": os.path.relpath(CORPUS, REPO_ROOT),
        "n_lines_read": n_lines, "n_sentences_processed": n_sent,
        "n_treatment_facts": n_facts, "n_distinct_terms": len(terms),
        "pattern_counts_all_five": counts_all,
        "treatment_patterns_frozen_in_advance": list(TREATMENT_PATTERNS),
        "forbidden_patterns": list(FORBIDDEN_PATTERNS),
        "forbidden_pattern_assertion": {
            "persisted_patterns": sorted(persisted_patterns),
            "forbidden_persisted": forbidden_present,
            "assertion": "sorted(set(persisted)) subset of ['COPULA','GLOSSARY_COLON']",
            "result": "PASS"},
        "hdlab_modified": False,
        "written_to_foundation_store": False,
        "banked_to_canonical_fact_store": False,
        "units": units,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        m = run("smoke", OUT_SMOKE, SMOKE_BLOCKS)
        assert m["n_treatment_facts"] > 0, "SMOKE VACUOUS: 0 treatment facts"
        assert m["pattern_counts_all_five"]["COPULA"] > 0, "SMOKE VACUOUS: 0 COPULA"
        n_forbidden = sum(m["pattern_counts_all_five"][p] for p in FORBIDDEN_PATTERNS)
        assert n_forbidden > 0, (
            "SMOKE VACUOUS: the corpus produced 0 FORBIDDEN-pattern definitions, so the frozen "
            "restriction removed nothing and is untested at this scale")
        print("SMOKE=PASS (facts=%d, forbidden seen-and-dropped=%d)"
              % (m["n_treatment_facts"], n_forbidden), flush=True)
        return
    run("full", OUT_FULL, None)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any sweep

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
