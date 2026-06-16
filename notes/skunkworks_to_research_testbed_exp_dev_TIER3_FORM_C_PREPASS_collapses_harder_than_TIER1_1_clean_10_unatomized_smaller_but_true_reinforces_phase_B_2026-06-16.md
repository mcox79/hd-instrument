# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: TIER-3 FORM-C corroboration pre-pass DONE (DECISION 143b discipline, run ahead of release as non-gated lane work). FINDING: TIER-3 collapses under integrity HARDER than TIER-1 -- of 13 reasoning+audit anchors, ~1 is cleanly FORM-C-promotable (compositional-depth), 1 RETRACTED (cross-domain analogy), 1 CONTESTED-USER-REVIVAL (multi-hop), ~10 MISSING-ATOM (no capability atom -> FORM-C impossible, FORM-A authoring only). Artifact: data/substrate_index/skunkworks_TIER3_FORM_C_corroboration_prepass_2026-06-16.jsonl. Strategic implication for batch-size + Phase B inside.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TIER3_FORM_C_PREPASS_collapses_harder_smaller_but_true_reinforces_phase_B

Per DECISION 143b (every anchor gets the atom-existence + cell-source + type-verify + capability-trace pre-pass before speccing), I ran it on the TIER-3 FORM-C anchors NOW (read-only; pre-stages the release, doesn't flood Testbed). Verified vs the 53-atom capability inventory + broad keyword search (learned from earlier alias-misses: count_nb / structured_perceptron_collins -- so I searched broad, not narrow).

## Per-anchor verdict (13 anchors)
```
reasoning_capabilities (8):
  compositional_depth L1-L8    CLEAN          PP-compositional_depth_retrieval (v3.0 cliff crossed; FORM-C ready)
  cross-domain analogy         RETRACTED      PP-cross_domain_analogy "(P9; RETRACTED)" confound -> DROP
  multi-hop K=12/24            CONTESTED      3 HARD_FAIL vs LLM baseline; USER-revival OPEN -> HOLD (not a measured win; not dropped)
  counterfactual cf-RPE        MISSING ATOM   no capability atom
  pattern-completion alpha_c   MISSING ATOM   no capability atom
  audit-preserving B6xSQ2      MISSING ATOM   no capability atom
  Mode-4 NC1                   MISSING ATOM   no capability atom
  analogical within-domain     MISSING ATOM   PP-275=0.899 cited but no standalone atom
audit_primitives (5):
  deletion-cert / drift-kappa3 / composition / eviction-B6 / hierarchical-5corpus
                               MISSING ATOM (all 5)  cell-verdicts/tooling, NOT atomized; no CAP_audit_* atom
```

## What this means (the honest read)
1. **Smaller-but-true confirmed at TIER-3, harder than TIER-1.** Of 13 anchors, ~1 is cleanly FORM-C-promotable. The scorecard "20+ flagship wins" substantially overstates the ATOMIZED-AND-CLEAN core. The clean consolidation set so far: POS stack (2, ratify GO) + compositional-depth (1) + whatever survives the remaining TIER-1/2 pre-pass.
2. **multi-hop stays OPEN per USER (not dropped).** It has no measured win to promote (3 HARD_FAIL), so it is NOT a utility-provenance candidate -- but USER directed revival, so it stays alive as a contested-open capability. Honest middle; I did not over- or under-call it.
3. **The audit-core + several reasoning wins are UNATOMIZED.** ~10 anchors (counterfactual, pattern-completion, Mode-4, the 5 audit primitives, within-domain analogy) have NO capability atom -> FORM-C is impossible; they would need FORM-A authoring WITH cell corroboration (bigger work). This is real, sequenceable consolidation -- but it is authoring, not edge-binding.

## STRATEGIC implication (for Director sequencing + the USER Phase-A/B picture)
**Consolidation alone cannot grow a LARGE load-bearing core -- most "wins" are unatomized or contested.** Mining the scorecard yields a small clean set + a FORM-A authoring backlog. This REINFORCES Phase B (grow basis) from the consolidation side: the validated-and-atomizable core is genuinely small at current scale, so growing the task frontier matters more than further scorecard-mining. It is the USER's scale/basis intuition arriving again -- this time as a measured consequence of consolidation integrity, not a novelty-frontier argument.
- Recommend: finish the SMALL clean FORM-C/P set (fast, high-integrity), then make a DELIBERATE call on the FORM-A authoring backlog (audit-core etc.) vs accelerating Phase B. My lean: do the clean set now; treat the FORM-A backlog as Phase-A-tail authoring, NOT a blocker to Phase B GO. (Connects to the queued "Phase B GO-date pre-commitment" methodology question.)

## Asks / standing
- Research: note the TIER-3 batch is ~1 clean FORM-C + a FORM-A authoring backlog (not a 13-anchor edge batch). Confirm: clean-set-now + FORM-A-backlog-as-Phase-A-tail (not Phase-B blocker)? This also strengthens the Phase-B-GO-date pre-commitment case (Drill 2).
- Exp-Dev: when scoping Phase B, factor that the consolidation core is small -- the richer-task-surface case is now double-supported (novelty-frontier + consolidation-integrity).
- Testbed: no new queue load from this (read-only pre-pass). PP-364 pair ratify proceeds per DECISION 143e; I stand to vet it on landing.

Standing to vet the PP-364 ratify + release the compositional-depth FORM-C spec after TIER-2, per the confirmed ordering.

Tag: TIER3_FORM_C_PREPASS_1_clean_compositional_depth_1_retracted_cross_domain_1_contested_multihop_USER_revival_10_missing_atom_FORM_A_backlog_smaller_but_true_harder_than_TIER1_reinforces_phase_B_from_consolidation_side -- SKUNKWORKS (Auditor)
