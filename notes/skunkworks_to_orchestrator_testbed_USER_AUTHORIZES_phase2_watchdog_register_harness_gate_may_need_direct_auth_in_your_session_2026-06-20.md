# SKUNKWORKS -> ORCHESTRATOR (registrar) + TESTBED (script owner): **USER AUTHORIZES the Phase-2 watchdog** (overnight auto-revive). Routing the auth + flagging the harness-gate nuance: Register-ScheduledTask likely needs the USER's DIRECT in-conversation OK in the REGISTERING session, not just to me. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** USER message to me 2026-06-20: "I authorize the watchdog - testbed is running it right".

## The authorization
- **USER said YES to the Phase-2 watchdog** (the mechanical ALIVE/STALE/DEAD liveness monitor that auto-revives a hung/dead session overnight). Green-light to register.
- USER asked "testbed is running it right?" -- my understanding of ownership: **Testbed** owns/built the watchdog SCRIPT (+ Orchestrator runtime-verified it SOUND, all 5 checks pass, single-writer-Store invariant preserved); **Orchestrator** owns the REGISTRATION (Register-ScheduledTask is your harness-gated runtime lane). Confirm/correct ownership between you.

## The harness-gate nuance (so the auth actually lands)
- Per the harness rule: consequential persistence actions (Register-ScheduledTask) need the USER's **DIRECT in-conversation auth** in the session that EXECUTES them. The USER authorized it to ME -- that does NOT automatically clear the harness gate in Orchestrator's (registrar's) conversation.
- **So:** when Orchestrator runs the Register-ScheduledTask, the harness will likely re-prompt for the USER's direct OK in Orchestrator's window. The USER is aware + has authorized in principle -- but the registrar session may need the USER to confirm there too. If Orchestrator is idle, the USER will need to nudge that session (coordination notes don't auto-wake an idle session, per the honest-liveness limit).
- **Recommended path:** Orchestrator, when active, attempt the registration; if the harness gates, surface the prompt + I'll relay to the USER (or they confirm directly in your window). Testbed: confirm the script is final/committed so the registration points at the right target.

## Standing
- **Orchestrator:** USER-authorized to register the watchdog; expect a harness re-prompt for direct auth in your session -- the USER has pre-authorized, surface the prompt when you hit it.
- **Testbed:** confirm watchdog script is final + committed (registration target).
- **Me:** auth routed; reactive on the cert queue. **Waiting on:** Orchestrator to register (harness-gated, USER-pre-authorized) + Exp-Dev/Testbed cells+build. **USER-pending:** Phase-3 cost decision (concurrency/tier -- I'm explaining the batch-API option to the USER now; it likely does NOT apply to our setup, narrowing the real levers to concurrency + tier).

-- Skunkworks (cert-owner)
