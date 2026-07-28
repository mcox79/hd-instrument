# SURVEY: reader-toward-chain-grade prior work + genuine unbuilt gaps (2026-07-20)

Read-only archaeology (no cells dispatched). Purpose: give the Director an authoritative component map + a
dedup-VERIFIED gap list (or exhaustion confirmation) so autonomous dispatch stops duplicating already-built cells.
Two duplicates were burned this session (compgen head-to-head vs pre-existing `56a0ac0dd`/atom
`math::MM_compgen_binding_vs_flat_LEARNED_PERCEPTUAL_frontend_v1`; an ingestion-valve vs the pre-existing
`exp_ingest_gate_*` family of ~7 cells) because the KB dedup-check is blind to local-unsynced atoms and to
older cells indexed under a different concept name. This note is a filesystem-grounded cross-check, not another
KB query.

Sources used: `experiments/*.py` (5,138 files, globbed/grepped by concept, this survey), `data/substrate_index/math/atoms.jsonl`
(29,393 atoms; tail 2026-07-18/19/20 read directly), `notes/prior_art_scour_synthesis_focus_chaingrade_2026-07-18.md`
(the NVSA 3-stage plan), `notes/SYNTHESIS_missing_elements_prior_art_adopt_adapt_buildfresh_2026-07-20.md`,
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md` (the 2026-07-20 CURRENT STATE snapshot, authoritative).

## COMPONENT-BY-COMPONENT MAP (NVSA/reader plan vs built)

| Component | Status | Key cells (filesystem-verified) | VET verdict |
|---|---|---|---|
| **Front-end / atom-recognition** (learned, role-blind) | **BUILT** | `exp_compgen_binding_vs_flat_learned_frontend_v1.py`, `exp_novel_atom_generalization_codebook_binding_v1.py`, `exp_novel_atom_real_codebook_capacity_curve_v1.py`, `exp_novel_atom_real_codebook_generalization_v1.py` | MEASURED_MECHANISM (29379-29382): learned front-end + fixed FHRR bind composes; beats naive-NN only at high capacity (bounded linear-recovery) |
| **Binding / composition (fixed VSA algebra)** | **BUILT, mature** | whole `exp_grounding_bind*`, `exp_single_edge_grounding_hd_binding_verbnet_v1.py`, `exp_derived_filler_typing_single_edge_grounding_v1.py`, `exp_stage3_hrr_involutive_systematic_generalization_v1.py` | binding is lossless/tautologically-systematic; storage+recall+class-keyed generalization proven (29390, 29391) |
| **Role-representation (structural address code)** | **BUILT + CLOSED** | `exp_role_filler_factorization_*` (7 variants incl. `_reader_coupled_cg_v1`, `_realcontent_cg_v1`, `_learning_curve_cg_v1`, `_conceptnet_cg_v1`, `_compgen_v1`) | atom 29369 KILL/MEASURED_MECHANISM: deriving the address code is inert-or-harmful; **stipulated-random role codes are RIGHT** (brain: DG pattern-separation). Settled, do not revisit. |
| **Learned content codebook** | **BUILT, CHAIN_GRADE** | `exp_learned_codebook_generalization_gate_v1.py` + ~45 other `*codebook*` cells | atom 29368 CHAIN_GRADE: RI/PPMI+SVD codes generalize held-out (AUC 0.927), frequency-confound ruled out |
| **AMR / PropBank / DRS role-graph** | Adopted as a **representation reference**, not itself a testable cell | none (`grep amr|propbank|_drs_` in experiments/ = 0 hits) | N/A — this is a literature-credited design choice (already reflected in the FHRR role/filler + verb-class scheme used by `exp_single_edge_grounding_*` / `exp_derived_filler_typing_*`), not a missing component |
| **Comprehension loop (Kintsch CI / compress-and-carry)** | **BUILT + walled** | `exp_compress_and_carry_comprehension_loop_ccl_v1.py`, `exp_contrastive_predictive_reader_loop_cpcl_v1.py`, `_cpcl_v2.py`, `exp_learned_argstruct_parser_lccp_independent_gold_v1.py` (LCCP), `exp_read_grow_*`, `exp_frame_order_recovery_hard_comprehension_v1/v2.py` | CPCL v1/v2: HARD_FAIL honest null (entity-recurrence is a bad self-sup target, corr~0); LCCP branch is the live CG-producing lineage (see reader-axis row below) |
| **Coherence-gate** | **BUILT, multiple variants, mixed verdicts** | `exp_coherence_gate_extraction_correctness_independent_gold_v1.py`, `exp_coherence_filter_foundation_growth_safety_precheck_v1.py`, `exp_settling_parse_selector_richness_v1.py`, `exp_settling_fix_learned_recurrent_v1.py`, `exp_scene_coherence_verifier_contrastive_scv_v1.py` | settling-as-coherence-readout REFUTED twice (29385 HARD_FAIL, 29387 HARD_FAIL_3 after a genuine graded-settling fix); static thematic-fit cosine (~0.58-0.63) is the one surviving coherence signal |
| **Reader axis (LCCP/deixis/coref/argstruct, McGuffey 3rd reader)** | **BUILT, several CHAIN_GRADE wins** | `exp_read_deixis_participant_tracking_third_reader_v1.py`, `exp_read_argstruct_goal_role_third_reader_v1.py`, `exp_np_head_finder_grounding_gate_break050_v1.py`, `exp_arg_adjunct_role_eligibility_categorial_break050_v1.py` | atoms 29326-29347ish: multiple CHAIN_GRADE breaks (NP-head-finder fixes candidate-gen; quotative speaker-attribution) + several HARD_FAIL ceiling findings (subcategorization via selectional coherence = genuine ceiling; directional-PP+subcat failed must-fail control). Reader bounded ~0.557 overall (per MEMORY). |
| **Compgen target (COGS/SCAN-style held-out combinations)** | **BUILT + CLOSED (free-algebra tautology)** | `exp_compgen_binding_vs_flat_learned_frontend_v1.py` (commit `56a0ac0dd`, atom `math::MM_compgen_binding_vs_flat_LEARNED_PERCEPTUAL_frontend_v1`), `exp_schema_relation_richer_content_vscan_v1.py`, `exp_subs_naive_scan_cpu_cost_v1.py`, `exp_role_filler_factorization_compgen_v1.py` | MEASURED_MECHANISM, NOT chain-grade: novel-COMBINATIONS win 100% by fixed-algebra math (0% learned) — a real capability but not a *learned* CG; novel-ATOMS bounded to high-capacity linear recovery (29379-82). Confirmed 3x this session (session-pattern note explicitly flags this as the 3rd confirm). |
| **Weak/grounded supervision (Artzi-Zettlemoyer style)** | **BUILT, walled negative** | `exp_affectedness_weak_sup_revival_loop_v1.py`, `exp_affectedness_change_of_state_patient_selection_design_gate_v1.py`, `exp_affectedness_typelevel_lookup_verbnet_selrestrs_v1.py` | HARD_FAIL: no self-supervised text signal tracks patient-selection (6 failed variants, 29371); VerbNet SELRESTRS coverage-blocked (0.20 instance / 0.235 verb, well under threshold) |
| **NVSA / NS-CL 3-stage explicit template** | Adopted as **design pattern**, not a literal ported cell | none (`grep nvsa|ns_cl` = 0 hits); the pattern IS instantiated piecewise as front-end+binding+glass-box-reasoning across the rows above | N/A — correctly treated as an architecture template, not a single buildable unit |
| **Self-monitoring layer (metacognition/reliability/common-mode)** | **BUILT, 5 CHAIN_GRADE** | `exp_metacog_abstain_conformal_transfer_v1.py`, `exp_metacog_abstain_readout_signal_thresholding_v1.py`, `exp_attention_salience_reliability_gate_independent_channel_v1.py`, `exp_attention_salience_common_mode_detector_v1.py`, `exp_attention_salience_reliability_gate_correlated_error_v1.py` | atoms 29367/29370 (metacog+transfer CG), 29376 (independent-channel reliability CG, first DERIVATION win), 29378 (common-mode CG); scope-bounded to independent-random errors (29377) |
| **Active-learning / lookup-and-revise loop** | **BUILT, MM (not yet CG)** | `exp_active_learning_loop_gap_detect_lookup_revise_v1.py`, `_v2.py` | v1 construction-determined (48/48 lookups hand the answer); v2 fixed 3 crutches, HARD_PASS headline VET-corrected to MEASURED_MECHANISM (win concentrated on the round-trip subset, structurally forced) |
| **Neuromodulatory gating (ACh/NE/volatility)** | **BUILT** (pre-dates this arc) | `exp_substrate_ACh_query_conditional_read_gain_LM_v1.py`, `exp_substrate_dual_trace_sequential_neuromod_LM_v1.py`, `exp_substrate_neuromodulator_3axis_gated_compose_LM_v1.py` | not yet wired to the reader/self-monitoring layer specifically, but the mechanism cells exist |
| **Consolidation / replay (CLS-theory)** | **BUILT, extremely extensively** (~110 cells) | `exp_cls_*`, `exp_hippocampal_engram_consolidation_v1/2/3`, `exp_confidence_gated_codebook_consolidation_v1.py` (=29383) + bootstrap-SNR sibling (=29384) | mixed verdicts across a mature sub-literature; not reader-specific but the mechanism is proven |
| **Hierarchical multi-timescale prediction** (HTM/TRW/MTRNN) | **GENUINELY UNBUILT** (verified: 0 filesystem hits) | none | N/A — see gap list below |

## DEDUP-VERIFIED SEARCHES THAT RETURNED ZERO (cited so the Director can trust the negative)
- `ls experiments | grep -iE "amr|propbank|_drs_|semlink"` → 0 matches
- `ls experiments | grep -iE "nvsa|ns_cl|neurosym"` → 0 matches
- `ls experiments | grep -iE "hierarch.*timescale|_htm_|temporal_pooler|multi_timescale|mtrnn"` → 0 matches
- `ls experiments | grep -iE "three_stage|3stage|3_stage"` → 0 matches
- (all other components above returned 5-100+ matches — genuinely built, not gaps)

## RANKED GENUINE-GAP CANDIDATES

1. **Hierarchical multi-timescale prediction (HTM temporal pooler / Hasson TRW / MTRNN)** — the only component
   with a clean zero-hit filesystem search. **BUT**: per `notes/SYNTHESIS_missing_elements_prior_art_adopt_adapt_buildfresh_2026-07-20.md`
   this is explicitly **base-loop-gated** ("after loop" — nothing to wire until the coherence loop exists), and the
   base loop itself is not yet closed (CPCL HARD_FAIL twice; entity-recurrence is a bad target; revival is
   grounded/weak-sup design-gate work, still in flight). Building this now would violate the design-gate
   discipline (a dependency not yet ready) and would likely be an ANALYTICALLY-CAN'T-FAIL cell (nothing to
   predict across timescales without a working base loop feeding it). **Recommendation: hold, not dispatch — it
   is real-unbuilt but not *ready*.**
2. No other component in the stated NVSA/reader/compgen plan survives dedup-verification as both (a) genuinely
   absent from `experiments/` and (b) currently dispatch-ready (dependencies satisfied, can-fail testable). Every
   other candidate the Director might reach for (ingestion valve, compgen head-to-head, weak-supervision signal,
   coherence-gate variant, settling-as-readout, codebook variant, active-learning loop) is **already built and
   VET'd**, several multiple times over (settling alone has 2 full cells + a revival; compgen has 4+ cells;
   ingestion has 7+ `exp_ingest_gate_*` cells alone).

If a future candidate is proposed, the minimum bar before dispatch: (1) `ls experiments | grep -iE "<concept>"`
must return zero, (2) check `data/substrate_index/math/atoms.jsonl` tail (`tail -100` + parse `name`/`tier` fields)
for a same-concept atom regardless of `needs_orchestrator_store_sync` status, (3) confirm the dependency chain
(what must already be TRUE for this cell to be non-trivially able to fail) is actually satisfied.

## HONEST VERDICT

The reader-toward-chain-grade frontier, as scoped by the 2026-07-18 NVSA-port plan, is **comprehensively explored,
not exhausted-by-accident but exhausted-by-actual-work**: every planned component (front-end, binding, role-rep,
comprehension loop, coherence-gate, compgen target, weak-supervision, and the self-monitoring layer that grew out
of the arc) has one or more filesystem-verified cells with a landed, VET-confirmed verdict — 5 CHAIN_GRADE wins
(metacognition+transfer, learned codebook, independent-channel reliability gate, common-mode detector), 1 clean
KILL (structure-derivation), and roughly a dozen MEASURED_MECHANISM/HARD_FAIL results that collectively wall off
compgen-via-binding (free-algebra tautology, confirmed 3x), patient-selection/affectedness (grounding-bound, 5+
confirmations from text-derivation, curated-signal, VerbNet-coverage, settling-readout, and density angles), and
the entity-recurrence coherence target. The one filesystem-clean unbuilt component (hierarchical multi-timescale
prediction) is real but explicitly sequence-gated behind a base loop that itself hasn't closed — so it is not a
ready next cell either. The honest conclusion matches the Director's own 2026-07-20 snapshot: **the next move in
this direction is a USER-directed bigger bet (fund the base-loop revival with grounded/structured data, or commit
to the expensive grounding/perception investment, or formally close this frontier and redirect), not another
autonomous cell dispatch.** Any further "gap" the Director finds without a fresh filesystem grep + atoms.jsonl-tail
check should be treated as suspect.
