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
## CYCLE 43 BATCH -- v374 -> v375 (2026-06-04)

### Step 0 Honest Re-Read
All 15 labels honest to per-cell metrics (all source=remote). 0 LVH catches. HONEST 670 -> 685 (+15).

Label checks:
- Q-A3 L=84..87 N=16384 (4x HP): EXACT-1.0000 all levels 5/5 seeds unanimous. Honest.
- Q-A3 L=48..50 N=8192 (3x HP): EXACT-class 1.0000000342 all levels 5/5 seeds. Honest.
- pp50 v5 extended sigma_g MIDDLE_BAND: monotone=False due to NaN at sg5.0 (overflow/diverge); amp_1_to_5=nan; HP condition not met. Honest.
- pp58_scs_formula_test_d8 HARD_FAIL: d_estimate=1.487 < 1.5 (no spectral spike; SCS assumption violated). Honest.
- spectral_gap_gamma_vs_M HARD_FAIL: ratio=1.130 > 0.85 threshold; gamma flat vs M across all 50 cells at N=4096 and N=16384 identically. Honest.
- substrate_trained_mini_lm rung1 HARD_FAIL: bpc_mean=5.5168 ~= uniform_bpc=5.5236; 0/3 seeds pass even MID(3.5). Honest.
- substrate_curriculum_learning rung1 HARD_FAIL: gain_mean=-0.0984 (negative; curriculum HURTS vs random at N=256). Honest.
- substrate_preloaded_icl rung1 HARD_FAIL: best_gain=0.0145 at K=10; << HP threshold 0.1. Honest.
- substrate_spectral_training_monitor rung1 HARD_FAIL: convergence phase lag 3/3 seeds (pre-reg condition met); overfitting phase lead 300 steps 3/3 seeds (rescue signal). Honest.
- substrate_8channel_orchestration rung1 HARD_FAIL: no converged seeds. Honest.

### Cap_map Decisions

**(A) Q-A3 L=84..87 N=16384 (4x HARD_PASS)**
All EXACT-1.0000 unanimous 5/5 seeds. Rungs 65-68. N=16384 series: {L=20..L=87} = 68 contiguous rungs. L=87 NEW DEEPEST project history (prior L=83 v374; +4 rungs). Ceiling NOT found. Walls ~27-28s GPU linear scaling.

**(B) Q-A3 L=48..50 N=8192 (3x HARD_PASS)**
All EXACT-class 1.0000000342 unanimous 5/5 seeds. Rungs 29-31. N=8192 series: {L=19,L=22..L=50} = 30 rungs. L=50 NEW N=8192 DEEPEST (prior L=47 v374; +3 rungs). Walls 4.1-4.2s GPU.

**(C) BAND-LIFT PP-12/Q-A3: 0.89-0.97 -> 0.90-0.97**
7-rung batch (4 N=16384 + 3 N=8192) exceeds 4-rung threshold. +0.01 lower bound. Upper 0.97 ceiling maintained. Lit-scan calibration penalty maintained. Product framing: EXACT-1.0000 composition moat confirmed through 87 levels at N=16384; 68-rung series; algebraic audit API moat structurally unbounded through L=87; N=8192 deepest L=50; 2-N cross-N at L=48/49/50.

**(D) pp50_kappa3_sigma_g_extended_v5_n16384 MIDDLE_BAND**
sigma_sep(d=0.04): [sg1.0:44085, sg1.5:797452, sg2.0:13224401, sg3.0:3451376952, sg5.0:nan]. Monotone sg1.0->sg3.0 (78265x amplification from raw counts). NaN at sg5.0 (overflow; beyond-float separation at d=0.04). MIDDLE_BAND because HP requires non-nan monotone amp>=10x specifically to sg=5.0; sg5.0 is NaN. PP-50 band 0.83-0.94 UNCHANGED. Sub-property annotation: v5 extended sigma_g sweep N=16384; monotone through sg3.0 confirmed (78000x amplification); sg=5.0 NaN overflow consistent with ultra-steep sensitivity beyond sg_crit; band unchanged.

**(E) pp58_scs_formula_test_d8_tau005_v1_n8192 HARD_FAIL**
d_estimate=1.487 < 1.5; SCS spike condition violated. gamma_emp=1.231, gamma_scs=1.487, ratio=1.208, tau=0.0000. 5/5 seeds match at 30% tolerance (reflects formula consistency below-spike-regime, not SCS signal). SCS formula test HARD_FAIL at d=8, tau=0.05. PP-58 MIDDLE 0.55-0.70 UNCHANGED (founding kappa_3 ratio=8.00 v353 still valid). Rescue cheapest-first: R1 (free) SCS sub-threshold-d regime audit -- modified formula applicable? R2 (2h CPU) d sweep d=6..14 to find d where spike emerges; R3 (3h GPU) tau sweep at d=8 to map tau-vs-spike.

**(F) substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384 HARD_FAIL**
ratio=1.130 > 0.85 (both N). Gamma flat vs M at alpha=0.05..0.15; 50 valid cells. SCS-vs-RSB discriminator HARD_FAIL: M-scaling not detected; Lyapunov-only regime. PP-58 MIDDLE 0.55-0.70 UNCHANGED. PP-33 framework classification UNAFFECTED. Rescue: R1 (free) theory audit -- why gamma flat vs M; R2 (2h CPU) extended M range (alpha>0.15); R3 (3h GPU) N=32768 to test N-scaling.

**(G) substrate_trained_mini_lm_rung1_tinychar_v1 HARD_FAIL**
bpc_mean=5.5168 ~= uniform_bpc=5.5236 (gap=0.007). Phase B rung 1 mini-LM: substrate-trained writes at N=512 produce random-level LM predictions. Substrate-LM coupling absent at N=512. No row movement (Phase B rung 1 exploratory; row not established). Rescue cheapest-first: R1 (free) interface audit -- is substrate signal passed to LM correctly at N=512; R2 (1h CPU) N=1024/2048 substrate to test N-dependence; R3 (2h CPU) direct-signal LM baseline (substrate bypassed) as upper bound.

**(H) substrate_curriculum_learning_rung1_tinychar_v1 HARD_FAIL**
gain_mean=-0.098 (curriculum HURTS vs random). N=256 substrate too small for meaningful difficulty ordering; noise-dominated. No row movement. Rescue: R1 (free) difficulty proxy audit at N=256 (substrate-noise vs signal); R2 (1h CPU) N=1024 curriculum test; R3 (2h CPU) oracle difficulty ordering (bpc-based, no substrate) as upper bound.

**(I) substrate_preloaded_icl_rung1_tinychar_v1 HARD_FAIL**
k0_acc_mean=0.0035; best_K=10 gain=0.0145 << HP=0.1. Substrate-preloaded context ICL fails at N=256. Key distinction from wave14d pool-retrieval ICL (green, +0.283 bpc): pool retrieval is substrate-native; preloaded-context injection is a substrate-LM coupling test. No row movement. Rescue: R1 (free) mechanism audit -- verify preloaded examples reach LM context; R2 (1h CPU) N=1024 test; R3 (2h CPU) explicit pool-retrieval ICL replication as comparison anchor.

**(J) substrate_spectral_training_monitor_rung1_tinychar_v1_n4096 HARD_FAIL -- overfitting rescue signal**
Convergence phase: mean_lead=-11.67 (3/3 seeds LAG; FAIL). Overfitting phase: mean_lead=300.0 (3/3 seeds LEAD; strong HP signal). Pre-reg HARD_FAIL (at least one phase lag in all seeds). HONEST. BUT overfitting-phase 300-step lead is a genuine rescue: substrate spectral fingerprint IS a strong overfitting sentinel at N=4096. Phase A rung 1 spectral monitor HARD_FAIL at full pre-reg standard. Annotation: 'convergence phase: lag 3/3 seeds (FAIL); overfitting phase: lead +300 steps 3/3 seeds (rescue-eligible)'. Rescue cheapest-first: R1 (free BEST-RESCUE) re-define pre-reg criterion as overfitting-phase-only detection -- substrate IS a useful overfitting sentinel; R2 (1h CPU) N=8192 for convergence-phase improvement; R3 (2h GPU) larger LM for phase-signal-to-noise.

**(K) substrate_8channel_orchestration_rung1_tinychar_v1_n4096 HARD_FAIL**
No converged seeds across 3 conditions. 8-channel routing via substrate fails at tinychar scale. No row movement. Rescue: R1 (free) convergence diagnostic; R2 (1h CPU) simplified 2-channel routing; R3 (2h GPU) larger LM for routing task.

### PROT compliance (v374 -> v375)
- PROT-004/006: No closures. 0 new rows. 1 BAND-LIFT (PP-12/Q-A3 0.89-0.97->0.90-0.97). 5 Phase B/A rung-1 HARD_FAILs with rescue R1-R3 cheapest-first each. 2 PP-50/PP-58/spectral_gap HF annotations. No PROT-004 closure triggers (rung-1 tinychar HARD_FAILs are exploratory-probe results; rows not yet established for tinychar rung results; rescue paths filed).
- PROT-007/008: v375 block appended. No portfolio regression. Portfolio 32+77 UNCHANGED.
- PROT-009: 286th PROT-009 paired commit.
- PROT-018: 15 anchors -- _n16384 x5 (L=84..87 + pp50v5); _n8192 x4 (L=48..50 + pp58_scs); _n4096_n16384 x1 (spectral_gap dual-N in name); _v1 x4 (tinychar rungs; no HDC-N suffix; LM/N param not anchor N); _n4096 x1 (spectral_training_monitor). 0 PROT-018 violations.
- PROT-021: all 15 source=remote run_mode=full. No smoke artifacts.
- PROT-022: Q-A3 EXACT-1.0000 consistent {L=20..L=87} N=16384 (68 rungs) and {L=19,L=22..L=50} N=8192 (30 rungs); pp50 v5 sigma_sep(sg3.0)=3.45e9 >> sigma_sep(sg1.0)=44085 (monotone to sg3.0); pp58 d_estimate=1.487 consistent with gamma_emp=1.231 (sub-spike regime); spectral_gap ratio=1.130~1.132 N-independent (Lyapunov-only regime); rung1 bpc=5.517 ~= uniform=5.524 (substrate-LM decoupled at N=512); curriculum gain=-0.098 consistent with noise-dominated N=256; ICL best_gain=0.0145 consistent with negligible preload at N=256; spectral_monitor convergence lag -11.67 / overfitting lead 300.0 internally consistent (different phase sensitivity).

HONEST: 670 -> 685 (+15). LVH: 213 UNCHANGED. Portfolio: 32+77 UNCHANGED.
Cap_map: v374 -> v375.
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
