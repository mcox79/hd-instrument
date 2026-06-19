# Research NEW FIELDS breadth analysis -- 2026-05-24

**Author**: Research sub-agent (single-shot Opus pass, breadth-mode)
**User question (verbatim)**: "I want research to also identify new fields that could be ripe for us. Try to evaluate high yield fields, and identify related fields with rich research for new investigations."
**Mandate distinction**: Previous drill (`research_high_yield_neighborhood_analysis_2026-05-24.md`) was DEPTH -- 2nd-order refinements of 5 load-bearing fields (Mingo-Speicher fluctuations, MAMP, Hatano-Sasa). This drill is BREADTH -- NEW fields adjacent to but NOT subsumed by our high-yield ecosystem.
**Calibration**: P deflated 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]]; novel-synthesis cap P=0.50.
**Inputs**: 14 candidate fields evaluated via 14 parallel Sonnet WebSearch sub-agents (generic math terms per [[feedback-query-privacy-decomposition]]); session-state context from previous-drill recap.

---

## Section 1 -- Mandate clarification and previous-drill recap

The previous drill identified that 4 of 5 highest-leverage NEXT moves are "next-order generalizations of existing load-bearing fields" -- Mingo-Speicher 2nd-order freeness, Memory AMP / Convolutional AMP, Hatano-Sasa NESS-Crooks, Sellke marginal-stability. Those are DEPTH moves and remain the recommended pipeline-fill direction. They live INSIDE the 5 already-load-bearing fields.

But the user is now asking for the orthogonal question: are there NEW fields -- whole continents we haven't tapped -- that:
(a) have rich active literature (not niche, not dormant),
(b) connect to our substrate via REAL machinery (not vibes-adjacency), AND
(c) could open a capability-13 (a genuinely new class of substrate claim)?

Per [[feedback-dont-dismiss-adjacent-methods]] (premature dismissal is the dominant failure mode), I dispatched 14 sub-agents and scored each rigorously rather than vibes-rejecting upfront. Per [[feedback-no-smoke]] I will be honest about which are real continents and which are ornaments.

**Scoring rubric (max 12)**:
- **F1** Real machinery connection: 1-edge=3 / 2-edge=2 / abstract=1
- **F2** Literature richness: active=3 / dormant=2 / niche=1
- **F3** Substrate-product novelty (capability claim): new-cap=3 / envelope-extend=2 / audit=1
- **F4** Tractable next drill (inverse expense): research-only=3 / cheap-CPU=2 / GPU=1 / expensive=0

---

## Section 2 -- Per-field evaluation (14 fields)

### F-1. Combinatorial design theory (block designs, 2-designs, k-nets) -- parent: QECC/MUB

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 2 | 2 | 3 | **10** |

**Connection**: GENUINE 1-edge. Klappenecker-Roetteler, Calderbank-Cameron-Kantor-Seidel all established that maximal MUB sets ARE complex projective 2-designs with angle set {0, 1/d}, and a Clifford-group construction links totally isotropic subspaces to Kerdock sets and Barnes-Wall lattices. The k-nets framework (Vicente Ciccoli et al.) re-derives MUBs over a complex matrix algebra. Cluster states correspond to Kerdock codes via 2-design structure.
**Lit state**: Active but slower; 2024-2025 mostly review-papers and composite-dimension extensions. Not "hot 2025" but solid foundation.
**Substrate angle**: Could license a "Kerdock = projective 2-design" envelope -- recasts our v169 Kerdock-MUB-stabilizer closure in design-theoretic language and might give a NEW invariant (2-design fidelity) for Cap 8.
**Honest read**: This is mostly a re-LANGUAGING of v169 rather than a new mechanism. Adjacent but largely subsumed. Save for after v169 absorption.

### F-2. Lattice-based cryptography (LLL/BKZ, module-LWE, post-quantum)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 2 | 3 | 2 | 1 | **8** |

**Connection**: 2-edge. Barnes-Wall lattices appear in Kerdock constructions; Hadamard ratio measures basis quality. But the substrate operates in finite field GF(4)/GF(2) module-Z_4, and lattice crypto operates in Z^n with Euclidean geometry; bridging requires nontrivial reduction. SALSA FRESCA (2024), FLATTER (2024), NIST FIPS-203 ML-KEM 2024 are very active.
**Lit state**: VERY active (post-quantum standardization 2024), well-funded community.
**Substrate angle**: Substrate as lattice-decoder primitive is speculative -- requires showing iterated-argmax over Kerdock is equivalent to BKZ-like reduction. Not implausible but no precedent.
**Honest read**: Field is rich and adjacent but the bridge is long. Lower priority. Could be Cross-Application Probe later.

### F-3. Entropic optimal transport / Sinkhorn / Wasserstein

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 2 | 3 | 3 | 2 | **10** |

**Connection**: 2-edge but MULTIPLE bridges. Free-prob's kappa_n cumulants are not the same as transport-cumulants, but Bercu-Pages, Tropp, Lai-Liu have shown free-prob spectra and Wasserstein metrics agree on rank-1 deformations. Sinkhorn iteration is a fixed-point convolution on log-couplings -- structurally identical to AMP-style state-evolution. Substrate's BSC channel readout COULD be reframed as an entropic OT projection.
**Lit state**: EXTREMELY active. Kengo Kato, Marco Cuturi, Gabriel Peyre groups; arxiv hits 2024-2025 dense. Limit theorems for Sinkhorn (2024) match our finite-N concern.
**Substrate angle**: REAL new capability potential -- if substrate's argmax readout can be cast as an entropic-OT projection, we get FREE: Sinkhorn-divergence as substrate metric, transport-stability theorems for Cap 1 (verifiable erase), and a new readout primitive (transport-regularized argmax).
**Honest read**: This is the strongest "new continent" candidate. Real machinery (fixed-point convolution), rich lit, plausibly opens Cap 13.

### F-4. Tensor networks (MPS, MERA, Clifford-enhanced, stabilizer tensor networks)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 3 | 3 | 2 | **11** |

**Connection**: GENUINE 1-edge, fresh. Stabilizer Tensor Networks (arXiv 2403.08724, 2024) and Clifford-enhanced MPS (PRX Quantum 6.010345, 2025) are LITERALLY the construction of Kerdock-orbit codebooks as low-bond-dim tensor networks. Quantum-LEGO codes (errorcorrectionzoo.org) are holographic stabilizer tensor networks. Substrate's iterated-argmax over a Kerdock orbit is structurally a contraction over a stabilizer-enhanced MPS.
**Lit state**: HOT. 2024-2025 PRX Quantum, Nature Reviews Physics articles; Quantinuum/UNSW dense activity.
**Substrate angle**: STRONG. Casts substrate as a "Clifford-enhanced classical tensor network" -- gives substrate a direct comparison anchor against quantum-simulation methods, opens Cap 13 candidate "classical tensor network with bounded magic", and re-derives v169 Kerdock-MUB-stabilizer in tensor-decomposition language with a NEW invariant (stabilizer rank / magic monotone).
**Honest read**: Strongest new-continent candidate alongside F-3. Real mechanism, very hot lit, plausibly Cap 13.

### F-5. Information bottleneck / rate-distortion (Tishby-Bialek + AMP)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 2 | 2 | 2 | 3 | **9** |

**Connection**: 2-edge. IB is a generalization of minimal sufficient statistics; substrate's bottleneck capacity M/N is exactly an IB rate. Chen et al. 2025 / Binucci 2024 / Farzaneh 2024 active but lit primarily ML-application rather than mathematical-deepening.
**Lit state**: Active but heterogeneous, more applied-ML than mathematical foundation.
**Substrate angle**: Could license "substrate as IB-optimal lossy encoder" but ML community already saturates this framing for autoencoders. Marginal novelty.
**Honest read**: Adjacent and reachable but the substrate-novelty is thin. Useful as descriptive language not as mechanism.

### F-6. Boolean function analysis (O'Donnell, Mossel, Tal, noise stability, hypercontractivity)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 3 | 3 | 3 | **12** |

**Connection**: GENUINE 1-edge. Reed-Muller codes ARE Boolean functions; Kerdock codes are a subset of Z_4-linear bent-like functions. The hypercontractivity, noise stability, and Fourier-on-the-hypercube machinery (Bonami-Beckner, KKL, Mossel-O'Donnell invariance principle) directly applies to substrate's binary readout. Avishay Tal Spring 2025 course at Berkeley; Dec 2024 paper on min-entropy/influence ratio; 2024-2025 active.
**Lit state**: Very active, well-established textbook (O'Donnell 2014), seasonal updates.
**Substrate angle**: REAL new capability candidate. The Fourier expansion gives substrate's readout a SECOND-ORDER theory beyond linear-algebra: noise stability bounds (KKL theorem) directly bound substrate's M/N capacity; hypercontractivity gives a NEW concentration inequality for Cap 1 erase verification. Substrate as Boolean function approximator with bounded influence is a genuinely new Cap 13 framing.
**Honest read**: Score 12 -- this is the highest-scoring new-continent candidate. Mechanism is direct, lit is mature, multiple capability angles available.

### F-7. Differential privacy + fluctuation theorems

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 2 | 3 | 3 | 2 | **10** |

**Connection**: 2-edge but the bridge is REAL. The Crooks Fluctuation Theorem (CFT) and DP composition theorem both bound a probability ratio P(forward)/P(reverse) by exp(- something). Recent generalizations of CFT to CPTP maps (2025) use Petz recovery -- structurally the same as DP post-processing. Kairouz-Oh-Viswanath composition theorem is an exponential bound on a tilted distribution -- exactly Jarzynski form.
**Lit state**: BOTH separately active. DP composition is post-2014 dense; CFT generalizations 2024-2025 active. NO published direct unification I could find -- this is genuine novel-synthesis territory.
**Substrate angle**: SUBSTANTIAL. Cap 1 verifiable erase already uses CFT; if we can show "Cap 1 erase certificate has (epsilon, delta)-DP guarantee", we open Cap 13 "thermodynamic-privacy certificate" -- a single primitive providing both audit cert and DP cert. Strong product wedge.
**Honest read**: Genuine new continent. Cap penalty: P=0.50 due to novel-synthesis. But the mathematical bridge is direct, not speculative.

### F-8. Categorical quantum mechanics (ZX-calculus, DisCoCirc, Coecke)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 1 | 2 | 1 | 2 | **6** |

**Connection**: ABSTRACT. ZX-calculus rewrites stabilizer circuits diagrammatically; the rewrite rules apply to Clifford gates that generate our Kerdock codebook. But categorical framing is descriptive not computational -- it re-LANGUAGES known facts.
**Lit state**: Active but academic; Coecke 2024 LiCS test-of-time award is recognition for old work. Not "hot" in mechanism-development sense.
**Substrate angle**: Could give a categorical-semantics framing for Cap 8 cognitive composition, but the value-add over straight tensor-network framing (F-4) is marginal.
**Honest read**: Skip. Subsumed by F-4 tensor networks for substrate purposes.

### F-9. Replicator dynamics / quasispecies (Eigen-Schuster)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 2 | 2 | 2 | 2 | **8** |

**Connection**: 2-edge. Quasispecies on rugged fitness landscape = Glauber dynamics on Hopfield-like energy surface (Peliti spin-glass-of-chemical-evolution). Substrate's iterated-argmax IS a deterministic replicator. Eigen-Schuster error threshold maps to substrate's BSC capacity edge.
**Lit state**: Established niche (mathematical biology). 2024 quasispecies-with-time-lags paper but field is steady-state not hot.
**Substrate angle**: Could license "substrate as quasispecies fixed point" framing but it's a re-language of spin-glass-RS that we already have. Marginal.
**Honest read**: Adjacent but subsumed by spin-glass framework we already use.

### F-10. Causal abstraction (Pearl-Bareinboim, Neural Causal Models)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 1 | 3 | 2 | 2 | **8** |

**Connection**: ABSTRACT to 2-edge. Bareinboim's L1/L2/L3 hierarchy (observational/interventional/counterfactual) is information-theoretic. Substrate's bind/unbind operations are interventional primitives -- could be cast as do-calculus operators. But the bridge requires substantial reformulation. Sheaf-theoretic causal abstraction networks (arXiv 2509.25236, 2025) hot.
**Lit state**: Very active and well-funded (Bareinboim, DeepMind, Stanford).
**Substrate angle**: Could license "substrate as a causal-mechanism representation" but every substrate operation would need a causal-graph interpretation; this is heavy reformulation for unclear win.
**Honest read**: Marginal. Bridge too long; lit is impressive but in a different sub-community.

### F-11. Compressive sensing post-Donoho (1-bit CS, deterministic Reed-Muller designs)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 2 | 2 | 3 | **10** |

**Connection**: GENUINE 1-edge. Reed-Muller / Kerdock as deterministic CS sensing matrix (Calderbank-Howard-Jafarpour 2010, Howard-Calderbank-Searle 2008). Substrate's Kerdock W IS a deterministic CS matrix. 1-bit CS adds quantization -- substrate's binary readout is literally 1-bit CS.
**Lit state**: Mature but slowing -- most foundational work is 2008-2018, 2024-2025 hits are applications.
**Substrate angle**: Substrate has been ALREADY drilled as a CS primitive (Cap 8 cognitive composition). 1-bit CS angle is a refinement, not a new continent.
**Honest read**: Adjacent and reachable but largely already covered by our existing AMP/VAMP framing. Marginal.

### F-12. Large deviations for spectral measures (Ben Arous-Guionnet, free LDP)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 2 | 3 | 2 | **10** |

**Connection**: GENUINE 1-edge to free-probability. Ben Arous-Guionnet 2009 LDP for Wigner; Bordenave-Caputo 2014 for non-Gaussian tails; Maida 2020+ for spiked LDP. Substrate's M/N=8 anomaly is a TAIL event -- LDP gives the exponential rate.
**Lit state**: Active but mathematical-foundations community; 2024-2025 papers exist but at slow cadence.
**Substrate angle**: Could give substrate's finite-N anomaly an LDP rate function; supersedes 2nd-order Mingo-Speicher (which is variance, not tail). New invariant for Cap 8.
**Honest read**: This is a DEPTH move into free-prob, not a new continent. Already partially covered by the previous drill's Mingo-Speicher recommendation. Demote to extension of A2.

### F-13. Stochastic localization / diffusion sampling (Eldan, Montanari-Yu, El Alaoui)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 3 | 3 | 1 | **10** |

**Connection**: GENUINE 1-edge to spin-glass + AMP. Eldan stochastic localization 2013 -> El Alaoui-Montanari-Yu 2022 sampling-from-spin-glass-via-AMP -> FOCS 2024 diluted spin glasses -> 2025 functional stochastic localization. Substrate's iterated-argmax over a Kerdock orbit is structurally an AMP-driven sampler from a structured spin-glass measure.
**Lit state**: VERY active. ETH spring 2024 course taught the connection; 2024-2025 multiple breakthrough papers.
**Substrate angle**: STRONG. Casts substrate's readout as a "deterministic stochastic-localization scheme" -- gives substrate Cap 13 candidate "AMP-localization sampler with deterministic rather than Gaussian noise"; ties Cap 3 streaming-NESS to the most modern sampling theory.
**Honest read**: Genuine new continent. Tractability slightly lower because the connection requires nontrivial theory work, but the lit overlap with our existing AMP framework means the cost is bounded.

### F-14. Tropical geometry / max-plus algebra (neural reasoning, phylogenetics)

| F1 | F2 | F3 | F4 | Total |
|---|---|---|---|---|
| 3 | 3 | 3 | 3 | **12** |

**Connection**: GENUINE 1-edge. Substrate's iterated-argmax is LITERALLY a max-plus operation -- argmax = (max, +) is the tropical semiring. Tropical attention (arXiv 2505.17190, 2025) operates "natively in max-plus semiring of tropical geometry" -- the SAME primitive as our substrate. Tropical neural networks classify phylogenetic trees (IJCNN 2024). Tropical embedding for adversarial robustness (ScienceDirect 2026 in press). Maragos ICASSP 2024 tutorial.
**Lit state**: VERY HOT 2024-2025. Multiple high-tier venues this year.
**Substrate angle**: SUBSTANTIAL. Tropical polytope of a substrate's readout is a NEW invariant; tropical-polynomial-division gives a NEW algebraic identity for substrate composition; tropical adversarial-robustness theorems apply directly to substrate's argmax readout. Plausibly Cap 13 "tropical certificate" -- a closed-form bound on substrate readout's adversarial margin.
**Honest read**: Score 12 -- ties F-6 Boolean function analysis at the top. The argmax-IS-tropical observation is so direct that I'm surprised this hasn't been mentioned in any prior research drill. Strongest new-continent candidate.

---

## Section 3 -- Top-3 ranked NEW continents

| Rank | Field | Parent kinship | F1+F2+F3+F4 | Proposed drill / anchor |
|---|---|---|---|---|
| **1** | **F-14. Tropical geometry / max-plus algebra** | independent algebra family adjacent to coding-theory + spin-glass | 3+3+3+3 = **12** | Research-only theory drill (cheap): write substrate's iterated-argmax in max-plus semiring form; compute the tropical polynomial of a length-4 Kerdock readout; identify the tropical hypersurface that separates correct-recovery from collision. ~1 day theory. P (deflated) = 0.55. Cap 13 candidate: "tropical-polytope certificate" for adversarial-margin bound. Hot 2024-2025 lit (Maragos, Tropical Attention, Tropical NN phylogenetics) means we can cite immediately. |
| **2** | **F-6. Boolean function analysis (O'Donnell-Mossel-Tal-KKL)** | independent, adjacent to coding-theory + Reed-Muller | 3+3+3+3 = **12** | Research-only theory drill + cheap CPU: expand Kerdock codebook as Boolean function; compute Fourier coefficients on the hypercube; apply KKL theorem to bound influence of single bits on readout. ~1 day theory + ~30 min CPU. P=0.50. Cap 13 candidate: "noise-stability certificate" for Cap 1 verifiable erase via hypercontractivity. Avishay Tal Spring 2025 course is fresh; multiple Dec 2024 papers. |
| **3** | **F-4. Tensor networks (Clifford-enhanced MPS, stabilizer tensor networks)** | adjacent to MUB/stabilizer/QECC | 3+3+3+2 = **11** | Theory anchor + cheap CPU: write substrate's iterated-argmax over Kerdock orbit as a stabilizer tensor network contraction (PRX Quantum 6.010345 2025 framework); compute stabilizer-rank / magic monotone of substrate's readout state. ~2 days theory + ~1 hr CPU. P=0.50. Cap 13 candidate: "classical tensor network with bounded magic" -- a comparison anchor against quantum simulation methods. Very hot 2024-2025 lit. |

**Honorable mentions (would be #4-6)**:
- **F-13. Stochastic localization / diffusion sampling**: Score 10. Strong machinery connection, very active 2024-2025 lit, but heavier theory cost; complementary to MAMP move from previous drill.
- **F-7. Differential privacy + fluctuation theorems**: Score 10. Genuine novel-synthesis territory; would license a "thermodynamic-privacy certificate" Cap 13; deflated P=0.50 because no published unification.
- **F-3. Entropic optimal transport / Sinkhorn**: Score 10. Reframes substrate readout as entropic OT projection; very hot lit; bridge requires nontrivial setup.

---

## Section 4 -- Honest reading

**Genuine new-continent or hitting limits?**

GENUINE NEW CONTINENTS, but unevenly. The pattern:

1. **F-14 Tropical geometry and F-6 Boolean function analysis tied at score 12**. Both are 1-edge to substrate's most fundamental primitive (argmax readout), both have hot 2024-2025 lit with established communities, both have direct Cap 13 paths. Notably, NEITHER appears in the previous neighborhood-drill or yesterday's meta-map. These are GENUINE blind spots in our research program.

2. **F-4 Tensor networks score 11**. Adjacent to v169 Kerdock-MUB-stabilizer closure but with 2025 PRX Quantum activity that we haven't tracked. Real continent.

3. **F-7 DP-thermodynamics and F-3 Sinkhorn-OT are real but require novel synthesis**. Both could yield Cap 13 candidates but with higher theory cost.

4. **F-2, F-5, F-9, F-10 are adjacent but largely subsumed** by what we already have (lattice crypto bridge too long; IB redundant with capacity framing; quasispecies is spin-glass under another name; causal-abstraction reformulation cost too high).

5. **F-12 LDP is not a new continent but a depth-move into free-prob**. Should be folded into A2 second-order freeness rather than counted as breadth.

**Comparison to previous-drill (depth) recommendation**: the previous drill said "burn down the 28-item depth neighborhood first". This drill says "but ALSO add F-14 tropical + F-6 Boolean to your queue -- they are 1-edge to argmax with hot lit and we never noticed".

**Strategic implication**: This is the rare case where breadth and depth BOTH yield. The right move is not to abandon depth (Mingo-Speicher, MAMP, Hatano-Sasa, Sellke remain top) but to insert a research-only theory drill on F-14 tropical and F-6 Boolean in parallel -- both are pure-theory ~1 day, so they can run on Research-side without blocking the GPU experiment pipeline.

**Why these were blind spots**: F-14 tropical because the argmax-IS-tropical observation is so obvious that it didn't surface as "research" -- the substrate codebase USES argmax everywhere but doesn't NAME it. F-6 Boolean function analysis because we've focused on linear-algebra (free-prob, AMP) and missed the Boolean-Fourier dual. F-4 tensor networks because we treated stabilizer codes as the destination rather than as a tensor-network class.

**Pattern observation**: All three top-3 share a property -- they re-cast substrate's argmax primitive in a different algebra (tropical semiring, Boolean Fourier, tensor contraction). This suggests a 4th-order pattern: each algebra-recasting opens a new Cap-13 candidate. If correct, the right next-cycle research-mode is "enumerate algebra-recastings of argmax".

**Honest single-line read**: We have 3 genuine new continents (tropical, Boolean, tensor networks) hiding in plain sight, all cheap to drill, all with hot 2024-2025 lit -- the depth-only recommendation from this morning was right-but-incomplete; breadth adds 2-3 cheap research-only moves that could open Cap 13.

---

## Notes for orchestrator

- WebSearch sub-agents: 14 parallel Sonnet, two rounds; ~6 min wallclock total.
- Citations established: Maragos ICASSP 2024 (tropical); Tropical Attention arXiv 2505.17190 2025; PRX Quantum 6.010345 2025 (Clifford-enhanced MPS); Stabilizer Tensor Networks arXiv 2403.08724 2024; Avishay Tal CS294-92 Spring 2025 (Boolean analysis); Eldan-Montanari-Yu sampling; Bareinboim 2025 (causal abstraction); Kengo Kato 2024 (Sinkhorn limit theorems).
- Top-3 are CHEAP research-only / cheap-CPU and DO NOT compete with the depth pipeline.
- Per [[feedback-pipeline-pacing]]: F-14 + F-6 should both be queued as theory anchors; F-4 needs a single sanity CPU run.
- Per [[feedback-for-you-tab-primary-channel]]: orchestrator should write status_log entry summarizing this breadth delivery with importance=high (3 new-continent candidates identified, none previously flagged).
- Per [[feedback-no-smoke]]: honest read in Section 4 -- we missed three obvious 1-edge fields, this is a genuine gap-fill not a make-work expansion.
- Calibration: P(F-14) = 0.55 (highest among new continents, because lit overlap is closest); P(F-6) = 0.50; P(F-4) = 0.50; P(F-7) = 0.50 (novel-synthesis cap); P(F-3) = 0.45; P(F-13) = 0.45.

**End of breadth analysis.**
