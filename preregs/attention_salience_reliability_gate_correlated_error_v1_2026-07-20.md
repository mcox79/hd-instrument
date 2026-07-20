# Pre-registration: attention/salience RELIABILITY-GATE, CORRELATED/SYSTEMATIC-ERROR scope-bound test (v1)

Cell: `experiments/exp_attention_salience_reliability_gate_correlated_error_v1.py`
Author: hdi_exp_dev. Date: 2026-07-20.

## WHY THIS CELL EXISTS (VET-banked next test on atom 29376)

`exp_attention_salience_reliability_gate_independent_channel_v1` landed `HARD_PASS` (atom 29376,
`data/substrate_index/math/atoms.jsonl`): the substrate DERIVES a leak-free, source-level,
leave-one-item-out reliability signal (`auc_unrel=0.6764`, below the oracle ceiling `0.698` --
structurally not a proxy) that measurably improves consolidation on a low-reliability item subset
(`+0.0634` primary, 5/5 seeds positive). This is the FIRST break of the substrate's recurring
"uses-injected-signal-it-cannot-DERIVE" pattern. The adversarial VET banked the decisive next test as a
named scope bound: informativeness was demonstrated only under an INDEPENDENT-RANDOM error model (every
wrong observation is a fresh, uncorrelated random draw). CORRELATED / SYSTEMATIC source errors -- the
textbook case that fools a consistency-based reliability estimate (common-mode bias / correlated raters;
violates the independent-noise assumption underlying Kalman-gain and Ernst & Banks optimal cue
combination) -- were explicitly left UNTESTED. This cell is that test.

## PRIOR-WORK CHECK (substrate-KB concept-query, exp_dev standing rule)

`bash tools/substrate_query.sh "correlated systematic source error reliability gate common-mode bias
consistency estimator"` -- top hit `entity='correlated'` (generic lexical concept node, cosine=0.332,
wordnet/atoms sourced), rest are unrelated resource-estimate notes at cosine<=0.317. **No prior
experiment-atom rediscovery at cosine>0.30.** This is a DELIBERATE, VET-directed continuation of atom
29376's own named scope bound, not a rediscovery; direct lineage is read from `atoms.jsonl` line 29376
(the CG cell) and its `scope_bounds` field, not surfaced via the concept-query.

## MECHANISM: ONE VARIABLE DIFFERS (error-generation content only)

Reuses atom 29376's LOCKED regime and code UNCHANGED (`S_LO=S_HI=10`, `V_PER_TIER=4000` -- VET framing
note: lift is robust 600-4000, reusing the mid-large population per that note -- `N=64`, `n_obs` in
[4,6], `P_LO=0.20`, `P_HI=0.65`, `MIX_MAJ=0.75`, source-level leave-one-item-out aggregation, `TAU`=
per-seed median source score, identical 6 arms). Two independent `numpy.random.Generator`s are spawned
per seed via `SeedSequence(seed).spawn(2)`:

- `rng_main` (child 0): codebook generation, item-tier assignment, per-item source draws, per-observation
  correctness draws. **IDENTICAL across both error modes for a given seed** -- verified in `_self_test()`
  by re-spawning the same child and asserting the derived codebook draw is bit-identical across two
  independent `SeedSequence` instantiations.
- `rng_err` (child 1): controls ONLY the vector CONTENT of WRONG observations. This is the ONLY stream
  whose usage differs by mode:
  - **`independent_random`** (atom 29376's exact construction): each wrong observation draws a FRESH,
    independent random bipolar vector from `rng_err`. Run here as a **Gate-D positive control**: if this
    arm does not reproduce atom 29376's `auc_unrel_mean` / `mean_delta_hard_unrel` within tolerance, this
    reimplementation is suspect and the correlated-mode verdict is NOT trusted.
  - **`correlated_systematic`** (the adversarial construction): one "decoy" vector per item,
    `decoy_v[i] ~ Bipolar(N)`, drawn once from `rng_err` (batched, so it never perturbs `rng_main`'s call
    sequence). EVERY source that errs on item `i` -- regardless of which source, or how many sources err
    on that item -- emits the SAME `decoy_v[i]` instead of independent noise. This models a
    "confidently-wrong" source population: whenever >=2 sources err on the same item (frequent for
    unrel-tier items, majority-sourced from the `P_LO=0.20` pool at an 80% error rate), their wrong
    observations are IDENTICAL to each other -- a common-mode / correlated-rater bias, the textbook case
    that fools a peer-consistency-based reliability estimator, because the raw ingredient
    (`same_item_loo[i,j] = cosine(obs_j, sum_{k!=j} obs_k)`) cannot distinguish "these agree because both
    are correct" from "these agree because they share a common bias."

Because `rng_main` is identical across modes, item/tier assignment, which sources observe which item, and
which individual `(item, obs)` pairs are correct/incorrect are BIT-IDENTICAL between the two runs at a
given seed -- ONLY the vector content of wrong observations changes. This isolates the causal variable
named in the task (error-correlation structure) from task difficulty, source-reliability rates, or
sampling variation.

## PRE-REG BANDS (locked BEFORE full dispatch)

Regime: identical to atom 29376 (`S=20`, `V_PER_TIER=4000`, `V=8000`, `N=64`, `n_obs` in [4,6], `P_LO=0.20`,
`P_HI=0.65`, `MIX_MAJ=0.75`). SEEDS_FULL=[7,17,23,31,41] (same 5 seeds as atom 29376, for direct
comparability). SEEDS_SMOKE=[7] (Option A -- smoke IS full-N/full-V, both modes, 1 seed; no separate
scale-up regime exists, same convention as the parent cell).

**GATE D (positive control; MUST hold before the correlated-mode verdict is trusted):**
```
|auc_unrel_mean(independent_random) - 0.6764| <= 0.10   AND
|mean_delta_hard_unrel(independent_random) - 0.0634| <= 0.10
```
If Gate D fails: `HARD_FAIL_REIMPLEMENTATION_MISMATCH` -- the correlated-mode result is NOT interpreted.

**PRIMARY VERDICT AXIS: correlated_systematic mode, hard_gate arm (contingent on Gate D holding):**

`HARD_PASS_CG_GENERALIZES` (ALL required):
1. `mean_5seed(delta_hard_unrel) >= 0.05` (correlated mode).
2. `>=4/5 seeds` positive-direction.
3. Shuffled control: `delta_shuffled_hard_unrel <= 0.00` on all 5 seeds.
4. Do-no-harm: `mean_5seed(delta_hard_rel) >= -0.03`.
5. `0.55 <= auc_unrel(correlated) <= 0.90` (still informative, not degenerate).
6. `baseline_in_band` (`0.05 < ungated_unrel < 0.95`) and `baseline_rel_non_ceiling` (`ungated_rel < 0.97`)
   hold under correlated_systematic mode too.

`HARD_FAIL_CORRELATED_ERROR_FOOLS_CHANNEL` (either):
- `auc_unrel(correlated) <= 0.55` -- the score collapses toward or below chance; the channel can no longer
  separate correct from confidently-wrong under correlated errors.
- `mean_5seed(delta_hard_unrel) <= 0.02` (correlated mode) -- ties or actively hurts.

`MIDDLE_BAND`: partial signal (small positive lift below floor, or majority-direction not met, with AUC
still nominally in-band).

**HP_SCOPE:**
```yaml
HP_SCOPE:
  independent_random: [gate_d_positive_control_only]   # not itself re-adjudicated HARD_PASS/HARD_FAIL
  correlated_systematic.hard_gate: [delta_floor_0.05, direction_majority, shuffled_control, do_no_harm, auc_in_band]
  correlated_systematic.soft_multiplier: [reported_not_gated]   # secondary, disclosed only
  oracle, shuffled_hard_gate, shuffled_multiplier (both modes): [diagnostic_or_control_only]
```

## SCHEMA-VET / CELL-TEMPLATE FIELDS

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = len(SEEDS) * len(ERROR_MODES) = 10 full / 2 smoke
arms_differ_verified: true           # hash-checked at self-test/smoke: 6 arms distinct, BOTH modes
final_metrics_atomicity: "tmp_replace"
except_ordering: "SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare/BaseException"
crlb_n_a: "not a CRLB/JL-capacity cell; reuses atom 29376's locked regime unchanged; bottleneck under test
  is whether error-correlation structure (not estimation precision) breaks the channel"
discriminator_reachability: true
baseline_in_band: "verified at self-test/smoke (V=8000,N=64,seed=7): independent_random ungated_unrel=0.549
  in (0.05,0.95); correlated_systematic ungated_unrel=0.210 in (0.05,0.95) -- lower than independent_random
  (expected: decoy-dominated unrel items degrade even the UNGATED baseline) but not vacuous/floored"
discriminator_survives_scale: "Option A -- smoke/self-test IS full-N/full-V (same regime, 1 seed, both
  modes); no separate scale-up regime exists (same convention as parent atom 29376 cell)"
cell_chunked: false
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false      # justified: total wall time (10 units) ~27s, well under 15-min threshold
progress_logging: "print_flush_true -- per-(seed,mode) [progress] lines with flush=True"
defensive_error_checking: "passed_all_4_patterns (start_marker + crash_diagnostic present; heartbeat
  exempted per above; not multi-seed-chunked, total wall time smoke-verified low)"
deterministic_seeding: true   # np.random.SeedSequence(fixed int seed).spawn(2) throughout; no hash()-derived seeding
calibration_check: "adaptive_with_discriminator_gate -- TAU formula IDENTICAL and unchanged from atom
  29376, applied unchanged across both error modes (not tuned per-mode toward a particular outcome)"
gate_d_positive_control: true  # independent_random arm MUST reproduce atom 29376 within tolerance 0.10;
  # measured deltas (see LANDED RESULT) are 0.0006 (auc) and 0.0066 (lift) -- reproduction essentially exact
one_variable_differs_verified: true  # self-test asserts rng_main child-spawn determinism across modes;
  # only rng_err's usage (fresh-random vs shared-decoy) differs between the two arms
```

## TIMEOUT / DISPATCH

Local timing (this machine, python 3.12-equivalent venv, numpy): self-test (1 seed x 2 modes) 5.2s; smoke
(same, written to `_smoke` dir) 5.1s; FULL (5 seeds x 2 modes = 10 units) 27.2s. Lightweight measurement by
compute-proportionality standards -- run FOREGROUND to completion, **no queue dispatch, no timeout
required**. Local-only per contract: no origin push, no remote-persist.

## GOVERNANCE

Pause-flag checked before this run: `data/orchestrator_paused.flag` absent (verified 2026-07-20,
immediately before the FULL dispatch). No origin push, no remote-persist, no queue_add invoked --
local-only per contract. Routes to Skunkworks for adversarial VET before any atomize/store-write. This
cell and its verdict are a direct answer to atom 29376's named scope bound; cite that atom's id/hash in
the follow-on VET.

## LANDED RESULT (FULL, 5 seeds x 2 modes = 10 units)

`verdict = HARD_FAIL_CORRELATED_ERROR_FOOLS_CHANNEL`
(MEASURED@data/exp_attention_salience_reliability_gate_correlated_error_v1/metrics.json)

**Gate D (positive control) HELD, reproduction essentially exact:**
- `auc_unrel_mean(independent_random) = 0.6770` vs prior atom 29376's `0.6764` (delta = 0.0006).
- `mean_delta_hard_unrel(independent_random) = 0.0568` vs prior atom 29376's `0.0634` (delta = 0.0066).
- Both well inside the 0.10 tolerance -- this reimplementation is faithful to atom 29376's mechanism; the
  correlated-mode result below is trustworthy, not an artifact of a broken reproduction.

**Correlated/systematic mode: the channel is FOOLED, decisively and consistently across all 5 seeds:**
- `auc_unrel_mean(correlated) = 0.3198` (per-seed 0.3240/0.3226/0.3121/0.3258/0.3144) -- COLLAPSED not
  merely below the 0.55 informativeness floor but **below chance (0.50) and even below the independent-mode
  floor's complement**, i.e. INVERTED: the derived score is anti-correlated with correctness under
  correlated errors.
- `mean_score_correct_unrel = 0.6688` vs `mean_score_incorrect_unrel = 0.7013` -- **wrong observations
  score HIGHER on average than correct ones.** This is the direct mechanistic signature of the adversary:
  confidently-wrong sources that share a per-item decoy reinforce each other's same-item peer-consistency,
  so the source-level aggregate rates them as MORE reliable than genuinely correct (but less
  mutually-reinforcing, since true observations are the OUTNUMBERED minority on unrel-tier items) sources.
- `mean_delta_hard_unrel(correlated) = -0.1018` (per-seed -0.0975/-0.0995/-0.1065/-0.0938/-0.1115, all 5/5
  NEGATIVE) -- the hard_gate arm actively HURTS, not merely ties; it preferentially up-weights the
  confidently-wrong sources it has been fooled into trusting.
- `do_no_harm_hard_ok = False`: `mean_delta_hard_rel = -0.2548` -- catastrophic on the rel-tier too (rel
  baseline itself already degraded to ~0.59 under correlated errors, since HI sources also err 35% of the
  time and their errors are correlated too; the gate compounds the damage).
- `control_ok_hard = False`: shuffled-control delta is `+0.016` to `+0.025` (small but POSITIVE) on every
  seed -- **de-structuring the (inverted) gate by shuffling it is slightly BETTER than applying it
  deterministically**, confirming the gate isn't merely noisy under correlated errors, it is
  systematically anti-correlated with correctness.
- `baseline_in_band = True` (correlated ungated_unrel per-seed 0.211-0.229 -- lower than the
  independent-random baseline's ~0.55-0.57, as expected: decoy-dominated unrel items degrade even the
  UNGATED consolidation, since majority-LO-sourced items are now dominated by a single wrong attractor
  rather than diffuse noise -- but not floored/vacuous). `baseline_rel_non_ceiling = True`.
- Cardinality 10/10 (5 seeds x 2 modes), arms-must-differ verified both modes at self-test/smoke,
  self-test/smoke/full all green on infra gates. Wall time: self-test 5.2s, smoke 5.1s, FULL (10 units)
  27.2s -- foreground, no queue needed.

**Interpretation (hypothesis-pending-VET, per standing discipline):** atom 29376's independent-channel
reliability CG is honestly and decisively BOUNDED to independent-random source errors. When errors are
CORRELATED/SYSTEMATIC (a shared "confidently-wrong" attractor per item, reused by every erring source
regardless of identity), the same-item peer-consistency raw ingredient the entire channel is built on is
not merely uninformative but INVERTED: it rewards mutual reinforcement among wrong sources exactly as
much as (here, more than) mutual reinforcement among correct sources, since the estimator has no way to
distinguish "these agree because they're both right" from "these agree because they share a bias." This
is precisely the failure mode predicted by the CG's own `brain_check` anchor (Kalman-gain / Ernst & Banks
optimal cue combination assumes INDEPENDENT sensor noise; when that assumption is violated, naive
reliability-weighted combination is not merely suboptimal but can be actively harmful -- overconfidence in
a shared bias). This is a real, informative scope limit, not a test-design artifact (Gate D reproduction
was essentially exact, and the failure signature is multi-signal-consistent: AUC collapse, negative
delta on both hard_gate and do-no-harm, and a shuffled control that BEATS the deterministic gate). Record
the bound: the independent-channel CG requires (or must be paired with a mechanism that detects and
discounts) independent, uncorrelated source errors to be safely deployed; a real-world reliability-gate
built on this mechanism would need an orthogonal correlated-error/common-mode detector before trusting
consistency-derived source reliability.
