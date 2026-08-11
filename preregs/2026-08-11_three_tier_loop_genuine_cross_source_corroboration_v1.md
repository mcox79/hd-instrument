# three_tier_loop_genuine_cross_source_corroboration_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: hdi_research/USER "tighten the three-tier proof to
the LITERAL 'combination of ALL sources' thesis by removing the one honest caveat in the
just-landed real-corpus cell (commit 73c54d094): its 6 encounters/gap were TEMPLATED-SYNTHETIC
repeats of the SAME fact, not genuinely distinct sources" (2026-08-11).

Prior-work check (`bash tools/substrate_query.sh "cross source corroboration accumulation multi
source knowledge combination gap coverage MadeOf bridge"`, cosine>0.30 threshold): top hits were
generic word-similarity matches (`combination` cos=0.3594, `corroboration` cos=0.3516,
`accumulation` cos=0.3438) plus one metrics-linked entity (`multisource_arena_combination_menu_v1`
cos=0.332, inspected -- an unrelated decision-model routing/fusion cell, not a prior gap-
corroboration measurement). None are a prior real-corpus cross-source-coverage measurement cell.
Genuinely novel work, not a rediscovery.

## Step 1: MEASURE (mandatory, reported regardless of Step 2's outcome)

For the 121 real MadeOf-bridge gaps (rebuilt byte-identically via
`experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1`'s own
`build_reading_facts`/`build_cskg_bridges`/`build_gap_set`, imported not re-derived), and the 62
of those that are ELIGIBLE for the per-cue REASON mechanism (rebuilt via
`experiments.exp_three_tier_loop_real_corpus_gap_stream_v1._eligible_targets`, imported not
re-derived -- MEASURED, matches the landed cell's own `n_eligible=62` exactly), compute per-gap
coverage across the 4 named sources:

1. **CSKG** (`data/cskg_foundation_v1/`): the `/r/MadeOf` edge that DEFINES the gap (trivially
   present for all 121, by construction) + any OTHER relation type between (via_material, whole)
   + any direct (process, whole) or (process, material) edge of any relation (single streaming
   pass over all 16 shards, 1,213,912 rows, ~3s).
2. **CauseNet-precision cache** (`data/bio_kb_cache/causenet/causenet-precision.jsonl.bz2`,
   197,806 causal pairs): literal (material,whole), (process,material), (process,whole) pairs,
   either direction (extends the landed cell's own `causenet_leak_check`, which only checked
   (process,whole) and found 0 -- this cell additionally checks the two sub-pair types).
3. **"reading-extracted process facts"** (`data/exp_bootstrap_dense_process_article_reading_
   fade_v6/`): MEASURED non-independence -- that cell's own `run()` imports the IDENTICAL
   extractor (`experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision.
   extract_facts_strict`) over the IDENTICAL corpus file
   (`data/corpora/process_articles_v1/process_articles.json`) as the gap-set's own S_READ leg --
   confirmed by direct source-file inspection (both facts verbatim-True). Any "coverage" from
   this cell's reading component would be CIRCULAR (same fact, not a second observation), so it
   is EXCLUDED and substituted with the genuinely-distinct source living in the SAME fade_v6
   dependency chain: `data/benchmark_trap_check/propara_process_physics_kb_v1.json` (loaded by
   `experiments.exp_propara_bridging_distilled_kb_endtoend_v1._load_kb`, which fade_v6 itself
   imports) -- a hand-curated ProPara-train-derived process-physics role schema
   (`consumes`/`produces`/`moves` keyword lists per process type), built from a DIFFERENT
   underlying corpus (ProPara paragraphs, not SimpleWiki process articles). All 9 gap-bearing
   process names are literal keys in this KB. This substitution is disclosed, not silent.
4. **go.obo** (`data/bio_kb_cache/go/go.obo`, Gene Ontology, 48,351 terms): literal term-name
   match among the 121 gaps' materials/wholes/processes. MEASURED: the only literal hit is the
   PROCESS name `photosynthesis` itself (GO legitimately has a term called "photosynthesis") --
   zero literal matches among any of the 13 materials or 72 wholes. A process-name-existence
   coincidence carries no relational content about a SPECIFIC (material,whole,fate) claim, so it
   is correctly excluded from gap-level "evidence" (counting it would inflate 19/121 gaps with a
   spurious, content-free hit). **go.obo's genuine contribution to this domain (physical
   objects/minerals/alloys) is measured to be exactly ZERO** -- same domain-mismatch conclusion
   the landed cell already reached for CauseNet-on-(process,whole), now independently confirmed
   for go.obo across all 3 pair types.

**HEADLINE MEASUREMENT** (script: `data/exp_gap_cross_source_coverage_audit_v1/coverage.json`,
reproduced inline in this cell's own `--audit-only` computation, not re-derived by hand):

| population | 1 source (CSKG only) | 2 sources | 3 sources | >=2 sources (genuine corroboration) |
|---|---|---|---|---|
| all 121 gaps | 67 (55.4%) | 46 (38.0%) | 8 (6.6%) | 54 (44.6%) |
| 62 eligible gaps | 26 (41.9%) | 28 (45.2%) | 8 (12.9%) | 36 (58.1%) |

Per-source hit rates (of 121): CSKG-extra (non-MadeOf relation or direct proc edge) 35/121
(28.9%); ProPara-KB role-schema 50/121 (41.3%); CauseNet 12/121 (9.9%); go.obo 0/121 (0.0%,
corrected). **Maximum observed distinct-real-source count for ANY single gap = 3** (CSKG +
CauseNet + KB-role-schema; go.obo never contributes a 4th).

## Step 2: the decisive mechanism-level pre-registration (computed BEFORE dispatch, per
CRLB/discriminator-reachability discipline)

`hdlab.grounding_acquisition_loop.MIN_CONFIRM = 4` (MEASURED@hdlab/grounding_acquisition_loop.py:
"schema_consistency_split_half needs >=2 traces PER HALF (n>=4) to ever produce a score") is the
FIRST gate `hdlab.prelim_tier.update_prelim_and_generalize` applies to EVERY item, BEFORE
retain-into-middle-tier and BEFORE cluster registration: `if n < min_confirm: continue` (n =
`len(it.traces)`, i.e. the item's own real encounter count). An item that never reaches n>=4 is
**never even registered into a CA3/DG cluster**, so it can never contribute to combined-evidence
exposure regardless of its cluster's size.

**Measured Step-1 ceiling: max real distinct-source encounters per gap = 3 < MIN_CONFIRM = 4.**
This is a hard, mechanism-level, PRE-registered prediction (not a hoped-for negative): with
genuine (non-repeated) real-source encounters, EVERY gap's own trace count tops out at 3, so NO
gap can ever cross the n>=4 retain floor, so NO cluster (regardless of its member count -- water's
20-eligible-member cluster included) can ever accumulate combined evidence toward
`cluster_exposure_floor = PROMOTE_MIN_EXPOSURE(8) * CLUSTER_EXPOSURE_MULTIPLIER(4) = 32`.
`crlb_n/a`: not a Gaussian-noise-floor metric; the reachability floor here is a discrete integer
gate (n>=4), and `discriminator_reachability = FALSE` for the genuine-encounter arm by this exact,
disclosed arithmetic (`3 < 4`). This cell RUNS the real pipeline to VET this hand-derivation
empirically (disk-verify discipline) rather than trusting arithmetic alone -- see self-test
section (b) below, which proves the SAME code path DOES cluster-promote at n=4/cluster-size-10
(synthetic control), isolating the shortfall to real-source scarcity, not a broken mechanism.

## What this cell IS (reuse, verbatim, no modification)

- Gap-set + eligibility: `experiments.exp_state_of_mind_relevance_gather_reasoning_union_v1`'s
  own build functions + `experiments.exp_three_tier_loop_real_corpus_gap_stream_v1`'s own
  `_eligible_targets`, `pk_of`, `cluster_key_fn`, `my_gap_register_fn`,
  `_positive_control_reproduction`, `run_arm` (imported directly).
- Mechanism organs: `hdlab.three_tier_loop.ThreeTierLoop`, `hdlab.grounding_acquisition_loop.
  {Library, consolidation_pass, context_vector, MIN_CONFIRM, PROMOTE_MIN_EXPOSURE,
  PROMOTE_MIN_CONSISTENCY}`, `hdlab.prelim_tier.{TierState, CLUSTER_MIN_MEMBERS,
  CLUSTER_EXPOSURE_MULTIPLIER}`, `hdlab.hd_fact_store.{HDFactStore, ACTIVE_STATUSES}`,
  `hdlab.gather_reason.{ca3_relevance_gather, fanout_two_hop, recovery_at, real_to_concat}`,
  `hdlab.situation_model_accumulate.{RelationRegister, unit_phase_vec}`.

## What this cell ADDS (the one new thing, honestly disclosed)

A **genuine distinct-source encounter-wave constructor**: for each eligible gap, up to 3 waves
(wave0=CSKG, always present; wave1=CauseNet, only if a literal pair was measured for that gap;
wave2=KB-role-schema, only if a literal role hit was measured for that gap), each wave's episode
text is a deterministic ASCII template WRAPPING the REAL matched source content (the specific
relation types / causal pair / role keyword actually found in Step 1 -- not a generic repeated
sentence). This REPLACES the landed cell's `VISITS_PER_GAP=6` uniform templated-repeat stream. No
gap ever gets more than 1 encounter per source category (no re-visiting the same source to
manufacture extra exposure -- that would reintroduce exactly the synthetic-multiplicity caveat
this cell exists to remove).

## Arms

- **G_full**: `ThreeTierLoop` (A_full wiring, per `hdlab/three_tier_loop.py`'s own documented
  ASSEMBLY DECISION) over the genuine encounter-wave stream (3 waves, FULL mode; 2 waves, smoke
  mode -- CauseNet's ~80s streaming scan is skipped in smoke per the landed cell's own
  do_causenet convention, so smoke's ceiling is 2 < MIN_CONFIRM, an even tighter case of the same
  finding).
- **G_no_middle**: bare `Library()` + `consolidation_pass` only, same genuine stream (mirrors the
  landed cell's B_no_middle ablation).
- **G_no_sweep**: full wiring, `tier_state.native_store_gen` reverted to a disconnected store
  (mirrors the landed cell's C_no_sweep ablation).
- **G_scramble**: G_full wiring, hop2 (CSKG bridge KG) scrambled (`scramble_edges`, imported) --
  eligibility is RECOMPUTED against the scrambled hop2 (matches the landed cell's own scramble
  population collapse), genuine stream applied to whatever tiny population remains eligible.
- **R_reference** (positive control / before-after contrast, NOT the test arm): EXACT reproduction
  of the landed cell's own A_full arm (`run_arm`, imported verbatim, `VISITS_PER_GAP=6`, templated
  `_episode_text`) on the SAME (unscrambled) eligible population. Purpose: (a) Gate-D-style proof
  that this NEW cell's plumbing correctly reproduces the KNOWN prior result (cited
  `data/exp_three_tier_loop_real_corpus_gap_stream_v1/metrics.json`: n_foundation=40, n_eligible=
  62), so a G_full zero is legible as a genuine data finding, not a cell bug; (b) the literal
  "before" side of the caveat-removal contrast requested by the task.

## Bands (pre-registered BEFORE running)

- `retain_floor_reachable = max(observed per-gap trace count in G_full) >= MIN_CONFIRM(4)`.
  HYPOTHESIZED@this pre-reg's Step-2 arithmetic: FALSE (max=3 in FULL mode, max=2 in smoke).
- `g_full_combined_promotions = sum(n_combined_promoted_this_pass across G_full checkpoints)`.
- `reference_reproduces_prior = abs(R_reference.final.n_foundation - 40) <= 15 AND
  R_reference.final.n_total_resolved == n_eligible` (generous tolerance: this cell uses fresh
  seeds, not the landed cell's own, so exact bit-reproduction is not expected, only the same
  qualitative regime; `n_total_resolved == n_eligible` is a tighter, near-deterministic check
  since ALL eligible items retain into middle by VISITS_PER_GAP=6 >= MIN_CONFIRM=4 regardless of
  seed).
- `no_leak_ok` = for every arm, `foundation_store.query(pk, RELATION) == []` for all eligible pk
  BEFORE the first encounter (audited, not assumed).
- `self_test_promotes_at_min_confirm_boundary` = self-test's synthetic matBig fixture (10-member
  cluster, 4 encounters/member, combined exposure 40>=32) DOES cluster-promote, AND matW3
  (3-member cluster, 3 encounters/member, mirroring the REAL ceiling) does NOT even retain.
  Proves the mechanism works correctly in principle; isolates the FULL-run zero to real-source
  scarcity specifically.

**HARD_PASS** (would require the Step-2 arithmetic to be WRONG -- an open question until run):
`g_full_combined_promotions > 0` for >= 1 real cluster AND `no_leak_ok` AND
`reference_reproduces_prior` AND `self_test_promotes_at_min_confirm_boundary`.

**HARD_FAIL_thin_cross_source_not_mechanism_failure** (expected, per Step-2 arithmetic):
`g_full_combined_promotions == 0` AND `retain_floor_reachable == False` (mechanistically
explained, not merely observed) AND `reference_reproduces_prior == True` (plumbing verified
correct -- rules out "cell bug" as the explanation) AND
`self_test_promotes_at_min_confirm_boundary == True` (mechanism verified NOT broken in general).
This verdict name is deliberately NOT "HARD_FAIL" alone -- per task instruction, a thin-coverage
finding is not a mechanism failure; it is reported as the Step-1 measurement's own conclusion.

**MIDDLE_BAND**: `reference_reproduces_prior == False` (plumbing suspect, investigate before
trusting G_full's zero) OR `self_test_promotes_at_min_confirm_boundary == False` (mechanism
itself suspect) OR `g_full_combined_promotions` is nonzero-but-small in a way inconsistent with
the Step-2 prediction (would need explanation).

`HP_SCOPE`: HARD_PASS/HARD_FAIL gates apply to G_full only. G_no_middle/G_no_sweep/G_scramble are
NOT expected to differ from G_full's (predicted) zero -- see `arms_differ_exempted` below.
R_reference carries its own single gate (`reference_reproduces_prior`), not the G_full bands.

## Controls

- **no-leak**: all 5 arms, audited explicitly.
- **scramble-the-chain**: G_scramble (see arms).
- **arms-must-differ** (META_RULE_AF), WITH DISCLOSED EXEMPTIONS: G_full vs R_reference MUST
  differ (different encounter construction, asserted not assumed). G_full vs G_no_middle vs
  G_no_sweep vs G_scramble are `arms_differ_exempted` -- per the Step-2 arithmetic, ALL FOUR are
  predicted to produce the IDENTICAL all-zero curve regardless of tier-wiring or chain-scrambling,
  because the binding constraint is the per-item TRACE-COUNT floor (n>=4), a property of the
  ENCOUNTER STREAM (which is identical across these 4 arms), not of which tier organs are wired
  or whether the bridge chain is scrambled. This is disclosed and pre-registered BEFORE running,
  not a post-hoc excuse for a failed assertion. If the empirical run contradicts this (arms DO
  differ), that itself falsifies part of the Step-2 prediction and is reported as a MIDDLE_BAND
  investigation trigger, not silently reconciled.

## Compute architecture

(b) sequential-CPU with justification: same regime as the landed cell (n_ent ~5000, n_dim=2048,
sub-10ms per fan-out call, ~60-90 distinct cues). One added cost: CauseNet full-file streaming
scan (~50-80s, FULL mode only, matches the landed source cell's own CauseNet-audit precedent).
Estimated total wall time: FULL ~90-150s (dominated by CSKG scan ~5s + CauseNet scan ~50-80s +
5 cheap arm-runs on <=62 targets, each sub-5s). No GPU-batching benefit (small fixed-size
sequential pipeline, not an independent phase-point sweep).

## Schema-vet declarations

```yaml
sweep_alignment_verdict: ALIGNED  # no swept parameter axis
discriminating_fraction: 1.0      # single regime; HYPOTHESIZED not saturated/floor per Step-2
composition_edges:
  - {from: gather_reason.fanout_two_hop, to: grounding_acquisition_loop.Library.flag, verdict: SHAPE_MATCH}
  - {from: grounding_acquisition_loop.consolidation_pass, to: hd_fact_store.HDFactStore.store, verdict: SHAPE_MATCH}
  - {from: prelim_tier.update_prelim_and_generalize, to: hd_fact_store.HDFactStore.store, verdict: SHAPE_MATCH}
positive_control_arms:
  - arm: R_reference
    primitive: experiments.exp_three_tier_loop_real_corpus_gap_stream_v1.run_arm (A_full wiring)
    cited_prior_atom: data/exp_three_tier_loop_real_corpus_gap_stream_v1/metrics.json
    cited_prior_metric: 40   # MEASURED@data/exp_three_tier_loop_real_corpus_gap_stream_v1/metrics.json:arm_results.A_full.final.n_foundation
    cited_prior_regime: {n_eligible: 62, visits_per_gap: 6, register_fn: my_gap_register_fn}
    test_regime: {n_eligible: 62, visits_per_gap: 6, register_fn: my_gap_register_fn}  # byte-identical call path, fresh seeds only
    tolerance: 15  # absolute, generous (fresh seeds -> cluster assignment may shift slightly)
    if_outside_tolerance: MIDDLE_BAND (plumbing suspect, investigate before trusting G_full's zero)
    regime_extension_audit: SHAPE_MATCH
  - arm: self_test_matBig_min_confirm_boundary
    primitive: hdlab.prelim_tier.update_prelim_and_generalize (n=4 retain floor)
    cited_prior_atom: hdlab/prelim_tier.py self_test() section (3) (n=12 traces/member, 3-member cluster)
    cited_prior_metric: "n_combined_promoted_total == 3 at exposure 36 >= 32"
    test_regime: {n_traces_per_member: 4, n_members: 10, combined_exposure: 40}
    tolerance: "exact (boolean: promotes or not)"
    if_outside_tolerance: HARD_FAIL (mechanism itself broken, not a data-thinness finding)
    regime_extension_audit: SHAPE_MATCH
functional_requirements: [see arms above; no new primitive, pure stream-construction + arm-wiring glue]
real_code_path_exercised: [KGStore, HDFactStore, Library, TierState, ScriptLibrary, RelationRegister, ThreeTierLoop]
substrate_signature_checked: [KGStore(n_ent,n_rel,n_dim,generator), HDFactStore(n_dim,seed,use_index), ThreeTierLoop(foundation_store,seed_base,n_dim,relation)]
guard_baseline_validated: N/A  # no control-beats-baseline (POP-vs-RANDOM-shaped) guard in this cell
deterministic_seeding: true    # fixed integer seeds throughout, no hash()/list(set()) ordering
cell_chunked: false
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false       # estimated wall time < 5 min, print-progress used instead
defensive_error_checking: "passed_start_marker+crash_diagnostic+no_bare_except; heartbeat exempted (est. wall time < 5 min)"
progress_logging: "print_flush_true"
arms_differ_verified: true     # G_full vs R_reference asserted; G_full vs {G_no_middle,G_no_sweep,G_scramble} EXEMPTED (see Controls section, rationale disclosed pre-run)
arms_differ_exempted: [[G_full, G_no_middle], [G_full, G_no_sweep], [G_full, G_scramble], [G_no_middle, G_no_sweep], [G_no_middle, G_scramble], [G_no_sweep, G_scramble]]
final_metrics_atomicity: tmp_replace
crlb_n/a: "discrete per-item trace-count retain floor (n>=MIN_CONFIRM=4), not a Gaussian noise-floor metric; discriminator_reachability=FALSE for G_full by measured Step-1 ceiling (max 3 real sources) vs MIN_CONFIRM=4 -- this IS the pre-registered finding, verified empirically not just hand-computed"
baseline_in_band: EXEMPTED for G_no_middle/G_no_sweep/G_scramble (deliberate ablation/sentinel arms, and ALL of G_* including G_full are expected near-zero by the Step-2 arithmetic -- not a saturating-baseline concern)
calibration_check: "default_ok_for_this_regime -- novelty_thresh calibrated identically to the landed cell (calibrate_novelty_threshold over real eligible-target cluster structure, imported verbatim)"
cardinality_ok: true  # EXPECTED checkpoints: G_* arms = n_waves (3 FULL / 2 smoke) each; R_reference = VISITS_PER_GAP(6); verified via len(checkpoints)==expected per arm
```

## Modes

`--self-test`: (a) calls `experiments.exp_three_tier_loop_real_corpus_gap_stream_v1.run_self_test`
directly (proves the REUSED R_reference-equivalent mechanism sound, avoids re-deriving ~100 lines
of fixture); (b) a NEW tiny synthetic fixture isolating the MIN_CONFIRM boundary: matW3 (3-member
cluster, 3 encounters/member, mirrors the REAL max) must NOT retain; matBig (10-member cluster, 4
encounters/member, combined exposure 40>=32) MUST cluster-promote. <10s total.

`--smoke`: real pipeline, `process_filter={"combustion","photosynthesis"}` (matches convention),
CauseNet scan skipped (2-wave ceiling: CSKG+KB only), same regime constants as FULL otherwise.
Discriminator-fires check: R_reference (the calibration arm) must still show
`n_combined_promoted_this_pass > 0` at some checkpoint (proves the REUSED mechanism fires
normally at smoke scale, i.e. this cell's plumbing, not just the landed cell's, works) -- this is
the smoke gate, NOT "G_full promotes" (G_full is analytically expected to stay at 0 even at smoke
scale, an even tighter case with only 2 waves available).

(no flag) FULL: all 121 real gap targets / 62 eligible, 3-wave genuine stream, CauseNet scan
included.

`--timeout 600` (10 min; estimated wall time ~90-150s per Compute Architecture, generous headroom
for the CauseNet streaming scan).
