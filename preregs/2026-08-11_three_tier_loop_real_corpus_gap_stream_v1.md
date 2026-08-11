# three_tier_loop_real_corpus_gap_stream_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: hdi_research "prove the FULL three-tier DYNAMICS
on a REAL corpus + a REAL gap-STREAM" (2026-08-11), landing on the already-assembled
`hdlab/three_tier_loop.py` (commit 4249cbfa6) and its organs
(`hdlab/gather_reason.py`, `hdlab/prelim_tier.py`, `hdlab/grounding_acquisition_loop.py`,
`hdlab/hd_fact_store.py`, `hdlab/script_grain_acquisition_loop.py`) -- all REUSED VERBATIM,
none modified by this cell.

Prior-work check (`bash tools/substrate_query.sh "three tier real corpus gap stream cumulative
resolution middle db sweep consolidation"`, cosine>0.30 threshold): top hits were generic
word-similarity matches (`consolation` cos=0.3721, `consolidation` cos=0.3447, `resolution`
cos=0.3379) -- none are a prior REAL-CORPUS three-tier consumer cell. Consistent with
`data/capability_registry.jsonl` row `three_tier_loop`, which explicitly states the module
"NOT yet run against a real external corpus ... this is a mechanism-composition witness, not a
benchmark result" and `integration_status: ISLAND`. This cell is genuinely novel work closing
that gap, not a rediscovery.

## What this cell IS

The REAL gap-set (121 targets), REAL reading corpus (`data/corpora/process_articles_v1/`),
REAL CSKG-narrow bridges (`data/cskg_foundation_v1/`), and the REAL GATHER (CA3 relevance
gather) + REASON (K<=2 fan-out) mechanism are reused verbatim from the landed HARD_PASS cell
`experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py`
(`data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json`,
verdict=HARD_PASS_state_of_mind_gather_load_bearing, arm3@5=0.3802, arm1@5=0.0413, N=121) via
its own functions (`build_reading_facts`, `build_cskg_bridges`, `build_gap_set`,
`build_entity_index`, `fresh_kg`, `ingest_reading_hop1`, `ingest_bridge_hop2`,
`build_material_codebook`, `scramble_edges`), imported directly, not re-derived.

## What this cell ADDS (the one new thing, honestly disclosed)

The prior cell computed EACH gap's answer in a single deterministic pass (no repeated
encounters, no middle-db, no sweep -- it directly measured recovery@k). This cell wraps the
SAME real gap-set + REAL reasoning mechanism in a multi-ENCOUNTER STREAM so the three-tier
accumulation dynamics (retain -> re-encounter-pull -> periodic CA3/DG sweep -> combined-
evidence gate-crossing) have something to operate on. The encounter multiplicity (repeated
episodic mentions of the same gap) is SYNTHETIC (deterministic, hashlib-seeded templated text
embedding the REAL entity names), matching the exact precedent already used by
`verification/test_three_tier_loop_e2e.py`'s `_episode_text` and by
`experiments/exp_crutch_fade_social_iqa_v1.py`'s own episode framing -- this is the
established convention for this codebase's middle-tier tests, not a new pattern. What is REAL
and NOT synthetic: the gap-set itself (121 targets, CSKG-bridge-derived), the KG structure
(hop1 reading edges + hop2 narrow-CSKG bridge edges), the CA3 gather + K<=2 fan-out REASON
mechanism (`hdlab.gather_reason`, called on real KGStore objects), and which candidate the
reasoning mechanism actually nominates (per-cue restricted fan-out, not hand-typed).

## Addenda from authoring/self-test (found empirically, disclosed before any full dispatch)

- **register_fn override.** The default `hdlab.three_tier_loop.gap_register_fn` binds
  AGENT=subject(process), CONSEQUENT=f"GAP_{label}". Since every trace this cell ever flags is
  POS (no NEG evidence is generated -- see below), CONSEQUENT is a CONSTANT across the whole
  target set, wasting a role slot; and since a real process typically touches multiple
  via_materials (~6.3 on average, `reading_audit.n_process_entity_pairs / n_processes` from the
  cited landed cell), AGENT=process collides across DIFFERENT via_material clusters. MEASURED
  during self-test debugging: a same-process-cross-cluster pair scored cosine=0.412 vs a
  genuine same-cluster pair's 0.384 under the default register_fn -- the FALSE match scored
  HIGHER, breaking CA3/DG separability. Fixed via a cell-local `my_gap_register_fn` override
  (an explicitly caller-overridable parameter of `update_prelim_and_generalize`/`ThreeTierLoop.
  consolidate`, not a modification to any reused module) that binds BOTH TRIGGER and CONSEQUENT
  to `cluster_key` (via_material) and confines the two per-instance-varying identifiers
  (candidate=whole, subject=process) to AGENT/PATIENT. MEASURED after the fix: same-cluster
  0.35-0.36, same-process-cross-cluster 0.25, no-overlap-cross-cluster ~0.00-0.03 -- cleanly
  ordered, correctly separable at a calibrated `novelty_thresh`. Calibration (both self-test and
  FULL) deliberately picks the HARDEST available wrong-pair (a same-process, different-via_
  material pair) rather than an easy no-overlap pair, per `calibrate_novelty_threshold`'s own
  "prefer correctly separating over correctly matching" discipline.
- **Smoke-scale VISITS_PER_GAP adjustment.** `cluster_exposure_floor = PROMOTE_MIN_EXPOSURE(8) *
  CLUSTER_EXPOSURE_MULTIPLIER(4) = 32` is a FIXED constant, not scale-adjusted. MEASURED at the
  smoke process_filter `{combustion, photosynthesis}`: the largest via_material clusters among
  18 eligible targets are size 5 (magnesium, water), size 3 (sugar) -- versus FULL's size 44/38
  (water/steel). At `VISITS_PER_GAP=6`, `5*6=30 < 32` -- the sweep never fires at smoke scale
  (confirmed: `n_combined_promoted_this_pass=0` at every checkpoint, first smoke attempt).
  `VISITS_PER_GAP_SMOKE=11` (`5*11=55>=32`) is used ONLY for `--smoke`; FULL keeps
  `VISITS_PER_GAP=6` unchanged (its own clusters already clear 32 comfortably per the hand-
  computed feasibility table below). This is the same class of adjustment the self-test's own
  `visits=12` already uses, for the identical reason (smaller cluster -> more visits needed to
  clear the SAME fixed floor) -- disclosed, not silently regime-mismatched, and does not touch
  the FULL regime's own parameters.
- **Positive-control (Gate D) gating is FULL-mode-only.** A 2-process smoke subset's recovery@5
  is a genuinely different (smaller) population than the cited 121-target FULL population (the
  cited cell's own `per_process_recovery` already discloses combustion@5=0.714,
  photosynthesis@5=0.526, both far from the population mean 0.3802) -- comparing a subset
  average against the full-population cited number is an apples-to-oranges test, not a genuine
  regime/invocation mismatch. `positive_control_ok` is computed (and gates the verdict) ONLY
  when `run_mode == "full"`; smoke logs `pc_recovery5` for visibility but does not gate on it.

## Mechanism: per-encounter CUE restriction (the design's one new wiring choice)

Each real target `t = (process, whole, fate, via_material)` defines a CUE
`(process, via_material, fate)`. At every encounter of `t`, REASON is run via
`hdlab.gather_reason.fanout_two_hop(hop1, hop2, ent_idx[process], fate_idx[fate], bridge_idx,
K1_FANOUT, K2_FANOUT, n_ent, restrict_hop1_to={ent_idx[via_material]})` -- restricting hop-1 to
the ONE material this gap's cue names (a single-element subset of the same
`restrict_hop1_to` mechanism `hdlab.gather_reason`'s own docstring documents as "how a
GATHER-stage result narrows REASON's search space"; no modification to that module). A target
is ELIGIBLE for the stream iff `via_material` is in the process's own real CA3-gathered
material set (`hdlab.gather_reason.ca3_relevance_gather`) AND `recovery_at(ranked, gold_idx,
K_RESOLVE=5) == 1` under this cue-restricted reasoning (both computed once per cue, cached;
verified empirically, not assumed). Because restriction narrows hop-1 to exactly the material
that (by the gap-set's own construction) real-bridges to the gold whole via `/r/MadeOf`, this
should recover the gold candidate reliably once the hub-material competition from a process's
OTHER materials is removed -- this is the SAME hub-competition phenomenon the source cell's own
`hub_material_counts` field discloses (water/steel dominate the wide fan-out).

**This directly manufactures the "weak sub-threshold, only-clusterable" regime the task asks
for**: `VISITS_PER_GAP = 6` is fixed BELOW `PROMOTE_MIN_EXPOSURE = 8` (the strict single-item
promotion floor, reused unmodified from `grounding_acquisition_loop.py`), so **no individual
gap can ever cross the strict per-item gate alone by construction** (a design choice, not an
accident -- it isolates cluster/sweep value cleanly: any FOUNDATION promotion in this cell is
attributable ONLY to the combined-evidence sweep, never to strict-gate accumulation alone).
Cluster membership is the target's own real `via_material` (parsed back out of
`hdlab.three_tier_loop.gap_item_key`'s relation slot via `parse_gap_item_key`), so clusters are
exactly the 10+ real bridging-material groups the source cell's `hub_material_counts` already
discloses (water, steel, rock, magnesium, sugar, energy, lava, ...) -- not a hand-picked
grouping.

## Positive control (Gate D -- reproduce the prior chain-grade result at the test regime)

Before trusting the new per-cue eligibility mechanism, this cell reproduces the SOURCE cell's
own arm3 recovery@5 metric (0.3802, N=121) using the IDENTICAL restriction pattern the source
cell used (restrict hop-1 to ALL CA3-gathered materials for the process, not the single-cue
restriction) via the PROMOTED `hdlab.gather_reason` module. `positive_control_arm3_reproduction
= recovery@5 over all 121 targets, restrict_hop1_to = full CA3-gathered set`.
`tolerance = 0.10` absolute; outside tolerance -> `HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH`,
downstream arms untrusted (per exp_dev SCHEMA-VET Gate D).

## Functional requirements (Gate E)

| Requirement | Owned primitive |
|---|---|
| Real gap-set + real KG structure | `experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py`'s own build functions (imported) |
| STATE OF MIND + GATHER | `hdlab.situation_model_accumulate.RelationRegister` + `hdlab.gather_reason.ca3_relevance_gather` |
| REASON (per-cue) | `hdlab.gather_reason.fanout_two_hop(restrict_hop1_to=...)` |
| PARSE (item identity + context) | `hdlab.three_tier_loop.gap_item_key` + `hdlab.grounding_acquisition_loop.context_vector` |
| GATE (strict single-item) | `hdlab.grounding_acquisition_loop.consolidation_pass` |
| MIDDLE TIER (retain-forever) | `hdlab.prelim_tier.TierState.prelim_lib` / `prelim_store` |
| SWEEP (CA3/DG combined-evidence) | `hdlab.prelim_tier.update_prelim_and_generalize` -> `hdlab.script_grain_acquisition_loop.ScriptLibrary.match_or_spawn` |
| FOUNDATION | `hdlab.hd_fact_store.HDFactStore` |
| Assembly / answer routing | `hdlab.three_tier_loop.ThreeTierLoop` |

No new primitive needed; this cell is pure stream-generation + arm-wiring glue around
already-validated organs (matches `three_tier_loop.py`'s own "assembly glue, not a new
mechanism" framing).

## Arms

- **A_full**: `hdlab.three_tier_loop.ThreeTierLoop` as documented (its own ASSEMBLY DECISION:
  `tier_state.native_store_gen = foundation_store`, i.e. combined-evidence promotions land in
  the shared foundation store). GATE + MIDDLE + SWEEP all active.
- **B_no_middle**: ablate the middle-db. No `TierState` constructed at all; only a bare
  `hdlab.grounding_acquisition_loop.Library()` + `consolidation_pass(..., native_store=
  foundation_store)` at each checkpoint (the strict-gate-only pipeline, i.e. this codebase's
  own pre-2026-08-11 status quo before the middle-tier promotion existed). Sub-threshold traces
  sit in the strict `Library`'s PENDING queue with no second-chance retrieval route -- never
  answerable from anywhere.
- **C_no_sweep**: full `ThreeTierLoop` wiring EXCEPT the one documented ASSEMBLY DECISION is
  reverted: immediately after construction, `loop.tier_state.native_store_gen` is reassigned to
  a fresh, DISCONNECTED `HDFactStore` (i.e. `TierState`'s own un-wired default, the state
  BEFORE `ThreeTierLoop.__init__` performs its documented wiring). The retain + CA3/DG
  cluster-keying + combined-evidence computation still run unmodified inside
  `update_prelim_and_generalize` (so `n_middle` should match arm A almost exactly -- logged as
  a cross-check), but any combined-evidence promotion lands in the disconnected store, never
  reaching `loop.answer()`'s FOUNDATION check. This ablates exactly the ONE wiring choice
  `three_tier_loop.py`'s own docstring calls out as "the ONE new wiring choice this module
  makes" -- a natural, in-scope ablation, not a hack.
- **A_scramble_control**: identical wiring to A_full, but `hop2` is built from
  `scramble_edges(narrow_edges, SEED_SCRAMBLE)` (source cell's own degree-preserving
  fixed-seed permutation, imported verbatim) instead of the real narrow-CSKG bridge edges.
  Breaks the (material -> whole) correspondence the whole mechanism depends on; expected near-
  total eligibility collapse (per-cue `recovery_at(ranked_scrambled, gold, 5)` should fail for
  nearly every cue) -> near-zero cumulative resolution.

All 4 arms consume the SAME target stream ordering (deterministic, `sorted()` throughout) and
the SAME `VISITS_PER_GAP` / checkpoint cadence, differing ONLY in the one documented ablation
axis (or the hop2 KG content, for the scramble control).

## Checkpoint / encounter-stream design

`VISITS_PER_GAP = 6` "rounds"; round `v` in `[0, 6)` flags one POS trace (episode-templated
context vector) for every ELIGIBLE target, in deterministic `sorted()` order. A checkpoint
(GATE `consolidation_pass` + MIDDLE `update_prelim_and_generalize`, or the arm-specific subset)
runs after every round completes (`pass_idx = v + 1`, matching `consolidation_pass`'s own
Dumay-Gaskell intervening-pass semantics). This gives 6 checkpoints per arm, a genuine
CUMULATIVE growth curve (encounters 1..6) suitable for the deliverable's cumulative-resolution
plot. `MIN_CONFIRM = 4` (reused default) -- so MIDDLE-tier retain can fire from checkpoint 4
onward (once >= 4 traces exist); strict banking (subject to the intervening-pass rule) can fire
from checkpoint 5 onward but individual exposure NEVER reaches `PROMOTE_MIN_EXPOSURE = 8` (by
construction, `VISITS_PER_GAP = 6 < 8`), so the strict per-item promotion branch is
STRUCTURALLY inert in every arm -- all FOUNDATION promotions in arm A are attributable
exclusively to the combined-evidence sweep.

## Controls

- **no-leak**: for every arm, `foundation_store.query(pk, RELATION) == []` for all eligible
  `pk` BEFORE the first encounter (audited explicitly, not assumed -- fresh `HDFactStore` per
  arm, zero facts stored pre-stream).
- **scramble-the-chain**: see A_scramble_control above.
- **arms-must-differ** (META_RULE_AF): per-checkpoint `(n_foundation, n_middle)` tuples hashed
  and compared pairwise across A/B/C; must be non-identical (trivial given the ablations, but
  asserted not assumed).

## Bands (pre-registered BEFORE running; `n_eligible` = arm A's real measured eligible-target
count, not the raw 121, for honesty in case some targets are excluded)

- `delta_B_frac = (resolved_A - resolved_B) / n_eligible` where `resolved = n_foundation +
  n_middle` at the FINAL checkpoint (middle-db load-bearing test).
- `delta_C_foundation_frac = (foundation_A - foundation_C) / n_eligible` at the FINAL
  checkpoint (sweep load-bearing test).
- `scramble_clean = scramble_resolved_final <= max(5, 0.10 * resolved_A_final)`.
- `no_leak_ok = no-leak holds for all 4 arms`.
- `arms_differ_ok = A/B/C per-checkpoint tuples pairwise non-identical`.
- `positive_control_ok = abs(positive_control_arm3_reproduction - 0.3802) <= 0.10`.

**HARD_PASS** requires ALL of: `delta_B_frac >= 0.50` AND `delta_C_foundation_frac >= 0.30` AND
`scramble_clean` AND `no_leak_ok` AND `arms_differ_ok` AND `positive_control_ok`.
(META_RULE_L: floors below are set with >=20-percentage-point headroom under the HARD_PASS
bars, well above the 5%-of-band-width minimum margin.)

**HARD_FAIL** if ANY of: `delta_B_frac < 0.10` (middle-db adds ~nothing) OR
`delta_C_foundation_frac < 0.05` (sweep adds ~nothing to FOUNDATION-crossing) OR
`positive_control_ok` is False (regime/invocation mismatch, downstream arms untrusted) OR
a control fails (`not scramble_clean` or `not no_leak_ok` or `not arms_differ_ok`).

**MIDDLE_BAND**: anything between (e.g. one delta clears its HARD_PASS bar but the other only
clears its HARD_FAIL floor, or controls are directionally right but not fully clean).

`HP_SCOPE`: HARD_PASS gates apply to the A-vs-B and A-vs-C comparisons on the REAL
(unscrambled) chain. `A_scramble_control` carries no HARD_PASS gate of its own (it is a
control, graded only on `scramble_clean`); `B_no_middle` and `C_no_sweep` are DELIBERATE
sentinel/ablation arms and are NOT expected to clear any HARD_PASS floor themselves (per
META_RULE_L 5b, chain-grade gates do not apply to them).

## Compute architecture

(b) sequential-CPU with justification: single deterministic pipeline pass per arm (4 arms),
no independent phase-point grid to batch; per-cue `fanout_two_hop` matmuls are tiny (`n_ent`
~5000, matching the source cell's own landed regime, `n_dim=2048`), each call sub-10ms on CPU;
total distinct cues ~60-90; total wall time estimated well under 5 minutes (source cell's own
FULL landed in 123.79s total, 80s of which was a CauseNet leak-scan this cell does NOT run).
No GPU-batching benefit available (no independent phase-point sweep to vectorize; the
sequential per-arm consolidation passes ARE the mechanism under test, not overhead to remove).

## Schema-vet declarations

```yaml
sweep_alignment_verdict: ALIGNED  # gate A -- no swept parameter axis; VISITS_PER_GAP, K1/K2,
                                   # MIN_CONFIRM/PROMOTE_MIN_EXPOSURE/CLUSTER_* all fixed,
                                   # reused-default constants, uniformly applied to all 4 arms
discriminating_fraction: 1.0      # gate B -- single regime; HYPOTHESIZED (below) situates it
                                   # well inside the discriminating band, not saturated/floor
composition_edges:                # gate C
  - {from: gather_reason.fanout_two_hop, to: grounding_acquisition_loop.Library.flag, verdict: SHAPE_MATCH}
  - {from: grounding_acquisition_loop.consolidation_pass, to: hd_fact_store.HDFactStore.store, verdict: SHAPE_MATCH}
  - {from: prelim_tier.update_prelim_and_generalize, to: hd_fact_store.HDFactStore.store, verdict: SHAPE_MATCH}
  # all edges pre-existing inside three_tier_loop.py / prelim_tier.py, already composed and
  # witnessed by verification/test_three_tier_loop_e2e.py; this cell adds no new organ edges,
  # only new callers into the same entry points.
positive_control_arms:            # gate D
  - arm: arm0_positive_control_reproduction
    primitive: hdlab.gather_reason (ca3_relevance_gather + fanout_two_hop)
    cited_prior_atom: data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json
    cited_prior_metric: 0.3802   # MEASURED@data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json:recovery.arm3_at5
    cited_prior_regime: {n_ent: 4946, K1: 30, K2: 500, restrict: all_ca3_gathered_materials}
    test_regime: {K1: 30, K2: 500, restrict: all_ca3_gathered_materials}  # byte-identical regime, promoted-module call path
    tolerance: 0.10
    if_outside_tolerance: HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
    regime_extension_audit: SHAPE_MATCH  # same code path via promoted hdlab.gather_reason, not a new regime
functional_requirements: [see table above]  # gate E
real_code_path_exercised: [KGStore, HDFactStore, Library, TierState, ScriptLibrary, RelationRegister, ThreeTierLoop]  # gate F.1
substrate_signature_checked: [KGStore(n_ent,n_rel,n_dim,generator), HDFactStore(n_dim,seed,use_index), ThreeTierLoop(foundation_store,seed_base,n_dim,relation)]  # gate F.2/F.3, base kwargs only
guard_baseline_validated: N/A  # no control-beats-baseline (POP-vs-RANDOM-shaped) guard in this cell; N/A per gate F.4 scope
deterministic_seeding: true    # gate F.5 -- fixed integer seeds throughout, no hash()/list(set()) ordering; queue_add static scan applies
cell_chunked: false            # single deterministic pass per mode, not a resumable multi-unit loop
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false       # estimated wall time well under the 15-min heartbeat bar; declared print-progress instead
defensive_error_checking: "passed_start_marker+crash_diagnostic+no_bare_except; heartbeat exempted (est. wall time < 5 min, well under 15-min bar)"
progress_logging: "print_flush_true"  # not strictly mandated (timeout < 1800s) but implemented for auditability
arms_differ_verified: true     # asserted at runtime via per-checkpoint (n_foundation,n_middle) hash comparison
final_metrics_atomicity: tmp_replace
crlb_n/a: "discrete gap-resolution counting (cumulative resolved-gap counts per checkpoint), no Gaussian noise-floor metric; discriminator_reachability=true by hand-computed cluster-size arithmetic below"
baseline_in_band: EXEMPTED for B_no_middle and C_no_sweep (deliberate ablation/sentinel arms per HP_SCOPE, not saturating baselines; META_RULE_AG does not apply -- these arms are EXPECTED near-zero-foundation by construction)
calibration_check: "default_ok_for_this_regime -- novelty_thresh calibrated via hdlab.script_grain_acquisition_loop.calibrate_novelty_threshold using REAL matched/wrong pairs drawn from the actual eligible-target cluster structure (largest vs second-largest via_material cluster), not hand-tuned per arm; module default (0.15) used as a disclosed fallback only if fewer than 2 distinct multi-member clusters exist among eligible targets"
cardinality_ok: true           # EXPECTED_N_UNITS = 4 arms * VISITS_PER_GAP(6) checkpoints = 24 consolidation-pass units; verified via len(checkpoints)==VISITS_PER_GAP for all 4 arms
```

## Hand-computed feasibility check (HYPOTHESIZED, pre-run, from the cited prior cell's disclosed
`hub_material_counts` -- MEASURED@data/exp_state_of_mind_relevance_gather_reasoning_union_v1/metrics.json:gap_set_audit.hub_material_counts, top-10 of 13 narrow materials, 121 targets total)

At `VISITS_PER_GAP=6`, cluster combined-exposure = `6 * n_cluster_members` (`CLUSTER_MIN_MEMBERS=3`,
`cluster_exposure_floor = PROMOTE_MIN_EXPOSURE(8) * CLUSTER_EXPOSURE_MULTIPLIER(4) = 32`):
water(44 members, 264>=32 CLEAR), steel(38, 228 CLEAR), rock(8, 48 CLEAR), magnesium(7, 42
CLEAR), sugar(6, 36 CLEAR), energy(6, 36 CLEAR), lava(3 members meets CLUSTER_MIN_MEMBERS but
18<32, correctly FAILS -- a genuine "insufficient combined evidence" case), mineral/material/
oxygen (2 members each, below CLUSTER_MIN_MEMBERS=3, never attempt combined promotion at all).
THEORETICAL@cluster_exposure_floor=promote_min_exposure*cluster_exposure_multiplier. This
situates the regime well inside the discriminating band (most-but-not-all clusters clear,
matching gate B's >=30% discriminating-fraction requirement trivially, and gives an honest
non-trivial residual of un-resolvable gaps for realism) -- not by-construction saturated (100%
resolve) nor floor (0% resolve).

## Modes

`--self-test`: tiny synthetic fixture (12-16 entities, 2 synthetic clusters: one 3-member
cluster expected to combined-promote, one 2-member cluster expected to never attempt combined
promotion), all 4 arms run, real `KGStore`/`HDFactStore`/`Library`/`TierState`/`ScriptLibrary`/
`RelationRegister`/`ThreeTierLoop` objects, <5s.

`--smoke`: real pipeline, `process_filter={"combustion","photosynthesis"}` (matches the source
cell's own smoke convention), same regime constants as FULL. Discriminator-fires check
(SCHEMA-VET Gate K / DISCRIMINATOR-MUST-SURVIVE-SCALE option A -- same regime params, smaller
target set): smoke MUST show `n_combined_promoted_this_pass > 0` at some checkpoint for arm A,
AND `foundation_A_final > foundation_C_final` at smoke scale, before FULL is dispatched. If the
smoke's 2-process subset doesn't have >=1 cluster with >=3 eligible members, re-spec the smoke
process_filter (add a 3rd process) rather than dispatch FULL blind.

(no flag) FULL: all 15 real processes, all 121 real gap targets (or however many survive the
eligibility audit).

`--timeout 600` (10 min; estimated wall time ~2-5 min per Compute Architecture above, generous
headroom).
