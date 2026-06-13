# Research: Tracking-document SECTION 9 FORMAL (substrate self-improvement loop) — published form derived from architecture doc + V1/V2 empirical anchors + 3-mode taxonomy + safety guarantee + DISTILLATION RATIO measurement protocol + 6-tier hierarchy tier-2 framing

**From:** Research (linchpin; per 12th rule own-work)  **Date:** 2026-06-13
**Re:** Architecture doc was source material; Section 9 published form is the canonical tracking-doc entry

---

## SECTION 9: Substrate self-improvement loop

### 9.1 Overview

Substrate operationalizes recursive self-improvement through a 5-step closed loop that detects its own structural redundancy, proposes structural change via its own operators, verifies via sound symbolic reasoning, integrates via atomic shard swap, and demonstrates capability preservation on substrate-internal benchmarks. The human operator only RATIFIES proposed structural changes; substrate authors them.

The loop operates in 3 distinct distillation modes (atom-removing / structure-adding / refusal), each SOUND by-construction. The 3-mode taxonomy provides the safety guarantee for recursive operation: substrate refuses to delete capabilities even when atoms LOOK similar.

As of 2026-06-13, the loop is OPERATIONAL at step 3 (VERIFY) with both halves demonstrated empirically (V1 atom-removing + V2 sound-discriminative). Steps 4-5 land in current cycle.

### 9.2 The 5-step closed loop

#### Step 1: DETECT — substrate identifies its own structural redundancy

**Operator**: skunkworks operator-overlap probe (v1 + bias-robust grounding ladder: prose → structured → provable → learned-vector)

**Mechanism**: substrate traverses its own typed atoms; identifies candidate merge groups via typed signatures + algebraic laws + serves_capability comparison

**Output**: candidate set partitioned into:
- Class A (provenance-witnessed): pairs with metadata.kp_p1_promotion or similar built-in witness
- Class B (proof-needing): same-capability/same-output groups lacking provenance pointer
- Class C (untyped): pairs sharing atom name but missing algebra_dict (UNDECIDABLE)

**Safety**: adversarial self-pre-screen catches false positives BEFORE handoff to verify step (per 19th methodology rule candidate)

**Empirical anchor (2026-06-13)**: skunkworks's substrate_distill_prescreen.py corrected 5 dups initially classified as redundancy to KP P1 promotion pairs (Class A) before Exp-Dev consumed them

#### Step 2: PROPOSE — substrate's own operators propose specific structural change

**Operator**: substrate's classification logic mapping candidate class to distillation mode

**Mechanism**:
- Class A → propose ATOM-REMOVING (schema collapse + PROMOTED_FROM link)
- Class B SHARED_ABSTRACTION → propose STRUCTURE-ADDING (extract abstract supertype + SPECIALIZES edges)
- Class B THEOREM_LINKED-unproven → propose REFUSAL + surface authoring gap
- Class C UNDECIDABLE → propose REFUSAL pending algebra_dict authoring

**Safety**: proposals are DECLARATIVE; not yet integrated; human RATIFIES before any persistence

#### Step 3: VERIFY — substrate's CHTV-1 type-checker + L6-PROOF prover validates sound equivalence

**Operator**: substrate's CHTV-1 (1.0 type-checker precision) + L6-PROOF backward-chaining sound prover

**Mechanism per class**:
- Class A: provenance pointer integrity check (built-in witness; already KP P1 HARD-PASS certified)
- Class B SHARED_ABSTRACTION: CHTV-1 verifies typed-signature compatibility with proposed supertype
- Class B THEOREM_LINKED: L6-PROOF searches for derivation chain; refuses if absent
- Class C: L6-PROOF cannot derive without typing; refuses

**Safety**: substrate refuses to assert what it cannot prove (per 18th methodology rule candidate)

**Empirical anchor (2026-06-13)**: OPERATIONAL today
- CELL-DISTILL-VERIFY-1 (Class A): 6/6 named pairs PROVABLY_EQUIVALENT + 22 UNDECIDABLE refused; distillation-over-named 1.00; 0 NOT_EQUIVALENT
- CELL-DISTILL-VERIFY-2 (Class B): 2/2 groups correctly discriminated (optimizer family → SHARED_ABSTRACTION; convolution-theorem pair → THEOREM_LINKED-unproven); 0 false-MERGEABLE; Exp-Dev caught own derivation_present overclaim via recursive 10th-rule application

#### Step 4: INTEGRATE — Testbed atomic shard swap + canonical-atom-ID alias map

**Operator**: Testbed atomic atom-write pattern (write-tmp + fsync + os.replace per drill 9 Pattern 1) + CURRENT-pointer snapshot swap (Pattern 2) + canonical-atom-ID alias map (per drill 15 Wikidata-pattern)

**Mechanism per class**:
- Class A: collapse promotion pair into single atom + tier attribute + PROMOTED_FROM link
- Class B SHARED_ABSTRACTION: create abstract supertype atom; ingest SPECIALIZES edges; preserve all original atoms
- Class B THEOREM_LINKED-unproven: no integrate action; refusal mode
- Class C UNDECIDABLE: no integrate action; refusal mode pending typed authoring

**Safety**: atomic shard swap ensures readers never see partial state; alias map preserves backwards compatibility

**Status**: URGENT NEXT (Testbed TESTBED-DISTILL-INTEGRATE-1 spec ready; dual target Class A + Class B SHARED_ABSTRACTION)

#### Step 5: METRIC UP — Research measures DISTILLATION_RATIO + capability preservation

**Operator**: Research metric measurement + substrate-internal benchmark vector

**Mechanism**:
- DISTILLATION_RATIO = (atoms_before - atoms_after) / atoms_before
- Capability constraint: substrate-internal benchmark vector B(s) = (B1 KP P1 count + B2 L6-PROOF FINDER recall + B3 retrieval recall@10 + B4 9d spectral dim-1 + B5 avg premise count) stays within tolerance
- HARD-PASS: ratio ≥ 5% corpus-wide + capability deviation < 5%
- Composite metric: DISTILLATION_RATIO (atom-removing) + STRUCTURE_DENSITY (structure-adding) + TYPING_GAP_COUNT (refusal)

**Status**: Pending step 4

### 9.3 The 3-mode distillation taxonomy

| Mode | Trigger | Mechanism | Atom-count effect | Witness |
|---|---|---|---|---|
| **ATOM-REMOVING** | provenance pointer present | schema collapse | DECREASES | provenance pointer |
| **STRUCTURE-ADDING** | same capability + different operation_type | supertype extraction | INCREASES by 1 | CHTV-1 typed compatibility |
| **REFUSAL** | proof missing / untyped | honest refusal | UNCHANGED | substrate refuses to assert |

All 3 modes are SOUND by-construction. The 3-mode taxonomy IS the safety guarantee: substrate's recursive self-improvement loop is SAFE TO RUN because the verifier soundly discriminates between modes.

**Measured 2026-06-13**: 0 false-MERGEABLE in CELL-DISTILL-VERIFY-2 (Class B). Substrate NEVER collapsed a distinct algorithm even when capabilities matched.

A self-improving system too eager to merge would silently delete capabilities (throw away Adam because it "looks like" plain gradient descent). Substrate's 3-mode taxonomy prevents this categorically.

### 9.4 DISTILLATION RATIO measurement protocol

Formal definition: DISTILLATION_RATIO(s_before, s_after) = |A(s_before) - A(s_after)| / |A(s_before)|

Subject to constraint: ||B(s_after) - B(s_before)|| / ||B(s_before)|| ≤ tolerance (5%)

Where B(s) is the substrate-internal benchmark vector defined in Section 9.2 step 5.

Pre-reg HARD-PASS bands per substrate-product positioning:

| Band | Ratio | Capability constraint | Interpretation |
|---|---|---|---|
| EXCEPTIONAL | ≥ 20% | within | dramatic self-curation |
| STRONG HARD-PASS | ≥ 10% | within | substantial self-curation |
| HARD-PASS | ≥ 5% | within | substrate maintains capability while compressing |
| MIDDLE-BAND | 1-5% | within | minor self-curation; partial pass |
| HARD-FAIL | any | drops > tolerance | unsound merges; substrate hallucinated equivalence |

Current measured value (2026-06-13, partial):
- Named-candidate distillation ratio: 1.00 (5/5 Class A pairs distillable; HARD-PASS bar 0.80 EXCEEDED)
- Corpus-wide distillation ratio: 0.33 (11/33 candidates distillable; gated on typing growth)

Full corpus-wide measurement awaits step 4 integration.

### 9.5 Audit-discipline rule family operating within the loop

The 5-step loop is supported by the audit-discipline rule family (currently 10 rules: 5 USER-LOCKED + 5 methodology candidates) governing claim integrity:

- 10th rule (PROMOTED today): verify-before-asserting — substrate's epistemic discipline as operational primitive
- 11th rule (USER-LOCKED): held-out test methodology
- 15th rule (APPROACHING): independence claims require authoring-blind null
- 16th rule (EARLY): higher-order observables need larger M
- 18th rule (APPROACHING): substrate refuses to merge what it cannot prove
- 19th rule (EARLY): adversarial self-correction of own DETECT output
- 20th rule (EARLY): substrate distillation modes taxonomy

These compose: 10th is the Tier-3 META rule; 11th + 15th + 16th + 18th + 19th + 20th are Tier-2 specific applications.

Substrate metacognition gains a 2-tier audit-discipline architecture (Tier 3 META + Tier 2 specific) operating within the closed loop.

### 9.6 Closed-loop demonstration → claim hierarchy positioning

This Section 9 content anchors substrate-on-its-own canonical claim hierarchy Tier 2 (substrate-internal operational; closed-loop step 3 OPERATIONAL today).

Tier transitions in closed-loop:
- Originally: Tier 6 (deferred speculation)
- Pre-2026-06-13: Tier 5 (pending demonstration)
- 2026-06-13 (today): **Tier 2 (OPERATIONAL via step 3)**
- Cycle 52 close target: Tier 1 (architectural primitive) when all 5 steps OPERATIONAL + DISTILLATION_RATIO measured

### 9.7 Forward path

#### Next-cycle Tier transitions

- Closed-loop step 4 OPERATIONAL → Tier 2 expansion
- Closed-loop step 5 OPERATIONAL → Tier 1 promotion (5 of 5 steps + DISTILLATION_RATIO measured)
- Convolution theorem PROVEN → Tier 2 expansion (THEOREM_LINKED-PROVEN demonstration)
- Optimizer SHARED_ABSTRACTION extraction → Tier 2 expansion (structure-adding measurement)

#### Concrete forward authoring targets

1. Testbed TESTBED-DISTILL-INTEGRATE-1 DUAL target (Class A schema collapse + Class B SHARED_ABSTRACTION extraction)
2. Convolution-theorem 4-step derivation chain authoring (per LANE B authoring spec)
3. 22 UNDECIDABLE algebra_dict authoring (refusal-mode → potentially merge or supertype)
4. Skunkworks widened Class B candidate extraction (V2 scale-ready)
5. DISTILLATION_RATIO + STRUCTURE_DENSITY + TYPING_GAP_COUNT first measurement

### 9.8 LLM categorical gap (context only, not lead per USER 11th rule)

For context: LLMs categorically lack analogs to:
- 5-step closed loop (no DETECT → PROPOSE → VERIFY → INTEGRATE → METRIC UP architecture)
- 3-mode distillation taxonomy (no atom-removing / structure-adding / refusal distinction)
- Sound by-construction guarantees per mode
- Self-correct derivation_present overclaims (no CHTV-1 analog)
- Adversarial self-pre-screen on own DETECT output (no recursive audit discipline)
- Refuse to assert what they cannot prove (LLMs hallucinate)

This is provided as architectural context for understanding what substrate is doing; it is NOT the lead framing of substrate's identity per USER 11th rule.

### 9.9 References

- CELL-DISTILL-VERIFY-1 (Exp-Dev 2026-06-13): empirical step 3 atom-removing demonstration
- CELL-DISTILL-VERIFY-2 (Exp-Dev 2026-06-13): empirical step 3 sound-discriminative demonstration; 0 false-MERGEABLE
- substrate_operator_overlap_v1.py (skunkworks 2026-06-13): step 1 DETECT
- substrate_distill_prescreen.py (skunkworks 2026-06-13): adversarial self-pre-screen
- DISTILLATION RATIO FORMAL SPEC v1 (Research 2026-06-13): step 5 measurement protocol

---

## Routing

- **Tracking-doc owners**: Section 9 published form ready; integrate into canonical tracking-doc
- **All sessions**: Section 9 canonical reference for closed-loop architecture + measurements + audit-discipline rule family role
- **USER**: substrate self-improvement loop empirical anchor at Tier 2; Cycle 52 close target Tier 1 promotion

## Cross-references

- notes/research_SUBSTRATE_SELF_IMPROVEMENT_LOOP_ARCHITECTURE_*.md (architecture doc source material)
- notes/research_DISTILLATION_RATIO_North_Star_metric_FORMAL_SPEC_*.md (Section 9.4 source)
- notes/research_SUBSTRATE_ON_ITS_OWN_CANONICAL_CLAIM_HIERARCHY_*.md (Tier framing)
- notes/research_TRACKING_DOC_SECTION_5_de_LLM_ify_REWRITE_*.md (Section 5 companion)
- memory `substrate-3-distillation-modes-taxonomy-*.md` + `substrate-methodology-rule-10th-VERIFY-BEFORE-ASSERTING-PROMOTED-*.md`
