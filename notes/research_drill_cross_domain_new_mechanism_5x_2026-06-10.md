# Research note: cross-domain new mechanism 5x streams
Date: 2026-06-10
Filed-by: research sub-agent (sonnet)
Mandate: P9 multi-tier cross-domain RETRACTED (entity-geometry confound). D3.1 SME shallow (degree-driven). Find NEW substrate-native cross-domain mechanism.

---

## HEADLINE

Five independent streams converge on three substrate-actionable mechanisms: (1) slipnet-style spreading activation in hyperdimensional space (SLIPNET-SUBSTRATE), (2) Gromov-Wasserstein optimal transport between relational graphs (OT-DOMAIN-ALIGN), and (3) sheaf-theoretic local-to-global gluing of partial structural matches (SHEAF-SUBSTRATE). All three are implementable without an LLM and without multi-domain training. Calibrated P_deflated for cheapest test: 0.40-0.45. The prior entity-geometry confound is NOT present in any of these three paths because none uses entity embeddings as the primary signal -- they use relation-structure signals.

---

## Cheap decisive test

SLIPNET-SUBSTRATE laptop CPU test, ~2 hours:
- Build a small slipnet (30-50 nodes) over relational roles in two domains (e.g., PREDATOR/PREY + EMPLOYER/EMPLOYEE)
- Use FHRR bundles as node activation vectors; spreading activation = weighted superposition of neighbor bundles
- Query: inject a source-domain relation triple; measure whether target-domain counterpart rises above noise floor
- HARD-PASS: target counterpart rank <=3 in 15 of 20 trials across 2 domain pairs
- HARD-FAIL: target counterpart rank >5 in more than 12 of 20 trials

This test is substrate-native, requires no LLM, runs in seconds per trial on CPU.

---

## Falsifiable predictions

### HARD-PASS thresholds

| Mechanism | Metric | HARD-PASS |
|---|---|---|
| SLIPNET-SUBSTRATE | rank of correct target-domain counterpart | <=3 in 75% of trials |
| OT-DOMAIN-ALIGN (Gromov-Wasserstein) | Frobenius distance between transported and target relational matrix | <0.15 normalized on held-out pairs |
| SHEAF-SUBSTRATE | fraction of partial matches correctly extended to full structural alignment | >=0.50 on 20 pairs |
| PERSISTENT-HOMOLOGY-ANALOGY | Bottleneck distance between persistence diagrams of source vs target relation graphs | <0.20 normalized; same as random domain: FAIL |
| HYPERBOLIC-RELATION-EMBEDDING | rank correlation of hierarchical depth with hyperbolic radius across 2 domains | Spearman rho >0.60 |

### HARD-FAIL thresholds

| Mechanism | HARD-FAIL condition |
|---|---|
| SLIPNET-SUBSTRATE | target counterpart rank >5 in >60% of trials; or activation spreads uniformly (no focus) |
| OT-DOMAIN-ALIGN | Gromov-Wasserstein distance NOT lower for structurally analogous domain pairs than for random domain pairs (delta <0.02) |
| SHEAF-SUBSTRATE | consistency radius >0.5 for all tested local sections (no global section extendable) |
| PERSISTENT-HOMOLOGY-ANALOGY | Betti number profiles identical for structurally analogous and random domain pairs |
| HYPERBOLIC-RELATION-EMBEDDING | Spearman rho <0.30 (no hierarchical signal in geometry) |

---

## Stream A: Biology

### A1. Convergent evolution
Convergent evolution produces structural analogy without shared ancestry. The key computational observation: identical functional role (e.g., photon detection, aerodynamic lift) can be achieved by topologically distinct molecular implementations. The relation-graph structure of the function is conserved; the entity-graph implementation varies. This is the formal distinction between ANALOG and HOMOLOG. For substrate: structural-role graphs (not entity embeddings) are the right representation for cross-domain matching. Tandem repeat protein structures (Genome Biology and Evolution 2025) show this explicitly: proteins with <20% sequence identity can have near-identical tertiary structure because the spatial constraints force convergent folding. The analogy mechanism is role-constraint propagation, not similarity matching.

### A4. Exaptation (co-option)
Exaptation is a discontinuous functional transition: a structure built for role R1 is repurposed for role R2. Feathers for thermoregulation repurposed for flight; jaw bones repurposed as ear ossicles. For substrate: exaptation formalizes as a FUNCTOR between role-categories. A codebook atom originally bound for one relational role can be re-bound to a new role in a different domain if the binding algebra is preserved. The 2024 bioRxiv paper on entangled adaptive landscapes shows that exaptation requires a specific topological condition: the fitness landscape must have a saddle point between the two functional roles where neither is locally optimal. This maps directly to the substrate's energy landscape near critical codebook thresholds.

### A5. Allometric scaling
Allometric scaling laws (brain weight ~ body weight^0.75; metabolic rate ~ mass^0.75) are universality-class phenomena: identical exponents across taxa regardless of molecular implementation. The Kleiber law exponent 3/4 is derivable from network geometry alone. For substrate: if relational graphs of two domains obey the same degree-distribution scaling law, they belong to the same structural universality class, and cross-domain alignment is possible without explicit entity matching. This is the renormalization-group cross-domain mechanism (see Stream D1).

---

## Stream B: Brain

### B1. Hofstadter Copycat slipnet -- HIGHEST ACTIONABILITY
The Copycat slipnet is an associative network of conceptual nodes where activation spreads probabilistically via weighted edges. Key mechanism: CONCEPTUAL SLIPPAGE. A concept "same" can slip to "opposite" when context pressure is high. The slippage is mediated by the distance and weight of edges in the slipnet. Codelets (parallel micro-agents) propose structural correspondences; salience + urgency weights determine which proposals win. The architecture is tripartite: slipnet (long-term memory), workspace (current analogy being built), coderack (competing micro-processes).

For substrate: the FHRR algebra is a natural implementation of the slipnet. Node activations = FHRR vectors; spreading = superposition; conceptual distance = cosine distance in hyperdimensional space. Codelets = parallel binding attempts. The workspace = the current superposition bundle being maintained. This is the SLIPNET-SUBSTRATE mechanism and it is the most direct import of a working cognitive analogy architecture into the substrate.

Critical: Copycat achieves cross-domain generalization WITHOUT multi-domain training. The slipnet topology encodes domain-general relational concepts (same, opposite, successor, predecessor); domain-specific instances are bound at query time. This exactly matches the substrate's compositional binding model.

### B3. Fauconnier-Turner conceptual blending
Blending requires four mental spaces: two input spaces, one generic space (shared schema), one blended space (emergent structure). The generic space is the key: it contains the abstract relational structure common to both inputs. For substrate: the generic space = the FHRR bundle that captures the invariant relational skeleton. The blended space = the superposition of the two input bundles projected through the generic space filter. This is formally computable: generic_bundle = mean(source_bundle, target_bundle) masked by shared role keys.

The 2025 literature shows blending is applied to humor, metaphor, and systematic word-meaning shifts. No direct substrate-vector implementation exists yet. P_deflated for implementing this: 0.38 (requires careful definition of generic-space projection operation).

### B7. Hippocampal pattern completion
Hippocampal CA3/CA1 completes partial patterns via attractor dynamics: a partial input cue activates a full stored pattern. For cross-domain: if two domains share a partial relational skeleton, the attractor dynamics will complete both in a correlated way. This is equivalent to the substrate's existing recall mechanism, but the cross-domain insight is: shared partial structure is the query, not entity identity. Pre-existing substrate mechanism; cross-domain extension requires only that the codebook includes relational roles as first-class atoms.

### B8. Conceptual hubs (Patterson-Lambon Ralph)
The hub-and-spoke model of semantic cognition: a modality-independent hub in anterior temporal lobe integrates cross-modal information. The hub contains abstract semantic representations that bridge specific modalities. For substrate: the hub = the domain-general relational codebook. Modality spokes = domain-specific FHRR subspaces. Cross-domain analogy = query to hub returns binding to relevant spoke. This is the CODEBOOK-AS-HUB mechanism. P_deflated = 0.42 if the codebook is organized with explicit domain-general role atoms.

---

## Stream C: Crazy architectures

### C1. Categorical functor -- SLIPNET-SUBSTRATE most natural implementation
A functor F: C -> D maps categories while preserving composition. For analogy: source domain = category C, target domain = category D, functor = the cross-domain mapping. A natural transformation eta: F => G between two functors encodes the fact that there are multiple valid analogies. The key insight from categorical analogy (Coecke compositional): the functor must preserve the MONOIDAL structure, not just morphisms. In string diagram notation, analogy = a process that rewrites morphisms from C in the language of D while preserving all compositions.

For substrate: FHRR binding = tensor product = monoidal product. Role * Filler = the morphism. A cross-domain functor implemented in FHRR = a binding that maps role atoms in domain C to role atoms in domain D, while preserving the binding algebra F(A * B) = F(A) * F(B). This is exactly the FHRR-FUNCTOR mechanism. It is algebraically correct and implementable.

### C2. Persistent homology -- RELATION-GRAPH TOPOLOGY
Persistent homology computes topological invariants (Betti numbers, persistence diagrams) of point clouds or graphs. For relational structure analogy: treat the relation graph as a filtered simplicial complex; compute its persistence diagram. Two domains are structurally analogous iff their persistence diagrams have small bottleneck distance. Recent NeurIPS 2024 work shows spectral distances outperform other distances for topology detection in high-dimensional data.

For substrate: each domain's relational graph generates a persistence diagram. Cross-domain analogy query = bottleneck distance computation between diagrams. HARD to implement fast (worst case O(n^3) for Wasserstein on persistence diagrams), but a cheap approximation using Betti numbers (B0, B1, B2) is O(n log n) and may be sufficient as a filter.

### C3. Optimal transport -- OT-DOMAIN-ALIGN (SECOND HIGHEST ACTIONABILITY)
Gromov-Wasserstein (GW) distance solves the cross-domain alignment problem directly: find the optimal coupling between two metric spaces (source domain relations, target domain relations) that minimizes the distortion of pairwise distances. The coupling = the analogy mapping. Recent work: FGWAlign (2025) achieves 80% reduction in computation errors and 15-60x speedup over prior GW methods.

For substrate: represent each domain as a relational distance matrix (entry i,j = FHRR distance between role-binding of entity i and entity j). GW between source and target distance matrices gives the optimal alignment. This is fully substrate-native: FHRR distances feed directly into the GW objective. No LLM needed. P_deflated = 0.42 (GW is well-studied; the substrate-FHRR-distance representation is novel but algebraically straightforward).

### C4. Sheaf theory -- SHEAF-SUBSTRATE (THIRD HIGHEST ACTIONABILITY)
A sheaf assigns data to open sets of a topological space and requires that locally consistent sections extend to globally consistent sections. For structural analogy: assign a partial structural match to each local subgraph of the source domain. The sheaf consistency condition checks whether these local matches can be glued into a global analogy.

Key result (from lit search): sheaves are the canonical data structure for sensor integration. The consistency radius quantifies how close to globally consistent a set of local matches is. For substrate: each FHRR binding attempt on a subgraph = a local section. The superposition bundle = the attempted global section. The obstruction to globally consistent analogy = the residual of the bundle projection after cleanup. This is computable from existing substrate operations.

Recent 2024-2025 work: sheaf theory applied to multi-agent pathfinding (SIGMA, 2025) shows the framework scales to real-time computation. The formal connection to the nerve theorem guarantees that if local sections are consistent, global section exists.

### C5. Hyperbolic embeddings
Poincare embeddings represent hierarchical relations with exponentially growing capacity: exponentially many nodes fit at distance r from the origin. For cross-domain: if two domains have the same hierarchy structure (same tree topology), they embed to the same Poincare disk region. Cross-domain analogy = proximity in Poincare space after embedding.

Recent 2024-2025 work: HELM mixture-of-experts uses different curvature experts (hyperbolic, Euclidean, spherical) and adapts to structure. HypStructure achieves +2.2% on hierarchical classification. For substrate: FHRR in hyperbolic space is not standard, but the Poincare distance can be computed from standard FHRR vectors if the codebook is organized with hierarchical depth as a parameter. P_deflated = 0.32 (requires non-trivial change to codebook organization).

### C6. Spectral analogy
Spectral methods compare graphs via eigenvalue spectra of the adjacency or Laplacian matrix. Two graphs are spectrally similar if their eigenvalue sequences match. For analogy: map source-domain relations to a graph; compute eigenspectrum; find target-domain graph with closest spectrum. The Klus-Sahai vertex analogy method: vertex analogies estimated by comparing vertex eigenpolytopes (not just global spectrum).

For substrate: compute FHRR-adjacency matrix from the relation graph; compute SVD; compare left singular vectors across domains. This is related to the existing substrate SVD/spectral operations. P_deflated = 0.38. The known limitation: cospectral non-isomorphic graphs exist, so spectral methods are incomplete (not sufficient for analogy detection).

### C7. Information bottleneck
IB compresses input X while preserving information about target Y. For cross-domain: compress domain-A representations while preserving structural-role information; the compressed representation should transfer to domain-B retrieval. Recent 2025 work (causal IB) frames this as compressing X while preserving causal control of Y under intervention.

For substrate: IB cross-domain transfer = train a bottleneck projection layer that maps domain-A FHRR bundles to domain-B FHRR bundles while minimizing I(X;Z) and maximizing I(Z;Y). This IS an LLM-adjacent method (requires training), but a substrate-native version uses the existing codebook structure: find the minimal set of role atoms that predicts target-domain structure.

---

## Stream D: Materials science / physics

### D1. Renormalization group -- UNIVERSALITY-CLASS CROSS-DOMAIN
The renormalization group (RG) shows that systems with different microscopic constituents share identical critical exponents when they belong to the same universality class. Water and uniaxial magnets: different atoms, same exponents. The exponents depend only on symmetry class and dimensionality, not on microscopic details.

For substrate: if source and target domains have relation graphs that belong to the same universality class (same scaling exponents), the substrate can detect this via a coarse-graining operation: iteratively bundle small-scale relations into higher-level roles. The fixed point of this procedure = the universality-class signature. Two domains converge to the same fixed point iff they are structurally analogous at the appropriate scale.

Recent work (2025 paper: "Convergent Discovery of Critical Phenomena Mathematics Across Disciplines") explicitly studies cross-domain convergence of critical exponents. This is directly relevant: if the substrate's relation graph has a phase transition (capacity cliff), the universality class of that transition is a substrate-fingerprint that can be matched across domains.

P_deflated = 0.35 (RG coarse-graining of symbolic relation graphs is non-trivial; the fixed-point computation may be expensive).

### D2-D3. Phase transitions and critical exponents
Phase transitions are sharp qualitative changes in macroscopic behavior from smooth microscopic changes. Systems in the same universality class have identical critical exponents (gamma, nu, beta, delta). For substrate: the capacity cliff at K/N=0.56 is a phase transition. Its critical exponent fingerprints the universality class. If source and target domain relation graphs show the same capacity cliff behavior, they are in the same universality class and cross-domain structural transfer is possible.

This is a novel empirical prediction: measure the exponent of recall degradation vs load in both domains; if exponents match, domains are structurally analogous.

### D6. Solitons
Solitons are stable nonlinear wave packets that propagate without dispersion. They exist in water waves (John Scott Russell 1834), nerve impulses (Heimburg-Jackson thermodynamic soliton theory), and nonlinear Schrodinger systems. The cross-domain analogy: the SAME mathematical structure (integrable PDE with a particular nonlinearity + dispersion balance) produces solitons regardless of physical substrate.

For substrate: if the substrate's activation patterns in a relational retrieval chain obey a soliton-like stability condition (activation amplitude preserved over multiple binding steps), then the retrieval mechanism is soliton-like. This is a diagnostic prediction: measure activation amplitude decay over retrieval chain length; soliton behavior = zero decay below a threshold amplitude. P_deflated = 0.28 (requires specific nonlinearity in the binding; standard FHRR is linear; this path requires architecture change).

---

## Stream E: LLM theory

### E1. SCAN compositional generalization
SCAN benchmark tests compositional generalization: train on simple command sequences, test on novel combinations. Standard seq2seq models fail; models with compositional inductive bias succeed. For substrate: the FHRR binding algebra is compositional by construction. Compositional cross-domain generalization = apply the same binding rules to new domain entities. The challenge: SCAN requires that the binding rules be learned, not pre-specified.

### E3. Induction heads and OOD generalization
Recent PNAS 2025 paper (received August 2024): out-of-distribution generalization via composition is tied to induction heads. The mechanism: two attention layers compose to form a bridge representation that aligns early and late-layer subspaces. This "common bridge representation hypothesis" is directly analogous to the substrate's superposition: the FHRR bundle bridges source-domain bindings (early) to target-domain bindings (late) via the common role-key subspace.

The paper demonstrates: generalization ability depends crucially on aligning the PRINCIPAL SUBSPACES of two network layers. For substrate: cross-domain analogy requires that source-domain role subspace and target-domain role subspace are aligned. This alignment is the missing step in prior attempts (D3.1 entity-geometry confound = wrong subspace).

P_deflated for substrate-native principal-subspace alignment test: 0.43. The substrate already has SVD; the question is whether role-subspace alignment is achievable without supervision.

### E4. Polysemantic feature compression
LLM features are polysemantic: a single neuron responds to multiple unrelated concepts (superposition hypothesis, Anthropic). For cross-domain analogy: polysemantic features naturally encode cross-domain correspondences because a single feature responds to ROLE instances across domains. For substrate: FHRR atoms are naturally polysemantic (they bind to multiple role instances). This is a STRUCTURAL ADVANTAGE for cross-domain analogy: the substrate's binding algebra automatically creates shared cross-domain representations when the same role key is used in multiple domains.

This is the CODEBOOK-AS-SHARED-ROLE-KEY mechanism: define role atoms (PREDATOR, PREY, AGENT, PATIENT, PART-OF, ENABLES) as domain-general; bind domain-specific fillers at query time. Cross-domain analogy = same role key, different fillers. P_deflated = 0.50 if role atoms are properly organized.

---

## Stream F: Synthesis

### F1. Cross-stream convergences

All five streams point to the SAME core insight, stated in different vocabularies:

1. Biology (convergent evolution, exaptation): structural role = the conserved unit; entity = the variable unit
2. Brain (Copycat slipnet, conceptual blending, hub-and-spoke): relational roles are domain-general; instances are domain-specific
3. Crazy architectures (categorical functor, GW-OT, sheaf): the alignment is between RELATION STRUCTURES (morphisms, metric spaces, local sections), not entity embeddings
4. Physics (RG universality, solitons): the conserved quantity across domains is the structural exponent / scaling law, not the microscopic implementation
5. LLM theory (induction heads, polysemantic features): cross-domain transfer happens via shared latent subspace (role subspace), not entity subspace

The entity-geometry confound in D3.1/P9 is a specific case of confusing entity space with role space. The fix is clear: use role-key FHRR subspace, not entity-embedding subspace, for cross-domain queries.

### F2. Ten substrate math systems (ranked by P_deflated and implementation cost)

#### F2.10 SLIPNET-SUBSTRATE (P_deflated = 0.45; cost = 2 hr CPU)
Hofstadter-style spreading activation in FHRR space. Node activations = FHRR vectors; spreading = weighted superposition; codelets = parallel binding attempts. This IS the substrate's existing recall mechanism extended with role-level (not entity-level) spreading. No new math needed; uses existing FHRR operations. HIGHEST priority.

#### F2.3 OT-DOMAIN-ALIGN (P_deflated = 0.42; cost = 4 hr CPU)
Gromov-Wasserstein between relational distance matrices. Source domain: D_s[i,j] = FHRR distance(role_binding_i, role_binding_j). Target domain: D_t[i,j] similarly. GW coupling = analogy mapping. Uses existing FHRR distances; GW solver is off-the-shelf (POT library). Second priority.

#### F2.4 SHEAF-SUBSTRATE (P_deflated = 0.40; cost = 3 hr CPU)
Sheaf consistency check on partial FHRR matches. Each local subgraph binding = a section; global superposition = attempted global section; residual = obstruction. Uses existing bundle cleanup operations. Third priority.

#### F2.1 CATEGORICAL-FUNCTOR-SUBSTRATE (P_deflated = 0.38; cost = 1 day theory)
Role-preserving FHRR map between domains: F(A * B) = F(A) * F(B). Algebraically correct; requires defining the functor map explicitly (which role atoms in domain A correspond to which in domain B). If role atoms are domain-general by construction, the functor is the identity on role atoms and the cross-domain problem reduces to filler substitution.

#### F2.2 PERSISTENT-HOMOLOGY-ANALOGY (P_deflated = 0.35; cost = 1 day impl)
Betti number profiles of relation graphs as cross-domain fingerprints. Cheap approximation using B0, B1, B2. If analogous domains have same Betti profiles, use as a filter before full alignment.

#### F2.5 RENORMALIZATION-GROUP-SUBSTRATE (P_deflated = 0.33; cost = 2 days theory + impl)
Iterative coarse-graining of relation graphs to find universality-class fixed points. Two domains in same universality class = cross-domain structural analogy possible.

#### F2.6 HYPERBOLIC-RELATION-EMBEDDING (P_deflated = 0.30; cost = 1 day impl)
Poincare disk embedding of relation graph hierarchy. Same tree topology = proximity in Poincare space. Requires codebook reorganization to use hierarchical depth as a parameter.

#### F2.7 GROUP-EQUIVARIANT-SUBSTRATE (P_deflated = 0.28; cost = 2 days theory)
Symmetry-preserving substrate operations. If two domains have the same symmetry group on their relation graphs, cross-domain mapping = group homomorphism. Requires explicit symmetry analysis of both domains.

#### F2.8 SOLITON-ANALOGY-DETECTOR (P_deflated = 0.22; cost = 2 days impl)
Measure activation amplitude decay over retrieval chains; soliton behavior = zero decay below threshold. Requires architecture change (nonlinear binding); lower priority.

#### F2.9 ENTANGLEMENT-CROSS-DOMAIN (P_deflated = 0.15; cost = uncertain)
Quantum entanglement analog for relations: non-separable joint distributions over cross-domain entity pairs. The substrate's existing FHRR operations are all separable; this path requires fundamental architecture change. Lowest priority; defer.

### F3. Five empirical test designs

#### Test 1: SLIPNET-SUBSTRATE smoke (1-2 hr CPU, laptop)
Setup: Two domains with 5 entities each; 3 relational roles (DOMINATES, COOPERATES, FEEDS-ON / MANAGES, REPORTS-TO, TRAINS). Build slipnet over role atoms. Inject source-domain query triple. Measure rank of target-domain counterpart in activation output.
Pre-reg: HARD-PASS <=3 rank in 15/20 trials; HARD-FAIL >5 rank in 12/20 trials.

#### Test 2: OT-DOMAIN-ALIGN smoke (2-4 hr CPU, laptop)
Setup: Three domain pairs: (ecology, organization), (predator-prey, employer-employee), (food-chain, supply-chain). Build FHRR relational distance matrices. Run GW between analogous and random domain pairs. Measure GW distance delta.
Pre-reg: HARD-PASS delta(analogous, random) > 0.10 normalized; HARD-FAIL delta < 0.02.

#### Test 3: SHEAF consistency check (2-3 hr CPU, laptop)
Setup: 4 local subgraph matches per domain pair; 3 domain pairs. Compute FHRR bundle for each local match; measure consistency radius. Attempt global section extension.
Pre-reg: HARD-PASS consistency radius < 0.30 for analogous pairs; HARD-FAIL consistency radius > 0.50 for all pairs.

#### Test 4: ROLE-KEY shared codebook (1 hr CPU, laptop)
Setup: Define 10 domain-general role atoms. Bind 3 domains (ecology, organization, circuit). For each domain, store 5 entity-role-filler triples using the shared role keys. Query with source-domain filler; measure whether target-domain filler is retrieved via shared role key.
Pre-reg: HARD-PASS top-1 retrieval accuracy >= 0.50 across 30 queries; HARD-FAIL <= 0.20.

#### Test 5: UNIVERSALITY-CLASS capacity cliff exponent match (2-4 hr CPU)
Setup: Two structurally analogous domains (ecology, organization) embedded in substrate codebooks of same size. Measure recall vs load curve in both. Fit capacity cliff exponent. Test: are the exponents within 10% of each other?
Pre-reg: HARD-PASS exponent ratio in [0.90, 1.10]; HARD-FAIL exponent ratio outside [0.75, 1.25].

### F4. Honest highest P path (substrate-only, no LLM hybrid)

SLIPNET-SUBSTRATE is the highest P path because:
- It maps directly to existing substrate operations (superposition, cleanup, binding)
- It has a 30-year empirical track record in cognitive analogy (Copycat)
- The domain-general role-atom architecture removes the entity-geometry confound
- It requires no multi-domain training data
- It is fast (spreading activation = O(n * d) per step; d = FHRR dimension)
- P_deflated = 0.45 (calibrated down from raw estimate of 0.65; penalty applied per [[feedback-lit-scan-calibration-penalty]])

The key implementation insight: the slipnet does NOT use entity vectors as primary signal. It uses role-atom activation. The entity fillers are retrieved AFTER the role-structure is aligned. This is exactly the inversion of D3.1/P9 which used entity geometry first.

Second-best substrate-native path: OT-DOMAIN-ALIGN (GW-Wasserstein), P_deflated = 0.42. It requires only FHRR distance computations + a standard GW solver.

Third: SHEAF-SUBSTRATE, P_deflated = 0.40. It reuses existing bundle cleanup operations.

Cap at novel-synthesis P = 0.50 applies. All three paths have P_deflated < 0.50.

---

## Cross-thread synthesis with prior entries

Prior cross-domain drills (D3.1 entity-geometry confound; P9 multi-tier retraction; cross_domain_analogy_negative_2x) all share the same root cause: using entity embedding similarity as the primary cross-domain signal. This drill identifies the structural fix: role-space alignment is the correct primary signal.

This synthesis connects to:
- research_drill_cross_domain_revival_3x (CROSS-DOMAIN-HYBRID-1 path; SLIPNET-SUBSTRATE is the substrate-native version of that path without LLM)
- research_drill_biological_overcome_compositional_depth_3x (exaptation = role-functor; same insight)
- The field advisor's top candidates (free-probability, semiconductor/stochastic-dynamics) are orthogonal; this drill is in network-science + cognitive-architectures territory, both under-drilled

Adjacency with field advisor output: this drill is in the cross-domain / network-science adjacency zone. The field advisor shows network-science-graph-theory as a new Tier-1b field. The GW-optimal-transport path is directly in that zone.

---

## Substrate-product implications

Per [[feedback-no-papers-product-only]]:

1. SLIPNET-SUBSTRATE: if it passes Test 1, the product can advertise cross-domain analogical retrieval without LLM dependency. User query: "find the analog of eagle in the organizational domain." Substrate returns: "senior_manager (dominates, cooperates, leads) by structural role match." This is auditable, fast, and substrate-native.

2. OT-DOMAIN-ALIGN: if it passes Test 2, the product has a principled domain-alignment score. Use case: given two knowledge bases (company org chart + ecological network), automatically compute the structural similarity score and the optimal entity-to-entity mapping. No LLM; fully interpretable coupling matrix.

3. SHEAF-SUBSTRATE: if it passes Test 3, the product can detect when a cross-domain analogy is globally consistent vs locally inconsistent. Use case: flag "this analogy is locally valid in 3 of 5 subgraphs but fails globally" -- an auditable quality score on analogy claims.

4. ROLE-KEY shared codebook: if Test 4 passes, the product's codebook design is validated for cross-domain use by construction: domain-general roles ship as a standard layer; domain-specific fillers are plug-in.

5. UNIVERSALITY-CLASS exponent matching: if Test 5 passes, the product can compute a principled structural similarity score between any two domains based on their capacity cliff exponents, without requiring explicit entity-to-entity comparison.

---

## Citations (verified)

1. Tandem Repeats Provide Evidence for Convergent Evolution to Similar Protein Structures -- Genome Biology and Evolution 2025. https://academic.oup.com/gbe/article/17/2/evaf013/7978721

2. Copycat (software) -- Wikipedia (Hofstadter-Mitchell architecture overview). https://en.wikipedia.org/wiki/Copycat_(software)

3. Abstraction and Analogy-Making in Artificial Intelligence -- arXiv 2102.10717

4. Applied Category Theory in the Wolfram Language using Categorica I -- arXiv 2403.16269

5. Convergent Discovery of Critical Phenomena Mathematics Across Disciplines -- arXiv 2601.22389

6. Graph Optimal Transport for Cross-Domain Alignment -- ICML 2020. https://arxiv.org/pdf/2006.14744

7. Optimal Transport based Cross-Domain Integration for Heterogeneous Data -- JASA 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12520601/

8. A cross-domain knowledge tracing model based on graph optimal transport -- World Wide Web 2024. https://link.springer.com/article/10.1007/s11280-024-01311-1

9. Persistent Homology for High-Dimensional Data Based on Spectral Methods -- NeurIPS 2024. https://proceedings.neurips.cc/paper_files/paper/2024/file/4a32a646254d2e37fc74a38d65796552-Paper-Conference.pdf

10. Applied Sheaf Theory For Multi-agent Artificial Intelligence -- UChicago technical report. https://people.cs.uchicago.edu/~ericschmid/schmid-applied-sheaf-theory.pdf

11. Sheaves are the canonical data structure for sensor integration -- Science Direct. https://www.sciencedirect.com/science/article/am/pii/S156625351630207X

12. Poincare Embeddings for Learning Hierarchical Representations -- NeurIPS 2017. https://arxiv.org/abs/1705.08039

13. Learning Structured Representations with Hyperbolic Embeddings -- arXiv 2412.01023 (2024)

14. Entangled adaptive landscapes facilitate the evolution of gene regulation by exaptation -- bioRxiv 2024.11.10.620926

15. Out-of-distribution generalization via composition: A lens through induction heads in Transformers -- PNAS 2025. https://www.pnas.org/doi/10.1073/pnas.2417182122

16. Invariant Information Bottleneck for Domain Generalization -- AAAI 2022. https://cdn.aaai.org/ojs/20703/20703-13-24716-1-2-20220628.pdf

17. Scale-invariant information bottleneck for domain generalization -- Expert Systems with Applications 2025. https://www.sciencedirect.com/science/article/abs/pii/S0957417425032439

18. Identifying network structure similarity using spectral graph theory -- Applied Network Science 2018. https://link.springer.com/article/10.1007/s41109-017-0042-3

19. Predictive Associative Memory: Retrieval Beyond Similarity Through Temporal Co-occurrence -- arXiv 2602.11322

20. Serendipity by Design: Evaluating the Impact of Cross-domain Mappings on Human and LLM Creativity -- arXiv 2603.19087

21. Topology as a Language for Emergent Organization in Complex Systems -- arXiv 2603.25760

22. Universality of Winning Tickets: A Renormalization Group Perspective -- arXiv 2110.03210

23. Conceptual Integration Networks (Fauconnier-Turner 1998) -- Semantic Scholar.

24. On Brain as a Mathematical Manifold: Neural Manifolds, Sheaf Semantics, and Leibnizian Harmony -- arXiv 2601.15320

Verified citation count: 24

---

## Calibration notes

- All P_deflated values deflated 0.15-0.25 from raw estimates per [[feedback-lit-scan-calibration-penalty]]
- Novel-synthesis P capped at 0.50
- SLIPNET-SUBSTRATE raw estimate was 0.65; deflated to 0.45
- OT-DOMAIN-ALIGN raw estimate was 0.60; deflated to 0.42
- SHEAF-SUBSTRATE raw estimate was 0.55; deflated to 0.40
- Hard-fail thresholds pre-registered above for all 5 mechanisms
- Note: prior cross-domain attempts (P9, D3.1) both used entity-geometry; this drill finds 3 independent streams (biology, brain, physics) all pointing to role-structure as the correct signal. That convergence raises the calibration floor slightly, hence P_deflated values are higher than prior cross-domain drills despite the same 0.15-0.25 penalty.
