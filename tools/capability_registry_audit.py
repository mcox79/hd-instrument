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
  (d) NEW 2026-08-13, REPORT-ONLY (never changes a row): the evidence a row CITES.
      witness_missing        -- row cites a verify_*/witness_* file not on disk at all
      witness_not_collected  -- row cites a witness pytest does not collect under the
                                current pyproject config (outside testpaths, or the
                                filename doesn't match python_files, or it matches but
                                exposes ZERO pytest items because its work sits behind
                                `if __name__ == "__main__":`)
      witness_failing        -- row cites a witness that exits non-zero
      witness_status_unknown -- cited witness has no exit-status evidence yet
      Exit status is read from the results the collected driver
      verification/test_all_witnesses_exit_clean.py persists to
      data/witness_exit_status/ (running ~27 witnesses inline would add ~8 min to a
      session-start audit); pass --run-witnesses to execute them live instead.

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
import tempfile
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
import safe_queue as sq  # noqa: E402 -- reuse the cross-platform (portalocker/msvcrt/
# fcntl auto-selected) file-lock backend already built for queue.json concurrency
# rather than inventing a second locking primitive for this file (house style).

REGISTRY_LOCK_PATH = REGISTRY.with_suffix(".jsonl.lock")

# ---------------------------------------------------------------------------
# COMPOSED ENTRY POINTS -- rewritten 2026-08-13 for defects D1 + D2
# (notes/registry_tighten_audit_2026-08-13.md).
#
# D2 (the critical one): this list used to be grepped as raw TEXT -- a row was
# marked WIRED if its module stem appeared ANYWHERE in one of these files, via
# `if base in src`. That is a bare substring match with a SHORT-CIRCUIT to WIRED
# ahead of every other test, so it could only ever INFLATE the WIRED count. Stems
# like `memory`, `store`, `atoms`, `metrics`, `multi_hop` matched prose, comments,
# unrelated identifiers (`memory` inside `working_memory`) and even the word
# "store" in a docstring, with no import anywhere. REPLACED by a real
# import-reachability closure: a path counts only if it is transitively reachable
# from one of these entry points through actual `import X` / `from X import`
# statements (and, per D3, only statements in real CODE -- strings and comments
# are blanked before matching). There is deliberately NO name-similarity fallback:
# if reachability cannot be established, the honest answer is "not reachable".
#
# D1: `hdlab/substrate.py` and `hdlab/pipeline.py` were declared here and DO NOT
# EXIST -- `git log --all --diff-filter=ADR -- <path>` returns EMPTY for both, i.e.
# they were never created, added, renamed or deleted in the history of this repo.
# They were copied from integration_health.py's COMPOSED_ENTRY_CANDIDATES tuple
# ("reasoner.py", "substrate.py", "pipeline.py"), which is a list of CANDIDATE
# names that script probes with os.path.exists() and reports "ABSENT" for -- it
# never asserted they exist. Rooting the graph at two files that have never
# existed silently shortened the closure. Replacements (evidence per entry below)
# are the entry points that DO exist and are independently documented as what
# actually runs. Missing entries now FAIL LOUD (see validate_entry_paths()).
# ---------------------------------------------------------------------------
COMPOSED_ENTRY_PATHS_REL = [
    # -- surviving originals (exist on disk, unchanged) --
    "hdlab/reasoner.py",
    "hdlab/cortex.py",
    # -- replacements for the two phantom entries --
    # Evidence: these five are the repo's ONLY independently-declared "code that
    # actually runs" root set (ACTIVE_PIPELINE_ENTRY_POINTS below, mirrored from
    # notes/integration_audit_built_vs_wired_vs_used_2026-08-02.md); all five are
    # verified present on disk, unlike substrate.py/pipeline.py which have no git
    # history at all. Using them as composed roots keeps the closure rooted at real
    # production entry points instead of at names that were only ever aspirational.
    "tools/read_anne_glassbox_v2_honest_ledger.py",
    "hdlab/coreference_resolver.py",
    "hdlab/situation_model_accumulate.py",
    "hdlab/self_improving_loop.py",
    "hdlab/state_of_mind.py",
    # -- added 2026-08-15 (hdi_testbed registry-reconcile audit): these two were
    # missing from BOTH entry-point lists even though CLAUDE.md's own evidence-
    # discipline section (2026-08-13) already names them as live -- "hdlab/reading_
    # grounding_loop.py:300-303" is cited as the exact site where pos_tagger/
    # arc_parser/arc_labeler are imported inside a function body "on the live path",
    # and grounding_acquisition_loop.py is named "one of the two live entry points."
    # Both are standalone-runnable (`if __name__ == "__main__":`), not imported by
    # any of the five entries above (verified: grep for the two module names inside
    # coreference_resolver.py / situation_model_accumulate.py / self_improving_loop.py
    # / state_of_mind.py / read_anne_glassbox_v2_honest_ledger.py returns nothing) --
    # they are independent roots, not already-reachable nodes, so omitting them
    # silently truncated the closure. This was the root cause of the 19 (row, module)
    # pairs mismarked WIRED_BUT_NOT_PIPELINE_REACHABLE while measurably live,
    # including reading_grounding_loop's own row.
    "hdlab/reading_grounding_loop.py",
    "hdlab/grounding_acquisition_loop.py",
]

# CLAUDE.md is NOT an entry point and is NO LONGER a WIRED signal (D2). A prose
# mention is a name-similarity match, which is exactly the defect being removed.
# It is still read, but only to report `documented_cli_only` as INFORMATION beside
# the honest reachability verdict -- it never changes integration_status.
DOC_MENTION_PATHS_REL = ["CLAUDE.md"]


def validate_entry_paths() -> list[str]:
    """Return the repo-relative entry paths that are declared but missing on disk.

    D1: a missing entry path used to be skipped silently by _composed_entry_sources()
    (`if p.exists()`), so the import graph could be rooted at a file that does not
    exist and nothing said so. Callers MUST fail loudly on a non-empty return.
    """
    return [p for p in COMPOSED_ENTRY_PATHS_REL + DOC_MENTION_PATHS_REL
            if not (ROOT / p).exists()]

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
    # -- added 2026-08-15, same evidence as the COMPOSED_ENTRY_PATHS_REL addition
    # above: both are independent, standalone-runnable roots that CLAUDE.md's
    # evidence-discipline section already documents as live, and neither was
    # reachable from the other five. See that comment for the full citation.
    "hdlab/reading_grounding_loop.py",
    "hdlab/grounding_acquisition_loop.py",
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
    """BFS import closure from ACTIVE_PIPELINE_ENTRY_POINTS -- "is X reachable from
    what actually RUNS", not "is X imported by *something*".

    D4 (2026-08-13): the hand-rolled regex set this used to carry (hdlab-absolute +
    hdlab-relative + same-directory bare) could not see a package-qualified import into
    any other directory (`from tools.X import`, `from verification.X import`), could not
    see hdlab SUBPACKAGE relative imports (`from .plugins import x` inside hdlab/learner/
    resolved to the wrong file or to nothing), and could not follow a re-export through a
    package `__init__.py`. It now delegates to the ONE shared resolver in
    integration_health (ih.file_import_edges + ih.build_module_index), so this closure and
    the consumer graph can no longer disagree about what an import statement means.

    Dynamic imports: string-literal `importlib.import_module("pkg.mod")` IS followed;
    non-literal ones are unresolvable and are surfaced by ih as
    `undetectable_dynamic_imports` rather than silently skipped.

    Returns a set of repo-relative paths across the scanned dirs; callers filtering for
    the registry check should keep only the 'hdlab/' subset.
    """
    entries = entry_points or ACTIVE_PIPELINE_ENTRY_POINTS
    index, _files = ih.build_module_index(str(ROOT))
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
        raw = ih._read(full)
        code, ok = ih.strip_strings_and_comments(raw)   # D3: real code only
        if not ok:
            ih.CODE_ONLY_PARSE_FAILURES.append(str(full).replace("\\", "/"))
        edges, _dyn = ih.file_import_edges(rel, code, raw, index)
        for target, _lineno in edges:
            if target not in seen:
                queue.append(target)
    return seen


def scan_unregistered_hdlab_modules(rows: list[dict]) -> list[str]:
    """Disk-scan hdlab/**/*.py (recursive) diffed against every registry row's `path` field.

    Catches the OTHER half of the working_memory failure mode: it wasn't just
    unreachable from the pipeline, it had NO registry row at all, so it never even
    hit the wire-or-shelve gate. Fails loud (returned list is non-empty) rather
    than silently passing -- run alongside the reachability check at session start.

    FIX 2026-08-15 (hdi_testbed registry-reconcile audit): this used to be a flat
    os.listdir(hdlab_dir), which only ever sees files directly inside hdlab/ --
    it silently skipped every subpackage (hdlab/learner/*.py, hdlab/learner/
    plugins/*.py, hdlab/dashboard/*.py), 9 files that never got a chance to hit the
    unregistered-module flag at all. os.walk is the same enumerate-from-filesystem
    fix CLAUDE.md's evidence-discipline section prescribes for this exact class of
    blind spot: the audit tool must not be structurally blind to its own subject.
    """
    registered_paths: set[str] = set()
    for r in rows:
        for p in (r.get("path") or []):
            registered_paths.add(p.replace("\\", "/"))
    hdlab_dir = ROOT / "hdlab"
    if not hdlab_dir.is_dir():
        return []
    unregistered = []
    for dirpath, dirnames, filenames in os.walk(hdlab_dir):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in sorted(filenames):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            full = Path(dirpath) / f
            rel = _rel(full)
            if rel not in registered_paths:
                unregistered.append(rel)
    return sorted(unregistered)


# ---------------------------------------------------------------------------
# INVISIBLE-ISLAND DETECTOR (2026-08-04, notes/capability_reconciliation_
# invisible_islands_audit.md "Systemic fix"): the two checks above only ever
# ask "is every REGISTERED capability wired." Neither ever asks "did every
# disk-verified PASS result get a registry row in the first place." That blind
# spot is how exp_theory_of_mind_sally_anne_nested_hrr_v1 (HARD_PASS, oracle
# 1.0, 5 seeds) sat with zero registry rows and zero hdlab promotion --
# invisible to both existing scans because scan_unregistered_hdlab_modules
# only globs hdlab/*.py and never looks at experiments/-only organs at all.
# This section adds the missing direction: scan data/exp_*/metrics.json for
# pass-shaped verdicts, collapse lineage/seed/smoke noise to one base anchor
# per experiment family, and flag any anchor whose core name has no match
# anywhere in the registry.
# ---------------------------------------------------------------------------

HARD_PASS_CACHE_PATH = REPORT_DIR / "hard_pass_anchor_index.json"

# Known-negative/pending verdict-name substrings (uppercased match). Anything
# NOT containing one of these is treated as a "candidate positive" -- a
# denylist is the safer proxy here because pass-verdicts are NOT a fixed
# vocabulary (VAMP-EP alone uses VAMPNOISE_ROBUST / K_STRESS_AGENT_READY /
# DEPTH_CEILING_HIGH / MECHANISM_EARNS -- none contain "HARD_PASS" literally).
# Deliberately does NOT include bare "CEILING": DEPTH_CEILING_HIGH is a PASS.
NEGATIVE_VERDICT_TOKENS = [
    "FAIL", "HONEST_NEG", "PENDING", "INCONCLUSIVE", "MIDDLE_BAND",
    "KILLED", "ABANDONED", "SMOKE",
]

# Trailing-suffix patterns stripped iteratively to collapse a raw exp_*
# directory name to one base anchor per experiment family (lineage/seed/smoke
# noise only -- deliberately conservative, does NOT strip config-sweep
# suffixes like _n4096/_K16/_s13 since those can denote genuinely distinct
# cells within a family; suffix conventions across ~7000 dirs are too
# inconsistent to fully normalize, and over-collapsing risks merging distinct
# capabilities into one anchor).
_ANCHOR_SUFFIX_PATTERNS = [
    re.compile(r"_smoke$"),
    re.compile(r"_localsmoke\d*$"),
    re.compile(r"_local\d+$"),
    re.compile(r"_selftest$"),
    re.compile(r"_seed_?\d+$"),
    re.compile(r"_v\d+[a-z]*$"),
    # harder lineage-collapse (2026-08-04 precision-tier ask): diagnostic/arm/
    # partial-run suffixes that denote the same experiment family run in a
    # different mode, not a distinct capability -- so a lineage counts once.
    re.compile(r"_diag$"),
    re.compile(r"_wholesent$"),
    re.compile(r"_frozen$"),
    re.compile(r"_gatecheck$"),
    re.compile(r"_arm_?[A-Za-z0-9]{1,3}$"),
]

# HIGH-SIGNAL precision tier (2026-08-04): the raw pass-shaped-unregistered set
# is ~3042 -- an alarm that fires 3042 times catches nothing (the same alarm-
# fatigue that hid ToM in the first place). The session-start FLAG must fire
# only on a TRIAGEABLE, high-signal subset (order of dozens); the raw count
# stays as an informational metric. An anchor is HIGH iff pass AND unregistered
# AND (map-named (b))  OR  (comprehension-ORGAN keyword (a) AND a real authored
# non-smoke cell (c)).
#
# marker (a) -- ORGAN vocabulary, NOT the full comprehension keyword list. The
# broader terms (causal/coref/binding/goal/memory/attention/retrieval/temporal/
# reason/hop/hopfield/wm/consolidat) were measured to flood the alarm to
# 113-342 -- they hit (i) low-level VSA/storage substrate primitives that are
# not comprehension organs and (ii) active, already-tracked research frontiers
# with dozens of exploratory cells each. Restricting to the ISLANDED-ORGAN
# vocabulary below yields a ~dozens alarm that still contains every manually-
# confirmed island (ToM, VAMP-EP chain family, grounded-appraisal, coherence-
# selector, situation-model, schema). hdlab-module islands like
# action_selection.py / slot_attention_wm.py are separately caught by
# scan_unregistered_hdlab_modules(), so they are not lost by this narrowing.
#
# All keywords are matched at token edges (underscore/start/end/digit as a
# boundary) so e.g. "valence" does NOT fire inside "equivalence" and "tom"
# does NOT fire inside "atom"/"custom"/"symptom".
_COMPREHENSION_ORGAN_KEYWORDS = [
    "theory_of_mind", "tom", "mentaliz", "appraisal", "valence", "coherence",
    "situation", "schema", "narrative", "vamp",
]
_RE_ORGAN_KW = {
    kw: re.compile(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])")
    for kw in _COMPREHENSION_ORGAN_KEYWORDS
}
# Degenerate/over-collapsed anchor cores (e.g. a dir named "exp_v1" collapses to
# core "") must never qualify -- an empty/short core is a substring of the map
# text and would spuriously map-match. Require a substantive core.
_MIN_CORE_LEN = 6
FUNCTIONAL_MAP_PATH = ROOT / "notes" / "brain_component_functional_map_2026-08-04.md"


def _load_functional_map_text() -> str:
    try:
        return FUNCTIONAL_MAP_PATH.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return ""


def high_signal_markers(core: str, map_text: str) -> list[str]:
    """Return the list of high-signal markers an anchor core name hits (empty =
    not high-signal). (a) ORGAN keyword (token-edge match), (b) named in the
    brain functional map (core is a substring of the map -- catches a full
    anchor name the map cites, e.g. theory_of_mind_sally_anne_nested_hrr).
    Real-authored-cell existence (c) is combined with (a) at the CALL SITE, not
    here -- this fn reports the raw markers; the alarm gate is (b) OR (a AND c)."""
    core_l = core.lower()
    if len(core_l) < _MIN_CORE_LEN:
        return []
    markers = []
    kw_hit = next((kw for kw, rx in _RE_ORGAN_KW.items() if rx.search(core_l)), None)
    if kw_hit is not None:
        markers.append(f"keyword:{kw_hit}")
    if map_text and (core_l in map_text):
        markers.append("map:core-in-map")
    return markers


def collapse_base_anchor(dirname: str) -> str:
    """Strip trailing seed/version/smoke suffixes iteratively (order-independent:
    e.g. `..._v1_seed_7` and `..._seed_7_v1` both collapse the same way) to get
    one base anchor per experiment family. Conservative by design -- see module
    comment above for what it deliberately does NOT strip."""
    name = dirname
    changed = True
    while changed:
        changed = False
        for pat in _ANCHOR_SUFFIX_PATTERNS:
            new = pat.sub("", name)
            if new and new != name:
                name = new
                changed = True
    return name


def anchor_core_name(base_anchor: str) -> str:
    """Base anchor with the leading `exp_` stripped -- the string used for
    registry substring matching (registry paths/ids rarely include the bare
    `exp_` prefix consistently, so stripping it avoids spurious mismatches)."""
    return base_anchor[4:] if base_anchor.startswith("exp_") else base_anchor


def classify_verdict(verdict) -> bool:
    """Return True if `verdict` looks like a pass-shaped result (candidate
    positive needing human triage), False if it matches a known negative/
    pending token or is missing/unparseable. Denylist, not allowlist -- see
    NEGATIVE_VERDICT_TOKENS comment for why."""
    if not verdict or not isinstance(verdict, str):
        return False
    v = verdict.upper()
    return not any(tok in v for tok in NEGATIVE_VERDICT_TOKENS)


def _build_registry_blob(rows: list[dict]) -> list[str]:
    """One lowercased string per registry row: every path-list entry + id +
    name, space-joined. Substring-membership target for anchor matching --
    NOT a single mega-blob (that would let an anchor spuriously "match" by
    straddling two unrelated rows' boundary text) and NOT token-overlap
    (Step 4 of the source audit found token-overlap gives false-registered
    positives on short/common words like "mind"/"nested"/"sally")."""
    out = []
    for r in rows:
        parts = list(r.get("path") or [])
        parts.append(str(r.get("id") or ""))
        parts.append(str(r.get("name") or ""))
        out.append(" ".join(parts).lower())
    return out


def _anchor_registered(core: str, registry_blob: list[str]) -> bool:
    if not core or len(core) < 4:
        return False
    core_lower = core.lower()
    return any(core_lower in entry for entry in registry_blob)


def _load_hard_pass_cache() -> dict:
    if not HARD_PASS_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(HARD_PASS_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_hard_pass_cache(cache: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = HARD_PASS_CACHE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, HARD_PASS_CACHE_PATH)


def scan_unregistered_hard_pass_anchors(rows: list[dict], use_cache: bool = True) -> dict:
    """Scan data/exp_*/metrics.json for pass-shaped verdicts with no registry
    match anywhere. Returns {candidates: [...], n_dirs_scanned, n_dirs_cached,
    n_base_anchors, n_candidates}.

    Per-directory cache (keyed by repo-relative metrics.json path) stores
    (verdict, verdict_msg snippet, mtime); a dir is only re-read if its
    metrics.json mtime changed since the cached entry, so routine re-runs
    after the first full scan stay cheap regardless of how large data/ grows.
    """
    exp_dir = DATA
    cache = _load_hard_pass_cache() if use_cache else {}
    new_cache: dict = {}
    n_scanned = 0
    n_cached = 0
    # anchor_core -> {"verdict", "verdict_msg", "base_anchor", "dirs": [...]}
    anchors: dict[str, dict] = {}

    for mp in sorted(DATA.glob("exp_*/metrics.json")):
        try:
            rel = _rel(mp)
            st_mtime = mp.stat().st_mtime
        except OSError:
            continue
        cached_entry = cache.get(rel)
        if cached_entry and abs(cached_entry.get("mtime", -1) - st_mtime) < 1e-6:
            verdict = cached_entry.get("verdict")
            verdict_msg = cached_entry.get("verdict_msg", "")
            n_cached += 1
        else:
            try:
                j = json.loads(mp.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            verdict = j.get("verdict")
            verdict_msg = str(j.get("verdict_msg") or "")[:200]
            n_scanned += 1
        new_cache[rel] = {"verdict": verdict, "verdict_msg": verdict_msg, "mtime": st_mtime}

        if not classify_verdict(verdict):
            continue
        dirname = mp.parent.name
        base = collapse_base_anchor(dirname)
        core = anchor_core_name(base)
        entry = anchors.setdefault(core, {
            "base_anchor": base, "verdict": verdict, "verdict_msg": verdict_msg, "dirs": [],
        })
        entry["dirs"].append(dirname)

    if use_cache:
        _save_hard_pass_cache(new_cache)

    registry_blob = _build_registry_blob(rows)
    hdlab_dir = ROOT / "hdlab"
    hdlab_stems = set()
    if hdlab_dir.is_dir():
        hdlab_stems = {Path(f).stem for f in os.listdir(hdlab_dir) if f.endswith(".py")}
    map_text = _load_functional_map_text()

    def _real_cell_exists(dirs: list[str]) -> bool:
        # (c): a distinct NON-SMOKE authored experiments/<dir>.py cell exists.
        # Checks the ACTUAL dir names (which retain version/config suffixes,
        # e.g. exp_..._depth_ceiling_v1.py) -- NOT the collapsed base anchor,
        # whose stripped name (..._depth_ceiling.py) would not exist on disk.
        for d in dirs:
            if d.endswith("_smoke") or d.endswith("_selftest") or d.endswith("_localsmoke"):
                continue
            if (ROOT / "experiments" / f"{d}.py").exists():
                return True
        return False

    candidates_all = 0
    candidates_high = []
    for core, entry in sorted(anchors.items()):
        if _anchor_registered(core, registry_blob):
            continue
        candidates_all += 1
        core_lower = core.lower()
        markers = high_signal_markers(core, map_text)
        if not markers:
            continue
        has_kw = any(m.startswith("keyword:") for m in markers)
        has_map = any(m.startswith("map:") for m in markers)
        has_real = _real_cell_exists(entry["dirs"])
        # alarm gate: map-named, OR (organ keyword AND a real authored cell).
        if not (has_map or (has_kw and has_real)):
            continue
        related_hdlab = sorted(
            stem for stem in hdlab_stems
            if len(stem) >= 5 and (stem.lower() in core_lower or core_lower in stem.lower())
        )
        candidates_high.append({
            "anchor": entry["base_anchor"],
            "verdict": entry["verdict"],
            "verdict_msg": entry["verdict_msg"],
            "n_dirs": len(entry["dirs"]),
            "sample_dirs": sorted(entry["dirs"])[:5],
            "high_signal_markers": markers,
            "has_real_cell": has_real,
            "related_hdlab_module": related_hdlab[0] if related_hdlab else None,
        })

    return {
        "candidates_high": candidates_high,
        "n_candidates_high": len(candidates_high),
        "n_candidates_all": candidates_all,
        "n_dirs_scanned_fresh": n_scanned,
        "n_dirs_cached": n_cached,
        "n_base_anchors_pass_shaped": len(anchors),
        "cache_path": _rel(HARD_PASS_CACHE_PATH),
    }


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


# ---------------------------------------------------------------------------
# CONCURRENCY SAFETY (2026-08-12, reported by an agent this session): write_registry()
# above is only atomic for the FINAL install step (tmp + os.replace never leaves a
# torn/partial file on disk). It does NOT protect the READ-MODIFY-WRITE span around
# it -- every registration script in this repo so far (archive/_tmp_register_6_
# modules.py, tools/_tmp_skunkworks_register_batch_2026-08-12.py, and every prior
# skunkworks atomize script) hand-rolls `rows = load_registry(); ...; write_registry
# (rows)` with nothing holding the file between those two calls. Two callers whose
# load...write spans overlap (measured today at ~1s) both read the same starting
# rows, both compute a different addition, and the SECOND os.replace silently
# clobbers the first writer's row -- a lost update, not a crash, so nothing flags
# it. The registry is the WIRE-or-SHELVE durability gate (CLAUDE.md "Capability
# tracking"); a lost row silently un-registers a real capability.
#
# Fix: RegistryLock (below) reuses tools/safe_queue.py's already-proven cross-
# platform lock backend (portalocker / msvcrt / fcntl, auto-selected -- see that
# module's docstring for why each is needed per platform) rather than a second
# hand-rolled primitive. registry_transaction() holds that lock across the ENTIRE
# load+mutate+write span, closing the actual race (RegistryLock alone would only
# help if every caller remembered to acquire it before calling load_registry(),
# which is exactly the kind of manual discipline that has already failed once).
# The lock is tied to the OS file handle/lock, not a sidecar mtime-based sentinel,
# so a crashed holder releases automatically when its process exits -- no stale-
# lock cleanup logic needed.
#
# append_rows() is the new canonical safe entry point for "add N rows" scripts;
# it replaces the reinvented load+refuse-duplicate+tmp+replace+verify pattern each
# prior one-off script wrote for itself.
# ---------------------------------------------------------------------------

class RegistryLock:
    """Cross-process mutual exclusion for capability_registry.jsonl read-modify-
    write sequences. `with RegistryLock():` around a load_registry()...
    write_registry() span makes that whole span one critical section (compare
    write_registry() alone, which only protects the final install). Prefer
    registry_transaction() below for the common case; use this directly only if
    you need custom control over what happens between load and write."""

    def __init__(self, max_wait_s: float = 30.0):
        self.max_wait_s = max_wait_s
        self._fd: int | None = None

    def __enter__(self) -> "RegistryLock":
        REGISTRY_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._fd = os.open(str(REGISTRY_LOCK_PATH), os.O_RDWR | os.O_CREAT, 0o644)
        ok = sq._acquire(self._fd, blocking=True, max_wait_s=self.max_wait_s)
        if not ok:
            os.close(self._fd)
            self._fd = None
            raise TimeoutError(
                f"could not acquire capability_registry lock within {self.max_wait_s}s "
                f"(backend={sq.lock_backend_name()}); another writer is likely stuck")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._fd is not None:
            sq._release(self._fd)
            os.close(self._fd)
            self._fd = None
        return False


class registry_transaction:
    """`with registry_transaction() as txn: txn.rows.append(new_row)` -- holds the
    lock across load+mutate+write as ONE critical section, so two concurrent
    transactions serialize (both land, in some order) instead of racing (second
    write clobbers first). On a clean exit the mutated txn.rows is written back
    atomically; on an exception inside the `with` block, nothing is written (the
    lock is still released). This is the required pattern for any script that
    adds or edits capability_registry.jsonl rows -- see append_rows() for the
    common "append new rows" case, which is built on this."""

    def __init__(self, max_wait_s: float = 30.0):
        self._lock = RegistryLock(max_wait_s=max_wait_s)
        self.rows: list[dict] = []

    def __enter__(self) -> "registry_transaction":
        self._lock.__enter__()
        self.rows = load_registry()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        try:
            if exc_type is None:
                write_registry(self.rows)
        finally:
            self._lock.__exit__(exc_type, exc, tb)
        return False


def append_rows(new_rows: list[dict], max_wait_s: float = 30.0) -> int:
    """Safely append new_rows to capability_registry.jsonl as one locked
    transaction. Refuses (raises ValueError, writes nothing) if any new row's id
    already exists in the registry OR collides with another row in new_rows --
    mirrors the duplicate-guard every prior one-off registration script hand-
    rolled for itself. Returns the new total row count. This is the canonical
    replacement for the load_registry()+tmp+os.replace+verify pattern scripts
    like tools/_tmp_skunkworks_register_batch_2026-08-12.py wrote inline."""
    if not new_rows:
        return len(load_registry())
    seen_new: set[str] = set()
    for r in new_rows:
        rid = r.get("id")
        if not rid:
            raise ValueError(f"REFUSING: new row missing 'id': {r}")
        if rid in seen_new:
            raise ValueError(f"REFUSING: duplicate id within new_rows itself: {rid}")
        seen_new.add(rid)
    with registry_transaction(max_wait_s=max_wait_s) as txn:
        existing_ids = {r.get("id") for r in txn.rows}
        for r in new_rows:
            if r.get("id") in existing_ids:
                raise ValueError(f"REFUSING: id already present, would duplicate: {r.get('id')}")
        txn.rows.extend(new_rows)
        return len(txn.rows)


def compute_composed_reachable(entry_points: list[str] | None = None) -> set[str]:
    """D2: real import-reachability closure from the composed entry points.

    Replaces the old `_composed_entry_sources()` + `if base in src` substring grep.
    A path is in this set only if it is an entry point itself (depth 0 -- the root
    of what runs) or is transitively imported from one via a genuine import
    statement. No name matching, no prose, no fallback.
    """
    missing = validate_entry_paths()
    if missing:
        raise FileNotFoundError(
            "COMPOSED/DOC entry path(s) declared but MISSING on disk: "
            + ", ".join(sorted(missing))
            + " -- the import graph would be rooted at a nonexistent file. "
              "Fix COMPOSED_ENTRY_PATHS_REL before trusting any WIRED verdict.")
    return compute_pipeline_reachable_modules(entry_points or COMPOSED_ENTRY_PATHS_REL)


def _doc_mention_sources() -> dict[str, str]:
    """CLAUDE.md text, for the INFORMATIONAL `documented_cli_only` flag only.
    Never feeds integration_status (D2)."""
    out = {}
    for rel in DOC_MENTION_PATHS_REL:
        p = ROOT / rel
        if p.exists():
            out[rel] = ih._read(p)
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


def compute_integration_status(row: dict, graph, composed_reachable: set[str]) -> tuple[str, list[str]]:
    """Return (integration_status, used_by_sample) for one registry row.

    D2 (2026-08-13): `composed_reachable` is now a SET of repo-relative paths from a
    real import closure (compute_composed_reachable()), not a {path: source_text} map
    grepped with `base in src`."""
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

    # D4 (2026-08-13): path-keyed consumer edges from the WIDENED import graph
    # (tools/->tools/, verification/->anything, backend/, scripts/, hdlab subpackages).
    # The two stem-keyed lookups below can only ever answer for a top-level experiments/
    # or hdlab/ module, so before this a row whose only importer lived in tools/ or
    # verification/ read as a FALSE ISLAND -- the dangerous direction, because it makes
    # us re-wire what is already wired or shelve live capability.
    path_consumers = getattr(graph, "path_consumers", None) or {}

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
        consumers |= {c for c in path_consumers.get(p, set()) if c != p}
        # D2: real import-reachability from a composed entry point, not a text grep.
        if p in composed_reachable:
            composed_hits.add(f"composed-reachable:{p}")

    # D4b: TRAPPED_SHARED means "reused, but ONLY by experiment cells -- never reaches the
    # library/CLI/certification layer" (that is the whole point of the state: islanded-but-
    # reused). An importer in hdlab/, tools/, verification/, backend/ or scripts/ is NOT
    # that case -- it is the library layer, i.e. WIRED. Before the D4 widening this rule
    # was unreachable in practice because no non-hdlab library importer was ever visible.
    library_consumers = sorted(c for c in consumers if not c.startswith("experiments/"))

    if composed_hits:
        return "WIRED", sorted(composed_hits | consumers)[:GREP_SAMPLE_CAP]
    if row.get("kind") == "hdlab-module" and consumers:
        return "WIRED", sorted(consumers)[:GREP_SAMPLE_CAP]
    if library_consumers:
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


# ---------------------------------------------------------------------------
# BRAIN-FIDELITY GATE (2026-08-16, owner standing directive 2026-08-15)
#
# THE OWNER'S WORDS, VERBATIM: "you overlooked that key aspect about brain fidelity - I want
# you to SOLIDIFY that sentiment - you need to approach every problem with that
# consideration." And: "I see you talking about exact-key retrieval only - wtf is that? we
# need to be doing brain foundational things - not maximizing performance in single areas."
#
# THE INCIDENT (cited here so this gate is never unsourced prose): the landed capability
# hdlab/perirhinal_conjunctive.py -- row id `perirhinal_conjunctive` in THIS FILE -- was
# SHELVED with the revival criterion "exact-key retrieval only". That is a PERFORMANCE-
# ENGINEERING framing in a project whose entire thesis is brain fidelity. The brain NEVER
# retrieves with an exact key; it COMPLETES FROM A PARTIAL CUE. The brain-framed criterion is
# that conjunction is not testable until PATTERN COMPLETION (hippocampal CA3) sits in front of
# it, because separation (dentate gyrus) and completion (CA3) are a MATCHED PAIR. The wrong
# frame would have shelved a real component FOR THE WRONG REASON and hidden the actual missing
# organ -- a wrong frame closes a live research direction.
#
# WHAT THIS GATE DOES: every row going forward must declare (1) `brain_structure` -- the NEURAL
# SYSTEM it corresponds to, not a cognitive-theory label -- and (2) `fidelity_basis`, one of
# pinned / invention_under_test / unpinned_and_unstated. Invention is AUTHORISED; presenting an
# invention as pinned is not, which is why the basis is a declared field rather than a vibe.
#
# WHAT THIS GATE DELIBERATELY DOES NOT DO: it does NOT retro-fill the 199 pre-existing rows.
# A fabricated brain justification is WORSE than a missing one -- it would launder invention as
# evidence, which is the exact defect the fidelity_basis field exists to prevent. Pre-existing
# rows are reported as a BACKLOG COUNT for humans to clear honestly, one at a time.
#
# WHY THE EFFECTIVE-DATE SPLIT: a permanently-red 199-row alarm is an alarm nobody reads. This
# file already carries that lesson (the 3042-candidate invisible-island alarm was narrowed to a
# triageable set for exactly this reason: "an alarm that fires 3042 times catches nothing").
# So: rows decided AT OR AFTER the gate landed are VIOLATIONS and count toward the exit code;
# older rows are BACKLOG, reported every run, never auto-filled, never masked.
# ---------------------------------------------------------------------------

# The moment this gate landed. Rows whose last_decision_utc is >= this must comply; anything
# older is backlog. Do NOT move this date backward to "catch" old rows -- that converts a
# clearable backlog into a permanent red and invites exactly the guess-filling this gate bans.
BRAIN_FIDELITY_GATE_EFFECTIVE_UTC = "2026-08-16T01:02:26Z"

VALID_FIDELITY_BASIS = ("pinned", "invention_under_test", "unpinned_and_unstated")

# Report-only heuristics below. Neither ever changes a row or the exit code -- whether a given
# string names a real neural system is a judgment call, and a tool that auto-rejected on a word
# list would just teach people to write anatomy-flavoured noise to get past it.

# Cognitive-theory LABELS that are routinely mistaken for structures. The owner's (a) clause is
# precisely "a neural system, not a cognitive-theory label."
_COGNITIVE_LABEL_TERMS = [
    "working memory", "attention", "binding", "retrieval", "encoding", "short-term memory",
    "long-term memory", "executive function", "cognitive control", "semantic memory",
    "episodic memory", "pattern separation", "pattern completion", "chunking", "priming",
]
# Anatomical / systems-level vocabulary. Presence of ANY of these means the author at least
# reached for a structure, so the label heuristic stands down (e.g. "hippocampal working-memory
# buffer" names a structure AND a label and must not be flagged).
_ANATOMICAL_TERMS = [
    "hippocamp", "ca1", "ca3", "ca2", "dentate", "subiculum", "entorhinal", "perirhinal",
    "parahippocampal", "amygdala", "thalam", "pulvinar", "striat", "caudate", "putamen",
    "basal ganglia", "cerebell", "cortex", "cortical", "gyrus", "sulcus", "prefrontal",
    "mpfc", "vmpfc", "dlpfc", "ifg", "stg", "mtg", "itg", "tpj", "precuneus", "pcc", "acc",
    "insula", "angular", "supramarginal", "fusiform", "occipit", "pariet", "tempor", "frontal",
    "default mode", "dmn", "mtl", "v1", "v2", "v4", "mt", "brainstem", "locus coeruleus",
    "hypothalam", "septal", "fornix", "claustrum", "colliculus", "olfactory", "piriform",
    "neocort", "allocort", "mentalizing network", "language network", "salience network",
]
# Performance-engineering vocabulary in a SHELVE / revival criterion -- the incident's signature.
_PERFORMANCE_FRAME_TERMS = [
    "exact-key", "exact key", "accuracy", "outperform", "beats baseline", "beat the baseline",
    "faster", "speedup", "speed-up", "throughput", "latency", "higher score",
    "improves the metric", "wins on", "sota", "state of the art", "performance improve",
]


def _has_term(text: str, terms: list[str]) -> str | None:
    t = (text or "").lower()
    for term in terms:
        if term in t:
            return term
    return None


def _decided_at_or_after_gate(row: dict) -> bool:
    """True if this row's decision timestamp is at/after the gate's effective moment.

    A row with NO last_decision_utc is treated as BACKLOG, not as a violation: an absent
    timestamp is not evidence the row is new, and guessing 'new' would manufacture violations
    for the same reason retro-filling would manufacture justifications.
    """
    ts = str(row.get("last_decision_utc") or "")
    if not ts:
        return False
    return ts >= BRAIN_FIDELITY_GATE_EFFECTIVE_UTC


# --- the GRADED score, added 2026-08-16 beside the two qualitative fields ---------------
#
# `brain_structure` and `fidelity_basis` ask "did you state it?". `brain_fidelity_score` asks
# "how far off is it?". A row can answer the first two perfectly and describe a component that
# matches nothing, which is why the graded field is separate rather than a refinement.
#
# THE FIELD STORES THE DIMENSIONS, NOT JUST THE NUMBER, AND THE AUDIT RECOMPUTES.  A bare
# number is a number anyone can type; a fabricated score is worse than a missing one for the
# same reason a fabricated brain justification is. Storing the per-dimension verdicts makes
# the total CHECKABLE, and the recompute below is what checks it.
#
# Shape (see tools/brain_fidelity_score.py for the scoring rules and the honesty gate):
#   "brain_fidelity_score": {
#       "mode": "design_time" | "post_hoc",
#       "dimensions": {"D1": 2, "D2": 1, "D3": "NA", "D5": 0, "D6": 2},
#       "points": 5, "max_points": 8}
# `NA` means the brain fact is DOCUMENTED AS UNPINNED and the dimension leaves BOTH numerator
# and denominator. It is not a middle value and it is not free -- tools/brain_fidelity_score.py
# coerces an unsourced NA to 0. Silence (a dimension simply absent) is 0, never NA.
#
# NOT RETRO-FILLED, for the same reason as the two fields above. 200 rows predate this.
BRAIN_FIDELITY_SCORE_FIELD = "brain_fidelity_score"
_BFS_MODE_DIMS = {"design_time": ("D1", "D2", "D3", "D5"),
                  "post_hoc": ("D1", "D2", "D3", "D5", "D6")}
_BFS_VALID_VERDICTS = (0, 1, 2, "NA")


def recompute_brain_fidelity_score(block: dict) -> dict:
    """Recompute points/max_points from the stored per-dimension verdicts.

    This is the anti-fabrication check. It is pure arithmetic and it deliberately does NOT
    import tools/brain_fidelity_score.py -- an audit that trusts the scorer to check the
    scorer is not a check. The two must agree by construction, and the self-test asserts they
    do on a shared fixture.
    """
    mode = str(block.get("mode") or "")
    dims = block.get("dimensions")
    problems = []
    if mode not in _BFS_MODE_DIMS:
        problems.append(f"mode must be one of {list(_BFS_MODE_DIMS)}; got {mode!r}")
        return {"problems": problems, "points": None, "max_points": None}
    if not isinstance(dims, dict):
        problems.append("dimensions must be an object mapping D1..D6 -> 0/1/2/'NA'")
        return {"problems": problems, "points": None, "max_points": None}

    required = _BFS_MODE_DIMS[mode]
    points = 0
    max_points = 0
    for d in required:
        if d not in dims:
            # Silence is a ZERO that stays in the denominator, never an omission and never NA.
            problems.append(f"{d} has no verdict; scored 0 and kept in the denominator "
                            f"(silence is not 'not applicable')")
            max_points += 2
            continue
        v = dims[d]
        if v not in _BFS_VALID_VERDICTS:
            problems.append(f"{d} verdict {v!r} is not one of {list(_BFS_VALID_VERDICTS)}")
            max_points += 2
            continue
        if v == "NA":
            continue                      # leaves numerator AND denominator
        points += int(v)
        max_points += 2
    extra = [d for d in dims if d not in required and d != "D4"]
    if extra:
        problems.append(f"dimensions carries {extra} which mode {mode!r} does not score "
                        f"(D4 is reported, not scored -- see tools/brain_fidelity_score.py)")
    return {"problems": problems, "points": points, "max_points": max_points}


def check_brain_fidelity_fields(rows: list[dict]) -> dict:
    """Report rows missing/invalid `brain_structure` + `fidelity_basis` + the graded
    `brain_fidelity_score`. REPORT-ONLY: never writes a field, never guesses one, never
    mutates a row. See the section comment above for why retro-filling is banned rather than
    merely skipped."""
    violations, backlog, invalid_basis = [], [], []
    suspected_label, revival_not_brain_framed = [], []
    score_inconsistent = []

    for i, r in enumerate(rows, start=1):
        rid = r.get("id")
        bs = (r.get("brain_structure") or "").strip()
        fb = (r.get("fidelity_basis") or "").strip()
        sc = r.get(BRAIN_FIDELITY_SCORE_FIELD)
        missing = [f for f, v in (("brain_structure", bs), ("fidelity_basis", fb)) if not v]
        if not isinstance(sc, dict) or not sc:
            missing.append(BRAIN_FIDELITY_SCORE_FIELD)
        else:
            rc = recompute_brain_fidelity_score(sc)
            stated_p, stated_m = sc.get("points"), sc.get("max_points")
            if rc["problems"] or (rc["points"] is not None
                                  and (stated_p != rc["points"] or stated_m != rc["max_points"])):
                score_inconsistent.append({
                    "row_index": i, "id": rid,
                    "stated": {"points": stated_p, "max_points": stated_m},
                    "recomputed": {"points": rc["points"], "max_points": rc["max_points"]},
                    "problems": rc["problems"],
                    "reason": ("the stored total does not follow from the stored per-dimension "
                               "verdicts. The field stores DIMENSIONS so the number is "
                               "checkable; a number that does not recompute is a fabricated "
                               "score, and a fabricated score is worse than a missing one")})

        if missing:
            entry = {"row_index": i, "id": rid, "missing_fields": missing,
                     "last_decision_utc": r.get("last_decision_utc")}
            if _decided_at_or_after_gate(r):
                violations.append(entry)
            else:
                backlog.append(entry)

        if fb and fb not in VALID_FIDELITY_BASIS:
            invalid_basis.append({"row_index": i, "id": rid, "fidelity_basis": fb,
                                  "allowed": list(VALID_FIDELITY_BASIS)})

        # (a)-clause heuristic: a cognitive-theory label with NO anatomical term anywhere.
        if bs:
            label = _has_term(bs, _COGNITIVE_LABEL_TERMS)
            if label and not _has_term(bs, _ANATOMICAL_TERMS):
                suspected_label.append({
                    "row_index": i, "id": rid, "brain_structure": bs, "matched_label": label,
                    "reason": ("names a cognitive-theory label with no neural system beside it; "
                               "the ask is WHICH BRAIN STRUCTURE (heuristic, report-only)")})

        # (d)-clause heuristic: the incident's own signature -- a SHELVE/revival criterion
        # written in performance-engineering terms with no anatomy anywhere in it.
        rc = str(r.get("revival_criteria") or "")
        if rc:
            perf = _has_term(rc, _PERFORMANCE_FRAME_TERMS)
            if perf and not _has_term(rc, _ANATOMICAL_TERMS):
                revival_not_brain_framed.append({
                    "row_index": i, "id": rid, "matched_performance_term": perf,
                    "revival_criteria_snippet": rc[:180],
                    "reason": ("revival criterion is PERFORMANCE-framed with no brain structure "
                               "named; a shelve reason must be BRAIN-framed (incident: "
                               "perirhinal_conjunctive shelved on 'exact-key retrieval only', "
                               "which hid the missing CA3 pattern-completion organ)")})

    return {
        "brain_fidelity_violations": violations,
        "brain_fidelity_backlog": backlog,
        "brain_fidelity_invalid_basis": invalid_basis,
        "brain_fidelity_suspected_label_not_structure": suspected_label,
        "brain_fidelity_revival_not_brain_framed": revival_not_brain_framed,
        "brain_fidelity_score_inconsistent": score_inconsistent,
        "brain_fidelity_stats": {
            "gate_effective_utc": BRAIN_FIDELITY_GATE_EFFECTIVE_UTC,
            "n_rows": len(rows),
            # The graded score is reported SEPARATELY from the two qualitative fields so the
            # two backlogs never get merged into one comfortable number.
            "n_with_graded_score": sum(
                1 for r in rows if isinstance(r.get(BRAIN_FIDELITY_SCORE_FIELD), dict)
                and r.get(BRAIN_FIDELITY_SCORE_FIELD)),
            "n_graded_score_backlog": sum(
                1 for r in rows if not (isinstance(r.get(BRAIN_FIDELITY_SCORE_FIELD), dict)
                                        and r.get(BRAIN_FIDELITY_SCORE_FIELD))),
            "graded_score_retro_fill": (
                "BANNED, same as the qualitative fields. A fabricated SCORE is worse than a "
                "missing one: it converts a guess into a number that reads like a "
                "measurement. Clearing this backlog is honest per-row work, not a script."),
            "graded_score_tool": "tools/brain_fidelity_score.py",
            # "Compliant" requires a VALID basis, not merely a non-empty one -- a row declaring
            # fidelity_basis:"probably_fine" has answered the question with a non-answer, and
            # counting it as compliant is the kind of soft pass this gate exists to remove.
            "n_compliant": sum(1 for r in rows
                               if (r.get("brain_structure") or "").strip()
                               and (r.get("fidelity_basis") or "").strip() in VALID_FIDELITY_BASIS),
            "n_violations_post_gate": len(violations),
            "n_backlog_pre_gate": len(backlog),
            "valid_fidelity_basis_values": list(VALID_FIDELITY_BASIS),
            "retro_fill": "BANNED -- a fabricated brain justification is worse than a missing one",
            "report_only": True,
        },
    }


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


# ---------------------------------------------------------------------------
# WITNESS-CITATION CHECK (2026-08-13, notes/uncollected_witness_audit_2026-08-13.md)
#
# THE HOLE: this audit computes integration_status from the import graph, but it never
# asked the other half of the WIRE gate -- "is the EVIDENCE this row cites real?" A row
# could be marked WIRED, name a witness in its provenance, and that witness could be
# absent from disk, never collected by pytest, or failing right now, and nothing here
# would say so. Measured off disk 2026-08-13: one row cites a witness that is not in
# verification/ at all; two rows are WIRED on the strength of a witness that FAILS; one
# of those two carries the literal status string "..._pytest_certified" for a file
# pytest has never collected (pyproject's python_files = ["test_*.py"] excludes every
# verify_*/witness_* file, and has since the 2026-05-16 scaffold).
#
# REPORT-ONLY BY CONSTRUCTION. These three fields never mutate gate_decision,
# integration_status, or any other row field -- evidence quality is a Director judgment
# call, and silently downgrading a row on a red witness would just move the lie. The
# thing that actually FAILS on a broken witness is the collected driver
# verification/test_all_witnesses_exit_clean.py; this section makes the registry say
# WHICH rows are standing on that broken evidence.
# ---------------------------------------------------------------------------

WITNESS_DRIVER_REL = "verification/test_all_witnesses_exit_clean.py"
WITNESS_RESULTS_DIR = DATA / "witness_exit_status"

# Matches a witness filename anywhere in a row's JSON text, with or without a leading
# directory (rows cite them both ways: inside `path` as "experiments/verify_x_v1.py",
# and in free-text provenance as a bare "verify_x.py").
_RE_WITNESS_CITATION = re.compile(
    r"((?:[A-Za-z0-9_.\-]+/)*(?:verify|witness)_[A-Za-z0-9_]+\.py)")

# verification/ modules that are NOT witnesses (kept in sync with the driver's
# NON_WITNESS_SUPPORT_MODULES); none of them match the regex above, listed for clarity.
_WITNESS_SUPPORT_MODULES = frozenset({"__init__.py", "run_certification.py",
                                      "oracle.py", "theory.py"})


def _pytest_collection_config() -> tuple[list[str], list[str]]:
    """Read testpaths + python_files out of pyproject.toml [tool.pytest.ini_options].

    Read from the config rather than hardcoded, so that if someone widens the glob this
    check follows them instead of reporting a stale answer.
    """
    testpaths, python_files = ["verification"], ["test_*.py"]
    pp = ROOT / "pyproject.toml"
    try:
        import tomllib  # py3.11 stdlib
        cfg = tomllib.loads(pp.read_text(encoding="utf-8"))
        ini = cfg.get("tool", {}).get("pytest", {}).get("ini_options", {})
        tp = ini.get("testpaths")
        pf = ini.get("python_files")
        if isinstance(tp, str):
            tp = tp.split()
        if isinstance(pf, str):
            pf = pf.split()
        if tp:
            testpaths = list(tp)
        if pf:
            python_files = list(pf)
    except (OSError, ImportError, ValueError):
        pass
    return testpaths, python_files


def _file_exposes_pytest_items(path: Path) -> bool:
    """AST: does this file define a top-level `test*` function or a `Test*` class with a
    `test*` method? (pytest's default python_functions/python_classes; neither is
    overridden in pyproject.) Work behind `if __name__ == "__main__":` is NOT an item --
    that is exactly the 18-file trap the driver exists to close."""
    import ast
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, SyntaxError, ValueError):
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            return True
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test"):
                    return True
    return False


def _resolve_witness(citation: str) -> str | None:
    """Map a cited witness string to a repo-relative path that exists, or None."""
    import fnmatch as _fn  # noqa: F401 -- (kept local; see _witness_is_collected)
    cand = citation.replace("\\", "/")
    if "/" in cand and (ROOT / cand).is_file():
        return cand
    base = Path(cand).name
    for d in ("verification", "experiments", "tools", "hdlab", "scripts", "backend"):
        if (ROOT / d / base).is_file():
            return f"{d}/{base}"
    hits = sorted(p for p in ROOT.glob(f"**/{base}")
                  if p.is_file() and ".venv" not in p.parts and "__pycache__" not in p.parts)
    return _rel(hits[0]) if hits else None


def _witness_is_collected(rel_path: str, testpaths: list[str], python_files: list[str]) -> tuple[bool, str]:
    """(collected, reason). Collected == inside a testpaths dir AND filename matches a
    python_files glob AND the file actually exposes >=1 pytest item."""
    import fnmatch
    p = Path(rel_path)
    if not any(rel_path == tp or rel_path.startswith(tp.rstrip("/") + "/") for tp in testpaths):
        return False, f"outside pytest testpaths {testpaths} (lives in {p.parent.as_posix()}/)"
    if not any(fnmatch.fnmatch(p.name, g) for g in python_files):
        return False, f"filename does not match python_files {python_files}"
    if not _file_exposes_pytest_items(ROOT / rel_path):
        return False, "matches the glob but exposes ZERO pytest items (work is behind __main__)"
    return True, "collected"


def _load_driver_results() -> dict:
    """Newest per-witness exit statuses persisted by the collected driver
    (data/witness_exit_status/<stem>.json, written by WITNESS_DRIVER_REL)."""
    out: dict[str, dict] = {}
    if not WITNESS_RESULTS_DIR.is_dir():
        return out
    for f in sorted(WITNESS_RESULTS_DIR.glob("*.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        name = j.get("witness") or (f.stem + ".py")
        out[name] = j
    return out


def _run_witness(rel_path: str, timeout_s: int = 600) -> dict:
    """Execute one witness as a subprocess (same contract as the driver). Only used with
    --run-witnesses; the default path reads the driver's persisted results instead."""
    import subprocess
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    cmd = [str(py) if py.exists() else sys.executable, str(ROOT / rel_path)]
    try:
        pr = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout_s)
        return {"witness": Path(rel_path).name, "returncode": pr.returncode,
                "timed_out": False, "passed": pr.returncode == 0,
                "run_utc": _utc_now_iso(), "source": "live"}
    except subprocess.TimeoutExpired:
        return {"witness": Path(rel_path).name, "returncode": None, "timed_out": True,
                "passed": False, "run_utc": _utc_now_iso(), "source": "live"}


def check_registry_witnesses(rows: list[dict], run_witnesses: bool = False) -> dict:
    """Cross-check every witness a registry row cites: does it EXIST, is it COLLECTED by
    pytest under the current config, and does it EXIT 0?

    Returns report-only lists. Nothing here mutates a row.
    """
    testpaths, python_files = _pytest_collection_config()
    driver_results = _load_driver_results()

    # row_index is 1-based to match the JSONL line numbers used in the audit notes.
    citations: dict[str, list[dict]] = {}   # citation string -> [{row_index, id}]
    for i, r in enumerate(rows, start=1):
        blob = json.dumps(r, ensure_ascii=False)
        seen_in_row: set[str] = set()
        for m in _RE_WITNESS_CITATION.finditer(blob):
            cit = m.group(1).replace("\\", "/")
            if Path(cit).name in _WITNESS_SUPPORT_MODULES:
                continue
            if cit in seen_in_row:
                continue
            seen_in_row.add(cit)
            citations.setdefault(cit, []).append({"row_index": i, "id": r.get("id")})

    missing, not_collected, failing, unknown_status = [], [], [], []
    resolved: dict[str, str] = {}
    for cit in sorted(citations):
        rel = _resolve_witness(cit)
        if rel is None:
            for owner in citations[cit]:
                missing.append({**owner, "cited_witness": cit,
                                "reason": "no such file anywhere in the repo"})
            continue
        resolved[cit] = rel
        collected, reason = _witness_is_collected(rel, testpaths, python_files)
        if not collected:
            for owner in citations[cit]:
                not_collected.append({**owner, "cited_witness": cit,
                                      "resolved_path": rel, "reason": reason})

    # exit-status pass: one execution/lookup per distinct resolved witness.
    status_cache: dict[str, dict] = {}
    for cit, rel in resolved.items():
        if rel in status_cache:
            continue
        name = Path(rel).name
        if run_witnesses:
            status_cache[rel] = _run_witness(rel)
        elif name in driver_results:
            status_cache[rel] = {**driver_results[name], "source": "driver_results"}
        else:
            status_cache[rel] = {"passed": None, "source": "no_result_on_disk"}

    for cit, rel in sorted(resolved.items()):
        st = status_cache.get(rel, {})
        for owner in citations[cit]:
            entry = {**owner, "cited_witness": cit, "resolved_path": rel,
                     "returncode": st.get("returncode"), "timed_out": st.get("timed_out"),
                     "evidence_source": st.get("source"), "run_utc": st.get("run_utc")}
            if st.get("passed") is False:
                failing.append(entry)
            elif st.get("passed") is None:
                unknown_status.append({**entry, "reason":
                                       f"no persisted result; run `pytest {WITNESS_DRIVER_REL}` "
                                       "or pass --run-witnesses"})

    return {
        "witness_missing": missing,
        "witness_not_collected": not_collected,
        "witness_failing": failing,
        "witness_status_unknown": unknown_status,
        "witness_check_stats": {
            "n_rows_scanned": len(rows),
            "n_distinct_citations": len(citations),
            "n_resolved": len(resolved),
            "pytest_testpaths": testpaths,
            "pytest_python_files": python_files,
            "exit_status_source": ("live subprocess runs (--run-witnesses)" if run_witnesses
                                   else f"persisted driver results in {_rel(WITNESS_RESULTS_DIR)} "
                                        f"({len(driver_results)} file(s)) written by {WITNESS_DRIVER_REL}"),
            "report_only": True,
        },
    }


def run_audit(stale_days: int, dry_run: bool, skip_hard_pass_scan: bool = False,
              run_witnesses: bool = False) -> dict:
    now = datetime.now(timezone.utc)
    # D1: fail LOUD, before any scanning, if an entry path is declared but missing.
    missing_entries = validate_entry_paths()
    if missing_entries:
        raise FileNotFoundError(
            "AUDIT ABORTED -- declared entry path(s) missing on disk: "
            + ", ".join(sorted(missing_entries)))
    graph = ih.compute_import_graph()
    composed_reachable = compute_composed_reachable()
    doc_sources = _doc_mention_sources()
    pipeline_reachable = compute_pipeline_reachable_modules()
    pipeline_reachable_hdlab = sorted(p for p in pipeline_reachable if p.startswith("hdlab/"))

    # Hold the registry lock across load -> mutate -> write as one critical section.
    # The audit rewrites integration_status/used_by/last_audit_utc/pipeline_status on
    # every row, i.e. it is itself a read-modify-write writer of this file (run at
    # SESSION START and on the meta_audit cadence, per CLAUDE.md) -- the same class of
    # race that caused the reported lost-update bug for one-off registration scripts.
    # The expensive read-only scans above (import graph, pipeline closure) deliberately
    # stay OUTSIDE the lock so this doesn't hold other writers up any longer than needed.
    with RegistryLock():
        rows = load_registry()

        n_wired = n_trapped = n_island = n_na = n_unknown = 0
        n_pipeline_used = n_wired_not_pipeline = 0
        path_missing_flags = []
        doc_only_rows = []
        for r in rows:
            status, used_by = compute_integration_status(r, graph, composed_reachable)
            r["integration_status"] = status
            r["used_by"] = used_by
            r["last_audit_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

            # INFORMATIONAL ONLY (D2): a CLAUDE.md prose mention no longer makes a row
            # WIRED. Reported separately so a genuinely CLI-only tool row is still
            # visible as documented rather than being lost among the ISLANDs.
            if status in ("ISLAND", "UNKNOWN"):
                for p in (r.get("path") or []):
                    stem = Path(p).stem
                    if any(stem in src for src in doc_sources.values()):
                        doc_only_rows.append({"id": r.get("id"), "path": p,
                                              "note": "named in CLAUDE.md prose only; NOT import-reachable"})
                        break

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
        # BRAIN-FIDELITY GATE (report-only; never writes or guesses a field). Runs INSIDE the
        # lock only because it reads `rows`; it contributes nothing to the write-back.
        fidelity_report = check_brain_fidelity_fields(rows)
        # REPORT-ONLY (2026-08-13): does the evidence each row cites exist / get collected /
        # pass? Never mutates a row -- see check_registry_witnesses() docstring.
        witness_report = check_registry_witnesses(rows, run_witnesses=run_witnesses)
        unregistered_hdlab = scan_unregistered_hdlab_modules(rows)
        if skip_hard_pass_scan:
            island_scan = {"candidates_high": [], "skipped": True}
        else:
            island_scan = scan_unregistered_hard_pass_anchors(rows)

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
        "composed_entry_points": list(COMPOSED_ENTRY_PATHS_REL),
        "composed_reachable_paths": sorted(composed_reachable),
        # D4: what the import graph could actually SEE this run. Before 2026-08-13 this
        # was ["experiments", "hdlab"] non-recursive and everything else was invisible.
        "import_graph_scan": {
            "wide": getattr(graph, "wide", False),
            "scanned_dirs": getattr(graph, "scanned_dirs", []),
            "n_scanned_files": len(getattr(graph, "scanned_files", [])),
            "n_path_edges": sum(len(v) for v in (getattr(graph, "path_consumers", {}) or {}).values()),
        },
        # Statically UNRESOLVABLE dynamic imports (importlib/__import__ on a non-literal).
        # Recorded, not silently dropped: any module reachable only this way can still
        # read as an ISLAND and no static graph can prove otherwise.
        "undetectable_dynamic_imports": getattr(graph, "undetectable_dynamic_imports", [])[:200],
        "n_undetectable_dynamic_imports": len(getattr(graph, "undetectable_dynamic_imports", [])),
        "documented_cli_only_rows": doc_only_rows,
        "code_only_parse_failures": sorted(set(ih.CODE_ONLY_PARSE_FAILURES)),
        "unregistered_hdlab_modules": unregistered_hdlab,
        "path_missing_flags": path_missing_flags,
        "undecided_validated_capabilities": undecided,
        "stale_vet_pending": stale,
        "invisible_island_candidates_HIGH": island_scan.get("candidates_high", []),
        "invisible_island_candidates_ALL_count": island_scan.get("n_candidates_all", 0),
        "invisible_island_scan_stats": {
            k: v for k, v in island_scan.items() if k != "candidates_high"
        },
        "dry_run": dry_run,
        "registry_path": _rel(REGISTRY),
    }
    summary.update(witness_report)
    summary.update(fidelity_report)
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
    ig = summary.get("import_graph_scan", {})
    print(f"[graph] wide={ig.get('wide')}  dirs={','.join(ig.get('scanned_dirs', []))}  "
          f"files={ig.get('n_scanned_files', 0)}  edges={ig.get('n_path_edges', 0)}  "
          f"unresolvable-dynamic-imports={summary.get('n_undetectable_dynamic_imports', 0)}")
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
    isl = summary.get("invisible_island_candidates_HIGH", [])
    n_all = summary.get("invisible_island_candidates_ALL_count", 0)
    stats = summary.get("invisible_island_scan_stats", {})
    if stats.get("skipped"):
        print("\n[note] invisible-island hard-pass scan skipped (--skip-hard-pass-scan)")
    else:
        print(f"\n[info] total pass-shaped unregistered anchors: {n_all} (informational, NOT the alarm; "
              f"scanned {stats.get('n_dirs_scanned_fresh', 0)} fresh + {stats.get('n_dirs_cached', 0)} cached dirs)")
        if isl:
            print(f"[FLAG] HIGH-signal invisible islands: {len(isl)} (pass-shaped, unregistered, map-named OR "
                  f"organ-keyword+real-cell -- the triageable alarm set):")
            for c in isl[:60]:
                hdlab_note = f" [related hdlab: {c['related_hdlab_module']}]" if c.get("related_hdlab_module") else ""
                mk = ",".join(c.get("high_signal_markers", []))
                print(f"    {c['anchor']}  verdict={c['verdict']}  ({mk}){hdlab_note}")
        else:
            print("[ok] no HIGH-signal invisible-island candidates")

    # --- witness-citation check (report-only; never changes a row's status) ---
    ws = summary.get("witness_check_stats", {})
    if ws:
        print(f"\n[witness] {ws.get('n_distinct_citations', 0)} distinct witness citation(s) "
              f"across {ws.get('n_rows_scanned', 0)} rows; pytest testpaths="
              f"{ws.get('pytest_testpaths')} python_files={ws.get('pytest_python_files')}")
        print(f"[witness] exit-status evidence: {ws.get('exit_status_source')}")
    for field, label in (("witness_missing", "cited witness FILE NOT ON DISK"),
                         ("witness_not_collected", "cited witness NOT COLLECTED by pytest"),
                         ("witness_failing", "cited witness EXITS NON-ZERO"),
                         ("witness_status_unknown", "cited witness exit status UNKNOWN")):
        items = summary.get(field, [])
        if items:
            print(f"\n[FLAG] {len(items)} row-citation(s): {label}  ({field}, report-only)")
            for it in items[:30]:
                print(f"    row {it.get('row_index')} {it.get('id')} -> {it.get('cited_witness')}"
                      + (f"  [{it.get('reason')}]" if it.get("reason") else "")
                      + (f"  rc={it.get('returncode')}" if it.get("returncode") is not None else ""))
        else:
            print(f"[ok] no rows with: {label}")

    # --- brain-fidelity gate (report-only; never retro-fills) ---
    bf = summary.get("brain_fidelity_stats", {})
    if bf:
        print(f"\n[brain-fidelity] gate effective {bf.get('gate_effective_utc')} -- every row "
              f"DECIDED at/after that must declare brain_structure + fidelity_basis "
              f"({'/'.join(bf.get('valid_fidelity_basis_values', []))}).")
        print(f"[brain-fidelity] compliant={bf.get('n_compliant')}/{bf.get('n_rows')}  "
              f"post-gate VIOLATIONS={bf.get('n_violations_post_gate')}  "
              f"pre-gate BACKLOG={bf.get('n_backlog_pre_gate')} (reported, never auto-filled: "
              f"a fabricated brain justification is worse than a missing one)")
        print(f"[brain-fidelity] GRADED SCORE (brain_fidelity_score): "
              f"present={bf.get('n_with_graded_score')}/{bf.get('n_rows')}  "
              f"BACKLOG={bf.get('n_graded_score_backlog')} -- NOT retro-filled. "
              f"Score a row with {bf.get('graded_score_tool')}; the field stores the "
              f"per-dimension verdicts so this audit can RECOMPUTE the total.")
    sci = summary.get("brain_fidelity_score_inconsistent", [])
    if sci:
        print(f"\n[FLAG] {len(sci)} row(s) whose brain_fidelity_score does NOT recompute from "
              f"its own per-dimension verdicts (a number that does not recompute is a "
              f"FABRICATED score):")
        for v in sci[:30]:
            print(f"    row {v['row_index']} {v['id']} -> stated {v['stated']} vs recomputed "
                  f"{v['recomputed']}"
                  + (f"  {v['problems']}" if v["problems"] else ""))
    else:
        print("[ok] every brain_fidelity_score present recomputes from its own dimensions")
    viol = summary.get("brain_fidelity_violations", [])
    if viol:
        print(f"\n[FLAG] {len(viol)} row(s) decided AFTER the brain-fidelity gate with missing "
              f"field(s) -- WHICH BRAIN STRUCTURE, and are we replicating it or substituting "
              f"something convenient?")
        for v in viol[:30]:
            print(f"    row {v['row_index']} {v['id']} -> missing {', '.join(v['missing_fields'])}"
                  f"  (decided {v.get('last_decision_utc')})")
    else:
        print("[ok] no post-gate rows missing brain_structure / fidelity_basis")
    inv = summary.get("brain_fidelity_invalid_basis", [])
    if inv:
        print(f"\n[FLAG] {len(inv)} row(s) with an invalid fidelity_basis value:")
        for v in inv[:30]:
            print(f"    row {v['row_index']} {v['id']} -> {v['fidelity_basis']!r} "
                  f"(allowed: {', '.join(v['allowed'])})")
    lab = summary.get("brain_fidelity_suspected_label_not_structure", [])
    if lab:
        print(f"\n[hint] {len(lab)} row(s) whose brain_structure reads as a COGNITIVE-THEORY "
              f"LABEL with no neural system beside it (heuristic, report-only):")
        for v in lab[:20]:
            print(f"    row {v['row_index']} {v['id']} -> {v['brain_structure']!r} "
                  f"[matched: {v['matched_label']}]")
    rev = summary.get("brain_fidelity_revival_not_brain_framed", [])
    if rev:
        print(f"\n[hint] {len(rev)} revival criterion/criteria written in PERFORMANCE terms with "
              f"no brain structure named (heuristic, report-only -- this is the "
              f"perirhinal_conjunctive incident's own signature):")
        for v in rev[:20]:
            print(f"    row {v['row_index']} {v['id']} [matched: {v['matched_performance_term']}]")
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

    # invisible-island classify + match logic (synthetic fixture, no disk scan)
    ok2 = True
    cases = [
        ("HARD_PASS", True), ("DEPTH_CEILING_HIGH", True), ("K_STRESS_AGENT_READY", True),
        ("MECHANISM_EARNS", True), ("VAMPNOISE_ROBUST", True),
        ("HARD_FAIL", False), ("HONEST_NEG", False), ("VET_PENDING", False),
        ("INCONCLUSIVE", False), ("MIDDLE_BAND", False), ("KILLED", False),
        ("ABANDONED", False), ("SMOKE_PASS", False), (None, False), ("", False),
    ]
    for verdict, expected in cases:
        got = classify_verdict(verdict)
        if got != expected:
            ok2 = False
            print(f"[selftest] classify_verdict({verdict!r}) = {got}, expected {expected}")

    fixture_rows = [
        {"id": "predictive_coding", "name": "predictive_coding (triaged 07-28)",
         "path": ["hdlab/predictive_coding.py"]},
        {"id": "working_memory_multibank_K_capacity", "name": "hdlab/working_memory.py -- multi-bank",
         "path": ["hdlab/working_memory.py",
                  "experiments/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1.py"]},
    ]
    blob = _build_registry_blob(fixture_rows)
    # registered: anchor's core name is a genuine substring of a registered path
    reg_core = anchor_core_name(collapse_base_anchor(
        "exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1"))
    # unregistered: ToM anchor, not present anywhere in the fixture registry
    unreg_core = anchor_core_name(collapse_base_anchor("exp_theory_of_mind_sally_anne_nested_hrr_v1"))
    ok3 = _anchor_registered(reg_core, blob) and not _anchor_registered(unreg_core, blob)
    if not ok3:
        print(f"[selftest] anchor-match FAIL: registered-case={_anchor_registered(reg_core, blob)} "
              f"(expect True), unregistered-case={_anchor_registered(unreg_core, blob)} (expect False)")

    # high-signal marker logic (synthetic, no disk): ORGAN keyword (token-edge
    # match) + map reference; degenerate/short cores + boundary false-positives
    # excluded.
    ok4 = True
    map_fixture = "the theory_of_mind_sally_anne_nested_hrr_v1 organ and vamp_chain solver"
    hi_cases = [
        ("theory_of_mind_sally_anne_nested_hrr", True),   # keyword tom + map
        ("wave14_vamp_chain_depth_ceiling", True),        # keyword vamp
        ("grounded_appraisal_sim_earned", True),          # keyword appraisal
        ("situation_model_multibank_capacity", True),     # keyword situation
        ("coherence_selector_text_transfer", True),       # keyword coherence
        ("cortex_schema_instantiation_context_prior", True),  # keyword schema
        ("substrate_distill_verify_operator_equivalence", False),  # 'valence' must NOT fire in 'equivalence'
        ("atom_custom_bottom_symptom_reason", False),     # 'tom' must NOT fire inside atom/custom/symptom
        ("saad_solla_n4096_m_sweep", False),              # no organ keyword
        ("multi_hop_caching_baseline", False),            # substrate primitive, not an organ
        ("x", False),                                     # degenerate short core -> no map false-match
        ("", False),
    ]
    for core, expected in hi_cases:
        got = bool(high_signal_markers(core, map_fixture))
        if got != expected:
            ok4 = False
            print(f"[selftest] high_signal_markers({core!r}) -> {got}, expected {expected} "
                  f"(markers={high_signal_markers(core, map_fixture)})")

    # Concurrency-safety self-test (the one exception to "no writes" above): exercises
    # RegistryLock / registry_transaction / append_rows against a THROWAWAY temp file
    # only -- never data/capability_registry.jsonl. Monkeypatches the module globals
    # for the duration and restores them in a finally regardless of outcome.
    global REGISTRY, REGISTRY_LOCK_PATH
    _orig_registry, _orig_lock = REGISTRY, REGISTRY_LOCK_PATH
    ok5 = True
    try:
        with tempfile.TemporaryDirectory() as td:
            REGISTRY = Path(td) / "capability_registry.jsonl"
            REGISTRY_LOCK_PATH = REGISTRY.with_suffix(".jsonl.lock")
            write_registry([{"id": "seed", "name": "seed", "kind": "exp-cell", "path": []}])

            n = append_rows([
                {"id": "a", "name": "a", "kind": "exp-cell", "path": []},
                {"id": "b", "name": "b", "kind": "exp-cell", "path": []},
            ])
            ids_after = {r["id"] for r in load_registry()}
            if n != 3 or ids_after != {"seed", "a", "b"}:
                ok5 = False
                print(f"[selftest] append_rows FAIL: n={n} ids={ids_after}")

            # duplicate-id refusal must raise ValueError and must NOT alter the file
            try:
                append_rows([{"id": "a", "name": "dup", "kind": "exp-cell", "path": []}])
                ok5 = False
                print("[selftest] append_rows FAIL: duplicate id was not refused")
            except ValueError:
                pass
            ids_after_dup = {r["id"] for r in load_registry()}
            if ids_after_dup != {"seed", "a", "b"}:
                ok5 = False
                print(f"[selftest] append_rows FAIL: refused duplicate still mutated file: {ids_after_dup}")

            # exclusivity: a second lock acquire while the first is held must NOT
            # succeed -- proves this is a real mutex, not a no-op wrapper.
            outer = RegistryLock(max_wait_s=30.0)
            outer.__enter__()
            try:
                inner = RegistryLock(max_wait_s=0.3)
                try:
                    inner.__enter__()
                    ok5 = False
                    print("[selftest] RegistryLock FAIL: nested acquire succeeded (should have blocked)")
                    inner.__exit__(None, None, None)
                except TimeoutError:
                    pass  # expected: second acquire blocks until timeout
            finally:
                outer.__exit__(None, None, None)
    finally:
        REGISTRY, REGISTRY_LOCK_PATH = _orig_registry, _orig_lock

    # witness-citation logic (2026-08-13). Pure/synthetic except _witness_is_collected's
    # AST step, which is exercised against real files in verification/ (read-only).
    ok6 = True
    cit_cases = [
        ('{"path": ["experiments/verify_encoder_retrain_persist_loader_v1.py"]}',
         ["experiments/verify_encoder_retrain_persist_loader_v1.py"]),
        ('{"provenance": "see verify_goal_typing.py and witness_did_it_happen_occurrence_gate_v1.py"}',
         ["verify_goal_typing.py", "witness_did_it_happen_occurrence_gate_v1.py"]),
        ('{"provenance": "no witness cited here, just test_foo.py"}', []),
    ]
    for blob, expected in cit_cases:
        got = [m.group(1) for m in _RE_WITNESS_CITATION.finditer(blob)]
        if got != expected:
            ok6 = False
            print(f"[selftest] witness-citation regex on {blob[:50]!r} -> {got}, expected {expected}")
    # a verify_* file inside testpaths is NOT collected under the default glob
    coll, why = _witness_is_collected("verification/verify_goal_typing.py",
                                      ["verification"], ["test_*.py"])
    if coll or "python_files" not in why:
        ok6 = False
        print(f"[selftest] _witness_is_collected(default glob) -> ({coll}, {why!r}); expected not-collected")
    # even under a WIDENED glob it stays uncollected, because it exposes zero pytest items
    coll2, why2 = _witness_is_collected("verification/verify_goal_typing.py",
                                        ["verification"], ["test_*.py", "verify_*.py"])
    if coll2 or "ZERO pytest items" not in why2:
        ok6 = False
        print(f"[selftest] _witness_is_collected(widened glob) -> ({coll2}, {why2!r}); "
              "expected not-collected/zero-items")
    # a witness living outside testpaths is never collectable regardless of glob
    coll3, why3 = _witness_is_collected("experiments/verify_encoder_retrain_persist_loader_v1.py",
                                        ["verification"], ["test_*.py", "verify_*.py"])
    if coll3 or "testpaths" not in why3:
        ok6 = False
        print(f"[selftest] _witness_is_collected(outside testpaths) -> ({coll3}, {why3!r})")
    print(f"[selftest] witness-citation check logic: {'OK' if ok6 else 'FAIL'}")

    # brain-fidelity gate (2026-08-16). Pure/synthetic: no disk, no writes. A gate nobody
    # verified is a gate that does not exist -- this project has shipped guards that silently
    # did nothing (the `if base in src` substring check that could only INFLATE the WIRED
    # count, D2 above), so each clause is proved to FIRE, and the compliant row is proved NOT
    # to fire (a check that flags everything is as useless as one that flags nothing).
    ok7 = True
    post = "2026-12-01T00:00:00Z"   # after BRAIN_FIDELITY_GATE_EFFECTIVE_UTC
    pre = "2026-01-01T00:00:00Z"    # before it
    # A valid graded-score block, and one whose stated total does not follow from its own
    # per-dimension verdicts (the fabrication case the recompute exists to catch).
    good_score = {"mode": "design_time",
                  "dimensions": {"D1": 2, "D2": 1, "D3": 1, "D5": 1},
                  "points": 5, "max_points": 8}
    na_score = {"mode": "design_time",
                "dimensions": {"D1": 2, "D2": 1, "D3": "NA", "D5": 1},
                "points": 4, "max_points": 6}
    fab_score = {"mode": "design_time",
                 "dimensions": {"D1": 2, "D2": 1, "D3": 1, "D5": 1},
                 "points": 8, "max_points": 8}
    fixture = [
        # 1: post-gate, missing BOTH -> violation
        {"id": "missing_both_post", "last_decision_utc": post},
        # 2: post-gate, missing only fidelity_basis -> violation naming exactly that field
        {"id": "missing_basis_post", "last_decision_utc": post,
         "brain_structure": "hippocampal CA3", "brain_fidelity_score": good_score},
        # 3: pre-gate, missing both -> BACKLOG, never a violation, never auto-filled
        {"id": "missing_both_pre", "last_decision_utc": pre},
        # 4: no timestamp at all -> backlog, not a manufactured violation
        {"id": "no_timestamp"},
        # 5: fully compliant post-gate row -> flags nothing at all
        {"id": "compliant_post", "last_decision_utc": post,
         "brain_structure": "perirhinal cortex (conjunctive coding)",
         "fidelity_basis": "invention_under_test", "brain_fidelity_score": good_score},
        # 6: invalid basis value -> invalid_basis flag
        {"id": "bad_basis", "last_decision_utc": post,
         "brain_structure": "dentate gyrus", "fidelity_basis": "probably_fine",
         "brain_fidelity_score": good_score},
        # 7: cognitive-theory LABEL with no anatomy -> label hint
        {"id": "label_not_structure", "last_decision_utc": post,
         "brain_structure": "working memory", "fidelity_basis": "pinned",
         "brain_fidelity_score": good_score},
        # 8: label WITH anatomy beside it -> must NOT fire (precision case)
        {"id": "label_with_anatomy", "last_decision_utc": post,
         "brain_structure": "hippocampal CA3 pattern completion", "fidelity_basis": "pinned",
         "brain_fidelity_score": good_score},
        # 9: THE INCIDENT, reconstructed: performance-framed revival criterion, no anatomy.
        {"id": "incident_perf_framed_revival", "last_decision_utc": pre,
         "revival_criteria": "Revive ONLY for a task whose QUERY IS THE STORED KEY "
                             "(exact-key facet addressing)."},
        # 10: THE FIX: same row, brain-framed revival criterion -> must NOT fire.
        {"id": "incident_brain_framed_revival", "last_decision_utc": pre,
         "revival_criteria": "Not testable until pattern completion (hippocampal CA3) sits in "
                             "front of it; dentate gyrus separation and CA3 completion are a "
                             "matched pair."},
        # 11: post-gate, both qualitative fields present, NO graded score -> violation naming
        #     exactly the score field. This is what makes the graded field REQUIRED and not
        #     merely welcome.
        {"id": "missing_score_post", "last_decision_utc": post,
         "brain_structure": "dentate gyrus", "fidelity_basis": "pinned"},
        # 12: THE FABRICATION CASE. Every field present, and the stated total does not follow
        #     from the stored per-dimension verdicts. Must be flagged as INCONSISTENT and must
        #     NOT be counted as a missing-field violation -- "you did not answer" and "your
        #     answer does not add up" are different faults.
        {"id": "fabricated_score_post", "last_decision_utc": post,
         "brain_structure": "hippocampal CA3", "fidelity_basis": "invention_under_test",
         "brain_fidelity_score": fab_score},
        # 13: a SOURCED not-applicable dimension shrinking the denominator, recomputing
        #     correctly -> must fire NOTHING. If this flagged, UNPINNED would be punished and
        #     honest invention would cost points, which is the fault this whole design exists
        #     to avoid.
        {"id": "sourced_na_score_post", "last_decision_utc": post,
         "brain_structure": "anterior temporal lobe hub", "fidelity_basis": "invention_under_test",
         "brain_fidelity_score": na_score},
    ]
    fr = check_brain_fidelity_fields(fixture)
    v_ids = {v["id"] for v in fr["brain_fidelity_violations"]}
    b_ids = {v["id"] for v in fr["brain_fidelity_backlog"]}
    i_ids = {v["id"] for v in fr["brain_fidelity_invalid_basis"]}
    l_ids = {v["id"] for v in fr["brain_fidelity_suspected_label_not_structure"]}
    r_ids = {v["id"] for v in fr["brain_fidelity_revival_not_brain_framed"]}
    s_ids = {v["id"] for v in fr["brain_fidelity_score_inconsistent"]}

    bf_cases = [
        # NOTE: `bad_basis` is deliberately NOT here. It DECLARED both fields, so it is not a
        # missing-field violation; it is caught by the invalid-value clause below instead. Both
        # clauses feed the exit code, so it cannot slip through -- the two flags just mean
        # different things ("you did not answer" vs "your answer is not one of the options").
        (v_ids == {"missing_both_post", "missing_basis_post", "missing_score_post"},
         f"post-gate rows missing a field are FLAGGED as violations (got {sorted(v_ids)})"),
        (next((v["missing_fields"] for v in fr["brain_fidelity_violations"]
               if v["id"] == "missing_score_post"), None) == ["brain_fidelity_score"],
         "the GRADED SCORE is REQUIRED post-gate and the violation names exactly it"),
        (sorted(next((v["missing_fields"] for v in fr["brain_fidelity_violations"]
                      if v["id"] == "missing_both_post"), []))
         == ["brain_fidelity_score", "brain_structure", "fidelity_basis"],
         "a row missing everything names all THREE fields"),
        (s_ids == {"fabricated_score_post"},
         f"a score that does not recompute from its own dimensions is FLAGGED (got {sorted(s_ids)})"),
        ("fabricated_score_post" not in v_ids,
         "a FABRICATED score is not filed as a missing-field violation -- 'you did not "
         "answer' and 'your answer does not add up' are different faults"),
        ("sourced_na_score_post" not in (v_ids | b_ids | i_ids | l_ids | r_ids | s_ids),
         "a SOURCED not-applicable dimension shrinking the denominator fires NOTHING "
         "(UNPINNED must not be punished, or honest invention costs points)"),
        (recompute_brain_fidelity_score(na_score)["max_points"] == 6,
         "an NA dimension leaves the DENOMINATOR, not just the numerator"),
        (recompute_brain_fidelity_score(
            {"mode": "design_time", "dimensions": {"D1": 2, "D2": 1, "D3": 1}}
         )["max_points"] == 8,
         "a dimension with NO verdict is scored 0 and STAYS in the denominator "
         "(silence is not 'not applicable')"),
        (next((v["missing_fields"] for v in fr["brain_fidelity_violations"]
               if v["id"] == "missing_basis_post"), None) == ["fidelity_basis"],
         "the violation names EXACTLY the missing field, not both"),
        (b_ids == {"missing_both_pre", "no_timestamp", "incident_perf_framed_revival",
                   "incident_brain_framed_revival"},
         f"pre-gate/undated rows are BACKLOG, never violations (got {sorted(b_ids)})"),
        ("compliant_post" not in (v_ids | b_ids | i_ids | l_ids | r_ids),
         "a fully compliant row triggers NOTHING (the gate is not a blanket alarm)"),
        (i_ids == {"bad_basis"}, f"invalid fidelity_basis value is flagged (got {sorted(i_ids)})"),
        (l_ids == {"label_not_structure"},
         f"cognitive-theory label flagged, label+anatomy NOT flagged (got {sorted(l_ids)})"),
        (r_ids == {"incident_perf_framed_revival"},
         f"THE INCIDENT: performance-framed revival criterion flagged, brain-framed one NOT "
         f"(got {sorted(r_ids)})"),
        # 6 = compliant_post, label_not_structure, label_with_anatomy, missing_score_post,
        # fabricated_score_post, sourced_na_score_post. `bad_basis` is excluded despite
        # declaring both fields, because its basis value is not one of the allowed three.
        (fr["brain_fidelity_stats"]["n_compliant"] == 6,
         f"compliant count requires a VALID basis (got "
         f"{fr['brain_fidelity_stats']['n_compliant']}, expected 6)"),
        # The two backlogs are reported SEPARATELY and must not be merged: 6 of the 13 fixture
        # rows carry no graded score at all (missing_both_post, missing_both_pre, no_timestamp,
        # both incident rows, and missing_score_post).
        (fr["brain_fidelity_stats"]["n_graded_score_backlog"] == 6,
         f"the GRADED-SCORE backlog is counted on its own (got "
         f"{fr['brain_fidelity_stats']['n_graded_score_backlog']}, expected 6)"),
        (fr["brain_fidelity_stats"]["n_with_graded_score"]
         + fr["brain_fidelity_stats"]["n_graded_score_backlog"]
         == fr["brain_fidelity_stats"]["n_rows"],
         "present + backlog accounts for every row (no row falls between the two)"),
    ]
    for passed, label in bf_cases:
        if not passed:
            ok7 = False
            print(f"[selftest] brain-fidelity FAIL: {label}")
    # Non-mutation: the gate must not have written a field onto any fixture row.
    if any("brain_structure" in r or "brain_fidelity_score" in r for r in fixture
           if r["id"] in ("missing_both_post", "missing_both_pre", "no_timestamp")):
        ok7 = False
        print("[selftest] brain-fidelity FAIL: the check MUTATED a row (retro-fill is banned)")
    print(f"[selftest] brain-fidelity gate (17 clauses + non-mutation, incl. the GRADED "
          f"brain_fidelity_score and its anti-fabrication recompute): "
          f"{'OK' if ok7 else 'FAIL'}")

    ok_all = ok and ok2 and ok3 and ok4 and ok5 and ok6 and ok7
    print(f"[selftest] invisible-island classify+match logic: {'OK' if ok2 and ok3 else 'FAIL'}")
    print(f"[selftest] high-signal precision-tier logic: {'OK' if ok4 else 'FAIL'}")
    print(f"[selftest] registry concurrency (RegistryLock/registry_transaction/append_rows): "
          f"{'OK' if ok5 else 'FAIL'}")
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report only; do not rewrite the registry")
    ap.add_argument("--stale-days", type=int, default=7, help="VET_PENDING staleness threshold (default 7)")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON instead of the human report")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--skip-hard-pass-scan", action="store_true",
                     help="skip the invisible-island (data/exp_*/metrics.json) scan; "
                          "keeps the rest of the audit on its fast path")
    ap.add_argument("--run-witnesses", action="store_true",
                     help="execute every registry-cited witness live (slow, ~minutes) instead "
                          "of reading the persisted results written by "
                          "verification/test_all_witnesses_exit_clean.py")
    ap.add_argument("--append-json", type=Path,
                     help="path to a JSON file holding a list of new registry rows; "
                          "appends them via the locked append_rows() transaction "
                          "(concurrency-safe) and exits, instead of running the audit. "
                          "Use this instead of hand-rolling a load+tmp+os.replace script.")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    if args.append_json:
        try:
            new_rows = json.loads(args.append_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"error reading {args.append_json}: {e}", file=sys.stderr)
            return 1
        if not isinstance(new_rows, list):
            print("error: --append-json file must contain a JSON list of row objects", file=sys.stderr)
            return 1
        try:
            n_total = append_rows(new_rows)
        except ValueError as e:
            print(f"append refused: {e}", file=sys.stderr)
            return 1
        except TimeoutError as e:
            print(f"append failed: {e}", file=sys.stderr)
            return 1
        print(f"appended {len(new_rows)} row(s); registry now has {n_total} rows")
        return 0

    summary = run_audit(stale_days=args.stale_days, dry_run=args.dry_run,
                         skip_hard_pass_scan=args.skip_hard_pass_scan,
                         run_witnesses=args.run_witnesses)
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
               + len(summary.get("unregistered_hdlab_modules", []))
               + len(summary.get("invisible_island_candidates_HIGH", []))
               # Brain-fidelity gate: POST-GATE violations + invalid values only. The pre-gate
               # BACKLOG is deliberately excluded from the exit code -- 199 permanently-red rows
               # would be an alarm nobody reads (the same alarm-fatigue lesson this file already
               # learned from the 3042-candidate invisible-island scan), and the fix for backlog
               # is honest human clearing, not a louder exit code.
               + len(summary.get("brain_fidelity_violations", []))
               + len(summary.get("brain_fidelity_invalid_basis", [])))
    return 5 if n_flags else 0


if __name__ == "__main__":
    sys.exit(main())
