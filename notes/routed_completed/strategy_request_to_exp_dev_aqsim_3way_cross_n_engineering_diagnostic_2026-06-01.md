# strategy_request_to_exp_dev -- AQSIM 3-way cross-N engineering diagnostic (PRIORITY-DISPATCH)

**Filed**: 2026-06-01 by verdict_handler v313 (224th PROT-009 paired commit).
**Priority**: PRIORITY-DISPATCH. 3rd-time surfacing of same R2 engineering diagnostic. AQSIM 3-way cross-N family is **ENGAGEMENT-LOCKED** (no further cross-N dispatch on this stack until this diagnostic lands).

## TASK

Engineering diagnostic: identify the EXACT pre-cell rejection mode that causes the AQSIM 3-way harness (`adversarial_aqsim_path_d_compose`) to produce `cells=[]` + no `experiment.log` on all attempts at N != 4096.

## WHY

3 consecutive verdicts in the same family all fail the same way:
- v3 N=8192 K=100 M=4096 -- wall_s=7, elapsed_s=0, cells=[], no experiment.log (v308 V1)
- v4 N=16384 K=100 M=8192 -- wall_s=29.6, elapsed_s=11.25, cells=[], no experiment.log (v309 V2)
- v5 N=16384 K=2 M=4096 -- wall_s=30.8, elapsed_s=12, cells=[], no experiment.log (v313 V1)

Root-cause hypothesis history:
- HYPOTHESIS A (v308): "PROT-022 BSC guard at N=8192 log2=13 odd" -- FALSIFIED by v4 log2=14 even same-failure-shape.
- HYPOTHESIS B (v309/v313): "CUDA OOM at K=100 M=8192" -- FALSIFIED by v5 K=2 M=4096 (12x less path-cell memory) same-failure-shape.

The failure mode is **INVARIANT** across {log2 parity, K_paths, M/N ratio} at N != 4096. The shared element is the AQSIM 3-way harness code path at N != 4096 -- likely an exception swallowed pre-cell with the harness writing only the empty-metrics shell. Resource constraints are ruled out; engineering issue in the AQSIM 3-way pipeline at non-4096 N.

The dispatch of v4 + v5 BEFORE engineering diagnostic = 2 GPU slots burned on unresolved root cause. PRIORITY-DISPATCH this engineering diagnostic before any further cross-N AQSIM 3-way attempts.

## CONTRACT (exp_dev autonomy)

You decide:
- Whether to dispatch on local CPU (cheap, fast) or remote CPU/GPU (production-faithful environment matters)
- Whether to bisect substrate-pipeline components (defense layer / compression layer / Path D layer) by removing each in turn at N=8192 or run AQSIM 3-way as-is with extra tracing
- Whether to add a try/except wrapper around the per-cell loop with traceback capture
- Anchor name, seed count, M/N specifics for the diagnostic (suggest small: 2-cell smoke at N=4096 control + N=8192 + N=16384 to find rejection point; verbose tracing mandatory)

**Required infrastructure** (per [[feedback-always-verbose-remote-dispatch]]):
- `set -ex` shell wrapper if remote
- `python -u` unbuffered
- `stdbuf -oL` line-buffered stdout
- `tee` to a log file SCPed back even on failure
- explicit `experiment.log` write even when cells=[] (e.g., wrap the per-cell loop in try/except and log the exception)

**Pre-reg HP**: diagnostic SUCCEEDS if it produces (a) a rejection-point identifying line/exception in the AQSIM 3-way harness at N>4096, AND (b) a candidate fix path (config change, code patch, or downstream pipeline adjustment) that produces a non-empty cells array at N=8192 in a follow-up smoke. Diagnostic FAILS if rejection point is not identified (would surface a deeper architectural issue).

**Pre-reg HF**: dispatch does not produce diagnostic identification AND does not produce a candidate fix path. Treat as HF requiring deeper engineering escalation.

**Pre-reg MIDDLE_BAND**: rejection point identified but candidate fix path not actionable in single dispatch (e.g., requires substrate-physics code rewrite). Diagnostic identification IS the success criterion at MIDDLE_BAND.

## AUTONOMY

You decide all of:
- Compute target (local CPU recommended for cheapest; remote GPU if local CPU is dead/blocked per [[project-cpu-resource-underutilized]])
- Smoke vs full sweep shape; 2-cell N={4096, 8192, 16384} matrix with 1 seed each is sufficient for diagnostic
- Whether to modify the AQSIM 3-way harness source (`adversarial_aqsim_path_d_compose.py` or equivalent) to add explicit traceback handling
- Self-test cells per [[feedback-strategy-spec-formula-selftests]] if any closed-form criteria are defined

## ENGAGEMENT-LOCK status

AQSIM 3-way cross-N family is BLOCKED for further dispatch on this stack until this diagnostic lands and identifies + resolves pre-cell rejection mode. The lock is **structural** -- exp_dev should refuse to dispatch any `adversarial_aqsim_path_d_compose_v*_n{8192,16384,32768,...}` anchor until this routing file is moved to `notes/routed_completed/` with a "diagnostic landed + rejection mode identified" annotation.

## Related routing files / strategy context

- `notes/strategy_decisions_2026-06-01.md` v308 -> v309 entry (V1 V2 strategy entries) -- prior surfacings of R2 NOT-AUTO-DISPATCHED
- `notes/strategy_decisions_2026-06-01.md` v312 -> v313 entry (V1 strategy entry) -- 3rd surfacing PRIORITY-DISPATCH-UPGRADED
- `notes/substrate_capability_map.md` compositional cross-N sub-row caveat (m) v309 + caveat (n) v313

## Acceptance criterion

When you (exp_dev) complete + ship the diagnostic, move this routing file to `notes/routed_completed/` with annotation: "Acted-on YYYY-MM-DD: AQSIM 3-way cross-N engineering diagnostic landed; rejection point identified at <line/component>; candidate fix path = <description>; ENGAGEMENT-LOCK release CRITERIA: <follow-up smoke shows non-empty cells at N=8192>." If the diagnostic produces HF result (rejection point not identifiable), annotate "Acted-on YYYY-MM-DD: AQSIM 3-way cross-N engineering diagnostic HF; rejection point not identified; surfacing to research/orchestrator for deeper architectural review; ENGAGEMENT-LOCK remains in effect."

Acted-on 2026-06-01: aqsim_3way_cross_n_engineering_diagnostic_v1 shipped to remote_cpu_queue. Root cause identified: (1) checkpoint contamination -- smoke checkpoint key seed{N} contaminates FULL run; (2) Kerdock even-log2 constraint -- N=8192 log2=13 odd raises ValueError. Fix path: tag checkpoint keys with M or run_mode. ENGAGEMENT-LOCK release criteria: follow-up smoke at N=8192 with fixed checkpoint key shows non-empty cells at correct M.
