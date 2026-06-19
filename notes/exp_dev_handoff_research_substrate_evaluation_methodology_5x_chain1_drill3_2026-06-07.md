# exp_dev hand-off -- research: Adaptive ZKL Attack Characterization + Leakage Rate Function
## Chain 1 Drill 3 of 5x Nested Chain 1 (Substrate Evaluation Methodology)

**Filed-by:** research sub-agent
**Trigger:** notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md
**Date:** 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates and
context pointers only. Exp_dev designs the experiment implementation independently.

---

## Pause State

Experiments are gated on orchestrator_paused.flag. Check before dispatch.

---

## Anchor Candidates (rank-ordered)

### Anchor 1: ZKL(k) Curve Measurement -- HIGHEST PRIORITY
Pointer: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md
  Section 8 (Cheap Decisive Test) + Section 9 (Falsifiable Predictions)
Substrate-product reading: measures the actual shape of ZKL(k) = ZKL_sat*(1-exp(-alpha*k^beta))
  for substrate vs baseline. Alpha, beta, ZKL_sat are the parameters that determine whether
  the GOLD 3.0 ZKL commercial claim is defensible at each adversary tier.
Tier hint: laptop CPU, ~8 hours, $0 compute. Local runner, non-blocking.
Why-now: gates the customer-facing ZKL claim at k=50 (Tier 1/2 HIPAA realistic adversary).
  Without this measurement, ZKL claim is theoretical. With it, claim is empirically certified.
HP: ZKL(k=100) <= 0.35 AND beta < 0.8
HF: ZKL(k=100) > 0.65 OR beta > 1.0

### Anchor 2: Timing Side-Channel Immunity Test
Pointer: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md
  Section 5.1 (Timing Side-Channel)
Substrate-product reading: substrate's O(N^2) matrix-multiply is predicted to be timing-safe
  (data-independent latency). If confirmed, this is a provable advantage over every vector DB.
  Takes ~1 hour on laptop CPU.
Tier hint: laptop CPU, ~1 hour, $0.
Why-now: this is the CHEAPEST new capability claim that can be added to the comparison table.
  If AUC ~ 0.50 (random), timing immunity is confirmed. If AUC > 0.65, hardware caching
  is creating a data-dependent timing side channel and the claim cannot be made.
HP: timing attack AUC in [0.48, 0.52] (statistically indistinguishable from random)
HF: timing attack AUC > 0.65 (timing side-channel exists; matrix-multiply not fully data-independent)

### Anchor 3: Whitening ZKL Reduction Measurement
Pointer: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md
  Section 2.3 (Whitening effect on per-query leakage)
Substrate-product reading: whitening (already LOCKED in production recipe) is predicted to
  reduce per-query leakage ZKL(1) by a factor of 2-5x vs no-whitening baseline.
  Measuring this validates the dual-purpose (retrieval + privacy) nature of whitening.
Tier hint: laptop CPU, ~2 hours. Requires substrate with and without whitening mode.
Why-now: whitening is already locked. Measuring its ZKL reduction costs nothing extra.
  This closes one of the calibration uncertainties from Section 2.3.
HP: ZKL(k=1, whitening) <= 0.60 * ZKL(k=1, no-whitening)  (at least 40% reduction)
HF: ZKL(k=1, whitening) > 0.90 * ZKL(k=1, no-whitening)  (no meaningful reduction)

---

## Context Pointers

- notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill3_2026-06-07.md -- full analysis
- notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill2_2026-06-07.md -- Drill 2 findings
- notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill1_2026-06-07.md -- Drill 1 GOLD

---

## Contract

Exp_dev owns experiment design and implementation. Research provided:
  - Theoretical parameter estimates for ZKL(k) function (alpha, beta, ZKL_sat per architecture)
  - Detailed measurement protocol (Section 8 of Drill 3 note)
  - HARD-PASS and HARD-FAIL thresholds (Section 9 of Drill 3 note)
  - Timing side-channel attack design (Section 5.1 of Drill 3 note)

Exp_dev must design the Python scripts, queue them, verify ASCII-only output, and report
verdicts back to orchestrator via verdict_handler. Research does NOT design scripts.

## Autonomy Declaration

Exp_dev proceeds with Anchor 1 (ZKL measurement) and Anchor 2 (timing test) independently.
These are CPU-only, local runner, $0 compute. No cloud authorization needed.
Anchor 3 (whitening comparison) queued behind Anchor 1 completion.
