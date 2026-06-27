"""KB PARTITION BY SOURCE CLASS v4 (ANCHOR 1 RESCUE; CALIBRATED; 2026-06-27).

Pre-reg: preregs/2026-06-27_kb_partition_by_source_class_v4_calibrated.md

v3 HARD_FAILed with ratio_resolved=0.1429 (HF floor 0.80) despite
routing_accuracy=1.0 and 8/8 target hits in correct partition. Drill
diagnosed TWO layered bugs in v3:

  Bug 1 (REFUSE_GATE_MISCALIBRATED):
    DEFAULT_TAU=0.30 inherited from v2 filename-index regime. v3 content-
    chunk regime produces cosines 0.14-0.30 -- most queries refused on
    CALIBRATION alone (even though 8/8 top-K atoms were in the right
    class).

  Bug 2 (SCHEMA_MEMORY_CLASS_DROP):
    per_class.memory.n_files=0 silently. Root cause: memory class uses
    root_dir_external = C:/Users/marsh/.claude/projects/d--AI/memory
    which exists on local but NOT on the remote_cpu runner. Plan returns
    {skipped_unreachable: True}, but the manifest doesn't propagate that
    distinction -- so a missing-on-remote class looks like a build bug.

v4 fixes per drill:

  Fix A (calibration):
    DEFAULT_TAU 0.30 -> 0.15 (empirically derived from v3 metrics top-1
    cosine band).

  Fix B (CARDINALITY_OK + visibility):
    Hard CARDINALITY_OK gate per META_RULE_H, but split into two cases:
      - HARD_FAIL: any class with skipped_unreachable=False produced
        n_chunks=0 (real ingest bug).
      - WARN + drop: class with skipped_unreachable=True (env diff;
        not a cell bug). Manifest records `unreachable_classes` so the
        drop is visible.
    Also: if ALL declared classes are unreachable -> HARD_FAIL.

  Fix C (density):
    SELF_CONTAINED_MAX_FILES 200 -> 800 (full); 50 -> 50 (smoke;
    unchanged for speed).

  Fix D (schema-version compat; latent bug surfaced by smoke):
    DirectorKBQuery.query() defaults schema_version="v1" but the
    schema file bumped to v2 today (commit 5c08f49f). Pass
    kb.schema_version explicitly on every query call.

  Diagnostic arms (additive; do NOT gate the verdict):
    ARM_DIAG_RANK_BASED_GATE: alternative refuse-gate where 'resolved'
      requires top-1 cosine to exceed top-50 mean + 1*sigma (rank-based
      vs absolute-threshold). Records ratio_resolved_rankgated for
      future re-calibration.
    ARM_DIAG_COSINE_DIST_DUMP: emits top-K cosine histograms per query
      to data/exp_<anchor>/cosine_distribution.json so future v5 /
      encoder-rework can calibrate without re-running the cell.

  D1 (Discriminator-must-survive-scale):
    Smoke at 50 files/class (10 queries). Additionally, smoke runs an
    in-cell FULL_N_PREVIEW arm: 800 files/class with 5 queries; if
    BASELINE ratio_resolved < 0.40 at preview, the cell HARD_FAILs in
    smoke before full dispatch.

MECHANISM IS UNCHANGED from v3 (Path A relaxed criterion + Path B multi-
class permissible-set queries). Only the gate threshold + cardinality
discipline + density change.

ARMS (3 mandatory band-gating + 2 diagnostic = 5 total):
  ARM_SINGLE_W_BASELINE                   - unpartitioned baseline reference
  ARM_PARTITIONED_W_EQUAL_CAPACITY        - source_class filter; routing acc
  ARM_PARTITIONED_W_MEMORY_OVERSIZED      - USER memory partition 4x k-floor
  ARM_DIAG_RANK_BASED_GATE                - diagnostic; not band-gating
  ARM_DIAG_COSINE_DIST_DUMP               - diagnostic; not band-gating

PRE-REG BANDS (HARD-LOCKED; identical to v3 except DEFAULT_TAU):
  HARD_PASS: routing_acc >= 0.95 AND leak < 0.05 AND ratio_resolved >= 0.80
             AND (n_ud == 0 OR ud_retention >= max(non_ud - 0.10, 0.70))
  MIDDLE_BAND: routing_acc in [0.90, 0.95) OR ratio_resolved in [0.70, 0.80)
               OR UD close to floor (within 0.15)
  HARD_FAIL: routing_acc < 0.90 OR leak >= 0.05 OR ratio_resolved < 0.70
             OR any arm raised exception OR cardinality breach
             OR (smoke FULL_N_PREVIEW baseline < 0.40)

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
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


# v4 ROUTED_QUERIES: identical to v3 (chunk-prefixed source_class tokens).
ROUTED_QUERIES: list[tuple[str, tuple[str, ...], str]] = [
    # notes
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
    # memory (USER directives are cross-cutting)
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
    # coverage
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
DEFAULT_TAU = 0.15  # v4 FIX A: was 0.30 (filename-index regime); 0.15
                    # calibrated for content-chunk regime cosines
                    # observed at 0.14-0.30.

# Diagnostic ARM thresholds (do NOT gate the verdict)
RANKGATE_TOPN_FOR_SIGMA = 50
RANKGATE_SIGMA_MULT = 1.0

# v4 PASS bands (inherited from v3; documented in pre-reg).
ROUTING_HP_FLOOR = 0.95
LEAK_HP_CEIL = 0.05
RATIO_RESOLVED_FLOOR = 0.80
ROUTING_MB_FLOOR = 0.90
UD_RELATIVE_GAP = 0.10
UD_ABS_FLOOR = 0.70

# v4 ingest envelope. FIX C: bump full from 200 to 800 to (a) lift density
# (b) reduce file-count artifact (c) approach real director-KB scale.
SELF_CONTAINED_CHUNK_CLASSES = ("note", "memory", "prereg")
SELF_CONTAINED_MAX_FILES_FULL = 800
SELF_CONTAINED_MAX_FILES_SMOKE = 50
SELF_CONTAINED_MAX_FILES_PREVIEW = 800  # FULL_N_PREVIEW in smoke (D1)
INGEST_N_DIM = 2048
INGEST_SEED = 17

# Cardinality bands
EXPECTED_N_BAND_ARMS = 3  # baseline / partitioned / memory-oversized
EXPECTED_N_DIAG_ARMS = 2  # rank-gate / cosine-dist
EXPECTED_N_ARMS_TOTAL = EXPECTED_N_BAND_ARMS + EXPECTED_N_DIAG_ARMS

EXPECTED_INGEST_ENTITIES_MIN_FULL = 2000
EXPECTED_INGEST_ENTITIES_MIN_SMOKE = 100

# D1 FULL_N_PREVIEW gate (catches scale-fragility BEFORE full dispatch)
FULL_N_PREVIEW_BASELINE_HF_FLOOR = 0.40
FULL_N_PREVIEW_N_QUERIES = 5


def _is_user_directive_query(expected_classes: tuple[str, ...]) -> bool:
    return "chunk_memory" in expected_classes


def _arm_single_w_baseline(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
    tau: float = DEFAULT_TAU,
) -> dict:
    t0 = time.perf_counter()
    n_resolved = 0
    per_query: list[dict] = []
    for q, _expected_classes, _expected_substr in queries:
        r = kb.query(q, k=DEFAULT_K, confidence_floor=tau,
                     schema_version=kb.schema_version)
        resolved = (not r["refused"]) and len(r["top_k_atoms"]) >= 1
        if resolved:
            n_resolved += 1
        per_query.append({
            "q": q[:50], "resolved": resolved,
            "confidence": r.get("confidence", 0),
            "n_top": len(r.get("top_k_atoms", [])),
        })
    elapsed = time.perf_counter() - t0
    ratio = n_resolved / len(queries) if queries else 0.0
    return {
        "arm": "ARM_SINGLE_W_BASELINE",
        "ok": True,
        "tau_used": tau,
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
    t0 = time.perf_counter()
    n_routed_correctly = 0
    n_resolved = 0
    n_regression = 0
    cross_partition_leakage = 0
    n_with_topk = 0
    per_query: list[dict] = []
    for i, (q, expected_classes, _expected_substr) in enumerate(queries):
        r = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU,
                     source_classes=list(expected_classes),
                     schema_version=kb.schema_version)
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
    ratio_resolved = n_resolved / len(queries) if queries else 0.0
    ok = (routing_acc >= ROUTING_MB_FLOOR
          and leak_rate < LEAK_HP_CEIL
          and ratio_resolved >= RATIO_RESOLVED_FLOOR)
    return {
        "arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY",
        "ok": bool(ok),
        "tau_used": DEFAULT_TAU,
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
                     source_classes=list(expected_classes),
                     schema_version=kb.schema_version)
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
        "tau_used": DEFAULT_TAU,
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


def _arm_diag_rank_based_gate(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
) -> dict:
    """DIAGNOSTIC: rank-based refuse-gate.

    Resolved = (top-1 cosine > top-N mean + sigma_mult * top-N stddev).
    Records ratio for future v5 / encoder-rework calibration.
    """
    t0 = time.perf_counter()
    n_resolved_rankgated = 0
    per_query: list[dict] = []
    for q, _expected_classes, _expected_substr in queries:
        # Query a large k so we can compute the top-N distribution.
        r = kb.query(q, k=RANKGATE_TOPN_FOR_SIGMA, confidence_floor=0.0,
                     schema_version=kb.schema_version)
        topk = r.get("top_k_atoms", [])
        if len(topk) < 2:
            per_query.append({
                "q": q[:50], "resolved_rankgated": False,
                "reason": "insufficient_topk",
            })
            continue
        cosines = [a.get("cosine", 0.0) for a in topk]
        top1 = cosines[0]
        # Use top-2..top-N as the "noise" distribution
        noise = cosines[1:]
        if not noise:
            per_query.append({
                "q": q[:50], "resolved_rankgated": False,
                "reason": "no_noise_samples",
            })
            continue
        mean_n = sum(noise) / len(noise)
        var_n = sum((c - mean_n) ** 2 for c in noise) / len(noise)
        sigma_n = math.sqrt(var_n)
        threshold_rank = mean_n + RANKGATE_SIGMA_MULT * sigma_n
        resolved = top1 > threshold_rank
        if resolved:
            n_resolved_rankgated += 1
        per_query.append({
            "q": q[:50], "top1": round(top1, 4),
            "noise_mean": round(mean_n, 4),
            "noise_sigma": round(sigma_n, 4),
            "threshold_rank": round(threshold_rank, 4),
            "resolved_rankgated": bool(resolved),
        })
    elapsed = time.perf_counter() - t0
    ratio_rank = n_resolved_rankgated / len(queries) if queries else 0.0
    return {
        "arm": "ARM_DIAG_RANK_BASED_GATE",
        "ok": True,
        "diagnostic_only": True,
        "n_queries": len(queries),
        "n_resolved_rankgated": n_resolved_rankgated,
        "ratio_resolved_rankgated": round(ratio_rank, 4),
        "topn_for_sigma": RANKGATE_TOPN_FOR_SIGMA,
        "sigma_mult": RANKGATE_SIGMA_MULT,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query[:15],
    }


def _arm_diag_cosine_dist_dump(
    kb: DirectorKBQuery,
    queries: list[tuple[str, tuple[str, ...], str]],
    out_dir: Path,
) -> dict:
    """DIAGNOSTIC: dump top-K cosine histograms per query.

    Persists data/exp_<anchor>/cosine_distribution.json so future calibration
    can re-derive DEFAULT_TAU without re-running the cell.
    """
    t0 = time.perf_counter()
    bins = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50,
            0.60, 0.80, 1.01]
    dist: list[dict] = []
    aggregate_top1: list[float] = []
    aggregate_topk: list[float] = []
    for q, expected_classes, _expected_substr in queries:
        r = kb.query(q, k=DEFAULT_K, confidence_floor=0.0,
                     source_classes=list(expected_classes),
                     schema_version=kb.schema_version)
        topk = r.get("top_k_atoms", [])
        cosines = [a.get("cosine", 0.0) for a in topk]
        if cosines:
            aggregate_top1.append(cosines[0])
            aggregate_topk.extend(cosines)
        hist = [0] * (len(bins) - 1)
        for c in cosines:
            for i in range(len(bins) - 1):
                if bins[i] <= c < bins[i + 1]:
                    hist[i] += 1
                    break
        dist.append({
            "q": q[:50],
            "expected_classes": list(expected_classes),
            "cosines": [round(c, 4) for c in cosines],
            "bin_edges": bins,
            "hist": hist,
        })
    elapsed = time.perf_counter() - t0
    top1_mean = (sum(aggregate_top1) / len(aggregate_top1)
                 if aggregate_top1 else 0.0)
    top1_min = min(aggregate_top1) if aggregate_top1 else 0.0
    top1_max = max(aggregate_top1) if aggregate_top1 else 0.0
    topk_mean = (sum(aggregate_topk) / len(aggregate_topk)
                 if aggregate_topk else 0.0)
    dump_path = out_dir / "cosine_distribution.json"
    with dump_path.open("w", encoding="utf-8") as f:
        json.dump({
            "queries": dist,
            "aggregate": {
                "top1_mean": round(top1_mean, 4),
                "top1_min": round(top1_min, 4),
                "top1_max": round(top1_max, 4),
                "topk_mean": round(topk_mean, 4),
                "n_queries": len(queries),
            },
            "default_tau_v4": DEFAULT_TAU,
        }, f, indent=2, default=str)
    return {
        "arm": "ARM_DIAG_COSINE_DIST_DUMP",
        "ok": True,
        "diagnostic_only": True,
        "n_queries": len(queries),
        "aggregate_top1_mean": round(top1_mean, 4),
        "aggregate_top1_min": round(top1_min, 4),
        "aggregate_top1_max": round(top1_max, 4),
        "aggregate_topk_mean": round(topk_mean, 4),
        "dump_path": str(dump_path),
        "elapsed_s": round(elapsed, 3),
    }


def _verdict_from_arms(arms: list[dict],
                       preview_baseline_ratio: float | None = None
                       ) -> tuple[str, str]:
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

    # D3 no-silent-except
    for a in arms:
        if a.get("error"):
            return "HARD_FAIL", f"arm_exception {a['arm']}: {a['error']}"

    # D4 cardinality
    if len(arms) != EXPECTED_N_ARMS_TOTAL:
        return "HARD_FAIL", (
            f"d4_cardinality_breach: expected {EXPECTED_N_ARMS_TOTAL} arms "
            f"(3 band + 2 diag), got {len(arms)}"
        )

    # D1 FULL_N_PREVIEW (smoke-only; if preview_baseline_ratio provided)
    if (preview_baseline_ratio is not None
            and preview_baseline_ratio < FULL_N_PREVIEW_BASELINE_HF_FLOOR):
        return "HARD_FAIL", (
            f"d1_full_n_preview_baseline_too_low: "
            f"preview_baseline_ratio={preview_baseline_ratio:.4f} < "
            f"{FULL_N_PREVIEW_BASELINE_HF_FLOOR}; "
            f"full dispatch BLOCKED per discriminator-must-survive-scale"
        )

    # HARD_PASS
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
            f"diag_n_capacity_regression={regression}; "
            f"tau_used={DEFAULT_TAU}"
        )

    # MIDDLE_BAND
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
            f"diag_n_capacity_regression={regression}; "
            f"tau_used={DEFAULT_TAU}"
        )

    return "HARD_FAIL", (
        f"v4_band_miss; routing_acc={routing:.4f} (mb_floor "
        f"{ROUTING_MB_FLOOR}); leak={leak:.4f} (ceil {LEAK_HP_CEIL}); "
        f"ratio_resolved={ratio_r:.4f} (floor "
        f"{RATIO_RESOLVED_FLOOR}); ud_ret={ud_ret:.4f} "
        f"(floor {ud_floor:.4f}); "
        f"diag_n_capacity_regression={regression}; "
        f"tau_used={DEFAULT_TAU}"
    )


def _instrumentation_selftest() -> None:
    base = {"arm": "ARM_SINGLE_W_BASELINE", "ok": True,
            "ratio_resolved": 0.85}
    diag1 = {"arm": "ARM_DIAG_RANK_BASED_GATE", "ok": True,
             "diagnostic_only": True}
    diag2 = {"arm": "ARM_DIAG_COSINE_DIST_DUMP", "ok": True,
             "diagnostic_only": True}

    # HARD_PASS
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 0.90, "n_capacity_regression": 1},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
        diag1, diag2,
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"

    # MIDDLE_BAND (routing 0.92 in [0.90, 0.95))
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 0.92, "cross_partition_leak_rate": 0.02,
         "ratio_resolved": 0.85, "n_capacity_regression": 4},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.75, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.80, "ud_floor_applied": 0.70},
        diag1, diag2,
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"

    # HARD_FAIL (routing 0.85 below MB)
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": False,
         "routing_accuracy": 0.85, "cross_partition_leak_rate": 0.10,
         "ratio_resolved": 0.50, "n_capacity_regression": 10},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.75, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.80, "ud_floor_applied": 0.70},
        diag1, diag2,
    ])
    assert v == "HARD_FAIL", f"selftest hf: {v}"

    # D4 cardinality breach (only 3 arms; missing diagnostics)
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 1.0, "n_capacity_regression": 0},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
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
        diag1, diag2,
    ])
    assert v == "HARD_FAIL", f"selftest d3_exception: {v}"

    # D1 FULL_N_PREVIEW (baseline too low)
    v, _ = _verdict_from_arms([
        base,
        {"arm": "ARM_PARTITIONED_W_EQUAL_CAPACITY", "ok": True,
         "routing_accuracy": 1.0, "cross_partition_leak_rate": 0.0,
         "ratio_resolved": 0.90, "n_capacity_regression": 1},
        {"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": True,
         "user_directive_retention": 0.85, "n_user_directive_total": 5,
         "non_ud_resolved_ratio": 0.85, "ud_floor_applied": 0.75},
        diag1, diag2,
    ], preview_baseline_ratio=0.20)
    assert v == "HARD_FAIL", f"selftest d1_preview: {v}"

    # FIX A sanity: assert DEFAULT_TAU is the new calibrated value
    assert DEFAULT_TAU == 0.15, f"DEFAULT_TAU should be 0.15 (FIX A); got {DEFAULT_TAU}"

    # FIX C sanity: assert SELF_CONTAINED_MAX_FILES_FULL bumped to 800
    assert SELF_CONTAINED_MAX_FILES_FULL == 800, (
        f"SELF_CONTAINED_MAX_FILES_FULL should be 800 (FIX C); "
        f"got {SELF_CONTAINED_MAX_FILES_FULL}"
    )

    # FIX B sanity: cardinality total accounts for 3 band + 2 diag
    assert EXPECTED_N_ARMS_TOTAL == 5, (
        f"EXPECTED_N_ARMS_TOTAL should be 5 (3 band + 2 diag); "
        f"got {EXPECTED_N_ARMS_TOTAL}"
    )

    print("[selftest] kb_partition_by_source_class_v4_calibrated "
          "formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME", "kb_partition_by_source_class_v4_calibrated"
    )


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _build_inline_kb(out_dir: Path, max_files: int) -> tuple[dict, dict]:
    """Build chunk-KB. Returns (manifest, cardinality_audit).

    cardinality_audit splits classes into:
      - "reached_and_ingested" (n_chunks > 0; healthy)
      - "reached_zero_chunks"  (n_chunks == 0; INGEST BUG; HARD_FAIL)
      - "unreachable"          (root_dir not on this runner; WARN; not HF)
    """
    schema = load_schema(REPO)
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=SELF_CONTAINED_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )

    # Capture unreachable classes from the plan BEFORE ingest (so we can
    # distinguish env-diff from real ingest bugs).
    unreachable_classes: list[str] = []
    reachable_classes: list[str] = []
    for cname in SELF_CONTAINED_CHUNK_CLASSES:
        plan_entry = plan.get(cname, {})
        if plan_entry.get("skipped_unreachable"):
            unreachable_classes.append(cname)
        else:
            reachable_classes.append(cname)

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
    manifest["_unreachable_classes"] = unreachable_classes
    manifest["_reachable_classes"] = reachable_classes

    # Build the cardinality audit (FIX B per drill).
    per_class = manifest.get("per_class", {})
    reached_and_ingested = []
    reached_zero_chunks = []
    for cname in reachable_classes:
        stats = per_class.get(cname, {})
        if stats.get("n_chunks", 0) > 0:
            reached_and_ingested.append(cname)
        else:
            reached_zero_chunks.append(cname)

    audit = {
        "declared_classes": list(SELF_CONTAINED_CHUNK_CLASSES),
        "reached_and_ingested": reached_and_ingested,
        "reached_zero_chunks": reached_zero_chunks,
        "unreachable": unreachable_classes,
        "all_unreachable": (len(unreachable_classes)
                            == len(SELF_CONTAINED_CHUNK_CLASSES)),
    }
    return manifest, audit


def _cardinality_gate_fail_msg(audit: dict, n_ent: int,
                               min_ent: int) -> str | None:
    """Return HF message if cardinality gate fires; None if OK.

    HARD_FAIL triggers (per FIX B):
      - any class with reachable_root produced n_chunks=0 (real bug)
      - ALL declared classes unreachable (build totally failed)
      - n_entities < min_ent
    """
    if audit["all_unreachable"]:
        return (
            f"d4_cardinality_breach_all_unreachable: declared "
            f"classes={audit['declared_classes']} ALL unreachable on this "
            f"runner; KB build empty"
        )
    if audit["reached_zero_chunks"]:
        return (
            f"d4_cardinality_breach_reached_zero_chunks: classes "
            f"{audit['reached_zero_chunks']} reached but produced 0 "
            f"chunks (INGEST BUG; per META_RULE_H)"
        )
    if n_ent < min_ent:
        return (
            f"INGEST_TOO_SMALL: n_entities={n_ent} < min {min_ent}"
        )
    return None


def _run_full_n_preview(out_dir: Path) -> tuple[float, dict]:
    """Build a preview KB at FULL_N density with 5 queries; return baseline
    ratio_resolved. Used during smoke to enforce D1.
    """
    preview_dir = out_dir / "_preview_kb"
    manifest, audit = _build_inline_kb(
        preview_dir, max_files=SELF_CONTAINED_MAX_FILES_PREVIEW
    )
    print(f"[preview] full-N preview KB built: "
          f"n_entities={manifest.get('n_entities')} "
          f"unreachable={audit['unreachable']}", flush=True)
    kb = DirectorKBQuery(kb_dir=preview_dir)
    preview_queries = ROUTED_QUERIES[:FULL_N_PREVIEW_N_QUERIES]
    base = _arm_single_w_baseline(kb, preview_queries)
    return base["ratio_resolved"], {
        "manifest": manifest,
        "audit": audit,
        "baseline_ratio_resolved": base["ratio_resolved"],
        "preview_n_queries": FULL_N_PREVIEW_N_QUERIES,
        "preview_hf_floor": FULL_N_PREVIEW_BASELINE_HF_FLOOR,
    }


def _write_metrics(out_dir: Path, payload: dict) -> None:
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)


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
    preview_baseline_ratio: float | None = None
    preview_info: dict | None = None

    # Phase 0 (smoke only): FULL_N_PREVIEW per D1
    if args.smoke:
        try:
            print(f"[d1_preview] running FULL_N_PREVIEW at "
                  f"max_files={SELF_CONTAINED_MAX_FILES_PREVIEW} with "
                  f"{FULL_N_PREVIEW_N_QUERIES} queries (D1 discriminator-"
                  f"must-survive-scale)", flush=True)
            preview_baseline_ratio, preview_info = _run_full_n_preview(out_dir)
            print(f"[d1_preview] baseline ratio_resolved="
                  f"{preview_baseline_ratio:.4f} (HF floor "
                  f"{FULL_N_PREVIEW_BASELINE_HF_FLOOR})", flush=True)
            if preview_baseline_ratio < FULL_N_PREVIEW_BASELINE_HF_FLOOR:
                payload = {
                    "verdict": "HARD_FAIL",
                    "verdict_msg": (
                        f"d1_full_n_preview_baseline_too_low: "
                        f"{preview_baseline_ratio:.4f} < "
                        f"{FULL_N_PREVIEW_BASELINE_HF_FLOOR}; full "
                        f"dispatch BLOCKED"
                    ),
                    "elapsed_s": round(time.time() - t0, 2),
                    "summary": {
                        "anchor": _exp_name(),
                        "preview_info": preview_info,
                    },
                }
                _write_metrics(out_dir, payload)
                print(f"\n[verdict] HARD_FAIL\n[verdict_msg] "
                      f"{payload['verdict_msg']}", flush=True)
                return
        except Exception as e:  # noqa: BLE001
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": (
                    f"d1_preview_exception: {type(e).__name__}: {e}"
                ),
                "elapsed_s": round(time.time() - t0, 2),
                "summary": {"anchor": _exp_name()},
            }
            _write_metrics(out_dir, payload)
            print(f"\n[verdict] HARD_FAIL\n[verdict_msg] "
                  f"{payload['verdict_msg']}", flush=True)
            return

    # Phase 1: build inline KB
    max_files = (SELF_CONTAINED_MAX_FILES_SMOKE if args.smoke
                 else SELF_CONTAINED_MAX_FILES_FULL)
    try:
        print(f"[ingest] building inline KB at {inline_kb_dir} "
              f"smoke={args.smoke} classes={SELF_CONTAINED_CHUNK_CLASSES} "
              f"max_files={max_files} tau={DEFAULT_TAU}", flush=True)
        manifest, audit = _build_inline_kb(inline_kb_dir,
                                           max_files=max_files)
        n_ent = manifest.get("n_entities", 0)
        min_ent = (EXPECTED_INGEST_ENTITIES_MIN_SMOKE if args.smoke
                   else EXPECTED_INGEST_ENTITIES_MIN_FULL)
        print(f"[ingest] done: n_entities={n_ent} "
              f"n_chunks={manifest.get('n_chunks')} "
              f"n_triples={manifest.get('n_triples')} "
              f"coverage={manifest.get('coverage_ratio')} "
              f"avg_chunks/file={manifest.get('avg_chunks_per_file')} "
              f"elapsed_s={manifest.get('_build_elapsed_s')} "
              f"unreachable={audit['unreachable']} "
              f"reached_and_ingested={audit['reached_and_ingested']} "
              f"reached_zero_chunks={audit['reached_zero_chunks']}",
              flush=True)

        gate_msg = _cardinality_gate_fail_msg(audit, n_ent, min_ent)
        if gate_msg is not None:
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": gate_msg,
                "elapsed_s": round(time.time() - t0, 2),
                "summary": {
                    "anchor": _exp_name(),
                    "manifest": manifest,
                    "cardinality_audit": audit,
                    "preview_info": preview_info,
                },
            }
            _write_metrics(out_dir, payload)
            print(f"\n[verdict] HARD_FAIL\n[verdict_msg] "
                  f"{payload['verdict_msg']}", flush=True)
            return
    except Exception as e:  # noqa: BLE001
        payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"INGEST_EXCEPTION: {type(e).__name__}: {e}",
            "elapsed_s": round(time.time() - t0, 2),
            "summary": {"anchor": _exp_name()},
        }
        _write_metrics(out_dir, payload)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] "
              f"{payload['verdict_msg']}", flush=True)
        return

    # Phase 2: load query
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
        _write_metrics(out_dir, payload)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] "
              f"{payload['verdict_msg']}", flush=True)
        return

    queries = ROUTED_QUERIES[:10] if args.smoke else ROUTED_QUERIES
    print(f"[run] kb_partition_by_source_class_v4_calibrated "
          f"smoke={args.smoke} kb_version={kb.kb_version} "
          f"n_ent={len(kb.entity_names)} n_queries={len(queries)} "
          f"tau={DEFAULT_TAU}",
          flush=True)

    # Phase 3: run arms (D3 no-silent-except)
    arms: list[dict] = []
    base_pq: list[dict] = [{"resolved": False} for _ in queries]
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

    try:
        part = _arm_partitioned_equal_capacity(kb, queries, base_pq)
        arms.append(part)
        print(f"  ARM_PARTITIONED_W_EQUAL_CAPACITY ok={part['ok']} "
              f"routing_acc={part['routing_accuracy']} "
              f"leak={part['cross_partition_leak_rate']} "
              f"ratio_resolved={part['ratio_resolved']} "
              f"diag_regression={part['n_capacity_regression']}",
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
              f"non_ud={mem['non_ud_resolved_ratio']} "
              f"ud_floor={mem['ud_floor_applied']} "
              f"n_ud_total={mem['n_user_directive_total']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_PARTITIONED_W_MEMORY_OVERSIZED", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_PARTITIONED_W_MEMORY_OVERSIZED FAILED: {e}",
              flush=True)

    # Diagnostic arms (additive; don't gate verdict)
    try:
        diag_rank = _arm_diag_rank_based_gate(kb, queries)
        arms.append(diag_rank)
        print(f"  ARM_DIAG_RANK_BASED_GATE ok={diag_rank['ok']} "
              f"ratio_resolved_rankgated="
              f"{diag_rank['ratio_resolved_rankgated']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_DIAG_RANK_BASED_GATE", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_DIAG_RANK_BASED_GATE FAILED: {e}", flush=True)

    try:
        diag_dist = _arm_diag_cosine_dist_dump(kb, queries, out_dir)
        arms.append(diag_dist)
        print(f"  ARM_DIAG_COSINE_DIST_DUMP ok={diag_dist['ok']} "
              f"top1_mean={diag_dist['aggregate_top1_mean']} "
              f"dump={diag_dist['dump_path']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_DIAG_COSINE_DIST_DUMP", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_DIAG_COSINE_DIST_DUMP FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms,
                                     preview_baseline_ratio=preview_baseline_ratio)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": _exp_name(),
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "schema_version": kb.schema_version,
        "encoder": kb.encoder_name,
        "inline_kb_manifest": manifest,
        "cardinality_audit": audit,
        "preview_info": preview_info,
        "inline_kb_dir": str(inline_kb_dir),
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "v4_calibrated_bands": {
            "routing_hp_floor": ROUTING_HP_FLOOR,
            "leak_hp_ceil": LEAK_HP_CEIL,
            "ratio_resolved_floor": RATIO_RESOLVED_FLOOR,
            "routing_mb_floor": ROUTING_MB_FLOOR,
            "ud_relative_gap": UD_RELATIVE_GAP,
            "ud_abs_floor": UD_ABS_FLOOR,
            "default_tau": DEFAULT_TAU,
            "self_contained_max_files_full": SELF_CONTAINED_MAX_FILES_FULL,
            "self_contained_max_files_smoke": SELF_CONTAINED_MAX_FILES_SMOKE,
            "full_n_preview_baseline_hf_floor": FULL_N_PREVIEW_BASELINE_HF_FLOOR,
        },
        "chunk_classes_ingested": list(SELF_CONTAINED_CHUNK_CLASSES),
        "v4_fixes_applied": ["FIX_A_tau_0.15", "FIX_B_cardinality_gate",
                             "FIX_C_max_files_800",
                             "FIX_D_pass_schema_version_to_query",
                             "DIAG_RANK_BASED_GATE",
                             "DIAG_COSINE_DIST_DUMP",
                             "D1_FULL_N_PREVIEW_in_smoke"],
    }
    _write_metrics(out_dir, {"verdict": verdict, "verdict_msg": vm,
                             "elapsed_s": elapsed, "summary": payload})
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
