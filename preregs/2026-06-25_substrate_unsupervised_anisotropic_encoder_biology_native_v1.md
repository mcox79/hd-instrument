# Pre-reg: substrate_unsupervised_anisotropic_encoder_biology_native_v1 (Cell H')

**Date:** 2026-06-25
**Anchor:** substrate_unsupervised_anisotropic_encoder_biology_native_v1
**Cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py
**Queue:** overnight_queue (GPU; matmul-heavy at N_DIM=8192 / V=4000 / text8-100k); numpy-only at author-time; future Fix #24 torch port if needed.
**Run-mode:** full (self-test PASS gate per USER embargo; NOT smoke-gated)
**Author:** Exp-Dev (cell author; not dispatching -- USER decides timing)
**Pre-reg source-of-truth:** notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md
**Drill source-of-truth:** notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md

## Question

Does any biology-native UNSUPERVISED anisotropic encoder mechanism (Olshausen-Field sparse coding / DeepWalk-on-bigram-graph / Foldiak anti-Hebbian / Kohonen SOM) beat isotropic random-bipolar baseline on BOTH text8 BPC AND a label-free heldout-word generalization probe (A3') at production scale (N_DIM=8192, V=4000)? Per USER's basis-vs-use-case principle (memory category O): the BASIS should not use labels; biology doesn't. P_deflated(any-arm HARD_PASS) = 0.45.

## Substrate-native arms (5; ALL unsupervised; NO external category labels at basis)

1. **ARM_RANDOM_BIPOLAR_BASELINE** -- isotropic random sparse-bipolar (control). Reproduces fair_harness baseline at sanity_T=0.05 within +/- 0.05 of 7.3065 BPC.
2. **ARM_OLSHAUSEN_FIELD_SPARSE_CODING** -- V1 analog. Forward-only SoftHebb (Moraitis 2107.05747) approximation; single linear layer over char-trigram input; k-WTA at K_WTA=5 on absolute value; Hebbian update over bigram-context pairs. Develops dominant-direction lanes from text8 co-occurrence statistics. NaN-guarded per Wave F Cell 1 heads-up (early-fallback to char-trigram if W goes non-finite).
3. **ARM_DEEPWALK_ON_BIGRAM_GRAPH** -- place-cell analog (Perozzi 2014). Builds bigram-cooccurrence graph from text8 train tokens (NO labels). Random walks of length WALK_LEN over top-K neighbors; skip-gram cooccurrence accumulator; JL random-bipolar projection to N_DIM; sparse-bipolar output.
4. **ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL** -- decorrelation. Foldiak 1990 anti-Hebbian lateral inhibition on bipolar codebook. NaN-guarded.
5. **ARM_KOHONEN_SOM_TOPOGRAPHIC** -- topographic input-statistics. Substrate-native variant: SOM codebook + per-position bipolar tag (substrate XOR-bind) so topographic identity is preserved across neighborhood-updates (preserves sigma=0 distinctness).

Char-trigram bipolar bundling is the SHARED substrate-native upstream input for arms 2/4/5. NO MiniLM / NO BGE / NO proprietary embedding per USER directive 2026-06-22.

## Config (full)

- N_DIM = 8192
- V_CAP = 4000 (text8 real vocab; matches fair_harness rail config)
- N_TRAIN = 100_000 tokens
- N_HELD = 20_000 tokens
- N_HELDOUT_WORDS = 200 (for A3' label-free generalization eval)
- N_BIGRAM_WALKS = 4000 (DeepWalk)
- WALK_LEN = 12 (DeepWalk walk length)
- N_OLSHAUSEN_BATCHES = 80 (batch_size=256 -> 20,480 effective training pairs)
- N_FOLDIAK_ITER = 30
- N_SOM_EPOCHS = 12
- K_WTA = 5 (sparsity at write)
- SPARSE_F = 0.02 (output sparsity)
- SEEDS = [7, 17, 23]
- LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0] for log-linear unigram interpolation

## Pre-reg HARD bands (verbatim from Director spec 2026-06-25)

### Metric B: BPC on text8 held (per arm, calibrated lambda)

- **HARD_PASS_FULL_BPC:** any biology arm BPC <= 6.95 (clears fair_harness rail by >=0.36 bits)
- **HARD_PASS_PARTIAL_BPC:** any biology arm BPC <= 7.30 (clears fair_harness rail)
- **HARD_FAIL_BPC:** all arms BPC >= 7.40

### Metric A3': label-free heldout-word generalization (per arm)

- Cluster IDs computed via k-means on bigram-cooccurrence rows (substrate-native; NOT labels)
- target_cluster[w] = majority bigram-neighbor cluster of w in train
- Heldout word h -> Hebbian-LM predict next; correct if cluster_ids[top-1] == target_clusters[h]
- Random baseline = 1/K_clusters ~ 1/63 = 0.016 (at V=4000, K=sqrt(4000) ~ 63)
- ARM_RANDOM_BIPOLAR_BASELINE's A3' is the BASELINE reference for "lift_vs_random"
- **HARD_PASS_FULL_A3:** any biology arm A3' lift_vs_random >= +0.10
- **HARD_PASS_PARTIAL_A3:** any biology arm A3' lift_vs_random >= +0.05
- **HARD_FAIL_A3:** NO biology arm beats random by >= +0.05 on A3'

### Anisotropy diagnostic (per arm; load-bearing for HARD_PASS_FULL)

- eigenspread = 1 - normalized_participation_ratio of encoder Gram eigvals
- cosine_spread = std of pairwise cosines among sampled vocab vectors
- mechanism_fired = (eigenspread >= 0.05); if False, that arm's mechanism silent-fallback -> METHODOLOGY_CHECK flag

### Cell-level verdict (per Director spec)

- **HARD_PASS_FULL (chain-grade-eligible):** any biology arm clears BPC <= 6.95 AND A3' lift >= +0.10 AND BPC cv <= 0.05 AND eigenspread >= 0.5.
- **HARD_PASS_PARTIAL (signal not chain-grade):** any biology arm clears BPC <= 7.30 AND A3' lift >= +0.05.
- **HARD_FAIL (biology-native path closes):** NO biology arm beats random by >= +0.05 on A3' OR all arms BPC >= 7.40.
- **MIDDLE_BAND:** intermediate cases.
- **CONFOUND_FAIL:** sigma=0 cleanup recall < 1.000 for any arm (implementation bug; NOT mechanism rejection).

## Sanity rails

- **sigma=0 cleanup mandatory:** all 5 arms must produce recall@1 = 1.000 at sigma=0. SOM uses per-position bipolar XOR-tag to preserve identity through neighborhood updates.
- **fair_harness provenance gate:** ARM_RANDOM_BIPOLAR_BASELINE BPC within +/- 0.05 of 7.3065 (recorded in `detail.sanity.fair_harness_provenance_ok`).
- **DeepWalk diversity gate:** A3'_lift on DeepWalk arm should be non-trivial (proves graph structure was used). Recorded via eigenspread + cosine_spread per-arm.
- **Foldiak decorrelation gate:** Foldiak arm should produce notable eigenspread relative to random (proves lateral inhibition fired). Recorded.
- **By-construction-saturation guard:** if ALL arms achieve A3' >= 0.95 (saturation), tier as MEASURED_MECHANISM not chain-grade and require larger V=16000 follow-up (per Director spec; checked in `detail`).
- **NaN guard:** Olshausen + Foldiak have per-batch NaN/Inf detection; on detection, fallback to char-trigram baseline (defensive against Wave F Cell 1 SoftHebb-NaN class bug; recorded in stderr).

## Wall budget

- Self-test (T1-T8 + production-scale Olshausen NaN probe at N=2048 V=400 idx=2000): ~30-40s.
- Smoke (1 seed, N_TRAIN=4000, N_HELD=1000, V=800): ~3-6 min CPU.
- Full (3 seeds, N_TRAIN=100k, N_HELD=20k, V=4000): estimated 90-150 min CPU per seed (Foldiak V x V matmul is heaviest at V=4000 -> 64MB x 8192-dim x 30 iter ~ 30 min per seed; Olshausen ~10-15 min; DeepWalk ~5-10 min; Kohonen ~10-15 min; total per-seed ~60-80 min); 3 seeds = 3-4 hr CPU.
- Per Fix #17 timeout = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.5 * (FULL_seeds/smoke_seeds)) -- target 10800s (3 hr per Director spec sequencing-recommendation), with atexit synthesizer to recover partials on timeout.

**GPU dispatch caveat (Fix #24 + coordinator heads-up 2026-06-25):** numpy-only baseline does NOT actually use GPU. If routed to overnight_queue, will run on GPU host's CPU only (~1% GPU util). For genuine GPU utilization, need torch port + explicit `.cuda()` + batched-arms profiling. Author recommends FIRST RUN on remote_cpu_queue (numpy baseline) to land verdict; GPU port is follow-up optimization if substrate-product economics justify. (Per spec, Foldiak V x V at V=4000 = 64MB and V=16000 = 1GB; GPU port becomes load-bearing at V >= 16000.)

## Implementation notes

- ASCII-only per `feedback_ascii_only_in_scripts`.
- numpy-only (no torch import at module level).
- Per-seed checkpoint + restartable via `experiments/_seed_checkpoint.py` (PROT-021 config-mismatch guard active).
- atexit synthesizer (Skunkworks #4) -- always produce metrics.json on timeout / SIGTERM.
- _LLM_CALL_COUNTER = [0] (substrate-only-decode gate; zero LLM at inference).
- NaN guards in Olshausen + Foldiak (Wave F Cell 1 heads-up); update-clipping + Frobenius-norm clipping.
- SOM uses per-position bipolar XOR-tag (substrate-native trick) to preserve sigma=0 distinctness through neighborhood updates.
- A3' uses substrate-native k-means cluster IDs on bigram-cooccurrence rows (NOT external labels; emerges from train statistics).

## Per-Fix discipline

- **Fix #26 (pre-dispatch verify-the-referent):** `tools/predispatch_check.py substrate_unsupervised_anisotropic_encoder_biology_native_v1` -> PROCEED (0 prior matches).
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling on data/exp_<anchor>/partial_metrics_*.json.
- **Fix #24 (GPU dispatch must actually use GPU):** acknowledged + caveat above; first run is numpy CPU; torch port is follow-up.
- **Fix #28 (per-arm metrics, not summary verdict):** ALL per-arm BPC + A3' + eigenspread + cosine_spread + sigma0_recall are stored in detail.by_arm_agg; post-landing run `tools/peek_arm_metrics.py` BEFORE propagating cross-arm narratives.
- **Long-cells discipline:** per-seed checkpoint via `_seed_checkpoint.write_partial_key`; smoke + full both restartable.
- **ASCII-only:** all print(), verdict_msg.

## Cites

- notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md (source-of-truth spec)
- notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md (3x drill)
- experiments/exp_encoder_dual_gain_softhebb_v1.py (template fork; same Hebbian/Foldiak base)
- experiments/exp_substrate_label_driven_anisotropic_encoder_v1.py (A1-A6 evaluator shape adapted to label-free A3')
- experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py (rail 7.3065 baseline ref)
- USER directive 2026-06-25 (basis-vs-use-case: no labels at basis layer)
- USER directive 2026-06-22 (no MiniLM, no BGE)
- USER directive 2026-06-23 (clean methodology; external ground truth where possible)
- Olshausen-Field 1996 Nature 381:607-609 (V1 sparse coding)
- Moraitis et al. 2107.05747 (SoftHebb forward-only Hebbian)
- Perozzi et al. 2014 DeepWalk
- Foldiak 1990 Biol Cybern 64:165-170 (anti-Hebbian decorrelation)
- Kohonen 1982 (SOM topographic maps)
- Coordinator heads-up 2026-06-25 (Wave F Cell 1 SoftHebb NaN at N=8192/V=4000/text8) -- defended via NaN guards + production-scale selftest probe

-- Exp-Dev
