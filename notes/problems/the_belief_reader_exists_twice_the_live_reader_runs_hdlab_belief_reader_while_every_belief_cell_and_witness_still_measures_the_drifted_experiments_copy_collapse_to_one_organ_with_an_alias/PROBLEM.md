---
priority: 139
slug: the_belief_reader_exists_twice_the_live_reader_runs_hdlab_belief_reader_while_every_belief_cell_and_witness_still_measures_the_drifted_experiments_copy_collapse_to_one_organ_with_an_alias
status: OPEN
review:
review_text:
---

# PROBLEM: the belief reader exists twice. The live reader runs `hdlab/belief_reader.py` (promoted 2026-09-09), but every belief cell and witness still imports `experiments/_belief_reader.py` as `BR`, a copy that has drifted (51 differing lines; 500 vs 493). So the belief numbers on record describe a module the product does not run. Collapse the two to ONE organ the way pri 137 did for the space reader (a `sys.modules` alias, not a star-import), prove equivalence, and re-measure the belief instruments on the organ.

**slug:** `the_belief_reader_exists_twice_the_live_reader_runs_hdlab_belief_reader_while_every_belief_cell_and_witness_still_measures_the_drifted_experiments_copy_collapse_to_one_organ_with_an_alias`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** One structure, many functions (owner 2026-09-11): the belief-at-t read (what an agent knows, when; testimony, perception, narrator epistemics) is ONE organ; a second implementation of the same computation is a defect even when it is byte-identical today, because it stops being identical at the next landing (the space reader's copy drifted four landings before pri 137 caught it).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. The 2026-09-09 spaCy purge reached the ledger; check the copy for any stand-in the organ has since lost.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** `hdlab/belief_reader.py` is the organ; the cells' `BR` becomes the same object.
> **DOWNSTREAM REGRESSION AFTER A BF UPSTREAM IS NOT FAILURE:** if a belief instrument's number moves when it is pointed at the organ, that number was describing the copy; report the organ's number and name what the 51 lines changed.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (with your diff applied), not on the tree you started from.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Diff the two files (`diff experiments/_belief_reader.py hdlab/belief_reader.py`, whitespace-insensitive: 51 lines on 2026-09-16) and classify every differing hunk: promotion-only (imports/paths), a landing the organ received and the copy did not, or a change the copy received and the organ did not (the dangerous class).
> 2. **REUSE.** pri 137's alias pattern in `experiments/_space_reader.py` (a `sys.modules` alias of `hdlab.space_reader`; its SOLVED.md explains why a star-import re-creates the defect) and its equivalence proof (9 documents, 0 mismatches).
> 3. **GENERALIZE.** Enumerate every importer of the copy (on 2026-09-16: 5 experiments, 2 hdlab mentions in comments/lazy-import notes, 4 verification; `grep -rn "_belief_reader" hdlab experiments verification`), repoint each through the alias, and run every belief witness on the organ.
> 4. **WALL -> DEEPER.** If a witness turns red on the organ, the copy was hiding a change: name the hunk and decide whether the organ or the copy is right (with the number), never keep the copy alive for that witness.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The belief-at-t instrument (`experiments/exp_belief_at_t_end_to_end_v1.py`, witness `verification/test_belief_at_t_end_to_end_organ.py`) before/after on the organ; the ToM chain witness; any board row fed by belief.
> 7. **ADJACENT.** pri 137 (the precedent), pri 132 (the analysis object; belief consumes entity/event ids), LOCATED item 15 (the cell's spaCy arm, repaired 2026-09-16).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Nothing to sweep in this brief.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The part of the reader that tracks what each character knows and when they learned it was copied from the experiments folder into the reader's own package on 9 Sep, and the reader was switched to the copy. The measurements of that part, though, still run the old file, which has since drifted apart from the one the reader uses (about fifty lines differ). So every 'belief' number on record is a number for code the product does not run. The same thing happened to the map-reading part and was caught and fixed today (pri 137): the fix is to make the old file a transparent alias of the real one, prove the two give the same answers on a set of documents, and re-run the belief measurements on the real one.

## 2. WHY THIS ONE

It is on the LOCATED list (item 18, found 2026-09-16 while repairing item 15), and the rule since the efficiency review is that a located cause becomes a brief the same day. Its cost is not a score: it is that the belief instruments are measuring a phantom, so any belief landing since 9 Sep is unverified on the product path. It is cheap (pri 137 did the same for the space reader in under an hour).

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

Not a mechanism brief. The structural rule is pinned by the owner (one structure, many functions; no islanded copies). The alias is OUR-INVENTION for the transition and is acceptable only because it makes the two names one object.

## 4. MEASURED vs INFERRED

MEASURED (2026-09-16 03:35): `hdlab/belief_reader.py` was added 2026-09-09 (commit 6c49804fd, 'promote _belief_reader -> hdlab; reader now has ZERO experiments imports'); `experiments/_belief_reader.py` last changed 2026-09-03, the organ 2026-09-09; a whitespace-insensitive diff shows 51 differing lines (500 vs 493 lines). The live reader imports the organ (`hdlab/situation_reader.py:2956`, `from hdlab import belief_reader as _BR`) while the belief end-to-end cell imports the copy (`experiments/exp_belief_at_t_end_to_end_v1.py:44`, `import experiments._belief_reader as BR`); importers of the copy: 5 experiments files, 4 verification files, 2 mentions in hdlab (comments at `situation_reader.py:1210/1216/2949`).

INFERRED (verify): that the 51 lines are promotion-only plus the spaCy purge (the copy may still carry a stand-in the organ dropped); that the belief numbers on record move little when pointed at the organ.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 137's alias (space): done and landed as the precedent; reuse its exact mechanism and its equivalence-proof shape.
- Do not star-import the organ into the copy (pri 137: that re-creates the defect for any monkeypatch-based witness).
- LOCATED item 15 (the cell's spaCy arm) is already repaired; do not touch that block except to keep it green.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `diff <(sed 's/[[:space:]]*$//' experiments/_belief_reader.py) <(sed 's/[[:space:]]*$//' hdlab/belief_reader.py)` -- read every hunk.
2. `grep -rn "_belief_reader" hdlab experiments verification | grep -v __pycache__` -- your importer list.
3. `sed -n 1,40p experiments/_space_reader.py` -- the alias precedent as landed by pri 137 (if it has landed; else read its diff in `notes/problems/the_live_space_readers_*/space_ground_lever_patch.diff`).
4. Run `verification/test_belief_at_t_end_to_end_organ.py` once as it ships (green on 2026-09-16, 29 s) to have the copy's number.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **One organ.** `experiments/_belief_reader.py` is a `sys.modules` alias of `hdlab.belief_reader` (every public name IS the organ's object; a witness that asserts identity, not equality), and every importer enumerated in SOLVED.md still imports green.
2. **Equivalence proven, not assumed.** The copy's read and the organ's read compared on at least 9 documents (the belief instrument's own passages plus GUM narrative docs): mismatches counted and, for each, the hunk responsible named; the organ's answer is the one kept.
3. **The belief instruments re-measured on the organ**: the belief-at-t end-to-end cell and its witness, the ToM chain witness, any belief-fed board row -- before (copy) and after (organ), with the delta and CI where the instrument has one; a moved number is reported with its cause, never hidden.
4. **No stand-in.** The organ path has no spaCy/nltk/supervised model at inference (assert it in the witness the way `test_no_nltk_on_the_live_path` does: poisoned import, the read completes).
5. **Nothing else changes.** A digest of every non-belief field of the situation model on 6 GUM docs is byte-identical before/after (pri 137's E-check).

## 8. FILES AND ENTRY POINTS

- `hdlab/belief_reader.py` -- the organ (`drive`, `extract_reality_events` :206, the ledger hand-off).
- `experiments/_belief_reader.py` -- the copy to alias.
- `hdlab/situation_reader.py:2949-2960` -- the live import; the comments at :1210/:1216 still name the copy (update them in the diff).
- `experiments/exp_belief_at_t_end_to_end_v1.py` (:44 `BR`), `experiments/exp_belief_extraction_drill_v1.py`, the other three experiments importers; `verification/test_belief_at_t_end_to_end_organ.py`, `test_belief_timeline*.py`, `test_tom_chain_landing.py` and the fourth verification importer.
- `experiments/_space_reader.py` -- the alias precedent (pri 137).

Write ONLY: `experiments/exp_belief_one_organ_v1.py` (NEW cell; the equivalence proof + the before/after; `get_output_dir` per Q115; `--self-test`), `verification/test_belief_reader_one_organ.py` (NEW witness: identity + poisoned-import), `notes/problems/<slug>/{SOLVED.md, belief_one_organ_patch.diff}` (unified diffs against `experiments/_belief_reader.py`, `hdlab/situation_reader.py` comments, and every importer you repoint; never edit hdlab/ or tracked verification files directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time.

## DO NOT QUOTE / DO NOT REDO

- Do not quote any belief number measured through the copy as the product's number until bar 3 has re-measured it.
- Do not re-derive pri 137's alias mechanism; copy it.
- 19c corpora are informational only (owner 2026-09-06).
