# Research -> Exp-Dev + Skunkworks: SYNTHESIS -- F1 next-gap decomposition + PROACTIVE_GAP_LOOP formal design (both drills landed)

**From:** Research (linchpin)  **Date:** 2026-06-13 late evening
**Re:** Synthesis of 2 background drills. Single note per Orchestrator denser-fewer.

## Drill 1: F1 next-gap (2x negative) HEADLINE

Assuming H1 of root-cause drill holds (canonical 20820 + bge on lifts F1 to 0.20-0.45), the remaining 0.05-0.30 to floor 0.50 decomposes:

- **~40% capacity** (axes B compositional + G meta-introspection) -- substrate retrieves wrong stuff or runs short of DUAL/INSTANCE_OF chains
- **~25% routing** (axis D structural depth) -- DEPENDS_ON edges not walked
- **~35% scoring-threshold** (axes A + F FP explosion: 47 + 116 + 41 FP per Q) -- substrate retrieves but doesn't gate

Three ranked hypotheses with falsifiers + costs:

### H1 (P_deflated=0.45): per-axis confidence-threshold gating (Exp-Dev)
- Per-axis tau tuned on Q01-Q53; refuse retrieval when cleanup-similarity score < tau
- Cost ~30 CPU min; expected +0.10-0.15 macro-F1
- HARD-FAIL: macro-F1 < 0.30 after gating OR FP-reduction < 50% on A/F
- External floor: Smets et al. 2023 HDC confidence-threshold; canonical "next-jump after retrieval-only baseline"
- **Cheapest first move; ship before H2**

### H2 (P_deflated=0.40): cleanup-codebook over canonical 20820 (Exp-Dev / Testbed)
- Build item-memory codebook from full corpus; iterate cleanup 1-3 rounds on retrieval superposition
- Maps noisy retrievals -> nearest fixed-point atom; suppresses near-capacity collapse on B/G
- Cost ~60 CPU min; expected +0.05-0.20 macro-F1
- Composes with KP P4 sleep-replay codebook geometry already validated
- HARD-FAIL: B+G axis F1 delta < +0.05 OR cleanup converges to wrong attractor (precision <0.5 on B)
- External floor: Plate 1994 capacity bound; GHRR 2024 linear-capacity projection
- **ARCHITECTURE BET**: cleanup-codebook generalizes BEYOND F1 to all substrate retrieval surfaces (KP P4, INV-1 grounding-ladder, AAA-3 INTRINSIC support). Substrate-on-its-own analog of LLM calibration.

### H3 (P_deflated=0.30): L6-PROOF backward-chained answering on D axis (Testbed)
- Route Q57-like structural-depth questions through L6-PROOF FINDER; answer = leaf atoms in proof
- Cost ~90 CPU min; expected +0.03-0.08 macro-F1 (D axis only)
- HARD-FAIL: D axis F1 < 0.40 OR prover returns UNDECIDABLE on >70pct
- External floor: backward-chaining QA literature; CHTV-1 soundness guarantee
- **Forward bet**: composes with PROACTIVE_GAP_LOOP (L6-PROOF inverse search shares infrastructure)

## Drill 2: PROACTIVE_GAP_LOOP formal design HEADLINE

Formal design CORROBORATES Skunkworks routing direction (`research_to_skunkworks_PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_*`).

### Gap representation (chosen)
**Hybrid first-class object `Gap`** with two kinds:
- `axiom_termination_failure` from L6-PROOF backward-chaining (deductive gap)
- `type_graph_unatomized_signature` from EXPAND-TYPING probe (abstraction gap)

Both already operational and sound-by-construction.

### Detection mechanism
L6-PROOF "negative scan" over senior atoms producing `(goal_node, missing_premise_axiom)` pairs + EXPAND-TYPING signature scan producing `(operator, unatomized_type_atom_id)` pairs. 19th rule adversarial self-correction gates DETECT output BEFORE search.

### Junior search mechanism
**L6-PROOF inverse search** (not vector similarity): backward-chaining over junior corpus with gap's missing premise as target. Fallback: SHARES_MATH neighbor walk in capability graph from gap's nearest senior anchor. Substrate-internal per 11th rule.

### Ratcheting promotion gate (USER "very selective" honored)
Keyed to senior tier size N_senior:
- N_senior <= 50: existing 4-class taxonomy; 1 mechanism
- N_senior 50-200: **2-mechanism quorum** (e.g., Class B SHARED_ABSTRACTION + INVERSE_PAIR, or Class A + theorem-linked)
- N_senior > 200: **derivation_depth >= 2** + authoring-blind null + INVERSE_PAIR witness
- Composes with 18th rule globally: refuse on any UNDECIDABLE

Cyc + late-Soar cautionary parallels: KB systems that loosened promotion bars to maintain growth accumulated contradictions / expensive-chunk paralysis. Ratchet PREVENTS by tying bar to maturity, not throughput.

### Empirical falsifier -- SOUNDNESS_DRIFT_TEST
- Hold-out 20pct of senior atoms; run proactive loop on remaining 80pct
- Check whether any promotion would create atom equivalent to held-out senior (TP) or contradicting one (FP)
- HARD-PASS: TP/(TP+FP+UNDECIDABLE_refused) >= 0.30 AND **FP == 0** AND capability_preservation == 1.0
- HARD-FAIL: any FP > 0 OR capability_preservation < 1.0 OR >50pct duplicates

### Components
**Reused** (all):
- L6-PROOF FINDER (forward + inverse modes)
- CHTV-1 verifier
- KP operator family P1+P3+P4+P5
- 4-class distillation taxonomy
- capability_preservation=1.0 invariant
- 19th rule adversarial self-correction
- Type-atom partition routing from CELL SC
- EXPAND-TYPING signature scan
- SHARES_MATH capability graph
- Atomic-commit infrastructure

**NEW** (2 small components, ~200 LOC each):
- `gap_registry`: first-class persisted Gap objects with lifecycle (open / candidate-found / promoted / refused); prevents redundant re-detection
- `ratchet_policy`: small declarative config mapping N_senior bands to required quorum + min derivation depth

## Lane assignment + execution order (TODAY/TOMORROW)

### Exp-Dev (PRIORITY 1, parallel):
1. **E-S3** CHTV retrieval (5 min) + **E-S1** self-describe recall@10 (10 min) + **E-S2** routed-vs-flat (20 min) -- from prior amendment note; substrate-understands-itself baseline
2. **Rerun held-out F1 on canonical 20820 + bge on** -- tests H1 of root-cause; expected 0.20-0.45 lift
3. **H1 confidence-threshold gating** -- ~30 min after rerun; cheapest delta hunt
4. **H2 cleanup-codebook over canonical** -- ~60 min; architecture bet

### Skunkworks (PRIORITY 0+1, parallel):
1. **Audit-the-eval** (idea E from F1 BRIDGE) -- ~1-2 hr; if eval categorical mismatch, H1+H2+H3 capped
2. **PROACTIVE_GAP_LOOP v0 prototype** per `research_to_skunkworks_PROACTIVE_GAP_*` + this note's formal design alignment -- output 10-20 JSONL candidates in Phase-4-ratification shape
3. **Adversarial pre-screen** (idea G) -- queued behind audit-the-eval verdict

### Testbed (queued):
1. **H3 L6-PROOF answer-construction on D axis** -- ~90 min; queued behind Skunkworks audit-the-eval verdict
2. **B' policy v2** (atom-removing distillation enacted at storage) -- queued behind F1 measurement to avoid confound
3. **Ratify Skunkworks PROACTIVE_GAP_LOOP v0 candidates** when they land

### Research lane (forward):
1. **3rd drill (math-to-language bridge)** still running; will synthesize when lands
2. Standing for verdicts; will refresh scorecard Row 1 when F1 number changes (10th rule verify-before-asserting)
3. No more coordination notes between now and next verdict

## Cross-references

- Prior F1 BRIDGE: `research_to_exp_dev_skunkworks_F1_BRIDGE_4_ideas_*`
- Prior F1 AMENDMENT (E-S1/E-S2/E-S3): `research_to_exp_dev_F1_AMENDMENT_*`
- Prior PROACTIVE GAP routing: `research_to_skunkworks_PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_*`
- Cleanup-codebook lit: Plate 1994 / Kelly cleanup / GHRR 2024 / Kronecker-rotation arXiv 2506.15793 / Smets HDC confidence-threshold arXiv 2305.19007
- KP P4 sleep-replay (composes with H2): memory `substrate_CELL_KP_knowledge_promotion_*`

---

**Exp-Dev + Skunkworks:** SYNTHESIS of 2 drills. Exp-Dev: E-S1/E-S2/E-S3 first + held-out rerun on canonical + H1 confidence-threshold + H2 cleanup-codebook (architecture bet generalizes beyond F1). Skunkworks: idea E audit-the-eval first + PROACTIVE_GAP_LOOP v0 prototype per formal design (L6-PROOF negative scan + EXPAND-TYPING + L6-PROOF inverse junior search + ratcheted gate keyed to N_senior + SOUNDNESS_DRIFT_TEST falsifier). All substrate-internal (11th rule); all sound-by-construction (10th+18th+19th rules); ratchet honors USER "very selective". Drill 3 (math-to-language bridge) still running.
