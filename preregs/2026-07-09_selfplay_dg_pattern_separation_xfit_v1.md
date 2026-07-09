# Pre-registration: selfplay_dg_pattern_separation_xfit_v1

Anchor: `selfplay_dg_pattern_separation_xfit_v1`
Cell: `experiments/exp_selfplay_dg_pattern_separation_xfit_v1.py`
Date: 2026-07-09
Gates: master-map BUILD #2 (internal self-play referential grounding) -- the brain-grounded FIX for the
confirmed differentiation negative.
Drill: `notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`
Prior cell (reference): `exp_selfplay_differentiation_failmask_decorrelation_v1.py` (commit 866f245b);
prereg `preregs/2026-07-09_selfplay_differentiation_failmask_decorrelation_v1.md`.

## Question
The differentiation VET confirmed disjoint-data cross-fit (B1) is the revival axis (naive-mirror
failmask-corr ~0.77 -> B1 ~0.39, grounding retained ~0.60) but INSUFFICIENT alone (still ~2x the
independence bar ~0.20). The reconciliation drill established brain-consensus across four independent
literatures: the brain fixes a shared-UPSTREAM blind spot by DECORRELATING THE CODE BEFORE THE SPLIT
(dentate-gyrus pattern separation), NOT by downstream reconciliation/precision-weighting (consumers, not
producers, of independence). **Does an upstream, fixed, independently-seeded DG-style pattern-separation
stage per branch, layered onto the B1 cross-fit arm, drive the two halves' failure masks GENUINELY
INDEPENDENT while RETAINING grounding -- the sweet spot plain downstream differentiation (B1 alone) could
not reach?**

## Task construction (self-play referential naming game; REUSED verbatim from the differentiation cell)
Referents = ConceptNet subgraph nodes (REUSED `load_cn_subgraph` + `char_trigram_features` + `build_adjlist`
+ `ProjHead`/`info_nce`/`vicreg_repulsion`, cert 06e5a493d). Speaker: PRIVILEGED info access
(neighborhood-augmented `Xn`); Listener: BARE (`X`). Shared discrete K-symbol message channel `P` (the
anti-collapse bottleneck; shared in ALL arms). The DG stage REUSES `hdlab.hippocampal_encoder.DGProjection`
VERBATIM (fixed bipolar random expansion feat->dg_dim + sign-preserving top-K -> ternary sparse code;
built + unit-tested, selftest `_st_dg_pattern_separation` PASSES).

## Three arms
- **B0_mirror** (MUST-FAIL control): Enc_S == Enc_L tied, differ ONLY in info access. Predicted HIGH
  failmask-corr (~0.77 shared-blind-spot signature). If B0 does not fire (>=0.40) at smoke -> screen
  saturation-vacuous, re-spec.
- **B1_crossfit** (the ~0.39 axis being improved): separate Enc_S/Enc_L; Speaker fit only on fold A,
  Listener only on disjoint fold B; channel P shared. No DG stage.
- **DG_XFIT** (the TREATMENT): B1 cross-fit + per-branch INDEPENDENTLY-SEEDED fixed DG pattern-separation
  upstream of the encoder split. Speaker Xn -> Xn_dg (seed_s = seed*13+5001); Listener X -> X_dg
  (seed_l = seed*13+6001, INDEPENDENT). Encoders take the DG codes as features; train cross-fit as B1.
  DG_XFIT vs B1 differ ONLY by the DG stage -> the controlled comparison isolates the DG contribution.

## DG design parameters (DECIDED by exp_dev; all HYPOTHESIZED unless MEASURED-tagged)
- `dg_dim = 2 * feat_dim` (2x expansion; constant across profiles for SMOKE=FULL mechanism-ratio parity).
  HYPOTHESIZED@this-prereg: 2x is a pragmatic expansion (biology ~10x; 10x of feat_dim=8192 is infeasible on
  CPU). Cross-branch independence (the active ingredient here) comes from the INDEPENDENT projection seeds,
  not the expansion factor; expansion is secondary on near-orthogonal text features.
- `dg_sparsity = 0.08` (keep top-8% by magnitude, ternary). CALIBRATION NOTE: initial 0.04 destroyed
  grounding at smoke (DG grounding 0.373 < 0.40 floor) while giving only +0.05 decorrelation. Raised to 0.08
  to give the CORE hypothesis (decorrelation-sufficiency) a fair test rather than confounding it with
  grounding-destruction. This choice WEAKENS the decorrelation axis (less separation), so it makes HARD_PASS
  HARDER, not easier -- anti-p-hacking. Logged in `config.dg_sparsity`.
- Independent per-branch, per-seed projection seeds -> proper seed-variance in the DG structure.

## Discriminator (the whole test; `failure_mask_corr` REUSED VERBATIM)
Per referent, two INDEPENDENT per-half competence outcomes on the SAME decision:
`speaker_correct[r] = argmax_c P[m(r)].Enc_S(view_S[c]) == r` (privileged self-decode);
`listener_correct[r] = argmax_c P[m(r)].Enc_L(view_L[c]) == r` (== the JOINT communicative-grounding event).
`failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct)` (phi over referents).
`grounding_acc(arm) = mean(listener_correct)`.

## Pre-registered bands (BOTH; LOCKED before FULL dispatch; per drill S2 falsifiable predictions)
- **HARD_PASS** (upstream pattern-separation cracks the self-grounding barrier): DG_XFIT `failmask_corr
  <= 0.20` AND `grounding_acc >= 0.50` AND `(B1 corr - DG corr) >= 0.10` (material improvement, not seed
  noise) AND all arms' codes non-degenerate (entropy >= 1.0 bit, >= 2 symbols) AND DG codes non-degenerate
  AND B0 fires (corr >= 0.40, both halves in [0.05,0.95]).
- **HARD_FAIL case (a)** (representation-level fix INSUFFICIENT -> the drill's flagged next step): DG_XFIT
  `failmask_corr >= 0.35` WHILE grounding retained (>=0.50) => the shared blind spot is very likely
  DISTRIBUTION/OBJECTIVE-level; a per-branch representational transform cannot fix it. REDIRECT to an
  exogenous-referent / held-out-reconstruction mechanism (Thread 2). Diagnostic, not a dead end.
- **HARD_FAIL case (b)** (over-aggressive sparsification DESTROYS grounding): DG_XFIT `grounding_acc < 0.40`
  (even if corr improves) => DG strips referential content. Fix = restrict PS to a non-semantic subspace.
- **MIDDLE_BAND**: DG_XFIT corr in (0.20, 0.35] with grounding >= 0.50 -> one sparsity/expansion sweep
  before concluding.
- **SATURATION_VACUOUS**: B0 `failmask_corr < 0.40` OR B0 failure-rate degenerate => screen not firing.
- **CODE_COLLAPSE_VOID**: any arm entropy < 1.0 bit => degenerate-code artifact; test void.
- **DG_CODE_DEGENERATE_VOID**: DG codes collapse (sparse-rate outside [0.005,0.30] / rows not distinct /
  DG pathologically INCREASES within-branch similarity) => DG mechanism did not fire; re-spec.

## Compute architecture
Class (c) mixed sequential-CPU with justification. Shallow linear ProjHead (feat/dg_dim -> code) + K x code
channel; per-step batched matmuls + Gumbel-softmax + candidate scoring. The DG stage is a one-time fixed
bipolar-projection matmul + top-k per branch per seed (numpy BLAS). NOT GPU-batching-mandatory: nets small
(code_dim<=192, dg_dim<=16384); cost is the sequential self-play loop (genuine epoch dependency); 3 arms x
5 seeds is ~1.5-2.5h CPU. Storage: no_storage (transient codes; no PartitionedStore writes).
`progress_logging: print_flush_true` (line-buffered stdout + flush=True + per (seed,arm) heartbeat; FULL
timeout_s >= 1800).

## SCHEMA-VET gate fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_arms(3) * n_seeds (no sweep axis); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land.
- `arms_differ_verified: true` -- all 3 arms' (speaker,listener) mask-pair digests asserted pairwise-distinct
  per seed (MEASURED: smoke passed the assertion; codes distinct).
- `final_metrics_atomicity: tmp_replace` (write_metrics -> os.replace; crash-diag atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException). Grep-gate PASS.
- `crlb_n/a`: discriminator is a within-cell failure-mask CORRELATION vs the B0 must-fail control, not a
  closed-form noise floor. `discriminator_reachability: true` -- HP corr<=0.20 sits inside [0, corr(B0)~0.79].
- `baseline_in_band: true` (AG) -- B0 failure rates 0.05..0.95 both halves (MEASURED smoke spk=0.364
  lis=0.370).
- `calibration_check: adaptive_with_discriminator_gate` -- K + Gumbel tau anneal + dg_expansion/sparsity
  fixed per profile; anti-collapse entropy floor + B0-fires + baseline-in-band + DG-fires recomputed per run
  (NOT tuned-for-verdict; the sparsity raise makes HARD_PASS harder).
- `cell_chunked: false` (arms x seeds looped in one cell; per-unit `write_partial` checkpoints).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`.
- `defensive_error_checking: passed_all_4_patterns`.
- `HP_SCOPE`: decorrelation HP -> {DG_XFIT} vs {B0 fires, B1 reference}; screen-fires -> B0; grounding floor
  -> DG_XFIT; anti-collapse -> ALL arms; DG-code non-degeneracy -> DG_XFIT.
- `discriminating_fraction: n/a` (no sweep axis; 3 fixed arms). `sweep_alignment_verdict: n/a`.
- `positive_control_arms`: B0_mirror (reproduces the shared-blind-spot high-corr signature at the test
  regime, MEASURED smoke 0.785) + B1_crossfit (reproduces the differentiation cell's B1 axis, MEASURED smoke
  0.327 vs prior smoke 0.316, within tolerance).

## Functional Requirements
1. Two encoders, tied or cross-fit -> ProjHead x2 (implemented).
2. Fixed independently-seeded DG pattern-separation per branch -> DGProjection x2 (reused; the treatment).
3. Shared anti-collapse-bottlenecked message channel -> MessageChannel (K prototypes) + entropy reg.
4. Per-referent independent competence of each half on the SAME decision -> eval_masks.
5. Failure-mask independence screen -> failure_mask_corr (reused verbatim).
6. Joint grounding metric + floor -> grounding_acc + GROUNDING_FLOOR.
7. DG-non-collapse guard -> `_dg_nondegenerate` (sparse-rate band + distinct rows + non-pathological-corr).

## Smoke result (MEASURED, gate CLEAR; 3 seeds x 3 arms, 223.1s local CPU)
MEASURED@data/exp_selfplay_dg_pattern_separation_xfit_v1_smoke/metrics.json:gates
- B0_mirror failmask_corr=0.785 (seeds 0.795/0.735/0.826) spk_fail=0.364 lis_fail=0.370 -> SCREEN FIRES +
  in-band.
- B1_crossfit corr=0.327 (0.350/0.293/0.338) grounding=0.468.
- DG_XFIT corr=0.291 (0.304/0.261/0.307) grounding=0.410 improve(B1-DG)=0.036 ; dg_fires=True
  (sparse spk=0.081 lis=0.196 both in [0.005,0.30]; distinct=1.000; decorr_gap spk~0.010 lis~-0.003).
- codes_ok=True (entropy B0/B1/DG = 3.26/2.84/2.71 bits) ; arms_differ passed ; discriminator telemetry
  selftest ok (planted corr high=0.77/indep=-0.07; e2e tied=1.0/separated=-0.05; DG toy decorr_gap=0.34).
- **Smoke verdict = MIDDLE_BAND**: DG_XFIT decorrelates slightly below B1 (0.327->0.291) but the improvement
  (0.036) is well under the 0.10 material-improvement margin and corr (0.291) is above the 0.20 HP bar; smoke
  grounding 0.410 is a conservative LOWER bound (K=12 smoke collision pressure vs K=24 FULL headroom).
- Smoke honestly FORESHADOWS MIDDLE_BAND / HARD_FAIL(a) at FULL (the representation-level DG fix shows only a
  marginal decorrelation gain on this substrate) -- but all four FULL outcomes (HARD_PASS / MIDDLE /
  HARD_FAIL(a) / HARD_FAIL(b)) remain REACHABLE at FULL (5 seeds, 220 epochs, K=24 grounding headroom,
  dg_dim=16384). Both HARD_PASS and HARD_FAIL(a) are declared gold by the drill.

## P estimates (from drill; deflated)
- P(DG_XFIT clears HARD_PASS: corr<=0.20 AND grounding>=0.50 AND improve>=0.10 at FULL): ~0.30-0.35
  (novel-synthesis + biological-translation deflation; smoke's small 0.036 gain deflates this further toward
  the low end).
- P(HARD_FAIL(a): representation-level insufficient -> exogenous redirect): ~0.35-0.45 (smoke-supported).
- P(HARD_FAIL(b): grounding destroyed even at 8% sparsity): ~0.15 (smoke grounding 0.41 is borderline; FULL
  headroom likely lifts it above 0.40).

## Dispatch
FULL -> `remote_cpu_queue` (CPU cell; local is SMOKE-ONLY per USER lock). timeout_s = 7200 (~2h estimate
with margin; heartbeat + print-flush make a hang diagnosable).
