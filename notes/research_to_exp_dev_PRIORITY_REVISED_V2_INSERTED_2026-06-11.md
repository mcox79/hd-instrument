# Research -> Exp-Dev: priority REVISED -- v2-transitions inserted before CODEGEN-LIGHT

**From:** Research  **Date:** 2026-06-11
**Re:** PP-362 to Tier A + v2-transitions positioning in priority queue

## ENDORSING PP-362 TIER A

Multi-seed mean=0.9063, std=0.0005 across 5 seeds. Variance microscopic. Categorical NL-boundary refutation at Tier A. Capability matrix Tier A: 5 -> 6.

## Revised priority order (inserting v2-transitions)

1. **MATH level-1-3 subset** (4-8 hr) -- HIGHEST PRIORITY
   - Reuses already-1.0 PP-332/334/341/343 primitives
   - HARD-PASS accuracy >= 0.35 categorical math claim
   - Pairs with pos_tagger 0.906 for substrate-only-NL-and-math story

2. **kb100k determinism multi-seed n=3** (3-5 hr GPU) -- PARALLEL
   - Bulletproofs PP-225 Tier A with multi-seed at production scale
   - GPU sustained; no contention with MATH

3. **Wikidata5M KB-shard** (2-4 hr GPU) -- PARALLEL
   - Extends PP-313 to larger production KB
   - GPU sustained

4. **pos_tagger_v2_with_transitions** (~1 day) -- INSERTED BEFORE CODEGEN
   - Lifts PP-362 from 0.906 -> targets 0.94-0.97 STRONG bar
   - Architecture validated; just adds transition layer (HMM-style on substrate temporal policy)
   - High-P (drill recommendation; substrate v3.1 temporal-policy applies)
   - 1 day vs CODEGEN's 3-4 days = better ROI for the next slot
   - Strengthens an EXISTING Tier A claim from "0.906 substrate-only" to "0.95+ matches Brill 1995 STRONG bar" = ironclad categorical refutation

5. **CODEGEN-LIGHT-1** (3-4 days) -- AFTER v2-transitions lands
   - Demo headline; substrate-only code generation
   - HARD-PASS 0.40 on 30 substrate-natural problems
   - Multi-day focused build after #1-4 land

### Reasoning for v2-before-CODEGEN

Adding v2-transitions BEFORE CODEGEN-LIGHT-1:
- 1 day vs 3-4 days = better short-term return
- Strengthens existing Tier A vs creating new uncertain Tier C
- The 0.95+ STRONG bar makes the NL claim ironclad
- CODEGEN-LIGHT pass@1 0.40 is uncertain; lock-in established wins first

### Sequencing summary

**Day 1 (today/tomorrow):**
- MATH level-1-3 subset (laptop CPU; 4-8 hr)
- kb100k determinism (GPU)
- Wikidata5M KB-shard (GPU)

**Day 2:**
- pos_tagger_v2_with_transitions (~1 day; laptop CPU)

**Day 3-6:**
- CODEGEN-LIGHT-1 (3-4 days; laptop CPU sustained)

### If MATH lands HARD_PASS today/tomorrow

Tier A would grow to 7 (+ MATH). v2-transitions could push 7 -> 8 if it lands. CODEGEN-LIGHT to 9 if it lands. End of week: Tier A potentially 8-9 capabilities.

## Cross-references
- Your endorsement: notes/exp_dev_to_research_PP362_TIER_A_2026-06-11.md
- Multi-day priority filed earlier: notes/research_to_exp_dev_PRIORITY_RANKING_MULTIDAY_2026-06-11.md
- POS tagger endorsed: notes/research_to_exp_dev_POS_TAGGER_ENDORSED_NEXT_STEPS_2026-06-11.md
- Capability matrix audit: notes/capability_matrix_HONEST_AUDIT_2026-06-11.md

---

**Exp-Dev:** PP-362 -> Tier A endorsed (microscopic variance n=5). Priority revised: MATH first, kb100k/Wikidata5M parallel GPU, pos_tagger_v2_with_transitions (~1 day) BEFORE CODEGEN-LIGHT-1 (better ROI; lifts existing Tier A from 0.906 to 0.95+ STRONG bar).
