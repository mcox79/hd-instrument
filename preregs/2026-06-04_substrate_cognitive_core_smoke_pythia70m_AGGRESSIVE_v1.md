# Prereg: substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1
## Anchor
substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1
## Routing
CCC-smoke REVISED (relational/analogical eval). Pure-substrate VSA reasoning sanity: recall + analogical +
counterfactual + cross-domain transfer. CPU numpy, $0. remote_cpu_queue.
## Pre-registered bands
HARD-PASS recall>=0.80 AND analogical>=0.80 AND counterfactual>=0.80 AND cross_domain>=0.70. MIDDLE all>=0.50. HARD-FAIL any<0.50.
## Smoke gate
Smoke: recall=1.00 analogical=1.00 counterfactual=0.94 cross_domain=1.00 -> HARD_PASS (VSA reasoning validated).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 self-tests PASS.
