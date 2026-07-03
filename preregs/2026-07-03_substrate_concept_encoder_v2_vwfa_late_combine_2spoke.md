# Pre-registration: substrate_concept_encoder_v2_vwfa_late_combine_2spoke_2026_07_03

**Author:** hdi_exp_dev
**Date:** 2026-07-03
**Cell:** `experiments/exp_substrate_concept_encoder_v2_vwfa_late_combine_2spoke_2026-07-03.py`
**Design note:** `notes/research_brain_reading_architecture_emulation_v2_prescription_substrate_content_HF_2026-07-02.md`
**Prior baseline (rescue target):** `data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json` (verdict = HARD_FAIL / HF2)

## Framing (LOAD-BEARING per USER)

Tests v2 concept-encoder architecture (VWFA-analog multi-scale orthographic
encoder + late-combine composition with existing sparse-competitive-Hebbian
ATL-analog).  This is brain-analog COMPOSITION via LATE COMBINE (N400-window
integration), not sequential cascade.

**Mechanism-claim scope:** SUPERVISED HELD-OUT-SYNONYM RETRIEVAL on
substrate-ingested WordNet content (kind=lexicon, pos in {n,v,a,r}, N=100
top-freq atoms at smoke, N=500 at full).  HP earned here does NOT grant
"substrate reads text" or "substrate knows language broadly"; grants
"v2 architecture rescues transfer failure on substrate's known symbolic
content at this regime".

References (LOAD-BEARING):
- `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`
- `project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02.md`
- `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`

## Task

Same as v1 baseline:
- Corpus: WordNet lexicon partition (top-freq atoms with definition + >=3 synonyms).
- Per atom: fit(training_sentences=[definition, syn0, syn1, "related to <hypernym>"],
              concept_label=atom_idx).
- Query: last held-out synonym.
- Metric: recall@{1,5,10} over top-cosine argmax from a per-atom prototype table.

New in v2: 50%-atom queries reserved as a WEIGHT-FIT split; ARM_V2_LATE_COMBINE
fits alpha via grid-search on the fit-split then reports on the eval-split.
All 5 arms are evaluated on the SAME eval-split for apples-to-apples.

## Arms

| Arm | Weights | Query encoder | Prototypes |
|---|---|---|---|
| ARM_V2_VWFA_ALONE           | alpha=1, gamma=0     | VWFAEncoder                     | VWFA table                   |
| ARM_V2_SEM_ALONE            | alpha=0, gamma=1     | ConceptEncoder surface encoder  | concept_hds (sparse-CH)      |
| ARM_V2_LATE_COMBINE         | alpha=fit, gamma=1-alpha | both VWFA + sem query HDs   | score-level late-combine     |
| ARM_V2_LATE_COMBINE_EQUAL   | alpha=0.5, gamma=0.5 | both VWFA + sem query HDs      | score-level late-combine     |
| ARM_CHAR_TRIGRAM_UNSUP_REFERENCE | -            | CharTrigramEncoder              | trigram bag table            |

VWFA config: `scales=(1,2,3,4)`, `bind_position=True`, `max_pos=24`,
`seed_prefix=f"VWFA_S{seed}"`, `sign_bundle=True`.  Same n_dim=2048 as v1.

## HP / HF bands (recall@5 unless noted)

### HP (all 5 must clear for HARD_PASS):
- **HP1** (backward-compat sem-only): `ARM_V2_SEM_ALONE recall@5` within +-0.02 of prior v1 baseline (0.16).  Scope: `ARM_V2_SEM_ALONE` only.
- **HP2** (VWFA correctness): `ARM_V2_VWFA_ALONE recall@5` within +-0.03 of `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE recall@5` (VWFA-analog subsumes char-trigram bag).  Scope: `ARM_V2_VWFA_ALONE` only.
- **HP3** (rescue): `ARM_V2_LATE_COMBINE recall@5 >= ARM_CHAR_TRIGRAM_UNSUP_REFERENCE recall@5 + 0.05` (v2 strictly beats bag).  Scope: `ARM_V2_LATE_COMBINE` only.
- **HP4** (composition useful): `ARM_V2_LATE_COMBINE recall@5 >= max(VWFA_ALONE, SEM_ALONE) recall@5 + 0.03` (composition earns complexity).  Scope: `ARM_V2_LATE_COMBINE` only.
- **HP5** (arms differ): all 5 arm HD-table hashes distinct.  Scope: all arms.

### HF (any triggers HARD_FAIL):
- **HF1** (VWFA broken): `ARM_V2_VWFA_ALONE recall@5 < 0.20` (VWFA implementation bug; not reproducing bag-of-trigrams baseline).
- **HF2** (late-combine no rescue): `ARM_V2_LATE_COMBINE < max(VWFA_ALONE, SEM_ALONE)` (composition HURTS).
- **HF3** (sem-only regression): `ARM_V2_SEM_ALONE recall@5` outside [0.14, 0.18] (backward-compat broken).
- **HF4** (arms bit-identical): any two arm HD-tables hash-collide.

### MIDDLE_BAND
Any subset of HP1-HP5 met that is NOT all-5.  Specifically ties/marginal-lifts
(< HP3/HP4 gaps) indicate mechanism has some signal but not decisive.  P2
(add morph_decomp + concept_encoder_v2 3-spoke assembly) becomes next step.

## Cardinality

- Smoke: 3 seeds × 5 arms = **15 units** expected.  `cardinality_ok = (landed_units == 15)`.
- Full: 3 seeds × 5 arms = **15 units** expected.

## HP_SCOPE mapping

```json
{
  "HP1": ["ARM_V2_SEM_ALONE"],
  "HP2": ["ARM_V2_VWFA_ALONE"],
  "HP3": ["ARM_V2_LATE_COMBINE"],
  "HP4": ["ARM_V2_LATE_COMBINE"],
  "HP5": ["ARM_V2_VWFA_ALONE", "ARM_V2_SEM_ALONE", "ARM_V2_LATE_COMBINE",
          "ARM_V2_LATE_COMBINE_EQUAL", "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"]
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
cell_chunked: false  # single-cell 3-seeds (small task; per-seed wall <30s at smoke)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns

# Feasibility / calibration
crlb_n/a: "supervised retrieval; chance floor = k/N = 5/100 = 0.05 at smoke; discriminator = arm-vs-reference gap, not absolute-vs-CRLB"
discriminator_reachability: true  # HP3 gap 0.05 is empirically observed as achievable in char-positional (0.21) vs concept-encoder (0.16) v1 gap; a further +0.05 above trigram-bag is testable
baseline_in_band: <computed at runtime; 0.05 < trigram_ref < 0.80 required>
calibration_check: default_ok_for_this_regime  # v1 used same k_sparsity=0.02 max_pos=24 n_dim=2048 and produced measurable non-saturated numbers 0.16/0.21/0.28
baseline_in_band_lo: 0.05
baseline_in_band_hi: 0.80

# §15 Test-design gates
sweep_alignment_verdict: N/A  # no swept axis; 5 arms x 3 seeds fixed
discriminating_fraction: 1.0  # single regime, all in [0.05, 0.80] discriminating band per v1 prior
composition_edges:
  - from: VWFAEncoder
    to: LateCombine
    A_natural_output_shape: "[n_dim] float32 sign-bundled bipolar HD"
    B_natural_input_shape: "[n_dim] arbitrary HD (LateCombine L2-normalizes internally)"
    verdict: SHAPE_MATCH
  - from: ConceptEncoder._surface_encoder
    to: LateCombine
    A_natural_output_shape: "[n_dim] float32 bipolar HD"
    B_natural_input_shape: "[n_dim] arbitrary HD"
    verdict: SHAPE_MATCH
positive_control_arms:
  - arm: ARM_V2_SEM_ALONE
    primitive: ConceptEncoder (sparse-competitive-Hebbian)
    cited_prior_atom: "data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json"
    cited_prior_metric: 0.16  # MEASURED@aggregate.arm_concept_encoder_recall_at_5_mean
    cited_prior_regime: {N: 100, n_dim: 2048, k_sparsity: 0.02, seeds: [11,17,23]}
    test_regime: {N: 100, n_dim: 2048, k_sparsity: 0.02, seeds: [11,17,23]}
    tolerance: 0.02
    if_outside_tolerance: HARD_FAIL_HF3
    regime_extension_audit: SHAPE_MATCH
  - arm: ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
    primitive: CharTrigramEncoder (bag-of-trigrams)
    cited_prior_atom: "data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json"
    cited_prior_metric: 0.28  # MEASURED@aggregate.arm_char_trigram_recall_at_5_mean
    cited_prior_regime: {N: 100, n_dim: 2048, seeds: [11,17,23]}
    test_regime: {N: 50, n_dim: 2048, seeds: [11,17,23]}  # 50 due to eval-split; expect drift within ~0.05 from small-N variance
    tolerance: 0.10  # eval-split halves N, so tolerance is looser than sem HP1 (0.02)
    if_outside_tolerance: HARD_FAIL_TRIGRAM_REPRODUCTION_BROKEN (flags eval-split anomaly)
    regime_extension_audit: SHAPE_DRIFT_documented (N=50 eval-split vs N=100 full; expected +-0.05 small-sample variance)
functional_requirements:
  - fr: "Retrieve correct concept atom given held-out synonym query"
    primitive: ConceptEncoder for semantic; VWFAEncoder for orthographic; LateCombine for parallel-stream integration
  - fr: "Backward compatibility with v1 sem-only baseline"
    primitive: LateCombine(alpha=0, gamma=1) recovers unit-normalized v_sem
  - fr: "Surface-orthographic signal (char n-grams) accessible for composition"
    primitive: VWFAEncoder multi-scale (1,2,3,4) with HRR position-bind
  - fr: "Weight-fitting on held-out validation without over-fit"
    primitive: fit_weights_grid_2spoke coarse 11-point grid on 50% fit-split; eval on other 50%
```

## Meta-rules touched
- **META_RULE_AF** (arms differ) -- 5 arm hashes distinct at smoke.
- **META_RULE_AG** (baseline in band) -- trigram reference 0.05 < r5 < 0.80.
- **META_RULE_AH** (atomic final metrics) -- tmp + os.replace.
- **META_RULE_K** (discriminator fires) -- late_combine - max_spoke >= 0.03 OR late_combine - trigram >= 0.05.
- **META_RULE_L** (strict above floor) -- HP3/HP4 use strict `>=` with defined gaps.
- **META_RULE_M** (calibration default) -- reuses v1 defaults (k_sparsity=0.02 max_pos=24 n_dim=2048); MEASURED baseline_in_band at v1 verified in-band.
- **META_RULE_H** (cardinality) -- 15 units enforced.
- **META_RULE_AC** (hypothesized vs measured) -- all quoted numbers tagged in cell + this prereg.
- **Rule 16** (run_mode verification) -- cell metrics include `run_mode` field; runner-facing verify hook can check.

## Compute architecture

- Class: **(b) sequential-CPU** justified.
- Justification: 100-atom retrieval task; per-seed wall < 30s at smoke.  Bulk of compute is per-query cosine-argmax over an N-row table; already vectorized via `p @ q` NumPy matmul; no GPU speedup at this scale.  Full at N=500 est. <5min/seed x 3 seeds = ~15min total; no GPU batching payoff.
- Storage strategy: **sharded** per-atom prototype HDs (each atom its own [n_dim] row).  Composition depth L=1 (no chain retrieval).  Sharded is default for compositional cells; here composition happens at query-scoring time (score-level late-combine) not at storage.

## Dispatch plan

1. Author + selftest PASS (this cycle).
2. Local smoke on local_cpu (N=100 atoms, 3 seeds, 5 arms).
3. Report smoke results + HP verdict for Director/USER review.
4. HOLD before FULL dispatch -- smoke result determines whether P1 rescues (HP) or we need P2 (morph_decomp + concept_encoder_v2 3-spoke).

## Estimated wall (smoke)

- Load corpus: 1-2s.
- Per seed: build 3 prototype tables (~1-3s each) + fit alpha (~5-10s at 11-point grid over 50 queries) + eval 5 arms (~2s each) = ~30s/seed.
- Total smoke: ~90s for 3 seeds.

Timeout allocated in queue_add: **180s** (2x margin).
