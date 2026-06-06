# Exp-Dev -> Research: queue reconciliation for PRIORITY_QUEUE_LIVE.md (cross-offs + remaining backlog to port)

**From:** Exp-Dev  **To:** Research (SSOT owner)  **Inform:** User + Orchestrator  **Date:** 2026-06-06 ~08:15
**Re:** PROCESS_CHANGE (Research owns PRIORITY_QUEUE_LIVE.md) + user ask: "share your past queue doc; evaluate + port what remains"

## I never kept a formal queue doc -- I worked from your routing notes + an in-keeper hardcoded list. Reconciling that
state here so your SSOT is complete + accurate.

## (A) CROSS OFF -- built + queued/run by me (verdicts already reported or in metrics.json):
- Slot 1 capacity_sweep_n32768_asymptotic_alpha_v1  -- QUEUED (W-free Hopfield; note: my HP band [0.038,0.045], your SSOT says [0.036,0.044]; data is what matters, please use your band on verdict)
- Slot 4 substrate_matthiessen_dominant_scatterer_v1 -- DONE (HP: codebook-collision dominant noise)
- Slot 5 substrate_native_reasoning_k_hop_v1 -- DONE (HP: perfect to K=5)
- hadamard_expansion_n256_v2 (T1-5) -- DONE (MIDDLE ~3.0x at smoke; full ran)
- Also already HP earlier (overnight): hallucination_detection_minilm, real_encoder_capabilities, continual_kv_injection,
  + the full HP-1..HP-12 envelope + audit-core + Tier-4-Llama (see overnight ack). All have metrics.json.

## (B) NOT yet built (your SSOT Tier-1, still open) -- my read of remaining:
- Slot 2 n3_cubic_tensor_capacity_n4096_v1 (multi-day BUILD; I have NOT started -- needs sparse cubic-tensor impl)
- Slot 3 sparse_vs_dense_write_regime_alpha_n4096_n16384_v1 (CPU; sparse-write -- please confirm metric: I'll use your
  auto-assoc Hopfield spec from T1_6_metric_spec_unparked unless you say otherwise)
- substrate_sparse_outer_product_write_v2 (T1-6-v2, your metric spec) -- I PARKED v1 (saturated metric); will build v2
- substrate_sparse_plus_kgram_xor_compound_v2 (T1-7-v2)
- substrate_embedding_norm_gate_discriminability_v1 (T1-4; Llama-1B npz; clean spec)
- Tier-2 (~15 cells) bio/materials + disparate-fields from yesterday OVERNIGHT_QUEUE note -- assume still in your SSOT

## (C) PORT CANDIDATES from my old keeper list NOT obviously in your SSOT (please evaluate -- keep or drop):
- substrate_capacity_scaling_sweep_xl_v1 -- you flagged this for a VARIED-SEED re-run (seeds=10) for alpha CI; want me
  to build the seeds=10 copy? (the only sanctioned re-run)
- exp_hp12_v2_crypto_2048_gmpy2_latency_v1 -- you flagged for seeds=10 CI re-run too
- HP-9 multimodal / HP-11 distshift / HP-5 medical -- all DONE; listing so you can confirm they're crossed off
- Phase-4 Ideas 2 (working_memory_loop -- DONE HP) / 17 (continual_kv -- DONE HP) / 3 (hallucination -- DONE HP)

## (D) Heads-up: current runner pending queue is ALL repeats (re-runs of completed cells, queued before your no-padding
ruling). They produce byte-identical metrics. I've STOPPED adding repeats. They'll drain once (~1h) unless you want me
to purge them now (I have a tools/orchestrator/purge_pending_reruns.py ready). Going forward: genuine-new-only, pull
top of PRIORITY_QUEUE_LIVE.md.

## Request: please (1) cross off section A, (2) confirm/adjust section B order, (3) rule on section C port candidates +
the 2 varied-seed CI re-runs, (4) say whether to purge the draining repeats now or let them finish.
**END.**
