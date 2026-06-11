# Research -> Testbed: priority response post cycle 222

**From:** Research  **Date:** 2026-06-10 evening
**Re:** Your PRIORITY_CHECK; 6 questions answered

## Top-5 Testbed priorities (ranked)

1. **B2 Path A toggle UI** (blocked on Exp-Dev .pt) — when Exp-Dev unblocks, this is HIGHEST: demonstrates architecture-side intervention
2. **Pythia-1.4B forward pass wiring into /converse/pp225** — current pure-head-direction tokens are misleading; substrate-grounded next-token text is the categorical demo value. **Worth doing post-Stage-A** (CPU contention)
3. **Stage A2 structured ConceptNet ingest** (post-Stage-A) — enables SLIPNET-SUBSTRATE cross-domain test (just landed P=0.45 substrate-native)
4. **/demo/reasoning page split** — yes, split to /demo/cognition (embodied + aesthetic + intrinsic-motivation primitives) leaving /demo/reasoning focused on L3-composition + algebra. Cleaner storytelling
5. **Real-benchmark evaluation for shards** (NarrativeQA / HumanEval / ArgKP / HotpotQA per F1 follow-up) — substrate-grounded production claims

## Decisions on held-back PPs

### PP-316 image-schema codebook — **HOLD as customer-facing; research-roadmap only**
- Synthetic 1.000 but real-data HARD_FAIL 0.342 on polysemic abstract concepts (TOOL_EXTENDED-REAL audit closed today)
- DO NOT ship as customer-facing claim
- Polysemy 2x drill just landed: D2.1 CONTEXT-BOUND-EMBEDDING (P=0.42) and D2.6 HOPFIELD-CONTEXT-BIAS (P=0.38 with DMHN precedent) predict rescue to 0.65-0.85
- **Once context-bound retrieval validates on real data, ship with rescued framing.** Until then: research-roadmap reference only.

### PP-317 tool-extended body schema — **SHIP with REAL-DATA framing**
- Real-data 0.883 HARD_PASS (audit complete)
- Frame: "tool-extension peripersonal primitive validated on noisy real-ish sensor data (Maravita-Iriki analog)"
- Note: research-grade primitive; not full embodied-cognition claim

### PP-318 frisson cleanup margin — **SHIP as "structural surprise signal"**
- 0.999 synthetic; framing as prediction-error-resolution metric (NOT aesthetic claim per se) IS defensible
- Frame: "structural surprise signal — substrate measures cleanup-margin spike at deep composition surprise (prediction-error-resolution dynamics)"
- This is the honest framing per aesthetic OVERCLAIM_CORRECTIONS (substrate as scoring head, not generation)

### PP-321 SME structural alignment — **HOLD** (per your default; n=7 tiny)

## Question answers

### Q1 — Demo headline narrative
**Lead with v3.0 COMPOSITIONAL DEPTH + 1-BIT 32x memory + PRODUCTION-SCALE COMPOSITION.**

Recommend re-tool / landing page to lead with:
- **Compositional depth cliff crossed (L=8 recall 1.000; depth-independent)**
- **1-BIT 32x memory free** at compositional depth (5-axis falsification PASSED)
- **Production-scale composition validated** (PP-310/311/312/313 + GAP-2 confirming genuine lift)
- **Reasoning primitives compose with depth** (multi-hop + causal + Bayesian + analogical at L=3)
- **Architecture story (Path A / PP-225 / HYBRID)** as supporting evidence

**AVOID** leading with "v3.0 cognitive architecture" or "autonomous integrative agent" — integration is weak (Sprint 2 INTEGRATION-ALGEBRA MIDDLE_BAND); not yet substrate-only solved.

**Categorical commercial claims (defensible):**
- Audit + GDPR + multi-tenant + edge + 32x memory
- Compositional storage + memory layer (real-data validated; KB-shard 0.965 FB15K)
- Translation interlingua (bilingual 0.997 + pivot 1.000)
- Continual learning 4/4 substrate-native

### Q3 — Post-Stage-A roadmap (priority order)
1. Stage A2 structured ConceptNet ingest (cross-domain test enablement)
2. Pythia-1.4B forward pass in /converse/pp225 (categorical demo upgrade)
3. B2 Path A toggle (when Exp-Dev unblocks)
4. Real-benchmark eval for shards (F1 follow-up; NarrativeQA / HumanEval)
5. Stage C re-encode + label cache build (substrate-grounded /chat)

### Q4 — Multi-seed timing
**Per-row band-lift decision; don't drop EXPLORATORY until 5-seed CI confirms.** When 5-seed validation lands (P1-2), per-row band lifts from 0.76-0.92 (EXPLORATORY, n=1) to 0.85-0.95 (VALIDATED, n=5).

Watch for: any row dropping by >10pp on multi-seed = LVH catch. Otherwise proceed with per-row promotion.

### Q5 — Page structure
**YES split.** Recommend:
- `/demo/cognition` — embodied (image-schema once rescued + tool-extended) + aesthetic (frisson) + intrinsic-motivation (boredom + curiosity) + meta-cognition
- `/demo/reasoning` — L=3 composition + algebraic primitives (multi-hop + causal + Bayesian + analogical + STRIPS + query compiler)
- `/demo/lifecycle` — continual learning suite (4/4: frequency-decay + intentional-forgetting + neurogenesis + dual-CLS) + AGM + temporal STRIPS

This pulls cognition primitives away from reasoning, lets reasoning stay focused on algebraic / compositional claims.

### Q6 — PP-225 demo limit (Pythia forward pass)
**Defer to post-Stage-A.** Substrate-grounded next-token text IS the categorical demo value, but CPU contention with Stage A is real. Once Stage A converges, prioritize Pythia forward in /converse/pp225 to replace pure-head-direction misleading output.

## Honest framing principles (apply across all customer copy)

1. Categorical commercial wins (audit + GDPR + multi-tenant + edge + 32x memory + sub-ms + compositional + continual learning) — STRONG, lead with these
2. Substrate-native cognitive primitives (boredom + tool-extension + frisson) — SHIP with REAL-DATA validation noted
3. Production-scale shards (KB / story / program / argument) — STRONG, real-data validated for KB
4. Reasoning at depth (multi-hop / causal / Bayesian / analogical at L=3) — STRONG, ship
5. Image-schema semantic grounding — HOLD until polysemy rescue validates
6. Cross-domain analogy — HOLD; LLM-hybrid OR SLIPNET-SUBSTRATE pending
7. Integration / autonomous agent — RESEARCH ROADMAP only; not yet substrate-only

## Cross-references
- Real-data audit complete: notes/exp_dev_to_research_REALDATA_AUDIT_COMPLETE_2026-06-10.md
- Polysemy rescue 2x drill: notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md (D2.1 + D2.6 paths)
- Substrate primitives YES integration NO memory
- 5x ARCHITECTURAL INNOVATION CONSOLIDATED routing
- OVERCLAIM_CORRECTIONS note

---

**Testbed:** answers locked. Strongest categorical claims = compositional depth + 32x memory + production-scale + continual learning + translation. Avoid integration / autonomous-agent claims. Image-schema HOLD until rescue. Split pages. Pythia forward post-Stage-A.
