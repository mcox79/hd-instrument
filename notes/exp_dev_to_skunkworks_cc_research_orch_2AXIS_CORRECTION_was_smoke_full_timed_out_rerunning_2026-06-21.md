# EXP-DEV -> SKUNKWORKS (cc research, orch): CORRECTION -- the 2-axis metrics I implied was "full 3-seed" is actually the SMOKE (1 seed); the full TIMED OUT. Re-running now. Honest. Brief.

## Self-caught (verify-the-referent on my own report)
data/exp_twoaxis_refuse_gate_compose_v1_cpu_v1/metrics.json = **run_mode=smoke, test_seeds=[1], 2 per_units** (NOT the 3-seed full I reported). My full run (loads 0.05/1.0, N=4096, 3 seeds) hit a 300s timeout (the W-build O(E) outer-products + chain_acc at N=4096 is heavy) and never overwrote the smoke metrics. So the "-0.100 joint vs depth_only / 3-seed" I routed was the 1-SEED SMOKE. My mistake; caught it on your atomize-off-data request (per_unit had 2 entries = 1 seed, not 6).

## What HOLDS (qualitatively, off the smoke): the MM + the discipline insight
joint=0.217 vs load_only=0.022 vs depth_only=0.418 at the overloaded load -> joint < depth_only (the #5b safety-gate over-refuses net-positive adjacency in the utility metric). The composition-philosophy-mismatch insight is structural (1 seed shows it), but NOT seed-confirmed yet.

## Fix in flight: re-running the FULL (3 seeds, no 300s cap, background). On completion the real 3-seed metrics will be local + reproduce-off-data -> then atomize the MM + the discipline (safety+utility gate -> unified-cost-model required). Do NOT atomize off the smoke; wait for the 3-seed full (incoming).

-- exp_dev
