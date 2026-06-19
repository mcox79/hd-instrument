# Upstream Push: tau_alpha_measurement_protocol_v1 Smoke HARD_FAIL -- Protocol mismatch

**Date:** 2026-06-02
**Anchor attempted:** tau_alpha_measurement_protocol_v1
**Status:** BLOCKED (smoke HARD_FAIL; protocol design mismatch)

## Smoke results

- rel_dev (alpha=0.05): 0.921 (92% deviation from theory)
- rel_dev (alpha=0.10): 0.902 (90% deviation from theory)
- tau_emp ~ 1000-1700 steps vs tau_theory ~ 10000-20000 steps

## Root cause

The tau_alpha theory assumes forgetting dynamics (Oja/online learning rule with decay).
The implemented protocol uses ADDITIVE streaming writes: W_new = W_old + Xi_new^T Xi_new / N.
This does NOT produce aging/forgetting -- it just adds new patterns indefinitely.
The effective tau in additive writes is ~1/alpha (normalized) not N/alpha (physical scale).

The theoretical prediction tau_alpha = N/alpha is for a system where:
  - W_t = W_{t-1} - gamma*W_{t-1} + xi_t xi_t^T / N (online rule with decay gamma)
  - OR the write rule naturally forgets old patterns (bounded capacity)

## Protocol fix needed

To measure tau_alpha correctly, the write rule needs forgetting:
  W_t = (1 - eta) * W_{t-1} + xi_t xi_t^T / N
where eta is the forgetting rate. Then tau_alpha = 1/eta in write-step units.
The existing measurement of tau_emp is measuring the wrong quantity.

## Recommendation for Strategy / Research

Provide the correct streaming write rule (with forgetting parameter eta) and the
formula for tau_alpha in terms of eta and N. The current script can be adapted once
the forgetting dynamics are specified.

The measurement framework is correct (exponential decay fit + comparison to theory),
but the experiment design needs the forgetting update rule specified.

Acted-on 2026-06-02: tau_alpha smoke fail diagnostic; redesign deferred to research
