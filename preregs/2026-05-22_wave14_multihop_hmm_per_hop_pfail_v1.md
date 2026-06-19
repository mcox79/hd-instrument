# Pre-reg: Wave 14 Multi-hop HMM Per-Hop p_fail v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_HMM_BCJR_phase1_validation_2026-05-22.md` (Strategy 20:55 EDT) — Test 3.

## Question

What is the substrate's empirical per-hop failure rate p_fail at N=65536, K=100? HMM cascade theory predicts p_fail ≈ 0.03 (since 0.97^50 ≈ 0.218 matches cycle 121 empirical 0.217).

## Hypothesis

H_confirms: p_fail ∈ [0.025, 0.035] — HMM cascade-error theory empirically validated.

H_higher: p_fail > 0.035 — substrate has more per-hop noise; HMM model undercounts.

H_lower: p_fail < 0.025 — substrate has less per-hop noise; HMM overcounts (multi-hop ~0.22 must come from other source).

## Pre-declared verdicts

- `PFAIL_CONFIRMS` — p_fail ∈ [0.025, 0.035].
- `PFAIL_HIGHER` — p_fail > 0.035.
- `PFAIL_LOWER` — p_fail < 0.025.
- `PFAIL_INCONCLUSIVE` — metric collection error.

## Method

Run 10⁴ single-hop chain queries at N=65536, K=100 facts in bundle M:
1. Pick 2 random entities (start, target) and 1 random relation.
2. Build M = sign(triple(s, r, o) + 99 distractor triples).
3. Probe = M · (entity[s] · rel[r]); pred = argmax(entity_atoms @ probe).
4. Count correct = pred == target.
5. p_fail = 1 - acc_1hop.

## Acceptance thresholds

- [0.025, 0.035] CONFIRMS band: ±0.005 around HMM's 0.03 prediction.
- 10⁴ trials gives ±0.003 95%CI on p_fail estimate — sufficient resolution.

## Config

- N=8192 smoke, 65536 full.
- num_entities=200, num_relations=20, num_facts=100.
- n_trials=10000 full, 200 smoke.
- Single seed=17.

## Pre-declared interpretation

- **CONFIRMS**: HMM cascade-error model validated across third axis (after Tests 1 + 2). Combined three-test agreement = first quantitative substrate-physics framework match across 3 mechanism-diagnosis attempts.
- **HIGHER/LOWER**: HMM cascade-error theory is qualitatively right but quantitative gap. Refine per-hop noise model.

## Cost

10⁴ 1-hop trials at N=65536: ~5 GPU-min per Research estimate.

## Not in scope

- Multi-K sweep (single K=100).
- Per-relation p_fail variation (single relation per trial).
- Different bundle sizes.
