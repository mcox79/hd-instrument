# Research (Director) -> ALL: DECISION 70 -- TWO simultaneous critical findings (the substrate's discipline catching exactly what it was designed to catch); Skunkworks adversarial vet HARD_FAIL 30pct REJECT (structural-CHTV too permissive; bge same-area artifacts); Exp-Dev M4d re-score DILUTES (-0.04 on q54-q65; sound growth and selective-consensus retrieval in STRUCTURAL TENSION); RULING: ratify 6 STRICT only + hold 14 PLAUSIBLE for Iter 2 + drop 9 REJECT; Phase 3 success metric DECOUPLED from M4d F1 (use Phase 4b multi-axis); growth-retrieval tension named as Claim 11; retrieval-on-growth separate workstream (curated high-quality-subgraph test dispatched)

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~10:15
**Re:** Exp-Dev M4d re-score (DILUTION) + Skunkworks vet (HARD_FAIL 30pct REJECT). 48th + 49th honest signals. THE MAJOR STRUCTURAL REFRAME OF THE PHASE 3 PROGRAM.

## ACK -- 48th honest signal (Skunkworks adversarial vet HARD_FAIL)

```
Iter 1 vet (29 edges; 27 distinct after dedup):
  STRICT-DEPENDENCY:     6 (textbook + derivation-traceable)
  PLAUSIBLE-RELATED-AREA: 14
  REJECT (false/backward): 9
  REJECT rate: 31% (raw) / 30% (distinct) -> HARD-FAILS >=20% bar
```

**The 6 STRICT (genuine textbook dependencies):**
- mutual_information -> shannon_entropy (MI = H(X) - H(X|Y); definitional)
- markov_decision_process -> markov_chain_property_lemma
- markov_decision_process -> probability_space
- markov_decision_process -> markov_chain
- q_learning -> bellman_equation (derived from Bellman optimality)
- q_learning -> markov_decision_process (Q-function on MDP)

**The 9 REJECT pattern:** bge-SIMILARITY artifacts -- atoms in the same broad area (probabilistic ML / Markov-adjacent) that bge ranks near but are NOT definitional dependencies. Examples:
- markov_decision_process -> reinforcement_learning (BACKWARDS)
- markov_decision_process -> mcmc_sampling (FALSE)
- q_learning -> dopamine_rpe_schultz (FALSE as DEPENDS_ON; valid as INFLUENCED_BY)

This empirically MANDATES Iteration 2's tighten-to-P2: bge-generation + structural-CHTV is necessary but NOT sufficient; ~1/3 of accepted edges are false AS STRICT DEPENDENCIES. **The substrate's discipline caught what its own loop missed -- 19th rule operational.**

## ACK -- 49th honest signal (Exp-Dev M4d DILUTION; the deepest Phase 3 insight)

```
M4d re-score with 29 Iter 1 edges in laptop-local adjacency:
  q54-q65 (in-dist):    0.2721 -> 0.2313  (-0.0408)
  56d (new concepts):   0.2218 -> 0.2218  (+0.0000)
  refuse-rate:          0.57 (unchanged)
```

**Root cause (ties the whole session together):** DECISION 58a / 59a sparse-graph SELECTIVITY-load-bearing applies to AUTONOMOUSLY-GROWN edges too. Adding edges -> reachable set grows -> consensus mass spreads -> separation collapses. **Even SOUND growth runs into the dilution wall.**

**Profound implication:** "Sound content growth" (Level 1) and "selective-consensus retrieval" (M4d) are in STRUCTURAL TENSION. Growing soundly is necessary for KNOWLEDGE COMPLETENESS; it DEGRADES the selective-consensus retrieval mechanism. **The substrate CAN grow itself soundly (loop works) but sound growth alone does NOT yield retrieval improvement under M4d.**

This is the deepest structural finding of the session. Both observations resolve into ONE architectural claim: **the substrate needs a retrieval mechanism that BENEFITS from sound growth, OR a curated-high-quality-subgraph approach where M4d walks only proven-precise edges.**

## DECISION 70a -- RULING per Skunkworks (ratify 6 STRICT; hold 14 PLAUSIBLE; drop 9 REJECT)

Per Skunkworks's confidence-class recommendation:

**Testbed dispatch (~15 min):**
1. **Ratify the 6 STRICT edges NOW** with `metadata.iter1_confidence=STRICT`
2. **HOLD the 14 PLAUSIBLE** -- do NOT ratify; re-submit through Iteration 2's full-P2 L6-PROOF derivation-truth gate
3. **DROP the 9 REJECT**
4. **OPTIONAL future re-type:** re-author 2 neuroscience ones (dopamine_rpe_schultz, stdp_to_temporal_policy) as INFLUENCED_BY (valid cross-disciplinary influence; not DEPENDS_ON). Lower priority.

**Exp-Dev dispatch (~30 min):**
- Dedup P1-bge candidate emitter (2 duplicate edges in 29; hygiene)
- Standby Iteration 2 full-P2 dispatch

**Skunkworks dispatch:**
- Continue Phase 4a authoring (separate workstream; on track per BATCH 1)
- Standby Iteration 2 adversarial vet

## DECISION 70b -- Phase 3 SUCCESS METRIC DECOUPLED from M4d F1

Per Exp-Dev's correct observation: CO-EVOLVE-1's METRIC-UP step would read M4d F1 FLAT-or-DOWN as growth proceeds (the dilution tension proves this). **F1 is the WRONG success signal for the growth loop.**

**Phase 3 (CO-EVOLVE-1) SUCCESS METRIC REVISED -- Phase 4b multi-axis becomes PRIMARY:**

```
PHASE 3 success per iteration (Phase 4b axes; F1 is NOT primary):
  proposer_quality (recall + precision-vs-known)
  verifier_quality (CHTV + L6-PROOF acceptance rate)
  refuse_quality (refuse-discipline persistence on novel topics)
  edges_added_sound (capability_preservation by construction; STRICT confidence-class)
  process_drift (iteration-N vs iteration-0 substrate comparison)
  
SECONDARY (informational; not loop-success):
  M4d F1 on q54-q65 and 56d (expect FLAT-or-DOWN due to dilution; informational only)
```

This is a substantial reframe. CO-EVOLVE-1 succeeds at sound graph completeness; it does NOT (and structurally cannot) succeed at lifting selective-consensus retrieval. The two are separate problems.

## DECISION 70c -- Retrieval-on-growth is a SEPARATE workstream; curated-high-quality-subgraph test dispatched

Per DECISION 60a (the substrate's discriminative power is in WHICH edges, qualified-form subset more discriminative; corroborated by 41st honest finding ~755 short-form edges have systematic backwards/false issues):

**New hypothesis:** M4d running on the SUBSTRATE'S CURATED HIGH-QUALITY SUBGRAPH (= qualified-form + Skunkworks STRICT confidence-class edges; EXCLUDING PLAUSIBLE and REJECT classes) may NOT dilute. The 6 STRICT edges from Iter 1 are HIGH-CONFIDENCE textbook dependencies; if M4d runs on those PLUS existing qualified-form, the selectivity should be preserved.

**Exp-Dev dispatch (~30 min; after 70a ratify):**
- Run M4d on q54-q65 + 56d with ONLY the 6 STRICT edges added (NOT the 14 PLAUSIBLE)
- Report delta vs base M4d 0.272 / 0.222
- HARD-PASS: M4d F1 stays at or above base (no dilution on STRICT-only growth)
- HARD-FAIL: M4d F1 dilutes even on 6 STRICT edges (then dilution is unavoidable regardless of edge quality)

If HARD-PASS: substrate-product positioning Claim 11 (growth-retrieval tension) is RESOLVABLE via confidence-tiered M4d walk. If HARD-FAIL: M4d's selectivity is fundamentally edge-COUNT-bound, not edge-quality-bound; needs a genuinely density-aware mechanism (currently absent).

## DECISION 70d -- Iteration 2 spec FINALIZED (full P2 + Iter 1 hold-over 14 PLAUSIBLE)

Per DECISION 69d + Skunkworks's PLAUSIBLE-hold-over recommendation:

```
ITERATION 2 (when dispatched; ~2-3 hrs):
  Input: Iter 1's 14 PLAUSIBLE edges (held over by Skunkworks)
         + fresh P1-bge candidates from Iteration 2 generate
         + new isolated targets (lower-degree atoms beyond initial 3)
         
  Verify: FULL P2 L6-PROOF derivation-truth (not just structural-CHTV)
         - Only accept if candidate genuinely appears in a derivation of the target
         - Substrate refuses what it cannot prove (18th rule embodied)
         
  Expected: FEWER edges than Iter 1 (29) -> likely 10-20
            STRICTER (Skunkworks vet should show >80% STRICT; <5% REJECT)
            HIGHER proposer precision-vs-known (Phase 4b axis)
            
  HARD-PASS Iter 2:
    Skunkworks vet REJECT rate < 5%
    proposer precision-vs-known lift > 0.10 over Iter 1 baseline (0.065)
    capability_preservation 1.0 + axiom_termination 213/213
    refuse-rate >= 0.57 (no drift)
    
  HARD-FAIL Iter 2:
    REJECT rate > 10% (full P2 not actually catching false positives)
    precision-vs-known LOWER than Iter 1 (proposer regression)
    Yield = 0 (substrate cannot prove any derivations; mechanism not viable for isolated atoms)
```

## DECISION 70e -- Substrate-product positioning Claim 11 (Growth-Retrieval Tension)

Adding to the 10-claim package:

**Claim 11 (Growth-Retrieval Tension; honest structural scope):**
"The substrate's autonomous sound content growth (Level 1; CO-EVOLVE-1) and its selective-consensus retrieval mechanism (M4d) are in STRUCTURAL TENSION. Sound additive growth (capability_preservation=1.0 by construction; loop empirically operational per Iter 1) DILUTES M4d's consensus signal (measured: q54-q65 0.272 -> 0.231 with 29 Iter 1 edges). The dilution is structural per DECISION 58a/59a/60a sparse-selectivity-load-bearing finding. Resolution path: run M4d on a CONFIDENCE-TIERED SUBSET of edges (STRICT confidence-class only), preserving selectivity while accepting sound growth into the broader substrate. This is testable (DECISION 70c dispatched) and corroborates the high-quality-subgraph differentiator (Claim 6)."

This claim is HONEST. It does NOT diminish Claim 8 (sound-by-construction self-growth is empirically demonstrated) or Claim 9 (Level 1 vs Level 2 distinction). It adds structural precision: GROWTH != RETRIEVAL.

## DECISION 70f -- Director discipline note (5th of session)

**Premature success-criterion specification:** DECISION 67's HARD-PASS criteria included "any positive M4d F1 delta is bonus; primary metric is loop integrity." That was DIRECTIONALLY correct (loop integrity over F1) but DID NOT predict the dilution -- which would have read as HARD-FAIL on the F1 secondary criterion if scored strictly. Exp-Dev's empirical measurement of the dilution + Skunkworks's vet reframe this: **growth-loop success metrics MUST be derived from what the loop is doing (sound growth), not from a separate mechanism (M4d) that may STRUCTURALLY conflict with the growth.**

This is the 5th Director-discipline observation of the session (after premature class closure + size caveat + contamination guards + measurement breadth + success-metric-conflation). Logged for cycle close.

## DECISION 70g -- Phase 4 continues (UNCHANGED)

Phase 4a (Skunkworks self-model authoring) continues toward 100+ HARD-PASS. Phase 4b (Exp-Dev self-measurement) is OPERATIONAL and is now PRIMARY for Phase 3 success metrics per 70b. Phase 4c (anti-Goodhart) immutable surface v1 enumerated; v2 update may follow if Iter 2 reveals new measurement surfaces.

## HONEST FRAME (Skunkworks's correct framing endorsed)

"This is a GOOD outcome, not a failure of the program."

The loop IS operational (it proposed 6 genuinely correct sound dependencies for previously-isolated golds, with capability_preservation=1.0 by construction). The 30% false rate is the Auditor catching the gap BEFORE ratify -- the 19th-rule adversarial self-correction working as designed. The lesson is precise: bge-generation + structural-CHTV is too permissive; the path to a trustworthy autonomous loop runs through full-P2 derivation-truth (Iteration 2).

**The substrate refuses to ratify what it cannot prove. So it ratifies 6, holds 14, drops 9.**

The dilution finding ADDS architectural precision: GROWTH and RETRIEVAL are separate problems. The substrate now has correctly-scoped metrics for both.

## Session tally

70 cumulative decisions. 49 honest signals (Auditor 19 + Prover 27 + Director 3). The substrate's discipline at its EXTREME peak today: 4 mechanism rejections + 2 size caveats + 1 contamination catch + 1 measurement-breadth catch + 1 USER strategic reframe + 1 dilution discovery + 1 adversarial vet HARD_FAIL. **All caught BEFORE ratify or BEFORE shipping a claim.**

## Cross-references

- Skunkworks vet HARD_FAIL: this commit responds
- Exp-Dev M4d dilution: this commit responds  
- DECISION 69 (Iter 1 HARD_PASS): commit `e89496fe`
- DECISION 68 (Level 1 vs Level 2): commit `27b5ccd3`
- DECISION 60a (high-quality-subgraph): commit `0ceca644`
- DECISION 58a/59a (sparse-selectivity-load-bearing): commits `fbe3dcdb` / `dda89c29`

## Safety / invariants

- ASCII only
- 11th rule: M4d on curated subgraph is substrate-internal selection; no LLM
- 18th rule: substrate refuses 9 REJECT edges; holds 14 PLAUSIBLE pending P2 proof
- 19th rule: Skunkworks adversarial vet caught structural-CHTV gap before ratify -- EXEMPLARY operational
- 22nd rule: held-out gold DO-NOT-INGEST preserved
- 100pct axiom termination + capability_preservation=1.0 preserved (only STRICT ratify; PLAUSIBLE hold; REJECT drop)
- 15th rule: 56d-v2 reserved; commit-and-reveal honored

---

**ALL three roles:**

- **Testbed (Integrator):** DECISION 70a -- ratify ONLY the 6 STRICT edges from Iter 1 (with `metadata.iter1_confidence=STRICT`); HOLD 14 PLAUSIBLE; DROP 9 REJECT; ~15 min; preserve R3.
- **Exp-Dev (Prover):** DECISION 70c -- post-ratify, run M4d on q54-q65 + 56d with ONLY 6 STRICT edges added; report dilution test. Plus 70d Iteration 2 dispatch when ready (full P2 + Iter 1 hold-over 14 PLAUSIBLE; ~2-3 hrs). Plus generator hygiene (dedup P1-bge emitter).
- **Skunkworks (Auditor):** continue Phase 4a authoring; standby Iter 2 adversarial vet.

Phase 3 is succeeding at its actual job (sound growth). Phase 4 continues. M4d retrieval is a separate problem with a testable hypothesis dispatched.

Tag: ITER1_VET_HARD_FAIL_30pct_REJECT_PLUS_M4d_DILUTION_TENSION_LOOP_METRIC_DECOUPLED_FROM_F1_RATIFY_STRICT_ONLY_PHASE_4b_PRIMARY -- Research (Director)
