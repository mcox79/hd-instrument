# Prereg: substrate_schema_exemplar_bayes_capacity_stress_v2

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Stage 2 capacity-stress drill — v1 MM -> chain-grade promotion path
**Drill source:** Skunkworks 2026-06-28 — v1 atomized as MIDDLE_BAND cross-seed AGG (commit 7274bafb). v1 results:
  - 3 seeds, lift_pts {38, 36, 41} / 60 — discriminator FIRES
  - avg_bayes_minus_nn {0.300, 0.306, 0.327} — mechanism advantage observable
  - low_load_sat=True (BAYES saturates at small load)
  - **cliff_observable=False (no capacity cliff in v1's regime)**
  - capacity_scaling_met=False (lift doesn't survive capacity stress)
  Recommendation: re-test at un-saturated low_load regime (higher capacity bound) so cliff becomes observable; if BAYES > NN lift survives the cliff, MB cross-seed AGG can promote to chain-grade.
**Stage:** Stage 2 (substrate higher-function characterization — schema Bayesian inference cliff)
**P_deflated:** 0.55 (existing chain-grade primitive at 75% completeness; capacity-stress = bounded discriminator drill on known mechanism; cliff regime well-characterized by Kanerva alpha-bound algebra)
**Phase-diagram axis:** (n_exemplars_per_class, n_classes, N_DIM) capacity-stress sweep at fixed prior_strength=1.0

## SUBSTRATE-AS-CANONICAL prior work

- `exp_substrate_schema_exemplar_bayes_phase_diagram_v1_seed_{7,13,19}` (2026-06-28): v1 baseline, MIDDLE_BAND, cliff_observable=False
- `exp_substrate_sequence_binding_K_cliff_phase_diagram_v1`: sibling structural template (chunked-per-seed; K cliff sweep)
- Existing chain-grade Stage 2 schema exemplar-Bayes primitive (75% completeness ANCHOR 3; v1 raised to ~80%; v2 promotes to chain-grade phase-characterization if cliff fires)

## HYPOTHESIS

Substrate **schema exemplar-Bayes** at capacity stress: same mechanism as v1 (Bayes posterior aggregation across stored exemplars per class), tested in regime where K_total / N approaches and exceeds the Kanerva alpha-cliff. Predict:

- At low K_total / N (alpha << alpha_cliff): both BAYES and NN saturate near 1.0 (SAT regime).
- At alpha ~ alpha_cliff: BAYES > NN by 0.15+ as Bayesian aggregation extracts signal NN cannot (CLIFF regime — where mechanism advantage is maximally visible).
- At alpha >> alpha_cliff: both BAYES and NN collapse to chance (FLOOR regime; both fail).

**Capacity bound (Kanerva bipolar):** capacity ~ 0.15 * N codes distinguishable; cliff at K_total/N ~ alpha_cliff = 1 / (4 * log(N)).

For our chosen grid:
| N     | log(N) | alpha_cliff | K_total at cliff |
|-------|--------|-------------|------------------|
| 2048  | 7.62   | 0.0328      | ~67              |
| 4096  | 8.32   | 0.0301      | ~123             |
| 8192  | 9.01   | 0.0277      | ~227             |
| 16384 | 9.70   | 0.0258      | ~422             |

**Sweep axes (CLIFF-DISCRIMINATING, NOT just "push high"):**

- **n_exemplars_per_class in {10, 50, 100, 200}** (4 points; spans below-cliff to above-cliff)
- **n_classes in {10, 50, 200, 500}** (4 points; class load interference; 500 forces FLOOR per empirical probe)
- **N_DIM in {2048, 4096, 8192, 16384}** (4 points; capacity ceiling sweep)
- **prior_strength = 1.0 fixed** (same as v1; ablate separately if needed)
- **= 64 phase points per seed** (4 x 4 x 4)

EMPIRICAL PROBE 2026-06-28: alpha-cliff theory (1/(4*log(N))) UNDERESTIMATES Bayesian aggregator robustness — BAYES holds at 0.60 at alpha=19.5 (n_ex=200, n_cl=200, N=2048). True cliff observed via class-interference: BAYES crashes to 0.15 at n_cl=500. Hence N_CLASS_VALUES revised to include 500 (replacing original 100 in v2.0 grid).

Predicted regime coverage at this grid (K_total = n_ex * n_cl):

| K_total range | alpha at N=2048 | alpha at N=8192 | regime         |
|---------------|-----------------|-----------------|----------------|
| 100 (10x10)   | 0.05            | 0.012           | EDGE..SAT      |
| 500 (10x50)   | 0.24            | 0.06            | CLIFF..CLIFF   |
| 5000 (50x100) | 2.44            | 0.61            | FLOOR..CLIFF   |
| 40000 (200x200)| 19.5           | 4.88            | FLOOR..FLOOR   |

So at small N=2048 + large K (200x200), we hit FLOOR; at large N=16384 + small K (10x10), we hit SAT. Mid-band points sweep through CLIFF. v1's grid (n_ex={1,5,10,50,100}, n_cl={2,5,10,50}, N={2048,4096,8192}) max K_total was 100*50=5000 and minimum K_total was 1*2=2 — heavy SAT bias, no FLOOR coverage. v2 expressly pushes upward to FLOOR while preserving SAT corner.

## ARMS (3) — per phase-point

1. **ARM_SCHEMA_BAYES** — full Bayes posterior aggregation: `posterior(c | q) ~ p(c) * sum_k exp(beta * cos(q, e_c_k))` then argmax. **The mechanism (same as v1).**
2. **ARM_NEAREST_EXEMPLAR** — argmax_c argmax_k cos(q, e_c_k); single nearest exemplar. **Discriminator floor — proves Bayes aggregation > best-NN.**
3. **ARM_UNIFORM_RANDOM** — random class assignment. **Chance floor; rules out artifact (~1/C accuracy).**

**arms-must-differ at each phase point:** BAYES > NN by >= 0.15 at HARD_PASS bands. If BAYES == NN at ALL points (within tolerance 0.02), META_RULE flag = "mechanism not firing" (Bayes degenerated to NN — bug).

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = classification accuracy in [0,1])

Phase-diagram headline: **bayes_advantage_per_(n_exemplars, n_classes, N)** = ARM_BAYES_acc - ARM_NN_acc; **cliff_observable** = some phase point has ARM_BAYES < 0.40 (capacity FLOOR observable); **capacity_scaling_met** = capacity advantage survives stress (mid-band N=8192 BAYES > mid-band N=2048 BAYES by >= 0.05).

- **HARD_PASS** (chain-grade phase-diagram characterization — promotion from MB cross-seed AGG):
  - For >= 25 of 64 phase points, ARM_BAYES - ARM_NN >= 0.15 (Bayes provides aggregation lift)
  - **cliff_observable=True**: >= 10 of 64 phase points with ARM_BAYES < 0.40 (capacity FLOOR observable)
  - low_load_sat=True: >= 1 phase point (n_ex >= 50, n_cl <= 50, N >= 8192) with ARM_BAYES >= 0.85
  - arms-must-differ: avg(ARM_BAYES - ARM_NN) across all 64 points >= 0.10
  - capacity_scaling_met=True: N=8192 top-third mean BAYES > N=2048 top-third mean BAYES by >= 0.05
  - ARM_UNIFORM_RANDOM ~ 1/C at each point (sanity)

- **MIDDLE_BAND**:
  - ARM_BAYES - ARM_NN >= 0.15 in 12-24 phase points (regime-narrow Bayes lift)
  - OR avg(ARM_BAYES - ARM_NN) in [0.05, 0.10] (modest aggregation effect)
  - OR cliff_observable=True but capacity_scaling_met=False
  - OR capacity_scaling_met=True but cliff_observable=False

- **HARD_FAIL**:
  - **HARD_FAIL_NO_CLIFF** (NEW): cliff_observable=False (no point with BAYES < 0.40) AND ALL points BAYES >= 0.85 (sweep missed regime; same v1 failure mode)
  - OR avg(ARM_BAYES - ARM_NN) < 0.05 (Bayes posterior not load-bearing over NN)
  - OR ARM_BAYES <= ARM_NN at HIGH-class-load sweet-spot (n_ex>=50, n_classes>=50, N>=8192) within tolerance 0.02 (mechanism not firing). NOTE: at very high K_total/N, BAYES~NN~chance is EXPECTED FLOOR, NOT pathology.
  - OR ARM_UNIFORM_RANDOM > 0.20 above 1/C floor at ANY point (random arm bug)

**HEADLINE per (n_exemplars, n_classes, N):** bayes_advantage value — this is the load-bearing phase-diagram output.

## FAIRNESS GATES (META_RULE_AC/AE/AF)

- Same encoder (bipolar random HDC) for both BAYES and NN arms.
- Same class+exemplar codebook per seed.
- Same query set per seed.
- BAYES and NN consume IDENTICAL query encoding; only readout differs (Bayes posterior aggregation vs argmax NN).
- beta (Bayes temperature) computed from class capacity: `beta = log(n_classes) / 0.1` so log-sum-exp is well-conditioned.
- Q-discipline: ARM_BAYES = 1.000 at high-load points (e.g. n_ex=200, n_classes=200, N=2048) triggers leakage audit.

## CARDINALITY (META_RULE_H_ANCHOR)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms x 4 n_ex x 4 n_classes x 4 N x 20 queries = **3840 records per seed**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms x 6 corners x 5 queries = **90 records per seed**
- **EXPECTED_N_SEEDS** = 3 chunked siblings (seed 7, 13, 19)
- **EXPECTED_N_UNITS_AGGREGATE_FULL** = 3840 x 3 = **11520 records**

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == expected_n)` per sibling.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

Smoke 6 corners (chosen to FIRE the discriminator at smoke time):

| corner                           | n_ex | n_cl | N    | K_total | alpha (vs cliff)    | expected_BAYES   | expected_NN     | expected_diff |
|----------------------------------|------|------|------|---------|---------------------|------------------|-----------------|----------------|
| low-load saturate                | 50   | 10   | 8192 | 500     | 0.06 (~2x cliff)    | HIGH (>=0.85)    | MID (0.55-0.80) | LARGE (>=0.15) |
| sweet-spot CLIFF Bayes-lift      | 100  | 50   | 4096 | 5000    | 1.22 (~40x cliff)   | LOW (<0.40)      | LOW (<0.30)     | SMALL-MID (>=0.05) |
| mid-load BAYES strongest         | 50   | 50   | 8192 | 2500    | 0.31 (~10x cliff)   | MID (0.50-0.80)  | LOW (0.30-0.50) | LARGE (>=0.20) |
| capacity FLOOR                   | 200  | 200  | 2048 | 40000   | 19.5 (~600x cliff)  | LOW (<0.30)      | LOW (<0.20)     | SMALL (~0.05) |
| SAT at large N                   | 10   | 10   | 16384| 100     | 0.006 (~0.2x cliff) | HIGH (>=0.90)    | HIGH (>=0.80)   | SMALL (0.05-0.15) |
| pure CLIFF                       | 100  | 100  | 8192 | 10000   | 1.22 (~40x cliff)   | LOW-MID (0.20-0.50)| LOW (0.15-0.40) | SMALL-MID (>=0.05) |

Smoke gate (BLOCK full dispatch if not met):
- 6 corners all RUN (no silent except)
- >= 2 corners with ARM_BAYES - ARM_NN >= 0.15 (mid-load + sweet-spot or sat)
- >= 1 corner saturates (SAT at large N: BAYES >= 0.85)
- **>= 1 corner low (capacity FLOOR or pure CLIFF: BAYES < 0.40) — REQUIRED so smoke proves cliff_observable**
- ARM_UNIFORM_RANDOM at ~ 1/n_classes (within +/- 0.15) at every corner
- cardinality_ok (observed_n == 90)
- arms_differ verified (BAYES vs NN per-corner diffs > 0 except possibly the FLOOR corner where both crash)

If discriminator does NOT fire at smoke (e.g. BAYES saturates everywhere — repeating v1's failure), HARD_FAIL prior to full dispatch.

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. META_RULE_X main-guard. PROT-021 N+anchor stamp on every partial.

## HARDWARE / DISPATCH

- **CPU-only cell** (no torch; numpy + scipy.special.logsumexp). All ops are O(C * K * N) matrix multiplies — for largest grid (n_ex=200, n_cl=200, N=16384) the per-point cosine matmul is (Q=20) x (CK=40000) x (N=16384) = ~13 GFLOPs/pt; ~5-15s/pt. 64 pts -> 5-15 min/seed full.
- Target queue: **local_cpu_queue** (Research directive; numpy CPU not GPU-bound).
- timeout_s = 4500 (75min; 5x safety margin for largest-N points).

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_7.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_13.py`
- `exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_19.py`

Shared core: `experiments/_substrate_schema_exemplar_bayes_capacity_stress_v2_core.py`
Resumability: `experiments/_seed_checkpoint.py` (PROT-021 anchor + N stamping).

Aggregation post-hoc: combine 3 sibling metrics.json -> phase-map matrix; verdict computed per-sibling AND combined.

## SUBSTRATE PREREQS (chain-grade primitives cited)

- Bipolar random HDC codebook (chain-grade per `exp_substrate_sequence_binding_v1`)
- Cosine similarity readout (chain-grade ubiquitous)
- Log-sum-exp Bayesian aggregation (substrate-native; no exotic ops)
- Class membership encoded via stored exemplar set (vmPFC schema analog)
- v1 atom (MM cross-seed AGG) demonstrates mechanism FIRES at non-saturated regime

## HDLAB_QUEUE CONTRACT (Skunkworks META RULE)

`# PRESERVE_ENV_VARS: HDLAB_QUEUE` header in cell files.
NO gpu_mandate_check that blocks CPU dispatch. This is a CPU-only cell.

## PRE-REG FIELDS

- expected_n_units_full = 3840 (per seed; 64 pts x 3 arms x 20 queries)
- expected_n_units_smoke = 90 (6 corners x 3 arms x 5 queries)
- HARD_FAIL_CARDINALITY_BREACH (asserted in metrics.json `cardinality_ok` field)
- HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR (asserted via all_saturated / avg_bayes_advantage_too_low)
- HARD_FAIL_ARMS_IDENTICAL (asserted via avg_bayes_minus_nn < 0.05)
- **HARD_FAIL_NO_CLIFF** (NEW v2-specific: cliff_observable=False AND all_saturated; catches v1 failure mode)
- discriminator_survives_scale (smoke gate gating full dispatch)
- CARDINALITY_OK
- META_RULE_AM_regime_flip (BAYES <= NN at low-load corner)
- §13 patterns (3-arm bracket; cliff axis; arms-must-differ)

## PHASE-DIAGRAM DECISION TABLE

| Smoke + Full outcome                                         | Phase-diagram verdict                                              |
|--------------------------------------------------------------|--------------------------------------------------------------------|
| HARD_PASS — Bayes lift in 25+ pts + cliff observable + scaling | Schema exemplar-Bayes chain-grade phase-characterization; MM -> chain-grade promotion path complete |
| MIDDLE_BAND — partial cliff coverage                          | Regime-narrow; another v3 with different alpha-band                |
| HARD_FAIL_NO_CLIFF — saturation again                         | Sweep STILL missed regime; v3 needs even higher K_total (push to n_ex=500 or n_cl=500) |
| HARD_FAIL — mechanism off                                     | Mechanism not load-bearing; abandon promotion path                  |

## NOTES

- v1 ran 60 pts with K_total in [2, 5000]; cliff_observable=False (max alpha at N=2048 = 5000/2048 = 2.44; insufficient stress at larger N where alpha was much smaller).
- v2 runs 64 pts with K_total in [100, 40000]; max alpha at N=2048 = 19.5 (CLEAR FLOOR); min alpha at N=16384 = 0.006 (CLEAR SAT). Covers full SAT-CLIFF-FLOOR phase diagram.
- Per USER 2026-06-26 discriminator-must-survive-scale: smoke uses full-N (16384) corner explicitly.
- Per USER 2026-06-27 substrate-as-canonical: builds on existing chain-grade schema exemplar-Bayes atom + v1 MIDDLE_BAND AGG.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring v1.
- Compute formula-derived bands at design-time (Fix: compute formulas in code 2026-06-27): all alpha values + cliff regimes computed via Python prior to authoring this prereg.
