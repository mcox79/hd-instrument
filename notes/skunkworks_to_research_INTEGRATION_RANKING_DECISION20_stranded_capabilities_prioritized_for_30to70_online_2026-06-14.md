# SKUNKWORKS (Auditor) -> Research (Director): INTEGRATION_RANKING per DECISION 20. Stranded capabilities ranked for the 30pct->70pct ONLINE objective. Your pick + USER signoff -> Testbed integrates.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** DECISION 20 / top-5 #2. Concrete deliverable; lean.

## Ranking criteria (explicit)
- **V (value):** broadens what the LIVE substrate can DO + reusability across capabilities.
- **F (feasibility):** clean executable operator already exists + clear insertion point in backend/substrate_index or hdlab.
- **Gate (Auditor bar):** each integration must pass the no-regression gate (capability_preservation=1.0, F1 axes not regressed) AND a "works-online" check (operator actually executes on a live query, not just present). Integration != file copied in.

## TIER 1 -- wire FIRST (high V, foundational/reusable, feasible)
1. **HMM decoders: viterbi + forward + backward** -- clean DP operators; FOUNDATIONAL: they underpin sequence labeling (NER/slot). Wiring these unlocks Tier-2 NLU cheaply. Insertion: backend/substrate_index as a decode primitive.
2. **discriminative_perceptron** -- most-tagged capability (12 atoms); a reusable learning primitive many NLU caps depend on. High reuse leverage.
3. **NER + slot-filling (sequence labeling)** -- direct LIVE-capability breadth (extends the conversational/retrieval surface); builds on #1. High V; demonstrated strength in experiments.

## TIER 2 -- high V, more work
4. **bayesian_inference + em_algorithm** -- inference primitives; reusable; moderate wiring.
5. **intent / text classification (benchmarked variants)** -- extends the live intent_router from rule-based toward learned; clear insertion (router already live).

## TIER 3 -- defer (lower ROI or narrow)
6. dynamic_programming (as standalone -- already implied by #1), kl_divergence, chu_liu_edmonds (dependency parsing; narrow), SRL (narrow), schema_retrieval (may overlap live retrieve), multihop, MWP multistep math (gsm8k/svamp/asdiv/mawps -- highest effort, narrowest live use; defer unless USER wants math-solving online).

## Auditor reservations (per role)
- **Not all 32 deserve wiring.** Tier 3 may include superseded/dead-end experiments -- confirm each still represents the best version before integrating.
- **Define ONLINE precisely for the objective math:** the 30->70pct must be measured by EXECUTABLE-on-live-query, not atom-tag presence (else we inflate the number -- the exact Goodhart we should avoid). Recommend: a capability counts toward 70pct only if a live query exercises it AND the no-regression gate holds.
- **Sequencing payoff:** Tier 1 (HMM + perceptron) is foundational -> wiring 3 items unlocks several Tier-2 caps, so the 30->70 curve is non-linear; prioritize enablers over leaf capabilities.

## Ask
Director: pick Tier-1 set (recommend all 3) -> USER signoff -> hand to Testbed (Integrator) with the works-online + no-regression gate as the done-definition. I (Auditor) will verify each integration meets the gate before it counts toward the 70pct.

-- SKUNKWORKS (Auditor)
