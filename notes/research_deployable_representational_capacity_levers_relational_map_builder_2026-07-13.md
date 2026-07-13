# Research: deployable representational-capacity levers for the relational map-builder's recoverable-signal ceiling

Date: 2026-07-13. Synthesis over 3 parallel Sonnet lit-scans (brain-grounded expansion/sparse-coding capacity
mechanisms; VSA/HDC sparse-block/sharded-FHRR/resonator capacity-vs-cost; product/factored-code + compressed-sensing
capacity-vs-cost), brain-first per mission order, generic math/neuroscience search terms only, no substrate-specific
names/numbers sent off-platform.

**Question posed:** what deployable representational-capacity lever raises the relational map-builder's
recoverable-signal CEILING without the O(n_dim^2) cost that makes naive high-dimension undeployable. Given (not
re-derived, per instruction): raising effective dimension moved an oracle ceiling 0.023 (1024-dim) -> 0.78 (8192-dim)
but at O(n_dim^2) cost; current representation is fixed-atom ~1024-dim VSA (bipolar/complex-phase FHRR) with low-rank
(k=24) relational coordinates; realized capability is weak (~0.13 MRR / 0.28 Hits@10 held-out-entity link prediction).

---

## HEADLINE

**The single mechanism that is BOTH brain-confirmed AND already operationalized as a published VSA construction is
residue-number-system (RNS) / Chinese-Remainder-Theorem (CRT) multi-module combinatorial coding — the same principle
the grid-cell system uses.** Across all three lit-scans, every mechanism that raises capacity while staying provably
sub-quadratic falls into one of two families: (a) **combinatorial/multiplicative** — capacity is the PRODUCT of
several small independent factors while cost is only their SUM (grid-cell multi-module code; RNS/CRT high-dimensional
coding; low-rank/Kronecker factorization), or (b) **decode-side** — a fixed representation's PRACTICAL recoverable
capacity is raised by a better (still closed-form) readout algorithm without touching the representation's dimension
at all (resonator-network iterative factorization; block-code factorized search). Family (a) is the direct answer to
"raise the ceiling without O(n^2)"; family (b) is a complementary, orthogonal lever that stacks with (a) or with a
dimension bump.

**Grid-cell code, brain-side (Sreenivasan & Fiete 2011, Nat. Neurosci.):** multiple grid modules at different spatial
periods jointly encode position as a residue/CRT-like construction. Capacity scales as the PRODUCT of module periods
(exponential in module count) while neuron/module count grows only LINEARLY — modules combine via CRT decoding, not
via pairwise/recurrent connectivity, so there is no hidden quadratic term. This is the cleanest brain-side capacity
mechanism found in this drill — genuinely O(N) resource for exponential representable range.

**VSA-side, already published (Frady, Kleyko et al., "Computing With Residue Numbers in High-Dimensional
Representation," Neural Computation 37(1), 2025, arXiv:2311.04872):** operationalizes the identical idea directly as
a vector-symbolic construction — encode an item as its residues modulo several small, pairwise-coprime moduli;
dynamic range (representable capacity) is the PRODUCT of the moduli, while compute/storage is the SUM of small
per-modulus codebooks. This is not a novel-synthesis leap for this drill to propose — it is an already-existing,
already-published mechanism that directly targets the stated problem (raise ceiling, avoid O(n^2)), with the brain
mechanism as independent grounding for WHY it should work, not merely an analogy invented after the fact.

**Contrast with the naive dimension-increase lever the mission cites as the proven-but-undeployable baseline:** raw
dimension scaling buys `SNR ~ sqrt(N/M)` (linear-ish SNR gain, well-precedented, but full O(n_dim^2) write/read cost
at the monolithic-matrix level, confirmed independently by two of this session's sibling drills on the native store
and the additive map-builder). RNS/CRT multi-module coding instead buys MULTIPLICATIVE range growth from ADDITIVE
resource growth — a genuinely different scaling class, not just a constant-factor improvement on the same curve.

**GO/NO-GO read: GO, with deflation.** The mechanism is real, brain-confirmed, and already published as a VSA
construction — but its transfer to THIS map-builder's specific task (relational link-prediction with low-rank
coordinates, not the pure high-dimensional pattern-recognition setting the grid-cell/RNS-HDC literature was built
for) is untested. **P_deflated = 0.35** for "RNS/CRT multi-module recoding raises the map-builder's oracle-ceiling
metric by >=2x at matched or lower total compute vs. the monolithic-dimension baseline" (capped under the
novel-synthesis rule for the specific transfer, not for the underlying mechanism's soundness, which is
well-established).

---

## Ranked deployable capacity levers

| # | Lever | Mechanism (1-2 lines) | Brain grounding | Ceiling-lift direction | Cost scaling (why deployable) | Glass-box | One-line test |
|---|---|---|---|---|---|---|---|
| 1 | **RNS/CRT multi-module residue coding** (LEADING CANDIDATE) | Split the atom/relation code into K small, pairwise-coprime-cardinality modules; represent/reconstruct via CRT. Capacity = product of module ranges; cost = sum of module dims. | Grid-cell multi-module combinatorial code (Sreenivasan & Fiete 2011) — capacity multiplicative, resource linear, no recurrent/pairwise cost | Multiplicative/exponential in module count, at fixed or lower total dimension than the monolithic 8192-dim run | O(K * d_k) where d_k << n_dim per module — sum, not product, of module costs; total footprint can be smaller than one monolithic 8192-dim vector | Yes — fully closed-form (CRT decode), zero learned parameters | Re-run the existing oracle-ceiling cell with atoms/relation-coords encoded as K=4-8 residue modules of small coprime cardinality instead of one monolithic n_dim vector; compare oracle-ceiling metric at matched total parameter count vs. the 1024-dim and 8192-dim monolithic runs |
| 2 | **Sparse Block Codes (SBC) + Block-Code Factorizer decode** | Split a D-dim vector into B blocks, one active unit per block (product-code structure); factorized resonator search drops decode cost from O(Di*Do) to O(Di*sqrt(Do)) | Weak/moderate — echoes cerebellar granule-layer AND cortical columnar modularity, not a tight direct citation (flagged honestly) | Empirically more noise-robust than dense bipolar codes at large problem sizes (operational capacity ~5x10^6 vs. degraded dense in the cited benchmark); no formal proof found that blocking alone raises capacity vs. monolithic at EQUAL total dimension | Sub-quadratic search cost via block/product-code factorization (Hersche et al. 2023/2025, arXiv:2303.13957) | Yes — deterministic block/one-hot code + fixed factorized search, no gradient training | Swap the current monolithic atom code for a B-block one-hot-per-block code and re-run the same oracle-ceiling/factorized-decode metric, holding total footprint fixed |
| 3 | **Resonator-network iterative factorized decode as a capacity multiplier at FIXED dimension** | Iteratively factor a superposed/bound code into components rather than one-shot decode; raises practical recoverable capacity (M_max) substantially at unchanged N | Weak-direct (predictive-coding / iterative error-correction analogy, already flagged in a sibling drill this session) | ~2 orders of magnitude higher operational capacity (M_max) vs. one-shot decode baselines (ALS/gradient) at fixed N, per Kent/Frady/Sommer/Olshausen (arXiv:1906.11684 Part 2) | Cost per iteration O(F * N * D_max), small fixed iteration count (5-7) — linear in dimension times factor-codebook size, not O(n_dim^2) | Yes — deterministic fixed-point iteration, reuses the substrate's own existing SIC-peel-family primitive | Already partially in flight via this session's SIC-peel lever (sibling drill); this drill's marginal contribution is reframing it explicitly as a CEILING lever (not just an accuracy lever) — no new cell needed beyond what is already proposed |
| 4 | **Kronecker-structured codebook clean-up** | Replace a monolithic O(N) codebook clean-up/readout with a Kronecker-rotation-product structure | None direct found (flagged honestly) | Claims capacity "comparable to standard codebooks" while codebook storage drops to O(log N) (Liu, Qiu, Khan & Katz, arXiv:2506.15793, NeSy 2025) | O(N log N) clean-up time, O(log N) codebook storage — attacks the READOUT/codebook-search side of the O(n^2) problem specifically, complementary to lever 1's representation-side fix | Yes — closed-form rotation-product structure, zero training | Swap the codebook clean-up step for the Kronecker-rotation variant and check whether the oracle ceiling holds at a much larger effective codebook size for the same compute budget |
| 5 | **DG/cerebellar-style fixed sparse-expansion front-end (small fixed in-degree)** | Widen the code via a sparse random expansion where each expanded unit samples only a small, FIXED number of inputs (no recurrence) | Cerebellar granule-cell layer (~100-200x expansion, ~4 inputs/granule cell, Marr-Albus; Cayco-Gajic & Silver) and DG pattern separation (Babadi & Sompolinsky) | Genuinely linear-cost capacity multiplier on the CODE side — but brain evidence shows combinatorial diversity SATURATES (short-dendrite sampling limits, Cayco-Gajic/Silver 2019) — a real, citation-backed caveat, not a hedge | O(1) fan-in per expanded unit -> total cost linear in expanded-unit count, no hidden quadratic recurrent term (unlike DG's own downstream CA3 stage, which stays O(N^2) in CA3 units regardless of how sparse the DG input is) | Yes — a wiring change; this substrate already has an unwired, built primitive for it (flagged in a sibling drill this session, `DGProjection`) | Wire the existing sparse-expansion primitive ahead of the atom/relation code before binding, and check whether the oracle ceiling moves at fixed total downstream dimension — cheapest lever to test (wiring only) but weakest expected magnitude per the saturation caveat |

**Explicitly deprioritized / cautionary, not ranked above:** raw tensor-product binding (Smolensky 1990) is a
cautionary counter-example, not a lever — its cost grows as the PRODUCT of role and filler dimensions (quadratic in
disguise) unless later re-factored/compressed; Kronecker-product EMBEDDING compression (as opposed to the clean-up
variant in lever 4) shows real accuracy loss (~26% on large NLP tasks per one cited ablation) when the target
function does not actually factor along the chosen axes — a genuine risk to flag for lever 1 and lever 4 both:
if the map-builder's true relational structure does not factor cleanly across residue moduli or Kronecker blocks,
these levers could underperform a monolithic representation despite the favorable asymptotic scaling law.

---

## Cheap decisive test

**Leading candidate: `map_builder_residue_module_ceiling_v1`.** Re-run the existing oracle-ceiling diagnostic cell
(the same one that produced the 0.023 -> 0.78 dimension-sweep result cited in the mission) with ONE change: replace
the monolithic n_dim atom/relation-coordinate representation with a K-module residue/CRT code (K=4-8 modules, each a
small pairwise-coprime-cardinality codebook), holding TOTAL parameter/compute budget matched to (a) the 1024-dim
monolithic baseline and (b) a mid-point budget well below the 8192-dim monolithic run's O(n^2) cost. Reuse the
existing oracle-ceiling harness and metric verbatim — no new evaluation machinery, only the atom/relation-code
construction changes.

**Secondary, cheap-to-bundle arm:** swap only the codebook clean-up/readout step for the Kronecker-rotation variant
(lever 4) while leaving the monolithic representation unchanged, to isolate whether the O(n^2) bottleneck is
primarily on the representation side (lever 1 territory) or the readout/codebook-search side (lever 4 territory) —
these are not mutually exclusive and stacking both is plausible.

### Falsifiable predictions

**HARD-PASS (RNS/CRT multi-module coding is a genuine deployable ceiling lever):**
1. Oracle-ceiling metric at the K-module residue code, matched total compute to the 1024-dim monolithic baseline,
   reaches **>= 2x** the 1024-dim monolithic oracle ceiling (i.e. moves meaningfully toward the 0.78 figure the
   8192-dim monolithic run achieved, without paying that run's O(n^2) cost).
2. A must-fail control (scramble the residue-to-atom mapping / permute moduli assignment) collapses back toward the
   1024-dim monolithic floor — confirms the lift is from the CRT/residue STRUCTURE, not merely from having more raw
   parameters scattered across modules.
3. Measured wall-clock / FLOP cost at the tested K stays sub-quadratic in the EFFECTIVE total dimension (K * d_k),
   confirmed empirically, not merely assumed from the closed-form cost model.

**HARD-FAIL (redirect priority to decode-side levers, 3/4, or accept the monolithic-dimension cost as unavoidable):**
1. Oracle-ceiling metric gain is **< 1.3x** at matched compute budget — the multiplicative-capacity theory (built for
   pure pattern-recognition/positional codes) does not transfer to this map-builder's specific relational/low-rank-
   coordinate task structure.
2. The true relational structure does not factor cleanly across residue moduli (per the Kronecker-embedding
   cautionary finding above) — diagnosable by checking whether the RECONSTRUCTED oracle-ceiling metric is
   SYSTEMATICALLY worse on entities/relations whose signal is concentrated in a single module vs. spread evenly.
3. If HARD-FAIL: this is still informative — it would mean the map-builder's ceiling is tied to genuinely
   high-dimensional entangled structure that RNS/CRT-style factoring cannot cleanly separate, sharpening the
   remaining bet toward lever 3 (resonator iterative decode, already partially in flight this session) or accepting
   that the O(n^2) dimension-increase cost is the only currently-known route to the 0.78 ceiling.

**Middle band (gain in [1.3x, 2x)):** sweep K (module count) and per-module cardinality independently — if gain
scales with K in the predicted multiplicative direction, the lever works but needs more modules/compute to fully
close the gap (a scaling finding, not an architecture failure); if gain is flat across K, the bottleneck is
elsewhere (likely readout, redirecting to lever 4).

**P_deflated:** lever 1 (leading) = 0.35; lever 2 (SBC) = 0.25; lever 3 (resonator decode, already-known direction)
= 0.30 (consistent with sibling drill this session); lever 4 (Kronecker clean-up) = 0.25; lever 5 (DG/cerebellar
sparse front-end) = 0.20 (saturation caveat pulls this down from where a naive read of "brain does this" would
place it).

---

## Cross-thread synthesis

- **Genuinely new relative to this session's three sibling 07-13 drills** (`research_native_representational_
  ceiling_levers_2026-07-13.md`, `research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md`,
  `research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md`): none of those three proposed a
  REPRESENTATION-level structural change (residue/CRT multi-module coding). They ranked write-rule decorrelation
  (pseudo-inverse/Storkey), reciprocal-edge bundling, sequential SIC-peel, and hard-negative scorer refit — all
  either write-side or decode/bundle-side levers operating on the EXISTING monolithic-dimension representation. This
  drill's lever 1 is orthogonal and stackable: it changes what the atoms/relation-coordinates ARE, not how they are
  written or read back out. Lever 3 in this drill (resonator iterative decode) is NOT new — it directly reinforces
  the SIC-peel lever already ranked #1 in `research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md`
  and lever 3 there — this drill adds the explicit reframe that the SAME mechanism is also a CEILING lever (raises
  the oracle's own achievable ceiling), not merely a realized-accuracy lever, which is a useful sharpening but not a
  new candidate.
- **Directly extends the grid-cell citation already surfaced but not built on** in
  `research_inductive_map_builder_best_in_class_magnitude_levers_2026-07-13.md`'s Lever 6 discussion (grid-cell/TEM
  factorized rebinding, there deprioritized for a DIFFERENT reason — that note was asking about generalizing
  relational STRUCTURE across graphs, not raising the representational CEILING; this drill asks the ceiling
  question directly and finds the grid-cell mechanism answers THIS question well even though it did not answer that
  one).
- **Connects to the standing relational-capability program spine**
  (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): that thread's core
  diagnosis is that the brain's ADDITIVE/GEOMETRIC codes (relations-as-directions) are degree-invariant in a way the
  current discrete HRR-bind regime is not. RNS/CRT multi-module coding is a DIFFERENT axis (capacity, not
  relational-generalization) but shares the same brain-grounding discipline of "look at what makes the brain's
  combinatorial codes cheap, not just what makes them big" — worth flagging to that thread as a second, orthogonal
  brain-grounded lever family, not a replacement for the additive/geometric-code diagnosis already made there.
- **Consistent with, does not contradict,** the standing `reference_correlation_hurts_associative_store_capacity_
  decouple_from_retrieval_2026-07-08.md` finding — residue/CRT modules are, by construction, DECORRELATED from each
  other (different moduli, independent residues), which is the same direction that finding already recommends;
  this drill's lever 1 can be read as a concrete structural mechanism for achieving that decorrelation, not a new
  or competing claim.

---

## Substrate-product implications

- **This is a construction-proof risk, not yet a capability win.** Nothing here should be read as "the ceiling
  problem is solved" — it is a ranked, falsifiable plan for whether a genuinely cheaper scaling class (multiplicative
  capacity from additive resource growth) can substitute for the proven-but-undeployable O(n^2) dimension increase.
  The cheap decisive test reuses the EXISTING oracle-ceiling harness verbatim, so the cost of finding out is low
  relative to the strategic value of the answer either way.
- **If lever 1 HARD-PASSes:** this would be a genuine architectural differentiator — "our relational memory's
  capacity ceiling scales combinatorially with a linear resource budget, the same principle the brain's spatial
  navigation system uses to represent an enormous range of positions with a small number of neurons" is a
  substantially stronger and more specific claim than "we made the vectors bigger." It would also generalize: any
  future capacity need would be met by adding a small additional module (linear cost) rather than by re-paying an
  O(n^2) tax on a monolithic vector each time.
- **If lever 1 HARD-FAILs:** still valuable, not a dead end — it would establish that this map-builder's specific
  relational/low-rank task structure does not decompose cleanly across independent residue moduli (a genuine,
  currently-unknown fact about the task, not an architecture failure), redirecting fully to the decode-side levers
  (3/4, already partially in flight) or to accepting the O(n^2) dimension-increase cost as the only currently-known
  route to the 0.78 ceiling for cases where that cost is affordable (e.g. periodic offline re-indexing rather than
  live per-query cost).
- **Either outcome sharpens, rather than muddies, the standing question:** this drill converts "is there a cheaper
  way to raise the ceiling" from a diffuse hope into one concrete, falsifiable, already-literature-grounded
  mechanism with a clear pass/fail bar, reusing existing infrastructure.

---

## Citations (verified count)

**Brain-grounded capacity mechanisms (10):** Marr (1971), archicortex/DG theory. Treves & Rolls (1991, *Network*),
sparse autoassociative capacity formula C ~ N/(a*ln(1/a)). Babadi & Sompolinsky (2014, *Neuron*), sparse expansion
recoding. O'Reilly & McClelland (1994), complementary learning systems. Marr (1969)/Albus (1971), cerebellar granule
layer expansion-coding theory. Cayco-Gajic, Clopath & Silver (2017, *Nature Communications*), granule-cell
decorrelation. Cayco-Gajic & Silver (2019, *Neuron*), combinatorial-diversity saturation from dendritic sampling
limits. **Sreenivasan & Fiete (2011, *Nature Neuroscience*), grid-cell multi-module residue/CRT-like capacity code
— the primary brain-side citation for lever 1.** Teyler & DiScenna (1986, *Behavioral and Neural Biology*),
hippocampal indexing theory (qualitative, no verifiable quantitative law found — flagged honestly).

**VSA/HDC capacity-vs-cost mechanisms (9):** Knoblauch, Palm & Sommer (2010, *Neural Computation*), sparse binary
associative-memory capacity. Amit, Gutfreund & Sompolinsky (1985, *Phys. Rev. Lett.*), dense Hopfield ~0.14N bound.
Clarkson, Ubaru & Yang, "Capacity Analysis of Vector Symbolic Architectures," arXiv:2301.10352 (2023). Hersche,
Terzić, Karunaratne et al., "Factorizers for Distributed Sparse Block Codes," arXiv:2303.13957 (2023/2025) — sparse
block codes + Block-Code Factorizer, O(Di*sqrt(Do)) decode. Kent, Frady, Sommer & Olshausen, Resonator Networks
Part 2, arXiv:1906.11684 (2020, *Neural Computation*) — iterative factorization capacity multiplier. Rahimi & Recht
(2007, NIPS), random Fourier features. **Frady, Kleyko et al., "Computing With Residue Numbers in High-Dimensional
Representation," *Neural Computation* 37(1), 2025, arXiv:2311.04872 — the primary VSA-side citation for lever 1,
directly operationalizing the grid-cell mechanism as a vector-symbolic construction.**

**Product/factored codes + compressed sensing (8):** Smolensky (1990, *Artificial Intelligence*), tensor-product
binding (cited here as a cautionary counter-example, not a lever). KroneckerBERT, arXiv:2109.06243, and "Doped
Kronecker Products," arXiv:2001.08896 — Kronecker compression accuracy-loss caveat. Liu, Qiu, Khan & Katz,
"Linearithmic Clean-up for Vector-Symbolic Key-Value Memory with Kronecker Rotation Products," arXiv:2506.15793
(NeSy 2025) — lever 4. Donoho & Tanner phase-transition theory; Candes & Tao, restricted isometry property (2005).
Donoho, Maleki, Montanari, approximate message passing (2009). Kane & Nelson, sparse Johnson-Lindenstrauss,
arXiv:1004.4240.

**Total: 27 external sources across 3 parallel lit-scans, all generic math/neuroscience/CS terms, no
substrate-specific names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]].** Several
specific numeric figures (grid-cell exact expansion ratio, resonator M_max order-of-magnitude, Kronecker-rotation
NeSy-2025 capacity-parity claim) are flagged by the sub-agents as approximate/figure-extrapolated rather than
directly confirmed from a table — treated as directional evidence, not precise numbers, consistent with the
calibration-penalty discipline.

---

## Intuitive summary

We asked: is there a cheaper way to make our knowledge-graph "memory" hold much more information reliably, without
paying the very expensive cost of just making the underlying number-storage vastly bigger (which works, but gets
expensive fast because the cost grows with the SQUARE of the size)?

We looked at the brain first. The clearest answer came from how the brain's navigation system represents position:
it doesn't use one giant, precise ruler. It uses several small, cheap "clocks" running at different speeds
simultaneously — a bit like reading the hour, minute, and second hands together to know the exact time even though
each hand alone only tells you a coarse fraction of it. Combining a handful of small, cheap clocks this way lets you
represent an enormous range of distinct positions using barely any extra material, because the number of positions
you can tell apart MULTIPLIES with each clock you add, while the cost only ADDS. That is a fundamentally different,
and much cheaper, way to buy capacity than just building one giant ruler.

The excellent news is that this exact idea has already been translated, by other researchers, into the same kind of
"hyperdimensional" math our knowledge system uses — it is not something we would be inventing from scratch, it is an
existing, published recipe we can adapt. The honest caveat: that recipe was proven for representing positions and
similar clean numeric ranges, not for our specific job (guessing facts about brand-new concepts in a knowledge
graph), so whether it transfers cleanly here is a real, testable, currently open question — which is exactly why the
next step is one cheap, reused test, not a leap of faith.

We also found a useful family of complementary, smaller ideas: ways to make the LOOKUP step itself cheaper and
smarter (checking a guess several times instead of once; a cheaper way to search a very large "dictionary" of known
patterns) that can stack on top of whichever capacity fix we pick, plus one important warning sign borrowed from a
related field (an idea that looks similar on paper but silently loses accuracy if the underlying facts don't
actually split apart as neatly as the math assumes) — flagged now so it doesn't surprise us later.
