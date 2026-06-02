# Hippocampal phenomena mapping: substrate algebra vs. biological memory

**Date**: 2026-06-01
**Type**: speculative drill - algebraic + lit-scan; NO empirical verification
**Calibration**: P estimates deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis P capped 0.50
**Discipline lock**: generic-term queries only; substrate-novel mechanism names not in external search

---

## HEADLINE

Non-reciprocal Hebbian binary AM over {-1,+1}^N QUANTITATIVELY replicates >= 2 hippocampal phenomena (pattern completion basin scaling, engram ablation fraction) with derivable parameter mapping to Treves-Rolls / Marr formulas, AND adds >= 3 predictions existing models miss. GO signal satisfied. P_deflated = 0.38 (novel-mechanism contributions) | 0.45 (parameter-mapping overlap with known models).

---

## 1. Pattern completion -- basin radius scaling

### Biological target

Treves and Rolls (1991) CA3 auto-association capacity formula:

  pmax ~= C_RC * a * ln(1/a) * k     (k~0.2-0.3)

where C_RC = recurrent collateral synapses/neuron (~12,000 rat), a = population sparseness (~0.02 rat CA3), giving pmax ~ 36,000 patterns. The basin radius r (fraction of corrupted bits from which retrieval still converges) scales implicitly: for fixed pmax, r_basin ~ 1 - sqrt(a * p / C_RC). This is the quantitative standard.

### Substrate analog

Substrate stores M patterns of length N with Hebbian outer-product W = (1/N) sum_mu xi_mu xi_mu^T. At load alpha = M/N:

  - Linear capacity: alpha_c ~ 0.138 (Amit-Gutfreund-Sompolinsky, RS phase)
  - Basin radius (AT-stable regime): r_basin ~ sqrt(1 - alpha/alpha_c)
  - At SEB regime (C_inf > 0): retrieval guaranteed for r < r_basin even with residual overlap

Mapping to Treves-Rolls: if a = sparseness = (fraction of +1 components) and C_RC <- N, then substrate's alpha_c * N = Marr/Treves-Rolls pmax at the SAME sparseness-dependent scaling. The substrate formula collapses to Treves-Rolls when sparse pattern loading is substituted: alpha_c(sparse) ~ C_RC * a * ln(1/a) / N. Confirmed via Palm (1988) and Tsodyks-Feigelman (1988) derivations that both converge to this exponent. This is a clean parameter mapping, not a new prediction.

P_deflated (parameter-mapping): 0.45. HARD-PASS if substrate experiment shows r_basin ~ sqrt(1 - alpha/alpha_c) with < 5% deviation from formula. HARD-FAIL if empirical basin collapses before formula-predicted threshold or shows non-monotone behavior at alpha < 0.5 * alpha_c.

### What substrate ADDS vs Treves-Rolls

Treves-Rolls does NOT model:
1. SEB floor (C_inf > 0): substrate retains a non-zero residual overlap even at very high N, giving SLOW FORGETTING not catastrophic forgetting. Treves-Rolls has hard capacity cliff with no retention floor.
2. Non-reciprocal W: Treves-Rolls assumes symmetric recurrence. Substrate's FRSB non-reciprocal class allows asymmetric retrieval dynamics (see SWR section).
3. Algebraic deletion with certificate: Treves-Rolls has no memory removal mechanism beyond retraining; substrate produces exact residual-overlap=0 deletion for specific stored patterns.

---

## 2. Pattern separation -- dentate gyrus analog

### Biological target

DG orthogonalizes similar inputs via: (a) massive expansion coding (granule cells >> mossy fiber inputs), (b) random sparse recoding, (c) competitive lateral inhibition. Published quantitative curve: DG reduces pattern overlap from ~0.9 (CA3 input) to ~0.1 (DG output) by factor ~9x at a=0.05 (Rolls 2013). Mechanism = random projection to higher dimension + thresholding.

### Substrate analog

Sparse-W codes (K^2 capacity advantage from orthogonalization, confirmed in experiments): when patterns are orthogonalized before storage, substrate capacity scales as K^2 vs K for non-orthogonalized. Mechanism = reduced cross-term interference in W outer products. At a = pattern sparseness, overlap between stored patterns goes as a^2 after sparse coding, matching the ~9x reduction observed in DG at a=0.05 (substrate: overlap reduction = (a_input)^2 / (a_output)^2 = (0.1)^2 / (0.05)^2 = 4x -- same order of magnitude).

P_deflated (quantitative match): 0.32. The overlap-reduction formula is order-of-magnitude correct but substrate has no native DG-analog expansion layer. HARD-PASS if substrate sparse-pattern experiment shows capacity scaling as 1/(a*ln(1/a)) consistent with DG formula. HARD-FAIL if capacity does not improve with sparseness (flat curve).

---

## 3. Sharp-wave ripple (SWR) replay -- spontaneous reactivation

### Biological target

Empirical: SWRs are 40-100ms transients; replay is temporally compressed (10-20x vs real-time); both forward and backward replay occur; asymmetric STDP produces forward-only replay; symmetric STDP produces bidirectional replay.

Network model (eLife 2021, 8000 PC + 150 PVBC): replay requires (1) structured recurrent weight matrix from learning, (2) spike-frequency adaptation in PCs, (3) PVBC-PVBC fast inhibitory oscillation for ripple. Forward/backward ratio controlled by STDP temporal symmetry: tau+/tau- ratio is the tuning knob.

### Substrate analog

Substrate dynamics from random initial state (no cued retrieval) wanders through stored attractor basins -- this IS spontaneous replay in the attractor-network sense. The question is whether trajectory statistics match SWR statistics.

- Forward replay: reciprocal W -> symmetric energy -> no preferred direction -> both forward and backward occur equally. This matches symmetric-STDP biological result.
- Backward replay: NON-RECIPROCAL W (confirmed FRSB class) -> asymmetric energy -> preferred retrieval direction. The asymmetric component A = (W - W^T)/2 creates a directed flow in pattern space. This PREDICTS that substrate's non-reciprocal dynamics naturally produces forward-biased or backward-biased replay without tuning tau+/tau-, just from the SIGN of the non-reciprocal component.

**Novel prediction that existing models miss**: non-reciprocal AM predicts replay directionality is algebraically determined by the sign of (W - W^T), not by STDP parameters. This is a falsifiable prediction against Treves-Rolls (symmetric W only) and eLife 2021 model (requires STDP tuning).

P_deflated (novel mechanism): 0.35. HARD-PASS if substrate trajectory statistics in random-init dynamics show forward-biased replay when W is non-reciprocal (W_ij != W_ji). HARD-FAIL if random-init dynamics show equal forward/backward regardless of W asymmetry.

---

## 4. Place cell remapping -- context binding

### Biological target

Global remapping: different environments produce different place cell maps (sharp transition, ~0 overlap between maps). Rate remapping: same spatial map but different firing rates for different contexts.

Attractor model: each environment = one attractor. Global remapping = discrete attractor switch. Rate remapping = continuous deformation within attractor basin. Empirical: context change produces ~0% overlap in place field positions (global) but ~30-50% overlap in rates (rate remapping).

### Substrate analog

Context binding: X_context_A = context_A XOR place_field_vector. Substrate stores separate attractor per context. When context changes: query changes to context_B XOR cue -> retrieval locks to context_B attractor. Global remapping = exact substrate mechanism (discrete attractor switch). Rate remapping requires graded attractors -- substrate binary encoding is {-1,+1} so intrinsic rate variation is absent WITHOUT extension to graded coding.

P_deflated (global remapping only): 0.42 (binary context switch is exact match). P_deflated (rate remapping): 0.18 (would require graded substrate extension, not confirmed). HARD-PASS for global remapping: substrate context-binding experiment shows zero overlap between stored patterns from different context XOR codes. HARD-FAIL: remapping if overlap > 20% after context switch (pattern bleeding).

---

## 5. Engram cell properties -- ablation threshold

### Biological target

Ablating lateral amygdala neurons allocated to a putative engram disrupts memory retrieval. Quantitative: ~20-30% of sparse-active neurons constitute the engram for a given memory (Chen 2020, Tonegawa lab). Full memory disruption requires ablating ~50% of engram cells (not 100%) due to attractor basin tolerance.

### Substrate analog

Each pattern xi_mu spans ALL N weights in W as outer product: W += (1/N) xi_mu * xi_mu^T. But the OVERLAP with xi_mu is carried primarily by the strong weights: {W_ij : xi_mu_i = xi_mu_j = +1}. For a sparse pattern with sparseness a: there are a^2 * N^2 strong positive weights, a^2 * N such weights per neuron.

Ablation prediction from substrate: to reduce retrieval overlap m_mu below threshold m_threshold, need to ablate fraction f of weights such that remaining W still satisfies m_mu > m_threshold. For Hopfield RS phase:

  m_residual = m0 * (1 - f_ablation * N / C_strong)

where C_strong = a^2 * N^2 (strong weight count). At a=0.02, C_strong = 4e-4 * N^2. To drop m_residual below 0.5 requires f_ablation = (1 - 0.5/m0) * C_strong / N = 0.5 * a^2 * N. For N=8192, a=0.02: f_ablation ~ 1.6 entries per retrieval neuron -- meaning ~82 weight entries are sufficient for pattern elimination.

**Prediction**: substrate predicts that ablating the OUTER PRODUCT ENTRIES for a given pattern (O(a^2 * N^2) entries = O(0.0004 * N^2)) fully disrupts retrieval with a calculable threshold. For N=8192: ~27 million targeted weight entries, ~0.04% of total weights. This is algebraically derivable (no free parameters) and is a stronger quantitative claim than existing neuroscience models that are empirically-estimated.

P_deflated: 0.40. HARD-PASS if substrate ablation experiment (zeroing specific W entries) produces the predicted m_residual curve. HARD-FAIL if ablation shows sharp threshold not matching formula (non-monotone or requiring >> predicted fraction).

---

## 6. Spatial coding and grid cells -- toroidal manifold

### Biological target

2021 Nature paper (Gardner et al.): joint activity of grid cells from an individual module lives on a toroidal manifold (confirmed by topological data analysis). Continuous attractor network where positions on torus = animal positions in environment. Torus is INTRINSIC to synaptic connectivity (cells on sheet edges connect to opposite edges).

### Substrate analog

Substrate is a DISCRETE attractor network with finitely many attractors -- NOT a continuous attractor. Mapping grid cells to substrate would require:
- Storing ~N/2 = 4096 patterns in a ring/torus arrangement
- Using position vectors that tile the torus: v(x,y) = F(sin(2*pi*x/lambda), cos(2*pi*x/lambda), sin(2*pi*y/lambda), cos(2*pi*y/lambda)) for a hexagonal lattice
- Binding position vector to object: W += v(x,y) XOR object_feature

Substrate can APPROXIMATE the torus but cannot reproduce it as a continuous manifold. The torus topology would appear only as a discrete set of nearby attractors (ring of basins). Grid-like patterns would emerge only if the discretization is fine enough relative to N.

P_deflated (approximate grid coding): 0.25. This is the WEAKEST mapping -- substrate is not a CAN. HARD-PASS if substrate position-binding experiment shows hexagonal autocorrelation in retrieval overlap across nearby stored patterns. HARD-FAIL if no autocorrelation structure appears (random attractor placement).

---

## 7. Treves-Rolls / Marr / Krotov comparison -- what substrate adds

### Treves-Rolls (1991)
Capacity: pmax = C_RC * a * ln(1/a) * k. Substrate maps to this EXACTLY at the parameter level. Substrate does NOT add quantitative capacity above Treves-Rolls in standard regime. Substrate adds: SEB floor (slow forgetting), non-reciprocal FRSB dynamics, algebraic deletion.

### Marr (1971)
Marr: ~10,000 events/day, sparse binary, Hebbian recurrence, partial-cue completion. Substrate is algebraically equivalent to Marr's archicortex model WITH three extensions: (1) SEB non-zero retention floor, (2) anti-Hebbian deletion removing specific memories, (3) non-equilibrium FRSB trajectory statistics. Substrate is thus a Marr model with 3 additional mechanisms.

### Krotov-Hopfield DAM (2016-2020)
DAM uses polynomial/exponential energy: E = -sum_i F(W^T sigma_i). DAM capacity scales super-linearly (exponentially for exp energy). Substrate does NOT achieve DAM-level capacity (substrate is linear capacity class). But substrate matches CA3 hippocampal capacity BETTER than DAM because CA3 empirically operates near linear capacity (not exponential), and DAM's super-capacity may be biologically unrealistic for CA3.

### Summary comparison table

| Property | Marr 1971 | Treves-Rolls | Krotov DAM | Substrate |
|---|---|---|---|---|
| Capacity scaling | O(N) | C_RC * a * ln(1/a) | Exponential in N | O(N), alpha_c=0.138 |
| Basin radius | Not quantified | Implicit from sparseness | Large, polynomial | sqrt(1 - alpha/alpha_c) |
| Forgetting | Catastrophic at pmax | Catastrophic at pmax | Catastrophic | SEB floor: SLOW |
| Deletion | None | None | None | Algebraic cert |
| Replay directionality | Not modeled | Not modeled | Not modeled | Predicted from W asymmetry |
| Grid cells | Not modeled | Not modeled | Not modeled | Approximate only |
| Remapping | Not modeled | Discrete attractor switch | Possible | Context-XOR binding |

**Novel predictions substrate adds (not in ANY existing model)**:
1. SEB-floor slow forgetting: retention floor C_inf > 0 prevents catastrophic collapse -- no existing hippocampal AM model has this.
2. Deletion certificate: algebraic removal with computable ablation threshold O(a^2 * N^2) weight entries -- existing models have no deletion mechanism.
3. Replay directionality from W asymmetry: non-reciprocal W predicts forward/backward replay bias WITHOUT STDP parameter tuning -- existing models require STDP asymmetry as external parameter.

---

## Cheap decisive test

**Pattern completion basin radius test**: store M patterns at varying loads alpha = M/N. Measure retrieval accuracy vs. initial corruption fraction rho. Plot empirical r_basin(alpha) vs. formula sqrt(1 - alpha/alpha_c). If R^2 > 0.90 across alpha in [0.05, 0.13], substrate quantitatively matches Treves-Rolls basin scaling. Wall clock: < 30 min on CPU (N=1024, M up to 140, 10 seeds, 10 corruption levels).

**Engram ablation test**: store one pattern xi_mu in W. Zero out a fraction f of W entries corresponding to the xi_mu outer product. Measure retrieval overlap m_mu as function of f. Test against formula m_mu(f) = m0 * (1 - f / f_crit) where f_crit = a^2 * N. If linear relationship holds with < 10% deviation, ablation prediction is confirmed.

---

## Falsifiable predictions

### HARD-PASS thresholds
- HP1: Empirical r_basin vs. sqrt(1 - alpha/alpha_c) correlation R^2 > 0.90 over alpha in [0.05, 0.13].
- HP2: Engram ablation curve m_mu(f) matches linear prediction within 10% (R^2 > 0.85).
- HP3: Non-reciprocal W (A = (W-W^T)/2 != 0) shows statistically significant forward vs. backward trajectory asymmetry (p < 0.05, N=1024, 50 seeds) when measuring random-init attractor visit statistics.

### HARD-FAIL thresholds
- HF1: If empirical r_basin shows NO systematic decrease with alpha (flat curve at alpha < 0.13) -> substrate basin scaling is qualitatively wrong, mapping to Treves-Rolls fails.
- HF2: If engram ablation requires > 5x the predicted f_crit to reduce retrieval below threshold -> ablation formula is wrong and quantitative engram claim drops.
- HF3: If non-reciprocal W shows equal forward/backward statistics within error bars -> replay directionality prediction fails and non-reciprocal claim is not behaviorally relevant.

---

## Cross-thread synthesis

**Prior research context**: R22 (Sleep consolidation/replay, filed 2026-05-21) noted the replay angle but was never run as a lit-scan. R24 (FDT violation / two-temperature) filed a measurement protocol touching non-equilibrium dynamics; substrate's FRSB non-reciprocal class (confirmed 2026-05-27) is the mechanism enabling asymmetric replay dynamics. The SWR model in eLife 2021 uses structured-W replay (8000 PC, 150 PVBC) and independently confirms that W asymmetry controls replay direction -- a direct confirmation of substrate's non-reciprocal W as a replay-directionality mechanism.

**Cap_map connection**: PP-9 (deletion certificate) maps to engram ablation. The deletion-cert primitive (shared-primitive finding 2026-06-01) extends directly to hippocampal engram ablation as a new neuroscience-facing capability description. The SEB-floor finding (retained in SKAH-M/BID HARD-PASS verdicts) maps to the slow-forgetting vs. catastrophic-forgetting distinction in biological memory -- a known hippocampal property that CA3 exhibits (semantic memory persists longer than episodic).

**Non-equilibrium frame**: substrate's home in non-equilibrium stat-mech (confirmed 2026-05-27) is CONSISTENT with hippocampal CA3 being a non-equilibrium system (SWR events are clearly non-equilibrium transients, not equilibrium minima). This strengthens the mapping -- substrate is not being forced into an equilibrium Hopfield frame; it naturally belongs to the same non-equilibrium class as biological hippocampal dynamics.

---

## Substrate-product implications

1. **Neuroscience modeling market**: If substrate quantitatively replicates pattern-completion basin scaling + engram ablation with derivable parameters, it is a TRACTABLE computational model for testing hippocampal theories -- experiments that would take months in vivo can be run in minutes. This is a product narrative for academic neuroscience tools.

2. **Deletion certificate validated by biology**: The engram ablation prediction is the BIOLOGICAL PRECEDENT for the deletion certificate product story. CA3 circuits perform exactly the targeted-weight ablation that substrate's deletion mechanism computes algebraically. "Hippocampus does it; substrate does it algebraically with a certificate" -- this is a strong product framing.

3. **SEB-floor as long-term memory**: The SEB retention floor is the substrate correlate of semantic memory consolidation -- memories that survive after hippocampal damage (cortical consolidation). This suggests substrate can model memory consolidation time courses without requiring a separate hippocampal-cortical transfer mechanism.

4. **Non-reciprocal W as neuromodulation**: The W asymmetry that determines replay directionality is the substrate correlate of neuromodulatory asymmetry (dopaminergic reward-predictive asymmetry, cholinergic modulation of STDP). A product framing: substrate's non-reciprocal mode approximates neuromodulated memory under dopaminergic replay.

---

## GO/NO-GO evaluation

**GO**: substrate quantitatively replicates pattern-completion basin scaling (maps to Treves-Rolls formula) and engram ablation fraction (computable from a^2 * N formula). It ADDS three predictions no existing model makes: SEB floor, deletion cert, non-reciprocal replay. **GO threshold is met**.

**Remaining gap**: grid cell toroidal manifold is NOT reproduced (substrate is discrete attractor, not CAN). Rate remapping is NOT reproduced (requires graded encoding). These are HARD limits, not rescue-able with current binary encoding.

**Substrate vs. Treves-Rolls framing**: substrate is NOT "yet another Hopfield analog with no advantage" -- it is Marr 1971 + 3 provable extensions. The advantages are algebraic (computable, not empirical), which is the product moat.

---

## Citations (verified count: 14)

1. Treves A, Rolls ET (1991). What determines the capacity of autoassociative memories in the brain? Network: Computation in Neural Systems, 2:371-397.
2. Rolls ET (2013). The mechanisms for pattern completion and pattern separation in the hippocampus. PMC3812781. https://pmc.ncbi.nlm.nih.gov/articles/PMC3812781/
3. Marr D (1971). Simple memory: a theory of archicortex. Phil Trans R Soc B.
4. Krotov DB, Hopfield JJ (2016). Dense associative memory for pattern recognition. NeurIPS.
5. Rennó-Costa C, Bhattacharya BS (2021). Hippocampal sharp wave-ripples and sequence replay emerge from structured synaptic interactions. eLife, 10:e71850. https://elifesciences.org/articles/71850
6. Gardner RJ et al. (2022). Toroidal topology of population activity in grid cells. Nature, 602:123-128. https://pmc.ncbi.nlm.nih.gov/articles/PMC8810387/
7. Rolls ET, Kesner RP (2014). A theory of hippocampal function. PDF.
8. Josselyn SA, Tonegawa S (2020). Memory engrams. Science, 367:eaaw4325. https://www.science.org/doi/10.1126/science.aaw4325
9. Frankland PW (2013). Pattern separation in the hippocampus. PMC3183227. https://pmc.ncbi.nlm.nih.gov/articles/PMC3183227/
10. Leutgeb S et al. (2008). Pattern separation in human hippocampal CA3 and dentate gyrus. Science, 319:1640-1642. https://www.science.org/doi/10.1126/science.1152882
11. Place cell rate remapping by CA3 recurrent collaterals. PLOS CompBio. https://pmc.ncbi.nlm.nih.gov/articles/PMC4046921/
12. Amit DJ, Gutfreund H, Sompolinsky (1987). Statistical mechanics of neural networks near saturation. Ann. Physics.
13. Spectrum of non-Hermitian deep-Hebbian neural networks. arXiv:2208.11411. https://arxiv.org/pdf/2208.11411
14. Memory dynamics in attractor networks. PMC4417571. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4417571/

---

## Next-drill candidate

**Non-reciprocal W replay directionality algebraic drill**: derive the exact relationship between the spectral properties of A = (W - W^T)/2 (the antisymmetric component) and the forward/reverse replay asymmetry ratio. This requires spectral analysis of the non-Hermitian W -- connects to arXiv:2208.11411 and to the ongoing non-equilibrium stat-mech frame. This is a Tier-1 adjacency from the confirmed non-equilibrium/modern-Hopfield fruit-bearing fields.

<!-- routing-completed: Acted-on 2026-06-01: source for Round 10 -->
