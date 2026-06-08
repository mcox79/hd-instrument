# exp_dev hand-off -- research: substrate math capabilities 5x

**Filed by**: research sub-agent
**Date**: 2026-06-08
**Trigger**: notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md (research delivery)
**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev designs all anchors with pre-reg per envelope-fail-bands. No inline experiment design in this file.

---

## Pause state block

Pause gate: check data/orchestrator_paused.flag before dispatch. If PAUSED, hold all queue-triggering actions.

---

## Anchor candidates (rank-ordered)

### Anchor A: PAL-bridge with substrate derivation cache
- Anchor pointer: math-pal-cache-A1
- Substrate-product reading: implement PAL-style code execution (LLM generates Python, interpreter executes, substrate stores result as KB triple with semantic key). Cache lookup before each LLM generation step. Measures substrate's reuse value on repeated math problem classes.
- Tier hint: Tier 2 (medium scope, novel integration, encoder pretest required first -- see cheap decisive test)
- Why now: fastest path to a demonstrable math capability that exceeds bare LLM. Uses only existing substrate primitives (KB, similarity search). No new operators. 1-2 week scope.
- Pre-reg bands: HARD-PASS = cache hit rate >20% after 500 GSM8K problems; HARD-FAIL = cache hit rate <5% (encoder unsuitable for math)
- PREREQUISITE: cheap decisive test below must pass before committing to this anchor

### Anchor B: Theorem dependency K-hop over mathlib subset (DUAL-PURPOSE: math capability + multi-hop revival)
- Anchor pointer: math-khop-theorems-B1
- Substrate-product reading: encode 1K Lean4 mathlib theorems as (theorem, depends-on, theorem) KB triples. Run K-hop to answer "what does theorem T depend on?" Measures K-hop on a formally structured math KB vs informal text KB. Dual-purpose: also probes multi-hop revival in a structured graph domain.
- Tier hint: Tier 2 (requires encoder pretest; if encoder fails, reverts to Tier 3)
- Why now: multi-hop revival is OPEN per MEMORY.md. Math theorem dependency is a high-quality structured graph with ground-truth (mathlib dependency graph is available). Better signal than HotpotQA for pure K-hop mechanism validation.
- Pre-reg bands: HARD-PASS = K-hop precision@1 >0.85 at k<=3 hops on 100-theorem test; HARD-FAIL = K-hop precision@1 <0.50 at k=1 hop (encoder failure gate)
- PREREQUISITE: cheap decisive test below must pass before committing

### Anchor C: Counterfactual axiom substitution via do() on formal theory KB
- Anchor pointer: math-do-axiom-C1
- Substrate-product reading: store a small formal theory (group axioms: closure, associativity, identity, inverse, optionally commutativity) as substrate KB. Test do(commutativity=false) to retrieve only theorems valid for non-abelian groups. Direct test of do() operator on a math-domain KB with known ground truth.
- Tier hint: Tier 1 (directly tests a validated substrate primitive PP-172 in a new domain; 1 week scope; minimal risk)
- Why now: do() operator is PP-172 validated. This is a cheap, fast domain transfer test. If it passes, opens counterfactual math reasoning as a product feature. If it fails, the failure mode is informative (is the do() mechanism too coarse for fine-grained axiom distinctions?).
- Pre-reg bands: HARD-PASS = do() precision >0.80 on 20-item axiom-substitution test set; HARD-FAIL = do() precision <0.60 (mechanism not discriminating for math domain)
- NOTE: this anchor does NOT require the encoder pretest to pass. Group axioms are short, simple, and likely encode well even if complex math notation does not.

### Anchor D: Z3 bridge with substrate orchestration
- Anchor pointer: math-z3-bridge-D1
- Substrate-product reading: substrate-orchestrated Z3 call pipeline. LLM extracts constraints; substrate stores constraint triple; Z3 solves; result stored back in KB with provenance. Tests full tool-orchestration loop with audit.
- Tier hint: Tier 3 (constraint extraction from text is the hard part; LLM quality gate; 2-3 week scope)
- Why now: deferred until Anchors A-C establish encoder baseline. Z3 bridge is higher-risk (constraint extraction quality is LLM-dependent, not substrate-dependent).
- Pre-reg bands: HARD-PASS = >70% end-to-end success on 50 NL constraint problems; HARD-FAIL = <40% (extraction pipeline fails)

### Anchor E: Autoformalization-to-KB pipeline
- Anchor pointer: math-autoform-E1
- Substrate-product reading: autoformalize 100 Wikipedia math articles (LLM + Lean parser); store (informal, formal) pairs in substrate KB; test semantic search precision@1.
- Tier hint: Tier 3 (depends on external LLM quality for autoformalization; 2-3 week scope)
- Why now: deferred. Anchor B (mathlib K-hop) is simpler and more controlled. Autoformalization pipeline adds external LLM dependency that clouds what is substrate-specific.

---

## Cheap decisive test (run BEFORE dispatching Anchors A or B)

Encode 50 theorems from Lean4 mathlib (titles + statement text) into substrate KB at N=4096. Query "what does the Cauchy integral theorem depend on?" and similar 10 queries. Measure K-hop precision@1 vs ground-truth mathlib dependency graph.
- Cost: ~1 hour, $0, laptop CPU
- PASS gate: precision@1 >0.70 on 10 test queries --> Anchors A, B, E unblocked
- FAIL gate: precision@1 <0.50 --> encoder is the bottleneck; fix encoder (try N=16384, different tokenization of math notation) before committing to Anchors A or B
- Anchor C (do() on group axioms) does NOT require this pretest to pass.

Recommended dispatch order:
1. Anchor C immediately (no pretest required, 1 week, tests PP-172 in math domain)
2. Cheap decisive test (1 hour, $0)
3. Anchor A or B depending on pretest outcome

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md
- Prior math drill: d:/AI/hd-instrument/notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- Prior math drill: d:/AI/hd-instrument/notes/research_5_directions_math_drill_2026-05-24.md
- PP-172 do() operator: reference in cap_map (counterfactual do() validated)
- Production architecture: d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Multi-hop revival: d:/AI/hd-instrument/memory/project_multihop_revive_priority.md
- K-hop depth validation: depth 55+ at accuracy 0.9949 (empirical, cycles 170-175)

---

## Contract

exp_dev designs all anchors with pre-reg per envelope-fail-bands. No inline experiment design is encoded here per [[feedback-no-experiment-design-in-prompts]]. Dispatch via queue_add.sh GPU or CPU as appropriate. Post-ship REMOTE VERIFY per role contract. Anchor C is CPU-eligible (small KB, no GPU required). Anchors A and B may require GPU depending on KB scale.

## Autonomy declaration

exp_dev has full autonomy to: design the specific experiment parameters for each anchor, choose N and KB size within pre-reg scope, order sub-anchors, decide smoke vs full run. exp_dev does NOT have autonomy to: skip the cheap decisive test before Anchors A/B, bypass pre-reg bands, treat mid-band as PASS.
