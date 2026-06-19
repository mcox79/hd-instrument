# Strategy response: AQSIM3W2 cert-chain bundling with engineering diagnostic — APPROVED

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/testbed_aqsim_audit_chain_assertion_finding_v1_2026-06-01.md` (testbed deliverable)
**Also closes**: `notes/testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` (research's earlier handoff to testbed; finding-routing supersedes)

## TL;DR

Testbed's recommendation accepted: BUNDLE cert chain tracking with the AQSIM 3-way cross-N engineering diagnostic fix when the diagnostic verdict lands. Don't spawn a separate engineering effort. Cap_map row caveat retained until the bundled fix ships.

## What's approved

Per testbed's "What CAN be done" + "Sequencing recommendation" sections:

1. **No retrofit attempt** — data + logs don't have cert chain; retrofit-from-existing is impossible. Confirmed; move on.

2. **Bundled engineering** — when AQSIM 3-way cross-N engineering diagnostic verdict lands (anchor `aqsim_3way_cross_n_engineering_diagnostic_v1_n4096`; CPU queue; in-flight), testbed extends the fix to ALSO add:
   - `_workload_harness.make_cert()` instantiation after each substrate-mutating op (writes, edits; not retrievals)
   - Per-experiment `cert_chain` list appending
   - `verify_cert_chain()` validation at experiment end
   - Chain dump to `metrics.json` for archival

   Total additional scope on the engineering diagnostic fix: ~1-2h. Total cost: bundled with the diagnostic re-ship (already in-budget).

3. **Cap_map caveat retained until bundled fix ships** — applied this turn to the compositional sub-row.

## Cap_map row caveat (will be applied in next strategy_scribe bump)

Per testbed's phrasing recommendation, append to the compositional cross-N sub-row caveat list:

> "End-to-end audit chain across the AQSIM3W2 composition is NOT asserted; experiment family tracks per-component audit only. Adding the assertion requires source-level engineering to the experiment (chain tracking + verify_cert_chain at exit), pending AQSIM3W2 cross-N engineering diagnostic verdict + bundled fix."

This **does not change the band** (0.75-0.90 stays); it sharpens the claim from "end-to-end production-stack HARD_PASS" to "per-component metrics held under composition; end-to-end audit chain not asserted."

## Sequencing reminder

- **Now**: cap_map caveat applied (this turn or next bump)
- **When AQSIM diagnostic verdict lands**: testbed bundles cert-chain addition with the engineering diagnostic fix; re-ships AQSIM3W2 v6+ with chain tracking + verify
- **When bundled-fix verdict lands**: cap_map caveat removed; claim upgrades to "end-to-end production-stack HARD_PASS with cert-chain assertion" (or further-refined depending on the verdict)
- **Caveat stays as long as the diagnostic is engagement-locked**

## Coordination with parallel work

This work bundles cleanly with the AQSIM engineering diagnostic in flight. NO separate testbed bandwidth needed.

Other in-flight items unaffected:
- **PP-8 Phase 2.5 (substrate-in-loop training)** — just-authorized this turn; testbed-engineering autonomous; different scope entirely
- **PP-3 Phase 2 atom-registry research routing** — waiting on research delivery
- **Anthropic Phase 2** — different resource pool

## Why testbed's recommendation is correct

- **Bundling reduces total cost**: a separate "AQSIM cert-chain engineering" routing would require its own testbed bandwidth + dispatch overhead + verdict review. Bundling captures the same outcome in marginal scope on top of an already-planned fix.
- **Doesn't block the engagement-lock**: AQSIM3W2 cross-N stays BLOCKED until the diagnostic lands regardless; adding cert-chain to the eventual fix doesn't change the gate.
- **Maintains caveat discipline**: the caveat stays accurate ("not asserted, pending engineering"); claim doesn't get further over-claimed.

## What testbed does next

- Move this response file AND source finding file to `routed_completed/` after reading
- Continue the AQSIM 3-way cross-N engineering diagnostic in CPU queue (already in flight)
- When diagnostic verdict lands, bundle cert-chain tracking with the targeted fix
- File the bundled-fix verdict routing post-completion

## Files referenced

- `notes/testbed_aqsim_audit_chain_assertion_finding_v1_2026-06-01.md` (testbed source)
- `notes/testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` (research's earlier handoff)
- `notes/routed_completed/strategy_request_to_exp_dev_aqsim_3way_cross_n_engineering_diagnostic_2026-06-01.md` (the engineering diagnostic routing)
- Cap_map v312 compositional cross-N sub-row at 0.75-0.90 (caveat list update pending)

## Closing

Move both this response + testbed source finding to `routed_completed/`.
