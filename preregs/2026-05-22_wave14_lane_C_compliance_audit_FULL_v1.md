# Pre-reg: Wave 14 Lane C Compliance-Audit FULL Multi-Seed v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_lane_C_compliance_FULL_2026-05-22.md` (Strategy 15:55 EDT).
**Predecessor:** cycle 86 `wave14_lane_C_compliance_audit_smoke_v1` = LANE_C_PRIMITIVES_COMPOSE PERFECT.
**Product dependency:** Demo 2 (browser-extension forensic-erase) + Demo 1 (Lane D agent memory SDK erase claim).

## Question

Does the cycle 86 Lane C smoke PERFECT (delete_leak=0, edit_acc=1.0, kept_acc=1.0, side_effect=0, ECE=0) reproduce across 5 multi-seed runs at FULL config (N=4096, M=100 facts, 50 edits, 30 deletes)?

Per cycle 102 smoke-not-predictive 7-anchor precedent: smoke PERFECT is not guaranteed to reproduce at FULL.

## Hypothesis

H_robust: all 5 probes (delete_leak, edit_acc, kept_acc, side_effect, ECE) pass across all 5 seeds with margins matching smoke (8th anchor reproduces).

H_diverges: 1+ probes regress at FULL — smoke-not-predictive precedent extends to 8th anchor.

## Pre-declared verdicts

- `LANE_C_FULL_PASS` — all 5 probes pass across all 5 seeds.
- `LANE_C_FULL_PARTIAL` — ≥3 of 5 probes pass across all seeds.
- `LANE_C_FULL_KILLED` — ≤2 of 5 probes pass across all seeds.
- `LANE_C_FULL_INCONCLUSIVE` — <3 seeds returned data.

## Method

Reuses `lc.run_one_seed` from `exp_wave14_lane_C_compliance_audit_smoke_v1.py`:
- N=4096, M_facts=100, n_edits=50, n_deletes=30.
- 5 seeds: [17, 23, 31, 41, 53].
- Per seed: 5-probe Mirage verification (delete_leak_max, edit_acc, kept_acc, side_effect_rate, ece_post).
- Aggregate: probe "robust" iff passes across all 5 seeds.

## Acceptance thresholds (from smoke baseline)

- delete_leak_max ≤ 0.05
- edit_acc ≥ 0.90
- kept_acc ≥ 0.90
- side_effect_rate ≤ 0.05
- ECE ≤ 0.10

## Config

- N=1024 smoke (2 seeds), N=4096 full (5 seeds).
- M_facts=100, n_edits=50, n_deletes=30 full.

## Pre-declared interpretation

- **PASS**: Lane C FULL-grounded for substrate-product Demo 2. Strategy promotes cap_map row to FULL-validated. Demo 2 SDK build proceeds.
- **PARTIAL**: Lane C partial FULL; identify which probe regresses (paraphrase_leak? long-tail edit?). Update Demo 2 positioning.
- **KILLED**: 8th smoke-not-predictive anchor. Lane C smoke PERFECT was test-scaffold artifact. Demo 2 reframes substantially.

## Not in scope

- Stretch tests beyond smoke parameter ranges (n_facts > 100, n_edits > 50).
- Adversarial probes (paraphrase, prompt-injection) — separate experiment.
- Cross-substrate transfer.
