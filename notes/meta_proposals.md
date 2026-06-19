# META proposals — approved and self-implementing

Format: each proposal has rationale, proposed change (specific file edit or
new protocol), risk assessment. User approves, rejects, or asks for revision.
META does not implement session prompt edits; **sessions self-implement
approved protocols via `notes/active_protocols.md`** — the user is not in
the loop after approval.

See `[[sessions-self-coordinate]]` feedback memory for the routing
mechanism.

---

## Proposal 1 — Bootstrap stubs for session output files

**Status**: ✅ APPROVED 2026-05-21. Live as PROT-001 in
`notes/active_protocols.md`. Each session self-implements on next cycle.

**Rationale**: META cannot distinguish "session hasn't run yet" from "session
ran but produced no output" — both look like "file absent." Stubs make this
distinguishable.

**Implementation**: see `notes/active_protocols.md#PROT-001`. No session
prompt edits needed; sessions reach the protocol via MEMORY.md →
`feedback_sessions_self_coordinate.md` → `notes/active_protocols.md` on
cold start (per charter bootstrap step 1).

**Risk**: very low. Stubs are tiny and self-documenting.

---

## Proposal 2 — Version session prompts under `notes/session_prompts/`

**Status**: ✅ APPROVED 2026-05-21. Live as PROT-002 in
`notes/active_protocols.md`. Each session self-drops its own prompt on next
cycle.

**Rationale**: META currently cannot detect a session prompt change. Without
a versioned snapshot, a session that's silently operating under different
rules than its decision log reflects looks identical to a healthy session.

**Implementation**: see `notes/active_protocols.md#PROT-002`. META already
dropped:
- `notes/session_prompts/charter.md` (shared charter snapshot)
- `notes/session_prompts/session_6_meta.md` (META's own prompt snapshot)

Each of the other five sessions drops its own snapshot on next cycle. They
have verbatim access to their own prompts.

**Risk**: low. File goes stale if a session's prompt changes and the snapshot
isn't refreshed. Mitigation: `snapshot_taken` header makes staleness
detectable; PROT-002 instructs sessions to refresh when their prompt
materially changes.

---

## Proposal 3 — Make `active_protocols.md` a per-cycle read (not just cold start)

**Status**: ✅ APPROVED 2026-05-21 by user. IMPLEMENTED same day:
- `notes/active_protocols.md` top section now leads with "READ THIS FILE
  EVERY CYCLE" and includes the per-cycle rationale.
- `feedback_sessions_self_coordinate.md` (memory) appended with the
  "Per-cycle, not per-session" rule.

**Rationale**: Cycle 2 audit found that PROT-001 / PROT-002 only reached
Strategy. Four other sessions ran cycles without acknowledging them.
Root cause: charter's "Bootstrap protocol" says "Read MEMORY.md and the
linked feedback files" but specifies "every session, cold start" — not
every cycle. The MEMORY.md routing has a one-cold-start lag. If a session
stays warm across many cycles, it may never see new protocols.

**Proposed change**: Add a single line to `feedback_sessions_self_coordinate`
(the memory file) and to `active_protocols.md` itself making it explicit
that reading `notes/active_protocols.md` is a **per-cycle** action, not
cold-start-only.

Specifically, append to `active_protocols.md`'s top section:

> **READ THIS FILE EVERY CYCLE.** The charter's bootstrap protocol fires
> only at cold start; this file must be re-read every cycle to detect
> newly-added protocols. If your per-cycle protocol does not list this
> file, add it implicitly under your existing "files I check each cycle."

And append to `feedback_sessions_self_coordinate.md`:

> **Per-cycle, not per-session**: re-read `notes/active_protocols.md` at
> the start of every work cycle, not just on cold start. Charter's
> bootstrap protocol covers cold start; this is the per-cycle extension.

**Why this is safe**: it doesn't change file-ownership rules, doesn't add
new write surfaces, and only asks sessions to add one extra file-read per
cycle (small, idempotent). Risk: a session that re-reads but doesn't
re-implement a protocol it already saw will waste a few cycles deciding
"oh I already did this" — mitigated by PROT entries specifying `One-shot:
yes` and sessions tracking their own implementation status in decision
logs.

**Risk**: very low. Strategy already does this (cycle 2 found
active_protocols.md), so the pattern is proven feasible.

**Who would edit**: META (this is META's owned file + a memory file META
is authorized to update via the auto-memory protocol). No session prompt
edits required — same routing as before.

---

## Proposal 4 — Strategy: ground tier labels in capability descriptions (REVISED)

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 by user + Strategy.
Strategy applied to `active_priorities.md` (Top-priority queue +
Recently resolved table) and `cap_map v38` ("Grounded Tier-1 board"
section). Historical versions v3-v37 retain bare labels per honest-
record policy.

**Rationale**: User flagged that "Tier-1 KILLER" appears as a default
tier label in `substrate_capability_map.md` and `active_priorities.md`
without grounding. The label itself is fine when it's earned — but a
reader sees "Tier-1 KILLER, now unblocked" and has no inline answer to
"killer how?" That's the failure mode (per
`feedback_value_creation_not_competition` + `feedback_no_smoke`).

**Proposed change**: Strategy keeps tier labels where they're useful for
sorting / prioritization, but every "Tier-1" / "KILLER" / equivalent
asserts WHY in the same line. Concretely:

- KILLER section header: keep the section, but the table's first column
  is the capability description, second column says specifically what
  the product can do if the capability validates (one short sentence).
  Don't lead with "KILLER" alone.
- In `active_priorities.md`, each Bet header carries a one-line plain
  description of what would change for the substrate if the bet
  validates, ahead of any tier badge.

Concrete examples for today's bets:
- Bet A → "Verify an edited fact actually changes query output. KILLER
  if proven: substrate can be corrected in-place without retraining."
- Bet B → "Test learning a 3rd domain without erasing 1+2. KILLER if
  proven: substrate retains genuinely different domains, not just
  same-distribution shifts."
- Bet C → "Extend deletion past M_stored=N with structured codebook.
  Substrate becomes useful at higher storage densities."

The pattern: claim, then in the same sentence the substrate-level
consequence.

**Risk**: low. State markers (✅/🟢/🟡/🔬/⚪/❌) and tier order remain —
those are diagnostic and prioritization, not marketing. Only the bare
labels-without-grounding get rewritten.

**Who would edit**: Strategy (single writer of both files). META does
not unilaterally edit Strategy's files.

---

## Proposal 5 — Rehab-discipline PROT (PROT-004)

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 5 by META,
addressing Strategy's outstanding cycle-4 request and the standing
memory `feedback_closures_drop_under_batch_pressure.md`.

**Rationale**: Strategy re-flagged the unaddressed closure-rehab request
across cycles 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 (12 cycles).
The memory `feedback_closures_drop_under_batch_pressure.md` documents
that rules read at cold start drop reliably under batch pressure (5+
new outcomes in one cycle). Strategy demonstrated structural compliance
voluntarily (R8 #5 closure narrow-not-parent; Bet G + Bet H filed
PROVISIONAL with rescue sketches + Research routing), and the framework
worked — 2/2 PROVISIONAL closures flipped back to ✅ within one cycle.
But the discipline was memorial only. META owes Strategy structural
enforcement.

**Implementation**: filed as PROT-004 in `notes/active_protocols.md`.
Per-closure trigger, three same-commit requirements (rescue sketches +
Research request + PROVISIONAL tag), adherence-marking format.

**Risk**: very low. Strategy has already been operating to this
discipline; the PROT just codifies what's been done voluntarily. No
session prompt edits required — PROT entries reach all sessions via
the now-per-cycle `active_protocols.md` reading (Proposal 3 mechanism).

---

## Proposal 6 — Experiment Dev on /loop with continuous-pipeline cadence

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 8 by META.
Filed as PROT-005 in `notes/active_protocols.md`. Experiment Dev
self-implements on its next cycle via the active_protocols per-cycle
re-read (PROT-3) mechanism.

**Rationale**: User-clarified rule (this morning) — Experiment Dev should
maintain queue depth ≥ 1 at all times; buffer is for design quality not
throughput. Currently Strategy and Research are both on /loop with
self-pacing; Experiment Dev appears to be user-triggered only. Cycle 7
audit observed: queue empty from 12:14 to 12:44 (30 min); Strategy's
12:06 request file unread for 38+ minutes. Strategy explicitly flagged
this in cycles 21 and 22 ("Experiment Dev STILL paused... push request
unread").

A per-cycle PROT requiring sessions to check incoming `<session>_request_from_*`
files would help — BUT only if each session has cycles to do the checking
in. Experiment Dev needs an automatic cadence first.

**Proposed change**: Experiment Dev sets up `/loop` with a continuous-
pipeline-aware prompt. Suggested cadence: check queue depth on each
fire; if depth < threshold (e.g., < 2), consume incoming request files
or pull next top-priority item from `active_priorities.md`; if depth
≥ threshold, write a heartbeat-only entry and wait.

Concretely, Experiment Dev would:
1. Create `C:\Users\marsh\.claude\commands\experiment-dev-cycle.md`
   (per PROT-003 slash-command pattern) containing its full bootstrap +
   per-cycle protocol body.
2. Set up `/loop /experiment-dev-cycle` with appropriate cadence
   (~10-15 min while pipeline is active; longer if quiet).
3. The fired cycle checks queue depth + reads incoming request files
   first, before any speculative work.

**Who would edit**: Experiment Dev session sets up its own /loop and
slash command (same pattern Strategy + Research used). User authorizes
the slash-command file creation per PROT-003.

**Risk**: low. Same /loop pattern Strategy and Research already use.
The only risk is Experiment Dev queueing speculative work to fill the
queue when nothing genuinely needs queueing — but the new memory
`feedback_two_experiments_per_cycle.md` (continuous pipeline framing)
already covers that: "queueing should never be rushed... buffer is for
design quality not throughput." Experiment Dev's cycle 5 Entry 8
showed honest scope discipline ("user instruction was scoped to an
existing backlog, not invent infinity experiments"); /loop cadence
won't break that.

**What this does NOT solve**: if Experiment Dev fires on /loop but the
GPU runs through the queue faster than Experiment Dev can analyze
verdicts and queue follow-ups, the queue still drains. That's the
genuinely-hard scheduling problem the user's continuous-pipeline rule
implicitly assumes is rare. Worst case, /loop cadence reduces the gaps
from "user-trigger-bound" (potentially hours) to "/loop-cadence-bound"
(10-15 min).

---

## Proposal 7 — PROT-006: sequence rehab before cap_map closure update

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 13 by user.
PROT-006 filed in `notes/active_protocols.md` with the four-step
atomic sequence, enforcement rule (cap_map commit fails if request
file not on disk), and adherence marker extending PROT-004's.

**Rationale**: PROT-004 requires rescue sketches + Research request +
PROVISIONAL tag at closure time, but doesn't enforce ORDERING. Strategy
cycles 43-44 showed the failure mode: under high verdict throughput
(6 experiments + 3 R-notes in 30 min), Strategy updated cap_map first
with ❌ closures (Bet N, Bet O), then drafted rescue sketches later.
User caught the drift twice in 10 minutes (cycle 43 framing + cycle 44
rehab). Strategy's own framing:

> "Lesson for META (potential PROT entry): Negative-verdict integration
> into cap_map should NOT precede the Strategy → Research rehab routing
> for that verdict. Required sequence: (1) verdict harvested, (2) 5
> axis-combination rescue sketches drafted, (3) request file filed,
> (4) cap_map updated with PROVISIONAL tag and file pointer. Steps 1-3
> must be atomic; cap_map step deferred until 3 complete."

**Proposed change**: file PROT-006 in `active_protocols.md` enforcing
the sequencing. Cap_map commits filing a ❌ closure (full or
PROVISIONAL) must reference a sibling request file already on disk
with the rescue sketches. If the request file isn't present, the
closure commit is treated as incomplete and reverted.

**Concretely**, the four-step sequence is per-closure atomic:
1. **Harvest verdict** (read metrics.json + event_outcome).
2. **Draft 5 axis-combination rescue sketches** as DRAFT in a request
   file.
3. **File `strategy_request_to_research_<bet>_rehab_<date>.md`** with
   the sketches + multi-probe success criteria + sequencing
   recommendation.
4. **Cap_map update**: ❌ PROVISIONAL row entry with explicit pointer
   to the request file in the row text.

If step 3 is missing at the time of step 4, the cap_map commit must
be reverted and re-done in the correct order.

**Risk**: very low. Strategy already does steps 1-4 voluntarily; this
just enforces order. The user catches are the empirical evidence that
the current order is failing under batch pressure.

**Who would implement**: META adds PROT-006 to `active_protocols.md`
upon user approval. Strategy self-applies via the per-cycle re-read
(Proposal 3 mechanism). No other session prompt edits needed.

**Connection to existing infrastructure**: this is a structural
reinforcement of PROT-004, not a new protocol — same trigger
(❌ closure), same required artifacts (rescue sketches + request
file), just adds sequencing. Could be filed as "PROT-004 amendment"
or as "PROT-006" — META prefers the latter for clarity.

---

## Proposal 8 — PROT-007: cap_map two-file split + compact version table

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 13 followup by
user ("do it"). PROT-007 filed in `notes/active_protocols.md`.

**Rationale**: META cycle 13 followup #2 audit found
`substrate_capability_map.md` at 326 KB / 5024 lines after v62, with
~60% of the bytes being version-update prose blocks (v2 update / v3
update / ... / v62 update) that Strategy reads every cycle but only
NEEDS on rare audit / retraction context-lookups. The same narrative
also lives in Strategy's per-cycle decision log
(`strategy_decisions_2026-05-21.md`, 2200 lines) — significant
duplication. Strategy hit a context limit at cycle 40 (v57) and had
to write a handoff entry; v62 is larger and growing.

**Proposed change**: split into two files (atomic edits):

1. **`notes/substrate_capability_map.md`** (live working file, ~1500-2000
   lines target):
   - All row tables (full current state per capability cluster)
   - Tier-1 board + theoretical grounding + compound capabilities
   - Recently retracted + CANNOT + UNSURE sections
   - **Version summary TABLE** at the bottom — one row per version,
     compact: `vN | date | what changed | trigger experiment | link to
     history`. Pure-state lookup; no prose narrative.

2. **`notes/substrate_capability_map_history.md`** (archive,
   append-only):
   - All current "vN update — ..." prose blocks, moved verbatim from
     cap_map.md
   - Strategy writes here when committing a new version; then writes
     the one-line entry in cap_map.md's version table
   - Read by Strategy only on demand (audit, retraction context,
     META requests)

**Going-forward discipline**: each cap_map version commit touches BOTH
files atomically. PROT-007 enforces this via the same sequencing rule
as PROT-006 (cap_map.md commit must reference an updated history.md
with mtime within seconds of the commit).

**Optional second-order wins** (not part of the minimal restructure):
- Evidence-list pruning for ✅-validated rows with 5+ confirming
  experiments (keep top 3 + "(N more in history)" pointer)
- Decision-log cross-references in version table entries (point to
  `strategy_decisions_<date>.md` cycle N instead of re-narrating
  rationale)

**Risk**: very low. Trivially reversible (concat the two files
restores prior state). One-time restructure pass by Strategy
(estimated 1-2 cycles). Discipline going forward is one extra file
touch per cap_map commit.

**Result**: cap_map.md drops from 326 KB → ~120 KB (-65%). Per-cycle
Strategy read drops from ~80K tokens → ~30K tokens for cap_map alone.
Should restore meaningful context-budget headroom and reduce
Strategy-handoff frequency.

**Who implements**: Strategy (single writer of cap_map). META filed
PROT-007 in `active_protocols.md`; Strategy self-applies on next cycle
via per-cycle re-read.

---

## Proposal 9 — PROT-008: pre-commit cap_map validator (mechanical enforcement)

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 18 followup by
user ("implement the best practice here"). PROT-008 filed in
`notes/active_protocols.md`; validator script at
`tools/validate_capmap_commit.py`; tested against current cap_map
(catches 1 real violation + 12 PROT-007 hygiene warnings; no false
positives in legend/tally/history sections).

**Rationale**: 4 overcloses in 5 hours of high-tempo work this
session, all caught only after the bad commit landed (user catches
2x, Experiment Dev catch 1x, Strategy self-catch 1x). The catches
required cross-session attention; not mechanically enforced. PROT-004
+ PROT-006 specified the discipline but relied on Strategy's
judgment under verdict-batch pressure.

**Implementation**: `tools/validate_capmap_commit.py` (~250 lines)
enforces 3 invariants mechanically:
1. Every ❌ closure capability row references an existing rehab
   request file (or is explicitly grandfathered).
2. cap_map version-table entries have matching history.md blocks.
3. PROT-007 hygiene: history-update prose blocks shouldn't remain in
   cap_map.md.

False-positive suppression handles legend bullets, summary tally
tables, retracted/CANNOT sections, and history-block prose.

**v1 catches**: missing rehab files (would have caught v62 Bet N/O
closures); orphan history entries; missing PROVISIONAL tags.

**v1 does NOT catch**: closure-scope-overreach (v60 multi-hop pattern;
requires rescue-inventory cross-check); seed-variance misreads (v65
Bet B; requires content judgment); multi-probe quality (v65 Bet E;
requires evidence-quality assessment). Deferred to v2 if patterns
recur.

**Strategy integration**: add a `python tools/validate_capmap_commit.py`
step to `/strategy-cycle` slash command body between "draft cap_map
changes" and "atomic commit." Block commit on non-zero exit.

**Cost**: ~1 hour Strategy time to integrate; validator runs in
<1 second per commit. Tradeoff: small per-commit overhead for
mechanical catch of the dominant overclose pattern.

**Risk**: very low. If validator over-flags, integration is
trivially removed. Validator itself remains as ad-hoc audit tool.

---

## Proposal 10 — PROT-009: mechanical decision-log enforcement (Strategy-originated)

**Status**: ✅ APPROVED + IMPLEMENTED 2026-05-21 cycle 24 followup by
user ("approved prop 10."). PROT-009 filed in
`notes/active_protocols.md`; validator extended with `--staged-files`
argument + `check_decision_log_paired` invariant; tested in 4
scenarios (no flag silent-skip; cap_map without decision log fails
exit 6; cap_map with decision log passes; --exempt-prot-009 skips
with INFO). Closes the last structural gap in the coordination
contract.

**Novelty**: this is the FIRST proposal originated by another session
and routed through META. Cross-session protocol request pattern per
`feedback_sessions_self_coordinate`.

**Empirical rationale (Strategy's own diagnosis)**: 5 decision-log
gaps caught this session, all the same pattern:

| Cycle | Catch | Gap duration |
|---|---|---|
| 53 | META cycle 16 audit | cycles 45-53 (~90 min) |
| 66 | META cycle 19 audit | (continued) |
| 66 | META cycle 21 audit | 130+ min silent |
| 66 | META cycle 22 audit | 130+ min silent (heartbeat) |
| 67 | Strategy self-catch | cycles 55-66 (~130 min) |

Under verdict-batch tempo (3-6 experiments + research deliveries in
5-10 min), cap_map version updates land atomically (PROT-007 +
PROT-008 mechanically enforced) but decision-log entries get skipped
— Strategy's cognitive load goes to cap_map state updates; the
decision-log entry feels redundant in the moment and gets dropped.
PROT-006 + PROT-007 + PROT-008 each closed a specific gap mechanically;
PROT-009 closes the remaining one.

**Proposed change**: Strategy commits that touch
`notes/substrate_capability_map.md` MUST also include
`notes/strategy_decisions_<date>.md` in the same commit. Enforced by
extending `tools/validate_capmap_commit.py` with
`check_decision_log_paired(staged_files)`.

**Validator extension** (Strategy-supplied stub):

```python
def check_decision_log_paired(staged_files: set[str]) -> None:
    """PROT-009: cap_map version updates must be paired with
    strategy_decisions entries in the same commit."""
    cap_map_changed = "notes/substrate_capability_map.md" in staged_files
    decision_log_changed = any(
        f.startswith("notes/strategy_decisions_")
        for f in staged_files
    )
    if cap_map_changed and not decision_log_changed:
        fail(
            6,
            "cap_map commit without decision_log entry",
            hint=(
                "PROT-009 requires Strategy decision-log entry paired "
                "with any cap_map version commit. Add cycle N entry to "
                "strategy_decisions_<date>.md and re-commit atomically."
            ),
        )
```

**Implementation requires**:
- Add `--staged-files <list>` argument to validator (Strategy passes
  the list of files in the current commit when invoking)
- Add `check_decision_log_paired` to invariants
- New exit code 6 for PROT-009 failures

**False-positive suppression** (Strategy's spec):
- Exempt PROT-007 hygiene commits (mechanical file-restructure, no
  state change). Heuristic: if cap_map net line change is NEGATIVE
  (lines removed > added), skip the check.
- Commit-message tag `[PROT-009-exempt]` for explicit override.

**Risk**: very low. Same mechanical-enforcement pattern as PROT-006
and PROT-008. Strategy already does decision-log entries voluntarily;
PROT-009 just makes the discipline structural.

**Cross-references**:
- `notes/strategy_request_to_meta_PROT_009_proposal_2026-05-21.md`
  (Strategy's request file — load-bearing)
- META audits cycles 16, 19, 21, 22 (gap detection)
- Strategy decision log cycles 53 (1st catchup), 67 (2nd catchup)
- PROT-006/007/008 (mechanical-enforcement predecessor pattern)

**Who implements**: META adds PROT-009 to `active_protocols.md` upon
user approval; META extends validator script with the new check.
Strategy then integrates the `--staged-files` argument into the
`/strategy-cycle` slash command body (alongside the existing PROT-008
invocation).

---

## Mechanism summary (one-time, for reference)

Approved cross-session protocols flow:

```
META proposes → meta_proposals.md
User approves → META adds entry to notes/active_protocols.md
Each session reads MEMORY.md → feedback_sessions_self_coordinate.md
                            → notes/active_protocols.md
                            → self-implements applicable protocols
                            → marks adherence in own decision log
META audits decision logs vs active_protocols.md for drift
```

No user-side coordination between approval and implementation.

---

## Proposal 11 — Per-cycle pipeline + Research delivery completeness scan (PROT-010 candidate)

**Status**: PROPOSED 2026-05-22 (META cycle 61).

**Rationale**: 3 documented attention-allocation gap instances this
session:
- Cycles 90-92 missed 2 Research deliveries (caught cycle 93 via user
  nudge)
- Cycles 105-108 missed verdicts under verdict-batch pressure (caught
  via Strategy self-check in cycle 109)
- Cycle 116 missed 2 smoke verdicts (caught via user prompt "didn't an
  experiment complete?")

Each gap = Strategy ran one or more cycles without integrating
Research deliveries or pipeline verdicts that landed since the last
Strategy commit. Pattern recurring under verdict-batch pressure.
Informal discipline (Strategy self-flagged mtime check at cycle 95)
reduces frequency but doesn't eliminate. Cycle 116 explicitly:
"PROT-010 candidate strengthens; mitigation = per-cycle dashboard
MUST scan ALL recent_verdicts entries chronologically not just most
recent."

**Proposed change**: add PROT-010 to `notes/active_protocols.md`:

```
## PROT-010 — Per-cycle pipeline + Research delivery completeness scan

- Status: active (approved 2026-05-22; addresses 3 documented
  attention-allocation gaps cycles 90-92, 105-108, 116)
- Applies to: Strategy (only writer of cap_map)
- Trigger: every Strategy /loop cycle, BEFORE drafting cap_map changes
- Per-cycle, always-on

What to do: add as first step in /strategy-cycle slash command body,
before dashboard check or cap_map draft:

1. `ls -lt notes/research_*<date>.md notes/research_*.md` — find
   research notes with mtime > last cap_map commit time. If found,
   read + integrate before drafting cap_map.
2. `ls -lt notes/*_request_to_strategy_*.md` — find inbound request
   files with mtime > last cap_map commit time. If found, read +
   integrate or respond.
3. `data/local_dashboard_snapshot.json` recent_verdicts: scan ALL
   entries chronologically (not just first / latest). Any verdict
   with mtime > last cap_map commit time → integrate before drafting.
4. Decision log entry MUST include explicit line: "PROT-010
   completeness scan: <N research> + <M requests> + <K verdicts> new
   since last cap_map; <integrated|none>"

Adherence marker (extends PROT-004/006/008/009):

PROT-004/006/008/009/010 compliance this commit:
- completeness scan: <N research> + <M requests> + <K verdicts> new;
  integrated
- <other PROT compliance markers>

Reversibility: trivially reversible — remove scan step from
/strategy-cycle slash command body.
```

**Risk**: low. Adds ~30s to each Strategy cycle (3 ls + 1 json scan).
Doesn't change cap_map semantics. Strategy already does informal
version of this; PROT-010 makes it mechanical.

**Files affected**: `notes/active_protocols.md` (new PROT-010 entry);
`C:\Users\marsh\.claude\commands\strategy-cycle.md` (Strategy adds
scan step to slash-command body on next cycle after approval).

**Why now vs cycle 50 retirement**: at cycle 50 I retired the
candidate after 4 clean cycles. Two more instances since then (cycles
105-108 missed by Strategy, caught in 109; cycle 116 caught by user)
demonstrate the informal discipline isn't fully robust. Third
instance with user-nudge-required catch is the criterion I set at
cycle 49 for proposing formally.

---
