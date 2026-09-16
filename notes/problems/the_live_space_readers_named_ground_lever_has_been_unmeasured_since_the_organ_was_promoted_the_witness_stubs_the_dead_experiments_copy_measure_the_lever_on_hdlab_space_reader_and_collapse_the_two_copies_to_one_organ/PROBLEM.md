---
priority: 137
slug: the_live_space_readers_named_ground_lever_has_been_unmeasured_since_the_organ_was_promoted_the_witness_stubs_the_dead_experiments_copy_measure_the_lever_on_hdlab_space_reader_and_collapse_the_two_copies_to_one_organ
status: OPEN
review:
review_text:
---

# PROBLEM: the live reader's named-ground lever (where a person IS after 'went into the barn') has had NO measurement since 2026-09-09. Its only end-to-end witness switches the lever off in a module the live reader no longer runs, so ON == OFF by construction (0.4255 both arms, recorded 2026-09-15). Measure the lever where it actually runs, repair it if it is genuinely inert, and collapse the two copies of the space reader into one organ.

**slug:** `the_live_space_readers_named_ground_lever_has_been_unmeasured_since_the_organ_was_promoted_the_witness_stubs_the_dead_experiments_copy_measure_the_lever_on_hdlab_space_reader_and_collapse_the_two_copies_to_one_organ`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A reader keeps one situation model per discourse; a motion clause with a NAMED ground ('into the barn') updates the mover's place in that model (Zwaan & Radvansky event-indexing, the spatial dimension; hippocampal place binding of an agent to a named location). The named-ground pass IS that update; the question here is whether the live organ still performs it.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. The space reader's parse comes from the reader's own category organ + attachment arm through `parse_provider`; keep it that way.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-11):** there is ONE space reader, `hdlab/space_reader.py`. `experiments/_space_reader.py` is a byte-faithful COPY left behind at the 2026-09-09 promotion; 56 files still import the copy. Two copies of one organ drift, and this brief exists because they did.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** if the lever, once actually ON, moves other space rows, name the flips and repair the consumer; never switch the lever off to satisfy a no-regress gate.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (with your diff applied), not on the tree you started from.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Reproduce the defect first-hand: run W4 of `verification/test_space_ground_binding.py` as written (it stubs `experiments._space_reader.ground_bind_events`) and then the SAME measurement with the stub applied to `hdlab.space_reader.ground_bind_events` (the module `hdlab/situation_reader.py:2926` imports). Report both ON/OFF pairs with n.
> 2. **REUSE.** `hdlab/space_reader.py` (`extract_events_in_substrate` :402, the named-ground append :477-484, `ground_bind_events` :687, `read_locations_in_substrate` :768 -- `ground_bind=ext`, live mode `prior_ext`), `hdlab/situation_reader.py::_read_space` (:2916-2940; passes the reader's own mention stream since pri 125), `hdlab/location_register.py` (the tracker the events fold into).
> 3. **GENERALIZE.** Every importer of `experiments._space_reader` (56 files: enumerate with grep, not memory) reads the ONE organ afterwards -- a re-export shim is acceptable as the transition, a second implementation is not.
> 4. **WALL -> DEEPER.** If ON == OFF holds on the live module too, the lever is dead for a reason on a line: `person_clusters` empty from the reader's stream (`build_backbone(..., mentions=...)`; pri 125's hand-off, LOCATED item 11: gendered common nouns become movers, -0.043 both arms), the conservative filter rejecting every clause, or `fold_tracker` discarding the appended events. Locate it, then repair the hand-off so the graded signal reaches the tracker.
> 5. **OPTIMIZE BY EXACT REPLICATION;** the conservative path is the landed one; the aggressive/anticipatory paths are located negatives (`hdlab/space_reader.py:519-521`) -- do not re-open them without a new reason.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The lever's effect must be measured through the FULL live read (`SituationReader...read(cp).locations`), never through the cell's own driver.
> 7. **ADJACENT.** pri 132 (the document analysis object; owns the space hand-off repair of item 11), pri 125 (the stream), pri 133 (attachment; PP grounds attach through the same arm).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Nothing to sweep in this brief; it is a measurement-and-consolidation brief with a repair branch.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When the reader reads 'Tom went into the barn', the space part of its situation model should record that Tom is now in the barn, by name, rather than 'somewhere away'. That named-place step was added on 6 Sep and measured then as a clear gain (+0.170 on the six modern test passages, end to end). On 9 Sep the space reader was promoted from an experiments file into the reader's own package as a byte-faithful copy, and the live reader was repointed to the copy. The end-to-end check was NOT repointed: it still switches the step off in the OLD file, which the live reader no longer runs. So the check compares the live reader with itself and reports the same number for 'on' and 'off' (0.4255, recorded 15 Sep). Nobody has measured the live named-place step since 9 Sep, and the check that was supposed to guard it cannot fail for the reason it was written.

Two things follow. First, measure the step where it runs; if it still works, pin the check to the live module and move on. If it is genuinely doing nothing there, find the line where the signal dies (the most likely place: the person clusters the reader hands to the space part since pri 125 differ from the ones the old driver built) and repair the hand-off. Second, the old file is a full second copy of the organ that 56 files still import; two copies of one organ drift, which is exactly how this defect arose. Collapse them to one.

## 2. WHY THIS ONE

It is a located root cause on the LOCATED list at the top of `notes/STATUS.md` (item 10), and the rule since the 2026-09-15 efficiency review is that a located cause becomes a brief the same day. It is cheap (a measurement, a witness re-pin, and a consolidation), it removes a witness that cannot fail, and it may recover a landed gain (+0.170 on where-is) that the live reader may have silently lost. It also serves the owner's one-structure-one-organ rule: the space reader currently exists twice.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED (computational level): readers maintain a spatial dimension of the situation model and update a protagonist's location on motion clauses (event-indexing, Zwaan & Radvansky 1998); place-to-agent binding is hippocampal (place cells; the binding of 'who' to 'where'). OUR-INVENTION: the specific event schema (cluster, kind, node, t, conf), the conservative filter (irrealis/discovery gates), the tracker's fold. The brief does not ask for new mechanism; it asks that the pinned update actually happen in the live organ.

## 4. MEASURED vs INFERRED

MEASURED: (a) `hdlab/situation_reader.py:2926-2935` imports `hdlab.space_reader` and calls `read_locations_in_substrate(..., mode="prior_ext", parse_provider=...)`; `hdlab/space_reader.py:782` passes `ground_bind=ext` (True in `prior_ext`); :477-484 appends `ground_bind_events(..., conservative=True)` when `person_clusters` is non-empty. (b) `verification/test_space_ground_binding.py:83-105` (W4) stubs `experiments._space_reader.ground_bind_events`, a function in the copy (`experiments/_space_reader.py:583`), then reads through the live `SituationReader`. (c) `git log`: `hdlab/space_reader.py` was added 2026-09-09 (3ed0c7f4a, 'promote _space_reader -> hdlab/space_reader.py (byte-faithful); reader _read_space repointed'); `experiments/_space_reader.py` last changed 2026-09-06. (d) `notes/STATUS.md` LOCATED item 10: W4 ON == OFF at 0.4255 on 2026-09-15, and the same on HEAD before pri 125. (e) 56 files under hdlab/experiments/verification/tools reference the experiments copy; 9 reference the hdlab organ.

INFERRED (verify): that the live lever DOES still move where-is when switched off in the right module (the +0.170 of 2026-09-06 was measured when the reader imported the copy, so the live path was measured then; nothing since). That LOCATED item 11 (the reader's stream making gendered common nouns movers, -0.043 both arms) shares a cause with a dead lever: unverified.

## 5. ALREADY TRIED / DO NOT RE-RUN

- The aggressive and anticipatory ground-binding paths: located negatives (`hdlab/space_reader.py:519-521`, the 2026-09-06 landing); do not re-run.
- The lazy locative-PP recall bridge (W1 of the same witness): refuted as a where-is lever (recall 0.44 -> 0.89 moved where-is only ~+0.06); do not re-run.
- The 2026-09-15 landing of pri 125 recorded W4's ON == OFF and moved on (item 10); no repair was attempted. Nothing here has been tried.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `grep -n "space_reader" hdlab/situation_reader.py` -- confirm the live import is `hdlab.space_reader` (line numbers above may have drifted).
2. `grep -n "ground_bind" hdlab/space_reader.py experiments/_space_reader.py verification/test_space_ground_binding.py` -- confirm the witness patches the copy.
3. `grep -rl "_space_reader" hdlab experiments verification tools | wc -l` -- your importer count (expect ~56).
4. Run W4 as written and note its current verdict (it asserts `on > off`; if ON == OFF it is RED today -- say so).
5. Confirm the 6-passage modern gold and its helpers still exist: `experiments/exp_space_where_is_modern_v1.py` (PASSAGES, write_conll, build_gold), `experiments/exp_space_where_is_end_to_end_v1.py` (gold_at, correct).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **The live lever measured where it runs.** The W4 measurement with the stub on `hdlab.space_reader.ground_bind_events`, through the full live read, on the six modern passages: ON vs OFF with n and a bootstrap CI over items, reported in SOLVED.md whatever the sign.
2. **Branch A (ON > OFF CI-separated):** W4 re-pinned to the live module (it must be able to go red: forcing OFF must lower where-is); the product board's space rows compared ON vs forced-OFF in ONE process and reported (a report, not a gate).
3. **Branch B (ON == OFF on the live module):** the death line located and named (file:line, with the count of clauses reaching `ground_bind_events` and the count of events it returns on the six passages, and the same counts through the old driver); the hand-off repaired so the lever moves (bar 1 then holds), OR, if the repair belongs to pri 132's analysis object, the located line handed to pri 132 in SOLVED.md and the dead call REMOVED rather than left silent.
4. **One organ.** `experiments/_space_reader.py` becomes a re-export shim of `hdlab.space_reader` (or is deleted with every importer repointed); every importer enumerated in SOLVED.md; the witnesses that import it still green (list them; run the fast tier via `tools/witness_status.py`).
5. **No-regress.** The six-passage modern where-is is not below 0.4255 after your diff; the who-did-what events on the W5 passage remain byte-identical (W5 of the same witness).
6. **Twin.** For branch A: the shuffled-ground twin (already in `exp_space_named_ground_binding_v1`) loses on the live module too.

## 8. FILES AND ENTRY POINTS

- `hdlab/space_reader.py` -- the ONE organ: `extract_events_in_substrate` (:402; the named-ground append :477-484), `ground_bind_events` (:687), `read_locations_in_substrate` (:768; `ground_bind=ext` :782).
- `hdlab/situation_reader.py::_read_space` (:2916-2940) -- the live call, `mode="prior_ext"`, the reader's own mention stream (`mentions=role_mentions`, :4994).
- `experiments/_space_reader.py` -- the dead copy (`extract_events_in_substrate` :298, `ground_bind_events` :583, `read_locations_in_substrate` :664).
- `verification/test_space_ground_binding.py` -- W4 (:77-113) is the defective check; W5 (:115-131) is the additive-safety check to keep green.
- `experiments/exp_space_where_is_modern_v1.py`, `experiments/exp_space_where_is_end_to_end_v1.py`, `experiments/exp_space_named_ground_binding_v1.py`, `experiments/exp_space_ground_binding_live_wire_v1.py` -- the gold, the scorer, the twin, the earlier live-wire cell.
- `hdlab/location_register.py` -- the tracker (`fold_tracker` in the organ folds into it).

Write ONLY: `experiments/exp_space_ground_lever_live_v1.py` (NEW cell; `get_output_dir` per Q115; `--self-test`), `notes/problems/<slug>/{SOLVED.md, space_ground_lever_patch.diff}` (unified diffs against `hdlab/space_reader.py`, `hdlab/situation_reader.py`, `experiments/_space_reader.py`, `verification/test_space_ground_binding.py` and any importer you repoint; never edit hdlab/ or tracked verification files directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time (the laptop is shared with the product board).

## DO NOT QUOTE / DO NOT REDO

- Do not quote the +0.170 live gain of 2026-09-06 as current: it predates the promotion and is exactly what this brief re-measures.
- Do not quote 0.4255 as the lever's effect: it is the SAME arm measured twice.
- Do not re-run the aggressive/anticipatory ground paths or the locative-PP bridge (located negatives above).
- 19c LitBank numbers (W3) are informational only (owner 2026-09-06); grade on the modern six passages and the product board.
