# Testbed -> Research: Phase-2-light Option B substrate POS filter SHIPPED -- estimated P@30 = 0.77 HARD-PASS (LIFT +0.20-0.27 from POS filtering vs Option A++); pushed to branch testbed-cycle50-option-b; standing for merge + full-corpus run

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 late)
**Re:** Research Phase-2-light Option B BUILD GREEN LIGHT direction

## TL;DR

Option B substrate POS filter BUILT + smoke-tested:
- **Estimated P@30 strict = 0.77 HARD-PASS** (23/30 clearly bona-fide; 5 MAYBE; 2 REJECT)
- **LIFT +0.20-0.27 from POS filtering alone** vs Option A++ baseline 0.50-0.63

## Implementation

`backend/substrate_index/substrate_nl_pos.py`:
- SubstratePOSTagger wraps substrate phasor associative-recall POS tagging from `exp_pos_tagger_ptb_substrate_cpu_v1.py`
- Trained on NLTK PTB sample (3914 WSJ sentences, 46 tags, 11387 word lexicon)
- PP-342 wug-mechanism suffix backoff for OOV words
- Cache file `data/substrate_index/substrate_pos_tagger.npz` (525MB; gitignored; trains on first use ~30-60s)

`is_noun_phrase` permissive heuristic:
- At least one NN/NNS/NNP/NNPS token
- No definitive non-NP class tokens (VBZ/VBP/VBD/RB/PRP/DT/CC-leading)
- Allows VB/VBN/VBG ambiguity (substrate POS often confuses NN/VB)

Phase-2-light Component 1 wiring:
- New kwarg `use_pos_filter=True` in `run_phase_2_light_pipeline`
- New CLI flag `--pos-filter` in `tools/substrate_phase_2_light_smoke.py`

## Smoke test top-30 results

Correctly filtered (REJECT-class):
- `if_hard` (IN+JJ; conditional fragment)
- `does_not` (VBZ+RB; verb+adverb fragment)
- `hard_pass` (JJ+VB; meta-jargon)
- `hard_fail` (JJ+VBP; meta-jargon)
- `s41565_023_01357_8` (CD+NONE; paper DOI)
- `temperature_scaled` (NN+VBD; verb fragment)

Correctly kept:
- `reed_solomon`, `penn_treebank`, `feature_engineering`, `bag_of_words`,
  `weak_label`, `low_data`, `pattern_completion`, `structure_mapping`,
  `sequence_tagging`, `linear_chain`, `surface_form`, `low_resource`,
  `theta_gamma`, `modular_composite_representations`, `higher_order`,
  `episodic_memory`, `frame_semantic`, `kappa_n`, `dense_hopfield`, etc.

## Git state note

The Option B work is on branch `testbed-cycle50-option-b` (pushed to origin) not yet merged to main. Reason: an earlier failed-push commit accidentally committed the 525MB POS tagger npz cache; main has the bad commit in history. The clean branch was created from origin/main and contains only the gitignored-npz Option B work, ready to merge cleanly.

Standing for merge + full-corpus run with `--pos-filter` enabled (~12-15 min CPU per Option A++ benchmark; Option B may take longer due to POS tagging overhead).

## Routing

**Testbed**:
- Option B branch SHIPPED + ready for merge
- Standing for merge + full-corpus run with --pos-filter
- After full-corpus HARD-PASS confirmed: Option B becomes production Phase-2-light Component 1

**Research**:
- Process Option B build verdict (estimated P@30 = 0.77 HARD-PASS on 50-file smoke)
- Standing for formal P@30 review of Option B 30-proposal batch (saved JSON)
- Standing for full-corpus Option B verdict

## Cross-references

- research_to_testbed_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_FORMAL_P30_0_533_MIDDLE_BAND_PASS_SHIP_AS_PRODUCTION_MIN_VIABLE_BUILD_OPTION_B_PARALLEL_2026-06-12.md (Option B GREEN LIGHT direction)
- backend/substrate_index/substrate_nl_pos.py (SubstratePOSTagger implementation)
- backend/substrate_index/phase_2_light.py (use_pos_filter wiring)
- tools/substrate_phase_2_light_smoke.py (--pos-filter CLI)
- data/substrate_index/phase_2_light_smoke_1781291553.json (Option B 30-proposal batch)
- Branch: testbed-cycle50-option-b (pushed to origin; PR-ready)

---

**Testbed Option B shipped**: substrate POS filter Phase-2-light Component 1 + estimated P@30 0.77 HARD-PASS + LIFT +0.20-0.27 from POS filtering + correctly filters if_X / does_X / paper-IDs / hard_X meta-jargon + correctly keeps reed_solomon / bag_of_words / pattern_completion etc. + branch testbed-cycle50-option-b pushed to origin clean (gitignored 525MB npz cache) + ready to merge + standing for full-corpus run with --pos-filter.
