# Research: brain capacity-efficient language mechanisms -> VSA/HDC capacity-fix menu

Filed by: research (Opus synthesis over 4 parallel Sonnet lit-scan angles: sparse coding,
hierarchical chunking/recursion, factorization/resonator, long-range positional/phase codes).
First drafted directly from literature knowledge per coordinator instruction to stop deferring
to sub-agent completions and deliver immediately; all four lit-scan sub-agents (sparse coding,
hierarchy/chunking, factorization/resonator, long-range/positional) have since returned with
live WebSearch-verified citations, and this version has been updated in place to fold in their
actual findings, corrections, and contested points (see inline notes and the Citations section
for the honest verified count).

## HEADLINE

The brain does not beat the capacity wall with one trick -- it STACKS four independent
capacity multipliers (sparse combinatorial coding, hierarchical chunk-and-pass compression,
structure/content factorization, phase/positional multiplexing), and each has a known,
CAPACITY-LIMITED VSA/HDC analog already in the literature (sparse block codes, chunked
recursive HRR with cleanup, resonator-network factorization, FHRR/SSP phase-fractional
binding). Critically, the brain's own versions of these mechanisms are ALSO bounded (sparse
codes have finite combinatorial capacity, recursion depth caps at ~2-3, working-memory slots
cap at ~4-7) -- so the correct target for our probe is not "unbounded," it is "brain-matched
bounded," which is a much cheaper, well-specified engineering target. Where our probe walls
out (vocab size vs. recursion depth vs. sentence length vs. novel combinations) selects WHICH
one of the four mechanisms to graft; grafting all four unconditionally is over-engineering. Two
of the four candidate fixes have a genuinely sharp, quantified capacity CLIFF rather than a
smooth degradation (resonator factorization: F=3-4 factor sweet spot, quadratic-N scaling,
sharp basin-narrowing near the ceiling; sparse VSA: a "superposition catastrophe" -- flat
capacity until a collapse threshold) -- this matters operationally: the cheap decisive test
should look for a THRESHOLD crossing, not a trend.
P_deflated = 0.48 (mechanisms now carry ~45 live-verified citations, several directly
quantitative, raising confidence in the mechanism claims from the initial ~0.80-0.85 estimate;
the specific graft-to-this-substrate mapping remains novel synthesis untested on this project's
actual probe, so still capped at 0.50 per the novel-synthesis calibration rule, with a small
residual deflation for the verified disentanglement-insufficient caveat that weakens the
compositional-generalization row specifically).

## 1. The brain's capacity-efficient language mechanisms

**(a) Sparse distributed coding -- combinatorial capacity from a bounded neuron pool.**
Cerebellar granule cells (Marr 1969; Albus 1971 "codon theory") and Drosophila mushroom-body
Kenyon cells receive dense random projections from a smaller input layer and were long thought
to fire sparsely to minimize representational overlap. **Verified correction (lit-scan):** the
codon-theory *prediction* of very sparse granule-cell activity is now CONTESTED -- recent
recordings show denser, lower-dimensional granule-cell activity than predicted, though the
underlying expansion-recoding computation (a kernel-machine-style separation) still holds
(Frontiers 2022; Sanger, J. Physiol 2020; "Theoretically Sparse, Empirically Dense" review).
Treat cerebellar sparsity as a contested prediction, not settled fact -- the general
sparse-coding mechanism (below) does not depend on this specific instance being correct.
Drosophila Kenyon cells remain a cleaner case: ~50 projection neurons expand to ~2000 KCs then
sparsify via winner-take-all-style inhibition, formalized as sparse binary random-projection
locality-sensitive hashing (FlyHash; Dasgupta, Stevens & Navlakha 2017) -- known limit: the
random projection cannot learn from data (motivating a learned variant, "BioHash"). Dentate
gyrus granule cells sparsify entorhinal input via feedforward/feedback inhibition
(competitive WTA-like dynamics), decorrelating similar inputs before CA3 storage (PLOS Comp
Bio 2023; PMC4542503) -- this is the cleanest, most replicated sparse pattern-separation
mechanism in the scan. Olshausen & Field (1996, Nature) showed sparse coding of natural images
reproduces V1 simple-cell receptive fields, with overcomplete sparse codes raising
representational capacity by orders of magnitude over complete codes.

The capacity payoff is combinatorial, not linear: for N units with k active, the number of
distinguishable sparse patterns is C(N,k), which for k<<N vastly exceeds N itself. Willshaw
associative memory theory (Willshaw, Buneman, Longuet-Higgins 1969; Graham & Willshaw 1997;
Knoblauch survey) formalizes this quantitatively: **binary-coupling information capacity
reaches ~0.69 bits/synapse at optimal sparsity (Gardner-style bound ~0.29 bits/synapse for
comparison), with capacity M ~ mn/(k*l) -- a k-dependent penalty unless sparsity is tuned, and
WTA-dynamics variants provably hit the optimal ln(2) capacity bound.** Sparse associative
memory's max storable-patterns-without-crosstalk scales as ~1/a where a is the mean-activity
fraction -- capacity formally diverges as activity -> 0, which is exactly why sparsity is a
capacity multiplier rather than a side effect. This is "bounded neurons -> unbounded-feeling
capacity": neuron count is fixed, the COMBINATORIAL ADDRESS SPACE over sparse activity patterns
is what scales.

**(b) Hierarchical composition + chunking -- recursive abstraction, not unbounded vocabulary.**
Cortical processing hierarchy shows increasing "temporal receptive windows" (TRW) going up the
hierarchy: primary auditory cortex integrates over milliseconds, superior temporal gyrus over
words, language areas over sentences, and apex parietal/frontal regions only over intact
multi-sentence narrative (Lerner, Honey, Silbert & Hasson 2011, J. Neurosci; replicated/
extended PNAS 2022). **Verified caveat:** one study (ScienceDirect 2020) found no significant
TRW differences among language regions specifically at fine resolution -- the hierarchy effect
is robust at whole-cortex scale but contested at fine within-language-network grain; treat as
solid-but-coarse-grained precedent. Ding et al. (2016, Nature Neuroscience) showed cortical
tracking of hierarchical linguistic units (syllables/words/phrases/sentences) at nested,
distinct oscillatory rates simultaneously -- direct neurophysiological evidence for online
hierarchical chunking during speech comprehension. Miller's "7+/-2" (1956), reinterpreted by
Cowan (2001, 2005) as a true attentional-focus limit of **~4 chunks** (with live debate whether
the floor is as low as 1 -- PMC3197943), shows working memory is chunk-bounded: a chunk is a
compression of lower-level primitives into one higher-level symbol. A 2024/25 PFC-basal-ganglia
circuit study (PMC11870651) shows adaptive chunking measurably INCREASES effective working
memory capacity -- i.e. chunking is a real neural capacity-multiplier mechanism, not just a
cognitive-psychology redescription, and it is implemented by a specific fronto-striatal circuit
with an anterior-to-posterior PFC gradient handling progressively more abstract chunk levels.
The capacity trick is RECURSIVE: the vocabulary/alphabet needed at any single level stays
small and bounded; what looks unbounded is the DEPTH of nesting of bounded-size chunks, not an
unboundedly large flat symbol set. (Caveat on "recursion" itself: Hauser, Chomsky & Fitch 2002
proposed recursion as the singular human-specific language mechanism; this is heavily contested
(Pinker & Jackendoff 2005 and later critiques) -- treat "language needs true recursion" as a
live linguistic debate, not settled neuroscience, when deciding how hard to chase recursion
depth in the VSA analog below.)

**(c) Factorization -- separating structure from content.**
Syntax-semantics dissociation in aphasia is real but GRADED, not a clean two-module split:
lesion-symptom mapping shows syntactic/morphosyntactic performance tracks left frontotemporal
network integrity while semantic/lexical performance is more bilaterally and "degenerately"
organized (right STG/MTG can partially substitute); agrammatism vs. paragrammatism map to
distinct lesion sites but true clean double dissociations are rare (verified via lit-scan --
moderate support, not proof of hard factorization). The clearest and STRONGEST direct
biological analog found is grid cells / entorhinal-hippocampal circuitry: entorhinal grid cells
provide a content-independent structural/relational scaffold (metric, graph-like coordinates)
that stays geometrically stable across environments, while hippocampal place cells bind
specific content onto that scaffold and REMAP when content changes but structure doesn't (Fyhn
et al. 2007, Nature, "Hippocampal remapping and grid realignment in entorhinal cortex"). The
Tolman-Eichenbaum Machine (Whittington, Muller, Mark, Barry, Behrens et al. 2020, Cell)
formalizes this as a factorized STRUCTURE code (grid-like, content-independent, reusable across
tasks/environments) bound to a swappable CONTENT code (place-like), and argues this
factorization is EXACTLY what licenses systematic generalization to novel content in a familiar
structure: the structure code never has to be relearned, only rebound. This is the direct
biological analog of the Fodor & Pylyshyn (1988) systematicity challenge to connectionism (whose
tensor-product-representation rebuttal by Smolensky is the direct ancestor of VSA binding).
**Important recent counter-evidence (verified):** a 2025 paper (arXiv 2501.18797,
"Compositional Generalization Requires More Than Disentangled Representations") shows
empirically that disentanglement/factorization ALONE is not sufficient -- many models with
clean factorized latents still fail to compose out-of-distribution. So factorization is
NECESSARY-looking in biology but not proven SUFFICIENT in engineered systems; the current best
engineered fix for the SCAN/COGS failure mode is Lake & Baroni's meta-learning-for-compositionality
(MLC, Nature 2023), which is a TRAINING-CURRICULUM fix, not a pure architectural-factorization
fix. This tempers how much weight the capacity-fix menu (section 4) should put on factorization
alone.

## 2. Mechanisms for exactly what VSA struggles with

**Long-range syntax without crosstalk.** Binding-by-synchrony (von der Malsburg 1981, 1999)
proposes precise spike-timing (phase), not a separate tag, binds co-belonging elements into
transient assemblies, with the same neuron joining different assemblies at different moments
(temporal multiplexing). **Verified calibration:** this is CONTESTED as established fact
(Shadlen & Movshon and others raise serious encoding/decoding objections) -- solid as a
proposed mechanism, not settled ground truth. Theta-gamma phase coding (Lisman & Idiart 1995;
Lisman & Jensen 2013; a 2023 computational instantiation, PMC10050512) extends a related idea
to working memory: nested gamma cycles within a theta cycle act as discrete slots, with slot
count tied to theta/gamma frequency ratio, converging with the Miller/Cowan ~4-7 capacity
numbers -- verified as a good-but-model-dependent mechanism (the quantitative theta-freq <->
capacity mapping is not yet a fully closed empirical loop). The STRONGEST verified positional
mechanism in the whole scan is theta phase precession (O'Keefe & Recce 1993; Skaggs et al.
1996): place cells fire at progressively earlier theta phases across a traversal, compressing
spatial trajectories into within-cycle firing-ORDER sequences ("theta sequences") -- a genuine,
well-replicated phase-based positional code. Time cells (PMC4348090) give an analogous
rate-coded (not phase-coded) temporal-position code for non-spatial event sequences in both
rodent and human hippocampus. Dentate gyrus sparse pattern separation (PMC3726960) independently
corroborates "sparse expansion = interference mitigation" as a general-purpose, not
language-specific, brain-wide mechanism.

**Recursion/embedding.** Human center-embedding is NOT unboundedly recursive in practice:
classic psycholinguistic results (Miller & Chomsky 1963) and corpus/experimental work
(Karlsson 2007; ResearchGate 345017757; arXiv 2206.13217) show comprehension craters beyond
depth ~2 in English, with some speakers managing 3-4 only under reduced-memory-load structures
(e.g. Japanese prenominal embedding). A specific, well-cited proposal -- the "magical number
two/three" (Gibson & Thomas-style interference account, *J. Psycholinguistic Research*) --
argues syntactic working memory can index NO MORE than ~2 constituents under the same relation
before interference dominates: a genuine, quantified biological capacity WALL directly
analogous to the resonator/codebook capacity ceilings below. Christiansen & Chater's
"Now-or-Never bottleneck" (2016, Behavioral and Brain Sciences) argues the brain does NOT
implement a symbolic push-down stack for recursion at all -- it survives apparent recursion via
aggressive CHUNK-AND-PASS compression: each constituent is compressed into a chunk and
discarded from raw working memory as soon as possible, so "recursion" is approximated, and the
approximation's error accumulates with depth (consistent with the sharp depth-2 ceiling). This
is an important calibration point: the brain's own recursion mechanism is finite and leaky, not
a template for unbounded recursion -- match that ceiling, don't try to beat it. (Note: an HRR
recursion-depth-vs-accuracy curve with specific numbers surfaced in the lit-scan but could NOT
be traced to a verifiable source this pass -- flag as plausible-direction-but-unconfirmed, do
not cite the specific numbers as fact.)

**Compositional generalization / systematicity.** The SCAN (Lake & Baroni 2018) and COGS
benchmarks demonstrated that standard seq2seq/transformer nets fail systematic generalization
to novel word combinations even when they've seen all the parts. Proposed fixes converge on
imposing explicit factorized/structured representations (slot-filling architectures,
meta-seq2seq, grammar-constrained decoding) -- i.e., the SAME factorization principle as TEM in
neuroscience, independently re-derived in the ML literature as the fix for the exact failure
mode.

## 3. VSA/HDC analogs -- mapped mechanism by mechanism

| Brain mechanism | VSA/HDC analog | Breaks the capacity wall? | Known gap vs. typical VSA use |
|---|---|---|---|
| Sparse combinatorial coding (DG pattern separation is the cleanest verified instance; cerebellar/KC contested-but-directional) | Binary Sparse Distributed Codes / Context-Dependent Thinning (Rachkovskij & Kussul), Sparse Block Codes + Factorizer (Frady/Kleyko/Sommer program, arXiv 2303.13957), FlyHash-style sparse random projection | Partially -- **verified quantitative finding: sparsity has essentially NO effect on VSA capacity until a "superposition catastrophe" threshold, where capacity collapses (a cliff, not smooth degradation)**; up to that cliff, Willshaw-style theory (~0.69 bits/synapse at optimal sparsity) supports the combinatorial-capacity story | Most VSA/HDC pipelines use DENSE bipolar/binary/complex vectors by default; disjunction-based sparse binding (OR) causes DENSITY INFLATION requiring an explicit re-thinning step (CDT) -- an added mechanism cost, not a free drop-in |
| Hierarchical chunking (cortical TRW hierarchy; PFC-basal-ganglia adaptive chunking, PMC11870651) | Recursive HRR / nested role-filler binding trees (Plate 1995) with a cleanup/re-binarization step after each bind; chunked/bundled hierarchical encoding (bundle local sub-groups before bundling groups, not one flat sequence) | Partially -- HRR natively supports recursive binding, but the quasi-inverse is inexact and noise VARIANCE accumulates with number of bindings, capping practical depth (specific depth-vs-accuracy numbers unverified this pass); chunked/bundled encoding is an established, explicit VSA engineering fix for crosstalk that directly mirrors the brain's chunking mechanism | Typical HRR/VSA composition binds recursively WITHOUT an explicit per-level cleanup/renormalize step, so noise from all levels compounds instead of being reset -- this is the single biggest addressable, verified-by-analogy gap |
| Factorization (grid/place code remapping, Fyhn et al. 2007; TEM) | Resonator Networks (Frady, Kent, Olshausen, Sommer 2020, Neural Computation I & II) for joint iterative unbinding of multiple superposed factors; structure-codebook vs. content-codebook split mirroring TEM directly | Yes for the architecture, WITH VERIFIED QUANTITATIVE LIMITS: **capacity scales roughly quadratically in vector dimension N; capacity vs. number-of-factors F peaks around F=3-4 and falls off for more factors or imbalanced (10-20x) codebook sizes; operational capacity runs ~2 orders of magnitude above optimization baselines (ALS/gradient methods); near the ceiling, basins of attraction narrow sharply and convergence is not guaranteed (empirically <0.001*N iterations well inside capacity)** | Typical VSA composition binds structure and content into ONE vector with no reusable, content-independent structure codebook -- so novel content in a familiar structure isn't recognized as "familiar structure," unlike TEM/grid-cell reuse. **Also verified: factorized/disentangled representations alone are empirically NOT sufficient for compositional generalization (arXiv 2501.18797)** -- expect this graft to need pairing with a training-curriculum signal (cf. MLC, Lake & Baroni, Nature 2023), not architecture alone |
| Phase/positional multiplexing (theta phase precession/time cells -- the strongest verified positional mechanism in this scan; theta-gamma slot nesting is model-dependent) | FHRR complex-valued phase binding (Plate 2003); Fractional Power Encoding / Spatial Semantic Pointers (Komer & Stewart; FPE cleanup arXiv 2412.00488; Generalized HRR arXiv 2405.09689) for continuous, degree-invariant positional binding | Yes for encoding continuous position without discrete slot explosion; **verified: bundling capacity scales roughly linearly with dimension, but unbinding from superposition always introduces crosstalk noise that grows with bundle size, mitigated only by cleanup/associative-memory readout (arXiv 2106.05268, arXiv 2301.10352)** | Typical VSA positional binding is FLAT (one positional code space for the whole sequence) rather than the brain's TWO-TIER nesting (slot-within-chunk, chunk-within-theta-cycle); no paper surfaced in this scan that directly measures positional-code capacity vs. sentence-length crosstalk in an HRR syntax-parsing setting -- flagged as a genuine open gap, not just an unexplored analogy |

**The core gap, stated once:** the brain never uses any ONE of these four mechanisms alone --
it stacks all four simultaneously (sparse + chunked/hierarchical + factorized + phase-coded).
Standard VSA/HDC benchmarks and our own probe architecture typically test/use these largely IN
ISOLATION (e.g., dense bipolar vectors with flat positional binding and no resonator-style
factor search). The capacity walls we hit are exactly where the missing combination would have
paid for itself. The verified resonator numbers above (F=3-4 sweet spot, quadratic-N scaling,
sharp-not-gradual failure near the ceiling) and the verified sparse-VSA "superposition
catastrophe" cliff both point to the SAME general shape: these are not smoothly-degrading
capacity curves, they are cliffs -- which means the cheap decisive test below should look for a
THRESHOLD crossing, not a gradual trend, when classifying which failure mode the probe hit.

## 4. THE CAPACITY-FIX MENU (keyed to where the probe walls out)

| Failure mode at the early-reader glass-box probe | Brain mechanism to match | VSA graft to test | Design target (brain-matched, NOT unbounded) |
|---|---|---|---|
| Wall at **larger vocabulary** (more distinct atoms/fillers needed than fit cleanly) | Sparse combinatorial coding (cerebellar/DG/KC expansion) | Swap dense atom vectors for sparse block-code / BSDC atoms at the SAME total dimension budget; capacity should scale ~C(N,k) not linearly | Target: combinatorial vocabulary headroom at fixed D, not infinite -- expect a new (higher, still finite) sparsity-dependent ceiling |
| Wall at **embedded clauses / recursion depth** | Chunk-and-pass compression (Now-or-Never bottleneck), NOT a true unbounded stack | Add a cleanup/re-binarize-to-nearest-codebook-vector step after EVERY bind operation in the recursive HRR tree (reset noise per level instead of letting it compound) | Target depth ~2-3 (matches human center-embedding ceiling) -- do not chase unbounded recursion; if cleanup doesn't get you to depth 3 the problem is the binding op's noise floor itself, not cleanup frequency |
| Wall at **long sentences / long-range dependency binding** | Theta-gamma nested phase multiplexing (~4-7 slot capacity per chunk) | Replace flat single-tier positional binding with a TWO-TIER scheme: chunk sentence into groups of ~4-7 tokens (theta-analog), bind each chunk with FHRR/SSP fractional positional codes (gamma-analog), then bind chunks into a higher-level sequence code | Target: recover long-range accuracy to near short-sentence baseline by keeping each tier's slot count within the brain-matched ~4-7 ceiling, rather than growing one flat positional space |
| Wall at **compositional generalization to novel word/relation combinations** | Structure/content factorization (grid-cell code x place-cell code, TEM) | Enforce a hard split: fixed, content-independent STRUCTURE codebook (reused across all utterances) bound to swappable CONTENT fillers; decode via resonator-network joint factorization rather than direct dense unbind. **Verified caveat: pair this with a training-curriculum signal (MLC-style, Lake & Baroni Nature 2023) -- disentangled/factorized representations ALONE are empirically insufficient (arXiv 2501.18797)** | Target: held-out novel content-in-familiar-structure combinations recovered at rates far above a non-factorized dense baseline -- this is the TEM/SCAN-fix signature, and it's the one most directly tied to the "relational is the core requirement" program spine. Do not treat a factorization-only graft as a full test of this hypothesis; a null result could mean "needs curriculum too," not "factorization doesn't help" |
| Wall at **simultaneous multi-factor decode / general crosstalk in superposition** | Iterative attractor-style constraint satisfaction (resonance/pattern-completion dynamics), only needed as backstop when sparse+modular coding doesn't fully prevent crosstalk | Resonator networks over sparse, block-local codebooks (combine fix #1 and this one) | Target: verified resonator capacity ceiling -- **quadratic-in-N scaling, F=3-4 factor sweet spot, sharp basin-narrowing failure near the ceiling (not gradual)** -- if the probe needs to exceed F=3-4 simultaneous factors, the correct move is shrinking simultaneous-factor count or growing block width/dimension, not pushing iteration count harder (empirically converges in <0.001*N iterations well inside capacity, so more iterations near the ceiling will not rescue it) |

**Ordering recommendation (cheapest-first):** the recursion-depth cleanup graft (row 2) and the
two-tier positional chunking graft (row 3) are single-parameter, low-engineering-cost swaps that
directly test the "brain caps itself, match the cap" hypothesis; try these FIRST when the probe
first shows a capacity wall, before reaching for the heavier sparse-block-code (row 1) or
resonator-factorization (row 4/5) grafts, which require architecture changes.

## Cheap decisive test

When the early-reader glass-box probe walls out, first CLASSIFY which of the four failure
modes it is (vocab-size-limited vs. recursion-depth-limited vs. sentence-length-limited vs.
compositional-generalization-limited) by looking at where accuracy first drops as each axis is
scaled independently while holding the others fixed. Then graft EXACTLY ONE corresponding fix
from the menu above in isolation (no combined fixes), re-run the identical probe, and measure
whether that single graft moves the wall. This is cheap because each graft is a single
swap-in (no multi-fix confound), and it directly tests which brain mechanism is the actual
missing piece for THIS substrate's specific failure, rather than assuming all four are needed
at once.

## Falsifiable predictions (HARD-PASS / HARD-FAIL per graft)

- **Sparse-coding graft (vocab wall):** HARD-PASS = swapping dense atoms for sparse
  block-code/BSDC atoms at the same dimension budget increases max passable vocabulary size by
  >=2x at the same crosstalk/accuracy threshold. HARD-FAIL = <10% relative improvement (within
  noise floor) -- reject; the substrate's capacity bottleneck is not code-density-driven, look
  at codebook orthogonality instead.
- **Recursion-cleanup graft (embedded-clause wall):** HARD-PASS = per-level cleanup extends
  usable recursion depth by >=1 full level (e.g. 2->3) at a fixed per-level factor-recovery
  threshold (>=90%). HARD-FAIL = depth gain <1 level or accuracy degrades with cleanup added --
  recursion noise is structural to the bind operator itself, not a cleanup-frequency artifact.
- **Two-tier positional-chunking graft (long-sentence wall):** HARD-PASS = two-tier chunked
  code (chunk size ~4-7) recovers long-range dependency accuracy to within 10% of the
  short-sentence baseline at lengths where a flat single-tier positional code has already
  degraded >30%. HARD-FAIL = <5% recovery -- the crosstalk source is not positional-code
  flatness; look elsewhere (e.g. codebook capacity itself).
- **Structure/content factorization + resonator graft (compositional-generalization wall):**
  HARD-PASS = >=20 percentage-point accuracy improvement on held-out novel
  content-in-familiar-structure combinations vs. a non-factorized dense baseline. HARD-FAIL =
  <5 points -- factorization doesn't transfer to this substrate without other confounds (e.g.
  training/ingest regime), reconsider whether the structure codebook is actually
  content-independent as constructed.

## Cross-thread synthesis

This drill sits directly on top of this project's own prior line of work rather than starting
cold:
- `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`,
  `notes/research_resonator_reachability_ceiling_2026-07-07.md`,
  `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md` -- prior
  drills already established that resonator-network factorization has a real, measured
  capacity ceiling on this substrate; this drill's row-4/5 graft should be read as "apply the
  already-known resonator ceiling deliberately, as a factorization tool," not as introducing an
  untested mechanism.
- `notes/research_bundling_capacity_beyond_fixed_N_theta_gamma_chunking_sparse_2026-07-08.md`
  and `notes/research_degree_agnostic_sparse_tail_relational_encoding_brain_first_2026-07-08.md`
  -- prior work already probed theta/gamma chunking and sparse-tail encoding; this drill adds
  the explicit brain-mechanism-to-VSA-graft mapping and the failure-mode-keyed menu structure
  those drills didn't yet organize into.
- `notes/research_meaning_growth_abstraction_compositionality_ladder_2026-07-09.md`,
  `notes/research_ood_compositional_generalization_for_M3_2026-07-02.md`,
  `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
  -- compositional generalization has a long history in this project; TEM/structure-content
  factorization (section 1c/3) is the biology-first mechanism these threads were reaching for.
- `notes/research_ssp_fractional_binding_degree_invariant_relational_code_2026-07-10.md` --
  fractional power encoding / SSP was already identified as a degree-invariant relational code
  in a prior drill; this note ties it explicitly to the theta-gamma positional-multiplexing
  mechanism and gives it a specific graft point (two-tier chunked positional code) rather than
  a standalone primitive.
- `project_session_endstate_machinery_complete_foundation_endgame_builder_2026-07-15` (memory
  index) names the exact trigger for this drill: an early-reader glass-box probe expected to
  wall out on complexity. This note is the pre-registered brain-faithful fix menu for that
  event, ready BEFORE the wall is hit, per the standing discipline of drilling negatives/walls
  proactively rather than reactively.

## Substrate-product implications

Framed as product roadmap, not publication (per the no-papers-product-only discipline): the
practical takeaway is that a capacity wall in the early-reader probe is NOT evidence of a
fundamental ceiling in the substrate-product's architecture -- it is evidence that ONE of four
well-characterized, biologically-grounded fixes has not yet been grafted in. This converts "the
probe walled out" from a stop-signal into a diagnostic (which of four failure modes?) with a
pre-registered, cheap, single-swap test per mode. It also gives the product narrative concrete
teeth: "bounded compute, brain-matched capacity ceilings, not infinite promises" is a more
honest and more defensible position than claiming unbounded scaling, and it is literally what
the existence-proof premise (finite ~86B neurons -> high-capability language) implies once you
look at HOW the brain achieves it -- every one of its four mechanisms is itself capacity-CAPPED
(sparse code combinatorics are finite, recursion depth caps at 2-3, working-memory slots cap at
~4-7). The product should advertise "brain-matched bounded capability" rather than promise
unbounded compositional reach.

## Citations (verified count)

**Update:** all four lit-scan sub-agents completed after the first draft of this note and their
live WebSearch-verified findings have been folded in above (contested cerebellar sparsity,
Willshaw 0.69 bits/synapse, superposition-catastrophe cliff, TRW fine-grain caveat, PFC-BG
adaptive chunking, HCF recursion debate, grid-cell remapping Fyhn 2007, disentanglement-
insufficient caveat, resonator F=3-4/quadratic-N/basin-narrowing numbers, magical-number-two/
three syntactic WM limit, theta phase precession / time cells, FPE/SSP cleanup literature).

**Verified-this-cycle (live WebSearch, sourced with URLs by the sub-agents): ~45 distinct
sources**, spanning: Frontiers 2022 & Sanger 2020 & ScienceDirect (cerebellar sparsity
contested); PLOS Comp Bio 2023 & PMC4542503 & PMC3726960 (dentate gyrus pattern separation);
Dasgupta/Stevens/Navlakha 2017 arXiv:2001.04907 (FlyHash); Olshausen & Field 1996 Nature; arXiv
1512.08892 & Knoblauch survey (Willshaw capacity); arXiv 2303.13957 (sparse block code
Factorizer, superposition catastrophe); Rachkovskij/Kussul BSDC (ACM survey, ResearchGate);
Frady/Kleyko/Sommer IEEE TNNLS 2023 (sparse binding theory); Lerner et al. 2011 PMC2556707 &
PNAS 2022 & ScienceDirect 2020 (TRW hierarchy + caveat); Cowan 2005 PDF & PMC3197943 (chunking
capacity); PMC10050512 (theta-gamma slot model); PMC11870651 (PFC-BG adaptive chunking); HCF
2002 Science & PMC3478773 (recursion debate); Smolensky 1990 (TPR); Plate HRR PDF (Redwood);
PeerJ VSA biomedical tips (chunked bundling); arXiv 2606.14512 & arXiv 1902.09006 &
Fodor/Pylyshyn systematicity literature; Fyhn et al. 2007 Nature & PMC7282808 (grid-cell
remapping / TEM precedent); aphasia dissociation sources (Academia.edu, PMC8293792); Lake &
Baroni 2018 arXiv:1711.00350 (SCAN) & Nature 2023 (MLC); arXiv 2501.18797 (disentanglement
insufficient); Frady/Kent/Olshausen/Sommer 2020 Resonator Networks I (rctn.org) & II (MIT
Direct); arXiv 2412.00354 (resonator noise robustness); arXiv 2404.19126 (scene factorization);
Scholarpedia & PMC9574343 & ScienceDirect S0896627300808223 & PMC3538094 (binding-by-synchrony,
contested); Wikipedia phase precession & PMC5550484 (theta phase precession); PMC4348090 (time
cells); PLOS Comp Bio 1007936 & PNAS 1820730116 (activity-silent working memory); PubMed
11523277 & ResearchGate 11823104 (filler-gap ERP evidence); ResearchGate 345017757 & arXiv
2206.13217 (center-embedding depth limits); Gibson & Thomas magical-number-two/three (J.
Psycholinguistic Research); Komer & Stewart SSP (eScholarship) & arXiv 2412.00488 (FPE cleanup)
& arXiv 2405.09689 (Generalized HRR); arXiv 2106.05268 & arXiv 2301.10352 (VSA capacity
analysis).

**Unverified-this-cycle (recalled from training knowledge, flagged inline, do not treat as
load-bearing for a HARD-PASS/HARD-FAIL gate without direct confirmation):** Marr 1969; Albus
1971 codon theory specifics beyond what the sub-agent independently found; Willshaw/Buneman/
Longuet-Higgins 1969 original paper (confirmed indirectly via Knoblauch survey, not directly
fetched); Ding et al. 2016 Nature Neuroscience (hierarchical oscillatory tracking); Miller 1956;
Miller & Chomsky 1963; Karlsson 2007; Christiansen & Chater 2016 Now-or-Never bottleneck;
Whittington et al. 2020 Cell (TEM) direct text; von der Malsburg 1981/1999 original text
(confirmed indirectly via Scholarpedia/PMC, not directly fetched); Lisman & Idiart 1995; Lisman
& Jensen 2013; O'Keefe & Recce 1993; Skaggs et al. 1996; Plate 2003 FHRR original text; one
specific HRR recursion-depth-vs-accuracy numeric claim (explicitly flagged unverifiable by the
hierarchy/chunking sub-agent -- do not cite).

Net: this cycle moved from 0 to ~45 live-verified sources; several previously-uncertain claims
(sparse-VSA "capacity is roughly flat until a cliff," resonator F=3-4 sweet spot, grid-cell
remapping as the TEM precedent, disentanglement being insufficient) are now solidly sourced and
should be treated as load-bearing for the falsifiable predictions below. The remaining
unverified list above is smaller and lower-stakes (mostly foundational-paper existence, not
the quantitative claims used in the decision gates).
