# exp_dev hand-off — research: native-binding comprehension toward richer/naturalistic NL

**Filed by:** research sub-agent, 2026-07-30
**Trigger:** notes/native_binding_comprehension_richer_nl_frontier_plan_2026-07-30.md (full design,
gap analysis, pre-registered bands, sequencing -- read that file first, this is the pointer summary)
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; this hand-off is informational
regardless of pause state (exp_dev picks it up on the next unpaused refill cycle).

Per [[feedback-no-experiment-design-in-prompts]]: this file gives ANCHOR POINTERS + WHY-NOW, not a
prescribed implementation -- exp_dev owns cell authoring, smoke iteration, and pre-reg detail.

## Anchor candidates (rank-ordered)

1. **`exp_vsa_native_bind_zeroshot_role_v1` + ORTHOGONALIZING-PROJECTION ARM (Step 0, fire first)**
   - Anchor pointer: extend `experiments/exp_vsa_native_bind_zeroshot_role_v1.py` in place with a new
     arm `ARM_ORTHOGONALIZED_ENCODER_KEYS` (Lowdin symmetric orthogonalization of the existing
     `oc.build_oracle_table` role-key matrix, `K_orth = K @ (K^T K)^(-1/2)`, closed-form, zero learned
     params) + a role-count scaling sweep (15/30/60 roles).
   - Substrate-product reading: if this clears, the substrate can derive quasi-orthogonal binding keys
     for MANY entity/relation types from its own frozen encoder without retraining -- directly enables
     "ask about combinations of many entities/relations" at product scale, not just the 2-15 roles
     tested tonight.
   - Tier hint: cheap/closed-form, <15 min CPU, no GPU, no new corpus -- should land same-session.
   - Why now: this is the SAME bottleneck already measured tonight (`encoder_key_cosine_mean=0.35`,
     `ARM_ENCODER_KEYS` held-out recall 0.29, bounded PARTIAL) in `exp_vsa_native_bind_zeroshot_role_v1`'s
     own metrics.json -- it is a pre-identified, already-isolated gap, not a speculative new direction.
   - Pre-registered bands: see frontier-plan Section 2 (HARD-PASS: recall>=0.50 @15 roles AND
     cosine<0.15 @15 roles AND cosine<0.25 @60 roles; HARD-FAIL: recall<0.35 @15 roles).

2. **`exp_native_binding_naturalistic_multirelation_v1` (Step 1+2, gated on #1's verdict)**
   - Anchor pointer: new cell, corpus generator "naturalistic case-role micro-stories" (5 Fillmorean
     roles: AGENT/PATIENT/RECIPIENT/INSTRUMENT/LOCATION, 4-6 syntactic frames per role incl.
     active/passive/relative-clause/cleft/pronoun-coreference, 3-6 sentences/passage, distractors +
     overwrite-events reused from the proven Selective-Overwrite-Recall construction). Pipeline:
     frozen v2 encoder -> pca_whiten conditioning -> role-key derivation (oracle-averaging +
     Step-0's orthogonalizing projection if it landed) -> native FHRR bind/accumulate -> 3 query types
     (novel-filler-via-pronoun, 5-role relational, 2-hop chained-unbind).
   - Substrate-product reading: this is the actual demoable milestone -- "read a short natural
     paragraph, answer who/what/where questions about it" via glass-box algebra, no external LLM.
   - Tier hint: build-heavy (new corpus + new pipeline module), moderate compute (frozen-encoder
     forward passes only, no gradient training in the native-VSA arm; the pooled-reader floor needs a
     small linear-probe fit, cheap). Est multi-hour build, CPU-only per current invariants.
   - Why now: composes three ALREADY-CONFIRMED capabilities (novel-filler read-conditioning,
     zero-shot-role native-VSA, cross-slot relational native-VSA) into one pipeline for the first time --
     the natural next integration step per tonight's unifying finding, not a new speculative mechanism.
   - Pre-registered bands: see frontier-plan Section 4 (HARD-PASS: all 3 query types >=0.80 both seeds
     with pooled-reader floor + coreference-antecedent floor both collapsing; INVALID if pooled-reader
     floor also clears PROVEN_MIN, the MES reservoir-decodable trap recurring).
   - MANDATORY build order within this cell (do not skip): build the pooled-reader floor and the
     coreference-random-antecedent floor and confirm BOTH collapse BEFORE trusting any native-VSA
     main-arm result -- this is the exact order-of-operations lesson the MES calibration thread
     (`db39c1082`) already had to learn the hard way; do not re-learn it here.

## Context pointers (file paths, not summaries)

- Full design + risk analysis: `notes/native_binding_comprehension_richer_nl_frontier_plan_2026-07-30.md`
- Confirmed cells (reuse machinery verbatim where noted):
  `experiments/exp_selective_overwrite_recall_nl_wm_novel_filler_composition_v1.py`,
  `experiments/exp_vsa_native_bind_zeroshot_role_v1.py`,
  `experiments/exp_cross_slot_relational_binding_v1.py`
- Native binding primitives: `hdlab/binding.py` (`bind`/`unbind`, dtype-dispatched FHRR/HRR)
- Frozen v2 encoder + conditioner: `exp_selective_overwrite_recall_nl_wm_roleseparated_v1.FrozenV2Encoder`,
  `exp_selective_overwrite_recall_nl_wm_readcond_v1.Conditioner` (pca_whiten)
- Entity vocab / generator patterns: `exp_selective_overwrite_recall_nl_calib_v1.py` (COLORS, SLOT_NOUNS)
- MES reservoir-decodable trap (the floor-ordering lesson): `notes/WHERE_WE_ARE_NOW.md` lines re: "MES
  order is RESERVOIR-decodable" and "db39c1082" calibration entry.
- Prior-art theory: `notes/research_native_binding_compositional_generalization_2026-07-25.md`

## Contract section

- Glass-box, NO external LLM at inference, NO borrowed-embedding encoder (frozen v2 encoder is
  substrate-trained, not a foreign pretrained model -- unchanged invariant).
- Native binding = substrate's own algebra (`hdlab/binding.py`), zero learned parameters in the VSA arms.
- Supplying the coreference-antecedent ANSWER as task metadata (for scoring) is OK per "supplying
  knowledge/data OK, supplying the reading MECHANISM forbidden" -- the model still must bind the pronoun
  token position to the right entity vector using its own reps; it is not handed a coreference resolver.
- CELL-TEMPLATE MANDATORY conventions apply unchanged (arms_differ_verified, atomic metrics write,
  deterministic seeding, checkpoint/resume for multi-unit loops, no BaseException, ASCII-only).

## Autonomy declaration

exp_dev owns: exact cell code, smoke-scale parameters, self-test design, dispatch queue choice
(local_cpu_queue expected for both anchors per compute-proportionality -- closed-form/frozen-encoder
work, no GPU need), and any construction adjustments needed to make the pre-registered floors
correctly collapse (per this file's mandatory build-order note for anchor #2). Anchor #1 should be
prioritized first and can likely ship same-cycle; anchor #2 is gated on anchor #1's verdict per the
frontier plan's Section 6 sequencing -- do not build anchor #2 with full open role-count before anchor
#1 lands (role-capped fallback if anchor #1 HARD-FAILs is specified in the frontier plan).
