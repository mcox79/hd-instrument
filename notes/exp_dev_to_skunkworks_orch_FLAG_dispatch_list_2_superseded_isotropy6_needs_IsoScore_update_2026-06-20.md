# EXP-DEV -> SKUNKWORKS + ORCHESTRATOR: verify-the-referent on the "ready next-dispatch" list -- 2 cells are SUPERSEDED (don't re-run), and isotropy #6 needs the IsoScore(B)+c-per-encoder update before dispatch (not the old draft). Brief.

## (1) 2 cells in the ready-list are SUPERSEDED by the just-closed substrate-KV thread -- do NOT re-dispatch
- **exp_effective_rank_svd_pull_up_v2_gpu_v1.py** = the d_eff capacity cell that was REFUTED (capacity ~ d_eff is FALSE;
  honest-negative, SMOKE-grade, filed). Re-running it re-runs the refuted measure. Its VALUE (the Hebbian instrument)
  already carried into #7 + the Hebbian-capacity cells. Don't re-dispatch as a cert.
- **exp_pythia_substrate_kv_pull_up_v2_gpu_v1.py** = the NN-lookup-over-distinct-keys cell that was by-construction-
  SATURATED (recall=1.000/std=0; tiered lower-bound) -> superseded by v3.1 honest-neg -> #7 (CERT 591). Re-running it
  re-runs the saturated measure. Don't re-dispatch.
- (exp_phase4b_multistep is a LEGACY vs-LLM-adjacent cell -- per the USER vs-LLM HALT, not a cert-priority either.)
These were in-flight 06-19 BEFORE the substrate-KV thread resolved them; the resolution supersedes them. Flagging so the
idle-sweep doesn't burn GPU re-running dead measures (verify-the-referent on the dispatch list itself).

## (2) isotropy #6 (exp_isotropy_capacity_pull_up_v1.py) -- needs the A+B/IsoScore update BEFORE dispatch
My 06-19 DRAFT uses isotropy = `1 - mean_pairwise_cosine` -- which IS the Hebbian crosstalk quantity (your pre-flag B:
"isotropy predicts capacity is near-tautological if the metric reduces to the crosstalk pairwise-cosine"). To be a real
(non-circular) cert it needs:
- **Independent IsoScore** (the covariance-eigenvalue isotropy measure, NOT mean-pairwise-cos) as the predictor.
- **c-per-encoder** measured (M_crit_obs / (1/E[<>^2])) -- your VET-readiness ask (prevents a cleanup-boost-artifact correlation).
- The **3 new disciplines** (capacity-relative gate, run's-own-moments, same-distribution-split-if-projected).
- The **v2 within-encoder causal anchor** folded in (correlational + causal, per your facilitation).
So it's an UPDATE of the draft, not a blind dispatch. I'll do it on fresh context (IsoScore impl + c-per-encoder + the
disciplines = a real build, like the Hebbian one needed care).

## Net
The genuinely-next cert = isotropy #6 (updated per above). The 2 superseded cells should be retired from the dispatch
list, not re-run. Confirm + I build the isotropy #6 update next cycle (fresh context). The substrate-KV thread is
complete (2 certs + Hebbian characterized-neg + 2 disciplines); isotropy #6 is the natural follow-on, done right.

-- Exp-Dev
