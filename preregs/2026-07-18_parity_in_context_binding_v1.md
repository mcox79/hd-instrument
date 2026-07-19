# Prereg: parity_in_context_binding_v1

**Date:** 2026-07-18
**Author:** exp_dev (Opus)
**Cell:** `experiments/exp_parity_in_context_binding_v1.py`
**Design source:** `notes/research_learning_mechanism_correlation_bound_structural_verdict_2026-07-18.md` (D3 drill, "Cheap decisive test")
**Question class:** DIAGNOSTIC / directional gate (compute-proportional: closed-form/Hebbian, no SGD, no GPU, < 1 min CPU). Resolves the confound behind the "correlation ties everything" learning negatives: task-triviality vs mechanism-poverty.

## Prior-work check
`substrate_query "parity in context correlation bounded predictive coding structure learning"` -> top cosine 0.327 (correlated-Hopfield-capacity lit note), 0.320 (predictive-coding/backprop lit note), 0.316 (predictive-coding drill). All are LITERATURE notes, none an experiment cell implementing parity-in-context. Existing `experiments/*parity*` files are all numeric dtype-parity (fp16/fp32) checks, unrelated to logical XOR parity. **Genuinely novel instrument; not a rediscovery.**

## Task
Delayed k=2 parity (XOR) embedded in an HD role-filler token stream. Window of W positions; each holds a bit; two informative offsets m1,m2 (neither is the most-recent position W-1); label y = bit[m1] XOR bit[m2]; other positions are distractor bits. Learner sees the full HD-encoded window, predicts y on a held-out test set.

## Arms (shared substrate front-end: bipolar role-filler encode + unbind/cleanup sign recovery; arms differ ONLY in readout/combination)
- **ARM_CORR** first-order marginal correlation counter over per-position signs. The additive/linear readout class (cf. `hdlab/additive_map.py` `score = -||X_h+D_r-X_t||`, a linear function of coordinates). Control that MUST stay at chance.
- **ARM_BIND_ORACLE** conjunction of the two KNOWN informative positions (capacity ceiling: proves HD channel carries the parity signal).
- **ARM_BIND_HEBB** all pairwise conjunctions + UNWEIGHTED parallel Hebbian readout (no error gating). Maps to negative #3 (dilution by unweighted context).
- **ARM_PREDCODE** same conjunctions + predictive-ERROR relevance gate (residual-driven competitive selection). ONE variable vs BIND_HEBB: target is the prediction ERROR (residual), not the raw label.

## DESIGN-GATE (pre-registered, verified at smoke BEFORE full)
1. **REAL baseline, provably chance:** ARM_CORR is a genuine marginal correlation counter; k=2 parity has exactly zero single-position marginal correlation (Minsky-Papert XOR non-separability). Proven analytically in `--self-test` (max |marginal corr| < 0.08; optimal least-squares linear < 0.55) AND verified empirically (MEASURED ARM_CORR mean 0.499-0.501). Must-fail control FIRES.
2. **CAN-FAIL BOTH WAYS:** R_large is a dilution regime where an un-gated structure arm (BIND_HEBB) is predicted to DEGRADE toward chance. MEASURED BIND_HEBB R_large = 0.642 (in discriminating band [0.30,0.70]) -> the discriminator demonstrably moves in the FAIL direction; not construction-locked to PASS. If the HD channel could not carry parity (low N / high W), ORACLE would also fail -> HARD_FAIL branch is reachable.
3. **DIFFICULTY-ON:** genuine k=2 parity; marginals uninformative (proven); not linearly separable (proven). n_train small in R_large to stress dilution.
4. **ONE VARIABLE across the discriminating pair:** BIND_HEBB vs PREDCODE differ ONLY in the combination target (raw label vs prediction error) over identical conjunction features / encoder / window.

## Envelope-fail-bands (verdict logic)
- **VOID_TASK_LEAKS** if ARM_CORR mean > 0.55 (not genuine parity).
- **VOID_RECOVERY_CONFOUND** if front-end recovery accuracy < 0.95 (confounds recovery with combination).
- **HARD_FAIL_MECHANISM_POVERTY** if ALL structure arms (incl ORACLE) < 0.65 while CORR at chance -> substrate cannot carry/solve parity at this construction (real bound; brain-check applies).
- **HARD_PASS_STRUCTURE_DISCRIMINATES** if any structure arm >= 0.65 while CORR pinned at chance -> the missing structure (conjunction/binding) is REAL and this task discriminates it.
- **Predictive-loop localization** per regime: `binding_alone_suffices` (both HEBB,PRED pass) | `predictive_error_element_required` (HEBB fails, PRED passes) | `predcode_underperforms_hebb` | `search_poverty` (both fail, oracle carries).

## Compute architecture
Class: **(b) sequential-CPU with justification** — closed-form correlations + matching-pursuit, no SGD, no GPU need; full run 0.3s wall over 10 units. Storage strategy: `no_storage` (no PartitionedStore; in-memory role codebook per unit). Ran inline foreground to completion per compute-proportionality (light diagnostic; heavy-local-fit prohibition does not apply — no training fit, sub-second).

## Meta-rule fields
- `cardinality_ok: true` — EXPECTED_N_UNITS = n_seeds(5) x n_regimes(2) = 10; verdict counts per-unit; HARD_FAIL_CARDINALITY_BREACH if short. MEASURED 10/10.
- `arms_differ_verified: true` (META_RULE_AF) — prediction-digest collisions among the 3 structure arms EXEMPTED only when both arms >= 0.99 acc (convergence to ground truth, not shared code); ARM_CORR never exempt; positive distinctness asserted (CORR differs from all; HEBB vs PREDCODE differ in R_large). Declared code-level exemption: (ORACLE,PREDCODE) converge whenever PREDCODE's search succeeds.
- `final_metrics_atomicity: tmp_replace` (os.replace).
- `crash_diagnostic_present: true`; `start_marker_written: true`; `except SystemExit: raise` before `except Exception` (no BaseException/bare except — grep-gated clean).
- `crlb_n/a`: parity is a discrete logical target, chance=0.5 exact, no CRLB noise floor; bands are binomial-significance based (n_test=2000 -> per-seed binomial std ~0.011, 5 seeds).
- `calibration_check: default_ok_for_this_regime` (analytic chance=0.5 exact).
- `baseline_in_band` (META_RULE_AG): the saturation-risk baseline is ORACLE (capacity ceiling, expected ~1.0 by design, not a discriminator); the DISCRIMINATING arm BIND_HEBB lands at 0.642 in R_large (in band). ARM_CORR is a must-fail-at-chance control, not an in-band baseline.
- `discriminator survives scale`: smoke ran at FULL N (N=4096 identical smoke vs full); only n_seeds reduced (3 vs 5). Discriminator (BIND_HEBB dilution) fired identically at smoke (0.636) and full (0.642).

## Brain-check (NOT pre-assuming outcome)
Does the brain solve parity-like nonlinear-in-context binding via a predictive/error mechanism?
- **Representation of XOR/conjunction: brain uses nonlinear DENDRITIC integration** (sigma-pi / coincidence detection); a single nonlinear dendritic branch computes XOR. This is the biological analog of the substrate's BIND primitive (forming a second-order conjunction). So a substrate that HAS bind has the representational analog; if it tied chance even with conjunction features (ORACLE fail), THAT would be a real representational bound to accept. MEASURED: ORACLE=1.0 -> substrate has the representational capacity, matching the brain's dendritic-conjunction affordance.
- **Predictive/error element maps to the LEARNING/SELECTION problem** (which conjunction matters among many candidates), NOT to representing XOR. The brain uses attention/salience/relevance gating to select among many possible conjunctions. MEASURED: BIND_HEBB (unweighted) degrades under many distractor conjunctions (R_large 0.642) while PREDCODE (error-gated selection) holds (1.0) -> matches the brain's use of relevance gating for SELECTION at scale. Predictive-loop is justified for SCALING (search among many conjunctions), not for parity representation per se.
- Net: the parity test isolates a MORE FUNDAMENTAL missing structure than the note framed — CONJUNCTION FORMATION (binding), which the substrate already has — with the predictive/error element earning its keep specifically in the many-distractor dilution regime. This is a hypothesis-pending-VET strategic read (caveat per Director discipline); skunkworks landed-VET to confirm.

## MEASURED results (on disk: `data/exp_parity_in_context_binding_v1/metrics.json`)
- R_small (W=8, C=28 pairs): CORR 0.501, ORACLE 1.000, BIND_HEBB 1.000, PREDCODE 1.000; recovery 1.000; predcode_focus 1.000.
- R_large (W=40, C=780 pairs, n_train=100): CORR 0.499, ORACLE 1.000, BIND_HEBB 0.642, PREDCODE 1.000; recovery 1.000; predcode_focus 1.000.
- Verdict: HARD_PASS_STRUCTURE_DISCRIMINATES; localization {R_large: predictive_error_element_required, R_small: binding_alone_suffices}.
