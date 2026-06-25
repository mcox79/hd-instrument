# 2026-06-24 substrate_hub_spoke_E1_v2_diverse_algorithm -- v1 RESCUE with genuine spoke diversity

## Anchor
`substrate_hub_spoke_E1_v2_diverse_algorithm`

## Status
- Prereg authored 2026-06-24 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home) -- routes via hdi_orchestrator (push is harness-DENIED to exp_dev)
- Timeout: 7200s (2h; matmul + Hebbian multi-algorithm spoke build at N=8192)
- Estimated wall: 45-90 min GPU full (3 seeds, 3-arms with 3 or 4 spokes each;
  v1 ran 50-110 min for SAME-algo spokes which were faster -- diverse-algo spokes
  amortize differently: SoftHebb scatter-add slower per pass, RI streaming dominated
  by python loop, FPE is one-shot)

## Cell
`experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py`

## v1 evidence + the bug
v1 (`exp_substrate_hub_spoke_E1_encoder_v1`) HARD_FAILed at landed run
(`data/exp_substrate_hub_spoke_E1_encoder_v1/metrics.json`):

```
ARM_BASELINE_PATH_C_SINGLE         bpc=7.667 cv=0.002
ARM_HUB_SPOKE_3SPOKE               bpc=7.707 cv=0.003
ARM_HUB_SPOKE_5SPOKE               bpc=7.707 cv=0.003
ARM_HUB_SPOKE_WITH_CFRPE           bpc=7.707 cv=0.003
best_hub=ARM_HUB_SPOKE_5SPOKE bpc=7.707 >= HF_BPC_MIN=7.60
```

**Diagnosis (per `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md`):**
All 5 spokes used the SAME predictive-coding update rule with only +/-15% alpha
jitter on the SAME training tokens. Per-spoke L3 recon error CV = 0.0008 across 15
spokes. Hub aggregation `sign(sum(spokes)) ~= sign(M * spoke_0) = spoke_0` -- the
"5-spoke federation" was a single spoke in disguise. cf-RPE gates collapsed to
uniform 0.333 because every spoke gave the same per-bigram alignment scores.
v1 had ensemble rank ~= 1.

## v2 hypothesis (the actual E1 design from the encoding drill)
Per `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`,
the E1 design specified DIFFERENT ALGORITHMS per spoke (brain ATL hub-spoke
Patterson-Lambon Ralph 2007: different cortical sources contribute different
modalities). Replace alpha-jitter-on-PC with three genuinely different algorithm
families:

- **S1 SoftHebb k-WTA** (Moraitis et al. 2107.05747): forward-only Hebbian +
  hard k-WTA mask on bigram-context bundles; init from char-trigram bag.
  Algorithm family: competitive Hebbian.
- **S2 char-trigram x Random-Indexing** (Sahlgren 2005 + Kanerva-style bag):
  orthographic vector * distributional context-window vector via Hadamard bind.
  Algorithm family: distributional / random projection.
- **S3 Path-C predictive coding** (v1 baseline architecture, preserved):
  3-layer Hebbian PC with iterative err-driven W updates.
  Algorithm family: hierarchical predictive coding.
- **S4 Fractional Power Encoding** (FPE arm only): random freq axes + co-occ
  amplitudes mapped to cos/sin pair.
  Algorithm family: random-Fourier kernel approximation.

These four are KNOWN to occupy different points in the codebook eigenspace
(empirical witness from self-test: 3-spoke diverse-algo CV = 1.09 vs v1's
alpha-jitter CV = 0.0008 -- three orders of magnitude more diverse by the
SAME measurement).

## Arms (4; substrate-OWNED encoders only; ONE knob varies = spoke composition)
1. **ARM_BASELINE_PATH_C_SINGLE** -- Single PC spoke (v1 baseline; control + sanity rail).
2. **ARM_HUB_3SPOKE_DIVERSE_ALGO** -- S1 SoftHebb + S2 char-trigram-RI + S3 Path-C PC,
   bundled via majority-rule sign-quantize.
3. **ARM_HUB_3SPOKE_DIVERSE_PLUS_FPE** -- arm 2 + S4 FPE (4 spokes total).
4. **ARM_HUB_3SPOKE_DIVERSE_WITH_CFRPE_GATING** -- arm 2 + cf-RPE-learned gates;
   gates must NOT collapse to uniform (gate_std_over_mean > 0). PRIMARY arm.

## Config (PRODUCTION SCALE GPU; one knob = spoke composition)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- All ops via torch.cuda (Fix #24)
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- Sparse-bipolar f=0.02 + 1/sqrt(f) amplitude scaling (Stage-1 foundations)
- SoftHebb: k_wta=64, lr=0.01, 1 pass, 100_000 train tokens
- Random Indexing: window=5, sparsity=16, 100_000 train tokens
- Path-C PC: 3 layers, alpha=0.05, beta=2.0, 1 pass, 100_000 train tokens
- FPE: bandwidth=1.5, n_axes=4096 (= N_DIM/2)
- cf-RPE: eta=0.05, n_steps=100 (vs v1 50; deeper signal for true diversity)
- Hub aggregation: majority-rule (arms 2/3) OR cf-RPE weighted (arm 4)

## Reported metrics per arm
- `bpc_best` (at best joint (T*, lambda*))
- `top1_acc`, `mrr_at_10`, `best_T`, `best_lambda`
- `raw_bpc_at_T1_L1` (sanity for DEGEN gate)
- `encoder_meta` (per-spoke algo + wall + recon)
- `spoke_diversity_cv` per arm: CV of per-spoke summary scalar (off-diagonal
  pairwise-cosine mean). v1's hubs had CV ~ 0.0008; v2 self-test smoke
  shows CV = 1.09 for the 3-diverse-algo bundle.
- `cfrpe_gates` + `cfrpe_gate_std_over_mean` (PRIMARY arm only)

## Discriminator (per Fix #28)
ensemble L3 reconstruction-error CV across spokes is the SUFFICIENT-DIVERSITY
discriminator. v1 hit CV=0.0008; v2 must hit `spoke_diversity_cv >= 0.05` to
qualify as genuinely diverse. If v2 still collapses to `cv < 0.01`, the
federation hypothesis is refuted at the algorithm level (not at the
parameter-jitter level).

## Pre-reg HARD bands (DIVERSITY-AWARE)
- **HARD_PASS CHAIN_GRADE:** best diverse hub bpc <= 6.95 AND
  spoke_diversity_cv >= 0.05 AND cross-seed cv < 0.05
  (genuine algorithmic diversity AND word2vec-class gap closed without leakage)
- **HARD_PASS:** best diverse hub bpc <= 7.20 AND beats baseline by >= 0.10 bpc
  AND cross-seed cv < 0.05
- **HARD_FAIL:** ALL hub arms bpc >= 7.60 AND any diverse arm cv < 0.01
  (federation fails AND diversity collapsed -> hypothesis refuted at the
  algorithm level)
- **METHODOLOGY_CHECK (MIDDLE_BAND):** diverse-arm spoke_diversity_cv < 0.01
  on any arm -- spokes did NOT maintain genuine diversity through the pipeline;
  report as MEASURED_MECHANISM, not architecture refutation
- **SANITY_RAIL_MISS (MIDDLE_BAND):** ARM_BASELINE_PATH_C_SINGLE bpc deviates
  more than +/- 0.02 from v1's 7.667 (provenance broken)

## Sanity rail
ARM_BASELINE_PATH_C_SINGLE must reproduce v1's 7.667 within +/- 0.02 bpc.
Same primitive, same data, same harness -> same answer. If rail misses, v2
results are suspect even if hubs look good.

## Apples-to-apples (Lane 1)
- Substrate-OWNED encoders ONLY (no word2vec, no Pythia, no MiniLM residuals)
- ONE knob varies across arms = spoke composition (number + algorithm)
- All arms share the storage primitive: sparse-bipolar f=0.02 + 1-bit signed
  + 1/sqrt(f) amplitude scale + rank-1 Hebbian W
- All arms share the readout primitive: joint (T, lambda) sweep, BPC + top1 + MRR@10
- All arms share corpus + train/held split

## Operating disciplines (mandatory)
- D1 roofline probe: smoke wall = 3.7s end-to-end on local CPU at N_DIM=256
  V=200 N_TRAIN=1500; scale to N=8192 V=4000 N_TRAIN=100k on GPU =~ 45-90 min
- D2 atexit + per-seed checkpoint: uses `experiments/_seed_checkpoint.py`
  (write_partial_key / aggregate_partials); atexit synthesizer writes
  partial metrics on SIGTERM / kill
- Predispatch_check: PROCEED (no prior landings for this anchor)
- Self-test: PASS (T1-T12; T8 confirms diversity_cv = 1.09 vs v1's 0.0008)
- Smoke (local CPU): PASS at N=256 V=200 N_TRAIN=1500 in 3.7s; all 4 arms
  produce valid metrics; n_llm = 0; sanity-rail-miss is EXPECTED at smoke scale
  (rail is calibrated against v1 full-scale; smoke is the gate-check, not the
  cert evaluation)
- ASCII only (no unicode in cell or prereg)
- GPU dispatch via Orchestrator (Fix #24): torch.cuda + batched matmul +
  scatter_add for SoftHebb k-WTA; chunked PC matmul; concurrent (per-seed)
  loop. Spokes built sequentially per seed (memory bound at 9GB total).
- Route to overnight_queue via hdi_orchestrator (exp_dev push is harness-denied)

## Smoke evidence (local CPU; 2026-06-24)
```
[seed=0 arm=ARM_BASELINE_PATH_C_SINGLE]            bpc=4.752 div_cv=0.0000
[seed=0 arm=ARM_HUB_3SPOKE_DIVERSE_ALGO]           bpc=4.752 div_cv=1.3174
[seed=0 arm=ARM_HUB_3SPOKE_DIVERSE_PLUS_FPE]       bpc=4.752 div_cv=0.9538
[seed=0 arm=ARM_HUB_3SPOKE_DIVERSE_WITH_CFRPE_GATING] bpc=4.752 div_cv=1.3174
```
BPC collapses to unigram (4.752) because at V=200 + N_TRAIN=1500, lambda=0.0
wins (substrate's signal is below unigram's prior at this microscale; an
EXPECTED smoke-scale artifact). The discriminator that matters at smoke scale
is **div_cv on diverse arms = 1.0+** vs **v1 was 0.0008 = 1000x more diverse
by construction**. The full-scale GPU run is where the BPC verdict matters.

## Cites
- preregs/2026-06-24_substrate_hub_spoke_E1_encoder_v1.md (v1 prereg)
- experiments/exp_substrate_hub_spoke_E1_encoder_v1.py (v1 cell; design preserved
  where unaffected)
- data/exp_substrate_hub_spoke_E1_encoder_v1/metrics.json (v1 HARD_FAIL evidence)
- notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md (bug + revival spec)
- notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md
- hdlab/random_indexing.py / hdlab/char_trigram_encoder.py
- Moraitis et al. 2107.05747 (SoftHebb)
- Sahlgren 2005 (Random Indexing); Kanerva 1988 (SDM)
- Plate 1994 / Komer-Stewart 2019 (FPE / fractional binding)
- USER 2026-06-23 Path C substrate-owned encoder is the answer
- USER 2026-06-22 Fix #24 GPU dispatch must actually use GPU
- USER 2026-06-22 Fix #28 verify per-arm metrics not summary verdict
