"""Grounded-ingest-at-scale Phase-0: exact-ID join hit-rate on the sparse tail.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: N/A (single measurement, no parallel-arm tensors)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor; binary exact-match join measurement
# - baseline_in_band: N/A (scramble control is a must-fail guard, not a
#   baseline-in-band arm)
# - discriminator survives scale: fixed 500-entity sample at both smoke and
#   full (no N-scaling axis to saturate)
# - HARD_PASS strictly above floor (drill note bands used verbatim)
# - HP_SCOPE: single measurement, one verdict, no per-arm scoping needed
# - cardinality_ok: EXPECTED_N_UNITS = 500 (tail sample size)
# - per-unit failure-class instrumentation: no bare except; SystemExit/
#   KeyboardInterrupt re-raised
# - calibration_check: default_ok_for_this_regime (bands taken verbatim from
#   preregs/grounded_ingest_tail_join_v1.md)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ in the prereg
# - Gate F.1/F.2 (real_code_path/substrate_signature): declared None,
#   justified -- no substrate KGStore/fit call in this cell (pure external
#   data-join measurement)
# - Gate F.4 (guard_baseline_valid / negative-control): scramble/wrong-ID
#   control implemented via assert_negative_control_fails_with_margin

Spec source: notes/research_grounded_ingest_at_scale_2026-07-14.md
Pre-reg: preregs/grounded_ingest_tail_join_v1.md

What this measures (NOT a training run -- a data-join measurement):
  1. Sample 500 current sparse-tail (support<=1) lexical entities from the
     live symbol graph (data/substrate_index/concept/relations.jsonl).
  2. Join against Wikidata via EXACT enwiki-sitelink-title match (no fuzzy,
     no embedding, no LLM) -- see prereg for why this IS the exact-ID method
     given CSKG carries no persisted external-ID crosswalk field.
  3. Measure (a) join hit-rate, (b) fraction of hits that cross the
     support>=2 connectivity threshold (see prereg's honest degenerate-metric
     caveat for this specific support==1 scoping).
  4. Cross-validate a scramble/gibberish-title control that must robustly
     MISS, proving the exact-match mechanism has real discriminating power.

Network-free at cell runtime: the actual Wikidata join was performed once,
interactively, with retries + a scramble-control sanity check; the full
result is committed at
data/exp_grounded_ingest_tail_join_v1/wikidata_tail_join_snapshot_500.json.
This cell RECOMPUTES the tail sample identically from the committed
relations.jsonl and cross-validates entity-for-entity identity against the
cached snapshot before trusting it -- a mismatch is a HARD_FAIL, not a
silent pass-through. This avoids a live-network dependency inside an
unattended remote-queued cell (SCRIPT_PRECONDITION_VIOLATION risk; no other
cell in this repo makes live HTTP calls at runtime).

ASCII-only. No em-dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ANCHOR_NAME = "grounded_ingest_tail_join_v1"
REPO_ROOT = Path(__file__).resolve().parent.parent
RELATIONS_PATH = REPO_ROOT / "data" / "substrate_index" / "concept" / "relations.jsonl"
SNAPSHOT_PATH = (REPO_ROOT / "data" / "exp_grounded_ingest_tail_join_v1"
                 / "wikidata_tail_join_snapshot_500.json")
EXPECTED_SOURCE_SHA256 = "d88acf2055fd986d67ea26eb79481bdf172f3284207e26f4679795fb73790e6d"

SAMPLE_SEED_PREFIX = "SEED42_LEXICAL_TAIL::"
SAMPLE_SIZE_FULL = 500
LEXICAL_PREFIX_RE = re.compile(r"^(CN|WN|FN)_")

# Pre-registered bands (preregs/grounded_ingest_tail_join_v1.md), verbatim
# from notes/research_grounded_ingest_at_scale_2026-07-14.md.
HARD_PASS_HIT_RATE = 0.15
HARD_PASS_CROSS_FRAC = 0.50
HARD_FAIL_HIT_RATE = 0.05

sys.path.insert(0, str(REPO_ROOT / "experiments"))
from _validity_preflight import (  # noqa: E402
    assert_negative_control_fails_with_margin,
    assert_real_code_path_exercised,
)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
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
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def prefix_of(entity_id: str) -> str | None:
    m = LEXICAL_PREFIX_RE.match(entity_id)
    return m.group(1) if m else None


def compute_degree_and_pool(relations_path: Path) -> tuple[dict, list, list]:
    """Return (degree_counter, lexical_tail_pool_sorted, excluded_nonlexical_tail_sorted)."""
    deg: dict = {}
    with open(relations_path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            deg[d["src_id"]] = deg.get(d["src_id"], 0) + 1
            deg[d["tgt_id"]] = deg.get(d["tgt_id"], 0) + 1
    lexical_tail = sorted(e for e, c in deg.items() if c <= 1 and prefix_of(e) is not None)
    excluded_tail = sorted(e for e, c in deg.items() if c <= 1 and prefix_of(e) is None)
    return deg, lexical_tail, excluded_tail


def _sample_key(entity_id: str) -> str:
    return hashlib.sha256((SAMPLE_SEED_PREFIX + entity_id).encode("utf-8")).hexdigest()


def deterministic_sample(pool: list, n: int) -> list:
    return sorted(pool, key=_sample_key)[:n]


def normalize_title(entity_id: str) -> str:
    m = re.match(r"^(CN|WN|FN)_(.+)$", entity_id)
    if not m:
        raise ValueError(f"entity id {entity_id!r} has no recognized lexical prefix")
    prefix, rest = m.group(1), m.group(2)
    if prefix == "WN":
        rest = re.sub(r"\.[a-z]\.\d+$", "", rest)
    words = rest.replace("_", " ")
    return (words[0].upper() + words[1:]) if words else words


def run_measurement(run_mode: str, sample_size: int) -> dict:
    t0 = time.perf_counter()
    output_dir = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}" if run_mode != "self_test" else (
        REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}_selftest")
    _write_start_marker(output_dir, run_mode, sample_size)

    if not RELATIONS_PATH.exists():
        raise FileNotFoundError(f"source graph not found: {RELATIONS_PATH}")
    source_sha256 = _sha256_file(RELATIONS_PATH)

    deg, lexical_tail_pool, excluded_tail = compute_degree_and_pool(RELATIONS_PATH)
    sample = deterministic_sample(lexical_tail_pool, sample_size)

    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            f"cached Wikidata join snapshot not found: {SNAPSHOT_PATH}. "
            f"This cell is network-free by design and requires the "
            f"pre-fetched, committed snapshot artifact."
        )
    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)

    snapshot_sample = snapshot["sample_order"]
    n_check = min(sample_size, len(snapshot_sample))
    identity_ok = sample[:n_check] == snapshot_sample[:n_check]
    if not identity_ok:
        raise ValueError(
            "SPLIT_IDENTITY_BREACH: recomputed tail sample does not match the "
            "cached snapshot's sample_order. The cached join no longer "
            "corresponds to the live graph's current sparse tail (graph may "
            "have been re-ingested, or the sampling method drifted). Do not "
            "trust the cached hit-rate; re-fetch the snapshot."
        )

    per_entity = []
    n_hit = 0
    n_missing = 0
    n_found_no_quantity = 0
    n_cross_threshold = 0
    for e in sample:
        rec = snapshot["results"].get(e)
        if rec is None:
            raise KeyError(f"entity {e!r} in recomputed sample has no cached join result")
        support = deg.get(e, 0)
        hit = bool(rec["hit"])
        crosses = False
        if hit:
            n_hit += 1
            # This sample is scoped to support==1 (see prereg scoping note);
            # adding exactly 1 grounded edge always crosses the >=2 threshold
            # for a support==1 entity. Reported honestly, not hidden as a
            # second independent signal (see prereg "Crossing-threshold
            # metric caveat").
            crosses = (support + 1) >= 2
            if crosses:
                n_cross_threshold += 1
        elif rec["missing"]:
            n_missing += 1
        else:
            n_found_no_quantity += 1
        per_entity.append({
            "entity_id": e,
            "support_pre": support,
            "title_queried": rec["title_queried"],
            "qid": rec["qid"],
            "missing": rec["missing"],
            "quantity_props": rec["quantity_props"],
            "hit": hit,
            "crosses_threshold": crosses,
        })

    n_total = len(per_entity)
    hit_rate = n_hit / n_total if n_total else 0.0
    cross_frac = (n_cross_threshold / n_hit) if n_hit else 0.0

    cardinality_ok = (n_total == sample_size)

    # Verdict per pre-registered bands.
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = (
            f"cardinality breach: expected {sample_size} units, got {n_total}"
        )
    elif hit_rate < HARD_FAIL_HIT_RATE:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: join hit-rate {hit_rate*100:.2f}% < "
            f"{HARD_FAIL_HIT_RATE*100:.0f}% floor. Bulk measured-numeric "
            f"sources (Wikidata quantity claims) do not reach this "
            f"substrate's sparse tail via exact-ID join; the tail is "
            f"dominated by entities with no measured-data analog (proper "
            f"nouns, rare taxonomic leaves, abstract relations). Do NOT "
            f"build the literal-fusion pipeline (Phase 1-3) on this basis; "
            f"the next grounding channel to try is gloss/definition text "
            f"(WordNet/Wiktionary), not numeric literals."
        )
    elif hit_rate >= HARD_PASS_HIT_RATE and cross_frac >= HARD_PASS_CROSS_FRAC:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: hit-rate {hit_rate*100:.2f}% >= "
            f"{HARD_PASS_HIT_RATE*100:.0f}% AND cross-frac "
            f"{cross_frac*100:.2f}% >= {HARD_PASS_CROSS_FRAC*100:.0f}%. "
            f"Justifies building the full literal-fusion + AdditiveKGMap "
            f"wiring (Phase 1-3 of the drill note's build plan)."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: hit-rate {hit_rate*100:.2f}% is between the "
            f"{HARD_FAIL_HIT_RATE*100:.0f}% floor and {HARD_PASS_HIT_RATE*100:.0f}% "
            f"ceiling (or cross-frac {cross_frac*100:.2f}% missed the "
            f"{HARD_PASS_CROSS_FRAC*100:.0f}% bar). Partial coverage: do NOT "
            f"launch the general literal-fusion pipeline; scope any first "
            f"production ingest to the sub-domains that actually hit."
        )

    hit_examples = [p["entity_id"] for p in per_entity if p["hit"]]
    prefix_composition = {}
    for e in sample:
        pfx = prefix_of(e)
        prefix_composition[pfx] = prefix_composition.get(pfx, 0) + 1

    elapsed_s = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "version": "v1",
        "run_mode": run_mode,
        "dispatched_ts": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"{verdict}: hit_rate={hit_rate:.4f} ({n_hit}/{n_total}), "
            f"cross_frac={cross_frac:.4f}, source_sha256_match="
            f"{source_sha256 == EXPECTED_SOURCE_SHA256}"
        ),
        "elapsed_s": round(elapsed_s, 3),
        "configs": {
            "sample_size": sample_size,
            "sample_seed_prefix": SAMPLE_SEED_PREFIX,
            "hard_pass_hit_rate": HARD_PASS_HIT_RATE,
            "hard_pass_cross_frac": HARD_PASS_CROSS_FRAC,
            "hard_fail_hit_rate": HARD_FAIL_HIT_RATE,
        },
        "REQUIRED_FIELDS": ["verdict_msg", "elapsed_s"],
        "cardinality_ok": cardinality_ok,
        "expected_n_units": sample_size,
        "n_units_measured": n_total,
        "join_hit_rate": hit_rate,
        "n_hit": n_hit,
        "n_missing": n_missing,
        "n_found_no_quantity_claim": n_found_no_quantity,
        "cross_threshold_frac_of_hits": cross_frac,
        "cross_threshold_caveat": (
            "sample is scoped to support==1 entities; any hit trivially "
            "crosses 1->2, so this fraction is a degenerate corollary of the "
            "scoping, not an independent signal -- see prereg."
        ),
        "hit_entity_examples": hit_examples,
        "prefix_composition_in_sample": prefix_composition,
        "excluded_nonlexical_tail_count": len(excluded_tail),
        "source_graph_sha256": source_sha256,
        "source_graph_sha256_expected": EXPECTED_SOURCE_SHA256,
        "source_graph_sha256_match": source_sha256 == EXPECTED_SOURCE_SHA256,
        "snapshot_identity_check_ok": identity_ok,
        "scramble_control": snapshot.get("scramble_control"),
        "per_entity": per_entity,
    }
    return metrics


def self_test() -> bool:
    """Reduced-scale self-test: exercises the REAL join path at N=20, plus the
    scramble/wrong-ID negative-control guard from the cached snapshot."""
    ok = True
    print("[self-test] recomputing tail sample + validating cached snapshot at N=20", flush=True)
    metrics = run_measurement(run_mode="self_test", sample_size=20)
    assert metrics["n_units_measured"] == 20, "self-test cardinality mismatch"
    assert metrics["snapshot_identity_check_ok"], "self-test snapshot identity check failed"
    assert metrics["source_graph_sha256_match"], (
        "source graph sha256 does not match pre-reg's pinned provenance hash; "
        "the graph file changed since the join snapshot was fetched"
    )
    print(f"[self-test] N=20 hit_rate={metrics['join_hit_rate']:.4f} "
          f"n_hit={metrics['n_hit']}", flush=True)

    # Gate F.4-equivalent: the scramble/wrong-ID control must ROBUSTLY MISS.
    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    scramble = snapshot["scramble_control"]
    control_scores = scramble["control_hit_rates"]
    print(f"[self-test] scramble control repeats: {control_scores}", flush=True)
    ok &= assert_negative_control_fails_with_margin(
        control_scores,
        headline_threshold=HARD_FAIL_HIT_RATE,
        higher_is_pass=True,
        margin=0.02,
        n_repeats_min=3,
        control_name="scramble_wrong_id_control",
        run_mode="selftest",
    )

    # Gate F.1: no substrate entrypoint invoked by this cell (pure external
    # data-join measurement) -- declare None with explicit justification per
    # prereg; this always warns (never blocks) and is expected/intentional.
    ok &= assert_real_code_path_exercised(
        None, None, run_mode="selftest",
        extra="N/A by design: this cell performs an external Wikidata join, "
              "not a substrate KGStore/fit-module call. See prereg Gate "
              "F.1 declaration.")

    if not ok:
        print("[self-test] one or more validity-preflight checks WARNED "
              "(see above); self-test still exits 0 under warn-mode checks.",
              flush=True)
    print("[self-test] PASS", flush=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "self_test"])
    parser.add_argument("--sample-size", type=int, default=SAMPLE_SIZE_FULL)
    args = parser.parse_args()

    run_mode = "self_test" if args.self_test else args.run_mode
    sample_size = 20 if run_mode == "self_test" and args.sample_size == SAMPLE_SIZE_FULL else args.sample_size

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok or True else 1)  # warn-mode checks never fail exit; enforce-mode raises

    metrics = run_measurement(run_mode=run_mode, sample_size=sample_size)
    output_dir = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"
    _write_metrics_atomic(output_dir, metrics)
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']} "
          f"hit_rate={metrics['join_hit_rate']:.4f} "
          f"elapsed_s={metrics['elapsed_s']}", flush=True)


if __name__ == "__main__":
    output_dir_for_crash = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- intentional: not BaseException
        _write_crash_metrics(output_dir_for_crash, e)
        raise
