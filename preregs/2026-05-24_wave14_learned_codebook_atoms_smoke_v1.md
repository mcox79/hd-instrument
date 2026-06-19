# Prereg — wave14_learned_codebook_atoms_smoke_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role
**Routing**: A6 from `notes/strategy_untested_rows_triage_2026-05-24.md` Priority A #6 — cheapest untested UNSURE 🔬 row; ~15 min CPU estimate from cap_map v1
**Script**: `experiments/exp_wave14_learned_codebook_atoms_smoke_v1.py`

## Hypothesis

Bigram-PPMI-derived bipolar atoms (sign-quantized SVD/PCA projection of corpus PPMI) beat purely random bipolar atoms at K-cleanup tasks, especially at low K (K=4-16). Cap_map UNSURE A6 row estimates +0.02-0.08 bpc improvement at K=4.

## Design

- Build PPMI matrix from corpus_a bytes (vocab=256).
- Random atoms: standard {-1,+1}^N i.i.d.
- Learned atoms: sign(top-N principal components of centered PPMI) padded with random.
- Cleanup task: bundle K random atoms via sum; argmax-K cleanup; measure fraction of K-set recovered.

## Parameters (exp_dev decided)

- N_FULL = 1024, vocab = 256
- K_VALUES = [4, 8, 16]
- SEEDS_FULL = [7, 17, 23]
- N_PROBES_FULL = 2000 per cell
- 3 K * 3 seeds * 2 atom types * 2000 probes = small CPU job

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] + [[feedback-no-smoke]])

- **HARD-PASS**: learned atoms strictly better at ALL three K values; best delta >= 0.05 bpc. UNSURE A6 row promotes from 🔬 to ✅ (or to 🟢 pending multi-N replication); learned codebook becomes a substrate-product primitive.
- **HARD-FAIL**: learned atoms NOT better at >= 2 of 3 K values. UNSURE A6 +0.02-0.08 prediction REFUTED; row closes to ❌ with rehab sketches required per PROT-004/006.
- **MIDDLE**: 1-of-3 K values shows learned advantage. K-dependent partial benefit; row stays 🔬 with K-dependent annotation; next probe = finer K sweep.

## Smoke result (this cycle, local CPU)

- N=256, 1 seed (17), 200 probes/cell: K=4 random=1.000 learned=1.000 delta=0; K=8 random=0.9975 learned=1.000 delta=+0.0025; K=16 random=0.9334 learned=0.9934 delta=+0.0600. VERDICT: LEARNED_CODEBOOK_MIDDLE_BAND (2/3 K wins; best delta=0.06). Full will resolve at N=1024.

## Dependencies verified

- `numpy`, `torch` (torch unused in this script but imported for consistency)
- Corpus fallback: synthetic deterministic byte stream if no enwik8/corpus_a file. Smoke confirmed corpus loading works.

## Verdict formula self-test

Passed (4/4 cases) — HARD_PASS / HARD_FAIL / MIDDLE / INCONCLUSIVE boundaries covered.

## Routing

local_cpu_queue per [[exp_dev tier policy]] Tier C: sub-minute work fit (smoke ran in <5s); full at N=1024 estimated <2 min CPU. Cheapest item on the v1 UNSURE list.
