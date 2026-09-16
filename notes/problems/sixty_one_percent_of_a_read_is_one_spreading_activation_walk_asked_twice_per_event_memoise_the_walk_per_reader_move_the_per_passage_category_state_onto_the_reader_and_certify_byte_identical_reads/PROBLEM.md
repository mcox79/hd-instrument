---
priority: 146
slug: sixty_one_percent_of_a_read_is_one_spreading_activation_walk_asked_twice_per_event_memoise_the_walk_per_reader_move_the_per_passage_category_state_onto_the_reader_and_certify_byte_identical_reads
status: OPEN
review:
review_text:
---

# PROBLEM: sixty-one per cent of the time it takes to read a document is one graph walk (personalised PageRank over the frozen lexicon graph), and two sibling functions ask it the identical question about the same word in the same sentence, so 26-40% of the walks inside a document are exact repeats. Memoise the walk PER READER (a pure function of its seed), certify byte-identical situation models, and, because certification needs a reader that reads the same document the same way twice, move the two per-passage category states that still live at module level onto the reader and pin the one remaining read-to-read difference. Measured: 28-39% of the whole read removed; every board row and every solver iteration gets ~2.5x more reads per hour.

**slug:** `sixty_one_percent_of_a_read_is_one_spreading_activation_walk_asked_twice_per_event_memoise_the_walk_per_reader_move_the_per_passage_category_state_onto_the_reader_and_certify_byte_identical_reads`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The walk is the right operation (spreading activation over a content-addressed semantic store: the anterior-temporal hub read; Collins & Loftus 1975); the defect is that it is invoked per EVENT rather than per distinct QUESTION. The brain does not re-run the same spread for the same cue in the same context within one reading; the activation is still there. A per-reader memo of a pure function IS that persistence.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- nothing about the walk changes: not the iteration count, not the damping, not the graph. This is latency, not accuracy; the gate is identity, not a CI.
> **ONE READER = ONE BRAIN (the rule this program is applying, pri 142 P7.2):** plastic or per-passage state lives on the SituationReader instance; module-level assets are read-only. The memo is per reader (it dies with the read); the two per-passage category states move onto the reader too.
> **THE OWNER'S PROGRAM (2026-09-16):** this is step 0 of the brain-structure consolidation (the optimization the owner asked for); pri 143/144/145 follow.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` before writing 'cannot be certified'.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.**

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Reproduce pri 142's cache probe first-hand (`experiments/exp_structure_map_cost_v1.py --cache-probe` and `--state-probe`; `data/exp_structure_map_cost_v1/{cache_probe,state_probe}.json`): the call counts (context_sense_sign 441, sense_posterior_in_context 447, _sense_ppr 672 on 6 GUM test docs), the repeat rate (46 of 116; 7 of 27), the timing (15.11 s -> 9.25 s; 3.18 s -> 2.24 s), and the read-to-read instability on GUM_academic_census.
> 2. **REUSE.** The walk: `hdlab/grounded_semantic_graph.py:88 _ppr(seed_idx, Tt, n, d, iters)` reached only through `:218 _sense_ppr(...)`; the two callers in `hdlab/force_dynamics_valence.py:688 sense_posterior_in_context` and `:718 context_sense_sign` (-> `grounded_semantic_graph.py:414 select_sense_blended`), both driven from `situation_reader._assign_affect -> context_grounded_valence.score_item -> force_dynamics_event_type`; the per-passage category state `hdlab/lexical_categories._INST` / `._REG_GEN` (a generation counter) and `new_document()`; the reader's existing per-read caches (the parse cache pri 137 measured) as the pattern.
> 3. **GENERALIZE.** The memo key is `(tuple(seed_idx), n, damping, iters)` -- the exact seed tuple, never the context words, so a caller that legitimately seeds differently never collides; scope = the reader instance (`self._ppr_memo`), created at `new_document()` / per read, capped and reported.
> 4. **WALL -> DEEPER.** If a document is not read the same way twice WITHOUT the memo, the memo cannot be certified on it: find the state that moves (pri 142 located it inside the per-passage category register machinery: `_INST`/`_REG_GEN` reset correctly yet the situation model differs) and fix it at the reader; do not certify around it.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep; the memo cap is reported, not tuned.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The gate is byte-identical situation models (sentences, entities, events, the full (predicate, agent, patient) tuple set) on every document whose reader is stable; the timing is reported per document with the honest wall clock (contention-checked: paired, alternating, stable pairs only).
> 7. **ADJACENT.** pri 142 (the map; P7.1/P7.2), pri 136 (the per-reader plastic object-file table, landed the same way), pri 143/144/145 (they run after this).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Nothing to sweep.

## 1. THE PROBLEM IN PLAIN LANGUAGE

More than half of the time the reader spends on a document goes into one operation: spreading activation through its dictionary graph to decide which sense of a verb is meant. Two parts of the same module ask that exact question about the same verb in the same sentence, independently, so a quarter to two fifths of those walks are repeats. Remembering the answer within one reading removes 28 to 39 percent of the whole reading time with no change to any answer. To prove 'no change', the reader must read the same document the same way twice; today it does not always, because two pieces of per-passage bookkeeping live at module level instead of on the reader. Move them, pin the one remaining difference, then memoise and certify.

## 2. WHY THIS ONE

It is the top of pri 142's ranked list by measured payoff (61% of a read; 28-39% removed; all nine rows touched), the laptop's read time is the program's bottleneck (every board takes 80 minutes; every solver's cells read the same documents), and it is the optimization the owner asked the consolidation program to include. It also forces the one-reader-one-brain rule through the categories rung, which pri 143/144 need.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

PINNED: spreading activation in a semantic network (Collins & Loftus 1975); the hub read (Patterson, Nestor & Rogers 2007); activation persists across the reading of a passage rather than being recomputed per cue occurrence (priming). OUR-INVENTION: the memo as the representation of persistence; the key; the per-read scope and cap.

## 4. MEASURED vs INFERRED

MEASURED (pri 142, 2026-09-16): `_ppr` = 204.5 s of a 337.4 s profiled read (184.8 s in `scipy.sparse.csr_matvec`, 20,160 products); the two callers build byte-identical context lists (`force_dynamics_valence.py:702` and `:720`) behind the same `< 2 content words` guard and the same `lemmatize_verb`; call counts 441 / 447 / 672 on 6 GUM test docs; repeats 46/116 and 7/27; GUM_letter_marcie3: identical situation model, 28% faster; GUM_academic_census: the reader is not stable read-to-read, 39% faster reported as timing only; per-passage state at module level: `lexical_categories._INST`, `._REG_GEN`; `new_document()` installs a fresh DiscourseRegister (the category clock does NOT leak: checked and refuted).

INFERRED (verify): that moving `_INST`/`_REG_GEN` onto the reader alone makes GUM_academic_census stable read-to-read (pri 142 could not pin the residual); that the memo's hit rate is similar across genres (report per document).

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 142's cache probe: done; reproduce once, do not re-derive the counts.
- pri 136's landing applied the same rule to the object-file table (entity_resolver: the reader owns a deep copy; the module cache is read-only): that is the template for `_INST`/`_REG_GEN`.
- Do not change `_ppr`'s iterations, damping or the graph; do not memoise at module level.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `sed -n 80,100p hdlab/grounded_semantic_graph.py; sed -n 210,230p hdlab/grounded_semantic_graph.py; sed -n 405,420p hdlab/grounded_semantic_graph.py` -- the walk and its two entries.
2. `sed -n 685,735p hdlab/force_dynamics_valence.py` -- the two callers and their context lists.
3. `grep -n "_INST\|_REG_GEN\|def new_document" hdlab/lexical_categories.py hdlab/situation_reader.py` -- the per-passage state.
4. `.venv/Scripts/python.exe experiments/exp_structure_map_cost_v1.py --state-probe` -- the three-read fingerprint (which docs are stable read-to-read today).
5. `git log --oneline -3 -- hdlab/entity_resolver.py` -- the pri 136 landing's per-reader pattern.

## 7. THE BAR (can-fail; the gate is IDENTITY, not a CI)

1. **Read-to-read stability first.** With NO memo, every one of the 6 GUM test documents (and 6 more of other genres) reads to a byte-identical situation model twice in one process with one reader and with two fresh readers; the per-passage category state lives on the reader; the GUM_academic_census residual is pinned to a line and fixed (or, if it is genuine plasticity the brain would have, named as such with the mechanism and excluded from the identity set with the reason).
2. **The memo, per reader.** Keyed by `(tuple(seed_idx), n, damping, iters)`; scoped to the reader/read; capped with the peak entries reported per document.
3. **Identity gate.** On every stable document the memoised read's situation model is BYTE-IDENTICAL (sentences, entities, events, the (predicate, agent, patient) tuple set) to the un-memoised read; any difference is a FAIL.
4. **The poisoned-memo twin**: returning a wrong stored vector on a hit CHANGES the read (else the walk's result is not consumed: a larger finding to report).
5. **The saving, honestly timed**: per document, paired and alternating on a quiet box (stable pairs only; a negative or 3x-variance pair is discarded and said so), with hits/misses per document; the product board's read time before/after (one board run each, or the reader-driven block alone) reported.
6. **The product board byte-identical** on every model row with the memo on.
7. **Witness**: a landing witness pinning the claims (per-reader memo; identity on the stable set; the twin) and the pri 128 tier marker.

## 8. FILES AND ENTRY POINTS

- `hdlab/grounded_semantic_graph.py` (`_ppr` :88, `_sense_ppr` :218, `select_sense_blended` :414).
- `hdlab/force_dynamics_valence.py` (`sense_posterior_in_context` :688, `context_sense_sign` :718).
- `hdlab/situation_reader.py` (`_assign_affect`; `new_document()`; the per-read caches), `hdlab/lexical_categories.py` (`_INST`, `_REG_GEN`).
- `experiments/exp_structure_map_cost_v1.py` (`--cache-probe`, `--state-probe`) and `data/exp_structure_map_cost_v1/`.

Write ONLY: `experiments/exp_ppr_memo_v1.py` (NEW cell: the stability set, the identity gate, the twin, the timing; `get_output_dir` per Q115; `--self-test`), `verification/test_ppr_memo_landing.py` (NEW witness), `notes/problems/<slug>/{SOLVED.md, ppr_memo_patch.diff}` (unified diffs against `hdlab/grounded_semantic_graph.py`, `hdlab/force_dynamics_valence.py`, `hdlab/lexical_categories.py`, `hdlab/situation_reader.py`; never edit hdlab/ directly; patch in BYTES with each file's own line endings). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command; never read `data/corpora/holdout/`.

## DO NOT QUOTE / DO NOT REDO

- Do not quote the 39% on GUM_academic_census as an equivalence (it is a timing until the residual is pinned).
- Do not quote retired figures (`notes/reference_retired_claims_never_requote.md`).
- 19c corpora are informational only (owner 2026-09-06).
