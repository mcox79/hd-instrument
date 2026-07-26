# Pre-reg: R3/R4 internal self-teacher (gloss-text + relational-predictive) on held-out-NEW concepts

Anchor: `self_teacher_gloss_relational_predictive_heldout_new_v1`
Cell: `experiments/exp_self_teacher_gloss_relational_predictive_heldout_new_v1.py`
Metrics: `data/exp_self_teacher_gloss_relational_predictive_heldout_new_v1/metrics.json`
Date: 2026-07-26. CPU-only. No GPU. No network at run time.

## Question (THE_PLAN R3/R4)
R1 landmark-geometry added only +0.0009 over RAW-GROUNDING (learned 0.6413 vs raw 0.6404,
MEASURED@data/exp_grounded_r1_landmark_geometry_wordnet_neighbourhood_v1/metrics.json) => the bottleneck
is INPUT. Does adding the MISSING input + predictive signal -- GLOSS/DEFINITIONAL text (encoded by OUR OWN
glass-box char-trigram encoder, teacher-free) + RELATIONAL-predictive objective + EMA self-distillation --
BREAK the +0.0009 grounding ceiling on held-out-NEW-concept WordNet-supersense placement?

## THE ONE NUMBER (pre-registered bands, applied to ARM_SELF_TEACHER primary)
margin = SELF_TEACHER same_lex_auc - RAW_GROUNDING same_lex_auc (held-out-NEW concepts).
- HARD_PASS: margin >= 0.03 AND margin_min > 0 (per-seed) AND self_teacher >= 0.60 AND self_teacher >=
  random_init AND can_fail(collapse in [0.44,0.56]) AND raw_signal_ok(raw >= 0.55) AND power(n_q >= 150).
- HARD_FAIL: collapse NOT in band (leak/saturation) OR raw < 0.55 (metric saturated) OR self_teacher <
  0.53 (chance) OR n_q < 150.
- MIDDLE_BAND (deeper-ceiling): real signal + valid controls but margin < 0.03. Per the Director contract,
  a tie/negative here is a MAJOR honest finding (a DEEPER input/representation ceiling), reported plainly.

Band values: HP_MARGIN_OVER_RAW=0.03 HYPOTHESIZED (grow the +0.0009 to a real >noise margin).
HP_SELF_TEACHER_SIGNAL=0.60, HF_AUC=0.53, RAW_SIGNAL_MIN=0.55, COLLAPSE_BAND=(0.44,0.56),
MIN_QUERY_TASKS=150. Base AUC = 0.5 exactly THEORETICAL (Mann-Whitney, class-balance-independent).

## Arms (ablation: attribute WHERE any gain comes from)
- ARM_SELF_TEACHER [PRIMARY]: grounding+gloss+relctx input; geometry + relational-prediction (InfoNCE) +
  masked-gloss prediction (BCE) + EMA self-distillation.
- ARM_GROUNDING_ONLY_LEARN: R1 geometry, grounding-only (reproduces the prior +0.0009 arm).
- ARM_PLUS_GLOSS_LEARN: grounding+gloss + geometry + masked-gloss prediction (isolate gloss).
- ARM_PLUS_RELPRED_LEARN: grounding + geometry + relational-prediction (isolate relpred).
- ARM_RAW_GROUNDING: raw grounding cosine (THE ceiling). ARM_RAW_GLOSS: raw gloss char-trigram cosine.
- ARM_RANDOM_INIT: untrained full encoder. ARM_COLLAPSE_SHUFFLE: input rows permuted across ids (can-fail).

## Invariants
TEACHER-FREE (gloss encoded ONLY by our from-scratch char-trigram Linear; NO GloVe/BGE/transformer/borrowed
vector anywhere; WordNet lexname EVAL-ONLY truth). INDUCTIVE (held-out placed from grounding + own gloss +
known TRAIN-neighbour context; never a lookup, never a landmark/anchor/InfoNCE-target). LEAK-PROOF (sha256
concept split; gloss uses vocab-free HASH bucketing => no train-fit-vocab leak; relctx TRAIN-only; supersense
truth disjoint from all inputs/targets).

## SCHEMA-VET fields
- arms_differ_verified: true (META_RULE_AF hash-test at smoke; all 8 arms distinct).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
- except SystemExit: raise before except Exception (no BaseException / bare except -- grep-clean).
- crlb_n/a: AUC base=0.5 analytic; collapse+random-init controls witness the floor empirically.
- baseline_in_band: collapse ~0.50; raw-grounding a real >0.55 signal; self_teacher not saturated.
- discriminator_survives_scale: FULL (cap=5000, matches R1) runs foreground-to-completion (~108s); FULL IS
  the discriminator test. Smoke (cap=2500) and FULL agree in sign.
- HP_SCOPE: {ARM_SELF_TEACHER: [margin>=0.03, self_teacher>=0.60, >=random_init]}; controls not gated.
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (3 full); verdict counts len(per_seed).
- per-unit failure-class instrumentation: yes (seed_failures with failure_class).
- calibration_check: default_ok_for_this_regime (AUC analytic base; controls witness).
- deterministic_seeding: true (sha256 split + sha256 gloss-hash + fixed int seeds + sorted(); no
  hash()/list(set()); PROT-023 source-scan clean).
- real_code_path / substrate_signature: N/A (self-contained jsonl reader + NLTK + torch MLP; no
  KGStore/fit objects).
- progress_logging: print_flush_true (timeout < 30min; present anyway).
- Compute architecture: sequential-CPU justified (small batched MLP, per-seed independent; FULL 108s wall,
  well under the 10s/point batching-candidate threshold is exceeded only in aggregate -- torch batches the
  matmuls; no GPU speedup material at this scale; R1 sibling ran 28s CPU).
- Storage strategy: no_storage (encoder + eval only; no substrate atoms written).

## RESULT (MEASURED@data/exp_self_teacher_gloss_relational_predictive_heldout_new_v1/metrics.json)
VERDICT = MIDDLE_BAND (deeper_ceiling=True). FULL, cap=5000, 3 seeds, n_q=1007.
THE NUMBER: self_teacher - raw_grounding = 0.6256 - 0.6361 = -0.0105 (min -0.0125) -- ceiling NOT broken.
Ablation vs raw_grounding 0.6361: raw_gloss 0.5978 (-0.0383); ground_only_learn 0.6383 (+0.0022, reproduces
R1 tie); plus_gloss 0.6431 (+0.0070, best learned but < 0.03); plus_relpred 0.6175 (-0.0186, HURTS).
rel_place_auc(SELF_TEACHER)=0.8027 (relational-prediction objective succeeds spectacularly, but that head is
supervised on the relational graph + uses neighbour-derived input). Controls: collapse 0.5020 (can_fail),
raw_signal_ok, random_init 0.6250. Deeper-ceiling confirmed: neither glass-box gloss-text nor
relational-predictive input breaks the grounding ceiling on the INDEPENDENT WordNet-supersense metric.
