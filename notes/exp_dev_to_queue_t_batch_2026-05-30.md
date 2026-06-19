# T-batch routing-note (5 anchors)

User-routed Path-D-focused + Path-BCE-characterization batch. Tests 14, 15,
22-alt, 23, 24 from user research plan. Queued behind S-batch (S2 latency
crossover currently running).

Shipped 2026-05-30 by exp_dev via queue_add.sh. All 5 REMOTE VERIFIED.

```
queue=overnight_queue name=path_d_mixed_confidence_v1_n4096 script=experiments/exp_path_d_mixed_confidence_v1_n4096.py prereg=preregs/2026-05-30_path_d_mixed_confidence_v1_n4096.md timeout=14400
queue=overnight_queue name=path_d_edit_isolation_under_load_v1_n4096 script=experiments/exp_path_d_edit_isolation_under_load_v1_n4096.py prereg=preregs/2026-05-30_path_d_edit_isolation_under_load_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=n_scaling_cpu_only_v8_n16384 script=experiments/exp_n_scaling_cpu_only_v8_n16384.py prereg=preregs/2026-05-30_n_scaling_cpu_only_v8_n16384.md timeout=86400
queue=overnight_queue name=path_e_engineering_characterization_v1_n4096 script=experiments/exp_path_e_engineering_characterization_v1_n4096.py prereg=preregs/2026-05-30_path_e_engineering_characterization_v1_n4096.md timeout=14400
queue=overnight_queue name=path_b_subcapacity_characterization_v1_n4096 script=experiments/exp_path_b_subcapacity_characterization_v1_n4096.py prereg=preregs/2026-05-30_path_b_subcapacity_characterization_v1_n4096.md timeout=14400
```

## Plain-language description

- **T1** (Test 14): Extends Path D with per-fact confidence weighting in
  likelihood queries + Bayesian posterior. Tests whether substrate yields
  CALIBRATED multi-hop reasoning — the key differentiator for regulated
  industries (legal / medical / audit).
- **T2** (Test 15): Path D under concurrent edits at rates 10 / 100 / 1000
  per second crossed with on-path / off-path / mixed patterns (9 cells).
  Tests whether Path D's per-candidate Bayesian evaluation gives natural
  edit-isolation for streaming agentic workloads.
- **T3** (Test 22-alt): 8th attempt at N=16384 Modern Hopfield activation
  bend. v4 / v5 / v6 / v7 all GPU-OOM. v8 abandons GPU codebook
  construction; pure-CPU chunkwise build on the remote runner (16+ GiB
  RAM available). 4 M-points (N/8, N/4, N/2, N) x 3 seeds.
- **T4** (Test 23): Path E characterized across 3 niche use cases:
  (A) top-K ranking at K=5000/10000, (B) early-termination within 50 ms
  budget, (C) latency-sensitive partial-accuracy tradeoff at sigma sweep.
  Tests whether Path E earns NICHE killer-feature classification.
- **T5** (Test 24): Path B characterized at Pattern B LLM integration
  regime (M=50-500, sub-capacity). 4 M-points x 3 depths x 5 seeds. Tests
  whether continuous-output substrate yields geometric-interpolation
  cosine >=0.85 + lat_b<lat_d AND accuracy >=0.90 in this regime.

## Pre-reg discipline

All 5 preregs include HARD_PASS + HARD_FAIL + MIDDLE_BAND bands. Per-test
self-tests called at module scope. Smoke gate PASS on all 5; instrumentation
self-tests PASS on all 5.

PROT-018 binding satisfied (T1/T2/T4/T5 contain N = 4096; T3 contains N =
16384). PROT-019 large-N timeouts satisfied (14400s / 86400s tier-floors
respected).

## Scientific stakes

- T1+T2 stress-test the Path D "production-scale robust" classification
  (v288 unanimous 1.000 through depth=20 M=24576).
- T3 finally resolves the N=16384 MH-bend open question.
- T4+T5 establish Path B and Path E's NICHE killer-feature classifications
  (which Pattern B / Pattern E use cases survive).
