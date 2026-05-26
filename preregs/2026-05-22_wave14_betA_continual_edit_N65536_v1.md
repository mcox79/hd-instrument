# Pre-reg: Wave 14 Bet A Continual Edit at N=65536 v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_post_v127_batch_2026-05-22.md` (Strategy 20:14 EDT) — Priority 3: V2.D Phase 3 completion sub-test #3.

## Question

At N=65536 with M=N initial stored pairs, does the substrate's Bet A anti-Hebbian erase + insert mechanism hold 100 edits AND 1000 edits with edit_acc ≥ 0.95 AND kept_acc ≥ 0.95?

Strategy theory: per cycle 98, edit horizon ~ M = N·k where k=8 at M=8N. At N=65536 predicts 524K edit horizon.

## Hypothesis

H_holds_1k: 1000-edit PASS — substrate scales editable memory to N=65536.

H_holds_100: 100-edit PASS but 1000-edit fails — Bet A scales partially.

H_kill: 100-edit fails — substrate's edit mechanism broken at N=65536.

## Pre-declared verdicts

- `BET_A_N65K_HOLDS_1K` — 1000-edit edit_acc ≥ 0.95 AND kept_acc ≥ 0.95.
- `BET_A_N65K_HOLDS_100` — 100-edit PASS AND 1000-edit fails.
- `BET_A_N65K_KILLED` — 100-edit fails.
- `BET_A_N65K_INCONCLUSIVE` — metric collection error.

## Method

1. Build initial W = (values^T @ keys)/N with M=N random ±1 pairs (bf16).
2. For each edit i: pick stored key k_i, generate new value v_new_i; apply
   - W -= α · outer(W·k_i, k_i) / ||k_i||²    (anti-Hebbian erase)
   - W += outer(v_new_i, k_i) / N              (insert)
3. Query 50 random edited pairs (k, v_new) → check sign(W·k) overlap with v_new > 0.7.
4. Query 50 kept (non-edited) pairs (k, v_orig) → same check.
5. Report edit_acc, kept_acc.

## Acceptance thresholds

- 0.95 PASS matches Bet A N=4096 baseline.
- 0.7 overlap = "matches new value" (per cycle 86 Lane C smoke convention).

## Config

- N=4096 smoke, 65536 full.
- M_init=N (so initial M/N=1).
- n_edits_grid full: [100, 1000].
- alpha=1.0 (full erase).
- Single seed=17.

## Pre-declared interpretation

- **HOLDS_1K**: V2.D Phase 3 sub-test #3 PASS. Substrate-product editable-memory claim scales to N=65536, 1000 edits. Lane C compliance-audit at scale viable.
- **HOLDS_100**: substrate scales partially. Demo 1 / Lane C bounded at 100-edit horizon.
- **KILL**: substrate's edit mechanism doesn't scale. V2.D Phase 3 sub-test #3 fails.

## Cost

W bf16 at N=65536: 8.6GB. Per-edit O(N²) ~ 4.3e9 ops. 1000 edits at bf16 GPU ~ a few minutes.

## Not in scope

- M/N > 1 init (separate V2.D Phase 3 study).
- Adversarial edit sequences.
- Edit horizon search (binary search of breaking point).
