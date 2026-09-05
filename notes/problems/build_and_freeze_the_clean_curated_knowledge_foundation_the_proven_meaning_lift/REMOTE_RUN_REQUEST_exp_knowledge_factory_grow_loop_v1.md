---
cell: experiments/exp_knowledge_factory_grow_loop_v1.py
args: "--broad"
queue: remote_cpu_queue
timeout_s: 10800
results_path: data/exp_knowledge_factory_grow_loop_v1/metrics_full.json
self_test: green
question: does a BROAD, BALANCED multi-genre ingestion (fiction + mystery + drama + textbook-science/social + graded readers + news + social-commonsense + capped encyclopedic/ARC = ~50M balanced tokens, 80k breadth-preserving vocab, 5 rounds, recurrence(min_count=2)+PPMI pruned, additive-accumulated) build a SIGNIFICANTLY LARGER, BREADTH-covering pruned associative store whose held-out SimLex/WordSim rho climbs, beating the raw-count (no-prune) arm and the shuffled-corpus info-free twin?
gate: final SimLex rho AND WordSim rho > the RAW-count arm (prune helps) AND > the SHUFFLED-corpus twin (info-free loses); rho climbs; the frozen store is >= 80k words spanning MANY genres (breadth_sources reported in metrics). Report CI half-width + null p95 on the covered-pair intersection.
kb_referents:
  - data/corpora/simplewiki/simplewiki_clean_v1.txt
  - data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt
  - data/encoder_eval_benchmarks/simlex999.txt
  - data/encoder_eval_benchmarks/wordsim353_combined.csv
---
THE SUBMISSION'S "significantly larger, BROAD, pruned KB" build -- breadth over raw volume. `--broad` = 5 rounds x
10M tokens, BALANCED across ALL genres via _stream_balanced (every diverse corpus read fully; simplewiki + ARC
CAPPED at 15M each so fiction / graded-readers / textbooks / drama / social-commonsense are a real fraction),
vocab_cap 80000 with a LOW min_count=2 floor so the low-frequency narrative vocabulary SURVIVES (a global count
floor would delete exactly the breadth we ingested), PPMI surprise-weighting does the real prune, SVD_K=300,
recurrence min_count=2. WHY BREADTH: different genres feed different typed stores -- encyclopedic -> topical
similarity; NARRATIVE/children's -> the concrete action-verb selectional preference + affect + goal + spatial/causal
knowledge the LIVE reader consumers read. Freezes data/frontend_assets/associative_similarity_store_v1.npz. Local
round-1 (10M broad) GREEN: SimLex 0.204 (raw 0.011, shuffled -0.081), WordSim 0.523 -- already ABOVE the narrow
12M-simplewiki store, confirming breadth-per-token. Reuses exp_learn_from_reading_strong_arm_v1 reader machinery.
NO external LLM, deterministic, no module-level spaCy. metrics_full.json (with breadth_sources genre breakdown)
returns via the ~20-min sync; the ~48MB frozen .npz is pulled via scp_recover_landing.py (strategy remote-op lane).
