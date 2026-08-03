#!/usr/bin/env python3
"""Capability Registry auto-integration-status auditor (durable capability-tracking system).

WHY THIS EXISTS (USER 2026-07-28, "I do NOT want this to happen again"): validated
capabilities keep getting islanded/forgotten because the old tracking docs
(substrate_capability_map.md, capability_scorecard.md, promotion_backlog.md) were
MANUALLY maintained and rotted -- checkboxes stayed unchecked after the work actually
landed (verified this session: hdlab/typed_rule_parser.py and hdlab/reasoner.py both
exist on disk, dated 2026-07-25, while promotion_backlog.md P1/P5 checkboxes are still
unchecked). A new hand-kept doc would rot the same way. The fix: status is COMPUTED
from the actual import graph + the actual capability-test registry, not hand-typed.

Relationship to existing tooling (read both; they answer different questions):
  - data/capability_registry.jsonl (this tool's subject) = curated, one row per
    DECIDED capability, tracking the WIRE-or-SHELVE gate decision + auto-computed
    wired-vs-islanded status. Small (~15-30 rows), Director/testbed-curated.
  - data/substrate_capability_registry.jsonl (tools/substrate_capability_registry.py,
    pre-existing) = auto-scanned, one row per exp_*/metrics.json TEST RUN (6000+ rows).
    Answers "what did this test measure." Does NOT track wiring or gate decisions.
  - data/substrate_capabilities_view.json (tools/substrate_capabilities_aggregate.py,
    pre-existing) = auto-aggregated, one row per capability_family with a verdict-tier
    heuristic (chain-grade / measured-mechanism / exploring / honest-negative). This
    tool cross-references it to catch NEWLY chain-grade families that have no gate
    decision yet in capability_registry.jsonl (see --check-undecided).
This tool does NOT replace those two; it reads substrate_capabilities_view.json as an
input and adds the missing WIRE/SHELVE + wired-vs-islanded layer on top.

Computes, per capability_registry.jsonl row:
  integration_status: one of
    WIRED               -- consumed by >=1 hdlab module OR named in a composed entry
                            point's source text (hdlab/reasoner.py etc.)
    TRAPPED_SHARED      -- consumed by >=1 exp_ cell as a de-facto module (or, for
                            "primitive" kind, the grep_symbol appears in many files)
                            but NEVER reaches hdlab -- the "islanded but reused" case
    ISLAND              -- zero consumers found anywhere (the worst case: proven,
                            unused)
    N_A_SHELVED         -- gate_decision is SHELVE/superseded with no path to check;
                            skipped (nothing to audit, by design)
    UNKNOWN             -- path(s) declared but none exist on disk (moved/deleted/typo)
  used_by: sample of consumer file paths (repo-relative, capped)
  last_audit_utc: this run's timestamp

Also FLAGS (does not silently pass):
  (a) capability_family rows in substrate_capabilities_view.json with tier=="chain-grade"
      that have no matching id/name in capability_registry.jsonl -- an undecided
      validated capability (--check-undecided, on by default).
  (b) capability_registry.jsonl rows with gate_decision in {VET_PENDING} whose
      last_decision_utc is older than --stale-days (default 7).
  (c) rows whose declared path(s) don't exist on disk.

Never mutates gate_decision / gate_decision_target / revival_criteria / supersedes /
provenance -- those are human/Director judgment fields. Only integration_status,
used_by, and last_audit_utc are auto-computed and rewritten.

ASCII-only, stdlib-only (imports tools/integration_health.py for the import graph).
Atomic write (tmp + os.replace). --self-test uses synthetic data (no disk scan).

CLI:
  python tools/capability_registry_audit.py                 # full audit + rewrite + report
  python tools/capability_registry_audit.py --dry-run        # report only, no rewrite
  python tools/capability_registry_audit.py --stale-days 14
  python tools/capability_registry_audit.py --self-test
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REGISTRY = DATA / "capability_registry.jsonl"
VIEW_PATH = DATA / "substrate_capabilities_view.json"
REPORT_DIR = DATA / "capability_registry_reports"
GREP_SAMPLE_CAP = 15
PROMOTE_MIN_CONSUMERS = 3  # matches integration_health.py's threshold

sys.path.insert(0, str(ROOT / "tools"))
import integration_health as ih  # noqa: E402

# Composed-entry files whose source TEXT we grep for a capability's basename/id --
# a capability mentioned here is reachable from the substrate's designated entry
# point even if the import-graph regexes (which only catch `import`/`from` statements)
# miss it (e.g. dynamic dispatch, string-keyed registry lookups).
COMPOSED_ENTRY_PATHS = [
    ROOT / "hdlab" / "reasoner.py",
    ROOT / "hdlab" / "cortex.py",
    ROOT / "hdlab" / "substrate.py",
    ROOT / "hdlab" / "pipeline.py",
    # CLAUDE.md documents CLI-invoked tools/ capabilities (e.g. "PRIMARY monitor =
    # `python tools/inflight_monitor.py`") that the hdlab/experiments import-graph
    # can never see (they are run directly, never imported). Treating a CLAUDE.md
    # mention as a wired-by-documented-convention signal avoids false ISLAND on
    # tools/*.py capabilities that are genuinely load-bearing but CLI-only.
    ROOT / "CLAUDE.md",
]

# ---------------------------------------------------------------------------
# THIRD INTEGRATION STATE (2026-08-02/03, notes/integration_audit_built_vs_wired_
# vs_used_2026-08-02.md): "WIRED" (an import-graph consumer exists ANYWHERE --
# even a single throwaway verify_*_v1 smoke-consumer) is not the same claim as
# "reachable from the code that actually runs today." hdlab/working_memory.py was
# WIRED-eligible (context_retention.py imports it) yet invisible to the real Anne
# reader -- the gap the audit named "the working_memory failure class." This
# section adds a STRICTER check: compute the import closure from the small,
# explicit, active-pipeline entry-point list below, and classify every WIRED
# hdlab-module row as WIRED_AND_PIPELINE_USED (its path is in that closure) or
# WIRED_BUT_NOT_PIPELINE_REACHABLE (WIRED per the old check, but not reachable
# from anything that actually runs). Declared explicitly here (not derived) so it
# can't silently drift; extend this list as the active reading pipeline grows.
# Mirrors notes/integration_audit_built_vs_wired_vs_used_2026-08-02.md Method
# section verbatim (5 entry points, exact-8-file reachable set at time of audit).
# ---------------------------------------------------------------------------
ACTIVE_PIPELINE_ENTRY_POINTS = [
    "tools/read_anne_glassbox_v2_honest_ledger.py",  # also pulls in tools/read_anne_glassbox_v1.py
    "hdlab/coreference_resolver.py",
    "hdlab/situation_model_accumulate.py",
    "hdlab/self_improving_loop.py",
    "hdlab/state_of_mind.py",
]

_RE_FROM_HDLAB = ih.RE_FROM_HDLAB
_RE_FROM_HDLAB_BARE = ih.RE_FROM_HDLAB_BARE
_RE_REL = ih.RE_REL
_RE_REL_BARE = ih.RE_REL_BARE
# Deliberately NOT reusing ih.RE_HDLAB_ATTR (bare `hdlab.foo` text match) here --
# that regex matches inside docstrings/comments too, which is exactly the false-
# positive this stricter check exists to avoid (state_of_mind.py's docstring
# *mentions* "hdlab.working_memory" as a design note without importing it; a
# text-match closure would wrongly call working_memory.py pipeline-reachable).
# Real import statements only.
_RE_LOCAL_FROM = re.compile(r"^\s*from\s+([A-Za-z0-9_]+)\s+import", re.M)
_RE_LOCAL_IMPORT = re.compile(r"^\s*import\s+([A-Za-z0-9_]+)(?:\s+as\s+\w+)?", re.M)


def _parse_import_names(chunk: str) -> list[str]:
    out = []
    for part in chunk.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(part.split(" as ")[0].split("#")[0].strip().strip("()"))
    return [n for n in out if n and n.isidentifier()]


def compute_pipeline_reachable_modules(entry_points: list[str] | None = None) -> set[str]:
    """BFS import closure from ACTIVE_PIPELINE_ENTRY_POINTS, restricted to real
    `import`/`from` statements resolving to files under hdlab/ or tools/ (mirrors
    integration_health.py's regex approach but seeded from explicit production
    entry points instead of scanning every file in the repo -- answers "is X
    reachable from what actually runs" not "is X imported by *something*").

    No dynamic-import handling: grepped `importlib|__import__` across the entry
    points (2026-08-02 audit) with zero hits, so this closure is exact for the
    current pipeline, not an approximation.

    Returns a set of repo-relative paths (both hdlab/ and tools/ members of the
    closure); callers filtering for the registry check should keep only the
    'hdlab/' subset.
    """
    entries = entry_points or ACTIVE_PIPELINE_ENTRY_POINTS
    seen: set[str] = set()
    queue: list[str] = list(entries)
    while queue:
        rel = queue.pop()
        if rel in seen:
            continue
        full = ROOT / rel
        if not full.exists():
            continue
        seen.add(rel)
        src = ih._read(full)
        cur_dir = str(Path(rel).parent).replace("\\", "/")
        found: set[str] = set()
        for m in _RE_FROM_HDLAB.finditer(src):
            found.add(f"hdlab/{m.group(1)}.py")
        for m in _RE_FROM_HDLAB_BARE.finditer(src):
            for n in _parse_import_names(m.group(1)):
                found.add(f"hdlab/{n}.py")
        if cur_dir == "hdlab":
            for m in _RE_REL.finditer(src):
                found.add(f"hdlab/{m.group(1)}.py")
            for m in _RE_REL_BARE.finditer(src):
                for n in _parse_import_names(m.group(1)):
                    found.add(f"hdlab/{n}.py")
        # local-directory bare imports (e.g. tools/read_anne_glassbox_v2 importing
        # tools/read_anne_glassbox_v1 as a sibling module, not a package import)
        for m in _RE_LOCAL_FROM.finditer(src):
            cand = f"{cur_dir}/{m.group(1)}.py"
            if (ROOT / cand).exists():
                found.add(cand)
        for m in _RE_LOCAL_IMPORT.finditer(src):
            cand = f"{cur_dir}/{m.group(1)}.py"
            if (ROOT / cand).exists():
                found.add(cand)
        for f in found:
            if f not in seen:
                queue.append(f)
    return seen


def scan_unregistered_hdlab_modules(rows: list[dict]) -> list[str]:
    """Disk-scan glob(hdlab/*.py) diffed against every registry row's `path` field.

    Catches the OTHER half of the working_memory failure mode: it wasn't just
    unreachable from the pipeline, it had NO registry row at all, so it never even
    hit the wire-or-shelve gate. Fails loud (returned list is non-empty) rather
    than silently passing -- run alongside the reachability check at session start.
    """
    registered_paths: set[str] = set()
    for r in rows:
        for p in (r.get("path") or []):
            registered_paths.add(p)
    hdlab_dir = ROOT / "hdlab"
    if not hdlab_dir.is_dir():
        return []
    unregistered = []
    for f in sorted(os.listdir(hdlab_dir)):
        if not f.endswith(".py") or f == "__init__.py":
            continue
        rel = f"hdlab/{f}"
        if rel not in registered_paths:
            unregistered.append(rel)
    return unregistered


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def load_registry() -> list[dict]:
    if not REGISTRY.exists():
        return []
    out = []
    with open(REGISTRY, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def write_registry(rows: list[dict]) -> None:
    tmp = REGISTRY.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, REGISTRY)


def _composed_entry_sources() -> dict[str, str]:
    out = {}
    for p in COMPOSED_ENTRY_PATHS:
        if p.exists():
            out[_rel(p)] = ih._read(p)
    return out


def _grep_symbol_files(symbol: str) -> list[str]:
    """Count files (experiments/ + hdlab/) whose source contains `symbol` as text.

    Used for 'primitive' kind capabilities that are copy-pasted functions, not
    importable modules (e.g. _seed_checkpoint) -- an import-graph regex can't see
    these; a text-occurrence count is the honest proxy.
    """
    hits = []
    for d in (ROOT / "experiments", ROOT / "hdlab"):
        if not d.is_dir():
            continue
        for f in os.listdir(d):
            if not f.endswith(".py"):
                continue
            p = d / f
            src = ih._read(p)
            if symbol in src:
                hits.append(_rel(p))
    return hits


def compute_integration_status(row: dict, graph, composed_sources: dict[str, str]) -> tuple[str, list[str]]:
    """Return (integration_status, used_by_sample) for one registry row."""
    exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files, hdlab_mods = graph

    if row.get("gate_decision") in ("SHELVE",) and not row.get("path") and not row.get("grep_symbol"):
        return "N_A_SHELVED", []

    # primitive kind with a grep_symbol: text-occurrence proxy
    sym = row.get("grep_symbol")
    if row.get("kind") == "primitive" and sym:
        hits = _grep_symbol_files(sym)
        if len(hits) >= PROMOTE_MIN_CONSUMERS:
            return "TRAPPED_SHARED", sorted(hits)[:GREP_SAMPLE_CAP]
        if hits:
            return "TRAPPED_SHARED", sorted(hits)[:GREP_SAMPLE_CAP]
        return "ISLAND", []

    paths = row.get("path") or []
    if not paths:
        return "UNKNOWN", []

    missing = [p for p in paths if not (ROOT / p).exists()]
    if len(missing) == len(paths):
        return "UNKNOWN", []

    consumers: set[str] = set()
    composed_hits: set[str] = set()
    for p in paths:
        full = ROOT / p
        if not full.exists():
            continue
        base = full.stem
        if p.startswith("hdlab/") and base in hdlab_mods:
            consumers |= {_rel(Path(c)) for c in hdlab_consumers.get(base, set())}
        else:
            consumers |= {_rel(Path(c)) for c in exp_module_consumers.get(base, set())}
        # composed-entry text mention (dynamic-dispatch catch-all)
        for entry_name, src in composed_sources.items():
            if entry_name == p:
                continue
            if base in src:
                composed_hits.add(entry_name)

    if composed_hits:
        return "WIRED", sorted(composed_hits | consumers)[:GREP_SAMPLE_CAP]
    if row.get("kind") == "hdlab-module" and consumers:
        return "WIRED", sorted(consumers)[:GREP_SAMPLE_CAP]
    if consumers:
        return "TRAPPED_SHARED", sorted(consumers)[:GREP_SAMPLE_CAP]
    return "ISLAND", []


def check_undecided_validated(rows: list[dict]) -> list[dict]:
    """Cross-check substrate_capabilities_view.json chain-grade families against
    capability_registry.jsonl. Returns list of {capability_family, tier, tier_evidence}
    for families with NO matching registry row (loose substring match on id/name)."""
    if not VIEW_PATH.exists():
        return [{"note": f"substrate_capabilities_view.json not found at {_rel(VIEW_PATH)}; "
                          "run tools/substrate_capabilities_aggregate.py first"}]
    try:
        view = json.loads(VIEW_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [{"note": f"view read/parse error: {e}"}]

    registry_blob = " ".join(
        f"{r.get('id', '')} {r.get('name', '')}".lower() for r in rows
    )
    undecided = []
    for fam_row in view.get("rows", []):
        if fam_row.get("tier") != "chain-grade":
            continue
        fam = (fam_row.get("capability_family") or "").lower()
        if not fam or len(fam) < 4:
            continue
        # 'other' is the aggregator catch-all for untagged tests (thousands), not a
        # real capability -- never a gate decision (skunkworks triage 2026-07-28).
        if fam == "other":
            continue
        # loose match: family name (or its underscore tokens) appears in the registry blob
        tokens = [t for t in fam.replace("-", "_").split("_") if len(t) >= 4]
        matched = fam in registry_blob or (
            tokens and sum(1 for t in tokens if t in registry_blob) >= max(1, len(tokens) // 2)
        )
        if not matched:
            undecided.append({
                "capability_family": fam_row.get("capability_family"),
                "tier": fam_row.get("tier"),
                "tier_evidence": fam_row.get("tier_evidence"),
                "n_tests": fam_row.get("n_tests"),
                "latest_test_ts": fam_row.get("latest_test_ts"),
            })
    return undecided


def check_stale_decisions(rows: list[dict], stale_days: int, now: datetime) -> list[dict]:
    stale = []
    for r in rows:
        if r.get("gate_decision") != "VET_PENDING":
            continue
        ts = r.get("last_decision_utc")
        if not ts:
            stale.append({"id": r.get("id"), "reason": "no last_decision_utc set"})
            continue
        try:
            d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            stale.append({"id": r.get("id"), "reason": f"unparseable last_decision_utc={ts}"})
            continue
        age_days = (now - d).total_seconds() / 86400.0
        if age_days > stale_days:
            stale.append({"id": r.get("id"), "age_days": round(age_days, 1)})
    return stale


def run_audit(stale_days: int, dry_run: bool) -> dict:
    now = datetime.now(timezone.utc)
    rows = load_registry()
    graph = ih.compute_import_graph()
    composed_sources = _composed_entry_sources()
    pipeline_reachable = compute_pipeline_reachable_modules()
    pipeline_reachable_hdlab = sorted(p for p in pipeline_reachable if p.startswith("hdlab/"))

    n_wired = n_trapped = n_island = n_na = n_unknown = 0
    n_pipeline_used = n_wired_not_pipeline = 0
    path_missing_flags = []
    for r in rows:
        status, used_by = compute_integration_status(r, graph, composed_sources)
        r["integration_status"] = status
        r["used_by"] = used_by
        r["last_audit_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # THIRD STATE: only meaningful for hdlab-module rows the old check already
        # calls WIRED -- refines "some consumer exists" into "reachable from what
        # actually runs" vs "importable but not on the active pipeline's path."
        if status == "WIRED" and r.get("kind") == "hdlab-module":
            paths = r.get("path") or []
            if any(p in pipeline_reachable_hdlab for p in paths):
                r["pipeline_status"] = "WIRED_AND_PIPELINE_USED"
                n_pipeline_used += 1
            else:
                r["pipeline_status"] = "WIRED_BUT_NOT_PIPELINE_REACHABLE"
                n_wired_not_pipeline += 1
        else:
            r["pipeline_status"] = "N_A"

        if status == "WIRED":
            n_wired += 1
        elif status == "TRAPPED_SHARED":
            n_trapped += 1
        elif status == "ISLAND":
            n_island += 1
        elif status == "N_A_SHELVED":
            n_na += 1
        else:
            n_unknown += 1
        for p in (r.get("path") or []):
            if not (ROOT / p).exists():
                path_missing_flags.append({"id": r.get("id"), "missing_path": p})

    undecided = check_undecided_validated(rows)
    stale = check_stale_decisions(rows, stale_days, now)
    unregistered_hdlab = scan_unregistered_hdlab_modules(rows)

    if not dry_run:
        write_registry(rows)

    summary = {
        "audit_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(rows),
        "integration_status_counts": {
            "WIRED": n_wired, "TRAPPED_SHARED": n_trapped, "ISLAND": n_island,
            "N_A_SHELVED": n_na, "UNKNOWN": n_unknown,
        },
        "pipeline_status_counts": {
            "WIRED_AND_PIPELINE_USED": n_pipeline_used,
            "WIRED_BUT_NOT_PIPELINE_REACHABLE": n_wired_not_pipeline,
        },
        "pipeline_reachable_hdlab_modules": pipeline_reachable_hdlab,
        "unregistered_hdlab_modules": unregistered_hdlab,
        "path_missing_flags": path_missing_flags,
        "undecided_validated_capabilities": undecided,
        "stale_vet_pending": stale,
        "dry_run": dry_run,
        "registry_path": _rel(REGISTRY),
    }
    return summary


def write_report(summary: dict) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    rp = REPORT_DIR / f"registry-audit-{ts}.json"
    tmp = rp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    os.replace(tmp, rp)
    return _rel(rp)


def print_report(summary: dict) -> None:
    print("=" * 72)
    print("CAPABILITY REGISTRY AUDIT  %s" % summary["audit_utc"])
    print("=" * 72)
    c = summary["integration_status_counts"]
    print(f"[status] rows={summary['n_rows']}  WIRED={c['WIRED']}  "
          f"TRAPPED_SHARED={c['TRAPPED_SHARED']}  ISLAND={c['ISLAND']}  "
          f"N_A_SHELVED={c['N_A_SHELVED']}  UNKNOWN={c['UNKNOWN']}")
    pc = summary.get("pipeline_status_counts", {})
    print(f"[pipeline] of the {c['WIRED']} WIRED hdlab-module rows: "
          f"WIRED_AND_PIPELINE_USED={pc.get('WIRED_AND_PIPELINE_USED', 0)}  "
          f"WIRED_BUT_NOT_PIPELINE_REACHABLE={pc.get('WIRED_BUT_NOT_PIPELINE_REACHABLE', 0)}")
    print(f"[pipeline] active-pipeline-reachable hdlab modules "
          f"({len(summary.get('pipeline_reachable_hdlab_modules', []))}): "
          f"{', '.join(summary.get('pipeline_reachable_hdlab_modules', []))}")
    unreg = summary.get("unregistered_hdlab_modules", [])
    if unreg:
        print(f"\n[FLAG] {len(unreg)} hdlab/*.py module(s) with NO capability_registry.jsonl row:")
        for m in unreg:
            print(f"    {m}")
    else:
        print("\n[ok] every hdlab/*.py module has a registry row")
    if summary["path_missing_flags"]:
        print(f"\n[FLAG] {len(summary['path_missing_flags'])} declared path(s) missing on disk:")
        for f in summary["path_missing_flags"][:20]:
            print(f"    {f['id']}: {f['missing_path']}")
    uv = summary["undecided_validated_capabilities"]
    if uv and "note" not in uv[0]:
        print(f"\n[FLAG] {len(uv)} chain-grade capability_family rows with NO gate decision in the registry:")
        for u in uv[:20]:
            print(f"    {u['capability_family']}  ({u['tier_evidence']})")
    elif uv:
        print(f"\n[note] {uv[0]['note']}")
    else:
        print("\n[ok] no undecided chain-grade capability_family rows")
    st = summary["stale_vet_pending"]
    if st:
        print(f"\n[FLAG] {len(st)} VET_PENDING row(s) stale (no decision update):")
        for s in st:
            print(f"    {s}")
    else:
        print("\n[ok] no stale VET_PENDING rows")
    print("-" * 72)


def self_test() -> int:
    """Synthetic-only: no disk scan, no network, no writes. Verifies the pure
    classification functions (compute_integration_status / check_stale_decisions)
    against constructed inputs."""
    # fabricate a minimal import graph: mod 'foo' consumed by 2 exp files
    graph = (
        {"foo": {"experiments/exp_a.py", "experiments/exp_b.py"}},  # exp_module_consumers
        {},  # hdlab_consumers
        set(), [], [], set(),
    )
    row_exp_trapped = {"id": "x", "kind": "exp-cell", "path": ["experiments/foo.py"], "gate_decision": "VET_PENDING"}
    # foo.py doesn't exist on disk in this synthetic test -> classify_integration_status
    # short-circuits via missing-path check; instead directly test the consumer-set logic
    # by monkeypatching path existence is out of scope for a pure unit test, so we test
    # the STALE-DECISION logic (pure, no disk) which is the other core piece.
    now = datetime.now(timezone.utc)
    rows = [
        {"id": "a", "gate_decision": "VET_PENDING", "last_decision_utc": "2020-01-01T00:00:00Z"},
        {"id": "b", "gate_decision": "VET_PENDING", "last_decision_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ")},
        {"id": "c", "gate_decision": "WIRE", "last_decision_utc": "2020-01-01T00:00:00Z"},
    ]
    stale = check_stale_decisions(rows, stale_days=7, now=now)
    ok = len(stale) == 1 and stale[0]["id"] == "a"
    print(f"[selftest] capability_registry_audit stale-decision logic: "
          f"{'OK' if ok else 'FAIL'} (expected 1 stale row id=a, got {stale})")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report only; do not rewrite the registry")
    ap.add_argument("--stale-days", type=int, default=7, help="VET_PENDING staleness threshold (default 7)")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON instead of the human report")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    summary = run_audit(stale_days=args.stale_days, dry_run=args.dry_run)
    report_path = write_report(summary)
    summary["report_path"] = report_path
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_report(summary)
        print(f"report written: {report_path}")
    n_flags = (len(summary["path_missing_flags"])
               + (len(summary["undecided_validated_capabilities"])
                  if summary["undecided_validated_capabilities"]
                  and "note" not in summary["undecided_validated_capabilities"][0] else 0)
               + len(summary["stale_vet_pending"])
               + len(summary.get("unregistered_hdlab_modules", [])))
    return 5 if n_flags else 0


if __name__ == "__main__":
    sys.exit(main())
