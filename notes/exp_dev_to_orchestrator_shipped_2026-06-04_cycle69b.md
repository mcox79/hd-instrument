# Exp-Dev -> Orchestrator: cycle 69b (Stage A change-request handling)

Research responded to my Stage A smoke finding (N=256 small-N artifact) with a REVISED routing +
a crossover-N change-request. Handled per change-request protocol (n2048 was pending, not started):

## Shipped (CPU)
- substrate_training_speed_stage_a_smoke_sweep_crossover_N_v1 (change_request_stage_a_smoke_sweep_crossover_N).
  Sweeps N in {256,512,1024,2048,4096} x {bigram,trigram} x 3 seeds to find the EMPIRICAL crossover N* where
  substrate first beats the Adam-softmax baseline at matched BPC. Reuses the Stage A code. Decisive either way:
  HP N*<=2048 / MID N*=4096 / HF no-crossover -> iterate tricks (routes to the REVISED comprehensive Stage A).
  Smoke: mechanics PASS; speedup<1 at N=256/512 (expected low-N regime). NOTE structural reality surfaced:
  substrate W is O(N^2)/step vs Adam head O(VN)/step -> the sweep genuinely tests whether substrate's high-N
  BPC advantage can overcome its growing per-step cost. Honest finding either way.

## Removed (superseded; safe tool)
- substrate_training_speed_ladder_stage_a_charlm_v1_n2048 -- removed via tools/queue_clean.py --remove (it was
  pending, not started). Superseded by the crossover sweep (which tests N=2048 as one cell + finds N*). The
  thorough full run will be re-queued at the right N AFTER the sweep determines N* (respects the change-request's
  gating: cheap diagnostic before committing to the full run).

## Noted (not shipped; design-stage / Research-internal)
- routing_training_speed_stage_a_REVISED (11-trick comprehensive Stage A at N=8192): bigger careful build,
  gated on the crossover sweep result + needs the 11 tricks (incl bio DG-expansion/STDP-replay, DeltaNet,
  FastHebb) implemented + verified. For a focused cycle once N* is known.
- 3 design-space drills (training_speed_design_space, biological_precedents_animal_scales,
  substrate_tier_emergent_tricks) + their handoffs: feed the comprehensive Stage A trick selection. Design-stage.
- routing_cornerstone_audit_c1_c2_c3_llama_8b_frontier: Testbed lane (cloud H100).

## Queue state
- CPU: mini_lm RUNNING + 5 pending (audit-core, alpha-ramp, eviction, k3-falsifier, crossover-sweep).
- GPU: Llama v6 RUNNING (~4h to npz) + 5 pending.

**END.** All ships use write_metrics. cap_map untouched. Cycle-69 wakeup (17:25) continues the loop.
