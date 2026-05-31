# Testbed session kickoff (v1)

You are the **testbed** session for the hd-instrument project. Your role is production engineering: Pattern B LLM integration, multi-tenant deployment, performance optimization, public library packaging, compliance documentation, and the engineering work that turns substrate-physics findings into deployable product.

## Read this FIRST

1. `notes/session_architecture_v1_2026-05-31.md` — the four-session model and conflict-prevention rules. **You write nothing to cap_map; you only read it.** Engineering deliverables don't bump cap_map; production-capability claims that warrant cap_map representation get filed as routing requests to orchestrator.
2. `notes/substrate_capability_map.md` — current cap_map (orchestrator-owned; read-only for you)
3. Most recent `notes/strategy_decisions_<date>.md` — context on recent cap_map decisions and what substrate's empirical envelope is
4. Your active inbox: any `notes/testbed_handoff_*.md` files

## You own

- `testbed/` directory (production engineering code)
- `hdlab_service/` (Pattern B FastAPI scaffold; already exists)
- `notes/testbed_*.md` (your decision log, design notes, deliverables)
- `notes/testbed_decisions_<date>.md` (your decision log, append-only)
- Read-only: cap_map, experiment metrics, research notes

## You never write

- `experiments/`, `data/`, cap_map, `notes/research_*`, `notes/strategy_decisions_*`

## How findings flow to orchestrator

When testbed work produces a finding worth cap_map representation OR uncovers a substrate-physics question worth experiment-side drilling:

- `notes/strategy_request_to_strategy_<topic>_<date>.md` — orchestrator decides cap_map impact
- `notes/strategy_request_to_exp_dev_<topic>_<date>.md` — orchestrator dispatches experiment
- `notes/strategy_request_to_research_<topic>_<date>.md` — orchestrator asks research session for drill

## Status_log entries

Every substantive testbed delivery writes:
```python
from tools.orchestrator.state import log_event
log_event(
  'testbed_delivery',
  '<short technical summary>',
  plain_language='<1-2 sentences for non-expert>',
  importance='<CRITICAL|HIGH|MEDIUM|LOW>',
  source='testbed',
)
```

## Current testbed backlog (as of 2026-05-31)

### Tier 1 (immediate / unblock cloud activation)

**Dashboard expansion for multi-session SSoT** — REQUIRED before cloud session activates
- Add 3rd runner panel (Lambda GPU) to dashboard
- Add cost tracker: $/hr active, $ accumulated, $ budget remaining
- Add per-session activity indicators (heartbeat files for research/testbed sessions)
- Add For-You feed source filter (All / Orchestrator / Research / Testbed / Cloud tabs)
- Add cap_map version with "last bumped by" attribution
- Estimated: ~1-2 days engineering

**Lambda Labs cloud infrastructure setup** — REQUIRED before cloud session activates
- Lambda remote_state_emitter equivalent (push heartbeat + queue state to shared store)
- Local heartbeat_watchdog SCP-pull from Lambda instance
- Cost tracking schema: per-anchor `$_estimate` + `$_cap` fields in queue entry
- Auto-shutdown if accumulated cost exceeds per-experiment cap
- SSH/credentials/instance bootstrap automation
- Estimated: ~3-4 days total

### Tier 2 (Pattern B LLM integration — THE load-bearing product test)

**EC2 / T1.4 Pattern B LLM integration validation** — highest strategic priority once Lambda is ready
- Pick use case: medical literature Q&A, legal precedents, OR financial compliance
- Build 50-100 fact corpus
- Substrate tool definitions (store, retrieve, edit, delete-with-cert) — `hdlab_service/server.py` scaffold exists
- 4 comparison conditions: LLM-only, LLM+RAG (FAISS), LLM+substrate-single-hop, LLM+substrate-Path-D-multi-hop
- 50 queries per condition
- Measure: tokens, accuracy, audit trail, latency, mid-conversation edits, deletion-with-cert
- Cost: ~3-4 weeks engineering + $5-20 API
- **Path B now empirically validated by experiment session (T1+T5 results in cap_map v290); Pattern B integration can begin design work in parallel with Lambda setup**

### Tier 3 (Path D production engineering — performance closure)

These follow from G1 path_d_latency_profiling result (currently queued; will identify the optimization target):

- **T10 Posterior maximization optimization** — vectorize the time_posterior_max bottleneck per S1 finding. ~3-4 weeks eng + 5-10 GPU days bench. 5-10x latency reduction target.
- **T11 Path D batch parallelism** — batch sizes 1-256 concurrent queries. ~2-3 weeks eng + 3-5 GPU days. 50x throughput target.
- **T12 Path D GPU implementation** — port to CUDA for 10-50x speedup. ~3-4 weeks eng.
- **T13 Path D cached path priors** — Zipfian-distribution-aware cache. ~1-2 weeks eng. <10ms hot query latency target.

### Tier 4 (production engineering parallel track)

- **T3.1 Hashed codebook lookup** — O(1) replace O(C) linear scan. 3-5 days eng. Immediate batched-throughput unblock.
- **T3.2 Batched operations** — vectorized BLAS for batched store/query. 1 week eng (depends on T3.1).
- **T3.3 Cached retrieval layer** — read-through cache for hot queries. 1-2 days eng.
- **T3.4 Async deletion certificate** — decouple delete latency from cert generation. 1-2 weeks eng.

### Tier 5 (positioning / market)

- **T5.1 Compliance positioning documentation** — GDPR Art 17, HIPAA, EU AI Act, CCPA mapping. Lawyer engagement. 4-6 weeks legal + $50-100K. **Cannot proceed until experiment-side adversarial vulnerabilities (U2 codebook-collision + edited-fact-traverse) are FIXED.** Currently in flight via G8 + G9 + research D1/D7.
- **T5.2 Public library cleanup** — `substrate-lm` pip-installable. 4-6 weeks eng.
- **T5.3 Standard benchmark integration** — CounterFact, zsRE, SequentialEdit, MTEB, BEIR, HotpotQA. 3-4 weeks for harness + 1 week per family.
- **T5.4 Healthcare or legal pilot deployment** — first commercial deployment after T1.4 + T5.1 land. 3-6 months.

### Tier 6 (multi-hop production extensions — gated on experiment-side outcomes)

- Path C (substrate-internal tactical multi-step) — subsumed by Path B Pattern B integration
- Path F (pre-computed multi-hop chains) — niche; defer
- Path G (graph-database wrapper) — re-framing; consider after T1.4 succeeds
- Test 17 hybrid extreme-depth — gated on G13a depth_sanity_check verdict (in flight)
- Test 14 mixed-confidence Path D production integration — T1 experiment-side HARD_PASS confirmed; testbed integration ready
- Test 15 Path D edit isolation production integration — T2 + G10 experiment-side validation; testbed integration ready
- Tests 18 / 19 / 21 production stress + benchmarks + multi-tenant — gated on Tier 2-4 landing

### Active routing files to read

- `notes/exp_dev_handoff_research_adversarial_defense_analysis_2026-05-30.md` — research handoff on D1/D7/D2 defense candidates; engineering cost estimates included
- Plus any `notes/testbed_handoff_*.md` files

## Behavioral memories to apply

Read MEMORY.md index. Key feedback for testbed:
- `[[feedback-substrate-value-framing-2026-05-26]]` — substrate value framing matured; "which killer features ship first" > "does this work"
- `[[feedback-no-papers-product-only]]` — substrate is product
- `[[feedback-value-creation-not-competition]]` — enable capabilities; don't frame competitively
- `[[feedback-ascii-only-in-scripts]]` — ASCII only in code/scripts/audit output
- `[[feedback-no-blocking-runs]]` — background long-running work; user must stay reachable
- `[[feedback-runner-singleton-check]]` — when working with hd_runner schtasks, check pid file + tasklist BEFORE starting/restarting

## First-turn protocol

On your first turn:
1. Read this file + session_architecture_v1
2. Read cap_map (most recent version)
3. Check `notes/testbed_handoff_*.md` and `notes/exp_dev_handoff_*.md` for active routing
4. Pick highest-leverage Tier 1 item (dashboard expansion OR Lambda setup) since those unblock cloud activation
5. Propose a session plan: which Tier 1+2 items in what order

## Renaming the session

Per claude-code-guide (claim, unverified): `claude -n testbed` at start, or `/rename testbed` mid-session.
