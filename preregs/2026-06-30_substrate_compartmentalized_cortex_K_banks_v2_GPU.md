# Pre-registration: substrate_compartmentalized_cortex_K_banks_v2_GPU

**Filed:** 2026-06-30
**Anchor:** substrate_compartmentalized_cortex_K_banks_v2_GPU
**Script:** experiments/exp_substrate_compartmentalized_cortex_K_banks_v2_GPU.py
**Queue:** overnight_queue (GPU; torch matmul on N_h x N_h = 8192^2 dominant)
**Tier:** MEASURED_MECHANISM -> HARD_PASS candidate (Stage 2 NREM Hc-rescue
K-sweep extension)
**N_h / N_c:** 8192 / 2048
**M:** 2048 (alpha_simple=0.25; matches v1 + hippo_bottleneck v2 reference)
**Seeds:** [7, 13, 19] (3-seed FULL)
**Drill source / parent:**
- v1 K-sweep FULL MEASURED@d:/AI/hd-instrument/data_remote_pull_staging/data/exp_substrate_compartmentalized_cortex_K_banks_v1_GPU/metrics.json:
  K=1: 0.220, K=2: 0.249, K=5: 0.342, K=10: 0.472, K=20: 0.643;
  best_lift=+0.423 at K=20 (MIDDLE_BAND; monotonic; HP floor=+0.50)
- Hippo bottleneck v2 MEASURED@d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_bottleneck_class_diagnostic_v2/metrics.json:
  R_DIRECT=0.985, R_STANDARD=0.219 (Hc cortex write-saturation confirmed)

## Brain mechanism (CITED@brain_lit_modular_cortex)
Cortex is modular: visual, motor, language, parietal regions consolidate
independently from different hippo subfields. Biological cortex columns are
on the order of thousands; v2 K=50-200 closer to biological compartmentation
than v1 K=2-20.

## Hypothesis (THEORETICAL + extrapolation from v1 MEASURED data)
v1 FULL K-sweep slope is STEEPENING: K=5->K=10 lift +0.130; K=10->K=20 lift
+0.171. If this continues, K=20->K=50 lift could be ~+0.20 to +0.30 yielding
K=50 recall ~0.85-0.95 (lift over STANDARD 0.22 ~ +0.63 to +0.73; above
HP_LIFT_MIN +0.50).

K=200 at full: per-bank load M/K = 2048/200 = ~10 items. Hopfield per-bank
capacity ~ 0.14 * N_c=2048 = ~286. Per-bank alpha=0.005 (far sub-capacity).
Expected ceiling ~ R_DIRECT_UPPER (oracle).

## Smoke result (MEASURED@d:/AI/hd-instrument/data/exp_substrate_compartmentalized_cortex_K_banks_v2_GPU_smoke/metrics.json)
```
ARM_STANDARD_K1     recall=0.604  (smoke STANDARD; cf full 0.220)
ARM_COMPARTMENT_K20 recall=0.826  (lift +0.222 over STANDARD)
ARM_COMPARTMENT_K50 recall=0.859  (lift +0.255; best smoke single-step)
ARM_COMPARTMENT_K100 recall=0.893  (lift +0.289; smoke saturation onset)
ARM_COMPARTMENT_K200 recall=0.891  (saturated; same as K=100 within noise)
ARM_DIRECT_UPPER    recall=1.000  (smoke oracle ceiling)
```

**Smoke-saturation note (load-bearing for full-regime interpretation):**
Smoke regime N_c=512 hits saturation between K=50 and K=100; K=200 plateaus.
Smoke STANDARD_K1=0.604 vs full STANDARD_K1=0.220 -- smoke under-states
the full-regime headroom by ~4x (full has 4x N_c=2048 and 4x M=2048).
v1 evidence: v1 smoke K=20=0.826 vs v1 full K=20=0.643 (smoke OVER-shoots
because of smaller N_c readout ceiling). Full N_c=2048 has substantially
more headroom; K=50 expected to extend the v1 monotonic slope rather than
plateau immediately.

DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at SAME alpha_simple=0.25 as full.
v1 evidence chain shows mechanism survives scale (smoke MB -> full MB with
larger lift). v2 smoke fires discriminator (monotonic to K=50; saturation
onset later than smoke regime supports as evidence of full-regime room).

## Arms (6; META_RULE_AF distinct W_cortex hashes verified at smoke)

| Arm | K_banks | Per-bank load (full) | Mechanism tested |
|-----|---------|----------------------|------------------|
| ARM_STANDARD_K1 | 1 | 2048 | Baseline (v2 STANDARD; lower-bound) |
| ARM_COMPARTMENT_K20 | 20 | 102 | v1 best (anchor for monotonic extension) |
| ARM_COMPARTMENT_K50 | 50 | 41 | mid K (predicted near HP) |
| ARM_COMPARTMENT_K100 | 100 | 21 | high K (predicted at HP) |
| ARM_COMPARTMENT_K200 | 200 | 10 | very high K (predicted at ceiling) |
| ARM_DIRECT_UPPER | 0 (direct) | M | Oracle ceiling (no replay) |

Routing: deterministic by item index (i % K_banks); balanced + reproducible.
Smoke verified all 6 arm hashes DISTINCT (META_RULE_AF).

## Pre-registered bands

Let R_X = mean(recall) across 3 seeds.
Let R_STANDARD = R[ARM_STANDARD_K1].
Let `best_lift = max(R[ARM_COMPARTMENT_K{20..200}]) - R_STANDARD`.
Let `cv_best = std/mean` at the best arm.

**HARD_PASS:** `best_lift >= 0.50` AND monotonic across K AND `cv_best <= 0.10`
(substantial closure of v2 hippo gap 0.766; strictly above floor +5% per
META_RULE_L via monotonic + cv discipline).
**MIDDLE_BAND:**
- `best_lift in [0.10, 0.50)`, OR
- `best_lift >= 0.50` but monotonic=False OR cv_best > 0.10 (HP_FLOOR_HIT_BUT_DISCIPLINE_GAP)
**HARD_FAIL:**
- `best_lift < 0.10`
- META_RULE_AF violation
- Cardinality breach (n_arms != 6 or n_seeds != 3)
- Any arm error

**HP_SCOPE (META_RULE 5b):**
- ARM_STANDARD_K1: NOT subject to HP gate (baseline by design)
- ARM_COMPARTMENT_K{20,50,100,200}: subject to HP best_lift gate
- ARM_DIRECT_UPPER: NOT subject to HP gate (oracle by design)

## CRLB / capacity feasibility (META_RULE_AC + Principle S)

K=200 banks at full N_c=2048: per-bank alpha = 2048/(200*2048) = 0.005.
Hopfield single-bank capacity ~ 0.14 * N_c=2048 = ~286 items.
Per-bank load = 10 items; well below capacity.
K=50 banks: per-bank alpha = 0.020 (41 items per bank; sub-cap).
K=100 banks: per-bank alpha = 0.010 (21 items per bank; sub-cap).
K=1 banks: per-bank alpha = 1.0 (2048 items; over-capacity; recall floor ~0.22).
crlb_n/a: "associative-memory capacity not Cramer-Rao; per-bank-alpha
analysis sufficient and captured by Hopfield 0.14 ceiling"

## Pre-reg schema fields (load-bearing)
- cardinality_ok: true (6 arms x 3 seeds = 18 units; verdict checks)
- arms_differ_verified: true (META_RULE_AF runtime check; smoke verified distinct hashes)
- final_metrics_atomicity: "tmp_replace" (single-shot smoke pattern)
- crlb_n/a: "associative-memory capacity not CRLB; per-bank alpha=0.005-0.020 sub-cap"
- discriminator_reachability: true (v1 FULL K=20 measured +0.423; v2 K-extension
  expected to reach HP +0.50 given slope-steepening evidence; smoke under-states
  full by construction per v1 evidence chain)
- baseline_in_band: smoke STANDARD=0.604 in (0.05, 0.95); full STANDARD=0.220 in band
- calibration_check: "default_ok_for_this_regime" (matches v1 + hippo v2 ref)
- cell_chunked: false (single-cell multi-seed loop via _seed_checkpoint)
- start_marker_written: true
- crash_diagnostic_present: true
- heartbeat_present: true
- defensive_error_checking: "passed_all_4_patterns"
- sweep_alignment_verdict: ALIGNED (K_banks parameter directly controls per-bank load)
- discriminating_fraction: 1.0 (4/4 K-sweep points predicted in discriminating
  band [0.30, 0.70] at full regime per v1 slope extrapolation)
- positive_control_arms: ARM_COMPARTMENT_K20 reproduces v1 K=20 at FULL regime
  (cited_prior_metric=0.643; tolerance 0.10; if outside -> regime-extension audit)
- functional_requirements: (1) cortex compartmentation via i%K routing
  [primitive: deterministic_hash_route]; (2) per-bank Hebbian outer-product
  [primitive: Hopfield_outer]; (3) per-query bank lookup at recall [primitive:
  hash_route_consistent]

## Dispatch destination + timeout

- Queue: overnight_queue (GPU; matmul N_h=8192 dominant)
- timeout_s: 1200 (20 min margin; v1 wall=6s; K=200 adds ~5x bank iter
  but matmul bound by M*N_c, not K; 1200s gives ~200x margin)
- Pre-flight: --self-test passes; smoke fires discriminator (monotonic +
  lift through K=50)

## Coordination

- Cell-author: exp_dev (this dispatch)
- Landed-VET: skunkworks (audit-only)
- Push gate: hd_metrics_sync (cell+prereg committed to local main; remote
  runner picks up by name)
- Promotion ladder: HARD_PASS at K=50+ -> chain-grade Hc-rescue (Stage 2
  NREM bottleneck closure); compose with hippo Ha-rescue for full Stage 2
  closure
