# Research drill: rank-1-diagonal SYM readout limitation — brain-check on rank vs. dimensionality/expansion

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan sub-agents)
Date: 2026-07-15
Trigger: standing rule — every mechanism limitation gets a brain-check. Detection decider measured SYM (symmetric-bind readout) as a RANK-1 DIAGONAL bilinear (score = Σ_d W_d·e_{a,d}·e_{b,d}), with noise-free synthetic-plant AUC degrading as interaction rank increases: rank1=0.975, rank2=0.851, rank3=0.711, rank4=0.693.
Research-only. No code, no compute, no cell dispatch.

---

## HEADLINE

**The brain is ALSO rank-limited per readout unit — it does not evade this by building an explicit high-rank operator. It evades it by SUMMING many independent low-rank (near-rank-1) nonlinear terms — either across dendritic subunits within one neuron, or across neurons in a mixed-selectivity population — and reading THAT sum out linearly. This is architecturally a sum-of-rank-1 (CP/tensor-rank) decomposition, not a giant rank-R bilinear form and not a purely-random high-dimensional blind expansion.**

**On the key hypothesis — is "rank" the same lever as "dimensionality/expansion"? Answer: CONDITIONALLY YES, with a load-bearing caveat.** For a **learned** (fit-to-data) expansion, rank R and dimension-R embedding + diagonal/linear readout are **literally the same mathematical object** (Eckart-Young-Mirsky / CP-rank identity — no conversion cost, D=R exactly). For a **random/fixed (unlearned)** expansion, they are **different levers with a real, provable overhead tax**: required dimension D to capture a rank/degree-R interaction to fidelity ε scales *worse* than R — exponentially in R for the direct tensor-sketch construction, polynomially in refined versions, and with a log(N) (not R) dependence for generic (task-agnostic) Johnson-Lindenstrauss-style embeddings. The brain's actual circuits (cerebellar granule cells, mushroom-body Kenyon cells, dendritic branch subunits) sit closer to the **cheap, no-tax regime** because their expansions are not blindly random — they are genetically/developmentally structured (fixed but non-arbitrary sparse connectivity, optimized in-degree) with a **learned linear readout** on top (Purkinje cells, place-cell weights, MBONs), i.e. the biological architecture is a reservoir-computing/extreme-learning-machine instance, not a naive-JL instance — and even there, dimensionality is NOT unboundedly cheap: Litwin-Kumar et al. (2017) prove an explicit **optimal (peaked, U-shaped) in-degree** for granule-cell/Kenyon-cell expansion, i.e. biology pays a real, finite-resource cost and tunes against it rather than treating "more dimensions" as free.

**Substrate translation:** the rank-1-diagonal SYM wall is best patched near-term by an **explicit learned low-rank-R bilinear** (R ∈ {2,4,8}) — the zero-overhead, CP-rank-identity fix, directly homologous to the dendritic-subunit / sigma-pi solution biology actually uses at the single-neuron level. The "high-dim expansion + simple readout" route (reusing the substrate's existing sparse-expansion phase-diagram regime) is the more brain-aligned population-level story in the BIG picture, but it is NOT free: it requires (a) the expansion's nonlinearity to actually generate multiplicative/product cross-terms (a sparse linear-threshold expansion does not automatically do this — you need something structurally like a quadratic/tensor-sketch feature), and (b) a dimension budget that the math says grows fast with target rank when the expansion is not purpose-built for that rank. Recommend explicit rank-R as the near-term cheap decisive test; treat expansion-route as a longer-term, higher-engineering-cost structural question.

---

## Cheap decisive test

**Primary test — explicit rank-R bilinear vs. the measured rank1→rank4 degradation curve:**

Implement `score(a,b) = Σ_{r=1}^{R} w_r · (P_r·a)(Q_r·b)` (R independent learned rank-1 projection pairs, summed — i.e. an R-term CP/tensor-rank decomposition of the bilinear form) as a drop-in alternative readout to the current single-term diagonal SYM. Sweep R ∈ {1 (control, = current SYM), 2, 4, 8} against the SAME noise-free synthetic plant used for the rank1–rank4 interaction-order sweep that produced the 0.975/0.851/0.711/0.693 curve.

**Secondary test — random high-dim expansion + rank-1 readout, as a contrast arm:** take the substrate's existing sparse-expansion phase-diagram regime (already-built dimensionality-expansion code), add a rank-1 (diagonal/linear) readout on top, and sweep expansion width D against the same rank2/rank3/rank4 plant. This directly measures whether the EXISTING expansion nonlinearity is rich enough to carry product/interaction structure, or whether it needs augmentation (e.g., an explicit pairwise-product/quadratic feature à la tensor-sketch) before a simple readout can exploit it.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 (explicit rank-R closes the gap — CP-identity prediction):**
- HARD-PASS: R = ground-truth rank (or R = 2×ground-truth rank as safety margin) recovers AUC ≥ 0.95 at rank2 (R=2 or 4), ≥ 0.90 at rank3 (R=4 or 8), ≥ 0.90 at rank4 (R=8) — i.e., closes ≥ 90% of the measured gap vs. the rank-1-diagonal baseline at each order.
- HARD-FAIL: increasing R from 1→8 improves AUC by < 0.03 at any tested rank order. This would falsify the "it's a capacity/expressivity bottleneck" read and instead implicate an optimization/identifiability failure (e.g., the R rank-1 terms can't be fit stably) or a plant-construction mismatch (the synthetic interaction isn't actually CP-rank-R structured in the way assumed).

**Prediction 2 (expansion + simple-readout route — dimension-tax prediction):**
- HARD-PASS: expansion width D in the range O(10×R) to O(100×R) (cheap, matches the "learned-ish / structured" biological regime, not a blind-JL regime) recovers AUC within 0.03 of the explicit-rank-R result at matched interaction order.
- HARD-FAIL: no expansion width up to D = 1000×R closes more than half the gap — this would confirm the theory-predicted tax (random/unstructured expansion pays exponential-in-R or log(N) overhead) and rule out "just make the existing expansion bigger" as a cheap fix; the expansion's nonlinearity itself would need re-architecting (explicit product/quadratic features), not just widening.

**Prediction 3 (brain-analogy consistency check, no compute needed — literature-only):** if dendritic-subunit-style "sum of independent low-rank terms" is truly the operative brain mechanism, then R (number of terms) needed to hit a target interaction order should scale roughly LINEARLY with the order/rank of the interaction being captured (consistent with CP-rank identity), not exponentially — this is a check the substrate math result should self-confirm if Prediction 1 HARD-PASSes.

## Cross-thread synthesis

**Bilinear wall:** the just-measured SYM rank-1-diagonal ceiling (0.975→0.693 as rank rises) is the substrate-native instance of exactly the "single rank-1 readout under-captures higher-rank structure" phenomenon that Poirazi & Mel (2001, 2003) modeled explicitly for single neurons (a linear-summation neuron ≈ our rank-1 case; adding independent nonlinear dendritic subunits ≈ our rank-R generalization) and that Rigotti/Fusi (2013) modeled at the population level (a single non-mixed-selectivity readout can't cover combinatorially many task-variable mixtures; a high-dimensional mixed-selectivity population lets a SIMPLE downstream readout cover them). Both literatures independently converge on: **don't build one big expensive high-order operator — sum many small ones (branches, or neurons), then read out simply.** This is a direct structural validation of pursuing explicit-rank-R (a "few small operators summed") over "one big rank-4 tensor."

**Joint-code:** if the substrate's joint/composite code already encodes both members of a pair in a shared space, the rank-R generalization is a near-zero-disruption change — it only touches the readout (add R−1 more projection-pairs and sum), not the encoding. This matters because the ENCODING LEVER finding (native bind commutativity wall; match code to data structure) says encoding changes are the harder, architecturally-constrained move — whereas a readout-side rank-R fix is comparatively cheap and reversible, consistent with the "OPTIMIZE-THEN-NATIVIZE" discipline (fix the readout before touching the bind/encode layer).

**Phase-diagram sparse-expansion regime:** this drill's secondary test (Prediction 2) is the correct way to ask "can we get the rank-R fix for free by reusing the expansion regime we already built for a different purpose (capacity/pattern-separation)." The kernel/tensor-sketch literature's central finding — that BLIND/unlearned expansions pay a tax that grows with target interaction order (exponential in the raw TensorSketch bound, polynomial in refined versions, log(N) for generic JL) — predicts this reuse will be MORE expensive in dimension-budget than a purpose-built rank-R operator, unless the expansion's nonlinearity is specifically product/quadratic-capable (which a sparse linear-threshold expansion, as typically built for capacity reasons, is not guaranteed to be). This is a testable, falsifiable prediction (Prediction 2), not a dismissal — per the standing "don't pre-judge adjacent methods" discipline, it should still be run as the contrast arm, but expectations should be calibrated: it is the LESS likely of the two routes to be cheap.

## Substrate-product implications

1. **Near-term fix, high confidence of being the right SHAPE of fix:** generalize the SYM readout from rank-1-diagonal to an explicit sum of R learned rank-1 terms (R ∈ {2,4,8}), i.e. a small CP/tensor-rank decomposition. Parameter cost is O(R·d) — cheap for R≤8. This is mathematically the EXACT (zero-overhead) way to represent a rank-R interaction, per Eckart-Young-Mirsky/CP-rank identity, and it is the direct homolog of the dendritic-subunit (sigma-pi/clusteron) solution biology uses at the single-neuron level for the identical problem (a single linear-summation unit under-capturing multi-way structure).
2. **Do NOT assume "just widen the existing sparse-expansion layer" is a free substitute.** The math says a blind/generic dimensionality expansion pays a real tax that grows with target interaction order; it is only "free" (D≈R) when the expansion is effectively LEARNED/fit to the target structure, which the current expansion regime (built for capacity/pattern-separation, not for reading out this specific bilinear structure) is not. Treat Prediction 2 as a genuine open question worth one contrast-arm test, not as the primary fix.
3. **Longer-term, brain-aligned direction:** the two routes are not mutually exclusive at the architecture level — biology's real circuits (cerebellar/mushroom-body) combine a genetically-structured (not random, not fully learned) expansion with a LEARNED linear readout, which is functionally a middle ground between explicit-rank-R and blind-expansion. If a future substrate iteration wants a MORE brain-aligned solution than a hand-picked R, the direction to explore is: fixed/structured (not random, not learned) moderate expansion + learned linear readout, sized against an explicit optimal-dimensionality criterion (Litwin-Kumar-style), rather than either extreme.
4. **This does not change the bind-commutativity wall finding** — the rank-R generalization is purely a readout-side change; it says nothing new about whether native bind can be made non-commutative. Keep these two threads separate in the cap_map.

## Citations (verified count: 4 independent Sonnet lit-scan passes, ~26 distinct primary/secondary sources cross-cited; treat as HIGH confidence on the underlying math/neuro claims, MEDIUM-LOW on substrate-specific application)

- Rigotti, Barak, Warden, Wang, Daw, Miller, Fusi — "The importance of mixed selectivity in complex cognitive tasks," *Nature* 496 (2013).
- Fusi, Miller, Rigotti — "Why neurons mix: high dimensionality for higher cognition," *Curr Opin Neurobiol* 37 (2016).
- Cover — "Geometrical and Statistical Properties of Systems of Linear Inequalities with Applications in Pattern Recognition," IEEE Trans. Electronic Computers (1965).
- Rahimi & Recht — "Random Features for Large-Scale Kernel Machines," NeurIPS (2007); and "Uniform Approximation of Functions with Random Bases," Allerton (2008).
- Sutherland & Schneider — "On the Error of Random Fourier Features," UAI (2015), arXiv:1506.02785.
- Pham & Pagh — "Fast and Scalable Polynomial Kernels via Explicit Feature Maps" (TensorSketch), KDD (2013).
- Ahle et al. / Zandieh et al. — "Oblivious Sketching of High-Degree Polynomial Kernels" (degree-dependence refinement of TensorSketch).
- Kolda & Bader — "Tensor Decompositions and Applications," SIAM Review (2009) [CP-rank, Eckart-Young-Mirsky context].
- Sarlós — subspace-embedding / oblivious random-projection bounds (2006); "Random Embeddings with Optimal Accuracy," arXiv:2101.00029.
- Donoho & Tanner — compressed-sensing phase-transition results.
- Mei & Montanari — "The Generalization Error of Random Features Regression," CPAM (2022).
- Huang, Zhu, Siew — "Extreme Learning Machine: Theory and Applications," Neurocomputing (2006).
- Grigoryeva & Ortega — "Echo State Networks are Universal," Neural Networks (2018), arXiv:1806.00797; Gonon & Ortega follow-ups.
- Poirazi & Mel — "Impact of Active Dendrites and Structural Plasticity on the Memory Capacity of Neural Tissue," *Neuron* (2001).
- Poirazi, Brannon, Mel — "Pyramidal Neuron as Two-Layer Neural Network," *Neuron* (2003).
- Polsky, Mel, Schiller — "Computational subunits in thin dendrites of pyramidal cells," *Nat Neurosci* (2004).
- London & Häusser — "Dendritic Computation," *Annu Rev Neurosci* (2005).
- Solstad, Moser, Einevoll — "From grid cells to place cells: a mathematical model," *Hippocampus* 16 (2006).
- Sargolini et al. — conjunctive grid × head-direction cells, *Science* (2006).
- Whittington et al. — "The Tolman-Eichenbaum Machine," *Cell* (2020).
- Litwin-Kumar, Harris, Axel, Sompolinsky, Abbott — "Optimal Degrees of Synaptic Connectivity," *Neuron* (2017).
- Cayco-Gajic & Silver — "Re-evaluating Circuit Mechanisms Underlying Pattern Separation," *Neuron* (2019).
- Dasgupta, Stevens, Navlakha — "A neural algorithm for a fundamental computing problem" (fly olfactory LSH), *Science* (2017).
- Caron et al. — "Random convergence of olfactory inputs" (mushroom body wiring), (2013).

**P_deflated = 0.42** (novel-synthesis cap 0.50 applied, further deflated for substrate-specific transfer uncertainty per lit-scan calibration penalty). Breakdown: confidence in the underlying MATH/NEURO claims themselves (rank≡dimension for learned case; brain uses sum-of-low-rank-terms) is HIGH (~0.75-0.85 per sub-thread); confidence that the specific recommended fix (explicit rank-R ∈ {2,4,8}) closes the MEASURED substrate AUC gap when actually implemented is capped lower because it is an untested prediction on this substrate's specific plant/optimization landscape (Prediction 1's HARD-FAIL branch — an identifiability/optimization failure rather than a capacity failure — is a real, non-negligible risk not ruled out by the literature).

## Next-drill candidate

If Prediction 1 lands HARD-PASS: no further research needed, hand to exp_dev as an operator-enrichment cell (rank-R bilinear sweep).
If Prediction 2 is of interest as a contrast arm and the substrate wants the brain-aligned "expansion" route explored more: next field to drill is `sparse-coding-compressed-sensing` (Tier-1b, adjacent to free-probability/AMP-VAMP) — specifically compressed-sensing phase-transition scaling laws (Donoho-Tanner) applied to "how many random expansion dimensions are needed to make a rank-R interaction linearly readable," which would sharpen Prediction 2's D-budget estimate beyond the qualitative bound found here.
