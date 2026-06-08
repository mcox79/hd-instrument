# Testbed v1 Demo BUILD PLAN — 4-6 weeks

**Author:** Testbed
**Date:** 2026-06-08 (REV 1: hosting + PATH A locked)
**Status:** USER-SIGNED OFF on architecture; audit week kicks off after CELL-A2 lands
**Per:** research_to_testbed_v1_demo_SPEC_2026-06-08.md + exp_dev_to_testbed_v1_demo_app_build_handoff_2026-06-08.md + research_to_testbed_BUILD_PLAN_response_2026-06-08.md

## LOCKED ARCHITECTURE (user-signed off 2026-06-08)

- **Hosting**: marsh@home desktop (64 GB RAM, RTX 4060 Ti 8 GB, i5-12400F) hosts EVERYTHING
- **Public access**: Cloudflare Tunnel → free public URL `demo.your-domain.com` or `*.trycloudflare.com`
- **Cost**: $0 infrastructure (desktop already owned; tunnel free) + user-handled API costs only
- **Auth gating** (optional, easy to add): Cloudflare Access → Google login + email whitelist
- **PATH A Tier-5** PRIMARY: Pythia-1.4B (~2.8 GB fp16) runs on desktop 4060 Ti for substrate-KV layer; gpt-4o-mini consumes substrate-KV results
- **Frontend**: Next.js (dark sophisticated style per OpenAI/Anthropic visual language)
- **Backend**: FastAPI on desktop
- **Substrate KB target**: 5-10M facts in 64 GB RAM (sharded)
- **Demo audience**: in-person + remote (laptop / phone / customer browser all hit same URL)
- **Single point of failure**: yes (desktop must be on); acceptable trade for $0 cost
- **Bandwidth**: home upload (~10-100 Mbps); enough for 5-10 concurrent users

## Executive summary

Build a full-stack demo app (FastAPI backend + Next.js frontend) that shows side-by-side
comparison of (a) bare gpt-4o-mini vs (b) gpt-4o-mini augmented with the validated
substrate primitives. 3 always-visible "wow moments" + 2 button-triggered ones. Hybrid
Wikipedia + Corporate Intelligence KB at ~10M facts. 4-6 week timeline.

Substrate-side scientific work is COMPLETE (Research lane). Substrate primitives are
PROVEN as research cells in `experiments/exp_*.py`. The remaining work is engineering:
porting research cells into a production-quality backend library, building the frontend,
ingesting data, deploying.

## Pre-Week-1: AUDIT WEEK (kicks off after CELL-A2 verdict lands)

Concrete pre-engineering tasks (2-3 days):

1. **Substrate primitive portability audit (1 day)**: read each of the 11 PP-* source cells,
   identify core functions, decide direct port vs refactor. Produce dependency graph.
2. **Cloudflare Tunnel setup on desktop (half day)**: `cloudflared` install + auth + tunnel
   config; test from external network. Optionally Cloudflare Access for email-whitelist auth.
3. **Pythia-1.4B + substrate-KV smoke on desktop GPU (half day)**: validate 4060 Ti can hold
   Pythia-1.4B fp16 + substrate-KV layer concurrently. If VRAM tight, fall back to int8 or
   reduce context window. This validates PATH A is viable before committing Week 2 effort.
4. **API key + budget setup (half day)**: user-handled OpenAI + Anthropic accounts; I plug keys
   into the FastAPI env config. Confirm rate limits + budget caps in writing.
5. **Node.js + Next.js + Tailwind on desktop (half day)**: install toolchain; scaffold project;
   confirm hot reload works over LAN + tunnel.
6. **CELL-A2 verdict integration (gated)**: if A2 HARD_PASSes, Wikipedia NER uses Llama-8B
   (with int4 quant for 4060 Ti); if HARD_FAILs, spaCy fallback. Demo ships either way.
7. **Risk register review (half day)**: surface remaining unknowns; revise plan if needed.

## Substrate primitive port plan

Each primitive is a research cell that needs to become a library module:

| Primitive | Source cell(s) | Target module | Risk |
|---|---|---|---|
| **PP-119 K-hop traversal** | `exp_chain3_v1_khop_3shard_gpu_v1.py`, `exp_fact_checked_khop_merkle_chain_hp12_root_v1.py` | `substrate/khop.py` | LOW — research-validated |
| **PP-123 Cascade native-first router** | `exp_cascade_native_first_router_cpu_v1.py` | `substrate/cascade_router.py` | LOW |
| **PP-127/128/129/130 Sharding + MERGE** | `exp_kg_sharding_strategy_compare_gpu_v1.py`, `exp_cross_shard_chain_extraction_cpu_v1.py`, `exp_hierarchical_subshard_kg_cpu_v1.py` | `substrate/sharding.py` | MEDIUM — multiple cells; need consolidation |
| **PP-135 Substrate-KV (Tier 5)** | `exp_d2_pythia1p4b_substrate_kv_gpu_v1.py`, `exp_d3_crossshard_substrate_kv_gpu_v1.py` | `substrate/kv_memory.py` | MEDIUM — needs Pythia 1.4B at inference; GPU cost in demo |
| **PP-125 Two-stage disambig** | `exp_two_stage_disambig_khop_cpu_v1.py` | `substrate/disambig.py` | LOW |
| **PP-107 Cleanup confidence** | `exp_cleanup_confidence_roc_cpu_v1.py`, `exp_calibrated_confidence_ece_v1_n1024.py` | `substrate/confidence.py` | LOW |
| **PP-104 GDPR exact erase** | `exp_delete_downdate_exactness_cpu_v1.py`, `exp_eu_aiact_gdpr_cocompliance_v1.py` | `substrate/gdpr.py` | LOW |
| **Bitemporal as-of** | `exp_bitemporal_asof_1M_v1.py` | `substrate/bitemporal.py` | LOW |
| **Counterfactual do()** | `exp_counterfactual_do_operator_v1.py`, `exp_counterfactual_do_demo_cpu_v1.py` | `substrate/counterfactual.py` | LOW |
| **Mechanism B (inverted shards)** | `exp_inverted_property_shards_cpu_v1.py` | `substrate/inverted.py` | LOW |
| **Mechanism C (cross-shard chain)** | `exp_cross_shard_chain_extraction_cpu_v1.py`, `exp_mechanism_composition_v1_n4096.py` | `substrate/cross_shard.py` | MEDIUM |

**Total port effort estimate: ~3-5 engineering days** for a clean abstraction layer.

## Week-by-week deliverables

### Week 1: Backend foundation (~5 days)

| Day | Deliverable |
|---|---|
| 1 | FastAPI scaffold; project structure; pin dependencies (`pyproject.toml`) |
| 2-3 | Port PP-107 (confidence) + PP-119 (K-hop) + PP-104 (GDPR) + PP-123 (cascade router) into `substrate/` library |
| 4 | `/query` endpoint: bare LLM call + substrate-enhanced call; return JSON with both answers + audit chain |
| 5 | Seed substrate with 10K demo facts; smoke test `/query` end-to-end with gpt-4o-mini |

**Acceptance gate**: `/query` returns JSON with `{bare_answer, substrate_answer, audit_chain, cleanup_confidence, facts_used, cost_per_call, latency}` for at least 5 demo queries.

### Week 2: KB ingestion + scaling (~5 days)

| Day | Deliverable |
|---|---|
| 6-7 | Wikipedia ingest pipeline: parse → NER (Llama-8B or spaCy per CELL-A2 verdict) → triples → substrate.write() |
| 8 | Port PP-127/128/129/130 sharding into `substrate/sharding.py`; scale substrate to 1M facts |
| 9 | Substrate-KV (PP-135) wire-up; test gpt-4o-mini using substrate-retrieved context |
| 10 | Corporate Intelligence overlay: Crunchbase + SEC EDGAR + News API stubs; seed 10K corporate facts |

**Acceptance gate**: substrate at 1M facts, `/query` returns correct results in <2s on multi-hop benchmark queries; corporate overlay has >=10K post-cutoff facts.

### Week 3: Frontend core (~5 days)

| Day | Deliverable |
|---|---|
| 11 | Next.js init; TailwindCSS; routing structure |
| 12 | Side-by-side panel layout (bare LLM vs substrate-enhanced); query input box |
| 13 | Audit chain expansion renderer (Merkle proof + per-step confidence) |
| 14 | Substrate stats sidebar (total facts, shards, last sleep-defrag); cost + latency display per panel |
| 15 | KB selector dropdown (Wikipedia / Corporate / Hybrid); LLM toggle (gpt-4o-mini / Claude Haiku) |

**Acceptance gate**: render correctly for 5 preset queries; mobile responsive; load in <3s.

### Week 4: Wow moment panels (~5 days)

| Day | Deliverable |
|---|---|
| 16 | "Add a fact" modal: NL + structured input; live substrate.write(); demo query against new fact |
| 17 | "Multi-hop with audit chain" preset queries + chain visualization |
| 18 | "Recency check" preset queries (post-April-2024); demo bare LLM saying "cutoff" |
| 19 | "GDPR delete" modal + curated person list; live substrate.surgical_erase(); audit proof |
| 20 | "Scale contrast" chart (D3 or SVG): 12M-facts sphere vs LLM context window dot |

**Acceptance gate**: all 5 wow moments work without cherry-picking; each demonstrates a categorical substrate advantage.

### Week 5: Integration + polish (~5 days)

| Day | Deliverable |
|---|---|
| 21 | Pre-scripted demo scenarios (5 query sequences that always look good); seed data tuned |
| 22 | Cost-per-query tracking (substrate vs bare); cost display formatting |
| 23 | PP-107 confidence display on every substrate answer; "I don't know" rendering |
| 24 | Mobile responsive testing; tablet + phone layout |
| 25 | Smoke tests: end-to-end tests for each `/query`, `/add_fact`, `/delete_facts`, `/scale_stats`, `/audit_chain` |

**Acceptance gate** (REVISED per Research clarification): substrate wins visibly on >=3 of 5 **corporate-recency OR multi-hop** queries (substrate's strength domain); for purely random queries the honest expectation is 50-60% win rate; substrate's pitch is "categorically does things LLM cannot" (add/delete/recency/audit) not "always beats". Mobile renders correctly.

### Week 6: Deployment + materials (~5 days)

| Day | Deliverable |
|---|---|
| 26 | Backend deploy target (Modal recommended for GPU substrate; or Lambda + S3 for state); env config |
| 27 | Vercel deploy frontend; connect to backend API; configure CORS + auth |
| 28 | Domain + HTTPS; production env vars; rate limiting |
| 29 | Demo video (3-5 min walkthrough); presentation deck markdown |
| 30 | Customer-ready dry-run; live demo to internal review; bug list + fix |

**Acceptance gate**: production demo URL works; <3s load, <2s query response, mobile responsive; demo video recorded.

## Architecture decisions

### Locked (per Research SPEC + Exp-Dev handoff)
- FastAPI backend (Python; matches substrate research stack)
- gpt-4o-mini primary; Claude Haiku toggle
- Hybrid Wikipedia + Corporate Intelligence KB
- Side-by-side panel UI
- 5 wow moments (3 primary + 2 secondary)
- Per-query cost + latency + confidence display
- Audit chain rendering

### Proposed (need user signoff)
- **Frontend**: Next.js (vs vanilla React or Vue) — Next.js wins for: SSR for fast first load, mature ecosystem, easy Vercel deploy
- **Backend deploy**: Modal.com (vs Lambda, RunPod, dedicated VM) — Modal wins for: serverless GPU, integrates Python natively, can scale substrate up/down with traffic
- **Frontend deploy**: Vercel free tier (vs Netlify, self-host) — Vercel wins for: zero config Next.js, fast CDN, free tier sufficient for demo traffic
- **Substrate runtime**: Python in Modal Docker container; persist KB to S3/R2 (vs in-memory only) — persistence enables fast restart + correct semantics for "add fact" wow moment
- **State management (frontend)**: Zustand or React Context (vs Redux) — simpler given small state surface
- **Charting**: Recharts or D3 (vs custom SVG) — Recharts simpler; D3 if scale-contrast needs custom animation

### Open
- Corporate data licensing budget: Crunchbase API tier varies $50-$1000+/month; need user to fix budget
- Tier-5 substrate-KV deployment: needs Pythia-1.4B running with substrate KV; per-query GPU compute cost is the biggest unknown
- LLM streaming responses: if we want token-by-token rendering in the UI, both gpt-4o-mini and Haiku support it; adds complexity but feels modern

## Dependencies + blockers

### On Research (incoming)
- Per-dataset substrate-side metrics (HotpotQA / TriviaQA / PubMedQA / BabiLong / WebQSP / CWQ / NELL) for benchmark dashboard
- Substrate-KV (PP-135) Tier-5 inference details — production-ready or research-only?

### On Exp-Dev (incoming)
- Cost-per-query measurements for the cost ratio displayed on each panel
- Cached-dataset benchmarks (already in progress per their note)
- A2 verdict (Llama-8B extractor) — determines Wikipedia NER quality

### On user (incoming)
- **API key allocation**: OpenAI, Anthropic, Crunchbase
- **Monthly budget signoff**: ~$250-300/month per SPEC
- **Tech stack signoff**: confirm Next.js + Modal + Vercel
- **Sign off on this plan** before Week 1 starts

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Substrate cells need significant rewriting to port (currently script-style not library-style) | HIGH | Audit week before Week 1 starts; budget extra days if portability is worse than hoped |
| Substrate-KV (Tier 5) not production-ready | HIGH | Pre-Week-2 readiness check; if not ready, demo uses K-hop only (no Tier-5 KV) and shows the architectural roadmap instead |
| Corporate API costs balloon beyond budget | MEDIUM | Lock budget in writing; choose cheaper data sources (SEC EDGAR is free; News API has cheap tier) |
| Wikipedia NER quality with spaCy fallback is too noisy for multi-hop wow moment | MEDIUM | CELL-A2 verdict gates this; if A2 HARD_FAILs, multi-hop wow moment becomes "structured KB only" instead of "free-text Wikipedia" |
| Demo deploy GPU costs (Modal Pythia 1.4B serverless) exceed budget | MEDIUM | Profile cost-per-query in Week 2; if too high, cache common queries or downsample model |
| Frontend animation (scale contrast chart) eats Week 5 budget | LOW | Use simple SVG with CSS animation first; upgrade to D3 only if time permits |
| API rate limits during demos (gpt-4o-mini, Crunchbase) | LOW | Implement caching; pre-warm common demo queries |
| User has different prioritization for the 5 wow moments | LOW-MEDIUM | User signoff on this plan; can drop secondaries (GDPR, scale chart) if needed |

## What this plan is NOT

- It is NOT a Research strategy plan (Research owns the substrate science; settled)
- It is NOT a benchmark suite build (Exp-Dev owns; in parallel)
- It is NOT a customer outreach plan
- It is NOT changing substrate primitive behavior (the cells are settled; we PORT them)
- It is NOT promising specific HARD-PASS verdicts on the demo's substrate metrics — those depend on KB quality + LLM behavior + benchmark choice

## What I propose user signs off on

1. **The 4-6 week timeline** (acknowledging risks; some slips possible)
2. **The week-by-week milestone structure** (Week 1 backend → Week 6 deploy)
3. **The 3 architecture decisions** (Next.js + Modal + Vercel)
4. **The monthly running budget** (~$250-300)
5. **The risk mitigations** (especially the Tier-5 KV fallback + spaCy fallback for NER)
6. **THE AUDIT WEEK PRE-COMMITMENT** — before Week 1 starts, I do 2-3 days of substrate primitive portability audit + API key + budget setup + risk re-review. Then we kick off Week 1 with eyes open.

## Standing for user

Reply with:
- **"signed off"** + any modifications → I begin the audit week
- **"hold"** + which sections to revisit → I'll revise
- **"different priority"** → we may pivot before commitment

Note: CELL-A2 still running in the background. Verdict will inform Week 2 (Wikipedia NER path).
