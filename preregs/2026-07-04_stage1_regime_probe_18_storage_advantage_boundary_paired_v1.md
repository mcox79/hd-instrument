# Pre-registration: Stage 1 Regime Probe 18 -- PAIRED STORAGE-advantage regime-boundary map

**Date:** 2026-07-04
**Anchor:** `stage1_regime_probe_18_storage_advantage_boundary_paired_v1`
**Cell (core):** `experiments/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_core.py`
**Wrappers (seeds 7/13/19):** `experiments/exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s{7,13,19}.py`
**Author:** exp_dev 2026-07-04 (Opus 4.8, agent-spawn)
**Source memo:** `notes/research_phase_diagram_genuine_open_questions_post_cross_term_collapse_2026-07-04.md` (Experiment 1, TOP dispatchable)

## Purpose

The STORAGE main effect (SHARDED >> BUNDLED readout quality; median gap ~0.93, 36/36 pairs positive, 3-seed -- `MATH Probe 1 SPLIT survivor`) is the #1 surviving Stage-1 law. But it was ONLY ever measured with SHARDED pinned at its accuracy CEILING (=1.0 everywhere in P1/P4's grid; BUNDLED ~0.09). So "gap ~0.93" is a LOWER bound and "gap is N-invariant (P4)" was measured in a regime where SHARDED cannot move. The gap's TRUE size and its SCALING are only measurable where SHARDED is IN-BAND -- i.e. near the SHARDED corruption cliff that P16 found (at one (N=512, F=1) point only).

This cell fills that: **PAIRED SHARDED-vs-BUNDLED** (shared salt per cell -> bit-identical items + corruption across the two storage arms), sweeping corr x F x N straddling the SHARDED cliff so SHARDED is IN-BAND (not saturated). The discriminator is the WITHIN-ITEM PAIRED gap `delta = acc_SHARDED - acc_BUNDLED`, its collapse boundary, and whether that boundary MOVES with N / F above a binomial noise-floor null.

## Why this CANNOT re-manufacture the mechanism-cross-term artifact (design invariants)

On 2026-07-04 a whole family of "axis moderates CLEANUP_MECHANISM" cross-terms collapsed to noise: paired TR=400 gave mechanism range EXACTLY 0.000000 (the 3 mechanisms are READOUT-DEGENERATE for the index-argmax readout), and the unpaired max/range-over-arms discriminators had been reading TR=100 sampling noise (~0.10-0.13) as signal (memory `feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`, commit `bf4408f2e`/`642f6394f`). This cell is built so it cannot repeat that:

1. **No mechanism axis.** Single MECH=modern_hopfield. The collapsed family moderated CLEANUP_MECHANISM; there is no mechanism here to moderate.
2. **Paired-by-construction.** Both storage arms consume BIT-IDENTICAL stochastic inputs (antecedent indices + fan-out slots + per-step corruption masks), pre-drawn ONCE per cell (`draw_shared_state`) and passed to both arms (`run_chain_paired`, which draws NOTHING from the generator internally). `delta` is a true within-item paired difference, not a difference of independent draws.
3. **Discriminator is a within-arm boundary LOCATION** (corr at which the paired gap crosses 0.5) and its movement across N / F, gated against a data-driven binomial noise-floor null. It is NOT a max/range-over-noisy-arms statistic.
4. **Both PASS bands are real results.** HARD_PASS (boundary moves) AND HARD_PASS_NULL (scale-free boundary; filed BOUNDED_NULL like P9v2) are both genuine findings, so there is no incentive to read noise as a moving boundary.

## Prior-work check (substrate-KB concept query, MANDATORY per USER-LOCKED 2026-07-01)

Ran `bash tools/substrate_query.sh "STORAGE advantage SHARDED BUNDLED collapse boundary paired gap corruption cliff"` at 2026-07-04. Top hit `substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19` at **cosine=0.2773** (a different argmax-pattern-completion readout, verdict HARD_FAIL); other neighbors are the SHARDED-cliff (P16) and sharded-capacity-beyond-bundle-bound arcs.

**Prior-work check: NONE at cosine>0.30 -- genuinely novel.** No prior arc cell measures a PAIRED within-item SHARDED-vs-BUNDLED gap or its boundary/scaling. Distinct from P16 (SHARDED-only cliff at one (N,F) point) and from P1/P4 (SHARDED ceiling-pinned, unpaired). Not a rediscovery.

## Source signature (cited per feedback_mechanism_abstraction_lossy_cite_source_signature)

- Mechanism: PAIRED SHARDED-vs-BUNDLED FHRR chain composition (`run_chain_paired`, a physics-preserving refactor of `run_chain` from `_stage1_physics_law_joint_composition_factorial_v1_core`; selftest asserts bit-for-bit equivalence to the reference on the SHARDED arm).
- Storage arms: SHARDED (per-antecedent per-fan-out complex64 phasor codebook) and BUNDLED (all M*F rules superposed), evaluated on identical items+corruption.
- MECH: modern_hopfield (fixed); L=2; M=4800 (fixed across (N,F)); BETA=8.0; ALPHA_SOFT=0.5.
- N in {512, 2048, 8192}; F in {1, 4}.
- TR: 200 (FULL) / 40 (SMOKE).
- SATURATION_PC (Gate D): iterative_cosine, M=800, N=2048, F=1, L=2, corr=0.20, SHARDED.

## Grid (empirically bracketed so SHARDED straddles the cliff at every (N,F))

Fixed M=4800 across all (N,F). corr grid PER N (the cliff moves with N -- that IS the finding). Same corr grid across F within each N; both F straddle.

MEASURED@scratchpad bracket_p18_storage_boundary.py 2026-07-04 TR=40 seed=7 CPU (paired SHARDED vs BUNDLED, reseeded so arms share draws):

```
                 corr sweep -> acc_SHARDED (acc_BUNDLED = 0.000 EVERYWHERE)
N=512  F=1 : 0.80->0.95  0.83->0.85  0.85->0.80  0.88->0.35  0.90->0.20  0.93->0.00
N=512  F=4 : 0.80->1.00  0.85->0.625 0.90->0.075
N=2048 F=1 : 0.89->1.00  0.91->0.925 0.93->0.55  0.95->0.125 0.96->0.025 0.97->0.00
N=2048 F=4 : 0.89->1.00  0.92->0.825 0.94->0.325 0.96->0.00
N=8192 F=1 : 0.93->1.00  0.95->0.975 0.96->0.875 0.97->0.225 0.975->0.10 0.98->0.00
N=8192 F=4 : 0.94->1.00  0.96->0.90  0.97->0.325 0.98->0.00  0.985->0.025
```

Locked 5-point corr grids (each straddles: a cell >= 0.90 AND a cell <= 0.30):
- **N=512:** `{0.80, 0.84, 0.87, 0.90, 0.93}`
- **N=2048:** `{0.88, 0.91, 0.93, 0.95, 0.97}`
- **N=8192:** `{0.93, 0.95, 0.96, 0.97, 0.98}`

**Key measured fact:** BUNDLED acc = 0.000 at every point (M=4800 >> Plate bound 0.14*N; at N=8192 0.14*N=1147 << 4800). So `delta ~= acc_SHARDED` and the storage-advantage boundary == the SHARDED cliff location. This is exactly the memo's intent (line 96 region: "delta ~= acc_S mostly"). The paired structure (a) rigorously confirms BUNDLED recovers ZERO on the SAME items SHARDED recovers (the advantage is the entire SHARDED accuracy), and (b) supplies the shared-noise binomial null. BUNDLED is a floor REFERENCE arm, not the discriminator arm; its floor value is the measured advantage, not a vacuous ceiling/floor-pinned interaction.

**Observed boundary movement (informational, from bracket):** SHARDED/delta boundary (corr at acc=0.5) moves 0.86 (N=512,F=1) -> 0.93 (N=2048,F=1) -> 0.965 (N=8192,F=1). F moves it far less (F=1 vs F=4 boundaries within ~0.01 at each N). The FULL run + binomial null will resolve whether the N-movement is above noise (HARD_PASS direction) and whether F is scale-free.

## Discriminators (all within-cell / paired; NONE is a max-over-noisy-arms)

- `delta[N,F,corr]` = `acc_SHARDED - acc_BUNDLED` (paired, per shared-salt cell).
- `boundary_corr[N,F]` = corr at which `delta` crosses below 0.5 (linear interp, first descending crossing) = the STORAGE-advantage collapse point. Also report `boundary_corr_sharded` (acc_S crossing 0.5) for transparency.
- `delta_scales_with_N` = range over N of `boundary_corr[N,F=1]`.
- `delta_scales_with_F` = range over F of `boundary_corr[N=512,F]`.
- `collapse_test` (informational, not gated): pooled r^2 of `delta` vs candidate load variables u in {raw corr, (1-corr)*sqrt(N), corr - boundary[N,F]}.

## Data-driven binomial noise-floor null (two-stage MC)

Because `delta` near the cliff is a difference of two in-band binomials, the boundary and its cross-axis range are gated against a MC binomial null (NDRAW=200000, fixed seed 20260704 for reproducibility):
- **Stage 1 (per cell):** resample `acc_S ~ Binom(TR, pS)/TR` and `acc_B ~ Binom(TR, pB)/TR` (pS, pB = MEASURED per-cell accuracies), recompute the delta-boundary via the SAME linear-interp estimator, take the binomial SE of the boundary estimate. Independent-binomial resampling is CONSERVATIVE (true paired noise on delta is smaller because corruption noise is shared -> harder to pass -> safe).
- **Stage 2 (range null):** impose H0 "boundary identical across the swept axis" -> each boundary estimate ~ Normal(0, SE_cell); MC the RANGE (max-min) statistic; take q95.
- **Fire condition:** observed `delta_scales_with_*` > null q95.

THEORETICAL note: `noise_2se` per cell = `2*sqrt(p*(1-p)/TR)`; at TR=200 and p=0.5, 2SE ~= 0.071; saturated/floor cells have near-zero noise; mid-cliff cells carry the boundary uncertainty.

## Envelope-fail-bands

- **HARD_PASS** (STORAGE law has a mapped, MOVING boundary): every (N,F) straddles (SHARDED has a cell >= 0.90 AND a cell <= 0.30, AND delta crosses 0.5) AND (`delta_scales_with_N` > null q95_N OR `delta_scales_with_F` > null q95_F) AND cross-seed `cv(boundary_corr) < 0.15`. cv is a 3-seed metric; single-seed FULL emits an MM_TENTATIVE candidate; MM_STANDARD requires 3-seed cv<0.15 (Skunkworks aggregates the s7/s13/s19 siblings).
- **HARD_PASS_NULL** (boundary is scale-free -- a strong clean result too): boundaries well-defined at every (N,F) but `delta_scales_with_*` <= null q95 on BOTH axes -> "STORAGE advantage collapses at a boundary independent of N,F". File BOUNDED_NULL (like P9v2), NOT a failure.
- **MIDDLE_BAND:** exactly one of the two scaling axes fires (single-seed FULL; cv unresolved).
- **HARD_FAIL (design bad, no atom):** any (N,F) fails to straddle the cliff (SHARDED all >0.9 or all <0.3); OR PAIRING_VALID assert fails (any cell has non-identical antecedent indices / corruption masks across arms); OR SATURATION_PC < 0.95; OR cardinality mismatch.

## HP_SCOPE per-arm

- **SHARDED + BUNDLED (paired):** `[HARD_PASS_boundary_moves | HARD_PASS_NULL_scale_free | MIDDLE_BAND | HARD_FAIL_straddle/pairing]`. SHARDED is the in-band discriminator arm (straddles by design); BUNDLED is the floor reference arm (its value IS the storage advantage; no HARD_PASS floor is applied to it).
- **SATURATION_PC:** `[Gate_D_reproducer]` acc >= 0.95 required or HARD_FAIL.

## PAIRING_VALID pre-flight gate (the small cell refactor the memo specifies)

The memo requires: "confirm SHARDED and BUNDLED at a fixed salt consume identical antecedent indices + corruption masks ... refactor so items+corruptions are drawn first (storage-independent) and passed to both storage layouts; assert bit-for-bit. If the assert fails, pairing is invalid and the cell must not ship."

Implemented: `draw_shared_state(gen, ...)` pre-draws start_idx, fan_choices, and per-step corruption (mask + phasor) ONCE; `run_chain_paired` consumes ONLY that pre-drawn state (draws NOTHING from the generator internally). Each arm returns (a) an `input_hash` of the exact shared inputs it consumed, (b) a `ncf0_hash` of the step-0 non-rule antecedent factor `A_cur.conj()*POS_step.conj()*IMPL_conj` (identical across arms iff antecedent indices + fan-slots + POS/IMPL match), and (c) a `mask0_hash` of the step-0 corruption mask. `pairing_valid = (input_hash_S == input_hash_B) AND (ncf0_hash_S == ncf0_hash_B) AND (mask0_hash_S == mask0_hash_B)`, checked per cell. Any cell with `pairing_valid == False` -> smoke/full HARD_FAIL. NOTE (verified in selftest): the reference `run_chain` already had NO storage-dependent generator draw before the corruption draw, so the two arms were already paired; this refactor makes pairing valid BY CONSTRUCTION (not by hoping two generator streams stay in lockstep) and adds the explicit assert. selftest asserts `run_chain_paired(SHARDED) == run_chain(SHARDED)` bit-for-bit (physics-preserving).

## CARDINALITY_OK

- **SMOKE:** 3 N x 2 F x 5 corr x 2 storage = 60 paired storage-evals + 1 PC = **61**. TR=40. `EXPECTED_N_UNITS_SMOKE=61`.
- **FULL:** identical grid; TR=200. `EXPECTED_N_UNITS_FULL=61`. SMOKE and FULL exercise the SAME code path (SMOKE=FULL structure; only TR differs). Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on `observed != 61`.

## Discipline gates satisfied (SCHEMA-VET pre-dispatch checklist)

- **cardinality_ok:** EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL = 61; verdict counts phase_map length; `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch.
- **META_RULE_AF (ARMS-MUST-DIFFER):** verifies SHARDED vs BUNDLED output hashes distinct at the first cell AND SHARDED low-corr vs high-corr output distinct at N=512,F=1 (both axes fire). `arms_differ_verified` emitted. Exemption: none (arms legitimately differ).
- **META_RULE_J (per-unit failure-class):** no bare `except:`; specific RuntimeError classes propagated (NAN_IN_SHARDED_CODEBOOK, PROPS_DTYPE_MISMATCH, UNKNOWN_STORAGE).
- **META_RULE_K (discriminator-fires):** discriminator (boundary_corr + N/F scaling vs binomial null) declared; smoke gates on infra + PAIRING_VALID + SHARDED-straddles-all-6 + PC, NOT on the scaling discriminator firing (null-hypothesis smoke discipline per `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03`).
- **META_RULE_L (strictly-above-floor):** HARD_PASS requires scaling STRICTLY > MC null q95 (not >= 0); HARD_PASS_NULL is the complementary real result.
- **META_RULE_M (calibration):** `default_ok_for_this_regime` -- BETA=8.0 ALPHA=0.5 inherited; empirical bracket at TR=40 confirms SHARDED straddles at every (N,F).
- **META_RULE_AH (atomic final metrics):** `tmp_replace` via `os.replace()` everywhere (wrapper).
- **META_RULE_AG (baseline_in_band):** SHARDED (the discriminator arm) straddles [<=0.30 .. >=0.90] at every (N,F) BY DESIGN (empirical bracket); enforced at smoke gate. `baseline_in_band: True_by_straddle_condition`. BUNDLED at floor is the intended storage-advantage reference (not a saturated discriminator).
- **META_RULE_AC (numbers tagged):** all empirical numbers MEASURED@ (bracket), THEORETICAL@ (2SE, Plate bound), or CITED@.
- **except SystemExit: raise** before `except Exception` in the wrapper (Section 8). Grep-clean of `except BaseException` / bare `except:`.
- **CRLB:** `crlb_n/a: "categorical accuracy; boundary is a grid-crossing LOCATION gated against an explicit two-stage MC binomial noise-floor null (the analog of a CRLB for a boundary estimate here)."`
- **cell_chunked:** true (one seed per file; s7/s13/s19).
- **start_marker_written:** true (`_write_minimal_metrics(out_dir, "STARTED", ...)`).
- **crash_diagnostic_present:** true (`_write_import_crash_sentinel` in outer try/except; `except Exception` not `BaseException`).
- **heartbeat_present:** per-phase-point flush prints (61 pts; each < ~5s on CPU; timeout well under 30min so runner `python -u` + per-point flush suffices).
- **defensive_error_checking:** `passed_all_4_patterns`.
- **progress_logging:** `print_flush_true` -- every per-phase-point line uses `flush=True`. `progress_cadence_expected_s: 5`.
- **arms_differ_verified:** true. **final_metrics_atomicity:** `tmp_replace`.

## Compute architecture

`(c) mixed with justification`: batched matmul at each phase point (cleanup = TR x N @ N x M matmul, `run_chain_paired` internally batched over TR trials); Python for-loop across the (N,F,corr) sweep is unavoidable (each point has a different codebook shape -- M x F x N -- so points cannot be batched into a single matmul). Per-phase-point wall < 10s on CPU at TR=40 (heaviest N=8192,F=4 ~4-5s/arm). **Torch is CPU-only on this host (2.12.0+cpu).** GPU-batching not applicable (no CUDA locally); remote FULL may use GPU if available, but modest sizes (N<=8192, M<=4800) make CPU adequate.

## SCHEMA-VET Section 15 gates

- **A) effective_vs_nominal_parameter_audit:** M, N, F, corr feed directly into `build_rules` / `run_chain_paired`; no partition/routing intermediary changes effective values. `sweep_alignment_verdict: ALIGNED`.
- **B) bracket_includes_discriminating_band:** empirical bracket -- every (N,F) straddles (a cell >= 0.90 AND a cell <= 0.30; delta crosses 0.5). By design, boundary-mapping REQUIRES straddling saturated + floor cells to locate the transition. `discriminating_fraction`: at least 1/5 cells per (N,F) land in [0.30, 0.90] with the cliff crossing bracketed; `straddles_condition_at_smoke_gate: True` enforced.
- **C) signal_shape_compatibility_audit:** single-primitive cell (SHARDED-vs-BUNDLED chain); no cross-primitive signal-shape edges. `composition_edges: []`.
- **D) reproduce_prior_chain_grade_result_as_positive_control:** `positive_control_arms: [SATURATION_PC]` reproduces the Gate D easy regime (iterative_cosine SHARDED M=800 N=2048 corr=0.20) expected acc >= 0.95; tolerance 0.05 vs prior P6/P7/P8/P16 baseline. Additionally the SHARDED arm reproduces the P16 cliff shape at N=512,F=1 (cross-check, same primitive same regime).
- **E) functional_requirement_decomposition_present:** functional requirement = "measure where the SHARDED>>BUNDLED storage advantage COLLAPSES, PAIRED and non-vacuous, and whether that boundary moves with N and F." Existing chain-grade primitive `run_chain` (refactored to `run_chain_paired`) addresses it directly (SHARDED + BUNDLED are native storage args; N/F/corr native). No new mechanism required beyond the paired-draw refactor.

## Provenance rail

Corpus is synthetic FHRR chain composition (no external data). `corpus_provenance: synthetic_paired_sharded_vs_bundled_fhrr_chain_storage_boundary_v1`. No LLM calls (`_LLM_CALL_COUNTER` asserted 0 before final write).

## SMOKE-then-FULL / queue / ETA

- **SMOKE:** 1 seed (7), TR=40, `local_cpu_queue` (SMOKE-only-on-local-cpu, USER-LOCKED 2026-07-01). Gate = cardinality + PAIRING_VALID (all 30 cells) + arms-distinct + SATURATION_PC + SHARDED-straddles-all-6-(N,F). NOT gated on the scaling discriminator firing (null-hypothesis smoke discipline).
- **FULL:** 3 seeds {7,13,19}, TR=200, 61 pts/seed, CHUNKED one-seed-per-file. Route via Orchestrator (remote_cpu_queue, or overnight_queue GPU) -- exp_dev cannot push. MM_STANDARD promotion requires 3-seed cv(boundary_corr) < 0.15.
- **ETA:** per-seed FULL wall estimated from SMOKE wall x (200/40 matmul-portion scaling); see completion report for the measured smoke wall and the derived `--timeout`.

## Framing (per USER prompt; MM_TENTATIVE at SMOKE at most)

HOLD_PENDING_3SEED_FULL is the honest default even if the scaling discriminator fires at SMOKE (Fix#28 discipline; single-seed smoke has overstated 3-seed discriminators by 0.05-0.25 this session). MM_STANDARD requires 3-seed cv<0.15 (arc-continuation != arc-closure). Both PASS bands are genuine results:
- **HARD_PASS** -> `EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALES_{N|F|N_AND_F}_v1`: the #1 surviving Stage-1 law has a mapped, moving boundary; extends P4's "N-invariant gap" (which was SHARDED-ceiling-pinned) to the in-band regime.
- **HARD_PASS_NULL** -> `EMPIRICAL_STORAGE_ADVANTAGE_BOUNDARY_SCALE_FREE_BOUNDED_NULL_v1`: the advantage collapses at a fixed corr independent of N,F (a strong clean result too, like P9v2).

Independence: independent of the encoder rescue (different files entirely). Uses local_cpu_queue for SMOKE only.

## Sibling wrappers plan

- `exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s7.py` (SMOKE + FULL seed 7)
- `exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s13.py` (FULL seed 13)
- `exp_stage1_regime_probe_18_storage_advantage_boundary_paired_v1_s19.py` (FULL seed 19)

All three authored 2026-07-04 (single-line SEED diff); dispatch each separately (chunked-per-seed; runner death loses one seed only).
