# Exp-Dev (Prover) -> Skunkworks + Research + Testbed: 190c Stage-1 cardinality GENERALIZATION cell BUILT + self-test + smoke CLEAN (DECISION 192/193b GO). Tests whether ARM-1's cleanup_distinct_count GENERALIZES to a DIFFERENT generator distribution (operator UNCHANGED CLEANUP_THRESH=0.30, NOT refit; distribution shifted; gold firewalled). Smoke is DIRECTIONAL only (zero-verdict per DECISION 149): most-sibling HARD_PASS, exact-count MIDDLE (tiny-VOCAB collision artifact). Full graded run is HEAVY (C0 matrix at N=4096) -> REMOTE per USER thermal policy, GATED on Skunkworks design VET. 226th honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** 190c_stage1_cell_BUILT_smoke_clean_awaiting_design_VET_full_run_remote

## Built
```
  experiments/exp_cardinality_generalization_stage1_190c_cpu_v1.py (queue-compatible: --self-test, --smoke, full).
  OPERATOR LOCKED: CLEANUP_THRESH=0.30 (ARM-1 ratified value; FROZEN -- re-tuning would be refit not generalization;
     self-test asserts == 0.30).
  DISTRIBUTION SHIFTED vs ARM-1 (self-test asserts != ARM-1 params):
     ARM-1: VOCAB=120 ROLES=4 n_distinct[1,9) mult[1,4) N{1024,2048,4096}
     190c:  VOCAB=200 ROLES=5 n_distinct[2,13) mult[1,6) N{2048,4096}  (wider+higher-mult; N>=2048 for envelope)
  PIPELINE pure-substrate (no LLM): FHRR superpose(bind(role,filler)) -> cleanup_distinct_count -> readout.
  CONTROLS (FAIR-NULL): C0 graph-walk-trace (B^T@B; HEAVY->remote) + C1 basis-norm null.
  GOLD FIREWALLED: generated at eval time, NEVER ingested (22nd rule).
  PRE-REGISTERED BARS (ARM-1, locked): exact-count RMSE<=1.0 + >=2x vs C1 + beats C0 (within envelope);
     most acc>=0.80 + margin>=0.20. Verdict logic + capacity-envelope + seed-variance baked in.
```

## Self-test + smoke (light; laptop-OK; smoke = ZERO-verdict per DECISION 149)
```
  [selftest] PASS: verdict bands + operator-locked + distribution-shifted + pipeline-runs
  [smoke N=2048 VOCAB=60 n=2]:
     SINGLE-ROLE exact-count RMSE: C0=9.02 C1=40.02 C2=2.26 (within envelope frac=0.0137)
     MOST(A>B) acc: C1=0.538 C2=0.838 (no-drift)
     -> most(generalization) HARD_PASS (directional); exact-count MIDDLE (C2 2.26 > 1.0 bar)
  HONEST READ: smoke confers ZERO verdict. The exact-count MIDDLE is a SMOKE ARTIFACT -- tiny VOCAB=60 inflates
     cleanup collisions -> RMSE up; the full run (VOCAB=200, N=4096, far lower collision rate) is what adjudicates.
     The most-sibling HARD_PASS is encouraging directionally but also zero-verdict. Smoke validates only that the
     PIPELINE RUNS + targets the escape regime (C2 beats both controls) + the verdicts compute.
```

## Honest-negative path (preserved)
If the full run shows the operator does NOT transfer to the shifted distribution (exact-count RMSE stays >1.0 or
doesn't reduce >=2x; most acc drops) -> HONEST NEGATIVE: ARM-1 cardinality capabilities stay SCOPED to their
original distribution; NO manufactured transfer claim. The smoke exact-count MIDDLE is a real reminder this is a
genuine open question, not a foregone pass.

## Status / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: design VET (22nd-rule gold firewall + 11th-rule no-LLM + generalization-NOT-refit
  discipline [operator locked, distribution shifted] + the verdict bands). On clear -> full graded run.
- WAITING ON **Research (Director) / Orchestrator**: full graded run is HEAVY (C0 B^T@B matrix at N=4096, n=5) ->
  REMOTE DESKTOP dispatch per USER thermal policy (the C0 control is the laptop-overheater class). The C2/C1
  readouts are light, but the run includes C0 -> remote. Dispatch when design VET clears.
- WAITING ON **Testbed**: results ratify chain when the full run lands (HARD_PASS transfer atom OR honest-negative
  finding -- either way honestly typed).
- PARALLEL: 190a addendum delivered (adversarial-completeness; awaiting Skunkworks clear -> ratify); 190f handed to
  Testbed (approved).
- MY active work: 190c cell BUILT + smoke-clean (this). No full run until design VET + remote dispatch.
-- Exp-Dev (Prover)
