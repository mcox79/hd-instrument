# Routing: orchestrator -- PP-3 drill sequencing verification request

**From**: testbed session
**To**: orchestrator (strategy)
**Date**: 2026-06-01
**Type**: scope-verification before dispatch
**Closes**: NOT YET (kept open until orchestrator confirms)
**Source handoff**: `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`

## What testbed proposes

Per the handoff's 6-item deliverable spec, testbed proposes a 3-phase
sequence with an early-exit gate at Phase 1 if the data says rotation
isn't needed at production scope.

### Phase 1: scoping pass (~2-3 hours)

- SCP V2 cert-chain artifacts back from remote
  `C:\dev\hd-instrument\data\exp_sustained_workload_24h_baseline_v1_n4096\`
- Fit empirical growth model: bytes/hour vs ops/hour at N=4096
- Project storage at production scope: 1M-ops/day -> 100M-ops/month
- Decision: is rotation strictly necessary at production scope or is
  natural growth tractable?

**Early-exit branch**: if production-scope projection is, say,
<10 GB/month uncompressed, rotation is OPTIONAL not REQUIRED.
Deliverable then describes "natural growth tractable; rotation
becomes compliance-optimization not capacity-optimization" with the
empirical fit + projection numbers.

**Continue branch**: if production-scope projection is large
(>100 GB/month or harder limits), proceed to Phase 2.

### Phase 2 (continue branch only): compression + rotation design (~3-4 days)

- 3 compression candidates: delta-encode adjacent cert hashes,
  payload dedup, summarization-to-checkpoint-hash
- 3 rotation strategies: hourly checkpoint, op-count checkpoint,
  hierarchical sliding-window
- Compliance mapping: GDPR right-to-erase (30-day max), HIPAA (6yr),
  SOC2 (7yr); which rotation strategies hit each window
- Per-strategy: queryability cost (can verifier replay from rotated
  state?), storage cost at production scope, recovery latency

### Phase 3 (always): verifier-replay test (~1-2 days)

- Take a slice of rotated cert-chain
- Re-run substrate verifier against the rotated state
- Confirm cert-chain still validates against original substrate
  baseline (this is the load-bearing correctness gate; without this
  rotation breaks the substrate's audit guarantee)

### Deliverable

`notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` with all 6
items from the handoff spec + Phase-1 empirical fit + Phase-3
verifier-replay outcome + cap_map PP-3 row recommendation.

## Total wall

- Early-exit at Phase 1: ~3-4 hours total (Phase 1 + minimal
  deliverable + verifier-replay sanity check)
- Full path: ~6-8 days (1-2 weeks per handoff estimate; faster
  because Phase 1 narrows scope before bigger design work)

## Open questions for orchestrator (verify before dispatch)

1. **Early-exit gate**: is testbed-side "rotation is OPTIONAL not
   REQUIRED" verdict acceptable as a Phase-1 deliverable, or does
   orchestrator want the full design regardless of the growth shape?
   Default: testbed will deliver full design if growth-projection
   surfaces production-scope strain, else surface the early-exit and
   wait for orchestrator's direction on whether to design anyway for
   compliance-optimization framing.
2. **Compliance window mapping**: testbed's read is GDPR right-to-erase
   = 30-day max retention, HIPAA = 6yr, SOC2 = 7yr. Confirm or
   redirect; this is a load-bearing assumption for Phase 2.
3. **Verifier-replay scope**: testbed will test "rotated state still
   validates against original substrate baseline" (correctness gate).
   Should the test ALSO include "rotated state allows reconstruction
   of full audit trail for a specific GDPR right-to-erase request"
   (which goes beyond verifier-replay)? Default: testbed scopes to
   verifier-replay only; orchestrator can dispatch a follow-on for
   audit-trail reconstruction.
4. **Cap_map move signal**: if Phase 1 surfaces early-exit, testbed
   will recommend "PP-3 row LIFT 0.55-0.70 -> 0.65-0.80 because
   production-scope growth is tractable (specific numbers in
   deliverable)" + caveat list update. If full design path produces
   compression-ratio + queryability evidence, recommend further LIFT.
   Confirm this is the right LIFT shape, or redirect.
5. **Sequencing relative to other in-flight items**: testbed has
   bandwidth right now for Phase 1 (no other testbed-side dispatched
   work in flight). Confirm or redirect; the handoff says PP-3 is
   parallel to Phase 2 Anthropic ($20-50) which is still awaiting
   user auth, so PP-3 has the floor right now.

## What testbed will do absent orchestrator response

Testbed will START Phase 1 (scoping pass) within ~30 minutes of
filing this routing. Phase 1 is reversible (data analysis only; no
state changes to substrate or cap_map; no incremental cost). If
orchestrator surfaces an objection or redirect during Phase 1,
testbed pauses and re-scopes.

The verification routing is the safety check on full-scope
commitment to Phase 2 + 3 (a 1-week-plus engineering build).
Orchestrator's response to questions 1-5 above gates the Phase 2
commit.

## Files of interest

- This routing
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`
  (source handoff)
- V2 sustained_workload data on remote (per handoff)
- Cap_map v305 PP-3 row + PP-2 row (just LIFTed) for context

## Closing this routing

Orchestrator response: confirm or redirect on questions 1-5; testbed
moves this file to `notes/routed_completed/` after orchestrator reply
lands.


---

Acted-on 2026-06-01: 5 questions answered via strategy_response_to_testbed_pp3_drill_sequencing_confirmed; testbed authorized to start Phase 1


Acted-on 2026-06-01: 5 questions answered via strategy_response_to_testbed_pp3_drill_sequencing_confirmed
