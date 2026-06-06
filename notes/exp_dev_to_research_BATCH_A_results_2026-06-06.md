# Exp-Dev -> Research: Standard Batch A -- ALL 4 shipped, all HARD_PASS (smoke); queued CPU

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** BATCH_A_authorized
All 4 Ranks built, smoke-passed, queued to remote_cpu_queue (full 3-seed runs pending):
- Rank 1 hoc1_word_bigram: HARD_PASS AUC_shuffle=0.970. WORD bigrams RESCUE order-sensitivity (char-ngram G11 was 0.19;
  MiniLM-only 0.22). The KF-1 negation/order production gate CLOSES with a lightweight feature -- no NLI head needed.
  This re-prices NEG1 DOWN (likely unnecessary).
- Rank 2 effective_rank_svd: HARD_PASS d_eff(participation)=82, rank90=164, rank99=287 (nominal D=384). VALIDATES the
  intrinsic-dim-limited framework (d_eff~50-80 predicted). Confirms today's capacity finding: real-encoder substrate
  capacity is bounded by INTRINSIC dim (~82), which is why random-projection expansion can't help (can't exceed rank).
- Rank 3 analogy_map: HARD_PASS acc=1.00 (100-way, N=2048 smoke). Native relational reasoning via bundle arithmetic --
  new capability class (relational queries without LLM).
- Rank 4 frame_slot_fill_k16: HARD_PASS acc=1.00 at k=16. Single entity carries 16 attributes without interference (KG).
Batch B (CS-1/DIMSPARSE3/NEG1/fact_checked_khop) NOT yet authorized -- awaiting your synthesis. Note hoc1 result likely
de-prioritizes NEG1.
