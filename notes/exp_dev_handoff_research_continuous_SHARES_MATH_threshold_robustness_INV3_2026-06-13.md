# exp_dev hand-off — research: continuous SHARES_MATH threshold-robustness (INV-3)

Filed-by: research:opus-4-7
Date: 2026-06-13
Trigger: skunkworks INV-3 flag — boolean SHARES_MATH may produce threshold-artifact archetype partition; research drill delivered.

Source research note: d:/AI/hd-instrument/notes/research_DRILL_continuous_SHARES_MATH_threshold_robustness_skunkworks_INV3_support_2026-06-13.md

## Pause state

Honor d:/AI/hd-instrument/data/orchestrator_paused.flag if present. Anchor candidates below are queue-refill candidates ONLY — do not ship while paused.

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off names anchors and points to the research note. It does NOT prescribe experimental design. exp_dev authors envelopes, fail-bands, and ship sequence autonomously.

## Anchor candidates (rank-ordered)

### Anchor 1: CELL INV-3a — continuous SHARES_MATH score authoring + boolean-correlation sanity check
- Substrate-product reading: validates whether a continuous score recovers the existing boolean signal as a coarsening (HP-1 in research note). Cheap precondition for the sweep.
- Tier hint: T0-infra (no theoretical risk; score implementation + Spearman correlation)
- Why-now: cheapest possible first cell; if HP-1 fails for Score #1, fall back to Score #2 or #3 before authoring the full sweep. Saves 1-2 hrs CPU if score is invalid.
- Compute hint: ~10-20 min CPU local on existing 61 atoms.

### Anchor 2: CELL INV-3b — tau-sweep + archetype-count plateau measurement
- Substrate-product reading: the decisive cell. Measures whether 12-archetype partition is threshold-robust (HP-2 + HP-3) or threshold-artifact (HF-1). Outcome directly answers skunkworks flag.
- Tier hint: T1-load-bearing (architectural claim about whether SHARES_MATH should be boolean or continuous)
- Why-now: this is THE cell the research drill exists to support. Gated on INV-3a HP-1 pass.
- Compute hint: ~1-2 hr CPU after INV-3a; sweep tau across ~2 decades at ~20 logarithmically-spaced points; partition via bisimulation closure OR modularity-max on weighted graph; ARI vs central-tau partition for each tau.

### Anchor 3 (optional, gated): CELL INV-3c — score-formulation comparison (Score #1 vs #2 vs #3)
- Substrate-product reading: if INV-3b returns PARTIAL, this cell compares which score formulation gives the widest plateau (which is the most stable representation).
- Tier hint: T2-refinement (only fires if INV-3b PARTIAL)
- Why-now: gated on INV-3b PARTIAL outcome.

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_DRILL_continuous_SHARES_MATH_threshold_robustness_skunkworks_INV3_support_2026-06-13.md
- Plateau methodology precedent (alpha plateau): MEMORY.md entry substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12
- KP P6 archetype context: MEMORY.md entry substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL_Cell_3_KP_P6_HARD_PASS_2026-06-13
- Don't-lock-in-frameworks rule (triggered this skunkworks): MEMORY.md entry feedback_always_reconsider_frameworks_dont_lock_in_prematurely_USER_LOCKED_2026-06-13
- Substrate SHARES_MATH boolean state: 332 edges over 61 atoms, 12 archetype classes via coalgebraic bisimulation (from skunkworks INV-3 prompt context)

## Contract

- Pre-reg per envelope-fail-bands (HP-1, HP-2, HP-3, HF-1, HF-2, HF-3 stated in research note section c).
- Smoke gate before ship.
- Ship via queue_add.sh.
- Post-ship REMOTE VERIFY per L4 standing duty.
- Self-test per formula-selftests.
- Pause-gated by data/orchestrator_paused.flag.

## Autonomy declaration

exp_dev decides: which score formulation to author first (research note ranks Score #1 cheapest); whether to use bisimulation closure or modularity-max for partition recovery; exact tau-grid spacing; whether to local-CPU smoke INV-3a before queue-shipping INV-3b. Research note states what to test (plateau width, ARI, Spearman) and what counts as PASS/FAIL; exp_dev decides HOW to implement.
