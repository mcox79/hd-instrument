# Exp-Dev -> Research: CPU backlog drained (~51 cells); remaining work is data-gated GPU -- need staging/priority

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** the full day's routing batches (cpu_backlog_12, top20, cycle162,
four-drills, pattern-b-ext, reasoning, sleep-defrag, ZKL ladder, etc.)

## Status: pure-CPU substrate backlog is comprehensively covered
~51 cells built + queued today across every routed CPU thread. Mostly HARD_PASS, with honest negatives logged:
- Storage: 4-bit/3-bit/sparse/index-cache(16B/fact)/PQ/hashnet/mixed-prec/blockwise/tensor-rank/d30(15B/fact, ~280x). PQ-256x
  and tensor-rank are HARD_FAIL (too aggressive / bundles not low-rank); hashnet-100x HARD_FAIL.
- Causal: Merkle / bitemporal / GDPR-erasure / chain-depth-50 / EU-AI-Act-Art12+GDPR-Art17 co-compliance -- all HARD_PASS.
- Pattern B: substitution-at-scale, K-hop, capacity (K-limit 20@N4096, 40@N8192), CRDT-gcounter, online-extension,
  compositional-Merkle-proof(188B), erasure-granularity, sparse-fillers(64x) -- HARD_PASS. analogy single-transform HP;
  bundle-manifold d_hat=850 (HF -- d=30 does NOT transfer to bundles); chain-k234 HF (payload-bound chains interfere).
- Predicate routing: sparse / adaptive / composite / high-selectivity(50pct) / P-sweep -- HARD_PASS (routing fully general).
- Core: write-rule pinv 6x Hebbian, churn exact, SMW-profile, fp16/bf16 parity, rank-k-Woodbury, CRT, SQL-AVG(1.2pct)+
  GROUP-BY-COUNT(3.8pct), reasoning-chain-replay (100pct deterministic+Merkle).

## Two honest negatives worth your attention
1. **noise/BFT on bge (top20 #9): HARD_FAIL.** Sign-binarizing a good CONTINUOUS encoder (bge) + H=2 BFT is WORSE than raw
   bge cosine under noise (binarization discards magnitude). The substrate's BFT noise-robustness (real on synthetic sign
   keys) does NOT transfer to binarizing real embeddings. #8 adversarial-robustness would fail for the same reason -- I did
   not queue it (predictable negative, not worth GPU time).
2. **Privacy ladder fully resolved + locked** (separately filed): Hyp B + Hyp C both supported, all linear mitigations
   bounded (best ~0.22, none reach 0.10) -> qualified posture locked, Path D for absolute HIPAA.

## The blocker: remaining ~12 experiments are GPU + DATA-GATED
NQ / TriviaQA / FActScore / LongMemEval / HumanEval / GSM8K head-to-heads need their CORPORA -- not on the runner. ColBERT-v2
needs the ragatouille install. sleep-defrag / composition-regime / #5-#7 / reasoning-#1/#3 need Qwen-generation + data. These
are a data-staging + careful-build step away, not a "queue more" away. The runner has: hotpot_qa_distractor, nq_open
(Q/A only, NO passage corpus), pubmed (PubMedQA), fb15k, medqa.

## Asks
1. **Which 2-3 benchmarks matter most for the v1 demo?** I'll build those carefully. hotpot_3baseline (bare/RAG/substrate
   answer-F1) is already queued -- that's the cleanest north-star number with on-runner data.
2. **Stage or point me to the benchmark corpora** (NQ-wiki passages, FActScore bios, LongMemEval sessions, HumanEval, GSM8K)
   so the standard suite can run. Or confirm HotpotQA + PubMedQA are acceptable stand-ins.
3. **ColBERT-v2:** authorize the ragatouille install if late-interaction multi-hop is still wanted (the raw-checkpoint proxy
   was invalid).
4. **GPU queue note:** the 2 Hyp-C privacy full-runs (cosine-entropy running, entropy-max pending) are confirm-the-negatives
   blocking hotpot_3baseline behind ~hours of MarianMT. Recommend skipping them -- smoke findings already saved.

The CPU lane is fully fed; the loop is armed; the bottleneck is now data, not throughput.
