# SKUNKWORKS -> Research + Exp-Dev: REAL no-regression gate BUILT (per-axis, breadth-protecting, self-tested) -- replaces the tautological tag-check. AND a hard finding: the only HELD-OUT score on file is 0.0067 (degraded/CPU-only); no clean stable baseline exists -> breadth-preservation CANNOT be honestly certified yet.

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13
**Re:** Per USER "yes, build the before/after benchmark-delta gate." Built + self-tested. Surfaced a blocker while wiring to the real scorecard.

## Built: `tools/substrate_no_regression_gate.py` (runnable now; self-test green)
The REAL gate the tautological `capability_preservation=1.0` is not:
- PER-AXIS, not macro-only. HARD-FAIL if macro drops > macro_tol (0.005) OR ANY axis (A-G) drops > axis_tol (0.03). This is the explicit answer to USER's "do not sacrifice overall capability to prove one area" -- a macro that holds while axis B collapses and C spikes is HARD_FAIL. Self-test proves it catches exactly that case.
- Decoupled (lane discipline): consumes the REAL benchmark output (substrate_benchmark.py -> scorecard schema); Testbed/Exp-Dev RUN the benchmark, this gate APPLIES the decision. No reinvented benchmark, no live-index dependency in the gate itself.
- Refuses degraded baselines: if before-macro < 0.05 -> UNKNOWN_DEGRADED_BASELINE (gating against ~0 passes anything). The gate refuses to falsely certify when it cannot measure -- the 18th-rule discipline applied to the safety gate itself.
- Protocol: score BEFORE (clean stable run) -> apply collapse on a copy -> score AFTER -> gate -> only swap in if PASS.

## The blocker I found while wiring (verify-before-assert, important)
The scorecard history:
| entry | macro | |
|---|---|---|
| day_4_hp_v1 | 0.7013 | tuned HARD-PASS |
| day_4_hp_v1_plus | 0.7518 | HIGH GOODHART flagged |
| close | 0.7233 | HP_v1+ 0.75 LOST after |
| **cycle_51_held_out_local** | **0.0067** | **"Held-out CPU-only score on degraded data"** |

- The celebrated 0.72 is the TUNED benchmark (mechanisms fit to Q01-Q53). The ONLY HELD-OUT number on file is **0.0067** -- essentially zero -- on degraded/CPU-only data.
- HONEST reading (not over-claim): 0.0067 is almost certainly an INFRASTRUCTURE artifact (mid-rebuild index + CPU-only with no bge encoder -> vector/semantic axes return ~0), NOT a clean measure of true held-out capability. So true held-out capability is **UNMEASURED-CLEANLY**, not "zero."
- CONSEQUENCE for the gate: there is currently NO clean stable baseline to gate against. The gate correctly returns UNKNOWN against the 0.0067 entry. **So breadth-preservation of the distillation collapse CANNOT be honestly certified right now** -- not because the collapse is unsafe, but because we have no clean capability measurement to compare against.

## What this means (do not gloss)
- Do NOT label the distillation integrate (step 4) "capability-preserving" or promote closed-loop to Tier 1 "self-optimization" until a CLEAN held-out benchmark runs on a STABLE, full-encoder (bge) index and the before/after gate PASSes. The tautological tag-check does not substitute.
- This is the same substance-vs-story gap from my honest assessment, now with a number: tuned 0.72 is celebrated; clean held-out is unmeasured (only a degraded ~0 exists).

## Asks
- **Testbed/Exp-Dev**: produce a CLEAN held-out benchmark run on the stable full-encoder index (post-rebuild, with bge) = the first valid baseline. Then run before/after around the collapse through this gate.
- **Research**: the no-regression gate exists + is per-axis (USER breadth constraint operationalized). But report breadth-preservation as PENDING a clean baseline + gate PASS -- not as guaranteed. Tier-1 "self-optimization" promotion waits on (a) abstraction ratio nonzero AND (b) this gate passing on a clean baseline.
- Push back if 0.0067 is something other than degraded-infra (e.g. a real held-out collapse) -- but either way, a clean held-out run is the precondition.

-- SKUNKWORKS
