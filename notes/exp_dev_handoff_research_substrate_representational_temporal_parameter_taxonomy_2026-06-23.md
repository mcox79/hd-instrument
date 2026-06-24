# exp_dev hand-off — research: substrate representational + temporal parameter taxonomy

**Filed by:** Research (Opus 4.7-1M) 2026-06-23
**Trigger:** Research drill `notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` BEFORE dispatch; ferry through orchestrator routing per Fix #14 (spawn budget ≤3).

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off contains ANCHOR POINTERS only. exp_dev owns implementation, pre-reg numerics, and cell-author.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP PRIORITY — load-bearing parameter taxonomy resolution)

- **Anchor pointer:** `exp_parameter_taxonomy_amplitude_x_f_grid_v1`
- **Substrate-product reading:** confirms whether amplitude scaling (1/sqrt(f) gain on sparse-bipolar entries — the under-recognized load-bearing parameter) is the dominant fix for 4 of 10 substrate-as-LM negative landings this arc
- **Tier hint:** Tier-1 (cheap-CPU, ~30min local, single 2D parameter sweep, HARD bands both directions pre-reg)
- **Why now:** USER directive on parameter taxonomy + receiver-SNR diagnosis already in flight + viability shotgun would benefit from corrected defaults BEFORE producing LIVE/DEAD map
- **Pre-reg HARD bands (in research note section "CHEAP DECISIVE TEST"):** CRITERION_A: recall_lift(f=0.02, sigma=16) >= 0.30; CRITERION_B: ARM_B recall vs f flat to within 0.05; HARD_FAIL_1: recall_lift < 0.10

### Anchor 2 (HIGH — dual-trace ratio axis missing from existing ablation)

- **Anchor pointer:** `exp_dual_trace_tau_ratio_sweep_v1` (NEW; not the in-flight 4-axis ablation)
- **Substrate-product reading:** tests whether brain-canonical tau_neg ≈ 0.5 * tau_pos beats substrate's current 10x INVERTED ratio (tau_neg=50, tau_pos=5). Skunkworks empirically caught "tau_neg barely activates at N_TRAIN=100k" — taxonomy says ratio inversion is the explanation.
- **Tier hint:** Tier-2 (medium-CPU, dependent on dual-trace 4-axis landing first to confirm baseline)
- **Why now:** add as 5th axis after the current 4-axis ablation lands; CHEAP add-on
- **Decision rule:** if Anchor 1 lands HARD_PASS, prioritize Anchor 2; if Anchor 1 lands HARD_FAIL or MIDDLE_BAND, deprioritize and re-anchor on receiver structure

### Anchor 3 (MEDIUM-HIGH — by-construction-saturation fix via lock-in P sweep)

- **Anchor pointer:** `exp_lock_in_P_discriminating_regime_v1`
- **Substrate-product reading:** tests whether lock-in P=64 (current default) is over-spec vs Lisman-canonical P=7. Hypothesis: by-construction-saturation patterns Skunkworks repeatedly catches are because P=64 is too easy.
- **Tier hint:** Tier-2 (cheap-CPU, ~30min local)
- **Why now:** companion to chain-grade discriminator design; should be standing default for future cells
- **Pre-reg HARD bands:** sweep P in {7, 16, 32, 64}; HARD_PASS if P=64 recall = 1.000 + P=16 recall in [0.4, 0.95] (discriminating regime exists at P=16); HARD_FAIL if all P > 4 saturate at 1.000

---

## Context pointers (file paths, not summaries)

- Research drill: `d:/AI/hd-instrument/notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md`
- Source diagnosis: `d:/AI/hd-instrument/notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (matched-filter-energy theorem)
- Synthesis context: `d:/AI/hd-instrument/notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (8/10 negatives are parameter-default-failures)
- Methodology infra: `d:/AI/hd-instrument/notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` (preflight_spec.yaml integration)
- Existing dual-trace ablation: `d:/AI/hd-instrument/notes/research_dual_trace_mechanism_elucidation_2026-06-23.md` (tau RATIO not currently varied — Anchor 2 fills the gap)

---

## Contract

- exp_dev owns: cell-author smoke / Fix #17 measurement / dispatch decision / queue routing / verdict pre-reg numerics
- Research owns: PARAMETER TAXONOMY claim + HARD bands + brain-analog framing + literature citations
- Skunkworks owns: cert-tier assignment + by-construction-saturation gate

## Autonomy declaration

exp_dev decides: which anchor to dispatch first; whether to bundle Anchor 1 + 3 in one cell (parameter-sweep with amplitude AND lock-in P as separate axes); whether to route via orchestrator hdi_orchestrator (CPU-bound, local queue acceptable); whether smoke gate suffices.
