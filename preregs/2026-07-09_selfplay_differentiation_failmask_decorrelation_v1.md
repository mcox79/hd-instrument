# Pre-registration: selfplay_differentiation_failmask_decorrelation_v1

Anchor: `selfplay_differentiation_failmask_decorrelation_v1`
Cell: `experiments/exp_selfplay_differentiation_failmask_decorrelation_v1.py`
Date: 2026-07-09
Gates: master-map BUILD #2 (internal self-play referential grounding loop).
Drill: `notes/research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`

## Question
WHICH minimal differentiation makes a shared-substrate internal Speaker/Listener pair have GENUINELY
INDEPENDENT failure modes (uncorrelated per-referent failure masks), and does that differentiation cost the
pair its ability to still AGREE (communicative grounding)? The possibility question is CLOSED (the brain
proves a system can be its own independent partner). The open question is the MECHANISM: info-access
asymmetry ALONE is predicted (SSL-collapse + emergent-comm + Neyman-orthogonality; convergent P_deflated
~0.60) to reproduce the shared-blind-spot mirror signature; at least one further differentiation axis is
predicted required.

## Task construction (self-play referential naming game on the reused relational encoder)
Referents = ConceptNet subgraph nodes (REUSED `load_cn_subgraph` + `char_trigram_features` + `build_adjlist`
+ `ProjHead`/`info_nce`/`vicreg_repulsion`, cert 06e5a493d). Speaker has PRIVILEGED info access
(neighborhood-augmented feature `Xn = X + neighbor_weight * mean-neighbor X`); Listener has BARE info access
(`X`). A SHARED discrete K-symbol message channel `P [K, code_dim]` (K << n_referents) is the ONLY
communication path (shared in ALL arms -- the medium, not the differentiation axis; the mandatory
anti-collapse bottleneck per emergent-comm). Speaker emits `m(r)=argmax_k Enc_S(Xn[r]).P[k]`
(straight-through annealed Gumbel at train). Listener decodes over a candidate set {target}+distractors:
`pick=argmax_c P[m].Enc_L(X[c])`.

## Four arms (differentiation of Speaker vs Listener; B0-B3 per Director task)
- **B0_mirror** (MUST-FAIL control): Enc_S == Enc_L tied, live gradients both, differ ONLY in info access.
- **B1_crossfit** (disjoint-data cross-fit; PROVEN rho=0 axis): separate Enc_S/Enc_L, Speaker params fit
  only on referent fold A, Listener only on disjoint fold B; channel P shared.
- **B2_ema_lag** (parameter-lag EMA; BYOL/DINO): Enc_L = EMA/stop-gradient-lagged copy of Enc_S.
- **B3_diff_algclass** (different, TRAINABLE architecture family; cerebellum): Enc_L = 2-layer ReLU MLP
  (ListenerMLP) vs speaker's linear ProjHead; trained jointly (fair grounding test, not a lobotomy).

## Discriminator (the whole test; screen REUSED VERBATIM from stacked_corrections `failure_mask_corr`)
Per referent over an eval set, two INDEPENDENT per-half competence outcomes on the SAME decision:
`speaker_correct[r] = argmax_c P[m(r)].Enc_S(Xn[c]) == r` (speaker self-decode, privileged view);
`listener_correct[r] = argmax_c P[m(r)].Enc_L(X[c]) == r` (== the JOINT communicative-grounding event).
`failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct)` (phi over referents).
`grounding_acc(arm) = mean(listener_correct)`.

## Pre-registered bands (BOTH; LOCKED before dispatch)
- **HARD_PASS**: B0 `failmask_corr >= 0.40` (screen fires; matches ~0.49 precedent) AND at least one of
  B1/B2/B3 has `failmask_corr <= 0.20` AND `(corr(B0) - corr(arm)) >= 0.20` AND `grounding_acc(arm) >= 0.50`
  AND all arms' codes non-degenerate (symbol entropy >= 1.0 bit, >= 2 symbols) AND B0 failure rates in-band
  (0.05..0.95 both halves). => differentiation is the operative ingredient AND preserves grounding.
- **HARD_FAIL variant (b)** (load-bearing negative): among grounding-retaining arms (>=0.50), NONE achieves
  `failmask_corr <= 0.35`. => even proven axes fail to decorrelate; common cause lives UPSTREAM of the split.
- **HARD_FAIL (grounding-destroyed)**: the arms that decorrelate (corr<=0.20) ALL have grounding_acc<0.50.
  => decorrelation only at the cost of destroyed communication (independence-vs-convergence tension).
- **SATURATION_VACUOUS**: B0 `failmask_corr < 0.40` OR B0 failure-rate degenerate => screen not firing.
- **CODE_COLLAPSE_VOID**: any arm entropy < 1.0 bit => degenerate-code artifact; test void.
- **MIDDLE_BAND**: best grounding-retaining arm corr in (0.20, 0.35] with grounding retained.

## Compute architecture
Class (c) mixed sequential-CPU with justification. Shallow linear ProjHead / small MLP + K x code channel;
per-step batched matmuls + Gumbel-softmax + candidate scoring. Matches landed teacher-free encoder pipeline
(CPU-only, cert 06e5a493d) and grounding_snowball (CPU FULL). NOT GPU-batching-mandatory: nets small
(code_dim<=192, feat_dim<=8192); cost is the sequential self-play loop (genuine epoch dependency); 4 arms x
5 seeds is ~45min CPU. Storage: no_storage (transient codes; no PartitionedStore writes).
`progress_logging: print_flush_true` (line-buffered + flush=True + per (seed,arm) heartbeat; FULL
timeout_s >= 1800).

## SCHEMA-VET gate fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_arms(4) * n_seeds (no sweep axis); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land.
- `arms_differ_verified: true` -- B0 (speaker,listener) mask-pair digest asserted != each B1/B2/B3 per seed.
- `final_metrics_atomicity: tmp_replace` (write_metrics -> os.replace; crash-diag atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException).
- `crlb_n/a`: discriminator is a within-cell failure-mask CORRELATION vs the B0 must-fail control, not a
  closed-form noise floor; reachability by construction (B0 fires >=0.40 at smoke; diff arms in [0,corr(B0)]).
- `baseline_in_band: true` (AG) -- B0 failure rates 0.05..0.95 both halves at smoke (verified 0.48/0.50).
- `discriminator_reachability: true` -- HP corr<=0.20 with margin>=0.20 sits inside [0, corr(B0)=0.82].
- `calibration_check: adaptive_with_discriminator_gate` -- K + Gumbel tau anneal fixed per profile;
  anti-collapse entropy floor + B0-fires + baseline-in-band recomputed per run, not tuned-for-verdict.
- `cell_chunked: false` (arms x seeds looped in one cell; per-unit partial checkpoints via write_partial).
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`.
- `defensive_error_checking: passed_all_4_patterns`.
- `HP_SCOPE`: decorrelation HP -> {B1,B2,B3} vs B0; screen-fires -> B0; grounding floor -> claimed diff arm;
  anti-collapse -> ALL arms.

## Functional Requirements
1. Two encoders that can be tied or differentiated -> ProjHead x2 / EMA copy / ListenerMLP (implemented).
2. A shared, anti-collapse-bottlenecked message channel -> MessageChannel (K prototypes) + entropy reg.
3. Per-referent independent competence of each half on the SAME decision -> eval_masks.
4. The failure-mask independence screen -> failure_mask_corr (reused verbatim).
5. Joint communicative-grounding metric + floor -> grounding_acc + GROUNDING_FLOOR.

## Smoke result (MEASURED, gate PASS; 2 seeds x 4 arms, 55.8s local CPU)
- B0_mirror failmask_corr=0.821 (seeds 0.830/0.813) spk_fail=0.482 lis_fail=0.497 -> SCREEN FIRES + in-band
  MEASURED@data/exp_selfplay_differentiation_failmask_decorrelation_v1_smoke/metrics.json:gates.per_arm.B0_mirror
- B1_crossfit corr=0.316 grounding=0.504 ; B2_ema corr=0.758 grounding=0.515 ; B3_diffalg corr=0.171
  grounding=0.254 ; codes_ok=True (entropy 2.7-3.2 bits) ; arms_differ passed ; telemetry-selftest ok
  (planted corr high=0.77/indep=-0.07; e2e tied=1.0/separated=-0.05).
- Provisional smoke verdict = HARD_FAIL_DECORR_DESTROYS_GROUNDING (B3 decorrelates but grounding<floor; B1
  retains grounding but corr>0.20). All three FULL outcomes (HARD_PASS / MIDDLE / load-bearing negative)
  remain reachable at FULL (5 seeds, 220 epochs, K=24 looser -> grounding headroom).

## P estimates (from drill; deflated)
- P(differentiation required; info-access-only insufficient): ~0.60-0.65 (B0 fired 0.82 -> supported).
- P(cross-fit B1 transfers cleanly: corr<=0.20 AND grounding>=0.50 at FULL): ~0.25-0.30.
- P(load-bearing negative: no proven axis decorrelates-while-grounding): ~0.12-0.15.

## Dispatch
FULL -> `remote_cpu_queue` (CPU cell; local is SMOKE-ONLY per USER lock). timeout_s = 5400.
