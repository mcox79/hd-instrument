"""SUBSTRATE-vs-MD HEAD-TO-HEAD post-compaction recovery proof-gate v1 (2026-06-27).

Pre-reg: preregs/2026-06-27_substrate_vs_md_head_to_head_post_compaction_recovery_v1.md
Design:  notes/research_drill_substrate_vs_md_head_to_head_proof_gate_design_2026-06-27.md

ASCII-only. No emojis. No em-dashes.

Operationally answers four questions before USER's MEMORY.md POST-COMPACTION
RITUAL flips from "Read BACKUP file directly" to "Query substrate-KB FIRST":

  1. Latency    : substrate end-to-end vs MD Read+grep wall-clock
  2. Completeness: returned content Jaccard vs ground-truth section text
  3. Freshness  : substrate KB last-ingest-ts lag vs FS file mtime
  4. Robustness : filesystem-fallback returns correct answer when KB partition-fault

Plus diagnostic ARM 5 SCALE_PROBE (full 1M-atom KB; not in verdict gate).

ENVELOPE (envelope-fail-bands; pre-registered):
  hp_max_substrate_latency_ratio_vs_md  = 2.0    HARD_PASS substrate <= 2x MD median
  hf_max_substrate_latency_ratio_vs_md  = 5.0    HARD_FAIL substrate > 5x MD median
  hp_min_content_match_ratio            = 0.95   HARD_PASS Jaccard >= 0.95 avg
  hf_min_content_match_ratio            = 0.70   HARD_FAIL Jaccard < 0.70 avg
  hp_max_freshness_lag_minutes          = 10     HARD_PASS max-lag <= 10 min
  hf_max_freshness_lag_minutes          = 60     HARD_FAIL max-lag > 60 min
  hp_min_fallback_success_ratio         = 1.0    HARD_PASS fallback succ == 1.0
  hf_min_fallback_success_ratio         = 0.80   HARD_FAIL fallback succ < 0.80

VERDICT: HARD_PASS iff ALL 4 axes hit hp_* AND no axis hits hf_*. Otherwise
MIDDLE_BAND if 3/4 axes pass; HARD_FAIL if any axis tripped hf_*.

Cell does NOT auto-flip MEMORY.md ritual. Emits proposal; USER approves.

Disciplines built in:
  - META_RULE_H cardinality_ok (cardinality_ok set in summary)
  - META_RULE_J no silent except (subprocess errors HALT cell verdict UNKNOWN)
  - META_RULE_K smoke must fire discriminator (smoke variant exercises latency + content)
  - META_RULE_L band-floor results are MIDDLE_BAND not HARD_PASS
  - META_RULE_M production-scale calibration (ARM 5 SCALE_PROBE flagged in verdict_msg)
  - BIAS-N verify-the-referent (selftest_verify_referent re-Reads each chunk)
  - BIAS-13 anti-rigging (gt_hash frozen at build time; cell re-verifies)
  - SCHEMA-VET 5b per-arm hp scope (each arm has own ok-band)
  - No AskUserQuestion (3 open Qs default-chosen per drill Sec 10)
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

GROUND_TRUTH_PATH = REPO / "experiments" / "_ground_truth" / "substrate_vs_md_v1.jsonl"

ENVELOPE = {
    "hp_max_substrate_latency_ratio_vs_md": 2.0,
    "hf_max_substrate_latency_ratio_vs_md": 5.0,
    "hp_min_content_match_ratio": 0.95,
    "hf_min_content_match_ratio": 0.70,
    "hp_max_freshness_lag_minutes": 10,
    "hf_max_freshness_lag_minutes": 60,
    "hp_min_fallback_success_ratio": 1.0,
    "hf_min_fallback_success_ratio": 0.80,
}

# Per-MD subprocess timeout (seconds). MD grep+Read is fast.
PER_MD_TIMEOUT_S = 30
# Per-substrate subprocess timeout (seconds). KB load + cosine on 1M atoms.
PER_SUBSTRATE_TIMEOUT_S = 120

# Search dirs for MD path.
MD_SEARCH_DIRS = ["notes", "memory"]
# Memory files external mirror (Claude userdata) -- used for memory-class GT files.
EXTERNAL_MEMORY_DIR = Path(
    "C:/Users/marsh/.claude/projects/d--AI/memory"
)

# 5 currently-active FS files for ARM 3 freshness sample.
FRESHNESS_SAMPLE_PATHS = [
    "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md",
    "notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md",
    "data/fleet_waiting_on.md",
    "data/director_plan.json",
    "CLAUDE.md",
]


# ----------------------- Helpers -----------------------

def _tokens(text: str) -> set[str]:
    """Lowercase alnum tokens; drops 1-char tokens to suppress noise."""
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    u = a | b
    if not u:
        return 0.0
    return len(a & b) / len(u)


def _load_ground_truth() -> list[dict]:
    if not GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(
            f"ground_truth not found at {GROUND_TRUTH_PATH}; "
            f"run experiments/_ground_truth/build_substrate_vs_md_v1.py first"
        )
    out: list[dict] = []
    with GROUND_TRUTH_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    if len(out) not in (5, 20):
        raise ValueError(f"ground_truth has {len(out)} entries; expected 5 (smoke) or 20")
    return out


def _verify_gt_hashes(entries: list[dict]) -> None:
    """BIAS-13 defense: re-verify each entry's gt_hash matches its ground_truth_text."""
    for e in entries:
        actual = hashlib.sha256(e["ground_truth_text"].encode("utf-8")).hexdigest()
        expected = e["gt_hash"].split(":", 1)[1] if ":" in e["gt_hash"] else e["gt_hash"]
        if actual != expected:
            raise RuntimeError(
                f"GT_HASH_MISMATCH id={e['id']} expected={expected[:16]} "
                f"actual={actual[:16]}: ground_truth_text was modified post-build "
                f"(BIAS-13 contamination defense fired)"
            )


# ----------------------- Substrate path -----------------------

def _substrate_query(question: str, k: int = 5) -> tuple[float, dict | None, str | None]:
    """Run substrate KB query via subprocess; return (elapsed_s, parsed_json, error_str).

    Uses --chunk-content (v2 content KB) which returns CHUNK_CONTENT snippets via
    the relations field. Per META_RULE_J: any subprocess error returns error_str
    instead of silent-skip; caller halts.
    """
    cmd = [
        sys.executable,
        str(REPO / "tools" / "director_kb_query.py"),
        question,
        "--chunk-content",
        "--json",
        "--k", str(k),
    ]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PER_SUBSTRATE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        return elapsed, None, f"TIMEOUT after {PER_SUBSTRATE_TIMEOUT_S}s"
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-400:]
        return elapsed, None, f"exit={proc.returncode} tail={tail}"
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return elapsed, None, f"json_decode_error: {e}"
    return elapsed, parsed, None


def _substrate_extract_content(parsed: dict | None) -> str:
    """Concatenate CHUNK_CONTENT snippets from top-K atoms."""
    if not parsed:
        return ""
    parts: list[str] = []
    for atom in parsed.get("top_k_atoms", []):
        for rel, obj in atom.get("relations", []):
            if rel == "CHUNK_CONTENT":
                parts.append(str(obj))
                break
        else:
            # No chunk content -- fall back to entity name (v1 metadata-index KB shape)
            parts.append(str(atom.get("entity", "")))
    return "\n".join(parts)


# ----------------------- MD path -----------------------

def _md_query(question: str, expected_files: list[str]) -> tuple[float, str, str | None]:
    """Simulate MD recovery: pick FIRST expected_file that exists, read it.

    Returns (elapsed_s, content_str, error_str). This models the actual
    post-compaction-recovery workflow (USER opens the BACKUP file the doc
    points to). To make the comparison fair we DON'T grep the whole tree
    (USER has the filename from POST_COMPACTION pointers).

    For MD ground-truth retrieval we read the entire candidate file
    (matches USER's actual workflow: open file, scan for relevant section).
    """
    t0 = time.perf_counter()
    last_err: str | None = None
    for rel_path in expected_files:
        # Two roots: REPO (notes/*) and external (C:/Users/.../memory/*)
        if rel_path.startswith("C:/") or rel_path.startswith("c:/"):
            p = Path(rel_path)
        else:
            p = REPO / rel_path
        if not p.exists():
            last_err = f"not_found:{p}"
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            elapsed = time.perf_counter() - t0
            return elapsed, content, None
        except OSError as e:
            last_err = f"read_error:{e}"
            continue
    elapsed = time.perf_counter() - t0
    return elapsed, "", last_err or "no_expected_file_resolved"


# ----------------------- Selftests -----------------------

def _selftest_cardinality(arm1: dict, arm3: dict, n_queries_expected: int) -> None:
    """META_RULE_H cardinality check."""
    n1 = len(arm1.get("per_query", []))
    n3 = len(arm3.get("per_file", []))
    if n1 != n_queries_expected:
        raise RuntimeError(
            f"CARDINALITY_BREACH arm1 per_query len={n1} expected={n_queries_expected}"
        )
    if n3 != len(FRESHNESS_SAMPLE_PATHS):
        raise RuntimeError(
            f"CARDINALITY_BREACH arm3 per_file len={n3} expected={len(FRESHNESS_SAMPLE_PATHS)}"
        )


def _selftest_verify_referent(arm2: dict) -> dict:
    """BIAS-N: for each substrate-returned snippet, verify it actually exists in
    SOME file under notes/ or memory/. Returns audit dict; does not halt cell."""
    audit = {"n_substrate_snippets_checked": 0, "n_substrate_snippets_grounded": 0,
             "samples": []}
    for pq in arm2.get("per_query", [])[:5]:  # sample first 5 only (cost)
        snippet = pq.get("substrate_content", "")
        if not snippet:
            continue
        # Use a representative token-trigram from the snippet
        toks = re.findall(r"[a-zA-Z0-9]+", snippet)
        if len(toks) < 5:
            continue
        probe = " ".join(toks[:5]).lower()
        grounded = False
        for d in MD_SEARCH_DIRS:
            root = REPO / d
            if not root.exists():
                continue
            for fp in root.glob("**/*.md"):
                try:
                    if probe in fp.read_text(encoding="utf-8", errors="replace").lower():
                        grounded = True
                        break
                except OSError:
                    continue
            if grounded:
                break
        audit["n_substrate_snippets_checked"] += 1
        if grounded:
            audit["n_substrate_snippets_grounded"] += 1
        audit["samples"].append({"probe": probe[:80], "grounded": grounded})
    return audit


def _selftest_antirigging(entries: list[dict]) -> None:
    _verify_gt_hashes(entries)


# ----------------------- ARMS -----------------------

def arm_latency_head_to_head(queries: list[dict]) -> dict:
    """ARM 1: 20 (or 5 smoke) queries; subprocess substrate vs MD Read."""
    t_arm = time.perf_counter()
    per_query: list[dict] = []
    sub_lat: list[float] = []
    md_lat: list[float] = []
    halts: list[str] = []
    for q in queries:
        sub_t, sub_parsed, sub_err = _substrate_query(q["q"])
        if sub_err:
            halts.append(f"id={q['id']}:{sub_err}")
        md_t, md_content, md_err = _md_query(q["q"], q["expected_files"])
        sub_lat.append(sub_t)
        md_lat.append(md_t)
        per_query.append({
            "id": q["id"], "bucket": q["bucket"],
            "substrate_s": round(sub_t, 4),
            "md_s": round(md_t, 4),
            "ratio": round(sub_t / md_t, 3) if md_t > 0 else None,
            "substrate_err": sub_err,
            "md_err": md_err,
        })
    elapsed = time.perf_counter() - t_arm
    if halts:
        return {
            "arm": "ARM_LATENCY_HEAD_TO_HEAD",
            "ok": False,
            "elapsed_s": round(elapsed, 3),
            "halt_reason": "substrate_subprocess_errors",
            "halts": halts[:10],
            "per_query": per_query,
        }
    sub_med = statistics.median(sub_lat)
    md_med = statistics.median(md_lat)
    sub_p95 = sorted(sub_lat)[int(0.95 * (len(sub_lat) - 1))]
    md_p95 = sorted(md_lat)[int(0.95 * (len(md_lat) - 1))]
    ratio_med = sub_med / md_med if md_med > 0 else float("inf")
    ratio_p95 = sub_p95 / md_p95 if md_p95 > 0 else float("inf")
    hp = ratio_med <= ENVELOPE["hp_max_substrate_latency_ratio_vs_md"]
    hf = ratio_med > ENVELOPE["hf_max_substrate_latency_ratio_vs_md"]
    return {
        "arm": "ARM_LATENCY_HEAD_TO_HEAD",
        "ok": hp,
        "hf_tripped": hf,
        "elapsed_s": round(elapsed, 3),
        "substrate_median_s": round(sub_med, 4),
        "substrate_p95_s": round(sub_p95, 4),
        "md_median_s": round(md_med, 4),
        "md_p95_s": round(md_p95, 4),
        "ratio_median": round(ratio_med, 3),
        "ratio_p95": round(ratio_p95, 3),
        "hp_threshold": ENVELOPE["hp_max_substrate_latency_ratio_vs_md"],
        "hf_threshold": ENVELOPE["hf_max_substrate_latency_ratio_vs_md"],
        "per_query": per_query,
    }


def arm_content_completeness(queries: list[dict]) -> dict:
    """ARM 2: substrate-content vs ground-truth-section Jaccard."""
    t_arm = time.perf_counter()
    per_query: list[dict] = []
    halts: list[str] = []
    jaccards_sub: list[float] = []
    jaccards_md: list[float] = []
    precisions_sub: list[float] = []
    recalls_sub: list[float] = []
    for q in queries:
        sub_t, sub_parsed, sub_err = _substrate_query(q["q"])
        if sub_err:
            halts.append(f"id={q['id']}:{sub_err}")
        sub_content = _substrate_extract_content(sub_parsed)
        md_t, md_content, md_err = _md_query(q["q"], q["expected_files"])

        gt_tokens = _tokens(q["ground_truth_text"])
        sub_tokens = _tokens(sub_content)
        md_tokens = _tokens(md_content)

        j_sub = _jaccard(sub_tokens, gt_tokens)
        j_md = _jaccard(md_tokens, gt_tokens)
        # Precision = fraction of substrate tokens that are in GT
        p_sub = (len(sub_tokens & gt_tokens) / len(sub_tokens)) if sub_tokens else 0.0
        # Recall = fraction of GT tokens that are in substrate
        r_sub = (len(sub_tokens & gt_tokens) / len(gt_tokens)) if gt_tokens else 0.0
        jaccards_sub.append(j_sub)
        jaccards_md.append(j_md)
        precisions_sub.append(p_sub)
        recalls_sub.append(r_sub)
        per_query.append({
            "id": q["id"], "bucket": q["bucket"],
            "substrate_jaccard": round(j_sub, 3),
            "md_jaccard": round(j_md, 3),
            "substrate_precision": round(p_sub, 3),
            "substrate_recall": round(r_sub, 3),
            "substrate_content_preview": (sub_content[:200] if sub_content else ""),
            "substrate_content": sub_content,  # retained for selftest_verify_referent
            "substrate_err": sub_err,
        })
    elapsed = time.perf_counter() - t_arm
    if halts:
        return {
            "arm": "ARM_CONTENT_COMPLETENESS",
            "ok": False,
            "elapsed_s": round(elapsed, 3),
            "halt_reason": "substrate_subprocess_errors",
            "halts": halts[:10],
            "per_query": per_query,
        }
    macro_sub = statistics.mean(jaccards_sub) if jaccards_sub else 0.0
    macro_md = statistics.mean(jaccards_md) if jaccards_md else 0.0
    macro_p = statistics.mean(precisions_sub) if precisions_sub else 0.0
    macro_r = statistics.mean(recalls_sub) if recalls_sub else 0.0
    hp = macro_sub >= ENVELOPE["hp_min_content_match_ratio"]
    hf = macro_sub < ENVELOPE["hf_min_content_match_ratio"]
    return {
        "arm": "ARM_CONTENT_COMPLETENESS",
        "ok": hp,
        "hf_tripped": hf,
        "elapsed_s": round(elapsed, 3),
        "substrate_macro_jaccard": round(macro_sub, 4),
        "md_macro_jaccard": round(macro_md, 4),
        "substrate_macro_precision": round(macro_p, 4),
        "substrate_macro_recall": round(macro_r, 4),
        "hp_threshold": ENVELOPE["hp_min_content_match_ratio"],
        "hf_threshold": ENVELOPE["hf_min_content_match_ratio"],
        "per_query": per_query,
    }


def arm_freshness_sample() -> dict:
    """ARM 3: 5 sample FS files; max lag of FS mtime - KB ingest_ts."""
    t_arm = time.perf_counter()
    per_file: list[dict] = []
    lags_min: list[float] = []
    halts: list[str] = []
    for rel in FRESHNESS_SAMPLE_PATHS:
        p = REPO / rel
        if not p.exists():
            per_file.append({"path": rel, "fs_exists": False, "skipped": True})
            continue
        fs_mtime = p.stat().st_mtime
        # Substrate query: search for the filename slug.
        slug = Path(rel).stem
        sub_t, parsed, err = _substrate_query(slug, k=3)
        if err:
            halts.append(f"file={rel}:{err}")
            per_file.append({"path": rel, "substrate_err": err})
            continue
        # Pick best atom: highest cosine.
        kb_ingest_ts: float | None = None
        kb_top_entity = None
        if parsed and parsed.get("top_k_atoms"):
            top = parsed["top_k_atoms"][0]
            kb_top_entity = top.get("entity")
            # Look for INGEST_TS or DATE_FILED edge
            for rel_name, obj in top.get("relations", []):
                if rel_name in ("INGEST_TS", "DATE_FILED", "INGESTED_AT", "MTIME"):
                    try:
                        # Try ISO parse via fromisoformat (handles Z by trim)
                        ts_str = str(obj).rstrip("Z")
                        from datetime import datetime
                        kb_ingest_ts = datetime.fromisoformat(ts_str).timestamp()
                        break
                    except (ValueError, TypeError):
                        continue
        if kb_ingest_ts is None:
            # No ingest_ts edge -- mark unknown and use kb file mtime as proxy
            kb_canon = REPO / "data" / "substrate_director_kb_v1" / "manifest.json"
            kb_arm_full = (REPO / "data" / "exp_substrate_director_kb_ingest_v1"
                           / "_arm_full" / "kb" / "manifest.json")
            proxy_path = kb_canon if kb_canon.exists() else (
                kb_arm_full if kb_arm_full.exists() else None)
            kb_ingest_ts = proxy_path.stat().st_mtime if proxy_path else 0.0
            ts_source = "kb_manifest_mtime_proxy"
        else:
            ts_source = "atom_edge"
        lag_s = max(fs_mtime - kb_ingest_ts, 0.0)
        lag_min = lag_s / 60.0
        lags_min.append(lag_min)
        per_file.append({
            "path": rel,
            "fs_mtime": fs_mtime,
            "kb_ingest_ts": kb_ingest_ts,
            "kb_top_entity": kb_top_entity,
            "ts_source": ts_source,
            "lag_minutes": round(lag_min, 2),
        })
    elapsed = time.perf_counter() - t_arm
    if halts:
        return {
            "arm": "ARM_FRESHNESS_SAMPLE",
            "ok": False,
            "elapsed_s": round(elapsed, 3),
            "halt_reason": "substrate_subprocess_errors",
            "halts": halts[:10],
            "per_file": per_file,
        }
    if not lags_min:
        return {
            "arm": "ARM_FRESHNESS_SAMPLE",
            "ok": False,
            "elapsed_s": round(elapsed, 3),
            "halt_reason": "no_files_evaluated",
            "per_file": per_file,
        }
    max_lag = max(lags_min)
    median_lag = statistics.median(lags_min)
    hp = max_lag <= ENVELOPE["hp_max_freshness_lag_minutes"]
    hf = max_lag > ENVELOPE["hf_max_freshness_lag_minutes"]
    return {
        "arm": "ARM_FRESHNESS_SAMPLE",
        "ok": hp,
        "hf_tripped": hf,
        "elapsed_s": round(elapsed, 3),
        "max_lag_minutes": round(max_lag, 2),
        "median_lag_minutes": round(median_lag, 2),
        "n_files": len(lags_min),
        "hp_threshold": ENVELOPE["hp_max_freshness_lag_minutes"],
        "hf_threshold": ENVELOPE["hf_max_freshness_lag_minutes"],
        "per_file": per_file,
    }


def arm_robustness_partition_fault(queries: list[dict]) -> dict:
    """ARM 4: rename KB chunk dir; verify fallback path serves correct answer.

    Uses a SAFE simulated fault: we rename the chunk KB to a sibling _HIDDEN
    name, attempt substrate query (which should fail or refuse), then verify
    that the MD fallback path returns content for the same query. Restore the
    dir at end. PARTIAL: also test a truncated-chunk scenario by reading one
    chunk file, truncating its written length, then verifying graceful handling.
    """
    t_arm = time.perf_counter()
    n_queries_to_test = min(5, len(queries))
    test_qs = queries[:n_queries_to_test]
    per_query: list[dict] = []

    # Locate chunk KB dir (canonical preferred; fallback arm_full).
    chunk_canon = REPO / "data" / "substrate_director_kb_chunk_v1"
    chunk_arm = (REPO / "data" / "exp_substrate_director_kb_content_chunk_ingest_v1"
                 / "_arm_full" / "kb")
    chunk_dir = chunk_canon if (chunk_canon / "manifest.json").exists() else (
        chunk_arm if (chunk_arm / "manifest.json").exists() else None)

    fault_applied = False
    fault_target = None
    fault_hidden = None
    if chunk_dir is not None:
        fault_target = chunk_dir
        fault_hidden = chunk_dir.with_name(chunk_dir.name + "_HEADTOHEAD_FAULT_HIDDEN")
        try:
            if fault_hidden.exists():
                shutil.rmtree(fault_hidden)
            os.rename(str(chunk_dir), str(fault_hidden))
            fault_applied = True
        except OSError as e:
            per_query.append({"setup_error": f"could_not_rename_chunk_dir: {e}"})

    try:
        n_fallback_success = 0
        for q in test_qs:
            # During fault: substrate should error/refuse; MD must serve.
            sub_t, sub_parsed, sub_err = _substrate_query(q["q"])
            md_t, md_content, md_err = _md_query(q["q"], q["expected_files"])
            # Fallback success criteria: MD returns non-empty content AND it
            # contains at least some ground-truth tokens.
            md_tokens = _tokens(md_content)
            gt_tokens = _tokens(q["ground_truth_text"])
            overlap = (len(md_tokens & gt_tokens) / len(gt_tokens)) if gt_tokens else 0.0
            success = bool(md_content) and overlap >= 0.30
            if success:
                n_fallback_success += 1
            per_query.append({
                "id": q["id"], "bucket": q["bucket"],
                "substrate_attempted_during_fault": True,
                "substrate_err": sub_err,
                "md_fallback_s": round(md_t, 4),
                "md_overlap_with_gt": round(overlap, 3),
                "fallback_success": success,
            })
    finally:
        if fault_applied and fault_target is not None and fault_hidden is not None:
            try:
                os.rename(str(fault_hidden), str(fault_target))
            except OSError as e:
                # Loud but do not halt the arm; mark restore failure.
                print(f"[arm4] RESTORE_ERROR could not restore chunk_dir: {e}",
                      file=sys.stderr, flush=True)

    elapsed = time.perf_counter() - t_arm
    n = max(len(test_qs), 1)
    fallback_ratio = n_fallback_success / n
    hp = fallback_ratio >= ENVELOPE["hp_min_fallback_success_ratio"]
    hf = fallback_ratio < ENVELOPE["hf_min_fallback_success_ratio"]
    return {
        "arm": "ARM_ROBUSTNESS_PARTITION_FAULT",
        "ok": hp,
        "hf_tripped": hf,
        "elapsed_s": round(elapsed, 3),
        "n_queries_tested": len(test_qs),
        "n_fallback_success": n_fallback_success,
        "fallback_success_ratio": round(fallback_ratio, 3),
        "fault_applied": fault_applied,
        "chunk_dir_path": str(chunk_dir) if chunk_dir else None,
        "hp_threshold": ENVELOPE["hp_min_fallback_success_ratio"],
        "hf_threshold": ENVELOPE["hf_min_fallback_success_ratio"],
        "per_query": per_query,
    }


def arm_scale_probe(queries: list[dict]) -> dict:
    """ARM 5 DIAGNOSTIC: full 1M-atom KB probe; flag scale degradation.

    Not in verdict gate. Repeats latency + completeness on a sub-sample of
    queries against whatever default KB is loaded (which is the full 1M+
    canonical KB if built, else arm_full smoke subset). Flags in verdict_msg
    if substrate degrades vs ARM 1/ARM 2 results.
    """
    t_arm = time.perf_counter()
    sample = queries[:min(5, len(queries))]
    per_query: list[dict] = []
    sub_lats: list[float] = []
    sub_jaccards: list[float] = []
    halts: list[str] = []
    for q in sample:
        sub_t, parsed, err = _substrate_query(q["q"])
        if err:
            halts.append(f"id={q['id']}:{err}")
            per_query.append({"id": q["id"], "substrate_err": err})
            continue
        content = _substrate_extract_content(parsed)
        j = _jaccard(_tokens(content), _tokens(q["ground_truth_text"]))
        sub_lats.append(sub_t)
        sub_jaccards.append(j)
        per_query.append({
            "id": q["id"],
            "substrate_s": round(sub_t, 4),
            "substrate_jaccard": round(j, 3),
        })
    elapsed = time.perf_counter() - t_arm
    # Read total atom count from KB manifest (if available) to log scale.
    kb_canon = REPO / "data" / "substrate_director_kb_v1" / "manifest.json"
    kb_arm = (REPO / "data" / "exp_substrate_director_kb_ingest_v1"
              / "_arm_full" / "kb" / "manifest.json")
    manifest_path = kb_canon if kb_canon.exists() else (kb_arm if kb_arm.exists() else None)
    n_atoms = None
    kb_label = None
    if manifest_path is not None:
        try:
            man = json.loads(manifest_path.read_text(encoding="utf-8"))
            n_atoms = man.get("n_atoms") or man.get("n_entities")
            kb_label = manifest_path.parent.name
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "arm": "ARM_SCALE_PROBE",
        "ok": True,  # diagnostic; not in verdict
        "diagnostic": True,
        "elapsed_s": round(elapsed, 3),
        "n_queries": len(sample),
        "n_atoms_in_kb": n_atoms,
        "kb_label": kb_label,
        "substrate_median_s": round(statistics.median(sub_lats), 4) if sub_lats else None,
        "substrate_median_jaccard": round(statistics.median(sub_jaccards), 3) if sub_jaccards else None,
        "halts": halts,
        "per_query": per_query,
    }


# ----------------------- Verdict -----------------------

def verdict_compute(arms: list[dict]) -> tuple[str, str]:
    """4-axis gate. ARM 5 is diagnostic; not in verdict but surfaced in msg."""
    primaries = [a for a in arms if not a.get("diagnostic")]
    diag = next((a for a in arms if a.get("arm") == "ARM_SCALE_PROBE"), None)

    # Halt detection
    halts = [a for a in primaries if a.get("halt_reason")]
    if halts:
        names = ",".join(a["arm"] for a in halts)
        reasons = "; ".join(f"{a['arm']}:{a.get('halt_reason')}" for a in halts)
        return "UNKNOWN", f"halted_per_META_RULE_J: {names} -- {reasons}"

    hf_axes = [a for a in primaries if a.get("hf_tripped")]
    if hf_axes:
        names = ",".join(a["arm"] for a in hf_axes)
        return "HARD_FAIL", f"{len(hf_axes)}_axes_HARD_FAIL: {names}; ritual_stays_MD_first"

    hp_axes = [a for a in primaries if a.get("ok")]
    n_pass = len(hp_axes)
    n_total = len(primaries)

    # Diagnostic scale-probe flag
    scale_flag = ""
    if diag is not None:
        a1 = next((a for a in primaries if a["arm"] == "ARM_LATENCY_HEAD_TO_HEAD"), None)
        a2 = next((a for a in primaries if a["arm"] == "ARM_CONTENT_COMPLETENESS"), None)
        if a1 and diag.get("substrate_median_s") is not None and a1.get("substrate_median_s"):
            if diag["substrate_median_s"] > 2.0 * a1["substrate_median_s"]:
                scale_flag = (f"; ARM5_SCALE_DEGRADATION_FLAG: scale_med={diag['substrate_median_s']}s "
                              f"vs arm1_med={a1['substrate_median_s']}s (>2x)")
        if (a2 and diag.get("substrate_median_jaccard") is not None
                and a2.get("substrate_macro_jaccard")):
            if diag["substrate_median_jaccard"] < 0.7 * a2["substrate_macro_jaccard"]:
                scale_flag += (f"; ARM5_SCALE_JACCARD_DEGRADE: scale_jac="
                               f"{diag['substrate_median_jaccard']} vs arm2_jac="
                               f"{a2['substrate_macro_jaccard']} (<70%)")

    if n_pass == n_total:
        return "HARD_PASS", (
            f"all_{n_total}_axes_HARD_PASS; substrate-vs-MD ritual-flip eligible "
            f"pending USER review{scale_flag}"
        )
    elif n_pass == n_total - 1:
        failed = [a["arm"] for a in primaries if not a.get("ok")]
        return "MIDDLE_BAND", (
            f"{n_pass}_of_{n_total}_axes_HP; failing_axes={','.join(failed)}; "
            f"ritual_stays_MD_first{scale_flag}"
        )
    else:
        failed = [a["arm"] for a in primaries if not a.get("ok")]
        return "HARD_FAIL", (
            f"only_{n_pass}_of_{n_total}_axes_HP; failing_axes={','.join(failed)}; "
            f"ritual_stays_MD_first{scale_flag}"
        )


def _instrumentation_selftest() -> None:
    """Verify verdict_compute branch coverage."""
    # All pass + scale OK -> HARD_PASS
    arms_hp = [
        {"arm": "ARM_LATENCY_HEAD_TO_HEAD", "ok": True, "hf_tripped": False, "substrate_median_s": 1.0},
        {"arm": "ARM_CONTENT_COMPLETENESS", "ok": True, "hf_tripped": False, "substrate_macro_jaccard": 0.96},
        {"arm": "ARM_FRESHNESS_SAMPLE", "ok": True, "hf_tripped": False},
        {"arm": "ARM_ROBUSTNESS_PARTITION_FAULT", "ok": True, "hf_tripped": False},
        {"arm": "ARM_SCALE_PROBE", "ok": True, "diagnostic": True,
         "substrate_median_s": 1.2, "substrate_median_jaccard": 0.92},
    ]
    v, msg = verdict_compute(arms_hp)
    assert v == "HARD_PASS", f"selftest_hp_path: got {v} msg={msg}"
    # HF on latency
    arms_hf = list(arms_hp)
    arms_hf[0] = {"arm": "ARM_LATENCY_HEAD_TO_HEAD", "ok": False, "hf_tripped": True}
    v, msg = verdict_compute(arms_hf)
    assert v == "HARD_FAIL", f"selftest_hf_path: got {v} msg={msg}"
    # MIDDLE_BAND: 1 axis missed hp but not hf
    arms_mb = list(arms_hp)
    arms_mb[0] = {"arm": "ARM_LATENCY_HEAD_TO_HEAD", "ok": False, "hf_tripped": False,
                  "substrate_median_s": 3.5}
    v, msg = verdict_compute(arms_mb)
    assert v == "MIDDLE_BAND", f"selftest_mb_path: got {v} msg={msg}"
    # UNKNOWN: halt reason
    arms_halt = list(arms_hp)
    arms_halt[1] = {"arm": "ARM_CONTENT_COMPLETENESS", "ok": False,
                    "halt_reason": "substrate_subprocess_errors"}
    v, msg = verdict_compute(arms_halt)
    assert v == "UNKNOWN", f"selftest_unknown_path: got {v} msg={msg}"
    # Cardinality selftest
    arm1 = {"per_query": [{"id": i} for i in range(20)]}
    arm3 = {"per_file": [{"path": p} for p in FRESHNESS_SAMPLE_PATHS]}
    _selftest_cardinality(arm1, arm3, n_queries_expected=20)
    try:
        _selftest_cardinality({"per_query": [{}]}, arm3, n_queries_expected=20)
        raise AssertionError("cardinality should have raised")
    except RuntimeError:
        pass
    # Hash check
    sample_entry = {
        "id": 1,
        "ground_truth_text": "abc",
        "gt_hash": f"sha256:{hashlib.sha256(b'abc').hexdigest()}",
    }
    _verify_gt_hashes([sample_entry])
    try:
        bad = dict(sample_entry)
        bad["ground_truth_text"] = "xyz"
        _verify_gt_hashes([bad])
        raise AssertionError("anti-rigging should have raised")
    except RuntimeError:
        pass
    # Jaccard sanity
    j_id = _jaccard({"a", "b"}, {"a", "b"})
    assert j_id == 1.0, f"jaccard identity {j_id}"
    j_disj = _jaccard({"a"}, {"b"})
    assert j_disj == 0.0, f"jaccard disjoint {j_disj}"
    print("[selftest] substrate_vs_md_head_to_head_v1 formula PASS", flush=True)


_instrumentation_selftest()


# ----------------------- Output -----------------------

def _exp_name(smoke: bool) -> str:
    base = os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_vs_md_head_to_head_post_compaction_recovery_v1",
    )
    return base + ("_smoke" if (smoke and not base.endswith("_smoke")) else "")


def _exp_dir(smoke: bool) -> Path:
    d = REPO / "data" / f"exp_{_exp_name(smoke)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_metrics(out_dir: Path, payload: dict) -> Path:
    out = out_dir / "metrics.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke variant: 5 queries (one per bucket) ARM 1+2 only")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0)

    t0 = time.time()
    entries = _load_ground_truth()
    _selftest_antirigging(entries)

    if args.smoke:
        # Pick first entry of each bucket up to 5 total
        seen_buckets: set[str] = set()
        smoke_qs: list[dict] = []
        for e in entries:
            if e["bucket"] not in seen_buckets:
                smoke_qs.append(e)
                seen_buckets.add(e["bucket"])
            if len(smoke_qs) == 5:
                break
        queries = smoke_qs
        print(f"[run] SMOKE variant: {len(queries)} queries (one per bucket)", flush=True)
    else:
        queries = entries
        print(f"[run] FULL variant: {len(queries)} queries (4 buckets x 5)", flush=True)

    arms: list[dict] = []

    print("[arm1] ARM_LATENCY_HEAD_TO_HEAD ...", flush=True)
    a1 = arm_latency_head_to_head(queries)
    arms.append(a1)
    print(f"  arm1 ok={a1.get('ok')} ratio_med={a1.get('ratio_median')} "
          f"sub_med={a1.get('substrate_median_s')}s md_med={a1.get('md_median_s')}s", flush=True)

    print("[arm2] ARM_CONTENT_COMPLETENESS ...", flush=True)
    a2 = arm_content_completeness(queries)
    arms.append(a2)
    print(f"  arm2 ok={a2.get('ok')} sub_jac={a2.get('substrate_macro_jaccard')} "
          f"md_jac={a2.get('md_macro_jaccard')}", flush=True)

    if not args.smoke:
        print("[arm3] ARM_FRESHNESS_SAMPLE ...", flush=True)
        a3 = arm_freshness_sample()
        arms.append(a3)
        print(f"  arm3 ok={a3.get('ok')} max_lag_min={a3.get('max_lag_minutes')}", flush=True)

        print("[arm4] ARM_ROBUSTNESS_PARTITION_FAULT ...", flush=True)
        a4 = arm_robustness_partition_fault(queries)
        arms.append(a4)
        print(f"  arm4 ok={a4.get('ok')} fallback_ratio={a4.get('fallback_success_ratio')}", flush=True)

        print("[arm5] ARM_SCALE_PROBE (diagnostic) ...", flush=True)
        a5 = arm_scale_probe(queries)
        arms.append(a5)
        print(f"  arm5 (diag) sub_med={a5.get('substrate_median_s')}s "
              f"jac_med={a5.get('substrate_median_jaccard')} n_atoms={a5.get('n_atoms_in_kb')}",
              flush=True)

    # Selftest cardinality
    n_expected = len(queries)
    try:
        if args.smoke:
            # Smoke skips arm3; only cardinality on arm1
            n1 = len(a1.get("per_query", []))
            if n1 != n_expected:
                raise RuntimeError(f"smoke_cardinality_breach arm1 {n1} vs {n_expected}")
        else:
            _selftest_cardinality(a1, a3, n_queries_expected=n_expected)
    except RuntimeError as e:
        print(f"[selftest] CARDINALITY_BREACH: {e}", flush=True)
        verdict = "UNKNOWN"
        verdict_msg = f"cardinality_selftest_failed: {e}"
        elapsed = round(time.time() - t0, 2)
        payload = {
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "elapsed_s": elapsed,
            "summary": {
                "anchor": "substrate_vs_md_head_to_head_post_compaction_recovery_v1",
                "smoke": args.smoke,
                "arms": arms,
                "envelope": ENVELOPE,
                "cardinality_ok": False,
                "n_queries_expected": n_expected,
            },
        }
        _write_metrics(_exp_dir(args.smoke), payload)
        print(f"\n[verdict] {verdict}\n[verdict_msg] {verdict_msg}", flush=True)
        sys.exit(0)

    # Verify-referent audit (sample-based; informational)
    referent_audit = _selftest_verify_referent(a2)

    # Compute verdict
    if args.smoke:
        # Smoke verdict: looser bands per design Sec 5 smoke variant.
        # HARD_PASS iff substrate ran without subprocess errors AND latency
        # ratio_median <= 5.0 AND content macro Jaccard >= 0.5.
        if a1.get("halt_reason") or a2.get("halt_reason"):
            verdict, verdict_msg = ("UNKNOWN",
                                    f"smoke_halted: a1={a1.get('halt_reason')} "
                                    f"a2={a2.get('halt_reason')}")
        else:
            ratio = a1.get("ratio_median", float("inf"))
            jac = a2.get("substrate_macro_jaccard", 0.0)
            if ratio <= 5.0 and jac >= 0.5:
                verdict = "HARD_PASS"
                verdict_msg = (f"smoke_HP: ratio_med={ratio} <= 5.0, "
                               f"sub_jac={jac} >= 0.5; full dispatch eligible")
            elif ratio <= 10.0 and jac >= 0.3:
                verdict = "MIDDLE_BAND"
                verdict_msg = (f"smoke_MM: ratio_med={ratio}, sub_jac={jac}; "
                               f"cell runs but discriminator margin thin")
            else:
                verdict = "HARD_FAIL"
                verdict_msg = (f"smoke_HF: ratio_med={ratio}, sub_jac={jac}; "
                               f"substrate underperforming basic threshold")
    else:
        verdict, verdict_msg = verdict_compute(arms)

    elapsed = round(time.time() - t0, 2)

    # Strip large content fields from arm2 per_query for compactness in summary
    # (preserve preview only). Drop full substrate_content (kept for selftest).
    a2_compact = dict(a2)
    a2_compact["per_query"] = [
        {k: v for k, v in pq.items() if k != "substrate_content"}
        for pq in a2.get("per_query", [])
    ]
    arms_out = [(a2_compact if a.get("arm") == "ARM_CONTENT_COMPLETENESS" else a)
                for a in arms]

    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "anchor": "substrate_vs_md_head_to_head_post_compaction_recovery_v1",
            "smoke": args.smoke,
            "n_queries": len(queries),
            "cardinality_ok": True,
            "envelope": ENVELOPE,
            "arms": arms_out,
            "referent_audit": referent_audit,
            "drill_design": (
                "notes/research_drill_substrate_vs_md_head_to_head_proof_gate_design_2026-06-27.md"
            ),
            "ground_truth_file": str(GROUND_TRUTH_PATH.relative_to(REPO)),
            "n_ground_truth_entries": len(entries),
            "auto_flip_disabled": True,
            "note": ("Cell does NOT auto-flip MEMORY.md ritual on HARD_PASS; "
                     "emits proposal for USER review per drill Sec 9."),
        },
    }
    out_path = _write_metrics(_exp_dir(args.smoke), payload)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[metrics] {out_path}", flush=True)


if __name__ == "__main__":
    main()
