# **SEVEN LIVE ORGANS WERE READING AS "NOT ON THE PIPELINE" BECAUSE THE REGISTRY WAS STALE BY EXACTLY ONE TOOL FIX. RE-RUNNING THE AUDIT FLIPPED ALL SEVEN.**

**Found by noticing that ONE row's `provenance` field contradicted its own `pipeline_status` field.**

> # 🔻 **THIS NOTE'S TITLE AND SECTION 3 ARE WRONG. CORRECTED THE SAME NIGHT BY A RETRODICTION I RAN ON MY OWN FIX.**
> **I wrote that the registry was stale because the audit "was simply not re-run" after its
> 09:49 fix. THEN I BUILT A DETECTOR FOR THAT AND ASKED WHETHER IT WOULD HAVE FIRED ON THE REAL
> PRIOR STATE. IT WOULD NOT -- and that is how I found the story was wrong.**
>
> **THE AUDIT *DID* RUN AFTER THE FIX, TWICE, AND COMPUTED THE CORRECT ANSWER BOTH TIMES:**
>
> | report | local time | computed |
> |---|---|---|
> | `...T092428Z` | 05:24 | 48 used / 101 not-reachable *(pre-fix)* |
> | `...T140051Z` | **10:00** | **55 / 94 -- CORRECT** |
> | `...T140353Z` | **10:03** | **55 / 94 -- CORRECT** |
>
> ***So the right answer was computed at 10:00 this morning and the ROWS still carried the 05:24
> values eleven hours later.*** **THE RESULTS WERE NOT MISSING. THEY WERE LOST.**
>
> **THE MECHANISM IS NAMED IN THE AUDIT'S OWN COMMENT (`capability_registry_audit.py:1495`): it is
> a read-modify-write writer of this file, *"the same class of race that caused the reported
> lost-update bug for one-off registration scripts."*** *Two such registration commits landed at
> 09:43 and 11:53 local, and both left rows with a hand-written `integration_status: None` that no
> audit would ever produce.* **A script that loaded the registry before the audit wrote it and saved
> afterwards silently discards the audit's work while its REPORT survives on disk.**
>
> ➡️ **SO "THE REPORT EXISTS" IS NOT EVIDENCE THE ROWS WERE UPDATED** -- and my tool-mtime detector
> is blind to this case, because the tool never moved. **A second detector was added for the real
> failure: the ROWS being older than the REPORT.** *Sections 1, 2, 4 and 5 below stand as written.*

---

## 1. THE CONTRADICTION THAT STARTED IT

*`definitional_extraction_surface_patterns`, the row for the organ tonight's top item is about:*

| field | value |
|---|---|
| `pipeline_status` | `WIRED_BUT_NOT_PIPELINE_REACHABLE` |
| `provenance` | *"pipeline_status **corrected from** WIRED_BUT_NOT_PIPELINE_REACHABLE on RUNTIME evidence -- 212 of 402 provenance rows... carry `meaning_source=DEFINITIONAL_EXTRACTION`"* |

**The correction was WRITTEN DOWN and NEVER APPLIED TO THE FIELD.** *Enumerated across all 210 rows,
this was the ONLY row where provenance claims a `pipeline_status` correction -- so it was one
instance, not a pattern.*

## 2. THE CAUSE IS NOT A BAD HAND-EDIT -- **THE AUDIT RECOMPUTES THIS FIELD ON EVERY RUN**

*`capability_registry_audit.py:1494` says so in its own comment: it rewrites
`integration_status` / `used_by` / `last_audit_utc` / `pipeline_status` **on every row**.*

> ### **SO A HAND-CORRECTION TO `pipeline_status` CANNOT SURVIVE. The next audit overwrites it from the computed closure, whatever runtime evidence motivated it.**

## 3. ~~AND THE COMPUTED CLOSURE WAS RIGHT ALL ALONG -- THE REGISTRY WAS SIMPLY NOT RE-RUN~~
### 🔻 **THIS SECTION IS THE WRONG EXPLANATION -- SEE THE CORRECTION BLOCK AT THE TOP. IT WAS RE-RUN AT 10:00 AND 10:03 AND ITS RESULTS WERE LOST BY A CONCURRENT WRITER.** *The closure being right IS true; "not re-run" is not.*

| | |
|---|---|
| audit tool FIXED at | **2026-08-21 09:49 local** -- *"the registry audit was not rooted at the assembled substrate"* |
| registry's `last_audit_utc` | **2026-08-21T09:15:02Z = 05:15 local** |

***The registry was last audited FOUR HOURS BEFORE the fix that changed the answer.*** *Measured
directly: with the corrected entry points, `hdlab/definitional_extraction.py` **is** in the closure.*

## 4. WHAT RE-RUNNING IT CHANGED -- **7 ORGANS**

| organ | was | now |
|---|---|---|
| `definitional_extraction_surface_patterns` | NOT_PIPELINE_REACHABLE | **AND_PIPELINE_USED** |
| `substrate_assembled_reader_v1` | " | **"** |
| `information_foraging_mvt_leave_rule` | " | **"** |
| `corpus_registry_enumerable_shelf` | " | **"** |
| `sensorimotor_spoke_organ_b5` | " | **"** |
| `cortical_recall_organs_q1_q3` | " | **"** |
| `foundation_persistence_roundtrip` | " | **"** |

*Plus two rows hand-registered earlier today with no `integration_status` at all, now computed
(`cold_placement_new_word_to_frontier`, `stated_entity_fate_reading_extractor_highprecision`).*
**Totals now: `WIRED_AND_PIPELINE_USED` 55, `WIRED_BUT_NOT_PIPELINE_REACHABLE` 94.**

## 5. ⚠️ **AND THE LIMIT ON WHAT THAT FLIP MEANS, WHICH I AM NOT GOING TO OVERSTATE**

***`WIRED_AND_PIPELINE_USED` here means IMPORT-REACHABLE FROM THE ASSEMBLED READER. It does NOT mean
the organ was EXERCISED.*** **Of the seven, exactly ONE carries independent runtime evidence that it
actually fires** -- `definitional_extraction`, via 212 of 402 provenance rows labelled
`meaning_source=DEFINITIONAL_EXTRACTION`, which a fact cannot carry unless the gate ran.

> ### **THE OTHER SIX ARE REACHABILITY, NOT EVIDENCE OF USE. Upgrading them in my own head to "these six are working" would be exactly the move this whole night has been about.**

## TLDR

I noticed one row of our capability list disagreed with itself: its notes said the "is this actually
in use" flag had been corrected, and the flag still held the old value.

**The cause was not a sloppy edit.** That flag is recomputed automatically every time the audit runs,
so correcting it by hand can never stick -- **the next run overwrites it.**

**I first thought the checker had simply not been re-run since it was repaired this morning. That was
wrong, and I only found out because I built a detector for it and then asked whether it would have
caught the real case. It would not have.**

**The checker DID run after the repair — twice, at 10:00 and 10:03 — and got the right answer both
times.** The list still showed this morning's stale values eleven hours later. **The results were not
missing, they were thrown away**: something else edited the same file at the same time, and whichever
save landed last won. The checker's own notes warn about exactly this. **So the fact that a check
produced a report is no evidence that anything was actually updated.**

**Re-running it moved seven organs from "not on the live path" to "on it"** -- including the
definition reader, the assembled reader itself, and the parts that choose what to read next.

**One caution I want to be clear about.** "On the live path" here means the code can be reached from
the reader, **not that it ran and did something useful.** Only one of the seven has separate evidence
that it genuinely fired. **Treating the other six as working would be the exact mistake I have spent
tonight correcting.**

## QUESTIONS

None.

## NEXT STEPS

1. ~~Re-run the audit after any change to its entry points~~ **SUPERSEDED BY THE CORRECTION: that
   was the wrong lesson. The real one is that a CONCURRENT WRITER can discard the audit's results
   while leaving its report behind, so BOTH checks are now in `session_start_hook.registry_report()`
   -- tool-newer-than-report, AND rows-older-than-report (1h tolerance, because the audit stamps
   rows at START and names its report at FINISH, an 8m24s gap on a healthy run).**
2. *Do not hand-edit `pipeline_status`. It is recomputed; write the evidence into `provenance` and
   fix the closure instead.*
3. *Method note: **the tell was a row contradicting itself.** Nothing external flagged it -- putting
   two of its own fields side by side did, which is the habit that has paid out most this session.*
