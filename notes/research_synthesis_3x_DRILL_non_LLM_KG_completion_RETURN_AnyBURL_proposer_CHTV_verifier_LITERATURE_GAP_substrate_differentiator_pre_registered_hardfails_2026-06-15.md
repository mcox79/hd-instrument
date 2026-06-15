# Research (Director) -- SYNTHESIS: 3x non-LLM KG completion drill RETURN; AnyBURL-style rule-based mining is literature-precedent proposer; CHTV-gated DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP loop is a GENUINE LITERATURE GAP (no published precedent); substrate-product differentiator territory; 5 pre-registered HARD-FAIL thresholds adopted for Phase 3; 5 substrate-defenses against documented NELL drift warnings

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~09:30
**Re:** 3x drill complete `notes/research_drill_REPORT_non_LLM_autonomous_KG_completion_rule_mining_pattern_ontology_learning_2026-06-15.md`. P_deflated = 0.42 (uncharted regime). Per USER strategic question + overnight full-auto + auto mode.

## Headline (compresses the drill)

The literature on non-LLM autonomous KG extension converges on a three-tier finding:

1. **Rule-based methods (AnyBURL, AMIE+, SAFRAN)** = best-precedent proposer with explicit per-rule confidence; INDUCTIVE (handles cold-start); precision >= 0.80 at top-100 with aggressive threshold tuning. Provides STATISTICAL confidence, NOT logical soundness.

2. **Embedding methods (TransE, RotatE, ComplEx)** = transductive by construction; FAIL cold-start by design; inductive variants (GraIL, NBFNet) recover some cold-start at 5-15 pct precision drop but require some local edges (truly isolated entities still fail).

3. **OpenIE / pattern-based (TextRunner, ReVerb, OpenIE 5/6, Hearst)** = extract triples without LLMs but plateau at ~0.65 precision with noisy relation labels; NELL (closest non-LLM closed-loop precedent) DRIFTS after 3-10 iterations without external grounding.

## THE LITERATURE GAP (substrate-product differentiator territory)

**NO published architecture matches DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP with CHTV-style sound verification.** Closest precedents:
- NELL (statistical confidence at every stage; drifts)
- NEIL (visual; same drift)
- Knowledge Vault (probabilistic prior, not logical verifier)
- DeepDive (Markov Logic; statistical)

**The substrate's CHTV verifier (logical termination as proposal gate) is a genuine literature gap, not re-invented prior art.** Combined with capability_preservation=1.0 invariant, the substrate has:
- Rule-based proposer (AnyBURL family)
- CHTV verifier (logical termination)
- Capability_preservation ratification gate

This is structurally STRONGER than NELL because CHTV is logical, not statistical agreement.

## DECISION 65a -- Substrate-product positioning UPDATE (7th claim)

Adding to the 6-claim package from DECISION 65:

**Claim 7 (Phase 3 architectural differentiator):** "Substrate's planned Phase 3 CO-EVOLVE-1 architecture pairs rule-based edge proposers (AnyBURL family analogue) with the CHTV verifier (logical termination) and capability_preservation=1.0 as ratification gate. This composition is a documented literature gap -- no published autonomous KG extension system (NELL, NEIL, Knowledge Vault, DeepDive) uses logical termination as the proposal gate. CHTV's refuse-derivation-free-edges rule is the structural defense against the documented NELL drift problem (semantic drift after self-bootstrapping iterations without external grounding)."

## 5 PRE-REGISTERED HARD-FAIL THRESHOLDS adopted for Phase 3 experiments

From drill Section 1+2 (Falsifiable predictions):

| HARD-FAIL Threshold | Trigger | Substrate Implication |
|---|---|---|
| HF-P1: Rule-based proposal precision | < 0.50 on cold-start with type-constrained rules | Rule mining inadequate for substrate's typed edges; pivot to pattern-based |
| HF-P2: Embedding cold-start recall | > 0.30 | Would refute the transductive-limit literature consensus; unexpected and worth deep investigation |
| HF-P3: Hearst-pattern precision over substrate corpora | < 0.30 | Pattern extraction captures syntax not semantics; drop pattern proposer |
| HF-P4: CHTV verifier acceptance on high-confidence rule proposals | < 10% OR >= 80% | <10% = proposer/verifier incompatible; >=80% = CHTV too lenient OR rule confidence well-calibrated to logical truth (novel; worth deep) |
| HF-P5: NELL-style multi-iteration drift in CO-EVOLVE-1 | verified-edge precision falls >= 15 pct in <= 5 iterations | Substrate drift confirmed; pause loop; investigate which CHTV defense failed |

These thresholds composed with the existing pre-registered HARD-FAIL thresholds from DECISION 56a (HF-1/HF-2/HF-3 generic-densification + question-conditional weighting + leakage gradient).

## 5 documented WARNINGS (NELL drift; literature) + 5 SUBSTRATE-DEFENSES

| Warning | Documented in | Substrate Defense |
|---|---|---|
| W1 Semantic drift after self-bootstrapping | NELL/NEIL | CHTV refuses derivation-free edges; drift cannot accumulate |
| W2 Over-coupling proposer/verifier shared signal | NELL | CHTV uses logical termination, structurally independent of proposer confidence |
| W3 Cold-start confidence mis-calibration | AnyBURL+AMIE | Typed-operator constraints filter most cold-start mis-calibration |
| W4 Open-world conflation (absence-by-design vs not-yet-observed) | KG completion | capability_preservation=1.0 makes "absence" structural, not statistical |
| W5 Iteration-induced narrowing (rewarded for easy edges) | NELL | METRIC-UP measures CAPABILITY gain not edge count; breaks easy-edge reward |

This is the substrate-product positioning's most fully-characterized architectural claim yet.

## Cross-thread synthesis (drill recognizes)

- Composes with M4d capability-graph walk: M4d already validated autonomous in-substrate walk mechanics (0.148 -> 0.272 in-distribution); CO-EVOLVE-1 extends this from "amplify in-distribution" to "grow new-concept neighborhoods"
- Composes with KP P1+P4 knowledge promotion: P1 frequency is statistically analogous to AnyBURL PCA; P4 sleep-replay codebook geometry is novel substrate primitive
- Composes with 3-distillation-modes taxonomy: rule-based methods only have atom-removing (threshold pruning); substrate's structure-adding + refusal modes are literature-missing

## Strategic implication (Phase 3 architecture clarified)

**Phase 3 CO-EVOLVE-1 dispatch spec (preliminary; awaiting 2x co-evolution drill + Skunkworks substrate-internal audit):**

```
LOOP CO-EVOLVE-1 (architecture):
  Proposer:  rule-based bottom-up mining (AnyBURL-style; precision-tuned >= 0.80)
             + inductive subgraph reranker (GraIL/NBFNet-analogue; cold-start)
             + Hearst-pattern extension over substrate-internal derivation corpora
  Verifier:  CHTV logical termination + L6-PROOF axiom-termination for DEPENDS_ON
             + capability_preservation=1.0 invariant gate
  Integration: atomic ratify via Testbed; rollback on capability regression
  Metric:    M4d F1 delta on rotating held-out (56d-v2 first; future v3+)
  Stop conditions: METRIC-UP saturates AND CHTV acceptance falls below threshold
  Drift defense: per-iteration audit comparing iteration-N vs iteration-1 substrate
                 (Skunkworks Auditor; rolls back if precision drops 15pct)
```

**Pre-registered HARD-FAIL gates** apply to every iteration. Substrate refuses to extend itself unsoundly.

## Phase 3 dispatch dependency tree (status check)

```
PHASE 3 DISPATCH PREREQS:
  3x non-LLM KG completion drill        DONE (this synthesis)
  2x co-evolution architecture drill    IN FLIGHT (ETA ~15-30 min)
  Skunkworks edge-proposal primitives audit  IN FLIGHT (ETA ~2-3 hrs)
  
PHASE 3 DISPATCH BLOCKER (lifts when above 3 land):
  Synthesize final architecture spec    Director (after all 3 inputs)
  Estimate cost + risk                  Director (after architecture)
  Dispatch initial loop (small scope)   Exp-Dev (1-2 iterations to start)
```

## Next-drill candidate (drill identified; logging for future)

The 3x drill flagged the next high-leverage drill: "inductive embedding x CHTV verifier composability" -- cheap CPU study to confirm subgraph-reasoning ranks can be plumbed through CHTV without breaking soundness. Worth dispatching AFTER Phase 3 initial loop runs, IF inductive embedding becomes part of the architecture.

## Session tally

65 cumulative decisions. 40 honest signals. 1 major literature drill returned with substrate-product-differentiator finding. 7th canonical substrate-product positioning claim adopted. Phase 3 architecture preliminarily specified.

## Cross-references

- 3x drill report: `notes/research_drill_REPORT_non_LLM_autonomous_KG_completion_rule_mining_pattern_ontology_learning_2026-06-15.md`
- DECISION 65 (Phase 2 close): commit `cc294b83`
- DECISION 64 (55a reframe + 6-claim package): commit `d37b210a`
- Phase 3 design cell + drills dispatch: commit `76302db1`

## Safety / invariants

- ASCII only
- 11th rule (substrate-on-its-own): Phase 3 architecture explicitly excludes LLM
- 18th rule: CHTV verifier IS the substrate's 18th-rule embodiment for autonomous extension
- 19th rule: pre-registered drift detection (HF-P5)
- 22nd rule preserved

---

**No new dispatches.** Awaiting 2x co-evolution drill + Skunkworks edge-proposal audit. Phase 3 dispatch synthesis arrives when all 3 outputs land.

Tag: 3x_DRILL_RETURN_ANY_BURL_PROPOSER_CHTV_VERIFIER_LIT_GAP_SUBSTRATE_DIFFERENTIATOR -- Research (Director)
