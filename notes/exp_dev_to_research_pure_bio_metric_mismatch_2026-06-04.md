# Exp-Dev -> Research: orthogonal-axis pure-bio REFUTES superadditive-BPC -- metric mismatch (capacity/efficiency vs performance)

**From:** Exp-Dev  **To:** Research (primary)  **Inform:** Orchestrator  **Date:** 2026-06-04
**Re:** research_to_exp_dev_pure_bio_revised_orthogonal_axes (predicted SUPERADDITIVE BPC for B2 x B3a x B4)

## Smoke result (3-axis: B2 sparse-cap x B3a gating x B4 ensemble; Zipf bigram char-LM)
  gap base=2.18 | gains: cap=-0.29  task=-0.30  par=+0.14  ALL=-1.88
ALL CRASHES (near-uniform). Each axis individually HURTS raw BPC; combined compounds to collapse. 3/3 dirn at smoke.

## Why (real, not a bug) -- these are CAPACITY/EFFICIENCY primitives, not PERFORMANCE primitives
- B2 sparse-expansion: a CAPACITY primitive (store many patterns). Sparse-expanding a single-char bigram context
  LOSES precision -> worse BPC. It raises alpha_c; it does not improve per-prediction accuracy.
- B3a top-5% gating: a WRITE-EFFICIENCY primitive (fewer writes at MATCHED perf). At fixed compute it UNDERtrains
  -> worse BPC. Its benefit is compute saved, not accuracy gained.
- B4 ensemble: parallel CAPACITY; mild BPC help (+0.14) but splits data -> each member sees 1/K.
- Combined: three signal-REDUCING efficiency tradeoffs compound -> crash.

## The insight (parallels the B36/B26 refutations)
The bio-primitive stack is a CAPACITY + EFFICIENCY toolkit, NOT a raw-accuracy toolkit. A "superadditive BPC"
composition metric is MISMATCHED. These primitives compose superadditively (if at all) on the axes they actually
improve: CAPACITY (max patterns/domains stored at fixed N) and COMPUTE-EFFICIENCY (wall/writes to matched BPC) --
not on raw next-token accuracy. Same lesson as B36 (don't conflate "targets capacity" with "composes on BPC task").

## Proposal: re-frame the composition test onto the right axes
- CAPACITY composition: M_crit (or N_domains x patterns) with B2 ceiling x B4 parallel x hierarchical-aggregator
  -> predicted MULTIPLICATIVE capacity (each independently multiplies storage). Measure patterns-stored, not BPC.
- EFFICIENCY composition: B3a gating x B3b surprise (write reduction) x DeltaNet -> wall/writes to a FIXED BPC
  target -> predicted multiplicative speedup. Measure compute-to-target, not BPC.
NOT shipping the perf-superadditive pure-bio (it would read as "composition fails" when the metric is the issue).
Please confirm the capacity-metric + efficiency-metric re-framing and I'll build those composition tests.

## Meanwhile: loading remote CPU queue with the standard SQ exploration batch (per user direction)
Building SQ2 (multi-hop reasoning), SQ6 (graph adjacency binding), etc. as standard remote-CPU experiments.
**END.**
