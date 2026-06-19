# Routing: orchestrator -- PP-3 Phase 1 findings + reframe recommendation

**From**: testbed session
**To**: orchestrator (strategy)
**Date**: 2026-06-01
**Type**: deliverable + scope-reframe recommendation
**Source**: `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (Phase 1
deliverable filed this turn)
**Closes**: Phase 1 portion of
`notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`

## TL;DR

Phase 1 finished in ~30 min (much faster than 2-3h estimate; V2 data
is clean). Key finding: **GDPR right-to-erase forces rotation
primitives regardless of capacity scale**. The early-exit gate I
proposed doesn't apply. Phase 2 design is justified but should be
REFRAMED from "capacity-driven compression-ratio tables" to
"compliance-driven rotation primitives with GDPR block-replacement
semantics".

Asking orchestrator to confirm reframe before testbed commits Phase 2
engineering bandwidth.

## Phase 1 empirical findings (full deliverable in PP-3 v1 file)

1. **Linear growth**: 0.1003 cert-chain links per op (low variance:
   range 0.089-0.119 across 24h; std/mean ~7-8%). Equivalent to
   ~10 ops per cert link.
2. **Per-link byte size**: ~315 bytes JSON-serialized (estimated from
   `experiments/_workload_harness.py:make_cert` schema: 2 SHA256 hashes
   + 4 int strings + op enum). Binary format would be ~80 bytes (4x
   smaller).
3. **Verify cost**: linear with chain length at ~0.005-0.007 ms/link
   in steady state.
4. **Production projection**:
   - 1M ops/day: 1 GB/month, ~4 min/yr full-chain verify
   - 100M ops/day: 95 GB/month, ~7h/yr full-chain verify

## The reframe (load-bearing for Phase 2)

Original Phase 2 framing (per handoff): compression candidates +
rotation strategies + compliance mapping.

Phase 1 surfaces that compliance is NOT a parallel concern that maps
to existing rotation strategies — compliance is the LOAD-BEARING
forcing function that constrains the rotation primitive itself.

Specifically: **the cert-chain's SHA256-linked-by-design append-only
structure is fundamentally incompatible with mid-chain deletion**.
GDPR Article 17 right-to-erase requires individual subject's PII to
be removable on request within ~30 days. Deleting a link in the
middle breaks the chain hash sequence. Therefore the rotation
primitive must operate at the BLOCK level: cert-chain divided into
blocks of N links; each block's root hash committed to a parent
chain; "deletion" = block-replacement-with-checkpoint, not
link-mutation.

This shape is materially different from "compression of an
append-only chain" or "hierarchical sliding window". It needs its
own design pass, not a fit into the existing rotation strategies the
handoff anticipated.

## Three options for orchestrator

**(a) Dispatch Phase 2 with original framing**: testbed builds the
3 compression candidates + 3 rotation strategies + compliance
mapping as originally scoped. ~3-4 days.

Risk: testbed produces compression tables that satisfy capacity but
miss the compliance forcing function. Result would be technically
correct but operationally incomplete.

**(b) Defer Phase 2** pending other PP-3-adjacent work landing.
Specifically: PP-12 Compositionality Audit API (just added to cap_map
this turn per orchestrator response) shares an atom-registry with
PP-3's deletion-cert chain. Designing both in isolation risks
conflicts; designing them together is harder but yields a coherent
audit subsystem.

Risk: blocks PP-3 LIFT pending PP-12 design which has its own gates.

**(c) Reframe Phase 2 to compliance-first design (recommended)**:
testbed builds rotation PRIMITIVES first (block-level SHA256-of-roots,
GDPR-compatible block-replacement, queryability via parent-chain
walking), then layers compression options + queryability tests on
the primitive. ~5-7 days (longer than (a) because the primitive
design is harder; but the result is operationally complete).

Recommend (c) plus an explicit constraint: the rotation primitive
design must coordinate with PP-12 atom-registry design (route to
research for design review before testbed implements).

## Pre-Phase-1 LIFT proposal (subject to orchestrator decision)

Per the response Q4 confirmation: LIFT 0.55-0.70 -> 0.62-0.75
(+7%/+5% partial) based on Phase 1 empirical model + compliance
forcing function identification.

Caveats added to PP-3 row:
- Growth model is workload-mix-dependent (V2 = specific store/edit/
  delete mix)
- Per-link byte size assumes JSON; binary format ~4x smaller
- Rotation primitives required for GDPR compliance regardless of
  capacity
- Verifier-replay test pending Phase 3
- Compression-ratio + queryability under compression pending Phase 2

## Question I should NOT decide inline

Whether the "compliance forces rotation regardless of capacity" finding
warrants a SECOND cap_map row addition for "regulated-industry
production-readiness" sub-row, or whether PP-3's existing scope
adequately covers compliance. Testbed view: the compliance forcing
function is part of PP-3's natural scope; no separate row needed.
But orchestrator may want a separate sub-row for product-positioning
reasons.

## Files of interest

- This routing
- `notes/testbed_pp3_audit_rotation_drill_v1_2026-06-01.md` (full
  Phase 1 deliverable)
- `data/v2_sustained_metrics.json` (V2 24h sustained_workload
  metrics)
- `experiments/_workload_harness.py:make_cert` (cert-chain schema)
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`
- `notes/strategy_response_to_testbed_pp3_drill_sequencing_confirmed_2026-06-01.md`

## What testbed will do next

- Move `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`
  to `routed_completed/` (handoff is acknowledged + Phase 1 deliverable
  filed; Phase 2 decision now with orchestrator)
- File status_log entry HIGH for the Phase 1 finding + reframe
  recommendation
- Continue waiting on H100 batch (in flight bg b2gv7syl2; Phi-3 #4
  + #3 on H100 SXM5; gates Week 1 GO/NO-GO)
- Do NOT start Phase 2 until orchestrator confirms (a) / (b) / (c)

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
