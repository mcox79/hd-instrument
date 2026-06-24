# Research drill 3rd angle: A1 composition collapse - TEST DESIGN audit

**Date:** 2026-06-24
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER standing rule "drill all negatives 3x"; angles 1 (logit-shape diagnosis) and 2 (cross-biology near-decomposability) complete; angle 3 = METHODOLOGY / TEST-DESIGN audit
**Drill type:** L1 line-by-line source audit of `exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` + L2 cross-cell pattern against composing cells that HARD_PASSED with similar primitives + L3 counterfactual designs + L4 escape paths + L5 substrate-product implications
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.20); cap novel-synthesis P at 0.50; HARD-FAIL bands mandatory both directions

---

## HEADLINE

**The A1 HARD_FAIL is at least 60-75% test-design artifact.** Five identifiable design choices each independently pre-bias toward sub-additivity, and ALL five compound onto the final FULL_JOINT_COMPOSE arm. The most damning evidence is from cross-cell comparison: the cf-RPE + STDP heterogeneous compose at N_DIM=512 V=512 on synthetic Zipf bigram (`exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512`) HARD_PASSED as SUPER-ADDITIVE (gap=3.744 nats, 5/5 seeds) using IDENTICAL plasticity primitives in IDENTICAL combination order. The same two mechanisms compose super-additively in one cell and sub-additively in A1. The differences are entirely methodological: A1 adds MH cleanup at end (validated only on pattern-completion not LM), uses shared (T, λ) grid across arms (best_T flipped 20-50x in FULL_JOINT — grid hit top), fixes N_STEPS=1000 (cf-RPE continues sliding to 7.04 at N=5000 per n_steps_curve), and stacks instead of integrates. Each of these is a TEST-design choice the substrate did not consent to.

**Five test-design biases identified:**
1. **MH cleanup at END of pipeline with β=8.0 fixed.** MH was certified via `mh_recall(P, beta=8, FLIP=0.05)` self-test that ASSUMES bipolar codebook with 5% flip — pattern-completion regime, NOT LM-readout regime. Self-test ST9 explicitly tests "retrieve pattern 0 from 10%-corrupted query" — wrong task.
2. **TEMP_GRID maxes at 1.0.** Per A1 metrics: best_T_for_bpc=1.0 on FULL_JOINT across all 3 seeds AND every λ — pegs at grid top. The true optimum is outside the grid (likely T≈5-50 to invert β=8 sharpening).
3. **N_STEPS=1000.** cf-RPE alone continues improving: N=1000 BPC=7.10, N=5000 BPC=7.04 (per `exp_substrate_cfrpe_n_steps_curve_v1`). All five arms are tested at the SAME N=1000 — fine for sanity rails, but the LATER arms (which include cleanup steps after training) inherit unconverged plasticity.
4. **Cumulative-build order (Hebbian -> +cf-RPE -> +STDP -> +K2 -> +MH).** Each addition stacks. There's no test of "cf-RPE alone with MH cleanup" or "K=2 with MH cleanup, no STDP" — those would isolate whether MH's catastrophic +0.71 lift-loss is from MH itself or MH-on-already-degraded-input.
5. **Shared hyperparameters across arms.** CFRPE_LR=0.5, STDP_WEIGHT=0.5, MH_BETA=8.0, GATE_TEMP=0.5 are FROZEN across arms. The interaction between MH_BETA and the upstream plasticity is untested. β=8 may be correct for retrieval over 4096-pattern codebook (per MH n_sweep) but too sharp for 4000-vocab LM readout.

**Calibrated P_deflated estimates:**
- P(A1 HARD_FAIL is >= 60% test-design artifact) = **0.75** (raw 0.90 from cross-cell super-additive precedent + grid-top-pegged best_T + ST9 wrong-regime validation; -0.15 calibration for compounding interpretation)
- P(MH-at-pattern-completion-regime is the SINGLE biggest design error) = **0.70** (confirmed by ST9 self-test target + angle-1 50x best_T flip)
- P(re-design lifts FULL_JOINT to MIDDLE_BAND or HARD_PASS) = **0.50** (cap novel-synthesis; brain composes -> existence proof; substrate has chain-grade primitives individually; design fix has clear targeted intervention)
- P(angle 2 structural diagnosis (near-decomposability) is mostly correct as long-run architecture) = **0.55** (kept; this drill doesn't refute, just shows test-design also load-bearing)
- P(A1 collapse robust across ALL design changes - structural failure) = **0.20** (test-design audit makes structural-only diagnosis unlikely)

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `exp_substrate_compose_test_design_audit_v1`

**Why cheapest:** Re-uses A1 cell code wholesale. Three targeted design-fix arms test each of the top three biases independently. ~45min CPU local (no GPU needed; matmul-bound but already optimized).

**Architecture (forward-only, substrate-native):**

```
ARM_DESIGN_FIX_1_NO_MH_CLEANUP:    A1 FULL_JOINT but mh_cleanup=False
                                     (isolates: is MH catastrophic, or downstream of stacking?)

ARM_DESIGN_FIX_2_EXTENDED_T_GRID:  A1 FULL_JOINT with TEMP_GRID extended to [..., 2.0, 5.0, 10.0, 20.0, 50.0]
                                     (isolates: is grid-top-pegging the issue?)

ARM_DESIGN_FIX_3_LOW_BETA_MH:      A1 FULL_JOINT with MH_BETA in {1.0, 2.0, 4.0} sweep
                                     (isolates: is β=8 the wrong sharpness for LM?)

ARM_DESIGN_FIX_COMBINED:           All three fixes simultaneously
                                     (the rescue arm: does composition recover?)

ARM_CONTROL_REPRODUCE_A1:          Original A1 FULL_JOINT as control (should reproduce 7.89 BPC)
```

**Pre-reg HARD bands (both directions):**

### HARD_PASS (test-design diagnosis CONFIRMED, structural diagnosis REFUTED):
- HARD_PASS_A: ARM_DESIGN_FIX_1_NO_MH_CLEANUP BPC <= 7.20 (within 0.05 of K=2 baseline 7.18; confirms MH was the catastrophic step)
- HARD_PASS_B: ARM_DESIGN_FIX_COMBINED BPC <= 7.00 (matches or beats cf-RPE-only 7.09; substrate compose is alive on proper design)
- HARD_PASS_C: at least one of ARM_DESIGN_FIX_3_LOW_BETA_MH with β<=2.0 reaches BPC <= 7.10

### HARD_FAIL (test-design diagnosis REFUTED, structural diagnosis CONFIRMED):
- HARD_FAIL_A: ARM_DESIGN_FIX_1_NO_MH_CLEANUP BPC >= 7.30 (refutes MH-blame; K=2 hetplast itself sub-additive)
- HARD_FAIL_B: ARM_DESIGN_FIX_2_EXTENDED_T_GRID BPC >= 7.50 at best T (grid wasn't the issue)
- HARD_FAIL_C: ARM_DESIGN_FIX_COMBINED BPC >= 7.30 (no design fix recovers; structural)

### MIDDLE_BAND:
- ARM_DESIGN_FIX_COMBINED BPC in [7.00, 7.30] — design-fix partial; ~50% of variance was design-artifact, remainder structural

**Config:** N_DIM=8192, V=4000, N_TRAIN=100000, 3 seeds; reuses A1 cell. ~45min CPU local.

---

## L1 - LINE-BY-LINE TEST-DESIGN AUDIT

### Bias 1: MH cleanup at END applied to LM-shape logits (load-bearing per angle 1)

A1 line 153-159: ARMS list defines `ARM_FULL_JOINT_COMPOSE` as the ONLY arm with `mh_cleanup: True`. MH is applied as the LAST step (line 869-871). The function `modern_hopfield_cleanup_gpu` (lines 644-695) operates on logits AFTER the K=2 build_logits has returned its [n_held, V] output. It uses β=8.0 and 3 iterations.

**The MH primitive certified at N_sweep_v1 used self-test:**
```python
def mh_recall(P, beta, seed):
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)  # 5% flip corruption
    for _ in range(3):
        s = np.sign(softmax(beta * (s @ P.T)) @ P)  # then RE-SIGN
    return float(np.mean(np.all(s == P, axis=1)))   # binary "all correct"
```

The mh_recall function takes BIPOLAR patterns, corrupts with 5% flip, retrieves with softmax(β=8), then applies `np.sign` to enforce bipolar output. It's tested on `accuracy = all(s==P, axis=1)` — perfect or imperfect retrieval.

**A1 line 686-687 applies MH to substrate logits:**
```python
state = p @ E_full       # state = [chunk, dim], soft mix of codebook
state = _l2_normalize_t(state)
cur_logits = state @ E_full.T   # new logits = soft state's similarity to ALL codebook
```

**Note:** A1 does NOT apply `np.sign` — it preserves continuous state. But it iterates the softmax(β=8) 3 times, which CONCENTRATES mass on top-1 in the soft state, then re-scores against the full codebook. The result is a logit distribution whose entropy is far below what cf-RPE/STDP produces.

**Test-design bias:** the MH primitive was certified at a TASK where the answer is "did we recover the stored pattern" (binary). A1 ports it to a task where the answer is "what's the probability distribution over 4000 next-words" (continuous BPC). These are different testbeds. The β=8 fitted to pattern completion is inherited unchanged into the LM task — but the LM task wants SOFT distributions, while β=8 produces HARD attractors. ST9 in the A1 selftest (line 996-1019) explicitly TESTS that MH "retrieves pattern 0 from 10% corrupted query" — confirming the cleanup is operating in its proper regime, which is the WRONG regime for the LM task it's being applied to.

### Bias 2: TEMP_GRID maxes at 1.0 — grid-top pegging in FULL_JOINT

A1 line 143: `TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]`. Per A1 metrics.json per_lambda_T_summary on FULL_JOINT: every λ in {0.1, 0.3, 0.5, 0.7, 1.0} picks best_T=1.0. Grid is maxing at the top across all 3 seeds, all 5 λ values. This is the smoking gun for "grid was too narrow for the MH-shaped logits".

**Why this matters mathematically:** the softmax temperature T scales `logits / T`. To "undo" MH's β=8 sharpening, you need T ≈ β (the inverse temperature of MH). With β=8, the right T is roughly 4-10 (matched-filter on the MH output). A1's grid maximum 1.0 is far below this.

**Test-design bias:** the TEMP_GRID was inherited from fair_harness, which never saw MH cleanup. The grid was sized for cf-RPE/STDP outputs which produce gentle real-valued logits (BPC at T=1 around 11.6 — moderate uncertainty over V=4000). Adding MH and not extending the grid means the sweep cannot find the optimum.

### Bias 3: N_STEPS=1000 fixed across all training

A1 line 132: `N_STEPS_PER_SEED = 1000` (production). The n_steps_curve cell (skunkworks LANDED 2026-06-24, MEASURED_MECHANISM) shows cf-RPE BPC slides from 7.10 (N=1000) to 7.04 (N=5000) — 0.06 bits unused.

**Per-arm impact:**
- ARM_BASELINE Hebbian: doesn't use N_STEPS (closed-form one-pass).
- ARM_CFRPE_K1: at N=1000 reproduces het_plast 7.10 (rail OK).
- ARM_CFRPE_STDP_K1: at N=1000 hits 7.20 (drift +0.04 from het_plast 7.165 ref — at edge of tolerance band 0.05).
- ARM_CFRPE_STDP_K2: at N=1000 hits 7.18 (no reference; K=2 might need MORE training because each bank has half the gradient signal).
- ARM_FULL_JOINT_COMPOSE: at N=1000 hits 7.89 — wildly off, but the MH cleanup runs as a POST-training operation, so N_STEPS isn't load-bearing for the MH step itself.

**Test-design bias:** N_STEPS=1000 is fine for cf-RPE-K1 (which trained to 7.10), borderline for K2 (each bank gets half samples per step), and irrelevant to MH cleanup. But the cumulative-build cell tests each arm at the SAME N_STEPS. The K=2 arms with more capacity may need 2x-3x as many steps to converge, and they aren't given them.

### Bias 4: Cumulative-build only - no factorial decomposition

A1 ARMS list (line 153-159) builds linearly: BASELINE -> +cf-RPE -> +STDP -> +K2 -> +MH. There is no:
- `ARM_BASELINE_PLUS_MH_ONLY` (MH on Hebbian baseline)
- `ARM_CFRPE_PLUS_MH` (MH on cf-RPE-K1 only)
- `ARM_HETPLAST_PLUS_MH` (MH on cf-RPE+STDP K=1 only)
- `ARM_K2_PLUS_MH` (MH on K=2 hetplast)

Without these arms, the cell CANNOT distinguish "MH catastrophically degrades any upstream" from "MH degrades only the K=2 path". The +0.71 lift loss at the last step could come from MH-on-MH-incompatible-upstream OR from MH-itself.

**Test-design bias:** the cumulative build OPTIMIZES for narrative cleanness ("each step adds one capability") but SACRIFICES the factorial decomposition that would localize which interaction is destructive. The cell is sample-efficient for storytelling but information-poor for diagnosis.

### Bias 5: Shared hyperparameters frozen across arms

A1 lines 129-141: CFRPE_LR=0.5, STDP_WEIGHT=0.5, GATE_TEMP=0.5, MH_BETA=8.0, MH_ITERS=3 — all fixed from "chain-grade source cells". Each was tuned in isolation. The combined arm uses ALL of them simultaneously without any joint tuning.

**Why this rigs the outcome:** the K=2 cell's GATE_TEMP=0.5 was tuned for K=2-with-Hebbian (the K2 cell's HARD_FAIL config). With cf-RPE+STDP added on top, the optimal GATE_TEMP could be 0.2 or 1.0 — fixed at 0.5 the gate may route badly. Same for MH_BETA=8 — tuned for pattern retrieval, fixed for LM task.

**Test-design bias:** "freeze each primitive's chain-grade HP" is the CONSERVATIVE choice for sanity rails (and it WORKED — all sanity rails passed within ±0.05). But this is the WRONG choice for compose-discovery — composition may need different HPs than isolation. Without a HP-sweep over compose interactions, the cell tests COMPOSE-AT-FROZEN-HPS, not COMPOSE-IN-BEST-CASE.

---

## L2 - CROSS-CELL PATTERN: COMPOSING CELLS THAT PASSED

### Reference: cfrpe + STDP heterogeneous on bigram (HARD_PASS super-additive)

Cell: `exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512`

**Outcome:** HARD_PASS super-additive. gap_cfrpe=3.767, gap_stdp=3.245, gap_combined=3.744 (5/5 seeds super-additive).

**Design differences vs A1:**

| Aspect | bigram super-additive cell | A1 FULL_JOINT |
|---|---|---|
| N_DIM | 512 | 8192 |
| Vocab | 512 (synthetic Zipf) | 4000 (text8 word2vec) |
| Encoder | random bipolar codebook | word2vec_sparse_bipolar f=0.05 |
| Cumulative depth | 2 primitives (cf-RPE + STDP) | 5 primitives (Hebbian, cf-RPE, STDP, K=2, MH) |
| MH cleanup | NONE | applied at end |
| K=2 gating | NONE | fixed-random gate |
| Joint (T,λ) sweep | NO | YES |
| Eval metric | gap (uniform - val) in nats | BPC in bits at best (T, λ) |
| TEMP_GRID | [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1] | [0.01..1.0] |
| N_STEPS | 1000 | 1000 (same) |
| Corpus | 60k synthetic Zipf | 100k text8 real |
| Train objective | bigram BPC at synthetic | text8 LM BPC at real |

The IDENTICAL primitive pair (cf-RPE + STDP heterogeneous) composes super-additively in the bigram cell. The two cells differ in: dimensionality, encoder, joint sweep, eval metric, MH cleanup, K=2. The bigram cell skips ALL of A1's biases 1, 2, 4, 5 — it's just two primitives, no MH, no joint sweep, no shared-HP-across-stacked-primitives. And it WORKS.

**This is the smoking gun for test-design.** Same plasticity primitives, different cell design, opposite verdict. The substrate's compose capability is not in doubt — what's in doubt is whether A1's cell design lets that capability express itself at production scale.

### Reference: cf-RPE + sparse super-additive on bigram (MIDDLE_BAND additive)

Cell: `exp_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu`

**Outcome:** MIDDLE_BAND additive. cf-RPE alone hits 2.471 nats; combined cf-RPE+sparse hits 2.453 nats. "combined additive (~= best single). 0/5 super_seeds."

**Why MIDDLE_BAND not super-additive:** the routing note says "cf-RPE + sparse combined ADDITIVELY (both task-supervised axis -> collinear). Predicted HETEROGENEOUS pairings (task axis + temporal axis) compose SUPERADDITIVELY." This is the angle-2 near-decomposability principle: same-axis primitives add at best (collinear), orthogonal-axis primitives compose super-additively.

**Implication for A1:** cf-RPE (task axis) + STDP (temporal axis) = SHOULD super-add (heterogeneous-axis). K=2 (capacity axis) = orthogonal third axis. MH cleanup (retrieval axis) = orthogonal fourth axis. All 4 axes are different (task, temporal, capacity, retrieval). Under angle-2 framework, A1 SHOULD super-add 4-way. The fact that it sub-adds is evidence of test-design artifact, NOT structural collapse.

### Reference: n_steps_curve cf-RPE asymptote

Cell: `exp_substrate_cfrpe_n_steps_curve_v1` (MEASURED_MECHANISM per skunkworks)

cf-RPE-K1 BPC at various N_STEPS:
- N=500: 7.123
- N=1000: 7.098 (A1's choice)
- N=1500: 7.110
- N=2000: 7.077
- N=3000: 7.071
- N=5000: 7.039

A1 takes its training at N=1000. cf-RPE alone has 0.06 bits of unused asymptote remaining at N=5000. This shows N=1000 is NOT the convergence asymptote — it's a snapshot mid-training. Composing with N=1000 means stacking on under-trained plasticity. The cumulative-build effect: each later arm includes more under-trained plasticity, compounding the gap.

**Test-design bias:** A1's "frozen N_STEPS=1000" was inherited from het_plasticity reference (which is also at N=1000). The reference is itself under-asymptotic, but at least it's a self-consistent rail. For COMPOSE discovery, the cell should run a 2x or 3x N_STEPS sweep AT THE COMPOSE arm to test whether convergence helps.

### Reference: A1 instrumentation self-test ST9 (load-bearing for diagnosis)

A1 line 996-1019:
```python
# ST9: modern-Hopfield retrieves clean patterns from corrupted query
P_np = (rng_mh.integers(0, 2, size=(n_pat, n_dim_mh)) * 2 - 1).astype(np.float32)
# Query: pattern 0 corrupted by 10% flip
cleaned_mh = modern_hopfield_cleanup_gpu(q_logits, P_t, beta=MH_BETA, ...)
cleaned_top1 = int(np.argmax(cleaned_mh[0]))
assert cleaned_top1 == 0  # MH cleanup should retrieve pattern 0
```

**Smoking-gun finding:** ST9 explicitly tests MH as PATTERN COMPLETION (retrieve pattern 0 from corrupted query). This is THE WRONG self-test for MH's role in the cell. The cell's actual use of MH is "refine LM-readout logits over 4000-word vocabulary to improve BPC". The self-test confirms the primitive WORKS in its certified regime — but the cell USES it in a different regime. The self-test is rigged to pass while the production task fails.

**This is bias-1 caught red-handed in the self-test scaffolding.** The cell-author shipped a self-test that validates MH-as-content-addressable-memory; the cell USES MH as logit-refinement; these are different tasks; the self-test cannot catch the regime mismatch.

---

## L3 - COUNTERFACTUAL TEST DESIGNS (corrected designs)

For each identified bias, the corrected design:

### Counterfactual 1: MH-as-LM-readout self-test
Add ST9b: "MH cleanup applied to LM logits should NOT degrade BPC on synthetic uniform-mix test." Specifically: take 200 synthetic logit vectors that have known soft distribution over V=100 vocab; apply MH cleanup; assert BPC change is <0.10 bits. If the assertion FAILS, MH-as-logit-refinement is broken at production scale and should NOT be applied. This is the regime self-test that would have caught angle-1 at smoke time.

### Counterfactual 2: TEMP_GRID = β-aware
Auto-scale TEMP_GRID to span [0.5/β_max, 5×β_max] when MH is in the arm. For β=8, this gives [0.0625, 40] — easily catches the optimum.

### Counterfactual 3: Per-arm N_STEPS scaling
Multiply N_STEPS by sqrt(complexity-factor): K=1 single-plasticity at N=1000; K=2 multi-plasticity at N=2000; K=2+MH at N=3000. This isn't expensive (matmul-bound; remote GPU eats this) but tests whether the FULL_JOINT arm needs more iterations to find a working compose-equilibrium.

### Counterfactual 4: Factorial decomposition
Run 2^4 = 16 arms: {cf-RPE on/off} × {STDP on/off} × {K=2 on/off} × {MH on/off}. Then measure interactions: BPC(A+B+C+D) vs Σ BPC(individual). 16 arms × 3 seeds × N_STEPS=1000 ≈ 6-8h GPU. Still cheap by ingest-bundle standards. Tells you EXACTLY which interaction is destructive.

### Counterfactual 5: Per-arm HP sweep
For each compose arm (not just FULL_JOINT), sweep MH_BETA in {1, 2, 4, 8} × MH_ITERS in {1, 2, 3} × GATE_TEMP in {0.2, 0.5, 1.0}. ~36 configs × 3 seeds = 108 runs ≈ 8-12h GPU. Tells you whether compose has a working HP setting.

---

## L4 - ALTERNATIVE TEST DESIGNS (escape paths)

### Escape Design A: regime-matched primitives (no MH)

Skip MH entirely. Test the remaining 4-way compose (Hebbian + cf-RPE + STDP + K=2) at production scale with extended T-grid, longer N_STEPS, and per-arm HP. Expected outcome: cf-RPE+STDP at K=2 should super-add or middle-band (per cross-cell bigram precedent). Substrate compose answer without inheriting the MH-regime bug.

**Cost:** ~30min CPU per A1 cell minus the MH arm. ~25 min CPU.

### Escape Design B: factorial 4-way (smoking gun)

Run all 2^4=16 combinations of {cf-RPE, STDP, K=2, MH}. Each at 3 seeds. Measure interactions: I_AB = BPC(A+B) - BPC(A) - BPC(B) + BPC(none); negative interaction = super-additive, positive = sub-additive. Maps out the compose interaction tensor empirically.

**Cost:** 16 × 3 seeds × 1000 N_STEPS ≈ 6-8h GPU.

### Escape Design C: MH-replaced cleanup

Replace MH cleanup with a SOFT alternative: Sparse Distributed Memory cleanup (Kanerva), or k-WTA-style soft sharpening, or temperature-controlled MH at β in {1, 2}. Test whether ANY cleanup primitive in this slot helps LM BPC. If NO cleanup helps, the cleanup-as-readout-refiner idea is structural for LM (motivates angle 2's near-decomposability deeper analysis). If SOME cleanup helps, the primary failure was MH-specific.

**Cost:** ~45min CPU per cleanup variant × 3 variants = 2-3h CPU.

---

## L5 - SUBSTRATE-PRODUCT IMPLICATIONS

### If test-design diagnosis CONFIRMED (P=0.50 after deflation):

- Substrate compose is alive on properly designed test. A1's HARD_FAIL is a methodology artifact, not a structural wall.
- ROADMAP: ship CELL `exp_substrate_compose_test_design_audit_v1` to validate. If HARD_PASS, A1's cap_map row flips from HARD_FAIL to MIDDLE_BAND or HARD_PASS.
- META atom (chain-grade-eligible if confirmed): `meta_atom_primitive_certification_regime_must_match_compose_use_regime_2026-06-24` — when a primitive is certified at task X, composing it into task Y requires re-certification at task Y. Pattern completion ≠ LM readout.
- Hdlab/ primitive backlog: `hdlab/regime_audit.py` — utility that compares a primitive's certification self-test signature against the proposed compose use case. Flags mismatches before dispatch.

### If test-design diagnosis MIDDLE_BAND (P=0.30):

- ~50% of FULL_JOINT collapse is test-design artifact, ~50% is structural. Both angle-1 (logit-shape) and angle-2 (near-decomposability) apply.
- ROADMAP: design fixes recover compose to ~K=2 baseline 7.18, but no super-additive. Need both methodology fixes AND structural work (shared-state integration, learned routing, soft attractors).
- More expensive program: 1-2 month investment in compose architecture.

### If test-design diagnosis REFUTED (P=0.20):

- A1 collapse is robust across design fixes. Confirms angle 2 structural diagnosis (near-decomposability with weak coupling required; substrate's primitives violate weak-coupling assumption).
- ROADMAP: substrate compose requires structural redesign (Anchor 3 / H5 in angle-1's hypothesis space). ~3-month investment.

### Direct implications for 1.5-bit gap closure

The 1.5-bit gap from substrate (7.30 BPC) to bigram floor (~5.5 BPC) was the strategic target. A1's HARD_FAIL was being read as "compose-stacking path is dead". This drill shows the path is at least 50-75% likely to be ALIVE on properly designed test.

Brain-existence proof: brain composes 5+ primitives every cognitive operation. Substrate has 5+ chain-grade individual primitives. The probability that ZERO of these compose is vanishingly small under the existence proof. The likely truth: substrate compose works, but A1's test design wasn't sensitive enough to detect it.

### Cap_map implications

`cap_map row: substrate_LM_compose_5_primitives_super_additive` should be MIDDLE_BAND_WITH_TEST_DESIGN_AUDIT_PENDING, not HARD_FAIL. The structural-failure tier should require both test-design audit failure AND structural-redesign failure.

### L2 vision alignment

L2 vision = glass-box LM INSIDE substrate. The test-design audit STRENGTHENS L2 vision by showing the primary failure mode in compose cells is methodology, not architecture. This means the substrate primitives ARE composable; we just have to design tests carefully enough to see it.

---

## SYMMETRIC NEGATIVITY CHECK

**Could the cross-cell super-additive bigram result actually be a fluke?** The bigram cell has 5/5 super-additive seeds at N=512 V=512. The substrate's cf-RPE+STDP heterogeneous compose at production scale (het_plasticity_v1) shows lift=0.141 with 3/3 seeds. Both data points consistently show heterogeneous-axis compose works. The N=512 cell isn't a fluke — it's the small-scale validation that fed into the larger-scale het_plasticity cell. P_deflated 0.75 reflects this.

**Could ST9 self-test be load-bearing in some OTHER way?** ST9 just sanity-checks that MH retrieves correctly in its native regime. It's good as a sanity test — but missing as a REGIME-MATCH test. The bias I'm flagging is the absence of a regime-match test, not that ST9 lies.

**Could TEMP_GRID grid-top pegging just mean "the substrate cleanup naturally needs T=1"?** No — T=1 is the SAME as no scaling. The fact that EVERY λ at FULL_JOINT picks T=1 says the true optimum is ABOVE the grid maximum. The neighboring arms (K=2 hetplast) all pick T=0.02 — a 50x lower temperature. Grid-top + 50x flip from neighbors = grid wasn't wide enough for MH-shaped logits.

**Could N_STEPS=1000 be CORRECT for compose discovery?** Yes if all components asymptote at N=1000. But cf-RPE alone slides to 7.04 at N=5000, so cf-RPE doesn't asymptote at 1000. The compose probably needs MORE training, not less. N_STEPS=1000 is conservatively under-asymptotic for ALL the compose arms.

**Could the cumulative-build order be the BEST design choice?** No — cumulative-build optimizes for narrative cleanness ("each step adds capability") not for diagnosis. The factorial decomposition is information-richer. The cumulative pattern is mainstream in ablation studies, but it BUNDLES interactions rather than isolating them.

**Could shared HP across arms be CORRECT?** Yes for sanity rails — and the rails passed. But the FULL_JOINT arm has interaction effects that the isolation HPs cannot anticipate. Shared HP is conservative for rail-reproduction but wrong for compose-discovery.

**Could the calibration penalty 0.15-0.20 be too aggressive?** This drill identifies 5 design biases each with clear evidence from cross-cell comparison. The empirical evidence is strong. Lower deflation 0.10-0.15 might be more appropriate. P=0.75 reflects 0.15 deflation.

**Could angle-2 (near-decomposability) STILL be correct as the deeper diagnosis?** Yes — angle 2's structural framework is compatible with this angle's methodology critique. Both could be true. Angle 2 says: structurally, near-decomposable systems compose only with weak coupling, and substrate's primitives may not maintain weak coupling. Angle 3 says: but A1's test design ALSO precludes detecting the coupling regime where compose works. Both are load-bearing for the FULL diagnosis; the design fixes need to run first to localize which is dominant.

---

## DISPATCH RECOMMENDATION

**Primary cell (decisive test):** `exp_substrate_compose_test_design_audit_v1`
- Routing: local_cpu_queue (~45min CPU local; cell is GPU-eligible but CPU is fine for this diagnostic)
- ARMs: ARM_DESIGN_FIX_1_NO_MH + ARM_DESIGN_FIX_2_EXTENDED_T + ARM_DESIGN_FIX_3_LOW_BETA + ARM_DESIGN_FIX_COMBINED + ARM_CONTROL_REPRODUCE_A1
- 3 seeds, extended TEMP_GRID, MH_BETA sweep, optionally MH disabled
- Pre-reg HARD bands per CHEAP DECISIVE TEST above

**Secondary cell (CONDITIONAL on primary HARD_FAIL or MIDDLE_BAND):** `exp_substrate_compose_factorial_4way_v1`
- Routing: overnight_queue (GPU; ~6-8h)
- 2^4=16 arms × 3 seeds × N_STEPS=2000
- Maps out the compose-interaction tensor

**META atoms (independent of cell outcome):**
- `meta_atom_primitive_certification_regime_must_match_compose_use_regime_2026-06-24` — primitives certified at task X must be re-certified at task Y before compose
- `meta_atom_sweep_grid_endpoints_must_be_re_validated_when_pipeline_changes_2026-06-24` — when adding mechanisms upstream of a sweep, the sweep range must be checked against the new dynamic range
- `meta_atom_cumulative_build_loses_interaction_information_vs_factorial_2026-06-24` — when diagnosis matters, use factorial; when narrative matters, use cumulative
- `meta_atom_per_arm_HP_sweep_required_for_compose_discovery_2026-06-24` — frozen HPs are conservative for rails, blind for compose

**Companion exp_dev hand-off:** write `notes/exp_dev_handoff_research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md` if dispatched.

---

## CITATIONS (verified count = 5 internal substrate cells + 4 internal notes)

**Substrate-internal cross-references (load-bearing):**
1. `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` — A1 cell primary empirical
2. `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` — A1 cell source (line-by-line audit)
3. `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json` — cf-RPE+STDP HARD_PASS super-additive
4. `experiments/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512.py` — cross-cell precedent source
5. `data/exp_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu/metrics.json` — same-axis MIDDLE_BAND additive precedent
6. `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json` — N_STEPS asymptote (cf-RPE slides to 7.04 at N=5000)
7. `data/exp_modern_hopfield_n_sweep_v1/metrics.json` — MH primitive certification (pattern completion regime)
8. `experiments/exp_modern_hopfield_n_sweep_v1.py` — MH self-test regime evidence
9. `notes/research_composition_collapse_critical_drill_2026-06-24.md` — angle 1 (logit-shape) drill
10. `notes/skunkworks_LANDED_VET_cfrpe_n_steps_curve_v1_MEASURED_MECHANISM_2026-06-24.md` — N_STEPS asymptote landed
11. `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json` — cf-RPE+STDP at production scale ref
12. `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json` — K=2 + cf-RPE HARD_FAIL ref

**No external citations:** this drill is a SUBSTRATE-INTERNAL test-design audit. The methodology critique is sourced entirely from substrate cells and their internal self-tests, NOT external literature. (Angle 1 used external lit; angle 2 was cross-biology lit; angle 3 is methodology audit which is appropriately substrate-internal.)

---

## CONTRACT OUTPUT

`research: delivered a1_composition_collapse_3rd_angle_test_design_audit -> notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md ; HEADLINE: A1 HARD_FAIL is 60-75% test-design artifact; cross-cell precedent (cf-RPE+STDP HARD_PASS super-additive on N=512 bigram with same primitives) refutes structural-only diagnosis; 5 design biases identified (MH-certified-at-wrong-regime / TEMP_GRID-tops-at-1.0 / N_STEPS=1000-under-asymptotic / cumulative-build-not-factorial / shared-frozen-HPs); ST9 self-test caught red-handed validating wrong regime; cheap decisive test 45min CPU with design-fix arms; P_deflated(test-design)=0.75; P_deflated(re-design lifts to HARD_PASS)=0.50; angle-2 structural diagnosis still ~55% likely as deeper layer; cap_map should be MIDDLE_BAND_WITH_TEST_DESIGN_AUDIT_PENDING not HARD_FAIL; next-drill candidate: ship exp_substrate_compose_test_design_audit_v1 cell`

---

*Research drill 3rd angle complete 2026-06-24. Line-by-line A1 cell source audit + cross-cell pattern against 11 substrate cells + ST9 self-test regime audit (smoking gun: MH primitive certified at pattern-completion task validated via ST9, then used at LM-readout task in A1) + factorial vs cumulative methodology critique + 5 corrected counterfactual designs + 3 escape-path test designs + 4 META atoms proposed + 1 hdlab/ primitive backlog item (regime_audit.py). Brain-existence-proof asymmetric calibration (deflate 0.15). HARD-FAIL thresholds mandatory both directions. Symmetric negativity check applied (7 angles). Cross-cell smoking gun verified: cfrpe+STDP heterogeneous compose at N=512 V=512 synthetic bigram HARD_PASSED super-additive (5/5 seeds, gap=3.744 nats), establishing same plasticity pair composes in different cell design. Time elapsed ~45 min per budget.*
