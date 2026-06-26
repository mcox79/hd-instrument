# exp_dev hand-off -- research: GAP 3 compositional generalization 5x drill

filed-by: research (Opus 4.7 1M)
trigger: research note d:/AI/hd-instrument/notes/research_gap3_compositional_5x_drill_2026-06-26.md
pause state: respect data/orchestrator_paused.flag at dispatch time

Per [[feedback-no-experiment-design-in-prompts]]: the research note above is the AUTHORITATIVE source for cell design. exp_dev is the experiment author. This handoff points to anchors, NOT pre-designs the cell.

## Anchor candidates (rank-ordered)

### Anchor #1 -- LARS-VSA relational bottleneck (TIER-A, P_deflated=0.42)

- substrate-product reading: gain first true schema-extraction primitive; flip GAP 3 row from RED to GREEN; pairs with capability-suite ARM_COMPOSITIONAL_GEN regression test
- tier hint: Tier-A; cell-author smoke + Fix #17 measurement; cell name suggestion `gap3_lars_vsa_relational_bottleneck_v1`
- why-now: substrate has all primitives (binding, codebook, iterative_attractor); 1-day local_cpu_queue cost; direct VSA precedent (arxiv 2405.14436 published 2024); decisive 3-arm discriminator design
- pre-reg bands per [[feedback-experiment-bias-master-checklist]]: HARD_PASS heldout >= 0.50 on any arm; HARD_FAIL all arms <= 0.10; MIDDLE_BAND [0.10, 0.50]
- failure-mode guard: per [[feedback-fix28-verify-per-arm-metrics]], read per-arm metrics.json BEFORE cross-arm framing
- contamination guard: synthetic data only per [[feedback-clean-encoder-tests-no-contamination]]
- N regime: 8192 minimum per HRR-crosstalk lesson (NOT 2048)

### Anchor #2 -- Percolation model of compositional emergence (TIER-A-equivalent, P_deflated=0.35)

- substrate-product reading: reframes GAP 3 from "mechanism-missing" to "data-coverage statement"; concrete prescription for which atomic pairs to add
- tier hint: Tier-A; cell name suggestion `gap3_percolation_emergence_threshold_v1`
- why-now: arxiv 2408.12578 (ICLR 2025) gives a sharp falsifiable prediction; pairs with substrate-mine breadth (588 atoms); under-drilled field per advisor (scope-expansion candidate)
- pre-reg bands: HARD_PASS substrate's heldout-accuracy-vs-coverage curve fits power-law within +/- 0.15 of predicted exponents; HARD_FAIL no power-law shape

### Anchor #3 -- Resonator network factor decomposition (TIER-A, P_deflated=0.40)

- substrate-product reading: substrate gets multi-hop chain reasoning; pairs with kg_traversal.py + multi_hop.py for chain-grade KG completion
- tier hint: Tier-A; cell name suggestion `gap3_resonator_decode_v1`
- why-now: Frady-Sommer resonator literature mature; substrate has codebook + iterative_attractor primitives ready; bottleneck is the resonator wrapper

### Anchor #4 -- CLS replay-driven schema extraction (TIER-B, P_deflated=0.30)

- substrate-product reading: continual-learning + compositional in one (substantial moat)
- tier hint: Tier-B; higher impl cost (~3 days); two-channel architecture
- why-now: brain-grounded mechanism per [[feedback-brain-is-existence-proof-higher-prior]]; substrate already has predictive_coding.py as foundation

### Anchor #5 -- Tropical / max-plus semiring attention (TIER-B, P_deflated=0.25)

- substrate-product reading: length-generalization on algorithmic reasoning (adjacent capability, not direct GAP 3)
- tier hint: Tier-B; novel synthesis for substrate; arxiv 2505.17190 (2025 paper)
- why-now: only if Anchors #1-#3 produce mixed results; lower P but novel direction

## Context pointers (file paths, not summaries)

- Research note: `d:/AI/hd-instrument/notes/research_gap3_compositional_5x_drill_2026-06-26.md`
- Prior compositional precedent: `d:/AI/hd-instrument/notes/skunkworks_to_testbed_exp_dev_compositional_depth_FORM_C_AMENDED_full_mode_L5_0p70_L8_0p30_smoke_1p0_was_INFLATED_atom_prose_overclaims_2026-06-16.md`
- Phase 3 abstraction ceiling: `d:/AI/hd-instrument/notes/testbed_to_research_exp_dev_PIVOT_PHASE_3_15_of_15_ABSTRACTION_distillation_0p70_to_0p82_ceiling_reached_2026-06-13.md`
- Substrate primitives ready: `d:/AI/hd-instrument/hdlab/predictive_coding.py`, `hdlab/iterative_attractor.py`, `hdlab/binding.py`, `hdlab/multi_hop.py`, `hdlab/kg_traversal.py`
- Capacity precedent (NOT compositionality, but adjacent): `d:/AI/hd-instrument/notes/project_session_2026-06-23_strategic_decisions_full_arc.md`
- Memory disciplines: `[[feedback-experiment-bias-master-checklist]]`, `[[feedback-clean-encoder-tests-no-contamination]]`, `[[feedback-substrate-mine-capacity-before-extrapolating]]`, `[[feedback-fix28-verify-per-arm-metrics]]`, `[[feedback-brain-is-existence-proof-higher-prior]]`

## Contract section

exp_dev: read this handoff + the linked research note; choose ONE anchor (per pause flag + spawn-budget ceiling Fix #14 <=3); cell-author smoke per checklist; ship via queue_add.sh; verify remote landing per Fix #21 poll. Do NOT chain to Anchor #2 unless #1 HARD_PASS or HARD_FAIL is unambiguous.

per [[feedback-results-to-application-cadence-same-cycle-atomize-and-hdlab-update]]: if HARD_PASS, atomize same cycle + ship hdlab/ primitive (relational_bottleneck.py or resonator_decode.py).

## Autonomy declaration

exp_dev decides: which anchor first; smoke regime; per-seed runtime budget; queue routing (local_cpu_queue default; overnight_queue if cell-author smoke shows >1hr runtime); pre-reg envelope-fail-bands (use the ranges in research note as starting point; adjust per substrate-mine).

research does NOT decide: experiment design, dispatch ordering, queue choice. research is a literature-and-mechanism input. cert-classification is cert-owner's call per [[feedback-cert-owner-overrides-director-via-by-construction-saturation]].

---

end of handoff.
