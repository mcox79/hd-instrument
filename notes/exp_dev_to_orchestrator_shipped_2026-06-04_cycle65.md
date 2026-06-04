# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 65 (queue refill + Phase 0.5 core)

## Shipped this cycle (user: refill empty queues "5 then 5 more")
GPU (overnight_queue):
- substrate_position_binding_combined_arch_trigram_v1_n4096 (Bundle E; ungated by Bundle B HARD_PASS) -> COMPLETED.
- substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu (5N x 50seed; tighten deletion-cert CI) -> COMPLETED.
- substrate_hierarchical_5corpus_meta_v1_n2048_gpu (flagship aggregator; smoke HARD_PASS H3=2.35 vs cross 4.83)
  -> runner marked FAILED, but likely GPU CONTENTION from the concurrent Llama crash-loop (manual re-run clean).
- phase05_v1_llama32_1b_residual_extract_v2_patched (Testbed's patched script, re-queued via --rerun-as) ->
  patch fixed import crash (startup.log + F:\ redirect now active) but still fails at a LATER stage; crash-loop
  killed; surfaced to Testbed (their lane).
CPU (remote_cpu_queue):
- phase05_v1_substrate_audit_core_v1 (Exp-Dev substrate-side core: Algorithm1 + kappa3-drift z-test + deletion
  cert; validated on synthetic; ready for Testbed real npz via env HDLAB_RESIDUAL_NPZ).
- substrate_alpha_ramp_mct_slowing_v1_n4096 (smoke HARD_PASS: graceful->catastrophic capacity curve + MCT
  critical-slowing 10.3x FREE early-warning signal).
- substrate_trained_mini_lm_readout_fix_nsweep_v2_capped (running; the v1 mis-route fix).

## Operational
- Killed the Llama crash-loop (was failing itself + collaterally failing concurrent GPU jobs via contention).
- ROUTING-SANITY gate in queue_add.sh is live (rejects numpy->GPU; warns numpy+large-N->CPU).

## Backlog (next cycle -- new handoffs/routings, NOT yet built)
- hierarchical re-queue (after confirming the manual full run completes clean post-Llama-kill).
- cross-domain handoff anchors 2 (ECR-vs-LRU eviction) + 3 (orthogonal vs random domain keys capacity).
- change_request_bundle_f_add_iterated_mode_cells; research_drill system1_hybrid / operating_modes (drills).
- CIFAR-10 non-linguistic probe (needs a manual loader; torchvision absent on runner).
- multimodal_substrate_primitives + unified_cross_modal handoffs (design-stage drills).

## Phase 1a / kappa3 norm
Phase 1a (drosophila CPU) still not landed. kappa_3 NLO normalization still unanswered by Research.

**END.**
