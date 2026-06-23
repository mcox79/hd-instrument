# Pre-reg: n11_random_indexing_semantic_v1

**Date:** 2026-06-22
**Anchor:** `n11_random_indexing_semantic_v1`
**Script:** `experiments/exp_n11_random_indexing_semantic_v1.py`
**New primitive:** `hdlab/random_indexing.py` (RandomIndexingEncoder)
**Route:** `remote_cpu_queue` (CPU-only; numpy + char_trigram encoder; no GPU needed)
**Driver note:** `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md`

## Mechanism under test

Substrate-native distributional semantics via Random Indexing (Sahlgren 2005, Kanerva 1988):
forward-only Hebbian co-occurrence accumulator. Each word `w` gets a sparse-ternary HD
index vector `i_w in {-1, 0, +1}^N` (s nonzero entries). The context vector `c_w` accumulates
sums of context-window index vectors as the corpus is streamed; cosine(c_w1, c_w2) reflects
distributional similarity (cat-dog close because they share context words; cat-car far).

Composes with substrate's bipolar bundling (Hebbian sum), HRR cyclic-shift (BEAGLE order
binding per Jones-Mewhort 2007), and Hadamard binding (hub-spoke conjunction with
char_trigram orthographic spoke per Patterson-Lambon Ralph ATL hub-and-spoke 2007).

Zero LLM at any stage. Zero backprop. Pure substrate primitives.

## Arms (Fix #16 discriminator)

| Arm | Mechanism | Hypothesis |
|---|---|---|
| 1. RANDOM_INDEXING_ALONE | Canonical RI (bag-of-context bundling) on text8 in-order | Distributional signal emerges |
| 2. RI_PLUS_BEAGLE_ORDER | RI + cyclic-shift HRR order-binding | Same signal + order info |
| 3. RI_HUB_SPOKE_KGSTORE | RI context vector x char_trigram orthographic (Hadamard bind) | Hub-spoke conjunction preserves signal |
| 4. CONTROL_RANDOM_PERMUTE | RI on position-shuffled corpus (destroys distributional structure) | Ratio collapses to ~1.0 (CAN-FAIL discriminator) |

## Pre-reg HARD bands

**HARD_PASS:** ALL three substantive arms (1, 2, 3) achieve `mean cos(similar_pairs) >= 1.5 * mean cos(dissimilar_pairs)`
AND CONTROL_RANDOM_PERMUTE arm ratio <= 1.1 AND max CV across seeds <= 0.20 AND `n_llm_calls == 0`.

**HARD_FAIL:** ANY substantive arm ratio < 1.1 (no distributional signal)
OR CONTROL arm ratio > 1.3 (probe construction is broken; cannot trust ratios).

**MIDDLE_BAND:** between the two. Per by-construction-saturation discipline, this is
MEASURED_MECHANISM not chain-grade win; Skunkworks adjudicates whether to ship a lever
(N_DIM up, window tuning, BEAGLE-only, or alternative hub-spoke binding).

## Probe set

Handcrafted; substrate-only (no network fetch of WordSim-353/SimLex-999 at runtime,
keeping the substrate-only gate intact). Categories: animals, vehicles, body_parts,
colors, time_words, numbers, weather. Within-category pairs = similar; across-category
pairs = dissimilar. Cap at 100 pairs per side after seed-0 reproducible sampling.

Filtered to text8 vocab at min_count=5 before testing. Smoke must produce >= 20 similar
and >= 20 dissimilar pairs in vocab; otherwise the probe is too sparse and the cell
must be re-scoped (vocabulary fail-fast).

## Config

- Corpus: text8 (data/text8_cache/text8.txt; ~17M tokens). FULL uses entire corpus;
  smoke uses first 200k tokens (~1MB).
- N_DIM = 8192
- sparsity = 10 (~ s/N = 0.001; Kanerva 2009 capacity floor)
- window = 5 (symmetric; standard word2vec-style)
- min_count = 5 (canonical word2vec preprocessing)
- seeds: full = [7, 17, 23], smoke = [0]

## Cost (estimated)

- Smoke: ~3-5 min CPU (3 encoder fits on 200k tokens; 4-arm probe eval).
- Full: 3 seeds x 3 encoder fits (bag, order, ctrl) x text8 ~ 30-60 min per seed wall;
  with per-seed checkpoint, total wall ~ 90-180 min CPU. `--timeout 14400` (4h) for
  safety margin + per-seed checkpoint per PROT-021. PROT-019 floor not triggered
  (no `_n<N>` suffix in anchor name).

## Why this matters (strategic)

Per drill, this is the substrate-native distributional semantics primitive missing for
Path A substrate-as-pseudo-LLM. Predicted downstream impact:

1. Replaces MiniLM-semantic in chat/QA with substrate-native encoder.
2. Validates ATL hub-spoke architecture for substrate (orthographic + distributional spokes).
3. Closes text8 word-bigram gap (~1.13 bits) by 0.3-0.6 bits via semantic-prior next-word.
4. Unlocks full substrate-native chat / QA pipeline (encode = RI, retrieve = KGStore.W,
   reason = multi_hop, generate = g1b).

## Skunkworks structural blockers (baked into cell)

- `_LLM_CALL_COUNTER = [0]` -- substrate-only at all stages (no encode-time LLM either).
- per_unit per seed (multi-seed exhaustive).
- cv computed across seeds in compute_verdict.
- atexit + SIGTERM synthesize from per-seed partials (Fix #11 TODO #9).

## CAN-FAIL discriminator (Fix #16)

CONTROL_RANDOM_PERMUTE arm. The mechanism predicts the corpus-position-shuffled
encoder will lose all distributional signal -> ratio ~ 1.0. If CONTROL ratio > 1.3 we
HARD_FAIL on probe-broken grounds (means our probe leaks signal even without
distributional structure).

## Cites

- Sahlgren, M. (2005). "An Introduction to Random Indexing." TKE 2005.
- Kanerva, P. (1988). "Sparse Distributed Memory." MIT Press.
- Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction..." Cognitive Computation 1.
- Jones, M. N., Mewhort, D. J. K. (2007). "Representing word meaning and order information
  in a composite holographic lexicon." Psychological Review 114(1).
- Patterson, K., Nestor, P. J., Rogers, T. T. (2007). "Where do you know what you know?"
  Nature Reviews Neuroscience 8.
- McClelland, J. L., McNaughton, B. L., O'Reilly, R. C. (1995). "Why there are
  complementary learning systems..." Psychological Review 102.
- CERT 585 (char_trigram_encoder; substrate's orthographic spoke).

## Predispatch check

`python tools/predispatch_check.py n11 random_indexing semantic` -> PROCEED (2026-06-22).
7 prior matches on "semantic" keyword; none are RI-specific; novel mechanism.
