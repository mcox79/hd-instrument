# Pre-registration: wave14t_multihop_v3

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14t_multihop_v3.py](../experiments/exp_wave14t_multihop_v3.py)
Priority source: [active_priorities.md](../notes/active_priorities.md) E4
Author: experiment_dev session, pipeline tick 5

## Why

`wave14e_multi_hop_v2` reported acc_1hop=0.98 but tested only hop depths
{1, 2, 3, 5} on a single seed. Bet-4-class capability claim ("multi-hop
reasoning works on the substrate") requires the hop-depth-sweep test
listed in active_priorities as E4: {1, 5, 10, 25, 50}. Substrate theory
(per v2's docstring): at N=4096, F=50, per-hop detection margin is
sqrt(N/F) ≈ 9.0σ; per-hop error < 1e-8 in the limit → 50-hop chains
should remain viable. v3 tests this prediction directly.

Two things v2 didn't have that v3 adds:
1. Hop-depth sweep through 50, not stopping at 5.
2. Multi-seed (3 seeds) + per-depth N_TRIALS=50 for statistical power.
3. Per-hop retention rate computed from the accuracy curve, compared to
   the theoretical prediction.
4. Verdict logic + multi-probe schema + gate compliance.

## Hypothesis

At N=4096, fact-base M with NUM_FACTS=100, per-hop cleanup against an
entity codebook of 200 atoms:

- 5-hop accuracy ≥ 0.85
- 10-hop accuracy ≥ 0.70
- 25-hop accuracy ≥ 0.40
- 50-hop accuracy ≥ 0.15
- Per-hop retention rate (geometric mean from the accuracy curve) ≥ 0.95
  per hop, consistent with the theoretical detection-margin prediction.

## Multi-probe success criteria (all required for PASS)

1. acc_1hop ≥ 0.98 (replicates v2 finding; if not, test setup is wrong)
2. acc_50hop > 0.10 (genuine deep-chain capability)
3. Across 3 seeds, std of per-hop retention < 0.05 (capability is stable)

**Discarded as redundant** during script implementation: a separate
`retention ≥ 0.90` check and a `log-decay slope ≥ -0.05` check were
folded out because they are mathematically implied by criterion 2
(if acc_50 > 0.10 then retention = acc_50^(1/50) ≥ 0.955; slope follows
similarly). Reporting both metrics in the summary regardless, for
audit. Verdict logic uses only the three non-redundant criteria.

## Kill criterion

acc_5hop < 0.50 in any seed → the v2 "PASS at 5-hop" finding doesn't
replicate; routes to test-setup audit before drawing depth conclusions.

OR acc_50hop ≤ 0.02 AND per-hop retention < 0.85 → cleanup-budget
tradeoff math doesn't carry the substrate through 50 hops; multi-hop
capability is bounded at some shorter depth (per-hop retention determines
the cliff location).

## Verdict labels (5)

- `MULTIHOP_50HOP_VALIDATED` — all 5 criteria pass; 50-hop reasoning works
- `MULTIHOP_DECAY_AT_<D>` — depth at which accuracy first falls below 0.10;
  partial credit
- `MULTIHOP_V2_NOT_REPLICATED` — kill criterion 1 (acc_5hop < 0.5 anywhere);
  audit setup before drawing conclusions
- `MULTIHOP_CATASTROPHIC_DECAY` — kill criterion 2 (per-hop retention < 0.85);
  cleanup-budget insufficient
- `MULTIHOP_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. `oracle.assert_baseline_high("acc_1hop_smoke", acc_1hop_smoke, 0.85)` —
   1-hop must work in smoke (else fact-base storage is broken).
2. `oracle.assert_in_range("entity_codebook_pairwise_max",
   max_pairwise_ip_entities, (0.0, 0.20))` — entity atoms must be
   near-orthogonal in expectation (random ±1 at N=512: max IP ~ 5/√512
   ≈ 0.22). Catches a broken codebook.

## Pre-mortem (3 failure causes)

1. **Per-hop cleanup error accumulates exponentially**. With per-hop rate
   p, K-hop accuracy is p^K. v2 implicitly assumed p≈1 from theory; if
   p actually ~0.85 (consistent with v2's acc_3hop ≈ 0.6), then 50-hop
   accuracy ≈ 0.85^50 ≈ 2.9e-4 — effectively zero. Mitigation: report
   per-hop retention; verdict `CATASTROPHIC_DECAY` triggers on this.
2. **Entity codebook collisions at NUM_ENTITIES=200**. At N=4096, the
   max pairwise IP for 200 random ±1 atoms is bounded by ~sqrt(2 log
   200)/sqrt(N) ≈ 0.05; safe. But if NUM_FACTS=100 facts ALL bind
   different entity pairs, the fact-base M has very mixed signal.
   Mitigation: smoke oracle 2 catches abnormal codebook structure.
3. **Distractor facts in M leak into the chain query**. A chain query
   `M * (A * R1)` mostly returns the chain's next entity, but distractor
   facts contribute noise. At F_DISTRACTOR=50, noise magnitude is
   bounded but may dominate at deep chains. Mitigation: per-hop
   retention number directly measures this; verdict captures it.

## Operational definition

- N = 4096 (substrate width)
- NUM_ENTITIES = 200 (entity codebook size)
- NUM_RELATIONS = 20 (relation codebook size)
- NUM_FACTS = 100 (size of fact-base M; chain transitions + distractors)
- HOP_DEPTHS = [1, 5, 10, 25, 50]
- N_TRIALS per depth = 50 (independent chains per depth per seed)
- SEEDS = [17, 23, 31]
- BSC binding: triple_i = sign(subj_i * rel_i * obj_i)
- Fact-base: M = sign(Σ triple_i)
- Multi-hop query at depth K: starting from chain[0], iteratively
  cleanup `M * (current * relation_k)` against entity_codebook for
  k in 0..K-1; check if final cleanup == chain[K]

## Cited mechanism / sources

1. Plate 1995, Kanerva 2009: HRR/BSC binding + cleanup primitives.
2. wave14e_multi_hop_reasoning_research (already in repo): triple-binding
   theory with per-hop margin calculation.
3. wave14e_multi_hop_v2 (own work): the v2 result this experiment
   extends to deeper hops.

## Expected runtime

- Smoke (N=512, depths=[1, 5], NUM_FACTS=20, NUM_TRIALS=5, 1 seed):
  ~3-6s on CPU
- Full (N=4096, depths=[1, 5, 10, 25, 50], NUM_FACTS=100, NUM_TRIALS=50,
  3 seeds): estimated 1-4 min on GPU. Cleanup ops are cheap matmuls
  (NUM_ENTITIES × N) per hop; total ~5 × 50 × 3 = 750 chain queries
  with up to 50 cleanup ops each.

## What product decision this enables

- `VALIDATED` → cap_map row "multi-hop reasoning to 50 hops" added at
  🟢/✅ (depending on stability); a Tier-2 KILLER capability claim
  becomes defensible.
- `DECAY_AT_<D>` → cap_map row added with depth caveat (capability
  works to depth D).
- `CATASTROPHIC_DECAY` → multi-hop is bounded at low depth; product
  story is "single- or low-hop reasoning only" until a cleanup-budget
  improvement lands.
- `V2_NOT_REPLICATED` → audit before drawing conclusions; not a substrate
  finding.
