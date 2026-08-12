# curriculum_prerequisite_scaffold_consolidation_v1 -- pre-registration

Author: exp_dev (Agent-Teams). Task source: Director spawn prompt (2026-08-11), "prove the
CURRICULUM / PREREQUISITE-ORDERING principle brain-foundationally" -- the schema-scaffolding
consolidation mechanism (Tse et al. 2007/2011: new info that fits an existing CONSOLIDATED
schema consolidates dramatically faster than info with no consolidated scaffold). Reuses the
proven three-tier loop (`hdlab/three_tier_loop.py`, commit 4249cbfa6 + siblings) as a NEW test:
does prior CONSOLIDATION (not mere exposure) scaffold later learning in-substrate.

Prior-work check: `bash tools/substrate_query.sh "curriculum prerequisite ordering schema
scaffolding consolidation dependent concept"` (cosine>0.30 threshold). Top hit cosine=0.3164,
entity="Prerequisite ordering" (`notes/exp_dev_handoff_research_substrate_compositional_shard_
system_3x_2026-06-10.md`) -- inspected directly: that note's "Prerequisite ordering" section is
an EXPERIMENT-DISPATCH sequencing list (which of 10 unrelated PP-COMP-* anchor cells to queue
first), not a schema-consolidation/curriculum-learning mechanism test. False-positive on the
generic English phrase, not a rediscovery. Second/third hits (cosine 0.30/0.297, "scaffolding" /
"DEPENDENCY ORDERING") are similarly generic term matches, not prior tests of THIS mechanism.
No genuine prior art at cosine>0.30 for schema-scaffolding/curriculum-consolidation in-substrate
-- this cell is novel work, not a rediscovery.

## What this cell IS

REUSE (wire-don't-island; every organ below imported read-only, called verbatim, none modified):
  `hdlab.three_tier_loop.ThreeTierLoop` (encounter/consolidate/answer -- the full GATE+MIDDLE
    engine, including its own documented ASSEMBLY DECISION wiring combined-evidence promotion
    into the shared foundation store) + `gap_item_key` / `gap_register_fn`
  `hdlab.gather_reason.ca3_relevance_gather` / `fanout_two_hop` / `top1` / `build_codebook` /
    `real_to_concat` (GATHER: topical relevance; REASON: restricted fan-out composition)
  `hdlab.grounding_acquisition_loop.context_vector` (per-episode context encoding) +
    `consolidation_pass` (via ThreeTierLoop.consolidate, the strict single-item GATE)
  `hdlab.prelim_tier.TierState` / `update_prelim_and_generalize` (middle tier: retain-forever +
    CA3/DG sweep, via ThreeTierLoop)
  `hdlab.hd_fact_store.HDFactStore` / `ACTIVE_STATUSES` (foundation)
  `hdlab.situation_model_accumulate.RelationRegister` / `unit_phase_vec` (state-of-mind cue)
  `hdlab.kg_traversal.KGStore` (tiny 5-entity DEPENDS_ON/IDENTITY structural KG)

## What this cell ADDS (the one new thing, honestly disclosed)

A small PREREQUISITE CHAIN (energy -> work -> power, 3 concepts, K=3 dependent property-facts
each for work/power = 6 measured "dependent facts") read under 5 different STREAM ORDERS,
where each dependent concept's per-encounter comprehension is gated by a REAL REASON call
(`fanout_two_hop`) whose `restrict_hop1_to` is computed FRESH each tick as the INTERSECTION of
(a) GATHER's topical-relevance set (`ca3_relevance_gather`, order-independent -- meaning-
similarity is always available, mirroring how a reader can tell a passage is "about" a topic
before mastering it) and (b) the set of concepts CURRENTLY ACTIVE in the shared
`HDFactStore` foundation (i.e., genuinely CONSOLIDATED, not merely present in the KG). This
composition (GATHER-set ^ CONSOLIDATED-set, cell-local, not a modification to `fanout_two_hop`
itself, which already documents `restrict_hop1_to` as caller-supplied) is the SPECIFIC
mechanism under test: comprehension of a dependent concept's material succeeds ONLY when its
direct prerequisite is queryable in the foundation store at that moment.

Per tick, `resolved_this_tick = (top1(ranked) == true_prereq_idx)` gates
`ThreeTierLoop.encounter(..., also_strict=resolved_this_tick)`: EVERY tick unconditionally
flags the MIDDLE tier (mere exposure, hippocampal-style retain-forever accumulation) but ONLY a
`resolved_this_tick=True` tick flags the STRICT/foundation-track Library (comprehension-gated
encoding). This directly operationalizes "seen" (middle-tier retention, independent of
comprehension) vs "consolidated" (foundation promotion, gated on successful REASON) as two
DIFFERENT, independently-observable outcomes (`ThreeTierLoop.answer()` returns
`MIDDLE_RESOLVED` vs `FOUNDATION_RESOLVED` vs `UNRESOLVED`), which is the decisive isolation
this task requires.

## Confound guard (disclosed BEFORE running, not found after a bad result)

The middle tier's OWN combined-evidence cluster-promotion path (`update_prelim_and_generalize`)
can ALSO reach the shared foundation store once a cluster of >= `CLUSTER_MIN_MEMBERS` items
crosses `cluster_exposure_floor = PROMOTE_MIN_EXPOSURE * CLUSTER_EXPOSURE_MULTIPLIER = 32`
raw exposures -- if that fired here it would let raw REPEATED EXPOSURE ALONE (no comprehension
gating) promote a dependent concept to foundation, defeating the isolation this cell exists to
prove. Guard: `middle_kwargs={"cluster_min_members": 999}` on every `loop.consolidate()` call,
structurally disabling combined-evidence promotion regardless of `cluster_key_fn`/register-
vector similarity (never relying on the two clusters staying accidentally dissimilar). Verified
at runtime: `n_combined_promoted_this_pass == 0` at every checkpoint, every arm (asserted, not
assumed) -- isolates FOUNDATION promotion to ONLY the strict single-item GATE path, which is
exactly the comprehension-gated (`also_strict`) pathway under test.

## Concept chain + items

```
energy  (root, no prereq)                         -- 1 concept-level item
work    (prereq: energy)   -- 3 property items: {definition, unit_relation, formula_role}
power   (prereq: work)     -- 3 property items: {definition, unit_relation, formula_role}
distractors: gravity (topical red herring for "work"), friction (for "power") -- never
  consolidated, never given a Library item; present ONLY as a spurious DEPENDS_ON hop1 edge +
  GATHER codebook entry, to verify GATHER's own topical selectivity is a real, exercised check
  (self-test asserts `ca3_relevance_gather` returns the true prereq, not the distractor).
```

Item keys (uniform `hdlab.three_tier_loop.gap_item_key` shape throughout, so
`ttl.gap_register_fn` reuses verbatim for BOTH concept-level and property items):
`concept_marker_key(name) = gap_item_key(name, "DEPENDS_ON", prereq or "AXIOM")`,
`prop_item_key(name, prop) = gap_item_key(f"{name}_{prop}", "DEPENDS_ON", prereq or "AXIOM")`.
`DEPENDENT_PROPERTY_KEYS` = the 6 work/power property keys -- these are the "B/C dependent
facts" the headline metric (`property_frac`) measures. `energy` (root) carries no property
items -- it is the scaffold being tested, not itself a dependent fact.

`RELATION = "CONCEPT_CONSOLIDATED"` (single relation name, uniform across all items).

## Arms

1. **CORRECT** -- order `[energy, work, power]`. Expect `property_frac = 1.0`.
2. **REVERSED** -- order `[power, work, energy]` (full reversal). Expect `property_frac = 0.0`
   (power's block ends before work exists; work's block ends before energy exists).
3. **PARTIAL** -- order `[work, energy, power]` (mechanism-SPECIFICITY bonus, not just "any
   prior exposure helps"). work fails (energy not yet consolidated during work's block);
   energy then consolidates normally (root); power's block runs AFTER energy consolidates, but
   power's DIRECT prereq is `work`, which never consolidated (its own block already ended with
   zero comprehension-gated ticks) -- so power must ALSO fail (`property_frac = 0.0`) despite a
   transitively-related concept (energy) being available. Distinguishes "direct-prerequisite
   consolidated" from "something upstream got learned eventually."
4. **SEEN_NOT_CONSOLIDATED** -- order `[energy, work, power]`, but energy's OWN
   `also_strict` is force-overridden to `False` for its entire block (energy is still read --
   flagged into the middle tier every tick, real coherent context, real repeated exposure --
   but NEVER flagged into the strict/foundation-track Library, so it can never bank or promote).
   Expect `property_frac = 0.0`: work's REASON check queries the foundation store for energy's
   marker key and finds nothing (energy is `MIDDLE_RESOLVED` via `loop.answer()`, never
   `FOUNDATION_RESOLVED`), despite correct topological order and genuine repeated exposure. This
   is the DECISIVE ISOLATION the task requires: order-correct + seen is insufficient; the
   prerequisite must be CONSOLIDATED (foundation-queryable).
5. **ANTI_ARTIFACT_SCRAMBLE** -- order `[energy, work, power]` (correct order, unmodified
   REASON gating), but energy's Library/middle flagging uses a SCRAMBLED key
   (`gap_item_key("SCRAMBLED_energy_ID", "DEPENDS_ON", "AXIOM")`) instead of its real
   `concept_marker_key("energy")` -- energy genuinely consolidates (banks + promotes normally,
   `exposure=9 consistency=1.0`), just under the wrong stored identity. work's REASON check
   still queries the REAL key (`concept_marker_key("energy")`, unchanged) and finds nothing.
   Expect `property_frac = 0.0`: proves success requires retrieving A's ACTUAL CONTENT (a named
   lookup), not an artifact of pass-index/order bookkeeping (which would have succeeded here
   since order and pass-count are byte-identical to CORRECT).

## Controls

- **no-leak**: fresh `HDFactStore` per arm; `foundation_store.query(k, RELATION) == []` for
  every concept-marker-key and property-key BEFORE the first tick, asserted per arm.
- **combined-evidence-promotion-disabled**: `n_combined_promoted_this_pass == 0` at every
  checkpoint, every arm (see Confound guard above).
- **arms-must-differ** (META_RULE_AF): `sha256(json({"concept_status":..., "property_status":
  ...}))` per arm; CORRECT's digest must differ from EACH of REVERSED / PARTIAL /
  SEEN_NOT_CONSOLIDATED / ANTI_ARTIFACT_SCRAMBLE's digest (asserted at runtime).
- **GATHER topical-selectivity self-check** (self-test): `ca3_relevance_gather` on the
  work/power query vectors must return the TRUE prereq, excluding the distractor
  (gravity/friction), confirming the restriction narrows on genuine meaning-similarity, not an
  artifact of an empty/trivial codebook.

## Bands (pre-registered BEFORE running)

`property_frac[ARM] = mean(FOUNDATION_RESOLVED over the 6 DEPENDENT_PROPERTY_KEYS)`.
`delta_reversed = property_frac[CORRECT] - property_frac[REVERSED]`.
`controls_clean = no_leak_ok AND n_combined_promoted_total==0 (all arms) AND arms_differ_ok`.

**HARD_PASS** requires ALL of:
`property_frac[CORRECT] >= 0.83` (>=5/6) AND
`property_frac[REVERSED] <= 0.17` (<=1/6) AND
`property_frac[PARTIAL] <= 0.17` AND
`property_frac[SEEN_NOT_CONSOLIDATED] <= 0.17` AND
`property_frac[ANTI_ARTIFACT_SCRAMBLE] <= 0.17` AND
`delta_reversed >= 0.5` AND `controls_clean`.
(META_RULE_L: analytically CORRECT is expected to land at exactly 1.0 and every other arm at
exactly 0.0 -- see Feasibility below -- so these floors carry >=65-percentage-point headroom
under the predicted values, comfortably above the 5%-of-band-width minimum margin.)

**HARD_FAIL** if ANY of:
`delta_reversed < 0.2` (no real order effect) OR
`property_frac[SEEN_NOT_CONSOLIDATED] >= 0.5` (mere exposure is sufficient -- NOT a
consolidation-gated mechanism; the honest "not the schema-scaffold mechanism" finding the task
asks to report if it occurs) OR
`property_frac[ANTI_ARTIFACT_SCRAMBLE] >= 0.5` (success is an order/pass-index artifact, not
content-driven) OR `not controls_clean`.

**MIDDLE_BAND**: anything between (e.g. CORRECT clears but one ablation arm shows partial
leakage above 0.17 but below 0.5 -- honest partial finding, name which axis leaked).

`HP_SCOPE`: HARD_PASS gates apply to all 5 arms' `property_frac` + the deltas above. No arm is
exempted (unlike sentinel-ablation cells, every arm here carries a specific, predicted value
that is itself the claim under test).

## Feasibility (hand-computed, THEORETICAL, pre-run)

`MIN_CONFIRM_GATE = PROMOTE_MIN_EXPOSURE = 8` (raised from the module default 4, deliberately,
so an item cannot bank via `consolidation_pass`'s intervening-pass rule before it ALSO has
enough exposure to satisfy the promotion floor -- see Addenda). With uniform per-tick flagging
and coherent context, an item first reaches `confirm_score=8` at local tick 8 of its block;
the Dumay-Gaskell intervening-pass rule defers banking to the NEXT pass (local tick 9,
`exposure=9 >= 8`, `consistency=1.0 >= 0.75`) -- banks + promotes at local tick 9.
`N_VISITS = 12` per concept-block gives 3 ticks of headroom past the earliest possible banking
tick. THEORETICAL@Dumay&Gaskell-2007-intervening-pass-rule +
`grounding_acquisition_loop.consolidation_pass` own gate arithmetic (verified directly against
that module's own self-test, which reproduces the identical n=8-exposure/1-intervening-pass
banking timing on its `repairtest` fixture).

## Compute architecture

(b) sequential-CPU with justification: 5 arms x 3 concept-blocks x 12 ticks = 180 total ticks,
each doing ONE tiny `fanout_two_hop` call (n_ent=5) + a `consolidation_pass`/
`update_prelim_and_generalize` pass over <=9 pending Library items (256-1024-dim vector ops).
No independent phase-point grid to batch; total estimated wall time under 30s. Matches the
"cell IS the substrate-primitive composition under test" exemption (sequential dependencies:
each tick's foundation-store state depends on the prior tick's consolidation outcome).

## Schema-vet declarations

```yaml
sweep_alignment_verdict: ALIGNED   # gate A -- no swept parameter axis; N_VISITS/MIN_CONFIRM_GATE/
                                    # K1/K2 fixed constants, uniform across all 5 arms
discriminating_fraction: 1.0       # gate B -- single regime; analytically situated at the
                                    # extremes (1.0 / 0.0) by construction (a genuine gate,
                                    # not a graded discriminator -- see HARD_PASS/HARD_FAIL bands)
composition_edges:                 # gate C
  - {from: gather_reason.ca3_relevance_gather, to: gather_reason.fanout_two_hop, verdict: SHAPE_MATCH}
  - {from: gather_reason.fanout_two_hop, to: three_tier_loop.ThreeTierLoop.encounter, verdict: SHAPE_MATCH}
  - {from: three_tier_loop.ThreeTierLoop.consolidate, to: hd_fact_store.HDFactStore.store, verdict: SHAPE_MATCH}
  # this cell's own NEW edge: fanout_two_hop's restrict_hop1_to = (GATHER-set) INTERSECT
  # (foundation-store-membership set), computed cell-locally each tick -- disclosed above,
  # not a modification to any reused organ (restrict_hop1_to is documented caller-supplied).
positive_control_arms: []          # gate D -- no PRIOR chain-grade metric on THIS exact
                                    # mechanism to reproduce (this cell IS the first test of the
                                    # curriculum-ordering mechanism); the organs composed
                                    # (ca3_relevance_gather / fanout_two_hop / consolidation_pass
                                    # / update_prelim_and_generalize) each carry their OWN
                                    # self-test as the positive-control-equivalent, exercised
                                    # directly in this cell's --self-test (real code path, not
                                    # re-derived); N/A per gate D scope (novel mechanism, no
                                    # prior atom at this test regime to reproduce).
functional_requirements:           # gate E
  - {requirement: "topical relevance is order-independent (meaning-similarity always available)",
     primitive: "hdlab.gather_reason.ca3_relevance_gather"}
  - {requirement: "comprehension composition requires the SPECIFIC prerequisite, restricted at REASON time",
     primitive: "hdlab.gather_reason.fanout_two_hop(restrict_hop1_to=GATHER ^ CONSOLIDATED)"}
  - {requirement: "mere exposure (seen) vs comprehension-gated encoding (consolidated) are separately observable",
     primitive: "hdlab.three_tier_loop.ThreeTierLoop.encounter(also_strict=...) / .answer()"}
  - {requirement: "combined-evidence promotion must not confound the strict-gate isolation",
     primitive: "hdlab.prelim_tier.update_prelim_and_generalize(cluster_min_members=999)"}
real_code_path_exercised: [KGStore, HDFactStore, Library, TierState, ScriptLibrary, RelationRegister, ThreeTierLoop]  # gate F.1
substrate_signature_checked: [KGStore(n_ent,n_rel,n_dim,generator), HDFactStore(n_dim,seed,use_index), ThreeTierLoop(foundation_store,seed_base,n_dim,relation)]  # gate F.2/F.3, base kwargs only
guard_baseline_validated: N/A      # no control-beats-baseline (POP-vs-RANDOM-shaped) guard in this cell
deterministic_seeding: true        # gate F.5 -- fixed integer seeds throughout, no hash()/list(set()) ordering
cell_chunked: false                # single deterministic pass per arm per mode, not a resumable multi-unit loop
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false           # estimated wall time << 15 min bar
defensive_error_checking: "passed start_marker+crash_diagnostic+no_bare_except; heartbeat exempted (est. wall time < 1 min)"
progress_logging: "print_flush_true"  # not mandated (timeout << 1800s) but implemented for auditability
arms_differ_verified: true         # asserted at runtime via per-arm (concept_status,property_status) digest comparison
final_metrics_atomicity: tmp_replace
crlb_n/a: "discrete gate-crossing (FOUNDATION_RESOLVED boolean per item), no Gaussian noise-floor metric; discriminator_reachability=true by hand-computed banking-tick arithmetic above"
baseline_in_band: EXEMPTED for REVERSED/PARTIAL/SEEN_NOT_CONSOLIDATED/ANTI_ARTIFACT_SCRAMBLE (deliberate ablation arms, each with its own predicted extreme value, not a graded baseline in [0.05,0.95])
calibration_check: "default_ok_for_this_regime -- NOVELTY_THRESH=0.15 (module default) never gates correctness here since cluster_min_members=999 structurally disables the combined-evidence path this threshold would otherwise calibrate; PROMOTE_MIN_EXPOSURE/PROMOTE_MIN_CONSISTENCY reused unmodified from grounding_acquisition_loop.py"
cardinality_ok: true               # EXPECTED_N_UNITS = 5 arms * 3 concepts * 12 visits = 180 ticks; verified via per-arm tick count == 36
```

## Modes

`--self-test`: tiny fixture, SAME real objects (KGStore/HDFactStore/Library/TierState/
ScriptLibrary/RelationRegister/ThreeTierLoop) at the SAME small scale as FULL (this cell has no
size axis to shrink -- 5 entities, <=9 Library items per arm is already minimal), running 3 of
the 5 arms (CORRECT / REVERSED / SEEN_NOT_CONSOLIDATED -- the three arms whose contrast is most
decisive) plus the GATHER topical-selectivity self-check. Asserts the predicted extremes. <5s.

`--smoke`: identical regime to FULL (DISCRIMINATOR-MUST-SURVIVE-SCALE option A -- this cell has
no separate smoke-vs-full size axis; smoke = full pipeline, all 5 arms, written to a
`_smoke`-suffixed dir, with an explicit discriminator-fires check
(`property_frac[CORRECT] - property_frac[REVERSED] >= 0.5`) gating readiness before FULL is
considered landed-equivalent.

(no flag) FULL: identical pipeline, canonical output dir.

`--timeout 120` (estimated wall time <30s, generous headroom).
