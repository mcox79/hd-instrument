# Pre-reg: semantic-embedding clustering key (crutch-fade v2, ONE-VARIABLE fork of v1's 3-tier cell)

Filed by: exp_dev (Sonnet). Task per Director spawn prompt "test whether swapping the near-concept
SWEEP clustering KEY to a SEMANTIC-EMBEDDING key flips the two fidelity HARD_FAIL flags in the
already-built three-tier knowledge loop, on the SAME real benchmark it failed on" +
`notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md` (the authoritative
design/audit doc; "SMALLEST FIRST EXPERIMENT" section is this cell's direct spec).

Prior-work check: `bash tools/substrate_query.sh "semantic embedding clustering key locality
sensitive hash CA3 DG script grain near-concept sweep prelim tier consolidation"` -> top hit
cosine=0.3076 (`T3/locality_sensitive_hashing`, a general math-primitive atom already in the
substrate-KB, appropriately REUSED here as the bucketing technique, not a prior cell). Hit #3
(cosine=0.2607, `semantic_concept_learning`, SHELVE/ISLAND) is an unrelated concept-learning cell.
No prior cell implements this exact semantic-clustering-key fix for the crutch-fade 3-tier sweep --
genuinely novel application of an owned technique, not a rediscovery.

## What this cell tests (one sentence)

Does replacing ONLY the CA3/DG near-concept clustering KEY -- from `relation_family(idx, pk)` (the
CSKG relation-TYPE label, disk-diagnosed as "intrinsically too coarse" in
`data/exp_crutch_fade_social_iqa_v1_3tier_seed7/metrics.json`) to `semantic_relation_key(idx, pk)`
(an OWNED, from-scratch, locality-sensitive-hash bucket over the pair's own two concept strings'
char-trigram HD embeddings) -- flip the two v1 HARD_FAIL flags (HP2 `tier_fidelity_ok`, HP3
`comp_lift_covered`) on the SAME real Social IQa dev set + SAME real 1.15M-edge CSKG crutch, holding
every other design element byte-identical?

## Baseline being extended (verbatim numbers, MEASURED, the run this cell must beat)

`data/exp_crutch_fade_social_iqa_v1_3tier_seed7/metrics.json` (seed=7, hub_penalized, pme=8, FULL
33410 train / 1954 dev): verdict=HARD_FAIL. HP1=True (tier_fire_drop_rel=0.3636 vs binary=0.1242).
**HP2=False**: tier_fidelity_checks show LIBRARY_RESOLVED acc < CRUTCH_RESOLVED_acc-0.03 at 3 of 4
measured checkpoints (frac 0.1/0.25/0.5; frac 1.0 barely OK at acc=0.357 vs cru_acc-0.03=0.339).
**HP3=False**: comp_lift_covered tier=0.3662 < binary=0.3775 (binary - 0.01 = 0.3675; tier misses by
0.0013). HP4=True (combined_evidence_promoted_n=403, combined_acc=0.356 n=163, cru_acc=0.369, within
-0.05). HP5=True. HP6=True. **HP7=False** (ablationB fire_drop=0.3606 vs tier=0.3636, gap=0.0030 <
0.02 required). Root cause (code-comment-disclosed, `relation_family` docstring in v1): only
`n_clusters=5` (`n_clusters_eligible_size=4`) formed by checkpoint 100 across the ENTIRE 1.15M-edge
CSKG-connected PRELIM population -- CSKG relation-TYPE label spans huge, semantically heterogeneous
swaths of common sense, so "same relation family" != "same schema."

## ONE-VARIABLE change (everything else held byte-identical to v1)

`experiments/exp_crutch_fade_social_iqa_v2_semantic_cluster_key.py` (fork of
`experiments/exp_crutch_fade_social_iqa_v1.py`, same file otherwise). The ONLY functional line
changed inside `update_prelim_and_generalize` (the CA3/DG cluster-registration call site):

```
fam = relation_family(idx, pk)          # v1
fam = semantic_relation_key(idx, pk)    # v2 (THE one-variable change)
```

plus the matching novelty-threshold-calibration vocabulary sample in `run()` (downstream
bookkeeping of the SAME key swap -- calibrates `calibrate_novelty_threshold` against the new key's
own bucket vocabulary instead of the old relation-family vocabulary; not a second variable).

`semantic_relation_key(idx, pk)`: encodes the pair's two concept strings with
`hdlab.char_trigram_encoder.CharTrigramEncoder` (registry row 12 `char_trigram_encoder`, WIRED,
OWNED, zero external model / zero borrowed vectors -- 14+ existing consumers), bundles (sums) the
two encodings, projects onto `SEM_KEY_N_BITS=6` deterministic (hashlib-seeded, PROT-023/F.5
compliant) random hyperplanes (Charikar 2002 SimHash locality-sensitive hashing), and returns the
resulting sign-bit-pattern as a `sem_<bits>` bucket-label string. `idx` is accepted for call-site
parity but unused (the key is a property of the CONCEPT PAIR, not of which CSKG edge/relation
happens to connect them -- no `UNKNOWN` fallback class, unlike `relation_family`).

**Encoder choice (per HARD CONSTRAINT, disclosed):** `char_trigram_encoder`, NOT
`scale_win_tinytransformer_encoder` (registry row 3). The tiny-transformer encoder lives inside
`experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py` as a `torch.nn.Module` requiring a
reloaded MLM-training checkpoint (`ckpt_seed_7.pt`) + its own tokenizer -- an exp-cell-internal,
`TRAPPED_SHARED` asset (registry `kind: exp-cell`, not `kind: hdlab-module`), not a portable
importable module for a light CPU-only symbolic cell (torch model load + checkpoint-file
remote-portability risk). The design audit's own smallest-first-experiment spec explicitly names
char-trigram as the fallback "if [the tiny-transformer encoder is] not readily composable" -- it is
not, so this fork takes that fallback, per Autonomy grant.

**Everything else held fixed (verified unchanged in the diff):** `HUB_DEGREE_THRESH=500`,
`CLUSTER_EXPOSURE_MULTIPLIER=4`, `PROMOTE_MIN_EXPOSURE=8` (CLI default, passed explicitly),
`PROMOTE_MIN_CONSISTENCY=0.75`, `CLUSTER_MIN_MEMBERS=3`, the 9-arm/5-checkpoint design, the frozen
1,954-item dev set, the real `data/cskg_foundation_v1` 1.15M-edge CSKG crutch, `score_mode=
hub_penalized`, seed=7. `relation_family()` itself is RETAINED unmodified in the file (reference/
diagnostic only, no longer called from the live path).

**New addition (HARD CONSTRAINT, not a second experimental variable):** resumable per-unit
checkpointing via `tools/exp_checkpoint.py` over the (checkpoint, arm) dev-eval grid (45 units) --
see "Resumability" section below. This is infra hardening, not a mechanism change.

## Owned organs reused verbatim (wire-don't-island)

Identical list to `preregs/2026-08-10_crutch_fade_prelim_tier_staged_consolidation_v1.md`:
`hdlab/grounding_acquisition_loop.py` (`Library`, `consolidation_pass`, `schema_consistency_
split_half`, `_vote_margin`), `hdlab/hd_fact_store.py` (`HDFactStore`), `hdlab/
script_grain_acquisition_loop.py` (`ScriptLibrary.match_or_spawn`, `build_instance_register`,
`calibrate_novelty_threshold` -- ALL unmodified; only the STRING fed into `build_instance_register`'s
`trigger_cat` argument changes, per the one-variable change above). NEW for v2: `hdlab/
char_trigram_encoder.py` (`CharTrigramEncoder`), used ONLY inside the new `semantic_relation_key()`.

## Disclosed deviation: `mdl_gate_fn` hook still NOT wired (unchanged from v1)

Same disclosed deviation as v1's own pre-reg. Per the design audit's own contingency ("if smoke
shows n_clusters still collapsing toward the degenerate 2-cluster case... you may add [mdl_gate_fn]
as arm 2... before concluding a new clustering design is needed"), this is the FIRST lever to try
if v2 also HARD_FAILs -- deliberately NOT added in this cycle to keep the fork to exactly one
variable and get a clean read on the clustering-key hypothesis in isolation.

## Compute architecture

Class (b) sequential-CPU with justification (unchanged from v1 -- symbolic dict lookups +
vote-counting + one cheap char-trigram encode per concept-pair-first-registration, no matmul-heavy
substrate primitive; `CharTrigramEncoder.encode` is microseconds per call per its own docstring and
is cached per-trigram, so the added encode cost is negligible next to the existing CSKG-lookup /
Library-bookkeeping cost). MEASURED@smoke (this run, SMOKE_TRAIN_CAP=15000/SMOKE_DEV_CAP=400):
125.06s wall, all 5 checkpoints. MEASURED@v1 FULL (33410/1954, same arms/checkpoints): 340.67s wall.
HYPOTHESIZED (pre-FULL): v2 FULL should land in the same order of magnitude (300-450s), since the
only added per-registration cost is one extra `CharTrigramEncoder.encode` call pair per NEWLY-
eligible PRELIM item (bounded by `n_prelim_pending_items`, not by dev-set size) -- to be MEASURED
and reported in the completion report.

## Resumability (HARD CONSTRAINT)

`tools/exp_checkpoint.py` (`unit_key`, `completed_units`, `record_unit`, `load_units`) wired over
the `(checkpoint_index, arm)` dev-eval grid (45 units: 5 checkpoints x 9 arms). Each unit's dev-eval
`rows` are recorded to `<output_dir>/units.jsonl` the instant that arm's evaluation finishes at that
checkpoint; on resume, already-recorded units are loaded and skipped rather than recomputed.
**Disclosed scope limit:** the SEQUENTIAL exposure + consolidation state-building (`process_
exposure_slice` / `consolidation_pass` / `update_prelim_and_generalize`, once per checkpoint, shared
mutable state across all 9 arms) is NOT itself checkpointed -- it always reruns from checkpoint 0 on
a resumed process, matching v1's own pre-reg precedent ("Resumability granularity: per-seed...
finer-grained mid-run checkpointing disproportionate per compute-proportionality" at this measured
wall-time scale). Serializing the mutable `Library`/`HDFactStore`/`ScriptLibrary` objects to make
state-building itself resumable is out of scope for a one-variable diagnostic rebuild. What this
DOES buy: a killed/hung run resumes without re-scoring already-completed (checkpoint, arm) x
1954-dev-item grids, and every completed unit is durable on disk independent of the final
`metrics.json` write. `resumable_per_unit: true` / `resumable_unit_grain: "checkpoint_x_arm"` /
`resumable_units_recorded: <int>` logged in metrics.

## Pre-registered CAN-FAIL bands (REUSES v1's own pre-registered shape verbatim, per task
instruction -- same HP1-HP7 / HARD-FAIL criteria, same `preregs/2026-08-10_crutch_fade_
prelim_tier_staged_consolidation_v1.md` definitions; NOT re-litigated here except to restate the
two flags this experiment's headline question is about)

**HARD-PASS (ALL required, unchanged from v1):**
1. HP1 fade grows at the same strict pme (8): `tier_fire_drop_rel >= binary_fire_drop_rel + 0.05`.
2. **HP2 (THE headline flag)** fidelity preserved at both new tiers: at every checkpoint n>=20,
   `LIBRARY_RESOLVED_acc >= CRUTCH_RESOLVED_acc - 0.03` AND `PRELIM_RESOLVED_acc >=
   CRUTCH_RESOLVED_acc - 0.03` for `gap_driven_3tier`.
3. **HP3 (THE headline flag)** coverage-controlled comprehension no-regression:
   `comp_lift_tier_covered@100% >= comp_lift_binary_covered@100% - 0.01`.
4. HP4 combined-evidence promotion works + fidelity: `combined_evidence_promotion_count > 0` AND
   (n>=5) `combined_evidence_cluster` accuracy `>= CRUTCH_RESOLVED_acc - 0.05`.
5. HP5 controls hold: 3-tier's own scramble arm within BoW +/-0.02, never beats `gap_driven_3tier`,
   no_regression.
6. HP6 ablation A (no-generalization must not beat full) + structural (zero leaked cluster
   promotions in the ablation arm's store).
7. HP7 ablation B (no-pull must show >=0.02 LESS fade than full).

**HARD-FAIL (ANY ONE, unchanged from v1):** tier fades less than binary; fidelity collapse (HP2);
coverage-controlled comprehension regression `< binary - 0.03` (HP3 hard-fail variant);
scramble ties/beats tier or exceeds BoW+0.02; `combined_evidence_promotion_count == 0`; ablation-
isolation leak; smoke-time cluster-cardinality tripwire (`n_clusters < 0.5 *
n_distinct_semantic_buckets_seen`) unresolved before FULL.

**MIDDLE_BAND**: any HARD-PASS criterion misses while no HARD-FAIL trips -- reported honestly, never
rounded up.

**This cell's specific success criterion (restated from the task, on top of the inherited bands):**
does HP2 AND HP3 flip to True relative to v1's `data/exp_crutch_fade_social_iqa_v1_3tier_seed7/
metrics.json` (False, False)? A clean flip of both = the diagnosed root-cause fix worked. A flip of
one but not the other, or neither, is a fine, honest, reportable outcome (MIDDLE_BAND or HARD_FAIL
respectively) -- not to be spun as success.

## Smoke gate (MEASURED, this pre-reg's own evidence -- see completion report for the numbers)

SMOKE_TRAIN_CAP=15000 / SMOKE_DEV_CAP=400 (v1's own established smoke scale -- MEASURED to fire real
promotions in v1's history), score_mode=hub_penalized, promote_min_exposure=8, seed=7. MEASURED:
125.06s wall, mechanism clearly fires (168 combined-evidence promotions, `n_clusters=4` vs v1's OWN
smoke-scale `n_clusters=2` -- an improvement, not the literal "collapsed to 2" contingency condition
in the task prompt), baseline in-band (bow=0.3775, not saturated). HP2/HP3 still measure False at
smoke scale (matching v1's own smoke, which ALSO showed HP2/HP3 False at this scale before its FULL
run resolved differently) -- SMOKE-SCALE RESULT IS NOT TREATED AS DEFINITIVE for HP2/HP3 given the
small sample (`combined_evidence_cluster` n=20 at smoke vs n=163 at v1's FULL) and v1's own
established precedent that smoke and FULL numbers on this exact cell diverge. `arms_differ_verified`
was False at smoke with one non-exempt collision (`scramble_crutch` vs `scramble_crutch_3tier`) --
CROSS-CHECKED against `data/exp_crutch_fade_social_iqa_v1_smoke/metrics.json`: v1's OWN smoke at the
IDENTICAL scale/config had the SAME collision PLUS one more (`gap_driven_3tier` vs `gap_driven_3tier_
no_pull`, which v2's smoke does NOT show -- one collision fewer), and v1's FULL run cleanly resolved
to `arms_differ_verified=True` with zero non-exempt collisions. This is a disclosed, historically-
precedented SMOKE-SCALE artifact (insufficient dev/exposure volume for the scramble-side PRELIM/
cluster tiers to diverge within only 400 dev items), not a new bug from this cell's one-variable
change -- FULL dispatch proceeds on this precedent, with the FULL run's own `arms_differ_verified`
re-checked independently (MANDATORY) before treating its HP2/HP3 verdict as clean.

## CELL-TEMPLATE MANDATORY (SCHEMA-VET checklist, unchanged from v1 except as noted)

- `arms_differ_verified`: 9-arm hash-differ; `arms_differ_exempted=[["bow","never_crutch"]]`
  (unchanged); smoke-scale collision disclosed above, re-verified TRUE at FULL (mandatory check).
- `final_metrics_atomicity`: tmp_replace (unchanged).
- `except SystemExit: raise` before `except Exception` (unchanged; grep-gate re-verified clean, no
  bare `except:` / `except BaseException:` in the new file).
- `crlb_n/a`: unchanged rationale (symbolic KB-lookup + vote-count pipeline).
- `HP_SCOPE`: unchanged (`dev_checkpoint_eval` gates only; `binary_baseline_verdict` informational).
- `cardinality_ok`: `EXPECTED_N_CHECKPOINTS=5`, `EXPECTED_N_ARMS=9` (unchanged).
- Per-unit failure-class instrumentation: unchanged (no bare except anywhere in new code).
- `calibration_check`: `adaptive_with_discriminator_gate` (GATE_THRESH unchanged) PLUS `novelty_
  thresh` calibrated against THIS run's own semantic-bucket vocabulary (v2 change, logged, not
  hand-tuned) -- MEASURED@smoke: `novelty_thresh=0.2903`, `n_semantic_buckets_sampled=64`,
  `discriminates=True`.
- `real_code_path_exercised`: self-test constructs the REAL `Library`, `HDFactStore`,
  `ScriptLibrary`, `build_instance_register`, `match_or_spawn`, `CharTrigramEncoder` at tiny
  synthetic scale -- PASSED (see completion report). Adds 4 new v2-specific assertions:
  `semantic_relation_key` determinism, idx-independence (unlike `relation_family`, no CSKG-edge
  lookup happens), content-sensitivity (a shared-concept pair embeds strictly closer than an
  unrelated pair -- the actual "semantic embedding" claim, tested on the deterministic encoder
  cosine directly, not on probabilistic bucket equality), and no-UNKNOWN-fallback. Combined-evidence-
  promotion test (9) uses a concept triple (`gate/fix`, `lock/fix`, `door/fix`) VERIFIED by direct
  script to collide at the SAME LSH bucket (`sem_011111`) under this file's own encoder+projection,
  not hand-waved.
- `progress_logging`: `print_flush_true` (unchanged).

## Dispatch

Same class as v1 -- light CPU-only. MEASURED@smoke 125.06s for the reduced-scale run; v1's own FULL
(same arm/checkpoint count, ~2.2x train exposure, ~4.9x dev items) measured 340.67s. Given this is
comfortably inside a single foreground Bash call (Bash tool max explicit timeout 600s), and matches
v1's OWN pre-reg's dispatch decision ("Dispatch: Same class as the base cell -- light CPU-only, run
foreground-to-completion (not queued), smoke first"), FULL runs foreground-to-completion (no queue),
NOT via `queue_add.sh` -- avoiding SSH/SCP/remote-parity risk for a run that fits comfortably in one
verified local foreground call and gives an immediate, honest verdict. Seed: 7 (matching v1's
canonical baseline seed for apples-to-apples HP1/HP2/HP3 comparison against `data/exp_crutch_fade_
social_iqa_v1_3tier_seed7/metrics.json`). Single seed for this diagnostic rebuild (the design audit's
own "smallest first experiment" spec does not mandate multi-seed; a second-seed robustness check is
a natural, cheap follow-up if HP2/HP3 flip and the result needs hardening before further build-out).
