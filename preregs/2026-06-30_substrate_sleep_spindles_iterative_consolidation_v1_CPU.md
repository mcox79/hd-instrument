# Pre-registration: substrate_sleep_spindles_iterative_consolidation_v1_CPU

**Filed:** 2026-06-30
**Anchor:** substrate_sleep_spindles_iterative_consolidation_v1_CPU
**Script:** experiments/exp_substrate_sleep_spindles_iterative_consolidation_v1_CPU.py
**Queue:** remote_cpu_queue (iterative per-item dynamics; not GPU-amenable)
**Tier:** MEASURED_MECHANISM candidate (Stage 2 NREM Hc-rescue test)
**N_h / N_c:** 8192 / 2048
**M:** 2048 (alpha_simple=0.25; matches hippo_bottleneck v2)
**Seeds:** [7, 17, 23]
**Drill source / parent:** hippo_bottleneck v2 (commit c374d74f) Hc confirmed.

## Brain mechanism (CITED@brain_lit_NREM2_sleep_spindles)
NREM2 sleep spindles (~12-15Hz) are a SEPARATE consolidation event from
NREM3 ripples; spindles do slow iterative reactivation + gradient-style
cortical integration, NOT burst-transmit. Standard sleep architecture:
NREM2 (spindles) -> NREM3 (slow waves + ripples) -> back.

## Hypothesis (THEORETICAL)
One-shot Hebbian write writes the FULL outer product; cumulative interference.
Spindle (gradient-residual) write: pred=sign(W @ c); residual=v-pred; W +=
eta * residual outer c. Self-correcting: well-stored items get small updates;
poorly-stored get larger. Slower per-item but lower cumulative noise.

Combined ripple+spindle: ripple seeds the consolidation; spindle corrects.
Predicts RIPPLE_THEN_SPINDLE order best (biological match).

## Arms (5)

| Arm | Mechanism | Order |
|-----|-----------|-------|
| ARM_RIPPLE_ONLY | One-shot Hebbian (= STANDARD baseline) | ripples only |
| ARM_SPINDLE_ONLY | Gradient/residual write only | spindles only |
| ARM_RIPPLE_THEN_SPINDLE | Phase 1 ripples + Phase 2 spindles | brain order |
| ARM_SPINDLE_THEN_RIPPLE | Phase 1 spindles + Phase 2 ripples | reverse |
| ARM_INTERLEAVED | Per-item ripple + random spindle correction | interleaved |

## Pre-registered bands

Let R_X = mean(recall) across seeds.
Let R_RIPPLE = R[ARM_RIPPLE_ONLY] (baseline).
Let `best_lift = max(R[non-RIPPLE]) - R_RIPPLE`.

**HARD_PASS:** `best_lift >= 0.30`
**MIDDLE_BAND:** `best_lift in [0.05, 0.30)`
**HARD_FAIL:** `best_lift < 0.05` OR META_RULE_AF violation OR cardinality breach

## Discriminator-must-survive-scale (META_RULE_AG)

Smoke seed=7 at M=512 (alpha=0.25 SAME as full):
```
ARM_RIPPLE_ONLY          recall=0.604  baseline
ARM_SPINDLE_ONLY         recall=0.705  +0.10
ARM_RIPPLE_THEN_SPINDLE  recall=0.814  +0.21 (BEST; brain order)
ARM_SPINDLE_THEN_RIPPLE  recall=0.664  +0.06
ARM_INTERLEAVED          recall=0.686  +0.08
```
Mechanism FIRES with clear signal aligning with brain literature.
AF hashes all distinct. At full M=2048 the RIPPLE baseline is expected
to drop to ~0.22 (v2 STANDARD reference); spindle/ripple+spindle arms
expected to climb proportionally if mechanism is robust.

## Pre-reg schema fields
- cardinality_ok: true (5 arms * 3 seeds = 15)
- arms_differ_verified: true (smoke confirmed distinct)
- final_metrics_atomicity: "tmp_replace"
- crlb_n/a: "associative-memory capacity not CRLB"
- baseline_in_band: smoke RIPPLE=0.604 in band; full RIPPLE expected ~0.22
- discriminator_reachability: true (smoke shows monotonic ordering effect)
- calibration_check: "default_ok_for_this_regime"
- cell_chunked: false
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: "passed_all_4_patterns"

## Dispatch destination + timeout
- Queue: remote_cpu_queue (iterative per-item; CPU)
- timeout_s: 3600 (1 hour; iterative loop M=2048 per arm, 5 arms, 3 seeds
  ~ 2-5 min/seed at full * 3 seeds + margin)
- No PROT-018/019 floor

## Coordination
- Cell-author: exp_dev
- Landed-VET: skunkworks
- Push gate: hd_metrics_sync auto-push
