# Pre-reg: c_composition_storage_density_v2 (GPU; supersedes v1 smoke regime)

**Date:** 2026-06-22
**Author:** Orchestrator (cell-author + dispatch under Fix #22+#23 first application)
**Cell:** `experiments/exp_c_composition_storage_density_v2.py`
**Composes with v1 pre-reg:** `notes/c_composition_storage_density_v1_pre_reg_2026-06-22.md` (same architecture; new bands + wider M_grid)

## Why v2

v1 (numpy/CPU; M_grid up to 25k) was DISCRIMINATOR-INVALID at smoke (M=2000 cap = all 5 arms saturated at M_fail=2001 = compound mechanisms had nothing to lift over). Fix #16 rule: "every pull-up needs a CAN-fail regime." v2 extends M_grid by 25x and switches to GPU+torch primitives so the heavy matmul-bound sweep completes within an overnight budget.

## Architecture (UNCHANGED from v1)

5 arms over the same mechanism stack:
- Arm 1 (BASELINE): plain multi-value Hebbian (n8 mechanism unchanged)
- Arm 2 (+ MODULAR): + K=8 macrocolumn content-routed (m1 lineage)
- Arm 3 (+ WHITENING): + ZCA whitening on encoded keys (n10 lineage)
- Arm 4 (+ KWTA): + k-WTA sparse readout, k=20 winners (n4 lineage)
- Arm 5 (COMBINED): MODULAR + WHITENING + KWTA stacked on top of BASELINE

Synthetic-bipolar keys (no encoder; substrate-primitive isolation; clean discriminator). N_DIM=4096 (matches n8 chain-grade baseline + v1).

## Config

| Param | v1 | v2 |
|---|---|---|
| Backend | numpy (CPU) | torch+cuda (GPU) |
| M_GRID | [1k, 5k, 10k, 25k] | **[1k, 10k, 50k, 100k, 250k, 500k]** |
| MAX_ENT_POOL | 25,000 | **200,000** (needed for M=500k) |
| SEEDS | [7, 17, 23] | [7, 17, 23] (unchanged) |
| N_EVAL | 300 | 300 (unchanged) |
| Queue | local_cpu (smoke only) | **overnight_queue (full GPU)** |

## Pre-reg HARD bands (NEW for v2; supersedes v1 lift-based bands)

Define `M_star` = smallest M in M_GRID where mean baseline setrecall < 0.50 across seeds.

**HARD_PASS (chain-grade):**
- M_star exists in M_GRID (= baseline DOES fail somewhere — discriminator-valid)
- AND combined-arm mean setrecall at M_star >= 0.80
- AND ratio combined / baseline at M_star >= 3.0x
- AND cv across seeds <= 0.05 (combined arm at M_star)
- AND substrate-only-decode preserved (n_llm_calls == 0)

**HARD_FAIL:**
- (a) DISCRIMINATOR_INVALID: no M in M_GRID causes baseline to fail (same trap v1 hit; need to re-scope upward), OR
- (b) ratio combined / baseline at M_star <= 1.0 (compound mechanisms don't compose — wrong direction)

**MIDDLE_BAND:**
- M_star exists AND ratio in (1.0x, 3.0x) — partial composition; characterize which mechanism pair load-bears.

## Direction (Fix #5 / pre-reg-direction-must-honor-intent)

Expected improvement direction: combined-arm setrecall at M_star is GREATER THAN baseline-arm setrecall at M_star (compounded mechanisms compose multiplicatively). Wrong direction (ratio < 1.0) = HARD_FAIL, NOT MIDDLE_BAND.

## Discriminator-regime sanity (Fix #16)

At DISCRIM_M = 10k: baseline should not catastrophically crater (we expect ~0.5–0.95 setrecall depending on capacity load). Reported in verdict_msg as diagnostic; not a gate (the M_star detection itself is the gate).

## Substrate-only-decode gate

`_LLM_CALL_COUNTER = [0]` at module top; pure torch primitives in ingest/score/verdict; zero LLM forward calls anywhere. Metrics field `zero_llm_calls_at_inference == True` required for HARD_PASS.

## Provenance

- Corpus: synthetic-bipolar (no external data dependency; allow_synthetic=True by design — this is a primitive-isolation cell, not a corpus-coverage cell).
- Encoded-key variant deferred to v3 (only ship if v2 HARD_PASS).

## Runtime expectations

- Full run: 6 M-points x 5 arms x 3 seeds = 90 cells.
- Heaviest cells: combined arm at M=500k (modular ingest + score on 200k-entity codebook).
- GPU walls on RTX (estimate): ~3-8 min per cell at large M; smaller M sub-minute. Total full ETA ~2-4h on GPU.
- Smoke: 1 seed, M_grid=[1k, 10k, 50k]; expected <15 min on GPU.
- atexit synthesize-on-timeout pattern baked in (TODO #9 from pipeline template): if SIGKILL fires, partial seeds reconstitute a TIMEOUT_PARTIAL metrics.json.

## Disposition / composes with

- If HARD_PASS: ratifies that modern hdlab primitives (modular K-W + whitening + sparse k-WTA) compose multiplicatively at scale, joining existing chain-grade composition evidence (`EXP_substrate_capacity_composition_b2xb4_v1_n2048` HARD_PASS 240x; `EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` HARD_PASS 600K patterns) at the modern primitive set + N=4096 + multi-value KG regime.
- If HARD_FAIL (composition-fails branch, not discriminator-invalid): the modern primitives do NOT compose at scale — would be a substantive negative; route to Research for 2x-revival drill on per-mechanism pair characterization.
- If MIDDLE_BAND: characterize which pair of mechanisms is load-bearing (m+w vs m+k vs w+k via per-arm setrecall pattern).

## Strategic value (per spawn-prompt)

First cell explicitly routed via the orchestrator under Fix #22 (compute-routing-discipline) + Fix #23 (GPU-vs-remote-CPU routing). Demonstrates the corrected routing pattern. P=0.40 (novel-synthesis cap; deflated for compound-orthogonality uncertainty; existing chain-grade composition atoms at N=2048 lift the prior).

— Orchestrator (cell-author + dispatch under Fix #22+#23); v2 pre-reg durable artifact
