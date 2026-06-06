# strategy_decisions_2026-06-06

## v442 -> v443 CYCLE 121 BATCH (2026-06-06)

Verdicts processed: substrate_kf1_ngram_augmented_v1 (HARD_FAIL) + substrate_kf1_hallucination_order_sensitive_encoder_v1 (MIDDLE_BAND)

### Step 0 honest re-read
- kf1_ngram_augmented_v1: HONEST. ADV mean=0.181 (range 0.171-0.197); ALL 3 seeds below 0.65 threshold; n-gram DEGRADES vs MiniLM baseline 0.217. HARD_FAIL label correct. No LVH.
- kf1_order_sensitive_encoder_v1: HONEST. ADV mean=0.746 (range 0.733-0.768); ALL 3 seeds within [0.70, 0.85] MIDDLE_BAND. MIDDLE_BAND label correct. No LVH.
HONEST: 956 -> 958 (+2). LVH: 225 UNCHANGED.

### Cap_map decisions
- kf1_ngram_augmented_v1: KF-1 row sub-property annotation. n-gram augmentation HARD_FAIL -- ADV=0.181 actually WORSE than MiniLM-only baseline (0.217). n-gram features do not encode order. Rescue axis R1 (n-gram) CLOSED. auc_easy=0.832 auc_hard=0.992 unaffected. KF-1 band 72-87% UNCHANGED.
- kf1_order_sensitive_encoder_v1: KF-1 + PP-8 sub-property annotation. Pythia-160m encoder lifts ADV 0.217->0.746 (+52.9pp). MIDDLE_BAND (0.70-0.85); HP requires >=0.85. Largest ADV rescue to date. KF-1 band 72-87% UNCHANGED. Active rescue: R3 Pythia-scale-up, R4 positional-embed, R5 adversarial-training.

### Rescue sketches V1 n-gram HARD_FAIL (cheapest-first per PROT-004/006)
R1-CLOSED: n-gram augmentation definitively closed (ADV degraded).
R2 (0-compute, SUBSUMPTION): V2 Pythia path already active and stronger.
R3 (CHEAP, CPU <30min): Pythia-410m/1B scale-up encoder sweep.
R4 (CHEAP, CPU <30min): Sinusoidal/rotary positional embedding augmentation.
R5 (MEDIUM, GPU <2h): Adversarial training on shuffled-fact pairs.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v442 -> v443)
- PROT-004/006: No closures. R1 closed; R3/R4/R5 filed cheapest-first.
- PROT-007: v443 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 355th PROT-009 paired commit.
- PROT-018: No _nN suffixes. CLEAN.
- PROT-021: both source=remote run_mode=full. No smoke artifacts.
- PROT-022: V1 tight-spread deterministic (n-gram fixed); V2 normal 3-seed variance. No HP-fragility.

Cap_map: v442 -> v443 CYCLE 121 (1 HF: kf1_ngram_augmented NGRAM-DEGRADES-ADV-0.181-WORSE-THAN-BASELINE; 1 MID: kf1_order_sensitive_encoder PYTHIA-ADV-0.746-MIDDLE-BAND-PARTIAL-RESCUE; 0 HP; 0 LVH; KF-1 band 72-87% UNCHANGED; R1 closed, R3/R4/R5 filed; HONEST 956->958; LVH 225; Portfolio 32+77; 355th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v443 -> v444 CYCLE 122 BATCH (2026-06-06)

Verdicts processed: substrate_embedding_norm_gate_discriminability_v1 (HARD_FAIL) + substrate_kf1_truthfulqa_style_v1 (HARD_FAIL) + substrate_etf_minilm_n_sub_lower_sweep_v1 (MIDDLE_BAND)

### Step 0 honest re-read

- substrate_embedding_norm_gate_discriminability_v1: HONEST. 3-seed full run. by_vc={'vc256':0.505, 'vc1024':0.4332, 'vc4096':0.4563}; kept_frac=0.30; min_coverage=0.4332. All 3 vc cells well below 0.90 threshold. HARD_FAIL label correct. No LVH.
- substrate_kf1_truthfulqa_style_v1: HONEST. Smoke n_seeds=1. auc_hard=0.975 (non-adversarial, exceptional), auc_negation=0.034 (negation/contradiction sub-axis). Failure is mechanistic: MiniLM encoder has no word-order/negation awareness; this is an encoder architectural limit, not statistical noise. Full run will not change outcome. HARD_FAIL label correct. No LVH. NOTE: smoke only.
- substrate_etf_minilm_n_sub_lower_sweep_v1: HONEST with nuance. Smoke n_seeds=1. D384: lift=1.21x (raw_rec=0.82->wht_rec=1.00). D512: lift=1.01x (raw_rec=0.99->wht_rec=1.00). MIDDLE_BAND classification is honest. NUANCE: D512 lift is trivially flat because raw_recall=0.99 is at ceiling pre-whitening; this is NOT evidence that whitening is ineffective at D512. Genuine whitening signal lives at D384 where raw_recall=0.82. verdict_msg 'roughly flat' over-simplifies but MIDDLE_BAND label is not an overclaim. No LVH; nuance noted.
HONEST: 958 -> 961 (+3). LVH: 225 UNCHANGED.

### Cap_map decisions
- substrate_embedding_norm_gate_discriminability_v1: PP-8 sub-property annotation. Norm-gate as discriminability filter for embedding-level routing HARD_FAIL at top-30% gate. Coverage=0.43-0.51 across all 3 vc sizes vs 0.90 threshold. Norm magnitude is not a reliable proxy for concept-level coverage. 3-seed full confirmed. KF-1/PP-8 UNCHANGED.
- substrate_kf1_truthfulqa_style_v1: KF-1 sub-property annotation (negation sub-axis). MiniLM blind to negations/contradictions (AUC_negation=0.034, near-chance). AUC_hard=0.975 on non-adversarial confirms the detector works -- negation is purely the encoder architectural gap. Corroborates v443 MiniLM order-insensitivity finding. Active rescue: v443 R3 (order-sensitive encoder). KF-1 band 72-87% UNCHANGED.
- substrate_etf_minilm_n_sub_lower_sweep_v1: PP-8 sub-property annotation (ETF MiniLM N_sub sweep). Whitening lift is N_sub-dependent: D384 1.21x genuine (raw_recall=0.82), D512 1.01x ceiling-saturated (raw_recall=0.99). Cross-N attenuation pattern from v441/v442 continues into lower range with ceiling caveat. MIDDLE_BAND. Active rescue: full 3-seed run at D384. ETF/whitening row UNCHANGED.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**A: substrate_embedding_norm_gate_discriminability_v1 HARD_FAIL**
R1 (0-compute, SUBSUMPTION): Higher kept_frac threshold (50-70% vs 30%); may recover coverage at cost of selectivity. Config change only.
R2 (CHEAP, CPU <30min): Inter-concept cosine variance gate instead of norm; algebraically more principled for HD memory discriminability.
R3 (CHEAP, CPU <30min): Per vc-class norm gating; vc256 already shows 0.505 vs 0.433 at vc1024; per-class thresholding may rescue.
R4 (MEDIUM, CPU <2h): Learned discriminability score from W activations replacing hand-crafted norm gate.

**B: substrate_kf1_truthfulqa_style_v1 HARD_FAIL**
R1 (0-compute, SUBSUMPTION): v443 R3 (Pythia-scale-up) already covers active rescue path. No additional rescue needed; v443 R3/R4/R5 stand.

**C: substrate_etf_minilm_n_sub_lower_sweep_v1 MIDDLE_BAND**
R1 (CHEAP, CPU <30min): Full 3-seed run at D384 to confirm 1.21x lift real (smoke n=1 only).
R2 (CHEAP, CPU <30min): D256 and D320 sweep to characterize lift curve at lower N_sub.
R3 (MEDIUM, CPU <2h): M-sweep at D384 to characterize lift vs M/N_sub ratio.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v443 -> v444)
- PROT-004/006: No closures. A: 4 rescues cheapest-first. B: subsumed by v443 R3. C: 3 rescues cheapest-first.
- PROT-007: v444 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes; 0 LVH. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 356th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of the 3 anchors. CLEAN.
- PROT-021: A source=remote run_mode=full; B source=remote run_mode=smoke; C source=remote run_mode=smoke. B,C smoke flagged -- B mechanistic failure robust; C lift confirmed single-seed only.
- PROT-022: A 3-seed full tight-spread; B smoke n=1; C smoke n=1. No HP-fragility concern.

Cap_map: v443 -> v444 CYCLE 122 (2 HF: embedding_norm_gate_COVERAGE-0.43-AT-0.90-THRESHOLD + kf1_truthfulqa_NEGATION-AUC-0.034-ENCODER-LIMIT; 1 MID: etf_minilm_n_sub_lower-D384-LIFT-1.21x-D512-CEILING-SATURATED; 0 HP; 0 LVH; KF-1 72-87% UNCHANGED; PP-8 UNCHANGED; HONEST 958->961; LVH 225; Portfolio 32+77; 356th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v444 -> v445 CYCLE 123 BATCH (2026-06-06)

Verdicts processed: 10-verdict batch (3 QUEUE-CONFIRMED + 7 ORPHANS)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_native_reasoning_k_hop_n16384_K10_v1 HARD_PASS -- LABEL HONEST**
3-seed full N=16384. ALL K={1,2,3,5,7,10}=1.000 unanimous 3/3 seeds. HP threshold >=0.70 at K=3: CLEARED by ALL cells (1.000). Test ceiling K=10 (prior v440 was K=6 at N=4096). Ceiling NOT found at K=10 N=16384. HONEST. +1 HONEST.

**(2) substrate_sparse_vs_dense_alpha_sweep_v1 HARD_PASS -- LABEL HONEST**
3-seed full. N4096: sparse_cap/dense_cap=819/163=5.02x (3/3 seeds). N16384: 3276/491=6.67x (seeds 7,17), 3276/655=5.00x (seed 23). Minimum ratio 5.0x >3x threshold. HONEST. +1 HONEST.

**(3) substrate_kgram_xor_k4_sweep_v1 MIDDLE_BAND -- LABEL HONEST**
3-seed full. 9 cells: k={3,4} x N=16384 x vc={1000,100000}. sub_acc=1.000 all cells; trigram=1.000 vc=100000 all cells; fourgram=1.000 all cells; k=4 vc=1000 bigram=0.90-0.97 (seed-variant, Vc-dependent). Verdict_msg: decisive k3/N4096 cell absent from grid. Grid covers N=16384 only. MIDDLE_BAND honest. HONEST. +1 HONEST.

**(4) substrate_extraction_sqrt_K_allocation_v1 HARD_FAIL -- LABEL HONEST**
Smoke n=1. sp10: sqrt_K=1.0 == uniform (TIE). sp100: sqrt_K=0.889 < uniform=1.0 (WORSE). sp1000: sqrt_K=0.556. sqrt-K does not beat uniform at any level. HONEST. NOTE: smoke n=1. +1 HONEST.

**(5) substrate_etf_dim_expansion_mpnet_768_v1 MIDDLE_BAND -- LABEL HONEST**
Smoke n=1. D768: raw=460 wht=1152 ratio=2.50x. D1536: raw=2304 wht=2304 ratio=1.00x (raw at ceiling). 2.50x < 3x HP threshold. MIDDLE_BAND honest. NOTE: smoke n=1. +1 HONEST.

**(6) substrate_hadamard_plus_whitening_combined_v1 HARD_FAIL -- LABEL HONEST**
Smoke n=1. expand_only=4000, expand_plus_whiten=4000, combined/best_single=1.00x. No additive benefit from combining. HONEST. NOTE: smoke n=1. +1 HONEST.

**(7) substrate_dim_expansion_cross_encoder_pythia_llama_v1 HARD_PASS -- LABEL HONEST (smoke flag)**
Smoke n=1. D384 wht=230, D1024 wht=1536, expansion ratio=6.68x >=3x threshold. raw_cap=0 expected for LM embeddings (correlated prior to whitening). Whitened expansion is the claim and it holds. HONEST. NOTE: smoke n=1; 3-seed full confirmation pending. +1 HONEST.

**(8) substrate_kf1_contradiction_detection_order_sensitive_v1 HARD_FAIL -- LABEL HONEST**
Smoke n=1. auc_easy=0.937, auc_hard=0.893, NEGATION=0.111 (near-chance). Primary metric fails <0.70. Order-sensitive encoder lifts NEGATION only 0.034->0.111 (+7.7pp, still near-chance). Mechanistic: negation detection requires more than order-sensitivity -- needs explicit negation awareness. HONEST. NOTE: smoke n=1. +1 HONEST.

**(9) substrate_concept_uniform_random_extraction_v1 HARD_FAIL -- LABEL HONEST**
Smoke n=1. sp10=0.597, sp100=0.156, sp1000=0.021 coverage; all <0.90 threshold. HONEST. NOTE: smoke n=1. +1 HONEST.

**(10) substrate_per_cluster_stratified_extraction_v1 MIDDLE_BAND -- LVH #226**
Smoke n=1. verdict_msg: 'MIDDLE_BAND: >=0.95 coverage at 10-100x speedup'. Per-cell: sp10 actual_speedup=20.6x, sp100 actual_speedup=20.6x, sp1000 actual_speedup=20.6x. ACTUAL SPEEDUP SATURATES AT ~20x for ALL three requested levels. sp100=100x and sp1000=1000x targets NOT achieved. Coverage=1.0 is real at achieved speedup of ~20x. Label over-claims by implying 100x speedup achieved -- only 20x achieved.
LVH #226: MIDDLE_BAND-speedup-saturates-at-20x-not-100x. Label: (a) 'coverage at 10-100x speedup'; (b) honest: coverage at ~20x speedup only; (c) cells contradicting: sp100/sp1000 actual_speedup=20.6x not 100x/1000x.
Honest reading for downstream: MIDDLE_BAND retained (coverage genuine); speedup range corrected to ~20x.

HONEST: 961 -> 970 (+9). LVH: 225 -> 226 (+1: per_cluster_stratified_extraction speedup saturation).

### Cap_map decisions

**(1) substrate_native_reasoning_k_hop_n16384_K10_v1 HARD_PASS**
PP-11 reasoning-store + multi-hop combined row. BAND-LIFT: v440 K=6 N=4096 HARD_PASS + this K=10 N=16384 HARD_PASS = two consecutive K-hop extensions, monotone K and N scale-up. PP-11 0.40-0.55 -> 0.55-0.70 +15%/+15% CONSERVATIVE. PROT-008 validator: two independent K-hop HPs at increasing K and N; monotone confirmed. PASS. Annotation: K=10 N=16384 no-ceiling confirmed; ceiling K>10 untested; K={12,15} sweep recommended as next step.

**(2) substrate_sparse_vs_dense_alpha_sweep_v1 HARD_PASS**
Capacity/scaling sub-property annotation. sparse pattern coding (alpha=0.20) gives 5.0-6.7x capacity vs dense at N={4096,16384} 3-seed full. Corroborates sparse coding direction. Annotation on capacity row: sparse PATTERN alpha=0.20 gives 5x+ capacity; PP-8 / ETF dim-expansion context -- sparsity-coding is a complementary rescue path to whitening+expansion. Band UNCHANGED (annotation only).

**(3) substrate_kgram_xor_k4_sweep_v1 MIDDLE_BAND**
PP-8 k-gram LM sub-axis sub-property annotation. k=4 N=16384 vc=100000: sub_acc=1.000 trigram-class confirmed (extends v432 k=3 N=4096 to k=4 N=16384). Missing decisive cell: k=3 N=4096 prevents HP. Band UNCHANGED. Annotation: k=4 ceiling at N=16384 confirmed; N=4096 cell required for band-lift.

**(4) substrate_extraction_sqrt_K_allocation_v1 HARD_FAIL**
Extraction sub-axis annotation. sqrt-K WORSE than uniform at sp100. Rescue (cheapest-first, PROT-004/006):
R1 (0-compute, SUBSUMPTION): Per-cluster stratified (anchor 10) beats uniform; sqrt-K failure subsumed by positive structured-extraction result.
R2 (CHEAP, CPU <30min): Proportional-to-cluster-size allocation (linear K not sqrt-K).
R3 (CHEAP, CPU <30min): Top-K density-weighted budget allocation.

**(5) substrate_etf_dim_expansion_mpnet_768_v1 MIDDLE_BAND**
PP-8 ETF dim-expansion sub-axis. MPNet-768: D768 wht=2.50x. Cross-encoder pattern holds (MiniLM, Pythia, MPNet all benefit from dim-expansion). 2.50x below 3x HP. Rescue R1: full 3-seed at D768. R2: D-sweep below 768. Band UNCHANGED.

**(6) substrate_hadamard_plus_whitening_combined_v1 HARD_FAIL**
PP-8 Phase 4B combination gate. combined=expand_only (no additive benefit). Closes combination rescue path. Rescue (cheapest-first):
R1 (0-compute, SUBSUMPTION): dim-expansion alone (4000) is the correct path; engineering effort concentrates on confirming expand-only 3-seed.
R2 (CHEAP, CPU <30min): Hadamard-first then expand (ordering swap -- may break symmetry).
R3 (CHEAP, CPU <30min): Hadamard-only at N=16384 to isolate Hadamard signal without expansion masking.

**(7) substrate_dim_expansion_cross_encoder_pythia_llama_v1 HARD_PASS (smoke)**
PP-8 encoder-generalization sub-property annotation. expand-then-orthogonalize rule encoder-family-agnostic: MiniLM + Pythia confirmed. 6.68x at D1024/D384. Smoke n=1; 3-seed full confirmation needed before band-lift. Annotation only.

**(8) substrate_kf1_contradiction_detection_order_sensitive_v1 HARD_FAIL**
KF-1 adversarial negation sub-axis annotation. Order-sensitive encoder: NEGATION 0.034->0.111 (+7.7pp, still near-chance). Negation detection is deeper than order-sensitivity. v443 R3/R4/R5 (Pythia scale-up + positional embed + adversarial training) remain active -- this result adds that negation specifically may require adversarial training (R5) or negation-aware fine-tuning beyond scale. KF-1 band 72-87% UNCHANGED.

**(9) substrate_concept_uniform_random_extraction_v1 HARD_FAIL**
Extraction baseline annotation. Random sampling rejects 0.90 coverage at all speedup levels. Confirms per-cluster structured extraction (anchor 10) is necessary. Combined with anchor 10, pair validates extraction design direction. Band UNCHANGED.

**(10) substrate_per_cluster_stratified_extraction_v1 MIDDLE_BAND [LVH #226 honest: speedup=20x not 100x]**
Extraction sub-axis annotation. coverage=1.0 real at actual_speedup=~20x. Speedup ceiling at ~20x is a structural limit of the cluster count/size in the test (n_tok=5000). MIDDLE_BAND honest at actual_speedup=20x. Rescue (cheapest-first):
R1 (0-compute, SUBSUMPTION): Verify what limits speedup to 20x -- if cluster count is fixed, increasing n_tok or reducing cluster granularity may push speedup higher.
R2 (CHEAP, CPU <30min): Sweep cluster_count to characterize speedup vs coverage tradeoff.
R3 (CHEAP, CPU <30min): Larger n_tok (50K, 100K) to see if speedup ceiling rises with corpus size.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 1 BAND-LIFT (PP-11 0.40-0.55->0.55-0.70). 0 closures.

### PROT compliance (v444 -> v445)
- PROT-004/006: No closures. Rescues filed cheapest-first for anchors 4, 6, 10.
- PROT-007: v445 history row appended to substrate_capability_map_history.md.
- PROT-008: PP-11 band-lift: v440 K=6 N=4096 HP + this K=10 N=16384 HP = two consecutive monotone extensions. Validator PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 357th PROT-009 paired commit.
- PROT-018: All 10 anchors lack _nN binding suffix. CLEAN.
- PROT-021: Anchors 1-3 source=remote run_mode=full multi-seed. Anchors 4-10 source=remote run_mode=smoke n=1. Smoke mechanistic HFs (4,6,8,9) robust; smoke HP (7) flagged for 3-seed confirmation.
- PROT-022: Anchors 1-3 3-seed full consistent. Smoke anchors n=1 -- no HP-fragility assessment possible.

Cap_map: v444 -> v445 CYCLE 123 (3 HP: k_hop_n16384_K10-CEILING-NOT-FOUND-K10-N16384-3SEED + sparse_vs_dense_alpha-5.0-6.7x-CAPACITY-3SEED + dim_expansion_pythia-6.68x-ENCODER-AGNOSTIC-SMOKE; 4 HF: sqrt_K_allocation-SMOKE-WORSE-UNIFORM + hadamard_whitening_combined-NO-ADDITIVE-1.00x-SMOKE + kf1_contradiction_order_sensitive-NEGATION-0.111-NEAR-CHANCE-SMOKE + uniform_random_extraction-COVERAGE-0.60-SMOKE; 3 MID: kgram_xor_k4-N16384-CEILING-N4096-MISSING + etf_dim_mpnet768-2.50x-BELOW-HP-SMOKE + per_cluster_stratified-COVERAGE-1.00-SPEEDUP-20x-LVH226; 1 LVH #226: per_cluster_stratified speedup-saturates-20x-not-100x; PP-11 BAND-LIFT 0.40-0.55->0.55-0.70 K-hop-K10-N16384-monotone-extension; HONEST 961->970; LVH 225->226; Portfolio 32+77; 357th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v445 -> v446 CYCLE 124 (2026-06-06)

Verdict processed: substrate_dim_expansion_plus_sparse_pattern_compound_v1 (HARD_FAIL)

### Step 0 honest re-read (MANDATORY)

- substrate_dim_expansion_plus_sparse_pattern_compound_v1: HONEST. Smoke n=1. arms={'a_baseline':2304, 'b_expand_keys':3072, 'c_sparse_values':2304, 'd_compound':3072}. gain_b=1.33x gain_c=1.00x gain_d=1.33x expected_stacking(b*c)=1.33x d/expected=1.00. Compound arm d equals max(b,c) not b*c. sparse_values arm (c) gave zero gain at M=50 -- c is a null lever at this M. Compound collapses to single-lever ceiling (dim-expansion only). HARD_FAIL label correct. No LVH.
HONEST: 970 -> 971 (+1). LVH: 226 UNCHANGED.

### Cap_map decisions

**substrate_dim_expansion_plus_sparse_pattern_compound_v1 HARD_FAIL**
PP-8 ETF dim-expansion + sparse-pattern stacking sub-axis. HARD_FAIL smoke n=1.
Key finding: sparse-pattern codes (c arm) produce ZERO gain at M=50 (gain_c=1.00x = baseline). This means the compound HARD_FAIL is a null-c artifact: stacking dim-expansion + a null lever cannot beat dim-expansion alone. This is NOT a stacking impossibility result -- it is a sparse-pattern-at-M=50 null result. The rescue axis question from cycle 123 (can these two levers stack?) is UNANSWERED because one lever failed to activate.
Annotation on PP-8 stacking sub-axis: stacking HF at M=50 due to sparse-pattern null (c=1.00x). Stacking question deferred pending sparse-pattern-at-higher-M confirmation.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

R1 (0-compute, SUBSUMPTION): Stacking question trivially reduces to: first confirm sparse-pattern arm is non-null. If c>1.00x exists at higher M, retest compound there. Config change only.
R2 (CHEAP, CPU <30min): M sweep for sparse-pattern arm alone (M={100,200,500,1000}) to find activation threshold where gain_c>1.00x.
R3 (CHEAP, CPU <30min): Compound test at M=200+ once sparse-pattern non-null M is identified. Direct stacking answer.
R4 (CHEAP, CPU <30min): Alpha-sweep on sparse-pattern coding (try denser/sparser codes) to see if M=50 null is alpha-specific.
R5 (MEDIUM, CPU <2h): Cross-encoder sweep of compound at identified activation M across MiniLM, MPNet, Pythia to characterize encoder-dependence of stacking.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v445 -> v446)
- PROT-004/006: No closures. R1-R5 filed cheapest-first.
- PROT-007: v446 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 358th PROT-009 paired commit.
- PROT-018: No _nN suffix on anchor. CLEAN.
- PROT-021: source=remote run_mode=smoke n=1. Smoke HF with mechanistic interpretation (c null at M=50); stacking question deferred not closed.
- PROT-022: Smoke n=1; no HP-fragility assessment. Single-lever ceiling is deterministic (arms measured directly).

Cap_map: v445 -> v446 CYCLE 124 (1 HF: dim_expansion_plus_sparse_pattern_compound-SMOKE-C-NULL-M50-STACKING-DEFERRED; 0 HP; 0 MID; 0 LVH; PP-8 stacking sub-axis deferred-null-c; HONEST 970->971; LVH 226 UNCHANGED; Portfolio 32+77; 358th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v446 -> v447 CYCLE 125 BATCH (2026-06-06)

Verdicts processed: substrate_sparse_pattern_M_activation_sweep_v1 (HARD_FAIL) + substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1 (HARD_FAIL [LVH #227])

### Step 0 honest re-read (MANDATORY)

**(1) substrate_sparse_pattern_M_activation_sweep_v1 HARD_FAIL -- LABEL HONEST**
Smoke n=1. source=remote. M sweep {50,200,800,2000}: all delta_pp=0.0 (M800 delta=-0.125pp, slightly worse). sparse-value lever uniformly null across all tested M. HARD_FAIL label accurate: no activation threshold found. Context: this IS the cycle-124 R2 rescue (M-sweep to find activation M for sparse-pattern arm). R2 definitively answered: no activation M exists in {50..2000}. R1 subsumption (stacking deferred pending sparse-pattern non-null M) must be revised: sparse-pattern is permanently null, not deferred. Stacking rescue path CLOSED. NOTE: smoke n=1 but mechanistic null is robust (all 4 M-cells zero lift; consistent with v446 compound c-null finding).
HONEST. +1 HONEST (971->972). No LVH.

**(2) substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1 HARD_FAIL -- LVH #227**
Smoke n=1. source=remote. N={512,1024}: real_recall=1.0 synth_recall=1.0 ratio=1.0 both N-cells. slope/log2N=0.000.
LABEL OVER-CLAIMS. verdict_msg 'real tracks synthetic; no attenuation in this range' implies the disambiguation question (cycles 119/122: is cross-N attenuation structural or artifact?) was answered negatively. But BOTH real and synthetic recall are at ceiling (1.0) at N={512,1024} -- well below M_c. Ratio=1.0 is a ceiling artifact, not evidence of true equivalence. The smoke does NOT test N near M_c where the original attenuation was observed. The question is UNANSWERED at this N range.
LVH #227: (a) label: HARD_FAIL with msg 'real tracks synthetic'; (b) honest: INCONCLUSIVE -- both at recall ceiling at sub-capacity N; ratio=1.0 is ceiling artifact not disambiguation evidence; (c) contradicting cells: N512 real=1.0 synth=1.0, N1024 real=1.0 synth=1.0 -- indistinguishable when denominator is trivially 1.0.
Honest verdict for downstream: UNKNOWN/INCONCLUSIVE. Needs N sweep through M_c to be informative.
LVH #227. +1 HONEST (972->973). LVH 226->227 (+1).

HONEST: 971 -> 973 (+2). LVH: 226 -> 227 (+1).

### Cap_map decisions

**(1) substrate_sparse_pattern_M_activation_sweep_v1 HARD_FAIL**
PP-8 sparse-pattern coding sub-axis annotation (extension of v446 compound HARD_FAIL).
Key finding: sparse-VALUE lever null at ALL M in {50,200,800,2000}. This CLOSES the cycle-124 R2 rescue path (find activation M): no activation M exists. The compound stacking question (cycle-124 R1/R3) collapses entirely -- sparse-VALUE encoding as a capacity-extension lever CLOSED at this probe level. DOES NOT close sparse-KEY encoding (cycle-123 sparse_vs_dense_alpha_sweep HARD_PASS at 5x+ capacity was sparse-KEY not sparse-VALUE). Annotation distinguishes sparse-KEY (alpha sweep, HARD_PASS, active) vs sparse-VALUE (this anchor, HARD_FAIL, closed). PP-8 band UNCHANGED. Portfolio 32+77 UNCHANGED.

Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, SUBSUMPTION): cycle-124 compound stacking (R1/R3) path closes by dependency. sparse-KEY (alpha=0.20) 5x+ capacity finding (cycle 123) UNAFFECTED and remains active sparse-coding direction.
R2 (0-compute, ANNOTATION): Clarify sparse-KEY vs sparse-VALUE distinction in PP-8 annotation to prevent re-exploration of sparse-VALUE under different guises.
R3 (CHEAP, CPU <30min): Alpha-sweep on sparse-VALUE encoding to verify null is not alpha-specific. Only if theoretical motivation surfaces -- 4-cell consistent null + compound corroboration is sufficient for probe-level closure.

**(2) substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1 [LVH #227 honest: INCONCLUSIVE]**
Cross-N attenuation disambiguation sub-axis (PP-8 / KF-1 encoder attenuation context).
Honest verdict: INCONCLUSIVE at sub-capacity N. Disambiguation question from cycles 119/122 remains OPEN. N={512,1024} far below M_c; ceiling recall on both real and synthetic makes ratio=1.0 uninformative. Genuine test requires N sweep from sub-capacity through M_c.
Cap_map annotation: real_vs_synthetic_N_sweep disambiguation probe INCONCLUSIVE (ceiling artifact at sub-capacity N). Original cycle-119/122 attenuation observation stands as prior. Cross-N attenuation status: OPEN. PP-8 / KF-1 encoder attenuation UNCHANGED.

Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, SUBSUMPTION): Reframe as UNKNOWN not closed; cycle-119/122 attenuation finding is the load-bearing observation; this smoke neither confirms nor refutes it.
R2 (CHEAP, CPU <30min): N-sweep at M near M_c (N={4096,8192,16384} at M=M_c-adjacent) comparing real-encoder vs synthetic-baseline recall -- only capacity-relevant N disambiguates.
R3 (CHEAP, CPU <30min): Decouple -- first confirm M_c for real encoder alone, then compare cross-N ratio at M=M_c.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures (sparse-VALUE sub-probe closed at probe level; no cap_map row closure; real_vs_synthetic disambiguation OPEN).

### PROT compliance (v446 -> v447)
- PROT-004/006: No row closures. sparse-VALUE: 3 rescue sketches cheapest-first. real_vs_synthetic: LVH #227 filed; 3 rescue sketches cheapest-first; status INCONCLUSIVE not closed.
- PROT-007: v447 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 359th PROT-009 paired commit.
- PROT-018: No _nN suffixes on either anchor. CLEAN.
- PROT-021: both source=remote run_mode=smoke n=1. sparse-VALUE: mechanistic null robust (4-cell consistent + compound corroboration). real_vs_synthetic: ceiling artifact flagged as INCONCLUSIVE; LVH #227 filed.
- PROT-022: Smoke n=1 both; no HP-fragility assessment possible. Null result (sparse-VALUE) deterministic; ceiling result (real_vs_synthetic) vacuous.

Cap_map: v446 -> v447 CYCLE 125 (1 HF: sparse_pattern_M_activation-SMOKE-LEVER-NULL-ALL-M-SPARSE-VALUE-CLOSED-sparse-KEY-UNAFFECTED; 1 HF-LVH #227: real_vs_synthetic_N_sweep-SMOKE-INCONCLUSIVE-CEILING-ARTIFACT-NOT-DISAMBIGUATION; 0 HP; 0 MID; LVH 226->227; PP-8 sparse-VALUE sub-probe closed; cross-N disambiguation OPEN; HONEST 971->973; Portfolio 32+77; 359th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
