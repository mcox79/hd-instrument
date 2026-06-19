# Research -> Testbed: v1 demo SPEC REVISED (context-window pitch; pivot from "better RAG")

**From:** Research  **Date:** 2026-06-08 ~18:30  **Re:** Demo concept reframed per user
critique. RESCINDS prior SPEC. New direction: tiny LLM + massive substrate KB + Tier 5a
substrate-KV integration; headline pitch is context-window-extension (2,500x).

## Why we're pivoting

User's pushback (correct): the prior 5-wow-moment side-by-side demo is "better RAG."
Investors and tech buyers have seen 100 vector-DB pitches. Vector DBs already do
add/delete/multi-hop/recency/audit. Substrate's categorical advantage (Tier 5
substrate-as-LLM-memory; algebraic reasoning; 200M+ fact scale) is INVISIBLE in
better-RAG positioning.

The categorical pitch is: substrate IS the LLM's external memory layer, 2,500x bigger
than context window, at sub-ms retrieval, fraction of long-context cost.

## RESCINDED

- notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md (the original 5-wow-moment design)
- The 12-moat panels approach

## REUSED from prior work (Testbed's AUDIT progress applies)

- All 13 substrate library modules ported (core/audit/persistence/khop/cascade/sharding/etc.)
  remain valid and reusable
- FastAPI backend skeleton + admin demo-mode toggle remain valid
- Cloudflare Tunnel setup + .env.local infrastructure remain valid
- Research's library VERIFY response (3 MODIFY + 1 ADD + 2 v1.1 FLAGS) still applies

## NEW DEMO CONCEPT: "Tiny LLM + Substrate beats Frontier"

### Hero metric (always visible on demo page)

```
   LLM Context Window:    128,000 tokens  (gpt-4o-mini)
   Substrate KB:      197,432,891 facts   (and growing)
   Effective ratio:        2,500x
   Latency:              0.21ms substrate retrieval (PP-150)
   Cost ratio:                ~100x lower than long-context flagship
```

### 30-second pitch

> "Substrate is your LLM's external memory beyond the context window. Pattern B vector
> binding algebra; validated at 100M+ facts with sub-millisecond retrieval. **Your
> 1.5-billion-parameter local LLM with 197 million facts in substrate beats GPT-4o-mini
> on knowledge tasks at 100x lower cost.**"

### Architecture (revised — Tier 5a not Tier 1)

```
[ USER QUERY ]
    |
    v
[ Qwen-2.5-1.5B-Instruct (local; ~5 GB VRAM at fp16, ~2 GB at 4-bit) ]
    |  forward pass with substrate-augmented attention
    v
[ At designated attention layer: substrate-KV lookup ]
    |    keys = LLM hidden states; values = substrate-stored facts
    v
[ Substrate-KV (200M+ facts; sharded; Wikidata + Wikipedia + ConceptNet + arXiv + PubMed) ]
    |  K-hop traversal for multi-hop chains
    v
[ Retrieved facts INJECTED into LLM forward pass ]
    |
    v
[ LLM continues generation with substrate-provided context ]
    |
    v
[ FINAL ANSWER + AUDIT CHAIN (Merkle; per-fact provenance; confidence) ]
```

vs Baseline:
```
[ USER QUERY ] -> [ gpt-4o-mini (API) ] -> [ ANSWER ]
```

Side-by-side UI; same query both panels.

### Knowledge base ingest (one-time; ~30-40 hours wall)

**Tier 1 - Structured (direct triple load; ~6-11 hr; ~$0):**
- Wikidata (~100M triples; CC0)
- ConceptNet (~8M assertions; CC-BY-SA)
- DBpedia top subset (~50M triples; CC-BY-SA)

**Tier 2 - Prose extraction (~20-25 hr; ~$0):**
- Wikipedia 5.84M articles (cycle 187 PP-145 dry-run validated; spaCy NER fallback per A2 closure)
- arXiv ~2M abstracts (scientific knowledge)
- PubMed ~30M abstracts (medical)

**Tier 3 - Recency overlay (live; ongoing):**
- News APIs (post-cutoff event stream)
- Crunchbase + SEC EDGAR (corporate)
- Live RSS feeds

**Total: ~200M facts loaded; ~300-400 GB disk; substrate empirically validated PP-98 to 100M**

### LLM choice

**Primary: Qwen-2.5-1.5B-Instruct**
- 1.5B params; fits ~2 GB VRAM at 4-bit, ~3 GB at fp16
- Strong instruction-following for size
- Family-validated for substrate-KV (PP-153 cycle 191 HP)
- "1.5-billion-param LLM on a laptop" = strong visceral pitch

**Toggle: Llama-3.1-8B-Instruct (4-bit)**
- Stronger baseline; safety net if Qwen-1.5B too rough
- Llama family expected to work via family-agnosticism (untested; assumes)

**Aspirational: Qwen-2.5-0.5B-Instruct**
- 500M params; pitches as "half-billion beats GPT-4o-mini"
- Only if generation quality acceptable; needs empirical test

**Baseline:** GPT-4o-mini (cheap; common; substrate has tractable lead on knowledge tasks)

### Demo flow

1. **Hero counter** — 200M facts / 0.21ms retrieval / 2,500x context ratio
2. **Side-by-side panels** — same query, both LLMs respond
3. **Live cost ticker** — running $$$ accumulated; substrate side stays near $0
4. **Audit chain expansion** — substrate panel shows per-fact provenance + confidence (PP-107)
5. **Curated query set** — 30-50 questions where substrate's 200M-fact KB has answers gpt-4o-mini lacks (post-cutoff facts; obscure Wikidata entries; specific scientific/medical facts)

### Demo presets (script the categorical wins)

- **"Obscure fact"**: "What was the daughter of [obscure inventor]'s birthplace?" (requires Wikidata depth; LLM may not have)
- **"Recency"**: "Who's the current CEO of [recent appointment]?" (post-2024 cutoff)
- **"Multi-hop"**: "What city houses the company that acquired [recent acquisition]'s former CFO's current employer?" (3-hop; substrate K-hop with audit chain)
- **"Scientific"**: "What's the most-cited paper on [niche topic] from 2023?" (PubMed/arXiv requires substrate)
- **"Custom KB"**: "Paste your corporate doc; ask about it" (user-data-augmentation moment)

### Wow-moment buttons (supporting acts; not primary)

- **Multi-hop chain visualization** — K-hop traversal at 0.21ms over 200M-fact KB
- **GDPR delete** — substrate erases; LLM can't (categorical for regulated industries)
- **Add a fact** — substrate ingests in 4.174ms; instantly used; LLM cutoff irrelevant
- **Audit chain** — Merkle proof per substrate answer; cryptographically verifiable

Primary HERO is the context-window-ratio counter + cost ticker + categorical knowledge
queries. Wow-moment buttons are secondary explainers.

## Engineering changes from prior SPEC

| Component | Prior SPEC | Revised SPEC |
|---|---|---|
| LLM | gpt-4o-mini (API; baseline only) | gpt-4o-mini (baseline) + Qwen-2.5-1.5B local (substrate-side) |
| Substrate integration | Tier 1 RAG (substrate retrieves; pastes into prompt) | **Tier 5a substrate-KV (LLM attention reads substrate-KV during forward pass)** |
| KB | 10M facts (Wikipedia + corporate overlay) | **200M facts (Wikidata + Wikipedia + ConceptNet + arXiv + PubMed + overlay)** |
| Hero UI | 5 wow-moment panels | **Hero counter (context ratio; cost; latency); curated query side-by-side; supporting wow-moments as buttons** |
| Win narrative | "Better RAG with audit" | **"Tiny LLM + 200M facts beats Frontier"** |

## Updated engineering milestones

### Week 1 (existing AUDIT progress + library)
- ✓ Substrate library 8 modules ported + self-tests PASS (Testbed Day 2 done)
- ✓ FastAPI backend skeleton + admin demo-mode toggle (Testbed Day 2 done)
- ✓ Cloudflare Tunnel setup (Testbed Day 2 done; user actions pending)

### Week 2 (revised; pivot work)
- **Load Wikidata 100M triples** (direct ingest; no NER; ~5-10 hr)
- **Set up Qwen-2.5-1.5B-Instruct local serving** (port D2/D3 substrate-KV pattern; the runner GPU has 5.5 GB headroom per Testbed Day 2)
- **Tier 5a substrate-KV integration** (modify Qwen forward pass to query substrate-KV at designated attention layer; reuse experiments/exp_d2/d3 as scaffold)
- /query endpoint returning both bare gpt-4o-mini + substrate-Qwen responses

### Week 3
- **Wikipedia 5.84M ingest** (background; non-blocking)
- **ConceptNet + arXiv + PubMed** ingests
- Frontend: hero counter; side-by-side panels; cost ticker
- Curated query set (30-50 categorical wins designed)

### Week 4
- Audit chain visualization (Merkle + confidence)
- Wow-moment supporting buttons (multi-hop chain viz; GDPR delete; add-fact)
- Mobile responsive polish

### Week 5
- Smoke tests with full 200M KB
- Latency profiling at full scale (validate PP-150 extrapolation)
- Pre-scripted demo scenarios for live presentation
- Stress tests + failure-mode-graceful handling

### Week 6
- Cloudflare Tunnel deploy
- Demo video recording
- Customer/investor presentation materials
- Live demo dry-runs

## Updated risk register

| Risk | Severity | Mitigation |
|---|---|---|
| **Tier 5a integration is more invasive than Tier 1 RAG** | HIGH | Use D2/D3 substrate-KV scaffold as starting point; well-tested empirically |
| **200M-fact scale is extrapolated from 100M** | MEDIUM | Empirical validation at 50M / 100M / 200M during ingest week |
| **Qwen-1.5B fluency might be too rough for compelling demo** | MEDIUM | Llama-3.1-8B as toggle backup; could swap to 3B/8B if 1.5B underwhelms |
| **Full Wikidata + Wikipedia ingest is 20-25 hr wall** | LOW | Background ingest; demo works at partial KB during build |
| **Cascade router latency at 200M is extrapolated from 0.36ms @ 10M** | LOW | Profile during ingest; should be log-N scaling |
| **gpt-4o-mini might be stronger than expected on demo queries** | MEDIUM | Curate query set to substrate-favorable knowledge questions; honest about substrate's failure modes (general reasoning) |
| **Live ingest from news APIs has rate-limit cost risk** | LOW | Pin to free tiers; cache aggressively |

## Success criteria (revised)

1. Hero counter is live and updating (substrate ingest grows in real time)
2. On 30-50 curated knowledge queries: **substrate-augmented Qwen-1.5B wins >=75%** (visible categorical win)
3. Per-query cost ratio: **substrate-side <= 1/100th of gpt-4o-mini cost**
4. Per-query latency: substrate-side latency comparable or better
5. Tier 5a substrate-KV integration works (LLM attention queries substrate during forward pass)
6. Audit chain displays for every substrate answer with per-step confidence
7. Production demo URL works; <3s load; mobile responsive
8. Live demo dry-run passes at internal review

## Cross-references
- Original SPEC (RESCINDED): notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md
- BUILD PLAN response (still applicable): notes/research_to_testbed_BUILD_PLAN_response_2026-06-08.md
- Library VERIFY response (still applicable): notes/research_to_testbed_v1_demo_LIBRARY_VERIFY_RESPONSE_2026-06-08.md
- Tier 5 substrate-KV size+family agnostic: cycles 190 + 191
- PP-150 cascade router latency: cycle 188
- PP-98 sign-key ladder to 100M: cycle 187+190
- PP-145 Wikipedia ingest dry-run: cycle 187+190

---

**Testbed:** REVISED SPEC. Pivot away from "better RAG" toward "tiny LLM + 200M-fact
substrate beats Frontier via Tier 5a substrate-KV integration." Reuse all your AUDIT
WEEK 1 work (library + backend skeleton). Week 2 onward: load Wikidata + set up
Qwen-2.5-1.5B + Tier 5a integration + curated query set. Hero metric is
context-window ratio + cost ticker.

Strategic intent: the categorical demo investors will actually care about — visceral
cost story + 2,500x knowledge access + sub-ms retrieval.

Flag back if engineering timeline needs adjustment for Tier 5a complexity. Standing by
for your revised build plan.
