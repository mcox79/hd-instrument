# Pre-reg: predictive_coding_relative_threshold_v1 (ANCHOR 2)

**Filed-by:** exp_dev, 2026-08-09.
**Hand-off:** `notes/exp_dev_handoff_research_brain_script_acquisition_consolidation_2026-08-09.md`,
anchor 2. Parent research note:
`notes/research_brain_script_acquisition_consolidation_2026-08-09.md`, section 1.

## Framing (honest, per Director's task instructions)

This cell BUILDS the brain-faithful EST (Event Segmentation Theory) RELATIVE
prediction-error flag signal and A/B-tests it against the currently-wired
ABSOLUTE `threshold_gate`. It does NOT claim the substrate already owns this
signal -- the brain-fidelity audit rated the EST *principle*
PRINCIPLE-FOUNDATIONAL but the currently-wired flag (isolated verb-lemma
MET/UNMET polarity, `hdlab.consequence_learning_loop.teacher_verdict`) a
DEVIATION from it. `hdlab.predictive_coding.relative_threshold_gate` is new
code added this session; this pre-reg + cell is its first proof.

## Mechanism under test

`hdlab/predictive_coding.py::relative_threshold_gate` (new function, this
session): fires iff `residual_magnitude(t) / running_avg(residual_magnitude)_{t-1}
>= threshold`, where `running_avg` is a 0.05-weighted low-pass filter
(literature-pinned to Reynolds/Zacks/Braver 2007 Eq. 8; also added
`running_avg_update` + `BoundaryDecision` to the same module). Compared
against the EXISTING `threshold_gate` (fires iff `residual_magnitude(t) >=`
a fixed constant) -- the CURRENT signal this cell tests the new one against.
Both reuse `predict` / `residual` / `residual_magnitude` / `vanilla_hebbian_write`
verbatim (unchanged).

## Pre-registered bands (from the hand-off, verbatim -- NOT loosened)

- **MANDATORY PRE-CHECK** (must pass BEFORE any HARD-FAIL is accepted as a
  mechanism negative): confirm `residual_magnitude` itself discriminates a
  synthetic coherent-repeat sequence from a scrambled/shuffled-order control.
  A flat result without this passing is a harness bug, not a mechanism
  negative.
- **HARD-PASS**: relative-threshold F1 (mean across seeds) >= 0.75 against
  known/labeled boundaries AND not worse than the absolute `threshold_gate`'s
  own F1 by more than 0.05 F1 in the worst-case seed (`min(rel_f1 - abs_f1)
  across seeds >= -0.05`).
- **HARD-FAIL**: relative-threshold F1 (mean across seeds) < 0.50 -- ONLY
  after the mandatory pre-check passes.
- **MIDDLE_BAND**: everything else (0.50 <= F1_mean < 0.75, OR F1_mean >=
  0.75 but the worst-case margin condition fails).

## Corpus design (exp_dev autonomy; documented exploration, not p-hacked)

Labeled-boundary synthetic stream: `EVENTS` distinct single-item "scenes"
(ONE brand-new bipolar key/value pair per scene, matching the literal Zacks
movie-segmentation paradigm), each cycled `REPEATS_PER_EVENT` times.
Boundary label=1 at the first step of every event except event 0. Grouped
into alternating LOW-noise / MODERATE-noise blocks of `BLOCK_EVENTS` events
(observation-only bit-flip corruption at rate `P_NOISY` in noisy blocks;
the underlying memory always consolidates the TRUE value -- only the
CURRENT comparison observation is corrupted). Both gates evaluate the
IDENTICAL online W trajectory / residual trace in a single pass (isolates
the gate-comparison logic from any write-policy confound).

**Exploration before locking the design** (see the cell's own docstring
HYPOTHESIS section for full detail): tried (a) monotonic Hebbian-crosstalk-
only drift (no explicit noise) at multiple N/EVENTS/ITEMS_PER_EVENT/REPEATS
combinations -- ABS matched or beat REL in every configuration tried,
including deliberately high-alpha (up to alpha=2.5) overload regimes; (b) a
single clean/noisy 50/50 split at several `P_NOISY` levels 0.30-0.50 --
same finding, and P_NOISY approaching 0.5 degrades BOTH gates together
(task becomes information-theoretically unsolvable, not a fair test); (c)
the final alternating-block design at several decay constants
(0.05/0.10/0.15/0.20/0.30) and block sizes -- REL never beat ABS in any
variant tried. The locked design below (N=256, EVENTS=60,
REPEATS_PER_EVENT=5, BLOCK_EVENTS=15, P_NOISY=0.35, DECAY=0.05) is the
best-faith, literature-motivated (heteroscedastic per-context noise, the
actual Reynolds/Zacks/Braver motivation for self-referential comparison)
design from that exploration, locked BEFORE the 5-seed FULL run, not
selected post-hoc to force a verdict. DECAY=0.05 is the literature-cited
default (kept as primary despite trying faster decays in exploration, since
none reversed the qualitative finding).

```yaml
N_DIM: 256
EVENTS: 60
REPEATS_PER_EVENT: 5
BLOCK_EVENTS: 15
P_NOISY: 0.35
DECAY: 0.05
SEEDS_FULL: [7, 17, 23, 31, 41]
THRESH_ABS_GRID: 30 points, 0.02..0.60 (fixed a priori)
THRESH_REL_GRID: 19 points, 1.05..10.0 (fixed a priori)
```

## SCHEMA-VET checklist (per exp_dev.md sections 1-16)

- `cardinality_ok`: `EXPECTED_N_UNITS = len(SEEDS) = 5` (single sweep axis =
  seed); verdict logic emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if
  `len(all_results) != len(SEEDS)`.
- `arms_differ_verified`: META_RULE_AF hash-test on ABS-vs-REL boolean
  prediction arrays at each gate's own best threshold, per seed.
- `final_metrics_atomicity`: `tmp_replace` (via `experiments._seed_checkpoint.
  write_metrics`, tmp + `os.replace`).
- `except SystemExit / KeyboardInterrupt: raise` BEFORE `except Exception`
  (never `except:` or `except BaseException:`) -- grep-verified clean.
- `crlb_n_a`: boundary-detection F1 cell, not an argmax/top-k
  associative-recall capacity cell; no CRLB ceiling applies.
- `baseline_in_band` (META_RULE_AG): smoke asserts `0.05 < ABS_GATE
  best_f1_mean < 0.95` via `assert_discriminator_fires` (both directions).
- Discriminator survives scale: smoke uses the SAME full-N corpus
  parameters as FULL (DISCRIMINATOR-MUST-SURVIVE-SCALE option A); only
  n_seeds shrinks 5 -> 1.
- `HP_SCOPE`: `{"REL_GATE": ["REL_F1_GE_0P75", "WORST_MARGIN_GE_NEG0P05"],
  "ABS_GATE": []}` (ABS is the comparison baseline, no HP gate of its own).
- `calibration_check`: `default_ok_for_this_regime` -- grids and corpus
  constants fixed a priori per the exploration above, not tuned per-seed.
- `deterministic_seeding`: true -- `np.random.RandomState` throughout, no
  built-in `hash()`, no `list(set())` ordering (grep-verified clean).
- Structured gate claims (`record_gate`): `REL_F1_GE_0P75`,
  `WORST_MARGIN_GE_NEG0P05`, `REL_F1_MEAN_LT_0P50` -- all three persisted in
  `metrics.json.verdict_stats.structured_gate_claims`.

## Compute architecture

Sequential-CPU, numpy, no GPU batching candidate: N=256, T=300 steps/seed,
5 seeds -- full run completes in well under 1 second wall time (measured:
0.44s total). Per COMPUTE-PROPORTIONALITY / INLINE-LOCAL-MANDATE discipline,
this is a lightweight measurement run FOREGROUND-TO-COMPLETION, not routed
through remote queue_add.sh (smoke IS routed via direct invocation per the
SMOKE-ONLY-on-local convention's intent, though this cell's compute is too
trivial to warrant queue overhead either way -- flagged for the record).

## MEASURED RESULT (this pre-reg filed alongside the completed FULL run)

Mandatory pre-check: **PASSED** (`coherent_late_mean_residual=0.000`,
`scrambled_late_mean_residual=0.477`, `gap=0.477` -- residual_magnitude
cleanly discriminates a learnable-repeat sequence from an unlearnable
scrambled one; any F1 result below is a genuine mechanism reading, not a
harness artifact).

5-seed FULL (seeds 7/17/23/31/41):
- REL_GATE best-F1 per seed: 0.699, 0.743, 0.684, 0.675, 0.686 (mean=0.697,
  min=0.675)
- ABS_GATE best-F1 per seed: 0.919, 0.891, 0.871, 0.912, 0.933 (mean=0.905,
  min=0.871)
- worst-case margin (rel - abs): -0.248; mean margin: -0.208
- RANDOM_FLAG_CONTROL (base-rate-matched, telemetry only): F1 ~0.18-0.25

**Verdict: MIDDLE_BAND.** REL clears the 0.50 HARD-FAIL floor comfortably
and consistently (never a harness-bug-shaped flat/degenerate result) but
does not reach the 0.75 HARD-PASS bar, and is CONSISTENTLY, non-trivially
worse than ABS (worst-case margin -0.248, well outside the -0.05 tolerance)
across every one of the 5 seeds. This is an honest negative on the specific
mechanism as literature-pinned (a raw ratio to a 0.05-decay EMA of past
residual magnitude): dividing by a single noisy point-estimate of the
running mean appears to amplify per-step observation noise about as much as
it corrects for genuine context-level baseline drift, on this substrate's
bounded [0, ~0.5] cosine-residual measure (the "boundary spike" saturates
near a fixed ~0.5 chance ceiling rather than itself scaling multiplicatively
with context noise, undercutting the ratio's normalization benefit).

Per the hand-off's own tier framing ("informative regardless of outcome...
a clean negative would mean the absolute threshold is already adequate and
the relative-signal literature, while real, doesn't matter at this
substrate's operating point"): this result does NOT invalidate the
EST/self-referential-comparison PRINCIPLE (still literature-supported by two
independent lines, per the parent research note) -- it says the SIMPLEST
possible implementation (raw EMA ratio) of that principle does not clear a
bar over the absolute baseline on this substrate, at this operating point.
A z-score / variance-normalized comparison (rather than a raw mean-ratio)
is the natural next refinement if this signal is revisited, but that is a
DIFFERENT, more complex mechanism than what this hand-off pinned, and is
out of scope for this anchor.
