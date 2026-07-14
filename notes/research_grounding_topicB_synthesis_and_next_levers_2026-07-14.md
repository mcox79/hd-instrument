# Topic-B (grounding) 5x-drill synthesis + next-lever designs

Date: 2026-07-14. Synthesis across the 5-lens grounding drill (neuro/bio/quantum/field/wildcard: parents B-neuro + B-bio consolidated; B-field/B-quantum/B-wildcard grandchild lit-scans all reported, parents pending -- fold refinements when they land). This note BANKS the convergence + specs the next grounding cells so they are dispatch-ready.

## CONVERGENCE (what multiple lenses independently agree on)

1. **GROUNDING PROVABLY REQUIRES AN EXTERNAL CHANNEL (quantum/info-theory, RIGOROUS).** Data Processing Inequality + Information Causality (Pawlowski et al., Nature 2009) PROVE a closed system cannot manufacture mutual information with an untouched external referent by ANY internal reshuffling; info gain <= bits actually exchanged. => internal-only "grounding" is impossible; the ONLY paths are BAKE-IN (ingest external measured data) or ACTIVE-SAMPLING (query an exogenous referent). This validates the entire Track-B thrust and kills any internal-consistency-alone grounding claim (see caveat under lever A).

2. **MINIMAL GROUNDING LOOP (bio+neuro converge): external-value -> COMPARATOR -> CONSEQUENCE.** Non-neural bio (chemotaxis, immune, morphogen): sensor -> comparator (fast-vs-slow-ref / value-vs-threshold / candidate-vs-independent-recheck) -> irreversible asymmetric consequence that DISCARDS miscalibrated states. Neuro: prediction-error / forward-model loop ("heavy" = mismatch between predicted and actual load, not raw sensing). Kinetic-proofreading (Hopfield 1974) = the sharpest transferable write-rule: double-independent-check-then-DISCARD-on-disagreement (not average).

3. **CHEAPEST PRIMITIVES (wildcard): COMPARISON/ORDINAL before ABSOLUTE + CONSISTENCY-AGAINST-INVARIANTS.** Representational measurement theory + Piaget seriation: ordinal ("A > B") needs only a comparison, is developmentally + structurally PRIOR to absolute/cardinal values. Null-comparison (Wheatstone) needs only a difference-detector, no calibration. Control-theory: a value is grounded if it must satisfy a known LAW/invariant, divergence-from-law = the error signal. Metrology 2019-SI: grounding in a law-of-nature-constant = self-recalibrating, the STRONGEST form.

4. **PROVEN BAKE-IN RECIPE (field): fuse measured numeric literals into the KG, with a WITH/WITHOUT ablation.** KBLRN / LiteralE = ablation-confirmed link-prediction improvement from numeric literals. RoCS (Thosar 2021): measure -> k-means discretize -> class-level attribute-value tuples; QUANTIFIED beat over WordNet/ConceptNet on a tool-substitution task. We JUST operationalized this = the grounding-improves-relation-inference cell (32d02329b, 8-seed FULL pending sync).

5. **DATA SOURCES (field, no-LLM, free, bulk): Materials Project / AFLOW / OQMD / NOMAD** (measured/computed density, hardness, moduli) + USDA FoodData + PubChem (common substances). TRAP to avoid: text-mined quantities (DoQ) = symbols-about-symbols, NOT grounding.

6. **HONEST LIMIT (field): every proven grounding recipe is CLOSED-VOCABULARY.** None generalizes grounding to NOVEL relations/concepts -- grounding supplies numeric ANCHORS, not open-relation generalization. Matches our standing frontier (generalize-to-new-relations is the wall).

## EMPIRICAL STATE (our cells)
- periodic-table xchannel: wiring PROVEN (FPE/level-code encode measured numbers into bind/bundle, decode clean, distance-decay 0.999) but value-add CONFOUNDED (A built from B).
- mammal-allometry attribute-recovery: GROUNDING_REDUNDANT (taxonomy strong via phylogenetic conservatism); grounding adds only at residual traits (lifespan).
- grounding-improves-RELATION-inference (the right metric) 8-SEED FULL = MIDDLE_BAND (fusion fails +0.03 bar: FUSED beats RELATIONAL only +0.011, 6/8 seeds positive). **KEY NUANCE: grounding is NOT uninformative -- GROUNDED_ONLY 0.618 >> RELATIONAL 0.387 (+0.231), SCRAMBLE 0.361 HURTS. Grounding CARRIES substantial held-out-relation reasoning signal; the FUSION recipe (LiteralE ridge) WASHES IT OUT (fused 0.398 << grounded-alone 0.618).** => redundancy is in the COMBINATION, not the grounding. VET in flight (ad1058aa): CRUX = is grounded-alone>>relational GENUINE, or a mammal trait<->taxonomy coupling/popularity artifact (POP 0.472 also beats fused/relational -- arena may be degree-easy)? On CONFIRM -> **BETTER-FUSION recipe = the direct win-path** (grounding has the signal; capture it without dilution).

## NEXT LEVERS (dispatch-ready designs; fire as CPU frees / after grounding-reasoning FULL)

**LEVER A -- CONSISTENCY-AGAINST-INVARIANTS grounding (cheapest, most novel; wildcard/control-theory).**
Ground attribute values by requiring them to satisfy a KNOWN LAW, using divergence-from-law as an error/correction signal. NB caveat vs convergence #1: a law is itself EXTERNAL info baked in (the law encodes real-world structure), so this is NOT internal-bootstrapping -- it is bake-in of a LAW rather than of data points, which is cheaper + more general (one law grounds many values). Design: domain with a known scaling law (allometry: metabolic-rate ~ mass^0.75; or periodic trends). Give substrate attribute values (some corrupted); test whether enforcing law-consistency (a) DETECTS/CORRECTS the corrupted values (grounding-as-error-correction) and (b) improves held-out attribute/relation inference over no-law baseline. Glass-box (closed-form law residual). Must-fail = wrong/scrambled law does NOT help. CPU.

**LEVER B -- ORDINAL/COMPARISON encoding variant (cheap robustness; wildcard/measurement-theory).**
Our grounding cells use ABSOLUTE FPE values (which degrade under bundling). Test an ORDINAL/rank encoding (A>B comparisons / thermometer code) as the grounding channel -- predicted cheaper + more bundling-robust + developmentally-prior. Re-run the grounding-improves-reasoning ablation with ordinal-B vs absolute-FPE-B. Does ordinal grounding match/beat absolute at lower cost? CPU.

**LEVER C -- ACTIVE-SAMPLING loop (Phase 5, deeper; quantum/field).**
The DPI proof: active sampling is the ONLY way to add genuinely NEW grounded info beyond static bake-in. Minimal loop: substrate queries an executable oracle (tiny simulated world / law-evaluator) for attribute values, choosing queries by INFORMATION-GAIN (BOED/BALD -- mature classical toolkit, particle-filter update). Test: do information-gain-selected queries ground faster (fewer queries to reach target inference accuracy) than random queries? Glass-box (BOED score + particle filter). CPU. Deepest / most speculative; sequence last.

## SEQUENCING
1. Collect grounding-reasoning 8-seed FULL -> VET (coupling-artifact check). If it holds = first real grounding-improves-reasoning signal.
2. Fire LEVER A (consistency-against-invariants) -- cheapest + most novel + doubles as grounding-error-correction.
3. LEVER B (ordinal variant) if absolute-FPE fragility bites.
4. LEVER C (active-sampling) as the Phase-5 depth probe.
Fold B-field/B-quantum/B-wildcard parent refinements when they land.
