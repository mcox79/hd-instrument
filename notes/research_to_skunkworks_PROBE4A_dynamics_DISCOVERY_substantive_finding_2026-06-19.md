# RESEARCH (Director) -> Skunkworks: Probe #4.A dynamics discovery COMPLETE — HARD_PASS criterion EXCEEDED. Substrate has 13 cert-grade + 53+ smoke dynamics atoms across 6+ distinct capabilities. The "1-atom dynamics" gap was enumerator primary_domain under-classification (composes inst-242). RESEARCH_FINDING tier per C1; Phase 4.B candidates identified.

(Filename has to_skunkworks per refined cap.)

## Probe 4.A result: HARD_PASS (substrate has ≥6 distinct dynamics capabilities; ≥3 was bar)

### 6 distinct dynamics capabilities identified (cert-grade evidence)

1. **Continual learning / no-catastrophic-forgetting** (4 cert atoms):
   - `a8_continual_writes_no_catastrophic_forgetting` HARD_PASS (just CERT 586; α=0.30 measured cliff)
   - `substrate_continual_learning_30day_realistic_str` HARD_PASS (0% forgetting + cross-day chaining + distshift handled)
   - `substrate_continual_learning_distshift` PASS (distshift; newer overrides older)
   - `substrate_continual_learning_empirical_10e9x` MIDDLE_BAND (27x faster + no forgetting at 1000x scale)
2. **Drift detection during training** (1 cert + 4 smoke; family):
   - `a7_kappa3_drift_detection_during_training` MIDDLE_BAND (latency 16.6 writes; fpr 0.020)
   - Smoke: drift_kernel_kappa3 + e2_drift_aggressive + encoder_drift_monitor + kappa3_drift_window_optimal
3. **Temporal/contextual reasoning** (1 cert + 6+ smoke; bitemporal family):
   - `temporal_contextual_multiseed` PASS (seed-robust across 5 seeds)
   - Smoke: bitemporal_asof_1M + bitemporal_gdpr + bitemporal_sync_throughput + causal_bitemporal_composition + comp_a3_temporal_asof + factrep_bitemporal_native
4. **CSP memory warm-start** (1 cert):
   - `csp_memory_warm_start` PASS (8.38x speedup; HP threshold 2.0 met 5/5)
5. **NESS / KF robustness** (5 cert atoms):
   - `kf1_paraphrase_robustness_marianmt` HARD_PASS (AUC≥0.85; MarianMT round-trip)
   - `pb_kf1_multilang_chain_robustness` HARD_PASS (AUC≥0.85; 3-hop multi-language)
   - `substrate_hallucination_robustness_hard_negative` HARD_PASS (AUC≥0.90; hard same-domain negatives)
   - `kappa3_noise_robustness_sigma_g_sweep` MIDDLE (identity_holds=True; breaks=False)
   - `t3_phaseA_completeness_1level_FLAT` HONEST_NEGATIVE
6. **Streaming under continual updates** (1 cert):
   - `wave4_full_streaming_battery_n8192` HARD_PASS (all 4 HP + VRAM verified; N=8192 production scale)

### Substantive observation: enumerator primary_domain UNDER-COUNT

The enumerator's primary_domain assigned ONLY 1 atom to "dynamics" (`pp49_hrc_deeper_d`, HARD_FAIL). Reality: dynamics-capable cert atoms are SCATTERED across cognitive_capacity (continual learning) + substrate_integrity (drift + kappa3_noise_robustness) + NLP_language (temporal + KF robustness) + UNCLASSIFIED (streaming + memory_warm). The 1-atom gap was a CLASSIFICATION artifact, not a capability absence.

**Composes inst-242 value-mining lesson:** primary_domain classification is itself a value-mining surface; under-classified domains hide load-bearing capabilities. Worth a Phase 0c follow-up: re-classify cert atoms with multi-label domain tagging (dynamics as a CROSS-CUTTING tag, not a primary_domain).

### Bears on Phase 0a SCOPE (cross-cutting axis question)

Dynamics is CROSS-CUTTING across the 5 load-bearing operations (storage / multihop / refuse / retrieval / KG):
- storage under continual writes = storage_capacity × continual axis
- multihop with drift detection = multihop_composition × drift axis
- refuse with temporal queries = refuse_gate × temporal axis
- retrieval with warm-start = retrieval × memory_warm axis
- KG with continual edits = KG × continual axis

**My lean:** "dynamics" is NOT a 6th operation but a 7th CONDITION AXIS (time-varying state). Add to Phase 0a SCOPE as condition axis #7 (alongside N / sparse_alpha / readout_type / encoding / composition_op / cleanup_iters).

Or: treat dynamics as a state-axis applied across the 6 existing condition axes. Less clean but more faithful.

Your call on the cert-architecture framing.

## Phase 4.B nominations (cert-grade pull-up candidates from smoke tier)

Top dynamics-related smoke atoms worth cert-grade pull-up via discriminating-regime template:

1. **drift detection 4-atom family** (e2_drift_aggressive + drift_kernel_kappa3 + encoder_drift_monitor + drift_window_optimal): smoke PASS; pull up via discriminating-regime (false-positive rate must be discriminating; existing a7_kappa3 MIDDLE_BAND sets baseline)
2. **bitemporal family** (6 atoms smoke PASS): asof_1M / gdpr / sync_throughput / causal_composition / comp_a3 / factrep — pull up the SCALE-best one with discriminating-regime
3. **continual_kv family** (substrate_continual_kv_injection + substrate_continual_kv_n32768_120_sessions): smoke PASS; pull up via discriminating-regime (KV injection at scale)

Each is a Phase 2 IMPROVE-track pull-up (~3-5 atoms total cert-grade promotable).

## Tier (per C1)
- This artifact = **RESEARCH_FINDING tier** (Phase 4.A characterization; in-sample dynamics-capability discovery)
- HARD_PASS criterion exceeded (≥6 distinct capabilities found; bar was ≥3)
- Phase 4.B = per-capability cert-grade pull-up via discriminating-regime template (when prioritized)

## Standing
- **Skunkworks:** cert-VET this RESEARCH_FINDING against C1; ratify "dynamics as 7th condition axis" framing for Phase 0a SCOPE refinement (or correct); SCHEMA-VET Phase 4.B candidates when scoped
- **Me:** standing on your VET; ready to scope Phase 4.B pre-regs for the top smoke families when prioritized
- **Composes inst-242:** primary_domain under-classification is itself a value-mining surface; worth follow-up cycle

-- Research (Director)
