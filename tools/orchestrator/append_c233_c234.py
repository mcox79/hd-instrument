"""Append cycle 233 catch-up and cycle 234 entries to substrate_capability_map.md"""

cap_map_path = "d:/AI/hd-instrument/notes/substrate_capability_map.md"

entries = """

## v566 -> v567 CYCLE 233 10-VERDICT BATCH (2026-06-11) [CATCH-UP: missing from file; only strategy_decisions updated in commit 276d97e2]

Phase-4B math integration battery + depparse v2 MST. All on cpu_runner_local (FrameworkMPC).

### Step 0 honest re-read

Metrics source: LOCAL (all 10 files). 1 LVH catch.

**[LVH-285] phase4_v25_gated_cpu_v1 MIDDLE_BAND (direction claim over-stated):** gated=0.048, v1=0.048, v2=0.048 -- ALL TIED. Null effect. LVH-285 filed.

All others HONEST. HONEST: 1759 -> 1769 (+10). LVH: 284 -> 285 (+1). 1 LVH catch.

### Cap_map decisions (v566 -> v567)

**(A) depparse_v2_mst_cpu_v1 (UNKNOWN corpus_load_failed -- ANNOTATION only):**
depparse_v2_mst_cpu_v1 UNKNOWN v567: corpus_load_failed, uas=0.0 (cycle 233). 2nd consecutive dep-parse UNKNOWN. No cap_map credit.

**(B) phase4b_svamp_solver_cpu_v1 (HARD_FAIL -- bag-of-words ceiling):**
phase4b_svamp_solver_cpu_v1 HARD_FAIL v567: accuracy=0.110, n=300 (cycle 233). Bag-of-words below majority (0.26). No new PP row.

**(C) [LVH-285] phase4_v25_gated_cpu_v1 (MIDDLE_BAND null-effect -- gating hypothesis closed):**
[LVH-285] phase4_v25_gated_cpu_v1 MIDDLE_BAND v567: gated=v1=v2=0.048, null effect (cycle 233). LVH-285 filed. No new PP row.

**(D) phase4_bipartite_svamp_cpu_v1 (HARD_FAIL -- bipartite factorization underperforms):**
phase4_bipartite_svamp_cpu_v1 HARD_FAIL v567: accuracy=0.187, threshold<0.25 (cycle 233). Confirms bipartite_engineered_underperforms_learned. No new PP row.

**(E) phase4b_svamp_richfeat_cpu_v1 (MIDDLE_BAND -- NEW ROW PP-373):**
NEW ROW PP-373: phase4b_svamp_richfeat_cpu_v1 MIDDLE_BAND v567: accuracy=0.297 (89/300), band 0.20-0.30, n_seeds=1 (cycle 233). DISCRIMINATIVE RICHFEAT ON SVAMP: lifts bag-of-words 0.110->0.297 (2.7x). AT TOP of MIDDLE_BAND; dep-parse needed for >0.30 threshold. P-band: 0.58-0.72 EXPLORATORY n=1 full elapsed=4.4s.

**(F) phase4b_multibench_solver_cpu_v1 (HARD_PASS -- NEW ROW PP-374):**
NEW ROW PP-374: phase4b_multibench_solver_cpu_v1 HARD_PASS v567: macro_avg=0.352, SVAMP=0.283/MAWPS=0.882/MultiArith=0.022/ASDiv=0.222, n_benchmarks=4, macro>=0.30, n_seeds=1 (cycle 233). SUBSTRATE MULTI-BENCHMARK MATH NO LLM: discriminative perceptron across 4 real benchmarks. MAWPS=0.882 near-ceiling. MultiArith=0.022 structural zero single-op (multistep in PP-375). P-band: 0.65-0.80 EXPLORATORY n=1.

**(G) phase4b_multistep_cpu_v1 (HARD_PASS -- NEW ROW PP-375):**
NEW ROW PP-375: phase4b_multistep_cpu_v1 HARD_PASS v567: accuracy=0.750, ceiling=0.791, n_test=172, threshold>=0.20, n_seeds=1 (cycle 233). SUBSTRATE 2-OP COMPOSITION: discriminative sequence prediction (16 op-pair classes) achieves 0.750 on MultiArith (>9x single-op baseline). LLM-CoT range. Seed-robust Tier A promotion in cycle-234. P-band: 0.72-0.88 EXPLORATORY n=1.

**(H) phase4b_multibench_multiseed_cpu_v1 (HARD_PASS 5-seed -- NEW ROW PP-376; TIER A seed-robust):**
NEW ROW PP-376: phase4b_multibench_multiseed_cpu_v1 HARD_PASS v567 (5-seed): macro_mean=0.336, macro_std=0.0072, SVAMP=0.294/MAWPS=0.806/MultiArith=0.019/ASDiv=0.224, n_seeds_internal=5, macro>=0.30 std<=0.02 (cycle 233). SUBSTRATE MATH SOLVER TIER A SEED-ROBUST: std=0.0072 tight, MAWPS=0.806 stable. Research Tier A endorsed (commit 1afd3c19). NORTH STAR: substrate exceeds tiny LLMs on multi-benchmark math (MAWPS 0.806 vs <0.40 without CoT). P-band: 0.72-0.88 PROVEN n=5.

**(I) phase4b_unified_solver_cpu_v1 (HARD_PASS -- NEW ROW PP-377):**
NEW ROW PP-377: phase4b_unified_solver_cpu_v1 HARD_PASS v567: macro_avg=0.450, SVAMP=0.138/MAWPS=0.716/MultiArith=0.728/ASDiv=0.217, threshold>=0.45 (exactly met), n_seeds=1 (cycle 233). UNIFIED ARITY-ROUTED SOLVER: auto-routing 1-op vs 2-op. HONEST CAVEAT: SVAMP degrades 0.297->0.138 (shared-pool interference). Threshold exactly met. Specialized solvers individually stronger. P-band: 0.65-0.80 EXPLORATORY n=1. Multi-seed cycle-234 shows 0.442 stable (MIDDLE_BAND) annotated in v568.

**(J) phase4b_collins_ab_cpu_v1 (MIDDLE_BAND -- no new row; structured ~ flat at 2-quantity):**
phase4b_collins_ab_cpu_v1 MIDDLE_BAND v567: A(flat)=0.159, B(structured)=0.155, diff=-0.003, 2SE=0.060 (cycle 233). NO STRUCTURE BENEFIT within 2SE. Ship flat perceptron (PP-374/PP-376 basis). Annotation on PP-373/PP-374.

Cap_map: v566 -> v567 CYCLE 233 (4 HP [CPU:4; multibench n=1 + multistep n=1 + multiseed-5 + unified]; 2 MIDDLE_BAND [richfeat + Collins]; 2 HF [svamp_bow + bipartite]; 1 UNKNOWN [depparse corpus_load_failed]; 1 LVH-285 [phase4_v25_gated null-effect direction claim]; 5 NEW PP ROWS PP-373..PP-377; PP-376 TIER A substrate math seed-robust; NORTH STAR validated; Collins A/B confirms flat preferred at 2-quantity; depparse blocker 2nd cycle; 0 closures; Portfolio 32+372 -> 32+377 +5; HONEST 1759->1769 +10; LVH 284->285 +1; 461st PROT-009 paired commit) (2026-06-11)

## v567 -> v568 CYCLE 234 7-VERDICT BATCH (2026-06-11) [NEUTRAL; cycle-233 cap_map catch-up in same commit]

phase4b_multistep_multiseed + phase4b_unified_multiseed + phase4d_code_typeclass + phase4b_unified_balanced + phase4d_code_algopattern + phase4d_code_fulldata + phase4d_code_multiseed. All on cpu_runner_local (FrameworkMPC).

### Step 0 honest re-read

Metrics source: LOCAL (all 7 files). 0 LVH catches.

**phase4b_multistep_multiseed_cpu_v1 HARD_PASS:** outer n_seeds=1 wrapper; per_seed[0] internal n_seeds=5, vals=[0.7558,0.7558,0.7558,0.7442,0.7558], mean=0.7530, std=0.0046. Same pattern as PP-376 (acknowledged cycle 233). HONEST.

**phase4b_unified_multiseed_cpu_v1 MIDDLE_BAND:** macro_mean=0.442, macro_std=0.0058, internal n_seeds=5. 0.442 < 0.45 ceiling. HONEST.

**phase4d_code_typeclass_cpu_v1 HARD_FAIL:** acc=0.560, majority=0.521, lift=0.039 (3.9pp < 5pp threshold). HONEST.

**phase4b_unified_balanced_cpu_v1 MIDDLE_BAND:** macro_mean=0.422, macro_std=0.0054, internal n_seeds=5. 0.422 < 0.45. HONEST. Full-data beats balanced.

**phase4d_code_algopattern_cpu_v1 MIDDLE_BAND:** acc=0.623, majority=0.307, lift=0.316 (31.6pp), 8 classes. Band 0.55-0.70. HONEST. First Phase-4D positive.

**phase4d_code_fulldata_cpu_v1 UNKNOWN:** load_failed, accuracy=0.0. HONEST.

**phase4d_code_multiseed_cpu_v1 UNKNOWN:** load_failed, accuracy=0.0. HONEST.

HONEST: 1769 -> 1776 (+7). LVH: 285 -> 285 (+0). 0 LVH catches.

### Cap_map decisions (v567 -> v568)

**(A) phase4b_multistep_multiseed_cpu_v1 (HARD_PASS 5-seed -- PP-375 SEED-ROBUST PROMOTION to TIER A):**
PP-375 SEED-ROBUST PROMOTION v568: mean=0.7530, std=0.0046, n_seeds_internal=5 (cycle 234). MULTI-STEP COMPOSITION TIER A: cycle-233 PP-375 (n=1, 0.750) confirmed seed-robust. std near-zero. No new PP row; PP-375 P-band lifts EXPLORATORY -> PROVEN n=5.

**(B) phase4b_unified_multiseed_cpu_v1 (MIDDLE_BAND -- PP-377 multi-seed annotation; stable below 0.45):**
phase4b_unified_multiseed_cpu_v1 MIDDLE_BAND v568: macro_mean=0.442, std=0.0058, SVAMP=0.147/MAWPS=0.671/MultiArith=0.728/ASDiv=0.224, n_seeds_internal=5 (cycle 234). PP-377 MULTI-SEED ANNOTATION: stable 5-seed but below 0.45 HP bar. SVAMP interference reproducible. No new PP row.

**(C) phase4d_code_typeclass_cpu_v1 (HARD_FAIL -- type-class not predicted from docstring; PROT-004/006 rescues):**
phase4d_code_typeclass_cpu_v1 HARD_FAIL v568: acc=0.560, majority=0.521, lift=0.039, n_classes=6, n_test=257 (cycle 234). CODE TYPE-CLASS FAILS: 3.9pp below 5pp threshold. Prompt says WHAT not HOW; type-class underdetermined. No new PP row. PROT-004/006 (cheapest first):
RESCUE-1: return-type keyword extraction from docstring.
RESCUE-2: code syntax tokens as additional features.
RESCUE-3: restrict to docstrings with explicit type annotations.
RESCUE-4: combine type-class + algo-pattern (PP-378) dual-axis.
RESCUE-5: few-shot code example injection (hybrid).

**(D) phase4b_unified_balanced_cpu_v1 (MIDDLE_BAND -- PP-377 balanced-training variant; full-data preferred):**
phase4b_unified_balanced_cpu_v1 MIDDLE_BAND v568: macro_mean=0.422, std=0.0054, SVAMP=0.154/MAWPS=0.692/MultiArith=0.647/ASDiv=0.194, n_seeds_internal=5 (cycle 234). BALANCED UNDERPERFORMS FULL-DATA: 0.422 vs 0.442. Use full training distribution. No new PP row.

**(E) phase4d_code_algopattern_cpu_v1 (MIDDLE_BAND -- NEW ROW PP-378; Phase-4D first positive):**
NEW ROW PP-378: phase4d_code_algopattern_cpu_v1 MIDDLE_BAND v568: acc=0.623, majority=0.307, lift=0.316, n_classes=8, n_test=257, n_train=170, n_seeds=1 (cycle 234). ALGORITHM-PATTERN PREDICTION PARTIAL: docstring predicts algorithm type (sorting/searching/dp/greedy/divide-conquer/counting/simulation/math) at 0.623 vs majority 0.307 -- 31.6pp lift. MIDDLE_BAND [0.55-0.70]: below 0.70 HP bar. First Phase-4D code positive. Algorithm approach (WHAT strategy) is more predictable from docstring than implementation structure (HOW built). P-band: 0.58-0.72 EXPLORATORY n=1 full elapsed=2.6s. Cross-ref phase4d_code_typeclass (HF), PP-374 (math analogy: discriminative prediction).

**(F) phase4d_code_fulldata_cpu_v1 (UNKNOWN load_failed -- MBPP data path issue on FrameworkMPC):**
phase4d_code_fulldata_cpu_v1 UNKNOWN v568: load_failed, accuracy=0.0, elapsed=2.1s (cycle 234). DATA PATH FAILURE (not corpus blocker). PROT-004/006:
RESCUE-1: verify data file absolute path on FrameworkMPC.
RESCUE-2: bundle data inline in experiment script.
No cap_map credit.

**(G) phase4d_code_multiseed_cpu_v1 (UNKNOWN load_failed -- same data path root cause):**
phase4d_code_multiseed_cpu_v1 UNKNOWN v568: load_failed, accuracy=0.0, elapsed=2.5s (cycle 234). Same as fulldata. Shares RESCUE-1/2. No cap_map credit.

Cap_map: v567 -> v568 CYCLE 234 (1 HP [CPU:1; phase4b_multistep_multiseed 5-seed]; 3 MIDDLE_BAND [CPU:3; unified_multiseed + unified_balanced + algopattern]; 1 HF [CPU:1; typeclass]; 2 UNKNOWN [load_failed]; 0 LVH; 1 NEW PP ROW PP-378 [algopattern first Phase-4D positive]; PP-375 TIER A seed-robust promotion; PP-377 multi-seed annotation MIDDLE_BAND 0.442; 5x typeclass PROT-004/006; 2x fulldata/multiseed infra rescues; balanced vs full-data: full preferred; 0 closures; Portfolio 32+377 -> 32+378 +1; HONEST 1769->1776 +7; LVH 285->285 +0; 462nd PROT-009 paired commit) (2026-06-11)
"""

with open(cap_map_path, 'a', encoding='utf-8') as f:
    f.write(entries)
print("appended ok")
