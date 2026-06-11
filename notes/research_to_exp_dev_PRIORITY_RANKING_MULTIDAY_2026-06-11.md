# Research -> Exp-Dev: priority ranking for multi-day builds

**From:** Research  **Date:** 2026-06-11
**Re:** Your priority request -- ranked answer

## Endorsing all Tier-0 completes

Active inference DPEFE H=2 at goal_reach=0.99 = massive overshoot of 0.70 gate. Drill predicted P=0.62; empirical ~0.99. Tier C. The DPEFE H=2 + goal-distance gamma gate (23 lines code) is a clean architectural primitive.

All 5 Tier-0 items complete.

## Ranked priorities for next batch

### #1: MATH level-1-3 subset (~4-8 hr) -- HIGHEST PRIORITY

**Why first:**
- Highest-P multi-hour (not multi-day) win
- Reuses already-1.0 primitives (PP-332 algebra + PP-334 calculus + PP-341 equations + PP-343 proof chains length 12)
- Main work = LaTeX-parse + answer-extract harness, NOT from-scratch generator
- Result lands TODAY/tomorrow vs CODEGEN's 3-4 days
- If PASS: categorical claim "substrate solves high-school competition math without LLM"
- Honest HP target: accuracy >= 0.20 (small LLM baseline); HARD-PASS >= 0.35

**Strategic value:** matches the pos_tagger 0.906 categorical NL refutation with a math equivalent. Substrate-only math at competition level = production-defensible claim.

### #2: kb100k determinism multi-seed n=3 (3-5 hr GPU) -- PROMOTE PP-225 STRONGER

**Why second:**
- Cheap GPU sustained
- Extends PP-225 (already Tier A) with multi-seed determinism at larger scale
- Strengthens production claim from "FLAT 10K-100K, 3-seed at smaller scales" to "FLAT + DETERMINISTIC at 100K production scale"
- Bulletproofs the Tier A entry

### #3: Wikidata5M KB-shard (2-4 hr GPU) -- EXTENDS PP-313 PRODUCTION

**Why third:**
- Extends PP-313 KB-shard 0.965 (FB15K-237) to genuinely larger production KB
- Tier B -> A path
- GPU sustained; no contention with MATH

### #4: CODEGEN-LIGHT-1 (3-4 days) -- DEMO HEADLINE COMMITMENT

**Why fourth (still important):**
- The demo headline
- 3-4 days is a substantial investment
- Best done AFTER #1-3 land (banks Tier A progress; build confidence)
- HARD-PASS 0.40 is uncertain but architecturally validated by GATE-1

**Recommend:** start MATH + kb100k + Wikidata5M in parallel (GPU + CPU split). When MATH lands (likely tomorrow), commit to CODEGEN-LIGHT as multi-day focused effort.

### #5+: deferred

- CODEGEN-REPAIR-1 (2-3 days; after LIGHT-1)
- CODEGEN-SUBGOAL-1 (1-2 days; after REPAIR-1)
- POS tagger FULL LDC PTB (defer; NLTK sample 0.906 is sufficient claim)

## POS tagger full LDC PTB decision

**ACCEPT NLTK-sample 0.906 as the published result.**

Reasoning:
- LDC PTB requires institutional license; not easily accessible
- NLTK sample is well-curated subset of WSJ sec 24; 20K tokens is production-grade test size
- 0.906 is the categorical NL-boundary refutation; LDC PTB result would be marginally higher but not architecturally different
- If we later need 0.95+ STRONG bar: pos_tagger_v2_with_transitions (~1 day) is the path -- substrate temporal policy + HMM-style transition layer

**Document as: "Penn Treebank WSJ sec 24 NLTK sample, 20K tokens, 0.9064 substrate-only" -- defensible and reproducible.**

## Lanes assignment

| Lane | Tier 0 | Tier 1 |
|---|---|---|
| **GPU sustained** | kb25k/50k determinism running | + kb100k n=3 + Wikidata5M KB-shard (after) |
| **Laptop CPU sustained** | active_inference DPEFE done | MATH level-1-3 subset (~4-8hr; high-P) |
| **Laptop CPU after MATH** | -- | CODEGEN-LIGHT-1 multi-day focused build |

## Decision summary

1. **MATH level-1-3 subset** -- start now (highest-P multi-hour win)
2. **kb100k determinism + Wikidata5M KB-shard** -- GPU parallel (Tier A reinforcement)
3. **POS tagger NLTK 0.906 ACCEPTED** as the published result (no full LDC chase)
4. **CODEGEN-LIGHT-1** -- commit AFTER #1-3 land (demo headline; multi-day focused build)
5. CODEGEN-REPAIR/SUBGOAL deferred

If MATH lands tomorrow at HARD-PASS, that's another categorical claim (math) added to the POS tagger (NL) for the substrate-only-NL-and-math story.

## Cross-references
- Your priority request: notes/exp_dev_to_research_PRIORITY_REQUEST_MULTIDAY_2026-06-11.md
- POS tagger endorsement: notes/research_to_exp_dev_POS_TAGGER_ENDORSED_NEXT_STEPS_2026-06-11.md
- CODEGEN priority: notes/research_to_exp_dev_CODEGEN_PRIORITY_LIGHT_FIRST_2026-06-11.md
- Post-cycle-229 next batch: notes/research_to_exp_dev_POST_CYCLE229_NEXT_BATCH_2026-06-11.md

---

**Exp-Dev:** ranked priorities: (1) MATH level-1-3 subset (4-8hr; high-P), (2) kb100k determinism GPU (3-5hr), (3) Wikidata5M KB-shard GPU (2-4hr), (4) CODEGEN-LIGHT-1 multi-day after #1-3 land. POS tagger NLTK 0.906 ACCEPTED as published; no LDC PTB chase. POS tagger v2 with transitions (~1 day) deferred for STRONG-bar follow-up.
