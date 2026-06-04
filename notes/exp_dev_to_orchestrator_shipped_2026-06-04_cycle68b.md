# Exp-Dev -> Orchestrator: cycle 68b (queue-fill for 6h unattended window)

User away ~6h; asked to deepen both queues. New note since cycle 68: routing_hierarchical_aggregator_scale_ext
(shipped cycle 68) + exp_dev_handoff_research_level3_meta_llm_over_substrate_aggregator (new, see below).

## Shipped
- substrate_k3_synthetic_uniform_zipf_falsifier_v1_n4096 (CPU). Isolates whether the Zipf marginal is
  load-bearing for Bundle E's K=3 trigram HP. Self-contained 2-arm (synthetic 2nd-order Markov; zipf-vs-uniform
  target selection => skewed-vs-flat marginal; posbind K=3 + symmetric Hebbian both arms). Smoke: manipulation
  validated (zipf marginal entropy < uniform), uniform gap << zipf at smoke -> directionally "Zipf load-bearing".

## Deferred (deliberate; not strawman-shipped)
- cross_domain anchor 3 (orthogonal-keys multiplicative capacity): BOTH natural constructions (auto-assoc bound
  patterns; heteroassoc shared-address) show orthogonal==random at smoke. Crosstalk analysis: elementwise
  bind-into-shared-full-rank-W does NOT realize N_domains-x capacity (dominant cross-domain cross-address terms
  not zeroed by key orthogonality). Construction is underspecified -> note filed to Research
  (exp_dev_to_research_orthogonal_keys_capacity_construction_gap). Will build the exact construction once specified.
- Bundle F (combined-everything trigram + iterated F5/F6): 6 cells x 5 combined mechanisms + 2-step iterated.
  Complex multi-mechanism integration; deferred to a focused wakeup cycle (build with care, not end-of-turn rush).
- Level-3 meta-LLM (new handoff): anchor 1 = 10M routing head on substrate-formatted pairs from a SPECIFIC
  5-corpus HP artifact (N=8192, N_domains=5, K_d=200). That artifact does not exist yet -> needs generation
  first (a Tier-1 substrate run) before the routing-head test. Flagged for a focused build.
- R4 sparse-block-code resonator: still needs lit-verified block-code mechanism (arXiv:2404.19126).

## Queue state for the 6h window
- GPU: Llama v6 RUNNING (residual extraction ~3.4h to npz) + 5 pending (hierarchical-5corpus reship,
  resonator-dense, cfrpe_stdp, noise-resonator, hierarchical-scale-ext). ~5-6h of work.
- CPU: mini_lm v2 RUNNING (~2h) + 4 pending (audit-core, alpha-ramp, eviction, k3-falsifier). ~3-3.5h.
- 30-min autonomous wakeup loop refills both as they drain (will build Bundle F / Level-3 / others next cycles).

**END.** All shipped scripts use write_metrics (cycle-67 fix). cap_map untouched (no verdict interpretation).
