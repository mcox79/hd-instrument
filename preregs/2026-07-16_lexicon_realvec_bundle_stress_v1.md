# Pre-reg: exp_lexicon_realvec_bundle_stress_v1

**Date:** 2026-07-16
**Author:** hdi_exp_dev
**Anchor:** lexicon_realvec_bundle_stress_v1
**Cell:** experiments/exp_lexicon_realvec_bundle_stress_v1.py
**Runs:** LOCAL / CPU, run-to-completion inline. NO queue / GPU / atoms / push.

## Motivation / the ONE remaining bound being stressed

The end-to-end result (`exp_lexicon_realvec_endtoend_reframe_v1`, HARD_PASS, commit c48604a28)
proved the glass-box grounding pipeline works on REAL DC-centered CoDEx geometry, but only at a
retrieval operating point where geometry was NOT yet limiting: 3-term SVO bundle, N=2048,
`geometry_cost = LEARNED_benign - LEARNED_real = +0.000` exactly, `ORACLE_real = 1.000` (clean
separability, high bundle SNR). So "the pipeline works on real geometry" was proven only where
geometry does not pressure retrieval. This cell STRESSES the retrieval axis until real concentrated
geometry actually bites, then characterizes the pipeline's behavior there.

## Pre-flight probes (MEASURED, scratchpad, not committed -- calibration evidence)

- **Cleanup breadth alone does NOT bite:** ORACLE_real stayed 1.000 with geometry_cost +0.000 across
  v_noun = {160..1600} (n_concept up to 2000 ~ full n_ent=2034) at N in {512,1024,2048} on the 3-term
  SVO bundle. MEASURED@probe_geom_bite. The 3-term crosstalk is too weak; V is not the limiter.
- **Bundle LOAD bites:** packing L role-filler pairs into ONE superposition and crossing the ~N/16
  FHRR crosstalk cliff pressures cleanup. At N=512, v_noun=160: ORACLE_real 1.000(L16) -> 0.953(L48)
  -> 0.882(L64) -> 0.698(L96) -> 0.540(L128); ORACLE_benign consistently above ORACLE_real
  (geometry_cost +0.02..+0.04). MEASURED@probe_learned_vs_oracle.
- **LEARNED tracks ORACLE at a constant gap:** with map_acc=0.965 (V=200), LEARNED-vs-ORACLE gap held
  ~+0.03 across L={16..128} (does NOT amplify under bundle strain; = the 1-map_acc=0.035 lexicon
  error). MEASURED@probe_learned_vs_oracle.
- **Reframe holds at N=512:** DC_DEFLATE sep-AUC=0.946, perm_p=0.0025, n_surv=394, survivor near-true
  0.755 vs rejected 0.492. MEASURED@reframe probe.

## Questions

- **Q1 (bundle-stress survival):** as bundle load L stresses retrieval (ORACLE_real < 0.90), does the
  end-to-end LEARNED-lexicon pipeline degrade GRACEFULLY -- keep tracking ORACLE within a small,
  non-amplifying gap and stay >> random -- or does the learned lexicon's error COMPOUND under bundle
  crosstalk (gap grows with L = a real bound)? `geometry_cost = ORACLE_benign - ORACLE_real` isolates
  the pure real-geometry penalty (no learner confound).
- **Q2 (reframe at scale/strain):** does the survivor-near-true semantic-cost reframe still hold on
  the full real entity-set codebook at the stressed low N=512, with geometry-discarding controls?

## Compute architecture

- **Class: (b) sequential-CPU with justification.** FHRR bind/bundle/cleanup on complex128 numpy;
  per-(L,arm,seed) cleanup is BATCHED (one `Q @ cand_rows.T` matmul over all L queries). The KGE fit
  is cached (k24_e200_s1). Estimated full wall time < 15 min on laptop CPU (probe: full L-sweep single
  seed ~ tens of seconds). Not a GPU-batching candidate (per-point wall << 10s; cached fit dominates).
- **Storage strategy: no_storage / bundled-as-discriminator.** The L-fact superposition IS the
  discriminator (bundle capacity under FHRR crosstalk); bundled is the object of study, not an
  accidental default. No downstream chained composition.
- **progress_logging: line_buffered_stdout** (`sys.stdout.reconfigure(line_buffering=True)` at start +
  per-seed/per-L flush prints). timeout_s < 1800 so §17 heartbeat not mandatory, provided anyway.

## Arms (fixed)

- Q1 per bundle-load L: `ORACLE_real` / `LEARNED_real` / `RANDOM_real` (floor) / `ORACLE_benign`
  (geometry-cost reference at a perfect lexicon; isolates the real-geometry penalty).
- Q2: `DC_DEFLATE` (primary) / `FPE_WIDE` (geometry-discarding control) / `RANDOM` (floor/framing).

## Config

- Full: N=512, fit_epochs=200 (cached), v_noun=160, v_verb=40 (V=200, VET'd learner regime),
  Ls=[16,32,48,64,96,128], seeds=[1,2,3], n_trials=80, n_perm=2000.
- Smoke: N=512, v_noun=80, v_verb=20 (V=100), Ls=[16,48,96], seeds=[1,2], n_trials=30, n_perm=600.
- EXPECTED_N_UNITS = n_seeds * n_L (cardinality gate, META_RULE_H).

## Pre-registered bands (envelope-fail-bands)

`stressed_L` = { L : mean ORACLE_real(L) < STRESS_ORACLE_THRESH=0.90 }. `lexicon_gap_bound =
max(0.10, (1-map_acc)+0.05)`.

- **HARD-PASS:** geometry BITES (|stressed_L| >= 1 AND mean geometry_cost over stressed_L > 0) AND
  **(Q1)** at every stressed L, gap = ORACLE_real - LEARNED_real <= lexicon_gap_bound AND the gap does
  NOT amplify (gap@max_stressed_L <= gap@min_stressed_L + 0.08) AND min (LEARNED_real - RANDOM_real)
  over stressed_L >= 0.20 AND ORACLE_real at the strongest stressed L >= 0.30 (retrieval recoverable)
  AND **(Q2)** DC_DEFLATE survivor-vs-rejected sep-AUC >= 0.58, perm p < 0.01, geometry-driven
  (DC n_surv >= 50 and both discarding controls' n_surv <= 0.5 * DC n_surv).
- **HARD-FAIL:** **(Q1)** LEARNED DECOUPLES from ORACLE under strain (a stressed L with ORACLE_real >=
  0.60 but gap > 0.20) OR LEARNED collapses (LEARNED_real - RANDOM_real < 0.05 at a stressed L) OR the
  gap AMPLIFIES sharply (gap@max_stressed_L > gap@min_stressed_L + 0.15), OR **(Q2)** survivors NOT
  near-true (sep-AUC < 0.53 OR perm p >= 0.05).
- **MIDDLE:** partial / mixed.
- **HONEST THIRD OUTCOME:** if |stressed_L| == 0 (geometry never stresses retrieval even at max L) ->
  MIDDLE headline `GEOMETRY_NEVER_STRESSES_RETRIEVAL_AT_THIS_N` (retrieval not the limiter at this N;
  report plainly -- NOT a fail, NOT a win). Probe evidence says this will NOT fire at N=512, but it is
  a pre-registered valid outcome.

## Predicted outcome (HYPOTHESIZED, from probes -- must be reproduced by the full run)

HARD_PASS: stressed_L expected {64,96,128}; mean geometry_cost > 0; LEARNED-vs-ORACLE gap ~+0.03
(constant, <= lexicon_gap_bound=0.10, non-amplifying); reframe sep-AUC ~0.95 p~0.002 geometry-driven.

## SCHEMA-VET checklist

- arms_differ_verified: True (REAL vs BENIGN concept codebooks hash-differ; smoke gate).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise before except Exception (no BaseException / no bare except).
- cardinality_ok: True (EXPECTED_N_UNITS = n_seeds*n_L; verdict counts per-L units, HARD_FAIL on breach).
- baseline_in_band: evaluated at stressed L (ORACLE_real in (0.30,0.90); RANDOM ~ 1/n_noun floor).
  ORACLE_real=1.0 at low L is the intentional UNSTRESSED anchor of the sweep (by design, not a
  saturation bug -- the discriminator is defined at the stressed L where ORACLE < 0.90).
- discriminator survives scale: smoke uses SAME N=512 + asserts >=1 stressed L (L=96) fires
  (ORACLE_real < 0.90) with LEARNED tracking within gap<=0.20 and above random.
- crlb_n/a: "no closed-form noise floor for this cell; the FHRR crosstalk cliff (~N/16) is the physics
  reference, verified empirically by the ORACLE_real(L) curve."
- calibration_check: default_ok_for_this_regime (DC_DEFLATE bandwidth via select_fpe_bandwidth
  target_med_coh=0.10, identical to the VET'd encoding_fix_v1 / endtoend_reframe_v1 codebook).
- deterministic_seeding: True (fixed int seeds; sorted() vocab + filler pool; no hash()/list(set())).
- real_code_path: self-test constructs the REAL fitter (fit_kge_anchor1), REAL learner (learn_lexicon),
  REAL DC_DEFLATE codebook, REAL reframe (reframe_negatives).
- HYPOTHESIZED/MEASURED/THEORETICAL tags applied to all numbers above.
- No new chain-grade primitive composition (reuses VET'd learner + reframe by import); positive control
  = ORACLE arm reproduces clean recovery at low L (the unstressed anchor).
