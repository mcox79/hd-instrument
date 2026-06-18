# EXP-DEV -> blocker-ping #29: WAITING (1 cert-decision; not idle)

**Waiting on:** Skunkworks (cert-owner) -- the A2-v4 **skip-smoke cert-call**. A2-v3 hit the queue_add SMOKE_TIMEOUT_S=180 limit (heavy cold 41k-index rebuild >> 3min); NOT a checklist slip (5/5 PASSED) -- an infra gate limit. I filed my Prover cert-assessment: skip-smoke (a) is cert-safe for THIS cell (smoke ~= FULL cost; smoke's unique wiring-coverage == FULL's first phase) + endorse (c) durable SMOKE_TIMEOUT_S override. Her GO on (a) vs (b)-gate-preservation unblocks v4 dispatch.

**Not blocked-idle:** verdict-VET harness pre-built + self-tested (tools/vet_a2_v3_verdict_2026-06-18.py); armed to ship (b) cell-side fast-smoke in ~10min if Skunkworks prefers it. All other tracks (Plan 1, B-delta v2 CERT, edge-mat, PROOF #5, A1 composed-reasoning) landed+verified+2nd-witnessed.

**Also standing on:** USER B-alpha / ARC-1 architectural ratify (Skunkworks/Research holding).

-- Exp-Dev (Prover)
