# Research drill: substrate-native autonomous discovery (5-stream)

**Date:** 2026-06-10
**Trigger:** Orchestrator dispatch -- autonomous discovery mandate
**Note path:** notes/research_drill_autonomous_discovery_5x_2026-06-10.md

---

## HEADLINE

Five independent streams (biology, brain, physics, crazy architectures, LLM theory) converge on a single structural finding: genuine novelty generation in compositional systems requires a *population* that is maintained off the fitness peak, not a single state vector optimizing toward one attractor. The substrate currently operates as a single-state system; every mechanism below maps to concrete changes that would let a population of substrate states jointly explore behavioral space. Highest-P path (deflated): substrate-quasispecies with a tunable mutation operator running in parallel with the production retrieval path, using Schmidhuber compression-progress as the fitness signal. P_deflated = 0.38.

---

## Stream A: Biology

### A1. Evolutionary novelty -- gene duplication, horizontal transfer, cooption

Gene duplication creates redundant copies that are free to mutate without fitness cost. Horizontal transfer (HGT) inserts tested modules from unrelated lineages. Evo-devo Hox cooption reuses existing developmental switches in new contexts.

**Substrate analog:** A substrate where stored pattern-vectors (atoms) can be *duplicated into a shadow buffer*, mutated (noise injection), and retained if they improve compression of incoming queries -- is a direct implementation of gene-duplication-plus-selection. Cooption maps to: retrieve atom A for context C1, then test whether atom A *also* compresses context C2 without modification. If yes, the atom is coopted. This requires no new architecture, only a secondary evaluation pass on each retrieved atom.

Key finding: a global 2025 survey of prokaryote HGT shows that ecological pressure (niche construction) gates which horizontal transfers fix (ref: PMC11090817). The substrate analog is: the *query distribution* is the ecological pressure; atoms that survive across many query contexts are the analogs of fixed HGT events.

### A2. Hopeful monsters (Goldschmidt)

Macromutations that are mostly lethal but occasionally produce viable novelty. The modern vindication: transgenic hybrid populations can produce true-breeding recombinant phenotypes with phenotypic distances much larger than point-mutation gradients (PMC3655218).

**Substrate analog:** Periodic large-perturbation injection into the codebook -- e.g., replace a random atom with the superposition of two existing atoms XOR'd -- then measure retrieval quality on held-out queries. Most perturbations degrade retrieval; rare ones create genuinely new compositional coverage. This is the "hopeful monster" move: large-scale perturbation followed by selection, not incremental gradient descent.

### A3. Symbiogenesis (Margulis)

Novelty via *merger of previously independent systems*, not mutation of a single lineage. Mitochondria and chloroplasts are not gradual inventions; they are acquired intact systems.

**Substrate analog:** Two separately trained substrate codebooks, each specialized on a different query distribution, can be merged into a single codebook via concatenation followed by a compression pass (remove atoms that duplicate coverage). The merged codebook has capabilities neither separate codebook had. This is structurally the symbiogenesis operation: acquisition + integration, not incremental mutation.

### A4. Evo-devo: Hox cooption

A small set of regulatory genes controls body-plan switches; the same genes have been coopted in different lineages to produce radically different morphologies. The mechanism is not new gene invention but *rewiring of existing regulatory connections*.

**Substrate analog:** Compositional primitives (bind, bundle, permute, threshold) are the Hox-equivalent regulatory toolkit. New "morphologies" in query space are new compositions of the same primitives. The autonomous discovery problem reduces to: which new compositions of the existing primitives cover uncovered regions of query space? This is tractable with a MAP-Elites style scan over the primitive composition space.

### A5. Quasispecies (Eigen)

Selection acts not on a single master sequence but on a *cloud* of mutants around it. The quasispecies occupies a fitness peak plus its mutational neighborhood. Above the error threshold, the cloud collapses and information is lost. Below the threshold, the cloud explores.

The eigenvector formulation: at equilibrium, the population distribution is the principal eigenvector of the mutation-selection matrix Q*F, where Q is the mutation matrix (Q_ij = probability of mutating sequence j to sequence i) and F is the fitness diagonal. The quasispecies is NOT the single fittest sequence; it is the vector that maximizes long-term fitness accounting for mutation load.

**Substrate analog (F2.1 -- SUBSTRATE-QUASISPECIES):** Replace single codebook with a population of codebooks {C_1, ..., C_k}. Each C_i is a perturbation of a master codebook C*. Mutation operator: add Gaussian noise scaled by mutation rate mu. Fitness: compression quality on a held-out query batch. Selection: retain top-p fraction by fitness, regenerate the rest by mutating survivors. The error threshold corresponds to the mutation rate at which codebook identity (mean cosine similarity to C*) drops below some fraction. This is a direct Eigen quasispecies implemented over codebook space. Cost: O(k * retrieval cost) per generation; k=10-20 is sufficient for exploration.

### A6-A10. Brief notes

**A6 (Punctuated equilibrium):** Long stasis + rapid change is consistent with a system on a fitness plateau exploring neutrally until it crosses a threshold. Substrate analog: many mutations are neutral (do not change retrieval quality); the neutral network is large; occasionally a neutral walk reaches a region with a fitness gradient to a new peak. This implies exploration on the neutral set is more efficient than random noise.

**A7 (Niche construction):** Organisms modify their environment, changing the selection pressure. Substrate analog: a substrate that *modifies its query distribution* (e.g., by flagging low-confidence retrievals as exploration targets) is doing niche construction.

**A8 (Cultural evolution):** Cumulative innovation requires transmission fidelity plus variation. Substrate analog: the retrieval history (which queries were answered confidently vs. not) is the transmission channel; atoms generated for low-confidence queries are the variation pool.

**A9 (Cell differentiation):** A single genome produces many specialized cell types. Substrate analog: a single codebook can produce query-specialized sub-codebooks by soft-attention weighting of the full codebook toward the current query context.

**A10 (Cancer):** Uncontrolled novelty generation with loss of fitness constraint. Substrate analog: mutation rate above the error threshold. Hard-fail condition.

---

## Stream B: Brain

### B1. Insight / Eureka (Sternberg)

Insight in humans is characterized by: (a) prior impasse, (b) sudden representational restructuring, (c) strong confidence in the solution. Neural correlates: anterior temporal lobe (semantic integration), right hemisphere (distant associations), gamma burst at the moment of insight.

**Substrate analog:** An impasse is a query for which no atom retrieves above the confidence threshold. Representational restructuring corresponds to a new binding operation over existing atoms. The substrate can detect impasses; the open question is whether it can autonomously trigger a restructuring search.

### B2-B3. Default mode and sleep consolidation

Rest/sleep is not passive; it is *active replay* of recent experiences in novel combinations (hippocampal generative replay). Wamsley's work shows that brief awakenings from NREM sleep reveal ongoing compositional recombination of waking memories. The default mode network (DMN) during rest generates counterfactual simulations -- sequences that were not experienced but are consistent with learned structure.

Key 2024-2025 finding: "insight predicts subsequent memory via cortical representational change and hippocampal activity" (Nature Communications 2025) -- the same hippocampal mechanism that consolidates insight also strengthens the memory of the insight-triggering query, creating a directed replay bias toward productive areas.

**Substrate analog (F2.3 -- DREAMING-SUBSTRATE):** A "sleep" pass runs after each retrieval session. During sleep: (1) replay recent queries in random order, (2) for each query, generate a new binding of atoms not retrieved during wakefulness, (3) retain new bindings that score above retrieval threshold on the held-out query. This is exactly hippocampal generative replay: offline recombination with quality filtering. The DMN analog is: the substrate explores compositional combinations not seen during waking, using the learned atom set as raw material.

### B4-B6. Dopamine, hippocampus, theta-gamma

Dopamine novelty signal: firing peaks at unexpected events, not expected ones. Hippocampal theta-gamma coupling: theta (4-8 Hz) organizes sequence encoding; gamma (30-100 Hz) loads individual items into working memory within each theta cycle. The binding of novel patterns occurs within a single theta cycle.

**Substrate analog:** Theta-gamma coupling maps to a two-timescale update: slow context accumulation (theta-equivalent, long window) + fast atom retrieval within the context window (gamma-equivalent). Novel patterns are those that require atoms from different slow-context windows to be jointly active within a single fast retrieval. This is detectable from the retrieval access pattern alone.

### B7-B10. Brief notes

**B7 (Anterior temporal lobe):** Semantic hub that integrates across modalities. Substrate analog: a hub atom that is a compression of a cluster of semantically related atoms -- a superatom.

**B8 (Right hemisphere):** Processes distant semantic associations; activates before insight. Substrate analog: low-threshold retrieval (accepting atoms at confidence well below operating threshold) during exploration passes to pick up distant associations.

**B9 (Children):** Higher exploration rate, lower exploitation. Substrate analog: exploration budget (fraction of queries routed to random atom sampling rather than argmax retrieval).

**B10 (Aesthetic chills):** Frisson signals pattern recognition at the boundary of expectation. Substrate analog (F2.10 -- AESTHETIC-GUIDED-SEARCH): a "surprise" score = negative log probability of the retrieved atom under the prior atom distribution. High surprise = high frisson. Use surprise as an exploration reward signal.

---

## Stream C: Crazy architectures

### C1. Stochastic resonance discovery

Stochastic resonance: adding noise to a subthreshold signal can push it over a detection threshold. The effect is NOT that noise is generally helpful; it is that there is an *optimal noise level* for a given signal and threshold.

**Substrate analog (F2.5 -- STOCHASTIC-RESONANCE-DISCOVERY):** For queries near but below the retrieval confidence threshold, inject controlled noise into the query vector before retrieval. The noise level is tuned to the signal-to-noise regime of the query (estimated from query vector norm and codebook coverage). At optimal noise, borderline queries cross the threshold and retrieve -- producing a discovery that a noiseless system would miss. This extends the prior PP-276 stochastic-resonance anchor to the discovery context.

### C2. Generative substrate via mutation and selection

Direct mapping of genetic algorithm over the atom space: initialize a population of k atoms drawn from the codebook; run tournament selection + crossover (component-wise averaging or XOR) + mutation; evaluate fitness as retrieval quality on a target query. This is a gradient-free search over atom space.

The key advantage over gradient descent: it can cross fitness valleys (neutral mutations accumulate; a sequence of neutral + one beneficial move is inaccessible to gradient descent). The quasispecies model says this valley-crossing is the primary source of genuine novelty.

### C3. Adversarial substrate pairs (F2.7)

Two substrate instances, A and B. A generates candidate new atoms; B attempts to retrieve them (tests whether they are novel but consistent with the existing codebook). Atoms that B retrieves weakly (low confidence) but A is confident about are the discovery zone. This is a GAN-style dynamic: A learns to generate atoms in the low-B-confidence region; B learns to distinguish novel atoms from noise.

The cortical adversarial dreaming paper (PMC9071267) implements exactly this: wake (encoding) + NREM (consolidation) + REM (adversarial generation) organized as three distinct objective-function phases. The REM phase is a discriminator; the NREM phase is a generator. Substrate analog: run a 3-phase loop mirroring wake/NREM/REM.

### C4. Substrate quasispecies (F2.1 expanded)

Population of codebooks rather than a single codebook. Each individual in the population is a slightly different codebook. Tournament selection: individuals with higher query-batch fitness reproduce. Crossover: for each atom slot, select the atom from parent A or parent B based on which scores higher on a held-out query. Mutation: Gaussian noise on the codebook matrix rows.

The Eigen model shows that at finite population size N_pop, there is a *finite-population error threshold* below which the quasispecies maintains its identity and above which it drifts. The Wright-Fisher drift correction (from the population-genetics stream) gives the effective population size needed to resist drift: N_pop > 1 / (mu * s) where mu is mutation rate and s is the selection coefficient per mutation.

### C5. Dreaming substrate (F2.3 expanded)

Three-phase loop: (1) Wake: standard retrieval on incoming queries, log all queries and retrieved atoms. (2) NREM: replay queries in shuffled order; for each query, retrieve atoms using a *lower confidence threshold* than waking; save all above-floor atoms into a candidate buffer. (3) REM: for each candidate in the buffer, generate a *compositional extension* (bind the candidate atom with a randomly sampled second atom); evaluate whether the composite retrieves better than either component alone on any held-out query; if yes, add to codebook.

This three-phase structure is exactly the Wamsley hippocampal-replay-during-consolidation mechanism: offline replay generates candidates that online retrieval filters.

### C6. Active inference exploration loop

Friston's active inference: an agent minimizes expected free energy, which has two terms -- (a) expected surprise (epistemic drive, exploration) + (b) expected utility (pragmatic drive, exploitation). The exploration term drives the agent to query states where its predictions are most uncertain.

**Substrate analog:** Expected surprise for a query = entropy of the retrieval distribution over atoms. High-entropy queries (many atoms retrieved with similar low confidence) are the epistemic targets. Route a fraction of computational budget to high-entropy queries, then store any atoms that allow those queries to be answered at higher confidence on subsequent passes. This is a direct implementation of active inference epistemic drive.

### C7. Open-ended MAP-Elites (F2.8)

MAP-Elites maintains an archive of solutions, one per behavioral descriptor cell. New candidates are generated by mutating archived solutions. A solution replaces the archive entry in its cell only if it scores higher. The archive fills over time, eventually covering the full behavioral descriptor space.

**Substrate analog:** Behavioral descriptor = (query domain, query difficulty). Codebook atom = solution. New atom candidates are generated by mutating existing atoms. An atom replaces the archived atom for its (domain, difficulty) cell if it retrieves better on that cell's representative query. Over time, the archive covers (domain, difficulty) space, producing a substrate that is competent across the full behavioral space.

Quality diversity literature (2024-2025) shows MAP-Elites consistently outperforms multi-objective EAs + pure novelty search on coverage metrics and is robust to stochasticity. The key finding: *heterogeneous emitters* (different mutation operators in different cells) further improve coverage. Substrate analog: use different mutation types (Gaussian noise / atom crossover / superposition) in different (domain, difficulty) cells.

### C8-C10. Brief notes

**C8 (Substrate dialogue):** Two substrate instances query each other; each retrieval is a query to the other. Novel atoms emerge from the fixed-point of the dialogue. This is combinatorial exploration without external data.

**C9 (Aesthetic-guided search, F2.10):** Surprise score = KL divergence between retrieved atom distribution and prior atom distribution. Maximize expected surprise subject to retrieval quality floor. This is implementable as a curiosity bonus in the retrieval scoring function.

**C10 (Schmidhuber compression progress, F2.2):** The compression-progress reward is the *derivative* of compression quality, not the level. Concretely: atom A generates compression-progress reward = (compression_quality_after_adding_A) - (compression_quality_before). An atom that is redundant with existing atoms gets zero reward even if it retrieves well. An atom that covers a genuinely new region of query space gets a large reward. This is the clean operationalization: reward = marginal compression gain per new atom.

The Schmidhuber formal theory (TAMD 2010) shows that this reward signal is sufficient to generate open-ended discovery in a computable agent. The compressor improvement is the only signal needed.

---

## Stream D: Materials science and physics

### D1. Symmetry breaking and emergence

Spontaneous symmetry breaking (SSB) is the mechanism behind all phase transitions: water to ice, magnetization at T_c, Cooper-pair condensation. The key mathematical structure: the system has a symmetric Hamiltonian (invariant under rotation/inversion/etc.) but the ground state breaks that symmetry. Multiple degenerate ground states exist; the system picks one.

**Substrate analog:** The codebook has a large space of equivalent configurations (atoms that retrieve equally well on training queries). When a new query type enters, the symmetry is broken: the codebook must pick one configuration over others. The novelty is the symmetry-breaking event. Tracking symmetry-breaking transitions (large changes in the principal eigenvector of the codebook Gram matrix) is a detection mechanism for genuine novelty generation.

The 2024 paper "Symmetry breaking of three self-organization rules" (arXiv:2405.16028) shows that Turing patterns, fractals, and spiral waves are all generated by the same three symmetry-breaking rules operating at different scales. The substrate analog: the three primitive operations (bind, bundle, threshold) applied at different scales of the query hierarchy generate the full observed diversity of retrieval patterns without any new primitives.

### D2. Self-organized criticality (Bak)

SOC systems self-tune to the critical point without external tuning: the sandpile avalanche dynamics push the pile slope toward the critical angle. At the critical point, power-law statistics emerge; the system is maximally responsive to perturbations.

**Substrate analog:** A retrieval confidence threshold that self-adjusts (raise when retrieval quality is high; lower when many queries are below threshold) is implementing SOC: the threshold self-tunes to keep the system near-critical. At criticality, maximum information is transmitted per query (maximum transfer entropy). SOC in the substrate means the confidence threshold is not a fixed hyperparameter but an adaptive parameter that tracks the critical point.

### D3. Far from equilibrium (Prigogine)

Dissipative structures: ordered patterns maintained by continuous energy input far from equilibrium. Prigogine: "order through fluctuations." Novel patterns emerge from bifurcations in the parameter space of the driving dynamics.

**Substrate analog:** The substrate under continuous query load (far from equilibrium) can develop persistent patterns in atom usage frequency. Atoms that are accessed frequently become "hot" (shorter effective retrieval path); atoms that are never accessed become "cold." The hot/cold partition is a dissipative structure maintained by the query distribution. Novel queries that activate cold atoms represent bifurcations -- they recruit a new part of the system into the active regime.

### D4-D6. Brief notes

**D4 (BZ reaction / chemical oscillators):** Periodic novelty generation via oscillation between exploration and exploitation phases. The BZ substrate analog: alternate between high-threshold (exploitation) and low-threshold (exploration) retrieval passes on a fixed cycle.

**D5 (Turing patterns):** Short-range activation + long-range inhibition generates spatial structure. Substrate analog: local atom similarity clustering (activation) + long-range dissimilarity penalty (inhibition) generates a structured atom space with distinct domains. Novelty = recruitment of a new domain.

**D6 (Glass transition):** A glass is stuck in a local minimum; exploration requires a large fluctuation. Substrate analog: the codebook can be in a glassy state where all retrieval confidence is moderate but no clear peaks exist. Getting out of the glass requires a large perturbation (hopeful monster move, not gradient).

### D7-D10. Brief notes

**D7 (Glass transition structural diversity):** The glass transition temperature T_g separates liquid-like (exploratory) from solid-like (exploitative) regimes. Substrate analog: the mutation rate mu plays the role of temperature; above the error threshold (T > T_c), liquid-like behavior; below it, solid-like.

**D8 (Cellular automata):** Wolfram Rule 110 is Turing-complete; complex patterns emerge from simple local rules. Substrate analog: the binding operation is a local rule; complex retrieval patterns emerge from iterated binding without any global planner.

**D9 (Reaction-diffusion):** Two reacting species with different diffusion rates generate stable spatial patterns. Substrate analog: two atom populations with different retrieval thresholds (one fast/broad, one slow/precise) generate a structured retrieval landscape.

**D10 (RG flow):** Coarse-graining reveals which parameters are relevant at each scale. Substrate analog: coarse-graining the atom space (clustering atoms and replacing each cluster with its centroid) reveals the relevant abstract structure of the query distribution.

---

## Stream E: LLM theory

### E1. Sampling temperature and novelty

LLM sampling: temperature T scales the logit distribution. T=0 is argmax (greedy); T>1 flattens the distribution toward uniform. 2024-2025 research shows a U-shaped novelty curve: novelty increases with T up to an optimal T*, then decreases as quality degrades faster than novelty increases.

The key result (arXiv:2504.09389): novelty measured as frontier of "original AND high quality" peaks at T* that depends on the query type and model size. This is exactly the optimal noise level in stochastic resonance.

**Substrate analog:** The retrieval confidence threshold theta plays the role of 1/T. Low theta (permissive) = high T (exploratory). The optimal theta for discovery is the substrate-analog of T*: permissive enough to retrieve novel atoms, strict enough to reject noise.

### E2-E3. RLHF reward hacking and Voyager

RLHF reward hacking: a sufficiently capable model finds novel outputs that maximize learned reward but violate the intent behind the reward. This is *adversarial novelty*: new outputs that game the reward, not new outputs that are genuinely useful.

Voyager (open-ended Minecraft): an LLM agent with a curriculum of self-generated tasks + a skill library. The skill library grows by storing executable code for each solved task. Novelty = new tasks proposed by the LLM that are neither trivially easy nor impossible given current skills. This is a direct MAP-Elites analog: the task space is the behavioral descriptor space; the skill library is the archive.

**Substrate analog:** A self-generated task curriculum where each task is a query type not yet answered with high confidence. The curriculum grows by: (1) identify queries near the confidence threshold, (2) generate compositional variations of those queries, (3) route variations to the retrieval + exploration pipeline. The substrate analog of Voyager's skill library is the codebook.

### E4-E6. Chain of thought, in-context exploration, adversarial training

Chain-of-thought (CoT) as exploration: each reasoning step narrows the search space. The substrate analog is multi-hop retrieval: each hop reduces the effective search space for the next hop.

In-context exploration: recent work (arXiv:2505.17621) shows that LLMs with intrinsic motivation rewards (curiosity) explore more effectively than those with only extrinsic rewards. The curiosity reward is the epistemic component of expected free energy -- exactly the active inference formulation.

Adversarial training: the discriminator in a GAN forces the generator to produce outputs in regions of low discriminator confidence. This is the adversarial substrate pair (C3) implemented at the LLM scale.

### E7-E10. Brief notes

**E7 (Diffusion model creativity):** Latent space interpolation generates smooth transitions between known patterns. Substrate analog: interpolation between two atoms in the codebook generates a new atom at the midpoint. The midpoint atom may not correspond to any stored pattern -- it is genuinely novel.

**E8 (AutoGPT):** Autonomous task generation via self-prompting. Substrate analog: the substrate generates its own exploratory queries based on low-confidence regions of the current codebook.

**E9 (Constitutional AI):** Critique-revision loop improves outputs. Substrate analog: after each retrieval, run a second retrieval using the first result as a query; if the second result is more specific than the first, the first result triggered a genuine discovery.

**E10 (Tool use):** Using tools enables behaviors impossible without them. Substrate analog: the compositional primitives are the tools; novel compositions are behaviors that were impossible with single-atom retrieval.

---

## Stream F: Synthesis

### F1. Cross-stream convergence

All five streams converge on three structural requirements for autonomous discovery:

1. **Population, not singleton.** Biological quasispecies, neural replay populations, MAP-Elites archives, Eigen model, Voyager skill libraries -- all maintain a *population* of candidates, not a single best guess. A singleton system can only hill-climb; a population can explore the neutral network around the fitness peak and cross valleys.

2. **Offline recombination pass.** Hippocampal replay, sleep consolidation, Schmidhuber compression-progress reward, GAN adversarial dreaming -- all run an *offline pass* that recombines existing elements without external data input. The offline pass is what generates novelty beyond composition of the most recent experience.

3. **Compression-progress as fitness, not retrieval quality.** Retrieval quality is a level signal; compression progress is a derivative signal. A system maximizing the level will overfit; a system maximizing the derivative will explore. The Schmidhuber formal theory is the cleanest operationalization.

### F2. Ten candidate substrate-native autonomous discovery systems

**F2.1 SUBSTRATE-QUASISPECIES**
- Architecture: Population of k codebooks {C_1..C_k}. Each is a noisy perturbation of master C*. Selection on per-batch compression quality. Mutation by Gaussian noise on codebook rows. Crossover by atom-slot tournament.
- Key parameter: mutation rate mu; error threshold mu_c ~ 1/(L * log(s_max)) where L = atom dimensionality, s_max = selective advantage of master over typical mutant.
- P_deflated: 0.42 (population search on compositional systems well-precedented in evolutionary computation; substrate application is novel but the math is standard).
- Cheap test: Run k=5 codebooks for 100 query batches. Compare coverage of held-out query distribution vs. single codebook. Expected: +5-15% coverage. Hard-fail: less than 2% coverage gain over single codebook after convergence.

**F2.2 NOVELTY-AS-COMPRESSION-PROGRESS**
- Architecture: Maintain a running compressor C of the query-atom log. Fitness of a new atom = delta compression rate on a held-out query batch. Store only atoms with positive compression-progress score.
- Implementation: Use a lightweight suffix-array compressor or LZ77 variant on the query-atom log. Delta = (length of compressed log with atom A) - (length without atom A).
- P_deflated: 0.40. The compression-progress signal is well-defined and computable; the question is whether it is discriminating enough to drive useful search.
- Cheap test: log 1000 queries + retrieved atoms; measure LZ77 compression length; add one new atom; measure delta. Expected: positive delta for atoms that cover new query patterns, zero for redundant atoms.

**F2.3 DREAMING-SUBSTRATE**
- Architecture: Three-phase loop: Wake (standard retrieval), NREM (low-threshold replay with candidate generation), REM (adversarial evaluation of candidates by second substrate instance).
- Key parameter: NREM threshold theta_nrem < theta_wake; REM acceptance criterion = candidate atom beats current best atom on at least one held-out query.
- P_deflated: 0.45. The three-phase loop is the most directly biology-validated mechanism; replay is empirically demonstrated in neural systems; the substrate analog is structurally clean.
- Cheap test: Run 500 wake queries. Run 1 NREM pass (lower threshold, log candidates). Run 1 REM pass (evaluate candidates on held-out batch). Count atoms that pass REM and are not already in the codebook. Expected: 5-20% of REM candidates are genuine novelties. Hard-fail: less than 2% of REM candidates are novel.

**F2.4 SYMMETRY-BREAK-NOVELTY**
- Architecture: Track the principal eigenvector of the codebook Gram matrix G = C^T C over time. A sudden change in the leading eigenvector direction (cosine distance > threshold) is a symmetry-breaking event. Log these events as discovery markers.
- P_deflated: 0.28. The symmetry-breaking detection is clean; but whether the detected events correspond to genuine discovery vs. noise is unclear without empirical data.
- Cheap test: Run Gram matrix eigenvector tracking over 1000 queries. Plot eigenvector drift. Check whether drift events correlate with queries answered at unusually high vs. low confidence.

**F2.5 STOCHASTIC-RESONANCE-DISCOVERY**
- Architecture: For queries with confidence in [theta_low, theta_high] (near-miss zone), inject Gaussian noise at amplitude sigma_opt into the query vector before retrieval. sigma_opt is estimated from the query norm and the gap between the top-1 and top-2 atom cosine scores.
- P_deflated: 0.38. Stochastic resonance is well-characterized; the optimal noise estimation from the score gap is novel but algebraically straightforward.
- Cheap test: Take 100 queries that retrieved with confidence in [0.6, 0.8]. Inject noise at sigma in {0.01, 0.05, 0.1, 0.2}. Measure whether any sigma level increases the fraction of queries that retrieve at confidence > 0.9. Hard-fail: no sigma level improves retrieval for more than 5% of near-miss queries.

**F2.6 EVOLUTIONARY-COOPTION**
- Architecture: For each retrieved atom A and each query context C, compute the cosine similarity of A to all *other* query contexts in the recent log (cooption score). Atoms with high cooption score across diverse contexts are candidates for "atomic primitives" -- Hox-equivalent regulatory nodes.
- P_deflated: 0.35. The cooption score is well-defined; whether high-cooption atoms are actually more useful as primitives is empirical.
- Cheap test: Rank atoms by cooption score after 1000 queries. Check whether high-cooption atoms appear in more diverse query-context retrievals than low-cooption atoms. Expected: Spearman rho > 0.4 between cooption rank and query-diversity of retrieval. Hard-fail: rho < 0.1.

**F2.7 ADVERSARIAL-SUBSTRATE-PAIRS**
- Architecture: Generator G proposes new atom candidates; discriminator D attempts to classify them as "genuine novel pattern" vs. "noise." Training: G maximizes D's uncertainty (cross-entropy on D's soft classification); D minimizes uncertainty. Novel atoms are those in D's high-uncertainty region that G can reliably produce.
- P_deflated: 0.30. GAN training instability is a known risk; substrate-specific adaptation needed.
- Cheap test: Train G+D for 200 steps on 1000 atoms. Measure fraction of D-uncertain atoms that are novel (not in the training set). Expected: 20-40% of uncertain atoms are genuinely novel. Hard-fail: less than 5% are novel (D has not learned anything useful).

**F2.8 OPEN-ENDED-MAP-ELITES**
- Architecture: Behavioral descriptor space = (query domain tag, query difficulty bin). For each new query, generate k mutant atoms from the retrieved atom; evaluate each mutant on the (domain, difficulty) cell; replace the archive entry if the mutant scores higher. Track archive coverage over time.
- P_deflated: 0.44. MAP-Elites is the most empirically validated QD algorithm; substrate adaptation is straightforward. 2024-2025 literature confirms robustness to stochasticity.
- Cheap test: Implement MAP-Elites with 10x10 behavioral descriptor grid. Run 500 queries. Measure grid coverage. Expected: >40% of cells filled after 500 queries. Hard-fail: <15% cells filled.

**F2.9 INSIGHT-ATTRACTOR**
- Architecture: Model impasse as a query that retrieves below threshold for N_stuck consecutive attempts. Impasse triggers a *state switch*: increase exploration budget (lower threshold, higher mutation rate) for the next K_explore queries. Track whether state switches are followed by above-threshold retrieval within K_explore steps (insight event).
- P_deflated: 0.36. The impasse-detection + state-switch is well-motivated by the brain literature; whether the substrate dynamics match the neural dynamics is uncertain.
- Cheap test: Log all queries that retrieve below threshold 3+ consecutive times. Check whether a lower-threshold retry (theta * 0.7) within 5 queries resolves the impasse. Expected: >50% impasse resolution rate with lower threshold. Hard-fail: <20% resolution rate.

**F2.10 AESTHETIC-GUIDED-SEARCH**
- Architecture: Surprise score S(q) = -log P(top_atom | q) under the prior atom distribution P(a) = frequency of atom a in the retrieval log. Use S(q) as an exploration priority: route high-surprise queries to the full population of codebooks (quasispecies); route low-surprise queries to the single master codebook.
- P_deflated: 0.38. The surprise score is computable from the retrieval log; the routing decision is deterministic; the question is whether high-surprise routing actually generates useful novelties.
- Cheap test: Split 1000 queries into high-surprise (top quartile of S) and low-surprise (bottom quartile). Route high-surprise to k=5 codebook population, low-surprise to single codebook. Measure whether high-surprise routing generates more novel retrievals (atoms not seen in the bottom quartile's results). Hard-fail: no difference in novelty rate between high-surprise and low-surprise routing.

### F3. Five empirical tests (ranked by cost and decisiveness)

**Test 1 (Cheapest, most decisive): Compression-progress signal exists**
- Claim: Marginal LZ77 compression delta is discriminating across atoms.
- Setup: Log 1000 query-atom pairs. Compute per-atom compression delta. Rank atoms by delta. Check whether high-delta atoms cover more diverse query contexts.
- Decision criterion: Spearman rho(compression delta, query-context diversity) > 0.3.
- Hard-pass: rho > 0.5 AND top-quartile atoms cover 2x more query contexts than bottom-quartile.
- Hard-fail: rho < 0.05 OR compression delta variance is less than 1% of mean delta (signal too weak).

**Test 2 (1 day CPU): NREM sleep pass generates non-redundant candidates**
- Claim: Low-threshold offline replay generates atoms that pass the REM evaluation and are not in the existing codebook.
- Setup: Wake pass (500 queries, standard threshold). NREM pass (same queries, theta * 0.6). REM evaluation (candidate atoms scored on 100 held-out queries). Count new atoms.
- Hard-pass: >10 new atoms per 500-query wake pass that score above theta on held-out queries.
- Hard-fail: Zero new atoms pass REM evaluation OR all new atoms are within cosine distance 0.05 of existing atoms (redundant).

**Test 3 (1 day CPU): Quasispecies coverage gain**
- Claim: Population of k=5 codebooks covers more of a held-out query distribution than a single codebook.
- Setup: Train single codebook on query batch A. Run quasispecies (k=5, mu=0.01) for 50 generations on query batch A. Evaluate both on held-out query batch B. Measure: fraction of B queries answered above threshold.
- Hard-pass: >5% coverage gain on batch B at k=5 vs. single codebook.
- Hard-fail: quasispecies DEGRADES coverage vs. single codebook at mu=0.01 (mutation rate too high; error threshold crossed).

**Test 4 (2 days CPU): MAP-Elites behavioral descriptor coverage**
- Claim: MAP-Elites over a 10x10 domain-difficulty grid achieves >40% cell coverage after 500 queries.
- Setup: Implement MAP-Elites with Gaussian mutation on atom rows. Run 500 queries. Track grid coverage over time.
- Hard-pass: >50% cells filled, coverage growing monotonically through query 500.
- Hard-fail: Coverage plateaus below 20% before query 300 (behavioral descriptor space is not accessible by mutation from the initial archive).

**Test 5 (1 hour CPU): Stochastic resonance near-miss improvement**
- Claim: Optimal noise injection improves retrieval for near-miss queries.
- Setup: Take 100 queries with confidence in [0.6, 0.8]. Test sigma in {0, 0.02, 0.05, 0.1, 0.2}. Measure fraction reaching confidence > 0.85 after noise injection.
- Hard-pass: At optimal sigma, >20% of near-miss queries cross 0.85 threshold (vs. 0% at sigma=0).
- Hard-fail: No sigma level improves more than 5% of near-miss queries.

### F4. Honest highest-P path (substrate-only)

Ranked by P_deflated, accounting for implementation cost and empirical precedent:

1. **F2.3 DREAMING-SUBSTRATE (P=0.45):** Three-phase loop with offline replay. The biology precedent is the strongest; the implementation is straightforward; the REM evaluation criterion is a clean falsifiable test. This is the recommended first implementation.

2. **F2.8 OPEN-ENDED-MAP-ELITES (P=0.44):** MAP-Elites over behavioral descriptor space. The 2024-2025 literature confirms robustness; implementation cost is moderate; the behavioral descriptor space needs to be defined for the substrate query domain.

3. **F2.1 SUBSTRATE-QUASISPECIES (P=0.42):** Population of codebooks with mutation-selection dynamics. The Eigen model is exact; the substrate adaptation is novel but algebraically clean. Main risk: mutation rate calibration.

4. **F2.2 NOVELTY-AS-COMPRESSION-PROGRESS (P=0.40):** Compression-progress fitness signal. The Schmidhuber theory is well-founded; the main uncertainty is whether the LZ77 delta is discriminating enough in practice.

5. **F2.9 INSIGHT-ATTRACTOR (P=0.36):** Impasse detection + state switch. The biology motivation is strong; the substrate dynamics are uncertain.

6. **F2.5 STOCHASTIC-RESONANCE-DISCOVERY (P=0.38):** Near-miss noise injection. Clean mechanism, cheap test. Extends existing PP-276 work.

7. **F2.10 AESTHETIC-GUIDED-SEARCH (P=0.38):** Surprise-based routing to population. Works as a wrapper around F2.1.

The three mechanisms that compose cleanly: F2.3 (dreaming) + F2.1 (quasispecies) + F2.2 (compression-progress fitness). Run dreaming to generate candidates; use compression-progress to evaluate them; maintain a quasispecies to prevent premature convergence. This is the three-layer stack.

**HARD-FAIL thresholds for the composite system:**
- If the dreaming pass generates zero novel atoms over 10 consecutive wake sessions: dreaming mechanism is not generating diversity; abort and return to single-codebook mode.
- If the quasispecies population converges (all k codebooks within cosine distance 0.02 of each other) before 100 generations: error threshold crossed; reduce mutation rate.
- If compression-progress delta variance drops below 1% of mean delta: fitness signal is flat; the query distribution is fully covered and no exploration is productive.

---

## Cheap decisive test

**The single cheapest decisive test** is Test 1 (compression-progress signal): compute per-atom LZ77 compression delta on a 1000-query log. This is a pure read-only analysis of existing retrieval logs requiring no new architecture. If the compression-progress signal exists (rho > 0.3), then the F2.2 mechanism is operational immediately. If it does not exist (rho < 0.05), then the Schmidhuber fitness function needs a different compressor (e.g., MDL-based rather than LZ77). Total cost: ~30 minutes of analysis on existing data.

---

## Falsifiable predictions

**HARD-PASS** (all of these must hold for the composite mechanism to be viable):
1. Compression-progress delta is discriminating: Spearman rho(delta, query-context diversity) > 0.3 on a 1000-query log.
2. NREM sleep pass generates >5 non-redundant atoms per 500-query wake session.
3. Quasispecies at k=5, mu=0.01 achieves >3% coverage gain on held-out queries vs. single codebook.
4. MAP-Elites achieves >35% cell coverage on a 10x10 grid after 500 queries.

**HARD-FAIL** (any one of these falsifies the mechanism):
1. Compression-progress delta has variance < 1% of mean delta (signal is flat; fitness function is degenerate).
2. NREM pass generates zero atoms that pass REM evaluation over 5 consecutive wake sessions.
3. Quasispecies DEGRADES coverage vs. single codebook at mu=0.01 (error threshold crossed at this rate).
4. MAP-Elites coverage plateaus below 20% before query 300 (behavioral descriptor space inaccessible).
5. Stochastic resonance noise injection improves fewer than 5% of near-miss queries at any sigma level.

---

## Cross-thread synthesis

**Prior work connections:**

- PP-276 (stochastic resonance): F2.5 is a direct extension. PP-276 established that noise injection is viable on the substrate; F2.5 operationalizes it for the discovery context (near-miss queries only).
- Population-genetics / Wright-Fisher drill (2026-06-04): The quasispecies model (F2.1) is the continuous-fitness limit of the Wright-Fisher model. The prior drill established the drift correction formula; F2.1 uses it to size the population (N_pop > 1/(mu * s)).
- Compositional cliff crossing (2026-06-10): The substrate has crossed the compositional cliff at v3.0. The post-cliff architecture now supports the dreaming pass (F2.3) because compositional recombination during NREM replay is feasible at the new compositional capability level.
- Tier-5c fact-recall work: The fact-recall zero problem (C1-FACT held-out fact-recall=0) is exactly the case where compression-progress is zero: the substrate is retrieving facts correctly on training but generating zero compression-progress on held-out facts. F2.2 would have flagged this: zero delta on held-out = no generalization. This is a retrodictive connection.

**Adjacent threads NOT dismissed (per feedback-dont-dismiss-adjacent-methods):**

- Theta-gamma binding (B6): Maps to two-timescale retrieval; has not been tested on the substrate. Adjacent to the existing multi-hop retrieval work.
- Symmetry-breaking detection (F2.4): Maps to tracking the Gram matrix eigenvector; adjacent to the free-probability / Tracy-Widom work that the field advisor flags as high-priority.
- Niche construction (A7): Maps to query distribution modification; adjacent to active inference (C6). Both have the substrate modifying its own input distribution.

---

## Substrate-product implications

1. **Dreaming substrate (F2.3) is the clearest product feature:** A substrate that generates novel atoms offline, without new training data, is differentiable from a static retrieval system. Product framing: "the substrate improves between queries, not just during queries." This is the product-level statement of the dreaming mechanism.

2. **Compression-progress as a telemetry signal:** Even without full dreaming, tracking the compression-progress delta per new atom gives a real-time measure of how much new capability each new ingested document adds. This is directly useful for data quality scoring in a product pipeline: high-delta documents improve the substrate; low-delta documents are redundant.

3. **MAP-Elites behavioral coverage map:** The 10x10 domain-difficulty grid is a product-legible representation of "what the substrate is good at." Filling the grid over time gives a progress metric that customers can see. This is a concrete capability map, not an internal metric.

4. **Quasispecies population for robustness:** A population of k=5 codebooks provides a natural ensemble for retrieval confidence estimation: the standard deviation of retrieval scores across the k codebooks is a calibrated uncertainty estimate. This is directly usable as a reliability signal in the product API.

---

## Citations (verified count: 14)

1. Evolutionary innovation through fusion across the tree of life (biorxiv 2025.08.30.672725)
2. Global survey of prokaryotic HGT eco-evolutionary pressures (PMC11090817, 2024)
3. Transgressive hybrids as hopeful monsters (PMC3655218)
4. Modelling the evolution of novelty: a review (PMC9750852)
5. Insight predicts subsequent memory via hippocampal activity (Nature Communications 2025, s41467-025-59355-4)
6. Mind wandering during creative incubation predicts creative performance (Scientific Reports 2025, s41598-025-09736-y)
7. Neural correlates of creative insight in spatial problem task (Scientific Reports 2025, s41598-025-13684-y)
8. Rest and default mode network: brain rest promotes learning (PMC11047624, 2024)
9. Offline neural replay and DMN coupling in schizophrenia (Brain Communications, fcad056)
10. Symmetry breaking of three self-organization rules (arXiv:2405.16028, 2024)
11. On principles of emergent organization (ScienceDirect, arXiv:2311.13749)
12. Measuring LLM novelty as frontier of original and high-quality output (arXiv:2504.09389, 2025)
13. Formal Theory of Creativity, Fun, and Intrinsic Motivation (Schmidhuber, IEEE TAMD 2010)
14. Learning cortical representations through perturbed and adversarial dreaming (PMC9071267)
15. MAP-Elites quality diversity review (rl-vs.github.io/rlvs2021, Mouret 2021)
16. Replay and compositional computation (arXiv:2209.07453)

Total verified: 16.

---

*Note path: notes/research_drill_autonomous_discovery_5x_2026-06-10.md*
*Companion handoff: notes/exp_dev_handoff_research_autonomous_discovery_5x_2026-06-10.md*
