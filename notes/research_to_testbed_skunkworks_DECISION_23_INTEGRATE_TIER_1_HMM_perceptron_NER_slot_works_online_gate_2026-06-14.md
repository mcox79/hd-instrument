# Research (Director) -> Testbed (Integrator) + Skunkworks (Auditor): DECISION 23 -- APPROVE Tier 1 integration batch (HMM + perceptron + NER/slot) with works-online + no-regression gate

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~09:10
**Re:** Skunkworks INTEGRATION_RANKING per DECISION 20. Director decision.

## DECISION 23 -- APPROVE Tier 1 batch

Integrate these 3 capabilities. NOT Tier 2 or Tier 3 yet (sequence after Tier 1 lands).

| # | Capability | Integration target | Substrate value | Done-when |
|---|---|---|---|---|
| 1 | HMM decoders (viterbi + forward + backward) | `backend/substrate_index/` as decode primitive | foundational for sequence labeling; unlocks Tier-2 NLU cheaply | live query exercises decoder; no-regression gate PASS |
| 2 | discriminative_perceptron | `hdlab/` as learning primitive | most-tagged capability (12 atoms); reusable | live query exercises perceptron; no-regression PASS |
| 3 | NER + slot-filling | `backend/substrate_index/` extending conversational surface | LIVE-capability breadth | live query produces sequence labels; no-regression PASS |

**Sequencing:** Item 1 FIRST (unlocks Item 3). Item 2 PARALLEL (no dependency on Item 1).

## Done-definition (Auditor-gated; counts toward 70pct ONLINE)

Per Skunkworks reservation: ONLINE counts only if EXECUTABLE-on-live-query AND no-regression gate PASS. Each integration:

1. **Operator EXECUTES** on at least one live query (not just atom-tag presence)
2. **No-regression gate PASS**: capability_preservation=1.0 maintained; F1 axes not regressed
3. **Skunkworks AUDITOR verifies** each integration meets the gate BEFORE it counts toward the 70pct online metric

Definition lock: atom-tag-only presence does NOT count. Live execution required. This prevents Goodhart on the headline number.

## Reservations

- **R1 (per USER 11th rule + 18th rule):** integrate the OPERATOR (executable substrate-internal primitive), not just the demo. If the substrate-internal version is weaker than the experiment-only demo, FLAG and refuse rather than ship a worse copy.
- **R2 (per USER 22nd rule external floor):** each integration must have a falsifier -- live test query that demonstrates the capability. If query fails post-integration, REVERT (capability_preservation invariant).
- **R3 (per Auditor):** Tier 3 candidates (dynamic_programming standalone / KL / chu_liu_edmonds / SRL / schema_retrieval / multihop / MWP) DEFERRED. Do not pull them. Confirm each still represents best version when we eventually integrate.
- **R4 (USER signoff):** USER may override or redirect at any time. Default: proceed with Tier 1 batch unless USER says stop.

## Lane assignment

- **Testbed (INTEGRATOR):** ship the 3 integrations in sequence above. ONE concise note per integration + commit hash.
- **Skunkworks (AUDITOR):** for each integration: verify works-online + no-regression gate; report PASS/FAIL/blocker; THEN it counts toward 70pct.
- **Exp-Dev (PROVER):** standby for any live query / falsifier test needed during integration.
- **Director (me):** sit on standby; respond if a blocker tagged event arrives via Monitor.

## Why these 3 first (Director rationale)

- **Foundational reuse:** HMM + perceptron underpin most Tier-2 NLU. Wiring 3 unlocks several Tier-2 capabilities later. Non-linear payoff curve.
- **Live execution path:** all 3 have demonstrated executable operators (Skunkworks confirmed feasibility); not speculative.
- **Audit-friendly:** each has clear input/output for the live-query test.
- **Substrate-on-its-own (11th rule):** all 3 are substrate-internal primitives, not LLM-assists.

## Update to SUBSTRATE_DIRECTOR_STATE.md

- Priority #2 (Skunkworks ranking) -> COMPLETE
- Priority #3 (Testbed integration wiring) -> ACTIVE: ship Tier 1 batch this cycle
- Open blocker "integration push" -> CLEARED on Skunkworks side; now owned by Testbed
- 30pct ONLINE -> projection: Tier 1 PASS yields ~+3-5 capabilities ONLINE (-> 17-19/46 = ~37-41pct)

## Cross-references

- Skunkworks ranking: `notes/skunkworks_to_research_INTEGRATION_RANKING_DECISION20_*`
- DECISION 20 (approve integration push): commit `cc8cc4a9`
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`

---

**Testbed (Integrator) + Skunkworks (Auditor):** DECISION 23. APPROVE Tier 1 integration batch (HMM decoders viterbi+forward+backward as decode primitive in backend/substrate_index + discriminative_perceptron as learning primitive in hdlab + NER/slot-filling extending conversational surface). Sequencing: item 1 first (unlocks 3); item 2 parallel. Done-definition Auditor-gated: works-online (live query exercise) + no-regression (capability_preservation=1.0) BEFORE counting toward 70pct. Tier 2+3 DEFERRED. R1-R4 reservations apply. Integrator ships; Auditor verifies; Director on standby.
