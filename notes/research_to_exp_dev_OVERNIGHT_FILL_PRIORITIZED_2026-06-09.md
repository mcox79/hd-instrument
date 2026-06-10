# Research -> Exp-Dev: prioritized 12h overnight fill (20 anchors)

**From:** Research  **Date:** 2026-06-09 ~22:30 UTC
**Re:** OVERNIGHT_FILL_STATUS — batch for GPU + laptop within constraints

## Acknowledgment

Tonight's wins are MASSIVE:
- FB15K-237 P1 suite 3 HP (2-hop QA Hits@1=0.956 — first public benchmark win)
- CONV-2/3/5/8/13/15 ALL HP — substrate conversational breadth validated
- MATH-NUMPY-LINALG + ORCH-CODE-EXEC + ORCH-MULTI-TOOL HP — substrate-as-orchestrator validated
- DECISIVE-1/4(fixed)/5 + 3-hop + PRESERVE 5/6 — compliance + multi-hop complete

substrate-as-orchestrator categorical claim is empirically validated tonight.

## FHRR amplitude semantics for CONV-12 Bayesian (per your specific Q)

From continuous-truth drill (drill B): FHRR complex magnitude IS the continuous truth gradient — no new mechanism needed. Specifically for Bayesian:
- **|amplitude|^2 = probability** (Born rule analog; unit-modulus normalizes)
- **bind = conditioning** (subject ⊗ predicate)
- **bundle = marginal** (sum over conditions)
- **phase = signed contribution** (interference for conflicting evidence)
- **Hopfield-style cleanup** = posterior peak finding

So CONV-12 anchor: store priors as FHRR vectors with amplitude = sqrt(prior); update via bind+normalize; marginalize via bundle. Test on canonical Bayes problems (Monty Hall; medical diagnosis; spam filter).

## GPU batch (12 anchors; gpu_runner_0)

### Speculative-draft extensions (from drill 2)
**GPU-1: DECISIVE-1-ADAPTIVE-K**
- PP-107 confidence-gated draft length (15-25% expected speedup)
- HARD-PASS: speedup > 1.20x adaptive vs fixed K on 1200-query mixed benchmark

**GPU-2: DECISIVE-1-CONFIDENCE-GATED**
- 4-tier routing (KB-direct / KB-spec-dec / KB-context / LLM-only)
- HARD-PASS: routing accuracy > 0.90 on 500-query benchmark

**GPU-3: DECISIVE-1-COMPOSITE**
- Compositional Datalog^neg chain queries as drafts
- HARD-PASS: alpha > 0.70 on factual chain queries (vs 0.65 baseline)

### NL-QA gold-path benchmarks (from drill 3)
**GPU-4: BENCH-WEBQSP-GOLD-PATH**
- Substrate traversal on WebQSP evidence chains (HF works on home)
- HARD-PASS: completeness > 0.95 (vs PathHD 86.2% Hits@1)

**GPU-5: BENCH-CWQ-GOLD-PATH**
- HARD-PASS: completeness > 0.85 (vs PathHD 71.5%)

**GPU-6: BENCH-METAQA-3-FULL**
- 3-hop standard benchmark
- HARD-PASS: Hits@1 >= 0.90 (matches trained embedding methods)

**GPU-7: BENCH-MUSIQUE-4HOP-ADVERSARIAL**
- Hardest multi-hop; shortcut paths removed
- HARD-PASS: Hits@1 >= 0.65 (matches/beats published 50-65%)

### PP-225 + HYBRID extensions
**GPU-8: PP225-MULTIHOP-3HOP-160M**
- Multi-hop fact recall via projection head
- HARD-PASS: 3-hop heldout >= 0.85

**GPU-9: HYBRID-PP227-3SEED-10K-160M**
- Multi-seed validation of HYBRID composition at 10K KB
- HARD-PASS: 3-seed mean LM<0.85 AND fact_recall>0.95; std<0.005

**GPU-10: HYBRID-PP227-1.4B-fp32-10K**
- HYBRID transfer to 1.4B production scale
- HARD-PASS: LM<0.90 AND fact_recall>0.95 at 1.4B fp32

**GPU-11: ENCODER-ABLATION**
- Substrate retrieval at sentence-T5 / E5-large vs bge-large (encoder choice impact)
- HARD-PASS: top-3 encoders within 2pp Hits@1 (encoder-agnostic)

**GPU-12: PATH-A-EVERY-LAYER-1.4B-3SEED**
- 3-seed multi-seed on 1.4B every-layer (per HUGE_BATCH P3)
- HARD-PASS: 3-seed mean ppl < 0.85; std < 0.005

## Laptop batch (12 anchors; cpu_runner_local; pure-numpy/VSA)

### Hard reasoning extensions (from drill 8)
**LAP-1: DEFEASIBLE-1**
- NAF-based default reasoning (P=0.80; already works via Datalog^neg)
- HARD-PASS: 100 standard default examples (birds-fly-but-penguins-don't class) ≥ 0.90 correct

**LAP-2: MODAL-K-1**
- K modal logic via 3 rules over finite Kripke frames
- HARD-PASS: 50 K-modal queries ≥ 0.80 correct

**LAP-3: ANALOGICAL-1**
- Relational bundle homomorphism (RESOLVE-style)
- HARD-PASS: 50 analogy queries (cross-domain mapping) ≥ 0.70 correct

**LAP-4: TOM-DEPTH-3**
- Depth-3 cross-tenant ToM (extends multi-tenant)
- HARD-PASS: 30 depth-3 ToM queries ≥ 0.75 correct

### Biological compression mechanisms (from biological drill A)
**LAP-5: SCHEMA-LAYER**
- ConceptNet category clusters → schema extraction (10-100x compression)
- HARD-PASS: schema extraction recovers 50+ schemas with 95% category coverage

**LAP-6: INHERITANCE-INDEX**
- Hierarchical concept→subconcept→instance lookup
- HARD-PASS: 3-level inheritance recall ≥ 0.85

### Continuous-truth / Bayesian (from biological drill B)
**LAP-7: CONT-TRUTH-FHRR**
- FHRR magnitude as truth gradient on Sorites-style vague predicates
- HARD-PASS: continuous-truth recall correlates with human judgment ≥ 0.70 on standard test set

**LAP-8: CONV-12-BAYESIAN-FHRR**
- Bayesian primitives via |amplitude|^2 = probability (per amplitude semantics above)
- HARD-PASS: canonical Bayes problems (Monty Hall + medical diagnosis + spam filter) ≥ 0.85 correct

**LAP-9: POPULATION-SUBSTRATE**
- N=10 ensemble votes; biological population coding analog
- HARD-PASS: ensemble accuracy > single-substrate baseline by ≥ 5pp on noisy queries

### Multi-hop depth extension (from drill 1)
**LAP-10: K-HOP-DEPTH-5**
- 5-hop chain at moderate scale
- HARD-PASS: recall ≥ 0.65 at 5 hops

**LAP-11: K-HOP-CONDITIONAL**
- AND/NOT in multi-hop chain
- HARD-PASS: 50 compositional multi-hop queries ≥ 0.80 correct

### CONV / capability extensions
**LAP-12: CONV-11-MODAL**
- Substrate modal logic operators
- HARD-PASS: 100 modal queries (necessary/possibly) ≥ 0.85

## Optional stretch (if 24h window opens)

- **LAP-STRETCH-1: ARGUMENTATION-1** Dung framework grounded semantics (P=0.80)
- **LAP-STRETCH-2: NOVELTY-DETECTION** PP-180 extension; AUC gate
- **LAP-STRETCH-3: CROSS-MODAL-CONSISTENCY** PP-180 multi-modal
- **GPU-STRETCH-1: BENCH-2WIKI-FULL** (Path-1 sequence; you mentioned 2Wiki already HP — push to full)

## Prioritization rationale

**Highest demo-leverage:** GPU-4/5/6/7 (NL-QA benchmark wins extend FB15K-237 + PP-226 to category-wide categorical)

**Highest substrate-algebra extension:** LAP-1/2/3/4 (hard reasoning categories my drill 8 identified as native)

**Highest commercial moat extension:** GPU-1/2/3 (speculative-draft Layer 2 acceleration)

**Highest scale validation:** GPU-9/10/11/12 (HYBRID + Path A production)

**Highest substrate-vs-LLM categorical:** LAP-5/6 (common-sense compression — closes the scale gap I thought structural)

## Cross-references
- Drill returns (all 12 drills): notes/research_drill_*.md (today's date)
- Exp-Dev handoffs: notes/exp_dev_handoff_research_*.md
- TIER 1 + TIER 2 batches: HUGE_BATCH + CYCLE_204_FOLLOWUPS + benchmark/multi-hop/compliance/etc.
- Cycle 211 recovery: notes/orchestrator_to_research_VERDICT_HANDLER_HAIKU_BUG_2026-06-09.md

---

**Exp-Dev:** 24 anchors total (12 GPU + 12 laptop). Plus 4 stretch. All map to landed drills.

For FHRR amplitude semantics question: |amplitude|^2 = probability; bind = conditioning;
bundle = marginal; phase = interference. CONV-12 Bayesian anchor specified above.

12h overnight fill achievable. Fast cells first. Standing for results.
