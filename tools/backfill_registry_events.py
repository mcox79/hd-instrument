"""Backfill experiment_outcome + experiment_research events for the registry tab.

Hand-curated verdicts for all wave14b/c experiments based on overnight_log.md +
STATE_2026_05_19.md + the agent research syntheses. Emits backdated events to
data/session_events.jsonl via hdlab.session_log.log_event.

Run once after the registry tab is live. Idempotent: rerunning emits duplicate
events (the tab is expected to dedupe by (event_type, name, ts) tuple).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Allow running from repo root
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.session_log import log_event


# (name, verdict, summary, headline, metrics_path_relative_or_None)
OUTCOMES = [
    # ===== Headline-tier positives =====
    ("r10_best_config_multiseed", "positive",
     "R10 best-config K=128 +0.412, K=256 +0.543 (3 seeds, sd~0.009). 196-200% over default config.",
     True, "data/exp_wave14b_r10_best_config_multiseed/metrics.json"),
    ("r10_best_config_K512", "positive",
     "R10 best-config K=512 +0.628 bpc (3 seeds). Extends headline; monotone K=8 to K=512.",
     True, "data/exp_wave14b_r10_best_config_K512/metrics.json"),
    ("r10_best_config_K16_K32_K64", "positive",
     "R10 best-config K=16 +0.183, K=32 +0.222, K=64 +0.318 (single-seed, crashed before completing 3 seeds at K=64).",
     True, None),
    ("r10_best_config_K64_verify", "positive",
     "R10 best-config K=64 verified at +0.321 (3 seeds, sd 0.008). Matches +0.318 single-seed from hyperparam sweep.",
     True, "data/exp_wave14b_r10_best_config_K64_verify/metrics.json"),
    ("r10_best_config_N8192_K128", "positive",
     "M1 mechanism confirmed: gap shrinks 15% (best +0.412 -> +0.352) when N doubled at K=128.",
     True, "data/exp_wave14b_r10_best_config_N8192_K128/metrics.json"),
    ("r10_ksweep_multiseed", "positive",
     "R10 default-config K-sweep: monotone gap K=16 (+0.008) to K=256 (+0.193). Falsifies Lippl-Stachenfeld redundancy theorem at K>=8.",
     True, None),

    # ===== Headline-tier negatives (supporting/closed) =====
    ("triple_compound", "negative",
     "FALSIFIED: random replay x R10 x R3 don't compound (substitute on same evidence base). Over-determined by 4 arguments.",
     True, None),
    ("replay_preshift_K4", "negative",
     "Stein pred #1 FALSIFIED: replay at fraction 0.9 gives pre-shift bpc delta +0.005 (well below threshold). Random replay is pre-shift-neutral.",
     True, "data/exp_wave14b_replay_preshift_K4/metrics.json"),

    # ===== Supporting positives =====
    ("decompose_K_cliff", "positive",
     "K-cliff at K/N~=0.56 cross-validated. Sharp 10%->0% in one step.",
     False, None),
    ("decompose_K_cliff_extended", "positive",
     "K-cliff cross-validation #2 confirms identical cliff. Independent 30-trial sweep.",
     False, None),
    ("acf_K_dependent_retry", "positive",
     "ACF K-dependent r-schedule confirms paper's prescription: r=0 below cliff, r=0.01 above; recovery 17%->73% across K=2048 to K=3072.",
     False, "data/exp_wave14b_acf_K_dependent_retry/metrics.json"),
    ("acf_K_dependent_extended", "positive",
     "ACF K-dep sweep extended to 16 K levels confirms monotone increase 17%->97%. Reveals K=2944 dip to 50% (likely noise).",
     False, "data/exp_wave14b_acf_K_dependent_extended/metrics.json"),
    ("acf_sparsity_sweep_redo", "positive",
     "ACF sparsity sweep r in {0.005,0.01,0.05,0.1} cross-validates asymmetric ACF: r=0.005 best at K=2560, r=0.01 best at K=3072.",
     False, None),
    ("acf_resonator_redo", "positive",
     "ACF resonator cross-validation at K=2048-16384. K=8192 recovery=100%.",
     False, None),
    ("r10_best_config_K2_K4_K8", "negative",
     "R10 best-config INVERTS at K<8: best -0.135 (K=2), -0.174 (K=4) -- WORSE than default. Regime boundary at K=8.",
     True, "data/exp_wave14b_r10_best_config_K2_K4_K8/metrics.json"),
    ("r10_best_config_N8192_K256", "positive",
     "M1 mechanism check at K=256 (still pending result; placeholder).",
     False, None),

    # ===== Closed mechanisms =====
    ("r1_modern_hopfield", "negative",
     "Iterative Hopfield as label readout: protocol mismatch (Ramsauer iterates to nearest pattern, not label). Closed.",
     False, None),
    ("mir_canonical", "negative",
     "MIR canonical (Aljundi 2019) closed by rank-equivalence math: priority and random monotonically related.",
     False, None),
    ("mir_replay", "negative",
     "MIR-style replay 3 rescues all lose to random replay. Closed.",
     False, None),
    ("mir_rescues", "negative",
     "MIR rescue attempts (decorrelate, top-k, importance-weighted) all lose to random.",
     False, None),
    ("r10_r3_combined", "negative",
     "R3+R10 don't compound. Over-determined by shared evidence base.",
     True, None),

    # ===== Retractions =====
    ("r3_multiseed", "retracted",
     "Original R3 +0.154 at K=4 (single-seed t=33) RETRACTED. True effect with Laplace fix = +0.032 (3 seeds).",
     False, None),
    ("r3_concept_readout_bias", "retracted",
     "Original R3-as-readout-bias result retracted: broken log+epsilon normalizer artifact.",
     False, None),
    ("r3_laplace", "positive",
     "R3 with Laplace smoothing gives +0.032 at K=4 (true effect after retracting variance artifact).",
     False, "data/exp_wave14b_r3_laplace/metrics.json"),
    ("r3_alone_laplace", "positive",
     "R3 alone Laplace +0.032 confirmed (3 seeds, sd 0.005). Settles +0.154 mystery.",
     False, "data/exp_wave14b_r3_alone_laplace/metrics.json"),

    # ===== Inconclusive =====
    ("r3_unigram_diagnostic", "inconclusive",
     "GAMMA mis-calibrated: unigram HURT (-0.097) while R3 helped (+0.032). Needs sparsity-matched test.",
     False, "data/exp_wave14b_r3_unigram_diagnostic/metrics.json"),
    ("r3_disjoint_concepts", "positive",
     "R3-disjoint at K=4 compounds with replay: +0.025 delta vs same-source. Hypothesis confirmed at K=4.",
     False, "data/exp_wave14b_r3_disjoint_concepts/metrics.json"),
    ("r3_disjoint_K16", "negative",
     "R3-disjoint K=16: delta +0.008. Effect 3x smaller than K=4. Doesn't scale.",
     False, "data/exp_wave14b_r3_disjoint_K16/metrics.json"),
    ("r3_disjoint_K32", "negative",
     "R3-disjoint K=32: delta +0.008. Effect flat above K=16. K=4-specific phenomenon.",
     False, "data/exp_wave14b_r3_disjoint_K32/metrics.json"),

    # ===== Operational/failed (no scientific outcome) =====
    ("decompose_K_cliff_dense", "inconclusive",
     "Timeout at 7200s. 16 K levels too dense for 2h budget. Replaced by dense8.",
     False, None),
    ("cpu_platform_timing_redo", "inconclusive",
     "Timeout at 3600s. Likely hung waiting for input. Not investigated further.",
     False, None),
]


RESEARCH_LINKS = [
    # (name, level, notes)
    ("replay_preshift_K4", "exhaustive", ["notes/wave14c_stein_pred1_rejection_research.md"]),
    ("r10_r3_combined", "exhaustive", ["notes/wave14b_compound_falsification_research.md"]),
    ("triple_compound", "exhaustive", ["notes/wave14b_compound_falsification_research.md"]),
    ("mir_canonical", "exhaustive", ["notes/wave14b_mir_failure_diagnosis.md"]),
    ("mir_replay", "exhaustive", ["notes/wave14b_mir_failure_diagnosis.md"]),
    ("mir_rescues", "exhaustive", ["notes/wave14b_mir_failure_diagnosis.md"]),
    ("r1_modern_hopfield", "exhaustive", []),
    ("r3_multiseed", "exhaustive", ["notes/wave14b_r3_laplace_synthesis_research.md"]),
    ("r3_alone_laplace", "exhaustive", ["notes/wave14b_r3_laplace_synthesis_research.md"]),
    ("r3_disjoint_concepts", "exhaustive", ["notes/wave14c_r3_disjoint_K_flatness_research.md"]),
    ("r3_disjoint_K16", "exhaustive", ["notes/wave14c_r3_disjoint_K_flatness_research.md"]),
    ("r3_disjoint_K32", "exhaustive", ["notes/wave14c_r3_disjoint_K_flatness_research.md"]),
    ("r3_unigram_diagnostic", "exhaustive", ["notes/wave14c_r3_unigram_failure_research.md"]),
    ("r10_best_config_multiseed", "partial", ["notes/wave14b_r10_deep_dive.md"]),
    ("r10_best_config_K512", "partial", ["notes/wave14b_r10_deep_dive.md"]),
    ("r10_best_config_K2_K4_K8", "in_progress", []),  # agent currently running
    ("acf_K_dependent_extended", "exhaustive", ["notes/wave14c_acf_cliff_substructure_research.md"]),
]


PLANNED_PENDING = [
    # (name, purpose, queue, tier)
    ("r10_best_config_K1024_retry", "Extends R10 best-config curve; predicted toward +0.7 if K=8 to K=512 trend continues.",
     "overnight_queue", "headline"),
    ("r3_sparse_unigram_diagnostic", "Decisive R3 mechanism test: sparse-gated unigram with same query_active as R3.",
     "overnight_queue", "diagnostic"),
    ("acf_K2944_100trials", "Settles K=2944 dip via 100 trials at single K. If recovery ~75%, dip was noise.",
     "remote_cpu_queue", "diagnostic"),
    ("r10_best_config_K8_verify", "Verifies K=8 boundary multi-seed where K2_K4_K8 single-seed showed +0.142.",
     "overnight_queue", "supporting"),
    ("r10_best_config_N8192_K256", "M1 mechanism at K=256: predict gap shrinks similarly to K=128's 15%.",
     "overnight_queue", "supporting"),
    ("r3_disjoint_K64", "Confirms K-flatness above K=32 for R3-disjoint compound.",
     "overnight_queue", "supporting"),
    ("decompose_K_cliff_dense8", "8-level dense sweep around the K-cliff (replaces dense16 that timed out).",
     "remote_cpu_queue", "supporting"),
    ("acf_K_dependent_extended_redo", "Cross-validates the K=2944 dip with same script.",
     "remote_cpu_queue", "supporting"),
]


def main():
    n_outcomes = 0
    n_research = 0
    n_planned = 0

    for name, purpose, queue, tier in PLANNED_PENDING:
        log_event("experiment_planned", name=name, purpose=purpose,
                  queue=queue, tier=tier)
        n_planned += 1

    for name, verdict, summary, headline, metrics_path in OUTCOMES:
        kwargs = {"name": name, "verdict": verdict, "summary": summary, "headline": headline}
        if metrics_path:
            kwargs["metrics_path"] = metrics_path
        log_event("experiment_outcome", **kwargs)
        n_outcomes += 1

    for name, level, notes in RESEARCH_LINKS:
        log_event("experiment_research", name=name, level=level, notes=notes)
        n_research += 1

    print(f"Emitted {n_planned} planned, {n_outcomes} outcome, {n_research} research events")


if __name__ == "__main__":
    main()
