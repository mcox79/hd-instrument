# Prereg: stretch4_1_bayes_net_learning_cpu_v1

## Anchor
`stretch4_1_bayes_net_learning_cpu_v1`

## Cell path
`d:/AI/hd-instrument/experiments/exp_stretch4_1_bayes_net_learning_cpu_v1.py`

## Metrics path
`d:/AI/hd-instrument/data/exp_stretch4_1_bayes_net_learning_cpu_v1/metrics.json`

## Queue routing
- **Smoke:** local (direct invocation via `.venv/Scripts/python.exe ... --smoke`); ran 2026-07-02 in 1.2s wall. Not via queue_add (smoke is direct-verification).
- **Full:** `remote_cpu_queue` (per USER 2026-07-01 SMOKE-ONLY local rule; FULL routes remote).

## Framing (Stage 3 compositional-understanding arc, USER 2026-06-26 pivot)

Substrate's chain-grade primitives cover point retrieval + confidence, but NOT joint probability distributions across multiple facts (per prior atom `substrate_multihop_value_add_and_cannot_do_v278` chunk 9.3: "substrate does NOT model joint probability distributions... Workaround: Complement substrate with explicit Bayesian-network primitives"). This cell probes the WORKAROUND path: can standard partial-correlation + MLE recover Bayes-net structure + parameters at Stage-3 scale, providing a REFERENCE baseline that future substrate-native probabilistic primitives can be evaluated against?

**Honest scope:** this cell is a NUMPY-BASELINE reference, NOT a substrate-primitive demonstration. Cell imports `cphasor`/`cidx` but never calls them; structure learning is `np.linalg.pinv` + partial-corr; CPT learning is masked-mean MLE. The verdict message text ("substrate LEARNS a Bayes net") is IMPRECISE — it should read "numpy-baseline learns a Bayes net; substrate-native probabilistic primitive deferred." Flagged for Director judgment; not blocking dispatch since a numpy-baseline reference is still substrate-portfolio-relevant as calibration for future substrate-native attempts.

## Hypothesis

At NV=5 variables, NSAMP=3000 samples, PROBS=90 problems (each with random parent-selection + random CPT):

- Partial-correlation skeleton learning with threshold=0.07 recovers Bayes-net edges with structure-precision >= 0.70.
- MLE from counts (masked-mean over samples matching parent-configuration) recovers CPT entries with |estimate - true_p| <= 0.10 mean absolute error.

## Bands (envelope-fail)

| Band | Structure-precision | CPT-err | Notes |
|---|---|---|---|
| HARD_PASS | `>= 0.70` (strict; band-floor is 0.70) | `<= 0.10` | Both conditions required |
| MIDDLE_BAND | `>= 0.55` (< 0.70 OR CPT-err > 0.10) | any | Partial |
| HARD_FAIL | `< 0.55` | any | Structure recovery below random-guess-plus-margin |

**Band strictness (META_RULE_L):** HARD_PASS band [0.70, 1.0]; width 0.30; strict floor = 0.70 + 0.05*0.30 = 0.715. Smoke result 0.951 is well strictly-above-floor (+0.236).

**Baseline analytical (META_RULE_AG):** at NV=5, expected true-edges per problem is ~5-8 of 10 pairs (depends on parent-selection). Random-guess partial-corr with threshold=0.07 on standard-normal correlations would achieve precision ~0.5-0.8 (edge base-rate). Observed 0.951 is analytically distinguishable from random.

## Discriminator-must-survive-scale (META_RULE_AG + scale rule)

**Analytical justification (path B):** Full grid is PROBS=90 vs smoke PROBS=25. Metrics `struct_precision`, `struct_recall`, `cpt_err` are aggregated tp/fp/fn ratios across problems and mean over CPT-entries — SAMPLE-SIZE increases (3.6x more problems) but the discriminator regime is IDENTICAL (same NV=5, NSAMP=3000 per problem, same partial-corr threshold=0.07). No qualitatively new regime at full-N; smoke IS the mechanism at scale with less statistical power.

Smoke result at PROBS=25: precision=0.951 (well above 0.715 strict-HP floor); expected full at PROBS=90: same expected value, tighter variance. Reject-dispatch criterion (baseline >= 0.95 of mechanism) is not applicable — cell has no separate mechanism vs baseline arm; the mechanism IS the readout and its discriminator is threshold-vs-random-precision.

## Compute architecture

**Class:** (b) sequential-CPU with justification.

**Justification:** Cell workload per PROBS iteration is `np.corrcoef(NSAMP=3000, NV=5)` + `np.linalg.pinv(5x5)` + MLE mask counts — trivially cheap (<50ms per problem). Total wall smoke=1.2s, expected full ~4-5s. No matmul-heavy substrate primitives (cphasor/cidx imported but unused; see Framing). GPU batching would provide NO speedup at this scale. Sequential PROBS loop over 90 independent problems on numpy CPU is optimal.

## META_RULE compliance

- **cardinality_ok**: N/A — no sweep axis; single-mode measurement over PROBS aggregates.
- **arms_differ_verified**: N/A — cell has ONE arm (structure+CPT joint readout); no arm-comparison logic.
- **final_metrics_atomicity**: relies on `experiments._seed_checkpoint.write_metrics` (tmp_replace pattern per §7).
- **except SystemExit: raise BEFORE except Exception**: cell has minimal try/except (only sys.stdout.reconfigure); no outer BaseException; SystemExit safe.
- **crlb_floor_computed**: N/A for this class — no argmax-noise floor; discriminator is statistical (partial-corr threshold). `crlb_n/a: "structure-learning-not-argmax-cleanup; discriminator is partial-corr-threshold vs random-baseline-precision"`.
- **baseline_in_band**: N/A — no separate baseline arm; analytical baseline (0.5-0.8) is on-file above.
- **HP_SCOPE**: single arm; HP gates apply to that arm.
- **calibration_check**: `default_ok_for_this_regime` — partial-corr threshold=0.07 hardcoded; NSAMP=3000 gives sufficient signal; smoke verified.
- **cell_chunked**: false — single-run cell, PROBS is inner iteration not seed axis.
- **start_marker_written**: false — cell is <5s wall; below §13 mandatory threshold for start-marker.
- **crash_diagnostic_present**: false — trivial cell (~50 lines exec); crash would appear in runner log directly.
- **heartbeat_present**: false — <60s wall; below threshold.
- **defensive_error_checking**: `"exempted_short_cell_under_5s_wall_no_multiseed"`.
- **run_mode**: cell defaults RUN_MODE to "full" when `--smoke` absent; `HDLAB_RUN_MODE` env var override respected. Runner will invoke without `--smoke` for FULL → RUN_MODE=full landed correctly. Verified by prior smoke run showing `run_mode="smoke"` when flag passed.
- **progress_logging**: `runner_python_u_only` — cell uses `print(..., flush=True)` on all diagnostic lines and total wall <10s, so §17 30-min-timeout progress rule N/A.

## Test-design gates (§15)

- **A) sweep_alignment_verdict**: N/A (no swept parameters).
- **B) discriminating_fraction**: N/A (no sweep). Analytical smoke-and-full both in discriminating band by construction (precision expected 0.7-1.0).
- **C) composition_edges**: N/A (no primitive composition; cell is standalone numpy).
- **D) positive_control_arms**: N/A — cell doesn't compose prior chain-grade primitives. Cell IS the reference-baseline for future substrate-native probabilistic primitives.
- **E) functional_requirements**: (1) skeleton recovery from data → `np.linalg.pinv`-based partial-correlation; (2) CPT MLE → masked-mean over samples matching parent-config. Both are standard-statistics primitives, not substrate primitives.

## Stage progression

**Stage 3** (compositional understanding — probabilistic reasoning over structured graphs). NOT Stage 4 (no language / no BPC / no vocab). Confirmed in-scope for USER 2026-06-26 pivot arc.

## Substrate-doesn't-know-anything check

No language testing; no ingested text corpus; synthetic Bayes-net problems with parent-child structure generated at runtime. Confirmed compatible with USER 2026-06-26 rule.

## Timeout

`--timeout 300s` (5 min) — 60x safety margin over expected 5s wall. Sufficient headroom for any transient CPU contention on remote host.

## Smoke evidence

- Timestamp: 2026-07-02 (fresh)
- Command: `.venv/Scripts/python.exe experiments/exp_stretch4_1_bayes_net_learning_cpu_v1.py --smoke`
- Wall: 1.2s
- Result: `struct_precision=0.951 struct_recall=0.777 cpt_err=0.015` → HARD_PASS
- Discriminator margin: +0.236 above strict-HP floor (0.715)
- Fired: yes (not saturated at 1.0; not at floor; substantively above random-baseline)

## Post-dispatch RUN_MODE_VERIFICATION (§16)

After FULL landing at `data/exp_stretch4_1_bayes_net_learning_cpu_v1/metrics.json`, verify:
- `run_mode == "full"`
- `elapsed_s` in range [2, 30] (expected ~4-5s; hard-flag if <1s = selftest-landed, or >60s = anomaly)
- `per_seed[0]` has `struct_precision`, `struct_recall`, `cpt_err` keys with numeric values
- File size > 500B (expect ~800B based on prior run)

## Framing caveat for atomization (Skunkworks/Director)

**If HP lands FULL:** the atom claim should be "NUMPY-BASELINE Bayes-net structure + CPT learning at NV=5/NSAMP=3000/PROBS=90 achieves structure-precision X and CPT-err Y" — NOT "substrate learns a Bayes net." Verdict message text should be corrected pre-atomization or the atom scope must caveat that the mechanism is numpy-statistical, not substrate-primitive. Substrate-native probabilistic primitive remains an OPEN capability gap per `substrate_multihop_value_add_and_cannot_do_v278` chunk 9.3.
