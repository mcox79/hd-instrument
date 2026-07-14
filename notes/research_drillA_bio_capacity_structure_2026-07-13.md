# Research: non-neural biology lens on cheap high-capacity codes + exploitable structure (drillA_bio_capacity_structure)

Date: 2026-07-13. Follow-up to `research_deployable_representational_capacity_levers_relational_map_builder_2026-07-13.md`,
whose leading lever (grid-cell/RNS-CRT multi-module residue coding) is a NEURAL-lens mechanism that requires the
underlying items to have exploitable continuous/spatial/numeric structure to factor across fixed small moduli. This
drill deliberately pivots to a DIFFERENT field (non-neural biology: molecular/cellular/evolutionary/immunological/
morphological) per the negative-result 2x-research discipline, because the map-builder's entities are arbitrary
structureless labels with nothing to compress — the exact condition under which residue/CRT-style algebraic
factoring is known to fail (also independently confirmed this session by the thalamic-router RC2 CRT hard-decision
fragility finding: `research_thalamic_router_RC2_mechanism_RC3_decision_2026-07-05.md`).

4 parallel Sonnet lit-scans, brain-adjacent-but-non-neural lens, generic public terms only, no substrate-specific
names/numbers sent off-platform: (A) DNA/genomic coding density + error correction; (B) protein folding as
compression + domain/exon shuffling as combinatorial reuse; (C) immune V(D)J combinatorial repertoire generation
(flagged MOST IMPORTANT per mission); (D) morphogenetic positional information + combinatorial signaling/TF codes.

---

## HEADLINE

**Biology's cheap-capacity trick is not "decode hidden structure out of an opaque atom" (the grid-cell/CRT approach
that fails on arbitrary labels) — it is "IMPOSE combinatorial generative structure AT CONSTRUCTION TIME from a small
reusable parts library, then retrieve via population-based approximate matching, not single-shot algebraic decode."**
Every non-neural mechanism found that works on genuinely arbitrary discrete symbols (immune V(D)J segments, protein
domains, transcription-factor combinatorial codes, histone marks) shares this shape: a SMALL library of discrete,
mutually-arbitrary parts + a COMBINATION RULE (choice, bind, bundle, randomized insertion) that multiplies capacity
while the library itself stays linear-cost. The one mechanism that instead depends on the underlying alphabet having
continuous/metric structure (protein folding's energy funnel) is explicitly disqualified for arbitrary-label
transfer, and is reported as such rather than force-fit.

**Most direct and most promising: V(D)J immune-repertoire generation + clonal-selection shape-space theory.** This is
the one mechanism in the whole non-neural-biology literature that is BOTH (a) proven to generate a vast, specific,
addressable space from a small combinatorial base of literally arbitrary discrete gene segments (no numeric/spatial
assumption anywhere in the mechanism), and (b) already has a 45-year-old formal mathematical treatment (Perelson &
Oster 1979 shape-space theory) that represents antigens/receptors as points in an abstract high-dimensional space
with distance-based matching and population-coverage arguments — this is structurally the closest existing
scientific precedent for "arbitrary discrete entities as points/vectors in a high-dimensional space, matched by
similarity, covered by a population of near-duplicate codes" that VSA/HDC itself is built on, independent of and
prior to VSA/HDC as a computational framework.

**GO/NO-GO read: GO on a specific, narrow reframe — not a new mechanism, a different DESIGN PHILOSOPHY for using the
mechanisms this substrate already has.** The concrete actionable difference from what already exists: (1) build
entity/relation codes as combinatorial binds of a SMALL typed-segment library (V(D)J / protein-domain analog) instead
of, or in addition to, monolithic opaque per-entity random vectors — i.e. give the entity SOME construction-time
combinatorial structure rather than trying to mine structure out of an already-opaque atom after the fact; (2)
retrieve via the substrate's EXISTING resonator/SIC-peel iterative decode reframed explicitly as a population-based,
error-tolerant "clonal selection" search (many near-miss candidates, threshold-based winner selection, iterative
local refinement = affinity maturation), NOT as a hard single-shot CRT/algebraic decode — this directly avoids the
exact failure mode (hard-decision residue fragility, unbounded reconstruction jump from one wrong digit) that
independently killed the thalamic-router CRT attempt in this codebase. **P_deflated = 0.35** for "V(D)J-style
segment-library + population-retrieval construction raises the map-builder's oracle-ceiling metric by >= 1.3x at
matched compute vs. the current monolithic-opaque-atom baseline" (capped under novel-synthesis rule — the underlying
biological mechanism and the shape-space math are well-established; the TRANSFER to this specific link-prediction
task is untested).

---

## Ranked mechanisms

| # | Mechanism | Arbitrary-symbol compatible? | Brain-independent (non-neural) source | HDC/VSA mapping | Deflated P (this transfers as a lever) |
|---|---|---|---|---|---|
| 1 | **V(D)J combinatorial segment choice + randomized junctional (TdT) insertion diversity** (LEADING) | **Yes — the closest fit found.** Gene segments and epitopes are inherently arbitrary discrete symbols, no numeric/spatial structure required anywhere in the mechanism. | RAG1/RAG2 recombination (immunology, textbook); junctional diversity dominates total repertoire size over pure combinatorial segment choice | Assign random hypervectors to a small library of "segment" roles (few dozen per slot); bind chosen segments per entity/relation; ADD a small random "junctional" perturbation vector unique per instance (this is the mechanism that generates the BULK of the diversity, not the combinatorics alone) | 0.35 |
| 2 | **Clonal selection + shape-space population retrieval** (pairs with #1, addresses the decode side) | Yes — shape-space theory (Perelson & Oster 1979) is explicitly a distance-based, population-covering formalism over abstract discrete/arbitrary entities | Burnet clonal selection theory; Perelson & Oster shape-space; germinal-center affinity maturation as iterated local search | Reframe existing resonator/SIC-peel iterative decode as population-based approximate-nearest-neighbor + iterative refinement (affinity maturation), explicitly NOT hard CRT-style algebraic decode — directly targets the known hard-decision fragility that killed the RC2 thalamic-router attempt | 0.35 (shared with #1; this is the retrieval-side half of the same lever) |
| 3 | **Cis-regulatory combinatorial logic (Britten-Davidson / Istrail-Davidson enhanceosome AND/OR logic)** | Yes — fully discrete/logic-based, no spatial dependency (Istrail & Davidson 2005 PNAS explicitly formalize cis-regulatory modules as Boolean-like "G operator" logic over TF binding-site occupancy) | Cis-regulatory module logic literature, non-neural (applies across all cell types/development) | Direct match to existing VSA primitives: bind = AND (conjunction of TF-like feature vectors), bundle = OR (disjunction across alternative regulatory paths) over a SMALL feature/relation-type alphabet — best applied at the RELATION-composition level (relations plausibly DO have exploitable small-alphabet structure, unlike raw entity identity) | 0.30 (mechanism solid, but largely already-practiced VSA primitives — the contribution is a reinforcing citation + a concrete "which alphabet to apply it to" recommendation, not a new operator) |
| 4 | **Protein domain / exon shuffling (combinatorial module reuse)** | Yes — domains function as opaque interchangeable tokens plugged into slots; internal domain structure is irrelevant to the combinatorics | Patthy, Bornberg-Bauer domain-shuffling evolution literature; Riechmann & Winter 2000 PNAS combinatorial-shuffling synthetic demonstration | Represent an entity as a combinatorial bind of a small library of TYPED ATTRIBUTE/DOMAIN vectors rather than one monolithic opaque random vector — imposes combinatorial structure on the entity itself at construction time (a structural fix, not a post-hoc decode) | 0.30 (qualitative "capacity multiplies, cost adds" claim is literature-supported in spirit but NOT quantitatively confirmed by any cited source — flagged as an inference, not a formula) |
| 5 | **Histone-code combinatorial tagging (additive multi-mark addressing)** | Yes — a combination of independent discrete flags per locus, non-spatial in the code itself (though mark PLACEMENT is chromatin-context-coupled) | Histone-code literature (Jenuwein & Allis framing; PNAS combinatorics review) | Near-exact match to bundling multiple discrete tag-vectors additively onto a base concept vector at near-zero incremental cost per tag — likely already how attribute-tagging is done in this substrate; low novelty, offered as confirming precedent | 0.20 (low novelty — already-standard VSA bundling; included for completeness, not proposed as new build) |
| 6 | **Codon degeneracy / error-minimizing genetic code (Freeland & Hurst)** | Yes — a static, evolved lookup table over arbitrary discrete triplet symbols, Gray-code-like adjacency (low-Hamming-distance codons -> similar/same amino acid) | Freeland & Hurst 1998 J. Mol. Evol.; contested vs. neutral-evolution critiques (Novozhilov/Koonin) | Could inform a static error-tolerant discrete-symbol-to-vector assignment (assign near-orthogonal vectors such that likely corruption modes land on semantically-close codewords) — a codebook-DESIGN idea, not a capacity-multiplying mechanism; weaker fit to "raise capacity," stronger fit to "raise robustness of an existing code" | 0.20 (real and citable, but answers a different question than capacity-ceiling; flagged as adjacent, not primary) |
| 7 | **Serial enzymatic proofreading (multi-stage multiplicative error suppression)** | Yes — re-checks actual content, not position/shape; content-agnostic | DNA replication fidelity literature (base selection, exonuclease proofreading, mismatch repair; ~10^9-10^10-fold combined error suppression) | Maps to iterative cleanup-memory/attractor-cleanup PASSES applied serially at retrieval time, not to codebook construction — complementary to, and consistent with, the substrate's existing SIC-peel-family iterative decode (family (b) from the prior deployable-levers drill) | 0.25 (reinforces an existing lever, does not add a new capacity mechanism) |
| — | **Protein folding funnel (Anfinsen/Levinthal) — EXPLICITLY DISQUALIFIED for this use case** | **No.** Requires amino acids to carry continuous physicochemical/metric structure (hydrophobicity, charge, H-bonding geometry) that produces a smooth funneled energy landscape; arbitrary unstructured labels have no such landscape. | Anfinsen thermodynamic hypothesis; Onuchic/Wolynes energy-landscape theory | No clean VSA mapping — informal Kolmogorov-complexity/entropy analogies exist in the literature but no rigorous sparse-coding/dictionary-learning formalization was found; reported honestly as a dead end for THIS transfer, not forced into the ranking | N/A (correctly excluded, not deflated-scored) |
| — | **Morphogen-gradient / French Flag positional information — MOSTLY DISQUALIFIED** | **Mixed/mostly no.** The gradient-generation half fundamentally requires a real continuous/spatial carrier (diffusion, concentration); only the threshold-DECODING half (continuous scalar -> discrete combinatorial ON/OFF state) is domain-general, and that half requires manufacturing a synthetic continuous scalar to threshold, which arbitrary discrete labels don't naturally provide for free. | Wolpert French Flag model; "many bits of positional information" literature | Not a free lever for arbitrary-label capacity; the exportable piece (multi-threshold discretization) is a generic recipe already implicit in existing bundling/argmax read-out, not a new capacity source | N/A (correctly excluded, not deflated-scored) |

---

## Cheap decisive test

**`map_builder_segment_library_clonal_retrieval_v1`.** Re-run the existing oracle-ceiling / relational-link-prediction
diagnostic (same harness used for the prior monolithic-dimension sweep and the RNS/CRT residue-module test) with ONE
structural change: construct each entity/relation code as a combinatorial BIND of K small typed "segment" vectors
drawn from K separate small libraries (V(D)J-analog; e.g. K=3-4 slots, each library ~20-50 arbitrary random
hypervectors) PLUS one additive random "junctional" perturbation vector unique to the instance (this is the piece
the immune-repertoire literature says does most of the diversity work, not the combinatorics alone). Retrieve using
the EXISTING resonator/SIC-peel iterative decode machinery, reframed explicitly as population-based threshold
matching over MULTIPLE candidate reconstructions (clonal-selection-style), not a single hard decode. Hold total
parameter/compute budget matched to the current monolithic-opaque-atom baseline.

### Falsifiable predictions

**HARD-PASS (V(D)J-style combinatorial-construction + population retrieval is a genuine deployable lever):**
1. Oracle-ceiling / MRR metric at matched compute improves by **>= 1.3x** over the current monolithic-opaque-atom
   baseline.
2. A must-fail scramble control (randomly permute which segment-library entries are assigned to which entities,
   destroying the combinatorial-library structure while preserving total parameter count) collapses the gain back
   toward the monolithic-atom floor — confirms the lift comes from the LIBRARY/COMBINATORIAL structure, not merely
   from added parameters.
3. The population-based iterative retrieval (multiple candidates + threshold selection) measurably outperforms a
   single hard-decode control on the SAME segment-library-encoded data — confirms the retrieval-side half of the
   lever (population matching beats one-shot decode), isolating whether the gain is construction-side, retrieval-
   side, or both.

**HARD-FAIL (redirect to accepting the monolithic-dimension cost, or to the decode-side levers already ranked in the
prior drill):**
1. Gain is **< 1.15x** at matched compute — the map-builder's relational signal does not correlate with any
   constructable small-segment decomposition of entity/relation identity the way immune epitope-recognition does
   with gene-segment identity; arbitrary labels really do have nothing to impose combinatorial structure ONTO either,
   not just nothing to mine structure OUT OF.
2. The scramble control does NOT collapse the gain — meaning any observed lift is a parameter-count artifact, not a
   genuine structural effect, which would falsify the entire "impose-structure-at-construction-time" hypothesis for
   this task, not just this specific instantiation of it.
3. If HARD-FAIL: still informative — it would establish that the map-builder's ceiling problem is NOT a
   "structure-imposition" problem at all (ruling out this entire family: V(D)J-style, domain-shuffling-style, and by
   extension any future "give the atoms cheap structure" proposal), sharpening the remaining bet fully onto the
   decode-side levers from the prior drill (resonator/SIC-peel at fixed monolithic dimension, Kronecker clean-up) or
   onto accepting the O(n^2) dimension-increase cost.

**Middle band (gain in [1.15x, 1.3x)):** sweep K (segment-slot count) and per-slot library size independently, and
separately sweep the magnitude of the junctional-perturbation term — if gain tracks K and perturbation magnitude in
the direction the immune analogy predicts (more slots + right amount of junctional noise = more capacity, too little
noise = under-diverse, too much = swamps the combinatorial signal), this is a scaling finding, not an architecture
failure, and warrants a second cheap sweep before a HARD-FAIL call.

**P_deflated by mechanism:** #1/#2 combined (V(D)J construction + clonal-selection retrieval, leading) = 0.35;
#3 (cis-regulatory AND/OR logic, apply at relation level) = 0.30; #4 (domain-shuffling-style typed-attribute
construction) = 0.30; #5 (histone additive tagging) = 0.20 (low novelty); #6 (codon-degeneracy error-tolerant
codebook design) = 0.20; #7 (serial proofreading -> iterative cleanup) = 0.25 (reinforces existing lever).

---

## Cross-thread synthesis

- **Directly answers the negative-result 2x-research trigger from the same-session grid-cell/RNS-CRT lever**
  (`research_deployable_representational_capacity_levers_relational_map_builder_2026-07-13.md`, lever 1). That
  lever's own HARD-FAIL condition #2 predicted exactly this outcome: "the true relational structure does not factor
  cleanly across residue moduli... the map-builder's ceiling is tied to genuinely high-dimensional entangled
  structure that RNS/CRT-style factoring cannot cleanly separate." This drill does not contest that finding — it
  answers the follow-on question the mission posed (what CHEAP lever remains, given that entities have nothing to
  factor out) by pivoting from "mine hidden structure out of an opaque atom" to "impose combinatorial structure at
  construction time," a genuinely different design philosophy, not a retry of the same one.
- **Directly reinforces and re-motivates, from an independent evidence source, the resonator/SIC-peel iterative
  decode lever already ranked #3 in the same prior drill** and already partially in flight this session. The
  immune-repertoire lens gives it a NEW and arguably stronger justification: not just "iterative factorization raises
  practical capacity" (the resonator-networks framing) but "population-based approximate matching with iterative
  local refinement is how biology's own closest analog to this exact problem (arbitrary discrete labels, vast
  addressable space, error-tolerant retrieval) actually works," which also explains from a different angle WHY the
  hard-decision CRT approach failed both here and in the thalamic-router RC2 finding.
- **Directly extends the thalamic-router RC2 mechanism finding**
  (`research_thalamic_router_RC2_mechanism_RC3_decision_2026-07-05.md`): that note found hard-decision non-redundant
  CRT decode is "textbook-fragile" (single-digit error causes unbounded reconstruction jump) and that the brain's own
  grid-cell system avoids this via large per-module POPULATIONS plus downstream attractor cleanup (hippocampal CA3).
  This drill finds the SAME graceful-degradation principle in a completely independent non-neural biological system
  (immune clonal selection: population of near-duplicate candidate codes + threshold-based selection, not single-
  decode reconstruction) — two independent biological systems (neural grid-cell + non-neural immune) converging on
  "population + soft threshold, not one-shot hard decode" as the robust design, which raises confidence in this
  principle beyond what either lit-scan alone would support.
- **Connects to the standing relational-capability program spine**
  (`project_relational_capability_is_the_core_requirement_make_it_real_USER_2026-07-10.md`): that thread's diagnosis
  is that the brain's ADDITIVE/GEOMETRIC codes (relations-as-directions) generalize where the current discrete
  HRR-bind (memorizing) regime does not. This drill's #3 finding (cis-regulatory AND/OR logic mapping to bind=AND/
  bundle=OR over a small RELATION-TYPE alphabet, not entity identity) is a concrete, independently-biology-grounded
  recommendation for WHERE to apply combinatorial-logic structure (relation composition) versus where it does NOT
  help (raw entity identity, per the disqualified protein-folding and gradient-decoding mechanisms) — sharpening that
  thread's scope rather than repeating it.

---

## Substrate-product implications

- **This reframes the entire "raise capacity cheaply" question from a REPRESENTATION-MINING problem to a
  CONSTRUCTION-TIME-DESIGN problem** — a genuine philosophical pivot, not a new operator. If validated, the claim
  becomes "we don't need our arbitrary entity labels to secretly contain exploitable structure; we can GIVE them
  structure at creation time the same way the immune system builds receptors from a small segment library, and
  retrieve them the same way clonal selection does (population + threshold, not brittle exact decode)." This is a
  stronger and more specific product claim than either the plain "bigger vectors" baseline or the now-likely-closed
  grid-cell/CRT lever.
- **If the cheap decisive test HARD-PASSes:** this becomes a construction-time recipe applicable to EVERY future
  entity/relation added to the map-builder, not a one-off fix — new entities are assembled from the existing small
  segment library (linear cost) rather than requiring a fresh monolithic high-dimensional slot each time, directly
  addressing the deployability concern that motivated this whole research thread.
- **If the cheap decisive test HARD-FAILs:** still valuable — it would rule out an entire FAMILY of "impose cheap
  combinatorial structure" proposals (this one, and by extension protein-domain-shuffling-style typed-attribute
  construction) in one falsification, rather than requiring separate tests per candidate, because the underlying
  claim ("arbitrary labels can be given exploitable combinatorial structure at construction time") is the same across
  that family. This would leave the decode-side levers (resonator/SIC-peel at fixed dimension, Kronecker clean-up)
  and the monolithic-dimension-increase cost as the only remaining known routes.
- **Construction-proof caution:** nothing here is yet a capability win. The cheap decisive test reuses existing
  harness and existing decode machinery (resonator/SIC-peel), so the marginal cost of finding out is low; the
  claim being tested is specific and falsifiable, per discipline.

---

## Citations (verified count)

**DNA/genomic (6, sub-agent A):** DNA digital-storage capacity/Shannon-ceiling literature (DNA storage
information-theoretic-ceiling scans). Freeland & Hurst 1998 (*J. Mol. Evol.*), error-minimizing genetic code. Neutral-
evolution critique of codon-table optimality (contested counter-view, cited honestly). DNA replication fidelity
(base-selection/exonuclease-proofreading/mismatch-repair, PMC4465240). Histone-code combinatorics (PNAS
0501853102). Genome-as-error-correcting-code framing (PLOS ONE 0036644, flagged as contested/suggestive not settled).
Telomere-as-checksum analogy explicitly flagged as NOT verified / likely weak.

**Protein folding + domain shuffling (10, sub-agent B):** Anfinsen thermodynamic hypothesis (PNAS 95(10):5545).
Levinthal's paradox / energy-landscape (Onuchic & Wolynes framing). Algorithmic-complexity-of-a-protein (*Phys. Rev.
E* 54:R39, 1996) and Shannon-entropy/Kolmogorov-complexity structural-prediction work (PMC4391790) — flagged as
narrow/informal analogies, not a rigorous coding-theory formalization of folding. Patthy, domain-shuffling evolution
review (*Biochem Soc Trans* 37(4):751, 2009). Bornberg-Bauer, modular protein evolution (PMC7023805,
PMC2245809/PMC187552). Riechmann & Winter 2000 (*PNAS* 97), combinatorial-shuffling synthetic novel-fold
demonstration. Cui, Xiao, Stolzer & Durand, vector-semantics-of-domain-architectures (*Bioinformatics Advances*,
domain-as-word/architecture-as-document embedding) — flagged as the closest existing CS-vector bridge, though not a
VSA-binding formalization by name.

**Immune V(D)J + shape-space (approx. 8, sub-agent C):** RAG1/RAG2 V(D)J recombination mechanism (immunology
textbook consensus). TdT-mediated junctional (N-nucleotide) diversity as dominant repertoire multiplier. Burnet
clonal-selection theory (1957/1959). **Perelson & Oster 1979 (*J. Theor. Biol.* 81:645-670), shape-space theory** —
primary formal-mathematics citation for lever 1/2. Germinal-center affinity-maturation-as-adaptive-walk framing
(Victora/Nussenzweig/Mesin-school, recalled not re-verified this session — flagged). Farmer, Packard & Perelson 1986
(*Physica D* 22:187), immune-network dynamical-systems model. De Castro & Timmis 2002, clonal-selection algorithms
(CLONALG). Forrest, Perelson, Allen & Cherukuri 1994 (IEEE S&P), negative-selection algorithm — AIS-vs-VSA distinction
explicitly flagged as the sub-agent's own reasoned judgment, not a literature-asserted claim.

**Morphogenesis/combinatorial signaling (8, sub-agent D):** Hox-cluster colinearity and combinatorial homeodomain
code (developmental-biology consensus). Wolpert French Flag model + "many bits of positional information" critique
(*Development* 146(24) and 148(2)). Britten & Davidson 1969, combinatorial-control hypothesis. **Istrail & Davidson
2005 (*PNAS* 102), cis-regulatory-module Boolean-logic formalization** — primary citation for lever 3. Istrail 2019
(*J. Comput. Biol.*), regulatory-genome-for-CS reframing. Clustered protocadherin combinatorial-stochastic
self-recognition code (PMC6888844, PMC8901172). Glycocode (*Annu. Rev. Biochem.* 2023) — flagged low-confidence/
underexplored as an implementable readout logic, included for completeness only.

**Total: approximately 32 external sources across 4 parallel lit-scans, all generic public scientific/math/
immunology/developmental-biology terms, no substrate-specific names/configs/numbers sent off-platform per
[[feedback-query-privacy-decomposition]].** Several figures (exact V(D)J repertoire-size estimates spanning 10^9 to
10^13-10^18 depending on source, exact histone-mark redundancy ratios, domain-shuffling capacity-scaling as a
qualitative rather than quantitatively-derived claim) are explicitly flagged by the sub-agents as approximate,
source-dependent, or their own structural inference rather than a directly-cited formula — treated as directional
evidence only, consistent with the calibration-penalty discipline.

---

## Intuitive summary

We asked biology a narrower, harder version of last drill's question: forget the brain's spatial "several clocks"
trick for a second (that one needs the thing being represented to have some natural continuous range, like a
position, and our knowledge-graph entities are just arbitrary names with no such range) — how does biology make cheap
big structured spaces out of things that are ALREADY just arbitrary labels with nothing special about them?

The clearest answer came from the immune system. Your body builds an almost incomprehensibly large number of
distinct antibody shapes from a genuinely small parts catalog: it picks one piece each from three short shelves of
interchangeable gene fragments, snaps them together, and then adds a small random splice at the seams. That splice
step, not the piece-picking, is what actually generates most of the variety. Crucially, none of those gene fragments
need to have any inherent order or structure to each other for this to work — unlike the brain's spatial clocks, this
trick works on things that are just arbitrary labels, which is exactly our situation. Then, when the body needs to
recognize a real threat, it doesn't do a single precise lookup — it lets a large population of slightly-different
candidate antibodies compete, keeps whichever ones are close enough, and then lets those refine themselves further
through trial and error. That's a genuinely different and much more forgiving strategy than the single fragile
"decode the exact right answer" approach we already tried and watched fail (both in this literature search and, we
found, in this project's own earlier attempt at a similar exact-decode trick).

The most promising concrete idea to borrow: instead of trying to find hidden structure inside our already-arbitrary
labels (which does not exist and cannot be mined out), we could instead BUILD each entity's code, from the start, out
of a small reusable parts catalog plus a bit of random variation — the same recipe the immune system and, separately,
recombining protein-building-blocks both use — and then look things up the immune system's forgiving way (many
close-enough candidates, pick the best, refine) using machinery this project already has, rather than one strict,
brittle decode. We designed one cheap, reusable test for exactly this, with a clear pass/fail line, so we will know
soon whether this is real or another honest dead end.
