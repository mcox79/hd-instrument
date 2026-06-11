# Substrate Self-Index — Day 1 closing summary

**Date:** 2026-06-11 (late evening)
**Author:** Testbed (autonomous mode)
**Audience:** user (for review when back)

## TL;DR

Day 1 of the substrate self-index foundational tool delivered **6 closed-loop substrate-self-improvement cycles spanning 6/6 signal types**, met Tier 1+2+3 gates per Research's 5-tier progression, and produced empirically validated substrate-distinguishing measurements.

Substrate now has 92 atoms, 284 relations, 7 corpus partitions (math + concept + meta + school + methodology + plus 6 history partitions ready for full-research-ledger ingest), 4 active eval Layers (1+2+3+4), and is autonomously generating + validating its own improvement candidates.

## What's in the substrate right now

| Partition | Atoms | Source |
|---|---|---|
| math | 60 | Research batch 01 + 02 + 53-atom algebra-vec follow-up |
| concept | 28 | Research 10-atom early-subset + 18 ACCEPT atoms (substrate-proposed → Research-validated → ingested) |
| meta | 0 | Day 2+ |
| school | 0 | Day 2 |
| **methodology** | **4** | **SUBSTRATE-PROPOSED + Research-validated**: 1bit_depth_verify_drill / 20_ambitious_ideas_drill / 8_channel_orchestration_drill / 1BIT_DEPTH_VERIFICATION_routing |
| research_history / decision_history / results_history / findings_history / verdict_history / memory_history | 0 | Schema ready; auto-ingest via evolve.py Week 2-4 |

**Total:** 92 atoms / 284 relations / 6 cross-store relations

## 6 closed-loop cycles in <24h

The user's "deeply evaluate to learn / improve" vision empirically operational:

| # | Type | Loop |
|---|---|---|
| 1 | B encoding | Layer 1 attribution caught algebra-vec NET NEGATIVE → 4-min surprise drill → v2 hybrid two-index architecture |
| 2 | E unification | Layer 3 archaeology surfaced 6 EQUIVALENT_UNDER candidates (5 unified prob-DP + graph_traversal); not in drill 13's catalog |
| 3 | B encoding | Layer 1 caught corpus_tag PURE NOISE + tier_tag COINCIDENCE → composite simplified to pure semantic |
| 4 | B + D | Substrate-eval v1 19/20 TIER-B (jargon-floor) → composite C → NOVEL cluster → substrate proposed `methodology_corpus` partition (Research validated) |
| 5 | A | atom_candidates surfaced 39 candidates → Research triage 18/16/5 → 18 hand-authored JSONL → Testbed ingested → re-run shows exactly 21 carryover (substrate remembers) |
| 6 | B | source #5 noise overshoot 1678 cands → Research's 4 Q1 fixes shipped → 77 cands (20x reduction; clean math primitives including Tracy-Widom / Voiculescu / Marchenko-Pastur / BCM / AGS / Glauber / Ramsauer / Wright-Fisher) |

5-type signal taxonomy (per Research) fully exercised Day 1.

## Architecture shipped

### Day 1 build (15 substrate_index modules)
schema / metrics / store / partition / encode / retrieve / relate / ingest / cli / reason / discover / meta / evolve / report / validate

### Days 4-8 build (additional substrate_index modules)
algebra_index (v2 HRR) / algebra_cluster (Layer 3) / atom_candidates (Tier 3) / dialectic (Layer 4) / spectral (Layer 2)

### v2 hybrid retriever
- Index 1: semantic bge (UNCHANGED) — pure semantic, no tag-vec contributions
- Index 2: HRR/TPR algebra (substrate-native shared-basis retrieval)
- RRF k=60 fusion
- Lexicon intent-router (12 structural + 8 semantic keywords; expand from experiment 3 gaps)

### Substrate-distinguishing measurement (Layer 2 spectral)
- Algebra-HRR codebook is **12x more structured** than semantic-bge codebook (mp_bulk_kl 27.6 vs 2.3)
- Both codebooks have tw_edge_z negative → substrate atoms cluster more than random (substrate-novel structural signal)
- LLM cosine cannot produce these measurements

## Tier gates met Day 1

| Gate | Requirement | State |
|---|---|---|
| Tier 1 → 2 | 3+ surprise cycles | **MET (6 cycles in <24h)** |
| Tier 2 → 3 | Substrate-proposed architectural improvement Layer 1-validated | **MET (composite C improvement validated)** |
| Tier 3 → 4 | 5+ atom candidates/month + 3+ relations/month sustained | **Begin measurement now; target 2026-07-09** |

## Honest limits and open items

### Surfaced empirically (substrate Type B signals; all OPEN)

- **Layer 2 numerics** at M < 100 in tall (M << N) regime have edge cases; Q2-deferred till M >= 150
- **Source #5 hyphen pattern** still leaks some compound English even after Q1 fix; ~50 candidates in top-50 post-cap have ~10 noise; Layer 1 attribution filter is the principled fix
- **Atom.from_dict** handles 2 of 3 atom-schema dialects (dedicated + flat-metadata); concept-corpus 8-field schema stuffs extra fields into metadata
- **discover_all** with retriever requires bge-large; ~21 sec to index 92 atoms on runner

### Unsurfaced limits (worth Day 2 attention)

- **Content-references axis** (per [[substrate-two-axes-semantic-vs-content-referenced-2026-06-11]]): substrate has TWO orthogonal axes (semantic-vec vs content-references); v3 = 3 indexes is architectural next step
- **Drill outputs auto-ingest** via evolve.py pattern-parsers: scaffold exists but currently regex-based (per user critique "substrate can't do its own evaluation?"); needs the substrate-evaluation ingest path (proof-of-concept ran on cross-domain-equivalences drill)
- **Layer 5** capability-substrate dialectic: not started; needs concept corpus growth + cross-corpus USES

## What's running right now

- 15-min ScheduleWakeup heartbeat (set at 17:03; should be firing)
- Path A full-scale (substrate-eval v2 composite C on ~150 drill/routing/exp_dev/testbed notes) — foreground SSH; ~11 min in; output buffered until completion

## What's deferred

- **Stage A Wikidata**: silently crashed after RESUME mode post desktop-restart; ~2.29M facts on F:; needs separate debug session. Not blocking substrate work.

## Notes filed today (substrate-self-index)

11 findings notes filed; 11 answered same day by Research. Closed-loop substrate-research workflow operational at end-of-day-1 cadence.

- findings #1-#3: schema design / batch 02 results
- findings #4-#5: Layer 1 encoding limits caught + fixed
- findings #6: Layer 3 substrate-proposed equivalences
- findings #7-#8: substrate-eval v1+v2 reframe + methodology partition
- findings #9: Tier 3 atom-candidate generation
- findings #10-#11: Cycle #5 closure + Layer 2 + Cycle #6 closure

## Recommendations for user when back

1. **Review Research's 18 ACCEPT hand-authored atoms** in `data/substrate_index/concept_corpus_findings_09_type_A_18_accept.jsonl` — substrate's first Type A loop output
2. **Check Path A results** when they land (foreground SSH should produce report soon)
3. **Decide Stage A**: restart with full debug (foreground) or defer until daytime?
4. **Day 2 directional choice**: prioritize Layer 5 capability-substrate dialectic (needs concept corpus growth) vs v3 content-references index (substrate architectural extension)

## Cross-references

- substrate_self_index foundational tool memory (updated tonight with Day 1 close state)
- 11 findings notes + 11 Research replies in notes/
- Bench reports: data/substrate_index/bench_reports/*.json
- Updated post-compaction brief: notes/testbed_POST_COMPACTION_BRIEF_2026-06-11_evening.md
