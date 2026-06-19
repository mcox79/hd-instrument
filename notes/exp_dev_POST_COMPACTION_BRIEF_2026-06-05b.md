# Exp-Dev POST-COMPACTION BRIEF (2026-06-05 ~15:50) -- READ FIRST after context reset

Role: Exp-Dev (4-session arch). Write/derive experiment scripts, smoke-verify, queue_add to remote runners. Do NOT
interpret verdicts (Orchestrator owns); read data/exp_<name>/metrics.json for completion only. User wants BOTH CPU+GPU
fed with high-priority work + queue healthy; checks frequently.

## PHASE STATE: Phase 2 (Llama-1B) OPEN + envelope HP-1..HP-12 COMPLETE.
Llama-1B per-token residuals on runner: data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/residuals_per_token.npz
(106427 tokens, 2048-dim, doc_boundaries CSR, 10000 docs). Pythia per-token npz also valid (pertoken_v1 dir).

## FLAGSHIP RESULTS THIS SESSION (all HARD_PASS unless noted):
- Tier-4-Llama (CLOUD, Testbed): HARD_PASS -- ppl_ratio 0.98 (substrate BETTER), entropy 2.82, grad 0.8. Substrate-as-
  attention SCALES to 1B (GQA+RoPE, swap layer 8). 14th-15th flagship anchor.
- HP-12 killer-demo core: HARD_PASS smoke (cert 0.512ms, 0 phantom, third-party verifier 1.0, RSA accumulator). FULL=MIDDLE
  (RSA-512/M=1200 latency/scale nuance -- recheck). THE Phase-3 demo claim (architecturally impossible for LLMs).
- audit-core-1B: HARD_PASS (C2 deletion-cert 1.00, C3 drift 15.5x on real 1B residuals -- HIPAA wedge at 1B).
- HP-1 long-conv-1k HP, HP-8 long-conv-10k HP, HP-2 multidoc-1000 HP, HP-3 30day-continual HP, HP-4 substrate-MAX-reasoning HP,
  HP-6 introspection+deletion-cert HP, HP-9 multimodal-binding HP, HP-11 distshift HP, K2-XOR rescue HP (synthetic 4.54x).
- EX-CONCEPT-1B MIDDLE (bigram-level architectural), K2-XOR-1B MIDDLE (mechanism confirmed K3>trigram), K-fact-anchors
  MIDDLE (beta*+Rule8 VALIDATED for HP-7), HP-5 medical MIDDLE (deletion-cert ok, MedQA Pythia-ceiling), HP-7 e2e
  borderline (1.48x + cert reconstructible 1.0), strong-baselines-1B HF (extctx<neural; XOR is the better encoding).

## IMMEDIATE NEXT / OPEN WORK
1. CRITICAL-PATH BLOCKER: HNSW sub-linear cleanup (gates HP-12-V2 scale to 1M facts). Cell built
   (experiments/exp_substrate_hnsw_sublinear_cleanup_v1.py) but FAISS HANGS on runner (Windows OpenMP deadlock:
   libomp140 vs libiomp5; KMP_DUPLICATE_LIB_OK + OMP_NUM_THREADS=1 + faiss.omp_set_num_threads(1) did NOT fix the
   IndexHNSWFlat.add hang). FLAGGED to Testbed (exp_dev_to_testbed_faiss_hnsw_env_hang) -> needs runner-env fix OR
   cloud-Linux run. When faiss works: HNSW HP gate = 3200x speedup + recall@1>=0.97 at M=1M.
2. HP-12 V2 build sequence (research HP12_core_HP_ack, ~3-5 days): HP-7 V2 scale to 100k -> HP-12 at 1M PubMed (needs
   PubMed full-corpus extraction, Testbed cloud) -> HIPAA API (4 endpoints) -> third-party verifier -> 5-min screen recording.
3. Phase-2 model-load reruns -> CLOUD via Testbed (8GB OOM locally): MedQA-at-Llama-1B (lifts the MedQA ceiling),
   CCC-1-v2 generation at 1B.
4. CAPTURE pending verdicts: HP-7, HP-9, HP-11, HP-12, K-fact, strong-baselines, EX-CONCEPT-1B (full).

## ROUTING DISCIPLINE (load-bearing)
- Residual-only / numpy cells -> remote_cpu_queue (local CPU). torch/Pythia-decoder small cells -> overnight_queue (local 8GB GPU OK).
- Llama-1B MODEL-LOAD cells (Tier-4, generation) -> CLOUD via Testbed (8GB OOM). User pre-authorized cloud ~$1-3/run for Tier-4-class.
- Cloud GPU is Testbed's lane: write the cell + a routing note w/ spec + user-auth; Testbed dispatches.
- Local GPU may legitimately IDLE during Phase 2 (residual=CPU, model-load=cloud). Do NOT force it / do NOT pad with HF cells.

## BUILD GOTCHAS (learned this session -- propagate)
1. queue_add.sh CANNOT pass `-- args` -> use forced-mode COPY scripts (per-token, etc.).
2. SEQUENTIAL projection-deletion re-introduces crosstalk at earlier-deleted keys -> add a STABILIZING re-projection pass for 0 phantom.
3. PHANTOM/recall must be measured by ABSOLUTE recall strength (EV@r), NOT cosine (near-zero residual has meaningless high cosine). Propagate to all cert/audit cells.
4. BATCHED Hebbian (W += V.T@K, one matmul) not sequential cf-RPE loop (O(N^2)/write) -- continual-learning speed + avoids timeouts at scale.
5. Capacity: dense Hebbian KB caps ~0.3N clean; >N overloads (retention drops). Use N>=facts/0.5 OR sparse (FAISS-HNSW for 1M).
6. PCA-whiten store before audit-core; when orig-dim > M, whiten newb into store-space too (SVD reduces rank).
7. neural-baseline MCQ/LM: LEFT-pad sequences (real last token at pos -1); keep Y-assignment off the comment line.
8. RAW (not sign()) retrieval when feeding structured-recovery (sparse composites). Pythia: dtype=float32+grad-clip, attn eager, TOKENIZERS_PARALLELISM=false, truncation_side='left' (keep query).
9. faiss on runner: Windows OpenMP deadlock (see blocker #1) -- cloud-Linux or env-fix needed.
10. sklearn 1.8/1.9 + faiss 1.8.0 installed on runner venv.

## RUNNER MECHANICS
- marsh@home, C:\dev\hd-instrument, .venv\Scripts\python.exe. queues data\<q>\queue.json. queue_add.sh <queue> <name> <script_rel> <prereg_rel> <timeout_s> [--allow-duplicate].
- Verdicts: ssh + read data/exp_<name>/metrics.json .verdict. RUNNER-HEALTH: pending>0+no heartbeat -> flag orchestrator (do NOT restart); exp cpu_s~0/no completions>40min -> taskkill exp SUBPROCESS only (NOT runner_v2_prod).
- ASCII-only, write_metrics(), --self-test early-exit (gate runs it 180s), smoke-gate before queue, PROT-018/019/021/022. Atomic commit+push each cell.

## LOOP: ScheduleWakeup 1200s active (270s if user just asked "check in 5"). Re-pass the build-loop prompt each firing.
Read notes newermt (research_to_exp_dev_* / testbed_to_exp_dev_* / routing_* / orchestrator_*) every firing; build NEW routed cells; keep both queues backlog>=1 where cells exist.
