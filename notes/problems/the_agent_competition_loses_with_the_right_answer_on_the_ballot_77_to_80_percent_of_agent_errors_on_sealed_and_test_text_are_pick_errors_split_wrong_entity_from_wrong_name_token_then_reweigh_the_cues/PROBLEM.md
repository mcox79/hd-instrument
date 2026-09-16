---
priority: 140
slug: the_agent_competition_loses_with_the_right_answer_on_the_ballot_77_to_80_percent_of_agent_errors_on_sealed_and_test_text_are_pick_errors_split_wrong_entity_from_wrong_name_token_then_reweigh_the_cues
status: OPEN
review:
review_text:
---

# PROBLEM: the reader's actor (agent) read is BELOW the simple word-order rule on raw modern text, on the sealed holdout (0.6328 vs 0.7171, n=806) and on the ordinary test set alike, and 77 to 80 percent of its errors had the right answer on the ballot and lost the weighing. It is a weighting defect in the agent competition, not a candidate-supply defect. First split the pick errors into 'wrong entity' and 'right entity, wrong token of its name' (a scoring convention), then re-weigh the competition's cues so wrong-ENTITY picks fall CI-separated on both populations.

**slug:** `the_agent_competition_loses_with_the_right_answer_on_the_ballot_77_to_80_percent_of_agent_errors_on_sealed_and_test_text_are_pick_errors_split_wrong_entity_from_wrong_name_token_then_reweigh_the_cues`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The agent of a clause is decided by a cue competition (Bates & MacWhinney's Competition Model: word order, animacy, agreement, case, the verb's own expectations), each cue weighted by its VALIDITY in the language as accrued from reading; English weighs word order highest. A competition that loses to bare word order on English is mis-weighted, not under-supplied.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. The cue validities are counts from reading (the attachment arm's form), never a fitted classifier.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the agent competition lives in `hdlab/graded_role_assigner.py` (the Competition-Model role labeler; pri 106/108/111/117/129 landed arms). Re-weigh it there; do not build a second agent picker.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** the agent row feeds who-did-what, goals, affect; name every flip and repair the consumer.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.** **THE SEALED HOLDOUT IS READ ONCE PER LANDING BY STRATEGY, NEVER BY A SOLVER**: you work on UD-EWT (train for validities, dev for choices, test for the number) and the reader-driven rows; the sealed number is strategy's at landing.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Reproduce pri 126's anatomy on UD-EWT test first-hand (`experiments/exp_sealed_modern_holdout_v1.py --agent-anatomy --pop udtest`: correct 424/561, no_event 3, candidate_set_miss 25, pick_error 109). Then THE SPLIT (bar 1): for every pick error, is the picked token a member of the SAME gold entity/name run as the gold head ('right entity, wrong token': the UD first-token-of-a-name convention, `Kori` vs `Schulman`) or a different entity ('wrong entity')? Use the gold `flat`/`compound` runs and gold coref where GUM is used; report both populations.
> 2. **REUSE.** `hdlab/graded_role_assigner.py` (the competition: `_cm_agent_candidates`, the cue tables, `strengths_from_counts`, the pri 106 `ppc` cue, the pri 111 clause-scoped passive cue, the pri 117 copular subject cue), `hdlab/attachment_arm.py` (heads and the graded head belief -- the word-order/structure cue should read the arm's SUBJECT arc, not token distance), `hdlab/lexical_categories.py` (the category posterior: a pick of an ADJ-tagged token is a category-rung leak, pattern 4), `hdlab/referent_per_np.py` (mentions; pri 138 will widen spans -- coordinate: your fix must not depend on the span).
> 3. **GENERALIZE.** The re-weighing is validities accrued from reading (UD-EWT train counts, online observe path), one table, every clause type.
> 4. **WALL -> DEEPER.** If the competition prefers a distant nominal (pattern 2: 66 items, `which` vs `it`), the missing cue is the relative-clause / clause-boundary scope (the same clause scoping pri 111 built for the passive cue); if it prefers a modifier (pattern 4), the category posterior is being read as a point estimate -- read it graded.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep only the validity-accrual rate and the decision temperature.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The no-event residual (copulas/modals: 25 sealed items) is the predicate-slot chain (pri 133-adjacent), not yours: count it, do not chase it.
> 7. **ADJACENT.** pri 126 (the instrument), pri 138 (spans), pri 133 (the predicate slot), pri 111 (clause scoping), LOCATED item 1 (sub-item below).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** The validity-accrual rate and the decision temperature are FREE TO SWEEP; the cue set is the Competition Model's.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the reader decides who did the action in a sentence, it is wrong more often than a rule that just takes the first noun before the verb, and that is true on text it has never seen. Looking at every mistake on both sets of documents: in about four of five, the right person or thing WAS among the candidates the reader considered, and it chose another one. So giving it more candidates cannot fix this (that would cap out at one mistake in seven); the way it weighs the candidates is wrong. Two of the commonest mistakes may partly be a scoring convention rather than a misreading: for a two-word name the test counts only the first word as right, and for 'the South Korean company' the reader sometimes picks 'Korean'. The brief's first job is to separate 'picked the wrong person' from 'picked the right person but the wrong word of their name', because they need opposite fixes; the second job is to re-weigh the competition so that picking the wrong person becomes rarer, clearly separated, on both sets.

## 2. WHY THIS ONE

The agent row is the product's most-answered question (coverage 0.969) and it reads below a trivial rule on the sealed holdout, the one instrument that cannot be tuned. The defect is located to the weighing with counts on two populations (pri 126, 2026-09-16). It sits on the roles rung, which every downstream question (goals, affect, who-did-what) consumes.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED: cue competition with language-specific cue validities (Bates & MacWhinney 1989; English: word order > agreement > animacy); validities accrued from exposure. OUR-INVENTION: the representation of the structure cue (the attachment arm's subject arc with its graded belief rather than linear order), the clause-scope gate, the decision temperature.

## 4. MEASURED vs INFERRED

MEASURED (pri 126, `--agent-anatomy`, raw text, gold read only after the answer): sealed PUD n=806 (806 active, 0 passive): correct 510 (0.6328), no_event 25, no_agent_emitted 0, candidate_set_miss 42 (14.2% of errors), pick_error 229 (77.4%); UD-EWT test n=561: correct 424 (0.7558 = the landed board's number), no_event 3, candidate_set_miss 25 (18.3%), pick_error 109 (79.6%). Patterns (sealed): nearby competing nominal 131 (`Kori` vs `schulman`), distant nominal >6 tokens 66 (`which` vs `it`), candidate miss + nearby nominal 26 (`BA` vs `iag`), an ADJ-tagged token picked 20 (`company` vs `korean`), a pronoun agent lost to a nominal 8 (`everyone` vs `party`). Gold-only convention bounds on the sealed 806: 95 (11.8%) gold agents head a flat/compound run (43 PROPN-headed); 265 (32.9%) carry a pre-head modifier -- UPPER BOUNDS. The floor is the word-order rule (0.7171 sealed). LOCATED item 1 (every token of a by-phrase as a candidate): 3 items on UD-EWT test (2.2% of its errors), 0 on the sealed set (no passives with an agent).

INFERRED (verify): that most of the 131 'nearby nominal' errors are wrong-ENTITY picks (the split decides); that the structure cue reads token distance rather than the arm's subject arc; that the ADJ picks are the category posterior read as an argmax.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 106 (the `ppc` cue: organ decision +0.0864 CI-sep on GUM test), pri 111 (clause-scoped passive cue), pri 117 (copular subject), pri 129 (patient reliability from the competition): landed arms; build on them, do not re-derive.
- `agent_hybrid` / `agent_hybrid_construction` flags: measured 2026-09-16 on the product's raw-text agent row -- ON is WORSE (-0.0488); do not re-try them as the lever.
- pri 126's withdrawn UD-EWT pass (1017 items / 0.7611): a harness bug; never quote it.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `experiments/exp_sealed_modern_holdout_v1.py --agent-anatomy --pop udtest` -- reproduce 424/561 and the cause table (touch NO sealed file; the sealed population is strategy's).
2. `grep -n "_cm_agent_candidates\|strengths_from_counts\|def .*agent" hdlab/graded_role_assigner.py` -- the competition's entry points; read the cue list and how the structure cue is computed.
3. `git log --oneline -5 -- hdlab/graded_role_assigner.py` -- pri 134's non-argument arm landed 2026-09-16 (run-members OFF); your hunks must apply on it.
4. Confirm pri 138's state (`notes/problems/the_introduction_organ_opens_one_referent_per_content_noun_token_*`): if its span diff has landed, mention spans are NPs and `wtok_start` is the span start; if not, the head. Your split must work either way.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **THE SPLIT FIRST.** Every pick error on UD-EWT test (109) and, by strategy at landing, on the sealed set (229) labelled wrong-ENTITY vs right-entity-wrong-TOKEN, with the method stated (gold name runs / coref) and the two counts reported; the scorer of the reader-driven agent row gains an entity-level column (right entity counts as right) beside the token-level one -- both reported, the token-level stays the gate until the owner rules otherwise.
2. **Wrong-entity pick errors DOWN CI-separated** on UD-EWT test (bootstrap over items, both arms in one process) with the re-weighed competition; the agent row ABOVE the word-order floor on UD-EWT test CI-separated; an info-free twin (validities permuted across cues) loses.
3. **No-regress:** patient / state / the copular subject read on the same populations not down CI-separated; the pri 106/111/117 witnesses green on the landed tree.
4. **Plastic:** the validities are counts with an observe path (a two-document read shows the second document's decisions used the first's updates); the accrual rate swept, not adopted.
5. **Sub-item (LOCATED item 1):** the by-phrase candidate set reads the attachment arm's head; the 3 UD-EWT items reported before/after.
6. **Hand-off for strategy:** the landed competition re-read on the sealed holdout ONCE at landing (pri 126's hook); you predict the sealed number from UD-EWT and the prediction is recorded before the read.

## 8. FILES AND ENTRY POINTS

- `hdlab/graded_role_assigner.py` -- the Competition-Model role labeler: `_cm_agent_candidates`, the cue tables, `strengths_from_counts`, `roles_with_decisions`, the pri 134 non-argument arm (do not touch it).
- `hdlab/attachment_arm.py` -- the subject arc and its graded belief; `hdlab/lexical_categories.py` -- the category posterior.
- `experiments/exp_sealed_modern_holdout_v1.py --agent-anatomy` -- the anatomy (pri 126); `experiments/exp_board_rows_on_the_reader_v1.py` -- the reader-driven agent row and its scorer.
- `data/frontend_assets/` -- the competition's validity assets (find the current one via the labeler's loader).

Write ONLY: `experiments/exp_agent_pick_reweigh_v1.py` (NEW cell: the split, the anatomy on the landed tree, the re-weighed competition, the twin, the no-regress; `get_output_dir` per Q115; `--self-test`), `verification/test_agent_competition_reweigh_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, agent_reweigh_patch.diff}` (unified diffs against `hdlab/graded_role_assigner.py`, the scorer in `experiments/exp_board_rows_on_the_reader_v1.py`, and any asset builder in `tools/`; never edit hdlab/ or tools/ directly), plus a rebuilt validity asset under `data/frontend_assets/` with a NEW name. Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command.

## DO NOT QUOTE / DO NOT REDO

- Do not quote 0.7611 / 1017 items (withdrawn harness bug).
- Do not read, list or open `data/corpora/holdout/` -- the seal is strategy's; a solver that reads it spends it.
- Do not re-try the agent_hybrid flags (measured worse).
- 19c corpora are informational only (owner 2026-09-06).
