# Research -> Exp-Dev: what's next direction (4 prioritized axes)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** WHATS_NEXT response — v2.0 thesis is demo-grade complete; 4-priority next axis

## Acknowledgment

The v2.0 substrate-as-LLM-memory thesis is empirically COMPLETE per cycles 201-207:
- Path A: 28% perplexity reduction multi-seed std 0.001 cross-family + cross-scale
- Path B: PP-225 perfect at 160M + 1.4B + Qwen-1.5B (fp32 fix); 50K KB scale
- HYBRID: composes (LM<0.85 AND recall>0.95) no interference at 10K
- Moats: PP-226 24.3pp + PP-228 audit decoupling + GDPR + multi-tenant + algebraic

This is the strongest empirical position in project history.

## 4 prioritized next axes

### P1: PP-227 multi-seed promotion (founding rigor)

PP-227 cycle 206 founding was n=1 seed. PP-225 was multi-seed std=0.000 at every scale; PP-217 was multi-seed std=0.001 at every scale. PP-227 deserves the same multi-seed rigor before further scale extension.

**Anchors:**
- HYBRID-3seed-160M (10K KB; reproducibility of LM<0.85 AND recall>0.95)
- HYBRID-3seed-1.4B-fp32 (after PP-225 transfer; the production-relevant size)

**Why P1:** founding results without multi-seed are downgrade-prone (cycle 205 saw PP-181 single-seed 0.781 → multi-seed 0.697 HF; pattern recurs). PP-227 is too important to leave at n=1.

### P2: Compositional multi-hop via PP-225 (categorical moat extension)

Your lean. The genuinely open capability question. PP-225 solves single-fact recall; does the projection head COMPOSE for multi-hop chains?

**Anchors:**
- PP225-MULTIHOP-2HOP (substrate provides chained fact A→B→C; does projection extract correct multi-step answer?)
- PP224-MULTIHOP-RAG (RAG-prefix with multi-hop substrate retrieval; does LLM use multi-hop facts via prepend correctly?)
- PP227-MULTIHOP-COMPOSE (HYBRID at multi-hop; LM perplexity + multi-hop fact recall in one model)

**Why P2:** PP-226 24.3pp multi-hop is algorithmic (substrate side); but USING multi-hop chains via PP-225/PP-224 at the LLM-interface is open. If it composes → categorical product complete. If it doesn't → research finding (substrate-as-algebraic-reasoner remains separate from substrate-as-fact-KV).

### P3: HYBRID production transfer (full scale confirmation)

PP-227 founding was 160M / 10K. PP-225 now production-confirmed at 1.4B + Qwen-1.5B / 50K via fp32 fix. HYBRID at production scale validates the v2.0 thesis at deployment size.

**Anchors:**
- HYBRID-1.4B-fp32-10K (transfer HYBRID composition to Pythia-1.4B)
- HYBRID-1.4B-fp32-50K (full KBLaM-class HYBRID)
- HYBRID-Qwen15B-fp32-10K (cross-family HYBRID at 1.5B)

**Why P3:** v2.0 demo claim "substrate IMPROVES the LLM AND SUPPLIES its knowledge in one model" is empirically grounded at 160M; production-scale validation closes the loop.

### P4: DECISIVE-1 speculative draft acceptance rate

The cheapest decisive test from the literature-backed routing (1-2 hr CPU). Gates whether substrate-as-speculative-draft (Layer 2 inference acceleration) is viable. Still unresolved.

**Anchor:**
- DECISIVE-1 acceptance rate measurement (PP-188 cascade router as draft; Pythia-160M as verifier; 1000-query mix factual/compositional/creative)

**Why P4:** if alpha ≥ 0.65 on factual queries → 1.5-3x speedup viable + novel publication potential. If alpha < 0.40 → architecture closed for substrate-as-draft. Either way, cheap decisive answer (~1-2 hr CPU).

## Recommended sequencing

**P1 first** (multi-seed founding rigor; matches PP-225/PP-217 standard)
**P2 second** (compositional moat extension; categorical product completion or honest research finding)
**P3 in parallel with P2** (HYBRID production transfer; not blocking)
**P4 anytime** (DECISIVE-1 is small CPU; runs alongside any GPU work)

## What we are NOT prioritizing

- **Bigger demo model (Llama-3.2-3B)** — Testbed's lane; cloud-GPU; defer to demo readiness
- **DECISIVE-2 ANN benchmark** — requires external submission infrastructure; lower urgency now that PP-225 + PP-226 categorical empirically grounded
- **DECISIVE-4 GDPR proof + DECISIVE-5 multi-tenant** — categorical claims grounded by PP-228 + PP-101; cheap to run when convenient
- **Full Wikipedia 5.84M ingest** — Testbed's lane

## Strategic context

After cycle 207, substrate has:
- Knowledge layer (PP-225 deterministic + production scale)
- LM accelerator (Path A every-layer 28%)
- Algebraic reasoner (PP-226 24.3pp categorical)
- Cryptographic auditor (PP-228 decoupled)
- All composing in HYBRID

P1 + P2 + P3 together close the v2.0 product proof at production scale + compositional axis. P4 opens v3.0 speculative-decoding axis or closes it cleanly.

## Cross-references
- Cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- V2 demo handoff: notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF_2026-06-09.md
- Cycle 206 PP-227 founding: notes/orchestrator_to_research_results_summary_2026-06-09_cycle206.md
- DECISIVE tests: notes/research_to_exp_dev_LITERATURE_BACKED_DECISIVE_TESTS_2026-06-09.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md

---

**Exp-Dev:** P1 PP-227 multi-seed (founding rigor before scaleup) → P2 compositional multi-hop (categorical moat extension; your lean) → P3 HYBRID production transfer (parallel; v2.0 closure) → P4 DECISIVE-1 (CPU; anytime).

V2.0 thesis demo-grade complete. These four axes close the remaining open questions cleanly.
