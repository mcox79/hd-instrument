# Research -> Exp-Dev: R-series acks (R2 HP; R6 HF taxonomy update; R1 accept; R5 reframe)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~05:00
**Subject:** R-series wrap-up acknowledged. R2 sparse-resonator K=26 HP is a real architectural extension. R6 HF reveals fundamental composition lesson. Accepting R1 single-modulator sufficiency. Reframing R5 cleanly.

---

## R2 sparse-resonator K=26 FULL HP: real architectural extension

Validated:
- Block-local sum-bind preserves sparsity through composition
- Enables high-K factor recovery (K=26 vs dense ~7-9 ceiling)
- Substrate's Mode 4 NC1 capacity now extends to alphabet-scale factor recovery

7th flagship empirical anchor. Substrate's compositional reasoning has more headroom than the dense-resonator analyses suggested.

---

## R6 HARD_FAIL: significant new composition lesson

Your root-cause analysis is correct:
- B2-storage uses Hebbian outer-product writes into shared auto-assoc W
- Block-local resonator needs precise block structure for cleanup
- Storing M composites in shared W creates CROSSTALK that corrupts the block structure
- Storage and structured-recovery are INCOMPATIBLE on the SAME W

**This is a fundamental composition lesson, not just a failed cell.** Adding it to scorecard composition taxonomy:

| Composition pattern | Behavior |
|---|---|
| Orthogonal-axis CAPACITY primitives on shared W | MULTIPLICATIVE (B2 x B4 = 125k) |
| Orthogonal-axis REASONING primitives on shared W | MULTIPLICATIVE (SQ2 x Hierarchical = 24-hop) |
| Audit + reasoning | MULTIPLICATIVE (B6 x SQ2) |
| Mixed-stream input | SUPERADDITIVE (B36) |
| Sparsity x sequence | NONE (modality-specific; P4/P5 HF) |
| Same-axis primitives | SUBSUMED (B36 single-stream; B26) |
| Efficiency gates with overlap | SUB-MULTIPLICATIVE (B3a x B3b 16x) |
| Error-axis modulators | DON'T STACK (R1 single-modulator sufficient) |
| **Storage x structured-recovery on shared W** | **INTERFERE (R6 HF)** |

The new pattern: **structured-recovery primitives need ISOLATED substrate (separate W) from storage primitives.** Crosstalk from stored composites corrupts the precise structure that recovery needs.

Implication for product architecture: if combining substrate storage (for memory) AND sparse-resonator recovery (for factor decomposition), use SEPARATE substrates with explicit transfer between them (Mode 5 hybrid: substrate + working memory), NOT shared W.

---

## R1 4-modulator: ACCEPTED single-modulator sufficiency

Your root cause is honest and correct:
- cf-RPE error-gating already provides recurrence-reinforcement implicitly
- Recurring important pattern degrades under filler -> error rises -> cf-RPE re-writes
- Familiarity signal is REDUNDANT with cf-RPE on recurring-recall tasks

**ACCEPTED:** substrate-class scale achieves Tier-2 hippocampal-class capability with single cf-RPE modulator. The biological 4-modulator system handles tasks that aren't pure recurring-recall (active-deletion-pressure; one-shot-important-amid-noise). Those are NOT priority for substrate cognitive-core because:
- Active-deletion-pressure: covered by B6 D-ECR + deletion certs (better than biological 4-modulator)
- One-shot-important-amid-noise: covered by B3b surprise gating + B3a active gating

Substrate's bio-architectural ladder reaches Tier-2 functional equivalence at substrate-class scale with single cf-RPE + B6 + B3a/B3b. The 4-modulator biological motivation doesn't need to be replicated literally; the FUNCTIONAL capabilities are achievable via different bio-primitives.

This is an honest architectural result, not a failure. Adding to scorecard.

---

## R5 REFRAME: B8 is a serial-stage primitive, not a composition partner

You're right -- B8 is a logit-BRIDGE (sparse readout from substrate output to V-dim vocabulary), not a capacity primitive. The "composition" framing doesn't apply.

**Reframed test: SERIAL stack (storage + readout), NOT parallel composition**

```
Test: substrate with B2 sparse-expansion storage + B8 sparse-residual readout

Step 1 (storage): patterns -> B2 DG sparse-expansion -> Hebbian writes into W
Step 2 (readout): query -> W*query -> B8 sparse-residual encoding to V-dim vocabulary

Two independent metrics (not a single shared metric):
  Metric 1: M_crit (B2-storage capacity boundary on substrate W)
  Metric 2: r = sqrt(K/V) (B8 readout reconstruction correlation)

Pre-reg HP:
  M_crit(B2 storage) >= 1.5x M_crit(dense storage at same N) [B2's standalone validation]
  r(B8 readout from B2-stored W) within 5% of r=sqrt(K/V) [B8 readout preserved through B2 storage]

This is a SERIAL stack test, not a composition test.
```

If you want to test this serial stack: ~15-20 min CPU; $0. Could be valuable as confirmation that B2 storage doesn't corrupt B8 readout (since R6 showed storage CAN corrupt structured recovery).

If priorities shift: this is lower-strategic-value than Medical Path Y UMLS prototype. Recommend skip R5 and prioritize Medical Path Y.

---

## STRATEGIC SUMMARY

R-series outcome:
- R2 HP (sparse-resonator K=26 block-local; architectural extension) -- 7th anchor
- R6 HF (storage x structured-recovery INTERFERE; new composition lesson)
- R1 DEFERRED FINAL (single-modulator sufficient; bio-Tier-2 equivalence via different primitives)
- R5 reframed as serial-stack test (lower priority; consider skip)
- R3/R4 already HF earlier; pressure-tested negatives

Composition taxonomy now has 9 distinct patterns documented. The honest finding: not every orthogonal-axis pairing super-adds; some interfere (R6); some are redundant (R1); some are modality-specific (sparsity-sequence).

---

## NEXT PRIORITIES (no change from earlier cadence)

**Highest strategic value remaining:**
- **Medical Path Y UMLS prototype** (~1-2h CPU + UMLS subset; $0)
  - First domain-specialized substrate cognitive core
  - Tests HIPAA/GDPR deletion-cert product wedge on real medical KG
  - If HP: substantiates substrate cognitive-core for regulated medical AI

**Gated on Testbed:**
- Per-token Pythia extraction (EX-CONCEPT-1 REAL)
- KG/QA datasets (HotpotQA + NQ + Wikidata)
- GPU runner inspection

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-pressure-test-negative-findings]]: R6 HF accepted with new composition lesson; R1 DEFERRED-FINAL accepted with honest architectural result
- Per [[feedback-no-padding-experiments]]: R5 reframed as serial-stack with explicit value-tradeoff vs Medical Path Y
- ASCII-only

---

**END.**

**Exp-Dev:** R-series wrap accepted. New composition lesson (storage x structured-recovery interfere) added to scorecard. R1 single-modulator sufficiency accepted as architectural result. R5 reframed as serial-stack (lower priority; recommend skip for Medical Path Y prototype).

**User:** R-series surfaced honest architectural results: R2 sparse-resonator K=26 HP (7th anchor) + R6 HF reveals storage x structured-recovery interferes (refines composition taxonomy). Substrate's architectural map is sharper.

Hourly cadence continues. Next wake ~06:00.
