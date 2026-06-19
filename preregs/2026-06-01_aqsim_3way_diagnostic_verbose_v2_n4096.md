# Pre-registration: aqsim_3way_diagnostic_verbose_v2_n4096

**Filed**: 2026-06-01 by exp_dev
**Anchor name**: aqsim_3way_diagnostic_verbose_v2_n4096
**Queue**: remote_cpu_queue
**Script**: experiments/exp_aqsim_3way_diagnostic_verbose_v2_n4096.py

## Context

Replaces v1 (aqsim_3way_cross_n_engineering_diagnostic_v1_n4096) which failed remotely
with status=failed, no wall_s, started_at=2026-06-01T14:38:44. Root cause of v1 remote
failure: metrics.json written to data/<NAME>/ (missing exp_ prefix) while runner
expects data/exp_<NAME>/metrics.json. V2 fixes this plus adds verbose tracing.

V1 local run (data/aqsim_3way_diagnostic_v1/metrics.json) already produced
DIAGNOSTIC_HARD_PASS identifying 2 root causes for AQSIM 3-way cross-N failure:
(1) Checkpoint contamination: smoke partials loaded by FULL run (PROT-021 fix exists)
(2) Kerdock even-log2 constraint: N=8192 (log2=13 odd) raises ValueError

V2 ships with these fixes baked in and verbose sentinel logging per
[[feedback-always-verbose-remote-dispatch]].

## Scientific question

Engineering diagnostic: confirm on remote runner that 2 root causes from v1 local run
reproduce correctly, with full verbose tracing to experiment.log so failure can be
diagnosed even if metrics.json write fails.

## Design

4 scenarios, CPU-only, 1 seed each:
- Scenario 1: N=4096 control (PASS expected)
- Scenario 2: checkpoint contamination simulation
- Scenario 3: N=8192 build_shared (Kerdock ValueError expected)
- Scenario 4: N=16384 K=2 (PASS expected; confirms fix path)

Verbose tracing: every scenario wrapped in _log_sentinel before/after;
full traceback on any exception; experiment.log written independently of metrics.json.

## Pre-registered threshold bands

**HARD-PASS**: verdict = DIAGNOSTIC_HARD_PASS
  Criteria: (a) N=4096 control PASS + (b) contamination_confirmed=True +
  (c) N=8192 kerdock_exception=True + (d) fix_path non-null
  Expected from v1 local data: all 4 criteria met.

**HARD-FAIL**: verdict = DIAGNOSTIC_HARD_FAIL
  Criteria: root_cause=None AND fix_path=None after all 4 scenarios
  Treatment: escalate to live debugging session; ENGAGEMENT-LOCK remains

**MIDDLE-BAND**: verdict = DIAGNOSTIC_MIDDLE_BAND
  Criteria: root cause identified but fix not actionable in single dispatch
  Treatment: route fix path to strategy; ENGAGEMENT-LOCK partial release pending fix

## Timeout estimate

smoke_wall_s = ~25s (v1 local, 4 scenarios)
Remote: ~60s maximum (CPU, same 4 scenarios)
timeout_s = ceil(1.5 * 60 * 1.0 * 1) = 90s -> PROT-019 floor 14400s
**timeout_s = 14400** (PROT-019 minimum for N>=4096)

scaling_exp = 1.0 (no matrix ops dominate; each scenario is a diagnostic probe)

## N-suffix section

N-suffix: _n4096 binds N_CONTROL = 4096.
Diagnostic also probes N=8192 and N=16384 but these are secondary probes;
production N = 4096 (control).

## PROT compliance

- PROT-018: N_CONTROL = 4096 matches _n4096 suffix
- PROT-019: timeout_s = 14400 (PROT-019 floor for N>=4096)
- PROT-021: checkpoint keys include mode suffix (selftest verifies)
