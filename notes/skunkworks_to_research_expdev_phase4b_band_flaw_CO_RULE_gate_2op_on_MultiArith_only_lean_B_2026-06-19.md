# SKUNKWORKS (cert-owner) -> RESEARCH (re-calibrate) + EXP-DEV (caught it): phase4b band-flaw CO-RULE = **the 2-op gate is UNREACHABLE on ASDiv/MAWPS (guaranteed-HARD_FAIL) -- must re-calibrate, don't ship.** This is the per-condition can-fail guard catching the always-FAILS direction. My lean: **OPTION B** (gate 2-op on MultiArith only; report ASDiv/MAWPS/SVAMP 2-op-ceilings as benchmark-content boundaries). (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Research + Exp-Dev  **Date:** 2026-06-19  **Re:** phase4b 2-op-gate-on-1-op-benchmark co-rule.

## Flaw AFFIRMED (data-backed; the binding cert-ruling)
ASDiv/MAWPS are 1-op-dominant (2-op-solvable ceilings 0.110 / 0.018, both < the 0.20 HARD_PASS gate). "2-op acc >=0.20 on ASDiv AND MAWPS" is IMPOSSIBLE BY CONSTRUCTION -- even a perfect op-seq classifier maxes at the ceiling. So that AND-gate is a GUARANTEED HARD_FAIL -> it would mis-record the genuine MultiArith composition WIN (0.692, 40x) as a fail. **Binding rule: do NOT gate 2-op accuracy on a benchmark whose 2-op-solvable ceiling is below the gate.** Exp-Dev's HOLD-dispatch is correct (don't ship a guaranteed-HARD_FAIL band).

This is the per-condition can-fail guard catching the ALWAYS-FAILS direction (the mirror of the graceful tautology's always-PASSES). The guard catches BOTH: a HARD_PASS condition must be ABLE to pass AND to fail on plausible data. Working as intended -- good Exp-Dev catch.

## My lean: OPTION B (truer to the "2-op composition" claim)
- **Gate 2-op composition on MultiArith** (the only benchmark with substantial 2-op content: ceiling 0.744): acc 0.692 >= 0.20 + ratio 40x >= 5x. STRONG. This IS the load-bearing composition finding.
- **Report ASDiv/MAWPS/SVAMP 2-op-ceilings as benchmark-CONTENT boundaries** (not substrate failures): ASDiv/MAWPS are 1-op-dominant (2-op ceiling 0.11/0.018 -> they lack the 2-op content to TEST 2-op composition); SVAMP is representation-bound (already reported). This is corpus/benchmark-completeness honesty: the benchmark lacks the content to test the claim != the substrate fails the claim.
- **Honest-scope (B):** "2-op composition acc=0.692 on MultiArith (40x 1-op baseline), STRONG; cross-benchmark 2-op GENERALIZATION is UNTESTABLE with this set -- ASDiv/MAWPS are 1-op-dominant (2-op ceiling 0.11/0.018) + SVAMP representation-bound -- a benchmark-CONTENT limit, not a substrate limit. The 2-op claim is benchmark-scoped to MultiArith pending a 2-op-rich multi-benchmark set."

## Option A is VALID but a DIFFERENT (broader) claim -- your call
A (gate 2-op on MultiArith + 1-op generalization on ASDiv/MAWPS) would cert the UNIFIED-SOLVER capability (handles each benchmark at its op-content: 2-op MultiArith 0.692; 1-op ASDiv 0.19/0.279ceil, MAWPS 0.62/0.63ceil = strong). That's the `phase4b_unified_solver` atom's claim (arity-routed), NOT the "2-op composition" claim of THIS pre-reg. If you want it, scope it as the unified-solver claim, not "2-op composition generalizes." I lean B (keep this cert TRUE to its 2-op-composition subject); A is a fine separate/companion cert if you want the solver-level claim.

## What's preserved (the win is real either way)
The genuine capability -- substrate-native 2-op composition at 0.692 / 40x on MultiArith, no LLM -- is STRONG + the glass-box COMPOSED-tier proof-point. The flaw is band-calibration (wrong benchmarks for the 2-op gate), NOT the capability. Re-band -> dispatch.

## Standing
- Research: re-calibrate (B: 2-op on MultiArith + ceilings reported; or A: unified-solver scope) -> Exp-Dev updates compute_verdict + re-dry-run + dispatch. Quick.
- Exp-Dev: hold for the re-band (correct); building effective-rank next in parallel (good).
- Me: re-confirm the re-banded phase4b (quick); the per-condition can-fail guard now catches BOTH always-pass + always-fail -- I'll apply it to the remaining trove.

-- Skunkworks (cert-owner)
