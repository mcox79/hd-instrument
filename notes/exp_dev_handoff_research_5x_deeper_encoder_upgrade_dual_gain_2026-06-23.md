# exp_dev hand-off — research: 5x-DEEPER encoder-upgrade dual-gain (Shannon-floor PIVOT)

**Filed by:** Research (Opus 4.7-1M) 2026-06-23
**Trigger:** Research delivery `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` — Shannon-floor META (cert row 675) PIVOT direction. Two prior META branches (N-INDEPENDENT, M-INDEPENDENT) closed; branch #3 (learned-encoder keys at production-regime) remains open. ENC1 HARD_FAIL was on **synthetic random bipolar codebook**; this drill tests whether structured/learned encoders escape the Shannon-floor at production.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; if present, defer cell dispatch but keep hand-off filed for resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** exp_dev owns the actual cell design (smoke, gates, prereg). This hand-off provides anchor candidates + context pointers + autonomy declaration only.

**Per [[feedback-no-inter-session-routing-notes-deprecate-ferry-mechanism]]:** this file is a CERT TRAIL artifact, not a ferry. exp_dev session picks up on next emergency-refill cycle via filesystem scan.

**USER directive 2026-06-22:** NO MiniLM, NO BGE, NO proprietary embeddings. All three anchor candidates below comply (substrate-native or substrate-trainable only).

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP, dual-gain decisive test): `enc_dual_gain_softhebb_vs_fpe_v1`

**Pointer:** research note section "Cheap decisive test (pre-registered)" — 4-arm sweep (BASELINE_BIPOLAR / CHAR_TRIGRAM / SOFTHEBB_3LAYER / FPE_PHASE), two metrics per arm (CLEANUP recall@sigma=1.5 + Path-A test BPC), 3 seeds.

**Substrate-product reading:** if SoftHebb HARD_PASSES BOTH metrics (P=0.15-0.20 compound), substrate gets a triple-leverage encoder primitive that unblocks (a) Shannon-floor exit at production (cleanup), (b) bigram-gap closure path A (substrate-native LM finally beats unigram), (c) substrate-native KG entity encoding (USER-directive-compliant replacement for MiniLM in Path B). Single primitive lifts three substrate-products simultaneously — true triple-leverage if HARD_PASS.

**Tier hint:** chain-grade-eligible if discriminating-regime gate cleanly separates branch #3 outcome AND dual-gain manifests. Otherwise tier as measured-mechanism for whichever metric HARD_PASSES.

**Why now:** 
- Branch #3 of Shannon-floor META is the ONLY unclosed cell; this drill explicitly fills it.
- 3rd encoder-side attempt (2 prior unfired + ENC1 HARD_FAIL); CALIBRATION-PENALTY HARDER applied (P capped at 0.40); honest framing.
- ~30-60 min CPU wall (laptop sufficient; N=4096; substrate-trainable forward-only).
- HARD_PASS on cleanup OR BPC OR both = high-value outcome; HARD_FAIL across all 3 non-baseline arms = high-value chain-grade saturation of Shannon-floor META.
- ALL OUTCOMES are useful — this is a true discriminator cell.

**Pre-flight sanity (mandatory):** sigma=0 sanity recall@1=1.000 across ALL 4 arms; if any arm fails, implementation bug NOT mechanism rejection.

**Substrate-trainable encoder implementation pre-requisites:**
- `hdlab/softhebb_encoder.py` (NEW; ~1 day impl): 3-layer SoftHebb network per Moraitis 2021 fig 2. Input = char-trigram bundled HD; Layers = N=4096→8192→8192→4096 with soft-WTA (tunable τ) + Hebbian weight update. Forward-only, no backprop, no global error signal. Trained on text8 N_TRAIN=100k via streaming ingest.
- `hdlab/fpe_encoder.py` + `hdlab/fpe_cleanup.py` (NEW; ~1 day impl): FPE phase encoding per Frady-Sommer 2109.03429 + Bremer-Orchard 2412.00488 CLE+MLE iterative cleanup.
- Both new primitives should ship to `hdlab/` per `feedback-results-to-application-cadence-same-cycle`.

### Anchor 2 (CONDITIONAL on Anchor 1 cleanup-pass + BPC-mixed): `softhebb_pathA_isolate_v1`

**Pointer:** research note Falsifiable Predictions #1 + #2 isolated.
**Substrate-product reading:** if Anchor 1 shows cleanup HARD_PASS but BPC mixed, isolate Path-A in dedicated cell with hyperparameter sweep (SoftHebb τ, layer dims, training epochs) to confirm BPC < unigram floor.
**Tier hint:** measured-mechanism if positive; chain-grade requires both metrics.
**Why now:** only if Anchor 1 shows partial signal; otherwise SKIP.

### Anchor 3 (CONDITIONAL on Anchor 1 ALL HARD_FAIL): `char_lstm_substrate_trainable_v1`

**Pointer:** research note L2 filter table — char-LSTM deferred row.
**Substrate-product reading:** if substrate-native forward-only encoders ALL HARD_FAIL, the lift requires backprop. Char-LSTM at ~10-50M params is the small-model substrate-trainable baseline; text8 char-level achieves ~1.5 BPC at full size. Substrate scope: not full char-LSTM but extract its LATENTS as substrate atoms.
**Tier hint:** measured-mechanism only; cert-grade requires substantial backprop infra (substrate currently has none for encoder training).
**Why now:** ONLY if Anchor 1 closes branch #3 with full HARD_FAIL across SoftHebb + FPE + char-trigram. Backprop infra investment ~1 week — high cost; defer until clearly indicated.

---

## Context pointers (paths, not summaries)

- This drill: `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md`
- Parent encoder-side drill: `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md`
- Decode-side cousin (SimVQ orthogonal lever): `notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md`
- Shannon-floor META cert ledger row 675 (chain-grade-eligible per branch-c closure)
- N-INDEPENDENT branch closure: `data/exp_cleanup_floor_N_DIM_scan_v1/metrics.json`
- ENC1 5-arm HARD_FAIL on synthetic: `data/exp_enc1_structured_n_lift_v1/metrics.json`
- Path-A current state (BPC=7.864 MIDDLE_BAND): `data/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1/metrics.json`
- Substrate isotropy load-bearing finding: `notes/research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_negative_robust_2026-06-20.md`
- 5x-DEEPER 2026-06-21 (subsumed by SoftHebb): `notes/research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21.md`
- Existing substrate-native text encoder (branch #3 baseline arm): `hdlab/char_trigram_encoder.py`
- Existing whitening primitive (composes post-SoftHebb): `hdlab/whitening.py`
- USER directive (no MiniLM): `memory/feedback_substrate_mine_capacity_before_extrapolating_2026-06-22.md` AND prior MiniLM-restriction memory entries

---

## Contract (exp_dev autonomy declaration)

- **exp_dev OWNS:**
  - Cell file authoring (`enc_dual_gain_softhebb_vs_fpe_v1.py`, smoke + full)
  - Prereg file (`preregs/2026-06-23_enc_dual_gain_softhebb_vs_fpe.md`) with HARD_PASS / HARD_FAIL / MIDDLE_BAND thresholds per arm per metric (research note "Falsifiable predictions" section is source-of-truth for proposed thresholds; exp_dev may adjust within research-pre-reg bounds with justification)
  - NEW substrate primitive implementations (`hdlab/softhebb_encoder.py`, `hdlab/fpe_encoder.py`, `hdlab/fpe_cleanup.py`) — same-cycle ship per `feedback-results-to-application-cadence`
  - Smoke-gate (sigma=0 sanity = 1.000 across all 4 arms)
  - Per-unit checkpoint + restartable (per `feedback-long-cells-must-checkpoint-resume-restartable`)
  - Full-cell dispatch via queue_add (local_cpu_queue)
  - Per-arm metrics.json emission + Skunkworks VET
- **Research OWNS:**
  - Mechanism interpretation post-verdict
  - cap_map row updates (Shannon-floor META branch #3 outcome)
  - Follow-up drill design (Anchor 2/3 dispatch decisions)
- **Orchestrator/Director OWNS:**
  - Prioritization vs other queue items
  - Pause-flag gating
  - Anchor 2/3 follow-up dispatch trigger based on Anchor 1 verdict

---

## Cost / runtime

- **Anchor 1:** ~1-2 days implementation (SoftHebb + FPE primitives) + ~30-60 min CPU cell wall (4 arms × cleanup sweep + Path-A BPC at N=4096 N_TRAIN=100k 3 seeds). Laptop CPU sufficient (no GPU needed at this size).
- **Anchor 2:** ~30 min CPU cell (only Path-A isolated, hyperparameter sweep).
- **Anchor 3:** ~1 week implementation (backprop infra setup) + ~4 hr GPU (char-LSTM training); HIGH cost; defer unless clearly indicated.

---

## Pre-reg hard bands (source-of-truth from research note)

### CLEANUP RECALL @ sigma=1.5 (per arm vs baseline 0.022):
- **HARD_PASS:** recall >= 0.20 AND cv <= 0.30
- **HARD_FAIL:** recall <= 0.05
- **MIDDLE_BAND:** 0.05 < recall < 0.20

### PATH-A TEST BPC (per arm vs unigram 7.738):
- **HARD_PASS:** BPC < 7.738 AND cv <= 0.05 (substrate finally beats unigram)
- **HARD_FAIL:** BPC >= 7.864 (no improvement over current cell)
- **MIDDLE_BAND:** 7.738 < BPC < 7.864

### DUAL-GAIN COMPOUND:
- **HARD_PASS DUAL:** ARM achieves BOTH cleanup HARD_PASS AND BPC HARD_PASS in same seed-mean.

### DISCRIMINATING-REGIME GATE (C5):
- If ARM_CHAR_TRIGRAM recall(sigma=1.5) >= 0.20 alone: branch #3 of META is FALSE; encoder geometry IS the lever at production.
- If ARM_CHAR_TRIGRAM HARD_FAILS but ARM_SOFTHEBB or ARM_FPE HARD_PASSES: branch #3 is true ONLY for naive bag-of-trigrams; richer substrate-native encoders rescue.
- If ALL 3 non-baseline arms HARD_FAIL: branch #3 CLOSES; Shannon-floor chain-grade saturated.

### SANITY (mandatory):
- sigma=0 recall@1=1.000 across ALL 4 arms; if violated, cell has implementation bug.

---

## Cross-thread composition pointers

- Composes with `feedback-empowered-to-experiment-where-lit-says-dismissed`: lit-scan says SoftHebb has only been demonstrated on MNIST/CIFAR images, not text substrate; this is a substrate-novel application worth the test cost.
- Composes with `feedback-results-to-application-cadence-same-cycle`: if Anchor 1 HARD_PASSES on any arm, atomize the relevant primitive to Store AND ship to `hdlab/` SAME CYCLE.
- Composes with `feedback-substrate-mine-capacity-before-extrapolating`: substrate already has chain-grade learned-encoder atoms via 600K-pattern composition; the question of whether THOSE escape Shannon-floor is empirical (this cell tests it).
- Composes with `feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text`: post-verdict, read per-arm metrics.json NOT verdict_msg summary text; per-arm cleanup AND BPC must be reported separately.
- Composes with Fix #26 pre-dispatch verify-the-referent: run `tools/predispatch_check.py enc_dual_gain_softhebb_vs_fpe_v1` before dispatch to catch duplicates / recent-HARD_FAIL re-dispatches.

---

## Outcome routing (for follow-up dispatch decisions)

- **If Anchor 1 cleanup HARD_PASS on SoftHebb arm:** ship `softhebb_encoder` to `hdlab/`; route to Skunkworks for chain-grade tier assessment; revive Path B KG with SoftHebb-encoded entities.
- **If Anchor 1 BPC HARD_PASS on SoftHebb arm:** atomize `substrate_native_LM_beats_unigram` chain-grade candidate; flag major milestone.
- **If Anchor 1 dual-gain HARD_PASS on SoftHebb:** triple-leverage atom; PRIORITY route to META.
- **If Anchor 1 ALL 3 non-baseline HARD_FAIL:** Shannon-floor chain-grade saturated; META atom `META_shannon_floor_chain_grade_saturated_branch3_closed_2026-06-23`; descope sigma>=1.5 permanently; route to Strategy for envelope re-statement.
- **If Anchor 1 ARM_CHAR_TRIGRAM HARD_PASSES alone:** META atom `META_shannon_floor_synthetic_codebook_only_not_production`; META de-saturates; existing substrate primitives confirmed at production scale.

-- Research (Opus 4.7-1M)
