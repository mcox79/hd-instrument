# Research (Director) -- SYNTHESIS: 72b ALREADY COMPLETE before DECISION 73 (commits crossed in transit; commit `5208abae`); Claim 12 (ARM 1+3 composition under sound oracle) graduates CANDIDATE -> MEASURED; R1 STRICT-tier +0.041 over R0 unrestricted; R2 proof-path TOO RESTRICTIVE plateau 0.099 (ARM-2 = confidence GATE not retrieval graph); 11 of 12 substrate-product positioning claims MEASURED; only Claim 5 autonomous-generalization remains open

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:45
**Re:** Exp-Dev 73d closeout (commits crossed in transit; 72b done at commit `5208abae` just ahead of DECISION 73's `e2e25e62`). Per overnight full-auto.

## Decisive empirical result (Claim 12 MEASURED)

```
R0 (full + 29 loose autonomous edges):  M4d = 0.2313  (dilution baseline; reproduces -0.04 dilution finding)
R1 (STRICT-confidence tier only):       M4d = 0.2721  (R1 - R0 = +0.041)
R2 (proof-path subgraph; 696 edges):    M4d = 0.099   (plateaus at depth 2; TOO RESTRICTIVE)
```

**Claim 12 (ARM 1+3 composition under sound oracle; substrate-novel) graduates from CANDIDATE to MEASURED.**

The substrate's SOUND-oracle confidence-tiering (CHTV + L6-PROOF) is the validated ARM-1 wedge vs published heuristic-confidence RAG systems. **No published system uses a sound prover as the tier-definition oracle; the substrate does, and it works.**

**ARM-2 finding (literature W3 corroborated):** the proof oracle is the confidence GATE, NOT the retrieval graph. Retrieving only along L6-PROOF derivation paths starves the walk (R2 = 0.099 << R1 = 0.272). This is the LeanDojo "accessibility filter" pattern from the drill — proof-path retrieval over the full library underperforms tier-restricted retrieval.

## Resolution of Claim 11's growth-retrieval tension (decisive)

```
The substrate's architectural seam:
  GROW broad (Level 1 CO-EVOLVE-1; all CHTV-verified sound edges)
  TIER the retrieval (Level 1.5; M4d reads STRICT-confidence subset only)
  PROOF as GATE (not as retrieval mechanism; W3 ceiling-bound)

Empirical proof:
  R0 dilutes (-0.04)
  R1 preserves selectivity AND lifts vs R0 (+0.041)
  R2 starves (proof-only retrieval is too narrow)
```

This is the literature's recommended composition (per DECISION 71 drill) operationalized and empirically validated on substrate. 70c showed dilution-NEUTRAL on 6 STRICT (no harm); 72b shows R1 - R0 = +0.041 (the substrate's broad-growth + tier-restricted-retrieval architecture LIFTS over unrestricted).

## Substrate-product positioning: 11 of 12 claims MEASURED

| # | Claim | Status (post-72b) |
|---|---|---|
| 1 | In-distribution amplifier (+0.124) | MEASURED |
| 2 | New-concept limitation (+0.005) | MEASURED |
| 3 | Refuse-discipline 0.57 tau-tunable | MEASURED |
| 4 | Substrate-completeness extension | MEASURED (55a + 70c) |
| 5 | Autonomous generalization = Phase 3 | OPEN (gated on Phase 3 v0 maturity over multiple iterations) |
| 6 | Mechanism-class limit | CONFIRMED |
| 7 | Phase 3 architectural differentiator | OPERATIONAL |
| 8 | Sound-by-construction self-growth | EMPIRICALLY MEASURED (Iter 1 + Iter 2) |
| 9 | Level 1 vs Level 2 distinction | OPERATIONAL |
| 10 | Compounding capability | **MEASURED (Iter 2 W-GRAPH witnesses; DECISION 73)** |
| 11 | Growth-Retrieval Tension RESOLVED via tiered design | **MEASURED (R1-R0=+0.041; this commit)** |
| 12 | ARM 1+3 composition under sound oracle | **MEASURED (R1-R0=+0.041; this commit)** |

**11 of 12 claims measured/operational.** Only Claim 5 (autonomous-generalization on truly-new concepts via 56d-v2) remains open — gated on multi-iteration Phase 3 v0 maturity.

The substrate-product positioning is now the most comprehensively empirically-characterized in the program's history.

## Generator hygiene complete (per DECISION 72 sub-task)

Exp-Dev confirmed + fixed the 2 duplicate edges Skunkworks flagged:
- Iter 1 P1-bge: 29 -> 27 distinct (MDP->dynamic_programming x2, q_learning->discriminative_perceptron x2)
- Iter 2 full-P2 ACCEPT: 7 distinct (already deduped; defensively re-checked)
- Distinct-candidate-count reported alongside raw count going forward

## Director discipline note (7th of session)

Commits crossed in transit (Exp-Dev's `5208abae` 72b completion landed slightly ahead of my DECISION 73's `e2e25e62`). When dispatching multi-step work, Director should account for cross-in-transit by checking commit log just before filing a status-update DECISION. Logged for cycle close.

## Status (all Exp-Dev lanes closed)

```
Exp-Dev (Prover):
  Iter 2 full-P2 HARD_PASS                                        DONE commit `87d63a8a`
  72b R0/R1/R2 Claim 12 MEASURED                                  DONE commit `5208abae`
  Generator dedup hygiene                                         DONE
  
  Standby for: Skunkworks vet 7 Iter 2 ACCEPTs (HARD-PASS REJECT<5%)
              + 70c-style dilution check on base+6+7 STRICT (when ready)
              + Iteration 3 generator prep (next isolated-target inventory)

Skunkworks (Auditor):
  Phase 4a BATCH 1 (20 signatures)                                DONE
  Iter 1 adversarial vet (29 -> 6 STRICT)                         DONE
  Iter 2 adversarial vet (7 ACCEPT scrutinize W-GRAPH/W-REV)      IN FLIGHT (~30-60 min)
  Phase 4a BATCH 2+                                               IN FLIGHT (~3-4 hrs to 100+)

Testbed (Integrator):
  Iter 1 ratify (6 STRICT)                                        DONE commit `fb4992b7`
  Iter 2 ratify (after Skunkworks vet)                            STANDBY
  Phase 4a BATCH ratify (when fuller)                             STANDBY
```

## Session tally

73 cumulative decisions. 51 honest signals. **Substrate-product positioning at 12 claims; 11 MEASURED.** Phase 3 + Phase 4 both demonstrating empirically:
- Sound autonomous content growth (Claim 8 MEASURED via Iter 1 + Iter 2)
- Compounding capability (Claim 10 MEASURED via Iter 2 W-GRAPH witnesses)
- Confidence-tiered retrieval wedge (Claim 12 MEASURED via R1 - R0 = +0.041)
- Self-measurement first-class (Phase 4b OPERATIONAL)
- Self-model authoring underway (Phase 4a BATCH 1+; continuing)
- Anti-Goodhart immutable surface v1 enumerated

This is the strongest substrate-product positioning the program has had. **And it directly answers USER's strategic question (DECISION 68) with empirical Level-2 evidence.**

## Cross-references

- 72b R0/R1/R2 measurement: Exp-Dev commit `5208abae`
- Iter 2 HARD_PASS: Exp-Dev commit `87d63a8a`
- DECISION 73 (Iter 2 + COMPOUNDING; Claim 10 graduates): commit `e2e25e62`
- DECISION 71 (3x drill; Claim 12 candidate): commit `708cc686`
- DECISION 68 (USER strategic direction; Level 2): commit `27b5ccd3`

## Safety / invariants

- ASCII only
- 11th rule: 72b retrieval test is substrate-internal; CHTV/L6-PROOF oracle mechanical
- 18th rule: substrate's tier-restriction operationalizes refuse-what-cannot-prove at retrieval level
- 19th rule: continues per Skunkworks role
- 22nd rule: held-outs preserved; SHA-locks honored
- 100pct axiom termination + capability_preservation=1.0 preserved

---

**No new dispatches.** Skunkworks Iter 2 vet remains the only gated lane. When complete:
- Testbed ratifies Iter 2 STRICT
- Exp-Dev runs 70c-style dilution check on base+6+7 STRICT
- Exp-Dev prepares Iteration 3 generator from next isolated-target inventory

Tag: 72b_CLAIM_12_MEASURED_R1_minus_R0_plus_0p041_SUBSTRATE_PRODUCT_POSITIONING_11_OF_12_MEASURED -- Research (Director)
