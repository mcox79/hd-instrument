# Pre-reg: DEEP from-scratch text encoder self-teacher (held-out-NEW concept)

- anchor: `deep_text_encoder_self_teacher_heldout_new_v1`
- cell: `experiments/exp_deep_text_encoder_self_teacher_heldout_new_v1.py`
- date: 2026-07-26
- author: hdi_exp_dev
- run: CPU-only, no GPU, no network at run time. seeds full=[7,13].

## Question
R3/R4 (MEASURED@data/exp_self_teacher_gloss_relational_predictive_heldout_new_v1/metrics.json)
showed the char-trigram gloss encoder is too shallow: the gloss arm added only +0.0070 over
RAW-GROUNDING (0.6431 vs 0.6361 same_lex_auc), and full self-teacher tied/lost raw grounding
(-0.0105). Does a DEEP from-scratch learned SEQUENCE text encoder (learned token embeddings + a small
Transformer, MLM-trained by masked-token PREDICTION) + MORE/LONGER text (gloss + WordNet examples +
mined UD-English-EWT sentences) extract more meaning and break the grounding ceiling on held-out-NEW
concepts?

## Invariants
TEACHER-FREE; NO borrowed vectors (token embeddings + Transformer learned FROM SCRATCH by MLM);
INDUCTIVE (held-out placed from its own text + grounding + TRAIN-neighbour context); LEAK-PROOF
(concept-level sha256 split; vocab-free hashed tokenizer = no fit; MLM trains on TRAIN text only;
WordNet lexname = EVAL-ONLY truth disjoint from all inputs/targets).

## Arms (ablation)
- ARM_RAW_GROUNDING  (ceiling), ARM_RAW_DEEPTEXT (deep-rep alone), ARM_CHARTRIGRAM_GLOSS (R3/R4 shallow),
  ARM_DEEP_TEXT (grounding+deep-text), ARM_FULL_FUSION (PRIMARY), ARM_RANDOM_INIT, ARM_COLLAPSE_SHUFFLE.

## THE ONE NUMBER + bands (applied to ARM_FULL_FUSION held-out SAME-LEXNAME AUC)
- THE NUMBER = FULL_FUSION same_lex_auc - RAW_GROUNDING same_lex_auc.
- HARD_PASS: margin >= +0.03 AND margin_min > 0 AND full >= 0.60 AND full >= random_init
  AND can_fail(collapse in [0.44,0.56]) AND raw_grounding >= 0.55 AND n_query >= 150.
- HARD_FAIL: collapse out of band OR raw_grounding < 0.55 OR full < 0.53 OR n_query < 150.
- MIDDLE_BAND: controls valid + full a real signal but margin < +0.03 = honest DEEPER/DATA-SCALE CEILING
  (deep text + more text still tie raw grounding). Reported plainly with corpus scale.
- KEY DEPTH ablation (reported, not a hard gate): DEEP_TEXT - CHARTRIGRAM_GLOSS (does depth > the +0.007 bag?).

## Eval fairness (kill the confound)
Relational-placement reported DEGREE-MATCHED (negatives drawn from TRAIN non-neighbours matched to the
positives' train-degree bins) AND random-neg for contrast (R3/R4 random-neg inflated to ~0.80).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (no sweep axis).
- arms_differ_verified: hash-test over 7 arm code matrices (META_RULE_AF) at seed end.
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except SystemExit: raise before except Exception (no BaseException / bare except; grep-clean).
- crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + random-init controls witness the floor.
- baseline_in_band: SMOKE MEASURED collapse=0.5125, raw_grounding=0.6407 (>0.55), full=0.6202 (not saturated).
- discriminator survives scale: FULL >=2 seeds; smoke previews THE NUMBER (below).
- calibration_check: default_ok_for_this_regime (AUC base analytic; controls witness empirically).
- start_marker_written / crash_diagnostic_present / heartbeat: start-marker + crash-metrics present.
  cell_chunked: false (seeds looped in one cell; per-seed write_partial checkpoints).
- real_code_path (F.1): deeptext_selftest() BUILDS the real DeepTextEncoder + runs MLM-pretrain at N=40
  tiny scale and asserts MLM loss drops + reps finite/distinct + tokenizer deterministic. F.2 N/A (no
  substrate KGStore/fit objects; self-contained jsonl reader + NLTK + torch).
- progress_logging: print_flush_true (MLM + fusion epoch logs; timeout < 30min so §17 not mandatory).

## SMOKE PREVIEW (MEASURED@data/exp_deep_text_encoder_self_teacher_heldout_new_v1_smoke/metrics.json)
cap=900, 1 seed, 34s. verdict=MIDDLE_BAND (deeper_ceiling=True).
- THE NUMBER full_fusion - raw = 0.6202 - 0.6407 = -0.0204 (LOSES; below +0.03 bar).
- DEPTH deep_text - chartrigram = 0.6452 - 0.6491 = -0.0039 (depth does NOT help).
- raw_deeptext alone = 0.5011 (near chance; 42k-token corpus barely trains the transformer).
- controls valid: collapse=0.5125 (can_fail), raw_signal_ok=True, n_q=179, arms differ.
- corpus: K=900, total_tokens=41,871, mean 46.5 tok/concept, mined 3.27 EWT-sents/concept, text_cov=1.0.
Interpretation (HYPOTHESIZED, to confirm at FULL): grounding is already the supersense ceiling; the
from-scratch transformer text encoder is data-starved (tiny corpus) -> honest data-scale ceiling.
FULL (cap=5000, 2 seeds, 140 MLM epochs, more mined text) confirms whether depth/scale changes this.

## FULL CONFIRMED (MEASURED@data/exp_deep_text_encoder_self_teacher_heldout_new_v1/metrics.json)
cap=5000, seeds=[7,13], 489s foreground-to-completion. verdict=MIDDLE_BAND (deeper_ceiling=True).
- THE NUMBER full_fusion - raw_grounding = 0.6240 - 0.6420 = -0.0180 (min=-0.0182). LOSES; below +0.03.
- DEPTH deep_text - chartrigram = 0.6406 - 0.6462 = -0.0056 (depth does NOT help; ties/loses the bag).
- raw_deeptext alone = 0.5191 (near chance -> from-scratch transformer data-starved).
- chartrigram +0.0042 over raw (matches R3/R4 +0.007 shallow ceiling); deep_text -0.0014 over raw.
- controls VALID: collapse=0.5014 (can_fail), raw=0.6420 (>0.55), n_q=1005, arms differ.
- full - random_init = -0.0004 (trained full fusion does NOT beat an untrained random-init on supersense).
- rel_place degree-matched=0.7514 vs random-neg=0.8073: the confound-fix removed ~0.056 of inflation
  (random-neg 0.807 reproduces R3/R4's 0.803); degree-matched still a real relational signal (>0.5).
- corpus: K=5000, total_tokens=265,273 (~53/concept), 3.07 mined EWT-sents/concept, MLM final loss 6.91.
HONEST FINDING: even a deep from-scratch sequence encoder + more text STILL ties/loses raw grounding on
held-out-NEW supersense. WHY = (1) grounding already saturates the supersense-neighbourhood ceiling
(~0.64); (2) the transformer is data-starved (265k tokens ~4 orders below LM scale; deep-rep alone 0.519
near chance); (3) supersense is coarse and grounding proxies it. Points at THE_PLAN coupling: the encoder
needs the FOUNDATION as its data source at far larger scale, and/or supersense-AUC is grounding-saturated
-> a finer eval is needed to expose text value.

## Compute architecture
Sequential-CPU with justification: small Transformer (d<=128, 2 layers) MLM-pretrain + light MLP fusion
over precomputed features; per-phase-point wall << 10s; whole FULL foreground-completable in ~few min.
No GPU speedup material at this scale (small model, CPU-resident). storage: no_storage / no_composition.
