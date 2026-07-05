# Research: ranking the 3 "multiples improve capability" candidates + decisive-cell spec for the top pick

**Date:** 2026-07-05
**Type:** Operational drill on an existing finding (2x-style depth, not a fresh lit-scan-as-verification). Spec only -- no dispatch.
**Trigger:** `notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` Section 3 named 3 "multiples/redundancy" candidates and flagged the R-banks-of-N == 1-bank-of-R*N caveat (delta<0.004) as the trap any of them could fall into. Since that note, `exp_pfc_gate_cfrpe_trained_v1` PASSED smoke (MIDDLE_BAND, gonogo_lift=+0.365, dynamics_lift=+0.4375, reach-vs-target-cosine corr=-0.086) -- verified directly off `data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json`, not asserted from memory.
**Discipline:** lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis P capped at 0.50). 1 parallel Sonnet lit-scan sub-agent dispatched on generic ensemble/bagging/TD-variance terms only -- no substrate-specific language left the query per query-privacy discipline.

---

## HEADLINE

**The just-passed `exp_pfc_gate_cfrpe_trained_v1` smoke result contains its own answer for which "multiples" candidate to build next: the ONE criterion that kept it at MIDDLE_BAND instead of HARD_PASS was cross-seed variance (`gonogo_cv=0.187`, vs the required `<0.10` -- every other HARD_PASS gate, including the anti-tautology dynamics-attributable check, already cleared). Variance reduction via decorrelated ensembling is the textbook fix for exactly that failure mode. Ranked by capability-gain x feasibility x decorrelation-plausibility, an ENSEMBLE of independently bootstrap-trained SR-transport/RPE estimators (candidate 1) beats POPULATION-CODED BG signal (candidate 2, real headroom but the existing diagnostic already calls the BG-analog operator's 0.04-lift ceiling "96% irreducible," which is a structural, not noise, ceiling -- exactly the profile the R-bank trap predicts) and 3-TIER CLS (candidate 3, a temporal-separation-of-function architecture that doesn't map onto the parallel-redundancy/decorrelation framework at all, plus 2 MIDDLE_BAND + 1 HARD_FAIL of prior evidence already banked). The decisive cell for candidate 1, `exp_pfc_gate_ensemble_cfrpe_v1`, is spec'd below with an explicit EQUAL-COMPUTE-BUDGET single-estimator control -- the one arm that turns "beats nothing" into "beats the R-bank trap," per the user's explicit caveat.**

Plain-English: the trained basal-ganglia gate we just shipped works, but it's a little noisy from one random seed to the next. In the brain, noisy signals get more reliable when several independent copies vote and average out -- that's literally what an ensemble is. We're proposing to train 5 independent copies of the reward-signal estimator (each seeing a different random slice of experience) and average them, but the experiment is designed so it can ONLY "pass" if the 5 copies are shown to be more informative than one estimator that got 5x as much training time instead -- otherwise we'd just be rediscovering the same "more copies of the same thing isn't a free lunch" result we already found on the memory side.

---

## 1. RANKING: the 3 multiples/redundancy candidates

| Rank | Candidate | Capability gain | Feasibility | Decorrelation plausibility | Verdict |
|---|---|---|---|---|---|
| **1** | **Ensemble RPE / SR-transport** (K independently bootstrap-trained value estimators, averaged) | HIGH -- directly targets the ONE metric (`cv=0.187`) that blocked today's HARD_PASS; GONOGO=0.479 vs ORACLE=0.969 still leaves 0.49 headroom | EASY -- reuses the entire `exp_pfc_gate_cfrpe_trained_v1` harness verbatim (KB, chains, E, W_ops, test set); only new code is a loop over K bootstrap-resampled `train_sr_transport` calls + averaging `reach_value` | HIGH -- bootstrap resampling of the shared rollout-transition pool is the textbook decorrelation mechanism (Osband et al. 2016 bootstrapped-DQN; Anschel et al. 2017 Averaged-DQN uses the SAME averaging-of-K-value-estimates recipe explicitly for variance reduction under equal compute) | **BUILD NEXT** |
| 2 | Population-coded BG conflict signal (replace the single scalar BG-analog operator with a multi-unit population code) | HIGH in principle (0.04 lift is nearly the floor) but the existing diagnostic (`frustration_bg_analog_cpu_v1`) already characterizes 96% of the frustration as "irreducible" -- language that describes a STRUCTURAL ceiling, not a noisy-estimator ceiling | MEDIUM/HARD -- no existing multi-unit harness to extend; the population's sub-units would need genuinely different tuning/basis (not N copies of the same scalar), which is an unsolved design question, not a drop-in loop | LOW/UNCERTAIN -- exactly the profile that produces the R-bank trap (replicating the same computation over "units" that carry the same information is definitionally what failed on the memory side, delta<0.004) | DEFER -- worth a dedicated design pass on WHAT distinguishes each population unit before building; don't build populations of the same scalar |
| 3 | 3-tier CLS (add a mid-timescale consolidation tier between fast/hippocampal and slow/cortical) | MEDIUM -- brain genuinely has >2 consolidation timescales, but our existing 2-tier CLS is itself weak/mixed (2x MIDDLE_BAND, 1x HARD_FAIL: `two_substrate_fastslow_cls` recall 0.689/0.378, both below gate, seed-robust) | HARD -- needs a new architecture (3 stores + a consolidation/replay schedule), not a loop over an existing harness; highest build cost of the three | DOES NOT MAP -- CLS tiering is a temporal-separation-of-FUNCTION architecture (each tier does a different job at a different rate), not a parallel-redundancy/ensemble-averaging structure; the Krogh-Vedelsby/bagging decorrelation framework that grounds candidates 1 and 2 has no natural analog here | DEFER -- per explicit caveat ("do NOT re-run naively"); adding a 3rd tier to an already-weak 2-tier system compounds architecture risk with no decorrelation theory to justify it |

**Why #1 wins outright, not just narrowly:** it is the only candidate that (a) has a concrete, already-measured failure mode to fix (`cv=0.187` vs `<0.10` -- a 0.087 gap, not a vague "more headroom exists" argument), (b) reuses a harness that already exists and already works, and (c) has direct external precedent for the EXACT mechanism (ensembling K independently-trained TD/value estimators, evaluated under an equal-compute-budget control) rather than a generic "redundancy helps" appeal. Candidates 2 and 3 are real candidates for a LATER cycle but are currently under-specified (2) or architecturally risky given prior weak evidence (3).

---

## 2. External lit-scan grounding (generic terms only; no substrate specifics left the query)

1 Sonnet sub-agent, public sources only:

- **Bagging variance formula (confirmed standard, Breiman 1996 / Hastie-Tibshirani-Friedman ESL ch.15):** `Var(mean of K estimators) = sigma^2 * [rho + (1-rho)/K]`, where `rho` = average pairwise correlation between members. **As K -> infinity, variance floors at `sigma^2 * rho`** -- the achievable variance reduction from ANY ensemble size is capped by how correlated the members already are. This is the formula the decorrelation control below is built on.
- **Direct precedent for TD/value-function ensembles:** Osband, Blundell, Pritzel & Van Roy, "Deep Exploration via Bootstrapped DQN" (NeurIPS 2016) -- K bootstrap-resampled heads on shared experience (structurally identical to the design below). Anschel, Baram & Shimkin, "Averaged-DQN: Variance Reduction and Stabilization for Deep RL" (ICML 2017) -- averages K value estimates specifically to reduce target-approximation variance, same total compute as the non-averaged baseline. This is the closest published analog to the equal-compute-budget control this cell requires.
- **Correlation threshold for "effectively redundant":** no single universal number, but the formula gives a principled one -- at `rho=0.90`, the BEST POSSIBLE variance reduction from any K is capped at ~10%; ensemble-feature-selection literature separately uses `rho>0.75` as a practical redundancy cutoff.
- **Equal-compute-budget failure precedent (the exact risk this cell is designed to catch):** Ashukha et al., "Pitfalls of In-Domain Uncertainty Estimation and Ensembling in Deep Learning" (ICLR 2020) -- large single homogeneous models can match deep-ensemble accuracy/calibration at matched budget. "Theoretical Limitations of Ensembles in the Age of Overparameterization" (ICML 2025, arXiv:2410.16201) -- proves overparameterized ensembles converge to a single matched-budget model with no inherent edge. This is the modern-ML restatement of our own R-banks-of-N==1-bank-of-R*N finding -- independent corroboration, not a new risk.

**P_deflated(claim: "ensemble RPE beats an equal-compute-budget single estimator on this substrate") = 0.38** (raw ~0.55: strong mechanism-class precedent [Osband, Anschel] + a concrete already-measured variance gap to close; -0.17 lit-scan calibration for novel-synthesis -- the specific composition [bootstrap-resampled SR-transport M-matrices feeding a Go/NoGo gate] has never been tried on this substrate, and the equal-budget-failure literature above is a real, not hypothetical, risk given the rollout-transition pool may be too small at smoke scale [6000 transitions] to generate genuine bootstrap diversity).

---

## 3. Decisive cell spec: `exp_pfc_gate_ensemble_cfrpe_v1`

**Reuses verbatim from `experiments/exp_pfc_gate_cfrpe_trained_v1.py`:** KB/chain generation (`make_kb_and_chains`), codebook (`make_bipolar_E`), operator matrices (`hebbian_W`), cleanup (`cleanup_batched`), rollout collection (`collect_rollout_transitions`), the `train_sr_transport` TD(0)/cfrpe delta-rule trainer, `reach_value`/`reach_control_targetcos`, the paired per-seed harness, and all rail bands (`ORACLE_RAIL_MIN`, `BASELINE_IN_BAND_*`, `ADDITIVE_RAIL_*`). **New code is additive only:** a loop over K bootstrap resamples of the rollout-transition pool feeding K independent `train_sr_transport` calls, an averaged `reach_value` across members, one equal-compute-budget single-estimator control arm, and 3 new diagnostics (cv-ratio, mean-pairwise-reach-correlation, promotion-check against the ORIGINAL v1 cell's own HARD_PASS bands).

### Arms (paired -- all share E, W_ops, and the SAME test chains per seed)

| Arm | Description | Total SR-training compute |
|---|---|---|
| `V1_NO_GOAL` | rail (unchanged) | -- |
| `ADDITIVE_BASELINE` | rail (unchanged) | -- |
| `CFRPE_CONTROL_IDENTITY` | anti-tautology foil (unchanged) | -- |
| `SINGLE_GONOGO_1X_BUDGET` | reproduces today's PASSED cell exactly (1 M, `SR_STEPS` steps) -- sanity rail, should reproduce `~0.479` test acc / `cv~0.187` at smoke scale | 1x |
| **`SINGLE_GONOGO_EQUAL_BUDGET`** | **ONE M trained on the full (non-bootstrapped) transition pool for `K x SR_STEPS` steps** -- the "1 bank of R*N" analog: same total compute as the ensemble, but monolithic, no decorrelation | Kx |
| **`ENSEMBLE_GONOGO_K5`** | **K=5 independently bootstrap-resampled (with replacement, same pool size) M-matrices, each trained for `SR_STEPS` steps with an independent RNG stream; `reach_ensemble = mean_k reach_value(cand, goal, M_k)`** -- THE TEST | Kx |
| `ORACLE` | rail (unchanged) | -- |

Optional secondary consistency check (non-gating): repeat `ENSEMBLE_GONOGO_K5` at K=3 to confirm cv-ratio moves in the direction the bagging formula predicts as K changes -- if it doesn't, that itself is diagnostic of high `rho`.

### Primary discriminators (paired, decision_depth unchanged)

- `ensemble_vs_equal_budget_lift = mean_test_acc(ENSEMBLE_GONOGO_K5) - mean_test_acc(SINGLE_GONOGO_EQUAL_BUDGET)` -- **THE decorrelation control.** This is what stands between "beats nothing" and "beats the R-bank trap": `SINGLE_GONOGO_EQUAL_BUDGET` gets the exact same total training compute as the ensemble, so any lift here is attributable ONLY to decorrelation across independently-sampled members, not to "more compute."
- `cv_ratio = cv(ENSEMBLE_GONOGO_K5 across seeds) / cv(SINGLE_GONOGO_EQUAL_BUDGET across seeds)` -- variance-reduction signature, interpretable directly via the bagging formula (`ratio ~= rho + (1-rho)/K`).
- `mean_pairwise_reach_corr (rho)` = average Pearson correlation between `reach_k(cand, goal)` scores across all `K*(K-1)/2` member pairs, computed on held-out test-chain candidates, pooled across seeds -- the direct MECHANISTIC decorrelation diagnostic (not inferred from cv, measured directly).
- `promotion_check`: does `ENSEMBLE_GONOGO_K5`'s OWN cross-seed `cv` fall under the ORIGINAL v1 cell's `HP_CV_MAX=0.10` while `gonogo_lift(ensemble vs additive)>=0.155` and `dynamics_lift(ensemble vs identity-control)>0.05` still hold -- i.e., does the ensemble complete the promotion of today's MIDDLE_BAND result to HARD_PASS on the bands that were ALREADY pre-registered (not new, looser bands invented after the fact)?

### HARD-PASS (ALL required)

1. `ensemble_vs_equal_budget_lift >= 0.03` (absolute test-chain accuracy; ensemble genuinely beats the SAME-compute monolithic estimator)
2. `cv_ratio <= 0.60` (implies `rho <~ 0.50` via the bagging formula -- a formula-consistent, not just numerically-convenient, variance-reduction bar)
3. `mean_pairwise_reach_corr (rho) < 0.70` (members measurably decorrelated -- direct mechanistic confirmation)
4. `ENSEMBLE_GONOGO_K5` cross-seed `cv < 0.10` (closes exactly the gap that blocked the immediately-prior cell's HARD_PASS)
5. paired sign-test (chain-level correct/incorrect, ensemble vs equal-budget-single) `p < 0.05`
6. rails hold: `oracle >= 0.90`, additive-baseline in-band, `dynamics_lift(ensemble vs identity-control) > 0.05`, `gonogo_lift(ensemble vs additive) >= 0.155`

### HARD-FAIL (ANY triggers)

1. `ensemble_vs_equal_budget_lift <= 0.00` -- **the equal-compute single estimator matches or beats the ensemble.** This is the R-bank trap confirmed in the RPE domain: the "multiple" added nothing beyond raw compute, exactly what the `Ashukha 2020` / `ICML 2025 overparameterized-ensembles` literature above warns is common.
2. `mean_pairwise_reach_corr (rho) >= 0.90` -- members are near-redundant; by the bagging-variance floor (`floor = rho`), the BEST possible variance reduction at `rho=0.90` is capped at ~10% regardless of K. This is a structural, not statistical-noise, explanation for a null result.
3. `cv_ratio >= 0.95` -- no meaningful variance reduction at all, independent of any mean-lift number.

### MIDDLE-BAND

Positive `ensemble_vs_equal_budget_lift` and/or partial variance reduction that doesn't clear the joint bar -- e.g. lift real but `rho` in `[0.70, 0.90)` (partial decorrelation), or `cv_ratio` in `(0.60, 0.95)`, or the lift/cv criteria pass but `ENSEMBLE_GONOGO_K5`'s own cv still `>= 0.10` (a genuine partial win that doesn't complete the promotion to HARD_PASS).

**Compute:** CPU, ~2-4x the original cell's 23.7s smoke runtime (K=5 SR-transport trainings instead of 1, all still batched matmul, no new representational machinery). FULL scale similarly cheap relative to the rest of the pipeline.

---

## Cheap decisive test

The spec in Section 3 above IS the cheap decisive test: reuse of an existing, already-fast (23.7s smoke) harness plus a K=5 bootstrap loop and one equal-budget control arm. No new representational machinery, no new KB/chain generation, no GPU required.

## Falsifiable predictions

**HARD-PASS** (ensembling genuinely decorrelates and helps): `ensemble_vs_equal_budget_lift>=0.03` AND `cv_ratio<=0.60` AND `rho<0.70` AND ensemble's own `cv<0.10` AND rails hold (full band list in Section 3).
**HARD-FAIL** (this is the R-bank trap recurring in the RPE domain): `ensemble_vs_equal_budget_lift<=0.00` OR `rho>=0.90` OR `cv_ratio>=0.95`.
**MIDDLE-BAND**: partial decorrelation benefit that doesn't clear the joint bar.

## Cross-thread synthesis

Builds directly on `notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` Section 3 (names all 3 candidates + the R-banks caveat) and on the just-landed `data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json` (identifies `cv=0.187` as the SOLE blocking criterion for HARD_PASS -- verified directly, not inferred). Extends the neuromodulation/basal-ganglia thread (`exp_pfc_gate_cfrpe_trained_v1`, `frustration_bg_analog_cpu_v1`) without re-opening the weak/mixed CLS thread (`c1_cls_replay_continual_ingest_complete_2026-06-22.md`: harness-verified but decisive test never reached full scale; `director_cell_consolidation_v2_proper_test_spec_2026-06-25.md`: HARD_FAIL_DECISIVE band already spec'd for a HARD_FAIL that has not yet been reversed) per the explicit "don't re-run naively" instruction. Directly reuses the memory-domain finding (equal-total-memory R-banks-of-N == 1-bank-of-R*N, delta<0.004) as the STRUCTURAL TEMPLATE for this cell's decorrelation control, rather than treating it as a closed/unrelated result.

## Substrate-product implications

If HARD-PASS: closes the ONE remaining gap between the just-shipped trained BG gate and a clean HARD_PASS verdict, using a mechanism (ensembling with an explicit equal-budget control) that is itself inspectable and glass-box (K named estimators + a measured decorrelation number), reinforcing the "trained, auditable Go/NoGo gate" product story rather than adding an opaque black-box ensemble. If HARD-FAIL: valuable negative -- confirms the R-bank/re-partition trap generalizes beyond memory capacity into control-signal estimation, which sharpens the product claim to "redundancy helps ONLY where independently-sourced information exists" rather than "redundancy helps" unconditionally, and redirects the next multiples-build cycle toward candidate 2 (population-coded BG) with a mandatory decorrelation-by-design step, or toward genuinely new information sources (e.g. more diverse rollout-exploration policies) rather than more compute on the same pool.

## Citations (verified: 6, cross-checked by 1 independent Sonnet lit-scan sub-agent against public sources; internal figures verified via direct Read of `experiments/exp_pfc_gate_cfrpe_trained_v1.py` and `data/exp_pfc_gate_cfrpe_trained_v1_smoke/metrics.json`, not asserted from memory)

1. Breiman L (1996) Bagging predictors. *Machine Learning* 24(2):123-140.
2. Hastie T, Tibshirani R, Friedman J. *The Elements of Statistical Learning*, ch.15 (random forests / decorrelating trees via the bagging-variance identity).
3. Osband I, Blundell C, Pritzel A, Van Roy B (2016) Deep exploration via bootstrapped DQN. arXiv:1602.04621 / NeurIPS.
4. Anschel O, Baram N, Shimkin N (2017) Averaged-DQN: variance reduction and stabilization for deep reinforcement learning. arXiv:1611.01929 / ICML.
5. Ashukha A et al. (2020) Pitfalls of in-domain uncertainty estimation and ensembling in deep learning. ICLR (arXiv).
6. Theoretical limitations of ensembles in the age of overparameterization (2025) ICML, arXiv:2410.16201.

Carried over from the prior inventory-drill note (already-verified, not re-verified here): Krogh A, Vedelsby J (1995) NeurIPS ambiguity decomposition; Wood D et al (2023) *JMLR* 24 unified diversity theory; Knight JC, Leveson NG (1986) *IEEE TSE* multiversion-programming correlated failures.
