# Consolidation -> inference-capable structure: the implementable algorithm (2026-07-14)

**Purpose.** Today we established (brain + glass-box VSA prototype) that genuine zero-shot INFERENCE needs codes carrying SHARED/CORRELATED structure, and that the brain MANUFACTURES that structure from experience via replay + consolidation (it is not present at encoding). This doc turns that into an implementable, glass-box VSA algorithm. Synthesized by director from two lit sub-scans (TEM/grid-code learning; CLS/Hebbian-replay learning rule) after the parent drill returned early. Precedented-vs-novel flagged; nothing certified.

## The one-paragraph algorithm
Manufacture structured codes by SLOW, small-step updates over INTERLEAVED REPLAY of (concept, relation-neighborhood) samples, while keeping the fast episodic store ORTHOGONALIZED (anti-smear). Slow interleaved updating provably extracts SHARED structure before idiosyncratic detail (Saxe theorem); the relation operators are SHARED transforms and the structure code is kept from binding raw content (TEM bottleneck), so the result transfers zero-shot. Prove it works by showing held-out-relation inference lift GROWS with consolidation passes (logarithmic), collapsing to zero under a correlation-destroying shuffle.

## Primitives -> VSA operations (each: brain mechanism / computational job / VSA op / what to measure / have-vs-missing)

### P1. Interleaved slow update  [CORE; impact/effort = HIGH/LOW]
- **Brain:** CLS cortical rule -- backprop at SMALL learning rate over INTERLEAVED old+new (McClelland/McNaughton/O'Reilly 1995; consistency-accelerates-integration, McClelland/McNaughton/Lampinen 2020).
- **Job (PROVEN, Saxe/McClelland/Ganguli 2019 PNAS, deep LINEAR nets):** gradient descent learns structural mode alpha on timescale t ~ (tau/s_alpha)*ln(s_alpha/eps). High-singular-value = SHARED-across-items structure -> learned FAST; item-idiosyncratic detail = small s_alpha -> learned LAST. So slow interleaved learning is MATHEMATICALLY FORCED to track population (shared) structure first. Staging vanishes in shallow nets (depth-dependent, falsifiable).
- **VSA op:** refit the additive-map learned codes (hdlab/additive_map.py) via SLOW SGD over INTERLEAVED replay batches of (entity, relation-context) samples; small LR, many passes. NOT one-shot, NOT sequential (sequential = catastrophic interference, Ratcliff 1990 / French 1999 -- overlapping codes get overwritten).
- **Measure:** structure-before-content staging (coarse/superordinate relations learned before fine); held-out inference lift vs #passes.
- **Have:** additive-map SGD fit. **Missing:** interleaved-replay scheduling + the staging measurement. (Cheapest high-value move -- a training-schedule change on an existing component.)

### P2. Structure-content bottleneck  [makes codes REUSABLE; impact/effort = HIGH/MEDIUM]
- **Brain:** TEM (Whittington et al. 2020 Cell). g (grid/structure) produced by recurrent net with ACTION/RELATION-conditioned SHARED transition matrices; g NEVER sees sensory content, only transitions -> forced to encode abstract relational position. p (place/content) = conjunction g (x) x in a FAST HEBBIAN memory. Parameter-shared transition weights reused across ALL environments; only the fast memory is environment-specific.
- **Job:** because every environment shares relational structure but has arbitrary content, GD has no incentive to fold content into g -> g generalizes zero-shot ("first/second visit" correct inference on NEW graphs). This is the mechanism of relational generalization.
- **VSA op:** the relation must be a SHARED operator applied regardless of entity (we HAVE this: additive-map relation = shared transform). CRUX ADDITION: update the entity/structure code ONLY through relation-TRANSITION consistency, never bind it directly to raw content; put content in a SEPARATE fast conjunctive store (= our sharded store). Enforce the g-sees-only-structure bottleneck.
- **Measure:** zero-shot inference on a held-out relational graph of the same structure but new entities; ablate the bottleneck (let content leak into structure) -> generalization should drop.
- **Have:** shared relation operators. **Partial/missing:** explicit bottleneck (our codes may leak content into structure).

### P3. Hebbian/PCA consolidation  [most GLASS-BOX route; impact/effort = HIGH/MEDIUM]
- **Brain:** local Hebbian plasticity as the biologically-plausible substitute for backprop; Oja's rule (1982) provably converges to top eigenvector of input covariance; Sanger/GHA (1989) extracts first k PCs in order -- streaming PCA with LOCAL updates, no teaching signal. (Grid-cell version: Dordek 2016 non-negative Hebbian PCA -> hexagonal code; Sorscher 2019/2022 -- hexagonal grid is the OPTIMAL constrained-coding solution regardless of algorithm.)
- **Job:** streaming PCA over replayed samples extracts the SHARED structural components; episode-specific noise averages out ~1/N over N replay passes (model x_i = s + eps_i; coherent s accumulates, uncorrelated eps washes out). [NOTE: "replay = streaming Hebbian PCA = shared-structure extraction" is a well-motivated SYNTHESIS chaining two established literatures, not a single named theorem -- flagged.]
- **VSA op:** run an Oja/Sanger update over replayed (relation-context) hypervectors to build structured entity/value codes as top-PC combinations of the co-occurrence covariance. FULLY INSPECTABLE (each component is an interpretable eigen-direction) = aligns with our glass-box value proposition better than opaque SGD.
- **Measure:** do the extracted PCs correspond to the semantic buckets? Inference lift vs #passes; compare glass-box Oja codes vs SGD additive-map codes.
- **Have:** nothing yet. **Missing:** an Oja/Sanger consolidation pass. Strong candidate cell -- the most glass-box way to manufacture structure.

### P4. Anti-smearing / pattern separation  [the counter-force; ALREADY BANKED as our own finding]
- **Brain:** dentate-gyrus sparse conjunctive coding orthogonalizes similar inputs; BCM (1982) sliding-threshold rule sparsifies/selects. This is what stops consolidation from COLLAPSING distinct items. CLS keeps overlap (needed for structure) but avoids interference via tiny increments + interleaving + a separate orthogonalized fast store.
- **Job:** decouple the two code systems -- near-orthogonal STORE codes (capacity) vs correlated SEMANTIC codes (generalization).
- **This IS our correlation-HURTS-capacity finding, now BRAIN-CONFIRMED as the CLS architecture** [[reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08]]. We already separate sharded near-orthogonal store from retrieval semantics.
- **Have:** the finding + sharded storage. Insight: it is the SAME mechanism -- don't fight it, exploit it (fast store orthogonal, slow store overlapping).

### P5. Prioritized replay  [targets OUR bottleneck; impact/effort = MEDIUM/MEDIUM]
- **Brain:** sharp-wave-ripple replay is reward/novelty/surprise-prioritized; SWR disruption impairs learning, prolonging ripples improves it (Science 2019/2024); reverse replay refines grid periodicity (bioRxiv 2023) -- replay CONSOLIDATES the structural code beyond online experience.
- **Job:** preferentially replay surprising/novel/boundary experiences -> faster structure extraction where it is most needed.
- **VSA op:** weight replay sampling toward the COLD/d1 SPARSE TAIL + high-surprise edges (the tail is exactly where our substrate is weak). 
- **Measure:** tail-inference lift with prioritized vs uniform replay.
- **Have:** nothing. **Missing.** Natural follow-on once P1/P3 loop exists.

## The proof-of-life measurement (fair + falsifiable)
Held-out-relation inference lift as a function of consolidation passes: predict a LOGARITHMIC rise (Saxe law), SATURATING. Controls: (1) SHUFFLE (destroy cross-relation correlation) -> lift must NOT grow; (2) info-ceiling (oracle from latent type) -> report headroom; (3) structure-before-content staging visible. Human analog exists (Ellenbogen 2007 PNAS: transitive-inference accuracy on distant pairs scales with SLEEP, not wake).

## Dose / sample-efficiency caveat (developmental)
Grid-code reusability needs a MINIMUM DOSE of STRUCTURED (geometrically regular) experience during a critical window -- NOT many distinct environments (PNAS 2023 deprivation study: 6.5% grid cells after featureless rearing vs 14-15% control; full recovery after ~7 days structured exposure; ANY cornered environment suffices). **Maps to our program:** what matters is that the foundation carries genuine RELATIONAL STRUCTURE, not raw volume -- reinforces "dense structured core > max size." TEM's env-count-for-generalization is a quantitative GAP in the literature (not reported).

## Convergence with our existing program (why this is not a detour)
- P1+P3 = a concrete BUILD for the reasoning-mechanism half: manufacture the structured codes the decisive experiment is testing for.
- P2 = TEM VALIDATES the additive-map architecture (shared relation operators + structure/content split) and names the missing piece (the bottleneck).
- P4 = our correlation-hurts-capacity finding IS the CLS anti-smear, brain-confirmed.
- P5 = aims the loop at the sparse tail (our confirmed bottleneck).
- The whole loop = the consolidation/sleep/confidence lifecycle we had sketched for grounding-the-tail, now with an implementable rule and a fair dose-response test.

## Ranked next moves (impact-per-effort)
1. **P1 interleaved-replay refit of additive-map + structure-before-content staging measurement** (HIGH/LOW) -- schedule change on existing code; directly feeds the decisive experiment's "structured codes" arm.
2. **P3 Oja/Sanger glass-box consolidation cell** (HIGH/MEDIUM) -- most-glass-box structure manufacture; compare to SGD codes.
3. **P2 enforce structure-content bottleneck** (HIGH/MEDIUM) -- the reusability lever; ablation-testable.
4. **P5 prioritized (tail-weighted) replay** (MEDIUM) -- once the loop exists.
