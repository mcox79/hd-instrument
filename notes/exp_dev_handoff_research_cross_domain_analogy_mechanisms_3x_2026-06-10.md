# exp_dev hand-off -- research: cross-domain-analogy-mechanisms-3x

**Filed-by:** research sub-agent
**Date:** 2026-06-10
**Trigger:** Research note at notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md
  documents why RotatE/KGE fails cross-domain (STRETCH4-2 HARD_FAIL: 0.244 vs 0.899
  within-domain), six mechanism classes that DO enable cross-domain analogy, and ten
  ranked engineering anchors. Four anchors are immediately substrate-viable without
  GPU or full retraining. This is exp_dev-actionable.

**Pause state:** Check orchestrator_paused.flag before dispatching any anchors.
  If paused, hold this file for next refill cycle.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the anchors;
  this file names the mechanisms and provides substrate-product readings only.
  Do NOT inline experiment code or exact parameter values here.

---

## Anchor candidates (rank-ordered)

### ANCHOR-1: CROSS-DOMAIN-SMOKE-50 (RANK 1 -- gates all others)
**Substrate-product reading:** Construct a 50-triple cross-domain test set spanning 5
  relation types (causes, part-of, enables, produces, random) across 5 domain pairs
  (medical-legal, geographic-biological, financial-social, scientific-organizational,
  random). Measure baseline RotatE Hits@1, then measure three conditions: (A) structural
  alignment filter (relational factor cosine), (B) atomic-primitive decomposition at
  relation level, (C) LLM-proposed candidates scored by substrate. This is the cheapest
  decisive test in the research note. Results gate the entire cross-domain engineering
  roadmap.
**Tier hint:** CPU-viable. No GPU required. LLM API calls for condition C cost ~$0.10-0.20
  for the full 50-triple batch.
**Why now:** STRETCH4-2 HARD_FAIL (0.244 Hits@1) means no cross-domain analogy claims
  can be made until a repair mechanism is empirically validated. This smoke test takes
  2-3 hours and resolves which of the three mechanism paths is worth engineering.
**Pre-reg bands:**
  - HP (any single condition): Hits@1 >= 0.40 on 50 cross-domain triples
  - HP (condition C LLM-hybrid): Hits@1 >= 0.55
  - MID: any condition 0.30-0.39 (worth continued engineering)
  - HF: ALL conditions < 0.30 (cross-domain requires fundamentally new training data)

### ANCHOR-2: STRUCTURAL-ALIGNMENT-MAPPING (RANK 2 -- no retraining)
**Substrate-product reading:** For K-hop relational chains, project out the entity
  factor (average entity embedding component) from the chain vector and compare
  cross-domain chains using the residual relational factor only. This implements
  Gentner's structural alignment (match over relation structure, not entity content)
  using the existing K-hop chain embeddings already in the substrate. Expected Hits@1
  improvement: +0.10 to +0.25 over cosine baseline.
**Tier hint:** CPU-viable. Uses existing K-hop chain machinery. No new training data.
  Pure vector arithmetic modification to the cross-domain retrieval path.
**Why now:** Zero additional training data or model retraining required. The substrate
  already has the chain embeddings from the K-hop pipeline. This is a 1-day
  implementation that could move the 0.244 baseline to 0.35-0.45.
**Pre-reg bands:**
  - HP: relational-factor Hits@1 >= 0.40 (vs 0.244 baseline)
  - MID: 0.30-0.39 (partial improvement, combine with other mechanisms)
  - HF: < 0.28 (entity and relational factors are not separable in current space)

### ANCHOR-3: HYBRID-LLM-RELATION-DISCOVERY (RANK 3 -- highest P_deflated)
**Substrate-product reading:** For a cross-domain query (h_A, r_?, t_B), prompt the LLM
  with h_A and t_B descriptions to generate 3-5 candidate relation labels. The substrate
  retrieves the closest stored relation embeddings to each candidate label via cosine
  similarity and ranks by combined LLM confidence + substrate cosine score. The LLM
  provides domain-agnostic relation hypothesis; the substrate provides grounded verification.
  This is the fastest path to Hits@1 > 0.55 cross-domain.
**Tier hint:** CPU-viable for substrate side. LLM API calls required (Sonnet or Claude
  Haiku for cost efficiency). Entire pipeline runs on CPU + LLM API.
**Why now:** P_deflated = 0.50 (highest single-mechanism estimate, at the cap). LLM
  cross-domain analogy is already at 0.60-0.70 for GPT-4 class models. The substrate
  verification step adds grounding without requiring within-domain retraining. This is
  the pragmatic fast path to closing the STRETCH4-2 gap.
**Pre-reg bands:**
  - HP: Hits@1 >= 0.55 on CROSS-DOMAIN-SMOKE-50 with LLM candidates
  - MID: 0.40-0.54
  - HF: < 0.35 (LLM relation proposals do not align with substrate embedding geometry)

### ANCHOR-4: ATOMIC-RELATION-VOCABULARY (RANK 4 -- offline precompute)
**Substrate-product reading:** Define a vocabulary of 15-30 universal relation primitives
  (cause, prevent, enable, part-of, instance-of, precedes, follows, similar-to,
  opposite-of, function-of, agent-of, patient-of, location-of, temporal-state-of,
  quantitative-comparison). For each stored relation in the KB, compute a primitive
  decomposition vector (weighted combination of primitives). Cross-domain analogy is
  resolved by comparing primitive decomposition vectors rather than full relation
  embeddings. Decompositions can be generated offline using LLM annotation of existing
  relations (one-time cost, not per-query).
**Tier hint:** CPU-viable. Offline precomputation of primitive decompositions using LLM
  annotation. No retraining. Query-time cost is pure vector arithmetic.
**Why now:** If CROSS-DOMAIN-SMOKE-50 condition B (atomic-primitive) shows improvement,
  this anchor implements the full primitive vocabulary for production use.
  Should be dispatched AFTER CROSS-DOMAIN-SMOKE-50 validates the mechanism.
**Pre-reg bands:**
  - HP: Hits@1 >= 0.45 on high-overlap cross-domain pairs (cause-enables, part-of-contains)
  - MID: 0.35-0.44
  - HF: < 0.30 on high-overlap pairs (primitive decomposition is too coarse)

### ANCHOR-5: MULTI-DOMAIN-RELATION-TRAINING (RANK 5 -- highest ceiling, highest cost)
**Substrate-product reading:** Retrain KGE jointly over ConceptNet (600K triples, 34
  relation types), Freebase 15K (311K triples, ~1000 relation types), and Wikidata
  subset (~1M triples). Pre-align entities across KBs using name-matching + Procrustes
  rotation. The joint training produces shared relation geometry where universal
  relations (type-of, part-of, cause) develop stable cross-domain embeddings.
  Expected cross-domain Hits@1 improvement: +0.15 to +0.25 over current baseline.
**Tier hint:** GPU required for full joint training (6-12h on single GPU). Data pipeline
  engineering (entity alignment) is the bottleneck. Estimated 1 week engineering + 1
  GPU training run.
**Why now:** This is the highest-ceiling long-term mechanism (expected ~0.40-0.49
  cross-domain Hits@1 from training alone). However, cost is significant. Dispatch
  only after CROSS-DOMAIN-SMOKE-50 confirms the training-distribution explanation is
  correct (HF condition: if all conditions < 0.30, training alone will not help).
**Pre-reg bands:**
  - HP: cross-domain Hits@1 >= 0.40 after joint training (vs 0.244 baseline)
  - MID: 0.30-0.39
  - HF: < 0.30 (domain manifold mismatch is not resolved by joint training alone)

---

## Context pointers

- Research note (full mechanism analysis): notes/research_drill_cross_domain_analogy_mechanisms_3x_2026-06-10.md
- STRETCH4-2 failure context: current KB, PP-275 result (RotatE Hits@1 = 0.899 within-domain, 0.244 cross-domain, 10-shot)
- K-hop chain machinery (for ANCHOR-2): substrate's existing multi-hop retrieval pipeline
- Compositional shard hierarchy (adjacent): notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
- Biological compositional depth (adjacent): notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
- Cap map: notes/substrate_capability_map.md (cross-domain analogy row)

---

## Contract section

This handoff proposes 5 ranked anchors in priority order. ANCHOR-1 (CROSS-DOMAIN-SMOKE-50)
is the gate: its results determine which of ANCHOR-2 through ANCHOR-5 are worth pursuing.
If ANCHOR-1 condition C (LLM-hybrid) achieves HP >= 0.55, ANCHOR-3 should be dispatched
immediately as the production implementation. If condition A (structural alignment) achieves
HP >= 0.40, ANCHOR-2 should be dispatched next.

Expected total CPU time for ANCHOR-1: 2-3 hours. LLM API cost: ~$0.10-0.20.
Expected total CPU time for ANCHOR-2: 4-6 hours (implementation + evaluation).
Expected total CPU time for ANCHOR-3: 1-2 hours (LLM calls dominate).
Expected total CPU time for ANCHOR-4: 3-4 hours (LLM annotation of ~500 relations).
GPU time for ANCHOR-5: 6-12 hours single GPU (after 1 week data pipeline engineering).

---

## Autonomy declaration

exp_dev has full autonomy to:
- Design the specific CROSS-DOMAIN-SMOKE-50 triple set construction methodology
- Choose which LLM model to use for ANCHOR-3 (cost vs quality tradeoff)
- Decide whether to co-dispatch ANCHOR-1 + ANCHOR-2 simultaneously or sequentially
- Pre-register exact bands before dispatch per standard protocol

exp_dev should NOT:
- Dispatch ANCHOR-5 (GPU training) without explicit orchestrator authorization
- Commit cross-domain Hits@1 product claims until ANCHOR-1 HP is verified
- Assume the within-domain 0.899 result is at risk (it is not; separate capability)
