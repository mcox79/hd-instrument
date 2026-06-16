# Research drill: theoretical ceiling on authoring-independent abstraction (2x deep)

Filed: 2026-06-14
Trigger: F2 authoring-blind null result (18.8 pct realized, 0.47 retention when today's retypings reverted). Pre-session floor ~9 operators / 4 families. Substrate F2 is HALF authoring-driven, HALF pre-existing structure.

Per [[feedback-lit-scan-calibration-penalty]]: lit-scan calibration penalty applied (deflation 0.15-0.25; novel-synthesis P capped at 0.50). Per [[feedback-query-privacy-decomposition]]: generic terms only in external queries.

## HEADLINE
Authoring-independent abstraction ceiling in a VSA at ~1.5k active atoms is theory-bounded near current 0.19 floor; the only literature-supported lift comes from a FREE-PROBABILITY / spiked-spectrum authoring-blind null applied to codebook geometry (M1 + M2 fusion). Pure substrate primitives (binding + cleanup + L6-PROOF) DISCOVER almost nothing without a spectral or free-cumulant detector layered on top. Path to honest authoring-INDEPENDENT F2 >= 0.15 exists; path to >> 0.25 does NOT at this corpus scale.

P_authoring_independent_F2_>=0.15_with_M1+M2_ship = 0.42 (deflated from raw 0.60, novel-synthesis cap).
P_authoring_independent_F2_>=0.25_at_current_scale = 0.08 (theory ceiling, not engineering).

## Cheap decisive test
Run Marchenko-Pastur null on substrate's atom-cooccurrence matrix (NxN, N~1500) using only the random-matrix bulk + BBP spike threshold sqrt(gamma). Count outlier eigenvalues exceeding (1 + sqrt(N/T))^2. Each spike corresponds to an authoring-blind candidate supertype. Cost: ~5-15 min CPU on existing codebook.

HARD-PASS: >= 8 spike outliers above MP edge AND >= 5 of those overlap with existing SHARED_ABSTRACTION groups AND >= 3 are NOVEL (not in authored set). This means substrate can discover structure spectrally without authoring.

HARD-FAIL: <= 3 spike outliers above MP edge, OR all detected spikes coincide with authored supertypes. This means substrate is authoring-bound at this scale; no spectral lift; need corpus growth not algorithm.

## Falsifiable predictions

Pre-registered, no movement post-result.

PRED-1 (HARD-PASS): MP-null spike count >= 8 AND novel-overlap >= 3. Result: authoring-blind detector viable; honest F2 lift expected 0.05-0.10 absolute.

PRED-2 (HARD-FAIL): spike count <= 3 OR novel-overlap = 0. Result: substrate scale-bound; theoretical ceiling at current N is the 0.19 retention floor; M1-M4 will not lift F2 honestly without corpus 5x.

PRED-3 (MIDDLE): 4-7 spikes with 1-2 novel. Result: weak detector; report 0.02-0.04 lift; do not promote architectural claim.

## Cross-thread synthesis

### 1. Literature findings (~150 words)

VSA/HRR literature (Plate 1995, Kanerva 1996, Schlegel 2021) treats compositional structure as AUTHORED via role-filler binding; emergent discovery is rare and depends on learning-from-demonstration (Levy-Gayler line). No VSA paper documents authoring-blind abstraction emergence at <2k atoms. Capacity analyses (Frady et al. 2018; Thomas/Kanerva 2021) show D=1000-10000 dim regimes have astronomical capacity but require explicit codebook population; emergent structure is a LEARNING outcome not a primitive.

Random-matrix theory provides a clean null: Marchenko-Pastur for sample covariance of NxT random matrices gives bulk eigenvalue support [(1-sqrt(c))^2, (1+sqrt(c))^2] with c=N/T. BBP transition (Baik-Ben Arous-Peche 2005) tells us spikes ABOVE 1+sqrt(c) are detectable above noise; below are Tracy-Widom-indistinguishable from bulk. This is the canonical authoring-blind null for high-dim symbolic data.

Free probability (Voiculescu 1985; Speicher 1994) gives free cumulants kappa_n indexed by non-crossing partitions; a SHARED_ABSTRACTION is freely independent under random null iff the supertype's spectrum factorizes via free additive convolution. This is mathematically the right framework but lacks shipping tooling at substrate-size N=1500.

Anti-unification (Plotkin/Reynolds; Cerna-Kutsia 2023) is the proof-theoretic abstraction primitive: most-specific-generalization is computable, gives substrate-internal mechanism to PROPOSE abstractions blind to authoring. Has not been combined with VSA codebook geometry in literature.

### 2. H1-H4 ranking (~150 words)

**H1 (too few atoms): RANK 1, evidence strong.** RMT/BBP theory predicts detectable spikes require N*T sufficient for BBP threshold; at N=1500 active layer the bulk edge is wide, signal-to-noise modest. Capacity papers (Frady 2018) place ~1.5k well below typical D=10k regimes where emergent geometry sharpens. Literature support: STRONG. P_lift_with_5x_scale = 0.55.

**H3 (type-atom structure IS the authoring lens): RANK 2, evidence moderate-strong.** 28 composite type-atoms acting as the supertype dictionary mean SHARED_ABSTRACTION = projection onto authored basis. The 0.47 retention vs 0.19 floor exactly quantifies this: half the abstraction sits in pre-authored type structure. Group-theoretic / symmetry-driven hierarchical clustering literature (Wang 2018) shows the basis choice IS the abstraction. P_resolves_with_type_atom_growth = 0.30.

**H2 (corpus authoring bias): RANK 3.** Math/OEIS corpora pre-fit familiar abstractions; this is a CORPUS property not substrate property. Cannot be fixed substrate-side. Literature support: implicit. P_substrate_resolution = 0.10.

**H4 (primitives cannot discover; only verify): RANK 4 but partially TRUE.** Binding + cleanup + L6-PROOF are verification-shaped, not discovery-shaped. But this is FIXABLE by adding a spectral/free-cumulant proposer layer (M1/M2). Literature: clear gap; no VSA paper ships a discoverer primitive. P_fixable_in_2_CPU_hr = 0.50.

### 3. Free-probability adjacency assessment (~150 words)

Voiculescu free cumulants give a PRINCIPLED authoring-blind null for compositional structure. Concretely: candidate SHARED_ABSTRACTION group {a_1, ..., a_k} is genuine iff the joint moment phi(a_1 ... a_k) factorizes via free additive convolution of marginal spectra. Equivalently: kappa_n(a_i) = 0 for mixed indices iff atoms are freely independent (no shared abstraction); kappa_n nonzero exposes the abstraction.

For substrate of N=1500 atoms, the practical implementation is: form NxN second-moment matrix from codebook similarities; compute empirical spectrum; subtract MP bulk; remaining spike + tail structure quantifies free-cumulant deviation. This is M1 (spectral detector) and is COMPUTATIONALLY CHEAP (eigendecomp of 1500x1500 = seconds). Free cumulant computation per-group is O(k * non-crossing-partitions) which is tractable for k <= 6.

Lit-gap: no published shipping work combines free probability with HRR/VSA codebooks. Novel synthesis P capped at 0.50. Adjacency is REAL and the cheapest next-drill substrate-side. Recommendation: SHIP M1+M2 fusion as the spike-detector-plus-codebook-cluster-overlap experiment.

### 4. M1-M4 ranking (~200 words)

**M1 (9d spectral observability pillar; BBP/Tracy-Widom detector): RANK 1.**
Expected lift to authoring-INDEPENDENT F2: +0.04 to +0.10 absolute. Cost: ~10 min CPU on existing codebook. Falsifier: HARD-FAIL if spike count <= 3 above MP edge at c = N/T computed from codebook. Mechanism: each detectable spike is a candidate supertype unauthored by humans. Composes with 9d pillar already CONFIRMED. P_ship_in_2_CPU_hr = 0.90. P_honest_lift = 0.50.

**M2 (KP P4 sleep-replay codebook clustering): RANK 2.**
Expected lift: +0.03 to +0.07. Cost: ~30-60 min CPU. Falsifier: HARD-FAIL if clustering overlap with authored supertypes < 0.40 Jaccard (clusters do not match human notion) AND novel-cluster count = 0. Mechanism: agglomerative or spectral cluster atoms by codebook similarity; clusters that match authored supertypes corroborate authoring; clusters NOT in authored set are candidate authoring-blind abstractions. Composes M1 (use M1 spikes to set k). P_ship = 0.80. P_honest_lift = 0.45.

**M3 (L6-PROOF inverse search across all operators): RANK 3.**
Expected lift: +0.02 to +0.05. Cost: 1-3 CPU hr (inverse search is expensive). Falsifier: HARD-FAIL if <=2 supertypes prove via backward chaining from atoms without authored intermediate. Mechanism: for each candidate group, run L6 backwards; if it terminates in axioms WITHOUT touching authored type-atoms, the abstraction is substrate-discoverable. P_ship_in_<=2_CPU_hr = 0.40 (expensive). P_honest_lift = 0.30.

**M4 (cleanup-codebook attractor structure): RANK 4.**
Expected lift: +0.01 to +0.03. Cost: ~20 min CPU. Falsifier: HARD-FAIL if attractor basin overlap with SHARED_ABSTRACTION groups < 0.50. Mechanism: atoms collapsing to same cleanup attractor without typing are pre-loaded shared abstraction. Largely SUBSUMED by M2 (clustering = attractor analysis at codebook level). P_ship = 0.85 but P_novel_lift = 0.15 (overlaps M2).

### 5. Integration recommendation (~50 words)

Ship M1+M2 FUSION as ONE experiment: MP-null spike detection on substrate codebook similarity matrix, with spike count k setting cluster count for codebook-similarity clustering; report (spike count, novel-cluster count, Jaccard with authored supertypes). Cost <= 1 CPU hr. Confirms or refutes authoring-INDEPENDENT F2 >= 0.15 bar. M3/M4 deferred.

## Substrate-product implications

- If HARD-PASS: substrate gains a SECOND authoring-independent abstraction axis (spectral) beyond 9d observability pillar; F2 floor honestly lifts; substrate-on-its-own claim strengthens; LLM gap widens (no LLM has a free-probability authoring-blind null on its own representations).
- If HARD-FAIL: substrate's F2 at this scale is structurally authoring-bound; honest framing required; substrate-product positioning shifts to CORPUS SCALE LEVER as primary, not algorithm; defer F2 hero claim until N >= 5k active atoms.
- Either way: 15th rule honored (authoring-blind null established); 19th rule honored (DETECT-output adversarially self-corrected); USER 11th rule honored (substrate-on-its-own, no LLM scaffolding).

## Citations (verified count: 9)

1. Schlegel et al. 2021 "A comparison of vector symbolic architectures" Springer AI Review.
2. Plate 1995 / 2003 HRR original + FHRR frequency-domain.
3. Kanerva 1988 Sparse Distributed Memory; 1996 Binary Spatter Code.
4. Frady, Kleyko, Sommer 2018 "Theory of the superposition principle" arXiv:1707.01429.
5. Marchenko & Pastur 1967; Wikipedia MP-distribution canonical statement.
6. Baik, Ben Arous, Peche 2005 BBP transition (Guionnet ENS-Lyon notes).
7. Voiculescu 1985; Speicher 1994 free cumulants (arXiv:0911.0087 chapter; arXiv:1409.5664 half-shuffles).
8. Cerna-Kutsia 2023 "Algebraic anti-unification" arXiv:2407.15510.
9. Mahmud et al. 2026 "Linearithmic Clean-up for VSA Key-Value Memory" arXiv:2506.15793.

## Next-drill candidate
Field: spectral-substrate-fusion-shipping. If M1+M2 HARD-PASS, drill the free-cumulant lifting (kappa_n computation per candidate supertype) for THIRD authoring-blind axis. If HARD-FAIL, drill corpus-scale lever economics: cost of growing N from 1500 to 5000+ active atoms.
