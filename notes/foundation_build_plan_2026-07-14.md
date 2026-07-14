# Knowledge Foundation — Build Plan (first pass)

Status 2026-07-14. USER-authorized pivot: build the substrate's knowledge FOUNDATION from existing tools (full + vetted); runtime reasoning stays glass-box. This is the plan. ONE decision (density strategy) is gated on the Part-C experiment; everything else is decided.

## 1. What we're building (one paragraph)
A **dense, vetted, module-extensible knowledge foundation**: every *general concept* the substrate holds characterized across the **7 relation-type buckets** (taxonomic / property / part-whole / functional / causal / spatial / social), assembled by (a) re-ingesting fuller existing KBs, (b) LLM-**generating** the semantic relations no KB has at density, and (c) attaching domain **modules** (science/math) on shared entities — with runtime reasoning kept glass-box (no external LLM at inference) and a clean **held-out slice reserved** so we can prove the substrate reasons/generalizes over it rather than parrots it.

## 2. Why — the gap, measured (not assumed)
- **Current active partition:** 93.4% of 141k concepts have <=1 semantic bucket; only 0.44% reach >=4. A lexical/taxonomic skeleton (dominated by SYNONYM + IS_A).
- **Re-ingesting the full on-disk CSKG (6.0M edges vs our 190k):** lifts >=4-bucket to **5.7%** (~13x) and <=1-bucket to **64.5%** — a real *free* win, but INSUFFICIENT. Even the full best-available merged KG is ~4M/6M **lexical** (RelatedTo/Synonym/Antonym/FormOf); the semantic buckets (property/functional/causal) are genuinely thin, and **33% of our lemmas get ZERO semantic relations** even from the full source.
- **Domain coverage (WordNet-supersense audit):** everyday commonsense is covered but skewed to the organism/person INSTANCE tail (21% living + 13% people). Reasoning-critical domains are near-absent: **science 0.6%, math 1.1%, folk-psychology 0.8%, society/economics 1.1%, time 1.0%.**
- **Prior art:** genuinely UNBUILT — no resource achieves dense balanced per-concept multi-bucket coverage.
=> The build is a **GENERATION problem** (create the missing semantic relations), not a merge problem. Re-ingest is the cheap warm-start; generation + domain modules are the real work.

## 3. THE OPEN GATE — Part C (density-strategy decision)
The premise "characterize every concept to >=4 buckets => better reasoning" is **unvalidated AND literature-challenged**: arXiv:2508.15291 found relation-type *diversity inversely correlated* with link-prediction in fused dense-embedding models. Part C (`exp_bucket_diversity_degree_controlled_inference_cskg_v1`) tests, DEGREE-CONTROLLED, whether bucket-diversity HELPS or HURTS inference on OUR glass-box VSA substrate.
- **HELPS** -> density target stands; Stage 1 generates toward >=4 buckets.
- **HURTS / NEUTRAL** -> pivot from "more buckets" to "the RIGHT buckets": Stage 1 generates only the specific reasoning-relevant relations, and we keep bundles decoupled (our correlation-hurts-capacity finding) to avoid the dense-embedding failure mode.
Downstream stages branch here. This is why we validate before building at scale.

## 4. Architecture (decided)
- **Dense universal CORE** = Wikidata + ConceptNet(full) + ATOMIC + WordNet + Wiktionary, with BabelNet as the multilingual label layer and YAGO4 as a constraint-checker. Every concept = one node with its identity + taxonomy + relations.
- **Open MODULE registry** = domain KBs (PubChem, periodic-table/Materials-Project, GeoNames, UMLS/SNOMED, a math ontology) attached to core entities. Add a module without rebuilding the core (contingency-admission: anchors to core + adds non-redundant content + declares provenance).
- **Cross-module interconnection THROUGH shared core entities** (one "diamond" node carries physical + chemical + use attributes); reconcile only where modules overlap on the same entity.
- **Concept-centric multilingual**: ground the language-independent concept once; attach multilingual labels; culture-specific concepts (hygge, saudade) as their own nodes.

## 5. Coverage scope — first pass (decided; checklist = WordNet supersenses + extensions)
- **INCLUDE, densely:** everyday commonsense + language + math/logic + **science fundamentals** + folk-psychology + society/economics + time. (These are the reasoning-critical domains; science/math/folk-psych/society/time are the measured GAPS to fill.)
- **DEFER:** the organism/person INSTANCE tail (34%, mostly species + specific people); exhaustive named entities; deep specialist sub-domains. Cover concept-TYPES densely, not the instance tail (that tail is the sparse-tail failure mode).

## 6. Stages
- **Stage 0 — RE-INGEST** the full on-disk CSKG (free, ~13x lift to 5.7% dense). Warm-start. *(Not gated — strictly more of data we already have; but re-scored under Part C's decoupling guidance.)*
- **Stage 1 — GENERATE + VET** the missing semantic-bucket relations per concept via LLM (property/functional/causal — the buckets no KB has at density), verified. **[GATED on Part C: generate-to->=4-buckets vs generate-right-buckets]** This is the build's center of gravity.
- **Stage 2 — DOMAIN MODULES** for science + math (PubChem, periodic table, Materials Project, math ontology) via shared-entity anchoring. Fills the measured science/math near-absence.
- **Stage 3 — VET / MERGE + HELD-OUT + OPTIMUM:** address the merge-lossiness (KB-merge ~51% entity-link precision, ~28% fact-loss); reserve the held-out slice BEFORE enrichment; measure reasoning-vs-bucket-coverage to find the EMPIRICAL density optimum (the "up to a point").
- **Stage 4 — LATER:** additional modules; the runtime autonomous-grounding loop (#3, place/consolidate/confidence) for ingesting genuinely-new things post-foundation.

## 7. Vetting ("fully vetted" = the hard part)
- Merge lossiness is the real risk (51% link precision). Mitigate: entity-resolution against Wikidata IDs (the shared key); cross-source agreement; YAGO4-style type constraints; sampled human/LLM spot-check.
- Generated relations: verify by cross-source consistency + must-not-contradict existing high-confidence relations + provenance tagging + confidence scalar (per-relation, decoupled from magnitude).

## 8. Held-out / evaluation (protects the prize)
- Reserve a clean slice of relations BEFORE enrichment (so it can't be contaminated by generation).
- Metric: does the glass-box substrate INFER the held-out relations, beating a frequency baseline, over the enriched foundation. That is the substrate's actual contribution (transparent reasoning), not having-the-facts.

## 9. Risks / open questions
- Density optimum unvalidated -> Part C (gating).
- LLM-generation hallucination/quality -> vetting protocol (Stage 3).
- Merge lossiness -> entity-resolution + constraints.
- Instance-tail bloat -> defer.

## 9b. STAGE-1 GENERATION PILOT — RESULT (2026-07-14, PASSED, fair/representative)
Fair pilot on a 92-concept stratified sample (easy/abstract/unmapped/degree-1/science + 8 scrambled neg-controls); generation done by director inline (agent died on API error), truth verified INDEPENDENTLY (adversarial judge, separate context — NOT self-graded).
- Densification 1 -> 2.7-4.3 buckets/concept (abstract lower, correctly); connectivity 94% (targets map to existing concepts); neg-control refusal 100% (4/4 + garbled artifacts refused = calibration holds).
- TRUTH (independent): 93.75% TRUE / 4.2% FALSE / 2.1% uncertain. Per-stratum: easy 93%, ABSTRACT 78% (weak), unmapped 100%, degree1 100%, science 100%. The FALSEs were NOT fabrication: 1 relation-type miscategorization + 1 overgeneralized folk-grammar nuance + 1 polysemy/sense-ambiguity. Zero invented facts/locations.
- CAVEATS (wanted result): small sample (48 rels, wide error bars); BEST-CASE generation (careful director; workhorse model at scale likely worse -> 93.75% is a ceiling); abstract is weakest; LLM-judge shares blind spots -> cross-model/external-KB verification needed at scale.
- VETTING-PASS SPEC (from the error profile): check (a) relation-type/target SCHEMA COHERENCE, (b) POLYSEMY/sense-disambiguation, (c) overgeneralized-nuance -- not just raw fact-check.
=> VERDICT: LLM-generation is a VIABLE, VETTABLE densification path. Foundation build de-risked; proceed to scale with the vetting spec + cross-model truth-check + extra care on abstract.

## 9c. DE-RISK — DOES DENSITY DRAMATICALLY IMPROVE REASONING? (2026-07-14, calibrated: MEANINGFUL not TRANSFORMATIVE)
Tested the core premise BEFORE scaling (USER: "have we shown we're at the ceiling on a correctly-sized corpus?"). Two cuts:
- WORST-CASE (mammal attributes, class-determined): DENSE did NOT beat SPARSE(taxonomy-only) -- slightly HURT (dilution). Where taxonomy already predicts, density adds nothing. Sobering.
- REAL GRAPH (density beyond taxonomy, fair relation-aware predictor, n=1716): taxonomy-only MRR 0.213 -> full-connectivity 0.257 = +0.043 overall (modest, taxonomy carries a lot). BUT on the 83% of cases where TAXONOMY FAILS: MRR 0.072 -> 0.219 = +0.147 (3x RESCUE). Density's value is concentrated exactly where taxonomy can't predict (the majority of relations).
- HONEST VERDICT: density adds REAL, meaningful value (3x on the 83% taxonomy misses) BUT to a MODEST ceiling (~0.25 MRR / hits@1 ~0.18 = normal commonsense-KG range, NOT transformative). "Meaningfully-better relational inference to a modest ceiling", not "dramatic reasoning". Bigger jumps would require MULTI-HOP (untested).
- CAVEATS: fair proxy (not the VSA mechanism); measured on already-dense concepts (whether GENERATED density rescues as well as real density = the final de-risk, learned early by the incremental loop); single-hop only.
=> BUILD JUSTIFIED but with CALIBRATED expectations. Do NOT oversell. Proceed incrementally (measure-as-you-go = safety valve); if the incremental rescue doesn't show up on generated density, stop. Consider testing whether MULTI-HOP is where a larger prize hides.

## 9d. THE REASONING THEORY (2026-07-14, load-bearing -- resolves "what caps reasoning + does density help")
Chain of inline VSA prototypes + de-risk experiments converged on: **reasoning resolution scales with the NUMBER OF CONSTRAINTS BROUGHT TO BEAR.** VSA toy (additive bundle+cleanup): acc vs #constraints-queried = 0.05/0.15/0.40/0.75/0.93/0.97/0.99 for K=1..7; ambiguity 24->1.0.
- DENSITY = capacity for constraints; QUERY-WIDTH = use of them; SAME lever. Accuracy governed by absolute #constraints-queried, ~independent of density per se (density just enables richer queries). Fully-queried dense concept -> 0.99; sparse concept caps ~0.20.
- SINGLE-HOP is modest because it = 1 constraint = underdetermined (~96% of single-hop gap is one-to-many unwinnable). Not a density failure -- a using-one-constraint failure.
- ESCAPE = ADDITIVE constraint-satisfaction (brain's attractor / CA3 pattern-completion), NOT joint tensor-binding: additive settling hits 0.99 where joint tensor-binding fails at 0.018 (50x below random). The reasoning-mechanism gap is closed by the RIGHT operation.
- MULTI-HOP CHAINS are NOT the escape: CG on synthetic (L=18-35) but real-knowledge gain unproven + 6 prior HARD-FAILs -- chains bring FEW constraints; the prize is CONJUNCTIONS.
- PHASE-DIAGRAM: operative dial = query-width (constraints); storage-mode + dimension swept + ruled out as second-order.
- CAVEAT: toy/clean (real noisier, ceiling <0.99); demonstrated for concept-identification; confirm on real knowledge (the decisive next experiment).
=> **COUPLES THE PROGRAM:** strong reasoning = DENSE FOUNDATION (constraints) + MULTI-CONSTRAINT additive constraint-satisfaction (bring them to bear) + additive settling (glass-box VSA, proven). Foundation build gets a precise purpose; the constraint-satisfaction reasoning mechanism is a first-class build target. [[project_reasoning_theory_constraints_brought_to_bear_dense_plus_constraint_satisfaction_2026-07-14]]. Storage protected by the sharded CG law.

## 9e. DECISIVE NEXT EXPERIMENT
Confirm the reasoning theory on REAL knowledge (not toy): additive multi-constraint constraint-satisfaction over a real dense concept subset (sharded store) -- does bringing many known relations to bear resolve underdetermined commonsense queries + beat single-hop, on the live substrate? This is the real-substrate version of the 0.99 toy result; the whole reasoning-mechanism bet rides on it reproducing (at a real, lower-but-meaningful level).

## 10. First concrete build step (fires on Part C verdict)
- **If Part C HELPS:** Stage 0 re-ingest (free) + a **Stage-1 pilot** — LLM-generate + vet the missing semantic buckets on a ~500-concept sample across the target domains; measure the bucket-coverage lift AND a held-out reasoning lift. That pilot sizes the full generation build and validates the vetting bar before scaling.
- **If Part C HURTS/NEUTRAL:** re-scope Stage 1 to the specific reasoning-relevant relations only; same pilot shape, different target.
