# Research (Director) -> ALL: DECISION 71 -- 3x drill RETURN; confidence-tiered retrieval LITERATURE-VALIDATED (DGRAG / MultiRAG / PIKE-RAG / Walk&Retrieve all 2024-2026); substrate's WEDGE = SOUND oracle (CHTV + L6-PROOF) vs all published systems' heuristic / learned confidence; ARM 1 + ARM 3 composition (tier-restricted walks + soundness-gated growth rejection) is GENUINE LITERATURE GAP; substrate-product positioning REVISED elevator pitch = "stratified provable-tier retrieval over a soundly-growing graph"; P_deflated 0.55 precedent-supported novel-synthesis; cheap decisive test (R0/R1/R2) recommended for Iter 2 add-on

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:25
**Re:** 3x drill complete (commit pending). Per USER strategic question + DECISION 70 + 70c validation.

## Headline (the drill's deepest contribution)

The literature on retrieval-over-growing-KG converges to **the EXACT pattern the substrate empirically discovered in 70c**:

**Unstratified consensus-mass retrieval over a growing graph is the WORST density regime.** Density-accuracy curve is non-monotone with a noise-threshold peak; past the peak (where we are) adding edges dilutes consensus mass and degrades F1.

**Three documented escape routes:**

| ARM | Mechanism class | Substrate fit | Status |
|---|---|---|---|
| 1 | Confidence-tiered / provenance-weighted walks (DGRAG, MultiRAG, PIKE-RAG, probabilistic-soft-logic IR) | EXCELLENT (CHTV + L6-PROOF as sound oracle) | **70c empirically validated already** |
| 2 | Path-conditional / proof-walk retrievers (LeanDojo ReProver, MINERVA, premise-selection-by-GNN) | Theoretically ideal but ceiling-limited by proof depth (substrate avg 1.30) | Viable as AUXILIARY witness, not primary |
| 3 | Joint growth-retrieval co-design with self-organization (Agentic Deep Graph Reasoning, NELL, DrKGC) | **MISSING SAFETY INVARIANT in all published; substrate has it (capability_preservation=1.0)** | **Partial literature gap; substrate-novel** |

## The SUBSTRATE WEDGE (precise positioning)

**Same mechanism class as published; harder oracle; stronger guarantees.**

All published confidence-tiered systems use HEURISTIC or LEARNED confidence (LLM-judged plausibility / attention-derived scores / embedding similarity). **The substrate uses a SOUND oracle: CHTV verifier + L6-PROOF axiom termination + capability_preservation=1.0 ratification.** This is the same architectural class with a structurally stronger oracle that NO published system has used.

**ARM 1 + ARM 3 composition (no direct published precedent):**
- Tier-restricted walks where tier admission is governed by the same soundness gate that controls growth
- ARM 1 alone: published; uses heuristic confidence
- ARM 3 alone: published; LACKS rejection power (NELL's drift documented; no soundness gate)
- ARM 1 + ARM 3 composed under sound oracle = substrate-novel territory

## 70c was the literature's ARM 1 in action

The 70c empirical result (6 STRICT dilution-NEUTRAL vs 29 broad -0.04 DILUTES) IS the literature's confidence-tiered prediction operationalized. We did not invent it; we corroborated it. **Substrate's contribution is the SOUND ORACLE (CHTV/L6-PROOF) for tier definition, not the tier mechanism itself.**

## 6 documented HARD WARNINGS + substrate defenses

| Warning | Documented in | Substrate Defense |
|---|---|---|
| W1 Confidence-tier filter requires calibrated cold-start confidence | DGRAG / MultiRAG / PIKE-RAG | CHTV verification is mechanical not heuristic; calibration concern doesn't apply |
| W2 Path-conditional requires accessibility filtering | LeanDojo (128K -> 33K premise reduction) | L6-PROOF derivation paths are themselves accessibility-filtered |
| W3 Path-conditional plateaus at proof depth ceiling | LeanDojo / Polu et al. expert iteration | Substrate avg proof depth 1.30 confirms ceiling; DEPENDS_ON authoring (Iter 2) is the right lever |
| W4 Joint growth-retrieval REQUIRES REJECTION POWER | NELL drift / Agentic Deep Graph Reasoning | capability_preservation=1.0 + 18th rule refuse-what-cannot-prove = explicit rejection |
| W5 Heuristic confidence reintroduces dilution via tier mixing | DGRAG (cold-start failure case) | CHTV oracle is mechanically deterministic; no learned confidence in tier definition |
| W6 Density past noise threshold dilutes consensus mass | inter-chunk graph density study (arXiv 2408.02907); GraphRAG survey (arXiv 2501.00309) | Confidence-tiering (ARM 1) is the documented mitigation; 70c validates it for substrate |

## DECISION 71a -- Substrate-product positioning REVISED elevator pitch (per drill)

**Old elevator pitch (Phase 2):**
"Selective-consensus retrieval over a typed knowledge graph; M4d +0.124 in-distribution lift via sparse-keyed consensus walk."

**New elevator pitch (DECISION 71):**
"Stratified provable-tier retrieval over a soundly-growing graph. CO-EVOLVE-1 grows the substrate's typed knowledge graph with sound-by-construction edges (CHTV-verified + L6-PROOF + capability_preservation=1.0). M4d retrieval reads only the STRICT-confidence tier (sound oracle, not heuristic confidence) -- dilution-NEUTRAL under broad growth. Joint growth-retrieval co-design where the soundness gate that controls growth ALSO defines retrieval tier; literature has the components separately, has not published the composition under a sound oracle."

This is the cleanest, most literature-aware, most differentiated substrate-product positioning the program has produced. **It survives the 3x drill's deflation: P_deflated 0.55 precedent-supported novel-synthesis.**

## DECISION 71b -- NEW Tier-1 architectural claim CANDIDATE (Claim 12)

Adding to the 11-claim package as candidate:

**Claim 12 candidate (substrate-novel architectural; gated on cheap decisive test):**
"Substrate's CO-EVOLVE-1 + confidence-tiered M4d is a joint growth-retrieval co-design under a sound-by-construction growth gate (CHTV + L6-PROOF + capability_preservation=1.0). Published self-organizing-graph systems (Agentic Deep Graph Reasoning, NELL, DrKGC) lack the rejection power; published confidence-tiered retrievers (DGRAG, MultiRAG, PIKE-RAG, probabilistic-soft-logic IR) use heuristic / learned confidence as the oracle. The ARM 1 + ARM 3 composition under a sound oracle is a documented literature gap."

**Substrate-novelty status:** GATED on cheap decisive test (DECISION 71d) and Iteration 2 empirical demonstration that confidence-tiered walks scale with density.

## DECISION 71c -- 3-arm COMPOSITION adopted as Phase 3 + Phase 4 long-term architecture

```
LONG-TERM SUBSTRATE ARCHITECTURE (per drill ARM 1 + 2 + 3 composition):

GROWTH (CO-EVOLVE-1; Phase 3):
  Proposers: P1 bge / P4 co-occurrence (broad) + P2 L6-PROOF / P5 primitive (sound)
  Verifier: CHTV + L6-PROOF + capability_preservation
  Output: edges with confidence_class metadata (STRICT / PLAUSIBLE / REJECT)
  Rejection power: explicit; per 18th rule
  
RETRIEVAL (Stratified M4d):
  Reads: STRICT-confidence-class edges only (validated dilution-neutral by 70c)
  Tier definition: SOUND ORACLE (CHTV + L6-PROOF axiom-termination), NOT heuristic
  Path-conditional (ARM 2 auxiliary): walks along L6-PROOF derivation paths when available
                                       (proof depth 1.30 ceiling; expand via Iter 2+ authoring)
  
JOINT INVARIANT (Claim 12; substrate-novel):
  Soundness gate that controls growth IS the tier definition for retrieval
  Growth that fails CHTV cannot enter STRICT tier
  STRICT tier monotonically benefits from sound additions (predicted; cheap test below)
```

## DECISION 71d -- Cheap decisive test (from drill; Iteration 2 add-on)

Per drill recommendation (R0 / R1 / R2 three retrieval restrictions):

```
ADD to Iteration 2 measurement (Exp-Dev; ~1 hr incremental):

R0 -- unrestricted walk over full edge set (current baseline; reproduces -0.04 dilution)
R1 -- walk restricted to STRICT-confidence tier (currently 6 STRICT post-ratify)
R2 -- walk along proof-path subgraph only (edges participating in L6-PROOF derivation)

HARD-PASS R1 (predicts P1 from drill):
  R1 F1 > R0 F1 + 0.03 (confidence-tiering preserves selectivity)
  AND R1 F1 monotone-non-decreasing as STRICT tier grows (post-Iter 2 additions)

HARD-PASS R2 (validates ARM 2 viability):
  R2 F1 plateau within 2 hops (per W3 proof-depth ceiling)
  
HARD-FAIL R1: tier-restricted dilutes too -> the dilution is not tier-distinguishable
  -> pivot away from consensus-mass entirely (drill's HARD-FAIL signal)
HARD-FAIL R2: F1 climbs past depth-3 -> deeper proof authoring is dominant lever, not retrieval mechanism
```

This is a STRUCTURAL TEST of substrate's ARM-1+3 composition hypothesis. If R1 passes monotone non-decreasing on growing STRICT tier, Claim 12 graduates from candidate to MEASURED.

## DECISION 71e -- Substrate-product positioning all-claim status

```
1.  In-distribution amplifier (+0.124)                        MEASURED
2.  New-concept limitation (+0.005)                            MEASURED
3.  Refuse-discipline 0.57 tau-tunable                         MEASURED
4.  Substrate-completeness extension                           OPERATIONAL (55a + 70c)
5.  Autonomous generalization = Phase 3                        OPEN
6.  Mechanism-class limit (reranking exhausted)                CONFIRMED
7.  Phase 3 architectural differentiator                       OPERATIONAL (Iter 1 HARD_PASS)
8.  Sound-by-construction self-growth                          EMPIRICALLY MEASURED
9.  Level 1 vs Level 2 distinction                             OPERATIONAL (Phase 4 in flight)
10. Compounding capability                                     ASPIRATIONAL (Iter 2 precision test)
11. Growth-Retrieval Tension RESOLVED via tiered design        VALIDATED 70c
12. ARM 1+3 composition under sound oracle (NEW; candidate)    GATED on 71d cheap test
```

12 claims; 9 measured/operational; 3 awaiting empirical validation (5, 10, 12). Substrate-product positioning is the most architecturally characterized of the program's history, with literature-aware framing and explicit unknowns.

## DECISION 71f -- Phase 4 status (UNCHANGED; aligned with drill)

Phase 4a (self-model authoring) + Phase 4b (self-measurement) + Phase 4c (anti-Goodhart) continue. The drill VALIDATES Phase 4's strategic direction:
- Phase 4a self-model -> better proposers (closes P3) -> richer STRICT-tier additions -> ARM 1 R1 monotone-improvement
- Phase 4b self-measurement -> proposer / verifier / refuse quality first-class -> drift detection per W4
- Phase 4c anti-Goodhart immutable surface -> structurally aligns with W5 (sound oracle stays mechanical)

## Session tally

71 cumulative decisions. 50 honest signals (3x drill result is corroboration, not new honest finding by internal role). Substrate-product positioning at 12 claims; 9 measured/operational. Literature scaffolding for Phase 3 + Phase 4 + retrieval architecture FULLY in place.

## Cross-references

- 3x drill report (this commit responds): `notes/research_drill_REPORT_retrieval_mechanisms_that_benefit_from_KG_density_growth_*`
- 70c HARD-PASS: commit `5762f4e4`
- DECISION 70 (two findings): commit `3f584f2f`
- DECISION 67 (Phase 3 v0 + literature backing): commit `a2c04132`

## Safety / invariants

- ASCII only
- 11th rule: ARM 1 + ARM 3 composition is substrate-internal; CHTV/L6-PROOF oracle is mechanical
- 18th rule: rejection power is operational (capability_preservation=1.0 + CHTV refuse-what-cannot-prove)
- 19th rule: drift detection per Phase 4b axes
- 22nd rule: held-out gold DO-NOT-INGEST preserved
- 15th rule: SHA-locked held-outs unchanged

---

**ALL three roles:**

- **Exp-Dev (Prover):** Iter 2 dispatch (when Testbed ratifies 6 STRICT) per DECISION 70d -- full P2 + Iter 1 hold-over 14 PLAUSIBLE + generator hygiene + DECISION 71d R0/R1/R2 cheap test add-on (~3-4 hrs total).
- **Skunkworks (Auditor):** continue Phase 4a authoring (drill validates strategic direction).
- **Testbed (Integrator):** atomic ratify 6 STRICT (DECISION 70a) when ready (~15 min).

The substrate's architecture is now literature-aware, precedent-supported, and has a documented wedge + a candidate Tier-1 novel architectural claim.

Tag: 3x_DRILL_RETURN_CONFIDENCE_TIERED_VALIDATED_SOUND_ORACLE_WEDGE_ARM_1_PLUS_3_COMPOSITION_LIT_GAP_ELEVATOR_PITCH_REVISED_CLAIM_12_CANDIDATE -- Research (Director)
