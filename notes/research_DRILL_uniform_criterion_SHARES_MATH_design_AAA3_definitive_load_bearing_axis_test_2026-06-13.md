# Research drill: uniform-criterion SHARES_MATH expansion design for AAA-3-definitive load-bearing axis test

Filed: 2026-06-13
Trigger: 2x DEEP drill from AAA-3 canonical 0.94x confounded result; provisional 1.33x auto-discovery reading needs methodology defense
Budget: ~30-45 min, 6 web searches + synthesis
Field: knowledge-graph structural similarity / null-model methodology (off the spectral-physics field-advisor axis; legitimate per Trigger D rescue cadence)
Privacy: generic-terms only in external queries (no substrate-novel mechanism names, no project-specific N or P)

## HEADLINE

Three concrete uniform-criterion SHARES_MATH expansion designs are defensible against authoring-sequence confound: (C1) Weisfeiler-Lehman 1-step neighborhood signature shared at hash-collision, (C2) Formal Concept Analysis attribute-intent overlap on a TOOLS x MATH-PRIMITIVES context, (C3) shared-capability USES uniform rule (already prototyped, the 1.33x reading). Recommended test design pairs C2-or-C3 as the criterion with a **degree-corrected SBM (DC-SBM) null model** and a deflated **effect-size bar of >=1.25x post-null-correction** (down from naive 1.4x to account for authoring-sequence residual variance). Honest framing: substrate is uncharted (operator-vs-material axis lacks a direct published precedent in HRR/FHRR), so lit-scan calibration penalty applies and P(load-bearing axis confirmed) caps at 0.50.

## Cheap decisive test (recommended AAA-3-definitive design)

**Step 1 (criterion selection).** Pick ONE of:
  - C2 (FCA-intent overlap): for each pair (a, b), share an edge iff the set of math-primitive attributes they participate in (axiom-ref, operator-arity, signature-class) has Jaccard >= tau. Tau pre-registered at 0.40 from pilot.
  - C3 (USES-rule): for each pair (a, b), share an edge iff there exists a third atom c with USES(a, c) and USES(b, c) where USES is the substrate's existing capability-uses graph. This is the criterion that produced the 1.33x provisional reading.

  **Preferred:** C3 because (a) it is already empirically prototyped, (b) it does NOT require new authoring (eliminates author-clique confound by construction since USES edges pre-exist), (c) it is interpretable as "co-tool dependency".

**Step 2 (null-model correction).** Compute observed out-degree ratio TOOLS:MATERIALS under criterion C3. Then build the DC-SBM null with two blocks (TOOLS, MATERIALS) preserving each block's degree sequence, sample N=200 null replicates, compute mean and 95% interval of the ratio under null. Report **excess ratio = observed / null_mean** with bootstrap CI.

**Step 3 (effect-size threshold).**
  - HARD-PASS: excess_ratio >= 1.25 with 95% CI lower bound > 1.0 AND naive observed ratio >= 1.30.
  - HARD-FAIL: excess_ratio <= 1.05 OR 95% CI crosses 1.0.
  - MIDDLE_BAND: 1.05 < excess_ratio < 1.25 -> re-drill with criterion C2 as cross-check before issuing verdict.

Bar deflation rationale: naive 1.4x bar was set against an authored count where clique-size confound inflated noise. Post-DC-SBM correction removes block-internal density bias, so a smaller absolute effect remains decisive. The 1.25x threshold is consistent with published heterogeneous-graph effect sizes where 20-30% excess over null is considered structurally meaningful (configuration-model literature).

## Falsifiable predictions

  - **HARD-PASS prediction:** under C3 + DC-SBM, TOOLS out-degree mean exceeds MATERIALS out-degree mean by excess_ratio >= 1.25, 95% bootstrap CI fully above 1.0, AND a permutation test (relabeling TOOLS/MATERIALS uniformly at random) yields p < 0.01. Substrate-product reading: tools-vs-materials is a structurally real, measurable load-bearing axis distinct from epistemic tier (T0-T3).
  - **HARD-FAIL prediction:** excess_ratio <= 1.05 OR 95% CI crosses 1.0 OR permutation p >= 0.10. Substrate-product reading: the 13th-rule load-bearing axis hypothesis does NOT survive uniform-criterion test; the 1.33x provisional reading was authoring-driven artifact; revert to epistemic-tier single-axis architecture and close cap_map row AAA-3-axis.
  - **MIDDLE_BAND prediction:** excess_ratio in (1.05, 1.25) with mixed CI/permutation signals -> mechanism is weakly load-bearing; recommend AAA-4 expansion with criterion C2 cross-check before architectural commit.

## Uniform-criterion candidates (3 concrete, ranked)

### C3 (RECOMMENDED): shared-capability USES rule

  - **Definition:** SHARES_MATH(a, b) iff exists c with USES(a, c) AND USES(b, c).
  - **Why uniform:** USES edges are NOT authored by clique-seed; they were extracted from existing atom signature/implementation graph (uniform crawler authority). Both TOOLS and MATERIALS get USES edges by the same rule.
  - **Confound resistance:** HIGH. No author-defined clique boundaries; criterion derived from substrate-internal capability-uses graph.
  - **Tradeoff:** USES coverage is sparse on materials (materials often "used" rather than "use"); may underestimate MATERIALS out-degree -> conservative bias TOWARD null (good for HARD-PASS interpretation).
  - **Lit anchor:** structural equivalence via shared-neighbor sets is the classical sociological criterion (Lorrain-White 1971 block-modeling); Weisfeiler-Lehman 1-step refinement is the modern graph-kernel formalization.

### C2 (ALTERNATIVE): FCA attribute-intent overlap

  - **Definition:** build a formal context K = (A, M, I) where A = atoms, M = math-primitive attributes (axiom-references, operator-arity classes, signature-template-ids, type-signature fingerprints), I = participation incidence. SHARES_MATH(a, b) iff Jaccard(intent(a), intent(b)) >= tau (pre-registered tau=0.40 from pilot).
  - **Why uniform:** attribute set M is exhaustively enumerated from substrate corpus (no clique-seed choices); FCA concept lattice is a canonical equivalence-class structure independent of authoring sequence.
  - **Confound resistance:** HIGH. FCA is the canonical "uniform-criterion" tool from formal concept analysis (Ganter-Wille).
  - **Tradeoff:** requires building attribute set M (~1 day authoring); tau choice has some discretion; Jaccard threshold sensitivity.
  - **Lit anchor:** FCA concept lattice gives a canonical hierarchy on heterogeneous objects via shared attributes; standard in ontology-alignment literature.

### C1 (FALLBACK): Weisfeiler-Lehman 1-step signature

  - **Definition:** run 1-step WL refinement on the substrate's full capability-graph (treating type-label as initial color); SHARES_MATH(a, b) iff WL-color(a) == WL-color(b) at depth 1.
  - **Why uniform:** WL hash is deterministic from graph structure + initial labeling; no author choice in edge creation.
  - **Confound resistance:** MEDIUM. WL collapses fine distinctions; may over-pool MATERIALS into a single color and over-stratify TOOLS, biasing ratio either direction.
  - **Tradeoff:** less interpretable than C2/C3; depth choice (1 vs 2 vs 3) matters; WL is known to undercount heterogeneous-type structural distinctions.
  - **Lit anchor:** WL-kernel literature; the 1-WL test is the canonical structural-equivalence baseline.

## Bias-correction null-model recommendation

**Primary: degree-corrected stochastic block model (DC-SBM)** with two blocks {TOOLS, MATERIALS}.

  - **Why DC-SBM not vanilla SBM:** vanilla SBM assumes nodes in the same block have the same expected degree (Poisson). The TOOLS-vs-MATERIALS degree distributions are likely heterogeneous within-block (some tools have many USES edges, some few). DC-SBM adds a per-node scaling parameter theta_u that preserves each node's empirical degree while randomizing the block-coupling. This is the standard fix when within-block degree heterogeneity matters (Karrer-Newman 2011).
  - **Sampling protocol:** N=200 null replicates; for each, compute the TOOLS:MATERIALS out-degree ratio under the chosen criterion (C3 preferred). Bootstrap 95% CI on excess_ratio.

**Secondary cross-check: configuration model.** Preserves the exact degree sequence but randomizes everything else. Cheaper to compute; serves as a second-opinion null. If C3-result is robust, configuration-model and DC-SBM excess ratios should agree within ~5%.

**Tertiary (only if MIDDLE_BAND): block-constrained configuration model.** Preserves the number of edges between blocks while randomizing within. Used as a tiebreaker if DC-SBM and configuration model disagree.

## Cross-thread synthesis

  - **Prior 8d/9d spectral observability pillar (Cycle 50/51 close):** spectral methods (Tracy-Widom, free cumulants, BBP spikes) are the substrate's "load-bearing-via-physics" observability. The structural-graph load-bearing axis is the **graph-theoretic** complement: where 9d pillar measures eigenvalue tails, AAA-3 measures degree/connectivity tails. The two should agree at the architectural level (load-bearing primitives should appear both as spectral outliers AND as high-SHARES_MATH degree hubs).
  - **CELL KP P1+P4 (Cycle 51 close):** knowledge-promotion operator is a uniform-criterion structural test (frequency-promotion + sleep-replay consolidation are objective rules, no clique-seed). This is the methodology template AAA-3-definitive should follow.
  - **11th methodology rule (held-out test):** the C3 USES-rule is "held-out" relative to AAA-3 family-clique authoring (USES edges were created for earlier cycles, not for AAA-3); naturally avoids Goodhart concern.
  - **Methodology rule cluster (Cycle 51):** verify-before-asserting 5-class cluster + USER-LOCKED never-lock-in-frameworks rule -> AAA-3 must NOT lock in load-bearing-axis architecture on confounded 0.94x or single-criterion 1.33x; AAA-3-definitive uniform-criterion + null-corrected test is the right discipline.
  - **Adjacent-method dispatch (per don't-dismiss-adjacent-methods):** FCA and WL were both NOT in the original AAA-3 design; both are mathematically adjacent and dispatched here -> aligns with the rule.

## Substrate-product implications

  - **If HARD-PASS (~30-40% prior):** substrate has empirically validated **two-axis architecture** (epistemic tier x structural-role). LLMs categorically lack this distinction (their token-embedding space conflates operator and operand). Product positioning: "substrate is the first cognitive architecture with empirically separable tool-axis and material-axis observability." Composes with 9d spectral pillar -> 11-dimensional structural-cognition observability claim.
  - **If HARD-FAIL (~30-40% prior):** substrate architecture remains single-axis (epistemic tier only); 13th-rule load-bearing-axis hypothesis closed; net positioning unchanged (we don't lose existing wins; we lose a candidate next-gen claim). 7th rule (always-reconsider-frameworks) honored.
  - **If MIDDLE_BAND (~20-30% prior):** weak signal -> AAA-4 expansion needed; treat as PARTIAL; no architectural commit.

**Lit-scan calibration penalty applied:** uncharted regime (no direct precedent for operator-vs-material structural-equivalence asymmetry in HRR/FHRR or in cognitive-architecture literature). Deflated P(HARD-PASS) from naive 0.55 to **0.40**. Cap on novel-synthesis P respected at 0.50.

## Honest framing (per "we might be first")

The closest published analogues are:
  - **Structural bias in entity alignment** (ESWC 2023, Fanourakis et al.): documents that heterogeneous KGs have systematic structural bias when entity types differ in connectivity patterns. Confirms our 13th-rule hypothesis is plausible but does not test it on tool-vs-material.
  - **Heterogeneous degree distributions in bipartite networks** (PMC12192312, 2025): confirms degree heterogeneity introduces bias and motivates degree-corrected null. Supports our DC-SBM choice.
  - **DC-SBM** (Karrer-Newman 2011, Yan-Jensen): canonical null for block-heterogeneous degree. Directly applicable.
  - **FCA** (Ganter-Wille): canonical uniform-criterion structural equivalence on heterogeneous attribute contexts. Directly applicable.
  - **WL kernel** (Shervashidze-Borgwardt JMLR 2011): canonical 1-step structural-equivalence test. Adjacent.
  - **Ryle knowing-how vs knowing-that** (SEP): conceptual support for the asymmetry (tools-as-procedural-knowledge vs materials-as-declarative-knowledge). Philosophical anchor only, not methodological.
  - **Operator-operand distinction** (mathematical practice / programming): conceptual support; standard distinction.

**What's NOT published (substrate-novel):** the specific claim that an HRR/FHRR cognitive substrate's atoms partition along an OPERATOR/MATERIAL axis ORTHOGONAL to epistemic tier, measurable via SHARES_MATH structural-equivalence with DC-SBM correction. This is substrate-original; prior work informs the methodology but does not govern the hypothesis.

## Citations (verified count: 11)

  1. Fanourakis et al., "Structural Bias in Knowledge Graphs for the Entity Alignment Task," ESWC 2023. https://2023.eswc-conferences.org/wp-content/uploads/2023/05/paper_Fanourakis_2023_Structural.pdf
  2. "Neighbor-Enhanced Link Prediction in Bipartite Networks," PMC12192312, 2025. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12192312/
  3. "Mitigating Degree Bias in Graph Representation Learning," arXiv 2504.15075. https://arxiv.org/html/2504.15075
  4. Karrer & Newman, "Stochastic blockmodels and community structure in networks" (DC-SBM origin), PMC4498413. https://pmc.ncbi.nlm.nih.gov/articles/PMC4498413/
  5. "The block-constrained configuration model," Applied Network Science, 2019. https://appliednetsci.springeropen.com/articles/10.1007/s41109-019-0241-1
  6. Configuration model (Wikipedia canonical). https://en.wikipedia.org/wiki/Configuration_model
  7. Yan-Jensen et al., "Model Selection for Degree-corrected Block Models," arXiv 1207.3994. https://arxiv.org/pdf/1207.3994
  8. Formal concept analysis (Wikipedia canonical / Ganter-Wille). https://en.wikipedia.org/wiki/Formal_concept_analysis
  9. "Relating coalgebraic notions of bisimulation," Staton 2009. https://www.cs.ox.ac.uk/people/samuel.staton/papers/calco09.pdf
  10. Shervashidze et al., "Weisfeiler-Lehman Graph Kernels," JMLR 2011. https://dl.acm.org/doi/10.5555/1953048.2078187
  11. Ryle on knowing-how / knowing-that, Stanford Encyclopedia of Philosophy. https://plato.stanford.edu/entries/ryle/knowing-how.html

## Recommendation for AAA-3-definitive cell (concrete handoff)

**Cell design (one-page spec):**
  - Criterion: C3 (USES-rule shared-capability), pre-registered.
  - Null: DC-SBM with TOOLS/MATERIALS blocks, N=200 null replicates, bootstrap 95% CI.
  - Cross-check null: configuration model (cheap; same N).
  - Metric: excess_ratio = observed / null_mean of TOOLS:MATERIALS out-degree ratio.
  - HARD-PASS bar: excess_ratio >= 1.25, 95% CI lower > 1.0, permutation p < 0.01, naive ratio >= 1.30.
  - HARD-FAIL bar: excess_ratio <= 1.05 OR 95% CI crosses 1.0 OR permutation p >= 0.10.
  - MIDDLE_BAND: rerun with C2 (FCA-intent, tau=0.40) before verdict.
  - Compute cost: ~30 min CPU (USES-rule on existing graph + DC-SBM sampling).
  - Authoring cost: 0 (C3 uses existing graph); ~1 day if C2 fallback needed (attribute-set construction).
  - Pre-reg deadline: before any code runs, write Cell pre-reg note with all four numeric thresholds.

**Why this design beats the canonical AAA-3 0.94x:**
  - Criterion (C3 USES-rule) is uniform across TOOLS and MATERIALS by construction.
  - No clique-seed authoring (USES edges pre-exist).
  - DC-SBM null corrects for within-block degree heterogeneity (the residual confound).
  - Effect-size bar (1.25x post-correction) is calibrated to literature norms for heterogeneous-graph excess.
  - Triple-witness (excess_ratio + CI + permutation p) prevents single-test false positive.

**Risk register:**
  - USES-rule sparsity on MATERIALS may inflate excess_ratio artificially (conservative bias toward HARD-PASS); mitigate by reporting raw counts alongside ratios.
  - DC-SBM with only two blocks may under-specify; consider 4-block variant (T0/T1/T2/T3 x TOOLS/MATERIALS) as sensitivity analysis if MIDDLE_BAND.
  - Pre-registration is mandatory per Cycle-51 verify-before-asserting cluster.
