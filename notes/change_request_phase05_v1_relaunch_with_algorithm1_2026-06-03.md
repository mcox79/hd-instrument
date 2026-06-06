# CHANGE REQUEST — Phase 0.5 v1 relaunch with Algorithm 1 embedding pipeline

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Subject:** Relaunch the Phase 0.5 v1 audit-primitive validation on Llama-3.1-8B with three substantive changes per the Hyperprobe reproduction drill landed today

---

## What this experiment is (plain language)

Phase 0.5 v1 = audit primitives (κ_3 drift, deletion cert, refusal cert) validated against live Llama-3.1-8B residuals via a hyperdimensional probe (Hyperprobe, arXiv:2509.25045). Prior cloud run failed: val_sim plateaued at 0.60 vs paper's 0.89 after 100 epochs. Hyperprobe reproduction drill landed 2026-06-03 with high-confidence diagnosis: 3 fixable issues + 3 code bugs (already being fixed). Total relaunch budget under $50.

---

## Status check requested

Before applying changes:

- [ ] Are the 3 code bug fixes (NaN-check + BFloat16 cast + device placement) completed?
- [ ] Has any partial relaunch already been started?
- [ ] Is the existing Algorithm-1-skipped pipeline currently being used in any other downstream experiment?

Expected: code bugs in progress; no relaunch dispatched; no downstream dependency.

---

## Required changes for relaunch

### Change 1 — Implement 3-stage embedding pipeline per Algorithm 1, Appendix B

The Hyperprobe paper (arXiv:2509.25045) specifies a specific residual extraction protocol that the prior run skipped. This is the PRIMARY cause of the val_sim gap (high confidence per drill).

**Required spec:**
- K-means clustering over layers 16-32 of Llama-3.1-8B
- Sum-pool centroids with k=5
- Use this 3-stage pipeline as the probe input, NOT raw residuals from a single layer

Drill output at `notes/research_drill_hyperprobe_reproduction_setup_2026-06-03.md` contains the full specification. Algorithm 1, Appendix B of the paper is the authoritative reference.

### Change 2 — Extended training schedule

Prior run was 4× too short:
- Total epochs target: ~421 (vs prior 100)
- Early-stop patience: 100
- Learning rate: 3e-5 (LR-finder-derived; not the rate used in prior run)
- Optimizer + decay schedule: per paper (drill output has details)

### Change 3 — Attention-augmented residual blocks (recommended, not required)

Best-result model in the paper uses attention-augmented residual blocks with num_heads=8. If engineering effort permits, include. If not, the embedding pipeline + epoch fix together should still close most of the gap.

### Change 4 — Optional H100 SXM5 vs PCIe

Switching from H100 PCIe to H100 SXM5 saves ~30% wall on the 4× longer training run. At Algorithm-1-pipeline scale + 4× epochs, the wall savings likely justify the hourly-rate premium. Testbed call on which instance type to use.

---

## Budget

**Cloud budget: under $50** per drill estimate. Includes:
- Algorithm-1 embedding pipeline computation (one-time setup per training corpus)
- 4× epoch training (vs prior 100 epochs)
- Hardware: H100 PCIe acceptable; H100 SXM5 recommended if wall matters

If budget creeps above $50 mid-run, surface to research session for decision.

---

## Pre-registered relaunch success criteria

Same as original Phase 0.5 v1 spec, with one addition:

- **Probe quality gate:** val_sim ≥ 0.85 (relaxed) OR ≥ 0.89 (paper-match) before Phase 0.5 sub-tests dispatch
- If val_sim < 0.75 after 4× epochs → substrate-LLM coupling tests cannot be cleanly interpreted; surface to research for design rework BEFORE Phase 0.5 sub-tests dispatch

---

## Dispatch instructions

### IF NOT YET relaunched → apply changes 1-3 (and optionally 4) per above, then dispatch

The 3 code bug fixes are already in progress (your hands). Once those land, apply changes 1-3 to the spec + dispatch. Drill output at `notes/research_drill_hyperprobe_reproduction_setup_2026-06-03.md` is the authoritative reference for Algorithm 1 implementation details.

### IF PARTIAL RELAUNCH ALREADY DISPATCHED with the broken pipeline → abort and restart

Don't keep training the Algorithm-1-skipped pipeline. The val_sim ceiling will be the same 60% regardless of additional epochs without the embedding pipeline change.

### IF relaunch is blocked on something else → surface back to research

If Algorithm 1 implementation turns out to require materially more engineering effort than estimated (drill says it's tractable, but if you find it's not), flag back.

---

## Why this change request

The Hyperprobe reproduction drill diagnosed the val_sim gap with high confidence (P_deflated=0.72). Primary cause is the missing embedding pipeline; secondary is training duration; tertiary is the LR. All three are fixable. Without these changes, relaunch just burns the cloud budget for the same 60% ceiling.

---

## Discipline declarations

- Per `feedback_change_request_protocol`: this is the standard format — addressed to testbed with status-check-first discipline
- Per `feedback_plain_language_experiment_tracking`: experiment described in plain language
- Per `feedback_obey_user_pause_explicitly`: relaunch authorized 2026-06-03 within $50 envelope
- Per `feedback_no_padding_experiments`: each change targets a specific cause of the val_sim gap

---

**END.**

**Testbed:** apply changes 1-3 (and optionally 4) once code bugs land; relaunch; report val_sim trajectory.

**Research session:** awaits relaunch verdict; will trigger Phase 0.5 sub-tests dispatch only if val_sim ≥ 0.75.
