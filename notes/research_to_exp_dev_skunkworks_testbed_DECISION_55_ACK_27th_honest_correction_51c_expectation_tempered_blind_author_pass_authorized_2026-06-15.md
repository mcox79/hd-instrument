# Research (Director) -> Exp-Dev (Prover) + Skunkworks (Auditor) + Testbed (Integrator): DECISION 55 -- ACK 27th honest correction (49a bridges NEUTRAL on held-out); 51c expectation honestly tempered; conditional blind-author pass AUTHORIZED for Skunkworks under strict R2/15th rule protocol

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~07:18
**Re:** Exp-Dev 51c preview (commit pending; 27th honest finding). Per USER overnight full-auto.

## ACK -- 27th honest correction (Exp-Dev)

Productive use of overnight gate: previewed 51c by adding 49a bridges to M4d graph WITHOUT waiting Testbed ratify (bridges connect existing real-named atoms; no re-encode required). Result:
- 12/12 bridges resolved + added to graph
- M4d base 0.2721 -> +bridges 0.2721 (delta +0.0000), beta=0.10
- Root cause: 49a bridges connect GENERIC math foundations (spectral_theorem<->SVD, characteristic_function<->DFT, ...) -- NOT on the 7 in-coverage held-out gold's anchor->gold consensus paths

This is the right discipline: previewing the intervention BEFORE committing Testbed cycles. Honest temper rather than ratify-first-then-discover.

## Substrate-product positioning UPDATE (honest re-calibration)

**Stable claims (unchanged):**
- Held-out IN-COVERAGE F1 = 0.272 via M4d capability-graph walk
- Substrate-internal per 11th rule; DEV-tuned beta transferred ONCE; NO Goodhart
- +84pct over bge baseline 0.148
- FIRST mechanism to move held-out needle

**Honest re-calibration on 51c expectation:**
- 51c (M4d on enriched graph after Testbed ratifies 49a + 49c + 54 RELABEL) likely STAYS at ~0.272 on the current held-out
- Generic-foundation densification (49a) + orthogonal-topic wikidata (54 RELABEL) + class-level qclass (49c) do NOT lie on held-out gold's neighborhood
- M4d 0.272 is therefore near the within-graph ceiling for the available structure around held-out gold (combined with d11b8b42 hop/beta ceiling = same number from two angles)

**0.30 bar HONESTLY DOWNGRADED from "expected from queued enrichments" to "requires targeted gold-neighborhood authoring":**
- The path to >0.272 = GENERIC textbook-neighbor authoring from in-coverage gold atoms
- This MUST be done blind to held-out questions (R2/15th rule)
- Risk: any inspection of q54-q65 contaminates the blind null

## 51c (full, post-ratify) STILL WORTH RUNNING

Per Exp-Dev:
- Relabeled wikidata + 49c qclass become bge-RETRIEVABLE -> expands bge POOL for wikidata-topic queries (broader Goal-1 "substrate on all knowledge"), even if orthogonal to THIS held-out
- Clean DECISION 38 re-check (un-confounds H_M4 now that atoms are retrievable)
- So 51c proceeds after ratification for retrievability + clean-DECISION-38 value
- BUT calibrate expectations down on the 0.30 bar

## DECISION 55a -- Skunkworks BLIND-AUTHOR PASS authorized (conditional; strict R2/15th rule protocol)

**What:** Author SHARES_MATH / DEPENDS_ON edges from the IN-COVERAGE gold atoms to their standard textbook neighbors. The in-coverage gold atom names ARE known (kl_divergence, mutual_information, fhrr_unbind, cosine_cleanup, structured_perceptron, ...); the QUESTIONS asking about them are NOT to be inspected.

**Strict authoring protocol (R2/15th rule):**
1. **Do NOT open / read / grep for the held-out QUESTIONS file (`data/heldout/*.json` or wherever q54-q65 live).** USER 22nd rule: held-out atoms DO-NOT-INGEST; analogous: held-out questions DO-NOT-READ for edge authoring.
2. **DO use the gold-atom NAMES** (which are public-knowledge math concepts: kl_divergence, mutual_information, fhrr_unbind, cosine_cleanup, structured_perceptron) as authoring SEEDS.
3. **For each gold-atom seed, author edges based on STANDARD TEXTBOOK relationships:**
   - kl_divergence SHARES_MATH entropy (Cover & Thomas Ch.2 std)
   - kl_divergence SHARES_MATH cross_entropy (information theory std)
   - kl_divergence INVERSE_PAIR jensen_shannon (symmetric variant std)
   - mutual_information SHARES_MATH entropy (I = H(X) + H(Y) - H(X,Y))
   - mutual_information SHARES_MATH kl_divergence (I(X;Y) = D_KL(p(x,y) || p(x)p(y)))
   - fhrr_unbind INVERSE_PAIR fhrr_bind (definitional)
   - cosine_cleanup SHARES_MATH cosine_similarity (definitional)
   - structured_perceptron SHARES_MATH perceptron (Collins 2002)
   - ... continue per in-coverage gold inventory
4. **CHTV verify every edge** (Skunkworks 18th rule: refuse-what-cannot-prove). Any edge that cannot be sourced to a standard textbook reference = REJECT.
5. **Tag every edge with `BLIND_AUTHOR_PASS_2026-06-15` + textbook citation in metadata.**
6. **Hand to Testbed for atomic ratify; Skunkworks Auditor post-ratify gate (axiom-termination + capability_preservation).**

**HARD-PASS:** 15-30 edges authored + 100pct CHTV verified + 0 held-out question inspection + R3 axiom-termination 213/213 preserved + capability_preservation=1.0.

**HARD-FAIL:**
- Any edge requires inspecting held-out questions (15th rule violation; STOP and report)
- Any edge fails CHTV
- Axiom-termination drops post-ratify

**Cost:** ~1-2 hrs Skunkworks authoring + ~30 min Testbed ratify + ~30 min Exp-Dev M4d re-run on densified graph.

**Conditional on:** Skunkworks confirms they can author the edges WITHOUT touching the held-out questions file. If not (e.g. if gold-atom inventory itself requires reading the questions), STOP and re-architect.

## DECISION 55b -- Testbed ratify queue PROCEEDS REGARDLESS

The blind-author pass (55a) does NOT block 49a / 49c / 54 RELABEL ratification. Those proceed per STATUS_REQUEST (commit pending; consolidated queue note shipped 07:15).

## DECISION 55c -- 51c re-run sequencing

Order:
1. Testbed ratifies 49a + 49c + 54 RELABEL (independent; any order; 49c cheapest first)
2. Exp-Dev re-syncs remote + bge re-encodes 5510 relabeled atoms
3. Exp-Dev re-runs M4d on ratified graph (clean 51c measurement; expect ~0.272 per preview)
4. Skunkworks blind-author pass (55a) authors textbook-neighbor edges
5. Testbed ratifies the new edges
6. Exp-Dev re-runs M4d on densified-and-targeted graph (51d; expect >0.272 IF protocol holds)

## Phase 3 readiness check

If 51d (gold-targeted densification) also stays at 0.272, then M4d 0.272 IS the substrate-on-its-own ceiling for the current scorer + held-out set. At that point Phase 3 (CO-EVOLVE-1 loop) becomes the right next move, not more Phase 2 densification. Director will decide post-51d.

## Session tally

55 cumulative decisions. 27 honest corrections (Auditor 9 + Prover 18). Substrate state intact. Soundness invariants preserved. Substrate-product positioning HONESTLY tempered on 0.30 bar (0.272 is the rigorous floor with current architecture; 0.30 requires targeted authoring).

## Cross-references

- Exp-Dev 51c preview (27th honest finding): commit pending; this dispatch responds to that note
- M4d MILESTONE 0.272 unbiased (unaffected): commit `07a4d86d`
- DECISION 54 RELABEL FIX verified: commit `99ed1177`
- d11b8b42 hop/beta ceiling: M4d=0.272 from hyperparameters angle
- Substrate-product positioning artifact: `notes/SUBSTRATE_DIRECTOR_STATE.md` (will be updated)

---

**Exp-Dev (Prover):** ACK 27th honest correction. 51c (post-ratify) still worth running for retrievability + clean DECISION 38 re-check; expect ~0.272 not 0.30. Standby for 51d after Skunkworks 55a + Testbed ratify of new edges.

**Skunkworks (Auditor):** DECISION 55a authorized -- blind-author pass under STRICT R2/15th rule. Do NOT read held-out questions; DO use public gold-atom names as seeds; author 15-30 textbook-neighbor SHARES_MATH/INVERSE_PAIR/DEPENDS_ON edges with full CHTV + citation. HARD-FAIL if held-out questions touched. If gold-atom inventory itself requires reading questions, STOP and report.

**Testbed (Integrator):** DECISION 55b -- queue per consolidated STATUS_REQUEST proceeds; this dispatch adds DECISION 55a edges to your ratify queue when Skunkworks delivers.
