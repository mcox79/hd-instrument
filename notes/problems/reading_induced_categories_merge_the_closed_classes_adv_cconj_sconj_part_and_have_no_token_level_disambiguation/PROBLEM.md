---
priority: 15
slug: reading_induced_categories_merge_the_closed_classes_adv_cconj_sconj_part_and_have_no_token_level_disambiguation
status: OPEN
review:
review_text:
---

# PROBLEM: the top rung of the reading chain — lexical categories induced from reading — reaches 0.745 type-level but merges the closed classes (ADV/CCONJ/SCONJ/PART ≈ 0 recall; CCONJ merged with ADP) and reads each word TYPE as one category, so the heads rung downstream still runs on a supervised stand-in

**slug:** `reading_induced_categories_merge_the_closed_classes_adv_cconj_sconj_part_and_have_no_token_level_disambiguation` — **opened:** 2026-09-12 by strategy (top-of-chain pass; `experiments/exp_reading_induced_categories_v1.py`, `notes/RESEARCH_reading_induced_categories_2026-09-12.md`, brain-math reference row "Lexical-category ACQUISITION").

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** Replicate the OPERATION, sweep the PARAMETERS.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** — no supervised tagger, no nltk/spaCy, no gold labels in learning; UD tags are the measuring instrument only (many-to-one / V-measure).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** this is the CATEGORY arm (distributional substitution classes; Harris / Mintz frequent frames / Redington-Chater-Finch; competitive Hebbian learning) — extend `exp_reading_induced_categories_v1` into the organ to be landed, do not mint a parallel one.
> **PLASTIC, NEVER FROZEN:** the `OnlineCategoryLearner` path exists (0.67–0.69 @20k) — whatever you add must have an online form.
> **🧱 WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.
> **A rigorous negative is a PASS** only if what failed was the brain's mechanism, faithfully built, with the number.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Children separate function words EARLY by (a) prosody/phonology (short, unstressed, high-frequency, reduced vowels — Shi, Werker & Morgan 1999; Hochmann, Endress & Mehler 2010: frequency alone makes a "function-word" class), (b) frequent FRAMES (Mintz 2003: the frame "the_X_is" categorises X; frames around function words are the most informative), (c) distributional DIRECTIONALITY (ADP/SCONJ take a right-complement, CCONJ sits between parallel units, ADV attaches freely, PART is bound to a verb). Token-level: the SAME word in different frames is categorised by its current frame (Redington et al.; Elman 1990 context-sensitive codes). State each as a computation over counts.
> 2. **REUSE.** `accrue_counts` (directional frame counts), `ppmi_svd`, exposure-weighted k-means (Rumelhart-Zipser), the form classes and suffix form cue, `token_readout_model`/`token_posterior`, `OnlineCategoryLearner`. Reuse the PROSODIC proxy already in the chain (punctuation as written prosody; word length/frequency as the reduced-form proxy).
> 3. **GENERALIZE.** The fix must separate all four closed classes and give a token-level posterior at 100% coverage; it must not break the open classes (PRON .87 NOUN .85 VERB .78 now).
> 4. **WALL → DEEPER.** If CCONJ still merges with ADP: check the INPUT (is the frame window symmetric? coordination needs a "parallel-units" cue — the two neighbours share a category), and the READOUT (many-to-one hides a class that exists but is small — report per-class recall AND V-measure).
> 5. **OPTIMIZE BY EXACT REPLICATION;** sweep k, window, frequency split, frame set as operating points.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Measure as the v1 probe does (UD-EWT gold UPOS as the instrument: type-level many-to-one, token-level graded readout, V-measure, per-class recall) on the same 1M-line simplewiki slice; floors: majority 0.141, shuffled twin 0.335; current 0.745 / 0.722 (k=68+2), 0.758 / 0.728 (k=136). THEN the hand-off test that matters: feed your token-level categories (collapsed as probe v15 does) to the attachment competition (`hdlab/attachment_arm.py` via `tools/build_attachment_validities.py` with your categories in place of UPOS on a 1.5k/150 smoke) and report UAS vs gold-UPOS (0.208 vs 0.276 was the v15 number at 17 classes).
> 7. **ADJACENT.** `hdlab/pos_tagger` (NOT_BF supervised perceptron) and `hdlab/crf_tagger` are the stand-ins to be REPLACED by this organ — do not edit them; report what the replacement would cost.
> 8. **COMPLETION BAR.** Closed classes separated (ADV/CCONJ/SCONJ/PART recall each > 0.4 at k ≤ 136 without losing the open classes), token-level posterior at 100% coverage, online form, and the hand-off smoke to the attachment competition reported — OR a numbered located negative after steps 1–5.

**(PHASE DIAGRAM.)** k, window, exposure weighting, frequency/length split for the function-word stratum, frame vocabulary size, online learning rate — FREE TO SWEEP.
**(FULL-STACK UPSTREAM.)** Tokens come from the regex tokenizer (BF-acceptable segmentation stand-in); everything downstream (heads → roles → entities → board) runs on supervised UPOS until this rung hands down a usable inventory — this IS the top of the chain.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader learns word kinds (noun-like, verb-like, "the"-like) from plain reading and gets three quarters of words right, but it cannot tell "and", "because", "very" and "to" apart from prepositions, and it gives every word one kind even when the same word works differently in different sentences. Children sort the little words first, by how short and frequent they are and by the frames they sit in. This problem builds that.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
It is the TOP of the reading chain (owner: a non-brain-foundational top can make downstream gains useless). Every rung below still runs on a supervised tagger because this rung's inventory is not usable yet; the closed classes are exactly what the heads rung's constructions and convention layer key on.

## 3. MEASURED vs INFERRED
- **MEASURED (2026-09-12):** 1M lines, k=68+2 form classes, exposure weighting, form cue: type-level 0.745, token-level 0.722 at 100% coverage, V 0.592; per class PRON .87 NOUN .85 AUX .83 ADP .83 DET .85 ADJ .80 VERB .78 PART .74, ADV/CCONJ/SCONJ ≈ 0; k=136: 0.758/0.728, SCONJ .55, ADV .26, CCONJ still merged with ADP. Volume saturates early; Ward hierarchical refuted (0.395 = twin). Hand-off (v15): 70-way inventory unusable by the attachment learner (UAS 0.012); 17-way collapse 0.208 vs gold 0.276.
- **INFERRED:** a function-word stratum (frequency/length) + frame-conditioned token readout separates the closed classes and makes the inventory usable downstream.

## 4. ALREADY TRIED / DO NOT REDO
- Ward/agglomerative clustering (no brain story; 0.395). Raw induced category as a role cue (null). Volume beyond 1M lines (flat).
- Do NOT use nltk/spaCy taggers or UD tags in learning.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `experiments/exp_reading_induced_categories_v1.py`, `notes/RESEARCH_reading_induced_categories_2026-09-12.md`, the brain-math reference row (`notes/BRAIN_MATH_REFERENCE.md`, "Lexical-category ACQUISITION"), `experiments/probe_attachment_competition_v15*.py` (the hand-off test), `hdlab/attachment_arm.py` and **`notes/SIGNAL_FLOW_MAP.md` §2e — the heads rung's EXACT signal requirement from your categories, consumer by consumer (participant class, predicate class separate from auxiliaries, form classes, NP-run classes, and the closed classes ADP/AUX/SCONJ/CCONJ/PART/DET each separately = the open gap), plus the hand-off test that decides 'usable'.** Assets: `data/frontend_assets/induced_categories_simplewiki_1m_k68.json`, `data/exp_reading_induced_categories_v1/`. Corpus: `data/corpora/simplewiki/simplewiki_clean_v1.txt`.

## 6. THE BAR (can-fail)
Closed-class separation with open classes held, token-level posterior, online form, CI-separated over the current 0.745/0.722 on the same instrument with the twin reported, AND the attachment hand-off smoke number — OR a located negative naming which class the distributional signal cannot separate and the oracle probe (what if the function-word stratum were gold?).

## 7. FILES AND ENTRY POINTS
Write ONLY: `experiments/exp_reading_induced_categories_v2.py` (must use `experiments._seed_checkpoint.get_output_dir`), `notes/problems/<slug>/SOLVED.md`, assets under `data/exp_reading_induced_categories_v2/`. Do NOT edit hdlab/ or tools/ — propose landing changes in SOLVED.md; strategy lands. Commit PATH-LIMITED (`git commit -m "..." -- <your files>`), never `git add -A`, NEVER push. Cap cores: `OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3`. Never edit `preregs/**` or any `arm_key*` file. Do not spawn sub-agents. Start at 200k lines (k=68) for iteration; run 1M only for the final number.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use gold tags, nltk, spaCy, or any pretrained embedding in learning. Do NOT re-run Ward.
