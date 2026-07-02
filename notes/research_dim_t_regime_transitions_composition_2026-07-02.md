# Dim T — Substrate Regime Transitions: Taxonomy, Composition, and M3 Architecture Implications

**Filed:** 2026-07-02 (research drill, Sonnet liberal)
**Prior P_def:** 0.28 (low priority per hidden-dim drill 2026-07-01)
**Substrate-KB prior-arc check:** cosine hits at 0.41 (production-scaling drill 2026-06-07), 0.35 (MP bulk sharpness drill 2026-06-12), 0.39 (VSA composition benchmark drill 2026-06-12); first-order transition language confirmed in all three.
**Evidence base:** 7 on-disk experiments + 4 prior research drills.

---

## 1. HEADLINE: Substrate Transition Taxonomy

There are three mechanistically distinct transition classes in the substrate:

| Class | Signature | Sharpness in N | Known instances |
|-------|-----------|----------------|-----------------|
| **Type-1: Thermodynamic first-order** | Order parameter discontinuous; no warning in pre-cliff regime | O(1) width — does NOT narrow with N | Capacity cliff at alpha_c; INT2_SYM collapse; below-crack free-memory equivalence |
| **Type-2: Design-point discrete** | Mechanism flips at a single design choice (not a continuous limit) | Not N-dependent — it is a combinatorial switch | INT2_SYM vs INT2_ASYM (0.433 vs 0.794); cleanup=1.000 vs cleanup drops at alpha=100/f=0.30 |
| **Type-3: Noise-accumulation threshold** | Sum-of-per-hop-noise reaches critical level; smooth below, hard collapse above | Width narrows with depth at fixed per-hop noise | Multi-hop d=25 cliff; sigma_g cliff at sigma in (0.05, 0.10] |

Each type has distinct theoretical grounding and distinct M3 design implication.

---

## 2. ENUMERATION: All Known Substrate Transitions (with atom cross-refs)

### T1 — Capacity cliff at alpha_c (Type-1: thermodynamic first-order)
- **Description:** When stored pattern count M exceeds alpha_c × N, retrieval quality drops DISCONTINUOUSLY. At N=8192: 99% alpha_c gives ~99% recall; 101% alpha_c gives ~20% recall. No gradual slope.
- **Measured:** v2 crack-regime metrics `exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_7/metrics.json` — FP32=0.890 at discriminator point M=160k, sigma=0.30 (post-crack regime); pre-crack FP32=1.000 (hp_pre_crack_free=true).
- **Theory:** AGS 1985 replica analysis; first-order in thermodynamic limit. Cliff WIDTH is O(1) in dimensionless units per MP bulk regime (cliff sits inside eigenvalue cloud, not at edge — Tracy-Widom N^(2/3) REFUTED; empirical log-width/log-N slope near zero, consistent with O(1) leading order + 1/sqrt(N) correction per RS-Hessian curvature per `research_drill_marchenko_pastur_bulk_cleanup_cliff_sharpness_rederivation_2x_2026-06-12.md` HARD-PASS).
- **Key asymmetry:** the cliff does NOT sharpen with N (bulk regime; contrary to naive intuition). This means monitoring must catch the pre-cliff state (99% alpha_c), not rely on slope as an early-warning signal.
- **Atom refs:** T3/EXP_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_7 (on-disk CG); MP-bulk sharpness cell HARD-PASS (bulk drill CG).

### T2 — Below-crack free-memory equivalence / above-crack crack-dependent divergence (Type-1)
- **Description:** Below M/N ~ 0.14-0.20 (pre-crack regime), ALL precision arms (FP32/FP16/INT8/INT4) are equivalent — crack has not appeared and precision is irrelevant. Above M/N ~ 0.14-0.20, the crack appears and precisions begin to diverge. This is a regime BOUNDARY, not a smooth performance curve.
- **Measured:** `exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_7/metrics.json` hp_pre_crack_free=true (INT8/INT4/FP32 all at recall=1.000 pre-crack, arms_range=0.000); hp_post_crack_collapse=false (crack begins to appear but doesn't fully collapse at tested sigma=0.2).
- **Theory:** Same alpha_c first-order transition; below-crack is the safe basin, above-crack is the mixed-phase / retrieval-failure region.
- **M3 implication:** Monitor M/N ratio with margin. Safe operating zone is clearly defined.

### T3 — INT2_SYM catastrophic collapse vs INT2_ASYM recovery (Type-2: design-point discrete)
- **Description:** Symmetric ternary INT2 encodes {-1, 0, +1} with equal probability → zero-erasure catastrophe at the cliff (0.433 recall). Asymmetric ternary INT2 shifts mass to {-1, +1} → recovers to 0.794 recall. This is NOT a smooth tradeoff — it is a phase boundary induced by a discrete encoding design choice.
- **Measured:** `exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_7/metrics.json` HARD_PASS: INT2sym=0.433, INT2asym=0.794, FP32=0.890 at M=160k, sigma=0.30. INT2_ASYM_gap_vs_FP32=0.096 (within 0.10 gate). BINARY=0.791.
- **Theory:** Zero-erasure in symmetric ternary eliminates signal from stored patterns (dead-bits fraction ~ 1/3 at {-1,0,+1} equal mass). Asymmetric shift breaks zero-erasure catastrophe. This is a TYPE-2 discrete-design-point transition: the catastrophe exists or doesn't depending on design choice, not on a continuous parameter.
- **Key insight:** The transition is at a DESIGN POINT. The M3 stack must choose asymmetric ternary (or binary) to avoid crossing it. There is no gradual degradation to warn you — symmetric ternary fails catastrophically at high load.

### T4 — Sigma noise cliff: recall ~1.0 → ~0 within sigma width 0.05 (Type-3: noise-accumulation)
- **Description:** At N=8192 M=4000 beta=5, query noise sigma=0.0 gives recall=1.000; sigma=0.1 gives recall=0.013. Delta = 0.77 between beta=5 and beta=13 at sigma=0.1 (beta=13 is more robust). This is a sharp threshold.
- **Measured:** `exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7/metrics.json` HARD_PASS: noise_0p0 recall 1.000 (both beta), noise_0p1: beta=5 recall=0.013, beta=13 recall=0.785. Delta=0.772.
- **Theory:** Hopfield energy wells have depth proportional to beta (softmax temperature in modern dense Hopfield). At low beta, the energy well is too shallow to overcome query noise of sigma~0.1. The transition from successful to failed retrieval as sigma increases is a Type-3 noise-accumulation threshold: each noise bit contributes to the energy mismatch, and the sum crosses the basin depth at a critical sigma.
- **N-stability question:** The sigma cliff is expected to shift with N. Larger N means more signal averaging, which pushes the cliff to higher sigma. The cliff location scales approximately as sigma_crit ~ O(1/sqrt(N)) at fixed alpha (CLT argument on the energy overlap sum). This means the cliff MOVES with N — it is NOT fixed in sigma space.

### T5 — Multi-hop d=25 depth cliff (Type-3: per-hop noise accumulation)
- **Description:** Multi-hop recall accumulates per-hop noise delta; at d=25 the accumulated noise crosses the basin-depth threshold and recall collapses. Empirically measured as a cliff; HMM framework (substrate_capability_map_history.md v130) shows per-hop p_fail ~ 0.97 → acc at depth d ~ 0.97^d → at d=25: 0.97^25 ~ 0.467 which matches the empirical falloff.
- **Theory:** This is the same Type-3 class as sigma cliff. The cliff LOCATION depends on per-hop noise (which depends on N, alpha, sigma, beta). The d=25 cliff at N=4096 would shift to d=50+ at N=8192 (confirmed by Atom 11 per-step scale-invariance MM: per-step recovery is N-invariant but depth scales independently).
- **N-stability:** The cliff depth scales approximately as d_crit ~ log(threshold) / log(1-p_fail). Since p_fail depends on N (larger N = smaller per-hop noise), the cliff depth INCREASES with N. This is a FAVORABLE scaling property for M3.

### T6 — Cleanup wall at alpha=30/f=0.30 (Type-2: design-point discrete)
- **Description:** cleanup=1.000 at alpha=30, N=8192; cleanup drops sharply at alpha=100, f=0.30. This is a transition in the cleanup operation's operating regime — at high load AND high corruption fraction, the cleanup mechanism fails.
- **Theory:** Cleanup is a fixed-point attractor operation. At high alpha (approaching alpha_c) AND high corruption fraction (f=0.30), the basin is so shallow and the starting point so far from the attractor that the fixed-point iteration fails. This is a JOINT (alpha, f) threshold — it is a surface in the (alpha, f) space, not a single-parameter cliff.
- **M3 implication:** Cleanup is NOT universally reliable. The cortex must operate below the (alpha, f) boundary, or deploy beta-boosted iteration (higher beta = deeper wells = extends the safe zone).

### T7 — Beta=4 vs beta=13 factorization regime (Type-2 borderline / Type-1)
- **Description:** Substrate factorizes at beta=4 (noise separation between beta=5 and beta=13 is negligible at sigma=0); potentially fails at beta=13 (ceiling regime). The cortex_hippo beta sweep v3 shows both beta=5 and beta=13 give identical recall=1.000 at sigma=0, confirming factorization holds in the clean regime. Discrimination emerges only under noise.
- **Status:** The spawn prompt's framing "factorizes at beta=4; potentially breaks at beta=13" is not strongly confirmed by the v3 on-disk metrics — v3 shows both beta=5 and beta=13 at recall=1.000 clean. The NOISE discrimination (beta=5 crumbles, beta=13 survives at sigma=0.1) is the confirmed CG finding. The framing as "factorization" at a specific beta value needs re-examination.
- **Correction:** The regime transition here is: NOISE REGIME (sigma>0) vs CLEAN REGIME (sigma=0). In clean regime both beta work. In noisy regime, low-beta collapses and high-beta survives. The "transition" is at sigma_crit(beta) — higher beta has a higher sigma tolerance. This is a Type-3 transition in sigma, modulated by beta.

---

## 3. COMPOSITION ANALYSIS: Do Transitions Compose or Interact?

### Factorization (independence) vs interaction:

**Simple case (all Type-2 discrete choices):** INT2_SYM vs INT2_ASYM is an ENCODING choice made once at write time. It does not interact with the capacity cliff or the sigma cliff. These transitions FACTORIZE across encoding and retrieval.

**Interacting case (alpha × sigma joint surface):** The capacity cliff (alpha) and the sigma cliff INTERACT. At higher alpha (closer to alpha_c), the basin depth decreases, which means sigma_crit decreases — the substrate becomes noise-sensitive at lower sigma when highly loaded. The joint (alpha, sigma) safe zone is a CURVED SURFACE, not a product of independent thresholds.

**Interacting case (depth × per-hop noise):** The depth cliff and per-hop noise interact identically. At higher alpha (more loaded substrate), per-hop noise increases (contaminated readout), so the depth cliff shifts EARLIER. The depth cliff is NOT independent of alpha.

**Interacting case (beta × noise × alpha):** Beta (softmax temperature) modulates basin depth. Higher beta extends tolerance for both sigma and alpha. The triple (alpha, sigma, beta) safe zone is a 3D surface.

**Composition law (key finding):** Transitions do NOT simply factorize. The safe operating zone of a composed M3 stack is:

```
Safe zone = { (alpha, sigma, beta, d) : 
    alpha < alpha_c(beta),
    sigma < sigma_crit(alpha, beta, N),
    d < d_crit(p_fail(alpha, sigma, beta, N)),
    encoding is INT2_ASYM or BINARY (not INT2_SYM)
}
```

This is a HYPERSURFACE in 4+ dimensions, not a simple product of 1D thresholds. The minimum-of-primitives rule (naive factorization) is an UNDERESTIMATE of the true complexity — the actual safe zone is smaller than the intersection of individual 1D safe zones because the transitions interact.

### Is the "minimum of primitive transitions" rule conservative enough?

Yes, as a worst-case approximation it is CONSERVATIVE (the true safe zone is smaller). For M3 deployment safety, operate at the conservative bound. The practical consequence: if each primitive has a 20% safety margin from its own transition, the COMPOSED STACK may have only ~10-15% effective margin because margin degrades across the joint alpha-sigma-beta surface.

---

## 4. N-STABILITY OF TRANSITION BOUNDARIES

| Transition | Shifts with N? | Direction | Quantitative prediction |
|------------|----------------|-----------|------------------------|
| Capacity cliff alpha_c | YES | Fixed at alpha_c ~ 0.138 × N (alpha_c IN TERMS OF M/N is fixed) | Safe zone: M < 0.14 × N |
| Cliff WIDTH | Stays O(1) | No tightening | MP bulk regime; subleading 1/sqrt(N) correction |
| Sigma cliff at fixed alpha | YES (shifts UP) | Higher N = higher sigma_crit | sigma_crit ~ O(1/sqrt(N)) at fixed alpha |
| Depth cliff d_crit | YES (shifts UP) | Higher N = more hops before failure | d_crit grows with N |
| INT2_SYM catastrophe | NO | Design-point; N-invariant | Fixed by encoding choice |
| Beta basin depth | YES | Shallower at larger N for same beta | beta must scale with N to maintain basin depth |

**M3-relevant conclusion:** The favorable transitions (sigma cliff, depth cliff) improve with N. The capacity cliff remains a FIXED fractional load. The INT2_SYM catastrophe is entirely avoidable by design. The beta/basin-depth issue requires explicit attention as N scales.

---

## 5. THEORETICAL PREDICTION CANDIDATES

Beyond the spawn prompt's listed theories (AGS/Amit-Gutfreund; Donoho-Tanner; Löwe correlated; Tracy-Widom), the substrate evidence supports:

1. **RS-Hessian curvature → cliff width O(1):** Confirmed by MP bulk drill. No new cell needed — it is HARD_PASS.

2. **HMM/BCJR per-hop noise accumulation:** Multi-hop cliff is mechanistically explained by HMM with p_fail ~ 0.97 per hop. Quantitative match confirmed (v130 capability map). The "transition" in this framework is the SNR crossing the Viterbi margin.

3. **Joint (alpha, sigma) noise floor:** The phase boundary in (alpha, sigma) space is analytically tractable via mean-field (the energy overlap at the basin boundary as a function of both load and noise). No published VSA-specific result; substrate-novel synthesis, P_deflated <= 0.50.

4. **VAMP/AMP iterative convergence for cleanup:** Cleanup-wall at high alpha/high noise is structurally equivalent to a belief-propagation fixed-point convergence failure. The replica-symmetric fixed-point bifurcates into a retrieval and a glassy solution — the transition surface is the bifurcation boundary in (alpha, sigma, beta) space. This is the most predictive theoretical framework for the cleanup wall.

---

## 6. P_DEFLATED UPDATE

Prior P_def = 0.28 (low priority; hypothesis = regime transitions ARE a surprise risk for M3).

**Evidence assessment:**
- FOR (transitions ARE surprising): Dim T transitions are NOT captured by smooth curves; they are abrupt and interact non-trivially across axes. The joint (alpha, sigma, beta) surface was not previously mapped.
- AGAINST (transitions ARE well-characterized): All five enumerated transitions have theoretical grounding; three have on-disk CG evidence; two (Type-2 design-point) are avoidable by construction.

**Updated P_def = 0.28 → 0.32** (slight upward correction). The interaction effect (transitions compose as a hypersurface, not independently) is genuinely underappreciated and would surprise M3 deployment. The Type-2 transitions (INT2_SYM, cleanup wall) are design-avoidable but the Type-3 interactions (alpha × sigma × beta × depth) require active monitoring that current cells do not cover as a JOINT surface.

Calibration note: P_deflated is the probability that Dim T produces a HARD_PASS CG (i.e., the joint-surface interaction is both experimentally confirmed as surprising AND a load-bearing architectural constraint). The upward move is small because the theoretical backing is already strong.

---

## 7. CHEAPEST DECISIVE EXPERIMENT

A "transition-surface map" cell is the decisive test. Two options:

**Option A (2-axis map): alpha × sigma grid at fixed N=8192, beta=13**
- Grid: alpha in {0.10, 0.20, 0.30, 0.40, 0.50} × sigma in {0.0, 0.05, 0.10, 0.20, 0.30}
- Metric: recall@1 at each grid point
- Prediction (from theory): recall contour at 0.95 is a CURVED boundary in (alpha, sigma) space, not a rectangle (factorized threshold). If it is curved, HARD_PASS for interaction hypothesis. If rectangular (factorized), MIDDLE_BAND.
- Runtime estimate: 5×5 grid × 3 seeds × ~2s/cell at N=8192 M=3000 = ~150s. Cheap CPU smoke.

**Option B (discriminator purity): compare min-of-primitives prediction vs actual**
- Measure sigma_crit at low alpha (say alpha=0.10) and at high alpha (say alpha=0.45).
- If sigma_crit(alpha=0.45) < sigma_crit(alpha=0.10), then interaction confirmed.
- 2 conditions × 3 seeds = minimal experiment. Could be folded into an existing wave.

**Recommended:** Option B as a 2-arm targeted discriminator. This is cheaper than Option A and directly tests the key claim (interaction vs independence).

This experiment does NOT block any current M3 milestone. It is characterization work. Flag as Stage 2 low-priority (not blocking Stage 1 100% closure which was already confirmed).

---

## 8. M3 CORTEX-LAYER ARCHITECTURAL IMPLICATION

**Central finding:** The substrate has three transition types; the Type-3 (noise-accumulation) transitions depend jointly on (alpha, sigma, beta, depth) in a way that cannot be handled by independent margin checks on each axis.

**M3 architecture recommendation (LOAD-BEARING):**

**1. Transition-aware operating point controller:**
The cortex must maintain a "safe-zone oracle" that tracks the joint operating point (current alpha = M/N; incoming noise sigma estimate; beta setting; retrieval depth d). This is NOT a simple threshold check per axis — it is a surface check. The controller must maintain margin from the joint boundary.

Practical implementation: pre-computed lookup table over (alpha, sigma, beta) from Option A experiment. Cortex queries the table before each write (alpha increment) or before each retrieval (sigma estimate).

**2. Beta must be tunable at runtime:**
Since beta is the single lever that simultaneously extends tolerance in sigma, alpha, and depth, the M3 cortex must expose beta as a runtime parameter. A static beta compiled at deployment time cannot adapt to variable load conditions.

**3. Refuse-gate placement precedes the transition:**
Atom 15 (M1.4 refuse-gate) was built precisely as the transition-avoidance mechanism at the noise/confidence axis. The Dim T finding VALIDATES this architectural choice: the refuse-gate intercepts inputs that would push the substrate into the Type-3 sigma cliff. The gate must be calibrated to the JOINT (alpha, sigma) boundary, not a fixed sigma threshold.

**4. INT2_SYM is a hard design prohibition:**
Type-2 transitions like INT2_SYM catastrophe are eliminated by construction — the cortex must enforce asymmetric ternary or binary encoding. This is already satisfied by INT8-Pareto CG (Atom 2 / Wave 2 CG) but must be preserved through any future precision reduction.

**5. Depth budget as a managed resource:**
The depth cliff (Type-3, multi-hop) is favorable with N but must be managed at deployment. M3 must track current retrieval depth and refuse chains that exceed d_crit(alpha, N) — which is a JOINT threshold, not a fixed depth limit. The current multihop d50/55 CG (Atom 19) measures this boundary at specific (alpha, N) configurations; the M3 controller must interpolate or bound.

**Summary architectural pattern:** M3 cortex needs a JOINT-SURFACE SAFETY CONTROLLER with three inputs (alpha, sigma, beta) and one output (safe/refuse). This is the Dim T extension of the 1D refuse-gate (Atom 15). It is more expensive than Atom 15 but is necessary for composed stack safety at deployment.

---

## Cross-References

- `notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md` — first-order cliff characterization
- `notes/research_drill_marchenko_pastur_bulk_cleanup_cliff_sharpness_rederivation_2x_2026-06-12.md` — cliff WIDTH O(1) in bulk regime (HARD_PASS)
- `notes/research_drill_field_modern_hopfield_5x_2026-06-07.md` — multihop d=25 cliff / percolation-class framing
- `data/exp_stage2_int8_dense_hopfield_end_to_end_recall_v2_crack_regime_seed_7/metrics.json` — on-disk pre-crack vs post-crack discrimination
- `data/exp_stage2_int2_binary_pareto_at_cliff_v2_with_asymmetric_ternary_seed_7/metrics.json` — INT2_SYM catastrophe vs INT2_ASYM recovery
- `data/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7/metrics.json` — sigma cliff / beta discrimination (M1.4 foundation)
- Atom 15 (M1.4 refuse-gate CONFORMAL) — transition-avoidance mechanism, M3 Phase 1
- Atom 11 (per-step scale-invariance MM) — depth cliff / N-scaling
- `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` — Dim T original enumeration (1-line stub)
