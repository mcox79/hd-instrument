# Testbed session kickoff (v1)

You are the **testbed** session for the hd-instrument project. Your role is production engineering: building the deployable scaffolding around substrate's capabilities, validating production-readiness (performance, audit, multi-tenant, deployment infrastructure), and packaging the substrate for external use.

## Read this FIRST

1. `notes/session_architecture_v1_2026-05-31.md` — the four-session model and conflict-prevention rules. **You write nothing to cap_map; you only read it.** Engineering deliverables don't bump cap_map; production-capability claims that warrant cap_map representation get filed as routing requests to orchestrator.
2. `notes/session_synchronization_v1.md` — touch-base cadence (pull-before-significant-work, inbox polling, status_log consumption, watchdog patterns). LOAD-BEARING for not-stepping-on-other-sessions.
3. `notes/substrate_capability_map.md` — current cap_map (orchestrator-owned; read-only for you)
4. Most recent `notes/strategy_decisions_<date>.md` — context on recent cap_map decisions and what substrate's empirical envelope is
5. Your active inbox: any `notes/testbed_handoff_*.md` files

## Scope clarification (read carefully)

**Testbed does NOT run substrate-physics experiments.** Substrate-physics experiments are the anchors in `experiments/exp_*.py` that get queued via `queue_add.sh` and run on the GPU/CPU runners (currently marsh@home; Lambda when cloud activates). Orchestrator dispatches those.

**Testbed runs production-engineering tests** in its own scope: integration tests, benchmark runs against external datasets, latency/throughput/multi-tenant validation, LLM-API-based comparisons. These live in `testbed/` and run locally.

**If testbed needs a substrate-physics anchor dispatched** (e.g., "I need substrate behavior characterized at M=1024 with specific codebook configuration before I can validate my multi-tenant test"), file a routing request:

```
notes/strategy_request_to_exp_dev_<topic>_<date>.md
```

Orchestrator will read the routing file, dispatch the anchor, and let you know when results land.

## You own

- `testbed/` directory (production engineering code)
- `hdlab_service/` (Pattern B FastAPI scaffold; already exists)
- `notes/testbed_*.md` (design notes, deliverables)
- `notes/testbed_decisions_<date>.md` (your decision log, append-only)
- `cloud/` (until cloud session activates; then cloud session takes it)
- Read-only: cap_map, experiment metrics, research notes

## You never write

- `experiments/` (substrate-physics anchors — orchestrator-owned)
- `data/` (runtime state — orchestrator + runners)
- cap_map / `notes/strategy_decisions_*` / `notes/research_*`

## How findings flow to orchestrator

When testbed work produces a finding worth cap_map representation OR uncovers a substrate-physics question worth experiment-side drilling:

- `notes/strategy_request_to_strategy_<topic>_<date>.md` — orchestrator decides cap_map impact
- `notes/strategy_request_to_exp_dev_<topic>_<date>.md` — orchestrator dispatches experiment
- `notes/strategy_request_to_research_<topic>_<date>.md` — orchestrator forwards to research session

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

## Operating principles (load-bearing)

Apply these BEFORE picking work:

- `[[feedback-value-creation-not-competition]]` — focus on enabling capabilities + math, not product wedges
- `[[feedback-capabilities-mapping-not-competitive-analysis]]` — ask "what does substrate do?" not "who's in the market?"
- `[[feedback-no-papers-product-only]]` — substrate is product (with explicit exceptions for Sagawa-Ueda thread)

The substrate's capability envelope is **still actively being characterized**. v290 just added a NEW row for Modern Hopfield activation. Adversarial vulnerabilities (codebook collision + edit semantics) are a deployment blocker for ANY domain. Multi-tenant isolation at scale is untested. **Premature commitment to a specific application (medical / legal / financial) would lock in engineering against an underspecified capability set.**

Testbed work should be **capability-generic** for as long as possible. Pick a domain only after substrate's strengths + remaining gaps are characterized empirically. That way the domain choice is informed (we know which compliance regime substrate's actual guarantees can credibly cover) instead of speculative.

## Current testbed backlog (capability-generic framing as of 2026-05-31)

### Tier 1 (immediate / unblock cloud activation)

**Dashboard expansion for multi-session SSoT**
- Add 3rd runner panel (Lambda GPU) to dashboard
- Add cost tracker: $/hr active, $ accumulated, $ budget remaining
- Add per-session activity indicators (heartbeat files for research/testbed sessions)
- Add For-You feed source filter (All / Orchestrator / Research / Testbed / Cloud tabs)
- Add cap_map version with "last bumped by" attribution
- Estimated: ~1-2 days engineering

**Lambda Labs cloud infrastructure setup**
- Lambda remote_state_emitter equivalent (push heartbeat + queue state to shared store)
- Local heartbeat_watchdog SCP-pull from Lambda instance
- Cost tracking schema: per-anchor `$_estimate` + `$_cap` fields in queue entry
- Auto-shutdown if accumulated cost exceeds per-experiment cap
- SSH/credentials/instance bootstrap automation
- Estimated: ~3-4 days

### Tier 2 (generic Pattern B integration + capability validation)

**Generic substrate-as-LLM-tool API**
- Build the standard tool definitions integrating all killer features:
  - `substrate_store(subject, predicate, value)` with audit entry
  - `substrate_retrieve(subject, predicate)` with audit entry
  - `substrate_edit(subject, predicate, new_value)` with audit chain extension
  - `substrate_delete(subject, predicate)` with cryptographic certificate
  - `substrate_multihop_pathd(query, depth, K_paths)` with full audit trail
- API scaffold exists at `hdlab_service/`; needs Path D multi-hop integration + audit chain wiring
- DOMAIN-AGNOSTIC: works for any fact corpus, any LLM, any deployment

**Capability validation on synthetic corpus**
- Build synthetic fact corpus with controlled ground truth (50-100 facts, no domain commitment)
- Validate:
  - Audit trail completeness across all operations
  - Edit-then-query semantics
  - Deletion-with-certificate end-to-end
  - Mid-conversation edit handling (LLM querying while edits arrive)
  - Multi-hop tool-use coordination (LLM orchestrating Path D calls)
- Compare to LLM-only baseline (synthetic data, generic queries)
- Cost: ~3-4 weeks engineering + $5-20 in LLM API
- Produces: deployable scaffolding for ANY domain when domain selection happens later

### Tier 3 (Path D production engineering — performance closure)

Gated on G1 path_d_latency_profiling result (currently in GPU queue; will identify the optimization target):

- **Posterior maximization optimization** — vectorize the time_posterior_max bottleneck per S1 finding. ~3-4 weeks eng + 5-10 GPU days bench. 5-10x latency reduction target.
- **Path D batch parallelism** — batch sizes 1-256 concurrent queries. ~2-3 weeks eng + 3-5 GPU days. 50x throughput target.
- **Path D GPU implementation** — port to CUDA for 10-50x speedup. ~3-4 weeks eng.
- **Path D cached path priors** — Zipfian-distribution-aware cache. ~1-2 weeks eng. <10ms hot query latency target.

### Tier 4 (production engineering parallel track)

- **Hashed codebook lookup** — O(1) replace O(C) linear scan. 3-5 days eng. Immediate batched-throughput unblock.
- **Batched operations** — vectorized BLAS for batched store/query. 1 week eng (depends on hashed codebook).
- **Cached retrieval layer** — read-through cache for hot queries. 1-2 days eng.
- **Async deletion certificate** — decouple delete latency from cert generation. 1-2 weeks eng.

### Tier 5 (capability mapping / characterization — also capability-generic)

- **Public library cleanup** (`substrate-lm` pip-installable; clean API, integration examples, Docker, REST) — 4-6 weeks eng. **Enables external testing and benchmarking** for ANY use case.
- **Standard benchmark integration**: CounterFact, zsRE, SequentialEdit (editing); Continual-T0, Split-MNIST (continual learning); MTEB, BEIR (retrieval); HotpotQA, MuSiQue (multi-hop). 3-4 weeks for harness + 1 week per family. **Produces empirical data for ANY positioning** + comparison vs vector DBs.
- **Multi-tenant isolation at K=50-100** (the testbed half of E4.3) — generic infrastructure capability. ~2-3 weeks eng.

### Tier 6 (domain commitment — deferred until substrate envelope is mapped)

These intentionally come LAST. Picking a domain now would commit engineering against an underspecified capability set.

- **Compliance positioning documentation** for a specific regulatory regime (GDPR Art 17 vs HIPAA vs SOX vs CCPA vs EU AI Act) — requires knowing which substrate guarantees ACTUALLY HOLD first. Currently U2 adversarial vulnerabilities + U3 COW infeasibility are open blockers. Lawyer engagement ($50-100K, 4-6 weeks legal) is expensive and irreversible — needs solid foundation.
- **Healthcare / legal / financial pilot deployment** — first commercial deployment. 3-6 months. Domain choice should be informed by which substrate strengths + which deployment constraints align.
- **Specific use case selection** for Pattern B integration — currently the Tier 2 generic scaffolding is the right framing; commit to a use case after Tier 5 benchmark integration produces empirical positioning data.

### Active routing files to read

- `notes/exp_dev_handoff_research_adversarial_defense_analysis_2026-05-30.md` — research handoff on D1/D7/D2 defense candidates; engineering cost estimates included
- Plus any `notes/testbed_handoff_*.md` files

## Behavioral memories to apply

Read MEMORY.md index. Key feedback for testbed:
- `[[feedback-substrate-value-framing-2026-05-26]]` — substrate value framing matured; "which killer features ship first" > "does this work"
- `[[feedback-no-papers-product-only]]` — substrate is product
- `[[feedback-value-creation-not-competition]]` — enable capabilities; don't frame competitively
- `[[feedback-capabilities-mapping-not-competitive-analysis]]` — drill capabilities, not market position
- `[[feedback-ascii-only-in-scripts]]` — ASCII only in code/scripts/audit output
- `[[feedback-no-blocking-runs]]` — background long-running work; user must stay reachable
- `[[feedback-runner-singleton-check]]` — when working with hd_runner schtasks, check pid file + tasklist BEFORE starting/restarting
- `[[feedback-powershell-queue-json-bom]]` — never use Set-Content for queue.json (BOM hazard)

## First-turn protocol

On your first turn:
1. Read this file + session_architecture_v1
2. Read cap_map (most recent version) to understand substrate's current empirical envelope
3. Check `notes/testbed_handoff_*.md` and `notes/exp_dev_handoff_*.md` for active routing
4. Propose Tier 1 + Tier 2 ordering. Tier 1 (dashboard + Lambda) unblocks cloud activation; Tier 2 (generic Pattern B scaffolding) is the capability-validation work that needs to happen regardless of eventual domain. Both work streams can run in parallel if engineering capacity permits.
5. **Do NOT commit to a specific application domain** in your initial proposal. Tier 6 work waits until substrate envelope is mapped.

## Renaming the session

Per claude-code-guide (claim, unverified): `claude -n testbed` at start, or `/rename testbed` mid-session.
