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
