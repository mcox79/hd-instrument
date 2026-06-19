# Testbed Track Queue v3 — Post-N=16384 priorities (filed 2026-05-30)

Routed from user message after N=16384 envelope result landed (max_M_at_95_recall =
N/2, 2x linear extrapolation). Four new testbed items prioritized on top of the
v2 Path D queue. Q3 composition_latency (READY from v1) is currently RUNNING on
remote (~3-4h bench).

## v3 priority order

| Pri | Item | Track | Status | Cost | Blocked on |
|-----|------|-------|--------|------|------------|
| TB1 | Updated cost model with N=16384 data | doc/analysis | **READY** | 4-6 hours | none |
| TB2 | Pattern B LLM integration with large-N awareness | product val | BLOCKED | 3-4wk + $ | Path D primitives + P1 verdict |
| TB3 | Adversarial defense engineering | security/compliance | BLOCKED | 2-3wk | GPU 5 result identifies viable defense mechanisms |
| TB4 | Multi-tenant validation at larger scale | enterprise val | **READY** | 2wk + GPU | none (was Q10/T21, now reframed at N=16384) |

## TB1. Updated cost model with N=16384 data [READY, NEXT]

**Purpose:** incorporate N=16384 findings into customer-facing cost model. Current
estimates assume linear N/4 envelope; actual N=16384 result shows N/2 at 95%
recall (2x the linear prediction). Per-store latency is also 56x faster than the
config estimate (530 us vs 30 ms).

**Why high priority:** cost model is what customers use for capacity planning.
Wrong estimates lead to wrong deployment decisions and erodes credibility.

**Design:**
- Document operating envelope per N (max_M_at_95_recall, max_M_at_50_near_uniform,
  TCFT operating range) from existing empirical data (N=2048, 4096, 8192, 16384)
- Build cost-per-fact model that includes large-N options
- Generate 3 deployment scenarios:
  - **Small-scale:** M=1K-5K at N=4096-8192 (Pattern B sweet spot for 50-500 facts
    in active context; small Pattern B integrations)
  - **Mid-scale:** M=5K-15K at N=8192-16384 (regulated-industry document corpus;
    medical drug interaction database; legal precedent corpus per practice area)
  - **Large-scale:** M=15K-65K at N=16384-32768 (predicted, requires N=32768
    bench to validate envelope continues super-linear)
- TCFT operating envelope per scenario (which deployments support deletion
  certificates at HARD_PASS thresholds, which only at WARN thresholds)
- Hardware requirements per scenario (RAM, disk, threads)

**Measurements:**
- Validated operating envelope per N (filled from empirical data)
- Cost-per-fact at various deployment scales (RAM cost + disk cost + cloud
  compute cost normalized per stored fact)
- Hardware requirements for each scenario

**Success criteria:**
- Production-ready cost model artifact in testbed/COST_MODEL.md or similar
- Customer-facing deployment guidance (which N for which use case)
- Clear documentation: what is validated vs predicted vs extrapolated

**Output artifact:** `testbed/COST_MODEL.md` (new file)

**Cost:** 4-6 hours documentation + analysis work.

**Strategic value:** HIGH. Required for customer engagement and pilot deployment
planning.

## TB2. Pattern B LLM integration with large-N awareness [BLOCKED]

**Purpose:** load-bearing Pattern B integration sized for the empirical envelope
(not the previously-extrapolated linear pattern).

**Why high priority:** Pattern B is THE load-bearing product test. N=16384 finding
means Pattern B can support larger corpora than previously framed: up to 8K
facts in single substrate at N=16384, predicted up to 16-32K at N=32768.

**Design (incorporating N=16384 findings):**
- Pick use case (medical literature Q&A, legal precedents, or financial
  compliance — user to decide)
- Sized for empirical capacity envelope:
  - Standard: 200-500 fact corpora at N=4096
  - Large: 2-8K facts at N=16384 (NEW; was thought to require sharding)
- Substrate tools as previously specified (Path D continuous-output multi-hop)
- Comparison conditions: (a) LLM-only, (b) LLM+RAG, (c) LLM+substrate single-hop,
  (d) LLM+substrate native multi-hop
- Critically: **document operating point and M/N ratio per deployment**

**Measurements:**
- Standard Pattern B metrics (tokens, accuracy, latency, audit completeness)
- Validation of capacity envelope claims in actual LLM integration
- Hardware-deployment tradeoffs (single-N vs sharded)

**Success criteria:**
- Validates Pattern B at empirical operating envelope
- Validates substrate's product positioning for the chosen use case

**Cost:** 3-4 weeks engineering, $20-50 API costs.

**Strategic value:** HIGH. Load-bearing product test.

**Blocked on:** Path D primitives in testbed (need experiment-session port) +
P1 verdict for M-range guidance.

## TB3. Adversarial defense engineering [BLOCKED]

**Purpose:** build production defenses for U2 adversarial vulnerabilities (codebook
collision, edit semantics).

**Why high priority:** regulated industry deployment cannot proceed without these
defenses. Defense engineering must start before pilot deployment.

**Design:**
- Implement defense mechanisms identified by **GPU 5** (experiment-session test
  that identifies viable approaches; gate on its result)
- Test each defense:
  - Query perturbation/cleanup
  - Codebook collision detection
  - Post-edit verification probes
  - Edit-log based query rewriting
- Integrate into Pattern B integration (after TB2 ships)

**Measurements:**
- Defense rate per adversarial pattern
- False positive rate
- Latency overhead
- Killer feature compatibility

**Success criteria:**
- Defense rate >= 80% on identified attack patterns
- False positive rate <= 5%
- Latency overhead <= 2x baseline

**Cost:** 2-3 weeks engineering.

**Strategic value:** HIGH. Required for compliance positioning credibility.

**Blocked on:** GPU 5 result identifies viable defense mechanisms.

## TB4. Multi-tenant validation at larger scale [READY]

**Purpose:** with larger-N capacity validated, multi-tenant deployments can hold
more per-tenant. Validate at scale.

**Why high priority:** enterprise multi-tenant deployments benefit from larger
per-tenant capacity. N=16384 finding means each tenant can hold 4-8K facts (vs
the linear N/4 = 4096 prediction).

**Design:**
- K=50 tenants at N=8192 (mid-scale, dense each)
- K=20 tenants at N=16384 (larger each)
- Compare resource utilization vs K=10 baseline (sharded_substrate already
  validated K=10 at smaller M)
- Sustained load across all tenants

**Measurements:**
- Cross-tenant isolation under load
- Per-tenant performance with N=16384 substrates
- Total memory footprint (K=20 at N=16384 ~= 20 * 5.5 GB = 110 GB peak; needs
  hardware-feasibility check before launch)
- Audit chain integrity

**Success criteria:**
- Multi-tenant deployment with larger per-tenant capacity works
- Resource scaling is acceptable

**Cost:** 2 weeks engineering, GPU costs for sustained workload (or extended
multi-day CPU run on remote; if 110 GB peak then needs hardware upgrade).

**Strategic value:** MEDIUM-HIGH. Enterprise deployment validation.

**Note:** supersedes Q10/T21 from v1/v2 queues; reframed at larger N.

## Reconciliation with v1 + v2 queues

- v1 Q3 composition_latency: **RUNNING NOW** on remote (~3-4h bench).
- v1 Q4 cold/warm timing: still READY; can launch parallel to Q3.
- v1 Q11 failure recovery: still READY.
- v1 Q6 vector DB comparison: still relevant (now informed by TB2 use case
  selection).
- v2 Tier 3 (T10-T13 Path D production engineering): all still BLOCKED on S2
  verdict + Path D primitives in testbed.
- v2 T17 hybrid extreme-depth: subsumed by TB2 (with large-N framing).
- v2 T19 vector DB comparison: now informed by N=16384 finding.
- v2 T21 multi-tenant: superseded by TB4.

## Recommended cadence post-N=16384

1. **NOW (Q3 running):** Start TB1 cost model (4-6h doc work, no compute
   contention with Q3).
2. **After TB1 ships:** Start Q4 cold/warm timing (small scope, can run while
   Q3 is still going if Q3 long-running).
3. **After Q3 + Q4 done:** Start TB4 multi-tenant at K=50 N=8192 (the
   K=20 N=16384 needs hardware-feasibility check first).
4. **In parallel:** monitor experiment-session for S2 verdict (unblocks Tier 3
   Path D primitives), P1 verdict (unblocks TB2 / Pattern B), GPU 5 (unblocks
   TB3 / adversarial defense).
5. **When unblocked:** sequence TB2 -> Path D primitive port -> Tier 3 -> TB3.

## End of v3 queue. Filed 2026-05-30.
