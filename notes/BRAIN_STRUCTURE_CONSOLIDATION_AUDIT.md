# Brain-Structure Consolidation Audit

**Date:** 2026-09-10 · **Author:** consolidation-audit pass (read-only; no `hdlab/` or `experiments/` file modified) · **Inventory:** `notes/bf_status_registry.jsonl` (83 organs) + `notes/ORGAN_MAP.md` (structure attributions) + per-organ registry notes.

## 0. Why this exists (the owner's concern, 2026-09-10)

> "we're creating organs left and right; in aggregate this may NOT be brain-foundational — one organ does one thing while another does a different thing, when in reality they're the SAME brain structure with different arms."

Per-organ certification asks "does THIS organ compute the brain's equation?" It has **never** asked "do our organ BOUNDARIES match the brain's STRUCTURE boundaries?" This audit assigns every registered organ to the brain structure it implements, groups by structure, and gives each multi-organ cluster a research-backed verdict: **KEEP (faithful sub-modularity)** / **CONSOLIDATE (artificial fragmentation)** / **INVERSE (under-fragmentation)**.

**Counter-caution honored throughout (pri-3 `the_parser_is_a_frozen_supervised_hard_decode`):** different LOSSES genuinely need different task-specific mechanisms (attachment ≠ coref). The bar to recommend CONSOLIDATE is that the *neuroscience says it is ONE structure computing ONE operation* — not merely that two organs are topically adjacent.

---

## (a) Full organ → brain-structure table

Structure codes used in the table:
`ATL-HUB` amodal semantic hub · `KB-STORE` typed semantic knowledge store · `SPOKE` sensorimotor grounding spoke · `AXES` Osgood evaluative/quality axes · `PARSE` incremental syntactic parser · `PARSE-SUP` frozen supervised parse stack (interim, NOT_BF) · `ROLES` thematic-role assignment (Competition Model) · `SRL` predicate/argument frontend · `COREF` coreference / entity resolution (cue-based retrieval) · `SALIENCE` discourse salience (Centering + ACT-R) · `DRT-REF` DRT referent construction · `CA3` hippocampal completion/cleanup · `RECOG` recognition memory / person identity · `PRED` predictive coding / forward world model · `TIME` temporal cognition (Reichenbach/Allen/Vendler) · `SITMODEL` situation model (Zwaan-Radvansky event-indexing) · `TOM` theory of mind (rTPJ/mPFC) · `APPRAISAL` affective appraisal (OCC / biased competition) · `FORCE` force dynamics (Talmy/Wolff) · `CAUSAL` causal reasoning (Pearl ladder) · `GOAL` goal/planning register (PFC) · `WM` theta-gamma working-memory buffer · `BIND` VSA/conjunctive binding · `SEG` event segmentation · `LOGIC` truth-conditional operators · `CUE` PPC reliability-weighted cue integration · `LEARN` acquisition/learning.

| # | organ | status | brain structure(s) | 1-line role |
|---|---|---|---|---|
| 1 | event_bundle | BF | BIND | FHRR bind/bundle/unbind/cleanup primitive — the binding algebra |
| 2 | role_slot_summarizer | BF | BIND | same primitives, sharded per-role slots (role-filler assembly) |
| 3 | incremental_parser | BF_SPIRIT | PARSE | left-corner Now-or-Never eager attach (the BF parser) |
| 4 | predictive_reader | BF_SPIRIT | PRED | −logP surprisal + Friston precision (N400 error stage) |
| 5 | graded_role_assigner | BF_SPIRIT | ROLES | MacWhinney Competition-Model cue-validity role assignment |
| 6 | grounded_similarity | BF_SPIRIT | SPOKE | Lancaster/Brysbaert 12-d sensorimotor table + cosine |
| 7 | sensorimotor_spoke | BF_SPIRIT | SPOKE | euclid-in-z wrapper that CALLS grounded_similarity's table |
| 8 | context_grounded_valence | BF_SPIRIT | APPRAISAL (+semantic-control gain) | biased-competition + appraisal read |
| 9 | force_dynamics_lexicon | BF_SPIRIT | FORCE | Wolff/Talmy truth-table (physical, ~16% cov) |
| 10 | predictive_world_model | BF_SPIRIT | PRED (+CAUSAL rung-1) | forward transition model + leave-one-out relevance |
| 11 | pos_tagger | NOT_BF | PARSE-SUP | frozen avg-perceptron POS (hard Viterbi) |
| 12 | arc_parser | NOT_BF | PARSE-SUP | arc-factored perceptron dependency (route AROUND) |
| 13 | force_dynamics_valence | NOT_BF | FORCE (+APPRAISAL) | harm/help WordNet-animacy+verb-list (retired) |
| 14 | causal_reasoner | BF_SPIRIT | CAUSAL | do()-surgery counterfactual on extracted causal graph (rung-3) |
| 15 | quality_relation | BF_SPIRIT | AXES (ATL-HUB) | signed Osgood opposition axis (antonymy) |
| 16 | online_entity_cluster | BF_SPIRIT | COREF (+SALIENCE) | Heim file-change + Lewis-Vasishth ACT-R retrieval |
| 17 | crosstype_bridge | BF_SPIRIT | COREF | precise-constructs predication + ACT-R cue retrieval |
| 18 | crosstype_live_adapter | BF_SPIRIT | COREF (adapter) | builds crosstype Doc from live parse; pure plumbing |
| 19 | iterative_attractor | BF | CA3 | graded soft-attractor for recall/completion (Treves-Rolls) |
| 20 | cleanup_family | BF | CA3 | cleanup primitive library (k-NN lookup) |
| 21 | conceptual_meaning | BF_SPIRIT | ATL-HUB | IDF-weighted taxonomic distinctive-feature cosine |
| 22 | meaning_foundation | BF_SPIRIT | ATL-HUB | curated w2v sense signatures (distributional relatedness) |
| 23 | arceager_parser | NOT_BF | PARSE-SUP | arc-eager perceptron (route AROUND, dead version) |
| 24 | reading_grounding_loop | BF_SPIRIT | ATL-HUB + LEARN (+CA3 consolidation) | grow-by-reading engine + graded-cosine readout |
| 25 | safe_kb_gate | BF | RECOG (+KB-STORE) | Bruce-Young/IAC familiarity + Yonelinas SDT gate |
| 26 | spatial_relational_model | BF | SITMODEL (space) | Franklin-Tversky Source-Path-Goal spatial construction |
| 27 | salience_binder | BF | SALIENCE | ACT-R base-level (Anderson-Schooler) + Centering Cf |
| 28 | temporal_reasoner | BF_SPIRIT | TIME | Reichenbach E/R/S + Allen interval algebra |
| 29 | event_centrality_coref | BF_SPIRIT | SALIENCE (+COREF) | graded ACT-R base-level entity centrality |
| 30 | referent_per_np | BF_SPIRIT | DRT-REF | Kamp/Heim DRT one-referent-per-NP construction |
| 31 | predicate_detector | BF_SPIRIT | SRL | noisy-channel logistic predicate detection |
| 32 | relcl_resolver | BF_SPIRIT | PARSE | deterministic filler-gap relative-clause resolution |
| 33 | np_head_reduce | BF_SPIRIT | PARSE | deterministic NP-head reduction |
| 34 | bridging_inference | BF_SPIRIT | ATL-HUB (+COREF bridging) | cosine over hub + WordNet part-whole for unstated bridges |
| 35 | structural_do | BF_SPIRIT | SRL/ROLES | structural direct-object cue + abstain |
| 36 | structured_matcher | BF_SPIRIT | ATL-HUB | relation-sign read + abstain-to-hub (converse/antonym) |
| 37 | situation_focus | BF_SPIRIT | WM | theta-gamma bounded WM buffer (capacity gap flagged) |
| 38 | typed_coref | BF_SPIRIT | COREF | Ariel accessibility + DRT type-cards + Nref type bridge |
| 39 | affect_lexicon | BF_SPIRIT | APPRAISAL (supply) | static affect-norm supply feeding appraisal |
| 40 | psych_verb_frames | BF_SPIRIT | ROLES/APPRAISAL (supply) | psych-verb experiencer/stimulus frame supply |
| 41 | goal_register | BF_SPIRIT | GOAL (supply) | goal/subgoal register (verb-class supply + graph) |
| 42 | occ_appraisal | BF_SPIRIT | APPRAISAL | OCC event-goal-congruence appraisal |
| 43 | event_type | BF_SPIRIT | KB-STORE (supply) | event-TYPE supply (MFS/WordNet) |
| 44 | verb_subcat_frames | BF_SPIRIT | PARSE/SRL (supply) | verb subcategorization-frame supply gating attachment |
| 45 | typed_spokes | BF_SPIRIT | KB-STORE | ATL hub-and-typed-spoke store (is-a/part-whole/antonym) |
| 46 | parse_confidence | NOT_BF | PARSE-SUP (precision) | fitted logistic parse-arc confidence (decision-dead) |
| 47 | aspect_interval | BF_SPIRIT | TIME | Vendler/Smith viewpoint aspect → Allen interval |
| 48 | temporal_ordering | BF_SPIRIT | TIME | tense/aspect+connective → chronological constraint order |
| 49 | temporal_ordering_multiframe | BF_SPIRIT | TIME | cross-sentence timeline (EXTENDS temporal_ordering) |
| 50 | temporal_order_register | BF_SPIRIT | TIME | queryable before/after (COMPOSES the ordering front-end) |
| 51 | arc_labeler | NOT_BF | PARSE-SUP | multiclass perceptron dep-relation labeler |
| 52 | thematic_role_labeler | BF_SPIRIT | ROLES | MacWhinney Competition-Model cue-integration (SAME as #5) |
| 53 | predicate_argument_frontend | BF_SPIRIT | SRL (+ROLES) | shallow event-semantic SRL (agent/theme/goal/...) |
| 54 | coref | BF_SPIRIT | COREF (+RECOG name-individuation) | Kintsch/van-Dijk backbone + EntityAliaser |
| 55 | causal_network | BF_SPIRIT | CAUSAL (+SITMODEL causation) | Trabasso/van-den-Broek causal-network discourse model |
| 56 | copular_binding | BF_SPIRIT | ATL-HUB | Higgins/Bemis-Pylkkänen LATL property attribution |
| 57 | belief_reader | BF_SPIRIT | TOM (driver) | glass-box driver for belief_timeline; no own decision |
| 58 | theory_of_mind | BF_SPIRIT | TOM | forward mentalizing believes×wants→action (rTPJ/mPFC) |
| 59 | world_state_register | BF_SPIRIT | SITMODEL (causation) | Zwaan-Radvansky mutable world-state via effects/preconds |
| 60 | possession_operators | BF_SPIRIT | SITMODEL (supply) | FrameNet TRANSFER operator supply |
| 61 | state_register | BF_SPIRIT | SITMODEL (entity state) | Zwaan-Radvansky entity state-history intervals |
| 62 | affect_register | BF_SPIRIT | SITMODEL (affect) (+APPRAISAL) | per-character affect dimension bound to experiencer |
| 63 | goal_hierarchy_graph | BF_SPIRIT | GOAL | goal→subgoal hierarchy graph over goal_register |
| 64 | frame_induction | BF_SPIRIT | LEARN | Gleitman syntactic bootstrapping (EXPANDS hdlab.learner) |
| 65 | location_register | BF_SPIRIT | SITMODEL (space) | Zwaan-Radvansky presence intervals per entity |
| 66 | joint_relation_frontend | BF_SPIRIT | SRL/PARSE | parse-once read-all-channels joint extraction |
| 67 | bound_event_backbone | BF_SPIRIT | BIND | tiered bound-event-token backbone (FHRR via event_bundle) |
| 68 | generalized_event_knowledge | BF_SPIRIT | PRED (+ATL-HUB event knowledge) | forward GEK associative co-activation readout |
| 69 | underspecified_sense_reader | BF_SPIRIT | ATL-HUB | context-primed biased-competition sense commit (WSD) |
| 70 | tense_preserving_detector | BF_SPIRIT | TIME | compositional Reichenbach tense reader (per VERB) |
| 71 | perceptual_access_ledger | BF_SPIRIT | TOM | did-agent-perceive-event observation-cue front-end |
| 72 | belief_timeline | BF_SPIRIT | TOM | per-agent belief timeline (rTPJ/mPFC register) |
| 73 | world_state_entity_binding | BF_SPIRIT | COREF binding (+SITMODEL) | Glenberg two-stage raw-mention → canonical entity key |
| 74 | causation_typing | BF_SPIRIT | FORCE (+CAUSAL) | Wolff/Talmy CAUSE/ENABLE/PREVENT within-clause typing |
| 75 | coherence_reader | BF_SPIRIT | SITMODEL/discourse coherence | SDRT-lite directed causal-plausibility coherence |
| 76 | commonnoun_binder | NOT_BF | COREF | head-lemma string-match binding (below string-identity floor) |
| 77 | entity_world_model_resolver | BF_SPIRIT | COREF (+KB-STORE) | curated role/kinship KB prior for entity resolution |
| 78 | polarity_operator | BF_SPIRIT | LOGIC | truth-conditional polarity + quantity operator |
| 79 | scene_segment | NOT_BF | SEG | fixed-window segmentation (superseded by sem_event_segmenter) |
| 80 | who_is_who_lexicon | BF_SPIRIT | RECOG/KB-STORE (supply) | grown possessed-type + title-role relational lexicon |
| 81 | valence_polarity_channel | BF_SPIRIT | AXES (+APPRAISAL) | signed Osgood evaluative valence axis |
| 82 | convergent_cue_reader | BF_SPIRIT | CUE | Ma/Pouget PPC reliability-weighted cue product |
| 83 | causal_sign_channel | BF_SPIRIT | CAUSAL | Forbus QP direct-influence edge sign |

**Tally: 83 organs → ~25 distinct brain structures** (26 if the frozen supervised parse stack is counted apart from the incremental parser it is being replaced by). Of the 83, **6 are pure static SUPPLY assets** (affect_lexicon, psych_verb_frames, event_type, verb_subcat_frames, possession_operators, who_is_who_lexicon) — these are admissible foundation feeding a parent structure, not brain structures in their own right, so they should never be counted as independent organs when judging aggregate modularity.

---

## (b) Multi-organ clusters, ranked by size, with verdicts

### Cluster 1 — COREF: coreference / entity resolution — **8 organs → CONSOLIDATE (artificial fragmentation)**
Organs: online_entity_cluster(16), crosstype_bridge(17), crosstype_live_adapter(18), typed_coref(38), coref(54), commonnoun_binder(76), entity_world_model_resolver(77), world_state_entity_binding(73). Adjacent-but-DISTINCT (see below): salience_binder(27), event_centrality_coref(29), referent_per_np(30).

**Verdict: CONSOLIDATE the six resolvers into ONE cue-based entity resolver.** The brain performs antecedent/reference resolution with a SINGLE content-addressable, cue-based retrieval mechanism (Lewis & Vasishth 2005 ACT-R cue-based retrieval; Parker, Shvartsman & Van Dyke — "basic binding operations in sentence comprehension are mediated by a content-addressable memory system"; the theory is explicitly *uni-modular*: all cues available at the anaphor are used immediately and in parallel to cue ONE retrieval). Our six organs each run a *variant of the same retrieval* differing only in the CUE set: type cue (typed_coref), cross-type name bridge (crosstype_bridge), head-lemma string (commonnoun_binder, NOT_BF), KB role/kinship prior (entity_world_model_resolver), file-change + exact-head (online_entity_cluster). That is one structure with different cue-arms, split for engineering convenience.

**Merge target:** one `entity_resolver` with a single ACT-R content-addressable retrieval core and pluggable **cue-arms** (type, name-bridge, KB-prior, morphosyntactic). commonnoun_binder (NOT_BF, measured below string-identity) drops out — it is already slated for replacement by the typed_coref content-addressed binding. crosstype_live_adapter is pure plumbing → folds in. world_state_entity_binding (Glenberg two-stage raw→canonical) is the *output-normalisation* arm of the same resolver, not a situation-model organ.

**KEEP separate (faithful):** salience_binder + event_centrality_coref compute *salience* (Centering local attentional state + ACT-R base-level), and referent_per_np constructs *referents* (DRT). Research shows Centering (local salience) and DRT (global referent construction) are **complementary, distinct processes**, not the retrieval step — so these are correctly separate FROM the resolver (but see Cluster 6 for salience-internal consolidation).

### Cluster 2 — TIME: temporal cognition — **6 organs → CONSOLIDATE (mostly), one KEEP split**
Organs: temporal_reasoner(28), aspect_interval(47), temporal_ordering(48), temporal_ordering_multiframe(49), temporal_order_register(50), tense_preserving_detector(70).

**Verdict: CONSOLIDATE the ordering layer; KEEP the tense/aspect transducers as arms.** Reichenbach reference-time + Allen interval algebra + Vendler aspect is ONE computational framework, and temporal order in comprehension is a single situation-model dimension (Zwaan time index). The registry notes are explicit that temporal_ordering_multiframe **"is an extension of temporal_ordering"** and temporal_order_register **"composes the pinned discrete front-end"** — i.e. these three are layers/versions of one order-construction organ, not three distinct computations.

**Merge target:** one `temporal_model` organ = `[tense-read arm | aspect-read arm | order-build+query core]`. tense_preserving_detector (Reichenbach tense per verb) and aspect_interval (Vendler viewpoint) are genuinely different *transducers* (tense ≠ aspect linguistically) feeding the same interval model — keep them as input arms, not standalone organs. temporal_ordering + temporal_ordering_multiframe + temporal_order_register → one order-core. 6 → effectively 3 arms of one organ. Low-risk (all BF_SPIRIT, one framework).

### Cluster 3 — SITMODEL: situation model (Zwaan-Radvansky event-indexing) — **8 organs → KEEP (faithful sub-modularity), tidy supply/binding**
Organs: world_state_register(59), state_register(61), affect_register(62), location_register(65), spatial_relational_model(26), possession_operators(60, supply), world_state_entity_binding(73), coherence_reader(75).

**Verdict: KEEP the per-dimension registers — this is faithful.** The Event-Indexing Model (Zwaan, Langston & Graesser 1995; Zwaan, Radvansky, Hilliard & Curiel) posits FIVE situational dimensions — time, space, causation, intentionality, protagonist — that readers monitor **separately and largely independently**: discontinuity on each dimension produces its *own* reading-time cost, and the dimensions dissociate (spatial monitoring only appears after a memorised map; temporal/causal/goal/protagonist each show independent costs). So dimension-specific registers (location_register = space, state_register = entity state, affect_register = affect, world_state_register = causation via effects/preconditions) are a faithful replica of a genuinely multi-dimensional structure — do NOT merge them into one blob.

**Tidy, not merge:** possession_operators is a supply lexicon → fold into world_state_register as its transfer-operator table. world_state_entity_binding is really the COREF resolver's output arm (Cluster 1), not a situation-model organ. spatial_relational_model (Franklin-Tversky construction) vs location_register (presence intervals) both touch SPACE — verify they are construction-vs-tracking (distinct) and not two encoders of the same space index (see honest bounds). coherence_reader (SDRT) is discourse-coherence, adjacent but a distinct computation (KEEP).

### Cluster 4 — ATL-HUB: amodal semantic hub representation + readout — **7 core organs → SPLIT VERDICT (CONSOLIDATE the representation, KEEP the reads)**
Organs: conceptual_meaning(21), meaning_foundation(22), reading_grounding_loop(24), structured_matcher(36), copular_binding(56), underspecified_sense_reader(69), bridging_inference(34). Meaning-axis channels quality_relation(15) + valence_polarity_channel(81) attach here.

**Verdict (representation): CONSOLIDATE into one fused meaning representation.** conceptual_meaning (distinctive-feature taxonomic), meaning_foundation (distributional relatedness), and the Osgood axes (quality_relation antonymy, valence_polarity_channel valence) are *different channels of the SAME concept representation* — the ATL hub is one amodal structure. This is precisely the pri-2/pri-5 meaning-fusion program already active: fuse identity/relatedness/valence channels, never pool. The consolidation move is a single `meaning_representation` organ exposing the channels as arms (which the convergent_cue_reader reliability-weights). This aligns with, and would formalise, the current north-star.

**Verdict (reads): KEEP — these are different operations (pri-3 respected).** underspecified_sense_reader (biased-competition WSD), copular_binding (LATL property attribution / predication), bridging_inference (part-whole + hub cosine for unstated bridges), structured_matcher (relation-sign typing) apply *distinct computations* over the shared representation. Semantic control applies multiplicative gain to reshape the SAME hub for different tasks (Chiou & Lambon Ralph 2018) — i.e. one representation, many task-conditioned reads. Keep the reads; unify only the representation they read.

### Cluster 5 — PARSE-SUP: frozen supervised parse stack — **5 organs → PRUNE VERSIONS, not a brain-structure fragmentation**
Organs: pos_tagger(11), arc_parser(12), arceager_parser(23), arc_labeler(51), parse_confidence(46). All NOT_BF.

**Verdict: not a fidelity CONSOLIDATE — a version-pruning problem.** These are interim supervised assets (POS is brain-unpinned; the perceptrons are frozen hard-decode). arc_parser and arceager_parser are **redundant versions** — both carry "route AROUND via incremental_parser." The brain-foundational move is to route the live path through incremental_parser (Cluster A parser) + graded parser marginals and PRUNE the dead perceptron versions (3-gate at-land pruning). This is consistent with pri-3: the supervised hard-decode is the wrong mechanism; the fix is to *replace*, not to merge the interim assets. Counted as one interim structure being retired, not five faithful organs.

### Cluster 6 — TOM: theory of mind — **4 organs → CONSOLIDATE the driver, KEEP the pipeline**
Organs: theory_of_mind(58), belief_reader(57), belief_timeline(72), perceptual_access_ledger(71).

**Verdict: fold belief_reader into belief_timeline; KEEP the rest.** The ToM network dissociates: rTPJ selectively represents others' beliefs/intentions/desires, while mPFC carries affective/motivational components (Saxe & Kanwisher 2003; Saxe & Powell; Koster-Hale et al.). Our four organs are NOT split along rTPJ/mPFC — they are a *pipeline*: perceptual_access_ledger (did A perceive E) → belief_timeline (what A believes at t) → theory_of_mind (believes×wants→action). belief_reader is explicitly **pure plumbing** ("no decision of its own beyond wiring") → CONSOLIDATE into belief_timeline. perceptual-access, belief-tracking, and intention-composition are genuinely different computations → KEEP. 4 → 3.

### Cluster 7 — APPRAISAL: affective appraisal — **4-6 organs → CONSOLIDATE the two appraisers**
Organs: occ_appraisal(42), context_grounded_valence(8), affect_register(62, situation-model arm), affect_lexicon(39, supply), psych_verb_frames(40, supply), force_dynamics_valence(13, NOT_BF).

**Verdict: CONSOLIDATE the appraisal computation.** occ_appraisal (OCC event-goal congruence) and context_grounded_valence (biased-competition + appraisal on the unpinned valence tier) are TWO appraisal reads over the same OFC/amygdala appraisal system. Merge into one `appraisal` organ with an OCC arm + a core-affect/biased-competition arm, fed by affect_lexicon (supply). affect_register is the *situation-model binding* of affect to a character (distinct = binding; keep in SITMODEL). force_dynamics_valence is NOT_BF harm/help (retired) — drop.

### Cluster 8 — CAUSAL: causal reasoning (Pearl ladder) — **4-5 organs → KEEP (faithful — the counter-caution case)**
Organs: causal_network(55), causal_reasoner(14), predictive_world_model(10, rung-1), causal_sign_channel(83), causation_typing(74, shared with FORCE).

**Verdict: KEEP — do NOT consolidate.** This is the textbook pri-3 case: the organs occupy *different rungs of Pearl's causal ladder*, which are genuinely different computations. The registry explicitly separates rung-1 leave-one-out predictive relevance (predictive_world_model) from rung-3 counterfactual do()-surgery (causal_reasoner); causal_network *constructs* the graph they operate on (Trabasso/van-den-Broek); causal_sign_channel adds an edge attribute (Forbus QP sign). Merging these would collapse association / intervention / counterfactual into one operator — the opposite of brain-foundational. Only minor tidy: causal_sign_channel writes edge signs into the same graph causal_network builds, so it could be a sign-arm of causal_network (optional, low value).

### Cluster 9 — FORCE: force dynamics — **3 organs → CONSOLIDATE**
Organs: force_dynamics_lexicon(9), causation_typing(74), force_dynamics_valence(13, NOT_BF).

**Verdict: CONSOLIDATE.** All three apply the Wolff/Talmy force-dynamic truth-table. force_dynamics_lexicon (physical CAUSE/ENABLE) + causation_typing (CAUSE/ENABLE/PREVENT within-clause) are the same operation over different inputs → one `force_dynamics` organ with a physical arm and a linguistic-causative arm. force_dynamics_valence (harm/help via WordNet-animacy + verb list, NOT_BF, retired) is a broken duplicate → drop.

### Cluster 10 — PRED: predictive coding / forward world model — **3 organs → KEEP as stages, CLOSE the loop**
Organs: predictive_reader(4), predictive_world_model(10), generalized_event_knowledge(68).

**Verdict: KEEP (faithful stages), but wire into one loop.** Rao-Ballard predictive coding has genuinely distinct stages: forward prediction (generalized_event_knowledge = GEK associative co-activation; predictive_world_model = event-transition), and precision-weighted error (predictive_reader = −logP surprisal + Friston precision, the N400 signal). These are different computations of one hierarchy, not duplicates — KEEP. The BF move (already the active program, per MEMORY: "forward event-transition model → close N400 forward loop") is to WIRE them into one recurrent predictive loop, not to merge them into one flat organ.

### Cluster 11 — BIND: VSA/conjunctive binding — **3 organs → KEEP (library + consumers)**
Organs: event_bundle(1), role_slot_summarizer(2), bound_event_backbone(67).

**Verdict: KEEP.** event_bundle is the *primitive library* (the binding algebra); role_slot_summarizer and bound_event_backbone are *consumers* that assemble role-filler / event-token structures using it. Library-vs-application is legitimate factoring, not fragmentation. Minor overlap (both consumers assemble role-filler bindings) — acceptable.

### Cluster 12 — SPOKE: sensorimotor grounding — **2 organs → CONSOLIDATE**
Organs: grounded_similarity(6), sensorimotor_spoke(7).

**Verdict: CONSOLIDATE.** sensorimotor_spoke is a thin euclid-in-z wrapper that *already calls grounded_similarity's table* rather than re-loading it. One `sensorimotor_spoke` organ owning the 12-d norm table + the metric (euclid/cosine SWEPT). Clean, low-risk.

### Cluster 13 — SALIENCE: discourse salience — **2 organs → CONSOLIDATE**
Organs: salience_binder(27), event_centrality_coref(29).

**Verdict: CONSOLIDATE.** Both compute Anderson-Schooler ACT-R base-level activation for entity salience; the registry even calls salience_binder "the pinned salience math the coref line reuses." event_centrality_coref is a second base-level activation site → make it an arm (centrality) of one `salience` organ. (online_entity_cluster also calls ACT-R retrieval — its salience use should route to this one organ, not re-implement.)

### Cluster 14 — CA3: hippocampal completion / cleanup — **2 organs → KEEP (library + application)**
Organs: iterative_attractor(19), cleanup_family(20). cleanup_family is the primitive library; iterative_attractor is the graded soft-attractor application. Both BF. Legitimate factoring — KEEP.

### Cluster 15 — GOAL: goal / planning register — **2 organs → mild CONSOLIDATE**
Organs: goal_register(41), goal_hierarchy_graph(63). goal_hierarchy_graph builds over goal_register's supply — could be arms of one `goal` organ. Low priority (goal_register is mostly supply).

### Cluster 16 — AXES: Osgood evaluative axes — **2 organs → CONSOLIDATE (into the hub representation)**
Organs: quality_relation(15), valence_polarity_channel(81). Both are axes of the Osgood semantic-differential frame (evaluation / potency-opposition). Fold as channel-arms of the fused meaning representation (Cluster 4).

### Cluster 17 — ROLES: thematic-role assignment — **2 core organs → CONSOLIDATE**
Organs: graded_role_assigner(5), thematic_role_labeler(52) (+ SRL frontend, structural_do, psych_verb_frames supply).

**Verdict: CONSOLIDATE the two Competition-Model organs.** Both implement the identical MacWhinney Competition-Model cue-validity integration — the registry note on thematic_role_labeler literally reads "same fitted-validity caveat as graded_role_assigner." Two organs, one equation → one `thematic_roles` organ. Keep SRL frontend (predicate_argument_frontend) and structural_do as distinct — SRL is the event-semantic mapping layer, a different loss (argument→role vs frame extraction).

**Single-organ structures (no cluster):** WM (situation_focus), DRT-REF (referent_per_np), LOGIC (polarity_operator), CUE (convergent_cue_reader), SEG (scene_segment, NOT_BF), LEARN (frame_induction + reading_grounding_loop's learning arm), RECOG (safe_kb_gate + who_is_who supply). No consolidation needed; listed for completeness.

---

## (c) Ranked action list — top consolidation opportunities

Ordered by aggregate brain-foundationality gain (cluster size × strength of the "one structure" evidence × how many live organs it de-duplicates).

**1. Coreference/entity resolution → one cue-based `entity_resolver` (6 organs → 1 + cue-arms).**
Organs: online_entity_cluster, crosstype_bridge, crosstype_live_adapter, typed_coref, coref, commonnoun_binder (drop; NOT_BF) + fold world_state_entity_binding's binding arm.
Basis: Lewis & Vasishth 2005 cue-based retrieval is a single *uni-modular content-addressable* mechanism; our six are one retrieval with different cues. Biggest cluster, strongest evidence, most live de-duplication. Keep salience + DRT referent-construction separate.

**2. Fused `meaning_representation` (conceptual_meaning + meaning_foundation + quality_relation + valence_polarity_channel → one channel-fused hub representation).**
Basis: the ATL hub is ONE amodal structure; distinctive-feature + distributional + Osgood axes are channels of the same concept vector (fuse-not-pool). Formalises the already-active pri-2/pri-5 meaning-fusion north-star. KEEP the distinct task-reads (WSD, predication, bridging).

**3. Temporal ordering trio → one `temporal_model` (temporal_ordering + temporal_ordering_multiframe + temporal_order_register → one order-core; tense/aspect readers become input arms).**
Basis: one Reichenbach/Allen/Vendler framework; the registry says multiframe *extends* ordering and order_register *composes* the front-end — layering/versioning, not distinct computation. Low-risk, all BF_SPIRIT.

**4. Thematic roles → one `thematic_roles` organ (graded_role_assigner + thematic_role_labeler).**
Basis: identical MacWhinney Competition-Model equation; registry flags them as sharing the same fitted-validity caveat. Cleanest merge on the board — two organs, one operation.

**5. Force dynamics → one `force_dynamics` organ (force_dynamics_lexicon + causation_typing; drop NOT_BF force_dynamics_valence).**
Basis: one Wolff/Talmy force-dynamic truth-table applied to physical vs linguistic-causative inputs.

Runners-up (small, clean, do opportunistically): sensorimotor_spoke↔grounded_similarity (wrapper); salience_binder↔event_centrality_coref (same ACT-R base-level); belief_reader→belief_timeline (plumbing); occ_appraisal↔context_grounded_valence (two appraisers). **Version-prune (separate track):** arc_parser + arceager_parser are dead perceptron versions superseded by incremental_parser — prune, don't merge.

---

## (d) Honest bounds — where I was unsure, and what a deeper pass needs

- **Structure assignment is from registry notes + established frameworks, not a full source read of all 83 files.** Assignments I am least sure of and that a deeper pass should confirm at code level: joint_relation_frontend (SRL vs PARSE — is it a *parser pass* or a *role reader*?), structural_do (ROLES vs SRL), bound_event_backbone vs role_slot_summarizer (do they duplicate role-filler assembly or is one strictly event-token, one strictly per-role?), and bridging_inference (ATL-HUB read vs a COREF bridging step — it touches both).
- **SITMODEL space dimension (spatial_relational_model vs location_register):** I rated the situation-model registers KEEP on strong Zwaan-Radvansky grounds, but I did NOT verify whether these two organs are construction-vs-tracking (distinct, keep) or two encoders of the same space index (a hidden fragmentation). Needs a code read of both.
- **PRED loop vs stages — ✅ RESOLVED (strategy code-check 2026-09-10, CONT-140): KEEP confirmed, no flip.** `generalized_event_knowledge` = the forward PREDICTION/expectation readout (`expected()`/`project_expected()`, associative co-activation, "the forward half"); `predictive_world_model` = the SURPRISAL/error + leave-one-out RELEVANCE read (N400/rung-1). Prediction vs prediction-ERROR are DISTINCT Rao-Ballard roles → genuinely distinct stages, not a duplication (neither imports the other). ONE refinement: PWM builds its OWN single-layer forward model → the two forward models should be UNIFIED (PWM's surprisal computed against GEK's prediction) = the already-named "close the recurrent predictive-coding loop" program, not a consolidation.
- **Supply assets counted carefully:** 6 organs are static supply lexicons, not structures. If aggregate-modularity is re-scored, exclude them from the organ count or the fragmentation ratio will look worse than it is.
- **"One structure" bar respected, but the neuroscience for a few is coarse:** TIME and APPRAISAL do not map to a single well-delimited cortical region the way ATL-HUB or rTPJ do; I leaned on the *computational-level* framework being unified (Reichenbach/Allen; OCC). A stricter neuroanatomical reading could keep more of these split.
- **Not audited for INVERSE exhaustively.** Named INVERSE risks below are the clear ones; a dedicated inverse pass (one organ spanning two structures) would read each multi-structure organ's internals.

**INVERSE (under-fragmentation) risks found:**
- **coref(54)** — bundles the discourse backbone + gender lookup + CoNLL loading + **EntityAliaser name-individuation**, where name-individuation is a Bruce-Young PERSON-IDENTITY computation (a different structure, RECOG) crammed into the coref organ. Split out (this is the filed `name_branch_shatters` problem).
- **context_grounded_valence(8)** — fuses biased-competition semantic-control gain (IFG) with OFC appraisal in one organ; two structures.
- **predictive_world_model(10)** — fuses N400 predictive-coding surprisal (PRED) with rung-1 causal relevance (CAUSAL) in one organ.
- **safe_kb_gate(25)** — fuses Yonelinas/Bruce-Young recognition (RECOG) with KB is-a fact retrieval (KB-STORE).
- **reading_grounding_loop(24)** — a mega-organ spanning ATL-HUB readout + CLS consolidation + grow-by-reading LEARN; the single biggest "does many structures' jobs" organ.

---

## TLDR (plain language)

We have 83 building blocks. When we sort them by which part of the brain each one is copying, they fall into about 25 real brain systems — which means several systems are currently built as three, six, even eight separate blocks. Some of that splitting is correct: the brain really does track time, space, and who-did-what as separate things, and it really does treat "what could have happened" differently from "what usually happens next," so we should leave those alone. But three splits are just us building the same brain system twice with slightly different wiring, and the science is clear that it is one system: the way we recognise which character a word refers to (built as six blocks — should be one), the way we represent what a word means (built as several channels — should be one fused representation), and the way we lay events out in time (built as six pieces — should be one). Two more are near-exact duplicates that should simply be merged: the two blocks that assign who-is-the-doer use the identical formula, and the blocks that read physical cause-and-effect overlap. Merging these would make the whole system more faithful to how a single brain is actually organised, without losing any capability. A few blocks also do the reverse problem — one block quietly doing two different brain jobs at once — and those should be split; the worst offender is our big "learn by reading" engine, which does three jobs in one. Nothing here says any single block is wrong; it says our *map* of blocks doesn't yet match the brain's *map* of systems, and this document is the corrected map.

**Questions:** none.

**Next steps:** (1) prioritise the coreference merge — largest cluster, unambiguous science, most live duplication; (2) formalise the meaning-representation fusion (already the active north-star) as the second merge; (3) do a code-level pass on the four uncertain assignments in (d) before executing any merge, since a merge is only safe once we've confirmed the two organs really compute the same operation.
