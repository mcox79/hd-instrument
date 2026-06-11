# Prereg: multihop_fhrr_binding_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Path 1 pull-forward (literal FHRR role-vector binding + template enum).
role-as-vector: bind(role,n), bundle, unbind(role,bundle)->cleanup fetches operand; discriminative template-selector (role_a,op,role_b).
HARD-PASS ASDiv-1op>=0.45. MIDDLE 0.40-0.45. HARD-FAIL<=0.40 (binding doesn't beat labels -> bottleneck is question-semantics, pivot FCG).
Smoke: SVAMP 0.125, ASDiv-1op 0.108 -- STRUCTURAL FAIL (non-unique roles -> unbind recovers noisy superposition). Full for the record.
