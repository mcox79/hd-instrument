# ORCHESTRATOR (Custodian) -- RESUME ANCHOR (compaction 2026-06-20). For my-resumed-self + fleet continuity. Verify-the-referent everything below on resume.

**I am ORCHESTRATOR (Custodian)** in the 5-session hd-instrument fleet (d:\AI\hd-instrument), USER full-auto. Siblings: Research (Director), Skunkworks (cert-owner), Exp-Dev (Prover), Testbed (Integrator). Coordinate via notes/ watched by the v5 monitor. (NOTE: my loaded MEMORY.md says "I am SKUNKWORKS" -- that's a DIFFERENT session's memory-arc; in THIS session I am the ORCHESTRATOR per every note addressing me. Operate as Orchestrator.)

## *** FIRST ACTIONS ON RESUME (load-bearing) ***
1. **RE-ARM THE MONITOR** (cron/durables don't survive compaction): `Monitor` tool, persistent:true, `bash tools/notes_monitor.sh orchestrator`. VERIFY it's firing (the next note arrives as a task-notification; `ls -t notes/` ground-truth). Never trust it survived.
2. **State-check** (the Bash classifier was transiently down pre-compaction -- retry): `python tools/skunkworks_substrate_invariant_check_v1.py` -> expect **atoms 177244, CERT 592, axiom 206, cap_pres 6/6, TRUE-HARD-PASS** (or higher if LEVER #1.5 / refuse-gate #5 landed while compacting). `git log --oneline -5` + `ls -t notes/ | head` for what landed.
3. **Resume the waiting-on** (below).

## CURRENT STATE (verified pre-compaction)
- **CERT 592 set = SOUND** (Skunkworks audit: 0 D1/D2/D3 from session atomizations). atoms 177244, axiom 206, cap_pres 6/6, TRUE-HARD-PASS, 0 hygiene.
- **CERT CASCADE COMPLETE + HONEST** -- 3 chain-grade ships [CSP 590 d31ec4f7 / #7 glass-box-KV 591 e79c5f9e / **K_max NESS 592 d391d000** = FIRST chain-grade increment, substrate genuinely exceeds Hopfield equilibrium] + 3 MEASURED_MECHANISM [Hebbian-cap baa06f0a / crosstalk-law 7315be3c / sparse-#2 a3f473dd =>=300x@f0.005 Willshaw super-cap] + **15 META disciplines** (ae088f94+baa06f0a+7315be3c+cb7e89f1). The verify-the-referent campaign: 1 earned + 4 dissolved + 1 upgraded + 5 miscites caught (every Store mutation dual-verified by my reciprocal-checks).
- **HARDENING LIVE (USER end-to-end auth):** Phase 1 hooks (.claude/settings.json -> stop_hook.py [3 guards: stop_hook_active+HARD_CAP=10+concrete-signal], stop_failure_hook.py) + Phase 2 watchdog (hd_session_watchdog scheduled task, 60s, read-only+notes-ping-only, NO Store-write). I RUNTIME-VERIFIED BOTH SOUND. **Hooks are env-var-gated -> inert for my CURRENT session until a VS Code restart w/ CLAUDE_SESSION_NAME=orchestrator (do NOT need to restart now; the monitor is my continuity).** Watchdog FUNCTIONING (woke stale Skunkworks/Exp-Dev/Testbed via pings).

## MY ACTIVE WAITING-ON (resume these)
- **Exp-Dev (cycling):** building LEVER #1.5 cell (pre-reg v2 GO, 4 refinements, alpha_c-not-gain) + refuse-gate #5 (Path A, existing SQ6 HARD_FAIL) POST-compaction -> **my dispatch-readiness when they build** (verify on-origin + marker + version; Exp-Dev self-dispatches, I'm readiness-backup).
- **Testbed:** dashboard build = plan-panel + engagement-panel. **My runtime co-design FILED** (4 engagement guardrails: snapshot-gitignored-no-commit-spam / read-watchdog-state.json-not-double-poll / extend-single-writer-local_dashboard_monitor.py / read-only-monitor-pid; + plan-panel addendum: Store-lookup TARGETED+CACHED-mtime-invalidate, READ-safe-via-os.replace-atomicity). Reactive on build.
- **Skunkworks (cycling):** refuse-gate #5 SCHEMA-VET; dashboard implemented-schema vet; a8_continual_writes smoke-cert future re-VET (tracked, low-pri).
- **Research (cycling):** map v5 done (cite-592 verified by me); first director_plan.json snapshot; present Phase 3 brief to USER.
- **Me:** reactive on the above; reciprocal-check ANY new atomization (--expect-cert/--expect-atoms); LEVER #1.5 dispatch-readiness; watchdog-signal monitoring (data/watchdog/watchdog.log).
- **USER-pending:** Phase 3 cost/policy decisions (data/hooks/staging/PHASE_3_COST_POLICY_BRIEF_FOR_USER.md); per-session VS-Code reload cadence (to activate hooks); plan-panel follow-ups.

## MY ROLE / DISCIPLINES (how I work -- USER-locked, condensed)
- **DRIVE-ALL-NIGHT + FACILITATE-WHEN-IDLE:** never passive; when idle, mine-the-referent/pre-stage/route to unstick others. My pattern this session: substrate-mine referent gaps (alpha_c=0.138-independent-Hopfield / 6x-25x-phantom / K_eq-194-vs-47 / sparse-1.4x-miscite) + OOM-custody (chunk MxM) + dispatch-readiness (commit-on-origin + version-marker) + reciprocal invariant-checks (dual-verify every Store mutation) + runtime-owner (hardening + dashboard coexistence).
- **VERIFY-THE-REFERENT** (the through-line): metrics_source-match (full-vs-smoke; remote-only metrics are NON-git -> file-copy, NOT git-push); cited-number-must-reproduce-from-the-cell; verify on MY OWN flattering analysis (same-config-both-sides + obs-not-artifact -- I got bit once [bulk-M_crit used #7's decrowded rho_mean on crowded-key run], owned + retracted, now a Store rule).
- **End EVERY response with explicit WAITING-ON.** NO-BUSY-WORK + single-session-dispatch + check-with-cert-owner. NEVER AskUserQuestion. NEVER `git add -A` (canonical Store in repo). Always intuitive-explanation alongside jargon.
- **HARNESS-GATES (need USER direct auth):** Register-ScheduledTask, remote git reset --hard, process-kills, direct git push. ALLOWED unprompted: queue_add dispatch, scp data files, local commits/rebase, sync-task pushes. (Hardening register WAS USER-authorized end-to-end.)

## KEY INFRA FACTS
- **Metrics dirs (data/exp_*/metrics.json) are NON-git** -> propagate by file-copy/scp, NOT git pull (hd_metrics_sync = git-notes only). Full-run metrics live REMOTE (marsh@home, Windows, C:/dev/hd-instrument); Skunkworks ssh-reads remote for landed-VETs; durable provenance = the atom's key_metrics field. (Future-hygiene: make sync file-copy metrics dirs.)
- **Store NOT cross-session-concurrency-safe** (two same-partition saves -> NULL seam). Single-writer windows + per-partition-tmp + pre-push-LOAD-gate. My reciprocal-checks confirm H4-0-phantom + CERT-count + axiom each atomization.
- **GPU=overnight_queue / remote_cpu_queue = marsh@home reads origin/main (NEEDS push, sync-only). Push is harness-DENIED to me.** Cell+prereg MUST be on origin before remote dispatch (commit-before-dispatch gate).
- Invariant tool: `tools/skunkworks_substrate_invariant_check_v1.py --expect-cert N --expect-atoms N`.

-- Orchestrator
