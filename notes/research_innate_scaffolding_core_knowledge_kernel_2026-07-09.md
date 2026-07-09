# Research: Innate Scaffolding -- the Pre-Linguistic Core-Knowledge Kernel and What to Bake Into the Substrate

Filed-by: research sub-agent (Sonnet lit-scan x4, parallel breadth dispatch)
Date: 2026-07-09
Drill class: 5x DEEP (brain-first, cross-domain, part of a 5-drill FOUNDATIONAL program mapping how
humans learn language, to design substrate replication). This drill's domain: INNATE SCAFFOLDING --
what is baked into an infant BEFORE any language exposure.

Prior scour: `python tools/director_kb_query.py "innate core knowledge concepts objects agents number
space causality"` returned no direct prior hit on this specific question (top cosine 0.35, all loosely
related concept-space/causality atoms, no dedicated innate-kernel note). Grepped `notes/` for
grounding/cascade/nativism/bootstrap keywords -- no duplicate. This drill is genuinely new scope,
though it is the 4th research delivery today in the same session arc (native-encoder-relational-vs-
grounded-meaning, grounding-cascade-depth-multihop, brain-independent-channels) -- see Cross-thread
synthesis below for how it connects.

---

## HEADLINE

Four independent lit-scans (infant-cognition VOE literature, numerical/spatial core-knowledge
literature, nativism-vs-usage-based linguistics debate, and proto-conceptual-primitive/bootstrapping
literature) converge on the same structural picture: the innate kernel is NOT a set of concepts, it is
a SMALL, FIXED SET OF ENCAPSULATED, DOMAIN-SPECIFIC PERCEPTUAL/RELATIONAL ANALYZERS (object,
agent/goal, dual-number, geometry, same/different-comparison) that each output a SPARSE, ANALOG-FORMAT
RELATIONAL CODE from raw sensorimotor input -- and a separate, DOMAIN-GENERAL bootstrapping process
(itself conceded innate on both sides of the nativism/empiricism debate) composes these sparse codes
into the much richer adult conceptual/linguistic repertoire. Critically, several of these systems are
demonstrated DOUBLY DISSOCIATED (parallel-individuation vs approximate-number: distinct psychophysical
signatures, distinct ERP components, Hyde & Spelke 2011) rather than one system at different scales --
this is a concrete, falsifiable architectural lesson: don't build one generic module where biology
built two. The nativism/empiricism debate itself has partially converged: even Chomsky's account has
shrunk to "minimal recursive combination + a hierarchy bias" (Hauser/Chomsky/Fitch 2002), and usage-
based accounts concede real innate domain-general learning machinery (intention-reading, pattern-
finding, statistical learning) -- both sides now agree the fight is about how much is language-specific
vs general-purpose, not whether anything is innate.

## Cheap decisive test

**Dual-number double-dissociation probe (no new substrate build required for the diagnostic half).**
Add a small fixed-cardinality (~3-4 slot) pointer-array module addressing individual bundles by
identity token (parallel-individuation analog) alongside the substrate's EXISTING continuous
similarity/norm-based magnitude code (ANS analog). Run two synthetic tasks: (a) small-set EXACT tracking
(does bundle X still exist / is it the same token after occlusion-like corruption, N in {1,2,3,4}); (b)
large-set RATIO discrimination (is set A bigger than set B, N in {8,16,32}, ratios 1:2 vs 2:3). Then run
a PAIRED perturbation test: selectively corrupt/ablate the pointer-array module and measure the delta on
task (a) vs task (b); separately corrupt/ablate the continuous-magnitude channel and measure the same
delta pair. HARD-PASS signature (double dissociation, matches Hyde & Spelke 2011's N1/P2p psychophysical
split): pointer-array ablation hurts (a) >> (b); magnitude-channel ablation hurts (b) >> (a), with
minimal cross-talk. This is cheap (CPU, synthetic corpus, no new store-format) and directly tests
whether "bake in two systems, not one" is worth the added complexity for THIS substrate.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

1. **Dual-number bake-in vs unified-magnitude-code.**
   - HARD-PASS: perturbing the small-N pointer array degrades small-set exact-tracking accuracy by
     >=2x more than it degrades large-set ratio-discrimination accuracy, AND vice versa for perturbing
     the continuous magnitude channel (clean double dissociation, both directions, on a held-out synthetic
     set).
   - HARD-FAIL: perturbing either channel degrades both tasks roughly equally (within 1.3x of each
     other in both directions) -- no dissociation, meaning a single unified magnitude representation is
     sufficient and the two-primitive bake-in adds complexity without functional benefit.
   - MIDDLE: dissociation present in one direction only (e.g. pointer-array ablation selectively hurts
     small-set task, but magnitude-channel ablation also hurts small-set task nearly as much) --
     asymmetric, partial evidence.

2. **Parsimony/hierarchy prior (Perfors-style: prefer nested/recursive binding chains over flat
   concatenation when both fit the data equally well).**
   - HARD-PASS: adding an explicit shorter-encoding-preferred regularizer at consolidation/decode time
     measurably improves compositional generalization (held-out novel combination accuracy) by a
     pre-registered margin (e.g. >=15% relative) over an unregularized baseline at matched capacity.
   - HARD-FAIL: the regularizer produces no measurable generalization benefit, or degrades in-distribution
     accuracy by more than it improves held-out compositional accuracy -- suggests the substrate's existing
     binding operator does not benefit from an explicit hierarchy bias (either because it already has one
     implicitly, or because the bias doesn't transfer to this representation format).

3. **Privileged-basis-relation-set (containment/support/path/contact/link/blockage) vs fully open
   relation vocabulary.**
   - HARD-PASS: seeding the relation-vocabulary with this ~6-10-item basis set as high-frequency,
     structurally-simple binding templates measurably speeds convergence (fewer ingest examples to reach
     a fixed accuracy) on downstream compositional relation tasks vs a cold-start fully-open vocabulary
     with no privileged basis.
   - HARD-FAIL: no measurable convergence-speed difference, or the privileged basis measurably HURTS
     coverage of relation types not well-approximated by the basis set (over-fitting to the "core" six
     at the expense of everything else) -- suggests the closed-basis intuition from Mandler/Talmy/NSM
     convergence does not transfer to this substrate's open relation-vocabulary design.

4. **Carey's placeholder-bootstrapping recipe for exact-cardinality (successor/counting) from the
   dual-number primitives + an arbitrary memorized ordinal placeholder sequence.**
   - HARD-PASS: given ONLY (i) the dual-number primitives above, (ii) an arbitrary memorized total order
     over a placeholder symbol sequence (no numeric interpretation given), and (iii) a domain-general
     analogy/induction operator already in the substrate, the substrate can be shown to induce a
     genuine successor-like relation (placeholder[k+1] reliably composes with placeholder[k] plus "add
     one individuated item") that generalizes to untrained placeholder positions.
   - HARD-FAIL: no successor-like generalization emerges beyond memorized training positions -- the
     "bootstrapping" step is not implementable as specified (consistent with Carey's own concession that
     the mechanism is a sketch, not a computational account); would need a different (more specified)
     composition mechanism.

## Cross-thread synthesis

This drill sits downstream of three research deliveries earlier in this same session:

- **`research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`** established
  that relational/structural closure cannot manufacture grounded meaning -- an exogenous or independent
  channel is required (per Harnad's symbol-grounding dictionary-go-round and the empirical
  congenitally-blind color-knowledge case). That drill's proposed fix was a small EXTERNALLY-FED
  numeric-attribute seed set (content grounding).
- **`research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md`** diagnosed why grounding only
  spreads 1 hop (one-shot readout vs recurrent settling; absent bind-chain operator).
- **`research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md`** established
  that the brain never relies on a single self-referential loop -- it runs a graded portfolio of
  independent channels (embodiment/action, cerebellar error, basal ganglia, social correction), and that
  the failure signature to watch for is SHARED failure mode, not just architectural independence.

**This drill adds a distinction those three did not make explicit: there are (at least) two
qualitatively different kinds of "grounding," not one.** (a) CONTENT grounding -- external facts fed in
as data (the numeric-attribute seed set from the relational-vs-grounded drill). (b) STRUCTURAL grounding
-- an architectural BIAS on how the substrate processes its OWN input stream, such that it discovers
object-persistence, agency, quantity, and spatial structure the way an infant's visual/motor system does,
without any hand-fed semantic content at all. The core-knowledge literature is unambiguous that (b) is
real and does most of the earliest developmental work: newborns discriminate numerosity and expect
object continuity/solidity before they have ANY vocabulary and before any adult has told them a single
fact. This means the "no external LM, no distillation" constraint does not force ALL grounding to come
through a content-injection channel -- some of the most foundational grounding can instead come from
getting the substrate's OWN perceptual/relational PROCESSING BIASES right (structural priors baked into
how ingest and binding operate), which is a cheaper, more scalable, and more principled path than
enumerating facts by hand. This reframes "bake-in vs learn" as a design axis orthogonal to, and
partially resolving, the earlier "content vs no external content" grounding tension.

The dual-number double-dissociation (Hyde & Spelke 2011: distinct ERP components, distinct
psychophysical laws for small-exact vs large-approximate number) is also a direct, independent
confirmation of a pattern already flagged in this project's memory:
**[[reference-self-margin-taxonomy-splits-by-decode-regime]]** (self-margin splits into 3 families by
decode regime: order-statistic, collision-count, product-law-chain) and
**[[reference-correlation-hurts-associative-store-capacity]]** (decouple store-codes from retrieval
semantics) -- biology independently confirms the general design lesson "don't force one mechanism to
cover regimes with different scaling laws; build the right number of distinct mechanisms and keep them
structurally separate."

## Substrate-product implications

**S1 -- Mechanism map of the innate kernel** (see full citations below; ages are the reliable
demonstration window in the literature, not necessarily the true onset):

| System | What's innate | Evidence anchor | Reliable by |
|---|---|---|---|
| Object (cohesion/continuity/contact) | spatiotemporal persistence, boundedness, causal-contact requirement for motion transfer | Kellman & Spelke 1983; Baillargeon, Spelke & Wasserman 1985; Aguiar & Baillargeon 1999 | weak at birth, robust 2.5-4.5mo |
| Object KIND/sortal individuation | NOT innate -- comes online after object-persistence | Xu & Carey 1996 (fails at 10mo, succeeds 12mo) | ~12mo, plausibly word-bootstrapped |
| Agency/goal-directedness | self-propulsion + contingent-responsiveness triggers agent-attribution, independent of human form | Woodward 1998; Premack 1990; Johnson, Slaughter & Carey 1998 (fuzzy contingent object) | teleological/rational-action reasoning by 12mo (Gergely & Csibra) |
| Causal perception | launching-effect causal structure (not just motion), contested whether separate from object system | Leslie & Keeble 1987; Scholl & Tremoulet 2000 | 6mo |
| Approximate Number System (ANS) | ratio/Weber-law-dependent large-magnitude discrimination, amodal | Izard et al. 2009 (newborns, cross-modal); Xu & Spelke 2000 | birth; sharpens to adulthood |
| Parallel individuation (exact small-N, ~1-4) | absolute-set-size-limited, NOT ratio-based, working-memory "object-file" indices | Feigenson & Carey 2005; Hyde & Spelke 2011 (double dissociation vs ANS, ERP N1 vs P2p) | present at/near birth (Coubart et al. 2014) |
| Geometric/spatial reorientation | encapsulated shape-extraction, initially blind to conjoined landmark features | Cheng 1986 (rats); Hermer & Spelke 1994/1996 (toddlers); Vallortigara (day-old chicks) | early; landmark-conjunction needs language (Hermer-Vazquez 1999) or matures with scale |
| Same/different relational match | structural comparison of ALIGNED pairs (not passive pooling) | Anderson et al. 2018 (3mo); Ferry, Hespos & Gentner 2015 (7-9mo) | 3mo+ |
| Image schemas (Containment/Support/Path/Contact/Link/Up-Down) | proposed general redescription (Perceptual Meaning Analysis) of attended spatiotemporal percepts into sparse relational form | Mandler 1992, 2004 | pre-word |
| Force-dynamics primitives (Agonist/Antagonist, blockage/help/hinder) | independently-derived from adult cross-linguistic typology, overlaps image schemas | Talmy 1988 | n/a (linguistic-typological claim) |
| Minimal recursive combination (Merge-like) + hierarchy bias | narrowed-down Chomskyan claim; NOT rich item-specific grammar | Hauser, Chomsky & Fitch 2002 | claimed universal |
| Intention-reading + pattern-finding | the ONLY innate ingredients usage-based theory requires | Tomasello 2003 | present pre-grammar |

**S2 -- MAPS-TO-SUBSTRATE: concrete bake-in vs learn recommendations**

BAKE IN (structural/architectural priors, not learned content):

1. **Object-persistence as a binding-stability default.** A bound role-filler relation (entity token)
   should remain stable across a transform/occlusion-like corruption unless actively broken -- implement
   as a persistent identity-role vector whose binding survives a class of noise/permutation by
   construction (bundle-coherent update: sub-vectors of one bound entity update together, not
   independently). This is the HD/VSA-native form of cohesion + continuity.
2. **Agency/goal-directedness as a SEPARATE structural detector, not derived from object features.** Tag
   any entity-bundle exhibiting self-initiated or cross-entity-contingent state transitions (uncorrelated
   with an external "impulse" vector) as AGENT rather than OBJECT -- a discriminable structural signature,
   analogous to the brain's self-propulsion/contingency cue, computed independent of the object channel.
3. **Dual number system as TWO distinct primitives, never unified:** (i) a small fixed-cardinality
   (~3-4) addressable pointer-array for exact small-set tracking; (ii) a continuous, ratio/Weber-scaled
   magnitude code for larger sets. Do not build one parameterized "counting" module -- the double
   dissociation (Hyde & Spelke 2011) argues for two structurally separate comparator circuits with
   different scaling laws.
4. **Geometry/shape channel kept structurally separate from content/feature channel**, with reorientation
   and structural-lookup queries defaulting to route through the geometric channel FIRST, matching
   Hermer & Spelke's finding that geometry dominates until a later (language-mediated or scale-mediated)
   conjunction step is learned.
5. **Same/different as the substrate's existing similarity/overlap operator between ALIGNED (paired)
   bundles** -- this is already present as a primitive operator; the actionable lesson is an ENCODER-
   DESIGN one: exposure/training regimes must present genuinely paired comparisons (AABB-style), not
   just a shuffled stream, per Anderson et al. 2018's finding that comparison STRUCTURE, not passive
   co-occurrence, is what triggers relational abstraction in infants.
6. **A small privileged basis of relation-types** (containment, support, contact, link, path/source-goal,
   up-down, blockage/help/hinder -- ~6-10 items) as high-frequency, structurally-simple binding templates,
   seeded with high prior but NOT a closed enum -- the open relation-vocabulary system should still be
   able to construct novel relations compositionally from this basis. This partially resolves the
   existing tension between "no closed enum" (per
   [[project-substrate-open-relation-vocabulary-no-closed-enum]]) and the cross-domain convergence of
   Mandler/Talmy/Carey/Wierzbicka on a similar small candidate set: privileged basis + open composition,
   not one or the other.
7. **A parsimony/hierarchy prior at consolidation/decode time** (prefer shorter, nested/recursive binding
   chains over flat concatenation when both fit equally) -- the one concrete, well-evidenced "innate bias,
   not innate content" lesson from the nativism/usage-based synthesis (Perfors, Tenenbaum & Regier showed a
   general parsimony/Occam prior alone, without a language-specific hierarchy rule, favors hierarchical
   grammars because they are more compact).

LEAVE TO LEARNING (do not bake in as structure):

1. **Kind/category-based object individuation** (DUCK vs BALL sortals) -- emerges only after
   object-persistence is established and appears to be bootstrapped BY word/ingest learning, not prior to
   it (Xu & Carey 1996). Substrate: category/kind binding should emerge from ingest-driven clustering
   over the already-baked persistent-identity primitive.
2. **Geometry+content/feature conjunction** for reorientation-like queries -- literature shows this
   integration is either language-scaffolded (Hermer-Vazquez et al. 1999) or matures with scale/salience
   (Newcombe's critique) -- should be a LEARNED higher-level fusion step, not baked into the primitive
   geometric channel.
3. **Full exact-cardinality/counting competence** (successor function, arbitrary-N counting) --
   demonstrably NOT innate (Le Corre & Carey 2007 show gradual, effortful acquisition over ~1-2 years).
   Carey's best-worked case study gives a concrete, testable recipe: bake in the two number primitives +
   a placeholder mechanism (memorize an arbitrary total order over symbols with no interpretation given),
   then test (see Falsifiable Prediction 4) whether the substrate's existing domain-general
   analogy/induction operator can bootstrap a genuine successor relation from that scaffold alone -- a
   novel, concretely buildable, and currently untested substrate design per this session's KB scour.
4. **Rich, specific grammatical/relation content beyond the minimal compositional bind/bundle operator**
   -- both nativist and usage-based camps now agree detailed grammar/construction content is learned, not
   innate; at most a minimal recursive-combination capacity + hierarchy bias (item 7 above) is a defensible
   bake-in.
5. **Semantic content of any specific "primitive" vocabulary item** (the NSM primes themselves, e.g. the
   word GOOD or WANT) -- only the ABSTRACT RELATION TYPE (agency, causation, quantity, sameness, spatial
   relation) is a bake-in candidate; the lexical items are learned vocabulary via ingest.

**S3 -- Sharpest open question + deflated P estimates (capped at 0.50, novel-synthesis)**

Sharpest open question: **does baking in the dual-number system as two structurally distinct primitives
(rather than one unified magnitude representation) produce a measurable, falsifiable double-dissociation
benefit in THIS substrate** -- this is the most concretely testable of the recommendations (Falsifiable
Prediction 1 above), requires no store-format change, and directly tests whether biology's "build two
mechanisms, not one" lesson transfers.

- P(dual-number bake-in gives measurable double-dissociation benefit) ~ **0.35** (deflated from a naive
  ~0.55-0.60 by 0.20-0.25 per lit-scan calibration penalty; no direct HD/VSA precedent found in any of
  the four lit-scans for this specific architectural choice).
- P(parsimony/hierarchy-prior regularizer measurably improves compositional generalization, mirroring
  Perfors et al.'s Bayesian result) ~ **0.40** (closer to an established MDL/Bayesian-Occam result in
  general ML, but untested for this substrate's specific binding operators -- moderate deflation only).
- P(privileged-basis-relation-set + open composition productively resolves the closed-enum-vs-open-
  vocabulary tension) ~ **0.30** (the cross-domain convergence of Mandler/Talmy/Carey/NSM is suggestive
  but the four lit-scans found NO evidence the three traditions cross-validated each other
  mechanistically -- real risk this is convergent intuition, not a proven minimal kernel).
- P(Carey's placeholder-bootstrapping recipe is well-specified enough to implement and test as stated) ~
  **0.35** (Carey explicitly concedes the "modeling processes" step is a sketch, not a computational
  account; critics -- Rips, Bloomfield & Asmuth's Fodorian-combination rival -- press exactly this point).

All capped at or below 0.50 per [[feedback-lit-scan-calibration-penalty]]; this entire drill is
novel-synthesis (mapping infant-cognition literature onto an HD/VSA substrate design has no direct
precedent in any of the four lit-scans).

## Citations (verified count)

Approximately **45 distinct primary citations** were surfaced across the four parallel lit-scans (author/
year/venue triples, cross-checked against at least one retrievable source link per lit-scan agent -- see
each agent's source list for direct URLs). Highest-confidence, most load-bearing (drawn from all four
sub-reports, deduplicated):

1. Spelke, E.S. (1990). Principles of object perception. *Cognitive Science*, 14, 29-56.
2. Kellman, P.J. & Spelke, E.S. (1983). Perception of partly occluded objects in infancy. *Cognitive
   Psychology*, 15, 483-524.
3. Baillargeon, R., Spelke, E.S. & Wasserman, S. (1985). Object permanence in five-month-old infants.
   *Cognition*, 20, 191-208.
4. Aguiar, A. & Baillargeon, R. (1999). 2.5-month-old infants' reasoning about occlusion. *Cognitive
   Psychology*, 39, 116-157.
5. Xu, F. & Carey, S. (1996). Infants' metaphysics: the case of numerical identity. *Cognitive
   Psychology*, 30, 111-153.
6. Woodward, A.L. (1998). Infants selectively encode the goal object of an actor's reach. *Cognition*,
   69, 1-34.
7. Gergely, G. & Csibra, G. (2003). Teleological reasoning in infancy. *Trends in Cognitive Sciences*,
   7, 287-292.
8. Leslie, A.M. & Keeble, S. (1987). Do six-month-old infants perceive causality? *Cognition*, 25,
   265-288.
9. Xu, F. & Spelke, E.S. (2000). Large number discrimination in 6-month-old infants. *Cognition*, 74,
   B1-B11.
10. Izard, V., Sann, C., Spelke, E.S. & Streri, A. (2009). Newborn infants perceive abstract numbers.
    *PNAS*, 106, 10382-10385.
11. Feigenson, L., Dehaene, S. & Spelke, E. (2004). Core systems of number. *Trends in Cognitive
    Sciences*, 8, 307-314.
12. Feigenson, L. & Carey, S. (2005). On the limits of infants' quantification of small object arrays.
    *Cognition*, 97, 295-313.
13. Hyde, D.C. & Spelke, E.S. (2011). Neural signatures of number processing in human infants: evidence
    for two core systems. *Developmental Science*, 14, 360-371.
14. Cheng, K. (1986). A purely geometric module in the rat's spatial representation. *Cognition*, 23,
    149-178.
15. Hermer, L. & Spelke, E.S. (1994/1996). A geometric process for spatial reorientation in young
    children. *Nature*, 370, 57-59; *Cognition*, 61, 195-232.
16. Halberda, J. & Feigenson, L. (2008). Developmental change in ANS acuity. *Developmental Psychology*,
    44, 1457-1465.
17. Chomsky, N. (1980). *Rules and Representations*. Columbia UP.
18. Crain, S. & Nakayama, M. (1987). Structure dependence in grammar formation. *Language*, 63, 522-543.
19. Hauser, M.D., Chomsky, N. & Fitch, W.T. (2002). The faculty of language. *Science*, 298, 1569-1579.
20. Tomasello, M. (2003). *Constructing a Language*. Harvard UP.
21. Elman, J. et al. (1996). *Rethinking Innateness*. MIT Press.
22. Saffran, J.R., Aslin, R.N. & Newport, E.L. (1996). Statistical learning by 8-month-old infants.
    *Science*, 274, 1926-1928.
23. Pullum, G.K. & Scholz, B.C. (2002). Empirical assessment of stimulus poverty arguments. *The
    Linguistic Review*, 19, 9-50.
24. Perfors, A., Tenenbaum, J.B. & Regier, T. (2011). The learnability of abstract syntactic principles.
    *Cognition*, 118, 306-338.
25. Yang, C. (2016). *The Price of Linguistic Productivity*. MIT Press.
26. Mandler, J.M. (1992). How to build a baby: II. Conceptual primitives. *Psychological Review*, 99,
    587-604.
27. Mandler, J.M. (2004). *The Foundations of Mind*. Oxford UP.
28. Talmy, L. (1988). Force dynamics in language and cognition. *Cognitive Science*, 12, 49-100.
29. Ferry, A.L., Hespos, S.J. & Gentner, D. (2015). Prelinguistic relational concepts. *Child
    Development*, 86, 1386-1405.
30. Anderson, E., Chang, Y., Hespos, S. & Gentner, D. (2018). Comparison within pairs promotes
    analogical abstraction in 3-month-olds. *Cognition*, 176, 74-86.
31. Carey, S. (2009). *The Origin of Concepts*. Oxford UP.
32. Carey, S. (2011). Précis of The Origin of Concepts. *Behavioral and Brain Sciences*, 34, 113-124.
33. Goddard, C. & Wierzbicka, A. (2002/2014). *Meaning and Universal Grammar* / *Words and Meanings*.

Remaining ~12 citations (Slater et al. 1996; Wang, Baillargeon & Paterson 2005; Bogartz, Shinskey &
Schilling 2000 / Cashon & Cohen 2000 replication debate; Baillargeon 2008 "Innate Ideas Revisited";
Premack 1990; Johnson, Slaughter & Carey 1998; Farroni et al. 2002; Scholl & Tremoulet 2000; Cordes &
Brannon; Coubart et al. 2014; Piazza et al. 2004/2010; Vallortigara et al. 2020; Newcombe/Learmonth
critiques; Reali & Christiansen 2005; Gentner & Loewenstein 2002; Le Corre & Carey 2007; Rips, Bloomfield
& Asmuth Fodorian-combination critique) are secondary/supporting and listed with source links inside
each sub-agent's report (available on request, not reproduced here to keep this note tractable).
Confidence: HIGH that the primary ~33 citations above are real, correctly attributed papers (all four
sub-agents independently retrieved live source URLs per citation, cross-checked author/year/venue
triples against multiple independent hosting sites, e.g. PMC, Wiley, PNAS, ScienceDirect, university lab
archives) -- this is a standard, well-established literature (decades of peer-reviewed developmental
psychology / linguistics), not a fringe or contested corpus, which lowers hallucination risk relative to
a narrow/novel technical query.

---

Per [[feedback-no-papers-product-only]]: no publication framing. Every recommendation above is scoped
to a concrete substrate design change (bake-in architectural prior, encoder-design constraint, or
buildable/testable cell), not a scientific contribution claim.
