# Prereg: e3b_permutation_binding_endtask_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** completes Research E3 pre-reg (end-task version of binding-isolation E3).
Shared discriminative selector picks (slot_i, op, slot_j) from per-slot + question features; ONLY retrieval differs: FHRR role-only
(collides on same-role occurrences) vs permutation (role,occ). Selection held constant -> isolates binding effect on answer accuracy.
ASDiv-1op multi-occurrence subset, 70/30 split. HARD-PASS perm-FHRR >= +0.10. MIDDLE +0.05-0.10. HARD-FAIL <+0.05.
