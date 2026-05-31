# Testbed Track Queue (filed 2026-05-30)

**SUPERSEDED for multi-hop items by `TESTBED_TRACK_QUEUE_v2_PATH_D_2026-05-30.md`.**
v288 cap_map identified Path D (Bayesian path-probability propagation) as the
production-scale robust mechanism, replacing the Path B emphasis assumed here.
This file remains authoritative for the parallel-track READY items (Q3 composition
latency, Q4 cold/warm timing, Q11 failure recovery) which are not Path-D-dependent.
See v2 file for the reconciliation table.

User-delivered comprehensive testbed roadmap. 14 items across 6 tracks. Each item is
a separate substantial work unit. This queue captures status, dependencies, and
ready-to-start partition.

## Quick status table

| #   | Item                                          | Track | Status     | Blocked on                    | Cost      |
|-----|-----------------------------------------------|-------|------------|-------------------------------|-----------|
| Q1  | EC2 Pattern B LLM integration                 | C     | BLOCKED    | P1 (M-range), MH primitives   | 3-4wk + $ |
| Q2  | E6.1 Hashed codebook lookup                   | 6     | **SHIPPED**| -                             | done      |
| Q3  | E2.3 Operation composition latency            | 2     | **READY**  | -                             | 2wk + run |
| Q4  | E2.4 Cold start vs warm timing                | 2     | **READY**  | -                             | 1wk       |
| Q5  | E5.1 Standard multi-hop benchmark suite       | 5     | BLOCKED    | MH primitives in testbed      | 2-3wk + $ |
| Q6  | E5.2 Substrate vs vector DB comparison        | 5     | **READY**  | -                             | 3-4wk + $ |
| Q7  | E5.3 Substrate vs LLM-only multi-hop          | 5     | BLOCKED    | MH primitives                 | 2-3wk + $ |
| Q8  | E3.1 Multi-hop LLM-guided orchestration       | 3     | BLOCKED    | MH primitives, E1.3 latency   | 4-6wk + $ |
| Q9  | E4.1 Sustained multi-hop workload (24-72h)    | 4     | BLOCKED    | MH primitives                 | 1wk + run |
| Q10 | E4.3 Multi-tenant substrate isolation         | 4     | **READY**  | -                             | 2-3wk     |
| Q11 | E4.4 Failure mode recovery testing            | 4     | **READY**  | -                             | 2-3wk     |
| Q12 | E6.3 Multi-hop caching                        | 6     | BLOCKED    | MH primitives                 | 1-2wk     |
| Q13 | E3.3 Multi-hop hybrid (substrate + LLM)       | 3     | BLOCKED    | E3.1 complete                 | 3-4wk + $ |
| Q14 | E3.4 (testbed phase) Mixed-confidence MH      | 3     | BLOCKED    | E3.4 experimentation, MH      | 2-3wk     |

**Legend:**
- SHIPPED = code in testbed/ and production-validated
- READY = no upstream verdict or primitive dependency; can start now
- BLOCKED = waits on experiment-side verdict OR upstream testbed primitive
- MH primitives = multi-hop mechanism implementations (Path B/D/E) — must land
  in testbed/ code before any LLM-integration item can run

## Ready partition (can start while N=16384 bench finishes + verdict-wait)

Six items are unblocked. Suggested execution order:

1. **Q3 E2.3 Operation composition latency** — extends existing
   `mixed_crud_workload` scenario to 100K ops at 5 mix ratios. Highest-value
   ready item because the prior 5K-op mixed workload showed unexplained 12%
   drift; this characterizes drift over production-scale duration.
2. **Q4 E2.4 Cold start vs warm timing** — small scope; quick win for
   public-facing deployment guidance.
3. **Q6 E5.2 Substrate vs vector DB comparison** — leverage existing baselines
   (FAISS, dict, sqlite_vec, chroma). Add Pinecone/Weaviate if accessible.
   Sweeps already partially present in `realistic_workloads.yaml` + crossover
   sweep configs.
4. **Q10 E4.3 Multi-tenant isolation** — extend existing
   `sharded_substrate.py` from K=10 to K=50 with concurrent operations.
5. **Q11 E4.4 Failure mode recovery** — checkpoint/restore scaffolding +
   crash-injection harness; tests audit chain integrity after recovery.

Q2 (E6.1) is already shipped — see `NEXT_SESSION_STATE.md` line 26 (T2 hashed
codebook 22.9x lift, production-validated at 26x).

## Blocked partition (waits on experiment-side or upstream)

Eight items require either (a) experiment-side verdicts that resolve M-range /
mechanism behavior, or (b) multi-hop mechanism primitives (Path B continuous-
output / Path D Bayesian / Path E spectral) to land in `testbed/` code first.

**Critical path to unblock LLM-integration items:**

1. Wait for experiment-side P1 verdict (24-48h horizon per handoff) — settles
   Path B durability at production M.
2. Once P1 lands, port Path B / D / E mechanism implementations from
   experimentation codebase into `testbed/` as `multihop_continuous.py`,
   `multihop_bayesian.py`, `multihop_spectral.py`. Estimate: 1-2 weeks.
3. With MH primitives in testbed, Q5 / Q7 / Q9 / Q12 unblock immediately;
   Q1 / Q8 unblock pending LLM integration scaffold.

## Per-item detailed sketches

### Q1. EC2 — Pattern B LLM integration (load-bearing product test)

**Status:** BLOCKED on P1 + MH primitives.

**Design:** Build substrate-as-tool integration with LLM (Claude Opus or
similar). Substrate exposes `substrate_retrieve_multihop_continuous` tool to
LLM. Test on regulated-industry document Q&A (medical drug-interaction chains,
legal precedent citations, financial compliance rule chains).

**Conditions:** (a) LLM-only, (b) LLM+RAG (FAISS), (c) LLM + substrate
single-hop + LLM orchestrates, (d) LLM + substrate native multi-hop.

**Measurements:** Tokens (c) vs (d) [expect 50-70% reduction], accuracy
(a)-(d), audit trail completeness, end-to-end + per-component latency.

**Success:** (d) >= (c) accuracy at substantially lower tokens.

**Cost:** 3-4 weeks engineering, $5-20 LLM API.

**Dependency unblock chain:** P1 verdict -> MH primitives in testbed -> LLM
scaffold -> document corpora -> run.

### Q2. E6.1 — Hashed codebook lookup [SHIPPED]

**Status:** Done. See `testbed/substrate_memory.py` persistent `_used_*_rows`
sets. Production-validated 26x lift on write_heavy (170 -> 4419 ops/s) and 2.9x
on mixed_crud. Bit-identical W parity preserved.

**Remaining work:** None for codebook lookup itself. The 5-20x throughput
promise was hit. Multi-hop benefits from this fix will compound once MH
primitives land (codebook lookups at each hop).

### Q3. E2.3 — Operation composition latency [READY]

**Status:** READY. Suggested first ready item.

**Design:** Extend `testbed/scenarios/mixed_crud_workload.py` to 100K ops at 5
mix ratios:
- 70/20/10 (retrieve-heavy)
- 40/30/20/10 (mixed CRUD with delete)
- 50/50 (read/write balanced)
- 90/10 (read-heavy)
- 20/60/20 (edit-heavy)

**Measurements:** Latency drift over 100K ops (target <5% drift), per-op
latency isolated vs mixed, memory growth, audit chain integrity at scale.

**Success:** Substrate maintains performance characteristics over 100K+
operations. Drift bounded and explained.

**Cost:** 2 weeks engineering, multi-day sustained runs.

**Why critical:** Prior 5K-op mixed_crud showed 12% drift not root-caused.
This is the test that either explains the drift or confirms a deployment-blocking
degradation.

**Scaffold path:**
- New config: `testbed/configs/composition_latency.yaml` with 5 mix ratios
- Extend `mixed_crud_workload.py` to support configurable mix ratios + 100K ops
- New report section: drift-over-time line chart per ratio

### Q4. E2.4 — Cold start vs warm timing [READY]

**Status:** READY.

**Design:** Measure operations at cold start (just-loaded, first 10 ops),
warming (ops 11-100), warm steady-state (100-1000), long-running (1000+).

**Measurements:** Cold-start latency multiplier vs warm, time to steady-state,
ops affected by warmup (look for codebook lazy-init, caching artifacts).

**Success:** Cold-start behavior documented for deployment guidance.

**Cost:** 1 week.

**Scaffold path:**
- New scenario: `testbed/scenarios/cold_warm_timing.py` — loads substrate
  from disk, runs 1000 retrieves with phase tags (cold/warming/warm/long), emits
  per-phase latency distributions.
- New config: `testbed/configs/cold_warm.yaml`.

### Q5. E5.1 — Standard multi-hop benchmark suite [BLOCKED on MH primitives]

**Design:** Run substrate native multi-hop against published benchmarks:
HotpotQA, MuSiQue, 2WikiMultiHopQA, ComplexWebQuestions.

**Comparison systems:** Substrate (Path B/D/E selected by mechanism), LLM+RAG
(FAISS+sentence-transformers), LLM+knowledge graph (Neo4j), LLM-only with CoT,
substrate via tool-use single-hop with LLM orchestration.

**Cost:** 2-3 weeks harness + 1 week per benchmark family + $50-100 API.

**Why important:** Academic-grade competitive comparison. Required for
industry credibility.

### Q6. E5.2 — Substrate vs vector DB comparison [READY]

**Status:** READY (mostly). Existing baselines cover FAISS / dict / sqlite_vec /
chroma. Adding Pinecone / Weaviate requires accounts + bridge code.

**Design:** Identical workloads across substrate + 3 vector DBs:
- Single-fact retrieval
- Edit-then-query
- Delete-then-query (substrate audit cert; vector DBs lack equivalent)
- Multi-hop via tool-use RAG-style
- Audit chain operations (substrate only; document absence in vector DBs)
- Multi-tenant deployment (50 tenants)

**Measurements:** Throughput, latency, cost per op + per month at scale,
killer feature presence/absence, deployment characteristics.

**Success:** Comprehensive competitive data. Clear customer guidance.

**Cost:** 3-4 weeks + API costs for Pinecone/Weaviate.

**Scaffold path:**
- Extend `testbed/baselines/` with `pinecone_adapter.py`, `weaviate_adapter.py`
- New config: `testbed/configs/vector_db_comparison.yaml`
- Reuse existing scenarios; add comparison-specific report

### Q7. E5.3 — Substrate vs LLM-only multi-hop [BLOCKED on MH primitives]

**Design:** Multi-hop queries through substrate native + LLM-only long-context
+ LLM CoT + LLM step-by-step prompting.

**Measurements:** Accuracy, latency, tokens, cost per query, audit/explainability.

**Success:** Clear positioning data. Identifies substrate's distinctive
advantages beyond LLM-only.

**Cost:** 2-3 weeks + API.

### Q8. E3.1 — Multi-hop LLM-guided orchestration [BLOCKED on MH primitives + E1.3 latency map]

**Design:** Four substrate tools exposed to LLM:
- `substrate_multihop_continuous` (Path B)
- `substrate_multihop_bayesian` (Path D)
- `substrate_multihop_spectral` (Path E)
- `substrate_multihop_compose` (B+D+E, gated on Q2/R2)

LLM tool descriptions include latency-accuracy characteristics from E1.3.
LLM decides per-query which mechanism to invoke.

**Test domain:** Regulated-industry document Q&A.

**Success:** Substrate native MH matches or exceeds LLM-orchestrated MH
accuracy at lower latency/tokens. LLM picks appropriate mechanism per query.

**Cost:** 4-6 weeks + $20-50 API.

**Strategic value:** HIGH. Substrate's defining capability for agentic apps.

### Q9. E4.1 — Sustained multi-hop workload (24-72h) [BLOCKED on MH primitives]

**Design:** 1000 multi-hop queries/hr for 24-72h. Mixed paths + depths,
continuous edit/delete interspersed, continuous audit verification.

**Measurements:** Throughput stability, memory growth, audit chain integrity at
scale, performance drift, state corruption.

**Success:** 24+ hour sustained operation without degradation. Throughput
within 10% of initial. Audit 100%.

**Cost:** 1 week engineering + multi-day run.

### Q10. E4.3 — Multi-tenant substrate isolation under load [READY]

**Status:** READY. Existing `sharded_substrate.py` validated at K=10 with
shared codebook. Extend to K=50 with concurrent operations.

**Design:** K=50 simulated tenants, each independent fact corpus, shared
codebook. Concurrent operations across all tenants. Test for cross-tenant
leakage, per-tenant performance independence, audit per tenant.

**Measurements:** Cross-tenant isolation (must be 100%), per-tenant
performance (independence from other tenants' load), audit integrity per
tenant, killer features under multi-tenant load.

**Success:** 100% isolation under sustained load. Per-tenant performance
independent.

**Cost:** 2-3 weeks engineering + multi-day run.

**Scaffold path:**
- Extend `sharded_substrate.py` to support concurrent operations across shards
- New scenario: `testbed/scenarios/multi_tenant_isolation.py`
- Concurrency harness: thread-pool with per-tenant operation streams
- New config: `testbed/configs/multi_tenant_k50.yaml`

### Q11. E4.4 — Failure mode recovery testing [READY]

**Status:** READY.

**Design:** Simulate failures during operations:
- Substrate process crash mid-multi-hop (after hop 3 of 5)
- Crash during sequential edit storm (after edit 500 of 1000)
- Crash during delete (after audit cert generation, before W update)
- Crash during audit chain verification
- Hardware-level interruption (simulated disk failure during checkpoint)

**Measurements:** Recovery time, data loss for committed ops (target zero),
audit chain integrity post-recovery, killer feature preservation.

**Success:** Clean recovery from all tested modes. Zero loss on committed ops.

**Cost:** 2-3 weeks engineering + 1 week testing.

**Scaffold path:**
- New harness: `testbed/failure_injection.py` — wraps substrate ops with
  configurable crash points
- New scenario: `testbed/scenarios/failure_recovery.py`
- Checkpoint protocol (save/load already exists via `MemoryBackend.save/load`)

### Q12. E6.3 — Multi-hop caching [BLOCKED on MH primitives]

**Design:** Cache (query, depth, mechanism) -> result with audit trail. Audit
extends to cache hits. Test on Zipfian-skewed multi-hop workloads.

**Measurements:** Hit rate at various skew, hot MH latency (cached), audit
across cache hits, cache invalidation correctness when underlying facts change.

**Success:** Hot MH queries <10ms via cache. Audit chain remains valid.

**Cost:** 1-2 weeks.

**Note:** Single-hop cache already shipped via `cached_substrate.py` (T4,
86.32% hit rate at production). Multi-hop cache is direct extension once MH
primitives exist.

### Q13. E3.3 — Multi-hop hybrid (substrate + LLM at decision points) [BLOCKED on E3.1]

**Design:** Substrate executes MH until ambiguity threshold (multiple
high-confidence paths or low single-path confidence). At ambiguity, return
top-K candidates to LLM. LLM picks most semantically reasonable continuation.
Substrate resumes. Continue until depth complete or LLM-intervention budget hit.

**Test depths:** 10, 15, 20 (where pure substrate likely fails per R1).

**Measurements:** Effective depth, LLM intervention frequency, tokens vs
depth, accuracy vs LLM-only at same depth, latency vs LLM-only.

**Success:** Depth 15+ with 50%+ fewer tokens than LLM-only at maintained
accuracy.

**Cost:** 3-4 weeks engineering after E3.1 + API.

### Q14. E3.4 (testbed phase) — Mixed-confidence multi-hop integration [BLOCKED on E3.4 experimentation]

**Design:** Integrate confidence-aware MH (from experimentation phase) into
Pattern B. Test on regulated-industry queries with varying source quality.

**Measurements:** LLM response quality with calibrated confidence, user-facing
confidence accuracy, compliance reporting includes confidence calibration.

**Success:** Calibrated confidence matches accuracy (80% confidence -> 80%
correct). Production-viable confidence reporting.

**Cost:** 2-3 weeks integration.

## Recommended next action

While N=16384 envelope bench finishes (~30-60 min more wall) and the
experiment-side verdict-wait holds, **start Q3 (E2.3 operation composition
latency)** since:

1. Highest strategic value among ready items — addresses the unresolved 12%
   drift observation from prior mixed_crud.
2. Reuses existing infrastructure (`mixed_crud_workload.py` extended to 100K
   ops + 5 mix ratios).
3. No upstream dependencies.
4. Multi-day sustained run can launch tonight, results available in 24-72h.
5. Outcome feeds directly into Q1 (Pattern B integration) production
   readiness — if substrate drifts at sustained scale, Pattern B has a
   deployment blocker; if it's stable, Pattern B is greenlit on stability
   grounds.

After Q3 launches and is running: Q4 (cold/warm timing) is the smallest ready
item; can complete in days.

## Cross-references

- Current testbed state: `testbed/NEXT_SESSION_STATE.md`
- Experiment-side handoff: `testbed/EXPERIMENT_SIDE_HANDOFF_2026-05-30.md`
- Capability inventory: `testbed/CAPABILITY_MAP.md`
- Codebase: `testbed/api.py` (interface), `testbed/substrate_memory.py`
  (reference), `testbed/variants/`, `testbed/scenarios/`, `testbed/configs/`

## End of queue file. Filed 2026-05-30.
