# Change Request -- Stage A smoke sweep to find crossover N (substrate vs Adam baseline)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Stage A smoke at N=256 HARD_FAIL is operating-mode-specific (capacity-starved); sweep N to find empirical crossover where substrate beats Adam baseline. Cheap fast iteration before committing to full run.

---

## What this is (plain language)

Smoke at N=256 said substrate is 0.2x baseline speed (HF). Honest reason: at N=256 substrate's achievable BPC is small enough that Adam trivially matches it in one epoch. Substrate's advantage emerges at LARGER N where its achievable BPC is harder for Adam to chase.

This change-request sweeps N to find the EMPIRICAL crossover N* where substrate first beats Adam. Below N*: Adam wins (small-N artifact). Above N*: substrate wins (capacity advantage realized).

Cheap. Fast. Honest signal either way.

---

## Capability question

At what substrate dimension N does the substrate-hybrid (cf-RPE + posbind + symW + cosine readout) achieve wall-time advantage vs Adam-softmax baseline on Wikitext-2 char-LM bigram + trigram task?

If N* < 2048: substrate has a realistic advantage at substrate-class scale; proceed to full Stage A run at N=2048.
If N* >= 4096: substrate's advantage only at larger scale; reassess full run target N.
If no crossover detected: substrate-hybrid as currently configured doesn't beat Adam at any tested N; iterate trick selection before full run.

---

## Smoke sweep design

**Anchor:** `substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1`

10 smoke cells (5 N values x 2 tasks; each ~30-60s wall):

### Cells

| Cell | N | Task | Pre-reg HP | Pre-reg HF | P_deflated_HP |
|---|---|---|---|---|---|
| S1 | 256 | bigram | speedup >= 1.5x | speedup < 1.0x | 0.10 (capacity-starved expected) |
| S2 | 256 | trigram | speedup >= 1.5x | speedup < 1.0x | 0.10 |
| S3 | 512 | bigram | speedup >= 1.5x | speedup < 1.0x | 0.20 |
| S4 | 512 | trigram | speedup >= 1.5x | speedup < 1.0x | 0.20 |
| S5 | 1024 | bigram | speedup >= 1.5x | speedup < 1.0x | 0.35 |
| S6 | 1024 | trigram | speedup >= 1.5x | speedup < 1.0x | 0.35 |
| S7 | 2048 | bigram | speedup >= 2x | speedup < 1.0x | 0.50 |
| S8 | 2048 | trigram | speedup >= 2x | speedup < 1.0x | 0.50 |
| S9 | 4096 | bigram | speedup >= 2.5x | speedup < 1.0x | 0.55 |
| S10 | 4096 | trigram | speedup >= 2.5x | speedup < 1.0x | 0.55 |

**Per-cell methodology:**
- Match-BPC speedup: substrate trains to its OWN BPC target at this N; Adam baseline trains to MATCH substrate's BPC; speedup = Adam_wall_time / substrate_wall_time
- 3 seeds per cell (smoke; fast iteration)
- Time-budget cap per smoke: 60s wall to prevent runaway

**Aggregate verdict pattern:**

**Crossover identified (preferred):** S1-S4 HF; S5/S6 transition (MID); S7-S10 HP. Crossover N* ~ 1024-2048. Validates substrate's capacity-scaling advantage. Proceed to full Stage A at N=2048.

**Late crossover:** S1-S8 HF/MID; S9/S10 HP at N=4096+. Crossover above target N=2048. Reassess full run target.

**No crossover:** All cells HF. Substrate-hybrid as configured doesn't beat Adam at any tested N. Drill on WHICH trick is the bottleneck before iterating.

**Anomalies:** trigram beats bigram earlier (substrate's K* extends faster than expected) -- characterize.

## Resource

Local CPU only.

## Cost ceiling

$0 CPU. Per-cell wall ~30-60s. Total: ~10-15 min for all 10 cells.

## Pre-reg discipline (per [[feedback-no-smoke-preframing-in-task-prompts]])

- Each smoke has EXPLICIT HP/MID/HF bands above
- NO implicit PASS expectation: small-N cells (S1-S4) are PRE-REGISTERED as predicted HF per capacity-starvation mechanism
- Crossover N* is the LOAD-BEARING metric, not raw HP count
- Below-crossover HF is HONEST signal of capacity-starvation; above-crossover HF would refute substrate's training-speed claim

## What this is NOT

- NOT a full Stage A replacement (still need full N=2048 run after crossover identified)
- NOT a final verdict on substrate training speed (only smoke signal)
- NOT cloud cost (all CPU)
- NOT a pre-framed HP attempt (S1-S4 expected HF; that's the design)

## Why this is the right move

Per [[feedback-pressure-test-negative-findings]] memory: N=256 HF was operating-mode-specific (small-N capacity-starvation), NOT evidence substrate fails. Smoke sweep at N={256, 512, 1024, 2048, 4096} tests the alternate operating modes (larger N where capacity isn't binding).

If crossover identified at N*=1024-2048: full Stage A at N=2048 is well-justified.
If crossover late (N>=4096): adjust target N before full run.
If no crossover: drill on WHY before iterating tricks.

This is honest cheap iteration before committing to engineering for full Stage A.

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: each cell pre-reg with explicit HP/MID/HF
- Per [[feedback-no-preframe-batch-all-pass]]: small-N cells PRE-REGISTERED as expected HF (no implicit PASS expectation)
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-pressure-test-negative-findings]]: tests alternate operating modes (larger N) where TC0 capacity-starvation doesn't bind
- ASCII-only

PROT-018: anchor uses N-sweep range suffix (no _n prefix per swept-N convention)
PROT-021: source=local CPU, run_mode=smoke, n_seeds=3

---

**END.**

**Exp-Dev:** ~10-15 min total CPU for 10 smoke cells. Reuses Stage A scaffold; just varies N parameter. Crossover N* finding drives full Stage A target N + trick selection adjustment.

**Research session:** holds for smoke sweep verdict; revises Stage A full run based on crossover finding.
