# Registry residue re-check (hdi_testbed, 2026-08-15 ~17:30Z)

## Finding
The **~61 unregistered hdlab modules** figure (from `notes/registry_tighten_audit_2026-08-13.md`,
itself produced by `tools/capability_registry_audit.py`'s `scan_unregistered_hdlab_modules`) is
**STALE and superseded**. That 08-13 audit's own writeup flags its method's blind spot at line 323:
"Sub-package modules are outside the audit's blind spot check" — i.e. its enumeration used a
non-recursive `os.listdir` and missed modules living in `hdlab/` sub-packages.

A registry reconciliation landed later (127 -> 198 rows in `data/capability_registry.jsonl`) that
root-caused this and other issues.

## Independent reproduction (this session, not trusting any prior number)
Method: `os.walk('hdlab')` recursively, excluding `__pycache__` dirs and `__init__.py` files,
producing relative POSIX-style paths. Cross-checked against `data/capability_registry.jsonl`
(198 rows) three ways:

1. **Exact match against each row's `path` field** (string or, for 43 rows, a list of strings):
   152 modules on disk, **0 missing** (152/152 matched).
2. **Stronger heuristic — any string field anywhere in a row** (covers `used_by`, notes, or any
   other field that might reference a module by an alias other than its canonical `path` entry):
   still **0 missing** (152/152 matched). This is a strict superset of check 1 and found no
   additional gaps, so aliasing-only references are not hiding anything.
3. **Reverse check — dangling registry rows**: every `path`-field string beginning with `hdlab/`
   was checked against the on-disk module set. **0 dangling** (no registry row points at a
   `hdlab/*.py` file that no longer exists).
4. Two registry rows have an empty `path: []` by design (`sr_routing_multihop`,
   `binder_direct_supply_grounding`), both explicitly `status: orphaned_source_not_locatable_*` /
   `closed_correctly_data_bound` — correctly excluded, not residue.

**Conclusion: 0 of 152 hdlab modules unregistered, confirmed independently, by two convergent
heuristics plus a reverse dangling-pointer check.** This corroborates (does not just repeat) the
fresh recompute cited in the dispatch-queue brief for this task, and contradicts the ~61 figure
still carried in `notes/RECOVERY_PROGRAM.md` and `CLAUDE.md`'s evidence-discipline section.

## What this does NOT check
This audit answers EXISTS (on disk) vs IS-REGISTERED (row in `capability_registry.jsonl`) only.
It does not answer IS-REACHED (actually imported/called at runtime) or IS-GOOD (produces a
verified capability) — those are separate questions per the standing discipline, and this task
was scoped to the registry-residue question only.

## Method reproducibility
Script used: ad hoc, `os.walk` + `json.loads` per line of the registry file, no external deps.
Not committed as a tool (task scope was verification, not tooling). Anyone can reproduce in
~1 second by re-running the same walk against current disk state — the registry gap should be
re-checked this way (filesystem enumerated first, reconciled to registry second) rather than
trusting either the 61 or the 0 figure as durable; both are timestamped snapshots.

## Files flagged as citing the stale figure (not edited — out of scope / DO-NOT-TOUCH)
- `CLAUDE.md` (evidence-discipline section) — DO-NOT-TOUCH per this session's constraints.
- `notes/RECOVERY_PROGRAM.md` — DO-NOT-TOUCH per this session's constraints; ownership unclear,
  left for the owner to fold this finding in.
