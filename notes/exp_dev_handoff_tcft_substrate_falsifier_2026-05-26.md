# exp_dev handoff -- TCFT-conditioned Jarzynski falsifier on cycle 177 forensic-erase data

**Date.** 2026-05-26
**Author.** Research sub-agent (companion to `notes/research_jarzynski_substrate_2026-05-26.md`).
**Recipient.** exp_dev (next refill cycle).
**Pause gate.** Honors `data/orchestrator_paused.flag`. If paused, file only; do not ship.

---

## TASK

Implement and run a Trajectory-Class Fluctuation Theorem (TCFT, Jurgens-Crutchfield 2022 / JSP 2025) estimator specialized to substrate's SVD-cascade plateau trajectory classes. Use it to re-analyze the cycle 177 forensic-erase data (4 noise cells: p in {0, 0.05, 0.10, 0.20}, 50 trials x 3 seeds). Compare delta_F_TCFT against the Sagawa-Ueda-corrected delta_F that Cap 1 already uses. Also fire the Palassini-Ritort phase-transition diagnostic: confirm that vanilla Jarzynski estimator collapses at substrate operating point (work_std > 4 k_B T in substrate units).

The trajectory class to condition on is "erase trajectories whose pre-erase top-K detached singular values match the SVD-cascade prediction" -- exp_dev chooses the operational definition (likely: |sigma_1_pre - bulk_edge - predicted_excess| / predicted_excess < 0.05 for top-mode conditioning; broader tolerance for plateau-1).

If cycle 177 trajectory logs only stored aggregate work (not per-step delta_W), escalate decision: (a) re-ship a minimal cycle 177-equivalent run with per-step logging (~1 hour CPU at N=1024 smoke; ~3 hours at N=4096 full); OR (b) defer to Strategy for re-prioritization.

## WHY

Load-bearing falsifier for the COMPLEMENTARY vs INDEPENDENT call on Jarzynski/TCFT vs SVD-cascade framework. Three load-bearing claims of the parent research note are tested simultaneously:

1. **Vanilla Jarzynski fails at substrate operating point** (Palassini-Ritort phase transition; work_std > 4 k_B T expected). If fail-diagnostic does NOT fire, the parent note's negative finding is wrong.
2. **TCFT rescues by conditioning on SVD-plateau trajectory class**. If TCFT variance > unconditioned Jarzynski variance, the parent note's positive finding is wrong.
3. **Killer-feature #5 (edit-with-impact-prediction) has a viable theoretical foundation**. If TCFT delta_F agrees with Sagawa-Ueda within +/- 10% on plateau 0, the killer-feature foundation is established.

If ALL THREE hold, the substrate framework gains a non-equilibrium pillar (TCFT) complementary to the equilibrium pillar (SVD-cascade) and the killer-feature #5 product story gains a theoretical foundation. If TCFT fails, the substrate framework loses the killer-feature foundation but no existing cap is endangered.

Pre-reg per [[feedback-envelope-expansion-fail-bands]]. Smoke gate before full. Post-ship REMOTE VERIFY per role contract.

## CONTRACT

Implement helper `hdlab.thermodynamics.tcft_conditioned_jarzynski(W_pre, W_post, work_trajectories, plateau_index)` that returns:

- `delta_F_TCFT` -- the TCFT-conditioned free energy estimate
- `variance` -- TCFT estimator variance (should be lower than unconditioned Jarzynski variance for HARD-PASS)
- `jarzynski_phase_transition_risk` -- bool, True if work_std > 4 k_B T (Palassini-Ritort diagnostic; vanilla Jarzynski expected to collapse)
- `P_class` -- fraction of trajectories in the conditioned class (expected: 50-80% for plateau 0)
- `n_class_trajectories` -- count of trajectories satisfying the class membership

Also implement `hdlab.thermodynamics.vanilla_jarzynski(work_trajectories)` for comparison.

Verification scaffold-free witness: a synthetic two-Gaussian work distribution where vanilla Jarzynski estimator phase-transitions (Palassini-Ritort 2011 reference numbers) and TCFT conditioned on the Gaussian-class label returns the correct delta_F. Witness lives in `verification/test_tcft.py`.

Pre-reg bands (HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL) per parent note section (b). Default plateau_index = 0 (top mode) for main verdict; also report plateau_index = 1, 2 for variance-scaling diagnostic.

## AUTONOMY

exp_dev's call on:
- N for re-ship if needed (suggested 1024 smoke; 4096 full)
- which queue (laptop CPU for the diagnostic + small re-ship; remote CPU for full re-ship)
- smoke vs full sequencing (smoke first; full only if smoke HARD-PASS or MIDDLE)
- exact tolerance for plateau membership (suggested 5% for plateau 0, 10% for plateaus 1-2)
- whether to extend to multi-plateau analysis if plateau 0 cleanly HARD-PASS

Hard rules:
- ASCII-only in print()/verdict_msg per [[feedback-ascii-only-in-scripts]]
- All experiments in background per [[feedback-no-blocking-runs]]
- Per-cell honest re-read per [[feedback-verdict-msg-honest-reread]] -- verdict_handler will compare claimed labels vs per-cell numbers
- ship_name uniqueness check pre-ship per [[feedback-ship-name-collision]] (suggested name: `tcft_substrate_falsifier_v1`)
- Pre-existing dependency check per [[feedback-ship-before-dependency-verified]]:
  - cycle 177 data dir: `data/exp_wave14_betB_crooks_forensic_erase_v2/` (or wherever cycle 177 FULL landed -- exp_dev confirms via the orchestrator status snapshot)
  - if per-step work data NOT in the dir, fall through to re-ship per TASK escalation path
- Self-test per [[feedback-strategy-spec-formula-selftests]]:
  - Vanilla Jarzynski self-test: synthetic Gaussian work distribution mean=2, std=1 (in k_B T units); expected delta_F via numerical integration = -log(integral of P(W) exp(-W) dW); helper should return this within 1% with 10k samples
  - TCFT self-test: synthetic mixture of two Gaussians (modes A and B with class labels); conditioning on class A should give delta_F_A; conditioning on class B should give delta_F_B; both should agree with the closed-form computation within 2% at 10k samples per class
  - Palassini-Ritort diagnostic self-test: synthetic Gaussian work distribution std=5 should return jarzynski_phase_transition_risk=True; std=2 should return False

## Citations

Primary:
- Jurgens, Crutchfield 2022 -- arxiv:2207.03612; JSP 2025 -- "Trajectory Class Fluctuation Theorem." TCFT formulation; equation 14 is the conditioned estimator. (Read the JSP 2025 version for the most current formulation.)
- Palassini, Ritort 2011 -- arxiv:1108.5783 -- "Phase transition in the Jarzynski estimator of free energy differences." Critical threshold ~4 k_B T for work fluctuation magnitude.
- Rooke, Krotov, Balasubramanian, Wolpert 2026 -- arxiv:2601.01253 -- "Stochastic Thermodynamics of Associative Memory." Mean-field tradeoff curve as context.

Parent:
- `notes/research_jarzynski_substrate_2026-05-26.md` -- this drill's research note (full P-budget, calibration penalty 0.13, novel-synthesis cap respected)
- `notes/research_crooks_noise_robust_2026-05-23.md` -- Sagawa-Ueda re-axiomatization for Cap 1
- `notes/research_framework_synthesis_moe_1rsb_saddle_2026-05-26.md` -- SVD-cascade synthesis (equilibrium pillar; this handoff tests the non-equilibrium pillar partner)

## Pre-reg bands (copy-paste from parent note (b))

- **HARD-PASS**: delta_F_TCFT vs Sagawa-Ueda delta_F within +/- 10% across plateau 0 and 1; AND TCFT variance < 5x unconditioned Jarzynski variance; AND Palassini-Ritort diagnostic returns True for plateau 0 trajectories (work_std > 4 k_B T).
- **HARD-FAIL**: Palassini-Ritort returns False on ALL plateau classes AND TCFT estimator variance does not decrease vs unconditioned Jarzynski.
- **MIDDLE BAND**: TCFT works on plateau 0 only, fails for plateaus 1+ (partial coverage).
- **INSTRUMENTATION-FAIL**: cycle 177 trajectory logs lack per-step delta_W; requires re-ship.

## Status_log discipline

exp_dev to log event:
- `event_kind = "experiment_ship"`, `importance = HIGH` on queue_add
- `event_kind = "experiment_verdict"`, `importance = HIGH` on verdict (per standard role contract)
- `plain_language` field MANDATORY per [[feedback-for-you-tab-primary-channel]]
