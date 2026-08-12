"""
A5-gated atomization: exp_attention_salience_reliability_gate_independent_channel_v1 (committed 7c44f5da9)
-> ONE atom (2026-07-20). CHAIN_GRADE.

CHAIN-GRADE CANDIDATE (author verdict HARD_PASS) -> HARDEST scrutiny (first self-monitoring capability of the
session). Auditor GRANTS CHAIN_GRADE scoped to the synthetic multi-source regime: a DERIVED, INDEPENDENT,
LEAK-FREE source-reliability channel genuinely helps a non-ceiling task and survives every decisive adversarial
check -- most importantly the leakage killer, which the predecessor v1 (29372) FAILED (injected AUC-0.999
proxy). This is the genuine advance: v1 INJECTED the signal; derived_v1 (29374) DERIVED it via same-item peer
consistency but starved on singletons; THIS cell DERIVES it via source-level cross-item track record and it is
leak-free, independent, and helpful.

INDEPENDENT RECOMPUTE (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28):
  BASE reproduced BIT-EXACT by re-running the committed cell: auc_unrel_mean=0.6764, mean_delta_hard_unrel=
    +0.0634 (per-seed +0.064/+0.066/+0.0675/+0.062/+0.0575), mean_delta_mult_unrel=+0.0837, shuffled_hard max
    delta=-0.1550, do-no-harm mean_delta_hard_rel=+0.0130, ungated_rel per-seed 0.8605-0.8778 (<0.97),
    ungated_unrel 0.536-0.558 (in-band). Verdict HARD_PASS. All match metrics.json exactly.
  Q1 LEAKAGE / CONSTRUCTION (THE KILLER) -- rebuilt seed-7 data independently and probed the channel:
    (a) indep_score AUC vs correctness on the unrel subset = 0.6859 (matches). SOURCE-TIER ORACLE
        (use ground-truth p_source[src] as predictor) = 0.6980. So the DERIVED channel AUC sits BELOW the
        source-tier oracle it is trying to estimate -- decisive proof it is a genuine, slightly-imperfect
        estimate, NOT an inflated proxy leak. (v1's failure was AUC 0.999 >> oracle; here 0.686 < 0.698.)
    (b) Confirmed BELOW-ORACLE on ALL 5 seeds: gap indep-minus-oracle = -0.0121/-0.0187/-0.0275/-0.0173/
        -0.0201. Cannot exceed the oracle => structurally impossible to be a same-item proxy in disguise.
    (c) WITHIN-SOURCE indep AUC vs correctness = 0.1152 (mean over sources; 0.50=no leak). It is <0.50
        (ANTI-leak): within a fixed source, correct obs get SLIGHTLY LOWER indep_score because their own high
        loo is subtracted (leave-one-out is conservative). Zero same-item leak past source identity.
    (d) indep_score is essentially CONSTANT per source: within-source std 0.00016 vs between-source std 0.170
        (ratio 0.001). The channel IS the source track record and nothing else. Residual same-item
        contamination (other obs of item i from the same source, NOT excluded by the loo[j] subtraction) =
        ~1/1997 of the aggregate = negligible; 48% of items have a duplicate source but the effect is 0.05%.
    (e) The raw same-item loo signal (derived_v1's channel) has AUC 0.884; if any same-item leak reached the
        weight, indep_score AUC would climb toward 0.884. It sits at 0.686 (BELOW even the source-tier oracle)
        => no same-item leak. Decisive.
  Q2 CONTROL / SUBSET / DO-NO-HARM: shuffled_hard fires at FULL scale on all 5 seeds (-0.155 to -0.177);
    shuffled permutes indep_score WITHIN item so the observation<->source-estimate correspondence is
    load-bearing. The unrel subset is a-priori 50% of items (tier assigned BEFORE data), NOT cherry-picked.
    Do-no-harm NON-VACUOUS: ungated_rel 0.8605-0.8778 all clearly <0.97 (margin ~0.10, verified off-disk),
    and hard_gate actually HELPS the rel tier (+0.013). Captures ~21% of the oracle headroom (0.063/0.294).
  Q3 MID-FLIGHT REDESIGN: the all-one-tier->no-op degeneration and the fix to heterogeneous per-item sourcing
    (MIX_MAJ=0.75) is MECHANISM-NECESSARY (without within-item source heterogeneity TAU sits between tiers and
    all unrel weights hit zero -> uniform fallback -> no-op) and introduces NO leak (proven by Q1). Dev-sim
    logged before the full run; bands (0.05 floor, AUC 0.55-0.90) are standard and the landed 0.063 clears
    with margin (not suspiciously at-floor).
  Q4 V_PER_TIER SWEEP / REGIME FAIRNESS: reproduced the sweep at seed 7: VPT 100:+0.040, 600:+0.027,
    2500:+0.060, 4000:+0.064. The lift is POSITIVE and ROBUST across population (600-4000), NOT a knife-edge --
    the regime is NOT stacked to a single winning point. AUC approaches the oracle weakly with population
    (gap -0.019@600 -> -0.012@4000), consistent with the Kalman precision story. CAVEAT (framing correction):
    the dev-sim log's CLEAN-MONOTONE "small pop nets NEGATIVE (-0.024 @ VPT=100)" narrative is NOT reproducible
    single-seed -- my VPT=100 seed-7 came back +0.040 POSITIVE. The low-population dev-sim numbers are
    seed-noisy; the "requires large population" scope claim is SOFTER than the log implies (the effect is
    actually robust down to VPT~600). Not a leak or gate failure -- a mechanism-narrative overstatement.
  Q5 REAL BASELINE / ONE VARIABLE / MUST-FAIL: ungated (w=1) is the real default consolidation; hard_gate
    differs only in the weight vector (one variable); shuffled must-fail fires hard. Clean.

TIER: CHAIN_GRADE, scoped to the synthetic multi-source regime. All decisive adversarial checks pass; the
  leakage killer passes CLEAN (the whole ballgame vs v1's injected proxy). This is a genuine DERIVATION win --
  the substrate ESTIMATES source reliability from data (AUC 0.686, below the 0.698 oracle) rather than being
  handed it, escaping both v1's injection and derived_v1's singleton-starvation. LOAD-BEARING SCOPE BOUNDS
  (why this is chain-grade-for-the-mechanism, NOT yet "the self-monitoring layer works on real data"):
  (i) SYNTHETIC regime, construction-supplied source tiers; real-data untested. (ii) The channel's
  informativeness is CONTINGENT on the independent-random-error model (correct obs = exactly true_v so they
  self-agree; wrong obs = i.i.d. random so they don't) -- CORRELATED / systematic source errors (a source
  consistently wrong the same way) would fool a consistency-based track record and are UNTESTED. (iii) modest
  effect (~21% of oracle headroom). CERT delta +1 CG.

LOCAL ONLY: store_head_at_write=unsynced_needs_orchestrator; NO origin push; NO remote persist; no git add -A.
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
ATOMIZED_BY = ("skunkworks_landed_vet_attention_reliability_gate_independent_channel_v1_CG_derived_leakfree_"
               "source_reliability_channel_auc_0p676_below_oracle_0p698_lift_0p063_2026-07-20")
ATOMIZED_DATE = "2026-07-20"
ANCHOR = "attention_salience_reliability_gate_independent_channel_v1"
CELL_COMMIT = "7c44f5da9"

PARENT_V1 = ("math::MEASURED_MECHANISM_attention_salience_reliability_gate_v1_CONSTRUCTION_PROOF_not_capability_"
             "win")  # prefix-match: 29372 injected near-oracle proxy, plumbing validated but construction-determined
PARENT_DERIVED = ("math::HARD_FAIL_NARROW_attention_salience_reliability_gate_DERIVED_v1_leave_one_out_cross_"
                  "observation_cosine_consistency")  # prefix-match: 29374, same-item peer consistency, singleton starvation

_iso = datetime.now(timezone.utc).isoformat()
_ts = time.time()

XARC = (
    "substrate_query 'independent channel reliability estimation source-level cross-item Kalman gain "
    "consolidation gate' (exp_dev prereg-logged) -> top hit generic 'consolidation' lexical node cosine 0.337 "
    "+ two unrelated write-amortization notes-chunks 0.307; NO prior EXPERIMENT-cell atom at cosine>0.30. Direct "
    "lineage is atoms 29372 (v1 construction-proof) and 29374 (derived_v1 narrow HF), a DELIBERATE revival per "
    "29374's own revival_criteria (independent reliability channel), NOT a hidden rediscovery. Auditor accepts."
)

ATOM_ID = (
    "math::CHAIN_GRADE_attention_salience_reliability_gate_INDEPENDENT_CHANNEL_v1_DERIVED_LEAK_FREE_source_level_"
    "leave_one_ITEM_out_reliability_channel_GENUINELY_HELPS_consolidation_on_low_reliability_subset_FIRST_self_"
    "monitoring_DERIVATION_win_of_session_auc_unrel_0p6764_IN_BAND_0p55_to_0p90_reproduced_BIT_EXACT_offdisk_"
    "mean_delta_hard_unrel_plus0p0634_5of5_seeds_positive_064_066_0675_062_0575_soft_mult_plus0p0837_shuffled_"
    "hard_control_neg0p155_to_neg0p177_all5_do_no_harm_POSITIVE_hard_rel_plus0p013_ungated_rel_0p8605_to_0p8778_"
    "all_below_0p97_NON_VACUOUS_ungated_unrel_0p536_to_0p558_in_band_LEAKAGE_KILLER_PASSES_CLEAN_indep_score_AUC_"
    "0p686_sits_BELOW_source_tier_ORACLE_0p698_on_ALL_5_seeds_gap_neg0p012_to_neg0p028_so_STRUCTURALLY_cannot_be_"
    "an_inflated_proxy_within_source_AUC_0p115_ANTI_leak_leave_one_out_conservative_within_source_std_0p0002_vs_"
    "between_0p170_ratio_0p001_channel_IS_source_track_record_raw_same_item_loo_AUC_0p884_would_show_if_leaked_but_"
    "indep_stays_0p686_ESCAPES_derived_v1_atom29374_informative_vs_vacuous_TENSION_and_v1_atom29372_INJECTION_this_"
    "one_DERIVES_the_signal_at_auc_0p686_below_oracle_NOT_handed_it_control_fires_full_scale_unrel_subset_apriori_"
    "50pct_not_cherrypicked_captures_21pct_of_oracle_headroom_0p063_over_0p294_SCOPED_SYNTHETIC_regime_informative_"
    "ness_CONTINGENT_on_INDEPENDENT_RANDOM_ERROR_model_correlated_systematic_errors_UNTESTED_real_data_UNTESTED_"
    "VPT_sweep_lift_robust_600_to_4000_NOT_knife_edge_but_devsim_clean_monotone_small_pop_negative_narrative_NOT_"
    "reproducible_single_seed_VPT100_came_back_plus0p040_LOCAL_ONLY_2026-07-20"
)

PLAIN = (
    "We wanted the substrate to DECIDE FOR ITSELF which of its noisy inputs to trust, and use that to clean up "
    "what it stores -- a first piece of a 'self-monitoring' ability. Two earlier tries failed the honest way: "
    "one was handed the answer (an injected confidence score that was basically an oracle in disguise), and one "
    "tried to judge each input by how well it agreed with its own siblings, which broke whenever an input had no "
    "sibling to check against. This third try WORKS and is honest: it rates each SOURCE by that source's track "
    "record across THOUSANDS of OTHER items (never the item being judged), then trusts inputs from good sources "
    "and down-weights inputs from bad ones. It measurably improves the hard cases (+6.3 points, 5 out of 5 "
    "seeds) without hurting the easy ones, and a shuffled control collapses (-15 points) so the source-to-input "
    "matching is doing the work. The decisive honesty check: the derived trust score is a genuine ESTIMATE, not "
    "a leak -- it is actually slightly WORSE than the true source-quality oracle (0.68 vs 0.70), which is "
    "impossible for a cheat. So this is the first time the substrate DERIVED (not was handed) a useful "
    "reliability signal. The catch: this is a clean synthetic world where wrong inputs are just random noise; "
    "we have NOT tested whether it survives when a source is CONSISTENTLY wrong in the same way, or on real "
    "data. So: real machinery, genuine first self-monitoring win, but proven so far only in the easy synthetic "
    "regime."
)

IMPORTANCE = (
    "HIGH. This is the first GENUINE self-monitoring / derived-reliability capability of the arc -- the substrate "
    "ESTIMATES which inputs to trust from data rather than being handed the answer (v1) or starving on siblings "
    "(derived_v1). It directly answers atom 29374's revival_criteria and the Kalman brain_check, and it is the "
    "first result to break the substrate's recurring 'USES an injected signal it cannot DERIVE' pattern "
    "(29372 / affectedness-MM / CPCL). It unblocks a real reliability-weighted consolidation gate for the "
    "learning-and-self-monitoring layer. Importance is bounded by scope: it is a mechanism/plumbing capability "
    "proven in a synthetic INDEPENDENT-ERROR regime; the load-bearing next question (does it hold under "
    "CORRELATED/systematic source errors and on REAL data) is untested, so it must NOT be over-read as 'the "
    "self-monitoring layer works'."
)

ATOM_CLAIM = (
    "MATH CHAIN_GRADE (scoped to the synthetic multi-source regime). CLAIM: a DERIVED, INDEPENDENT, LEAK-FREE "
    "per-observation reliability channel -- SOURCE-level track record estimated leave-one-ITEM-out from the "
    "same-item consistency of THOUSANDS of OTHER items, never the item being weighted -- genuinely improves "
    "bipolar-sum consolidation on the low-reliability item subset via a hard_gate (w=1[indep_score>=median TAU]) "
    "WITHOUT harming the reliable subset. Reproduced BIT-EXACT off-disk (re-ran committed cell 7c44f5da9): "
    "auc_unrel_mean=0.6764 IN-BAND [0.55,0.90]; mean_delta_hard_unrel=+0.0634 (5/5 seeds positive, +0.058 to "
    "+0.068); soft_multiplier +0.0837; shuffled_hard control -0.155 to -0.177 all 5 seeds; do-no-harm POSITIVE "
    "on the rel tier (+0.013) with ungated_rel 0.8605-0.8778 all NON-CEILING (<0.97, margin ~0.10); ungated_unrel "
    "0.536-0.558 in-band. AUDITOR TIER (CHAIN_GRADE): all decisive adversarial checks pass; the LEAKAGE KILLER "
    "passes CLEAN, which is the whole difference from the predecessor v1 (29372, MM, injected AUC-0.999 proxy): "
    "the derived indep_score AUC (0.6859 seed-7) sits BELOW the ground-truth source-tier ORACLE (0.6980) on ALL "
    "5 seeds (gap -0.012 to -0.028) -- structurally impossible for an inflated proxy; within-source AUC=0.1152 "
    "(ANTI-leak, leave-one-out is conservative); indep_score is constant per source (within/between std ratio "
    "0.001) so the channel IS the source track record; the raw same-item loo signal is AUC 0.884 and indep_score "
    "does NOT climb toward it. This is a genuine DERIVATION win: the substrate ESTIMATES source reliability from "
    "data (0.686, below oracle) rather than being handed it (v1) or starving on same-item singletons (derived_v1, "
    "29374). The unrel subset is a-priori 50% (not cherry-picked); the shuffled control fires at full scale "
    "(observation<->source correspondence is load-bearing); it captures ~21% of the oracle headroom "
    "(0.063/0.294). ESCAPES atom 29374's informative-vs-vacuous tension SIMULTANEOUSLY (informative: AUC 0.676 "
    "interior; non-vacuous: ungated_rel 0.867 << 0.97 ceiling). LOAD-BEARING SCOPE BOUNDS: (i) SYNTHETIC regime, "
    "construction-supplied source tiers, REAL-DATA UNTESTED; (ii) the channel's informativeness is CONTINGENT on "
    "the INDEPENDENT-RANDOM-ERROR model (correct obs = exactly true_v so they self-agree, wrong obs = i.i.d. "
    "random so they don't) -- CORRELATED / systematic source errors would fool a consistency-based track record "
    "and are UNTESTED; (iii) modest effect. FRAMING CORRECTION vs the dev-sim log: the 'small population nets "
    "NEGATIVE (-0.024 @ VPT=100), clean monotone to +0.060 @ 4000' narrative is NOT reproducible single-seed "
    "(VPT=100 seed-7 came back +0.040 POSITIVE); the lift is actually ROBUST across VPT 600-4000, so the "
    "'requires large population' claim is softer than the log implies (not a leak or gate failure)."
)

ATOM_RECOMPUTE = (
    "INDEP recompute (.venv Scripts/python, off-disk, NOT verdict_msg; Fix #28): "
    "(A) BIT-EXACT re-run of committed cell 7c44f5da9: auc_unrel_mean=0.6764 (per-seed 0.6859/0.6777/0.6696/"
    "0.6787/0.6700), mean_delta_hard_unrel=+0.0634 (0.064/0.066/0.0675/0.062/0.0575), mean_delta_mult_unrel="
    "+0.0837, shuffled_hard max delta=-0.1550 (all5 -0.155 to -0.177), mean_delta_hard_rel=+0.0130, "
    "ungated_rel 0.8605/0.8625/0.86475/0.87775/0.871 (<0.97), ungated_unrel 0.53575/0.542/0.54075/0.5585/"
    "0.5435, verdict HARD_PASS. All match metrics.json. "
    "(B) LEAKAGE KILLER -- rebuilt seed-7 data independently: indep_score AUC vs correctness (unrel)=0.6859 "
    "(matches); SOURCE-TIER ORACLE (p_source predictor)=0.6980; source-mean track record AUC=0.7056; raw "
    "same-item loo AUC=0.8840. indep AUC (0.686) < source-tier oracle (0.698) => genuine imperfect estimate, "
    "NOT a proxy. CONFIRMED below-oracle on ALL 5 seeds (gap -0.0121/-0.0187/-0.0275/-0.0173/-0.0201). "
    "(C) WITHIN-SOURCE indep AUC vs correctness = 0.1152 (mean; 0.50=no leak) -> ANTI-leak (leave-one-out "
    "subtracts obs's own high loo). (D) indep_score within-source std=0.00016 vs between-source std=0.170 "
    "(ratio 0.001): channel IS the source track record; residual same-item contamination ~1/1997 (negligible) "
    "though 48% of items have a duplicate source. (E) V_PER_TIER sweep seed-7: 100:+0.040, 600:+0.027, "
    "2500:+0.060, 4000:+0.064 -> lift robust 600-4000 (not knife-edge); AUC->oracle weakly with pop "
    "(gap -0.019@600 -> -0.012@4000). NOTE: dev-sim 'VPT=100 nets -0.024' NOT reproduced (single-seed +0.040). "
    "(F) shuffled fires full-scale (permutes indep WITHIN item, breaks obs<->source correspondence). "
    "unrel subset a-priori 50%. do-no-harm non-vacuous (ungated_rel <0.97, margin ~0.10) and POSITIVE (+0.013). "
    "oracle headroom mean_delta_unrel=+0.294; captured ~21%."
)

ATOM_SCOPE = (
    "Synthetic multi-source consolidation regime: S=20 sources (10 lo P_LO=0.20, 10 hi P_HI=0.65), V=8000 items "
    "(50/50 unrel/rel a-priori tier), N=64 bipolar, n_obs in [4,6], MIX_MAJ=0.75 heterogeneous per-item "
    "sourcing, TAU=per-seed median source score, 5 seeds [7,17,23,31,41]. LOAD-BEARING BOUNDS: "
    "(a) CHAIN-GRADE FOR THE MECHANISM, NOT A REAL-DATA CAPABILITY WIN: the derived leave-one-item-out "
    "source-reliability channel is proven leak-free, independent, and helpful IN THIS SYNTHETIC REGIME. "
    "Real-data (real heterogeneous sources) is UNTESTED -- do not read as 'the self-monitoring layer works'. "
    "(b) INFORMATIVENESS CONTINGENT ON THE ERROR MODEL: the channel works because correct obs = exactly true_v "
    "(self-agree, high same-item cosine) while wrong obs = i.i.d. random bipolar (don't agree). A source's "
    "average same-item consistency therefore tracks its correctness rate. In real data, CORRELATED / systematic "
    "errors (a source consistently wrong in the SAME way) would produce high self-consistency for WRONG obs and "
    "FOOL the track record -- this failure mode is UNTESTED and is the key open capability question. "
    "(c) DERIVED not INJECTED (the genuine advance): AUC 0.686 sits BELOW the 0.698 source-tier oracle, proving "
    "the signal is estimated from data (v1's injected proxy was AUC 0.999 >> oracle). This BREAKS the substrate's "
    "recurring 'USES injected signal it cannot DERIVE' pattern for the first time -- but only under (b). "
    "(d) MODEST EFFECT: captures ~21% of oracle headroom; soft_multiplier (+0.084) actually beat hard_gate "
    "(+0.063) at full run despite being scoped SECONDARY (scale-mismatch argument partly moot at landed scale). "
    "(e) REGIME NOT STACKED but NARRATIVE SOFTER: lift is robust across VPT 600-4000 (not a cherry-picked point), "
    "which STRENGTHENS the result, but the dev-sim's clean-monotone 'small pop negative' story is not "
    "reproducible single-seed (VPT=100 -> +0.040). "
    "BRAIN-CHECK: matches Kalman gain / cue-reliability weighting (Ernst-Banks optimal multisensory integration): "
    "the brain weights a cue by a reliability estimate that is INDEPENDENT of the current measurement being "
    "weighted (accumulated sensor precision), NOT by within-measurement self-consistency. This cell's "
    "source-level cross-item track record is exactly that structure -- brain-faithful. The brain ALSO fails the "
    "same way under correlated cue errors (systematically-biased cues degrade optimal integration), consistent "
    "with bound (b). GREEN-LIGHT / NEXT (revival): (1) CORRELATED-ERROR regime -- the decisive real-world test; "
    "(2) REAL heterogeneous-source data; (3) whether the same channel helps when redundancy is higher / task "
    "is harder. Only then does 'derived reliability-gating is a real capability' upgrade beyond synthetic."
)

ATOM_METRICS = {
    "auc_unrel_mean": 0.6764, "auc_unrel_per_seed": [0.6859, 0.6777, 0.6696, 0.6787, 0.6700],
    "auc_pooled_mean": 0.7124,
    "mean_delta_hard_unrel": 0.0634, "delta_hard_unrel_per_seed": [0.064, 0.066, 0.0675, 0.062, 0.0575],
    "n_pos_hard": 5, "mean_delta_mult_unrel": 0.0837,
    "mean_delta_hard_rel_do_no_harm": 0.0130, "mean_delta_mult_rel": 0.0186,
    "shuffled_hard_max_delta": -0.1550, "shuffled_hard_range": [-0.1765, -0.1550],
    "shuffled_mult_max_delta": -0.0992,
    "ungated_rel_per_seed": [0.8605, 0.8625, 0.86475, 0.87775, 0.871], "ungated_rel_ceiling": 0.97,
    "ungated_unrel_per_seed": [0.53575, 0.542, 0.54075, 0.5585, 0.5435],
    "oracle_mean_delta_unrel": 0.2939, "headroom_captured_fraction": 0.216,
    "LEAKAGE_indep_score_auc_seed7": 0.6859, "LEAKAGE_source_tier_ORACLE_auc_seed7": 0.6980,
    "LEAKAGE_indep_minus_oracle_gap_all_seeds": [-0.0121, -0.0187, -0.0275, -0.0173, -0.0201],
    "LEAKAGE_within_source_auc": 0.1152, "LEAKAGE_raw_same_item_loo_auc": 0.8840,
    "LEAKAGE_indep_within_vs_between_source_std_ratio": 0.001,
    "LEAKAGE_verdict": "PASSES_CLEAN_derived_estimate_below_oracle_no_same_item_leak_NOT_a_proxy",
    "VPT_sweep_seed7_delta": {"100": 0.040, "600": 0.027, "2500": 0.060, "4000": 0.064},
    "VPT_devsim_monotone_narrative": "NOT_reproducible_single_seed_VPT100_came_back_positive_0p040_not_neg0p024",
    "cell_verdict": "HARD_PASS",
    "auditor_tier": ("CHAIN_GRADE scoped to synthetic multi-source regime: derived leak-free independent "
                     "reliability channel genuinely helps non-ceiling task; leakage killer passes clean (AUC "
                     "below oracle); real-data + correlated-error UNTESTED"),
}

COMPOSES = [
    ("SUPERSEDES-in-spirit / RESOLVES the open question of PARENT v1 (" + PARENT_V1 + " ..., atom 29372, "
     "MEASURED_MECHANISM): v1 validated the consolidation-gate PLUMBING but its win was CONSTRUCTION-DETERMINED "
     "because the reliability signal was INJECTED (near-oracle AUC 0.999 proxy), leaving open whether the "
     "substrate can PRODUCE a reliability signal from inputs. THIS cell answers that open Q in the AFFIRMATIVE "
     "for a synthetic multi-source regime: it DERIVES the signal (AUC 0.686, BELOW the 0.698 oracle -- the "
     "opposite of an injected proxy) and it still helps. Does NOT supersede 29372 (different mechanism, and "
     "29372's plumbing-validation stands); it CLOSES 29372's untested real-open-Q for the synthetic/independent-"
     "error case."),
    ("REVIVES + ANSWERS PARENT derived_v1 (" + PARENT_DERIVED + " ..., atom 29374, HARD_FAIL_NARROW): 29374 "
     "proved same-item peer-consistency has NO regime that is both informative and non-vacuous (partner-rich "
     "regimes drive the rel tier to ceiling / AUC out of band), and its revival_criteria + Kalman brain_check "
     "prescribed an INDEPENDENT reliability channel. THIS cell is that channel and it ESCAPES the tension: "
     "informative (AUC 0.676 interior) AND non-vacuous (ungated_rel 0.867 << 0.97) SIMULTANEOUSLY, because the "
     "source-level cross-item aggregate is immune to singleton-true-starvation by construction. Does NOT "
     "supersede 29374 (its narrow-bound-for-same-item-peer-consistency finding stands); it CLOSES 29374's "
     "revival in the affirmative for the independent-channel option it recorded as untested."),
    ("BREAKS (for the first time, conditionally) the substrate's recurring INJECTED-vs-DERIVED boundary: 29372 "
     "(injected reliability), the affectedness-MM (curated affectedness USE-win, text-derivation HARD_FAILED), "
     "CPCL-v2 (injected-vs-derived) all showed 'substrate USES a supplied signal it cannot DERIVE'. THIS is the "
     "first DERIVATION win (source reliability estimated from same-item-consistency track record, AUC below "
     "oracle). IMPORTANT boundary: the derivation succeeds because the synthetic error model is INDEPENDENT-"
     "RANDOM; whether the substrate can derive reliability under CORRELATED errors / on real data is the "
     "untested continuation, so this does not yet fully overturn the pattern."),
    ("credit: Kalman (1960) optimal reliability-weighted estimation; Ernst & Banks (2002) optimal multisensory "
     "integration by cue reliability (the brain_check anchor); the cell AUTHOR (exp_dev) CREDITED for a clean, "
     "honest design -- the leakage-risk was pre-empted structurally (leave-one-item-out), the AUC in-band gate "
     "correctly DISQUALIFIES a >0.90 proxy (v1's failure mode), the shuffled must-fail control and the "
     "non-ceiling-rel do-no-harm gate are both non-vacuous, the pooled-AUC inflation was disclosed and small "
     "(0.712 vs derived_v1's 0.91), the no-op degeneration was logged and fixed mechanistically, and the "
     "primary/secondary split was disclosed with dev-sim numbers in hand. The AUC-below-oracle honesty is what "
     "lets the leakage adjudication land as a clean PASS."),
]

OVER_READS = [
    ("Do NOT read this as 'the self-monitoring layer works' or 'the substrate can derive reliability'. It is "
     "CHAIN-GRADE FOR THE MECHANISM IN A SYNTHETIC REGIME. The channel's informativeness is CONTINGENT on the "
     "independent-random-error construction (correct obs self-agree, wrong obs are random); CORRELATED / "
     "systematic source errors -- the real-world failure mode -- would fool a consistency-based track record and "
     "are UNTESTED. Report as 'derived reliability-gating works in a synthetic independent-error regime', not as "
     "a general capability."),
    ("Do NOT cite the dev-sim log's 'small population nets NEGATIVE (-0.024 @ VPT=100), clean monotone to 4000' "
     "as evidence of a sharp Kalman precision threshold -- it is NOT reproducible single-seed (VPT=100 seed-7 "
     "-> +0.040 POSITIVE). The lift is actually ROBUST across VPT 600-4000. This STRENGTHENS the result "
     "(not a cherry-picked point) while WEAKENING the specific 'requires large population' narrative."),
    ("Do NOT over-weight soft_multiplier's landed +0.0837 (which beat hard_gate's +0.0634 despite being scoped "
     "SECONDARY on a scale-mismatch argument). The scale-mismatch rationale is partly moot at landed scale; "
     "both arms consume the identical channel and both beat their shuffled control, so the headline capability "
     "is the CHANNEL, and hard_gate remains the pre-registered PRIMARY. Effect size is modest either way "
     "(~21% of oracle headroom)."),
    ("Do NOT claim this DEMOTES or overturns 29372 or 29374 -- both parent findings stand on their own "
     "mechanisms (v1 injected-plumbing validation; derived_v1 same-item-peer-consistency narrow bound). This "
     "atom COMPLEMENTS them by closing their recorded revival questions in the affirmative for the independent "
     "channel."),
]

REVIVAL = [
    ("THE decisive next test: a CORRELATED / SYSTEMATIC-ERROR regime -- a source that is consistently wrong in "
     "the SAME way (wrong obs mutually agree). A consistency-based source track record should be FOOLED here "
     "(high self-consistency for wrong obs). If the derived channel still helps under correlated errors, upgrade "
     "toward a real-data capability; if it fails, the bound (b) is confirmed structural and the fix is a "
     "reliability estimate that does not rely on self-consistency (e.g. cross-source agreement / ground-truthed "
     "calibration)."),
    ("REAL heterogeneous-source data: replace the synthetic source-tier construction with genuinely different "
     "real sources (e.g. multiple extractors / annotators / retrieval channels of differing quality) and "
     "re-measure the derived leave-one-item-out track record. This is the untested real capability question."),
    ("HARDER / higher-redundancy regime: the small-redundancy (n_obs 4-6) low-population negative behavior "
     "(derived_v1 + the VPT<=600 softness) suggests the channel pays off only when source track-record precision "
     "exceeds the per-item redundancy-averaging benefit. Map that trade-off (redundancy x population x "
     "reliability-gap) to characterize WHEN independent-channel gating is worth its cost."),
]

GENUINE_POS = (
    "GENUINE positive preserved (symmetric anti-negativity): this is a REAL, leak-free, first-of-session "
    "DERIVATION win and I do NOT dilute it. The decisive leakage killer PASSED CLEAN -- the derived indep_score "
    "AUC (0.686) sits BELOW the ground-truth source-tier oracle (0.698) on ALL 5 seeds, which is structurally "
    "impossible for an inflated proxy; within-source AUC is 0.115 (anti-leak); the channel is provably just the "
    "source track record (within/between std ratio 0.001) with negligible same-item contamination. It "
    "genuinely helps (+0.063 hard 5/5, +0.084 soft, both beating strongly-negative shuffled controls -0.10 to "
    "-0.18), do-no-harm is non-vacuous AND positive (+0.013 on a 0.867<0.97 rel tier), and it captures ~21% of "
    "real oracle headroom. It escapes derived_v1's informative-vs-vacuous tension and, for the FIRST time, "
    "breaks the substrate's 'USES injected signal it cannot DERIVE' pattern -- here it DERIVES the reliability "
    "estimate from data. It is brain-faithful (Kalman / Ernst-Banks reliability weighting from an independent "
    "channel). The author's design is clean and honest (in-band AUC gate that would have DISQUALIFIED a >0.90 "
    "proxy, non-vacuous controls, disclosed pooled-AUC inflation, logged/fixed no-op). What this IS: chain-grade "
    "evidence that a derived, independent, leak-free reliability channel genuinely improves consolidation -- the "
    "first self-monitoring capability of the arc. What it is NOT (the scope that keeps it honest): a real-data "
    "capability, nor robust to correlated/systematic source errors (both UNTESTED); the informativeness is "
    "contingent on the benign independent-random-error construction. The auditor's scoping SHARPENS (synthetic-"
    "regime, error-model-contingent, modest effect, VPT-narrative softened); it does NOT overturn the reality "
    "of the derivation win."
)


def build_atom():
    return {
        "id": ATOM_ID, "name": ATOM_CLAIM, "corpus": "math", "tier": "CHAIN_GRADE",
        "kind": "experiment_landed_vet",
        "cert_status": "chain_grade",
        "cert_class": ("DERIVED_leak_free_independent_source_level_leave_one_item_out_reliability_channel_"
                       "GENUINELY_HELPS_consolidation_low_reliability_subset_auc_0p676_in_band_below_oracle_"
                       "0p698_no_proxy_leak_lift_0p063_5of5_do_no_harm_positive_non_vacuous_FIRST_self_"
                       "monitoring_DERIVATION_win_escapes_29374_tension_breaks_29372_injection_pattern_SCOPED_"
                       "synthetic_independent_error_regime_correlated_error_and_real_data_UNTESTED"),
        "plain_language": PLAIN,
        "importance": IMPORTANCE,
        "description": (ATOM_CLAIM + "\n\nPLAIN LANGUAGE: " + PLAIN + "\n\nRECOMPUTE (off-disk .venv, Fix #28): "
                        + ATOM_RECOMPUTE + "\n\nHONEST SCOPE: " + ATOM_SCOPE),
        "aliases": [
            "attention/salience reliability-gate independent-channel v1 (CHAIN_GRADE)",
            "derived leak-free source-level leave-one-item-out reliability channel genuinely helps",
            "first self-monitoring DERIVATION win: substrate estimates source reliability from data (AUC 0.686 below oracle 0.698)",
            "leakage killer passes clean: derived AUC below source-tier oracle on all 5 seeds (not a proxy)",
            "escapes atom 29374 informative-vs-vacuous tension; breaks atom 29372 injection pattern",
            "SCOPE: synthetic independent-error regime; correlated-error + real-data UNTESTED",
        ],
        "ts_iso": _iso, "ts": _ts,
        "serves_capability": "learning_and_self_monitoring_layer_reliability_weighted_consolidation_gate",
        "metadata": {
            "provenance_quality": ("independent_venv_offdisk_bit_exact_rerun_of_committed_cell_plus_independent_"
                                   "seed7_data_rebuild_leakage_probe_source_tier_oracle_AUC_comparison_all5seeds_"
                                   "plus_within_source_AUC_plus_within_between_std_ratio_plus_VPT_sweep_"
                                   "reproduction"),
            "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes": None,
            "store_head_at_write": "unsynced_needs_orchestrator",
            "metrics_path": "data/exp_attention_salience_reliability_gate_independent_channel_v1/metrics.json",
            "plain_language": PLAIN, "importance": IMPORTANCE,
            "verified_off_data": ATOM_RECOMPUTE, "honest_scope": ATOM_SCOPE, "metrics": ATOM_METRICS,
            "over_reads_corrected": OVER_READS,
            "genuine_positives_symmetric_anti_negativity": GENUINE_POS,
            "revival_criteria": REVIVAL,
            "cross_arc_overlap_check": XARC,
            "leakage_test_result": ("PASSES CLEAN. Derived indep_score AUC=0.6859 (seed7) sits BELOW the "
                                    "ground-truth source-tier ORACLE AUC=0.6980, and below-oracle on ALL 5 seeds "
                                    "(gap -0.012 to -0.028) -> structurally impossible for an inflated proxy. "
                                    "Within-source AUC=0.1152 (ANTI-leak; leave-one-out subtracts the obs's own "
                                    "high loo). indep_score constant per source (within/between std ratio 0.001) "
                                    "= it IS the source track record. Raw same-item loo AUC=0.8840 -> if any "
                                    "same-item leaked, indep would climb toward it; it stays 0.686. NO same-item "
                                    "leak, NOT construction-inflated. Distinct from v1 (29372) whose injected "
                                    "proxy was AUC 0.999 >> oracle."),
            "derived_vs_injected": ("DERIVED (the genuine advance). indep_score is estimated from same-item "
                                    "consistency aggregated by source across the population, leave-one-item-out; "
                                    "the cell never uses p_source in the derivation. AUC 0.686 < 0.698 oracle "
                                    "proves it is a real imperfect estimate. First result to break the "
                                    "substrate's INJECTED-vs-DERIVED boundary -- but only under the synthetic "
                                    "independent-random-error model (correlated errors UNTESTED)."),
            "cites": [
                "Fix_28_verify_off_data_not_verdict_msg",
                "symmetric_anti_negativity_verify_both_directions_USER",
                "cited_number_must_reproduce_from_cell",
                "verify_the_referent_atom_ids_mechanism_metric_regime",
                "ground_by_X_grade_by_X_circularity_leakage_require_independent_blind_or_heldout",
                "construction_proof_not_capability_win_could_it_fail_informatively",
                "synthetic_toy_corpus_outcomes_can_be_construction_determined_real_questions_need_real_data",
                "feedback_strategic_reads_run_ahead_of_evidence_caveat_interpretation_not_just_verdicts",
                "every_negative_and_positive_brain_check_mechanism_vs_shortcut",
                "substrate_kb_concept_overlap_check_on_schema_vet",
                "chain_grade_hardest_scrutiny_before_granting_first_capability_win",
                "revival_of_hard_fail_false_rescue_risk_apply_hardest_scrutiny",
            ],
            "composes_with": COMPOSES,
            "atomized_by": ATOMIZED_BY, "atomized_date": ATOMIZED_DATE,
            "needs_orchestrator_store_sync": True,
            "local_write_only_no_origin_push_no_remote_persist": True,
        },
    }


def ledger_row(atom):
    return {
        "op": "cert_ruling", "corpus": "math", "tier": atom["tier"], "cert_status": atom["cert_status"],
        "anchor": ANCHOR, "cell_commit": CELL_COMMIT, "supersedes_commit": None,
        "supersedes_atom_id": None, "amends_atom_id": None,
        "store_head_at_write": "unsynced_needs_orchestrator", "verified_off_data": True,
        "auditor": "hdi_skunkworks", "atomized_by": ATOMIZED_BY,
        "author_verdict": "HARD_PASS",
        "verdict": ("CHAIN_GRADE_scoped_synthetic_regime_DERIVED_leak_free_independent_source_reliability_channel_"
                    "GENUINELY_HELPS_auc_unrel_0p6764_in_band_lift_hard_0p0634_5of5_LEAKAGE_KILLER_PASSES_CLEAN_"
                    "indep_AUC_0p686_BELOW_source_tier_oracle_0p698_all5seeds_within_source_AUC_0p115_anti_leak_"
                    "NOT_a_proxy_escapes_29374_tension_breaks_29372_injection_pattern_correlated_error_and_real_"
                    "data_UNTESTED"),
        "cert_increment_delta": 1,
        "decision": (
            "CHAIN_GRADE (scoped to synthetic multi-source regime). Author verdict HARD_PASS CONFIRMED. "
            "Chain-grade CANDIDATE + first self-monitoring capability -> hardest scrutiny. Off-disk (.venv, "
            "Fix #28): (1) BIT-EXACT re-run of committed cell 7c44f5da9 -- auc_unrel 0.6764, mean_delta_hard_"
            "unrel +0.0634 5/5, shuffled -0.155 to -0.177, do-no-harm +0.013 on ungated_rel <0.97. (2) LEAKAGE "
            "KILLER PASSES CLEAN (the whole ballgame vs v1's injected proxy): rebuilt data independently, "
            "indep_score AUC=0.686 sits BELOW the ground-truth source-tier oracle 0.698 on ALL 5 seeds -> "
            "structurally cannot be an inflated proxy; within-source AUC=0.115 (anti-leak); channel is provably "
            "the source track record (within/between std ratio 0.001); raw same-item loo AUC 0.884 not "
            "approached. (3) GENUINE DERIVATION win -- substrate ESTIMATES source reliability from data rather "
            "than being handed it (v1/29372) or starving on same-item singletons (derived_v1/29374); breaks the "
            "INJECTED-vs-DERIVED pattern for the first time. (4) control fires full-scale, unrel subset a-priori "
            "50% not cherry-picked, captures ~21% oracle headroom. LOAD-BEARING SCOPE: SYNTHETIC regime; "
            "informativeness CONTINGENT on the independent-random-error model (correlated/systematic errors "
            "would fool a consistency-based track record -- UNTESTED); real-data UNTESTED; modest effect. FRAMING "
            "CORRECTION: dev-sim 'small pop nets negative / clean monotone' NOT reproducible single-seed (VPT=100 "
            "-> +0.040); lift robust 600-4000. Counts toward CERT as a chain-grade mechanism/capability "
            "demonstration. Local-only; needs orchestrator store sync."),
        "framing_correction_vs_director": (
            "Director framed this as a chain-grade candidate + 'the first NEW capability win of the session -- "
            "the self-monitoring layer'. RESULT (symmetric): I GRANT CHAIN_GRADE -- every decisive adversarial "
            "check passes and the LEAKAGE KILLER passes CLEAN (derived AUC 0.686 BELOW the source-tier oracle "
            "0.698 on all 5 seeds -> not a proxy; within-source AUC 0.115 anti-leak; channel is just the source "
            "track record). This IS a genuine, first-of-session DERIVATION win that breaks the substrate's "
            "'USES injected signal it cannot DERIVE' pattern. BUT I SCOPE the framing: it is chain-grade FOR THE "
            "MECHANISM IN A SYNTHETIC INDEPENDENT-ERROR REGIME, NOT yet 'the self-monitoring layer works on real "
            "data'. Two load-bearing bounds keep it honest: (i) the channel's informativeness is CONTINGENT on "
            "the independent-random-error construction -- CORRELATED / systematic source errors (the real-world "
            "failure mode) would fool a consistency-based track record and are UNTESTED; (ii) real-data untested; "
            "effect modest (~21% of oracle headroom). Also correcting the cell's dev-sim narrative: the 'small "
            "population nets negative / clean monotone' story is NOT reproducible single-seed (VPT=100 -> +0.040); "
            "the lift is robust across VPT 600-4000 (which STRENGTHENS the result). Genuine capability preserved; "
            "exp_dev CREDITED for the clean honest design (in-band AUC gate that disqualifies a >0.90 proxy, "
            "non-vacuous controls + do-no-harm, disclosed pooled-AUC inflation, logged/fixed no-op)."),
        "cross_arc_overlap_check": XARC,
        "net_cert_delta": ("+1 CG (first self-monitoring DERIVATION win: derived, independent, leak-free "
                           "source-reliability channel genuinely helps consolidation on the low-reliability "
                           "subset; leakage killer passes clean -- AUC below oracle -> not a proxy; escapes "
                           "atom 29374's informative-vs-vacuous tension and breaks atom 29372's injection "
                           "pattern. SCOPED synthetic independent-error regime; correlated-error + real-data are "
                           "the untested continuation)."),
        "supersedes": None,
        "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
        "ts_iso": _iso, "ts": _ts, "atom_id": atom["id"],
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
    atom = build_atom()
    ledger = ledger_row(atom)
    print("=== A5 atom-write: attention_reliability_gate_independent_channel_v1 -> CHAIN_GRADE (derived leak-free source-reliability channel) (2026-07-20) ===")
    print("ts_iso =", _iso)
    assert atom["id"].isascii(), "non-ascii atom id"
    assert ledger["atom_id"] == atom["id"], "atom_id/id mismatch"

    existing = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                existing.add(json.loads(line).get("id"))
            except Exception:
                pass
    if atom["id"] in existing:
        print("ABORT: id already in store:", atom["id"]); sys.exit(1)
    print("id-uniqueness OK (1 new, not pre-existing)")

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

    n_ok = 0
    present = set()
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            json.loads(line); n_ok += 1
    with open(MATH_ATOMS, "rb") as f:
        for line in f:
            try:
                present.add(json.loads(line).get("id"))
            except Exception:
                pass
    assert atom["id"] in present, "post-write integrity: new id missing"
    print("integrity: math/atoms.jsonl fully parses (%d lines), new id present." % n_ok)
    print()
    print("=== A5 WRITE COMPLETE (LOCAL ONLY; needs_orchestrator_store_sync=True; no origin push; no remote persist) ===")
    print("ATOM (CHAIN_GRADE):", atom["id"][:110], "...")


if __name__ == "__main__":
    main()
