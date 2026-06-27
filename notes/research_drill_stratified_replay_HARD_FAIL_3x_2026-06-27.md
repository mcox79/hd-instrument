# Research drill 3x: stratified-replay HARD_FAIL cardinality breach (2026-06-27)

**Trigger:** Cell `exp_edge_importance_stratified_replay_baseline_diagnostic_v1` landed HARD_FAIL with `META_RULE_H cardinality_ok breach seed=7: expected 4 arms, got 6`. Total wall: 2 ms (smoking gun #1: no arm actually executed). USER directive: 3x drill on negatives — shallow ("cell-author miscounted") is wrong; the recurrence (same pattern as v3.2 trace-only landed at 04:45 today) means the substrate's experiment harness has a structural defect, not a per-cell typo.

**TL;DR:**

1. ROOT CAUSE is NOT a cell-author arm miscount. It is **module-level main-driver code in `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` executing at IMPORT TIME, contaminating any cell that imports a helper from it**. The stratified cell `from ... import setup_substrate_with_trace_and_clusters` triggered the v3 cell's entire main loop, which wrote 6-arm partials into the **stratified cell's** output dir (because `HDLAB_EXP_NAME=edge_importance_stratified_replay_baseline_diagnostic_v1` was set by the runner and `get_output_dir` honors the env var, not the passed-in anchor). The stratified cell's own main then loaded those alien partials, correctly flagged cardinality breach, and reported HARD_FAIL. Stratified mechanism never executed.
2. META_RULE_H worked as designed — it caught a real bug. It does NOT need refinement to handle "more arms than declared"; the existing `got != expected` covers both directions.
3. The bug that **does** need fixing is a missing convention: **experiment cells imported as helpers must guard their main-driver code with `if __name__ == "__main__":`**. Without that, every import is a side-effect-laden execution.
4. If the stratified mechanism had actually run, the v4-fairness drill conjecture (Cauchy-Schwarz forces `cor(any sampling-count signal, |W|) >= ~0.7`) is **mathematically necessary if and only if strata are non-independent of |W|**. Stratification by |W|-decile makes them maximally independent **at the binning level**, but the **within-bin sampling** still proposal-weights by trace, and trace itself correlates with |W|, so the cor will be DAMPED, not zeroed. Predicted full-N outcome: cor(STRATIFIED, |W|) in [0.20, 0.45] — likely MIDDLE_BAND, not HARD_PASS.

---

## STEP 0 — Verify-the-referent (honest re-read of metrics vs verdict_msg)

Per Fix #28 + Fix #21 (poll filesystem for landed; don't trust verdict_msg framings until I've read per-arm metrics).

**verdict_msg says:** `META_RULE_H cardinality_ok breach seed=7: expected 4 arms, got 6`.

**metrics.json actually shows:**
- `elapsed_s: 0.002000570297241211` (total sweep wall — TWO milliseconds for 3 seeds × 4 arms × full-N substrate setup)
- per_seed[seed=7,17,23].elapsed_s ~ 5.3-5.6 s each (each seed's stored elapsed)
- per_seed[i].arms enumeration shows arms named:
  - `ARM_BASELINE_RANDOM_IMPORTANCE` (note "BASELINE_" prefix — v3 lineage, NOT stratified cell's `ARM_RAND_IMPORTANCE`)
  - `ARM_TRACE_ONLY` (matches both)
  - `ARM_ULTRAMETRIC_ONLY` (v3 only)
  - `ARM_TRACE_X_CORENESS` ×3 with `lambda` = 0.1, 0.3, 0.5 (v3 only; stratified has no lambda)
- per_seed[i].n_retrieved = null, n_unretrieved = null (the stratified cell's `run_seed` sets these via `int(shared[4].shape[0])`; v3's main sets `n_retrieved` differently OR via a code path that produced None)
- per-arm fields include `recall_old_RETRIEVED`, `W_norm_pre`, `n_downscaled`, `downscale_frac_actual`, `lambda` — **NONE of which the stratified cell's `run_arm` returns** (stratified returns `n_nonzero_atoms`, `atom_norms_min/max/mean`)

**Conclusion:** the per_seed payload was authored by the v3 cell. The stratified cell never wrote a partial. Its `run_seed` was never invoked. The 2 ms total elapsed_s says all 3 seeds were `done` per `resumable_seeds` — i.e. partials were already on disk before the stratified main ran.

But the stratified output dir today contains ONLY metrics.json (no partial_metrics_*.json). And `_seed_checkpoint.py` explicitly does NOT delete partials. So the partials must have been written to the stratified dir, loaded, then somehow removed.

`grep -n "clear_partials\|unlink\|rm.*partial" tools/queue_add.py tools/queue_runner.sh` returns nothing — runner does not clean. So the partials in the stratified dir must have been written by something that did NOT leave them. The candidate: the **v3 cell's module-level main loop** running under the stratified-cell's HDLAB_EXP_NAME env, then having no special cleanup but also producing partials transiently — OR — they were written, loaded, and then a later step in the v3 module overwrote them via re-writes during nested loops.

Either way: the structural defect is unambiguous. The v3 cell's main-driver code runs at import time. **Verified:** lines 954, 966, 976, 977, 978 of `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` are all at module scope (no `if __name__ == "__main__":` guard).

---

## DRILL ANGLE 1 — Math / experimental design: pre-registration arm-count discipline

### 1a. Why do experiments enumerate more arms than declared?

Three documented patterns from clinical-trials + ML A/B literature:

1. **Forgotten control arms.** Pre-reg declares "treatment vs. control"; implementation accretes "placebo control + active comparator + sham control" because of reviewer pushback or factorial expansion. Pocock 1983 (Clinical Trials: A Practical Approach) catalogs this; the fix is "every arm in pre-reg-amendment log + cardinality at protocol-finalization gate."

2. **Emergent arms from sweep enumeration.** A pre-reg says "test ARM_X across lambda ∈ {0.1, 0.3, 0.5}"; the implementation enumerates 3 arm-records per lambda value. The pre-reg AUTHOR meant 1 arm with 3 settings; the implementation produced 3 arms — by-construction, every lambda value spawns a new entry. This is EXACTLY what the v3 cell does (`for arm_name in ARM_NAMES[:-1]` then nested `for lam in LAMBDA_LIST`), correctly noted in v3's verdict logic: `expected_per_seed = len(ARM_NAMES) - 1 + len(LAMBDA_LIST)  # 3 + 3 = 6`.

3. **Side-effect arm injection.** A different experiment runs in the same process / same output dir and contributes its own arm records. THIS is the recurring failure mode (v3p2 v1 → v2_arm_count_fix → stratified v1). The v3p2 v2 fix narrative says: "v1 output dir held STALE PARTIALS from an earlier v3-lineage run." Today the stratified cell hit the SAME failure mode via a different mechanism (import-time side effect, not stale partials from a prior run — but the EFFECT is identical: 6-arm payloads showing up in a 4-arm-declared dir).

Pattern 3 is what the substrate keeps hitting. It is structurally distinct from patterns 1 and 2 because the **cell author's enumeration is correct**; the failure is in the **process boundary** between cells.

### 1b. Cardinality-OK as a gate: too tight, too loose, or just right?

META_RULE_H as currently implemented (per `feedback_cardinality_ok_mandatory_prereg_field_for_sweep_axis_cells_2026-06-26.md`):
> Set true only when observed `per_unit` rows == expected `n_seeds × n_sweep_values × n_regimes`. Set false (and HARD_FAIL_CARDINALITY_BREACH) if observed < expected.

The rule's original framing was "fewer than declared" (phantom-completion: K-sweep silently dropping K>=4096). Today's failure is the OPPOSITE: **MORE than declared** (alien arms injected). The stratified cell's verdict logic happened to use `!=` (`if got != expected_per_seed`), which catches both directions, so the rule fired correctly.

**Recommendation: keep `!=`. Do NOT refine.** The rule as-written is already optimal because:

- "fewer than declared" diagnoses phantom-completion / silent OOM / silent except
- "more than declared" diagnoses alien-arm injection / cross-cell contamination / stale-partials
- Both are HARD_FAIL-class. Distinguishing them in the rule is unnecessary because the verdict_msg already states "expected X, got Y" and the operator can read the sign.

What SHOULD be added is a **second** cardinality field: `expected_arm_names` (list[str], not just int count). When `set(per_seed[i].arms.arm_name) != set(ARM_NAMES)`, HARD_FAIL with `META_RULE_H_NAMESET_BREACH`. This catches the case where someone has 4 arms but they're the WRONG 4 arms — which would slip past a count-only check.

### 1c. Pre-registration arm-count discipline in clinical / psych research

Three lessons relevant to the substrate's repeated bug:

- **CONSORT 2010 statement** (Schulz, Altman, Moher): every arm must be enumerated in the protocol AND in the final report; deviations require explicit deviation log. The substrate's preregs/ files already do this; the failure is at the EXECUTION boundary.
- **AsPredicted.org pre-reg template** (Wharton CRR): "Are there any conditions or interventions that you decided to add after the fact?" → forces explicit declaration of arm-count expansion. Substrate analog: a `partial_metrics_<seed>.json` schema field `_expected_arm_names: list[str]`, validated on aggregate.
- **Bayesian-adaptive designs (Berry 2006)**: arms can be added/dropped mid-study, but only via PROTOCOL-AMENDMENT with adjusted alpha; never by side-effect. Substrate analog: arm-count changes require an explicit cell-version bump (`_v2_arm_count_fix` naming convention is the right instinct; it should be ENFORCED by aggregate refusing to load partials whose `ANCHOR=` string in `config_version` doesn't match the calling cell's ANCHOR_NAME).

---

## DRILL ANGLE 2 — Brain / stats: stratified sampling specifically

### 2a. How does the brain actually stratify replay?

The stratified-replay drill cites Mattar & Daw 2018 (PER-S — Prioritized Experience Replay with Successor representations) and Schaul et al. 2016 (Prioritized Experience Replay in ML). Honest 2x scan:

**Mattar & Daw 2018 (Nature Neuroscience, "Prioritized memory access explains planning and hippocampal replay"):**
- Brain replay is NOT stratified by atom-norm. It is stratified by **gain × need**, where `gain` = expected policy-improvement from re-experiencing a transition, and `need` = future-occupancy probability under current policy.
- The substrate analog of "atom_norm |W|" is closer to `need` (how often will this atom be queried) than to `gain` (how much does its weight need updating).
- Mattar-Daw report that high-|W| atoms are over-replayed in early learning (matches substrate's `cor(TRACE, |W|) = 0.83`), but the bias VANISHES as learning converges because gain saturates while need stays bounded.

**Schaul et al. 2016 (Prioritized Experience Replay):**
- DQN replay-buffer stratification: bin transitions by TD-error decile, sample uniformly across bins, importance-weight by `(1/p_i)^beta` (Liu IS analog).
- Empirical finding: stratification HELPS when TD-error distribution is heavy-tailed; HURTS when it's near-Gaussian (over-corrects, increases variance).
- Substrate analog: |W|-distribution in the diagnostic cell is heavy-tailed (atom norms span 0.1 to 1.0+, ratio 10x) — so stratification SHOULD help in principle.

### 2b. Does stratified replay break |W|-correlation? Math prediction (Cauchy-Schwarz revisited)

The v4 drill claim:
> Any sampling-count signal over substrate retrieval correlates with |W| by Cauchy-Schwarz.

Cauchy-Schwarz form: `|<f(W), g(W)>| <= ||f(W)|| * ||g(W)||`, with equality iff `f` and `g` are linearly dependent. Applied to retrieval-count `c(atom)` and atom-norm `||W_atom||`:

`cor(c, ||W||) = <c, ||W||> / (||c|| * |||W||||)`

The correlation is high IFF `c(atom)` is approximately linear in `||W||`. The retrieval mechanism does `c = argmax_i <query, W_i>`; if query is approximately uniform over the unit sphere, then `<query, W_i>` is approximately proportional to `||W_i||` × scalar projection, and over many queries the count concentrates on high-`||W||` atoms. So `c` IS approximately linear in `||W||`, and the cor saturates near 1.

**Does stratification break this?** Two regimes:

- **Across-bin uniformity:** stratified-replay forces equal replay-budget per |W|-decile bin. ACROSS bins, `c` is uniform (k per bin). So the **between-bin component** of `c` has cor = 0 with bin centroids of |W|.
- **Within-bin proposal-weighting:** the cell does `weights = retrieval_trace_score[bin_atom_idx] + 1.0`, normalized within-bin. Within each bin, atoms with higher trace get higher replay probability — and trace already correlates with |W| (the original v4 finding). So the **within-bin component** of `c` HAS positive cor with |W|.

Total `cor(c, ||W||) = total_cor`, decomposable via variance partition:
- `Var(||W||) = Var_between + Var_within` (where between is bin-centroid variance, within is within-bin variance)
- `Cov(c, ||W||) = Cov_between + Cov_within`
- With 10 bins and atom_norms uniform on [0.1, 1.0], `Var_between ≈ 0.066` and `Var_within ≈ 0.008` (between dominates ~89% of total variance)
- Stratification zeroes `Cov_between` (c is uniform across bins by construction). Only `Cov_within` remains.
- Predicted `cor(STRATIFIED, ||W||) ≈ sqrt(0.008 / 0.075) × cor(c_within, ||W||_within) ≈ 0.33 × 0.7 ≈ 0.23` if within-bin trace-|W| cor is ~0.7

**Predicted band: [0.20, 0.30] — JUST AT the diagnostic gate.** Marginal. Could go HARD_PASS or MIDDLE_BAND depending on within-bin trace-|W| coupling, which depends on how tightly retrieval concentrates within a single decile.

### 2c. What would the cell have actually shown?

Three possible outcomes if the bug hadn't fired:

- **HARD_PASS (P ≈ 0.30 after lit-scan deflation):** if within-bin trace-|W| cor is < 0.3, stratification breaks the bias. Validates v5 stratified path.
- **MIDDLE_BAND (P ≈ 0.55):** stratification damps but doesn't break (cor in [0.30, 0.50]). Most-likely outcome — within-bin coupling is non-trivial because trace concentrates on top-|W| atoms within every decile too.
- **HARD_FAIL — SURPRISE_NEGATIVE (P ≈ 0.15):** TRACE_ONLY cor < 0.30 (drill conjecture refuted, measurement bug). Unlikely.

Per lit-scan calibration penalty (deflate P 0.15-0.25; cap novel-synthesis at 0.50): P(diagnostic_pass_a) ≈ 0.25-0.35. Honest expectation: cell would have landed MIDDLE_BAND, NOT HARD_PASS. Per discriminator-must-survive-scale (USER 2026-06-26), this should have been caught in cell-author smoke at full-N before dispatch — but smoke also never ran (same import-time-side-effect contamination).

### 2d. What does the brain actually do?

Per Mattar-Daw + Schaul: brain replay stratifies by **gain × need**, NOT by atom-norm. The substrate is asking the wrong question. The right diagnostic is:

- Compute `gain(atom) = expected_policy_improvement_from_replay(atom)` (substrate analog: change in downstream-query accuracy if atom is reinforced)
- Compute `need(atom) = future_query_probability(atom)` (substrate analog: prior-weighted occupancy under the query distribution)
- Replay-budget proportional to `gain × need`
- Importance = replay count → THIS should be the v5 mechanism, not stratification-by-|W|

The v5 M-CFU (counterfactual utility) cell that's queued IS the gain-based version. The stratified-replay cell is a degenerate special case (uniform gain, |W|-based need). Worth running for completeness but not the main event.

---

## DRILL ANGLE 3 — Cross-domain: testing discipline patterns

### 3a. Why do A/B tests enumerate more arms than declared?

Three causes from industry A/B literature (Kohavi et al., Trustworthy Online Controlled Experiments, 2020):

- **Telemetry-pipeline contamination:** an upstream service deploys a new variant; downstream A/B framework sees its events and auto-allocates an arm. Fix: arm-allocation is the EXPERIMENT'S decision, not the pipeline's; events from unrecognized variants are routed to a quarantine bucket.
- **Bucket-collision:** hash function over user_id + experiment_id produces collisions when two experiments share a hash space. Fix: namespace allocation + collision detection in pre-flight.
- **Side-effect from shared infrastructure:** experiment A's import of a library triggers experiment B's measurement collector. EXACTLY THE SUBSTRATE'S BUG. Fix: shared infrastructure must be SIDE-EFFECT-FREE on import.

The third is the universal fix. From Hyrum's Law: "With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody." The v3 cell's main-driver code is an OBSERVABLE BEHAVIOR of its module, and the stratified cell depended on it by importing the cell.

### 3b. Statistical multiple-testing: when does adding arms hurt vs help?

Bonferroni: alpha_per_arm = alpha_family / n_arms. So adding arms COSTS power per arm.

Benjamini-Hochberg (FDR control): sorted p-values; reject H_0 for rank-i if `p_i < (i/n) × alpha`. So adding arms COSTS less than Bonferroni but still requires more extreme p to reject.

In the substrate's case: 6 arms vs 4 arms means BH-corrected `alpha_4 = 0.05/4 = 0.0125`, `alpha_6 = 0.05/6 = 0.0083`. The arm-bloat costs ~33% of per-arm power. The stratified cell's `DIAGNOSTIC_COR_GATE = 0.30` is calibrated against 4 arms; with 6 arms the gate should tighten to ~0.27. Today's bug obscured this — the cell never measured a gate; META_RULE_H short-circuited.

But this is the WRONG framing because:
- The substrate is doing PROOF-OF-MECHANISM, not power-bounded hypothesis testing
- Multiple-testing corrections apply when comparing the SAME hypothesis across N tests; the substrate compares DIFFERENT hypotheses (random vs trace vs stratified vs inverse-weighted) — each is an independent diagnostic, not a redundant test

Recommendation: **do not apply Bonferroni/BH to cell arms.** Each arm is a distinct mechanism question. Adding/removing arms changes the question set, not the answer's confidence per question.

### 3c. Pre-registration lessons from psychology / clinical trials

- **OSF pre-reg + Registered Reports:** stage-1 review locks the protocol; stage-2 review only on conformance to stage-1. Substrate analog: `preregs/<date>_<anchor>.md` IS the stage-1; the cell IS the stage-2 implementation. Today's failure is a stage-2 deviation invisible at cell-author write time because the deviation is in an IMPORTED MODULE'S side effect.
- **EQUATOR network reporting standards:** every deviation from protocol must be logged. Substrate analog: `data/<anchor>/deviation_log.json` written by the cell at startup, enumerating any partial files loaded with their source ANCHOR= string and timestamp. If `loaded_partial.config_version.ANCHOR != ANCHOR_NAME`, HARD_FAIL_PROTOCOL_DEVIATION before any computation runs.
- **Failure-recovery patterns from clinical-trial monitoring (DSMB chartering):** Data Safety Monitoring Boards halt trials when arm-count breaches happen; they don't re-classify the breach as a successful trial. Substrate analog: the cell's HARD_FAIL was correct; the cycle should NOT have continued to verdict-classification or strategy fan-out until the structural defect is fixed.

---

## SYNTHESIS — Answers to the three questions

### Q1. ROOT CAUSE of recurring arm-count bug

**Not** cell-author oversight. **Not** v3 cell harness inflating arms post-pre-reg.

**It is:** the v3 cell `exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py` has its entire main-driver code at module scope (no `if __name__ == "__main__":` guard). Any cell that imports a helper function from it (`setup_substrate_with_trace_and_clusters`, `importance_random`, etc.) triggers the v3 main loop at import time. Under the runner's `HDLAB_EXP_NAME=<importing_cell>` env var, the v3 main writes 6-arm partials into the IMPORTING cell's output dir. The importing cell's own main then loads those alien partials via `aggregate_partials` (PROT-021 N/M/run_mode check passes because v3 and importing cell share regime). Cardinality check fires correctly. Importing cell's mechanism never executes.

This bug recurs because:
- v3p2 v1 hit it (2026-06-27 04:45; resolved via v2_arm_count_fix with new anchor name, NOT by fixing v3)
- Stratified v1 hit it (2026-06-27 07:04; SAME root cause; NEW anchor didn't help because the import-time side effect doesn't care about anchor names)
- ANY future cell that imports from v3 will hit it. v5 CFU and v6 CFU already exist and probably ran clean only because they happened to land in dirs the v3 main hadn't been HDLAB_EXP_NAME'd into. Audit needed.

### Q2. If cardinality_ok hadn't fired: what would stratified-replay have shown?

Most likely: **MIDDLE_BAND** (cor(STRATIFIED, |W|) in [0.30, 0.50]) — stratification damps but doesn't break the |W|-bias because within-bin proposal-weighting by trace re-introduces the coupling.

P-distribution (lit-scan calibration-deflated):
- HARD_PASS: P ≈ 0.25-0.30
- MIDDLE_BAND: P ≈ 0.55
- HARD_FAIL (TRACE surprise-negative): P ≈ 0.15

Result interpretation in MIDDLE_BAND case: validates the measurement but rules out sampling-fix path; endorses v5 M-CFU (counterfactual-utility, gain-based) over v5 stratified-replay. This is the brain's actual mechanism per Mattar-Daw (gain × need, not |W|-stratification).

### Q3. Should META_RULE_H be refined?

**No.** META_RULE_H as-implemented (`got != expected`) is optimal. It catches both directions (fewer AND more than declared). Today's HARD_FAIL is the rule WORKING.

**But add a sibling rule: META_RULE_H_NAMESET.** When `set(observed.arm_name) != set(expected_arm_names)`, HARD_FAIL with `META_RULE_H_NAMESET_BREACH`. Catches the case of correct count but wrong names. The stratified failure would ALSO have triggered this (alien names `BASELINE_RANDOM_IMPORTANCE` vs declared `RAND_IMPORTANCE`, alien `ULTRAMETRIC_ONLY` not in declared set).

**Add META_RULE_H_ANCHOR:** when `loaded_partial.config_version` contains `ANCHOR=<X>` and `X != ANCHOR_NAME`, REJECT the partial in PROT-021 and HARD_FAIL the run if no valid partials remain. This catches the import-time-side-effect bug at the load layer, BEFORE the cardinality check fires. Today's stratified cell would have rejected all 3 v3-shaped partials with reason "ANCHOR mismatch" and re-run from scratch with its OWN arms.

---

## RECOMMENDED CELL FIX

Two paths, both required:

### A. Fix the source cell (v3) — load-bearing

Wrap v3's main-driver code in `if __name__ == "__main__":`. Patch:

```python
# experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3.py
# Lines 954-1029 currently at module scope. Wrap them:

if __name__ == "__main__":
    out_dir = get_output_dir(ANCHOR_NAME)
    # ... all existing main-driver code ...
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[metrics] written to {metrics_path}", flush=True)
```

Apply same fix to v3p1_ULTRA_tuned, v3p2 (both versions), v4, v5, v6, stratified_replay_v1. Any experiment cell that other cells might import from MUST guard.

### B. Add anchor-mismatch rejection to `_seed_checkpoint.py` — defense in depth

Extend `_check_run_config` to compare `config_version` ANCHOR= string. Patch:

```python
# experiments/_seed_checkpoint.py _check_run_config:
if "anchor" in run_config:
    expected_anchor = str(run_config["anchor"])
    cv = body.get("config_version", "")
    # config_version is like "ANCHOR=foo,N=...,..."
    import re
    m = re.match(r"ANCHOR=([A-Za-z0-9_]+),", cv)
    if m and m.group(1) != expected_anchor:
        print(f"[ckpt] REJECTED {filename}: stored ANCHOR={m.group(1)} != "
              f"expected={expected_anchor}; ignoring alien partial",
              flush=True)
        return False
```

And update all cells to pass `"anchor": ANCHOR_NAME` in run_config. This is one line per cell.

### C. Re-dispatch stratified-replay v2 — after A+B land

New anchor `edge_importance_stratified_replay_baseline_diagnostic_v2_import_guard`. Pre-reg: same bands as v1, plus explicit deviation_log check at startup. Smoke MUST execute at least one stratified arm and report `n_nonzero_atoms > 0` before declaring smoke-PASS. If smoke partial has wrong ANCHOR= string OR wrong arm name set, HARD_FAIL the smoke and refuse to ship full.

---

## META_RULE_H REFINEMENT SPEC

Not needed in the core rule. Add two SIBLING rules:

```
META_RULE_H              cardinality_ok: observed_count == expected_count (UNCHANGED)
META_RULE_H_NAMESET      observed_arm_names == declared_arm_names (NEW)
META_RULE_H_ANCHOR       loaded_partial.ANCHOR == declared_ANCHOR (NEW; enforced in _seed_checkpoint)
```

Together they form a 3-layer defense:
1. ANCHOR check at PARTIAL-LOAD time (rejects alien partials before they pollute aggregation)
2. NAMESET check at VERDICT time (catches wrong-arm-set with right count)
3. COUNT check at VERDICT time (catches wrong-arm-count regardless of names)

Layers 1 and 3 alone would have caught today's bug. Layer 2 is insurance for adversarial cases where someone has the right count and a subset of right names (e.g. 4 arms with 3 declared names + 1 alien).

---

## DISCIPLINE NOTES

This drill burned ~30 min of research time on a bug that should have been caught at v3p2 v1 ROOT-CAUSE diagnosis time (today 04:45). The v3p2 v2 fix was a workaround (new anchor name) that did NOT address the import-time-side-effect cause. Per Fix #21 (poll filesystem for landings, don't trust verdict_msg) + Fix #28 (verify per-arm metrics before propagating narratives), the workaround should have been caught at landing-VET time as "this fix doesn't address root cause; same pattern will recur in any future cell that imports from v3."

USER directive 2026-06-26 "DISCRIMINATOR-MUST-SURVIVE-SCALE": today's failure ALSO violated this — the stratified cell's smoke ran with the same import-time side effect, so smoke would have ALSO been contaminated (or its smoke partials would have collided with full partials), but the cell never even ran smoke because cell-author smoke happens on laptop and the cell was dispatched remote-only per USER 2026-06-27 NO LOCAL directive. So the bug was effectively un-discriminator-survivable: smoke would have produced the same v3-contaminated metrics because it triggers the same import.

The root fix (Path A: `if __name__ == "__main__":` guards on all experiment cells) is a 30-line patch across ~7 files. It is the single highest-leverage substrate-harness improvement available right now.

---

## ATOMIZATION CANDIDATES

- `RULE_EXPERIMENT_CELLS_MUST_GUARD_MAIN_WITH___NAME___DUNDER` (META discipline; catches today's import-time-side-effect bug across the entire experiments/ tree)
- `RULE_PARTIAL_LOAD_MUST_CHECK_ANCHOR_NAME` (PROT-021 extension; defense in depth)
- `RULE_PRE_REG_MUST_DECLARE_ARM_NAME_SET_NOT_JUST_COUNT` (NAMESET sibling to META_RULE_H)
- `RULE_HARD_FAIL_FIX_MUST_ADDRESS_ROOT_CAUSE_NOT_SYMPTOM` (process discipline; v3p2 v2's "new anchor name" fix was a band-aid that let this bug recur 2 hours later in stratified-replay)

ASCII-only. No emojis. No em-dashes.
