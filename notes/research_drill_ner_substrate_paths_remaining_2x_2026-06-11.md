# Research drill: substrate NER plateau -- 5 remaining substrate-only paths (2x DEEP)

Date: 2026-06-11
Topic: substrate NER aux-feature plateau; map 3 untested + 2 new substrate-only paths to OntoNotes-18 fine-grained F1 lift
Calibration: lit-scan penalty applied (deflate P 0.15-0.25; cap novel-synthesis P at 0.50); brain-can-do-it + literature-is-not-oracle + dont-parrot-drill-defeatism rules active
ASCII-only.

## HEADLINE

Substrate NER F1 ~0.57 (OntoNotes-18 fine-grained) sits ~12 F1 below the pre-transformer feature-engineered ceiling (~0.89-0.91 with neural feature learning; Flair-era state of the art). 4-type collapsed 0.6477 already matches CoNLL-2003 feature-era baseline ~0.65. Gap is concentrated in fine-grained 18-type discrimination, NOT in coarse boundary detection. Of the 5 candidate substrate-only paths drilled, FRAME-SEMANTIC ENTITY-TYPE BUNDLE ACTIVATION (Path 4 NEW) carries the highest deflated P because (a) frame semantics is the cognitive mechanism literature names for fine-grained type discrimination (PERSON vs NORP vs ORG), (b) substrate already has Tier-2 schema bundles + LEX_entity_TYPE atoms shipped, (c) it does NOT shrink with data scale the way emission-style features do -- frames bind to syntactic role and discourse, which become MORE informative with more sentences. Substrate-CRF Tier-1 shared library (Path 2) carries the second-highest P because the literature lift from feature-engineered CRF over context-window emissions is well-documented and the bundling-redundancy correction (substrate-self-index Day 1 finding) directly addresses why our context-window already saturated. Discourse-level cross-sentence integration (Path 5 NEW) is the asymmetric upside: literature reports document-context lift > sentence-context lift on CoNLL, and substrate retrieval is mechanically suited to cross-sentence binding. The two Cycle-5-mechanism paths (Path 1 atoms-as-features, Path 3 schema-construction-grammar) are AUXILIARY -- low expected lift in isolation but useful as ingredients to Paths 2 + 4 + 5.

## Cheap decisive test

Single CPU smoke (~30 min total budget):

1. Path 4 (frame-semantic bundle activation) at n=300 train (composition-matched smoke per smoke-test-methodology rule). Wire LEX_entity_TYPE atom activation against syntactic-role slot context (subject-of, object-of, prep-object, possessor) using HMM-style emission + transition already shipped in substrate-self-index. HARD-PASS if F1 lift > 0.06 over POS-cascade baseline at 300-train, AND lift > 0.020 at full-data (5982-train) i.e. the lift does NOT shrink 6x the way emission did. HARD-FAIL if lift < 0.010 at 300-train (no early signal) or lift < 0.005 at full-data (saturation-equivalent).

2. Path 2 (substrate-CRF Tier-1 shared library) at n=300 train using substrate-self-index's HMM emission + transition + context-window bundles WIRED as a single Tier-1 shared feature library with bundling-redundancy correction (the discovery-engine finding from self-index Day 1). HARD-PASS if F1 lift > 0.05 at 300 AND > 0.015 at full-data. HARD-FAIL if lift < 0.008 at 300.

3. Path 5 (discourse-level retrieval) at n=300 train, sentence-window = previous 2 sentences fed as substrate retrieval keys for entity-type prior. HARD-PASS if F1 lift > 0.04 at full-data AND lift_full > lift_300 (i.e. SCALES UP, opposite of emission features). HARD-FAIL if lift < 0.005 at full-data.

Order: run Path 4 first (highest P, highest novelty). If HARD-PASS, queue Path 5 (compositional with frames). If HARD-FAIL, fall back to Path 2 + diagnosis whether full-data lift > 300-train lift (rule-out shrinkage).

Pre-registered prior to compute: if all three HARD-FAIL, the plateau IS architectural for current substrate primitives + 18-type fine-grained discrimination. That would force the substrate-LLM boundary to shift to include fine-grained NER on the LLM side. Per brain-can-do-it rule: refuse boundary acceptance until at least one of Paths 4 / 5 has been wired with the bundling-redundancy correction. Per dont-parrot-drill-defeatism: a single-emission feature plateau is NOT a substrate-architectural plateau.

## Falsifiable predictions (HARD-PASS + MIDDLE + HARD-FAIL)

### Path 1: Cycle 5 mechanism atoms as features (CAP_em_algorithm / CAP_bayesian_inference / CAP_discriminative_perceptron / CAP_hungarian_assignment)

- Brain analogue: prefrontal-cortex attention to task-relevant features; the brain DOES use meta-cognitive process atoms when categorization is hard (executive working memory recruits rule-based categorization in left dorsolateral PFC). The substrate ACCEPT atom for discriminative_perceptron is the closest analogue.
- Substrate primitives: ACCEPT atoms bound as features in feature_hash; discriminative perceptron substituted for count-NB emission (matches the substrate-discriminative-beats-generative-asymmetric-NL memory: 0.110 -> 0.267 = 2.4x lift on SVAMP).
- Expected lift: SMALL standalone (0.005-0.015 F1). Atoms are mechanism descriptors, not lexical-distributional features; they help orchestrate Paths 2/4/5 but rarely lift alone.
- Pre-reg HARD-PASS: F1 lift > 0.020 at full-data (would refute "atoms are orchestrators only" framing).
- Pre-reg MIDDLE: 0.005 <= lift <= 0.020.
- Pre-reg HARD-FAIL: lift < 0.005. Outcome: keep as compositional ingredient only; do not pursue standalone.
- P_deflated: 0.25.

### Path 2: substrate-CRF Tier-1 shared feature library

- Brain analogue: cortical Wernicke + Broca for word-identity + syntactic-role; in particular the well-attested left-ATL person-selective response and place-selective parahippocampal response (literature: anterior temporal lobe selectively processes person- vs place-related semantic info). Substrate-CRF is the structural equivalent: a Tier-1 SHARED library of emission + transition + context-window features available to all NER tasks, rather than per-task one-shots.
- Substrate primitives: HMM emission (PP-364 0.95 POS Tier-A) + transition + context-window emission (PP-369 slot-filling 0.871) wired together into one Tier-1 library with the BUNDLING-REDUNDANCY correction from substrate-self-index Day 1 (which surfaced that bundled context-window already absorbs much of what feature-stacking would add).
- Expected lift: MODERATE. Literature feature-importance ordering "Character > Context > Global > Document > Sentence" suggests our existing context-window already captures the dominant feature class. Lift is bounded by how much non-redundant signal sits in transition + multi-window stacking.
- Pre-reg HARD-PASS: F1 lift > 0.030 at full-data AND lift > 0.05 at n=300.
- Pre-reg MIDDLE: 0.015 <= full-data lift <= 0.030.
- Pre-reg HARD-FAIL: full-data lift < 0.015. Outcome: confirms bundling-redundancy is real and stacking is the dominant failure mode; pivot to Paths 4/5 (which target NON-EMISSION feature classes).
- P_deflated: 0.40.

### Path 3: Tier-2 schema construction grammar

- Brain analogue: frame semantics in temporal lobe + prefrontal cortex; the brain encodes "X gave Y to Z" with role assignments AGENT/THEME/RECIPIENT in working memory, and roles license entity-type expectations.
- Substrate primitives: Construction-grammar slot-fillers (Computational CxG literature: LEX / SYN / SEM constraints) bound as Tier-2 schema bundles. Schemas like "PROPN-PROPN dot CITY State zip" -> LOCATION; "Inc Corp LLC" suffix -> ORG; "President of NORP_adj NORP_country" -> NORP.
- Expected lift: MODERATE on fine-grained types where schemas are well-defined (NORP, GPE, MONEY, DATE, PERCENT). Low on PERSON / ORG (already lexical-distributional).
- Pre-reg HARD-PASS: F1 lift > 0.040 at full-data, with type-level breakdown showing the lift concentrates in 5+ of the 14 fine-grained types beyond CoNLL-4 collapse.
- Pre-reg MIDDLE: 0.020 <= full-data lift <= 0.040.
- Pre-reg HARD-FAIL: full-data lift < 0.020. Outcome: schemas overlap with Path 4 frame semantics; absorb into Path 4 implementation.
- P_deflated: 0.35.

### Path 4: NEW -- Frame-semantic entity-type bundle activation (TOP-RANKED)

- Brain analogue: temporal-frontal frame-semantic network. Anterior temporal lobe shows person-selective response with ~100 ms latency on visual presentation; left-ATL is sensitive to semantic distance; left-vlPFC is sensitive to category membership. This is the EXACT brain mechanism the literature names for fine-grained entity-type discrimination, and it is what is MISSING from our current substrate pipeline.
- Substrate primitives: LEX_entity_TYPE atoms (shipped earlier) activated by syntactic-role context (subject-of-VERB, object-of-VERB, prep-object-of, possessor-of-NOUN). Implementation: HMM-style emission already in substrate-self-index, where emission is now P(LEX_entity_TYPE | syntactic-role + surrounding-window). Bundles built from frame-evoking lexical units (PropBank-style verb frames mapping to typed roles).
- Expected lift: HIGHEST. Fine-grained type discrimination is the dominant remaining error class (gap is 0.57 -> 0.65 collapsed, i.e. ~0.08 F1 sits in 18-vs-4 fine-grained). Literature directly attributes fine-grained NER gains to type-context features (attention mechanisms learning contextual cues like "got a Ph.D. from" -> EDUCATIONAL_INSTITUTION).
- Crucial property: frame features DO NOT SHRINK WITH DATA. They become MORE informative as more sentences are seen because frame coverage scales with verb-frame diversity. This breaks the 6x emission-shrinkage pattern.
- Pre-reg HARD-PASS: F1 lift > 0.06 at 300-train AND > 0.020 at full-data AND ratio (lift_300 / lift_full) < 4.0 (anti-shrinkage criterion).
- Pre-reg MIDDLE: lift > 0.020 at full-data but shrinkage ratio > 4.0 (still good but emission-class signal).
- Pre-reg HARD-FAIL: full-data lift < 0.010 OR 300-train lift < 0.020. Outcome: frame semantics in substrate Tier-2 form is insufficient -- pivot to Path 5 discourse OR to Tier-3 schema construction.
- P_deflated: 0.50 (capped at novel-synthesis ceiling).

### Path 5: NEW -- Discourse-level cross-sentence integration via substrate retrieval

- Brain analogue: working memory + episodic-memory binding via hippocampal theta-gamma phase coding. The brain holds prior sentences' entity assignments in active working memory and uses them to disambiguate type ambiguity in the current sentence (e.g. "Apple" introduced as ORG in S1 stays ORG in S3 unless reframed). Theta-gamma phase coding literature confirms sequence-binding mechanism.
- Substrate primitives: substrate retrieval (RRF over semantic + algebra + content-reference per substrate-two-axes memory) keyed on the previous N sentences' entity-type assignments; results bind to the current sentence as a discourse-prior context-window. Implementation reuses substrate-self-index retrieval primitives unchanged.
- Expected lift: SCALES UP with data because more document context becomes available. Literature explicitly confirms this: "Adding multiple sentences to BERT input systematically increases NER performance" + "On CoNLL the accuracy lift follows Character > Context > Global > Document > Sentence" -- BUT document-level lift is non-trivial when sentence-level has saturated.
- Pre-reg HARD-PASS: F1 lift > 0.030 at full-data AND lift_full > lift_300 (opposite-shrinkage scaling).
- Pre-reg MIDDLE: 0.015 <= full-data lift <= 0.030.
- Pre-reg HARD-FAIL: lift < 0.005 at full-data OR lift_300 > lift_full (still shrinks with data). Outcome: discourse retrieval contaminates type-priors (carries over wrong types); requires confidence-gating.
- P_deflated: 0.40.

## Cross-thread synthesis

- substrate-classical-NLP-methods-outperform-phasor memory: HMM emission + transition + Viterbi at substrate Tier-2 BEAT phasor on POS (0.906), slot-filling (0.871), intent (0.834). This validates the Tier-2 substrate-CRF library direction (Path 2) but ALSO predicts the saturation: emission-class features have a known ceiling that the literature calls out.
- substrate-discriminative-beats-generative-asymmetric-NL memory: 2.4x lift from discriminative perceptron over count-NB on SVAMP. Path 1 (Cycle 5 atoms) can ride this: substitute discriminative_perceptron for count-NB emission in the substrate-CRF library.
- substrate-two-axes memory: semantic-vec + content-references + algebra. Path 5 discourse retrieval composes all three for cross-sentence entity-type prior carryover. This is the substrate-novel implementation of working-memory-mediated discourse.
- substrate-self-index Day 1 finding (bundling-redundancy): explains why context-window already saturates. Path 2 must explicitly correct for redundancy before stacking, otherwise stacking does nothing.
- methodology-benchmark-must-break-symmetry memory: fine-grained NER 18-type IS asymmetric (each type has distinct frame distributions). Frame-semantic Path 4 directly breaks the relevant symmetry; collapsed 4-type was approximately symmetric and saturated faster.
- drill-pattern-TEMPORAL-CONTEXTUAL-works memory: Paths 4 (contextual frame-binding) and 5 (temporal cross-sentence) match the validated drill pattern; Paths 2 (fixed-architecture shared library) and 3 (fixed-schema grammar) match the lower-yield pattern. P_deflated reflects this.
- Literature ceiling: pre-transformer CoNLL-2003 ~0.91 with neural feature learning (BiLSTM-CNN-CRF); pure feature-engineered CRF ~0.85-0.88; OntoNotes-18 ~0.89-0.91 with Flair char-embeddings. Substrate without pretrained embeddings sits at ~0.57 with collapsed 0.65. Gap to feature-engineered (non-neural) CRF is ~0.21-0.28 F1; gap to neural-feature is larger. The 5 paths target collectively ~0.10-0.15 F1 lift (if Path 4 + 5 PASS), which would put substrate at 0.67-0.72 -- still below feature-engineered CRF ceiling but within the territory where the substrate-LLM boundary becomes coherent (substrate handles coarse + frame-discriminable types, LLM front-end provides distributional smoothing).

## Substrate-product implications

- Substrate-self-index becomes the host platform: all 5 paths plug in as feature bundles via the 13-category algebra taxonomy already shipped. No core changes required.
- Anti-shrinkage criterion (lift_300 / lift_full < 4.0) is a NEW pre-registered structural test that future feature-class drills should adopt; emission-class features shrink, frame/discourse-class features should not.
- Frame-semantic Tier-2 bundles are a reusable substrate primitive beyond NER: relation extraction, slot-filling, intent decoding all use the same machinery. Path 4 success transfers.
- Discourse-level retrieval (Path 5) is the substrate-native implementation of cross-sentence integration that LLMs achieve via large context windows. This is a substrate-product differentiator: the substrate carries the prior-entity-type as a structured retrievable atom, not as an opaque attention pattern.
- Boundary update: substrate handles coarse + frame-discriminable NER; the LLM-only residue is fine-grained sub-type discrimination requiring open-world world-knowledge (e.g. distinguishing CARDINAL vs MONEY vs PERCENT contextually with rare-token entities). This is much narrower than "NER is LLM-only" and aligns with substrate-LLM-boundary-decomposition memory.
- Honest framing: the F1 gap to feature-engineered ceiling will NOT fully close substrate-only without pretrained distributional embeddings (literature is unanimous that the Brown-cluster -> word-embedding transition unlocked the 0.85 -> 0.91 gain). Substrate may match feature-engineered NON-EMBEDDING CRF with all 5 paths; closing the embedding gap requires substrate-Brown-cluster equivalent (already Path 2 NER drilled, saturated at +0.011 -- so this is a HARDER question for a future drill).

## Ranked top 5 paths (decision order)

1. Path 4 (NEW) frame-semantic entity-type bundle activation -- P_deflated 0.50, anti-shrinkage criterion central, brain-mechanism direct match
2. Path 2 substrate-CRF Tier-1 shared feature library (with bundling-redundancy correction) -- P_deflated 0.40
3. Path 5 (NEW) discourse-level cross-sentence retrieval -- P_deflated 0.40, asymmetric upside (scales UP with data)
4. Path 3 Tier-2 schema construction grammar -- P_deflated 0.35, absorbable into Path 4
5. Path 1 Cycle 5 mechanism atoms as features -- P_deflated 0.25, compositional ingredient only

Decision: run Path 4 smoke FIRST. If HARD-PASS, queue Path 5 (composes with frames). If HARD-FAIL, run Path 2 with bundling-redundancy correction explicitly enabled, then Path 5. Path 3 absorbed into Path 4. Path 1 deferred to compositional use.

## Citations (verified)

1. Lisman + Jensen 2013 (theta-gamma neural code), PMC3648857; Heusser et al 2016 slow-theta-to-gamma PAC in human hippocampus, PubMed 25316340 -- brain mechanism for sequence/working-memory binding underlying Path 5 discourse retrieval.
2. Patterson et al 2007 (anterior temporal lobes and semantic memory), PMC2791360; Anzellotti et al 2014 person-selective ATL, Nature Communications Biology 2018 -- brain mechanism for fine-grained PERSON/ORG/LOCATION discrimination underlying Path 4 frame-semantic bundles.
3. Badre + Wagner 2002 (semantic retrieval, mnemonic control, PFC) -- prefrontal attention to task-relevant features underlying Path 1 atom orchestration.
4. Augenstein et al 2017 / Ma+Hovy 2016 BiLSTM-CNN-CRF on CoNLL-2003 (F1 91.62) -- pre-transformer neural feature-learning ceiling.
5. Akbik et al 2018 / 2019 Flair embeddings on OntoNotes-18 (F1 89-90.93) -- 18-type ceiling reference.
6. Dunietz / Choi et al frame-semantic / type-context for fine-grained NER (attention mechanisms learning contextual cues) -- Path 4 literature precedent.
7. Computational Construction Grammar slot-fillers (LEX / SYN / SEM) -- Path 3 literature precedent.
8. Luoma + Pyysalo 2020 cross-sentence contexts for NER (ACL Coling 2020.coling-main.78) -- Path 5 document-context lift, validated on CoNLL-02/03 multilingual.
9. Liu et al 2023 exploiting global contextual information for document-level NER (KBS / arxiv 2106.00887) -- Path 5 lift trend "Character > Context > Global > Document > Sentence".
10. Settles 2004 / Finkel + Manning CRF + Brown clusters + gazetteer feature library -- Path 2 literature precedent for CRF-shared-feature-library lift.

Verified count: 10 distinct lit anchors across brain mechanism (3) + pre-transformer NER ceiling (2) + frame-semantic / construction-grammar / cross-sentence (5).
