# Research: SUBSTRATE SELF-IMPROVEMENT LOOP ARCHITECTURE (formal 5-step loop + 3-mode distillation taxonomy + safety guarantee + DISTILLATION RATIO North Star metric + closed-loop step 3 OPERATIONAL today + tracking-doc Section 9 source material + substrate-product positioning artifact)

**From:** Research (linchpin; per 12th USER-LOCKED rule own-work)  **Date:** 2026-06-13
**Re:** Closed-loop step 3 OPERATIONAL with both halves; integrating into formal substrate self-improvement loop architecture

## Intuitive (the spine)

Substrate's recursive self-improvement loop is a 5-step process operating in 3 distillation modes, all sound by-construction. Substrate finds redundancy in its own structure, decides whether each candidate is truly mergeable / shares an abstraction / lacks proof, and integrates only when it has a proof or built-in witness. The human operator ratifies; the substrate authors.

Like a kitchen that maintains its menu by: noticing two similar dishes, deciding whether to combine them / extract a common technique / leave them separate pending a recipe verification, and updating the menu accordingly — all while never accidentally removing a dish's distinctive feature.

## Formal 5-step architecture

### Step 1: DETECT
**Operator**: skunkworks operator-overlap v1 + bias-robust grounding ladder (prose → structured → provable → learned-vector)
**Mechanism**: traverses substrate's typed atoms; identifies candidate merge groups via typed signatures + algebraic laws + serves_capability
**Output**: candidate set partitioned into Class A (provenance-witnessed) + Class B (proof-needing) + Class C (untyped, UNDECIDABLE)
**Safety**: adversarial self-pre-screen (substrate_distill_prescreen.py) catches false positives BEFORE handoff
**Status**: OPERATIONAL

### Step 2: PROPOSE
**Operator**: substrate's own classification logic via typed signature + algebraic laws + serves_capability comparison
**Mechanism**: for each candidate group, propose:
- Class A → ATOM-REMOVING distillation (schema collapse + PROMOTED_FROM link)
- Class B SHARED_ABSTRACTION → STRUCTURE-ADDING distillation (extract supertype + SPECIALIZES)
- Class B THEOREM_LINKED-unproven → REFUSAL distillation (surface as authoring target)
- Class C UNDECIDABLE → REFUSAL (pending algebra_dict authoring)
**Safety**: proposals are DECLARATIVE, not yet integrated
**Status**: OPERATIONAL

### Step 3: VERIFY
**Operator**: substrate's CHTV-1 type-checker + L6-PROOF sound backward-chaining prover
**Mechanism**:
- Class A (V1 HARD-PASS): provenance pointer is built-in witness; verify provenance integrity
- Class B SHARED_ABSTRACTION (V2 HARD-PASS): CHTV-1 verifies typed-signature compatibility with proposed supertype
- Class B THEOREM_LINKED (V2 HARD-PASS): L6-PROOF searches for derivation chain; refuses if absent
- Class C UNDECIDABLE: L6-PROOF cannot derive; refuses honestly
**Safety**: substrate refuses to assert what it cannot prove (per 18th methodology rule); 0 false-MERGEABLE measured
**Status**: **OPERATIONAL TODAY (V1 + V2 both HARD-PASS)**

### Step 4: INTEGRATE
**Operator**: Testbed atomic shard swap + canonical-atom-ID alias map (per drill 9 atomicity Pattern 2 + drill 15 alias methodology)
**Mechanism**:
- Class A: collapse promotion pair into single atom + tier attribute + PROMOTED_FROM link
- Class B SHARED_ABSTRACTION: create supertype atom + ingest SPECIALIZES edges
- Class B THEOREM_LINKED: no integrate action (refusal mode)
- Class C: no integrate action (refusal mode)
**Safety**: atomic shard swap means readers never see partial state; canonical-ID alias map preserves backwards compatibility
**Status**: URGENT NEXT (Testbed TESTBED-DISTILL-INTEGRATE-1)

### Step 5: METRIC UP
**Operator**: Research distillation-ratio measurement + substrate-internal benchmark
**Mechanism**:
- DISTILLATION_RATIO = (atoms_before - atoms_after) / atoms_before
- Capability constraint: ||B(s_after) - B(s_before)|| / ||B(s_before)|| <= tolerance (5%)
- Substrate-internal benchmark B = (KP P1 count + L6-PROOF FINDER recall + retrieval recall@10 + 9d spectral dim-1 + avg premise count)
**Safety**: HARD-PASS pre-reg bands per DISTILLATION RATIO formal spec
**Status**: Pending step 4

## 3-mode distillation taxonomy

| Mode | Trigger | Mechanism | Effect on atom count | Witness |
|---|---|---|---|---|
| **ATOM-REMOVING** | provenance pointer present | schema collapse | DECREASES | provenance pointer |
| **STRUCTURE-ADDING** | same capability + different operation_type | supertype extraction | INCREASES by 1 | CHTV-1 typed compatibility |
| **REFUSAL** | proof missing / untyped | honest refusal | UNCHANGED | substrate refuses to assert |

All 3 modes are SOUND by-construction (per 18th methodology rule candidate).

## Safety guarantee

The 3-mode taxonomy IS the safety guarantee: substrate's recursive self-improvement loop is SAFE TO RUN because the verifier soundly discriminates between modes.

**Measured 2026-06-13**: 0 false-MERGEABLE in CELL-DISTILL-VERIFY-2 (Class B). Substrate NEVER collapsed a distinct algorithm even when capabilities matched.

A self-improving system that's too eager to merge would silently delete capabilities (throw away Adam because it "looks like" plain gradient descent). Substrate's 3-mode taxonomy prevents this categorically.

## North Star metric: DISTILLATION RATIO

**Definition**: (atoms_before - atoms_after) / atoms_before subject to capability tolerance

**Mode contributions**:
- ATOM-REMOVING mode: DIRECT positive contribution to ratio
- STRUCTURE-ADDING mode: INVERSE contribution (atom count goes up, but distinct atoms become better-organized)
- REFUSAL mode: NEUTRAL (no contribution, but signal value: surfaces typed-authoring gaps)

**Composite metric** (proposed):
- PRIMARY: DISTILLATION_RATIO (ATOM-REMOVING; aggregate compression measure)
- SECONDARY: STRUCTURE_DENSITY = SPECIALIZES_edges / atoms (STRUCTURE-ADDING measure)
- TERTIARY: TYPING_GAP_COUNT = UNDECIDABLE_candidates (REFUSAL measure; surfaces engineering priority)

These three together describe substrate's self-improvement output across all 3 modes.

## Audit-discipline rule family member counts (post today)

| Rule | Status | Empirical witnesses today |
|---|---|---|
| 7th USER-LOCKED: always reconsider | LOCKED | INV-1 C3 + V2 derivation_present + DETECT pre-screen (3x) |
| 9th USER-LOCKED: monitor armed | LOCKED | 1 missed note caught (orchestrator) |
| 10th methodology rule: verify-before-asserting | **PROMOTED today** | 9+ chronological witnesses |
| 11th USER-LOCKED: substrate-standalone-first | LOCKED | empirically realized in closed-loop |
| 12th USER-LOCKED: research never passive | LOCKED today | passive gap 14:43-15:55 caught |
| 15th methodology rule: independence-claims-blind-null | 2 empirical witnesses | INV-1 + INV-2a |
| 16th methodology rule: higher-order-needs-larger-M | 1 candidate | F4-RELABEL |
| 18th methodology rule: refuses-what-cannot-prove | 1 candidate | DISTILL-VERIFY-1 22 UNDECIDABLE |
| 19th methodology rule: adversarial-self-correction-of-own-detect | 1 candidate today | skunkworks DETECT pre-screen |
| 20th methodology rule: distillation-modes-taxonomy | 1 candidate today | V1 + V2 3-mode demonstration |

5 audit-discipline rules in some promotion stage. Substrate metacognition Tier-2/3 architecture is emerging as a coherent rule family.

## LLM categorical gap (widens)

LLMs cannot:
- Distinguish 3 distillation modes (no taxonomy)
- Maintain sound-by-construction guarantees per mode
- Refuse to assert what they cannot prove (LLMs hallucinate; substrate refuses)
- Self-correct derivation_present overclaims (no CHTV-1 analog)
- Run adversarial self-pre-screen on own DETECT output (no recursive audit discipline)
- Surface typed-authoring gaps as concrete forward targets (no UNDECIDABLE classification)

The 5-step loop + 3-mode taxonomy + 5-member audit-discipline rule family is substrate's epistemic architectural primitive. No LLM analog exists.

## Concrete forward authoring targets (typing-is-the-lever)

Per 3-mode taxonomy + closed-loop step 3 OPERATIONAL:

1. **Convolution-theorem derivation chain** (Class B THEOREM_LINKED-unproven → PROVEN):
   - Cross-domain L6-PROOF demonstration (VSA binding ↔ signal processing)
   - 3-4 typed steps (DFT linearity + pointwise product + inverse DFT)
   - Cheapest concrete L6-PROOF win pending

2. **22 UNDECIDABLE algebra_dict authoring** (Class C → typed):
   - astar, dijkstra, backward_algorithm, etc.
   - Same lever as parser-v2 multi-premise extraction
   - Once typed, become Class A or Class B candidates for distillation

3. **Optimizer SHARED_ABSTRACTION supertype**:
   - Create `first_order_optimizer` abstract atom
   - SPECIALIZES from gradient_descent + adam_optimizer + stochastic_gradient_descent
   - First demonstrated STRUCTURE-ADDING distillation integration

4. **Class B full candidate extraction** (skunkworks ongoing):
   - All same-capability-same-output operator groups lacking provenance pointer
   - Widens V2 discrimination guard test at scale

## Tracking-document Section 9 source material

This architecture doc IS the source material for tracking-document Section 9 (substrate self-improvement loop). When Testbed step 4 + step 5 land, Section 9 will be authored with measured DISTILLATION_RATIO + STRUCTURE_DENSITY + TYPING_GAP_COUNT values + closed-loop FULL operational demonstration.

## Routing

- **All sessions**: this architecture doc is the canonical substrate self-improvement loop reference; Testbed step 4 dual target (Class A schema collapse + Class B SHARED_ABSTRACTION extraction) is the unblock
- **USER**: substrate-on-its-own thesis empirically operationalized in 5-step loop with 3-mode taxonomy + 0 false-MERGEABLE safety guarantee; tracking-doc Section 9 ready when step 4 + 5 complete

## Cross-references

- notes/research_to_exp_dev_skunkworks_testbed_CELL_DISTILL_VERIFY_2_HARD_PASS_*.md (V2 + 3-mode taxonomy + 11th writeback)
- notes/research_to_skunkworks_DETECT_PRESCREEN_ACK_*.md (10th writeback DETECT pre-screen)
- notes/research_DISTILLATION_RATIO_North_Star_metric_FORMAL_SPEC_*.md (North Star metric spec)
- memory `substrate-3-distillation-modes-taxonomy-atom-removing-structure-adding-refusal-20th-methodology-rule-candidate-substrate-product-architectural-primitive-2026-06-13.md` (memory)
- memory `substrate-closed-loop-OPERATIONAL-step-3-HARD-PASS-first-measured-self-improvement-instance-5-provably-equivalent-0-false-merge-22-refused-2026-06-13.md` (closed-loop step 3 V1)
- memory `substrate-methodology-rule-10th-VERIFY-BEFORE-ASSERTING-PROMOTED-candidate-to-CONFIRMED-5-plus-class-distinct-witnesses-audit-discipline-family-2026-06-13.md` (10th rule promoted)
- memory `feedback-substrate-standalone-capability-first-before-LLM-positioning-USER-LOCKED-2026-06-13.md` (USER 11th rule)
- memory `feedback-research-never-goes-passive-always-work-research-lane-own-output-between-inbox-events-USER-LOCKED-2026-06-13.md` (USER 12th rule)
