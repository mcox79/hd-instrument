---
priority: 149
slug: twenty_six_remember_a_pure_function_memos_live_at_module_level_and_on_readers_make_one_memo_organ_lexicon_memo_and_passage_memo_with_the_activation_cue_set_parse_and_passage_pos_memos_as_arms_after_143_144_145
status: OPEN
review:
review_text:
---

# PROBLEM: twenty-six 'remember a pure function of this key' memos exist on the tree (pri 142's 25 module-level memos, pri 137's per-read parse cache, pri 146's per-reader activation and cue-set memos): two computations (a property of the FROZEN LEXICON, process-lived; a property of THIS PASSAGE, read-lived) implemented 26 times with 26 growth policies -- make ONE memo organ with two scopes (LexiconMemo, PassageMemo) and the existing memos as arms, equivalence by identity per arm, the standing one-object witness as the gate. Sequenced AFTER pri 143/144/145 (the program's step 6).

**slug:** `twenty_six_remember_a_pure_function_memos_live_at_module_level_and_on_readers_make_one_memo_organ_lexicon_memo_and_passage_memo_with_the_activation_cue_set_parse_and_passage_pos_memos_as_arms_after_143_144_145`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** One structure, many functions (owner 2026-09-11/16). Persistence of a computed value is one mechanism in the brain -- activation that has not decayed (priming; ACT-R base-level activation within a trial) -- with two time scales here: what is true of the lexicon for the life of the process and what is true of this passage for the life of the read. Twenty-six private copies of that mechanism are the copy defect pri 145 collapses for organs, applied to memos.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- no external tool, dataset or model at inference; offline foundation assets admissible at build time only; parameters swept, never adopted.
> **ONE READER = ONE BRAIN (pri 142 P7.2, applied by pri 136/146):** plastic or per-passage state lives on the SituationReader instance; module-level assets are read-only.
> **THE OWNER'S PROGRAM (2026-09-16, consolidate by brain structure):** REUSE BY STRUCTURE before building (list the organs that already compute this, from notes/STRUCTURE_MAP_2026-09-16.md); a second implementation of an existing computation is a defect; the phase-7 probe asks 'did you re-implement an organ that exists?'.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing 'wall', 'ceiling' or 'negative'.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED** (detect the landed state from the live modules, never with hasattr on something that may exist for another reason).
> **PATCH IN BYTES with each file's own line endings** (the tree mixes LF and CRLF; assert `git diff -w --stat` == `git diff --stat`); never a delete command; never read `data/corpora/holdout/`; cap cores `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; waits are background shell loops.

## 1. THE PROBLEM IN PLAIN LANGUAGE

Twenty-six places in the reader remember the answer to a question they have already asked, each with its own rules for how much to remember and when to forget, and none of them knows about the others. Two of them are the reader's newest and largest (pri 146). There are only two kinds: things true of the dictionary for as long as the program runs, and things true of this page for as long as it is being read. Make one part that does both, with the existing twenty-six as its arms, and prove each arm gives byte-identical answers.

## 2. WHY THIS ONE

pri 146 found it while adding the 26th (its phase-7 re-implementation check): the memos' growth is uncapped at module level (pri 142: 'keep; growth uncapped'), their scopes are implicit (a module memo that keys on passage state is the read-to-read instability class pri 146 just removed), and every future per-reader memo (the category posterior asked 1.98x, the arc scores 2.17x -- pri 146's next two repeats) would be a 27th and 28th. It is the program's step 6 and lands after 143/144/145 so it does not block the reads landing now.

## 3. HOW THE BRAIN DOES THIS (frame)

PINNED: persistence of activation within a reading (priming; ACT-R base-level activation); decay across readings. OUR-INVENTION: the exact-then-evicted representation; the two scopes as classes; the capacity as a reported bound.

## 4. MEASURED vs INFERRED

MEASURED (pri 142 P7 A; pri 146 C): 25 module-level content-addressed memos over 56 live-read modules (keep, growth uncapped); pri 137's `SituationReader._read_parse_cache`; pri 146's `_ppr_memo` (cap 128; one entry 470,636 bytes; peak 20-128; 7 evictions on one document) and its cue-set memo; cross-document repeat rate of the activation keys 0.00% (so a passage memo must die with the read); 26 call sites in ~16 modules, two being written by landings (140, 146).

INFERRED (verify): that every module memo is a pure function of its key (no hidden passage state) -- the state probe of pri 142/146 (fingerprint the INSTANCE) decides; that consolidation costs no read time (measure).

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 146's proposal (its SOLVED.md section C: `hdlab/memo.py` with `LexiconMemo` + `PassageMemo`, costed) is the design to start from.
- pri 145's collapse procedure (alias, identity witness, equivalence per pair, the one-object witness) is the procedure; do not invent another.

## 6. VERIFY BEFORE YOU START

1. `notes/STRUCTURE_MAP_2026-09-16.md` (the plasticity section + pri 146's dated addendum) -- the 25 memos by name.
2. `grep -n "_memo\|lru_cache\|_cache" hdlab/*.py | wc -l` and the list -- the call sites.
3. pri 146's SOLVED.md section C and `ppr_memo_patch.diff` -- the two newest memos.
4. `git log --oneline -5` -- whether 143/144/145 have landed (this brief waits for them).

## 7. THE BAR (can-fail; the gate is IDENTITY)

1. **One organ, two scopes**, every existing memo an arm (enumerated: 26 + any added since), each with its key function, scope and capacity declared.
2. **Byte-identical reads** per arm (the pri 146 harness) and the product board byte-identical on every model row.
3. **The one-object witness** green: no memo outside the organ (a standing gate like pri 139's copy witness).
4. **Read time not up; peak memory reported** per scope.
5. **The state probe green:** fingerprinting the reader INSTANCE and the module tables shows no per-passage state at module level.

## 8. FILES AND ENTRY POINTS

- `hdlab/grounded_semantic_graph.py`, `hdlab/situation_reader.py` (`_read_parse_cache`, `_ppr_memo`), the 25 module memos as the map lists them.

Write ONLY: `hdlab/memo.py` (NEW, via the diff), `experiments/exp_memo_organ_v1.py` (NEW cell; `get_output_dir`; `--self-test`), `verification/test_memo_organ_one_object.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, memo_organ_patch.diff}`.

## DO NOT QUOTE / DO NOT REDO

- Do not build a cross-document activation store (refuted: 0.00% key recurrence).
- Do not land before 143/144/145 (their members carry memos this brief will absorb).
- 19c corpora informational only.

*(filed by strategy 2026-09-16 15:22 from pri 146 phase 7; same-day rule for a located root cause.)*
