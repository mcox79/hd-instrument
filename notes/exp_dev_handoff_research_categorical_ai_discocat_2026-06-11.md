# exp_dev hand-off -- research: categorical AI / DisCoCat 2x DEEP

Filed-by: research (Opus) 2026-06-11
Trigger: 2x DEEP drill completion, notes/research_drill_categorical_ai_discocat_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag at dispatch time

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR POINTERS and SUBSTRATE-PRODUCT READINGS only. exp_dev owns experiment design (smoke gate, pre-reg per envelope-fail-bands, queue routing, self-test). research does NOT prescribe code, hyperparameters, or evaluation harness.

## Anchor candidates (rank-ordered by P_deflated x cheapness x diagnosticity)

### Anchor 1 (HIGHEST PRIORITY): CAT-1 -- substrate-categorical typed-tensor binding on sentence paraphrase

- Anchor pointer: research note section (b) "Pilot CAT-1"
- Substrate-product reading: validate that DisCoCat-typed binding outperforms current untyped sum-bundle on substrate-only sentence-similarity. If PASS, typed-tensor becomes Tier-2 primitive.
- Tier hint: Tier-2 (CPU, ~2 hr)
- Why-now: cheapest of the 3 pilots; lowest-risk; highest-prior P_deflated (0.55).
- HARD-PASS / HARD-FAIL bands: AUC_typed - AUC_untyped >= 0.05 (PASS) / <= 0.00 (FAIL).
- Seed primitive (~30 lines) provided in research note section "substrate-categorical primitive".

### Anchor 2 (HIGH PRIORITY): CAT-3 -- density-matrix lexical entailment

- Anchor pointer: research note section (b) "Pilot CAT-3"
- Substrate-product reading: validate that substrate atoms as density matrices support graded hyponym/hypernym entailment via von Neumann entropy. If PASS, opens lexical-entailment substrate capability without LLM dependency.
- Tier hint: Tier-2 (CPU, ~1 hr)
- Why-now: cheapest pilot; Bankova et al. 2016 has published FHilb precedent (~0.70 prior).
- HARD-PASS / HARD-FAIL: hyponym-precision >= 0.70 (PASS) / <= 0.55 (FAIL).

### Anchor 3 (MEDIUM PRIORITY): CAT-2 -- SCAN compositional-generalization probe

- Anchor pointer: research note section (b) "Pilot CAT-2"
- Substrate-product reading: zero-parameter substrate-functor on SCAN held-out compositional split. If PASS, substrate unlocks BENCH-class compositional-generalization claim.
- Tier hint: Tier-2 (CPU, ~3 hr)
- Why-now: highest-diagnosticity but lowest prior (P_deflated 0.32); run AFTER CAT-1 confirms typed-tensor pays off.
- HARD-PASS / HARD-FAIL: held-out accuracy >= 0.40 (PASS) / <= 0.15 (FAIL).

### Anchor 4 (DEFER): CAT-PARSE -- substrate-categorical dependency parsing

- Anchor pointer: research note section (c) Prediction P5
- Substrate-product reading: substrate-only unsupervised pregroup-type-inference for dependency parsing.
- Tier hint: Tier-3 (CPU, ~1 day; requires CAT-1 + CAT-2 outcomes first)
- Why-defer: lower P_deflated (0.35); higher engineering cost; depends on CAT-1 + CAT-2 confirming typed-tensor pays off at all.

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_categorical_ai_discocat_2x_2026-06-11.md (this drill; primary reference)
- d:/AI/hd-instrument/memory/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (categorical recovery of HMM-Viterbi NLP precedent)
- d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md (v3.0 cliff crossing IS the categorical-functor-preserves-composition empirical signature)
- d:/AI/hd-instrument/memory/substrate_LLM_boundary_decomposition_2026-06-10.md (categorical framing aligns with the substrate-as-functor / LLM-as-front-end-grammar division)

## Contract section

- Research provides: anchor pointers, substrate-product reading, tier hints, HARD-PASS/HARD-FAIL bands, seed primitive (~30 lines numpy).
- exp_dev owns: full experiment design, smoke gate, pre-reg per envelope-fail-bands, queue routing (CPU lane), self-test per formula-selftests, post-ship REMOTE VERIFY.
- Research does NOT prescribe: hyperparameters, codebook sizes, eval-harness internals, number of seeds, multi-seed protocol.
- Research escalation: if exp_dev surfaces blocking design question (e.g., "what dataset for paraphrase pairs?"), file strategy_request_to_research_*.md routing note.

## Autonomy declaration

- exp_dev MAY: choose dataset (e.g., MSRP for CAT-1, WordNet for CAT-3, official SCAN for CAT-2); choose D (substrate dim); choose multi-seed n; defer any anchor to next cycle; reject any anchor if smoke gate fails.
- exp_dev MUST: respect HARD-PASS / HARD-FAIL bands as filed (do not relax thresholds); pre-reg per envelope; honor pause flag.
- exp_dev SHOULD: run CAT-1 first (cheapest + highest prior); use CAT-1 outcome to gate CAT-2 dispatch.
