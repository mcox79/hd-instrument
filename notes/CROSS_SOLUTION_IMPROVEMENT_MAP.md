# CROSS-SOLUTION IMPROVEMENT MAP — the reverse-index that propagates improvements

**Purpose (owner 2026-09-09):** every recent solution flagged (a) what it still needs improved UPSTREAM, and (b) what
INPUTS its component consumes. Correlating those across solutions reveals that improvements are NOT siloed — a handful of
shared components are named again and again. **So when a NEW discovery improves component X, this map tells you exactly
which already-"done" solutions to REOPEN and re-measure.** Built by mining the ~36 most recent + load-bearing solutions
(INTEGRATION_LEDGER CONT-11→29 + the 4 WIP); ~145 older/perf/infra solutions have no flagged needs (byte-identical, fully
realized) and are not itemized.

**HOW TO USE.** You improved / are about to improve component X? → grep this file for X in **PART 2 (the reverse-index)**:
it lists every solution that FLAGGED X as its wall + every solution that CONSUMES X. Re-open and re-measure those.

**⚠️ DISK-VERIFY BEFORE ACTING.** Flagged-needs here are lifted from each solution's SOLVED.md *as written at its time* — some go stale as later work lands. Always verify the claim on disk before building (e.g. the "C8 DBpedia asset unbuilt" claim below was STALE — the asset is built + live as of 2026-09-09). Disk outranks this map.

**MAINTENANCE RULE (keep it a live reverse-index).** When you integrate a new SOLVED, add one row to PART 1 (component +
BF status | inputs consumed | flagged needs) AND append the solution's slug under each PART-2 target it consumes or flags.
Each brief's `ADJACENT COMPONENTS` + `NEXT STEPS` sections are the source. Cross-ref `notes/bf_status_registry.jsonl` for
the BF status of every component named here (79 organs certified 2026-09-09; the live set is 100% tagged).

---

## PROPAGATION STATUS (owner Q3 2026-09-10: "have we introduced later-solver updates into the earlier components they flag?")
The reverse-index is the LOG; this is the running ANSWER of what has actually been propagated vs. queued.
- **✅ PROPAGATED (later-solver update → applied to the earlier component):** the rung-1 relabel (causal solver) → `predictive_world_model` + the live `situation_reader` causal-antecedent read; `causal_sign` (causal solver) → wired live as `sm.causal_sign`; FIX-A recency (name-bridge) → *tested* on the live `crosstype_bridge` experiencer path (population-specific, correctly not flipped); the grown-knowledge assets (who_is_who_lexicon, Warriner VAD, directional store, directed causal store) → registered in `KNOWLEDGE_ASSET_REGISTER.md`.
- **✅ TARGET 1 PARSER (CONT-126, pri-3 integrated):** the parser-cluster located-negative characterization → folded to §2b (the wall is the SCORER acquisition ~99%, not the decode; the 5 NOT_BF parser organs keep their tags with the sharper residual = scorer/POS acquisition). CONSUMES: POS tags + token stream. FLAGS: the supervised arc SCORER acquisition = the deep 20.7-pt gap → the reading-learned scorer follow-on = pri-2 `scale_the_reading_learned_arc_scorer…` (enriched with pri-3's proven 0.463/DMV-refuted/structure-lever results). **NOT propagated to the live head path (Q125):** the decode/marginal route-through targets the arc-FACTORED parser, but the live head path is arc-EAGER (owner-DONE consolidation) → route-through is a measure-first follow-on, not applied (would reverse the consolidation for +0.002). The ~16 downstream consumers of the parser cluster are UNAFFECTED (no head change).
- **⏳ QUEUED ON THE REVIEW WAVE (the biggest propagations):** pri-3 the parser BF fix (once owner-DONE) → propagates to ~16 downstream consumers (Target 1); pri-4 `typed_coref` → replaces `commonnoun_binder` across the coref layer (Target 3); pri-7 Wolff force-dynamics → the causal/affect valence consumers. All three are fleet-SOLVED, awaiting owner review; propagation fires at integration.
- **🛠️ READY-FOR-ITS-USE-CASE (not a gap):** `safe_kb_gate` (name-bridge) is landed but has NO live consumer — CORRECT: the name-bridge solution measured it **coverage-NEUTRAL on the current clean KBs** (it protects a *broad/noisy* KB under noise, 0.61→0.40 ungated vs 0.60 gated); it activates when a broad KB is acquired (the world-model program), not on today's curated C8/entity KBs.
- **RULE:** at each owner-DONE integration, walk PART 2 for the integrated solution's components and apply/queue every consumer update; record the result here.

## PART 2 — THE REVERSE-INDEX (by target, ranked by leverage: "improve X → revisit these")

### 🥇 TARGET 1 — THE PARSER / EXTRACTION FRONT-END — ~16 solutions
`pos_tagger` + `arc_parser`/`arceager_parser`/`arc_labeler` (all **NOT_BF**: frozen supervised avg-perceptron, hard-decode
discards marginals) · `graded_parser` (Matrix-Tree marginals, the BF route) · `incremental_parser` (BF_SPIRIT, the named replacement).
- **FLAGGED it as their wall:** `replace_the_greedy_arc_eager…` (scorer FEATURES are the wall, decode/normalization solved),
  `improve_the_parser_verb_argument_attachment…` (+0.15-to-ceiling = verb→arg attachment), `the_who_did_what_selection_residual…`,
  `represent_negation_and_quantifier…` (parser-repair NET-NEGATIVE on general POS → needs tagger-confidence gating),
  `the_situation_model_has_no_goal_intention_dimension` (bare-purpose attachment parse-gated 0.33 vs oracle), `the_agent_tie_wall…`,
  `upgrade_the_pos_tagger…`/`crf_tagger` (OOD word-order = dominant leak), `structural_do…`, `extract_…whole_subgraph_survival`
  (NOT_BF upstream = the residual), `build_the_obl_spatial_defer_consumer…` (arc scorer surface-feature, 18% confident-wrong),
  pri-2 / pri-5 / pri-1 (all name `incremental_parser` as the fix), `add_the_arc_labeler_fast_scoring_path…` (~21% heads wrong).
- **CONSUMES it live:** every who-did-what/role/coref/temporal/spatial/causal reader (`joint_relation_frontend`,
  `predicate_argument_frontend`, `graded_role_assigner`, `situation_reader`).
- **Fleet home:** pri-1 `build_the_generative_result_state_world_model` (route through `incremental_parser`+`graded_parser`, close the top-down loop).

### 🥈 TARGET 2 — THE MEANING CHANNEL / REPRESENTATION — ~15 solutions
`grounded_similarity` (BF_SPIRIT) · `meaning_foundation` (BF_SPIRIT, LATENT loader) · `conceptual_meaning` (BF_SPIRIT) ·
`distributional_meaning_channel` · `reader_meaning_channel` (MISSING — no read()-time consumer) · `convergent_cue_reader` (fitted DEFAULT_W).
- **FLAGGED it / gated on it:** `build_and_freeze_the_clean_curated_foundation`, `grow_broad_coverage_rare_sense…`,
  `build_the_atl_hub_and_spoke…`, `break_the_contextual_input_encoding_ceiling…`, `build_the_controlled_knowledge_growth_consolidation_gate`,
  pri-2 `the_meaning_representation_is_a_point_vector…` (relation-blindness = the NEXT gap), pri-5 `measure_end_to_end…` (grounded-dominant read),
  `replace_the_attractor_as_ranker…` (fusion-wire + relational is-a = 214× lever), `audit_the_grounding_acquisition…` (G1: read-out LOSES to word-counting),
  `infer_unstated_emotion…` (Tier-2), `gate_the_eventive_nominal…` (event-vs-result WSD), `causal_mental_bridge` (contextual WSD),
  `theory_of_mind` (desired-VALUE), `reason_over_the_causal_network` (densification).
- **CONSUMES it live:** `bridging_inference` (1st consumer), `underspecified_sense_reader`/`select_sense`, `structured_matcher`, `reading_grounding_loop`.
- **CONVERGENT SUB-FINDING (5 solvers, PART-3 cluster #1): the wall is the REPRESENTATION (point-vector cosine / bag-of-words), NOT the computation.** Fleet home: pri-2 (population-code) + pri-5 (grounding-coverage measurement).

### 🥉 TARGET 3 — COREF / ENTITY-BINDING LAYER — ~14 solutions
`coref` (BF_SPIRIT + the OUR-INVENTION aliaser) · `typed_coref` (BF_SPIRIT) · `commonnoun_binder` (**NOT_BF**, string-identity) ·
`online_entity_cluster` (BF_SPIRIT) · `event_centrality_coref` (BF_SPIRIT) · `entity_world_model_resolver` (BF_SPIRIT, dormant) · `crosstype_bridge` (BF_SPIRIT).
- **FLAGGED it as their cap / consumes it:** `the_situation_model_has_no_affect_emotion_dimension` (**coref = 87% of loss**),
  `infer_unstated_emotion…` (experiencer), `wire_the_copular_state_qa_consumer` (cross-sentence canonical-entity binding),
  `the_world_state_register_is_coref_blind…`, pri-1 `grow_the_causal_mechanism…` (coref lifts causal 3.29×), `report_the_typed_coref…`,
  `improve_the_common_noun_coref…`, `compose_the_unified_referent…`, `strengthen_the_cue_based_pronoun_coreference…`,
  `the_name_branch_shatters…`, `seed_the_entity_world_model_resolver…`, `form_a_discourse_referent…`,
  `replace_the_entity_gate_gold_coref_inheritance…` (de-leak = the #1 blast-radius unblocker), `acquire_wikidata_p31…` (name-bridge).
- **SHARED WALL: the common-noun/name residual is ~84–88% WORLD KNOWLEDGE (encyclopedic instance-of), not resolver mechanics** → see Target 5.
  Fix coref/entity-binding → cashes affect (+0.43), causal (3.29×), experiencer bind, world-state. Fleet home: pri-6 (entity-gate) + the de-leak (landed).

### 4 — THE GENERATIVE WORLD-MODEL / RECURRENT PREDICTIVE-CODING LOOP (the "MAIN EVENT") — ~9 solutions (SHARED-WALL)
- **Named it as the completing lever:** `sdrt_discourse_coherence_reader…` (p7: "the ONE full-population lever is a GENERATIVE world-model"),
  `close_the_recurrent_predictive_coding_loop_n400…` (p1), `generate_dont_retrieve_causal_edges…` (N400 error against the forward model = the loop-closure),
  `build_the_generative_result_state_world_model`, `chain_multi_step…`, pri-1 `grow_the_causal_mechanism…` (rung-2/3 simulation over a bound per-item situation model = the unlock),
  `infer_unstated_emotion…` (Tier-2 abductive), `predictive_inference_forward_project…`, `the_reader_is_feed_forward_where_the_brain_is_predictive`.
- **Consumers-to-be:** `predictive_world_model`, `causal_reasoner`, `sem_event_segmenter`, `n400_coherence_monitor`, `goal_register`, `occ_appraisal`.
- **The single largest strategic lever — building it discharges ~9 solutions' residual at once.** Fleet home: pri-1.

### 5 — WORLD-KNOWLEDGE / ENCYCLOPEDIC KB — ~8 solutions
`typed_spokes` C5/C6/C7/C8 (BF_SPIRIT) · `safe_kb_gate` (BF, wrap ANY KB lookup) · DBpedia P31 / Wikidata.
- `report_the_typed_coref…` (88% headroom = world knowledge), `improve_the_common_noun_coref…` (84%),
  `world_knowledge_common_noun_to_name_bridge…` (30% doc-local coverage), `acquire_wikidata_p31…`, `expand_the_clean_semantic_memory_foundation…`,
  `the_situation_model_has_no_affect_emotion_dimension` (common-noun world-knowledge), `replace_the_attractor_as_ranker…` (relational is-a = 214× lever), pri-1 (commonsense/procedural corpus).
- **✅ C8 ASSET IS BUILT + LIVE (verified on disk 2026-09-09): `available_entity_type()` returns True; `data/frontend_assets/entity_type_spoke_v1.sqlite` (548MB) + compact `.npz` (82MB) present; Zurbaran→artist, Einstein→scientist resolve.** The "unbuilt → abstains" claim in the acquire_p31 / typed_coref SOLVEDs is STALE (rebuilt in the acquire_p31 compact-swap `47ab3aec4`). The residual is COVERAGE of a famous-but-missing slice (Denmark/Dvorak uncovered) — which the name-bridge SOLVED BOUNDED (a bigger static KB is capped at +0.0084, fitted-probe; the document-local half needs the generative route, Target 4). So this is NOT a cheap rebuild win — the world-knowledge lever is the generative world-model + broadening coverage (bounded), not the asset.

### 6 — BOARD INSTRUMENTS / "LIVE ≠ SCORED" — ~13 solutions (SHARED-WALL)
Recurring: "a board-invisible PROVEN win needs its own instrument-arm." Needing an arm: patient-slot QA on clean gold, goal_hierarchy multi-hop,
coverage-QUALITY/correct-link (pri-5), mental-causal gold, event↔goal-congruence, board_bridging, board_tom, coarse-sense, selective-reliability,
spatial SpaceEval-precision, board_namebridge/crosstype_experiencer, intrinsic-necessity/predictive-causal-necessity. **Build the missing arms → make ~13 already-live gains visible.**

### 7 — EVENT / PREDICATE DETECTION — ~7 solutions
`predicate_detector` (BF_SPIRIT) · `crf_tagger` (LATENT, default-off consumer) · `joint_relation_frontend` (BF_SPIRIT).
`register_robust_event_detection` (×2), `upgrade_the_pos_tagger…`, `extract_…whole_subgraph`, `gate_the_eventive_nominal…`,
`the_extraction_front_end_recovers_only_a_third…`, `the_event_detector_misses_copular_and_nominal…`.
**Shared unblock:** wire `crf_tagger` → `predicate_detector` behind a HIGH-PRECISION verb-recovery gate.

### 8 — PRECISION / RELIABILITY DEFER CONSUMER — ~6 solutions
`parse_confidence` (**NOT_BF**, fitted logistic, decision-dead) · `precision_weight`.
`replace_the_greedy_arc_eager…` (no live obl consumer), `build_the_obl_spatial_defer_consumer…`, `precision_weight_the_head_driven_readers…`,
`wire_a_defer_consumer…`, pri-2 (gain-based deferral, same shape), pri-5 (SDT accept). **BF fix named: swap the fitted logistic → the `graded_parser` Matrix-Tree marginal (`obl_reliability_marginal`).**

### 9 — CAUSAL / TEMPORAL KNOWLEDGE STORES + `causal_reasoner` (BF_SPIRIT, rung-2/3 do-surgery) — ~6 solutions
pri-1, `generate_dont_retrieve_causal_edges…`, `grow_a_broad_causal_event_order_store…`, `reason_over_the_causal_network…`, `causation_typing` (dormant), `reason_over_event_time_order…`.
**Shared ceiling:** generic mined knowledge does NOT instantiate on the item's specific states (granularity wall) → needs Target 4 (the world-model simulation).

### 10 — LEARNER / GROW-BY-READING / `consolidation_gate` — ~5 solutions
`build_the_controlled_knowledge_growth_consolidation_gate`, `grow_broad_coverage_rare_sense…`, pri-2 (grow the learned channel), pri-5 (more reading), pri-1 (scale ceiling).
**Shared thesis:** "more knowledge" = clean/typed/resolved, grown ONLINE by reading; the exposure gap is the dominant remaining loss once every upstream is BF.

---

## PART 3 — SHARED-WALL CLUSTERS (N solvers converged on the SAME need)
1. **"The representation, not the computation" (meaning)** — pri-2, pri-5, C7 audit, grounding-acquisition audit (G1), break_the_contextual_ceiling. **5 solvers → the point-vector/bag-of-words meaning representation.**
2. **"The generative world-model simulation is the full-population lever"** — p7 SDRT, p1 loop-closure, generate_dont_retrieve, generative_result_state, pri-1, chain_multi_step, occ_appraisal Tier-2. **~7 solvers → the MAIN EVENT.**
3. **"EXTRACTION is the shared wall"** — the parser cluster (Target 1): p2 whole-subgraph, negation-repair, patient-attachment, bare-purpose goals, agent-tie, the causal/meaning learned channels. **~6 solvers (owner-noted).**
4. **"Coref/entity-binding caps the downstream dimension"** — affect (87%), experiencer bind, world-state (coref-blind), causal (3.29×), who-has-what. **~6 solvers.**
5. **"The residual is WORLD KNOWLEDGE we don't have"** — common-noun coref (84%), name-bridge (30% doc-local), typed-coref (88%), affect experiencers. **~4 solvers; partly blocked on ONE unbuilt C8 DBpedia asset.**
6. **"Live ≠ scored — the win needs its own board arm"** — ~13 solutions (Target 6).

---

## PART 1 — PER-SOLUTION TABLE (condensed: solution | component+BF | consumes | flags)
*(Full detail in each folder's SOLVED.md; this is the maintained index — append a row per new integration.)*

**✅ INTEGRATED (2026-09-10, this session):** pri-1 grow_the_causal_mechanism [INTEGRATING] (`causal_reasoner` BF_SPIRIT rung-2/3 + NEW `causal_sign_channel` BF_SPIRIT **LIVE** as `sm.causal_sign` | sm.causal_links, formal-model couplings, directed causal store | **rung correction landed; formal-model sign LIVE 14% cov; everyday-sign tail SUBSUMED by the in-flight world-model program; abduction+directed-store-wire+Rhea = staged invasive builds**) · pri-2 point-vector [INTEGRATED] (directional ROUTE-B channel + `valence_polarity_channel` + intrinsic gain, all default-off/latent | fusion-flip gated on pri-5) · pri-6 reward-audit [INTEGRATED] (catalog | 7-organ import closure | **decision core FAITHFUL-but-DORMANT, NO live stand-in; #1 gap = MISSING tonic-DA vigor dial +579; V=M·R not cosine; dials #2-6 unbuilt — follow-on fuel, off-the-reading-path**).
**WIP frontier (assignable / in-flight):** pri-3 the_parser [PARTIAL, fleet] (graded_parser/incremental_parser route-through + acquisition; 5 NOT_BF organs) · pri-4 commonnoun_binder→typed_coref [OPEN] · pri-5 measure_end_to_end [PARTIAL] (grounded-dominant read + SDT accept; gates the pri-2 fusion-flip) · pri-7 force_dynamics_valence→Wolff [OPEN].

**Coref/entity/causal/knowledge (CONT-23→29):** de-leak (online_entity_cluster/crosstype_bridge/crosstype_live_adapter BF_SPIRIT | live parse, coref, salience_binder, typed_spokes | KB coverage) · crosstype/route_unified (crosstype_bridge BF_SPIRIT | parsed tokens, ACT-R salience, Centering | live-wire; occupation-KB=located-neg) · obl-spatial (joint_relation_frontend BF_SPIRIT, spatial_relational_model BF | exact-MAP marginals | **arc scorer surface-feature; AtLocationClassFit; powered spatial gold**) · generate_dont_retrieve (predictive_world_model BF_SPIRIT | pos_tagger, simplewiki | **N400 loop-closure=world-model; rich event key; event_type MFS→WSD**) · reader-audit (catalog | substrate.read trace | gold-coref leak, C7 read-out) · grounding-audit (catalog | reading_grounding_loop trace | **G1 read-out loses to counting; G2 grounded_similarity inert**) · C7 attractor (iterative_attractor/cleanup_family BF | canonicalize_fast, conceptual_meaning | **fusion-wire gated on coverage; point-vector rep=deep lever**) · name-bridge (safe_kb_gate BF + who_is_who_lexicon BF_SPIRIT [grown-knowledge INCORPORATED 2026-09-10, → `KNOWLEDGE_ASSET_REGISTER.md`] | DBpedia, typed_spokes, recency, who-is-who relational lexicon | **doc-local COVERAGE; generative route WORLD-MODEL-GATED; token-overlap clustering + ungated-KB + coarse-typing = NOT_BF**) · acquire_p31 (typed_spokes C8 BF_SPIRIT | DBpedia InstanceOf, C5 closure | live-wire; **C8 asset unbuilt**).

**Parser/predictive/knowledge (CONT-17→22):** graded_parser (Matrix-Tree; arc_parser NOT_BF | arc-factored scorer | **scorer FEATURES are the wall; no live obl consumer**) · loop-closure p1 (sem_event_segmenter BF_SPIRIT island | forward error, FHRR scene | **SEM organ NO live consumer; multi-dim forward projector**) · structured_matcher p4 (BF_SPIRIT | WordNet, FrameNet, affect_lexicon | episodic-simulation organ; board arm) · typed_spokes p11 (BF_SPIRIT | WordNet is-a/part-whole | **P31 instance-of KB; part-whole no transitive closure**) · typed_coref promote/report (BF_SPIRIT beats commonnoun_binder NOT_BF | live schema, typed_spokes | **~88% headroom=world knowledge; C8 unbuilt**) · improve_common_noun_coref (event_centrality_coref BF_SPIRIT | typed card, Nref bridge | 84% world-knowledge→P31) · grow_broad_causal_order (temporal_reasoner/temporal_script_schema BF_SPIRIT | 454k verb-pairs | **ceiling=context-free SCRIPT PRIOR; needs reading the implicit context**).

**Reasoning-phase dimensions (CONT-13→20):** whole-subgraph p2 (joint_relation_frontend BF_SPIRIT | one parse/sent, WN | **tense-gate was the wall; NOT_BF parser residual**) · negation p9 (polarity_operator BF_SPIRIT | state_register, factive lexicon | **parser-repair net-neg → VerbNet subcat + tagger-confidence gating**) · unified_referent p12 (event_centrality_coref BF_SPIRIT | phi-filter, gender | **gender-UNKNOWN inference; 67% same-gender→world-knowledge**) · occ_appraisal p3 (BF_SPIRIT | affect+goal+event registers | **common-noun coref; meaning-channel Tier-2**) · spatial p6 (spatial_relational_model BF | sm.locations | extraction-capped→p2) · temporal p5 (temporal_reasoner BF_SPIRIT | sm.events, TB-Dense | **live TIMEX/DCT + duration extractors; copular channel**) · affect (affect_register BF_SPIRIT | coref-experiencer, psych frames | **common-noun coref=87% of loss**) · goal (goal_register BF_SPIRIT | purpose constructions, coref | register-native parse; meaning Tier-2) · copular (copular_binding/state_register BF_SPIRIT | UD-EWT, robust_cop | **cross-sentence canonical-entity binding**).

**Foundational (Chunk A/B/C/D):** parser-attachment (predicate_argument_frontend BF_SPIRIT; arc_parser NOT_BF | arc heads, valency | **+0.15-to-ceiling=parser; patient QA on clean gold**) · role-assigner swap (graded_role_assigner BF_SPIRIT gold-fitted validities | net_activation, coref | register-general parser; thetic/unaccusative detector) · pos_tagger/crf (crf_tagger LATENT | 19c transfer, P(VERB) | high-precision verb-gate; **consumer default-off**) · predicate_detector (BF_SPIRIT | register cues | joint calibrated POS+parse) · bridging_inference (BF_SPIRIT, 1st meaning consumer | ATL PPMI+SVD, meaning_foundation | **no meaning board dim**) · theory_of_mind (BF_SPIRIT | belief_timeline, goal_register | **no board arm; desired-VALUE via meaning channel**) · meaning_foundation (BF_SPIRIT LATENT | 117k sense-signatures | **no read()-time consumer; 15k→80k store**).

---

## THE TWO CONCRETE CROSS-SOLUTION UNBLOCKS (highest ROI on this map)
1. **BUILD THE GENERATIVE WORLD-MODEL SIMULATION (Target 4)** — discharges ~9 solutions' residual including the pri-1 causal frontier. The largest single lever. (In flight: pri-1.)
2. ~~REBUILD THE C8 DBpedia ASSET~~ — **RETRACTED after disk-verify (2026-09-09): the C8 asset is already BUILT + LIVE** (`available_entity_type()`=True). The SOLVED-file "unbuilt" claims were stale. The real world-knowledge lever is Target 4 (the generative world-model for document-local coverage) + bounded static-KB coverage expansion — NOT an asset rebuild. (This is the disk-verify caveat in action.)
