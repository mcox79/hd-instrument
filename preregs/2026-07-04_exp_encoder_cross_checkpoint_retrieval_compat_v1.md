# Pre-reg: Encoder cross-checkpoint retrieval-compatibility probe

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED bands, then SMOKE + FULL both run
in-session (light read-only probe; both landed before this file's numbers were filled in --
see "Measured results" section, all tagged MEASURED@).

Cell: `experiments/exp_encoder_cross_checkpoint_retrieval_compat_v1_core.py`
Anchor: `encoder_cross_checkpoint_retrieval_compat_v1` (smoke suffix `_smoke`, full = no suffix).
Reused (import only, NOT edited): `experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`.
Does NOT touch the running v3b GPU cell's dirs (`data/substrate_concept_encoder_v1b_v3b_*`,
`data/exp_encoder_migration_step1b_v3b_*`) -- own artifact dirs only:
`data/exp_encoder_cross_checkpoint_retrieval_compat_v1{_smoke,}/metrics.json`.

Spec source: `notes/research_drill_brain_grounded_continual_self_improving_encoder_2026-07-04.md`,
"Cheap decisive test" section. Question: if the concept encoder is UPDATED (version B) after
vectors were already stored by version A, can a query encoded by one version still retrieve
the correct item stored by the other, or does an encoder update silently break every stored
vector? Falsifiable predictions CITED@that doc: HARD-PASS >= 90% of same-checkpoint retrieval,
HARD-FAIL < 50%, MIDDLE_BAND 50-90%.

## Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01)

Query: "cross-checkpoint retrieval compatibility encoder version backward compatible embedding
drift" -> top hit cosine=0.3916 (generic WordNet "compatibility"/"incompatibility" antonym
lexical entries, not a prior arc cell); rank-4 hit "Versioning + backwards compatibility"
(`notes/research_drill_production_deployment_architecture_2026-06-07.md`, cosine=0.376) is a
DIFFERENT topic (deployment/ops versioning practice, not encoder cross-checkpoint retrieval
mechanism). NONE of the top-5 hits is a prior arc cell addressing this specific probe.
**Verdict: GENUINELY NOVEL** instantiation of the continual-encoder drill's own recommended
test; not a rediscovery.

## Instantiation decision (YOU-decide caveat, per spawn instruction)

The drill's literal design compares step1200-vs-step1800 checkpoints of ONE lineage (within-run
drift). No intermediate per-step checkpoints exist on disk for either R1 MID arm -- only the
final step-1800 checkpoint was retained per arm (`data/substrate_concept_encoder_v1b_v3global_mid/
_ckpt_block_{global,in_batch}.pt`, both `step: 1800` MEASURED@both checkpoint files' `step` key).
A retrain to manufacture an earlier checkpoint was judged out of scope for a "cheap decisive,
no new training" probe (the drill's own words: "no new training required").

**Decision: instantiate cross-"version" as GLOBAL-objective (version A, the R1 landmark-anchor
fix) vs IN_BATCH-objective (version B, the v2 baseline, no landmark anchor at all) final
checkpoints of the SAME R1 MID run.** Both share seed=7, the same held-out split, the same
teacher embedding space, and (per `_make_student`'s `torch.manual_seed(seed)`) the SAME initial
MLP weights before 1800 steps of divergent training.

This is a FAITHFUL test of "did an encoder UPDATE (an objective swap -- a realistic
real-world encoder-improvement event) break already-stored vectors," directly answering the
USER's question. It is only a PARTIAL test of the narrower "the landmark anchor alone IS a
BCT (backward-compatible-training) mechanism" claim, because only arm A references the
landmark frame; arm B never does, and neither arm carries an explicit CROSS-version
compatibility loss (the drill's own NEXT-priority item, not yet built). A HARD_PASS here would
have been the stronger, more surprising result (compatibility for free, no explicit loss
needed); a HARD_FAIL is the expected, mechanism-consistent result and is exactly the evidence
the drill says would justify pulling the compatibility-loss work forward -- see "Verdict routing"
below.

## Bands (declared before the run, thresholds cited not re-derived)

Let `ratio[dir,code] = cross_top1[dir,code] / same_top1[code]` for `dir in
{A_index_B_query, B_index_A_query}` and `code in {dense, block}` (4 ratios). `min_ratio =
min` over all 4.

- **HARD_PASS**: `min_ratio >= 0.90` (CITED@drill "cross-checkpoint retrieval stays at or
  above ~90% of same-checkpoint... on BOTH DENSE and BLOCK"). -> compatibility-loss work is
  NEXT-priority, not urgent.
- **HARD_FAIL**: `min_ratio < 0.50` (CITED@drill "cross-checkpoint retrieval drops below ~50%
  of same-checkpoint... the piriform chance-level-by-day-32 signature reproduces"). -> pull
  compatibility-loss work FORWARD to NOW, before any periodic re-distillation cadence.
- **MIDDLE_BAND**: `0.50 <= min_ratio < 0.90`. -> real but not urgent; proceeds as NEXT per
  the drill's default recommendation.

`HP_SCOPE`: the HARD_PASS/HARD_FAIL gate applies ONLY to the 4 `ratios` units (the
`CROSS_*` vs `SAME_*` comparison). `SAME_*` and `RANDOM_CONTROL_*` units are integrity-only
correctness sanity checks, exempt from the gate (they gate the CELL's own validity, not the
science question).

## SCHEMA-VET / META_RULE fields

- `cardinality_ok`: `EXPECTED_N_UNITS = 10` (2 SAME-checkpoint x 2 codes + 2 CROSS-directions x
  2 codes + 1 RANDOM_CONTROL x 2 codes). Verdict counts `per_unit`; shortfall ->
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified`: true (sha256 over the 4 code matrices A_dense/B_dense/A_block/B_block;
  MEASURED distinct in both smoke and full -- see digests in metrics.json).
- `final_metrics_atomicity`: `"tmp_replace"` (this cell writes its own `metrics.json.tmp` +
  `os.replace`, does not depend on `_seed_checkpoint.write_metrics`'s non-atomic write).
- except-discipline: `except SystemExit`/`KeyboardInterrupt` re-raise before `except Exception`;
  grep gate for bare `except:` / `except BaseException` PASSED (verified before dispatch).
- `crlb_floor_computed`: **n/a** -- this is a retrieval-identity ratio, not a noise-floor/
  capacity metric. Closest analytical floor is chance-level top-1 = `1/n_probe` (SMOKE
  1/200=0.0050, FULL 1/4390=0.000228 THEORETICAL@uniform-random-argmax); verified empirically
  via the `RANDOM_CONTROL` arm rather than a closed-form bound. `discriminator_reachability`:
  true (HARD_FAIL threshold 0.50 is far above the chance floor and far below the same-checkpoint
  ceiling of 1.0, so both PASS and FAIL are physically reachable outcomes).
- `baseline_in_band` (META_RULE_AG analog, this cell's own correctness gate): `SAME_*` retrieval
  must be `>= 0.99` (near-ceiling sanity; if not, the retrieval computation itself is broken).
  Hard-asserted in code (raises `SAME_CHECKPOINT_SANITY_FAIL` if violated), not merely reported.
- discriminator-fires (META_RULE_K): `RANDOM_CONTROL_*` (two independent random codebooks) must
  score `<= 0.10`; proves the metric has real floor-vs-ceiling dynamic range and is not
  vacuously saturating to 1.0 regardless of input. Hard-asserted (raises
  `RANDOM_CONTROL_TOO_HIGH` if violated).
- discriminator-survives-scale: SMOKE runs at `n_probe=200` (random subsample of the 4390-item
  held set); FULL runs at the full held set (n=4390). The qualitative question (is
  cross-checkpoint retrieval close to the same-checkpoint ceiling) is not scale-sensitive here
  -- chance level scales as `1/n` either way, always far below both thresholds -- so SMOKE-at-
  reduced-N is a legitimate discriminator preview (option A/C hybrid per
  DISCRIMINATOR-MUST-SURVIVE-SCALE), not merely a machinery check. CONFIRMED: smoke min_ratio
  (0.073, see below) and full min_ratio (0.0100) land in the SAME verdict tier (HARD_FAIL);
  scale did not flip the qualitative conclusion.
- `calibration_check`: `"default_ok_for_this_regime"` (identical regime/split/architecture to
  the already-validated R1 MID cell; this cell only adds a read-only cross-encode + retrieval
  pass on top, no new training config).
- `cell_chunked`: false (single fixed seed=7 matching the R1 lineage's own split; not a
  multi-seed statistical claim -- both checkpoints being compared were themselves trained at a
  single seed). `start_marker_written`: true. `crash_diagnostic_present`: true (tmp+replace
  atomic CELL_CRASHED writer). `heartbeat_present`: **n/a-with-reason** -- total elapsed_s
  MEASURED at 10.7s (full) / 2.3s (smoke), both far under the 60s heartbeat-cadence threshold in
  exp_dev.md SS13.D and the 30-min SS17 print-flush-mandatory threshold; no heartbeat needed for
  a single-digit-to-low-teens-second cell. `defensive_error_checking`: `"passed_all_4_patterns"`
  (start marker + crash diagnostic + per-unit failure-class via raised exceptions + N/A-justified
  heartbeat).
- `progress_logging`: **n/a** (`timeout_s` is nowhere near the 1800s/30min SS17 threshold;
  MEASURED elapsed_s = 10.7s full run). `print(..., flush=True)` used throughout anyway
  (defense-in-depth, zero cost).
- Section 15 gates: `sweep_alignment_verdict` N/A (no swept parameter; single fixed probe).
  `discriminating_fraction` N/A (not a sweep). `composition_edges`: N/A (no primitive
  composition; this is a pure encode + cosine-retrieval read). `positive_control_arms`:
  `SAME_A_*`/`SAME_B_*` ARE the positive controls (must hit the analytically-certain ceiling of
  1.0; MEASURED 1.0000 in both smoke and full, see below). `functional_requirements`: FR1
  (does an encoder update preserve retrieval of already-indexed vectors) is the entire point of
  this cell; addressed by the CROSS_* units directly, no existing chain-grade primitive maps to
  this FR (it is itself the new mechanism-validation probe the drill requested).

## Compute architecture

Class (a) batched (read-only inference, not training). Both checkpoints' forward passes are
single-batch MLP calls (`_dense_sign_codes` / `_encode_hard_block`, both already batched
internally at `batch=8192`, well above `n_probe<=4390`); the `[n,n]` cosine retrieval matrix is
one batched matmul per unit (chunked at 1024 rows only to bound peak memory, not because it is
sequential). No per-phase-point Python loop. Storage strategy: no_storage (this cell reads two
already-trained student checkpoints and a cached teacher embedding array; it writes no new
atoms/index entries).

**Dispatch class exception (explicit, flagged):** per the standing USER-lock
(`feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`), FULL runs
normally route to `remote_cpu_queue`/`overnight_queue`, not `local_cpu_queue`. This task's own
spawn instruction explicitly authorized "RUN (light, LOCAL CPU..." for this specific one-shot
read-only probe (no training, reuses existing checkpoints, MEASURED total wall time 10.7s for
FULL). Both SMOKE and FULL were run directly via `python experiments/exp_encoder_cross_
checkpoint_retrieval_compat_v1_core.py --{smoke,full} --seed 7` in this session -- NOT via
`tools/queue_add.sh` -- because the cell has no training loop and the standing local-CPU-queue
restriction exists to protect the USER's laptop from multi-hour training runs, which does not
apply here. Flagged explicitly rather than silently treated as routine.

## Timeout

MEASURED@this session (both already landed, not estimated): SMOKE `elapsed_s=2.3` (wall
`16.1s` incl. Python/torch import overhead), FULL `elapsed_s=10.7` (wall `15.6s` incl. import
overhead). No `--timeout` needed for a queue dispatch since this ran directly; if re-run via
`queue_add.sh` in the future, `--timeout 120` is generous (>10x the measured full-run cost).

## Halt conditions

Checkpoint missing -> `FileNotFoundError` before any encode (`CHECKPOINT_MISSING`).
`load_state_dict` missing/unexpected keys -> `STATE_DICT_MISMATCH`, hard abort (no silent
partial-load). Held-split reproduction mismatch vs the R1 MID run's known split
`(39515, 4390)` -> `SPLIT_MISMATCH`, hard abort (teacher-cache selection drift would silently
compare the wrong concepts). Same-checkpoint sanity `< 0.99` -> `SAME_CHECKPOINT_SANITY_FAIL`
(retrieval-computation bug, not a real result). Random-control `> 0.10` ->
`RANDOM_CONTROL_TOO_HIGH` (discriminator-fires check failed). Bit-identical arms ->
`META_RULE_AF_VIOLATION`. Any of the above raise and let the crash-diagnostic writer record
`CELL_CRASHED` with full traceback; none were hit in the actual smoke/full runs.

## Measured results (both SMOKE and FULL landed this session; all numbers MEASURED@disk)

**SMOKE** (n_probe=200, seed=7)
MEASURED@`data/exp_encoder_cross_checkpoint_retrieval_compat_v1_smoke/metrics.json`:
`SAME_A_DENSE=1.0000 SAME_A_BLOCK=1.0000 SAME_B_DENSE=1.0000 SAME_B_BLOCK=1.0000`
`CROSS_INDEX_A_QUERY_B_DENSE=0.0800 CROSS_INDEX_A_QUERY_B_BLOCK=0.0850`
`CROSS_INDEX_B_QUERY_A_DENSE=0.1100 CROSS_INDEX_B_QUERY_A_BLOCK=0.0850`
`RANDOM_CONTROL_DENSE=0.0100 RANDOM_CONTROL_BLOCK=0.0000`
`min_ratio=0.0800` -> **HARD_FAIL** (< 0.50 threshold by a wide margin).
Cardinality: 10/10 units. Arms differ: verified (4 distinct sha256 digests). Elapsed: 2.3s.

**FULL** (n_probe=4390, the entire held set, seed=7)
MEASURED@`data/exp_encoder_cross_checkpoint_retrieval_compat_v1/metrics.json`:
`SAME_A_DENSE=1.0000 SAME_A_BLOCK=1.0000 SAME_B_DENSE=1.0000 SAME_B_BLOCK=1.0000`
`CROSS_INDEX_A_QUERY_B_DENSE=0.01116 CROSS_INDEX_A_QUERY_B_BLOCK=0.01002`
`CROSS_INDEX_B_QUERY_A_DENSE=0.01549 CROSS_INDEX_B_QUERY_A_BLOCK=0.01162`
`RANDOM_CONTROL_DENSE=0.000228 RANDOM_CONTROL_BLOCK=0.000228` (matches THEORETICAL chance
1/4390=0.000228 almost exactly).
`min_ratio=0.01002` (i.e. cross-checkpoint retrieval is ~1.0% of same-checkpoint retrieval).
-> **HARD_FAIL**, far below the 50% threshold (min_ratio is ~50x below the HARD_FAIL boundary,
not a borderline case). Cardinality: 10/10 units. Arms differ: verified. Elapsed: 10.7s.

Cross-checkpoint retrieval (1.0-1.5%) IS meaningfully above the pure-random floor (0.023%) --
roughly 45-68x better than chance -- confirming the metric is not floor-saturated and there is
SOME residual shared structure (consistent with the shared initialization + shared semi-hard
negative mining + shared teacher space), but this residual correlation is catastrophically
insufficient for any practical "swap the encoder, keep the old index" use case.

## Verdict routing

**HARD_FAIL, as instantiated.** Per this pre-reg's own routing: pull the explicit
compatibility-loss work forward -- do NOT adopt any periodic re-distillation/encoder-swap
cadence without a compatibility term from the first cycle. This is the EXPECTED,
mechanism-consistent outcome given the caveat above (neither arm implements an explicit
cross-version compatibility loss; GLOBAL's landmark anchor fixes in-batch coverage WITHIN its
own training, it does not by itself grant free compatibility with an unrelated encoder run).
Read together with the drill's own Part 3 condition list, this result is additional evidence
FOR building the drill's NEXT-priority item 2 (freeze a held set encoded under the CURRENT
encoder version, train the next-version candidate WITH an added BCT-style compatibility loss
against that frozen set, measure cross-version retrieval WITH vs WITHOUT the term) BEFORE
promoting any future encoder version into production -- exactly the guard the drill's own
"top failure mode" section names. Does not block R1's own base-objective work (DENSE-recovery
in flight on v3b); this is a parallel, independent finding about a DIFFERENT question
(compatibility across versions, not semantic quality within one version).
