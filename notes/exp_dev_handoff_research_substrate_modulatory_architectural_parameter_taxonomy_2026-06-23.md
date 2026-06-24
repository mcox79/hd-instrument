# exp_dev hand-off — research: substrate modulatory + architectural parameter taxonomy

filed-by: research:opus
trigger: 3x deep research drill on substrate modulatory + architectural parameter taxonomy
source note: `d:/AI/hd-instrument/notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md`
pause state: check `data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]] — anchors below are POINTERS to substrate-mine candidates, not full pre-reg specs. exp_dev owns smoke + pre-reg + remote-verify per its role contract.

---

## Anchor candidates (rank-ordered)

### PRIMARY (rank 1) — substrate_compose_order_x_compose_function_2x2_factorial_v1

**Anchor pointer:** 2×2 factorial isolating the TWO highest-leverage parameters identified in the taxonomy (compose order × compose function) at N=4096 / V=4000 / 100k tokens / 3 seeds.
- AXIS_1: compose order ∈ {brain-canonical sparse→bind→cleanup→read, REVERSED}
- AXIS_2: compose function ∈ {multiplicative-shared-target, sigmoidal-additive-heterogeneous-targets}
- 4 arms + 1 vehicle (plain rank-1 Hebbian) = 5 arms total

**Substrate-product reading:** if HARD_PASS (canonical+sigmoid-add wins by ≥0.20 BPC), confirms that the parameter taxonomy is the substrate's load-bearing tuning surface — sets correct defaults for ALL subsequent cells AND identifies the substrate-product positioning as "K-module heterogeneous-algebra compose engine with biologically-motivated control".

**Tier hint:** TRACK_A_APPLY candidate (cap_map impact if HARD_PASS)
**Why now:** taxonomy is fresh; 4 in-flight cells will land in 4-24 hours testing INDIVIDUAL axes — this 2×2 tests the INTERACTION; gives clean factorial verdict to anchor the next planning round.

**Cost estimate:** ~20 min CPU local (5 arms × ~4 min each at N=4096); cheap.

### SECONDARY (rank 2) — substrate_K_sweep_at_fixed_compute_v1

**Anchor pointer:** K-sweep ∈ {1, 4, 8, 16} at fixed total parameter count (so each bank shrinks as K grows: N_per_bank = 8192/K), with heterogeneous algebraic structures per bank.

**Substrate-product reading:** identifies the OPTIMAL K for substrate at N=8192, V=4000. Levy-Horn-Ruppin theory predicts log-lift ∝ K · log(N/K) up to a per-bank-capacity collapse point. Finding the inflection point sets the architectural default for ALL future K-module cells.

**Tier hint:** TRACK_B_KG_CERT (architectural-default setting)
**Why now:** ONLY if k_module_heterogeneous_compose_LM_v1 (currently overnight_queue) HARD_PASSes. If that HARD_FAILs, defer this cell — K wasn't load-bearing.

**Cost estimate:** ~40 min GPU (4 arms × ~10 min each at N=8192).

### TERTIARY (rank 3) — substrate_per_context_T_extended_with_combined_features_v1

**Anchor pointer:** per-context T with COMBINED features: T(c) = T_base · σ(α · H(p_sub) + β · (1 - max_cos)) — sigmoidal-additive form matching the compose-function brain canonical from L3-A.

**Substrate-product reading:** only useful if per_context_decode_temperature_LM_v1 (in-flight local_cpu_queue) HARD_PASSes on the simpler entropy-only form. This cell tests whether the BRAIN-CANONICAL sigmoidal-additive form lifts above the simpler entropy-only form.

**Tier hint:** MEASURED_MECHANISM (decode-time refinement)
**Why now:** purely conditional on per_context simpler version landing; defer if it HARD_FAILs.

**Cost estimate:** ~10 min CPU local.

---

## Context pointers (file paths, not summaries)

**Source research note:**
- `d:/AI/hd-instrument/notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md`

**Related in-flight cells (verdicts will inform anchor choice):**
- `substrate_k_module_heterogeneous_compose_LM_v1` (overnight_queue; shipped 20:21)
- `substrate_dual_trace_RESCUE_corrected_baseline_v1` (overnight_queue; shipped 20:28)
- `substrate_per_context_decode_temperature_LM_v1` (local_cpu_queue; shipped 20:28)
- `substrate_ACh_query_conditional_read_gain_LM_v1` (remote_cpu_queue; shipped 20:36)
- `substrate_serotonin_mode_switch_bank_select_LM_v1` (remote_cpu_queue; shipped 20:47)
- `substrate_sparse_receiver_energy_diagnosis_v1` (remote_cpu_queue; shipped 20:37)

**Prior research notes (for context):**
- `d:/AI/hd-instrument/notes/research_negative_landings_evidence_totality_synthesis_2026-06-23.md` (4-class taxonomy of negatives; 80% rescuable)
- `d:/AI/hd-instrument/notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md` (Brzosko sequential)
- `d:/AI/hd-instrument/notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md` (Levy-Horn-Ruppin)

**Methodology guardrail:**
- `d:/AI/hd-instrument/notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md` — 6-arm factorial discipline; preflight spec; verdict lint

---

## Contract section

- exp_dev is empowered to author cells matching PRIMARY anchor without further research consultation.
- Smoke gate per exp_dev role contract.
- Pre-reg HARD_PASS / HARD_FAIL bands per envelope-fail-bands discipline.
- Remote verify per standard exp_dev protocol.
- If pause flag present: DO NOT dispatch; file pre-reg note and wait for resume.

## Autonomy declaration

exp_dev decides:
- Exact smoke parameters (default N=512, ~20s)
- Whether to ship to local_cpu_queue (PRIMARY at N=4096 is light enough) or overnight_queue (SECONDARY K-sweep at N=8192 needs GPU)
- Whether to defer PRIMARY pending pivotal verdicts (recommendation: ship PRIMARY in parallel — it tests INTERACTION axes independently of individual-axis cells)
- Whether to add 6-arm vehicle/A/B/A+B/B+A/random structure per neuroscience-methodology drill recommendation

End of hand-off.
