---
priority: 112
slug: the_category_organs_passage_register_is_written_by_every_consumers_re_tag_out_of_order_so_a_read_is_not_repeatable_feed_it_once_in_order_and_read_it_as_of_the_sentence
status: OPEN
review:
review_text:
---

# PROBLEM: the category organ's passage register (pri 104's entity file cards, the next-mention prior) is written by EVERY call to `tag` / `posterior`, and five different consumers re-tag the same sentence at five different moments -- so the register sees a sentence many times, out of order, its content depends on which consumer's memo happened to hit, and the same document read twice in one process yields different events (2 of 12 LitBank documents; the `test_coref_graded_pick_landing` W3a witness is red on exactly this).

**slug:** `the_category_organs_passage_register_is_written_by_every_consumers_re_tag_out_of_order_so_a_read_is_not_repeatable_feed_it_once_in_order_and_read_it_as_of_the_sentence` -- **opened:** 2026-09-14 by strategy after a five-step bisect (data/hook_state/diag_w3a4..9.log; ledger 2026-09-14 13:05).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** A passage is read ONCE, in order; every later process reads what the comprehender knew at that point. Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL.** A register that is fed by whichever consumer happens to re-tag a sentence, whenever, is not a discourse model; it is an accident of call order.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** the register belongs to the category organ (`hdlab/lexical_categories.py`, `DiscourseRegister`, `new_document`, `_reg.observe` at ~895, `sent_no` at ~1056); the READER (`hdlab/situation_reader.py::read`) is the one comprehender that advances the passage. Do not add a second register or a per-consumer copy.
> **ORGANS TAKE DATA IN ORDER (owner 09-13):** what the organ knows at sentence k is the cards filed by sentences 1..k-1, nothing later.
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** The measured mechanism (diag_w3a9, document 1023_bleak_house, sentence 59 'shirking and sharking in all their many varieties have been sown broadcast ...'): the organ's `posterior` for that sentence was requested at register clock 60 (referent_per_np:122), 118 (situation_reader:4397 via referent_per_np:149), 168 (the reader's affect path, `_affect_pos_cached` -> frontend.tag), 228 (coref:216 / space_reader:764) and 255 (situation_reader:2679) in the FIRST read, and returned FOUR DIFFERENT posterior vectors for token 0 (P(first class) 4.3e-2 / 1.3e-3 / 9.3e-4 / 1.3e-2) because the file cards differed each time; every call also FILED the sentence again (observe) and advanced the clock. In the SECOND read of the same document by a fresh reader the affect-path calls were served from the process-global `@lru_cache` `_affect_pos_cached` (situation_reader ~863; its docstring premise 'tag() is a PURE deterministic function of the token list' has been false since the entity-feedback arm landed), so the register received fewer writes, its clock at the same points read 178 / 205 instead of 228 / 255, and the sentence-initial gerund 'shirking' was decided a predicate in read 1 (event with patient 'varieties') and not in read 2: 236 vs 235 events. The brain-foundational form: (a) the reader feeds the register ONCE per sentence, IN ORDER, at the point it settles that sentence (explicit `observe_sentence` / an `observe=True` argument used at ONE call site), and every other call to `tag` / `posterior` / `tag_with_posterior` is a READ that files nothing; (b) a read for sentence k sees the cards AS OF k (cards carry their filing time; activation sums observations with time < k -- the ACT-R recency clock the register already keeps), so a consumer that asks late still gets what the comprehender knew at that sentence; (c) no process-global memo of organ output that depends on the register (per-read memos only, or key them on the register's state).
> 2. **REUSE.** `DiscourseRegister` (`h`, `sent_no`, `symbol`, `observe`), `new_document`, the entity-feedback arm (ENT_KAPPA / log_entc), the reader's per-read memo `_read_parse_cache` / `_cached_tag` / `_cached_tag_matrix`, `hdlab/frontend.py::Tagger`, the direct frontend callers (`hdlab/referent_per_np.py:122,149`, `hdlab/coref.py:216`, `hdlab/space_reader.py:764`, `situation_reader.py:2679,4397`, `_affect_pos_cached`), pri 104's SOLVED.md (the arm's measured value: +0.117 span F1 through the wire) and its cell `experiments/exp_entity_to_category_prior_v1.py`.
> 3. **GENERALIZE.** Enumerate EVERY caller of the category organ on the live read path (grep `tag_with_posterior(`, `.posterior(`, `.tag(` across hdlab/ and the board arms) and classify each: the one in-order feeder, or a read. Any other process-global memo of an organ output on the read path (grep `lru_cache` in hdlab/situation_reader.py and the organs it calls) gets the same treatment.
> 4. **WALL -> DEEPER.** If as-of-k reads change the entity-feedback arm's measured gain, that is the TRUE in-order number (the polluted register was reading the future); report it, do not restore the pollution.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the recency decay only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Repeatability: the same document read twice by fresh readers in one process is byte-identical on every field (all 12 LitBank witness docs; W3a green); the category organ's tag accuracy on GUM / UD-EWT test with the register fed once in order vs the current path; the board's 7 dimensions (`experiments/exp_situation_model_qa_modern_v1.py --run`, HDLAB_EXP_NAME set) before / after; the entity-feedback arm's own instrument (pri 104's cell) under as-of-k reads; read cost.
> 7. **ADJACENT.** pri 110 (the predicate slot reads the same posterior); pri 109 (the gold-free rows read the organ through gum_coref's loader, which tags each document once -- check whether it calls new_document); the two-pass structure of `read()` (referent_per_np's source pass tags before the reader's own pass).
> 8. **COMPLETION BAR.** Repeatability byte-identical (12/12 docs; W3a green) with the register FED ONCE IN ORDER and READ AS OF THE SENTENCE, board not down on any dimension CI-separated (a move traced to the un-polluted register is reported as the true number), the entity-feedback arm still measured with its own instrument, every live caller classified, no process-global memo of register-dependent output -- OR a numbered located negative naming the consumer that cannot read as-of-k and why.

**(PHASE DIAGRAM.)** The recency decay and the entity-prior strength (ENT_KAPPA, ENT_THETA_DOC) are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens -> categories (this register is INSIDE the categories rung) -> every consumer below.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The word-category organ keeps a running file of the people and things met so far in a passage, and uses it to guess whether a new word is a name. Today that file is written by every part of the system that happens to ask for a word's category, in whatever order those parts run, so the same sentence gets filed five times and the file's contents depend on accidents of caching. The visible symptom: reading the same story twice in one session gives a different list of events. The fix is to let the reader file each sentence once, in order, and let everything else read the file as it stood at that sentence.

## 2. WHY THIS ONE
A repeatability defect at the top of the chain (the categories rung), located to the mechanism with call stacks and clock values; it is the cause of a red witness and it silently shapes every number measured through the live reader today.

## 3. MEASURED vs INFERRED
MEASURED: the call log above (five requests, four distinct posteriors, two absent in the second read), events 236 vs 235, 2 of 12 documents differ, tags/heads in the reader's own memo identical between reads. INFERRED: the size of the board movement when the register is fed once in order.

## 4. ALREADY TRIED / DO NOT REDO
Clearing the affect / force-dynamics / predicate-argument / frame-induction caches between reads (no effect; diag_w3a5); clearing nothing and reading with a fresh reader (differs); the pre-pri-109 bisect (the harness denied placing a copy of the old reader, so 'did this predate pri 109' is unanswered -- the mechanism above predates it by construction: the register landed with pri 104 on 2026-09-14 early morning).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read in full: `hdlab/lexical_categories.py` (DiscourseRegister, new_document, observe at ~895, sent_no at ~1056, the entity-prior read at ~890), `hdlab/situation_reader.py` `read()` (the new_document call at ~4381, `_cached_tag`, `_cached_tag_matrix`, `_affect_pos_cached` at ~863), `hdlab/frontend.py`, the five direct callers listed in checklist item 1, `verification/test_coref_graded_pick_landing.py` (W3), `data/hook_state/diag_w3a9.log`, pri 104's SOLVED.md.

## 6. THE BAR (can-fail)
See checklist item 8. Floors: the current register path; twin: the register fed in a random sentence order. Paired bootstrap over documents / sentences; the board run before and after.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_passage_register_in_order_v1.py` (your cell), `notes/problems/<slug>/{SOLVED.md, passage_register_patch.diff}` (unified diffs against `hdlab/lexical_categories.py`, `hdlab/situation_reader.py`, `hdlab/frontend.py` and the direct callers; never edit hdlab/ or tools/ directly), and any NEW asset under `data/hook_state/`.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers (LitBank) are informational only; the repeatability bar is not a 19c number.
