# Research -> Exp-Dev: SYSTEMATIC PROMOTION CAMPAIGN -- waves to Tier A

**From:** Research  **Date:** 2026-06-11
**Re:** User mandate "promote the most important ones, move everything we can into Tier A, methodically in waves"

## Promotion ladder definitions

| Tier | Criteria |
|---|---|
| **A** | Real-data + multi-seed n>=5 + production-scale + cross-validated |
| **B** | Real-data + n=1 (need multi-seed) |
| **C** | Synthetic + multi-seed (need real-data) |
| **D** | Synthetic + n=1 ceiling (need multi-seed + real-data) |
| **E** | v3.2 wrapper just-validated (need multi-seed + integration test) |

**Promotion path:** D -> C (multi-seed) -> B (real-data) -> A (scale + cross-validate).

## WAVE 1 -- MULTI-SEED PROMOTION (cheapest; closes LVH-277 urgency)

All cycle 224-227 ceiling wins are n=1 EXPLORATORY. Multi-seed n=5 promotes ~14 capabilities one tier in 1-3 days CPU.

### Tier 0 (single-script multi-seed sweep; cheapest)

| Anchor (current Tier) | Multi-seed test | Cost |
|---|---|---|
| PP-331 comm1 (D) | n=5 seeds, same gates | <1 hr |
| PP-332 math1 (D) | n=5 | <1 hr |
| PP-333 code1 (D) | n=5 | <1 hr |
| PP-334 math3 (D) | n=5 | <1 hr |
| PP-335 math4 smoke (D) | n=5 FULL (not smoke) | ~1 hr |
| PP-336 code2-R1 (D partial) | n=5 FULL (not smoke) | ~1 hr |
| PP-337 comm6 (D) | n=5 | <1 hr |
| PP-338 comm-lex (D) | n=5 | <1 hr |
| PP-339 code6 (D) | n=5 | <1 hr |
| PP-341 math2 (D) | n=5 | <1 hr |
| PP-342 lex-wug (D) | n=5 | <1 hr |
| PP-343 math4-rung3 (D) | n=5 | <1 hr |
| PP-344 key-rotation (D) | n=5 | ~1 hr |
| PP-345 comm2 typological (D) | n=5 | <1 hr |
| PP-330 slipnet-noise (C) | n=5 | <1 hr |
| **TOTAL** | **~15 anchors** | **~15 hr CPU** |

### Tier 1 (Sprint-4 wrapper multi-seed completion)

| Anchor | Current | Test |
|---|---|---|
| PP-353 write-lock | TIER C (n=5 done) | promote with real-data test |
| PP-354 RS-parity | TIER E (n=1) | n=5 full (not smoke) |
| PP-355 per-tier-importance | TIER C (per_role component done) | full n=5 on all 3 axes |
| PP-356 per-role | TIER C (n=5 done) | promote with real-data test |
| PP-357 v3.2 unified | TIER E (n=1) | n=5 full |
| PP-358 3x-redundant | TIER E (smoke) | n=5 FULL (close LVH-279) |

### Tier 2 (Sprint-4 wrapper rescues)

| Anchor | Rescue paths |
|---|---|
| two_substrate_fastslow_cls HF | RESCUE-1 threshold + RESCUE-3 explicit KV (cheapest first; 2x drill in flight will refine) |
| LVH-278 neurogenesis_hiermerge | threshold recalibrate (13 -> 12 shards) |

### WAVE 1 success metric

If Wave 1 lands: ~15 capabilities promoted D -> C; ~6 wrapper components reach C or A. Substrate capability matrix gains ~21 Tier C entries.

## WAVE 2 -- REAL-DATA PROMOTION (C -> B)

After Wave 1 multi-seed lands, take strong Tier C candidates to real data.

### Tier 0 (immediate post-Stage-A ingest start; ConceptNet/Tatoeba available)

| Anchor (current Tier) | Real-data test | Source |
|---|---|---|
| polysemy-context-bound (C; PP-346 + PP-350 n=5) | real polysemic WordNet/ConceptNet | post-Stage-A |
| comm2-translation-distant (C if n=5 passes) | Tatoeba typologically distant | post-Stage-A |
| SLIPNET noise-robust (C; PP-330) | ConceptNet polysemic graph | post-Stage-A |
| temporal+contextual unified (C; PP-351) | end-to-end on real-data | post-Stage-A |

### Tier 1 (benchmark promotion - production grade)

| Anchor (current Tier) | Benchmark | HARD-PASS target |
|---|---|---|
| code1 function-compose (D->C->B) | **HumanEval FULL n=164** | pass@1 >= 0.15 (small LLM baseline) |
| code1 + code6 | **MBPP basic Python** | pass@1 >= 0.20 |
| math1+3+4 | **MATH benchmark** | accuracy >= 0.20 |
| math4 rung-3 | **Lean Mathlib subset** | proof completeness |
| comm1 paragraph-compose | **BLEU/semantic vs reference** | semantic_similarity >= 0.60 |
| **LLM-boundary engineering test** | **POS tagger Penn Treebank WSJ sec 24** | tag-accuracy >= 0.90 (substrate-only, pre-LLM era benchmark) |

### Tier 2 (architectural rescues empirical promotion)

| Anchor | Test |
|---|---|
| KEY-ROTATION (C -> B) | scale to 100K keys + adversarial recovery test |
| INTEG-TEMPORAL (C; PP-348) | extended K=20 drives + Pareto frontier characterization |
| CORE-REFRESH (C; PP-349/352) | scale beyond 50K to 500K edits |
| ZCA pre-whitening | online+offline hybrid test |

## WAVE 3 -- PRODUCTION SCALE (B -> A)

After Wave 2 real-data lands, promote to production scale + cross-validated.

| Anchor (current Tier) | Production test | Hard-pass |
|---|---|---|
| PP-225 fact-recall (A) | kb500K -> kb1M genuine | recall >= 0.95 at 1M |
| KB-shard real (B) | FB15K full + Wikidata5M subset | recall@1 + cross-fold validation |
| LLM Path A (A) | deployed-LLM live A/B test | seamless |
| HumanEval full (after Wave 2) | scale across model sizes | reproducible |
| code2 R1 (after Wave 1 multi-seed) | full HumanEval-bug variant | F1 >= 0.65 |
| INTEG-TEMPORAL | with K=50 drives + real-world drive sets | escape > baseline |
| CORE-REFRESH (after Wave 2) | 500K edits + adversarial edit sequences | recall >= 0.95 |

## WAVE 4 -- ARCHITECTURAL VALIDATIONS

After Waves 1-3, promote validated architectural primitives to production claims.

| Capability | Promotion test |
|---|---|
| substrate-only NL via VSA/HRR-FCG | classical NLP benchmarks at Tier B; comparison to small LLMs |
| substrate-only statistical fluency | Zipf-weighted codebook empirical generation quality |
| substrate-only LLM-grade English parse | dependency parsing benchmark at >= 0.85 |
| substrate as self-improving system (if Wave 3 closes) | meta-substrate cell |

## Sequencing

**Days 0-1 (tonight + tomorrow):**
- WAVE 1 Tier 0 multi-seed sweep (~15 hr CPU; ~15 capabilities)
- LVH-278 neurogenesis threshold tune (cheap)
- LVH-279 3x_redundant FULL run

**Days 2-3:**
- WAVE 1 Tier 1 + Tier 2 (Sprint-4 wrapper completion + CLS rescue from 2x drill in flight)
- WAVE 2 Tier 0 real-data extensions (post-Stage-A ConceptNet/Tatoeba)

**Days 4-7:**
- WAVE 2 Tier 1 benchmark promotion (HumanEval/MBPP/MATH/POS-tagger)
- WAVE 3 Tier 1 production scaling
- LLM-boundary cheapest test (POS tagger Penn Treebank WSJ sec 24)

## Expected promotions per wave

| Wave | Promotions |
|---|---|
| Wave 1 | ~15 D->C + ~6 E completions |
| Wave 2 | ~10 C->B real-data + ~6 benchmark validations |
| Wave 3 | ~5 B->A production grade |
| Wave 4 | ~5 architectural claims established |

**End-state target:** Tier A grows from 5 today to ~25-30 within 1-2 weeks. Tier B + C lift everyone else off n=1 exploratory.

## Full-auto authorization

All waves authorized full-auto per pre-reg HARD-PASS gates already in routing. Multi-seed urgent (LVH-277/279 catch). Route back only for:
- Novel HP recipes for production benchmarks
- Multi-seed failures (indicating n=1 was a fluke)
- New architectural ideas surfacing from the 2x DEEP negative drills

## Cross-references
- HONEST AUDIT: notes/capability_matrix_HONEST_AUDIT_2026-06-11.md
- Cycle 228 cap_map: notes/strategy_decisions_2026-06-11.md
- Memory: substrate_v32_engineered_wrapper_2026-06-11.md
- LLM-boundary drill: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md
- 5 negative 2x drills (in flight): CLS rescue + slipnet polysemic + code2 recall + active-inference + 96% irreducible probe

---

**Exp-Dev:** Systematic promotion campaign in 4 waves. Wave 1 cheap multi-seed n=5 sweep (~15 hr CPU) promotes ~15 capabilities D->C immediately. Wave 2 real-data + benchmarks. Wave 3 production scale. Wave 4 architectural claims. End-state Tier A ~25-30.

Multi-seed urgent per LVH-277/279. Privilege temporal+contextual where it composes (per cycle 226 meta-finding).
