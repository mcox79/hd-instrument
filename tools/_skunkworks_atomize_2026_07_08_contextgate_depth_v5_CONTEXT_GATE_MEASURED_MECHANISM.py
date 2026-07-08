"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) of substrate_gen_lm_contextgate_depth_v5_n8192_gpu.
THE NIGHT'S HEADLINE: first positive on the Stage-4 attention-routing gap.

CELL: experiments/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu.py (commit 4692cd9cc)
METRICS: data/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu/metrics.json (run_mode=full, 3 seeds
  7/17/23, N_DIM=8192, K_GRID=1,2,3,5, GATE_TAU=0.1, verdict MIDDLE_BAND, cardinality 84/84)

INDEPENDENT OFF-DISK RECOMPUTE (.venv python off per_seed[], this session -- matched cell exactly):
  RAW_BIND per-seed d(K5-K1) = [+0.7399, +0.5509, +0.6552]  mean dRAW = +0.6486   (degrades 3/3)
  CONTEXT_GATE per-seed d     = [+0.0002, -0.0050, +0.0134]  mean dGATE = +0.0028  (flat 3/3; seed17 NEG)
  CONTEXT_GATE_SCRAMBLED d    = [+1.4537, +1.5141, +2.2220]  mean +1.7299 (blows up worse than RAW, 3/3)
  RAW curve  {1:2.7071, 2:2.9728, 3:3.1464, 5:3.3558}
  GATE curve {1:2.7071, 2:2.7086, 3:2.7052, 5:2.7100}   -- GATE@Kmax 2.710 ~= RAW@K1 2.707 (discards noise)
  GSCR curve {1:2.7071, 2:4.0208, 3:4.1614, 5:4.4371}
  gap_gate@Kmax = RAW-GATE = +0.6458 (>=0.30 prereg gate: PASS)
  control separation gap_gate-gap_gscr = +1.7271 (>=0.15 prereg gate: PASS by 11x)
  dGATE = +0.0028 (prereg HARD_PASS needs <=0: MISSES by +0.003 -- knife-edge, soft-gate leakage as flagged)
  degradation reduction = 1 - dGATE/dRAW = 0.9956 (99.56% flatten)
  K=1 anchor: RAW==GATE==GATE_SCRAMBLED EXACTLY per seed (2.77491/2.68426/2.66226) -> identity at K=1.
  Baselines (mean): bigram_oracle 1.982, unigram_floor 5.745, trigram 2.425. RAW@K1 2.707 sits BETWEEN
    bigram-oracle and unigram-floor -> genuine learning, NOT saturation-vacuous.

Q1 (flatten genuine across all 3 seeds, not one seed carrying?) -- YES. Per-seed dGATE=[+0.0002,-0.0050,
  +0.0134]; max |d|=0.0134 (seed23), seed17 is slightly NEGATIVE. All three are essentially flat vs RAW's
  +0.55..+0.74. No single seed carries it; the sign-variation is noise around zero, not seed dependence.

Q2 (scramble fires for the RIGHT reason -> SELECTION not renormalization/free-parameter?) -- YES, proven
  programmatically. gate_scrambled is a PERMUTATION of gate: sorted(g)==sorted(gs), sum(g)==sum(gs)==1.0,
  g[scramble_perm]==gate_scrambled to 1e-6, for every (seed,K>=2). The ONLY difference between CONTEXT_GATE
  and CONTEXT_GATE_SCRAMBLED is WHICH slot gets which admission weight -- identical magnitude spectrum,
  identical normalization. Scramble moves the dominant weight (0.78-0.89) OFF the most-recent slot
  (argmax K-1 -> a noise slot) -> catastrophic blow-up (worse than RAW). Renormalization/magnitude is held
  constant; only slot-assignment differs -> the benefit is SELECTION. Gate is healthy: argmax(g)=K-1 with
  g[K-1] in 0.69..0.89 (>0.5) for all seeds/K -> concentrates on the most-recent (predictive) slot.

Q3 (TIER + honest framing) -- CONTEXT_GATE arm earns MEASURED_MECHANISM as its own finding.
  Whole-cell MIDDLE_BAND is CORRECT at the aggregate level (the strict pre-registered HARD_PASS needs
  dGATE<=0 and it is +0.003; and the OTHER antidotes CLEANUP/RESIDUAL only partially flatten). But the
  CONTEXT_GATE ARM specifically is a near-complete, seed-robust, control-validated flatten (99.56% of the
  +0.649 degradation removed, 3/3 seeds, gap 0.646 bits, permutation-only scramble fires at 11x the gate).
  It is NOT a clean HARD_PASS (misses the pre-committed dGATE<=0 by +0.003 -- exactly the soft-gate residual
  leakage the prereg flagged as risk (a)), so per anti-inflation discipline we do NOT stamp it PASS. It is
  far more than "partial", so we do NOT bury it in the aggregate MIDDLE either. Proven-mechanism = MM: the
  mechanism (selective admission gating flattens noise-compounding) is real and characterized; the claim is
  one knife-edge weaker than the pre-registered clean flatten. cert_delta MM +1.

Q4 (fair regime?) -- YES. RAW genuinely learns (K1 2.707 between bigram-oracle 1.982 and unigram-floor
  5.745) then degrades monotone K1->K5 (2.707->3.356) in all 3 seeds; discriminator VALID-ONLY-IF fired
  (dRAW +0.649>0). K=1 anchor holds: all arms identical at K=1 (identity). Not saturation-vacuous.

Q5 (HONEST SCOPE, locked) -- this is a RECENCY gate on a 1st-ORDER corpus where the optimal selection is
  SIMPLE (attend the most-recent slot; all older context is provable noise). The gate LEARNED exactly that
  (concentrates on slot K-1) and at K5 reproduces the K1 single-token bpc (2.710 ~= 2.707) -- i.e. it fully
  DISCARDS the noise slots rather than integrating multi-slot information. Scope: "selection flattens
  noise-compounding in the regime where the optimal selection is simple," NOT "attention-routing solved."
  The harder UNTESTED question is content-dependent gating on a HIGHER-ORDER corpus where relevant != most-
  recent (a follow-on cell is being scoped). This is the FIRST positive PROBE of the Stage-4 attention-
  routing gap, not closure of it.

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory): top hits cosine 0.368 (wordnet 'degradation'),
  0.341 (GNN per-edge learned weight note), 0.335 (competitive-author selection / selective-attention
  notes) -- NONE is the per-slot context-admission gating mechanism on a noise-compounding generation
  regime. Nearest prior ATOMS are distinct mechanisms: wave14_moe_attention_routing / moe_cosine_router
  (MoE TASK routing, not per-context-slot admission), comp3_cleanup_at_depth (denoise, which this cell
  shows FAILS where gating succeeds), natural_analog_tmr_priority_gating. No prior arc cell at cosine>0.30
  for this mechanism -> GENUINELY NOVEL targeted extension of the noise-compounding arc (the v4 predecessor
  predresidual_td_depth was not atomized into the Store; this cell establishes both the failure (RAW arm,
  dRAW +0.649 3/3 seeds) AND the selection fix in one run with proper permutation-only controls).

PARENTS/COMPOSES:
  correlation-hurts-capacity reference (verified in Store): the flip side -- selective ADMISSION discards
    the noise slots BEFORE they dilute the superposition; complements decouple-store-from-retrieval.
  (textual) noise-compounding arc + Stage-4 attention-routing/action-selection gap (program-level).
  (textual) failed-denoise family: CLEANUP_PER_STEP (dCLEAN +0.504) and PREDICT_RESIDUAL_TD (dRES +0.522)
    only partially flatten in THIS run -> gating succeeds EARLIER (admission) where denoise/residual fail.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_contextgate_depth_v5_CONTEXT_GATE_MEASURED_MECHANISM"
CELL_COMMIT = "4692cd9cc"
TS = time.time()
TS_ISO = "2026-07-08T06:30:00Z"
SESSION = "2026-07-08_contextgate_depth_v5_landed_vet"

CORR_HURTS_REF = "reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08"

atom = {
    "id": (
        "math::MEASURED_MECHANISM_contextgate_depth_v5_n8192_gpu_CONTEXT_GATE_selective_admission_gating_"
        "FLATTENS_noise_compounding_FIRST_POSITIVE_on_Stage4_attention_routing_gap_dGATE_plus0p0028_vs_"
        "dRAW_plus0p6486_99p56pct_reduction_3of3_seeds_perseed_dGATE_plus0p0002_neg0p0050_plus0p0134_all_"
        "flat_gap_gate_Kmax_plus0p646_ge_0p30_SCRAMBLE_is_PERMUTATION_ONLY_of_gate_weights_sorted_g_eq_"
        "sorted_gs_sum_1p0_g_perm_eq_gs_moves_dominant_0p78to0p89_weight_OFF_most_recent_slot_blows_up_"
        "dGSCR_plus1p730_worse_than_RAW_separation_plus1p727_ge_0p15_by_11x_benefit_is_SELECTION_not_"
        "renormalization_gate_concentrates_argmax_K_minus_1_gKm1_0p69to0p89_gt_0p5_healthy_GATE_at_Kmax_"
        "2p710_eq_RAW_at_K1_2p707_fully_DISCARDS_noise_slots_reduces_to_single_token_MISSES_strict_prereg_"
        "dGATE_le_0_by_plus0p003_soft_gate_leakage_as_flagged_NOT_clean_HARD_PASS_whole_cell_MIDDLE_BAND_"
        "correct_RECENCY_gate_1st_order_corpus_optimal_selection_SIMPLE_content_dependent_higher_order_"
        "UNTESTED_regime_fair_RAW_K1_2p707_between_bigram_oracle_1p982_unigram_floor_5p745_learns_then_"
        "degrades_monotone_3of3_K1_anchor_identity_cardinality_84of84_commit_4692cd9cc_2026-07-08"
    ),
    "name": (
        "CONTEXT_GATE selective-admission gating FLATTENS noise-compounding (dGATE +0.003 vs dRAW +0.649, "
        "99.6% reduction, 3/3 seeds) with a permutation-only scramble control that fires catastrophically "
        "-> the lever is SELECTION not renormalization. FIRST positive probe of the Stage-4 attention-routing "
        "gap. Scoped: RECENCY gate on a 1st-order corpus (optimal selection is simple); misses the strict "
        "pre-registered dGATE<=0 by +0.003 (soft-gate leakage) -> MEASURED_MECHANISM, not a clean HARD_PASS."
    ),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "measured_mechanism_selective_admission_gating_flattens_noise_compounding_first_positive_stage4_"
        "attention_routing_gap_recency_regime_misses_strict_dGATE_le_0_by_0p003"
    ),
    "cert_class": (
        "per_slot_relevance_gated_admission_over_roll_bind_context_slots_removes_99pct_of_depth_degradation_"
        "in_a_1st_order_generation_regime_where_optimal_selection_is_recency_selection_validated_by_a_"
        "permutation_only_scramble_control_that_blows_up_worse_than_ungated_baseline_content_dependent_"
        "higher_order_gating_untested"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu (commit "
        "4692cd9cc; FULL, 3 seeds 7/17/23, N_DIM=8192, K_GRID=1,2,3,5, GATE_TAU=0.1, 84/84 units). CLAIM "
        "VERIFIED off-disk (independent .venv recompute off per_seed[], matched the cell exactly). The "
        "confirmed noise-compounding failure reproduces at scale: RAW_BIND depth-degradation dRAW=+0.6486 "
        "bits (K1 2.707 -> K5 3.356), monotone, per-seed [+0.740,+0.551,+0.655] (3/3). The CONTEXT_GATE arm "
        "(per-slot relevance-gated admission over the K roll-bind slots, the ONLY delta vs RAW being the "
        "multiplicative gate) is essentially FLAT: dGATE=+0.0028, per-seed [+0.0002,-0.0050,+0.0134] (3/3 "
        "flat; seed 17 slightly NEGATIVE) -- a 99.56% reduction of the RAW degradation. gap_gate@Kmax = "
        "RAW-GATE = +0.646 (>=0.30 prereg gate: PASS). The firing control CONTEXT_GATE_SCRAMBLED blows up "
        "(K2 4.02, K3 4.16, K5 4.44; dGSCR=+1.730, WORSE than RAW), control-separation +1.727 (>=0.15 prereg "
        "gate: PASS by ~11x). SELECTION IS THE LEVER, PROVEN: gate_scrambled is a PERMUTATION of the gate "
        "weight vector (verified sorted(g)==sorted(gs), sum(g)==sum(gs)==1.0, g[scramble_perm]==gate_scrambled "
        "to 1e-6, every seed/K>=2) -- identical magnitude spectrum and normalization; the ONLY difference is "
        "WHICH slot receives the dominant admission weight. The scramble moves that weight (0.78-0.89) off the "
        "most-recent slot onto a noise slot and the readout collapses -> the benefit is admission SELECTION, "
        "NOT renormalization or a free magnitude parameter. Gate is healthy: argmax(g)=K-1 (most-recent) with "
        "g[K-1] in 0.69-0.89 (>0.5) for all seeds/K; at K=5 GATE bpc (2.710) reproduces the RAW K=1 single-"
        "token bpc (2.707) -- the gate fully DISCARDS the older noise slots rather than integrating them. "
        "TIER = MEASURED_MECHANISM (not clean HARD_PASS): CONTEXT_GATE misses the strict pre-registered "
        "dGATE<=0 by +0.003 -- exactly the soft-gate residual leakage the prereg flagged as risk (a) -- so "
        "per anti-inflation discipline it is a proven mechanism, one knife-edge weaker than the clean flatten, "
        "NOT a stamped PASS. The whole-cell MIDDLE_BAND verdict is CORRECT at the aggregate level (strict gate "
        "missed + the OTHER antidotes CLEANUP dCLEAN=+0.504 and PREDICT_RESIDUAL_TD dRES=+0.522 only partially "
        "flatten). But the CONTEXT_GATE arm as its own finding is far more than partial and earns MM. HONEST "
        "SCOPE (locked): this is a RECENCY gate on a 1st-ORDER corpus where the optimal selection is SIMPLE "
        "(all context beyond gap-1 is provable noise -> discard it); the gate learned exactly that. Content-"
        "dependent gating on a HIGHER-ORDER corpus (relevant != most-recent) is the UNTESTED harder question "
        "and the real Stage-4 attention-routing test; this is the FIRST positive PROBE of that gap, not its "
        "closure. REGIME FAIR: RAW@K1 2.707 sits between bigram-oracle 1.982 and unigram-floor 5.745 -> "
        "genuine learning, not saturation-vacuous; K=1 anchor is exact identity across RAW/GATE/GATE_SCRAMBLED "
        "per seed. HARNESS: cardinality 84/84 (cardinality_ok); arms_differ (7 distinct depth-curve digests, "
        "META_RULE_AF); self-test PASS (roll-bind order-sensitive, gate K1==raw, gate-uniform==raw, gate "
        "concentrates on recent slot, scramble moves off recent, gpu_cleanup==numpy ref). NOT saturation-"
        "vacuous; NOT joint-gate (single depth-curve discriminator); NOT flattering-reconciliation (GATE and "
        "SCRAMBLE share the identical encoder + gate spectrum, differing only by slot permutation -- the "
        "correct paired selection control). CROSS-ARC OVERLAP: top hit cosine 0.368 (<0.30 for the mechanism); "
        "nearest atoms are distinct (MoE task-routing, cleanup-at-depth) -> genuinely novel."
    ),
    "provenance": {
        "cell": "experiments/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu/metrics.json",
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "whole_cell_verdict": "MIDDLE_BAND",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[]: dRAW +0.6486 (per-seed +0.7399/+0.5509/+0.6552); "
            "dGATE +0.0028 (per-seed +0.0002/-0.0050/+0.0134); dGSCR +1.7299; gap_gate@Kmax +0.6458; "
            "separation +1.7271; GATE@Kmax 2.710 == RAW@K1 2.707. Scramble verified as pure permutation of "
            "gate: sorted(g)==sorted(gs), sum==1.0, g[perm]==gs (1e-6), every seed/K. Gate argmax==K-1, "
            "g[K-1] 0.69-0.89. Baselines mean bigram 1.982/unigram 5.745. K1 anchor exact identity per seed."
        ),
    },
    "verified_numbers": {
        "dRAW": 0.6486, "dRAW_per_seed": [0.7399, 0.5509, 0.6552],
        "dGATE": 0.0028, "dGATE_per_seed": [0.0002, -0.0050, 0.0134],
        "dGATE_scrambled": 1.7299, "dGATE_scrambled_per_seed": [1.4537, 1.5141, 2.2220],
        "degradation_reduction_frac": 0.9956,
        "RAW_curve": {"1": 2.7071, "2": 2.9728, "3": 3.1464, "5": 3.3558},
        "GATE_curve": {"1": 2.7071, "2": 2.7086, "3": 2.7052, "5": 2.7100},
        "GATE_SCRAMBLED_curve": {"1": 2.7071, "2": 4.0208, "3": 4.1614, "5": 4.4371},
        "gap_gate_at_Kmax": 0.6458, "prereg_gap_threshold": 0.30,
        "control_separation": 1.7271, "prereg_separation_threshold": 0.15,
        "prereg_dGATE_hardpass_threshold_le": 0.0, "dGATE_miss_over_threshold": 0.0028,
        "GATE_at_Kmax": 2.7100, "RAW_at_K1": 2.7071,
        "gate_argmax_is_most_recent_slot": True, "gate_weight_on_recent_slot_range": [0.6954, 0.8946],
        "scramble_is_permutation_of_gate": True,
        "bigram_oracle_bpc": 1.9819, "unigram_floor_bpc": 5.7446, "trigram_bpc": 2.4249,
        "dCLEANUP": 0.5037, "dPREDICT_RESIDUAL_TD": 0.5220,
        "cardinality_units": 84, "cardinality_expected": 84,
        "K1_anchor_identity_per_seed": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES against a REAL can-fail alternative. The permutation-only SCRAMBLE control could have replicated "
        "the gate benefit if the gain were a renorm/magnitude artifact; it does the OPPOSITE -- catastrophic "
        "blow-up (dGSCR +1.730, worse than RAW), separation +1.727 (11x the 0.15 gate). Discriminator "
        "distinguishes SELECTION from renormalization and fired for selection. Also VALID-ONLY-IF held: RAW "
        "genuinely degrades (dRAW +0.649>0), so the flatten is not a saturated-null artifact."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "Whole-cell MIDDLE_BAND (cell verdict) is CORRECT and UPHELD at the aggregate level -- do NOT restamp "
        "the cell HARD_PASS. But the CONTEXT_GATE ARM specifically is a near-complete seed-robust flatten and "
        "is under-served by the aggregate MIDDLE; it earns MEASURED_MECHANISM as its own finding.",
        "Director framing 'first positive on the Stage-4 attention-routing gap' CONFIRMED off-disk, with a "
        "SCOPE LOCK: it is the first positive PROBE in the RECENCY-optimal regime, NOT attention-routing "
        "solved. The gate learned to DISCARD (reduce to single-token), not to route among competing relevant "
        "slots; content-dependent higher-order gating is untested.",
        "Do NOT inflate the +0.003 miss of dGATE<=0 into a clean HARD_PASS (anti-inflation); do NOT bury the "
        "99.6% flatten under the aggregate MIDDLE (symmetric, anti-negativity). MM is the honest middle.",
        "The benefit is SELECTION, proven by the permutation-only scramble (same weight spectrum, wrong "
        "slots -> collapse); it is NOT a renormalization or free-parameter effect.",
    ],
    "revival_to_hardpass_and_broader_scope_criterion": (
        "Two independent promotion paths. (CLEAN-HARD-PASS in this regime) sharpen GATE_TAU or use a hard "
        "top-1 admission so dGATE<=0 strictly (the +0.003 is soft-gate softmax leakage); if a hard gate holds "
        "dGATE<=0 with the same control-separation, promote MM->CG for the recency regime. (BROADER SCOPE, the "
        "real Stage-4 test) run content-dependent gating on a HIGHER-ORDER corpus where the relevant slot is "
        "NOT the most-recent -- if a learned relevance gate concentrates on the CORRECT (non-recent) slot and "
        "flattens degradation there, that is the substantive attention-routing win; this cell does NOT show it."
    ),
    "composes": [CORR_HURTS_REF],
    "compose_note": (
        "Complements correlation-hurts-capacity DECOUPLE (selective admission discards the noise/correlated "
        "slots BEFORE they dilute the superposition -- gating acts EARLIER than denoise). Parents (textual, "
        "not yet atomized): the noise-compounding arc (v4 predresidual_td_depth, established in-cell here via "
        "the RAW arm dRAW +0.649 3/3) and the Stage-4 attention-routing/action-selection program gap. Contrasts "
        "the failed-denoise family: CLEANUP (dCLEAN +0.504) and PREDICT_RESIDUAL_TD (dRES +0.522) only "
        "partially flatten in THIS same run; admission-gating succeeds where cleanup/residual do not."
    ),
    "cross_arc_overlap_check": (
        "substrate_query top hits cosine 0.368 (wordnet 'degradation'), 0.341 (GNN per-edge weight note), "
        "0.335 (competitive-author/selective-attention notes) -- NONE is per-slot context-admission gating "
        "on a noise-compounding generation regime. Nearest atoms are DISTINCT mechanisms: "
        "wave14_moe_attention_routing / moe_cosine_router (MoE TASK routing), comp3_cleanup_at_depth "
        "(denoise, shown to FAIL where gating succeeds), natural_analog_tmr_priority_gating. No prior arc "
        "cell at cosine>0.30 for this mechanism -> genuinely novel targeted extension."
    ),
    "anchor": "substrate_gen_lm_contextgate_depth_v5_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "context-gate selective admission flattens noise-compounding dGATE +0.003 vs dRAW +0.649 99.6% 3/3 seeds",
        "first positive probe of Stage-4 attention-routing gap: gating succeeds where cleanup/residual partially fail",
        "scramble is permutation-only of gate weights -> benefit is SELECTION not renormalization, control blows up 11x",
        "recency gate on 1st-order corpus reduces to single-token (discards noise); content-dependent higher-order untested",
        "misses strict pre-registered dGATE<=0 by +0.003 soft-gate leakage -> MEASURED_MECHANISM not clean HARD_PASS",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "atom_id": atom["id"], "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "disposition": "measured_mechanism_context_gate_selective_admission_flattens_noise_compounding_first_stage4_positive",
    "cert_status": (
        "mm_selective_admission_gating_flattens_depth_degradation_recency_regime_misses_strict_dGATE_le_0_"
        "by_0p003_whole_cell_middle_band"
    ),
    "cert_class": (
        "per_slot_relevance_gated_admission_removes_99pct_depth_degradation_selection_validated_permutation_"
        "only_scramble_recency_optimal_1st_order_content_dependent_higher_order_untested"
    ),
    "cert_increment_delta": 1,
    "cert_delta": {"CG": 0, "MM": 1, "HF": 0},
    "cert_delta_note": (
        "MM +1: NEW proven mechanism. CONTEXT_GATE selective-admission gating flattens the noise-compounding "
        "depth-degradation from dRAW +0.649 to dGATE +0.003 (99.56% reduction, 3/3 seeds), gap@Kmax +0.646, "
        "with a permutation-only scramble control that fires catastrophically (+1.730, worse than RAW) -> the "
        "lever is SELECTION not renormalization. FIRST positive probe of the Stage-4 attention-routing gap. "
        "MEASURED_MECHANISM not clean HARD_PASS: misses the strict pre-registered dGATE<=0 by +0.003 (soft-"
        "gate leakage as flagged); whole-cell verdict MIDDLE_BAND is correct (other antidotes only partial). "
        "Scoped to the RECENCY-optimal 1st-order regime (gate reduces to single-token / discards noise); "
        "content-dependent higher-order gating UNTESTED. Needs orchestrator Store-sync (atoms.jsonl append; "
        "skunkworks atoms do not auto-persist)."
    ),
    "verified_off_data": True,
    "anchor": "substrate_gen_lm_contextgate_depth_v5_n8192_gpu",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [CORR_HURTS_REF],
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")
    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")
    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            time.sleep(0.1 * (2 ** _attempt))
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")
    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={TS:.3f}")
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (CONTEXT_GATE MEASURED_MECHANISM)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (MM +1)")
    print(f"[A5] DONE OK -> CONTEXT_GATE MEASURED_MECHANISM (MM +1); whole-cell MIDDLE_BAND upheld")


if __name__ == "__main__":
    main()
