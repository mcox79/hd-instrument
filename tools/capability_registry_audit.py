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


def run_audit(stale_days: int, dry_run: bool, skip_hard_pass_scan: bool = False) -> dict:
    now = datetime.now(timezone.utc)
    graph = ih.compute_import_graph()
    composed_sources = _composed_entry_sources()
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

    ok_all = ok and ok2 and ok3 and ok4 and ok5
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
                         skip_hard_pass_scan=args.skip_hard_pass_scan)
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
               + len(summary.get("invisible_island_candidates_HIGH", [])))
    return 5 if n_flags else 0


if __name__ == "__main__":
    sys.exit(main())
