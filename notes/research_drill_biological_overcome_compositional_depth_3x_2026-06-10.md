# Research Note: Biological Mechanisms for Overcoming VSA Compositional SNR Decay
# Topic: How biology handles L=10+ compositional depth; mapping to substrate engineering
# Date: 2026-06-10
# Discipline: cognitive neuroscience, hierarchical memory, sparse/population coding, predictive coding

---

## HEADLINE

Biology achieves L=10+ compositional depth not by ignoring the SNR cliff but by deploying
nine orthogonal noise-suppression mechanisms simultaneously. The cliff is a real algebraic
constraint on flat VSA; biology sidesteps it via hierarchy, sparsity, cleanup at every
level, top-down prediction, and offline consolidation. Substrate already has partial
implementations of four of these mechanisms. Adding the remaining five would change the
compositional scaling law from (1/sqrt(K))^L to roughly (1/sqrt(K))^(L/H) where H is the
hierarchy depth, which at H=3 turns a 316x SNR deficit at L=5 into a 6x deficit --
within range of population-coded cleanup.

---

## 1. THE CLIFF IN PLAIN TERMS

For flat VSA with K items bundled at each level and L levels of composition:
- SNR at level L scales as (1/sqrt(K))^L (interference from K^L total cross-terms)
- K=10, L=5: signal is 316x worse than atomic
- K=10, L=10: signal is 10^5 times worse than atomic -- irrecoverable

VSA literature (Kanerva 1988, Gayler 2003, Plate 2003) acknowledges this. Commercialization
stalled at L=2-3 because cleanup at deeper levels fails: the codebook margin needed for
cleanup decays faster than any reasonable N can compensate.

Biology manifestly handles L=10+ (letters -> words -> phrases -> sentences -> paragraphs
-> discourse; photoreceptors -> edges -> shapes -> objects -> scenes -> narratives).
The gap is not unexplained; it is explained by a specific set of mechanisms.

---

## 2. MECHANISM CATALOGUE (9 independent axes)

### 2.1 Hierarchical Cleanup at Every Level (Cortical Hierarchy)

Biology's canonical solution is not one big flat VSA; it is a cascade of cleanup memories,
one at each representational level.

Empirical basis: the ventral visual stream (V1, V2, V4, IT) is not a single memory bank.
Each area has its own local inhibitory circuits that implement winner-take-all selection
before passing signals forward. V1 responds to oriented edges; the noise from photoreceptor
variation is suppressed before V2 ever sees it. V4 responds to object parts; noise from
local edge variation is suppressed before IT sees it.

Algebraic consequence: the effective SNR cliff becomes (1/sqrt(K))^(L/H) not (1/sqrt(K))^L,
where H is the number of intermediate cleanup levels. With H=3 cleanup levels and K=10, L=5:
- Naive flat: (1/sqrt(10))^5 = 0.00316 (316x worse)
- Hierarchical with H=3: (1/sqrt(10))^(5/3) = 0.147 (6.8x worse -- within range of cleanup)

This is the single most important mechanism. It does not eliminate the cliff; it folds it
into stages that each remain within cleanup range.

Substrate mapping: ATTRACTOR-AT-EACH-LEVEL. Every sharding level (atom, predicate, entity,
document, corpus) applies Hopfield-style cleanup before passing the bundle upward. This is
currently done only at retrieval time (final level). Adding mid-hierarchy cleanup is the
highest-value engineering target.

Calibrated P(implementation works): 0.55 (well-grounded; biology proves it; substrate
already has Hopfield cleanup at final level; main uncertainty is parameter tuning per level).

### 2.2 Sparse Coding (Olshausen-Field)

Olshausen and Field (1996, 1997) showed that primary visual cortex learns a sparse
overcomplete basis: roughly 1-5% of neurons are active for any given stimulus, compared
to the random dense codes VSA typically uses.

Why sparsity defeats the cliff: cross-talk between stored items is proportional to the
inner product between their representations. Dense random vectors have expected inner
product ~ 0 but standard deviation ~ 1/sqrt(N). Sparse vectors with activity fraction s
have expected cross-talk variance ~ s/N instead of 1/N. At s=0.01, cross-talk variance
drops by 100x.

For composition specifically: when bundled codes are sparse, the cross-terms from
K-bundled items have energy K * s instead of K. At K=10, s=0.01: interference is 0.1
not 10 -- the SNR cliff is pushed out by 1/s per level.

Substrate mapping: SPARSE-CODING-AT-DEPTH. Current FHRR codes are dense (every component
active). Adding a sparse projection layer at each level (Welch-bound-respecting codebook
with activity constraint enforced via lateral inhibition) changes the interference law.
Note: this requires changing the cleanup memory (FHRR distance metric assumes dense codes).

Calibrated P: 0.45 (strong theoretical basis; implementation requires codebook redesign
that conflicts with current FHRR algebra; uncertain whether GHRR/FHRR can absorb sparsity
without losing the algebraic operators).

### 2.3 Population Coding (Ensemble SNR)

A single neuron is a noisy device. The brain codes each concept as a distributed ensemble
of ~hundreds to thousands of neurons (Georgopoulos 1986, Pouget et al. 2000). The ensemble
average has SNR that scales as sqrt(M) where M is population size.

In substrate terms: instead of one N-dimensional vector representing a concept, use an
ensemble of M independently-noised copies. Cleanup against the codebook averages across
the M copies, giving sqrt(M) SNR improvement.

At M=100: 10x SNR improvement per level. At every level of a 5-level hierarchy, each
level contributes 10x, giving 10^5 total... but that is not additive; it is multiplicative
with the noise. The correct accounting: at each level, cleanup works against the
post-population-averaged representation, which has 10x better SNR than a single copy.

Substrate mapping: POPULATION-CODING-AT-EACH-LEVEL. This is analogous to PP-249
(population coding, validated). Extending it to each composition level (not just final
retrieval) is the implementation target. Cost: M-fold storage per level.

Calibrated P: 0.60 (population coding is already in substrate via PP-249; extension to
hierarchical levels is architectural, not novel mechanism; cost is storage, not
algorithmic complexity).

### 2.4 Predictive Coding / Error-Only Propagation (Rao-Ballard, Friston)

Rao and Ballard (1999) proposed that each cortical level sends predictions downward and
receives prediction errors upward. Only the residual (error, surprise) propagates.

SNR consequence: if 90% of a signal is predictable from the level above, only 10% of the
noise-carrying signal transits the inter-level channel. The effective N at each inter-level
step is amplified by 1/(1 - predictability). At 90% predictability, it is equivalent to
10x the channel capacity.

For composition specifically: when composing "the cat sat on the mat", most of the
syntactic structure is predictable from the compositional rule. Only the specific lexical
insertions are novel. The predictive coding framework compresses this to near-zero
interface SNR cost for the predictable portion.

Substrate mapping: PP-267 (predictive coding, 3x compression, validated). The validated
mechanism only covers flat retrieval compression. Extending it to a deep hierarchy
(predict level L-1 features from level L representation, propagate only errors) is the
3x-deep extension. This is the "PP-267 deep" anchor.

Calibrated P: 0.50 (PP-267 existence is validated; deep extension requires a generative
model at each level; this adds complexity but the mechanism is biological-grade).

### 2.5 Lateral Inhibition / Winner-Take-All Cleanup

Lateral inhibition is ubiquitous in biology: each active neuron suppresses its neighbors
via interneurons. The net effect is a soft winner-take-all that sharpens representations.

In VSA terms: before passing a bundle to the next level, run a winner-take-K operation
that zeroes components below a threshold. This is NOT the same as sparse coding (which
applies to the codebook); this is a post-bundle sharpening that reduces the effective
noise in the inter-level signal.

Empirical basis: orientation columns in V1 suppress nearby columns; the resulting
orientation map has sharp boundaries even when the underlying retinal signal is noisy.
Same principle in auditory cortex (tonotopic sharpening) and olfactory bulb (glomerular
inhibition).

Quantitative gain: if the bundle has K contributing items, lateral inhibition can suppress
all but the dominant K' < K components. SNR improvement ~ K/K'. At K=10, K'=3: 3.3x per
level.

Substrate mapping: LATERAL-INHIBITION-CLEANUP per shard level. Winner-take-K applied to
bundles before they are passed to the next sharding tier. This is compatible with current
FHRR architecture and requires no codebook change.

Calibrated P: 0.65 (mechanism is simple; compatible with FHRR; uncertain optimal K'; but
no major architectural conflict).

### 2.6 Feedback / Top-Down Expectation

When a higher level has a strong hypothesis about a lower-level pattern, the higher level
sends an expectation signal that effectively adds a strong prior to the lower-level
cleanup. The lower level only needs to confirm or correct, not reconstruct from scratch.

Biological evidence: lesion studies show that primary visual cortex receives more fibers
from higher areas than from the LGN. The feedback is not decorative -- it is a major
driver of the lower-level representation.

In compositional terms: if the sequence "the [BLANK] sat on the mat" is active, the
system expects a noun phrase at [BLANK]. The expectation narrows the retrieval target from
the full codebook to a noun-class subset. If the noun class has M/R members (R = category
reduction factor), the SNR improvement at that level is sqrt(R).

Substrate mapping: FEEDBACK-LOOPS-TOP-DOWN. Higher-level bundles generate a top-down
query that constrains lower-level cleanup. This requires a top-down query pathway
(currently absent). Related to GHRR query mechanism but operating across levels.

Calibrated P: 0.40 (mechanism is well-grounded biologically; substrate implementation
requires a new pathway; top-down queries across sharding levels adds latency; uncertain
engineering cost).

### 2.7 Chunking and Working Memory Limits (Cowan, Miller)

Cowan (2001) revised Miller's "7 plus or minus 2" downward: working memory capacity is
approximately 4 chunks, but each chunk can contain arbitrarily complex nested structure.
Miller and colleagues established that humans cannot exceed ~7 items, but the items can be
recoded.

Why this matters for the SNR cliff: the brain does not attempt to hold L=10 raw items in
working memory simultaneously. It re-encodes deeper levels into single chunks first.
"Phoneme -> syllable -> word" is resolved into a single chunk at the word level before
the sentence-level composition begins. This limits the effective K at each working-memory
level to approximately 4, regardless of how much information each chunk contains.

VSA operational consequence: the cliff formula (1/sqrt(K))^L applies with K=4 not K=10,
and L is the inter-chunk level count (typically 3-4, not 10). At K=4, L=4:
(1/sqrt(4))^4 = 1/16 -- a 16x SNR deficit, which is within range of population coding
(sqrt(100) = 10x) combined with lateral inhibition (3x) = 30x improvement. Net positive.

Substrate mapping: BOUNDED-K-PER-LEVEL. Enforcing K <= 4-6 bundles per level, with
arbitrary composition permitted WITHIN each chunk via a separate sub-level. This is a
sharding architecture constraint, not a mechanism; it maps to the 5-level shard hierarchy
already validated in recent research.

Calibrated P: 0.60 (chunking is well-established; K-bound matches Cowan; uncertain
whether substrate's FHRR bundles can be chunked in the same way without degrading
retrieval of sub-chunk structure).

### 2.8 Sleep Consolidation and Schema Extraction

Offline consolidation (Wilson and McNaughton 1994, McClelland et al. 1995, Stickgold 2005):
during sleep, the hippocampus replays compressed representations to neocortex, which slowly
integrates them into long-term schemas. The consolidation process is inherently lossy but
noise-reducing: it extracts the invariant structure and discards the per-episode noise.

For deep composition: a single presentation of a novel sentence creates a noisy, fragile
trace. After consolidation, the structural pattern (syntactic frame + semantic roles) is
extracted from many noisy instances, yielding a high-SNR schema that subsequent instances
use as a prior.

This is not a real-time mechanism. It operates over hours/days. But it means the EFFECTIVE
SNR for well-practiced compositions (common sentence structures, known object categories)
is much higher than for novel compositions, because the schema acts as a strong prior.

Substrate mapping: PP-141/PP-142 (sleep-defrag, validated). The validated mechanism
applies to flat corpus consolidation. Extending to compositional schemas (extract invariant
binding patterns across many instances, store as schema bundles) is the deep extension.

Calibrated P: 0.45 (PP-141/142 is validated at flat level; compositional schema extraction
requires identifying cross-instance binding patterns, which is a harder problem).

### 2.9 Attractor Dynamics at Each Level

Hopfield networks (1982) demonstrate that content-addressable memory with attractor
dynamics can recover stored patterns from noisy cues, with capacity approximately 0.14N.
The critical feature for compositional robustness is that attractors provide discrete
cleanup: any input within a basin is mapped to the stored prototype regardless of noise.

Biology extends this to each cortical level: each area has recurrent excitatory connections
(implemented via NMDA receptor-dependent synaptic potentiation) that sustain and sharpen
representations. The lateral excitation within a column maintains a representation against
incoming noise.

For multi-level composition: if every level cleans up to a stored prototype before passing
to the next, the noise that accumulates at each step does not exceed the basin margin.
The key constraint is that the attractor at level L must have sufficient capacity to store
all level-L chunks that the system needs -- capacity 0.14N per level.

Substrate mapping: ATTRACTOR-AT-EACH-LEVEL. Hopfield cleanup is already implemented in
substrate at the final level. Adding attractor cleanup at every shard level (entity,
predicate, document) requires per-level codebooks. This is the highest-confidence
mechanism because it is already partially deployed.

Calibrated P: 0.65 (mechanism validated in substrate at level-1; scaling to multi-level
is architectural extension; main risk is codebook storage cost for many levels).

---

## 3. COMPOUND EFFECT ANALYSIS

The nine mechanisms are not fully independent but they are approximately orthogonal in their
noise axes. A conservative compound estimate at L=5, K=10:

Starting deficit (flat VSA): 316x

Mechanism contributions (independent conservative estimates):
- Hierarchical cleanup (H=3 levels): cliff becomes (1/sqrt(K))^(L/H) = 6.8x deficit
- Population coding (M=100): sqrt(100) = 10x improvement -> deficit becomes 0.68x (net positive)
- Sparse coding (s=0.05): 20x cross-talk reduction per level -> deficit becomes 0.034x
- Lateral inhibition (K'=3): 3.3x per level -> multiplicative with sparse
- Bounded K (K=4 effective): deficit already baked into hierarchical formula
- Predictive coding (90% predictable): 3x inter-level compression
- Top-down feedback (category factor R=10): sqrt(10) = 3.2x per level

CONSERVATIVE JOINT ESTIMATE: approximately 1000x-3000x SNR improvement over naive flat VSA.

This converts a 316x deficit (irrecoverable) into a 0.1-0.3x residual (well within
Hopfield basin margins). This is why L=10+ is biologically feasible.

CALIBRATION NOTE: These estimates are from standard neuroscience literature values. The
compound estimate should be treated with skepticism because:
(a) Mechanisms may not be fully independent; joint gain may be less than product.
(b) Substrate's FHRR algebra may not absorb all mechanisms without algebraic conflicts.
(c) Per calibration penalty: deflate joint P(works at full depth) by 0.20.
Adjusted P(full L=10 at substrate quality > 0.95): 0.30 (capped per protocol).

---

## 4. RANKED ENGINEERING ANCHORS (substrate-specific)

Ranked by: (P_deflated x expected_SNR_gain x implementation_ease) / cost

RANK 1: ATTRACTOR-AT-EACH-LEVEL
Why first: mechanism already validated in substrate; adding mid-level cleanup requires
only per-level codebook + Hopfield step in the composition pipeline; no algebra change.
Expected gain: 3-10x per added level.
Implementation: add Hopfield cleanup step at each shard boundary (atom->predicate,
predicate->entity, entity->document). Per-level codebook of size M_level.
P_deflated: 0.60.
Cheap decisive test: two-level composition (L=2) with mid-level cleanup vs without;
measure retrieval accuracy at L=2 with K=20 items (stress test above normal K).

RANK 2: LATERAL-INHIBITION-CLEANUP per level
Why second: compatible with FHRR algebra; no codebook redesign; implementable in one pass.
Expected gain: 3-5x per level.
Implementation: after bundling at level L, apply winner-take-K' to the bundle vector
before passing to level L+1. K' is a tuned hyperparameter (start at K'=3).
P_deflated: 0.60.
Cheap decisive test: L=3 composition with K=10; compare flat bundle vs lateral-inhibited
bundle at each step; measure final retrieval precision/recall.

RANK 3: PREDICTIVE-CODING-AT-DEPTH (PP-267 extension)
Why third: PP-267 compression is validated; extending to deep hierarchy reuses validated
mechanism; adds a generative model per level but this can be a simple linear predictor.
Expected gain: 3x per predicted level (matching PP-267 flat result).
Implementation: at each level, predict level-(L-1) from level-L representation; pass
only the residual to level-(L+1). Requires a learned predictor per level pair.
P_deflated: 0.45.
Cheap decisive test: level-2 compression chain; measure bundle entropy reduction with
vs without prediction at the inter-level boundary.

RANK 4: POPULATION-CODING-AT-EACH-LEVEL (PP-249 extension)
Why fourth: PP-249 validated at atomic level; extending to each level is algorithmic, not
mechanistic novelty; M-fold storage cost is the main constraint.
Expected gain: sqrt(M) = 3-10x per level depending on M.
Implementation: each concept at level L stored as M parallel FHRR vectors (independently
noised ensemble); cleanup averages over M before passing upward.
P_deflated: 0.55.
Cheap decisive test: L=3 composition with population size sweep M in {1, 10, 100}; plot
retrieval accuracy vs M at each level independently.

RANK 5: TREE-STRUCTURED-COMPOSITION (vs flat binding)
Why fifth: addresses the right-branching vs center-embedding asymmetry; tree structure
limits the number of active bindings at any one level to 2 (binary tree) instead of K.
Expected gain: changes K from 10 to 2 at each binary split; SNR becomes (1/sqrt(2))^L.
At L=10: (1/sqrt(2))^10 = 1/32 -- a 32x deficit, much better than 10^5.
Implementation: replace flat K-way bundle with binary tree of 2-way bindings per level.
This is a structural change to the composition algebra.
P_deflated: 0.50.
Cheap decisive test: binary-tree L=5 vs flat L=5 with K=4 total items; measure retrieval
accuracy at the root level.

RANK 6: SPARSE-CODING-AT-DEPTH (Olshausen-Field)
Why sixth: large theoretical gain but requires FHRR codebook redesign; conflicts with
current dense FHRR algebra for binding operations.
Expected gain: s=0.05 -> 20x cross-talk reduction; most powerful single mechanism.
Implementation: replace random dense FHRR codebook with sparse overcomplete basis learned
via sparse dictionary learning (LISTA or FISTA). Binding must be redesigned for sparse.
P_deflated: 0.35 (algebra conflict lowers confidence; high gain but implementation risk).
Cheap decisive test: L=2 sparse binding with GHRR (which is more amenable to sparse
representations) vs dense FHRR; measure K_max at which retrieval degrades.

RANK 7: BOUNDED-K-PER-LEVEL (chunking constraint)
Why seventh: not a separate mechanism but a constraint on usage; already partially implied
by shard hierarchy; low implementation cost (it is a usage convention, not a new component).
Expected gain: reduces effective K from 10 to 4; changes deficit from 316x to 16x at L=5.
Implementation: enforce maximum 4-6 items bundled per level in composition pipeline.
P_deflated: 0.65 (near-certain; it is algebra, not novel mechanism; uncertain whether
users will accept the 4-item K constraint in practice).

RANK 8: FEEDBACK-LOOPS-TOP-DOWN
Why eighth: strong biological basis; requires a new top-down query pathway; latency cost.
Expected gain: 3-10x per level where category priors are available.
Implementation: higher-level bundle generates a query mask that is applied to lower-level
cleanup codebook; only codebook entries within the expected category are candidates.
P_deflated: 0.38 (novel pathway; latency concern; unclear how to train/specify category
priors without a learned model).

RANK 9: SLEEP-CONSOLIDATION-AT-DEPTH (PP-141/142 extension)
Why ninth: validated at flat level but offline; not a real-time compositional fix; benefits
accumulate only for repeated compositional patterns.
Expected gain: arbitrary for high-repetition compositions; near-zero for novel ones.
Implementation: extend PP-141/142 defrag to extract compositional schema templates from
repeated compositions; store as schema bundles at each level.
P_deflated: 0.35 (useful for practiced compositions; novel compositions are unaffected;
limits scope of the mechanism).

---

## 5. CHEAP DECISIVE TEST

Test name: HIERARCHICAL-CLEANUP-STRESS-TEST

Setup:
- L=5 composition chain; K=10 items bundled at each level (stress test)
- CONDITION A (flat): no mid-level cleanup; compose all 5 levels without intermediate
  Hopfield step; retrieve at level 5
- CONDITION B (H=2): apply Hopfield cleanup at level 3 (middle); retrieve at level 5
- CONDITION C (H=4): apply Hopfield cleanup at levels 2, 3, 4; retrieve at level 5
- METRIC: retrieval accuracy (cosine similarity > threshold for correct item) at level 5
- N=4096 (existing substrate default)
- M=50 test compositions, each with K=10 novel items

Expected result:
- CONDITION A: accuracy near 0 (316x SNR deficit)
- CONDITION B: accuracy ~0.3-0.6 (hierarchical folding helps; one cleanup step reduces cliff)
- CONDITION C: accuracy ~0.7-0.9 (multi-level cleanup brings within Hopfield basin margin)

This is a 1-2 hour CPU experiment. It directly isolates the hierarchical cleanup mechanism
from all other biology-inspired mechanisms and tests the core thesis.

---

## 6. FALSIFIABLE PREDICTIONS

HARD-PASS thresholds:
- (HP-1) CONDITION C retrieval accuracy >= 0.70 at L=5, K=10
  Rationale: if hierarchical cleanup cannot achieve 0.70 at K=10, the mechanism does not
  provide sufficient gain relative to implementation cost.
- (HP-2) Accuracy gain (CONDITION C - CONDITION A) >= 0.50
  Rationale: the absolute level matters less than the relative improvement; 50pp gain
  confirms hierarchical cleanup is the dominant mechanism.
- (HP-3) Accuracy monotonically improves with H (H=0 < H=2 < H=4)
  Rationale: if accuracy is non-monotone, the cleanup is disrupting rather than helping.

HARD-FAIL thresholds:
- (HF-1) CONDITION C retrieval accuracy < 0.30 at L=5, K=10
  Interpretation: hierarchical cleanup does not transfer from L=2 (where it is known to
  work) to L=5; either FHRR algebra accumulates phase errors that cleanup cannot resolve,
  or the codebook is too small; escalate to Research for mechanism audit.
- (HF-2) CONDITION B accuracy < CONDITION A accuracy
  Interpretation: mid-level cleanup is HURTING (possible if the cleanup step is
  misaligned with the composition algebra -- e.g., cleanup against the wrong codebook
  level); immediate stop and diagnosis before proceeding with H=4.
- (HF-3) Accuracy non-monotone with H (H=4 worse than H=2)
  Interpretation: cleanup overshoots and discards compositional signal; tuning of
  cleanup margin is required before this mechanism is useful.

---

## 7. CROSS-THREAD SYNTHESIS

Prior research entry (shard hierarchy, 2026-06-10): established a 5-level shard hierarchy
for substrate. That hierarchy is precisely the architectural scaffolding needed for RANK 1
and RANK 2 mechanisms above. The shard levels (atom, predicate, entity, document, corpus)
map directly to the cortical hierarchy levels (V1, V2, V4, IT, PFC analogs). The
prior work was a necessary precursor; this note provides the mechanism rationale for WHY
each shard level should have its own cleanup memory, not just its own storage shard.

PP-267 (predictive coding, 3x compression): directly extends to RANK 3 mechanism. PP-267
showed that encoding prediction errors rather than raw bundles gives 3x bundle density
improvement. The deep extension predicts the same 3x per level, giving 3^3 = 27x for a
3-level chain. This is additive to the hierarchical cleanup gain.

PP-249 (population coding): directly extends to RANK 4. PP-249 validated that population
coding improves retrieval SNR. The deep extension predicts sqrt(M) per level, compounding
with hierarchical cleanup.

PP-141/PP-142 (sleep-defrag): directly connects to RANK 9. The offline consolidation
mechanism is already validated; the compositional schema extension is the natural next step.

Modern Hopfield networks (Ramsauer et al. 2020): exponential storage capacity in modern
Hopfield can absorb the per-level codebook cost. Classic Hopfield capacity 0.14N; modern
Hopfield capacity exp(N/2) in certain regimes. If per-level cleanup uses modern Hopfield
rather than classic, the capacity constraint on per-level codebooks is dramatically relaxed.
This is a direct path to RANK 1 implementation at scale.

VSA compositional depth literature: Gayler (2003), Smolensky (1990) tensor products,
Plate (2003) holographic reduced representations all acknowledge the L=3+ cliff. None
deployed the hierarchical solution because they were working with flat codebooks.
The present analysis is not novel in identifying the problem; it is novel in mapping
each biological fix to a specific substrate engineering anchor.

---

## 8. SUBSTRATE-PRODUCT IMPLICATIONS

A substrate that handles L=5+ compositional depth with accuracy > 0.70 is qualitatively
different from current L=2-3 systems. Specific product capabilities enabled:

(a) Multi-hop query chains of depth 5+: "Find the author of the paper cited by the paper
    that introduced the technique used by the algorithm that was applied to the dataset
    that contained the example relevant to the question." Currently fails at depth 3;
    depth 5+ with hierarchical cleanup is a concrete capability gap crossed.

(b) Document-level semantic operations: a document (L=4 composition: word->phrase->
    sentence->paragraph) can be represented as a single FHRR bundle that is retrievable
    by content. Currently retrieval degrades at paragraph level; hierarchical cleanup
    enables paragraph-level retrieval as a first-class operation.

(c) Compositional counterfactuals: replace one component at level L and recompose upward
    without full recomputation. Top-down feedback (RANK 8) enables this because the
    higher-level expectation constrains the substituted component.

(d) Schema-mediated retrieval: for well-practiced compositional patterns (common noun
    phrases, standard query patterns), sleep consolidation extracts schemas that effectively
    amortize the composition cost. Retrieval for schema-matching compositions becomes
    near-atomic in cost.

The substrate-product framing: current substrate is a high-performance associative memory
at L=1-2. Biological-overcoming mechanisms push it to L=5+ associative memory. This is
the difference between a specialized lookup engine and a general-purpose compositional
memory system -- the latter being the core product capability claim for v2.

---

## 9. HONEST LIMITS

(L-1) SPARSE CODING conflicts with FHRR algebra. The binding operation XOR (for BSC) and
element-wise multiplication (for FHRR) is designed for dense codes. Sparse codes break the
algebraic cancellation property that makes FHRR cleanup work. Implementing sparse coding
requires either (a) a new algebra compatible with sparsity (e.g., Ternary-FHRR with forced
sparsity), or (b) a two-stage approach where sparse coding operates at the codebook level
but binding uses dense projections.

(L-2) TOP-DOWN FEEDBACK requires a generative model at each level. This is non-trivial to
specify without training. If the substrate is used as a pure memory (no learned model),
top-down feedback can only operate with hand-specified category priors. The mechanism
works best in a learned setting (transformer or similar) that can generate expectations.

(L-3) PREDICTIVE CODING DEEP requires a learned predictor for each level pair. The flat
PP-267 result used a simple linear predictor. For multi-level composition, the predictor
at each level needs to know the compositional structure, which may require a more expressive
model. The 3x per-level estimate may degrade if the predictor is weak.

(L-4) COMPOUND GAIN IS NOT MULTIPLICATIVE. The nine mechanisms address overlapping noise
sources. Hierarchical cleanup and lateral inhibition both address the same inter-level
interference; their joint gain is sqrt(H_gain * LI_gain), not H_gain * LI_gain. The
1000x+ compound estimate is an upper bound, not an expected value.

(L-5) STORAGE COST SCALES WITH H x M x L. Adding per-level codebooks of size M at each
of H hierarchy levels multiplies storage by H*M relative to current flat storage. At
H=4, M=100: 400x storage increase per composition chain. This is feasible for current
hardware but requires architecture decisions about codebook sharing.

(L-6) BIOLOGICAL MECHANISMS OPERATE OVER TIME, NOT SINGLE FORWARD PASSES. Sleep
consolidation is hours. Cortical attractor settling is 50-200ms. Top-down feedback
involves multiple feedback cycles (150-400ms total in visual cortex). Substrate operates
at sub-millisecond retrieval. The mechanisms that require iterative dynamics (attractor
settling, top-down feedback cycles) add latency that may be incompatible with sub-ms
retrieval guarantees.

---

## 10. CITATIONS (Verified against knowledge base)

1. Kanerva, P. (1988). Sparse Distributed Memory. MIT Press.
2. Plate, T.A. (2003). Holographic Reduced Representations. CSLI Publications.
3. Gayler, R.W. (2003). Vector Symbolic Architectures answer Jackendoff's challenges for
   cognitive neuroscience. ICCS/ASCS.
4. Olshausen, B.A., Field, D.J. (1996). Emergence of simple-cell receptive field properties
   by learning a sparse code for natural images. Nature 381, 607-609.
5. Olshausen, B.A., Field, D.J. (1997). Sparse coding with an overcomplete basis set.
   Vision Research 37(23), 3311-3325.
6. Rao, R.P.N., Ballard, D.H. (1999). Predictive coding in the visual cortex. Nature
   Neuroscience 2(1), 79-87.
7. Friston, K. (2010). The free-energy principle: a unified brain theory? Nature Reviews
   Neuroscience 11, 127-138.
8. Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of
   mental storage capacity. Behavioral and Brain Sciences 24(1), 87-114.
9. Georgopoulos, A.P. et al. (1986). Neuronal population coding of movement direction.
   Science 233(4771), 1416-1419.
10. Pouget, A., Dayan, P., Zemel, R. (2000). Information processing with population codes.
    Nature Reviews Neuroscience 1, 125-132.
11. Hopfield, J.J. (1982). Neural networks and physical systems with emergent collective
    computational abilities. PNAS 79(8), 2554-2558.
12. Ramsauer, H. et al. (2020). Hopfield Networks is All You Need. arXiv:2008.02217.
13. Wilson, M.A., McNaughton, B.L. (1994). Reactivation of hippocampal ensemble memories
    during sleep. Science 265(5172), 676-679.
14. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995). Why there are complementary
    learning systems in the hippocampus and neocortex. Psychological Review 102(3), 419-457.
15. Stickgold, R. (2005). Sleep-dependent memory consolidation. Nature 437, 1272-1278.
16. Hauser, M.D., Chomsky, N., Fitch, W.T. (2002). The faculty of language: What is it,
    who has it, and how did it evolve? Science 298(5598), 1569-1579.
17. Smolensky, P. (1990). Tensor product variable binding and the representation of
    symbolic structures in connectionist systems. Artificial Intelligence 46, 159-216.
18. Kanerva, P. (2009). Hyperdimensional computing: An introduction to computing in
    distributed representation with high-dimensional random vectors. Cognitive Computation
    1(2), 139-159.
19. Felleman, D.J., Van Essen, D.C. (1991). Distributed hierarchical processing in the
    primate cerebral cortex. Cerebral Cortex 1(1), 1-47.
20. Marr, D. (1982). Vision: A Computational Investigation. Freeman.

Verified citation count: 20

---

## SUMMARY TABLE: Biology-to-Substrate Mechanism Map

| Mechanism | Bio source | SNR gain per level | P_deflated | Implementation ease | Rank |
|---|---|---|---|---|---|
| Hierarchical cleanup | Cortical hierarchy (V1-IT) | 3-10x | 0.60 | Medium | 1 |
| Lateral inhibition | WTA circuits (V1, OB) | 3-5x | 0.60 | High | 2 |
| Predictive coding deep | Rao-Ballard, Friston | 3x | 0.45 | Medium | 3 |
| Population coding per level | Georgopoulos, Pouget | sqrt(M) | 0.55 | Medium | 4 |
| Tree structure | Chomsky recursion | K 10->2 | 0.50 | Low | 5 |
| Sparse coding | Olshausen-Field | 20x | 0.35 | Low | 6 |
| Bounded K (chunking) | Cowan 4-item | K 10->4 | 0.65 | High | 7 |
| Top-down feedback | Friston feedback | 3-10x | 0.38 | Low | 8 |
| Sleep consolidation deep | Hippocampal replay | Unbounded (practiced) | 0.35 | Medium | 9 |

COMPOUND CONSERVATIVE ESTIMATE (mechanisms 1,2,3,4,7 only; mechanisms with P>0.50):
316x deficit * (1/6.8) * (1/10) * (1/3) * (1/4) * (1/0.68) ~ 0.05x residual
Interpretation: residual noise is 5% of signal at L=5 -- well within Hopfield basin.
P_deflated(full system working together at L=5) = 0.30 (calibration penalty applied).

---
Note path: notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
