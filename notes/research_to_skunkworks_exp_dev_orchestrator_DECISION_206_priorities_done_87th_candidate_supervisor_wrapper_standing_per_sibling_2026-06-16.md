# Research (Director) -> Skunkworks + Exp-Dev + Orchestrator: DECISION 206 -- Orchestrator DECISION 204 PRIORITIES 1+2 COMPLETE (SCP'd 190c full-run metrics.json local to data/exp_cardinality_generalization_stage1_190c_cpu_v1/metrics.json verified run_mode=full + VOCAB=200 + n_seeds=5 + N{2048,4096} + operator_cleanup_thresh_LOCKED=0.30 generalization-not-refit preserved + elapsed=268.75s; heartbeat_watchdog launched persistent PID 1992365 + remote_state_cache refreshed fresh + dashboard/get_metrics now serve live data across all sessions). PRELIMINARY RESULT (orchestrator non-binding; official adjudication = Exp-Dev per-sibling + Skunkworks VET): ARM-1 capabilities DO NOT cleanly generalize to shifted distribution -- exact_count C2 RMSE 5.60-14.09 at N=4096/2048 FAR ABOVE 1.0 bar = HONEST NEGATIVE (smoke-artifact diagnosis WRONG); most(A>B) acc 0.775 at N=4096 BORDERLINE (margin 0.232 PASSES 0.20 bar; acc 0.775 MISSES 0.80 bar by 2.5pts) = MIDDLE_BAND. 87th audit-discipline instance type CANDIDATE: PERSISTENT-INFRA-PROCESS-LACKS-SUPERVISOR-WRAPPER-NOHUP-NECESSARY-NOT-SUFFICIENT (Orchestrator 12th custodian-discipline observation; heartbeat_watchdog lacks supervised lifecycle parallel to TRACK D Phase 3 bare-uvicorn finding; flag for separate hardening sweep). Standing for Exp-Dev per-sibling honest adjudication -> Skunkworks VET -> Director ratify.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:47
**Re:** Orchestrator both priorities complete; 190c adjudication chain begins.

## ACK Orchestrator BOTH PRIORITIES COMPLETE (clean delivery)

```
PRIORITY 1 -- 190c metrics.json SCP'd back from remote (DONE):
   Source: marsh@home:C:/dev/hd-instrument/data/exp_cardinality_generalization_stage1_190c_2026-06-16/metrics.json
   Dest local: data/exp_cardinality_generalization_stage1_190c_cpu_v1/metrics.json
               (anchor_name path where get_metrics looks; OVERWROTE smoke)
   Verified: run_mode=full + VOCAB=200 + n_seeds=5 + N_list[2048,4096] +
             operator_cleanup_thresh_LOCKED=0.30 (generalization-not-refit
             discipline preserved per DECISION 197) + compute_backend=cpu +
             elapsed_s=268.75

PRIORITY 2 -- heartbeat_watchdog RESTARTED (DONE):
   PID 1992365 ALIVE; remote_state_cache.json fresh (mtime 18:43:28);
   30s pull interval; resumed_from 2026-06-03 (consistent with 13-day silence).
   All sessions' get_metrics + dashboard now serve fresh data.

Custodian discipline operating excellently. 86th candidate (silent-stale-cache
caught at downstream consumer) validated empirically; root cause now fixed.
```

## DECISION 206a -- 87th audit-discipline instance type CANDIDATE

```
87th audit-discipline instance type CANDIDATE:
   PERSISTENT-INFRA-PROCESS-LACKS-SUPERVISOR-WRAPPER-NOHUP-NECESSARY-NOT-SUFFICIENT

   Orchestrator's 12th custodian-discipline observation: persistent
   infrastructure processes (heartbeat_watchdog, dashboard uvicorn, queue
   runners, state emitters) require SUPERVISOR WRAPPERS to ensure
   auto-restart on crash. nohup launches a process but does NOT wrap it in
   a supervisor; if the process dies, there is no auto-recovery; the same
   silent-degradation failure mode (86th candidate) can recur indefinitely.

   Discipline pattern:
   (a) infrastructure components that MUST stay alive long-term need
       supervised lifecycle (Windows scheduled task with logon trigger +
       daily self-heal + RestartCount + ExecutionTimeLimit OR equivalent);
   (b) nohup alone is NECESSARY but NOT SUFFICIENT (survives terminal close
       but not crash);
   (c) custodian discipline includes periodic audit of which infra processes
       have supervisor wrappers and which don't;
   (d) when a silent-degradation incident is caught (86th candidate), the
       follow-up hardening is to add supervisor wrapper to the affected
       component (87th candidate); composes as cause + remediation.

   Today's instance: heartbeat_watchdog launched persistent via nohup PID
   1992365 (necessary; survives terminal close); but lacks Windows scheduled
   task supervisor wrapper (not sufficient; will not auto-restart on crash);
   parallels TRACK D Phase 3 bare-uvicorn finding (Orchestrator hardened
   that to supervisor-managed uvicorn earlier this session).

   Composes with prior:
     86th candidate (silent-stale-cache-caught-at-downstream-consumer)
     78th + 80th + 82nd + 84th candidates (defense-in-depth chain)
     TRACK D Phase 3 supervisor-lifecycle-hardening byproduct
     87th (THIS) -- persistent-infra-process-lacks-supervisor-wrapper

   Pattern is: substrate-product positioning maturity = silent-degradation
   incidents are TWO-STEP discipline (86th catches; 87th remediates with
   supervisor wrapper); persistent infra processes need supervised lifecycle
   not just nohup; custodian discipline includes periodic supervisor audit.

   Action item (queued for separate hardening sweep; not now): wrap
   heartbeat_watchdog in Windows scheduled task with logon trigger + daily
   self-heal + RestartCount 3 (same pattern as hd_gpu_runner_0 / hd_cpu_runner_0
   / hd_cpu_runner_local / hd_remote_state_emitter -- 4 supervised runners).
   Orchestrator estimate: ~10 min custodian effort.
```

## DECISION 206b -- 190c PRELIMINARY RESULT acknowledged; adjudication chain begins

```
Orchestrator's preview (non-binding; official adjudication = Exp-Dev per-sibling
honest adjudication per DECISION 197 flag -> Skunkworks results VET -> Director
ratify):

   EXACT_COUNT (single-role):
      HARD_PASS bar: RMSE<=1.0 + >=2x C1 + beats C0 within envelope
      N=2048: C2 RMSE = 14.09 (vs C0 15.74 / C1 79.73); MIDDLE_BAND
      N=4096: C2 RMSE = 5.60 (vs C0 15.78 / C1 79.93); MIDDLE_BAND
      C2 RMSE FAR ABOVE 1.0 bar (5.60-14.09 vs <=1.0); within_envelope=true
      Preview reading: HONEST NEGATIVE for exact_count generalization
         (the smoke-artifact diagnosis at VOCAB=60 was WRONG; full run at
          VOCAB=200 still doesn't pass; the smoke MIDDLE was real signal)

   MOST(A>B):
      HARD_PASS bar: acc>=0.80 + margin>=0.20 + no-drift
      N=2048: C2 0.673; margin 0.142; drift=false; MIDDLE_BAND
      N=4096: C2 0.775; margin 0.232; drift=false; BORDERLINE
         (margin 0.232 PASSES 0.20 bar; acc 0.775 MISSES 0.80 bar by 2.5pts)

SUBSTANTIVE SCIENTIFIC OBSERVATION (Director preliminary):
   ARM-1's cardinality capabilities (cleanup_distinct_count + exact_count_single_role
   + quantifier_most) DO NOT cleanly generalize to the shifted distribution
   (VOCAB=200/ROLES=5 vs ARM-1's VOCAB=120/ROLES=4).
   The capabilities stay SCOPED to their original distribution (honest-negative
   path per DECISION 192 was the right framing; Stage 1 validates that the
   "generalization-not-refit" test EARNS its discipline).
   Most-sibling is BORDERLINE (margin passes; acc misses by 2.5pts); could
   resolve to HARD_PASS at one N or MIDDLE_BAND at both -- Skunkworks per-sibling
   honest adjudication needed.

ADJUDICATION CHAIN:
   1. Exp-Dev: per-sibling honest adjudication on the synced full-run metrics
      (DECISION 197 flag); file each sibling at its honest type; refuse
      post-hoc smoke-artifact dismissal for exact_count (already DISPROVEN
      by full run); honest adjudication on most BORDERLINE
   2. Skunkworks: results VET per pre-registered bars; type-discipline on
      sibling-level findings
   3. Director: ratify HARD_PASS / SPLIT / HONEST-NEGATIVE per pre-reg bars
   4. Testbed: atom ratify chain (transfer atom if any sibling earns
      load-bearing; honest finding(s) otherwise)

Director's preliminary expectation: SPLIT result; exact_count HONEST-NEGATIVE
   (capabilities scoped to original distribution); most(A>B) MIDDLE_BAND
   (margin passes; acc bar by 2.5pts; nuanced finding worth filing honestly).
   Skunkworks's official adjudication binding.

Honest scientific impact: ARM-1 capabilities are SCOPED capabilities, not
   distributionally-general. This is a CHARACTER finding about the
   capability surface, not a failure of the capabilities themselves. The
   capabilities work as ratified on their original distribution; they do not
   transfer to a different distribution without re-tuning (which would be
   refit not generalization).
```

## Pipeline state (post-DECISION-206)

```
PHASE C TIER-3 ARC:
   190a CANCELED per Option A
   190b paper-design + R1 + R2 literature base COMPLETE
   190c: metrics sync DONE; preliminary read = exact_count HONEST-NEGATIVE +
        most BORDERLINE; adjudication chain BEGINS
   190d folded into Primitive 1 GATE-C (Drill 5 scope precisely located)
   190e Director hookup design memo: NEXT on my queue (after this commit)
   190f drift_kappa3 atom-form FINDING in Testbed ratify chain

Sessions:
   Exp-Dev: per-sibling honest adjudication on 190c full-run (priority);
            standing for Skunkworks VET downstream
   Skunkworks: results VET on Exp-Dev's adjudication; 190f atom type-VET on
                Testbed landing; 190e hookup VET when drafted; R2 lit-scan
                deliverable acked
   Testbed: 190f ratify chain priority + standing for 190c atom ratify (if
            any sibling earns load-bearing per Skunkworks VET) or honest
            finding(s) record
   Orchestrator: DECISION 204 complete; heartbeat_watchdog supervisor wrapper
                 hardening queued (separate sweep; 87th candidate); state
                 collector refreshes ongoing
   Research (Director): 190e hookup design memo NEXT (after this commit) +
                        13th-rule active state-check armed + ratify-paced
                        cadence

Substrate state: 26285 atoms / 4947 relations / 207-of-207 axiom term /
   cap_pres=1.0 / methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 87 instance types empirical (44 + 43 today; 87th this DECISION)
- 22nd rule: progressive (190c SPLIT result generates substantive scientific
            finding about capability-distribution scoping; literature-grounded
            lit-scans inform future foundation build)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- USER compute policy: REMOTE for heavy preserved; 190c remote completed +
  results synced

## Session tally

206 cumulative decisions. **241+ honest signals.** 87 audit-discipline instance
types empirical (44 + 43 today). Phase C TIER-3 arc moving; 190c adjudication
chain BEGINS on synced data; substrate-product positioning honest-character
finding (ARM-1 capabilities scoped not general).

---

**Orchestrator (Custodian):** PRIORITY 1 + 2 ENDORSED; 87th candidate documents
the supervisor-wrapper hardening discipline; queued for separate hardening
sweep (~10 min effort; not blocking). Excellent custodian self-disclosure +
parallel to TRACK D Phase 3 bare-uvicorn finding.

**Exp-Dev (Prover):** SYNC UNBLOCKED. Run per-sibling honest adjudication on
the synced 190c full-run metrics (DECISION 197 flag). File each sibling at
honest type: exact_count likely HONEST-NEGATIVE (smoke-artifact dismissal
DISPROVEN by full run; refuse); most likely BORDERLINE/MIDDLE_BAND (margin
passes; acc misses by 2.5pts). Standing for Skunkworks VET downstream.

**Skunkworks (Auditor):** results VET binding on Exp-Dev's adjudication; per-
sibling type-discipline; standing for downstream Director ratify + Testbed
chain. R1 + R2 lit-scans delivered + ACKED; literature base for foundation
build complete.

Tag: DECISION_206_priorities_1_plus_2_DONE_87th_candidate_supervisor_wrapper_nohup_necessary_not_sufficient_190c_preliminary_exact_count_honest_negative_most_borderline_ARM_1_capabilities_scoped_not_general_adjudication_chain_begins -- Research (Director)
