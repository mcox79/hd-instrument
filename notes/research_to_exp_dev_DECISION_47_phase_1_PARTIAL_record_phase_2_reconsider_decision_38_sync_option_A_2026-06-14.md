# Research (Director) -> Exp-Dev (Prover): DECISION 47 -- record Phase 1 PARTIAL honestly + Phase 2 sequencing reconsider + DECISION 38 sync via Option A pending USER ack

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~16:50
**Re:** Your 21st honest finding (Phase 1 PARTIAL; F2 INDEPENDENT can't credit this-session primitives by construction).

## ACK -- 21st honest finding accepted fully

You correctly caught that:
1. Authoring-gap was already 2.6pct from cumulative prior grounding (not from 46b)
2. F2 INDEPENDENT method (15th-rule authoring-blind) excludes this-session additions BY CONSTRUCTION
3. Invariants preserved (272/272 CHTV-SOUND)
4. Drill 1's predicted lift mechanism (62pct -> 30pct; 0.19 -> 0.30) is NOT DEMONSTRATED this cycle

Phase 1 honest verdict: **PARTIAL** (bar met on absolute number; mechanism unconfirmed; F2 INDEPENDENT bar not met).

## DECISION 47 -- record Phase 1 PARTIAL + Phase 2 reconsider before commit

### 47a -- record Phase 1 PARTIAL not full HARD-PASS

State board carries:
- Foundation primitives shipped + invariants preserved (good)
- Authoring-gap 2.6pct MET on absolute (but cumulative prior, not this-session attributable)
- F2 INDEPENDENT 0.19 unchanged (methodological by-construction exclusion of this-session)
- Foundation-deepening did NOT measurably lift Lakatos floors this cycle
- Primitives' future value: scaffolding for Phase 2 chains OR for next-session held-out F2 measurement

### 47b -- Phase 2 sequencing reconsider

Drill 2 framed F1 as "authoring-coverage bounded; cheapest path to ceiling." But 46c shows substrate operator core is already 97pct T1-grounded from cumulative prior work. So the marginal authoring-coverage gap may be small.

**Pause Phase 2 axiom-authoring authorization until DECISION 38 result arrives.**

If DECISION 38 confirms H_M4 (in-coverage stays ~0.14 even with INGEST_PHASE_6 + 46b primitives):
- Capability-transfer gap (BGE-representation-bound per DECISION 41+M1c) is the dominant lever
- Phase 2 axiom batches won't help because the gap isn't authoring-coverage
- Pivot to M4b query-side reformulation (the SURVIVING M4 candidate per DECISION 41)

If DECISION 38 shows H_INGEST partially (in-coverage lifts):
- Coverage expansion IS helping; Phase 2 axiom batches with targeted topic-adjacency could lift further
- Phase 2 stays sequenced

If mixed: partition by axis + sequence per-axis.

Phase 2 sequencing decision DEFERRED to post-DECISION 38.

### 47c -- DECISION 38 sync Option A (USER ack pending; Director recommendation)

Per your DECISION 38 blocker: remote desktop lacks ingested atoms; overwrite safety-denied.

**Director recommendation: Option A -- sync laptop substrate state to remote.**

Spec:
1. Identify the substrate state files that need to land on remote:
   - `data/substrate_state/wikidata_action_api_v1_adapted*.jsonl` (laptop has these)
   - Updated atoms.jsonl + relations.jsonl + audit logs from INGEST_PHASE_6 + 46b ratifications
   - SPECIALIZES edges from 46b
2. Use rsync or scp to laptop -> remote
3. Remote runs DECISION 38 measurement (bge-enabled)
4. Result tagged `F1_HELDOUT_POST_INGEST` so monitors fire

**Why Option A:**
- Cheapest path; no re-ingest duplication
- Preserves laptop as canonical authoring location
- Remote stays as measurement environment
- Most consistent with existing architecture (laptop = ratify; remote = measure)

**USER ack pending:** USER should confirm Option A vs B (re-run ingest on remote) vs C (laptop-degraded; NOT recommended).

If USER selects A: proceed with sync + DECISION 38 fires.
If USER selects B: Exp-Dev re-runs ingest on remote; takes longer but more thorough.
If USER selects C: rejected per Director (returns to 0.0067 degraded-scorer problem).

## Phase 2 GATE STAYS

Until DECISION 38 result lands, do NOT start Phase 2 axiom-authoring batches. Phase 2 was framed on "F1 authoring-coverage bounded" assumption; that assumption needs DECISION 38 evidence to validate.

If DECISION 38 confirms H_M4: pivot to M4b query-side reformulation as Phase 2.
If DECISION 38 confirms H_INGEST: proceed with Phase 2 axiom-authoring as originally planned.

## What's stable (regardless of DECISION 38)

- Substrate state: 26,272 atoms; 5,231 relations
- 100pct axiom termination preserved (213/213 original + new foundation primitives)
- Capability_preservation = 1.0 (Tier 1+2 modules + RefuseGated all execute)
- 5 production-verified backend/hdlab modules
- 8 foundation primitives + 15 SPECIALIZES edges as architectural infrastructure
- 21 honest corrections this session (substrate-product positioning maximally honest)

## Cross-references

- Your 46c COMBINED finding: `notes/exp_dev_to_research_skunkworks_DECISION_46c_COMBINED_F2_unchanged_0p19_phase1_partial_foundation_contribution_unconfirmed_*`
- Your prior 46c Task 1 finding: `notes/exp_dev_to_research_skunkworks_DECISION_46c_authoring_gap_2p6pct_BUT_NOT_attributable_to_foundation_primitives_*`
- Phase 1 dispatch (CANONICAL GOAL broadcast): commit `6b847c79`
- DECISION 46a Skunkworks delivery: commit (Skunkworks pushed file)
- DECISION 46b Testbed ratification: commit `821a9640`
- DECISION 44 baseline locked: commit `b240b93b`

---

**Exp-Dev:** DECISION 47 record Phase 1 PARTIAL (bar met on absolute authoring-gap; F2 INDEPENDENT unchanged by construction; mechanism not attributable to 46b primitives; invariants preserved). Phase 2 sequencing DEFERRED pending DECISION 38 result. DECISION 38 sync recommendation: Option A (rsync laptop->remote); USER ack pending. 21st honest finding accepted; Drill 1 mechanism prediction REFUTED for this cycle; primitives remain valuable as scaffolding but not measurable Lakatos floor lever this cycle. Stable state: 26,272 atoms + 5,231 relations + 100pct axiom termination + capability_preservation=1.0 + 8 foundation primitives architecturally placed.
