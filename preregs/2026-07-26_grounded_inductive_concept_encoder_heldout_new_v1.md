# Pre-reg: grounded_inductive_concept_encoder_heldout_new_v1

Cell: `experiments/exp_grounded_inductive_concept_encoder_heldout_new_v1.py`
Author: exp_dev | Date: 2026-07-26 | CPU-only, teacher-free.

## Question (THE coupling step)
Can a concept's measured EXPERIENTIAL GROUNDING (Lancaster sensorimotor 11 + concreteness + VAD 3 + AoA),
passed through an encoder trained TEACHER-FREE with a relational self-teacher on KNOWN concepts, place an
UNSEEN concept near its true relational neighbours in `data/cskg_foundation_v1/`? Judged ONLY on
held-out-NEW-concept generalization.

## Hard invariants
- TEACHER-FREE: only input = measured grounding norms; no GloVe/BGE/transformer/borrowed vector (teacher, target, init, feature).
- INDUCTIVE: encoder = f(grounding_features) -> code. Held-out concept coded from grounding ALONE. Per-concept lookup table is a CONTROL that must collapse.

## Leak-proof concept-level split
Each grounded concept (induced-deg >= min_deg) -> TRAIN or HELDOUT by sha256(id) (deterministic, PYTHONHASHSEED-independent).
Training graph = edges with BOTH endpoints TRAIN. EVERY edge incident to a held-out concept removed from training.
Held-out concept's edges to TRAIN concepts = eval target only (never seen by encoder). Held-out<->held-out edges discarded.
Grounding standardized on TRAIN stats only.

## Arms
- ARM_GROUNDING_ENCODER [PRIMARY]: MLP(20->hidden->code), InfoNCE over neighbour positives vs EMA self-teacher + VICReg.
- ARM_RAW_GROUNDING [must-BEAT reference]: no encoder; rank by raw standardized-grounding cosine.
- ARM_RANDOM_INIT [training-added-value ref]: untrained encoder.
- ARM_FEATURE_SHUFFLE [COLLAPSE control -> 0.5]: grounding shuffled across concept ids.
- ARM_LOOKUP_RECALL [COLLAPSE control -> 0.5]: transductive per-concept table; held-out concept has NO row ->
  independent RANDOM unit code (true no-information floor). NOTE: mean-train-code fill was REJECTED after the
  first FULL -- the train centroid encodes a POPULARITY prior (cosine-to-centroid ranks by degree), a strong
  baseline NOT a floor; that role is now the explicit ARM_POPULARITY.
- ARM_POPULARITY [strong baseline the encoder must BEAT]: rank train concepts by TRAIN-degree, identical for
  every held-out concept (a new concept is guessed to attach to popular hubs). This is the genuine bar.

Can-fail gate is on FEATURE_SHUFFLE + LOOKUP_RECALL (both true floors -> ~0.5). F.4: RANDOM_INIT is structurally
non-floor (a random projection partially preserves grounding-cosine) -> reference, not a collapse gate.

## Metric (held-out-NEW-concept)
For each held-out concept, rank ALL train concepts by cosine to enc(h). Primary = mean rank-AUC (true-neighbour vs
non-neighbour; base/chance = 0.5). Secondary = recall@10, MRR, neighbour-cosine margin.

## Pre-registered bands (PRIMARY = ARM_GROUNDING_ENCODER held-out AUC; HP_SCOPE = primary only)
- can_fail_fired := shuffle_auc in [0.44,0.56] AND lookup_auc in [0.44,0.56]  (else LEAK/BROKEN).
- HARD_PASS: enc>=0.60 AND (enc-max(shuffle,lookup))>=0.07 AND (enc-raw)>=0.02 AND (enc-popularity)>=0.02 AND can_fail_fired.
- HARD_FAIL: NOT can_fail_fired OR enc<0.55 OR (enc-max_collapse)<0.03 OR enc<raw-0.01 OR (enc-popularity)<0.0
  (encoder that does not beat a trivial popularity prior FAILS the genuine-generalization bar).
- else MIDDLE_BAND (weak-but-real generalization).
All thresholds tagged HYPOTHESIZED@this-prereg (chance=0.5 THEORETICAL; strictly-above-floor per META_RULE_L).

## Compute architecture
sequential-CPU justified: small MLP (20->256) + single-matmul eval; wall < 6 min full. No GPU batching gain.
Storage: no_storage / no_composition. Deterministic seeding: sha256 split + fixed int seeds + sorted() (PROT-023 clean).

## SCHEMA-VET fields
- arms_differ_verified: true (hash test, 5 arms) | final_metrics_atomicity: tmp_replace
- crlb_n/a: "AUC base=0.5 analytic; collapse controls witness the floor empirically"
- baseline_in_band: collapse controls must sit in [0.44,0.56]; discriminator survives scale (smoke IS a genuine held-out test)
- calibration_check: default_ok_for_this_regime | cardinality_ok: EXPECTED_N_UNITS = n_seeds
- real_code_path/substrate_signature: N/A (self-contained jsonl reader; no KGStore/fit objects)
- progress_logging: print_flush_true | start_marker_written/crash_diagnostic_present: true
- except SystemExit: raise before except Exception (no BaseException)

## Profiles
- smoke: min_deg=3 cap=6000 seeds=[7,13] epochs=80 code=128. FULL: min_deg=3 cap=8700 seeds=[7,13,17] epochs=180 code=256.

## MEASURED (FULL, definitive) @ data/exp_grounded_inductive_concept_encoder_heldout_new_v1/metrics.json
3 seeds [7,13,17], 8603 grounded deg>=3, train 6860 / heldout-eval 1656:
- ENCODER heldout_auc=0.5879 (min 0.5797; recall@10=0.093; mrr=0.042)
- raw_grounding=0.5627 (enc-raw=+0.025); random_init=0.5568
- POPULARITY=0.8148 (enc-pop=-0.227; pop recall@10=0.508, mrr=0.319)
- COLLAPSE shuffle=0.498, lookup_rand=0.495 -> can_fail_fired=True (enc-maxcollapse=+0.090)
- VERDICT FULL = HARD_FAIL: the inductive grounding encoder generalizes to NEW concepts WEAKLY (beats collapse
  floor + raw grounding, stable 3 seeds) but is DECISIVELY beaten by a popularity/degree prior -> does NOT clear
  the genuine-generalization bar. WHY: cskg_foundation_v1 is hub-dominated (LocatedNear + hubs); new concepts'
  true neighbours are mostly popular hubs, which grounding norms (perceptual profile) do not encode. Grounding-
  only input is insufficient to beat popularity.
- (smoke @ ..._smoke/metrics.json: enc 0.581 vs collapse ~0.50; popularity leak weaker at 6k so smoke read
  MIDDLE_BAND under the mean-code lookup -- the FULL + explicit popularity arm is the definitive read.)

## NEXT LEVERS (for Director)
1. Popularity-CONTROLLED eval: score against DEGREE-MATCHED negatives so the encoder must beat popularity, not
   re-derive it -- reveals whether grounding adds signal ON TOP of the degree prior.
2. Add RELATIONAL CONTEXT to the inductive input: encode a held-out concept from its edges to KNOWN concepts
   (typed-neighbour grounding aggregate), not grounding alone -- gives the encoder the structure popularity uses.
3. R1 global/landmark objective (encoder_rescue): in-batch InfoNCE may under-supervise graded geometry.
