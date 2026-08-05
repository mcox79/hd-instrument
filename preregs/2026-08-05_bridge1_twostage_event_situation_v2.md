# Pre-reg: BRIDGE-1/C-AB v2 = two-stage event + situation-conditioned grounding

anchor_name: bridge1_twostage_event_situation_v2
cell: experiments/exp_bridge1_twostage_event_situation_v2.py
date: 2026-08-05

## Why (see notes/deepdrill_SYNTHESIS_bridge1_certainty.md)
Confirmation test (data/exp_bridge1_confirmation_test_v1/metrics.json, commit 761211bf6,
RULING_CONFIRMED) MEASURED the governor-only reader (exp_bridge1_governor_grounding_v1.py,
commit 96e8e8404) at acc_A=0.962 (local-governor, KEEP) but acc_B=0.500 and acc_C=0.500
(event-differing / discourse-decisive, chance-by-construction). This cell builds and measures
the corrected two-stage architecture the deep-drill specified.

## Mechanism (design, not hypothesized)
Stage 1 (unmodified, imported): bridge1's governor/adjmod perceptron = dominance-default.
Stage 2a (event assembly): closed OBJECT_EVENT_CLASS lexicon (GOAL_OBJECT / ADVERSARIAL /
ANIMATE_HARMABLE) + a structural ADP-crossing direct-object gate + a FORCE_CLASS_HARM verb
lexicon; fires only for a closed word set, abstains elsewhere (protects subset A).
Stage 2b (situation-bias port): THREAT_WORDS/BENIGN_WORDS lexical reader over the item's `prior`
sentence field (coref-adjacent: "it" corefers to the prior sentence's introduced entity).
Combine = biased competition: situation > event > governor (governor never erased, always the
fallback/dominance-default).

## Controls (mandatory, all present in the cell)
- governor_only baseline arm (bit-for-bit same code path as bridge1/confirmation) -- must
  reproduce ~0.500 on B/C, ~0.96 on A.
- bag-of-words control -- must stay near chance on B/C.
- scrambled_event control (permuted OBJECT_EVENT_CLASS dict) -- must collapse the B lift.
- scrambled_discourse control (mispaired `prior` field) -- must collapse the C lift.
- unseen-concept generalization: subset B_GEN (4 new pairs, fresh verbs/objects) and subset
  C_GEN (1 new pair, fresh prior sentences) exercising the SAME lexicons on NEW words/sentences.
- theta witness: BLOCK_HIGH != BLOCK_LOW value (coping differentiates value at fixed congruence).

## Pre-registered bands (set BEFORE running FULL)
HARD_PASS: A_two_stage >= 0.85 AND B_two_stage >= 0.75 AND C_two_stage >= 0.70 AND
  (B_two_stage - B_scrambled_event) >= 0.15 AND (C_two_stage - C_scrambled_discourse) >= 0.15 AND
  B_bow <= 0.60 AND C_bow <= 0.60 AND Bgen_two_stage >= 0.70 AND Cgen_two_stage >= 0.60.
PARTIAL_EVENT_FIXED_SITUATION_PENDING: B-side of HARD_PASS holds but C-side does not (event-
  assembly works, situation-port needs the real Component-5 situation model).
HARD_FAIL: B_two_stage < 0.60 (event-assembly did not work).
HARD_FAIL_REGRESSION_ON_A: A_two_stage < 0.85 (mechanism broke the local-governor-sufficient case).
Else: MIDDLE_BAND.

## Compute architecture
Sequential-CPU, justified: wall time < 10s total per seed (perceptron training on ~180 items +
closed-form theta training reused from the frozen sim); 5 seeds foreground in well under 2 minutes.
Storage strategy: no_storage (no PartitionedStore writes; pure in-memory eval cell).

## Gates (per exp_dev.md SCHEMA-VET checklist)
- cardinality_ok: EXPECTED_N_SEEDS=5
- arms_differ_verified: true (per-seed two_stage_eq_governor_{B,C} checked; smoke asserts NOT both)
- final_metrics_atomicity: tmp_replace
- crlb_n/a: no swept capacity dimension; sign-accuracy discriminator only
- baseline_in_band: n/a (majority baseline 0.500 by construction on B/C, matching confirmation test)
- discriminator survives scale: full-N == smoke-N item sets; only theta-training steps differ
- deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
- progress_logging: print_flush_true (well under 30 min anyway)
- real_code_path_exercised: bridge1.extract_governor_feats, bridge1.valence_for_type,
  sim.Codebook/sim.train_theta, hdlab.thematic_role_labeler.train_perceptron,
  hdlab.animacy_lexicon.lookup_animacy (sanity-check only)

## Honest scope caveat
Event/situation stages are supplied closed lexicons + a structural gate, standing in for the full
hdlab.frame_induction / hdlab.situation_reader / hdlab.coreference_resolver / hdlab.
situation_model_accumulate pipelines named in the build brief. Deep-wiring those organs is
deferred to a follow-up cell if this shape is confirmed; this cell measures whether the corrected
TWO-STAGE+PORT SHAPE recovers B/C with the minimum lexical knowledge that shape requires.
