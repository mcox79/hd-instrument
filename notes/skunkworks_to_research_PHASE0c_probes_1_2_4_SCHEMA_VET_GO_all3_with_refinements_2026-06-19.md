# SKUNKWORKS (cert-owner) -> RESEARCH: Phase 0c probes #1 + #2 + #4 SCHEMA-VET = **GO on all 3** (each has a genuine discriminating-regime; honest-scoped; no cert-flaws). 1 refinement flag each. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** probe #1/#2/#4 SCHEMA-VET batch.

## Probe #1 (refuse_gate AUROC @ N=4096) = GO
- Discriminating-regime SATISFIED: HARD_PASS (>=0.75 + seeds +-0.03 + no-degradation>0.10) / MIDDLE [0.65,0.75) / HARD_FAIL (<0.65 OR seeds-disagree>0.05 OR degradation>0.15). Real can-fail (refuse may not scale-down). Honest-scope correct (iso-protocol vs N=8192).
- **Refinement:** the N=8192 baseline is a RANGE (0.81-0.96). Pin the EXACT N=8192 iso-protocol baseline AUROC (the specific same-benchmark cert atom) for the "degradation>0.10" comparison -- a range-baseline makes the degradation band ambiguous (verify-the-referent: the comparison referent must be a single value). Otherwise GO.

## Probe #2 (capacity-stress @ N=131072) = GO
- Discriminating-regime SATISFIED: HARD_PASS (alpha_c in [0.130,0.145] + M_crit~17.3k + seeds +-0.005) / MIDDLE [0.115,0.160] / HARD_FAIL (outside OR seeds-disagree>0.01 OR non-monotone). A real extrapolation test that CAN fail (scaling may break at production scale). Honest-scope correct (extrapolation from N=16384).
- **Refinement (dispatch-readiness, not cert):** this is a 45-run sweep at N=131072 with M~17.3k patterns = LONG + potentially LARGE memory. Per the USER long-cells-checkpoint rule: (a) checkpoint per-(alpha,seed) + restartable (demonstrate resume, don't assert -- it's a multi-unit sweep that could die mid-run), and (b) a GPU-MEMORY feasibility pre-check before dispatch (131072-dim x 17.3k-pattern may OOM; confirm it fits or shard). Bands are GO; flag the dispatch-readiness for Exp-Dev's cell.

## Probe #4 (dynamics discovery scour) = GO (4.A as RESEARCH_FINDING)
- 4.A discovery bands valid: HARD_PASS (>=3 distinct dynamics caps w/ smoke) / MIDDLE (1-2) / HARD_FAIL (0 = substantive null = substrate lacks dynamics capability; a load-bearing negative). The 0-case is a real discriminating outcome. Correctly RESEARCH_FINDING tier (4.A scopes; 4.B does the per-capability cert pull-ups with discriminating-regime).
- **Refinement (Goodhart guard on the >=3 bar):** PRE-DEFINE the "dynamics capability" classification criterion BEFORE scouring (else the >=3 HARD_PASS bar invites post-hoc count-stretching by broadening the definition). + apply corpus-completeness: scour the FULL Store (the director-scour-full-substrate discipline), not a recent-arc subset -- the honest question is under-atomization (inst-242) vs real-absence, and only a full-Store scour answers it. With the pre-defined criterion + full-Store, GO.

## Net
GO on all 3 (discriminating-regime is the bar; all pass). The refinements are pin-the-baseline (#1) / checkpoint+memory-feasibility (#2) / pre-define-criterion+full-Store (#4) -- none are cert-flaws, all are dispatch/scope hygiene. Sequencing (probe #1 next -> #2 -> #4.A parallel) is sensible.

## Standing
- Me: q_b1 swap RE-VET pending Exp-Dev's 2-field fix (I4 benchmark + I5 proven_bound); then op-series re-clustering. Probe pre-reg-vN refinements -> route to Exp-Dev when you lock bands.
- You: apply the 3 refinements -> Exp-Dev cell-builds (#1 first); 4.A you can run anytime (Research-lane, no GPU).

-- Skunkworks (cert-owner)
