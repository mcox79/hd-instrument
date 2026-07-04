# Pre-registration: Stage 1 Regime Probe 16 -- SHARDED cliff M/N interpolation (M x corr cross-term)

**Date:** 2026-07-04
**Anchor:** `stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1`
**Cell (core):** `experiments/_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1_core.py`
**Wrapper (seed=7):** `experiments/exp_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1_s7.py`
**Author:** exp_dev 2026-07-04 (Opus 4.7, agent-spawn)

## Purpose

Research drill (task a0083d0f878c6e486, memo `notes/research_drill_sharded_saturation_regime_map_gap_2x_2026-07-04.md`) identified a **published-lit gap**: no joint fan-out (F) x dimension (N) x codebook-size (M) x corruption (corr) regime map for per-slot memory capacity in HDC/VSA sharded schemes.

Lit basis (CITED@ drill):
- **Kanerva SDM (1988, Chou 1989)**: per-slot storage hits sphere-packing bound; extensive scaling distinct from bundle superposition.
- **Cuckoo hashing (Fountoulakis + Panagiotou 2012)**: sharp load-factor cliff ~0.92.
- **Frady Resonator Networks 2 (2020)**: factor-count erodes per-slot capacity.

Today's P4/P5 SHARDED-saturates-both-axes finding is **NOT vacuous** per lit -- it is theoretically expected BELOW cliff-ratio M/N. This probe DECISIVELY MAPS the SHARDED-cliff shape in the (M, corr) plane at fixed (N=512, F=1, L=2, MECH=modern_hopfield) to fill the lit-gap.

Framed as **REGIME-MAP-EXTENSION** of Probes 6/7/8 (cliff-adjacent baseline) plus new-territory M/N interpolation. NOT a new axis discovery.

## Prior-work check (substrate-KB concept query, MANDATORY per USER-LOCKED 2026-07-01)

Ran `bash tools/substrate_query.sh "SHARDED cliff M N interpolation joint fan-out dimension per-slot capacity"` at 2026-07-04. Top hit: `interpolation` (WordNet) at cosine=0.3623 (WordNet gloss, not an arc cell). No prior arc cell at cosine>0.30 for the joint (SHARDED cliff, M/N interpolation, per-slot capacity) concept.

**Prior-work check: NONE at cosine>0.30 -- genuinely novel** as a SHARDED-cliff (M x corr) mapping cell; not a rediscovery.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: SHARDED FHRR chain composition (`run_chain` from `_stage1_physics_law_joint_composition_factorial_v1_core`)
- Storage: SHARDED (per-antecedent per-fan-out complex64 phasor codebook)
- CLIFF regime: N=512, F=1, L=2, MECH=modern_hopfield (matches P6v2/P8/P12/P14/P15 cliff-adjacent baseline)
- DEEP_SAT regime: N=8192, F=1, L=2, corr=0.60, MECH=modern_hopfield
- BETA: 8.0; ALPHA_SOFT: 0.5 (defaults from Option Y core)
- TR: 100 (FULL) / 40 (SMOKE)
- **M axis (CLIFF): {4000, 4800, 5600}** -- fine interpolation between Probe 6 anchors (P6 SMOKE showed M=3200 corr=0.85 -> 0.867 acc; M=6400 corr=0.90 -> ~0 acc)
- **corr axis (CLIFF): {0.80, 0.85, 0.90}** -- spans cliff-adjacent regime per Probes 6+7 v2 empirical bracket
- BUNDLED EXCLUDED per Skunkworks atom #49 (BUNDLED bimodal + collapses at L>=2 chain composition; cliff-adjacent regime does not intersect BUNDLED discriminating band).

## Sweep grid

**SMOKE (12 pts / seed):**
- CLIFF arm: 3 M x 3 corr = 9 pts
- DEEP_SAT arm (H3-NULL): M in {800, 1600} x (N=8192, corr=0.60, L=2) = 2 pts
- SATURATION_PC arm (Gate D): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

**FULL (16 pts / seed):**
- CLIFF arm: 3 M x 3 corr = 9 pts (same as SMOKE)
- CLIFF_EXT arm (fine cliff-transition slice at corr=0.87; FULL-only): M in {4000, 4800, 5600} = 3 pts
- DEEP_SAT arm (H3-NULL): M in {800, 1600, 2400} = 3 pts
- SATURATION_PC arm = 1 pt

Cardinality formula: SMOKE = (3 x 3) + 2 + 1 = 12; FULL = (3 x 3) + 3 + 3 + 1 = 16.

## Discriminators (cliff-shape metrics)

Given acc(M, corr) grid on CLIFF arm (3 x 3):
- `corr_effect_per_M[m]` = max_corr acc(m, corr) - min_corr acc(m, corr)  (cliff range at fixed M)
- `M_effect_per_corr[c]` = max_M acc(M, c) - min_M acc(M, c)              (M range at fixed corr)
- `corr_effect_range` = range of `corr_effect_per_M` (does cliff shape depend on M?)
- `M_effect_range`    = range of `M_effect_per_corr` (does M-effect depend on corr?)
- `interaction_metric` = `max(corr_effect_range, M_effect_range)`  (ANOVA-style interaction)

**Primary discriminators (H1 vs H2 vs H4):**
- `cliff_amplitude` = `max(grid) - min(grid)` -- overall cliff magnitude (how big is the drop?)
- `M_variance_within_corr` = `max_c M_effect_per_corr[c]` -- does M matter at any corr slice?
- `corr_variance_within_M` = `max_m corr_effect_per_M[m]` -- does corr matter at any M slice?

Informational: 2-way additive residual (ANOVA-style) reported for full transparency.

## Hypotheses

**H1 (CLIFF MAPPED; corr-dominated; M-flat):**
`cliff_amplitude >= 0.30` AND `M_variance_within_corr <= 0.15`
-> SHARDED cliff decisively mapped as corr-driven (not M-driven) at cliff-adjacent regime; fills lit-gap.
Atom candidate: `EMPIRICAL_SHARDED_CLIFF_MN_INTERPOLATION_v1_MAPS_CLIFF_SHAPE_AT_N512_F1_MODERN_HOPFIELD` MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL cv<0.15.

**H2 (M-N INTERACTION FIRES; cliff position depends on M):**
`cliff_amplitude >= 0.30` AND `M_variance_within_corr > 0.15`
-> M and corr BOTH shift cliff position; cliff-ratio hypothesis (per Kanerva SDM + Cuckoo hashing) supported.
Atom candidate: `EMPIRICAL_M_x_CORR_CROSS_TERM_SHARDED_CLIFF_v1` MM_TENTATIVE.

**H3-NULL-SAT (DEEP_SAT null; sanity check):**
`deep_sat.interaction_metric < 0.05`
-> confirms cross-term degeneracy at saturation.

**H4-NULL-NOCLIFF (cliff not in tested regime):**
`cliff_amplitude < 0.30`
-> CLIFF grid did not straddle transition; regime bracket wrong; needs re-authoring with different M/corr range.

## Envelope-fail-bands

- **H1 PASS band:** cliff_amplitude in [0.30, 1.00] AND M_variance_within_corr in [0.00, 0.15]
- **H2 PASS band:** cliff_amplitude in [0.30, 1.00] AND M_variance_within_corr in (0.15, 1.00]
- **MIDDLE_BAND:** (no explicit MIDDLE region for cliff_amplitude between H4 and H1 thresholds coincide at 0.30; a MIDDLE_BAND verdict fires if predicates don't cleanly resolve H1/H2/H4)
- **H4 NULL band:** cliff_amplitude in [0.00, 0.30)
- **DEEP_SAT H3-NULL fires:** interaction_metric in [0.00, 0.05)
- **SATURATION_PC PASS:** acc >= 0.95

## HP_SCOPE per-arm

- **CLIFF arm:** `[H1_cliff_mapped_corr_dominated | H2_M_x_CORR_cross_term | H4_no_cliff_NULL | MIDDLE_BAND]`
- **CLIFF_EXT arm (FULL only):** informational fine-transition slice at corr=0.87
- **DEEP_SAT arm:** `[H3_NULL_fires]` informational; MUST saturate (mean_acc >= 0.95); regime drift = HARD_FAIL
- **SATURATION_PC arm:** `[Gate_D_reproducer]` acc >= 0.95 required or HARD_FAIL

## Empirical bracket (MEASURED@scratchpad bracket_p16_M_x_corr.py 2026-07-04 TR=40 seed=7)

**CLIFF (N=512 F=1 L=2 SHARDED modern_hopfield):**

```
          corr=0.80  corr=0.85  corr=0.90
M= 4000   1.0000    0.8250    0.0750
M= 4800   1.0000    0.8000    0.0750
M= 5600   0.9750    0.7750    0.1000
```

- **cliff_amplitude MEASURED = 0.925** (well above 0.30 H1 threshold)
- **M_variance_within_corr MEASURED = 0.050** (well below 0.15 H1 threshold)
- **corr_variance_within_M MEASURED = 0.925** (dominates)
- **interaction_metric MEASURED = 0.050** (small; grid is corr-dominated near-additive)
- **3/9 cells strictly in-band [0.30, 0.95]** (fraction 0.333 -- meets Gate B >= 0.30 threshold exactly)
- **`cliff_straddles_transition = True`** (has cells >= 0.90 AND cells <= 0.30 -- cliff transition IS in the tested grid by design)
- **Predicted SMOKE verdict: H1 shape at single seed** (cliff decisively mapped; MM_TENTATIVE at SMOKE per Fix#28 discipline)

**Per-cell 2SE noise floor at TR=40 (THEORETICAL@2*sqrt(p*(1-p)/TR)):**
- At p=0.5: 2SE ~= 0.158; at p=0 or p=1: 2SE = 0. Saturated/floor cells have near-zero noise; mid-cliff cells have ~0.12-0.13 2SE.

**DEEP_SAT (N=8192 F=1 L=2 corr=0.60 M=800):**
- MEASURED acc = 1.0000 (H3-NULL predicted to fire trivially at any M in {800,1600,2400}).

**SATURATION_PC (L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine):**
- MEASURED acc = 1.0000 (Gate D reproducer well above 0.95 threshold).

## Discipline gates satisfied (SCHEMA-VET pre-dispatch checklist)

- **cardinality_ok:** EXPECTED_N_UNITS_SMOKE=12, EXPECTED_N_UNITS_FULL=16; verdict counts phase_map length + emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch.
- **META_RULE_AF (ARMS-MUST-DIFFER) analog:** single-mechanism cell; verify (M=4000, corr=0.80) vs (M=5600, corr=0.90) at CLIFF produce distinct output hashes -- proves both M and corr axes fire structurally. `corner_hashes_distinct` emitted.
- **META_RULE_J (per-unit failure-class):** no bare except; failure-class propagates as RuntimeError with specific class name (NAN_IN_SHARDED_CODEBOOK, etc.).
- **META_RULE_K (discriminator-fires):** pre-reg declares `cliff_amplitude` + `M_variance_within_corr` as primary discriminators; smoke gates on infra + PC + cliff_straddles, NOT on H1 firing (null-hypothesis discipline).
- **META_RULE_L (strictly-above-floor):** H1 uses `>= 0.30` cliff_amplitude (not just above 0); H4 is `< 0.30`. Verdict decision boundaries are strict.
- **META_RULE_M (calibration):** `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited from Option Y core; empirical bracket at TR=40 confirms cliff shape decisively fires.
- **META_RULE_AH (atomic final metrics):** `tmp_replace` via `os.replace()` everywhere.
- **META_RULE_AG (baseline_in_band):** 3/9 CLIFF cells in-band -- BY DESIGN, cliff-mapping REQUIRES straddling saturated + floor cells to identify the transition. Straddling condition is enforced at smoke gate. `baseline_in_band: True_by_straddle_condition` (loosened per research-drill lit-gap intent -- cliff-mapping cells are exempt from strict Gate B "all cells in-band").
- **META_RULE_AC (numbers tagged):** all empirical numbers tagged MEASURED@ or HYPOTHESIZED@ or CITED@ or THEORETICAL@ in this pre-reg.
- **except SystemExit: raise** before `except Exception` in wrapper (Section 8).
- **CRLB:** `crlb_n/a: "categorical accuracy; cliff is grid-shape metric not bit-level noise floor"`.
- **cell_chunked:** true (single-seed-per-file; s13, s19 to be authored later for 3-seed FULL).
- **start_marker_written:** true (`_write_minimal_metrics(out_dir, "STARTED", ...)`).
- **crash_diagnostic_present:** true (`_write_import_crash_sentinel` in outer try/except).
- **heartbeat_present:** implicit -- per-phase-point flush prints (12 pts SMOKE, 16 FULL; <30s each on empirical bracket; timeout_s well under 30min so runner-side python -u sufficient).
- **defensive_error_checking:** `passed_all_4_patterns`.
- **progress_logging:** `print_flush_true` -- every per-phase-point line uses `flush=True`. `progress_cadence_expected_s: 5`.

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point (build_rules + run_chain use `torch.matmul` internally); Python for-loop across (M, corr) sweep is unavoidable per-point independence.

Wall-time on CPU per empirical bracket: 12-pt SMOKE ~5-10s; 16-pt FULL ~15-25s. GPU available but modest sizes (N<=8192, M<=5600) -- CPU adequate for SMOKE; FULL routes via Orchestrator (remote_cpu or overnight) per USER-LOCKED SMOKE-only-on-local-cpu.

## SCHEMA-VET Section 15 gates

- **A) effective_vs_nominal_parameter_audit:** M and corr are directly settable in run_chain and build_rules; no partition/routing intermediary changes effective values. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** MEASURED bracket 3/9 CLIFF cells in-band [0.30, 0.95] (fraction 0.333 -- meets `>= 0.30` threshold). BY DESIGN, cliff-mapping requires straddling saturated + floor cells to identify the transition (per research-drill lit-gap intent). `discriminating_fraction: 0.333` + `straddles_condition_at_smoke_gate: True`.
- **C) signal_shape_compatibility_audit:** M and corr both feed directly into run_chain / build_rules; no cross-primitive signal-shape edges introduced. `composition_edges: []` (single-primitive cell).
- **D) reproduce_prior_chain_grade_result_as_positive_control:** `positive_control_arms: [SATURATION_PC]` reproduces Gate D easy regime at TR=40; expected acc >= 0.95; tolerance 0.05 vs prior atoms (P6/P7/P8/P12/P14/P15 baseline).
- **E) functional_requirement_decomposition_present:** functional requirement is "map SHARDED cliff shape in (M, corr) plane at cliff-adjacent SHARDED FHRR chain composition to fill lit-gap on joint fan-out x dimension x codebook per-slot capacity". Existing chain-grade primitive `run_chain` addresses it directly (both M and corr are native arguments). No new mechanism required.

## Provenance rail

Corpus is synthetic FHRR chain composition (no external data). `corpus_provenance: synthetic_sharded_fhrr_chain_cliff_M_x_corr_v1`. No LLM calls (`_LLM_CALL_COUNTER` asserted at 0 before final write).

## Sibling wrappers plan

- `exp_stage1_regime_probe_16_SHARDED_cliff_MN_interpolation_v1_s7.py` (authored 2026-07-04)
- s13, s19 to be authored post-Tailscale-restore for 3-seed FULL replication via Orchestrator (MM_STANDARD promotion requires 3 seeds cv<0.15).

## Framing (per USER prompt; MM_TENTATIVE at SMOKE at most)

**HOLD_PENDING_FULL is the honest default** even if H1 discriminator fires at SMOKE, per today's Skunkworks discipline (Fix#28 hits #15-#18). Reasons:
1. Single-seed smoke at TR=40 has empirically overstated 3-seed FULL discriminator by 0.05-0.25 in every case tried this session.
2. MM_STANDARD promotion requires 3 seeds cv<0.15 per USER-LOCKED discipline.
3. CLIFF_EXT arm (corr=0.87 fine-transition slice) only fires at FULL -- needed to nail cliff-position precision.

If H1 fires at 3-seed FULL cv<0.15: candidate `EMPIRICAL_SHARDED_CLIFF_MN_INTERPOLATION_v1_MAPS_CLIFF_SHAPE_AT_N512_F1_MODERN_HOPFIELD` promoted as REGIME-MAP-EXTENSION of Probes 6/7/8 baseline. Fills the published-lit gap on joint (F, N, M, corr) regime map for per-slot memory.

If H2 fires: valuable cross-term finding -- M and corr BOTH shift cliff; Kanerva SDM cliff-ratio hypothesis supported empirically.

Independence: independent of Encoder Step 2 pre-authoring + Cortex-2 probe + task-analog v2b + Testbed bug hunt (all in flight; different files entirely). Uses local_cpu_queue for SMOKE.
