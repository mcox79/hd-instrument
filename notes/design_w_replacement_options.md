# Design Doc: Replacing the W Layer with Resonator-Based Prediction

Drafted 2026-05-18 while Wave 14.B bundle sweep + Wave 4.5 v3 run in
background. Purpose: enumerate concretely what "replace W with
resonator decomposition" could mean, identify the equations and
training loops, and decide which (if any) variants are worth coding
once Wave 14.B characterization completes.

This is a paper exercise, not an implementation. The goal is a
reusable strategic map regardless of how 14.B turns out.

## Current architecture (baseline)

```
ctx_t = sum_{k in [0..K-1]} byte_atoms[byte_{t-k-1}] (*) pos_atoms[k]
        # bundle of last K bytes, each bound to its position

P(byte = y | ctx) = softmax_y(beta * (W ctx) . byte_atoms[y])
                  # cosine score against codebook, temperature beta

W update (delta rule):
W <- (1 - decay) W + alpha * (byte_atoms[target] - W ctx) ctx^T

Pool branch:
P_pool(y | ctx) = sum_{i in pool} sim(ctx, ctx_i) * 1[label_i = y]
P_final = alpha * P_pool + (1 - alpha) * P(.|ctx via W)
```

W contains all learned statistics. N=4096 -> 16.7M floats.

## Option A: Pure retrieval with decomposition

**Idea:** drop W entirely. Use the pool as the only source of
predictions. 14.B decomposition extracts structural parts of each
retrieved entry, recombines for prediction.

**Inference equations:**

```
For new ctx_t:
  candidates = top_M_similar(ctx_t, pool)  # M most-similar stored ctx
  For each (ctx_i, target_i) in candidates:
    (atoms_i, slots_i) = decompose_14B(ctx_i)  # K-tuple of atoms + positions
  predicted_atoms = aggregate(atoms_i ...)   # vote or weighted combine
  predicted_targets = aggregate(target_i ...) weighted by similarity
  return predicted_targets
```

**Training:** none. Just populate the pool with (ctx, target) pairs
as data streams in.

**Pros:**
- Zero parameters beyond the pool.
- Trivially continual: append-only.
- Fully interpretable: every prediction traces to specific stored
  examples + their decompositions.
- Decomposition discovers which slots of similar bundles tend to
  share atoms across episodes -> implicit feature extraction.

**Cons:**
- Pool size bounds capacity. To match W's effective capacity at
  N=4096, pool needs to store ~N^2 / N = N = 4096 distinctive
  bundles minimum; realistically 10-100x that. Memory grows linearly.
- Prediction quality saturates at retrieval-set ceiling. No
  generalization beyond observed bundles.
- Latency: top-M search + M decompositions = O(M N + M * resonator_cost)
  per prediction. Resonator cost is iterations * restarts * N. For
  M=8, restarts=8, iters=20: ~10K N-dim ops per prediction. vs. one
  N x N matmul for W (16M ops). Comparable, perhaps slower.

**Expected perplexity vs. current W:** WORSE by 0.2-0.8 bpc.
This is the weakest option.

**Decision criterion:** never the primary system; possibly a
**diagnostic baseline** for "how much does W actually compile beyond
raw retrieval?"

## Option B: Pattern library replaces W

**Idea:** use 14.B across the training set to discover recurring
sub-bundles. Those become a "discovered alphabet." Replace W's
implicit pattern store with an explicit, interpretable library.

**Training equations:**

```
Phase 1 (decompose):
  for each ctx_t in training set:
    parts_t = decompose_14B(ctx_t)  # (a_1, ..., a_K) at known positions

Phase 2 (cluster recurring 2-atom co-occurrences):
  pair_counts: dict[(atom_i, pos_i, atom_j, pos_j) -> int] = {}
  for each parts_t:
    for each (a_i, p_i), (a_j, p_j) in pairs(parts_t):
      pair_counts[(a_i, p_i, a_j, p_j)] += 1

  pattern_library = top_L_pairs_by_count
                  = [PatternBundle(a_i (*) p_i + a_j (*) p_j), target_freq]

Phase 3 (predict via pattern lookup):
  for new ctx:
    matching_patterns = [p for p in pattern_library
                         if sim(ctx, p.bundle) > tau]
    P(byte = y | ctx) = weighted_vote(p.target_freq for p in matching_patterns)
```

**Pros:**
- Patterns are interpretable: you can list "what compositions did
  the system find?"
- Continual: new patterns can be added without retraining.
- Compositionally extensible: new bundles built from known patterns
  inherit predictions.

**Cons:**
- Pattern library size grows. For byte-LM with 256-byte vocab and
  K=4 positions, the number of distinct (atom, position) pairs is
  256 * 4 = 1024. Pairs of pairs: 1M. Most are spurious; need to
  prune by frequency.
- Loses information that doesn't decompose cleanly into recurring
  pairs. Single-occurrence patterns evaporate.
- Equivalent to ngram frequency counting at the bundle level -
  unless decomposition discovers STRUCTURAL patterns (e.g., "any
  byte at pos 0 followed by byte X at pos 1") that raw substring
  counting can't see.

**The bet:** does 14.B decomposition discover structural patterns
that substring frequency counting cannot? This is the core empirical
question. If yes: option B has a meaningful contribution. If no:
it's a worse n-gram model.

**Expected perplexity vs. current W:** WORSE by 0.1-0.4 bpc on byte-LM.
Wins on continual learning, interpretability, compositional
generalization (uncountable in standard byte-LM metrics).

**Decision criterion:** explore in a toy experiment after 14.B sweep
lands. Compare perplexity AND interpretability AND continual-learning
behavior. Decide based on the multi-axis comparison, not perplexity
alone.

## Option C: Hierarchical decomposition stack

**Idea:** stack option B recursively. Level-1 patterns are 2-atom
decompositions. Level-2 patterns are pairs of level-1 patterns
(themselves bundles). Continue until convergence.

**Training equations:**

```
Initialize: level_0_atoms = byte_atoms (256 atoms)

For level in [1, 2, 3, ...]:
  for each pair (a_i, a_j) co-occurring in observed bundles:
    pair_bundle = a_i (*) p_left + a_j (*) p_right
    if count(pair_bundle) > threshold:
      new_atom = hash(pair_bundle)
      level_atoms[level].append(new_atom)
      # Replace pair occurrences in training set with new_atom.

Stop when no new patterns exceed threshold.
```

This is **VSA-implemented BPE**, but the merging rule is determined
by decomposition algebra (which compositions are valid bundles)
rather than literal substring frequency.

**Pros:**
- Multi-scale: short-range (byte pairs) AND long-range
  (paragraph-level) patterns in one hierarchy.
- Connes-Kreimer tree algebra is a natural mathematical home for
  this (each tree IS a hierarchical decomposition).
- Patterns themselves become composable bundles -> a recursive
  pattern algebra.

**Cons:**
- Engineering complexity: managing the hierarchy, the merge rule,
  the inference traversal.
- Risk of pathological merging (e.g., all atoms collapse into one).
  Needs careful threshold and stopping criteria.
- Computational cost: training-time hierarchy construction is
  expensive (multiple passes over corpus).

**Expected perplexity vs. current W:** uncertain. Could be SIMILAR
or slightly BETTER if hierarchical patterns capture long-range
structure W misses. Could be WORSE if quantization to discrete
patterns loses information.

**Decision criterion:** revisit only if option B's toy comparison
shows decomposition discovers structural patterns. This is Wave
14.C territory.

## Option D: Hybrid - W stays, 14.B feeds it

**IMPORTANT correction (noted 2026-05-18 after first draft):**

The naive form of Option D — "decompose ctx and feed parts to W" —
is TRIVIAL in our setup. We construct ctx ourselves from observed
bytes, so decomposing it just hands back the byte identities we
already had. No new information.

The real non-trivial Option D requires 14.B to discover something
we don't already have. Two viable forms:

**D.1: Pattern-augmented features.** Build a pattern library from
14.B applied across MANY stored bundles in the pool (per Option B).
Augment ctx with binary indicators: "does this ctx match pattern P
in the library?" for each P. Train W on enriched_ctx =
concat(ctx, pattern_indicators).

```
Phase 1 (pattern discovery via 14.B across pool):
  pattern_library = mine_recurring_subpatterns(pool, 14B_decompose)

Phase 2 (training with augmented features):
  for each (ctx_t, target_t):
    indicators_t = [int(ctx_t matches pattern_p) for p in library]
    enriched_ctx_t = concat(ctx_t, indicators_t)
    W <- delta_rule_update(enriched_ctx_t, target_t)
```

This is meaningful because pattern matching is a NEW signal —
recurring structure across the pool that W can't see in a single
ctx alone.

**D.2: Discovered-atom codebook expansion.** From 14.B mining,
identify subpatterns that should themselves be treated as atoms.
Add them to the codebook (extending byte_atoms with "concept
atoms"). Bind these to virtual positions. Now ctx can include
not just byte atoms but compositional atoms representing
discovered structural features.

```
Phase 1: discover concept atoms = recurring 2-atom co-occurrences
  in stored bundles.
Phase 2: extend codebook = byte_atoms + concept_atoms
Phase 3: at training time, include concept atoms in ctx when their
  trigger pattern appears.
```

This is closer to BPE-via-decomposition (Option C) but doesn't
require a full hierarchical stack.

**Pros:**
- Conservative: doesn't bet against W. Just feeds richer signal in.
- W's compiled-statistics advantage stays.
- Compatible with current architecture - minimal rewrite.
- If 14.B works only partially (76% pair recovery like Wave 13.3),
  the partial signal is still useful as a feature.

**Cons:**
- Dimensionality blow-up: enriched_ctx is K*N or 2*N dims; W
  becomes N x (K*N) or N x 2N. More parameters, more computation.
- Adds dependency: prediction pipeline now requires 14.B to run
  per-bundle at training AND inference time. Latency cost.
- If 14.B has high failure rate at certain bundle sizes, the
  feature signal is noisy and may hurt.

**Expected perplexity vs. current W:** POSSIBLY BETTER by 0.05-0.15
bpc IF decomposition extracts useful structural info. POSSIBLY
WORSE if the feature is too noisy. Multi-seed experiment required.

**Decision criterion:** the actual interesting bet for perplexity.
Pursue if option B shows decomposition is reliable AND adds
information not already in raw bundle. Or pursue directly if 14.B
sweep is favorable (wide operating envelope at K=32).

## Decision tree

```
After Wave 14.B sweep lands:

  IF bundle sweep shows narrow envelope (B <= 4 only):
    -> 14.B is a niche primitive, not architecture-shaping
    -> Skip ALL replacement options
    -> Keep current W as primary
    -> 14.B becomes optional memory-decomposition tool

  ELIF sweep shows medium envelope (B up to ~16, K=32):
    -> Worth toy comparison on Option B
    -> If structural patterns discovered: pursue Option D
    -> If only frequency-based patterns: file as interpretability tool

  ELIF sweep shows wide envelope (B = 32+, K = 32):
    -> Pursue Option D immediately (hybrid)
    -> Build Option C (hierarchical) as the next research wave
    -> Option B becomes the interpretability baseline
```

## What we ARE NOT doing

- Full system rewrite. Even if 14.B is spectacular, current W stays
  as the prediction engine until a replacement is empirically
  validated.
- Premature commitment to a replacement architecture before
  evidence.
- Letting "interesting capabilities" override "competitive
  perplexity." Capability axes are real but they don't substitute
  for the perplexity number that's our primary benchmark.

## Open questions for after 14.B sweep

1. Does 14.B work at bundle sizes equivalent to our actual ctx
   bundle (K=4 in current byte-LM)? If yes, option D is in scope
   today. If no, options A/B/C are speculative.

2. How fast is decomposition per bundle? If >100ms per inference
   call, real-time prediction is dead. If <10ms, all options viable.

3. Do discovered patterns match human intuitions about byte-LM
   structure (common bigrams, word boundaries)? If yes:
   interpretability win is real. If no: decomposition is doing
   something different from frequency counting (interesting but
   potentially less useful).

4. Does decomposition robustness degrade gracefully under noise
   (atom drift, atom contamination)? Continual learning will
   introduce both. Needs a robustness test.

## Cost estimates if pursued

- Option A toy: 1 day (mostly retrieval infra)
- Option B toy: 2-3 days (pattern mining + lookup)
- Option C: 1-2 weeks (hierarchy + Connes-Kreimer)
- Option D: 2-4 days (W training on enriched input)

Option D is the highest expected-value bet. Option A is the
cheapest baseline. Option C is the highest-ceiling but riskiest.
Option B is the most informative on the underlying question
"what does decomposition discover?"

## Default plan (subject to sweep results)

1. Wave 14.B bundle sweep finishes -> read results.
2. If sweep is favorable at B=4-16: build Option B toy first
   (cheap and informative).
3. After Option B toy: build Option D in parallel with the
   continual-learning integration of 14.B.
4. Defer Option C until we have evidence one of B or D is real.
