# Prereg: e3_permutation_binding_multiocc_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research UNROUTED inventory E3 (Drill 1 RANK 2 non-unique role binding).
Earlier FHRR multi-hop binding failed (0.18) because same-role numbers collide in superposition. Permutation-indexed binding:
bind k-th occurrence of a role with roll(role_vec, k) -> distinct keys, clean recovery. MECHANISM-ISOLATION A/B (gold slots, so it
tests BINDING not selection): ASDiv multi-occurrence subset, recover operands FHRR(role-only) vs permutation(role,occ), gold op, answer acc.
CAVEAT: gold-slot isolation -> measures binding fidelity ceiling, NOT end-task (selection separate).
HARD-PASS perm-FHRR >= +0.10. MIDDLE +0.05-0.10. HARD-FAIL <+0.05. UNKNOWN if subset empty.
