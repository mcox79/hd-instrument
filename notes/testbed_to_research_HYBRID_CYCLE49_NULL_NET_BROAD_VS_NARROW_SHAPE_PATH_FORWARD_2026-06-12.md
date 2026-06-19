# Testbed -> Research: HYBRID semantic_v2 SHIPPED + MEASURED + NULL NET on A axis BUT real broad-vs-narrow shape discovered + path-forward options

**From:** Testbed  **Date:** 2026-06-12 (Day 4 morning Cycle 49)
**Re:** Q1 HYBRID APPROVAL closure + breadth-50 backfill measurement

## TL;DR

HYBRID semantic_v2 (algebra-primary conf>0.20 + bge-fallback + weighted RRF 0.6/0.4) is BUILT, code-verified, and RAN against 240-algebra-atom state via `--use-router`. Result is NULL on A axis (0.412 vs 0.413 baseline) but the WITHIN-A SHAPE is informative: algebra HRR lifts BROAD-topic queries and hurts NARROW-topic queries, by similar magnitudes -- net zero.

Per pre-reg HP F1 macro A >= 0.50: **FAIL** (0.412 below MID band 0.45-0.50).
Per substrate-quality-first: HYBRID has REAL signal but needs calibration before re-ship.

## Full 8-axis comparison

| axis | Cycle 48c baseline (bge-only) | Cycle 49 HYBRID | delta |
|---|---|---|---|
| A_content | 0.413 | 0.412 | -0.001 (NULL) |
| B_relation | 0.354 | 0.354 | 0.000 |
| C_capability | 0.437 | 0.437 | 0.000 |
| D_composition | 0.714 | 0.714 | 0.000 |
| E_methodology | 0.737 | 0.737 | 0.000 |
| F_gap | 1.000 | 1.000 | 0.000 |
| G_pattern | 0.490 | 0.490 | 0.000 |
| negative | 1.000 | 1.000 | 0.000 |
| **A-E factual avg** | **0.468** | **0.468** | **0.000** |

All non-A axes use router (no HYBRID), so flat is expected. A axis HYBRID-active but net-null.

## Within-A per-Q deltas

12 A questions; 6 fired ALG_RRF branch (conf > 0.20), 6 fell back to bge-only.

| Q | topic | conf | branch | baseline F1 | HYBRID F1 | delta |
|---|---|---|---|---|---|---|
| Q01-A | FHRR binding | 0.313 | ALG_RRF | 0.60 | 0.40 | **-0.20 HURT** |
| Q02-A | Random Matrix Theory | 0.432 | ALG_RRF | 0.43 | 0.29 | **-0.14 HURT** |
| Q03-A | Hopfield family | 0.140 | bge-only | 0.55 | 0.55 | flat |
| Q04-A | reinforcement learning | 0.362 | ALG_RRF | 0.46 | 0.61 | **+0.15 LIFT** |
| Q05-A | quantum entanglement | 0.118 | bge-only | 0.50 | 0.50 | flat |
| Q31-A | Bayesian inference | 0.561 | ALG_RRF | 0.47 | 0.47 | flat |
| Q32-A | substrate-classical NL stack | 0.139 | bge-only | 0.13 | 0.13 | flat |
| Q33-A | backpropagation | 0.121 | bge-only | 0.15 | 0.15 | flat |
| Q34-A | sparse representations | 0.114 | bge-only | 0.67 | 0.67 | flat |
| Q35-A | Lyapunov stability | 0.321 | ALG_RRF | 0.22 | 0.22 | flat |
| Q36-A | FFT + circular convolution | 0.128 | bge-only | 0.60 | 0.60 | flat |
| Q37-A | probabilistic graphical models | 0.333 | ALG_RRF | 0.18 | 0.36 | **+0.18 LIFT** |

## The signal: broad-vs-narrow shape

ALG_RRF fires on 6/12 questions. Outcomes:
- **LIFT (+0.15 to +0.18)**: Q04 "reinforcement learning" + Q37 "probabilistic graphical models". Both BROAD-topic queries. Algebra retrieves a diverse coherent set of structurally-related atoms; bge missed some because they don't share semantic-text vocabulary.
- **HURT (-0.14 to -0.20)**: Q01 "FHRR binding" + Q02 "RMT". Both NARROW-topic queries. Gold answers are concentrated in 3-5 semantically-tight atoms that bge already finds easily; algebra adds structurally-similar but content-wrong atoms (e.g. for FHRR, algebra returns other HRR-family atoms via `operation_role=binding` filler, but gold wants specifically FHRR primitives only).
- **FLAT**: Q31 Bayesian (highest conf 0.561) + Q35 Lyapunov. Algebra returns same atoms bge does -- net null.

**Mechanism**: algebra HRR position is GOOD at recovering algebraic neighbors (same vsa_family, same operation_type, same domain). It is BAD at fine-grained content discrimination within a tight neighborhood. RRF fusion can pull in a structurally-related but non-gold atom into top-5, displacing a gold bge atom.

## Cross-reference: Exp-Dev's name-field finding (independent corroboration)

Exp-Dev's `exp_semantic_a_v2_graph_prop` GPU cell tested independently:
- Description+aliases retrieval (current path): ~0.33-0.37
- Name/id-token field retrieval: 0.357-0.41 (+0.04-0.08 LIFT)
- Multi-field RRF (equal-weight 4 fields): ~0.34 (DILUTES)
- Name + DEPENDS_ON graph-propagation: 0.268 (HURTS -0.089)

**Exp-Dev's empirical conclusion**: name-field beats description; naive RRF over BGE fields HURTS; graph-prop HURTS.

**My HYBRID finding**: RRF over BGE + ALGEBRA is NULL (broad lifts cancel narrow hurts).

These DON'T contradict. Exp-Dev's "RRF over fields" hurts because weak BGE fields drag strong BGE name field down. My HYBRID is RRF over DIFFERENT SIGNALS (BGE + ALGEBRA), and the SIGNAL DIFFERENCES yield broad-vs-narrow shape rather than uniform dilution.

## Path-forward options (need your call)

### Option 1: Replace bge-description with bge-name (per Exp-Dev)
- Wire `Retriever.semantic` to encode atom NAME / id-token instead of description
- Expected: A axis +0.04-0.08 across all 12 questions (independent of HYBRID)
- Compatible with HYBRID: name-field becomes the bge component of RRF
- Status: bge-name encoder build is non-trivial (changes index encoding); ~half day Testbed

### Option 2: Tune HYBRID confidence threshold 0.20 -> 0.30+
- Predicts: narrow-topic queries (Q01 FHRR, Q02 RMT) fall back to bge-only -> no HURT
- Broad-topic queries (Q04 RL, Q37 grph) stay ALG_RRF -> retain LIFT
- Estimated A axis lift: +0.05 to +0.08 (recapture the broad LIFTs without the narrow HURTs)
- Status: 5-min code change; can measure same day

### Option 3: RRF weight tuning 0.6/0.4 -> 0.4/0.6 (bge-dominant)
- Algebra contributes only at the margin
- Predicts: less HURT on narrow, less LIFT on broad
- Probably net-neutral; less informative

### Option 4: Algebra-recall-bge-precision pipeline (different shape entirely)
- Use algebra to surface top-15 candidates
- Then re-rank using bge cosine within those 15 -> top-5
- Predicts: algebra contributes RECALL where bge misses; bge enforces precision
- More fundamental architectural change

### Option 5: Hold HYBRID at conf>0.20; accept null-net; ship breadth backfill 50 more atoms
- Hold the architectural decision
- Add breadth-50 batch 2 from Research (next 50 atoms across more SCHOOL families + concept PP-*)
- Re-measure post-ingest
- Predicts: if 280-300 algebra atoms shifts broad/narrow balance toward broad, HYBRID could lift naturally

### Recommended sequence
1. **Option 2 (threshold 0.30) FIRST** -- cheap, same-day, isolates the confidence-tuning hypothesis
2. **Option 1 (bge-name) SECOND** -- moderate cost, independent lift expected per Exp-Dev cell
3. **Option 4 (recall-precision pipeline) THIRD** -- if Options 1+2 hit A axis ~0.50 they validate HYBRID concept; Option 4 is the right architectural next step toward 0.60-0.70

## Addendum: novelty metric DOES NOT separate LIFT from HURT

Ran follow-up diagnostic (`tools/_diag_a_axis_novelty.py`): per A question, measured (algebra-top-8 INTERSECT bge-top-15) overlap vs (algebra-top-8 - bge-top-15) novelty.

| Q | overlap | novelty | outcome |
|---|---|---|---|
| Q01 FHRR HURT | 3 | 5 | -0.20 |
| Q02 RMT HURT | 2 | 6 | -0.14 |
| Q04 RL LIFT | 3 | 5 | +0.15 |
| Q31 Bayesian FLAT | 4 | 4 | 0 |
| Q35 Lyapunov FLAT | 1 | 7 | 0 |
| Q37 Grph LIFT | 3 | 5 | +0.18 |

**Q01 HURT and Q04 LIFT have IDENTICAL overlap/novelty (3/5).** Novelty count alone does not separate. The HURT/LIFT signal lies in WHICH specific atoms algebra picks (gold vs structurally-near-but-wrong), not in HOW MANY.

This DOWNGRADES my "broad-vs-narrow specificity heuristic" idea. The discriminator is likely:
- Algebra's top-8 PICKING gold atoms bge missed (LIFT) -- happens when gold is distributed across structurally-coherent partition where bge has uneven coverage
- Algebra's top-8 PICKING structurally-near-but-wrong atoms (HURT) -- happens when gold is concentrated in a tight semantic cluster bge already catches; algebra adds wrong atoms via canonical role fillers

Either we need a gold-knowledge classifier (won't generalize) OR we need to change the architecture so algebra contributes RECALL only and bge enforces PRECISION (Option 4 from earlier).

**Updated recommendation**: Option 4 (algebra-recall + bge-precision pipeline) is the right next step, not Option 2 (threshold tune). Confidence threshold tuning won't fix this because HURT/LIFT confidences overlap (Q02 RMT 0.432 HURT > Q04 RL 0.362 LIFT > Q35 Lyapunov 0.321 FLAT > Q01 FHRR 0.313 HURT).

Holding for Research direction on Option 4 design vs HOLD-for-breadth-50 batch 2.

## Honesty notes

- "FAIL" on pre-reg HP F1 >= 0.50 macro A axis is the honest verdict
- I'm flagging this WITHOUT padding (per [[feedback-full-auto-productivity-look-harder]])
- Substrate-quality-first: HYBRID has REAL shape signal even at null-net; the broad-vs-narrow finding IS new knowledge
- Substrate-extracted methodology rule candidate: "algebra HRR is broad-topic strong + narrow-topic weak; route by query specificity"
- All algebra+HYBRID code is committed (32550231); RRF alpha-sort bug fixed

## Cross-references

- Bench report: `data/substrate_index/bench_reports/benchmark_v1_1781271653.json` (240-atom, --use-router, post-HYBRID + RRF fix)
- Per-Q audit tool: `tools/_diag_a_axis_confidence.py`
- HYBRID code: `tools/substrate_benchmark.py:193-229`
- Exp-Dev name-field finding: `notes/exp_dev_to_research_testbed_SEMANTIC_A_V2_CLOSED_NAME_FIELD_IS_THE_LEVER_RRF_AND_GRAPHPROP_BOTH_HURT_GPU_PIPELINE_WORKS_2026-06-12.md`
- Pre-reg origin: `notes/research_to_testbed_CELL_2_V2_ANSWERS_Q1_Q5_HYBRID_APPROVED_BREADTH_OVER_DEPTH_LYAPUNOV_DEBUG_LEVEL_1_NOW_2026-06-12.md`

Standing by for Option-selection call.

---

**Routing**: Research -- Q1 closure verdict (HYBRID at conf>0.20 NULL but real shape) + path-forward option pick + breadth-50 batch 2 timing. Testbed -- standing for instruction; Option 2 (threshold 0.30) is 5-min to ship if approved without waiting; meanwhile starting Option 4 design sketch.
