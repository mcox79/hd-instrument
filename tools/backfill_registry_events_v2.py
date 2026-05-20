"""Backfill_v2: emit experiment_outcome events for the remaining ~52 experiments.

These are historical work (morning M2/basis/C3/phase_b2/c3_minimal sequence)
plus various supporting experiments that the original backfill missed.

Verdicts hand-curated from STATE_2026_05_19.md + HANDOFF_2026_05_19.md +
queue.log inspection.

Idempotent-after-merge: dashboard expected to dedupe by (event_type, name).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.session_log import log_event


# (name, verdict, summary, headline, metrics_path)
ADDITIONAL_OUTCOMES = [
    # ===== R10 / scaling positives (early-day work that led to best-config) =====
    ("r10_K128_K256_multiseed", "positive",
     "R10 default-config K=128 +0.139, K=256 +0.193 (multi-seed). Established the K-scaling curve before hyperparam sweep.",
     False, None),
    ("r10_K32_K64_multiseed", "positive",
     "R10 default-config K=32, K=64 multi-seed. Filled lower K of the scaling curve.",
     False, None),
    ("r10_hyperparam_sweep", "positive",
     "Found nc=50/lam=0.3/beta=16 config gives +0.318 at K=64 single-seed (3x default). Source of best-config used in all subsequent K-extensions.",
     True, None),
    ("r10_N8192", "positive",
     "R10 at N=8192 confirms M1 bundle-SNR mechanism: gap shrinks 12-50% per K vs N=4096. Default config.",
     False, None),
    ("r10_K16_m2", "negative",
     "R10 at K=16 with M2 retrieval-augment (pre-best-config era). Closed -- M2 framing at K=16 didn't add over baseline.",
     False, None),

    # ===== Triple compound history =====
    ("triple_compound_v2", "negative",
     "Triple compound (replay x R10 x R3) confirmed FALSIFIED after string-parsing bugfix in v1.",
     False, None),

    # ===== R3 rescues (closed) =====
    ("r3_rescues", "negative",
     "R3 rescue attempts closed; R3 in any form does not compound with replay or R10.",
     False, None),

    # ===== Replay / continual learning positives =====
    ("r7_concept_replay", "positive",
     "R7 concept-tagged replay during Phase B: +0.66-0.73 BWT recovery at K=4. The first replay-works result.",
     True, None),
    ("r7_multiseed", "positive",
     "R7 replay BWT confirmed multi-seed (3 seeds, robust).",
     True, None),
    ("replay_mechanism_sweep", "positive",
     "Replay mechanism sweep: random > priority > targeted. Source of the random-replay-wins finding.",
     False, None),

    # ===== ACF / resonator infrastructure =====
    ("acf_K_dependent", "positive",
     "First ACF K-dependent run (later retried -- the retry is the canonical one). Established the K-dep r prescription.",
     False, None),
    ("acf_sparsity_sweep", "positive",
     "ACF sparsity sweep r in {0.005, 0.01, 0.05, 0.1} across K. Established asymmetric ACF behavior.",
     False, None),
    ("acf_resonator", "positive",
     "ACF resonator first run. Cliff at K/N~0.55, rescue beyond.",
     False, None),
    ("acf_resonator_v2", "positive",
     "ACF resonator cross-validation v2. Confirms K=8192 recovery=100%.",
     False, None),
    ("noise_resonator", "positive",
     "Resonator with noise injection. Established robustness behavior under noise perturbation.",
     False, None),

    # ===== Decompose / K-cliff =====
    ("decompose_K_extreme", "positive",
     "Decompose at extreme K (K=16384+). Confirms substrate decomposability at large bundle sizes.",
     False, None),
    ("decompose_extreme_B", "positive",
     "Decompose at extreme B (large bundle counts). Confirms decomposition robustness.",
     False, None),

    # ===== Phase B / pool infrastructure positives =====
    ("phase_b2_pool_size_sweep", "positive",
     "Phase B.2 pool size sweep. Established POOL_SIZE=1024 sweet spot.",
     False, None),
    ("phase_b2_pool_size_sweep_v2", "positive",
     "Phase B.2 pool size sweep v2 cross-validation.",
     False, None),
    ("phase_b2_pool_size_annealed", "positive",
     "Phase B.2 with annealed pool size. Tests dynamic pool management.",
     False, None),
    ("phase_b2_pool_size_annealed_v2", "positive",
     "Phase B.2 annealed pool size v2 cross-validation.",
     False, None),

    # ===== Substrate uniqueness demos =====
    ("interpretability_demo", "positive",
     "Substrate interpretability demonstration. Shows decompose-edit-recompose flow end-to-end.",
     True, None),
    ("memory_recomposition", "positive",
     "Memory recomposition demonstration. Constructs novel bundles from extracted atoms.",
     True, None),
    ("memory_editing", "positive",
     "Memory editing demonstration. Surgical (byte, position) edit without retraining W.",
     True, None),

    # ===== Scaling / timing =====
    ("scaling_extreme_128K_256K", "positive",
     "Scaling at N=128K-256K. Confirms substrate operates at large N.",
     False, None),
    ("cpu_timing_extended", "positive",
     "Extended CPU timing benchmark. Latency profile across K and pool sizes.",
     False, None),
    ("hard_nn_pool_sweep_workstation", "positive",
     "Hard nearest-neighbor pool sweep on workstation CPU. Confirms efficient pool retrieval.",
     False, None),
    ("retrieval_3way", "positive",
     "Three-way retrieval comparison (factored / classical / mixed). Established ALPHA=0.3 sweet spot.",
     False, None),
    ("rerank_sanity_check", "positive",
     "Rerank sanity check. Confirms reranking infrastructure works.",
     False, None),

    # ===== M2 retrieval-augment closures (all closed at K=4; reopened at K>=8 by R10) =====
    ("m2_concept_extraction", "negative",
     "M2 concept extraction at K=4. Closed -- original M2 dead-at-K=4 framing. R10 reopened at K>=8.",
     False, None),
    ("m2_concept_extraction_v2", "negative",
     "M2 concept extraction v2 at K=4. Same closure.",
     False, None),
    ("m2_ppmi", "negative",
     "M2 PPMI variant. Subsumed by R3/R10's use of PPMI.",
     False, None),
    ("m2_slot_attention", "negative",
     "M2 slot attention. Closed -- attention-style retrieval did not beat baseline.",
     False, None),
    ("m2_slot_attention_v2", "negative",
     "M2 slot attention v2 closure.",
     False, None),
    ("m2_slot_attention_v3", "negative",
     "M2 slot attention v3 closure.",
     False, None),
    ("m2_nmf", "negative",
     "M2 NMF concept factorization. Closed.",
     False, None),
    ("m2_nmf_v2", "negative",
     "M2 NMF v2 closure.",
     False, None),
    ("m2_cp_tensor", "negative",
     "M2 CP tensor decomposition concept extraction. Closed.",
     False, None),
    ("m2_sparse_autoencoder", "negative",
     "M2 sparse autoencoder concept extraction. Closed.",
     False, None),
    ("m2_sparse_autoencoder_v2", "negative",
     "M2 sparse autoencoder v2 closure.",
     False, None),
    ("m2_with_proper_rerank", "negative",
     "M2 with proper rerank. Closed.",
     False, None),

    # ===== C3 factored compositional retrieval (retracted) =====
    ("c3_factored", "retracted",
     "Original C3 factored +0.098 headline RETRACTED. Was a lambda=0.7 artifact; true effect ~0.",
     False, None),
    ("c3_minimal", "retracted",
     "C3 minimal -- early variant of retracted C3.",
     False, None),
    ("c3_minimal_v2", "retracted",
     "C3 minimal v2 -- retracted same as parent.",
     False, None),
    ("c3_minimal_v3", "retracted",
     "C3 minimal v3 -- retracted same as parent.",
     False, None),

    # ===== Basis modifications (all closed -- no meaningful beat) =====
    ("basis_modification", "negative",
     "Basis modification first attempt (exit 1 in runner.log). Closed in v2 cleanup.",
     False, None),
    ("basis_modification_v2", "negative",
     "Basis modification v2. No meaningful beat over baseline. Closed.",
     False, None),
    ("basis_modification_indep", "negative",
     "Basis modification independent variant. Closed.",
     False, None),

    # ===== F1 coverage / A1 alternative basis closures =====
    ("f1_coverage_sweep", "negative",
     "F1 coverage sweep (M2-era F1 metric). Closed -- F1 framing didn't survive to R10 framing.",
     False, None),
    ("a1_cubic_binding", "negative",
     "A1 cubic binding alternative basis test. Closed -- cubic binding did not beat BSC bipolar.",
     False, None),
]


def main():
    n = 0
    for name, verdict, summary, headline, metrics_path in ADDITIONAL_OUTCOMES:
        kwargs = {"name": name, "verdict": verdict, "summary": summary, "headline": headline}
        if metrics_path:
            kwargs["metrics_path"] = metrics_path
        log_event("experiment_outcome", **kwargs)
        n += 1
    print(f"Emitted {n} additional experiment_outcome events.")


if __name__ == "__main__":
    main()
