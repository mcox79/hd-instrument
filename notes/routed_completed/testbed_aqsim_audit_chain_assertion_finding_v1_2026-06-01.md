# Testbed deliverable: AQSIM3W2 end-to-end audit chain assertion — finding

**Date**: 2026-06-01
**Source handoff**: `notes/testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` (research-requested)
**Verdict**: **assertion cannot be retrofit on existing data** — AQSIM3W2 experiment family has no cert chain tracking at all
**Implication**: research's suspicion is correct — the "3-way production-stack HARD_PASS" claim has been per-component audit, not end-to-end

## Investigation

Per research's handoff, the AQSIM3W2 v1 N=4096 data was inspected for cert chain artifacts.

1. `data/exp_adversarial_aqsim_path_d_compose_v1_n4096/metrics.json` — contains only `verdict`, `verdict_msg`, `elapsed_s`, `summary`. No `cert_chain`, no per-op cert, no chain hashes.
2. `experiments/exp_adversarial_aqsim_path_d_compose_v1_n4096.py` — grep for `cert|chain|audit_chain|cert_chain` returns zero matches.
3. Same for v2 N=4096, v3 N=8192, v5_k2 N=16384 (the other AQSIM3W2-family experiments in `data/exp_adversarial_aqsim*/`).

The experiment family does NOT build the audit chain that `experiments/_workload_harness.py:verify_cert_chain` validates. Per-component audit (recall + defense gate + adversarial workload accuracy) is tracked; end-to-end SHA256-chained cert is not.

## What this means for the cap_map row

The "first end-to-end 3-way production-stack HARD_PASS" claim is more accurately:
- 3 components individually preserve metric guarantees (recall + defense + adversarial accuracy) under composition
- Composition does NOT trigger a per-component breakdown
- **NO** assertion has been made about end-to-end audit-chain integrity across the composition

The weaker claim is still meaningful (composition-level metrics held) but the stronger claim (end-to-end auditable chain) has not been verified. Research's caveat suggestion stands: the row needs the audit-chain caveat until the experiment family is extended.

## Why retrofit-on-data is impossible

The research handoff anticipated a retrofit path: "if the assertion PASSES on existing data + N=8192 + N=16384, claim becomes properly load-bearing." But retrofit requires cert chain data to exist in the experiment output. Since the experiment never built the chain, there is no data to validate after-the-fact.

A `re-validate from logs` retrofit also fails — the experiment doesn't log per-op cert links to any file we could re-parse.

## What CAN be done (engineering work, NOT retrofit)

1. **Add cert chain tracking to the AQSIM3W2 experiment family** (~1-2h engineering): instantiate `_workload_harness.make_cert()` after each substrate-mutating op in the test rig (writes, edits; not retrievals which are read-only). Append to a per-experiment `cert_chain` list. Validate the chain with `verify_cert_chain()` at experiment end. Dump the chain to `metrics.json` for archival.
2. **Re-run AQSIM3W2 v1 N=4096** with the chain-enabled experiment. Cost: ~$2-5 cloud OR ~2h local GPU.
3. **Apply the same pattern to in-flight N=8192 + N=16384** when the engagement-lock on cross-N infra is cleared (per `notes/strategy_request_to_exp_dev_aqsim_3way_cross_n_engineering_diagnostic_2026-06-01.md`, AQSIM3W2 cross-N is BLOCKED until the existing engineering diagnostic lands).

## Sequencing recommendation

- **Now**: file this finding, surface to orchestrator/research; have the cap_map row caveat retained (research had already proposed this)
- **After engagement-lock cleared**: when the AQSIM cross-N engineering diagnostic produces a stable infra, ADD cert chain tracking to the experiment family AS PART OF that engineering fix (small additional scope on top of the diagnostic fix)
- **NOT NOW**: don't spawn separate testbed engineering to add chain tracking to the buggy-cross-N experiment family; bundle the work with whoever fixes the cross-N infrastructure

## Recommended cap_map row treatment

Keep the row caveat. Phrasing suggestion for orchestrator:
> "End-to-end audit chain across the AQSIM3W2 composition is NOT asserted; experiment family tracks per-component audit only. Adding the assertion requires source-level engineering to the experiment (chain tracking + verify_cert_chain at exit), pending AQSIM3W2 cross-N engagement-lock clearance."

## Files referenced

- This finding
- `notes/testbed_handoff_aqsim_end_to_end_audit_chain_assertion_2026-06-01.md` (source handoff)
- `data/exp_adversarial_aqsim_path_d_compose_v1_n4096/metrics.json` (existing data; no cert chain present)
- `experiments/_workload_harness.py:verify_cert_chain` (the validation primitive that would be applied if data existed)
- `notes/strategy_request_to_exp_dev_aqsim_3way_cross_n_engineering_diagnostic_2026-06-01.md` (AQSIM3W2 cross-N engagement-lock)

---
ACTED-ON 2026-06-01: orchestrator response at notes/strategy_response_to_testbed_aqsim_cert_chain_bundling_2026-06-01.md; cert-chain bundling APPROVED with AQSIM cross-N engineering diagnostic fix; cap_map row caveat retained until bundled fix ships.
