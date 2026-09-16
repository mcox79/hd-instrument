---
priority: 142
slug: the_structure_map_every_organ_to_the_brain_structure_it_stands_in_for_the_computation_it_performs_the_organs_that_perform_the_same_computation_and_the_structures_each_task_uses_and_should_use
status: OPEN
review:
review_text:
---

# PROBLEM: the substrate is organized by task, not by brain structure, so nobody can see that five organs perform the same selection computation, four registers share no update mechanism, 14 organs exist twice, and a task uses one structure where the brain would use three. Build THE STRUCTURE MAP: every organ -> the brain structure it stands in for -> the computation it performs -> the other organs performing the SAME computation -> the structures each board task uses today and SHOULD use (the coordination map) -> each organ's read-time cost. Its output is the ranked consolidation list the next three briefs execute.

**slug:** `the_structure_map_every_organ_to_the_brain_structure_it_stands_in_for_the_computation_it_performs_the_organs_that_perform_the_same_computation_and_the_structures_each_task_uses_and_should_use`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The brain reuses one structure for many functions (the owner's rule of 2026-09-11): one basal-ganglia selection loop serves every competition; one hippocampal-cortical situation model serves every dimension; one anterior-temporal hub serves every lexical read. This brief is the audit that makes that reuse VISIBLE for our substrate, with numbers, so the consolidations that follow are ranked by measurement, not opinion.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the map records, per organ, PINNED / MODEL / OUR-INVENTION / NOT_BF honestly (the capability registry's `fidelity_basis` and `notes/bf_status_registry.jsonl` exist; reconcile them, do not restate them).
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the map's unit is the STRUCTURE; organs are its arms or its copies.
> **THE OWNER'S CONCERN (2026-09-16):** "tasks aren't using other brain components in conjunction when they could and ultimately should" -- the coordination map is not optional; it is the deliverable that answers 'is each component doing what it should and coordinating with whom it should'.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing 'cannot be mapped'.
> **NO CODE CHURN IN THIS BRIEF:** the map is documents + registry fields + one measured cost table; the consolidations are pri 143-145.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Enumerate every organ: `hdlab/*.py` (all of them, ~70 modules), the capability registry (`data/capability_registry.jsonl`, `brain_structure` and `fidelity_basis` fields), `notes/bf_status_registry.jsonl`, `ORGAN_MAP.md`, `notes/BRAIN_FOUNDATIONAL_AUDIT.md`, `notes/BRAIN_MATH_REFERENCE.md`. Reconcile: where they disagree, the disk wins and the disagreement is a row.
> 2. **REUSE.** pri 139's `verification/test_organ_copies_are_one_object.py` (the 16 pairs); pri 134's SOLVED.md (four organs reused for one rung -- the model case); pri 137/139's alias mechanism; the live chain description in `notes/STATUS.md` (tokens -> categories -> lemma -> heads -> roles -> mentions -> entities -> registers).
> 3. **GENERALIZE.** The SAME-COMPUTATION groups must be found by reading what each organ computes (its math), not by name: e.g. every organ that scores candidates by summed log-odds cue validities and picks an argmax (attachment_arm's arc competition, graded_role_assigner's role labels, the agent pick, entity_resolver's object-file competition, space_reader's ground selection, the pronoun pick's ACT-R retrieval) is one group; every organ that folds timed evidence into a per-entity state with a prior and a revise-on-surprise rule (state_register, location_register, belief_reader/ledger, goal_register) is another; every organ that reads a frozen lexical asset (lexicon_foundation, meaning_foundation, the animacy lexicon, the supersense asset) is a third.
> 4. **WALL -> DEEPER.** An organ with no brain structure you can name is a finding, not a gap in the map: record it as OUR-INVENTION with the computation it performs and the structure that performs the nearest computation in the brain.
> 5. **OPTIMIZE BY MEASUREMENT.** Read-time cost per organ on the same 6 GUM documents (profile one full read; attribute time per module; `cProfile` is admissible for measurement), so the consolidation list is ranked by cost as well as by duplication.
> 6. **THE COORDINATION MAP.** For each board row (the seven reader-driven rows + where-is + the entity set), list the structures the task USES today (trace the call graph from the row's reader call) and the structures the brain would use for that task (cite), and name every missing conjunction with the number it would touch (e.g. the goal register decides closure without the state register's result state; the agent pick reads word order without the attachment arm's subject arc; belief binds nothing because the id spaces are disjoint).
> 7. **ADJACENT.** pri 143 (the competition engine), 144 (the register), 145 (the copies), 132 (the analysis object = the one id space), 140 (the agent competition), 138 (spans).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Not applicable; a map.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The reader is built from about seventy parts named after jobs ("goal register", "space reader", "crosstype bridge"), not after the brain structures they imitate. So nobody can see, without reading all seventy, that five of them make decisions the same way (score the options by learned weights, pick the best), that four keep running tallies the same way, that fourteen exist twice, or that a job uses one part where a brain would use three together. Last night measured the cost: two solvers built the same repair, one solver rebuilt a part that already existed and had been validated, one part had drifted from its copy across four landings, and the knowledge tracker cannot bind names to pronouns because two parts number entities differently. This brief draws the map: for every part, which brain structure it stands in for, what it computes, which other parts compute the same thing, how much reading time it costs, and, for every job the reader is scored on, which structures it uses now and which it should be using together. The map's last page is the list of what to merge, in order of payoff.

## 2. WHY THIS ONE

The owner asked for it on 2026-09-16 ("very important; much faster than a week") after last night's evidence, and it gates the three consolidations that follow: they must be ranked by measured duplication and cost, not by guess. It also changes how every later brief is written (REUSE by structure) and how every phase-7 probe is answered.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED at the level that matters here: one structure, many functions -- basal-ganglia loops select among cortical candidates for every domain (motor, attention, working memory, language: Bates & MacWhinney's competition is one instance); the hippocampal-cortical situation model has dimensions (space, time, protagonist, causation, intentionality: Zwaan & Radvansky) that share one indexing mechanism; the anterior temporal hub serves every lexical-semantic read (Patterson, Nestor & Rogers 2007). The map assigns each organ to one of these (or names its own structure) and records the citation.

## 4. MEASURED vs INFERRED

MEASURED (2026-09-16): 16 organ/copy pairs, 14 drifted, none an alias (pri 139's witness); three parse sources for the space organ (pri 137); the same coverage repair built twice (134/136); a validated organ re-implemented (139 vs attachment_arm.cop_subject_pairs); disjoint entity id spaces (744 negative / 345 positive / 0 shared); `strengths_from_counts` shared by the role labels and the non-argument arm (pri 134 asserted identity) but the agent pick, the object-file competition and ground selection each carry their own scoring; four registers (state, location, belief, goals) with four update paths; ~38 organs rated in the brain-foundational audit, ~5 computing the brain's actual equation (notes/BRAIN_FOUNDATIONAL_AUDIT.md). The registry's `brain_structure` field exists on every row.

INFERRED (verify): that the same-computation groups are the three named in checklist item 3 plus a fourth (the trackers/typers that classify by a frozen table); that read time is dominated by repeated parses (pri 139 counted ~90k redundant re-parses in one arm; pri 137 found the space organ re-parsing with a private parser).

## 5. ALREADY TRIED / DO NOT RE-RUN

- `ORGAN_MAP.md` and the brain-foundational audit exist and are partial: build ON them, do not restart them.
- The registry audit (`tools/capability_registry_audit.py`) enumerates modules and reachability; reuse its enumeration, do not re-derive it.
- Do not rename anything in this brief (the owner's rule: rename at consolidation time).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `ls hdlab/*.py | wc -l`; `python tools/capability_registry_query.py --kind hdlab-module --json | head` -- the organ list and the registry fields.
2. `.venv/Scripts/python.exe verification/test_organ_copies_are_one_object.py` -- the 16 pairs and their states (pri 139).
3. `sed -n 1,120p ORGAN_MAP.md`; `grep -n "^## \|^### " notes/BRAIN_FOUNDATIONAL_AUDIT.md | head -40`; `head -60 notes/BRAIN_MATH_REFERENCE.md`.
4. The live chain: `grep -n "def read\b\|_read_" hdlab/situation_reader.py | head -40` -- the reader's dimensions and their order.
5. `grep -n "strengths_from_counts\|def .*competition\|def .*_pick" hdlab/*.py` -- the candidate members of the selection group.

## 7. THE BAR (can-fail; a map is graded by completeness and by what it lets the next brief measure)

1. **Every organ mapped.** One row per `hdlab/*.py` module (plus the experiments copies as 'copy of'): structure (with citation), computation (one sentence of math), BF status reconciled with the registry, arms, importers count, copies. Zero unmapped modules; an organ whose structure cannot be named is a row marked OUR-INVENTION with the nearest brain computation.
2. **The same-computation groups, with the math.** Each group lists its members and the equation they share (and where a member deviates); the selection group, the register group, the lexical-read group, and any other you find; each with the measured evidence that they are the same computation (e.g. the same log-odds sum; the same evidence-prior-revise loop).
3. **The cost table.** Read time per organ on the same 6 GUM documents (one profiled full read; per-module attribution; total), with the redundant work named (repeated parses, repeated lexical reads).
4. **The coordination map.** For each board row + where-is + the entity set: the structures used today (traced), the structures the brain uses (cited), every missing conjunction with the rows it would touch. This answers the owner's question directly.
5. **The ranked consolidation list**: targets ordered by duplicated computation x read-time cost x product rows affected, each with the brief that owns it (143 competition engine, 144 register, 145 copies) or a new brief-ready text.
6. **Registry + map updated**: `brain_structure` and `fidelity_basis` filled for every row via the registry's locked writer (`tools/capability_registry_audit.py::append_rows` / the transaction helper -- never a raw write); `ORGAN_MAP.md` regrouped by structure with the task view kept; `notes/BRAIN_FOUNDATIONAL_AUDIT.md` gets a §2b entry.
7. **No code changed** in hdlab/ or tools/ (a witness that the map is documents + registry: `git diff --stat -- hdlab tools` empty for your commits).

## 8. FILES AND ENTRY POINTS

- `hdlab/*.py` (all), `hdlab/situation_reader.py` (the dimensions and their order), `hdlab/frontend.py` (the shared reading frontend).
- `data/capability_registry.jsonl` (+ `tools/capability_registry_audit.py`, `tools/capability_registry_query.py`), `notes/bf_status_registry.jsonl`, `ORGAN_MAP.md`, `notes/BRAIN_FOUNDATIONAL_AUDIT.md`, `notes/BRAIN_MATH_REFERENCE.md`.
- `verification/test_organ_copies_are_one_object.py` (pri 139), `experiments/exp_board_rows_on_the_reader_v1.py` (the rows to trace).

Write ONLY: `notes/STRUCTURE_MAP_2026-09-16.md` (the map: organs, groups, cost table, coordination map, ranked list), `experiments/exp_structure_map_cost_v1.py` (the profiled read; `get_output_dir` per Q115; `--self-test`), the registry rows via the locked helper, `ORGAN_MAP.md` (regrouped), `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (a §2b entry), `notes/problems/<slug>/SOLVED.md`. No hdlab/ or tools/ edits; no renames. Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command.

## DO NOT QUOTE / DO NOT REDO

- Do not quote retired figures (`notes/reference_retired_claims_never_requote.md`).
- Do not rename modules or move files; do not collapse copies here (pri 145).
- 19c corpora are informational only (owner 2026-09-06); the cost table uses modern GUM documents.
