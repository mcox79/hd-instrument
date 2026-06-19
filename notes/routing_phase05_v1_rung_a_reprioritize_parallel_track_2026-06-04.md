# Routing -- Phase 0.5 v1 Rung A re-prioritize as parallel track

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Re-prioritization note (re-surfaces an already-routed item; engineering spec unchanged)
**Source:** existing change-request `change_request_phase05_v1_final_8gb_4060ti_2026-06-03.md` (still authoritative)

---

## Capability question

Does Algorithm 1 (KG-distillation embedding pipeline per arXiv:2509.25045 Appendix B) + Hyperprobe MLP + substrate audit primitives (kappa_3 drift detection + rank-1 deletion certificate + refusal certificate) work cleanly on Llama-3.2-1B residual streams, validating substrate-as-AUDIT-on-real-LLM at substrate-class scale?

This is the Tier 1 product validation (substrate audits a finished LLM) -- distinct from the substrate-as-training-mechanism work (Tier 2-6) that consumed today's research focus.

---

## Why this is being re-surfaced

Today's brain drill cascade (7 drills + convergent architecture empirical batch) consumed all Research's routing focus. Phase 0.5 v1 Rung A engineering has not started; it's queued behind the substrate-physics + brain-inspired-tinychar work.

But Rung A and the convergent architecture batch DON'T CONFLICT:
- Rung A runs on remote GPU 4060 Ti (8GB VRAM available)
- Convergent architecture tests run on local CPU
- Different runner slots; can run in parallel
- Phase 0.5 v1 Rung A engineering can start now while the convergent architecture work continues

This note re-surfaces Phase 0.5 v1 Rung A as a parallel-track priority alongside (NOT instead of) the convergent architecture batch.

---

## Cost + resource

- Remote GPU 4060 Ti 8GB (per existing change-request)
- Llama-3.2-1B in BF16: ~4-5GB total memory; comfortable on 8GB
- Runs alongside substrate-physics queue (combined ~5-7GB; tight but feasible per existing spec)
- Cost: $0 (NO cloud per `feedback_cloud_only_when_absolutely_necessary`)
- Engineering: ~6-10h (Algorithm 1 K-means + sum-pool + Hyperprobe MLP + 3 audit primitive integration; per existing change-request spec)
- Experiment wall: ~2-4h on remote GPU

---

## Pre-reg (UNCHANGED from existing change-request)

**Hyperprobe gate:**
- HP: val_sim >= 0.80 at Llama-3.2-1B (relaxed from paper's 8B-specific 0.89; structurally different scale class)
- MIDDLE: val_sim 0.65-0.80
- HF: val_sim < 0.65 -- Algorithm 1 implementation issues OR LLM-scale mismatch; surface for research

**Audit primitive gates (run only if Hyperprobe HP):**
- kappa_3 drift: HP detects drift at sigma_sep > 3.0 across 5 seeds on held-out perturbed probe set; HF at sigma_sep < 1.0
- Deletion cert: HP cos >= 0.95 for non-target retrievals after rank-1 deletion (per v341 protocol applied to 1B-derived bipolar substrate vectors); HF cos < 0.80
- Refusal cert: HP correct refusal classification >= 90% on held-out adversarial probes; HF < 70%

P_deflated: 0.55 (Algorithm 1 debug HP at Pythia-160M v374 strong empirical anchor; same pipeline at Llama-3.2-1B should preserve)

---

## Open dependencies

### User-side: 3 code bug fixes (status check)

Original Phase 0.5 v1 cloud run failed with 3 bugs:
1. NaN check in verdict logic
2. torchmetrics BFloat16 unique() crash (needs float32 cast)
3. CUDA/CPU device mismatch

**Are these fixed?** The Pythia-160M Rung 0 debug PASSed cleanly (3/3 seeds) which suggests the new pipeline doesn't have these specific bugs -- but the Llama-3.2-1B Rung A scaffold may inherit something from the prior failed cloud-path code. Worth verifying before dispatch.

**If fixes are needed:** ship them to Exp-Dev as integration into the Rung A scaffold engineering. ~1-2h additional engineering.

### Exp-Dev side: Algorithm 1 + Hyperprobe + audit primitives engineering

Per the existing change-request:
- Algorithm 1 K-means clustering over Llama-3.2-1B layers 8-16 + sum-pool centroids k=5
- Hyperprobe MLP probe training (~421 epochs target, early-stop patience 100, LR=3e-5, AdamW)
- 3 audit primitive harnesses (kappa_3 drift + deletion cert + refusal cert)

Reuses the Algorithm 1 debug code that PASSed at Pythia-160M; extends to Llama-3.2-1B + adds audit primitives.

---

## Dispatch sequencing

### Phase 0.5 v1 Rung A subphase 1: Hyperprobe at Llama-3.2-1B (gate)

**Anchor:** `phase05_v1_llama32_1b_hyperprobe_v1`

- Engineer Algorithm 1 + Hyperprobe MLP at Llama-3.2-1B scale (~6-8h)
- Run Hyperprobe training to val_sim measurement
- If HP (val_sim >= 0.80): proceed to subphase 2
- If MIDDLE/HF: surface to Research for diagnosis

### Phase 0.5 v1 Rung A subphase 2: Audit primitives on bipolar substrate (gated on subphase 1 HP)

**Anchor:** `phase05_v1_llama32_1b_audit_primitives_v1`

- Apply 3 substrate audit primitives to the Hyperprobe-derived bipolar substrate vectors
- Cells: kappa_3 drift detection / deletion certificate / refusal certificate
- Each tested at 5 seeds against pre-reg HP/HF bands

### Parallel with both: substrate-physics + brain-inspired convergent architecture continue uninterrupted

---

## Why this matters for product narrative

Today's substrate-physics findings (L=10000 composition + capacity-stress + drift detection NHSE-grounded + deletion cert ROME/MEMIT precedent) are all on STATIC substrate properties -- proven at substrate-class scale but NOT at real-LLM scale.

Phase 0.5 v1 Rung A is the FIRST end-to-end validation of substrate AT REAL-LLM SCALE (Llama-3.2-1B residual streams). If HP:
- "Substrate audits live LLM residuals" capability empirically validated
- 3 killer features (drift detection + deletion certificate + refusal certificate) tested in product context
- Lit anchor strengthened: Hyperprobe paper precedent at 1B scale (relaxed from 8B paper-match)
- Conservative product anchor distinct from the more aggressive substrate-as-training-mechanism work

This is the CLEAREST product story we have. Worth shipping in parallel with the exploratory frontier.

---

## What I am NOT requesting

- Cloud GPU dispatch (per `feedback_cloud_only_when_absolutely_necessary`; remote 4060 Ti 8GB only)
- Llama-3.1-8B paper-match reproduction (8GB GPU can't fit; deferred per prior change-request)
- Phase 0.5b KG-distillation full deployment (blocked on Rung A)
- Change to existing change-request spec (still authoritative; just re-prioritization)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-cloud-only-when-absolutely-necessary]]: remote GPU only; $0 cloud
- Per [[feedback-small-scale-first-methodology]]: Llama-3.2-1B is the smallest real-LLM rung that validates the capability; not premature scale
- Per [[feedback-no-padding-experiments]]: Rung A subphases discriminate Hyperprobe + audit primitives independently
- Per [[feedback-change-request-protocol]]: this re-surfaces the existing change-request; no spec change
- ASCII-only output

PROT-018: anchors use `_v1` suffix
PROT-021: source=remote GPU, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** Phase 0.5 v1 Rung A is the highest-value pending LLM-integration item and runs on a different runner (remote GPU 4060 Ti) than the convergent architecture batch (CPU). Engineering can START NOW in parallel. Estimated ~6-10h engineering + ~2-4h experiment wall. Status check: user-side bug fixes status?

**Research session:** holds for Rung A subphase 1 (Hyperprobe gate) verdict; will ship audit-primitive synthesis when subphase 2 lands.

**Orchestrator:** informed. Cap_map: Rung A would found NEW sub-property under PP-8 (Phase 0.5 deployment) row -- "substrate audits Llama-3.2-1B residual streams via Algorithm 1 + Hyperprobe + 3 audit primitives" if HP.

**User:** are the 3 prior bug fixes (NaN check + BFloat16 cast + CUDA/CPU device) ready, OR were they specific to the prior cloud-path code (which Rung 0 Pythia-160M debug bypassed)? If ready, engineering can start immediately. If not, surface fix status.
