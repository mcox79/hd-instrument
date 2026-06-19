# Pre-reg: Wave 14 Bet S K-ceiling Diagnosis v1

**Filed:** 2026-05-22
**Source:** Research Entry 113 (`research_decisions_2026-05-21.md`, 2026-05-22 morning) — Bet S K-ceiling diagnosis design.

## Question

At K=200 (above current Bet S ceiling K_crit ≈ 130 at N=4096), which of three Research-identified mechanisms restores accuracy when its knob is varied?

Research priors:
- **Cleanup cross-talk** (P=0.75): K_crit = D / (2 log M); smaller M restores acc.
- **Hopfield blackout** (P=0.50): K_crit = 0.138·D (AGS); softer β (modern-dense-AM) restores acc.
- **Capacity / binding noise** (P=0.25): scales with √(D/(K-1)); higher N restores acc.

## Hypothesis

H_cross_talk: M-sweep wins. Reducing num_entities from 200 → 50 restores subject_acc by ≥ 0.20 at K=200, while β-sweep and N-sweep produce <0.20 gains.

H_compound: 2 or 3 of {M, β, N} all restore acc — failure is compound (matches Research's compound-diagnosis prior).

## Pre-declared verdicts

- `KCEIL_M_LIMITED` — only M-sweep restores ≥ 0.20 (cross-talk dominant).
- `KCEIL_BETA_LIMITED` — only β-sweep restores ≥ 0.20 (Hopfield blackout dominant).
- `KCEIL_N_LIMITED` — only N-sweep restores ≥ 0.20 (capacity dominant).
- `KCEIL_COMPOUND` — 2+ knobs restore ≥ 0.20.
- `KCEIL_NONE` — no knob restores ≥ 0.20 (fundamental ceiling at K=200).
- `KCEIL_INCONCLUSIVE` — metric collection error.

## Method

- Baseline: K=200, N=4096, M=num_entities=200, β=∞ (argmax cleanup). subject-slot acc.
- M-sweep: hold N=4096, β=∞; vary M ∈ {50, 100, 200, 400, 800}.
- β-sweep: hold N=4096, M=200; vary β ∈ {1, 4, 16, 64, ∞}; β<∞ uses softmax-weighted state then argmax (modern dense AM cleanup).
- N-sweep: hold M=200, β=∞; vary N ∈ {4096, 8192, 16384}.
- 60 trials per config; single seed=17.
- Best-of-sweep = max acc over that sweep.

## Acceptance thresholds

- RESTORE_DELTA = 0.20 (knob must restore at least 20pp acc to count as "limiting").

## Config

- K_test=200, n_trials=60 full, single seed=17.
- N_base=4096, M_base=200, β_base=∞.
- Full sweeps as above; smoke uses 3 values each + N=1024 base.

## Pre-declared interpretation

- **M_LIMITED**: cross-talk hypothesis confirmed. Mitigation: subset partitioning OR Kerdock codebook (which gives smaller-effective-M via orthogonality).
- **BETA_LIMITED**: Hopfield blackout confirmed. Mitigation: modern dense AM cleanup at moderate β (relates to Bet Y V2.D Phase 1 — but that was REFUTED at N=4096 multi-β; reconciliation needed).
- **N_LIMITED**: capacity-bound confirmed. Aligns with V2.D Phase 1 N=65536 substrate-scale-up path.
- **COMPOUND**: matches Research's primary diagnosis (cross-talk + blackout co-act). Both mitigations needed.
- **NONE**: K=200 is the true ceiling. Closing K-extension path at current substrate arch.

## Not in scope

- K ≠ 200 (single K-test; this is diagnosis, not K-sweep).
- Kerdock or non-random codebooks (random BSC per Bet S baseline).
- Relation / object slot (subject-slot only; symmetry tested elsewhere).
