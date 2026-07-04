# DIRECTOR-PRELIMINARY re-audit: Probe 1 STORAGE x CLEANUP cross-term vs noise floor

**2026-07-04. NOT authoritative — Skunkworks to ratify before any cert mutation.**
Continues the family null-audit that the weekly agent rate-limit killed mid-run.
Script: `scratchpad/probe1_reaudit_mc_null.py` (reproduce-check-first; ASCII).

## Method

For each BUNDLED subregime cell (M,N,corruption), 3 cleanup mechanisms each give an
accuracy over TR=100 trials (independent salts per mechanism — no trial pairing,
verified vs P8 note). The stored `mechanism_variance_at_BUNDLED` is the **range**
(max-min) of the 3 mechanism accuracies — VERIFIED by exact reproduce (recomputed vs
stored, max|diff| = 2e-17). Under H0 (mechanisms identical) the 3 accuracies are iid
Binomial(TR, p_cell)/TR with p_cell = cell mean acc. Data-driven MC null (20000 draws,
each cell's OWN p_cell and TR).

## Result — the mechanism cross-term is INDISTINGUISHABLE FROM NOISE

Pooled 36 BUNDLED cells (12 subregimes x 3 seeds {7,13,19}):

| statistic | observed | null mean | null sd | z | P(null >= obs) |
|---|---|---|---|---|---|
| MAX range | 0.1200 | 0.1353 | 0.0248 | **-0.62** | 0.79 |
| MEAN range | 0.0306 | 0.0351 | 0.0041 | **-1.13** | 0.88 |
| COUNT(>0.02) | 16/36 | 18.0/36 | 1.53 | **-1.30** | 0.94 |

**In ALL THREE statistics the observed value is BELOW the binomial-noise null mean.**
The atom's headline per-seed max mechanism-range (0.10/0.12/0.09) is LOWER than pure
noise produces (null max mean 0.135). The mechanism-moderation "signal" is weaker than
the sampling noise it sits in. Same failure mode as the P8 demote (2026-07-04,
z=0.40) — the whole "axis moderates CLEANUP_MECHANISM" family runs on a TR=100 noise
floor.

## What SURVIVES vs what FALLS (split the atom — symmetric verify)

- **SURVIVES (untouched by this audit):** the STORAGE main effect. median storage gap
  SHARDED - BUNDLED = **0.93** (per atom + metrics `median_storage_gap`). That is an
  enormous, real effect, unrelated to any mechanism-variance noise floor. Probe 1 is
  NOT worthless — "storage strategy dominates readout quality" stands firmly.
- **FALLS (DEMOTE-CANDIDATE):** the STORAGE x CLEANUP mechanism cross-term — the
  "mechanism choice matters ONLY at BUNDLED, not at SHARDED" interaction. The BUNDLED
  side is binomial noise; the SHARDED 0/36 is ceiling-pinned (acc~1.0, zero-variance by
  construction — no evidential weight either way). The categorical 24/36-vs-0/36
  contrast is confounded: SHARDED zeros are forced, BUNDLED "firing" is noise.

## Family-wide implication (HIGH)

If Probe 1 (the strongest, 3-seed GPU HARD_PASS cross-term) is a noise artifact, then
the entire mechanism-moderation cross-term family is suspect at TR=100:
- **P8** ALGEBRA x CLEANUP — already DEMOTED (z=0.40).
- **P1** STORAGE x CLEANUP — this audit: DEMOTE-CANDIDATE (cross-term only).
- **P6v2 / P7v2** (TOPOLOGY/N x CLEANUP, MM_TENTATIVE, MIDDLE_BAND) — same audit needed;
  near-certain to also be noise-floor.

**Revival path for ALL:** TR >= 400 (null range sd scales ~1/sqrt(TR); at TR=400 the
null max drops ~2x, and a genuine 0.10 mechanism effect — if real — would then clear).
These cells run in ~3-11s FULL, so a TR>=400 re-run is CHEAP (local CPU subprocess
feasible; no GPU needed). This is the correct negatives-2x revival, not a permutation
test on the existing (underpowered) data.

## Discipline note (candidate meta-atom, Skunkworks tier)

The regime-map cross-term discriminators (range/max of mechanism accuracies at TR=100)
were NEVER gated against a data-driven binomial noise floor at pre-reg — the extreme-
value-null meta-atom filed at the P8 demote (`9825af151`) must be applied RETROACTIVELY
to the whole family. Recommend a family SCHEMA-VET sweep + TR>=400 revival bundle.

## Status
- **NO cert ledger mutation performed.** This is a Director estimate.
- Skunkworks must ratify (independent reproduce + confirm unpaired-null assumption +
  decide split-atom tiers) before demoting the Probe 1 CG_META.
- If ratified: Probe 1 -> split into `STORAGE_MAIN_EFFECT` (CG-grade, 0.93 gap) +
  `STORAGE_x_CLEANUP_cross_term` (DEMOTE to MIDDLE_BAND / noise-floor, revival at TR>=400).
