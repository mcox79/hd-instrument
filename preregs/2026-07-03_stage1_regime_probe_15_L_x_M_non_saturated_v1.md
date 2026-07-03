# Pre-registration: Stage 1 Regime Probe 15 -- L (chain-depth) x M (codebook size) CROSS-TERM

**Date:** 2026-07-03
**Anchor:** `stage1_regime_probe_15_L_x_M_non_saturated_v1`
**Cell (core):** `experiments/_stage1_regime_probe_15_L_x_M_non_saturated_v1_core.py`
**Wrapper (seed=7):** `experiments/exp_stage1_regime_probe_15_L_x_M_non_saturated_v1_s7.py`
**Author:** exp_dev 2026-07-03 (Opus 4.7, agent-spawn)

## Purpose

Skunkworks atom #48 addendum flagged "L cross-terms (L x N, L x F, L x M, L x corr) unmapped."
- L x N was probed at P9 v2 (HOLD_PENDING_FULL).
- L x F was probed at P14 (HOLD_PENDING_FULL per Skunkworks VET Fix#28 hit #17).
- L x CLEANUP was probed at P13 (HOLD_PENDING_FULL).
- Probe 15 fills the **last unmapped L cross-term: L x M** (chain-depth vs codebook size).

The 5th CG_META axis `PHYSICS_LAW_cleanup_mechanism_M_scaling_non_Hebbian` (M-sweep FULL atom, established 2026-07-03) was established at **fixed L=2**. This probe asks: **does M-sweep behavior change with L**, or is the M-sweep atom L-invariant at cliff-adjacent SHARDED?

Framed per Skunkworks-authoritative language as **REGIME-EXTENSION** of atom #3 (chain-depth CG_META) and the M-sweep CG_META atom (5th physical law), NOT as new axis discovery. If H1 fires at 3-seed FULL cv<0.15, an atom candidate `EMPIRICAL_L_x_M_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1` may be promoted to MM_STANDARD as REGIME-EXTENSION of the M-sweep CG_META. If H2 fires, valuable NULL finding: M-sweep atom holds across L.

## Prior-work check (substrate-KB concept query, MANDATORY per USER-LOCKED 2026-07-01)

Ran `bash tools/substrate_query.sh "L chain depth M codebook cross-term SHARDED cliff cleanup capacity"` at 2026-07-03. Top hit: `RF/research_drill_free_probability_VSA_cleanup_clustered_codebook_capacity_2x_2026_06_12` at cosine=0.2832 (below 0.30 threshold). No prior arc cell at cosine>0.30. **Genuinely novel** as a L x M cross-term measurement; not a rediscovery.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: SHARDED FHRR chain composition (`run_chain` from `_stage1_physics_law_joint_composition_factorial_v1_core`)
- Storage: SHARDED (per-antecedent per-fan-out complex64 phasor codebook)
- CLIFF regime: N=512, F=1, corr=0.85, MECH=modern_hopfield (matches P6v2/P8/P12/P14 cliff-adjacent baseline)
- DEEP_SAT regime: N=8192, F=1, corr=0.60, MECH=modern_hopfield
- BETA: 8.0; ALPHA_SOFT: 0.5 (defaults from Option Y core)
- TR: 100 (FULL) / 40 (SMOKE)
- L axis: {1, 2, 4} band-only per Probe 12 VET (L=8,16 fall below 0.30 floor at CLIFF)
- M axis (CLIFF): {3200, 6400, 12800} -- spans capacity band (P6v2/P8 used M=6400; extend below and above)
- M axis (DEEP_SAT): {800, 1600} -- both saturate cleanly per bracket

BUNDLED FHRR chain composition is **EXCLUDED** per Skunkworks atom #49 (BUNDLED bimodal + collapses at L>=2 chain composition; cliff-adjacent regime does not intersect BUNDLED discriminating band).

## Sweep grid

**FULL (14 pts / seed):**
- CLIFF arm: L in {1,2,4} x M in {3200,6400,12800} x modern_hopfield = 9 pts
- DEEP_SAT arm (H3-NULL): L in {1,4} x M in {800,1600} x modern_hopfield = 4 pts
- SATURATION_PC arm (Gate D reproducer): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

**SMOKE (12 pts / seed):**
- CLIFF arm: L in {1,2,4} x M in {3200,6400,12800} x modern_hopfield = 9 pts (SMOKE = FULL grid on M axis)
- DEEP_SAT arm spot-check: L in {1,4} x M in {800} x modern_hopfield = 2 pts
- SATURATION_PC arm: 1 pt

## Discriminator (2-way L x M cross-term)

Given acc(L,M) grid on CLIFF arm (3 x 3):
- **M_effect_per_L[l]** = max_M acc(l,M) - min_M acc(l,M)  (M range at fixed L)
- **L_effect_per_M[m]** = max_L acc(L,m) - min_L acc(L,m)  (L range at fixed M)
- **M_effect_range** = max_l M_effect_per_L[l] - min_l M_effect_per_L[l]  (does M-effect depend on L?)
- **L_effect_range** = max_m L_effect_per_M[m] - min_m L_effect_per_M[m]  (does L-effect depend on M?)
- **interaction_metric** = max(M_effect_range, L_effect_range)  <- PRIMARY

Additional (informational, 2-way ANOVA-style):
- add_model[l,m] = row_mean[l] + col_mean[m] - grand_mean
- residual[l,m]  = acc[l,m] - add_model[l,m]
- **additive_residual_max_abs** = max |residual| across grid

**Noise-floor discipline (Fix#28 hit #17):** at TR=40 single-seed, 2SE on binary p is ~sqrt(p(1-p)/TR); at p~0.5 that is ~0.158. An interaction_metric at ~0.10 sits AT the SMOKE noise floor. The cell records `noise_2se` per phase point and `max_noise_2se` per grid. Honest H1 requires `interaction_metric >= max_noise_2se` at FULL scale (TR=100 halves the noise floor to ~0.10; still not a wide margin for a 0.10 interaction).

**Ceiling-confounded flag:** cells with `acc > 0.90` are flagged as ceiling-confounded (per Fix#28 hit #17 lesson). H1 requires `n_ceiling_confounded == 0` for the honest-signal condition.

## Hypotheses

**H1 (L x M interaction; REGIME-EXTENSION of M-sweep CG_META atom):**
`cliff.interaction_metric >= 0.10` AND `n_ceiling_confounded == 0` AND `interaction_metric >= max_noise_2se`
-> M-sweep behavior is L-conditional at cliff-adjacent SHARDED; M-sweep CG_META atom (5th physical law, established at fixed L=2) needs L-slice annotation as REGIME-EXTENSION.
Atom candidate: `EMPIRICAL_L_x_M_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1` MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL cv<0.15.

**H2 (L x M orthogonal, additive; NULL finding):**
`cliff.interaction_metric < 0.05`
-> M effect same across L values; M-sweep CG_META atom HOLDS at other L values without L-conditioning; L=2-fixed convention correctly labeled orthogonal for M-axis.
Atom candidate: `L_x_M_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_NEGATIVE_v1` MM_TENTATIVE.

**H3-NULL (DEEP_SAT null; sanity check):**
`deep_sat.interaction_metric < 0.05`
-> confirms cross-term degeneracy at saturation (per feedback_smoke_gates_null_hypothesis_2026-07-03 discipline).

## Envelope-fail-bands

- **CLIFF arm PASS band (H1):** interaction_metric in [0.10, 2.00] AND ceiling_confounded==0 AND interaction >= max_noise_2se
- **CLIFF arm PASS band (H2):** interaction_metric in [0.00, 0.05)
- **MIDDLE_BAND (weak cross-term):** interaction_metric in [0.05, 0.10)
- **DEEP_SAT H3-NULL fires:** interaction_metric in [0.00, 0.05)
- **SATURATION_PC PASS:** acc >= 0.95

## HP_SCOPE per-arm

- **CLIFF arm:** `[H1_cross_term_REGIME_EXTENSION | H2_orthogonal_NULL | MIDDLE_BAND_weak]`
- **DEEP_SAT arm:** `[H3_NULL_fires]` informational; MUST saturate (mean_acc >= 0.95); regime drift = HARD_FAIL
- **SATURATION_PC arm:** `[Gate_D_reproducer]` acc >= 0.95 required or HARD_FAIL

## Empirical bracket (MEASURED@scratchpad 2026-07-03 TR=40 seed=7)

**CLIFF (N=512 F=1 corr=0.85 SHARDED modern_hopfield):**

MEASURED@`C:/Users/marsh/AppData/Local/Temp/claude/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a/scratchpad/bracket_p15_L_x_M.py` 2026-07-03 (single-seed=7, TR=40):

```
        M=3200   M=6400   M=12800
L=1     0.8750   0.8750   0.7000
L=2     0.7500   0.7750   0.5000
L=4     0.5000   0.4000   0.3250
```

**Per-cell 2SE noise floor at TR=40 (THEORETICAL@2*sqrt(p*(1-p)/TR)):**
```
        M=3200    M=6400    M=12800
L=1     0.1045    0.1045    0.1449
L=2     0.1369    0.1319    0.1581
L=4     0.1581    0.1549    0.1481
```
- All 9 CELLS IN-BAND [0.30, 0.95] at seed=7 TR=40. `discriminating_fraction: 1.0`.
- No cell ceiling-confounded (`acc > 0.90`); max acc = 0.875.
- **Empirical interaction_metric at TR=40 seed=7:** M_effect_per_L = {L1: 0.175, L2: 0.275, L4: 0.175}; L_effect_per_M = {M3200: 0.375, M6400: 0.475, M12800: 0.375}; M_effect_range = 0.100; L_effect_range = 0.100; **interaction_metric = 0.100 (AT H1 threshold; AT single-seed noise floor)**.
- **MEASURED interaction sits AT threshold AND AT noise floor** -- HOLD_PENDING_FULL is the honest default per Fix#28 hit #17 lesson. FULL at TR=100 3-seed will halve the noise floor to ~0.10; need FULL to disambiguate H1 vs weak-signal MIDDLE_BAND.

**DEEP_SAT (N=8192 F=1 corr=0.60 SHARDED):**
MEASURED@`bracket_p15_deep_sat.py` 2026-07-03:
```
        M=800    M=1600
L=1     1.0000   1.0000
L=4     1.0000   1.0000
```
All four saturated exact; H3-NULL strongly predicted to fire (interaction = 0.000 exact).

**SATURATION_PC (L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine):**
- MEASURED@prior P6/P7/P8/P12/P14 selftests: acc >= 0.95 at TR=40 typical.

## Discipline gates satisfied (SCHEMA-VET pre-dispatch checklist)

- **cardinality_ok:** EXPECTED_N_UNITS_FULL=14, EXPECTED_N_UNITS_SMOKE=12; verdict counts phase_map length + emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch. Formula: (3 x 3) + (2 x 2) + 1 = 14; (3 x 3) + (2 x 1) + 1 = 12.
- **META_RULE_AF (ARMS-MUST-DIFFER) analog:** single-mechanism cell; verify (L=1, M=3200) vs (L=4, M=12800) at CLIFF produce distinct output hashes (proves both L and M axes fire structurally). `corner_hashes_distinct` emitted.
- **META_RULE_J (per-unit failure-class):** no bare except; failure-class propagates as RuntimeError with specific class name (NAN_IN_SHARDED_CODEBOOK, etc.).
- **META_RULE_K (discriminator-fires):** pre-reg declares `interaction_metric` as discriminator; smoke gates on infra + PC + escapes-saturation, NOT on discriminator firing (null-hypothesis discipline per feedback_smoke_gates_null_hypothesis_2026-07-03).
- **META_RULE_L (strictly-above-floor):** H1 uses `>= 0.10` (not just above 0); MIDDLE_BAND for [0.05, 0.10).
- **META_RULE_M (calibration):** `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited from Option Y core; empirical bracket at TR=40 confirms 9/9 cells in-band.
- **META_RULE_AH (atomic final metrics):** `tmp_replace` via `os.replace()` everywhere.
- **META_RULE_AG (baseline_in_band):** EMPIRICALLY CONFIRMED 9/9 CLIFF cells in [0.30, 0.95] at seed=7 TR=40 (see bracket above). `baseline_in_band: True`.
- **META_RULE_AC (numbers tagged):** all empirical numbers tagged MEASURED@ or HYPOTHESIZED@ or CITED@ or THEORETICAL@ in this pre-reg.
- **META_RULE_AF full-scale probe:** the ARMS-MUST-DIFFER-analog corner-hash check runs on the actual CLIFF phase points (full-scale) at smoke gate, satisfying discriminator-survives-scale by preview-arm construction.
- **except SystemExit: raise** before `except Exception` in wrapper (§8).
- **CRLB:** `crlb_n/a: "categorical accuracy; discriminator is grid-shape interaction metric, not a bit-level noise floor"` (noise-floor treated separately as binary 2SE per cell)
- **cell_chunked:** true (single-seed-per-file; s13, s19 to be authored later)
- **start_marker_written:** true (`_write_minimal_metrics(out_dir, "STARTED", ...)`)
- **crash_diagnostic_present:** true (`_write_import_crash_sentinel` in outer try/except)
- **heartbeat_present:** implicit -- per-phase-point flush prints (12/14 pts; <60s each on empirical bracket; timeout_s well under 30min so runner-side python -u sufficient).
- **defensive_error_checking:** `passed_all_4_patterns`
- **progress_logging:** `print_flush_true` -- every per-phase-point line uses `flush=True`. `progress_cadence_expected_s: 5` (per-phase-point ~0.1-1s CLIFF, ~0.5s DEEP_SAT per empirical bracket).

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point (build_rules + run_chain use `torch.matmul` internally); Python for-loop across (L, M) sweep is unavoidable (each phase point requires independent state build with fresh gen).

Wall-time smoke on CPU per empirical bracket ~5s (12 phase points at 0.05-0.5s each on N=512, M<=12800). FULL on CPU estimated ~15-30s (14 phase points at 0.15-1.5s each; TR=100 vs 40). GPU available but modest sizes (N<=8192, M<=12800) -- CPU adequate for smoke; FULL routes remote via Orchestrator per USER-LOCKED SMOKE-only-on-local-cpu.

## SCHEMA-VET §15 gates

- **A) effective_vs_nominal_parameter_audit:** L and M are directly settable in run_chain and build_rules; no partition/routing intermediary changes effective L or M. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** MEASURED bracket 9/9 CLIFF cells in-band [0.30, 0.95]. `discriminating_fraction: 1.0`; `>= 0.30` satisfied with margin.
- **C) signal_shape_compatibility_audit:** L and M both feed directly into run_chain / build_rules; no cross-primitive signal-shape edges introduced. `composition_edges: []` (single-primitive cell).
- **D) reproduce_prior_chain_grade_result_as_positive_control:** `positive_control_arms: [SATURATION_PC]` reproduces Gate D easy regime at TR=40; expected acc >= 0.95; tolerance 0.05 vs prior atoms (P6/P7/P8/P12/P14 baseline).
- **E) functional_requirement_decomposition_present:** functional requirement is "measure L x M cross-term interaction at cliff-adjacent SHARDED FHRR chain composition, framed as REGIME-EXTENSION of M-sweep CG_META atom." Existing chain-grade primitive `run_chain` addresses it directly (both L and M are native arguments). No new mechanism required.

## Provenance rail

Corpus is synthetic FHRR chain composition (no external data). `corpus_provenance: synthetic_sharded_fhrr_chain_composition_L_x_M_cross_term_v1`. No LLM calls (`_LLM_CALL_COUNTER` asserted at 0 before final write).

## Sibling wrappers plan

- `exp_stage1_regime_probe_15_L_x_M_non_saturated_v1_s7.py` (authored 2026-07-03)
- s13, s19 to be authored post-Tailscale-restore for 3-seed FULL replication via Orchestrator (MM_STANDARD promotion requires 3 seeds cv<0.15).

## Framing (per USER prompt; MM_TENTATIVE at SMOKE at most)

**HOLD_PENDING_FULL is the honest default** even if H1 discriminator fires at SMOKE, per today's Skunkworks pattern (Fix#28 hits #15-#18). Reasons:
1. TR=40 single-seed 2SE noise floor at p=0.5 is ~0.158; interaction_metric at 0.10 sits AT noise floor.
2. Single-seed smoke has empirically overstated 3-seed FULL discriminator by 0.05-0.25 in every case tried this session.
3. Even at TR=100 3-seed FULL, cv<0.15 is required for MM_STANDARD promotion.

If H1 fires at 3-seed FULL cv<0.15: candidate `EMPIRICAL_L_x_M_CROSS_TERM_SHARDED_CLIFF_ADJACENT_v1` promoted as REGIME-EXTENSION of M-sweep CG_META atom. NOT a new axis discovery.

If H2 fires: valuable NULL finding: M-sweep CG_META atom holds at other L values.

Independent of Testbed template audit (fired in parallel; different files).
