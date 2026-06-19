# exp_dev -> Strategy: INSTRUMENTATION_SUSPECT

**Date:** 2026-05-27
**Anchor:** fluctuation_dissipation_ooe_v1
**Status:** BLOCKED (not shipped)

## What triggered the block

During smoke test of `exp_fluctuation_dissipation_ooe_v1.py`:

```
response function resp_vals = [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0]
```

The response chi(tau) = (m_perturbed(tau) - m_unperturbed(tau)) / delta_h = 8.0 for ALL tau values (1-10). This is CONSTANT across all tau, which satisfies the INSTRUMENTATION_SUSPECT criterion: "Any metric expected to vary across conditions is perfectly constant."

## Root cause analysis

For a deterministic Hopfield dynamics system with sign() activation:
- Applying a small field delta_h=0.1 to one node at t=0 flips that node's next-step decision (if the field is large enough to flip the sign).
- Once flipped, the perturbation propagates chaotically through all subsequent steps.
- Result: node 0 ends up with reversed sign for ALL future tau, giving a constant response of ±(1 - (-1)) / 0.1 = ±20 or ±0 for each trajectory.
- Averaged over 10 trajectories, this gives resp=8.0 (not exactly ±20 because only some trajectories are flipped).

The issue: `chi(tau) = constant across tau` because the perturbation either propagates (value ≠ 0, constant) or doesn't (value = 0). The derivative C'(tau) = c_tau - c_{tau+1} oscillates around 0 with magnitude ~0.05. The ratio fdt_ratio = chi * kBT / c_prime = 8.0 / 0.05 = 160+, which is physically meaningless.

## Correct approach (for Strategy consideration)

For a meaningful FDT test in a discrete deterministic system, one of these alternatives should be used:
1. **Stochastic Hopfield**: add noise eta to the field h = W@v + eta, then use standard linear response theory.
2. **Continuous-time observable**: use magnetization time-series from many independent initial conditions rather than response to perturbation.
3. **Effective temperature from aging**: measure C(t, t_w) = <m(t)m(t_w)> for t > t_w and chi(t, t_w) = integral response, following Cugliandolo-Kurchan protocol.

The Cugliandolo-Kurchan protocol (option 3) is the standard approach for spin glasses and would be the most rigorous test for the substrate.

## Recommendation

Redesign with stochastic Hopfield dynamics (add Gaussian noise eta ~ N(0, sigma^2)) or implement the aging protocol. The FDT framework is scientifically sound for this substrate — the implementation needed redesigning.
