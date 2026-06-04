# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 69

## Llama v6: RUNNING (no action)
doc ~22100/100000, FAILED=0, wall ~3300s. npz in ~4h. No npz yet -> audit-core-on-real-residuals still deferred.

## Shipped (CPU)
- substrate_training_speed_ladder_stage_a_charlm_v1_n2048 (routing_training_speed_iterative_ladder_stage_a).
  Stage A of the user's training-speed ladder. Fair design: substrate (cf-RPE/posbind-symW + cosine) vs standard
  Adam-softmax head on the SAME context features; speedup = baseline wall-to-match-substrate-BPC / substrate wall.
  Bigram + trigram, V=70, N=2048, 3 seeds. SMOKE NOTE: smoke verdict was HARD_FAIL (0.2x) -- an EXPECTED
  small-N artifact (at N=256 substrate is capacity-starved, gap~0.5, so Adam matches that easy target in 1 epoch).
  Full N=2048 is the real test (substrate BPC scales with N -> harder target for SGD -> where the speedup shows).

## Routed elsewhere (not my lane)
- routing_cornerstone_audit_c1_c2_c3_llama_8b_frontier: explicitly To: Testbed (cloud H100; Llama-3.1-8B
  needs ~16GB > 4060 Ti 8GB). Noted for Testbed; not shipped here.

## Queue state (both fed; pending=5 each)
- GPU: Llama v6 RUNNING + 5 pending (hierarchical-5corpus reship, resonator-dense, cfrpe_stdp, noise-resonator,
  hierarchical-scale-ext).
- CPU: mini_lm v2 RUNNING + 5 pending (audit-core, alpha-ramp, eviction, k3-falsifier, training-speed-stageA).

## Still deferred / pending (for later cycles)
- cross_domain anchor 3 (orthogonal-keys capacity): awaiting Research construction spec (note filed cycle 68b;
  both natural constructions show no orthogonality benefit -- elementwise-bind-into-shared-W can't realize N_domains-x).
- Bundle F (combined-everything + iterated F5/F6): complex 6-cell multi-mechanism; build with care next cycle.
- Level-3 meta-LLM: needs a specific 5-corpus artifact (N=8192,K_d=200) generated first.
- position_binding_corrected_k_star, true_scaling_law handoffs; CIFAR-10 (manual loader); R4 sparse-block-code (lit-verify).

**END.** All ships use write_metrics (cycle-67 fix). cap_map untouched. Next cycle: both queues at 5 -> likely
SKIP new ships unless drained; check Llama v6 npz (run audit core on real residuals when it lands); build Bundle F.
