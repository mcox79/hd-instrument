# Pre-reg: causal enrichment probe-recovery, DEGREE-PRESERVING NULL v1
(causal_enrichment_probe_recovery_degree_preserving_null_v1)

Date: 2026-08-11. Cell: `experiments/exp_causal_enrichment_probe_recovery_degree_preserving_null_v1.py`.
Author: exp_dev. FORK of `experiments/exp_causal_enrichment_probe_recovery_v1.py` (commit 875598d08),
prereg `preregs/2026-08-11_causal_enrichment_probe_recovery_v1.md`. Fair-test REFINEMENT, not a new
question: the prior run's `verdict_msg` (`data/exp_causal_enrichment_probe_recovery_v1/metrics.json`)
was `HARD_FAIL` because its GLOBAL relation-label shuffle control did not collapse
(`shuffle=0.55` vs `baseline=0.2`, `shuffle_delta=0.35 > 0.05` tolerance) -- but the per-hop breakdown
(`conditions.enriched.hop1_rate=0.425` vs `conditions.shuffle.hop1_rate=0.300`) shows the failure was
concentrated at 2-hop (enrichment roughly doubled the causal-edge fraction --
`causal_edge_fraction.generous_baseline=0.1489` -> `generous_enriched=0.2698` -- so random 2-hop
"causal-typed, causal-typed" paths appear by chance once density is high enough), while a genuine
1-hop content signal survived (`+0.125` = `0.425 - 0.300`). Director's diagnosis: the global-label
shuffle is the WRONG null for isolating content from density; the correct null is DEGREE-PRESERVING
(configuration-model). This cell re-runs the SAME probe-recovery test with that corrected null.

## PRIOR-WORK CHECK (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring)
`bash tools/substrate_query.sh "degree preserving configuration model null causal graph recovery
density artifact"` -> top hit cosine=0.3232
(`notes/research_DRILL_uniform_criterion_SHARES_MATH_design_AAA3_definitive_load_bearing_axis_test_2026-06-13.md`:
"Secondary cross-check: configuration model. Preserves the exact degree sequence but randomizes
everything else. Cheaper to compute; serves as a second-opinion null."); 2nd hit cosine=0.2861
(`notes/research_substrate_self_map_2x_revival_full_store_mechanism_null_drill_2026-06-22.md`:
**"Uniform-relation-shuffle is the WRONG null model ... The right null ... is degree-preserving
rewire, not uniform-relation-type swap."**). **Both hits are at/near the cosine>0.30 threshold and
state the EXACT SAME methodological lesson this cell now applies, independently learned on a
different substrate-self-mapping cell 2026-06-22.** No prior cell tests THIS causal-enrichment
KB probe-recovery discriminator with a degree-preserving null -- the APPLICATION here is genuinely
novel, but the null-model CHOICE is corroborated by established codebase precedent, not an ad hoc
invention. Verdict: **novel application of an already-validated methodological pattern, not a
rediscovery.**

## WHAT CHANGED FROM v1 (explicit diff; everything else is REUSED, not re-authored)
1. **REMOVED**: the global relation-label permutation control (`shuffle` arm in v1).
2. **ADDED**: a DEGREE-PRESERVING (configuration-model) null, implemented as a per-relation-type
   PERMUTATION of the target column, restricted to causal-typed edges (`ENRICHED_CAUSAL_RELS`) in the
   ENRICHED edge list; non-causal edges pass through unchanged. See `## NULL MODEL` below for the
   exact algorithm + why it exactly preserves per-node per-relation causal degree.
3. **ADDED**: an ensemble of `N_NULL_SEEDS_FULL = 6` independent null draws (fixed int seeds, not
   `hash()`-derived), reporting mean + std, to average out Monte Carlo noise from a single draw.
4. **CHANGED gate scope**: HARD_PASS/HARD_FAIL/MIDDLE_BAND now gate on **hop-1-only** recovery gain
   (`enriched.hop1_rate - null.hop1_rate_mean`), not the combined hop<=2 `recovery_rate` v1 gated on.
   Rationale (director's diagnosis, confirmed by v1's own `hop1_rate`/`hop2_rate` breakdown): the
   density artifact concentrates at 2-hop; gating on hop-1 isolates the content claim from the exact
   failure mode v1's control caught.
5. **KEPT UNCHANGED, REUSED VIA DIRECT PYTHON IMPORT (not retyped)**: the 40 probes (`PROBES`), the
   CSKG-baseline load, the CauseNet-Precision regex extraction, the GO regulates-family extraction
   (`parse_gene_ontology`), `canon()`, the recovery function `_recover()` (1-2 hop, every-hop-causal-
   typed), the `CAUSAL_RELS_BASE`/`NEW_RELS`/`ENRICHED_CAUSAL_RELS`/`STRICT_CAUSAL_RELS` buckets, the
   RANDOM-EDGES control construction (`build_random_control_edges`, same seeds), `build_adjacency`,
   `compute_recovery`, `_edge_set_hash`, `causal_edge_fraction`. Reused via
   `import experiments.exp_causal_enrichment_probe_recovery_v1 as base` (REUSE, DO NOT MODIFY --
   precedent: `exp_bridge1_confirmation_test_v1.py` imports `exp_bridge1_governor_grounding_v1` the
   same way), so "same 40 probes + same enriched KB" is a structural guarantee (same code object), not
   a retyped-and-hopefully-identical copy. This satisfies the hard constraint: do NOT re-author probes
   or re-ingest sources; change ONLY the null model + hop analysis.
6. **KEPT**: the RANDOM-EDGES control (unchanged construction + seeds), reported at both hop-1 and
   hop<=2, still used as a non-gating validity check (`random_stays_low_ok`, tol=0.10, same as v1).

## NULL MODEL (exact algorithm)
`degree_preserving_shuffle(edges, causal_rels, seed)`:
1. Partition `edges` into `causal` (r in `causal_rels`) and `passthrough` (r not in `causal_rels`).
2. Group `causal` edges by relation type `r` (deterministic order: `sorted(by_rel.keys())`).
3. For each relation group: collect `sources = [s for s,o in group]`, `targets = [o for s,o in group]`.
   Permute `targets` with `np.random.default_rng(seed).permutation(len(targets))`. Re-pair
   `sources[i]` with `shuffled_targets[i]`.
4. Return `passthrough + all shuffled per-relation causal edges`.

**Why this exactly preserves "per-node per-relation causal out-degree" (and in fact BOTH out- and
in-degree)**: a permutation of one column preserves the MULTISET of values in that column exactly. So
for relation `r`, the multiset `{sources}` is bit-identical before/after (every node's out-degree for
relation `r` unchanged), AND the multiset `{targets}` is bit-identical before/after (every node's
in-degree for relation `r` unchanged) -- only WHICH source connects to WHICH target within relation
`r` is randomized. This is a stronger/exact guarantee than the general directed-configuration-model
stub-matching algorithm (which only preserves degree in EXPECTATION and needs self-loop/multi-edge
rejection handling) -- a column permutation is degree-preserving BY CONSTRUCTION, no rejection sampling
needed. Self-loops (`s==o` after shuffle) CAN occur by chance (a node coincidentally re-paired with
itself); these are counted (`n_self_loops_introduced`) but never affect recovery, since no probe's
subject equals its object and `_recover()`'s mid-node search explicitly excludes `n == obj`.
**This isolates "does having K causal edges of type r matter" (density; PRESERVED) from "does the
specific source->target content matter" (CONTENT; DESTROYED)** -- exactly the fair-test refinement
required.

Self-test invariant (the CRUX correctness check for this cell, mandatory): on a small real sample,
assert `sorted(sources_before) == sorted(sources_after)` and `sorted(targets_before) ==
sorted(targets_after)` PER RELATION, assert passthrough (non-causal) edges are byte-identical
before/after (untouched), and assert the shuffled edge SET differs from the original (the permutation
actually moved something, not an identity permutation).

## RECOVERY FUNCTION, CAUSAL_RELS, PROBES, BASELINE/ENRICHED/RANDOM CONSTRUCTION
Identical to `preregs/2026-08-11_causal_enrichment_probe_recovery_v1.md` (see that file for full
detail) -- reused verbatim via the import in item 5 above. Not restated here to avoid drift between two
copies of the same specification; the cell code is the single source of truth (imports, does not
retype).

## FALSIFIABLE PRE-REGISTERED BANDS (director-specified, verbatim from task; this section is the
authoritative gate -- HARD_FAIL is checked FIRST)
```
gain_hop1 = enriched.hop1_rate - degree_preserving_null.hop1_rate_mean   # PRIMARY GATE METRIC
gain_hop_le2 = enriched.recovery_rate - degree_preserving_null.recovery_rate_mean   # reported only, NOT gated
random_stays_low_ok = abs(random.hop1_rate - baseline.hop1_rate) <= 0.10   # same tol as v1

HARD_FAIL if: gain_hop1 < 0.05
HARD_PASS if (and only if, HARD_FAIL false):
    gain_hop1 >= 0.15  AND  random_stays_low_ok
MIDDLE_BAND: otherwise (gain_hop1 in [0.05, 0.15), or gain_hop1 >= 0.15 but random control broke)
```
**Honest interpretation, pre-committed both ways (per director's framing)**:
- HARD_PASS or MIDDLE_BAND-with-positive-gain -> genuine causal CONTENT signal survives a proper
  degree-preserving null even at 1-hop; CauseNet-scale general-domain causal DBs are CONTENT-ADDITIVE,
  not just density padding -- supports continued investment in general-domain causal source ingestion.
- HARD_FAIL (gain_hop1 < 0.05) -> the apparent v1 "genuine 1-hop signal" (+0.125 vs the WRONG global
  shuffle) does not survive the CORRECT null; CauseNet is largely redundant with CSKG's existing
  1-hop causal content once degree/density is controlled for -> redirects sourcing priority to a
  genuinely new register (Reactome/Rhea science KBs) or the corpora+reading path, per the director's
  explicit fallback framing. Report honestly regardless of which way it lands.

## COMPUTE ARCHITECTURE
(c) mixed with justification -- CPU-only, no GPU. Same DIRECTIONAL GATE / coverage-diagnostic class as
v1 (structural graph BFS-to-depth-2 recall proxy, not an HD-vector/KGE magnitude claim); reuses v1's
already-justified compute-proportionality argument. Storage strategy: `no_storage` (in-memory adjacency
dict per condition/seed, discarded after recovery computation).

**Wall-time budget (declared before running, MEASURED-anchored)**: v1's FULL run measured
`elapsed_s=195.5` for {source-parse (causenet regex ~70.4s one-time + go parse ~1.2s one-time +
baseline load, single-digit s) + 4 adjacency+recovery builds (baseline/enriched/shuffle/random, ~1.24-
1.6M edges each)} `MEASURED@data/exp_causal_enrichment_probe_recovery_v1/metrics.json:elapsed_s`.
Backing out the one-time parse cost (~85s), the 4 builds averaged ~27.5s each. This cell has 3 fixed
conditions (baseline/enriched/random, SAME as v1 minus shuffle) + `N_NULL_SEEDS_FULL=6` null-ensemble
builds = 9 builds total, same one-time parse. Budget: `85s + 9*27.5s ~= 332.5s ~= 5.5 min`, safely
under the 600s (10 min) INLINE-LOCAL foreground cap with ~4.5 min margin. `N_NULL_SEEDS_FULL=6` chosen
(exp_dev's call, per task autonomy) to balance ensemble-mean stability against this margin; if smoke
timing shows meaningfully lower per-build cost than budgeted, the actual FULL run has slack -- 6 stays
the committed count either way (pre-registered before running, not tuned post-hoc).

## MULTI-UNIT CHECKPOINT/RESUME (CLAUDE.md mandate: any cell looping over >1 seed unit MUST use
`tools/exp_checkpoint.py`)
The null-ensemble loop (`N_NULL_SEEDS` draws) is the one genuine seed axis this cell adds; wired via
`unit_key("null", seed)` / `completed_units` / `record_unit` / `load_units` (same API + import
convention as `exp_bridge1_confirmation_test_v1.py`: `sys.path` gets both `REPO_ROOT` and
`REPO_ROOT/tools`, then `from exp_checkpoint import ...`). A killed/hung FULL run resumes by skipping
already-recorded null seeds; resume order stays deterministic (fixed seed list, not
`hash()`/`list(set())`-derived). `baseline` / `enriched` / `random` remain single deterministic passes
(no seed axis; same as v1's own `cell_chunked: false` scope for those 3 arms) -- NOT checkpointed
per-unit (would be over-engineering a non-looped computation); only the null ensemble is.
`cell_chunked: true (scoped to the null-seed loop only)`.

## SCHEMA-VET DECLARATIONS
- `cardinality_ok`: `N_NULL_SEEDS_FULL=6` fixed at pre-reg time; `EXPECTED_N_UNITS=6` (null-seed loop
  only); verdict logic asserts `len(null_units) == EXPECTED_N_UNITS` before computing the ensemble
  mean, else `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `crlb_floor_computed`: N/A (same as v1) -> `crlb_n/a: "structural graph-path recall proxy, not a
  capacity/argmax-noise measurement"`.
- `baseline_in_band` (META_RULE_AG): EXEMPTED, same rationale as v1 (KB-coverage recall diagnostic;
  near-zero baseline recovery is the expected, diagnostically meaningful starting point, matching the
  disk-verified 1.39% causal-edge sparsity) -> `baseline_in_band_exempted: true`.
- `arms_differ_verified`: mandatory; hash every condition (baseline, enriched, random, each of the 6
  null seeds = 9 arms, 36 pairwise checks) via `_edge_set_hash` (reused from v1); assert zero
  collisions.
- `final_metrics_atomicity`: `tmp_replace` (single-shot final write, `metrics.json.tmp` ->
  `os.replace`); per-unit null-seed results additionally durable via `units.jsonl`
  (`record_unit`) as they complete, per the checkpoint mandate above.
- `except SystemExit: raise` before `except Exception` (not `BaseException`): yes, per template.
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: all true (heartbeat at
  each major stage: baseline loaded, causenet parsed, go parsed, each fixed-condition build, each null
  seed).
- `progress_logging`: N/A -- `timeout_s` well under the 1800s (30 min) mandatory threshold; heartbeats
  included anyway as defense-in-depth (INLINE-LOCAL, operator watching).
- `real_code_path_and_signature_preflight`: self-test constructs REAL objects at tiny scale (imports
  `base = experiments.exp_causal_enrichment_probe_recovery_v1`; calls REAL `base.load_baseline_edges`
  with a line cap, REAL `base._extract_causenet_pairs` with a line cap, REAL `base._extract_go_regulates`
  against the REAL `go.obo`); declared entrypoints: `base.load_baseline_edges`,
  `base._extract_causenet_pairs`, `base._extract_go_regulates`, `degree_preserving_shuffle`,
  `base.build_adjacency`, `base.compute_recovery`, `base._recover` (via `compute_recovery`),
  `exp_checkpoint.record_unit`/`load_units`. Degree-preservation invariant (per-relation source/target
  multiset unchanged) checked on the REAL small sample, not synthetic data.
- `deterministic_seeding`: true -- all RNG via `numpy.random.default_rng(<fixed int seed>)`; null-seed
  list = `[NULL_SEED_BASE + i for i in range(N_NULL_SEEDS)]` with `NULL_SEED_BASE=20260820` (fixed
  int, distinct from v1's `SHUFFLE_SEED`/`RANDOM_ENDPOINT_SEED`/`RANDOM_REL_SEED` to avoid any seed
  reuse ambiguity); `sorted()` used for all relation-group iteration order; no `hash()`-seeded RNG.

## TIMEOUT / RUN MODE
`--self-test`: tiny-scale (small line caps). Measured `MEASURED@this cycle, wall-clock `time`
around the --self-test invocation`: 30.7s real -- HIGHER than the naively-declared "<10s" target
(corrected here post-measurement, self-test has no downstream SLA gate so this is an honesty
correction, not a re-spec). Root cause: `hdlab.director_kb_bio_sources.parse_gene_ontology` is
lazy-imported inside `_extract_go_regulates`; the FIRST call in a fresh process pays a one-time
~20s cold-import cost (subsequent calls in the SAME process, e.g. the nested `run()` call inside
`self_test()`, complete in ~1.2-1.3s, matching v1's own measured GO-parse figure) -- this cell's
self-test calls `_extract_go_regulates` twice (once directly, once via the nested reduced `run()`),
so it pays the cold-import cost once and a warm ~1.3s parse once. Correctness (all assertions,
including the degree-preservation invariant) PASSED; only the wall-time estimate was optimistic.
`--run-mode smoke`: reduced line caps
(`baseline_line_cap=100000`, `causenet_line_cap=30000`, `go_max_terms=None` -- GO parse is already
cheap at ~1.2s full), `N_NULL_SEEDS_SMOKE=3`, all 40 probes retained (probes are cheap; a real
discriminator check needs the real probe set, not a reduced one) -- verifies the null-model code path
+ a plausible content-gap direction BEFORE spending FULL wall time; target <60s. FULL (default
`--run-mode full`): `N_NULL_SEEDS_FULL=6`, target <=5.5 min per the wall-time budget above; INLINE-
LOCAL foreground Bash call with explicit `timeout: 600000` (10 min cap) as safety margin. NOT
dispatched via `queue_add.sh` / any queue this cycle -- same NO ORIGIN PUSH constraint as v1 makes
remote dispatch mechanically unavailable, and `local_cpu_queue` is FULL-run-restricted per the
2026-07-01 USER lock; INLINE-LOCAL foreground is the correct, disciplined choice (same precedent as
v1's own dispatch).
