# Brain-functional component map — hd-instrument (2026-08-04)

**Owner:** read-only inventory/synthesis (Director-requested). **Method:** hdlab/*.py
docstring headers (105 files) × `data/capability_registry.jsonl` (57 rows) ×
`notes/capability_integration_ledger.md` × the **disk-verified import graph**
(`from hdlab.X import` across experiments/, hdlab/, tools/, verification/). WIRED
status is computed from the import graph and **triangulated against the *current*
comprehension frontier**, not trusted from the registry's `integration_status`
field alone (that field only answers "imported by *something*", not "imported by the
*active reading path*" — the 08-02 audit's key correction, upheld here).

**The load-bearing distinction this map draws:**
- **WIRED+USED (reader)** = imported by the *current* grounded-comprehension pipeline
  (`tools/read_anne_glassbox_v2` + the `situation_model_accumulate` /
  `coreference_resolver` / `self_improving_loop` hub + the live causal-link /
  grounded-appraisal / coherence-selector frontier cells).
- **WIRED (other track)** = imported + load-bearing, but for a *different* live
  program (ARC/reasoner, KB ingest/query, cortex, VSA capacity science). Not a debt.
- **ISLANDED** = built + validated, imported by ~0 live consumers (or only by its own
  verify/smoke). The wiring opportunities.
- **LOST** = source not on disk / registry-retired; recover from git only.

---

## THE TABLE

### A. Current grounded-comprehension pipeline (the live frontier) — mostly WIRED+USED

| organ (hdlab / key exp) | COGNITIVE PROCESS | BRAIN STRUCTURE | VALIDATION GRADE | WIRED STATUS | serves / notes |
|---|---|---|---|---|---|
| `situation_model_accumulate.py` (AccumulateRegister, CausalLinkRegister, make_situation_register) | situation-model accumulation; per-entity role-bound event register; causal-link write/read | hippocampus + DMN/mPFC event model (Kintsch/van-Dijk, Zwaan event-indexing) | VET-confirmed organ, atoms 29609/29610; **CausalLinkRegister honestly = GIVEN-link write/read capacity 0.9722, NOT a selector** (ledger 08-03) | **WIRED+USED — the hub.** ~20 frontier consumers (all causal_link, grounded_appraisal, coherence_selector, cross_span, goal_* cells + both readers) | THE spine of the reading layer |
| `coreference_resolver.py` (run_match_or_allocate, run_principle_b, normalize_tokens) | coreference / entity identity across clauses | hippocampal relational antecedent retrieval; Centering/Cb | atoms 29613/29614/29616/29618; **recency backward-search FALSIFIED on the recency-trap (0/4)** — not a coherence selector | **WIRED+USED.** read_anne_glassbox_v1/v2 + many frontier cells | competency #1 (entity-identity); the falsified `_pick_strict_cb` is explicitly NON-REUSED |
| `self_improving_loop.py` (decide_keep_or_revert, ABSTAIN_BAND) | coherence-gated keep/revert control; abstain band | ACC/PFC conflict-monitoring + control | promoted 2026-08-02 (VET'd in exp_coref_autonomous_fix_router) | **WIRED+USED** as the abstain-band control-flow in coherence_selector v1–v4 + consolidation_ledger | decision layer; reused as *architecture* only |
| `state_of_mind.py` (WorkingOverlay, PRONOUN_SCOPE, deixis_person, EntityState) | symbolic discourse working-overlay; participant/deixis tracking | PFC working memory + discourse model | validated 2-layer state-of-mind arc (07-17, SETTLED) | **WIRED (reader cluster).** Imported by coref/bundle_focus/event_centrality/scene_segment + ~25 exp_reader_* cells | registry row `working_overlay_situation_reader` gate=SHELVE, but the *primitives* are live in the reader cluster |
| `candidate_generator.py` (CandidateGenerator, ud_tokenize, candidates_from_parse) | argument-candidate extraction: sentence → (verb, arg-candidate) set | IFG/pTL argument-structure; UD parse front-end | rides persisted pos_tagger+arc_parser front-end | **WIRED (reader-extraction cluster).** ~25 exp_reader_whoaffected/*extraction cells | **directly serves the CURRENT event-extraction bottleneck** (the frontier's binding constraint) |
| `coref.py` / `bundle_focus_coref.py` / `event_centrality_coref.py` / `coref_distractor_suppress.py` / `scene_segment.py` | cross-sentence pronoun coref backbone; Cowan-4 event-bundle focus; event-centrality tie-break; distractor suppression; scene segmentation | hippocampal relational + Cowan-4 focus of attention + WM | reader-cluster, internally composed on state_of_mind | **WIRED (reader cluster)** — compose on state_of_mind; consumed by the xsent-coref exp battery | the "reader" internal subtree (07-25 audit's healthy island) |
| `animacy_lexicon.py` | glass-box animacy/agent-capable lexicon | temporal-lobe lexical semantics (WordNet) | registered 2026-08-03 (coverage-gap close) | **WIRED (thin)** — 1 consumer (extraction_commit_then_revise_v4) | supplied-knowledge asset for agent detection |
| `glass_box_loop.py` (cleanup_with_margin) | retrieve→gate→audit→requery→commit micro-loop | PFC-gated cortico-hippocampal loop | CHAIN_GRADE micro-loop | **WIRED** — reader-selfimprove + composition cells | |

### B. Reasoning / retrieval / KB track — WIRED to a *different* live program (not a debt)

| organ | COGNITIVE PROCESS | BRAIN STRUCTURE | GRADE | WIRED STATUS | notes |
|---|---|---|---|---|---|
| `hd_fact_store.py` | source-trust-vetted fact store (S,R,O as one bound HV) | semantic memory / neocortex | wired pre-07-25 | **WIRED (ARC/KB track).** ~10 consumers | one of the few hdlab pieces reaching the ARC frontier |
| `director_kb.py` / `director_kb_query.py` / `kb_encoder_registry.py` / `director_kb_*_sources.py` | KB ingest + query surface | semantic knowledge store | wired load-bearing | **WIRED (KB track).** query surface cited in CLAUDE.md | ingest/query cluster |
| `char_trigram_encoder.py` | zero-external-model text→HD | VWFA orthographic | wired load-bearing | **WIRED (load-bearing).** ~59 exp + 12 hdlab | the de-facto text encoder for KB/ARC |
| `typed_rule_parser.py` (parse_tablestore_typed) | typed WorldTree rule graph builder | rule/schema representation | promoted 2026-07-25 (P1) | **WIRED.** reasoner.py + intrinsic_foundation_loop | the graph the reasoner consumes |
| `reasoner.py` (DerivationReasoner, meet-in-middle) | verification-by-derivation composed reasoner (audit P5) | PFC compositional reasoning | **built 2026-07-25 then ABANDONED 2026-07-27** (below-band walls) | **WIRED-but-SHELVED.** ~9 ARC-reasoner cells import it; docstring claims "supersedes K=2 multi_hop" but comprehension frontier imports it 0× | revive if encoder-comprehension reps lift its coverage walls |
| `kg_traversal.py` / `multi_hop.py` | KG ingest + n-hop chain traversal | hippocampal path integration | kg_traversal CERT-585 chain-grade K=2; multi_hop MIDDLE_BAND K=2 | **WIRED (kg track)**; `multi_hop.py` wired-but-orphaned, no registry row | the *weaker* K=2 chain; the better meet-in-middle never promoted |
| `additive_map.py` (AdditiveKGMap) | additive inductive KG map-builder (CLS schema mode) | neocortical schema (CLS slow system) | maintained capability | **WIRED (ingest-gate track).** ~12 consumers | |
| `cortex.py` / `edge_importance.py` + M1.x primitives (`refuse_gate`, `context_retention`, `chunked_attention`, `role_slot_summarizer`, `clarify_gate`, `noise_channel`, `semantic_parser`, `intent_classifier`) | dialogue/cortex composed stack: refuse, context, attention-router, summarize, clarify, intent | PFC cortical control stack | ALREADY_WIRED family (07-28 triage); many CG/HARD_PASS individually | **WIRED (cortex track)**, disjoint from reader/ARC roots | 4 disjoint composition roots (07-25): cortex, situation_reader, bundle_focus_coref, semantic_parser |
| `reachability_audit.py` / `completeness_checker.py` | cert/consistency audit; sentence-completeness | metacognitive monitoring | ALREADY_WIRED (cert_audit) | **WIRED (cert track).** ~15 codex/ingest-gate cells | |
| `ultrametric_clustering.py` | hierarchical coarse-graining | cortical hierarchy | ALREADY_WIRED | **WIRED.** coarse-grain/edge-importance cells | |

### C. Substrate primitives (infra — correctly not standalone "capabilities")

| organ | process | grade | status |
|---|---|---|---|
| `binding.py` / `bundling.py` (superposition) / `atoms.py` / `memory.py` / `modulators.py` / `tracing.py` / `store.py` / `semantic.py` / `metrics.py` | VSA bind/unbind, superposition, cleanup memory, control scalars, trace bus, storage | ALREADY_WIRED (superposition, composition) | **WIRED (universal)** — imported everywhere incl. the reader closure (binding/bundling/modulators/tracing reachable from the 8-file reader set) |
| `cleanup_family.py` / `iterative_attractor.py` / `modern_hopfield_readout.py` | pattern-completion / cleanup / attractor readout / softmax-Hopfield retrieval | ALREADY_WIRED (readout, pattern_completion, cleanup_attractor = ONE mechanism split 3 ways) | **WIRED** (cleanup/attractor); `modern_hopfield_readout` near-islanded (1 consumer) |
| `sequence_memory.py` | sequence binding (ordered-pair store) | HARD_PASS every depth (a27939c5) | **WIRED (sequence_binding family)** |
| `continual.py` | NREM-replay consolidation, forgetting bounds | MEASURED_MECHANISM +0.57 drift-reduction | **WIRED (catastrophic_forgetting).** ~15 CLS/replay cells |
| `schema_exemplar_bayes.py` / `bayesian_inference.py` / `perceptron.py` / `learning.py` | schema router; Bayes/EM; discriminative perceptron; RM-Hebbian | ALREADY_WIRED (schema_abstraction) | **WIRED** |
| encoders: `vwfa.py` / `ppmi_sparse_encoder.py` / `composed_encoder_v3.py` / `concept_encoder.py` / `hippocampal_encoder.py` / `random_indexing.py` / `gsbc_graded_encoder.py` / `whitening.py` / `late_combine.py` / `char_positional_encoder.py` / `token_vocab.py` | text/concept→HD encoding variants (VWFA, PPMI/SVD, CLS-DG, random-indexing, graded sparse block, N400 late-combine) | VWFA / hippocampal DG / distributional cortex | composed_encoder_v3 SHELVE (superseded, untouched since 07-03) | **MIXED** — char_trigram WIRED; the vwfa/ppmi/composed_encoder_v3 cluster SHELVED; **current reader uses NO neural encoder** (regex/difflib) |

### D. ISLANDED — built + validated, ~0 live consumers (the wiring opportunities)

| organ (hdlab / exp) | COGNITIVE PROCESS | BRAIN STRUCTURE | VALIDATION GRADE | WIRED STATUS | serves |
|---|---|---|---|---|---|
| **`predictive_coding.py`** | **novelty / prediction-error residual detection** | **VTA-dopamine RPE + cortical predictive coding (Friston/Rao-Ballard)** | **HARD_PASS** as a novelty signal: `exp_disequilibrium_novelty_signal_test_v1` residual gap 0.27, p=0.0003, needs-vs-fits IQR-overlap 0.0 (disk-verified) + `exp_lap2_9_predictive_coding` HARD_PASS | **ISLANDED from the reader.** Consumers = only prediction-hierarchy / selfplay / disequilibrium *probe* cells; imported 0× by the comprehension hub or the self-extension trigger | **EXHIBIT A.** The organ that decides "this is novel → mint a new competency". Just validated for exactly that role, still not wired as a standing trigger |
| **`working_memory.py`** (multibank K-capacity) | **K-item working-memory capacity via per-bank cleanup** | **PFC + hippocampal WM (Cowan-4 → K-capacity)** | **chain-grade CERT K=4096** (recall 0.9927/0.9801; ledger 62ce9e7dca071828); phase-diagram to K≥16384 | **ISLANDED from the reader.** Only in-hdlab consumers are `context_retention.py` + `role_slot_summarizer.py`, themselves unreachable from the reader | AccumulateRegister's naive per-entity dict hits a capacity wall on longer/denser passages — this is the direct fix |
| **`situation_model_multibank.py`** (MultiBankAccumulateRegister) | multi-bank situation register (capacity fix for flat-bundle wall) | hippocampal multi-entity binding | validated drop-in (verify_situation_model_multibank_dropin) | **near-ISLANDED.** Only `exp_situation_model_multibank_capacity_v1` + verify import it; the live causal-link frontier uses flat `AccumulateRegister` | swap-in when entity count grows |
| **`slot_attention_wm.py`** (SlotAttentionWM) | brain-faithful slot-attention stateful WM core | parietal slot-attention / PFC binding | `cross_boundary_comprehension_construction` = validated_asset 2026-07-28 | **ISLANDED-ish** — the "stateful core" line (stateful_core_situation_model, oracle_wm, mes cells); disjoint from the grounded-appraisal frontier | alternative stateful situation core |
| **VAMP-EP deep-chain solver** (`exp_wave14_*vamp_chain*`) | forward-backward Expectation Propagation / belief-propagation over chains | cortical belief propagation | acc **1.000 to depth ~200**, robust K=5000 + 30% edge-noise (VAMPCHAIN_RESTORES / VAMPNOISE_ROBUST verified) | **ISLANDED — never left experiments/.** No hdlab organ, no registry row (grep-confirmed) | the repo's best deep-chain solver; the multi-hop selector's 3-hop collapse fix |
| **`action_selection.py`** (basal-ganglia Go/NoGo) + certified `pfc_gate_cfrpe_trained_v2` (RPE actor-critic) | value-based action selection; error-driven RL update | basal-ganglia + VTA-dopamine actor-critic | action_selection extracted from 5-seed FULL HARD_PASS; pfc_gate_cfrpe HARD_PASS (gonogo_lift 0.600, narrow n_fair 2/7) | **ISLANDED** (action_selection: only verify test) | the reuse target for the grounding sim's appraisal→action layer (ledger 08-03) |
| **grounded appraisal function** (`exp_grounded_appraisal_sim_earned_v1` + transfer) | earned appraisal/valence → action (blocked-goal→anger→retaliate) | amygdala/OFC appraisal + goal-outcome valuation | MECHANISM_EARNS (5 seeds; all 3 floors fail; revenge emerges no label); transfer = EXTRACTION_BOTTLENECK (arm-A oracle 1.0 vs recency 0.0) | **ISLANDED (gate=WIRE, target unbuilt).** Not yet consumed by a reading organ | the grounded-meaning layer; blocked on event-extraction to populate appraisal slots |
| `gated_fusion.py` (+0.297) | learned per-axis convex-gate text+grounding fusion | multimodal integration | HARD_PASS full 8-seed; promoted to hdlab 07-28 | **TRAPPED_SHARED** — applied only inside the encoder-fusion exp cluster; current reader has no encoder | Pareto-dominates z-avg fusion; narrow (recovers z-avg's self-damage) |
| `encoder_retrain_persist.py` | minimal-unfreeze entity-consistency encoder lever | VWFA plasticity | chain-grade generalizing lever (atom 29596) | **WIRED (thin)** — opt-in loader + 1 verify consumer; no reader adopts it | eval-only encoder swap for entity-addressed comprehension |
| native-VSA binding cells (`cross_slot_relational_binding`, `native_binding_naturalistic_multirelation`, `read_conditioning_novel_filler`, `situation_model_assembly_binding_wm_coref`) | zero-shot/novel-filler role-binding; multi-relation slot-filling; integration proof | parietal/PFC role-filler binding | VET-confirmed / chain-grade (idealized input) | **ISLANDED** (gate=WIRE, no consumer) | binding competencies for the situation model |
| `k_cliff_scaling.py` (capacity_scaling) | closed-form sequence-binding capacity law | — | analytic | **ISLAND** (gate=WIRE, sizing-consult) | cell-design sizing helper |
| `additive_map`-adjacent `learned_relational_readout` / `cross_boundary` readouts | learned relational readout across boundary | pMTG-IFG semantic control | landed_hard_pass_majority (readout); attn_bilinear HARD_FAIL | **TRAPPED_SHARED** | |

### E. LOST / retired

| organ | process | status |
|---|---|---|
| **`sr_routing_multihop` (+0.253)** | SR-based multi-hop routing | registry `orphaned_source_not_locatable_retired_2026-08-03`, gate=SHELVE — **source gone, recover from git history only** (`git log --all -- '*sr_routing*multihop*'`) |
| `binder_direct_supply_grounding` | direct-supply grounding | CLOSED correctly (data-bound, atom 29571); Binder-65 not on disk |
| shelved diagnostics: `lock_in_amp.py`, `redundancy_robustness`, `external_embedding_diag` (invariant-2b: diagnostic-only), `provenance_watermark`, `semantic_concept_learning` (superseded by scale-win encoder), `language_prediction_DEPRECATED`, dead modules (`action_selection`*, `compose_freq_routing`, `excitability`, `profiling`, `self_manager`) | — | SHELVE / dead (07-25 named 7 truly-dead; *action_selection now has a reuse target — see D) |

---

## SYNTHESIS

### 1. ISLANDED-BUT-VALIDATED (the wiring opportunities, ranked by relevance to self-extension + grounded comprehension)

1. **`predictive_coding.py` — novelty/prediction-error organ (HARD_PASS).** Exhibit A. Just
   validated (disequilibrium test, p=0.0003) as the exact signal that discriminates
   "needs a new schema" from "fits" — i.e. the **minting trigger for self-extension** —
   yet imported 0× by the comprehension hub or any standing loop. Highest-leverage wire.
2. **VAMP-EP deep-chain solver (depth ~200, never left `experiments/`).** The repo's best
   multi-hop engine, no hdlab organ, no registry row. The coherence-selector's confirmed
   3-hop collapse (v4: all ~0.35 < random at 3-hop) is exactly what this solves.
   Recover→port into an hdlab organ on the situation-model substrate. **Caveat:** all VAMP
   wins are synthetic KG chains; transfer to NL causal chains is untested (the real frontier).
3. **`working_memory.py` multibank (chain-grade K=4096) + `situation_model_multibank.py`.**
   The live reader uses a flat per-entity dict (`AccumulateRegister`) that will wall on
   longer/denser passages; the certified K-capacity fix sits unused with only unreachable
   in-hdlab consumers. Direct answer to MEMORY.md's "richer/longer content" next lever.
4. **`action_selection.py` / certified `pfc_gate_cfrpe` actor-critic.** The reuse target the
   grounding-sim ledger already names for appraisal→action + error-driven credit. Islanded
   but is the *correct organ to re-point*, not rebuild (the reuse gate keeps predicting right).
5. **grounded appraisal function** (earned-sim, transfer=extraction-bottleneck) + **native-VSA
   binding cells.** Gate=WIRE with no target built yet; blocked precisely on event-extraction.
6. **`gated_fusion.py` / `encoder_retrain_persist.py`.** Real encoder-track wins, but
   categorically out of scope for the *current* reader (it reads with no neural encoder) —
   wire only if/when the reader adopts an encoder front-end.

### 2. COGNITIVE-PROCESS COVERAGE MAP (for grounded comprehension + self-extension)

| process | status | organ |
|---|---|---|
| perception / text encoding | **COVERED (but reader bypasses it)** — reader uses regex/difflib; char_trigram/vwfa/ppmi encoders exist but the live reader reads without one | char_trigram_encoder (KB); reader = symbolic |
| entity-tracking / coreference | **COVERED (wired)** | coreference_resolver + state_of_mind reader cluster |
| situation-model accumulation | **COVERED (wired hub)** | situation_model_accumulate |
| working-memory capacity (K-item) | **ISLANDED** — flat dict live; certified multibank unused | working_memory + situation_model_multibank |
| argument/thematic-role extraction | **COVERED but WEAK — the confirmed live bottleneck** (cross-span/inferential blockers unreachable locally) | candidate_generator + patient-extraction cells |
| causal attribution / cross-span binding | **PARTIAL** — recall wins (cross_span_causal_binding), **selection unsolved**; CausalLinkRegister is given-link capacity, not a selector | situation_model_accumulate.CausalLinkRegister |
| causal-coherence *selection* (M_backward) | **GAP / in-progress** — coherence_selector v1 HARD_FAIL→v2 HARD_PASS(known types)→v3 MIDDLE_BAND(novel types, abstract rule confirmed); 3-hop collapses | exp_coherence_selector_* (not yet an hdlab organ) |
| novelty / prediction-error | **ISLANDED (HARD_PASS)** — the self-extension trigger, unwired | predictive_coding |
| appraisal / valence (grounded) | **ISLANDED (earned, WIRE-gated)** — blocked on extraction | grounded appraisal fn; reuse pfc_gate_cfrpe |
| goal representation | **PARTIAL** — goal_register / goal_close cells on CausalLinkRegister; no standing organ | exp_goal_* |
| ToM / mentalizing | **GAP (thin)** — intent_valence_via_mentalizing probe only; no wired organ; retaliation≠general irony (per MEMORY) | — |
| consolidation / schema-learning | **COVERED (wired, other track)** | continual + schema_exemplar_bayes + additive_map |
| retrieval / pattern-completion | **COVERED (wired)** | cleanup_family / iterative_attractor / hd_fact_store |
| action selection / RL credit | **ISLANDED** — certified, not wired to comprehension | action_selection / pfc_gate_cfrpe |
| multi-hop derivation | **ISLANDED (best solver) + SHELVED (reasoner)** | VAMP-EP; reasoner.py; multi_hop.py |

**Reading of the map:** the *reader spine* (encode→coref→situation-model→consolidate→retrieve)
is genuinely WIRED. The **gaps + islands cluster exactly on the current program**: grounded
appraisal, causal-coherence *selection*, novelty-triggered self-extension, and the WM-capacity
headroom those need — and for three of the four we already own a validated organ sitting
islanded (predictive_coding, working_memory, VAMP-EP, action_selection/pfc_gate).

### 3. TOP 5 WIRING ACTIONS (most impactful first)

1. **Wire `predictive_coding.py` as the standing novelty/prediction-error trigger** for the
   self-extending store (the "mint a new competency when residual is high" gate). It's
   HARD_PASS for exactly this discrimination and currently fires only inside throwaway probes.
2. **Port VAMP-EP into an hdlab organ** on the situation-model substrate + add a forward pass
   (meet-in-middle) to the coherence selector — recover-don't-reinvent the 3-hop collapse fix;
   test transfer to NL causal chains (the untested frontier). Also `git`-recover `sr_routing_multihop`.
3. **Swap the reader's flat `AccumulateRegister` for `working_memory`/`situation_model_multibank`
   K-capacity** behind an entity-count threshold — removes the capacity wall "richer/longer
   content" will hit; the cert (K=4096) already exists.
4. **Re-point `action_selection` / `pfc_gate_cfrpe` as the appraisal→action layer** for the
   grounded function (the ledger's named reuse), instead of any new RL organ — unblocks the
   grounded-meaning layer once extraction lands.
5. **Promote the causal-coherence selector into an hdlab organ** once v3's abstract-rule result
   stabilizes (it's currently exp-trapped across v1–v4), and **harden `candidate_generator`
   for cross-span/inferential extraction** — the confirmed binding bottleneck feeding both the
   selector and the grounded appraisal function.

---

**Honesty caveats.** (a) "WIRED+USED (reader)" is judged against the current
`dataprep/mcguffey-graded-corpus` frontier; a different active program (ARC/cortex/KB)
legitimately consumes many "other-track" organs — not flagged as debt. (b) Grades cite the
registry/ledger/metrics.json where available; several "ALREADY_WIRED" rows are *integration*
verdicts, not re-certifications (`tier=chain-grade` = ≥1 HARD_PASS ever, not "family nets
positive" — skunkworks 07-28). (c) `predictive_coding` HARD_PASS is a novelty-discrimination
result on one disequilibrium test, not a general-purpose cert. (d) `CausalLinkRegister` 0.9722
is given-link capacity, explicitly NOT a selector — do not read it as coherence-selection.
(e) VAMP-EP + all multi-hop wins are synthetic KG chains; NL transfer untested.
