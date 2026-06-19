# exp_dev hand-off -- research: small-brain substrate template

Filed-by: research sub-agent
Date: 2026-06-04
Trigger: d:/AI/hd-instrument/notes/research_drill_small_brain_learning_substrate_template_2x_2026-06-04.md

## Pause state block

This hand-off is discovered on emergency-refill cycles. Exp_dev should check
data/orchestrator_paused.flag before dispatching any experiment from this file.
If paused, hold hand-off pending resume.

## Per [[feedback-no-experiment-design-in-prompts]]

This file contains TASK + WHY + CONTRACT + AUTONOMY pointers only. It does NOT specify
anchor names, sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds,
queue choice, or ETA. Exp_dev chooses all design parameters autonomously.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
Anchor pointer: Sparse-single-modulator (SSM) vs dense-multi-modulator (DMM) ablation
Substrate-product reading: Does switching from dense bipolar (+/-1, f=0.50) to sparse
  binary (0/1, f=0.05 via k-WTA preprocessing) + single RPE modulator match or beat
  the current multi-channel (4-8 modulator) architecture on associative pattern retrieval?
Tier hint: Tier-1 (load-bearing architecture decision; affects all downstream Cap 1-4 work)
Why now: The 5-arm ablation at N=4096 found no differentiation from K=1 single-channel
  baseline. This drill identifies the algebraic root as CODE DENSITY, not modulator count.
  The cheap test (2-cell CPU ablation, ~60s wall, N=4096, M=500 pairs) is immediately
  actionable. No GPU needed.

### Anchor 2 (SECONDARY)
Anchor pointer: Sparse coding capacity cliff location under f sweep
Substrate-product reading: At what sparseness f does the substrate's capacity cliff
  (currently at K/N=0.56 for dense codes) move or disappear? If cliff disappears at f<0.10,
  sparse reframing resolves the capacity constraint structurally.
Tier hint: Tier-2 (validates or refutes sparse reframing; complements Anchor 1)
Why now: If Anchor 1 passes, this determines the operational regime (what f to use).
  If Anchor 1 fails, this tells us whether a different f might rescue it.

### Anchor 3 (FOLLOW-ON if Anchor 1 passes)
Anchor pointer: MBON-readout layer scaling (M_out sweep from 1 to 50 readout neurons)
Substrate-product reading: How does retrieval accuracy scale with MBON count (readout
  layer size) at fixed N=4096, f=0.05? Is there a saturation point (analogous to 34 MBONs
  in fly mushroom body)?
Tier hint: Tier-2 (capacity calibration after architecture confirmed)
Why now: Only meaningful if Anchor 1 confirms the sparse-SSM architecture. Gives the
  product-engineering parameter for how many readout neurons to implement.

---

## Context pointers

Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_small_brain_learning_substrate_template_2x_2026-06-04.md
Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Prior failing ablation context: cap_map Cap 4 / multi-modulator 5-arm ablation at N=4096

Key algebraic results from research note (for exp_dev reference, not binding):
  - Sparse capacity advantage: alpha_c(sparse,f=0.05) ~ 3.3 vs alpha_c(dense) ~ 0.14
  - Pattern overlap: sparse f=0.05 gives ~200x lower inter-pattern overlap than dense bipolar
  - Biological template: Drosophila MB at N_KC=2000, f=0.05, 1 modulator (dopamine), M~30-100
  - Substrate scale N=4096 is within 1 OOM of Drosophila MB scale

---

## Contract

The exp_dev agent commits to:
1. Read this file and the linked research note before designing anchors
2. Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds before any run
3. Use generic math terminology in any external references
4. NOT design the experiment inline in this file -- the research note is context only
5. Verify queue name uniqueness before ship (per [[feedback-ship-name-collision]])
6. Use appropriate wall-time budget: Anchor 1 is CPU-local (<60s), not GPU
7. Apply per-experiment --timeout formula before queue_add.sh

## Autonomy declaration

Exp_dev has full autonomy to:
  - Choose anchor names, sweep parameters, threshold values
  - Decide whether to combine Anchors 1+2 in a single run or sequence them
  - Reject any anchor candidate and substitute a better-motivated alternative
  - Adjust N, f, M, and M_out values based on implementation constraints
  - Determine whether GPU is needed or CPU suffices
