# Pre-registration: self_map_v2f_pretrained_encoder_smoke_v1

**Date:** 2026-06-22
**Anchor:** self_map_v2f_pretrained_encoder_smoke_v1
**Queue:** local_cpu_queue (smoke-class anchor)
**N:** 4096, **Seeds:** [1] (smoke), **n_anchors:** 100 (chain-grade prefix)

## Scientific question

Does swapping the substrate atom encoder from char_trigram (lexical bigram) to word2vec-google-news-300 (semantic; Spearman ~0.6 vs human similarity) break the substrate self-mapping HARD_FAIL of v2e? Per Skunkworks v2e landed-VET diagnosis, the encoder was the bottleneck, not the discriminator (modularity-Z vs degree-preserving null is by-construction-immune to by-construction-saturation).

## Background

v2e HARD_FAIL diagnosis: modularity-Z self-mapping at chain-grade Store failed not because the discriminator was wrong (Louvain + Newman modularity + degree-preserving null is the right family) but because char-trigram + 2-hop Jaccard adjacency cannot extract dependency-graph context from a substrate where atom_ids encode mechanism families lexically. The 5x drill conclusion: "encoder must move from name-bigram to dependency-graph-context embedding."

USER methodology fix 2026-06-22: strip mechanism keyword from atom_ids in the honest baseline arm to prevent name-leak from masquerading as community structure.

## 4 arms (encoder varies, discriminator fixed)

| Arm | Encoding | Role |
|---|---|---|
| ARM_CHAR_TRIGRAM_NAME_LEAK | char_trigram on FULL atom_id | reproduces v2e (gets name-leak boost) |
| ARM_CHAR_TRIGRAM_STRIPPED | char_trigram on atom_id with mechanism keyword -> hash | honest lexical baseline (no name-leak) |
| ARM_WORD2VEC_KEYWORDS | extract keywords + word2vec lookup + bundle + project | Path A semantic encoder |
| ARM_HYBRID | bundle(word2vec_keywords, char_trigram_stripped) | semantic + lexical composition |

Discriminator (held fixed across arms): modularity-Z + Louvain @ gamma in {0.5, 1.0, 2.0, 4.0} vs degree-preserving null (30 rewires in smoke). Same KGStore + multi_hop K=2 + Jaccard adjacency from v2e.

## Pre-registered bands

**HARD-PASS:**
- ARM_WORD2VEC_KEYWORDS `mod_Z >= 3.0` at any gamma in the sweep
- ARM_WORD2VEC_KEYWORDS `mod_Z / ARM_CHAR_TRIGRAM_STRIPPED mod_Z >= 2.0` (semantic beats stripped-lexical by 2x)
- ARM_WORD2VEC_KEYWORDS `mean Z > ARM_CHAR_TRIGRAM_NAME_LEAK mean Z` (semantic also beats the name-leak baseline; rules out "name-leak is doing all the work")
- `atom_retrieval_recall >= 0.50` minimum per arm (encoder must still index its own atoms reasonably)
- `n_llm_calls == 0` (substrate-only-decode)

**MIDDLE:** partial improvement; semantic arms beat stripped baseline but not 2x or not Z>=3.

**HARD-FAIL:** ALL semantic arms `mod_Z < 1.5` at every gamma, OR `max ratio (w2v|hybrid)/stripped < 1.5`. This indicates substrate self-mapping is fundamentally hard regardless of encoder (forces a different probe family entirely; this would invalidate the encoder-bottleneck hypothesis).

## Calibration rationale

Pass band for mod_Z >= 3.0 carries forward from v2e (3-sigma community-detection rule). 2x ratio threshold ensures the semantic signal is genuine (not just slightly above stripped baseline). Beating name-leak too is the strict test: it rules out the alternative explanation that name-leak in NAME_LEAK arm is structurally as good as semantic. Recall floor lowered to 0.50 (vs v2e's 0.95) because w2v keyword extraction is over a small per-atom token set; perfect self-recall isn't structurally guaranteed but a 50% floor catches encoder collapse.

## Sanity self-test (endpoint)

`--self-test` builds 45 synthetic atom_ids across 3 blocks with DISTINCT keyword sets per block (block A: animals; B: vehicles; C: music). Requires `Z(w2v) > Z(stripped)` AND `Z(w2v) >= 1.5` AND zero LLM calls. Confirms the encoder substitution actually delivers semantic signal that stripped-lexical cannot capture.

## Implementation notes

- Uses cached `data/gensim_cache/word2vec-google-news-300` (no network required)
- Keyword extraction: split atom_id on `_`; drop short tokens / version markers / pure numerics
- Mechanism-keyword strip regex covers ~80 substrate-mechanism vocabulary tokens
- Hash-based replacement is deterministic per (atom_id, seed) for reproducibility
- Reuses v2e's modularity_Z_score / louvain_partition / degree_preserving_rewire primitives unchanged

## Smoke vs full delta

This is a smoke-class anchor (suffix `_smoke_v1`). FULL follow-up would have:
- 3 seeds, n_anchors=150, n_null_rewires=100, jaccard_tau=0.10
- New anchor name without _smoke (e.g. `self_map_v2f_pretrained_encoder_v1`)
- ~3h remote_cpu_queue

## N-suffix section

Anchor name does not include `_n4096` suffix because PROT-018 is satisfied by `N_DIM=4096` constant; the `_smoke_v1` suffix signals smoke-class. Production N=4096 across both smoke and full (encoder is not the bottleneck per v2e diagnosis).

## Timeout estimate

Smoke: 4 arms x [encode + KG build + 2-hop neighborhoods + modularity-Z sweep over 4 gammas with 30 null rewires each] over 100 anchors at N=4096. Expected wall ~15-20 min on local_cpu (word2vec load adds ~30s; cached in-process across arms).

formula: 1.5 * 1200s = 1800s (smoke margin)
timeout_s = 1800
