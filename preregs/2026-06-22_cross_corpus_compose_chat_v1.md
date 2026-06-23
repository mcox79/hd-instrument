# Pre-reg: cross_corpus_compose_chat_v1_n4096

Date: 2026-06-22
Author: Exp-Dev (per Research task)
Anchor: cross_corpus_compose_chat_v1_n4096
Script: experiments/exp_cross_corpus_compose_chat_v1_n4096.py
Routing: remote_cpu_queue
Estimated wall (full): ~30-60min (3 backends x 200 queries x encoder.nearest + KGStore.predict)

## Gap (per Skunkworks 273-composition META audit 2026-06-22)

Three KG backends are independently chain-grade:
- FB15k-237 (CERT 584; structured KG)
- ConceptNet (CERT 585; commonsense)
- HotpotQA (CERT 588; multi-hop Wikipedia)

Cross-corpus composition across the three is NOT chain-grade evidenced -- only
intra-corpus ingest + within-synthetic-set aggregation (hierarchical_5corpus_meta
covers 5 SYNTHETIC domains, not 3 REAL ones). This cell closes that gap.

## Hypothesis

Composing the three real-corpus backends into one query-time pipeline yields
strictly more correct answers than the best single-backend baseline, with no
per-corpus regression.

## Arms (Fix #16 discriminator: 3 arms; 1 baseline + 2 contrastive composition strategies)

1. **SINGLE_BACKEND** (baseline)
   - For each query: ask each backend independently; pick the one whose answer
     scored highest (per its own internal score). Current state.
2. **CROSS_COMPOSE_UNION**
   - Query all 3 backends; UNION their top-k anchors + relations; rank by
     combined score (sum of per-backend normalized scores). Single answer.
3. **CROSS_COMPOSE_HUB_SPOKE**
   - Query all 3 backends; each backend's top anchor encoded in shared HD
     (CharTrigramEncoder at N_DIM=4096); HUB-SPOKE convergence: superpose the
     3 anchor vectors, then nearest-in-union-codebook (the hub) picks the
     single most-confident-across-backends answer (Patterson-Rogers ATL motif).

## Test set (200 questions; spans the 3 corpora's domains)

- 70 ConceptNet-domain (commonsense): "is a tomato a vegetable", "what causes rust", ...
- 70 HotpotQA-domain (Wikipedia): "who directed doctor strange", "where is tehran", ...
- 60 FB15k-domain (structured KG): freebase entity queries via human-readable names

Test set is generated programmatically from each backend's entity vocabulary +
relation set; gold-answer is the backend's first-hop predict for the chosen
(entity, relation) pair (substrate-anchored; not LLM-judged).

## Pre-reg hard bands

- HARD_PASS: BOTH conditions
  - max(CROSS_COMPOSE_UNION_acc, CROSS_COMPOSE_HUB_SPOKE_acc) >= SINGLE_BACKEND_acc + 0.10
  - per-corpus subset breakdown: best-COMPOSE arm acc >= SINGLE_BACKEND acc on EVERY corpus
    (composition doesn't HURT any single-corpus subset)
- HARD_FAIL: max(CROSS_COMPOSE_*) <= SINGLE_BACKEND_acc (composition adds no value)
- MIDDLE_BAND: positive lift but below +0.10, OR positive lift but a corpus regressed
- Substrate-only-decode gate: metrics.n_llm_calls == 0 (HARD_FAIL if violated)

## Formula self-tests (PROT-022)

1. encoder.nearest returns same anchor on identical-string query (idempotency).
2. KGStore.predict_one_hop_topk returns tensor of correct shape.
3. Hub-spoke superposition reduces to argmax-of-single-anchor when 2/3 anchors
   are zero (sanity: composition degrades gracefully).

## Routing rationale

- 3 backends x 200 queries x (encoder nearest at ~100k codebook + KGStore predict)
  = numpy/torch matmul-bound, NOT GPU-required (no large batched matmul; per-query
  serial calls).
- ~30-60min CPU wall fits remote_cpu_queue tier.
- N_DIM=4096 (caches already exist at this dim).

## Composes with

- exp_substrate_hierarchical_5corpus_meta_v1_n2048_gpu (CERT chain-grade for 5
  SYNTHETIC domains) -- this cell extends the composition discipline to 3 REAL
  domains.
- 273-composition META atom (Skunkworks 2026-06-22 audit).

## Negativity-bias symmetry note

Either HARD_PASS or HARD_FAIL is a usable outcome. PASS = composition mechanism
chain-grade for real corpora; FAIL = composition mechanism does NOT transfer
across real corpora, route to revival drill (per USER 2x-revival rule). The bands
must NOT be loosened in either direction post-hoc.
