# SESSION STATE / HANDOFF (solver, pre-compaction 2026-08-28)

Read this + `SOLVED.md` + `DESIGN_brain_analysis.md` to resume. The RESULTS are already in SOLVED.md;
this note captures the OPERATIONAL in-flight state that compaction could otherwise lose.

## Where the solve is
- `SOLVED.md` = the deliverable, status **PARTIAL**, ledger-valid, witness `verification/verify_structured_context_learner.py` PASS. WIP until `owner_verdict: DONE` in OWNER_NOTES.md.
- BAR #1-#5 answered. Fidelity phases 1-2 folded in. Fidelity PHASE 3 (4 remote drills) folded in.
- A **brief submission prompt** was already shared with the owner in chat (copyable summary).

## The 4 remote architecture drills -- DONE, results pulled locally, folded into SOLVED:
- `exp_semantic_control_routing_v1` -> **HARD_PASS** (dynamic IFG control beats fixed blend, shuffled loses; pooled 0.274 vs 0.262; win on relatedness routing).
- `exp_grounding_supply_v1` -> **HARD_PASS** (richer grounding beats text on MEN +0.1275 CI-sep, crossover holds; Binder-65 alone 0.633 on MEN).
- `exp_exemplar_selpref_v1` -> MIDDLE_BAND (beats shuffle +0.013, loses to word-identity even on rare 0.056 vs 0.176 -> low-data-regime advantage, NOT a 15M wall).
- `exp_dependency_path_context_v1` -> MIDDLE_BAND (paths beat their shuffle but not the immediate context -> saturation, NOT a wall).

## IN FLIGHT (resume here): the 5th drill -- broad brain-based grounding
- Agent `hdi_exp_dev` (id a...adf2cace...) is BUILDING `experiments/exp_binder_attr_prediction_grounding_v1.py` (ridge predictor of Binder-65 attrs over full vocab from Lancaster+Brysbaert+DEP-embedding; 7 arms; MEN/SimLex/WordSim; predictor-validity + shuffled-target twin). As of writing the cell file is NOT yet written.
- WHEN IT REPORTS GREEN (self-test+smoke exit 0, remote-safe): (1) drop `REMOTE_RUN_REQUEST_exp_binder_attr_prediction_grounding_v1.md` in this folder (front-matter per the other 4 request files here + the canonical brief); (2) the 5-min watcher auto-dispatches it to remote_cpu_queue; (3) pull the result and fold into SOLVED.

## HOW REMOTE RUNS WORK (self-service; see memory `reference_solver_remote_run_request_protocol` + `notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`)
- Solver drops `notes/problems/<slug>/REMOTE_RUN_REQUEST_<cell>.md`; watcher `hd_remote_run_watcher` (5-min) validates + writes prereg + ships code+data + queues. Edit the request (1 char) to RE-FIRE.
- Cell must: NO spaCy on any run-time path; load pre-parsed cache (never parse); `# KB_REFERENT:` every dep; `smoke = bool(args.smoke) or args.mode == "smoke"` (BARE == FULL); write metrics.json INCREMENTALLY per-arm (partial:true) -- match `exp_exemplar_selpref_v1.py`.
- **INFRA GOTCHAS (flag to owner, not solver-fixable): (a) `hd_metrics_sync` scheduled task is DISABLED** -> results do NOT auto-return; re-enable `schtasks /change /tn hd_metrics_sync /enable`, else pull manually via the orchestrator (`scp_recover_landing.py --verify-after <cell>`). **(b) SH-4 double-prefix:** remote writes metrics to `C:/dev/hd-instrument/data/exp_exp_<name>/metrics.json` (double `exp_`), pull to local `data/exp_<name>/metrics.json`. Both mean a solver run needs an orchestrator pull until fixed.

## NEXT STEPS TO COMPLETE THE SUBMISSION
1. Land the Binder follow-on (build->smoke->request->dispatch->pull->fold into SOLVED as the phase-3 grounding scale-up).
2. Confirm `python tools/problem_ledger.py --check` still passes (malformed/incomplete: 0) after edits.
3. Submission is COMPLETE for owner review; do NOT integrate (strategy lands hdlab on owner_verdict: DONE).
4. Optional next-tier (only if owner wants): downstream comprehension with the fully-optimized routed+grounded read-out (the "does-it-matter" payoff); semantic-control gold-blind CONFLICT-gate deepening.

## DISCIPLINE REMINDERS
- Owner: drill brain-can-we-can't walls aggressively; do NOT excuse-label a wall as "bounded"/"artifact" (memory `feedback_do_not_deprioritize_brain_can_we_cannot_walls...`). Distinguish genuine gap vs correct-dissociation/supply-limit/saturation with a SPECIFIC reason.
- Heavy runs -> remote via REMOTE_RUN_REQUEST; lightweight self-tests inline. Never bundle rm/delete with work (auto-denied). If a tool call is denied, STOP + report verbatim.
