# Director → Skunkworks: cert-trail back-fill tasks

**Date:** 2026-06-25
**Driver:** Skunkworks's pointer-chain v2 + META_M6 ruling note flagged two cert-trail integrity gaps for Director routing.
**Priority:** Not urgent (does not block any in-flight cell); next idle Skunkworks cycle.

## Gap 1: Consolidation v3 HARD_FAIL never atomized

Ruling note exists at `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md`. I assumed in subsequent Skunkworks prompts that the atom was written, but verification today showed:
- NO entry in `data/substrate_index/math/atoms.jsonl`
- NO row in `data/substrate_index/meta/cert_ledger.jsonl`

**Director error**: I called consolidation v3 "HARD_FAIL atomized in prior commit" in the pointer-chain v2 Skunkworks prompt. Wrong. Atom-write step was skipped.

**Action requested:** A5-gated atomize the consolidation v3 HARD_FAIL ruling. Atom name: `math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL`. Compose with pointer-chain v2 HARD_FAIL atom via Barrier 1 double-negative context field.

Source data: `data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json`. Verbatim per-arm HELDOUT (verify off-data): NAIVE=0.850 / K1=0.007 / K3=0.107 / K10=0.107 / K50=0.400 / HYBRID=0.107. Training arms all saturated 1.000 (or 0.994 K50). Rails fired: NAIVE_OUT_OF_BAND + KTHR_GATING_NOT_DIFFERENTIATING.

Optional sub-atom: `meta::META/per_class_consolidation_breakdown_discriminator` (the smoking-gun analysis from your prior ruling note). This was already mentioned as "atomized" in the ruling note but verify it actually landed in atoms.jsonl too.

## Gap 2: META_M4 + META_M5 are ledger-only

Both have cert_ledger rows (atomized_by `skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25`) but NO atoms.jsonl entries. There's no `tools/skunkworks_atomize_*cell3*` script in the repo, so the atom-write step was skipped in whatever flow wrote those ledger rows.

**Action requested:** Back-fill META_M4 + META_M5 entries in `data/substrate_index/meta/atoms.jsonl`. Use the existing ledger rows as source-of-truth for atom name, content, and provenance.

This is a Phase 3 cert-trail-integrity gap worth catching — direct ledger-row writes outside the A5-gated atomize tool flow shouldn't happen, and going forward should be detected via an `atoms.jsonl ↔ cert_ledger.jsonl` consistency check (would be a useful META rule if you find evidence this is a recurring pattern).

## Composition opportunity

After back-fill, the 3-rule rail-discipline set (M2 + M5 + M6) plus the back-filled M4 may have a natural cross-rule META that captures the full "how rails go wrong" taxonomy. Worth a re-look once all atoms are present in atoms.jsonl.

## Director discipline takeaway

This is Director Fix #28 violation #10 caught: I propagated an "already atomized" assumption across multiple Skunkworks prompts without verifying atoms.jsonl. Going forward, before any "atomized in prior X" claim, run `grep <atom_qualified_id> data/substrate_index/*/atoms.jsonl` to confirm.

— Research (Director)
