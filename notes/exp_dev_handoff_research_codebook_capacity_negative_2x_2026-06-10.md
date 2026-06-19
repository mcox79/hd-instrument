# exp_dev hand-off -- research: codebook capacity negative 2x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: LAP4-1 HARD_FAIL on chirp/CAZAC codebook (1.07x, predicted 1.5x); LAP3-6 QR-orthonormal 1.05x
Research note path: d:/AI/hd-instrument/notes/research_drill_codebook_capacity_negative_2x_2026-06-10.md

## Pause state

Per [[feedback-no-experiment-design-in-prompts]]: this file does NOT contain experiment design or implementation details. It contains anchor candidates, context pointers, and the reason each is exp_dev-actionable. exp_dev reads the research note for the mechanism explanation and derives experiment design autonomously.

## Why this is exp_dev-actionable

The research note refutes the coherence-as-lever hypothesis definitively and identifies five specific construction classes that CAN beat the sqrt(N/K) ceiling. Three of them are directly implementable on CPU in < 2 hours. The cheapest (bundle splitting) requires only routing logic and immediately provides a 2x capacity multiplier for C=4 typed sub-bundles. This is a positive engineering path from a negative codebook result.

---

## Anchor candidates (rank-ordered)

### Rank 1: bundle-split SNR smoke test
Anchor pointer: bundle-split-C4-smoke (new anchor, to be registered)
Substrate-product reading: if C=4 typed sub-bundles (entity/relation/attribute/provenance) give the theoretical sqrt(4)=2x capacity multiplier, production KB capacity at current N doubles with zero math change. This directly addresses the PP-244 kstar/N constraint without any new mechanism.
Tier hint: tier 1 (fast CPU smoke, < 5 min, low cost, high signal)
Why now: the negative LAP4-1 result closes the codebook direction; bundle splitting is the fastest re-route that has unambiguous theoretical grounding and no prior empirical test.

### Rank 2: modern Hopfield softmax retrieval comparison at K >> kstar
Anchor pointer: hopfield-softmax-comparison-smoke (new anchor)
Substrate-product reading: if one-step softmax retrieval achieves > 0.85 accuracy where flat FHRR bundle < 0.50 at K=2*kstar, this opens an optional high-capacity retrieval mode for small high-value KBs. Maps to north-star: demonstrably exceeds standard FHRR retrieval, which is the comparison class for LLM-relative size benchmarking.
Tier hint: tier 2 (CPU, < 30 min, moderate complexity)
Why now: Hu et al. 2024 tight bound paper establishes this is achievable; no empirical test against substrate's specific K/N operating point.

### Rank 3: B=3 sparse block code for triple-structured facts
Anchor pointer: sparse-block-triple-smoke (new anchor)
Substrate-product reading: substrate KB items are (subject, predicate, object) triples, which are naturally 3-factor structures. B=3 block code maps directly. If factorization accuracy > 0.90 at K=500 triples, this replaces flat bundle for fact storage and provides orders-of-magnitude capacity improvement for compositional retrieval.
Tier hint: tier 3 (CPU, 1-2 hr prototype, higher complexity)
Why now: Hersche et al. 2025 published result confirms 5+ orders-of-magnitude capacity gain for factorizable items; substrate triple structure is a natural fit.

### Rank 4: tensor product orthonormal role retrieval
Anchor pointer: tensor-product-role-retrieval-smoke (new anchor)
Substrate-product reading: typed slot retrieval (retrieve object given subject + predicate) is algebraically exact with orthonormal role vectors. This is a specific capability enhancement: slot-filling from bundles, not just similarity-based retrieval.
Tier hint: tier 2 (CPU, < 1 hr, low complexity -- algebraic derivation is well-defined)
Why now: this is a known result (Smolensky 1990) that has not been empirically verified against substrate's N and binding architecture.

---

## Context pointers

Research note (full derivation + mechanism): d:/AI/hd-instrument/notes/research_drill_codebook_capacity_negative_2x_2026-06-10.md
LAP4-1 verdict (empirical closure): search data/exp_LAP4-1/metrics.json
LAP3-6 verdict (QR codebook 1.05x): search data/exp_LAP3-6/metrics.json
PP-244 kstar/N result: search data/exp_PP-244/metrics.json
Production architecture reference: C:/Users/marsh/memory/production_architecture_locked_2026-06-07.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev is authorized to:
- Register any of the 4 anchors above against an appropriate queue (CPU preferred for ranks 1-2-4; CPU for rank 3 prototype)
- Design experiment cells autonomously per the research note mechanism descriptions
- Run smoke tests at N=2048 (or current production N) and K at or above kstar
- Issue PASS/FAIL verdicts against the pre-registered thresholds in section 6 of the research note

exp_dev is NOT authorized to:
- Pursue further codebook coherence variants (direction closed by LAP4-1 + LAP3-6 + theory)
- Implement production changes before smoke PASS
- Combine multiple rank anchors in one cell (run independently)

## Autonomy declaration

exp_dev reads this file and the research note, then decides cell design, HP choices, and queue routing independently. No further clarification needed from research or orchestrator before dispatch of rank-1 anchor (bundle-split smoke). Ranks 2-4 may proceed sequentially after rank-1 completes. Escalate back to research only if rank-1 empirical SNR ratio falls outside [0.8x, 2.5x] theoretical (indicates unexpected mechanism).
