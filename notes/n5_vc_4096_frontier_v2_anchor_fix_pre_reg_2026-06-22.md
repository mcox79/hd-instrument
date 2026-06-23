# Pre-reg: n5_vc_4096_frontier_v2_anchor_fix (anchor-fix revival of v1)

**Date:** 2026-06-22
**Cell:** `experiments/exp_n5_vc_4096_frontier_v2_anchor_fix.py`
**Anchor name:** `n5_vc_4096_frontier_v2_anchor_fix`
**Queue:** `remote_cpu_queue` (residuals_per_token.npz lives on marsh@home)
**Author:** Exp-Dev (anchor-fix revival cycle per route-negatives-to-research)
**Source pre-reg trigger:** Revival of n5_vc_4096_frontier_v1 HARD_FAIL 2026-06-22 07:03Z (wall=5530s). v1 hit ANCHOR-MISMATCH at V_C=1024/N=16384 (measured sub_bpc=5.084 vs N2 baseline's 4.959, diff=0.125 > 0.10 tolerance). v1 headline (V_C=4096 best=5.680) is INVALIDATED because the baseline-reproduction CAN-FAIL gate failed.

---

## Why v1 failed (root-cause audit)

Cross-checking v1 vs `exp_n2_capacity_scaling_v1.py` (the source of the 4.959 anchor) reveals TWO methodological divergences that compound:

### Cause 1: codebook RNG seed formula diverged

- v1: `rng2 = default_rng(seed + 1000 + vc*31 + n_dim*17)`
  - at (seed=7, vc=1024, n_dim=16384): seed_val = 7 + 1000 + 31744 + 278528 = **310279**
- N2: `rng2 = default_rng(seed + 1000 + n_dim_idx*100)`
  - at (seed=7, n_dim_idx=2 i.e. n=16384): seed_val = 7 + 1000 + 200 = **1207**

Two completely different RNGs produce two completely different sparse codebooks C. Same downstream pipeline, different W matrix, different recall. NON-COMMUTING with N2.

### Cause 2: VQ assignment method diverged

- v1: L2-normalize `km.cluster_centers_`, then `np.argmax(residuals_L2norm @ centers_L2norm.T)` (cosine-sim argmax).
- N2: `km.predict(residuals_L2norm)` — sklearn euclidean argmin against RAW (un-normalized) `cluster_centers_`.

Sklearn's `km.predict` is not equivalent to cosine-sim argmax post-L2-norm. They accumulate disagreement across 100k tokens, shifting cids assignment → shifts D writes and W transitions → shifts sub_bpc.

### Evidence from the v1 results

Notably v1's V_C=1024/N=**32768** arm measured sub_bpc=4.954 (matches N2's 4.959 nearly exactly). That suggests at higher N the codebook-RNG divergence partially washes out, but at N=16384 the two error sources combine destructively to produce the 0.125 drift. Both root causes must be fixed for byte-level reproduction.

---

## Three changes vs v1

1. **Codebook RNG**: `codebook_rng_seed(seed, n_dim_idx, vc)` returns N2's formula `seed + 1000 + n_dim_idx*100` for V_C=1024 (byte-for-byte). For V_C>1024, adds +50000 offset (disjoint stream so it cannot collide with V_C=1024 codebooks at any (seed, n_dim_idx)). Verified by selftest T13.

2. **VQ assignment**: `n2_baseline_assign_cids(km, doc_res_list)` calls `km.predict(L2_normalized_residuals)` directly. No manual L2-normalization of centers, no cosine-sim argmax. Matches N2's `assign_cids()` at `exp_n2_capacity_scaling_v1.py:636-639` verbatim. CONFIG_VERSION marker `ASSIGN=km_predict_n2_baseline`.

3. **CAN-FAIL pre-flight gate** (Fix #16 explicit discriminator): in `run_seed`, V_C=1024/N=16384 runs FIRST. If `sub_bpc ∉ [4.939, 4.979]` (N2 4.959 ± 0.02), the cell SKIPS the V_C=4096 sweep for that seed and `verdict()` emits `HARD_FAIL_HARNESS_DRIFT`. Tolerance is +/-0.02 (tightened from v1's +/-0.10), enforced symmetrically. Saves ~90 min of compute when the harness is drifted.

ANCHOR_NAME = `n5_vc_4096_frontier_v2_anchor_fix`. CONFIG_VERSION contains the literal substring `anchor-fix-N2-baseline-reproduction-gate-tol_0.02`.

n_seeds = 3 (same as v1). V_C_GRID = [1024, 4096] (same). N_GRID = [16384, 32768] (same). K=1 (same). F_SPARSE=0.006 (same). All other knobs identical.

---

## Fixed config (verbatim from v1 except anchor-fix items above)

- K = 1
- F_SPARSE = 0.006
- TRAIN_FRAC = 0.8
- LR_DECODE = 1.0
- LAM_BACKOFF = 0.1
- INTERP_B = 0.3
- seeds = [7, 17, 23] (full); [1] (smoke)
- MAX_DOCS = 100000 (full); 200 (smoke)

## V_C × N_DIM sweep

`VC_GRID = [1024, 4096]` × `N_GRID = [16384, 32768]` = 4 arms per seed.

- (V_C=1024, N=16384): ANCHOR PRE-GATE arm (load-bearing harness check; ABORT on drift).
- (V_C=1024, N=32768): N_DIM-alone control arm.
- (V_C=4096, N=16384): V_C-alone load-bearing FRONTIER arm.
- (V_C=4096, N=32768): joint V_C + N_DIM arm.

km fit is cached PER V_C across the N_DIM sweep (V_C=1024 km is fit ONCE, shared by the anchor + N=32768 arms; V_C=4096 km is fit ONCE, shared by both N=16384 and N=32768 frontier arms). Mirrors N2's per-VC fit-once pattern.

---

## Pre-registered bands (HARD; SYMMETRIC verify-both-directions per negativity-bias rule)

### ANCHOR_PRE-GATE (load-bearing harness check)

- `V_C=1024/N=16384` sub_bpc ∈ [4.939, 4.979] (N2 4.959 ± 0.02) for ALL 3 seeds.
- If ANY seed misses → `HARD_FAIL_HARNESS_DRIFT` (cell aborts that seed's V_C=4096 sweep; verdict short-circuits).
- This is a STRICT tightening vs v1's ±0.10 tolerance.

### HARD_PASS (chain-grade, ALL of)

- ANCHOR_PRE-GATE PASSED on all seeds.
- V_C=4096 best sub_bpc ≤ 4.859 (N2 4.959 − 0.10 margin: clear lift over baseline at frontier).
- cv across 3 seeds ≤ 0.05 for the passing config.
- NOT saturated (alpha < 1.0).
- substrate-only-decode (zero LLM calls; counter asserted = 0).
- direction-correct: V_C=4096 strictly better than V_C=1024 at SAME N_DIM (tolerance 0.05).
- run_mode = "full" (Fix #5 pre-flight guard).

### HARD_PASS_PLUS

- substrate_bpc < bigram_bpc (3.844) at some V_C=4096 arm.

### MIDDLE_BAND

- ANCHOR_PRE-GATE PASSED.
- V_C=4096 best sub_bpc in (4.859, 4.959] — partial lift but doesn't clear HARD_PASS margin.

### HARD_FAIL (any)

- ANCHOR_PRE-GATE FAILED on any seed → `HARD_FAIL_HARNESS_DRIFT`.
- OR V_C=4096 best sub_bpc ≥ 4.959 (no lift over N2 baseline → V_C scaling alone doesn't help; route to k-WTA + V_C joint composition).
- OR V_C=4096 WORSE than V_C=1024 at SAME N_DIM (wrong-direction).
- OR substrate-only-decode gate violated (LLM call counter > 0).
- OR run_mode != "full" (Fix #5 stale-smoke catch).

---

## Instrumentation (REQUIRED, per Skunkworks chain-grade spec)

- per_unit BPC per (V_C × N_DIM × seed); cv ≤ 0.05 (chain-grade per_unit blocker).
- `assignment_mode = "km_predict_n2_baseline"` per per_unit row.
- `codebook_rng_seed` per per_unit row (audit trail for byte-level reproduction).
- `pregate_arm` flag on the V_C=1024/N=16384 arm rows so consumers can identify it.
- `anchor_pregate_status` + `anchor_pregate_sub_bpc` per seed metrics.
- `zero_llm_calls_at_inference` LOGGED.
- `ceiling_bpc` + `concept_top1` per config.
- `corpus_provenance_real=True`; `allow_synthetic=False`.
- run_mode default = "full"; CONFIG_VERSION captures VC_GRID, N_GRID, seeds, ASSIGN marker, anchor-fix marker, and tolerance.
- `km_wall_s` recorded per (seed, V_C).

---

## Wall projection / timeout

v1 measured walls (full, 3 seeds):
- V_C=1024/N=16384: ~109s per seed (anchor)
- V_C=1024/N=32768: ~324s per seed
- V_C=4096/N=16384: ~136s per seed
- V_C=4096/N=32768: ~382s per seed
- km fit V_C=1024: ~154s (shared); V_C=4096: ~729s (shared)
- Per seed total ≈ 154 + 729 + 109 + 324 + 136 + 382 ≈ 1834s ≈ 31min
- Total 3 seeds = 92 min (matches v1's 5530s)

v2 anchor pre-gate runs first (the V_C=1024/N=16384 arm + V_C=1024 km fit), so wall projection unchanged. PROT-021 `_seed_checkpoint` is wired (resume-safe). FAIL_DRIFT skip saves remaining ~70min/seed if drift happens.

**Timeout:** 10800s (3hr). Generous against the ~90min projection; allows one seed to over-run by 2x without dropping it. PROT-019 not applicable (no `_n<N>` suffix in anchor name). PROT-021 `_seed_checkpoint` imported.

---

## Falsifiable predictions

1. **ANCHOR_PRE-GATE passes on all 3 seeds:** P ≈ 0.90. The combination of N2-formula codebook RNG + km.predict assignment is sufficient to reproduce N2's pipeline byte-for-byte (modulo numpy/sklearn version-induced numerical drift). The 10% caveat: remote sklearn version may differ from N2's; if so the deterministic km fit can drift slightly and produce sub_bpc ~4.97 or ~4.94 (still in band).

2. **V_C=4096 lifts over N2 by ≥0.10 (HARD_PASS):** P ≈ 0.25. The v1 evidence showed V_C=4096 was actually WORSE (sub=5.680 vs N2 4.959, delta=-0.721). That said, v1's bad anchor reproduction means the V_C=4096 measurement is also suspect — re-running with correct VQ pipeline could shift it either direction. Brain-drill prediction is V_C scaling needs k-scaling at biological sparsity; V_C-alone may still under-perform.

3. **V_C=4096 direction-correct (better than V_C=1024 at same N):** P ≈ 0.45. v1 showed V_C=4096 was strictly WORSE direction-wise (sub=5.753 > V_C=1024's 5.084 at N=16384). With the fixed VQ pipeline this may flip, but the brain-drill cautions us that V_C=4096 + K=1 may saturate concept coverage thinly (each concept covers fewer tokens → ceiling lowers but recall noise increases). True effect direction is the open question this cell answers.

---

## Composability

- If HARD_PASS or MIDDLE_BAND: compose with n4 k-WTA (`V_C=4096 + k-WTA at k~200`) is the joint follow-on (brain-drill biological-sparsity optimum).
- If HARD_FAIL_HARNESS_DRIFT: deeper harness investigation needed (numpy/sklearn version mismatch on remote? deterministic km fit drift?). Route to Testbed integration-check.
- If HARD_FAIL (V_C=4096 doesn't lift): route to n4+V_C joint REVIVAL drill — V_C-needs-k brain-drill caveat becomes load-bearing.

---

## Fixes applied (Fix #1-#28 discipline)

- Fix #4: NO background bash watchers; Director polls.
- Fix #5: pre-flight run_mode check inside verdict().
- Fix #6: zero-D-overlap fallback in batched_token_logprob.
- Fix #10: this note filename is `<topic>_<date>.md`, no `to_<role>` prefix.
- Fix #11: spawn template used for this dispatch cycle.
- Fix #14: cell + prereg committed BEFORE remote dispatch (commit-first; uncommitted laptop notes invisible to autonomous pipeline).
- Fix #16: explicit discriminator — ANCHOR_PRE-GATE is the load-bearing harness check; HARD_FAIL_HARNESS_DRIFT is a distinct verdict from V_C science failure.
- Fix #18: anchor-reproduction strict — tolerance tightened to ±0.02 vs v1's ±0.10.
- Fix #26: predispatch_check.py reports HOLD due to v1 HARD_FAIL; rationale to PROCEED is documented here (anchor-fix is the targeted revival per route-negatives-to-research discipline; the ±0.02 pre-gate + km.predict + N2 RNG formula are specifically engineered to fix the v1 failure mode).
- ASCII-only / 13 selftest tests / per-unit blocker / commit-before-remote-dispatch.

— Exp-Dev (anchor-fix revival cycle), 2026-06-22
