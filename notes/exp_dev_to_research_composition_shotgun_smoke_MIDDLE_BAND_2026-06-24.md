# exp_dev -> Research: composition shotgun smoke LANDED (MIDDLE_BAND_SMOKE_TOO_SMALL)

**Date:** 2026-06-24
**Anchor:** `substrate_composition_separation_shotgun_smoke_v1`
**Verdict:** MIDDLE_BAND_SMOKE_TOO_SMALL
**Commit:** f64e6f0b (cell + prereg + smoke metrics on origin/main)
**Wall:** ~12 min CPU pure-numpy local
**Type:** cell_land + next-step routing ask

[from=exp_dev] [type=cell_land] [verdict=MIDDLE_BAND]

## Headline

Per USER directive "shotgun smoke the composition question," authored 9-arm
shotgun cell testing 8 separation strategies for cf-RPE x STDP same-W
composition collapse. Smoke completed clean (V=300 N_DIM=2048 N_TRAIN=20k
3 seeds pure-numpy CPU ~12 min). All primitives operational; verdict_lint
PASS; 6/6 formula self-tests PASS.

**The collapse did NOT reproduce at smoke scale.** NAIVE-BASELINE delta=0.0442
just under the 0.05 pre-reg threshold for confirming collapse. So no rescue
arm's "lift" is interpretable -- there is no collapse to rescue.

## Per-arm BPC means (3 seeds; uniform_bpc = log2(300) = 8.23)

| Arm                                | bpc_mean | bpc_cv | top1_mean | vs_baseline | vs_naive |
|------------------------------------|---------:|-------:|----------:|------------:|---------:|
| ARM_BASELINE_CFRPE_ALONE           |  2.9310  | 0.0138 |   0.5790  |    --       |   --     |
| ARM_NAIVE_CFRPE_PLUS_STDP          |  2.9752  | 0.0070 |   0.5765  |   +0.0442   |   --     |
| ARM_ORTHOGONAL_PROJECTION          |  2.9541  | 0.0121 |   0.5757  |   +0.0231   | -0.0211  |
| ARM_TIME_SEPARATION                |  2.9632  | 0.0170 |   0.5763  |   +0.0322   | -0.0120  |
| ARM_FREQ_SEPARATION                |  2.9819  | 0.0062 |   0.5723  |   +0.0509   | +0.0067  |
| ARM_REPLAY_BASED                   |  2.9908  | 0.0117 |   0.5760  |   +0.0598   | +0.0156  |
| ARM_BANK_SEPARATION                |  3.0071  | 0.0248 |   0.5728  |   +0.0761   | +0.0319  |
| ARM_SEQUENTIAL_CONSOLIDATION       |  3.1724  | 0.0399 |   0.5063  |   +0.2414   | +0.1972  |
| ARM_SUBSPACE_SEPARATION            |  3.2887  | 0.0231 |   0.5265  |   +0.3577   | +0.3135  |

Lower BPC = better. Negative vs_naive = arm beats naive compose. Negative
vs_baseline = arm beats cf-RPE alone. All cv <= 0.04 (well under 0.10 smoke
tolerance; well under 0.05 cert standard).

## Discriminator information available (despite no reproduced collapse)

The smoke DOES discriminate among arms, just not the way HARD_PASS expected:

**Clearly capacity-REDUCING separation strategies (drop arms; not promotable):**
- ARM_SUBSPACE_SEPARATION (+0.36 BPC over baseline; top1 drops to 0.527) --
  splitting W into two half-rank sub-blocks loses too much capacity at smoke
- ARM_SEQUENTIAL_CONSOLIDATION (+0.24 BPC; top1 drops to 0.506) -- freezing
  cf-RPE then adding STDP on top is worse than NAIVE composition

**Near-baseline cluster (do not destroy capacity; collapse not yet stressed):**
- ARM_ORTHOGONAL_PROJECTION (PCGrad-style; -0.021 vs naive at smoke; cv=0.012)
- ARM_TIME_SEPARATION (even/odd step alternation; -0.012 vs naive; cv=0.017)
- ARM_FREQ_SEPARATION (high/low freq routing; +0.007 vs naive; cv=0.006)
- ARM_REPLAY_BASED (CLS-style one-way replay; +0.016 vs naive; cv=0.012)
- ARM_BANK_SEPARATION (two W; avg-logits readout; +0.032 vs naive; cv=0.025)

**Reference arms (sanity rails):**
- ARM_BASELINE_CFRPE_ALONE at 2.93 BPC, well under HARD_FAIL_PROVENANCE floor
  of 7.73; cf-RPE primitive operational
- ARM_NAIVE_CFRPE_PLUS_STDP only +0.044 over baseline at this scale; collapse
  signal is sub-threshold

## Intuitive frame

The "5 chefs in one pot" collapse needs LOAD (longer training, bigger vocab,
denser bigram transitions) to manifest. At smoke (V=300, only 300 steps,
20k tokens of synthetic Zipf bigram), the substrate hasn't been pushed hard
enough for STDP's antisymmetric "temporal coherence" updates to actually
DAMAGE cf-RPE's "task-supervised" updates -- they coexist quietly. At A1
production scale (V=4000, 1000 steps, 100k tokens of text8), STDP+cf-RPE on
same W produces +0.116 BPC regress -- the chefs interfere.

What smoke IS telling us:
- 2 of 7 separation strategies (SUBSPACE / SEQUENTIAL) are DECISIVELY BAD
  at any scale (capacity-reducing structurally; not promotable)
- 5 of 7 separation strategies don't destroy capacity (TIME / BANK / FREQ /
  REPLAY / ORTHOGONAL_PROJECTION); whether any of them RESCUE the collapse
  is untestable here

## Path forward (3 options; ask Research to choose)

### Option A: Production-scale dispatch of the 5 near-baseline arms (RECOMMENDED)

Re-author shotgun at production config (V=4000, N_DIM=8192, N_TRAIN=100k,
text8 corpus + word2vec encoder + sparse-bipolar projection per A1 pipeline)
with the 7 arms: BASELINE + NAIVE + the 5 promising (TIME / BANK / FREQ /
REPLAY / ORTHOGONAL_PROJECTION). Drop SUBSPACE + SEQUENTIAL (smoke decisively
showed they reduce capacity).

- Routing: overnight_queue (GPU; A1 cell already uses torch+CUDA pipeline)
- Push needed -> route via hdi_orchestrator (harness-DENIED to me)
- Estimated wall: ~3-5h on GPU (7 arms x 3 seeds x ~10-15 min per arm-seed
  at production scale)
- Decisive: at production scale the A1 collapse IS reproducible (7.0888 ->
  7.2044 in A1 metrics); any of the 5 arms beating naive by >= 0.05 BPC
  AND beating baseline by >= 0.03 BPC = HARD_PASS chain-grade-eligible
  architecture
- This is the smallest-scope production cell that resolves USER's question

### Option B: Re-author at intermediate smoke (cheaper; less decisive)

Re-author with V=1000, N_DIM=4096, N_TRAIN=50k, N_STEPS=500 -- larger smoke
that might reproduce collapse without going to production. ~30-45 min CPU.

- Risk: still might not reproduce collapse (the collapse threshold for cf-RPE
  vs naive might be scale-dependent in non-trivial ways)
- Cost: ~30-45 min CPU; cheaper than GPU production but slower than this smoke
- Worth doing only if we want a cheaper-than-production but more-than-smoke
  diagnostic before committing GPU time

### Option C: Direct production cf-RPE+STDP NAIVE-only re-test first (cheapest decisive)

Skip the shotgun for now; dispatch a 2-arm production cell (BASELINE_CFRPE_ALONE
+ NAIVE_CFRPE_PLUS_STDP only) at A1 config to RE-CONFIRM the collapse
reproduces at production. ~1-2h GPU. If naive collapse confirmed -> Option A.
If naive collapse doesn't reproduce in fresh cell -> the A1 metrics were
config-specific and the whole composition-collapse premise needs re-examination.

This is the most-information-per-GPU-minute option but adds a serialization
step before the shotgun.

## My (cell-author) recommendation

**Option A** -- production-scale 7-arm dispatch via hdi_orchestrator. The 5 near-baseline
arms ALL deserve their fair production test; the 2 capacity-reducers are
already excluded; the BASELINE + NAIVE references provide the collapse anchor.
This is one well-scoped cell, not 7 separate ones, and matches the USER's
"shotgun" intent. Spawn budget cost: 1 spawn (orchestrator dispatch ask).

If Option A is approved, I can re-author the production-scale variant as a
direct fork of this cell with the A1 encoder pipeline (word2vec + sparse-bipolar)
swapped in for the smoke synthetic encoder. The arms / verdict / lint already
work; the change is purely encoder + corpus + scale.

## References

- `experiments/exp_substrate_composition_separation_shotgun_smoke_v1.py` (cell; f64e6f0b)
- `preregs/2026-06-24_substrate_composition_separation_shotgun_smoke_v1.md` (pre-reg)
- `data/exp_substrate_composition_separation_shotgun_smoke_v1_smoke/metrics.json` (smoke result)
- A1 collapse provenance: `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json` (cf-RPE 7.0888 vs naive 7.2044, +0.116 regress)
- Heterogeneous super-additive precedent at N=512: `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json`
- PCGrad ANCHOR 2 (currently in flight; remote_cpu): `preregs/2026-06-24_substrate_pcgrad_cfrpe_stdp_v1.md`
- Composition store-mine inventory: `notes/director_composition_store_mine_inventory_2026-06-24.md`

## What I am NOT claiming

- I am NOT claiming any separation strategy WORKS or FAILS (no reproduced
  collapse to test against)
- I am NOT claiming the shotgun-smoke methodology is broken (smoke ran clean;
  primitives validated; lint + selftests PASS)
- I am NOT claiming 7 strategies are equivalent (clear discrimination on
  SUBSPACE / SEQUENTIAL as capacity-reducers; 5 others cluster near baseline)
- I AM claiming that smoke V=300/N_DIM=2048/N_TRAIN=20k is below the A1
  collapse-stress threshold and a larger scale is required to discriminate
  rescue arms

## Waiting on

Research decision on Option A/B/C. I can re-author + smoke a production
variant within one cell-author cycle if Option A approved.
