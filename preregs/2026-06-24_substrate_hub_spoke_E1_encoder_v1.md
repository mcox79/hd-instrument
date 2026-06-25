# 2026-06-24 substrate_hub_spoke_E1_encoder_v1 -- HUB-and-SPOKE FEDERATION

## Anchor
`substrate_hub_spoke_E1_encoder_v1`

## Status
- Prereg authored 2026-06-24 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 7200s (2h; matmul-heavy at N=8192 with multi-spoke PC training)
- Estimated wall: 50-110 min GPU full (3 seeds * 4 arms; ARM_HUB_SPOKE_5SPOKE trains 5 PC stacks)

## Cell
`experiments/exp_substrate_hub_spoke_E1_encoder_v1.py`

## Why now (encoding drill 2026-06-24)
Per encoding drill 2026-06-24 (`notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`),
the optimal Stage-1 substrate encoding is the **hub-and-spoke federation** (E1 candidate,
P_deflated=0.45). Brain ATL (anterior temporal lobe) hub-spoke architecture is decisively
the brain's choice (Patterson-Rogers 2007; Lambon Ralph 2017). CLIP/ImageBind 2021-2023
converged on the same architecture for multi-modal ML. Substrate has all the parts
(SoftHebb/PC primitive, sparse-bipolar f=0.02 chain-grade, multi-modal binding chain-grade)
but the federation composition is NOT yet shipped.

This cell tests the encoding-drill's #1 ranked architecture with substrate-OWNED encoders
only (Lane 1; NO word2vec/Pythia leakage per USER 2026-06-23 Path C directive).

## Arms (4; substrate-OWNED encoders; 3 seeds; text8 V=4000 N_DIM=8192)
1. **ARM_BASELINE_PATH_C_SINGLE** -- Single PC spoke (Path C v2 reference)
   Sanity rail: bpc_best within +/- 0.10 of Path C v2 landed reference (7.6184).
   Provenance check: same primitive should yield same answer under same harness.
2. **ARM_HUB_SPOKE_3SPOKE** -- 3 independent PC spokes -> hub via majority-rule
   Spokes use different seeds + slightly varied alpha/beta to ensure diversity
   (not just rank-1 redundancy).
3. **ARM_HUB_SPOKE_5SPOKE** -- 5 spokes -> hub. One-knob change from 3SPOKE
   (INTRA_LANE_DELTA = spoke count axis).
4. **ARM_HUB_SPOKE_WITH_CFRPE** -- 3 spokes + adaptive cf-RPE plasticity on
   hub gating weights. **PRIMARY pre-registered arm.** Tests whether plasticity
   ADAPTS the gates to improve LM signal vs uniform majority.

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- All ops via torch.cuda (Fix #24); spokes trained in sequence
- INGEST_CHUNK=4096, RECALL_BATCH=256
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- PC encoder per spoke: 3 layers, alpha~0.05, beta~2.0, 1 pass, 100_000 train tokens
- Sparse-bipolar f=0.02 + 1/sqrt(f) amplitude scaling (Stage-1 foundations)
- Hub aggregation: majority-rule (arms 2/3) OR cf-RPE weighted (arm 4)
- cf-RPE: eta=0.02, n_steps=50 (zero-baseline cf-RPE on bigram alignment)

## Reported metrics per arm
- `bpc_best` (at best joint (T*, lambda*))
- `top1_acc`, `mrr_at_10`, `best_T`, `best_lambda`
- `raw_bpc_at_T1_L1` (sanity for DEGEN gate)
- `encoder_meta` (per-spoke PC train wall + recon errors)
- `cfrpe_gates` (PRIMARY arm only): final gate softmax weights per spoke

## Pre-reg HARD bands (PRIMARY arm: ARM_HUB_SPOKE_WITH_CFRPE)

### CHAIN_GRADE (closes gap to word2vec-equivalent WITHOUT leakage)
- best hub arm `bpc_best <= 6.95` AND `cv < 0.05`
- AND sanity-rail OK (baseline within +/- 0.10 of 7.6184)

### HARD_PASS (improves Path C single-spoke by >= 0.40 bits)
- best hub arm `bpc_best <= 7.20` AND `cv < 0.05`
- AND sanity-rail OK

### MIDDLE_BAND
- best hub arm in (7.20, 7.60)
- OR sanity-rail miss (provenance broken; results suspect)
- OR READOUT_DEGENERATE (raw_bpc_at_T1_L1 near vocab-uniform AND no substrate clears unigram)

### HARD_FAIL
- ALL hub-spoke arms `bpc_best >= 7.60`
- (federation doesn't help; hub-spoke principle may not transfer to substrate)

## Master bias checklist disciplines (per encoding drill)
- **Lane 1 declared:** substrate-native (substrate-OWNED encoders only; NO leakage)
- **CONFOUND_AUDIT:** spoke count (3 vs 5); hub aggregation method (majority vs cf-RPE);
  per-spoke alpha/beta diversity
- **INTRA_LANE_DELTA:** arm 3 vs arm 2 varies ONE knob (spoke count: 3->5)
- **Single primary metric:** BPC (Lane 1 substrate-vs-substrate; NOT word-bigram comparison)
- **Pre-register PRIMARY arm:** ARM_HUB_SPOKE_WITH_CFRPE
- **Corpus provenance:** text8 (acknowledged); Lane 1 substrate-vs-substrate comparison
- **CAN-fail discriminators:** sanity rail (provenance can fail symmetric);
  ALL-arms HF and best-arm CG both pre-registered

## Mandatory sanity self-tests (T1-T13)
- T1: char-trigram bipolar primitive
- T2: sparse-bipolar primitive (exact nnz; post 1/sqrt(f) scaled uniq set)
- T3: T=0.01 peaked -> max_prob > 0.5
- T4: T=10.0 peaked -> near-uniform
- T5: joint sweep lambda=0 reproduces unigram BPC (endpoint)
- T6: lambda=1.0 reproduces raw substrate
- T7: MRR@10 on planted 5-pair set
- T8: PC encoder forward shape + L2-norm output
- T9: hub majority-rule bundling preserves bipolar geometry
- T10: cf-RPE weighted hub aggregates N spokes correctly
- T11: verdict bands (CG / HP / HF / MID / SANITY_RAIL_MISS)
- T12: cf-RPE gates evolve under training (softmax weights non-degenerate)
- T13: zero LLM calls at inference

## Routing rationale
- GPU REQUIRED per Fix #24 (torch.cuda for multi-spoke PC training is the dominant cost).
- Timeout 7200s (2h) -- under PROT-019 14400s threshold for `_n>=4096`; anchor has NO
  `_n<N>` suffix so PROT-018/019 not directly applicable.
- atexit synthesizer writes partial metrics.json from completed seeds on SIGTERM/kill.
- Per-seed checkpoint via `_seed_checkpoint` for resume on partial timeout.

## Risk caveat (per task brief)
Gap-map's "existing solutions" may be data-specific (Resonator just showed this). Same
risk here -- encoding drill's recommendation is theoretical until tested. The PRIMARY arm
encodes the strongest version of the hub-spoke + cf-RPE bet; if HARD_FAIL across ALL hub
arms, the hub-spoke principle may not transfer to substrate (route to next encoding drill
recommendation).

## Cites
- `notes/director_stage2_preauthored_dispatch_specs_2026-06-24.md` DISPATCH 3
- `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md` (E1 candidate)
- `experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py` (reference cell)
- `data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json` (sanity rail 7.6184)
- USER 2026-06-23 Path C substrate-owned encoder is THE answer
- USER 2026-06-23 brain-is-existence-proof higher prior for brain-grounded mechanisms
- USER 2026-06-22 Fix #24 (GPU dispatch must use GPU)
- USER 2026-06-22 Fix #26 (predispatch_check: PROCEED 0 prior matching landings)

## Pre-dispatch
- predispatch_check (`substrate_hub_spoke_E1_encoder_v1`): PROCEED (0 matching landings; 0 matching atoms)
- predispatch_check (`hub_spoke`): PROCEED (2 prior smoke landings of related cell SELFTEST_OK; no chain-grade landings)
- Self-test (T1-T13): TO RUN
- Smoke target: < 180s laptop CPU under N_DIM=256 V=200 N_TRAIN=1500 PC_TRAINING_TOKENS=500
