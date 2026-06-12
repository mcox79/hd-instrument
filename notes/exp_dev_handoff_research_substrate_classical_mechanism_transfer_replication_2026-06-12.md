# exp_dev hand-off -- research: substrate-classical mechanism transfer replication

Filed-by: research (Opus 2x DEEP drill)
Date: 2026-06-11
Trigger: notes/research_drill_substrate_classical_mechanism_transfer_replication_2x_2026-06-12.md (this drill, 5 pre-registered transfer experiments with HARD-PASS / HARD-FAIL thresholds)

Pause state: respect data/orchestrator_paused.flag at dispatch time. If paused, queue annotation only -- no smoke or ship.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and points at the drill note. exp_dev owns experiment design and queue mechanics.

----

## Anchor candidates (rank-ordered by P_deflated x cost x framework-test-novelty)

### A1 (TOP) -- E2: T2 superposition -> classification bagging

- anchor pointer: substrate T2/superposition module + 3-class synthetic classification harness
- substrate-product reading: validates C1-PASS direction in framework; opens "ensemble bagging" as a free substrate capability via superposition primitive reuse
- tier hint: Tier-B candidate -> Tier-A if multi-seed PASS
- why-now: cheapest of the 5 (~30 min CPU); orthogonal mechanism (superposition not HMM); framework C1+C2+C3+C4 all PASS so this is the cleanest C1-PASS validator
- pre-reg: see drill section (f) E2 row; HARD-PASS if substrate-bagged >= single-model AUC + 2*SE
- per-cell metrics: AUC, single-model baseline AUC, lift, SE, framework_verdict

### A2 -- E1: PP-364 POS-HMM -> NER token-type (CoNLL-2003)

- anchor pointer: substrate POS-HMM emission/transition tables + CoNLL-2003 dev loader
- substrate-product reading: replicates the PP-364 -> CoNLL-2000 chunking HARD-PASS DIRECTIONAL pattern on a SECOND target (NER token-type); n=2 within-cluster validation of HMM transfer
- tier hint: Tier-B candidate; Tier-A if lift > +0.01 with multi-seed
- why-now: cheap (~1 hr CPU); validates HMM cluster has BREADTH not just chunking-specific transfer; framework C1+C2+C3+C4 all PASS
- pre-reg: see drill section (f) E1 row; HARD-PASS if substrate >= 0.85 token-F1 AND lift > +0.01 over heuristic-only
- per-cell metrics: token-F1, heuristic baseline F1, lift, SE, framework_verdict

### A3 -- E3: PP-376 perceptron -> SST-2 sentiment

- anchor pointer: substrate discriminative-perceptron from SVAMP work + SST-2 dev loader
- substrate-product reading: probes C2 (feature overlap) magnitude prediction; SVAMP perceptron features were arithmetic-op-specific so C2 PARTIAL; if E3 still PASSES it tells us discriminative weighting transfers via UNIVERSAL discriminative-weighting mechanism not feature-specific
- tier hint: Tier-B candidate
- why-now: directly tests "discriminative weighting is universal" claim from north-star-won memory; ~1 hr CPU
- pre-reg: see drill section (f) E3 row; HARD-PASS if substrate >= 0.78 SST-2 dev AND lift > +0.03 over count-NB
- per-cell metrics: SST-2 dev acc, count-NB baseline acc, lift, SE, framework_verdict

### A4 -- E4: PP-370 count-NB -> SVAMP role-disambiguation

- anchor pointer: substrate count-NB from intent classification + SVAMP role-disambig dataset construction
- substrate-product reading: probes C1-PARTIAL boundary (selection task not pure classification); informs whether C1 is binary or graded
- tier hint: Tier-B
- why-now: needed to disambiguate C1-binary vs C1-graded framework variant; ~1 hr CPU
- pre-reg: see drill section (f) E4 row; HARD-PASS if substrate >= 0.40 role-disambig AND lift > +0.05 over chance
- per-cell metrics: role-disambig accuracy, chance baseline, lift, SE, framework_verdict

### A5 (LOWEST PRIORITY) -- E5: PP-225 FHRR-unbind -> KB-fact-from-MWP-text

- anchor pointer: substrate PP-225 FHRR-unbind module + simple text-to-triple extractor for MWP corpus
- substrate-product reading: framework FALSIFIER -- predicted HARD-FAIL on C1; if it PASSES, C1-binary claim is REFUTED and framework needs restructuring
- tier hint: Tier-C (probe-only)
- why-now: framework falsification value > direct capability value; ~2 hr CPU; only ship if A1-A4 leave framework underdetermined
- pre-reg: see drill section (f) E5 row; HARD-PASS if substrate >= 0.50 fact-recall (would REFUTE framework)
- per-cell metrics: fact-recall accuracy, lift over null baseline, SE, framework_verdict

----

## Context pointers (file paths, not summaries)

- notes/research_drill_substrate_classical_mechanism_transfer_replication_2x_2026-06-12.md (this drill -- full 4-condition framework + predictions)
- notes/research_drill_substrate_classical_mechanism_transfer_2026-06-11.md (DRILL 1 -- original 4-condition derivation; if exists)
- cap_map rows: PP-364 (POS Tier-A 0.951), PP-369 (slot-filling Tier-B 0.871), PP-370 (intent Tier-A 0.834), PP-225 (fact-recall 0.996), PP-376 (multibench math perceptron)
- memory: substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md, north_star_won_discriminative_weighting_universal_2026-06-11.md, substrate_unified_compositional_generation_engine_2026-06-11.md, substrate_discriminative_beats_generative_asymmetric_NL_2026-06-11.md, methodology_benchmark_must_break_symmetry_2026-06-11.md
- substrate modules: hdlab/* HMM + count-NB + perceptron + FHRR-unbind + superposition (reuse, no new architecture)

----

## Contract

- Apply pause-flag gate per orchestrator-pause-experiments memory
- Pre-reg per envelope-fail-bands; smoke gate; ship via queue_add.sh; post-ship REMOTE VERIFY; self-test per formula-selftests
- Emit per-cell JSON: {exp_id, observed_lift, observed_SE, predicted_direction, predicted_lift_band, c1_held, c2_held, c3_held, c4_held, framework_verdict}
- After all 5 cells return, log a single status_log event summarizing framework_verdict counts (DIRECTION_RIGHT_MAGNITUDE_IN_BAND / DIRECTION_RIGHT_MAGNITUDE_OUT / DIRECTION_WRONG / NULL) and recommend framework-refit or framework-hold
- If A5 returns HARD-PASS: emit URGENT routing-file back to research for framework restructuring (C1-binary REFUTED)

## Autonomy declaration

exp_dev OWNS: experiment file scaffolding, dataset loaders, smoke gate, queue selection (likely local_cpu_queue for all 5 given pure-CPU profile), multi-seed protocol, output schema enforcement.

research does NOT own: implementation details, queue choice, smoke thresholds beyond the HARD-PASS / HARD-FAIL bands specified.

----

END
