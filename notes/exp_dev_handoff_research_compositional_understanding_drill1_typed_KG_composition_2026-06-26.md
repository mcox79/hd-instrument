# exp_dev hand-off — research: compositional understanding DRILL 1 (typed KG composition)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER strategic pivot 2026-06-26: language-prediction track CLOSED; build compositional understanding FIRST. Standing memory `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`. Pivot note `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`.

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off, do NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not full cell specs. exp_dev authors cells per substrate-physics. Pre-reg bands LOAD-BEARING — bake into prereg verbatim.

## Pivot frame (mandatory context)

The substrate has NO understanding of language. We are NOT testing language prediction. We ARE testing whether the substrate can:
1. INGEST typed semantic structure (concepts + relations + types)
2. COMPOSE atomic meanings into composite meanings via mathematical operations
3. RECOVER composed meanings when queried
4. DETECT type-incompatible compositions (refuse rather than confabulate)
5. FILL compositional gaps from structural constraints

text8 / BPC / bigram-gap / next-token-prediction are NOT relevant evals here. The eval is COMPOSITION FIDELITY.

## Anchor candidates (rank-ordered)

### Anchor 1 (top priority): comp_understanding_typed_kg_composition_v1

- **Anchor pointer:** `experiments/exp_comp_understanding_typed_kg_composition_v1.py` (new cell; substrate-native; uses existing chain-grade KG primitives)
- **Substrate-product reading:** "extend existing FB15k-237 / ConceptNet KG ingest to TYPED predicates with TYPED arguments; test substrate's ability to (a) recover composed meaning of multi-predicate queries, (b) detect type-incompatible compositions and refuse, (c) fill missing arguments from structural constraints; eval = composition fidelity not retrieval accuracy"
- **Tier hint:** chain-grade candidate IF composition_fidelity >= 0.70 AND type_error_detection_rate >= 0.80 AND gap_fill_accuracy >= 0.60 AND cv <= 0.05; MIDDLE_BAND if any in (HARD_PASS - 0.10, HARD_PASS); HARD_FAIL if composition_fidelity < 0.50 (composition is dominated by noise) OR type_error_detection < 0.50 (substrate can't tell valid from invalid compositions)
- **Why now:** First-of-its-kind cell for the substrate. Tests whether compositional understanding is even POSSIBLE on the current primitives before we invest in building richer compositional infrastructure. Uses existing chain-grade KG ingest as scaffold — substrate-mine before extrapolating.
- **Composition:** uses existing FB15k-237 / ConceptNet KG triples (chain-grade ledger) + HRR role-filler binding (DESIGNED for this; n5 trigram failure was wrong-tool not wrong-primitive) + concept codebook + refuse-gate (epistemic humility on type errors)
- **Arms (4 mandatory):**
  - **ARM_ATOMIC_RETRIEVAL_BASELINE** — single-triple retrieval (reproduces existing chain-grade KG ingest accuracy at ~0.97; rail for sanity)
  - **ARM_COMPOSITION_FIDELITY** — test query: substrate is asked to recover the composed meaning of `(SubjA, Rel1, ObjB) AND (ObjB, Rel2, ObjC)`; eval = does the substrate's composed representation match the bound representation of the two triples? Cosine of substrate's composed-vector to the ground-truth composed-vector ≥ 0.70 for HARD_PASS.
  - **ARM_TYPE_ERROR_DETECTION** — test query: substrate is given type-incompatible composition (e.g. `(Stone, runs, Marathon)` — STONE is not ANIMATE so can't be agent of RUN); eval = does substrate's refuse-gate fire? Type-error detection rate >= 0.80 for HARD_PASS.
  - **ARM_COMPOSITIONAL_GAP_FILL** — test query: substrate is given `(SubjA, Rel1, ?)` with TYPE constraint on `?`; eval = does substrate fill `?` with a type-consistent answer? Gap-fill accuracy >= 0.60 for HARD_PASS.
- **Pre-reg bands:** HARD_PASS comp_fid >= 0.70 AND type_err >= 0.80 AND gap_fill >= 0.60 (P=0.25); MIDDLE in respective lower bands per arm (P=0.45); HARD_FAIL comp_fid < 0.50 OR type_err < 0.50 (P=0.30)
- **Smoke gate:** sigma=0 sanity (ARM_ATOMIC_RETRIEVAL_BASELINE reproduces existing 0.97 accuracy); type assignments per concept loaded correctly from existing KG metadata; HRR role-filler bind/unbind round-trip recall = 1.000 on 100 test triples; zero LLM calls AUDIT logged.
- **Cost estimate:** ~5 min smoke / ~3-5 hr local_cpu (3 seeds; uses existing chain-grade KG ingest so most of the wall is composition + eval not ingest)
- **DEPENDENCY:** runs on local_cpu_queue. CAN FIRE TODAY post-orchestrator routing.
- **What this teaches us:** if HARD_PASS, the substrate CAN do compositional understanding on its existing primitives — and we know which primitives (HRR role-filler + KG triples + refuse-gate) compose well. Then we expand to richer typed semantic resources. If HARD_FAIL, the existing primitives don't support compositional fidelity — we need to build new compositional infrastructure before going further.

### Anchor 2: comp_understanding_predicate_argument_v1

- **Anchor pointer:** `experiments/exp_comp_understanding_predicate_argument_v1.py` (new cell)
- **Substrate-product reading:** "ingest VerbNet-style typed predicate-argument templates (GIVE has agent:ANIMATE, recipient:ANIMATE, theme:CONCRETE-NOUN); test substrate's compositional sentence-meaning construction; eval = does composed sentence-meaning preserve role-filler bindings under composition?"
- **Tier hint:** MEASURED_MECHANISM expected; chain-grade-eligible if role-recovery >= 0.70 across 3-argument predicates
- **Why now:** Anchor 1 tests COMPOSITION between two atomic triples; Anchor 2 tests composition WITHIN a single predicate-argument template (richer compositional structure per atomic unit). Orthogonal lever.
- **Composition:** VerbNet-style predicate templates + HRR role-filler binding + refuse-gate on type-error agents/themes
- **Arms (3 mandatory):** ARM_2ARG_PREDICATE (give:agent+theme); ARM_3ARG_PREDICATE (give:agent+recipient+theme); ARM_TYPE_ERROR_DETECTION (stone-as-agent of running)
- **Cost estimate:** ~10 min smoke / ~4-6 hr local_cpu
- **Order:** dispatch in parallel with Anchor 1 OR after Anchor 1 verdict

### Anchor 3 (deferred): comp_understanding_compositional_concept_formation_v1

- **Anchor pointer:** `experiments/exp_comp_understanding_compositional_concept_formation_v1.py` (DEFER until Anchor 1 verdict)
- **Substrate-product reading:** "present concept instances (red+ball, blue+cube, red+cube, blue+ball); substrate learns to represent each as composite of factored features; test compositional generalization: substrate predicts feature-vector for unseen combination (red+pyramid) given only (red+X for X != pyramid) and (Y+pyramid for Y != red)"
- **Tier hint:** Phase-2 cell; requires Anchor 1 verdict to inform whether HRR factor-binding or direct-vector-arithmetic is the right composition primitive
- **Cost estimate:** ~3 days build + 6-8 hr CPU
- **Order:** DEFER until Anchor 1 lands

## Context pointers (file paths, not summaries)

- **Pivot note (this hand-off's parent):** `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
- **USER directive memory:** `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- **SUPERSEDED handoffs (do NOT pick up):**
  - `notes/exp_dev_handoff_research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
  - `notes/exp_dev_handoff_research_language_ingest_drill2_segmentation_block_size_2026-06-26.md`
  - `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
  - `notes/exp_dev_handoff_research_lm_pipeline_partition_routed_trigram_2026-06-26.md`
- **Existing chain-grade KG primitives (the scaffold):** substrate cert_ledger.jsonl ch_584 (FB15k-237) / ch_585 (ConceptNet) / ch_588 (HotpotQA)
- **HRR role-filler binding primitive:** `hdlab/binding.py` + chain-grade test in `verification/`
- **refuse-gate primitive:** `hdlab/refuse_gate.py` (chain-grade at V_REL=256)
- **multi-hop chain-grade primitive:** `hdlab/multi_hop.py`
- **concept codebook V_C=1024:** existing n1v3 substrate codebook (already in repo); RE-USE structure but composition queries are NEW
- **Bias master checklist:** `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - Principle Q (suspect 1.000 results) APPLIES: composition fidelity at 1.000 in smoke means easy regime — verify discriminating regime
  - Principle S (band-calibration regime checks) APPLIES: 3-arm discriminator design spelled out

## Contract

- Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHORS and POINTERS only. exp_dev authors cells per substrate-physics. Pre-reg bands are load-bearing.
- All cells must include META_M7 reproduce-once rail.
- Substrate-only-decode gate preserved (n_llm == 0; AUDIT logged).
- Per-seed runtime + cv <= 0.05 required for chain-grade.
- ARM_ATOMIC_RETRIEVAL_BASELINE rail MANDATORY in Anchor 1 (reproduces existing chain-grade KG retrieval; sanity).
- Smoke gate per anchor BEFORE full dispatch.
- Pre-flight verify-the-referent gate per Fix #26.
- text8 / BPC / bigram-gap / next-token-prediction are NOT relevant evals for these cells. If exp_dev finds itself reaching for those metrics, STOP and check with research.

## Autonomy declaration

exp_dev has full autonomy over:
- Cell authoring within research-note guidance
- Encoder / N_DIM / seed choice within standard envelope
- Smoke / full split per queue-add gate
- Reprioritization between Anchors 1 and 2

exp_dev does NOT have autonomy over:
- Re-defining HARD_PASS / MIDDLE / HARD_FAIL bands
- Reaching for language-prediction evals (text8, BPC, bigram-gap) — this hand-off explicitly disallows them
- Bumping to chain-grade pre-Skunkworks review (default = MIDDLE per Fix #28)
- Re-opening any of the SUPERSEDED language-ingest handoffs

---

-- Research (Opus 4.7-1M)
