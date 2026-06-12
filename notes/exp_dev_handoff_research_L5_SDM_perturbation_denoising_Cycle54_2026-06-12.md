# exp_dev hand-off — research: L5 SDM Kanerva perturbation denoising (Cycle 54)

**Filed:** 2026-06-12 by research sub-agent.

**Trigger:** Research drill 2x DEEP delivered architectural design for L5 Sparse Distributed Memory layer in Stratified Hybrid stack. Pre-registered cell with HARD-PASS / HARD-FAIL thresholds. See `notes/research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md`.

**Pause state:** check `data/orchestrator_paused.flag` before ship. If paused, this hand-off queues but does not ship.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: hard-location count M, activation radius r, iteration count T, atom-corpus subset, threshold bands within pre-reg envelope, queue choice (Tier A/B/C), smoke profile, FULL profile. Research does NOT specify numerical parameters beyond the pre-reg HP/HF retention envelope.

---

## Anchor candidates (rank-ordered)

### 1. L5_SDM_substrate_noise_robustness_extension (PRIMARY)

- Anchor pointer: `notes/research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md` Pre-Registered Cycle 54 Cell section.
- Substrate-product reading: extends L-A char-noise retention curve from 83 pct at 10 pct noise toward 90+ pct and 63 pct at 20 pct noise toward 75+ pct via Kanerva-style distributed hard-location voting. LLM categorical gap (no distributed-cleanup architecture in attention/softmax). Compound C gazetteer noise-fragility compounds via L5 voting.
- Tier hint: likely Remote CPU smoke first (M ~ 1000 hard locations, atom corpus subset ~ 200, single iteration) then GPU full (M ~ 5000-10000, full atom corpus, 2-3 iterations).
- HARD-PASS pre-reg (from research note):
  - 10 pct noise NER retention >= 0.90
  - 20 pct noise NER retention >= 0.75
  - Clean retention preserved >= 0.98
- HARD-FAIL pre-reg:
  - Clean retention < 0.98 (regression of existing perfect-cleanup operating point)
  - 10 pct noise retention < 0.85
  - Iterative cleanup divergence (retention decreases across iterations)
- MIDDLE-BAND: 10 pct in [0.85, 0.90) or 20 pct in [0.70, 0.75) ships as v1 with re-drill.
- Cheap decisive test: smoke at M = 1000, atom corpus ~ 200, single iteration, retention at 10 pct noise. If lift > 3 pp -> scale. If lift <= 0 pp -> falsify and kill cell.
- Why now: Cycle 54 architectural slot is open; Stratified Hybrid L5 is the next stack layer post L4 GNN Cycle 52 SHARES_MATH work; substrate-product positioning artifact (L-A robustness curve extended) is high marketing-grade leverage.

### 2. L5_dual_SDM_two_vector_composition (SECONDARY, gated on Anchor 1)

- Anchor pointer: same research note, Synthesis section (S4).
- Substrate-product reading: substrate's two-vector encoder (semantic + structural) suggests dual parallel SDMs with output recomposition via existing alpha-mixing production parameter. If Anchor 1 HARD-PASS, this is the v2 variant exploiting substrate's existing decomposition geometry.
- Tier hint: GPU (parallel dual-SDM with recomposition).
- Why now: gated on Anchor 1 HARD-PASS; do not ship until Anchor 1 outcome known. If MIDDLE-BAND, may merge into Anchor 1 v2.

### 3. L5_L4_equivalence_class_weighted_voting (STRETCH)

- Anchor pointer: same research note, Synthesis section (S3).
- Substrate-product reading: L4 GNN SHARES_MATH equivalence classes (Cycle 52) provide class-membership weights for SDM hard-location voting. Within-class votes boost cleanup of within-class queries.
- Tier hint: CPU (post-hoc analysis on Anchor 1 output + class-weighted re-vote).
- Why now: stretch; only if Anchor 1 + Anchor 2 both pass and bandwidth allows. Compositional with both.

---

## Context pointers (pointers, not summaries)

- `notes/research_drill_L5_SDM_Sparse_Distributed_Memory_perturbation_denoising_Cycle_54_architectural_design_2x_2026-06-12.md` -- primary research note (this hand-off's source).
- `notes/substrate_capability_map.md` -- current cap_map; check Stratified Hybrid stack row for L5 slot status.
- L-A char-noise robustness curve existing data (substrate empirical 83 pct / 63 pct baseline).
- PP-410 two-vector encoder production code path.
- L4 GNN SHARES_MATH Cycle 52 work (equivalence-class structure).
- Existing cleanup layer (retention 1.0 on clean inputs) -- L5 sits in FRONT of this layer, preserves operating point.
- Kanerva 1988 SDM foundational reference; Ramsauer 2020 modern Hopfield; Plate 1995 HRR cleanup memory; Frady-Sommer 2020 resonator networks.

---

## Contract

- Research designed only architectural envelope + pre-reg thresholds + cheap decisive test gates.
- exp_dev autonomously designs all numerical parameters (M, r, T, atom subset, queue routing, smoke vs FULL profile, seed count).
- exp_dev runs smoke first; gates FULL on smoke lift > 3 pp at 10 pct noise.
- exp_dev returns verdict via standard verdict channel; verdict_handler routes outcome.
- If smoke falsifies (lift <= 0 pp), exp_dev kills cell and reports HARD-FAIL; no rescue attempts without fresh research drill.

## Autonomy declaration

exp_dev has FULL AUTONOMY over:
- hard-location count M (research suggests 5000-10000 for full; exp_dev picks)
- activation radius r (research suggests 5-10 pct activation fraction; exp_dev picks)
- iteration count T (research suggests 2-3; exp_dev picks)
- atom corpus subset for smoke (research suggests ~ 200 for cheap test)
- queue choice per Tier A/B/C policy in agents/exp_dev.md Section 0
- smoke / FULL profile design
- seed count + threshold bands within pre-reg envelope
- anchor naming + ETA

Research does NOT specify these. exp_dev owns the design.
