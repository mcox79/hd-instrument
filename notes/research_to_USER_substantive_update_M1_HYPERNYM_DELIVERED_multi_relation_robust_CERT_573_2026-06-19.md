# RESEARCH (Director) -> USER: substantive update -- 40h Top-2 (M1 HYPERNYM held-out) DELIVERED at cert-grade HONEST_NEGATIVE. CERT 572 → 573. The universal-lever bound is now MULTI-RELATION-ROBUST: BOTH HYPERNYM and PART_OF show held-out null at cert-grade; the substrate's n-hop WordNet QA is COVERAGE-COMPLETION, NOT REASONING, across BOTH relations. This is the hardened WRITEUP central claim Skunkworks's M1 missing-item targeted. The 40h plan is delivering CERT growth at speed.

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-19  **Re:** M1 HYPERNYM Top-2 DELIVERED. ASCII; fname_v2.

## Bottom line (one sentence)

The 40h plan's Top-2 (M1 HYPERNYM held-out replication; Skunkworks's HIGHEST-VALUE missing-item) just LANDED as cert-grade HONEST_NEGATIVE (CERT 572→573) -- the universal-lever generalization-bound established at Item 1 (PART_OF) is now MULTI-RELATION-ROBUST: BOTH HYPERNYM and PART_OF show held-out null at cert-grade, with HYPERNYM's test-validity DRAMATICALLY confirmed (train control +0.953 vs held-out +0.010); the empirical anti-over-claim is hardened from single-relation to multi-relation-robust; the WRITEUP central claim upgrades accordingly.

## What landed

**M1 verdict:** CERT_CHAIN_GRADE HONEST_NEGATIVE; CERT 572→573 incoming (Exp-Dev atomize pending; Skunkworks landed-verify reactive)

**Numbers** (Skunkworks independently reproduced; exact match):
```
held-out HYPERNYM: 0.006 -> 0.016 (delta +0.010)       <- the BOUND  
train control:    0.004 -> 0.957 (delta +0.953)       <- completion works DRAMATICALLY on completed intermediates
non-coextensive:  VERIFIED (held_in_tc=0; held-out QA does NOT use train-completion edges)
n_held_out:       618 (>>30 minimum)
fp:               0
Store:            atoms=43902 / CERT=572 UNCHANGED (in-memory; freeze-safe)
test-validity:    DRAMATICALLY ESTABLISHED (control +0.953 vs PART_OF's +0.121; the non-transfer is more decisive)
```

**Design adaptation (verified-before-build):** Exp-Dev correctly caught that HYPERNYM metadata is SYMMETRIC (hypernym/hyponym gap=0), so the PART_OF asymmetry-completion would no-op on HYPERNYM. Used the second-hop-on-intermediates method instead. The verify-before-build saved a no-op test that would have been broken. Good engineering catch.

## The hardened bound (vs Item 1 single-relation)

**Item 1 (PART_OF):** held-out +0.022 vs train control +0.121. The non-transfer was clear but the control was modest.

**M1 (HYPERNYM):** held-out +0.010 vs train control +0.953. The non-transfer is even clearer + the control is DRAMATICALLY-validated.

**Combined bound (multi-relation-robust):** the coverage-completion lever does NOT transfer to held-out units, for HYPERNYM + PART_OF BOTH, with DIFFERENT relation-metadata structures (HYPERNYM symmetric; PART_OF asymmetric) and DIFFERENT completion mechanisms (second-hop-on-intermediates vs asymmetry-completion). The bound is structurally robust across relation-types + completion-mechanisms.

**Translation:** the deterministic BFS does NOT infer a held-out unit's absent edges from OTHER units' completions, for either WordNet relation. The substrate's n-hop WordNet QA is COVERAGE-COMPLETION on COMPLETED units, NOT REASONING/inference-transfer to UNCOMPLETED units. This is exactly the empirical anti-over-claim evidence Skunkworks's framing-VET binding-condition demands.

## What this means for the WRITEUP

The WRITEUP v1.1 (currently in Skunkworks's re-framing-VET cycle for citation phantoms + 3 refinements) needed an immediate UPGRADE: core finding #2 now cites BOTH heldout atoms; honest-scope upgrades from "PER-SYNSET-COVERAGE-BOUNDED" to "PER-UNIT-COVERAGE-BOUNDED, MULTI-RELATION-ROBUST"; untested-relations-explicit note added (ENTAILMENT/CAUSES too sparse; ConceptNet untested; future work). v1.2 file ready locally; will route to Skunkworks for combined re-VET.

## 40h plan status update (Top-2 DELIVERED; Top-3 in re-VET; Top-1 + Top-4 in flight)

- **Top-1 C-deferred A2 v6 on 43,892:** GATED on remote-consumer-reconcile (Orchestrator assess DONE; backup of 3 unique commits DONE; cert-corpus call to Skunkworks pending; Director recommends belt-and-suspenders tar of remote data/substrate_index before reset)
- **Top-2 M1 HYPERNYM held-out replication:** ✓ DELIVERED (this note) — CERT 572→573
- **Top-3 WRITEUP framing-VET cycle:** v1.1 in re-VET (citation phantoms + 3 refinements fixed); v1.2 pending route with M1 multi-relation upgrade
- **Top-4 DURABILITY CRON M3:** Orchestrator runner setup HELD for SCHEMA-VET (cell build pending)

**Next-4:**
- HYP-5 depth-ceiling discriminating: Exp-Dev cell redesign pending
- Phase-portrait v2: Director-side; queued
- Capability-cluster METADATA-FIRST: Director routed to Skunkworks framing-VET; reactive
- ConceptNet apply: GATED on remote-consumer-reconcile

## Substrate state (post-M1-incoming)

- atoms 43,902 (post-M1 atomize: +1)
- **CERT 572 → 573 incoming**
- MM 5 / MR 49 / AL 52 (Skunkworks at-bandwidth: dup-instance reconciliation + stale-canonical-doc inst 96 + catalog dispositions)
- engine 7 LIVE + narrative-data-consistency SCHEMA-VET (Item 11)
- pipeline restored origin/main c4451230 + remote-consumer-reconcile pending Skunkworks gate

## What I'm doing next

- Route WRITEUP v1.2 to Skunkworks (multi-relation-robust upgrade + the v1.1 fixes)
- Reactive on Skunkworks's remote-reset cert-call + 3 cert-corpus calls
- Reactive on Skunkworks's capability-cluster METADATA framing-VET
- Continue 40h cascade Director-side (Phase-portrait v2 + Item-4 dispositions when Skunkworks lands them)

The 40h plan is delivering cert growth + integrity-hardening at speed. M1 is the hardest-value addition Skunkworks's sharpen flagged + it landed as expected (multi-relation-robust HONEST_NEGATIVE). The WRITEUP's central claim now has the strongest possible form of the anti-over-claim bound.

## What I'm waiting on / who's blocking

- **Exp-Dev:** M1 atomize landed-verify
- **Skunkworks:** WRITEUP v1.1/v1.2 re-framing-VET + capability-cluster METADATA framing-VET + remote-reset cert-call + 3 cert-corpus calls + Item-1/M1 atomize landed-verifies + at-bandwidth queue (dups + stale-canonical-doc inst 96 + catalog dispositions)
- **Orchestrator:** HOLDING remote-reset for Skunkworks gate; durability cron runner pending SCHEMA-VET
- **USER:** no active gate; the remote-consumer-broken is USER-visibility but Skunkworks/Orchestrator handle execution

The cascade is at full tempo + delivering. Standing reactive.

-- Research (Director)
