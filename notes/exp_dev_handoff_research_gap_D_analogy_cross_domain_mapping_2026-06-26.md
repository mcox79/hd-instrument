# exp_dev hand-off -- research: gap_D_analogy_cross_domain_mapping

**Filed-by:** research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Research note at notes/research_gap_D_analogy_cross_domain_mapping_2026-06-26.md drills three substrate-feasible mechanism families for cross-domain analogy, with pre-registered HARD-PASS / HARD-FAIL bands. USER addendum surfaces cortex-composition (TWO_TIER + BCM + Modern Hopfield) as the natural mechanism aligned with brain (parietal-mPFC abstract relational map).

**Pause state:** Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching any anchors. If paused, hold this file for next refill cycle.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the anchors; this file names the mechanisms and provides substrate-product readings only. Do NOT inline experiment code or exact parameter values here.

---

## Anchor candidates (rank-ordered)

### ANCHOR-1: cross_domain_analogy_3arm_discriminator_v1 (RANK 1 -- cheapest decisive cell)
**Substrate-product reading:** A single discriminator cell with three relational arms + one baseline arm, run on a 200-analogy cross-domain test set spanning 4 domain pairs and 4 relation primitives. Arms:
- ARM_DIRECT_HRR_UNBIND: classical Plate-style unbind(B, A) -> R; bind(C, R) -> D; cleanup
- ARM_PARTITION_ROUTE: classify (A,B) into ConceptNet primitive partition; within-partition retrieval for D given C
- ARM_CORTEX_HOPFIELD: cortex schema retrieval via Modern Hopfield over W_schema (gated on TWO_TIER + BCM + Modern Hopfield primitives landing)
- ARM_BASELINE_COSINE: chance-level methodology rail

Discriminator is the margin between arms, not absolute accuracy. The +0.10 separation requirement is what distinguishes mechanism families from baseline.

**Tier hint:** CPU-viable for ARM_DIRECT_HRR_UNBIND + ARM_PARTITION_ROUTE + ARM_BASELINE_COSINE. ARM_CORTEX_HOPFIELD depends on cortex primitives landing (TWO_TIER + BCM + Modern Hopfield each at HARD_PASS or PARTIAL); when those land, this arm fires.

**Why now:** USER deep-drill on Gap D. Cortex layer dispatched today. Within-domain analogy already chain-grade (PP-115 K10=0.953); cross-domain is the open capability. This cell resurrects the 2026-06-10 ANCHOR-3 ConceptNet partition plan AND adds the new cortex-composition mechanism made possible by today's cortical infrastructure.

**Pre-reg bands (from research note, copied here for exp_dev convenience):**
- HARD_PASS (any single relational arm): top-1 >= 0.45 AND >= ARM_BASELINE_COSINE + 0.20 AND >= other relational arms + 0.10 (discriminator)
- HARD_PASS (alt): ARM_DIRECT_HRR_UNBIND top-1 >= 0.45 standalone (would refute STRETCH4-2 ceiling -- VERY informative)
- MIDDLE_BAND [0.30, 0.45]: partial mechanism; queue N_DIM scale-up
- HARD_FAIL: all relational arms within 0.05 of baseline, OR all top-1 < 0.30 -> encoder pivot needed
- HARD_FAIL (cortex-specific): ARM_CORTEX_HOPFIELD top-1 < ARM_DIRECT_HRR_UNBIND + 0.03 in a regime where cortex primitives are individually healthy -> cortex composition doesn't add cross-domain value

### ANCHOR-2: concept_net_partition_classifier_v1 (RANK 2 -- gates ARM_PARTITION_ROUTE quality)
**Substrate-product reading:** A relation-type classifier that maps an entity pair (A, B) to its ConceptNet primitive (causes / part-of / instance-of / used-for / ...). Trained via either (a) LLM-annotation of substrate's existing relations, offline, ~$10-50 LLM cost; or (b) substrate-internal via relation-embedding cosine to ConceptNet's 34 reference relation vectors.

This is a substrate-internal capability cell. It is independently cert-eligible (relation classification is a chain-grade primitive on its own). It's also the gate on ARM_PARTITION_ROUTE quality: if the classifier accuracy is < 0.70, the partition routing degrades.

**Tier hint:** CPU-viable. LLM cost for option (a) is modest ($10-50 one-shot). Option (b) is pure substrate cosine and costs nothing.

**Why now:** Required input for ANCHOR-1's ARM_PARTITION_ROUTE arm. Can be developed in parallel with ANCHOR-1.

**Pre-reg bands:**
- HARD_PASS: classifier accuracy >= 0.75 on held-out (A, B, r_label) test set
- MIDDLE_BAND: 0.50-0.75 (acceptable, but partition routing will inherit error)
- HARD_FAIL: < 0.50 (random for 34-class problem; routing degrades to chance)

### ANCHOR-3: cortex_schema_basin_audit_v1 (RANK 3 -- diagnostic for ARM_CORTEX_HOPFIELD readiness)
**Substrate-product reading:** Audit cell that runs over W_schema (output of TWO_TIER + BCM slow-learning pass) and counts (a) number of distinct Modern-Hopfield-retrievable schema basins; (b) per-basin retrieval cosine; (c) W_schema density (non-zero fraction); (d) overlap with ConceptNet 34 primitives.

**Tier hint:** CPU-viable. ~1 CPU-hr to compute basin count + per-basin retrieval over W_schema at N=16384.

**Why now:** Diagnoses whether ARM_CORTEX_HOPFIELD is READY to dispatch. If N_basins << 34 (cortex under-trained), need more BCM slow-learning passes before firing ARM_CORTEX_HOPFIELD; if N_basins >> 100 (over-specialized), need to sharpen via NREM replay; if 20-60 basins with cosine > 0.7, ready for ARM_CORTEX_HOPFIELD.

**Pre-reg bands:**
- HARD_PASS (ready for ARM_CORTEX_HOPFIELD): 20 <= N_basins <= 100 AND mean per-basin retrieval cosine >= 0.65 AND W_schema density >= 0.5
- MIDDLE_BAND (cortex under-trained): N_basins < 20 OR mean cosine 0.4-0.65; queue additional slow-learning
- HARD_FAIL (cortex layer broken): density < 0.3 OR mean cosine < 0.4 -> investigate TWO_TIER + BCM mechanism

### ANCHOR-4: drama_eliasmith_thagard_replication_v1 (RANK 4 -- academic precedent anchor)
**Substrate-product reading:** Replicate Eliasmith-Thagard 2001 DRAMA on substrate at N=16384. DRAMA used HRR + structural-mapping for analogical mapping on benchmarks from Gentner. This is a substrate-product precedent cell: shows that the 2001 academic result holds at substrate's modern scale.

**Tier hint:** CPU-viable. ~2-4 CPU-hr. DRAMA implementation is well-documented in the original paper.

**Why now:** Substrate-product narrative anchor. DRAMA is the canonical published precedent that HRR substrate can do analogy. Replicating it on substrate's chain-grade infrastructure (vs DRAMA's small-scale 2001 implementation) shows substrate's modern advance over the academic baseline.

**Pre-reg bands:**
- HARD_PASS: substrate DRAMA achieves >= DRAMA 2001 reported accuracy on each benchmark (Gentner's analogy test set)
- MIDDLE_BAND: matches DRAMA within 10pp
- HARD_FAIL: substrate DRAMA below DRAMA 2001 -- indicates substrate implementation has a bug vs 2001 reference

---

## Context pointers

- Research note (full mechanism analysis): notes/research_gap_D_analogy_cross_domain_mapping_2026-06-26.md
- Prior cross-domain analogy negative drill (substantive prior art): notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md
- Within-domain analogy chain-grade evidence: PP-115 / PP-165 / comp24 (substrate_capability_map.md)
- Cortex primitives in flight TODAY:
  - TWO_TIER: notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md
  - BCM slow-learning: notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md (Gap 3)
  - Modern Hopfield revival: notes/research_modern_hopfield_revival_slow_built_basins_2026-06-26.md (today)
  - Cortex-as-router brain mechanism: notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md (Gap 1, today)
- DRAMA reference: Eliasmith-Thagard 2001, Cognitive Science 25:245-286. Open access at http://watarts.uwaterloo.ca/~celiasmi/Papers/ce.pt.2001.drama.cogsci.html
- ConceptNet 34 primitives: substrate already has ConceptNet ingested (458K facts per testbed_post_compaction_brief_2026-06-09_overnight_chain.md)
- Cap map cross-domain row state: DROPPED 2026-06-10 per STRETCH4-2 retraction. To be resurrected ONLY if ANCHOR-1 HARD_PASS

---

## Contract section

ANCHOR-1 is the GATE. It encompasses all three mechanism families in a single discriminator cell. Its results determine downstream:
- If ARM_CORTEX_HOPFIELD HARD_PASS: cortex-composed cross-domain analogy is the substrate-product capability. Cap_map cross-domain row resurrected at P-band 0.55-0.70. Substrate-product narrative anchors on cortex + algebraic transfer.
- If ARM_PARTITION_ROUTE HARD_PASS: ConceptNet-anchored structural alignment is the capability. Cap_map row at 0.45-0.60 with annotation "ConceptNet-anchored, not yet cortex-native".
- If ARM_DIRECT_HRR_UNBIND HARD_PASS only: substrate algebra alone suffices. Cap_map row at MIDDLE_BAND, substrate-product positioning is "within-domain + algebraic-cross-domain on universal relations" (narrower than full cross-domain).
- If all HARD_FAIL: cap_map row stays DROPPED. Pivot to encoder approaches (Path C v2).

Expected total CPU time for ANCHOR-1: 3-6 CPU-hr (without ARM_CORTEX_HOPFIELD); +2-4 CPU-hr when cortex arm fires.
Expected total CPU time for ANCHOR-2 (option b, substrate-internal): 1-2 CPU-hr.
Expected total CPU time for ANCHOR-3: 1 CPU-hr.
Expected total CPU time for ANCHOR-4: 2-4 CPU-hr.

ANCHOR-2 (partition classifier) should be developed in parallel with ANCHOR-1 -- it's an input to ARM_PARTITION_ROUTE. ANCHOR-3 (cortex audit) gates the ARM_CORTEX_HOPFIELD arm of ANCHOR-1 -- run it when cortex primitives land, before firing the cortex arm.

ANCHOR-4 (DRAMA replication) is the substrate-product narrative anchor but NOT on the critical path for capability. Lower priority.

---

## Autonomy declaration

exp_dev has full autonomy to:
- Decide the exact 200-analogy test set construction methodology (4 domain pairs x 4 relation primitives x 50 analogies; sources can include FB15K-237 + ConceptNet + HotpotQA + a small custom set for domain coverage)
- Choose between substrate-internal vs LLM-annotated relation classifier for ANCHOR-2
- Sequence ANCHOR-1 (without cortex arm) -> ANCHOR-3 (cortex audit) -> ANCHOR-1 (cortex arm fires) when cortex primitives land
- Pre-register exact bands before dispatch per standard protocol; the bands in this file are the floor; exp_dev may tighten them
- Choose ARM_CORTEX_HOPFIELD's exact slow-learning corpus (within-domain analogy training pairs from FB15K-237 + ConceptNet are the natural choice; HotpotQA adds multi-hop diversity)

exp_dev should NOT:
- Dispatch ARM_CORTEX_HOPFIELD before cortex primitives (TWO_TIER + BCM + Modern Hopfield) are each individually HARD_PASS or PARTIAL
- Commit cross-domain analogy product claims until ANCHOR-1 HARD_PASS is verified per Fix #28 per-arm metrics
- Assume the within-domain K10=0.953 result is at risk (it is NOT; separate capability, already chain-grade)
- Skip the discriminator margin check: HARD_PASS requires +0.10 over other relational arms AND +0.20 over baseline, NOT just absolute top-1 >= 0.45 (per [[feedback-experiment-bias-master-checklist]] BIAS-13/14/15 and Fix #28)
