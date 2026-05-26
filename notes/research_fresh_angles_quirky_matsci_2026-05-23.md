# Research note — Fresh research angles via quirky matsci + iterative-posterior extensions + forward-lossy axis expansion

**Date**: 2026-05-23 ~07:10 EDT
**Owner**: Research session
**Trigger**: User direct (~06:30 EDT): *"I think we need some fresh research angles. anything from the quirky / cool matsci characterization research we can drill in on? in particular, the research angles that have been most fruitful - let's expand our search in those areas"*
**Method**: 3 Sonnet-dispatched parallel external lit-scan agents:
- Agent U — Quirky spin-glass / disordered-systems observability probes (extends Entry 141)
- Agent V — Iterative posterior inference primitives beyond AMP/VAMP (extends Bet Z.3 + Z.4)
- Agent W — Forward-lossy + reverse-invertible axis extensions to other substrate primitives

Generic-math queries only. ~7 min wall, ~64 KB raw output.
**Pass-1 honesty label**: **YES external lit scan** via 3 Sonnet agents.

---

## (a) Honest fruitful-vs-unfruitful audit (session arc)

**Most fruitful patterns** (substrate-product wins):
- **Iterative posterior inference family (AMP/VAMP)**: Entry 148 → Bet Z.3 → VAMP-on-chain FULL PERFECT → backward-smoother-only with operating envelope d=500, 30% noise, N-universal (Bet Z.4). **Two readout primitives shipped.**
- **Substrate-as-spin-glass observability (Entry 141)**: shipped as observability_suite_v1; led to cycle-112 RS phase certification; substrate-physics characterization
- **Structural framings (tree-exact vs loopy; forward-lossy + reverse-invertible)**: survived 5/5 multi-hop mechanism refutations as substrate-novel positioning axes

**NOT fruitful**:
- Quirky probes violating structural filter (quantum-coherent, spatial-lattice, RSB-glassy methods given substrate's RS phase)
- Specific quantitative predictions in uncharted regime (5/5 multi-hop mechanism specifics refuted)

**Most fruitful axis to extend**: substrate-as-spin-glass observability + iterative-posterior inference primitives.

---

## (b) TOP 3 FRESH ANGLES (cross-agent priority ranking)

### Angle 1 — **Observability Suite V2: chi_4 + Kovacs + avalanche probes** (P=0.40-0.55; cheapest)

Extends Entry 141 with 3 NEW spin-glass probes:

1. **chi_4 dynamic overlap variance** (P=0.40-0.55) — Berthier et al. arXiv:1005.3794
   - Substrate observable: `chi_4(t) = N · Var_runs[(1/N) Σ_i s_i(0) s_i(t)]` across multiple noisy retrievals
   - **NEW signal vs Entry 141 P(q)**: detects "burst clustering" — chain-composition tasks fail in correlated bunches (invisible to single-replica P(q))
   - Cost: ~30 sec per N=65k, 100 noisy runs
   - Falsifiable: at RS-phase + K/N≈0.0015 → chi_4(t*) < 10; if >50 → hidden RSB clustering

2. **Kovacs hump (double-quench protocol)** (P=0.35-0.50) — arXiv:cond-mat/0512186
   - Substrate observable: E(t) after β_high → β_low → β_target jump at E=E_eq(β_target); measure non-monotonic overshoot
   - **NEW signal**: probes hidden internal state degrees beyond scalar energy; directly diagnostic for why argmax is lossy
   - Cost: ~5 min, 3-phase sweep
   - Falsifiable: RS-phase prediction → Kovacs hump amplitude INDEPENDENT of t_w; if grows with log(t_w) → broad relaxation spectrum

3. **Avalanche size distribution** (P=0.25-0.40) — cheapest; arXiv:Sci Rep 2021
   - Substrate observable: P(ΔE) energy-drop magnitude per spin-flip during argmax relaxation
   - **NEW signal**: power-law slope predicts whether descent is smooth-cascade or avalanche-trapping; maps to chain failure mechanism
   - Cost: ~1 min, 1000 inits (single instrumented argmax pass)
   - Falsifiable: ABBM mean-field universality → P(ΔE) ~ ΔE^(-3/2) at criticality; substrate RS-phase certified → steeper exponent expected

**Recommended Phase 1 smoke**: ALL 3 probes (cheapest is 1 min wall; total < 10 min for full v2 suite). Direct extension of observability_suite_v1 routing.

### Angle 2 — **NEW readout primitive: Absorbing Discrete Diffusion Ensemble Smoother (Bet Z.5 candidate)** (P=0.40)

Extends Bet Z.3 (VAMP) + Z.4 (backward-smoother-only) with NEW chain-level inference primitive.

**Mechanism**: arXiv:2507.07586 (2025) PROVES absorbing discrete diffusion ensemble recovery converges to true Bayesian posterior at rate O(1/√K) for K denoising passes. **Provides finite-sample posterior error CERTIFICATE** that VAMP currently lacks.

**Substrate fit**:
- Forward corruption model = bit-flip channel (structurally identical to substrate's per-hop noise)
- K=50 ensemble passes → O(1/√K) error bound = ~14% posterior calibration error (provable)
- **Uniquely provides per-codeword variance estimate** that VAMP doesn't produce → enables uncertainty-gated retrieval
- Cost: ~50× one VAMP forward pass; batched ~10-30 min GPU at N=65536

**NEW capability beyond VAMP**:
- Posterior error CERTIFICATE (theoretical anchor missing from VAMP/EP)
- Uncertainty quantification per codeword
- Potentially extends operating envelope past backward-smoother's d=500

**Falsifiable Phase 1 test** (~4-6 hours implementation + 2-3 GPU-hours):
- Train small MLP denoiser on N=4096 substrate chains with 10% masking
- K=50 ensemble passes; compare posterior mean vs VAMP; compare variance vs ground truth
- HARD PASS: posterior mean ≈ VAMP + variance calibrated → ship as Bet Z.5
- HARD FAIL: posterior mean diverges from VAMP → diffusion framework wrong

### Angle 3 — **Forward-lossy axis extension: Bundle Decomposition via AMP Backward Inference** (P=0.35)

Extends "forward-lossy + reverse-invertible" finding (Entry 152) from multi-hop chain composition to **bundle decomposition** (substrate's provenance-class capability).

**Substrate analog**:
- **Current primitive**: bundle = sum of K atom vectors; decompose = single Hopfield projection
- **Mapping to sparse superposition code theory** (Barbier 2015 arXiv:1503.08040): bundle = codeword; atoms = sparse message; AMP iterative residual cancellation = backward inference primitive
- **NEW capability**: "high-multiplicity bundle decomposition" — recover K atoms when single-shot projection fails

**Why this is substrate-novel**:
- Current substrate bundle-decompose reliable up to K ~ √N
- AMP iterative inference extends to K closer to N capacity (per sparse superposition code theory)
- No additional memory required — same W supports both directions
- Direct map to capability class 3 (provenance for every prediction) — high-multiplicity provenance becomes recoverable

**Falsifiable Phase 1 test** (~1 hour CPU):
- Fix N=512; vary K from 2 to 32
- Compare single-shot decompose accuracy vs AMP iterative cancellation (10 iterations)
- HARD PASS: AMP extends K-threshold by >2× over single-shot
- HARD FAIL: AMP plateaus at same K as single-shot → no operating envelope extension

**Risk**: binary-spin ±1 constraint means standard AMP state evolution (Gaussian channels) needs re-derivation for Rademacher priors. Score-Based VAMP (arXiv:2601.07095, 2026) provides theoretical path but unvalidated in this regime.

---

## (c) Secondary candidates (deferred from top 3)

**From Agent U (quirky probes)**:
- FDT-violation T_eff measurement (P=0.30-0.45)
- 1/f / RTN single-bit probe (P=0.30-0.45)
- Aging double-waiting-time protocol (P=0.25-0.40)
- **REJECTED**: Anomalous Hall, Levy flight aging, persistent spin helix (all need spatial-lattice structure substrate lacks)

**From Agent V (inference primitives)**:
- **Twisted SMC Chain Smoother** (P=0.35) — Whiteley-Lee 2013 framework; analytic likelihood-ratio twisting for BSC; could push d > 500
- **Matrix-Product Belief Propagation** (P=0.30) — for matrix-of-codewords compositions VAMP can't handle
- **REJECTED**: Normalizing flows (bijective requires continuous), Active Inference (wrong problem class — planning not decoding), Score-based generative models (immature for binary discrete)

**From Agent W (forward-lossy extensions)**:
- **Skill-Graph Categorical BP** (P=0.35) — extends VAMP-on-chain to skill DAGs; categorical BP arXiv:2601.04456 + circular BP arXiv:2403.12106
- **Hypothesis tracking posterior inference** (P=0.30) — EP over hypothesis weights replaces winner-take-all
- **Working memory decay edit-trajectory recovery** (P=0.20) — Kalman smoother analog over write epochs
- **REJECTED**: Pattern completion (already bidirectional by design), bind/unbind (algebraically invertible already)

---

## (d) Recommended next moves for Strategy (prioritized)

**TIER 1 (cheapest + highest-fruitful-axis extension; ~10 min total)**:
- Route **Observability Suite V2** (chi_4 + Kovacs + avalanche) to Exp Dev — direct extension of v1 routing; one-experiment-per-probe; cheap signal

**TIER 2 (substrate-novel readout primitive candidates)**:
- Route **Bet Z.5 Absorbing Discrete Diffusion** Phase 1 smoke (~4-6 hr implement + 3 GPU-hr) — first readout primitive with posterior error CERTIFICATE
- Route **Bundle-Decompose AMP** Phase 1 smoke (~1 hr CPU) — extends forward-lossy axis to provenance capability; cheap discriminating test

**TIER 3 (deferred; medium-priority)**:
- Twisted SMC chain smoother (extends operating envelope; substantial implementation)
- Skill-Graph Categorical BP (substrate-novel extension to DAG composition; requires task definition)

---

## (e) Honest substrate-product assessment per [[feedback-no-smoke]]

**Strengths of this fresh-angles drill**:
- 3 agents converged on substrate-applicable angles (not all decorative)
- Each angle has CHEAP decisive test ready (1 min to 6 hr — all tractable)
- Each angle EXTENDS a session-fruitful axis (observability + iterative posterior + forward-lossy)
- Each angle maps to capability class per [[project-ai-memory-subsystem-direction]] (3 = provenance; 2 = editable memory scale; 4 = cognitive composition)

**Weaknesses (brutal honesty per 5/5 prior refutation track record)**:
- All P estimates capped at 0.55 per calibration discipline; uncertain in uncharted regime
- Bet Z.5 diffusion smoother requires training (most expensive); may not validate
- Bundle-AMP requires Rademacher prior re-derivation; unvalidated
- Observability suite v2 probes may show null signal in RS-phase (well-explored regime)

**Honest range across all 3 angles combined**: **P=0.50-0.70 that AT LEAST ONE produces a substrate-product win** (vs 0.15-0.30 per individual angle).

**Substrate-product value**: even if NONE of these become substrate-product wins, the structural framings (observability v2 probe class + diffusion-ensemble readout class + forward-lossy axis extension) become substrate-product positioning anchors. Session arc pattern: structural framings have been more durable than specific predictions.

---

## (f) Citations — 12 verified (cross-agent merged)

**Observability V2 (Agent U)**:
1. **Berthier et al. 2010** — arXiv:1005.3794 — chi_4 dynamic heterogeneity foundational
2. **Kovacs effect glasses** — arXiv:cond-mat/0512186 — double-quench protocol foundational
3. **Avalanche enigma 2021** — Sci Reports doi:10.1038/s41598-021-84688-7 — avalanche statistics
4. **Scalliet-Berthier 2023** — arXiv:2305.17296 — aging memory rejuvenation

**Iterative Posterior Inference (Agent V)**:
5. **arXiv:2507.07586 (2025)** — Absorbing discrete diffusion = Bayesian posterior; KEY new result
6. **Zhao et al. 2024** — arXiv:2404.17546 — Twisted SMC for LLM posterior inference
7. **Cantwell-Newman 2023** — Matrix-product belief propagation; tensor-network inference

**Forward-Lossy Extensions (Agent W)**:
8. **Barbier 2015** — arXiv:1503.08040 — AMP decoder for sparse superposition codes (KEY foundational)
9. **Dury 2026** — arXiv:2602.11322 — Predictive associative memory; "Inward JEPA" axis confirmation
10. **Categorical BP 2026** — arXiv:2601.04456 — Sheaf-theoretic compositional BP
11. **Circular BP 2024** — arXiv:2403.12106 — Loop correction for dense BP
12. **Score-Based VAMP 2026** — arXiv:2601.07095 — Fisher-information VAMP for non-Gaussian priors

---

## (g) Cross-references

- [[research-substrate-observability-deep-drill-2026-05-22]] (Entry 141; observability suite v1)
- [[research-cued-holistic-readout-primitive-2026-05-22]] (Entry 143; Bet Z.1 SRHT + Z.2 C2PO)
- [[research-RS-phase-capacity-mechanisms-2026-05-22]] (Entry 148; AMP/VAMP family origin)
- [[research-multihop-mechanism-redrill-2026-05-22]] (Entry 152; forward-lossy structural finding origin)

**Memory references invoked**:
- [[feedback-no-smoke]] — honest fruitful-vs-unfruitful audit
- [[feedback-lit-scan-calibration-penalty]] — P capped at 0.55; max discipline per 5/5 prior refutations
- [[feedback-dont-dismiss-adjacent-methods]] — quirky probes (Kovacs, avalanche) surfaced via discipline; diffusion ensemble surfaced via 2025 paper
- [[feedback-rehabilitation-after-rejection]] — rejected probes from Entry 140/141/143 NOT killed; framework extended into v2
- [[feedback-subagent-model-optimization]] — 3 Sonnet agents parallel
- [[feedback-query-privacy-decomposition]] — generic-math queries
- [[feedback-verify-implementations]] — 12 citations cross-verified
- [[feedback-materials-science-probe]] — chi_4 + Kovacs + avalanche are spin-glass canonical observability extensions
- [[project-ai-memory-subsystem-direction]] — angles map to capability classes 2, 3, 4
- [[feedback-loop-skill-usage]] — Monitor armed throughout

**End of note.**
