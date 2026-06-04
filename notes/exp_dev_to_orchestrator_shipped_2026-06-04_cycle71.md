# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 71

## Llama v6: RUNNING (no action)
doc 66000/100000, 0 failures, wall ~9400s (~66%). npz in ~1.4h. No npz yet -> audit-core-on-real-residuals pending.

## Remote queues
- GPU pending=5 + Llama running. CPU pending=0 (DRAINED -- all 7 CPU experiments finished: mini_lm, audit-core,
  alpha-ramp, eviction, k3-falsifier, training-speed-stageA, crossover-sweep). No clean non-bio backlog ready to
  feed remote CPU (B36/B26/pure-bio are laptop-local per user; B8 awaits build; cross-domain-anchor3 deferred;
  bundle_f complex). NO-PADDING -> not shipping marginal work to fill it. Verdicts are Orchestrator's to read.

## Research responded to my round-2 note (all 3 requests answered)
- B5: ACCEPT THE NEGATIVE (linear-additive-W -> replay-order algebraically irrelevant = FUNDAMENTAL FINDING,
  not eng failure). Do NOT build bounded-weights. Future: B5-sparse-replay (does B2 k-WTA nonlinearity enable
  replay?) awaits minimal-nonlinearity drill.
- B8: Cell 4 (logit-space sparse residual) recommended first (r~0.27, ~14x M_crit, no embedding training).
- B3: RECOGNIZE BOTH a+b as validated primitives (B3a write-reduction; B3b = capacity-mgmt/anti-crosstalk,
  116% perf explained as keeping alpha sub-critical). top-2% optional stretch.
- Research now counts 4 validated bio HP anchors (B2 + B4 + B6 + 5-corpus aggregator) + B3 near-HP. "bio-architecture-first program is working."

## Built + ran this cycle (laptop)
- B36 composition (B3b gating x B6 D-ECR eviction, 3 loads low/near/over alpha_c). Research predicted
  SUPERADDITIVE at near-capacity. SMOKE REFUTES IT: gating dominates (gain +0.58..+0.72), eviction adds ~0
  (and HURTS at over-load: both=0.67 vs gate-alone=0.86). Mechanism: gating writes each distinct pattern ~once
  -> already bounds capacity -> eviction redundant (low/near) or harmful (over, drops wanted patterns). HONEST
  finding: B3b + B6 are capacity-mgmt for DIFFERENT stream types (redundant vs novel), NOT complementary on one
  task. Full N=2048 confirming (in flight). -> report to Research as a prediction-refuting composition result.

## Next builds (Priority 1 per Research; laptop)
- B26 composition (B2 sparse + B6 eviction; same capacity axis -> predicted ADDITIVE control).
- Pure-bio-combined (B2 + B3b + B4 + B6 unified; FLAGSHIP composition).
- B8 Cell 4 (logit-space sparse residual).
- (B5-sparse-replay awaits minimal-nonlinearity drill; B7 phase-binding later.)

**END.** All laptop scripts use write_metrics. Cleaned up a duplicate-laptop-python slip (6 B4 procs) earlier.
