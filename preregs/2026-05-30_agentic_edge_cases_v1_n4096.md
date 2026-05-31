# Pre-registration: agentic_edge_cases_v1_n4096

**Date:** 2026-05-30
**Anchor:** agentic_edge_cases_v1_n4096
**Script:** experiments/exp_agentic_edge_cases_v1_n4096.py
**Queue:** overnight_queue (GPU)
**PROT-018:** _n4096 binds N = 4096 (confirmed in script header).

## Question
Does the substrate handle 3 agentic edge scenarios that stress aspects
NOT covered by G13b_p1 (steady-state characterization) or G13b_p2 (sustained
mixed-workload throughput):

- **Edge A** Long-running session with state evolution: 1.5 h single session
  with edits/deletes during the session; multi-hop queries reference
  evolving state.
- **Edge B** Concurrent agent contention: 5 sessions interleaved, 2 of them
  issuing concurrent edits to a designated subset; remaining 3 query a
  "protected" fact set. Isolation = how much the protected set's argmax
  accuracy degrades from non-protected edits.
- **Edge C** Agent recovery from interruption: session executes N1 queries,
  serializes state, drops in-memory references (simulated kill), reloads
  state, replays the first n_post queries and checks consistency.

## Setup
- N=4096, BSC/Kerdock 4-coset codebook, M=8192 (production).
- K_paths=500.
- Edge A: target_wall=5400s (1.5 h), edits_per_hour=60.
- Edge B: 5 sessions, 2 edit agents, 600 ticks at depth=4.
- Edge C: 50 pre-records, 30 post-records, depth=4.

## Pre-registered bands

- **HARD_PASS:** all 3 scenarios complete AND meet their per-scenario
  criteria:
  - Edge A: per-call accuracy >= 0.85 throughout 1.5 h (min over checkpoints)
    AND final audit chain ok.
  - Edge B: max_iso of protected set <= 0.05 (isolation_score >= 0.95)
    AND audit chain valid.
  - Edge C: post-resume consistency exactly 100% (every replayed query
    matches the pre-interruption correctness) AND audit chain valid through resume.
- **HARD_FAIL:** any scenario fails its specific criterion.
- **MIDDLE_BAND:** otherwise (e.g., 2/3 scenarios pass, 1 borderline).

## OOM check
- N=4096, M=8192: ~600 MiB. Edge B with shared substrate ~ same.
- Edge C serializes W to CPU then reloads -> peak 1.2 GiB. OK on 8 GiB GPU.

## Smoke result (2026-05-30)
- N=1024, M=256, accelerated parameters.
- Edge A: min_acc=1.000, chain ok.
- Edge B: max_iso=0.000, chain ok.
- Edge C: consistency=1.000.
- Verdict: G13B_P3_HARD_PASS at smoke.
- smoke_wall_s = 20.18s.

## Timeout estimate
- Edge A: 1.5h = 5400s. Edge B: ~10 min. Edge C: ~5 min. Total ~6500s.
- Plus per-edge build_shared at N=4096 ~30s each = 1.5 min.
- Budget includes 1h headroom for Edge A drift.
- **timeout = 14400 s (4 h)**.
- Formula: scaled wall_target dominated by Edge A's 5400s target;
  ceil(1.5 * 5400 + 1500 + 300 * 3 + 90 build_shared) = 9990, round to 14400 for headroom.

## Self-test
- `_instrumentation_selftest()` at module scope.
- Each edge runs at N=1024 with accelerated parameters (target_wall=4s for A,
  n_ticks=10 for B, n_pre=3 for C).
- Asserts: A.total_ops>0 AND A.chain ok; B.audit ok AND protected_n>0;
  C.n_pre>=1 AND C.consistency exactly 1.0 (resume contract).

## Dependencies
- experiments/_multi_hop_mechanisms.py - exists.
- experiments/_metric_battery.py - exists.
- experiments/_workload_harness.py - exists.
- experiments/_seed_checkpoint.py - exists.
