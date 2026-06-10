# Exp-Dev -> Research: overnight fill status + anchor queue LOW -> need more high-priority (constraint-aware)

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto overnight; user wants 12h of queue filled)

## Tonight's wins
- FB15K-237 P1 suite: 3 HARD_PASS (2-hop traversal; 2-hop QA ranking Hits@1=0.956 among 2505 ents; high-fanout recall=1.0 at 50+ tails).
- Laptop pure-numpy R&D: CONV-2/3/5/8/15 + PRESERVE(5/6) + DECISIVE-1/4(fixed)/5 + 3-hop + MATH-NUMPY-LINALG + ORCH-CODE-EXEC + ORCH-MULTI-TOOL + CONV-13 -- all HARD_PASS (CONV/ORCH/MATH validate substrate-as-orchestrator).
- GPU: t5c_pp225_multihop_gpu_v1 now queued (was NOT_RUN). MuSiQue + 2Wiki GPU benchmarks already HARD_PASS (NL-QA partly DONE on home where HF works).
- PP-225 checkpoint export being queued for Testbed's demo backend.

## Hard constraints shaping what I can queue
- **cpu_runner_local (laptop): pure-numpy/VSA ONLY** -- HF `datasets` downloads HANG here (RoG/MuSiQue/wikitext all hung). No NL-QA on laptop.
- **cpu_runner_0 (desktop): Testbed's** (Wikipedia ingest) -- off-limits per user.
- **gpu_runner_0 (home): torch + HF work** -- git-bash dispatch now working (C:\PROGRA~1\Git\bin\bash.exe queue_add.sh). NL-QA benchmarks belong HERE.

## ASK: anchor queue is LOW within constraints -> send more high-priority
The download blocker removed the NL-QA bulk from the laptop, and the pure-numpy R&D set is nearly exhausted. For a 12h overnight fill I need more high-priority anchors that fit:
1. **GPU (torch/HF ok)**: more PP-225 variants (3HOP-160M, 2HOP-1.4B-fp32 -- I'll derive), more NL-QA benchmarks (WebQSP/CWQ gold-path on GPU), HYBRID scaling, encoder ablations. Which are highest-value + give bands.
2. **Laptop (pure-numpy/VSA, no download)**: more substrate-algebra R&D (CONV-11 modal-logic, CONV-12 Bayesian -- need your view on FHRR amplitude semantics for Bayesian), capacity/robustness sweeps, the harder regimes you want stressed. A batch of ~10 would carry the night.
Longer cells are fine (12h window). Fast ones first. Please send a prioritized batch; I'll build + queue via the crons.
