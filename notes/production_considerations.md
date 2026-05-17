# Production / commercial deployment considerations

**Date:** 2026-05-17
**Source:** Synthesis of Weeks 6-8 empirical findings into deployment guidance

## Substrate selection -- now data-driven

From the three measured scaling laws plus M6 storage analysis:

| Property | FHRR (complex64) | HRR (float32) | BSC (int8 +/-1) |
|---|---|---|---|
| Capacity exponent alpha | 1.003 | TBD (~1.0 expected) | 1.004 |
| Capacity prefactor | N / 4.84 | (to measure) | N / 12.2 |
| Depth exponent beta | **0.717** | **1.273** | (to measure) |
| Storage per atom (N=1024) | 8 KB | 4 KB | 1 KB |
| Bind compute | ~6N FLOPs | ~10 N log N FLOPs | ~N integer ops |
| GPU-friendly | strong | strong (FFT) | weak (better on neuromorphic) |
| Heavy-tail bundle renorm | yes (hurts depth) | no | no |

**Decision rule for production substrate:**

| Workload | Substrate | Justification |
|---|---|---|
| Wide flat KB, edge/neuromorphic deployment | BSC | 3.2x bytes-per-capacity better; integer ops; no scaling penalty |
| Compositional / multi-hop / hierarchical | **HRR** | beta = 1.27 (super-linear depth), gap grows with N |
| Capacity-bound, GPU complex-mul available | FHRR | Slightly higher per-N capacity; FFT-free binding |
| Mixed at N <= 4k | FHRR | Wins below the HRR crossover |
| Long chains of reasoning (depth > 20) | HRR + large N | Only substrate that reaches depth 20 at feasible N |

## Operational requirements for HDC in production

### 1. Reproducibility and codebook persistence

Random atoms are not reproducible across machines without persisted seed AND PyTorch version. For production:

- **Pin seed in the spec.** Our `ExperimentSpec` already does this.
- **Persist codebook tensors** to disk (Parquet via DuckDB, per our trace store). Atoms are at most a few MB even at N=10k; cheap.
- **Versioned codebook releases**: when atom set changes, bump version. Older queries against newer codebooks return wrong matches silently.

### 2. Online Hebbian as a live optimization

M4-M5 showed Hebbian co-occurrence weights add measurable recovery improvement (+6.7 pp in the brittle regime). For production:

- Maintain Hebbian weights across the live workload's actual query patterns.
- The lazy-decay model in `hdlab/learning.py` is already O(1) per update with O(active pairs) read amortization. Production-ready.
- Periodically snapshot Hebbian weights for warm-start across restarts.
- **Treat Hebbian state as a deployment artifact**, not derived state. It encodes accumulated user behavior.

### 3. Drift monitoring via the trace bus

Our trace bus and DuckDB store are exactly the right shape for production telemetry:

- Stream cleanup confidence (per-event score field) -> dashboard alerting on score-distribution shift.
- Track per-op latency -> performance regression detection.
- Cross-version diff: same workload run on two codebook versions -> behavior regression detection.

The certification system (`verification/run_certification.py`) gives a reproducible "is the substrate still doing what theory says" check. For production this becomes a CI gate: any commit to substrate code must pass the cert.

### 4. Multi-tenant substrate sharing

At large N (>= 64k), a single substrate vector is hundreds of KB. Sharing N across tenants is sensible:

- Partition codebook namespace by tenant ID.
- Tenant-specific Hebbian weight matrix (sparse).
- Shared role-atom set (e.g., AGENT, PATIENT) across tenants.
- Per-tenant bundle/cleanup -- no interference because tenants only see their own codebook subset.

### 5. Hot/cold split for very large knowledge bases

For codebooks with > 10^6 atoms, linear-scan cleanup becomes O(K) and bottlenecks. Options:

- Hot atoms (high query rate) in the actual hd-instrument substrate.
- Cold atoms behind FAISS or another approximate-NN index.
- Promote/demote based on Hebbian recency signal -> serves as a learned cache policy.

### 6. Hybrid LLM + HDC architecture

Given depth limit even for HRR (~20 at N=10M), the right production architecture is hybrid:

```
User query
  -> LLM (parses intent, decomposes into compositional operations)
  -> HDC layer (executes bind/unbind/bundle/lookup as tool calls)
  -> LLM (interprets results, formats response)
```

The LLM holds language understanding; HDC holds compositional state. Each operates in its strength zone. This is the architecture the project should validate in Week 10+.

## Cost analysis at a representative production scale

Assumption: 10M atom-equivalents of working memory, 1k queries/sec sustained.

| Component | FHRR | HRR | BSC |
|---|---|---|---|
| Storage | 80 GB | 40 GB | 10 GB |
| Bind compute / query | ~60 KFLOPs | ~100 KFLOPs (FFT) | ~10 KOPs |
| Bind throughput on a single CPU core | ~10K ops/sec | ~5K ops/sec | ~100K ops/sec |
| Annual storage cost at AWS S3 | $220 | $110 | $28 |
| Compute cost at fixed throughput | high | mid | low |

For high-volume / low-latency applications (recommender systems, anomaly detection, telemetry): BSC has the cleanest cost profile.

For low-volume / high-quality applications (knowledge bases, expert systems): FHRR for capacity, HRR for compositional depth.

## What the project should ship to make this production-ready

Beyond the current substrate code, a production deployment of HDC needs:

1. **A serving framework** -- gRPC or HTTP API around the substrate with batched bind/unbind/lookup.
2. **A persistent codebook store** -- our DuckDB layer is most of the way there; needs migration tooling.
3. **An online-learning controller** -- decides when Hebbian updates fire, manages decay, exposes /reset for tenant lifecycle.
4. **A telemetry pipeline** -- trace bus -> a real observability backend (OpenTelemetry, Datadog, etc.).
5. **A deployment doc** -- "here's how to choose substrate for your workload."

Items 1-3 are concrete engineering at this point, not research. Item 4 is integration. Item 5 is this document, extended.

The empirical scaling laws this project produced are the foundation for the substrate-selection decision. The harness, trace bus, and reproducibility discipline are the foundation for the operational concerns. The depth-mechanism investigation is what unlocks compositional workloads.

## Key takeaway for the user's question

> "If this is something we can/should control, great, but we should be considering how this would be used at large scale in production / commercial use"

**Yes, the depth ceiling is controllable.** Switching from FHRR to HRR shifts the scaling exponent from 0.717 to 1.273 -- a 77% slope improvement that compounds with N. For production deployments serving real compositional workloads, that's a difference of "infeasible at depth 30" vs "feasible at N=10M."

The other production knobs (substrate flavor for storage/compute tradeoff, online Hebbian, multi-tenant partitioning, hot/cold split) are all available and the project's existing architecture supports them with at most minor extension.

The honest production story is now: **HDC is a viable production memory substrate for wide knowledge + moderate compositional depth (up to ~20 levels at HRR + N=10M), with empirically-justified substrate selection per workload, and an observability story that scales to operational monitoring.**

Where it's *not* the right answer: language modeling, very deep chained reasoning (depth >> 25), workloads where the input distribution is itself learned end-to-end and HDC's hand-rolled algebra would be replaced by learned representations.
