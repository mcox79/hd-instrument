# SESSION STATE — aimed_reading_is_built_and_the_reader_never_calls_it (compaction handoff, 2026-08-24)

**READ THIS FIRST after compaction.** This captures the full arc so we can finish. The SOLVED.md in
this folder is STALE (it describes only v1-v3 and says REFUTED) — it predates the v6 win and the
entire meaning investigation. Do NOT trust it; rewrite it per "HOW TO FINISH" below.

## THE ONE-PARAGRAPH TRUTH
The brief asked: can aimed reading beat a fixed schedule on held-out COVERAGE. **v6 (comprehensible-
input reader) SOLVES that bar** (0.0915 vs FROZEN 0.0510, CI-separated, both info-free twins lose).
BUT the owner drove a REFRAME: coverage is the WRONG objective. On a fair MEANING metric the ranking
decouples from coverage. And the deepest correction (owner-driven): I wrongly measured the reader's
RAW co-occurrence and called its meaning "hollow" — but this substrate produces meaning by DISTILLING
a grounded hub into the distributional channel (the project's best result: cross-modal distillation
0.865). The current, running experiment JOINS the reader to grounding via that distillation and it
WORKS (smoke: distilled ρ 0.22 vs raw 0.07, info-free twin loses).

## THE EXPERIMENTAL ARC (all cells in experiments/, all self-tested + witnessed where noted)
- **v1 `exp_aimed_reading_register_controlled_v1.py`** — FORAGE (surprise) LOSES to FROZEN even
  register-controlled (0.0407 vs 0.0510). Beats info-free RANDOM. Witness:
  `verification/test_aimed_reading_register_controlled.py` (PASSES, reads banked checkpoint).
- **v2 `exp_aimed_reading_learning_progress_v2.py`** — LP-target LOSES worse (0.0254), TIES the
  random-target twin (LP signal uninformative). Witness:
  `verification/test_aimed_reading_learning_progress.py` (PASSES).
- **v3 `exp_aimed_reading_lp_currency_v3.py`** — full learning-progress WORST (0.0206), ties random.
- **v5 `exp_aimed_reading_comprehensible_input_v5.py`** — i+1 = argmax(known-fraction) PLATEAUED at
  136 grounded (camped on primers). Diagnostic negative.
- **v6 `exp_aimed_reading_learnable_input_v6.py`** — **THE COVERAGE WIN.** choice = max NEW-LEARNABLE
  words + grounding-yield currency. grounded 1018, register-controlled coverage **0.0915 vs FROZEN
  0.0510, CI [+0.030,+0.051]**; beats RANDOM_GY (choice matters) and RANDOM. Witness:
  `verification/test_aimed_reading_learnable_input.py` (PASSES).
- **v7 `exp_aimed_reading_combined_fidelity_v7.py`** — FUSION (comprehensible + REAL predictive
  constraint from substrate vectors + spacing + cross-situational + concreteness, leave-one-out
  ablations). REGRESSED coverage (0.0497); every process helps WITHIN the fusion but the additive
  framework trades depth for breadth. All arms banked.
- **v4 `exp_aimed_reading_seed_replication_v4.py`** — seed-replication harness (multi-policy). PARTIAL
  run banked (frequency@20260901, frozen@20260901). PAUSED/resumable to confirm v6 seed-robustness:
  `--mode full --policy learnable --seeds 20260901,20260902 --source data/exp_aimed_reading_learnable_input_v6/metrics.json`.

## THE MEANING INVESTIGATION (the reframe)
- **`exp_reading_meaning_vs_coverage_v1.py`** (dirs `_v2`, `_v3`) — scored readers on MEANING not
  coverage. Fairness audit (owner-driven): original WordNet-AUC metric was UNFAIR (floored on
  known-good PPMI+SVD at 0.53). Corrected to **WordSim-353 Spearman rho** (positive control on
  PPMI+SVD = 0.262, validated + wired into self-test). FIRM-UP (v3, full budget + bootstrap CIs +
  SHARED-PAIRS): FROZEN 0.345 > v6 0.170 > fusion 0.128 on shared pairs; FROZEN-v6 delta +0.175 CI
  [-0.14,+0.48] (85% directional, NOT CI-separated at n=32); fusion-v6 TIED. **What survived:
  coverage and meaning DECOUPLE (reframe holds, directionally). What did NOT: the 6k "fusion wins
  meaning" was an artifact of different-pairs comparison — RETRACTED.**
- **CRITICAL CORRECTION (owner: "this is not our wall"):** the above measured the reader's RAW
  co-occurrence (meaning-blind BY DESIGN — the project's self-learned word encoder scores SimLex
  −0.002). The substrate produces meaning by DISTILLATION. Grounding scour findings:
  - Best meaning result on disk: **cross-modal distillation AUC 0.865** (label-free, CI-separated),
    `exp_crossmodal_distillation_substitutability_v1` (from the `where_does_a_meaning_signal` problem).
  - Reusable grounded hub asset: **`hdlab/grounded_similarity.py`** — 12-dim (Lancaster sensorimotor
    + Brysbaert concreteness), ~39,707 words, SimLex rho 0.245, registered WIRE. `grounded_vector(w)`.
  - Reader + grounding are SEPARATE at the live path (open PRIORITY 2:
    `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`).

## RUNNING NOW / STATE ON DISK
- **RUNNING: `exp_reader_distilled_meaning_v1.py` full run (PID 9568, stdout
  scratch/distilled_stdout.log, out data/exp_reader_distilled_meaning_v1/).** THE corrected demo:
  each reader (FROZEN/COMPREHENSIBLE/RANDOM) reads -> accumulates a word-context CO-OCCURRENCE store
  (the distributional STUDENT) -> grounded hub DISTILLS a meaning direction over its PPMI+SVD ->
  score DISTILLED meaning on held-out WordSim-353. **SMOKE VALIDATED: distillation works (distilled
  0.22 > raw 0.07), info-free random-hub twin loses (~0), teacher ceiling grounded_alone 0.41.**
  Full run gives firm numbers + the reader comparison (does the aimed reader distill to BETTER
  meaning than FROZEN/RANDOM?). Self-test passes.
- v6 replication PAUSED (resumable, see v4 above).

## HOW TO FINISH (post-compaction)
1. **Read the distilled-meaning full result** (`data/exp_reader_distilled_meaning_v1/metrics.json`,
   table: distilled_rho / raw_phi_rho / grounded_alone_rho / random_hub_rho per reader). The key
   question: does a better reader (COMPREHENSIBLE) distill to higher meaning than FROZEN/RANDOM?
   (Smoke had FROZEN > COMPREHENSIBLE — deep coherent reading may build a better student; the full
   run decides.) Write a scaffold-free witness if promoting.
2. **Optionally resume v4** to confirm v6's coverage win is seed-robust (2 fresh seeds) — needed only
   if SOLVED.md status = SOLVED and we want the replication firm.
3. **REWRITE SOLVED.md** (currently stale REFUTED). Honest final structure:
   - status **SOLVED** on the BRIEF'S STATED BAR: v6 beats FROZEN on register-controlled coverage,
     CI-separated, info-free twins lose. (frozen block: result 0.0915 vs 0.0510 CI[+0.030,+0.051];
     floor FROZEN 0.0510 + twins; controls = register stratification + RANDOM + RANDOM_GY;
     reverify = test_aimed_reading_learnable_input.py.)
   - **HEADLINE FINDING (the reframe, per owner):** coverage is the WRONG objective. Fusion of
     brain-faithful meaning processes REGRESSES coverage while (on a fair meaning metric) coverage
     and meaning DECOUPLE. Report the firm-up honestly (directional, not CI-separated at n=32;
     the "fusion wins meaning" claim was retracted).
   - **THE CORRECTION + THE JOIN:** the substrate DOES represent meaning — via DISTILLING the grounded
     hub into the reading-built distributional channel (`exp_reader_distilled_meaning_v1`; distilled
     >> raw, twin loses). The reader's real value is to build a good distributional STUDENT for the
     grounded TEACHER — reading in service of meaning, not a word count.
   - **PROPOSED hdlab CHANGE (not landed; strategy lands it — board Q111):** (a) wire the corpus
     chooser into `substrate.read()` (L584-636, replace the rotated `order` with the organ's choice);
     BUT note this alone does NOT improve coverage (depth is upstream). (b) The higher-value wiring:
     give the reader a SEPARABLE co-occurrence store (the PRIORITY-2 blocker) so
     `grounded_similarity` can distill meaning into it — that is where reading finally produces
     meaning. Feed distillation from the 40k-word grounded hub; gate on the random-hub null.
   - NEXT STEPS: swap the 12-dim norm hub for the CSKG 1.2M-edge graph as a stronger teacher (the
     `where_does_a_meaning_signal` SOLVED.md's own highest-yield upgrade); measure comprehension, not
     coverage.
   - Validate: `python tools/problem_ledger.py --check` (needs floor + controls; exit 0).
4. Files this session created (all writable scope): experiments/exp_aimed_reading_{register_controlled_v1,
   learning_progress_v2,lp_currency_v3,comprehensible_input_v5,learnable_input_v6,combined_fidelity_v7,
   seed_replication_v4}.py, experiments/exp_reading_meaning_vs_coverage_v1.py,
   experiments/exp_reader_distilled_meaning_v1.py; verification/test_aimed_reading_{register_controlled,
   learning_progress,learnable_input}.py; this file.

## OWNER STEERS THIS SESSION (load-bearing)
- Push brain-foundational + as-successful-as-possible (led to v6 win, then v7 fusion).
- REFRAME: coverage is the wrong thing; put it in the report.
- Be VERY sure meaning is scored FAIRLY (caught the unfair WordNet-AUC; positive control mandatory).
- "We've done so much grounding... this is not our wall" — scour the corpus (found distillation 0.865
  + the grounded hub); DO the distillation experiment. THIS is the key correction.
- Do the RIGHT thing not the easy thing (upgraded #1 to real predictive constraint from substrate
  vectors; measure meaning via distillation not raw cosine).
