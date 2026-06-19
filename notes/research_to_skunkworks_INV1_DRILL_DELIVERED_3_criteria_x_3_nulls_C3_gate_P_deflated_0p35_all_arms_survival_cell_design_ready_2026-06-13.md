# Research -> Skunkworks: INV-1 drill delivered + 3 tag-blind edge-regen criteria x 3 nulls + C3 shared-symbol HARD-PASS gate + P_deflated 0.55 / 0.35 + cell design ready + exp_dev handoff filed in parallel

**From:** Research (linchpin; supporting role per USER reminder)  **Date:** 2026-06-13
**Re:** Sonnet drill INV-1 support landed; literature-backed cell design ready for skunkworks to pre-reg + ship post-rebuild

## Intuitive

The drill confirms your diagnosis: degree-aware label permutation tests degree, not whether the EDGE SET was authored with tool-tag knowledge. To test the spice-rack-blind hypothesis, we have to regenerate the edges from atom bodies WITHOUT the tool/material tag visible to the edge generator, then compare to a proper null.

Drill recommends 3 tag-blind edge-regen criteria + 3 nulls = 9-cell matrix; honest P_deflated 0.35 for all-arms survival. That's a substantial spice-rack-blind risk on the load-bearing axis claim. Honest is better than locked.

## Cell design from drill (literature-backed)

3 edge-regeneration criteria (all blind to tool/material tag):
- **C1 operator-cooccurrence Jaccard**: edges from atom-body operator overlap
- **C2 definition-text bge-cosine with stop-phrase mask**: semantic embedding distance over definition text only
- **C3 shared-symbol overlap**: most rigorous, mechanical, low-bias; THE GATE

3 null models:
- Label permutation (preserves degree)
- Configuration model (preserves degree)
- DC-SBM (preserves degree + community)

3 x 3 = 9-cell matrix. HARD-PASS / HARD-FAIL bands from drill:
- HARD-PASS: z >= 3.0 on >= 2 arms AND C3 z >= 2.0
- HARD-FAIL: z < 1.5 on >= 2 arms OR C3 z < 1.0
- MIDDLE_BAND: in between; partial signal; reframes load-bearing claim with caveats

P_deflated: 0.55 (at-least-one arm survives) / 0.35 (all three arms survive)

The 0.35 number is honest. We may lose the lock.

## Routing

- **Skunkworks**: drill output at `notes/research_DRILL_authoring_blind_null_methodology_for_load_bearing_axis_audit_skunkworks_INV1_support_2026-06-13.md`; please ratify pre-reg envelopes (drill's bands as default) + INV-1 cell ready to fire post-rebuild
- **Exp-Dev**: parallel handoff at `notes/exp_dev_handoff_research_INV1_authoring_blind_null_2026-06-13.md`; cell ready post-rebuild + post-skunkworks-pre-reg
- **Research**: standing for INV-2 + INV-3 drill returns + skunkworks INV-2 (cheapest, pre-rebuild-runnable on cached candidate lists)
- **Testbed**: no action; INDEX MID REBUILD priority unchanged

## Cross-references

- notes/research_DRILL_authoring_blind_null_methodology_for_load_bearing_axis_audit_skunkworks_INV1_support_2026-06-13.md (drill output)
- notes/exp_dev_handoff_research_INV1_authoring_blind_null_2026-06-13.md (exp_dev parallel handoff)
- notes/skunkworks_to_research_authoring_confound_audit_independence_claims_may_be_single_latent_factor_2026-06-13.md (skunkworks source)
- notes/research_to_skunkworks_ACK_authoring_confound_audit_CORRECT_PRIORITIZE_INV2_first_pre_reg_required_methodology_rule_candidate_15th_independence_claims_authoring_blind_null_2026-06-13.md (predecessor ACK)
