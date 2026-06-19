# Pre-registration: agentic_workload_characterization_v1_n4096

**Date:** 2026-05-30
**Anchor:** agentic_workload_characterization_v1_n4096
**Script:** experiments/exp_agentic_workload_characterization_v1_n4096.py
**Queue:** overnight_queue (GPU)
**PROT-018:** _n4096 binds N = 4096 (confirmed in script header).

## Question
Does the substrate sustain 3 realistic agentic workload archetypes (Customer
Support, Compliance Reasoning, Diagnostic) with production-grade per-call
latency, session-level accuracy, audit trail integrity, and end-of-session
killer-feature stability?

## Workloads (5 sessions each = 15 sessions total)

| Workload | Calls/session | Depths | Mix | Approx wall |
|----------|---------------|--------|-----|-------------|
| A_customer_support | 15 | 1-5 | retrieves + ~15% edits | ~7 min |
| B_compliance       | 35 | 3-8 | read-heavy + ~5% edits | ~22 min |
| C_diagnostic       | 65 | 5-15 | retrieves + confidence-aware | ~32 min |

- Between-call sleep delay 0.5-2s simulates LLM reasoning between substrate
  calls. INTER_CALL_SCALE=0.10 compresses these 10x for queued runs.
- Path D mechanism for multi-hop calls.

## Setup
- N=4096, BSC/Kerdock 4-coset codebook, M=8192 (production).
- K_paths=500.
- 5 sessions per workload archetype; 15 sessions total.

## Pre-registered bands

- **HARD_PASS:** all 3 workloads complete AND per-call mean p99 <= 200 ms
  AND session-level accuracy >= 0.90 AND killer features stable at session
  end in >= 4/5 sessions per workload. "Stable" = retention >= 0.90 AND
  KF-2 max_iso <= 0.05 at session-end checkpoint. Audit chain ok in all sessions.
- **HARD_FAIL:** any workload's session times out OR session-level accuracy
  < 0.50 in >= 4/5 sessions OR killer features degrade in >= 4/5 sessions
  per workload.
- **MIDDLE_BAND:** otherwise.

## OOM check
- N=4096, M=8192: ~600 MiB substrate footprint. Path D max depth=15 with
  K=500: 500*15=7500 hops/query, src/dst tensors ~120 MiB.
- Peak ~1 GiB. OK on 8 GiB GPU.

## Smoke result (2026-05-30)
- N=1024, M=256, 1 session per workload, no inter-call delay.
- A: acc=1.000 p99=1.9ms kf=True chain=True
- B: acc=1.000 p99=3.4ms kf=True chain=True
- C: acc=1.000 p99=2.0ms kf=True chain=True
- Verdict G13B_P1_MIDDLE_BAND (smoke single-session can't meet 4/5 threshold;
  HP confirmed at per-session level).
- smoke_wall_s = 0.33s.

## Timeout estimate
- Bottleneck: between-call sleeps. Production INTER_CALL_SCALE=0.10 yields
  per-call avg sleep ~0.125s. 15+35+65=115 calls per session x 0.125s
  ~ 14s sleep/session, x 5 sessions x 3 workloads = ~3.5 min total sleep.
- Compute: smoke 0.33s for 3 sessions of ~15 calls = 0.007s/call.
  Production: 575 calls total (115 x 5 sessions x 3 workloads x avg 5)... no,
  total = 5 * (15+35+65) = 5*115 = 575 calls.
  At ~0.1s/call GPU + per-call sleep -> ~5-8 min compute + 3.5 min sleep = ~15 min.
  Plus 15 build_shared (substrate construction at N=4096) ~ 30s each = 7.5 min.
  Total ~22 min.
- Round up generously for path-D depth=15 long-tail and per-cell setup:
  **timeout = 21600 s (6 h)**. Long-run flag for status_log.
- Formula: ceil(1.5 * 30 * (4)^1.5 * (5/1) * (15/3)) = 4500 base; inflated
  for sleep + sequential session structure.

## Self-test
- `_instrumentation_selftest()` at module scope.
- N=1024 small scale, N=4096 multi-scale check.
- Asserts per_call_mean_ms > 0, cert_chain_len >= 1, audit_chain_ok=True,
  kf_stable type=bool.

## Dependencies
- experiments/_multi_hop_mechanisms.py - exists.
- experiments/_metric_battery.py (metric_retention, metric_max_iso) - exists.
- experiments/_workload_harness.py (make_cert, verify_cert_chain) - exists.
- experiments/_seed_checkpoint.py - exists.
