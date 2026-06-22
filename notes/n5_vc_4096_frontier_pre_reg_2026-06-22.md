# Pre-reg: n5_vc_4096_frontier_v1 (Path A V_C=4096 frontier; V_C-alone discriminator)

**Date:** 2026-06-22
**Cell:** `experiments/exp_n5_vc_4096_frontier_v1.py`
**Anchor name:** `n5_vc_4096_frontier_v1`
**Queue:** `remote_cpu_queue` (residuals_per_token.npz lives on marsh@home)
**Author:** Exp-Dev (cell-author cycle)
**Source pre-reg trigger:** Skunkworks bundled VET (commit bcaab129) — "DISPATCH Path A V_C=4096 IMMEDIATELY (priority 1); standalone first for clean discriminator." Research N2 frontier ranking note + brain-drill V_C-needs-k-scaling prediction (k-WTA composition is the n4+V_C joint follow-on).

---

## Mechanism (V_C-alone discriminator)

N2 demonstrated `V_C=1024 / N_DIM=16384 / K=1` substrate_bpc=4.96 (MIDDLE_BAND). The Path A lever asks: does V_C scaling ALONE (independent of n4 k-WTA-VQ multiplicity, currently smoke-running) lower the ceiling at the source?

Concept-LM ceiling = H(token | concept) is bounded by codebook resolution. A larger V_C should reduce per-concept token entropy: each concept covers fewer tokens, ceiling drops. The brain-drill predicts V_C scaling needs k-scaling at biological sparsity (V_C=4096 → optimal k ≈ 200), but this cell tests V_C ALONE first (K=1 hard one-hot) for a CLEAN discriminator. k-WTA + V_C composition is a follow-up (after n4 lands).

WRITE: hard one-hot km.predict() at each residual position; D[c, tok] += C[c] * LR_DECODE.
READ: hard one-hot pred_c row of D for token decode (no soft-pooling at read; this isolates V_C-alone effect).

Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM forward calls).

## Fixed config

- K = 1 (substrate depth; clean V_C-alone discriminator; n4 K_GRID composition deferred)
- F_SPARSE = 0.006
- TRAIN_FRAC = 0.8
- LR_DECODE = 1.0
- LAM_BACKOFF = 0.1
- INTERP_B = 0.3
- seeds = [7, 17, 23] (full); [1] (smoke)
- MAX_DOCS = 100000 (full); 200 (smoke)

## V_C × N_DIM sweep (Phase 1)

`VC_GRID = [1024, 4096]` × `N_GRID = [16384, 32768]` = 4 arms per seed.

- (V_C=1024, N=16384): N2 ANCHOR SANITY (must reproduce 4.96 substrate_bpc within 0.10).
- (V_C=1024, N=32768): N_DIM-alone control arm.
- (V_C=4096, N=16384): V_C-alone load-bearing FRONTIER arm.
- (V_C=4096, N=32768): joint V_C + N_DIM arm.

Substrate plugin: N1 v3.1 concept-LM (Jelinek-Mercer + count-proportional decode; MKN composition deferred).
Corpus: pythia residual subset (same as N1/N2/n3/n4 for direct comparison).

## Pre-registered bands (HARD)

**HARD_PASS (chain-grade, ALL of):**
- some V_C=4096 arm (any N_DIM) has substrate_bpc <= 4.36 (>=0.60 bit improvement vs N2's 4.96)
- cv across 3 seeds <= 0.05 for the passing config
- not saturated (alpha < 1.0)
- substrate-only-decode (zero LLM calls; counter asserted = 0)
- direction-correct: V_C=4096 strictly better than V_C=1024 at SAME N_DIM (per Skunkworks pre-reg-direction discipline)
- anchor sanity: V_C=1024/N=16384 reproduces N2's 4.96 within 0.10 bits
- run_mode = "full" (Fix #5 pre-flight guard)

**HARD_PASS_PLUS:** substrate_bpc < bigram_bpc (3.844) at some V_C=4096 arm.

**MIDDLE_BAND (partial, EITHER):**
- 0.10-0.60 bit improvement at V_C=4096 vs N2 baseline
- ceiling drops but substrate doesn't clear HARD_PASS bar

**HARD_FAIL (any):**
- <0.10 bit improvement at V_C=4096 vs N2 → V_C scaling alone doesn't help → route to k-WTA + Path A composition (n4+V_C joint).
- OR V_C=4096 WORSE than V_C=1024 at SAME N_DIM (wrong-direction; pre-reg-direction-must-match-intent).
- OR V_C=1024/N=16384 anchor mismatch (differs from N2 4.96 by > 0.10 at full).
- OR substrate-only-decode gate violated (LLM call counter > 0).
- OR run_mode != "full" (Fix #5 stale-smoke catch).

## Instrumentation (REQUIRED, per Skunkworks N2 chain-grade spec)

- per_unit BPC per (V_C × N_DIM × seed); cv <= 0.05 (chain-grade per_unit blocker #1).
- zero_llm_calls_at_inference LOGGED in metrics (#3).
- ceiling_bpc + concept_top1 decomposition per config (does V_C=4096 lower ceiling?) (#4).
- corpus_provenance_real=True LOGGED; allow_synthetic=False.
- run_mode default = "full"; CONFIG_VERSION captures VC_GRID + N_GRID + seeds.
- Substrate-only-decode gate: cell imports NO transformers/torch modules; counter STAYS at 0 (structural guarantee + AST-verified + logged).
- km_wall_s recorded per (seed, V_C) — for honest GPU-vs-CPU routing decision.

## Honest sizing concern (load-bearing GPU/CPU question)

V_C=4096 is 4x larger codebook than N2's V_C=1024. MiniBatchKMeans fit time scales ~linearly in V_C; recall + decode scale similarly. Local CPU sklearn probe stalled at trivial 2k-sample input (Windows .venv overhead), so per-arm wall is NOT measurable locally — must measure on the remote runner.

Projection from N2 baseline (V_C=1024/N=16384 took ~10-11 min/seed on remote_cpu):
- V_C=1024/N=16384 arm: ~10 min/seed (anchor)
- V_C=1024/N=32768 arm: ~20 min/seed (2x N memory)
- V_C=4096/N=16384 arm: ~40 min/seed (4x V_C)
- V_C=4096/N=32768 arm: ~80 min/seed (4x V_C + 2x N)
- Total per seed: ~150 min (~2.5h)
- 3 seeds: ~7.5h projected

Per-arm wall_s is logged so Director can route to overnight_queue (GPU) if remote_cpu is too slow. The cell's `_seed_checkpoint` resume harness preserves seed-1 results if a timeout interrupts mid-seed-2.

**Timeout:** 28800s (8h) — generous against the ~7.5h projection; PROT-021 _seed_checkpoint already wired. No PROT-019 _n suffix on this anchor name.

## Falsifiable predictions

1. **Primary (V_C=4096 lowers substrate by >=0.60 bits):** P(HARD_PASS) ≈ 0.30 (V_C-alone has known limits; brain-drill predicts joint V_C+k scaling is needed). 0.10-0.60 partial improvement P ≈ 0.45.
2. **Secondary (direction-correct: V_C=4096 strictly < V_C=1024 at same N):** P ≈ 0.75. The other 25%: VQ-overfit at V_C=4096 with limited training data (concept coverage thin → ceiling improvement gets cancelled by recall noise).

## Composability

If HARD_PASS or MIDDLE_BAND: compose with n4 k-WTA (`V_C=4096 + k-WTA at k~200`) is the joint follow-on, predicted to land f_eff ≈ 0.05 biological sparsity (brain-drill optimum).
If HARD_FAIL: route to n4+V_C joint REVIVAL drill (the V_C-needs-k brain-drill caveat is then load-bearing).

## Fixes applied (10-fix discipline)

- Fix #4: NO background bash watchers; Director polls
- Fix #5: pre-flight run_mode check inside verdict() (smoke-mislabel-as-full HARD_FAIL)
- Fix #6: zero-D-overlap fallback in batched_token_logprob (n3/n4 pattern)
- Fix #10: this note filename is `<topic>_<date>.md`, no `to_<role>` prefix
- ASCII-only / 12 selftest tests / per-unit blocker / commit-before-remote-dispatch

— Exp-Dev (cell-author cycle), 2026-06-22
