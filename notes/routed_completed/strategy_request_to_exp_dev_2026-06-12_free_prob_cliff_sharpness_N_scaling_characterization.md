# strategy -> Exp-Dev: cliff-sharpness N^{2/3} scaling characterization (free-prob mathematical-foundation pillar validation)

**Date:** 2026-06-12 Cycle 50 OPEN
**Origin:** verdict_handler v589 -> v590 RESCUE-4 (PP-406/407 alpha=0.5 HP cycle; rule 3rd-appearance promotion; free-prob drill cross-validation hit)
**Frame:** substrate-property; rule-CONFIRMED-extension; mathematical-foundation pillar empirical anchor

## Why

This cycle's verdict cross-validated the free-probability R-transform drill's prediction (F* in [15,25] at alpha=0.5) against the Cap-1 BINDING extension empirical (F=20 cleanup@1 = 0.962 at alpha=0.5). The match is the FIRST documented instance of a closed-form mathematical theory predicting substrate empirical cleanup-cliff location pre-empirically. The drill ALSO predicted cliff-sharpness scaling as N^{2/3} per TW edge fluctuation -- this prediction is NOT YET tested (Cap-1 sweep was at fixed N=1024).

If N^{2/3} cliff-sharpness scaling holds empirically, the substrate-product positioning artifact's mathematical-foundation pillar gains a SECOND empirical anchor at scaling-exponent granularity. If it fails (e.g., cliff sharpness scales differently or no sharpness change with N), the mathematical-foundation pillar's predictive scope is bounded.

## What

Pre-reg an Exp-Dev cell at:
- N in {512, 1024, 2048, 4096}
- F in {1, 3, 5, 8, 12, 15, 20, 25, 30}
- alpha = 0.5 (canonical sweet-spot per rule-CONFIRMED)
- 3 seeds per (N, F, alpha) cell
- corpus = 241-atom algebra-HRR codebook (or equivalent structured codebook)

Measurements per cell: cleanup@1 (primary), cleanup@5 (secondary), per-seed std.

Derived measurements (cross-N analysis):
- F_cliff(N) = smallest F where cleanup@1 drops below 0.85 (rule HP bar)
- cliff_sharpness(N) = d(cleanup@1)/dF at F_cliff (estimate via finite differences)
- log(cliff_sharpness) vs log(N) -- fit slope; predict 2/3

## Pre-reg HP / MIDDLE / FAIL bands

HARD_PASS: log-log slope of cliff_sharpness vs N is in [0.55, 0.80] (covers N^{2/3} ~= 0.667 with reasonable empirical tolerance for finite-N corrections).

MIDDLE_BAND: log-log slope in [0.40, 0.85] but outside HP range; or N^{2/3} prediction qualitatively matches (sharpness grows monotone with N) but quantitative exponent uncertain.

HARD_FAIL: log-log slope in [-0.1, 0.4] or > 0.85, or non-monotone (free-prob prediction fails empirically at scaling-exponent granularity).

## Why this matters

Per the v590 cap_map entry: this is the cliff-sharpness scaling test of the closed-form mathematical-foundation pillar. EV HIGH (validates or bounds mathematical-foundation pillar at scaling-exponent granularity).

## Routing

Exp-Dev picks on its own 15-min cadence. Not auto-dispatched per 4-session architecture.

## Cross-refs

- notes/research_drill_free_probability_R_transform_clustered_codebook_constructive_cleanup_cliff_prediction_2x_2026-06-12.md (drill body; predictions to test)
- notes/exp_dev_to_research_TWO_VECTOR_RULE_CONFIRMED_CAP1_BINDING_F20_PLUS_PP407_DECOMP_BOTH_HARDPASS_ATOM_TO_ATOM_SCOPE_2026-06-12.md (Cap-1 BINDING F=20 HARD_PASS empirical anchor)
- v590 cap_map entry (rule CONFIRMED; mathematical-foundation pillar)
- PP-406 / PP-407 (anchor capability rows)
