# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 64b (note-triggered)

**From:** Exp-Dev  **To:** Orchestrator (inform)  **Date:** 2026-06-04

## Trigger
User "check notes" -> 3 new actionable notes since cycle 64. Shipped all 3 (1 Testbed handoff + 1 routing + 1 change-request).

## Shipped (all overnight_queue / GPU)
1. **phase05_v1_llama32_1b_residual_extract_v1** (Testbed handoff; 10800s) -- THE genuinely GPU-efficient job
   (Llama-3.2-1B, ~2-3h wall, 4-5GB VRAM). License accepted (user); Testbed engineered+smoke-validated the
   script+prereg+verbatim queue cmd (first Testbed->Exp-Dev queueing handoff). Queued as-is; remote self-test
   passed (23s, model loaded). VSA_D confirmed at 4096 default (my substrate-side is independent of it).
   F:\ self-config on the desktop; artifacts npz (n_docs,9,2048) SCP'd back when done.
2. **substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu** (routing_bundle_a_combined_superadditive; 14400s)
   -- 4 arms (hebbian / cfrpe / sparse_hebbian / combined) x 5 seeds; is cf-RPE+sparse superadditive at bigram?
   Corrects Bundle A's conflation (its "drosophila_sparse" was actually sparse+cf-RPE). Smoke: substitutive
   preview (cf-RPE is the driver; sparse adds little on top). Full N=512 is the test.
3. **substrate_friston_fep_trigram_cell_v1_n4096** (change_request_bundle_b_add_friston_fep; 14400s) --
   Bundle B addendum (shipped SEPARATE since Bundle B already queued = change-request-protocol "in flight").
   FEP vs K=1 at trigram; does FEP activate at K=3 where it HF'd at K=2? Smoke: FEP worse than baseline
   (preview HARD_FAIL -> implicit-subsumption, consistent with Bundle A). Full N=4096 is the test.

## State
- GPU overnight_queue: 4 pending (Bundle B, Llama extract, superadditive, FEP-trigram) + Bundle C running. WELL-FED
  including the heavy Llama job (real GPU saturation).
- CPU: 6 pending + 1 running.

## Phase 0.5 Rung A handshake established
Testbed->Exp-Dev queueing protocol now live (Testbed produces script+prereg+ready-to-queue note; Exp-Dev runs
the verbatim queue_add). Next: when Llama npz lands, Testbed pings residuals_delivered; Exp-Dev runs the
substrate-side core (Algorithm 1 + 3 audit primitives) on it.

## Discipline
- No verdict interpretation. PROT-018/019/021/022 enforced; smoke dirs cleared; ASCII-only; GPU template.
- Change-request handled per protocol (FEP cell shipped separate, not silently folded into queued Bundle B).
- Bundle E still HELD (gated on Bundle B). Phase 1a (CPU) still not landed. kappa_3 normalization still unanswered.

**END.**
