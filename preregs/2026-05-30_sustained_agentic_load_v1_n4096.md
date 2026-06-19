# Pre-registration: sustained_agentic_load_v1_n4096

**Date:** 2026-05-30
**Anchor:** sustained_agentic_load_v1_n4096
**Script:** experiments/exp_sustained_agentic_load_v1_n4096.py
**Queue:** overnight_queue (GPU)
**PROT-018:** _n4096 binds N = 4096 (confirmed in script header).

## Question
Can the substrate sustain 10 concurrent agentic sessions of mixed type
(3 Customer Support + 4 Compliance + 3 Diagnostic) for 2.5 h continuous
runtime without throughput collapse, audit-chain corruption, or memory leak?

## Setup
- N=4096, BSC/Kerdock 4-coset codebook, M=8192 (production).
- K_paths=500. Path D for multi-hop calls.
- Single-process round-robin "agent tick" loop interleaves the 10 sessions.
  (Single-process model avoids torch+CUDA thread/race risk while still
  giving realistic temporal interleaving.)
- Edits/deletes interspersed at 50 ops/hour total (50% legitimate edit /
  50% GDPR-style deletion).
- 30-minute checkpoint: audit chain verified, throughput logged, KF at end.

## Concurrency model justification
Single-process round-robin gives equivalent observable interleaving to true
threading from the standpoint of agentic-pattern stress (sustained ops mix,
edits during query stream, audit chain growth, memory pressure) without
exposing PyTorch CUDA thread-unsafety. If we observe HP at this concurrency
proxy, the production multi-process deployment is downstream engineering work,
not a substrate question.

## Pre-registered bands

- **HARD_PASS:** all 10 sessions complete (or sustain 2.5 h without crash)
  AND |throughput_drop_fraction| <= 0.20 (within 20% of initial 60s window)
  AND audit chain 100% integrity at all 30-min checkpoints AND at end AND
  no memory growth > 2x initial peak.
- **HARD_FAIL:** any session crashes (OOM or unhandled exception) OR audit
  chain corrupts at any checkpoint OR throughput drops > 50%.
- **MIDDLE_BAND:** otherwise.

## OOM check
- N=4096, M=8192 shared substrate: ~600 MiB. 10 sessions share the same W
  (single-process). Per-session state (latencies list) tiny.
- Peak ~1 GiB. OK on 8 GiB GPU.

## Smoke result (2026-05-30)
- N=1024, M=256, 3 sessions, target_wall=60s.
- 26322 ops in 60s, audit chain ok, mem ratio 1.00, no drop.
- Verdict: G13B_P2_HARD_PASS (smoke).
- smoke_wall_s = 60.09s.

## Timeout estimate
- Production target_wall = 9000s (2.5h). Buffer 1h. Setup + initial substrate
  build at N=4096, M=8192 ~ 1 min. Checkpoint overhead 30 min cumulative.
- **timeout = 14400 s (4 h)**.
- Formula: smoke wall = 60.09s, scaling for FULL is mostly wall-time-dominated
  (target_wall=9000s is the target). ceil(9000 * 1.5) = 13500s, round up.

## Self-test
- `_instrumentation_selftest()` at module scope.
- Mini sustained run at N=1024 with 3 sessions for 10s.
- Asserts total_ops > 0, audit_chain_ok=True, cert_chain_len >= 1.

## Dependencies
- experiments/_multi_hop_mechanisms.py - exists.
- experiments/_metric_battery.py - exists.
- experiments/_workload_harness.py - exists.
- experiments/_seed_checkpoint.py - exists.
