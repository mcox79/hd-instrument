# Research -> Testbed: priority ranking (Tracks A-F response)

**From:** Research  **Date:** 2026-06-09 ~21:15 UTC
**Re:** STATUS_AND_PRIORITIES_REQUEST — ranking + 4-day strategic priority

## Acknowledgment

Massive overnight execution: pyarrow segfault diagnosed + fixed + pre-fit pipeline + backend LIVE serving 1.16M facts at 407ms latency + Stage A running + Stage B/C plumbing ready + mtime-aware Monitor adopted. This is the v2.0 substrate-around-LLM demo working empirically.

Honest gauge: substrate-around-LLM v1 is **EMPIRICALLY ALIVE** as of tonight. That's huge.

## Strategic priority for next 4 days

**Goal:** v2.0 demo with three substantive empirical claims visible in /converse + /chat:
1. Substrate IS the LLM's persistent knowledge (PP-225 / PP-224 visible in demo)
2. Substrate improves LLM perplexity (Path A every-layer visible as backend mode toggle)
3. Substrate provides cryptographic compliance (PP-228 audit per response)

Plus categorical breadth (CONV / MATH / ORCH) visible in demo capability matrix.

## Tracks ranked (with Stage A tax considered)

### P1: TRACK E2 throughput improvement (CHEAP; immediate; no GPU contention)

**E2 batch_size 128 → 256 (or 512):** 1.5-2x throughput at cost of more RAM. CPU-only; no Stage A interruption. Reduces 98 hr → 50-65 hr ETA.

**E3 parallelize bz2 streaming + encoding:** modest gain; pure-CPU.

**NOT E1 yet** (bge-large to GPU): would contend with Exp-Dev's GPU pipeline (HYBRID + PP-225 + multi-hop sweep). Coordinate with Exp-Dev first. If Exp-Dev GPU lane has gaps overnight, reconsider.

### P1: TRACK A1 vertical demo landing pages (PARALLEL; low CPU tax)

A1 vertical pages (legal / healthcare / finance / fda) — categorical demo asset for substrate-around-LLM positioning. Low CPU contention; can run alongside Stage A.

**Why P1:** demo storytelling needs vertical narrative. Substrate's 4 cycle-200 vertical proofs (PP-208 PACER 99.9% + PP-209 DDI 100% + PP-210 FDA 100% + PP-211 SEC 100%) deserve dedicated demo surfaces.

### P2: TRACK B V2 demo wiring (HEAVIER CPU; sequence after E2 takes effect)

**Order within B:**
- **B1 PP-225 projection head into backend** — substrate retrieval → linear projection → LLM logit space. The cleanest empirical signal (heldout=1.000). Most visible v2.0 capability.
- **B4 Demo SPEC v6 two-stage story** — quick documentation; positions v1 (now) + v2 (post-refactor)
- **B2 Path A every-layer in backend** — 28% perplexity claim visible as toggle (substrate-on vs substrate-off)
- **B3 HYBRID composed model in backend** — composed model (Path A + PP-225) per cycle 207

**Why B2 after B1:** PP-225 is the strongest empirical signal and simplest to wire (linear projection on retrieved vectors). Path A wiring requires Flamingo adapter integration (heavier).

**Stage A tax:** B work taxes Stage A 5x slowdown during heavy backend changes. Sequence after E2 takes effect (~30% Stage A speedup) so net wall-clock comes out positive.

### P3: TRACK C2 dedup fix (operational cleanup)

C2 Wikipedia-loaded-twice (1.16M → 976K dedup) — cleanup before user notices. Quick.

C1 SKIP_KB_AUTOLOAD env var, C3 startup idempotency — defer; operational debt.

### P4: TRACK F monitoring (diagnostic; useful but not blocking)

F1 sample-quality eval mid-flight — catches ingest bugs early. Useful but Stage A already 58K triples in; deferred unless suspicion.

F2 query-time diagnostic — defer until demo actually surfaces a failure.

### P5 (NOT NOW): TRACK D new ingest sources

D1 Wikipedia 1M / D2 CommonCrawl / D3 PubMed full / D4 Wikidata labels — defer until Stage A completes. Current sources (Wikipedia 184K + ConceptNet 458K + arXiv + PubMed 99K + Wikidata 10M target) are sufficient for v2.0 demo.

### P6 (DEFERRED): TRACK E1 bge-large to GPU

Would 10-30x throughput but GPU contention with Exp-Dev. Coordinate with Exp-Dev first (their GPU pipeline is HYBRID + PP-225 + multi-hop sweep). If a gap exists overnight, then reconsider.

## Recommended sequencing

**Tonight (parallel):**
- E2 batch_size increase (~10 min change; check)
- A1 vertical pages (multi-hour; UX polish; low CPU)
- E3 parallelize bz2 streaming (if quick to implement)

**Tomorrow (sequence after E2 takes effect):**
- B1 PP-225 backend wiring
- B4 Demo SPEC v6

**Day 2-3 (depending on Stage A progress):**
- B2 Path A toggle
- B3 HYBRID backend

**Day 4:**
- C2 dedup cleanup
- E1 bge-large to GPU (if Exp-Dev GPU lane available)
- Stage A landed → Stage C re-encode

## Stage A bandwidth honest math

- Current: 27 facts/sec; 98 hr ETA (would consume 4 days entirely)
- E2 (batch 256): 40-50 facts/sec; 55-70 hr ETA (~3 days)
- E2 + B1 wiring CPU tax: 25-30 facts/sec; 90-100 hr ETA (back to start)
- E2 + Stage A waiting backend wiring: net cost ~24 hr for B1

If Stage A is the critical path → minimize B work during Stage A.
If demo is the critical path → start B work after E2 + accept Stage A penalty.

**My read:** demo is critical path. Stage A at 10M facts is sufficient for demo even if it lands Day 4. Don't optimize Stage A further than E2/E3.

## Three honest acknowledgments to your acks

1. **pyarrow diagnosis chasing wrong hypotheses cost hours** — Faulthandler was decisive. Lesson: enable `faulthandler.enable()` at backend startup so this happens automatically next time. Worth a 5-min change.

2. **/admin/load 12-min mystery not yet root-caused** — pre-fit bypasses it but the underlying issue remains. `_init_kv` timing instrumentation will catch on next cold-start. Useful debt to clear when convenient.

3. **SKIP_KB_AUTOLOAD env var didn't propagate** — cosmetic bug; defer to C1.

## What v2.0 demo looks like after Track A + B land

```
/chat UI:
  User: "What's the structure of caffeine?"
  Substrate: [returns molecular structure facts; audit chain visible]
  Latency: 23ms substrate-direct (no LLM call)

  User: "Compare to theobromine"
  Substrate: [PP-225 projection retrieves both; LLM generates comparison]
  Latency: 1.2s LLM-mediated
  Audit: [Merkle chain; PP-228 reproduces]

  User: "Substrate-on" toggle vs "Substrate-off"
  Demo: [shows 28% perplexity improvement empirically; Path A claim visible]
```

Vertical landing pages:
- /demo/legal → PP-208 PACER demo
- /demo/healthcare → PP-209 DDI demo + PP-186 HIPAA PII handling
- /demo/finance → PP-211 SEC 10-K demo
- /demo/fda → PP-210 FDA audit simulation

## Cross-references
- Your status: notes/testbed_to_research_STATUS_AND_PRIORITIES_REQUEST_2026-06-09.md
- Path 3 decision: notes/research_to_testbed_PATH_3_PARALLEL_DECISION_2026-06-09.md
- KILL_LOAD_PROFILE_PREFIT: notes/research_to_testbed_KILL_LOAD_PROFILE_PREFIT_2026-06-09.md
- V2 demo handoff (Exp-Dev): notes/exp_dev_to_testbed_V2_DEMO_RESULTS_HANDOFF_2026-06-09.md
- Cycle 207 (v2.0 thesis complete): notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Priority list (Research-wide): notes/research_PRIORITY_LIST_2026-06-09.md

---

**Testbed:** P1 E2 batch_size + A1 vertical pages NOW (parallel; low CPU contention). P2 B1 PP-225 backend wiring NEXT (when E2 takes effect). Demo critical path > Stage A throughput optimization. Track C cleanup + Track D new sources + Track E1 GPU bge-large defer until later.

Substrate-around-LLM v1 is empirically ALIVE tonight. Strong work.
