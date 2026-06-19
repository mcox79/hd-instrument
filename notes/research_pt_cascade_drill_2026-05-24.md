# Research drill — Adaptive parallel tempering temperature scheduling -> replay-timescale cascade design

**Date**: 2026-05-24
**Role**: Research (2x adjacency-cascade follow-up to prior hierarchical-replay + 1-RSB drill)
**Calibration**: lit-scan penalty applied (P estimates deflated 0.15-0.25; novel-synthesis P capped at 0.50) per [[feedback-lit-scan-calibration-penalty]]. Substrate-specific framing held out of all WebSearch queries per [[feedback-query-privacy-decomposition]].
**Drill discipline**: 2x = depth on three sub-questions, not re-verification of prior drill per [[feedback-2x-means-depth]].

---

## TL;DR (for orchestrator triage)

Across ~40 years of parallel-tempering (PT) literature, three results are well-established and one important negative:

1. **Cascade depth ~ sqrt(system size).** Optimal number of temperatures scales as sqrt(N) for simple systems; round-trip time scales as (n_T)^2 (diffusive in temperature space). Nadler & Hansmann 2007 (arXiv:0709.3289); Machta 2009 (arXiv:0908.0012).
2. **Spacing rule has two equally-defensible asymptotic targets**: 23.4% acceptance (optimal in high-dimensional Atchade-Roberts-Rosenthal diffusion limit; recently re-validated in low dimensions by Hird & Livingstone 2024, arXiv:2408.06894) vs 50% (Kone-Kofke / common practice for moderate D). Both reduce to GEOMETRIC spacing only for near-Gaussian / quadratic landscapes; geometric fails generically at phase transitions per Katzgraber-Trebst-Huse-Troyer 2006 (arXiv:cond-mat/0602085).
3. **Homogeneous-schedule failure mode IS real** at phase transitions / glass crossovers — diagnosed by replica round-trip slowdown and acceptance-rate dips at specific T-bands; rescued by adaptive densification (Katzgraber feedback-optimized), policy-gradient adaptive (Patel et al 2024, arXiv:2409.01574, 3.4x-8.8x ACT improvement on Egg-box/Rosenbrock), or learned-proposal augmentation (IsingFormer / Bunaiyan et al 2025, arXiv:2509.23043).
4. **NEGATIVE finding** (the load-bearing one for our Pred-5 question): the PT literature does **NOT** establish that optimal cascade depth is a DISCRETE function of basin/cluster/RSB-hierarchy depth. The cascade-depth question is answered by a CONTINUOUS rule (sqrt(N) replicas, adaptively densified at the bottleneck) — not by matching k+1 in k-RSB or log2(number of basins). Where PT theory engages with RSB structure (Billoire-Marinari, Alvarez-Banos), the practical recommendation remains "add replicas until round-trip time saturates and put extras near the bottleneck", not a closed-form depth-matching rule. Confidence: 0.55 (calibration-deflated; we can't prove the absence of an unpublished result, but the major PT reviews 2018-2025 do not assert such a rule and ablation studies that would have found it would be cited).

---

## (a) Optimal cascade structure — what the PT literature establishes

### A1. Cascade depth (number of replicas n_T)

**Sqrt-N scaling**: For simple systems, n_T optimally scales as sqrt(N) where N = degrees of freedom; for a double-well barrier of height Delta, optimal n_T scales as sqrt(Delta). This yields an exponential speedup over single-replica MCMC. (Nadler-Hansmann arXiv:0709.3289; Machta arXiv:0908.0012; Katzgraber strengths-and-weaknesses review). Confidence 0.75 (calibration-deflated from 0.90; result is decades-old and benchmarked, but most studies are on equilibrium spin systems, not on replay-driven continual learning — the analogy step is where uncertainty enters).

**Empirical anchors**: 56 replicas for 3D Edwards-Anderson at L=10 (N=1000); 22 replicas in IsingFormer 3D spin glass L^3=10^3; 15 replicas in Patel et al Egg-box / Rosenbrock benchmarks; 8-15 replicas in Factorization benchmarks. So "small-to-moderate" (8-30) for D~10^3-10^4 problems; one to two dozen replicas is the empirical operating regime.

**Implication for replay-timescale cascade**: if "system size" maps to effective task-distribution dimensionality / number of stored items K, then a sqrt(K) cascade-depth scaling is the literature-supported guess. For K~10^3-10^4 (substrate's continual-learning regime), 3-30 cascade levels is the recommended search band — NOT 100+, NOT 2.

### A2. Spacing ratio

**Two competing optimality targets**:
- 23.4% acceptance: Atchade-Roberts-Rosenthal asymptotic diffusion limit (D -> infinity, product target). Re-validated by Hird & Livingstone 2024 (arXiv:2408.06894) for surprisingly low dimensions and non-iid targets. Becomes 13.5% for discontinuous targets.
- 50% acceptance: Kone-Kofke 2005 (J Chem Phys; classical chemistry-community convention); roughly the heuristic for moderate D.

**Geometric spacing**: optimal ONLY for Gaussian / quadratic energy distributions; Katzgraber-Trebst-Huse-Troyer 2006 (arXiv:cond-mat/0602085) showed that achieving uniform acceptance via geometric is not the right target — the FEEDBACK-OPTIMIZED schedule densifies replicas at bottlenecks (phase transitions) and explicitly accepts non-uniform acceptance rates.

**Implication for replay cascade**: blindly imposing geometric timescale spacing (e.g., tau_k = 2^k) is the analog of the Katzgraber failure mode. If continual-learning landscape has a "critical" task-shift band where forgetting is sharpest, the replay timescales should be densified there — NOT uniform-geometric.

### A3. Online-adaptive update rules

Three families, each well-established:

- **Robbins-Monro / stochastic-approximation tuning of T_i**: maintains target swap acceptance; provably-convergent (Atchade-Roberts-Rosenthal 2011 family of "Adaptive PT" algorithms).
- **Feedback-optimized iterative**: Katzgraber et al 2006; iteratively densifies where measured replica flow is slow.
- **Infinite-swap limit**: Plattner-Doll-Dupuis-Wang 2011 / Lu-Vanden-Eijnden 2019; mathematically simpler limit where swap moves are made infinitely fast; loses replica-distinguishability but improves diffusion.
- **Policy-gradient adaptive**: Patel et al Sep 2024 (arXiv:2409.01574); RL-trained scheduler with swap-mean-distance reward beats both geometric and uniform-acceptance baselines by 3.4x (Rosenbrock) to 8.8x (Egg-box) in autocorrelation time.

**Implication for replay cascade**: an online learning rule that adapts the cascade timescales based on observed forgetting / replay-effectiveness signal is the literature-preferred design, not a fixed schedule.

### A4. What is "optimal" relative to what objective?

This is where the literature splits and where exp_dev must commit upfront:

- **Round-trip time** (Katzgraber): minimum time for a replica to traverse from T_min to T_max and back. Best when the goal is exploration / ergodicity.
- **Integrated autocorrelation time** (Patel et al; Machta): direct proxy for sampling efficiency at a fixed observable. Best when the goal is precise estimates of specific quantities.
- **Mean first passage time across the transition** (Nadler-Hansmann): time to first reach the low-T basin from high-T. Best when the goal is rare-event sampling / ground-state finding.
- **Ensemble diversity / KL coverage**: not standard in PT literature; would be the relevant criterion for replay if the goal is "retain coverage over past task distribution".

**Hard-fail threshold (Pred-5 design)**: if the substrate's cascade-depth sensitivity sweep does NOT show a measurable monotone improvement up to n ~ sqrt(K_effective) and saturation thereafter, that is evidence AGAINST the PT-analogy framing being load-bearing. Specifically: if 1-cascade and 16-cascade have indistinguishable forgetting profiles (within 2 sigma) at K=4096, the cascade-depth lever is not the active mechanism — look elsewhere.

---

## (b) Homogeneous-schedule failure mode at computational phase transitions

### B1. The failure mode itself

Confirmed across ~3 decades of PT literature. Standard formulation: at a phase transition (first-order, glass, SAT-UNSAT, RSB transition), the energy distributions of adjacent replicas develop a bimodal structure that DECOUPLES under standard local updates, leading to:
- exchange-rate dips at the T-band straddling the transition (specific replica indices i,i+1 have acceptance << target)
- replica round-trip histograms that bottleneck (replicas accumulate above or below the transition; few make a full traverse)
- autocorrelation times that scale exponentially (not polynomially) with barrier height in the homogeneous regime
- specifically for FIRST-ORDER transitions, the energy discontinuity makes adjacent-replica acceptance exponentially small in system size unless the schedule is densified near T_c

(Refs: Predescu-Predescu-Ciobanu 2004; Bittner-Nussbaumer-Janke arXiv:0809.4020; Machta 2009 review; Frigessi et al Chemistry 2024 analytical review.)

Confidence 0.80 (calibration-deflated from 0.90; the phenomenon is mature literature).

### B2. arXiv:2509.23043 (IsingFormer, Bunaiyan et al Sep 2025) — direct fetch

What the paper claims:
- Identifies the general failure mode "MCMC mixes slowly near critical points and in rough landscapes; PT improves mixing by swapping replicas across temperatures, yet each replica still relies on slow local updates."
- Uses adaptive scheduler (Isakov et al 2015) as their baseline PT schedule (so they accept that homogeneous IS suboptimal).
- 22 replicas for 3D spin glass L^3=10^3; 8 replicas for 8-bit factorization; 15 replicas for 16-bit factorization.
- **What the paper does NOT do** (important for our drill calibration): does not provide round-trip-time histograms, does not analyze RSB / basin structure, does not isolate whether their gain comes from learned global moves vs the adaptive temperature schedule. So this paper is NOT a definitive reference for cascade-depth-vs-hierarchy theory; it is a reference for "learned global proposals compose with PT".
- Their TAPT (Transformer-Augmented PT) result: learned proposals "replace thousands of local updates" — i.e., the rescue is to break the slow-local-update bottleneck, not to redesign the ladder.

### B3. Diagnostic signatures practitioners use

In rough order of practitioner utility:
1. **Replica round-trip histogram f(i)**: count of times each replica index visits T_min and T_max. Flat = healthy; bimodal / spiked = bottleneck at the slow indices. (Trebst-Troyer-Hansmann; standard since ~2004.)
2. **Acceptance-rate-vs-index plot**: dip below the target rate at specific i pinpoints the bottleneck temperature.
3. **Free-energy histogram overlap between adjacent replicas**: if adjacent energy histograms are bimodal AND their modes don't overlap, the schedule is broken at that boundary.
4. **Autocorrelation time vs replica index**: spike at bottleneck index.
5. **Population annealing analog** ("rho_t" effective population size at each T-step): direct readout of how many independent replicas survive the annealing step (Wang-Machta-Katzgraber 2015 arXiv:1508.05647).

**Hard-fail threshold (Pred-5 diagnostics)**: if exp_dev cannot construct an equivalent of the round-trip histogram in the substrate (i.e., trace which tasks an item visited and how often it cycled), the cascade-design claim cannot be validated — the diagnostic must be instrumentable.

### B4. Rescue protocols (ranked by literature-support strength)

1. **Adaptive densification at bottleneck** (Katzgraber feedback-optimized, 2006). Strongest support; 2x speedups on Wishart problems with first-order transitions cited.
2. **Policy-gradient adaptive scheduler** (Patel et al 2024, arXiv:2409.01574). Newer; 3.4x-8.8x ACT improvement.
3. **Population annealing** as outright PT alternative (Wang-Machta-Katzgraber 2015; arXiv:1412.2104). Different sampler family; competitive at low T for spin glasses; suffers small-population bias.
4. **Infinite-swap limit** (Plattner-Doll-Dupuis-Wang 2011). Eliminates the discrete-swap rejection bottleneck; mathematically clean but loses replica identity.
5. **Learned global-move augmentation** (IsingFormer, arXiv:2509.23043; Boltzmann generators). Composes with PT; targets the local-update bottleneck specifically.
6. **Multiple-Markov-chain bridging** (Geyer 1991 original; less common in modern PT but a documented rescue).
7. **Simulated-tempering weight reoptimization** (Marinari-Parisi 1992; less common when full-replica memory is available).

**Implication for replay**: a "homogeneous-cascade" replay schedule (e.g., MTR with fixed geometric timescales per Wang et al arXiv:2004.07530) is the analog of Katzgraber's "geometric PT" — the literature predicts it will fail at the continual-learning equivalent of a phase transition (sharp task-distribution shift). The rescue is to densify replay-timescales near the shift.

---

## (c) Discrete cascade-depth optima matching basin / hierarchy depth — load-bearing NEGATIVE finding

### C1. The literature claim

**The PT theory literature does NOT establish a discrete cascade-depth optimum matching the number of RSB levels k, the basin count, or the ultrametric tree depth.**

Evidence base:
- Optimal n_T scaling rules in the literature are CONTINUOUS in N (sqrt(N) or sqrt(barrier)) — see arXiv:0709.3289, arXiv:0908.0012.
- The Parisi-tree / ultrametric structure literature (cond-mat/0207071, arXiv:1508.01232, arXiv:1210.6290) characterizes the LANDSCAPE structure (number of pure states, overlap distribution, tree branching at each RSB step), but does not derive a PT-design rule that matches replica count to tree depth.
- The closest "match" in the literature is qualitative: feedback-optimized PT puts MORE replicas near phase-transition bottlenecks; in a multi-level (k-RSB) landscape there are multiple bottlenecks, so the schedule has MORE concentration points. But this is "densify near each bottleneck", not "exactly k+1 replicas".
- Edwards-Anderson 3D PT uses 22-56 replicas — a continuous range determined by system size, not k+1 for some specific k.
- We did not find any 2020-2025 PT paper proposing a depth-matching rule. Confidence 0.55 (calibration-deflated; absence-of-evidence reasoning carries lit-scan-penalty risk per [[feedback-lit-scan-calibration-penalty]]).

### C2. The closest things to a depth-matching prediction

a) **Folena-Urbani 2024 Kac-Rice 3-point complexity** (cited in substrate_capability_map neighbor E2): the DISTRIBUTION of triplets of stationary points has structure that depends on RSB level. This is a LANDSCAPE invariant, not a PT design rule, but it would be the natural starting point if one wanted to derive a depth-matching theorem.

b) **Population annealing temperature schedule** (Wang-Machta-Katzgraber 2015) DOES suggest non-uniform spacing concentrated at phase transitions — if a substrate's landscape has well-defined transitions at known beta values, the cascade naturally develops k bands matching the transitions. But the prediction is still "densify at each transition", not "k+1 replicas".

c) **Multiple Markov chain methods** (Geyer 1991): the classical motivation was to bridge bimodal posteriors with a small number of bridging chains (often 2-4). For a SINGLE first-order transition (k=1 effective hierarchy level), this maps to 3-4 cascade levels (2 endpoints + 1-2 bridges). This is the closest "small discrete optimum" prediction we found.

### C3. Recommendation specific to 1-RSB landscapes

For 1-RSB substrates (the prior drill's mapping), the literature implies:
- expect ONE primary bottleneck (the RSB transition beta_K)
- recommended cascade depth: enough replicas to traverse it diffusively (sqrt(N) general rule), with DENSIFICATION centered on beta_K
- if a clean two-band split exists, 3-4 replica clusters (sub-cascade above transition + sub-cascade below + 1-2 bridge replicas) may be the minimum viable depth
- but there is NO theoretical reason to expect a sharp peak in performance at exactly 3 or exactly 4 cascade levels; the prediction is "monotone improvement until sqrt(N_effective) saturation, with the SHAPE of densification mattering more than the absolute count"

### C4. Honest framing for Pred-5

The "Pred-5 cascade-depth sensitivity" hypothesis as stated (discrete optimum matching hierarchy depth) is, on literature evidence, **LOW prior probability** as a substrate phenomenon driven by general PT/MCMC theory. P(discrete depth optimum matching k+1) ~ 0.20-0.30 (calibration-deflated; capped below 0.50 per novel-synthesis rule).

What is HIGHER prior probability (~0.55-0.65):
- monotone-saturating improvement up to a system-size-dependent depth, with rapid diminishing returns past that point
- improvement from non-uniform spacing densified at the substrate's analog of phase transitions, regardless of absolute depth
- sensitivity to WHERE the replay timescales concentrate, not HOW MANY there are

This reframing is the load-bearing finding from the drill and should drive Pred-5's experimental contract design.

---

## Capability map deltas (proposed; not committed)

- **Open new neighbor row** "PT-replay-cascade analogy" under Field-C (statistical physics of inference): research-only (🔬), prior P 0.20-0.30 for discrete-optimum framing per C4. Add as candidate for design-space neighbor table.
- **No closures** from this drill.
- **No rehab actions** triggered (no existing closed row resurrected).

If Strategy wants to commit the new row, the strategy_scribe sub-agent handles via the cap_map bump protocol per [[feedback-cap-map-update-protocol]].

---

## Sources (key references, by question)

### Q(a) — Optimal structure

- Katzgraber, Trebst, Huse, Troyer 2006 "Feedback-optimized parallel tempering Monte Carlo" arXiv:cond-mat/0602085
- Nadler, Hansmann 2007 "Dynamics and optimal number of replicas in PT" arXiv:0709.3289
- Machta 2009 "Strengths and weaknesses of parallel tempering" arXiv:0908.0012
- Predescu, Predescu, Ciobanu 2004 (cited in many reviews; the iterative-method foundation)
- Atchade, Roberts, Rosenthal 2011 "Towards optimal scaling of Metropolis-coupled MCMC"
- Kone, Kofke 2005 J Chem Phys (50% acceptance heuristic)
- Hird, Livingstone 2024 arXiv:2408.06894 (re-validation of 0.234 in low-D and PT)
- Patel et al Sep 2024 arXiv:2409.01574 "Policy Gradients for Optimal Parallel Tempering MCMC"
- Plattner, Doll, Dupuis, Wang 2011 (infinite-swap limit; cited via review)

### Q(b) — Homogeneous-schedule failure and rescues

- Bunaiyan et al Sep 2025 arXiv:2509.23043 "IsingFormer: Augmenting PT With Learned Proposals"
- Bittner, Nussbaumer, Janke 2008 arXiv:0809.4020 "First-order phase transitions: PT study"
- Comparing PT and ST at phase transitions arXiv:1011.2358
- Wang, Machta, Katzgraber 2015 arXiv:1508.05647 "Population annealing: Theory and application in spin glasses"
- Wang, Machta, Katzgraber 2014 arXiv:1412.2104 "Comparing MC methods for Ising spin glass ground states"

### Q(c) — Discrete depth vs hierarchy

- Alvarez Banos et al 2012 arXiv:1210.6290 "Correlations between PT dynamics and free-energy landscape in spin glasses"
- Multi-level ultrametric tree in p-spin glasses arXiv:1508.01232
- Ultrametricity between states at different temperatures cond-mat/0207071
- Sellke 2024 / Folena-Urbani 2024 Kac-Rice 3-point complexity (substrate cap_map E1/E2; full refs in cap_map history)

### Replay-side / continual-learning analog refs

- Wang et al Apr 2020 arXiv:2004.07530 "Continual RL with Multi-Timescale Replay" (MTR cascade prototype)
- Fusi, Drew, Abbott 2005 "Cascade Models of Synaptically Stored Memories" (power-law forgetting from multi-timescale plasticity)
