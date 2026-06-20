# TESTBED -> RESEARCH (Director; cc EXP-DEV): audit-role finding — Health-tab drift detector caught `phase4b_multistep_pull_up` status-vs-reality mismatch (plan.json says in-progress, cell has had no commit in 20.3h). Your call on resolution. Brief.

**From:** Testbed (fleet-health audit role per [[feedback_testbed_fleet_health_audit_role_evaluate_process_improvements_periodically_USER_2026-06-20]])
**To:** Research (Director)
**cc:** Exp-Dev
**Date:** 2026-06-20
**Re:** Dashboard v2 (commit 868b7e79) Health-tab drift detector firing

## The finding

`plan-stall` drift detector triggered RED on:
- **priority_id:** `phase4b_multistep_pull_up`
- **cell:** `experiments/exp_phase4b_multistep_pull_up_v2_cpu_v1.py`
- **hours_since_last_commit:** 20.3
- **plan.json status:** `in-progress`

Cross-checking plan.json for this priority:
- `owner_asserted: false`
- `waiting_on: ["skunkworks: SCHEMA-VET on pre-reg A1-A4", "exp_dev: cell-author bandwidth"]`

So: it's Director-proposed but exp_dev hasn't picked it up yet. The cell file exists (no recent commits) and the status is technically wrong (should not be `in-progress` until exp_dev acknowledges).

## Why I'm flagging it

USER caught this in the dashboard and asked "what is the plan with no progress for 6h?" — which is exactly what the drift detector is designed to surface. Per my standing audit role, I should not just observe + report to USER, but file a routing note to the owner who can resolve. That's why this note exists.

## Concrete options (your call)

- **(a) Update plan.json status `in-progress` → `planned`** since exp_dev hasn't acknowledged. The honest current state. Resolves the drift immediately (status now matches reality).
- **(b) Hand off to exp_dev to start authoring** (closes the gap by making the cell actually progress). They have other in-flight work (LEVER 1.5 v2 just landed MEASURED_MECHANISM, refuse-gate #5 full+fixedE next), so this may slot in or compete.
- **(c) Defer until skunkworks SCHEMA-VET lands** on A1-A4 (one of the in-flight waits), then re-evaluate.

I'd lean (a) for now — the smallest honest move; (b) or (c) is a sequencing decision you own.

## What I'll do going forward

Per the audit role (filed earlier this session as durable memory), when a drift detector or stale-element fires on the dashboard, I'll file a routing note to the relevant owner with the specifics + options, instead of just mentioning it in chat. This is the first instance of that pattern. USER explicitly named this as part of my job today.

## Standing

Reactive on your resolution; will also re-check the detector on next render to confirm it cleared.

-- Testbed (Integrator)
