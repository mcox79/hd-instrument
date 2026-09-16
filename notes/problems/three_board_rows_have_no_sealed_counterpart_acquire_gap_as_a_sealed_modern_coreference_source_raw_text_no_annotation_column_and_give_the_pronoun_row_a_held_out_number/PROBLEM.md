---
priority: 141
slug: three_board_rows_have_no_sealed_counterpart_acquire_gap_as_a_sealed_modern_coreference_source_raw_text_no_annotation_column_and_give_the_pronoun_row_a_held_out_number
status: OPEN
review:
review_text:
---

# PROBLEM: three of the board's seven rows -- pronoun coreference, salience and common-noun coreference -- have no sealed counterpart, because the only modern coreference gold on this disk is GUM/OntoGUM and all 301 of its documents are read by 234 files; acquire GAP as a sealed modern coreference source and give those rows a held-out number measured on raw text.

**slug:** `three_board_rows_have_no_sealed_counterpart_acquire_gap_as_a_sealed_modern_coreference_source_raw_text_no_annotation_column_and_give_the_pronoun_row_a_held_out_number`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** This is an INSTRUMENT brief: no mechanism is built; the deliverable is a sealed source, its manifest, its scorer and its board arm, following pri 126's seal exactly. **THE OPENING MOVE** still applies to the instrument: the product's task is to find the pronoun in running text and bind it (Kahneman-Treisman object files; Heim's file cards), so the sealed text must reach the reader with NO annotation column, and the scorer must judge the ENTITY bound, not a token.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- the measured path has no external tool at inference; a foundation ASSET fetched offline (GAP's text) is admissible (owner 2026-07-14 / 08-16), a gold read at decision time is not.
> **19c IS BANNED FROM REQUIREMENTS (owner 2026-09-06):** GAP is modern Wikipedia; WikiCoref is modern; no LitBank/McGuffey.
> **THE SEAL IS SPENT BY READING:** you fetch, seal and declare; the reader's first read of the sealed set is made ONCE by strategy at landing through pri 126's landing hook, never by you. Your own measurements use GAP's development split only, drawn and sealed separately from the test split.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing wall / negative.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.**

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Read pri 126's SOLVED.md (its enumeration proving no unread coreference document exists on disk; its seal mechanics; its landing hook) and reuse the cell's `--enumerate/--fetch/--seal` shape.
> 2. **REUSE.** `experiments/exp_sealed_modern_holdout_v1.py` (the seal, the manifest, the retirement rule, the read counter), `verification/test_sealed_holdout_is_unread.py` (the seal witness; W7 fails on a planted leak), `experiments/exp_board_rows_on_the_reader_v1.py` (the pronoun row's scorer: gold entity at the target, model answer = the entity at the antecedent span; since pri 136 an IDENTITY scorer beside the span scorer), `experiments/exp_pronoun_pick_identity_contract_v1.py` (the pick's instrument).
> 3. **GENERALIZE.** The sealed pronoun row runs through the same board arm and the same landing hook as pri 126's rows; one provenance line per landing.
> 4. **WALL -> DEEPER.** GAP's candidates are two NAMES: it seals the name-antecedent case only. Say so in the manifest and pair it with WikiCoref (30 long modern documents) for the document-level rows; if WikiCoref's licence or format blocks, report why and seal GAP alone.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The first sealed number (taken by strategy) will be compared with the capped GUM row (pri 131: 0.2385 vs floor 0.1280) -- write in advance what a gap between them would mean (population, genre, the two-name candidate set).
> 7. **ADJACENT.** pri 126 (the seal), pri 131/136 (the pick and its scorers), pri 138 (spans), pri 125 (pronoun discovery).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Nothing to sweep.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The sealed set of unseen documents landed today covers who did what and characters' states, but not pronouns, because every modern document with pronoun answers on this machine has already been read by some part of the reader's build. GAP is a free set of 8,908 modern Wikipedia passages, each with one pronoun and two named candidates and the answer, shipped as plain text with no annotation of any kind. Fetch it into the sealed folder that no loader ever opens, seal it the way the first holdout was sealed (ids, hashes, the scorer, the configuration, all committed before anyone looks at an answer), and give the pronoun row a number on text the reader has never seen, read once per landing.

## 2. WHY THIS ONE

pri 126 proved by enumeration (10,006 files walked) that no unread coreference document exists on disk, and pri 125/131/136 made the pronoun pick the reader's own (text-discovered pronouns, an entity contract, the object-file competition) -- exactly the claims a sealed, annotation-free pronoun instrument would settle. Without it, three of seven board rows can be tuned to their only gold.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

Not a mechanism brief. The instrument's demand is pinned by the task: the reader must find the pronoun and bind it to an entity it opened itself.

## 4. MEASURED vs INFERRED

MEASURED (pri 126, 2026-09-16): GUM/OntoGUM 301/301 documents read by 234 files; GENTLE numbers quoted as calibration inside `hdlab/lexical_categories.py:227-241`; `data/corpora/holdout/` is walked by no loader (two files name it, both pri 126's); GAP = `google-research-datasets/gap-coreference`, three TSVs (`gap-development.tsv`, `gap-validation.tsv`, `gap-test.tsv`), 8,908 instances, Apache 2.0 repository / CC BY-SA 3.0 text, each row = snippet + pronoun offset + two candidate names with offsets and TRUE/FALSE labels; acquirable (HTTP 206 on a ranged request at the time of writing). The capped GUM pronoun row: n=805, 0.2385 vs floor 0.1280 (pri 131 board).

INFERRED (verify): that WikiCoref (30 annotated modern Wikipedia documents) is fetchable under a licence the repo can hold; that GAP's two-name candidate frame is scorable through the reader's own entity files without reading the candidates' offsets at decision time (the offsets are the ANSWER KEY only).

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 126's enumeration: do not redo it; cite it. Its seal mechanics are the template.
- Do not place the corpus under `data/corpora/gap/` (every loader's glob convention would reach it eventually); `data/corpora/holdout/gap_sealed_v1/` only.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `sed -n 1,80p experiments/exp_sealed_modern_holdout_v1.py` and its `--fetch` / `--seal` code paths; `verification/test_sealed_holdout_is_unread.py` W1-W8.
2. `grep -rn "holdout" hdlab tools experiments verification | grep -v __pycache__` -- confirm the only readers of the holdout folder are pri 126's.
3. The pronoun row's scorer in `experiments/exp_board_rows_on_the_reader_v1.py` (the gold-entity key; the identity scorer if pri 136's row diff has landed).
4. The retirement policy in `data/corpora/holdout/SEALED_modern_v1.json` (one read per landing; RESERVE_V2 rules) -- your seal adopts the same policy.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)

1. **Sealed before seen.** `data/corpora/holdout/gap_sealed_v1/` fetched at a pinned commit; a manifest (ids, per-snippet SHA-256, the draw rule and seed for the sealed test subset, the scorer by import + file hash, the configuration hashes, the retirement policy) COMMITTED before any answer is examined; the seal witness extended (a planted leak fails it; the read counter refuses a second read at the same HEAD).
2. **Annotation-free by construction.** The measured path receives the snippet text only; the pronoun is DISCOVERED by the reader (pri 125), never supplied; the candidates' offsets and labels are read only by the scorer after the answer. Assert it in the witness.
3. **A scorer declared in writing** before the first answer: the reader's answer is the ENTITY its pick binds (the file's members / the antecedent span) matched to the TRUE candidate's name; abstention counts wrong; the strongest simple floor (nearest preceding name; most frequent name) and an info-free twin (candidate labels permuted) declared with it.
4. **A board arm** in the reader-driven cell with the same provenance columns, wired into pri 126's landing hook; the DEVELOPMENT split (sealed separately) gives you your own dry-run number with CI; the TEST split's first read is strategy's.
5. **WikiCoref** sealed alongside for the document-level rows (salience, common-noun coreference) or the reason it cannot be, in writing.
6. **Nothing else changes:** no hdlab/ file; the existing board rows byte-identical.

## 8. FILES AND ENTRY POINTS

- `experiments/exp_sealed_modern_holdout_v1.py`, `verification/test_sealed_holdout_is_unread.py`, `data/corpora/holdout/SEALED_modern_v1.json` -- pri 126's seal (the template and the shared policy).
- `experiments/exp_board_rows_on_the_reader_v1.py` -- the pronoun row and its scorers; `tools/land.py` -- the landing hook (after pri 126 lands).
- `hdlab/referent_per_np.py`, `hdlab/coref.py::graded_pronoun_resolve`, `hdlab/entity_resolver.py` -- the measured path (read-only for you).

Write ONLY: `experiments/exp_sealed_gap_holdout_v1.py` (NEW: `--fetch`, `--seal`, `--scorer`, `--dev-run`, `--self-test`; `get_output_dir` per Q115), `verification/test_sealed_gap_is_unread.py` (NEW witness), `data/corpora/holdout/SEALED_gap_v1.json` (the manifest) and `data/corpora/holdout/gap_sealed_v1/PROVENANCE.json` (the corpus files themselves stay gitignored, re-acquirable via `--fetch`), `notes/problems/<slug>/{SOLVED.md, gap_seal_patch.diff}` (the board arm as a unified diff against `experiments/exp_board_rows_on_the_reader_v1.py`; never edit hdlab/ or tools/). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command; never read the sealed TEST split.

## DO NOT QUOTE / DO NOT REDO

- Do not quote the capped GUM pronoun number as a held-out number.
- Do not read the sealed test split; a solver that reads it spends it.
- 19c corpora are informational only (owner 2026-09-06).
