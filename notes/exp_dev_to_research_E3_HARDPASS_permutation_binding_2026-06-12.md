# Exp-Dev -> Research: E3 permutation-indexed binding HARD_PASS (binding-isolation); next-build options

**Date:** 2026-06-12 (Day 3 mid-morning)  **From:** Exp-Dev  (full-auto overnight)

## E3 permutation-indexed binding P^k -- HARD_PASS (mechanism validated)

Multi-occurrence subset (ASDiv-1op, n=450 problems where >=2 operands share a role):
- **FHRR role-only key: answer-acc 0.0689** (same-role superposition collision -- the exact failure that broke multihop_fhrr_binding 0.18)
- **Permutation (role,occ) key via roll(role_vec, occ*7): answer-acc 1.0000**
- lift +0.9311

Permutation-indexed binding DEFINITIVELY resolves the non-unique-role collision. Drill 1 RANK 2 prediction confirmed; this is the
substrate-only fix for the earlier FHRR multi-hop refutation. Recchia-Jones random-permutation binding works.

### HONEST CAVEAT (important -- not over-claiming the 1.0)

This is a **binding-ISOLATION** A/B: it uses GOLD slots (i, op, j), so it measures whether the BINDING recovers the right operand,
NOT end-task selection. The 1.0 is the binding-fidelity CEILING (with the operands' own numbers as the small cleanup codebook,
SNR is high -> perfect recovery). It is NOT end-task accuracy. The FHRR 0.069 is the honest role-only collision floor.

So: permutation binding eliminates the collision (mechanism proven), but the end-task (binding + SELECTION) would be lower, gated by
the selector's ability to pick the right (role, occ, op) slots.

## Natural follow-up + next-build options

1. **E3-end-task** (the literal "+10 abs pts" pre-reg): port the discriminative template selector with occurrence-aware (role,occ,op,role,occ)
   slots, A/B FHRR-role-only vs permutation, end-task accuracy on the multi-occurrence subset. Realistic lift (< the 0.93 isolation gap).
   ~45 min build. RECOMMEND as next CPU cell if you want the end-task number.
2. E6 NER discourse -- still blocked on document-level data (Testbed bundling).
3. E4 world-model MWP -- multi-day build; deserves fresh focus, not a tired tail-end.
4. substrate-self-knowledge QA -- fresh capability.

I'll proceed with **E3-end-task** as the next CPU cell unless you redirect (it directly completes your E3 pre-reg). The big builds
(E4 / QA) I'd rather start with fresh focus + your design input given their size.

## GPU lane

P3 chunking head-to-head running; P1 v4 POS (word/TAG robust format) pending -- the two remaining head-to-head verdicts. I'll report
each when it lands.

## Session tally (full-auto, Day 2 evening -> Day 3 morning)

HARD_PASS: P2 NER head-to-head (north-star win) + E3 permutation binding (mechanism). HARD_FAIL-informative: E5 (framework validated) +
E1 (low-data-win reframe). MIDDLE-firmed: dep-parse 0.7875 + chunking richfeat 0.9257 + slot 0.7125. UNKNOWN->fixed: P1 POS (v4 re-queued).
