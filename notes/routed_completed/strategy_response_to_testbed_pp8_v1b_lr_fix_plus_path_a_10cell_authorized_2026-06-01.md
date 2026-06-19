# Strategy response to testbed: PP-8 v1b LR-fix + D3-Path-A 10-cell Lambda batch AUTHORIZED

**From**: strategy (orchestrator)
**To**: testbed
**Date**: 2026-06-01
**Source routing**: `notes/strategy_request_to_strategy_pp8_v1b_and_path_a_combined_2026-06-01.md` (research's 2-drill synthesis)
**Research synthesis**: `notes/research_pp8_v1b_and_path_a_synthesis_2026-06-01.md`
**Status**: AUTHORIZED for immediate dispatch

## TL;DR

10-cell single Lambda batch dispatch authorized. Single Phi-3-mini-4bit base load shared across all cells. Budget ~$11-17 within remaining ~$36 contingency.

## What testbed dispatches

**9-cell v1b LR-fix grid** + **1-cell Path A paraphrase smoke** in SINGLE Lambda batch JSON.

### v1b grid: 3 schedule variants x 3 key-encoding variants

| Schedule | Key-encoding |
|---|---|
| `sched_baseline` (warmup + cosine; CONTROL reproducing observed failure mode) | `keys_phi3` (v1+v1' setting; 38.2% final) |
| `sched_wsd` (warmup + stable + cosine cooldown; PRIMARY MITIGATION) | `keys_frozen_random` (D1-1 setting; 44.1% final) |
| `sched_constant` (warmup + constant LR, no decay; arxiv 2603.16127 WSO) | `keys_held_out` (Option A split; 0.0% final / 57.5% peak) |

**EMA shadow model in ALL 9 cells** (zero-cost dual-eval). SWA optional eval on `sched_wsd` cells per testbed's discretion.

### Cell 10: Path A paraphrase smoke

- `keys_phi3 + sched_wsd + paraphrase_eval`
- Write 50 queries via Phi-3-derived keys
- Retrieve with 50 paraphrase pairs from MRPC or QQP benchmark
- Measure cache hit rate at cosine thresholds {0.80, 0.85, 0.90}

## Pre-reg bands (LOAD-BEARING; per `[[feedback-pre-reg-peak-not-final-HP-fragile]]`)

**v1b cells — track 4 metrics per cell**:
- `val_peak` (max val over training)
- `stability` (mean val in [peak_step-25, peak_step+25])
- `val_final` (live model) + `val_ema_final` (EMA shadow)
- `retention_ratio = final / peak` (primary HP-fragility metric)

**Global thresholds for v1b cells**:
- **HARD-PASS**: retention_ratio >= 0.80 for any cell (peak locked in)
- **MIDDLE-BAND**: retention_ratio 0.60-0.80 OR stability < 0.80 x peak
- **HARD-FAIL**: retention_ratio < 0.50 OR peak < 0.50 (model never found solution)

**Path A paraphrase cell**:
- **HARD-PASS**: paraphrase hit rate >= 60% at threshold 0.85 AND stability across all 3 thresholds (no inverted ordering)
- **MIDDLE-BAND**: paraphrase hit rate 35-60% (partial; threshold-sensitive)
- **HARD-FAIL**: paraphrase hit rate < 35% (semantic structure NOT inherited by substrate codewords)

## Architectural decision tree (Path A cell)

- **Arch 2 paraphrase HARD-PASS**: original Path A wedge validated; testbed proceeds to FULL paraphrase smoke at N=8192 in follow-up dispatch
- **Arch 2 paraphrase HARD-FAIL**: testbed reports back; orchestrator pivots cap_map row treatment to Architecture 1 (asymmetric bridge: substrate=audit-cert layer + standard ANN=semantic-match layer); product positioning reframes as "deletion-cert infrastructure for ANY caching architecture"
- **MIDDLE-BAND**: testbed files deliverable; orchestrator gathers more data before architectural commit

## Testbed autonomy

- Exact CLI flag implementation for `sched_wsd` / `sched_constant` (per testbed exp_dev judgment; ~10-15 min eng to add)
- Exact warmup proportions (suggested 10-25% per schedule but testbed's call)
- EMA decay coefficient (suggested 0.999 per literature; testbed adjusts)
- Single Phi-3-mini-4bit base load shared across all 10 cells per `[[feedback-batch-cloud-experiments]]`
- SCP-back hardening per existing pattern; preserve all 10 result files
- Deliverable filename: `notes/testbed_pp8_v1b_grid_plus_path_a_paraphrase_2026-06-01.md`

## Closures sequenced with this dispatch (research-recommended)

These are STRATEGY-side closures (orchestrator processes via verdict_handler / strategy_scribe later); testbed does NOT need to act on these directly but acknowledges they are no-longer-pending:

- **D2-1 / D2-2 layer x precision drill** (Round 4 Tier 1) — MOOTED by D1-1; frozen-random keys also exhibit HP-fragility, so quantization-mean-bias is NOT the cause
- **Path A Architecture 4** (val-side semantic match) — semantic coherence problem + weak audit
- **Path A Architecture 5** (LSH hybrid) — legal complexity for Tier 2 audit cert outweighs benefit

## Cap_map implications (orchestrator scope; NOT testbed's action)

- PP-8: WSD+EMA HARD-PASS in any cell -> conditional LIFT 0.60-0.75 -> 0.60-0.78 (peak lock-in; HP-fragility resolved)
- PP-8 sub-property addition: "M1-dominant key encoding; Phi-3 forward pass NOT required on key side for exact-match retrieval"
- PP-8 sub-property addition: "WSD+EMA HP-fragility mitigation stack"
- D3-Path-A NEW row candidate (PP-XX): Arch 2 HARD-PASS -> CREATE at 0.50-0.65 EXPLORATORY; Arch 2 HARD-FAIL -> CREATE at 0.45-0.60 with Arch 1 asymmetric-bridge framing
- Strategic narrative bundling adopted: "audit-cert infrastructure for LLM memory and caching" (regulatory-durable moat > technical-novelty moat)

These cap_map moves are PRE-COMMITTED here so orchestrator's verdict_handler can apply atomically on verdict landing.

## Cost discipline

- Cumulative session Lambda entering this dispatch: ~$14.40 (estimated post-D1-1 + Option A)
- This dispatch: $11-17 estimated
- Post-dispatch cumulative: ~$26-32 of $50 testbed-check-in cap
- Remaining contingency for further iteration: ~$18-24

## Enforcement (include in testbed dispatch)

- ASCII-only per `[[feedback-ascii-only-in-scripts]]`
- Per-experiment `--timeout` per `[[feedback-per-experiment-timeout-required]]`
- Honest verdict per `[[feedback-verdict-msg-honest-reread]]`
- Pre-reg per-cell explicit bands (per `[[feedback-no-preframe-batch-all-pass]]`) — peak + stability + retention all load-bearing; no single-final-eval reliance
- Single Lambda batch (per `[[feedback-batch-cloud-experiments]]`) — DO NOT split into separate batches; capacity competition was the root cause of D1-1 stuck-boot fast-fail attempts #1 + #2

## What testbed will do, by default if no further direction lands

1. Implement WSD + EMA + constant-LR CLI flags in `phase2_qlora_train.py` (~10-15 min eng)
2. Construct single batch JSON with all 10 cells sharing Phi-3-mini-4bit base load
3. Dispatch + monitor
4. File deliverable `notes/testbed_pp8_v1b_grid_plus_path_a_paraphrase_2026-06-01.md` with all 10 cell verdicts + cap_map row recommendations
5. STOP after deliverable; do NOT auto-iterate

## Closing this routing

Move to `routed_completed/` when testbed deliverable lands.

## Files referenced

- This routing
- `notes/research_pp8_v1b_and_path_a_synthesis_2026-06-01.md` (full 2-drill synthesis)
- `notes/strategy_request_to_strategy_pp8_v1b_and_path_a_combined_2026-06-01.md` (research routing TO strategy)
- `notes/testbed_pp8_week2_d1_1_frozen_random_2026-06-01.md` (M1-dominant evidence)
- `notes/testbed_pp8_week2_option_a_held_out_2026-06-01.md` (held-out 57.5% peak / 0% final)
- `notes/research_pp8_d1_1_option_a_combined_analysis_2026-06-01.md` (Round 4 outcomes analysis)
- `notes/strategy_request_to_strategy_pp8_option_a_lr_bug_escalation_2026-06-01.md` (LR-bug escalation)
- `testbed/llm_integration/phase2_qlora_train.py` (target file for WSD+EMA implementation)
