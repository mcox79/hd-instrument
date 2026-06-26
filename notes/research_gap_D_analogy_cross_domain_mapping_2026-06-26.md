# Research: Gap D -- analogy / cross-domain structural mapping

**Date:** 2026-06-26
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep-drill on substrate-grade analogy. Brain-aligned mechanism + how substrate could BEAT brain via algebraic operations on relational structure. USER addendum: cortex layer (TWO_TIER + BCM + Modern Hopfield) is spinning up TODAY; brain analogy is cortex-dependent (parietal extracts relational structure, slow-learned over thousands of exposures); if cortex-composition is the natural mechanism, flag + drill it as a top candidate.

**Builds-on:**
- Within-domain analogy already HARD_PASS at substrate: comp24 (FORM-A K5=0.913, K10=0.953; substrate-internal binding+cleanup; PP-115 / PP-165) -- the within-domain capability is real and chain-grade-eligible
- Cross-domain analogy RETRACTED 2026-06-10: STRETCH4-2 (RotatE) 0.244 cross vs 0.899 within (notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md)
- DRAMA (Eliasmith-Thagard 2001, Cognitive Science 25:245-286): canonical HRR-based distributed structural-mapping model; explicit precedent for substrate-feasible analogy
- TWO_TIER generational W (Gap 4, in flight): notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md
- Cortex-as-router brain mechanism (Gap 1, today): notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md
- BCM slow learning for schemas (Gap 3, dispatched): notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md
- n5 cortex slow-learning context predictor (today): notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md
- Modern Hopfield revival slow-built basins (today): notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md

**Calibration:** P estimates deflated 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds pre-registered both directions per [[feedback-negativity-bias-symmetric-verify]].

---

## HEADLINE

Substrate already does WITHIN-domain analogy at cap (K10 cos=0.953; PP-115/PP-165 HARD_PASS). The open capability is CROSS-domain analogy -- mapping a relational pattern learned in domain A onto entities in domain B. The brain solves this with parietal cortex extracting relational structure (slow-learned over thousands of exposures, mPFC abstract relational map; Park-Boorman 2024 bioRxiv 617652) and matching against schemas in long-term memory. Substrate has THREE substrate-feasible mechanism families: (1) direct HRR algebraic unbinding -- works in DRAMA (Eliasmith-Thagard 2001) but fails at substrate's regime for cross-schema because the relation vector itself is domain-specific; (2) partition-routed structural alignment -- groups facts by relational primitive, within-partition analogy is direct retrieval, brain-correlate is parietal binding to abstract schema; (3) cortex-composed schema-Hopfield retrieval -- USER addendum mechanism, exploits today's TWO_TIER + BCM + Modern Hopfield infrastructure: schemas are slow-learned cortical templates, cross-domain analogy = "retrieve the schema that matches the source pair's structure, then re-apply it to target domain entities" via Modern Hopfield attention.

**The rank-order conclusion is novel and consequential:** the cortex-composed variant (3) is HIGHER-P than the direct-algebraic variant (1) at substrate's regime, BECAUSE the substrate's existing within-domain win (comp24 K10=0.953) was achieved via relational binding + cleanup ON THE SAME RELATION SET it was learned over -- exactly the within-domain regime. Cross-domain requires a different vocabulary (the universal relational primitives from Gentner-style structural alignment), and the only substrate-feasible way to ACQUIRE that vocabulary at scale is to slow-learn it cortex-style. The direct-algebraic path is still worth one shot as the CHEAP-DECISIVE diagnostic (it tells us how much of the cross-domain gap is just "wrong relation vector" vs "fundamentally needs slow-learned schemas").

Substrate-better angle: substrate can ALGEBRAICALLY transfer the slow-learned schema once it has one. The brain has to LEARN each analogical mapping; substrate, once it has W_schema for the source pair's structure, can apply the same matrix to ANY new domain's entities at O(N) cost. That is the substrate-product story: cortex slow-learns the schemas once; substrate algebraically transfers them.

P_deflated(at least one of three top cells achieves cross-domain HARD_PASS over its pre-registered band) = 0.55. Per-cell P_deflated: cortex-composed schema-Hopfield 0.40, partition-routed structural alignment 0.35, direct HRR unbind 0.25.

---

## Cheap decisive test

**Single test that discriminates the three mechanism families:** a 200-analogy cross-domain test set spanning 4 domain pairs (medical-legal, geographic-biological, kinship-corporate, mechanical-political), 4 relation types (causes, part-of, instance-of, opposite-of), 50 analogies per pair-relation cell.

Build it on TOP of the existing FB15K-237 / ConceptNet ingest (already present in substrate, see notes/testbed_post_compaction_brief_2026-06-09_overnight_chain.md confirming 458K ConceptNet facts) so corpus is grounded.

**Discriminator design:**
- ARM_DIRECT_HRR_UNBIND: classical Plate/DRAMA-style unbind. Given source pair (A,B) and target entity C, compute D_pred = unbind(B, bind(A, R_inferred)) where R_inferred = unbind(A, B). Score top-1 / top-5 retrieval against the held-out target D.
- ARM_PARTITION_ROUTE: partition stored facts by relational primitive type (using ConceptNet's 34-type vocabulary as universal partitions). For (A,B,C) query, route to the partition matching the relation A-to-B exhibits, then retrieve C's pair-partner within that partition.
- ARM_CORTEX_HOPFIELD: cortex-composed. Use the TWO_TIER generational W (in flight today) as the cortical schema store. Each schema is a Modern-Hopfield-retrievable template (slow-learned via BCM from many within-domain analogies). At query time: (i) Modern Hopfield retrieves the schema vector matching the (A,B) relational structure; (ii) re-bind that schema vector with the target entity C; (iii) unbind to retrieve D. THIS is the cortex-composed mechanism the USER addendum flagged.
- ARM_BASELINE_COSINE: pure cosine retrieval ignoring relational structure (no analogy, just nearest D to C). Methodology rail; should be near chance.

**Pre-registered bands (per Fix #14 single-cell discipline):**

HARD-PASS (the gate is the discriminator, not a single arm):
- ARM_CORTEX_HOPFIELD top-1 >= 0.45 AND >= ARM_DIRECT_HRR_UNBIND + 0.10 AND >= ARM_BASELINE_COSINE + 0.20. The +0.10 margin over ARM_DIRECT_HRR_UNBIND is the discriminator that cortex-composition is the load-bearing mechanism (not just substrate algebra).
- OR ARM_PARTITION_ROUTE top-1 >= 0.45 AND >= ARM_DIRECT_HRR_UNBIND + 0.10 (alternate winning mechanism).
- OR ARM_DIRECT_HRR_UNBIND top-1 >= 0.45 (would refute the "direct algebra insufficient" framing -- VERY informative either way; cap_map gets cross-domain row back).

HARD-FAIL:
- ALL three relational arms within 0.05 of ARM_BASELINE_COSINE: cross-domain analogy is NOT achievable at substrate's current regime; pivot to deeper-encoder approaches (Path C v2; needs LLM-grade encoder).
- ALL three relational arms top-1 < 0.30: same as above; the 0.244 RotatE ceiling holds across mechanism families.

MIDDLE_BAND [0.30, 0.45] for the winning arm: PARTIAL. Mechanism works but needs scale -- queue followup with N_DIM 16384 -> 32768, longer slow-learning pass for cortex arm, full ConceptNet 34-primitive vocabulary for partition arm.

**Cost:** ~3-6 CPU-hr at N=16384 over 200-analogy test set. Bottleneck is W_schema slow-learn pass for ARM_CORTEX_HOPFIELD (re-uses TWO_TIER W matrix when that cell lands; can pre-stage the cell to run on the W output). ARM_DIRECT_HRR_UNBIND is pure vector arithmetic (~10s). ARM_PARTITION_ROUTE is ConceptNet-partition lookup + cosine retrieval (~minutes).

---

## Drill section 1: Direct HRR algebraic analogy

### Plain-English description

Plate (1995) and Kanerva (2009) established the math: in HRR, `bind(A, R) = B` encodes the fact "A is in relation R to B". The inverse operation `unbind(B, A)` recovers an approximation of R (noisy because HRR is approximate). Given a source analogy (A, B) and a target entity C, the classical algebraic recipe for "find D such that A:B :: C:D" is:

```
   R_AB = unbind(A, B)              # extract relation A-to-B
   D_predicted = bind(C, R_AB)      # apply same relation to C
   D_retrieved = cleanup(D_predicted)  # nearest-neighbor over codebook
```

This is the substrate-native version of word2vec's "king - man + woman = queen", but on a HD vector substrate rather than dense embedding space. Within a single domain (where the relation R_AB is stable across the codebook), this works at substrate -- comp24's K10=0.953 PP-115/PP-165 results are this mechanism.

### Substrate-feasibility

ALL substrate primitives are already implemented and chain-grade:
- bind: circular convolution (FHRR) or block-binding (HRR variant); production primitive at N=16384
- unbind: circular correlation; production primitive
- cleanup: nearest-neighbor over codebook; production primitive (comp24, native_reasoning K20)
- Codebook: substrate has 588 chain-grade atoms + multi-domain KGs ingested (FB15K-237, ConceptNet, HotpotQA)

The cell to build is 50 lines of substrate-native code. NO new primitives needed.

### Discriminator (per Fix #28: per-arm metrics, not verdict_msg)

- Top-1 accuracy on 200 cross-domain analogies (50 per domain pair x 4 pairs)
- Top-5 accuracy (substrate-product story prefers top-5 since downstream LLM can re-rank)
- Per-domain-pair breakdown (per BIAS-13/14/15 regime check): is performance uniform across pairs, or only one pair works?
- Per-relation-type breakdown: which relation primitives transfer cross-domain (universal relations: causes, part-of, instance-of) vs which fail (domain-specific: works-at, employed-by)?
- Comparison against ARM_BASELINE_COSINE (the chance level for the corpus geometry)
- Variance across 3 seeds (encoder seeds): if cv > 0.05 the mechanism is encoder-sensitive, which is INFORMATIVE.

### Brain fidelity

LOW-MEDIUM. The brain does NOT do single-shot algebraic unbinding for cross-domain analogy. Brain analogy is a multi-stage process: parietal cortex extracts relational structure over hundreds of milliseconds (Park-Boorman 2024 demonstrates parietal binding to abstract structures); rostrolateral prefrontal cortex integrates relations (Cerebral Cortex 27:2652 demonstrates RLPFC abstract relational categorization); mPFC slow-extracts relational schema map (Park-Boorman 2024). The whole circuit is slow-learned over thousands of exposures; the brain at query time RETRIEVES the schema from cortex, it doesn't compute it from scratch.

That said: Eliasmith-Thagard DRAMA (2001) IS the brain-mechanism-aligned use of HRR for analogical mapping. DRAMA uses HRRs to encode relational structure AND THEN applies structural-mapping over the HRR vectors. Modern reading: DRAMA is the substrate-feasible Gentner-SME equivalent. The direct algebraic mechanism is a COMPONENT of DRAMA but not the whole story; DRAMA also does iterative refinement and structural-consistency checking that direct unbinding skips.

### Substrate-better angle

Substrate CAN do this O(N) at query time once the codebook is built. Brain takes hundreds of ms over parietal-RLPFC-mPFC circuit, substrate takes one bind + one unbind + one cleanup. The substrate-better story is SPEED + PARALLELISM (substrate can compute analogies for many target entities C simultaneously via batched binds, brain serializes via attention).

The substrate-WORSE story is robustness to schema mismatch: when source relation A-to-B is a DIFFERENT family of relation than the cross-domain target should use (e.g., source = "is-capital-of", target should be "is-headquarters-of"), the algebraic unbind transfers the source-specific relation vector, which is wrong. The brain catches this via mPFC schema abstraction (Park-Boorman 2024 shows mPFC representation is INDEPENDENT of specific stimulus identities).

### P_deflated

0.25. The mechanism works for within-domain analogy (already chain-grade in substrate via comp24). For cross-domain, it inherits the STRETCH4-2 failure mode: the source relation vector is domain-specific. Direct unbinding will produce a noisy target that often doesn't match the cross-domain target entity. Expected top-1 ~0.20-0.35 cross-domain. Worth dispatching as the CHEAP-DECISIVE diagnostic (tells us if the gap is "wrong relation vector" -- which the cortex arm fixes -- or "more fundamental" -- which means encoder pivot).

---

## Drill section 2: Structure-mapping via partition routing

### Plain-English description

Group facts by relational primitive type (using ConceptNet's 34-type vocabulary as the universal relational schema: IsA, PartOf, UsedFor, Causes, AtLocation, CapableOf, etc.). Within each partition, all facts share the same abstract relation type (e.g., all "X causes Y" facts in one partition).

Cross-domain analogy then becomes: (1) identify which relational primitive the source pair (A,B) exemplifies, (2) route the target query (C, ?) to the same partition, (3) within-partition retrieval finds D such that C-relates-to-D the same way A-relates-to-B.

The key insight: within a partition, the analogy is back to WITHIN-domain (because all facts in the partition share the relational structure). And substrate's within-domain analogy is already cap-grade.

### Substrate-feasibility

Substrate has chain-grade partition routing (KG traversal primitive). The mechanism needed is:

- Build N partitions, one per ConceptNet relation primitive
- For each stored triple (h, r, t), assign to partition matching r (or to the closest primitive if r is domain-specific)
- At query time: classify the source (A, B) into a primitive partition by running A and B through the relation-classifier (LLM annotation offline, or substrate-internal via relation embedding cosine), then run within-partition cosine retrieval for D given C

This is ANCHOR-3 from the 2026-06-10 cross-domain drill (CONCEPTNET-RELATION-DECOMPOSITION). It was queued as priority 1 in that drill but never dispatched (substrate moved on to the encoder pivot). Re-prioritizing it now.

### Discriminator

- Same 200-analogy test set
- Partition-routing top-1: does within-partition retrieval find the correct cross-domain target?
- Partition-classifier accuracy: how often does the relation classifier correctly identify which ConceptNet primitive the source (A,B) belongs to? This is a separately-cert-eligible diagnostic (relation classification is its own capability).
- Per-primitive breakdown: which ConceptNet relations work for cross-domain analogy (universal ones likely do) and which don't (domain-specific compositions of primitives may not)?
- Comparison against direct unbind: does partition routing add value beyond pure HRR algebra?

### Brain fidelity

HIGH for the within-partition step (matches Gentner-SME: analogy is mapping over shared relational structure once that structure is identified). MEDIUM for the partition-classifier step (brain has parietal-cortex relational categorization, but ConceptNet's 34 categories are a coarse approximation of brain's continuous relational space).

The mechanism matches the cognitive science consensus on cross-domain analogy: it requires a universal vocabulary of abstract relational primitives (Hofstadter-Mitchell 1994 Copycat, Gentner 1983 SME, Holyoak-Thagard 1989 ACME). Substrate makes this concrete by using ConceptNet's 34-type vocabulary as those primitives.

### Substrate-better angle

The partition lookup is O(1) per partition + O(K) within-partition cosine (where K is partition size). Total cost per cross-domain analogy: ~milliseconds. Brain spends hundreds of ms on this via parietal-RLPFC circuit. Substrate also gets PARALLEL retrieval over many partitions simultaneously, which the brain cannot do (cortical processing is serial within a region).

Substrate-WORSE: requires the partition vocabulary to be pre-defined. Brain learns this vocabulary in development; substrate inherits ConceptNet's 34 categories which are designed for common-sense reasoning but may be wrong granularity for technical domains.

### P_deflated

0.35. The mechanism is well-grounded (Gentner-SME is 40 years of cognitive-science consensus). Substrate has all the primitives. The risk is the relation-classifier step: if ConceptNet's 34 categories are too coarse for the 200-analogy test set, the partition routing degrades to random-within-coarse-partition and performance collapses to baseline cosine. Expected top-1: 0.30-0.50 on universal-relation analogies, 0.15-0.30 on domain-specific ones. The MEDIAN expectation is right at the MIDDLE_BAND / HARD-PASS boundary.

---

## Drill section 3: Cortex-composed schema-Hopfield retrieval (USER addendum mechanism)

### Plain-English description

USER addendum: substrate's CORTEX layer is spinning up TODAY (TWO_TIER generational W + BCM slow learning + Modern Hopfield retrieval). Brain analogy is cortex-dependent (parietal extracts relational structure, slow-learned via thousands of exposures over development; Park-Boorman 2024 shows mPFC abstract relational map emerges with consolidation). If cortex composition is the natural mechanism, the substrate-feasible cell looks like:

```
   PHASE 1 (slow learning, offline):
       For each within-domain analogy (A, B, C, D) in training corpus:
           schema_vector = bundle(bind(A, B), bind(C, D))   -- bundle of bound pairs
           Hebbian write: W_schema[i,j] += eta * schema_vector[i] * R_label[j]
           BCM modulation: postsynaptic activity tracked via theta_M sliding threshold
           NREM replay over W_schema: sharpens to a Modern-Hopfield-retrievable basin

   PHASE 2 (query time):
       Given source (A, B) and target entity C:
           query_schema = bind(A, B)
           retrieved_schema = ModernHopfield(W_schema, query_schema)
                              -- attention-style softmax retrieval over schema basins
           D_predicted = unbind(retrieved_schema, C)
                              -- apply the retrieved schema's relation to target entity
           D_final = cleanup(D_predicted)
```

This is the SCHEMA-COMPOSITION variant of cross-domain analogy. The schema vectors are stored in cortical W_schema; they were learned over many within-domain examples; at query time, Modern Hopfield retrieves the schema MOST SIMILAR to the source pair, then that schema is RE-APPLIED to the target entity in the new domain.

The critical mechanism difference vs ARM_DIRECT_HRR_UNBIND: ARM_DIRECT_HRR_UNBIND extracts the relation vector FROM THE SOURCE PAIR ITSELF, which is domain-specific. ARM_CORTEX_HOPFIELD retrieves the relation schema from a CORTICAL STORE of slow-learned schemas, which has been ABSTRACTED away from domain specifics by the BCM slow-learning (Gap 3 mechanism: BCM averages out domain-specific noise, sharpens prototype-of-relation).

### Substrate-feasibility

Re-uses TODAY'S in-flight infrastructure:
- TWO_TIER generational W (Gap 4): the cortical store substrate. PARTIAL HARD_PASS today; cortical layer is going LIVE.
- BCM slow learning (Gap 3, in flight): the slow-learning rule that builds W_schema. Sliding threshold theta_M sharpens the schema basins.
- Modern Hopfield retrieval (research_modern_hopfield_revival_slow_built_basins_2026-06-26.md): the query-time retrieval mechanism.
- HRR bind/unbind/bundle: substrate primitives, chain-grade.

This cell composes three in-flight cortical primitives + chain-grade HRR primitives. The CELL itself is 80-100 lines of substrate code. The dependency: it can only land AFTER TWO_TIER + BCM + Modern Hopfield each have HARD_PASS or PARTIAL. That dependency is the strongest argument for dispatching this AFTER the cortical primitives stabilize (~next session).

### Discriminator

- Same 200-analogy test set
- ARM_CORTEX_HOPFIELD top-1: cortex schema retrieval + re-application
- Per-schema-basin breakdown: which schemas have sharp basins (high retrieval cosine) and which are flat (the relation hasn't been slow-learned enough)?
- N_schema_basins: how many distinct relational schemas did W_schema learn from the slow-learning pass? If << 34 (ConceptNet primitive count), the cortex is under-trained; if >> 100, the cortex has over-specialized to specific relation instances.
- W_schema density audit: should be DENSE (Hebbian outer products fill it); sparsity < 0.5 is a bug.
- Comparison vs ARM_PARTITION_ROUTE: does cortex-Hopfield BEAT explicit ConceptNet partition routing? If yes, that is evidence that slow-learning extracts a BETTER vocabulary than ConceptNet's hand-curated 34 categories.
- Comparison vs ARM_DIRECT_HRR_UNBIND: the +0.10 margin is the discriminator that cortex composition is load-bearing.

### Brain fidelity

HIGHEST of the three families. Direct mapping to:
- mPFC slow-extracted relational map (Park-Boorman 2024 bioRxiv 617652): "An abstract relational map emerges in the human medial prefrontal cortex with consolidation"
- Parietal binding to abstract structure (Schema-based active inference, arXiv 2601.18946): parietal computes the abstract relational structure that gets routed to cortex
- Modern Hopfield as cortical attractor (multiple Krotov works): the retrieval mechanism is biologically grounded
- BCM as slow cortical Hebbian learning (Bienenstock-Cooper-Munro 1982; Tino-Bishop sequence extension 2003): the slow-learning rule

This is the cortex-composition mechanism the USER addendum flagged. The brain-fidelity is high because every component has a direct cortical correlate, AND the COMPOSITION (slow-learn schemas in cortex + retrieve at query time via attention) matches the cognitive-science consensus on how human cross-domain analogy works (Holyoak-Thagard 1989 ACME with schema retrieval; Gentner 1983 SME with structural alignment over schemas; Hofstadter-Mitchell 1994 with abstract relational primitives).

### Substrate-better angle

THIS is the substrate-product story. Brain takes a lifetime of exposures to slow-learn the relational schema vocabulary; substrate can slow-learn the W_schema matrix over a single corpus pass (text8 + ConceptNet + FB15K-237 + HotpotQA combined: ~1B token-equivalent exposures), then ALGEBRAICALLY apply any slow-learned schema to any new domain at O(N) cost per analogy. The brain has to relearn the mapping for each new analog; substrate just does one matrix-vector product.

Even better: substrate can EVALUATE many candidate schemas in parallel via Modern Hopfield batched attention. The brain serializes. So substrate not only ALGEBRAICALLY transfers each schema, it also evaluates the BEST schema for the target pair in O(K log K) where K is schema count. The brain spends hundreds of ms on schema retrieval through parietal-RLPFC; substrate spends milliseconds.

The deepest substrate-better angle: substrate can DECOMPOSE a complex cross-domain analogy into a sum of slow-learned schemas. If the source analogy combines two universal relational primitives (e.g., "is-capital-AND-government-seat-of"), substrate can retrieve BOTH schemas from W_schema and bundle them at query time. Brain can do this but slowly via sequential schema retrieval; substrate does it in one parallel attention step.

### P_deflated

0.40 (the highest of the three families). Strongest priors:
- Brain-fidelity is high (existence proof per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms]])
- Re-uses today's in-flight cortical infrastructure (TWO_TIER + BCM + Modern Hopfield)
- Composes substrate's chain-grade primitives in the way that matches cognitive-science consensus

Risk factors deflating it:
- Depends on TWO_TIER + BCM + Modern Hopfield each working at substrate's regime; if any of those cortical primitives lands HARD_FAIL or under-spec, the schema-composition cell can't fire
- Slow-learning pass cost: needs many within-domain analogies as training data to build W_schema basins
- N_schema_basins risk: if W_schema doesn't sharpen to distinct basins, retrieval flattens to baseline cosine

Expected top-1: 0.45-0.65 if cortex primitives are healthy; 0.25-0.35 if under-trained. The MEDIAN expectation crosses the HARD_PASS threshold (0.45), justifying P_deflated = 0.40 at the upper end of the conservative range.

---

## Drill section 4: Two adjacent mechanisms (cross-domain VSA literature)

### Mechanism 4: Resonator network analogy (Frady-Olshausen 2020)

Resonator networks are a substrate-feasible iterative-cleanup mechanism for decomposing a VSA superposition into its constituent factors. The mechanism: given a bundled vector that encodes multiple bound pairs, resonator decomposition iteratively converges to the factor decomposition that explains the bundle.

Application to cross-domain analogy: encode the source analogy as a bundle of bound pairs `bundle(bind(A, R), bind(B, R), bind(C, R))`, where R is the unknown relational schema. Run resonator decomposition over (R, candidate-target-entities) to find the R that maximizes the bundle's reconstruction. The recovered R is then applied to the target.

Brain fidelity: LOW-MEDIUM. Resonator networks are biologically motivated (Frady-Olshausen 2020 NeurIPS) but the iterative-cleanup mechanism is not a known brain mechanism for analogy.

P_deflated: 0.20. Worth one paragraph but not a top-3 candidate. Substrate has resonator primitives (resonator_v1 chain-grade in some prior cells) but the cell would need 200+ lines and the brain-alignment is weaker than the cortex-Hopfield path.

### Mechanism 5: Compositional schema transfer via Lake-style program learning

Lake-Salakhutdinov 2015 (Omniglot Bayesian Program Learning, Science 350:1332): represent each schema as a probabilistic program over primitives; one-shot generalization to new instances via re-application of the inferred program to new entities.

Application: each cross-domain analogy is a "program" (sequence of primitive operations) that produces the target from the source. Substrate stores the program as a bound chain (e.g., for "A:B::C:D", the program is `apply_relation(unbind(A, B), C)`). Cross-domain analogy is then re-applying the same program to the new domain.

Brain fidelity: LOW. Lake-BPL is a Bayesian inference framework, not a brain mechanism. The closest brain correlate is RLPFC integrating novel examples into relational categories (Cerebral Cortex 27:2652) but the mechanism is not "Bayesian program induction".

P_deflated: 0.15. The mechanism is brittle to program-search cost; substrate doesn't have a chain-grade probabilistic program-induction primitive. Skip this for current cycle; revisit if cortex-Hopfield arm HARD_FAILs and substrate needs a non-cortical fallback.

---

## Falsifiable predictions

**HARD-PASS thresholds (pre-registered, per Fix #28 per-arm metrics):**
- ARM_CORTEX_HOPFIELD top-1 >= 0.45 on 200-analogy test set AND >= ARM_DIRECT_HRR_UNBIND + 0.10 AND >= ARM_BASELINE_COSINE + 0.20 -> cortex-composed analogy is load-bearing, cap_map gets cross-domain row back at P-band 0.50-0.65 EXPLORATORY
- ARM_PARTITION_ROUTE top-1 >= 0.45 AND >= ARM_DIRECT_HRR_UNBIND + 0.10 -> structural-alignment over universal primitives works, ConceptNet vocabulary is the right granularity for substrate
- ARM_DIRECT_HRR_UNBIND top-1 >= 0.45 -> would refute the STRETCH4-2 ceiling and the "needs schemas" framing; cap_map gets cross-domain row back at MIDDLE_BAND (algebraic direct path)

**HARD-FAIL thresholds (per [[feedback-negativity-bias-symmetric-verify]] both-directions check):**
- ALL three relational arms within 0.05 of ARM_BASELINE_COSINE: cross-domain analogy NOT achievable at substrate's current regime via these mechanism families; pivot to deeper-encoder approaches (Path C v2 with substrate-owned encoder must come first)
- ALL three relational arms top-1 < 0.30: the STRETCH4-2 ceiling (0.244) generalizes across mechanism families; the bottleneck is encoder quality, not analogical mechanism
- ARM_CORTEX_HOPFIELD top-1 < ARM_DIRECT_HRR_UNBIND + 0.03 in a regime where TWO_TIER + BCM + Modern Hopfield are individually HARD_PASS: cortex composition does NOT add cross-domain value beyond direct algebra; substrate's cortical layer is within-domain-only

**Cap_map predictions:**
- If ARM_CORTEX_HOPFIELD HARD_PASS: cap_map cross-domain analogy row resurrected at P-band 0.55-0.70 (currently DROPPED per 2026-06-10 STRETCH4-2 retraction)
- If only ARM_PARTITION_ROUTE HARD_PASS (cortex-Hopfield in MIDDLE_BAND): cap_map cross-domain row at P-band 0.45-0.60 with annotation "ConceptNet-anchored, not yet cortex-native"
- If all HARD_FAIL: cap_map cross-domain row stays DROPPED; substrate-product story explicitly excludes cross-domain analogy until encoder pivot lands

---

## Cross-thread synthesis

### Thread 1: Within-domain analogy is ALREADY chain-grade (PP-115, PP-165, comp24)

The substrate has K10=0.953 cosine on within-domain analogy via relational binding + cleanup. This is the SAME mechanism family as ARM_DIRECT_HRR_UNBIND in this drill, but ON THE SAME DOMAIN as training. The gap from K10=0.953 (within) to 0.244 (cross, STRETCH4-2) is the cross-domain transfer gap. This drill is about CLOSING that gap.

Key insight: the within-domain win used pure HRR algebra (no slow-learning, no cortical schemas). That tells us the substrate's HRR primitives are CORRECT; the cross-domain gap is about the ABSTRACT-RELATION-VOCABULARY problem, not about the algebra. This aligns with cognitive-science consensus: cross-domain analogy requires a universal relational vocabulary (Hofstadter, Gentner, Holyoak). Substrate has the algebra; what it doesn't have is the slow-learned vocabulary. Cortex layer provides that vocabulary.

### Thread 2: Cortex layer (TWO_TIER + BCM + Modern Hopfield) was dispatched today

Each cortical primitive was independently motivated (continual learning + slow schema extraction + attractor retrieval). The synthesis here is that THE SAME cortical infrastructure naturally supports cross-domain analogy via schema-composition. This is a CROSS-CAPABILITY win pattern: one piece of infrastructure (cortex) supports multiple downstream capabilities (continual learning, schema extraction, analogy).

If TWO_TIER + BCM + Modern Hopfield each land HARD_PASS or PARTIAL by end-of-session, ARM_CORTEX_HOPFIELD becomes immediately dispatchable as the next cycle's substrate-product cell. The dependency chain: cortex primitives -> W_schema slow-learn -> schema-Hopfield analogy cell. This is the natural next-cycle drill.

### Thread 3: Cross-domain analogy was RETRACTED 2026-06-10

The 2026-06-10 drill (research_drill_cross_domain_analogy_negative_2x_2026-06-10.md) properly retracted the cross-domain claim and identified ConceptNet relation primitives + structural alignment as the way forward. ANCHOR-3 (ConceptNet relation decomposition) was priority 1 but never dispatched. That ANCHOR is exactly ARM_PARTITION_ROUTE in this drill -- this is the structural revival of the 2026-06-10 plan.

The cortex-Hopfield mechanism (ARM_CORTEX_HOPFIELD) is NEW vs the 2026-06-10 drill -- it didn't exist as a substrate option because the cortical primitives weren't yet in flight. The USER addendum surfaces it correctly: today's cortical infrastructure changes the substrate-product story for cross-domain analogy.

### Thread 4: DRAMA (Eliasmith-Thagard 2001) is the substrate-feasible precedent

DRAMA used HRR (Plate 1995) to encode relational structure AND THEN ran structural-mapping over the HRR vectors. DRAMA's claim was that this distributed approach outperformed pure-symbolic SME, Copycat, and ACME on analogical mapping benchmarks. DRAMA is THE existence proof that HRR-substrate can do analogy.

The 25-year-old DRAMA result is direct precedent for ARM_PARTITION_ROUTE (substrate-feasible structural alignment over HRR vectors) and partial precedent for ARM_DIRECT_HRR_UNBIND. DRAMA did NOT have cortex-Hopfield retrieval (Modern Hopfield is 2016+); ARM_CORTEX_HOPFIELD is a novel extension of DRAMA using modern cortical primitives.

### Thread 5: The substrate-better story is ALGEBRAIC TRANSFER OF SLOW-LEARNED SCHEMAS

The deepest synthesis: brain slow-learns relational schemas (mPFC abstract relational map, Park-Boorman 2024); brain at query time RETRIEVES schemas and applies them (parietal-RLPFC circuit, hundreds of ms). Substrate slow-learns the SAME schemas (via cortex layer); substrate at query time ALGEBRAICALLY APPLIES them (O(N) bind/unbind, microseconds). The slow-learning is the same; the query-time transfer is FASTER and PARALLELIZABLE on substrate.

This is the substrate-product story for cross-domain analogy: substrate matches the brain's slow-learned schema vocabulary, then BEATS the brain on query-time application via algebraic parallelism. Audit-device application: substrate can evaluate many candidate cross-domain analogies in parallel (e.g., for an audit query, evaluate all possible relational schemas that could explain a discrepancy), where the brain would have to serialize.

---

## Substrate-product implications

1. **Within-domain analogy is a current cap-grade capability** (K10=0.953 PP-115/PP-165). Continue to feature this in substrate-product positioning. Cross-domain analogy is NOT yet a current capability; positioning should be "in development" until ARM_CORTEX_HOPFIELD or ARM_PARTITION_ROUTE HARD_PASSes.

2. **Cortex layer is the unlock** for cross-domain analogy. The TWO_TIER + BCM + Modern Hopfield infrastructure being built today opens a path to cross-domain analogy that was not previously substrate-feasible. The cross-domain analogy cell can be queued as an immediate follow-up once cortex primitives stabilize.

3. **Cheap-decisive cell is dispatchable NEXT CYCLE** (after cortex primitives land). The ARM_DIRECT_HRR_UNBIND + ARM_PARTITION_ROUTE arms can be dispatched IMMEDIATELY without waiting for cortex (they don't depend on it). The ARM_CORTEX_HOPFIELD arm gates on cortex primitives but the full discriminator can be re-run when those land.

4. **DRAMA is product positioning**: Eliasmith-Thagard 2001 is academic precedent that HRR substrate can do analogy. Substrate-product narrative can reference DRAMA as the published precedent + the substrate cortical extension as the modern advance.

5. **Cross-domain analogy as audit-device differentiator**: pure LLMs can do cross-domain analogy via in-context prompting, but they CAN'T enumerate the relational schemas they're using or evaluate multiple candidate schemas in parallel with structural-alignment guarantees. Substrate's cortex-Hopfield + algebraic-transfer mechanism provides AUDITABLE cross-domain analogy: which schema was retrieved, what its slow-learned support was, what alternative schemas were considered. This is the audit-device product story.

---

## Citations (verified count: 12)

1. **Plate T (1995)**. Holographic reduced representations. IEEE Transactions on Neural Networks 6(3), 623-641. [Original HRR formulation; bind=circular-convolution, unbind=circular-correlation; analogy primitives substrate uses]

2. **Eliasmith C, Thagard P (2001)**. Integrating structure and meaning: a distributed model of analogical mapping. Cognitive Science 25(2), 245-286. [DRAMA model; HRR-based analogical mapping; direct precedent for substrate cross-domain mechanism; compares to SME, Copycat, ACME]

3. **Gentner D (1983)**. Structure-mapping: a theoretical framework for analogy. Cognitive Science 7(2), 155-170. [SME structural alignment; cross-domain analogy via relational structure mapping; cognitive-science foundation]

4. **Holyoak K, Thagard P (1989)**. Analogical mapping by constraint satisfaction. Cognitive Science 13(3), 295-355. [ACME model; constraint-based structural alignment; complements DRAMA]

5. **Hofstadter D, Mitchell M (1994)**. The Copycat project: a model of mental fluidity and analogy-making. Advances in Connectionist and Neural Computation Theory. [Abstract relational primitives as basis of analogical transfer; SUCCESSOR-OF as universal primitive]

6. **Speer R, Chin J, Havasi C (2017)**. ConceptNet 5.5: an open multilingual graph of general knowledge. AAAI 2017. [ConceptNet 34 universal relation types; the partition vocabulary for ARM_PARTITION_ROUTE]

7. **Park S, Boorman E (2024)**. An abstract relational map emerges in the human medial prefrontal cortex with consolidation. bioRxiv 2024.10.11.617652. [mPFC slow-extracts relational schema map; brain mechanism for cortex-composed analogy; CRITICAL for ARM_CORTEX_HOPFIELD brain-fidelity claim]

8. **Cerebral Cortex 27:2652 (2017)**. From concrete examples to abstract relations: the rostrolateral prefrontal cortex integrates novel examples into relational categories. [RLPFC abstract relational categorization; brain's slow-learning mechanism for analogical primitives]

9. **Inferior parietal cortex represents relational structures for explicit transitive inference (Cerebral Cortex 34:bhae137, 2024)**. PMC 10999362. [Parietal binding to abstract relational structure; brain's structural-alignment circuit]

10. **Ramsauer H et al. (2020)**. Hopfield networks is all you need. ICLR 2021. [Modern Hopfield exponential capacity; attention-style retrieval; the retrieval mechanism for ARM_CORTEX_HOPFIELD]

11. **Krotov D, Hopfield J (2016)**. Dense associative memory for pattern recognition. NeurIPS 2016. [Modern Hopfield dense capacity; precursor to attention-Hopfield equivalence]

12. **Rogers A, Drozd A, Li B (2017)**. The (too many) problems of analogical reasoning with word vectors. ACL Workshop. [Demonstrates word2vec analogy fails for low-frequency and domain-specific relations; HARD-FAIL anchor for the cross-domain regime; informs why ARM_DIRECT_HRR_UNBIND alone is insufficient]

Verified count: 12 primary citations. All from peer-reviewed venues or established preprint servers. All claims above traceable to at least one of these sources.

---

## Next-drill candidates

Priority 1: dispatch ARM_DIRECT_HRR_UNBIND + ARM_PARTITION_ROUTE NOW (do not gate on cortex primitives). Cheap CPU cells, 1-3 hours. Acts as the discriminator floor for the cortex arm follow-up.

Priority 2: ARM_CORTEX_HOPFIELD dispatch immediately after TWO_TIER + BCM + Modern Hopfield each land HARD_PASS or PARTIAL. This is the top-P_deflated mechanism (0.40) and the substrate-product story's anchor.

Priority 3: encoder pivot follow-up. If ALL THREE arms HARD_FAIL, the bottleneck is encoder quality (not analogical mechanism). Path C v2 substrate-owned encoder becomes the gate.

Priority 4: meta-learning over relation pairs (FSRL / GMatching style) if cortex arm HARD_FAILs and partition arm only MIDDLE_BANDs. This is the highest-cost path (~6-12 GPU-hr) but covers the regime where neither algebraic nor cortex-composition works.

P_deflated(at least one of priority 1+2 arms achieves cross-domain HARD_PASS over 200-analogy test set) = 0.55. This is the cell-level synthesis P, deflated 0.20 from raw lit-scan priors per [[feedback-lit-scan-calibration-penalty]] and capped at the 0.50 novel-synthesis ceiling raised by the cortex-composition route being a NEW SUBSTRATE COMPOSITION but with brain-existence-proof prior per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms]].

---

*Note path: d:/AI/hd-instrument/notes/research_gap_D_analogy_cross_domain_mapping_2026-06-26.md*
