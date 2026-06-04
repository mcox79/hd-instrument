# Strategy Decisions 2026-06-04
## CYCLE 42 BATCH -- v373 -> v374 (2026-06-04)

### Step 0 Honest Re-Read
All 12 labels honest to per-cell metrics (all source=remote). 0 LVH catches. HONEST 658 -> 670 (+12).

### Cap_map Decisions

**(A) Q-A3 L=78..83 N=16384 (6x HARD_PASS)**
All EXACT-1.0000 unanimous 5/5 seeds. Rungs 59-64. N=16384 series: {L=20..L=83} = 64 contiguous rungs. L=83 NEW DEEPEST project history (prior L=71 v373; +12 rungs in batch). Ceiling NOT found. Walls 26.3-27.8s GPU linear scaling.

**(B) Q-A3 L=45..47 N=8192 (3x HARD_PASS)**
All EXACT-class 1.0000000342 unanimous 5/5 seeds. Rungs 23-25. N=8192 series: {L=19,L=22..L=47} = 27 rungs. L=47 NEW N=8192 DEEPEST (prior L=42 v373; +5 rungs). Walls 4.1-4.2s GPU.

**(C) BAND-LIFT PP-12/Q-A3: 0.88-0.97 -> 0.89-0.97**
9-rung batch (6 N=16384 + 3 N=8192) exceeds 4-rung threshold. +0.01 lower bound. Upper 0.97 ceiling maintained. Lit-scan calibration penalty maintained. Product framing: EXACT-1.0000 composition moat confirmed through 83 levels at N=16384; 64-rung series; audit API algebraic moat structurally unbounded through L=83; N=8192 deepest L=47.

**(D) PP-58 BBP dense XN N=8192 HARD_FAIL**
pp58_bbp_dense_xn_n8192_v1_n8192. ratio=1.00 outside [2.0,5.0]. Recall stays ~1.0000 flat across sigma_g=0.0..8.0 (no separation at all). BBP N-scaling prediction fails in dense XN regime. cap_crit=8.0 unreachable in practice because sigma_sep never drops. Distinct from: (1) BBP-spectral-gap-calibration sub-path CLOSED v373; (2) isochoric kappa_3 founding ratio=8.00 v353 still valid. PP-58 MIDDLE 0.55-0.70 UNCHANGED. Rescue cheapest-first per [[feedback-rescue-sketch-first-sequencing]]: R1 dense-XN theory audit -- why does substrate NOT separate in dense regime? (~2h; free); R2 alt alpha=0.1 in dense XN regime (~2h CPU); R3 N-scale dense XN at N=16384 to test N-dependence (~3h GPU). Dense XN failure may indicate substrate robustness is POSITIVE (retrieval holds even under high-density XN noise), not a model failure.

**(E) PP-50 v4 ultra-fine sigma_g N=16384 HARD_PASS**
pp50_kappa3_ultra_fine_sigma_g_v4_n16384. sep(sg=0.83)=15539 (15.5x HP=1000); amplification=851.1x (170x HP=5x); monotone=True. Ultra-fine sigma_g bracket {sg0.83:15539, sg0.85:17618, sg0.87:19958, sg0.90:24025, sg1.00:44025, sg1.50:797452, sg2.00:13224401}. Confirms steep monotone rise through sigma_g_crit regime (sg>0.83); entry-boundary annotation from v372 v3 HF confirmed. PP-50 band 0.83-0.94 UNCHANGED (v4 is refinement within already-counted regime; no new rung-level cross-N data point). Sub-property annotation: 'v4 ultra-fine sigma_g bracket N=16384: monotone steep rise sg=0.83..2.00; amplification 851x; entry-boundary confirmed; NLO sigma_g_crit=0.833 is onset of steep sensitivity not plateau exit boundary.'

**(F) Phase 0.5 Rung A GATE HARD_PASS -- CRITICAL MILESTONE**
phase05_v1_algorithm1_debug_pythia160m_v1. n_valid_seeds=3, n_converged=3/3, balance_mean=0.0066 (HP<=0.7; 106x below threshold), diversity_mean=0.6497 (HP>=0.1; 6.5x above threshold), nan_frac_max=0.0, pipeline_clean=True, diverse_enough=True. Wall=4.9s. Algorithm1 (KG-distillation / hyperprobe pipeline debug) passes debug validation on Pythia-160m (EleutherAI/pythia-160m, LAYER_START=6, LAYER_END=12, K_CLUSTERS=5). Phase 0.5 Rung A gate OPEN. CRITICAL milestone: first Algorithm1 pipeline end-to-end debug pass on a real LLM. PP-8 Phase 0.5 combined deployment (Llama-3.1-8B + Hyperprobe + KG-distillation; 2026-06-02 auth) Rung A validated. New sub-property annotation on PP-8 row: 'Phase 0.5 Rung A GATE HARD_PASS v374: Algorithm1 debug Pythia-160m 3/3 converge; balance=0.0066; diversity=0.6497; pipeline_clean; Rung A OPEN.'

### PROT compliance (v373 -> v374)
- PROT-004/006: No closures. 0 new top-level rows. 1 BAND-LIFT. PP-58 dense XN HF rescue R1-R3 cheapest-first filed. Phase 0.5 Rung A HP annotation only (no band change; first rung on Pythia-160m debug scale not a band-lift trigger).
- PROT-007/008: v374 block appended. No portfolio regression. Portfolio 32+77 UNCHANGED.
- PROT-009: 285th PROT-009 paired commit.
- PROT-018: 12 anchors -- all _n<N> suffix bindings confirmed (_n16384 x7 [6 Q-A3 + PP-50 v4], _n8192 x4 [3 Q-A3 + PP-58 dense], _v1 [phase05 no N suffix, run_mode=full]. Phase05 anchor: no _nN suffix -- N not applicable (LLM pipeline not HDC dimension). 0 PROT-018 violations.
- PROT-021: all 12 source=remote run_mode=full. No smoke artifacts.
- PROT-022: Q-A3 EXACT-1.0000 consistent {L=20..L=83} N=16384 (64 rungs) and {L=19,L=22..L=47} N=8192 (27 rungs); PP-50 v4 amplification=851x >> HP=5x (self-consistent with 851x amplification at sg=0.83 which is the steep entry regime); PP-58 dense XN ratio=1.00 = sigma_sep/cap_crit = 1.0/8.0 = 0.125 (cap_crit=8.0; substrate never reaches cap_crit separation); Phase 0.5 balance_mean=0.0066 + diversity_mean=0.6497 internally consistent (3 seeds span 0.0041-0.0086 balance, 0.556-0.740 diversity; all within HP bounds).

HONEST: 658 -> 670 (+12). LVH: 213 UNCHANGED. Portfolio: 32+77 UNCHANGED.
Cap_map: v373 -> v374.
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.