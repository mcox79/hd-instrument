# Relational Capability Track Record — Off-Disk Cert Map (SCOUR, 2026-07-10)

**Purpose:** authoritative, off-disk inventory of EVERY relational-capability experiment cross-referenced to its LANDED CERT TIER, so the "make the relational aspect real" program builds on proven vs failed vs untested — not on memory.

**Authoritative source:** `data/substrate_index/meta/cert_ledger.jsonl` (1,576 rows; the landed math/meta atom cert ledger). Tier read from `verdict` + `cert_class` per row (the skunkworks A5 atomize step recomputes each verdict off-disk per Fix#28, so the ledger row — not the filename — is the verdict of record). Load-bearing recent numbers additionally re-read from the cell `metrics.json`. Numbers below are traceable to a ledger row or a metrics.json field; where a verdict is not findable it is marked UNKNOWN.

**Tier normalization used here:** CG = CHAIN_GRADE / HARD_PASS (proven across seeds, discriminator fires). MM = MEASURED_MECHANISM (real signal, bounded/scope-narrowed/single-seed/by-construction). MB = MIDDLE_BAND (partial/inconclusive). HF = HARD_FAIL / HONEST_NEGATIVE (proven bound / capability closed). **Caveat (anchor):** many CG cells are tagged `by_construction` / `HARD_PASS_by_construction` — these are construction-proofs, NOT capability wins; flagged inline.

**Scan scope:** 550 relational EXPERIMENT cells matched (of 1,118 EXP_ atoms). Full tier histogram per bucket below; tables list the load-bearing (non-routine-PASS) cells. ~290 additional `pre_reg_pass` micro-atoms in B (mostly chain-depth phase points) are summarized in aggregate, not enumerated.

---

## A. BINDING OPERATOR (bind/unbind, systematicity, role-filler, superposition, cross-modal)

Histogram (non-PASS): CG 19 · MM 23 · MB 1 · HONEST_NEG 7 · HF 5.

| Tier | Cell | Key metric | Verdict (one line) |
|---|---|---|---|
| CG | `substrate_permutation_binding_multiocc_v2` | HRR primitive upgrade | Cyclic-shift cleanup rescues FHRR collision; multi-occurrence bind PROVEN. |
| CG | `parietal_relational_v3` | HRR unbind 0.995, lift 0.749 | Unbind of role-filler bindings chain-grade. |
| CG | `parietal_cortex_spatial_reasoning_v1` | move-recall 0.867, lift-over-fixed 0.576 | Movable rebind (rebind + move + recall) chain-grade. (NB: the *relational* arm of this cell aliased to movable and landed HONEST_NEG below.) |
| CG | `substrate_cross_modal_binding_visual_auditory_v1` (3 seeds) | disc 18/45, pos-ctrl 1.0 | 2-modality TPJ-analog HRR cross-modal bind proven; "HRR works, positional partial-sum broken". |
| CG | `substrate_cross_modal_binding_3rd_modality_v1` (3 seeds) | n_disc 16-17/45 | 3-way tensor-product cross-modal bind CG. |
| CG | `cross_modal_binding_4_5_modality_v1` (3 seeds) | disc_frac 0.74-0.78, recall 1.0 | Extends cross-modal bind to 4/5 modalities CG. |
| CG | `substrate_theta_gamma_v2` / `v4_extended_seeds` (7 seeds) | log2 delta 3.32-4.32 | Theta-gamma nested position-encoding sequence bind CG (1-in-7 seed outlier). |
| CG | `substrate_pc_sparsity_x_encoder_crossproduct_v2` (3 seeds) | capacity lift 2x | Sparsity x encoder capacity lift CG. |
| CG | `substrate_anchor4_encoder_family_N16384` (3 seeds) | dominance 1.0, recall 0.73-0.77 | 5 encoders (binary/bipolar/HRR/FHRR/sparse) all competitive at N16384. |
| CG | `substrate_task_vector_HRR_ICL_K_500` | K50 TV 1.0 → K1000 0.243 | HRR task-vector ICL; K-cliff of mechanism death localized. |
| CG | `cortex_context_retention_v2` (M1p5) | two-tier top1 1.0 @load 800 vs 0.021 | First cortex WM/LTM composition primitive CG (2-tier bind). |
| MM | `theory_of_mind_sally_anne_nested_hrr_v1` | smoke HP | Nested HRR ToM (Sally-Anne) — smoke MM, not landed FULL. |
| MM | `substrate_role_tagged_compositional_generalization_on_concept_KG_v1` | HYBRID 1.0, NO_ROLES 0.167 | **Role-filler binding for compositional generalization = by-construction saturation**; label-driven encoder pre-fuses the category basis, role-binding lift NEUTRAL. Did NOT reach CG. |
| MM | `pfc_goal_conditioned_gate_v2` | BIND_CLEAN 0.000 @depth6 | **Cleanup-after-bind DESTROYS bind structure** — snaps to single codebook entry, loses composite. Substrate-algebra bound. |
| HF | `stage3_hrr_involutive_systematic_generalization_v1` | hrr_inv 0.0067 = chance | **Systematic generalization via involutive HRR = mechanism null.** |
| HF | `substrate_working_memory_v2_extended_K_cleanup_per_slot` | K ceiling 64 | Cleanup-per-slot does NOT extend bind capacity (architectural). |
| HF | `substrate_order_binding_family_v1` (2 seeds) | all 3 ops K* 500 identical | Order-binding op family INVARIANT at WM regime. |
| HF | `substrate_binding_op_x_capacity_v1` (3 seeds) | K-cliff 750 all ops | Binding-op axis capacity-INVARIANT; choosing the bind op does not change capacity. |

---

## B. COMPOSITION / MULTI-HOP CHAINING (reach@2+, chain depth, traversal, compounding fidelity)

Histogram (non-PASS): CG 25 · MM 26 · MB 14 · HONEST_NEG 8 · HF 17. (+~289 routine chain-depth `pre_reg_pass` phase-point atoms.)

**THE PROVEN CORE — multi-hop depth via PARTITION-ORACLE routing:**

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| CG | `phase_diagram_multihop_depth_ceiling_sweep_20_25_30` | reach: d15 0.810, d20 0.708, d25 0.673, d30 0.637 | Depth ceiling 30, partition-oracle routed cleanup, all HP bands. |
| CG | `multihop_reasoning_depth_20_to_40_gpu` (3 seeds) | d40 0.533 (>0.50), per-step 0.985 | Envelope extends to depth 40; per-step accuracy scale-invariant. |
| CG | `multihop_reasoning_depth_45_to_60_gpu` (3 seeds) | d45 0.532, d60 0.480 (<0.50) | 0.50-crossing bracketed 45-60; per-step ~0.985 stable across 4x depth range. |
| CG | `multihop_reasoning_depth_50_55_crossing_bracket_gpu` (3 seeds) | d50 0.502, d55 0.455 | d* (recall=0.50) localized to 50-55 hops. |
| CG | `substrate_multihop_compose_fly_lsh_multibank_partition_v2` | 5-hop per-hop 0.955 | Partition-per-hop routed 5-hop chain CG — **oracle-routing scope flag** (twin MM says substrate-native routing OPEN). |
| CG | `substrate_multihop_brain_pushback_v3` | depth5 per-hop argmax mean 0.582 | Brain-grounded per-hop argmax-cleanup baseline; mechanism arms all tie baseline (substrate at ceiling). |
| CG | `substrate_compose_freq_routing_v5_DEFINITIVE` | 5 seeds, N8192 | Frequency-routing composition definitive CG. |
| CG | `digital_repeater_regenerative_hard_snap_cleanup` (math atom) | regen d5 0.70, rises with N | **Hard-snap (regenerative) cleanup BEATS analog soft-carry above Hebbian crosstalk M/N>1** — the fidelity mechanism that makes chaining survive depth. |
| CG | `cortex_ultrametric_clustering_coarse_grain_v1` (3 seeds) | cap-drop 0.212, d-vs-random +0.104 | First chain-grade compositional-abstraction primitive (after E-tensor abstraction was refuted). |
| MM | `phase_diagram_multihop_depth_extension_via_partition_oracle_v1` | d5 0.965 → d15 0.808 | Oracle-routing REQUIRED for depth>5 (by-construction). |
| MM | `multihop_reasoning_scale_invariance_N_axis` | d30 scale-invariant, d15 breaks | Partial scale-invariance; d15 N-dependent. |
| MM | `multihop_reasoning_partition_size_sweep` | PS5 0.908 / PS10 0.748 / PS20 0.492 @d15 | Per-hop cleanup accuracy scales INVERSELY with partition size — NOT scale-invariant on PS axis. |
| MM | `substrate_multihop_consolidation_memory_v1` | by-construction saturation | Consolidation "answers as 1-hop" — immediate-write regime, not true multi-hop. |

**THE WALLS — substrate-NATIVE multi-hop (no oracle) and primitive composition:**

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| HF | `brain_faithful_4_primitive_multihop_chain_composition` (CAPABILITY CLOSED, 2x drill) | drill A + drill B both HF @depth15 | **Chain-grade primitives CANNOT compose a multi-hop chain at depth 15; M3 needs external cortex layer for hint derivation.** Central closure. |
| CG(meta) | `META_RULE_AP` / `META_RULE_AQ` | 2 witnesses | Naive compose of CG primitives breaks on signal-shape / regime mismatch; multi-step needs an explicit state-tracker primitive re-firing upstream per step. |
| HF | `partition_oracle_substrate_derived_hint` | route acc @ chance | Substrate-DERIVED (non-oracle) routing hint = no signal. |
| HF | `partition_oracle_brain_composition_hint` (3-primitive) | arm_c 0.01 | vmPFC+cortex+hippo lacks 4th primitive (dlPFC WM); composition collapses. |
| HF | `partition_oracle_pfc_wm_state_tracker` (4-primitive) | all adapters dead | State-tracker cannot rescue hop-0-anchored upstream schema. |
| HONEST_NEG | `multihop_bidirectional_meet_in_middle_v3` (5 seeds) | bidir < fwd-half at every depth | No meeting premium; meeting step adds zero. |
| HONEST_NEG | `substrate_multihop_csp_gated_iterated_cleanup_v1` | csp hurts baseline | 4th barrier-1 attempt; CSP hurts geometric chain decay. |
| HONEST_NEG | `gap1_multihop_ldpc_rts_bidirectional_v2` | zero lift | LDPC/RTS converge to soft-forward. |
| HONEST_NEG | `cross_corpus_compose_chat_v1` | compose 0.059 = single 0.059 | Cross-corpus composition zero lift. |
| MB/HF | `substrate_multihop_consolidation_v3_heldout_fix` / `pointer_chain_hybrid_v2` / `wm_scaffolded_v1` | all HF | Held-out-correct multi-hop consolidation variants all fail. |
| HF (infra) | ~10 `HF_BACKLOG` cells (chain-gen yielded zero chains, cardinality breach, runner died) | — | Test-design/infra failures, NOT capability signal. |

---

## C. RELATION ENCODING / RICHNESS (open vs closed vocab, relation-type ladder, edge richness)

Histogram (non-PASS): 1 landed. **Nearly untested.**

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| MB/HF | `relation_type_richness_ladder_v1` (3 seeds, FULL, 2026-07-09) | best_inductive flat [0.673, 0.667, 0.666, 0.675], slope 0.002; type_entropy ROSE 0.62→1.40, n_types 2→15 | **Relation-type richness ALONE does not raise held-out inductive inference** — confound-free (oracle-PA flat range 0.004, degree held). Cell verdict MIDDLE_BAND; atomized honest-negative. |

Note: relation *encoding* capacity (open vocabulary, distinct-entity/edge counts) is exercised implicitly by the KB-ingest tooling (bio-trio 222k triples ingested, deterministic re-ingest) but there is NO cert cell that isolates "richer relation VOCABULARY raises relational capability." **GAP.**

---

## D. GOAL-CONDITIONED / SR TRAVERSAL (successor-representation, goal-conditioning, routing, landmark)

Histogram (non-PASS): CG 6 · MM 4 · HONEST_NEG 5 · HF 1.

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| CG | `chain_grade_barrier1_substrate_native_break_partition_oracle_goal_conditioning` (3 seeds) | lift ~0.46-0.54 over baseline | **Barrier-1 goal-conditioning BROKEN via partition oracle** — 3-seed verified. Per-seed FULL cells landed MIDDLE_BAND (A0.30/B0.83); cross-seed aggregate promoted to CG. Oracle-routed. |
| CG | `substrate_partition_routing_10M_full_v2` / `hierarchical_2level_v1` | chain-grade @M100k, bound @M1M | Partition ROUTING capacity (not reasoning) proven to 100k, bounded 1M. |
| CG | `kb_partition_by_source_class_v4_calibrated` | routing acc 1.0, leak 0.0 | Source-class routing CG (a capacity/deletion capability). |
| MM | `pfc_gate_cfrpe_trained_v1` (math atom) | target-cosine-independent advantage preserved across scale | **cfRPE successor-feature transport for GoNoGo gate DELIVERS the v3 revival** — but end-to-end floor-bound in deep regime, additive rail broke. SR gating = MM. |
| MM | `phase_diagram_capacity_sweep_n16384_vc_higher_alpha` | rec 1.0 @alpha·VC≤4.1 → 0.42 | SR-key routing envelope mapped; collapses when codebook exhausted. |
| HF | `pfc_goal_conditioned_gate_v3_goal_cosine_gating` (math atom) | plateaus 0.42 vs oracle 0.994 @depth6 | **Goal-cosine gating structural ceiling** — target-cosine captures only 11% of headroom. |
| HONEST_NEG | `gap1_partition_routing_cortex_R_schema_closed_form` | top1 0.000 overfit | Closed-form linear router fails (overfit 3/3). |
| HONEST_NEG | `gap1_partition_routing_bidirectional_collide_fly_lsh` | 3 routers cluster @0.66 | Learned linear routers stuck at naive-centroid floor. |
| HONEST_NEG | `typed_multibank_K128_adversarial` | typed recall 0.44 vs baseline 0.998 | **Typed routing actively HURTS** at overlap 0.40. |
| HONEST_NEG | `substrate_routing_geometry_family_kg_ingest_v2` / `hierarchical_bank_v1/v2` | 4/5 arms crash @M100k; router SNR 0.358 | Substrate-native routing geometry fails at ingest scale / under load. |

**Pattern: routing WITH an oracle = CG; every LEARNED / substrate-native / typed router = HONEST_NEG.**

---

## E. ANALOGY / GEOMETRIC / ADDITIVE CODES (TransE h+r≈t, additive/geometric inductive inference, held-out generalization — the current lead)

Histogram (non-PASS): CG 1 (+1 math-VSA CG) · MM ~3 · MB 1 · HONEST_NEG 3 · HF (grounding) 3.

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| CG | `MATH_VSA_CELL1_ANALOGY_COMPLETION_HRR_BIND_UNBIND_CLEANUP` (math atom) | r1 = 0.8613, mechanism-vs-baseline gap 0.854 | **Analogy completion via bind/unbind/cleanup PROVEN CG** on synthetic/math VSA (a:b::c:? closed-form). K-dist sweep also CG. This is the current lead's proof-of-mechanism — but IN-graph / synthetic. |
| MM | `inductive_relational_transfer_to_NOVEL_entities_moves_OFF_ZERO` (math atom) | content-conditioned bilinear SCORER off-zero; **global TransE = ZERO** | Inductive transfer to novel entities is "non-vacuous, modest, under-parameterized" via a bilinear scorer; **global additive TransE (h+r) scored ZERO / vacuous.** |
| MM | `schema_bundle_structural_transfer_holistic_analogical_map` (math atom) | M=R·mean·bind(B_inv,A) | Bundle-schema holistic analogical map extracts systematic relational transfer (synthetic dialable subject). |
| HF | `grounding_learned_sr_heldout_reasoning_v1` (3 seeds, FULL, 2026-07-10) | **LEARNED held-out reach@2 = 0.1148 vs random-code CODEALIAS 0.104, Δ=0.011 < 0.05 margin; codes_necessary=False. KNOWN_T held-out reach@2 = 0.462; memoryless 0.017** | **THE central held-out inductive negative:** learned SR codes route NO BETTER than random codes on held-out edges = memorized search, not reasoning. Learned DOES fill holes over memoryless (+0.098) = real memorized traversal, but NOT inductive inference. |
| HF | `grounding_density_payoff_relational_reasoning_v1` (3 seeds, FULL) | rel_gain sparse 0.084 → dense 0.022, rise = **-0.062** | **Density (k-core) ALONE does not raise held-out reasoning** — branchiness confound (oracle ceiling also collapses). |
| HF | `encoder_structure_aware_sharpness_v1` (3 seeds, FULL, 2026-07-10) | ΔM5 = -0.0175 (all 3 seeds negative); baseline A held-out M5 0.68 = graph-inductive ceiling | **Structure-aware encoder training does NOT lift held-out inductive generalization**; the walk component HURTS 1-hop AUC. |
| HF | `cortex_task_analog_downstream_v2b/v3/v4` (DEFINITIVE NEGATIVE, arc closed) | H3 gap 0.000, H1 gap -0.333 | Cortex task-analog composition does not help single task even at high noise. |
| HONEST_NEG | `hypernym_heldout_falsifiable` / `partof_heldout_falsifiable` | held-out negative | Held-out hypernym/part-of relational inference falsified. |
| CG(neg) | `substrate_concept_encoder_substrate_content_v1` | encoder r5 0.160 < char-trigram 0.280 | Synthetic-CG concept-encoder mechanism does NOT transfer to real WordNet held-out synonym retrieval. |

---

## F. RELATIONAL PRIMITIVES / BAKE-INS (same-different, agency, object-permanence, comparison)

Histogram (non-PASS): 2 landed (both MM). **Barely probed.**

| Tier | Cell | Key metric | Verdict |
|---|---|---|---|
| MM | `SUBSTRATE_HOLOGRAPHIC_BINDING_SUPPORTS_OBJECT_PERMANENCE_STYLE_OCCLUDED_IDENTITY_RECOVERY` (math atom) | paired recovery ratio, must-fail controls fire | **Object-permanence-style occluded-identity recovery** via holographic binding (structured vs iid, holographic vs localist) = MM. |
| MM | `SUBSTRATE_VSA_UNBIND_COMPARE_ALGEBRA_SUPPORTS_ABSTRACT_FILLER_INVARIANT_2ND_ORDER_RELATIONAL_SAME_DIFFERENCE` (math atom) | unbind-compare algebra | **Same-different / 2nd-order relational (filler-invariant) comparison** via unbind-compare = MM. |

- **AGENCY-detector: NO cell found. UNTESTED.**
- Same-different and object-permanence exist only at MM (single characterization), never lifted to CG or FULL cross-seed.

---

## G. OTHER RELATIONAL (mis-bucketed / adjacent)

Histogram (non-PASS): CG 4 · MM 9 · MB 3 · HF 7.

- CG: `refuse_gate_5_graph_health` (substrate reads its own graph-overload state), `substrate_KG_capacity_sweep` (CG @M10k, cliff @50k), `substrate_refuse_gate_v_rel_extension` (relation-check arm, V_REL 256, 32x lift), `director_kb_bio_trio_ingest` (tooling — 222k bio triples ingested deterministically).
- **Edge-importance family (9 cells, ALL MM/MB/HONEST_NEG):** `edge_importance_bound_pair_consolidation` v1/v2, `retrieval_trace_x_ultrametric_coreness` v3/v3p1, `v5_CFU`, `stratified_replay_diagnostic`. Structural orthogonality holds (fairness gate passes, cor≈0.06) but sel-unretr signal sits at +0.08 ceiling, below the 0.85 PASS floor. "Can the substrate rank which edges matter from the retrieval trace alone?" = proven-bounded at +0.083. Multiple HF_BACKLOG infra variants.
- MM: `schema_exemplar_bayes_capacity_stress` (Bayes>NN lift replicated, majority MB @capacity edge).

---

## PROVEN (certified working relational sub-capabilities)

1. **Binding operator (bind/unbind) is CG** — permutation/HRR bind, unbind (0.995), cross-modal bind to 2/3/4/5 modalities, theta-gamma sequence bind, task-vector HRR. The compositional PRIMITIVE is solid. [A]
2. **Analogy completion (a:b::c:?) via bind/unbind/cleanup is CG** — r1 0.8613 on synthetic/math VSA. [E]
3. **Multi-hop traversal over a KNOWN graph is CG to ~50 hops** — via PARTITION-ORACLE routing, per-step ~0.985, d*(0.50)≈50-55 hops. Held-out KNOWN_T reach@2 ≈ 0.44-0.46. [B]
4. **Regenerative hard-snap cleanup beats analog soft-carry (CG)** — the fidelity mechanism that lets chains survive depth above the crosstalk threshold. [B]
5. **Goal-conditioning "Barrier-1" is CG via partition oracle**, and **partition ROUTING capacity is CG to 100k** (bounded 1M). [D]
6. **Two-tier WM/LTM composition primitive (cortex_context_retention) is CG** (M1p5). [B]
7. Cross-modal/ToM/coarse-grain abstraction primitives CG/MM. [A/B]

---

## THE WALLS (failed sub-capabilities + ROOT CAUSE per the VET)

1. **Held-out INDUCTIVE inference fails — THE wall (07-10, 3 FULL HF cells).** Learned SR codes route no better than random codes on held-out edges (reach@2 0.115 vs 0.104, Δ0.011 < 0.05). Root cause per VET: this is *memorized search, not reasoning* — the substrate fills holes over a memoryless baseline (real traversal of KNOWN edges) but cannot infer edges it never ingested. **Global additive TransE (h+r) scored ZERO / vacuous;** only a content-conditioned bilinear scorer moves modestly off zero (MM). [E]
2. **Richer codes/graph knobs are NOT the lever.** Relation-type richness (flat 0.673, slope 0.002), k-core density (rise -0.062), and structure-aware encoder training (ΔM5 -0.0175) each independently FAIL to move held-out inductive inference, confound-free. Root cause: they are all "same-graph knobs"; **the lever is INGEST more KNOWLEDGE, not richer structure over the same graph.** [C/E]
3. **Substrate-NATIVE multi-hop composition fails at depth ≥15.** Chain-grade primitives cannot compose a multi-hop chain without an oracle: derived hints at chance, 3-/4-primitive brain-faithful compositions collapse (arm 0.01, adapters dead). Root cause: signal-shape / operating-regime mismatch between a primitive's validated regime and the downstream chained regime (META_RULE_AP/AQ); needs an explicit per-step state-tracker that re-fires upstream primitives. **The proven depth-50 result RIDES ON the oracle router.** [B]
4. **Learned / typed / substrate-native ROUTING fails.** Closed-form router 0.000, learned routers stuck at 0.66 centroid floor, typed routing HURTS (0.44 vs 0.998), routing-geometry crashes at ingest scale. Root cause: router SNR ~√(N/M) degrades under load; only the oracle escapes it. [D]
5. **Systematic generalization via involutive HRR is null** (0.0067 = chance); **cleanup-after-bind destroys the composite** (snaps to one codebook entry); **binding-op choice and cleanup-per-slot don't change capacity** (invariant K-cliffs). Root cause: substrate algebra bounds — superposition capacity is set by N and load α, not by the bind op. [A]
6. **Role-filler compositional generalization is by-construction, not earned** — the label-driven encoder pre-fuses the category basis; role binding adds neutral lift (MM, not CG). [A]

---

## UNTESTED / GAPS (not probed, or only at smoke/MM)

- **Agency detector — NOT probed at all.** [F]
- **Same-different and object-permanence — only MM** (single synthetic characterization each), never FULL cross-seed / CG. No comparison-primitive ladder. [F]
- **Relation VOCABULARY isolation — no cert cell** proves open-vocab / richer relation TYPES raise capability (the one richness cell was negative on inductive lift; encoding *capacity* only exercised via ingest tooling). [C]
- **Substrate-native (oracle-free) routing that WORKS — open.** Every landed attempt failed; no positive result exists. [B/D]
- **TransE / additive codes with proper parameterization — only tested as GLOBAL additive (scored zero).** The bilinear-scorer MM is under-parameterized; a properly-trained additive/geometric inductive code has not landed a positive. [E]
- **Cross-modal / analogy at CG is SYNTHETIC only** — real-corpus transfer of the concept-encoder analogy mechanism is a CG *negative* (loses to char-trigram). No real-world relational analogy CG. [E]
- **Multi-hop over INGESTED real KG (vs synthetic chains)** — HotpotQA / ConceptNet transfer all HF/MB; the CG depth results use synthetic partition-oracle chains. [B]

---

## CONVERGENCE (the through-line)

Reading the whole record, the relational story splits cleanly along one seam: **memorized structure vs. inductive inference.** Everything that operates over structure the substrate has ALREADY ingested is proven — binding/unbinding is CG, analogy completion is CG on synthetic algebra, and multi-hop traversal of a KNOWN graph is CG out to ~50 hops with a regenerative-cleanup fidelity mechanism that beats soft-carry. The composition primitive is real and deep. But every capability that requires going BEYOND the ingested graph breaks in the same place, and 2026-07-09/10 pinned it three times over with confound-free FULL cells: learned codes route no better than random codes on held-out edges (Δ0.011), and richness, density, and structure-aware training each fail to move that number. The consistent VET reading is that the substrate does *memorized search*, not *reasoning* — it fills holes over a memoryless baseline but does not infer unseen edges, and global additive TransE codes are outright vacuous. The second, orthogonal wall is that the proven depth results all ride on an ORACLE router: every learned, typed, or substrate-native router collapses to the naive-centroid floor or crashes at scale, because router SNR ~√(N/M) degrades under load. So the program should build on binding + oracle-routed traversal + regenerative cleanup as the solid floor, and treat the two live frontiers as (a) making inductive inference real, where the evidence says the lever is INGESTING more knowledge (grounding/active-referent) rather than richer codes over the same graph, and (b) an oracle-free router that survives load — with same-different, object-permanence (both only MM) and agency (untested) as the unbuilt relational-primitive bake-ins.
