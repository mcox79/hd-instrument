"""KB PARTITION BY SOURCE CLASS v1 (ANCHOR 1; INFRASTRUCTURE; 2026-06-26).

Pre-reg: preregs/2026-06-26_kb_partition_by_source_class_v1.md
Wave 3b (ships after ANCHOR 5 dual-store audit lands).

Validates the QUERY-SIDE source-class routing layer over the existing
single-W KB (atoms ALREADY tagged with source_class per hdlab/director_kb.py).
Per Principle 12, this is a non-breaking additive routing layer; no schema
modification, no physical re-shard.

ARMS (3 mandatory):
  ARM_SINGLE_W_BASELINE                   - unpartitioned baseline reference
  ARM_PARTITIONED_W_EQUAL_CAPACITY        - source_class filter; routing accuracy
  ARM_PARTITIONED_W_MEMORY_OVERSIZED      - USER memory partition 4x k-floor

SUCCESS CRITERIA (INFRASTRUCTURE tier):
  - ARM_PARTITIONED routing accuracy >= 0.90 (target source-class atoms
    appear in top-K when filter active).
  - ARM_PARTITIONED preserves all queries ARM_SINGLE resolved (no capacity
    regression).
  - ARM_PARTITIONED_W_MEMORY_OVERSIZED: 100% USER_DIRECTIVE retention.

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


# Queries with expected source_class targets.
# (question, expected_source_classes_tuple, expected_substr).
ROUTED_QUERIES: list[tuple[str, tuple[str, ...], str]] = [
    # notes (canonical)
    ("substrate director kb ingest", ("note",), "director_kb"),
    ("chain grade multi hop depth extension", ("note",), "multihop"),
    ("fleet waiting on tracker", ("note",), "fleet"),
    ("anisotropy rescue 4 arm", ("note",), "anisotropy"),
    ("eff rank diagnostic shakespeare", ("note",), "eff_rank"),
    ("phase diagram capacity sweep", ("note",), "phase_diagram"),
    ("ultrametric clustering chain grade", ("note",), "ultrametric"),
    ("standstill ack inflight inventory", ("note",), "standstill"),
    # preregs
    ("substrate director kb ingest pre reg", ("prereg",), "director_kb"),
    ("kb dual store audit pre reg", ("prereg",), "dual_store"),
    ("language trio ingest pre reg", ("prereg",), "language_trio"),
    # memory (USER directives)
    ("USER directive no busy work", ("memory",), "no_busy"),
    ("USER directive monitor armed", ("memory",), "monitor"),
    ("memory curator skill dispatch", ("memory",), "memory_curator"),
    ("fleet waiting on shared file", ("memory",), "fleet_waiting"),
    ("MEMORY index curation", ("memory",), "MEMORY"),
    # metrics (exp_*/metrics.json)
    ("exp cortex ultrametric clustering metrics", ("metrics",), "ultrametric"),
    ("exp substrate director kb ingest metrics", ("metrics",), "director_kb"),
    ("exp substrate director kb language trio metrics", ("metrics",), "language_trio"),
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


def _is_user_directive_query(expected_classes: tuple[str, ...]) -> bool:
    return "memory" in expected_classes


def _arm_single_w_baseline(kb: DirectorKBQuery, queries: list[tuple[str, tuple[str, ...], str]]) -> dict:
    """Unpartitioned baseline: no source_class filter; record what resolves."""
    t0 = time.perf_counter()
    n_resolved = 0
    per_query: list[dict] = []
    for q, expected_classes, expected_substr in queries:
        r = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU)
        resolved = (not r["refused"]) and len(r["top_k_atoms"]) >= 1
        if resolved:
            n_resolved += 1
        per_query.append({
            "q": q[:50], "resolved": resolved, "confidence": r.get("confidence", 0),
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
        "_per_query_full": per_query,  # used for regression check by ARM 2
    }


def _arm_partitioned_equal_capacity(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
    baseline_per_query: list[dict],
) -> dict:
    """Source-class-filtered query; routing accuracy + capacity preservation."""
    t0 = time.perf_counter()
    n_routed_correctly = 0
    n_resolved = 0
    n_regression = 0
    cross_partition_leakage = 0
    n_with_topk = 0
    per_query: list[dict] = []
    for i, (q, expected_classes, expected_substr) in enumerate(queries):
        r = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU,
                     source_classes=list(expected_classes))
        resolved = (not r["refused"]) and len(r["top_k_atoms"]) >= 1
        if resolved:
            n_resolved += 1
        # Regression check: baseline resolved AND this didn't
        if baseline_per_query[i]["resolved"] and not resolved:
            n_regression += 1
        # Routing accuracy: top-K source_class intersects expected
        topk = r.get("top_k_atoms", [])
        target_hits = 0
        leak_hits = 0
        for atom in topk:
            scset = set(atom.get("source_classes", []))
            if scset & set(expected_classes):
                target_hits += 1
            elif scset:  # has some other source_class
                leak_hits += 1
        if topk:
            n_with_topk += 1
            if target_hits >= 1:
                n_routed_correctly += 1
            cross_partition_leakage += leak_hits
        per_query.append({
            "q": q[:50], "expected_classes": list(expected_classes),
            "resolved": resolved, "target_hits": target_hits,
            "leak_hits": leak_hits, "n_top": len(topk),
            "top1_classes": (topk[0].get("source_classes", []) if topk else []),
        })
    elapsed = time.perf_counter() - t0
    routing_acc = n_routed_correctly / n_with_topk if n_with_topk else 0.0
    leak_rate = cross_partition_leakage / (n_with_topk * DEFAULT_K) if n_with_topk else 0.0
    ratio_resolved = n_resolved / len(queries)
    ok = routing_acc >= 0.90 and n_regression == 0
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
        "n_capacity_regression": n_regression,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _arm_partitioned_memory_oversized(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """USER memory queries get 4x k-floor; test USER_DIRECTIVE load-bearing retention."""
    t0 = time.perf_counter()
    n_ud_total = 0
    n_ud_resolved = 0
    n_non_ud_resolved = 0
    n_non_ud_total = 0
    per_query: list[dict] = []
    for q, expected_classes, expected_substr in queries:
        is_ud = _is_user_directive_query(expected_classes)
        k = MEMORY_K if is_ud else DEFAULT_K
        r = kb.query(q, k=k, confidence_floor=DEFAULT_TAU,
                     source_classes=list(expected_classes))
        topk = r.get("top_k_atoms", [])
        resolved = (not r["refused"]) and len(topk) >= 1
        if is_ud:
            n_ud_total += 1
            if resolved and len(topk) >= 4:  # memory partition requires >= 4 hits
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
    non_ud_ratio = n_non_ud_resolved / n_non_ud_total if n_non_ud_total else 1.0
    # Hard gate on USER_DIRECTIVE
    ok = ud_retention >= 1.0
    return {
        "arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED",
        "ok": bool(ok),
        "n_user_directive_total": n_ud_total,
        "n_user_directive_resolved": n_ud_resolved,
        "user_directive_retention": round(ud_retention, 4),
        "n_non_ud_total": n_non_ud_total,
        "n_non_ud_resolved": n_non_ud_resolved,
        "non_ud_resolved_ratio": round(non_ud_ratio, 4),
        "memory_k": MEMORY_K,
        "default_k": DEFAULT_K,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by = {a["arm"]: a for a in arms}
    if not all(a.get("ok") for a in arms if a["arm"] != "ARM_SINGLE_W_BASELINE"):
        bad = [a["arm"] for a in arms
               if a["arm"] != "ARM_SINGLE_W_BASELINE" and not a.get("ok")]
        return "HARD_FAIL", f"one_or_more_arms_failed: {','.join(bad)}"
    part = by.get("ARM_PARTITIONED_W_EQUAL_CAPACITY", {})
    mem = by.get("ARM_PARTITIONED_W_MEMORY_OVERSIZED", {})
    base = by.get("ARM_SINGLE_W_BASELINE", {})
    routing = part.get("routing_accuracy", 0.0)
    regression = part.get("n_capacity_regression", 0)
    ud_ret = mem.get("user_directive_retention", 1.0)
    n_ud = mem.get("n_user_directive_total", 0)
    if n_ud > 0 and ud_ret < 1.0:
        return "HARD_FAIL", (
            f"USER_DIRECTIVE retention {ud_ret:.4f} < 1.0; load-bearing violation"
        )
    if regression > 0:
        return "HARD_FAIL", (
            f"capacity_regression={regression}; ARM_PARTITIONED lost queries "
            f"ARM_SINGLE resolved"
        )
    if routing >= 0.95:
        return "HARD_PASS", (
            f"all_arms_ok; routing_acc={routing:.4f} >= 0.95; "
            f"capacity_regression=0; user_directive_retention={ud_ret:.4f}; "
            f"baseline_resolved={base.get('ratio_resolved')}"
        )
    if routing >= 0.90:
        return "MIDDLE_BAND", (
            f"all_arms_ok_operational; routing_acc={routing:.4f} in [0.90, 0.95); "
            f"capacity_regression=0; user_directive_retention={ud_ret:.4f}; "
            f"partitioning_operational_per_Fix28_default_MM"
        )
    return "HARD_FAIL", (
        f"routing_acc={routing:.4f} < 0.90; partition leakage too high"
    )


def _instrumentation_selftest() -> None:
    base = {"arm": "ARM_SINGLE_W_BASELINE", "ok": True, "ratio_resolved": 0.8}
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 0.98, "n_capacity_regression": 0},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 1.0, "n_user_directive_total": 5},
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 0.92, "n_capacity_regression": 0},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 1.0, "n_user_directive_total": 5},
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
         "routing_accuracy": 0.6, "n_capacity_regression": 3},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 1.0, "n_user_directive_total": 5},
    ])
    assert v == "HARD_FAIL", f"selftest hf: {v}"
    # USER directive loss = HARD_FAIL
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 0.99, "n_capacity_regression": 0},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": False,
         "user_directive_retention": 0.8, "n_user_directive_total": 5},
    ])
    assert v == "HARD_FAIL", f"selftest hf-ud: {v}"
    print("[selftest] kb_partition_by_source_class_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "kb_partition_by_source_class_v1")


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
            payload = {"verdict": "HARD_FAIL", "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                       "elapsed_s": 0.0, "summary": {"anchor": "kb_partition_by_source_class_v1"}}
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}", flush=True)
            return

    t0 = time.time()
    queries = ROUTED_QUERIES[:10] if args.smoke else ROUTED_QUERIES
    print(f"[run] kb_partition_by_source_class_v1 smoke={args.smoke} "
          f"kb_version={kb.kb_version} n_ent={len(kb.entity_names)} "
          f"n_queries={len(queries)}", flush=True)

    arms: list[dict] = []
    try:
        base = _arm_single_w_baseline(kb, queries)
        arms.append(base)
        print(f"  ARM_SINGLE_W_BASELINE ok={base['ok']} ratio_resolved={base['ratio_resolved']}",
              flush=True)
        base_pq = base.pop("_per_query_full")
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_SINGLE_W_BASELINE", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_SINGLE_W_BASELINE FAILED: {e}", flush=True)
        base_pq = [{"resolved": False} for _ in queries]

    try:
        part = _arm_partitioned_equal_capacity(kb, queries, base_pq)
        arms.append(part)
        print(f"  ARM_PARTITIONED_W_EQUAL_CAPACITY ok={part['ok']} "
              f"routing_acc={part['routing_accuracy']} regression={part['n_capacity_regression']}",
              flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_PARTITIONED_W_EQUAL_CAPACITY FAILED: {e}", flush=True)

    try:
        mem = _arm_partitioned_memory_oversized(kb, queries)
        arms.append(mem)
        print(f"  ARM_PARTITIONED_W_MEMORY_OVERSIZED ok={mem['ok']} "
              f"ud_retention={mem['user_directive_retention']} "
              f"n_ud_total={mem['n_user_directive_total']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_PARTITIONED_W_MEMORY_OVERSIZED FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "kb_partition_by_source_class_v1",
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "schema_version": kb.schema_version,
        "encoder": kb.encoder_name,
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
                   "summary": payload}, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
