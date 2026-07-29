# Pre-reg: entity_state_replication_vet_cross_boundary_v1 (2026-07-29)

- Anchor: `entity_state_replication_vet_cross_boundary_v1`
- Cell: `experiments/exp_entity_state_replication_vet_cross_boundary_v1.py`
- No new modules. Pure EVAL-ONLY read of existing FROZEN encoders through the EXISTING
  calibration-validated `gen_cross_boundary` construction
  (`experiments/diag_order_critical_comprehension_calib_v1.py`). NO retrain, NO new mechanism
  (`hdlab/entity_slot_gate.py` NOT touched this cell).
- RE-DISPATCH NOTE: a prior attempt at this same question died with the Claude process overnight
  before anything shipped or committed. This is a fresh start; nothing from that attempt is reused
  besides the already-committed construction/encoder-loader machinery cited above.

## Prior-work check (substrate-KB, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "cross boundary entity tracking replication seed variance frozen
encoder mean pool margin calibration"` -- top hits: this session's own
`preregs/2026-07-28_entity_slot_gate_cross_boundary_v1.md` (cosine ~0.5, the SAME construction,
directly the prior cell this replication-vet follows up on) and
`notes/comprehension_situation_model_frontier_scoping.md` (cosine ~0.4, the frontier scoping note
that motivated both cells). No independent prior cell already answers the seed-13 replication
question -- the 2026-07-28 cell measured seed_7 only (+0.2083/+0.21 MEAN_POOL margin,
MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json and
MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json) and
explicitly left seed_13 unmeasured on THIS construction. **Verdict: genuinely novel
measurement (fills a stated gap in the immediately-prior cell); not a rediscovery.**

## Question

Does the frozen RELOBJ_v3 encoder's cross-boundary entity-tracking MEAN_POOL margin on
`gen_cross_boundary` REPLICATE at seed_13, or does it collapse the way the OLDER
`gen_entity_state` construction did (seed_7 +0.283 -> seed_13 +0.130, non-replicated)? Also: is
any signal objective-independent (v2 MLM-objective baseline, seed_7) or specific to the RELOBJ
training objective?

ONE variable = seed / encoder-objective identity. Construction, readouts, split, calibration gate
all held FIXED and IDENTICAL to the 2026-07-28 cell.

## Units (fixed list; no sweep, no chunked-file split -- EVAL-only, CPU, expected <10 min total
wall time; see `cell_chunked` exemption below)

1. `RELOBJ_v3_seed_13` -- `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_13.pt`
   (**THE key replication number** -- gates the verdict)
2. `RELOBJ_v3_seed_7` -- `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt`
   (within-run reproduction check of the cited +0.21 number, same code path as this cell, not the
   2026-07-28 cell's byte-different implementation -- informational cross-check)
3. `BASELINE_v2_seed_7` -- `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` (v2, the
   original MLM-style objective per `exp_scale_meaning_learn_arc_heldout_v2.py` docstring --
   answers "is cross-boundary tracking objective-independent or specific to RELOBJ training?")

All three ckpts share IDENTICAL architecture (`vocab=16000, max_len=128, d_model=512, n_layers=6,
n_heads=8, ffn_mult=4, pad_id=0` -- MEASURED@torch.load of all three `.pt` files, this session),
so `TinyTransformer` construction + the random-init-encoder control are directly comparable
across units.

## Readouts (per unit)

- **MEAN_POOL**: whole-sentence attention-mask-weighted mean pool over the frozen forward pass
  (reused verbatim: `experiments.diag_comprehension_readout_sweep_v1.readout_mean_pool` via
  `compute_hidden_cache`) -- the primary, gating readout.
- **CLAUSE_SPLIT_CONCAT**: `[h1 (unit-norm MEAN_POOL of clause1); h2 (unit-norm MEAN_POOL of
  clause2)]`, matched-scale per the 2026-07-28 cell's "Test B" finding (raw concat without
  unit-norm is a scale-mismatch artifact) -- informational side-readout, NOT part of the
  REPLICATES/FAILS gate (the 2026-07-28 cell found this readout ~flat vs MEAN_POOL, +0.03 gain at
  best; reported here for completeness on the new seed/objective units, not re-litigated).
- **RANDOM_INIT_ENCODER (MEAN_POOL)**: MANDATORY control -- same `TinyTransformer` architecture at
  the SAME ckpt's `model_cfg`, weights left at `torch.manual_seed`-fixed random init (zero training
  steps), scored through the identical MEAN_POOL readout + probe-fit pipeline. This is the control
  the frontier note flags as non-negotiable: "this session found random-init beat trained on the
  OLDER entity-state construction." Must NOT match/exceed the trained encoder's MEAN_POOL margin.
- **Scrambled-at-chance**: built into every `score_readout_arm` call (margin = coherent_acc -
  scrambled_acc where scrambled = `LOOP2._scramble_words`, identical word multiset, shuffled
  order) -- if scrambled itself decodes near-coherent, the margin collapses to ~0 by construction,
  so this is a structural control, not a separate arm.

## Compute architecture

- Class: **(b) sequential-CPU with justification.** This is pure inference (frozen forward passes,
  no gradient descent on the encoder) + tiny linear-probe fits (300 Adam steps on a 512- or
  1024-dim linear layer, sub-second each). No GPU-batching opportunity beyond what
  `compute_hidden_cache`'s existing `encode_batch=256` already provides. Estimated wall time:
  ~3 units x (1 trained-encoder pass + 1 random-init-encoder pass) x (whole-sentence + clause1 +
  clause2 encodes for train=1800/eval_coh=600/eval_scr=600 sentences) -- well under 10 minutes
  total on CPU per the same construction's measured cost in the 2026-07-28 smoke
  (MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json
  elapsed_s_total, single-unit full-N smoke completed in low hundreds of seconds).
- Storage strategy: `no_storage` -- no compositional chaining, no `SequenceMatrix`/Hebbian write of
  any kind this cell (that mechanism belongs to the SEPARATE, not-dispatched-here,
  `entity_slot_gate` cell). Pure encode -> probe -> score.

## Bands (envelope-fail-bands, set BEFORE running)

- **REPLICATES**: `RELOBJ_v3_seed_13.MEAN_POOL.margin >= 0.15` AND
  `RELOBJ_v3_seed_13.MEAN_POOL.comprehension_specific == True` (train-sanity + coherent-floor
  both clear) AND NOT structure-alone (random-init-encoder control on this unit does not clear
  `MARGIN_THRESH=0.15`, and trails the trained margin by >= `RANDOM_GATE_EPS=0.02`).
- **FAILS_TO_REPLICATE**: `RELOBJ_v3_seed_13.MEAN_POOL.margin < 0.05` OR
  `RELOBJ_v3_seed_13.MEAN_POOL.margin <= 0.5 * RELOBJ_v3_seed_7.MEAN_POOL.margin` (mirrors the
  ~46% ratio of the prior ENTITY_STATE collapse, +0.130/+0.283 = 0.46 -- a comparable proportional
  drop here is diagnosed as the SAME seed-luck failure mode, not noise).
- **HARD_FAIL_STRUCTURE_ALONE** (overrides REPLICATES even if the margin number clears): if the
  seed_13 random-init-encoder control's MEAN_POOL margin is within `RANDOM_GATE_EPS=0.02` of (or
  exceeds) the trained seed_13 MEAN_POOL margin -- structure/architecture alone explains the
  signal, not the RELOBJ-learned semantics.
- **MIDDLE_BAND**: everything else (e.g. seed_13 margin in [0.05, 0.15), or a partial ~20-40% drop
  from seed_7 that is a real decline but not a full collapse).
- `BASELINE_v2_seed_7` result is **informational only** (objective-independence question), does
  NOT gate REPLICATES/FAILS/MIDDLE_BAND for the seed_13 headline verdict.
- `RELOBJ_v3_seed_7` (within-run reproduction) is **informational only** -- a sanity cross-check
  that this cell's own code path reproduces the ~+0.21 number the 2026-07-28 cell measured with
  different code; large deviation (>0.10) would flag an implementation discrepancy requiring
  investigation before trusting the seed_13 number, but does not itself gate the verdict.

### HP_SCOPE

```yaml
HP_SCOPE:
  RELOBJ_v3_seed_13: [REPLICATES, FAILS_TO_REPLICATE, MIDDLE_BAND, HARD_FAIL_STRUCTURE_ALONE]
  RELOBJ_v3_seed_7: []       # informational cross-check only
  BASELINE_v2_seed_7: []     # informational objective-independence check only
```

## Gate checklist (per exp_dev.md canonical file)

- `arms_differ_verified: true` -- hash-check over {MEAN_POOL, CLAUSE_SPLIT_CONCAT,
  RANDOM_INIT_ENCODER} eval-coherent feature arrays per unit (META_RULE_AF).
- `final_metrics_atomicity: "tmp_replace"` -- single-shot run, `metrics.json.tmp` +
  `os.replace()`.
- `except SystemExit: raise` before `except Exception` (no `BaseException`) -- YES.
- `crlb_n/a: "accuracy-margin discriminator over a binary probe, not a capacity/noise regime"`.
- `baseline_in_band: true` -- MEAN_POOL coherent_acc MEASURED 0.63-0.75 range on this construction
  across the 2026-07-28 calibration + seed_7 own-encoder runs, comfortably inside [0.05, 0.95].
- Discriminator survives scale: construction runs at FULL scale (train=1800, eval_per_label=300,
  IDENTICAL to the 2026-07-28 `FULL_CFG`) for every unit -- Option A, no smaller smoke-only regime.
- `HARD_PASS`-equivalent (REPLICATES) strictly above floor: 0.15 threshold sits well inside the
  measured 0.13-0.28 range this construction/family has produced across all measured points to
  date -- not a floor-hugging threshold.
- `cardinality_ok`: `EXPECTED_N_UNITS = 3` (fixed list above, no sweep axis).
- Per-unit failure-class instrumentation: every unit wrapped in `try/except Exception` (no bare
  except), failure recorded to `per_unit[key]["failure_class"]`, no silent continue.
- `calibration_check: "adaptive_with_discriminator_gate"` -- this cell RE-RUNS the CROSS_BOUNDARY
  calibration gate itself at dispatch time (imported verbatim from
  `experiments.exp_entity_slot_gate_cross_boundary_v1.run_calibration_gate`, same function, not
  reimplemented) and SKIPS all own-encoder scoring (`CALIBRATION_GATE_FAIL`) if no known reader
  clears `MARGIN_THRESH=0.15`/`COHERENT_FLOOR=0.65` at this exact regime.
- `cell_chunked: false` -- **EXEMPTION per §13A**: this is a lightweight (<10 min wall,
  MEASURED-estimated from the cited prior smoke), CPU-only, EVAL-ONLY (no gradient training of any
  mechanism) cell; the immediately-prior cell in this same family
  (`exp_entity_slot_gate_cross_boundary_v1.py`) used the identical single-file +
  `write_partial`/`resumable_seeds`-per-unit pattern (not physically separate seed files) and that
  precedent is followed here verbatim -- per-unit `write_partial` still gives runner-death
  resilience (a crash after unit 1 preserves unit 1's result) without the overhead of 3 separate
  cell files for a sub-10-minute run.
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true`
  (`CellHeartbeat`, `interval_s=30`), `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"` -- N/A trigger technically (expected `timeout_s < 1800`)
  but declared anyway since `_log` already uses `flush=True` throughout (reused convention).
- `deterministic_seeding: true` -- single fixed `SEED = 20260728` (MATCHES the construction seed
  used by both the diag script and the 2026-07-28 cell, so the identical train/eval split and
  identical scrambled sentences are reused/reproduced exactly), no `hash()`-derived seeding
  anywhere in this cell.

## Self-test (`--self-test`)

Tiny REAL-code-path pass: `train_target=40, eval_target_per_label=20`, ONE unit
(`RELOBJ_v3_seed_7`), calibration gate COMPUTED but not hard-blocking at this tiny scale
(`enforce_calibration=False`) -- constructs the ACTUAL `gen_cross_boundary`, `load_frozen_encoder`
(real ckpt), `compute_hidden_cache`, `fit_binary_probe`, `TinyTransformer` (random-init control)
objects, not a synthetic-only branch (Gate F.1).

## Dispatch plan

Given the compute-proportionality rule (this is a DIRECTIONAL/replication-gate question, cheapest
decisive method = re-run the exact existing readout machinery, no new training) and the
INLINE-LOCAL mandate, this cell is run **foreground-to-completion locally** (estimated well under
10 minutes) rather than queued -- there is no long-running heavy fit here that needs remote/GPU
routing, and the explicit re-dispatch context (prior attempt died mid-flight overnight) makes a
short, observable, foreground run the safer choice for THIS specific vet. The commit (this
pre-reg + the cell file, committed BEFORE running) is what survives a process exit; the run itself
completing inline is the verdict delivery mechanism. If, contrary to the estimate, `--self-test`
or `--full` run past ~8 minutes wall without finishing, the fallback is `remote_cpu_queue` (GPU is
reported free but unneeded for CPU-only frozen-forward-pass inference).
