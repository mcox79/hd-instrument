# Pre-reg: n4_kwta_soft_decode_v1 (top-k soft kWTA-VQ at write+read of D)

**Date:** 2026-06-22
**Cell:** `experiments/exp_n4_kwta_soft_decode_v1.py`
**Anchor name:** `n4_kwta_soft_decode_v1`
**Queue:** `remote_cpu_queue` (residuals_per_token.npz lives on marsh@home)
**Author:** Exp-Dev (cell-author cycle)
**Source pre-reg:** `notes/research_brain_within_concept_floor_5x_drill_2026-06-22.md` (Research 5x novel-synthesis drill)

---

## Mechanism (novel synthesis, brain-drill 3.1)

Top-k soft kWTA-VQ at write AND read of decode matrix D. Replace hard one-hot `km.predict()` with top-k softmax assignment:

- WRITE: for each residual r, find top-k nearest centroids, softmax-weight by `-||r-c||^2 / tau`, accumulate `D[c_i, token] += w_i * LR_DECODE` for each of the k centroids.
- READ: same top-k pooling at decode (Phase-1 keeps READ as hard-pred-c-from-recall + lookup D row, since D already carries the soft-write effect; Phase-2 tau-sweep adds query-time pooling).

Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM forward calls; AST-verified counter at 0).

Biological motivation: cerebellum granule cells (Marr/Albus/Litwin-Kumar 2017), mushroom body Kenyon cells (Modi 2020), dentate gyrus (Cayco-Gajic 2019) converge on coding-level f ≈ 0.05-0.10. Substrate runs at f = 1/V_C ≈ 0.001, 50-100x too sparse. The k-sweep tests MULTIPLICITY directly.

## Fixed config (matches N2/n3 for direct comparison)

- V_C = 1024
- N_DIM = 16384
- K = 1 (substrate depth)
- F_SPARSE = 0.006
- TAU = 1.0 (softmax temperature; Phase-1 default; tau-sweep is Phase-2 conditional)
- seeds = [7, 17, 23] (full); [1] (smoke)
- MAX_DOCS = 100000 (full); 200 (smoke)
- TRAIN_FRAC = 0.8
- LAM_BACKOFF = 0.1
- INTERP_B = 0.3

## Phase-1 K_GRID

`K_GRID = [1, 8, 32]`

- k=1: hard one-hot anchor (must reproduce N2 ceiling_bpc = 2.049 within 0.05 bits).
- k=8: f_eff = 0.008 (multiplicity-direction test below biological optimum).
- k=32: f_eff = 0.031 (approaching biological optimum at V_C=1024).

Phase-2 (conditional on Phase-1 ceiling drop >= 0.10 at any k > 1): add {4, 16, 64, 128} for resolution + tau ∈ {0.5, 2.0} at best-k.

Brain-drill predicts optimum k* ≈ 50-100 (f* ≈ 0.05-0.10), bracketed by Phase-1's k=8 (too-sparse) and k=32 (mid). If Phase-1 shows monotone-improving k=1 → k=32, Phase-2 ships {64, 128} to localize the optimum.

## Pre-registered bands (HARD)

**HARD_PASS (chain-grade, ALL of):**
- some k > 1 has ceiling_bpc <= 1.75 (>= 0.30 bits drop vs N2's 2.049)
- same k has substrate_bpc <= 4.75 (>= 0.21 bits drop vs N2's 4.959)
- cv across 3 seeds <= 0.05 for the passing config
- not saturated (alpha < 1.0; pre-determined OK at N=16384 alpha ~ 0.5)
- substrate-only-decode (zero LLM calls; counter asserted = 0)
- best_k != 1 (mechanism IS multiplicity; k=1-best = noise effect)
- run_mode = "full" (Fix #5 pre-flight guard against stale-smoke metric)

**HARD_PASS_PLUS:** substrate_bpc < bigram_bpc (3.844) at some k -- the first bigram-beating substrate LM (super-pass).

**MIDDLE_BAND (partial mechanism, EITHER of):**
- ceiling_bpc drops 0.10-0.30 bits vs k=1 at some k > 1
- substrate_bpc improves >= 0.10 bits but does not clear HARD_PASS bar

**HARD_FAIL (ALL conditions checked):**
- best ceiling change < 0.05 bits across all k > 1 → biological-sparsity hypothesis falsified at V_C=1024 → route to n5 hippocampal episodic + Path A V_C scaling (brain-drill Prediction 5).
- OR anchor mismatch (k=1 ceiling differs from N2's 2.049 by > 0.05 at full).
- OR substrate-only gate violated (LLM forward call counter > 0).
- OR wrong-direction (ceiling_delta < 0 = soft averaging destructive at this V_C). pre-reg-direction-must-match-intent (Skunkworks n3 SimVQ catch).
- OR run_mode != "full" (Fix #5: stale-smoke leak suspected; rerun full).

## Bracket sanity (REQUIRED in pre-reg, per brain-drill Prediction 4)

- **k=1 bracket:** must reproduce N2 anchor (2.049 ± 0.05). Selftest T10 + verdict ANCHOR-OK check.
- **k=V_C=1024 bracket (uniform pooling, Prediction 4 NULLABILITY):** not in Phase-1 K_GRID since the cost is one full unit; Phase-1's k=32 already shows direction. If Phase-1 lands HARD_PASS, Phase-2 includes k=V_C as the SANITY arm to verify near-unigram-BPC degradation.

## Falsifiable predictions (brain-drill, 5 total)

1. **Primary:** kWTA at k* lowers ceiling_bpc by >= 0.30 bits. P(HARD_PASS) ≈ 0.40 (novel-synthesis cap, deflated).
2. **Secondary:** optimum-k in [32, 128] (f ≈ 0.03-0.125). P ≈ 0.35. Phase-1 partial probe (k=32) tests direction; Phase-2 localizes.
3. **Conditional:** depth K=2 post-floor-drop surfaces +0.05 bits depth_token_gain. P ≈ 0.45. Free piggyback (n4 + K=2 follow-on cell).
4. **Nullability bracket:** k=V_C ~ uniform-BPC. Phase-2 sanity arm.
5. **Revival route on HARD_FAIL:** n5_hippocampal_episodic_v1 + Path A V_C scaling.

## Instrumentation (Skunkworks chain-grade structural blockers; all 4 baked)

1. `per_unit` per (seed, k_value) row in per_seed; recompute-off-per_unit ready.
2. `cv <= 0.05` computed across seeds for each k in verdict.
3. `zero_llm_calls_at_inference = True` LOGGED in metrics (asserted == 0 at end).
4. VQ-floor decomposition: ceiling_bpc separate per k.

## Version markers (BPC-affecting; AST-verifiable)

`assignment_mode = "top_k_soft"`, `k_value` per row, `tau`, `effective_coding_level = k / V_C`. CONFIG_VERSION includes `K_GRID`, `TAU`, `ASSIGN=top_k_soft`.

## Pre-flight fixes baked in

- **Fix #5 run_mode preflight in verdict():** HARD_FAIL if mixed/partial run_modes (stale-smoke leak guard); smoke-only run emits soft `[SMOKE: non-binding]` tag.
- **Fix #6 zero-D-overlap fallback in batched_token_logprob:** returns uniform when concept code has zero D-overlap; selftest T7 verifies.
- **pre-reg-direction-must-match-intent (Skunkworks n3 catch):** negative ceiling_delta -> HARD_FAIL, not MIDDLE_BAND.
- **Substrate-only-decode gate verified by code-trace:** no transformers/torch import; counter assertion at end of main sweep.

## Disposition path

- HARD_PASS at Phase-1 -> Skunkworks SCHEMA-VET + landed-VET cycle; Phase-2 ships {4, 16, 64, 128} + tau ∈ {0.5, 2.0} at best-k; downstream composes with K=2 depth + MKN + Path A.
- MIDDLE_BAND -> route to Research for refinement options (tau sweep, k localization).
- HARD_FAIL -> route to Research for 2x revival drill: n5 hippocampal episodic + investigate concept-prediction-layer-not-decode.

## Smoke dispatch + commit plan

1. AST-check + self-test PASS locally (DONE; 13/13 selftests).
2. Commit cell + pre-reg path-scoped.
3. Smoke dispatch: `remote_cpu_queue`, RUN_MODE=smoke (1 seed × {1,8,32} × small config).
4. After smoke lands: REMOTE VERIFY metrics path + cell-spec match.
5. Full dispatch: 3 seeds × {1,8,32} × full config (~3.5 hr per brain-drill).

## Honest surprises during cell-design

- **Soft-pool re-norm:** softmax already sums to 1 → total mass written per token = `LR_DECODE * sum(w) = LR_DECODE`, unchanged from k=1. Decode preserves total mass naturally; no extra re-norm needed.
- **Hebbian-compatibility:** the multi-row write is just multiple Hebbian co-activations weighted by similarity. Forward-only; no backprop. PASS.
- **Read-side pooling choice:** Phase-1 keeps READ as hard-pred-c-from-recall (the soft-write effect is ALREADY in D from training). Adding query-time top-k pooling at READ adds a second softness axis that would conflate effects; Phase-2 tau-sweep at best-k can probe that.
- **k_means centers L2-normalize:** added `centers /= norm` step after sklearn fit, to match the L2-normalized input convention. Sklearn's MiniBatchKMeans does NOT normalize centroids by default.
- **k=V_C bracket:** would cost a full additional unit (3 seeds at full = ~1 hour extra). Phase-1 omits; Phase-2 conditional adds.

— Exp-Dev cell-author, 2026-06-22
