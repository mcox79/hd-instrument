
## CYCLE 128 -- 2026-06-06 -- 3-VERDICT BATCH (substrate_etf_hadamard_n_sweep_capacity_v1 + hoc1_word_bigram_v1 + effective_rank_svd_v1)

### labeled-vs-honest entries

**LVH #229: substrate_etf_hadamard_n_sweep_capacity_v1**
- Label: HARD_PASS "ETF Hadamard lift persists >=5x at N=2048 -- Phase-3 linear capacity scales (~10x more facts)"
- Honest reading: HP-SMOKE. run_mode=smoke, n_seeds=1. 2 N-values only (1024, 2048). Per-cell ratios 8.02x/8.03x both clear >=5x threshold, but smoke/single-seed is not sufficient for HARD_PASS. "Phase-3 linear capacity scales" extrapolation from 2 smoke points premature.
- Cells contradicting: run_mode=smoke n_seeds=1 (PROT-021/022 multi-seed requirement not met).
- Downstream action: cap_map receives HP-SMOKE annotation not closed HARD_PASS. Full multi-seed N-sweep required to close.

**LVH #230: hoc1_word_bigram_v1**
- Label: HARD_PASS "WORD bigrams rescue order-sensitive hallucination detection (AUC>=0.90) -- gate closes, no NLI needed"
- Honest reading: HP-SMOKE. run_mode=smoke, n_seeds=1. auc_shuffle=0.970 is genuinely excellent (>> 0.90 threshold, 4.5x above char-ngram baseline). But "gate closes" from 1 smoke seed is a closure-level claim not supported by smoke protocol.
- Cells contradicting: run_mode=smoke n_seeds=1; gate-closed declaration requires multi-seed full run.
- Downstream action: cap_map receives HP-SMOKE / gate-OPEN annotation. Full multi-seed run required before gate-closed declaration.

**effective_rank_svd_v1: LABEL HONEST. No LVH.**

### Strategy decisions

1. Capacity-scaling row receives HP-SMOKE annotation for Hadamard N-sweep. No band move. Phase-3 floor update deferred pending full multi-seed N-sweep. Prior 3-N corroboration (smoke 1024/2048 + full 4096 from v439) is strong but not sufficient for plan update.

2. KF-1 row receives HP-SMOKE annotation for hoc1_word_bigram. No band move. Band-lift (72-87% -> ~75-90%) is a candidate if full multi-seed run replicates auc_shuffle >= 0.90. Gate-closed declaration requires unanimous multi-seed full run.

3. effective_rank_svd confirms DT/intrinsic-dim framework. PP-8 and Phase-4A rows receive d_eff=82 constraint annotation. This is a hard constraint on all real-encoder operations at MiniLM N_sub=384: whitening (v441) and dim-expansion (v444) are bounded by d_eff=82, not D=384. Larger encoder is the primary lever for Phase-4 capacity expansion.

4. HONEST: 977 -> 980 (+3). LVH: 228 -> 230 (+2).

5. Portfolio 32+77 UNCHANGED. 0 row state changes. 0 band-lifts. 0 closures.

Cap_map: v449 -> v450 CYCLE 128 (0 HP; 0 HF; 3 SMOKE-PASS; 2 LVH #229+#230: etf_hadamard_n_sweep HP-SMOKE-N1024/2048-8x-FLAT-NOT-HARD_PASS + hoc1_word_bigram HP-SMOKE-AUC-0.970-GATE-OPEN; effective_rank_svd HONEST-D_EFF-82-INTRINSIC-DIM-CONFIRMED; HONEST 977->980 +3; LVH 228->230 +2; KF-1 72-87% UNCHANGED; Portfolio 32+77; 362nd PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
