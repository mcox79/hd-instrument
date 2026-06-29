# Pre-registration: substrate_refuse_gate_adaptivity_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER + Research directive (2026-06-28). Systematic component-substitution phase-diagram series. Refuse-gate has been chain-grade-tested at ONE point only (`substrate_refuse_gate_v_rel_extension_v1` at V_REL=256 with fixed_threshold mechanism, commit 2026-06-25). The gate FAMILY (adaptivity strategy) has never been compared across alternatives. This cell SUBSTITUTES the refuse-gate decision rule (OUTER axis) holding the V_REL=256 envelope FIXED.

## Anchor

`substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed pattern, matches `substrate_pc_cleanup_family_phase_diagram_v1`).

Shared core: `experiments/_substrate_refuse_gate_adaptivity_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; numpy-light; expected ~5-10s wall per seed smoke).
- **Full queue:** `remote_cpu_queue` (cpu_runner_0 alive idle ~3h per USER context; numpy-light cell).
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap)

Chain-grade refuse-gate evidence to date (PASS at V_REL=256, `substrate_refuse_gate_v_rel_extension_v1` 2026-06-25) uses a SINGLE adaptivity strategy: **fixed similarity threshold** `refused = (sim < SUBJECT_AUDIT_THR=0.40)`. The threshold is hand-tuned at the cell-design layer and held constant across queries.

Alternative gating strategies routinely outperform fixed thresholds in psychophysics / OOD-detection / abstention literature:
- **Bayesian credible-interval gating:** refuse when posterior P(in-domain | sim) credible interval includes the boundary (NOT a point threshold; carries uncertainty about its own decision)
- **Learned logistic readout:** train a single sigmoid on calibration set; threshold becomes implicit (parameter of a learned classifier, not a magic-number)
- **Percentile-based gating:** refuse when query similarity falls below P-th percentile of calibration-set in-domain similarities (DATA-DRIVEN, no manual threshold)

Each strategy adapts differently to: (a) different similarity-distribution shapes (Gaussian vs heavy-tail), (b) calibration set size (small-data vs large-data regimes), (c) class imbalance (more vs fewer OOD queries).

**The gap:** fixed_threshold may be dominated by an adaptive family at V_REL=256, OR may be invariant across families (cleanup primitive saturates the readout regardless of which gate). Neither outcome was checked.

## Refuse-gate families (the OUTER axis)

Four families, each producing a `refused: bool` decision from query similarity to substrate:

| Family | Decision rule | Calibration-set dependence | Threshold magic-number |
|--------|---------------|----------------------------|------------------------|
| `fixed_threshold` | `refused = (max_sim < 0.40)` | NONE (hard-coded) | YES (0.40 from prior cell) |
| `adaptive_bayesian_CI` | Build Beta(alpha, beta) posterior over in-domain similarity from calibration; refuse if query sim falls below CI lower bound (95% CI) | YES (calibration size shifts CI width) | NO (CI is calibration-derived) |
| `learned_logistic` | Fit sigmoid `P(in | sim)` on calibration; refuse if P < 0.5 | YES (more cal data -> tighter sigmoid) | NO (implicit via sigmoid coefs) |
| `percentile_based` | Compute 5th percentile of calibration in-domain max-sim; refuse if query max-sim below that | YES (calibration sets percentile) | NO (data-driven percentile) |

**Apples-to-apples:** the SAME substrate (V_REL=256, V_C=600, N), the SAME query corpus, the SAME max-similarity computation feed each gate. ONLY the decision rule downstream of the similarity score differs.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| refuse_gate_family (OUTER) | {fixed_threshold, adaptive_bayesian_CI, learned_logistic, percentile_based} | 4 |
| query_regime (inner) | {PURE_IN_DOMAIN, PURE_OUT_OF_DOMAIN, NEAR_DOMAIN_MIXED, AMBIGUOUS_BOUNDARY} | 4 |
| V_REL_calibration_size (inner) | {64, 256, 1024} | 3 |

Fixed config: `N=8192`, `V_C_IN=600` (200 per category x 3 cats), `V_C_OUT=600`, `V_REL=256` (matches CG envelope), `N_QUERIES_PER_REGIME=80`. Encoder: `binary_bipolar` dense. Score: max cosine to in-domain substrate.

**Cardinality FULL per seed:** `4 * 4 * 3 = 48` phase points per seed.
**Cardinality SMOKE per seed:** `4 * 2 * 1 = 8` corner points per seed (regimes ∈ {PURE_IN, PURE_OUT}; cal_size=64).

Smoke uses `N=2048`, `V_C_IN=150` (50/cat), `N_QUERIES=30`.

Seeds: 7, 13, 19 (matches sibling phase-diagram convention).
Total FULL grid: 48 pts × 3 seeds = 144 phase points.

## Hypothesis

**H1 (PRIMARY):** Refuse-gate families WILL differ on (TPR, TNR) across regimes. At AMBIGUOUS_BOUNDARY regime, the calibrated families (bayesian_CI, percentile, logistic) outperform fixed_threshold's hand-tuned 0.40. At PURE_IN and PURE_OUT, all four families produce near-identical decisions (signal/noise gap is large).

**H2 (calibration-size effect):** adaptive_bayesian_CI and learned_logistic improve monotonically with cal_size (64 -> 1024). percentile_based plateaus quickly. fixed_threshold is cal-size INVARIANT (doesn't use calibration).

**H3 (positive control):** `fixed_threshold` at `V_REL=256, PURE_OUT_DOMAIN, cal_size=any` reproduces prior chain-grade evidence (refuse_rate >= 0.85 on PURE_OUT queries — matches `substrate_refuse_gate_v_rel_extension_v1` HARD_PASS_BOTH_WORK at V_REL=256). If control fails: cell HARD_FAILs with verdict CONTROL_FAIL.

**H4 (null):** All 4 refuse-gate families produce TPR, TNR within +/- 0.05 at every (regime, cal_size). If H4 holds, refuse-gate FAMILY choice is not a discriminating lever for refuse decisions — load-bearing **negative** finding (substrate cleanup dominates the readout regardless of decision rule). Downstream cells free to pick simplest family.

**H5 (dominance):** One family strictly dominates all others across all 4 regimes. If H5 holds at AMBIGUOUS_BOUNDARY (the hardest regime), substrate should switch default. Calibrated families predicted favorite per OOD literature.

## Discriminator: per (family, regime) TPR + TNR + F1

For each (family, regime, cal_size) phase point we measure:
- `TPR` (true-positive refuse rate): for OOD queries (PURE_OUT, AMBIGUOUS), fraction CORRECTLY refused
- `TNR` (true-negative answer rate): for in-domain queries (PURE_IN), fraction CORRECTLY answered
- `F1`: harmonic mean of TPR and TNR (joint quality)
- `ARM_RANDOM_FLOOR`: random Bernoulli(0.5) refuse decisions (no info); used for arms_differ gate (META_RULE_AF). Random F1 ~ 0.50.

**Per-family discriminating_fraction prediction (HYPOTHESIZED@):**
- fixed_threshold: ~0.30 (well-tuned at this V_REL but not adapted to AMBIGUOUS)
- adaptive_bayesian_CI: ~0.40 (best at small cal; CI captures uncertainty)
- learned_logistic: ~0.40 (best at large cal; needs data to converge)
- percentile_based: ~0.35 (robust, simple, data-driven)

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold (>= 15/48 pts per seed in HARD_PASS+MIDDLE_BAND across all families).

## Pre-reg bands (per-point; LOCKED at module init)

Per-point F1 tiering:

| Tier | F1_mechanism | Discriminator (F1_mech - F1_random) |
|------|--------------|-------------------------------------|
| SATURATED | >= 0.98 | record but down-weight (META_RULE_S Q-suspect) |
| HARD_PASS | [0.85, 0.98) | >= 0.30 |
| MIDDLE_BAND | [0.65, 0.85) | >= 0.15 |
| HARD_FAIL | (0.30, 0.65) | family is breaking |
| FLOOR | <= 0.30 | gate at chance |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_ADAPTIVITY_DISCRIMINATION**: cardinality_ok + arms_differ (vs random_floor) + ALL 4 family-pair-hashes differ at >= 2 of 6 pairs + >= 15/48 pts HARD_PASS+MIDDLE_BAND + positive control reproduces (fixed_threshold @ PURE_OUT @ any cal: refuse_rate >= 0.85) + at least one family shows AMBIGUOUS_BOUNDARY differentiation
- **MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC**: arms_differ + family-pair hashes differ but disc_pts < 15
- **MIDDLE_BAND_NULL_FAMILY_INVARIANCE**: arms_differ but ALL 4 family-pair-hashes IDENTICAL (H4 confirmed — gate family doesn't matter for refuse decisions; honest-negative finding routes back to Research)
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 48
- **HARD_FAIL_ARMS_IDENTICAL**: mechanism F1 hash matches random_floor F1 hash for any family (gate not working)
- **HARD_FAIL_CONTROL_FAIL**: fixed_threshold @ PURE_OUT @ any cal: refuse_rate < 0.85 (prior chain-grade evidence not reproduced; halt before any framing claims)

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 8/8 corner points + arms_differ + 4 distinct family hashes + positive control (fixed_threshold @ PURE_OUT @ cal=64): refuse_rate >= 0.85 + at least 1 family shows F1 in [0.30, 0.95] at PURE_OUT (cliff-edge visible)
- **HARD_FAIL_SMOKE_FAMILY_COLLAPSE**: 2+ families produce identical refuse-decision hashes at smoke (mechanism bug)
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails at smoke
- **HARD_FAIL_SMOKE_NO_DISCRIMINATION**: zero pts in HARD_PASS+MIDDLE_BAND tiers at smoke
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE** (USER 2026-06-26 DISCRIMINATOR-SURVIVES-SCALE): smoke at N=2048 shows ALL 4 families collapsed to F1 saturation >= 0.98 (signal too strong at this regime; can't discriminate)

## Calibration selftest (refuse-gate mechanism sanity)

For each family at N=512, V_C=12, V_REL=8:
- (a) at PURE_IN query (clean subject + clean in-relation): the gate ANSWERS (refused=False) >= 80% of the time
- (b) at PURE_OUT query (out-subject + out-relation): the gate REFUSES (refused=True) >= 80% of the time
- (c) at AMBIGUOUS query (boundary): all 4 families return a decision (no crash); decision values across families differ for at least 1 pair (mechanism distinctness sanity)

If ANY family fails (a) or (b), selftest exit 1 with verdict_msg naming the failure. This catches broken gate implementations at selftest time.

## CRLB / threshold prediction (META_RULE_AG)

At `V_REL=256, N=8192, M=600`:
- In-domain max-sim distribution: signal cos ~ 0.80 (10% bit-flip noise), variance ~ 1/sqrt(N) (~ 0.011)
- Out-domain max-sim distribution: noise floor sqrt(2 ln V_C / N) ~ 0.04
- Gap: 0.80 - 0.04 = 0.76 (massive; supports H4 partial — easy decisions)
- AMBIGUOUS regime: queries straddle the boundary (noise = signal); family choice may matter most here

`crlb_threshold_prediction = noise_floor + 3 * sigma_signal` computed per (N, V_C) for sanity stamping.

## Arms per point (META_RULE_AF)

Each (family, regime, cal_size) point logs TWO arm results:
1. `ARM_MECHANISM` — family's refuse decisions across query corpus
2. `ARM_RANDOM_FLOOR` — Bernoulli(0.5) refuse decisions, same query corpus; F1 ~ 0.50

`arms_differ_sha256` per family: SHA-256(json(family.decisions_per_point)) != SHA-256(json(random.decisions_per_point)).

`family_pair_hashes` (META_RULE_AF extension): SHA-256(json(family_decisions)) for each family. All 4 hashes computed; for chain-grade discrimination claim, at least 2 of the 6 pairs must differ. If all 4 identical, H4 NULL finding.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 8 (4 families * 2 regimes * 1 cal_size * 1 seed)
FULL : EXPECTED_N_UNITS = 48 (4 families * 4 regimes * 3 cal_sizes * 1 seed)
```

HARD_FAIL if observed != expected.

## Compute routing (Fix #24 note)

This cell is CPU-natural — numpy-only, no torch. binary_bipolar substrate at N=8192 + V_C=600 + V_REL=256 + 80 queries/regime = ~38MB substrate matrix + ~5KB queries. Total runtime estimate ~70-90s per seed FULL on CPU.

- No GPU mandate
- Substrate constructed once per (cal_size); queries derived per regime
- Per-point peak memory tracked

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_refuse_gate_adaptivity_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py`.

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics written before any heavy work
2. crash-diag: outer try -> import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (mechanism vs random; per-family)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 family arms produce distinct hashes (else family substitution didn't happen)
- META_RULE_AG: per-family CRLB / noise-floor pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (48 full, 8 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24): production-scale calibration; verify-referent; 1.000 results suspect
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at N=2048 cliff-edge — abort if smoke saturates all families
- BAND-FLOOR-IS-MIDDLE-BAND: clearing 15-MB threshold AND positive control reproducing AND >= 2 family-pair-hashes differing — all three required for HARD_PASS
- Honest-downward classification per family
- Substrate-as-canonical query-first: `substrate_refuse_gate_v_rel_extension_v1` (2026-06-25 chain-grade at V_REL=256) reviewed; this cell SUBSTITUTES the gate family, not the V_REL envelope

## Positive control

`fixed_threshold` at `V_REL=256, PURE_OUT_OF_DOMAIN, cal_size=any`: refuse_rate >= 0.85. Reproduces prior `substrate_refuse_gate_v_rel_extension_v1` chain-grade evidence (HARD_PASS_BOTH_WORK at V_REL=256, near_refuse >= 0.85; same gate primitive used here as fixed_threshold arm). If control fails: cell HARD_FAILs with verdict CONTROL_FAIL.

Smoke-variant positive control: `fixed_threshold` at `V_REL=256, PURE_OUT, cal_size=64, N=2048`: refuse_rate >= 0.75 (relaxed for smaller smoke N).

## Composition edges (substrate atomization context)

- This cell uses the FIXED V_REL=256 envelope (matches CG evidence) and SUBSTITUTES the gate adaptivity decision rule. SHAPE_MATCH: each family's input is `(query_sim_score: float, calibration_set: optional)` and output is `refused: bool`.
- Gate family is the COMPONENT being swept; substrate cleanup + V_REL=256 envelope is the COMPOSED-WITH-it primitive (unchanged across arms).
- Downstream atomization: HARD_PASS_ADAPTIVITY_DISCRIMINATION promotes the winning family for the refuse-gate ROLE.

## ETA

Per-point on CPU (N=8192, V_C=600, V_REL=256, 80 queries): substrate build cached per cal_size; per-family eval ~0.3-1.0s. 48 pts/seed * 1s = ~50s science + 10s init + 3 cal_size substrate builds at ~5s each = ~75-90s per seed FULL on CPU.

Per-point on CPU (smoke; N=2048, V_C=150, 30 queries): ~0.1s. 8 pts/seed * 0.1s = ~1s science + 2s init = ~3-5s per seed SMOKE on CPU.

Timeouts:
- SMOKE: 60 s
- FULL: 1200 s (20 min; ~13x margin)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (no LLM calls; pure substrate mechanism).

## Smoke gate (MUST pass before FULL dispatch)

1. 8 corner points all ran (no silent except)
2. cardinality_ok: observed_n_units == 8
3. arms_differ_sha256.differ == True for ALL 4 families
4. family_pair_hashes: 4 distinct family decision hashes
5. positive_control: fixed_threshold @ PURE_OUT @ cal=64, N=2048 shows refuse_rate >= 0.75
6. discriminator visible: F1 spread across families >= 0.05 OR all families NOT in saturation (>= 0.98)

If gates 1-5 fail, FULL dispatch is HARD-blocked. Gate 6 fires HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE if all 4 saturate.

## Family routing tier classifications

Per-family downstream verdict (informational; cell aggregator stamps these):
- DOMINANT_FAMILY: F1_mean > 0.05 above all others
- COMPETITIVE_FAMILY: F1_mean within +/- 0.03 of best
- DOMINATED_FAMILY: F1_mean > 0.05 below best (downstream should NOT default to this family)

## Outputs

`data/exp_substrate_refuse_gate_adaptivity_phase_diagram_v1_seed_{7,13,19}/metrics.json` with:
- phase_map (list of 48 dicts; one per phase point)
- per_family_summary (4 entries; tier classification + F1_mean + TPR_mean + TNR_mean + cal_size_sensitivity)
- family_pair_distinctness (6 pair-comparisons)
- positive_control_result (fixed_threshold refuse_rate @ PURE_OUT)
- crlb_predictions (per cal_size)
- arms_differ_sha256 (per family)
- tier_counts per family + overall

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_ADAPTIVITY_DISCRIMINATION: SUBSTRATE_REFUSE_GATE_FAMILY_DISCRIMINATING + WINNING_GATE_FAMILY
- if MIDDLE_BAND_NULL_FAMILY_INVARIANCE: REFUSE_GATE_FAMILY_NOT_DISCRIMINATING_LEVER atom
- if HARD_FAIL: NEEDS-RERUN with smoke-gate-specified fix
