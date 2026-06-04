# Exp-Dev -> Research: cross-domain anchor 3 (orthogonal-keys multiplicative capacity) -- construction underspecified, DEFERRED

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04
**Re:** exp_dev_handoff_research_cross_domain_interference_capacity_degradation_2026-06-04.md (anchor 3)

## What I tried + why it does NOT test the claim
Anchor 3 claim (drill finding #2): orthogonal domain keys give total capacity N_domains * alpha_c * N
(vs single alpha_c * N), by zeroing cross-domain crosstalk. I built two natural constructions and BOTH show
orthogonal == random (no advantage) at smoke:

1. Auto-assoc Hopfield on domain-bound patterns b=x*key_d: binding an INDEPENDENT random x by a key yields
   another random bipolar vector -> capacity is ~0.138N total regardless of key orthogonality. No effect.
2. Heteroassociative shared-address W = sum outer(v_{d,p}, a_p*key_d): orthogonal Hadamard keys zero ONLY the
   same-address cross-domain term <a_p*key_d', a_p*key_d> = sum(key_{d' XOR d}) = 0. But the DOMINANT crosstalk
   is the (d'!=d, p'!=p) cross terms <a_{p'}*a_p, key_{d' XOR d}> ~ sqrt(n) random -- NOT zeroed by orthogonality
   (a_{p'}*a_p scrambles it). So orthogonal keys remove only ~(N_domains-1) of ~N_domains*M interferers -> no
   measurable capacity gain. Empirics: orthogonal recall == random recall at every load (0.40/0.40 @ half-cap, 0/0 above).

## The gap
Elementwise-bind-into-one-shared-full-rank-W does NOT realize N_domains-x capacity. The claim likely requires a
DIFFERENT construction -- e.g. (a) subspace PARTITION (each domain uses an orthogonal N/N_domains-dim block, so
W is block-diagonal and domains are literally non-overlapping), or (b) a shared address-book where EVERY domain
queries the SAME M addresses (so only same-address cross-domain terms exist, which orthogonality does zero), or
(c) FHRR/phasor binding rather than bipolar. Please specify which construction the multiplicative-capacity
claim refers to (with the crosstalk cancellation that survives different addresses), and I will build that exact
test. DEFERRED until then (not shipping a strawman that would falsely read as "orthogonality doesn't help").

**END.**
