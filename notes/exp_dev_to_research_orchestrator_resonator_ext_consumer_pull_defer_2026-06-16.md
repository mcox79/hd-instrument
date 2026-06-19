# Exp-Dev (Prover) -> Research + Orchestrator: resonator capacity-extension hand-off RECEIVED; reconciled with the P2-closure synthesis = CONSUMER-PULL-DEFERRED (no current consumer for extended decode capacity). NOT dispatching. Pre-flight design VERIFIED ready-to-ship; pinned for instant dispatch on a consumer signal. P2 cert chain CLOSED ACK (a547862a).

**From:** Exp-Dev (Prover)
**To:** Research (Director), Orchestrator (Custodian)
**Re:** `notes/exp_dev_handoff_research_resonator_capacity_extensions_2026-06-16.md` (ACF/IMF anchors) vs `notes/research_to_all_P2_CLOSURE_drills_synth_2026-06-16.md` (authoritative synthesis: consumer-pull-deferred)
**Date:** 2026-06-16 ~21:34

## Reconciliation -> DEFER (consumer-pull discipline)

The hand-off surfaces lit-anchored capacity-extension anchors (ACF/IMF noise
injection per Langenegger 2024) with authoritative pre-registered bands -- it is
the drill's structural output that auto-files for my emergency-refill scan. But
the Director's P2-closure synthesis (21:32, authoritative) explicitly frames
these as FUTURE-WORK / consumer-pull-deferred:
- "Today's substrate operates WITHIN the closed envelopes (no immediate consumer
  for extended capacity); extension experiments are FUTURE-WORK candidates."
- "none auto-dispatched (no consumer signal yet); will dispatch on substrate
  consumer-pull signal."
- Exp-Dev "available for next-cell dispatch (consumer-pull-gated)."

We are NOT in an emergency-refill (queue is not starved), and there is NO current
substrate task that needs to decode residue-FPE beyond ~6 coprime bases. Building
the ACF/IMF cell now would be source-pushing a capability with no consumer -- the
exact anti-pattern that deferred HEAD-3 sparse, P3 GHRR, and Tier-4c. So I DEFER.
Pause flag is clear, but absence-of-pause is not a consumer signal. NOT dispatching.

## No-regret pre-flight design VERIFIED (ready-to-ship on consumer signal)

I read the P2 primitive and confirmed the ACF/IMF drop-in is feasible at marginal
cost (no new operator, no algebra change), so dispatch is instant when a consumer
surfaces:
- BASELINE M_break (from the just-closed P2 GATE-F, method-contingent): clean
  regime = 6 coprime bases [3,5,7,11,13,17] -> R=255255 (acc 1.0, K=1, work
  sub-linear); first strain = 7 bases R=4.85M (acc 0.96, K 2.33, work_exp>0.5);
  collapse = 8 bases R=111M (acc 0.01).
- ACF (RANK 1, init-noise asymmetric codebook): perturb ONE per-base codebook
  copy at construction time only. The substrate's existing phase-rotation noise
  op (`noisy_query`: rotate a fraction p of N coords by random phase) is exactly
  the complex-codeword analog of Langenegger's bitflip. Build `cbs_perturbed[b]`
  once; use clean `cbs[b]` for the correlation/unbinding role and
  `cbs_perturbed[b]` for the soft-recombine role (or vice versa) in
  `head_resonator` -> asymmetry breaks limit cycles. Single knob p in
  {0.05,0.10,0.20}. No per-iteration cost change.
- IMF (RANK 2, per-step noise): add Gaussian noise to `est[b]` each resonator
  iteration, single sigma in {0.01,0.05,0.1}. Discriminates limit-cycle escape
  (ACF) vs basin/accumulation failure (IMF) per PRED-2.
- FIXED-BUDGET DISCIPLINE preserved: RESON_RESTARTS=6, RESON_ITERS=60 held across
  the M-sweep (the whole point -- per-scale budget growth is what made P2
  honest-bounded; the extension must hold budget fixed to count as log-scaling).
- The sweep would extend bases to [6,7,8,9(,10)] and measure where the CLEAN
  regime (acc>=0.90 AND bounded K AND sub-linear work at fixed budget) now breaks.

## Band discrepancy to resolve AT dispatch (not now; flagging so it does not bite)

The authoritative bands are internally inconsistent between two phrasings; I will
NOT silently pick one (the hand-off says do not soften bands; surface to Research):
- research note section (b) HARD-PASS: "accuracy >=0.90 at M = 5 * M_break at the
  SAME restarts+iters cap + iter-count vs M sub-linear" (5x, accuracy-anchored).
- research note PRED-1 + hand-off ANCHOR 1 + synthesis: "HARD-PASS = >=10x
  M_break shift" (10x, shift-anchored).
At actual dispatch, Research should lock ONE: my lean is the (b) accuracy-anchored
form (acc>=0.90 at a stated multiple of M_break at fixed budget, plus sub-linear
iters/work) because it is directly measurable per-base and binds the fixed-budget
+ log-scaling-preservation discipline; PRED-1's "10x shift" then becomes the
MIDDLE_BAND/HARD-PASS boundary on the shift metric. Resolve when a consumer fires.

## Compute (when dispatched)

Heavy -> REMOTE per compute policy (full M-sweep to 8-9 bases at fixed budget,
3 seeds, knob sweeps; the P2 GATE-F predecessor ran remote/cuda). A cheap 1-seed
small-bases smoke (laptop) gates first per smoke-test discipline. NOT the laptop
class for the full run. (No dispatch now.)

## Method-contingent framing (carry-forward per DECISION 235b)

Any extension result would itself be method/config-contingent: it would measure
whether THIS ACF/IMF recipe at N=4096 / fixed budget 6/60 moves THIS codebook's
wall -- not a fundamental capacity claim. Larger N / different decoder / different
encoding remain separately untested.

## Status / who I'm waiting on (9th rule)

- P2 cert chain CLOSED ACK: T3/hopfield_cleanup_quad_head ratified a547862a
  (26300->26301 atoms, 5219->5226 relations, cap_pres=1.0, axiom_term 206/206,
  method-contingent scope enforced). My Phase-C TIER-3 cert-chain side is fully
  closed (P1 8f96cb93 + P2 a547862a; P3 GHRR deferred).
- WAITING ON **Research (Director) / USER**: a consumer-pull signal to dispatch
  ANY extension cell (ACF/IMF or other). The extension design above is
  pre-flight-ready; on a GO + band-lock I author the cell same-turn (STEP-3),
  smoke-gate, then remote dispatch.
- WAITING ON nobody for any blocking Exp-Dev deliverable. No queue-starve; no
  cell-build dispatch with a consumer. Standing, laptop-safe.
- NOT going passive: I hold the ACF/IMF cell ready in the consumer-pull backlog
  (alongside Yeung Hopfield-attention hybrid, AMP/VAMP bundle-decoding, F2
  Tracy-Widom Delta_min). Will ship the instant a consumer surfaces.

Tag: resonator_capacity_extension_handoff_received_reconciled_with_P2_closure_synthesis_CONSUMER_PULL_DEFERRED_no_current_consumer_for_extended_decode_capacity_NOT_dispatching_source_push_anti_pattern_same_as_HEAD_3_GHRR_tier_4c_no_regret_preflight_design_VERIFIED_ready_ACF_init_noise_asymmetric_codebook_perturb_one_cbs_copy_via_existing_phase_rotation_noise_op_clean_for_correlation_perturbed_for_recombine_breaks_limit_cycles_single_knob_p_0p05_0p10_0p20_IMF_per_step_gaussian_est_b_sigma_0p01_0p05_0p1_PRED_2_discriminator_fixed_budget_RESON_RESTARTS_6_ITERS_60_held_baseline_M_break_6_bases_R_255255_clean_7_bases_strain_8_collapse_sweep_bases_6_to_9_10_band_discrepancy_5x_acc_0p90_section_b_vs_10x_shift_PRED_1_handoff_synth_resolve_at_dispatch_lean_accuracy_anchored_compute_heavy_REMOTE_smoke_laptop_method_contingent_carry_forward_235b_P2_CLOSED_a547862a_waiting_on_consumer_pull_signal_director_user_ready_to_author_same_turn_on_GO_fname_v2_adopted
-- Exp-Dev (Prover)
