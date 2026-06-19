# exp_dev hand-off -- research: natural analog swarm intelligence (5x drill)

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale only. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by P_deflated x engineering cost)

### 1. Cell SW1 -- Time-windowed Misra-Gries temporal signal validation (HIGHEST PRIORITY)
Anchor pointer: STIGMERGY-DECAY-SW1 (new; not yet queued)
Substrate-product reading: validates that adding an explicit decay rate alpha to Misra-Gries counters correctly promotes recent access patterns over stale ones; directly upgrades customer pitch from "aggregates usage" to "prioritizes recent usage"; no risk (alpha=0 recovers current behavior)
Tier hint: CPU; < 1 hour wall; laptop or remote_cpu_queue; existing Misra-Gries code + HotpotQA access simulation
Why-now: 1-2 day engineering cost with P_deflated=0.75; cheapest highest-P extension from the swarm drill; synergizes with sleep defrag (already HP cycles 167+170)
Pre-test note: per [[feedback-drill-pretest-required]] -- run alpha sweep on simulated 30-day query log before committing engineering time; pre-test IS the experiment here (no production encoder needed)
HARD-PASS: new query keys hold >60% of top-K counter mass at alpha=0.05 despite <20% of query volume
HARD-FAIL: new keys hold <30% of top-K (no temporal signal; alpha does nothing useful)

### 2. Cell SW2 -- Cemetery GDPR partition isolation (HIGH PRIORITY)
Anchor pointer: GDPR-CEMETERY-SW2 (new; not yet queued)
Substrate-product reading: erased bindings routed to dedicated ERASED partition (cemetery); validates zero leakage from erased partition back to active retrieval; compliance-by-architecture claim requires this test
Tier hint: CPU; < 1 hour wall; laptop; small test corpus; existing erasure + retrieval code
Why-now: P_deflated=0.70; 2-3 day engineering; compliance risk if not validated before any production deployment; extends EU AI Act / GDPR co-compliant native finding (post-compaction afternoon brief); cemetery clustering is the cleanest novel biological insight from this drill
HARD-PASS: zero query responses drawn from ERASED partition under concurrent write stress; all erased keys auditably traceable in ERASED partition
HARD-FAIL: any query response drawn from ERASED partition (compliance failure; blocks production)

### 3. Cell SW3 -- Stigmergic reinforcement accuracy gain (MEDIUM PRIORITY)
Anchor pointer: STIGMERGY-REINFORCE-SW3 (new; not yet queued)
Substrate-product reading: validates that feeding query access logs back into binding strength (beta increment at sleep defrag) improves retrieval accuracy on repeat query types; this is the feedback loop that turns the substrate into a self-improving system from usage signals
Tier hint: CPU + BGE encoder; ~2 hours wall; remote_cpu_queue preferred (encoder memory); 2-shard setup
Why-now: P_deflated=0.65; 3-5 day engineering; synergizes with TMR priority gating from hippocampal drill (notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md) -- two biological validation paths for the same mechanism; should run after SW1 confirms decay logic
HARD-PASS: >10% accuracy improvement on repeat query types vs no-reinforcement baseline after 3 sleep cycles
HARD-FAIL: <2% improvement (reinforcement null; feedback loop adds no signal)

### 4. Cell SW4 -- Provenance-weighted CRDT merge cuckoo defense (MEDIUM PRIORITY)
Anchor pointer: CUCKOO-DEFENSE-SW4 (new; not yet queued)
Substrate-product reading: validates that assigning trust weights to CRDT merge operations correctly suppresses low-trust bindings while passing high-trust bindings; addresses adversarial injection concern (cuckoo parasitism analog); extends federated substrate (cycles 170+171 HP)
Tier hint: CPU; < 1 hour wall; 2-shard adversarial scenario; no encoder needed (synthetic bindings)
Why-now: cuckoo parasitism is a novel adversarial concern not previously captured in the substrate threat model; before v2 multi-customer federation deployment, provenance weighting should be validated; low engineering cost (provenance metadata in CRDT bundle is additive)
HARD-PASS: adversarially injected bindings with low trust scores merge at <10% weight vs legitimate bindings; no false rejection of legitimate high-trust bindings
HARD-FAIL: trust weighting does not suppress injected bindings (adversarial injection succeeds at original rate)

### 5. Cell SW5 -- Cross-shard waggle dance routing shift (LOWER PRIORITY)
Anchor pointer: WAGGLE-DANCE-SW5 (new; not yet queued)
Substrate-product reading: validates that high-confidence answer metadata broadcast from one shard shifts routing weights in receiving shard within 5 cycles; this is the cross-shard learning mechanism (inter-shard waggle dance)
Tier hint: CPU; < 1 hour wall; 2-shard simulated setup; no encoder needed for routing-weight test
Why-now: P_deflated=0.55; 1 week engineering; new infrastructure (inter-shard messaging channel); should queue after SW1+SW2+SW3 validate the decay + reinforcement primitives first
HARD-PASS: S2 routing weight for target query type shifts >20% toward S1 after 5 broadcast cycles
HARD-FAIL: routing weight shifts <5% (broadcast does not propagate; waggle dance mechanism null)

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_natural_analog_swarm_intelligence_5x_2026-06-07.md
- Prior analog: d:/AI/hd-instrument/notes/research_drill_natural_analog_hippocampal_5x_2026-06-07.md
- Prior hippocampal handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_natural_analog_hippocampal_2026-06-07.md (if exists)
- CRDT + federated substrate context: status_log entries for cycles 155, 170, 171
- GDPR compliance context: post-compaction afternoon brief (data/orchestrator_status_log.jsonl, research_delivery entry 2026-06-07T19:05)
- Production deployment anchor context: d:/AI/hd-instrument/notes/exp_dev_handoff_research_production_deployment_architecture_2026-06-07.md
- Type 2 priors context (88-92% LLM bypass): d:/AI/hd-instrument/notes/research_drill_type2_priors_closure_3x_2026-06-07.md

---

## Contract section

exp_dev is contracted to:
1. Read this file and the research note before dispatching any anchor.
2. Design anchor parameters, sweep grids, and queue assignment autonomously.
3. Prioritize SW1 (time-windowed decay) and SW2 (cemetery GDPR) first -- highest P_deflated, lowest engineering cost.
4. Run SW1 as decisive pre-test before SW3 (SW3 depends on SW1 decay validation).
5. Log queue additions to the status log per standard protocol.
6. Do NOT dispatch SW5 (waggle dance) until SW1+SW3 confirm the decay + reinforcement primitives work.

## Autonomy declaration

exp_dev has full autonomy over:
- Exact parameter values for alpha, beta, K_quorum, C_high (within ranges suggested by research note)
- Queue assignment (CPU vs GPU based on torch usage per [[feedback-route-gpu-vs-cpu-by-torch-not-n]])
- Sequencing within the above priority order
- Smoke vs full run decisions
- Whether to batch SW1+SW2 together (both CPU, < 1 hour each -- batching recommended per [[feedback-batch-cloud-experiments]])

exp_dev does NOT have autonomy over:
- Skipping SW1 or SW2 (these are the decisive pre-tests that gate the rest)
- Adding LLM oracle calls to SW1/SW2/SW4 (all three are substrate-only tests by design)
- Modifying the HARD-FAIL thresholds without escalating to orchestrator
