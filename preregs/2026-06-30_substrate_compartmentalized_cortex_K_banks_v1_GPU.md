# Pre-registration: substrate_compartmentalized_cortex_K_banks_v1_GPU

**Filed:** 2026-06-30
**Anchor:** substrate_compartmentalized_cortex_K_banks_v1_GPU
**Script:** experiments/exp_substrate_compartmentalized_cortex_K_banks_v1_GPU.py
**Queue:** overnight_queue (GPU; torch matmul on N_h x N_h = 8192^2 dominant)
**Tier:** MEASURED_MECHANISM candidate (Stage 2 NREM Hc-rescue test)
**N_h / N_c:** 8192 / 2048
**M:** 2048 (alpha_simple=0.25; matches hippo_bottleneck v2 reference regime)
**Seeds:** [7, 17, 23] (3-seed FULL)
**Drill source / parent:** hippo_bottleneck v2 (commit c374d74f) confirmed
Ha (Hebbian cross-term) + Hc (cortex write saturation) as Stage 2 H_OTHER
mechanisms. This cell tests COMPARTMENTALIZED CORTEX as a brain-inspired
rescue for Hc.

## Brain mechanism (CITED@brain_lit_modular_cortex)
Cortex is modular: visual, motor, language, parietal regions consolidate
independently from different hippocampal subfields. One undifferentiated
dense cortex saturates; compartments do not. Models cortex as K disjoint
W_c banks, each receiving its own subset of hippo writes.

## Hypothesis (THEORETICAL)
Single W_c (N_c, N_c) writes M outer products into one matrix; saturation
~ M / capacity(N_c). K-bank rescue: each item routes to bank b = i % K;
per-bank load M/K. Hopfield capacity per bank proportional to N_c, so
per-bank saturation drops by factor 1/K.

At v2 baseline (M=2048, N_c=2048), STANDARD measured R=0.219 (write-saturated).
K=10 banks -> per-bank load 205 (alpha_per_bank=0.025; well sub-capacity);
expect recall to climb toward DIRECT ceiling 0.985.

## Arms (5; META_RULE_AF arms-must-differ via distinct W_cortex hashes)

| Arm | K_banks | Per-bank load (full) | Mechanism tested |
|-----|---------|----------------------|------------------|
| ARM_STANDARD_K1 | 1 | 2048 | Baseline (v2 STANDARD path) |
| ARM_COMPARTMENT_K2 | 2 | 1024 | Coarse compartmentation |
| ARM_COMPARTMENT_K5 | 5 | 410 | Mid compartmentation |
| ARM_COMPARTMENT_K10 | 10 | 205 | Brain-realistic K |
| ARM_COMPARTMENT_K20 | 20 | 102 | High compartmentation |

Routing: deterministic by item index (i % K_banks); balanced + reproducible.

## Pre-registered bands

Let R_X = mean(recall) across 3 seeds.
Let R_STANDARD = R[ARM_STANDARD_K1].
Let `best_lift = max(R[ARM_COMPARTMENT_K{2..20}]) - R_STANDARD`.

**HARD_PASS:** `best_lift >= 0.50` (substantial closure of v2 measured gap=0.766;
50% closure tested as meaningful rescue).
**MIDDLE_BAND:** `best_lift in [0.10, 0.50)` (partial rescue; mechanism contributes
but doesn't fully close).
**HARD_FAIL:**
- `best_lift < 0.10` (compartmentalization does not rescue Hc)
- META_RULE_AF violation (distinct K_banks yield bit-identical W_cortex hash)
- Cardinality breach (n_arms != 5 or n_seeds != 3)
- Any arm error

## Discriminator-must-survive-scale (META_RULE_AG)

Smoke at M=512, N_h=2048, N_c=512 (alpha_simple=0.25 SAME as full).

**Smoke result (2026-06-30 18:00 UTC, seed=7 cpu):**
```
ARM_STANDARD_K1     recall=0.604  (smoke under-states v2 STANDARD=0.219 at full)
ARM_COMPARTMENT_K2  recall=0.658  (lift +0.054)
ARM_COMPARTMENT_K5  recall=0.721  (lift +0.117)
ARM_COMPARTMENT_K10 recall=0.787  (lift +0.183)
ARM_COMPARTMENT_K20 recall=0.826  (lift +0.222)
```
MONOTONIC LIFT confirmed at smoke; mechanism FIRES. AF hashes all distinct.
Expected at full: STANDARD ~0.22; COMPARTMENT_K20 substantially higher
(write-saturation is the bottleneck and partitioning lifts it).

## CRLB / capacity feasibility (META_RULE_AC + Principle S)

K=20 banks at N_c=2048: per-bank alpha = M/(K*N_c) = 2048/(20*2048) = 0.05.
Hopfield single-bank capacity ~ 0.14 * N_c (Amit_Gutfreund_Sompolinsky).
At alpha=0.05 well below capacity; recall ceiling ~0.99.
At K=1: per-bank alpha = 1.0; far over-capacity; recall floor ~0.20.
crlb_n/a: "associative-memory capacity not Cramer-Rao; argmax-noise floor
analysis sufficient and captured by per-bank-alpha"

## Pre-reg schema fields (load-bearing)
- cardinality_ok: true (5 arms x 3 seeds = 15 units; verdict checks)
- arms_differ_verified: true (META_RULE_AF runtime check; smoke verified)
- final_metrics_atomicity: "tmp_replace" (single-shot smoke pattern)
- crlb_n/a: "associative-memory capacity not CRLB; per-bank alpha 0.05 sub-cap"
- baseline_in_band: smoke shows STANDARD=0.604 in (0.05, 0.95); full expected 0.22 in band
- discriminator_reachability: true (smoke monotonic lift confirmed)
- calibration_check: "default_ok_for_this_regime" (matches v2 reference)
- cell_chunked: false (single-cell multi-seed loop via _seed_checkpoint)
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: "passed_all_4_patterns"
- sweep_alignment_verdict: ALIGNED (K_banks parameter directly controls per-bank load)
- discriminating_fraction: 1.0 (4/4 sweep points predicted in discriminating band)

## Dispatch destination + timeout

- Queue: overnight_queue (GPU; matmul N_h=8192 dominant)
- timeout_s: 1800 (30 min; ~5s/arm/seed at full * 15 + GPU init + 6x margin)
- No PROT-018 _n suffix; no PROT-019 floor
- Pre-flight: --self-test passes; smoke passes mechanism-fires gate

## Coordination

- Cell-author: exp_dev (this dispatch)
- Landed-VET: skunkworks (audit-only)
- Push gate: hd_metrics_sync (cell+prereg committed to local main; remote
  runner picks up by name).
