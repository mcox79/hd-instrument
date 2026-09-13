---
priority: 97
slug: the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots
status: OPEN
review:
review_text:
---

# PROBLEM: the governor picks the sentence's main word right 71 times in 100; in most misses it crowns the SUBJECT before the predicate arrives, and its own cue activations rate the true main word as a non-root (about −5) — the decode is faithful to bad activations, so the missing piece is CUE KNOWLEDGE about what makes a word the main assertion (finiteness, copular predication, clause-initial subordination), not the decoder

**slug:** `the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots` — **opened:** 2026-09-13 by strategy from the main-word anatomy of the in-order governor (698 root misses of 692 test sentences: predicted root LEFT of the true one in 120, the gold relation of the crowned word nsubj 47 / advcl 28 / nmod 26; gold roots missed VERB 54, ADJ 35, NOUN 30, NUM 24; takeover margin at the predicate's arrival −13.4 on average; re-teaching the validity table under the in-order decode did NOT move root: 0.716 vs 0.713).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** What tells a reader which word carries the main assertion? Finiteness (a tensed verb or an auxiliary marks the predicate that asserts), copular predication (in "the vote is confusing" the assertion is carried by "confusing"; the copula is a functional carrier), and clause-initial subordination ("When/If/What if ..." opens a clause that hangs on a later one, so its verb is NOT the root). These are cue-competition inputs (Bates & MacWhinney): the root decision is a competition among finite predicates, with subordinators and copulas as cues with learned validities -- not a per-word root prior over categories.
> 2. **REUSE.** `hdlab/attachment_arm.py`: the ROOT decision today = `root_cfg_id[cat]` (a per-category root strength) + the cues that exist for ordinary arcs; `SentenceCues` (one cue pass), `strengths_from_arc_counts` / `accrue_sentence` (counts -> strengths), `function_word_arcs` (the AUX/copula/subordinator frames), `incremental_tree` (root reanalysis exists: a later word may take the root arc over; it loses on activations, not on mechanics), `hold_expectation` (per category x verb-seen x subordinator-pending). The category organ gives AUX/SCONJ/VERB posteriors (`hdlab/lexical_categories`).
> 3. **GENERALIZE.** Verbal, adjectival and nominal predicates; questions with inversion ("Is that a money maker?"); imperatives; fragments (NUM/PROPN roots in lists and headlines are legitimate).
> 4. **WALL -> DEEPER.** If root recall does not move, split the misses by gold-root category and by "subordinator present"; a residual dominated by fragments/headlines is a population fact, not a mechanism failure -- report it as such with counts.
> 5. **OPTIMIZE BY EXACT REPLICATION;** cue validities are LEARNED from the teacher posterior like every other cue (add the cue values, rebuild); sweep smoothing only.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700, gold categories, BOTH decodes (`experiments/_diag_decode_incremental.py`), against the CURRENT live asset (in-order decode: UAS 0.6125, root 0.721, nsubj 0.763, ccomp 0.603, advcl 0.321; search: root 0.747); report root, nsubj, ccomp, advcl, xcomp; UAS not down; twin (shuffled cue values) at baseline; also the LIVE-chain number under the organ's own categories (`experiments/probe_heads_under_category_posterior_v1.py`).
> 7. **ADJACENT.** The main word feeds every event read (predicate recall, roles, state); coordinated main clauses (pri 95 landed) share the root decision; do not edit consumers.
> 8. **COMPLETION BAR.** Root recall up CI-separated under both decodes with nsubj/ccomp/advcl not down and UAS not down; knowledge in counts with an online observe path; witness green -- OR a numbered located negative (e.g. the residual is fragments) with counts.

**(PHASE DIAGRAM.)** Cue smoothing, the teacher's rounds, the hold offset of the in-order decode are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Categories: the live count organ (AUX 0.96+, SCONJ 0.733 on test -- the subordinator tag is the weakest input; say if it limits you). Governor: the attachment arm, in-order decode, live asset taught with semantic bootstrapping + parallel structure. Do not touch the decoder unless the activations are shown correct and the decode wrong.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader has to decide which word a sentence is really about, its main statement. It gets that right about 7 times in 10. When it fails, it usually crowns the subject noun before the real predicate has arrived, and when the predicate does arrive the reader's own cues still say it is a poor main word (adjective and noun predicates, and clauses that start with "when" or "what if" are the typical cases). People use simple signals: a tensed verb or "is" marks the statement; "when" at the start marks a clause that depends on another. We want those signals as learned cues in the same competition the reader already uses.

## 2. WHY THIS ONE
The main word is the top of every event read; the in-order governor beats the search on objects and modifiers but trails it on the main word (0.721 vs 0.747); the residual is DIAGNOSED as cue knowledge (activations −5.4 for the true root arc), and neither the decode nor a re-taught table moved it.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-13):** root 0.721 (in-order) / 0.747 (search); 32 subject-crowned cases: mean takeover margin −13.4, gold root arc −5.4, gold predicate->subject −7.7, subject root arc +0.24; re-teach under the in-order decode: root 0.716 (null); clitic copulas added to the convention: root 0.706 -> 0.713.
- **INFERRED (prove with a number):** finiteness / copular-predication / subordination cues with learned validities lift root by 3+ points under both decodes and pull nsubj with it.

## 4. ALREADY TRIED / DO NOT REDO
Root as a sentence-final wrap-up decision (refuted: root 0.56-0.66); root reanalysis while reading (landed; helps little because activations are wrong); re-teaching the table under the in-order decode (null); the copular convention (landed; keep).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py` (cues, root config, `function_word_arcs`, teacher, decode), `tools/build_attachment_validities.py`, `experiments/_diag_decode_incremental.py`, `notes/OVERNIGHT_PLAN_2026-09-12.md` (entries 12:18 and 12:22 local), `notes/BRAIN_MATH_REFERENCE.md` (attachment rows), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_main_assertion_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (do NOT edit hdlab/ or tools/ directly -- strategy lands it). Commit PATH-LIMITED, never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser at inference or as a teacher. Do NOT read the treebank's trees while learning. Do NOT call 0.68 a ceiling.
