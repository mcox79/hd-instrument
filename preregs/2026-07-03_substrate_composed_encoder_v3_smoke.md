# Pre-registration: substrate_composed_encoder_v3_smoke_2026_07_03

**Author:** hdi_exp_dev
**Date:** 2026-07-03
**Cell:** `experiments/exp_substrate_composed_encoder_v3_smoke_2026-07-03.py`
**Module:** `hdlab/composed_encoder_v3.py` (13 selftests PASS)
**Related preregs:**
- `preregs/2026-07-03_substrate_concept_encoder_v2_vwfa_late_combine_2spoke.md` (VWFA + sparse-CH ATL late-combine; different sem stream)
- `preregs/2026-07-03_substrate_concept_encoder_v2_A_ppmi_svd_sparse.md` (PPMI/SVD alone)
- `preregs/2026-07-03_substrate_concept_encoder_component_C_modern_hopfield_readout.md` (Component C smoke HARD_FAIL 2026-07-03)

**Prior MEASURED baselines (all @ `data/exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03_smoke/metrics.json` and `data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json`):**
- ARM_V1_CONCEPT_ENCODER_COSINE r@5 = 0.160  MEASURED@component_C_smoke:aggregate.arm_v1_concept_encoder_cosine_recall_at_5_mean
- ARM_CHAR_TRIGRAM_UNSUP_REFERENCE r@5 = 0.280  MEASURED@same:aggregate.arm_char_trigram_unsup_reference_recall_at_5_mean
- Component C HOPFIELD r@5 = 0.050 (worse than random)  MEASURED@same:aggregate.arm_v1_concept_encoder_modern_hopfield_recall_at_5_mean

## Framing (LOAD-BEARING per USER 2026-07-02)

Tests brain-analog COMPOSITION of parallel-stream encoders (VWFA + PPMI/SVD)
late-combined via score-level cosine weighting.  Skunkworks + 4/5 drills
recommended SKIP Component C (modern-Hopfield readout HF'd 2026-07-03,
`4cd1d30ba`); real load-bearing lever is COMPOSITION.

**Mechanism-claim scope (LOAD-BEARING):** SUPERVISED HELD-OUT-SYNONYM
RETRIEVAL on substrate-ingested WordNet symbolic content (kind=lexicon, pos in
{n,v,a,r}; N=100 top-freq atoms at smoke).  HP earned here does NOT grant
"substrate understands English" or "substrate reads text broadly"; grants
"brain-analog VWFA+ATL composition at score-level late-combine beats the
individual streams on substrate's known symbolic content at this regime."
This is a MECHANISM-COMPOSITION CG on a SUPERVISED synthetic-corpus regime,
per `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`.

Substrate KNOWS ALMOST NOTHING per USER-locked 2026-07-02.  All labels are
supervised at fit time.

## Task

Same as Component C smoke baseline for direct comparison:
- Corpus: WordNet lexicon partition (top-freq atoms with definition + >=3 synonyms).
- Per atom: fit(training_sentences=[definition, syn0, syn1, "related to <hypernym>"], concept_label=atom_idx).
- Query: last held-out synonym.
- Metric: recall@{1,5,10}.
- N=100 smoke atoms, seeds [11, 17, 23], n_dim=2048.

## Arms (5 x 3 seeds = 15 units)

| Arm | Weights (alpha, beta) | Query streams | Prototypes | Purpose |
|---|---|---|---|---|
| ARM_V3_COMPOSED_EQUAL_ALPHA        | (0.5, 0.5)  | VWFA + PPMI | v3 protos    | LOAD-BEARING (target r@5 >= 0.32) |
| ARM_VWFA_ALONE                     | (1.0, 0.0)  | VWFA        | v3 vwfa      | positive control; identity to pure VWFA |
| ARM_PPMI_ALONE                     | (0.0, 1.0)  | PPMI        | v3 ppmi      | positive control; identity to pure PPMI |
| ARM_V1_CONCEPT_ENCODER_COSINE      | (n/a)       | ConceptEncoder surface | v1 concept_hds | regression check on v1 baseline (0.16 prior) |
| ARM_CHAR_TRIGRAM_UNSUP_REFERENCE   | (n/a)       | CharTrigramEncoder | trigram-bag proto | reference target to beat (0.28 prior) |

VWFA config: `scales=(1,2,3,4)`, `bind_position=True`, `max_pos=24`,
`seed_prefix=f"COMPOSED_V3_S{seed}"`, `sign_bundle=True`.  
PPMI config: `min_term_freq=2`, `smoothing=0.75`, `k_sparsity=0.02` (dense
encode path is used for retrieval).  
n_dim=2048 across all arms.

Component C (modern-Hopfield readout) is INTENTIONALLY EXCLUDED per 2026-07-03
Skunkworks recommendation.

## HP / HF bands (recall@5)

### HP (all must clear for HARD_PASS):
- **HP1** (composition lift): `ARM_V3_COMPOSED_EQUAL_ALPHA r@5 >= max(VWFA_ALONE, PPMI_ALONE) + 0.03` — composition earns complexity vs best single spoke.  Scope: `ARM_V3_COMPOSED_EQUAL_ALPHA`.
- **HP2** (beat bag): `ARM_V3_COMPOSED_EQUAL_ALPHA r@5 >= ARM_CHAR_TRIGRAM_UNSUP_REFERENCE + 0.04` — v3 strictly beats trigram bag by margin above floor+5% band-width (0.28 + 0.04 = 0.32; META_RULE_L).  Scope: `ARM_V3_COMPOSED_EQUAL_ALPHA`.
- **HP3** (v1 backward-compat regression check): `ARM_V1_CONCEPT_ENCODER_COSINE r@5` within +/-0.03 of prior 0.16.  Scope: `ARM_V1_CONCEPT_ENCODER_COSINE`.
- **HP4** (trigram reference match): `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE r@5` within +/-0.03 of prior 0.28.  Scope: `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE`.
- **HP5** (arms differ): all 5 arm top-k index stacks hash-distinct (META_RULE_AF).  Scope: all arms.
- **HP6** (formula-identity in-cell verification): ARM_VWFA_ALONE r@5 exactly matches pure-VWFA-cosine-argmax r@5 AND ARM_PPMI_ALONE r@5 exactly matches pure-PPMI-cosine-argmax r@5.  Scope: `ARM_VWFA_ALONE`, `ARM_PPMI_ALONE`.

### HF (any triggers HARD_FAIL):
- **HF1** (composition hurts): `ARM_V3_COMPOSED_EQUAL_ALPHA r@5 < max(VWFA_ALONE, PPMI_ALONE)` — composition strictly HURTS single-spoke performance (mechanism design bug).
- **HF2** (still loses to bag): `ARM_V3_COMPOSED_EQUAL_ALPHA r@5 < ARM_CHAR_TRIGRAM_UNSUP_REFERENCE` — v3 composition BELOW trivial trigram bag (major reframe; skip C recommendation may be wrong OR VWFA+PPMI composition insufficient).
- **HF3** (arms bit-identical): any two arm top-k index stacks hash-collide.
- **HF4** (v1 baseline regression): `ARM_V1_CONCEPT_ENCODER_COSINE r@5` OUTSIDE [0.13, 0.19] — reproducibility broken.

### MIDDLE_BAND
Any subset of HP1-HP6 met that is NOT all-6.  Common outcomes:
- HP2+HP3+HP4+HP5+HP6 met, HP1 missed (composition ties best spoke, doesn't lift) — MIDDLE_BAND with note "composition_no_lift"
- HP1+HP3+HP4+HP5+HP6 met, HP2 missed (composition lifts but doesn't beat bag by 0.04 margin) — MIDDLE_BAND with note "beat_bag_margin_short"

## Cardinality

- Smoke: 3 seeds x 5 arms = **15 units** expected.  `cardinality_ok = (landed_units == 15)`.
- (No FULL band declared in this prereg; Director decides FULL post-smoke.)

## HP_SCOPE mapping

```json
{
  "HP1": ["ARM_V3_COMPOSED_EQUAL_ALPHA"],
  "HP2": ["ARM_V3_COMPOSED_EQUAL_ALPHA"],
  "HP3": ["ARM_V1_CONCEPT_ENCODER_COSINE"],
  "HP4": ["ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"],
  "HP5": ["ARM_V3_COMPOSED_EQUAL_ALPHA", "ARM_VWFA_ALONE", "ARM_PPMI_ALONE",
          "ARM_V1_CONCEPT_ENCODER_COSINE", "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"],
  "HP6": ["ARM_VWFA_ALONE", "ARM_PPMI_ALONE"]
}
```

## SCHEMA-VET fields

```yaml
cardinality_ok: <computed at runtime; 15 expected>
arms_differ_verified: <computed at runtime; True required>
final_metrics_atomicity: tmp_replace
progress_logging: print_flush_true
storage_strategy: sharded_per_atom_prototype_hds
compute_arch: sequential_cpu_numpy
cell_chunked: false                        # 3-seed single-cell; per-seed wall < 30s at smoke
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns

# Feasibility / calibration
crlb_n/a: "supervised retrieval; chance floor = k/N = 5/100 = 0.05 at smoke; discriminator = arm-vs-reference gap not absolute-vs-CRLB"
discriminator_reachability: true            # composition-lift HP1 gap 0.03 empirically observed in v2 vwfa+CH cell target (HP4 same gap)
baseline_in_band: <computed at runtime>     # 0.05 < TRIGRAM_ref < 0.80 required
calibration_check: default_ok_for_this_regime  # reuses v1 defaults (k_sparsity=0.02 max_pos=24 n_dim=2048) already MEASURED in-band at v1
baseline_in_band_lo: 0.05
baseline_in_band_hi: 0.80

# Sec 15 Test-design gates
sweep_alignment_verdict: N/A                # no swept axis; 5 arms x 3 seeds fixed
discriminating_fraction: 1.0                # single regime; TRIGRAM=0.28 and V1_COS=0.16 both in [0.05, 0.80]
composition_edges:
  - from: VWFAEncoder
    to: ComposedEncoderV3.retrieve_topk
    A_natural_output_shape: "[n_dim] float32 bipolar-sign-bundled HD"
    B_natural_input_shape: "[n_dim] arbitrary HD -> L2-normalized then cosine-scored"
    verdict: SHAPE_MATCH
  - from: PPMISparseEncoder
    to: ComposedEncoderV3.retrieve_topk
    A_natural_output_shape: "[n_dim] float32 SVD-reduced dense HD (zero-padded if effective < n_dim)"
    B_natural_input_shape: "[n_dim] arbitrary HD -> L2-normalized then cosine-scored"
    verdict: SHAPE_MATCH
  - from: score-level combine
    to: argmax topk
    A_natural_output_shape: "[n_concepts] float32 combined cosine scores"
    B_natural_input_shape: "[n_concepts] float32 scores; argmax returns top-k int64"
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: ARM_V1_CONCEPT_ENCODER_COSINE
    primitive: ConceptEncoder (sparse-competitive-Hebbian) + cosine argmax
    cited_prior_atom: "data/exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03_smoke/metrics.json"
    cited_prior_metric: 0.16   # MEASURED@aggregate.arm_v1_concept_encoder_cosine_recall_at_5_mean
    cited_prior_regime: {N: 100, n_dim: 2048, k_sparsity: 0.02, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, k_sparsity: 0.02, seeds: [11,17,23]}
    tolerance: 0.03
    if_outside_tolerance: HARD_FAIL_HF4
    regime_extension_audit: SHAPE_MATCH
  - arm: ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
    primitive: CharTrigramEncoder (bag-of-trigrams) + cosine argmax
    cited_prior_atom: "data/exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03_smoke/metrics.json"
    cited_prior_metric: 0.28   # MEASURED@aggregate.arm_char_trigram_unsup_reference_recall_at_5_mean
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime:        {N: 100, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.03
    if_outside_tolerance: HARD_FAIL_TRIGRAM_REPRODUCTION_BROKEN
    regime_extension_audit: SHAPE_MATCH
  - arm: ARM_VWFA_ALONE
    primitive: ComposedEncoderV3 alpha=1,beta=0 (formula identity to pure VWFA argmax)
    cited_prior_atom: hdlab/composed_encoder_v3.py::_selftest[5]
    cited_prior_metric: BIT-IDENTICAL top-k to pure-VWFA-cosine-argmax
    cited_prior_regime: {toy_corpus: 5_concept_synthetic, n_dim: 2048}
    test_regime:        {WordNet_subset: 100_atoms, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.0             # bit-identical top-k assertion
    if_outside_tolerance: HARD_FAIL_HP6_FORMULA_IDENTITY_BROKEN
    regime_extension_audit: SHAPE_MATCH   # score-scaling invariance holds at all regimes
  - arm: ARM_PPMI_ALONE
    primitive: ComposedEncoderV3 alpha=0,beta=1 (formula identity to pure PPMI argmax)
    cited_prior_atom: hdlab/composed_encoder_v3.py::_selftest[6]
    cited_prior_metric: BIT-IDENTICAL top-k to pure-PPMI-cosine-argmax
    cited_prior_regime: {toy_corpus: 5_concept_synthetic, n_dim: 2048}
    test_regime:        {WordNet_subset: 100_atoms, n_dim: 2048, seeds: [11,17,23]}
    tolerance: 0.0
    if_outside_tolerance: HARD_FAIL_HP6_FORMULA_IDENTITY_BROKEN
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - fr: "Retrieve correct concept atom given held-out synonym query"
    primitive: ComposedEncoderV3.retrieve_topk (score-level VWFA + PPMI late-combine)
  - fr: "Backward-compat identity: alpha=1,beta=0 recovers pure VWFA argmax"
    primitive: ComposedEncoderV3 (selftests 5 + in-cell HP6 verification)
  - fr: "Backward-compat identity: alpha=0,beta=1 recovers pure PPMI argmax"
    primitive: ComposedEncoderV3 (selftests 6 + in-cell HP6 verification)
  - fr: "Surface orthographic multi-scale signal"
    primitive: VWFAEncoder scales=(1,2,3,4) HRR-position-bound
  - fr: "Amodal semantic co-occurrence via SVD-reduced PPMI"
    primitive: PPMISparseEncoder (fit on labeled corpus)
  - fr: "Parallel-stream late-combine (N400 window analog)"
    primitive: ComposedEncoderV3 score-level cosine weighting
```

## Meta-rules touched
- **META_RULE_AF** (arms differ) — 5 arm top-k stack hashes distinct at smoke.
- **META_RULE_AG** (baseline in band) — TRIGRAM reference 0.05 < r5 < 0.80.
- **META_RULE_AH** (atomic final metrics) — tmp + os.replace.
- **META_RULE_K** (discriminator fires) — HP1 composition gap >= 0.03 above best spoke OR HP2 composition r@5 >= 0.32.
- **META_RULE_L** (strict above floor) — HP2 uses `+0.04` above trigram (floor 0.28 + 5% band-width where band-width defined as 0.04 on the ~[0.20, 1.00] scale).
- **META_RULE_M** (calibration default) — reuses v1 defaults; MEASURED baseline in-band at Component C smoke.
- **META_RULE_H** (cardinality) — 15 units enforced.
- **META_RULE_AC** (hypothesized vs measured) — all quoted numbers tagged MEASURED@ / THEORETICAL@ / HYPOTHESIZED@.
- **Rule 16** (run_mode verification) — cell metrics include `run_mode` field.

## Compute architecture

- Class: **(b) sequential-CPU with justification** — 100-atom retrieval task; per-seed wall < 30s at smoke; per-query cosine-argmax already NumPy-matmul-vectorized; no GPU speedup at N=100.
- Storage strategy: **sharded** per-atom prototype HDs (each atom its own [n_dim] row) for both VWFA and PPMI streams.  Composition depth L=1 (no chain retrieval).
- Progress logging: `print_flush_true` + line-buffered stdout at cell entry.

## Dispatch plan

1. Author `hdlab/composed_encoder_v3.py` (13 selftests PASS) — DONE.
2. Author + selftest smoke cell (this pre-reg's cell).
3. Local smoke on `local_cpu_queue` (SMOKE-ONLY per USER-locked 2026-07-01 "SMOKE only local_cpu").
4. Report per-arm r@5 + HOLD status.  Director decides FULL post-smoke.
5. HOLD before FULL dispatch — no autonomous FULL routing from this cell.

## Estimated wall (smoke)

- Load corpus: 1-2s.
- Per seed: build 3 prototype tables (~1-3s each) + eval 5 arms (~2s each) = ~15-30s/seed.
- Total smoke: ~60-90s for 3 seeds.

Timeout allocated in queue_add: **180s** (2x margin; smoke-timeout ceiling is 180s in queue_add.py without override).

## Non-negotiable disciplines
- Never `git add -A` (stage specific files).
- ASCII-only in cell + module (verified).
- All numbers in this prereg tagged with MEASURED@ / THEORETICAL@ / HYPOTHESIZED@.
- Substrate KNOWS ALMOST NOTHING — HP framing is MECHANISM-COMPOSITION on SUPERVISED regime; not "substrate understands English."
- Commit prereg + cell + module before dispatch (local dispatch does not require push).
