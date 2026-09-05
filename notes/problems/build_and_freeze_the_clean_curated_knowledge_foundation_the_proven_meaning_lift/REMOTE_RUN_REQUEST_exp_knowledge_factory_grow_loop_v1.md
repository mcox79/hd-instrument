---
cell: experiments/exp_knowledge_factory_grow_loop_v1.py
mode: full
queue: remote_cpu_queue
timeout_s: 3600
results_path: data/exp_knowledge_factory_grow_loop_v1/metrics_full.json
self_test: green
question: does multi-round grow-from-reading (ingest -> recurrence+PPMI prune -> additive accumulate) CLIMB held-out SimLex/WordSim rho over 6 rounds to a respectable frozen associative store, beating the raw-count (no-prune) arm and the shuffled-corpus info-free twin?
gate: final SimLex rho AND WordSim rho > the RAW-count arm (prune helps) AND > the SHUFFLED-corpus twin (info-free loses); rho climbs round-over-round (monotone within CI noise). Recompute on the covered-pair intersection; report CI half-width + null p95.
kb_referents:
  - data/corpora/simplewiki/simplewiki_clean_v1.txt
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
---
6 rounds x 3,000,000 tokens (18M of the 38M-token simplewiki), vocab cap 40k, WINDOW=2, PPMI alpha 0.75, SVD_K=300.
Bare invocation == FULL (smoke only via --smoke), so the remote bare run is the real one.
Arms per round: (a) MAIN = recurrence-gate(min_count=3) + PPMI + SVD -> SimLex/WordSim rho; (b) RAW-count no-prune
control (must lose -> the prune is what converts raw-regression into gain); (c) SHUFFLED-corpus info-free twin
(must lose). Accumulation is ADDITIVE co-occurrence (CLS, catastrophic-forgetting-free). Freezes
data/frontend_assets/associative_similarity_store_v1.npz = the reading-grown ASSOCIATIVE store (the SECOND typed
store; complements the frozen curated sense-discriminative C1 meaning_sense_signatures_v1.npz). Reuses the proven
exp_learn_from_reading_strong_arm_v1 reader machinery (does_learning_from_reading_deserve_to_continue, SOLVED). NO
external LLM, deterministic. Smoke locally GREEN: SimLex 0.061->0.078 climb, prune 0.070 >> raw -0.037, shuffled loses.
