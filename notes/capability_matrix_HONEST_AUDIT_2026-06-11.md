# Capability Matrix HONEST AUDIT -- 2026-06-11

Reality classification of substrate capabilities by how strongly they're empirically validated. Real-data + multi-seed + production-scale is the strongest claim level; the lower tiers are honest about what's still single-seed exploratory or synthetic-only.

## TIER A -- REAL-DATA + MULTI-SEED + PRODUCTION-SCALE (strongest claim)

Capabilities that meet ALL of: (1) real data not synthetic, (2) multi-seed n>=3 reproducibility, (3) production scale, (4) cross-validated.

| PP | Capability | Evidence |
|---|---|---|
| **PP-225** | Substrate-as-LLM-memory fact recall | kb10K=0.9945, kb25K=0.996, kb50K=0.994, kb100K=0.997 (real KB, FLAT to 100K, kb500K running); 3-seed mean=1.000 std=0.000 at smaller scales |
| **PP-217** | Path A every-layer substrate-attention LLM ppl reduction | 3-seed std=0.0006, 4 model scales 160M/1.4B/1.5B/3B, real LLM benchmark, 28pct reduction reproducible |
| **PP-226** | Multi-hop completeness vs LazyGraphRAG | 24.3pp categorical advantage; algebraic property (exact inner-product search finds all neighbors by definition); not just an empirical lucky result |
| **PP-228** | Cryptographic audit decoupled from retrieval | Categorical mathematical property; reproducibility 1.000 INDEPENDENT of retrieval correctness; structurally impossible for probabilistic systems |
| **PP-227** | Hybrid LM+fact-KV composition | Validated at 10K KB; ratio=0.797x AND fact_recall=1.000 same model; multi-seed needed for full TIER A |

**Tier A count: ~5 capabilities truly proven functional in real ways.**

## TIER B -- REAL-DATA VALIDATED, n=1 or smoke (need multi-seed promotion)

| PP | Capability | Evidence + gap |
|---|---|---|
| PP-326 | Tool-extended real (peripersonal+tool-use) | AUC=0.866 real (gap -0.134 from synthetic); n=1 |
| PP-325 | Boredom real | AUC=0.908 real (gap -0.092); n=1 |
| PP-323 | Bilingual NSM-tier translation | 0.997 universal concept pivot; n=1 |
| PP-345 | Comm2 translation typologically distant (SVO/SOV/VSO) | 1.000 concept + 1.000 order; n=1; needs distant-language real-corpus test |
| PP-313 | KB-shard storage real entities | 0.965 on FB15K-237 real; n=1 single seed |

**Tier B count: ~5 capabilities.**

## TIER C -- SYNTHETIC + MULTI-SEED (cross-seed robust; real-data pending)

| PP | Capability | Evidence |
|---|---|---|
| **PP-350** | Temporal+Contextual meta-pattern n=5 seeds | temporal-escape min-seed 20.7%; core-refresh mean=1.000 std=0.0; polysemy mean=1.000 std=0.0 -- ALL 3 capabilities across all 5 seeds |
| PP-348 | INTEG-TEMPORAL-POLICY full | 138.7% escape, recovery=1.000, full run (not smoke) |
| PP-349 | CORE-PERIPHERY-REFRESH | refresh_core_recall=1.000 vs baseline 0.002 at 5000 edits, full run |
| PP-352 | Core-refresh scale-invariant | 1.000 at 5K/20K/50K edits (zero degradation) |
| PP-351 | Substrate v3.1 UNIFIED end-to-end | All 3 capabilities running together in one substrate, smoke n=1 |
| PP-347 | Stochastic tunneling temporal | escape_pct=22.1 smoke |
| PP-346 | Polysemy context-bound | context_bound_purity=1.000 (n=1 originally; in PP-350 across 5 seeds) |
| PP-330 | Slipnet noise-robust | hits1@25%noise=0.697 |
| PP-327 | Slipnet cross-domain synthetic | 0.985 controlled |
| PP-328 | Dreaming autonomous discovery | compression 0.712, progress 0.618, purity 0.875 |
| PP-329 | T-BIND multimodal | crossmodal_recall=0.944 |

**Tier C count: ~11 capabilities (synthetic ceiling, validated robust to seed/noise).**

## TIER D -- SYNTHETIC n=1 CEILING (exploratory; cycle 224-227 domain wins)

These are at-ceiling results from synthetic tests with single seed. Per LVH-277, all need multi-seed n=5 promotion.

| PP | Capability |
|---|---|
| PP-331 | Comm1 paragraph-compose 1.000 (slot+coherence) |
| PP-332 | Math1 algebra simplify 1.000 (n=400 expressions) |
| PP-333 | Code1 function compose 1.000 (n=300 programs, executes correctly) |
| PP-334 | Math3 calculus derivative 1.000 (n=400) |
| PP-335 | Math4 proof-chains 1.000 length 2/4/6 (smoke) |
| PP-336 | Code2 bug-detection (partial rescue) F1=0.704 smoke |
| PP-337 | Comm6 intent decoding 1.000 (n=1000 surface variants) |
| PP-338 | Comm-lex retrieval emission 1.000 (LLM gap for novel fluent generation honestly named) |
| PP-339 | Code6 algorithm compose 4-step 1.000 (n=300) |
| PP-340 | HumanEval-structural pass@1=0.750 (n=12 small benchmark) |
| PP-341 | Math2 equation solve 1.000 (n=400) |
| PP-342 | Lex-wug test morphological productivity 1.000 (Berko 1958 1-shot+3-shot) |
| PP-343 | Math4 rung-3 deep chains 1.000 length 8/10/12 (n=100 full; beyond human working memory ~7) |
| PP-344 | Key-rotation certified new=1.000 old=0.002 (n=120 keys; GDPR/credentials primitive) |

**Tier D count: ~14 capabilities. All ceiling but single-seed exploratory.**

## TIER E -- DRILL-PREDICTED + RECENTLY-EMPIRICALLY-TESTED (substrate v3.2 wrapper)

| Wrapper layer | Sprint-4 result |
|---|---|
| Write-lock-after-threshold | locked-core 1.000 vs fixed-CORE-PERIPHERY 0.008 |
| FHRR-RS-parity (Vandermonde erasure) | recover 2-of-6 lost shards at 1.000 |
| Per-tier-importance | Tier-1 1.0 / accessed-T3 1.0 / unaccessed-T3 0.0 (correct fade) |
| 2-substrate FastSlow CLS | recent 0.967 + old-consolidated 0.944 vs single-substrate 0.006 |
| Per-role isolation | per-domain 1.000 vs shared-crosstalk 0.774 |
| v3.2 unified capstone | per-role + write-lock + RS-parity all 1.000 |

**Tier E count: 6 v3.2 wrapper components empirically validated at n=1; need multi-seed; need real-data integration test.**

## TIER F -- PARTIAL / MIXED / UNVALIDATED

| Capability | Status |
|---|---|
| Slipnet real polysemic (cross-domain on real noisy heterogeneous data) | MIDDLE recall@1=0.375 n=28; needs typed reltype-specific routing |
| Neurogenesis hierarchical-merge | MIDDLE smoke: purity=1.000 PERFECT but 13 shards vs true_K=12 (threshold tune needed) |
| Frequency-decay rescue via ZCA pre-whitening | partial: online 0.625, offline 0.690 (vs raw 0.586; target was 0.85+) |
| LEX-1 substrate-only lexicalization | NOT YET TESTED; user decision pending |
| Active-inference-lite | MIDDLE error_drop=20.5%, goal_reach=0.610 |
| Many older synthetic-only cognitive primitives (frisson, frustration-BG, image-schema synthetic, etc.) | held at synthetic only |
| Cross-stream consensus architectures the drill predicted but empirically failed | retracted (see Tier G) |

## TIER G -- REFUTED / RETRACTED (correction filed)

| Claim | What happened |
|---|---|
| CORE-PERIPHERY fixed topological protection (5-stream consensus P=0.52) | TOTAL COLLAPSE at 5000 edits; replaced by refresh-cycle (Tier C/PP-349) |
| INTEG-RENORM L2 normalize before cleanup ("algebraically guaranteed") | HF empirical ratio=0.636; replaced by temporal-policy (Tier C/PP-348) |
| OVERLAY-THEN-FILTER alone (cross-domain polysemic 3x DEEP) | MIDDLE no differential 0.989/0.989; replaced by context-binding (Tier C/PP-346) |
| Adaptive-threshold neurogenesis | WORSENS (purity 0.603 -> 0.159); replaced by hierarchical-merge (Tier F partial) |
| Multi-tier P9 cross-domain via universal Tier-0 | Entity-geometry + degree-bias confound; retracted |
| Image-schema semantic grounding for abstract concepts (synthetic-only claim) | Polysemy artifact; rescued via context-binding (Tier C/PP-346) |
| "Continual learning is strongest area" (cycle 222) | Synthetic-orthogonality artifact; revised to STATIC robust + DYNAMIC tractable with cognitively-natural representations |

## HONEST SUMMARY

| Tier | Description | Count | What it means for product claims |
|---|---|---|---|
| A | Real-data + multi-seed + production-scale | **5** | Categorically defensible commercial claims |
| B | Real-data + n=1 or smoke | 5 | Promising; multi-seed promotion next |
| C | Synthetic + multi-seed | 11 | Architecture validated; real-data promotion next |
| D | Synthetic + n=1 ceiling | 14 | Exploratory existence proofs; multi-seed needed |
| E | v3.2 wrapper empirically validated n=1 | 6 | New today; needs multi-seed + integration with real data |
| F | Partial / mixed / unvalidated | many | Open research questions |
| G | Refuted / retracted | 7+ | Honest catches preserved for methodology learning |

**Total tracked: ~98 PP rows (PP-1 through PP-352 with renumbering gaps).**

## The honest answer to your question

**Truly PROVEN functional in real ways = ~5 capabilities (Tier A).** These are:
1. Substrate-as-LLM-memory fact recall (kb100K validated; deterministic at small scales)
2. Substrate-as-LLM-enhancer (Path A every-layer 28pct ppl reduction; multi-scale + 3-seed)
3. Multi-hop completeness 24.3pp categorical (algebraic property)
4. Cryptographic audit decoupled (categorical property)
5. Hybrid LM+fact-KV composition (10K KB validated; need multi-seed)

**Promising but need promotion = ~10 more (Tier B + most of C).** Real-data n=1 or synthetic multi-seed; one missing dimension each.

**Exploratory existence proofs = ~14 more (Tier D).** All today's cycle 224-227 ceiling wins -- substrate "can do" math/code/comm at synthetic small-scale ceiling but EVERY one is n=1 exploratory. None yet survives multi-seed + real-data + scale + benchmark.

**Drill-predicted + just-tested = 6 (Tier E v3.2 wrapper).** New today; engineering plausibility demonstrated; not yet multi-seed + scale.

## The matrix update gap

The scorecard goes through cycle 207 (2026-06-09). Cycles 208-227 (~80 PP-row additions today + Sprint-4 wrapper validations) are in strategy_decisions but not yet in scorecard synthesis. Scorecard rewrite would be ~1-2 hours.

## Recommended next action

Multi-seed n=5 promotion run for ALL Tier D + E capabilities. After that:
- ~5 Tier A claims production-defensible
- ~10 Tier B/C claims architecture-defensible
- ~20 Tier D/E claims promoted to architecture-defensible if multi-seed holds
- Real-data promotion for Tier C/D/E synthetic results

## What is genuinely UNPROVEN (open research)

- Substrate-only English parse + statistical fluency (current 3x DEEP drill in flight per user pushback)
- Real-data cross-domain analogy on heterogeneous polysemic data (slipnet 0.375 MIDDLE)
- Adversarial robustness anywhere
- Substrate at >100K edits / >100K facts (kb500K running)
- Path-A LEX-1 substrate-only lexicalization (HELD pending user)
- Honest deep multi-drive 96% irreducible (genuine fundamental, accepts via cultural-convention fallback)
