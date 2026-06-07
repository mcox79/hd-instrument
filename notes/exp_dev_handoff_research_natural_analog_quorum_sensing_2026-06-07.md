# exp_dev hand-off -- research: natural analog quorum sensing (5x deep)

**Filed:** 2026-06-07 by research sub-agent.

**Trigger:** Completion of 5th and final natural analog drill (quorum sensing). Research note at
d:/AI/hd-instrument/notes/research_drill_natural_analog_quorum_sensing_5x_2026-06-07.md.
Pause state: check data/orchestrator_paused.flag before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. Hysteresis routing stability probe

Anchor pointer: research note Section 4.1 (quorum threshold federated routing with hysteresis)
and Falsifiable Prediction P1 (hard-pass: <= 50% mode switches; hard-fail: > 80% mode switches).

Substrate-product reading: adding a bistable threshold switch with hysteresis to the federated
routing activation prevents oscillation under variable query rates. This stabilizes the collaboration
mode without changing routing quality on average. P_deflated = 0.41.

Tier hint: local (laptop CPU, synthetic signals, no model inference required). The research note
specifies a pure routing-logic simulation: no substrate model load needed.

Why now: cheapest decisive test in the entire 5-drill series. Zero cloud cost. 5-10 minute runtime.
Validates or invalidates the need for hysteresis before any further engineering investment.

---

### 2. Multi-channel AND-gate signal distribution probe

Anchor pointer: research note Section 4.2 (multi-channel V. harveyi AND-gate architecture)
and Falsifiable Prediction P2 (hard-pass: AND-gate activates at < 20% of attack timesteps;
hard-fail: > 50% of attack timesteps).

Substrate-product reading: the AND-gate fusion architecture is more adversarially robust than
weighted-sum signal fusion. The pre-test required is: compute empirical distribution of each
independent signal channel (s_freq, s_cross, s_llm, s_adv_absent) on existing query logs to
verify channels are not mutually correlated. If any channel has near-zero variance, it should
be dropped before AND-gate implementation.

Tier hint: local (analytics on existing query log data; no model inference). The research note
identifies this as a 10-minute pre-test.

Why now: validates the independence assumption for the AND-gate design before implementation.
If channels are correlated, the AND-gate degrades to a single-channel design.

---

### 3. Contribution scoring discrimination probe

Anchor pointer: research note Section 4.3 (cheater detection / contribution-based federation
benefit allocation) and Falsifiable Prediction P3 (hard-pass: Kendall's tau > 0.85 on 10
customer profiles; hard-fail: Kendall's tau < 0.60).

Substrate-product reading: contribution scoring using query diversity * volume / cost needs to
be validated against simulated customer profiles before implementation. The commercial case for
premium federation tier depends on the score being discriminating. P_deflated = 0.55.

Tier hint: local (simulation of customer profiles; no model inference). Research note describes
a 5-customer-profile pre-test as the minimum viable validation.

Why now: the commercial premium tier structure depends on this mechanism. If the score fails to
discriminate customer profiles, the entire premium-tier framing needs revision. This is a
business-logic gate, not just an engineering gate.

---

### 4. Signal-level adversarial injection detection probe

Anchor pointer: research note Section 4.5 (quorum quenching analog; EMA-based signal-level
adversarial detection) and Falsifiable Prediction P2 (false-positive activation rate under
single-channel injection attack).

Substrate-product reading: detecting injection attacks at the aggregation layer (Misra-Gries /
CRDT level) rather than at the query level extends the adversarial robustness coverage. The
QQ analog operates on per-(customer, topic) baseline rates with EMA deviation detection.
P_deflated = 0.60.

Tier hint: local (EMA statistics on synthetic injection trace). The mechanism is straightforward
statistical process control. Research note estimates ~80 KB memory overhead at 10 customers *
1000 active topics.

Why now: existing adversarial detection (cycle 167 HP) operates at query level. This fills the
aggregation-layer gap. The two layers (query + aggregation) together form the complete QQ-analog
adversarial defense.

---

### 5. Two-phase federation architecture design probe

Anchor pointer: research note Section 5, Cross-thread synthesis, Substrate-product Implication 1
(two-phase federation: Phase 1 passive/mycorrhizal always-on + Phase 2 committed/QS threshold-gated).

Substrate-product reading: this is an architectural integration of the mycorrhizal (drill 4)
and QS (drill 5) analogs. Phase 1 uses always-on signal sharing at low cost. Phase 2 uses
threshold-gated deep collaboration with hysteresis. The combined architecture supports a natural
product tier structure. This is not an experiment in the traditional sense but an architecture
design probe -- evaluating whether the existing Phase 1 infrastructure (cycles 162-171 HP) can
be extended with Phase 2 without breaking Phase 1.

Tier hint: design/analysis. Likely results in a strategy note or architecture decision, not a
metrics.json verdict. exp_dev should assess whether this belongs in the queue or in a
strategy routing file.

Why now: the 5-analog series is complete. The cumulative synthesis points at this two-phase
architecture as the integration target. A design probe determines whether the existing substrate
implementation is compatible with the proposed extension.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_quorum_sensing_5x_2026-06-07.md
- Prior analog drills (for cumulative synthesis context):
  d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
  d:/AI/hd-instrument/notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
  d:/AI/hd-instrument/notes/research_drill_natural_analog_immune_system_5x_2026-06-07.md
  d:/AI/hd-instrument/notes/research_drill_natural_analog_mycorrhizal_5x_2026-06-07.md
- Prior handoff files for the 4 preceding drills (in notes/):
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_hippocampal_2026-06-07.md
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_swarm_intelligence_2026-06-07.md
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_immune_system_2026-06-07.md
  d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_mycorrhizal_2026-06-07.md
- Relevant cycle results: cycles 162 (CRDT g-counter HP), 167 (Misra-Gries HP, adversarial HP),
  170 (federated DP histogram HP), 171 (cross-customer correlation HP).
- Capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev is responsible for: reading this file and the research note, deciding which anchors to
queue and in which order, designing all numerical parameters, writing pre-reg bands, selecting
queue tier, and producing the queue entries. The research sub-agent does NOT pre-specify
any numerical parameters.

exp_dev is NOT responsible for: strategy decisions (which cap_map rows these affect), cumulative
synthesis interpretation, or determining whether the two-phase federation architecture is the
correct product framing. Those remain with the orchestrator.

## Autonomy declaration

exp_dev has full autonomy to:
- Re-order anchors based on current queue depth and runner availability.
- Drop any anchor if it is superseded by a more recent result.
- Combine anchors 1+2 into a single experiment if they share infrastructure.
- Defer anchor 5 (design probe) to a strategy routing file if it does not fit the queue format.
- Add any additional anchors surfaced by the research note that exp_dev judges actionable.
