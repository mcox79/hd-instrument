# exp_dev -> queue: BBMD anchor experiments (Anchor 1 + Anchor 2)

**Date**: 2026-05-23 (late session)
**Trigger**: Research note `notes/research_promising_direction_2026-05-23.md` — Bulk-Bounded Moment-Divergent (BBMD) inference regime proposal as a 12th portfolio capability candidate (P_deflated = 0.45). Cap-12 promotion is conditional on BOTH anchors landing positive — NOT on the synthesis alone.

## Routing entries (markdown-table schema per [[feedback-multi-experiment-routing-notes]])

| queue            | name                                          | script                                                          | prereg                                                          | timeout(s) |
|------------------|-----------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_bbmd_vamp_correspondence_sweep_v1      | experiments/exp_wave14_bbmd_vamp_correspondence_sweep_v1.py     | preregs/2026-05-23_wave14_bbmd_vamp_correspondence_sweep_v1.md  | 5400       |
| remote_cpu_queue | wave14_kappa_profile_cross_codebook_v1        | experiments/exp_wave14_kappa_profile_cross_codebook_v1.py       | preregs/2026-05-23_wave14_kappa_profile_cross_codebook_v1.md    | 5400       |

## Anchor 1 — BBMD_VAMP_CORRESPONDENCE_SWEEP_v1

- **Hypothesis**: AMP-error scales monotonically with the BBMD-distance `sum_{n=2..6} |kappa_n - kappa_n^MP|` while VAMP-error stays bounded across alpha in {0, 0.25, 0.5, 0.75, 1.0}.
- **Design**: interpolate `W_alpha = (1 - alpha) * G + alpha * W_kerdock`, N=4096, M=N, 10 seeds, sigma_noise=0.1.
- **Verdict thresholds (FROZEN in prereg)**:
  - HARD PASS: Spearman rho(AMP-error, BBMD-distance) > 0.8 AND max VAMP-error < 0.05.
  - HARD FAIL: Spearman rho < 0.4 OR max VAMP-error > 0.10.
- **Smoke**: PASS (self-test 7/7); ran N=1024 M=512 3-alpha 1-seed (INCONCLUSIVE expected at smoke; metrics.json written; AMP-rel-err 0.26-0.32, VAMP-rel-err 0.02-0.06 — directionally correct).
- **ETA**: 30-60 min on remote CPU.

## Anchor 2 — KAPPA_PROFILE_CROSS_CODEBOOK_v1

- **Hypothesis**: BBMD-distance ordering `iid_gauss <= SRHT < Hadamard <= RM(1,m) < Kerdock` AND MP-KS < 0.05 for all five — proving standard MP-KS misses AMP-non-universality and kappa_n is the needed extra discriminator.
- **Design**: 5 codebooks at N=4096, M=N, 10 seeds. SRHT = D*H + row subsample; Hadamard = row-subsample of Sylvester; RM(1, m=12) = Hadamard ∪ -Hadamard subsample; Kerdock = substrate 4-coset.
- **Verdict thresholds (FROZEN in prereg)**:
  - HARD PASS: ordering matches expectation AND MP-KS mean < 0.05 for all 5.
  - HARD FAIL: ordering scrambled (iid_gauss not min, Kerdock not max, OR SRHT > RM(1,m)) OR some structured codebook has MP-KS >= 0.05.
- **Smoke**: PASS (self-test 5/5 including iid-MP-KS sanity); ran N=1024 2-codebook 1-seed (iid_gauss BBMD=0.17, Kerdock BBMD=4.05 — directional signal correct).
- **ETA**: 60-90 min on remote CPU.

## Construction notes

- Reed-Muller RM(1, m): used the standard equivalence "RM(1, m) = Sylvester Hadamard rows union -rows" (2N codewords). No new code added to repo; built inline via existing `sylvester_hadamard`.
- SRHT: random sign diagonal D * H, then row subsample. Built inline.
- Kerdock: re-used `make_kerdock_4coset_codebook` from `exp_wave14y_erase_kerdock_v3.py` (PRIMITIVE_POLY supports t in {5, 6, 7} -> N in {1024, 4096, 16384}).
- kappa_n inversion: re-used `moments_to_free_cumulants_general` from `exp_wave14_kappa_n_profile_v1.py` (NCP-Mobius on Catalan partitions).
- MP-KS: pattern from `exp_wave14_kerdock_AMP_universality_pretest_v1.py` step2_mp_fit, vectorized to numpy.

## Decision tree (excerpt from research note)

- BOTH anchors PASS -> propose Cap-12 (BBMD-VAMP); upgrade kappa_n to formal substrate observability primitive.
- Anchor 1 PASS + Anchor 2 FAIL -> Cap-12 framed Kerdock-internal.
- Anchor 1 FAIL -> BBMD as a regime axis is wrong; 5-axis stack remains 5 quirks on one matrix.
- Both FAIL -> drop the BBMD framing; reopen 5-axis decomposition.

## Queue state post-ship

- remote_cpu_queue: 4 pending (`amp_se_kerdock_longiter_v1`, `wave14_rsb_exchange_mcmc_v1`, anchor 1, anchor 2)
- overnight_queue: not modified by this shipment

## status_log entries

- Both shipments wrote `experiment_queued` entries via `log_event` with `importance=HIGH` and plain-language framing.
