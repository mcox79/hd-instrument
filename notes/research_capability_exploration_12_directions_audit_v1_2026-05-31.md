# Research: 12-direction capability-exploration audit (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- shared external Claude evaluation proposing 12 substrate capability-exploration directions; "I want to eventually deep dive into all of the below. Thoughts on this, and can we start researching these and considering experiments that could show these?"
Method: main-thread audit + cap_map cross-reference + 3 parallel Sonnet drills dispatched on the highest-leverage directions (1, 6, 7). This note documents the audit, prioritization, and dispatch; the 3 drill deliverables synthesize into a follow-on routing file when they return.

## HEADLINE

The doc's 12 directions are all theoretically tractable from substrate's architecture but they fall into 4 distinct categories with different ownership, tractability, and overlap with current in-flight work. The substrate-LLM build (started today; 7-8 weeks) ALREADY EXPOSES partial empirical evidence on Directions 5, 7, and 10 via its 4 bespoke benchmarks. The pure-substrate research drills should focus on what the build does NOT cover: Direction 1 (compositional binding at production scope), Direction 6 (hierarchical concept formation; instrumentation-only on existing 24h workload state), and Direction 7 (Bet B ret_A rescue — closes a known cap_map gap). Three parallel Sonnet drills dispatched. Directions 5 (standalone follow-on), 2, 4 are next-cycle candidates. Directions 3, 8, 9, 11, 12 defer with explicit criteria for revisit.

## 4-category split of the 12 directions

| Category | Directions | Owner / handoff | Tractability now |
|---|---|---|---|
| Substrate-physics questions (inherent to architecture) | 1, 2, 6, 12 | research drill -> exp_dev probe design | YES |
| Capability tests of validated mechanisms | 5, 7 | research drill -> exp_dev refinement | YES |
| New mechanism design required first | 3, 8, 9, 11 | research -> multi-week design -> exp_dev | NO (defer) |
| Engineering integrations (substrate + external system) | 4, 10 | testbed engineering + research consultation | MEDIUM |

This is different from the doc's "research session capacity" lumping. Each category has different cost shapes and ownership paths.

## Overlap with the substrate-LLM build's 4 bespoke benchmarks

The build (handoff at `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`) specs 4 substrate-favored bespoke benchmarks for Week 5 evaluation. These ALREADY TEST PARTIAL ASPECTS of several proposed directions:

| Bespoke benchmark | Directly addresses | Partially addresses |
|---|---|---|
| Edit-then-query (substrate updates atom; old answer should be replaced) | -- | Direction 7 (continual learning under edit pressure) |
| Deletion-cert audit (verifier checks deleted facts can't be retrieved) | -- | Direction 10 (provenance for explainability) |
| Provenance citation (atom-level citation precision vs gold evidence) | -- | Direction 10 (substrate-native explainability) |
| Real-time-learn-then-query (write fact; re-query same Q; should improve) | Direction 5 PARTIAL | Direction 7 (continual learning per fact) |

**Implication**: the doc's recommended Direction 5 standalone drill is partially duplicative -- but the build's real-time-learn-then-query tests SINGLE-FACT INCREMENTAL learning, not FEW-SHOT PATTERN GENERALIZATION (Direction 5's distinctive claim: N examples -> unseen instances). So a separate Direction 5 drill IS valuable, but should be scoped to FEW-SHOT GENERALIZATION specifically (not single-fact incremental, which the build already covers).

The doc's #10 (substrate-native explainability) overlaps so heavily with provenance citation + deletion-cert audit that a separate drill should focus on the ML-PIPELINE-INTEGRATION question (substrate as audit layer for ML training data), not the per-prediction provenance question already covered.

## Per-direction evaluation

### Highest leverage, dispatch NOW

**Direction 1: Compositional binding algebra at production scope**
- **Why dispatched**: substrate-physics story most worth empirically nailing. The S13 / #150 CEILING_AT_CONSERVATIVE_ENVELOPE catch is real (verified in cap_map; sub-capacity envelope cannot discriminate reasoning from pattern matching). Validated mechanism (binding algebra) but UNVALIDATED capability claim (composition over novel non-stored combinations).
- **Drill scope**: test corpus design that DISCRIMINATES compositional binding from memorization / stored-chain retrieval; memorization traps; production-scope envelope (depth=5, M past M_c, K_paths=500, n_queries scaled); falsifiable predictions; substrate Path D vs Path B comparison baseline; audit-trail-verification protocol.
- **Distinctiveness**: HIGHEST. If PASS, substrate has a reasoning claim that distinguishes it from any memory or RAG system. If FAIL, substrate positioning narrows but engineering-validated capabilities remain.
- **Owner**: research drill returns; exp_dev refines + ships at production-scope envelope; ~2-3 week experiment.

**Direction 6: Hierarchical concept formation**
- **Why dispatched**: cheap INSTRUMENTATION drill on EXISTING V2 24h workload accumulated substrate state (K=2000+ facts; no new experiment needed). Measures whether substrate's internal codebook geometry shows emergent conceptual clustering distinct from corpus-statistical artifacts.
- **Drill scope**: operationalize hierarchical concept formation (SVD spectrum, codebook clustering, bind-then-query); measurement protocol on existing W; null-distribution discrimination (shuffled facts); dense-RAG baseline; falsifiable predictions; substrate-physics vs corpus-property discrimination.
- **Distinctiveness**: MEDIUM-HIGH. If PASS, substrate has a "concept-level queries" capability LLMs / vector DBs can't natively provide. If FAIL, substrate positioning unchanged but rules out a speculative capability.
- **Owner**: research drill returns; exp_dev refines into a 1-2 hour instrumentation script that runs against the post-V2 substrate state; no new experiment design.

**Direction 7: Bet B 4-stage continual learning ret_A rescue**
- **Why dispatched**: HIGHEST-LEVERAGE / LOWEST-NOVELTY-RISK. The doc puts this MEDIUM priority; I rank it HIGH because (a) it's a KNOWN cap_map gap (🟡 PARTIAL at v189 with ret_A=0.745 vs >=0.80 HARD-PASS threshold; B + C clear; A misses by 5.5pp); (b) closing it moves a Tier-1 killer capability from yellow to green; (c) the probe exists and works -- just needs rescue mechanism design. NOT a from-scratch capability test.
- **Drill scope**: catastrophic forgetting literature; Hebbian-compatible rescue mechanisms (decay rules, reactivation/replay, hierarchical encoding, sparsity-isolation, per-stage encoding diversity); 3-5 candidate rescues ranked by Hebbian-compatibility x expected retention_A lift x cost; falsifiable predictions per candidate.
- **Distinctiveness**: HIGHEST PRODUCT-IMPACT. "LLM that genuinely learns from interactions" Tier-1 killer goes yellow -> green if ret_A closes.
- **Owner**: research drill returns; exp_dev refines rescue mechanism into experiment; ~2-3 weeks.

### Tractable but lower priority (NEXT-CYCLE drill candidates)

**Direction 5 (substrate-mediated few-shot learning), SCOPED TO FEW-SHOT GENERALIZATION specifically**
- **Why next-cycle**: build's real-time-learn-then-query benchmark partially covers; separate drill should focus on N-examples-to-unseen-instances generalization (the doc's distinctive claim) not single-fact incremental
- **When**: after substrate-LLM Week 5 eval lands; the build provides baseline data
- **Cost**: ~2 weeks separate from build

**Direction 2: Variable-binding analogical reasoning**
- **Why next-cycle**: classic word2vec-style analogy in substrate's bipolar algebra; well-studied in VSA lit; substrate-distinctiveness comes from AUDIT + edit-isolation overlay, not the analogy mechanism itself
- **When**: after Direction 1 returns; if compositional binding PASSES, analogical reasoning is a natural follow-on at lower marginal cost
- **Cost**: ~2 weeks

**Direction 4: Cross-domain transfer**
- **Why next-cycle**: requires multi-domain corpus construction (substantial); the substrate-LLM build's TriviaQA + MuSiQue benchmarks are already multi-domain implicitly; substrate-LLM eval results may inform whether cross-domain transfer is in scope
- **When**: after substrate-LLM build Week 5 eval lands
- **Cost**: ~3-4 weeks

### Engineering integrations (testbed scope, research consultation)

**Direction 10: Substrate-native ML explainability**
- **Reframe**: the substrate-LLM build's provenance-citation benchmark already tests this for the LLM-prediction case. Direction 10's ML-PIPELINE-INTEGRATION variant (substrate as audit layer for ML model training data) is a different scope -- testbed Tier 3+ engineering.
- **When**: after substrate-LLM Phase 1 PASS; pilot deployment cycle
- **Cost**: 6-8 weeks per doc; mostly engineering

### Defer with explicit criteria for revisit

**Direction 3: Counterfactual reasoning via geometric manipulation**
- **Defer reason**: substantial design work to define counterfactual operators; substrate's edit-with-impact-prediction (related) was PARKED because SVD-cascade falsifier HARD_FAILED per `project_substrate_killer_features_2026-05-26`
- **Revisit when**: a substrate-physics framework for counterfactual operators emerges, OR the substrate-LLM build surfaces a use case that requires it

**Direction 8: Meta-learning**
- **Defer reason**: highly speculative; hard to even formulate experimentally
- **Revisit when**: research session has slack capacity AND a concrete operational definition emerges

**Direction 9: Causal inference engine**
- **Defer reason**: requires implementing causal binding semantics (substantial new mechanism); orthogonal to current substrate capabilities
- **Revisit when**: substrate-LLM build PASSES and a regulated-industry pilot deployment requests causal-attribution as a feature

**Direction 11: Differential privacy**
- **Defer reason**: substantial cryptographic work alongside substrate work; DP-as-feature is a Phase 2+ ambition per substrate-product-feature row
- **Revisit when**: pilot deployment requires DP (medical / financial regulated context)

**Direction 12: Universal function approximator**
- **Defer reason**: theoretically interesting but practically demanding; closer to academic claim than product capability
- **Revisit when**: substrate-LLM build PASSES and there's a specific product case for ML-as-substrate (e.g., logistic regression with audit chain)

## Sequencing recommendation (not 20-30% allocation)

The doc's "20-30% capability exploration / 70-80% engineering" allocation is arbitrary. Concrete sequencing tied to milestones is more actionable:

**Now (this week, parallel with substrate-LLM Week 0)**:
- 3 Sonnet drills dispatched: Directions 1, 6, 7 (highest-leverage; research-session-owned)
- Drill returns synthesized into routing file proposing experiment designs
- ~$0 cost; main-thread synthesis

**Next 2-3 weeks (parallel with substrate-LLM Week 1-2)**:
- Direction 7 (Bet B ret_A rescue) experiment ships via exp_dev once mechanism design lands
- Direction 6 (hierarchical concept formation) instrumentation script runs against post-V2 substrate state
- Direction 1 (compositional binding) experiment design refined; ships at production scope

**Next 4-6 weeks (parallel with substrate-LLM Week 3-5)**:
- Direction 5 (few-shot generalization) drill dispatched after substrate-LLM build's bespoke benchmarks return baseline data
- Direction 2 (analogical reasoning) drill dispatched if Direction 1 PASSES
- Direction 4 (cross-domain transfer) candidacy assessed after substrate-LLM Week 5 multi-corpus eval data

**After substrate-LLM Phase 1 PASS (Week 6+)**:
- Direction 10 (ML explainability ML-pipeline-integration variant) testbed engineering
- Direction 11 (DP) if pilot deployment requires
- Direction 3, 8, 9, 12 revisited based on Phase 1 results + market signal

## Cap_map implications

If the 3 dispatched drills land favorably, the cap_map gets these new rows (proposed to orchestrator via routing):

- **Compositional binding algebra at production scope** -- NEW capability row, initial P-band TBD pending drill return
- **Hierarchical concept formation** -- NEW capability row OR sub-row under "Concept structure", initial P-band TBD
- **Bet B 4-stage continual learning ret_A>=0.80** -- existing 🟡 PARTIAL row promotion to 🟢 GREEN gated by ret_A closure

## Internal cross-refs

- `notes/substrate_capability_map.md` line 123 (Bet B 4-stage @ ret_A=0.745); line 133 (real-time-learning v191 ✅); v228 NOVEL CLASS rejection (compositional probes at conservative scope)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (build that already partially covers Directions 5, 7, 10)
- `notes/research_substrate_llm_aggressive_eval_v1_2026-05-31.md` (aggressive eval that locked the 4 bespoke benchmarks)
- `project_substrate_killer_features_2026-05-26.md` (5 product-layer killer features; alignment check)
- `project_substrate_strategic_inversion_48h_2026-05-26.md` (24-36mo competitive window context)

## Method note

This is an audit + dispatch turn, not a synthesis turn. The synthesis routing file is filed when the 3 drills return. ~20 min main-thread audit; 3 Sonnet drills running in parallel (~45 min each). Token-efficient pattern reconfirmed for 3-direction-multiplex drills.

Per [[feedback-no-padding-experiments]]: dispatched 3, not 12. The 12-direction list is a long-term backlog; selecting top-3 by leverage x tractability x distinctiveness avoids padding. Per [[feedback-no-smoke]]: doc's recommendations honestly evaluated; Direction 5 partial-duplication flagged not buried; Direction 7 elevated above doc's medium-priority framing because cap_map state warrants it; speculative directions (3, 8, 9, 11, 12) deferred with explicit criteria not silently dropped.
