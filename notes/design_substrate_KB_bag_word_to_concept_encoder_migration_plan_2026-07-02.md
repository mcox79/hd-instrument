# Design — Substrate-KB migration from bag-of-word to substrate-owned concept encoder

**Filed:** 2026-07-02 late evening (main-thread strategic planning while Spoke 1 v3-D authors)
**Anchor:** `substrate_kb_encoder_migration_plan`
**Prereq:** Stage 2 concept encoder Spoke 1 lands CG (v3-D competitive-Hebbian in flight; a9167ee4)
**Motivation:** USER's original phrase "storage strategy sharded bundled scale free topology physics law" hits target atom at cosine 0.5381 — the bag-of-word encoder ceiling. Concept encoder should lift this to 0.85+ (semantic understanding of the query terms). Multiple drills also hit the 7.4GB numpy OOM on this KB's embedding matrix — a concept-encoder replacement is an opportunity to fix BOTH problems.

## Intuitive summary (no jargon)

**Where we are.** The substrate has a knowledge base that stores concept "atoms" (proven substrate physics laws, mechanism CGs, prereg files, notes). To find things, we compare a query against the atoms via cosine similarity of vector representations. Right now those vectors are made by a character-trigram encoder: it slices each atom's text into 3-character windows and bundles their random-hash HDs. That's a surface-level similarity — it matches word-parts, not concepts.

**Concrete failure.** USER queries "sharded bundled scale free topology physics law." Target atom is named `META_storage_strategy_SCALE_FREE_AND_TOPOLOGY_FREE_physics_law_v1` — the atom TEXT doesn't contain the word "sharded" or "bundled" so the trigram encoder can't score them as similar. Only "storage" + "strategy" + "scale" + "free" + "topology" + "physics" + "law" match on trigrams. Result: cosine 0.5381 — a passable but not great match. In the older separate chunk KB (broken), the query returned cosine 0.31 because chunks lacked even the atom name text. Full failure.

**What concept encoder fixes.** A substrate-owned concept encoder learns from data that:
- "sharded" and "SHARDED" and "storage strategy" cluster together as one concept
- "physics law" is a distinct concept
- "scale free" and "topology free" are properties of physics-law atoms
- The query is asking for the atom that's ABOUT storage-strategy physics laws with those properties

So query and atom get encoded as CONCEPT vectors, not bag-of-word vectors. Concept-vector cosine 0.85+ becomes possible because both sides represent the underlying MEANING, not the surface text.

## Migration architecture

### Current architecture (bag-of-word)

```
Atom / query text
     ↓
tools/director_kb_query.py
     ↓
hdlab/char_trigram_encoder.py — bag-of-trigrams bipolar HD (or MiniLM-alt in some paths)
     ↓
E matrix: [n_entities × 2048 float32]  (7.4 GB post-unify; OOM on multi-drill day)
     ↓
cosine(query_hd, E) via matmul
     ↓
top-K entities
```

### Target architecture (concept-encoder)

```
Atom / query text
     ↓
hdlab/char_positional_encoder.py — surface HD (V1-analog, KEEP for input)
     ↓
hdlab/concept_encoder.py — substrate-owned concept HD via competitive-Hebbian (from Spoke 1 v3-D)
     ↓
E_concept matrix: [n_entities × 8192 sparse-bipolar]  (target: <2GB via sparse-encoded format)
     ↓
cosine(query_concept_hd, E_concept) — accelerated by sparsity (only compare active dims)
     ↓
top-K entities
```

Two structural wins:
- **Semantic queries**: concept encoder handles "sharded" ↔ "SHARDED" ↔ "storage strategy" semantic clustering that bag-word can't
- **Memory efficiency**: sparse-bipolar (2% active dims) compresses to ~1/50th the dense storage; 7.4GB → ~200MB. OOM resolved.

## Migration plan (5 steps, ~1-2 weeks post-Spoke-1-CG)

### Step 1 — Concept encoder training on KB corpus (~2-3 days)

Once `hdlab/concept_encoder.py` exists (post-Spoke-1 v3-D CG + hdlab extraction):
- Load all unified KB atom + chunk text as training stream (~970K entities, ~1.6M triples)
- Train competitive-Hebbian encoder on this stream via purely-local rules
- Verify convergence: after N passes, adjacent-in-text tokens produce similar concept HDs
- Save trained encoder state to `data/substrate_concept_encoder_v1/`

**Prereqs:**
- Spoke 1 v3-D CG (in flight)
- Spoke 1 hdlab extraction (post-CG)

**Smoke gate:**
- After 100K training tokens, "cat" and "kitten" produce cosine ≥ 0.4 (Spoke 1 baseline expectation)
- Sparse activation rate ∈ [0.01, 0.03]
- Reproducible across seeds (cv < 0.20)

### Step 2 — Re-encode unified KB with concept encoder (~1-2 days)

- For each entity in unified KB (970K), compute concept HD via trained encoder
- Save as sparse-bipolar E_concept.pt: [970K × 8192 int8 sparse-CSR format]
- Verify: total size < 2GB (target)
- Query path: modify `hdlab/director_kb_query.py` to load E_concept.pt via sparse-load path
- Preserve E.pt (bag-word) as fallback for A/B comparison

**Sparse format design:**
- Store only active dims per entity: `[entity_idx, active_dim_indices, ±1 signs]`
- Query cosine: only compare against dims where BOTH query and entity are active
- Fast: query with k=160 active dims × entity with k=160 → 160 dim comparisons per entity vs 8192 dense

### Step 3 — Verification against 100-query gold-standard test set (~1 day)

Author 100 diverse queries covering:
- Direct-hit atom queries (e.g., "storage strategy physics law")
- Concept-cluster queries (e.g., "brain-analog neural learning rule")
- Failure-mode queries (e.g., queries that USER has hit low-cosine on this session)
- Prior-work queries (e.g., "sparse allocation falsified")

Run each query on BOTH:
- E.pt bag-word (baseline)
- E_concept.pt concept-encoded (new)

Success criteria:
- Mean top-1 cosine on concept-encoded > 0.15 higher than bag-word
- USER's original test query "storage strategy sharded bundled scale free topology" hits target atom at cosine ≥ 0.75 (up from 0.5381 bag-word)
- No query regresses more than 0.10 cosine (concept encoder shouldn't lose semantic queries that bag-word could handle)

### Step 4 — Route wrapper to concept-encoded KB + continuous ingest daemon update (~1 day)

- `tools/substrate_query.sh` default = concept-encoded KB; `--legacy-bagword` opt-in for A/B
- `tools/director_kb_continuous_ingest.py` runs BOTH encoders on new content (during migration period)
- Once concept-encoded is validated for 1 week: retire bag-word E.pt; save disk

### Step 5 — Concept-encoder retraining schedule (~ongoing)

- Nightly incremental retraining on new atom + note content
- Weekly full re-training if concept-clustering drift is detected
- Continuous validation against 100-query gold-standard test set — alert if any query regresses > 0.10

## What this unlocks (beyond query improvement)

**For USER:** substrate-KB concept-query discipline becomes truly semantic. Every USER query returns conceptually-related prior work, not just word-overlap hits. The "did we do this before" check becomes reliable.

**For downstream Stage 3-5:**
- Cortex primitives (M1.9/M1.10/M1.11) can be RE-VALIDATED against concept-encoded inputs (post-Spoke-1-hdlab extraction) — mechanism proofs on structured concept vectors, not random codebooks. Under brain-best-in-class, this is the legitimate substrate-product primitive test.
- M3 conversational becomes tractable — cortex primitives operate on real concept vectors, not integer-indexed codebooks

**For substrate self-improvement (M4/M5):**
- Substrate can query itself semantically about its own atoms → "what physics laws have we proven about compositional cells?" returns SCALE_FREE + TOPOLOGY_FREE + storage-strategy META atoms via concept similarity, not text overlap
- Basis for USER's substrate-as-director-KB dogfood pattern

## Risk register

**R1 — Concept encoder collapses on real KB text (vs synthetic corpus).** Real KB text is structured technical prose, not conversational sentences. Foldiak/Kohonen mechanism may need parameter tuning. Mitigation: Spoke 2 (Foldiak trace) will help with temporal-invariance; if v3-D concept encoder doesn't handle KB text well, defer migration until Spoke 2 lands.

**R2 — Sparse-CSR format bugs.** Sparse-storage rarely first-try. Mitigation: unit-test sparse cosine against dense reference on small subsets before full 970K migration.

**R3 — Query regression.** Some queries might work better on bag-word (highly-specific technical terms with exact match). Mitigation: A/B period + gold-standard test set + rollback capability.

**R4 — Retraining cost.** If encoder needs frequent re-training as new atoms land, adds ongoing compute. Mitigation: incremental Hebbian updates on new content instead of full retraining.

## Timeline (post-Spoke-1 v3-D CG)

- Step 1 (train encoder on KB): ~2-3 days
- Step 2 (re-encode KB with concept encoder): ~1-2 days
- Step 3 (100-query verification): ~1 day
- Step 4 (route wrapper + daemon update): ~1 day
- Step 5 (schedule ongoing): ~ongoing after

**Total: ~1-2 weeks from Spoke 1 CG to concept-encoded substrate-KB.**

## Blocked-on

- Spoke 1 v3-D CG (in flight, a9167ee4)
- Spoke 1 hdlab extraction (post-CG)
- Testbed KB OOM fix (aeaf906c, in flight) — needed for A/B queries during migration
- USER approval on plan

## Composability with Stage 2 arc

This plan runs AFTER Spoke 1 lands CG. Spoke 2 (Foldiak trace / temporal contiguity) is orthogonal — it improves the encoder's temporal-invariance property but doesn't gate the KB migration. Migration could proceed with v3-D competitive-Hebbian Spoke 1 alone; Spoke 2's temporal-contiguity improvements can be applied via incremental re-training.

Spoke 3 (hippocampal DG+CA3+CLS) also orthogonal — Spoke 3 adds one-shot binding + consolidation which is useful for the KB (fast ingest of new atoms) but not required for the initial migration.

**Recommended sequence:**
1. Spoke 1 CG → migrate KB to concept-encoded (this plan)
2. Spoke 2 CG → incrementally re-train concept-encoded KB with temporal-contiguity refinement
3. Spoke 3 CG → add one-shot fast-ingest path for new atoms
4. Continual validation via 100-query gold-standard test set
