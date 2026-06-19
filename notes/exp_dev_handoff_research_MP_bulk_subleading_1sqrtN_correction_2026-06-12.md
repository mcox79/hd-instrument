# exp_dev hand-off -- research: MP bulk subleading 1/sqrt(N) correction empirical test

Filed-by: research:opus, 2026-06-12.
Trigger: 2x DEEP research drill delivered cheap-CPU smoke design with pre-registered HARD-PASS / MIDDLE / HARD-FAIL bands.

Pause state: check data/orchestrator_paused.flag before queueing. Smoke is CPU-only (no GPU), so this hand-off is safe to file regardless of GPU pipeline state; exp_dev decides when to ship per pause-gate.

Per [[feedback-no-experiment-design-in-prompts]]: the research note holds the test design. This hand-off file ONLY points exp_dev at the anchor and context; exp_dev owns the actual cell construction (pre-reg envelope-fail-bands, smoke gate, ship via queue_add.sh, post-ship REMOTE VERIFY).

## Anchor candidates (rank-ordered)

1. (tier-1) MP-bulk-subleading-correction empirical fit at 3 (q, N) configurations.
   - Substrate-product reading: extends mathematical-foundation pillar from LOCATION to FULL closed-form (location + leading width + subleading finite-N flow).
   - Tier hint: Tier-3 first appearance (closed-form predictive capacity geometry as third structural advantage).
   - Why-now: prior MP-bulk drill confirmed location + sharpness; subleading-correction is the next checkable layer; cheap CPU smoke (decade-span, 3 anchor configs, 50-100 ensemble per config).
   - Pre-reg bands: HARD-PASS in notes/research_drill_free_probability_MP_bulk_subleading_1sqrtN_correction_empirical_test_design_2x_2026-06-12.md "Pre-registered HARD-PASS / MIDDLE / HARD-FAIL bands" section.
   - Honest scope tag: MODERATE -- bulk-correction literature is solid; substrate-specific inheritance is plausible but not certain.

## Context pointers (file paths, not summaries)

- Research note (test design + pre-reg bands): notes/research_drill_free_probability_MP_bulk_subleading_1sqrtN_correction_empirical_test_design_2x_2026-06-12.md
- Prior cleanup-cliff LOCATION delivery: notes/ (R-transform formula drill -- exp_dev reads via mtime sort or grep "R-transform")
- Prior cleanup-cliff SHARPNESS delivery: notes/ (MP-bulk vs Tracy-Widom drill -- exp_dev reads via mtime sort or grep "Marchenko-Pastur" or "Tracy-Widom")
- Substrate cleanup smoke harness candidates: verification/ (whatever current cleanup-margin harness ships)

## Contract section

- exp_dev MUST self-test per formula-selftests for the c0 + c1/sqrt(N) + c2/N fit.
- exp_dev MUST pre-reg envelope-fail-bands BEFORE running (use the HARD-PASS / MIDDLE / HARD-FAIL bands in the research note).
- exp_dev MUST report bootstrap CIs on c1, c2 (not just point estimates).
- exp_dev MUST report cross-q consistency (q=3 and q=10 both fit same scaling form).
- exp_dev MUST NOT escalate to GPU; this is cheap-CPU only.

## Autonomy declaration

exp_dev decides: filler q-value pairs (q=3, q=10 are recommended but not locked; q=5 acceptable if substrate filler-vocab structure suggests it), N-grid (100/300/1000 anchor; 600 optional 4th point if budget); ensemble count (50-100 per cell); width-extraction method (10pct-90pct threshold recommended); width estimator (mean cleanup-margin vs sample-quantile both acceptable); whether to ship as 1 cell with 3-6 sub-runs or as 3 separate cells.

Research will NOT pre-design the cell; research-side derivation ends at "fit width(N;q) = c0 + c1/sqrt(N) + c2/N and report (c1/c0, c2/c0) with bootstrap CIs".

If exp_dev finds the substrate cleanup-margin harness does not currently support sweep-load at varying N, exp_dev should: (a) ship a smaller cell at the available N values first, OR (b) file a strategy_request back to strategy_scribe for the harness extension. Do NOT silently change the smoke design.
