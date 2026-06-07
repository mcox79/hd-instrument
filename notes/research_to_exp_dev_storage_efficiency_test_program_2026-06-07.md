# Research -> Exp-Dev: Storage efficiency test program (7 cheap cells + tier-3 follow-on)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Storage efficiency 3x drill + user directive to test all promising paths.

User target: bring per-fact cost from current 286 KB to a range where substrate is 10-100x
worse than LLM parametric memory (not 1000x+). That's roughly 1-10 KB per fact range as
v2 target.

Authorize all of the following. All are CPU laptop scale or local GPU smoke, $0.

## Tier 1: Gates v1 cost reduction (run first; ranked by ROI)

### 1. Sparse-W validation at production N=65,536
- Anchor: storage drill Path B, exp_dev handoff anchor 1
- Test: load M = 16K facts at N = 65,536, sweep sparsification thresholds, measure W
  weight-reduction-vs-retrieval-accuracy curve
- Pass: >= 8x weight reduction with <= 3% retrieval accuracy drop at M/N = 0.25
- Wall: 30 min GPU smoke
- Why now: gates everything downstream

### 2. 4-bit W quantization accuracy test
- Anchor: storage drill Path C
- Test: same M, N as above; replace bf16 W with 4-bit symmetric quantized W; measure
  retrieval quality drop
- Pass: <= 3% retrieval accuracy drop vs bf16 baseline
- Wall: 1 hr GPU smoke
- Why now: second highest single-axis reduction (4x)

### 3. Lower-N substrate test
- Anchor: storage drill Path A
- Test: N = 16,384 + 32,768 vs N = 65,536 at same M/N ratio; compare retrieval and K-hop
  accuracy
- Pass: lower N maintains >= 95% of baseline retrieval and K-hop quality
- Wall: 1 hr GPU smoke
- Why now: 4x reduction; orthogonal to sparse-W

## Tier 2: Cheap and high-promise (run in parallel to Tier 1)

### 4. Source vector PCA compression
- Test: PR/D = 0.16 means only ~10,500 dimensions carry signal. Compress source vectors
  via PCA projection at storage time, decompress at retrieval. Measure quality loss vs
  compression ratio.
- Pass: 4x source-vector compression with <= 2% retrieval quality drop
- Wall: 1 hr CPU
- Reduces source vector cost from 16 KB to ~4 KB per fact

### 5. Content-addressable keys (no explicit key storage)
- Test: derive key vector from fact text via SHA-256 -> bipolar projection; don't store
  the key vector itself. Measure: retrieval still works (key is reconstructable at query
  time)?
- Pass: retrieval quality matches stored-key baseline within 1%
- Wall: 30 min CPU
- Saves 8 KB per fact (half the source vector cost)

### 6. Hybrid sparse-key + dense-value
- Test: store keys at sparse-mode (alpha = 0.005), values dense. Measure retrieval +
  K-hop quality and effective storage cost.
- Pass: retrieval quality within 2% of dense-key baseline at sparse storage
- Wall: 1 hr CPU
- Saves ~7.5 KB per fact (sparse key is ~0.5 KB vs 8 KB dense)

### 7. Forgetting / pruning policy probe
- Test: implement utility-score-based pruning (drop facts not retrieved in last simulated
  N queries). Measure capacity freed and retrieval quality on retained facts.
- Pass: 25%+ capacity freed with retrieval quality > 95% on retained facts at moderate
  pruning rate
- Wall: 2 hr CPU
- Could free 10-50% of effective capacity over time

## Tier 3: Crazy / research-grade (queue subject to drill output)

I'm dispatching a separate 2x drill on the most promising unconventional storage
mechanisms. That drill will identify which tier-3 ideas are worth empirically testing.
The candidates being evaluated:
- Modern Hopfield at reduced dimension (exponential energy function may lower effective N
  floor; storage drill flagged this as the next research direction)
- Delta storage / hierarchical compression (cortex-like predicate templates + sparse
  diffs)
- Holographic / FFT-domain encoding (frequency-space storage)
- Substrate-of-substrates (recursive nesting; different N per level)
- Bloom filter pre-stage for negative facts
- Huffman-style pre-computed codes for common patterns

I'll route a follow-up note with Tier 3 anchor candidates after the drill lands (~25 min).

## Path explicitly NOT to test

**Low-rank W decomposition (Path F from the storage drill) is foreclosed.** At production
load M/N ~ 0.5 the W singular value spectrum is flat (Marchenko-Pastur random matrix
theory). No low-rank structure to exploit. Do not queue any low-rank tests.

## Engineering integration

Stack the validated paths into the v1 spec:

v1 (cheap stack, after Tier 1 + 2 validate):
- Sparse-W (Path B): 10x
- 4-bit quant (Path C): 4x
- Source vector PCA (Path 4): 4x on source half
- Content-addressable keys (Path 5): 2x on source half
- Hybrid sparse-key (Path 6): 16x on key half if content-addressable doesn't work

Conservatively expect v1 stack reduction: ~30-60x on W, ~4-16x on source vectors.
Per-fact cost: ~5-10 KB (was 286 KB). That's the target zone.

v2 (after Tier 3 drill output): another ~5-10x reduction targeting ~500 bytes per fact.

## Decision rules (so you don't have to ask me about every result)

If Tier 1 test 1 (sparse-W production N) HARD-FAILS: pause v1 cost reduction entirely; the
cycle 142 sparse-W validation didn't scale. We need to research why. Flag to me.

If Tier 1 tests 2 and 3 (4-bit quant + lower N) both HARD-FAIL: ship v1 with sparse-W
only. Per-fact cost lands ~30 KB. Marginal improvement vs target. Flag to me.

If any Tier 2 test HARD-FAILS: drop that path from v1, retain the others. Don't block
v1 ship.

If all Tier 1 + Tier 2 tests HARD-PASS: stack into v1 spec immediately. Per-fact cost
projected ~5 KB. Strong v1 demo number.

## Cross-references

- Storage 3x drill: notes/research_drill_storage_efficiency_per_fact_3x_2026-06-07.md
- Storage handoff: notes/exp_dev_handoff_research_storage_efficiency_2026-06-07.md
- v1 plan update: notes/research_to_exp_dev_orchestrator_v1_plan_update_2026-06-07.md
- North star: ~/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md

---

**END.**

**Exp-Dev:** authorize all 7 tier-1+2 tests. Run Tier 1 sequentially (each gates the
next); run Tier 2 in parallel with Tier 1. Report HP/MID/HF per cell to verdict_handler.
Decision rules above tell you when to flag to me vs proceed autonomously.

**User:** all promising paths authorized. Tier 3 crazy paths drill dispatched in parallel.
Per-fact cost target zone (1-10 KB) is achievable if Tier 1 + 2 stack as predicted.
