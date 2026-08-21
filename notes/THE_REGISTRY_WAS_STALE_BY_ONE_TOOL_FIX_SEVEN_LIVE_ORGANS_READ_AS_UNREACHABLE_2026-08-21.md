# **SEVEN LIVE ORGANS WERE READING AS "NOT ON THE PIPELINE" BECAUSE THE REGISTRY WAS STALE BY EXACTLY ONE TOOL FIX. RE-RUNNING THE AUDIT FLIPPED ALL SEVEN.**

**Found by noticing that ONE row's `provenance` field contradicted its own `pipeline_status` field.**

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

## 3. AND THE COMPUTED CLOSURE WAS RIGHT ALL ALONG -- **THE REGISTRY WAS SIMPLY NOT RE-RUN**

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

The deeper reason was simpler still: **the audit tool was fixed this morning to start from the real
reader, and the list had last been checked four hours before that fix.** So it was stale by exactly
one repair.

**Re-running it moved seven organs from "not on the live path" to "on it"** -- including the
definition reader, the assembled reader itself, and the parts that choose what to read next.

**One caution I want to be clear about.** "On the live path" here means the code can be reached from
the reader, **not that it ran and did something useful.** Only one of the seven has separate evidence
that it genuinely fired. **Treating the other six as working would be the exact mistake I have spent
tonight correcting.**

## QUESTIONS

None.

## NEXT STEPS

1. **Re-run the audit after any change to its entry points** -- the stored rows are a CACHE of a
   computation, and a fix to the computation does not update them.
2. *Do not hand-edit `pipeline_status`. It is recomputed; write the evidence into `provenance` and
   fix the closure instead.*
3. *Method note: **the tell was a row contradicting itself.** Nothing external flagged it -- putting
   two of its own fields side by side did, which is the habit that has paid out most this session.*
