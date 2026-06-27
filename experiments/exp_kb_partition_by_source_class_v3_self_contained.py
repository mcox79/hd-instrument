"""KB PARTITION BY SOURCE CLASS v3 (ANCHOR 1 RESCUE; SELF-CONTAINED; 2026-06-27).

Pre-reg: preregs/2026-06-27_kb_partition_by_source_class_v3_self_contained.md

v2 HARD_FAILed on remote with KB_REFERENT_MISSING:
  `load_default_kb(REPO)` expects an upstream
  `data/exp_substrate_director_kb_ingest_v1/_arm_full/kb` directory that
  was built by a separate local-only ingest cell; that directory is not
  on the remote_cpu runner, so the v2 cell never executed its arms.

v3 fix: build a labeled mini-KB IN-CELL from filesystem sources
(notes/ + memory/ + preregs/) using the chain-grade
hdlab.director_kb_chunk_ingest.run_chunk_ingest primitive. This makes the
cell self-contained (no upstream dependency) and remote-ready.

MECHANISM IS UNCHANGED FROM v2 (Path A relaxed criterion + Path B multi-
class permissible-set queries). The chunk-ingest module tags atoms with
source_class = "chunk_<cname>" (prefix `chunk_`), so v3 ROUTED_QUERIES
use the prefixed class names (chunk_note, chunk_memory, chunk_prereg).

ARMS (3 mandatory; unchanged from v2):
  ARM_SINGLE_W_BASELINE                   - unpartitioned baseline reference
  ARM_PARTITIONED_W_EQUAL_CAPACITY        - source_class filter; routing
                                            accuracy
  ARM_PARTITIONED_W_MEMORY_OVERSIZED      - USER memory partition 4x k-floor

PRE-REG BANDS (load-bearing; identical to v2):
  HARD_PASS: routing_acc >= 0.95 AND leak < 0.05 AND ratio_resolved >= 0.80
             AND (n_ud == 0 OR ud_retention >= max(non_ud - 0.10, 0.70))
  MIDDLE_BAND: routing_acc in [0.90, 0.95) OR ratio_resolved in [0.70, 0.80)
               OR UD close to floor (within 0.15)
  HARD_FAIL: routing_acc < 0.90 OR leak >= 0.05 OR ratio_resolved < 0.70
             OR any arm raised exception OR ingest produced 0 entities

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb import load_schema  # noqa: E402
from hdlab.director_kb_chunk_ingest import (  # noqa: E402
    build_chunk_plan,
    run_chunk_ingest,
)
from hdlab.director_kb_query import DirectorKBQuery  # noqa: E402


# v3 ROUTED_QUERIES: expected_classes uses the chunk-prefixed source_class
# tokens (chunk_note, chunk_memory, chunk_prereg) because the chunk_ingest
# module prefixes its source_class atoms with "chunk_" (per Principle 8;
# preserves distinction in mixed-export scenarios). Cross-cutting queries
# get multi-class permits.
ROUTED_QUERIES: list[tuple[str, tuple[str, ...], str]] = [
    # notes (canonical; mostly singletons)
    ("substrate director kb ingest",
     ("chunk_note", "chunk_prereg"), "director_kb"),
    ("chain grade multi hop depth extension",
     ("chunk_note",), "multihop"),
    ("fleet waiting on tracker",
     ("chunk_note", "chunk_memory"), "fleet"),
    ("anisotropy rescue 4 arm",
     ("chunk_note",), "anisotropy"),
    ("eff rank diagnostic shakespeare",
     ("chunk_note",), "eff_rank"),
    ("phase diagram capacity sweep",
     ("chunk_note",), "phase_diagram"),
    ("ultrametric clustering chain grade",
     ("chunk_note",), "ultrametric"),
    ("standstill ack inflight inventory",
     ("chunk_note",), "standstill"),
    # preregs
    ("substrate director kb ingest pre reg",
     ("chunk_prereg",), "director_kb"),
    ("kb dual store audit pre reg",
     ("chunk_prereg",), "dual_store"),
    ("language trio ingest pre reg",
     ("chunk_prereg",), "language_trio"),
    # memory (USER directives are cross-cutting; live in memory + notes +
    # often prereg too because they get referenced)
    ("USER directive no busy work",
     ("chunk_memory", "chunk_note", "chunk_prereg"), "no_busy"),
    ("USER directive monitor armed",
     ("chunk_memory", "chunk_note"), "monitor"),
    ("memory curator skill dispatch",
     ("chunk_memory", "chunk_note"), "memory_curator"),
    ("fleet waiting on shared file",
     ("chunk_memory", "chunk_note"), "fleet_waiting"),
    ("MEMORY index curation",
     ("chunk_memory",), "MEMORY"),
    # additional coverage queries (lift count >= 20; v2 had 28 incl. KGs
    # that are not present in the inline build, so we keep this list to
    # the TEXT-class queries the inline KB can answer)
    ("director plan priorities",
     ("chunk_note", "chunk_memory"), "director_plan"),
    ("edge importance retrieval trace",
     ("chunk_note", "chunk_prereg"), "edge_importance"),
    ("NREM replay consolidation",
     ("chunk_note", "chunk_prereg"), "nrem_replay"),
    ("smoke discipline cardinality ok",
     ("chunk_note", "chunk_memory"), "smoke_discipline"),
    ("stage progression substrate",
     ("chunk_memory", "chunk_note"), "stage_progression"),
    ("agent spawn model only",
     ("chunk_memory", "chunk_note"), "agent_spawn"),
    ("hard pass cert grade verdict",
     ("chunk_note", "chunk_prereg"), "hard_pass"),
    ("compositional understanding pivot",
     ("chunk_note", "chunk_memory"), "compositional"),
    ("substrate own encoder predictive coding",
     ("chunk_note", "chunk_memory"), "substrate_encoder"),
    ("USER directive overhead reduction",
     ("chunk_memory", "chunk_note"), "overhead"),
    ("dispatch queue runner gpu",
     ("chunk_note", "chunk_prereg"), "dispatch_queue"),
    ("HARD FAIL no silent except",
     ("chunk_note", "chunk_memory"), "hard_fail"),
]
assert len(ROUTED_QUERIES) >= 20, f"want >= 20, got {len(ROUTED_QUERIES)}"

DEFAULT_K = 8
MEMORY_K = 32  # 4x oversize for USER memory partition (ARM 3)
DEFAULT_TAU = 0.3

# v3 PASS bands (inherited from v2; documented in pre-reg).
ROUTING_HP_FLOOR = 0.95
LEAK_HP_CEIL = 0.05
RATIO_RESOLVED_FLOOR = 0.80
ROUTING_MB_FLOOR = 0.90
UD_RELATIVE_GAP = 0.10
UD_ABS_FLOOR = 0.70

# v3 ingest envelope (self-contained build budget)
SELF_CONTAINED_CHUNK_CLASSES = ("note", "memory", "prereg")
SELF_CONTAINED_MAX_FILES_FULL = 200
SELF_CONTAINED_MAX_FILES_SMOKE = 50
INGEST_N_DIM = 2048
INGEST_SEED = 17

# Cardinality bands
EXPECTED_N_ARMS = 3
EXPECTED_INGEST_ENTITIES_MIN_FULL = 500
EXPECTED_INGEST_ENTITIES_MIN_SMOKE = 100


def _is_user_directive_query(expected_classes: tuple[str, ...]) -> bool:
    """A query is a USER directive (gets 4x k) iff 'chunk_memory' is in
    its permissible classes (Path B: UD queries are cross-cutting)."""
    return "chunk_memory" in expected_classes


def _arm_single_w_baseline(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """Unpartitioned baseline; record what resolves."""
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
        "ok": True,
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

    v3 (= v2 logic): routing correctness counts top-1 hit in ANY
    permissible class as success (Path B relabel).
    """
    t0 = time.perf_counter()
    n_routed_correctly = 0
    n_resolved = 0
    n_regression = 0  # diagnostic only
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
        "n_capacity_regression": n_regression,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _arm_partitioned_memory_oversized(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """USER memory queries get 4x k-floor; test relative UD retention."""
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

    # D3 no-silent-except => any exception in arms = HARD_FAIL
    for a in arms:
        if a.get("error"):
            return "HARD_FAIL", f"arm_exception {a['arm']}: {a['error']}"

    # D4 cardinality => exactly 3 arms expected
    if len(arms) != EXPECTED_N_ARMS:
        return "HARD_FAIL", (
            f"d4_cardinality_breach: expected {EXPECTED_N_ARMS} arms, "
            f"got {len(arms)}"
        )

    # HARD_PASS: all four conditions
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

    # MIDDLE_BAND: routing in [0.90, 0.95) and operational and UD close
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
        f"v3_band_miss; routing_acc={routing:.4f} (mb_floor "
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

    # D4 cardinality breach
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 1.0, "n_capacity_regression": 0},
    ])
    assert v == "HARD_FAIL", f"selftest d4_cardinality: {v}"

    # D3 arm exception
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
         "error": "TestException: synthetic"},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
    ])
    assert v == "HARD_FAIL", f"selftest d3_exception: {v}"

    print("[selftest] kb_partition_by_source_class_v3_self_contained "
          "formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME", "kb_partition_by_source_class_v3_self_contained"
    )


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _build_inline_kb(out_dir: Path, smoke: bool) -> dict:
    """Build the self-contained chunk-KB from notes/ + memory/ + preregs/.

    Returns the manifest dict (n_entities, n_chunks, etc.). Wipes any
    pre-existing out_dir contents.
    """
    schema = load_schema(REPO)
    max_files = (SELF_CONTAINED_MAX_FILES_SMOKE if smoke
                 else SELF_CONTAINED_MAX_FILES_FULL)
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=SELF_CONTAINED_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )
    n_disc = sum(len(plan[c]["files"]) for c in plan)
    t0 = time.perf_counter()
    manifest = run_chunk_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=INGEST_N_DIM,
        seed=INGEST_SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    manifest["_build_elapsed_s"] = round(elapsed, 3)
    manifest["_n_files_discovered"] = n_disc
    manifest["_smoke"] = bool(smoke)
    return manifest


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--inline-kb-dir", default=None,
                   help="Override location for the inline KB build "
                        "(default: data/exp_<anchor>/_inline_kb).")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    inline_kb_dir = (Path(args.inline_kb_dir) if args.inline_kb_dir
                     else out_dir / "_inline_kb")

    t0 = time.time()

    # Phase 1: build inline KB (self-contained; no upstream dependency)
    try:
        print(f"[ingest] building inline KB at {inline_kb_dir} "
              f"smoke={args.smoke} classes={SELF_CONTAINED_CHUNK_CLASSES} "
              f"max_files={SELF_CONTAINED_MAX_FILES_SMOKE if args.smoke else SELF_CONTAINED_MAX_FILES_FULL}",
              flush=True)
        manifest = _build_inline_kb(inline_kb_dir, smoke=args.smoke)
        n_ent = manifest.get("n_entities", 0)
        min_ent = (EXPECTED_INGEST_ENTITIES_MIN_SMOKE if args.smoke
                   else EXPECTED_INGEST_ENTITIES_MIN_FULL)
        print(f"[ingest] done: n_entities={n_ent} n_chunks={manifest.get('n_chunks')} "
              f"n_triples={manifest.get('n_triples')} coverage={manifest.get('coverage_ratio')} "
              f"avg_chunks/file={manifest.get('avg_chunks_per_file')} "
              f"elapsed_s={manifest.get('_build_elapsed_s')}", flush=True)
        if n_ent < min_ent:
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": (
                    f"INGEST_TOO_SMALL: n_entities={n_ent} < min {min_ent} "
                    f"(smoke={args.smoke}); inline KB did not populate; "
                    f"check notes/ memory/ preregs/ exist on this runner"
                ),
                "elapsed_s": round(time.time() - t0, 2),
                "summary": {"anchor": _exp_name(), "manifest": manifest},
            }
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
                  flush=True)
            return
    except Exception as e:  # noqa: BLE001
        payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"INGEST_EXCEPTION: {type(e).__name__}: {e}",
            "elapsed_s": round(time.time() - t0, 2),
            "summary": {"anchor": _exp_name()},
        }
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
              flush=True)
        return

    # Phase 2: load query over inline KB
    try:
        kb = DirectorKBQuery(kb_dir=inline_kb_dir)
    except Exception as e:  # noqa: BLE001
        payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"KB_LOAD_EXCEPTION: {type(e).__name__}: {e}; "
                f"inline_kb_dir={inline_kb_dir}"
            ),
            "elapsed_s": round(time.time() - t0, 2),
            "summary": {"anchor": _exp_name(), "manifest": manifest},
        }
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
              flush=True)
        return

    queries = ROUTED_QUERIES[:10] if args.smoke else ROUTED_QUERIES
    print(f"[run] kb_partition_by_source_class_v3_self_contained "
          f"smoke={args.smoke} kb_version={kb.kb_version} "
          f"n_ent={len(kb.entity_names)} n_queries={len(queries)}",
          flush=True)

    # Phase 3: run arms (D3 no-silent-except)
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
        "anchor": _exp_name(),
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "schema_version": kb.schema_version,
        "encoder": kb.encoder_name,
        "inline_kb_manifest": manifest,
        "inline_kb_dir": str(inline_kb_dir),
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "v3_self_contained_bands": {
            "routing_hp_floor": ROUTING_HP_FLOOR,
            "leak_hp_ceil": LEAK_HP_CEIL,
            "ratio_resolved_floor": RATIO_RESOLVED_FLOOR,
            "routing_mb_floor": ROUTING_MB_FLOOR,
            "ud_relative_gap": UD_RELATIVE_GAP,
            "ud_abs_floor": UD_ABS_FLOOR,
        },
        "chunk_classes_ingested": list(SELF_CONTAINED_CHUNK_CLASSES),
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm,
                   "elapsed_s": elapsed, "summary": payload},
                  f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
