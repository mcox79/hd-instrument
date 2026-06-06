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
