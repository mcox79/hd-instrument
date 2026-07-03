# Pre-registration: substrate_composed_encoder_v3_adaptive_alpha_smoke_2026_07_03

**Author:** hdi_exp_dev
**Date:** 2026-07-03
**Cell:** `experiments/exp_substrate_composed_encoder_v3_adaptive_alpha_smoke_2026-07-03.py`
**Module:** `hdlab/composed_encoder_v3.py` (13 selftests PASS) + `hdlab/late_combine.py::fit_weights_grid_2spoke`
**Related preregs:**
- `preregs/2026-07-03_substrate_composed_encoder_v3_smoke.md` — v3 EQUAL-alpha WordNet smoke (HF landed; commit `114a0f3cf`; Skunkworks VET commit `cc1807726`)

**Prior MEASURED values (all @ `data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json`):**
- ARM_V3_COMPOSED_EQUAL_ALPHA r@5 = 0.333 (per-seed [0.34, 0.33, 0.33])  MEASURED@aggregate.arm_v3_composed_equal_alpha_recall_at_5_mean
- ARM_VWFA_ALONE r@5 = 0.240 (per-seed [0.23, 0.25, 0.24])  MEASURED@aggregate.arm_vwfa_alone_recall_at_5_mean
- ARM_PPMI_ALONE r@5 = 0.340 (per-seed [0.34, 0.34, 0.34])  MEASURED@aggregate.arm_ppmi_alone_recall_at_5_mean
- ARM_V1_CONCEPT_ENCODER_COSINE r@5 = 0.160  MEASURED@aggregate.arm_v1_concept_encoder_cosine_recall_at_5_mean (Component C smoke)
- ARM_CHAR_TRIGRAM_UNSUP_REFERENCE r@5 = 0.280  MEASURED@aggregate.arm_char_trigram_unsup_reference_recall_at_5_mean

## Framing (LOAD-BEARING per USER 2026-07-02 + Fix#28 discipline 2026-07-02)

Direct test of Skunkworks' MM_TENTATIVE_SYNTHESIS
`COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS` expansion
criterion.  Equal-alpha composition of asymmetric-strength streams (VWFA 0.24
weak + PPMI 0.34 strong) SYSTEMATICALLY underperformed best-single by 0.007 r@5
across 3 seeds (per-seed diffs [0.00, -0.01, -0.01]).  The proposed fix is
ADAPTIVE-alpha via held-out grid search: given the strong+weak asymmetry, the
grid should snap alpha near 0 (PPMI-dominant) rather than the equal-weight
0.5/0.5 that dilutes the strong stream.

**Mechanism-claim scope (LOAD-BEARING):** SUPERVISED HELD-OUT-SYNONYM RETRIEVAL
on substrate-ingested WordNet symbolic content (kind=lexicon, pos in {n,v,a,r};
N=100 top-freq atoms at smoke).  This cell tests the composition-dilution
lemma expansion criterion.  A PASS does NOT constitute:
- "PPMI-alone first substrate-native win" — this is V2-A REDISCOVERY territory,
  not novel (PPMI-alone was already the best single spoke per prior).
- "substrate understands English" — substrate KNOWS ALMOST NOTHING.
- A capability breakthrough — the substrate is not learning; only the mechanism
  composition strategy is being validated.

A PASS validates: brain-analog late-combine composition needs ADAPTIVE weighting
when parallel streams are asymmetric-strength.  A FAIL provides STRONGER
structural finding: score-level late-combine is fundamentally lossy for these
two spokes; not a rescue-required situation.

**V2-A precedent (SMOKE-TO-FULL discriminator narrowing):** V2-A smoke lifted
+0.06 (0.34 -> 0.40); FULL landed at +0.012 (0.372 vs 0.360).  If adaptive-alpha
recovers or lifts at smoke, expect discriminator to narrow at scale; do NOT
over-frame smoke lift as guaranteed FULL result.

## Task

Same as v3 EQUAL-alpha smoke for direct comparability:
- Corpus: WordNet lexicon partition (top-freq atoms with definition + >=3 synonyms).
- Per atom: fit(training_sentences=[definition, syn0, syn1, "related to <hypernym>"], concept_label=atom_idx).
- Query: last held-out synonym per atom = 100 queries at smoke.
- N=100 smoke atoms, seeds [11, 17, 23], n_dim=2048.  Prior EQUAL-alpha SMOKE
  regime BIT-IDENTICAL for regression arms.

## Held-out discipline (LOAD-BEARING)

**Adaptive-alpha grid-search MUST NOT touch the retrieval evaluation set.**

Per-seed query split (each seed uses independent permutation of 100 queries):
- `val_queries` — first 50 (fits alpha via `fit_weights_grid_2spoke`)
- `test_queries` — last 50 (evaluates adaptive-alpha r@1/r@5/r@10)

All 100 atom prototypes are in play at retrieval (val and test queries retrieve
against the same 100-atom index).  The val vs test split is on the QUERY axis
only.  Alpha grid: `(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)`.

**Regression-check arms** (VWFA, PPMI, v3-equal, trigram) are computed on ALL
100 queries — matches prior MEASURED values exactly.  This lets HP3/HP4/HP5/HP6
enforce direct-reproduction discipline while ARM_V3_ADAPTIVE_ALPHA reports
honest held-out generalization.

**In-cell no-leakage assertion:** the fit uses only val query cosine scores;
test queries are computed AFTER alpha is frozen.  Verified via
`_verify_no_leakage()` selftest (see cell) which asserts:
- `set(val_query_indices) & set(test_query_indices) == empty_set`
- `fit_weights_grid_2spoke` is invoked with `labels = val_labels`, NOT test_labels
- Adaptive-alpha eval uses `test_queries` only (not val queries)

## Formula selftest (LOAD-BEARING)

Verify that `fit_weights_grid_2spoke` behaves per Skunkworks expansion criterion:

1. **PPMI-dominant regime**: construct synthetic queries where PPMI stream is
   discriminative (queries close to PPMI protos) and VWFA is noise.  Assert
   fitted `alpha_star <= 0.2` (grid snaps toward PPMI-alone).  Then verify
   that adaptive-alpha top-1 retrieval on held-out val queries equals
   PPMI-alone (alpha=0) top-1 retrieval bit-identically.
2. **VWFA-dominant regime**: symmetric; VWFA stream is discriminative, PPMI is
   noise.  Assert fitted `alpha_star >= 0.7`.  Verify adaptive-alpha ~= VWFA-alone.
3. **Balanced regime**: both streams contribute equally.  Assert fitted
   `alpha_star in [0.3, 0.7]` (grid picks near-0.5 or any tied minimum).

This confirms the adaptive-alpha grid is functioning per the composition-dilution
lemma expansion criterion (Skunkworks MM_TENTATIVE_SYNTHESIS 2026-07-03).

Also invokes `hdlab.composed_encoder_v3._selftest()` (13 checks) +
`hdlab.late_combine._selftest()` (grid-search validation).

## Arms (5 x 3 seeds = 15 units)

| Arm | Weights (alpha, beta) | Metric domain | Purpose |
|---|---|---|---|
| ARM_V3_ADAPTIVE_ALPHA              | fitted per-seed         | test split (n=50) | LOAD-BEARING |
| ARM_V3_EQUAL_ALPHA                 | (0.5, 0.5)              | all queries (n=100) | regression (MUST reproduce 0.333) |
| ARM_PPMI_ALONE                     | (0.0, 1.0)              | all queries (n=100) | best-single ref (MUST reproduce 0.340) |
| ARM_VWFA_ALONE                     | (1.0, 0.0)              | all queries (n=100) | weak-stream ref (MUST reproduce 0.240) |
| ARM_CHAR_TRIGRAM_UNSUP_REFERENCE   | (n/a)                   | all queries (n=100) | baseline (MUST reproduce 0.280) |

Additional metrics for ARM_V3_ADAPTIVE_ALPHA:
- `fitted_alpha_per_seed`: list of 3 fitted alpha values (one per seed).
- `val_r1_per_seed`: r@1 on val split at fitted alpha (grid-search objective).
- `test_r5_per_seed`: r@5 on test split at fitted alpha (LOAD-BEARING metric).
- `full100_r5_per_seed`: r@5 on ALL 100 queries at fitted alpha (comparability with prior).

VWFA config: `scales=(1,2,3,4)`, `bind_position=True`, `max_pos=24`,
`seed_prefix=f"COMPOSED_V3_S{seed}"`, `sign_bundle=True` (BIT-IDENTICAL to prior).
PPMI config: `min_term_freq=2`, `smoothing=0.75`, `k_sparsity=0.02`,
`seed=int(seed)` (BIT-IDENTICAL to prior).
n_dim=2048 across all arms.

## HP / HF bands (recall@5, adaptive on test split, regression on all-100)

Director-specified bands (LOAD-BEARING on `ARM_V3_ADAPTIVE_ALPHA`):

### HP (all must clear for HARD_PASS):
- **HP1** (adaptive-alpha recovers OR beats best-single):
  `ARM_V3_ADAPTIVE_ALPHA test_r5 >= 0.35`.  Scope: `ARM_V3_ADAPTIVE_ALPHA`.
- **HP2** (adaptive-alpha at least matches best-single MINUS tiny epsilon on val→test transfer):
  `ARM_V3_ADAPTIVE_ALPHA test_r5 >= max(VWFA_ALONE, PPMI_ALONE)_full - 0.01`.  Scope: `ARM_V3_ADAPTIVE_ALPHA`.
- **HP3** (equal-alpha regression): `ARM_V3_EQUAL_ALPHA r@5` within +/-0.02 of prior 0.333.  Scope: `ARM_V3_EQUAL_ALPHA`.
- **HP4** (PPMI regression): `ARM_PPMI_ALONE r@5` within +/-0.02 of prior 0.340.  Scope: `ARM_PPMI_ALONE`.
- **HP5** (VWFA regression): `ARM_VWFA_ALONE r@5` within +/-0.02 of prior 0.240.  Scope: `ARM_VWFA_ALONE`.
- **HP6** (trigram regression): `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE r@5` within +/-0.02 of prior 0.280.  Scope: `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE`.
- **HP7** (no leakage): val queries and test queries disjoint per seed; alpha
  fit only on val; test eval only on test.  Scope: `ARM_V3_ADAPTIVE_ALPHA`.
- **HP8** (arms differ): all 5 arm top-k index stacks hash-distinct (META_RULE_AF).  Scope: all arms.

### HF (any triggers HARD_FAIL):
- **HF1** (adaptive-alpha strictly fails to recover):
  `ARM_V3_ADAPTIVE_ALPHA test_r5 < max(VWFA_ALONE, PPMI_ALONE)_full - 0.01`.
  STRONGER structural finding per Skunkworks: score-level late-combine is
  fundamentally lossy for these two spokes at this regime.
- **HF2** (regression broken): any of HP3/HP4/HP5/HP6 outside +/-0.02 tolerance
  from prior MEASURED.  Reproduction discipline breach.
- **HF3** (arms bit-identical): any two arm top-k index stacks hash-collide.
- **HF4** (leakage detected): val/test overlap OR alpha fit on test labels OR
  test eval on val queries.  Cell-design bug.

### MIDDLE_BAND
- Adaptive-alpha recovers (>= best_single - 0.01) but does NOT lift above 0.35:
  `test_r5 in [max(VWFA, PPMI)_full - 0.01, 0.35)`.
  Interpretation: adaptive-alpha grid snapped near 0 (PPMI-dominant) so it
  RECOVERS best-single but doesn't earn composition lift.  This confirms the
  composition-dilution lemma expansion criterion at 1-regime; needs 1 more
  regime for CG_META promotion per Skunkworks expansion criterion.

## Cardinality

- Smoke: 3 seeds x 5 arms = **15 units** expected.  `cardinality_ok = (landed_units == 15)`.
- (No FULL band declared in this prereg; Director decides FULL post-smoke.)

## HP_SCOPE mapping

```json
{
  "HP1": ["ARM_V3_ADAPTIVE_ALPHA"],
  "HP2": ["ARM_V3_ADAPTIVE_ALPHA"],
  "HP3": ["ARM_V3_EQUAL_ALPHA"],
  "HP4": ["ARM_PPMI_ALONE"],
  "HP5": ["ARM_VWFA_ALONE"],
  "HP6": ["ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"],
  "HP7": ["ARM_V3_ADAPTIVE_ALPHA"],
  "HP8": ["ARM_V3_ADAPTIVE_ALPHA", "ARM_V3_EQUAL_ALPHA", "ARM_PPMI_ALONE",
          "ARM_VWFA_ALONE", "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"]
}
```

## SCHEMA-VET fields

```yaml
cardinality_ok: <computed at runtime; 15 expected>
arms_differ_verified: <computed at runtime; True required>
final_metrics_atomicity: tmp_replace
progress_logging: print_flush_true
storage_strategy: sharded_per_atom_prototype_hds_composed_v3
compute_arch: sequential_cpu_numpy
cell_chunked: false                        # 3-seed single-cell; per-seed wall < 40s at smoke
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns

# Feasibility / calibration
crlb_n/a: "supervised retrieval; chance floor = 5/100 = 0.05 at r@5; discriminator = adaptive-vs-best-single gap not absolute-vs-CRLB"
discriminator_reachability: true            # adaptive-alpha only needs to snap alpha to 0 (already-observed grid behavior in late_combine._selftest); reachability trivial
baseline_in_band: <computed at runtime>     # 0.05 < TRIGRAM_ref < 0.80 required
calibration_check: default_ok_for_this_regime
baseline_in_band_lo: 0.05
baseline_in_band_hi: 0.80

# Sec 15 Test-design gates
sweep_alignment_verdict: N/A                # no swept axis
discriminating_fraction: 1.0                # single regime; regression targets all in [0.20, 0.35]; discriminator target 0.34-0.40
composition_edges:
  - from: VWFAEncoder
    to: ComposedEncoderV3.retrieve_topk
    A_natural_output_shape: "[n_dim] float32 bipolar-sign-bundled HD"
    B_natural_input_shape: "[n_dim] arbitrary HD -> L2-normalized then cosine-scored"
    verdict: SHAPE_MATCH
  - from: PPMISparseEncoder
    to: ComposedEncoderV3.retrieve_topk
    A_natural_output_shape: "[n_dim] float32 SVD-reduced dense HD"
    B_natural_input_shape: "[n_dim] arbitrary HD -> L2-normalized then cosine-scored"
    verdict: SHAPE_MATCH
  - from: per-query VWFA+PPMI cosine tables
    to: fit_weights_grid_2spoke
    A_natural_output_shape: "list of [n_dim] HDs per query; [n_atoms, n_dim] proto tables"
    B_natural_input_shape: "list of query HDs + [n_atoms, n_dim] protos + labels [n_val] int"
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: ARM_V3_EQUAL_ALPHA
    primitive: ComposedEncoderV3 alpha=beta=0.5 (score-level late-combine)
    cited_prior_atom: data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json
    cited_prior_metric: 0.333   # MEASURED@aggregate.arm_v3_composed_equal_alpha_recall_at_5_mean
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.02
    if_outside_tolerance: HARD_FAIL_HF2_REGRESSION_BROKEN
    regime_extension_audit: SHAPE_MATCH   # bit-identical corpus + hyperparams
  - arm: ARM_PPMI_ALONE
    primitive: ComposedEncoderV3 alpha=0,beta=1 (formula identity to pure PPMI)
    cited_prior_atom: data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json
    cited_prior_metric: 0.340
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.02
    if_outside_tolerance: HARD_FAIL_HF2
    regime_extension_audit: SHAPE_MATCH
  - arm: ARM_VWFA_ALONE
    primitive: ComposedEncoderV3 alpha=1,beta=0 (formula identity to pure VWFA)
    cited_prior_atom: data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json
    cited_prior_metric: 0.240
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.02
    if_outside_tolerance: HARD_FAIL_HF2
    regime_extension_audit: SHAPE_MATCH
  - arm: ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
    primitive: CharTrigramEncoder + cosine argmax
    cited_prior_atom: data/exp_substrate_composed_encoder_v3_smoke_2026_07_03_smoke/metrics.json
    cited_prior_metric: 0.280
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.02
    if_outside_tolerance: HARD_FAIL_HF2
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - fr: "Grid-search alpha on held-out val queries with retrieval-r@1 objective"
    primitive: hdlab.late_combine.fit_weights_grid_2spoke
  - fr: "Evaluate adaptive-alpha retrieval on held-out test split (no leakage)"
    primitive: ComposedEncoderV3.set_weights + retrieve_topk on test queries only
  - fr: "Snap alpha to 0 when one spoke dominates the other (adaptive discriminator)"
    primitive: fit_weights_grid_2spoke (verified in _selftest ortho-noise + sem-discriminative)
  - fr: "Recover PPMI-alone performance when PPMI is best single spoke"
    primitive: formula identity alpha=0,beta=1 == pure PPMI argmax (bit-identical top-k)
  - fr: "Preserve equal-alpha regression check (BIT-IDENTICAL to prior smoke)"
    primitive: ARM_V3_EQUAL_ALPHA arm re-runs with (0.5, 0.5) on all 100 queries
```

## Meta-rules touched
- **META_RULE_AF** (arms differ) — 5 arm top-k stack hashes distinct at smoke.
- **META_RULE_AG** (baseline in band) — TRIGRAM reference 0.05 < r5 < 0.80.
- **META_RULE_AH** (atomic final metrics) — tmp + os.replace.
- **META_RULE_K** (discriminator fires) — adaptive-alpha grid must SNAP (not stay flat at 0.5) OR HP1 is met.
- **META_RULE_L** (strict above floor) — HP1 uses 0.35 (>= best_single + 0.01 above 0.340).
- **META_RULE_M** (calibration default) — reuses v3 defaults; MEASURED baseline in-band at v3 EQUAL-alpha smoke.
- **META_RULE_H** (cardinality) — 15 units enforced.
- **META_RULE_AC** (hypothesized vs measured) — all quoted numbers tagged MEASURED@ / THEORETICAL@ / HYPOTHESIZED@.
- **Rule 16** (run_mode verification) — cell metrics include `run_mode` field.
- **Section 15D** (positive-control reproduce) — 4 regression arms enforce +/-0.02 tolerance.
- **Section 15E** (functional decomposition) — 5 functional requirements mapped to primitives.

## Compute architecture

- Class: **(b) sequential-CPU with justification** — 100-atom retrieval + 11-point grid search over 50 val queries; per-seed wall ~30-40s at smoke; per-query cosine-argmax already NumPy-matmul-vectorized; no GPU speedup at N=100.
- Storage strategy: **sharded** per-atom prototype HDs (each atom its own [n_dim] row) for both VWFA and PPMI streams.  Composition depth L=1 (no chain retrieval).
- Progress logging: `print_flush_true` + line-buffered stdout at cell entry.

## Dispatch plan

1. Author + selftest cell (this pre-reg's cell) — LOCAL smoke ONLY per USER-locked 2026-07-01 "SMOKE only local_cpu".
2. Report per-arm r@5 + per-seed fitted alpha + HOLD status.  Director decides FULL post-smoke.
3. HOLD before FULL dispatch — no autonomous FULL routing from this cell.

## Estimated wall (smoke)

- Load corpus: 1-2s.
- Per seed: 3 encoder fits (~3-5s) + 5 arm evals + 11-point grid (~1s incremental) = ~30-40s/seed.
- Total smoke: ~100-130s for 3 seeds.

Timeout allocated in queue_add: **240s** (2x margin).

## Non-negotiable disciplines
- Never `git add -A` (stage specific files).
- ASCII-only in cell (verified).
- All numbers in this prereg tagged with MEASURED@ / THEORETICAL@ / HYPOTHESIZED@.
- Substrate KNOWS ALMOST NOTHING — HP framing is MECHANISM-COMPOSITION FIX on SUPERVISED regime; not "substrate understands English."
- Commit prereg + cell before local dispatch.
- Do NOT frame PASS as "capability breakthrough" or "first substrate-native win" — this is V2-A REDISCOVERY if adaptive-alpha snaps to PPMI-alone.
