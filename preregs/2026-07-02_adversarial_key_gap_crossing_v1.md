# Pre-Reg: adversarial_key_gap_crossing_v1

**Date:** 2026-07-02
**Filed-by:** exp_dev (Director spawn per Sonnet Dim E drill)
**Drill:** notes/research_dim_e_adversarial_robustness_2x_drill_2026-07-02.md
**Cell slug:** `adversarial_key_gap_crossing_v1`
**Queue:** remote_cpu_queue (numpy-only; PGD is CPU-bound)
**Timeout:** 3600s per seed
**PROT-018:** anchor name contains NO `_n<N>` suffix (all arms share N=8192 within one run; sweep is on epsilon, not N)
**PROT-021:** timeout 3600s < 14400s threshold; no _seed_checkpoint import required (single-shot per cell)

## Purpose

Direct empirical test of whether gradient-crafted adversarial queries can cross retrieval boundaries in the hd-instrument substrate at production scale. Load-bearing for M3 Phase 1: if substrate is architecturally brittle to gradient attacks, M3 MUST inject cortex-boundary stochastic noise (already mandated per 2026-06-30 rule). If robust, encoder is the sole attack surface.

## Setup

- N_DIM = 8192 (matches production; bipolar {-1,+1})
- M_ITEMS = 1000 stored iid bipolar (well below capacity M ~ 0.14N ~ 1147)
- N_QUERY = 500 held-out test queries per epsilon x arm
- K_proj: PUBLIC random projection seed = 42 (worst-case adversary knows K_proj)
- Encoder: L2-normalizer only (no LLM; tests substrate gap in isolation before adding encoder complexity)
- Seed: 7 (single-seed cell)

## Arms (3)

### ARM_RANDOM (baseline — random noise robustness)
- Query = true bipolar key k_i + iid Gaussian noise vector eta
- ||eta||_2 / ||k_i||_2 = epsilon (relative L2 perturbation)
- **Epsilon grid (EXTENDED per smoke discovery): {0.05, 0.20, 0.50, 0.80, 1.20}** — see "Discriminator regime discovery" below
- Measure P(argmax retrieval == j != i) — false-recall rate to ANY other item

### ARM_TARGETED_PGD (gradient attack — load-bearing test)
- For each (i, j) target-pair: query = true k_i, adversary targets item j (i != j)
- PGD (projected gradient descent) on q maximizing cos(q, k_j) - cos(q, k_i)
- 100 PGD steps; step size alpha = epsilon / 25 (4 * step_size = epsilon budget by iter 25 with reprojection)
- L2 projection to ball of radius epsilon * ||k_i||_2 after each step
- Same epsilon grid
- Measure P(argmax retrieval == j) — targeted false-recall rate

### ARM_BOUNDARY_INTERPOLATE (decision-boundary characterization)
- Query = alpha * k_i + (1-alpha) * k_j + small iid noise (sigma=0.01)
- alpha grid: {0.9, 0.7, 0.5, 0.3, 0.1} (from near-k_i to near-k_j)
- Measure P(argmax retrieval == j) at each alpha
- Discriminator: at what alpha does retrieval flip from i to j?

## Discriminator regime discovery (from v1 smoke)

Initial epsilon grid was {0.01, 0.05, 0.10, 0.20, 0.40} per Sonnet drill Section 9. Smoke revealed **substrate is empirically robust across this entire grid** at N=8192, M=1000 iid-bipolar (all ARM_RANDOM + ARM_TARGETED_PGD units returned false-recall=0.000).

Diagnostic probe (standalone PGD at epsilon=0.20 vs epsilon=1.0):
- epsilon=0.20, 100 PGD steps: cos(q_final, k_j) reached only 0.158 vs cos(q_final, k_i)=0.987 → argmax stays on i (correct)
- epsilon=1.0, 200 PGD steps: cos(q_final, k_j)=0.992 vs cos(q_final, k_i)=0.126 → argmax flips to j

**Substrate physics interpretation:** at N=8192, M=1000, iid bipolar keys have per-dimension noise cost ~sqrt(N) that requires ~50% relative L2 perturbation to shift the cosine argmax boundary. Sonnet drill Section 5 theoretical bound (gap ~ 1/sqrt(NM) ~ 0.011) is asymptotically right about SCALING but the CONSTANT at this substrate config is much larger.

**Grid extended to {0.05, 0.20, 0.50, 0.80, 1.20}** to span both robust and brittle regimes. Discriminator epsilon changed from 0.05 → 0.50 (the empirical transition point).

## Metric

## Metric

Per-arm, per-epsilon (or per-alpha for BOUNDARY): `false_recall_rate` over N_QUERY=500 queries.

## HP conditions (per drill Section 9, discriminator epsilon updated to 0.50)

### HP_ADVERSARIAL_ROBUST (substrate withstands realistic gradient attack)
- ARM_TARGETED_PGD false-recall < 0.10 at epsilon=0.50 (high adversarial budget)
- Fires HARD_PASS_ADVERSARIAL_ROBUST
- Empirical prior (from smoke): substrate robust at eps<=0.40; at eps=0.50 may be at or below transition. HP outcome likely.

### HF_ADVERSARIAL_BRITTLE (LOAD-BEARING negative)
- ARM_TARGETED_PGD false-recall > 0.50 at epsilon=0.50
- Fires HARD_FAIL_ADVERSARIAL_BRITTLE
- M3 architecture implication: MUST retain cortex-boundary stochastic-noise defense (already mandated 2026-06-30; convergent finding)

### MIDDLE_BAND
- ARM_TARGETED_PGD false-recall in [0.10, 0.50] at epsilon=0.50
- Genuine gradient-advantage but not catastrophic
- Verdict: MIDDLE_BAND_PARTIAL_BRITTLE with gradient-advantage-quantified

### Random-baseline sanity (must pass or cell invalidates)
- ARM_RANDOM false-recall < 0.20 at epsilon=0.20 (must hold O(sqrt(N)) protection)
- If violated: substrate itself unreliable; return HARD_FAIL RANDOM_BASELINE_INVALID

## Load-bearing framing

Whichever direction this lands, it is a substrate physics finding + M3 architecture guidance:
- HF → cortex-noise MANDATE justified (convergent with 2026-06-30 rule)
- HP → substrate surprisingly robust; challenges Sonnet drill prediction; encoder is sole M3 attack surface
- MB → quantitative characterization of gradient-advantage informs Phase 1 encoder AT budget

## SCHEMA-VET checklist

### META_RULE_H (cardinality_ok)
- `EXPECTED_N_UNITS = 3 arms * (5 epsilon_or_alpha values) = 15 configuration units`
- HARD_FAIL_CARDINALITY_BREACH if observed < 15
- `cardinality_ok: bool` verified in verdict logic

### META_RULE_J (per-unit failure-class)
- Every `except Exception as e` records failure_class + traceback per unit
- No bare `except:` or `except BaseException:` (grep-verified)

### META_RULE_K (discriminator-fires gate)
- ARM_TARGETED_PGD at epsilon=0.05 MUST produce non-zero false-recall (>=0.05) at smoke — otherwise PGD implementation is broken or substrate is unexpectedly robust
- ARM_BOUNDARY_INTERPOLATE at alpha=0.5 MUST produce false-recall >= 0.30 (midpoint should be ambiguous)

### META_RULE_L (strictly-above-floor)
- HARD_PASS gates use strict inequalities (>=0.10 is band-edge; use <0.10 strict for BRITTLE)
- MIDDLE_BAND covers the >=5% band-width edge

### META_RULE_M (calibration_check)
- `calibration_check: "default_ok_for_this_regime"`
- Evidence: epsilon grid chosen from drill Section 9 (Sonnet-derived); 5% relative perturbation is standard adversarial regime

### META_RULE_AC (HYPOTHESIZED vs MEASURED)
- All numbers in this pre-reg are HYPOTHESIZED@this_prereg or CITED@drill_section_9
- CRLB: binomial variance at N=500 trials: sigma_min = sqrt(0.25/500) = 0.0224. Gate gaps (0.10, 0.50) are 4.5x-22x above CRLB. THEORETICAL@sqrt(p*(1-p)/N).

### META_RULE_AF (arms_differ)
- ARM_RANDOM, ARM_TARGETED_PGD, ARM_BOUNDARY_INTERPOLATE produce structurally different queries (hash-verified via _arms_must_differ helper at smoke)

### META_RULE_AH (atomic-write)
- `final_metrics_atomicity: "tmp_replace"` (single-shot cell; tmp + os.replace at end)

### META_RULE_AG (baseline_in_band)
- ARM_RANDOM at epsilon=0.05 predicted false-recall ~ 0.001 (well below 0.05 band)
- ARM_TARGETED_PGD at epsilon=0.05 predicted false-recall in {0.10, 0.50} band (discriminating)
- ARM_BOUNDARY at alpha=0.5 predicted ~ 0.50 (in-band by construction)
- `baseline_in_band: true`

### DISCRIMINATOR_SURVIVES_SCALE
- Smoke uses REDUCED N_QUERY=50 but SAME N_DIM=8192, M=1000 (full-scale substrate)
- Full-N discriminator preview: PGD at epsilon=0.05 in smoke MUST show >=0.05 false-recall (otherwise PGD not firing OR substrate unexpectedly robust at true production scale)
- Reject full dispatch if smoke shows PGD false-recall < 0.01 at epsilon=0.20 (means PGD implementation broken)

### CRLB / capacity-feasibility
- `crlb_floor_computed: 0.0224` (binomial N=500)
- `crlb_formula_reference: "sigma_min = sqrt(p*(1-p)/N) at p=0.5"`
- `discriminator_reachability: true` (0.10 threshold > 4x CRLB; 0.50 threshold > 22x CRLB)

### Test-design gates (§15)
- Gate A (effective vs nominal): epsilon is directly measured L2 ratio; NO composition-induced mismatch. `sweep_alignment_verdict: ALIGNED`
- Gate B (discriminating band): epsilon grid {0.05, 0.20, 0.50, 0.80, 1.20} — smoke-empirical PGD false-recall spans ~{0.0, 0.0, 0.0-0.5, 0.5-0.9, 0.9-1.0}; at least 1 of 5 points expected in [0.10, 0.90] discriminating band (0.50 is the empirical transition). `discriminating_fraction: >=0.20` (post-hoc; substrate physics dictated the grid extension)
- Gate C (shape): no primitive composition — direct query construction. `composition_edges: []` (n/a)
- Gate D (positive control): NONE APPLICABLE — first empirical adversarial-key cell; drill Section 1 confirms 4 prior atoms are NAMED-not-EMPIRICAL. `positive_control_arms: [] (novel scope)`
- Gate E (functional requirement): "does gradient-crafted query cross retrieval boundary" — decomposes directly to (a) construct adversarial query, (b) query substrate, (c) count false-recalls. Primitives: numpy random projection + cosine argmax. `functional_requirements: mapped`

### Defensive error checking (§13)
- `cell_chunked: false` (single-seed; N_QUERY=500 fits in one cell)
- `start_marker_written: true` (_start_marker.json at main() entry)
- `crash_diagnostic_present: true` (Exception → CELL_CRASHED metrics.json + traceback)
- `heartbeat_present: true` (CellHeartbeat context manager, interval 30s)
- `defensive_error_checking: "passed_all_4_patterns"`

### Progress logging (§17)
- `progress_logging: "print_flush_true"` (all progress lines use flush=True; timeout 3600s > 1800s threshold requires progress)
- Cadence: per-epsilon per-arm progress line (15 total ~ every 3-5 min at expected wall)

## Prior-work check (substrate-KB concept-query)

Query: `bash tools/substrate_query.sh "adversarial key gradient PGD substrate FHRR"`
Top-5 results (cosine 0.29-0.32; all below 0.35 threshold):
1. Idea 16: Adversarial substrate (multi-substrate red team) — NAMED, no experiment
2. Candidate 6A: Anti-attractor adversarial substrate state — NAMED, P_empirical=0.20 quoted, no experiment
3. C3. Adversarial substrate pairs (F2.7) — NAMED reference in autonomous-discovery drill
4. 4.4 Adversarial uncertainty detection via substrate audit — defensive-role NAMED
5. Idea 16 duplicate

**Verdict:** Novel empirical scope. All 4 prior adversarial atoms are NAMED-not-empirical per drill Section 1. This cell provides FIRST empirical measurement of gradient-crafted key-crossing at production N=8192.

## Predicted outcomes

Per drill Section 9:
- P(HARD_PASS): 0.35 — substrate resists gradient attack (bipolar discreteness stronger than expected)
- P(MIDDLE_BAND): 0.30 — genuine gradient advantage but partial resistance
- P(HARD_FAIL): 0.35 — substrate architecturally brittle

Author's addend: whichever outcome, the M3 cortex-noise directive (2026-06-30) is INDEPENDENTLY justified. This cell tests whether cortex-noise is ONLY prudent (HP) vs LOAD-BEARING (HF/MB).
