# exp_dev hand-off -- research: real-encoder cross-N attenuation disambiguation (2x drill)

**Filed-by**: Research sub-agent (2x operational drill, 2026-06-06)
**Trigger**: d:/AI/hd-instrument/notes/research_drill_real_encoder_cross_N_attenuation_disambiguation_2x_2026-06-06.md
**Pause state**: check data/orchestrator_paused.flag before dispatching any queue_add.sh

Per [[feedback-no-experiment-design-in-prompts]]: this file names ANCHOR CANDIDATES and
WHY they are ready; exp_dev does the implementation, sweep grid, and threshold formulas.
Do NOT treat the threshold values in this file as the final pre-reg -- exp_dev re-derives
per its own protocol.

---

## Anchor candidates (rank-ordered)

### 1. Cell D -- disambiguation sweep (HIGHEST PRIORITY)

**Why now**: This is the gating cell. H1 vs H2 disambiguation routes ALL subsequent
investments. Running any rescue cell before this result is premature optimization.

**Anchor pointer**: "disambiguation N-sweep: Q_real vs Q_synthetic as a function of N at
fixed alpha, Hadamard codebook"

**Substrate-product reading**: cheap decision point; 30 min CPU; binary output that
determines which rescue path gets engineering resources.

**Tier hint**: CPU-only; no GPU required; runs in remote_cpu_queue.

**Why-now**: the level-2 algebraic analysis (Section 1 of research note) shows H1 and H2
make DIFFERENT Q(N) curve shapes (sub-linear decay vs linear decay); this cell directly
measures which shape is observed.

---

### 2. LC1 N-sweep addendum -- SHM Q(N) characterization

**Why now**: Level-2 analysis shows SHM (already queued as LC1) attacks BOTH H1 and H2
via two independent mechanisms (anisotropy decorrelation + H2 subspace saturation delay).
Adding an N-sweep to the already-queued LC1 cell costs minimal extra compute and upgrades
LC1 from "nice-to-have" to "attacks both hypotheses simultaneously."

**Anchor pointer**: "LC1 SHM N-sweep: run LC1 at N in {384, 1024, 2048} to characterize
Q(N) shape for SHM vs Hadamard"

**Substrate-product reading**: if Q(N) is flat under SHM, SHM ships as the single highest-
leverage training-free intervention for all downstream experiments.

**Tier hint**: CPU-only; extends the already-queued LC1 anchor.

**Why-now**: the subspace saturation delay mechanism is a new level-2 finding (not in
level-1); validates SHM as a combined H1+H2 rescue before committing to more complex
alternatives.

---

### 3. H2-A -- SRHT codebook at large N

**Why now**: If Cell D confirms H2 (or mixed), SRHT is the cheapest H2 rescue (one-time
random sign-flip diagonal + Hadamard, zero retrieval mechanism changes). The algebraic
argument (Section 3b) shows SRHT converts systematic M^2/N interference to random
interference, recovering the synthetic-key Q(N) curve.

**Anchor pointer**: "SRHT codebook baseline: compare SRHT codebook vs fixed Hadamard at
N=2048 on real and synthetic keys"

**Substrate-product reading**: trivially implemented; ships as a one-line codebook
construction change; no training required.

**Tier hint**: CPU-only; run at N=2048 (where H2 effect is maximal per M^2/N formula).

**Why-now**: conditioned on Cell D result. Run if Cell D shows H2-dominant or mixed.

---

### 4. EA-1 -- PCA pre-whitening

**Why now**: cheapest encoder-architecture-aware intervention; one offline PCA + one O(d^2)
multiply per query. Attacks BOTH H1 (anisotropy) and H2 (by converting anisotropic
distribution to isotropic, making Hadamard near-optimal). If it passes, it ships as a
one-line preprocessing change to the substrate VQ layer.

**Anchor pointer**: "PCA pre-whitening: apply PCA whitening to encoder output before
sign-projection; measure capacity vs unwhitened Hadamard at N=384 on real encoder keys"

**Substrate-product reading**: multiplicative improvement across all downstream experiments;
no codebook redesign required.

**Tier hint**: CPU-only; N=384 baseline; ~25 min wall.

**Why-now**: independent of Cell D result; can run in parallel with disambiguation.

---

## Context pointers

- Research note (this drill):
  d:/AI/hd-instrument/notes/research_drill_real_encoder_cross_N_attenuation_disambiguation_2x_2026-06-06.md
- Prior level-1 note:
  d:/AI/hd-instrument/notes/research_drill_learned_codebooks_real_encoder_rescue_1x_2026-06-06.md
- v195 handoff template:
  d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

---

## Contract

exp_dev MUST:
- Check data/orchestrator_paused.flag before any queue_add.sh
- Pre-register HP/MID/HF bands per its own envelope-fail-band protocol (DO NOT copy
  threshold values from this file verbatim; re-derive per the anchor contracts)
- Run smoke gate before FULL sweep
- Post-ship REMOTE VERIFY (check queue.json for anchor presence)
- Self-test per formula-selftests on any closed-form formula used

## Autonomy declaration

exp_dev has full autonomy over:
- Exact anchor names (subject to _n<N> suffix contract where N is the sweep size)
- Sweep grid specifics (N values, seed count, FLIP values)
- Queue assignment (CPU vs GPU routing per torch.cuda grep)
- Implementation details for SRHT, PCA whitening, adaptive sign threshold
- Which of the 4 anchors to ship first given current queue state
