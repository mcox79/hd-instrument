# exp_dev hand-off — research: substrate-vs-brain timescale ratio (2x drill)

filed-by: research:opus
trigger: 2x deeper drill on substrate-vs-brain TIMESCALE RATIOS following parameter taxonomy B (modulatory + architectural taxonomy L5 caveat #3) and Skunkworks empirical finding (TAU_NEG=50 barely activates at N_TRAIN=100k ~24 chunks).
source note: `d:/AI/hd-instrument/notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md`
pause state: check `data/orchestrator_paused.flag` before dispatch

Per [[feedback-no-experiment-design-in-prompts]] — anchors below are POINTERS to substrate-mine candidates, not full pre-reg specs. exp_dev owns smoke + pre-reg + remote-verify per its role contract.

---

## Anchor candidates (rank-ordered)

### PRIMARY (rank 1) — substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1

**Anchor pointer:** 2x4 factorial isolating the TWO highest-leverage timescale corrections (dual-trace TAU_NEG/TAU_POS ratio × CLS-replay multi-pass count) at N=4096 / V=4000 / 100k tokens / 3 seeds.

- AXIS_1 (dual-trace ratio): {TAU_NEG=50 [current, 10x ratio], TAU_NEG=10 [brain-canonical 2x ratio]} at fixed TAU_POS=5
- AXIS_2 (CLS replay count): {N_REPLAY=1 [current], 10, 30, 100}
- 8 arms + 1 vehicle (no dual-trace, no CLS) = 9 arms total

**Substrate-product reading:** if HARD_PASS (TAU_NEG=10 and N_REPLAY=10-30 wins by ≥0.20 BPC), confirms the substrate-clock-hierarchy diagnosis and (a) corrects the Skunkworks-caught TAU_NEG mismatch, (b) validates multi-pass CLS-replay as continual-learning MOAT element, (c) sets correct defaults for all subsequent dual-trace and CLS cells.

**Tier hint:** TRACK_A_APPLY candidate (cap_map impact: corrects TAU_NEG default + enables multi-pass CLS-replay continual-learning capability).

**Why now:** the dual_trace_RESCUE_corrected_baseline_v1 cell is in overnight_queue with TAU_NEG=50 (the wrong value). If it HARD_FAILs that may be because of the ratio mismatch, not the dual-trace mechanism itself. Running the TAU_NEG sweep IN PARALLEL on a cheaper N=4096 rig disambiguates BEFORE the overnight_queue verdict lands. CLS-replay multi-pass is brain-strongly-supported (10^4-10^5 SWR/night vs substrate's 1x) and zero-novelty implementation.

**Cost estimate:** ~30-45 min CPU local (9 arms x 100k tokens at N=4096); piggyback on dual_trace test rig if possible.

### SECONDARY (rank 2) — cls_replay_multipass_n_replay_sweep_v1

**Anchor pointer:** ONLY if PRIMARY's N_REPLAY axis is load-bearing but TAU_NEG axis is null — isolate the N_REPLAY effect at production-scale N=8192. Sweep N_REPLAY ∈ {1, 10, 30, 100, 300} on continual-learning retention task.

**Substrate-product reading:** identifies the optimal N_REPLAY for substrate-LM continual-learning. The L2-vision MOAT element ("continual learning via CLS-replay") needs this characterization to be a deployable product feature.

**Tier hint:** TRACK_B_KG_CERT (architectural-default setting for CLS module)

**Why now:** ONLY if PRIMARY shows N_REPLAY > 1 lifts BPC. If PRIMARY shows N_REPLAY monotone-worse, defer indefinitely — single-pass replay is the substrate-correct choice and we should not multi-pass.

**Cost estimate:** ~60 min GPU (5 arms x ~12 min each at N=8192).

### TERTIARY (rank 3) — theta_gamma_k_count_saturation_audit_v1

**Anchor pointer:** EXISTING-CELL audit (no new cell needed); read metrics.json from in-flight + recently-landed lock-in cells with k_gamma=31 / k_theta=1 and check novelty_ratio. If at metric-cap consistently, by-construction saturation per the META atom is confirmed and the recommendation is to lower k_gamma to brain-canonical proportions.

**Substrate-product reading:** documentation work; surfaces whether the lock-in by-construction-saturation pattern (the brake on lock-in chain-grade tiering) is due to k_gamma=31 absolute count vs the 7:1 ratio.

**Tier hint:** MEASURED_MECHANISM audit; documentation update if confirmed.

**Why now:** zero compute cost (read existing metrics.json files); cheap closure on a META atom concern.

**Cost estimate:** ~5 min wall-time (read existing metrics).

---

## Context pointers (file paths, not summaries)

**Source research note:**
- `d:/AI/hd-instrument/notes/research_substrate_brain_timescale_ratio_2x_drill_2026-06-23.md`

**Direct parents:**
- `d:/AI/hd-instrument/notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md` (L5 caveat #3 surfaced the timescale-ratio drill)
- `d:/AI/hd-instrument/notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md` (TAU_POS/TAU_NEG 10x INVERTED ratio identified)
- `d:/AI/hd-instrument/notes/research_dual_trace_mechanism_elucidation_2026-06-23.md` (4-axis confound: sign / target / timescale / cardinality)

**Related in-flight cells (verdicts may invalidate or confirm timescale corrections):**
- `substrate_dual_trace_RESCUE_corrected_baseline_v1` (overnight_queue; running at TAU_NEG=50 wrong value per this drill)
- `cleanup_multi_iteration_v1` (af8c402990385f452; tests TIER_0 cleanup count assumption)
- `substrate_k_module_heterogeneous_compose_LM_v1` (overnight_queue; architectural axis)
- `substrate_ACh_query_conditional_read_gain_LM_v1` (remote_cpu_queue; TIMESCALE 6c per-query phasic ACh)
- `substrate_serotonin_mode_switch_bank_select_LM_v1` (remote_cpu_queue; TIMESCALE 6d slow tonic 5HT)
- `substrate_per_context_decode_temperature_LM_v1` (local_cpu_queue; TIMESCALE 6e per-token phasic NE)

**Methodology guardrail:**
- `d:/AI/hd-instrument/notes/research_neuroscience_methodology_for_substrate_lm_3x_drill_2026-06-23.md` — 6-arm factorial discipline; preflight spec; verdict lint

---

## Contract section

- exp_dev is empowered to author cells matching PRIMARY anchor without further research consultation.
- Smoke gate per exp_dev role contract.
- Pre-reg HARD_PASS / HARD_FAIL bands per envelope-fail-bands discipline (research note has pre-registered bands per timescale).
- Remote verify per standard exp_dev protocol.
- If pause flag present: DO NOT dispatch; file pre-reg note and wait for resume.

## Autonomy declaration

exp_dev decides:
- Exact smoke parameters (default N=512, ~20s)
- Whether to ship to local_cpu_queue (PRIMARY at N=4096 is light enough) or overnight_queue (SECONDARY at N=8192 needs GPU)
- Whether to piggyback PRIMARY on the dual_trace_RESCUE rig (most efficient if rig is reusable) OR ship standalone
- Whether to add 6-arm vehicle/A-only/B-only/A+B/B+A/random structure per neuroscience-methodology drill recommendation
- Whether to gate SECONDARY on PRIMARY verdict (recommended) or run them in parallel
- TERTIARY is read-only audit; can run in main thread without spawn

End of hand-off.
