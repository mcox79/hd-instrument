# exp_dev hand-off -- research: substrate-native structured prediction (CRF + SSVM + EBM)

Filed-by: research:opus (2x DEEP drill)
Trigger: research delivery notes/research_drill_substrate_structured_prediction_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag; this is queue-refill candidate material only

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHOR CANDIDATES and POINTERS, not full experiment specs. exp_dev owns the design.

## Anchor candidates (rank-ordered)

### A1 -- substrate-linear-chain-CRF for POS tagging (HIGHEST PRIORITY)
- Anchor pointer: research_drill_substrate_structured_prediction_2x_2026-06-11.md section (b) EXP-1
- Substrate-product reading: discriminative upgrade to the validated count-based POS tagger (0.906); lift expected 1-3 points
- Tier hint: Tier B candidate, can reach Tier A with multi-seed n=5 and stable lift >= 1.4 SE over baseline
- Why now: substrate-only POS already validated; this is the discriminative-training swap; no new infrastructure; ~1 hr CPU
- Cheap-CPU candidate (no GPU needed)

### A2 -- substrate-structured-SVM (Frank-Wolfe / 1-slack)
- Anchor pointer: research_drill_substrate_structured_prediction_2x_2026-06-11.md section (b) EXP-2
- Substrate-product reading: max-margin regularization gives generalization-gap reduction on top of A1
- Tier hint: Tier B contingent on A1 passing
- Why now: same architecture as A1; only training-procedure swap; isolates the margin question
- Cheap-CPU candidate

### A3 -- substrate-energy mean-field for nested-NER
- Anchor pointer: research_drill_substrate_structured_prediction_2x_2026-06-11.md section (b) EXP-3
- Substrate-product reading: unlocks nested NER / SRL / multi-label structured outputs as substrate-native (currently cap_map says LLM-front-end required)
- Tier hint: novel-synthesis; Tier B if F1 >= 0.85; Tier C / partial below that
- Why now: validates the EBM-on-substrate framework end-to-end; tests whether substrate algebra supports mean-field variational inference
- ~2-3 hr CPU; could run overnight on home/laptop runners

### A4 -- substrate-resonator-as-belief-propagation formalization (theory + smoke)
- Anchor pointer: research_drill_substrate_structured_prediction_2x_2026-06-11.md cross-thread synthesis point 5
- Substrate-product reading: reinterprets existing resonator-network primitive as max-product loopy BP on factor graph; opens graph-structured EBMs without new substrate code
- Tier hint: theoretical; could be Tier B with a single graph-EBM smoke (e.g. small image-segmentation task)
- Why now: most substrate-novel finding in the drill; cheapest path to publishable / shippable novel architecture
- Cheap-CPU candidate

## Context pointers (paths, not summaries)

- notes/research_drill_substrate_structured_prediction_2x_2026-06-11.md (this drill)
- notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md (adjacent: structured-perceptron updates on substrate validated empirically)
- notes/substrate_only_NL_pos_tagger_validated_2026-06-11.md (current 0.906 baseline that A1 would lift)
- notes/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (substrate-classical pattern; this drill extends it to substrate-discriminative-structured)
- notes/substrate_capability_map.md (cap_map row for structured-prediction would be NEW; sequence-labeling rows would shift from LLM-front-end to substrate-native if A1 passes)
- notes/research_drill_active_inference_rescue_2x_2026-06-11.md (free-energy framing is shared with active-inference work; if A3 passes, the two unify)

## Contract

- exp_dev owns smoke gate, pre-reg per envelope-fail-bands, REMOTE VERIFY, self-test per formula-selftests
- Pause-gated by data/orchestrator_paused.flag
- Honest re-read of verdict_msg vs per-cell metrics on completion (Step 0)
- HARD-PASS and HARD-FAIL thresholds binding from research note section (c)

## Autonomy declaration

exp_dev decides:
- Order of A1 / A2 / A3 / A4
- Whether to combine A1 and A2 in one batch (same architecture, different training procedure -- could share data + features)
- Smoke configuration and seeds
- Whether to ship A4 theory-first or smoke-first
- Whether to gate A3 on A1 passing first (recommended but not required)

Research has NO opinion on the cell-mechanics; the drill output is the pre-registered targets.
