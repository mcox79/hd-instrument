#!/usr/bin/env python
"""Ready-work dispatch queue -- pre-written, ready-to-dispatch briefs for parallel Agent fan-out.

WHY THIS EXISTS (2026-08-15, owner directive on parallel-dispatch enforcement):
notes/agent_usage_practices_audit_2026-08-14.md measured 0/235 Agent-tool-use messages ever
batched more than one Agent call in a single turn -- the 5-agent concurrent budget was never once exercised. The diagnosed cause is a
thinking-cost problem, not a permission problem: the Director thinks of ONE task, dispatches
it, and only then thinks of the next. A file of pre-written, ready-to-dispatch briefs removes
that cost at the moment of dispatch -- open the queue, grab N unclaimed items, fire N Agent
calls in one message.

SCHEMA (JSONL, one object per line, data/dispatch_queue.jsonl):
{
  "id":          str,  REQUIRED, stable slug, unique.
  "category":    str,  REQUIRED, one of CATEGORIES below.
  "title":       str,  REQUIRED, one-line human summary.
  "brief":       str,  REQUIRED, the ready-to-paste Agent `prompt` body. Self-contained --
                       a dispatcher should be able to paste this verbatim into Agent(prompt=...)
                       without adding context. Mandatory boilerplate (disclosure rule, no-spawn
                       constraint, fragment convention, DO-NOT-TOUCH list) is already folded in
                       by tools/dispatch_batch.py at emit time, NOT baked into this field, so the
                       boilerplate can be updated in one place as the project's rules evolve.
  "priority":    str,  REQUIRED, "H" | "M" | "L".
  "status":      str,  REQUIRED, "unclaimed" | "claimed" | "done".
  "claimed_by":  str | None.
  "claimed_at":  str | None, UTC ISO-8601.
  "done_at":     str | None, UTC ISO-8601.
  "created_at":  str,  UTC ISO-8601.
  "source":      str,  REQUIRED, file:line pointer to the backlog item this was seeded from --
                       every item must be traceable to a measured, disk-verified number.
}

CATEGORIES (seeded 2026-08-15, each traced to a specific measured backlog count -- see
seed_default()'s docstring for the full provenance table):
  metrics-triage, atom-triage, registry-reconcile, organ-untested, organ-missing,
  ledger-dangling, litscan-dedup, status-open-thread

CONCURRENCY / CLAIM SAFETY: two agents (or two sessions) must never claim the same item.
claim() takes an exclusive OS-level lock via open(lockfile, 'x') -- atomic create-or-fail,
works cross-process on Windows and POSIX alike. If the lock is held, retry with short backoff
up to a timeout, then FAIL LOUDLY (raise) rather than silently proceeding unlocked or silently
overwriting. A stale lock (holder crashed) is detected by age and force-broken after
STALE_LOCK_SECS, logged to stderr so the break is visible, never silent.

USAGE
  python tools/dispatch_queue.py seed                  # populate from the 2026-08-15 backlog (idempotent: skips ids already present)
  python tools/dispatch_queue.py list [--status unclaimed] [--category X] [--limit N]
  python tools/dispatch_queue.py claim <id> --by <agent-name>
  python tools/dispatch_queue.py release <id>            # un-claim (claimed_by crashed / gave up)
  python tools/dispatch_queue.py done <id>
  python tools/dispatch_queue.py stats
  python tools/dispatch_queue.py self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = REPO_ROOT / "data" / "dispatch_queue.jsonl"
LOCK_SUFFIX = ".lock"
STALE_LOCK_SECS = 30.0
LOCK_RETRY_SECS = 0.15
LOCK_TIMEOUT_SECS = 10.0

CATEGORIES = {
    "metrics-triage", "atom-triage", "registry-reconcile", "organ-untested",
    "organ-missing", "ledger-dangling", "litscan-dedup", "status-open-thread",
}
STATUSES = {"unclaimed", "claimed", "done"}
PRIORITIES = {"H", "M", "L"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class QueueLockError(Exception):
    pass


class _Lock:
    """Exclusive create-based lock. Cross-process safe: open(path, 'x') is an atomic
    create-fails-if-exists syscall on both Windows and POSIX -- no separate flock needed."""

    def __init__(self, queue_path: Path):
        self.lock_path = Path(str(queue_path) + LOCK_SUFFIX)
        self._acquired = False

    def __enter__(self):
        deadline = time.time() + LOCK_TIMEOUT_SECS
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w") as fh:
                    fh.write(f"{os.getpid()} {_now()}\n")
                self._acquired = True
                return self
            except FileExistsError:
                # Stale-lock break: a holder that crashed leaves the lock forever otherwise.
                try:
                    age = time.time() - self.lock_path.stat().st_mtime
                except OSError:
                    age = 0.0
                if age > STALE_LOCK_SECS:
                    print(f"[dispatch_queue] WARNING breaking stale lock "
                          f"(age {age:.1f}s > {STALE_LOCK_SECS}s): {self.lock_path}",
                          file=sys.stderr)
                    try:
                        self.lock_path.unlink()
                    except OSError:
                        pass
                    continue
                if time.time() > deadline:
                    raise QueueLockError(
                        f"could not acquire {self.lock_path} within {LOCK_TIMEOUT_SECS}s "
                        f"(held, age {age:.1f}s) -- another dispatch is mid-write; retry shortly")
                time.sleep(LOCK_RETRY_SECS)

    def __exit__(self, exc_type, exc, tb):
        if self._acquired:
            try:
                self.lock_path.unlink()
            except OSError:
                pass
        return False


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load_items(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def save_items(path: Path, items: list[dict]) -> None:
    """Atomic write: temp file + os.replace, same pattern as scan_out_collect / clear_scratch."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=True) + "\n")
    os.replace(str(tmp), str(path))


# ---------------------------------------------------------------------------
# Mutating ops (all lock-guarded)
# ---------------------------------------------------------------------------

def add_items(path: Path, new_items: list[dict], skip_existing: bool = True) -> int:
    """Append new_items, skipping any whose id already exists. Returns count actually added."""
    with _Lock(path):
        items = load_items(path)
        existing_ids = {it["id"] for it in items}
        added = 0
        for it in new_items:
            if skip_existing and it["id"] in existing_ids:
                continue
            items.append(it)
            existing_ids.add(it["id"])
            added += 1
        save_items(path, items)
    return added


def claim(path: Path, item_id: str, by: str) -> dict:
    with _Lock(path):
        items = load_items(path)
        for it in items:
            if it["id"] == item_id:
                if it["status"] == "claimed" and it.get("claimed_by") != by:
                    raise QueueLockError(
                        f"{item_id} already claimed by {it.get('claimed_by')!r} "
                        f"at {it.get('claimed_at')!r}")
                if it["status"] == "done":
                    raise QueueLockError(f"{item_id} already done")
                it["status"] = "claimed"
                it["claimed_by"] = by
                it["claimed_at"] = _now()
                save_items(path, items)
                return it
        raise KeyError(f"no such item: {item_id}")


def release(path: Path, item_id: str) -> dict:
    with _Lock(path):
        items = load_items(path)
        for it in items:
            if it["id"] == item_id:
                it["status"] = "unclaimed"
                it["claimed_by"] = None
                it["claimed_at"] = None
                save_items(path, items)
                return it
        raise KeyError(f"no such item: {item_id}")


def mark_done(path: Path, item_id: str) -> dict:
    with _Lock(path):
        items = load_items(path)
        for it in items:
            if it["id"] == item_id:
                it["status"] = "done"
                it["done_at"] = _now()
                save_items(path, items)
                return it
        raise KeyError(f"no such item: {item_id}")


def stats(path: Path) -> dict:
    items = load_items(path)
    out = {"total": len(items), "unclaimed": 0, "claimed": 0, "done": 0, "by_category": {}}
    for it in items:
        out[it["status"]] = out.get(it["status"], 0) + 1
        cat = it.get("category", "?")
        c = out["by_category"].setdefault(cat, {"unclaimed": 0, "claimed": 0, "done": 0})
        c[it["status"]] += 1
    return out


# ---------------------------------------------------------------------------
# Seed data -- the 2026-08-15 backlog, each row traced to a measured disk count.
# ---------------------------------------------------------------------------

def _mk(id_, category, title, brief, priority, source):
    assert category in CATEGORIES, category
    assert priority in PRIORITIES, priority
    return {
        "id": id_, "category": category, "title": title, "brief": brief,
        "priority": priority, "status": "unclaimed", "claimed_by": None,
        "claimed_at": None, "done_at": None, "created_at": _now(), "source": source,
    }


def seed_default() -> list[dict]:
    """The 2026-08-15 backlog. Provenance for every count (measured this session, not
    copied from the owner's prompt uncritically -- three of the six original figures
    needed correction against fresher on-disk state):

    - metrics.json: 7665 files found live under data/ this session (`find data -iname
      metrics.json | wc -l`). notes/STATUS.md line 43 (2026-08-14) says "~7,150/7,634
      metrics" untriaged; notes/RECOVERY_PROGRAM.md G4 says on-disk 7,623, 6,566 (86%)
      unindexed. The three counts (7623/7634/7665) disagree by ~1% -- different scan
      timestamps and data/ vs data/+experiments/ scope, not a contradiction. Batched
      into 29 items of ~250 files each (7150/250 ~ 29), covering the STATUS.md-cited
      untriaged estimate.
    - atoms: notes/RECOVERY_PROGRAM.md line 193 + 1409, notes/STATUS.md line 43: cert
      ledger holds ~1,925 distinct atoms (atom_id, verified via
      notes/cert_ledger_triage_2026-08-14.md line 97), ~745 triaged, "~1,180 atoms...
      still never [examined]". Batched into 12 items of ~100 atoms each.
    - hdlab/registry reconciliation: THE OWNER'S "~61 unregistered hdlab modules" FIGURE
      IS STALE. Fresh recompute this session (os.walk hdlab/, match each module's
      relative path against every `path` array in data/capability_registry.jsonl,
      152 modules found, 152 matched, 0 residue) finds ZERO unregistered modules by
      exact-path match -- not 61. notes/STATUS.md line 50 (2026-08-14) already says
      "+4 unregistered modules", not 61 -- consistent with the gap having been mostly
      closed since the 2026-08-13 CLAUDE.md figure of 62/141. Seeded as ONE
      reconciliation item (not 61 fabricated rows) whose job is to confirm this with a
      stronger heuristic (basename-only modules imported under an alias, or listed
      inside a `used_by` array rather than `path`) and either confirm ~0 or find the
      real residue.
    - organ-untested / organ-missing: notes/ORGAN_MAP.md sec 1 tally (line 78: "UNTESTED
      -- no floored evidence at all | 16/38"; line 72: "MISSING entirely | 7/38",
      naming: successor representation, cascade synapse, discourse bridging, coherence
      monitor, construction-integration, information foraging, settling [declined on
      purpose]). MISSING seeded as 6 items (the 7th, "settling"/C4, is an EXPLICIT
      NEGATIVE RECOMMENDATION per ORGAN_MAP.md line 433 -- not queued). UNTESTED seeded
      as 12 items from a text-adjacency heuristic (nearest preceding "**X# --**" header
      before an "UNTESTED" mention, MISSING organs excluded) -- THIS UNDER-RECOVERS the
      stated 16 by ~4; each item's brief tells the dispatched agent to re-verify against
      the live doc rather than trust this list's precision.
    - ledger-dangling: notes/RECOVERY_PROGRAM.md sec 5.7, exactly 12 rows, itemized with
      row-id + resolution-attempt in the table there. Seeded as 12 items, one per row.
    - litscan-dedup: 13 notes/lit_scan_*.md files on disk (`find notes -iname
      "lit_scan_*"`); 4 near-duplicate PAIRS identified by topic-name overlap + same
      2026-08-14 date + comparable byte size (21874-26374 bytes each) -- NOT diffed for
      byte-identity, so each item's brief instructs a real diff before deleting either
      side, matching CLAUDE.md's "never bundle a deletion with real work" rule (the
      queue item authors the diff + recommendation; it does NOT itself delete).
    - status-open-thread: notes/STATUS.md "OTHER PATH STATE" line 49-50, the two items
      NOT already marked DO-NOT-TOUCH elsewhere in that file (C13 re-run; C12 gap index
      NOT BUILT).
    """
    items: list[dict] = []

    # --- metrics-triage: 29 batches of ~250, covering the ~7,150 STATUS.md-cited backlog ---
    N_METRICS_BATCHES = 29
    for i in range(N_METRICS_BATCHES):
        lo, hi = i * 250, i * 250 + 249
        items.append(_mk(
            f"metrics-triage-batch-{i:02d}", "metrics-triage",
            f"Triage floor-status of metrics.json batch {i:02d} (rank {lo}-{hi} of sorted paths)",
            f"Enumerate `find data -iname metrics.json | sort` fresh (do not trust a cached "
            f"list -- the backlog changes as experiments land). Take rows {lo}-{hi} (0-indexed) "
            f"of that sorted list. For each: read metrics.json, determine whether it carries a "
            f"named floor field (see notes/ORGAN_MAP.md 'The evidence base, measured' section for "
            f"the floor-detection caveat: key-name based, several real floors are named 'OFF', "
            f"'fz', 'brute', 'naive_dual_w' -- a NO_FLOOR verdict from a naive key-scan is not "
            f"proof of absence, verify by reading the file for any of those). Record HAS_FLOOR / "
            f"NO_FLOOR / UNREADABLE per file plus whether the verdict field (if present) reads as "
            f"PASS-flavoured with no floor behind it (a red flag per notes/ORGAN_MAP.md's '134 "
            f"carry a PASS-flavoured verdict with no floor' finding). Do not re-run any experiment. "
            f"Write findings to notes/ (topic-slug name, not from/to naming) -- do not touch "
            f"notes/STATUS.md, notes/RECOVERY_PROGRAM.md, or CLAUDE.md.",
            "L", "notes/STATUS.md:43 + notes/RECOVERY_PROGRAM.md:G4",
        ))

    # --- atom-triage: 12 batches of ~100, covering the ~1,180 cert-ledger backlog ---
    N_ATOM_BATCHES = 12
    for i in range(N_ATOM_BATCHES):
        lo, hi = i * 100, i * 100 + 99
        items.append(_mk(
            f"atom-triage-batch-{i:02d}", "atom-triage",
            f"Triage cert-ledger atoms batch {i:02d} (rank {lo}-{hi} of untriaged atom_id set)",
            f"Read notes/cert_ledger_triage_2026-08-14.md for the ledger schema and the "
            f"already-triaged ~745 (do not re-do those). Derive the untriaged atom_id set "
            f"(distinct atom_id values in the cert ledger minus the already-triaged set), sort "
            f"it deterministically, take rows {lo}-{hi} (0-indexed). For each atom_id: does its "
            f"result directory resolve on disk (per the join method in "
            f"notes/RECOVERY_PROGRAM.md sec 5.7/G4 -- exact, case-insensitive, string-prefix, "
            f"longest-common-token-prefix, in that order)? Record RESOLVES / DANGLING / "
            f"WRITE-PATH-BUG per atom, citing which stage resolved it or that all four failed. "
            f"Do not drop any row even if dangling -- per RECOVERY_PROGRAM.md sec 5.7, 'a "
            f"dangling pointer is a defect in the WRITE path, and deleting the row hides the "
            f"defect.' Write findings to notes/ (topic-slug name). Do not touch "
            f"notes/RECOVERY_PROGRAM.md, notes/STATUS.md, or CLAUDE.md.",
            "L", "notes/RECOVERY_PROGRAM.md:193,1409 + notes/cert_ledger_triage_2026-08-14.md:97",
        ))

    # --- registry-reconcile: single item, the STALE 61-figure correction ---
    items.append(_mk(
        "registry-reconcile-hdlab-residue", "registry-reconcile",
        "Re-audit hdlab/registry gap with a stronger heuristic (owner's '~61 unregistered' figure is STALE)",
        "notes/RECOVERY_PROGRAM.md and CLAUDE.md both cite an hdlab-modules-unregistered figure "
        "from a 2026-08-13 audit (62/141). A fresh recompute this session (os.walk hdlab/ "
        "recursively for *.py excluding __init__.py and __pycache__ -> 152 modules; match each "
        "module's relative path e.g. 'hdlab/foo/bar.py' against every entry of the 'path' array "
        "across all 198 rows of data/capability_registry.jsonl) found 152/152 matched, 0 "
        "residue -- NOT 61. notes/STATUS.md line 50 (2026-08-14) already says '+4 unregistered "
        "modules', consistent with the gap having mostly closed since 08-13, not with 61. "
        "TASK: (1) reproduce the 152/0 result independently (do not trust this brief's number "
        "uncritically -- re-run the enumeration yourself); (2) if it holds, try a STRONGER "
        "heuristic that could still find real gaps the exact-path match misses -- e.g. a module "
        "imported only under an alias, a module referenced only in a 'used_by' array rather "
        "than 'path', or a module that exists on disk but whose registry row was deleted/never "
        "written; (3) report the corrected number with method, and flag both CLAUDE.md's "
        "evidence-discipline section and notes/RECOVERY_PROGRAM.md as citing a stale count (do "
        "not edit either file directly -- CLAUDE.md is DO-NOT-TOUCH / concurrent writers; "
        "RECOVERY_PROGRAM.md ownership is unclear from this brief, write findings to a new note "
        "instead and let the owner decide whether to fold it in).",
        "M", "CLAUDE.md 'Evidence discipline #2' + notes/STATUS.md:50 (contradicts)",
    ))

    # --- organ-missing: 6 items (7th, 'settling', is an explicit do-not-build) ---
    missing_organs = [
        ("D7", "Successor representation: the predictive relational map",
         "MISSING, and its math is FULLY PINNED per ORGAN_MAP.md line 596-614"),
        ("D8", "The cascade synapse: memory lifetime",
         "MISSING, and its math is FULLY PINNED per ORGAN_MAP.md line 615-666"),
        ("E4", "Discourse / bridging inference",
         "listed among the 7 MISSING organs in the sec-1 tally; read ORGAN_MAP.md line 773+ for scope"),
        ("F5", "Coherence monitor (the N400 generator)",
         "MISSING -- a legitimate PHASE-B target per ORGAN_MAP.md line 865-886"),
        ("F6", "Construction-Integration: settling a multi-sentence interpretation",
         "MISSING per ORGAN_MAP.md line 887-906"),
        ("H2", "Information foraging: deciding WHAT TO READ NEXT",
         "MISSING -- and it is step 1 per ORGAN_MAP.md line 1040-1068"),
    ]
    for code, name, note in missing_organs:
        items.append(_mk(
            f"organ-missing-{code.lower()}", "organ-missing",
            f"{code} -- {name} (MISSING organ, no code exists)",
            f"Read notes/ORGAN_MAP.md's {code} section in full ({note}) -- it states the brain "
            f"structure, the pinned (or unpinned) math, and why nothing in hdlab/ implements it. "
            f"BUILD NOTHING yet. Task: write a short design note (topic-slug name in notes/) that "
            f"(a) restates the brain-fidelity target in your own words to prove you read it, (b) "
            f"proposes the SMALLEST buildable version with a can-fail acceptance test (per "
            f"CLAUDE.md 'When implementing a new feature': closed-form theory first, then a "
            f"verification test), (c) names which existing hdlab/ module it would wire into and "
            f"whether that module is on the live path (per ORGAN_MAP.md's runtime-closure "
            f"finding -- 83/155 modules are unreachable from any entry point; a wire target that "
            f"is itself unreached is a second problem to flag, not silently inherit). Do not "
            f"touch hdlab/ or experiments/ in this pass -- design only, per the standing rule "
            f"that experiment cells are exp_dev's job, not a general-purpose dispatch's.",
            "M", "notes/ORGAN_MAP.md:72 (tally) + per-organ section",
        ))

    # --- organ-untested: 12 items (heuristic under-recovers stated 16 by ~4, flagged) ---
    untested_organs = [
        ("A1", "VWFA: orthography -> an invariant lexical code"),
        ("B1", "ATL amodal hub: the concept representation itself"),
        ("D2", "CA3: pattern completion / auto-association"),
        ("D3", "Hippocampus: one-shot episodic write / index"),
        ("D4", "Consolidation: replay scheduling"),
        ("D9", "Synaptic tag and capture: which write gets consolidated"),
        ("E5", "Theta-gamma multi-item ordered buffer"),
        ("F1", "Lexical category (POS)"),
        ("G1", "The cortical learning rule"),
        ("G2", "Prediction error / surprise gating of plasticity"),
        ("G3", "Neuromodulatory gain"),
        ("H2b", "cross-check: information foraging is MISSING not UNTESTED -- verify H2 is not double-counted"),
    ]
    for code, name in untested_organs:
        items.append(_mk(
            f"organ-untested-{code.lower()}", "organ-untested",
            f"{code} -- {name} (UNTESTED organ, evidence column NO FLOOR)",
            f"notes/ORGAN_MAP.md's sec-1 tally states 16/38 organs are 'UNTESTED -- no floored "
            f"evidence at all' (column 7). This item's organ code ({code}) was attributed by a "
            f"crude text-adjacency heuristic (nearest header before an UNTESTED mention) that is "
            f"KNOWN to under-recover the stated 16 by about 4 and may mis-attribute individual "
            f"organs. FIRST STEP, mandatory: open notes/ORGAN_MAP.md, find the {code} section, "
            f"and confirm its EVIDENCE line actually says UNTESTED / NO FLOOR -- if it does not "
            f"(this heuristic was wrong for this organ), say so and stop; do not force a floor "
            f"design onto a mis-attributed organ. If confirmed UNTESTED: design the smallest "
            f"can-fail floor test for it (a floor that CANNOT pass trivially -- ORGAN_MAP.md rule "
            f"3: 'A floor that cannot fail is not a floor'). Write findings to notes/ (topic-slug "
            f"name). BUILD NOTHING -- design + floor-test proposal only.",
            "M", "notes/ORGAN_MAP.md:78 (tally, 16/38) -- per-organ attribution is a heuristic, verify before acting",
        ))

    # --- ledger-dangling: 12 items, one per row from RECOVERY_PROGRAM.md sec 5.7 ---
    dangling_rows = [
        ("RP-F11", "pipeline_status field integrity",
         "NOT a cell -- it is the capability_registry.jsonl field-integrity audit itself. Listed for completeness."),
        ("RP-G3", "the capability registry",
         "NOT a cell -- the registry itself (data/capability_registry.jsonl). Not a broken pointer."),
        ("RP-G5", "the 2026-06-25 archaeology tooling",
         "NOT a cell -- files exist (data/_archaeology_*) but there is no result directory to resolve."),
        ("CG-F1", "exp_chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning_3seed",
         "genuinely absent -- cited name is an ATOM-ID sentence not a directory; longest token match against 7,898 dirs is 1."),
        ("CG-F4", "exp_narrative_q3_temporal_sequence_replay_k20_3seed_hp_cg_q15_1",
         "genuinely absent under this name. Closest on disk: exp_narrative_q3_v2_q15_seed{7,13,19}_full at 3 matched tokens -- a candidate, not a match. Confirm or write off."),
        ("CG-F16", "metrics.json",
         "WRITE-PATH bug, not a missing result: ledger wrote the literal string 'metrics.json (ssh pulled)' into the pointer field."),
        ("CG-F17", "see per_seed_metrics_paths in atom metadata",
         "WRITE-PATH bug: ledger wrote this literal instruction string into the pointer field instead of a path."),
        ("RD-R25", "exp_dependency_context_codebook_weight_sweep_location_artifact_v2",
         "genuinely absent under this name; longest token match is 2."),
        ("RD-R166", "exp_perceptual_grounding_gap_audit_v1",
         "genuinely absent under this name; longest token match is 1."),
        ("RD-R167", "exp_derived_filler_typing_single_edge_grounding_v1",
         "genuinely absent under this name; longest token match is 2."),
        ("RD-R168", "exp_af43a6dd_grounding_feasibility_probe_atomic2019",
         "genuinely absent under this name; longest token match is 1."),
        ("RD-R170", "exp_probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1",
         "genuinely absent under this name; longest token match is 2."),
    ]
    for row_id, cited_as, why in dangling_rows:
        items.append(_mk(
            f"ledger-dangling-{row_id.lower()}", "ledger-dangling",
            f"{row_id}: resolve or confirm-absent '{cited_as}'",
            f"notes/RECOVERY_PROGRAM.md sec 5.7 flags ledger row {row_id} as dangling: cited as "
            f"'{cited_as}'. Prior finding: {why} TASK: for the genuinely-absent ones, do one more "
            f"pass with a WIDER search (semantic/fuzzy match on the experiment's apparent topic, "
            f"not just token-prefix) against a fresh `find data experiments -maxdepth 2 -type d` "
            f"listing -- the goal is to either find the real artifact under a renamed/typo'd "
            f"path, or confirm with higher confidence that the result was never actually run. For "
            f"the WRITE-PATH-bug rows (CG-F16, CG-F17), check whether the actual metrics path can "
            f"be recovered from the atom's OTHER metadata fields (per_seed_metrics_paths, "
            f"provenance) rather than the broken pointer field. Do NOT drop the row regardless of "
            f"outcome -- per RECOVERY_PROGRAM.md sec 5.7, a dangling pointer is a WRITE-PATH "
            f"defect and deleting the row hides it. Write findings to notes/ (topic-slug name); "
            f"do not touch notes/RECOVERY_PROGRAM.md directly (ownership unclear from this "
            f"brief -- let the owner decide whether to fold the finding in).",
            "L", f"notes/RECOVERY_PROGRAM.md:1344-1367 (row {row_id})",
        ))

    # --- litscan-dedup: 4 pairs, near-duplicate by topic+date+size, NOT diffed yet ---
    dedup_pairs = [
        ("vvs-mtl", "notes/lit_scan_vvs_to_mtl_representational_hierarchy_interference_2026-08-14.md",
         "notes/lit_scan_vvs_mtl_hierarchy_interference_2026-08-14.md", 24566, 23077),
        ("perirhinal-counterposition", "notes/lit_scan_perirhinal_purely_mnemonic_counter_position_2026-08-14.md",
         "notes/lit_scan_purely_mnemonic_counterposition_2026-08-14.md", 26374, 24843),
        ("feature-ambiguity", "notes/lit_scan_feature_ambiguity_lesion_evidence_2026-08-14.md",
         "notes/lit_scan_feature_ambiguity_hypothesis_lesion_evidence_2026-08-14.md", 21874, 23571),
        ("perirhinal-conjunction", "notes/lit_scan_perirhinal_conjunction_operation_2026-08-14.md",
         "notes/lit_scan_perirhinal_conjunctive_coding_operation_2026-08-14.md", 23025, 24720),
    ]
    for slug, a, b, sa, sb in dedup_pairs:
        items.append(_mk(
            f"litscan-dedup-{slug}", "litscan-dedup",
            f"Diff + resolve near-duplicate lit_scan pair: {slug}",
            f"Two lit_scan_*.md notes on the same topic, both dated 2026-08-14, comparable size "
            f"({sa} vs {sb} bytes) -- NOT byte-diffed yet, only flagged by filename/topic overlap. "
            f"Files: '{a}' ({sa}B) and '{b}' ({sb}B). TASK: (1) diff the two files' actual content "
            f"and evidence claims -- do they cover the same literature with the same "
            f"ESTABLISHED/CONTESTED/SINGLE-STUDY/FAILED-REPLICATION tags, or does one add findings "
            f"the other lacks? (2) if genuinely duplicate, recommend which to keep (prefer the one "
            f"cited from notes/STATUS.md's '4 rescued lit_scan_*_2026-08-14.md' line if either "
            f"is that one -- check first) and write the recommendation to a new note; per CLAUDE.md "
            f"'never bundle a deletion with real work in one call' and this session's own DO-NOT "
            f"TOUCH list, DO NOT DELETE either file yourself -- write the recommendation only and "
            f"let a separate, later, deletion-only call execute it. (3) if the two files are NOT "
            f"duplicates (cover genuinely different sub-claims despite similar names), say so "
            f"explicitly and recommend keeping both.",
            "L", f"notes/ (13 lit_scan_* files on disk, this pair flagged by name+date+size overlap)",
        ))

    # --- status-open-thread: 2 items from STATUS.md 'OTHER PATH STATE', not DO-NOT-TOUCH ---
    items.append(_mk(
        "status-open-c13-rerun", "status-open-thread",
        "C13 re-run (phase-diagram validation full run) -- open thread from STATUS.md",
        "notes/STATUS.md 'OTHER PATH STATE' lists 'PHASE DIAGRAM closed, neither cash-in hit; "
        "OPEN (C13 re-run, C12 gap index NOT BUILT...)' pointing to notes/STATUS_LESSONS.md "
        "'OPEN THREADS (older)' for detail. TASK: read that LESSONS section for what C13 actually "
        "requires, confirm whether it is still open (STATUS.md dates are 2026-08-14; re-verify "
        "against current disk state per CLAUDE.md evidence-discipline rule 4 -- notes go stale "
        "within hours), and if still open, scope the re-run (design only, do not launch an "
        "experiment from a general-purpose dispatch -- that is exp_dev's job; hand off a "
        "ready-to-dispatch brief instead).",
        "L", "notes/STATUS.md:49 + notes/STATUS_LESSONS.md 'OPEN THREADS (older)'",
    ))
    items.append(_mk(
        "status-open-c12-gap-index", "status-open-thread",
        "C12 gap index NOT BUILT -- open thread from STATUS.md",
        "notes/STATUS.md 'OTHER PATH STATE' lists 'C12 gap index NOT BUILT' among open phase-"
        "diagram threads, pointing to notes/STATUS_LESSONS.md 'OPEN THREADS (older)' for detail. "
        "TASK: read that section, confirm current status against disk (re-verify, do not trust "
        "the 08-14 timestamp blindly), and if still not built, scope what building it requires "
        "(design only -- hand off a ready-to-dispatch brief for the actual build rather than "
        "doing it in this pass).",
        "L", "notes/STATUS.md:49 + notes/STATUS_LESSONS.md 'OPEN THREADS (older)'",
    ))

    return items


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_item_line(it: dict) -> None:
    print(f"{it['status']:9s} {it['priority']} {it['category']:18s} {it['id']:40s} {it['title']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("seed")

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", choices=sorted(STATUSES))
    p_list.add_argument("--category", choices=sorted(CATEGORIES))
    p_list.add_argument("--limit", type=int, default=0)
    p_list.add_argument("--ids-only", action="store_true")

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("id")
    p_claim.add_argument("--by", required=True)

    p_release = sub.add_parser("release")
    p_release.add_argument("id")

    p_done = sub.add_parser("done")
    p_done.add_argument("id")

    sub.add_parser("stats")
    sub.add_parser("self-test")

    args = ap.parse_args(argv)
    path = Path(args.queue)

    if args.cmd == "seed":
        new = seed_default()
        added = add_items(path, new)
        print(f"[dispatch_queue] seed: {added} new item(s) added ({len(new)} in seed set, "
              f"{len(new) - added} already present -> skipped)")
        return 0

    if args.cmd == "list":
        items = load_items(path)
        if args.status:
            items = [it for it in items if it["status"] == args.status]
        if args.category:
            items = [it for it in items if it["category"] == args.category]
        if args.limit:
            items = items[: args.limit]
        if args.ids_only:
            for it in items:
                print(it["id"])
        else:
            for it in items:
                _print_item_line(it)
            print(f"-- {len(items)} item(s)")
        return 0

    if args.cmd == "claim":
        try:
            it = claim(path, args.id, args.by)
        except (KeyError, QueueLockError) as e:
            print(f"[dispatch_queue] REFUSED: {e}", file=sys.stderr)
            return 2
        print(f"[dispatch_queue] claimed {it['id']} by {args.by} at {it['claimed_at']}")
        return 0

    if args.cmd == "release":
        try:
            it = release(path, args.id)
        except KeyError as e:
            print(f"[dispatch_queue] {e}", file=sys.stderr)
            return 2
        print(f"[dispatch_queue] released {it['id']}")
        return 0

    if args.cmd == "done":
        try:
            it = mark_done(path, args.id)
        except KeyError as e:
            print(f"[dispatch_queue] {e}", file=sys.stderr)
            return 2
        print(f"[dispatch_queue] done {it['id']} at {it['done_at']}")
        return 0

    if args.cmd == "stats":
        s = stats(path)
        print(json.dumps(s, indent=2))
        return 0

    if args.cmd == "self-test":
        return _self_test()

    return 1


def _self_test() -> int:
    import tempfile
    ok = True
    tmp_dir = Path(tempfile.mkdtemp(prefix="dispatch_queue_selftest_"))
    qpath = tmp_dir / "queue.jsonl"

    # 1. add + load round-trip
    n1 = [_mk("t1", "metrics-triage", "title1", "brief1", "M", "src1")]
    added = add_items(qpath, n1)
    if added == 1 and load_items(qpath)[0]["id"] == "t1":
        print("[self-test] PASS add_items round-trips")
    else:
        print("[self-test] FAIL add_items round-trip", file=sys.stderr)
        ok = False

    # 2. idempotent re-add (skip_existing)
    added2 = add_items(qpath, n1)
    if added2 == 0 and len(load_items(qpath)) == 1:
        print("[self-test] PASS re-seeding is idempotent (skips existing id)")
    else:
        print("[self-test] FAIL re-seed was not idempotent", file=sys.stderr)
        ok = False

    # 3. claim then double-claim by a different agent must fail
    claim(qpath, "t1", "agentA")
    try:
        claim(qpath, "t1", "agentB")
        print("[self-test] FAIL double-claim by a different agent was NOT refused", file=sys.stderr)
        ok = False
    except QueueLockError:
        print("[self-test] PASS double-claim by a different agent refused")

    # 4. same agent re-claiming its own item is idempotent (not an error)
    it = claim(qpath, "t1", "agentA")
    if it["status"] == "claimed" and it["claimed_by"] == "agentA":
        print("[self-test] PASS same-agent re-claim is idempotent")
    else:
        print("[self-test] FAIL same-agent re-claim broke state", file=sys.stderr)
        ok = False

    # 5. release then re-claim by a different agent succeeds
    release(qpath, "t1")
    it = claim(qpath, "t1", "agentB")
    if it["claimed_by"] == "agentB":
        print("[self-test] PASS release + re-claim by a different agent succeeds")
    else:
        print("[self-test] FAIL release + re-claim did not transfer ownership", file=sys.stderr)
        ok = False

    # 6. done then claim must fail
    mark_done(qpath, "t1")
    try:
        claim(qpath, "t1", "agentC")
        print("[self-test] FAIL claiming a done item was NOT refused", file=sys.stderr)
        ok = False
    except QueueLockError:
        print("[self-test] PASS claiming a done item refused")

    # 7. stats totals add up
    s = stats(qpath)
    if s["total"] == 1 and s["done"] == 1:
        print("[self-test] PASS stats totals correct")
    else:
        print(f"[self-test] FAIL stats wrong: {s}", file=sys.stderr)
        ok = False

    # 8. lock is actually released after each op (a second immediate op does not hang/timeout)
    t0 = time.time()
    add_items(qpath, [_mk("t2", "atom-triage", "t2title", "t2brief", "L", "src2")])
    dt = time.time() - t0
    if dt < 1.0:
        print(f"[self-test] PASS lock released promptly (next op took {dt*1000:.0f}ms)")
    else:
        print(f"[self-test] FAIL lock held too long ({dt*1000:.0f}ms)", file=sys.stderr)
        ok = False

    # 9. seed_default produces internally-consistent items (schema + category validity)
    seeded = seed_default()
    seen_ids = set()
    schema_ok = True
    for it in seeded:
        if it["id"] in seen_ids:
            schema_ok = False
            print(f"[self-test] FAIL duplicate seed id: {it['id']}", file=sys.stderr)
        seen_ids.add(it["id"])
        if it["category"] not in CATEGORIES or it["priority"] not in PRIORITIES:
            schema_ok = False
            print(f"[self-test] FAIL bad category/priority on {it['id']}", file=sys.stderr)
        if not it["brief"] or not it["source"]:
            schema_ok = False
            print(f"[self-test] FAIL empty brief/source on {it['id']}", file=sys.stderr)
    if schema_ok:
        print(f"[self-test] PASS seed_default produces {len(seeded)} schema-valid, unique-id items")
    else:
        ok = False

    print(f"[self-test] leftover temp dir (not auto-removed, by design): {tmp_dir}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
