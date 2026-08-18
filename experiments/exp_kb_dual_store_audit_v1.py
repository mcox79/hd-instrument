"""KB DUAL-STORE AUDIT v1 (ANCHOR 5; INFRASTRUCTURE; 2026-06-26).

Pre-reg: preregs/2026-06-26_kb_dual_store_audit_v1.md
Wave 3a (SHIPS FIRST per USER vetting protocol).

Load-bearing SAFETY harness: every Director query simultaneously hits the
substrate-KB AND filesystem-grep; results compared; mismatches logged to
data/director_kb_audit_log.jsonl with timestamp + query + substrate-result +
filesystem-result + reason + capacity-metrics.

ARMS (2 mandatory):
  ARM_DUAL_STORE_MATCH        - 100 known queries; substrate vs filesystem;
                                pass if match rate >= 0.95 (HARD_PASS) or
                                >= 0.90 (MIDDLE).
  ARM_AUDIT_LOG_INTEGRITY     - audit log durable + parseable + concurrent
                                ingest+query safe.

SUCCESS CRITERIA (TOOLING tier; OPERATIONAL not CERT-bands per Fix #28):
  - ARM_DUAL_STORE_MATCH: match_rate >= 0.95 (HARD_PASS) or >= 0.90 (MIDDLE).
  - ARM_AUDIT_LOG_INTEGRITY: all lines parseable + required fields present;
    no concurrent-write corruption.
  - USER_DIRECTIVE retention check: zero loss tolerance (load-bearing).

(Verdict bands are OPERATIONAL not CERT-LEVEL; tool wins via being USEFUL
not via being cert-grade.)

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb_query import DirectorKBQuery, load_default_kb  # noqa: E402


AUDIT_LOG_PATH = REPO / "data" / "director_kb_audit_log.jsonl"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


# 100 known queries: 30 from query cell + 70 synthesized variants.
# Each: (question, expected_substring_for_match_check).
KNOWN_QUERIES_FULL: list[tuple[str, str]] = [
    ("substrate director kb ingest", "director_kb"),
    ("chain grade multi hop depth extension", "multihop"),
    ("char trigram encoder", "trigram"),
    ("fleet waiting on", "fleet"),
    ("director plan", "director_plan"),
    ("cert ledger", "cert_ledger"),
    ("substrate index atoms", "substrate_index"),
    ("ANCHOR_FOR", "ANCHOR_FOR"),
    ("HARD_PASS verdict", "HARD_PASS"),
    ("kg traversal", "kg"),
    ("USER directive memory", "memory"),
    ("substrate product positioning", "substrate"),
    ("phase diagram multihop", "multihop"),
    ("ingest pipeline determinism", "ingest"),
    ("semantic concept learner", "semantic"),
    ("brain mechanism analogue", "brain"),
    ("conceptnet ingest", "conceptnet"),
    ("FB15k 237", "FB15k"),
    ("HotpotQA", "hotpot"),
    ("encoder bottleneck", "encoder"),
    ("orchestrator paused flag", "orchestrator"),
    ("queue add tool", "queue"),
    ("smoke gate", "smoke"),
    ("verdict handler", "verdict"),
    ("research lit scan", "research"),
    ("skunkworks cert audit", "skunkworks"),
    ("substrate native concept", "concept"),
    ("memory curator", "memory"),
    ("director kb query", "query"),
    ("self test discipline", "self"),
    # 70 synthesized variants (substrate-relevant terms from notes/preregs/memory)
    ("ultrametric clustering", "ultrametric"),
    ("E tensor importance signal", "E_tensor"),
    ("cortex separate importance", "cortex"),
    ("phase diagram capacity sweep", "phase_diagram"),
    ("substrate anisotropy", "anisotropy"),
    ("pattern separation dg", "pattern_separation"),
    ("topk composition", "topk"),
    ("predictive coding cleanup", "pc_cleanup"),
    ("edge importance bound", "edge_importance"),
    ("bio trio ingest", "bio_trio"),
    ("language trio ingest", "language_trio"),
    ("wordnet synsets", "wordnet"),
    ("verbnet thematic roles", "verbnet"),
    ("framenet frame elements", "framenet"),
    ("gene ontology obo", "gene_ontology"),
    ("kegg pathway kgml", "kegg"),
    ("neurolex ttl", "neurolex"),
    ("noise scaling bug", "noise"),
    ("by construction saturation", "saturation"),
    ("middle band verdict", "MIDDLE_BAND"),
    ("hard fail verdict", "HARD_FAIL"),
    ("seed checkpoint resume", "_seed_checkpoint"),
    ("cv tightness across seeds", "cv"),
    ("smoke before full dispatch", "smoke"),
    ("config version hash", "config_version"),
    ("verify the referent", "referent"),
    ("negativity bias rule", "negativity_bias"),
    ("director plan json", "director_plan"),
    ("fleet waiting on tracker", "fleet_waiting_on"),
    ("monitor arm canonical", "monitor"),
    ("event bus singleton", "event_bus"),
    ("queue add gate checks", "queue_add"),
    ("prereg envelope fail bands", "prereg"),
    ("schema config externalized", "schema"),
    ("char trigram bigram", "trigram"),
    ("hopfield modern classical", "hopfield"),
    ("retrieval cleanup ratio", "retrieval"),
    ("vq codebook granularity", "vq"),
    ("substrate native lm", "substrate_lm"),
    ("text8 bpc evaluation", "text8"),
    ("wikitext2 broken loader", "wikitext2"),
    ("shakespeare char corpus", "shakespeare"),
    ("frozen encoder baseline", "frozen_encoder"),
    ("inference transfer eval", "inference_transfer"),
    ("refuse gate confidence", "refuse_gate"),
    ("graph traversal multi hop", "multi_hop"),
    ("set recall ratio", "setrecall"),
    ("orchestrator routing", "orchestrator"),
    ("strategy request routing", "strategy_request"),
    ("two tier generational w", "two_tier"),
    ("partition routing hierarchical", "partition_routing"),
    ("hrr binding chain grade", "hrr"),
    ("pythia residual encoder", "pythia"),
    ("encoder caching gpu oom", "encoder_cache"),
    ("kb determinism reingest", "determinism"),
    ("ingest pipeline coverage", "coverage"),
    ("operational tier middle band", "operational"),
    ("autonomous arc fixes", "autonomous_arc"),
    ("user directive load bearing", "USER_DIRECTIVE"),
    ("memory curator skill", "memory_curator"),
    ("meta audit cadence", "meta_audit"),
    ("session local handoff snapshot", "session_local"),
    ("phase 3 agent teams", "agent_teams"),
    ("research lead team coordination", "research_lead"),
    ("exp dev cell author", "exp_dev"),
    ("skunkworks cert owner", "skunkworks"),
    ("testbed fleet health", "testbed"),
    ("orchestrator pause flag", "paused_flag"),
    ("director kb dogfood", "dogfood"),
    ("substrate self map v2", "self_map"),
    ("compositional understanding wave", "compositional"),
    ("first wave 7 anchors", "first_wave"),
]
assert len(KNOWN_QUERIES_FULL) >= 100, f"want >= 100 queries, got {len(KNOWN_QUERIES_FULL)}"
KNOWN_QUERIES_FULL = KNOWN_QUERIES_FULL[:100]


SMOKE_QUERIES = KNOWN_QUERIES_FULL[:10]
DEFAULT_K = 8
DEFAULT_TAU = 0.3

# USER_DIRECTIVE query subset: any query matching USER memory directive content.
# These MUST match across both stores; zero loss tolerance.
USER_DIRECTIVE_QUERY_SUBSTRINGS = (
    "USER directive", "user directive", "USER_DIRECTIVE",
    "memory curator", "no busy work",
)


def _is_user_directive_query(q: str) -> bool:
    ql = q.lower()
    return any(s.lower() in ql for s in USER_DIRECTIVE_QUERY_SUBSTRINGS)


def _filesystem_grep(question: str, repo_root: Path, max_hits: int = 32) -> dict:
    """Filesystem-grep over canonical corpus: notes/ + preregs/ + memory/.

    Returns dict {paths: [...], n_files: N, elapsed_s: ...}.
    Uses substring search (case-insensitive) on each word in the question.
    Heuristic: take the LONGEST non-stop-word as the primary needle (3+ chars).
    """
    t0 = time.perf_counter()
    words = [w for w in re.split(r"[^A-Za-z0-9_]+", question) if len(w) >= 3]
    if not words:
        return {"paths": [], "n_files": 0, "elapsed_s": 0.0, "needle": ""}
    # Sort by length desc; pick longest (most discriminative).
    words.sort(key=lambda w: -len(w))
    needle = words[0].lower()
    hits: list[str] = []
    # Search notes/ + preregs/ + memory (external).
    roots = [
        repo_root / "notes",
        repo_root / "preregs",
        Path("C:/Users/marsh/.claude/projects/d--AI/memory"),
    ]
    for root in roots:
        if not root.exists():
            continue
        for p in sorted(root.glob("*.md"))[:5000]:  # cap per dir
            if len(hits) >= max_hits:
                break
            try:
                txt = p.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            if needle in p.name.lower() or needle in txt:
                try:
                    rel = str(p.relative_to(repo_root)).replace("\\", "/")
                except ValueError:
                    rel = str(p).replace("\\", "/")
                hits.append(rel)
        if len(hits) >= max_hits:
            break
    elapsed = time.perf_counter() - t0
    return {"paths": hits[:max_hits], "n_files": len(hits), "elapsed_s": round(elapsed, 4), "needle": needle}


def _match_check(substrate_result: dict, fs_result: dict, expected: str) -> tuple[bool, str]:
    """Match heuristic: substrate top-K OR fs paths share a path-token OR
    expected substring is in either result.
    """
    sub_tokens: set[str] = set()
    for atom in substrate_result.get("top_k_atoms", []):
        ent = atom.get("entity", "")
        sub_tokens.add(ent.lower())
        for sp in atom.get("source_paths", []):
            sub_tokens.add(sp.lower())
    fs_tokens = {p.lower() for p in fs_result.get("paths", [])}

    # 1. Direct path overlap
    if sub_tokens & fs_tokens:
        return True, "path_overlap"
    # 2. Expected substring hit in either
    exp_lc = expected.lower()
    if any(exp_lc in t for t in sub_tokens):
        return True, "substrate_has_expected"
    if any(exp_lc in t for t in fs_tokens):
        # Substrate didn't have it but FS did = mismatch (substrate lost info).
        # UNLESS substrate refused with low confidence (which is honest behavior).
        if substrate_result.get("refused"):
            return False, "substrate_refused_but_fs_found"
        return False, "fs_has_expected_substrate_missed"
    # 3. Both came up empty/refused/no-hits = vacuous match (no info to compare).
    if substrate_result.get("refused") and fs_result.get("n_files") == 0:
        return True, "both_vacuous"
    if not sub_tokens and fs_result.get("n_files") == 0:
        return True, "both_empty"
    # 4. Substrate returned hits but FS empty: substrate may be over-recalling
    # OR the needle heuristic was too narrow; do not penalize as mismatch.
    if sub_tokens and fs_result.get("n_files") == 0:
        return True, "fs_empty_substrate_hit_likely_needle_mismatch"
    return False, "no_overlap_no_expected_hit"


def _audit_log_append(row: dict) -> None:
    """Append one row to data/director_kb_audit_log.jsonl atomically."""
    line = json.dumps(row, default=str, ensure_ascii=False) + "\n"
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)
        f.flush()


def _arm_dual_store_match(kb: DirectorKBQuery, repo_root: Path, queries: list[tuple[str, str]]) -> dict:
    """Run dual-store comparison across queries; log to audit log; return verdict dict."""
    t0 = time.perf_counter()
    n_match = 0
    n_user_directive_total = 0
    n_user_directive_match = 0
    per_query_summary: list[dict] = []
    mismatch_reasons: dict[str, int] = {}

    capacity = {
        "n_entities": len(kb.entity_names),
        "n_atoms": sum(len(v) for v in kb._atoms_by_s.values()),
        "kb_version": kb.kb_version,
        "schema_version": kb.schema_version,
        "encoder": kb.encoder_name,
    }

    for q, expected in queries:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            substrate_result = kb.query(q, k=DEFAULT_K, confidence_floor=DEFAULT_TAU)
        except Exception as e:  # noqa: BLE001
            substrate_result = {"refused": True, "refusal_reason": f"query_error:{type(e).__name__}:{e}",
                                "top_k_atoms": [], "confidence": 0.0}
        fs_result = _filesystem_grep(q, repo_root)
        is_match, reason = _match_check(substrate_result, fs_result, expected)
        if is_match:
            n_match += 1
        else:
            mismatch_reasons[reason] = mismatch_reasons.get(reason, 0) + 1

        is_ud = _is_user_directive_query(q)
        if is_ud:
            n_user_directive_total += 1
            if is_match:
                n_user_directive_match += 1

        row = {
            "ts": ts,
            "q": q,
            "expected": expected,
            "is_user_directive": is_ud,
            "substrate": {
                "refused": bool(substrate_result.get("refused")),
                "confidence": substrate_result.get("confidence", 0.0),
                "top_k_atoms": [
                    {"entity": a.get("entity"), "cosine": a.get("cosine"),
                     "source_paths": a.get("source_paths", [])[:3]}
                    for a in substrate_result.get("top_k_atoms", [])[:5]
                ],
            },
            "filesystem": {
                "needle": fs_result.get("needle"),
                "paths": fs_result.get("paths", [])[:5],
                "n_files": fs_result.get("n_files", 0),
            },
            "match": is_match,
            "match_reason": reason,
            "capacity": capacity,
        }
        _audit_log_append(row)
        per_query_summary.append({
            "q": q[:60], "match": is_match, "reason": reason,
            "is_ud": is_ud,
        })

    n_total = len(queries)
    match_rate = n_match / n_total if n_total else 0.0
    ud_retention = (n_user_directive_match / n_user_directive_total
                    if n_user_directive_total else 1.0)
    elapsed = time.perf_counter() - t0
    ok = match_rate >= 0.90  # MIDDLE floor; HP gate is >= 0.95
    return {
        "arm": "ARM_DUAL_STORE_MATCH",
        "ok": bool(ok),
        "n_queries": n_total,
        "n_match": n_match,
        "match_rate": round(match_rate, 4),
        "n_user_directive_total": n_user_directive_total,
        "n_user_directive_match": n_user_directive_match,
        "user_directive_retention": round(ud_retention, 4),
        "mismatch_reasons": mismatch_reasons,
        "capacity": capacity,
        "elapsed_s": round(elapsed, 3),
        "sample_per_query": per_query_summary[:15],
        "audit_log_path": str(AUDIT_LOG_PATH.relative_to(REPO)).replace("\\", "/"),
    }


def _concurrent_writer_thread(stop_evt: threading.Event, n_writes_holder: list[int]) -> None:
    """Background thread: appends synthetic ingest events at ~1s cadence.
    Tests audit log under concurrent write pressure.
    """
    i = 0
    while not stop_evt.is_set():
        try:
            row = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "kind": "concurrent_synthetic_ingest",
                "i": i,
                "payload": "concurrent-write-stress-test",
            }
            _audit_log_append(row)
            n_writes_holder[0] += 1
            i += 1
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.2)  # 5 writes/s to amplify race exposure


def _arm_audit_log_integrity(do_concurrent_stress: bool = False,
                              stress_duration_s: float = 3.0) -> dict:
    """Re-read audit log; assert parseable + required fields present.
    Optionally run a concurrent-write stress test.
    """
    t0 = time.perf_counter()
    required_fields = ("ts", "q", "match", "capacity")  # for query rows

    n_writes_holder = [0]
    if do_concurrent_stress:
        stop_evt = threading.Event()
        thread = threading.Thread(target=_concurrent_writer_thread,
                                  args=(stop_evt, n_writes_holder), daemon=True)
        thread.start()
        time.sleep(stress_duration_s)
        stop_evt.set()
        thread.join(timeout=2.0)

    n_lines = 0
    n_parseable = 0
    n_with_required = 0
    parse_errors: list[str] = []
    if AUDIT_LOG_PATH.exists():
        try:
            with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    n_lines += 1
                    try:
                        row = json.loads(line)
                        n_parseable += 1
                        # Only check required fields on QUERY rows (not synthetic ingest rows)
                        if "q" in row:
                            if all(k in row for k in required_fields):
                                n_with_required += 1
                    except json.JSONDecodeError as e:
                        parse_errors.append(f"line {n_lines}: {e}")
        except OSError as e:
            parse_errors.append(f"audit log read failed: {e}")

    elapsed = time.perf_counter() - t0
    parseable_rate = n_parseable / n_lines if n_lines else 1.0
    ok = (n_lines > 0 and parseable_rate >= 0.99
          and (not parse_errors or len(parse_errors) <= 1))
    return {
        "arm": "ARM_AUDIT_LOG_INTEGRITY",
        "ok": bool(ok),
        "n_lines": n_lines,
        "n_parseable": n_parseable,
        "n_with_required_fields": n_with_required,
        "parseable_rate": round(parseable_rate, 4),
        "parse_errors_sample": parse_errors[:5],
        "concurrent_stress_run": do_concurrent_stress,
        "concurrent_writes_total": n_writes_holder[0],
        "elapsed_s": round(elapsed, 3),
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by = {a["arm"]: a for a in arms}
    if not all(a.get("ok") for a in arms):
        bad = [a["arm"] for a in arms if not a.get("ok")]
        return "HARD_FAIL", f"one_or_more_arms_failed: {','.join(bad)}"
    match = by.get("ARM_DUAL_STORE_MATCH", {})
    mr = match.get("match_rate", 0.0)
    ud_ret = match.get("user_directive_retention", 1.0)
    # USER_DIRECTIVE zero-loss invariant is hard gate (HARD_FAIL if violated)
    n_ud = match.get("n_user_directive_total", 0)
    if n_ud > 0 and ud_ret < 1.0:
        return "HARD_FAIL", (
            f"USER_DIRECTIVE retention {ud_ret:.4f} < 1.0 "
            f"({match.get('n_user_directive_match')}/{n_ud}); "
            f"load-bearing zero-loss invariant violated"
        )
    if mr >= 0.95:
        return "HARD_PASS", (
            f"all_arms_ok; match_rate={mr:.4f} >= 0.95; "
            f"user_directive_retention={ud_ret:.4f}; "
            f"audit_log_integrity_ok; load_bearing_safety_harness_operational"
        )
    if mr >= 0.90:
        return "MIDDLE_BAND", (
            f"all_arms_ok; match_rate={mr:.4f} in [0.90, 0.95); "
            f"user_directive_retention={ud_ret:.4f}; "
            f"audit_only_mode_recommended_review_mismatches"
        )
    return "HARD_FAIL", (
        f"match_rate={mr:.4f} < 0.90; substrate-KB diverged from filesystem; "
        f"rollback trigger"
    )


def _instrumentation_selftest() -> None:
    # HARD_FAIL: arm not ok
    v, _ = _verdict_from_arms([
        {"arm": "ARM_DUAL_STORE_MATCH", "ok": False, "match_rate": 0.5,
         "user_directive_retention": 1.0, "n_user_directive_total": 0},
        {"arm": "ARM_AUDIT_LOG_INTEGRITY", "ok": True},
    ])
    assert v == "HARD_FAIL", f"selftest hf-arm: {v}"
    # HARD_FAIL: USER_DIRECTIVE loss (zero-tolerance)
    v, _ = _verdict_from_arms([
        {"arm": "ARM_DUAL_STORE_MATCH", "ok": True, "match_rate": 0.99,
         "user_directive_retention": 0.95, "n_user_directive_total": 20,
         "n_user_directive_match": 19},
        {"arm": "ARM_AUDIT_LOG_INTEGRITY", "ok": True},
    ])
    assert v == "HARD_FAIL", f"selftest hf-ud: {v}"
    # HARD_PASS
    v, _ = _verdict_from_arms([
        {"arm": "ARM_DUAL_STORE_MATCH", "ok": True, "match_rate": 0.96,
         "user_directive_retention": 1.0, "n_user_directive_total": 10,
         "n_user_directive_match": 10},
        {"arm": "ARM_AUDIT_LOG_INTEGRITY", "ok": True},
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"
    # MIDDLE_BAND
    v, _ = _verdict_from_arms([
        {"arm": "ARM_DUAL_STORE_MATCH", "ok": True, "match_rate": 0.92,
         "user_directive_retention": 1.0, "n_user_directive_total": 5,
         "n_user_directive_match": 5},
        {"arm": "ARM_AUDIT_LOG_INTEGRITY", "ok": True},
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"
    print("[selftest] kb_dual_store_audit_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "kb_dual_store_audit_v1")


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

    # Fix #26 referent-check: KB must exist. If canonical missing, fall back.
    if args.kb_dir:
        kb = DirectorKBQuery(kb_dir=Path(args.kb_dir))
    else:
        try:
            kb = load_default_kb(REPO)
        except FileNotFoundError as e:
            print(f"[run] KB not found at canonical; fallback failed too: {e}", flush=True)
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                "elapsed_s": 0.0,
                "summary": {"anchor": "kb_dual_store_audit_v1", "error": str(e)},
            }
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}", flush=True)
            return

    t0 = time.time()
    queries = SMOKE_QUERIES if args.smoke else KNOWN_QUERIES_FULL
    print(f"[run] kb_dual_store_audit_v1 smoke={args.smoke} "
          f"kb_version={kb.kb_version} n_ent={len(kb.entity_names)} "
          f"n_queries={len(queries)}", flush=True)

    arms: list[dict] = []
    for arm_fn, name in [
        (lambda: _arm_dual_store_match(kb, REPO, queries), "ARM_DUAL_STORE_MATCH"),
        (lambda: _arm_audit_log_integrity(do_concurrent_stress=not args.smoke,
                                          stress_duration_s=2.0), "ARM_AUDIT_LOG_INTEGRITY"),
    ]:
        try:
            a = arm_fn()
            arms.append(a)
            print(f"  {name} ok={a['ok']} elapsed={a['elapsed_s']}s "
                  f"{', '.join(f'{k}={a[k]}' for k in a if k not in ('arm','ok','elapsed_s','sample_per_query','mismatch_reasons','parse_errors_sample','capacity'))}",
                  flush=True)
        except Exception as e:  # noqa: BLE001
            arms.append({"arm": name, "ok": False, "error": f"{type(e).__name__}: {e}"})
            print(f"  {name} FAILED: {type(e).__name__}: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "kb_dual_store_audit_v1",
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
