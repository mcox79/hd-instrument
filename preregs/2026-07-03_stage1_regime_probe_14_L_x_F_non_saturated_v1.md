# Pre-registration: Stage 1 Regime Probe 14 -- L (chain-depth) x F (fan-out) CROSS-TERM

**Date:** 2026-07-03
**Anchor:** `stage1_regime_probe_14_L_x_F_non_saturated_v1`
**Cell (core):** `experiments/_stage1_regime_probe_14_L_x_F_non_saturated_v1_core.py`
**Wrapper (seed=7):** `experiments/exp_stage1_regime_probe_14_L_x_F_non_saturated_v1_s7.py`
**Author:** exp_dev 2026-07-03 (Opus 4.7, agent-spawn)

## Purpose

Skunkworks atom #48 addendum flagged "L cross-terms unmapped."
- L was CG_META-covered at atom #3 (chain-depth).
- F axis was filled at Probe 8 (algebra x cleanup).
- Probe 12 established L has genuine marginal effect at cliff-adjacent SHARDED.
- Prior probes (6v2, 8) fixed L=2 while varying F -- implicitly assumed L and F orthogonal.

Probe 14 asks: **does F effect depend on L**, or are L and F orthogonal axes as the L=2-fixed convention implicitly assumed?

If H1 fires: F effect is L-conditional; prior findings need L-slice annotation; opens new theoretical arc (cross-term physics).

If H2 fires: F was correctly labeled orthogonal to L; prior Probes 6v2/8 findings hold at L=2 slice without loss of generality; strong support for the additive-axes model of the CG_META regime matrix.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: SHARDED FHRR chain composition (`run_chain` from `_stage1_physics_law_joint_composition_factorial_v1_core`)
- Storage: SHARDED (per-antecedent per-fan-out complex64 phasor codebook)
- CLIFF regime: N=512, M=6400, corr=0.85
- DEEP_SAT regime: N=8192, M=800, corr=0.60
- MECH: modern_hopfield (single mechanism; best F=1 performer per Probe 6 v2 at cliff-adjacent regime; single-mech chosen to isolate L x F cross-term and keep cardinality tight -- mech cross-terms already covered by Probe 8)
- BETA: 8.0; ALPHA_SOFT: 0.5 (defaults from Option Y core)
- TR: 100 (FULL) / 40 (SMOKE)
- L axis: {1, 2, 4} band-only per Probe 12 VET (L=8,16 fall below 0.30 floor at CLIFF)
- F axis: {1, 2, 4, 8, 16} matches Probe 8 grid

BUNDLED FHRR chain composition is EXCLUDED (per Skunkworks atom #49: BUNDLED bimodal + collapses at L>=2 chain composition; cliff-adjacent regime does not intersect BUNDLED discriminating band).

## Sweep grid

**FULL (20 pts / seed):**
- CLIFF arm: L in {1,2,4} x F in {1,2,4,8,16} x modern_hopfield = 15 pts
- DEEP_SAT arm (H3-NULL): L in {1,4} x F in {1,16} x modern_hopfield = 4 pts
- SATURATION_PC arm (Gate D reproducer): L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine = 1 pt

**SMOKE (12 pts / seed):**
- CLIFF arm: L in {1,2,4} x F in {1,4,16} (endpoints + mid) x modern_hopfield = 9 pts
- DEEP_SAT arm spot-check: L in {1,4} x F in {1} x modern_hopfield = 2 pts
- SATURATION_PC arm: 1 pt

## Discriminator (2-way L x F cross-term)

Given acc(L,F) grid on CLIFF arm:
- **F_effect_per_L[l]** = max_F acc(l,F) - min_F acc(l,F)  (F range at fixed L)
- **L_effect_per_F[f]** = max_L acc(L,f) - min_L acc(L,f)  (L range at fixed F)
- **F_effect_range** = max_l F_effect_per_L[l] - min_l F_effect_per_L[l]  (does F-effect depend on L?)
- **L_effect_range** = max_f L_effect_per_F[f] - min_f L_effect_per_F[f]  (does L-effect depend on F?)
- **interaction_metric** = max(F_effect_range, L_effect_range)  <- PRIMARY

Additional (informational, 2-way ANOVA-style):
- add_model[l,f] = row_mean[l] + col_mean[f] - grand_mean
- residual[l,f]  = acc[l,f] - add_model[l,f]
- **additive_residual_max_abs** = max |residual| across grid

## Hypotheses

**H1 (L x F interaction):**
`cliff.interaction_metric >= 0.10`
-> L x F cross-term fires; F effect is L-conditional at cliff-adjacent SHARDED; today's 6-pair regime matrix (Probes 1/2/4/5/6v2/7v2/8/9v2/10) needs L-slice annotation.
Atom candidate: `L_x_F_CROSS_TERM_AT_CLIFF_ADJACENT_SHARDED_v1` MM_TENTATIVE at SMOKE, MM_STANDARD at 3-seed FULL.

**H2 (L x F orthogonal, additive):**
`cliff.interaction_metric < 0.05`
-> L and F ARE orthogonal axes at this signature; F effect same across L values; prior Probes 6v2/8 findings hold at L=2 slice without loss of generality; L=2-fixed convention was correctly labeled orthogonal.
Atom candidate: `L_x_F_ORTHOGONAL_AT_CLIFF_ADJACENT_SHARDED_NEGATIVE_v1` MM_TENTATIVE.

**H3-NULL (DEEP_SAT null; sanity check):**
`deep_sat.interaction_metric < 0.05`
-> confirms cross-term degeneracy at saturation (H3-null discipline per META_saturation_floor).

## Envelope-fail-bands

- **CLIFF arm PASS band (H1):** interaction_metric in [0.10, 2.00]
- **CLIFF arm PASS band (H2):** interaction_metric in [0.00, 0.05)
- **MIDDLE_BAND (weak cross-term):** interaction_metric in [0.05, 0.10)
- **DEEP_SAT H3-NULL fires:** interaction_metric in [0.00, 0.05)
- **SATURATION_PC PASS:** acc >= 0.95

## HP_SCOPE per-arm

- **CLIFF arm:** `[H1_cross_term | H2_orthogonal | MIDDLE_BAND_weak]`
- **DEEP_SAT arm:** `[H3_NULL_fires]` informational; MUST saturate (mean_acc >= 0.95); regime drift = HARD_FAIL
- **SATURATION_PC arm:** `[Gate_D_reproducer]` acc >= 0.95 required or HARD_FAIL

## Empirical bracket (MEASURED per prior probes)

**CLIFF (N=512 M=6400 corr=0.85 SHARDED modern_hopfield):**
- MEASURED@scratchpad probe12_L_bracket 2026-07-03 (TR=40 seed=7, F=1):
  L=1: 0.950; L=2: 0.725; L=4: 0.375 -- all in [0.30, 0.95] band
- HYPOTHESIZED@this-prereg F effect at each L: F sweep at fixed L expected to
  show accuracy degradation with increasing F (per Probe 8 F=1 top, F=16
  floor-adjacent for iterative_cosine at TR=100 3-seed).
- HYPOTHESIZED@this-prereg (interaction under H1): if capacity budget is a
  joint L x F function, F=16 at L=4 may bottom out below F=16 at L=1 by more
  than the marginal L effect predicts.

**DEEP_SAT (N=8192 M=800 corr=0.60 SHARDED):**
- MEASURED@scratchpad probe12_L_bracket 2026-07-03: L in {1,2,4,8,16} at F=1
  all saturated at 1.000 exact; spread 0.000.
- HYPOTHESIZED@this-prereg: F sweep at DEEP_SAT also fully saturates
  (capacity vastly exceeds task); H3-NULL strongly predicted to fire.

**SATURATION_PC (L=2 F=1 M=800 N=2048 corr=0.20 iterative_cosine):**
- MEASURED@prior Probes 6/7/8/12 selftests: acc >= 0.95 at TR=40 typical.

## Discipline gates satisfied (SCHEMA-VET pre-dispatch checklist)

- **cardinality_ok:** EXPECTED_N_UNITS_FULL=20, EXPECTED_N_UNITS_SMOKE=12; verdict counts phase_map length + emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch. Formula: (3 x 5) + (2 x 2) + 1 = 20; (3 x 3) + (2 x 1) + 1 = 12.
- **META_RULE_AF (ARMS-MUST-DIFFER) analog:** single-mechanism cell; verify (L=1, F=1) vs (L=max, F=max) at CLIFF produce distinct output hashes (proves both L and F axes fire structurally). `corner_hashes_distinct` emitted.
- **META_RULE_J (per-unit failure-class):** no bare except; failure-class propagates as RuntimeError with specific class name.
- **META_RULE_K (discriminator-fires):** pre-reg declares `interaction_metric` as discriminator; smoke gates informationally (null-hypothesis discipline per feedback_smoke_gates_null_hypothesis_2026-07-03).
- **META_RULE_L (strictly-above-floor):** H1 uses `>= 0.10` (not just above 0); MIDDLE_BAND for [0.05, 0.10).
- **META_RULE_M (calibration):** `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited from Option Y core; empirical bracket at TR=40 confirms discriminator present.
- **META_RULE_AH (atomic final metrics):** `tmp_replace` via `os.replace()` everywhere.
- **META_RULE_AG (baseline_in_band):** empirically confirmed L={1,2,4} at F=1 in [0.30, 0.95]; F sweep expected to hold in-band based on Probe 8 pattern.
- **META_RULE_AC (numbers tagged):** all empirical numbers tagged MEASURED@ or HYPOTHESIZED@ or CITED@ in this pre-reg.
- **META_RULE_AF full-scale probe:** the ARMS-MUST-DIFFER-analog corner-hash check runs on the actual CLIFF phase points (full-scale) at smoke gate, satisfying discriminator-survives-scale by preview-arm construction.
- **except SystemExit: raise** before `except Exception` in wrapper (§8).
- **CRLB:** `crlb_n/a: "categorical accuracy; discriminator is grid-shape interaction metric, not a bit-level noise floor"`
- **cell_chunked:** true (single-seed-per-file; s13, s19 to be authored later)
- **start_marker_written:** true (`_write_minimal_metrics(out_dir, "STARTED", ...)`)
- **crash_diagnostic_present:** true (`_write_import_crash_sentinel` in outer try/except)
- **heartbeat_present:** implicit -- per-phase-point flush prints (12/20 pts; <60s each; timeout_s well under 30min so runner-side python -u sufficient).
- **defensive_error_checking:** `passed_all_4_patterns`
- **progress_logging:** `print_flush_true` -- every per-phase-point line uses `flush=True`. `progress_cadence_expected_s: 15` (per-phase-point ~1-10s).

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point (build_rules + run_chain use `torch.matmul` internally); Python for-loop across (L, F) sweep is unavoidable (each phase point requires independent state build with fresh gen).

Wall-time smoke on CPU estimated ~30-90s total (12 phase points at 1-8s each; F=16 x L=4 is the slowest cell). FULL on CPU estimated ~2-6 min (20 phase points at 3-15s each; TR=100 vs 40). GPU available but modest sizes (N<=8192, M<=6400) -- CPU adequate for smoke; FULL routes remote via Orchestrator per USER-LOCKED SMOKE-only-on-local-cpu.

## SCHEMA-VET §15 gates

- **A) effective_vs_nominal_parameter_audit:** L and F are directly settable in run_chain; no partition/routing intermediary changes effective L or F. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** predicted per-cell accuracies from Probe 12 bracket (F=1 slice) + Probe 8 pattern (F sweep at L=2): CLIFF grid has ~9-15 cells (out of 15 FULL) in [0.05, 0.95] discriminating band. `discriminating_fraction: >= 0.60`; `>= 0.30` satisfied.
- **C) signal_shape_compatibility_audit:** L and F both feed directly into run_chain step count / fan-out choices; no cross-primitive signal-shape edges introduced. `composition_edges: []` (single-primitive cell).
- **D) reproduce_prior_chain_grade_result_as_positive_control:** `positive_control_arms: [SATURATION_PC]` reproduces Gate D easy regime at TR=40; expected acc >= 0.95; tolerance 0.05 vs prior atoms.
- **E) functional_requirement_decomposition_present:** functional requirement is "measure L x F cross-term interaction at cliff-adjacent SHARDED FHRR chain composition." Existing chain-grade primitive `run_chain` addresses it directly (both L and F are native arguments). No new mechanism required.

## Provenance rail

Corpus is synthetic FHRR chain composition (no external data). `corpus_provenance: synthetic_sharded_fhrr_chain_composition_L_x_F_cross_term_v1`. No LLM calls (`_LLM_CALL_COUNTER` asserted at 0 before final write).

## Sibling wrappers plan

- `exp_stage1_regime_probe_14_L_x_F_non_saturated_v1_s7.py` (authored 2026-07-03)
- s13, s19 to be authored post-Tailscale-restore for 3-seed FULL replication via Orchestrator (MM_STANDARD promotion requires 3 seeds).

## Framing (per USER prompt)

**MM_TENTATIVE at SMOKE.** If H2 fires cleanly at 3-seed FULL: strong evidence for L/F orthogonality; today's 6-pair regime matrix findings hold without L-conditioning. If H1 fires at 3-seed FULL: L cross-terms are real; matrix needs L-slice annotation per Skunkworks atom #48 addendum.

Independent of Probe 13 (L x CLEANUP, parallel) and dispatch bundle authoring (different scope).
