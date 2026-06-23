# exp_dev hand-off -- research: encoder-side cleanup-ceiling-break

**Filed by:** Research (Opus 4.7) 2026-06-23
**Trigger:** Research delivery `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md` -- instantiates the HARD_FAIL conditional branch from `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` after 4 decoder-side cleanup mechanism families (att1 v1+v2, OMP, multi-bump CAN) all failed to lift argmax at sigma=1.5 N=512 M=200. Cleanup-ceiling is now identified as encoder-bound.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; if present, defer cell dispatch but keep hand-off filed for resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** exp_dev owns the actual cell design (smoke, gates, prereg). This hand-off provides anchor candidates + context pointers + autonomy declaration only.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP): `enc1_structured_n_lift_v1`
**Pointer:** research note section "Cheap decisive test (top candidate: structured N-lift with discriminating control)".
**Substrate-product reading:** if HARD_PASSES on ARM_SPARSE_FANIN_K5_N4096 OR ARM_DENSE_N4096, unblocks n4 / n9 / n10 / p1 cleanup-ceiling AND opens a new substrate-flat encoder primitive `sparse_fanin_codebook(M, N, K)` shippable to `hdlab/`. Bigram-gap closure for Path A pseudo-LM possible (0.3-0.7 bits) if sparse-fan-in is the load-bearing arm. Composes with existing `hdlab/whitening.py` ZCA primitive.
**Tier hint:** chain-grade-eligible if discriminating control (ARM_DENSE_N4096 vs ARM_SPARSE_FANIN_K5_N4096) cleanly separates dimension-vs-structure mechanism.
**Why now:** cheapest possible test (~5-10 min laptop CPU; numpy matmul only); fires the encoder-side branch that 3 prior negative drills have anticipated; directly subsumes whether the 5x-DEEPER 2026-06-21 cell (M=10k anisotropic learned keys, ARMs A,B,C still pre-reg, unfired) is worth the larger commitment (~1-2hr CPU); critical pre-screen.
**Pre-flight sanity (mandatory):** all 5 arms must achieve recall@1 = 1.000 at sigma=0.0. If any arm fails this, implementation bug, NOT mechanism rejection.

### Anchor 2 (CONDITIONAL on Anchor 1 HARD_PASS structured arms): revive 5x-DEEPER 2026-06-21 cell
**Pointer:** `notes/research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21.md` "Cheap decisive test (b)" section -- ARMs A (cerebellar K=5), B (fly-LSH + median-subtract on CERT 591), C (composition).
**Substrate-product reading:** validates the cleanup-ceiling-break mechanism at PRODUCTION regime (M=10k anisotropic learned BGE/pythia keys); chain-grade ship if HARD_PASS.
**Tier hint:** chain-grade.
**Why now:** Anchor 1 result tells you whether this larger cell is credible. If Anchor 1's ARM_SPARSE_FANIN_K5_N4096 HARD_PASSES, this cell becomes high-priority. If Anchor 1 HARD_FAILS sparse arms but HARD_PASSES dense arm, this cell may need design revision.

### Anchor 3 (CONDITIONAL on Anchor 1 HARD_FAIL or MIDDLE_BAND): `enc2_foldiak_antihebb_codebook_v1`
**Pointer:** research note section "#4. Foldiak 1990 anti-Hebbian decorrelation".
**Substrate-product reading:** tests whether structural-encoder approach needs MEANINGFUL ATOMS (substrate's actual production atoms) rather than random bipolar (Anchor 1's synthetic regime) to manifest. Substrate-native codebook construction; composes with continual-learning ingest.
**Tier hint:** measured-mechanism if positive; chain-grade requires production-encoder regime.
**Why now:** if random-bipolar regime is structurally limited (mu ~ 0 by construction means Foldiak / median-subtract are no-ops), then the mechanism may rescue only the production-encoder regime; Anchor 3 is the appropriate decisive test there.

---

## Context pointers (paths, not summaries)

- Parent research drill (HARD_FAIL conditional branch trigger): `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md`
- This drill: `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md`
- Substrate's deepest encoder finding (isotropy is load-bearing, not d_eff): `notes/research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_negative_robust_2026-06-20.md`
- 5x-DEEPER biology/brain branching drill (ARMs A,B,C pre-reg unfired): `notes/research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21.md`
- Existing whitening primitive: `hdlab/whitening.py`
- n10 whitening HARD_FAIL at production: `data/exp_n10_whitening_projection_revival_v1/metrics.json`
- Parent metrics (argmax baseline 0.023 at sigma=1.5): `data/exp_omp_sparse_coding_cleanup_v1/metrics.json`
- Multi-bump CAN MIDDLE_BAND: `data/exp_multi_bump_can_ensemble_cleanup_v1/metrics.json`
- Krotov HARD_FAIL: `data/exp_att1_iterative_attractor_v2_low_storage_ratio_krotov_v1/metrics.json`
- n4 k-WTA at N=16384 (suggests dimension alone insufficient): `data/exp_n4_kwta_soft_decode_v1/metrics.json`

---

## Contract (exp_dev autonomy declaration)

- exp_dev OWNS:
  - cell file authoring (`enc1_structured_n_lift_v1.py`, smoke + full)
  - prereg file (`preregs/2026-06-23_enc1_structured_n_lift.md`) with HARD_PASS / HARD_FAIL / MIDDLE_BAND thresholds per arm (research note "Falsifiable predictions" section is the source-of-truth for proposed thresholds; exp_dev may adjust within research-pre-reg bounds with justification)
  - smoke-gate cell (sigma=0 sanity = 1.000 across all 5 arms)
  - full-cell dispatch via queue_add
  - per-arm metrics.json emission + Skunkworks VET
- Research OWNS:
  - mechanism interpretation post-verdict
  - cap_map row updates
  - follow-up drill design (Anchor 2 dispatch if Anchor 1 HARD_PASS; Anchor 3 if Anchor 1 HARD_FAIL/MIDDLE_BAND)
- Orchestrator/Director OWNS:
  - prioritization vs other queue items
  - pause-flag gating
  - Anchor 2/3 follow-up dispatch trigger

---

## Cost / runtime

- Anchor 1: ~5-10 min laptop CPU (numpy matmul, 5 arms x 5 sigmas x 3 seeds at N<=4096 M=200; sub-second per arm-seed)
- Anchor 2: ~1-2 hr CPU + possible GPU for encoder forward (CERT 591 projection on BGE/pythia keys)
- Anchor 3: ~1 hr CPU (Foldiak iteration on M=200 atoms; sub-second per iteration; converge in O(10-100) iterations)

---

## Cross-thread composition pointers

- Composes with `feedback-empowered-to-experiment-where-lit-says-dismissed`: lit-scan said random projection lift is JL-distance-preserving (effectively a no-op for argmax recovery), but the substrate-native variant (sparse-fan-in K=5 + median-subtract) is structurally different and may rescue where JL alone cannot.
- Composes with `feedback-results-to-application-cadence-same-cycle`: if Anchor 1 HARD_PASSES, atomize `sparse_fanin_codebook` to Store AND ship to `hdlab/` same cycle.
- Composes with `feedback-substrate-mine-capacity-before-extrapolating`: scour Store FIRST for existing chain-grade sparse-fan-in primitives before declaring this novel (Drosophila MB K=6-8 cells may already be substrate-shipped from `research_2x_drill_ARCH_A_Drosophila` 2026-06-18).
