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

---

## CONSTANT-BEHAVIOUR PROBE -- 13 LARGEST UNREACHED ORGANS, RUNTIME EVIDENCE

**10 FUNCTIONAL, 3 THIN, 0 CONSTANT_OR_PASSTHROUGH, 0 CANNOT_PROBE.**
**THE ORGAN LAYER IS IN GENUINELY BETTER SHAPE THAN THE CLAIMS LAYER, AND THE OWNER WAS RIGHT TO
INSIST WE LOOK.**

**Method validated on a known-good calibrator FIRST**, so a THIN verdict cannot be method bias:
`definitional_extraction` returned 9 distinct outputs over 12 inputs, all five pattern families
fired, and it disagreed with a naive "contains ' is '" heuristic on 3 of 12.

| organ | public entry | distinct out / in | verdict | evidence |
|---|---|---|---|---|
| `goal_achievement` | `goal_achievement_verdict` | 6/14 | FUNCTIONAL | all 4 channels fire; beats naive negation-word baseline on 4/14 |
| `definitional_extraction` | `extract_definitions` | 9/12 | FUNCTIONAL | 5/5 patterns; fires on 9.38% of 4,000 SimpleWiki lines |
| `goal_owner_select` | `select_outcome_owner` | 5/5 correct | FUNCTIONAL | one-variable goal-swap 5/5; **scramble control collapses to the foil** |
| `situation_reader` | `SituationReader.read` | 6/6 | FUNCTIONAL | coref_acc 0.042-0.835; xsent **0.5292 vs blind baseline 0.0000** |
| `concept_encoder` | `fit` / `encode_with_result` | 56 distinct confidences / 96 | FUNCTIONAL (documented scope) | same-cluster 1.0000 >= 0.40, cross -0.1755 / 0.0343 <= 0.10 |
| `definitional_predicate_v61` | `extract_predicates_v61` | 5/12 | **THIN** | **fires on 1 of 375 already-definitional sentences (0.27%)** |
| `reasoner` | `DerivationReasoner.reason` | 4 choices, 3 modes | **THIN** | derivation reaches 7/40 questions; **answer == similarity baseline on 38/40** |
| `goal_outcome_relation` | `relation_votes` | 4/12 | FUNCTIONAL (narrow) | both sources fire; 7/12 abstain; avoidance branch exercised |
| `atom_consultation` | `consult` | 3/12 | **THIN, DECISION-INERT** | 7-atom table; **`applied=False` hard-coded**; disabled by default in Cortex |
| `information_foraging` | `ForagingController` | 7/7 | FUNCTIONAL | identical patch: **rich env leave@3, poor env leave@8** (marginal-value behaviour) |
| `hippocampal_encoder` | `encode_and_write` / `retrieve` | 12/12 | FUNCTIONAL | **pattern completion cos 0.2000 -> 0.9173**; sparsity 0.0195 |
| `coref` | `CorefReader.resolve_stream` | 8/8 | FUNCTIONAL | cross 0.3610 vs single-sentence 0.2116; strategy changes 7/8 |
| `cortex` | `Cortex.forward` | 11/11 | FUNCTIONAL | monotone confidence 1.0 -> 0.0256; ACCEPT/CLARIFY/REFUSE at documented taus |

### WORTH WIRING -- each has a real can-fail discriminator its own mechanism passes

`hippocampal_encoder`, `cortex`, `information_foraging`, `coref`, `goal_owner_select`,
`situation_reader` (**budget 204.5 s import**), `definitional_extraction`.

### WOULD BE FALSE COVERAGE -- do NOT wire these as capabilities

- **`atom_consultation`** -- retrieval works (8/8 with explicit hints), but with params alone it
  returns `None` for 3 of 5 op-classes and the same `SHARDED` for every COMPOSITION query, and
  **`applied` is hard-coded `False`. IT CANNOT CHANGE A DECISION BY CONSTRUCTION.**
- **`definitional_predicate_v61`** -- 0.27% fire rate on its own intended population.
- **`goal_achievement`'s desiderative-negation channel** -- fires 7/7 on its own authored exemplars
  but **4/7 on minimal-edit paraphrases**, changing the verdict on 1 of 14 even at best. *This
  REFINES the claim audit's "bit-identical ON vs OFF" finding: the cause is the `channel=='majority'`
  gate plus surface-tuning, NOT a constant function.*

### THE AUDITOR CORRECTED ITSELF THREE TIMES, AND SAID SO

1. Its first `reasoner` probe read nonexistent keys and reported "1 distinct output / 24" -- **an
   artifact of its own code**, discarded; correct keys give 4 choices / 3 modes.
2. Its first `concept_encoder` probe masked the target across identical frames, **making the inputs
   literally identical** -- the collapse was the probe's corpus, not the organ.
3. `hippocampal_encoder.retrieve` equalling the raw DG code on CLEAN cues is **correct attractor
   fixed-point behaviour, not passthrough** -- the noisy-cue arm is the discriminator.

*Every one of those, uncaught, would have been a false negative against working machinery.*

**Probe scripts:** `scratch/organ_audit/probe_*.py`. Checked per the triple-check rule: right file
(HEAD `hdlab/`), right env (`.venv` throughout), right corpus (`data/corpora/simplewiki`,
`data/litbank/coref/conll`), right metric (source-verified keys), right arm (ablation flags toggled
one at a time).

---

## SELF-TEST SWEEP -- LANDED. AND THE RECOVERABLE LIST IS 67 ORGANS.

**87 modules carry a self-test entry point** -- another upward correction (the Director first said
31, then ~82; the measured figure is **87**). Each run as `python -m hdlab.<mod>` in an ISOLATED
subprocess, 240 s timeout, exit code as the primary signal and printed text only as secondary.

| | count |
|---|---|
| swept | **87** (742 s) |
| **exit 0** | **83** |
| exit 0 AND printing an explicit pass marker | **78** |
| not clean | **4** |

**THE FOUR THAT ARE NOT CLEAN, and only one is a real failure:**
- **`goal_achievement` -- rc=1, a GENUINE FAILING ASSERTION:**
  `AssertionError: channel 'relation:recur' != 'majority' for 'I met up with my friend.'`
  **This is the SAME organ whose desiderative-negation channel the constant-probe flagged (7/7 on
  authored exemplars, 4/7 on minimal-edit paraphrases). Two independent methods converged on the
  same component.** That convergence is the finding, not either result alone.
- `concept_encoder`, `reasoner`, `situation_reader` -- **TIMEOUT at 240 s, which is a BUDGET
  result, not a breakage result.** `situation_reader` alone costs 204.5 s just to import. **Do not
  read these as failures**; re-run them with a longer ceiling before any judgement.

## *** THE ANSWER TO THE OWNER'S QUESTION: 67 ORGANS ARE BUILT, SELF-TEST-PASSING, AND UNWIRED ***

**`GOOD_BUT_UNUSED` = self-test exits 0 AND absent from the live closure = 67 modules.**
(Of the 116 unreached, 71 have a self-test at all; 67 of those pass.)
**Only 16 organs are BOTH live AND self-test-passing.**

**The largest recoverable, by source size:** `definitional_extraction` (110 KB),
`goal_owner_select` (62 KB), `definitional_predicate_v61` (51 KB), `goal_outcome_relation` (47 KB),
`atom_consultation` (43 KB), `information_foraging` (39 KB), `hippocampal_encoder` (38 KB),
`foundation_persistence` (37 KB), `cortex` (34 KB), `goal_outcome_relation_grounded` (33 KB),
`prelim_tier` (32 KB), `semantic_parser` (31 KB), `context_retention` (31 KB),
`result_type_induction` (30 KB), `script_grain_acquisition_loop` (29 KB), `action_selection` (29 KB).

**CROSS THE TWO AUDITS BEFORE WIRING ANYTHING.** A passing self-test is NOT sufficient -- the
constant-probe found `atom_consultation` self-test-passing AND decision-inert (`applied` hard-coded
`False`), and `definitional_predicate_v61` self-test-passing AND firing on 0.27% of its intended
population. **BOTH APPEAR IN THE 67.** The wire list is the INTERSECTION of self-test-passing and
probe-FUNCTIONAL, not either alone.

**WIRE LIST, both audits agreeing:** `hippocampal_encoder`, `cortex`, `information_foraging`,
`coref`, `goal_owner_select`, `definitional_extraction` -- and `situation_reader` once its self-test
is re-run with a longer budget.

**`_scratch_orig_goal_owner_select` appears in the 67. It is a SCRATCH FILE. Remove it from
`hdlab/` and from the registry rather than counting it as recoverable capability.**

**Evidence:** `scratch/organ_audit/selftest_results.json`, `scratch/organ_audit/good_but_unused.json`.
