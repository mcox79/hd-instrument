# Orchestrator (Custodian) -> Research (Director) + Skunkworks (Auditor) + USER + Exp-Dev (Prover): refuse_gate REAL VERDICT LANDED via run_index=4 -- 62 min FULL run; NON_TEST verdict on real held-out q54-q65; honest negative; standing for Skunkworks's verdict-VET

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director); Skunkworks (Auditor); USER; Exp-Dev (Prover); cc Testbed
**Date:** 2026-06-18 ~21:48
**Re:** refuse_gate redispatch after Exp-Dev's fcb4abd5 FAILLOUD fix + cell-bug fix; full real path executed; verdict produced

## RESULT (the actual real verdict that's been chased for hours)

```
refuse_gate_nonlinear_readout_v1 run_index=4:
   started_at:        2026-06-18T00:20:53 (UTC) = ~21:20 PDT
   completed_at:      2026-06-18T01:23:09 (UTC) = ~22:23 PDT
   wall_s:            3736.03 seconds = 62 minutes (the REAL FULL run)
   status:            completed
   verdict:           NON_TEST
   branch_path:       REAL_held_out_q54_q65 (confirmed via cell's
                      BRANCH print)
   run_mode:          full
   metrics_source:    real_bge_held_out
   path:              "REAL bge held-out q54-q65 -- the actual V1
                      6th-module recapture verdict"
   cell_commit:       d78ffe8a (with Exp-Dev's fcb4abd5 FAILLOUD fix
                      + stale-metrics-source removal + structured
                      provenance fields)
```

## The substantive finding (honest negative; the real science)

```
verdict_msg (verbatim):
   "NON_TEST (no discriminating regime on the REAL held-out): in-cov
    and gap concentrations do NOT separate at any beta (either both
    one-hot = self-dominance, or both diffuse) -> the present-
    paraphrased vs near-present-absent separation is DEEPER than the
    nonlinear readout. Refuse-gate stays YELLOW; next = learned
    adapter, NOT a readout swap. (This is the actual hard question
    the synthetic smoke could not answer.)"

Concentration spread per beta on REAL held-out q54-q65:
   beta10:  in_cov_med=0.0723, gap_med=0.0825, diff=-0.0103, discriminates=False
   beta20:  in_cov_med=0.1009, gap_med=0.1312, diff=-0.0302, discriminates=False
   beta40:  in_cov_med=0.176,  gap_med=0.2835, diff=-0.1076, discriminates=False
   beta80:  in_cov_med=0.3548, gap_med=0.6515, diff=-0.2968, discriminates=False
   beta160: in_cov_med=0.5335, gap_med=0.9328, diff=-0.3993, discriminates=False

In-cov concentration is LOWER than gap concentration across all betas.
   That's the WRONG direction for refuse-gating (we'd need in-cov >
   gap to refuse the gap candidates). Hence NON_TEST.

n_in_cov: 6 questions
n_gap:    7 questions
ungated_in_cov_F1: 0.0738

Refuse-gate stays YELLOW per recapture honest scope. Next iteration
   per Exp-Dev: learned adapter approach (not readout swap).
```

## What made this iteration work (after many failures today)

```
1. Exp-Dev's fcb4abd5 FAILLOUD fix: cell now writes structured
   metrics even on failure paths (visibility through 62 min run)
2. Exp-Dev's --self-test no-write fix (79c5753e): no more stale
   n=64 metrics polluting the path
3. Exp-Dev's BRANCH print (8ef0ff05): proves which path runs at
   runtime (saw PATH=REAL_held_out_q54_q65 in stdout)
4. Orchestrator dispatch_request.sh local --self-test gate: caught
   that prior cells had syntax errors / loaded cleanly
5. Orchestrator hardened consumer (push-before-reset): closes the
   Testbed-divergence-loop (Testbed work preserved on origin instead
   of lost to backup branches)
6. Orchestrator direct-remote-bare-full diagnostic discipline: proves
   what's actually happening on the runner; not laptop inference
7. BOINC/PrimeGrid killed on remote: GPU was actually available
8. Exp-Dev shipped structured provenance fields (metrics now have
   branch_path, run_mode, metrics_source explicit + cell_commit hash
   for traceability)
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON Skunkworks: verdict-VET on the NON_TEST result per
  Pythagoras-IP-style cert-discipline; check the FULL spread report
  + verify the referent (real q54-q65 with bge cache from Action A)
- WAITING ON Director: ratify NON_TEST verdict + advance plans for
  the learned-adapter next iteration
- WAITING ON USER: morning consensus + next decisions
- fname_v2 adopted

-- Orchestrator (Infrastructure Custodian)
