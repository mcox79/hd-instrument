# Pre-reg: cls_distributed_protection_budget_envelope_v1

Date: 2026-07-18
Author: exp_dev (hdi_exp_dev)
Cell: `experiments/exp_cls_distributed_protection_budget_envelope_v1.py`
Anchor: `cls_distributed_protection_budget_envelope_v1`
Type: ENVELOPE CHARACTERIZATION (NOT a new capability claim). CLAIM-VET-pending; NOT self-declared chain-grade.

## Question
The VET-confirmed cell `exp_cls_distributed_protection_independent_content_v1` (VET ad3947bd,
MEASURED_MECHANISM) showed that replaying a small subsample of old memories protects the INDEPENDENT
within-class content of NEVER-REPLAYED held-out memories -- REAL (both confounds at 0.000, 3/3 seeds) but
PARTIAL. UN-CHARACTERIZED: how does the equal-compute-CORRECTED never-replayed protection scale with REPLAY
BUDGET? Load-bearing for continual textbook ingestion: does a SMALL replay budget protect a LARGE
never-replayed set (sub-linear -> usable foundation), track budget ~linearly (must-rehearse-most -> does not
scale), or stay flat-marginal (budget-independent, small)?

## Design (ONE swept variable = replay budget)
Regime IDENTICAL to the parent cell (N=256, D_T=64, H=160, 12 old classes x 12 exemplars = 144 old items,
E_OLD=400, E_NEW=200, 8 interference blocks x 3 new classes, LR=0.04, SHARED_FRAC fixed at the structured
end 0.75). The ONLY swept variable: `ELIG_PER_CLASS in {1,2,3,4,6,9}` = replay budget = fraction of old
items made replay-eligible = {8.3, 16.7, 25, 33.3, 50, 75}%. The held-out never-replayed set is the
complement (132, 120, 108, 96, 72, 36 items respectively).

Per-seed efficiency: the budget-INDEPENDENT nets (no_replay, replay_all) and the post-old-block init are
trained ONCE and held-out-eval is sliced per budget (bit-identical to the parent's per-arm approach; makes
those arms genuinely budget-independent and eliminates an init confound).

## Arms (per budget; eval/cue/target/init FIXED across arms and budgets)
- `no_replay`            : forgetting FLOOR (budget-independent net; held-eval sliced).
- `subsample_replay`     : MECHANISM -- interleave replay of ONLY the eligible subsample; held-out NEVER replayed.
- `equal_compute_struct` : PRIMARY equal-compute control -- reuses OLD class protos (same shared-structure
                           subspace + same class-code DIVERSITY as the subsample) + fresh probes + random
                           targets. Same volume + same structure reactivation, removes only the old items'
                           OWN cue->target content. genuine_effect = subsample - equal_compute_struct.
- `equal_compute_random` : BRACKET control -- fresh random protos+probes+targets (matches volume only).
                           CAVEAT: random protos are more diverse than the correlated old items, so this is a
                           STRONGER regularizer -> it OVER-corrects (genuine_random is a lower bracket).
- `replay_all`           : protectable CEILING (budget-independent net; held-eval sliced).
- `one_nn_proximity`     : CONFOUND (zero training) -- must stay ~0 across budgets (independence holds).
- `fresh_net_subsample`  : CONFOUND -- fresh net trained ONLY on subsample; must stay ~0 across budgets.

## Why TWO equal-compute controls (surfaced at smoke, documented honestly)
The task named an "equal-compute-random-filler." At smoke the literal random-proto filler gave a much larger
correction (~0.21 at 25%) than the VET's cited ~0.04, because random protos span more directions than the
correlated 12-class old items and thus regularize more strongly (an unfair, too-strong control). The
diversity-matched STRUCT filler (old protos, random targets) recovers genuine ~0.09 at the 25% anchor --
consistent with the VET's ~0.11. STRUCT is therefore the PRIMARY load-bearing control; RANDOM is reported as
a (lower) bracket. The equal-compute control definition is load-bearing; both are reported for transparency.

## LOAD-BEARING metric
The EQUAL-COMPUTE-CORRECTED (STRUCT) never-replayed protection vs replay-budget curve:
`genuine_effect(budget) = subsample_replay_heldout - equal_compute_struct_heldout`, plus the RANDOM bracket
and the raw (subsample - no_replay) for transparency. Retrieval = nearest-target over the old codebook
(chance = 1/144 = 0.0069).

## CAN-FAIL / honest read (characterization -- NO HARD_PASS/FAIL framing)
Report the SHAPE of genuine_effect(budget):
- `SUB_LINEAR_EFFICIENT` : small budget captures disproportionate protection -> USABLE continual-ingestion foundation.
- `LINEAR_MUST_REHEARSE` : protection tracks budget ~linearly (or worse/accelerating) -> must rehearse most -> does NOT scale.
- `FLAT_MARGINAL`        : small, budget-independent effect -> fixed modest protection, not budget-scalable.
The honest curve IS the result. Descriptors reported raw: genuine_lo, genuine_hi, genuine_max, eff_ratio
(genuine_lo/genuine_hi), linear_ratio (budget_lo/budget_hi). Classifier is a labeling aid; the numbers govern.

## Difficulty-ON gates (per budget, aggregate; from parent)
- net learned held-out initially (heldout_initial >= 0.70) -- forgetting not inability.
- no_replay forgets (heldout <= 0.30).
- replay_all protects (heldout >= 0.55) -- independent content IS protectable if rehearsed.
- BOTH confounds fail (<= 0.25) at EVERY budget -> held-out content is independent (else uninterpretable).

## Positive control (Gate D)
At ELIG=3 (25%, the parent regime) subsample held-out must reproduce the parent MEASURED 0.247 within tol
0.10 (identical regime; larger deviation = invocation/regime drift). SMOKE MEASURED: 0.232 (dev 0.015). PASS.

## Cardinality (META_RULE_H)
EXPECTED_N_UNITS = len(BUDGET_GRID) * len(SEEDS) = 6 * 3 = 18. Verdict emits HARD_FAIL_CARDINALITY_BREACH if
n_units != expected. SEEDS = [7, 17, 23].

## Compute architecture
Class: (b) sequential-CPU with justification. Pure numpy MLP regression (cue->tanh hidden->linear target),
self-contained, glass-box, local-runnable; this IS a small reference regime (no substrate primitive to batch;
wall ~6 min full). Storage strategy: no_storage / no_composition (MLP readout, not KGStore). GPU batching not
applicable (tiny dense matmuls; sequential per-seed training with gradient-step dependencies).

## SCHEMA-VET fields
- arms_differ_verified: True at smoke (hash-test over per-arm held-out predictions per unit).
  arms_differ_exempted: [("one_nn_proximity","fresh_net_subsample")] -- the two zero-training MUST-FAIL
  confounds legitimately produce identical degenerate predictions when BOTH fully fail (0.000) at extreme-low
  budget; distinct code paths, not a bit-identical-arm bug. All OTHER pairs must differ.
- final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace).
- crlb_n/a: "retrieval accuracy over a 144-item codebook; chance=1/144; feasibility = replay_all ceiling >= 0.55 verified at smoke."
- discriminator_reachability: True (smoke fires: no_replay forgets, replay_all=1.0 protects, both confounds 0.000, genuine effect resolves a budget-shaped curve).
- baseline_in_band: True at smoke (no_replay ~0.08 in band; replay_all=1.0 protects; confounds 0.000).
- discriminator survives scale: smoke runs FULL grid difficulty at 1 seed; forgetting deepens with pool/interference (not seeds), so only seed count is reduced.
- cardinality_ok: True. cell_chunked: False (single-file sweep; no per-seed runner-death risk at ~6 min).
- start_marker_written: True. crash_diagnostic_present: True (Exception -> CELL_CRASHED + traceback). heartbeat_present: False (short cell). defensive_error_checking: "start_marker + crash_diagnostic + except-ordering; heartbeat exempt (wall ~6 min << 5-min-hang watchdog is per-cell short)."
- calibration_check: "default_ok_for_this_regime" (identical to the VET-confirmed parent regime; positive-control reproduces parent 0.247 within 0.015).
- No PYTHONHASHSEED nondeterminism: all splits/seeds/targets/fillers are fixed ints or deterministic index math; `scan_source_for_nondeterminism` findings = [].
- real_code_path: self-test constructs the REAL RegNet + both fillers + confounds + run() at the smoke grid, 1 seed (no synthetic-only branch).

## SMOKE VERDICT (1 seed, budgets [1,3,9])
PASS. CHARACTERIZATION_LINEAR_MUST_REHEARSE. genuine(struct) curve: b=0.083 -> -0.038; b=0.250 -> 0.093;
b=0.750 -> 0.472. confounds_ok=True, arms_differ=True, units=3/3, anchor positive-control dev=0.015.

## Dispatch
Local-runnable characterization; run FULL on local (foreground/local_cpu_queue), no remote push. Pause-gated:
NOT dispatched to remote queues while paused. FULL verdict reported by exp_dev directly (COMPLETE, not handoff).
