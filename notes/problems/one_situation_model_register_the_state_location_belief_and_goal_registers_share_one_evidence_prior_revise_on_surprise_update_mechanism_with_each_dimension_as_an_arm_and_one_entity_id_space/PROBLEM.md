---
priority: 144
slug: one_situation_model_register_the_state_location_belief_and_goal_registers_share_one_evidence_prior_revise_on_surprise_update_mechanism_with_each_dimension_as_an_arm_and_one_entity_id_space
status: OPEN
review:
review_text:
---

# PROBLEM: the reader keeps four situation-model dimensions (state, location, belief, goals) in four registers with four update mechanisms, four hand-offs from the entity layer and, as of last night, two of them dead at the hand-off (belief binds nothing; the space hand-off discarded the reader's own resolutions until pri 137). The brain keeps ONE situation model whose dimensions share one indexing and updating mechanism. Make the four registers ARMS of one register: one evidence-in / prior / revise-on-surprise / decay loop, one entity id per mention from the object-file organ, one hand-off; byte-identical per dimension first, then the shared repairs reach every dimension at once.

**slug:** `one_situation_model_register_the_state_location_belief_and_goal_registers_share_one_evidence_prior_revise_on_surprise_update_mechanism_with_each_dimension_as_an_arm_and_one_entity_id_space`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The situation model is one hippocampal-cortical structure with dimensions (space, time, protagonist, causation, intentionality; Zwaan & Radvansky 1998's event-indexing) that are updated by the same mechanism: new evidence is indexed against the current model, a mismatch (surprise) triggers an update, continuity leaves it standing (Zacks, Speer & Reynolds 2009's event segmentation is the same loop at a coarser grain). Our four registers are four copies of that loop.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no external tool at inference; priors and decay are swept parameters, never adopted numbers.
> **ONE ENTITY ID SPACE (pri 132's requirement, pri 139's finding):** the register keys every dimension by the object-file organ's entity id (pri 131/136), pronoun and nominal alike; the negative/positive split on `m["cluster"]` is retired at this mechanism.
> **THE OWNER'S CONCERN (2026-09-16):** dimensions must coordinate -- a goal closes on a RESULT STATE (the state arm), a belief about a location reads the location arm, a location change is an EVENT the time arm orders. One register makes each of those a read of a sibling arm.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** byte-identity per dimension is bar 1; a shared repair that moves a dimension is named and its consumers repaired.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.** Land AFTER pri 137 and 135 (their register diffs) and coordinate with pri 132 (the analysis object): read both SOLVED.md files first.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Read pri 142's map (the register group). Then each register's update loop as code: `hdlab/state_register.py` (`apply_state`, the copular/result-state reads, the pri 117/135 arms), `hdlab/location_register.py` (`fold_tracker`'s prior/revise-on-surprise, pri 137's union at the hand-off), `hdlab/belief_reader.py` + `hdlab/perceptual_access_ledger.py` (the ledger; the dead id-space binding), `hdlab/goal_register.py` (+ `goal_hierarchy_graph`; pri 135's constraints and closing_outcome). Write the four loops side by side as equations.
> 2. **REUSE.** The location register's prior_fold (the most explicit evidence/prior/surprise loop), pri 135's 'a conflict is evidence only when the rung that produced it could know', pri 137's `unify_entity_files`, pri 136's entity ids, pri 131's `resolved_entity`.
> 3. **GENERALIZE.** ONE register module with: an entity-keyed store per dimension, `index(evidence, t)`, the surprise test, `revise`, `decay`, and `query(entity, t)`; each dimension = its evidence reader + its value space, declared as an arm. The hand-off from the entity layer happens ONCE (the mention stream + entity ids) for all arms.
> 4. **WALL -> DEEPER.** Where a dimension's loop genuinely differs (goals have a satisfaction test; belief has an access ledger), keep the difference as the arm's own step inside the shared loop, and say what the brain's version of that step is.
> 5. **OPTIMIZE BY EXACT REPLICATION;** decay, prior weight and the surprise threshold are per arm, swept.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Byte-identity per dimension on its own instrument (the board's state row; where-is; the belief-at-t instrument; the goal instrument of pri 135) is bar 1; then ONE shared repair (the one id space; the one hand-off) applied to all and measured on all.
> 7. **ADJACENT.** pri 142, 132 (the analysis object), 137/135/139 (the register diffs landing before this), 138 (spans), 143 (the engine: the register's evidence readers may be engine arms).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Per arm: prior weight, surprise threshold, decay -- FREE TO SWEEP.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The reader keeps four running accounts of a story -- what state things are in, where people are, what each person knows, what each person wants -- in four separate ledgers with four separate bookkeeping rules and four separate ways of being told who is who. Last night showed two of those ledgers were not being told who is who at all: the knowledge ledger cannot match a name to a pronoun because two parts number people differently, and the map ledger was throwing away the reader's own pronoun decisions until a repair yesterday. A brain keeps one situation model whose dimensions share one updating rule. Make ours one register with four arms: first proving each arm gives exactly the answers it gave before, then fixing the shared plumbing once for all four, and letting the arms read each other (a goal is met when the state ledger shows the result; a belief about a place reads the map ledger).

## 2. WHY THIS ONE

Four copies of one loop are where last night's hand-off defects lived (items 11, 19, 20 on the LOCATED list), and the owner's coordination concern is concrete here: goals close without reading states; beliefs bind without reading the entity layer. It is the second-ranked consolidation in the program after the competition engine.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED: event-indexing across dimensions with one updating mechanism (Zwaan & Radvansky 1998; Zwaan 2016); event segmentation as prediction error / surprise (Zacks et al. 2007, 2009); the hippocampal index binding an entity to its situation (Teyler & DiScenna 1986; the file-card view of pri 136). OUR-INVENTION: the value space per dimension; the ledger's access rules for belief; the goal satisfaction test.

## 4. MEASURED vs INFERRED

MEASURED: the space hand-off discarded the reader's resolutions (pri 137: where-is 0.0426 -> 0.4043 with the union); the belief hand-off binds nothing by construction (pri 139: 744 negative / 345 positive / 0 shared ids); the goal register decided closure by verb + agent alone until pri 135 (content constraint 0.94 vs 0.50); the state register has no parse access (pri 139's census) and reads the copular subject through the attachment arm (pri 117); four registers, four `apply`/`fold`/`drive`/`update` entry points (pri 142's map will list them with line numbers).

INFERRED (verify): that byte-identity per dimension is reachable in one step; that the one hand-off + one id space repair moves belief binding from 0 to the tens pri 139 measured with the union (18-26 binds on 71 facts) and leaves the state row unchanged.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 137's union and pri 135's constraints are landed arms of this register; build on them.
- The belief mention hand-off ALONE is a measured no-op (pri 139); do not ship it without the id space.
- Do not re-open Principle B (pri 136: stays off) or the aggressive ground paths (pri 137).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `notes/STRUCTURE_MAP_2026-09-16.md` -- the register group (pri 142).
2. `grep -n "def apply_state\|def fold_tracker\|def drive\|def apply\b\|def update" hdlab/state_register.py hdlab/location_register.py hdlab/belief_reader.py hdlab/goal_register.py` -- the four loops.
3. `grep -n "resolved_entity\|_online_lab\|m\[\"cluster\"\]" hdlab/situation_reader.py | head -30` -- the id spaces and the hand-offs (:2965, :4920-4924, :4995).
4. pri 137's, 135's and 139's SOLVED.md and whether their diffs have landed (`git log --oneline -8`).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **One register, four arms, byte-identical** on each dimension's own instrument (state row; where-is; belief-at-t; the goal instrument) before/after; every register witness green.
2. **One hand-off, one id space**: every arm keyed by the object-file organ's entity id; the negative/positive split gone from the register's path (a witness that a nominal and a pronoun of the same entity share a key); the belief binding rate 0 -> the union's figure (pri 139: 18-26 binds on 71 facts) reported with CI.
3. **Coordination shown**: at least two cross-arm reads measured (a goal closing on the state arm's result state; a belief about a location reading the location arm), each with the twin.
4. **Product board**: every model row byte-identical at the byte-identity step; the shared repairs' effect on the reader-driven rows reported (state, where-is, goals if a row exists).
5. **Plastic**: priors/decay swept; an observe path for the surprise threshold if any is learned.
6. **Cost**: read time not up; one hand-off instead of four.

## 8. FILES AND ENTRY POINTS

- `hdlab/state_register.py`, `hdlab/location_register.py`, `hdlab/belief_reader.py`, `hdlab/perceptual_access_ledger.py`, `hdlab/goal_register.py`, `hdlab/goal_hierarchy_graph.py` -- the four registers.
- `hdlab/situation_reader.py` (:2916-2965 the space/belief hand-offs; :4920-4924 the id split; :4994 the mention stream) -- the hand-offs.
- `hdlab/entity_resolver.py`, `hdlab/coref.py` -- the entity ids (pri 131/136).

Write ONLY: `experiments/exp_situation_register_v1.py` (NEW cell: per-arm replay identity, the shared-repair A/B, the cross-arm reads; `get_output_dir` per Q115; `--self-test`), `verification/test_situation_register_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, situation_register_patch.diff}` (unified diffs; never edit hdlab/ or tools/ directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command; never read `data/corpora/holdout/`.

## DO NOT QUOTE / DO NOT REDO

- Do not quote retired figures (`notes/reference_retired_claims_never_requote.md`); do not quote the belief witness's 0.600 (a phantom, pri 139).
- Do not ship the belief mention hand-off without the id space.
- 19c corpora are informational only (owner 2026-09-06).
