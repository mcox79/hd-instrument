# exp_dev -> Strategy: K6 axis 3 cleanup-iteration SMOKE HARD_FAIL

**Filed**: 2026-05-24 by exp_dev
**Trigger**: K6 axis 3 cleanup-iteration smoke HARD_FAIL. Cleanup loop DIVERGES.

## Smoke result

best_hold_out_acc=0.031 at T=0 (0.5x chance, below chance level).
T=0: 0.031, T=1: 0.016, T=2: 0.000, T=4: 0.000, T=8: 0.000.

Cleanup iterations make performance WORSE, not better. The probe = obj * sign(attr_t)
is not a valid key in W's attractor basin; re-querying with a corrupted intermediate
diverges from all stored items rather than converging.

## Root cause hypothesis

The cleanup iteration assumes W has attractor structure around stored bindings.
But W is a LINEAR Hebbian associator (outer products), not a Hopfield network.
Linear W @ probe has no attractor basins; each step amplifies noise from
cross-talk terms. True resonator cleanup requires NONLINEAR feedback (e.g.,
thresholding at each step in resonator network formulation).

## Rescue directions for K6 (per [[feedback-rehabilitation-after-rejection]])

1. **Axis 4 -- Bet X position-indexed integration** (NEXT per v193 rescue list):
   use position-indexed mechanism class rather than pure compositional binding.

2. **Resonator with thresholding** (modified axis 3): use threshold step at each
   cleanup iteration: attr_{t+1} = sign(W @ (obj * binarize(attr_t, threshold))).
   Different from current linear accumulation.

3. **Axis 2 at larger N** (envelope rescue): axis 2 hierarchical pre-binding failed
   at N=512 (smoke only). May succeed at N=4096+ where cross-talk is lower.

4. **Factored retrieval** (new mechanism): decompose W into task-specific components
   and query with task context vector before attribute retrieval.

5. **K6 scope narrowing**: accept K6 as a 🟡 evidence-strength row requiring
   mechanism-class innovation; axes 1/2/3 exhausted or blocked; sequencing axis 4.

## Recommended next action for Strategy

Route axis 4 (Bet X position-indexed integration) to exp_dev. Axes 1/2/3 are
now all blocked (1: dim-scaling saturated; 2: hierarchical pre-binding HARD_FAIL;
3: cleanup-iteration diverges). Axis 4 is the remaining untested mechanism-class path.
