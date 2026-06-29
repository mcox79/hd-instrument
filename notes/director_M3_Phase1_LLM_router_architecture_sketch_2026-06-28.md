# M3 Phase 1 — LLM router architecture sketch

**Status:** v0 design sketch by Director, 2026-06-28
**Audience:** Director (future me) + USER (when ready to weigh in)
**Scope:** Concrete starting point for the external cortex layer that M3 requires above the substrate. Not a full design doc.

---

## Why M3 needs an external cortex layer

Two substrate-only blockers, both with 2x-drill closure (mechanism-class-2 negatives, not implementation bugs):

1. **Barrier 1 hint derivation** — CLOSED-negative. 5 drills HF (cosine + 3 brain-comp + supervised linear). PFC/cortex-style derivation requires surface-form access; substrate doesn't carry it.
2. **CLS handoff at chain-grade M=8192** — CLOSED-negative. Willshaw capacity 227x exceeded; substrate replay path floors at small-M. Chain-grade scale requires a different protocol OR an external cortex layer that holds surface forms during consolidation.
3. **Long-narrative Q2 coref** — CLOSED-negative. HRR-recency + substrate-faithful Lappin-Leass both HF; needs surface-form access to entity strings.
4. **Hierarchical planning (substrate-native)** — CLOSED-negative. Closed earlier; needs external planner.

These four 2x-drill closures jointly say: the substrate is a memory + composition + retrieval + audit device, and a cortex layer above it is load-bearing for the M3 conversational AI target.

---

## What the LLM router does (Phase 1)

The router is the cortex layer's MVP. It receives a USER query, decides whether substrate primitives can answer it, and either delegates or falls back to LLM general response.

Concretely:

```
USER query
   |
   v
[Intent classifier (substrate)] — returns intent_class + confidence
   |
   v
[Router decision]
   - if intent in {KG_LOOKUP, MULTI_HOP, SCHEMA_RETRIEVAL, COMPOSITIONAL} and confidence >= threshold:
       -> delegate to substrate primitive
       -> verify substrate output (cleanup attractor confidence; refuse-gate fires?)
       -> if verified: return substrate output (glass-box)
       -> if refused: fall back to LLM
   - else:
       -> fall back to LLM general response
```

The router itself is an LLM call (initial Phase 1) — claude-haiku-4-5 sized for fast routing decisions. Phase 2 replaces with a learned classifier; Phase 3 (5+yr) makes it substrate-native.

## What the router DOESN'T do (Phase 1 scope discipline)

- Doesn't synthesize substrate output with LLM output (that's Phase 2)
- Doesn't decompose multi-hop queries before delegation (substrate's multi-hop primitive handles full chains)
- Doesn't have memory across turns (Phase 2)
- Doesn't decide WHICH substrate primitive to use beyond intent class (Phase 2 routing learns this)

---

## Substrate primitives ready to expose (chain-grade today)

From the BACKUP characteristics table:

| Primitive | Chain-grade status | Router exposure (Phase 1) |
|---|---|---|
| KG ingest (FB15k/CN/HotpotQA) | CG HIGH | Yes — `kg_lookup(entity, relation) -> entity` |
| Multi-hop reasoning depth-15 | CG HIGH | Yes — `multi_hop(start, relation_chain) -> entity` (needs partition-oracle hint, which is an internal substrate detail) |
| Schema exemplar-Bayes | CG MID (chain-grade promotion path live) | Maybe — `schema_retrieve(query, schema_id) -> exemplar` |
| Partition routing M=10M | CG HIGH | Internal — routing primitive, not exposed |
| Cleanup attractor | CG HIGH | Internal — confidence signal for verification |
| Refuse-gate V_REL=256 | CG HIGH | Internal — drives "fall back to LLM" decision |
| Intent classifier n=100 | CG MID | YES — this IS the router's first stage |
| Cross-modal binding | CG HIGH | Not Phase 1 (no audio/visual input) |
| TASK_VECTOR HRR ICL | CG (pending VET) | Maybe — if VET confirms, `apply_task_vector(query) -> output` |

Compositional generation, sequence binding, WM K-cliff, etc. are infrastructural — used internally by the primitives above, not exposed to router.

---

## Phase 1 interface contract (sketch)

```python
# Substrate exposes a thin API to the router
class SubstrateRouterAPI:
    def classify_intent(self, query: str) -> tuple[str, float]:
        """Returns (intent_class, confidence in [0,1])."""

    def kg_lookup(self, entity: str, relation: str) -> tuple[str | None, float]:
        """Returns (answer entity or None, confidence)."""

    def multi_hop(self, start: str, relation_chain: list[str]) -> tuple[str | None, float]:
        """Returns (final entity or None, confidence)."""

    def schema_retrieve(self, query: str, schema_id: str) -> tuple[str | None, float]:
        """Returns (matched exemplar or None, confidence)."""

    def is_refused(self, query: str, intent: str) -> bool:
        """Refuse-gate fires when query is outside substrate's known domain."""
```

Router calls these; if any returns confidence below threshold OR refuse-gate fires, router falls back to LLM.

---

## Phase 1 milestones (concrete, sequenced)

**M1.1** — Intent classifier exposed via Python API; integrate into a router LLM call template
**M1.2** — KG lookup (FB15k) exposed; smoke a 100-query test where router correctly delegates 80%+ of KG_LOOKUP intents
**M1.3** — Multi-hop exposed; smoke a 50-chain test (chain depth 2-5)
**M1.4** — Schema retrieve exposed (if VET confirms chain-grade promotion); smoke schema-typed queries
**M1.5** — Refuse-gate integrated; verify router correctly falls back to LLM when refuse-gate fires
**M1.6** — End-to-end demo: 200 queries spanning KG/multi-hop/schema/refused/general. Measure: substrate-routed accuracy + LLM-fallback accuracy + router decision accuracy

After M1.6: USER decision point on Phase 2 (learned router + cross-turn memory).

---

## Open questions for USER (Phase 1 v0)

1. **Router LLM choice** — claude-haiku-4-5 for speed? Or a different model for cost reasons?
2. **Confidence threshold** — what's the substrate-output confidence above which router trusts substrate over LLM? 0.8? Tune empirically?
3. **Schema promotion** — should I block M1.4 on the in-flight Skunkworks VET of schema_bayes capacity-stress v2, or implement defensively?
4. **TASK_VECTOR exposure** — if VET confirms chain-grade, should TASK_VECTOR be a primary primitive in M1.3 or held for Phase 2?
5. **Glass-box explanation** — should the router return both the answer AND the substrate's reasoning trace (attractor convergence path, hop sequence)? This is the "glass-box" property M3 promises.

---

## What this is NOT

- Not a literature-deep architecture review (defer)
- Not a code-ready spec (M1.1 lands the first concrete API)
- Not a commitment to claude-haiku-4-5 specifically (router LLM choice is open)
- Not Phase 2 / Phase 3 design — those wait for Phase 1 to land

---

## Next step

This sketch unblocks USER review. After USER weighs in on the open questions, M1.1 (intent classifier Python API) becomes the first hdi_exp_dev spawn target for M3 work. The Phase 1 router LLM call template lives in a new module (substrate_router/) outside hdlab/ proper, since it's the cortex layer not substrate.
