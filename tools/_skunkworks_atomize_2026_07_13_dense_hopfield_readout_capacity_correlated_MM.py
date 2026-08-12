"""
A5-gated atom-write: dense/modern-Hopfield READOUT capacity lift on correlated codes (2026-07-13).

Landed-VET (AUDIT-ONLY, adversarial off-disk recompute, .venv) of the #1 Phase-2 capacity lever.
CLAIMED verdict HARD_PASS / CAPACITY_LIFT_REAL (3.25x corr lift, iid 5.48x, scramble 0.01).

INDEPENDENT RECOMPUTE (reimplemented the readout+codegen from scratch, NOT imported from the
cell, NOT from verdict_msg; Fix #28):
  - 5 spot-checked recall curves reproduce BIT-EXACT (corr_strong N512 p2/p8, corr_strong N1024
    p2, corr_mild N256 p2/p8): MATCH=True on every ladder point.
  - Full geomean aggregation reproduces EXACT: corr_lift_geo 3.2452; per_dist {mild 6.7396,
    mod 3.1162, strong 1.6272}; iid pos-control 5.4846 (>=1.5 pass). base_floored corr_strong|N256
    correctly excluded from geomean.
  - Scramble controls fire on FULL across ALL 3 seeds: worst scramble_recall 0.0078, best_intact
    0.71-1.0; scramble_collapses=True. Positive control (iid 5.48x) fires.

DISPOSITION: CONFIRM the lift is REAL and reproduces, controls fire -- BUT with THREE load-bearing
DOWNWARD framing corrections that make the deployed claim narrower than the raw headline, so this
is banked as a MEASURED_MECHANISM (proven capacity mechanism/bound), not an unqualified 3.25x win:

  (1) THE LIFT IS IN RECONSTRUCTION *FIDELITY*, NOT RETRIEVAL ACCURACY. Adversarial probe of the
      success criterion (argmax-NN AND recon_cos>=0.80) vs a pure-argmax-only criterion:
        corr_mild N256 a=1.0: GATE p2=0.008 p8=0.961 (gate-gain +0.953) BUT
                              ARGMAX-ONLY p2=0.945 p8=0.961 (argmax-gain +0.016).
        corr_mod N256 a=1.0:  GATE p2=0.168 p8=0.883 BUT ARGMAX-ONLY p2=0.824 p8=0.898 (+0.074).
        corr_strong N512 a=1.0: GATE p2=0.896 p8=0.947 BUT ARGMAX-ONLY p2=0.926 p8=0.947 (+0.021).
      The pairwise baseline ALREADY finds the correct nearest neighbor at nearly the same rate as
      super-quad (argmax gain only +0.01..+0.07); its reconstruction p_hat is just too BLURRY to
      clear the cosine>=0.80 fidelity gate. The ~3.25x lift lives entirely in reconstruction
      SHARPNESS/fidelity, exactly as modern-Hopfield theory predicts. This is DISCLOSED in the
      prereg ("a pure 1-NN score readout is n-invariant; F's ONLY lever is sharpening"). NOT gamed
      (the scramble control -- same weight-magnitude multiset, ranking destroyed -- collapses to
      ~0.001), and fidelity IS the deployment-relevant metric for a glass-box readout that must emit
      a clean vector for downstream unbind/compose. But the claim MUST be scoped as "faithful-
      RECONSTRUCTION capacity", NOT "retrieval/identification capacity" (which is ~n-invariant here).

  (2) THE HEADLINE IS CENSOR-DEFLATED (conservative), AND THE LIFT VANISHES AT LARGE N. The crossing-
      alpha metric is capped at ALPHA_MAX=4.0 / M_CAP=6144. At N>=1024 for corr_mod/strong and at
      N=2048 for ALL strata, BOTH arms saturate the ceiling -> per-cell lift=1.0. Those 1.0 cells
      are (correctly, since base is not floored) INCLUDED in the geomean and drag it DOWN -- so the
      3.25x is a LOWER bound w.r.t. censoring, not an inflation (refutes refutation-target #1: the
      censoring compresses ratios TOWARD 1.0, it does not inflate them). Consequence: the measurable
      lift is a SMALL-to-MID-N phenomenon; at the largest tested N (2048) there is NO resolvable lift
      on any correlated stratum. Deploying at large N would require raising M_CAP just to MEASURE a lift.

  (3) STRONG-CORR 1.63x RESTS ON A SINGLE CLEAN CELL. corr_strong_lift 1.6272 = geomean of
      {N256 EXCLUDED (base floored), N512=4.309, N1024=1.0 (both arms ceiling-censored), N2048=1.0
      (both arms ceiling-censored)} = geomean(4.309, 1.0, 1.0) = 1.627. Only ONE cell (N512) carries
      real separation signal; the "1.63x in every stratum, above the 1.5x bar" survives arithmetically
      but is FRAGILE -- it is one clean cell plus two unresolved ceiling-saturated cells, not a robust
      across-N strong-correlation survival.

SCOPE HONESTY (refutation-target #5, CONFIRMED): this is a CAPACITY-METRIC result (recoverable-
pattern crossing-load alpha* on synthetic iid/correlated codes), NOT an end-task held-out-entity
MRR gain. The cell explicitly does NOT reproduce the 0.128 inference number nor the MONO_MATCHED
MRR 0.466 (cited as a SEPARATE harness). The correlated codes are subspace-confined synthetic codes
(d_sub const across N), a mechanism-analog of the substrate's correlation regime -- NOT the live
substrate KGStore. Codes + ingest UNCHANGED; only the readout nonlinearity varied.

TIER: CONFIRM (lift real, reproduces bit-exact, controls fire, positive control fires) banked as
MEASURED_MECHANISM (proven capacity mechanism with fidelity-scope + censor-deflation + small-N +
capacity-metric bounds). cert_increment_delta=1 (a proven capacity-mechanism boundary; the #1
Phase-2 lever is REAL but correctly scoped). No new META (application of existing disciplines:
censoring-robust capacity, telemetry-sensitive discriminator via scramble, positive-control-clears-
own-floor via iid).

Writes: 1 math atom (MEASURED_MECHANISM) + 1 cert_ledger row. needs_orchestrator_store_sync=True.
A5 protocol: read -> build -> tmp write + fsync -> os.replace -> re-read + verify count delta +
tail round-trip ID match. Abort on any mismatch (originals untouched pre-replace).
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
ATOMIZED_BY = "skunkworks_landed_vet_dense_hopfield_readout_capacity_correlated_2026-07-13"
ATOMIZED_DATE = "2026-07-13"

ANCHOR = "dense_hopfield_readout_capacity_correlated_codes_v1"
METRICS = "data/exp_dense_hopfield_readout_capacity_correlated_codes_v1/metrics.json"
CELL_COMMIT = "3fa59f6b4"
STORE_HEAD_AT_WRITE = "d149e6bb2"

atom = {
    "id": ("math::MEASURED_MECHANISM_dense_modern_Hopfield_super_quadratic_READOUT_lifts_FAITHFUL_RECONSTRUCTION_"
           "capacity_on_CORRELATED_codes_corr_lift_geo_3p25x_over_pairwise_reproduced_BIT_EXACT_off_disk_iid_pos_"
           "control_5p48x_scramble_collapses_0p008_all_3seeds_BUT_THE_LIFT_IS_IN_RECONSTRUCTION_FIDELITY_cosine_ge_"
           "0p80_NOT_retrieval_argmax_which_is_n_INVARIANT_pairwise_ALREADY_finds_correct_NN_argmax_gain_only_plus_"
           "0p01_to_0p07_vs_gate_gain_plus_0p63_to_0p95_AND_the_3p25x_is_CENSOR_DEFLATED_conservative_both_arms_"
           "saturate_M_CAP_6144_at_large_N_lift_vanishes_to_1p0_at_N2048_all_strata_AND_strong_corr_1p63x_rests_on_a_"
           "SINGLE_clean_cell_N512_4p31x_geomean_with_two_ceiling_saturated_1p0_cells_CAPACITY_METRIC_synthetic_codes_"
           "NOT_end_task_MRR_0p128_codes_and_ingest_UNCHANGED_only_readout_nonlinearity_varied_3seed_7_13_19_FULL_2026-07-13"),
    "name": ("MATH MEASURED_MECHANISM (CONFIRM with 3 downward framing corrections): a dense / modern-Hopfield "
             "super-quadratic READOUT (F(x)=relu(x)^n, n=4/8, plus exp(25x)) lifts FAITHFUL-RECONSTRUCTION capacity "
             "~3.25x over the pairwise (n=2) readout on the substrate's synthetic CORRELATED codes -- reproduced "
             "BIT-EXACT off-disk. corr_lift_geo 3.2452 (per-dist mild 6.7396 / mod 3.1162 / strong 1.6272); iid "
             "positive-control 5.4846x (>=1.5 pass); scramble collapses to 0.008 across ALL 3 seeds (intact 0.71-1.0). "
             "CORRECTION 1 (the load-bearing one): the lift is in reconstruction FIDELITY (recon cosine>=0.80), NOT "
             "retrieval accuracy. The success gate is (argmax-NN==target AND recon_cos>=0.80); adversarial probe vs "
             "pure-argmax-only shows the pairwise baseline ALREADY finds the correct nearest neighbor at nearly the "
             "same rate (argmax-gain only +0.01..+0.07) -- its p_hat is just too BLURRY to clear the 0.80 fidelity "
             "gate (gate-gain +0.63..+0.95). The lift lives entirely in reconstruction SHARPNESS, exactly as modern-"
             "Hopfield theory predicts and as the prereg DISCLOSES ('a pure 1-NN readout is n-invariant'). Not gamed "
             "(scramble control collapses). Scope as faithful-RECONSTRUCTION capacity, NOT identification capacity. "
             "CORRECTION 2: the 3.25x is CENSOR-DEFLATED (conservative, refuting the inflation worry) -- both arms "
             "saturate M_CAP=6144/alpha=4 at large N, so per-cell lift->1.0 drags the geomean DOWN; the lift is a "
             "small-to-mid-N phenomenon and VANISHES to 1.0 on ALL strata at N=2048. CORRECTION 3: strong-corr 1.63x "
             "rests on a SINGLE clean cell (N512=4.31x) geomean'd with two ceiling-saturated 1.0 cells -- fragile, not "
             "a robust across-N survival. SCOPE: capacity-metric on synthetic subspace-confined codes, NOT the 0.128 "
             "end-task MRR nor the live KGStore. Codes+ingest UNCHANGED; only the readout nonlinearity varied. "
             "3 seeds [7,13,19] FULL."),
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "kind": "experiment_landed_vet",
    "cert_status": ("confirmed_measured_mechanism_dense_super_quadratic_readout_lifts_faithful_reconstruction_capacity_"
                    "on_correlated_codes_reproduced_bit_exact_controls_fire_but_lift_is_fidelity_not_retrieval_censor_"
                    "deflated_small_N_dominated_strong_corr_single_cell_capacity_metric_not_end_task"),
    "cert_class": ("crossing_load_alpha_star_capacity_lift_super_quadratic_vs_pairwise_readout_iid_and_correlated_codes_"
                   "faithful_reconstruction_fidelity_gate_not_argmax_retrieval"),
    "description": (
        "Independent adversarial off-disk recompute (.venv). Reimplemented the readout (make_codes / make_queries / "
        "_separation_weights / dense_readout_recall / crossing-alpha) FROM SCRATCH (NOT imported from the cell, NOT "
        "from verdict_msg; Fix #28) and re-ran the deterministic (RandomState(seed*100003+m)) pipeline.\n\n"
        "RAW DATA REPRODUCES BIT-EXACT: 5 spot-checked recall curves match on every ladder point (corr_strong|N512|"
        "poly2|s7, corr_strong|N512|poly8|s7, corr_strong|N1024|poly2|s7, corr_mild|N256|poly2|s7, corr_mild|N256|"
        "poly8|s7) -- MATCH=True all. AGGREGATION REPRODUCES EXACT: independent geomean over stored alpha* gives "
        "corr_lift_geo 3.2452, per_dist {corr_mild 6.7396, corr_mod 3.1162, corr_strong 1.6272}, iid 5.4846 -- "
        "identical to the stored headline. base_floored corr_strong|N256 is correctly EXCLUDED (poly2 floors 2/3 seeds).\n\n"
        "CONTROLS FIRE ON FULL, ALL 3 SEEDS (refutation-target #3 CONFIRMED): scramble (row-permute weights, preserving "
        "the weight-magnitude multiset but destroying the similarity ranking) collapses to worst 0.0078 / mean ~0.001-"
        "0.003 across every dist x N x seed; best_intact 0.71 (corr_strong N256) to 1.0; scramble_collapses=True. iid "
        "positive control 5.48x >= 1.5 (readout not broken / regime not saturated).\n\n"
        "REFUTATION-TARGET #2 (fidelity metric fair or gamed?) -- the DECISIVE finding. The success criterion is "
        "(argmax-NN==target AND recon_cos>=RECON_TAU 0.80). Adversarial probe comparing the gated metric vs a pure-"
        "argmax-only metric (drop the recon_tau gate):\n"
        "  corr_mild N256 a=0.5: GATE p2=0.227 p8=0.969 | ARGMAX p2=0.984 p8=0.969 (argmax-gain -0.016)\n"
        "  corr_mild N256 a=1.0: GATE p2=0.008 p8=0.961 | ARGMAX p2=0.945 p8=0.961 (argmax-gain +0.016)\n"
        "  corr_mild N256 a=2.0: GATE p2=0.000 p8=0.926 | ARGMAX p2=0.920 p8=0.959 (argmax-gain +0.039)\n"
        "  corr_mod  N256 a=1.0: GATE p2=0.168 p8=0.883 | ARGMAX p2=0.824 p8=0.898 (argmax-gain +0.074)\n"
        "  corr_strong N512 a=1.0: GATE p2=0.896 p8=0.947 | ARGMAX p2=0.926 p8=0.947 (argmax-gain +0.021)\n"
        "=> The pairwise baseline ALREADY retrieves the correct nearest neighbor at nearly the same rate as super-quad "
        "(argmax gain only +0.01..+0.07, occasionally negative); its reconstruction p_hat is merely too BLURRY to clear "
        "the cosine>=0.80 gate. The ~3.25x 'capacity lift' lives ENTIRELY in reconstruction FIDELITY/sharpness, NOT in "
        "which pattern is identified (argmax is ~n-invariant here). This is HONESTLY DISCLOSED in the prereg. It is NOT "
        "a gamed artifact (the scramble control with identical weight magnitudes collapses to ~0.001), and fidelity is "
        "the deployment-relevant metric for a glass-box readout that must emit a clean vector for downstream unbind/"
        "compose. But the claim MUST be scoped as faithful-RECONSTRUCTION capacity, not identification/retrieval "
        "capacity.\n\n"
        "REFUTATION-TARGET #1 (censoring/floor artifact inflating the ratio?) -- REFUTED, and REVERSED. The crossing-"
        "alpha is capped at ALPHA_MAX=4.0 / M_CAP=6144. At N>=1024 (corr_mod/strong) and N=2048 (all strata) BOTH arms "
        "stay above RECALL_THRESH through the whole ladder -> both censored -> per-cell lift=1.0. These 1.0 cells are "
        "INCLUDED in the geomean (base not floored) and drag it DOWN. So censoring COMPRESSES the ratio toward 1.0 (a "
        "conservative lower bound), it does NOT inflate it. base_floored cells (where pairwise fails even at min load) "
        "ARE excluded (clean_only), so floored baselines cannot inflate either. Consequence: the resolvable lift is a "
        "small-to-mid-N effect; at N=2048 there is NO measurable lift on any correlated stratum (all 1.0).\n\n"
        "REFUTATION-TARGET #4 (strong-corr 1.63x real or noise?) -- REAL at N512 but FRAGILE across N. "
        "corr_strong_lift 1.6272 = geomean{N256 EXCLUDED (base floored), N512=4.309, N1024=1.0 (both ceiling-censored), "
        "N2048=1.0 (both ceiling-censored)} = geomean(4.309,1.0,1.0). Only the single N512 cell carries separation "
        "signal (poly8 alpha* per-seed [1.668,1.616,1.320] vs poly2 [0.288,0.414,0.366]); the '>=1.5x in every stratum' "
        "claim survives arithmetically but rests on one clean cell plus two unresolved saturated cells.\n\n"
        "REFUTATION-TARGET #5 (scope) -- CONFIRMED capacity-metric. Measures recoverable-pattern crossing-load alpha* "
        "on SYNTHETIC iid / subspace-confined correlated codes (d_sub const across N: mild 64, mod 24, strong 12). "
        "Does NOT reproduce the 0.128 held-out-entity inference MRR nor the cited MONO_MATCHED MRR 0.466 (a separate "
        "harness). Correlated codes are a mechanism-analog of the substrate's correlation regime, NOT the live KGStore "
        "(substrate knows nothing; this is a supervised synthetic-code capacity probe). Codes + ingest UNCHANGED; only "
        "the readout nonlinearity varied -- so any lift transfers to deployment ONLY as a readout swap, and only for "
        "the faithful-reconstruction objective.\n\n"
        "TIER: CONFIRM the lift is REAL, reproduces bit-exact, and controls fire; banked as MEASURED_MECHANISM (proven "
        "capacity mechanism/bound) because the deployed claim is narrower than the raw '3.25x recoverable capacity, "
        "deployable >=1.5x in every stratum' framing on three axes (fidelity-not-retrieval; censor-deflated / vanishes "
        "at large N; strong-corr = one cell). cert_increment_delta=1 (the #1 Phase-2 lever is a REAL, proven capacity "
        "mechanism -- correctly scoped). REVIVAL / NEXT: (a) raise M_CAP to resolve whether the lift survives at large "
        "N or is purely a small-N / high-load-relative-to-ceiling effect; (b) test the readout swap on the LIVE "
        "substrate readout path (KGStore cleanup) on the faithful-reconstruction objective; (c) quantify how much a "
        "sharper (higher-fidelity) p_hat actually improves a DOWNSTREAM unbind/compose end-task -- the only path from "
        "this capacity-metric win to an end-task MRR gain."
    ),
    "aliases": [
        "dense modern-Hopfield super-quadratic readout lifts faithful-reconstruction capacity 3.25x on correlated codes reproduced bit-exact",
        "the capacity lift is in reconstruction fidelity cosine>=0.80 not retrieval argmax which is n-invariant pairwise already finds correct NN",
        "3.25x is censor-deflated conservative both arms saturate M_CAP at large N lift vanishes to 1.0 at N2048 all strata",
        "strong-corr 1.63x rests on a single clean cell N512 4.31x geomean with two ceiling-saturated 1.0 cells fragile",
        "capacity-metric on synthetic correlated codes not end-task MRR 0.128 codes and ingest unchanged only readout nonlinearity varied",
    ],
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_CONFIRM_capacity_lift_real_reproduced_bit_exact_controls_fire_three_downward_scope_corrections",
        "cert_status": "confirmed_measured_mechanism_lift_real_but_fidelity_scoped_censor_deflated_small_N_dominated_capacity_metric",
        "cert_class": "crossing_load_alpha_star_capacity_lift_super_quadratic_vs_pairwise_readout_faithful_reconstruction_fidelity_gate",
        "verdict_cell": "HARD_PASS_CAPACITY_LIFT_REAL",
        "verdict_scored_correctly": True,
        "skunkworks_adjudication": "CONFIRM_lift_real_reproduces_controls_fire_banked_MEASURED_MECHANISM_with_fidelity_and_censor_and_smallN_and_capacity_metric_scope_corrections",
        "anchor": ANCHOR,
        "cell_commit": CELL_COMMIT,
        "store_head_at_write": STORE_HEAD_AT_WRITE,
        "metrics_path": METRICS,
        "verified_off_data": (
            "Reimplemented readout+codegen from scratch (.venv, NOT imported from cell, NOT from verdict_msg; Fix #28). "
            "5 recall curves reproduce BIT-EXACT (corr_strong N512 p2/p8, corr_strong N1024 p2, corr_mild N256 p2/p8, "
            "MATCH=True). Geomean aggregation reproduces EXACT: corr_lift_geo 3.2452, per_dist {6.7396,3.1162,1.6272}, "
            "iid 5.4846. Fidelity-gate vs pure-argmax probe: corr_mild N256 a=1.0 GATE p2=0.008 p8=0.961 but ARGMAX "
            "p2=0.945 p8=0.961 (argmax-gain +0.016); corr_mod N256 a=1.0 argmax-gain +0.074; corr_strong N512 a=1.0 "
            "argmax-gain +0.021 -> argmax ~n-invariant, lift is fidelity. Censoring: N2048 all strata lift=1.0 "
            "(both arms M_CAP=6144 saturated), N1024 mod/strong 1.0 -> geomean deflated toward 1.0 (conservative). "
            "strong-corr 1.6272=geomean(N512 4.309, N1024 1.0, N2048 1.0); N256 excluded (base floored). Scramble "
            "worst 0.0078 / intact 0.71-1.0 all 3 seeds. Cross-arc overlap check (substrate_query): top hits are "
            "research NOTES (cosine <=0.328: 'Modern Hopfield capacity rescue' candidate note, correlated-key-capacity "
            "note) = the HYPOTHESIS lineage this cell TESTS, NOT prior certified experiment atoms -> genuine first "
            "experimental measurement, not a rediscovery."
        ),
        "honest_scope": (
            "CONFIRMS a REAL, reproduced, control-clean capacity lift of a super-quadratic readout over pairwise on "
            "synthetic correlated codes, but scoped as: (1) FAITHFUL-RECONSTRUCTION capacity (cosine>=0.80), NOT "
            "retrieval/identification (argmax ~n-invariant, +0.01..+0.07); (2) CONSERVATIVE / censor-deflated, "
            "resolvable only at small-to-mid N -- vanishes to 1.0 at N=2048 all strata; (3) strong-corr survival rests "
            "on a single clean cell (N512); (4) a CAPACITY-METRIC on synthetic codes, NOT the 0.128 end-task MRR nor "
            "the live KGStore. Transfers to deployment only as a readout swap for the faithful-reconstruction objective."
        ),
        "n_seeds": 3, "seeds": [7, 13, 19],
        "run_mode": "full", "expected_n_units": 192, "n_units": 192, "cardinality_ok": True,
        "metrics": {
            "corr_lift_geo": 3.2452,
            "corr_lift_per_dist": {"corr_mild": 6.7396, "corr_mod": 3.1162, "corr_strong": 1.6272},
            "iid_lift_geo_pos_control": 5.4846,
            "hp_lift_bar": 1.50, "hf_lift_bar": 1.15, "pos_control_iid_lift_bar": 1.50,
            "worst_scramble_recall": 0.0078, "best_intact_recall": 0.7109, "scramble_collapses": True,
            "pos_control_iid_passes": True,
            "reproduced_bit_exact_curves": 5,
            "argmax_gain_range_super_minus_pairwise": [-0.016, 0.074],
            "gate_gain_range_super_minus_pairwise": [0.033, 0.953],
            "corr_strong_per_cell_lift": {"N256": "EXCLUDED_base_floored", "N512": 4.309, "N1024": 1.0, "N2048": 1.0},
            "iid_per_cell_lift": {"N256": 19.136, "N512": 7.779, "N1024": 3.837, "N2048": 1.584},
            "corr_mild_per_cell_lift": {"N256": 19.719, "N512": 14.153, "N1024": 7.393, "N2048": 1.0},
            "corr_mod_per_cell_lift": {"N256": 6.748, "N512": 13.973, "N1024": 1.0, "N2048": 1.0},
            "m_cap": 6144, "alpha_max": 4.0, "recon_tau": 0.80, "recall_thresh": 0.90, "cos_target": 0.25,
        },
        "lift_is_reconstruction_fidelity_not_retrieval_argmax_n_invariant": True,
        "headline_censor_deflated_conservative_not_inflated": True,
        "lift_vanishes_at_large_N_all_strata_1p0_at_N2048": True,
        "strong_corr_1p63x_rests_on_single_clean_cell_N512": True,
        "controls_fire_all_3_seeds_scramble_collapses": True,
        "positive_control_iid_fires_readout_not_broken": True,
        "capacity_metric_synthetic_codes_not_end_task_MRR_not_live_kgstore": True,
        "codes_and_ingest_unchanged_only_readout_nonlinearity_varied": True,
        "revival_criteria": [
            "raise_M_CAP_to_resolve_whether_lift_survives_at_large_N_or_is_purely_small_N_ceiling_relative_effect",
            "test_readout_swap_on_live_substrate_KGStore_cleanup_faithful_reconstruction_objective",
            "quantify_downstream_unbind_compose_end_task_gain_from_sharper_higher_fidelity_p_hat_path_to_MRR",
        ],
        "composes_with": [
            "notes::Candidate_A_Modern_Hopfield_capacity_rescue_60pct_confidence (hypothesis lineage this cell TESTS)",
            "reference::crt_residue_helps_clean_encoding_hurts_noisy_readout (readout-regime taxonomy)",
            "reference::correlation_hurts_associative_store_capacity_decouple_from_retrieval (correlated-code capacity)",
        ],
        "cites": [
            "Fix_28_verify_per_arm_metrics_not_verdict_msg",
            "symmetric_anti_negativity_verify_both_directions_USER",
            "feedback_discriminator_must_be_telemetry_sensitive_not_analytically_pinned",
            "feedback_construction_proof_is_not_a_capability_win_ask_could_it_fail_informatively",
            "feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime",
            "substrate_kb_concept_overlap_check_on_schema_vet_USER_locked_2026-07-01",
        ],
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "needs_orchestrator_store_sync": True,
    },
}

ts = time.time()
_iso = datetime.now(timezone.utc).isoformat()
atom["ts_iso"] = _iso
atom["ts"] = ts

ledger = {
    "op": "cert_ruling",
    "ts_iso": _iso,
    "ts": ts,
    "atom_id": atom["id"],
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": atom["cert_status"],
    "cert_class": atom["cert_class"],
    "anchor": ANCHOR,
    "cell_commit": CELL_COMMIT,
    "store_head_at_write": STORE_HEAD_AT_WRITE,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": ATOMIZED_BY,
    "verdict": ("CAPACITY_LIFT_REAL_CONFIRMED_reproduced_bit_exact_controls_fire_but_lift_is_reconstruction_FIDELITY_"
                "not_retrieval_argmax_n_invariant_censor_deflated_vanishes_at_large_N_strong_corr_single_cell_capacity_"
                "metric_not_end_task"),
    "cert_increment_delta": 1,
    "cv": {"corr_lift_geo_reproduced_exact": 0.0, "corr_strong_N512_alpha_star_crossseed": 0.10},
    "decision": (
        "CONFIRM (banked MEASURED_MECHANISM). The dense/super-quad readout capacity lift is REAL: raw recall curves "
        "reproduce BIT-EXACT off independent reimplementation, geomean aggregation reproduces exact (corr 3.2452, iid "
        "5.4846), scramble collapses to 0.008 across all 3 seeds, positive control fires. THREE downward corrections "
        "make it narrower than the raw headline: (1) the lift is in reconstruction FIDELITY (cosine>=0.80) not "
        "retrieval -- pure-argmax accuracy is ~n-invariant (baseline already finds correct NN, argmax-gain +0.01..+0.07 "
        "vs gate-gain +0.63..+0.95); (2) the 3.25x is CENSOR-DEFLATED / conservative (both arms saturate M_CAP=6144 at "
        "large N, lift->1.0; vanishes at N=2048 all strata) -- refutes the inflation worry, reverses it; (3) strong-corr "
        "1.63x = geomean(N512 4.31, two ceiling-saturated 1.0) rests on one clean cell. Scope: capacity-metric on "
        "synthetic correlated codes, NOT end-task MRR 0.128, NOT live KGStore; codes+ingest unchanged, readout swap only."
    ),
    "framing_correction_vs_director": (
        "CLAIMED HARD_PASS / 'CAPACITY_LIFT_REAL 3.25x, deployable >=1.5x in EVERY correlation stratum' is CONFIRMED as "
        "a real reproduced lift, but must be re-scoped on THREE axes before treating it as the deployable Phase-2 win: "
        "(A) it is FAITHFUL-RECONSTRUCTION capacity, NOT retrieval/identification capacity -- the pairwise readout "
        "already identifies the right pattern at ~the same rate; super-quad only makes p_hat sharp enough to clear the "
        "0.80 fidelity gate. (B) '>=1.5x in every stratum' is arithmetically true but the strong-corr 1.63x rests on a "
        "SINGLE clean cell (N512); the other two strong-corr cells are ceiling-saturated (both arms=M_CAP) and the lift "
        "VANISHES to 1.0 on every stratum at N=2048 -- the effect is small-to-mid-N, censor-deflated (conservative). "
        "(C) capacity-metric on synthetic codes, NOT the 0.128 end-task MRR. The refutation-target worry that censoring "
        "INFLATES the ratio is REFUTED and reversed: censoring compresses toward 1.0."
    ),
    "net_cert_delta": "+1 (proven capacity MECHANISM: super-quad readout lifts faithful-reconstruction capacity on correlated codes, correctly scoped; NOT an end-task MRR gain).",
    "needs_orchestrator_store_sync": True,
    "referent_pointer": {"metrics_path": METRICS, "atom_qualified_id": atom["id"]},
}


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
    print("=== A5 atom-write: dense-Hopfield readout capacity lift MEASURED_MECHANISM (2026-07-13) ===")
    print("ts_iso =", _iso)
    print()
    print("Writing 1 atom to math/atoms.jsonl ...")
    pre, post, ok, err = write_atomic_append(MATH_ATOMS, [atom])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: math atoms write failed"); sys.exit(1)

    print("Writing 1 row to meta/cert_ledger.jsonl ...")
    pre, post, ok, err = write_atomic_append(CERT_LEDGER, [ledger])
    print("  pre=%d post=%d ok=%s err=%s" % (pre, post, ok, err))
    if not ok or post - pre != 1:
        print("ABORT: cert_ledger write failed"); sys.exit(1)

    print()
    print("=== A5 WRITE COMPLETE ===")
    for p in (MATH_ATOMS, CERT_LEDGER):
        with open(p, "rb") as f:
            n = f.read().count(b"\n")
        print("  %s: %d lines" % (p.name, n))
    print()
    print("CERT N delta: +1 MEASURED_MECHANISM (proven capacity mechanism, correctly scoped). No new META.")
    print("needs_orchestrator_store_sync = True")
    print("atom_id =", atom["id"][:90], "...")


if __name__ == "__main__":
    main()
