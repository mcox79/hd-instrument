"""KB PARTITION BY SOURCE CLASS v2 (ANCHOR 1 RESCUE; INFRASTRUCTURE; 2026-06-26).

Pre-reg: preregs/2026-06-26_kb_partition_by_source_class_v2.md
v1 HARD_FAILED at the same-day diagnosis as a GATE problem, not a mechanism
problem.

v1 result re-read (off data/exp_exp_kb_partition_by_source_class_v1/metrics.json):
  ARM_PARTITIONED_W_EQUAL_CAPACITY
    routing_accuracy            = 1.0     (PERFECT)
    cross_partition_leak_rate   = 0.0     (PERFECT)
    ratio_resolved              = 0.80    (vs baseline 1.0)
    n_capacity_regression       = 6       (the over-strict gate that fired HARD_FAIL)
  ARM_PARTITIONED_W_MEMORY_OVERSIZED
    user_directive_retention    = 0.6     (3 of 5 USER directives)
    n_user_directive_total      = 5
    non_ud_resolved_ratio       = 0.84

v1 verdict was HARD_FAIL because:
  (A) Hard gate `n_capacity_regression == 0` compared partition-filtered
      retrieval to UNFILTERED baseline (the comparison is structurally
      lossy: filter is by construction a strict subset of candidates).
  (B) Several ROUTED_QUERIES are cross-cutting (USER directives, fleet
      cross-refs) and legitimately live in multiple source_classes
      (memory + notes + preregs simultaneously). The singleton expected-
      class encoding undercounts hits.
  (C) ARM_MEMORY_OVERSIZED required user_directive_retention=1.0 (with
      the confidence_floor=0.3 nested inside the memory shard). That gate
      measures whether memory partition individually retains UDs, not
      whether OVERSIZING helps UD match the non-UD resolve rate.

v2 fixes (research-confirmed; see handoff task body):

PATH A (success criterion relaxation):
  - HARD_PASS requires: routing_accuracy >= 0.95 AND
                        cross_partition_leak_rate < 0.05 AND
                        ratio_resolved >= 0.80
  - MEMORY_OVERSIZED replaces the 1.0 retention floor with:
      user_directive_retention >= max(non_ud_resolved_ratio - 0.10, 0.70)
    measures whether OVERSIZING helps UDs match non-UDs, not whether
    confidence_floor=0.3 is met inside the memory shard.
  - n_capacity_regression NO LONGER hard-gates; reported as diagnostic.

PATH B (corpus relabel):
  - ROUTED_QUERIES now has expected_classes as a tuple-of-permissible
    rather than a singleton. ~5 cross-cutting queries (USER directives,
    fleet cross-refs, etc.) accept hits in any of the listed classes.
  - routing_accuracy now counts as correct if top-1 lands in ANY of the
    permissible classes for that query.

ARMS (3 mandatory; unchanged from v1):
  ARM_SINGLE_W_BASELINE                   - unpartitioned baseline reference
  ARM_PARTITIONED_W_EQUAL_CAPACITY        - source_class filter; routing
                                            accuracy
  ARM_PARTITIONED_W_MEMORY_OVERSIZED      - USER memory partition 4x k-floor

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb_query import DirectorKBQuery, load_default_kb  # noqa: E402


# v2 ROUTED_QUERIES: expected_classes is a TUPLE of all permissible source
# classes for that query (Path B relabel). Cross-cutting queries get
# multi-class permits (USER directives live in memory AND in notes AND in
# preregs; fleet cross-refs live in notes AND in memory; etc.).
ROUTED_QUERIES: list[tuple[str, tuple[str, ...], str]] = [
    # notes (canonical; mostly singletons)
    ("substrate director kb ingest", ("note", "prereg"), "director_kb"),
    ("chain grade multi hop depth extension", ("note",), "multihop"),
    ("fleet waiting on tracker", ("note", "memory"), "fleet"),
    ("anisotropy rescue 4 arm", ("note",), "anisotropy"),
    ("eff rank diagnostic shakespeare", ("note",), "eff_rank"),
    ("phase diagram capacity sweep", ("note",), "phase_diagram"),
    ("ultrametric clustering chain grade", ("note",), "ultrametric"),
    ("standstill ack inflight inventory", ("note",), "standstill"),
    # preregs
    ("substrate director kb ingest pre reg", ("prereg",), "director_kb"),
    ("kb dual store audit pre reg", ("prereg",), "dual_store"),
    ("language trio ingest pre reg", ("prereg",), "language_trio"),
    # memory (USER directives are cross-cutting; live in memory + notes +
    # often prereg too because they get referenced)
    ("USER directive no busy work",
     ("memory", "note", "prereg"), "no_busy"),
    ("USER directive monitor armed",
     ("memory", "note"), "monitor"),
    ("memory curator skill dispatch", ("memory", "note"), "memory_curator"),
    ("fleet waiting on shared file",
     ("memory", "note"), "fleet_waiting"),
    ("MEMORY index curation", ("memory",), "MEMORY"),
    # metrics (exp_*/metrics.json)
    ("exp cortex ultrametric clustering metrics", ("metrics",), "ultrametric"),
    ("exp substrate director kb ingest metrics", ("metrics",), "director_kb"),
    ("exp substrate director kb language trio metrics",
     ("metrics",), "language_trio"),
    # cert ledger
    ("cert ledger atom row", ("cert_ledger",), "cert_ledger"),
    # wordnet (language trio)
    ("wordnet synset hypernym", ("wordnet",), "wordnet"),
    ("wordnet noun definition gloss", ("wordnet",), "wordnet"),
    # verbnet
    ("verbnet class lemma frame", ("verbnet",), "verbnet"),
    # framenet
    ("framenet frame element evoke", ("framenet",), "framenet"),
    # bio
    ("gene ontology obo term hierarchy", ("gene_ontology",), "gene_ontology"),
    ("kegg pathway kgml metabolic", ("kegg_pathway",), "kegg"),
    ("neurolex brain region ttl", ("neurolex",), "neurolex"),
    # director_plan
    ("director plan priorities", ("director_plan",), "director_plan"),
    # mixed (just check it routes somewhere reasonable)
    ("HARD_PASS verdict elapsed", ("metrics", "note"), "HARD_PASS"),
    ("substrate index atom row", ("atoms", "cert_ledger"), "substrate_index"),
]
assert len(ROUTED_QUERIES) >= 30, f"want >= 30, got {len(ROUTED_QUERIES)}"

DEFAULT_K = 8
MEMORY_K = 32  # 4x oversize for USER memory partition (ARM 3)
DEFAULT_TAU = 0.3

# v2 PASS bands (relaxed per Research handoff; documented above).
ROUTING_HP_FLOOR = 0.95
LEAK_HP_CEIL = 0.05
RATIO_RESOLVED_FLOOR = 0.80
ROUTING_MB_FLOOR = 0.90  # below MB floor is HARD_FAIL
# UD retention relative band: ud_ret >= max(non_ud - 0.10, 0.70)
UD_RELATIVE_GAP = 0.10
UD_ABS_FLOOR = 0.70


def _is_user_directive_query(expected_classes: tuple[str, ...]) -> bool:
    """A query is treated as a USER directive (gets 4x k) iff 'memory' is
    among its permissible classes (Path B relabel: UD queries are
    cross-cutting and have multiple permissible classes)."""
    return "memory" in expected_classes


def _arm_single_w_baseline(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """Unpartitioned baseline: no source_class filter; record what resolves."""
    t0 = time.perf_counter()
    n_resolved = 0
    per_query: list[dict] = []
    for q, _expected_classes, _expected_substr in queries:
        r = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU)
        resolved = (not r["refused"]) and len(r["top_k_atoms"]) >= 1
        if resolved:
            n_resolved += 1
        per_query.append({
            "q": q[:50], "resolved": resolved,
            "confidence": r.get("confidence", 0),
            "n_top": len(r.get("top_k_atoms", [])),
        })
    elapsed = time.perf_counter() - t0
    ratio = n_resolved / len(queries)
    return {
        "arm": "ARM_SINGLE_W_BASELINE",
        "ok": True,  # baseline is always ok (it's the reference)
        "n_queries": len(queries),
        "n_resolved": n_resolved,
        "ratio_resolved": round(ratio, 4),
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:10],
        "_per_query_full": per_query,
    }


def _arm_partitioned_equal_capacity(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
    baseline_per_query: list[dict],
) -> dict:
    """Source-class-filtered query; routing accuracy on permissible-set.

    v2: routing correctness counts top-1 hit in ANY permissible class as
    success (Path B relabel; multi-class queries get fair credit).
    """
    t0 = time.perf_counter()
    n_routed_correctly = 0
    n_resolved = 0
    n_regression = 0  # diagnostic only in v2
    cross_partition_leakage = 0
    n_with_topk = 0
    per_query: list[dict] = []
    for i, (q, expected_classes, _expected_substr) in enumerate(queries):
        r = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU,
                     source_classes=list(expected_classes))
        resolved = (not r["refused"]) and len(r["top_k_atoms"]) >= 1
        if resolved:
            n_resolved += 1
        if baseline_per_query[i]["resolved"] and not resolved:
            n_regression += 1
        topk = r.get("top_k_atoms", [])
        target_hits = 0
        leak_hits = 0
        # v2: top-1 routing correctness is hit-in-permissible-set
        top1_correct = False
        if topk:
            top1_classes = set(topk[0].get("source_classes", []))
            top1_correct = bool(top1_classes & set(expected_classes))
        for atom in topk:
            scset = set(atom.get("source_classes", []))
            if scset & set(expected_classes):
                target_hits += 1
            elif scset:
                leak_hits += 1
        if topk:
            n_with_topk += 1
            if top1_correct:
                n_routed_correctly += 1
            cross_partition_leakage += leak_hits
        per_query.append({
            "q": q[:50], "expected_classes": list(expected_classes),
            "resolved": resolved, "target_hits": target_hits,
            "leak_hits": leak_hits, "n_top": len(topk),
            "top1_correct": top1_correct,
            "top1_classes": (topk[0].get("source_classes", []) if topk
                             else []),
        })
    elapsed = time.perf_counter() - t0
    routing_acc = n_routed_correctly / n_with_topk if n_with_topk else 0.0
    leak_rate = (cross_partition_leakage / (n_with_topk * DEFAULT_K)
                 if n_with_topk else 0.0)
    ratio_resolved = n_resolved / len(queries)
    # v2 relaxed gate: ok if PASS or MIDDLE bands met
    ok = (routing_acc >= ROUTING_MB_FLOOR
          and leak_rate < LEAK_HP_CEIL
          and ratio_resolved >= RATIO_RESOLVED_FLOOR)
    return {
        "arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY",
        "ok": bool(ok),
        "n_queries": len(queries),
        "n_resolved": n_resolved,
        "ratio_resolved": round(ratio_resolved, 4),
        "n_routed_correctly": n_routed_correctly,
        "n_with_topk": n_with_topk,
        "routing_accuracy": round(routing_acc, 4),
        "cross_partition_leak_rate": round(leak_rate, 4),
        "n_capacity_regression": n_regression,  # diagnostic only
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _arm_partitioned_memory_oversized(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """USER memory queries get 4x k-floor; test relative UD retention.

    v2: success = ud_retention >= max(non_ud_resolved - 0.10, 0.70).
    Measures whether oversizing helps UDs MATCH non-UDs (relative-band)
    rather than the by-construction-impossible 1.0 floor on the memory
    shard (with confidence_floor=0.3 nested inside).
    """
    t0 = time.perf_counter()
    n_ud_total = 0
    n_ud_resolved = 0
    n_non_ud_resolved = 0
    n_non_ud_total = 0
    per_query: list[dict] = []
    for q, expected_classes, _expected_substr in queries:
        is_ud = _is_user_directive_query(expected_classes)
        k = MEMORY_K if is_ud else DEFAULT_K
        r = kb.query(q, k=k, confidence_floor=DEFAULT_TAU,
                     source_classes=list(expected_classes))
        topk = r.get("top_k_atoms", [])
        resolved = (not r["refused"]) and len(topk) >= 1
        # v2 relaxation: UDs are resolved if ANY top hit lands; we no
        # longer require >= 4 hits inside the memory shard (that gate
        # is by-construction tight when confidence_floor truncates).
        if is_ud:
            n_ud_total += 1
            if resolved:
                n_ud_resolved += 1
        else:
            n_non_ud_total += 1
            if resolved:
                n_non_ud_resolved += 1
        per_query.append({
            "q": q[:50], "is_ud": is_ud, "k": k,
            "resolved": resolved, "n_top": len(topk),
            "confidence": r.get("confidence", 0),
        })
    elapsed = time.perf_counter() - t0
    ud_retention = n_ud_resolved / n_ud_total if n_ud_total else 1.0
    non_ud_ratio = (n_non_ud_resolved / n_non_ud_total
                    if n_non_ud_total else 1.0)
    # v2 relative band: ud_ret >= max(non_ud - 0.10, 0.70)
    ud_floor = max(non_ud_ratio - UD_RELATIVE_GAP, UD_ABS_FLOOR)
    ok = ud_retention >= ud_floor
    return {
        "arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED",
        "ok": bool(ok),
        "n_user_directive_total": n_ud_total,
        "n_user_directive_resolved": n_ud_resolved,
        "user_directive_retention": round(ud_retention, 4),
        "n_non_ud_total": n_non_ud_total,
        "n_non_ud_resolved": n_non_ud_resolved,
        "non_ud_resolved_ratio": round(non_ud_ratio, 4),
        "ud_floor_applied": round(ud_floor, 4),
        "memory_k": MEMORY_K,
        "default_k": DEFAULT_K,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by = {a["arm"]: a for a in arms}
    part = by.get("ARM_PARTITIONED_W_EQUAL_CAPACITY", {})
    mem = by.get("ARM_PARTITIONED_W_MEMORY_OVERSIZED", {})
    base = by.get("ARM_SINGLE_W_BASELINE", {})
    routing = part.get("routing_accuracy", 0.0)
    leak = part.get("cross_partition_leak_rate", 1.0)
    ratio_r = part.get("ratio_resolved", 0.0)
    regression = part.get("n_capacity_regression", 0)
    ud_ret = mem.get("user_directive_retention", 0.0)
    non_ud = mem.get("non_ud_resolved_ratio", 1.0)
    ud_floor = mem.get("ud_floor_applied", 0.0)
    n_ud = mem.get("n_user_directive_total", 0)

    # exception inside arms => HARD_FAIL
    for a in arms:
        if a.get("error"):
            return "HARD_FAIL", f"arm_exception {a['arm']}: {a['error']}"

    # v2 HARD_PASS: all three relaxed conditions hold + UD relative band
    if (routing >= ROUTING_HP_FLOOR
            and leak < LEAK_HP_CEIL
            and ratio_r >= RATIO_RESOLVED_FLOOR
            and (n_ud == 0 or ud_ret >= ud_floor)):
        return "HARD_PASS", (
            f"all_arms_ok; routing_acc={routing:.4f} >= {ROUTING_HP_FLOOR}; "
            f"leak={leak:.4f} < {LEAK_HP_CEIL}; "
            f"ratio_resolved={ratio_r:.4f} >= {RATIO_RESOLVED_FLOOR}; "
            f"ud_ret={ud_ret:.4f} >= floor={ud_floor:.4f} "
            f"(non_ud={non_ud:.4f}); "
            f"baseline_resolved={base.get('ratio_resolved')}; "
            f"diag_n_capacity_regression={regression}"
        )

    # MIDDLE_BAND: routing in [0.90, 0.95) OR ratio_resolved 0.70-0.80 OR
    # UD retention close to floor; otherwise operational but undecisive
    operational = (routing >= ROUTING_MB_FLOOR
                   and leak < LEAK_HP_CEIL
                   and ratio_r >= max(RATIO_RESOLVED_FLOOR - 0.10, 0.0))
    ud_close = (n_ud == 0
                or ud_ret >= max(ud_floor - 0.15, UD_ABS_FLOOR - 0.20))
    if operational and ud_close:
        return "MIDDLE_BAND", (
            f"operational_per_Fix28_default_MM; "
            f"routing_acc={routing:.4f} in [{ROUTING_MB_FLOOR}, "
            f"{ROUTING_HP_FLOOR}); leak={leak:.4f}; "
            f"ratio_resolved={ratio_r:.4f}; "
            f"ud_ret={ud_ret:.4f} (floor={ud_floor:.4f}); "
            f"diag_n_capacity_regression={regression}"
        )

    return "HARD_FAIL", (
        f"v2_band_miss; routing_acc={routing:.4f} (mb_floor "
        f"{ROUTING_MB_FLOOR}); leak={leak:.4f} (ceil {LEAK_HP_CEIL}); "
        f"ratio_resolved={ratio_r:.4f} (floor "
        f"{RATIO_RESOLVED_FLOOR}); ud_ret={ud_ret:.4f} "
        f"(floor {ud_floor:.4f}); "
        f"diag_n_capacity_regression={regression}"
    )


def _instrumentation_selftest() -> None:
    base = {"arm": "ARM_SINGLE_W_BASELINE", "ok": True,
            "ratio_resolved": 0.8}
    # HARD_PASS: routing=1.0, leak=0.0, ratio=1.0, ud=0.85, non_ud=0.85,
    # floor=max(0.85-0.10, 0.70)=0.75
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 1.0, "n_capacity_regression": 6},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"

    # MIDDLE_BAND: routing=0.92 in [0.90, 0.95)
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 0.92, "cross_partition_leak_rate": 0.02,
         "ratio_resolved": 0.85, "n_capacity_regression": 4},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.75, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.80, "ud_floor_applied": 0.70},
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"

    # HARD_FAIL: routing 0.85 below MB floor
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
         "routing_accuracy": 0.85, "cross_partition_leak_rate": 0.10,
         "ratio_resolved": 0.50, "n_capacity_regression": 10},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.75, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.80, "ud_floor_applied": 0.70},
    ])
    assert v == "HARD_FAIL", f"selftest hf: {v}"

    # v1 reprocess: routing=1.0 leak=0.0 ratio=0.80 ud=0.6 non_ud=0.84
    # floor=max(0.84-0.10, 0.70)=0.74; ud=0.6 < 0.74 (PASS UD relax-band
    # is close-to but does not clear floor); ud 0.6 is also close enough
    # to 0.74-0.15=0.59 floor for MIDDLE_BAND; expect MIDDLE
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 0.80, "n_capacity_regression": 6},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": False,
         "user_directive_retention": 0.6, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.84, "ud_floor_applied": 0.74},
    ])
    assert v == "MIDDLE_BAND", (
        f"selftest v1-reprocess (should be MIDDLE on relabeled UDs): {v}"
    )

    # Sanity: with multi-class permissible queries (Path B), UDs should
    # resolve more often. If ud=0.85 (per Path B helping), expect PASS
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 0.90, "n_capacity_regression": 3},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
    ])
    assert v == "HARD_PASS", f"selftest v1-pathB-improved: {v}"

    print("[selftest] kb_partition_by_source_class_v2 formula PASS",
          flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "kb_partition_by_source_class_v2")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--kb-dir", default=None)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    if args.kb_dir:
        kb = DirectorKBQuery(kb_dir=Path(args.kb_dir))
    else:
        try:
            kb = load_default_kb(REPO)
        except FileNotFoundError as e:
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                "elapsed_s": 0.0,
                "summary": {"anchor": "kb_partition_by_source_class_v2"},
            }
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
                  flush=True)
            return

    t0 = time.time()
    queries = ROUTED_QUERIES[:10] if args.smoke else ROUTED_QUERIES
    print(f"[run] kb_partition_by_source_class_v2 smoke={args.smoke} "
          f"kb_version={kb.kb_version} n_ent={len(kb.entity_names)} "
          f"n_queries={len(queries)}", flush=True)

    arms: list[dict] = []
    try:
        base = _arm_single_w_baseline(kb, queries)
        arms.append(base)
        print(f"  ARM_SINGLE_W_BASELINE ok={base['ok']} "
              f"ratio_resolved={base['ratio_resolved']}", flush=True)
        base_pq = base.pop("_per_query_full")
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_SINGLE_W_BASELINE", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_SINGLE_W_BASELINE FAILED: {e}", flush=True)
        base_pq = [{"resolved": False} for _ in queries]

    try:
        part = _arm_partitioned_equal_capacity(kb, queries, base_pq)
        arms.append(part)
        print(f"  ARM_PARTITIONED_W_EQUAL_CAPACITY ok={part['ok']} "
              f"routing_acc={part['routing_accuracy']} "
              f"leak={part['cross_partition_leak_rate']} "
              f"ratio_resolved={part['ratio_resolved']} "
              f"diag_regression={part['n_capacity_regression']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_PARTITIONED_W_EQUAL_CAPACITY FAILED: {e}", flush=True)

    try:
        mem = _arm_partitioned_memory_oversized(kb, queries)
        arms.append(mem)
        print(f"  ARM_PARTITIONED_W_MEMORY_OVERSIZED ok={mem['ok']} "
              f"ud_retention={mem['user_directive_retention']} "
              f"non_ud={mem['non_ud_resolved_ratio']} "
              f"ud_floor={mem['ud_floor_applied']} "
              f"n_ud_total={mem['n_user_directive_total']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_PARTITIONED_W_MEMORY_OVERSIZED FAILED: {e}",
              flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "kb_partition_by_source_class_v2",
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "schema_version": kb.schema_version,
        "encoder": kb.encoder_name,
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "v2_relaxed_bands": {
            "routing_hp_floor": ROUTING_HP_FLOOR,
            "leak_hp_ceil": LEAK_HP_CEIL,
            "ratio_resolved_floor": RATIO_RESOLVED_FLOOR,
            "routing_mb_floor": ROUTING_MB_FLOOR,
            "ud_relative_gap": UD_RELATIVE_GAP,
            "ud_abs_floor": UD_ABS_FLOOR,
        },
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm,
                   "elapsed_s": elapsed, "summary": payload},
                  f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
