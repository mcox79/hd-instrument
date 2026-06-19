# Strategic roadmap: substrate-LLM integration (3-month, v278)

User-delivered strategic synthesis at 2026-05-29 end-of-day. Significant pivot from prior cycle's framing:

> **The bottleneck has shifted. Substrate-physics characterization is mature. The bottleneck now is integration architecture and validation.**

This note captures the 20-item research agenda + 3-month allocation + what's already aligned vs what's missing.

## The strategic pivot

Prior cycle framing: "characterize substrate-physics, discover capabilities, publish findings."

New framing: "**substrate is mature; integration is unstarted; the highest-leverage single experiment is Pattern B (substrate-as-LLM-tool with substrate-mediated outputs) on a regulated-industry use case**."

The single highest-leverage decision: build Pattern B integration with one production use case. Everything else either validates against that integration or extends from it.

## Probabilities (user-stated)

- P(substrate becomes meaningful component in production LLM-based AI systems within 24 months) = 55-65%
- P(substrate becomes category-defining for some segment within 36 months) = 30-45%

Up from prior cycle estimates because operational-layer-invariance synthesis clarified what substrate actually is and how its properties translate to capabilities.

## Honest substrate cannot-do list (canonized)

- Replace LLM generation quality at scale
- Match transformer multi-hop reasoning depth (current d=25-50 cliff)
- Operate as a general-purpose language model
- Handle arbitrary natural-language composition (algebraically constrained)
- Achieve true emergence (substrate behavior mostly predictable from parameters)

Positioning must respect these. Substrate is specialized component, not LLM replacement.

## The 7 intrinsic properties (canonical list)

These are the substrate's structural mathematical primitives that distinguish it from vector databases:
1. Native text/byte operation (encoder cost ~0)
2. Atomic fact granularity
3. Compositional binding algebra
4. LLM-internal representation compatibility (speculative)
5. Parallel retrieval during LLM inference
6. Structural output verification (deterministic, exact)
7. CoT state management

## The 3 integration patterns (canonical)

- **Pattern A (shallow)**: RAG-replacement. Token reduction ~2-5x. Build cost ~3-4 wks. Lower risk, smaller payoff.
- **Pattern B (medium)**: substrate-as-LLM-tool with substrate-mediated outputs. Token reduction ~5-15x. Build cost ~6-8 wks. **THE PRIORITY**.
- **Pattern C (deep)**: integration into LLM inference loop (representation level, parallel retrieval, bounded-context CoT). Token reduction potentially 10-50x. Build cost 6-12 months + LLM-vendor partnership.

## The 20-item research agenda

### Tier 1: Validate the core integration thesis (4-8 wks)

1. **Pattern B integration demo** [HIGHEST PRIORITY] -- regulated-industry document Q&A; full pipeline; measure token consumption, verifiability, audit, latency. ~6-8 wks eng + ~$5-10K API costs.
2. **7 intrinsic property validations** -- one per property; ~1-2 wks each; mostly parallelizable to ~4-6 wks calendar.
3. **End-to-end latency profiling** -- in production-like pipelines; ~2 wks once Item 1 exists.

### Tier 2: Strengthen substrate-physics foundations (6-12 wks)

4. **Coherent multi-hop validation** -- QE-2 from prior cycle; quantum-inspired no-argmax pipeline; ~1-2 wks eng + 3-5 GPU days.
5. **Multi-hop in unexplored phase regions** -- beta > beta_c, very-low-M; ~5-7 GPU days.
6. **BE-1 W-magnitude-operative validation** -- soft-readout + pool-retrieval at quantized precision; resolves v272 over-claim; ~1-2 GPU days.
7. **Internal-layer capability exploration** -- entropy/spectral/Lyapunov/free-probability readouts; ~4-6 GPU days.
8. **Bet B architectural rescue completion** -- gamma-1/2/3; ~3-5 GPU days.

### Tier 3: Production engineering foundation (8-16 wks)

9. **Public library cleanup** -- pip-installable substrate-lm with API, examples, docs, Docker, REST; ~4-6 wks.
10. **Standard benchmark integration** -- CounterFact, zsRE, SequentialEdit, Continual-T0, Split-MNIST, MTEB, BEIR, HotpotQA, MuSiQue; ~3-4 wks harness + ~1 wk per family.
11. **Multi-tenant deployment infrastructure** -- per-customer isolation; KF-3 at production scale; observability dashboard; ~4-5 wks.
12. **PROT-019 verdict_handler implementation + back-validation** -- prevent labeling errors from compounding; ~1-2 wks.

### Tier 4: Strategic positioning (12-24 wks)

13. **Regulatory documentation** -- GDPR Art 17, HIPAA, EU AI Act; lawyer review; ~4-6 wks legal + $50-100K.
14. **Anthropic/OpenAI/Google partnership exploration** -- substrate as memory layer for vendor agentic products; requires Item 1.
15. **Healthcare/legal pilot deployment** -- one regulated-industry pilot; requires Items 1+13; ~3-6 mo.
16. **Hardware partnership exploration** -- Mythic, Sambanova, neuromorphic; ~3-6 mo.
17. **Personal AI on-device deployment** -- consumer device demo; OEM partnership work; ~2-4 mo eng + partnerships.

### Tier 5: Academic publication (optional, parallel)

18. **Editing benchmarks paper** -- NeurIPS/ICLR; 5000+ sequential edits beating ROME/MEMIT/AlphaEdit; ~3-4 wks writing once Items 9+10 land.
19. **Substrate-physics framework paper** -- PRE/JSTAT/JCP; SKAH-M, multi-anchor, two-orthogonal-boundary lattice; ~3-4 wks. **Sagawa-Ueda thread is publication-ready TODAY at 70-80%** per Agent 6 v276 surge.
20. **Auditable memory positioning paper** -- CACM/AI&Law/USENIX-Security; compliance primitives; ~3-4 wks + 2 wks demo scenario.

## 3-month priority allocation (user-specified)

| Weeks | Items |
|---|---|
| 1-4 (Foundation) | Items 1 + 6 + 12 + 4 (parallel) |
| 5-8 (Validation & extension) | Continue 1; add 2 + 5 + 8 (parallel) |
| 9-12 (Production positioning) | Items 9 + 10 + 13 + 7 |
| 13-24 (Partnerships, deployment) | Items 14-17 based on what validated |
| Parallel | Items 18-20 as data becomes available |

## What's already in flight vs what's missing

### Already in flight (aligned with the agenda)

| Item | Status |
|---|---|
| 4. Coherent multi-hop | QE-2 Option-1 smoke shipped + HARD_FAILed (softmax saturation); Option-3 spectral propagation = next-drill per pre-registered plan |
| 5. Multi-hop phase regions | Region C/D probes done at v272 (beta-invariance confirmed; narrows search) |
| 6. BE-1 W-magnitude-operative | Filed as P2 in convergent priorities; Agent 2 forensic clarified the discretization-floor mechanism (need new metric) |
| 7. Internal-layer exploration | kf45_pre_argmax_joint_probe shipped (FIRST Direction B test); spectral readout in queue |
| 8. Bet B architectural | 3 anchors shipped: TP-HDC + gen-replay + MoE-DG-gating |
| 18. Editing benchmarks paper | LLM-1 scaffold exists at Phase-1 (commit d95cf18) |
| 19. Substrate-physics paper | Sagawa-Ueda publication-ready at 70-80% (Agent 6) |
| 20. Auditable memory paper | Compliance positioning analyzed (Agent 7) |

### MISSING -- the big strategic gaps

| Item | Why this matters |
|---|---|
| **1. Pattern B integration demo** | USER-SPECIFIED HIGHEST PRIORITY; not started; we've been characterizing not integrating |
| **2. 7 intrinsic property validations** | None of the 7 has a formal validation; each is engineering work, not GPU/CPU drilling |
| 3. Production-pipeline latency profiling | Cannot start until Item 1 exists |
| 9. Public library cleanup | Substrate is not pip-installable; cannot be evaluated externally |
| 10. Standard benchmark integration | LLM-1 scaffold needs Phase-2 + Phase-3; need other benchmark suites scaffolded too |
| 11. Multi-tenant deployment infra | Substrate has no enterprise deployment model |
| 13. Regulatory documentation | No lawyer engagement, no compliance mapping documents |
| 14-17. Partnerships & pilots | Cannot pursue until earlier work lands |

## The single recommendation

**Build Pattern B integration with one production use case.** Suggested verticals per user: regulated-industry document Q&A in medical literature, legal research, or financial compliance.

This is **6-8 weeks of focused engineering work**, not GPU experiments. It cannot fit in the overnight queue; it's a project-level commitment requiring sustained attention next session.

## Strategic positioning summary (for product cycle handoff)

- Primary: **compliance-grade auditable memory layer** for regulated AI deployments. EU AI Act Aug 2026 collapses window to 3-9 months URGENT.
- Secondary additive: D-Wave classical analog for CTO/innovation-officer persona (Agent B v278 D-Wave research).
- Agentic AI memory: substrate as the memory subsystem agentic LLMs need; "LLM brain + substrate memory" framing; potentially the biggest TAM ($100B+ by 2030).
- Anthropic Memory complementarity: not "better than Anthropic Memory" but "the architecture that enables what Anthropic Memory structurally cannot" -- specialized $5-20B market.
- CoT state management: substrate as the state layer for thousands-step LLM reasoning chains.
- Personal AI on-device: structurally differentiated against Apple/Google/Microsoft cloud-bound personal AI.

## Decision required next session

Concrete decision before substantive work resumes: **which production use case for Pattern B?**

Three candidates per user:
- Medical literature Q&A (HIPAA + clinical decision support; high stakes; high regulatory)
- Legal research (attorney-client privilege + eDiscovery; clear audit story)
- Financial compliance (SOX + GDPR + AML/KYC; clear cost ROI story)

Each has different partner-acquisition pathway, different compliance complexity, different demonstration aesthetics. Picking one is the single most important strategic choice in the next 3-month cycle.
