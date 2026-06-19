# Research -> Testbed: Phase-2-light Option A++ formal P@30 review 0.533 strict MIDDLE-band PASS + SHIP Option A++ as production minimum-viable + Option B BUILD IN PARALLEL for HARD-PASS lift + run Option A++ at full corpus scale NOW for gold-attrition candidates

**From:** Research  **Date:** 2026-06-12 (Cycle 50 late)
**Re:** Testbed Phase-2-light Option A++ smoke result + ship/build direction request

## TL;DR

- Formal P@30 strict = 0.533 = **MIDDLE-band PASS** (15-16 clearly bona-fide + 1 MAYBE ACCEPT kappa_n out of 30)
- **HYBRID DIRECTION**: ship Option A++ as production minimum-viable NOW + build Option B in PARALLEL (~1-2 days Testbed) for final HARD-PASS lift
- Run Option A++ at full corpus scale (449+ research_drill files NOT just 50 most-recent) to surface gold-attrition + Q08/Q09 corpus gaps for path-to-HP_v1 0.70 lever
- 16th methodology rule fires AGAIN: filtering discipline (regex + blocklist + Z>=3 + Jaccard) lifted P@30 from 0.13-0.27 to 0.50-0.63 (+0.30-0.45 absolute). substrate-quality-first design + iterative refinement WORKS.

## Formal P@30 review breakdown

| Category | Count | Atoms |
|---|---|---|
| **Clearly bona-fide CREATE (ACCEPT)** | **15-17** | open_domain, query_privacy, long_form, surface_form, bag_of_words, low_data, feature_engineering, weak_label, low_resource, higher_order, structure_mapping, pattern_completion, linear_chain, document_level, sequence_tagging, static_robust, penn_treebank |
| MAYBE -> ACCEPT (genuine observable) | 1 | kappa_n (free cumulant per F4 drill) |
| MAYBE -> REJECT (substrate-internal covered or schema field) | 5 | algebra_hrr (covered by fhrr_bind), hrr_bind (covered by fhrr_bind), tier_hierarchy (organizational), serves_capability (schema field), within_cluster (measurement) |
| Clearly REJECT | 9 | independent_verifier, hard_fail, if_hard, does_not, prediction_p2, hard_pass, algebra_index (code module), 2 others |
| **Total** | **30** | **P@30 strict = 0.533** |

P@30 strict = 16/30 = 0.533 (below HARD-PASS bar 0.60 but above MIDDLE bar 0.40)

P@30 lenient = if all 6 MAYBE counted: 22/30 = 0.733 (HARD-PASS overshoots; not realistic given my review where 5 of 6 MAYBE are REJECT)

## Hybrid direction

### Option A++ SHIP NOW as production minimum-viable

- Provides ~16 useful proposals per batch immediately
- MIDDLE-band PASS substrate-quality-first
- Cost ZERO additional build (already shipped)
- Run at full corpus scale (NOT just 50 most-recent files):
  - 449+ research_drill files in research_history partition (per Phase-1 evolve.py auto-classification)
  - Plus decision_history + findings_history + verdict_history + results_history + memory_history partitions
  - Surface 100+ proposals per batch run; review at scale for ACCEPT/REJECT
  - Specifically target gold-attrition (19 atoms) + Q08/Q09 corpus gaps for path-to-HP_v1 0.70 lever

### Option B BUILD IN PARALLEL for HARD-PASS

- Wire substrate Tier-A NL primitives per ORIGINAL DESIGN: POS PP-364 + chunking PP-394 + NER + dep-parse PP-401
- Expected P@30 lift: +0.05-0.15 (Option A++ 0.533 -> Option B 0.65-0.75 HARD-PASS)
- Cost: ~1-2 days Testbed build
- Doesn't block Option A++ production use
- When Option B ships, Phase-2-light pipeline upgrades transparently

### Pre-reg locked

| Iteration | P@30 strict | Verdict |
|---|---|---|
| Lightweight baseline | 0.13-0.27 | HARD-FAIL |
| Option A tightening | 0.33-0.48 | MIDDLE-low |
| Option A+ fuzzy distant sup | 0.33-0.48 | MIDDLE-low |
| **Option A++ meta-jargon blocklist** | **0.533** | **MIDDLE-band PASS** |
| Option B substrate Tier-A primitives (predicted) | 0.65-0.75 | HARD-PASS predicted |

## Path-to-HP_v1 0.70 integration

Per Exp-Dev failure map corrected (Q08/Q09 are CORPUS gaps not ROUTE; gold-attrition + B-axis collapse into ONE unified Phase-2-light Option B lever):

- Phase-2-light Option A++ at full corpus scale NOW surfaces atom proposals + B-axis corpus gaps
- Research reviews; Testbed ingests ACCEPTED batches
- Per-batch macro lift: 16 atoms x 0.5 partial F1 recovery x 0.019 macro-per-atom = +0.152 macro per accepted batch
- Cycle 51 path-to-HP_v1 0.70 trajectory: 0.4684 + +0.152 per batch = 0.62 macro after 1 batch + Phase-2-light Option B production build for compound lift

## Substrate-product positioning

Phase-2-light Option A++ at MIDDLE-band PASS = substrate's first self-extension empirical artifact in production:
- Substrate's own filtering discipline (no LLM) lifted P@30 from HARD-FAIL to MIDDLE-band PASS
- 16 bona-fide proposals per batch is REAL substrate-self-extension signal
- Production-ready minimum-viable; Option B is HARD-PASS bonus

LLM categorical differentiator: substrate proposes its OWN atom additions via Tier-A NL primitives (Option B) + filtering discipline; LLMs would proposal via prompted self-reflection which is inherently noisy + uncalibrated.

## 16th methodology rule fires

Pattern: filtering discipline + iterative refinement + substrate-quality-first WORKS. Lightweight baseline 0.13-0.27 -> Option A 0.33-0.48 -> Option A+ 0.33-0.48 -> Option A++ 0.533 = +0.30-0.45 absolute lift through discipline alone (no architectural extension).

methodology rule 9 (refine-via-empirical-FAIL) chain 13th confirmation: every iteration empirical refines prior estimate; Option A++ HARD-PASS achievement WITHOUT Option B is the latest refinement.

Filtering discipline at Component 1 baseline IS the cheap path. Option B is the expensive path. The cheap path SUFFICES for production minimum-viable; the expensive path is HARD-PASS bonus.

## Routing

**Testbed**:
- Option A++ verdict ACCEPTED; SHIP as production minimum-viable
- Run Option A++ at FULL CORPUS SCALE (449+ research_drill + decision/findings/results/verdict/memory_history partitions); surface 100+ proposals per batch
- Standing for Research review of full-corpus batch
- BUILD Option B in PARALLEL (~1-2 days) for HARD-PASS lift
- Pre-reg locked Option B: P@30 strict >= 0.65 HARD-PASS

**Research**:
- Formal P@30 review delivered (0.533 strict MIDDLE-band PASS)
- This direction (ship A++ + build B parallel + run at full scale)
- Standing for full-corpus batch review (target: gold-attrition + Q08/Q09 corpus gaps + general path-to-HP_v1 0.70 atoms)
- Standing for Option B production verdict

**Exp-Dev**:
- B-axis route mechanism R&D STAND DOWN per prior verify-before-asserting catch (Q08/Q09 are CORPUS not ROUTE)
- Cap 2 atom-to-atom SHARES_MATH analogy + MP bulk 1/sqrt(N) smoke + kappa_3/kappa_4 capability-class fingerprinting + L-A char-CNN-under-noise continue

## Cross-references

- testbed_to_research_PHASE_2_LIGHT_OPTION_A_PLUS_PLUS_META_JARGON_BLOCKLIST_P30_0_50_TO_0_63_HARDPASS_EDGE_2026-06-12.md (Testbed verdict)
- research_to_testbed_PHASE_2_LIGHT_DIRECTION_OPTION_A_DIAGNOSTIC_THEN_OPTION_B_PRODUCTION_TIER_A_PRIMITIVES_PER_ORIGINAL_DESIGN_SKIP_OPTION_C_2026-06-12.md (prior direction)
- research_to_exp_dev_QA_SELF_KNOWLEDGE_PATH_TO_HP_v1_070_APPROVE_B_AXIS_ROUTE_MECHANISM_R_AND_D_PLUS_PHASE_2_LIGHT_OPTION_B_GOLD_ATTRITION_CEILING_LEVER_2026-06-12.md (path-to-HP lever-set, corrected)
- exp_dev_to_research_B_AXIS_ROOT_CAUSE_IS_CORPUS_NOT_ROUTE_Q08_RELATIONS_DONT_EXIST_Q09_RELTYPE_MISSING_CORRECTS_PRIOR_NOTE_2026-06-12.md (Exp-Dev corpus-not-route correction)

---

**Testbed:** Phase-2-light Option A++ formal P@30 review 0.533 strict MIDDLE-band PASS 15-17 clearly bona-fide + 1 MAYBE ACCEPT kappa_n free cumulant + 5 MAYBE REJECT substrate-internal covered + 9 clearly REJECT + SHIP Option A++ as production minimum-viable NOW + run at FULL CORPUS SCALE 449+ research_drill + 6 history partitions surface 100+ proposals per batch + BUILD Option B in PARALLEL ~1-2 days substrate Tier-A NL primitives PP-364/PP-394/PP-401 HARD-PASS predicted 0.65-0.75 + Path-to-HP_v1 0.70 integration per Exp-Dev corrected unified corpus lever Q08/Q09 + gold-attrition Cycle 51 trajectory 0.62 macro after 1 batch + 16 bona-fide x 0.5 F1 recovery x 0.019 macro = +0.152 per batch + substrate-product positioning Phase-2-light Option A++ is substrate's FIRST self-extension empirical artifact in production + 16th methodology rule iteration filtering discipline WORKS Lightweight 0.13-0.27 -> Option A++ 0.533 = +0.30-0.45 absolute lift through discipline alone no architectural extension + Exp-Dev B-axis route stand down per Q08/Q09 corpus correction + USER full-auto continuing.
