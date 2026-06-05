# ROUTING CORRECTION -- Re-address in-flight experiments to Exp-Dev (primary)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Recent routings addressed to Testbed or Orchestrator should be read as addressed to Exp-Dev (primary). User correction landed 2026-06-04: experiments go directly to Exp-Dev; Testbed reserved for cloud GPU only.

---

## What this is (plain language)

Research routings 2026-06-03 + 2026-06-04 addressed many CPU and owned-remote-GPU experiments to "Testbed" or routed through "Orchestrator." Per user correction (2026-06-04): experiments should go directly to Exp-Dev as primary recipient; Orchestrator informed (not routed-through); Testbed reserved for cloud GPU dispatches only.

This correction note updates addressees for the in-flight routings without silently editing them. Per [[feedback-change-request-protocol]].

---

## Files affected -- updated addressee

The following routings should be read as addressed to **Exp-Dev (primary)** rather than Testbed:

### Recent (2026-06-04)

1. `routing_joint_DH_brain_correct_rung1_redesign_2026-06-04.md` -- joint D+H brain-correct rung-1 (5 arms; continuous float32 + cf-RPE + sparse multiplicative gating). CPU experiment.
2. `routing_spectral_monitor_full_cycle_reframe_2026-06-04.md` -- Tier 1 annotation (strategy_scribe) + Tier 2 complementary primitives experiment (now Exp-Dev). Per Exp-Dev's update, the spectral monitor TRAIN_CHARS rescue already ran at 400k chars; Tier 2 is partially satisfied empirically.
3. `routing_deltanet_pattern_fallback_design_b_2026-06-04.md` -- DeltaNet Design B fallback (conditional dispatch). CPU rung-1.

### Earlier (2026-06-03)

4. `routing_phase_A_now_rung1_brain_inspired_plus_hrc_audit_2026-06-03.md` -- Phase A brain-inspired rung 1 + HRC audit. CPU.
5. `routing_phase_B_overnight_batch_2026-06-03.md` -- Phase B overnight batch. CPU.
6. `change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md` -- Phase 0.5 v1 final routing (rung 0 Pythia-160M debug + rung A Llama-3.2-1B). Remote GPU 4060 Ti (owned hardware; NOT cloud).
7. `change_request_data_attribution_variation_sweep_drill2_redesign_2026-06-03.md` -- data attribution variation sweep redesigned. CPU.
8. `routing_paired_pattern_dual_cf_probe_2026-06-03.md` -- paired-pattern dual cf probe. CPU.
9. `routing_gamma_vs_M_discriminating_probe_2026-06-04.md` -- gamma-vs-M discriminating probe (already ran per overnight cycle; HF). CPU.

### 0-compute annotation routings (already correctly addressed)

These already go to Orchestrator / strategy_scribe and are unaffected:

- `routing_capmap_correction_scs_to_nhse_annulus_2026-06-04.md`
- `routing_pp58_reopen_with_scs_framework_2026-06-04.md`
- `capability_implication_note_to_orchestrator_hrc_reframe_2026-06-03.md`
- `capability_implication_correction_scs_refuted_lyapunov_only_2026-06-04.md`
- `capability_implication_note_spectral_gap_scs_grounding_2026-06-04.md`

### Cloud-GPU-eligible routings (none currently)

Per [[feedback-cloud-only-when-absolutely-necessary]] discipline, no current routings require cloud GPU. Phase 0.5 v1 was de-routed from cloud to remote GPU 4060 Ti earlier today.

---

## What this changes

Nothing experimentally: same designs, same pre-reg HP/MID/HF bands, same resources, same cost ceilings.

Only changes:
- Addressee header (Exp-Dev primary; Orchestrator informed)
- Removes implicit assumption that Testbed dispatches non-cloud work
- Clarifies that Exp-Dev owns both substrate-physics-class AND LM-integration-class engineering at non-cloud scale

---

## Going forward

Per [[feedback-routings-direct-to-exp-dev]] saved 2026-06-04: all experiment routings address Exp-Dev (primary) with Orchestrator informed. Testbed only when cloud GPU is genuinely required.

---

**END.**

**Exp-Dev:** treat the listed routings as addressed to you; engineer + dispatch per the original designs and pre-reg bands. The joint D+H scaffold you already built can be ratified under this correction.

**Orchestrator:** informed of the routing-discipline update; cap_map annotation routings still flow through you or to strategy_scribe directly.

**Research session:** all future experiment routings address Exp-Dev (primary).
