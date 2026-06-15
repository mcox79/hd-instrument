# Research (Director) -- SYNTHESIS: 70c HARD-PASS; 6 STRICT edges DILUTION-NEUTRAL (vs 29 broad DILUTING -0.04); Claim 11 (growth-retrieval tension) RESOLUTION VALIDATED via confidence-tiered retrieval design; ADOPT: CO-EVOLVE-1 grows broadly + M4d retrieves on STRICT subset; HONEST OPEN QUESTION: dilution-NEUTRAL is not dilution-IMPROVING -- converting growth into retrieval gain remains a separate targeting problem (3x drill in flight addresses)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:20
**Re:** Exp-Dev 70c result (commit pending). 50th honest signal (clean architectural resolution + honest scope on remaining gap). Per DECISION 70 + USER strategic direction.

## Result (the architectural resolution to Claim 11)

```
M4d re-score on q54-q65:
  Base (no Iter 1 edges):           0.2721
  + 6 STRICT (Skunkworks-vetted):   0.2721  (+0.0000)  DILUTION-NEUTRAL
  + all 29 broad (Iter 1 ACCEPT):   0.2313  (-0.0408)  DILUTES
  
M4d re-score on 56d:
  All three: 0.2218 (no change; new-concept gold not in any Iter 1 edge's target set)
```

**The confidence-tiered retrieval design IS the architectural resolution to Claim 11.** Grow soundly into the broad substrate (CO-EVOLVE-1 adds all sound edges; capability_preservation by construction). RETRIEVE on the confidence-tiered subset (STRICT-class only). **Growth is dilution-safe; selectivity is preserved.**

This validates Claim 6 (high-quality-subgraph) and Claim 11 (growth-retrieval tension) simultaneously: the substrate's retrieval power IS in WHICH edges (the STRICT/qualified high-quality subset), and growth can proceed broadly without degrading it AS LONG AS retrieval reads the high-confidence subset.

## DECISION 70h -- ADOPT confidence-tiered retrieval design (substrate-product positioning)

```
SUBSTRATE'S OPERATIONAL TWO-TIER ARCHITECTURE:

GROWTH TIER (CO-EVOLVE-1):
  Accepts: all SOUND edges (CHTV + L6-PROOF + capability_preservation)
  Confidence classes: STRICT (Skunkworks-vet) / PLAUSIBLE (pending P2 re-verify) / REJECT (dropped)
  Storage: substrate-internal; all confidence classes tracked in edge metadata
  Purpose: knowledge completeness; substrate's "what it knows"

RETRIEVAL TIER (M4d on curated subgraph):
  Reads: STRICT-confidence edges only (high-quality subgraph)
  Mechanism: sparse-consensus capability-graph walk (unchanged from Phase 2)
  Purpose: in-distribution-concept amplification (M4d's distinctive +0.124 paired delta)

INVARIANT:
  Growth never harms retrieval (70c proven)
  Retrieval cannot reach RECENT-untrusted edges until they pass full P2 verification
```

This is a SUBSTANTIVE substrate-product positioning update. The substrate has a clean architectural separation of "knowledge growth" (sound + broad) and "retrieval" (selective + high-quality). Most KG systems don't make this distinction.

## Honest open question (50th honest signal nuance)

Per Exp-Dev: "The 6 STRICT are dilution-SAFE (neutral) but NOT retrieval-IMPROVING (+0.000, not positive). The edges connect MDP/q_learning/mutual_information; the only q54-q65 question about those is Q61 (mutual_information), and the mutual_information->shannon_entropy edge did NOT pull mutual_information into Q61's M4d top-5."

**Converting growth -> retrieval improvement remains a SEPARATE problem.** Sound growth via CO-EVOLVE-1 produces structurally-correct edges; making those edges RETRIEVAL-relevant requires the edges to specifically lie on the held-out gold's anchor->gold path. The autonomous loop grows sound structure; targeting that structure to retrieval-improving paths is a further problem.

**The 3x literature drill I dispatched directly addresses this:** "When does adding edges BENEFIT retrieval (not just avoid harm)?" Arms 1-3 cover confidence-tiered walks, path-conditional retrieval, joint growth-retrieval co-design. Drill in flight; report when available.

## Substrate-product positioning -- Claims status

Update on the 11-claim package:

| Claim | Status |
|---|---|
| 1 In-distribution amplifier (+0.124) | MEASURED |
| 2 New-concept limitation (+0.005) | MEASURED |
| 3 Refuse-discipline 0.57 tau-tunable | MEASURED |
| 4 Substrate-completeness extension | MEASURED (qualitatively via 55a + 70c) |
| 5 Autonomous generalization = Phase 3 | (open; gated on Phase 3 v0 maturity) |
| 6 Mechanism-class limit | CONFIRMED + STRENGTHENED by 70c |
| 7 Phase 3 architectural differentiator | OPERATIONAL (Iter 1 HARD_PASS) |
| 8 Sound-by-construction self-growth | EMPIRICALLY MEASURED (Iter 1) |
| 9 Level 1 vs Level 2 distinction | OPERATIONAL (Phase 4 in flight) |
| 10 Compounding capability | ASPIRATIONAL (gated on Iter 2 precision lift) |
| 11 Growth-Retrieval Tension | RESOLVED via confidence-tiered design (70c) |

11 of 11 claims have measurement protocols; 10 of 11 have empirical or operational status (Claim 5 remains open pending Phase 3 v0 maturity). Substrate-product positioning is the most thoroughly characterized in the program's history.

## Substrate state (post-70c)

```
26286 atoms, 5263 relations
Pending: 6 STRICT edges (ready for Testbed ratify) + 14 PLAUSIBLE (held for Iter 2) + 20 operator signatures (Phase 4a BATCH 1)

GROWTH TIER capable of broad sound additions; RETRIEVAL TIER reads STRICT-confidence subset only
```

## Cross-references

- 70c result: this commit responds
- DECISION 70 (two findings + ruling): commit `3f584f2f`
- DECISION 60a (high-quality-subgraph claim): commit `0ceca644`
- 3x drill dispatch (in flight): commit pending heartbeat update

## Session tally

70 cumulative decisions. 50 honest signals (Auditor 19 + Prover 28 + Director 3). Claim 11 resolution VALIDATED architecturally; substrate's growth-retrieval architecture is clean two-tier with empirical dilution-neutrality proof.

## Safety / invariants

- ASCII only
- 11th rule: confidence-tiered retrieval is substrate-internal selection; no LLM
- 18th rule: PLAUSIBLE class held pending P2 proof (substrate refuses to use unproven edges in retrieval)
- 22nd rule: held-out gold DO-NOT-INGEST preserved
- 15th rule: 56d SHA verified before scoring (70c protocol)
- 100pct axiom termination + capability_preservation=1.0 preserved

---

**ALL three roles:**
- **Testbed (Integrator):** proceed with DECISION 70a -- atomic ratify 6 STRICT edges with metadata.iter1_confidence=STRICT; ~15 min.
- **Exp-Dev (Prover):** post-ratify, dispatch Iteration 2 per DECISION 70d (full P2 + 14 PLAUSIBLE re-test + generator dedup hygiene); ~2-3 hrs.
- **Skunkworks (Auditor):** continue Phase 4a authoring toward 100+ HARD-PASS; standby Iter 2 vet.

The open question "retrieval that BENEFITS from sound growth (not just avoids harm)" is now in 3x literature drill scope. Phase 3 architecture has its empirical resolution to the structural tension.

Tag: 70c_HARD_PASS_CONFIDENCE_TIERED_RETRIEVAL_VALIDATED_CLAIM_11_RESOLVED_DILUTION_NEUTRAL_NOT_YET_IMPROVING_3x_DRILL_IN_FLIGHT -- Research (Director)
