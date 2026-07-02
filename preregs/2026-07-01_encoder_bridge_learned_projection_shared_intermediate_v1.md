# Pre-registration: encoder_bridge_learned_projection_shared_intermediate_v1

**Date:** 2026-07-01
**Anchor:** encoder_bridge_learned_projection_shared_intermediate_v1
**Queue:** remote_cpu_queue
**N:** 8192, **Seeds:** 7, 13, 19
**M items bound per bundle:** 1000
**M train Procrustes pairs:** 1000

## Scientific question

Encoder cocktail v1 landed HF_PROVEN_NEGATIVE 3/3 seeds. Cross-encoder recall
= 0.004
(MEASURED@d:/AI/hd-instrument/data/exp_encoder_cocktail_composition_v1_seed_7
/metrics.json:per_arm_recall.ARM_FHRR_QUERY_SPARSE_KEYS) vs within-encoder
FHRR baseline = 0.352
(MEASURED@same:per_arm_recall.ARM_FHRR_ONLY). Structural bound established;
Skunkworks flagged revival criteria:
    (a) learned projection between encoder spaces
    (b) shared intermediate binding geometry
    (c) family-tag routing

Does ANY of (a)/(b)/(c) actually recover cross-encoder retrieval to a useful
level? Load-bearing for M3 architecture: bridge presence determines whether
substrate needs 1 unified encoder or can operate with multi-encoder mixing
plus bridge glue.

## Prior work check (substrate-KB concept query 2026-07-01)

Query: "Procrustes bridge FHRR sparse encoder cross-family projection"
- Top hit cosine=0.269: notes/research_drill_bridge_id_categorical_closure_3x
  (bridge-entity NER ranker; unrelated).
- Chunk at cosine=0.263:
  notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10
  Confirms KNOWN structural sparse-vs-FHRR conflict: "SPARSE CODING conflicts
  with FHRR algebra... requires either (a) a new algebra compatible with
  sparsity, or (b) a two-stage approach where sparse coding operates at
  codebook level but binding uses dense projections."
- No prior chain-grade evidence for a Procrustes-style empirical bridge test
  between FHRR and sparse encoders. NOVEL empirical validation of (a)/(b)/(c).

## Arms (5 total; EXPECTED_N_UNITS = 5)

### ARM_WITHIN_FHRR (positive control; sentinel)
Single-family FHRR bundle; FHRR key -> FHRR val. Should reproduce cocktail v1
ARM_FHRR_ONLY = 0.35 within tolerance.
HYPOTHESIZED@this-prereg: recall ~0.30-0.40 at N=8192 M=1000.
Sentinel gate: recall >= 0.20 (must fire; else verdict invalid).

### ARM_CTRL_NO_BRIDGE (negative control; sentinel)
Reproduces cocktail v1 cross-encoder setup: sparse-key substrate, FHRR-key
query, cross-family bind attempt.
Expected: near-chance recall matching cocktail v1's 0.004.
Sentinel gate: recall <= 0.10 (must NOT fire; else v1 not reproduced).

### ARM_LEARNED_PROJECTION (mechanism arm)
Train orthogonal rotation R via SVD Procrustes on 1000 paired
(FHRR_key_real, sparse_key) pairs at TRAIN indices (disjoint from TEST).
At TEST time: real-project FHRR test key, apply R -> bridged real[dim] in
sparse-space; bind against candidate SPARSE vals; cosine against sparse
bundle. If FHRR and sparse geometries are linearly related, R recovers signal.
CITED@Schoenemann 1966 (orthogonal Procrustes); Gower & Dijksterhuis 2004.

### ARM_SHARED_INTERMEDIATE (mechanism arm)
Both FHRR and sparse project to bipolar-N intermediate via sign(). Bind +
bundle + query all in intermediate space. Tests whether sign() preserves
enough discriminative geometry to bridge families. Directly implements the
"two-stage approach" from the substrate-KB chunk hit.

### ARM_FAMILY_TAG_ROUTING (cheat baseline)
Query is REBUILT as same-family sparse-tagged key deterministically (matches
substrate family). This reduces to within-sparse retrieval; provides upper
bound on "if we just abandon the FHRR encoder and use sparse, what do we
get?" It's a "cheat" (separates rather than bridges).

## Pre-registered verdict bands

Per envelope-fail-bands + META_RULE_L strict-above-floor:

**HARD-PASS:**
- HP_STRONG_BRIDGE: max(ARM_LEARNED_PROJECTION, ARM_SHARED_INTERMEDIATE)
  >= 0.62 (= 0.60 + 5% * (1.00 - 0.60)). Strong bridge near single-family
  baseline. CHAIN_GRADE if 3/3 seeds.
- HP_BRIDGE_RECOVERS: max(ARM_LEARNED_PROJECTION, ARM_SHARED_INTERMEDIATE)
  >= 0.315 (= 0.30 + 5% * (0.60 - 0.30)). Useful bridge exists.

**HARD-FAIL:**
- HF_BRIDGE_FAILS: ALL of ARM_LEARNED_PROJECTION, ARM_SHARED_INTERMEDIATE,
  ARM_FAMILY_TAG_ROUTING < 0.10 (rules out mechanism class; encoder-family
  bind is truly structural).
- HF_POSITIVE_SENTINEL_FAIL: ARM_WITHIN_FHRR < 0.20 (baseline broken).
- HF_NEGATIVE_SENTINEL_FAIL: ARM_CTRL_NO_BRIDGE > 0.10 (cocktail v1 not
  reproduced).

**MIDDLE_BAND:** max true bridge in [0.10, 0.315) OR partial signal.

**HP_SCOPE (per-arm gate applicability):**
- ARM_LEARNED_PROJECTION: HP_BRIDGE_RECOVERS, HP_STRONG_BRIDGE
- ARM_SHARED_INTERMEDIATE: HP_BRIDGE_RECOVERS, HP_STRONG_BRIDGE
- ARM_FAMILY_TAG_ROUTING: HP_BRIDGE_RECOVERS (but NOT strong; tag-routing
  is cheat baseline, not a true bridge)
- ARM_WITHIN_FHRR: sentinel_positive_control (must fire)
- ARM_CTRL_NO_BRIDGE: sentinel_negative_control (must NOT fire)

**CHAIN_GRADE gate:** HP_STRONG_BRIDGE fires cross-seed (3/3) on
LEARNED_PROJECTION OR SHARED_INTERMEDIATE.

## Calibration rationale

- **0.30 recovery floor:** matches "sanity floor" from task hand-off. Well
  above cocktail v1 cross-recall 0.004. Recovery to 0.30 (vs within-baseline
  ~0.35) means the bridge captures ~85% of within-encoder capacity.
- **0.60 strong-bridge threshold:** matches "strong" from task hand-off.
  ~1.7x the within-encoder baseline (0.35) is implausible; this threshold is
  aspirational and would require a bridge that INCREASES retrieval capacity,
  which is theoretically possible if the shared intermediate has higher
  effective dim than the natural FHRR real-projection.
- **0.10 structural floor:** cocktail v1 cross-recall was 0.004; a bridge
  arm below 0.10 has failed to lift signal meaningfully above chance
  (chance = 1/M = 1/1000 = 0.001).
- **5% strict-above-floor margin (META_RULE_L):** prevents band-hugging
  false HARD_PASS.

## CRLB / capacity-feasibility

- **Chance rate:** 1 / M = 1/1000 = 0.001 THEORETICAL@1/M-argmax-uniform.
- **HARD_PASS 0.30 reachability:** 0.30 >> 0.001; discriminator_reachability
  = True.
- **Within-encoder ceiling (from cocktail v1):** ARM_FHRR_ONLY = 0.352
  MEASURED@d:/AI/hd-instrument/data/exp_encoder_cocktail_composition_v1_seed_7
  /metrics.json:per_arm_recall.ARM_FHRR_ONLY. This is the practical ceiling
  for bridge arms in same regime.
- **HP_STRONG (0.60) reachability:** ABOVE within-encoder ceiling 0.352;
  bridge arm hitting 0.60 would imply the bridge produces MORE separable
  representations than the FHRR-alone bundle. This is only plausible if
  SHARED_INTERMEDIATE's bipolar-N space provides denoising via sign(). We
  keep the strict threshold as aspirational; realistic expected outcome is
  HP_BRIDGE_RECOVERS (0.315) at most.

## Cardinality (CARDINALITY_OK; META_RULE_H)

EXPECTED_N_UNITS = 5 arms per seed; cross-seed = 15 units total.
HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if any per-seed cardinality != 5.
Field: cardinality_ok: True.

## Discriminator-must-survive-scale check (USER 2026-06-26)

Approach (A): smoke runs at FULL-N (N=8192) with M reduced (M_SMOKE=512,
N_QUERY_SMOKE=96, M_TRAIN_PROCRUSTES_SMOKE=512). Since the mechanism is
retrieval-noise-limited (not scale-limited), smoke that fires the
discriminator will fire at full. If smoke ARM_WITHIN_FHRR saturates to 1.000
(unexpected), regime rebalance.

Expected at smoke:
- ARM_WITHIN_FHRR: ~0.40-0.60 (M=512 in N=8192 for FHRR is well below
  saturation; discriminator active but slightly stronger than full).
- ARM_CTRL_NO_BRIDGE: <=0.02 (near-chance; should reproduce cocktail v1
  behavior at reduced M).
- ARM_LEARNED_PROJECTION, ARM_SHARED_INTERMEDIATE: TBD (that's the science);
  smoke must show the arms don't crash and produce recall in [0, 1].
- ARM_FAMILY_TAG_ROUTING: near ARM_WITHIN_FHRR of the sparse-family baseline
  (~0.30-0.50); this is the cheat.

## META_RULE compliance summary

- META_RULE_AC (HYPOTHESIZED/MEASURED/THEORETICAL tags): applied throughout.
- META_RULE_AF (arms-must-differ): pre-flight distinctness gate (FHRR /
  sparse / binary_intermediate SHA-256 verification); per-arm implementations
  demonstrably differ (different families, different bind ops, different
  bundle types).
- META_RULE_AH (atomic metrics): tmp_replace via os.replace() (final_metrics
  _atomicity: "tmp_replace").
- META_RULE_H (cardinality_ok): EXPECTED_N_UNITS = 5 declared + verified.
- META_RULE_J (failure-class instrumentation): per-arm try/except catches
  specific classes (MemoryError, ValueError, AssertionError); no bare except.
- META_RULE_K (discriminator-fires gate): smoke selftest verifies within-arm
  recall > 0.70 AND ctrl-arm recall < 0.20 (baseline fires + ctrl fails).
- META_RULE_L (strict-above-floor): HARD_PASS thresholds strict + 5% margin.
- META_RULE_M (calibration_check): default_ok_for_this_regime (matches
  cocktail v1 regime).
- META_RULE_S (band-calibration regime check): argmax-noise floor at
  M=1000 is ~0.001; HP=0.30 well above.
- Discriminator-survives-scale: (A) smoke at FULL-N.

## Defensive error checking (§13 mandate)

- cell_chunked: True (3 separate seed cells; one seed per file).
- start_marker_written: True (_start_marker.json at main() entry).
- crash_diagnostic_present: True (_write_crash_metrics on Exception; except
  SystemExit/KeyboardInterrupt handled before broad Exception).
- heartbeat_present: False (cell wall <5 min; no heartbeat needed).
- defensive_error_checking: "passed_all_4_patterns" (marker + crash-diag +
  atomic metrics + failure-class per arm).

## Test-design gates (§15)

- **A) effective_vs_nominal_parameter_audit:** N/A (cell not sweeping
  parameters; testing 5 fixed arms).
- **B) bracket_includes_discriminating_band:** 3 bridge arms each
  discriminating between [0.001 chance, 0.352 ceiling]; discriminating_
  fraction = 1.00.
- **C) signal_shape_compatibility_audit:** all cross-family binds documented
  with real-projection adapter (fhrr complex[N/2] -> real[N] concat; sparse
  identity; sign() intermediate); composition_edges all SHAPE_MATCH_with_
  adapter.
- **D) reproduce_prior_chain_grade_result_as_positive_control:**
  ARM_WITHIN_FHRR reproduces cocktail v1 ARM_FHRR_ONLY = 0.352 at same
  regime (N=8192, M=1000; MEASURED tolerance 0.10). ARM_CTRL_NO_BRIDGE
  reproduces cocktail v1 ARM_FHRR_QUERY_SPARSE_KEYS = 0.004 (MEASURED
  tolerance 0.05).
- **E) functional_requirement_decomposition_present:**
  1. Encode cross-family similarity: LEARNED_PROJECTION via Procrustes.
  2. Provide encoder-neutral bind: SHARED_INTERMEDIATE via bipolar sign().
  3. Segregate encoder domains: FAMILY_TAG_ROUTING via tag-concat.
  4. Preserve within-family baseline: WITHIN_FHRR (positive control).
  5. Reproduce known negative: CTRL_NO_BRIDGE (negative control).

## Substantive if

- **HP_STRONG or HP_RECOVERS on LEARNED_PROJECTION:** M3 can use FHRR queries
  against sparse substrate via a trained rotation. Enables multi-encoder
  cortex plumbing with linear-algebraic glue.
- **HP_STRONG or HP_RECOVERS on SHARED_INTERMEDIATE:** M3 can use a canonical
  bipolar intermediate as the "shared vocabulary" between encoder families;
  all cross-family binding happens in intermediate. Enables multi-modal
  substrate.
- **HF_BRIDGE_FAILS on all 3:** M3 must commit to ONE encoder family per
  substrate instance. Multi-modality requires separate substrate silos with
  routing at the cortex layer, not at the substrate bind level.

## Cross-references

- experiments/_encoder_cocktail_composition_v1_core.py (parent negative;
  same 6-arm structural bound).
- experiments/_substrate_anchor4_encoder_family_phase_diagram_v4_core.py
  (5 encoders individually verified; encoder registry pattern).
- notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
  (substrate-KB chunk 45: known sparse/FHRR algebra conflict; "two-stage
  approach" cited as one resolution -> this cell's Arm B).
