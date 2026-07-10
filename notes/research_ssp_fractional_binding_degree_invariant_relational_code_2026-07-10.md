# SSP / fractional-binding as a degree-invariant relational code -- construction spec -- 2026-07-10

Self-conducted lit-scan (no sub-agent fan-out, per director's explicit instruction after the 07-08 coordination
stall). WebSearch/WebFetch only, generic math terms, no substrate-novel framing sent off-platform.

## HEADLINE

1. Fractional-binding Spatial Semantic Pointers (SSP) are a **concrete, already-buildable extension of our own
   FHRR algebra** (unit-modulus phasor atoms, phase exponentiation, kernel-similarity readout) with a 30-year VSA
   lineage (Plate -> Komer/Eliasmith -> Frady/Kanerva/Sommer) -- this is not speculative math, it reuses primitives
   already in the codebase.
2. The degree-invariance case is **mechanistically plausible but not proven for discrete graphs**: SSP's
   bounded unit-modulus code + kernel readout structurally blocks the *norm-blowup* channel that drives TransE/
   DistMult degree bias (Shomer et al. 2023), but a knowledge-graph entity has no intrinsic continuous coordinate
   -- you must FIT one from graph structure, which can reopen a degree-correlated *estimation-quality* back door
   that the kernel-form argument does not touch.
3. The dominant risk is the **continuous-vs-discrete mismatch**: SSP/grid-cell literature is proven for physical
   2D/3D space; analogical inference over a discrete, non-spatial knowledge graph via grid-code phase-subtraction
   has never been demonstrated in neural data or in a KGE degree-bias study. Treat this as an open engineering bet,
   gate hard on a stratified retest, do not believe the mechanism story pre-VET.

## 1. The construction: fractional-binding SSP algebra over a KG

**Base vectors (already our primitive).** A base/axis vector is a unit-modulus complex phasor with i.i.d.
random phase per dimension:
`e_j = exp(i * phi_j)`, `phi_j ~ Uniform(0, 2*pi)`, `j = 1..d`.
This is exactly the FHRR "atom" construction already in `hdlab/` (complex64, random-phase unit vectors) -- no new
primitive required, only a new *operation* on existing atoms.

**Fractional binding = phase exponentiation.** For a real-valued (possibly non-integer) scalar `x`:
`S(x) = e^x`, i.e. componentwise `S(x)_j = exp(i * x * phi_j)`.
Integer `x` recovers ordinary repeated self-binding (`e (bind) e (bind) e = e^3`); fractional `x` generalizes the
same operator to a continuous exponent. Modulus is preserved exactly for ANY real `x` (`|S(x)_j| = 1` always) --
this single fact is the crux of the degree-invariance argument in Section 2.
[Komer, Stewart, Voelker & Eliasmith 2019, "A neural representation of continuous space using fractional binding",
CogSci; code: github.com/ctn-waterloo/cogsci2019-ssp]

**Multi-axis composition (for multi-dimensional relation spaces).** Independent continuous axes get independent
base vectors and are composed by elementwise (Hadamard) product:
`S(x, y) = S_A(x) (.) S_B(y) = e_A^x (.) e_B^y`.
Dumont & Eliasmith (2020) show that when axis vectors are the **hexagonal grid-cell basis** (three 60-degree-offset
phase directions per grid module, multiple spatial scales), this composition reproduces measured grid-cell firing
statistics and gives the most accurate place-cell readout of any SSP basis tested -- i.e. the grid-cell code IS
(empirically, in their model) close to the optimal basis for this kind of continuous binding.
[Dumont & Eliasmith 2020, "Accurate representation for spatial cognition using grid cells", CogSci]

**Triple representation.** Place each entity at a continuous coordinate `x_e` in a `k`-dimensional relation-space
(coordinates are LEARNED/FIT from graph structure -- see Section 3, this is the crux of the risk). A relation `r`
is represented as a continuous DISPLACEMENT `delta_r` in the same space (a "movement", not a discrete tag):
`T_r = S(delta_r)`.
A triple `(h, r, t)` is well-formed when
`S(x_h) (.) T_r ~= S(x_t)`  <=>  `S(x_h + delta_r) ~= S(x_t)` (since fractional powers of the same base
multiply/add phases: `e^a (.) e^b = e^(a+b)`).
This is algebraically isomorphic to TransE's `h + r ~= t` **in the exponent domain** -- the crucial difference is
where the addition happens (inside a bounded phase argument, read out through a kernel) rather than in a raw,
unconstrained embedding space read out through a magnitude-sensitive dot product. This is exactly the distinction
Section 2 leans on.

**Held-out inference readout = kernel similarity, not raw dot product.** Given `h` and `r` at test time, compute
the predicted-tail code `S_hat = S(x_h) (.) T_r`, then score every candidate tail `t` by
`k(x_hat, x_t) = Re[<S_hat, S(x_t)>] / d = (1/d) * sum_j cos((x_hat - x_t) * phi_j)`.
Frady et al. (2021) show this is exactly **fractional power encoding (FPE)**, a randomized-feature map whose inner
product is a valid PSD kernel (their "Vector Function Architecture" reframing) -- FPE is the same construction as
Rahimi & Recht's Random Fourier Features (Bochner's theorem: a shift-invariant kernel is the Fourier transform of a
probability measure over frequencies, and the base-vector's phase distribution IS that measure). Nearest-tail
selection is a resonator/cleanup-memory search against a codebook `{S(x_t)}`, not a magnitude race.
[Frady, Kleyko, Sommer et al. 2021, "Computing on Functions Using Randomized Vector Representations", arXiv:2109.03429]

**Unbinding = phase subtraction = the grid-cell goal-vector operation.** Recovering the offset given `S_hat` and
`T_r`:
`S_hat (.) conj(T_r) = S(x_hat) (.) S(-delta_r) = S(x_hat - delta_r)`.
This is precisely the Fourier-shift-theorem operation Bush et al. (2015) propose for grid-cell goal-vector
computation (goal-vector phase = current-location phase MINUS goal-location phase, decoded by correlation across
grid modules of different scale). The user's framing (FHRR unbind = phase subtraction = grid-cell goal-vector op)
is literally this result.
[Bush, Barry, Manson & Burgess 2015, "Using Grid Cells for Navigation", Neuron 87(3)]

This is concrete enough for exp_dev to design a cell from directly: (a) atom construction is the existing FHRR
primitive; (b) fractional bind is one new op (`torch.exp(1j * x * angle(base))`, closed form, no iteration); (c)
scoring is a kernel/cleanup-memory lookup, not a new scoring head; (d) unbind is the existing conjugate-multiply
op applied to a continuous-exponent code instead of a discrete one.

## 2. Why this WOULD be degree-invariant where TransE isn't -- and the honest limit of that argument

**The mechanistic case.** Shomer et al. (2023), "Toward Degree Bias in Embedding-Based Knowledge Graph
Completion" (WWW 2023 / arXiv:2302.05044), empirically validate that high-degree nodes are learned "substantially
better" than low-degree nodes across MULTIPLE KGE families (translational TransE and bilinear DistMult both show
it) -- i.e. this is not a TransE-specific quirk, it recurs whenever entity/relation vectors are FREE PARAMETERS fit
by gradient descent against triple counts: high-degree entities get more gradient signal, and (per our own
retest's smoke preview) that shows up as norm/effective-magnitude differences a dot-product score rewards.
Fractional-binding SSP structurally removes exactly ONE channel for this: every `S(x)` has EXACTLY unit modulus
per component for ANY `x`, by construction, not by regularization -- there is no "learn a bigger vector because
you were seen more often" degree of freedom inside the binding algebra itself, and the readout is a bounded kernel
similarity (bounded in `[-1, 1]` per Section 1), not an unbounded dot product that a larger-norm embedding can win
by brute magnitude.

**The honest limit.** This argument is about the SCORING FORM, not about the ENTITY COORDINATES. If `x_h` and
`x_t` are themselves fit as free parameters against the SAME observed triples (which they must be, for a discrete
KG -- see Section 3), the popularity shortcut can re-enter through the back door: high-degree entities still get
more gradient signal to estimate a good coordinate; low-degree entities get noisier placement. The kernel-form
argument blocks the norm-blowup channel; it does **not** automatically block a coordinate-estimation-quality
channel correlated with degree. Hubness -- the tendency for a few points to dominate many others' nearest-neighbor
lists -- is documented as an INTRINSIC property of high-dimensional metric spaces in general (Radovanovic,
Nanopoulos & Ivanovic 2010 and follow-on hubness-reduction literature), not specific to dot-product scoring, so a
kernel-similarity nearest-neighbor readout is not automatically immune if the underlying coordinate ESTIMATION is
what carries the bias. **Do not manufacture the degree-invariance answer**: the literature supports "SSP removes
one known bias channel," not "SSP is degree-invariant on discrete KGs" -- that second claim is untested.

**A biological existence proof for the RIGHT polarity (suggestive, not proof).** The transitive-inference
literature's "terminal item" / "end-anchor effect" (items with FEWER, more unambiguous associative pairings are
recognized MORE easily and MORE accurately than intermediate, higher-degree items -- e.g. at symbolic distance 5,
100% of test pairs contain a terminal/end anchor vs 40% at distance 1, and terminal-item trials show higher
accuracy) is the OPPOSITE polarity from a popularity shortcut: low-associative-degree items are FAVORED, not
penalized. Lippl et al.'s (2024, PNAS) mathematical theory frames this as arising from norm-minimization pressure
toward a low-conjunctivity, ADDITIVE, item-wise (rank-based) representation -- generalization comes from a
computed geometric RANK, not memorized associative frequency. This is a real biological result that a
geometric/ordinal code CAN structurally favor low-degree items; it is an analogy (their result is for a strict
1D linear order, not a general multi-relational graph) and should be read as consistent-with, not confirmation-of,
the SSP hypothesis.

## 3. Honest risks

- **Dimensionality vs graph size.** FPE/SSP capacity is governed by how many distinguishable "kernel bumps" fit in
  `d` dimensions before cleanup/resonator-network crosstalk degrades recovery; no source surfaced in this scan
  gives a graph-size-scaled rule (entities x average degree -> required `d`) for a discrete relational graph --
  the closest published capacity analyses (Resonator Networks I/II, Frady/Kent/Olshausen/Sommer 2020, Neural
  Computation) are for factoring a SMALL fixed number of bound discrete factors, not for placing thousands of
  entities at distinguishable continuous coordinates. This is an open, unpublished engineering unknown for our
  scale, not a solved parameter.
- **Kernel-bandwidth choice is an untuned free hyperparameter.** Frady et al. (2021) state the base-vector phase
  DISTRIBUTION determines the FPE kernel's shape (narrow phase spread -> wide/flat kernel, can't discriminate
  nearby entities; wide phase spread -> narrow/near-delta kernel, degenerates to discrete lookup and loses the
  smooth-generalization benefit that motivates this whole hypothesis). No principled, graph-size-derived selection
  rule was found. Any cell built from this MUST pre-register the bandwidth before seeing held-out results, or the
  "degree-invariant" verdict is untrustworthy by construction (post-hoc-tuned kernel).
- **The central risk: continuous-vs-discrete mismatch.** SSP/fractional binding was built and empirically
  validated for physical 2D/3D continuous space, where "the coordinate of a thing" has intrinsic pre-existing
  meaning (a place in a room). A KG entity ("Paris", "mitochondria") has NO intrinsic continuous coordinate --
  one must be manufactured via an auxiliary embedding-fitting step (e.g., spectral/Laplacian embedding, or a
  learned coordinate via SGD against the graph). That fitting step reintroduces exactly the frequency-sensitive
  estimation dynamic that produces TransE's popularity artifact in the first place (Section 2's honest limit).
  Corroborating this: **HolE** (Nickel, Rosasco & Poggio 2016, "Holographic Embeddings of Knowledge Graphs") is
  the closest EXISTING discrete analog -- circular-correlation/multiplicative composition (same VSA family as
  FHRR bind) applied directly to discrete KG relations, later shown algebraically equivalent to ComplEx (Hayashi &
  Shimbo 2017). If a multiplicative/holographic binding operator by itself cured degree bias, HolE/ComplEx would
  show it -- but Shomer et al.'s (2023) degree-bias audit explicitly spans "multiple KGE model families," and
  bilinear/holographic-family models are NOT reported as escaping the pattern. **The literature gives no evidence
  that swapping the binding operator (additive vs multiplicative/circular-correlation vs continuous-fractional)
  by itself fixes degree bias for discrete, non-spatial graphs** -- the fix, if there is one, has to come from
  HOW coordinates get assigned, not from the binding algebra alone.
- **Grid-cell-scan caveat (carried forward as instructed).** No neural-recording study demonstrates analogical or
  relational inference over a discrete, non-spatial knowledge graph via grid-cell-style phase subtraction. Bush et
  al. (2015), the 2018 Nature vector-navigation work, and later structural work (e.g. Whittington et al.'s
  Tolman-Eichenbaum-Machine line) all operate on literal or embedded-as-continuous physical/task manifolds. Their
  extension to abstract, discrete, multi-relational-type KGs is a theoretical extrapolation the field itself has
  not closed -- consistent with our own prior finding (`research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`)
  that the brain's mechanism for novel relational inference is comparison/alignment producing an additive-geometric
  or schema-slot code, not literal grid-arithmetic over discrete relation types.

## 4. Falsifiable prediction skeleton (reusing the retest's controls; NOT a cell design)

Reuse the exact scaffolding from `preregs/2026-07-10_grounding_additive_geometric_degree_control_retest_v1.md`:
same completable held-out split, same LOW/MID/HIGH degree tertiles (data-driven quantiles of visible-graph
degree), same `POPULARITY_DEGREE` baseline arm, same `RANDOM_CODES` null, same transductive-oracle must-fire
check, same DistMult-style convergence sanity check.

**New arm to add:** `SSP_FRACTIONAL` -- entities placed at continuous coordinates via a coordinate-fitting step
performed on the VISIBLE graph only (e.g. spectral/Laplacian embedding, pre-registered before seeing held-out
splits); relations as fitted continuous offsets (`delta_r`) on visible edges only; scored via kernel similarity
per Section 1. Alongside it, add a **coordinate-precision-vs-degree diagnostic**: measure per-entity coordinate
variance/instability across seeds and correlate it with entity degree. This directly tests Section 2's "honest
limit" (estimation-quality back door) rather than inferring it.

**HARD-PASS SSP_DEGREE_INVARIANT** (all must hold):
- aggregate margin over `DISCRETE_HRR_BIND` clears a materiality bar (reuse `GEOM_MARGIN`-equivalent),
- `SSP_FRACTIONAL` margin over `POPULARITY_DEGREE` survives in BOTH LOW and MID strata at >= `STRAT_MARGIN`,
- **flatness check** (the genuinely new bar): `|reach@1_HIGH - reach@1_LOW| <= 0.05` for `SSP_FRACTIONAL`
  specifically -- degree-invariant means FLAT across strata, not merely "less bad than TransE" in the tail,
- popularity does not recover (`pop/ssp <= 0.60`, same logic as `POP_RECOVER_FRAC_MAX`),
- coordinate-precision-vs-degree correlation is NOT significant (r < 0.2) -- if it IS significant, the back door
  from Section 2 is open and any aggregate win is suspect regardless of the flatness check.

**HARD-FAIL SSP_INHERITS_SHORTCUT**:
- `SSP_FRACTIONAL` margin over discrete/popularity collapses in LOW or MID stratum (`<= TIE_EPS`), matching
  TransE's failure mode, OR
- popularity recovers (`pop/ssp >= 0.80`), OR
- coordinate-precision correlates significantly with degree (r >= 0.4) even if aggregate margin looks fine --
  this is the "back-door" fail: it means any apparent win is riding the same estimation-quality channel as TransE,
  just laundered through a kernel.

**MIDDLE-BAND**: SSP beats popularity in aggregate but fails the flatness check (tail-vs-head gap persists, just
smaller than TransE's); OR the kernel bandwidth needed to make entities distinguishable at this graph's scale is
so wide that resolution collapses (kernel-degenerates-to-near-uniform, distinguishable from a genuine
degree-invariance failure -- a capacity/dimensionality problem, not a mechanism problem).

**Oracle/null controls carried over**: `RANDOM_CODES` (scrambled coordinates, same kernel machinery) must fail
near-chance -- proves the GEOMETRY carries the signal, not the kernel math alone; transductive-`SSP_FRACTIONAL`
(train+test on visible split) must fire well above random, proving the construction is functional before judging
its inductive/degree behavior.

## Cross-thread synthesis

- Directly downstream of tonight's decisive degree-control retest (`grounding_additive_geometric_degree_control_v1`,
  smoke preview `HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT`, dispatched 2026-07-10 13:27 UTC, FULL pending): this
  note is the concrete next-build regardless of that verdict, per the director's framing -- if additive/global
  TransE is confirmed a popularity shortcut, this is the alternative geometric hypothesis to test next; if the
  retest instead lands MIDDLE_BAND or reverses, this note is still the right next drill because the flatness/
  coordinate-precision diagnostics it proposes are strictly MORE informative than the current controls either way.
- Converges with `research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md`: both threads
  independently surface Lippl et al. (2024, PNAS) as the load-bearing brain-mechanism citation for a compositional,
  additive/low-conjunctivity geometric code -- that note used it to argue relation-TYPE richness matters for
  inductive reach; this note uses its end-anchor-effect corollary to argue the SAME family of codes can be
  degree-favoring-of-the-rare rather than degree-biased-toward-the-popular. These are complementary, not
  competing, readings of the same paper.
- Distinct from `research_degree_agnostic_sparse_tail_relational_encoding_brain_first_2026-07-08.md` (DG-expansion
  pattern-separation front end for degree-0/1 items): that mechanism achieves degree-agnosticism through SPARSE
  CODING GEOMETRY (expand-then-sparsify, no neighbors needed); this note's mechanism achieves it (if it works)
  through CONTINUOUS KERNEL GEOMETRY (bounded phase code, smooth similarity). They are not mutually exclusive --
  a future build could combine a DG-style sparse front end for placement with an SSP-style continuous kernel for
  the relational read-off -- but that composition is out of scope here and should not be pre-designed.

## Substrate-product implications

If the HARD-PASS band is met, this becomes the substrate's specific answer to "can the machinery generalize to
rare/novel relational facts as well as it does to famous ones" -- a real capability differentiator versus any
standard KGE approach, since Shomer et al.'s audit suggests the popularity shortcut is endemic across the
mainstream KGE families we'd otherwise be compared to. If HARD-FAIL, the negative is still valuable: it would
show that swapping the geometric FORM of relational binding is not suffient on its own, redirecting effort toward
the coordinate-ASSIGNMENT problem (how entities get placed) or back to the knowledge-richness axis from the
07-09 note. Either way this is a machinery lever, not a training-data lever, so it composes with (does not
replace) the ingest-completeness / relation-vocabulary work already in flight.

## Cheap decisive test

Before committing to the full stratified cell above: a same-day CPU-only smoke check that the coordinate-
precision-vs-degree correlation diagnostic alone fires or doesn't, using the EXISTING retest's harness and
graph (swap only the arm's coordinate-fitting step in for the current `TRANSE_ADDITIVE` arm, reuse everything
else). If coordinate precision already correlates strongly with degree at smoke scale, the back-door risk in
Section 2/3 is confirmed cheaply and the full flatness-check cell can be deprioritized in favor of the
knowledge-richness direction instead.

## Citations (verified count: 14, all located via WebSearch/WebFetch this session)

1. Komer, Stewart, Voelker & Eliasmith (2019). "A neural representation of continuous space using fractional
   binding." CogSci 2019. (compneuro.uwaterloo.ca/files/publications/komer.2019.pdf)
2. Dumont & Eliasmith (2020). "Accurate representation for spatial cognition using grid cells." CogSci 2020.
3. Frady, Kleyko, Sommer et al. (2021). "Computing on Functions Using Randomized Vector Representations."
   arXiv:2109.03429.
4. Frady et al. (2024). "Improved Cleanup and Decoding of Fractional Power Encodings." arXiv:2412.00488.
5. Bush, Barry, Manson & Burgess (2015). "Using Grid Cells for Navigation." Neuron 87(3).
6. Plate (1995). "Holographic Reduced Representations." IEEE Transactions on Neural Networks.
7. Nickel, Rosasco & Poggio (2016). "Holographic Embeddings of Knowledge Graphs." AAAI 2016.
8. Hayashi & Shimbo (2017). "On the Equivalence of Holographic and Complex Embeddings for Link Prediction."
   arXiv:1702.05563.
9. Shomer et al. (2023). "Toward Degree Bias in Embedding-Based Knowledge Graph Completion." WWW 2023 /
   arXiv:2302.05044.
10. Lippl, Kording et al. (2024). "A mathematical theory of relational generalization in transitive inference."
    PNAS 121(28) / bioRxiv:2023.08.22.554287.
11. Radovanovic, Nanopoulos & Ivanovic (2010) and follow-on hubness literature -- hubness as an intrinsic
    high-dimensional-space phenomenon (surfaced via secondary search results on hubness reduction).
12. Rahimi & Recht random Fourier features / Bochner's theorem -- surfaced as the named equivalence to FPE in
    Frady et al.'s framing ("FPE also referred to as Random Fourier Features").
13. Resonator Networks I & II (Frady, Kent, Olshausen & Sommer, 2020, Neural Computation) -- discrete
    combinatorial factorization capacity, cited for the dimensionality/capacity risk.
14. Terminal-item / end-anchor-effect transitive-inference literature (symbolic-distance-effect studies in
    rhesus macaques and humans; PMC3774320 and related) -- cited for the low-degree-favoring polarity claim.

P_construction (algebra is correct and buildable): ~0.90 (established VSA math, not novel synthesis, no
calibration penalty applies).
P_degree_invariance_on_discrete_KG (the load-bearing NEW claim): base ~0.35, deflated 0.20 per
[[feedback-lit-scan-calibration-penalty]] (uncharted regime: no published precedent tests fractional/kernel
binding specifically for KGE degree bias) -> **P_deflated = 0.28** (already under the 0.50 novel-synthesis cap).
