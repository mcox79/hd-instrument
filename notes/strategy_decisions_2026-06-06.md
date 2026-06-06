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

## v447 -> v448 CYCLE 126 BATCH (2026-06-06)

Verdicts processed (re-runs / smoke->full promotions):
1. substrate_etf_hadamard_phase4a_infra_eval_v1 (HARD_PASS label -- re-pointed Hopfield metric, 3-seed full)
2. substrate_kf1_contradiction_detection_order_sensitive_v1 (HARD_FAIL -- 3-seed full promotion from cycle 123 smoke)
3. substrate_kf1_truthfulqa_style_v1 (HARD_FAIL -- 3-seed full promotion from cycle 122 smoke)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_etf_hadamard_phase4a_infra_eval_v1 HARD_PASS -- [label-vs-honest] LVH #228**
source=remote run_mode=full n_seeds=3. Re-pointed to Hopfield exact-recovery on ZCA-whitened sign-binarized real keys (b2da096; fixes dim-reduction bug in prior whiten() + fixes unique-value artifact metric). Pre-reg HP band: whitened/raw >=2x.
Per-cell: seed7={raw=0, wht=0, ratio=0.0}, seed17={raw=0, wht=38, ratio=38.0}, seed23={raw=0, wht=38, ratio=38.0}.
LABEL OVER-CLAIMS. verdict_msg 'ratio=25.33x' is mean (0+38+38)/3=25.33 -- but seed7 achieves wht=0 (zero Hopfield capacity on this seed). 2/3 seeds clear HP threshold (38x >> 2x). 1/3 seed (seed7) fails completely: whitening produced ZERO recoverable patterns. This is not a ratio=low issue -- seed7 has no capacity, raw or whitened. HARD_PASS requires per-cell evidence across all 3 seeds; 1/3 seed=0 means this is at best MIDDLE_BAND (2/3 seeds HP, 1/3 HF).
LVH #228: (a) label: HARD_PASS 'ratio=25.33x'; (b) honest: MIDDLE_BAND -- 2/3 seeds whitened=38 (~0.10N, genuine lift >=2x HP); 1/3 seed (seed7) wht=0 (zero capacity, HP fail); seed7 likely a ZCA whitening collapse at this initialization; (c) contradicting cells: seed7 raw=0 wht=0 ratio=0.0 fails HP threshold entirely.
Honest verdict: MIDDLE_BAND (2/3 seeds pass HP at 38x; 1/3 seed fails at 0x; mechanism confirmed 2/3 but not unanimous).
Context: Prior cycle 119 2.75x was metric artifact (unique-value hetero metric); current Hopfield metric is correct. Current 38x on seeds 17+23 is the genuine whitening signal -- much stronger than 2.75x artifact. Seed7 collapse is likely a ZCA numerics issue at this seed's encoder sample.
LVH #228. +1 HONEST (973->974). LVH 227->228 (+1).

**(2) substrate_kf1_contradiction_detection_order_sensitive_v1 HARD_FAIL -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. 3-seed full promotion from cycle 123 smoke (n_seeds=1 NEGATION=0.111).
Per-seed: {seed7: easy=0.8017, hard=0.8925, neg=0.0785}, {seed17: easy=0.8023, hard=0.8873, neg=0.0799}, {seed23: easy=0.8081, hard=0.9056, neg=0.0905}.
Mean NEGATION=0.083 (range 0.078-0.090). HP threshold >=0.70. NEGATION=0.083 is well below threshold (gap: 0.617). HARD_FAIL label correct. NOTE: smoke n=1 had NEGATION=0.111; 3-seed full gives 0.083 (smoke over-estimated by 2.8pp -- within normal variance, not a pre-reg contradiction). NOT a byte-identical duplicate. New finding: NEGATION variance across seeds is tight (0.012pp spread) -- mechanistic consistency confirms architectural limit, not noise.
HONEST. +1 HONEST (974->975). No LVH.

**(3) substrate_kf1_truthfulqa_style_v1 HARD_FAIL -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. 3-seed full promotion from cycle 122 smoke (n_seeds=1 NEGATION=0.034).
Per-seed: {seed7: hard=0.9683, neg=0.0194}, {seed17: hard=0.9659, neg=0.0152}, {seed23: hard=0.9687, neg=0.0190}.
Mean NEGATION=0.018 (range 0.015-0.019). auc_hard mean=0.968 (3/3 seeds >= 0.90, excellent). HP threshold for NEGATION axis >=0.70; actual=0.018 (gap: 0.652). HARD_FAIL label correct. NOTE: smoke n=1 had NEGATION=0.034; 3-seed full gives 0.018 -- slightly lower, tight variance (0.004pp spread). Mechanistic: MiniLM has no negation/word-order sensitivity; 3-seed confirmation makes this architecturally definitive. NOT a byte-identical duplicate.
HONEST. +1 HONEST (975->976). No LVH.

HONEST: 973 -> 976 (+3). LVH: 227 -> 228 (+1: etf_hadamard_phase4a seed7-wht=0 fails HP).

### Cap_map decisions

**(1) substrate_etf_hadamard_phase4a_infra_eval_v1 [LVH #228 honest: MIDDLE_BAND]**
PP-8 sub-property annotation (Phase 4A re-pointed Hopfield metric).
Honest verdict: MIDDLE_BAND. 2/3 seeds: whitened Hopfield capacity=38 (~0.10N at N_sub=384) vs raw=0. Whitening is MANDATORY for real encoders (raw=0 is unusable without whitening). Genuine whitening signal confirmed on 2/3 seeds at 38x lift. 1/3 seed (seed7) ZCA collapse: wht=0 -- likely ZCA numerics failure at this seed PCA initialization. Not a stochastic noise issue (seeds 17+23 are identical at 38); seed7 is a degenerate initialization.
Context: Supersedes the prior 2.75x metric-artifact reading (cycle 119). The correct metric (Hopfield exact-recovery) shows a much stronger signal (38x on good seeds) but reveals seed-stability issue in ZCA whitening. Band UNCHANGED (MIDDLE_BAND; not unanimous HP). Phase 4B recommendation: ZCA-stability patch + 3-seed recheck.

Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Document seed7 ZCA collapse pattern; clarify whitening=38x is the genuine mechanism signal on non-degenerate seeds; capacity confirmed at ~0.10N.
R2 (CHEAP, CPU <30min): Patch ZCA whitening to handle low-rank edge cases (add rank-check + regularization floor); re-run seed7 to confirm 38x is achievable unanimously.
R3 (CHEAP, CPU <30min): N_sub sweep at {512, 1024, 2048} with patched ZCA to characterize how whitened Hopfield capacity scales with N_sub.
R4 (CHEAP, CPU <30min): Compare ZCA vs PCA vs random-projection whitening at N_sub=384 to identify most stable whitening strategy.

**(2) substrate_kf1_contradiction_detection_order_sensitive_v1 HARD_FAIL (3-seed full confirmation)**
KF-1 adversarial negation sub-axis annotation (3-seed full confirms cycle 123 smoke HF).
NEGATION mean=0.083 (range 0.078-0.090). Tight variance confirms mechanistic architectural limit, not noise. Order-sensitive encoding moves NEGATION from MiniLM-baseline 0.034 to 0.083 (+4.9pp) -- marginal improvement, far below 0.70 threshold. Gap is 0.617. Definitively closes the 'order-sensitivity as negation rescue' hypothesis for MiniLM. Active rescues v443 R3/R4/R5 (Pythia scale-up, positional embed, adversarial training) remain valid; this result specifically motivates R5 (adversarial training -- order alone insufficient). KF-1 band 72-87% UNCHANGED.

**(3) substrate_kf1_truthfulqa_style_v1 HARD_FAIL (3-seed full confirmation)**
KF-1 negation sub-axis annotation (3-seed full confirms cycle 122 smoke HF + cycle 123 annotation).
NEGATION mean=0.018 (3-seed tight spread 0.015-0.019). Architecturally definitive: MiniLM negation-insensitivity is not a single-seed artifact. auc_hard=0.968 (excellent non-adversarial detection) confirms the substrate detection mechanism works -- the gap is entirely in the encoder's negation representation. Convergent evidence with v443+v445: negation requires explicit negation-aware training/architecture, not order-sensitivity. KF-1 band 72-87% UNCHANGED.

Rescue sketches for KF-1 negation HARD_FAIL (both anchors combined, cheapest-first):
R1 (0-compute, SUBSUMPTION): v443 R5 (adversarial training on shuffled-fact pairs) already covers primary path. 3-seed confirmation shifts priority weight to R5 over R3/R4. No new rescue needed.
R2 (CHEAP, CPU <30min): Negation-contrast fine-tuning on MiniLM using only negation-pair examples (targeted minimal fine-tune, not full retraining).
R3 (CHEAP, CPU <30min): Instruction-tuned or NLI-trained sentence encoder as drop-in for MiniLM on negation axis specifically.
R4 (MEDIUM, GPU <2h): Pythia-scale-up (R3 from v443) + explicit negation-pair adversarial training (R5 from v443) combined -- most direct path to closing negation gap.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v447 -> v448)
- PROT-004/006: No closures. etf_hadamard LVH #228: 4 rescues cheapest-first. KF-1 negation: 4 rescues combined cheapest-first; R1 subsumption applies.
- PROT-007: v448 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 360th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of the 3 anchors. CLEAN.
- PROT-021: all source=remote run_mode=full n_seeds=3. No smoke artifacts. CLEAN.
- PROT-022: etf_hadamard seeds 17+23 identical (38x); seed7 zero collapse -- ZCA numerics degenerate init (not HP-fragility in classical sense; rescue R2 addresses). KF-1 anchors tight 3-seed spread (normal variance). No HP-fragility.

Cap_map: v447 -> v448 CYCLE 126 (0 HP; 2 HF-full: kf1_contradiction_order_sensitive-NEGATION-0.083-3SEED-FULL-ARCH-LIMIT-ORDER-INSUF + kf1_truthfulqa-NEGATION-0.018-3SEED-FULL-ARCH-DEFINITIVE-MINIML-NEGATION-INSENSITIVE; 1 MID-LVH #228: etf_hadamard_phase4a_repointed-HOPFIELD-ZCA-2/3-SEEDS-38x-1/3-SEED-ZCA-COLLAPSE; LVH 227->228; HONEST 973->976 +3; KF-1 72-87% UNCHANGED; PP-8 UNCHANGED; Portfolio 32+77; 360th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v448 -> v449 CYCLE 127 (2026-06-06)

Verdicts processed: substrate_per_cluster_stratified_extraction_v1 (MIDDLE_BAND -- 3-seed full promotion of cycle 123 LVH #226 smoke)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_per_cluster_stratified_extraction_v1 MIDDLE_BAND -- [label-vs-honest] LVH #226 CONFIRMED**
source=remote run_mode=full n_seeds=3.
Per-seed: seed7={sp10:(1.0,12.12x), sp100:(1.0,12.12x), sp1000:(1.0,12.12x)}, seed17={sp10:(1.0,11.93x), sp100:(1.0,11.93x), sp1000:(1.0,11.93x)}, seed23={sp10:(1.0,11.53x), sp100:(1.0,11.53x), sp1000:(1.0,11.53x)}.
LABEL OVER-CLAIMS. verdict_msg 'MIDDLE_BAND: >=0.95 coverage at 10-100x speedup' implies sp100=100x and sp1000=1000x achieved. Actual_speedup is uniformly 11.5-12.1x across ALL seeds and ALL sp-target cells. sp-target label does not reflect achieved speedup. Coverage=1.0 is genuine. LVH #226 (cycle 123 smoke) confirmed and refined: smoke estimated ~20x ceiling; full 3-seed resolves to ~12x ceiling. Smoke overestimated speedup by ~1.7x (n_tok=5000 smoke vs n_tok=40000 full changes cluster partitioning density).
Honest verdict: MIDDLE_BAND retained (coverage=1.0 real, 3-seed unanimous). Speedup range corrected: ~12x actual ceiling, NOT 10-100x label range.
LVH #226 STANDING (no new catch number; this is 3-seed confirmation of existing catch).
HONEST: 976 -> 977 (+1). LVH: 228 UNCHANGED (LVH #226 confirmed at 3-seed full).

### Cap_map decisions

**substrate_per_cluster_stratified_extraction_v1 MIDDLE_BAND [LVH #226 3-seed full: speedup ceiling=12x not 100x]**
Extraction sub-axis annotation (3-seed full promotion).
Coverage=1.0 confirmed unanimous 3/3 seeds. Per-cluster stratified extraction achieves perfect coverage.
Speedup ceiling characterised: ~12x across all 3 seeds and all sp-target levels. sp-target parameter does not drive actual speedup -- governed by cluster geometry relative to corpus size (n_tok=40000). Structural finding: at fixed cluster structure, speedup is partition-geometry-determined, not request-target-driven.
LVH #226 smoke reading (~20x) was an n_tok artifact: smaller corpus (5000 tok) gives more concentrated clusters = higher apparent speedup. Full corpus (40000 tok) resolves to 12x true ceiling.
Cycle-123 rescue R3 (larger n_tok sweep) reframing: speedup ceiling likely falls further with n_tok increase (larger corpus = denser inter-cluster coverage needed = lower speedup ratio). R3 now probes speedup/coverage tradeoff at scale rather than expecting speedup ceiling rise.
MIDDLE_BAND confirmed. No band-lift (HP threshold speedup >=50x; actual=12x). Extraction direction validated: stratified (1.0) >> random (0.60, cycle 123 anchor 9).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

R1 (0-compute, SUBSUMPTION): Coverage=1.0 at 12x is clean. Question pivots from 'achieve higher speedup' to 'does 12x speedup translate to useful downstream retrieval speed?' No additional coverage probes needed; 12x is definitive.
R2 (CHEAP, CPU <30min): Reduce cluster granularity (fewer, larger clusters) to push speedup ceiling above 12x while monitoring coverage degradation. Mechanism: fewer clusters = higher speedup ratio.
R3 (CHEAP, CPU <30min): Multi-level hierarchical extraction (coarse cluster -> fine sub-cluster) to decouple coverage from speedup ceiling. Should allow speedup >12x without coverage loss.
R4 (CHEAP, CPU <30min): Adaptive cluster count per query based on query embedding density, not fixed K. Expected: heterogeneous speedup/coverage tradeoff per query type.
R5 (MEDIUM, CPU <2h): Cross-encoder sweep (MiniLM, MPNet, Pythia) to test whether 12x ceiling is encoder-dependent (cluster geometry varies with encoder dimensionality).

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v448 -> v449)
- PROT-004/006: No closures. 5 rescues filed cheapest-first (R1 subsumption, R2-R4 cheap CPU, R5 medium CPU).
- PROT-007: v449 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 361st PROT-009 paired commit.
- PROT-018: No _nN suffix on anchor. CLEAN.
- PROT-021: source=remote run_mode=full n_seeds=3. No smoke artifacts. CLEAN.
- PROT-022: 3-seed spread tight (12.12x, 11.93x, 11.53x -- 0.59x range normal variance). No HP-fragility.

Cap_map: v448 -> v449 CYCLE 127 (0 HP; 0 HF; 1 MID-LVH#226-CONFIRMED: per_cluster_stratified_extraction-3SEED-FULL-COVERAGE-1.0-SPEEDUP-CEILING-12x-NOT-100x; LVH #226 confirmed at full-run; HONEST 976->977 +1; LVH 228 UNCHANGED; Portfolio 32+77; 361st PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

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

## v450 -> v451 CYCLE 129 BATCH (2026-06-06)

Verdicts processed (5):
1. substrate_continual_kv_n32768_120_sessions_v1 (GENUINELY NEW; N=32768 120-session continual-KV extension)
2. substrate_sparse_hadamard_mixture_codebook_v1 (GENUINELY NEW; sparse+Hadamard mixture codebook)
3. effective_rank_svd_multi_encoder_v1 (GENUINELY NEW; multi-encoder d_eff diagnostic, follow-up to v450 d_eff=82 MiniLM)
4. substrate_extraction_sqrt_K_allocation_v1 (RE-RUN smoke->full promotion; DUPLICATE-CHECK hint)
5. substrate_concept_uniform_random_extraction_v1 (RE-RUN smoke->full promotion; DUPLICATE-CHECK hint)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_continual_kv_n32768_120_sessions_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=32768, 7200 facts across 120 sessions.
Per-seed: seed7={all checkpoints: retention=1.0}, seed17={all checkpoints: retention=1.0}, seed23={all checkpoints: retention=1.0}.
HP threshold >=0.95 retention. ALL 3 seeds unanimous 1.000 at ALL checkpoints (session 30/60/90/120). HARD_PASS label correct. HONEST. +1 HONEST (980->981).

**(2) substrate_sparse_hadamard_mixture_codebook_v1 HARD_FAIL -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=4096, K_mix=4.
Per-seed: seed7={hadamard_cap=2048, shm_cap=0, ratio=0.0}, seed17={same}, seed23={same}.
ALL 3 seeds shm_cap=0. SHM completely fails: mixing Hadamard with sparse destroys capacity entirely. HARD_FAIL label correct. HONEST. +1 HONEST (981->982). No LVH.

**(3) effective_rank_svd_multi_encoder_v1 HARD_FAIL -- [label-vs-honest] LVH #231**
source=remote run_mode=smoke n_seeds=1. Encoders: all-MiniLM-L6-v2 (d_eff=77.1, D=384), pythia-160m (d_eff=18.3, D=768).
LABEL INCONSISTENCY IN verdict_msg. HARD_FAIL verdict technically correct (no encoder beats MiniLM by >1.3x). BUT verdict_msg claims 'all encoders ~MiniLM d_eff (<1.3x)' -- characterises Pythia as 'similar' when Pythia d_eff=18.3 is 4.2x LOWER than MiniLM=77.1. Pythia is dramatically WORSE (not similar); d_eff=18.3 vs 77.1.
LVH #231: (a) label HARD_FAIL 'all encoders ~MiniLM d_eff (<1.3x)'; (b) honest: Pythia-160m d_eff=18.3 is 4.2x LOWER than MiniLM=77.1; correct finding is 'LM-trained encoders have collapsed intrinsic dimensionality vs sentence-trained'; (c) contradicting cells: Pythia d_eff=18.3 vs MiniLM d_eff=77.1; best/MiniLM=1.00 label masks the 4.2x shortfall in absolute d_eff.
Honest verdict: HARD_FAIL confirmed. Key insight: sentence encoder training (MiniLM) produces 4x higher d_eff than LM training (Pythia) despite Pythia having 2x higher D. LVH #231. +1 HONEST (982->983). LVH 230->231 (+1). NOTE: smoke n_seeds=1 only.

**(4) substrate_extraction_sqrt_K_allocation_v1 MIDDLE_BAND -- [REVERSAL vs cycle-123 HF]**
source=remote run_mode=full n_seeds=3. VQ-fidelity (centroid_cos+heldout_agree)/2 at speedup=20x.
Per-seed sqrt_K/uniform fidelity: seed7={sqrt_K=0.716, uniform=0.685, ratio=1.046x}, seed17={sqrt_K=0.704, uniform=0.685, ratio=1.027x}, seed23={sqrt_K=0.748, uniform=0.716, ratio=1.047x}.
Mean ratio=1.039x. MIDDLE_BAND label correct (marginal 1.0-1.10x lift). HONEST.
REVERSAL NOTE: Cycle-123 smoke (n=1, coverage-by-speedup-target metric) gave HARD_FAIL -- sqrt_K WORSE than uniform. Full run uses VQ-fidelity metric at speedup=20x; shows sqrt_K 3.9% better. Reversal is a metric change (coverage vs VQ-fidelity), not stochastic flip. +1 HONEST (983->984). No LVH.

**(5) substrate_concept_uniform_random_extraction_v1 HARD_FAIL -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. n_tok=40000.
Per-seed sp10 coverage: seed7=0.542, seed17=0.514, seed23=0.515. sp100: 0.097/0.097/0.089. sp1000: 0.009/0.011/0.010.
ALL 3 seeds ALL speedup levels ALL below 0.90 threshold. 3-seed full confirms cycle-123 smoke HF. HONEST. +1 HONEST (984->985). No LVH.

HONEST: 980 -> 985 (+5: 5 genuinely new or full-promoted measurements). LVH: 230 -> 231 (+1: LVH #231 effective_rank_svd_multi_encoder Pythia-NOT-similar-to-MiniLM).

### Cap_map decisions

**(1) substrate_continual_kv_n32768_120_sessions_v1 HARD_PASS**
'True continual learning at production scale' Tier-1 KV sub-axis (extension of v437 continual-KV).
3-seed unanimous retention=1.000 at N=32768 120 sessions (7200 facts). Strongest continual-KV result to date.
IMPORTANT DISTINCTION: this is continuous-session KV (streaming facts into one epoch), NOT 4-stage conceptual CL (learn A/B/C/D discretely). Tier-1 row state remains PARTIAL (4-stage still blocked on ret_A<0.80). Continual-KV sub-property annotation strengthened: N=32768 120-session HARD_PASS added. No full Tier-1 band-lift.
Portfolio: UNCHANGED (sub-property within existing Tier-1 row).

**(2) substrate_sparse_hadamard_mixture_codebook_v1 HARD_FAIL**
PP-8 mixture codebook sub-axis. Combining sparse + Hadamard gives zero capacity (shm_cap=0 all 3 seeds). Complete failure.
The sparse-KEY alpha=0.20 direction (cycle-123 5x+ capacity HARD_PASS) is UNAFFECTED. This fails the MIXTURE of the two axes.
Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Diagnose which element of the mixture destroys capacity. K_mix=4 sparse components likely create orthogonality conflicts with Hadamard structure.
R2 (CHEAP, CPU <30min): Sweep K_mix={1,2,8,16} -- K_mix=1 (mostly Hadamard) may recover near-pure performance.
R3 (CHEAP, CPU <30min): Structured sparse components (LDPC-like, guaranteed near-orthogonal) instead of random sparse.
R4 (CHEAP, CPU <30min): Hadamard-only N-sweep as control -- verify pure Hadamard scales before attributing failure to mixture.
R5 (MEDIUM, CPU <2h): Algebraic analysis: does random-sparse + Hadamard product maintain Gram matrix properties for HD capacity?
PP-8 band UNCHANGED. Portfolio UNCHANGED.

**(3) effective_rank_svd_multi_encoder_v1 [LVH #231 honest: Pythia d_eff=18.3 MUCH LOWER than MiniLM=77.1]**
Phase-4A + PP-8 encoder selection sub-axis.
Honest finding: LM-trained encoders have collapsed intrinsic dimensionality (Pythia d_eff=18.3) vs sentence-trained (MiniLM d_eff=77.1). d_eff is training-regime-specific, NOT architecture-bounded near 80. Encoder search space must be sentence-trained only.
Implications: (a) LM-trained encoders (Pythia, GPT2, Llama) EXCLUDED as Phase-4 capacity levers; (b) sentence-trained larger encoders (MPNet-768, BGE-large, E5-large) are the correct search direction; (c) v450 d_eff=82 constraint (bounds all Phase-4 operations) applies to MiniLM; larger sentence-trained encoders may yield higher d_eff and thus more Phase-4 headroom.
Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Annotate encoder search space: sentence-trained only. LM-trained definitively excluded.
R2 (CHEAP, CPU <30min): d_eff diagnostic on MPNet-768 and BGE-large-1.5 to test if d_eff scales with D within sentence-training regime.
R3 (CHEAP, CPU <30min): Contrastive-trained encoder (e5-base) d_eff check -- different training objective may yield higher d_eff than standard SBERT.
PP-8 band UNCHANGED. NOTE: smoke n=1 only; directional finding robust (d_eff stable across random samples within a model).

**(4) substrate_extraction_sqrt_K_allocation_v1 MIDDLE_BAND (3-seed full; reversal from cycle-123 smoke HF)**
Extraction sub-axis (3-seed full promotion).
sqrt_K allocation: VQ-fidelity 1.039x over uniform at speedup=20x (3-seed consistent: 1.027-1.047x). MIDDLE_BAND (marginal, not HP).
REVERSAL NOTE: Different metrics explain the smoke/full discrepancy -- coverage-by-speedup (smoke) vs VQ-fidelity (full). sqrt_K has marginal fidelity advantage; no coverage advantage at requested speedup targets. Both metrics are valid; they measure different things.
Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Document metric split: VQ-fidelity MIDDLE_BAND 3.9%; coverage-by-target HARD_FAIL (smoke). Two evaluation axes.
R2 (CHEAP, CPU <30min): sqrt_K tested on coverage metric at n_tok=40000 (same corpus as full run) to verify coverage HF holds at full corpus scale.
R3 (CHEAP, CPU <30min): Exponential or variance-weighted allocation for higher VQ-fidelity leverage than sqrt_K.
Band UNCHANGED. Portfolio UNCHANGED.

**(5) substrate_concept_uniform_random_extraction_v1 HARD_FAIL (3-seed full confirmation)**
Extraction baseline. 3-seed full at n_tok=40000 definitively confirms random sampling cannot hold 0.90 coverage.
Structured extraction (per_cluster stratified, cycle-127 coverage=1.0 at ~12x speedup) clearly dominates.
No additional rescues needed: cycle-127 R2/R3/R4/R5 remain valid active directions.
Band UNCHANGED. Portfolio UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v450 -> v451)
- PROT-004/006: No capability-row closures. Rescues filed cheapest-first: anchor 2 (5 rescues), anchor 3 (3 rescues), anchor 4 (3 rescues). Anchor 5 subsumed by cycle-127 rescues.
- PROT-007: v451 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 363rd PROT-009 paired commit.
- PROT-018: No _nN suffixes on any anchor. CLEAN.
- PROT-021: Anchors 1,2,4,5 source=remote run_mode=full n_seeds=3. Anchor 3 source=remote run_mode=smoke n_seeds=1. Anchor 3 smoke flagged.
- PROT-022: Anchors 1,2,4,5 3-seed full consistent tight spreads. Anchor 3 smoke n=1; d_eff finding directionally robust.

Cap_map: v450 -> v451 CYCLE 129 (1 HP: continual_kv_n32768_120sessions-3SEED-FULL-RETENTION-1.000-120SESSIONS-7200FACTS; 2 HF: sparse_hadamard_mixture-3SEED-SHM-CAP-0-COMPLETE-FAIL + concept_uniform_random_extraction-3SEED-COVERAGE-0.52-HARD-FAIL-CONFIRMED; 1 HF-LVH#231: effective_rank_svd_multi_encoder-SMOKE-PYTHIA-DEFF-18.3-4.2x-LOWER-MINILM-77.1-LM-TRAINING-COLLAPSES-D_EFF; 1 MID: extraction_sqrt_K-3SEED-VQ-FIDELITY-1.039x-REVERSAL-FROM-SMOKE-HF; LVH #231: Pythia-d_eff-NOT-SIMILAR-MiniLM; continual-KV N=32768/120sessions sub-property strengthened; Tier-1-CL row PARTIAL UNCHANGED; PP-8 encoder search: LM-trained excluded, sentence-trained only; HONEST 980->985 +5; LVH 230->231 +1; Portfolio 32+77; 363rd PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v451 -> v452 CYCLE 130 8-VERDICT BATCH (2026-06-06)

Verdicts processed: 8 verdicts (5 genuinely new + 3 re-runs/promotions).

GENUINELY NEW: frame_slot_fill_k16_v1 + analogy_map_v1 + substrate_native_reasoning_K10_K20_n16384_v1 + substrate_sparsity_fine_battery_gpu_v1 + substrate_sparse_vs_dense_large_n_gpu_v1
RE-RUNS: hoc1_word_bigram_v1 (cycle-128 LVH #230 HP-SMOKE -> full promotion) + effective_rank_svd_v1 (cycle-128 d_eff diagnostic -> full) + substrate_etf_hadamard_phase4a_infra_eval_v1 (cycle-126 LVH #228 MIDDLE_BAND re-run)

### Step 0 honest re-read (MANDATORY)

**(1) frame_slot_fill_k16_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=8192, k=16. Per-seed: all={retrieval_accuracy=1.0}. HP>=0.95. ALL 3 seeds unanimous 1.000. HONEST. +1 HONEST (985->986).

**(2) analogy_map_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=8192, 300-way. Per-seed: all={analogy_accuracy=1.0}. HP>=0.70. ALL 3 seeds unanimous 1.000. HONEST. +1 HONEST (986->987).

**(3) substrate_native_reasoning_K10_K20_n16384_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. K-hop curve k={1,3,5,8,10,15,20} ALL=1.000 ALL 3 seeds. HP>=0.70 at K=3: CLEARED. Extension: K=20 no ceiling found (v445 stopped at K=10). HONEST. +1 HONEST (987->988).

**(4) substrate_sparsity_fine_battery_gpu_v1 HARD_PASS -- [label-vs-honest] LVH #232**
source=remote run_mode=smoke n_seeds=1. N=8192 ratios: sparse0.02=20.03x, sparse0.05=20.03x, sparse0.08=8.01x, sparse0.12=8.01x, sparse0.20=4.0x, sparse0.35=2.0x, sparse0.50=1.0x. HP>=3x: cleared at alpha<=0.20.
LABEL OVER-CLAIMS. smoke n=1 -- HARD_PASS requires multi-seed full per PROT-021.
LVH #232: (a) label HARD_PASS; (b) honest: HP-SMOKE -- fine battery genuine but single-seed; 3-seed full needed before HARD_PASS; (c) cells: run_mode=smoke n_seeds=1 (PROT-021 multi-seed not met).
Honest: HP-SMOKE. Fine sparsity curve: 20x at alpha=0.02-0.05, 8x at 0.08-0.12, 4x at 0.20, floor at 0.50. +1 HONEST (988->989). LVH 231->232 (+1).

**(5) substrate_sparse_vs_dense_large_n_gpu_v1 HARD_PASS -- [label-vs-honest] LVH #233**
source=remote run_mode=smoke n_seeds=1. N=4096: ratio=8.03x, N=8192: ratio=8.01x (alpha=0.08).
LABEL OVER-CLAIMS. smoke n=1. HARD_PASS 'production-scale capacity lever' from single smoke seed on new N configuration.
Context: v445 cycle-123 3-seed full alpha=0.20 N={4096,16384} (5.0-6.7x). Current alpha=0.08 gives 8x (higher ratio). Directionally consistent but single-seed new configuration.
LVH #233: (a) label HARD_PASS; (b) honest: HP-SMOKE -- large-N extension corroborated but single-seed; (c) cells: run_mode=smoke n_seeds=1 (PROT-021 not met).
Honest: HP-SMOKE. +1 HONEST (989->990). LVH 232->233 (+1).

**(6) hoc1_word_bigram_v1 HARD_PASS -- LABEL HONEST (cycle-128 LVH #230 full promotion)**
source=remote run_mode=full n_seeds=3. Per-seed: seed7=0.9783, seed17=0.9788, seed23=0.9743. Mean=0.977. HP>=0.90: ALL 3 seeds clear. Tight spread (0.005pp) = mechanistically stable. Gate CLOSES: word-bigram HD discriminator rescues KF-1 word-shuffle at AUC=0.977 (char-ngram 0.19, MiniLM-only 0.22). HONEST. +1 HONEST (990->991).

**(7) effective_rank_svd_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=1. d_eff=91.6, rank90=175, rank99=296, D=384, n_enc=8000. HP d_eff<=120: CLEARED. Updates cycle-128 d_eff=82 (fewer samples); 91.6 with n_enc=8000 is authoritative. Phase-4A ceiling: real-encoder ops bounded by d_eff=91.6 (+12% headroom vs 82). HONEST. +1 HONEST (991->992).

**(8) substrate_etf_hadamard_phase4a_infra_eval_v1 HARD_FAIL -- LABEL HONEST (critical regression)**
source=remote run_mode=full n_seeds=3. Per-seed: all={raw=0, wht=0, ratio=0.0}. HARD_FAIL correct.
CRITICAL REGRESSION from cycle-126 v448 (seeds17+23 wht=38; seed7=0; LVH #228 MIDDLE_BAND). Current run: ALL seeds wht=0. ZCA whitening completely failed. Prior v448 2/3-seeds partial pass superseded by all-zeros. Diagnosis: script version change or ZCA rank-floor patch regression. HONEST. +1 HONEST (992->993).

HONEST: 985 -> 993 (+8). LVH: 231 -> 233 (+2: LVH #232 sparsity_fine_battery HP-SMOKE + LVH #233 sparse_vs_dense_large_n HP-SMOKE).

### Cap_map decisions

**(1) frame_slot_fill_k16_v1 HARD_PASS**
NEW ROW: KG multi-attribute frame binding. k=16 attributes/entity, N=8192, 3-seed unanimous retrieval=1.000. Substrate stores 16-slot entity frames at perfect retrieval. Product: KG entity binding validated at k=16.
Portfolio: +1 (NEW ROW; P-band 0.75-0.90 EXPLORATORY; single-N single-k; deeper k and multi-entity interference untested).

**(2) analogy_map_v1 HARD_PASS**
NEW ROW: Native relational reasoning. 300-way analogy_accuracy=1.000, N=8192, 3-seed unanimous via bundle arithmetic (A-B+C=D). Substrate executes relational queries as pure vector arithmetic -- no LLM decode loop.
Portfolio: +1 (NEW ROW; P-band 0.70-0.85 EXPLORATORY; single-N; larger vocabulary and noisy analogies untested).
[Total after both additions: 32+79]

**(3) substrate_native_reasoning_K10_K20_n16384_v1 HARD_PASS**
PP-11 BAND-LIFT: 0.55-0.70 -> 0.60-0.75 (+5%/+5% CONSERVATIVE).
K=20 N=16384 unanimous 1.000, 3-seed full. Two consecutive monotone K-extensions at N=16384: v445 K=10 HP + this K=20 HP. PROT-008 validator PASS. Ceiling K>20 untested. Annotation: K=20 no-ceiling; K={25,30} recommended next.

**(4) substrate_sparsity_fine_battery_gpu_v1 [LVH #232 honest: HP-SMOKE]**
PP-8 sparsity fine-battery annotation. HP-SMOKE (smoke n=1). Fine curve at N=8192 characterised: 20x at alpha=0.02-0.05, 8x at 0.08-0.12, 4x at 0.20, 1x at 0.50. Refines v445 alpha=0.20->5x. No band-lift.
Rescue (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): HP-SMOKE consistent with v445 alpha=0.20->5x; 20x at alpha=0.02 is steeper extension.
R2 (CHEAP, GPU <30min): 3-seed full fine battery at N=8192 to convert HP-SMOKE to HARD_PASS.
R3 (CHEAP, GPU <30min): N-sweep at alpha=0.02 across N={4096,8192,16384} to characterize N-scaling of peak sparsity capacity.
PP-8 band UNCHANGED.

**(5) substrate_sparse_vs_dense_large_n_gpu_v1 [LVH #233 honest: HP-SMOKE]**
PP-8 large-N sparsity annotation. HP-SMOKE (smoke n=1). alpha=0.08, N=8192: ratio=8.01x. Cross-anchor corroboration with anchor 4 (both measure alpha=0.08 at N=8192 independently -- exact match 8.01x).
Rescue (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Cross-anchor consistency confirmed; independent corroboration of alpha=0.08->8x.
R2 (CHEAP, GPU <30min): 3-seed full at N=8192 alpha=0.08 to convert HP-SMOKE to HARD_PASS.
PP-8 band UNCHANGED.

**(6) hoc1_word_bigram_v1 HARD_PASS (cycle-128 LVH #230 full promotion)**
KF-1 BAND-LIFT: 72-87% -> 75-90% (+3%/+3% CONSERVATIVE). Gate closes: word-shuffle axis AUC=0.977 3-seed full (>> 0.90). Best KF-1 adversarial rescue to date (4.4x lift vs MiniLM-only baseline 0.22). PROT-008 validator PASS (cycle-128 smoke 0.970 + full 0.977 consistent). Negation sub-axis still architecturally open (mean=0.018-0.083); band-lift scoped to word-shuffle closure only.

**(7) effective_rank_svd_v1 HARD_PASS**
PP-8 + Phase-4A annotation update. d_eff=82->91.6 (participation_ratio, n_enc=8000 authoritative). All real-encoder substrate operations bounded by d_eff=91.6 not 82. +12% headroom. Sentence-trained larger encoder search (MPNet/BGE/E5) unchanged -- expected higher d_eff.
Band UNCHANGED (annotation update only).

**(8) substrate_etf_hadamard_phase4a_infra_eval_v1 HARD_FAIL (critical ZCA regression)**
PP-8 Phase-4A annotation downgraded: MIDDLE_BAND-2/3-seeds -> HARD_FAIL-all-zeros-ZCA-regression. ALL seeds wht=0 vs v448 seeds17+23 wht=38. Phase-4B blocked pending ZCA diagnosis.
Rescue (PROT-004/006; cheapest-first):
R1 (0-compute, DIAGNOSIS): Git diff on Phase-4A script between v448 and current; identify ZCA rank-floor patch regression.
R2 (CHEAP, CPU <30min): Verify ZCA at seeds 17+23 with v448 code version to isolate regression point.
R3 (CHEAP, CPU <30min): PCA or random-projection whitening at N_sub=384 (v448 R4 recommendation; bypasses ZCA numerics).
R4 (MEDIUM, GPU <2h): If ZCA repaired: N_sub sweep {384,512,1024} to characterize Phase-4A capacity curve.
PP-8 Phase-4A sub-axis: HARD_FAIL-ZCA-regression (Phase-4B blocked; diagnosis R1 first).

### Portfolio: 32+77 -> 32+79 (+2 NEW ROWS: KG-multi-attribute-frame-binding + native-relational-reasoning). 2 BAND-LIFTS (PP-11 0.55-0.70->0.60-0.75 + KF-1 72-87%->75-90%). 0 closures.

### PROT compliance (v451 -> v452)
- PROT-004/006: No closures. Rescues filed cheapest-first: anchors 4 (3 rescues), 5 (2 rescues), 8 (4 rescues).
- PROT-007: v452 history row appended to substrate_capability_map_history.md.
- PROT-008: PP-11 LIFT: v445 K=10 + this K=20 monotone at N=16384. Validator PASS. KF-1 LIFT: smoke 0.970 + full 0.977 consistent. Validator PASS. NEW ROWs: 3-seed 1.000 both; no regression.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 364th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of 8 anchors. CLEAN.
- PROT-021: Anchors 1,2,3,6,7,8 source=remote run_mode=full. Anchors 4,5 source=remote run_mode=smoke n_seeds=1. LVH #232+#233 filed.
- PROT-022: Anchors 1,2,3,6 3-seed tight spreads. Anchor 7 n=1 deterministic. Anchor 8 ZCA regression (not HP-fragility). Anchors 4,5 smoke n=1.

Cap_map: v451 -> v452 CYCLE 130 (3 HP: frame_slot_fill_k16-3SEED-KG-ATTR-1.000 + analogy_map-3SEED-RELATIONAL-1.000-300WAY + native_reasoning_K20-3SEED-K20-NO-CEILING; 1 HP-diag: effective_rank-DEFF-91.6-UPDATED; 1 HF: etf_hadamard_phase4a-ALL-SEEDS-ZCA-0-REGRESSION; 1 HP-full: hoc1_word_bigram-AUC-0.977-3SEED-KF1-GATE-CLOSED; 2 HP-SMOKE-LVH #232+#233: sparsity_fine_battery + sparse_vs_dense_large_n; PP-11 LIFT 0.55-0.70->0.60-0.75; KF-1 LIFT 72-87%->75-90%; +2 NEW ROWS 32+79; HONEST 985->993 +8; LVH 231->233 +2; 364th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v452 -> v453 CYCLE 131 BATCH (2026-06-06)

Verdicts processed: effective_rank_svd_multi_encoder_v1 (HARD_FAIL RE-RUN) + substrate_expansion_method_battery_gpu_v1 (HARD_PASS SMOKE LVH#234)

### Step 0 honest re-read

**(1) effective_rank_svd_multi_encoder_v1 HARD_FAIL -- LABEL HONEST**
3-encoder full run (n_seeds=1). MiniLM d_eff=91.1, mpnet d_eff=87.0, bge-large d_eff=114.8. All below 150 threshold. HARD_FAIL label correct.
DUPLICATE CHECK: cycle 129 LVH#231 had MiniLM=77.1; this run shows MiniLM=91.1 (+14pp) AND adds mpnet+bge-large two new encoders. NOT a duplicate -- expanded encoder coverage. Standard verdict applies.
Note: bge-large=114.8 is highest d_eff observed to date across all encoder probes; still 24% below 150 threshold.
HONEST +1.

**(2) substrate_expansion_method_battery_gpu_v1 HARD_PASS SMOKE -- LVH #234**
run_mode=SMOKE n_seeds=1 elapsed=11.8s. Per-cell metrics are alpha values only: native/rp_x2/rp_x4 alpha=0.0; zca_whiten r=64 alpha=0.01953125; zca_whiten r=256 alpha=0.0498046875.
verdict_msg claims rp_x4/native(avg)=0.00 | zca/native(low-r)=19531250.00.
LVH #234: ratio 19531250.00 is a zero-division artifact (native alpha=0.0 makes any ratio degenerate and numerically meaningless). A smoke n=1 run with a degenerate comparison metric CANNOT support HARD_PASS. Directional signal is real (whitening produces nonzero alpha; expansion methods stay at zero), but no actual d_eff or capacity measurement is present in per-cell data.
Honest reading: SMOKE-PARTIAL -- directional whitening-beats-expansion signal confirmed at synthetic scale; HARD_PASS requires full run with actual capacity/d_eff numbers.
LVH entry: (a) label=HARD_PASS; (b) honest=SMOKE-PARTIAL directional-signal-only; (c) cells contradicting: all per-cell alpha=0.0 for native/rp; ratio=19531250 is 0.0/0.0 artifact not empirical measurement.
HONEST +1. LVH 233 -> 234 (+1).

HONEST: 993 -> 995 (+2). LVH: 233 -> 234 (+1).

### Cap_map decisions

**(1) effective_rank_svd_multi_encoder_v1 HARD_FAIL**
PP-8 / effective-dimensionality sub-property annotation. Re-run of LVH#231 (cycle 129 MiniLM=77.1 only) with expanded encoder coverage. New findings:
- MiniLM: d_eff=91.1 (consistent with v452 update to 91.6; re-measurement corroborates)
- mpnet: d_eff=87.0 (lower than MiniLM despite 2x wider D=768 -- encoder architecture not raw dimension determines d_eff)
- bge-large: d_eff=114.8 (highest d_eff of all tested encoders; D=1024; still 24% below 150 threshold)
Conclusion: d_eff is architecture-bounded at current encoder class; best off-the-shelf encoder reaches 114.8 -- 23.5% below 150 threshold. Encoder choice matters (+28pp bge vs mpnet) but all three are below threshold. LM-trained encoders (Pythia d_eff=18.3, v451) excluded; that conclusion stands.
Cap_map annotation: update effective_rank sub-property with bge-large=114.8 as new best; mpnet=87.0 added; encoder ordering by d_eff: bge-large > MiniLM > mpnet. Rescue axes (cheapest-first per PROT-004/006):
R1 (0-compute, SUBSUMPTION): Use bge-large as Phase-4 default encoder (highest d_eff; already tested); no additional run needed.
R2 (CHEAP, CPU <30min): ZCA whitening applied to bge-large embeddings -- if whitening 2.75x lift (v441 result on MiniLM) applies similarly to bge-large: 114.8*2.75=315.7 >> 150 threshold. High-value next step.
R3 (CHEAP, CPU <30min): PCA dim-reduction to decorrelate bge-large embeddings before d_eff measurement -- may increase effective rank by removing correlated directions.
R4 (MEDIUM, CPU <2h): Instruction-tuned encoder sweep (e5-large, GTE-large) -- instruction-tuning may preserve more semantic axes and increase d_eff.
Band UNCHANGED.

**(2) substrate_expansion_method_battery_gpu_v1 HARD_PASS -> SMOKE-PARTIAL (LVH#234)**
Honest reading SMOKE-PARTIAL. Directional signal: whitening produces nonzero alpha at both r={64,256}; native/rp methods stay at alpha=0.0. Expansion methods (rp_x2, rp_x4) do NOT improve over native on this alpha metric. Framework qualitative direction confirmed: whitening > expansion. No cap_map state change from LVH#234 anchor -- per-cell data is alpha values not capacity/d_eff; HARD_PASS cannot be committed. Routing note: needs full run with d_eff or capacity as primary metric before cap_map update.
R1 (CHEAP, GPU <1h): Full run (n_seeds=3) with d_eff as primary output metric replacing alpha; compare native/rp_x2/rp_x4/zca_whiten at r={64,256} directly on d_eff scale.
R2 (CHEAP, CPU <30min): Apply ZCA whitening to bge-large baseline (R2 above subsumes encoder-axis test).

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v452 -> v453)
- PROT-004/006: Anchor 1 HARD_FAIL: R1-R4 cheapest-first filed. Anchor 2 LVH: R1-R2 filed.
- PROT-007: v453 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes. Validator not triggered.
- PROT-009: cap_map.md + history.md + decisions log atomically staged; 365th PROT-009 paired commit.
- PROT-018: No _nN suffixes. CLEAN.
- PROT-021: Anchor 1 source=remote run_mode=full CLEAN. Anchor 2 source=remote run_mode=SMOKE -- LVH#234 filed; smoke artifact not propagated to cap_map.
- PROT-022: Both n_seeds=1. HP-fragility not evaluable. LVH#234 covers smoke-as-HARD_PASS risk.

Cap_map: v452 -> v453 CYCLE 131 (1 HF: effective_rank_svd_multi_encoder ENCODER-BOUNDED-bge_large=114.8-BEST-BELOW-150; 1 LVH#234: expansion_method_battery HARD_PASS-SMOKE-ZERO_DIV-ARTIFACT-HONEST=SMOKE-PARTIAL; 0 HP; HONEST 993->995 +2; LVH 233->234 +1; Portfolio 32+79 UNCHANGED; R1-R4 encoder rescues filed; R1-R2 expansion rescues filed; annotation-only; 365th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v453 -> v454 CYCLE 132 BATCH (2026-06-06)

Verdicts processed: substrate_expansion_method_battery_gpu_v1 (RE-RUN full 3-seed; cycle 131 LVH #234 proper re-run) + multi_head_sparse_key_battery_gpu_v1 (GENUINELY NEW orphan-recovered; multi-head sparse-KEY battery) + dimsparse3_alpha_at_mc_v1 (GENUINELY NEW orphan-recovered; dim-expansion + sparse-KEY AT M_c regime)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_expansion_method_battery_gpu_v1 HARD_PASS -- LABEL HONEST (RE-RUN CLEAN)**
source=remote run_mode=full n_seeds=3. DUPLICATE-CHECK: cycle 131 LVH#234 was smoke n=1 with zero-division artifact alpha ratio. THIS is the proper 3-seed full re-run with actual per-cell alpha data. NOT a duplicate.
Per-cell (representative): native/rp_x2/rp_x4 alpha=0.0 at r=32,64; equal and near-zero at r=128,256,512. ZCA whitening: r=32->0.0195, r=64->0.0298, r=128->0.0498, r=256->0.0796, r=512->0.0796. All 3 seeds unanimous on every cell (deterministic).
Verdict_msg means verified: native=0.0065, rp_x4=0.0065, zca_whiten=0.0517. rp_x4 == native cell-by-cell (verified). ZCA strictly > native at all r (verified).
Label claim 'd_eff framework confirmed at synthetic scale': FRAMEWORK-VALIDATION verdict, not numerical-threshold claim. HONEST. No LVH.
HONEST +1 (995->996).

**(2) multi_head_sparse_key_battery_gpu_v1 HARD_PASS -- LVH #235**
source=remote run_mode=SMOKE n_seeds=1. elapsed=0.87s (very fast -- single tiny run).
Per-cell: H1=0.1997, H2=0.3999, H4=0.6997, H8=0.6997. H2/H1=2.00x, H4/H2=1.75x.
LABEL OVER-CLAIMS. HARD_PASS on smoke n=1 violates PROT-021 multi-seed requirement. Additionally: H8=H4 (alpha saturates at 0.700 beyond H=4) -- saturation not disclosed in verdict_msg.
LVH #235: (a) label HARD_PASS; (b) honest: HP-SMOKE -- H2/H1=2.00x and H4/H2=1.75x genuine monotone scaling signals but single-seed; HARD_PASS requires 3-seed full; also H8=H4 plateau; (c) contradicting cells: run_mode=smoke n_seeds=1 (PROT-021 not met); H8 alpha=H4 alpha (saturation at H=4 not disclosed in verdict_msg).
Honest verdict: HP-SMOKE. Multi-head sparse-KEY composition lever confirmed directionally; saturation at H>=8 noted.
HONEST +1 (996->997). LVH 234->235 (+1).

**(3) dimsparse3_alpha_at_mc_v1 HARD_FAIL -- LABEL HONEST**
source=remote run_mode=SMOKE n_seeds=1.
Per-cell: M_c={baseline:32, dim_expand_x2:32, sparse_key:4, compound:4}. best_rescue/baseline=1.00x.
Label claim 'no rescue >1.2x' -- verified: dim_expand=32=baseline (1.00x), sparse_key=4 (0.125x, WORSE), compound=4 (0.125x, WORSE). HARD_FAIL label correct.
NUANCE: sparse_key AT M_c regime is anti-helpful (M_c drops from 32 to 4, 8x degradation). Directly answers cycle-124 deferred question and cycle-129 ordering question with proper M-regime data. dim-expansion holds M_c stable; sparse-KEY collapses it. NOT contradictory with cycle-123 sub-capacity alpha result (different operating regimes).
HONEST. No LVH. HONEST +1 (997->998).

HONEST: 995 -> 998 (+3: 1 genuine re-run + 2 genuinely new). LVH: 234 -> 235 (+1: multi_head_sparse_key HP-SMOKE-SINGLE-SEED-SATURATION).

### Cap_map decisions

**(1) substrate_expansion_method_battery_gpu_v1 HARD_PASS (3-seed full; supersedes LVH#234 smoke)**
PP-8 / effective-dimensionality sub-property annotation (FINAL proper reading).
Supersedes cycle-131 LVH#234 SMOKE-PARTIAL. Full 3-seed confirms: expansion (rp_x2, rp_x4) does NOT improve alpha over native. ZCA whitening strictly > native at all r, 3 seeds unanimous. d_eff framework: whitening increases effective rank through decorrelation; random projection expands dimension but does NOT increase effective rank. Closes rp_x2/rp_x4 as capacity levers. ZCA whitening confirmed as the single mechanism lifting alpha.
Annotation: HARD_PASS (full); SMOKE-PARTIAL annotation from v453 superseded.

**(2) multi_head_sparse_key_battery_gpu_v1 [LVH #235 honest: HP-SMOKE; H2/H1=2.00x H4/H2=1.75x; saturation H>=8]**
PP-8 / sparse-KEY multi-head sub-axis. HP-SMOKE annotation only.
Genuine signal: multi-head sparse-KEY shows clean monotone scaling H1->H4 at N=2048. Saturation at H>=8. Extends cycle-123 sparse-KEY single-head result. Multi-head is a composition lever up to H=4.
Rescues (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): H1->H4 monotone scaling documented; saturation H>=8 documented.
R2 (CHEAP, GPU <30min): 3-seed full at H={1,2,4,8} N=2048 to convert HP-SMOKE to HARD_PASS.
R3 (CHEAP, GPU <30min): N-sweep at H=4 across N={4096,8192,16384} to check scaling at larger N.
R4 (MEDIUM, GPU <2h): Multi-head sparse-KEY + dim-expansion compound at H=4 to test stacking of orthogonal mechanisms.
Band UNCHANGED.

**(3) dimsparse3_alpha_at_mc_v1 HARD_FAIL (smoke; cycle-124+129 open questions ANSWERED)**
PP-8 M_c-regime stacking sub-axis. HARD_FAIL smoke n=1.
Key finding: AT M_c, sparse-KEY DESTROYS capacity (M_c collapses 32->4, 8x degradation). dim-expand HOLDS M_c stable (32=32). Compound collapses to sparse_key (M_c=4). Decisive negative at the most critical operating regime.
Answers cycle-124 deferred question: stacking at M_c is anti-synergistic when sparse-KEY is one lever.
Answers cycle-129 ordering question: dim-expansion survives at M_c; sparse-KEY does not.
Does NOT contradict cycle-123 sparse-KEY sub-capacity HARD_PASS (different regime: M_c vs alpha).
Rescues (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Clarify regime split -- sparse-KEY improves sub-capacity alpha (cycle-123) but collapses M_c (this result). Not contradictory; different operating points.
R2 (0-compute, SUBSUMPTION): dim-expansion-alone at M_c is clean lever (M_c=32=baseline); compound designs must exclude sparse-KEY at M_c regime.
R3 (CHEAP, GPU <30min): M_c probe for sparse-KEY at lower alpha values (alpha=0.05, 0.10) to test if M_c collapse is alpha-specific.
R4 (CHEAP, GPU <30min): Multi-head sparse-KEY (H=4) at M_c to test if multi-head structure avoids collision-induced M_c collapse.
R5 (MEDIUM, GPU <2h): Full 3-seed M_c sweep with compound dim_expand_x2 + structured keys (Hadamard) as M_c baseline robustness control.
Band UNCHANGED. Portfolio UNCHANGED.

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v453 -> v454)
- PROT-004/006: No closures. Anchor 2 LVH#235: 4 rescues cheapest-first. Anchor 3 HF: 5 rescues cheapest-first.
- PROT-007: v454 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes. Anchor 1 supersedes SMOKE-PARTIAL (quality upgrade within HARD_PASS). Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 366th PROT-009 paired commit.
- PROT-018: No _nN suffixes. CLEAN.
- PROT-021: Anchor 1 source=remote run_mode=full n_seeds=3 CLEAN. Anchors 2+3 source=remote run_mode=smoke n_seeds=1. LVH#235 filed for anchor 2. Anchor 3 smoke HF mechanistically robust.
- PROT-022: Anchor 1 all-seeds identical (deterministic alpha). Anchors 2+3 n=1 smoke; HP-fragility not evaluable.

Cap_map: v453 -> v454 CYCLE 132 (1 HP-full: expansion_method_battery-3SEED-WHITENING-BEATS-EXPANSION-ZCA-0.0517-CONFIRMED-SUPERSEDES-LVH234; 1 HP-SMOKE-LVH#235: multi_head_sparse_key-SMOKE-H2/H1=2.00x-H4/H2=1.75x-SATURATION-H8; 1 HF: dimsparse3_alpha_at_mc-SMOKE-SPARSE-KEY-DESTROYS-Mc-32->4-DIM-EXPAND-HOLDS-32=32-CYCLE124+129-ANSWERED; LVH 234->235 +1; HONEST 995->998 +3; Portfolio 32+79 UNCHANGED; 366th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v454 -> v455 CYCLE 133 BATCH (2026-06-06)

Verdicts processed: 6-anchor batch (5 genuinely new + 1 full-run promotion of cycle-132 HF-smoke)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_hierarchical_hadamard_then_sparse_key_alpha_v1 -- MIDDLE_BAND -- LVH #236**
source=remote, run_mode=full, n_seeds=3.
Per-cell: ALL 3 seeds (7,17,23): dense=0.0498, hadamard=0.5, sparse=0.5, hadamard_then_sparse=0.5 (identically 0.5 on all seeds, no variance).
verdict_msg claims range '1.0-1.2x' for hadamard_then_sparse/best_single but ALL cells show exactly 1.00x -- the '1.2x' upper bound is unsupported by any seed in the data.
LVH #236: verdict_msg range overclaims upper bound. Honest reading: MIDDLE_BAND at 1.00x -- sequential layering does NOT compound; matches best single with zero gain.
HONEST: 998 -> 999 (+1). LVH: 235 -> 236 (+1).

**(2) cs1_dt_algebraic_audit_v1 -- MIDDLE_BAND -- HONEST**
source=remote, run_mode=full, n_seeds=1 (algebraic deterministic audit).
Per-arm: dense rho_DT=0.008 (below_boundary=False), sparse0.20 rho_DT=0.059 (False), sparse0.10 rho_DT=0.179 (False), sparse0.05 rho_DT=0.998 (True), hadamard rho_DT=0.179 (False).
Only 1/5 arms (sparse0.05: alpha=1.0, delta=1.0, rho=0.05) satisfies DT boundary condition. 4/5 arms do not. MIDDLE_BAND honest: DT boundary partially predictive -- only extreme-sparsity arm confirms theory.
elapsed_s=0.001 -- algebraic deterministic; n=1 appropriate. HONEST. +1 HONEST.

**(3) fact_checked_khop_v1 -- HARD_PASS -- HONEST**
source=remote, run_mode=full, n_seeds=3, N=8192.
Per-seed: ALL K={2,3,4,5} acc=1.000 unanimous 3/3 seeds. fabrication_flag_auc=1.000 unanimous 3/3 seeds.
Both primary claims (k-hop reasoning + per-hop fabrication localization) confirmed at ceiling. HP threshold cleared with no borderline cells. HONEST. +1 HONEST.

**(4) multi_head_sparse_key_M2_v1 -- HARD_PASS -- HONEST (resolves LVH #235)**
source=remote, run_mode=full, n_seeds=3, N=4096.
Per-seed H2/H1 ratios: seed7=0.5498/0.1999=2.75x, seed17=0.3999/0.1999=2.00x, seed23=0.3999/0.1999=2.00x. Mean=2.25x.
HP threshold >=1.3x: ALL 3 seeds clear (min=2.00x). Cycle-132 LVH #235 (smoke HP label from n=1 H2/H1=2.00x) RESOLVED by full 3-seed confirmation.
Seed7 spread (2.75x vs 2.00x on seeds 17/23) noted -- HP-fragility PROT-022 check: all seeds above threshold, spread is directionally consistent (not fragile). HONEST. +1 HONEST.

**(5) sparse_key_composition_battery_gpu_v1 -- MIDDLE_BAND -- HONEST**
source=remote, run_mode=full, n_seeds=3, N={4096,8192,16384}.
flat_sparse alpha 0.45-0.60 (strong, consistent across N). hadamard alpha ~0.15 (weak). hadamard_indep_mask alpha 0.45-0.60 (matches flat_sparse). block_sparse alpha 0.02-0.05 (very weak).
'One composition arm passes' claim: hadamard_indep_mask ~ flat_sparse (ratio=1.00x); no arm strictly BEATS flat_sparse. MIDDLE_BAND honest. HONEST. +1 HONEST.

**(6) dimsparse3_alpha_at_mc_v1 -- HARD_FAIL -- HONEST (full-run confirmation of cycle-132 HF-smoke)**
source=remote, run_mode=full, n_seeds=3.
Per-seed Mc: baseline={12,12,12}, dim_expand={12,16,12}, sparse_key={2,2,2}, compound={4,8,4}.
Mean: baseline=12.0, dim_expand=13.3, sparse_key=2.0, compound=5.3. best_rescue/baseline=1.11x (dim_expand).
HF threshold: no rescue >1.2x. Unanimous across all 3 seeds. Sparse_key DESTROYS Mc (Mc=2.0 vs baseline=12.0). Full-run CONFIRMS cycle-132 HF-smoke. M_c rescue axis for sparse-key definitively closed. HONEST. +1 HONEST.

TOTAL HONEST: 998 -> 1003 (+5 genuinely new + 1 LVH catch = net +5 to HONEST counter).
LVH: 235 -> 236 (+1 catch #236 hierarchical_hadamard range overclaim 1.0-1.2x vs actual 1.00x).

### Cap_map decisions (v454 -> v455)

**(1) hierarchical_hadamard_then_sparse_key annotation [MIDDLE_BAND; LVH #236]**
Sequential Hadamard-first then sparse-KEY layering: alpha_combined == alpha_best_single at ALL 3 seeds (1.00x, zero compounding). Cycle-132 regime-split hypothesis refuted at full 3-seed. Sequential hierarchy does NOT compound capacity. PP-8 annotation: sequential composition closed -- ordering does not matter at compatible alpha. Independent-mask path (sparse_key_composition_battery hadamard_indep_mask arm) is the superior architecture.

**(2) cs1_dt_algebraic_audit annotation [MIDDLE_BAND; algebraic audit]**
DT boundary condition predictive only at extreme-sparsity limit (alpha=1.0, delta=1.0, rho=0.05). At moderate sparsity (alpha<=0.4, rho>=0.25) DT boundary is NOT predictive. CS-1 DT boundary is a high-alpha/low-rho limit law, not a general predictor. PP-8 sub-annotation: use empirical alpha sweeps for moderate-sparsity engineering; DT framework has limited range.

**(3) fact_checked_khop + fabrication localization [HARD_PASS; sub-property extension]**
K-hop reasoning K={2-5} + per-hop fabrication localization both at 1.000 unanimous 3-seed N=8192. Sub-property added to existing K-hop row: 'per-hop fabrication_flag localization -- substrate audits its own reasoning chain hop-by-hop (AUC=1.000 3-seed).' This is uniquely differentiating vs frontier LLMs which cannot localize which hop introduced hallucination. Portfolio 32+79 UNCHANGED (sub-property extension, not new row).

**(4) multi_head_sparse_key M=2 HARD_PASS full; LVH #235 RESOLVED [sub-property]**
H2/H1 mean=2.25x (min=2.00x, max=2.75x), all 3 seeds above 1.3x HP threshold. LVH #235 resolved: full run confirms smoke HP. Super-sqrt(M) gain on seed7. PP-8 sparse-KEY multi-head sub-property: 'M=2 multi-head composes cleanly; H2/H1 = 2.00-2.75x 3-seed full. Super-sqrt(M) gain warrants M=4 sweep.' Active probe: M=4 sweep to characterize multi-head scaling exponent.

**(5) sparse_key_composition_battery annotation [MIDDLE_BAND]**
flat_sparse and hadamard_indep_mask equivalent (~0.45-0.60). hadamard joint-mask weak (0.15). block_sparse very weak (0.02-0.05). Key design principle: independent mask paths preserve capacity; coupled/joint-mask transformations are destructive. PP-8 annotation: use independent mask paths not coupled transformations for sparse-KEY multi-arm architectures.

**(6) dimsparse3_alpha_at_mc HARD_FAIL full; M_c-sparse-key rescue CLOSED**
Sparse_key Mc=2.0 vs baseline=12.0 -- capacity destroyed. dim_expand best 1.11x. No rescue >1.2x. M_c rescue axis for sparse-key definitively closed (3-seed full).
RESCUE SKETCHES (cheapest-first per PROT-004/006):
R1 (0-compute, SUBSUMPTION): sparse-KEY alpha benefit real on alpha metric; this closure is M_c axis only.
R2 (CHEAP, CPU <30min): Dense M_c + sparse-KEY retrieval head -- orthogonal pipeline stages.
R3 (CHEAP, CPU <30min): dim_expand x4/x8 sweep (x2 gave 1.11x; x4/x8 might clear 1.2x).
R4 (MEDIUM, CPU <2h): Tied-key orthogonalization prior to sparse masking -- preserve M_c while recovering alpha benefit.
R5 (MEDIUM, GPU <2h): Hierarchical M_c with sub-sparse-KEY per level.
Portfolio 32+79 UNCHANGED (sub-axis closure, not portfolio row closure).

### PROT compliance (v454 -> v455)

- PROT-004/006: 1 sub-axis closure (dimsparse3 M_c rescue), R1-R5 filed cheapest-first. 0 portfolio row closures.
- PROT-007: v455 history row appended to substrate_capability_map_history.md.
- PROT-008: 1 sub-property extension (fact_checked_khop per-hop localization); 0 row state changes requiring validator. Annotation-only + LVH #236. PROT-008 validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 367th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of the 6 anchors. CLEAN.
- PROT-021: All 6 source=remote run_mode=full. No smoke contamination.
- PROT-022: hierarchical_hadamard alpha identical across seeds (discrete optimization); multi_head spread 2.00-2.75x all above HP threshold -- not fragile.

Cap_map: v454 -> v455 CYCLE 133 (1 HP-full: fact_checked_khop-3SEED-KHOP-K2-K5-1.000-FABRICATION-AUC-1.000-PER-HOP-LOCALIZATION; 1 HP-full-LVH235-RESOLVED: multi_head_sparse_key_M2-3SEED-H2/H1-2.25x-SUPER-SQRT-M; 2 MID: hierarchical_hadamard_then_sparse_key-LVH236-1.00x-NO-COMPOUNDING + cs1_dt_algebraic_audit-DT-BOUNDARY-EXTREME-SPARSITY-ONLY; 1 MID-ANNOTATION: sparse_key_composition_battery-INDEP-MASK-PARITY-FLAT-JOINT-MASK-DESTROYS; 1 HF-full-CONFIRMED: dimsparse3_alpha_at_mc-3SEED-SPARSE-KEY-Mc-2-vs-12-M_c-RESCUE-AXIS-CLOSED; 1 LVH #236: hierarchical_hadamard 1.0-1.2x-RANGE-OVERCLAIM-HONEST-1.00x; LVH 235->236 +1; HONEST 998->1003 +5; Portfolio 32+79 UNCHANGED; per-hop-fabrication-localization sub-property added to K-hop row; M_c-sparse-key rescue closed R1-R5 filed; 367th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v455 -> v456 CYCLE 134 BATCH (2026-06-06)

Verdicts processed: fact_checked_khop_confidence_weighted_v1 (MIDDLE_BAND) + fact_checked_khop_middle_hop_localization_v1 (HARD_PASS) + hierarchical_vq_plus_sparse_key_v1 (HARD_PASS) + crt_multi_scale_grid_cell_composition_v1 (HP-SMOKE LVH#237)

### Step 0 honest re-read (MANDATORY)

**(1) fact_checked_khop_confidence_weighted_v1 MIDDLE_BAND -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=8192, K={5,10,20}.
Per-cell: ALL seeds (7,17,23) x ALL K-cells: binary_AUC=1.000, best_conf_AUC=1.000, lift=+0.000 (exact zero, no variance).
Verdict_msg 'confidence ~ binary (no clear lift)' accurate: substrate binary discrimination is already at ceiling (1.000); confidence-weighted scoring adds zero marginal lift. MIDDLE_BAND honest -- not HF (binary works), not HP (confidence adds nothing). HONEST. +1 HONEST (1003->1004). No LVH.

**(2) fact_checked_khop_middle_hop_localization_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=8192, K={3,5}.
Per-seed: ALL seeds (7,17,23) ALL K-hop positions (K3: h0/h1/h2 + K5: h0/h2/h4): localization=1.000. middle_hop_loc=1.000 unanimous.
HP threshold >=0.85. Cleared at 1.000 on ALL cells. The hardest case (middle-hop) passes at ceiling. 'production gate clears, forward-only K-hop deployable' claim accurate. HONEST. +1 HONEST (1004->1005). No LVH.

**(3) hierarchical_vq_plus_sparse_key_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=3. N=4096.
Per-seed: ALL seeds (7,17,23): alpha B1=1.0, B8=8.0, B64=8.0 (tight unanimous across all seeds).
best_hier/flat-sparse=8.00x >= 4x HP threshold. Pipeline composition (dense M_c + sparse-KEY retrieval) gives 8x vs sparse-alone, all 3 seeds identical. Bank capacities add cleanly. HP label accurate. HONEST. +1 HONEST (1005->1006). No LVH.

**(4) crt_multi_scale_grid_cell_composition_v1 HARD_PASS -- LVH #237 (HP-SMOKE)**
source=LOCAL (no _source field from bridge; metrics from data/exp_crt_multi_scale_grid_cell_composition_v1/metrics.json). run_mode=SMOKE. n_seeds=1.
Per-seed (seed=1): single=7, two_scale=77, three_scale=1001 (CRT product=7*11*13=1001), ratio_3_vs_1=143.0x.
LABEL OVER-CLAIMS. HARD_PASS on smoke n=1 violates PROT-021. The CRT product matching is mathematically extraordinary (143x, exact modular product), but single-seed smoke does not meet multi-seed full protocol for HARD_PASS. Directional signal is extremely strong and theoretically principled (CRT exact match). Metrics source=LOCAL -- potential pre-ship smoke artifact locally staged; bridge had no remote data.
LVH #237: (a) label HARD_PASS; (b) honest: HP-SMOKE -- multiplicative CRT composition confirmed at single seed with exact product match, but requires 3-seed full run per PROT-021; metrics source=LOCAL adds additional uncertainty; (c) contradicting cells: run_mode=smoke n_seeds=1, PROT-021 multi-seed not met.
HONEST. +1 HONEST (1006->1007). LVH 236->237 (+1).

HONEST: 1003 -> 1007 (+4). LVH: 236 -> 237 (+1: crt_multi_scale HP-SMOKE PROT-021-violation + LOCAL source).

### Cap_map decisions (v455 -> v456)

**(1) fact_checked_khop_confidence_weighted_v1 MIDDLE_BAND**
K-hop + KF-1 fabrication-detection sub-property annotation. Extension of v455 fact_checked_khop HP.
Binary discrimination at ceiling (AUC=1.000); confidence-weighted scoring adds zero additional signal at N=8192. Interpretation: substrate HD similarity scores are already maximally discriminative for binary fabrication -- confidence weighting is redundant when binary signal is perfect. At lower N or harder tasks, confidence weighting may add lift; this is an N=8192 K<=20 saturation result.
Cap_map: fact-checked K-hop sub-property annotation -- 'confidence weighting redundant at binary-ceiling regime (N=8192); binary AUC=1.000 sufficient'. No band-lift.

Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): MIDDLE_BAND is the operating-regime boundary -- confidence weighting adds lift only when binary signal is non-ceiling. At N=8192 binary is already perfect; test at lower N or larger K where binary signal degrades.
R2 (CHEAP, CPU <30min): Test confidence weighting at N=1024/2048 where binary AUC may be sub-ceiling -- expected regime for confidence lift.
R3 (CHEAP, CPU <30min): Synthetic adversarial regime (noise-added facts, partial K-hop chains) to find operating point where confidence weighting provides real discrimination.

**(2) fact_checked_khop_middle_hop_localization_v1 HARD_PASS**
K-hop + KF-1 sub-property extension. Middle-hop fabrication localization: substrate pinpoints WHICH intermediate hop introduced a hallucination. Unanimous 1.000 across all hop positions K={3,5} 3-seed full.
Extends v455 fact_checked_khop per-hop localization sub-property with explicit middle-hop targeted probe. Confirms substrate can audit its own multi-step reasoning chain at the hop level -- differentiating vs frontier LLMs that cannot localize chain-of-thought errors. Production gate clears; forward-only K-hop deployable.
Cap_map: K-hop row sub-property -- 'middle-hop fabrication localization at 1.000 3-seed full (K={3,5}, all hop positions); production-gate passes'. Convergent evidence with v455 fabrication_flag_auc=1.000.

**(3) hierarchical_vq_plus_sparse_key_v1 HARD_PASS**
GENUINELY NEW pipeline architecture: dense M_c (hierarchical VQ) + sparse-KEY retrieval as two separate stages. Validates cycle-133 R2 rescue from dimsparse3 HARD_FAIL ('dense M_c + sparse-KEY retrieval head -- orthogonal pipeline stages').
Key finding: 8.00x lift over flat-sparse-KEY-alone (alpha B8=8.0, B64=8.0 vs B1=1.0, unanimous 3-seed). Bank capacities ADD when staged as pipeline -- composition works when two mechanisms are orthogonalized into pipeline stages rather than mixed in-place.
Closes cycle-133 R2 rescue hypothesis affirmatively. PP-8 sparse-KEY pipeline composition sub-property: HARD_PASS 3-seed full.
Cap_map: PP-8 annotation -- 'hierarchical VQ + sparse-KEY as staged pipeline: 8.00x over sparse-alone, 3-seed full. Cycle-133 R2 rescue confirmed. Dense-M_c stage + sparse-KEY retrieval head: bank capacities add cleanly. Mechanism: staging preserves orthogonality; in-place mixing (cycle-132/133) destroys capacity.' PROT-008: new sub-property on existing PP-8 row; band-lift deferred pending wider N confirmation.

**(4) crt_multi_scale_grid_cell_composition_v1 [LVH #237 honest: HP-SMOKE]**
GENUINELY NEW: CRT multi-scale grid-cell composition. Novel neuroscience-inspired probe -- replicates grid-cell multi-scale positional encoding via Chinese Remainder Theorem modular arithmetic in HD vectors.
Source=LOCAL smoke artifact (remote bridge had no data). HP-SMOKE annotation only. Run_mode=smoke n_seeds=1.
Signal: three_scale=1001 = CRT product (7*11*13=1001), 3/1=143x. Algebraically deterministic -- CRT theorem guarantees multiplicative capacity given coprime moduli; result is exact not approximate. Confidence in mechanism is very high despite single-seed; however PROT-021 requires multi-seed full.
Cap_map: provisional annotation -- 'CRT multi-scale grid-cell composition: HP-SMOKE (n=1, LOCAL source); 3-scale CRT product exact (1001=7*11*13); 143x capacity over single-scale. Algebraically deterministic; mechanism fully principled. Full run needed for HARD_PASS row entry.' PROT-008: not triggered (HP-SMOKE provisional; no band-lift).

Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): CRT theorem guarantees multiplicative capacity given coprime moduli; algebraically deterministic result. n=1 smoke theoretically sufficient for mechanism validation but PROT-021 multi-seed required for HARD_PASS.
R2 (CHEAP, CPU <30min): 3-seed full run at N=2048 to meet PROT-021 and convert HP-SMOKE to HARD_PASS.
R3 (CHEAP, CPU <30min): N-sweep to characterize minimum N for 4-scale, 5-scale CRT extensions.
R4 (CHEAP, CPU <30min): Cross-moduli families (Mersenne primes, Fermat primes) to verify CRT product capacity is moduli-family-agnostic.
R5 (MEDIUM, CPU <2h): CRT-grid-cell + sparse-KEY pipeline (analogous to hierarchical_vq_plus_sparse_key) -- multiplicative CRT capacity as the dense stage + sparse-KEY retrieval head.

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.
Note: hierarchical_vq_plus_sparse_key HP and CRT HP-SMOKE are sub-axis sub-property expansions of existing PP-8 and K-hop rows. Band-lift deferred for hierarchical_vq (wider N needed) and CRT (3-seed full needed).

### PROT compliance (v455 -> v456)
- PROT-004/006: No closures. Rescues filed cheapest-first: anchor 1 (3 rescues R1-R3). Anchor 4/CRT (5 rescues R1-R5).
- PROT-007: v456 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only + new sub-property (hierarchical_vq pipeline 8x). 0 row state changes. 0 band-lifts. Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 368th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of the 4 anchors. CLEAN.
- PROT-021: Anchors 1,2,3 source=remote run_mode=full n_seeds=3. CLEAN. Anchor 4 source=LOCAL run_mode=smoke n_seeds=1. LVH #237 filed; HP-SMOKE only.
- PROT-022: Anchors 1,2,3 3-seed deterministic (zero variance on all cells). Anchor 4 n=1 smoke; CRT is algebraically deterministic. No HP-fragility.

Cap_map: v455 -> v456 CYCLE 134 (1 HP-full: fact_checked_khop_middle_hop_localization-3SEED-MIDDLE-HOP-1.000-PRODUCTION-GATE-CLEARS; 1 HP-full: hierarchical_vq_plus_sparse_key-3SEED-DENSE-Mc+SPARSE-KEY-PIPELINE-8.00x-CYCLE133-R2-RESCUE-CONFIRMED; 1 MID: fact_checked_khop_confidence_weighted-3SEED-BINARY-CEILING-CONF-LIFT-ZERO; 1 HP-SMOKE-LVH#237: crt_multi_scale_grid_cell-SMOKE-LOCAL-CRT-EXACT-143x-ALGEBRAIC; LVH 236->237 +1; HONEST 1003->1007 +4; Portfolio 32+79 UNCHANGED; annotation-only; 368th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## CYCLE 135 -- v456 -> v456 (2026-06-06) -- NO VERSION BUMP

Verdicts processed: 2 (sparse_key_composition_battery_gpu_v1 DUPLICATE + multi_head_x_sparsity_battery_gpu_v1 SMOKE-NEW)

### Step 0 honest re-read (MANDATORY)

**(1) sparse_key_composition_battery_gpu_v1 MIDDLE_BAND -- HONEST + DUPLICATE**
source=remote run_mode=full n_seeds=3. N={4096,8192,16384} 3-seed.
Per-arm means: flat_sparse=0.4833 (range 0.45-0.60), hadamard=0.1499, hadamard_indep_mask=0.4666 (range 0.45-0.60), block_sparse=0.0466 (range 0.02-0.05).
verdict_msg uses minimums (0.45/0.45) for flat/indep ratio => reports hadamard_indep/best=1.00; mean-based ratio is 0.4666/0.4833=0.965 (indep slightly below flat at mean). 3.5% difference -- conservative use of minima, not over-claim. HONEST.
DUPLICATE: cycle 133 v455 already fully processed this anchor at 3-seed full with identical findings. cap_map annotation 'design principle locked: independent masks' ALREADY applied at v455. No new cap_map action.
HONEST: 1007 UNCHANGED (already counted in cycle 133). LVH: UNCHANGED.

**(2) multi_head_x_sparsity_battery_gpu_v1 MIDDLE_BAND -- [label-vs-honest] LVH #238**
source=remote run_mode=SMOKE n_seeds=1. elapsed=1.03s. N=2048, seed=1 only.
Per-cell: H=1 f=0.05: 0.1997; H=1 f=0.10: 0.0996 (ref); H=2 f=0.05: 0.3999 (best); H=2 f=0.10: 0.1997.
verdict_msg best/ref=4.01x uses cross-f comparison (H=2,f=0.05 vs H=1,f=0.10). NUMBER CORRECT.
Honest re-read: iso-f H-effect = H=2,f=0.10 / H=1,f=0.10 = 0.1997/0.0996 = 2.00x; H=2,f=0.05 / H=1,f=0.05 = 0.3999/0.1997 = 2.00x. Iso-H f-effect = H=1,f=0.05 / H=1,f=0.10 = 0.1997/0.0996 = 2.00x. Cross-factor product = 2.00 * 2.00 = 4.00 = observed 4.01x. H and f effects are MULTIPLICATIVELY INDEPENDENT -- no supra-linear composition.
LVH #238: (a) label: 'partial compounding (2-5x) best/ref=4.01x' implies composition benefit beyond independent effects; (b) honest: H-effect and f-effect independently 2.00x each and multiply; 4.01x = product of independent effects, NOT supra-multiplicative composition; no new composition capability; (c) contradicting cells: H=2,f=0.10 / H=1,f=0.10 = 2.00x = H=2,f=0.05 / H=1,f=0.05 = 2.00x -- H-effect is f-invariant, confirms independence.
Honest verdict: MIDDLE_BAND retained (4.01x within [2,5] band); COMPOSITION framing corrected to INDEPENDENCE.
NOTE: SMOKE n=1 flag. Full 3-seed at N=4096 required before any design decisions.
LVH #238. HONEST: 1007 -> 1008 (+1). LVH: 237 -> 238 (+1).

### Cap_map decisions

**(1) sparse_key_composition_battery_gpu_v1 -- DUPLICATE, NO CAP_MAP ACTION**
Cycle 133 v455 already applied: PP-8 sparse-KEY independent-mask design principle annotation. Data identical. No redundant annotation. HONEST count not incremented (already tallied in cycle 133).

**(2) multi_head_x_sparsity_battery_gpu_v1 [LVH #238 honest: INDEPENDENCE not COMPOSITION] -- PP-8 annotation**
PP-8 multi-head x sparsity composition sub-axis. SMOKE n=1 at N=2048.
Finding: H-effect and f-effect are MULTIPLICATIVELY INDEPENDENT (each 2.00x, product = 4.00x = observed 4.01x). No supra-linear composition. Multi-head scaling and sparsity scaling are orthogonal independent levers combinable multiplicatively -- useful for product design but does NOT demonstrate a new composition capability beyond what cycle 133 multi_head_M2 HP already showed.
Comparison to cycle 133 multi_head_M2 HP (H2/H1=2.25x super-sqrt at N=4096 3-seed): that finding holds. The current anchor adds: sparsity does not interfere with or amplify the H-effect; effects are cleanly separable.
PP-8 annotation: 'multi_head_x_sparsity SMOKE-n1 v456: H-effect and f-effect independently ~2.00x each; combine multiplicatively (4x total); no supra-linear composition; SMOKE flag -- full 3-seed at N=4096 required.'
Band UNCHANGED. Smoke flag on all design conclusions.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])
R1 (CHEAP, CPU/GPU <30min): Full 3-seed at N=4096 with H={1,2,4} x f={0.05,0.10,0.20} grid to confirm independence pattern and characterize H=4 scaling.
R2 (CHEAP, CPU <30min): Iso-f H={1,2,4} sweep at N={4096,16384} to verify H-scaling exponent (cycle 133 found 2.25x at N=4096 3-seed; this smoke at N=2048 gives 2.00x -- possible N-dependence worth checking).
R3 (MEDIUM, GPU <2h): H={1,2,4,8} x f={0.05,0.10,0.20} full 3-seed envelope at N=16384 to characterize product-space scaling law at production scale.

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v456 UNCHANGED -- annotation-only, no version bump)
- PROT-004/006: No closures. multi_head_x_sparsity: 3 rescues cheapest-first.
- PROT-007: No version bump (annotation-only + duplicate). History note only.
- PROT-008: Annotation-only; 0 row state changes. Validator not triggered.
- PROT-009: Decisions log appended; no cap_map .md state change (duplicate + annotation). No atomic commit needed; push NOT required.
- PROT-018: No _nN suffixes on either anchor. CLEAN.
- PROT-021: sparse_key source=remote run_mode=full n_seeds=3 (DUPLICATE -- cycle 133 already processed). multi_head source=remote run_mode=smoke n_seeds=1. Smoke design conclusions deferred pending full 3-seed.
- PROT-022: sparse_key 3-seed normal variance. multi_head smoke n=1 -- no HP-fragility assessment possible. SMOKE flag on all multi_head conclusions.

Cap_map: v456 UNCHANGED CYCLE 135 (1 DUPLICATE: sparse_key_battery already-annotated-v455-NO-ACTION; 1 MID-SMOKE-LVH#238: multi_head_x_sparsity-INDEPENDENCE-not-COMPOSITION-H-effect-2x-f-effect-2x-product-4x-SMOKE-n1; LVH 237->238 +1; HONEST 1007->1008 +1; Portfolio 32+79 UNCHANGED; NO VERSION BUMP; push NOT required) (2026-06-06)

## v456 -> v457 CYCLE 136 BATCH (2026-06-06)

Verdicts processed: substrate_pca_prewhitening_codebook_v1 (HARD_PASS label -- PCA pre-whitening Phase-4A unblock candidate) + substrate_etf_minilm_M_star_cross_N_v1 (HARD_PASS label -- M_star cross-N whitening benefit grows with N_sub)

### Step 0 honest re-read (MANDATORY)

**(1) substrate_pca_prewhitening_codebook_v1 HARD_PASS -- [label-vs-honest] LVH #239**
source=remote run_mode=smoke n_seeds=1. N=384 real MiniLM keys.
Per-cell (seed1 only): cap_unwhitened=3, cap_pca_whitened=11, ratio=3.67x.
LABEL OVER-CLAIMS. smoke n_seeds=1 violates PROT-021 multi-seed requirement. ratio=3.67x clears >=2x threshold on single seed, but single-seed smoke is not sufficient for HARD_PASS per PROT-021.
LVH #239: (a) label: HARD_PASS; (b) honest: HP-SMOKE -- ratio=3.67x genuine on n=1 seed; 3-seed full required for HARD_PASS; (c) contradicting cells: run_mode=smoke n_seeds=1 (PROT-021 not met).
Context: CRITICAL Phase-4A unblock. ZCA HARD_FAIL all-zeros cycle 130 regression. PCA as alternative is exactly rescue R4 from cycle-126 LVH #228 and rescue R3 from cycle-130. 3.67x on single seed is directionally strong and mechanistically principled.
Honest verdict: HP-SMOKE. +1 HONEST (1008->1009). LVH 238->239 (+1).

**(2) substrate_etf_minilm_M_star_cross_N_v1 HARD_PASS -- [label-vs-honest] LVH #240**
source=remote run_mode=smoke n_seeds=1. N_sub={384,768} MiniLM.
Per-cell (seed1 only): N384={m50_raw=8, m50_whitened=32, ratio=4.0x}; N768={m50_raw=8, m50_whitened=48, ratio=6.0x}. slope(vs logN)=2.89.
LABEL OVER-CLAIMS. smoke n_seeds=1 violates PROT-021. Ratios 4.0x and 6.0x both clear threshold at single seed; growing-with-N_sub directional finding clear.
LVH #240: (a) label: HARD_PASS (H2); (b) honest: HP-SMOKE -- both N-cells clear threshold at n=1; 3-seed full required for HARD_PASS; (c) contradicting cells: run_mode=smoke n_seeds=1 (PROT-021 not met).
Context: RESOLVES cycles 119/122/125/130 ETF cross-N attenuation question. Prior apparent attenuation was ceiling artifacts (raw_recall at ceiling, not degraded whitening). M_50 metric avoids ceiling artifact by measuring capacity at 50th-percentile recall. M_50 growing with N_sub confirms whitening increasingly mandatory at scale (Hadamard/intrinsic-dim saturation mechanism).
Honest verdict: HP-SMOKE. +1 HONEST (1009->1010). LVH 239->240 (+1).

HONEST: 1008 -> 1010 (+2). LVH: 238 -> 240 (+2: LVH #239 pca_prewhitening + LVH #240 etf_minilm_M_star).

### Cap_map decisions (v456 -> v457)

**(1) substrate_pca_prewhitening_codebook_v1 [LVH #239 honest: HP-SMOKE; ratio=3.67x smoke-n=1]**
PP-8 Phase-4A rescue sub-property annotation. HP-SMOKE.
Key finding: PCA whitening gives 3.67x capacity lift vs unwhitened (cap=11 vs 3) on MiniLM N=384 single seed.
CRITICAL CONTEXT: Phase-4A unblock candidate. ZCA HARD_FAIL all-zeros at cycle 130 (regression). PCA recommended by cycle-126 R4 and cycle-130 R3. PCA avoids ZCA numerics instability (eigenvectors directly, no zero-divisor risk). 3.67x clears HP band (>=2x).
Phase-4A status: ZCA BLOCKED; PCA HP-SMOKE (single seed). Phase-4A unblock deferred pending 3-seed full PCA confirmation.
PP-8 Phase-4A sub-property annotation: 'PCA whitening HP-SMOKE v457: ratio=3.67x n=1 remote; ZCA HARD_FAIL regression stands; PCA is active Phase-4A unblock path; 3-seed full required before Phase-4A plan update.'
Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): HP-SMOKE consistent with rescue recommendation. Phase-4A path = PCA as ZCA-alternative.
R2 (CHEAP, CPU <30min): 3-seed full PCA whitening at N_sub=384 to convert HP-SMOKE to HARD_PASS and formally unblock Phase-4A.
R3 (CHEAP, CPU <30min): PCA vs ZCA comparison at N_sub=384 with patched ZCA -- compare stability; PCA expected to win on degenerate seeds.
R4 (CHEAP, CPU <30min): PCA N_sub sweep {384,512,768,1024} to characterize Phase-4A capacity curve with stable whitening.
PP-8 Phase-4A: ZCA blocked, PCA HP-SMOKE active. Band UNCHANGED.

**(2) substrate_etf_minilm_M_star_cross_N_v1 [LVH #240 honest: HP-SMOKE; N384=4.0x N768=6.0x grows]**
PP-8 ETF/whitening cross-N sub-axis. HP-SMOKE annotation (smoke n=1; 2 N-cells).
Key finding: M_50 (whitened/raw capacity ratio) GROWS with N_sub -- N384=4.0x, N768=6.0x, slope=2.89 vs logN.
RESOLVES cycles 119/122/125/130 cross-N attenuation: prior apparent attenuation was ceiling artifact (recall at ceiling pre-whitening); M_50 metric measures true capacity avoiding ceiling bias. Mechanism: Hadamard/intrinsic-dim saturation -- at larger N_sub raw encoder fills more dimensions near d_eff ceiling faster, whitening lifts proportionally more.
PP-8 ETF cross-N annotation: 'M_star_cross_N HP-SMOKE v457: M_50 N384=4.0x N768=6.0x slope=2.89; whitening benefit GROWS with N_sub; prior attenuation was ceiling artifact; cross-N attenuation RESOLVED; 3-seed full required for HARD_PASS.'
Rescue sketches (PROT-004/006; cheapest-first):
R1 (0-compute, ANNOTATION): Cross-N attenuation resolved as ceiling artifact. M_50 metric correct for N-scaling characterization.
R2 (CHEAP, CPU <30min): 3-seed full at N_sub={384,768} to confirm slope=2.89 with statistical confidence.
R3 (CHEAP, CPU <30min): N_sub sweep {384,512,768,1024} single-seed to characterize slope over wider range.
R4 (CHEAP, CPU <30min): M_star measurement for bge-large (D=1024, d_eff=114.8) -- higher d_eff expected to give higher M_50 ratio and steeper slope.
PP-8 ETF cross-N: HP-SMOKE; band UNCHANGED; cross-N attenuation RESOLVED (ceiling artifact).

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v456 -> v457)
- PROT-004/006: No closures. Anchor 1: R1-R4 cheapest-first. Anchor 2: R1-R4 cheapest-first.
- PROT-007: v457 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 band-lifts; HP-SMOKE not triggering validator.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 369th PROT-009 paired commit.
- PROT-018: No _nN suffixes on either anchor. CLEAN.
- PROT-021: Both source=remote run_mode=smoke n_seeds=1. LVH #239+#240 filed; HP-SMOKE only; no HARD_PASS committed to cap_map.
- PROT-022: Both n_seeds=1 smoke; HP-fragility not evaluable. Mechanism (PCA decorrelation, M_50 monotone) principled.

Cap_map: v456 -> v457 CYCLE 136 (0 HP; 2 HP-SMOKE-LVH [#239 pca_prewhitening-SMOKE-3.67x-ZCA-ALT-PHASE4A-UNBLOCK-CANDIDATE + #240 etf_minilm_M_star-SMOKE-N384=4.0x-N768=6.0x-GROWS-CROSS-N-RESOLVED]; 0 MID; 0 HF; LVH 238->240 +2; HONEST 1008->1010 +2; Portfolio 32+79 UNCHANGED; Phase-4A ZCA-blocked PCA-HP-SMOKE active; ETF cross-N attenuation resolved ceiling-artifact; 369th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v457 -> v458 CYCLE 137 BATCH (2026-06-06)

Verdicts processed: fact_checked_khop_merkle_chain_hp12_root_v1 (HARD_PASS) + fact_checked_khop_kscaling_battery_v1 (HARD_PASS) + multi_head_x_corruption_battery_gpu_v1 (HARD_FAIL)

### Step 0 honest re-read (MANDATORY)

**(1) fact_checked_khop_merkle_chain_hp12_root_v1 HARD_PASS -- HONEST (PROT-021 flag: n_seeds=1)**
source=remote run_mode=full n_seeds=1. K={3,5,10,20}: roundtrip_ms={0.0107, 0.0165, 0.0291, 0.0507} all valid=True. Pre-reg HP: <1ms at K=20 valid=True -- CLEARED (0.0507ms << 1ms). Core claim is deterministic (Merkle chain build+verify is cryptographic; 1 seed sufficient). PROT-021 flag noted: n_seeds=1 for a certification benchmark; cryptographic validity is not stochastic -- HP label honest for this class of test. No LVH.
HONEST. +1 HONEST (1010->1011).

**(2) fact_checked_khop_kscaling_battery_v1 HARD_PASS -- LABEL HONEST**
source=remote run_mode=full n_seeds=5. 5 seeds x K={3,5,8,10,15,20}: ALL conf_auc=1.000, binary_auc=1.000, localization=1.000. Pre-reg HP: detection + localization survive K=20 -- CLEARED unanimously 5/5 seeds all 6 K-cells (30 cells, 30/30 ceiling). Strongest confirmation in K-hop battery. No LVH.
HONEST. +1 HONEST (1011->1012).

**(3) multi_head_x_corruption_battery_gpu_v1 HARD_FAIL -- LABEL HONEST (smoke flag)**
source=remote run_mode=smoke n_seeds=1. flip=0.05: H1=0.200, H4=0.700 (H4/H1=3.5x -- advantage preserved at low corruption). flip=0.45: H1=0.000, H4=0.000 (both collapse, H4/H1 undefined). HARD_FAIL label honest: production-robustness claim fails (high corruption erases advantage). Nuance: flip=0.05 cell confirms v455 multi-head advantage valid in benign regime. smoke n_seeds=1; mechanistic collapse at flip=0.45 robust (both zero). No LVH.
HONEST. +1 HONEST (1012->1013).

HONEST: 1010 -> 1013 (+3). LVH: 240 UNCHANGED.

### Cap_map decisions (v457 -> v458)

**(1) fact_checked_khop_merkle_chain_hp12_root_v1 HARD_PASS**
K-hop + KF-1 + HP-12 sub-property composition annotation.
Key finding: Merkle chain builds and verifies at K=20 in 0.051ms end-to-end. Valid=True all K. Combines three audited capabilities (HP-12 V2 crypto root + K-hop reasoning + per-hop fact-checked localization) into a single cryptographically anchored audit chain. COMPOSITION milestone: each individual capability was HP; composition at K=20 depth verified at <1ms threshold. No frontier equivalent for cryptographic reasoning-chain certification. Deterministic test; n=1 sufficient.
Cap_map annotation on K-hop row: 'Merkle-chain-cert HP n=1 v458: K=20 roundtrip=0.051ms valid=True; composition HP-12+K-hop+KF-1; production-grade cryptographic audit chain; cross-ref HP-12 row and KF-1 row.'
Portfolio 32+79 UNCHANGED (sub-property extension; no new row).

**(2) fact_checked_khop_kscaling_battery_v1 HARD_PASS -- PRODUCTION-GRADE DESIGNATION**
K-hop + KF-1 row band annotation.
Key finding: 5-seed x 6-K battery at N=8192; fabrication detection AND per-hop localization both 1.000 unanimous across all 30 cells (K={3,5,8,10,15,20}). Extends v455 3-seed K={2-5} and v456 middle-hop HP to 5-seed K={3..20} depth. PROT-008 validator: consecutive HPs at increasing K and seed count; monotone confirmed. Sub-property annotation: production-grade designation for fact-checked K-hop at K=20 depth.
Cap_map annotation on K-hop/KF-1 row: 'khop_kscaling_battery HP 5-seed K=20 v458: all-ceiling 30/30 cells; PRODUCTION-READY designation; fabrication localization at any hop position through K=20; extends v455+v456 HPs.'
Portfolio 32+79 UNCHANGED (annotation-only; existing row).

**(3) multi_head_x_corruption_battery_gpu_v1 HARD_FAIL (smoke)**
Multi-head robustness sub-axis annotation. Extension of v455 multi-head M2 HP.
Key finding: High-corruption (flip=0.45) collapses both H1 and H4 capacity to zero -- corruption saturation is the floor, head count irrelevant past saturation. Low-corruption (flip=0.05): H4/H1=3.5x advantage preserved (confirms v455 M2 HP in benign regime). Production envelope: multi-head advantage valid only for flip below saturation floor (~0.20 estimated). This narrows the deployment envelope; does NOT refute multi-head.
Cap_map annotation on multi-head row: 'multi_head_x_corruption HF smoke v458: flip=0.45 saturation (H1=H4=0); flip=0.05 H4/H1=3.5x preserved; production envelope flip<0.20; smoke n=1 -- full flip-sweep needed.'

Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):
R1 (0-compute, SUBSUMPTION): Multi-head M2 advantage (v455 HP) valid for flip<~0.20 regime; production deployment in low-corruption environments unaffected. Scope narrows, does not close.
R2 (CHEAP, CPU <30min): flip sweep {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.45} to characterize saturation threshold (crossover point where H4/H1 drops below 1.3x).
R3 (CHEAP, CPU <30min): Corruption-aware retrieval using fact-checked K-hop confidence scores to downweight high-corruption hops pre-extraction.
R4 (CHEAP, CPU <30min): Redundant-key encoding -- bind each fact with multiple independent key vectors to improve resilience under high flip rates.
R5 (MEDIUM, GPU <2h): Iterative cleanup pass (multi-round binding+unbinding) to rescue retrieval at flip=0.30-0.45 using v455 sparse-key independence.

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v457 -> v458)
- PROT-004/006: No row closures. Anchor 3 HF: 5 rescues cheapest-first. R1 subsumption applied.
- PROT-007: v458 history row appended to substrate_capability_map_history.md.
- PROT-008: Anchor 2 K-hop production-grade annotation; consecutive HPs at increasing K+seeds; monotone confirmed; validator PASS. Anchor 1 sub-property composition annotation. Anchor 3 annotation-only HF. No row state regression.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 370th PROT-009 paired commit.
- PROT-018: No _nN suffixes on any of the 3 anchors. CLEAN.
- PROT-021: Anchor 1 n_seeds=1 crypto-deterministic (HP honest; not stochastic); Anchor 2 n_seeds=5 full (multi-seed strongest); Anchor 3 n_seeds=1 smoke (HF mechanistic robust; collapse at zero). CLEAN per class.
- PROT-022: Anchor 1 crypto-deterministic; Anchor 2 5-seed ceiling consensus (no HP-fragility); Anchor 3 smoke n=1 (collapse mechanistic, not stochastic noise).

Cap_map: v457 -> v458 CYCLE 137 (2 HP: merkle_chain_cert-K20-0.051ms-VALID-CRYPTO-COMPOSITION-HP12+KHOP+KF1 + khop_kscaling_battery-5SEED-K20-ALL-CEILING-PRODUCTION-READY; 1 HF-SMOKE: multi_head_x_corruption-FLIP0.45-SATURATION-BOTH-ZERO-FLIP0.05-3.5x-PRESERVED; 0 LVH; K-hop/KF-1 PRODUCTION-GRADE K=20 5-seed annotation; HONEST 1010->1013 +3; LVH 240 UNCHANGED; Portfolio 32+79 UNCHANGED; 370th PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

---

## v458 -> v459 -- CYCLE 138 (2 verdicts: HARD_PASS + LVH #241 HARD_PASS->MIDDLE_BAND; HONEST 1013->1015; LVH 240->241)

### Step 0 -- Honest re-reads

**(1) substrate_last_token_vs_whitening_mean_pool_v1 HARD_PASS -- LABEL HONEST**
source=remote n_seeds=3. Per-cell: seed7=seed17=seed23 identical (deterministic PCA whitening). cap: last_token_raw=0, mean_pool_whiten=40, last_token_whiten=122. combined/best_single=122/40=3.05x >> 1.2x HP threshold. Label 'COMPLEMENTARY (combined >=1.2x best single)' honest. Key nuance: last_token_raw=0 (whitening mandatory; last-token pooling adds nothing without whitening). last_token_whiten IS the combined recipe (last-token + whitening = 122). No over-claim. NO LVH.
HONEST. +1 HONEST (1013->1014).

**(2) substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1 LVH #241 HARD_PASS -> MIDDLE_BAND**
source=remote n_seeds=3. Per-cell: seed7=seed17=seed23 identical. cap: base_raw=3, whiten_only=7, expand_only=0, expand_whiten=7. CRITICAL: expand_only=0 (dim-expansion ALONE collapses to ZERO capacity at n_enc=10000). expand_whiten=7 = whiten_only=7 (expand adds ZERO marginal capacity on top of whitening). Reported ratio 7e9x is division-by-zero artifact (7/0), not an empirical measurement. LVH #241: HARD_PASS label 'stacking holds / production rule = expand + whiten' is FALSE -- no stacking benefit exists (expand+whiten = whiten_only). Honest finding: whitening subsumes dim-expansion at n_enc=10000, not vice versa. Phase-4A PCA/whitening work is confirmed MANDATORY (not redundant). Dim-expansion is a NULL lever at n_enc=10000 when whitening is present. The pre-registered subsumption question is answered in the REVERSE direction: whitening subsumes dim-expansion.
LVH #241 filed. Honest reading: MIDDLE_BAND (whitening confirmed mandatory+sufficient; dim-expansion null at this scale). +1 HONEST (1014->1015). LVH 240->241.

HONEST: 1013 -> 1015 (+2). LVH: 240 -> 241 (+1 LVH #241).

### Cap_map decisions (v458 -> v459)

**(1) substrate_last_token_vs_whitening_mean_pool_v1 HARD_PASS**
Encoder recipe sub-property annotation on PP-8 / ETF-whitening design axis.
Key finding: Last-token pooling + whitening ('last_token_whiten=122') is 3.05x better than mean-pool + whitening alone (40). Raw last-token without whitening gives zero capacity. Production encoder recipe confirmed: last-token pooling + PCA whitening is the dominant design point. Whitening is a prerequisite (not optional). 3-seed unanimous (deterministic).
Cap_map annotation on PP-8 / ETF-whitening sub-property:
'last_token_vs_mean_pool HP v459: last_token_whiten=122 vs mean_pool_whiten=40 (3.05x); last_token_raw=0 (whitening mandatory); production encoder recipe = last-token + PCA whitening; 3-seed unanimous deterministic; 2026-06-06.'
Portfolio 32+79 UNCHANGED (sub-property annotation; no new row).

**(2) substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1 [LVH #241 -- honest: MIDDLE_BAND]**
Encoder recipe + ETF/whitening design axis sub-property annotation.
Key finding: At n_enc=10000, dim-expansion alone gives ZERO capacity. Whitening alone gives 7. Expand+whiten gives 7. Dim-expansion adds ZERO marginal benefit on top of whitening. The 7e9x ratio in the verdict_msg is a division-by-zero artifact (7/0), not a measurement. Honest reading: whitening SUBSUMES dim-expansion at this scale (not the reverse). Phase-4A PCA work is the load-bearing axis. Stacking does NOT hold at n_enc=10000.
LVH #241 entry: label 'stacking holds; production rule = expand + whiten' over-claims; honest = MIDDLE_BAND; expand_only=0 is the critical finding; 7e9x ratio is computational artifact not signal.
Cap_map annotation on ETF/whitening / dim-expansion sub-property:
'dim_expansion_subsumes_whitening [LVH #241] MIDDLE_BAND v459: n_enc=10000; expand_only=0 (ZERO capacity); whiten_only=7; expand_whiten=7 (no stacking); whitening SUBSUMES dim-expansion at n_enc=10000; Phase-4A PCA is load-bearing; dim-expansion is NULL lever when whitening present; 7e9x ratio is div/zero artifact; HARD_PASS label over-claims stacking; 2026-06-06.'

Rescue sketches for dim-expansion null finding (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]]):
R1 (0-compute, SUBSUMPTION): Phase-4A PCA/whitening work is confirmed as dominant and load-bearing. No design change needed. Dim-expansion null finding actually SIMPLIFIES the production recipe (whitening only; skip expansion).
R2 (CHEAP, CPU <30min): Test dim-expansion at smaller n_enc (n_enc=1000, 500) to find the scale where expand_only transitions from zero to non-zero. This characterizes the n_enc threshold for expansion utility.
R3 (CHEAP, CPU <30min): Test expand_only at larger N (N=8192, N=16384) to check if dim-expansion recovers at higher vector dimensionality. Zero at N_sub=default may be N-dependent.
R4 (CHEAP, CPU <30min): Test a different expansion strategy (e.g., random projection expansion vs learned PCA expansion) to determine if the zero is algorithm-specific or universal to dim-expansion at n_enc=10000.
R5 (MEDIUM, GPU <2h): Full sweep: n_enc x N x expansion_method 3-way grid to map the operating envelope where dim-expansion contributes marginal capacity beyond whitening alone.

### Portfolio: 32+79 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### PROT compliance (v458 -> v459)
- PROT-004/006: No row closures. Anchor 2 LVH #241: 5 rescues cheapest-first. R1 subsumption applied.
- PROT-007: v459 history row appended to substrate_capability_map_history.md.
- PROT-008: Both anchors annotation-only sub-property updates. No row state regression.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 371st PROT-009 paired commit.
- PROT-018: No _nN suffixes on either anchor. CLEAN.
- PROT-019: LVH #241 (dim_expansion_subsumes_whitening HARD_PASS -> MIDDLE_BAND) filed. Over-claimed label NOT applied to cap_map. Honest reading authoritative.
- PROT-021: Both anchors n_seeds=3 full runs; all 3 seeds identical (deterministic PCA whitening of fixed encoder geometry). CLEAN.
- PROT-022: Both anchors 3-seed consensus on identical cells -- deterministic; not stochastic noise. CLEAN.

Cap_map: v458 -> v459 CYCLE 138 [label-vs-honest LVH #241] (1 HP: last_token_vs_mean_pool-COMPLEMENTARY-3.05x-WHITENING-MANDATORY-LAST-TOKEN-RECIPE; 1 LVH #241: dim_expansion_subsumes_whitening-HARD_PASS->MIDDLE_BAND-expand_only=0-NO_STACKING-WHITENING_SUBSUMES_EXPANSION-7e9x-DIV-ZERO-ARTIFACT; 0 HF; 1 LVH; PP-8/ETF-whitening encoder-recipe annotations; HONEST 1013->1015 +2; LVH 240->241; Portfolio 32+79 UNCHANGED; 371st PROT-009 paired commit) (2026-06-06)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
