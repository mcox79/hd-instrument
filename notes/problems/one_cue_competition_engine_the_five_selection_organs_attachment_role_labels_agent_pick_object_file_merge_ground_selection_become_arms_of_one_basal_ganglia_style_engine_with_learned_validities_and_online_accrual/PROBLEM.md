---
priority: 143
slug: one_cue_competition_engine_the_five_selection_organs_attachment_role_labels_agent_pick_object_file_merge_ground_selection_become_arms_of_one_basal_ganglia_style_engine_with_learned_validities_and_online_accrual
status: OPEN
review:
review_text:
---

# PROBLEM: at least five organs perform the same computation -- score candidates by summed cue validities learned from reading, pick the winner, accrue the validities online -- each with its own scorer, its own accrual and its own decision rule (the attachment arm's arc competition, the role labeler, the agent pick, the object-file merge decision, the space reader's ground selection; the pronoun pick's ACT-R retrieval is the same family). Make them ARMS of ONE cue-competition engine (the cortex-basal-ganglia selection loop with learned validities), byte-identical per arm first, so that an improvement to the engine (pri 140's re-weighing; a graded decision; a clause-scope gate) reaches every arm at once.

**slug:** `one_cue_competition_engine_the_five_selection_organs_attachment_role_labels_agent_pick_object_file_merge_ground_selection_become_arms_of_one_basal_ganglia_style_engine_with_learned_validities_and_online_accrual`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Selection among cortical candidates is ONE mechanism for every domain: the basal ganglia's action-selection loop (Redgrave, Prescott & Gurney 1999; Mink 1996) applied to language as the Competition Model (Bates & MacWhinney 1989): cue strength = validity (from exposure) x availability; the candidate with the highest summed support wins; the outcome updates the validities. Our substrate has five copies of this loop. One structure, many functions (owner 2026-09-11).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no fitted classifier, no external tool at inference; validities are counts from reading with an online observe path (the attachment arm's form is the template).
> **THE OWNER'S CONCERN (2026-09-16):** components must coordinate: an arm's decision must be able to READ another arm's graded output (the agent pick reading the attachment arm's subject arc belief; ground selection reading the role competition's goal/source roles). One engine makes that a call, not a re-implementation.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** byte-identity per arm is the FIRST bar; once the engine is one, an engine improvement that moves an arm is named and its consumers repaired.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.** Coordinate with pri 140 (the agent competition re-weigh, in flight): read its SOLVED.md; its re-weighing becomes the engine's default for the agent arm if landed, else an engine feature the arm switches on.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Read pri 142's structure map (the selection group with the shared equation and each member's deviation). If pri 142 has not finished, derive the group yourself from the code: `hdlab/attachment_arm.py` (arc scores, validities asset, `observe`), `hdlab/graded_role_assigner.py` (`strengths_from_counts`, the role competition, `agent_competition_pick` / `_pick_conf` :2402-2440, the pri 134 non-argument arm), `hdlab/entity_resolver.py` (`competition_cluster`, `observe_file_decision`, the criterion shift), `hdlab/space_reader.py:717-731` (ground selection), `hdlab/coref.py::graded_pronoun_resolve` (ACT-R retrieval).
> 2. **REUSE.** `strengths_from_counts` (already shared by two arms -- the seed of the engine), the attachment arm's validity asset format and `observe` path, pri 136's accrual margin and criterion shift, pri 140's re-weighing (if landed).
> 3. **GENERALIZE.** ONE module (`hdlab/cue_competition.py` or the surviving organ's name at consolidation time) exposing: candidates + cue values -> summed log-odds support per candidate -> the decision (argmax, threshold-to-open-new, or a graded posterior) -> `observe(outcome)` accrual; each arm = a cue reader + a validity table + a decision rule declared as data, not code.
> 4. **WALL -> DEEPER.** Where an arm's math genuinely differs (ACT-R base-level activation + spreading vs summed log-odds), say whether it is the same computation in a different parameterisation (it usually is: activation = log-odds of need) and unify the parameterisation, or keep it as a documented second decision rule of the same engine.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the engine's parameters (accrual rate, threshold, temperature) are per arm and swept, never adopted.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Byte-identical decisions per arm on the arm's own instrument (the attachment arm's UD-EWT heads; the role labels; the agent row; the object-file B-cubed; where-is) is bar 1; then ONE engine improvement applied to all arms and measured on all (bar 3).
> 7. **ADJACENT.** pri 142 (the map), 140 (agent re-weigh), 136 (object files), 133/110 (attachment), 134 (labels), 137 (ground selection), 131 (the pick).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Per arm: accrual rate, decision threshold, temperature -- FREE TO SWEEP, never adopted.

## 1. THE PROBLEM IN PLAIN LANGUAGE

Five parts of the reader decide things the same way: they weigh the options by how reliable each clue has been in past reading and take the best. Each part has its own copy of that weighing, so an improvement to one (last night's re-weighing of the actor decision, for instance) helps only that one, and a part cannot easily ask another part what it thinks. The brain has one such decision mechanism serving every domain. Make ours one engine with five arms: first proving each arm decides exactly as before, then improving the engine once and watching every arm move.

## 2. WHY THIS ONE

It is the largest duplicated computation in pri 142's map (five to six members), it is where the product's most-answered row is losing (the agent pick, pri 140), and it is the mechanism through which components would coordinate (the owner's concern): one engine lets the agent arm read the attachment arm's subject belief and the ground arm read the role arm's goal role as inputs.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED: basal-ganglia action selection as a domain-general winner-take-all over cortical candidates with learned weights (Redgrave et al. 1999; Gurney, Prescott & Redgrave 2001); the Competition Model's cue validity x availability (Bates & MacWhinney); ACT-R's activation as log-odds of need (Anderson & Schooler 1991), which makes the pronoun pick the same computation. OUR-INVENTION: the candidate/cue representation per arm; the threshold-to-open-new rule (pri 136); the accrual margin.

## 4. MEASURED vs INFERRED

MEASURED: `strengths_from_counts` is the identical math for the role labels and the non-argument arm (pri 134 self-test S7); the agent pick has its own scorer (`agent_competition_pick`, pri 126: 77-80% of its errors are pick errors); the object-file competition has its own scorer + accrual (pri 136: ACT-R base level + log-odds validities; accrual margin 1.0); ground selection is a preposition-list scan (pri 137: 14/26 change points however it is read); the attachment arm's validities asset + observe path is the most mature form (pri 94-133).

INFERRED (verify): that unifying the parameterisations costs nothing per arm (byte-identity achievable) and that one engine-level improvement (the re-weighing, a graded decision) moves at least two arms.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 134 already reused `strengths_from_counts` verbatim; that is the model.
- The `agent_hybrid` flags (measured worse 2026-09-16); do not re-try.
- Do not re-derive the validity assets from scratch; the engine reads the existing per-arm assets (new names only where a format changes).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `notes/STRUCTURE_MAP_2026-09-16.md` (pri 142) -- the selection group; if absent, item 1 of the checklist.
2. `grep -n "def strengths_from_counts\|def agent_competition_pick\|def competition_cluster\|def observe" hdlab/*.py` -- the members' entry points.
3. pri 140's folder (`notes/problems/the_agent_competition_loses_*`) -- its state and diff.
4. Each arm's own instrument and witness (attachment: `verification/test_attachment_arm*.py`; roles: `test_role_*`; object files: `test_object_file_competition.py`; where-is: `experiments/exp_space_ground_lever_live_v1.py`; the pick: `experiments/exp_pronoun_pick_identity_contract_v1.py`).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **One engine, five arms, byte-identical.** Each arm's decisions on its own instrument are IDENTICAL before/after (a replay witness per arm: same inputs, same decisions, same numbers); the engine's `observe` reproduces each arm's accrual exactly.
2. **Every arm's witnesses green** on the landed tree; the product board byte-identical on every model row at this step.
3. **One engine improvement reaches every arm**: apply ONE change at the engine (e.g. the graded decision, or pri 140's structure cue read from the attachment arm's belief) and report every arm's number before/after with CI; at least two arms move, the twin loses per arm.
4. **Coordination shown**: at least one arm reads another arm's graded output through the engine (the agent arm reading the subject-arc belief; the ground arm reading the role arm's goal role) and the effect is measured.
5. **Plastic**: every arm's validities accrue online through the engine; a two-document read shows it.
6. **Cost**: read time not up; the map's cost table re-measured for the arms.

## 8. FILES AND ENTRY POINTS

- `hdlab/attachment_arm.py`, `hdlab/graded_role_assigner.py`, `hdlab/entity_resolver.py`, `hdlab/space_reader.py`, `hdlab/coref.py` -- the members.
- `data/frontend_assets/` -- the validity assets (attachment_validities_*, fine_relation_validities_*, object_file_validities_*).
- `notes/STRUCTURE_MAP_2026-09-16.md` -- the group and the ranking (pri 142).

Write ONLY: `experiments/exp_cue_competition_engine_v1.py` (NEW cell: per-arm replay identity, the engine improvement A/B, the coordination measurement; `get_output_dir` per Q115; `--self-test`), `verification/test_cue_competition_engine_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, cue_competition_engine_patch.diff}` (unified diffs: the new engine module and each member's arm; never edit hdlab/ or tools/ directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command; never read `data/corpora/holdout/`.

## DO NOT QUOTE / DO NOT REDO

- Do not quote retired figures (`notes/reference_retired_claims_never_requote.md`).
- Do not rebuild any validity asset from scratch; do not re-try the agent_hybrid flags.
- 19c corpora are informational only (owner 2026-09-06).
