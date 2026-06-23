# exp_dev hand-off — research: 5x deeper substrate-self-mapping gap (v2e)

**Filed-by.** research (Opus 4.7) 2026-06-23
**Trigger.** 5x deeper research drill on substrate-native self-mapping gap completed. v2c HARD_FAIL (3 seeds) + v2d-smoke confound (degenerate ground truth) closed the discriminator-tuning hypothesis class. New axis = modularity-Z + LRG + engram-allocation under degree-preserving null. Phase 1 V3 gate.
**Pause state.** Honors `data/orchestrator_paused.flag`. If paused, file only; do not ship.
**Cite.** `d:/AI/hd-instrument/notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` (parent research note; pre-reg bands + HARD_PASS/HARD_FAIL thresholds verbatim).
**Discipline.** Per [[feedback-no-experiment-design-in-prompts]] — this handoff names anchor candidates + pointers, not implementations.

---

## Anchor candidate (single, rank 1)

### Anchor 1: `substrate_self_map_v2e_modularity_Z_LRG_engram_v1`

**Anchor pointer.** `notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` section "Cheap decisive test (v2e pre-reg)"; parent data:
- `d:/AI/hd-instrument/data/exp_substrate_self_map_v2c/metrics.json` (3 seeds HARD_FAIL cluster_gap=-3)
- `d:/AI/hd-instrument/data/exp_substrate_self_map_v2d_discriminator_corrected_v1_smoke/metrics.json` (smoke confound; 2/20 anchors in v1-families = degenerate ARI)
- `d:/AI/hd-instrument/notes/research_2x_revival_overnight_negatives_2026-06-23.md` (parent 2x revival note; supersedes its v2d recommendation)
- `d:/AI/hd-instrument/notes/research_substrate_self_map_2x_revival_full_store_mechanism_null_drill_2026-06-22.md` (3x mechanism-null drill; carry-forward IRF + config-null upgrades)

**Substrate-product reading.** Genuine substrate-native self-mapping IS the Phase 1 V3 gate. Without it, Phase 2 (autoatom) and Phase 3 (substrate proposes new mathematics) have no traction. The 5x drill closes the discriminator-tuning hypothesis class; either v2e HARD_PASSes (Phase 1 closes; 6 new primitives candidate; autoatom can use multi-scale partition) OR HARD_FAILS (mechanism is encoder-bound; next move = substrate-native context-bundle encoder, 5-7 cycle research arc, not a 1-cycle cell). Either outcome unblocks the V3 program.

**Tier hint.** Five-axis upgrade bundle with diagnostic ablations:
- v2e-FULL (all 5 upgrades; primary HARD_PASS attempt): ~3hr remote_cpu
- v2e-1 (IRF weighting only): ~1hr
- v2e-3 (modularity-Z gamma sweep only): ~1hr
- v2e-4 (LRG diffusion tau sweep on v2c cached adjacency): ~30min
- v2e-5 (engram-allocation iterative refinement on v2c clusters): ~30min
Total ~6hr remote_cpu; bundles isolation of which of the 5 upgrades is load-bearing.

Mechanism = char_trigram_atom (UNCHANGED — encoder is not the bottleneck per v2b signal at small scope; testing this directly is HARD_FAIL diagnosis) + KGStore_multivalue_Hebbian (with IRF weighting) + 2hop_Jaccard adjacency + Louvain at gamma sweep {0.5, 1.0, 2.0, 4.0, 8.0} + degree-preserving config-null (100 rewires/seed for Z) + Laplacian heat-kernel at tau {0.1, 1.0, 10.0, 100.0} for scale-stability + engram-allocation iterative refinement (softmax-temp-with-cluster-size-decay, 10 iterations). N_DIM=4096, n_anchors=150 (raised from 100), 5 seeds (raised from 3 for stability at production scope), full Store admit (~200k triples).

**Why-now.** v2/v2b/v2c/v2d-smoke is a 4-attempt cascade in the SAME hypothesis class (encoder=char_trigram + primitives=KGStore+multi_hop + discriminator=cluster-statistic-or-ARI-vs-external-truth). v2d-smoke proved the external ground truth (v1-Director-lexical families) is structurally degenerate — only 2/20 anchors have v1-family labels. The 5x drill's structural innovation: **abandon external ground truth entirely**. Modularity-Z (vs degree-preserving null) is by-construction CAN-fail and doesn't need an external partition; LRG diffusion-time stability is scale-invariant and intrinsic. Both are lit-canonical (Reichardt-Bornholdt 2006 Potts mapping; Villegas 2024 LRG; Fortunato 2007 resolution-limit). The composition with Hebbian-KG substrate IS novel; P deflated to **0.32** (cap 0.40 per 3-prior-null empirical Bayes).

**HARD_PASS thresholds (verbatim from parent):** Z(gamma*) >= 2.5 AND partition_stability_LRG >= 0.50 AND consensus_entropy_ratio <= 0.7 AND recall >= 0.95 AND cv across seeds <= 0.15.

**HARD_FAIL thresholds (verbatim from parent):** Z(gamma*) <= 1.5 at EVERY gamma in the sweep AND partition_stability_LRG <= 0.30.

**MIDDLE_BAND:** Z(gamma*) in (1.5, 2.5) OR partition_stability_LRG in (0.30, 0.50). Recall >= 0.95.

**Cost.** ~6hr remote_cpu for full ablation bundle; ~3hr if only v2e-FULL.

---

## Bayes-flip threshold (PRE-COMMITTED)

After 4 attempts in the same hypothesis class with progressively-deeper diagnoses, the empirical Bayes prior on "another discriminator fix works" is 0.40. If v2e ALSO returns HARD_FAIL, P(discriminator-class works) drops to ~0.20 — below the threshold for further cycles in this class. **The forcing function is structural:** atomize META "lexical-encoder + relational-Hebbian pipeline cannot resolve capability-grade structure at full Store density" and pivot to encoder substitution.

This pre-commit is important: do NOT propose v2f / v2g / etc. with yet another discriminator tweak after v2e HARD_FAIL. The next move IS encoder substitution (5-7 cycle research arc), and the 5x drill has done the prework to justify it.

---

## Parked anchors

None new in this drill. The 2x revival note's parked anchors (cross_corpus_compose, b2_tinystories) remain parked.

---

## Context pointers (NOT summaries)

- Parent research note (5x drill, full diagnosis + thresholds + calibration penalty): `d:/AI/hd-instrument/notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md`
- 2x revival parent (carry-forward IRF + config-null upgrades): `d:/AI/hd-instrument/notes/research_2x_revival_overnight_negatives_2026-06-23.md`
- 3x mechanism-null parent: `d:/AI/hd-instrument/notes/research_substrate_self_map_2x_revival_full_store_mechanism_null_drill_2026-06-22.md`
- Failure metrics:
  - `d:/AI/hd-instrument/data/exp_substrate_self_map_v2c/metrics.json`
  - `d:/AI/hd-instrument/data/exp_substrate_self_map_v2d_discriminator_corrected_v1_smoke/metrics.json`
- Existing primitives to compose: `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py` + `d:/AI/hd-instrument/hdlab/kg_traversal.py` + `d:/AI/hd-instrument/hdlab/multi_hop.py` + `d:/AI/hd-instrument/hdlab/iterative_attractor.py` (for engram-allocation refinement)
- META atoms referenced: `[[by-construction-saturation]]`, `[[cleanup-load-bearing]]`, `[[Shannon-floor]]`
- Phase 2 design (gated by this v2e verdict): `d:/AI/hd-instrument/notes/substrate_self_improvement_phase_2_autoatom_design_2026-06-22.md`

---

## Contract section

- **Allowed work:** author + smoke v2e-FULL or any of the ablation variants {v2e-1, v2e-3, v2e-4, v2e-5}; commit + dispatch via `tools/queue_add.sh` to remote_cpu (per GPU-underutilization rule, this is matmul-bound on Hebbian writes + 100-rewire null which IS GPU-friendly if torch.cuda used — exp_dev decides routing per Fix #24). Pre-flight `tools/predispatch_check.py substrate_self_map_v2e` per Fix #26.
- **Disallowed:** changing the encoder (char_trigram_atom is the control; this is part of the HARD_FAIL diagnostic — proving encoder is the bottleneck). Changing N_DIM below 4096 (the production-regime requirement). Changing n_seeds below 5 (stability assessment requires it). Bypassing the pre-reg bands above.
- **Verdict mapping:**
  - HARD_PASS → Phase 1 closes; queue strategy_scribe for cap_map bump + Phase 2 autoatom dispatch trigger; queue 6 hdlab/ primitive promotion cells.
  - MIDDLE_BAND → ablation isolates load-bearing upgrade; queue single-axis follow-on at the load-bearing variant; partial Phase 1 close on the load-bearing primitive only.
  - HARD_FAIL → atomize META "lexical-encoder + relational-Hebbian pipeline cannot resolve capability-grade structure at full Store density"; queue research drill on substrate-native context-bundle encoders; DO NOT propose v2f with another discriminator.

## Autonomy declaration

exp_dev decides: (a) routing (local_cpu vs remote_cpu vs overnight_queue per heaviness audit); (b) ablation variant ordering (recommend v2e-4 LRG-on-v2c-cache FIRST as cheapest diagnostic — if LRG stability ≤ 0.30 on v2c cached adjacency, the meta-conclusion is reached without running the full bundle; this is the 5x drill's load-bearing single-test); (c) whether to ship the full bundle or only the LRG-cache test first; (d) seed selection (5 seeds {7, 17, 23, 31, 41} recommended to compose with v2c's prior seeds for differential analysis).

— Research (5x deeper handoff)
