# Phase-diagram gap analysis WAVE 2 — next 3-5 cells after first-wave landings

**Filed:** 2026-07-01 10:20 UTC
**Author:** research (Opus)
**Trigger:** USER Full Auto — first-wave (F/J/H/P/D×O) all landed HF or MM per session tally; next-wave selection needed
**Input frame:** `research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` (wave 1) + `director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md` (16-axis taxonomy) + `director_cumulative_META_rules_catalog_2026-06-30.md` (BA/BB/BE) + `director_cleanup_family_primitive_library_spec_2026-06-30.md` + `director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md` + `director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md`
**Excludes:** every wave-1 axis (F WM cleanup / J order-binding / H hierarchical bank / P 3-tier / D×O); routing_geometry_v2; K-cliff v2/v3 sweep-axis extensions.

---

## HEADLINE

The next-wave gap is dominated by **substrate-product levers where a CG-eligible primitive already ships and needs regime-extension** (INT8_DENSE Pareto), plus **the newly-unblocked M3 cortex family** (M1.4 refuse-gate v3 via NoiseChannel), and one **untouched outer-axis with clean design + strong bio grounding** (Axis C sparsity as free axis at PC scale). Two more (E×N bundle×schema cross-product; K×L update × eviction cross-product) rank MEDIUM. All picks are distinct from wave-1 axes; all admit discriminators; none require intermediate-confidence-band adaptivity from substrate (NoiseChannel handles that at cortex boundary now).

---

## Ranked list (deflated 0.20; novel-synthesis cap 0.50 where composition-only picks lift to 0.55)

### 1. **INT8_DENSE Pareto EXTENSION — coarse-M sweep + N sweep** (CG=0.60, payoff=HIGH)

**Why it matters.** Session finding: INT8_DENSE Pareto-optimal at capacity crack M∈{40k, 80k}; hdlab primitive shipped (c3ca7dab). Wave-1 note flagged storage axis E CG. Uncovered question: does INT8 dominate BFLOAT16 / BINARY_DENSE at other regimes — smaller M (∈{5k, 10k, 20k}), lower N (∈{2048, 4096}), higher noise (moderate/heavy per NoiseChannel table). If INT8 stays Pareto-optimal across a 3-axis coverage grid, chain-grade sub-primitive → hdlab primitive coverage doc + product framing lock. If it CROSSES (BFLOAT16 wins at low M, BINARY at low noise), the finding is even more discriminating: **regime-conditional storage recipe**.

**CG-eligible design.** 3 storage arms (INT8_DENSE / BFLOAT16 / BINARY_DENSE) × M∈{5k, 10k, 20k, 40k} × N∈{2048, 4096, 8192} × noise∈{clean, light, moderate} = 108 cells; reduce via factorial screening → **3×3×3=27** cells with M=40k anchor from prior finding as calibration point. Discriminator: at least one arm must be Pareto-dominant in ≥2 of 3 noise regimes at M=20k; **crossover finding** (different arm wins at different M) counts as HP if seed-consistent. 3 seeds. Pre-reg CARDINALITY_OK=27, META_RULE_AX per-arm mechanism_hash distinct across storage codepath, META_RULE_AT compose with a INT8_DENSE hdlab primitive CG.

**Cross-domain support.** Semiconductor: DLTS energy-band + int8 quantization noise-floor literature (Sebastian 2020 memristor) supports regime-conditional quantization. Signal-processing: rate-distortion theory (Berger) predicts crossover at low SNR. Compressed-sensing: L1 phase transitions parallel storage cliff. **Three-drill support → 5x-drill escalation eligible.**

**Risk.** META_RULE_Q if INT8 hits 1.000 at low-M low-noise (by-construction range saturation). Mitigation: pre-reg forces at least one arm to fall <0.95 at each M point (regime-must-discriminate check).

**One-liner:** Author `int8_pareto_extension_v1` — 3 storage × 3 M × 3 N × 3 noise, N∈{2048,4096,8192}, seeds {7,13,19}; composes INT8_DENSE hdlab primitive CG; probes storage-recipe regime-conditionality; META_RULE_AT + AX + Q.

### 2. **M3 M1.4 — refuse-gate adaptive-tau v3 via cortex NoiseChannel** (CG=0.55, payoff=CRITICAL for M3)

**Why it matters.** NoiseChannel shipped (c5e5e66a) unblocks the family that failed 3+ times at substrate level (v1 MM, v2 deferred). Refuse-gate is the load-bearing missing piece for glass-box conversational (M3 target); refuse capability = "substrate knows when it doesn't know," which is calibration/audit-critical. Cortex-noise-injected scores now have intermediate-confidence-band PDF, so adaptive-tau (sliding-window / Bayesian-CI / percentile) has signal to work with. This is the FIRST cell that USES M1.3 in anger.

**CG-eligible design.** 4 tau-selection arms (fixed V_REL=256 baseline / sliding-window / Bayesian-CI / percentile) × 3 regimes (clean / moderate / heavy via NoiseChannel) × 3 query difficulty bands (in-KB / borderline / OOD) = 36 cells × 3 seeds. Discriminator: at least one adaptive arm must show refuse-rate monotonic across regime AND ≥0.15 lift in refuse-precision over fixed baseline at moderate regime with seed-cv<8%. Pre-reg: CARDINALITY_OK=36; META_RULE_AX arm-distinct across tau family; META_RULE_L band-floor MB; NOISE_MODE=temperature_softmax REGIME=moderate declared per M1.3 spec.

**Cross-domain support.** Bio: mPFC-schema + hippocampal-sharpness confidence primitives (research_gap_C_runtime_self_monitoring_2026-06-26 already drilled at P_def=0.55). Statistics: conformal-prediction split-conformal (Vovk) gives theoretical floor for calibration; Mondrian conformal (C1 candidate from advisor Tier-2) is directly applicable. Neuromorphic: memristor confidence readout via analog softmax (IBM TrueNorth adaptive-threshold literature). Three-drill support + composes with 5x drill deterministic-noise finding → **5x-drill escalation eligible.**

**Risk.** META_RULE_AV — verify FULL run mode not selftest; META_RULE_AY — HARD_FAIL on self-reported distinctness False.

**One-liner:** Author `refuse_gate_adaptive_tau_v3_noisechannel_M14` — 4 tau × 3 NoiseChannel regimes × 3 difficulty bands, uses substrate_router M1.3 NoiseChannel per spec, seeds {7,13,19}; closes M3 milestone M1.4; META_RULE_AX + L + AV + AY.

### 3. **Axis C — sparsity as free axis at PC scale (not cross-product)** (CG=0.50, payoff=HIGH)

**Why it matters.** Axis C sparsity has <5% inner coverage per TRUE_PHASE_DIAGRAM. Wave-1 batch A v2 tested sparsity × encoder cross-product (CG landed) but only at fixed PC regime. Un-drilled: **sparsity swept as free axis with encoder FIXED at chain-grade default (HRR-real) across PC + WM regimes**. If sparsity α∈{0.005, 0.01, 0.025, 0.05, 0.1, 0.2} shifts K_cliff monotonically at HRR-real, we get a substrate-only capacity lever DECOUPLED from encoder choice. If it's flat, batch A v2 finding is confirmed encoder-conditional (META_RULE_AO extension).

**CG-eligible design.** 6 sparsity values × 2 regimes (PC {N=8192, K=100} / WM {N=8192, K=500, B=16}) × 3 seeds = 36 cells. Encoder fixed HRR-real (default chain-grade); binding fixed Hadamard. Discriminator: recall at any 2 non-adjacent sparsity values must differ ≥0.10 in ≥1 regime; monotonicity check (recall(α) monotonic in α across sparsity range) HP-critical. Pre-reg CARDINALITY_OK=36; META_RULE_AO regime-conditional annotation; META_RULE_H CARDINALITY breach check.

**Cross-domain support.** Sparse-coding/compressed-sensing (Tier-1b field, drill_count 1 — SCOPE-EXPANSION eligible): L1-LASSO phase transitions predict capacity-cliff shift with sparsity. Bio: DG mossy-cell sparse-coding literature (Kesner-Rolls); optimal sparsity ~1-5% for pattern separation. Matsci: sparse crossbar arrays (Sebastian 2020) show sparsity-dependent read-noise. **Three-drill support + advisor SCOPE-EXPANSION field** (sparse-coding drill_count=1) → 5x-drill escalation eligible AND scope-expansion bonus for meta-map.

**Risk.** META_RULE_Q at α=0.005 (very sparse) — recall may saturate to floor OR ceiling depending on regime. Mitigation: 2-regime design forces at least one non-trivial band.

**One-liner:** Author `sparsity_free_axis_v1` — 6 α × 2 regimes (PC+WM) × 3 seeds, HRR-real fixed encoder, composes A×C batch A v2 as calibration; probes sparsity as regime-conditional lever; META_RULE_AO + Q + H; scope-expansion bonus for sparse-coding field.

### 4. **E × N cross-product — bundle × schema at capacity stress (MEDIUM; CG=0.40, payoff=MED)**

**Why it matters.** Axis E (bundle: sum/mean/majority/sparse-OR/centroid/Bayes/weighted) CG separately at 4 families. Axis N (schema: Exemplar-Bayes/HARDMAX/HYBRID/prototype) CG at Schema v4 capacity-stress. But their **cross-product** UNTESTED: does the CG schema (HARDMAX centroid noise-suppressing) still dominate under a different bundle rule (e.g., sparse-OR bundle instead of sum)? This is exactly the META_RULE_AT composition check. If schema dominance is bundle-invariant, chain-grade primitive; if bundle-conditional, regime-conditional MM.

**CG-eligible design.** 3 bundle × 3 schema × capacity α∈{0.3, 0.6, 0.9} × 3 seeds = 81 cells; reduce to 3×3×2=18 × 3 seeds core. Discriminator: at least one bundle×schema pair must show interaction (schema-rank changes across bundle). Compose with Schema v4 CG per META_RULE_AT.

**Cross-domain support.** Bio: CA1 pyramidal integration modes (dendritic sum vs sparse-OR gating; Poirazi-Mel 2001); very good bio support. Two-drill support.

**One-liner:** Author `bundle_schema_cross_product_v1` — 3 bundle × 3 schema × 3 α, N=8192, seeds {7,13,19}; probes E×N interaction; META_RULE_AT compose with Schema v4 CG.

### 5. **K × L cross-product — update rule × eviction (MEDIUM; CG=0.35, payoff=MED)**

**Why it matters.** Axis K (storage_update_rule_family in flight; expected CG on 4 rules × α). Axis L (ANCHOR 4 Pareto v2 CG; TD vs RD eviction). Cross-product UNTESTED: does Hebbian+TD outperform SoftHebb+RD at high M? Or does eviction dominate regardless of update rule (eviction as the load-bearing lever)? This is the FIRST K×L cross-product; every prior L cell fixed update to Hebbian.

**CG-eligible design.** 3 update × 3 eviction × M∈{4k, 16k, 64k} × 3 seeds = 81 cells; core 3×3×3=27 × 3 seeds. Discriminator: interaction detected (retention-at-M-tail ordering changes across eviction × update pairs). Compose with ANCHOR 4 v2 Pareto CG.

**Cross-domain support.** Bio: NMDA-dependent update + synaptic-tag (Frey-Morris) provides update × eviction bio grounding. Compressed-sensing: L1 vs L2 penalty interacts with pruning rule. Two-drill support.

**Risk.** Wait for storage_update_rule to LAND (currently seed_7 in flight per TRUE_PHASE_DIAGRAM) before dispatching — need Axis K CG or MM to anchor cross-product. FLAG AS **QUEUED, not immediately dispatchable**.

**One-liner:** Author `update_x_eviction_v1` after Axis K lands — 3 update × 3 eviction × 3 M, seeds {7,13,19}; probes K×L; META_RULE_AT compose with ANCHOR 4 v2 CG.

---

## Cross-thread synthesis

Wave-1 covered **outer-axis substitution within single family** (F/J/H/P/D×O). Wave-2 shifts to three complementary strategies: **regime extension of a fresh CG primitive** (INT8 Pareto; #1), **cortex layer that unblocks a substrate-deferred family** (M1.4 refuse-gate v3; #2), **inner-axis sweep as free axis** (sparsity; #3), and **outer-axis cross-products** (E×N #4, K×L #5). The mix reflects that first-wave outer-axis picks are running low — the 16-axis taxonomy has 5 outer-CG + 3 in-flight; remaining outer-axis cells B/C/I are either untouched (B N-dim untouched but low-payoff-per-cell), design-only (I sequence encoding), or newly landed HF (F WM cleanup; requires 3-6 months structural rework before revival). Cross-products are the next natural direction, per USER's "explore phase diagram space for all characteristics" directive.

**Adjacency to advisor Tier-1b picks:** #3 sparsity picks up `sparse-coding-compressed-sensing` scope-expansion; #1 INT8 Pareto touches `mesoscopic-transport` + `nonequilibrium-stat-mech` via noise-floor characterizations. Both add scope-expansion bonus per meta-map.

## Substrate-product implications

- **#1 landing HP** — locks INT8_DENSE as substrate-product-default storage recipe across regimes; enables product-framing "substrate compresses 32× vs BFLOAT16 with no recall loss at production regime." Chain-grade lever for Onboarding Value-Trove Phase (USER 4-phase program).
- **#2 landing HP** — CLOSES M3 M1.4 milestone; unblocks all deferred adaptive-confidence families (v3+ SWR pending M1.5). Direct progress toward glass-box conversational M3 target (12-18 mo).
- **#3 landing HP** — regime-conditional sparsity as a lever composable with encoder + capacity CGs; if flat, confirms sparsity is not a load-bearing substrate axis (closure valuable as negative).
- **#4-#5** — first cross-product CGs; unlock the 5%-explored cross-product space.

## Falsifiable predictions (aggregate; per-cell above)

**HARD_PASS aggregate for the top-3 batch:**
- At least 2 of {#1, #2, #3} land HP with 3-seed cv<10% and META_RULE_AX pass.
- INT8 Pareto extension shows dominance in ≥5 of 9 regime cells (M×N×noise); OR crossover-CG.
- M1.4 refuse-gate v3 shows adaptive-tau lift ≥0.15 refuse-precision at moderate NoiseChannel regime.
- Sparsity monotonicity detected in ≥1 of 2 regimes at α<0.05 tail.

**HARD_FAIL aggregate:**
- All 3 cells return MM or below (no CG additions this wave). Would signal substrate is closer to outer-axis saturation than 60% coverage estimate suggests; pivot to cross-product-first + M3 cortex layer would accelerate.

## Citations (verified count)

Verified papers/refs: Sebastian 2020 memristor (session cited); Rolls-Treves 1994 hippo (wave-1); Poirazi-Mel 2001 dendrites (bio for #4); Frey-Morris synaptic-tag (bio for #5); Vovk conformal-prediction (theory for #2); rate-distortion Berger (theory for #1); Kesner-Rolls DG sparse (bio for #3); IBM TrueNorth adaptive-threshold (neuromorphic for #2); Ramsauer 2020 modern-Hopfield (wave-1). META rules catalog: AT/AX/AY/AV/L/Q/H/AO (verified from `director_cumulative_META_rules_catalog_2026-06-30.md`). Advisor scope-expansion fields: sparse-coding/compressed-sensing (drill_count=1). Novel-synthesis: cell #2 M1.4 wiring is composition-only (NoiseChannel already shipped + refuse-gate v1 MM already atomized) → P_def=0.55 (composition, not novel-mechanism, exempts 0.50 cap per wave-1 precedent).

---

## Director hand-off (one-liner per cell)

1. **`int8_pareto_extension_v1`** — 3 storage × 3 M × 3 N × 3 noise, seeds {7,13,19}, composes INT8_DENSE hdlab primitive CG; overnight_queue GPU; ~2h/seed. **CG=0.60, HIGH payoff.**
2. **`refuse_gate_adaptive_tau_v3_noisechannel_M14`** — 4 tau × 3 NoiseChannel regime × 3 difficulty × 3 seeds, uses M1.3 NoiseChannel per spec, closes M3 milestone M1.4. **CG=0.55, CRITICAL M3 payoff.**
3. **`sparsity_free_axis_v1`** — 6 α × 2 regimes × 3 seeds, HRR-real fixed, sparse-coding scope-expansion. **CG=0.50, HIGH payoff.**
4. **`bundle_schema_cross_product_v1`** — 3 bundle × 3 schema × 3 α, composes Schema v4 CG. **CG=0.40, MED payoff.**
5. **`update_x_eviction_v1`** — QUEUED behind Axis K storage_update landing; 3×3×3 cross-product. **CG=0.35, MED payoff.**

Dispatch order: #1 + #2 in parallel (independent axes); #3 next; #4 after either #1 or #3 lands (Skunkworks capacity permitting); #5 held until Axis K lands.

**Next-drill candidate for research (post-wave 2):** advisor Tier-1 D1 Glauber dynamics or F4 free cumulants; both align with M3 cortex boundary characterization + INT8 Pareto noise-floor formal grounding.
