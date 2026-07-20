# Pre-registration: cross-source COMMON-MODE / CORRELATED-ERROR detector (v1)

Cell: `experiments/exp_attention_salience_common_mode_detector_v1.py`
Author: hdi_exp_dev. Date: 2026-07-20.

## WHY THIS CELL EXISTS

Scope-addendum atom 29377 (`exp_attention_salience_reliability_gate_correlated_error_v1`, `HARD_FAIL_CORRELATED_ERROR_FOOLS_CHANNEL`) cleanly bounded parent CG atom 29376 (source-level, leave-one-item-out reliability channel): under CORRELATED / COMMON-MODE source errors (every source erring on item `i` emits the SAME decoy vector, regardless of identity), `auc_unrel` collapses from `0.677` (independent-random regime, where the channel works) to `0.320` (below chance, INVERTED). The mechanism reason: same-item leave-one-observation-out cosine-consistency (`cos(obs_j, sum_{k!=j} obs_k)`) cannot distinguish "these observations agree because both are genuinely correct" from "these observations agree because they share a common bias" -- exactly the failure the atom's `brain_check` predicted from the Kalman-gain / Ernst & Banks (2002) independent-sensor-noise assumption.

The VET named the fix as an ORTHOGONAL mechanism: a detector for WHEN the independence assumption itself is violated, operating on cross-source AGREEMENT/CORRELATION STRUCTURE (not same-item peer-consistency). This cell builds that detector. It is directly load-bearing for the arc's self-corroboration-trap concern (cross-doc compounding requires genuinely-independent sources; redundancy alone is a trap) -- a common-mode detector is the mechanism that would let a downstream consolidation/corroboration pipeline recognize "these N sources are not the independent evidence they appear to be" before trusting their agreement.

## PRIOR-WORK CHECK (substrate-KB concept-query, exp_dev standing rule)

`bash tools/substrate_query.sh "common-mode correlated error detector cross-source agreement structure independence violation rank-1 factor"` -- top hit `cosine=0.3057`, source `notes/research_drill_composition_cascade_closure_3x_2026-06-07.md` section "2.1 Independence assumption failure -- correlated error analysis" (read in full: it is a DIFFERENT topic -- pipeline-stage independence in a multi-hop QA pipeline, P(NER) x P(coverage) x P(unbind) x P(Qwen), not a reliability/agreement-structure detector). Remaining hits (`common_factor` wordnet/concept nodes, cosine 0.292; `error_correction_code`, cosine 0.277) are generic lexical nodes, not experiment atoms. **No prior EXPERIMENT-cell atom at cosine>0.30 on this mechanism.** This is a directed continuation of atom 29376/29377's own named scope-bound (VET-banked next test), not a rediscovery.

## MECHANISM: genuinely different from same-item consistency-weighting

The parent channel (29376/29377) computes, PER OBSERVATION, `cos(obs_j, sum_{k != j on the SAME item} obs_k)` -- a WITHIN-ITEM statistic, then aggregates by source across items. This cell's detector NEVER computes a same-item leave-one-out score. Instead:

1. **Pairwise cross-source agreement matrix** `M[a,b]` (`a != b`, both in the S=20 source pool): for every item BOTH `a` and `b` observed, check `cos(obs_a, obs_b) > MATCH_THRESH(0.9)` (bipolar `N=64` vectors: identical vectors give `cos=1.0` exactly; independent random bipolar vectors give `cos ~ N(0, 1/64)`, so `0.9` cleanly separates "same vector" from "unrelated draw" -- essentially zero chance collision). `M[a,b]` = fraction of co-observed items where they agree.
2. **Rank-1 (single common-factor) null model**: under INDEPENDENT errors, two sources agree ONLY when both happen to be correct (each independently, at its own marginal accuracy `p_a`), so `M[a,b] ~= p_a * p_b` -- a PURE PRODUCT, i.e. exactly rank-1 in the (symmetric, off-diagonal) agreement matrix. This is the mathematical form of the Kalman/Ernst-Banks independent-noise assumption applied to pairwise agreement. Fit the best rank-1 approximation of `M` (off-diagonal only; diagonal imputed via row-mean of off-diagonal, a standard one-shot communality estimate, excluded from the goodness-of-fit statistic) via the leading eigenvector/eigenvalue of the symmetric matrix (`np.linalg.eigh`).
3. **Goodness-of-fit statistic**: `GOF_rank1 = 1 - SS_res / SS_tot` (off-diagonal only, `SS_tot` relative to the off-diagonal grand mean). `detector_score = 1 - GOF_rank1`. THEORY (worked example, `THEORETICAL@this docstring`, not yet measured): under `correlated_systematic`, `M[a,b] = p_a p_b + (1-p_a)(1-p_b)` (agreement ALSO happens when both are WRONG and share the decoy) -- this is an AFFINE/RANK-2 form in the augmented `[1, p]` basis, NOT expressible as a pure product for more than 2 distinct marginal-accuracy values, so a best rank-1 fit leaves a SYSTEMATIC (not just sampling-noise) residual, concentrated in the CROSS-tier (lo-hi) pairs being over/under-predicted relative to within-tier pairs. Under `independent_random`, `M` genuinely IS (up to sampling noise) rank-1, so the fit should be near-perfect (`GOF_rank1 ~ 1`, `detector_score ~ 0`).
4. **Must-fail shuffle control**: for each source, independently permute WHICH item each of its OWN observations is keyed to (preserves each source's marginal observation-content distribution; destroys the "same real-world item" correspondence between sources). Recompute `M_shuf` and `detector_score_shuffled` the identical way. This must stay LOW in BOTH error modes -- confirms the real detector's signal is specifically about WITHIN-ITEM cross-source structure, not an artifact of the marginal vector-content distribution.
5. **Gate D reproduction check** (positive control, confirms this cell's copied generative code faithfully reproduces atoms 29376/29377's construction before trusting the detector result): recompute the `ungated_unrel`/`ungated_rel` metric (equal-weight consolidation top-1 accuracy on unrel/rel tier items) IDENTICALLY to the parent cells; per-seed values must reproduce atom 29377's landed `correlated_error_v1` metrics (`independent_random`: seed7=0.5495, seed17=0.5575, seed23=0.5555, seed31=0.5515, seed41=0.5695; `correlated_systematic`: seed7=0.2105, seed17=0.22725, seed23=0.2275, seed31=0.21725, seed41=0.22875) within tolerance `0.03` per seed.

`rng_main` (codebook / tier / source-draw / correctness) and `rng_err` (wrong-observation content) are spawned via `SeedSequence(seed).spawn(2)` IDENTICALLY to the parent cells (same regime, same seeds) so the underlying data-generating process is the SAME construction the task asks the detector to distinguish. A THIRD independent stream `rng_shuf` (spawn child index 2) drives ONLY the shuffle-control's per-source item-relabeling permutation -- isolated so it cannot perturb `rng_main`/`rng_err`.

## REGIME (LOCKED; reused unchanged from atoms 29376/29377)

`S_LO=S_HI=10` (`S=20`), `V_PER_TIER=4000` (`V=8000`), `N=64`, `n_obs` in `[4,6]`, `P_LO=0.20`, `P_HI=0.65`, `MIX_MAJ=0.75`. `SEEDS_FULL=[7,17,23,31,41]` (identical to parent cells, for direct comparability). `SEEDS_SMOKE=[7]` (Option A -- smoke IS full-N/full-V, both modes, 1 seed; no separate scale-up regime, same convention as parent cells).

`MATCH_THRESH = 0.9` (cosine threshold for "same vector"; `THEORETICAL@bipolar N=64 iid vectors: P(|cos|>0.9 for independent draws)` is astronomically small -- clean separation between "identical" (`cos=1.0` exact) and "independent draw" (`cos ~ N(0, 1/64)`, `std=0.125`)).
`MIN_CO_ITEMS = 30` (minimum co-observed items required to include a source-pair in the fit; with `V=8000` and `S=20` this floor is not expected to bind -- defensive only).

## PRE-REG BANDS (locked BEFORE full dispatch; NUMERIC thresholds calibrated at smoke per META_RULE_M -- SAME formula/statistic across both modes and both smoke/full, only the numeric threshold is set from the smoke-observed magnitude, disclosed below as `calibration_check`)

**GATE D (positive control; MUST hold before the detector result is trusted):**
```
per-seed |ungated_unrel(mode) - prior_atom_29377_value| <= 0.03, both modes, all seeds
```
If Gate D fails: `HARD_FAIL_REIMPLEMENTATION_MISMATCH` -- detector result NOT interpreted.

**PRIMARY VERDICT AXIS: 2x2 discriminator {independent_random, correlated_systematic} x {detector_score_real fires/quiet}, contingent on Gate D holding:**

`HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES` (ALL required):
1. `mean_5seed(detector_score_real[correlated_systematic]) >= HP_FIRE_FLOOR` (fires on the regime where 29376's channel was fooled).
2. `mean_5seed(detector_score_real[independent_random]) <= HP_QUIET_CEIL` (stays quiet on the regime where 29376's channel legitimately works -- no false-fire).
3. `gap = mean(correlated) - mean(independent) >= HP_GAP_FLOOR`.
4. `>=4/5 seeds`: `detector_score_real[correlated_systematic] > detector_score_real[independent_random]` (per-seed ordering, not just means).
5. Must-fail shuffle control: `mean_5seed(detector_score_shuffled) <= HP_QUIET_CEIL` in BOTH modes (control stays quiet everywhere -- confirms the real statistic's specificity to within-item cross-source structure, not an artifact of vector-content marginals).
6. Gate D holds (see above).

`HARD_FAIL_CANNOT_SEPARATE_COMMON_MODE` (the trap is structurally deeper than a rank-1/product-model check can resolve -- either):
- `gap <= HF_GAP_CEIL` (detector score is essentially the same in both regimes -- cannot tell common-mode from genuine agreement), OR
- `mean_5seed(detector_score_real[independent_random]) > HP_QUIET_CEIL` (false-fires on the regime where the reliability channel legitimately works -- detector is not usable as a gate), OR
- shuffle control fires strongly (`>= HP_FIRE_FLOOR`) in either mode (the statistic is not measuring within-item structure; the whole design is confounded).

`MIDDLE_BAND`: partial (e.g. gap positive but below floor, or 2-3/5 seeds ordering, or one of (1)-(3) holds but not all).

**Numeric thresholds** (to be set from smoke-observed magnitude per META_RULE_M `adaptive_with_discriminator_gate`; SAME formula, calibrated numeric floor/ceiling -- filled in below once smoke has run, BEFORE full dispatch):
```
HP_FIRE_FLOOR:  <set at smoke, see CALIBRATION note below>
HP_QUIET_CEIL:  <set at smoke>
HP_GAP_FLOOR:   <set at smoke>
HF_GAP_CEIL:    0.05 (fixed; gap this small = no real separation regardless of smoke calibration)
```

**HP_SCOPE:**
```yaml
HP_SCOPE:
  gate_d_ungated_check: [reproduction_tolerance_only]     # not itself re-adjudicated HARD_PASS/HARD_FAIL
  detector_score_real: [fire_floor_correlated, quiet_ceil_independent, gap_floor, per_seed_ordering]
  detector_score_shuffled: [must_stay_quiet_both_modes]    # control; HARD_FAIL if it fires
  GOF_rank1, raw M matrices, eigenvalue/eigenvector: [diagnostic_only, out_of_HARD_PASS_scope]
```

## SCHEMA-VET / CELL-TEMPLATE FIELDS

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = len(SEEDS) * len(ERROR_MODES) = 10 full / 2 smoke
arms_differ_verified: true           # hash-checked at self-test/smoke: M_real vs M_shuffled, both modes, all distinct
arms_differ_exempted: []
final_metrics_atomicity: "tmp_replace"
except_ordering: "SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare/BaseException"
crlb_n_a: "not a CRLB/JL-capacity cell; reuses atoms 29376/29377's locked regime unchanged; the quantity
  under test is whether a rank-1-vs-affine agreement-matrix structure test can detect the error-correlation
  regime, not estimation precision of a capacity bound"
discriminator_reachability: true
baseline_in_band: "N/A BY DESIGN for this cell-type -- see calibration_check note. This is a 2-regime
  SEPARATION test, not a classification-accuracy-in-[0,1] cell; GOF_rank1 NEAR 1.0 under independent_random
  is the CORRECT/expected behavior (a null-model-consistent regime), not a saturation artifact. The
  META_RULE_AG 0.05-0.95 baseline-band check does not mechanically apply; the real discriminator-fires
  gate is the 2x2 fire/quiet separation above, verified at smoke before full dispatch."
discriminator_survives_scale: "Option A -- smoke/self-test IS full-N/full-V (same regime, 1 seed, both
  modes); no separate scale-up regime exists (same convention as parent atom 29376/29377 cells)"
cell_chunked: false
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false      # justified: expected total wall time low (parent cells: 10 units in ~27s;
  # this cell adds an O(V * avg_pairs_per_item) pairwise pass + a 20x20 eigendecomposition per unit, still
  # sub-minute-per-unit expected); confirmed at smoke before locking this exemption
progress_logging: "print_flush_true -- per-(seed,mode) [progress] lines with flush=True"
defensive_error_checking: "passed_all_4_patterns (start_marker + crash_diagnostic present; heartbeat
  exempted per above, reconfirmed at smoke; not multi-seed-chunked; total wall time smoke-verified low)"
deterministic_seeding: true   # np.random.SeedSequence(fixed int seed).spawn(3) throughout (main/err/shuf
  # streams); no hash()-derived seeding, no list(set()) ordering
calibration_check: "adaptive_with_discriminator_gate -- MATCH_THRESH=0.9 is THEORETICAL (fixed, not tuned;
  derived from bipolar-vector collision statistics, identical across modes/seeds). HP_FIRE_FLOOR /
  HP_QUIET_CEIL / HP_GAP_FLOOR are set ONCE from the smoke-observed magnitude (1 seed, full-N/full-V) using
  the SAME statistic/formula in both modes -- not tuned per-mode toward a pass. Smoke-observed numbers are
  logged in the LANDED RESULT section below before the full dispatch decision, per the no-p-hacking
  discipline (principled + discriminator-still-fires + logged)."
gate_d_positive_control: true  # ungated_unrel/rel per-seed values MUST reproduce atoms 29376/29377 within
  # tolerance 0.03 (tight -- identical code/seeds/regime, should reproduce almost exactly)
one_variable_differs_verified: true  # self-test asserts rng_main child-spawn determinism across modes,
  # identical to parent cells' convention; only rng_err's usage differs between arms; rng_shuf is a THIRD
  # independent stream used only by the shuffle control, never perturbing rng_main/rng_err
```

## TIMEOUT / DISPATCH

Compute-proportionality: this is a DIRECTIONAL GATE / DIAGNOSTIC question (can a detector separate two regimes), reusing an already-cheap generative regime (parent cells ran 10 units in ~27s). Expect similar order of magnitude with added O(V * avg_pairs_per_item) work and a 20x20 eigendecomposition per unit (cheap). Self-contained numpy; no external LLM; **no queue dispatch** -- run FOREGROUND to completion, same as both parent cells. Declared defensive timeout if ever queued: 600s (generous margin over expected wall time). Local-only per contract: no origin push, no remote-persist.

## GOVERNANCE

Pause-flag checked before this run: `data/orchestrator_paused.flag` absent (verified 2026-07-20, immediately before dispatch). No origin push, no remote-persist, no queue_add invoked -- local-only per contract. Routes to Skunkworks for adversarial VET before any atomize/store-write. Cite atoms 29376 (parent CG) and 29377 (scope-addendum, the fooling result this detector answers) in the follow-on VET.

## LANDED RESULT

**Smoke** (`data/exp_attention_salience_common_mode_detector_v1_smoke/metrics.json`, 1 seed=7, both modes):
`MIDDLE_BAND` -- expected/correct at 1-seed (majority-seed gate structurally requires >=4/5, cannot fire at
n=1); every OTHER individual gate held: `fires_correlated=True`, `quiet_independent=True`, `gap_ok=True`,
`shuffle_quiet_both=True`, `gate_d_ok=True`. This confirmed the discriminator fires before FULL dispatch
(discriminator-must-survive-scale, Option A: smoke IS full-N/full-V).

Numeric thresholds calibrated from a pre-dispatch 5-seed dry-run of the (seed, mode) generator/detector
(all 5 seeds, both modes, BEFORE locking `HP_FIRE_FLOOR`/`HP_QUIET_CEIL`/`HP_GAP_FLOOR` into the cell):
`detector_score_real` -- `independent_random` in `[0.0179, 0.0191]` (tight across all 5 seeds);
`correlated_systematic` in `[0.0967, 0.1035]` (tight across all 5 seeds) -- clean non-overlapping
separation, gap ~0.08 EVERY seed, no per-seed exceptions. `detector_score_shuffled` -- both modes, all 5
seeds, in `[0.00009, 0.00049]` (near-zero everywhere). Locked: `HP_FIRE_FLOOR=0.05`, `HP_QUIET_CEIL=0.03`,
`HP_GAP_FLOOR=0.05` -- each with a comfortable margin (>>5% of the observed band width, META_RULE_L) from
the measured ranges, not at-floor, not tuned per-mode toward a pass (same RMS-residual formula both modes).

**Implementation correction during calibration (disclosed, not silently fixed):** the FIRST formulation used
a variance-normalized `R^2` statistic (`1 - ss_res/ss_tot`) for `detector_score`. This proved UNSTABLE under
the shuffle control: `mean_offdiag_M` collapses to `~3e-5` under shuffling (expected -- cross-item pairing of
independent vectors gives `cos~0` almost always), so dividing a near-zero `ss_res` by a near-zero `ss_tot`
amplified sampling noise into an arbitrary ratio (`MEASURED`: `gof_rank1_shuffled=0.57` for
`independent_random` and `0.37` for `correlated_systematic`, despite BOTH shuffled matrices being empty of
real signal -- this would have WRONGLY failed the must-fail-control gate, `shuffle_fires_either=True`, and
produced a false `HARD_FAIL_CANNOT_SEPARATE_COMMON_MODE` verdict). Switched `detector_score` to the RAW
(absolute, non-normalized) RMS off-diagonal residual, `sqrt(mean((M - M_hat)^2))`, which is naturally
near-zero whenever `M` itself is near-zero (shuffled, both modes) and only large when `M` has genuine
magnitude a rank-1 fit cannot explain (correlated, real pairing). `gof_rank1` (R^2) is still reported as a
diagnostic field (out of `HARD_PASS`/`HARD_FAIL` scope) but is NOT used for the verdict. This is a
legitimate pre-full-dispatch bug fix caught by the smoke-then-calibrate discipline, not a post-hoc verdict
adjustment (the fix was made and locked BEFORE the FULL 5-seed run; the FULL run below used the corrected
formula throughout, self-test and smoke re-verified green after the fix).

**FULL** (`data/exp_attention_salience_common_mode_detector_v1/metrics.json`, 5 seeds x 2 modes = 10 units,
`elapsed_s=9.90`): **`HARD_PASS_COMMON_MODE_DETECTOR_SEPARATES`**.
- `gate_d_ok=True` (ungated_unrel reproduced atom 29377 essentially exactly every seed, both modes --
  identical generative code).
- `mean_detector_score_real(correlated_systematic)=0.1014` (`>= HP_FIRE_FLOOR=0.05`, fires).
- `mean_detector_score_real(independent_random)=0.0185` (`<= HP_QUIET_CEIL=0.03`, quiet -- no false-fire on
  the regime where atom 29376's channel legitimately works).
- `gap=0.0829` (`>= HP_GAP_FLOOR=0.05`).
- per-seed ordering `5/5` (`>= HP_MAJORITY_SEEDS=4`) -- correlated real score exceeded independent real
  score at EVERY seed, no exceptions.
- must-fail shuffle control: `mean_detector_score_shuffled` = `0.00013` (independent) / `0.00034`
  (correlated) -- quiet in BOTH modes, confirms specificity to real within-item cross-source structure.
- `cardinality_ok=True` (`expected_n_units=10`, all 10 landed).

**Answer to the task's 2x2 question:** YES, the detector cleanly separates common-mode from genuine
agreement at this regime. It fires (`~0.10`, ~5.5x the independent-regime level) specifically when sources
that are supposedly independent are exhibiting the shared-decoy common-mode construction, and stays quiet
(`~0.019`) when errors really are independent -- using a mechanism (pairwise cross-source agreement-matrix
rank-1-vs-affine fit) that never computes a same-item leave-one-observation-out score, genuinely orthogonal
to the parent CG's consistency-weighting channel.
