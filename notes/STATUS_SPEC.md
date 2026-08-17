# STATUS_SPEC -- the required structure and trim rules for `notes/STATUS.md`

Authority: this file governs `notes/STATUS.md`. Written 2026-08-13 after an ad-hoc byte-shave
deleted a standing discipline that had cost two full experiments to learn (detail in sec 8).
`STATUS.md` must link to this file in its header so no rewriter can plead ignorance.

This spec is itself uncapped and is NOT rewritten each session. Amend it deliberately.

---

## 1. The file's job, in one sentence

**A cold session that has read only `STATUS.md` must be able to pick the next action and must
not be able to repeat any work that has already been paid for.**

Both halves are load-bearing. "Pick the next action" is the obvious half and is what byte-shaves
optimise for. "Must not repeat paid-for work" is the half that gets silently sacrificed, because
its failure mode is invisible at write time and expensive months later.

Corollary that decides every trim argument:

> **A fact is cheap and a lesson is expensive.** Counts, paths, row totals, pass/fail tallies
> and commit hashes can be recomputed from disk by a script in seconds. A refuted hypothesis, a
> do-not-redo entry, or a discipline learned from a failed experiment cannot be recomputed at
> all -- it can only be re-learned by paying for the failure again. A byte cap that treats these
> as interchangeable will always evict the expensive one, because the expensive one is the one
> that reads as "unsourced prose".

---

## 2. Two files, and what lives in each

STATUS is **two files** as of 2026-08-13 (see sec 7 for why, and for the measurement that forced
it):

- **`notes/STATUS.md`** -- hard-capped, rewritten in place every session. Holds STATE: where the
  project is, what to do next, what is running, what is dangerous. Plus a **stub line naming
  every never-trim entry**.
- **`notes/STATUS_LESSONS.md`** -- **uncapped**, append-mostly, NOT rewritten. Holds the
  never-trim material in full: eliminated routes with their numbers, refuted hypotheses, revival
  criteria, and disciplines bought with failed experiments, each with its citation.

The split is not a filing convenience. It is the structural fix: the never-trim class grows
monotonically (a lesson is never un-learned) and so will breach any fixed cap eventually, while
the state class is naturally bounded (it is rewritten, not accumulated). Putting them in one
budget guarantees that the growing class eventually evicts something, and sec 8 is the record of
what that costs. Separate files, separate growth laws.

**Contract between them.** Nothing may appear in `STATUS_LESSONS.md` that is not stubbed by name
in `STATUS.md`. A cold session must be able to see that a route is closed from `STATUS.md`
alone; only the reasoning and the evidence require the second read.

### Required sections of `STATUS.md`, in order, with byte budgets

Order is for the reader (position -> what to do -> why -> what not to do -> hazards). Budgets
are ceilings, not targets; unused budget rolls forward to later sections.

| # | Section | Purpose -- what a cold session gets from it | Budget (B) |
|---|---|---|---|
| 1 | `# STATUS` + header block | Date, branch, HEAD, origin delta, links to this spec and to `STATUS_LESSONS.md`, the rewrite-in-place + follow-the-pointer rules | 450 |
| 2 | `## POSITION` | One paragraph. The single true statement about where the project stands, and whether growth is paused | 450 |
| 3 | `## TOP ITEM` | The one thing to work on next, with the evidence that makes it the top item | 900 |
| 4 | PATH STATE -- one `##` subsection per live workstream | Per-workstream: what is measured, what it licenses, where the evidence is | 3100 |
| 5 | `## DO NOT REDO` **(NEVER-TRIM)** | A stub naming **every** closed route, plus the link to `STATUS_LESSONS.md` | 1000 |
| 6 | `## STANDING DISCIPLINES` **(NEVER-TRIM)** | Each rule bought with a failure, in enough form to act on, plus the link to full text | 1400 |
| 7 | `## WHAT IS RUNNING / BLOCKED` | Live processes not to disturb, files another agent owns, data-loss hazards, USER-authorization gates | 650 |

**Two literal strings are MACHINE-PARSED and must not be reworded.** `tools/session_start_hook.py`
injects a STATUS summary at every session start / clear / compact. `status_summary()` scans for a
line beginning `AS OF:` (line 112, colon required) and for a heading beginning
`## WHAT IS RUNNING` (line 117). Both were broken by the 2026-08-13 rewrite -- the header had
been reworded to `AS OF` without the colon and the section to `## RUNNING / BLOCKED`, so the hook
had been injecting `(no AS OF line found)` and `(no WHAT IS RUNNING section found)` into every
compaction recovery. Restored 2026-08-13 by conforming `STATUS.md` to the parser (no code
change). A silent degradation of the compaction entry point is exactly the failure class this
spec exists to catch, so: **if either string is reworded, `tools/session_start_hook.py` must be
updated in the same change.**

**A SECOND READER JOINED 2026-08-15: `tools/board.py`.** It mirrors this file into the `## STATUS`
section of `notes/BOARD.md` (the owner-facing async decision board) and parses **four** literals:
`AS OF:` (colon required), `## POSITION`, `## TOP ITEM`, and `## WHAT IS RUNNING`. The first and
last were already an API of `session_start_hook.py`; **`## POSITION` and `## TOP ITEM` are newly
machine-parsed and are now in the same do-not-reword class.** All four are matched by
*heading prefix*, so extending a heading is safe (`## TOP ITEM -- A FLAT BAG...` matches
`## TOP ITEM`) but renaming or dropping one is not. `board.py` FAILS LOUD on a missing literal --
it writes a `MISSING REQUIRED LITERAL` banner into the board rather than a quiet placeholder --
but the banner only helps if someone reads the board, so: **if any of the four is reworded, update
BOTH `tools/session_start_hook.py` and `tools/board.py` in the same change.** All four are covered
by `python tools/board.py self-test`.

Budget sum: **7950 B** against an **8704 B** cap (raised from 8192 2026-08-15, sec 7) -> 754 B of
slack. Sections 5 and 6 together
hold **2400 B** and are floors as well as ceilings: they may not be squeezed below their
content, only below their *wording*.

Section 4 carries the largest budget because it carries the most evidence pointers, and it is
simultaneously the **first thing to trim** (sec 3) because its content is the most re-derivable.
Large budget and low trim-priority are not a contradiction: it is big because pointers are
bulky, and it is cheap because pointers are recoverable.

A section may be empty (write `- none`), but no section may be **absent**. An absent section is
how a class of knowledge stops being tracked.

---

## 3. Trim priority order -- cut tier 1 to exhaustion before touching tier 2

Grounding principle: **evict what is cheaply RE-DERIVABLE FROM DISK before what is EXPENSIVE TO
RE-LEARN.** Test to apply, per candidate line: *"if this were deleted, what would it cost to get
back?"* A shell command = tier 1. A failed experiment = never.

1. **Recomputable numbers.** Row counts, corpus sizes, commits-ahead, `pytest` tallies, module
   inventories. Replace with the command or the note that produces them. `git rev-list --count`
   is free; a refutation is not.
2. **Recoverable paths and inventories.** Lists of module/file names that a `Glob` or the
   capability registry would return. Keep one representative pointer, drop the enumeration.
3. **Finished-work status.** "X landed at <hash>" -- `git log` has this. Keep the hash only when
   it is the citation for a *claim*, not when it is a progress report.
4. **Emphasis and connective prose.** Bold, superlatives, "tonight", "importantly", restated
   topic sentences. This is pure compression with zero information loss and it is usually where
   the needed 200 bytes are hiding. **Most over-cap situations should end here.**
5. **Superseded findings** whose successor is present and cites them.
6. **Worked examples inside a lesson** -- keep the rule and the citation, drop the illustration.
   Last resort; the example is often what makes the rule recognisable in a new situation.

**Never** (see sec 4). If tiers 1-6 do not free enough bytes, the file has outgrown the cap:
invoke the escalation in sec 7. Do not descend into the never-trim list.

---

## 4. NEVER-TRIM list

These are removable only when the *underlying claim itself* is retracted or superseded on disk
-- never for space, never for style, never for lacking a citation.

1. **Any DO-NOT-REDO entry.** Cost of loss = the whole experiment, re-run.
2. **Any standing discipline earned from a failure**, and the failure count that motivates it
   ("happened 2x", "4x in one night") -- the count is the argument.
3. **Any refuted hypothesis**, with the number that refuted it. A refutation deleted becomes an
   attractive-looking idea again within one session.
4. **Any SHELVED item's revival criterion.** Without it the shelving is either permanent by
   accident or reversed by whim.
5. **Any data-loss hazard** -- single-copy data, no-backup paths, files a concurrent agent owns.
6. **Any USER-authorization gate** (push, remote-persist, growth-unpause).
7. **Any claim whose loss would cause repeated work**, as judged by the trimmer. This is the
   catch-all and it is deliberately a judgement call; that is why sec 6 restricts who may trim.

---

## 5. The citation rule

> **A lesson without a citation gets a citation added. It is never deleted for lacking one.**

Missing provenance is a defect in the *record*, not evidence against the *claim*. The correct
response, in order:

1. Search disk for the note/metrics that produced the lesson; add the pointer.
2. If none exists, write one (a short note stating the observation and where it was seen) and
   cite that. **Manufacturing the evidence doc is the cheap half of the work; the lesson is the
   expensive half and it already exists.**
3. If neither is possible, keep the lesson and mark it `[uncited -- provenance lost]`. An
   uncited true lesson beats a deleted one.

Inverse rule, equally binding: **a citation is not a licence to keep the line.** A recomputable
count is tier-1 trimmable no matter how well cited.

---

## 6. Who may trim

**Only an agent whose assigned task is STATUS.md maintenance**, working explicitly to this spec,
with judgement-class capability (per `CLAUDE.md` "Choosing the model for a subagent": deciding
what a number means and adjudicating what may be lost is judgement work, not mechanical work).

**Forbidden: the incidental byte-shave.** An agent that came to ADD something and found the file
over cap is the single worst-positioned actor to decide what leaves, because its own addition is
the one line it will never consider cutting. That agent's permitted actions, in order:

1. Compress its OWN addition.
2. Evict from **tiers 1-4 only** (recomputable numbers, recoverable paths, finished-work status,
   emphasis prose).
3. If that is not enough: **STOP. Do not descend to tiers 5-6, do not touch sections 5-6 of the
   file. Report that STATUS.md is at cap and hand the trim to a maintenance pass.**

A trim that removes a NEVER-TRIM item is a defect regardless of the resulting byte count.

---

## 7. Was the 6144 B cap still right? -- NO. SPLIT, and set the cap at 8192

**Recommendation, in order of importance: (1) SPLIT the file, (2) set `STATUS.md`'s cap to
8192 B. Do not do (2) without (1).**

### Why split -- the cap was not the primary fault, but it was a real one

The 2026-08-13 loss was **not** caused by the cap. The file was rewritten to 5974 B -- 170 B
*under* cap -- and the discipline was deleted anyway, on the stated grounds that it carried no
file pointer. That is a **selection-rule** failure. Secs 3-5 fix it directly and would have
saved the entry at any cap.

But the cap was the standing pressure that made a selection necessary at all, every session,
forever, with lessons and facts drawn from one budget. Given that the never-trim class only
grows, that pressure has exactly one long-run outcome. The split removes the pressure from the
class that cannot absorb it.

### Why 8192, measured rather than guessed

Rebuilding `STATUS.md` to this spec on 2026-08-13 -- deleted discipline restored, the top-item
finding updated from "IN PROGRESS" to the traced answer, every pre-existing evidence pointer
preserved, never-trim reasoning already moved out to `STATUS_LESSONS.md`, and tiers 1-4 of sec 3
applied -- lands at **7363 B**. It does not fit in 6144, and the residue is not prose: roughly
850 B of the file is note filenames alone (17 pointers at ~50 B each), which are irreducible by
construction. Concretely, fitting 6144 would have required deleting evidence pointers, which is
the failure mode this spec exists to prevent.

8192 gives ~830 B (about 11%) of headroom for the next session's findings, and keeps the file
at roughly 100-130 lines -- still one cold read in one pass, which is the whole justification
for having a cap.

### Why raising the cap is safe NOW and was not safe BEFORE

Raising the cap without splitting would have been the wrong call, and this spec said so in its
first draft: it preserves the same failure (lessons and facts competing in one budget) while
weakening the readability constraint. After the split that objection no longer applies. The
remaining cap governs only the STATE half, where the trim order in sec 3 works cleanly because
the never-trim class is **absent from that budget entirely**. The cap now constrains only
material that is re-derivable from disk by construction.

### Escalation, pre-authorised so no future agent improvises under pressure

If a rewrite cannot fit within 8192 after applying tiers 1-4 honestly:

1. Move more never-trim reasoning to `STATUS_LESSONS.md` and leave a stub. This is free.
2. Retire PATH STATE subsections for workstreams that are closed, leaving the audit-note pointer.
3. Only then consider a further cap raise, and record the measurement that justified it here.

**Never** resolve an over-cap by deleting a never-trim entry (sec 4), and never let an agent that
merely needs room make the call (sec 6). Splitting costs one extra read. Trimming costs an
experiment.

### 2026-08-15: escalation step 3 invoked -- cap raised 8192 -> 8704

An agent whose task WAS `STATUS.md` maintenance (`hdi_testbed`, dispatched by the research
Director) proposed exactly this raise on 2026-08-14/15 and correctly DECLINED to enact it,
citing sec 6: the actor who merely needs room is the worst-positioned party to grant it. That
refusal is the mechanism working as designed -- it escalated instead of self-authorising.

The Director (one level up, not the party needing the room) granted it, with this reasoning
recorded here per the instruction that a raise be auditable: escalation steps 1 and 2 above were
already spent before the raise was requested -- tier-4 formatting and stale-count trims had
already been harvested by the proposing agent, and further squeezing would have meant cutting
evidence pointers or never-trim content, the exact failure this spec exists to prevent. The
proximate cause was two pieces of new content that could not be compressed into the existing
830 B of headroom: (a) STANDING DISCIPLINE 9/10 had been living as a 58 B placeholder stub --
barely a name-check -- for two disciplines each bought with a specific, costly failure (a
keyword detector misreading honest scope disclosure as overclaim, 49/49 false positives across
three atom-triage passes; and silent joins fabricating both false-green and false-red results);
the stub needed room to actually state the lesson, not merely gesture at it. (b) A HARD_FAIL
foundation-validation result (`exp_foundation_validation_harness_v2_floors_v1`, `62ecec9d5`,
correctness 0.9667 against a frequency floor of 0.96, CIs overlapping) needed recording in the
one file `notes/STATUS.md` that is guaranteed to be read after compaction -- it previously
existed only in fragments and metrics files.

512 B (8192 -> 8704) was chosen as the minimum that closes the measured gap: after applying
tiers 1-4 exhaustively to the new content itself (the added FOUNDATION VALIDATION section was
compressed from an initial 1224 B draft to 585 B by moving the full mechanism narrative to a new
`STATUS_LESSONS.md` entry and leaving a citation-bearing pointer, per escalation step 1) and
after modest tier-1/tier-4 trims elsewhere in the PATH STATE subsections (redundant recomputable
counts, one duplicated cross-reference, connective prose), the rewritten file lands at **8697 B**
-- under the new cap with 7 B to spare, and without touching any DO-NOT-REDO entry or
STANDING DISCIPLINE 1-8 (verified byte-for-byte unchanged) and without removing any evidence
pointer. Escalation step 2 (retiring a closed PATH STATE subsection to a bare pointer) was not
needed; the gap closed via steps 1 and legitimate tier 1-4 trims of the new material.

**The never-trim material stays never-trim.** This raise is not licence to relax eviction
discipline going forward -- it closes a real, measured, one-time gap between two genuinely new
never-trim-class entries and the room available to state them honestly.


### 2026-08-16: escalation step 3 MEASURED AND PROPOSED (NOT ENACTED) -- 8704 -> 9216

Written by the agent whose assigned task WAS `STATUS.md` maintenance (auditor pass, 2026-08-16),
following sec 6: the party that needs the room measures and proposes; it does not grant. Recorded
here per sec 7's requirement that any raise be auditable, and left OPEN for the Director.

**The measurement, section by section, after tiers 1-4 were applied exhaustively to the whole file
(not merely to the new content):**

| section | bytes | SPEC budget | over/under |
|---|---|---|---|
| header | ~480 | 450 | +30 |
| `## POSITION` | ~390 | 450 | -60 |
| `## TOP ITEM` | ~800 | 900 | -100 |
| PATH STATE (3 subsections) | ~2,540 | 3,100 | **-560** |
| `## DO NOT REDO` (+ CAVEATS + CORRECTIONS stubs) | 2,669 | 1,000 | **+1,669** |
| `## STANDING DISCIPLINES` | 1,867 | 1,400 | **+467** |
| `## WHAT IS RUNNING` | ~980 | 650 | +330 |
| **total** | **9,725** | 7,950 (+754 slack) | **+1,021 over the 8,704 cap** |

**The overage is entirely in the never-trim class, and every other section is already under its own
budget.** Sections 5 and 6 together hold 4,536 B against a 2,400 B allowance -- 89% over -- and they
are *pure stubs already*: 42 DO-NOT-REDO names, 6 caveat names, 31 correction names, 13 disciplines.
There is no reasoning left in them to move; sec 7 escalation step 1 was spent tonight (about 27 KB of
new reasoning was appended to `STATUS_LESSONS.md`, leaving only names behind), and step 2 was spent
too (the FOUNDATION VALIDATION and RECOVERY TRIAGE subsections were reduced to bare pointers).

**Why this was predictable and is not a failure of the rewrite.** Sec 2 states the growth law: the
never-trim class grows monotonically and will breach any fixed cap eventually. It breached 6,144 on
2026-08-13, 8,192 on 2026-08-15, and 8,704 tonight. Five never-trim entries were added on
2026-08-16 -- DO-NOT-REDO 38-42, corrections C28-C31, standing disciplines 11-13 -- each bought with
a measured result or a measured mistake:

- 38/39 are two MEASURED NULLS with brain-framed revival criteria (bridging with the thematic hub
  supplied; sparsifying the reading anchor). Losing either buys a repeat of the experiment.
- C28-C31 are four retractions, three of which are the SAME failure mode (a number carried between
  scorers or populations) and one of which is a tool defect that can hand out a FALSE PASS.
- Disciplines 11-13 are the rules those retractions bought. Sec 4 item 2 makes them unremovable, and
  sec 8 is the record of what happens when a discipline is evicted for space.

**What was NOT done, deliberately.** No DO-NOT-REDO entry, caveat, correction or discipline was
dropped or merged away; no evidence pointer was deleted; the four machine-parsed literals are
unchanged. The file is left OVER CAP with the overage disclosed in its own `## WHAT IS RUNNING`
section, because sec 3 is explicit that the correct response to "tiers 1-6 do not free enough bytes"
is to escalate, not to descend into the never-trim list.

**The proposal.** 9,216 B (+512, the same increment as the 2026-08-15 raise) closes the measured gap
with ~500 B of headroom. **It is NOT enacted here.** If the Director declines, the alternative that
does not destroy anything is a THIRD file -- an uncapped `STATUS_CLOSED.md` holding the DO-NOT-REDO
and CORRECTIONS stub indexes, with `STATUS.md` keeping only the disciplines plus a single pointer.
That trades one extra cold read for a permanently bounded `STATUS.md`, and it is the structurally
honest fix if the stub lists keep growing at the current rate (11 new never-trim entries in 72
hours).

### 2026-08-17: the 9216 B proposal is SUPERSEDED. RE-MEASURED, TWO OPTIONS, NEITHER ENACTED

Written by the agent whose assigned task WAS `STATUS.md` maintenance (audit pass, 2026-08-17),
following sec 6: the party that needs the room measures and proposes; it does not grant. **The
2026-08-16 proposal of 9216 B is now insufficient and should not be enacted as written.**

**The measurement, after tiers 1-4 were applied to the whole file (not only to the new content):**

| section | bytes | SPEC budget | over/under |
|---|---|---|---|
| header | 493 | 450 | +43 |
| `## POSITION` | 509 | 450 | +59 |
| `## TOP ITEM` | 805 | 900 | **-95** |
| PATH STATE (4 subsections) | 3,094 | 3,100 | **-6** |
| `## DO NOT REDO` (+ CAVEATS + CORRECTIONS stubs) | 3,109 | 1,000 | **+2,109** |
| `## STANDING DISCIPLINES` | 2,011 | 1,400 | **+611** |
| `## WHAT IS RUNNING` | 1,550 | 650 | **+900** |
| **total** | **11,571** (140 lines) | 7,950 (+754 slack) | **+2,867 over the 8,704 cap** |

**The overage is again almost entirely the never-trim class: sections 5 and 6 hold 5,120 B against a
2,400 B allowance and are PURE STUBS -- 43 DO-NOT-REDO names, 6 caveats, 34 corrections, 14
disciplines, with every line of reasoning already moved to `STATUS_LESSONS.md`.** Escalation step 1
was spent again on 2026-08-17 (about 14 KB of new reasoning appended to `STATUS_LESSONS.md`, leaving
only names behind). Four never-trim entries were added, each bought with a measured result or a
measured mistake: DO-NOT-REDO 43 (selectional-constraint bridging, a landed FULL null that is
CI-separated BELOW the incumbent it was built to beat) and CORRECTIONS C32-C34 plus STANDING
DISCIPLINE 14 (three retractions with one shared cause -- an underpowered null read as a capability
statement -- and the rule that closes it).

`## WHAT IS RUNNING` is 900 B over its budget and that is not prose bloat: it carries a data-loss
hazard, three USER-authorisation gates, a blocked path, two agents stopped mid-task, and a livelocked
index that makes a query tool return stale answers. Sec 4 items 5-6 make most of that never-trim too.

**TWO OPTIONS. THE DIRECTOR CHOOSES; NEITHER IS ENACTED HERE.**

1. **Raise the cap to 12,288 B** (+3,584, closing the measured gap with ~700 B of headroom). Honest
   about the growth law, but it is the third raise in five days and it weakens the one-cold-read
   justification the cap exists for.
2. **RECOMMENDED -- take the THIRD-FILE option this spec already named on 2026-08-16, and NO RAISE
   IS NEEDED.** Move the `## DO NOT REDO` stub index (with CAVEATS and CORRECTIONS) into an uncapped
   `notes/STATUS_CLOSED.md`, leaving a single pointer line in `STATUS.md`. Measured: 11,571 - 3,109 +
   ~120 for the pointer = **~8,580 B, UNDER the existing 8,704 cap**, with nothing deleted, nothing
   demoted and no evidence pointer lost. It costs one extra cold read and it bounds `STATUS.md`
   permanently, because the list that grows monotonically stops sharing a budget with the list that
   is rewritten. The same structural argument that justified splitting `STATUS_LESSONS.md` off in
   the first place applies here one level up.

**What was NOT done, deliberately.** No DO-NOT-REDO entry, caveat, correction or discipline was
dropped or merged. No evidence pointer was deleted. The four machine-parsed literals are unchanged
and `tools/session_start_hook.py --self-test` passes ALL, including its check that the real
`notes/STATUS.md` parses clean. The file is left OVER CAP with the overage disclosed in its own
`## WHAT IS RUNNING` section, because sec 3 says the correct response to "tiers 1-6 do not free
enough bytes" is to escalate, not to descend into the never-trim list.

---

## 8. The incident this spec exists to prevent (2026-08-13)

Deleted from `STATUS.md` in the rewrite between commit `19754614c` and the working tree:

> **3. DO NOT GATE A CELL ON A HAND-SCORED MEANINGFUL DELTA WHILE THE GENERATOR FLOORS AT 1-3%.**
> The comparator's max attainable |delta| was 0.02 against its own declared min-detectable 0.11.
> "Only CONTROL is floor-pinned" is a restatement of H1, not a power argument.

Purchase price: two complete experiments, both UNDERPOWERED BY FLOOR --
`exp_grounding_quality_readout_v1` (`notes/director_handscore_readout_v1_2026-08-13.md:31-44`,
3 MEANINGFUL rows in 100, max attainable |delta| 0.06 inside its own NULL band) and
`exp_structured_comparator_v1` (`notes/director_handscore_structured_comparator_2026-08-13.md:56-81`,
1 MEANINGFUL row, max |delta| 0.02, 5.5x below its own declared minimum detectable delta). The
second cell's prereg had explicitly claimed to have FIXED the first's defect. It recurred, worse.

Stated grounds for deletion: the entry carried no file/hash pointer. Every citation needed was
on disk at the time, in the two notes above. Under sec 5 the correct action was to add them.

Restored to `STATUS.md` on 2026-08-13 with both pointers attached.
