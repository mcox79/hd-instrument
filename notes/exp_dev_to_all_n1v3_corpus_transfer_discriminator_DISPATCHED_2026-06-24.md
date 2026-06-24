# exp_dev DISPATCH: substrate_n1v3_corpus_transfer_discriminator_v1

**Filed:** 2026-06-24T16:42:24Z by exp_dev (Agent Teams; Opus 4.7 1M)
**Recipients:** research (primary, drill author) / cc skunkworks (will VET on land) / cc orchestrator (queue visibility)

## Status

- **Queue:** overnight_queue (GPU runner; torch.cuda)
- **State:** RUNNING since 2026-06-24T12:42:24 (gpu_runner_0)
- **Timeout:** 7200s (2h)
- **Script:** experiments/exp_substrate_n1v3_corpus_transfer_discriminator_v1.py
- **Prereg:** preregs/2026-06-24_substrate_n1v3_corpus_transfer_discriminator_v1.md
- **Commit:** 4156dff8 (path-scoped: cell + prereg only)

## What

Per `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md`, 4-arm
corpus-transfer discriminator resolves whether n1_v3 chain-grade (+61.6% top1;
cert row 699) is corpus-specific (Pythia-residuals) or substrate-general
(text8/word2vec).

Four arms (each FRESH state; 3 seeds at N_DIM=8192 V_C=256 k=25):
1. ARM_TEXT8_WORD2VEC_LOGIT_MIXER -- reference baseline
2. ARM_TEXT8_WORD2VEC_N1V3_READOUT -- PRIMARY TEST
3. ARM_PYTHIA_RESIDUALS_LOGIT_MIXER -- new baseline
4. ARM_PYTHIA_RESIDUALS_N1V3_READOUT -- SANITY/PROVENANCE (cert reproduction)

## Pre-reg HARD bands

- HARD_PASS_SUBSTRATE_GENERAL: text8_n1v3 top1 >= 0.40 AND pythia_n1v3 in
  +/-0.05 of 0.4455 AND cv < 0.05. Substrate has corpus-general +60% top1 path.
- HARD_PASS_CORPUS_SPECIFIC: pythia_n1v3 in sanity rail AND text8_n1v3 < 0.30.
  Chain-grade requires Pythia ingest OR Path C substrate-OWNED encoder.
- HARD_FAIL_PROVENANCE: pythia_n1v3 < 0.40. Cert row 699 fails to reproduce
  on this harness; flag for re-examination.
- MIDDLE_BAND: text8_n1v3 in [0.30, 0.40] OR cv > 0.05 on any PASS arm.

## Verification trail

- Local --self-test PASS in <2s (T1-T10 incl BUGFIX-1 sparse-Willshaw selectivity)
- Local --smoke PASS in 51s on laptop CPU (text8 arms only; Pythia gracefully
  skipped because NPZ is remote-only)
- Remote --self-test PASS in 3.3s on remote .venv
- Remote queue.json shows entry running on gpu_runner_0
- Script size on remote: 66099 bytes (matches local SCP)

## Honest caveats

- N_DIM=8192 differs from cert anchor's N_DIM=4096; the +/-0.05 provenance
  tolerance accommodates this scale port. Drill predicted top1 >= 0.40 at
  N=8192 on home corpus (HARD-PASS) or top1 < 0.38 (would invalidate the
  scale port).
- Pythia unigram log-prob in joint_sweep uses held-set counts (biased toward
  the held tokens' distribution) rather than train. This is a back-off floor
  only; joint_sweep picks best lambda per metric anyway. NOT load-bearing for
  the top1 verdict.
- "ARM_PYTHIA_RESIDUALS_LOGIT_MIXER" is a "decode-D-only" baseline (no W_C
  transition store; just source-concept-code into D). Different mechanism from
  the text8 logit_mixer (which uses outer-product W on bipolar word codes).
  Both are reasonable "no n1_v3 readout" comparators for their respective
  corpora. Calling them both "LOGIT_MIXER" is a slight name-stretch but the
  per-arm metric stays well-defined.

## Next-step for cert chain

When the metrics land (~25-40min remote), Skunkworks VET on:
1. Re-derive each arm's top1 from per-seed (Fix #28 verify-the-referent).
2. Confirm pythia_n1v3 reproduces cert row 699 within tolerance.
3. Confirm cv > 0.05 demote-to-MIDDLE_BAND if any PASS arm is seed-unstable.
4. Classify verdict per pre-reg tier (HARD_PASS_SUBSTRATE_GENERAL /
   HARD_PASS_CORPUS_SPECIFIC / HARD_FAIL_PROVENANCE / MIDDLE_BAND).

If HARD_PASS_CORPUS_SPECIFIC: USER's standing Path C substrate-owned-encoder
directive becomes the load-bearing next step.

## Cites

- notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md (drill source)
- data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json
  (cert row 699 reference: top1=0.4455 across 3 seeds)
- experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.py
  (text8/word2vec scaffolding reused; the failing-replication source the v1 BUGFIX
  closed at top1=0.2128 -- now reproduced inside a matched-config 4-arm cell)
