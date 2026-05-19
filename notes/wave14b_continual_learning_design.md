# Wave 14.B + Continual Learning Integration: Design Doc

Drafted 2026-05-18 after Wave 14.B robustness confirmed across both
bundle-size (B=2..128) and codebook-size (K=32..2048) axes. The
primitive works. Time to test what it enables that nothing else can.

## The actual research question

Standard continual learning measures: how much does a model retain on
old tasks after training on new ones? Our W_frozen mitigation already
gives near-zero forgetting (+0.05 bpc). The interesting question
isn't "does our system forget less?" — it's already there.

The interesting question with 14.B in hand is:

**Does compositional decomposition of stored episodes enable
*generalization* across distribution shifts that no other architecture
can match?**

Specifically: if corpus B contains contexts that share structural
parts with corpus A but no whole episode, can VSA-pool retrieval +
14.B decomposition extract the relevant parts from A episodes and
recombine them for B predictions? Classical pool retrieval can only
return whole episodes by similarity — it cannot disassemble and
recombine.

## The architecture

### Baseline: classical pool

```
Pool entry: (ctx_i, target_i) stored explicitly.
At eval:
  scores_i = cosine(ctx_query, ctx_i)
  P(target | query) = softmax(scores) . one_hot(target_i)
```

Stored value is just a byte label. Retrieval is whole-episode by
similarity. Cannot recombine parts.

### Test condition: VSA-pool

```
Pool entry: bundle_i = ctx_i + byte_atom[target_i] * pos_atom[K]
            (one bundle per episode, target encoded in-bundle)

At eval:
  scores_i = cosine(ctx_query, bundle_i - position-K-contribution)
            or more cleanly via subspace projection
  Retrieved bundles: top-M by score
  For each retrieved bundle:
    extracted_atom = decompose_14B(bundle_i, expected positions)[K]
    target_i_hat = cleanup(extracted_atom, byte_atoms)
  P(target | query) = aggregate over retrieved targets
```

Stored value is a single bundle containing both ctx and target. The
14.B decomposition recovers any slot from the bundle. This means we
can also do **partial query**: given parts of ctx, decompose the
bundle to find what's in the missing slot.

### The compositional capability

The unique thing VSA-pool can do, classical pool cannot:

```
Given: query has 3 of 4 ctx atoms known, 1 unknown.
       (E.g., we know bytes at positions 0, 1, 2 but want predictions
       that fit the partial context.)

VSA-pool: for each retrieved bundle, decompose, check if the known
  atoms match. If yes: extract the OTHER positions' atoms. This
  allows compositional matching: "find episodes where positions 0
  and 1 match mine; tell me what was at position 3."

Classical pool: scores entire ctx vs entire ctx. Cannot select
  matching by sub-positions.
```

## Experimental design

### Corpora

- **Corpus A**: standard English text. Common bigrams and patterns.
- **Corpus B**: SHUFFLED corpus A at the byte level — same byte
  distribution, but no preserved local context.

This ensures:
- A and B share atoms (same bytes).
- A has structural patterns (recurring bigrams).
- B lacks A's structural patterns.
- Training on B should destroy W's A-knowledge.
- Pool retention is the only mechanism that can hold A-knowledge.

### Phases

1. **Pretrain on A**: standard byte-LM training. Get W_A and pool_A.
2. **Eval on A heldout**: baseline performance metric_0_A.
3. **Continual train on B**: continue training W on B. W_A overwritten
   to W_B. Pool gets B episodes appended (or replaces - tested both).
4. **Eval on A heldout**: post-shift performance metric_1_A.
5. **Compute BWT** = metric_1_A - metric_0_A. More negative = more
   forgetting.

### Conditions

- **C0** (control): no pool. Pure W prediction.
  - Worst BWT expected. ~-0.5 to -1.0 bpc.
- **C1** (baseline): classical pool retained across phase 3.
  - Already-validated W_frozen result: BWT ~ -0.05 bpc.
- **C2** (VSA-pool whole retrieval): pool stores bundles
  (ctx+target encoded), retrieves whole, extracts target via 14.B.
  - Hypothesis: BWT similar to C1.
- **C3** (VSA-pool COMPOSITIONAL retrieval): pool stores bundles,
  retrieves with PARTIAL ctx match (e.g., only positions 0-1 must
  match), extracts target via 14.B from the matched bundles.
  - Hypothesis: BWT BETTER than C1 because more episodes are
    "near-matches" via partial similarity.

### Critical measurement

The headline number is **C3 BWT vs C1 BWT**. C3's compositional
retrieval is the unique 14.B capability — if it doesn't beat C1 on
forgetting OR doesn't enable new behavior (like compositional
generalization to unseen contexts), the integration adds nothing.

### Secondary measurement: compositional generalization

Construct synthetic test set: ctx vectors that have:
- 3 of 4 atoms appearing somewhere in A's pool
- The full 4-atom combination NEVER appearing in A's pool

For each method:
- C1 (classical): scores all 4-atom contexts; best score is the most
  similar whole episode, which is at most 3/4 similar.
- C3 (VSA-pool compositional): can match episode-X for atoms 0,1 and
  episode-Y for atoms 2,3, extract target predictions from each, vote.

Metric: prediction accuracy on these synthetic "compositional" tests.
C3 should win decisively if compositional retrieval works.

## Implementation plan

### Phase A (this session if time allows)

1. **Wave 14.B-CL Phase A: data and baselines.**
   - Load corpus A, build shuffled corpus B.
   - Train baseline W on A (existing exp_wave45_v3 code is fine).
   - Save W_A, pool_A for use in Phase B.

### Phase B (next session)

1. **Wave 14.B-CL Phase B: VSA-pool implementation.**
   - Build VSA-pool data structure: bundles = ctx + target*pos[K].
   - Add 14.B decomposition call at retrieval time.
   - Implement C0, C1, C2, C3 as switchable conditions.
   - Run phases 1-5 of the experimental design.

### Phase C (later)

1. **Wave 14.B-CL Phase C: scaling and ablations.**
   - Vary pool size, K (ctx length), corpus sizes.
   - Stress test: train on 5 sequential corpora, measure cumulative BWT.

## Risks and falsification

- **Risk 1**: 14.B decomposition is too slow at inference time.
  - Mitigation: profile decomposition latency; if >10ms per query,
    redesign with batched parallel decomposition or smaller codebook.

- **Risk 2**: C3 compositional retrieval is no better than C1 because
  partial-ctx matches return noisy / wrong targets.
  - This would falsify the headline hypothesis. The right move:
    redesign with a verification step (retrieved targets must
    self-consistently match the full ctx via reconstruction error).

- **Risk 3**: Implementation complexity exceeds value.
  - Mitigate by aggressive scope cuts. Start with the bare-minimum
    C2 vs C1 comparison. Only build C3 if C2 works.

- **Falsification (pre-registered)**: If C3 BWT ≥ C1 BWT (no
  improvement) AND C3 compositional accuracy ≤ C1 (no new
  capability), Wave 14.B integration is NOT a win for byte-LM.
  Fall back to using 14.B as a memory inspection tool only.

## Why this is the right experiment

This experiment tests whether 14.B unlocks something **no other
architecture has**: structural decomposition of stored memories,
enabling compositional generalization across distribution shifts.

Transformers don't have this: their stored knowledge is in opaque
attention patterns and MLP weights. They cannot decompose old
predictions into reusable parts.

Our W_frozen continual learning already gives strong retention.
14.B adds the compositional layer on top. If C3 beats C1, we have
a capability that's genuinely novel, not just incrementally better.

If it doesn't, we still have the working continual-learning byte-LM
as a contribution. The downside is bounded.

## Estimated effort

- Phase A: 0.5 day (mostly reusing existing code)
- Phase B: 2-3 days (VSA-pool + 4 conditions + measurement)
- Phase C: 1 week (scaling)

Total: ~1.5-2 weeks for a complete result.

## Next concrete step

Start Phase A: load corpora, prepare shuffled-B, train baseline W_A.
This is mostly reuse — the existing exp_wave45 script can be adapted.

While Wave 4.5 v4 finishes on GPU (separate question, separate
loop), Phase A can be implemented locally on CPU since training
data is small.
