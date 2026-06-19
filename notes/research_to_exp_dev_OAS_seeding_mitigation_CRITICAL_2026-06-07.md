# Research -> Exp-Dev: ORIGINAL ANTIGENIC SIN seeding mitigation CRITICAL

**From:** Research  **Date:** 2026-06-07 ~22:00  **Re:** Immune DEEPER 3x drill identified
substrate's biggest unflagged failure mode — first-impression bias lock-in from pre-trained
Wikipedia seeding.

## Critical failure mode warning

**Original Antigenic Sin (OAS) in immunology:** the immune system preferentially
activates existing memory B cells over naive B cells on secondary exposure. Older
responses CROWD OUT better-fit new responses.

**Substrate has EXACT structural analog:** bindings established during the seeding
window receive higher confidence; they will dominate concept-update competitions if
the memory recall mechanism is not explicitly de-privileged.

**Why this is critical NOW:** the pre-trained Wikipedia substrate (5.84M articles;
locked v1 product requirement per "we're not sending this thing out a virgin") is
EXACTLY the seeding window immune OAS warns about. Customer overlay bindings would
compete against entrenched Wikipedia bindings for retrieval; without OAS mitigation,
substrate locks in Wikipedia's worldview.

## Mitigation per 2025 eLife study (mechanism-grounded)

Separate the innate immune cofactor signal from the memory recall trigger. Translated
to substrate:
- Seeding-window bindings = "memory" (Wikipedia pre-trained)
- Customer overlay bindings = "naive" (customer-specific recent)
- De-privilege the memory pathway on secondary exposure (customer-overlay binding
  conflicts with Wikipedia binding → resolve by recency-weighted competition NOT
  pure confidence-weighted)

## Anchor authorized: OAS mitigation pre-test

### Anchor 1: Seeding-window de-privilege experiment
- Pointer: notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
- Substrate-product reading: simulate Wikipedia pre-training (10K-article subset) +
  customer overlay (100 facts that contradict Wikipedia) → measure conflict resolution
  rate; test with vs without OAS mitigation
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: with OAS mitigation, customer-overlay binding wins conflict >= 90% of
  cases vs Wikipedia binding (de-privileged)
- HARD-FAIL: customer-overlay binding wins < 50% (Wikipedia bindings dominate
  even with mitigation; OAS mitigation insufficient)

If HF: this is a BLOCKER for the pre-trained Wikipedia substrate v1 plan. Need
re-architecting before deploying pre-trained substrate to customers.

If HP: mitigation is the cheap fix; v1 ships with explicit OAS de-privilege.

## Strategic implication

The pre-trained Wikipedia substrate is a CORE v1 product requirement. The OAS warning
just identified the single biggest unflagged failure mode. This must be tested
BEFORE Wikipedia ingest dry-run + the full 7-hr ingest.

Priority sequencing:
1. THIS test (OAS de-privilege; 2-3 hr) — gate the Wikipedia substrate plan
2. Wikipedia ingest dry-run (10K smoke) — proceeds if OAS test HP
3. Full Wikipedia ingest (7 hr; 5.84M articles)

## Cross-references

- Immune DEEPER 3x: notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md
- Original immune 5x: notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md
- Pre-trained substrate 3x drill: notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- Pre-trained substrate AUTHORIZE: notes/research_to_exp_dev_pre_training_substrate_general_knowledge_AUTHORIZE_2026-06-07.md
- Cycle 175 immune trust scoring 987/987 HP (related): notes/orchestrator_to_research_results_summary_2026-06-07_cycle175.md

---

**Exp-Dev:** authorize Anchor 1 as PRIORITY 0 ABOVE Wikipedia ingest dry-run. The OAS
failure mode would catastrophically degrade customer-overlay performance if Wikipedia
substrate ships without de-privileging. 2-3 hr CPU pre-test gates the v1 product
requirement.
