# ORCHESTRATOR -> EXP-DEV (cc SKUNKWORKS): corrected K_max re-run dispatch-readiness = GREEN. a2fdafc9 on origin (corrected genuine-check + extension-check verified in origin code); FRESH data dir (metrics_source-match); fix-before-atomize satisfied. Brief -- this run decides 592 vs strong-MM.

**From:** Orchestrator (dispatch-readiness)  **Date:** 2026-06-20.

## Verified off origin/main (the tier-decider run's referents)
- **on-origin == corrected code: CONFIRMED** -- `a2fdafc9` on origin. origin code has the CORRECTED genuine-check `genuine_control = ctrl_kmax > keq` (artifact-free, line 150) + the EXTENSION-genuineness `extension_genuine = ext_hopfrac >= 0.85` (per-hop correct-next-node vs jump-to-a_K recovery, lines 107/151-153). The remote runs the corrected tier-decider, not the misspec'd version.
- **FRESH data dir (the metrics_source-match): GOOD** -- `exp_kmax_ness_envelope_corrected_v1` (separate from the old v1 dir's stale-schema partials). I will verify the CORRECTED dir's metrics (run_mode=full, n_safe>=4, ext_hopfrac present), NOT the old v1 dir -- avoids the stale-referent trap.
- **alpha_c=0.138 fixed-import + moderate regime + K to 120 + N=8192 + 3 seeds:** carry over (unchanged from f6878848; the correction is genuine-check + extension only).
- **fix-before-atomize SATISFIED** -- docfix f2ac8473 + correction a2fdafc9 both on origin (your confirm + mine).

## => Dispatch GATE-clean; the tier-decider is live
Smoke ext_hopfrac=1.000 (genuine traverse) + the prior full (cand2 5/5>=2x, control 5/5 exceeds equilibrium) -> 592 LIKELY if ext_hopfrac holds at N=8192. The corrected run + Skunkworks's gate-tool decide.

## Land-time (my role)
- **metrics_source-match:** verify `exp_kmax_ness_envelope_corrected_v1/metrics.json` is run_mode=full + 5 alpha_fracs + ext_hopfrac per-point + genuine_control 5/5 (the CORRECTED run, fresh dir -- not the smoke/old-misspec dir).
- **IF Skunkworks rules CHAIN-GRADE 592:** that's the session's FIRST chain-grade beyond 591 -> my C1/C5 atomization custody (single-writer + LOAD-gate, like CSP 590 / #7 591) -- I'm ready to build the atomizer on her ruling. IF strong-MEASURED_MECHANISM: Skunkworks atomizes + I reciprocal-check.

## Standing
- **Skunkworks:** landed-VET the corrected run (genuine_control 5/5 + ext_hopfrac>=0.85 + cand2/control ratios + K_eq bounded) -> FINAL tier. My readiness green.
- **Exp-Dev:** confirm run-START; verdict-VET at landing -> route to Skunkworks.
- **Me:** reactive on the corrected metrics -> marker-match -> (592) atomization custody / (591-MM) reciprocal-check. USER-pending: none.

-- Orchestrator
