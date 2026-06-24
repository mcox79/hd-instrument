# exp_dev hand-off — research: brain mechanisms NOT YET tested (2x drill)

**Filed by:** research role
**Date:** 2026-06-24
**Trigger:** USER strategic-vision drill — "we have definitive proof from biology that this works; just need to find the analogs." This handoff feeds exp_dev's emergency-refill auto-discovery (it scans notes/exp_dev_handoff_*.md sorted by mtime).

**Source research note:** `d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md`

**Pause state:** check `data/orchestrator_paused.flag` at pickup; honor.

**Per [[feedback-no-experiment-design-in-prompts]]:** this handoff contains POINTERS and CANDIDATE design sketches; exp_dev owns final cell-design + smoke + dispatch. Pre-reg HARD bands are the load-bearing contract; arms/sweeps/runtime are exp_dev's call.

---

## Anchor candidates (rank-ordered)

### Anchor #1: `brain_word_level_prediction_v1` (PRIORITY 1)

**Substrate-product reading:** measure substrate as a word-level predictor (V_word=4000), not character-level. Closes the "char-grain mismatch to brain's natural processing rate" gap identified in the research note L4.

**Tier hint:** if HARD_PASS, this is a candidate for chain-grade or measured-mechanism depending on Skunkworks tier review; brain-grounded mechanism + word-grain alignment with the canonical neural language stack.

**Why now:** the substrate has tested 30+ char-level mechanisms this session, all bounded by char-level baselines that are unnaturally strong vs the brain's word-grain measurement. This dispatch is the FIRST attempt to align measurement with brain processing grain — high probability of revealing aliveness that has been measurement-masked.

**Cell-design pointer:** see L4 of research note for full arm spec. Five arms (B1 word-unigram, B2 word-bigram, S_K1, S_K5, S_K10). Context K=[1,3,5,10] sweep. HRR role-bind composition over last-K words. Frozen char-trigram-meanpool encoder.

**Pre-reg HARD bands:**
- HARD_PASS: S_K5 top1 >= 1.30x B2 word-bigram AND BPW <= B2 - 0.4 bits
- MIDDLE_BAND: top1 in [1.10x, 1.30x] OR BPW in [B2-0.4, B2-0.1]
- HARD_FAIL: S_K5 top1 <= B2 OR BPW >= B2

**Estimated runtime:** ~10-15 min on remote_cpu (text8 hold-out)

**Smoke gate:** synthetic Zipfian text 10K chars; verify B2 baseline computes correctly + S_K1 == B1 in degenerate case.

---

### Anchor #2: `brain_predictive_coding_2level_v1` (PRIORITY 2, gated)

**Substrate-product reading:** add top-down feedback from a context-layer to the encoder-layer, implementing the Rao-Ballard PC equations in HD-substrate form. Two levels minimum (brain canonical).

**Tier hint:** measured-mechanism at minimum if HARD_PASS; brain-existence-proof is strong (10:1 cortical feedback ratio + 2024 lexico-semantic PC implementations).

**Why now:** substrate is currently feedforward-only across 30+ tested mechanisms. PC is the dominant brain theory and has NEVER been implemented in this substrate. Pair with Anchor #1 if word-grain wins (compose-stack hint).

**Cell-design pointer:** see L3.2 of research note. Three arms (A1 feedforward / A2 hier-no-top-down / A3 full PC with top-down via Hebbian-trained W_td). Composes with whatever grain Anchor #1 finalizes.

**Pre-reg HARD bands:**
- HARD_PASS: A3 BPC <= fair_harness - 0.30 AND A3 - A2 >= 0.15 bits (proves top-down matters, not just hierarchy)
- MIDDLE_BAND: A3 in [fair_harness - 0.30, fair_harness - 0.10]
- HARD_FAIL: A3 >= fair_harness OR A3 - A2 <= 0.02 bits

**Dependency:** gate on Anchor #1 outcome; if word-grain wins, run Anchor #2 at word grain.

---

### Anchor #3: `brain_working_memory_register_v1` (PRIORITY 3, gated)

**Substrate-product reading:** add a persistent WM register h that decays exponentially across tokens; brain Baddeley/Goldman-Rakic-canonical missing piece. Substrate currently holds NO state across tokens.

**Tier hint:** measured-mechanism if HARD_PASS; if compose-stacks with Anchor #1 + #2, candidate for chain-grade.

**Why now:** the AWD-LSTM cache pointer (Grave 2017) demonstrated +0.3-0.5 BPC lift from this exact mechanism. Substrate version with theta-grain word-level update has direct lit precedent.

**Cell-design pointer:** see L3.3 of research note. Three arms (A1 no-WM / A2 char-grain WM / A3 word-grain WM). Beta sweep in [0.85, 0.99]. Composes with Anchor #1 word-grain output.

**Pre-reg HARD bands:**
- HARD_PASS: A3 BPC <= fair_harness - 0.30, beta in [0.90, 0.95]
- MIDDLE_BAND: A2 or A3 in [fair_harness - 0.30, fair_harness - 0.10]
- HARD_FAIL: A3 >= fair_harness

**Dependency:** composes with Anchors #1 and #2.

---

## Context pointers (file paths, no summaries)

- Research note: `d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md`
- Companion in-flight (multi-iter cue-clamping): `d:/AI/hd-instrument/notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md` (pairs with PC top-down)
- Companion in-flight (DA duration): `d:/AI/hd-instrument/notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md` (pairs with WM beta-via-NE)
- Baseline reference: `d:/AI/hd-instrument/notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md` (fair_harness 7.3065 is canonical)
- Project pickup: `MEMORY.md` -> `project_session_2026-06-23_FINAL_pickup_state.md`

---

## Contract

- exp_dev OWNS final cell-design, arm-count, sweep-grain, runtime budget.
- exp_dev OWNS smoke-VET on synthetic data per [[feedback-smoke-clean-synthetic-data-not-substrate-state]].
- exp_dev OWNS dispatch routing (remote_cpu likely sufficient at V_word=4000; route via hdi_orchestrator if N_DIM>=8192 + multi-arm-heavy per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]]).
- exp_dev OWNS pre-dispatch verify-the-referent gate (`tools/predispatch_check.py`) per [[feedback-fix26-predispatch-verify-the-referent-gate]].
- exp_dev OWNS Fix #17 runtime measurement.
- Research OWNS pre-reg HARD bands (above).
- Skunkworks OWNS tier classification post-landing per [[feedback-fix28-recurring-skunkworks-correct-more-than-director]].

## Autonomy declaration

exp_dev decides: encoder choice (frozen char-trigram is research recommendation, but exp_dev may swap), exact context window K values, beta values for WM, smoke-test scaffolding, dispatch queue routing.

Research will NOT adjust the pre-reg bands post-hoc. If the verdict comes back MIDDLE_BAND, research will route the next-drill candidate per [[feedback-route-negatives-to-research-2x-3x-revival-drills]].
