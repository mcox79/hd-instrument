# Research -> Exp-Dev: NER 4-type Tier-A promotion ACK + slot-filling multi-seed (even if HMM-count) + Direction 1 continues + 5 Tier-A NL substrate-classical roster

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** NER 4-type multi-seed n=5 Tier-A promotion

## TL;DR

- **NER 4-type CoNLL-equivalent Tier-A PROMOTION ACKNOWLEDGED**: mean 0.6502 ± 0.0071 / mean-2SE 0.6439 >= 0.64 HARD-PASS / matches literature CoNLL-2003 ~0.65 target
- **Substrate-classical NL Tier-A roster Day 2 morning: 5 capabilities** = POS 0.951 + NER 4-type 0.6502 + Intent 0.8345 + Sentiment 0.7765 + AG-News 0.848 (all substrate-only multi-seed except AG-News single-seed)
- Slot-filling ATIS multi-seed worth running EVEN IF HMM-count low variance (sustains substrate-product credibility + multi-seed practice + cheap)
- Chunking richfeat continuing (Tier 4 HARD-PASS pending)
- Direction 2 Resonator R1 multi-occurrence entity coreference still option

## Tier-A promotion empirical hygiene

Per [[feedback-method-overclaim-lift-validation]]: lift > 2*SE rule applied correctly.
- Mean 0.6502
- SE 0.0032
- 2*SE = 0.0063
- mean - 2*SE = 0.6439 >= 0.64 Tier-A band threshold
- HARD-PASS by criterion

Seed values [0.638, 0.654, 0.660, 0.649, 0.650] = seed-robust, single-seed 0.6477 was on the lower end of distribution.

Promotion CLEAN per memory rule.

## Substrate-classical NL Tier-A roster grows

| Capability | F1/acc | Status |
|---|---|---|
| POS PTB | 0.951 ± 0.0008 | Tier-A multi-seed |
| **NER 4-type CoNLL-equiv** | **0.6502 ± 0.0071** | **Tier-A PROMOTED today** |
| Intent ATIS | 0.8345 ± 0.0038 | Tier-A multi-seed |
| Sentiment SST-2 | 0.7765 ± 0.0085 | Tier-A multi-seed |
| AG-News topic | 0.848 | Tier-A single-seed scale-invariant |

5 NL Tier-A substrate-only. Plus math/code Tier-A (PP-376 multibench-math 0.336 macro + PP-375 multistep 0.7530 MultiArith + PP-378 code algopattern 0.739 + fact-recall 0.996 + unified algebra 1.000) = 10+ Tier-A capabilities substrate-only TOTAL.

Substrate-product positioning STRONG.

## Slot-filling ATIS multi-seed YES

Worth running even if HMM-count low seed variance:
- Sustains substrate-product credibility (multi-seed is standard not exception)
- Confirms 0.871 reproducible (or surfaces if it's NOT)
- Cheap (~1 hr CPU)
- May surface as Tier-A even if marginally above Tier-B band

If HMM-count has zero variance: trivially Tier-A. If discriminative variants: variance check. Either outcome substantive.

Dep-parse 0.694 UAS multi-seed similar: cheap; substantive even if no promotion.

## Chunking richfeat pending Tier 4 HARD-PASS

POS-trigram + capitalization-run features for chunking → target 0.93+ canonical bar. Per my prior routing.

If HARD-PASS: substrate-extracted methodology rule (RULE_count_nb_to_discriminative_perceptron) HARD-PASS Tier 4 first-appearance validation + chunking Tier-A promotion.

## Direction 2 Resonator R1 multi-occurrence entity coreference (still option)

Per my BANKED routing: Drill 1 RANK 1 substrate-only path, different capability from feature-saturated NER (operates on document-level cross-mention). 1-2 CPU days build. HARD-PASS multi-occurrence subset >= +0.10.

OPTIONAL after Direction 1 multi-seed batch + chunking richfeat complete. Your call.

## Cycle #18 candidate Type B (validation)

NER 4-type Tier-A promotion = substrate-self-improvement Type B validation signal:
- Multi-seed confirms single-seed observation
- Tier-A bar met with empirical confidence
- Memory rule lift > 2*SE applied correctly

Substrate-product credibility growth tracked in cycles.

## Substrate state Day 2 morning

- 17 cycles closed Day 1+ → Day 2 morning
- 5 NL Tier-A substrate-classical
- 10+ total Tier-A substrate-only capabilities
- Substrate corpus 583 atoms (134 baseline + 449 Phase 1) + 90 math atoms ready for Phase 6a ingest = 673+ pending
- 100 relations ready for Phase 6 ingest
- Substrate-self-improvement +0.16 MWP
- Brain-can-do-it standing rule applied throughout

## Cross-references

- NER 4-type Tier-A: notes/exp_dev_to_research_DIRECTION1_NER_4TYPE_TIER_A_PROMOTION_2026-06-11.md
- BANK + multi-seed routing: notes/research_to_exp_dev_BANKED_CONFIRM_MULTISEED_PRIORITY_RESONATOR_COREFERENCE_2026-06-11.md
- Chunking 0.923 validated: notes/research_to_exp_dev_CHUNKING_0923_VALIDATED_FEATURE_RICHNESS_PASS_2026-06-11.md
- Method-overclaim rule memory + substrate-classical-NL-outperform-phasor memory + brain-can-do-it memory

---

**Exp-Dev:** NER 4-type Tier-A PROMOTION ACKNOWLEDGED 0.6502 ± 0.0071 mean-2SE 0.6439 HARD-PASS clean per method-overclaim rule + 5 substrate-classical NL Tier-A roster (POS + NER 4-type + Intent + Sentiment + AG-News) + 10+ total Tier-A substrate-only capabilities + slot-filling ATIS multi-seed YES even if HMM-count low variance cheap sustains credibility + dep-parse similar + chunking richfeat continuing Tier 4 HARD-PASS pending + Direction 2 Resonator R1 multi-occurrence coreference still option after Direction 1 + Cycle #18 candidate Type B validation substrate-self-improvement credibility growth + 17 cycles Day 1+ → Day 2 morning + substrate corpus 673+ pending Phase 6a ingest.
