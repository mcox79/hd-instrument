# Research -> Testbed: v1 demo concrete spec

**From:** Research  **Date:** 2026-06-08 ~12:45  **Re:** v1 demo build per user-confirmed
design decisions. Concrete spec for Testbed implementation.

## Design decisions (LOCKED)

### LLM choice
- **PRIMARY:** gpt-4o-mini via OpenAI API
- **TOGGLE:** Claude Haiku (parity check; shows model-agnostic substrate value)
- Rationale: cheap (~$50/month demo traffic), widely recognized, known LLM weaknesses
  (April 2024 cutoff, hallucination on long-tail, no multi-hop)

### Knowledge base
- **HYBRID architecture:**
  - **Base:** Wikipedia substrate (5.84M articles; pre-trained per OAS-cleared plan)
  - **Overlay:** Corporate Intelligence (recent post-cutoff facts: M&A / executive
    moves / product launches / earnings; sourced from Crunchbase + SEC EDGAR + news feeds)
- Rationale: Wikipedia catches any query; corporate overlay creates categorical recency wins

### Wow moments (3 PRIMARY always-visible + 2 SECONDARY button-triggered)
1. Add a fact (PRIMARY)
2. Multi-hop with audit chain (PRIMARY)
3. Recency / post-cutoff facts (PRIMARY)
4. Delete a fact (GDPR) (SECONDARY)
5. Scale capacity contrast chart (SECONDARY)

## Architecture

### Backend (FastAPI monolith)

```
[ POST /query ]
  -> input: user question + KB selection (default: hybrid)
  -> substrate-side: cascade router (PP-123)
       -> step 1: substrate K-hop on structured triples (PP-119)
       -> step 2: if cleanup_confidence (PP-107) < threshold, fall back to fuzzy retrieval
       -> step 3: Tier-5 substrate-KV memory backbone (PP-135) feeds LLM
  -> LLM-side: same gpt-4o-mini, two calls:
       (A) bare LLM (no retrieval)
       (B) LLM + substrate-retrieved context (Tier-5 KV + K-hop chain)
  -> response: { bare_answer, substrate_answer, audit_chain, cleanup_confidence,
                 facts_used, cost_per_call, latency, substrate_stats }
```

Validated substrate primitives wired:
- K-hop traversal (PP-119; 2-hop 0.805 / 3-hop 0.735 on discrete; 1.000 with sharded)
- Cascade native-first router (PP-123; 0.853 at 48% cost)
- Per-subject + per-relation + per-customer sharding (PP-127/128/129/130 + MERGE)
- Substrate-KV memory backbone (PP-135 31x context expansion)
- Cross-shard scatter-gather (PP-130 100% transparent)
- Mechanism B inverted property shards (set queries)
- Mechanism C cross-shard chain extraction (sleep-defrag pre-computed chains)
- Two-stage disambig hybrid (PP-125; 0.820)
- Anti-hallucination (PP-107 AUC=1.0 cleanup confidence)
- GDPR exact erasure (PP-104; 0.0004ms/delete)
- Bitemporal as-of queries (0.003ms at 1M)
- Counterfactual do() operator (cycle 175 HP)

```
[ POST /add_fact ]
  -> input: structured triple (s, r, o) OR natural language fact
  -> NER + relation extraction if NL (Path B Llama-8B pending; spaCy fallback)
  -> substrate.write() via SMW pinv (4.174 ms/update at 1M)
  -> response: { fact_id, audit_hash, shard_id }

[ POST /delete_facts ]
  -> input: entity name
  -> substrate.surgical_erase() via cycle 162 mechanism + GDPR PP-104
  -> response: { deleted_count, audit_proof, verification_remaining_recall_unchanged }

[ GET /scale_stats ]
  -> response: { total_facts, shard_count, per_shard_capacity, llm_context_limit, ratio }

[ GET /audit_chain/{query_id} ]
  -> response: { K_hop_chain, facts_used_per_hop, merkle_proof, cleanup_confidence_per_step }
```

### Frontend (Next.js or simpler React/Vue)

**Page 1: Main side-by-side panel (always default view)**

```
+--------------------------------------------------------------------+
| [Query input box] [Send] [Reset]   KB: [Wikipedia + Corporate v]  |
+--------------------------------------------------------------------+
|              BARE LLM              |      SUBSTRATE-ENHANCED       |
| (gpt-4o-mini, no retrieval)        | (same LLM + substrate context)|
|------------------------------------|--------------------------------|
|  [answer text]                     |  [answer text]                 |
|                                    |                                |
|  cost: $0.0012                     |  cost: $0.0008 (substrate saves|
|  latency: 1.2s                     |        $0.0004)                |
|  cutoff: April 2024                |  latency: 0.8s                 |
|                                    |  confidence: 0.97 (PP-107)     |
|                                    |  [show audit chain v]          |
+--------------------------------------------------------------------+
| 12,847,392 facts loaded in 8,541 shards | last sleep-defrag: 2h ago|
+--------------------------------------------------------------------+
| [Wow moments]:                                                     |
| (+ Add a fact)  (Multi-hop) (Recency check) (GDPR delete) (Scale)  |
+--------------------------------------------------------------------+
```

**Audit chain expansion (substrate panel):**
```
| > Step 1: Q -> entity "OpenAI"           [shard: companies/OpenAI] |
|   Confidence: 0.99                                                 |
| > Step 2: OpenAI -> CEO -> Sam Altman   [Pattern B binding]        |
|   Confidence: 0.98                                                 |
| > Step 3: Sam Altman -> previous_role  [shard: people/SamAltman]   |
|   Confidence: 0.95                                                 |
| Merkle proof: 0x7a... (verifiable)                                 |
```

### Wow moment panels

**1. Add a fact (modal or expansion):**
- Text input: "Add a fact in natural language" (e.g., "Anthropic released Claude 4.6 in June 2026")
- OR structured input: subject / relation / object
- Substrate immediately processes; shows new shard or updated shard
- Sample query auto-generated to demonstrate substrate uses new fact
- Bare LLM shown saying "I don't have information about [new entity]" or hallucinating

**2. Multi-hop with audit chain (already-included core):**
- Always toggleable on substrate panel
- Preset multi-hop queries shown as quick-suggest buttons:
  - "What was the previous role of the CFO of the company that acquired XYZ?"
  - "Who founded the third-largest competitor to OpenAI?"
- Substrate shows step-by-step K-hop chain with confidence per step
- Bare LLM gives single black-box answer

**3. Recency check (button + auto-suggested queries):**
- Predefined post-cutoff queries always available:
  - "What happened at OpenAI in May 2026?"
  - "What was Apple's latest product launch?"
  - "Who's the current CEO of Meta?"
- Substrate has answer (loaded from corporate intelligence overlay)
- Bare LLM either refuses ("my knowledge cutoff is April 2024") or guesses

**4. GDPR delete (button + curated person list):**
- Modal: "Delete all facts about this person" with dropdown of demo-loaded notable executives
- User picks "John Doe" (a demo executive)
- Substrate erases all (Person, John Doe, *) triples; returns audit proof
- Substrate-side queries about John Doe now return "no facts"
- Bare LLM continues to answer about John Doe (training data persistence)
- "Substrate forgets exactly; LLM cannot"

**5. Scale contrast chart (button + visualization):**
- Animated visualization: substrate loaded with N facts vs LLM context window
- Shows N=12M facts as massive sphere; context window as tiny dot
- Substrate answers questions across the 12M; LLM only sees facts that fit in 200-token context
- "Substrate is your LLM's unbounded external memory"

## Data ingestion plan

### Wikipedia base (5.84M articles)
- Source: Wikipedia dump (cached; per CELL-2 v3 plan)
- Processing: NER + relation extraction (Path B Llama-8B if available; spaCy fallback)
- Storage: per-subject shards (PP-128 routing); ~5K shards at average ~1000 entities/shard
- Time: ~7 hours per CELL-2 v3 estimate

### Corporate intelligence overlay
- Sources:
  - Crunchbase API (companies, funding, acquisitions; ~$100/month)
  - SEC EDGAR (public filings; FREE)
  - News APIs (NewsAPI / GDELT; ~$50/month)
  - Wikipedia infoboxes (executive lists, founding info; cached)
- Frequency: weekly ingest job; substrate auto-shards
- Initial seed: 100K corporate facts (companies + executives + products + events 2024-2026)

### Total estimated KB size at v1 demo launch
- Wikipedia base: ~10M facts (after NER+extraction from 5.84M articles)
- Corporate overlay: ~100K initial + ~1K/week ongoing
- Total: ~10.1M facts at launch; growing weekly

## Engineering milestones (4-6 weeks)

### Week 1: backend substrate engine
- FastAPI scaffolding
- Wire validated substrate primitives (K-hop, cascade router, sharding, KV)
- /query endpoint working end-to-end (bare LLM + substrate-enhanced)
- Substrate KB seeded with small demo dataset (10K facts) for development
- Dependency: gpt-4o-mini API key + budget allocation

### Week 2: KB ingestion + scaling
- Wikipedia ingest pipeline (NER+extraction)
- Corporate intelligence overlay seeding (Crunchbase + SEC EDGAR + news)
- Substrate scales to 10M+ facts (sharded; per cycle 185 PP-127 confirmed at GPU S=256)
- Substrate-KV (Tier 5) integrated with gpt-4o-mini retrieval

### Week 3: frontend core panel
- Next.js/React frontend
- Side-by-side panels with audit chain expansion
- Always-on substrate stats sidebar
- Two-panel comparison rendering

### Week 4: wow moment panels
- Add a fact modal + integration
- Multi-hop preset queries + chain visualization
- Recency check preset queries
- GDPR delete modal + curated person list
- Scale contrast chart (D3 or simple SVG)

### Week 5: integration + curated scenarios + polish
- Pre-scripted demo scenarios that always look good
- Cost/latency tracking + display
- Cleanup confidence (PP-107) display on every substrate answer
- Mobile responsive

### Week 6: testing + deployment + presentation materials
- Smoke tests across primary moments
- Vercel deploy (or similar)
- Demo video + walkthrough doc
- Customer-ready presentation materials

## Dependencies on Exp-Dev (benchmark suite)

Testbed needs from Exp-Dev:
- Per-dataset substrate-side metrics (HotpotQA / TriviaQA / PubMedQA / BabiLong / WebQSP / CWQ / NELL)
  for the head-to-head comparison numbers on benchmark dashboard
- Cost-per-query measurements (substrate-side; for the cost ratio displayed on each query)

Coordination: Exp-Dev starting cached-dataset benchmarks immediately per their note.

## Success criteria for demo

1. Lay technical decision-maker types 5 random queries; substrate wins visibly on >=3 of 5
2. Categorical wow moments (add-fact, GDPR-delete, recency) work cleanly without preset cherry-picking
3. Multi-hop audit chain renders correctly for at least 5 preset queries
4. Cost per query for substrate is visibly less than bare LLM
5. Substrate confidence (PP-107) correctly flags when it doesn't know
6. Demo loads in <3 seconds; query response in <2 seconds
7. Mobile responsive (investors may demo on phone)

## Cost envelope

- gpt-4o-mini API: ~$50/month
- Claude Haiku API (toggle): ~$20/month
- Crunchbase API: ~$100/month
- News API: ~$50/month
- Vercel hosting: $0-20/month
- Substrate hosting (local GPU OR Lambda): $0-50/month
- **Total demo running cost: ~$250-300/month**

## What this demo CAN'T do (be honest in pitch)

- Free-text multi-hop precision bounded by extractor (Path B Llama-8B result pending; if HF, demo uses structured KB only for multi-hop wow moment)
- Wikipedia base extraction quality varies (substrate works with what it gets)
- Substrate is NOT going to win on every query (cascade router falls back to bare LLM for synthesis/factoid where LLM is better)
- Specific failure modes shown openly (substrate's "I don't know" via PP-107 is itself a feature)

## Cross-references
- STRATEGIC_PRIORITY routing: notes/research_to_exp_dev_STRATEGIC_PRIORITY_v1_demo_plus_dataset_auth_2026-06-08.md
- Routing split confirmation: notes/research_to_exp_dev_testbed_v1_demo_routing_CONFIRMED_2026-06-08.md
- Exp-Dev demo handoff to Testbed: notes/exp_dev_to_testbed_v1_demo_app_build_handoff_2026-06-08.md
- Cycle 185 full architecture lock (PP-136): notes/orchestrator_to_research_results_summary_2026-06-08_cycle185.md
- North star (functional system beats LLMs): memory/north_star_functional_system_beats_LLMs.md

---

**Testbed:** v1 demo concrete spec per user-confirmed design. 4-6 week timeline.
gpt-4o-mini + Claude Haiku toggle. Hybrid Wikipedia + Corporate Intelligence KB. 3
primary + 2 secondary wow moments. Budget ~$250-300/month running cost.

Exp-Dev supplies benchmark metrics in parallel. Research stands by for blockers /
strategic redirects.

This is the v1 demo per the north star: "deployed system soon that EMPIRICALLY exceeds
LLMs of relative size in clear measurable ways."
