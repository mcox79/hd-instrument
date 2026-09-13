---
priority: 95
slug: coordination_is_parallel_structure_not_a_convention_the_coordinator_predicts_a_like_conjunct
status: OPEN
review:
review_text:
---

# PROBLEM: coordination ("X and Y") is the attachment arm's worst structural class (conj recall 0.30 on UD-EWT test; 3.4% of tokens) and every convention rule for it was REFUTED — the brain treats a coordinator as a PREDICTION of a parallel phrase that shares the first conjunct's slot, and that structure is what is missing

**slug:** `coordination_is_parallel_structure_not_a_convention_the_coordinator_predicts_a_like_conjunct` — **opened:** 2026-09-13 by strategy while landing the INCREMENTAL arm of the attachment organ (`hdlab/attachment_arm.py` `incremental_tree`, `HDLAB_ARM_DECODE=incr`).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** How does the brain read "the man and the woman saw the dog"? PARALLELISM: the coordinator predicts a second phrase of the SAME kind as the phrase just closed (Frazier, Munn, Taft & Clifton 2000 parallel-structure facilitation; Levy 2008 prediction), and the two conjuncts SHARE one slot of the governing head (one subject slot filled by a plural set). Retrieval for the second conjunct is cue-based (Lewis & Vasishth 2005): the cue is "a like-category open phrase before the coordinator". Name the structure; then state the computation in the organ's terms (cues -> learned validities -> competition).
> 2. **REUSE.** `attachment_arm.SentenceCues` (one cue pass; cues are discrete values per arc with learned validities), `strengths_from_arc_counts` / `accrue_sentence` (the counts -> strengths path), `arc_scores` (vectorised readout; `arc_scores_reference` is the oracle), `decode` (map1 = whole-sentence search; incr = incremental commitment with `hold_expectation`), `punct_convention` (the convention layer's pattern). UD's convention: the right conjunct depends on the LEFT conjunct (`conj`), the coordinator on the RIGHT conjunct (`cc`) — that convention is the measuring instrument, not the brain claim.
> 3. **GENERALIZE.** Nouns, verbs, adjectives, clauses, prepositional phrases all coordinate; a noun-only patch fails the bar. The same prediction must work in the incremental arm (the coordinator's HOLD expectation = "a like phrase is coming"; `hold_expectation` is per category + verb-seen today — propose the coordination context as the next conditioning of that expectation).
> 4. **WALL -> DEEPER.** If conj does not move: check whether the first conjunct's own attachment is already wrong (then the conjunct inherits the error — trace to the first conjunct's cue), and whether the learned validity for the new cue is flat (then the teacher never saw the contrast — say which teacher signal is missing).
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the cue's smoothing / the prediction strength as operating points; never adopt a number.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700, gold categories (`tools/build_attachment_validities.sentences(TEST, cap=700, maxlen=10**6)`), UAS AND per relation under BOTH decodes (`experiments/_diag_decode_incremental.py` shows the exact loop; add `cc`), against the CURRENT asset `data/frontend_assets/attachment_validities_v1.json` (map1 0.6034; conj 0.300; incr beam 8 with the learned hold ties it). Also the LIVE-chain number under the organ's own categories (`experiments/probe_heads_under_category_posterior_v1.py`).
> 7. **ADJACENT.** Coordinated subjects/objects feed coreference and who-did-what (a conjoined agent is one plural entity) — report which downstream reads would change; do not edit them.
> 8. **COMPLETION BAR.** A coordination cue/prediction in the attachment arm's knowledge form (counts -> strengths, online-observable) that lifts conj (and cc) recall CI-separated over the current asset under both decodes with UAS not down, twin (shuffled strengths) far below, witness green — OR a numbered located negative naming the upstream cause.

**(PHASE DIAGRAM.)** Cue smoothing, prediction strength, the beam width of the incremental decode, the teacher's rounds are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Categories enter as gold UPOS for the measurement (the live organ is the count-based tagger, 0.926); the teacher is semantic bootstrapping v2 + the read-time plausibility cue; the decode is map1 (default) or incr. If coordination needs a teacher signal the current one lacks, say exactly which.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the reader meets "and", it has to decide what is being joined to what. Today it treats the word after "and" like any other word and guesses its governor from the usual cues, so it gets 30 in 100 of these links right. People do something specific: hearing "and", they expect a phrase of the same kind as the one they just finished, and they treat the pair as one unit filling one slot. We want that expectation and that sharing built into the governor organ.

## 2. WHY THIS ONE
conj is 3.4% of all tokens and the single worst structural relation; a wrong conjunct drags its whole phrase with it; coordinated subjects and objects are one plural participant for coreference and who-did-what. Conventions were tried and REFUTED with numbers (below): this needs the structural account.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-13, UD-EWT test 700, gold categories, current asset):** conj recall 0.300 (map1), 0.296–0.364 (incr variants); UAS 0.6034. On GOLD trees: "right conjunct's head = nearest preceding same-class word before the coordinator" 0.538; "top of the left chain of the same class" 0.589 — too weak for a convention rule (best case +0.8 UAS with the arm's own tree).
- **INFERRED (prove with a number):** a predictive like-conjunct cue with learned validity lifts conj well above 0.5 and cc with it.

## 4. ALREADY TRIED / DO NOT REDO
- The two conventions above (measured on gold trees; not landed).
- Occupancy at decode (`HDLAB_ARM_OCCUPANCY`, refuted: UAS −0.004, obj −0.07) — a different problem (pri 93, re-scoped to roles).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py` (cues, teacher, `arc_scores`, `decode`, `incremental_tree`, `hold_expectation`, `punct_convention`), `tools/build_attachment_validities.py`, `experiments/_diag_decode_incremental.py`, `notes/BRAIN_MATH_REFERENCE.md` (attachment rows), `notes/OVERNIGHT_PLAN_2026-09-12.md` (log entries 06:55 and 10:15 local), `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.

## 6. THE BAR (can-fail)
Over the current asset on UD-EWT test 700 with gold categories, under BOTH decodes: conj and cc recall up CI-separated (report half-widths; ≥3 seeds where randomness exists), UAS not down, twin (shuffled strengths) far below, witness green, knowledge in counts with an online observe path. A rigorous negative is a PASS only if what failed was the brain's mechanism, faithfully built, with the number.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_coordination_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (your proposed change to `hdlab/attachment_arm.py` as a diff; do NOT edit hdlab/ or tools/ directly — strategy lands it). Commit PATH-LIMITED (`git commit -m "..." -- <your files>`), never push, never `git add -A`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser at inference or as a teacher. Do NOT read the treebank's trees while learning (they are the measuring instrument). Do NOT call 0.68 a ceiling — it is the field's label-free record, and the brain is at 0.9+.
