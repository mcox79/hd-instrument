# Drill: brain's foundational grounded data -- composition, scope, growth, density

Filed by: research (Sonnet, 4 parallel lit-scan sub-agents + Opus synthesis)
Date: 2026-07-15
Trigger: USER strategic hypothesis -- "we may be reasoning at a scale far ahead of our grounded-data base; the brain reasons from a vast, densely-grounded, slowly-accumulated foundation; ours is a sliver." This drill establishes the biological baseline to calibrate against.

Per [[feedback-query-privacy-decomposition]]: all search terms below were generic developmental-psychology / neuroscience / psycholinguistics terms. No substrate-specific framing left the process.

---

## HEADLINE

The brain's foundational grounding is (1) overwhelmingly **sensorimotor/perceptual + motor-action**, with statistical-regularity learning as the domain-general acquisition mechanism running over it from birth; (2) **scale-wise, a firehose-to-trickle funnel** -- raw sensory input ~1e6-1e9 bits/sec collapses to ~10-50 bits/sec of functionally retained signal, with a lifetime lexicon of only ~4e4 words sitting atop a synaptic-capacity ceiling of ~1e14-1e15 bits (Landauer's actually-retained estimate is ~1e9 bits, 5-6 orders below the hardware ceiling); (3) developmentally, grounding is genuinely **front-loaded** (synaptic density overshoot age 1-3, critical periods for vision/language) but does **NOT gate** relational reasoning in a strict sequential sense -- infants show binary-relation and numerical competence in the first year, well before grounding is dense, so the right model is **co-development with a grounding head-start**, not "ground fully, then reason"; and (4) per-concept density before a concept is reasoning-ready is **~13 features, multi-modal (graded profile across ~5-6 modalities with one dominant peak), and require on the order of 6-and-up repeated exposures** to move from fragile fast-map to robust representation.

## Cheap decisive test

Measure the substrate's current per-concept grounding density against the three biological floors below, using existing on-disk cap_map/substrate metadata (no new build required):
1. avg grounded attributes/edges per concept (bio floor: ~13.4, McRae et al. 2005)
2. avg distinct source-types/modalities per concept (bio floor: 3+ of ~5-6 modality/effector channels, graded not binary, Lynott & Connell / Lancaster Sensorimotor Norms)
3. avg reinforcement/exposure count per concept (bio floor: ~6 for "robust" in controlled paradigms; likely dozens for naturalistic automaticity)

Per current memory (`project_substrate_has_zero_grounded_measured_attribute_data...`), substrate metadata is reported 100% empty -- this test is expected to return density ~0 against all three floors, i.e. an immediate, cheap confirmation that the substrate currently sits several orders of magnitude below even the infant "fragile fast-map" threshold on every axis. This is a measurement, not a build; run it before any further density-building investment to get the honest starting gap.

## Falsifiable predictions

**HARD-PASS (confirms "thin grounding is the deficit; correct fix = build density, not rearchitect the reasoning engine"):**
- Current substrate density is well below floor on all three axes above (attributes <5, modalities <2, exposures ~1) -- AND
- A controlled ablation that dials concept-density upward (more attributes/edges, more distinct source-types, repeated reinforcement) shows the relational/reasoning advantage over a frequency baseline grows monotonically as density approaches the biological floor (~13 attributes, 3+ modalities, 6+ exposures).
- If both hold: the USER hypothesis is confirmed -- the reasoning engine is fine, the grounded base is the bottleneck, and the fix is to build toward these floors (consistent with the PIVOT program).

**HARD-FAIL (refutes the pure thin-grounding-is-the-deficit story; points elsewhere):**
- If a density-dial sweep pushes concept density to or beyond the biological floor (~13-20 attributes, >=3 modality/source-types) and the relational-reasoning advantage over the frequency baseline **stays flat or absent**, grounding thinness is NOT the (sole) explanation. This would point to either (a) the composition operator itself (consistent with the existing additive_map improvement thread), or (b) the reasoning engine's independent **capacity axis** -- per Halford's Relational Complexity theory, the ability to jointly hold n-ary relations matures on a working-memory/PFC clock that is empirically separable from grounding richness (unary ~age 1, binary ~age 2, ternary ~age 5, quaternary/adult ceiling ~age 11). A substrate whose composition op can only jointly hold 1-2 "relations" would behave like a toddler regardless of how densely grounded its concepts are.
- If increasing repetition/exposure count alone (without adding distinct attribute/modality types) fails to move relational performance even at high multiples (>=6x, >=20x), that specifically falsifies "just repeat more" and implicates distinctiveness/modality-diversity (per Lynott & Connell's modality-exclusivity effect, where a concentrated peak-modality profile predicts processing quality better than raw magnitude) as the load-bearing variable, not sheer repetition volume.

## Cross-thread synthesis

- Directly informs `project_PIVOT_build_ideal_knowledge_foundation...` and `project_substrate_has_zero_grounded_measured_attribute_data...`: this drill supplies the actual biological floor numbers (13.4 features/concept, 3+ modalities, 6+ exposures) to calibrate "how much is enough" for the foundation build, rather than building density with no target.
- Reinforces `project_reasoning_theory_constraints_brought_to_bear...` (resolution scales with # constraints jointly held) but **adds a distinct third axis**: the biology shows grounding richness (content) and relational capacity (constraint-holding, per Halford) mature on **partially independent clocks**. Current framing (density=capacity, query-width=use) is not contradicted, but should explicitly separate "content density per concept" from "how many relations the engine can jointly bind" -- these may need separate interventions, and a no-advantage result on thin real data could be explained by either deficit alone. Don't conflate them when designing the next ablation.
- Reinforces `project_grounding_tail_learning_loop_architecture_placement_consolidation_confidence...`: Landauer's finding that functionally-retained memory (~1e9 bits) sits 5-6 orders of magnitude below raw synaptic capacity (~1e14-1e15 bits) is evidence the brain's usable grounded base is **actively distilled/consolidated**, not a raw sensory dump. A near-empty metadata store is not merely "low volume" -- it also currently has zero consolidation process. This favors building the place->consolidate->confidence loop over trying to brute-force ingest raw volume.
- Reinforces `project_grounding_is_build_a_spoke_on_hub_quinian_bootstrap...`: Mandler's image-schema primitives (containment, support, path, agency, source-goal) extracted in the first year of life are a concrete candidate list for the initial "hub" categories later concepts index against -- a literature-grounded starting vocabulary for the spoke-on-hub bootstrap, worth pulling in in a follow-up drill if the hub-vocabulary needs concretizing.
- Adjacency-cascade candidate (per Trigger C): Halford's Relational Complexity theory (unary/binary/ternary/quaternary developmental timetable) is a new, previously-undrilled angle with direct substrate relevance -- it gives an independent, falsifiable, quantitative maturational curve for "how many jointly-held relations" a reasoning system should be able to support at a given developmental/training stage. Flagging as next-drill candidate below.

## Substrate-product implications

1. **Calibration targets, not just direction.** The build has concrete floor numbers to hit before concluding "still not enough grounding": ~13 attributes/edges per concept, 3+ distinct modality/source-types per concept (graded, with one dominant), and ~6+ independent reinforcement events per concept. Below these, "no advantage over frequency baseline" is fully expected and uninformative about the reasoning engine's quality. Above these, a persistent null result becomes a genuine architectural signal.
2. **Two independent levers, not one.** Content density (what's grounded) and relational capacity (how many things can be jointly reasoned about) are dissociable in the biological data. A build that only adds grounded attributes without also checking/growing the composition operator's joint-relation capacity may plateau for the wrong reason. Recommend the next capability audit explicitly separate "concept density" metrics from "max relations jointly bound" metrics.
3. **Consolidation is a first-class requirement, not an afterthought.** The multi-order-of-magnitude gap between raw sensory throughput and functionally retained memory means the brain's real "grounded base" is a heavily curated residue, not raw ingest. This substantiates prioritizing the grounding-tail consolidation loop over raw-volume ingestion sprints.
4. **Concrete anchor vocabulary available.** Mandler's ~6-10 image-schema primitives (containment, support, path, source-goal, agency, animacy, contact) are a literature-sourced, developmentally-first candidate set for hub concepts, usable directly if/when the spoke-on-hub bootstrap needs a starting content set instead of an arbitrary one.

## Next-drill candidate

Halford's Relational Complexity theory (unary -> binary -> ternary -> quaternary developmental timetable, ages ~1/2/5/11) as an independent, quantitative model for how many jointly-held relations a reasoning system should support at a given stage -- distinct from and complementary to the grounding-density question answered here. This is a genuinely new field-adjacency (developmental-psychology / working-memory capacity theory) not previously in the field-advisor's physics-oriented matrix; treat as a scope-expansion candidate (Trigger B/F) rather than ranking it against the physics fields.

## Citations (verified count: 24 sources fetched/cited across 4 sub-agent passes; 3 flagged as recalled/unverified-this-session)

**Composition/anchors (Barsalou, Mandler, Lakoff/Johnson, Glenberg, Piaget, Saffran, Gibson, Smith & Gasser):**
- Barsalou, L.W. (1999). "Perceptual symbol systems." *Behavioral and Brain Sciences* 22(4). https://pubmed.ncbi.nlm.nih.gov/11301525/
- Mandler, J.M. (1992). "How to Build a Baby: II. Conceptual Primitives." *Psychological Review* 99(4). https://cogsci.ucsd.edu/~jean/abstract/MandlerPaganC.pdf
- Lakoff, G. & Johnson, M. *Metaphors We Live By* (1980) / *Philosophy in the Flesh* (1999). https://en.wikipedia.org/wiki/Conceptual_metaphor
- Glenberg, A.M. & Kaschak, M.P. (2002). *Psychonomic Bulletin & Review* 9(3), action-sentence compatibility effect.
- Saffran, J.R., Aslin, R.N., Newport, E.L. (1996). *Science* 274, statistical learning in 8-month-olds. https://linguistics.berkeley.edu/~kjohnson/ling290e/saffran_et_al_1996.pdf
- Gibson, J.J. (1979). *The Ecological Approach to Visual Perception*; overview: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4950022/
- Smith, L. & Gasser, M. (2005). *Artificial Life* 11(1-2). https://www.cogsci.msu.edu/DSS/2010-2011/Smith/6lessons.pdf
- Multisensory integration protracted development (to ~age 14): https://pmc.ncbi.nlm.nih.gov/articles/PMC4390790/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3077428/

**Scale (sensory bandwidth, synaptic capacity, vocabulary):**
- Zheng, J. & Meister, M. (2024). "The unbearable slowness of being: Why do we live at 10 bits/s?" *Neuron*. https://www.cell.com/neuron/fulltext/S0896-6273(24)00808-0
- Norretranders, T. (1991). *The User Illusion*.
- Landauer, T.K. (1986). "How much do people remember?" *Cognitive Science* 10. https://gwern.net/doc/cs/algorithm/information/1986-landauer.pdf
- Bartol, T.M. et al. (2015). "Nanoconnectomic upper bound on the variability of synaptic plasticity." *eLife*. https://elifesciences.org/articles/10778
- Brysbaert, M. et al. (2016). "How Many Words Do We Know?" *Frontiers in Psychology*. https://pmc.ncbi.nlm.nih.gov/articles/PMC4965448/
- Neocortical synapse count estimate (~1.4e14): https://pmc.ncbi.nlm.nih.gov/articles/PMC11423976/

**Growth trajectory (critical periods, Piaget, core knowledge, relational complexity):**
- Huttenlocher synaptic density / pruning: https://pmc.ncbi.nlm.nih.gov/articles/PMC3055433/ ; https://www.pnas.org/doi/10.1073/pnas.2010281117
- Hubel & Wiesel ocular dominance critical period: https://pmc.ncbi.nlm.nih.gov/articles/PMC3612584/ ; https://www.cell.com/fulltext/S0092-8674(00)81665-7
- Lenneberg critical period hypothesis + softening critique: https://en.wikipedia.org/wiki/Critical_period_hypothesis ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3723803/
- Piaget sensorimotor stage, critical review: https://www.ncbi.nlm.nih.gov/books/NBK448206/
- Spelke & Carey core knowledge: https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/is-core-knowledge-a-natural-subdivision-of-infant-cognition/FDF42D2BC2DFAB5358ABD155FE47076A
- Halford relational complexity theory: https://www.researchgate.net/publication/13106042_Processing_Capacity_Defined_by_Relational_Complexity

**Density (feature norms, exposure counts, network degree, modality norms):**
- McRae et al. (2005). "Semantic Feature Production Norms." https://link.springer.com/content/pdf/10.3758/BF03192726.pdf (~13.4 features/concept, verified)
- Horst & Samuelson fast-mapping/poor retention: https://www.researchgate.net/publication/227828034_Fast_Mapping_but_Poor_Retention_by_24-Month-Old_Infants (verified)
- Hulme et al. (2019). Incidental word learning exposure counts. https://onlinelibrary.wiley.com/doi/full/10.1111/lang.12313 (verified)
- Small World of Words / free association norms: https://link.springer.com/article/10.3758/s13428-018-1115-7 (verified; exact mean-degree figure NOT independently confirmed this session -- flagged)
- Steyvers & Tenenbaum (2005) network degree figure -- **flagged as recalled/unverified this session**, PDF fetch failed to render.
- Lynott & Connell modality exclusivity norms: https://link.springer.com/article/10.3758/s13428-012-0267-0 (verified)
- Lancaster Sensorimotor Norms: https://pmc.ncbi.nlm.nih.gov/articles/PMC7280349/ (verified; "average modality count per concept" as a single discrete number -- NOT found, flagged)

## Calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]: all "ratio" and "density floor" figures above carry the standard deflation. The scale numbers in particular span 7+ orders of magnitude depending on which pipeline stage counts as "grounded" (raw sensory vs. synaptic capacity vs. functionally-retained memory) -- this spread is itself load-bearing information, not noise to average away: it means "grounded data scale" must be operationalized precisely before any substrate-vs-brain comparison is claimed. P_deflated = 0.45 on the co-development (not strict sequential-gating) conclusion, reflecting genuine, cited contestation in the developmental literature between embodied/empiricist and nativist/core-knowledge camps. P_deflated = 0.55 on the per-concept density floor numbers (McRae features, exposure counts), which are better-established single-study figures with less theoretical contestation, though still a single-paradigm estimate. Novel-synthesis cap of 0.50 applies to the "two independent levers" cross-thread synthesis claim (content density vs. relational capacity) since this specific integration across the two literatures is this drill's own synthesis, not a directly-cited joint claim from any one source.
