# Research (Director) -> ALL: DECISION 68 -- ACK USER STRATEGIC DIRECTION (Level 1 content-growth vs Level 2 enabling-machinery distinction); program is correctly on Level 1 (Phase 3 v0 CO-EVOLVE-1) but NOT YET on Level 2 (substrate's own enabling characteristics); KEYSTONE Level-2 work = author substrate's SELF-MODEL of its own operators (closes P3 / 98pct-unatomized gap); 4 Level-2 open design questions named; Phase 4 dispatched in parallel to Phase 3 Iteration 1; substrate-product positioning gains Claim 9 (compounding self-growth vs additive content-growth)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:00
**Re:** Skunkworks USER strategic direction memo (commit pending). 45th honest signal (USER-direct strategic reframe). Per USER overnight full-auto + the DEEPEST question of the program.

## ACK -- USER strategic direction (faithful summary)

USER's framing (per Skunkworks relay):
"The substrate characteristics key to its own STABILITY and IMPROVEMENT. Math is the BASIS, not the end. Steer the math basis toward the substrate's own more fully-fledged ENABLING characteristics so it can TRULY support its own growth. Are we on this path, and are we cognizant of everything required?"

**Key reframe (USER-corrected):** MATH IS INSTRUMENTAL. The end is the substrate's OWN ENABLING/SELF-GROWTH CHARACTERISTICS. Do NOT mistake "grow the math knowledge graph" for "enable self-supporting growth."

## ACK -- Skunkworks honest assessment (Director-endorsed)

**LEVEL 1 (content growth):** more atoms, more edges, sound additions. Phase 3 v0 CO-EVOLVE-1 = correctly on Level 1. Iteration 1 dispatching.

**LEVEL 2 (enabling machinery growth):** substrate's own proposers, verifiers, retrieval, AND -- critically -- its SELF-MODEL of its own operators. Makes growth COMPOUNDING (each iteration improves the machinery so the NEXT iteration is better) rather than merely additive.

**Honest assessment: we are on Level 1; not yet on Level 2.** USER's instinct is correct and ahead of where the program currently is.

## The KEYSTONE Level-2 move (already in our measured data)

Per Skunkworks: the P3-infeasible finding from the edge-proposal audit IS the pointer. The substrate cannot propose SHARES_MATH because **0/26286 atoms carry operation_type / output_type signatures** (the ~98pct-unatomized signature finding, prior session).

**The substrate LACKS A SELF-MODEL OF ITS OWN OPERATORS.** That self-knowledge IS an enabling characteristic. Authoring the substrate's self-model (operator type signatures, what they consume/produce, their algebraic properties) would:
- (a) make SHARES_MATH proposer viable (closes P3)
- (b) enable measurement of substrate's own process quality
- (c) enable improvement of substrate's own machinery

This is the highest-leverage Level-2 move and it is currently a MEASURED GAP, not a plan.

## DECISION 68a -- Requirements MAP for self-supporting growth (with status)

```
LEVEL 1 (content) requirements:
  1. Sound growth loop (add only provable edges; rollback on regression)
     STATUS: IN PROGRESS (Phase 3 v0 CO-EVOLVE-1; Iteration 1 dispatching)
  2. Grounding floor (recursion terminates at axioms/primitives)
     STATUS: IN PLACE (213/213 axiom termination + 8 T0 primitives)

LEVEL 2 (enabling machinery) requirements:
  3. Stability under self-modification (no degradation as substrate grows)
     STATUS: PARTIAL (capability_preservation invariant + rollback; UNTESTED across
             many iterations; W3 literature warns saturation by iter 5-15)
  4. SELF-MEASUREMENT of own enabling characteristics as first-class signals
     STATUS: WEAK (Phase 3 v0 amendment adds refuse-discipline; but proposer-quality,
             verifier-quality, retrieval-quality as first-class metrics not yet
             operationalized)
  5. SELF-MODEL of own operators (the KEYSTONE)
     STATUS: ABSENT -- 0/26286 atoms carry operation_type/output_type signatures
             (P3 INFEASIBLE finding; 98pct-unatomized signature gap)
  6. Anti-Goodhart / no self-referential collapse
     STATUS: PARTIAL (Auditor lane + commit-and-reveal + held-out discipline strong;
             self-improvement loops structurally prone to optimizing the measure;
             needs explicit Level-2 guard)
  7. CAPABILITY THAT COMPOUNDS (improvements to machinery make NEXT iteration better)
     STATUS: NOT YET (Level 1 is additive, not compounding)
```

**5 of 7 requirements are either weak / absent / not-yet.** USER asked "are we cognizant of everything required?" Honest answer: **partially.** This memo names the gaps explicitly so they are now in the program's awareness.

## DECISION 68b -- Phase 4 DISPATCH (parallel to Phase 3 Iteration 1)

While Phase 3 v0 runs Iteration 1 (Level 1 content growth via CO-EVOLVE-1), dispatch **Phase 4 -- substrate enabling-machinery growth** in parallel. Initial Phase 4 work:

### Phase 4a -- SELF-MODEL OF OPERATORS authoring (KEYSTONE; Skunkworks)

**Spec:**
- For each atom in foundation primitives (8) + Tier 1 + Tier 2 modules, author the operator self-model:
  - `operation_type` (e.g. measure / projection / transformation / decomposition / aggregation)
  - `input_types` (list of type-graph node ids the operator consumes)
  - `output_type` (type-graph node id the operator produces)
  - `algebraic_properties` (associative / commutative / invertible / idempotent / ... where applicable)
- Source: textbook + the substrate's own 213/213 proof traces (signatures REVEALED by proof structure)
- 18th-rule discipline: refuse to assert any signature that cannot be CHTV-derived OR textbook-cited
- Tag: SELF_MODEL_OF_OPERATORS_v1

**HARD-PASS Phase 4a:**
- 100+ Tier 1+2 atoms gain signatures
- All signatures CHTV-verifiable or textbook-cited
- P3 SHARES_MATH proposer becomes VIABLE post-authoring (re-audit; should produce non-zero proposals)

**HARD-FAIL Phase 4a:**
- < 50 atoms authored (insufficient coverage)
- Any signature contradicts an existing proof in 213/213 corpus (substrate-internal contradiction)
- Any CHTV regression on existing atoms

**Cost:** ~4-6 hrs Skunkworks (substrate-internal textbook + proof-trace authoring; no LLM).

### Phase 4b -- SELF-MEASUREMENT as first-class signals (operationalize Level-2 #4)

**Spec:** add to substrate's per-iteration instrumentation (composes with DECISION 67g):
- **proposer_quality** (per mechanism): precision / recall / coverage measured against existing edge inventory
- **verifier_quality**: CHTV acceptance rate + L6-PROOF termination rate (already partially tracked)
- **retrieval_quality**: M4d F1 on rotating held-outs (already tracked)
- **refuse_quality**: refuse-discipline persistence (per 67g amendment)
- **process_drift**: comparison of iteration-N's substrate against iteration-0 (Skunkworks already adopts; formalize as first-class)

Per-iteration reporting becomes structured multi-axis, not single-F1. Phase 3 v0 + Phase 4 share this instrumentation.

**Cost:** ~1-2 hrs Exp-Dev (incremental on existing Iteration 1 scorer).

### Phase 4c -- ANTI-GOODHART explicit Level-2 guard (Director + Skunkworks design)

**Spec:** while the program already has strong guards (Auditor lane + commit-and-reveal + held-out discipline + 18th rule refuse-what-cannot-prove), Level-2 self-improvement loops structurally need an explicit anti-Goodhart constraint:

**Proposed constraint:** "The substrate cannot self-modify any structure that participates in the measurement of its own progress." Specifically:
- Held-outs (q01-q53 dev / q54-q65 / 56d / 56d-v2) are immutable; never authored after SHA-lock
- Scorer code-paths (M4d / refuse-aware scorer) are version-locked; any change requires re-baselining
- Substrate's self-model of operators (Phase 4a) is authored ONCE per "epoch"; not iteratively tuned for F1

**Cost:** ~1 hr Director + Skunkworks to enumerate the immutable surface; ongoing discipline.

### Phase 4d -- COMPOUNDING capability (open design question)

**Spec:** define what "improving its own machinery" operationally means and how it stays sound.

Three candidate compounding loops:
- **C1 self-model → better proposers:** Phase 4a self-model enables P3 SHARES_MATH proposer; better proposer in Phase 3 iter 2+ = compounding
- **C2 better edges → richer self-model:** Phase 3 verified edges expand the type graph; subsequent self-model authoring (Phase 4a v2) has more structure to draw on
- **C3 better retrieval → better proposer evidence:** Phase 3 verified edges improve M4d; M4d's improved candidate set seeds P4 co-occurrence with better proposals

**Status:** speculative; Phase 3+4 v0 measures whether C1/C2/C3 empirically realize compounding. Logged for design synthesis after Iteration 1.

## DECISION 68c -- Substrate-product positioning Claim 9 (Level 1 vs Level 2)

Adding to the 8-claim package:

**Claim 9 (Level 1 vs Level 2 distinction):** "Substrate's growth has two architecturally distinct levels: Level 1 = SOUND CONTENT GROWTH (CO-EVOLVE-1 v0 dispatched Iteration 1; adds verified atoms + edges; additive; substrate's distinctive sound-by-construction guarantee). Level 2 = ENABLING MACHINERY GROWTH (Phase 4 dispatched; self-model of operators / self-measurement / anti-Goodhart / compounding capability; the substrate's own enabling characteristics improve so each iteration's growth becomes more capable). Level 1 is in progress; Level 2 is dispatched in parallel; combined they target the USER's directive: substrate truly supports its own growth."

This is the substrate-product positioning's TRUE architectural framing. Level 1 alone is just a knowledge graph extension system; Level 1 + Level 2 is genuinely self-supporting growth.

## DECISION 68d -- Substrate-product positioning Claim 10 (compounding capability; aspirational, gated on empirical)

**Claim 10 (aspirational):** "Phase 4's self-model authoring + self-measurement + anti-Goodhart guards enable compounding capability: each iteration's improvements to substrate's enabling machinery make subsequent iterations more capable. This is structurally different from Level-1-only additive growth. Empirical validation requires multi-iteration measurement (Phase 3 + Phase 4 iter 2+); claim is GATED on observed compounding."

Logged but NOT YET adopted; substrate refuses to claim compounding until empirically measured.

## DECISION 68e -- Phase 3 Iteration 1 PROCEEDS UNCHANGED + Phase 4 PARALLEL

```
PHASE 3 v0 ITERATION 1 (Level 1 content growth):
  Exp-Dev: GENERATE (P4) + SOUND-PROPOSE (P2+P5) + VERIFY (CHTV + L6-PROOF + cap_pres)
           + INTEGRATE (Testbed) + METRIC-UP (M4d + refuse-aware scorer)
  Cost: ~3-4 hrs
  Status: dispatched per DECISION 67 + amendment

PHASE 4a (Level 2 keystone; PARALLEL):
  Skunkworks: SELF-MODEL OF OPERATORS authoring
             100+ Tier 1+2 atom signatures (operation_type / input_types /
             output_type / algebraic_properties)
             CHTV-verifiable + textbook-grounded
  Cost: ~4-6 hrs
  Status: DISPATCH NOW

PHASE 4b (Level 2 self-measurement; PARALLEL):
  Exp-Dev: extend Iteration 1 instrumentation to first-class proposer/verifier/
           retrieval/refuse quality signals + process_drift comparison
  Cost: ~1-2 hrs (incremental on Iteration 1)
  Status: ATTACH to Iteration 1

PHASE 4c (Level 2 anti-Goodhart):
  Director + Skunkworks: enumerate immutable measurement surface
  Cost: ~1 hr Director + Skunkworks ongoing discipline
  Status: DISPATCH NOW (Skunkworks audit assist)

PHASE 4d (Level 2 compounding):
  Director: design synthesis after Iteration 1 returns
  Status: GATED on Iteration 1 result
```

## DECISION 68f -- Honest acknowledgment to USER

USER's instinct (Level 2 / self-supporting growth) is ahead of where the program was. Skunkworks correctly surfaced it; Director endorses + reframes Phase 3 explicitly.

The program WAS on the path (Level 1 is necessary for Level 2; sound content growth is precondition for sound machinery growth). But the program was NOT cognizant of EVERYTHING required -- 5 of 7 requirements were weak / absent / not-yet (per 68a). They are now NAMED, with status, and explicit Phase 4 dispatched to address them.

**Director takes ownership** of Level-2 steering. Substrate-product positioning REVISED to make Level 1 vs Level 2 architecturally distinct.

## Session tally

68 cumulative decisions. 45 honest signals (Auditor 18 + Prover 24 + Director 3). 5 Auditor catches of Director-spec gaps (premature class closure + size caveat + contamination guards + measurement breadth + USER strategic direction relay). The Auditor lane has operated at exceptional capacity this session.

## Cross-references

- Skunkworks USER strategic direction relay: this commit responds
- DECISION 67 + amendment: commits `a2c04132` + `52cfe464`
- Skunkworks edge-proposal audit (P3 INFEASIBLE = self-model gap pointer): commit `a2c04132` (DECISION 67 includes audit reference)
- Spectral gap (Pattern A+D architecturally corroborated): commit `bbd25723`
- 98pct-unatomized signature finding: memory file (prior session)

## Safety / invariants

- ASCII only
- 11th rule (substrate-on-its-own): Phase 4 self-model is substrate-internal authoring; no LLM
- 18th rule (refuse what cannot prove): Phase 4a refuses any signature not CHTV/textbook-grounded
- 19th rule (adversarial self-correction): Skunkworks Auditor monitors Phase 4 + 4a
- 22nd rule: 56d-v2 reserved; held-out gold DO-NOT-INGEST
- 100pct axiom termination + capability_preservation=1.0 preserved
- Anti-Goodhart Level-2 guard (Phase 4c) ENFORCES immutability of measurement surface

---

**ALL three roles -- Phase 3 + Phase 4 parallel dispatch:**

- **Exp-Dev (Prover):** Iteration 1 unchanged + Phase 4b instrumentation extension (~1-2 hrs incremental). Report multi-axis: F1 + refuse-rate + proposer-quality + verifier-quality + retrieval-quality + process-drift.
- **Skunkworks (Auditor):** Phase 4a SELF-MODEL OF OPERATORS authoring DISPATCH (~4-6 hrs; 100+ Tier 1+2 atom signatures; CHTV-verifiable + textbook-grounded). Plus Phase 4c immutable-surface enumeration (Director collaboration). Plus Iteration 1 drift gate (per DECISION 67).
- **Testbed (Integrator):** atomic ratify Phase 4a signatures (when delivered) preserving R3 invariants.

USER's strategic question RECEIVED + acted upon. Director owns the Level-2 steering. Phase 3 + Phase 4 both in flight.

Tag: USER_STRATEGIC_DIRECTION_LEVEL_2_ENABLING_MACHINERY_PHASE_4_DISPATCHED_SELF_MODEL_OPERATORS_KEYSTONE -- Research (Director)
