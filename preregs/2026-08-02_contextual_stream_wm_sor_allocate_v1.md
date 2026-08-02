# Pre-reg: contextual_stream_wm_sor_allocate_v1 (DG/CA3 match-or-allocate fix)

Cell: `experiments/exp_contextual_stream_wm_sor_allocate_v1.py`
Prior cell (unchanged, reused as task/vocab/baseline source):
`experiments/exp_contextual_stream_wm_sor_probe1_v1.py`
(metrics: `data/exp_contextual_stream_wm_sor_probe1_v1/metrics.json`, MIDDLE_PARTIAL_SIGNAL)

## Functional requirements
- FR1: a NOVEL entity's first touch must route to an empty/least-occupied slot (allocate),
  not smear across occupied slots. Existing primitive that partially addresses this:
  `PEGatedSlotWM.addr_net` content competition (does NOT have a novelty/occupancy signal).
- FR2: a FAMILIAR entity must still route via content-match pattern completion (unchanged).
- FR3: lossy HRR-unbind recall readback should be cleaned up via CA3 pattern completion
  (`hdlab.iterative_attractor.iterative_cleanup`) before scoring.

## PREREQUISITE FINDING (2026-08-02, discovered during --self-test)
`SlotAttentionWM`/`PEGatedSlotWM`'s `init_slots` zero-initializes all K slots identically, and
`addr_net`/`gate`/write are fully permutation-symmetric functions of `(addr_src, slot_k)`. When
every `slot_k` is bit-identical, the function evaluated per slot is bit-identical for every k --
an exact mathematical fixed point that NO amount of gradient training can break (identical
inputs to a deterministic function always give identical outputs). MEASURED@ this session (direct
debug script, `train_on(0,48,32,30)` then a fresh eval rollout): a TRAINED PEGatedSlotWM's final
slot norms are bit-identical across all 8 slots, for every batch item. This means the prior
probe1 `route_consistency=1.00` / `allocate_rate=0.167` numbers were an argmax TIE-BREAK
ARTIFACT (ties always resolve to the same index), not genuine per-entity slot routing; the
measured `recall_acc=0.336` came from a single collapsed HRR-superposition recency-weighted
trace, not real multi-slot maintenance. This is reported honestly as a re-interpretation of the
PRIOR landed cell's brain-metric claim (its `brain_metric_ok=True` was a false positive under
this reading) -- flagged for Director/Skunkworks follow-up, not silently patched over.

**Fix applied here (`_SlotInitFix` mixin, SHARED prerequisite):** each slot gets a small LEARNED
per-slot init bias (`0.01 * randn`, Locatello 2020 Slot-Attention's own i.i.d. per-slot init
convention) instead of `torch.zeros`, breaking the tie from step 0. Init magnitude kept well
below `OCCUPIED_THRESH` so it does not itself register as "occupied". Applied to BOTH `ON_BASE`
(`ReproducedBaseWM`) and `ON_ALLOC`/`ON_ALLOC_RAND` (`AllocateGatedSlotWM`) so the allocate-vs-
no-allocate comparison isolates the NEW mechanism's own marginal lift on a now-functional
(non-degenerate) baseline, per the "ONE VARIABLE" discipline.

## THE ONE VARIABLE: DG/CA3 match-or-allocate
`AllocateGatedSlotWM(_SlotInitFix, PEGatedSlotWM)`: `addr_net`/`role_key_net`/`bind`/`unbind`/
`boundary_k` byte-identical to `PEGatedSlotWM`. Adds an ADDITIVE bias on `addr_logits`:
`alloc_bonus_k = alloc_gain * novelty * (1 - occupancy_k)`, where:
- `occupancy_k = ||slot_k||` (no extra state; empty ~0, written ~1 per Plate 1995 bind-norm).
- `novelty = (1 - max_k_occupied(familiarity_k)) * 0.5`, `familiarity_k` = cosine overlap between
  the incoming entity's `hdlab.hippocampal_encoder.DGProjection`-encoded identity fingerprint and
  a per-slot running DG-fingerprint bank (`id_bank`, updated with the SAME write weight `w_k` as
  slot content). Unoccupied slots forced to familiarity=-1 (never "familiar").
- DGProjection (dg_dim = D_MODEL*8, sparsity=0.08) is FIXED/unlearned (zero trainable params) --
  supplied STRUCTURE per the organ's own contract, not a hard-coded routing decision.
- Recall cleanup: `iterative_cleanup` (temp=4.0, max_steps=6, alpha=0.5) applied to the readback
  ONLY at eval time (training loss backprops through the raw, uncleaned readback so cleanup
  cannot distort learned weights). Reported both ways (raw vs cleanup), tagged, so its own
  contribution isn't conflated with the allocate fix.

## Arms
- `OFF`: unchanged reservoir floor (verbatim import from probe1_v1).
- `ON_BASE`: `ReproducedBaseWM` (PEGatedSlotWM + shared init fix), retrained fresh this run.
- `ON_ALLOC`: `AllocateGatedSlotWM` (the fix). + shuffled-slot-id placebo.
- `ON_ALLOC_RAND`: `AllocateGatedSlotWM(random_alloc=True)` -- can-fail ablation: the novelty-
  driven bonus replaced by an uninformative per-event random per-slot bonus of matched scale.

## Pre-registered bands (fixed before the full run)
- `FLOOR_MAX = 0.20` (unchanged from probe1; OFF must stay at/below).
- `PASS_MIN = 0.75`, `PASS_LIFT_MIN = 0.50` (ON_ALLOC vs OFF; unchanged targets from probe1).
- `HARD_FAIL_LIFT = 0.10` (ON_ALLOC <= OFF + this -> no lift at all).
- `ALLOC_LIFT_MIN = 0.05` (ON_ALLOC must beat ON_BASE by this -- the fix's OWN contribution).
- `RANDCTRL_MAX_LIFT = 0.10` (ON_ALLOC_RAND must NOT beat ON_BASE by more than this -- can-fail).
- `ALLOCATE_RATE_MIN = 0.40` (allocate_rate must clear this, vs prior-probe1's 0.167).
- `ALLOC_SELECTIVITY_MIN = 1.5` (novelty(first-write-touch) / novelty(repeat-touch) -- the
  allocate brain-metric; NOTE: two unrelated sparse ternary DG codes have EXPECTED cosine
  overlap ~0, not -1, so a "novel" entity's novelty clusters near 0.5 not 1.0 -- the
  discriminating signal is the GAP vs familiar (~0.0-0.15), verified in `--self-test`).
- `SPIKE_RATIO_MIN = 2.0`, `ROUTE_CONSIST_MIN = 0.80` (preserved brain-metrics from probe1;
  must NOT regress on ON_ALLOC).
- Controls that must fail: floor (OFF <= 0.20), placebo (shuffled slot ids, <= floor+0.15),
  position-only (<= floor).

## Verdict logic
`HARD_PASS_DG_MATCH_OR_ALLOCATE_RESOLVES_SOR` requires: accuracy HARD-PASS (ON_ALLOC >= 0.75,
both seeds, lift over OFF >= 0.50) AND brain_metric_ok (spike+route) AND
allocate_selectivity_ok AND allocate_rate_ok AND randctrl_failed (can-fail control genuinely
fails) AND placebo_failed AND ON_ALLOC beats ON_BASE by >= ALLOC_LIFT_MIN. Partial-signal /
confound / no-lift outcomes are distinct MIDDLE/HARD_FAIL verdicts (see `decide_verdict` in the
cell) -- MIDDLE is an honest, reportable outcome, not a failure to force past.

## Compute architecture
Sequential-CPU (numpy DGProjection + torch autograd loop); wall time < 10 min per cell-author
foreground call, justified by the small D_MODEL=32/dg_dim=256 regime and per-unit checkpoint
resumability (`tools/exp_checkpoint.py`) across chained foreground calls. Not a GPU-batching
candidate (small tensors, DG numpy round-trip per step dominates any matmul benefit).

## Storage strategy
No persistent multi-item store (in-memory training regime); n/a for sharded/bundled distinction.

## Cardinality
`EXPECTED_N_UNITS = 2 seeds x 4 unit-keys (OFF, ON_BASE, ON_ALLOC, ON_ALLOC_RAND) = 8` for
`full` mode (each `ON_ALLOC` unit-key also includes its placebo run in the same training call).

## Schema-vet checklist
- `cell_chunked`: true (per-(arm,seed) checkpoint via `tools/exp_checkpoint.py`).
- `start_marker_written`: n/a (uses `CellHeartbeat` + `tools/exp_checkpoint.py` durable per-unit
  shard instead of a separate start-marker file; every unit write is itself proof of progress).
- `crash_diagnostic_present`: true (`except SystemExit/KeyboardInterrupt: raise` before
  `except Exception` with FATAL print + `SystemExit(2)`; no bare except/BaseException, grep-
  verified clean).
- `heartbeat_present`: true (`CellHeartbeat`, interval_s=20).
- `arms_differ_verified`: true (`_arms_differ_selftest`, hash-checked in `--self-test`).
- `final_metrics_atomicity`: `tmp_replace` (`metrics.json.tmp` + `os.replace`).
- `crlb_n/a`: no closed-form noise floor for this discrete-vocabulary recall task; reachability
  judged empirically via the moderate-scale probe (see below), not analytically.
- `baseline_in_band`: OFF measured 0.094 (self-test)/0.062 position-only, well within
  (0.05, 0.95); not saturated.
- `discriminator_reachability`: MEASURED@ moderate-scale probe (this session, n_tr=160/ep=150/
  seed=0, informal, not the final full-run config): BASE=0.271, ALLOC raw=0.323 (lift +0.052),
  allocate_rate 0.20->0.559, allocate_selectivity=1.506, spike_ratio_WR=1.68, route_consistency
  =0.539 -- directional lift confirmed present at HALF the planned FULL budget (224 train/200
  epochs), so the FULL config is not expected to be underpowered relative to the observed effect
  size, though route_consistency/spike_ratio are the tightest bands (near their floors at the
  moderate scale) and may land MIDDLE rather than HARD_PASS.

## Calibration
`adaptive_with_discriminator_gate`: N/A -- no adaptive calibration used; all bands fixed before
running, per probe1's original bands plus new bands for the allocate-specific metrics (chosen to
mirror the existing `SPIKE_RATIO_MIN=2.0` precedent, i.e. "notably above 1.0/chance", not tuned
post-hoc against an observed number -- the moderate-scale probe's 1.506 for `ALLOC_SELECTIVITY_MIN
=1.5` is close, tagged honestly as MEASURED@ pre-full-run rather than retroactively lowered).

## Numbers tagged
- prior probe1 recall/allocate_rate: MEASURED@data/exp_contextual_stream_wm_sor_probe1_v1/
  metrics.json:summary.
- degenerate-symmetry finding: MEASURED@ this session's direct debug script (not persisted to
  disk as an artifact; reproducible via the `_SlotInitFix` docstring's stated procedure).
- moderate-scale probe numbers: MEASURED@ this session's ad hoc script (not the cell's official
  self-test/full path; informal pre-full-run calibration check only).
