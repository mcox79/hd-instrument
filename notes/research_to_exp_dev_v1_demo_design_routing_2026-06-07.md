# Research -> Exp-Dev: v1 customer-facing DEMO design routing

**From:** Research session
**To:** Exp-Dev (backend) + Testbed (frontend if needed)
**Date:** 2026-06-07
**Re:** User-mandated v1 demo design: two-panel side-by-side webpage with public-LLM
baseline + substrate-enhanced LLM + interactive moat demonstrations.

## Demo architecture

### Frontend: simple two-panel webpage
- Two answer panels side-by-side (baseline LLM vs substrate-enhanced LLM)
- Single query input box at top; same query goes to both
- Results displayed below
- Six interactive moat-feature buttons (see below)
- React or Streamlit; latter likely faster to ship

### Backend: FastAPI monolith
- Per the perf bottlenecks drill's demo-barrier routing (12 engineer-days)
- /query endpoint: dispatches to both LLM panels in parallel
- /add_fact endpoint: live KB updates (substrate side)
- /delete_fact endpoint: live GDPR erasure (substrate side)
- /reasoning_chain endpoint: returns Merkle audit chain
- /asof_query endpoint: bitemporal queries
- /inconsistency_check endpoint: adversarial contradiction detection
- /knowledge_update_speed endpoint: timed comparison

### Baseline LLM (public; eliminates "implementation tricks" criticism)
Default options:
- gpt-4o-mini via OpenAI API ($0.15/1M tokens; trusted brand; same capability class as
  Qwen-1.5B)
- Qwen-1.5B-Instruct via HuggingFace Inference (same model as substrate side; pure
  substrate-vs-no-substrate comparison)
- BEST: user toggle between "vs frontier" (gpt-4o-mini) vs "vs same-LLM" (Qwen-1.5B)

### Substrate-enhanced LLM
- Same base LLM as baseline (e.g., Qwen-1.5B)
- + substrate retrieval (pre-trained Wikipedia base layer per pre-training drill)
- + customer demo KB layer (vertical-specific facts)
- + Pattern B compositional retrieval (audit chain attached)

## Six interactive moat demonstrations

These viscerally show what no frontier LLM or RAG can match:

1. **Q&A side-by-side** (static baseline framing) — substrate matches/beats RAG on
   TriviaQA / HotpotQA / PubMedQA / BabiLong

2. **"Add a fact" live demo** — customer types a new fact (e.g., "Acme Corp Q3 revenue
   was $5M"); immediately queryable in substrate panel; baseline LLM can't see it.
   Demonstrates: continual learning + no-fine-tune knowledge updates.

3. **"Delete a fact" GDPR demo** — customer deletes a fact; substrate panel immediately
   reflects deletion (re-query shows fact gone); baseline LLM still has it baked into
   parametric memory. Demonstrates: Article 17 surgical erasure (cycle 162 HP).

4. **"Show reasoning" audit demo** — substrate shows full Merkle-proven reasoning chain
   with citations per hop + cryptographic proof of step-by-step deterministic execution;
   baseline LLM shows chain-of-thought that diverges between runs (demonstrate side-by-
   side regenerate). Demonstrates: EU AI Act Art 12 audit primitive (cycle 164/166
   K-hop audit replay HP at 100% deterministic + tamper-verified).

5. **"What was true at time T" bitemporal demo** — substrate handles as-of queries
   ("What was Acme Corp Q3 revenue per the system on March 15?"); baseline LLM has no
   temporal grounding for stored facts. Demonstrates: cycle 152 bitemporal capability.

6. **"Inconsistency alert" demo** — customer loads two contradictory facts; substrate's
   adversarial sleep defrag flags them with audit-time report; baseline LLM happily
   uses both and produces incorrect synthesis. Demonstrates: cycle 167 sleep-defrag
   adversarial contradiction detection.

7. **"Knowledge update speed" comparison** — side-by-side timer: add 100 facts to
   substrate (177 ms per cycle 164 measured); fine-tune comparable LLM on same facts
   via LoRA (5-30 min). Demonstrates: ~100x faster knowledge updates (cycle 164/166).

## Engineering scope (3-4 weeks)

- Week 1: FastAPI monolith + 4 core endpoints (/query, /add_fact, /delete_fact, /reasoning)
- Week 2: Frontend 2-panel + 6 interactive buttons (Streamlit recommended for v1 speed)
- Week 3: Pre-trained Wikipedia substrate base layer integration (per pre-training drill)
- Week 4: Demo KB curation + vertical narrative + end-to-end polish

## Demo KB curation

Pick a SINGLE vertical for the demo narrative (most compelling):
- **Medical Q&A** (PubMed-flavored; substrate's biomedical encoder shows; GDPR mattering
  for medical compliance)
- **Legal case research** (case law + audit chain mattering for regulatory)
- **Customer support** (high query redundancy; self-improving routing shows)
- **Technical documentation** (internal docs; audit/erasure for IP-sensitive material)

Recommendation: **Medical Q&A** — covers all six moat demos compellingly + maps to
substrate's strongest validated benchmarks (PubMedQA 95% RAG parity; HIPAA Path D
positioning).

## Strategic positioning

This demo is the v1 product proof-point. Per user "not sending this thing out a virgin":
- Substrate ships with Wikipedia-scale baseline + customer KB layer
- Customer interacts with the system; doesn't just see static benchmarks
- Six moat demos categorically demonstrate what frontier LLM + RAG cannot do
- "Try the substrate vs the baseline yourself" beats "trust our numbers"

## Cross-references

- Perf bottlenecks drill (FastAPI monolith routing): notes/research_to_exp_dev_perf_bottlenecks_v1_1_actions_AUTHORIZE_2026-06-07.md
- Pre-training 3x drill (Wikipedia base layer): notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- K-hop audit replay HP: scorecard cycle 164/166
- Sleep defrag adversarial 3/3 HP: scorecard cycle 167
- PubMedQA v3 95% RAG parity: scorecard cycle 167
- 3-drill unified routing: notes/research_to_exp_dev_3_drills_unified_routing_2026-06-07.md

---

**END.**

**Exp-Dev:** v1 demo is the customer-facing endpoint of all today's empirical work.
Authorize 3-4 week engineering scope per blanket authorization. Demo KB vertical
selection (recommend medical) is the first design decision; everything else flows from
that.

**Testbed:** frontend lane if Exp-Dev's bandwidth is full (Streamlit is simple enough
that either lane works).

This is the COMMERCIAL PROOF POINT for everything today's drilling has established. The
six moat demonstrations are what close enterprise customers.
