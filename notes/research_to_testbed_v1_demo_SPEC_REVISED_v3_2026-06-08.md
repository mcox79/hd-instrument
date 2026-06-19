# Research -> Testbed: v1 demo SPEC REVISED v3 (3-mode toggle: Default / Cost-efficiency / Compliance)

**From:** Research  **Date:** 2026-06-08 ~19:00 UTC
**Re:** Demo concept refined through 3 rounds of user critique. Final version: 3-mode demo
serving 3 distinct audiences. RESCINDS SPEC v1 + v2.

## What changed across SPEC iterations

| Version | Concept | Critique that drove revision |
|---|---|---|
| v1 (12 wow moments) | Side-by-side gpt-4o-mini vs substrate-enhanced; 5+ wow panels | User: "looks like better RAG; investor would say who gives a shit" |
| v2 (tiny LLM + 200M KB) | Qwen-1.5B + substrate vs gpt-4o-mini; context-window pitch | User: "real demo user will push complex questions; small LLM will look bad; also how do we guarantee deletion?" |
| **v3 (3-mode toggle)** | **Default safe + Cost-efficiency + Compliance modes; each addresses specific concern** | THIS SPEC |

## 3-mode demo architecture

### Mode 1: DEFAULT (always-loaded; investor-safe; conversational-safe)

**Panels:**
- Left: bare gpt-4o-mini
- Right: gpt-4o-mini + substrate (Tier 1 RAG with substrate's smart retrieval)

**Why this is the default:**
- SAME LLM both sides → generation quality matched → only knowledge differs
- Demo user can ask Claude-like complex questions → never embarrassing rough output
- Substrate's value-add is purely the knowledge differential
- Robust for live demos where users push unpredictable queries

**Visible to user:**
- Same query both panels
- Substrate panel: faster on multi-hop / has post-cutoff facts / shows audit chain
- Bare panel: standard gpt-4o-mini behavior
- Cost ticker (similar; substrate marginally cheaper via focused context vs Wikipedia-dump RAG)
- Substrate stats sidebar (200M facts loaded; X shards; last sleep-defrag)

### Mode 2: COST-EFFICIENCY (toggle; investor-pitch focused)

**Panels:**
- Left: bare gpt-4o-mini ($$$  per query)
- Right: Qwen-2.5-1.5B local + substrate ($0 marginal cost)

**Why this toggle:**
- Visceral "tiny LLM + huge substrate beats Frontier" cost pitch
- For INVESTOR audiences who care about AI economics
- Cherry-picked knowledge-heavy queries where substrate's facts win
- Caveat shown clearly: "small LLM may produce shorter answers; substrate provides accuracy"

**Visible to user:**
- Same query both panels
- Substrate-side: shorter / less polished prose; correct facts via substrate
- Cost ticker: dramatic gap (substrate-side $0; gpt-4o-mini per-query API cost)
- Latency comparable

### Mode 3: COMPLIANCE (toggle; regulated-industry / data-residency pitch)

**Panels:**
- Left: bare gpt-4o-mini API ("your data goes to OpenAI")
- Right: Local Qwen-1.5B + Tier 5a substrate-KV ("zero external network traffic")

**Why this toggle:**
- Categorical advantage for HIPAA / EU AI Act / GDPR / trade-secret use cases
- Tier 5a substrate-KV: facts passed as VECTORS through attention; never serialized to text
- No API calls = data residency by construction
- End-to-end GDPR deletion (substrate erases; LLM has no persistent memory of fact)

**Visible to user:**
- Data path indicator (gray for API mode; green for compliance mode)
- Optional: packet trace showing zero external traffic in compliance mode
- Substrate facts shown as vector representations (compliance LLM attends to vectors not text)
- Honest captions: "facts never serialized for LLM consumption; substrate vectors only"

## 3-tier architecture progression (within each mode)

Within Default/Cost-efficiency modes, the "substrate-enhanced" panel uses Tier 1 RAG (substrate retrieves → injects as text context).

Within Compliance mode, the "substrate-enhanced" panel uses Tier 5a substrate-KV (substrate vectors fed to LLM's attention layer directly; never serialized).

**Tier 4 LoRA is DROPPED.** Tier 5a empirically subsumes most of Tier 4's value (D1/D2/D3 HP at 156x context expansion + size+family agnostic). Tier 4 LoRA was originally planned BEFORE Tier 5a worked; now redundant.

## Hero metric (always visible across all modes)

```
   LLM context window:    128,000 tokens (gpt-4o-mini) / 32,768 (Qwen-1.5B)
   Substrate KB:      197,432,891 facts (and growing)
   Effective ratio:        2,500x more knowledge accessible
   Substrate latency:        0.21ms P95 at 1M facts (PP-150)
   Substrate KB sources:  Wikidata (100M) + Wikipedia (50-200M extracted) +
                           ConceptNet (8M) + arXiv (10-20M) + PubMed (100M+)
```

## Knowledge base ingest (one-time; ~30-40 hours)

**Tier 1 - Structured triples (direct load; ~6-11 hr; ~$0):**
- Wikidata (~100M triples; CC0)
- ConceptNet (~8M assertions; CC-BY-SA)
- DBpedia top subset (~50M triples; CC-BY-SA)

**Tier 2 - Prose extraction (~20-25 hr; ~$0):**
- Wikipedia 5.84M articles (spaCy NER+relation extraction)
- arXiv ~2M abstracts
- PubMed ~30M abstracts

**Tier 3 - Recency overlay (live; ongoing):**
- News APIs (post-cutoff event stream)
- Crunchbase + SEC EDGAR (corporate)

**Total: ~200M+ facts; ~300-400 GB disk; substrate empirically validated PP-98 ladder to 100M; should extend cleanly.**

## Engineering deliverables (revised; integrates Testbed's existing AUDIT progress)

### Already DONE by Testbed (reuse)
- 8 substrate library modules (core/audit/persistence/khop/confidence/cascade/gdpr/bitemporal) — Research VERIFY signed off (with 3 MODIFY + 1 ADD + 2 v1.1 FLAGS)
- FastAPI 13-route skeleton
- Demo-mode toggle (live-verified)
- Pythia-1.4B GPU smoke (validated 2.6 GB VRAM)
- Cloudflare Tunnel setup
- runner toolchain (Python + torch + Node + Cloudflared)

### Still TODO (revised priorities)

**Week 1 (immediate):**
- Apply 3 Research MODIFY items (shards.py threshold; cross_shard.py default; bitemporal.py limitation doc)
- Apply 1 ADD item (inverted.py per-property entity list)
- Wire library into `/query` endpoint (Tier 1 RAG path)
- Demo KB seed (10K facts; smoke test)

**Week 2 (KB ingest + Mode 1 wiring):**
- Wikidata 100M ingest (~5-10 hr)
- ConceptNet 8M ingest (~1 hr)
- Wikipedia 5.84M ingest (~12-15 hr; spaCy NER)
- Mode 1 (Default): gpt-4o-mini both panels working
- OpenAI + Anthropic API keys (user action)

**Week 3 (Mode 2 cost-efficiency):**
- Qwen-2.5-1.5B-Instruct local serving (port D2 substrate-KV scaffold; 4-bit quant)
- Mode 2 toggle: Qwen + substrate vs gpt-4o-mini panel
- Curated query set (30-50 knowledge-heavy queries where Qwen+substrate wins)

**Week 4 (Mode 3 compliance + Tier 5a integration):**
- Tier 5a substrate-KV proper integration (vectors fed to LLM attention; not text RAG)
- Mode 3 toggle: local Qwen + Tier 5a vs gpt-4o-mini panel
- Data path indicator UI
- Optional: packet trace visualization
- arXiv + PubMed ingest (background; non-blocking)

**Week 5 (frontend + UI polish):**
- Hero counter (context ratio; cost; latency; sources)
- Audit chain expansion (Merkle + per-step confidence + provenance)
- Cost ticker (per-mode; live)
- Substrate stats sidebar
- Mode toggle UI
- Mobile responsive

**Week 6 (deployment + materials):**
- Cloudflare Tunnel deploy
- Live demo dry-runs (test each of 3 modes)
- Demo video (3-5 min showing all 3 modes)
- Customer-ready presentation deck
- Investor-ready presentation deck

## Wow moments (supporting; secondary to hero metric)

Available as buttons across modes:
- **Multi-hop chain visualization** — K-hop traversal at 0.21ms; audit chain visible
- **Add a fact** — substrate ingests in 4.174ms; instantly used; LLM cutoff irrelevant
- **GDPR delete** — substrate erases; in compliance mode end-to-end guarantee
- **Counterfactual do() panel** — 20 ready-to-go scenarios per PP-172
- **Sharding contrast viz** — sharded 1.000 vs monolithic 0.060 at 16x load (PP-127)

## Honest failure-mode acknowledgments (built into UI)

- "Small LLM may produce shorter / less polished answers — substrate provides knowledge accuracy"
- "API logs may retain query inputs per provider policy (Default mode)"
- "Compliance mode: no API calls; substrate vectors only; local LLM"
- "Substrate confidence < threshold → 'I don't know' (PP-107 abstention; not hallucination)"
- "Substrate scope: structured public knowledge + your loaded KB; not opinion / creative / general reasoning"

## Success criteria

1. All 3 modes load and toggle cleanly
2. Default mode handles unpredictable user queries without embarrassing failure (gpt-4o-mini both sides as safety net)
3. Cost-efficiency mode demonstrates 100x cost gap on curated 30 queries
4. Compliance mode shows zero external network traffic (verifiable via UI indicator)
5. Hero counter updates live; numbers accurate to within 5%
6. Audit chain renders for >= 95% of substrate-side answers
7. Production demo URL <3s load; <2s query response in each mode
8. Mobile responsive

## Cost envelope (running)

- gpt-4o-mini API: ~$50/month
- Claude Haiku API toggle: ~$20/month
- Crunchbase API: ~$100/month (or free tier)
- News API: ~$50/month (or free tier)
- Vercel hosting: $0-20/month
- Substrate local + Qwen local: $0 (laptop GPU)
- Cloudflare Tunnel: free
- **Total: ~$150-250/month**

## Cross-references
- SPEC v1 (RESCINDED): notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md
- SPEC v2 (RESCINDED): notes/research_to_testbed_v1_demo_SPEC_REVISED_2026-06-08.md
- BUILD PLAN response: notes/research_to_testbed_BUILD_PLAN_response_2026-06-08.md
- Library VERIFY response: notes/research_to_testbed_v1_demo_LIBRARY_VERIFY_RESPONSE_2026-06-08.md
- Tier 5 substrate-KV validation (D1/D2/D3 HP): cycle 185 + cycle 190 + cycle 191
- PP-150 sub-ms latency at 1M: cycle 188
- PP-98 sign-key 100M scale: cycle 187/190
- Wikipedia ingest dry-run validated: cycle 187 (10k) + cycle 190 (100k)

---

**Testbed:** SPEC v3 is final design. 3-mode toggle (Default / Cost-efficiency /
Compliance) addresses all user critiques. Reuse all your AUDIT WEEK 1 work. Week-by-week
plan revised. Standing for your BUILD PLAN response.

This is the demo to build.
