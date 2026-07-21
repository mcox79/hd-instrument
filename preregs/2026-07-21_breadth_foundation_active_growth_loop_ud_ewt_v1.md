# Pre-registration: exp_breadth_foundation_active_growth_loop_ud_ewt_v1

Date: 2026-07-21
Author: exp_dev (hdi_exp_dev)
Cell: experiments/exp_breadth_foundation_active_growth_loop_ud_ewt_v1.py

## Question
Can the read-drives-knowledge LOOP run as an ACTUAL active-learning loop that reads real varied
prose, detects word-meaning coverage GAPS, ASSIGNS meanings on-demand from the KB resources
(VerbNet affectedness lexicon + WordNet noun/adj semantics), GROWS a foundation store, and shows
the active-learning SIGNATURE (ask-rate DECLINING as coverage grows)? This is the Layer-0 breadth
foundation the composition/reasoning pyramid sits on ("build the pyramid from the bottom").

## Corpus / difficulty-on
- UD-EWT train.conllu (English Web Treebank: blogs, reviews, emails, newsgroups) processed
  sentence-by-sentence in FIXED corpus order (held-out ordering: loop never sees the future).
- GOLD UPOS+LEMMA read from conllu (no front-end needed for the loop). Content words =
  {NOUN, VERB, ADJ, PROPN}. Real varied prose, NOT McGuffey's tiny vocab.
- SMOKE = 400 sentences; FULL = 6000 sentences.

## Arms (one variable = the store-write / assignment rule; identical stream + ask-accounting)
- growth-ON: resolve from resource, store TRUE meaning, mark known.
- growth-OFF (REAL BASELINE): never store -> every non-seed content token re-asks -> ask-rate flat.
- growth-SHUFFLE (MUST-FAIL): same retention as ON (identical coverage + ask-rate curves) but stores a
  PERMUTED (wrong) meaning -> the usefulness probe must COLLAPSE.

## Metrics
- MISS-RATE per content token per bin (PRIMARY, decisive, confound-free): asks/content-tokens. OFF=1.0
  by construction (every token re-asks, no retention); ON declines by retention. 12 bins.
- ASK-RATE per sentence per bin (USER-named view; carries a sentence-length drift across UD-EWT genre
  blocks -> reported but not the verdict driver).
- COVERAGE curve: fraction of content tokens the store functionally supplies per bin.
- Usefulness probe: binary affect prediction (grown verb graded_score>=0.5) vs INDEPENDENT human gold
  (UD-EWT breadth gold; HIGH={patient,effected} vs LOW={target_not_affected}).
- Residual gap breakdown by category: named_entity / verb_not_in_verbnet / noun_oov_wordnet /
  adj_oov_wordnet (+ resolved_sense_flagged reported separately).

## Bands (declared BEFORE full)
- learns := on_miss_ratio(per-token last/first) <= 0.50 AND on_cov_delta(last-first) >= +0.20 AND
  on_spearman_vs_index(miss-rate) <= -0.50 (Spearman trend = robust "monotone-ish"; adjacent-bin strict
  monotonicity is fragile to corpus document-burstiness; adjacent-bin frac still reported as telemetry)
- baseline_flat (baseline_no_retention) := off_miss_mean >= 0.98 AND off_cov_delta <= 0.02 (OFF per-token
  miss = 1.0 by construction; a retention LEAK into the control drops it -> can-fail integrity check.
  NOTE: OFF per-SENTENCE ask-rate drifts with sentence length across genre blocks -> per-token drives verdict)
- retention_gap := (off_miss_last - on_miss_last) >= 0.30
- shuffle_collapses := (real_auc - shuffle_auc_mean) >= 0.15 AND real_auc >= 0.70 AND shuffle_auc_mean in [0.40,0.60]
  (usefulness = rank-AUC that grown verb graded_score separates HIGH-affect vs LOW-affect human gold;
  multi-seed shuffle null over 20 permutations; verbs lemmatized)
- HARD_PASS_BREADTH_LOOP: learns AND baseline_flat AND retention_gap AND shuffle_collapses AND arms_differ AND deterministic
- HARD_FAIL_BREADTH_LOOP: on_miss_ratio>0.80 OR on_cov_delta<0.10 OR off_miss_mean<0.98 (control leaked retention) OR not shuffle_collapses OR not arms_differ
- MIDDLE_BAND_BREADTH_LOOP: otherwise

## Design-gate checklist
- REAL baseline: growth-OFF (no retention) -> flat ask-rate. Not a strawman.
- Can-fail: if the store did not retain, ON would look like OFF (no decline) -> HARD_FAIL. If ask-rate
  declined even for OFF (Heaps-only, no retention), off_ask_ratio<0.70 -> HARD_FAIL (contrast confounded).
- One variable: the store-write rule (ON writes, OFF does not, SHUFFLE writes wrong).
- Difficulty-on: real varied web prose, held-out corpus order.
- Discriminator survives scale: smoke at 400 sentences fires ALL discriminators; probe verbs resolved
  through the arm rule -> full probe coverage so must-fail fires at smoke AND full.

## Must-fail control
growth-SHUFFLE: presence/ask-rate identical to ON (cannot distinguish) -> usefulness probe must collapse
to ~chance. Proves the grown foundation is real MEANING, not just marking-words-seen.

## Self-test (non-tautological)
(1) real_code_path exercises the REAL VerbNet lexicon + wn_noun_semantics + wn_adj_meaning at N~16.
(2) coverage is FUNCTIONAL not raw-presence: >=1 verb in WordNet but NOT in the affectedness lexicon.
(3) named_entity escalation category fires for a PROPN with no common-noun synset.
(4) ask-rate RESPONDS to growth: toy repetitive stream -> ON drops to 0, OFF stays flat.
(5) shuffle collapses the usefulness probe (real-shuffle >= 0.15).
(6) arms_differ: ON vs SHUFFLE store hashes differ on a real stream.
(7) determinism: re-run identical curves.

## Compute architecture
sequential-CPU justified (glass-box streaming dict/lookup; ~O(1e4) unique lookups cached; no matmul;
wall < few min dominated by ~28s WordNet import). Storage: dict foundation (grown COPY at
data/breadth_foundation_grown_v1; production KBs untouched). Determinism: fixed seeds, np.random
Generator only, no hash()-seed, sorted iteration, OMP/MKL/OPENBLAS=1.

## Dispatch
LOCAL foreground to COMPLETION (light compute). NO queue, NO push, NO remote-persist, NO atom bank.
Skunkworks VETs on land.
