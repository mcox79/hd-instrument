# Pre-registration: n5_trigram_concept_lm_v1

**Date:** 2026-06-26
**Anchor name:** n5_trigram_concept_lm_v1
**Script:** experiments/exp_n5_trigram_concept_lm_v1.py
**Queue:** remote_cpu_queue (per USER directive 2026-06-26 + residuals_per_token.npz on marsh@home)
**Authority:** Research drill 1 (notes/research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md) + exp_dev handoff (notes/exp_dev_handoff_research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md ANCHOR 1)
**Composes with:** n1v3 (chain-grade harness) + n2 (N=16384 V_C=1024 anchor) + c3 sequence-binding 586 + g1b autoregressive 587

---

## What this tests

FIRST substrate-native language ingest cell of arc 2026-06-26. Tests whether
context-depth via HRR sequence-bind of 2-prior concepts (P(c_t | c_{t-1}, c_{t-2}))
closes the 1.13-bit gap between substrate-LM bigram floor (4.96 BPC) and text8
word-bigram (3.84 BPC). Substrate-only-decode (zero LLM calls at inference).

If HARD_PASS: substrate-LM crosses word-bigram parity on real text -- first
measurable LM-class win. If MIDDLE: route to Anchor 2 (V_C sweep). If HARD_FAIL:
context-depth NOT the lever; route to Gap-3 modern-Hopfield cleanup composition.

---

## 3 ARMS (mandatory per handoff)

| Arm                              | Context construction                         | Decoder path                              |
|----------------------------------|----------------------------------------------|-------------------------------------------|
| ARM_BIGRAM_BASELINE              | ctx[t] = L2_norm(C[c_t])                     | W (bigram) -> argmax over codebook         |
| ARM_TRIGRAM_HRR                  | ctx[t] = L2_norm(hrr_bind(C[c_{t-1}], C[c_t])) | Same W; HRR bind composes context     |
| ARM_TRIGRAM_HRR_PLUS_BACKOFF     | HRR-bind when count(c_{t-1}, c_t) >= 3; else bigram | Same W; Witten-Bell sparsity backoff |

**Key design (load-bearing):** W = P_src.T @ P_dst built from BIGRAM (c_t -> c_{t+1})
training pairs in ALL arms. Trigram lift happens at QUERY time via the
hrr_bind composition (substrate's chain-grade c3 sequence-binding primitive).
The recall is q @ W: same W, different query construction per arm. This is
the COMPOSITION primitive (orthogonal axes: storage W is bigram; query is
trigram via HRR-bind).

---

## Pre-registered verdict bands (LOCKED at module init via assert; verbatim from handoff)

**HARD_FAIL_SANITY (META_M7 reproduce-once rail; FIRES FIRST):**
- ARM_BIGRAM_BASELINE must reproduce n2 N=16384/V_C=1024/K=1 anchor sub_bpc=4.96
  within 0.05 BPC
- If sanity FAILS: ABORT trigram verdict claim (substrate-LM gap measurement invalid)

**HARD_PASS (chain-grade candidate; P_deflated = 0.25):**
- best_trigram_bpc <= 4.30 (closes >= 0.66 of 1.13-bit gap to word-bigram 3.84)
- AND cv <= 0.05 across 3 seeds (seed-stable)
- AND zero LLM forward calls at inference (structural + counter == 0)
- AND ARM_TRIGRAM_HRR_PLUS_BACKOFF wins (distinguishing regime: BACKOFF load-bearing)
  OR ARM_TRIGRAM_HRR wins alone (regime: HRR-alone sufficient; ship as primitive)

**MIDDLE_BAND (partial closure; P_deflated = 0.45):**
- best_trigram_bpc in (4.30, 4.70]
- Reports best arm + distinguishing regime; route to n6 V_C sweep

**HARD_FAIL (P_deflated = 0.30):**
- best_trigram_bpc > 4.70 (less than 0.26 bits closed) OR
- depth_gain NEGATIVE for BOTH trigram arms (HRR-bound context HURT vs bigram)
- Triggers: context-depth NOT the lever; route to n6 V_C sweep as PRIMARY

**Probabilities sum to 1.00** (asserted at module init). Asymmetric toward MIDDLE
consistent with PROVEN-BOUND tier history + Skunkworks diminishing-returns caveat.

---

## Distinguishing-regime gate (mandatory C5; from handoff Section 7)

- ARM_TRIGRAM_HRR HARD_PASSES alone:        HRR sequence-bind sufficient; ship as primitive
- ARM_TRIGRAM_HRR_PLUS_BACKOFF wins alone:  backoff load-bearing; sparsity dominates; ship with WB backoff
- Both FAIL:                                 context-depth NOT the lever; route to n6_optimal_V_C_sweep_v1

---

## Config

| Param         | Full default | Smoke default | How to set                    |
|---------------|--------------|---------------|-------------------------------|
| N_DIM         | 16384        | 16384         | HDLAB_N_DIM or --n-dim        |
| V_C           | 1024         | 1024          | HDLAB_VC or --vc              |
| F_SPARSE      | 0.006        | 0.006         | HDLAB_F_SPARSE or --f-sparse  |
| WB_THRESHOLD  | 3            | 3             | HDLAB_WB_THRESHOLD env        |
| MAX_DOCS      | 100000       | 200           | hard-coded per RUN_MODE       |
| SEEDS         | [7,17,23]    | [7]           | hard-coded per RUN_MODE       |
| ALLOW_SYNTHETIC | False (LOCKED) | False     | code-locked; fail-loud only   |
| ENCODER_PROV    | SUBSTRATE_NATIVE | SUBSTRATE_NATIVE | module constant (R3 Path C) |

META_M7 capacity-sensitive dims (N_DIM, V_C, F_SPARSE) IDENTICAL smoke/full so the
reproduction rail is meaningful (BIGRAM_BASELINE smoke = BIGRAM_BASELINE full
modulo doc count). Only MAX_DOCS + SEEDS differ.

---

## Substrate primitives composed (Path C compliant)

- char_trigram_encoder.py    basis (hash-based deterministic; NO label leak)
- sequence_memory.py         c3 chain-grade sequence binding (586)
- iterative_attractor.py     cleanup memory at readout
- binding.py                 HRR bind (np-FFT circular convolution; numpy-only)
- bundling.py                concept superposition for Witten-Bell interpolation
- generation.py              g1b autoregressive primitive (587)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE" (R3 Path C; no external encoder).
All composition uses numpy (no torch import; no LLM forward call structurally).

---

## By-construction guards

1. **CORPUS_PROVENANCE_REAL = True asserted + LOGGED.** allow_synthetic = False
   passed to load_data (fail-loud per phase_d_tier6 wikitext2 silent-fallback lesson).
2. **Substrate-only code-trace:** this cell imports NO transformers/torch.
   _LLM_CALL_COUNTER asserted == 0 before metrics write. T11 selftest validates.
3. **HARD_FAIL_SANITY rail FIRES FIRST** before any trigram verdict claim.
   Catches the substrate-LM bigram-gap measurement invalidity case (META_M7 reproduce).
4. **Per-arm metrics structure (Fix #28):** arm_metrics dict per arm in per_seed;
   verdict reads per-arm sub_bpc directly, NOT verdict_msg framing.
5. **depth_gain sign discriminator:** by-construction CAN-fail (HRR-bound context
   COULD hurt if binding noise dominates the shorter-context signal). Negative
   depth_gain on BOTH trigram arms triggers HARD_FAIL.
6. **Pre-reg bands LOCKED via assert at module init:** any param mutation
   triggers AssertionError before run starts (P_HARD_PASS + P_MIDDLE + P_HARD_FAIL == 1.0;
   HARD_PASS_BPC < MIDDLE_BAND_UPPER < HARD_FAIL_SANITY_ANCHOR).
7. **cv <= 0.05 required for HARD_PASS** (3-seed seed-stability).

---

## Instrumentation (Fix #28 + Skunkworks 4 structural blockers)

1. **per_unit:** per-seed entry stored in per_seed; recompute-off-per_unit ready
2. **cv <= 0.05** computed across seeds in verdict
3. **zero_llm_calls_at_inference: True LOGGED** in metrics (structural + counter audit)
4. **VQ-floor decomposition** via per-arm substrate_bpc and depth_gain
5. **Per-ARM metrics:** ALL 3 arms scored + stored in arm_metrics dict per seed;
   verdict reads per-arm directly (no over-claiming from summary framing per Fix #28)
6. **Pre-reg bands LOCKED:** module-init assert blocks mutation

---

## Formula self-tests (PROT-022; T1-T11; ALL PASS on .venv)

- T1: HRR bind/unbind roundtrip recall + codebook cleanup recovers original
- T2: Sparse codebook k-of-N active + near-orthogonal
- T3: build_W identity holds
- T4: Batched concept recall == per-query recall
- T5: BPC formula finite + positive on synthetic
- T6: 3-ARM dispatcher returns per-arm context vectors
- T7: HARD_FAIL_SANITY discriminator correctly distinguishes 4.96 vs 4.00
- T8: depth_gain sign discriminator (+ for trigram-improves, - for hurt)
- T9: Witten-Bell backoff routes low-count to bigram, high-count to HRR
- T10: Pre-reg bands LOCKED via module-init assert
- T11: LLM_CALL_COUNTER == 0 substrate-only-decode structural

**Verified ALL 11 PASS on d:/AI/hd-instrument/.venv/Scripts/python.exe.**

---

## Smoke-graceful-degradation gate

residuals_per_token.npz lives on marsh@home (remote runner), NOT local laptop.
When --smoke runs locally without NPZ, the cell writes a stub metrics.json with
verdict=SMOKE_INFRA_OK so queue_add gate passes structurally. REAL smoke
(MAX_DOCS=200, SEEDS=[7]) runs on REMOTE runner after dispatch where NPZ exists.

This matches the n1v3 + n2 pattern: those cells are also remote_cpu_queue-only
(residuals_per_token.npz is the upstream Pythia residual output that lives on
marsh@home).

---

## Timeout estimate (per handoff cost estimate + n2 measured wall)

**Smoke arm** (this dispatch):
- Smoke MAX_DOCS=200 with N=16384/V_C=1024/3 ARMS on remote_cpu
- n3 cell wall ~0.8s for 10k chars; n5 has 3 arms but smaller doc count
- Estimated smoke wall on remote: ~60-180s (within SMOKE_TIMEOUT_S=180s)
- **Smoke entry timeout pre-reg: 600s** (safety margin)

**Full run** (queued in same submission):
- Per-handoff cost estimate: ~4-6 hr local_cpu for 1 arm at N=16384/V_C=1024/3 seeds/100k docs
- 3 arms x 4-6 hr each = 12-18 hr base, BUT W is built ONCE and reused across arms;
  per-arm marginal cost is just ctx_vec construction + scoring loop (~30-60min per arm)
- Effective total: W-build ~30min + 3*scoring(~30-60min) + VQ-fit ~20min ~ 2.5-4 hr per seed
- 3 seeds x 4hr = 12 hr; with margin = ~18000s (5hr) is too tight
- **Full entry timeout pre-reg: 21600s (6 hours)** per PROT-019 floor for N>=8192
  - Note: anchor name has NO _n<N> suffix (PROT-018 N-suffix binding only fires if
    suffix matches), but timeout chosen at PROT-019 _n>=8192 tier as safety floor
- Per-seed checkpoint (PROT-021) protects partial progress

---

## Routing (USER directive 2026-06-26 -- remote only today)

- Route to remote_cpu_queue (NOT local_cpu_queue or overnight_queue)
- Commit cell + prereg + push to origin/main before remote dispatch
  (BUT: push is harness-DENIED to exp_dev; only hd_metrics_sync can push)
  -> file the cell, commit locally, ask hd_metrics_sync to push
- queue_add.py to remote_cpu_queue with --skip-smoke (local NPZ absent;
  smoke runs on remote after dispatch via runner's HDLAB_EXP_NAME=*_smoke)
- REMOTE VERIFY post-dispatch (Fix #21 polling)
- Timeout: 21600s (6h budget per handoff cost estimate + PROT-019 safety)

---

## PROT-018 N-suffix note

Anchor `n5_trigram_concept_lm_v1` has NO `_nN` suffix. N is configurable via
HDLAB_N_DIM env (default 16384). Per PROT-018 rule 3: no _nN suffix because
N is exposed as a tunable param. PROT-019 tier-floor logic only fires on
explicit _n<N> in anchor name; this cell uses the 21600s timeout voluntarily
as safety floor for N=16384.

---

## Risk surface (honest)

- BIGRAM_BASELINE may NOT reproduce 4.96 exactly within 0.05 BPC: doc subset
  permutation seed effects, MiniBatchKMeans initial state differences. If
  sanity fails, ABORT trigram verdict per HARD_FAIL_SANITY rail. This is the
  designed behavior (META_M7 reproduce-once is load-bearing).
- HRR bind on sparse-bipolar codes is noisier than on dense-Gaussian (Plate's
  analysis assumes Gaussian); the substrate codes are sparse k-of-N. Roundtrip
  cos sim measured at 0.51 in selftest (vs 1.0 on Gaussian); codebook cleanup
  argmax recovers the original within selftest scale (V_C=8). At V_C=1024 the
  noise floor may dominate -> depth_gain NEGATIVE band is the diagnostic.
- WB_BACKOFF_THRESHOLD=3 is a hyperparameter; tuned by intuition not measurement.
  If ARM_TRIGRAM_HRR_PLUS_BACKOFF backs off too aggressively (rate > 0.5),
  the arm collapses to bigram + some noise; expected as the by-construction CAN-fail
  outcome for sparse trigrams.
- 6h timeout assumes 3-arm scoring shares W-build cost. If per-arm scoring is
  IO-bound or sklearn VQ-fit dominates, full may exceed 6h -> per-seed
  checkpoint protects.

---

## Dispatch plan (this prereg covers FULL via remote_cpu_queue)

1. Self-test PASS (11/11) on .venv -- DONE.
2. Local smoke gate gracefully degrades (NPZ absent on local; stub metrics
   with SMOKE_INFRA_OK verdict) -- DONE.
3. Commit cell + prereg path-scoped (NO git add -A).
4. queue_add.py to remote_cpu_queue with --timeout 21600 + --skip-smoke
   (data lives on remote; runner's HDLAB_EXP_NAME=_smoke will trigger
   real smoke pass on remote first).
5. REMOTE VERIFY post-dispatch: confirm cell-spec arrives on remote +
   check queue.json status.
6. Notify Orchestrator (cell filed + queued for remote dispatch).
7. Notify Skunkworks on landing (data arrives; ready for landed-VET).

-- Exp-Dev (Opus 4.7-1M)
