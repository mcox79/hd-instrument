"""
A5-gated atomization: VET'd foundation-builder / multi-source-arena / claim-validity batch (2026-07-16).

USER-AUTHORIZED (bank the day's VET'd batch to the LOCAL canonical Store; NO origin push, NO remote-persist).
All 15 dispositions INDEPENDENTLY VET'd off-disk (.venv; Fix #28: recompute discriminators from metrics.json
contract/gate/per_seed maps, NOT verdict_msg). Cross-arc overlap check (USER-locked): substrate_query top hits
are lexical wordnet/concept only (Orthogonality 0.267, Frequency 0.240) -- NO prior CERTIFIED experiment atom at
cosine>0.30; the claim-validity + arena arc is a genuine new/targeted-extension line. No concurrent atom-writer.

Tiers (my OWN off-disk re-VET, NOT rubber-stamping cell self-verdict or Director framing):
  CG  = CHAIN_GRADE construction-proof (recompute confirms, controls/nulls fire; synthetic scope loud)
  MM  = MEASURED_MECHANISM (real but narrower/weaker-than-framing bound; or a measured TIE)
  HF  = HARD_FAIL (honest negative; attribution structural vs test-design)

 1 pairwise_schemafit          -> MM  (MIDDLE: SR>freq +0.093 but widening over RA +0.021<0.03)
 2 degree_orth_schemafit S     -> MM  (MIDDLE: pop-neutral-by-constr win, but point margin 0.096<0.10 gate)
 3 degree_orth_schemafit M     -> MM  (MIDDLE: margin GENERALIZES larger; pop-neutrality does NOT -> per-dataset)
 4 nativelang_svo_vsa          -> CG  (construction: glass-box VSA SVO parse/gen duality; synthetic role-filler)
 5 arena_v1                    -> MM  (arena VALID non-circular; multi-signal gate MARGINAL, loses within-cell)
 6 curriculum_order            -> CG  (construction: ingest ORDER matters, curriculum rescues; null on flat)
 7 provisional_hold            -> CG  (construction: hold recovers arbitrary order at bounded cost)
 8 consolidation_regimes       -> CG  (construction: hold REGIME-APPROPRIATE; wins capacity+order, ties interference)
 9 snr_ramp_schedule           -> HF  (SNR-trigger REFUTED; schedule concept validated by time-clock)
10 combination_menu            -> MM  (TIE: brain-faithful ties learned logistic gap 0.006<TIE_EPS; NOT a win)
11 conjunction_menu            -> CG  (form-matched construction: mult wins in certified-conjunctive arena, marginal)
12 continual_retention         -> HF  (route LOSES to consolidate-everything at Nmax; crossover EXTRAPOLATED)
13 phase_boundary              -> MM  (route-vs-keep advantage REGIME-GATED; N-axis alone never robustly crosses)
14 temporal_hold_recover       -> HF  (TIES arrival; NO accruing temporal info -- unfaithful world / test-design)
15 temporal_accrual_fair       -> CG  (fair world: hold beats arrival z=25; but TIES keep-everything, structure adds 0)

A5: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta + tail-id match.
Single process (save_atoms NOT concurrency-safe): 15 atoms to math/atoms.jsonl, then 15 rows to meta/cert_ledger.jsonl.
LOCAL ONLY: every atom carries store_head_at_write=unsynced_needs_orchestrator + needs_orchestrator_store_sync=True.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"
ATOMIZED_BY = "skunkworks_landed_vet_foundation_builder_arena_claimvalidity_batch_2026-07-16"
ATOMIZED_DATE = "2026-07-16"
XARC = "substrate_query lexical-only (Orthogonality 0.267, Frequency 0.240); no prior cert experiment atom >0.30; novel/targeted-extension."

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

atoms = []
ledgers = []


def mk(id, tier, anchor, claim, recompute, scope, metrics, composes, kind, cert_status, cert_class,
       verdict, decision, framing, net, hf_attr=None):
    atom = {
        "id": id, "name": claim, "corpus": "math", "tier": tier, "kind": kind,
        "cert_status": cert_status, "cert_class": cert_class,
        "description": (claim + "\n\nRECOMPUTE (off-disk .venv, Fix #28): " + recompute
                        + "\n\nHONEST SCOPE: " + scope),
        "aliases": [], "ts_iso": _iso, "ts": _ts,
        "metadata": {
            "provenance_quality": "recompute_off_disk_contract_gate_per_seed_not_verdict_msg",
            "anchor": anchor, "cell_commit": "UNKNOWN_local_capture_needed",
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_%s/metrics.json" % anchor,
            "verified_off_data": recompute, "honest_scope": scope, "metrics": metrics,
            "composes_with": composes, "cross_arc_overlap_check": XARC,
            "cites": ["Fix_28_verify_off_data_not_verdict_msg",
                      "symmetric_anti_negativity_verify_both_directions_USER",
                      "feedback_construction_proof_is_not_a_capability_win",
                      "feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_USER"],
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE, "needs_orchestrator_store_sync": True,
        },
    }
    if hf_attr:
        atom["metadata"]["hf_attribution"] = hf_attr
    led = {
        "op": "cert_ruling", "corpus": "math", "tier": tier, "cert_status": cert_status,
        "anchor": anchor, "cell_commit": "UNKNOWN_local_capture_needed",
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY, "verdict": verdict,
        "cert_increment_delta": 1, "decision": decision,
        "framing_correction_vs_director": framing, "cross_arc_overlap_check": XARC,
        "net_cert_delta": net, "needs_orchestrator_store_sync": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": id,
    }
    if hf_attr:
        led["hf_attribution"] = hf_attr
    atoms.append(atom)
    ledgers.append(led)


# 1 -------------------------------------------------------------------------------------------------
mk("math::MM_MIDDLE_claimvalidity_pairwise_SR_PPR_schemafit_beats_degree_matched_freq_margin_0p093_but_widening_over_RA_0p021_below_0p03_gate_codexS_hardneg_2026-07-16",
   "MEASURED_MECHANISM", "codex_claimvalidity_pairwise_schemafit",
   "MATH MM (MIDDLE): on CoDEx-S human-verified hard negatives, a pairwise SR/PPR resolvent schema-fit signal beats a degree-matched frequency baseline (AUROC 0.605 vs cert-at-chance 0.511, margin-over-freq +0.093) with the frequency certificate firing near chance (0.512) under the relation_nn_degree_matched control -- BUT the widening of pairwise SR over the simpler RA baseline is only +0.021, below the pre-registered +0.03 hard-pass gate, so MIDDLE.",
   "verdict=MIDDLE; margin_SR_pairwise_vs_freq=0.0934; widening_SR_over_RA=0.0209 (<0.03 gate); cert_fires(relation_nn_degree_matched)=True; freq_single_best 0.5125 in band [0.45,0.55].",
   "SYNTHETIC-FREE real KG (CoDEx-S) but the win is NARROW: SR-over-RA widening under the pre-reg gate; the bankable claim is pairwise schema-fit>degree-matched-freq, NOT a blanket structure-beats-frequency.",
   {"sr_ppr_auroc": 0.6046, "freq_cert_auroc": 0.5125, "margin_sr_vs_freq": 0.0934, "widening_sr_over_ra": 0.0209, "gate": 0.03},
   ["degree-orthogonal pairwise schema-fit (this batch, the promoted a-priori signal)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_middle_pairwise_schemafit_beats_degree_matched_freq_narrow",
   "claim_validity_pairwise_sr_ppr_schemafit_vs_degree_matched_frequency_codexS_hardneg_middle",
   "MIDDLE_pairwise_sr_beats_freq_0p093_but_widening_over_RA_0p021_below_0p03_gate",
   "MM MIDDLE. Pairwise SR/PPR schema-fit beats degree-matched freq (+0.093) but widening over RA (+0.021) is below the 0.03 gate -> MIDDLE, not a clean win.",
   "Confirms Director MIDDLE. I bank the NARROW claim only (pairwise>degree-matched-freq); the degree-orthogonal cell is the airtight-popularity-neutral version, this v1 is the raw-frontier predecessor.",
   "+1 MM (narrow: pairwise schema-fit beats degree-matched frequency on hard negatives; below the widening gate).")

# 2 -------------------------------------------------------------------------------------------------
mk("math::MM_MIDDLE_claimvalidity_degree_orthogonal_pairwise_schemafit_beats_degree_matched_freq_codexS_min_margin_0p096_max_0p119_popneutral_by_construction_labelfree_below_0p10_gate_2026-07-16",
   "MEASURED_MECHANISM", "codex_claimvalidity_degree_orthogonal_schemafit",
   "MATH MM (MIDDLE, the real narrow win): degree-orthogonalized pairwise SR/PPR schema-fit (signal fixed a-priori, LABEL-FREE, projection fit on VAL applied to TEST) beats a degree-matched frequency baseline on CoDEx-S hard negatives -- min point margin-over-freq 0.096, max 0.119 across the prereg gamma {0.5,0.6,0.7} x caliper {0.15,0.20,0.25} grid; POPULARITY-NEUTRAL BY CONSTRUCTION (held-out degree_explained ~0.0) and label-free verified (residual bit-identical under label shuffle). MIDDLE because the min point margin 0.096 does not clear the ambitious +0.10 gate at ALL prereg gamma x caliper and the bootstrap p05 floor is not robust across every config.",
   "verdict=MIDDLE; min_point_margin(prereg gxc)=0.0956 max=0.1191; point_pass_ge_0.10_all=False; pop_neutral_by_construction=True (deg_explained 0.0); label_free_verified=True; beats_ra=True; cert fires all calipers.",
   "Real KG (CoDEx-S). The airtight part is POPULARITY-NEUTRALITY BY CONSTRUCTION -- but this neutrality is PER-DATASET (see CoDEx-M atom where it fails). Bank the narrow claim: degree-orthogonal structure beats degree-matched frequency on NOVEL/hard-negative claims, popularity-neutral on THIS dataset; brain's edge is novel claims where frequency is blind.",
   {"sr_orth_auroc_verdict_gamma": 0.6264, "min_point_margin": 0.0956, "max_point_margin": 0.1191, "ra_raw_frontier": 0.0725, "deg_explained_heldout": 0.0, "gate": 0.10},
   ["pairwise_schemafit v1 (raw-frontier predecessor)", "codexM generalization (this batch, where pop-neutrality FAILS)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_middle_degree_orthogonal_schemafit_popneutral_by_construction_codexS_below_gate",
   "degree_orthogonal_pairwise_schemafit_beats_degree_matched_frequency_popularity_neutral_by_construction_codexS_hardneg",
   "MIDDLE_min_point_margin_0p096_below_0p10_gate_but_popneutral_by_construction_labelfree_win_real",
   "MM MIDDLE. Degree-orthogonal pairwise schema-fit beats degree-matched freq (min margin 0.096, max 0.119), popularity-neutral BY CONSTRUCTION (deg_explained 0.0), label-free -- but min margin below the 0.10 point gate -> MIDDLE.",
   "Confirms Director: this is the real, VET'd, MODEST win. I bank the NARROW popularity-neutral claim and flag that neutrality is PER-DATASET (the CoDEx-M atom shows it does not generalize).",
   "+1 MM (the real narrow win: degree-orthogonal structure beats degree-matched frequency on hard negatives, popularity-neutral by construction on CoDEx-S).")

# 3 -------------------------------------------------------------------------------------------------
mk("math::MM_MIDDLE_claimvalidity_degree_orthogonal_schemafit_generalizes_codexM_margin_LARGER_min_0p132_clears_gate_BUT_popneutrality_does_NOT_generalize_deg_explained_0p127_above_0p10_per_dataset_2026-07-16",
   "MEASURED_MECHANISM", "codexM_claimvalidity_degree_orthogonal_schemafit",
   "MATH MM (MIDDLE, generalization with a load-bearing caveat): the degree-orthogonal pairwise SR/PPR schema-fit result GENERALIZES to CoDEx-M in MARGIN -- min point margin-over-freq 0.1315 (clears the 0.10 gate; larger than CoDEx-S), max 0.209, bootstrap p05 0.117, label-free verified -- BUT the airtight POPULARITY-NEUTRALITY does NOT generalize: held-out degree_explained fraction is 0.127, ABOVE the 0.10 threshold, so on CoDEx-M part of the win is degree-attributable and pop-neutral-by-construction is FALSE. Verdict MIDDLE for that reason.",
   "verdict=MIDDLE; min_point_margin=0.1315 (point_pass_ge_0.10_all=True, LARGER than CoDEx-S); max=0.2095; pop_neutral_by_construction=False; max_heldout_degree_explained=0.1266 (>0.10); label_free_verified=True.",
   "Real KG (CoDEx-M, 17050 ent / 51 rel). The MARGIN generalizes and is bigger, but the airtight popularity-neutrality is PER-DATASET and FAILS here (12.7% degree-explained). Honest generalization statement: the schema-fit margin over degree-matched frequency generalizes; the airtight popularity-neutrality does NOT. Do NOT claim a blanket popularity-neutral structure-beats-frequency across datasets.",
   {"min_point_margin": 0.1315, "max_point_margin": 0.2095, "ra_raw_frontier": 0.1104, "boot_p05": 0.1169, "deg_explained_heldout": 0.1266, "gate": 0.10, "neutrality_threshold": 0.10},
   ["codexS degree_orthogonal (this batch, where pop-neutrality holds by construction)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_middle_degree_orthogonal_schemafit_margin_generalizes_codexM_popneutrality_does_not_per_dataset",
   "degree_orthogonal_schemafit_margin_generalizes_codexM_but_popularity_neutrality_is_per_dataset_fails",
   "MIDDLE_margin_generalizes_larger_min_0p132_but_deg_explained_0p127_above_0p10_popneutrality_per_dataset",
   "MM MIDDLE. Margin generalizes to CoDEx-M (min 0.132, larger than S, clears gate) but popularity-neutrality does NOT (deg_explained 0.127>0.10) -> per-dataset. MIDDLE.",
   "Confirms Director's guardrail EXACTLY: popularity-neutrality is per-dataset. My recompute shows the margin generalizes (even larger) while the airtight neutrality fails on CoDEx-M -- I bank the honest split, not a blanket generalization.",
   "+1 MM (generalization: schema-fit margin generalizes to CoDEx-M and grows; airtight popularity-neutrality is per-dataset and fails here).")

# 4 -------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_glassbox_VSA_SVO_parse_generate_duality_heldout_compositional_gen_parse_1p000_gen_1p000_gap_0_nulls_collapse_mem_0_flat_0p121_scram_0p010_32configs_synthetic_rolefiller_not_english_2026-07-16",
   "CHAIN_GRADE", "nativelang_svo_vsa_probe_v1",
   "MATH CHAIN_GRADE (construction-proof): a glass-box VSA subject-verb-object probe binds fillers to roles so that ONE bidirectional role-filler mapping serves BOTH parse and generate (duality); on a held-out compositional split (filler combinations never seen) parse_acc=1.000 and gen_acc=1.000 with generalization_gap=+0.000, and across 32 (N,V,n_slots) configs NONE drop below 0.90. Nulls collapse as required: a memorization model gets 0.000 on held-out (must-fail fires), flat bag-of-fillers 0.121, scrambled-role 0.010 -- so the mechanism is compositional role-binding, not lookup.",
   "verdict=HARD_PASS; positive regime parse_heldout=1.0 gen_heldout=1.0 gap=0.0; mem_heldout=0.0 (must-fail collapses); flat_heldout=0.121; scram_heldout=0.010; configs_below_0.90 = 0 of 32.",
   "SYNTHETIC role-filler binding: the 'vocabulary' V is random HD atoms, NOT English words; this is a CONSTRUCTION-PROOF of the parse/generate duality and compositional generalization of role-binding, NOT an English-language-understanding capability (USER-lock: never narrate synthetic HD bundles as language capability). Could-fail was real (mem/flat/scram nulls all had to collapse and did).",
   {"parse_heldout": 1.0, "gen_heldout": 1.0, "gap": 0.0, "mem_null": 0.0, "flat_null": 0.121, "scram_null": 0.010, "n_configs": 32, "configs_below_0.90": 0},
   ["reasoning architecture = additive_map shared-code compositional-readout (role-binding lineage)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_glassbox_vsa_svo_parse_generate_duality_heldout_compositional_generalization_synthetic_rolefiller",
   "glassbox_vsa_svo_parse_generate_role_filler_binding_duality_heldout_compositional_generalization_synthetic_construction",
   "HARD_PASS_glassbox_vsa_svo_parse_1p000_gen_1p000_gap_0_nulls_collapse_32_configs_no_ceiling_drop",
   "CHAIN_GRADE construction. Glass-box VSA SVO parse+generate via ONE bidirectional role-filler map, held-out compositional gen 1.0/1.0 gap 0, all nulls collapse (mem 0, flat 0.121, scram 0.010), 0/32 configs below 0.90.",
   "Confirms Director HARD_PASS but I TIGHTEN scope to CONSTRUCTION-PROOF of role-filler binding duality on SYNTHETIC atoms -- explicitly NOT an English-language capability (USER-lock). The load-bearing content is the parse/generate duality + compositional-generalization holdout.",
   "+1 CHAIN_GRADE (construction: glass-box VSA SVO parse/generate duality with held-out compositional generalization; synthetic role-filler, not language).")

# 5 -------------------------------------------------------------------------------------------------
mk("math::MM_multisource_arena_VALID_noncircular_4signals_decorrelate_maxr_0p199_copy4x_cMI_4of4_but_multisignal_gate_MARGINAL_loses_to_best_single_recurrence_within_cell_2026-07-16",
   "MEASURED_MECHANISM", "multisource_arena_v1",
   "MATH MM (foundation-builder core; validity YES, capability MARGINAL): the multi-source arena is CERTIFIED NON-CIRCULAR and structurally valid -- the 4 ingest signals (unexpectedness, schema_fit, recurrence, importance) decorrelate (max pairwise |r|=0.199), copying is detected and separated (copy ratio 4.0x, worst p<=0.0002), and all 4 signals are conditionally informative (min informative 4/4); self-tests pass. BUT the multi-signal GATE is MARGINAL: within-cell the multi-signal integration LOSES to the best single signal (recurrence) -- route 0.593 and weighted_sum 0.617 both below best_single 0.645 (route rel-err-reduction -14.8%, wsum -8.0%); multi-signal only helps in the marginal/aggregate setting (wsum 0.866 vs single 0.813).",
   "verdict=MIDDLE; ARENA_VALID max|r|=0.199 copy_ratio=4.0 cMI_informative=4/4; within-cell route 0.593 wsum 0.617 best_single 0.645 -> multisignal_beats_single_within_cell=False; marginal wsum 0.866 vs single 0.813.",
   "SYNTHETIC arena. Bank the VALIDITY construction (the foundation-builder arena is non-circular and its 4 signals genuinely decorrelate) -- this is the load-bearing enabler. Do NOT bank a multi-signal-beats-single capability win: within-cell the integration LOSES to best-single recurrence; the aggregate gain is a marginal-setting artifact.",
   {"max_abs_r": 0.199, "copy_ratio": 4.0, "cMI_informative": 4, "within_route": 0.593, "within_wsum": 0.617, "within_best_single": 0.645, "marginal_wsum": 0.866, "marginal_single": 0.813},
   ["conjunction_menu / combination_menu / temporal / continual siblings (same arena)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_arena_valid_noncircular_4signals_decorrelate_gate_marginal_loses_within_cell",
   "multisource_arena_non_circular_validity_4_signals_decorrelate_multisignal_gate_marginal_not_a_win",
   "MIDDLE_arena_VALID_noncircular_4signals_decorrelate_but_multisignal_gate_MARGINAL_loses_best_single_within_cell",
   "MM. Arena is VALID/non-circular (max|r| 0.199, copy 4x, cMI 4/4); multi-signal gate is MARGINAL and LOSES to best-single recurrence within-cell (only helps in marginal aggregate).",
   "Confirms Director MIDDLE. I sharpen: bank the ARENA-VALIDITY (non-circular, 4 signals decorrelate) as the real content; the multi-signal gate is NOT a capability win (within-cell it loses to best-single).",
   "+1 MM (foundation-builder core: arena certified non-circular, 4 signals decorrelate; multi-signal gate marginal, not a win).")

# 6 -------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_ingest_ORDER_matters_curriculum_rescues_schema_fit_hierarchical_foundation_quality_curr_1p000_vs_reverse_0_arb_0p039_gap_1p0_NULL_on_flat_spread_0_synthetic_2026-07-16",
   "CHAIN_GRADE", "curriculum_order_ingest_schema_fit_v1",
   "MATH CHAIN_GRADE (construction-proof): on HIERARCHICAL data, ingest ORDER matters and a curriculum (foundations-first) order rescues schema-fit -- curriculum foundation_quality 1.000 vs reverse 0.000 vs arbitrary 0.039 at depth 5 (quality_gap curriculum-minus-reverse = 1.0; rescue arbitrary-premature-minus-curriculum-premature = 0.909). The effect is depth-monotone (arbitrary quality 0.32/0.27/0.075/0.039 at depth 2/3/4/5) and is a clean NULL on FLAT (non-hierarchical) data (flat quality spread 0.000 across all orders), so the effect is specific to hierarchical structure, not an artifact.",
   "verdict=HARD_PASS_ORDER_MATTERS; quality_gap(curr-rev)=1.0; rescue=0.909; flat_spread(null)=0.0; depth5 arbitrary_quality=0.039; 8 seeds.",
   "SYNTHETIC hierarchical trees; 'quality' = admit/placement in a designed hierarchy. Construction-proof that ORDER is load-bearing for hierarchical foundation-building and the flat-data null holds; not a real-data capability claim.",
   {"gap_curr_minus_reverse": 1.0, "rescue": 0.909, "flat_spread_null": 0.0, "curr_quality": 1.0, "reverse_quality": 0.0, "arb_quality_depth5": 0.039},
   ["provisional_hold (this batch: recovers arbitrary order at bounded cost)", "consolidation_regimes (order regime)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_ingest_order_matters_curriculum_rescues_schema_fit_null_on_flat",
   "ingest_order_matters_curriculum_rescues_schema_fit_hierarchical_data_null_on_flat_synthetic_construction",
   "HARD_PASS_ingest_order_matters_curriculum_1p000_vs_reverse_0_arbitrary_0p039_null_on_flat_depth_monotone",
   "CHAIN_GRADE construction. Ingest ORDER matters on hierarchical data: curriculum quality 1.0 vs reverse 0 vs arbitrary 0.039, gap 1.0, depth-monotone, clean null on flat (spread 0).",
   "Confirms Director HARD_PASS; I keep scope SYNTHETIC and note the flat-data null is what makes it a clean construction (order-effect is hierarchy-specific, not a universal claim).",
   "+1 CHAIN_GRADE (construction: ingest order matters; curriculum rescues schema-fit on hierarchical data; null on flat).")

# 7 -------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_provisional_hold_recovers_arbitrary_order_ingest_arb_strict_0p039_to_hold_1p000_recovery_1p0_bounded_cost_passes_max_3_le_depth_plus_2_buffer_drains_synthetic_2026-07-16",
   "CHAIN_GRADE", "provisional_hold_bootstrap_arbitrary_order_v1",
   "MATH CHAIN_GRADE (construction-proof): a provisional-hold buffer recovers arbitrary-order ingest at bounded cost -- arbitrary strict-order quality 0.039 rises to 1.000 under provisional-hold (recovery_fraction 1.0, premature_recovered_fraction 1.0), with re-queue passes bounded (max 3 <= depth+2=7), the hold buffer monotone non-increasing and draining to final_hold 0 (no orphans admitted; graceful degradation drains and terminates), and a clean flat-data null (no holding needed). Cost scales but stays bounded (retry ~340 at depth 5, ~1545 at branch 4).",
   "verdict=HARD_PASS_PROVISIONAL_HOLD; recovery_fraction=1.0; arb_strict_quality=0.039 -> arb_hold_quality=1.0; re_queue_passes_max=3 (<=depth+2); buffer drains final_hold=0; 8 seeds.",
   "SYNTHETIC hierarchical trees. Construction-proof that provisional-hold bootstraps arbitrary order to curriculum-quality at BOUNDED cost; the 'bounded' claim rests on passes<=depth+2 and monotone-draining buffer. Not a real-data capability claim.",
   {"recovery_fraction": 1.0, "arb_strict_quality": 0.039, "arb_hold_quality": 1.0, "passes_max": 3, "bounded_le_depth_plus_2": True, "retry_depth5": 339.9},
   ["curriculum_order (this batch: the order-matters result this rescues)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_provisional_hold_recovers_arbitrary_order_bounded_cost_buffer_drains",
   "provisional_hold_bootstrapping_recovers_arbitrary_order_ingest_bounded_cost_synthetic_construction",
   "HARD_PASS_provisional_hold_recovery_1p0_arb_0p039_to_1p000_passes_max_3_bounded_buffer_drains",
   "CHAIN_GRADE construction. Provisional-hold recovers arbitrary-order ingest (0.039 -> 1.0, recovery 1.0) at bounded cost (passes max 3 <= depth+2; buffer drains to 0).",
   "Confirms Director HARD_PASS; I note the 'bounded cost' is the load-bearing part (passes<=depth+2, monotone-draining buffer) and keep scope synthetic.",
   "+1 CHAIN_GRADE (construction: provisional-hold recovers arbitrary-order ingest at bounded cost).")

# 8 -------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_consolidation_hold_earns_keep_REGIME_APPROPRIATE_capacity_WINS_z28_order_WINS_z86_interference_TIES_3of3_valid_controls_fire_not_blanket_hold_better_synthetic_2026-07-16",
   "CHAIN_GRADE", "consolidation_correct_regimes_v1",
   "MATH CHAIN_GRADE (construction; REGIME-APPROPRIATENESS): selective-hold consolidation earns its keep in the CORRECT regimes and only there. Across 3/3 valid regimes with controls and null-guards firing: (R2 capacity-scarcity) HOLD_WINS, selective_hold 0.605 vs keep-everything 0.561 (margin +0.044, z=28.1); (R3 order/trajectory) HOLD_WINS, trajectory_hold 1.000 vs flat_raw 0.493 (margin +0.490, z=85.9); (R1 interference) HOLD_TIES, hold 0.682 = flat 0.682 (margin +0.000). So hold is regime-appropriate -- it wins under capacity-scarcity and order-dependence, and merely TIES flat under pure interference (where keep-everything 0.712 is actually strongest).",
   "verdict=HARD_PASS; n_valid_regimes=3; R2 capacity HOLD_WINS m=+0.044 z=28.1; R3 order HOLD_WINS m=+0.490 z=85.9; R1 interference HOLD_TIES m=0.000; all controls + null-guards fired.",
   "SYNTHETIC. The honest, load-bearing framing is REGIME-APPROPRIATENESS: hold is NOT universally better -- it ties on interference. Bank 'hold earns its keep specifically under capacity-scarcity and order-dependence', not a blanket 'hold consolidation is better'.",
   {"R2_capacity_margin": 0.044, "R2_z": 28.1, "R3_order_margin": 0.490, "R3_z": 85.9, "R1_interference_margin": 0.0, "R1_keep_everything": 0.712, "n_valid_regimes": 3},
   ["curriculum_order + provisional_hold (order regime lineage)", "temporal_accrual_fair (this batch: hold-vs-arrival order-in-time)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_consolidation_hold_regime_appropriate_wins_capacity_order_ties_interference",
   "selective_hold_consolidation_regime_appropriate_wins_capacity_scarcity_and_order_ties_interference_synthetic_construction",
   "HARD_PASS_hold_wins_capacity_z28_order_z86_ties_interference_3of3_valid_controls_fire",
   "CHAIN_GRADE construction. Hold is REGIME-APPROPRIATE: wins capacity (z=28) and order (z=86), TIES interference; 3/3 valid, controls+nulls fire. Not a blanket 'hold better'.",
   "Confirms Director HARD_PASS ('hold wins on order + capacity'); I add the honest R1 TIE (hold=flat on interference, keep-everything strongest there) so this is banked as regime-appropriateness, not universal superiority.",
   "+1 CHAIN_GRADE (construction: hold consolidation is regime-appropriate -- wins capacity+order, ties interference).")

# 9 -------------------------------------------------------------------------------------------------
mk("math::HARD_FAIL_ingest_gate_SNR_trigger_REFUTED_snr_0p699_below_fixed_0p714_and_time_1p000_null_guard_fails_BUT_schedule_concept_VALIDATED_by_time_clock_time_beats_fixed_plus_0p286_2026-07-16",
   "HARD_FAIL", "ingest_gate_snr_ramp_schedule_v1",
   "MATH HARD_FAIL (honest negative with nuance): an SNR-triggered adaptive ingest schedule is REFUTED -- the SNR-triggered arm (0.699) does NOT beat the best fixed threshold (0.714, d=-0.015) and is far below a simple time-clock schedule (1.000, d=-0.301), and it FAILS the null-guard (snr 0.914 vs fixed 1.000 -- SNR does not reject the noise-only null cleanly); the trigger does not track noise (tighten shift -0.03). BUT the schedule CONCEPT survives: a permissive->selective TIME-CLOCK schedule beats fixed by +0.286 (time_ba 1.000 vs best_fixed 0.714). joint_hard_pass=False.",
   "verdict=HARD_FAIL_snr_trigger_refuted; gates HP_SNR_BEATS_FIXED=False HP_SNR_BEATS_TIME=False HP_NULL_GUARD=False; SCHEDULE_TIME_BEATS_FIXED=True; time_ba 1.0 vs fixed 0.714 (+0.286) vs snr 0.699; joint_hard_pass=False.",
   "SYNTHETIC ingest arena. The negative is SUBSTANTIVE for the SNR-TRIGGER mechanism specifically (the trigger carries no usable noise signal; null-guard fails). It is NOT a test-design failure: the time-clock arm reaches 1.0 and beats fixed by +0.286, validating the harness AND the schedule concept. Revival: implement the schedule via a time-clock (validated); an SNR-trigger would need a genuinely noise-tracking signal.",
   {"snr_ba": 0.699, "best_fixed_ba": 0.714, "time_ba": 1.0, "d_snr_vs_fixed": -0.015, "d_snr_vs_time": -0.301, "time_vs_fixed": 0.286, "null_guard_pass": False},
   ["curriculum_order + provisional_hold (the permissive->selective schedule the time-clock validates)"],
   "experiment_landed_vet", "confirmed_hard_fail_snr_trigger_refuted_schedule_concept_validated_by_time_clock",
   "snr_triggered_ingest_schedule_refuted_but_time_clock_schedule_validated_honest_negative_with_nuance_synthetic",
   "HARD_FAIL_snr_trigger_refuted_does_not_beat_fixed_or_time_null_guard_fails_time_clock_validates_schedule_plus_0p286",
   "HF (honest negative, nuanced). SNR-trigger REFUTED (loses to fixed and time, null-guard fails, trigger does not track noise). Schedule CONCEPT validated by time-clock (+0.286 vs fixed).",
   "Confirms Director's 'atomize the negative-with-nuance'. Attribution HF_STRUCTURAL for the SNR-trigger mechanism (not test-design: the time-clock arm validates harness+concept at 1.0). The schedule concept is kept via the time-clock.",
   "+1 HF (honest negative: SNR-triggered schedule refuted; the permissive->selective schedule concept validated by a time-clock instead).",
   hf_attr="HF_STRUCTURAL_for_SNR_trigger_mechanism (SNR carries no usable noise signal; null-guard fails). NOT test-design: time-clock arm reaches 1.0 and beats fixed +0.286, validating harness+schedule concept. Revival: time-clock schedule; better noise-tracking signal for a trigger.")

# 10 ------------------------------------------------------------------------------------------------
mk("math::MM_TIE_multisource_arena_combination_brain_faithful_race_accumulator_0p868_TIES_learned_logistic_0p863_gap_0p006_below_TIE_EPS_NOT_a_win_route_needs_calibration_gain_0p077_2026-07-16",
   "MEASURED_MECHANISM", "multisource_arena_combination_menu_v1",
   "MATH MM (a measured TIE, NOT a win): across a menu of signal-combination forms, the best brain-faithful combiner (race / 2-accumulator, marginal 0.868) TIES a learned additive logistic (0.863) -- gap +0.006, below the TIE_EPS 0.01 band (verdict BRAIN_FAITHFUL_TIES_OR_BEATS). Route needs calibration to be competitive (uncalibrated 0.784 -> calibrated 0.861, calibration_gain +0.077; branch cost ~0). This is competitiveness/parity of a brain-faithful integrator with a learned baseline, NOT a capability win over the baseline.",
   "verdict=HARD_PASS(=BRAIN_FAITHFUL_TIES_OR_BEATS); best_bf=race_2accumulator 0.868; logistic 0.863; gap_vs_logistic=0.0056 (<TIE_EPS 0.01); route calibration_gain=0.077.",
   "SYNTHETIC arena, MARGINAL metric. The Director's guardrail (statistical TIE ~p0.22, NOT a win) holds off-disk: gap 0.006 is within the tie band. Bank the honest PARITY claim (brain-faithful combination is competitive with a learned baseline), never a 'brain-faithful beats learned' win.",
   {"best_bf_form": "race_2accumulator", "best_bf_marginal": 0.868, "logistic_marginal": 0.863, "gap_vs_logistic": 0.0056, "tie_eps": 0.01, "calibration_gain": 0.077},
   ["arena_v1 (validity parent)", "conjunction_menu (the conjunctive-regime form-match win)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_tie_brain_faithful_combination_ties_learned_logistic_not_a_win",
   "brain_faithful_signal_combination_ties_learned_logistic_measured_parity_not_capability_win_synthetic",
   "TIE_brain_faithful_race_accumulator_0p868_ties_learned_logistic_0p863_gap_0p006_below_tie_eps_route_needs_calibration",
   "MM (measured TIE). Best brain-faithful combiner (race) 0.868 TIES learned logistic 0.863 (gap 0.006 < TIE_EPS). NOT a win. Route needs calibration (+0.077).",
   "Confirms Director's guardrail: this is a statistical TIE, NOT a win. I bank it as a measured parity result (brain-faithful competitive with learned), explicitly refusing a capability-win framing.",
   "+1 MM (measured TIE: brain-faithful signal combination ties a learned logistic; competitive, not a win).")

# 11 ------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_formmatched_conjunctive_arena_multiplicative_gate_beats_additive_logistic_0p850_vs_0p810_marginal_gap_0p039_certified_nonadd_0p073_within_cell_NOT_beats_best_single_2026-07-16",
   "CHAIN_GRADE", "multisource_arena_conjunction_menu_v1",
   "MATH CHAIN_GRADE (form-matched construction-proof): on an arena CERTIFIED conjunctive (nonadditivity gap 0.073; interaction acc 0.757 > linear 0.684; arena non-circular, 4 signals decorrelate, copy 4x), a multiplicative gate beats an additive logistic in the marginal metric -- 0.850 vs 0.810, gap +0.039 (> X_BAND 0.03), multiplicative rank 1 of 9 forms. This demonstrates that when the environment is genuinely conjunctive, a FORM-MATCHED (multiplicative) combiner beats an additive one.",
   "verdict=HARD_PASS(MULTIPLICATIVE_WINS); ARENA_VALID_CONJUNCTIVE nonadd_gap=0.073; mult_marginal 0.850 vs logistic 0.810 gap=0.039; mult_rank 1/9; WITHIN-cell mult 0.616 < best_single 0.650 (mult does NOT beat best-single within-cell).",
   "SYNTHETIC arena constructed to be conjunctive. This is a FORM-MATCHED construction-proof (the arena was built multiplicative, so a multiplicative combiner winning is confirmatory of the form-match), NOT a general 'multiplicative beats additive' capability win. Caveat: within-cell the multiplicative gate does NOT beat best-single (0.616 vs 0.650); the win is in the marginal aggregate.",
   {"nonadd_gap": 0.073, "int_acc": 0.757, "lin_acc": 0.684, "mult_marginal": 0.850, "logistic_marginal": 0.810, "gap": 0.039, "mult_rank": 1, "within_mult": 0.616, "within_best_single": 0.650},
   ["arena_v1 (validity parent)", "combination_menu (non-conjunctive regime where forms TIE)", "nonadditive_discovery arc (conjunctions are the prize)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_formmatched_conjunctive_arena_multiplicative_gate_beats_additive_marginal_not_within_cell",
   "form_matched_multiplicative_gate_beats_additive_logistic_in_certified_conjunctive_arena_construction_proof_synthetic",
   "HARD_PASS_formmatched_multiplicative_beats_additive_0p850_vs_0p810_certified_conjunctive_within_cell_not_beats_single",
   "CHAIN_GRADE (form-matched construction). In a certified-conjunctive arena (nonadd 0.073), multiplicative gate beats additive logistic +0.039 marginal (rank 1/9). Within-cell mult does NOT beat best-single (0.616<0.650).",
   "Confirms Director's guardrail: this is a FORM-MATCHED CONSTRUCTION-PROOF, NOT a capability win. I encode the form-match + the within-cell non-win as scope; it demonstrates conjunctive environments reward form-matched integration, not that multiplicative universally wins.",
   "+1 CHAIN_GRADE (form-matched construction: conjunctive environments reward form-matched multiplicative integration; not a general win).")

# 12 ------------------------------------------------------------------------------------------------
mk("math::HARD_FAIL_multisource_arena_continual_route_gate_hold_LOSES_to_consolidate_everything_0p719_vs_0p826_at_Nmax120_margin_neg0p106_gap_shrinks_but_crossover_EXTRAPOLATED_not_demonstrated_2026-07-16",
   "HARD_FAIL", "multisource_arena_continual_retention_v1",
   "MATH HARD_FAIL (honest negative): in the continual-learning regime, the brain-faithful route/gate/hold arm LOSES to a simple consolidate-everything engineering baseline at every tested scale -- retention@Nmax(120) route 0.719 vs consolidate-everything 0.826 (margin -0.106); the gap does shrink with scale (gap@Nmin(30) -0.153 -> gap@Nmax -0.106, delta +0.047, SCALE_EPS present) but route STILL LOSES at the largest tested N, so any crossover is EXTRAPOLATED, not demonstrated within range. Native exact storage does not dominate either (0.700 at Nmax). Positive control and null-guard both hold (forget-drop fired, route-every posctrl +0.127).",
   "verdict=HARD_FAIL_ROUTE_LOSES; route@Nmax=0.719 vs eng_best(consolidate_everything)=0.826, margin=-0.106; gap@Nmin=-0.153 scaling_delta=+0.047; crosses_within_range=False; native_exact@Nmax=0.700 (does not dominate).",
   "SYNTHETIC continual arena, N<=120. Per brain-baseline discipline, a brain-faithful arm losing to an engineering baseline is a presumed IMPLEMENTATION localization until proven a structural bound -- so this is HF_localization: route underperforms consolidate-everything in the tested continual regime. The gap-shrinking-with-N trend is suggestive but the crossover is NOT demonstrated. Revival: test larger N to check the extrapolated crossover; drill the route as a possible implementation bug.",
   {"route_at_Nmax": 0.719, "eng_best_at_Nmax": 0.826, "margin": -0.106, "gap_at_Nmin": -0.153, "scaling_delta": 0.047, "native_at_Nmax": 0.700, "crosses_within_range": False},
   ["phase_boundary (this batch: N-axis alone never robustly crosses)", "consolidation_regimes (where hold wins in-regime)"],
   "experiment_landed_vet", "confirmed_hard_fail_route_loses_continual_regime_crossover_extrapolated_not_demonstrated",
   "brain_faithful_route_gate_hold_loses_consolidate_everything_continual_regime_crossover_extrapolated_synthetic",
   "HARD_FAIL_route_0p719_loses_consolidate_0p826_at_Nmax_gap_shrinks_but_crossover_extrapolated_native_no_dominate",
   "HF (honest negative). Route/gate/hold LOSES to consolidate-everything at Nmax (0.719 vs 0.826, margin -0.106); gap shrinks with N (+0.047) but crossover is EXTRAPOLATED not demonstrated; native does not dominate.",
   "Confirms Director's guardrail EXACTLY: the scale-crossover is EXTRAPOLATED, not demonstrated. My recompute confirms route still loses at Nmax. HF_localization (brain-faithful losing to engineering = presumed implementation issue until proven structural).",
   "+1 HF (honest negative: brain-faithful route loses to consolidate-everything in the tested continual range; crossover extrapolated).",
   hf_attr="HF_LOCALIZATION (per brain-baseline discipline: brain-faithful arm losing to engineering baseline is presumed implementation until proven structural). Crossover EXTRAPOLATED not demonstrated (route loses at Nmax). Revival: larger N; drill route.")

# 13 ------------------------------------------------------------------------------------------------
mk("math::MM_multisource_arena_phase_boundary_route_vs_keep_advantage_REGIME_GATED_N_axis_ALONE_never_robustly_crosses_through_N1000_margin_neg0p123_to_plus0p004_wins_only_high_noise_corner_2026-07-16",
   "MEASURED_MECHANISM", "multisource_arena_phase_boundary_v1",
   "MATH MM (regime-boundary characterization): the route/gate/hold-vs-keep-everything advantage is REGIME-GATED, not scale-achieved. Along the N axis ALONE the route never robustly crosses keep-everything even out to N=1000 -- margin_vs_keep goes -0.123 (N30), -0.105 (60), -0.035 (120), -0.011 (250), -0.014 (500), +0.004 (N1000, within se 0.016) -- verdict N_ALONE_MOVES_BUT_NEVER_ROBUSTLY_CROSSES. There IS a robust single-axis win vs keep on the p_noise and gate_snr axes (the high-noise corner), so the route's advantage lives in a specific regime, not from scaling N.",
   "verdict=HARD_PASS(but) pure_N robust_crosses_vs_keep=False; margins_by_N=[-0.123,-0.105,-0.035,-0.011,-0.014,+0.004] through N=1000; robust single-axis WIN vs keep only on {p_noise, gate_snr}.",
   "SYNTHETIC arena. Bank the honest regime-map: the brain-faithful route's edge over keep-everything is REGIME-GATED (high-noise / gate_snr corner), NOT achievable by scaling N (N-axis alone never robustly crosses through N=1000). This directly reinforces the continual guardrail: no scale-crossover claim.",
   {"robust_crosses_vs_keep_N_axis": False, "margin_N30": -0.123, "margin_N120": -0.035, "margin_N1000": 0.004, "robust_win_axes": ["p_noise", "gate_snr"]},
   ["continual_retention (this batch: crossover extrapolated on N)", "consolidation_regimes (regime-appropriateness lineage)"],
   "experiment_landed_vet", "confirmed_measured_mechanism_phase_boundary_route_advantage_regime_gated_N_axis_never_robustly_crosses",
   "route_vs_keep_advantage_regime_gated_high_noise_corner_N_axis_alone_never_robustly_crosses_synthetic_phase_map",
   "MIDDLE_regime_map_N_axis_never_robustly_crosses_through_N1000_route_wins_only_high_noise_gate_snr_corner",
   "MM (regime map). Route-vs-keep advantage is REGIME-GATED: N-axis alone never robustly crosses keep-everything through N=1000 (margins -0.123 -> +0.004); route wins robustly only in the high-noise / gate_snr corner.",
   "The cell self-verdict HARD_PASS reads a 'clean crossover' win; my recompute REFRAMES it: N-scaling never robustly crosses (even N=1000), the win is REGIME-GATED. I bank the honest regime characterization (reinforces the continual guardrail), not a scale-crossover win.",
   "+1 MM (regime characterization: route-vs-keep advantage is regime-gated to the high-noise corner; N-scaling alone never robustly crosses).")

# 14 ------------------------------------------------------------------------------------------------
mk("math::HARD_FAIL_multisource_arena_temporal_hold_recover_TIES_decide_at_arrival_0p862_vs_0p859_because_NO_accruing_temporal_info_tig_neg0p016_unfaithful_single_shot_world_posctrl_fires_test_design_2026-07-16",
   "HARD_FAIL", "multisource_arena_temporal_hold_recover_v1",
   "MATH HARD_FAIL (honest negative; regime/test-design, not a broken route): temporal hold-and-recover TIES decide-at-arrival -- route 0.862 vs static_arrival_logistic 0.859 (margin +0.003, below TIE_EPS 0.01) -- because in THIS arena configuration there is NO accruing temporal information to exploit (temporal_info_gain full-minus-arrival = -0.016, i.e. the full trajectory carries no more than the arrival snapshot). The positive control FIRES (when temporal info is planted, route 0.772 vs arrival 0.502), confirming the mechanism works; the arena was an unfaithful single-shot world for this route.",
   "verdict=HARD_FAIL_ROUTE_TIES; route 0.862 vs static_arrival 0.859 margin +0.0035 (<TIE_EPS 0.01); temporal_info_gain=-0.016; positive control fired (route 0.772 vs arrival 0.502 when info present); ARENA_VALID.",
   "SYNTHETIC arena. Attribution is TEST-DESIGN / UNFAITHFUL-WORLD (per the two-frontiers memory: a mechanism shaped by a challenge looks inert when you remove the challenge). The route is NOT broken -- the positive control shows it exploits temporal info when present; this arena config simply had none (tig negative). Revival: the fair-accrual arena (sibling temporal_accrual_fair) where tig is certified positive.",
   {"route": 0.862, "static_arrival": 0.859, "margin": 0.0035, "tie_eps": 0.01, "temporal_info_gain": -0.016, "posctrl_route": 0.772, "posctrl_arrival": 0.502},
   ["temporal_accrual_fair (this batch: the fair world where the route DOES beat arrival)"],
   "experiment_landed_vet", "confirmed_hard_fail_temporal_route_ties_arrival_no_accruing_info_test_design_unfaithful_world",
   "temporal_hold_recover_ties_decide_at_arrival_no_accruing_temporal_info_test_design_unfaithful_world_posctrl_fires",
   "HARD_FAIL_route_ties_arrival_0p862_vs_0p859_tig_neg0p016_no_temporal_info_posctrl_fires_test_design",
   "HF (honest negative, test-design). Temporal hold-recover TIES decide-at-arrival (0.862 vs 0.859) because tig=-0.016 (no accruing info); positive control fires when info is present -> route not broken, world unfaithful.",
   "Confirms Director HARD_FAIL. Attribution TEST-DESIGN/UNFAITHFUL-WORLD (matches the two-frontiers memory rule): the positive control proves the route works when temporal info exists; this config had none. The fair-accrual sibling is the faithful-world revival.",
   "+1 HF (honest negative: temporal route ties arrival in an unfaithful single-shot world with no accruing info; positive control confirms the route works when info is present).",
   hf_attr="HF_TEST_DESIGN / UNFAITHFUL_WORLD (temporal_info_gain -0.016 = no accruing info in this config; positive control fires when info planted -> route works). Revival: temporal_accrual_fair (certified tig +0.249).")

# 15 ------------------------------------------------------------------------------------------------
mk("math::CHAIN_GRADE_construction_temporal_accrual_FAIR_hold_beats_decide_at_arrival_0p855_vs_0p637_plus0p219_z25_certified_tig_0p249_grows_with_noise_BUT_TIES_keep_everything_neg0p030_structure_adds_nothing_beyond_flat_2026-07-16",
   "CHAIN_GRADE", "multisource_arena_temporal_accrual_fair_v1",
   "MATH CHAIN_GRADE (construction; the faithful-world complement to the temporal HF): with CERTIFIED accruing temporal information (temporal_info_gain full-minus-arrival = +0.249, cert fires), deferring commitment (hold-and-recover) BEATS decide-at-arrival -- 0.855 vs 0.637, margin +0.219, z=25.0 (>2 sigma) -- and the advantage GROWS with noise (tig +0.089 clean -> +0.307 high-noise; margin z 11.7 -> 34.2). Controls fire (positive control gap +0.431, null tig +0.000, linear control). BUT hold TIES / slightly-loses to flat keep-everything (margin -0.030): the temporal STRUCTURE (hold/recover) adds nothing beyond flat accumulation.",
   "verdict=HARD_PASS; certified temporal_info_gain=+0.249 (fired); margin_hold_vs_arrival=+0.219 z=25.0; sweep tig grows +0.089->+0.307 with noise; margin_hold_vs_keep=-0.030 (structure adds nothing beyond flat); 8 seeds.",
   "SYNTHETIC arena with certified accruing info. Honest DUAL scope: (a) deferring commitment beats committing-at-arrival WHEN evidence genuinely accrues (this is the real, clean, >2-sigma win, and the faithful-world revival of the temporal_hold_recover HF); (b) the hold/recover STRUCTURE adds nothing over flat keep-everything (margin -0.030) -- so the value is 'wait for evidence', not the specific hold machinery.",
   {"certified_tig": 0.249, "hold": 0.855, "decide_at_arrival": 0.637, "keep_everything": 0.886, "margin_vs_arrival": 0.219, "z_vs_arrival": 25.0, "margin_vs_keep": -0.030, "tig_clean": 0.089, "tig_highnoise": 0.307},
   ["temporal_hold_recover (this batch: the unfaithful-world HF this rescues)", "consolidation_regimes (order/trajectory regime lineage)"],
   "experiment_landed_vet", "confirmed_chain_grade_construction_temporal_accrual_fair_hold_beats_arrival_certified_info_ties_keep_everything",
   "temporal_accrual_hold_beats_decide_at_arrival_with_certified_accruing_info_but_ties_keep_everything_synthetic_construction",
   "HARD_PASS_hold_beats_arrival_0p855_vs_0p637_z25_certified_tig_0p249_but_ties_keep_everything_neg0p030",
   "CHAIN_GRADE construction (dual-scope). With certified accruing info (tig +0.249), hold beats decide-at-arrival +0.219 (z=25), advantage grows with noise; BUT hold TIES keep-everything (-0.030) -- structure adds nothing beyond flat accumulation.",
   "Confirms Director HARD_PASS; I bank the DUAL honest scope: the real win is 'deferring commitment beats committing-at-arrival when evidence accrues' (faithful-world revival of the temporal HF), NOT that the hold/recover structure beats flat keep-everything (it ties/slightly-loses).",
   "+1 CHAIN_GRADE (construction: deferring commitment beats commit-at-arrival with certified accruing info; hold structure ties keep-everything).")


# ==================================================================================================
def write_atomic_append(path, new_lines):
    if not path.exists():
        return (0, 0, False, "path does not exist: %s" % path)
    with open(path, "rb") as f:
        cur_bytes = f.read()
    cur_text = cur_bytes.decode("utf-8")
    pre_count = cur_text.count("\n")
    if cur_bytes and not cur_bytes.endswith(b"\n"):
        cur_bytes = cur_bytes + b"\n"
    parts = [cur_bytes]
    for line in new_lines:
        s = json.dumps(line, ensure_ascii=True)
        if "\n" in s:
            return (pre_count, pre_count, False, "JSON contains newline; not jsonl-safe")
        parts.append((s + "\n").encode("utf-8"))
    new_bytes = b"".join(parts)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "wb") as f:
        f.write(new_bytes); f.flush(); os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        verify_text = f.read().decode("utf-8")
    post_count = verify_text.count("\n")
    expected_post = pre_count + len(new_lines)
    if post_count != expected_post:
        return (pre_count, post_count, False, "line count mismatch: expected %d got %d" % (expected_post, post_count))
    tail = verify_text.rstrip("\n").split("\n")[-len(new_lines):]
    for i, tl in enumerate(tail):
        try:
            parsed = json.loads(tl)
        except Exception as e:
            return (pre_count, post_count, False, "tail-line %d JSON round-trip fail: %s" % (i, e))
        for key in ("id", "atom_id"):
            if key in new_lines[i] and parsed.get(key) != new_lines[i][key]:
                return (pre_count, post_count, False, "tail-line %d %s mismatch" % (i, key))
    return (pre_count, post_count, True, "OK")


def main():
    print("=== A5 atom-write: foundation-builder / arena / claim-validity batch (2026-07-16) ===")
    print("ts_iso =", _iso, " atoms:", len(atoms), " ledger rows:", len(ledgers))
    assert len(atoms) == 15 and len(ledgers) == 15, "expected 15+15"
    ids = [a["id"] for a in atoms]
    assert len(set(ids)) == 15, "duplicate ids in batch"
    for a in atoms:
        assert a["id"].isascii(), "non-ascii id"
    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    dup = [i for i in ids if i in existing]
    if dup:
        print("ABORT: id already in store:", dup); sys.exit(1)
    print("id-uniqueness OK (15 new, none pre-existing)")

    print("Writing 15 atoms to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, atoms)
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 15:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 15 rows to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, ledgers)
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 15:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    # integrity: reload full math atoms, assert all parse and all 15 present
    n_ok = 0
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    missing = [i for i in ids if i not in present]
    assert not missing, "post-write integrity: missing ids %s" % missing
    print("integrity: math/atoms.jsonl fully parses (%d lines), all 15 new ids present." % n_ok)

    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True) ===")
    from collections import Counter
    c = Counter(a["tier"] for a in atoms)
    print("CERT N delta:", dict(c))
    for a in atoms:
        print("  ", a["tier"], "::", a["id"][:70], "...")


if __name__ == "__main__":
    main()
