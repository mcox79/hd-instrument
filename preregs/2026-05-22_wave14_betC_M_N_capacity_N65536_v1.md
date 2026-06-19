# Pre-reg: Wave 14 Bet C M/N Capacity at N=65536 v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_post_v127_batch_2026-05-22.md` (Strategy 20:14 EDT) — Priority 2: V2.D Phase 3 completion.

## Question

At N=65536, what is the largest M/N where Hebbian W substrate retrieves ≥95% of test queries correctly? Strategy target: M/N ≥ 8 (matches N=4096 baseline).

Memory engineering: W in bf16 (8.6GB) + batched per-query computation to avoid M×M intermediates that would OOM.

## Hypothesis

H_scales: capacity M/N ≥ 8 at N=65536 — substrate-product capacity claim extends linearly to higher N.

H_drops: capacity M/N < 4 — substrate has finite-N anomaly at N=4096 that doesn't scale.

## Pre-declared verdicts

- `BET_C_N65K_PASS` — M/N ≥ 8.
- `BET_C_N65K_PARTIAL` — 4 ≤ M/N < 8.
- `BET_C_N65K_KILLED` — M/N < 4.
- `BET_C_N65K_INCONCLUSIVE` — metric collection error.

## Method

For each M/N ratio r ∈ {1, 2, 4, 8}:
1. Build M = r·N random ±1 patterns (bf16 storage).
2. W = (values^T @ keys) / N as bf16.
3. For 100 random test queries: readout = W^T @ keys[i]; pred = argmax(values @ readout); check pred == i.
4. acc = mean correct.
5. Capacity = largest r where acc ≥ 0.95.

Per-query computation avoids M×M intermediates; fits in 16GB VRAM at N=65536 r=8 (~13GB total bf16 footprint).

## Acceptance thresholds

- 0.95 PASS threshold matches Bet C N=4096 baseline.
- 8 M/N PASS matches N=4096 substrate-product anchor.

## Config

- N=4096 smoke, 65536 full.
- M/N grid full: [1, 2, 4, 8].
- n_test_queries=100 full.
- Single seed=17.

## Pre-declared interpretation

- **PASS**: V2.D Phase 3 sub-test #2 PASS. Substrate-product capacity claim scales linearly to N=65536. 4 of 5 V2.D sub-tests pass.
- **PARTIAL**: substrate scales sub-linearly. Update positioning to honest "M/N ≥ 4" claim.
- **KILL**: substrate doesn't scale on capacity. V2.D thesis broken on Bet C; investigate why.

## Cost

W bf16 at N=65536: 8.6GB allocation. Per-query: O(N²) + O(M·N) ops. 100 queries × 4 ratios at M=8N: ~10 min total.

## Not in scope

- Kerdock 4-coset codebook (random ±1 baseline matches Bet C N=4096).
- M/N > 8 (cost prohibitive at N=65536).
- Modern dense AM cleanup (V2.D revision dropped this).
