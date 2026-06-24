# exp_dev hand-off — research: sparse-cleanup compose breakage diagnosis

**Filed-by:** Research (Opus 4.7-1M)
**Date:** 2026-06-23
**Trigger:** companion to `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md`
**Source negative:** `data/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1/metrics.json` HARD_FAIL_1
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; if paused, hold

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off contains anchor candidates + context pointers + autonomy declaration. exp_dev OWNS cell design (smoke gate, pre-reg envelope, ship-via-queue_add).

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (PRIMARY) — `exp_sparse_receiver_energy_diagnosis_v1`

**Anchor pointer:** decisive test of matched-filter-energy hypothesis at f-grid
**Substrate-product reading:** confirms or refutes the receiver-side -17dB diagnosis; CHEAPEST path to either fix or repivot
**Tier hint:** MM (measurement_mechanism, single hypothesis test); chain-grade-eligible if Pearson r >= 0.85 on grid
**Why-now:** the source research's predicted P=0.60 brain-compose lift produced empirical 0.187 — gap = -0.79. Drill correction routes to a SINGLE cheap cell that identifies the mechanism class (energy loss vs cleanup pathology vs composition interference). Until this lands, every sparse-bipolar arm in flight is under-powered by unknown amount.
**Runtime estimate:** ~30min CPU local
**Pre-reg HARD bands (per research note L4 Prediction 1):**
- HARD_PASS: Pearson r(recall, sqrt(f*N)/sigma) >= 0.85 across (f in {0.005, 0.01, 0.02, 0.10, 0.5, 1.0}, sigma in {16, 32, 64, 128}) grid
- HARD_FAIL: r < 0.50 (matched-filter-energy is NOT primary mechanism — different bug; refer back to Research for re-drill)
- MIDDLE_BAND: r in [0.50, 0.85] — partial; matched-filter explains some variance, other mechanism also contributes

### ANCHOR 2 (CONDITIONAL on Anchor 1 HARD_PASS) — `exp_theta_gamma_nested_brain_amplified_compose_v2`

**Anchor pointer:** repeat the brain-compose cell with amplitude-scaled sparse codebook (entries +/- 1/sqrt(f) instead of +/- 1)
**Substrate-product reading:** restores the source research's Prediction 2 (brain-compose beats single-frequency at mid-noise) with corrected receiver math
**Tier hint:** chain-grade-eligible if BRAIN_AMPLIFIED@sigma=32 exceeds SINGLE_LOCKIN@sigma=32 by >=0.05
**Why-now:** if matched-filter-energy is the primary bug, this is the cleanest substrate-native fix and revives the brain-canonical compose mechanism
**Runtime estimate:** ~60min CPU local OR remote_cpu_queue
**Pre-reg HARD bands (per research note L4 Prediction 3):**
- HARD_PASS: delta(BRAIN_AMPLIFIED - SINGLE) >= +0.05 at sigma=32
- HARD_FAIL: delta < 0 at sigma=32 (brain-compose still doesn't beat single — deeper structural issue; pivot to TDM-gating Anchor 3 from source research)
- MIDDLE_BAND: delta in [0.0, +0.05] — partial; tune amplitude scaling or f-grid

### ANCHOR 3 (PARALLEL alternative) — `exp_sparse_bipolar_support_restricted_WTA_receiver_v1`

**Anchor pointer:** test brain-canonical receiver (thresholded coincidence on active support) as alternative to amplitude-scaling
**Substrate-product reading:** dual-validation; if Anchor 2 works AND Anchor 3 works, two equivalent paths to the same fix — pick by orthogonal trade-offs (numerical precision vs runtime)
**Tier hint:** MM; potentially chain-grade-eligible
**Why-now:** more substrate-novel than amplitude-scaling; closer to brain-canonical mechanism; may give different generalization characteristics
**Runtime estimate:** ~45min CPU local
**Pre-reg HARD bands:**
- HARD_PASS: ARM_THRESHOLDED_COINCIDENCE@f=0.02@sigma=16 >= 0.90
- HARD_FAIL: ARM_THRESHOLDED_COINCIDENCE@f=0.02@sigma=16 < 0.50 (receiver doesn't recover the gap)

---

## Context pointers (file paths only; no summaries)

**Empirical (load-bearing):**
- `d:/AI/hd-instrument/data/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1/metrics.json`
- `d:/AI/hd-instrument/data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json`
- `d:/AI/hd-instrument/data/exp_fair_harness_substrate_as_lm_v1/metrics.json`

**Source code (existing implementations):**
- `d:/AI/hd-instrument/experiments/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1.py` (the cell that HARD_FAILed; contains `make_sparse_bipolar_codebook` which needs the amplitude-scale fix)
- `d:/AI/hd-instrument/experiments/_seed_checkpoint.py` (per-seed checkpoint scaffold to reuse)

**Research notes:**
- `d:/AI/hd-instrument/notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (this drill; full L1-L5 + 6 predictions + algebra derivation)
- `d:/AI/hd-instrument/notes/research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` (source research; predictions revised by this drill)

**Hdlab/ primitives (existing; may need update):**
- `d:/AI/hd-instrument/hdlab/` — check for `sparse_bipolar.py`; if exists, audit for amplitude-scaling option; if absent, candidate for new primitive `hdlab/sparse_bipolar_amplified.py`

**Audit targets (cells currently in flight that may inherit the bug):**
- K-module heterogeneous compose cell abda9f08 — check sparse-bipolar arm receiver
- Substrate-as-LM cell — check sparse-bipolar amplitude

---

## Contract

exp_dev OWNS:
- Pre-reg envelope per Anchor 1 HARD bands above (mandatory both directions)
- Smoke gate at N=512, M=50 before full N=4096 dispatch (per [[long-cells-must-checkpoint-resume-restartable]])
- Self-tests on amplitude-scaling math: codebook L2 norm matches dense within 1e-3 at amplitude=1/sqrt(f); Pearson r computation correct on synthetic data; recall@1 calibration on known sigma=0 endpoint
- ASCII-only, no emojis
- Per-seed checkpoint + restartable (use `experiments/_seed_checkpoint.py`)
- Commit prereg note + cell to origin/main BEFORE remote dispatch
- Post-ship REMOTE VERIFY: `python tools/peek_arm_metrics.py <anchor_name>` to confirm per-arm metrics before tier framing

exp_dev does NOT:
- Re-design the hypothesis (research has set it; pre-reg is immutable post-dispatch)
- Skip the smoke gate
- Use raw +/-1 amplitude for the SPARSE-AMPLIFIED arm (the whole point is amplitude = 1/sqrt(f))

---

## Autonomy declaration

exp_dev decides:
- N_EVAL per arm (suggest 200 to match source cell)
- Seed count (suggest 3 to match source cell)
- f-grid resolution (suggest 6 points: {0.005, 0.01, 0.02, 0.10, 0.5, 1.0})
- sigma-grid (suggest 4 points: {16, 32, 64, 128} — covers low-saturation through high-collapse)
- Routing queue (local_cpu_queue recommended; ~30min)
- Whether to bundle Anchor 1 + Anchor 2 into a single mega-cell OR ship sequentially (Anchor 2 gated on Anchor 1 result)
- Whether to also include cleanup-on/off ablation in Anchor 1 (recommended yes; cheap; doubles data)

---

## Cert chain expectation

If Anchor 1 HARD_PASS + Anchor 2 HARD_PASS:
- Atomize: `sparse_bipolar_pays_sqrt_f_receiver_SNR_unless_amplitude_scaled_meta_2026-06-23` (META, chain-grade-eligible per Pearson r >= 0.85)
- Atomize: `brain_compose_nested_theta_gamma_with_amplitude_scaled_sparse_beats_single_frequency_at_mid_noise_2026-06-23` (META, chain-grade-eligible)
- Update CERT 592 framing in atoms.jsonl (add receiver-SNR companion atom)
- Add hdlab/ primitive: `hdlab/sparse_bipolar_amplified.py`
- Source research note `research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md` gets POST-EXPERIMENTAL CORRECTION section

If Anchor 1 HARD_FAIL:
- Route back to Research for re-drill on alternative failure mechanism (basin-overlap finite-N? attractor pathology? compose interference?)
- Do NOT dispatch Anchor 2 (gated on Anchor 1)

If Anchor 1 MIDDLE_BAND:
- Atomize partial finding
- Dispatch Anchor 3 (support-restricted WTA) as alternative; if BOTH partial, deeper structural investigation

---

*Hand-off filed 2026-06-23 by Research. Companion to research note. exp_dev auto-discovers via `notes/exp_dev_handoff_*.md` mtime sort.*
