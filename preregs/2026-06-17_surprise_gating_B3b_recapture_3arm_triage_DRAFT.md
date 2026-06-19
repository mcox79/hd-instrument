# PREREG (DRAFT): Surprise-gating B3b RECAPTURE -- 3-arm named-failure-mode triage (collapse / mis-cal / noisy-TV)

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT (R4 Track-F; Day-2) -- pending Skunkworks SCHEMA-VET + Director STEP-2 LOCK before cell-author.
**Drill source:** notes/research_surprise_gating_B3b_recapture_3x_2026-06-17.md (22-unique-citation 3-angle lit-scan + Opus synthesis).
**Recaptures:** scorecard claim 8b (surprise-driven gating B3b) -- STEP-4 disposition = MIDDLE/HF (partial; not a load-bearing gating primitive).
**Part of:** Director R4 Tier-2 ECONOMICS BATCH (8a + 8b + 18; this prereg = the 8b component; efficiency-composition 18 = sibling prereg).

## Honest-recapture framing (load-bearing; HONEST-NEGATIVE acceptable)
The drill BET: the B3b MIDDLE/HF ceiling is ONE OF THREE named MoE/curiosity failure modes (each with a named, cheap
lift), NOT a fundamental surprise-gating ceiling. This is NOT a re-run -- it is named-failure-mode TRIAGE (diagnose which
mode, apply the matched lift), genuinely different from "search for a new gating mechanism." HARD-FAIL on all 3 is an
ACCEPTABLE outcome (verdict -> structural-closure / HONEST_BOUNDED): "B3b is hitting a substrate-novel ceiling not
addressed by the public MoE/curiosity literature" -- a real finding (downgrade to "explored, structural ceiling";
rescue-dispatch to modern-Hopfield surprise-energy). P_deflated=0.45 (one named lift applies; uncharted HD-substrate regime).

## Design (3-arm diagnostic + matched lift; reuse existing B3b cell)
```
BASE TASK (R1 RESOLVED -- data-independence confirmed; OPTION A chosen): the original anchor
   exp_surprise_gated_pool_charlm.py IS charLM-DEPENDENT (Titans surprise-gate scored by BPC on a char-LM byte-
   prediction task, baseline 2.4994) -> charLM is DATA-PAUSED (USER; Tier-6) -> a "lift failed" there could be a DATA
   artifact, NOT a gating-mechanism artifact (the confound Skunkworks flagged). RESOLUTION (Director-recommended A):
   re-scope the MECHANISM recapture to a DATA-SUFFICIENT SYNTHETIC memory-pool gating task where data is NOT the binding
   constraint -- a pool fed a controllable Zipf/power-law item-frequency stream (the real "frequent items flood the pool,
   crowd out rare/informative" problem, generated to any size), metric = pool-retrieval top-1 quality under write-all vs
   surprise-gated writes. The Titans surprise-gate + the 3 named-failure-mode arms are MECHANISM-level (router-collapse/
   ECE/noisy-TV) and run identically on the synthetic pool. This tests the GATING-MECHANISM recapture cleanly; the
   charLM-pool (BPC) instantiation DEFERS to Tier-6-resume (when language packs are ingested) -- so the verdict cannot be
   confounded by char-LM data scarcity. (If Director prefers OPTION C, add the charLM-data-limited regime as a reported
   CONTROL alongside; but A is the clean primary.)
ARM 1 (router/specialization COLLAPSE): diagnostic = router-logit norm + per-expert token-share entropy over last 100
   batches. COLLAPSE iff max-share > 0.40 OR token-share entropy < 0.7*uniform. LIFT = L2-normalize hidden + low-dim
   projection before routing (Chi 2022 XMoE) + router z-loss (Zoph 2022, coef 1e-3).
ARM 2 (raw-softmax MIS-CALIBRATION): diagnostic = ECE of the surprise-gate score (quantile-binned) vs gating-relevant
   outcome on held-out. MIS-CAL iff ECE > 0.05. LIFT = temperature-scale the gate (1-param fit on val; NO retrain).
ARM 3 (NOISY-TV trap): diagnostic = inject 5% irreducible-noise samples; measure gate-firing on noise vs signal.
   NOISY-TV iff gate fires on noise at >= signal rate. LIFT = swap surprise estimator forward-error(ICM) -> frozen-target
   distillation (RND, Burda 2018b; converges to 0 on aleatoric states).
SEEDS: >=5 (drill specifies n>=5, p<0.05). COMPUTE: diagnostics = laptop-cheap (norms/ECE/noise-firing, no retrain);
   ARM-2 lift = no-retrain (laptop); ARM-1/ARM-3 lifts = retrain -> REMOTE (R4 Day-2 batch). Smoke laptop.
```

## Pre-registered bands (from drill (c); per-arm; n>=5, p<0.05)
```
ARM 1 LIFT (L2 + z-loss + low-dim route):  HARD-PASS = >= +6 pp on B3b metric vs MIDDLE baseline (expected +8..+15).
ARM 2 LIFT (temperature scaling):          HARD-PASS = >= +4 pp (expected +3..+8; cheapest, no retrain).
ARM 3 LIFT (forward-error -> RND):         HARD-PASS = >= +5 pp (expected +5..+12 if NOISY-TV dominant).
R2 BASELINE-DISCRIMINATING-RANGE (Skunkworks-required; before scoring any +Npp LIFT): CONFIRM the write-all baseline
   pool-retrieval metric is measurably BETWEEN floor (chance) and ceiling (saturation) -- NOT already ~0 (nothing to
   lift) and NOT already near-perfect (no headroom). If the baseline is degenerate (floor/ceiling), the +Npp lift is
   undetectable -> that config is a NON-TEST (report it; re-pick the pool load so the baseline is discriminating). This
   makes the LIFT measurement meaningful. (The all-3-fail -> HONEST_BOUNDED structural-closure verdict already has its
   discriminating guard via the diagnostics: max-share<0.30 + ECE<0.03 + noise-firing<0.5x.)
VERDICT MAP:
   any arm HARD-PASS -> PASS (B3b cap_map VALIDATED; surprise-gating becomes load-bearing conditional-compute primitive;
      the winning mode+lift is the recaptured mechanism; cert-grade at >=5 seeds; method-contingent).
   ALL THREE arms stacked LIFT < +3 pp (AND diagnostics show no-collapse max-share<0.30 + ECE<0.03 + noise-firing<0.5x
      signal) -> HONEST_BOUNDED / structural-closure: not one of the 3 named modes; rescue-dispatch to modern-Hopfield
      surprise-energy (Krotov-Hopfield non-residual surprise prior) per the drill's next-candidate.
   mixed/between -> MIDDLE_BAND (report which mode partially lifts; inform the rescue decision).
```

## Provenance (recapture_of populated per Skunkworks ruling B)
- recapture_of = scorecard_claim_8b_surprise_gating_B3b (MIDDLE/HF)
- failing_config_avoided = raw surprise-gate (hard top-k routing + raw-softmax score + forward-error surprise) hitting an
  unnamed one of {router-collapse, mis-calibration, noisy-TV} -> MIDDLE/HF ceiling read as a partial gating result
- method_delta = named-failure-mode TRIAGE: diagnose the SPECIFIC mode (3 cheap diagnostics) then apply the MATCHED
  literature lift (L2+z-loss / temp-scale / RND), NOT a re-run and NOT a blind new-mechanism search
- FULL >=5 seeds -> CERT_CHAIN_GRADE. method-contingent (3-named-lift + config axes; softer-gate/non-residual UNTESTED).

## Cert-chain next steps
1. Skunkworks SCHEMA-VET: confirm B3b base cell (+ charLM-pause independence); method-genuinely-different (triage not
   re-run); falsifiable per-arm bands; metric-matches-semantic (gating metric, not a proxy); >=5-seed criteria.
2. Director STEP-2 LOCK.
3. Exp-Dev cell-author (3-arm diagnostic+lift harness) + witness + smoke (laptop) -> diagnostics (laptop) + lifts
   (ARM-2 laptop, ARM-1/3 REMOTE Day-2) -> verdict -> re-atomize.

## Batch note
2 of 3 in the Director Tier-2 economics batch. Siblings: efficiency-composition (18) prereg DRAFTED
(2026-06-17_efficiency_composition_recapture_3arm_bakeoff_DRAFT). 8a active-gating = next (drills:
research_drill_multiplicative_gating_vs_additive_2x + storage-efficiency). B8 SKIPPED (Director: memory-recon, not frontier).
"Good-enough efficiency" honest bar for the batch (gates overlap -> sub-multiplicative expected per Director/Skunkworks).

-- Exp-Dev (Prover) [DRAFT]
