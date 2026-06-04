# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 66

## Headline: Llama-3.2-1B residual extraction UNBLOCKED + queued (heavy GPU job)
Testbed resolved the token (SCP'd licensed .hf_token to runner; verify_runner_llama_access -> PASS). I
re-verified PASS + queued phase05_v1_llama32_1b_residual_extract_v5_token_fixed (overnight_queue, 10800s).
All three blockers now cleared: datasets installed (c65) + token (c66) + v3 stage-logging. Expected to run
end-to-end (~model download ~2.5GB to F:\hf_cache then extract). THE GPU-saturating job is finally live.

## Reconciled
- hierarchical_5corpus_meta_v2: HARD_PASS confirmed (full N=2048; aggregates 5 domains near-losslessly,
  H3_agg=2.598 vs specialist 2.561 vs cross-domain 6.196, deletion retention=1.002). NO re-queue needed.

## Shipped (CPU)
- substrate_eviction_ecr_vs_lru_v1_n4096 (cross-domain anchor 2; audit-preserving eviction; ECR vs LRU at 90%
  capacity). Smoke validates mechanics; full N=4096 is the discrimination test.

## Earlier this session (in flight / done)
- GPU completed: Bundle E, finer-N spectral arbiter, hierarchical HARD_PASS, resonator, Bundle G (ext-context
  ceiling), cf-RPE+STDP superadditive.
- CPU: audit core, alpha-ramp/MCT (HARD_PASS smoke: graceful->catastrophic + 10.3x MCT early-warning), mini_lm v2.

## Remaining backlog (next cycles)
cross-domain anchor 3 (orthogonal vs random domain keys); k3_synthetic_uniform_zipf_falsifier;
change_request_mode4_resonator_add_sparse_noise; bundle_f iterated-mode; position_binding_corrected_k_star;
true_scaling_law; CIFAR-10 (needs manual loader, torchvision absent); multimodal/cross-modal (design-stage).

## Notes
- datasets-install side effect: wikitext loader hits HfUriError -> falls back to local cache (data OK); could
  pin datasets / fix loader if desired.
- Phase 1a (drosophila CPU) + kappa_3 NLO normalization: still not landed / unanswered.

**END.**
