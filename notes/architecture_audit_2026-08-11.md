# ARCHITECTURE AUDIT — the three-tier glass-box knowledge substrate (2026-08-11)

Synthesis of 3 parallel read-the-code cluster-audits (A=stores/gather/sources/encoders, B=reason/gate/middle/sweep, C=reading/canon/gap-detection/state-of-mind/grounding). All claims disk-verified (code read + metrics.json + registry + re-run self-tests + grep for real importers), not label-trusted. Deflated per-axis, never aggregate.

## GREAT / brain-foundational (keep as-is)
- **hd_fact_store** (HDFactStore): conjunctive role-filler HD memory, native (s,r) signature, trust-vetted ingest. Real-data proven (1.24M CSKG edges). Best-built organ. [caveat: WIRED_BUT_NOT_PIPELINE_REACHABLE]
- **situation_model_accumulate** (AccumulateRegister): Kintsch/Zwaan multi-event indexing; accumulate 1.0 vs overwrite 0.46 vs floor 0.21 on real McGuffey. WIRED_AND_PIPELINE_USED (best integration status). [caveat: upstream real-text role-extractor real=0.231 vs oracle=1.0 -> current use is oracle/synthetic-role]
- **gather_reason.ca3_relevance_gather + fanout_two_hop**: CA3 peel-loop + K<=2 relational fan-out. Strongest real-benchmark win (arm3@5 0.38 vs blind-union 0.04). [REASON honestly-scoped: shallow K<=2 associative read, not search/logic]
- **cleanup_family.iterative_attractor**: CA3/DG canonical soft attractor. Heavily reused.
- **three_tier_loop** (ThreeTierLoop): the assembled loop. Real-data HARD_PASS (delta_B=1.00, delta_C=0.645). e2e witness sabotage-verified.
- **grounding_acquisition_loop.consolidation_pass** (the GATE): Logan instance-count + Schneider-Shiffrin consistency + schema-coherence false-memory guard. [MEH only on registry hygiene: UNREGISTERED despite backing 2 WIRED rows]
- **prelim_tier** (MIDDLE-db) retain-forever + ScriptLibrary CA3/DG sweep-keying. Retain proven (delta_B=1.00). [envelope caveat below]
- **content_repr_vector** (canonicalization primitive): bind(REL,ARG0,ARG1) -> bit-identical vector, native store dedup, zero similarity-call in retrieval. Genuine ATL-hub amodal encoding. GREAT.
- **char_trigram_encoder**: great at its narrow orthographic job; zero mislabel (never claims meaning).

## MEH / second-look, ranked by IMPACT

### TIER 1 -- the deepest ceiling (assets already exist, only the wire is missing)
1. **MEANING is a ~380-word HAND-TAGGED lexicon, while 2 bigger built assets sit UNUSED.** The live similarity/animacy path reaches only lexical_similarity.CONCEPT_FEATURES (~230 hand-typed concepts) + verb_lexical_similarity (~150 lemmas). Meanwhile: (a) 39,707-word grounding norms (Lancaster sensorimotor / Brysbaert concreteness / Warriner VAD / AoA in data/grounding_testbed) = a grep-confirmed DISCONNECTED ISLAND (zero live inference paths; registry self-flags cskg_foundation_v1 as expected-island); (b) scale_win_tinytransformer_encoder = a LEARNED-from-scratch transformer on 237.7M ARC tokens, "beats grounding +0.050 semantic/+0.071 relational", gate=WIRE, but integration_status=TRAPPED_SHARED, zero hdlab imports. **Impact: VERY HIGH (the deep grounding ceiling; everything reads through meaning). Effort: S/M (wire existing assets).** = THE #1 shore-up. Anti-over-merge is the decisive guard.

### TIER 2 -- the reading/extraction upstream bottleneck (recurring across all 3 clusters)
2. **Reading extractor depth**: SVO/passive pattern-matcher, 38 hand-picked verbs -> 3 classes (CONSUMED/PRODUCED/MOVED); closed-schema IE, not comprehension. Every downstream fact traces through it. Also surfaces as: situation_model has no real-text role-extractor (real 0.231 vs oracle 1.0); FHRR-store HARD_FAIL is upstream ~85% tagging-skip. **Impact: HIGH. Effort: L** (open-vocab predicate recognition; helped by TIER-1 grounding).
3. **Gap-DETECTION has no autonomous component** (MISLABEL): every "gap" is an offline KB set-difference or a hand-picked curriculum. No online prediction-error/surprise/confidence -- the machinery has never run on a gap it found itself. **Impact: VERY HIGH (the autonomy gap for real reading). Effort: L** (new organ: CA3-gather-confidence vs a decision floor mid-read).

### TIER 3 -- combination/sweep claims narrower than the headline
4. **The SWEEP's combined-evidence promotion has NEVER fired on real SPARSE data** -- only on templated-6-visit-repeat (delta_C 0.645). On every genuinely-sparse real-source regime (independence_weighted_confirm, concept_coherence) n_combined_promoted=0. The core generalization claim is unproven under realistic conditions. **Impact: HIGH. Effort: M.**
5. **The clustering key is a LITERAL shared-entity-string match (via_material), NOT semantic** (CORRECTION: the semantic-embedding key v2 ALSO HARD_FAILED per prelim_tier's own docstring; the coarse relation-type key was the first fail). Works by domain-coincidence. **Impact: MEDIUM (generality). Effort: M.**
6. **Multi-source coverage measured-thin**: max 3 real sources/gap, {1src:67, 2:46, 3:8} over 121, go.obo=0 usable, MIN_CONFIRM=4 structurally unreachable. The literal "gather from many DBs" gap. **Impact: HIGH. Effort: M-L** (add ChEBI/KEGG-live/WorldTree/OpenStax/WikiHow).

### TIER 4 -- wire-don't-island + hygiene
7. **glass_box_loop UNWIRED**: a validated (real ConceptNet V=48000) Go/NoGo value-gate + Merkle audit-trail mechanism -- exactly the arbitration/fusion three_tier_loop.answer() lacks (Gap G1) -- sits with zero importers. **Impact: MEDIUM-HIGH. Effort: M.**
8. **Islands + registry gaps**: multi_hop.py (CERT 585, zero importers, duplicative with fanout_two_hop) + script_consolidation_pass (prioritized-replay, never called live) are orphans; 4 load-bearing modules UNREGISTERED (glass_box_loop, grounding_acquisition_loop, multi_hop, script_grain_acquisition_loop) -- an audit trusting the registry alone would conclude the GATE doesn't exist. **Impact: process-integrity. Effort: S.**
9. **Uncommitted/untracked hdlab files** (arc_parser, pos_tagger, coref, candidate_generator, ... + modified kg_traversal.py, lexical_similarity.py): likely leftovers from the old goal-owner/thematic-role frontier OR a concurrent session. LEFT UNTOUCHED (concurrent-session caution). Reconcile before a clean commit.

## HONEST CORRECTIONS the audit forced (the discipline working)
- "semantic clustering key fixed the sweep" -> FALSE; the semantic key ALSO failed; the wired key is domain-coincidence string-match.
- "same-representation earned" -> the PRIMITIVE (content_repr_vector) is great, but the entity/relation canon relies on the ~380-word hand-lexicon => proven on covered vocab, NOT open-vocab.
- "FHRR store 0.956 proven" -> 0.956 is REPRESENTATION-only; the real-corpus integration HARD_FAILED (upstream tagging), never root-caused.
- "independence-weighting" -> on real data it has only ever been a ">=2 distinct sources y/n" rule; the repeat-decay/correlated machinery is synthetic-self-test-only; numbers reverse-engineered to the boundary.
- "gap-detection" -> an offline KB set-difference, not detection.
- reading "concreteness gate" -> actually a WordNet-category lookup (animacy_lexicon), not concreteness.

## SHORE-UP ORDER (worst-first, brain-foundational, right-path)
1. **GROUNDING/MEANING wire-in (TIER-1)** -- highest impact x lowest effort; the foundation the reading curriculum needs (grounding IS the prerequisite, per the curriculum principle). Wire the 39K sensorimotor/concreteness norms (perceptual grounding = most brain-foundational) and/or the 237M-token learned encoder into concept_similarity's fallback. Decisive guard: anti-over-merge (distinct concepts MUST stay distinct) + no-regression on proven results. DRIVING FIRST.
2. **Reading-depth / real-text extraction** (open-vocab, aided by #1's grounded meaning).
3. **Gap-detection autonomy** (the online "notice what I don't know" organ).
4. **Sweep on real sparse data + a real semantic clustering key** (test the combination claim under realistic conditions).
5. **Multi-source coverage** (add real complementary sources).
6. **Wire-don't-island + registry hygiene** (glass_box_loop into answer(); the 4 missing rows; reconcile the untracked files) -- do as cleanup alongside.
