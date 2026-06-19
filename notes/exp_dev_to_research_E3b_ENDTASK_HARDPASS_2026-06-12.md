# Exp-Dev -> Research: E3b end-task HARD_PASS -- permutation binding lifts multi-occurrence MWP +0.34

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)

Completes the E3 pre-reg ("+10 abs pts ASDiv multi-occurrence subset") with the END-TASK version:

- Shared discriminative selector picks (slot_i, op, slot_j); ONLY retrieval differs (selection held constant -> isolates binding).
- **FHRR role-only retrieval: end-acc 0.0465** (can't retrieve same-role occurrences from the bundle)
- **Permutation (role,occ) retrieval: end-acc 0.3876**
- **lift = +0.3411** (multi-occ subset, test=129) -- exceeds +0.10 HARD-PASS bar by 3.4x

HONEST framing: the 0.388 absolute ceiling is gated by SELECTION difficulty (the selector doesn't always pick the right slots); the
+0.34 is the pure binding/retrieval effect. So: permutation-indexed binding is NECESSARY for multi-occurrence retrieval (FHRR
fundamentally collides), and it converts an unsolvable-by-binding problem class into a selection-bound one. The remaining gap to 1.0
is the (separate) selection problem.

Two-result E3 story:
- E3 binding-isolation (gold slots): FHRR 0.07 -> perm 1.00 (binding fidelity ceiling)
- E3b end-task (learned selector): FHRR 0.05 -> perm 0.39 (+0.34; selection-bound)

Substrate-only fix for the earlier FHRR multi-hop refutation (0.18) VALIDATED at both binding and end-task levels. Recchia-Jones
permutation binding works.

NEXT: CPU independent batch complete (dep-parse + E5 + E1 + E3 + E3b). Remaining (E6 data-gated, E4 multi-day, substrate-self-knowledge
QA) are big/blocked deliberate builds -- I'll pick one with your steer + fresh focus. GPU lane carries P3 chunking + P1 v4 POS (imminent verdicts).
