# Pre-reg: Wave 14 Bet S K-ceiling at N=65536 v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_BetY_V2D_mechanism_revision_2026-05-22.md` (Strategy 13:15 EDT)
**Predecessor:** Bet S validated at N=4096 with K_crit ~ 130-205 (cycle 88).

## Question

At N=65536, with bipolar BSC substrate + Plate-1995 HRR inversion + standard cleanup, what is the maximum K (stored facts) for which all 3 slot directions (subject, relation, object) still recall above 0.85?

V2.D mechanism revision (Strategy 13:15) drops modern dense AM and asserts substrate verifies via N scale-up: Bet S K-ceiling at N=4096 → 19× at N=65536 (~2487 predicted per cycle 88 K_crit theory).

## Hypothesis

H_scale: K_crit(N=65536) ≥ 1000. Substrate's HDC capacity scales linearly with N; the K=130 ceiling at N=4096 should rise to ≥1000 at N=65536.

H_null: K_crit stays at ~200 or lower — substrate does NOT scale, contradicting V2.D pivot.

## Pre-declared verdicts

- `BET_S_N65K_PASS` — K_crit ≥ 1000 (substrate scales as V2.D predicts).
- `BET_S_N65K_PARTIAL` — 500 ≤ K_crit < 1000.
- `BET_S_N65K_KILLED` — K_crit < 500 (V2.D Phase 1 sub-test fails).
- `BET_S_N65K_INCONCLUSIVE` — metric collection error.

## Method

Reuses `bets.run_one_K` from validated `exp_wave14_betS_pattern_completion_v1.py`:
- num_entities=200, num_relations=50 (held fixed).
- K_sweep ∈ {200, 500, 1000, 2000, 3000}.
- 60 trials/K, 2 seeds {17, 23}.
- PASS per slot at 0.85 (same as N=4096 baseline).

K_crit = max K where min(subject_acc, relation_acc, object_acc) ≥ 0.85.

## Acceptance thresholds

- 0.85 per-slot acceptance matches N=4096 baseline.
- 1000 PASS threshold = 5× the N=4096 K_crit (sublinear-but-substantial scaling).

## Config

- N=4096 smoke, 65536 full.
- K_sweep full: [200, 500, 1000, 2000, 3000].
- seeds full: [17, 23].
- Smoke: K_sweep=[50, 200], seeds=[17].

## Pre-declared interpretation

- **PASS**: substrate scales to N=65536 on Bet S. V2.D Phase 1 sub-test 1 of 5 PASS. Next: Bet C, Bet A, multi-hop, Bet V at N=65536.
- **PARTIAL**: substrate scales partially. Investigate whether N=65536 needs codebook orthogonalization (Kerdock).
- **KILLED**: substrate doesn't scale on Bet S. V2.D revision premise weakened; update Strategy.

## Memory cost estimate

At N=65536: entity codebook (200 × 65536 bits) ~ 16 MB; M_S bundle = 65536 bits ~ 8 KB; per-query matmul = 200 × 65536 ~ 13M ops. Memory fits comfortably in 16GB VRAM (unlike full Hopfield W which is N² = 17GB at fp32).

## Not in scope

- Kerdock codebook (random BSC per Bet S baseline).
- Multi-hop chains (separate experiment).
- Joint capacity with other primitives (Lane D capacity stress covers that).
