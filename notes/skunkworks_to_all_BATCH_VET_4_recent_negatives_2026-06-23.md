# Skunkworks BATCH landed-VET — 4 recent negatives (2026-06-23)

Author: Skunkworks (cert-owner; broad-verify MINUS dispatch)
Scope: aggressive verify-OFF-DATA on 4 recent landings flagged by Director
Discipline: A5 non-destructive / read-only on substrate / Fix #28 per-arm metrics direct read
Routing: cert-owner verdicts — Research/Orchestrator dispatches any rescues per recommendations below.

---

## TARGET 1 — `substrate_multi_iteration_cleanup_LM_v1` (smoke HARD_FAIL)

**Verdict: METHODOLOGY_CONFOUND (small-N + encoder-mismatch) — DO NOT promote to genuine null until full N=8192 run lands.**

### Evidence (file-cited)

- Smoke metrics: `data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json` (mode=smoke, N_DIM=512, V=300, N_TRAIN=2000, 1 seed).
- Per-arm reads:
  - ARM_BASELINE_NO_CLEANUP bpc=4.9948 (BEATS unigram=5.0133 by 0.018 bits — substrate IS doing work)
  - ARM_SINGLE_STEP_CLEANUP bpc=5.0364 (WORSE than baseline by 0.042; worse than unigram by 0.023)
  - ARM_3_ITER, ARM_10_ITER bpc=5.0364 (identical to single-step; both converge at iter 3)
- Cell source: `experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py`
  - Line 280: `updated = np.sign(updated)` — discrete bipolar attractor.
  - Line 271-283: each iteration is `sign(W @ states)` then L2-normalize.
- Smoke uses char_trigram_encode (line 217-228) which produces ±1 vectors before L2-norm. The first iteration `sign(W @ E)` collapses continuous Hebbian signal to bipolar — that's what kills it. The NO-CLEANUP arm just keeps the continuous L2-normalized prediction.

### Why this is METHODOLOGY_CONFOUND not GENUINE_FAILURE

1. **The smoke shows the OPPOSITE of what was tested.** Cleanup HURTS at this scale (not "doesn't help"). NO-CLEANUP beats both unigram and all cleanup arms. That's a signal that the test design loses signal under sign-collapse, not that brain-CA3 attractor dynamics are absent.
2. **Convergence at iter 3 means the bipolar attractor is shallow.** ARM_10_ITER reports `mean_iters=3.0`, which equals ARM_3_ITER. Both reach the same fixed point. This is consistent with low-V (300 words) bipolar Hopfield: very few attractors, fast convergence to the wrong basin.
3. **N=512 / V=300 / N_TRAIN=2000 is FAR below the regime where multi-iter cleanup would matter.** Brain CA3 capacity arguments require sparse-coded N>>K patterns; smoke is in saturated regime.
4. **PENDING full run at N=8192** (per task): the full result is the load-bearing evidence. Smoke is preflight, not the real test.

### Rescue dispatch recommended

NO — wait for the full N=8192 run to land. THEN run landed-VET on full. If full ALSO shows HARD_FAIL/NULL, additional diagnostics needed (see #3 below). If full shows MIDDLE_BAND/HARD_PASS, smoke result is just smoke-scale artifact.

### Tier-call

- Smoke: classify as `INSTRUMENTATION_SMOKE_BELOW_REGIME` (don't atomize as substrate finding).
- Full: pending. Atomize when landed.

---

## TARGET 2 — `substrate_serotonin_mode_switch_bank_select_LM_v1` (HARD_FAIL elapsed_s=0.0)

**Verdict: GENUINE_FAILURE (mechanism truly doesn't help) + ELAPSED_S=0.0 IS A COSMETIC METRICS-FIELD BUG, NOT A CELL ERROR.**

### Evidence (file-cited)

- Metrics: `data/exp_substrate_serotonin_mode_switch_bank_select_LM_v1/metrics.json` (run_mode=full, N_DIM=8192, 3 seeds, real wall time ran).
- Per-arm reads (this is what matters per Fix #28, NOT the elapsed_s field):
  - ARM_UNIGRAM bpc=7.6838 top1=0.269
  - ARM_SINGLE_BANK bpc=7.2268 top1=0.2907 (LIFTS 0.46 bits vs unigram — substrate doing real work, close to fair_harness 7.3065)
  - ARM_4_BANK_RANDOM_SELECT bpc=7.2426 top1=0.284
  - ARM_4_BANK_FEATURE_GATED_SELECT bpc=7.2291 top1=0.294 (lift_vs_single = -0.0022)
- cv across all 3 arms ~0.0003 (very tight, 3 seeds).
- Cell source: `experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py`
  - Self-test (line 475-554) PASSED at module-scope before main run.
  - Lines 247-306: `build_gate_W_np` — Hebbian gate trained via softmax over per-bank utility = cosine(tgt_slice, W_b @ src_slice). Implementation is correct.
  - Lines 357-391: feature-gated logits select via `argmax(softmax(src_full @ gate_W))`. Hard selection per token.
- **elapsed_s=0.0 is the summary field, not the cell-error indicator.** The full run obviously executed (3 seeds × 4 arms × N=8192 × N_TRAIN=100k all ran; the `verdict_msg` reports real BPCs to 4 decimals from real computation). The 0.0 is just a missing `time.time() - _T_START` capture in the synthesizer wrapper.

### Why this is GENUINE_FAILURE

1. Per-arm BPCs ARE valid and computed. Feature-gated achieves bpc=7.2291. Single-bank achieves bpc=7.2268. Difference of 0.0022 bits is well below the pre-reg HARD_FAIL threshold of 0.03 AND below MIDDLE_BAND threshold.
2. Substrate IS learning (single-bank lifts 0.46 bits vs unigram, close to fair_harness 7.3065 chain-grade). The mechanism just doesn't help.
3. Feature-gated beats RANDOM_SELECT by 0.0135 bits — gate IS doing SOME work (it's not equivalent to random), just not enough to beat the parameter-budget-matched single-bank baseline.
4. By-construction-saturation argument: 4 banks × N_DIM_BANK=2048 = 8192 total params, same as single-bank. The gating overhead doesn't pay off because softmax-argmax over 4 banks at the LM scale costs more capacity than it saves.
5. cv is 0.0003 — very robust signal across 3 seeds.

### Rescue dispatch recommended

OPTIONAL — single follow-up: rerun with larger N_DIM_BANK (e.g., N_DIM=16384 single vs 4×4096 banks) to test if param-budget-up regime changes the picture. Brain-prior says serotonin SELECTS compartments only after enough compartments exist to differentiate; 4 may be too few. This would be a NEW cell, not a rescue of the existing one.

ALSO recommend: open a small Fix #29 for the metrics_synthesizer to set `elapsed_s = time.time() - _T_START` always (not just on success path).

### Tier-call

- Atomize as `MEASURED_MECHANISM_NULL` (not chain-grade since it's a null result).
- Brain-prior P=0.45 was warranted; mechanism didn't lift.
- Cert_status: `landed_VET_PASS_genuine_negative`.

---

## TARGET 3 — `substrate_per_context_decode_temperature_LM_v1` (HARD_FAIL -0.32 below unigram)

**Verdict: IMPLEMENTATION_BUG — ENCODER MISMATCH vs claimed baseline; ARM_GLOBAL_T collapses to unigram (fails its own self-test); per-context arms then WORSE than unigram.**

### Evidence (file-cited)

- Metrics: `data/exp_substrate_per_context_decode_temperature_LM_v1/metrics.json` (run_mode=full, N_DIM=8192, 3 seeds, wall ~40 min, REAL computation).
- Per-arm reads:
  - ARM_UNIGRAM bpc=7.7378 top1=0.2171
  - ARM_GLOBAL_T bpc=7.7378 top1=0.2171 — **IDENTICAL TO UNIGRAM EXACTLY** (best_T=0.01, best_lam=0.0 — the joint sweep PICKED pure unigram because no T beats it).
  - ARM_PER_CONTEXT_T_ENTROPY bpc=8.1118 (-0.374 vs global)
  - ARM_PER_CONTEXT_T_MARGIN bpc=8.0544 (-0.317 vs global)
- Cell source: `experiments/exp_substrate_per_context_decode_temperature_LM_v1.py`
  - Line 149-164: `char_trigram_encode_np` is a **HASH-INDEX-BUCKET** encoder (one bucket per trigram, accumulator), NOT a bipolar-HV-sum encoder like fair_harness.
  - Line 504: `E = sparsify_bipolar_np(E_base, f=SPARSE_F)` — sparsifies the wrong-shaped base.
  - Cell DOCSTRING (line 33) claims: "ARM_GLOBAL_T reproduces fair_harness sparse-bipolar baseline (BPC=7.3065)". Line 543-547 has a WARN gate for deviation > 0.05 — but the WARN fires for 0.43 bits deviation and the cell PROCEEDS anyway.
- Comparison to fair_harness encoder (`experiments/exp_fair_harness_substrate_as_lm_v1.py` line 184-194 + line 254-274): fair_harness uses `word2vec-google-news-300` via gensim, projected via Gaussian, then sparsified. Char-trigram is ONLY the OOV fallback.

### Why this is IMPLEMENTATION_BUG (not GENUINE_FAILURE)

1. **The cell's ARM_GLOBAL_T self-test bar (7.3065 within 0.05) FAILS BY 0.43 BITS.** The cell warns but doesn't halt. This is the load-bearing baseline; if it can't reproduce fair_harness, the whole experiment is moot.
2. **Why does ARM_GLOBAL_T collapse to unigram?** With hash-bucket-only char-trigram encoder, the cosine logits are too NOISY for any temperature to make them useful. The joint sweep correctly finds that the cleanest predictor is lambda=0.0 (pure unigram weight) at lowest T, which DEGENERATES to argmax-from-unigram = unigram BPC.
3. **Per-context arms are then WORSE because** lambda is FIXED at 0.3 (line 110: `LAMBDA_PER_CONTEXT = 0.3`) — they can't escape via the lambda→0 unigram fallback the global arm took. So the per-context arms get penalized 0.3-0.4 bits for being forced to MIX in 30% substrate signal that is noisier than unigram.
4. The diagnostic cell `substrate_per_context_T_diagnostic_v1` (smoke landed) CONFIRMS this: at smoke scale, ARM_PER_CONTEXT_T_DENSE bpc=5.162 = ARM_UNIGRAM bpc=5.162 exactly (degenerate to unigram via lambda=0.0). ARM_GLOBAL_T_DENSE lifts 0.056 bits. The mechanism is INVISIBLE under encoder-collapse.

### Rescue dispatch recommended

YES — re-author cell with the SAME encoder pipeline as fair_harness:
- Replace `char_trigram_encode_np` with word2vec-projected-then-sparsified path (mirror fair_harness lines 254-298).
- ALSO add lambda sweep to per-context arms (don't fix lambda at 0.3; sweep [0.0..1.0] jointly with T_base) so they're not handicapped vs global.
- OR: keep lambda fixed at the same value used by ARM_GLOBAL_T at its best dev config (per-seed adaptive).

This is a `substrate_per_context_decode_temperature_LM_v2` rescue. Cost: ~40min CPU per seed × 3 seeds = 2h wall time. Worth the spend because per-context T is a Tier-1 untested gap.

### Tier-call

- Atomize current run as `INSTRUMENTATION_CONFOUND_ENCODER_MISMATCH`.
- Do NOT cite -0.317 bpc lift as evidence that per-context T fails — the methodology can't see it.
- Cert_status: `landed_VET_INVALID_methodology_confound`.

---

## TARGET 4 — `substrate_higher_order_taylor_nonlinear_hebbian_LM_v1` (ALL arms collapsed to unigram)

**Verdict: IMPLEMENTATION_BUG — calibration-collapse to unigram across all 5 arms, identical to per-context-T cell's pathology (lambda=0.0 + T=0.01 + bpc=7.7378 unigram floor).**

### Evidence (file-cited)

- Metrics: `data/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1/metrics.json` (run_mode=full, N_DIM=8192, 3 seeds, dense_word2vec_projected encoder).
- Per-arm reads (all 5 arms identical to 4 decimals):
  - ARM_UNIGRAM bpc=7.7378 top1=0.2171
  - ARM_n1 bpc=7.7378 top1=0.2176 (best_T=0.01, best_lam=0.0)
  - ARM_n2 bpc=7.7378 top1=0.2171 (best_T=0.01, best_lam=0.0)
  - ARM_n3 bpc=7.7378 top1=0.2171 (best_T=0.01, best_lam=0.0)
  - ARM_n4 bpc=7.7378 top1=0.2171 (best_T=0.01, best_lam=0.0)
  - ARM_n5 bpc=7.7378 top1=0.2171 (best_T=0.01, best_lam=0.0)
- DETERMINISTIC_METRIC: bpc_std=0.0 across all seeds for all arms (the cell flagged this internally).
- Per-arm `raw_bpc_at_T1_L1` differs (n1=11.6996, n2=11.7058, n3=11.7214, n4=11.7435, n5=11.7695) — so the underlying logits ARE different per arm; only the calibrated BPC collapses.
- Cell source: `experiments/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.py`
  - Lines 98-105 (CELL'S OWN COMMENTS): "The n=1 arm will reproduce fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE (~7.72 BPC); the HARD_PASS threshold is lift vs n=1 ARM (not vs fair_harness sparse_bipolar 7.3065)."
  - BUT line 982-989 `honest_scope` says: "n=1 arm must reproduce fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR BPC=7.3065 within 0.05" — **THE HONEST_SCOPE FIELD DISAGREES WITH THE CELL'S OWN DESIGN COMMENT.**
  - Line 115: `BASELINE_BPC = 7.3065` — referenced in verdict messaging but the cell deliberately uses dense word2vec which targets ~7.72.
  - Verdict logic line 879-881 (`readout_degen`): `n1_bpc > unigram_bpc - 0.05` ⇒ flag DEGEN. n1_bpc=7.7378, unigram=7.7378 ⇒ 7.7378 > 7.6878 ⇒ DEGEN fires correctly. So the cell DID detect the collapse, but the framing in `summary` cites fair_harness 7.3065 as the missed baseline (wrong; fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE was 7.7199, which would also fail the n1 reproduction within 0.05 against the FAIR_HARNESS dense arm).
- fair_harness `ARM_SUBSTRATE_WORD2VEC_DENSE` bpc=7.7199 (best_T=0.0233 best_lam=0.0333) — the n=1 arm here at bpc=7.7378 misses THAT baseline by 0.018 bits, NOT by 0.43.

### Why this is IMPLEMENTATION_BUG (not GENUINE_FAILURE)

1. **The n=1 arm is OFF the fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE baseline by 0.018 bits and collapses to unigram.** fair_harness's dense arm found best_T=0.0233 best_lam=0.0333 (NON-zero lambda; non-trivial calibration). This cell's n=1 found best_T=0.01 best_lam=0.0 (degenerate to pure unigram).
2. **Root cause hypothesis:** the joint sweep grid `LAMBDA_GRID=[0.0, 0.1, 0.3, ...]` skips lambda=0.0333 — the fair_harness optimal point. With this cell's grid, the optimal calibration point doesn't exist in the search space, so it falls back to lambda=0.0 (pure unigram). Verify by checking whether adding lambda=0.05 to the grid recovers n1≈7.72.
3. **The higher-order arms (n2..n5) ALL hit the same lambda=0.0 collapse** because the polynomial nonlinearity attenuates magnitude further (per cell's own comment line 622-623: "(1/sqrt(128))^3 ~ 0.007; so n4 << n1 norm"). With smaller W norm, logits are noisier, calibration even more likely to pick pure-unigram fallback.
4. **The DESIGN was always dense word2vec.** The cell's `honest_scope` field citing fair_harness SPARSE_BIPOLAR 7.3065 is a copy-paste error in the verdict text (cell-author may have copied the docstring from another cell). The actual mechanism — Ocker-Buice nonlinear-Hebbian on dense vectors — is intact in code (lines 295-341).

### Rescue dispatch recommended

YES — minimal-fix rescue cell:
1. Expand LAMBDA_GRID to include {0.02, 0.05, 0.07} so fair_harness's optimal (~0.033) is bracketed.
2. ALSO add an explicit `n_eff = arm.raw_bpc_at_T1_L1` reporting for ALL arms (currently only mean reported) — this is the "uncalibrated" signal that DOES show separation across n.
3. Add fallback verdict: if all arms collapse to unigram via lambda=0.0, report `CALIBRATION_GRID_TOO_COARSE` not `HARD_FAIL`.
4. Consider per-arm best_lambda + best_T REPORTED IN verdict_msg (Fix #28 lesson) so future audits can spot lambda=0.0 collapse instantly.

This is `substrate_higher_order_taylor_nonlinear_hebbian_LM_v2`. Cost: GPU N=8192 was 3.5min per seed previously (per metrics elapsed_s_seed=205-238s); 3 seeds ×5 arms re-run = ~15min wall. Cheap.

### Tier-call

- Atomize current run as `INSTRUMENTATION_CONFOUND_CALIBRATION_COLLAPSE_LAMBDA_ZERO`.
- The cell's `READOUT_DEGEN` flag fired correctly — credit cell-author for the detection logic.
- Cert_status: `landed_VET_INVALID_calibration_grid_too_coarse`.

---

## Cross-target META — convergent pattern

### Shared root-cause family: calibration-collapse to unigram via lambda=0.0

3 of 4 cells (TARGETS 1 unclear pending full, 3, 4) suffer the SAME pathology:

**The joint (T, lambda) sweep can ESCAPE to pure unigram (lambda=0.0) when substrate logits are too noisy to provide ANY lift, and the LAMBDA_GRID includes 0.0 as a valid choice.** Once lambda=0.0 is selected, BPC = unigram BPC exactly, and the mechanism-under-test is INVISIBLE (no matter what it does).

This pattern is INVISIBLE to the cell-author's eye because:
- The verdict_msg cites a per-arm bpc that LOOKS computed (it's just exactly unigram).
- The `top1` stays at unigram's top1 (because argmax of pure-unigram-mixed distribution is the unigram argmax).
- The raw_bpc_at_T1_L1 shows REAL substrate signal (~11.6) but is buried in detail per-arm fields.

### Skunkworks recommendation: cert-architecture C7 (NEW)

Propose META atom: `CALIBRATION-GRID-MUST-EXCLUDE-LAMBDA-ZERO-OR-FLAG-COLLAPSE`.

Concretely:
1. Joint sweep grid should either EXCLUDE lambda=0.0 OR flag `LAMBDA_ZERO_COLLAPSE` post-hoc when best_lambda=0.0.
2. EVERY cert-grade-eligible cell should include `raw_bpc_at_T1_L1` per-arm AND a `READOUT_DEGEN` sanity check (Taylor cell has this — credit) AND a `calibration_collapse` check (Taylor cell does NOT have this).
3. Self-test should fail-loud (sys.exit) on baseline mismatch > tolerance, not just WARN. Per-context-T cell's WARN gate (line 543-547) was insufficient; the WARN fired and the cell PROCEEDED.

### Which negatives are WORTH 2x research drilling vs methodology-fixable

| Target | 2x research drill worth it? | Why |
|---|---|---|
| 1 multi-iter cleanup | WAIT for full N=8192 | Smoke shows opposite-direction signal; full result is load-bearing |
| 2 serotonin mode-switch | NO 2x; instead launch N_DIM=16384 bank-count sweep | Mechanism doesn't lift at param-matched 4-banks; brain says select-compartment needs MORE compartments |
| 3 per-context-T | DON'T 2x current; SAME cell with encoder-fix is the 2x | Methodology can't see the mechanism; rerun with correct encoder |
| 4 Taylor nonlinear-Hebbian | DON'T 2x current; SAME cell with lambda-grid-fix is the 2x | Methodology can't see ANY arm's signal because calibration collapsed |

USER directive "research negatives 2x" applies cleanly to TARGET 2 (genuine null → brain-revival angle = "more compartments"). TARGETS 3 and 4 are NOT real negatives yet; they're methodology-broken cells. Rescue dispatches FIRST, THEN if rescue STILL shows null, run 2x.

---

## Per-target dispatch recommendations (ordered)

1. **WAIT** for TARGET 1 full N=8192 result. Skunkworks will re-VET when landed.
2. **DISPATCH** `substrate_higher_order_taylor_nonlinear_hebbian_LM_v2` (cheap, GPU ~15min wall). Owner: exp_dev. Dispatch via: orchestrator.
3. **DISPATCH** `substrate_per_context_decode_temperature_LM_v2` (CPU ~2h wall, 3 seeds). Owner: exp_dev. Dispatch via: orchestrator.
4. **DISPATCH** `substrate_serotonin_bank_count_sweep_v1` (NEW cell, brain-revival angle for TARGET 2's genuine null). Owner: exp_dev. Larger param budget at 4/8/16 banks. Dispatch via: orchestrator.
5. **SHIP** META atom `CALIBRATION-GRID-MUST-EXCLUDE-LAMBDA-ZERO-OR-FLAG-COLLAPSE` (C7) into Store. Owner: Skunkworks (cert-owner authority).
6. **SHIP** Fix #29 patch to metrics_synthesizer for elapsed_s capture on all paths. Owner: testbed.

---

## Files touched by this audit (read-only, no Store writes; A5 non-destructive)

- `data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json` (read)
- `data/exp_substrate_serotonin_mode_switch_bank_select_LM_v1/metrics.json` (read)
- `data/exp_substrate_per_context_decode_temperature_LM_v1/metrics.json` (read)
- `data/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1/metrics.json` (read)
- `data/exp_substrate_per_context_T_diagnostic_v1/metrics.json` (read; cross-witness)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (read; baseline reference)
- `experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py` (read)
- `experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py` (read)
- `experiments/exp_substrate_per_context_decode_temperature_LM_v1.py` (read)
- `experiments/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1.py` (read)
- `experiments/exp_fair_harness_substrate_as_lm_v1.py` (read; encoder comparison)

Write: only this note file.
