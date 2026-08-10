# Pre-reg: PRELIM middle tier + generalization-fed staged consolidation (crutch-fade, extends v1)

Filed by: exp_dev (Sonnet). Task per Director spawn prompt "Build + run the PRELIM middle tier +
generalization-fed staged consolidation for the crutch-fade Social IQa arc" +
`notes/design_prelim_tier_staged_consolidation_crutch_fade_2026-08-10.md` (the authoritative design
note -- crux, owned-organ pointers, HARD-PASS shape, ablations).

Prior-work check: `bash tools/substrate_query.sh "PRELIM tier staged consolidation generalization
CA3 DG cluster crutch fade"` -> see completion report for hit list; this is a direct, explicit
extension of the ALREADY-FILED design note (fde61f252) and the binary cell it supersedes
(74d310e11), not an independent rediscovery risk.

## What this cell tests (one sentence)

Does retaining sub-threshold crutch-fills in a low-trust PRELIM tier (pulled at re-encounter) PLUS
clustering related PRELIM traces by relation-family and letting COMBINED evidence cross the
still-STRICT native promote gate, produce MORE fade + climbing comprehension than the binary
promote-or-discard baseline, WITHOUT native fidelity collapsing -- at the SAME strict gate.

## Baseline being extended (verbatim numbers from commit 74d310e11, MEASURED, reproduced fresh in
this same run's `gap_driven` arm for apples-to-apples comparison, not hardcoded)

`data/exp_crutch_fade_social_iqa_v1_full_pme8_hubpen/metrics.json`: promote_min_exposure=8,
score_mode=hub_penalized, fire_rate rel-drop 0.1244 (0.3378->0.2958), comprehension lift +0.012
(gap_driven 0.4096 vs bow_final 0.3976 -- MEASURED@that file's checkpoints[-1].accuracy), 90/6768
promoted, consolidation_fidelity_ok=True.

## Owned organs reused (wire-don't-island; see design note for full citations)

- `hdlab/grounding_acquisition_loop.py`: `Library`, `consolidation_pass` (native single-item
  promotion, UNCHANGED, reused verbatim for the `gap_driven` baseline arm and for the 3-tier's
  single-item native leg), `schema_consistency_split_half`, `_vote_margin` (reused directly, by
  hand, over a SEPARATE always-PENDING `Library` instance -- see "PRELIM accumulation" below; no
  modification to `grounding_acquisition_loop.py` itself).
- `hdlab/hd_fact_store.py::HDFactStore` -- reused unmodified. PRELIM = a SEPARATE `HDFactStore`
  instance, every fact stored at `trust="TRUST_LOW"` (the module's existing trust ladder already
  has this level; no schema change). NATIVE (generalization-fed) = a second, separate `HDFactStore`
  instance receiving both single-item AND cluster-combined promotions.
- `hdlab/script_grain_acquisition_loop.py::ScriptLibrary.match_or_spawn` /
  `build_instance_register` -- reused unmodified as the CA3/DG clustering organ. Register =
  `build_instance_register(agent=concept_a, patient=concept_b, trigger_cat=relation_family(pk),
  consequent_cat="OUTCOME_"+label)`. `relation_family` buckets a CSKG driving pair's own relation
  label (already present in the loaded CSKG index) by stripping its `/r/` `at:` `mw:` namespace
  prefix (MEASURED@shard sample: 33 distinct relation types in shard 0 alone -- `/r/LocatedNear`,
  `at:xAttr`, `at:xWant`, `at:xEffect`, `at:xNeed`, `mw:MayHaveProperty`, `at:xReact`, `at:xIntent`,
  `/r/CapableOf`, `at:oWant`, ... -- a well-bounded, semantically-meaningful clustering key, NOT an
  invented taxonomy). TRIGGER/CONSEQUENT category tags are the STABLE per-type signal (2 of 4 role
  binds); AGENT/PATIENT (the specific concept pair) are the varying per-instance fillers -- this
  reproduces the module's own self-test shape (same-type-different-fillers matches strongly,
  different-type does not), so no modification needed.
- `hdlab/learner/` MDL gate -- deliberately NOT wired in v1 (disclosed deviation, below).
- `hdlab/predictive_coding.py` -- unchanged (the FLAG gate stays the existing BoW-margin adaptive
  threshold; PRELIM/generalization is entirely downstream of an already-flagged gap).
- `experiments/exp_crutch_fade_social_iqa_v1.py` -- EXTENDED in place (same file, same
  ANCHOR_NAME), not forked. The existing 5 arms (`bow`, `never_crutch`, `always_crutch`,
  `gap_driven`, `scramble_crutch`) are UNCHANGED, byte-identical code paths -- `gap_driven` is the
  baseline arm to beat, reproduced fresh every run, not cited from history.

## Disclosed deviation: MDL gate (`hdlab.learner`) not wired in v1

The design note names `hdlab/learner/` as a candidate organ for schema-worthiness gating (parallel
to `script_grain_acquisition_loop.script_consolidation_pass`'s optional `mdl_gate_fn` hook). This
build uses the CONJUNCTIVE (exposure >= promote_min_exposure) AND (|vote_margin| >=
promote_min_consistency) combined-evidence gate as the schema-worthiness check (identical SHAPE to
the existing single-item native promote gate, applied at cluster grain) -- this is what HARD-PASS
criterion 4 (below) actually asks for and keeps the comparison to the single-item gate apples-to-
apples. An MDL two-part-code gate on TOP of this is a natural v2 stretch (`mdl_gate_fn` is already
plumbed in `script_consolidation_pass` for exactly this), scoped out here under the Autonomy grant
to keep this build's scope achievable in one cycle; noted as the "one-line next step" candidate.

## Disclosed deviation: DG pattern-separation (`hdlab/dg_pattern_separation.py`) not wired, with a
smoke-time tripwire

`hdlab/dg_pattern_separation.py` exists because `ScriptLibrary.match_or_spawn`'s CA3-only attractor
CATASTROPHICALLY OVER-MERGED at 195-way scenario cardinality in MCScript2.0
(`exp_mcscript2_real_benchmark_validation_v1`, HARD_FAIL, mean item_purity ~0.19-0.20). This cell's
cluster cardinality is MUCH lower (~33-40 distinct CSKG relation families vs 195 script types) and
the two dominant clustering signals (TRIGGER_ROLE/CONSEQUENT_ROLE content vectors) are independent
hashlib-seeded FHRR draws per relation-family STRING, not narrative-derived registers with
plausible near-duplicate structure -- lower a-priori collision risk, but not zero, and this is a
KNOWN failure class for this exact organ. Mitigation (not a full DG-separation wire, a cheap
tripwire): (a) `calibrate_novelty_threshold` (already-owned) is run against synthetic same-family
vs different-family register pairs before the run to pick `novelty_thresh`, logged; (b) smoke
reports `n_clusters` vs `n_distinct_relation_families_seen` -- if `n_clusters < 0.5 *
n_distinct_relation_families_seen` (majority over-merge), that is a BLOCK_DISPATCH condition
(re-spec `novelty_thresh` or escalate to wiring `dg_pattern_separation` before FULL, do not ship
past it). Self-test also directly asserts two different relation-family registers built from this
cell's own token vocabulary do NOT match at the calibrated threshold.

## COORDINATOR REFINEMENT (mid-build, DISK-VET'd sibling diagnosis, commit e9ee736ec) -- read before
the bands below

The sibling promotion-fault diagnosis (pme=4, same hub_penalized scoring) found: fade becomes
dramatic at the low gate (fire-rate 0.3378->0.1515, rel-drop 0.5515) but comprehension stays flat
(+0.009) -- NOT a storage/use-quality fault. `retrieval_use_diagnostic` (already-owned, reused
unmodified by this cell) isolated the cause: `retrieval_hit_rate` 0.446-0.538 -- **the crutch
(CSKG) itself only reaches the GOLD answer's concepts for ~45-54% of the gaps it fires on**;
`use_quality_given_hit` is fine (0.68-0.80). This means comprehension has a COVERAGE-CAPPED ceiling
independent of consolidation quality -- a perfect consolidation architecture cannot push overall
comprehension past that ceiling. Consequence for THIS cell's bands:

- Overall `comprehension_lift_3tier@100% vs BoW` is CONFOUNDED by crutch coverage and is now a
  REPORTED metric, not a blocking HARD-FAIL trigger.
- ADDITIONALLY compute a COVERAGE-CONTROLLED subset: `dev_crutch_covered` = dev items that are
  gap-flagged (BoW margin < GATE_THRESH) AND `crutch_candidate_scores(item)[gold_idx] > 0`
  (checkpoint-independent -- a property of the static CSKG index + item content, computed once at
  Stage-0, same score_mode=hub_penalized as the run). Report `coverage_rate = n_covered /
  n_gap_flagged` (should land near the sibling's 0.45-0.54). For EVERY arm, at every checkpoint,
  ALSO report accuracy restricted to `dev_crutch_covered` (`accuracy_covered`), alongside overall
  accuracy, and the `always_crutch` arm's accuracy on that same subset as the CEILING reference
  (not BoW) -- this is the closest-to-fair comprehension read, isolating consolidation quality from
  the coverage bottleneck.
- This cell's PRIMARY deliverable reframes to the ARCHITECTURAL wins the prelim tier is actually
  FOR: fade grows at the STRICT gate (criterion 1) while fidelity is preserved (criterion 2,
  something the sibling's OWN pme=4 fix does NOT achieve -- lib_acc 0.347 < cru_acc 0.373 there),
  combined-evidence promotion fires cleanly (criterion 4), and the two ablations behave (criteria
  6-7). Comprehension (overall AND coverage-controlled) is reported prominently, cited, and used as
  a SOFT/advisory regression check (criterion 3, revised below) rather than a hard blocking gate.
  Retrieval coverage itself is explicitly OUT OF SCOPE for this build (a separate, already-flagged
  next build) -- this cell must not re-scope into fixing coverage; it isolates the consolidation
  architecture as the one clean variable.

## Mechanism: the 3 tiers

**Tier 0 CRUTCH** (`crutch_candidate_scores` / `idx`) -- unchanged.

**Tier 1 PRELIM** -- a SEPARATE, permanently-PENDING `Library` instance (`prelim_lib`) fed the SAME
`(pair_key, episode_id, "POS", context_vec)` calls as the existing `real_lib` during
`process_exposure_slice` (so it never terminalizes -- `Library.flag()`'s existing "reject once
non-PENDING" guard never fires against it, by construction, since its items' `.status` is never
mutated away from PENDING; NO modification to `grounding_acquisition_loop.py`). At every checkpoint,
for every `prelim_lib` item with `>= MIN_CONFIRM` (4, reused constant) traces AND
`schema_consistency_split_half(traces) >= 0.10` (reused default `schema_thresh`) AND a decidable
vote (`_vote_margin` sign != 0): RETAIN into a `TRUST_LOW` `HDFactStore` (`prelim_store`) if not
already live there (idempotent). This is the SAME bar as the existing BANK step
(`consolidation_pass`'s own schema-gate), just computed by hand against a Library that is never
allowed to reach a terminal GROUNDED/ESCALATED state -- so items keep ACCUMULATING evidence forever
(no discard), the literal "retain, don't discard" fix the binary cliff lacked.

**Re-encounter PULL (the fade lever)**: the 3-tier arms consult LIBRARY (native, strict), then
PRELIM (`prelim_store`), THEN crutch -- so a gap whose driving pair is PRELIM-covered resolves
WITHOUT touching the live crutch. Tag: `PRELIM_RESOLVED` (new, alongside the existing
`BOW_RESOLVED`/`LIBRARY_RESOLVED`/`CRUTCH_RESOLVED`/`ABSTAINED`).

**Tier 2 NATIVE (generalization-fed)** -- every PRELIM-eligible pair is ALSO registered (once, on
first eligibility, sticky membership) into a `ScriptLibrary` via `match_or_spawn`, clustering by
relation-family. At every checkpoint, for every cluster with `>= CLUSTER_MIN_MEMBERS` (3) distinct
member pairs: pull each member's OWN raw traces from `prelim_lib`, concatenate, and evaluate the
IDENTICAL gate the single-item native path uses -- `combined_exposure >= promote_min_exposure` (8)
AND `abs(combined_vote_margin) >= promote_min_consistency` (0.75) -- **the gate itself is never
loosened, only the evidence pool is COMBINED across members sharing a schema.** A FIDELITY GUARD
additionally requires a member's OWN vote (if it has one) not OPPOSE the cluster's majority label
before that member is force-promoted under the cluster's label (protects HARD-PASS 5). Cluster-
promoted facts are tagged `source="combined_evidence_cluster"` (glass-box recoverable from the
`SOURCE` role) vs `source="cskg_crutch_real_single"` for single-item promotions -- lets fidelity be
measured PER PROMOTION PATH, not just aggregate.

## New arms (existing 5 UNCHANGED; these 4 are additive)

- `gap_driven_3tier` -- LIBRARY(single+cluster) -> PRELIM -> CRUTCH -> ABSTAIN. THE full mechanism.
- `gap_driven_3tier_no_generalization` -- LIBRARY(single-item ONLY, literally `real_store`, the
  SAME store `gap_driven` uses) -> PRELIM -> CRUTCH -> ABSTAIN. Ablation A: retain+pull, no
  clustering feed.
- `gap_driven_3tier_no_pull` -- LIBRARY(single+cluster) -> CRUTCH -> ABSTAIN (PRELIM never
  consulted, though it and the cluster machinery still run in the background). Ablation B: retain
  without pull.
- `scramble_crutch_3tier` -- mirrors `gap_driven_3tier` on the scramble side (own `prelim_lib` /
  `prelim_store` / `script_lib` / cluster-fed native store, fed via the SAME deterministic
  wrong-partner draw the existing `scramble_crutch` arm already uses). The load-bearing control for
  the NEW mechanism specifically (not just the old crutch-retrieval control).

`EXPECTED_N_ARMS = 9`. `arms_differ_exempted`: `[["bow","never_crutch"]]` (both routes are
IDENTICAL by construction -- `never_crutch` IS bow-only; this was already true, silently, in the
baseline cell's own arms-must-differ check and is now explicitly declared rather than left
undisclosed).

## Compute architecture

Class (b) sequential-CPU with justification (unchanged from the base cell -- symbolic dict lookups
+ vote-counting, no matmul-heavy substrate primitive). PRELIM eligibility scan is O(n_pending_pairs)
per checkpoint (cheap: up to ~7000 pairs x 5 checkpoints, each a `schema_consistency_split_half`
over a handful of D=256 traces). Cluster registration is O(1) `match_or_spawn` calls against a
codebook bounded by ~33-40 relation families (NOT by item count), so `iterative_attractor` stays
cheap even as membership grows. MEASURED@baseline: 5-arm FULL (33410 train / 1954 dev) = 197s.
HYPOTHESIZED (pre-smoke): 9-arm 3-tier FULL, same data scale, order 400-700s (roughly linear in
arm count plus PRELIM/cluster bookkeeping) -- to be MEASURED at smoke and confirmed before FULL.
Storage: PRELIM/NATIVE-generalization stores are flat keyed lookups (no chained composition),
`no_composition`/sharded-by-construction, same as the base cell.

## Smoke-scale change (disclosed)

Base cell's default `--smoke` (train_cap=3000/dev_cap=250) MEASURED ZERO native promotions in prior
history (too small even for the single-item gate). This 3-tier smoke needs the discriminator (PRELIM
retain-rate, cluster combined-evidence promotion) to actually FIRE (SMOKE-MUST-FIRE-DISCRIMINATOR).
Bumping `SMOKE_TRAIN_CAP` 3000->15000 and `SMOKE_DEV_CAP` 250->400 (matching the `--diag` scale that
MEASURED real promotions in the prior cycle, still << FULL's 33410/1954, still at FULL CSKG-index
scale per DISCRIMINATOR-MUST-SURVIVE-SCALE). Old smoke output path preserved via `--out-tag`.

## Pre-registered CAN-FAIL bands (this cell's TOP-LEVEL verdict answers the 3-TIER question; the
binary `gap_driven` arm's own verdict is still computed and reported as `binary_baseline_verdict`,
informational, not the headline)

**HARD-PASS (ALL required):**
1. FADE GROWS at the SAME strict pme (8): `tier_fire_drop_rel(gap_driven_3tier) >=
   binary_fire_drop_rel(gap_driven, this run) + 0.05` (absolute margin over the SAME-run binary
   baseline, not the historical 0.124 figure -- avoids any cross-run config drift).
2. FIDELITY PRESERVED (both new tiers): at every checkpoint where `n>=20`,
   `LIBRARY_RESOLVED_acc >= CRUTCH_RESOLVED_acc - 0.03` AND `PRELIM_RESOLVED_acc >=
   CRUTCH_RESOLVED_acc - 0.03` for `gap_driven_3tier`.
3. COMPREHENSION DOES NOT REGRESS, COVERAGE-CONTROLLED (revised per coordinator refinement above --
   overall comprehension is reported, not gated, since it is coverage-capped independent of
   consolidation quality): on the `dev_crutch_covered` subset, `comprehension_lift_3tier_covered@100%
   >= comprehension_lift_binary_covered@100% - 0.01` (3-tier not worse than binary where the crutch
   COULD help, small noise tolerance). Overall (uncontrolled) lift and the `always_crutch` ceiling
   comparison are computed and reported at every checkpoint regardless of this gate's outcome.
4. COMBINED-EVIDENCE PROMOTION WORKS: `combined_evidence_promotion_count > 0` AND (when `n>=5`
   `promo_source=="combined_evidence_cluster"` resolved items exist) their accuracy `>=
   CRUTCH_RESOLVED_acc - 0.05`.
5. CONTROLS HOLD: `scramble_crutch_3tier` within BoW +/-0.02 at every checkpoint; never beats
   `gap_driven_3tier`; `no_regression` (`gap_driven_3tier_acc >= bow_acc - 0.02`) at every
   checkpoint.
6. ABLATION A (no-generalization must not beat full): `gap_driven_3tier_acc@100% >=
   no_generalization_acc@100% - 0.005` AND (structural, asserted) `no_generalization`'s
   `combined_evidence_promotion_count == 0`.
7. ABLATION B (no-pull must show less fade than full): `tier_fire_drop_rel(gap_driven_3tier) -
   tier_fire_drop_rel(no_pull) >= 0.02`.

**HARD-FAIL (ANY ONE):**
- `tier_fire_drop_rel(gap_driven_3tier) < binary_fire_drop_rel` (3-tier fades LESS than binary --
  regression on the core claim).
- Fidelity collapses at either tier at any `n>=20` checkpoint (criterion 2 violated).
- COVERAGE-CONTROLLED comprehension regression: `comprehension_lift_3tier_covered@100% <
  comprehension_lift_binary_covered@100% - 0.03` (3-tier meaningfully WORSE than binary specifically
  where the crutch could help -- the coverage-controlled, apples-to-apples regression signal;
  overall/uncontrolled comprehension going flat is NOT by itself a HARD-FAIL trigger per the
  coordinator refinement above).
- Scramble ties/beats `gap_driven_3tier`, or exceeds BoW+0.02, at any checkpoint.
- `combined_evidence_promotion_count == 0` (the crux mechanism never fires at all).
- `no_generalization`'s `combined_evidence_promotion_count != 0` (ablation-isolation implementation
  bug -- the "no generalization" arm leaked cluster promotions).
- Smoke-time cluster-cardinality tripwire fires (`n_clusters < 0.5 * n_distinct_relation_families`)
  and is not resolved before FULL dispatch.

**MIDDLE_BAND**: any HARD-PASS criterion misses while no HARD-FAIL trips -- reported with the exact
criteria that missed (never rounded up to HARD_PASS, never silently downgraded to HARD_FAIL).

## CELL-TEMPLATE MANDATORY (SCHEMA-VET checklist, additive to the base cell's own)

- `arms_differ_verified`: 9-arm hash-differ, `arms_differ_exempted=[["bow","never_crutch"]]`
  (declared, not silent).
- `final_metrics_atomicity`: tmp_replace (unchanged).
- `except SystemExit: raise` before `except Exception` (unchanged, no bare except anywhere new).
- `crlb_n/a`: unchanged rationale (symbolic KB-lookup + vote-count pipeline).
- `HP_SCOPE`: `{dev_checkpoint_eval: [tier_fire_drop, tier_comprehension_lift,
  tier_scramble_control, tier_consolidation_fidelity, combined_evidence_promotion,
  ablation_underperformance]}`.
- `cardinality_ok`: `EXPECTED_N_CHECKPOINTS=5`, `EXPECTED_N_ARMS=9`.
- Per-unit failure-class instrumentation: unchanged (no bare except anywhere in new code).
- `calibration_check`: `adaptive_with_discriminator_gate` (GATE_THRESH unchanged) PLUS
  `novelty_thresh` calibrated via `calibrate_novelty_threshold` against this cell's own synthetic
  same-family/different-family register pairs, logged (not hand-tuned for a pass).
- `real_code_path_exercised`: self-test constructs the REAL `Library`, `HDFactStore`,
  `ScriptLibrary`, `build_instance_register`, `match_or_spawn` at tiny synthetic scale -- verifies
  (a) sub-threshold retain-without-promote, (b) re-encounter PULL resolves via PRELIM not CRUTCH,
  (c) multiple related sub-threshold pairs combine across the SAME cluster to cross the strict
  native gate when no single one does, (d) the fidelity guard blocks a member whose own evidence
  opposes the cluster majority, (e) two distinct relation-family registers do NOT merge at the
  calibrated `novelty_thresh`.
- `progress_logging`: `print_flush_true` (unchanged; per-checkpoint heartbeat already present).

## Dispatch

Same class as the base cell -- light CPU-only, run foreground-to-completion (not queued), smoke
first. Multi-seed FULL: 3 seeds (7, 13, 19; only affects `HDFactStore`/`EventBundleCodec` role-key
codebook seeding -- SIQa exposure/dev order is file-order-deterministic regardless of seed, so this
is a nondeterminism/robustness check, not an expected-high-variance sweep). Resumability
granularity: per-seed (each single-seed FULL run is a few minutes, well inside one foreground call;
commit immediately after each seed's metrics land, before starting the next -- this is the
"per-unit" the durability discipline binds to here, given the measured wall-time makes finer-grained
mid-run checkpointing disproportionate per compute-proportionality).
