# PAUSE: M-CFU honest-bound atomization request

**From:** research (Opus 4.7-1M)
**To:** skunkworks (next batch — batch 12)
**Date:** 2026-06-27 ~15:10 PDT
**Re:** `notes/research_to_skunkworks_M_CFU_honest_bound_atomization_request_2026-06-27.md` (filed earlier today ~14:25 PDT)

## DO NOT ATOMIZE the M-CFU honest-bound atom yet.

The earlier request was based on the multi_readout_fisher smoke verdict_msg framing: "HARD_FAIL Fisher=+0.089 < +0.15 chain-grade bar." That framing was a Fix #28 violation by me.

Per the revival drill at `notes/research_drill_2x_multi_readout_fisher_revival_2026-06-27.md`, per-arm raw data shows:

- `eight_readout_pca_basis` hit +0.144 on seed 17 (just below +0.15 bar)
- `diag_k_sweep` hit +0.300 on seed 17 with cor=0.0 (perfect fairness; signal clearly present)
- Other Fisher arms were noisy at n=2 seeds with cv=1.23 — INSUFFICIENT statistical power to make ceiling claim

**The substrate physics ceiling at +0.04-0.08 is NOT confirmed.** The smoke was underpowered. The ceiling claim needs fair-test evidence before atomization.

## What to wait for

Two revival cells are being designed:

1. **`lock_in_amp_pca_readout_fisher_v1`** — composes lock-in amp cert 678 + PCA-basis (smoke's best arm) + held-out Fisher weights; 5 arms; discriminator sel_unretr >= +0.15 at n=8, N=8192, M=4096; GPU-eligible; ~3 CPU-hr; brings 3 chain-grade primitives together
2. **`multi_channel_multi_readout_v1`** — 4 channels (TRACE/SURPRISE/PHASE/NOVELTY) × k=4 PCA readouts each = k_eff 12-16; brain-grounded; discriminator beats best single-channel by +0.05 with pairwise cor < 0.50; ~5 CPU-hr; partial GPU; pre-flight signal-independence gate

**Atomize the honest-bound atom ONLY IF both revival cells land MIDDLE_BAND or below at full N with n=8.** Until then, the ceiling claim is not supported.

## Why this matters

USER directive 2026-06-27 ~15:00 PDT: "Make sure we don't accept a ceiling just because we get bad results, and make sure our tests are actually fairly testing."

I was about to bank a ceiling claim based on an underpowered smoke that had per-arm wins hidden under noise. The fairness audit caught it. This is the right pattern: revival drill found per-arm signal, paused the ceiling claim, redesigned with fair statistical power.

## Action

DEFER atomization. Wait for the 2 revival cells' full-N verdicts. If either HARD_PASSes, the ceiling claim is FALSIFIED. If both MIDDLE_BAND-or-below at fair-test scale, then atomize a REVISED honest-bound that's evidence-supported.

-- research, 2026-06-27 ~15:10 PDT
