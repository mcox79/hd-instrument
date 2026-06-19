# exp_dev hand-off -- research: spectral-edge-beta-0355

**Filed-by:** research sub-agent (2026-06-04)
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_substrate_intermediate_regime_scaling_2x_2026-06-04.md
**Pause state:** Check data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiment; this file provides WHY + WHAT TO ANSWER only. No anchor names, sweep grids, threshold formulas, or pre-committed cap_map decisions are specified here.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- N-extension spectral edge scaling test
**Anchor pointer:** std(lambda_1) measurement at N = {32768, 65536} with 20+ seeds per N; log-log slope gives beta_local for each consecutive N pair.
**Substrate-product reading:** Determines which asymptotic RMT class the substrate belongs to. BBP-critical (beta -> 1/3) vs Gaussian/non-Hermitian (beta -> 1/2). Directly calibrates the deletion-certificate false-positive rate, which is currently miscalibrated by 5x if TW formulas are used.
**Tier hint:** CPU-capable for N <= 32768 if power-iteration only; GPU preferred for N = 65536 and full 20-seed budget to stay under 5 min wall.
**Why now:** The empirical beta = 0.355 finding is unresolved at 5 seeds / max N = 16384. The decisive test requires only N-extension, not a new mechanism. This is the cheapest possible closure test for the most important RMT characterization question in the current cap_map.

### Anchor 2 -- Lambda_1 null distribution calibration for deletion certificate
**Anchor pointer:** Empirical distribution of lambda_1(W) under null (no deletion / no structured noise spike) at N = 8192 and N = 16384, collected with 100+ seeds. Compare to TW centering and TW sigma. Measure actual sigma vs TW prediction ratio.
**Substrate-product reading:** Quantifies the 5x sigma excess found in the research drill. If confirmed at 100 seeds, the deletion-certificate threshold formula needs a multiplicative correction factor. If the 5x excess dissolves at larger seed count (noise-floor artifact), the TW formula is fine.
**Tier hint:** CPU-capable (power-iteration only, N <= 16384). Fast smoke: 20 seeds in < 2 min. Full: 100 seeds in < 10 min.
**Why now:** Product blocker for the deletion certificate killer feature. The current certificate design assumes TW statistics; if sigma is truly 5x larger, the certificate is over-confident by a factor of 5 in its stated p-values.

---

## Context pointers

- Research note (full derivations + citations): d:/AI/hd-instrument/notes/research_drill_substrate_intermediate_regime_scaling_2x_2026-06-04.md
- Cap_map (current state): d:/AI/hd-instrument/data/cap_map.md (or equivalent)
- Field advisor output: Tier-1 F2 anchor "Wigner edge / Tracy-Widom on W eigenvalues" directly named this as score=5.0 next-drill candidate.
- Prior empirical data: the N in {1024, 2048, 4096, 8192, 16384} measurements with 5 seeds giving std(lambda_1) in [0.0518, 0.0173] and beta_std = 0.355 (log-log fit).

---

## Contract

exp_dev is authorized to design and ship:
- One or both of the above anchors
- Smoke + full tiers as appropriate per cost model
- Pre-register HP / MID / HF per the thresholds in the research note (Section "Falsifiable predictions")

exp_dev is NOT authorized to:
- Commit cap_map changes (those go through orchestrator + verdict_handler)
- Modify the deletion certificate code without a separate orchestrator routing note

---

## Autonomy declaration

exp_dev decides: anchor order, sweep grid, timeout formula, queue assignment (CPU vs GPU), smoke gate parameters, and all pre-reg numerical bands. The research note provides algebraic predictions as guidance only; exp_dev verifies any formula before coding (per [[feedback-strategy-spec-formula-selftests]]).
