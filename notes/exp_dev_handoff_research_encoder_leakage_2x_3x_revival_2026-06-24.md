# exp_dev hand-off - research: encoder-leakage 2x+3x revival drill

**Filed by:** research (Opus 4.7-1M)
**Date:** 2026-06-24
**Trigger:** USER standing rule "drill all negatives 3x"; 3-angle revival drill on encoder-leakage HARD_PASS_LEAKAGE_REAL complete; finding is actionable (proposes cheap decisive cell that may downgrade v1 verdict)
**Cite:** `notes/research_encoder_leakage_2x_3x_revival_2026-06-24.md`

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** the substrate-product reading + tier hint + why-now + pre-reg bands are below. exp_dev decides cell name, file structure, sweep mechanics, smoke design, and dispatch routing. Research does not pre-design the cell.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY, ~2 hr CPU) -- fair-regime clean-encoder re-run

**Anchor pointer:** re-run the clean-encoder eval under conditions that fix the two highest-impact audit findings from Angle 3 of the revival drill:
- (A2) arm B was trained on 100K tokens vs Google News 100B (1,000,000x deficit); needs proper 17M-token text8 training.
- (A6) V=4000 pins all 4 arms to the unigram floor (~7.3-7.7 BPC; lit-grounded unigram entropy for V=4000-5000 Wikipedia is 7.3-8.35 bits); needs V=20k and conditional-bigram metric to have discriminating headroom.

**Substrate-product reading:** if leakage_delta on the FAIR regime drops below 0.10 BPC, the v1 HARD_PASS_LEAKAGE_REAL verdict was a measurement-regime artifact. Substrate-as-LM's original "+12% top-1" claim returns to the active table. If leakage_delta stays >= 0.30 BPC in the fair regime, the v1 verdict is confirmed and Path C substrate-owned encoder becomes load-bearing for substrate-product viability.

**Tier hint:** MEASURED_MECHANISM-eligible (single-hypothesis re-do of v1 cell under audit-driven design fixes). NOT chain-grade by itself; flips cap_map row direction depending on outcome.

**Why-now:** the v1 HARD_PASS verdict landed today and is currently shaping framing of substrate-as-LM viability. Propagating it as a closed door without the fair-regime check would over-commit to a structural conclusion based on a regime artifact. Cheap (~2 hr CPU) compared to multi-week downstream commitments to Path C substrate-owned encoder build.

**Pre-reg HARD bands (both directions; research-supplied):**
- HARD_PASS_LEAKAGE_REFUTED: leakage_delta_B_minus_A on bigram-conditional metric at V=20k < 0.10 BPC AND arm B BPC <= unigram floor by >= 0.5 BPC margin.
- HARD_PASS_LEAKAGE_CONFIRMED: leakage_delta on bigram-conditional metric at V=20k >= 0.30 BPC AND arm B BPC > unigram floor by < 0.2 BPC.
- MIDDLE_BAND: leakage_delta in [0.10, 0.30) -- some pretraining contribution but smaller than v1 estimated.
- HARD_FAIL_REGIME: all arms still cluster within 0.10 BPC at V=20k bigram-conditional -- measurement regime STILL not discriminating; need V=50k or trigram-conditional.
- HARD_FAIL_PROVENANCE: arm A on the fair regime does not reproduce within 0.20 BPC of expected text8-V=20k word2vec-google-news rail (drift -> cell methodology bug; halt).

**Arms suggestion (exp_dev decides exact structure):**
- ARM_A_W2V_GOOGLE_NEWS_FAIR (rail; reproduces v1 arm A but on V=20k bigram-conditional metric)
- ARM_B_W2V_TEXT8_FULL_17M (clean; PROPERLY converged on full 17M-token text8, 5+ epochs, training_wall ~30 min not 1.82 sec)
- ARM_C_RANDOM_PROJECTION_FAIR (floor)
- ARM_D_CHAR_TRIGRAM_FAIR (floor; existing substrate baseline)

**Config:** N_DIM=8192, V=20000 (NOT 4000), N_TRAIN=100k, seeds=[7,13,29], TEMP_GRID extended down to [0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0], LAMBDA_GRID unchanged, report BOTH unigram-conditional AND bigram-conditional BPC per arm (the bigram-conditional is the load-bearing one for verdict).

### Anchor 2 (CONDITIONAL on Anchor 1 HARD_PASS_LEAKAGE_CONFIRMED, ~1-2 weeks substrate eng) -- Path C S1 SoftHebb + Eugenio-2025 hybrid

**Anchor pointer:** if Anchor 1 confirms leakage is real in the fair regime, the substrate cannot rely on word2vec pretraining and must build its own encoder. Path C S1 spec already exists in research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md. This drill surfaces a NEW candidate: Eugenio 2025 arxiv 2503.02057 "Hebbian learning the local structure of language" -- direct published precedent for Hebbian word-level encoder learning without pretraining. Worth slotting as S1 architecture variant or replacement.

**Substrate-product reading:** if substrate-owned Hebbian encoder reaches within 0.20 BPC of properly-trained clean word2vec on the fair-regime metric, the substrate has a leakage-free encoder path. This is the strategic answer per project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.

**Tier hint:** chain-grade-eligible if it lands within target band AND distinguishing-regime gate passes.

**Why-now:** conditional on Anchor 1 outcome; do not dispatch until Anchor 1 lands.

**Pre-reg HARD bands:**
- HARD_PASS: substrate-owned encoder BPC <= clean-w2v BPC + 0.20 on fair-regime bigram-conditional metric.
- HARD_FAIL: substrate-owned encoder BPC > clean-w2v BPC + 0.50.

### Anchor 3 (DEFERRED unless Anchor 1 lands HARD_FAIL_REGIME, ~3 hr CPU) -- measurement-regime calibration cell

**Anchor pointer:** if even V=20k bigram-conditional pins all arms within 0.10 BPC, run a calibration sweep over (V in {4k, 10k, 20k, 50k}) x (metric in {unigram-cond, bigram-cond, trigram-cond}) with a fixed arm pair (Google-News-w2v vs random-projection). The arm pair has a known large representational gap; whichever (V, metric) combo gives leakage_delta_random_minus_w2v > 0.5 BPC is the minimum-discriminating regime for any future encoder test on substrate.

**Substrate-product reading:** establishes the substrate's encoder-test methodology going forward. Permanent reference cell.

**Tier hint:** infrastructure / methodology cell; not cap_map-bumping.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): `notes/research_encoder_leakage_2x_3x_revival_2026-06-24.md`
- v1 cell metrics (the finding being revisited): `data/exp_substrate_clean_encoder_substrate_as_LM_v1/metrics.json`
- v1 cell prereg: `preregs/2026-06-23_clean_encoder_eval_harness_v1.md`
- v1 cell code: `experiments/exp_clean_encoder_eval_harness_v1.py` and `experiments/exp_substrate_encoder_ablation_on_fair_harness_v1.py`
- Path C substrate-owned encoder spec (for Anchor 2): `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
- USER directive on Path C: `notes/project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md`
- USER directive on brain-existence-proof prior: `notes/feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md`
- New 2025 precedent (Eugenio arxiv 2503.02057): https://arxiv.org/abs/2503.02057 -- not yet in substrate roadmap.

## Contract

exp_dev:
- Pre-flight: schema-vet via tools/exp_dev/formula_selftests.py.
- Smoke at run_mode='smoke' with sigma=0 sanity rail (recall=1.000 across arms).
- HDLAB_EXP_NAME set; commit-first for any new cell file.
- Ship via queue (Anchor 1 is local_cpu_queue-eligible; ~2 hr CPU).
- Post-ship REMOTE VERIFY if dispatched to remote.
- Per [[feedback-no-experiment-design-in-prompts]]: cell structure decisions are exp_dev's; this hand-off only provides anchor pointer + pre-reg bands + why-now.

## Autonomy declaration

Research is not pre-designing the cell. exp_dev decides: cell file name, arm structure (the 4-arm suggestion above is a starting point not a contract), sweep mechanics, smoke design, dispatch routing (local_cpu_queue vs remote_cpu_queue), seeds count beyond minimum 3, partial-write checkpoint format. Research's contract is: anchor pointer + substrate-product reading + tier hint + why-now + pre-reg HARD bands. The bands are sacrosanct per negativity-bias rule; cell mechanics are exp_dev's call.
