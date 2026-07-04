# Research Drill: Cardinality/Capacity Ceiling -- Is 0.85 Reachable? (2026-07-04)

**Author:** Director (Research)
**Trigger:** 2x-drill flagged a likely NEXT lever after NCE-off: DENSE spearman ~0.734 at full 178k vocab vs
~0.825 at tiny (~3k) vocab, a scale-driven drop no batch/objective trick controls for. This memo prepares
the move IF the NCE-off FULL run lands ~0.73 and short of 0.85.
**Method:** 4 parallel Sonnet lit-scans (sign-rank/combinatorial capacity bounds; neural-collapse geometry vs
JL distortion scaling; structural-lever ranking; diagnostic-location methodology), generic math-terms-only
queries per query-privacy discipline (no substrate-novel vocabulary, no configs/numbers used off-platform).
Multiple citations independently spot-verified via direct WebFetch by the sub-agents themselves (not just
snippet-level), flagged per-item below.
**Calibration:** lit-scan penalty applied throughout (deflate 0.15-0.25 off naive reads; novel-synthesis
extrapolation to our exact combined setup capped at 0.50). **Do NOT dispatch experiments** -- decision memo
only, per instruction. No exp_dev hand-off file written this cycle (the trigger condition -- NCE-off FULL
landing short of 0.85 -- has not yet confirmed; this memo stages the lever menu for that moment, following
the same precedent as the two prior same-day sibling drills in this thread, which also used decision tables
rather than premature hand-offs).

---

## HEADLINE

**0.85 is very likely reachable in principle -- there is no hard information-theoretic wall in the way -- but
it is unlikely to be reached by the NCE-fix alone, at the CURRENT rigid code structure and loss function.**
Four independent lit-scans converge on the same shape of answer from four different angles:

1. **The classical "ran out of room" ceilings do not apply here.** Both sign-rank/embedding-dimension theory
   (Weller et al., LIMIT paper, arXiv:2508.21038, directly fetched) and Johnson-Lindenstrauss-style continuous
   distortion theory predict d=4096 is comfortably oversized for representing 177,899 items' *natural*
   (non-adversarial) pairwise similarity structure -- JL's own bound implies only a ~23% relative increase in
   worst-case distortion going from N=3,000 to N=177,899, nowhere near enough to explain a 0.825->0.734 drop.
   Raw combinatorial capacity (~640 bits/item of support-pattern entropy in a K=128-of-4096 code) vastly
   exceeds the ~17.4 bits needed for bare item-distinctness at N=177,899. **Sheer distinctness is not
   remotely exhausted.**
2. **The real cost is structural, not dimensional: the code's rigid, axis-aligned BLOCK structure is
   mathematically Product Quantization (PQ)**, and PQ is well-documented (independent of our project) to pay
   a real, well-characterized "subspace-independence" tax whenever the true data does not decompose along the
   fixed block boundaries -- which is virtually certain for a dense, non-block-structured teacher embedding.
   This tax gets WORSE as N grows because more items means finer distinctions are needed, and the
   axis-misaligned blocks have less resolving power per distinction than an aligned or free code would.
3. **A second, independently-converged, essentially-free lever is the LOSS FUNCTION itself**: raw
   reconstruction/cosine-MSE-style objectives are not the same as rank-preservation objectives, and the ANN
   literature (Guo et al., "anisotropic vector quantization" / ScaNN, arXiv:1908.10396, directly fetched) has
   already solved a structurally identical problem by reweighting reconstruction error toward the direction
   that matters for ranking. This costs zero width/architecture change.
4. **Whether a genuine hard ceiling exists at all cannot yet be determined from two data points** (N=3,000
   and N=177,899) -- the literature is unanimous that a sharp capacity cliff (Hopfield-style, compressed-
   sensing-style) looks qualitatively different from a smooth training/objective-driven decline
   (distillation capacity-gap scaling laws), and two points cannot distinguish the two shapes.

**P_deflated(0.85 is reachable via SOME structural lever, not necessarily the current code as-is) = 0.45**
(capped; novel cross-domain synthesis).
**P_deflated(the NCE-fix ALONE, with the current rigid block-code and reconstruction-style loss, reaches
0.85 at full scale) = 0.20** (deflated hard; convergent structural evidence says real, currently-uncorrected
fidelity is being left on the table independent of the NCE issue).
**P_deflated(there is a genuine, hard, N-dependent capacity ceiling that NO structural lever below can fix)
= 0.15-0.20** (low; the classical "ran out of room" mechanisms that would justify a hard wall do not fit the
evidence, per all four scans).

---

## Does the ceiling depend on N (cardinality) or on d/K (code capacity)?

**Both, but not the way the naive framing suggests -- it depends on the RATIO of N (demand for resolving
power) to the code's EFFECTIVE (not raw combinatorial) resolving power, and "effective" is where the
answer lives.**

- Classical continuous-embedding theory (JL, sign-rank on natural/non-adversarial structure) says N enters
  only *logarithmically* -- a 59x growth in N should cost almost nothing at d=4096. This was checked
  independently by two lit-scans and both falsify a naive "N is too big for d" story on its own.
- But the RAW combinatorial capacity of a K-of-d code (`C(d,K)`, or the bits-per-item entropy of choosing
  which K of d slots are active) systematically OVERSTATES the code's true, EFFECTIVE resolving power for
  a continuous rank-order target, because (a) the block-structured/axis-aligned selection (Product
  Quantization) forces information into slots that do not align with the teacher's actual semantic axes,
  and (b) the training loss currently optimizes reconstruction fidelity, not the ranking-relevant projection
  of that fidelity. Both of these are FIXABLE, structural/objective inefficiencies, not fundamental limits.
- The VSA/HDC "bundling capacity" literature (Clarkson-Ubaru-Yang, arXiv:2301.10352, fetched) and the
  Donoho-Tanner / compressed-sensing phase-transition literature both describe scaling laws for *this kind*
  of discrete/sparse code that are much closer to POWER-LAW-in-N (or linear-in-d for fixed accuracy) than
  JL's logarithmic law -- consistent with the empirically observed large drop, and consistent with "this is
  a real, structural, code-type effect," not with "d=4096 fundamentally cannot hold 177,899 items."
- **Bottom line: N drives the DEMAND for resolving bits (more items -> finer distinctions needed as the
  typical similarity gap between the i-th and (i+1)-th nearest neighbor shrinks, an order-statistics
  effect); d/K/code-TYPE determines the SUPPLY of resolving bits per item. The current gap is best explained
  by supply being systematically under-delivered relative to its raw combinatorial potential (axis
  misalignment + wrong loss), not by an intrinsic d-vs-N impossibility.**

---

## Ranked structural levers (highest to lowest expected gain-per-cost)

| Rank | Lever | Mechanism | Cheapest test | Cost | P_deflated |
|---|---|---|---|---|---|
| **1** | **Rank-aware / anisotropic quantization loss** (reweight reconstruction error toward the direction that matters for pairwise-ranking, not raw magnitude) | ANN-search literature (Guo et al., ScaNN, arXiv:1908.10396, VERIFIED via fetch) solved a structurally identical problem: standard reconstruction-MSE quantizer training leaves real ranking-fidelity on the table; anisotropic reweighting recovers it at ZERO width/architecture cost. Directly addresses the "compounds with sparsity" finding (anisotropic teacher geometry + coarse quantizer = fewer effective resolving bits inside the dominant similarity cone) that a 4th lit-scan independently flagged as the compounding factor. | Swap the training loss from reconstruction/cosine-MSE to a Spearman/ranking-aware or inner-product-weighted loss, same code, same width, one retrain. | Near-zero (loss-function ablation only) | **0.50** (capped; strong adjacent-domain analog, no source runs our exact distillation-into-bipolar-sparse-code setup) |
| **2** | **Code-type fix: learned rotation before block-selection (OPQ-style), or move away from rigid block-WTA toward free top-k / additive quantization** | Our block-WTA structure IS Product Quantization (PQ) mathematically. PQ's well-documented "subspace-independence" cost is exactly the axis-misalignment tax described above. Optimized Product Quantization (OPQ, rotation-learning) fixes this CHEAPLY -- learn a rotation matrix applied before the same per-block argmax, no width/runtime change. A full free-top-k or Additive Quantization (AQ) rebuild would recover more but costs a genuinely different selection mechanism. | Insert one learned (or even PCA/whitening) rotation before the existing per-block argmax; retrain, compare to un-rotated baseline at full N. | Low (rotation matrix + retrain; OPQ variant) to Medium (full AQ/free-top-k rebuild) | **0.45** (rotation-only variant); **0.30-0.35** (full rebuild, higher cost) |
| **3** | **Widen the code (d: 4096->8192, K: 128->256, same ~3% fraction)** | Two competing scaling proxies bracket the answer and DISAGREE on magnitude: the cheap log-regime (compressed-sensing-style `M ~ k*log(N/k)`) implies ~2.3x width growth needed for the observed 59x N growth; the steeper power-law regime (LIMIT's own empirical cubic fit, d ~ N^(1/3)) implies ~3.9x needed. The empirical fact that a fixed d=4096 already shows a substantial drop across this N range is itself evidence AGAINST the cheap log-regime governing this specific discrete/sparse/block-structured code -- meaning doubling (2x) is likely a PARTIAL fix, not sufficient alone, and Donoho-Tanner phase-transition theory warns that landing short of the needed growth near a capacity boundary can leave you on the wrong side of a cliff rather than "halfway recovered." | Retrain at d=8192/K=256, everything else identical, full N. | Medium (2x memory + compute) | **0.35** (partial-fraction-of-gap-closed); **0.10** (closes most/all of gap alone) |
| **4** | **Bigger student / mapping-function capacity** | Distillation "capacity gap" literature almost universally frames this as student-too-weak-to-fit, a DIFFERENT failure mode than a fixed-code ceiling. By data-processing-inequality logic, a bigger encoder can only get closer to whatever the CODE's own ceiling already permits -- it cannot exceed it. The observed degradation pattern (tracks item count, same architecture) looks more like a moving code-ceiling than student underfitting. | FREE pre-check: read whether train/val loss is still descending (underfit) vs. plateaued (ceiling reached) at full N with the CURRENT student -- near-zero cost, should be run regardless of which lever is chosen. | Low (diagnostic) to Medium (architecture change if diagnostic says underfit) | **0.15-0.20** |
| **5** | **Teacher's own geometry as an independent ceiling** | Anisotropy/effective-rank-degradation literature confirms pretrained embeddings concentrate in a narrow angular cone with effective rank well below ambient dimension -- but this is NOT automatically an independent hard ceiling (an unconstrained code at >= teacher dimension could in principle just copy the teacher's geometry, anisotropy included, and still hit near-1.0 correlation). The literature-grounded, defensible version: anisotropy COMPOUNDS with the code's own sparsity/discreteness constraints (fewer effective bits available inside the crowded cone as N grows), rather than being a separate, independent cause. This is why Rank 1 (rank-aware loss, which specifically targets resolution inside the dominant cone) is the top lever, not a coincidence. | Not independently actionable; folds into Rank 1's fix. | -- | **0.20** (as an INDEPENDENT, un-fixable ceiling); folded into Rank 1 as a compounding factor otherwise |

---

## Cheap decisive test (single most important action)

**Bypass-the-student "teacher-to-sparsifier direct" leg -- zero new training, pure inference pass:**

Take the teacher's own dense 1024-d embeddings directly (skip the student network entirely -- no training
required) and pass them straight through the SAME K=128-of-4096 sparsifier used in production, at full
N=177,899. Compute held-out Spearman on that leg alone.

- **If this recovers close to the small-N ceiling (~0.82+):** the code/sparsifier is NOT the bottleneck at
  scale -- the drop is downstream-of-teacher but upstream-of-code, i.e. **student-bound or a training-
  objective artifact** (which may already be substantially addressed by the in-flight NCE fix). This would
  argue AGAINST spending on Ranks 1-3 above and FOR continuing to focus purely on the student/objective side.
- **If this itself collapses to ~0.73-0.74, matching the observed end-to-end number:** that is a clean,
  un-confounded **code-capacity-bound signature**, because the student was never in the loop. This would
  CONFIRM that Ranks 1-3 above (loss reweighting, code-type fix, widening) are the correct next moves.

This is cheaper than training an unconstrained dense probe (which would also require a training run) --
it requires only an inference pass through the existing sparsifier module. **This single test discriminates
the entire decision tree below at near-zero cost and should run in parallel with (or immediately after)
however the in-flight NCE-off FULL run lands.**

**Secondary recommended diagnostic (higher information value, still cheap, second priority):** an
intermediate-N measurement (log-spaced, e.g. N~15,000 and N~50,000, reusing existing infra) to determine
whether the N-vs-fidelity curve is a SMOOTH decline (favors student/teacher/training-artifact explanations,
consistent with distillation capacity-gap scaling-law literature) or a SHARP cliff/knee (favors a genuine
hard code-capacity ceiling, consistent with classical Hopfield/compressed-sensing capacity-transition
literature). Two data points (N=3,000 and N=177,899) cannot distinguish these shapes on their own, and the
literature is unanimous that the two mechanisms have qualitatively different curve shapes -- this is exactly
the kind of information a single extra measurement point resolves cheaply.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

Framed against the bypass-the-student diagnostic (teacher embeddings -> same sparsifier, full N, no
training):

**HARD-PASS (code is NOT the bottleneck; the NCE fix + normal student-side work is sufficient; do NOT
invest in Ranks 1-3 structural levers yet):**
- Teacher-to-sparsifier-direct Spearman at full N=177,899 >= 0.80 (recovers close to the small-N ceiling of
  0.825, confirming the sparsifier itself handles this N fine when fed a clean, already-correct dense
  target).

**HARD-FAIL (code/structure IS a real, independent contributor; Ranks 1-3 above are load-bearing and worth
the investment regardless of how the student/NCE fix lands):**
- Teacher-to-sparsifier-direct Spearman at full N=177,899 <= 0.76 (materially reproduces the ~0.73-0.74
  collapse even with a PERFECT, un-confounded dense target and zero student/training involvement) -- this
  would be the cleanest possible confirmation that the ceiling lives in the sparsifier/code structure itself.

**MIDDLE BAND:** Teacher-to-sparsifier-direct Spearman in [0.76, 0.80) -- partial/ambiguous; some real
code-side cost exists but is not the dominant driver. Recommend running the intermediate-N sweep next
(smooth-vs-cliff diagnostic) before committing to a structural rebuild, and prioritize Rank 1 (loss
reweighting) first regardless, since it is near-zero cost and independently well-supported.

**Separate falsifiable band for the smooth-vs-cliff intermediate-N diagnostic (secondary, if run):**
- **Smooth-decline signature (favors student/teacher/training-artifact):** Spearman degrades roughly
  continuously/log-linearly across N=3k -> 15k -> 50k -> 177,899k, no point showing a sudden drop
  disproportionate to its log(N) step.
- **Cliff signature (favors genuine code-capacity ceiling):** Spearman stays near 0.80-0.825 through an
  intermediate N (e.g. 15k-50k) then drops sharply between two adjacent measured points -- a discontinuity
  larger than the log(N) step would predict from the surrounding points.

---

## Cross-thread synthesis

- **research_drill_encoder_052_to_085_ranked_levers_2026-07-04.md** (same-day prior): ranked the NCE-schedule
  fix as the top lever toward 0.85, with Rank 5 (student capacity) explicitly gated on a free in-sample-
  vs-held diagnostic. THIS drill does not contradict that ranking (the NCE fix is still likely necessary) --
  it adds that the NCE fix is probably NOT SUFFICIENT alone, because a structurally separate, convergent-
  across-4-lit-scans cost (block-code axis misalignment + wrong loss function) sits downstream of the NCE
  issue and has not yet been addressed by anything in that drill's lever list. Ranks 1-2 here (loss
  reweighting, OPQ-style rotation) are NEW levers not present in that drill's ranking at all.
- **research_drill_2x_batch_ratio_match_negative_understanding_2026-07-04.md** (same-day prior, the drill
  that first flagged this cardinality hypothesis): identified the smoke->MID drop (0.825 at V~3k -> 0.36-0.47
  at V=39,515, even at generous batch ratios) as likely co-driven by a raw-cardinality ceiling, citing the
  same Jiang et al. generalized-neural-collapse paper and the same LIMIT paper this drill re-examined in
  depth. THIS drill sharpens that finding considerably: (1) confirms via direct fetch that the LIMIT paper's
  bound is a worst-case/adversarial construction that does not directly transfer at our scale, so the
  "cardinality ceiling" framing from that drill was directionally right but the MECHANISM was likely
  mis-attributed to raw dimensionality rather than to code STRUCTURE/loss-function; (2) resolves the "is the
  drop N-driven or ratio-driven" ambiguity that drill left open, by showing classical continuous-embedding
  theory (JL) predicts almost no N-driven cost at this d, meaning the real driver is structural (block-code
  axis misalignment), not a fundamental N-vs-d wall; (3) provides the missing cheap diagnostic (teacher-to-
  sparsifier-direct leg) that drill's "raw-V sweep at fixed generous ratio" recommendation was gesturing
  toward but did not fully specify.
- **research_drill_sparse_code_semantic_fidelity_frontier_2026-07-04.md** (same-day prior): established that
  varying ACTIVE FRACTION (2% vs 3.1%, i.e. k=82 vs k=128) at fixed/moderate N produces no material fidelity
  gap -- sparsity level per se is not the bottleneck. THIS drill is fully consistent and sharpens the
  boundary of that finding: the earlier drill's verdict holds at MODERATE N (where block-axis-misalignment
  cost has not yet compounded enough to show up as a k=82-vs-k=128 difference); at FULL N=177,899, the
  compounding structural cost (block STRUCTURE and loss function, not the k fraction) becomes the dominant
  lever. This is a refinement, not a contradiction: "sparsity fraction doesn't matter much" and "code
  STRUCTURE/loss-alignment matters a lot at scale" are compatible, adjacent findings about DIFFERENT axes of
  the same code.
- **research_drill_concept_encoder_design_correctness_2026-07-04.md**: established the pre-distillation
  design could not reach 0.85 (P=0.05) and recommended BGE distillation -- the redesign this entire
  investigation operates within. This drill does not reopen that; it operates entirely inside the
  distillation redesign, addressing a residual risk the design-correctness drill flagged as an outer bound
  even after a correct objective is found.

---

## Substrate-product implications

- **No infrastructure change needed for the top two levers.** Rank 1 (rank-aware/anisotropic loss) is a loss-
  function swap; Rank 2's rotation variant (OPQ-style) is a single learned linear map inserted before the
  existing per-block argmax. Neither requires a wider code, a bigger student, or new training infrastructure.
  Both should be staged ahead of any decision to widen the code (Rank 3), which is more expensive and,
  per two independent scaling-law proxies, unlikely to be sufficient alone even if pursued.
- **The single highest-value action before spending more GPU budget is the free bypass-the-student
  diagnostic.** It requires zero training and directly discriminates "the code/sparsifier already handles
  this N fine" from "the code/sparsifier itself needs Ranks 1-3" -- this should run as soon as (or in
  parallel with) reading the in-flight NCE-off FULL result, not after a further round of guessing.
- **This drill downgrades confidence that the cardinality story is a hard, unconditional ceiling.** The
  prior 2x-drill's framing ("a raw cardinality/vocabulary-size ceiling... independent of any batch/objective
  trick") is now more precisely understood as a REAL but STRUCTURAL and LIKELY-FIXABLE cost (code
  axis-misalignment + loss-function choice), not an information-theoretic wall. This is a meaningfully more
  optimistic reframe for the USER strategy decision on whether 0.85 is achievable at all -- it shifts the
  open question from "is there enough room in d=4096 for 177,899 items" (evidence says yes, room is not the
  problem) to "is the current code STRUCTURE and LOSS FUNCTION using that room efficiently" (evidence says
  probably not, and there are near-free fixes to try before concluding otherwise).
- **If the bypass diagnostic HARD-FAILs (code genuinely capacity-bound even with a perfect dense target):**
  that would be the first clean, unconfounded evidence of a real ceiling in this specific code family, and
  would elevate Ranks 1-3 from "worth trying" to "necessary" -- a decision point worth surfacing to the USER
  explicitly rather than continuing to iterate on student/objective-side fixes alone.
- **Two-data-point diagnostic caution should become standing practice for this encoder lineage:** per lit-
  scan D's finding, distinguishing a genuine capacity cliff from a smooth training-artifact decline requires
  at least one intermediate measurement point; future N-scaling claims for this encoder should not rely on
  only the two extreme points (smoke-scale and full-scale) without an intermediate check, mirroring the
  standing scale-ratio-matching discipline already filed for batch-size sweeps.

---

## Per-claim P_deflated (summary)

| Claim | P_deflated | Basis |
|---|---|---|
| 0.85 is reachable via SOME structural lever (not necessarily current code as-is) | **0.45** | Convergent 4-scan evidence against a hard information-theoretic wall; capped as novel cross-domain synthesis. |
| NCE-fix ALONE (current rigid code + reconstruction loss) reaches 0.85 at full scale | **0.20** | Deflated hard; structural cost (axis misalignment + loss mismatch) is convergent across scans and independent of the NCE mechanism. |
| A genuine, hard, N-dependent ceiling exists that no structural lever can fix | **0.15-0.20** | Low; classical "ran out of room" mechanisms (sign-rank worst-case, JL, raw combinatorial count) all argue against a hard wall at this N/d. |
| Rank-aware/anisotropic loss reweighting (Rank 1) meaningfully improves fidelity | **0.50** | Capped; strong, directly-fetched adjacent-domain analog (ScaNN), no source runs our exact setup. |
| OPQ-style rotation before block-WTA (Rank 2) meaningfully improves fidelity | **0.45** (rotation) / **0.30-0.35** (full rebuild) | Directly analogous to well-documented PQ->OPQ literature gain; deflated for extrapolation to our exact code family. |
| Widening code 2x (Rank 3) closes a meaningful fraction of the gap | **0.35** (partial) / **0.10** (closes most/all) | Two disagreeing scaling proxies (2.3x vs 3.9x needed) both exceed the proposed 2x; doubling is directionally right but likely insufficient alone. |
| Bigger student (Rank 4) is the dominant lever | **0.15-0.20** | Capacity-gap literature frames this as a different failure mode; data-processing-inequality argument and observed degradation pattern argue against student capacity being primary. |
| Teacher's own geometry is an INDEPENDENT hard ceiling (Rank 5) | **0.20** | Anisotropy is real but the literature frames it as compounding with code sparsity/discreteness (fixable via Rank 1), not as a separate unfixable wall. |
| The observed drop already shows a genuine sharp-cliff capacity signature (vs. smooth artifact) | **0.20-0.25** | Two data points cannot distinguish shape; literature says the two candidate mechanisms have qualitatively different curve shapes; intermediate-N measurement needed to resolve. |

---

## Citations (verified count)

**4 parallel Sonnet lit-scan sub-agents, ~103 tool-uses total across WebSearch/WebFetch this cycle.**
Load-bearing citations, by lit-scan:

- **Sign-rank / combinatorial capacity (lit-scan A):** Weller, Boratko, Naim, Lee, "On the Theoretical
  Limitations of Embedding-Based Retrieval" (LIMIT paper), arXiv:2508.21038, Google DeepMind, Aug 2025 --
  **VERIFIED via direct fetch of arXiv HTML**, sign-rank theorem and empirical N*(d) cubic-fit table
  extracted directly. Thomas, Dasgupta, Rosing, "A Theoretical Perspective on Hyperdimensional Computing,"
  JAIR 72 (2021): 215-249 -- **VERIFIED via direct fetch** (full paper text), incoherence bound
  mu=O(sqrt(ln m / d)) and polynomial-in-features precision-scaling theorems extracted directly. Johnson-
  Lindenstrauss lemma (Alon tightness result) -- standard reference, confirmed via search aggregation.
  Tsodyks & Feigelman (1988) sparse-Hopfield capacity, Graham & Willshaw (1990) Willshaw-model capacity,
  Kanerva SDM critical-point framing, Cabannes et al. "Scaling Laws for Associative Memories" arXiv:2310.02984
  -- search-snippet/partial-fetch confidence only, flagged by the sub-agent itself.
- **Neural collapse / JL scaling (lit-scan B):** Papyan, Han, Donoho, "Prevalence of Neural Collapse," PNAS
  2020 (background anchor, not re-verified this session). Jiang et al., "Generalized Neural Collapse for a
  Large Number of Classes," ICML 2024, arXiv:2310.05351 -- **verified via fetch, abstract-level**. Wu et al.,
  "Linguistic Collapse: Neural Collapse in (Large) Language Models," arXiv:2405.17767 -- **VERIFIED via direct
  HTML fetch with quoted text**, the load-bearing anchor for the "graceful, not catastrophic" degradation
  shape at vocab>>dim. Liu, Yu, Weller, Scholkopf, "Generalizing and Decoupling Neural Collapse via
  Hyperspherical Uniformity Gap," ICLR 2023, arXiv:2303.06484 -- abstract-level. Clarkson, Ubaru, Yang,
  "Capacity Analysis of Vector Symbolic Architectures," arXiv:2301.10352 -- **verified via fetch, abstract-
  level**, the load-bearing "linear-in-d bundling capacity" analog. Dasgupta & Gupta (1999) JL simplified
  proof -- textbook-standard.
- **Structural levers (lit-scan C):** Guo, Sun, Lindgren, Geng, Simcha, Chern, Kumar, "Accelerating Large-
  Scale Inference with Anisotropic Vector Quantization" (ScaNN), arXiv:1908.10396, ICML 2020 -- **VERIFIED
  via fetch**, the load-bearing anchor for Rank 1. Weller et al. LIMIT paper (as above) -- re-used for the
  d~N^(1/3) cubic-fit extrapolation. Candes RIP, Donoho & Tanner "Precise Undersampling Theorems" Proc. IEEE
  98(6), 2010 -- snippet-level (phase-transition/cliff-not-gradual framing). Babenko & Lempitsky, "Additive
  Quantization for Extreme Vector Compression," CVPR 2014 -- snippet-level. OPQ (Ge et al., rotation-learning
  PQ variant) -- snippet-level, standard method, primary source not independently fetched. Anisotropy cluster
  (arXiv:2401.12143, 2311.05928, 2506.01435, 2604.08764) -- snippet-level.
- **Diagnostic methodology (lit-scan D):** Nelson & Nguyen, "Sparsity Lower Bounds for Dimensionality
  Reducing Maps," arXiv:1211.0995 -- **verified via fetch**, theorem text confirmed. Tamamori, "Geometric and
  dynamical analysis of attractor boundaries and storage limits in kernel Hopfield networks," arXiv:2605.00366
  -- **verified via fetch, abstract**. Williams, "Equivalence between RSA, CKA, and CCA," PMLR v285 (UniReps
  2024) -- **verified via fetch**. Busbridge et al., "Distillation Scaling Laws," arXiv:2502.08606 --
  **verified via fetch** (authors/venue only; specific claim not extractable, flagged snippet-level for that
  claim). Zhang et al., "Towards the Law of Capacity Gap in Distilling Language Models," arXiv:2311.07052 --
  **verified via fetch**. Amit, Gutfreund, Sompolinsky, Phys. Rev. Lett. 55, 1530 (1985), classical Hopfield
  alpha_c~0.138 capacity threshold -- snippet-level, canonical/textbook result. Kornblith et al. original CKA
  paper, arXiv:1905.00414 -- snippet-level. Roy & Vetterli, "The Effective Rank," EUSIPCO 2007 -- snippet-
  level.

**Total distinct sources across all 4 scans: ~45+, of which 9 were independently VERIFIED via direct
WebFetch this session (not merely reported from memory or search-snippet text): arXiv:2508.21038 (fetched
twice, by two different sub-agents, independently corroborating), JAIR Thomas/Dasgupta/Rosing 2021,
arXiv:2405.17767, arXiv:2310.05351, arXiv:2303.06484, arXiv:2301.10352, arXiv:1908.10396, arXiv:1211.0995,
arXiv:2605.00366, PMLR v285 Williams 2024, arXiv:2502.08606, arXiv:2311.07052.** Remainder are title/venue-
level confidence as reported by the sub-agents, explicitly flagged where lower-confidence. None were
independently re-verified a third time by the synthesizing (Director) agent beyond the sub-agents' own
fetch calls; apply the standard discount for that tier of citation confidence per standing lit-scan-
calibration discipline.

---

## Intuitive summary (plain language, 6-10 lines)

Is the 85%-match target even physically possible given how much we're squeezing into a small, sparse code?
Yes, most likely -- four independent literature checks agree there is no "ran out of room" wall here; the
code has vastly more raw capacity than the number of things it needs to tell apart. But the current setup is
probably still leaving real quality on the table for a fixable reason, not an unfixable one: the code is
built like a jigsaw puzzle cut into fixed-size, fixed-position pieces (one "winner" picked per piece), and
outside research shows that kind of rigid cutting pattern loses information whenever the real picture's
important lines don't line up with the piece boundaries -- which they almost certainly don't here. On top of
that, the training is currently graded on "does the redrawn picture look close to the original," when it
should be graded on "does the redrawn picture preserve which pairs of things are more or less alike than
other pairs" -- a subtly different scoring rule that outside researchers already found buys real quality for
free, with no new pieces or bigger pieces needed. The single cheapest next check, costing no training at
all: feed the ORIGINAL (not our student's guess) full-detail picture straight through the same jigsaw-cutting
step at full scale and see how well that comes out -- if it comes out fine, the jigsaw isn't the problem
(something upstream is); if it comes out just as poorly as today's number, that pins the problem squarely on
the jigsaw's cutting pattern and grading rule, exactly where the top two fixes above are aimed.

**Why it matters:** this reframes "maybe 0.85 is just impossible at this scale" (a discouraging, closure-
adjacent read) into "0.85 is probably reachable, but likely needs one or two near-free structural fixes
beyond the in-flight NCE fix, and there's a free test to find out which" -- a meaningfully more actionable
and more optimistic position for the USER strategy decision.
**Near-term decision:** the moment the in-flight NCE-off FULL run lands, run the free bypass-the-student
diagnostic (teacher embeddings straight through the same sparsifier, no training) in parallel with reading
that result -- it costs nothing and immediately tells us whether to invest in Rank 1 (loss reweighting) and
Rank 2 (learned rotation before block selection), both near-free, before considering the more expensive
Rank 3 (widening the code).

ASCII-only. No emojis. No em dashes.
