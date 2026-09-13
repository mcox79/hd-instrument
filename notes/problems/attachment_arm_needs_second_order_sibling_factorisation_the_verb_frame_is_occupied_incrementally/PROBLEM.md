---
priority: 16
slug: attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally
status: OPEN
review:
review_text:
---

# PROBLEM: the attachment arm scores every head→dependent arc independently (first-order), so a verb can take two objects, a noun two determiners, and the biggest published label-free lever (sibling second-order factorisation, +13.3 UAS) is absent — the brain attaches each word given what the head has ALREADY taken

**slug:** `attachment_arm_needs_second_order_sibling_factorisation_the_verb_frame_is_occupied_incrementally` — **opened:** 2026-09-12 by strategy after landing the heads rung (`hdlab/attachment_arm.py`) and its semantic-bootstrapping teacher (ledger `notes/SIGNAL_LOSS_LEDGER_affected_entity_chain.md`, entries 2026-09-12 evening).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Name the structure and the computation; replicate the OPERATION, sweep the PARAMETERS (never adopt a number).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — spaCy / any off-the-shelf parser / treebank-trained model at inference is a DEFECT; the UD treebank is a MEASURING instrument only (its trees are never read while learning).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is an extension of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`; sibling arm `hdlab/graded_role_assigner.coarse_roles`). Do NOT mint a new organ; propose the change as a patch + probe, strategy lands it.
> **PLASTIC, NEVER FROZEN:** knowledge = counts in the asset; strengths = one pure function of counts; an online `observe_*` path must exist for anything you add.
> **🧱 WALL-PUSH PROTOCOL:** before writing wall / ceiling / negative, read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md`. A wall = an upstream trace + a stronger brain build, else a SPECIFIC board question.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Cue-based retrieval in sentence comprehension (Lewis & Vasishth 2005; Van Dyke & McElree) retrieves a head whose FEATURES include what it has already taken — an occupied frame slot lowers its activation for another filler of the same type (argument-structure expectation, Tanenhaus/Trueswell; the verb's remaining valence). Constraint integration (MacDonald-Pearlmutter-Seidenberg 1994) is over the WHOLE structure, not independent arcs. State the computation: P(head=h | j, the set of h's other dependents) — a sibling factor.
> 2. **REUSE.** `attachment_arm.SentenceCues` (one cue pass), `strengths_from_arc_counts`, `accrue_sentence`, `head_posterior`; `hdlab/graded_parser.single_root_marginals` (first-order Matrix-Tree); the verb frames (`verb_frames_from_reading`). The field's exact second-order inside–outside is PROJECTIVE (Eisner/McDonald-Pereira 2006 sibling factorisation; Yang-Jiang-Han-Tu COLING 2020 Sib&L-NDMV 67.9 UAS). Decide whether the brain's operation is (a) an exact second-order posterior (projective), or (b) an INCREMENTAL occupancy update (left-to-right attach-and-update, the psycholinguistic regime), and build THAT. Both are admissible; label PINNED/MODEL.
> 3. **GENERALIZE.** Must serve all head classes (verb frames: subject/object/oblique slots; nouns: one determiner, one case marker; conjunctions) — not a verb-only patch.
> 4. **WALL → DEEPER.** If the sibling factor does not move obj/obl, check the INPUT (is the first-order posterior already confident and wrong? then the factor cannot repair it — trace upstream) and the READOUT (MAP vs posterior).
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the occupancy weight / decay / smoothing as operating points.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Measure on UD-EWT test 700 (gold categories; `tools/build_attachment_validities.sentences(TEST, cap=700, maxlen=10**6)`), UAS AND per relation (`uas(..., per_relation=True)`), against the CURRENT asset as the floor run; a scrambled-strengths twin; CI half-width reported. Brain 0.9+; supervised 0.78; label-free field ceiling 0.68; our organ ≈0.54–0.55 expected after tonight's rebuild (read the number from the ledger/asset, do not assume).
> 7. **ADJACENT.** The role competition (`graded_role_assigner.coarse_roles`) will CONSUME the improved head posterior — report which relations improved so strategy can trace the hand-off; do not edit it.
> 8. **COMPLETION BAR.** A sibling/occupancy factor in the attachment arm's knowledge form (counts → strengths, online-observable) that lifts UAS and obj/obl CI-separated over the current asset, beats its twin, with a witness — OR a numbered located negative after steps 1–5.

**(PHASE DIAGRAM.)** Occupancy weight, decay, number of self-teaching rounds, α anchor, β of the semantic teacher are FREE TO SWEEP; a wall "at this config" = move the operating point.
**(FULL-STACK UPSTREAM.)** Categories enter as gold UPOS (stand-in for the reading-induced categories rung); the teacher is co-occurrence + semantic bootstrapping (β=10). If the sibling factor needs a better teacher signal, say exactly which and why.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader decides each word's governor on its own, so it can hang two objects on one verb or two "the"s on one noun. People attach a word knowing what the governor has already taken: once "bit" has an object, a second noun is not another object. This problem builds that memory of "what has already been taken" into the attachment decision.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
It is the single biggest documented label-free lever (+13.3 UAS in the field), it is the brain's operation (retrieval cues include the head's current state), and the heads rung feeds every consumer (roles → entities → board). The earlier mean-field occupancy CUE (−0.01) was a weak implementation (a cue inside a first-order posterior, confounded with function-word constructions); the brain's version is a FACTOR over the structure.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-12):** first-order organ, knowledge-free teacher: UAS 0.4826, obj 0.189, obl 0.118, root 0.413 (core collapsed). With semantic bootstrapping (β=10) on the 1.5k/150 smoke: UAS 0.5399, obj 0.756, obl 0.556, root 0.793, nmod 0.23. Occupancy mean-field cue (probe v18 `--sibling`): −0.01 (confounded). Field: sibling second-order +13.3 (Yang et al. 2020).
- **INFERRED (prove with a number):** a sibling factor lifts obj/obl/nmod by removing double-filling and raises UAS toward 0.6.

## 4. ALREADY TRIED / DO NOT REDO
- Occupancy as a mean-field CUE inside the first-order posterior (probe v18 `--sibling`): −0.01 — do not re-run as built.
- Learning-time length penalty + hard punctuation + curriculum bundle: −0.04 as built (DMV-regime result) — not this problem.
- Raw induced 70-way categories as the attachment input (UAS 0.012) — use gold UPOS as the stand-in.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py`, `tools/build_attachment_validities.py`, `experiments/probe_attachment_competition_v18.py` (the `--sibling` code and why it was confounded), `hdlab/graded_parser.py` (`single_root_marginals`, `chu_liu_edmonds`), `notes/RESEARCH_attachment_organ_spec_2026-09-12.md`, `notes/RESEARCH_sota_parser_anatomy_and_glassbox_recovery_2026-09-12.md` §2–5, `notes/RESEARCH_syntax_acquisition_brain_and_labelfree_parsers_2026-09-12.md`, the ledger's 2026-09-12 attachment entries. Run `python verification/test_attachment_arm.py` first and record its numbers. Check `git log -5 -- hdlab/attachment_arm.py data/frontend_assets/attachment_validities_v1.json` — the asset is being rebuilt tonight (β=10); use whatever is on disk and say which.

## 6. THE BAR (can-fail)
Over the current asset on UD-EWT test 700 with gold categories: UAS and obj+obl recall both up, CI-separated (report half-widths, ≥3 seeds where randomness exists), twin (shuffled strengths) far below, witness green, knowledge in counts with an online observe path — OR a located negative naming exactly which relation class the factor cannot move and why (with the oracle-ceiling probe: what if the sibling set were gold?).

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_second_order_sibling_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (your proposed change to `hdlab/attachment_arm.py` as a diff; do NOT edit hdlab/ or tools/ directly — strategy lands it). Commit PATH-LIMITED (`git commit -m "..." -- <your files>`), never `git add -A`, NEVER push. Cap cores: `OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3`. Never edit `preregs/**` or any `arm_key*` file. Do not spawn sub-agents.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk taggers / any supervised parser at inference or as a teacher. Do NOT read the treebank's trees while learning (they are the measuring instrument). Do NOT call 0.68 a ceiling — it is the field's label-free record, and the brain is at 0.9+.
