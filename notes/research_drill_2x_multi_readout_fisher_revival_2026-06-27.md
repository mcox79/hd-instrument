# Research Drill 2x — multi_readout_fisher_importance_v1 Revival

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** smoke HARD_FAIL Fisher=+0.039 lift=+0.089 cv=1.230 cor=0.085 n=2 at N=2048, M=100, K_max=4 (toy-scale smoke).
**Parent drill:** `research_drill_5x_importance_ceiling_barrier_2026-06-27.md`
**Cell artifact:** `data/exp_multi_readout_fisher_importance_v1_smoke/metrics.json`

---

## FIX #28 HONEST RE-READ FIRST (per `feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text`)

The verdict_msg headline `Fisher=0.039 Single=-0.049 Two=-0.108 | lift=0.089` UNDER-REPORTS the cell. Reading per_arm raw:

| Arm | Seed 7 sel_unretr | Seed 17 sel_unretr | Mean | Best per-seed | cv | cor with W |
|---|---|---|---|---|---|---|
| single_readout_baseline | -0.082 | -0.017 | -0.049 | n/a | 0.66 | 0.076 |
| two_readout_avg | -0.108 | -0.109 | -0.108 | n/a | 0.005 | 0.018 |
| eight_readout_fisher | **+0.087** | -0.009 | +0.039 | +0.087 | 1.23 | 0.085 |
| eight_readout_pca_basis | -0.005 | **+0.144** | +0.070 | +0.144 | 1.07 | 0.070 |
| diag_k_sweep | +0.037 | **+0.300** | +0.168 | +0.300 | 0.78 | 0.000 |

Three critical honest reads the verdict_msg buried:
1. **PCA-basis arm beat Fisher arm** (mean +0.070 vs +0.039) — PCA basis is the right geometric choice and was already in the pre-reg.
2. **diag_k_sweep arm hit +0.30 on one seed at cor=0.0** — that's chain-grade if it replicates; fairness perfect.
3. **Smoke ran at N=2048, M=100, K_max=4** (toy regime); the real cell pre-reg targets N=8192–32768, M=4096, K=8–16. Smoke isn't testing what the cell will measure. cv=1.23 at n=2 means population mean of Fisher arm could plausibly be anywhere in [-0.05, +0.13].

This isn't strong evidence the ceiling exists; it's the smoke being underpowered. The verdict_msg framing pushed me toward "ceiling confirmed" — wrong.

---

## ANGLE A — STATISTICAL / MEASUREMENT REVIVAL

### A.1 Seed-budget calculation
For cv=1.23 (worst arm) → 95% CI on the mean at n=2 is roughly ±2·(0.048/√2) = ±0.068. We literally cannot see a +0.089 lift through that noise. Required n for ±0.02 CI: n ≥ (1.96·0.048/0.02)² ≈ 22 seeds. Realistic: **n=12 (chain-grade), n=8 (revival-evidence)**.

### A.2 Proposal A1 — Same cell, full N, 8 seeds, drop the broken arms (CHEAPEST)
Re-dispatch the same `multi_readout_fisher_importance_v1` cell at **production scale (N=8192, M=4096, K_max=16, n=8 seeds)**, KEEP `eight_readout_pca_basis` + `eight_readout_fisher` + `diag_k_sweep` + `single_readout_baseline` as control, **DROP `two_readout_avg`** (it was destructive at -0.108 in smoke — cell-author intuition was right; 2 readouts is the worst case for orthogonal-basis fusion because you can't average-out the bias). Discriminator: PCA-basis mean ≥ +0.10 AND cv ≤ 0.30 across 8 seeds.

### A.3 Proposal A2 — Gram-Schmidt orthogonalize bases against substrate's actual PCA
The smoke's "PCA-basis" arm presumably used a fresh PCA on the substrate snapshot, but the random-Gaussian arm assumed orthogonality that doesn't hold in substrate's anisotropic geometry (Mu-Viswanath / cert 678 lock-in finding). New arm: project each candidate readout vector orthogonal to the top-32 substrate principal components via Gram-Schmidt **then** normalize. Predicted lift: random-Gaussian arm goes from "destructive" to "comparable to PCA-basis" (+0.05 to +0.10 over current); makes the Fisher-fusion math actually apply.

### A.4 Proposal A3 — Fisher weights from data, not assumed-equal
The current `eight_readout_fisher` arm uses Fisher-info weighting where each readout's variance is estimated from the SAME data being scored — that's circular / over-fit at small M. Use **held-out variance estimation** (split M=4096 atoms into 2048 fit + 2048 score; estimate I_k on fit, weight on score). Brain analog: PFC weights neuromodulator channels based on context-prior, not current measurement. Predicted: removes the over-fit collapse seen in seed 17 (-0.009).

---

## ANGLE B — MECHANISM REVIVAL

### B.1 Cramér-Rao independence problem
The Fisher-fusion derivation requires INDEPENDENT readouts; per-arm cor=0.085 looks low but is measured pairwise — joint independence across 8 readouts is much weaker. The smoke's `cor_with_W` is the WRONG quantity (correlation with the substrate matrix); we need **pairwise readout-readout correlations**, which the cell doesn't currently report. If true joint rank of the 8 readouts is ~3, "k=8" is actually k_eff=3 and the predicted variance reduction is √3 not √8.

### B.2 Proposal B1 — Multi-CHANNEL × multi-readout (compose with cell 3.A from parent drill)
Instead of 8 readouts of ONE signal (TRACE), use **k=4 readouts PER channel × 4 channels = 16 total**: TRACE / SURPRISE / PHASE / NOVELTY each get 4 PCA-basis readouts. Channels are orthogonal by construction (different substrate signals), so k_eff ≈ 12–16 not 3. Predicted: breaks Cramér-Rao that single-signal multi-readout cannot, because the 4 channels carry truly independent information. This IS the cell 3.A from the parent drill, upgraded with the multi-readout machinery.

### B.3 Proposal B2 — Lock-in amp AS the readout (cert ledger 678 composition)
Replace dot-product readout with the lock-in-amplifier primitive (chain-grade cert 678 — already proven, no new infrastructure). Per-readout: modulate atom_j's importance at f_ref=1/4 over consolidation cycles, correlate score time-series with cos(2πf_ref·t). The 1/f noise (cor=0.085 cross-atom interference) is REJECTED at f_ref. Predicted: sel_unretr +0.10–0.15 single-readout; +0.15–0.22 with k=4 PCA-basis lock-in readouts. **High prior because the underlying primitive is chain-grade.**

### B.4 Proposal B3 — Two-stage gated readout (sparse-competitive K-WTA composition)
Stage 1: multi-readout extracts top-200 candidate atoms (high-recall, low-precision). Stage 2: single optimal-projection readout on the 200-atom subset (low-noise; only 200 cor-pairs vs 4096²). Brain analog: hippocampal coarse recall → cortical refinement. Brings in the substrate_sparse_competitive_readout MIDDLE_BAND result — composing two MIDDLE_BAND mechanisms often super-adds. Predicted: +0.12–0.18 on full-population AUC; tagged-subset AUC much higher (matches cell 3.C engram framing).

---

## TOP-2 REVIVAL CELLS

### TOP-1: lock_in_amp_pca_readout_fisher_v1 (composes B2 + A2 + A1)
- **Arms:** ARM_SINGLE_DC (baseline) / ARM_K4_PCA_DC / ARM_K4_PCA_LOCKIN_F4 / ARM_K8_PCA_LOCKIN_F4 / ARM_K8_PCA_LOCKIN_FISHER_HELDOUT (full stack)
- **Falsifiable discriminator:** ARM_K8_PCA_LOCKIN_FISHER_HELDOUT mean sel_unretr ≥ +0.15 with cv ≤ 0.25 across n=8 seeds at N=8192, M=4096. Fairness gate cor(imp, |W|) < 0.30 per Fix BIAS-Q.
- **Honest-bound:** if K8-LOCKIN_FISHER is within ±0.02 of K4-PCA-DC, lock-in is not adding; ceiling confirmed; bank honest-bound atom.
- **Cost:** ~3 CPU-hr; **GPU eligible: YES** (k=8 readouts × M=4096 atoms × 8 seeds = 8192·4096·64 matmul = matrix-heavy; route via hdi_orchestrator per Fix #24).
- **Why high prior:** combines THREE chain-grade primitives (cert 678 lock-in, PCA-basis already best in smoke, held-out variance estimation).

### TOP-2: multi_channel_multi_readout_v1 (composes B1 + parent cell 3.A)
- **Arms:** ARM_SCALAR_TRACE / ARM_4CHANNEL_NO_READOUT / ARM_4CHAN_K1_PCA / ARM_4CHAN_K4_PCA_FISHER (k_eff=12-16) / ARM_4CHAN_K4_PCA_FISHER_LEARNED (logistic-regression fusion weights)
- **Falsifiable discriminator:** ARM_4CHAN_K4_PCA_FISHER_LEARNED mean sel_unretr ≥ +0.15 AND beats best single-channel by ≥ +0.05 AND pairwise channel cor < 0.50 (channels truly orthogonal). n=8 seeds, N=8192, M=4096.
- **Honest-bound:** if pairwise channel cor ≥ 0.65 at pre-flight, channels are degenerate (substrate doesn't actually represent them independently); kill the cell pre-tier, file the negative finding, multi-channel is FALSE.
- **Cost:** ~5 CPU-hr (PHASE channel needs new timestamp-tracking primitive); **GPU eligible: PARTIAL** (matmul heavy YES; timestamp logic CPU). Route encoding to GPU, fusion to CPU.
- **Why high prior:** brain's existence proof (no scalar importance anywhere in neuroscience) + Fix #28 from smoke (per-seed +0.30 on the diag K-sweep arm at cor=0.0 hints that high-dim readouts CAN extract signal).

---

## HONEST-BOUND ASSESSMENT

**The smoke does NOT confirm the substrate physics ceiling.** Three reasons:
1. n=2, cv=1.23 → 95% CI is ±0.07; can't distinguish +0.05 from +0.13.
2. PCA-basis arm and diag_k_sweep arm hit per-seed maxima of +0.144 and +0.300 with low cor — high-value signal is there, just noisy.
3. Smoke ran at toy scale (N=2048, M=100) not production scale.

**Banking honest-bound NOW would be premature.** Re-dispatch TOP-1 at full scale first; if TOP-1 lands ≤ +0.05 with cv ≤ 0.10 (clear failure), the ceiling is real and we bank then. **If both TOP-1 AND TOP-2 land MIDDLE_BAND-or-below at full N with n=8 seeds, THAT is when we bank `M_CFU_honest_bound_substrate_importance_ceiling` atom and commit to Path C substrate-owned encoder.**

**Recommended sequence:**
1. Spawn `hdi_orchestrator` to dispatch TOP-1 on GPU (3 CPU-hr; matrix-heavy → use cuda matmul + batched-over-seeds per Fix #24).
2. While TOP-1 runs, parent thread prepares TOP-2 pre-flight signal-independence test (cheap CPU test: just measure pairwise channel cor on existing W). If channels degenerate, TOP-2 cancelled before dispatch.
3. If TOP-1 HARD_PASS: chain-grade importance unlocked; revival succeeded.
4. If TOP-1 MIDDLE_BAND + TOP-2 MIDDLE_BAND: bank ceiling atom; pivot to Path C encoder.
5. If TOP-1 HARD_FAIL but TOP-2 HARD_PASS: multi-channel is the answer, scalar fusion isn't.

---

## ARTIFACTS REFERENCED

- `d:/AI/hd-instrument/data/exp_multi_readout_fisher_importance_v1_smoke/metrics.json` (smoke per-arm raw)
- `d:/AI/hd-instrument/notes/research_drill_5x_importance_ceiling_barrier_2026-06-27.md` (parent drill; cells 1.A, 2.A, 3.A originate here)
- `d:/AI/hd-instrument/notes/research_to_skunkworks_M_CFU_honest_bound_atomization_request_2026-06-27.md` (premature honest-bound request — RECONSIDER pending TOP-1)
- Cert ledger 678 (lock-in amp chain-grade primitive — reusable for B2)
- `feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md` (the rule that caught the verdict_msg framing)
- `feedback_fix24_gpu_dispatch_must_actually_use_gpu_USER_2026-06-22.md` (route TOP-1 via cuda matmul)
- `feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md` (TOP-2 multi-channel prior boost)
