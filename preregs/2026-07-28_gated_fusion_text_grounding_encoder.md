# Pre-reg: Gated-fusion cash-in on the encoder's text+grounding channels

- Anchors: `gated_fusion_text_grounding_encoder_seed_7`, `gated_fusion_text_grounding_encoder_seed_13`
  (CHUNKED single-seed-per-cell; shared core `experiments/_gated_fusion_text_grounding_encoder_core.py`)
- Cells: `experiments/exp_gated_fusion_text_grounding_encoder_seed_7.py`,
  `experiments/exp_gated_fusion_text_grounding_encoder_seed_13.py`
- Date: 2026-07-28
- Queue target: `remote_cpu_queue` (CPU-only, lightweight measurement on already-saved reps; no
  training; do NOT run locally per standing directive; do NOT contend with the GPU box's own
  seed_13 grounding training)
- Capability-integration gate: cash-in of `gated_fusion_relation_inference`
  (`data/capability_registry.jsonl`, `hdlab/gated_fusion.py`, HARD_PASS +0.297 MRR mammal-KG,
  8 seeds) per `notes/prereg_stub_gated_fusion_text_grounding_fusion_QUEUED_2026-07-28.md`.

## Prior-work check (substrate-KB concept-query, per exp_dev discipline)
`bash tools/substrate_query.sh "learned gate fusion text grounding channel relational semantic AUC"`
top hits (cosine>0.30): (1) `CN_semantic_relation` 0.36 -- generic KB noise, unrelated; (2)/(3)
`semantic_relation`/`semantic relation` (wordnet/atoms) 0.356 -- generic KB noise, unrelated;
(4) `grounding_gated_fusion_relation_inference_mammal_v1` metrics 0.333 -- **this IS the source
mechanism cell being cashed in**, not a duplicate of this application; (5) the mammal cell's own
pre-reg text 0.325 -- same. **Verdict: genuinely novel application, not a rediscovery.** No prior
cell applies `hdlab.gated_fusion` to the encoder's text+grounding channels; the only hit is the
mechanism's own origin cell (expected and desired -- confirms lineage, not duplication).

## Question
Does the LEARNED convex gate (`hdlab.gated_fusion.gated_table` / `learn_lambda`, promoted,
HARD_PASS elsewhere) beat the encoder's own fixed 0.5/0.5 z-avg fusion (`ARM_FUSE_ZAVG`) on
held-out-NEW SEMANTIC and RELATIONAL AUC, when applied as the text+grounding fusion operator?
Motivated by the grounding cell's OWN measured baseline arms (recomputed fresh off the saved reps,
not re-cited): z-avg helps semantic (TEXT=0.624->ZAVG=0.638, +0.014) but HURTS relational
(TEXT=0.632->ZAVG=0.611, -0.021) because grounding-alone is near-chance on relational (0.560). A
gate that can down-weight grounding on relational while up-weighting it on semantic should recover
what z-avg loses -- this is exactly the load-bearing test, per Director design-verification
(2026-07-28).

## Design-verification response (Director, 2026-07-28 -- both addressed in the core module)
1. **Two independent scalar gates, not one global lambda.** `fit_lambda_semantic` and
   `fit_lambda_relational` each call the promoted mechanism (`gated_table`/`learn_lambda`)
   SEPARATELY, each on its own VAL sample and its own score_fn (semantic same-lexname AUC;
   relational true-neighbour-vs-degree-matched-negative AUC). A single global lambda would average
   away exactly the asymmetry the hypothesis is about; this cell does NOT do that.
2. **VAL != TEST, runtime-asserted.** Both fits sample VAL exclusively from `split["train_eval_idx"]`
   (TRAIN-side); `split["held_idx"]` (TEST) is never touched at fit time.
   `_assert_val_test_disjoint` RAISES (hard failure, not a soft flag) if any overlap is found --
   defends the by-construction disjointness (`build_split` already excludes held from
   train_eligible) against any future refactor silently breaking the invariant.

## Mechanism mapping (this cell's own choice; documented so lambda direction is never ambiguous)
`primary_codes = GROUNDING` (per-query z-scored cosine vs candidates; sometimes near-chance or
entirely absent -- a concept with zero grounding-norm coverage has an exactly-zero 20-dim rep,
verified not approximated). `fallback_codes = TEXT` (always present). `gated_table`'s cold-row
contract ("support_deg==0 -> pure fallback") therefore does the right thing automatically: a
concept with zero grounding coverage gets pure TEXT regardless of the fitted lambda.
`lambda=0.0` -> pure GROUNDING. `lambda=1.0` -> pure TEXT. GRID = `[0.0, 0.1, ..., 1.0]` (11
points), covering BOTH pure endpoints (this cell's own broadening of gated_fusion's "grid must
include 1.0" discipline to also include 0.0, so the gate can never do worse than EITHER pure
channel on VAL, whichever dominates for that axis).

**Fusion level: score-level, not raw-embedding-level.** TEXT reps (d_model-dim) and GROUNDING reps
(20-dim) live in different-dimensional spaces -- a raw convex blend of the two embeddings is not
well-formed (the exact projection-step gap the 2026-07-28 testbed stub flagged). The sibling
cell's own `ARM_FUSE_ZAVG` already solves this by fusing at the per-query z-scored COSINE-SCORE
level; this cell applies `gated_table` to the SAME z-scored score vectors instead of the fixed
0.5/0.5 -- a dimensionally-honest generalization of the mechanism z-avg already uses, with a
LEARNED weight instead of a fixed one. `gated_table`'s per-row API is agnostic to what a "code" is;
a per-query z-scored candidate-score vector is as legitimate a "code" as a per-concept embedding.

**Correctness cross-check (mandatory runtime assertion, not just self-test):** at lambda=0.5,
`gated_table`'s formula reduces EXACTLY to `0.5*(primary+fallback) = 0.5*(z(cos_ground)+z(cos_text))`
-- the SAME formula `ARM_FUSE_ZAVG` already uses. The cell asserts its own lambda=0.5 recompute
matches the imported, UNMODIFIED `_r.semantic_eval` / `_r.relational_eval` `FUSE_ZAVG_ARM` output
on the identical held-out query set within 1e-4, and RAISES (does not silently continue) if it
doesn't. MEASURED@dry-run (seed_7, real data, 2026-07-28): sem_delta=0.000000, rel_delta=0.000000
-- exact match.

## Reuse discipline
Imports `exp_scale_meaning_learn_arc_heldout_v3_relobj` (alias `_r`) UNCHANGED: `_load_eval_bundle`
(the existing EVAL-ONLY npz re-run loader), `select_fusion_on_train`, `semantic_eval`,
`relational_eval`, `_cos_matrix`, `_zscore_rows`, `_auc_from_scores`, arm-name constants. The
sibling module file is NEVER edited (read-only import; the GPU box may still be training seed_13
concurrently -- importing here does not touch that process, verified: importing does not execute
training, `if __name__ == "__main__":` guards the sibling's own driver). The relational per-query
gate-eval loop additionally reproduces the sibling's EXACT rng-consumption order (including the
upfront `rng.permutation(len(elig_q))` the sibling burns for its own ARM_COLLAPSE_SHUFFLE control,
which this cell has no use for but must still consume to keep candidate/negative draws identical --
this was a real bug caught during authoring: omitting the burn produced a 0.025 AUC delta at the
lambda=0.5 cross-check; fixed and now exact-zero).

## Metric
Per-query AUC (base 0.5), same leak-proof construction as the sibling cell's SEMANTIC (same-lexname,
held-out-NEW concepts) and RELATIONAL (true TRAIN-neighbour vs degree-matched negatives, held-out-NEW
query) evals. PRIMARY comparison: GATE arm vs `ARM_FUSE_ZAVG` (the arm being replaced) and vs
`ARM_RAW_TEXT` (text-alone, the honest relational ceiling reference). Both axes reported.

## Arms
- `ARM_RAW_TEXT`, `ARM_FUSE_ZAVG`, `ARM_RAW_GROUNDING` -- REUSED baselines (unmodified sibling
  functions; recomputed fresh from the same saved reps every run, not cited).
- `GATE_SEM`, `GATE_REL` -- the mechanism arms (this cell's own), lambda fit independently per axis.
- `PURE_TEXT` (gate at lambda=1.0), `PURE_GROUNDING` (gate at lambda=0.0) -- gate-family endpoints,
  reported for the arms-differ check and as sanity references (should closely track
  `ARM_RAW_TEXT`/`ARM_RAW_GROUNDING` respectively, modulo the score-vs-embedding-cosine formula
  detail already noted).

## PRE-REGISTERED BANDS (both axes; cross-seed -- apply ONLY once BOTH seed_7 AND seed_13
metrics.json exist; a single seed's metrics.json carries verdict
`SINGLE_SEED_MEASURED_GATES_PASS/PARTIAL`, NEVER a HARD_PASS/HARD_FAIL by itself)

Let `sem_margin[s] = GATE_SEM_auc[s] - ZAVG_sem_auc[s]`, `rel_margin[s] = GATE_REL_auc[s] -
ZAVG_rel_auc[s]`, `rel_dist_to_text[s] = GATE_REL_auc[s] - RAW_TEXT_rel_auc[s]`, for s in {7, 13}.

**HARD_PASS_GATE_RECOVERS_BOTH_AXES**, ALL of:
  (a) `mean(sem_margin) > 0` AND `min(sem_margin) >= -0.005` (semantic: gate beats z-avg on
      average and never meaningfully regresses on either seed -- "modest" gain per the honest
      framing, not required to be large);
  (b) `mean(rel_margin) >= 0.01` AND `sem_margin[7] > 0 and sem_margin[13] > 0`-style per-seed
      positivity is NOT required for relational's HARD_PASS (only the mean, since z-avg's
      relational damage (-0.021) is itself larger than typical single-seed AUC noise at this
      n_query (~600), so a real mean recovery is the honest bar) -- but BOTH seeds' rel_margin
      must be `> -0.01` (no seed makes it meaningfully worse than z-avg);
  (c) **Honest relational ceiling** (per Director): `mean(rel_dist_to_text) <= 0.02` in absolute
      value -- the gate RECOVERS TOWARD text-alone, it is not required to (and is not expected to)
      exceed it, since grounding carries ~no relational signal. Exceeding text-alone by a small
      margin (as seed_7 alone shows, +0.0028) is NOT penalized -- only a large positive excess
      (>0.02, which would be suspicious/overfit) or a large shortfall (<-0.02, meaning the gate
      failed to recover) fails this gate;
  (d) both fits actually ran the real grid-search (`used_fallback == False` on both seeds for both
      axes) -- a fallback-to-lambda=1.0 landing means the VAL sample was too thin to trust, not a
      genuine null result, and should be reported as INCONCLUSIVE_THIN_VAL, not HARD_FAIL;
  (e) leak-assert passes on all 4 fit calls (2 seeds x 2 axes) -- structural, not a soft gate (the
      cell RAISES rather than reporting a false PASS if this fails, so by the time metrics.json
      exists this is already implicitly true).

**MIDDLE_BAND_PARTIAL_RECOVERY**: relational recovers (`mean(rel_margin) >= 0.005`) but semantic
regresses beyond -0.005, OR semantic clears but relational's mean margin is in [0, 0.01) (real but
too small to call decisive), OR one seed used a fallback lambda (VAL too thin -- report as
INCONCLUSIVE_THIN_VAL, sub-case of MIDDLE_BAND).

**HARD_FAIL_GATE_DOES_NOT_RECOVER**: `mean(rel_margin) <= 0` (the gate fails to beat z-avg's own
degraded relational number at all, despite the mechanism firing on real VAL data) -- this would
mean the gate mechanism itself does not transfer to this domain, a genuine negative worth reporting
plainly (per the no-defeatist-but-honest standing discipline: this IS an informative outcome, not
grounds to keep tuning until it flips).

**INCONCLUSIVE**: either seed's evalreps.npz never lands, or the xcheck assertion fails (structural
bug, not a science result), or `used_fallback == True` on both seeds for an axis (VAL genuinely too
thin at this scale to fit anything -- should not occur at FULL scale given ~14,900 train_eval
concepts, but declared for honesty).

## Self-test (real code path; enforce) -- MEASURED
`python experiments/exp_gated_fusion_text_grounding_encoder_seed_7.py --self-test`: constructs a
REAL synthetic bundle (N=24->40 concepts, ring+chord adjacency, dual-lexname labeling, 1 planted
cold concept with exactly-zero grounding norm) and calls the ACTUAL `fit_lambda_semantic` /
`apply_gate_semantic` / `fit_lambda_relational` / `apply_gate_relational` / `gated_table` /
`learn_lambda` / `_r.semantic_eval` / `_r.relational_eval` functions (not a mocked path).
SELFTEST_PASS: baseline reuse OK (sem_n_query=20, rel_n_query=20); lambda_sem=0.10 (n_val=20),
lambda_rel=1.00 (n_val=0, correctly fell back to pure-TEXT floor at this tiny synthetic scale);
**XCHECK PASS (sem_delta=0.000000, rel_delta=0.000000)**; cold-row fallback OK (1 cold concept
forced to pure TEXT at lambda=0.0, `np.allclose` verified); LEAK ASSERT positive control OK (raises
on a deliberately-overlapping id set -- proves the guard is live, not dead code).
MEASURED@(local self-test run, 2026-07-28, exit 0, "ALL CHECKS PASS").

## Dry-run against REAL seed_7 data (informative; NOT the FULL dispatch verdict -- see next section)
Before shipping, `run_one_seed(7, ..., evalreps_seed_7.npz, ...)` was executed directly (foreground,
local CPU, real seed_7 npz scp'd to a scratch path) to catch real-data bugs before remote dispatch
(the self-test's synthetic bundle cannot catch e.g. the rng-consumption-order bug the xcheck caught
mid-authoring). MEASURED@(local dry-run, 2026-07-28, wall=32.9s):
  K=16522, held=800, train_eval=14915.
  baseline semantic: TEXT=0.6244 ZAVG=0.6379 (+0.0135) GROUNDING=0.5968 (n_query=797)
  baseline relational: TEXT=0.6316 ZAVG=0.6105 (-0.0211) GROUNDING=0.5603 (n_query=596)
  XCHECK: sem_delta=0.000000, rel_delta=0.000000 (PASS)
  GATE_SEM: lambda*=0.60 (val_score=0.6419, n_val=1500, used_fallback=False) -> TEST_AUC=0.6409
    (margin vs ZAVG = +0.0030; margin vs TEXT = +0.0165)
  GATE_REL: lambda*=0.90 (val_score=0.6649, n_val=444, used_fallback=False) -> TEST_AUC=0.6344
    (margin vs ZAVG = +0.0239; dist_to_text = +0.0028 -- essentially full recovery, slightly past)
This SINGLE-SEED evidence is directionally exactly what the hypothesis predicted (gate beats z-avg
on BOTH axes; relational recovery lands almost exactly at text-alone) -- HYPOTHESIZED-then-MEASURED,
not the other way around. It is explicitly NOT a HARD_PASS by itself (n=1 of 2 seeds; semantic
margin is small, ~within single-seed AUC noise at n_query=797, `sqrt(0.25/797)~=0.018`) -- seed_13
is required before any BOTH-seeds band applies. Re-run via the actual dispatched cell (not this
dry-run harness) is the FULL landed verdict of record.

## Compute architecture
(c) mixed, justified: CPU-only (no GPU dependency at all -- text/grounding reps are ALREADY
computed and saved by the grounding training cell; this cell only loads them and does numpy/torch
CPU vector ops over ~800 held queries x ~11 grid points x 2 axes -- a few thousand small tensor
ops, sub-minute wall time, well under the 10s-total exemption's spirit scaled up for real data I/O).
Sequential-CPU justified: this is the primitive under test (the gate module) at its actual intended
application; no batching opportunity exists beyond what's already vectorized (semantic axis IS
batched via one NxN `learn_lambda` call; relational axis is a Python loop over ~600-800 queries,
each a microsecond-scale `gated_table` call -- profiled wall time 32.9s total for the WHOLE cell
including npz load, dominated by I/O and the sibling functions' own O(n^2) semantic score-matrix
construction, not by the gate loop itself).

## Storage strategy
no_storage / no_composition -- this is a read-only measurement over already-saved reps; no new
persistent store writes beyond metrics.json.

## SCHEMA-VET checklist
- `cell_chunked: true` (one seed per file; shared core).
- `start_marker_written: true`, `crash_diagnostic_present: true` (own `_write_start_marker` /
  `_write_crash_metrics`, atomic tmp+os.replace).
- `heartbeat_present: false` -- expected wall time ~1 min (measured 32.9s on real data), well under
  the section-13 "any cell >~15 min" heartbeat threshold; declared exemption, not an omission.
- `defensive_error_checking: "passed_all_4_patterns_except_heartbeat_exempted_by_wall_time"`.
- `final_metrics_atomicity: "tmp_replace"`.
- Grep gate: no bare `except:` / `except BaseException:` anywhere in the core or wrappers (verified
  by inspection at authoring time; only `except SystemExit: raise` / `except KeyboardInterrupt:
  raise` / `except Exception as e:` appear).
- `crlb_n/a`: AUC discriminator base=0.5 exactly; validity is inherited from the sibling cell's own
  already-validated COLLAPSE/POPULARITY/RAW_SIGNAL_MIN controls (this cell recomputes but does not
  re-gate them -- they are cited via the reused, unmodified functions) PLUS this cell's own
  lambda=0.5-reduces-to-ZAVG structural cross-check (a stronger, cell-specific validity witness).
- `baseline_in_band`: verified via the xcheck (lambda=0.5 gate output == sibling's own validated
  ZAVG arm, to 1e-4) -- if the sibling's baseline were out of band, this cross-check would still
  hold (it's an identity, not a magnitude claim), so baseline validity is inherited from the
  sibling cell's own landed metrics, not re-derived here.
- `discriminator_survives_scale`: N/A per module docstring (no smaller scale exists for a read-only
  measurement over an already-full-scale npz); self-test substitutes real-code-path proof at N~40.
- `arms_differ_verified: true` (GATE_SEM vs PURE_TEXT vs PURE_GROUNDING hash-differ unless fitted
  lambda lands exactly on an endpoint, in which case `arms_differ_exempted` records the pair with
  the by-construction rationale -- seed_7 dry-run: lambda_sem=0.60, lambda_rel=0.90, neither at an
  endpoint, so no exemption fired).
- `HP_SCOPE`: gates (a)-(e) above apply to GATE_SEM/GATE_REL vs ZAVG/RAW_TEXT on TEST (held_idx)
  only; VAL-fit `val_score`/`curve` fields are model-selection diagnostics, never gated.
- `cardinality_ok`: `EXPECTED_N_UNITS = 1` per cell file (no sweep axis; 2 cell files = 2 seeds).
- `calibration_check: "default_ok_for_this_regime"` (AUC base 0.5 analytic; xcheck + inherited
  sibling controls witness it empirically).
- `deterministic_seeding: true` (fixed int seeds + offsets, `sorted()` everywhere, no `hash()` /
  `list(set())` for ordering or seeding).
- `real_code_path_and_signature_preflight`: self-test constructs the REAL bundle and calls the REAL
  `gated_table`/`learn_lambda`/`_r.semantic_eval`/`_r.relational_eval` functions at N~40 (not a
  synthetic-only branch); `substrate_signature` for `gated_table`/`learn_lambda` bound via direct
  keyword-matched calls throughout (both self-test and FULL code paths use the identical call
  signature -- no version-specific optional kwargs).
- `progress_logging: "print_flush_true"` (every `_log` call uses `flush=True`); `timeout_s` below
  the 1800s §17 mandatory-heartbeat threshold (see dispatch section).

## Dispatch plan
- `gated_fusion_text_grounding_encoder_seed_7`: DISPATCH NOW.
  `evalreps_seed_7.npz` landed 2026-07-28 13:06 (remote, confirmed via `dir` over ssh).
  `timeout_s = 1200` (20 min) -- measured local dry-run wall on the REAL seed_7 npz = 32.9s;
  1200s is a ~36x safety margin for remote CPU contention (the GPU box is concurrently training
  seed_13) and npz I/O variance, deliberately kept under the 1800s §17 heartbeat-mandatory
  threshold since genuine expected wall time is ~1 min.
- `gated_fusion_text_grounding_encoder_seed_13`: HOLD. `evalreps_seed_13.npz` had NOT landed at
  authoring time (grounding cell's seed_13 GPU training still in progress, `ckpt_seed_13_inprogress
  .pt` only). The cell FAILS LOUD (`FileNotFoundError`, failure_class `NPZ_NOT_LANDED`) rather than
  silently waiting if dispatched before landing -- so it is deliberately NOT queued yet. Dispatch
  trigger: `evalreps_seed_13.npz` appears in
  `data/exp_scale_meaning_learn_arc_heldout_v3_grounding/` on the remote (check via
  `tools/runner_status.py` / `dir` over ssh). Same `timeout_s = 1200`.

## REMOTE VERIFY (post-ship; mandatory before claiming "shipped")
After `queue_add.sh remote_cpu_queue gated_fusion_text_grounding_encoder_seed_7 ...`: verify (a) the
script + prereg + core sibling landed at `C:/dev/hd-instrument/experiments/` on marsh@home (scp
confirmation from queue_add.sh output, or an explicit `dir` check); (b) the queue entry appears in
remote `queue.json` (queue_add.py's own exit code; exit 5 = referent absent, treated as ship
failure); (c) once landed, `metrics.json` `run_mode == "full"` (not a phantom self-test landing per
§16) and `verdict` is one of the expected SINGLE_SEED_MEASURED_* values (not CELL_CRASHED).
