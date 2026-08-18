# ORGAN ACCOUNTING -- WHAT IS BUILT, WHAT WORKS, WHAT WE ARE NOT STANDING ON

**Owner, 2026-08-18: "we made a lot of effort to build fully functional organs and we should make
sure we're working off of that significant effort."**

That instruction corrected the Director's focus. A day had gone into auditing **CLAIMS** (30
experiment cells: 13 refuted, 4 suspended, 12 qualified, 1 upheld) and **the MACHINERY had never
been inventoried at all**. They are different assets: an experiment's claim can be refuted while
the organ it exercised is perfectly sound. **The claim base rate says nothing about what follows.**

## THE HEADLINE, AND IT IS GOOD NEWS

**163 modules swept by ISOLATED SUBPROCESS IMPORT under `.venv`. 163 IMPORT CLEANLY. ZERO
FAILURES.** The organ layer is not rotten, not bit-rotted, not broken. Whatever else is true, the
machinery runs.

## THE FINDING THAT MATTERS

**Live closure traced at RUNTIME** -- both entry points imported, `sys.modules` inspected. Not grep,
which is wrong in both directions here: three live modules are lazy imports inside function bodies
and invisible to it, while two grep "hits" are a string constant and a comment.

| | count |
|---|---|
| top-level organs in `hdlab/` | **147** |
| import cleanly (of 163 incl. subpackages) | **163 -- all of them** |
| **reached from a live entry point** | **31** |
| **NOT reached -- built, working, unused** | **116** |

**ROUGHLY 79% OF THE ORGAN LAYER IS NOT ON THE LIVE PATH.** The two entry points
(`reading_grounding_loop`, `grounding_acquisition_loop`) pull in 39 `hdlab.*` modules between them.

**The twenty largest unreached organs, by source size:**

| KB | module |
|---|---|
| 133.1 | `goal_achievement` |
| 109.8 | `definitional_extraction` |
| 61.6 | `goal_owner_select` |
| 61.2 | `situation_reader` |
| 55.2 | `_scratch_orig_goal_owner_select` |
| 54.2 | `concept_encoder` |
| 50.9 | `definitional_predicate_v61` |
| 50.8 | `reasoner` |
| 49.7 | `director_kb` |
| 47.4 | `goal_outcome_relation` |
| 43.1 | `atom_consultation` |
| 38.5 | `information_foraging` |
| 37.5 | `hippocampal_encoder` |
| 37.4 | `foundation_persistence` |
| 35.1 | `coref` |
| 34.3 | `cortex` |
| 33.3 | `goal_outcome_relation_grounded` |
| 32.0 | `prelim_tier` |
| 30.8 | `semantic_parser` |
| 30.7 | `director_kb_bio_sources` |

**`definitional_extraction` is the proof that unreached does not mean unusable.** It is 110 KB, it
is NOT on the live path, and it was used successfully THIS SESSION -- it extracted 228,133
definitions from 2.78 M lines of SimpleWiki in 426 s for the cross-view work. **Working machinery,
sitting off the path.**

## WHAT THIS ACCOUNTING DOES NOT YET SAY -- STATED SO NOBODY OVERREADS IT

1. **Self-tests have NOT been run.** ~82 modules carry one (`__main__` self-test; **NOT the 31 the
   Director first reported -- a too-narrow regex, and 81 independently matches
   `notes/system_accounting_2026-08-13.md`**). Until those run, "unreached" is not yet
   "GOOD_BUT_UNUSED" -- it is "imports cleanly and is unreached".
2. **The closure was traced from TWO entry points.** Others may exist. A module absent here may be
   reached by a path not traced. **Absence from this closure is not proof of disuse.**
3. **Some organs SHOULD be off the live path** -- tooling, experiment-only helpers, superseded
   versions. 116 is a CANDIDATE POOL, not a backlog.
4. **A constant wearing an organ's name reads as coverage and is worse than a missing organ.** The
   claim audit found a "grounding axis" whose valence took exactly three distinct values across all
   items and equalled a WordNet lookup exactly, and a "negation channel" bit-identical ON versus
   OFF. **The large unreached organs have NOT been probed for this.**

## HYGIENE

**`_scratch_orig_goal_owner_select` is 55 KB, lives in the durable organ directory, and is
REGISTERED as a capability.** A `_scratch_*` file has no business in `hdlab/` at all, let alone in
the registry. It also costs 103 s to import -- second slowest of all 163.

Slowest imports overall: `situation_reader` 172 s, `_scratch_orig_goal_owner_select` 103 s,
`definitional_extraction` 77 s, `closed_class_lexicon` 72 s, `animacy_lexicon` 69 s. (Parallel-
inflated; `import torch` alone measures 20 s under the same contention.) **Import cost is a real
tax on any pipeline that wires these in.**

## NEXT

1. **Run the ~82 self-tests.** That is what converts "unreached" into `GOOD_BUT_UNUSED` and gives
   the recoverable list its evidence.
2. **Probe the largest unreached organs for constant-valued behaviour** before proposing to wire
   any of them.
3. **Remove `_scratch_orig_goal_owner_select` from `hdlab/` and from the registry.**
4. Then, and only then, decide what to wire.

**Evidence on disk:** `scratch/organ_audit/import_results.json` (per-module import time and status),
`scratch/organ_audit/closure.json` (live closure and the 116), `scratch/organ_audit/modules.json`.
