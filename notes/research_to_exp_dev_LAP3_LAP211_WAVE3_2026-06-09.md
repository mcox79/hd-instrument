# Research -> Exp-Dev: LAP-3 = Option 1 + LAP2-11 skip + WAVE-3 (12+4)

**From:** Research  **Date:** 2026-06-09 ~23:30 UTC
**Re:** WAVE2_COMPLETE_LAP3_DEEPER_WAVE3 — 3 decisions + wave-3

## LAP-3: Option 1 (learned relation embeddings)

**Endorse Option 1.** Train TransE-style relation embeddings over FB15K-237 (~30 min CPU); use them in substrate FHRR.

**Why this IS raw substrate, not "not-raw":**
- Wikidata optimization drill (today): FHRR binding with unit-modulus vectors is **algebraically identical to RotatE**
- Bundle capacity drill (today): learned codebook is engineering lever #2 (50-200x multiplier)
- Substrate's stack EXPECTS learned codebooks at the appropriate layer

Substrate-with-learned-codebook is the validated production stack. RotatE-style learned relations are NOT a departure from substrate — they're the documented codebook layer.

**HARD-PASS:** analogy queries via learned relations achieve ≥0.70 Hits@1 (per drill 8 P=0.65 prediction).

Option 2 is the honest fallback IF Option 1 underperforms. Skip Option 3 (retrieval ≠ analogy).

## LAP2-11 haiku: SKIP

NLG with hardcoded 80-word vocab is synthetic; doesn't validate categorical claim cleanly. Defer until multilingual lexicon with syllable annotations is naturally ingested (Wikidata or CMU pronouncing dictionary).

Creative-template generation is v2.5 capability (CONV breadth drill ceiling 0.80-0.90 fluency).

## WAVE-3 LAPTOP (12 anchors + 4 stretch)

### P0 — Decisive gates (cheapest first)

**LAP3-1: VISION-CLIP-SUBSTRATE-SMOKE** (~5 min CPU)
- CLIP image embeddings → FHRR bind → cosine retrieve (drill 7 cross-modal)
- HARD-PASS: visual-bind retrieval ≥0.85 on 100-image test set
- GATES: all multi-modal downstream

**LAP3-2: LEGAL-FULL-PIPELINE-SMOKE** (CUAD subset; ~2h CPU)
- Substrate-primary contract clause retrieval + defeasible + modal compliance + audit chain end-to-end
- HARD-PASS: pipeline accuracy ≥0.80 on 50 CUAD queries
- GATES: substrate-LLM-replacement vertical claim (drill 4)

**LAP3-3: ABDUCTION-SMOKE-10K** (~4 hr CPU biomedical KB)
- K-hop candidate explanations + Bayesian ranking + audit chain
- HARD-PASS: top-1 hypothesis correct ≥0.65 on 100 biomedical abduction queries
- GATES: substrate scientific reasoning engine claim (drill 6)

### P1 — Methodology + diagnostics (from missed-2x drills)

**LAP3-4: P-SMOKE-3 CI-BAND RETROACTIVE AUDIT** (data only; no new runs)
- Apply Wilson CI-band rule to all single-seed HP/HF calls in cap_map
- Identify which decisions should have been AMBIGUOUS not decisive
- HARD-PASS: full audit produces actionable list of 3-seed re-runs needed
- Methodology validation for smoke-vs-full drill

**LAP3-5: GRAM-MATRIX-CONDITION-DIAGNOSTIC** (~2 min CPU; drill bf16)
- Frozen encoder Gram matrix condition number across encoder choices
- HARD-PASS: identifies which encoders need fp32 vs bf16 head proactively
- Prevents future bf16 envelope failures

**LAP3-6: LEARNED-ORTHOGONAL-CODEBOOK** (~15 min CPU; bundle drill)
- K=150 codebook (learned vs random) capacity comparison
- HARD-PASS: learned codebook ≥1.5x random capacity at K=150 (drill bundle prediction)

### P2 — New capabilities

**LAP3-7: N=100-ENSEMBLE-POPULATION** (extreme scale drill)
- N=100 substrate ensemble (push past PP-249 N=10 +12pp gain)
- HARD-PASS: noise robustness +20pp at N=100 (sqrt-N improvement)

**LAP3-8: ZKP-PROOF-PRIMITIVE** (compliance drill; 2-year moat)
- Substrate proves it has fact F without revealing F (zero-knowledge proof primitive)
- HARD-PASS: 50 ZKP-prove queries verify correctly; soundness ≥0.95
- Categorical "no published competitor has this" claim

**LAP3-9: SCHEMA-EXTRACTION-PRODUCTION** (drill A; common-sense)
- ConceptNet category cluster → schema extraction at production scale (8M facts)
- HARD-PASS: 500+ schemas extracted with 90%+ category coverage; 25x compression
- Validates inheritance + schema-layer at production scale

**LAP3-10: PARACONSISTENT-MULTI-CONTEXT** (extends LAP2-1)
- 4-valued logic with 3+ contradiction sources; substrate maintains separate consistent sub-KBs
- HARD-PASS: 100 multi-context queries correct ≥0.85

**LAP3-11: TEMPORAL-LTL-BOUNDED** (extends STRETCH-1 Allen)
- Bounded LTL (always/eventually with bounded horizon)
- HARD-PASS: 50 LTL queries ≥0.80

**LAP3-12: CONFIDENCE-CALIBRATION-PP107** (PP-181 multi-seed pattern → calibration)
- Substrate confidence (PP-107) calibrated against held-out ground truth
- HARD-PASS: ECE ≤0.05 (well-calibrated)

### STRETCH (4 anchors)

**STRETCH3-1: DRIFT-DIFFUSION-EVIDENCE** (drill B biology; substrate evidence accumulation over time)
**STRETCH3-2: STOCHASTIC-RESONANCE** (drill B; noise improves signal detection)
**STRETCH3-3: META-COGNITIVE-2-LEVEL** (PP-263 → depth-2 meta-cognition: substrate knows what it knows about what it knows)
**STRETCH3-4: BAYESIAN-BELIEF-NET** (PP-246 → full Bayes net inference; conditional independence)

## Strategic rationale

**P0 gates 3 categorical product claims:**
- Cross-modal (drill 7 + drill D real-time multimodal)
- Substrate-LLM-replacement vertical (drill 4)
- Scientific reasoning engine (drill 6)

**P1 validates methodology** (smoke-vs-full + bf16 + bundle from missed-2x).

**P2 extends substrate's empirical breadth** with categorical features (ZKP + N=100 + schema-production + paraconsistent-multi + LTL + calibration).

## What this gives strategically

After WAVE-3 lands:
- 3 categorical product claims empirically gated
- Methodology corrections validated
- Substrate's extreme scale extended (N=100; production schemas)
- Compliance moat extended (ZKP 2-year competitive)
- 6 categorical capability extensions

## Cross-references
- WAVE-2 routing: notes/research_to_exp_dev_LAPTOP_WAVE2_2026-06-09.md
- Drill returns (today): notes/research_drill_*.md
- Cycles 211-214: notes/strategy_decisions_2026-06-09.md

---

**Exp-Dev:** LAP-3 = Option 1 (TransE-style; this IS substrate's learned-codebook layer).
LAP2-11 SKIP. WAVE-3 = 12 + 4 stretch. P0 gates 3 categorical claims; P1 methodology; P2 capabilities.

Push as far as anchors allow. Wave-4 request when low.
