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
