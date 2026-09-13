---
priority: 17
slug: pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading
status: OPEN
review:
review_text:
---

# PROBLEM: prepositional-phrase attachment (does "with the telescope" modify the verb or the noun?) is the attachment arm's worst comprehension-relevant class (obl ≈0.5, nmod ≈0.2) because the arm has no LEXICAL association between the governor and the preposition/its noun — the brain learns it from the cases that are unambiguous

**slug:** `pp_attachment_obl_nmod_is_the_worst_comprehension_relevant_class_mine_unambiguous_cases_from_reading` — **opened:** 2026-09-12 by strategy from the error anatomy of the landed heads rung (`hdlab/attachment_arm.py`; ledger 2026-09-12).

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — no spaCy / off-the-shelf parser / treebank-trained model at inference or as a teacher; the UD treebank is the measuring instrument only. Offline FOUNDATION assets built from reading are admissible; say exactly what they were built with.
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is a CUE of the ATTACHMENT arm of the Competition-Model organ (`hdlab/attachment_arm.py`), learned by the arm's own plastic counts. Do NOT mint a new organ or a separate PP classifier.
> **PLASTIC, NEVER FROZEN:** knowledge = counts; strengths = one pure function of counts; an online observe path.
> **🧱 WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Constraint-based integration of LEXICAL co-occurrence knowledge in ambiguity resolution (MacDonald 1994; Spivey-Knowlton & Sedivy 1995: verb-bias × definiteness; Altmann & Steedman 1988 referential context). The learner acquires verb–preposition and noun–preposition association from experience where attachment is NOT ambiguous (no competing attachment site) and generalises it to the ambiguous cases — Ratnaparkhi 1998 (81.9% from raw text vs 70.4 baseline; Hindle & Rooth 1993 lexical association). State the computation: contrast log-odds(attach to verb | verb, prep) vs (attach to noun | noun, prep), learned only from confident cases.
> 2. **REUSE.** The arm's posterior (`attachment_arm.head_posterior`) gives the MARGIN of every arc: unambiguous = high-margin. `SentenceCues.cues(j,h)` already carries `frame` (per-lemma transitivity) — the PP association is a sibling cue in the same knowledge form (`counts["cues"][cue]["config|value"]`). The reading corpus: `data/corpora/simplewiki/simplewiki_clean_v1.txt` (64 MB); categories via the substrate's tagger (`hdlab/pos_tagger` is NOT_BF supervised — say so; gold UPOS on UD-EWT train sentences is the stand-in the rest of the rung uses). Consolidate: the spec (`RESEARCH_attachment_organ_spec_2026-09-12.md`) asks for ONE grown argument-frame lexicon instead of three per-lemma tables — design the PP association to live in that lexicon.
> 3. **GENERALIZE.** Verb-attached obl AND noun-attached nmod; prepositions beyond of/with/in; back off from lexical item to the verb's class / the noun's supersense (the typed selectional preference organ, `hdlab/typed_selectional_preference.py`, already gives Resnik class association — reuse for the noun side).
> 4. **WALL → DEEPER.** If association does not move obl/nmod: check the INPUT (is the preposition's own head — the `case` convention — right? the convention layer handles it), the candidate set (is the correct site even retrievable under locality decay?), and the READOUT.
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep the margin threshold for "unambiguous", the shrinkage m, the backoff weights.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** UD-EWT test 700, gold categories, per relation (`tools/build_attachment_validities.uas(..., per_relation=True)`): obl, nmod, and UAS over the CURRENT asset as the floor run, twin (verb-shuffled association), CI half-width. PP set reference: Ratnaparkhi baseline 70.4 / mined 81.9 / supervised 84.5.
> 7. **ADJACENT.** The role competition reads OBL vs OBJ from heads + prep cues (`graded_role_assigner.coarse_roles`) — report which cases flip so strategy traces the hand-off; do not edit it.
> 8. **COMPLETION BAR.** A PP-association cue in the attachment arm's knowledge form, learned from the arm's own unambiguous cases on raw reading (no treebank trees), lifting obl+nmod CI-separated over the current asset, beating its twin, witnessed — OR a numbered located negative with the oracle probe (gold association → how much would it buy?).

**(PHASE DIAGRAM.)** Margin threshold, reading volume, shrinkage, lexical→class backoff, locality decay are FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** The categories are a supervised stand-in (gold UPOS) until the reading-induced categories rung hands down a usable inventory; the teacher is co-occurrence + semantic bootstrapping (β=10). Say what your cue needs from upstream.

## 1. THE PROBLEM IN PLAIN LANGUAGE
"She saw the man with the telescope" — who has the telescope? The reader currently guesses mostly by distance and gets about half of these wrong. People decide from experience: "saw … with a telescope" is a familiar pairing, "man with a telescope" less so, learned from thousands of sentences where there was only one possible reading. This problem builds that experience into the reader from plain text.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
obl/nmod is the largest comprehension-relevant loss of the heads rung after the core was restored; the brain's fix is lexical association learned from unambiguous experience (documented at +11 points from raw text), and it is a cue inside the existing organ's knowledge form, not a new component.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-12):** knowledge-free organ: obl 0.118, nmod 0.188; with semantic bootstrapping (β=10, smoke 1.5k/150): obl 0.556, nmod 0.23, UAS 0.5399; a lexical cue at 6k sentences was too sparse (−0.02) — that was an UNFILTERED lexical cue, not an unambiguous-case-mined association.
- **INFERRED:** mining high-margin cases over ~700k simplewiki sentences gives a dense association that lifts obl/nmod by ≥0.05 each.

## 4. ALREADY TRIED / DO NOT REDO
- Unfiltered lexical head–dependent cue at 6k sentences (−0.02): sparse — do not repeat without the unambiguous-case filter and class backoff.
- The hand-authored universal prior (kept OUT of the organ) — do not re-add.
- Induced constructions by n-grams / transition dips (negative) — not this problem.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/attachment_arm.py`, `tools/build_attachment_validities.py`, `hdlab/typed_selectional_preference.py` (and its store provenance note), `notes/RESEARCH_attachment_organ_spec_2026-09-12.md` (§ one grown lexicon), `notes/RESEARCH_sota_parser_anatomy_and_glassbox_recovery_2026-09-12.md` §3–4, the ledger's 2026-09-12 attachment entries; run `python verification/test_attachment_arm.py` and record. The asset is being rebuilt tonight (β=10) — use what is on disk and say which (`git log -3 -- data/frontend_assets/attachment_validities_v1.json`).

## 6. THE BAR (can-fail)
obl and nmod recall CI-separated above the current asset on UD-EWT test 700, UAS not down, twin far below, knowledge in counts with an online observe path, witness green — OR a located negative with the oracle-association probe number.

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_attachment_pp_association_unambiguous_mining_v1.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, `notes/problems/<slug>/attachment_arm_patch.diff` (proposed change to `hdlab/attachment_arm.py`; do NOT edit hdlab/ or tools/ directly — strategy lands it), and any mined asset under `data/exp_attachment_pp_association_unambiguous_mining_v1/`. Commit PATH-LIMITED (`git commit -m "..." -- <your files>`), never `git add -A`, NEVER push. Cap cores: `OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3`. Never edit `preregs/**` or any `arm_key*` file. Do not spawn sub-agents. Mining 700k sentences with the unvectorised arm is slow — mine a capped slice first (50k), measure, then scale only if the curve is rising.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / nltk / any supervised parser to mine the cases (the arm's own posterior is the miner). Do NOT read treebank trees while learning.
