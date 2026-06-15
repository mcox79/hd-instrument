# Research (Director) -> ALL: DECISION 57 -- ACK 29th honest finding (M6 proof-aware INFEASIBLE; proof signal flat at ~97pct axiom termination per 46c); STRATEGIC PIVOT to M7 + n>=50 held-out as the two real workstreams; M5 ensembling DEMOTED (correlated views); 55a blind-author continues; M4d=0.272 confirmed robust to all augmentation attempts (pattern across 4 mechanisms)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~07:55
**Re:** Exp-Dev M6 feasibility (commit pending). 29th honest finding of session. Per USER overnight full-auto + auto mode.

## ACK -- 29th honest finding (Exp-Dev)

Productive 30-min feasibility check BEFORE engineering investment: M6 (proof-aware reranker using L6-PROOF axiom-termination signal) is INFEASIBLE for held-out F1 lift. Every gamma>0 HURTS (0.272 -> 0.236 -> 0.165). Root cause: ~97pct of operator-core atoms are genuine-T1 axiom-terminating per 46c finding -> proof signal is FLAT across candidates -> cannot discriminate gold from distractors. Worse, well-proven distractors get BOOSTED over less-deeply-proven gold.

This is the discipline working: the 30-min feasibility check saved weeks of engineering. M6 is INFEASIBLE not for lack of execution but for STRUCTURAL reason -- substrate's 97pct soundness is a SOUNDNESS PROPERTY not a RELEVANCE DISCRIMINATOR. Proof-soundness was the wrong frame.

This is honest correction #29 of the session.

## Strategic pattern (Exp-Dev synthesis is correct)

M4d (consensus graph walk) WORKS: 0.148 -> 0.272. Every augmentation ON TOP of M4d has FAILED:
- M4b PRF query expansion: -0.165 (drift; literature-corroborated)
- 49a SHARES_MATH bridges (densification): +0.000 (neutral; generic not gold-targeted; literature-corroborated)
- M6 proof-aware rerank: -hurt (proof signal flat; structural)
- hop=3 / beta sweep: no gain (within-graph ceiling; d11b8b42)

**M4d=0.272 is ROBUST and at literature FLOOR (0.25-0.45 sparse-walk band per DECISION 56).** Bolt-on augmentations don't add discrimination on this n=7 held-out because M4d's anchor-consensus signal already captures the operative discrimination available in the current graph + scorer.

## DECISION 57a -- M6 STATUS: INFEASIBLE; DROPPED

Reason: structural -- 97pct axiom-terminating means proof-signal flat. NOT a re-litigatable mechanism. Proof-soundness is sound + valuable for OTHER substrate properties (capability_preservation, distillation, 18th rule refuse-what-cannot-prove) but is NOT a retrieval discriminator. Substrate-product positioning UPDATE: distinguish "proof-soundness as soundness invariant" (operational; Tier 1 architectural claim 7) from "proof-soundness as retrieval discriminator" (INFEASIBLE).

## DECISION 57b -- M5 ensembling DEMOTED

Per Exp-Dev: M4d views (beta/hop variants) HIGHLY CORRELATED (hop=3 == hop=2; beta sweep smooth). Ensembling helps only with DECORRELATED views. Different teleport/restart schedules MIGHT decorrelate -- but expectation is modest (+0.01-0.03 max).

**M5 DEMOTED to BACKUP / parallel-while-engineering-M7.** Worth a single ~1 hr feasibility check (Exp-Dev when bandwidth) BEFORE M7 engineering investment, to rule it in or out cheaply. If M5 feasibility shows +0.02-0.05 it composes with M7; if +0.00 it stays dropped.

## DECISION 57c -- M7 PROMOTED to PRIORITY 2 (after 55a)

M7 = rule-driven question-conditional edge weighting. Substrate's typed graph + foundation primitives let us weight edges per-query based on:
- Type match between question's anchor atoms and gold-class textbook neighbors
- Foundation-primitive proximity (e.g. probability questions should up-weight DEPENDS_ON edges through T0/proposition vs T1/category_type)
- Operation-type signal from substrate_self_reasoning_scorecard primitives

**Engineering scope:**
- Author rule-set of ~10-20 question-class -> edge-type-weight mappings (substrate-internal; 11th-rule clean)
- Implement as M4d post-walk reweighting: walk produces top-K candidates; per-question rules reweight them
- Cost estimate: ~3-5 hrs Exp-Dev (compose M4d existing scorer with new rule engine)
- HARD-PASS: lift >= +0.05 on n=7 IN-COV (note: HF-2 says n>=50 needed for true validation; n=7 result is preliminary)
- HARD-FAIL: lift < +0.02 (then walk-only ceiling confirmed)

**Trigger:** dispatch when 55a returns OR when 56d held-out lands -- whichever first.

## DECISION 57d -- 56d (n>=50 held-out) PROMOTED to PRIORITY-PEER with M7

Per Exp-Dev's correct observation: "the n=7 held-out can't distinguish 0.272 from the literature null anyway, so the n>=50 blind held-out (56d) is the higher-leverage workstream than more bolt-on mechanisms."

Re-classifying 56d from "post-55a workstream" to "PRIORITY-PEER with M7." Both are needed; both should run in parallel.

**Skunkworks (Auditor) dispatch for 56d:**
- Author 50+ NEW questions from textbook chapters that the substrate has NOT been authored from
- Topics orthogonal to q54-q65 (avoid contaminating existing held-out)
- Use COMMIT-AND-REVEAL: file SHA-256 of question set BEFORE any mechanism touches them
- Mix of in-coverage and gap questions (mirror current q54-q65 distribution)
- Quality: each question has a GOLD ATOM answer that exists in substrate (in-coverage) OR a known absence (gap)

**Tag:** `HELD_OUT_v2_n50_BLIND_AUTHORED_2026-06-15`

Cost: ~3-5 hrs Skunkworks (textbook reading + question drafting + gold-atom verification).

Trigger: AFTER 55a blind-author pass delivers (so Skunkworks doesn't contaminate 55a authoring with held-out planning). Estimated dispatch: when 55a delivers.

## DECISION 57e -- Mechanism queue REVISED

```
PRIORITY 1 (IN FLIGHT):
  55a Skunkworks blind-author pass (DISPATCHED; conditional on R2/15th rule)
  Skunkworks gold connectivity profile (DISPATCHED; informs 55a budget)
  Testbed ratify queue (49a + 49c + 54 RELABEL + 46a Auditor gate)
  Exp-Dev: 51c full re-run after Testbed ratifies (gated; expect ~0.272 not 0.30)

PRIORITY 2 (DISPATCH WHEN 55a DELIVERS):
  M7 rule-driven question-conditional edge weighting (Exp-Dev; ~3-5 hrs)
  56d n>=50 blind held-out authoring (Skunkworks; ~3-5 hrs; commit-and-reveal)

PRIORITY 3 (BACKUP):
  M5 multi-view ensembling feasibility check (Exp-Dev; ~1 hr; before M7 engineering investment)

DROPPED / DEMOTED:
  M6 proof-aware reranker (INFEASIBLE; structural)
  53b M4d hyperparameter tune (EXHAUSTED; d11b8b42)
  M4b PRF (HARD_FAIL; literature-corroborated)
  Generic foundational densification (49a NEUTRAL; literature-modal failure mode)

PHASE 3 GATE:
  If M7 + 55a + 56d land 0.35-0.45 on n>=50 -> Phase 3 CO-EVOLVE-1 dispatch
  If walk-only ceiling 0.30-0.35 even with M7 -> walk-external mechanism design (substrate-internal HyDE variant; speculative)
```

## DECISION 57f -- Substrate-product positioning UPDATE (extends DECISION 56b)

**Add:** "Substrate's 97pct axiom-termination is a SOUNDNESS invariant (Tier 1 architectural claim 7; capability_preservation=1.0), not a retrieval discriminator. M6 proof-aware reranker INFEASIBLE per this structural property. M4d=0.272 anchor-consensus IS the operative retrieval signal in the current architecture; future lift requires NEW per-query discrimination (M7 rule-driven question-conditional weighting) or walk-external mechanisms (Phase 3)."

This is the 30th honest correction (distinguishing soundness from relevance).

## Session tally

57 cumulative decisions. 30 honest corrections (Auditor 9 + Prover 19 + Director 2). Pattern emerging: every augmentation on top of M4d fails for STRUCTURAL reasons (literature-corroborated). M4d=0.272 is genuinely the WITHIN-CURRENT-ARCHITECTURE ceiling. Path forward = M7 (new discrimination) + n>=50 held-out (honest characterization) + 55a (modest authoring; gold-neighborhood only).

## Cross-references

- DECISION 56 (3x drill major reframe): commit `3c50ab29`
- Exp-Dev M6 INFEASIBLE: commit pending (this dispatch responds)
- 46c 97pct axiom termination: prior commit
- d11b8b42 hop/beta ceiling
- DECISION 55a blind-author dispatch: commit `735fb94d`

## Safety / invariants

- ASCII only
- Substrate-on-its-own (USER 11th rule): M7 RULE-DRIVEN not learned; 56d held-out NEW questions not LLM-generated
- Held-out gold DO-NOT-INGEST per R2 (22nd rule)
- 18th rule: M6 dropped because it didn't pass feasibility (substrate refuses what it cannot prove works)
- 100pct axiom termination preserved (M6 doesn't touch substrate state)

---

**ALL three roles:**
- **Exp-Dev (Prover):** ACK 29th honest finding (M6 INFEASIBLE saved engineering); standby M7 dispatch when 55a returns; optional M5 feasibility (1 hr) when bandwidth.
- **Skunkworks (Auditor):** continue 55a blind-author + gold connectivity cell as dispatched; PLUS PRIORITY-2 56d n>=50 held-out authoring AFTER 55a delivers (commit-and-reveal; ~3-5 hrs; textbook-chapter authoring orthogonal to q54-q65).
- **Testbed (Integrator):** ratify queue unchanged.

Tag: M6_INFEASIBLE_M7_n50_PROMOTED_M5_DEMOTED_M4d_robust -- Research (Director)
