"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) of glass_box_micro_loop_retrieve_gate_audit_requery_v1.
Deep-prize glass-box reasoning micro-loop: retrieve -> gate(self-audit) -> re-query -> commit, every hop
Merkle-audited + causally hand-editable. Composes certified attention-gate + value-gate + Merkle-audit.

CELL: experiments/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1.py (commit ba552930a)
METRICS: data/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1/metrics.json (run_mode=full,
  5 seeds 7/17/23/31/41, N=4096 V=256 M=20 n_trials=200 frac_easy=0.5 tau_gate=0.30, verdict HARD_PASS, 5/5)

INDEPENDENT OFF-DISK RECOMPUTE (.venv python off per_seed[], this session -- matched cell exactly):
  Q1 loop-beats-single-shot ALL 5 SEEDS: resolve_lift per seed [0.495 x5] min=max=0.495 (floor 0.25);
    accB=1.000 vs accA=0.505 every seed (accB>accA all 5); paired sign n_b_only=99 n_a_only=0 each seed
    (pooled 495:0). HOLDS unanimously.
  Q2 causal-edit-flip ALL 5 SEEDS: causal_edit_flip [1.0 x5], causal_edit_tamper [1.0 x5],
    tamper_detect [1.0 x5]; n_causal_trials=100 per seed (all 100 HARD+correct trials, substantial N).
    Hand-edit flips downstream recompute AND trips Merkle tamper on every demonstrated trial. HOLDS.
  Q3 scramble/always controls fire ALL 5 SEEDS: accScramble [0.5,0.5,0.5,0.5,0.51], accAlways
    [0.5,0.5,0.505,0.505,0.5] -- both chance-band while accB=1.0; scramble_gap [0.5,0.5,0.5,0.5,0.49]
    min=0.49 (floor 0.25); gate_route_margin min=0.495. HOLDS.
  TELEMETRY-SENSITIVE (not analytically pinned -- the load-bearing MEMORY discipline check): gate_separation
    VARIES per seed 0.7684..0.7897 (spread 0.0213), margin_easy 0.791..0.810, margin_hard 0.0198..0.0273 all
    move per seed; accScramble moved to 0.51 (seed 41), accAlways moved to 0.505 (seeds 23,31) -- discriminators
    respond to seed perturbation. Passes perturb-a-seed-moves-it.
  HARNESS: cardinality 5/5; arms_differ per seed (4 core-arm digests distinct 4/4 each seed; ORACLE==ALWAYS
    exempted, coincide iff hop1=1.0, MEASURED not bug); positive control oracle_bridge=1.0 hop1=1.0; audit
    rails det/verify=1.0; SMOKE=FULL N=4096 (option A); no silent-except (SystemExit before Exception).

FOUR LOCKED CAVEATS (baked into the atom -- do NOT over-extend the framing):
  (1) accB=1.000 is CEILING-SATURATION on an ENGINEERED clean weak-first regime (M/N=20/4096, orthogonal
      codes -> near-lossless retrieval). Certifies the LOOP MECHANISM + glass-box editability + causal
      faithfulness AT A CLEAN REGIME; NOT multi-hop-reasoning-solved-in-the-wild. Baseline ARM_A (0.505) is
      NOT saturated -> not the saturation-vacuous-null failure; baseline_in_band satisfied.
  (2) resolve_lift/accA identical (0.495/0.505) across all 5 seeds is a coincidence of near-zero HARD
      single-shot hit-rate (~1/256 -> exactly 1 lucky hit / 100 hard trials). NOT a red flag because the
      underlying telemetry (gate_sep, margins, scramble/always acc) DOES move per seed -> the metric is a
      real accuracy gap, not a data-ignoring pin.
  (3) sign_p formula quirk (NON-load-bearing): binom_two_sided_p's obs+1e-12 absolute tolerance over-counts
      tail terms when obs~=0.5^99, inflating p from true ~3e-30 to reported 8e-13/seed. Direction is
      CONSERVATIVE (larger p) and still <<0.05 -> does not threaten verdict. Flag for exp_dev if the helper
      is reused for marginal p-values.
  (4) tamper_detect/merkle_verify=1.0 are cryptographic near-certainties (any edit breaks a SHA256 chain),
      soundness rails NOT empirical discoveries. The substantive glass-box claim is causal_edit_flip=1.0
      (the recompute COULD have coincided but did not, 500/500 demonstrated trials).

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory): top cosine ~0.31 -- working_memory (wordnet 0.3154),
  MemReasoner note (0.3086), substrate_working_memory_multi_bank_routing_v1 metrics (0.3076) -- surface
  char-trigram / related-WM hits, NONE a landed cell running THIS composed gated-requery + Merkle causal-edit
  loop. Prereg's own 0.3242 PER-HOP-AUDIT hit is a DESIGN anchor, not a landed loop. Genuine novel composition;
  July-1 INT8-rediscovery pattern does NOT apply.

PARENTS/COMPOSES (mechanism-level reuse; the GPU/import-unsafe cells NOT re-run):
  Merkle audit-replay rail: exp_reasoning_chain_replay_v1 / exp_khop_audit_replay_v1 (helpers transcribed verbatim)
  arbitration-margin gate:  exp_substrate_gen_lm_combinedgate_recency_content_v8 (CHAIN_GRADE, v8 arbitration margin)
  BG Go/NoGo value-gate:    exp_pfc_bg_composed_attention_value_gate_v1

TIER = CHAIN_GRADE / CERTIFY-WITH-CAVEAT. All 3 audit questions HOLD unanimously across 5 seeds; discriminators
  telemetry-sensitive (perturb-verified, not pinned); positive controls + audit rails clean; novel composition.
  The caveat is SCOPE (clean engineered regime), not validity -- the finding is fully supported within regime.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_08_glass_box_micro_loop_retrieve_gate_audit_requery_v1_CHAIN_GRADE"
CELL_COMMIT = "ba552930a"
TS = time.time()
TS_ISO = "2026-07-08T00:00:00Z"
SESSION = "2026-07-08_glass_box_micro_loop_retrieve_gate_audit_requery_v1_landed_vet_GLASS_BOX_REASONING_LOOP_CG"

# mechanism-level parents (verified present in Store; cited, not re-run)
P_COMBINEDGATE_V8 = (
    "math::CHAIN_GRADE_combinedgate_recency_content_v8_n8192_gpu_COMBINED_GATE_parameter_free_biased_"
    "competition_ARBITRATES_recency_prior_and_content_cue_bias_bias_softmax_content_rel_over_tau_plus_recency_"
    "bias_CAPSTONE_of_attention_routing_arc_commit_4227e7e97_2026-07-08"
)

atom = {
    "id": (
        "math::CHAIN_GRADE_glass_box_micro_loop_retrieve_gate_audit_requery_v1_GLASS_BOX_self_auditing_"
        "retrieve_gate_audit_requery_loop_composes_certified_attention_gate_value_gate_merkle_audit_gated_WM_"
        "mediated_requery_RESOLVES_weak_first_multihop_single_shot_CANNOT_resolve_lift_0p495_accB_1p000_vs_"
        "accA_0p505_ALL_5_seeds_7_17_23_31_41_paired_sign_495to0_pooled_99to0_perseed_controls_at_chance_"
        "accScramble_0p50_accAlways_0p50_scramble_gap_0p49to0p50_gate_route_margin_0p495_TELEMETRY_SENSITIVE_"
        "not_pinned_gate_separation_VARIES_perseed_0p7684to0p7897_spread_0p0213_margins_move_accScr_to_0p51_"
        "seed41_accAlways_to_0p505_seed23_31_CAUSAL_HAND_EDIT_holds_edit_logged_bridge_flips_downstream_"
        "recompute_AND_fires_merkle_tamper_causal_edit_flip_1p000_tamper_1p000_100of100_trials_perseed_"
        "positive_control_oracle_bridge_1p000_hop1_1p000_audit_rails_det_verify_1p000_CAVEAT_accB_1p000_is_"
        "CEILING_SATURATION_engineered_clean_regime_MoverN_20over4096_orthogonal_certifies_LOOP_MECHANISM_plus_"
        "glass_box_editability_NOT_multihop_reasoning_solved_in_wild_baseline_ARM_A_0p505_in_band_not_saturated_"
        "resolve_lift_identical_across_seeds_is_near_zero_hard_hit_rate_coincidence_NOT_pin_telemetry_moves_"
        "tamper_merkle_1p000_are_sha256_soundness_rails_not_discoveries_causal_flip_is_the_substantive_claim_"
        "composes_reasoning_chain_replay_merkle_rail_combinedgate_v8_arbitration_margin_pfc_bg_value_gate_"
        "cardinality_5of5_commit_ba552930a_2026-07-08"
    ),
    "name": (
        "GLASS-BOX self-auditing retrieve->gate->audit->requery micro-loop: a gated WORKING-MEMORY-mediated "
        "re-query RESOLVES a weak-first multi-hop regime a single shot CANNOT (resolve_lift=0.495, accB=1.000 "
        "vs accA=0.505, ALL 5 seeds, paired 495:0), controls sit at chance (scramble/always ~0.50, "
        "telemetry-sensitive not analytically pinned -- gate_sep varies per seed), and the causal HAND-EDIT "
        "property holds (edit a logged step -> downstream recompute flips AND Merkle tamper fires, 100/100 "
        "trials/seed). Composes certified attention-gate (v8) + BG value-gate + Merkle-audit rail. CAVEAT: "
        "clean engineered regime, accB=1.0 ceiling-saturation -> certifies the loop MECHANISM + glass-box "
        "editability, NOT multi-hop-reasoning-solved-in-the-wild. CHAIN_GRADE / CERTIFY-WITH-CAVEAT."
    ),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "cg_glass_box_self_auditing_retrieve_gate_audit_requery_loop_gated_wm_requery_resolves_weak_first_"
        "multihop_single_shot_cannot_controls_at_chance_telemetry_sensitive_causal_hand_edit_flips_downstream_"
        "and_fires_merkle_tamper_5seed_robust_clean_engineered_regime_mechanism_plus_glass_box_editability"
    ),
    "cert_class": (
        "composed_retrieve_then_margin_self_audit_gate_go_nogo_then_wm_mediated_requery_bind_bridge_hat_into_"
        "hop2_store_then_commit_every_hop_merkle_chained_over_a_mixed_easy_hard_corpus_where_single_shot_"
        "resolves_easy_only_and_gated_loop_resolves_both_with_scramble_and_always_requery_controls_and_a_"
        "monitor_not_control_causal_hand_edit_of_the_logged_bridge_that_flips_the_downstream_recompute_and_"
        "breaks_the_committed_root_clean_engineered_weak_first_regime_ceiling_saturated_mechanism_arm"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1 (commit "
        "ba552930a; run_mode=full; 5 seeds 7/17/23/31/41; N=4096 V=256 M=20 n_trials=200 frac_easy=0.5 "
        "tau_gate=0.30; 5/5 units; verdict HARD_PASS). Deep-prize glass-box reasoning micro-loop: retrieve -> "
        "gate(self-audit) -> re-query -> commit, every hop Merkle-audited and causally hand-editable. CLAIM "
        "VERIFIED off-disk by independent .venv recompute off per_seed[] (NOT from verdict_msg). THE LOOP: hop-1 "
        "retrieves a bridge into working memory (WM active-slot); the arbitration MARGIN (top1-top2 cleanup) is "
        "the self-audit 'why-signal'; a BG-style Go/NoGo value-gate commits the single shot if margin>=tau else "
        "re-queries by BINDING the WM bridge into the hop-2 store; every step is logged as a hop_record and "
        "Merkle-chained. THE WEAK-FIRST REGIME (falsifiable, B-beats-A NOT tautological): a mixed corpus half "
        "EASY (answer bound to the query anchor -> single shot resolves, high margin) half HARD (answer bound to "
        "a BRIDGE not the anchor -> single shot lands on noise). Single-shot resolves EASY only (acc~frac_easy); "
        "always-requery resolves HARD but BREAKS EASY; only the GATED loop resolves BOTH. AUDIT FINDINGS (all "
        "three load-bearing questions HOLD unanimously across ALL 5 FULL seeds, verified off per_seed NOT the "
        "means): (Q1) LOOP BEATS SINGLE-SHOT EVERY SEED -- resolve_lift per seed [0.495 x5] min=max=0.495 (floor "
        "0.25, clears ~2x); accB=1.000 vs accA=0.505 on all 5 seeds (accB>accA true every seed); paired sign "
        "test n_b_only=99 n_a_only=0 each seed (pooled 495:0), p<<0.05. (Q2) CAUSAL-EDIT-FLIP + TAMPER EVERY "
        "SEED -- causal_edit_flip [1.0 x5], causal_edit_tamper [1.0 x5], tamper_detect [1.0 x5]; "
        "n_causal_trials=100 per seed (all 100 HARD+correct trials, substantial N not 1-2): hand-editing the "
        "logged bridge (true->distractor) flips the recomputed downstream answer AND trips the Merkle root "
        "mismatch on every demonstrated trial. (Q3) SCRAMBLE/ALWAYS CONTROLS FIRE EVERY SEED -- accScramble "
        "[0.5,0.5,0.5,0.5,0.51], accAlways [0.5,0.5,0.505,0.505,0.5] both stay in chance-band while accB=1.0; "
        "scramble_gap [0.5,0.5,0.5,0.5,0.49] min=0.49 (floor 0.25); gate_route_margin min=0.495. TELEMETRY-"
        "SENSITIVE, NOT ANALYTICALLY PINNED (the load-bearing discipline check): gate_separation VARIES per seed "
        "(0.7684..0.7897, spread 0.0213), margin_easy 0.791..0.810 and margin_hard 0.0198..0.0273 both move per "
        "seed, and accScramble moved to 0.51 (seed 41) / accAlways to 0.505 (seeds 23,31) -- the discriminators "
        "respond to seed perturbation (perturb-a-seed-moves-it satisfied). HARNESS: cardinality 5/5; arms_differ "
        "per seed (4 core-arm committed-answer digests distinct 4/4 each seed; ARM_ORACLE_BRIDGE==ARM_ALWAYS "
        "coincide exactly iff hop1_retrieve_acc==1.0, a MEASURED property, documented/exempted not a bug); "
        "positive control oracle_bridge_acc=1.000 + hop1_retrieve_acc=1.000; audit rails deterministic_replay="
        "merkle_verify=1.000; SMOKE holds N==FULL N=4096 (option A, same branches); no silent-except (SystemExit "
        "raised before Exception, crash-metrics path present); prereg bands == code HP constants == metrics gate "
        "thresholds (aligned). FOUR LOCKED CAVEATS (scope, not validity): (1) accB=1.000 is CEILING-SATURATION "
        "on an ENGINEERED CLEAN weak-first regime (M/N=20/4096, near-orthogonal codes -> near-lossless "
        "retrieval); certifies the LOOP MECHANISM + glass-box auditability/editability + causal faithfulness AT "
        "A CLEAN REGIME, NOT multi-hop-reasoning-solved-in-the-wild. Baseline ARM_A (0.505) is NOT saturated so "
        "this is NOT the saturation-vacuous-null failure; baseline_in_band satisfied. (2) resolve_lift/accA "
        "identical (0.495/0.505) across all 5 seeds is a coincidence of near-zero HARD single-shot hit-rate "
        "(~1/256 -> exactly 1 lucky hit per 100 hard trials), NOT a data-ignoring pin -- the telemetry beneath "
        "it (gate_sep, margins, scramble/always acc) DOES move per seed. (3) the sign_p helper "
        "(binom_two_sided_p) has an obs+1e-12 absolute-tolerance quirk that over-counts tail terms when "
        "obs~=0.5^99, inflating p from true ~3e-30 to reported 8e-13/seed -- CONSERVATIVE (larger p) and still "
        "<<0.05, non-load-bearing; flag for exp_dev if reused for marginal p-values. (4) tamper_detect/"
        "merkle_verify=1.0 are SHA256 cryptographic near-certainties (any edit breaks a hash chain) -- soundness "
        "rails, NOT empirical discoveries; the substantive glass-box claim is causal_edit_flip=1.0 (the "
        "recompute COULD have coincided but did not, 500/500 demonstrated trials). TIER = CHAIN_GRADE / "
        "CERTIFY-WITH-CAVEAT: all three audit questions hold unanimously 5/5 seeds, discriminators "
        "telemetry-sensitive (perturb-verified not pinned), positive controls + audit rails clean, genuine novel "
        "composition (cross-arc top cosine ~0.31, no prior loop cell). Composes reasoning_chain_replay Merkle "
        "rail + combinedgate_v8 arbitration margin + pfc_bg value-gate at the mechanism level (those cells NOT "
        "re-run). commit ba552930a 2026-07-08."
    ),
    "provenance": {
        "cell": "experiments/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1.py",
        "commit": CELL_COMMIT,
        "metrics_path": "data/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1/metrics.json",
        "prereg": "preregs/2026-07-08_glass_box_micro_loop_retrieve_gate_audit_requery_v1.md",
        "seeds": [7, 17, 23, 31, 41],
        "run_mode": "full",
        "whole_cell_verdict": "HARD_PASS",
        "audit_tier": "CHAIN_GRADE",
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent .venv recompute off per_seed[] (5/5 units). Q1: resolve_lift [0.495 x5] min=max=0.495; "
            "accB=1.0 vs accA=0.505 all seeds; paired sign 99:0 per seed, 495:0 pooled. Q2: causal_edit_flip / "
            "causal_edit_tamper / tamper_detect all [1.0 x5]; n_causal=100/seed. Q3: accScramble "
            "[0.5,0.5,0.5,0.5,0.51], accAlways [0.5,0.5,0.505,0.505,0.5], scramble_gap min 0.49, gate_route_margin "
            "min 0.495. Telemetry: gate_separation [0.7768,0.7684,0.7816,0.7897,0.7779] (spread 0.0213), "
            "margin_easy [0.7966,0.7913,0.8089,0.8101,0.8027], margin_hard [0.0198,0.0229,0.0273,0.0204,0.0247] "
            "-- all move per seed. cardinality 5/5; 4 core arm_digests distinct each seed; oracle_bridge=1.0 "
            "hop1=1.0 det=verify=1.0. Summary means reproduce exactly from per_seed."
        ),
    },
    "verified_numbers": {
        "N": 4096, "V": 256, "M": 20, "n_trials": 200, "frac_easy": 0.5, "tau_gate": 0.30,
        "resolve_lift_per_seed": [0.495, 0.495, 0.495, 0.495, 0.495], "resolve_lift_min": 0.495,
        "resolve_lift_max": 0.495, "resolve_lift_floor": 0.25,
        "accA_per_seed": [0.505, 0.505, 0.505, 0.505, 0.505],
        "accB_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "accScramble_per_seed": [0.5, 0.5, 0.5, 0.5, 0.51],
        "accAlways_per_seed": [0.5, 0.5, 0.505, 0.505, 0.5],
        "accOracle_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "scramble_gap_per_seed": [0.5, 0.5, 0.5, 0.5, 0.49], "scramble_gap_min": 0.49, "scramble_gap_floor": 0.25,
        "gate_route_margin_per_seed": [0.5, 0.5, 0.495, 0.495, 0.5], "gate_route_margin_min": 0.495,
        "causal_edit_flip_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "causal_edit_tamper_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "tamper_detect_per_seed": [1.0, 1.0, 1.0, 1.0, 1.0],
        "n_causal_trials_per_seed": [100, 100, 100, 100, 100],
        "gate_separation_per_seed": [0.776767578125, 0.7683984375, 0.7815722656, 0.789697265625, 0.7779101562],
        "gate_separation_spread": 0.0213, "gate_separation_floor": 0.10,
        "margin_easy_per_seed": [0.7965625, 0.79134765625, 0.808857421875, 0.810078125, 0.80265625],
        "margin_hard_per_seed": [0.019794921875, 0.02294921875, 0.02728515625, 0.020380859375, 0.02474609375],
        "hop1_retrieve_acc": 1.0, "oracle_bridge_acc": 1.0, "gate_routing_acc": 1.0,
        "deterministic_replay": 1.0, "merkle_verify": 1.0,
        "sign_n_b_only_per_seed": 99, "sign_n_a_only_per_seed": 0, "sign_pooled": [495, 0],
        "sign_p_reported": 2.9843823673616163e-12, "sign_p_true_order": 3e-30,
        "sign_p_note": "reported p CONSERVATIVE (obs+1e-12 tolerance over-counts tail); true ~3e-30, both <<0.05",
        "cardinality_units": 5, "cardinality_expected": 5, "arm_digests_distinct_per_seed": 4,
        "accB_is_ceiling_saturation": True, "baseline_ARM_A_in_band": True,
    },
    "can_fail_discriminator_verdict": (
        "FIRES against REAL can-fail alternatives and is TELEMETRY-SENSITIVE (verified by seed perturbation, not "
        "just by low cv). (1) ARM_B_SCRAMBLE (gated but re-queries with a RANDOM bridge) could have replicated "
        "the gain if the benefit were merely 'a free second try'; it COLLAPSES to chance (scramble_gap 0.49-0.50) "
        "-> the WM CONTENT is what resolves. (2) ARM_ALWAYS_REQUERY (never accept the shot) BREAKS the easy "
        "trials (accAlways ~0.50) -> the GATE ROUTING is load-bearing, not the re-query alone. (3) HARD_FAIL "
        "branch was reachable: if a single shot could solve HARD, ARM_A would win and resolve_lift~0 -- it did "
        "not (accA=0.505 in-band, not saturated). (4) The discriminators MOVE across seeds (gate_sep spread "
        "0.0213, accScr->0.51, accAlways->0.505) -> NOT analytically pinned. (5) causal_edit_flip could have "
        "coincided (recomputed answer == original) but flips on all 500 demonstrated trials. The audit rails "
        "(tamper/merkle) are SHA256 near-certainties (soundness, not the discriminator)."
    ),
    "framing_corrections_vs_cell_author_and_director": [
        "HARD_PASS (cell verdict) UPHELD at CHAIN_GRADE off independent recompute -- all three load-bearing "
        "audit questions hold UNANIMOUSLY across 5 seeds (resolve_lift min=max=0.495, causal_flip/tamper 1.0 all "
        "seeds, controls at chance all seeds). Symmetric anti-negativity: do NOT deflate a 5-seed-robust "
        "telemetry-sensitive glass-box loop that rescues both single-shot failure modes.",
        "SCOPE QUALIFIER IS LOAD-BEARING (bake into any downstream framing): accB=1.000 is CEILING-SATURATION on "
        "an ENGINEERED CLEAN weak-first regime (M/N=20/4096, orthogonal codes -> near-lossless retrieval). This "
        "certifies the LOOP MECHANISM + glass-box auditability/hand-editability + causal faithfulness, NOT "
        "'multi-hop reasoning solved in the wild'. The correct claim is 'a gated WM re-query loop cleanly "
        "resolves the engineered weak-first regime and is glass-box editable', NOT 'the substrate reasons'. The "
        "prereg itself scopes this carefully ('minimal glass-box micro-loop') -- the author did NOT overclaim; "
        "this note prevents downstream over-extension.",
        "resolve_lift/accA being identical (0.495/0.505) across all 5 seeds is a coincidence of the near-zero "
        "HARD single-shot hit-rate (~1/256), NOT evidence of an analytically-pinned metric. The telemetry "
        "underneath (gate_separation varies per seed, margins vary, scramble/always acc perturb) confirms the "
        "discriminator reads the data -- it is a real accuracy gap, not a data-ignoring constant.",
        "tamper_detect=1.0 and merkle_verify=1.0 are cryptographic near-certainties (any edit breaks a SHA256 "
        "chain), soundness RAILS not empirical findings. The substantive glass-box CLAIM is causal_edit_flip=1.0 "
        "(editing the logged bridge changes the recomputed downstream answer) -- that IS measured (500/500 could "
        "have coincided but did not). Anchor the glass-box claim on causal_edit_flip, not on the hash rails.",
        "sign_p reported (2.98e-12 pooled / 8e-13 per seed) is a CONSERVATIVE over-estimate from the "
        "binom_two_sided_p obs+1e-12 tolerance quirk (true ~3e-30); still <<0.05, so the significance is real "
        "and the quirk is non-load-bearing. Not a science defect; a helper-precision note for exp_dev.",
    ],
    "revival_or_extension_criterion": (
        "CG scope LOCKED to: the composed retrieve->gate(margin self-audit)->WM-mediated re-query->commit loop "
        "with per-hop Merkle audit + causal hand-edit, on the ENGINEERED clean weak-first mixed corpus (N=4096 "
        "V=256 M=20, frac_easy=0.5, tau_gate=0.30, orthogonal bipolar codes, argmax-margin cleanup), 5 seeds. "
        "EXTENSIONS (each a NEW cell, composes NOT supersedes): (1) CAPACITY-STRESS / NOISY-READOUT regime -- "
        "push M/N toward capacity or inject rendering noise so retrieval is NO LONGER near-lossless; does the "
        "gate self-audit still route correctly and does resolve_lift survive when accB is NOT at ceiling (this "
        "is the load-bearing robustness question the clean regime cannot answer). (2) DEEPER CHAINS -- >2 hops "
        "(current loop is up to 2 hops); does the WM re-bind compose across 3-4 hops without a global chain "
        "bundle. (3) MULTI-BRIDGE / branching re-query -- more than one candidate bridge competing at the gate. "
        "(4) LEARNED (not fixed) tau_gate adapted per-context. DEMOTION trigger: if a re-run shows the resolve "
        "depends on the ceiling-saturation (i.e. resolve_lift collapses once accB leaves 1.0 under any "
        "non-degenerate noise), or the scramble control stops firing, or causal_edit_flip drops below 0.80."
    ),
    "composes": [P_COMBINEDGATE_V8],
    "compose_note": (
        "The glass-box reasoning micro-loop composes three certified substrate parts at the MECHANISM level "
        "(the source cells are NOT re-run): (A) the Merkle audit-replay rail from exp_reasoning_chain_replay_v1 "
        "/ exp_khop_audit_replay_v1 (helpers h/merkle_root/merkle_verify transcribed verbatim; those cells run "
        "_selftest at import so are import-unsafe) -- the glass-box wrapper; (B) the arbitration MARGIN "
        "(top1-top2 biased-competition) from combinedgate_recency_content_v8 (CHAIN_GRADE) -- realized here as "
        "the CPU cleanup margin the self-audit gate reads; (C) the basal-ganglia Go/NoGo value-gate from "
        "exp_pfc_bg_composed_attention_value_gate_v1 -- the margin-threshold commit-vs-requery decision. The "
        "NOVEL contribution is the COMPOSED LOOP: a gated WM-mediated re-query that resolves a falsifiable "
        "weak-first multi-hop regime a single shot cannot, PLUS the causal hand-edit demonstration (editing a "
        "logged step changes the downstream recompute and fires the tamper flag). None of the parents is "
        "superseded. Brain-grounding (research_neural_reasoning_loop_mechanism_inventory_2026-07-08): "
        "PFC->hippocampus retrieval-in-service-of-inference (match/mismatch = stop-vs-requery), WM active-slot "
        "holds the partial result and is re-bound into the store, cortico-BG-thalamic Go/NoGo value-gate."
    ),
    "cross_arc_overlap_check": (
        "substrate_query 'glass box reasoning loop retrieve gate audit re-query working memory multi-hop merkle "
        "tamper causal edit' -> top cosine 0.3154 (wordnet 'working_memory'), 0.3086 (MemReasoner note: latent "
        "memory for multi-hop), 0.3076 (substrate_working_memory_multi_bank_routing_v1 metrics) -- surface "
        "char-trigram / related-WM hits, NONE a landed cell running THIS composed gated-requery + Merkle "
        "causal-edit loop at cosine>0.30 on the MECHANISM. The prereg's own 0.3242 PER-HOP-AUDIT hit is a DESIGN "
        "anchor (realized by the audit layer), not a landed loop cell. Consistent with SUBSTRATE-KNOWS-NOTHING. "
        "Genuine novel composition of reasoning_chain_replay + combinedgate_v8 + pfc_bg_value_gate; the July-1 "
        "INT8-rediscovery pattern does NOT apply."
    ),
    "anchor": "glass_box_micro_loop_retrieve_gate_audit_requery_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23, 31, 41],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "needs_orchestrator_store_sync": True,
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "glass-box self-auditing retrieve->gate->audit->requery micro-loop -- gated WM re-query resolves weak-first multi-hop a single shot cannot; CHAIN_GRADE / CERTIFY-WITH-CAVEAT",
        "resolve_lift=0.495 accB=1.000 vs accA=0.505 all 5 seeds (paired 495:0); controls at chance (scramble/always ~0.50, telemetry-sensitive not pinned)",
        "causal hand-edit property: edit a logged step -> downstream recompute flips AND Merkle tamper fires, 100/100 trials/seed (causal_edit_flip=1.0)",
        "SCOPE CAVEAT: clean engineered weak-first regime, accB=1.0 ceiling-saturation -> certifies loop MECHANISM + glass-box editability, NOT multi-hop-reasoning-in-the-wild",
        "composes reasoning_chain_replay Merkle rail + combinedgate_v8 arbitration margin + pfc_bg Go/NoGo value-gate (mechanism-level reuse, not re-run)",
        "glass_box_micro_loop_retrieve_gate_audit_requery_v1 landed-VET CHAIN_GRADE",
    ],
    "added_atom_id": None,
}
atom["added_atom_id"] = atom["id"]

ledger = {
    "ts": TS, "ts_iso": TS_ISO, "op": "add", "atom_id": atom["id"], "corpus": "math",
    "tier": "CHAIN_GRADE",
    "disposition": "chain_grade_new_capability_glass_box_reasoning_loop_certify_with_caveat",
    "cert_status": (
        "cg_glass_box_self_auditing_retrieve_gate_audit_requery_loop_gated_wm_requery_resolves_weak_first_"
        "multihop_single_shot_cannot_controls_at_chance_telemetry_sensitive_causal_hand_edit_flips_downstream_"
        "and_fires_merkle_tamper_5seed_robust_clean_engineered_regime_certify_with_caveat"
    ),
    "cert_class": (
        "composed_retrieve_margin_self_audit_gate_go_nogo_wm_mediated_requery_merkle_audited_loop_over_mixed_"
        "easy_hard_weak_first_corpus_with_scramble_and_always_requery_controls_and_causal_hand_edit_proven_"
        "bound_clean_engineered_regime"
    ),
    "cert_increment_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta": {"CG": 1, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "CG +1: NEW capability (glass-box reasoning micro-loop), not a promotion of an existing atom. A composed "
        "retrieve->gate(margin self-audit)->WM-mediated re-query->commit loop, every hop Merkle-audited and "
        "causally hand-editable. ADVERSARIAL landed-VET verified off-disk by independent .venv recompute off "
        "per_seed[] (NOT verdict_msg). ALL THREE load-bearing audit questions HOLD UNANIMOUSLY across 5 seeds "
        "7/17/23/31/41: (Q1) loop beats single-shot EVERY seed (resolve_lift [0.495 x5] min=max=0.495, accB=1.0 "
        "vs accA=0.505, paired sign 99:0/seed pooled 495:0); (Q2) causal hand-edit flips downstream recompute AND "
        "fires Merkle tamper EVERY seed (causal_edit_flip/tamper_detect [1.0 x5], 100/100 trials/seed); (Q3) "
        "scramble + always-requery controls stay at chance EVERY seed (accScramble/accAlways ~0.50, scramble_gap "
        "min 0.49, gate_route_margin min 0.495). DISCRIMINATOR TELEMETRY-SENSITIVE (perturb-verified, NOT "
        "analytically pinned): gate_separation varies per seed 0.7684..0.7897 (spread 0.0213), margins move, "
        "accScr->0.51 seed41 / accAlways->0.505 seeds23,31. Positive control oracle_bridge=1.0 hop1=1.0; audit "
        "rails det/verify=1.0; cardinality 5/5; 4 core arm_digests distinct each seed. FOUR LOCKED CAVEATS "
        "(scope not validity): (1) accB=1.0 is CEILING-SATURATION on an ENGINEERED clean regime (M/N=20/4096, "
        "orthogonal codes) -> certifies the LOOP MECHANISM + glass-box editability, NOT multi-hop-reasoning-in-"
        "the-wild; baseline ARM_A=0.505 NOT saturated (not saturation-vacuous). (2) identical resolve_lift/accA "
        "across seeds is a near-zero-hard-hit-rate coincidence, not a pin (telemetry moves). (3) sign_p helper "
        "obs+1e-12 quirk inflates p CONSERVATIVELY (true ~3e-30, reported 8e-13, both <<0.05). (4) tamper/merkle "
        "=1.0 are SHA256 soundness rails, not discoveries; causal_edit_flip is the substantive claim. Whole-cell "
        "HARD_PASS verdict UPHELD at CHAIN_GRADE / CERTIFY-WITH-CAVEAT. Composes reasoning_chain_replay Merkle "
        "rail + combinedgate_v8 arbitration margin + pfc_bg Go/NoGo value-gate (mechanism-level reuse, none "
        "superseded, cells NOT re-run). Needs orchestrator Store-sync (atoms.jsonl append; skunkworks atoms do "
        "not auto-persist)."
    ),
    "verified_off_data": True,
    "anchor": "glass_box_micro_loop_retrieve_gate_audit_requery_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks", "atomized_by": "hdi_skunkworks",
    "landed_VET_session": SESSION,
    "composes": [P_COMBINEDGATE_V8],
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": ["data/exp_glass_box_micro_loop_retrieve_gate_audit_requery_v1/metrics.json"],
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
    append_jsonl_a5(MATH_ATOMS, atom, "math/atoms (GLASS_BOX micro-loop CHAIN_GRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger, "cert_ledger (CG +1)")
    print(f"[A5] DONE OK -> GLASS_BOX reasoning micro-loop CHAIN_GRADE (CG +1); whole-cell HARD_PASS upheld")


if __name__ == "__main__":
    main()
