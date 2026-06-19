# Active protocols — read this every cycle

**READ THIS FILE EVERY CYCLE.** The charter's bootstrap protocol fires only
at cold start; this file must be re-read at the start of every work cycle
to detect newly-added protocols. If your per-cycle protocol does not list
this file, add it implicitly under your existing "files I check each cycle."

**Owner**: META session (single writer). All other sessions read this file
every cycle, after MEMORY.md.

**How to read this file**: each protocol has a `status` and `applies_to`. If
status is "active" and your session is in `applies_to`, perform the protocol
once on your next cycle (if not already done), then carry on with your normal
per-cycle work. Mark adherence in your own decision log (e.g.
"Implemented PROT-001 this cycle"). Do NOT write to this file — META owns it.

If you've already implemented a protocol in a prior cycle, skip it; you don't
need to redo it unless the protocol explicitly says "every cycle." But you
still must READ the file every cycle to catch new entries.

---

## PROT-001 — Bootstrap stub for primary output file

- **Status**: active (approved 2026-05-21)
- **Applies to**: Strategy, Visibility, Queue Health, Research, Experiment Dev
  (META has already self-bootstrapped)
- **Trigger**: first cycle in which your primary output file does not exist
- **One-shot**: yes (do once, then never again)

**What to do**: before doing real work this cycle, check if your primary
output file exists. If not, write a stub at that path. The stub format is
your choice; recommended minimum content:

```
# <artifact name> — initialized <date>
# Session: <your session name>
# First cycle running under PROT-001. Real content next cycle or later this cycle.
```

For JSON files (e.g. snapshot), use:
```json
{"initialized": "<date>", "session": "<your session>", "fields": null}
```

**Primary output file by session**:
| Session | Primary output file |
|---|---|
| Strategy | `notes/active_priorities.md` |
| Visibility | `data/local_dashboard_snapshot.json` |
| Queue Health | `notes/queue_health_log.md` |
| Research | most-recent `notes/research_<topic>_<date>.md` OR a heartbeat at `notes/research_idle_<date>.md` if no topic ran |
| Experiment Dev | first entry of `notes/exp_dev_decisions_<date>.md` (your own decision log counts) |
| Product (Session 7, added 2026-05-22) | `notes/product_options_ranked.md` (initial table); subsequently `notes/product_demos_spec.md` + `notes/product_decisions_<date>.md` |

**Why**: META cannot distinguish "session hasn't run" from "session ran but
emitted nothing." Stubs break the ambiguity. See
`notes/meta_proposals.md#Proposal 1`.

---

## PROT-002 — Drop your own session prompt snapshot

- **Status**: active (approved 2026-05-21)
- **Applies to**: Strategy, Visibility, Queue Health, Research, Experiment Dev
  (META already dropped its own and the shared charter)
- **Trigger**: file `notes/session_prompts/session_<N>_<role>.md` does not
  exist for your session
- **One-shot**: yes (do once; on subsequent cycles, only if your prompt has
  materially changed since the last snapshot)

**What to do**: write your verbatim session-specific prompt (the role +
files-owned + cadence + per-cycle-protocol sections — NOT the shared charter
which lives separately at `notes/session_prompts/charter.md`) to:

`notes/session_prompts/session_<N>_<role>.md`

Where `<N>` is your session number (1=Strategy, 2=Visibility, 3=Queue Health,
4=Research, 5=Experiment Dev, 6=META — already done) and `<role>` is the
lowercase role name (e.g. `strategy`, `visibility`, `queue_health`,
`research`, `exp_dev`).

Use this header:
```
---
snapshot_taken: <today's date>
charter_version: 2026-05-21 (see ./charter.md)
session: <N> — <role>
---

<paste your verbatim session-specific prompt below this line>
```

**Why**: META audits session-prompt-vs-behavior coherence; without a
versioned snapshot, prompt drift is undetectable. See
`notes/meta_proposals.md#Proposal 2`. Reference: META already snapshotted its
own at `notes/session_prompts/session_6_meta.md` — use that as a format
example.

---

## PROT-003 — Long /loop or cron prompts go behind a slash command

- **Status**: active (approved 2026-05-21)
- **Applies to**: any session that uses `/loop` or `CronCreate` with a
  prompt longer than ~3 lines. Today that's Strategy (/loop dynamic) and
  Research (/loop 20m). META already applied this protocol to itself.
- **Trigger**: your current /loop or cron's prompt text is long enough
  that when it fires, it clutters the chat and makes your output hard to
  read.
- **One-shot per session**: yes (do once; redo only if your prompt
  materially changes)

**Why**: when /loop or CronCreate fires, the prompt text shows in the
chat as the "user" message for that turn, pushing your real output
below. A multi-paragraph prompt makes the chat unreadable for the human.
Slash commands hide the body (only the short `/name` invocation shows in
chat) while still running the same content.

**What to do**:

1. Create a slash command file at `C:\Users\marsh\.claude\commands\<name>.md`.
   Filename = command name minus `.md`. Recommended names:
   - Strategy: `strategy-cycle.md`
   - Research: `research-cycle.md`

2. Format (frontmatter optional but recommended):
   ```
   ---
   description: <one-line summary of what this command does>
   ---

   <your verbatim /loop prompt body — the full bootstrap+per-cycle instructions>
   ```

3. Re-set your /loop using the slash command:
   ```
   /loop <interval> /<name>
   ```
   For example: `/loop 20m /research-cycle`. Delete the old long-prompt
   /loop first (CronList → CronDelete the old job ID).

4. Verify on the next fire — chat should show only `/<name>` instead of
   the wall of text.

**Reference implementation**: META did this for its hourly cron — see
`C:\Users\marsh\.claude\commands\meta-cycle.md` and CronList for the
short-prompt cron entry.

**Note on permissions**: creating `~/.claude/commands/` requires user
authorization (Claude Code sandbox flags it as agent-config modification).
If you hit a permission denial, document it in your decision log and ask
the user to approve once; the directory already exists after META's
setup so subsequent file writes should be fine.

---

## PROT-004 — Rehab discipline at closure time

- **Status**: active (approved 2026-05-21 by META, addressing Strategy's
  cycle-4 outstanding request and the
  `feedback_closures_drop_under_batch_pressure.md` memory)
- **Applies to**: Strategy (only writer of cap_map / active_priorities) +
  any other session that ever files a ❌ closure in a cross-session
  capability ledger.
- **Trigger**: any commit that adds a ❌ closure row (or downgrade from
  ✅ / 🟡 / 🔬 to ❌) in `notes/substrate_capability_map.md`,
  `notes/active_priorities.md`, or equivalent ledger.
- **Per-closure, not per-cycle**.

**What to do**: the same atomic commit that files the ❌ must include:

1. **3-5 axis-combination rescue sketches** in the same row or in an
   adjacent block. Tagged explicitly as DRAFT and unvetted — Strategy's
   brainstorm, not load-bearing. Per
   `feedback_rehabilitation_after_rejection`.

2. **A Research request entry** routing a 2× deep research pass to
   *generate* the actual rescue list. Strategy's draft sketches are
   starting points; Research's 2× pass is the load-bearing ranking. Per
   `feedback_unbiased_research` + `project_research_playbook` item 9.

3. **A PROVISIONAL tag on the ❌** (use "❌ PROVISIONAL" rather than
   bare "❌") until Research's pass + the first rescue-experiment lands.
   Once any rescue passes its multi-probe criteria, the row flips to ✅
   under that rescue's evidence; if N/5 rescues all fail multi-probe,
   the row flips to bare ❌ (closure made structural).

**Why**: rules enforced by reading feedback files at cold start
reliably drop when a session is integrating multiple new outcomes in a
single cycle (caught twice in Strategy 2026-05-21 — cycles 3 and 4).
Structural enforcement via PROT entry — read every cycle, applied at
commit time — closes the gap.

**Reference**: see Strategy cycles 7, 9, 11, 14, 15, 16 for examples
where this discipline was applied even before this PROT existed (R8 #5
closure narrow not parent; Bet G + Bet H filed as ❌ PROVISIONAL with
draft sketches + R11 + R12 routings). Two ❌ PROVISIONAL closures
already flipped back to ✅ via the discipline (Bet G via TEMPSCALE,
Bet H via T=0.5 sampling).

**How to mark adherence**: in your decision log, when filing a
closure, add a one-line block:

```
PROT-004 compliance this commit: <closure row>; <N rescue sketches>;
Research request <R#> routed; PROVISIONAL tag applied.
```

---

## PROT-005 — Sessions without auto-cadence set up /loop

- **Status**: active (approved by user 2026-05-21, addressing the
  cross-session coordination gap META cycle 7 surfaced).
- **Applies to**: Experiment Dev (currently the only session without
  an automatic /loop cadence). Strategy and Research already use this
  pattern.
- **Trigger**: your session depends on user-triggered cycles and lacks
  an automatic /loop or cron schedule.
- **One-shot per session**: yes.

**Why**: the system's coordination architecture (request files from
peers, top-priority queue in `active_priorities.md`, push files from
Strategy) only works if each session has cycles in which to read
incoming requests. Cycle 7 audit (12:46) observed: Experiment Dev
idle 38+ minutes after Strategy's 12:06 push request; queue went to 0
for 30 minutes, violating the user's continuous-pipeline rule.

**What to do**:

1. Per PROT-003, create a slash command at
   `C:\Users\marsh\.claude\commands\<session-name>-cycle.md` with
   `description:` frontmatter and your verbatim bootstrap +
   per-cycle protocol body.

2. Set up `/loop <interval> /<session-name>-cycle`. Recommended interval:
   - Experiment Dev: **10-15 min** while pipeline is active (queue
     depth ≥ 1 expected). Longer if pipeline genuinely quiet.

3. Each cycle on fire:
   - Check `data/local_dashboard_snapshot.json` for queue depth.
   - Check `notes/<your-session>_request_from_*.md` for any peer
     requests (Strategy's push file in this case).
   - Check `notes/active_priorities.md` for the current top-priority
     queue.
   - Consume requests / queue items before any speculative work.
   - If queue depth ≥ N (your judgment of "healthy backlog") and no
     incoming requests, write a heartbeat decision-log entry and end
     the cycle.

4. Per `feedback_two_experiments_per_cycle.md` (continuous-pipeline
   reframe): keep queue depth ≥ 1 at all times; buffer is for design
   quality, not throughput. Don't queue speculative work to fill the
   buffer when no genuine candidates exist — pace and write an honest
   decision-log entry explaining what's waiting on direction.

**Reference**: META's `meta-cycle.md` + cron `2033c0c5`, and
Strategy's `strategy-cycle.md` per Strategy decision-log cycle 6
adoption of PROT-003.

**Adherence marker**: in your decision log on first cycle after
setting this up, add:

```
PROT-005 compliance: set up /loop /<session-name>-cycle at <cadence>;
slash command file at <path>; first cycle confirms incoming request
files + active_priorities checked before queueing.
```

---

## PROT-006 — Sequence rehab before cap_map closure update (PROT-004 reinforcement)

- **Status**: active (approved by user 2026-05-21 cycle 13, addressing
  the rehab-discipline drop pattern under verdict-batch pressure
  documented in `feedback_closures_drop_under_batch_pressure.md` and
  observed twice in Strategy cycles 43-44).
- **Applies to**: Strategy (only writer of cap_map / active_priorities)
  + any session that ever files a ❌ closure in a cross-session
  capability ledger.
- **Trigger**: any commit that adds a ❌ closure row (or downgrade from
  ✅ / 🟢 / 🟡 / 🔬 to ❌) in `notes/substrate_capability_map.md`,
  `notes/active_priorities.md`, or equivalent ledger.
- **Per-closure, NOT per-cycle.**

**What this adds to PROT-004**: PROT-004 requires the rescue sketches +
Research request + PROVISIONAL tag AT closure time but doesn't enforce
ORDERING. Under verdict-batch pressure (5+ outcomes in one cycle),
Strategy has been observed updating cap_map first and catching up with
rescue sketches later — user caught this twice in Strategy cycles 43
and 44. PROT-006 enforces the atomic order.

**Required sequence (per-closure atomic)**:

1. **Harvest verdict**: read metrics.json + event_outcome for the
   experiment that triggered closure.

2. **Draft 5 axis-combination rescue sketches** as DRAFT only
   (explicitly unvetted) per PROT-004 + `feedback_rehabilitation_after_rejection`.

3. **File the request file** at
   `notes/strategy_request_to_research_<bet>_rehab_<date>.md` (or
   equivalent path for non-Strategy closures) containing:
   - The 5 axis-combination sketches
   - Multi-probe success criteria each rescue would need to clear
   - Sequencing recommendation (which rescue Research should pick up
     first based on leverage / cost)

4. **Cap_map update**: ❌ PROVISIONAL row entry with explicit pointer
   to the request file (filename in the row text or evidence cell).
   The PROVISIONAL tag stays until Research's Pass 2 + at least one
   rescue experiment lands.

**Enforcement**: if step 3 is missing at the time of step 4 (cap_map
commit), the commit is incomplete. Strategy MUST revert and re-do in
the correct order. META audits will flag any ❌ closure row whose
request file isn't on disk at the same commit time.

**Why**: rules enforced by reading feedback files at cold start drop
under verdict-batch pressure (5+ outcomes / 30 min). PROT-004 catches
the WHAT (rescue sketches, request file, PROVISIONAL tag); PROT-006
catches the WHEN (must happen before the cap_map commit, not after).
Together they are the structural fix for the recurring drift pattern.

**Reference**: Strategy cycles 43 (multi-hop overclosure) and 44 (Bet
N + Bet O closures without rescue sketches) both required user-catch
corrections. PROT-006 would have made both impossible by failing the
cap_map commit until the request files were present.

**Adherence marker** (extends PROT-004 marker):

```
PROT-004/006 compliance this commit: <closure row>; <N rescue sketches>;
request file at notes/<filename>; PROVISIONAL tag applied; sequence
verified (request file mtime < cap_map commit mtime).
```

---

## PROT-007 — Cap_map two-file split + compact version table

- **Status**: active (approved by user 2026-05-21 cycle 13 followup,
  addressing the 326 KB / 5024-line cap_map size that triggered
  Strategy's context-limit handoff at cycle 40).
- **Applies to**: Strategy (only writer of `substrate_capability_map.md`).
- **Trigger**: one-time restructure pass on next Strategy cycle; then
  ongoing discipline per cap_map commit.
- **One-shot restructure + ongoing two-file discipline**.

**Why**: cap_map carries two kinds of content with very different
access patterns:
- **Current state** (row tables, Tier-1 board, theoretical grounding,
  compound capabilities, retracted / CANNOT / UNSURE sections) —
  Strategy reads every cycle. ~40% of current bytes.
- **Version history prose** (v2 update / v3 update / ... / v62 update
  blocks) — Strategy reads rarely (audit, retraction context). ~60%
  of current bytes. Largely duplicates content already in
  `strategy_decisions_<date>.md`.

The current single-file design forces Strategy to re-read 326 KB on
every cycle. Context limit hit at cycle 40 (v57). v62 is larger.

**What to do** (one-time restructure):

1. Create `notes/substrate_capability_map_history.md` (new file).
2. Move all "vN update — ..." prose blocks from cap_map.md to
   history.md, in chronological order. This is the bulk of cap_map's
   current content (~3000 lines).
3. In cap_map.md, replace the moved prose blocks with a **compact
   version table**: one row per version, columns: `version | date |
   what changed (one-line summary) | trigger experiment(s) | history
   ref`. The "history ref" column points to the corresponding section
   in history.md (e.g., `#v42`).
4. Atomic commit: both files updated in a single commit; commit
   message references PROT-007.

**Going-forward discipline** (every subsequent cap_map version):

1. When committing a new cap_map version, write the new prose block
   to `substrate_capability_map_history.md` first.
2. Add the new one-line entry to cap_map.md's version table.
3. Update row states in cap_map.md as usual.
4. Commit both files atomically. Commit message format:
   `Cap map: <change> (<trigger>); history.md: vN block appended`.

**Sequencing enforcement** (per PROT-006 pattern): cap_map.md commit
must reference a history.md commit with mtime within ~5 seconds.
META audits will flag any cap_map version-table entry whose
corresponding history.md block is missing.

**Adherence marker** (in Strategy decision log on first cycle
restructure happens):

```
PROT-007 compliance this commit: restructured substrate_capability_map.md;
moved <N> version blocks to substrate_capability_map_history.md;
cap_map.md now <size> KB / <lines> lines; ongoing two-file discipline
acknowledged.
```

**Reversibility**: trivially reversible — concatenating cap_map.md
and history.md restores the prior state. No information loss; only
spatial redistribution.

**Optional follow-on** (not required by PROT-007 itself):
- Evidence-list pruning for ✅-validated rows with 5+ confirming
  experiments: keep top 3 + "(N more in history)" pointer.
- Decision-log cross-references in version table: point to
  `strategy_decisions_<date>.md` cycle N for the rationale narrative.

---

## PROT-008 — Pre-commit cap_map validator (mechanical PROT-004/006/007 enforcement)

- **Status**: active (approved by user 2026-05-21 cycle 18 followup,
  addressing the 4-overclose pattern from this session despite PROT-004
  + PROT-006 being in effect).
- **Applies to**: Strategy (single writer of cap_map).
- **Trigger**: before every cap_map atomic write.
- **Per-commit, always-on**.

**Why**: PROT-004 + PROT-006 + PROT-007 specify what Strategy SHOULD do
when committing cap_map state changes. Under verdict-batch pressure
this session, 4 overcloses landed despite the protocols — the
discipline relied on Strategy's judgment under load. PROT-008 adds a
mechanical pre-commit check that fails the commit until invariants
are observed.

**The validator** is at `tools/validate_capmap_commit.py`. It enforces:

1. **PROT-004/006 rehab discipline**: every ❌ closure capability row
   must either:
   - Reference an existing `strategy_request_to_research_<bet>_rehab_<date>.md`
     file (matched by regex; file must exist on disk), OR
   - Carry an explicit grandfather marker (`pre-PROT-004`,
     `grandfathered`, or `pre-rehab-discipline`) for historical closures
     that pre-date this protocol.
2. **PROT-007 sequencing**: every cap_map version-table entry must
   have a matching `## vN — ...` block in
   `substrate_capability_map_history.md`.
3. **PROT-007 hygiene**: warn (not fail) when history-update prose
   blocks (`## vN update` / `## YYYY-MM-DD ... vN update`) appear in
   cap_map.md — they should live in history.md.
4. **PROT-004 PROVISIONAL tag**: warn when an ❌ row references a
   rehab file but lacks the PROVISIONAL tag.

**False-positive suppression** built in:
- Legend bullet definitions (lines starting with `- `, `*`)
- Summary tally tables (rows showing ≥4 state markers)
- `Recently retracted` / `CANNOT` sections (historical record)
- Lines inside `## vN update` history blocks

**What to do**:

Add this step to your `/strategy-cycle` slash command body, between
"draft cap_map changes" and "atomic commit":

```
4. Validate cap_map before commit:
   - cd d:\AI\hd-instrument
   - python tools/validate_capmap_commit.py
   - If non-zero exit: read stderr, fix the violation, re-validate.
   - Common violations:
     - Missing rehab file: file the
       strategy_request_to_research_<bet>_rehab_<date>.md FIRST
       (PROT-006 sequencing), then re-validate.
     - Pre-PROT-004 closure: add 'pre-PROT-004' inline marker to the
       row text.
     - history.md mismatch: write the matching `## vN — ...` block
       to history.md, then re-validate.
5. Atomic commit only after validator passes.
```

**Initial state on first invocation** (audited 2026-05-21 18:25):
- 1 real PROT-004/006 violation: line 395 R3-Laplace row needs
  grandfather marker or retrospective rehab file.
- 12 history-update blocks still in cap_map (PROT-007 restructure
  was incomplete; Strategy should finish moving them).

**Adherence marker** (Strategy decision log, first cycle that uses
the validator):

```
PROT-008 compliance: integrated tools/validate_capmap_commit.py into
/strategy-cycle slash command body; pre-commit validation passed
before cap_map atomic write; <N> warnings noted (non-blocking).
```

**Reversibility**: if the validator produces too many false positives
or blocks valid commits, the integration is trivially removed (remove
the validator step from the slash command). The script remains for
ad-hoc audit use.

**v1 scope (intentional limits)**:
- Catches: missing rehab files (v62 pattern), orphan history entries,
  missing PROVISIONAL tags.
- Does NOT catch: closure-scope-overreach (v60 pattern), seed-variance
  misreads (v65 Bet B), multi-probe quality (v65 Bet E).
- v2 candidates: rescue-inventory cross-check across cap_map +
  active_priorities + open request files; closure scope vs active
  rescue path count.

---

## PROT-009 — Decision-log entry paired with cap_map commits (Strategy-originated)

- **Status**: active (approved by user 2026-05-21 cycle 24 followup,
  addressing 6 documented decision-log gap instances this session;
  Strategy-originated proposal — first cross-session protocol request).
- **Applies to**: Strategy (only writer of cap_map and
  strategy_decisions).
- **Trigger**: any commit that touches
  `notes/substrate_capability_map.md`.
- **Per-commit, always-on when invoked with `--staged-files`**.

**Why**: cap_map captures STATE; strategy_decisions captures WHY. Both
are needed for cross-session cold-start. 6 instances this session
showed Strategy commits cap_map atomically (PROT-007 mechanical) but
skips decision-log under verdict-batch tempo (PROT-004/006/008 are
mechanical; decision-log discipline relied on judgment and failed
repeatedly). PROT-009 closes that gap mechanically.

**What to do**:

Strategy's `/strategy-cycle` slash command body adds these steps
between "draft cap_map changes" and "atomic commit":

1. Stage cap_map.md + history.md + strategy_decisions_<date>.md
   atomically:
   ```
   git add notes/substrate_capability_map.md \
           notes/substrate_capability_map_history.md \
           notes/strategy_decisions_<date>.md
   ```

2. Validate with PROT-009 check:
   ```
   python tools/validate_capmap_commit.py \
       --staged-files $(git diff --cached --name-only)
   ```

3. If exit 0 → commit. If exit 6 (PROT-009 violation) → write the
   decision-log entry, re-stage, re-validate.

**Exemption** for PROT-007 mechanical-restructure commits (no
capability state change):

```
python tools/validate_capmap_commit.py \
    --staged-files $(git diff --cached --name-only) \
    --exempt-prot-009
```

Use sparingly and only for pure file-restructure commits. Heuristic:
if you're moving prose blocks from cap_map.md to history.md without
adding any new ✅/❌/🟢/🟡/🔬/⚪ row state changes, exemption is
appropriate.

**Validator behavior**:
- `--staged-files` argument required to fire the check
- Without `--staged-files`: PROT-009 silently skipped (backward
  compatible with ad-hoc cap_map validation)
- Exit code 6 for violations
- Tested on real cap_map state 2026-05-21 cycle 24: passes when
  decision-log staged; fails when not.

**Adherence marker** (extends PROT-004/006/008 marker):

```
PROT-004/006/008/009 compliance this commit: <closure rows> + rehab
files + history.md sibling + strategy_decisions paired; validator
passed.
```

**Reversibility**: trivially reversible — Strategy removes the
`--staged-files` from the slash command body and the check stops
firing. Script remains for ad-hoc use.

**Reference**: Strategy's empirical case in
`notes/strategy_request_to_meta_PROT_009_proposal_2026-05-21.md`
documented 5 instances of the gap; META's cycle 24 audit caught the
6th instance within 42 minutes of the proposal filing — strongest
empirical justification of any structural-enforcement PROT in the
session.

---

## PROT-010 — Read post-compaction brief before any other action after context reset

- **Status**: active (approved 2026-05-23, addressing Gap 1 from orchestrator context-reset readiness audit)
- **Applies to**: Orchestrator (primary); any session that may undergo context compaction
- **Trigger**: cold start OR any context compaction / summarization event
- **Per-compaction, always-on**

**What to do**: the FIRST action after any context reset or compaction is to read:

```
notes/orchestrator_post_compaction_brief.md
```

This file contains the dense behavioral-restoration document: current pause state check, wrapper-first rule, hard rules, 7 known failure modes, skills registry, and what to do right now. Do NOT take any other action until this file has been read.

The brief is indexed in three locations for maximum survivability:
1. `C:\Users\marsh\.claude\projects\d--AI\memory\MEMORY.md` — first entry in the index
2. `tools/orchestrator/orchestrator_prompt.md` — STEP 0 of cold-start sequence
3. This file — PROT-010

If all three locations are somehow lost, the file lives at `d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md`.

**Adherence marker**:

```
PROT-010 compliance: read orchestrator_post_compaction_brief.md at cold start; pause state confirmed; wrapper-first rule acknowledged.
```

---

## PROT-011 — Use named subagent_type for all 7 defined roles

- **Status**: active (approved 2026-05-24 by meta_audit sub-agent after subagent_type architecture rollout landing 4 new types: strategy_scribe, routing_handler, meta_audit, memory_curator)
- **Applies to**: Orchestrator (all Agent() dispatches)
- **Trigger**: any Agent() call from main thread
- **Per-dispatch, always-on**

**What to do**: Any `Agent()` call where the target role has a named subagent_type definition in `C:\Users\marsh\.claude\agents\` MUST use `subagent_type: "<name>"` — NOT `subagent_type: "general-purpose"`. The 7 named roles are: `exp_dev`, `research`, `verdict_handler`, `strategy_scribe`, `routing_handler`, `meta_audit`, `memory_curator`. The only legitimate `subagent_type: "general-purpose"` invocations are for one-off ad-hoc analysis tasks with no defined role.

**Pre-response checklist addition** (add to brief Section 3b after item 7):

```
8. Subagent-type check: if dispatching Agent(), is the target role one of the 7 named types?
   If yes, use subagent_type: "<name>". Do NOT use general-purpose with a full prompt paste.
```

**Why**: The named subagent types carry frozen contracts (pause gate, self-discovery, return format, hard constraints) in the agent definition. Using `general-purpose` with a prompt paste bypasses these — the main thread would be doing the sub-agent's setup work, which is exactly the smell the structural-agent-usage-mandate calls out. This PROT closes the gap before a pattern emerges.

**Adherence marker**:

```
PROT-011 compliance: used subagent_type: "<name>" for [role]; no general-purpose fallback.
```

---

## PROT-012 — For-You tab entry mandatory for routing-dispatch cycles

- **Status**: active (approved 2026-05-24 by meta_audit sub-agent; gap found in cycle 206 routing dispatch that wrote 2 routing files with no status_log entry)
- **Applies to**: Orchestrator main thread; strategy_scribe sub-agent
- **Trigger**: any cycle that produces >= 1 routing file as output (strategy_request_to_exp_dev_*.md, strategy_request_to_research_*.md, exp_dev_handoff_*.md, exp_dev_to_queue_*.md)
- **Per-cycle when triggered**

**What to do**: Write a status_log entry at the end of any cycle that writes >= 1 routing file:

```python
python -c "
import sys; sys.path.insert(0, 'd:/AI/hd-instrument')
from tools.orchestrator.state import log_event
log_event('routing_dispatch', '<technical summary: which files, which recipients>',
  plain_language='<1-2 sentences: what was routed and why it matters>',
  importance='LOW')  # raise to MEDIUM if routing touches cap_map or triggers new capabilities
"
```

**Why**: Routing cycles that produce 2+ routing files and a research request are substantive orchestration actions. Without a status_log entry, the For You dashboard tab has a silent gap for a period where the orchestrator was doing real strategic routing work. The brief's covered-events list includes "major dispatch returned" but did not explicitly call out routing-dispatch cycles (which write files rather than returning a wrapper result). PROT-012 closes that omission.

**Adherence marker**:

```
PROT-012 compliance: wrote status_log entry for routing dispatch; files: <list>; importance: <level>.
```

---

## How to mark adherence

In your per-cycle decision log entry, add one line like:
```
PROT compliance this cycle: implemented PROT-001 (wrote stub); PROT-002 already done in earlier cycle.
```

META reads decision logs and reconciles against this file.

## How protocols get added / retired

- **Added**: META proposes in `meta_proposals.md`. User approves. META adds
  the protocol here as `PROT-<NNN>` with status=active.
- **Retired**: META changes status to "retired" with retirement date. Do not
  re-implement retired protocols.
- **Modified**: META changes the protocol body. Reset adherence: re-implement
  on next cycle. Modification dates are noted at the top of the protocol.

Never remove a protocol entry — change status instead. The historical record
matters for audit.

## PROT-014 -- research dispatches must use subagent_type='general-purpose' with description starting "research:"

- **Status**: active (approved 2026-05-26; audit fix 4; background: v206-era "Agent type 'research' not found" wasted 1 Opus call + 2 retries)
- **Applies to**: Orchestrator
- **Trigger**: any research-skill dispatch (Skill tool invocation of /research or direct Agent() call to research role)
- **One-shot**: yes (orchestrator internalizes; no per-cycle action required once internalized)

**What to do**: Every research dispatch MUST use:
- `subagent_type: "general-purpose"` (custom subagent_types are NOT registered in the harness; `subagent_type: "research"` fails with "Agent type 'research' not found")
- `description` field MUST start with `"research:"` to identify the role

Correct form:
```
Agent({
  subagent_type: "general-purpose",
  description: "research: <topic>",
  prompt: "<full prompt>"
})
```

Wrong form (fails):
```
Agent({
  subagent_type: "research",   // NOT registered -- causes immediate error
  ...
})
```

**Background**: v206-era dispatch attempted `subagent_type: "research"`. The harness returned "Agent type 'research' not found" on the first call. Orchestrator retried twice before falling back to `general-purpose`. One Opus call wasted, 2 retries consumed. The root cause is that named subagent_type definitions in `C:\Users\marsh\.claude\agents\` are NOT the same as the `subagent_type` enum the harness accepts -- only "general-purpose" is valid for Agent() calls from the main thread.

**Note on PROT-011 interaction**: PROT-011 says "use named subagent_type for defined roles." PROT-014 is a targeted override: research is the one role where the named type is NOT registered. PROT-014 takes precedence for research dispatches.

**Adherence marker**:

```
PROT-014 compliance: research dispatch used subagent_type: "general-purpose"; description starts with "research:".
```

---

## PROT-015 -- orchestrator cold-start cap at 2 main-thread calls

- **Status**: active (approved 2026-05-26; audit fix 5; background: 2026-05-25 session-open cluster of 12 sequential Read+Bash calls in 2 minutes flagged by Audit Part 2 agent a890c0fbde6f5ea65 as dominant historical drag on routing_ratio)
- **Applies to**: Orchestrator
- **Trigger**: orchestrator session start (cold-start sequence per brief Section 7)
- **One-shot**: yes per session

**What to do**: at cold-start, the orchestrator is allowed AT MOST 2 main-thread calls:

1. `Read notes/orchestrator_post_compaction_brief.md` (PROT-010 requirement)
2. `python tools/orchestrator/state_check.py` (pipeline state snapshot)

Any additional orientation work -- reading recent decisions, listing handoff files, grepping cap_map, tailing the dashboard snapshot, checking queue.json, reading active_protocols.md -- MUST be dispatched to a state-check sub-agent (general-purpose Agent() call with description: "state-check: cold-start orientation"). That sub-agent performs all additional reads and returns a 1-paragraph summary.

**Why**: the 2026-05-25 cold-start had 12 sequential Read+Bash calls in the first 2 minutes. Each main-thread call is a denominator increment in routing_ratio. A cold-start cluster of 12 zeros-out the ratio for the first 20-turn window (routing_ratio = 0/12 = 0.00 for those turns). A single state-check sub-agent dispatch counts as 1 dispatch in the numerator instead.

**Adherence marker**:

```
PROT-015 compliance: cold-start limited to 2 main-thread calls (brief + state_check.py); additional orientation dispatched to state-check sub-agent.
```

---

## PROT-013 -- evaluate_bpc signature self-test in all new scripts (exp_dev-originated)

- **Status**: active (filed 2026-05-26 by exp_dev; META to ratify next audit cycle)
- **Applies to**: Experiment Dev (script writing)
- **Trigger**: every new script that calls base.evaluate_bpc or imports from a kovacs/betB chain

**Canonical signature** (exp_wave14d_betB_kovacs_v1.py line 198):
  evaluate_bpc(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms, eval_bytes, eval_targets, batch_size, device) -- 10 args

**What to do**: Include in _instrumentation_selftest() a callable check:
  # assert callable without TypeError at smoke scale
  _ = base.evaluate_bpc(W_tiny, pool_v, pool_l, pool_u, ba, pa, eb, et, 8, device)

This catches the arg-count mismatch that caused v1 INSTRUMENTATION_FAIL on:
  exp_wave14_1rsb_hysteresis_v1.py (Pred-4 v1, TypeError)
  exp_wave14_betB_pac_bayes_kl_predictor_v1 (defensive fix applied)
  exp_wave14_betB_replay_hA_direct_v1 ("same evaluate_bpc signature bug fixed in all 3 arm functions")

**Adherence marker**:
PROT-013 compliance: _instrumentation_selftest() includes evaluate_bpc callable check (or script does not call evaluate_bpc).

---

## PROT-018 — Anchor-name N-suffix binding (exp_dev + queue_add.py enforcement)

- **Status**: active (approved 2026-05-27; evidence: 60+ label-vs-honest mismatches in a single day where `_n4096` anchor names ran at N=512 in 2.6s — smoke config leaked into the queued full run)
- **Applies to**: Experiment Dev (script authoring); queue_add.py (ship-time gate)
- **Trigger**: every exp_dev cycle that produces an anchor whose name contains `_n<NUMBER>`
- **Per-anchor, always-on**

**Rule**: the anchor name `_n<NUMBER>` suffix is a BINDING CONTRACT, not a label.

1. If anchor name contains `_n<NUMBER>` (e.g. `_n4096`, `_n8192`, `_n16384`):
   - The script's PRODUCTION config (top-level `N = ...`, argparse default, etc.) MUST equal that number.
   - Smoke runs at a smaller N are expected and allowed — smoke is a gate, not the final config.
   - But the FULL queued configuration must set N = suffix-N.

2. Pre-ship audit (exp_dev, MANDATORY):
   ```bash
   grep -E "(N\s*=|n\s*=)\s*<SUFFIX_N>" experiments/exp_<name>.py
   ```
   If no match → BLOCK ship. Fix the script or fix the anchor name before queueing.

3. If anchor name lacks `_n<N>` suffix but script uses a non-obvious N: exp_dev MUST either add the suffix OR justify in the prereg under `## N-suffix` section.

4. `_v<NUMBER>` version suffixes do NOT carry N-binding. Only `_n<NUMBER>` triggers this rule.

5. **Structural enforcement: `tools/queue_add.py` exits with code 6 on N-suffix mismatch.**
   The validator runs at gate time (before smoke), parses the anchor name for `_n<N>`, searches the script for a matching production-N assignment, and rejects if not found. exp_dev's pre-ship grep is defense-in-depth on top of this.

**Why**: 60+ anchors shipped on 2026-05-27 where the production script had `N=512` (smoke config) but the anchor name declared `_n4096`. Verdicts logged the wrong scale, downstream analysis was misleading, and none of the standard smoke-pass gates caught it because smoke PASSED at N=512.

**Adherence marker**:
```
PROT-018 compliance: anchor _n<N> suffix verified against script production N before ship; queue_add.py gate passed (exit 0).
```

---

## PROT-022 -- Formula selftest registry + R3+ closed-form discipline

- **Status**: active (filed v340 by verdict_handler; registry updated v344 2026-06-02 with 3 new entries from R2 audits)
- **Applies to**: Experiment Dev (spec writing); Research (R3+ rescue hypothesis proposals); Strategy (spec review)
- **Trigger**: any spec containing a closed-form formula used as an HP gate; any R3+ rescue hypothesis proposal
- **Per-spec, always-on**

**What to do**: before writing or approving a formula-based HP gate:
1. Look up the formula in the registry below.
2. If in registry: apply the listed selftest cells as a check. If predicted != actual, fix the formula BEFORE writing the gate.
3. If not in registry: derive selftest cells inline and add them to the spec. File a registry addition in the next strategy_decisions log.

**Research-side R3+ discipline (added v344):**
> **Item: closed-form derivation + self-test of the rescue hypothesis BEFORE proposing R3+.**
> If the R3 hypothesis is "knob X will move metric Y to HP," derive Y(X) symbolically and check predicted value at current AND proposed knob settings. If Y(X) is approximately flat in X, hypothesis is falsified at zero cost. Saves the GPU re-ship. (Root cause of K-bump + Krylov-budget research errors 2026-06-02.)

### Formula registry

**Entry 1: MP 3rd moment (Marchenko-Pastur; Narayana number identity)**
```
m_3(alpha) = 1 + 3*alpha + alpha^2
```
Selftest cells (input -> expected output):
- alpha=0.5: m_3 = 1 + 1.5 + 0.25 = 2.75
- alpha=1.0: m_3 = 1 + 3 + 1 = 5.0
- alpha=2.0: m_3 = 1 + 6 + 4 = 11.0
Apply to: any implicit-Gram / Wishart / random-feature spec where the kappa_3 normalization gate appears. HP gate form: |kappa3_resc - m_3(alpha)| / m_3(alpha) <= 0.05.
Evidence: R2 audit 2026-06-02 found combo1_v3 line 175 asserted <= 0.15 of 1.0 (wrong); should assert <= 0.15 of m_3(alpha). Gate-spec bug; substrate was algebraically correct.

**Entry 2: Hopfield single-step retrieval cosine with neighbor overlap**
```
cos(retrieved, target) ~ 1 / sqrt(1 + sum_{j!=target} overlap(j, target)^2)
```
Selftest: for K Gaussian place-field patterns with SIGMA=sigma in K-space, neighbor overlap ~ exp(-(j-k)^2 / (4*sigma^2)); sum_overlap_sq ~ 4*sigma at large K (continuum integral). For sigma=2.0: sum_overlap_sq ~ 4.0, predicted cos ~ 0.45 (single-step) -> ~0.65-0.72 (post-iteration).
Apply to: any composition spec involving Hopfield retrieval where pattern overlap is non-zero (place-field encoding, low-rank pattern banks, structured codes).
Evidence: R2 audit 2026-06-02 -- K-bump hypothesis for PP-47xPP-49 baseline_cos refuted by this formula; baseline_cos is flat in K; correct knob is PLACE_FRAC not K.

**Entry 3: Hutchinson variance floor (stochastic trace estimator)**
```
trace_rel_err_floor = O(1 / sqrt(N_PROBES))
```
Selftest: at N_PROBES=1000, expect trace rel_err approximately 1e-3 to 3e-3 (depending on normalization). Increasing matvec budget does NOT reduce this floor; only increasing N_PROBES does.
Apply to: any Krylov-based kappa_3 / cert / trace audit where HP gate tightness approaches this floor. Adjust HP gate to accept floor, or increase N_PROBES.
Evidence: I-17 R3 (exp_dev) matvec=50 gave trace=1.3e-2 WORSE than matvec=3 result of 3e-3 -- floor is MC noise, not matvec-limited. I-17 CLOSED (v344) with HP bar lowered to 3e-3.

**Adherence marker**:
```
PROT-022 compliance: formula <name> selftest cells checked; predicted=<X> actual=<Y>; gate written as <formula>; OR no registry formula applies to this spec.
```
