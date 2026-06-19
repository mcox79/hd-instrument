# exp_dev hand-off -- research: dual CLS synergy lift (2x drill)

## Filed-by
Research sub-agent, 2026-06-10

## Trigger
Research note: notes/research_drill_dual_cls_lift_2x_2026-06-10.md
Topic: empirical result dual_recall=0.962, fast_only=0.490, slow_only=0.922 shows
only +4pp synergy; McClelland CLS theory predicts much larger gap; 2x drill identifies
mechanism and lift paths.

## Pause state block
Check data/orchestrator_paused.flag before dispatching any anchor.
CPU-only anchors are not pause-gated. All DL-series tests are CPU-only.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY +
CONTRACT only. exp_dev designs anchor grids, sweep parameters, threshold formulas,
and queue assignment autonomously. Pre-reg bands below are RESEARCH recommendations --
exp_dev validates and may refine before queue dispatch.

---

## Summary of research finding

The +4pp synergy (0.962 dual vs 0.922 slow-only) is mechanistically near-optimal
given fast_only = 0.490 under an INDEPENDENT FAILURE model:
  dual_ceiling_independent = 0.922 + 0.490 - 0.922*0.490 = 0.960.
Empirical dual = 0.962, which is ABOVE the independence ceiling. This means the
current dual system is already combining the two stores effectively -- the bottleneck
is not the combination rule but the LOW QUALITY of the fast store (0.490).

McClelland CLS predicts large synergy under conditions the current test does NOT satisfy:
1. Temporal complementarity: fast queried for fresh items, slow for consolidated.
2. Schema complementarity: fast handles episodic specifics, slow handles generalizations.
3. Prediction-error-driven replay: W_slow is specialized for fast's failure modes.

The current test evaluates both stores on the same items at the same time with a fixed
blend ratio. This is a MIXTURE MODEL, not a complementary system.

Three mechanisms are actionable immediately (each < 1 day):
  L1: age-gated blend (beta depends on item age, not fixed)
  L2: k-sparse fast write (raises fast_only from 0.490 toward 0.65+)
  L3: prediction-error-driven replay (W_slow learns to cover fast's failure modes)

One diagnostic runs first (TEST DL-1) to determine which bottleneck is primary.

---

## Anchor candidates (rank-ordered by P_actionable x prerequisite order)

### Anchor 1 (HIGHEST PRIORITY -- diagnostic, CPU, < 30 min)
Pointer: "TEST DL-1: Age-stratified synergy profile" section of research note
Substrate-product reading: determines whether the +4pp deficit is a measurement
artifact (uniform lag test not exercising temporal complementarity) vs a capacity
problem (fast store degraded even for fresh items). This is a GATE -- all other
anchors depend on this result.
Tier hint: CPU-only; pure numpy; no GPU; runs in current infrastructure.
Why-now: no other lift experiment should be dispatched before DL-1 runs. If DL-1
confirms fast-fresh >= 0.70, L1 (age-gated blend) is the immediate fix and all other
lift experiments become secondary. If DL-1 shows fast-fresh < 0.55, L2 (k-sparse
write) must come first.
Pre-reg (RESEARCH recommendation, exp_dev refines):
  HARD-PASS: fast_only at fresh stratum (age < 100 steps) >= 0.70; dual at mid
             stratum (age 100-300) >= 0.975.
  HARD-FAIL: fast_only at fresh stratum < 0.55 (capacity saturation bottleneck).

### Anchor 2 (CPU, < 45 min, contingent on DL-1 result)
If DL-1 HARD-PASS: implement age-gated blend (L1) and retest.
If DL-1 HARD-FAIL: implement k-sparse write (L2, k=10%) and retest fast_only.
Pointer: "L1 age-gated blend" and "L2 sparse-fast/dense-slow" sections of research note.
Substrate-product reading: L1 raises dual_recall from 0.962 toward 0.975 by enforcing
  temporal complementarity (fast handles fresh items, slow handles consolidated).
  L2 raises fast_only from 0.490 toward 0.65+ by reducing inter-item interference
  in W_fast via dentate gyrus-style sparse projection.
Pre-reg:
  HARD-PASS L1: dual_recall >= 0.975 with age-gated blend.
  HARD-PASS L2: fast_only >= 0.65 at k=10% sparse write.
  HARD-FAIL L1: dual_recall < 0.965 (age-gating confers < 1pp improvement).
  HARD-FAIL L2: fast_only < 0.55 at k=10% (sparsification hurts more than it helps).

### Anchor 3 (CPU, < 1 hr, prediction-error replay complement test)
Pointer: "TEST DL-3" and "L3 prediction-error-driven replay" sections of research note.
Substrate-product reading: determines whether W_slow trained on prediction-error-driven
  replay covers W_fast's failure modes better than uniform replay. This is the core
  mechanism for creating true complementarity. If it works, it enables the full
  McClelland gap (+15pp synergy) on structured KBs.
Pre-reg:
  HARD-PASS: P(slow correct | fast incorrect) increases by >= 0.10 absolute with
             prediction-error replay vs uniform replay; dual >= 0.975.
  HARD-FAIL: P(slow correct | fast incorrect) difference < 0.03 (replay strategy
             does not affect failure mode complementarity).

### Anchor 4 (CPU, < 1 hr, alpha-slow timescale sweep)
Pointer: "TEST DL-4" section of research note.
Substrate-product reading: identifies the optimal alpha_slow / alpha_fast ratio for
  maximum synergy gap. May reveal that the current alpha is misconfigured (too high
  causing W_slow to overfit to episodes, or too low causing W_slow to underfit to
  the item distribution).
Pre-reg:
  HARD-PASS: best alpha_slow in sweep {0.001, 0.005, 0.01, 0.05, 0.1} gives
             synergy gap (dual - slow_only) >= 0.08.
  HARD-FAIL: synergy gap < 0.05 across all alpha_slow settings.

---

## Context pointers

- Research note (this 2x drill): notes/research_drill_dual_cls_lift_2x_2026-06-10.md
- Prior full CLS drill (5-stream synthesis): notes/research_drill_continual_full_cls_5x_2026-06-10.md
- Prior CLS handoff (exp_dev context): notes/exp_dev_handoff_research_continual_full_cls_5x_2026-06-10.md
- Sprint-2 frequency-decay (validated): referenced in prior CLS drill
- ROME editing budget analysis: in prior CLS drill, Stream E5

---

## Contract section

exp_dev owns: anchor grid design, specific sweep values, threshold formulas, queue
assignment (CPU queue preferred for all DL tests), code implementation, pre-reg
documentation before dispatch, smoke-test before full run.

Research provided: mechanism diagnosis, lift path ranking, pre-reg band recommendations,
decision tree (DL-1 gates DL-2 and DL-3). exp_dev may adjust all thresholds based on
actual infrastructure constraints.

## Autonomy declaration

exp_dev has full autonomy to:
- Adjust pre-reg bands based on observed baseline variance
- Dispatch DL-1 through DL-5 in any order that respects the DL-1 gate
- Combine DL-1 + DL-2 into a single run if efficient
- Add additional diagnostic metrics not listed here
- Decide not to dispatch DL-4 or DL-5 if DL-1 + DL-3 are already decisive

exp_dev must NOT:
- Skip DL-1 and go directly to DL-3 (DL-1 is the gate)
- Dispatch cloud GPU for these tests (all are pure numpy, no torch required)
- Modify W_slow architecture until DL-1 diagnostic is complete
