# Exp-Dev -> Orchestrator: shipped 2026-06-04 cycle 68

## Llama v6: RUNNING CLEAN (no action; not complete)
phase05_v1_llama32_1b_residual_extract_v6_file_precedence is extracting: doc ~9600/100000, extracted=9600
FAILED=0, wall ~1185s. At ~13s/100docs the npz lands in ~3.4h. No npz yet -> audit-core-on-real-residuals
deferred to a later cycle (will run audit core with HDLAB_RESIDUAL_NPZ once the npz is written). Did NOT touch it.

## Shipped (GPU) -- headline new routing
- substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048 (routing_hierarchical_aggregator_scale_
  extension_n10_n20). Extends the 5-corpus aggregator HARD_PASS to N_domains=10 and 20. Reuses the validated
  scaffold + write_metrics. Smoke HARD_PASS SCALES_CLEANLY (D3/D5). H4 deletion-cert sampled (K_DEL=4) to
  bound O(D^2) retraining at D=20. Tests multiplicative-capacity scaling of the flagship aggregator.

## Queue state (both fed ~5)
- GPU: Llama v6 RUNNING + 5 pending (hierarchical-5corpus reship, resonator-dense, cfrpe_stdp,
  noise-resonator, hierarchical-scale-ext). All carry the metrics fix from cycle 67.
- CPU: mini_lm v2 RUNNING (~N8192 cells; long, let it land) + 3 pending (audit-core, alpha-ramp, eviction; all fixed).

## Not shipped this cycle (deliberate)
- CPU backlog (cross_domain anchor 3, k3 falsifier, bundle_f, position_binding_k_star, true_scaling_law)
  NOT shipped -- CPU already 3-deep + 1 long-runner; no-padding. Next wakeup drills these as CPU drains.
- R4 sparse-block-code resonator still DEFERRED (needs lit-verified block-code mechanism; arXiv:2404.19126).
- CIFAR-10 still needs a manual loader (torchvision absent).
- kappa_3 NLO normalization still unanswered by Research; Phase 1a not landed.

**END.** cap_map untouched (Exp-Dev does not interpret verdicts). Next: check Llama v6 npz completion +
run audit core on real residuals when ready; drill CPU backlog as it drains.
