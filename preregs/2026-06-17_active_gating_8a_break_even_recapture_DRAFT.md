# PREREG (DRAFT): Active-gating 8a RECAPTURE -- break-even regime-boundary map (primary) + Bayesian-surprise gate (secondary)

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Status:** DRAFT (R4 Track-F; Day-N REMOTE) -- pending Skunkworks SCHEMA-VET (incl. ANCHOR-MECHANISM-MATCH check) + Director STEP-2 LOCK.
**Drill source:** notes/research_active_gating_perf_cost_2026-06-17.md (5-family map; 14+ arXiv cites; Candidate B primary + Candidate A secondary; SAFE evidence-verified).
**Recaptures:** scorecard claim 8a (active-gating 13.8x) -- STEP-4 disposition = FLAGSHIP -> PARTIAL (ceiling_followup HARD_FAIL @perf 0.83: the 13.8x speedup did NOT hold at the performance ceiling).

## ANCHOR-MECHANISM-MATCH (the new check from the 18 catch -- VERIFIED before drafting)
The 18 mistake (recapture operators undefined for the anchor cell) is avoided here by verifying the anchor first:
- ANCHOR = active-gating perf-COST: claim-8a = the B3a top-k-error gate's 13.8x write-reduction (same b3axb3b family),
  downgraded because the ceiling-followup HARD_FAILed at perf 0.83 -- i.e. the speedup is REGIME-DEPENDENT and fails at
  the performance ceiling. The anchor's ACTUAL limiter = "active-gating's net-benefit is not characterized; it breaks at
  a perf/load boundary."
- RECAPTURE Candidate B = break-even regime-boundary characterization (when does router+dispatch+memory cost EXCEED the
  FLOP/write savings, and where does the perf bar fail?). This DIRECTLY targets the anchor's actual limiter (the unmapped
  perf-cost boundary that caused the ceiling-fail). MECHANISM MATCHES (perf-cost gating <-> perf-cost gating). CONFIRMED.
- (Contrast 18: there the bake-off was binding-capacity operators on a gating cell = mismatch. Here Candidate B is a
  perf-cost characterization of the SAME active-gating mechanism the anchor measures. Match holds.)

## Honest-recapture framing (load-bearing; measured-bounds rule)
The 8a downgrade is the measured-bounds lesson made concrete: a SINGLE-POINT "13.8x active-gating speedup" claim is
method/config-contingent and failed at the perf ceiling. The recapture does NOT re-assert a fixed 13.8x -- it HONESTLY
MAPS the break-even regime boundary (the envelope where active-gating is a net win vs net loss, and where the 13.8x holds
without failing the perf bar). HARD-PASS = a clean deterministic boundary exists (recaptures the claim AS A BOUNDED,
regime-mapped result = "exact/combinatorial cert-grade territory" per the drill); HARD-FAIL = no boundary (active-gating
net-benefit is flat/absent = the claim does not even hold as a bounded result). HONEST-NEGATIVE acceptable.

## Design (Candidate B primary = break-even map; Candidate A secondary = mechanism arm)
```
PRIMARY (Candidate B -- break-even regime boundary; deterministic map):
   BASE: the active-gating mechanism of the b3axb3b family (B3a top-k-error gate over the cf-RPE char-LM pool) OR a clean
      MoE-top-k surrogate (Exp-Dev picks the cleanest instrumentable harness; same active-gating mechanism).
   SWEEP a grid over: load (batch B in {tiny..large}) x sequence/corpus scale (L) x sparsity (gate-frac k/N) x
      perf-target (the bar that failed at 0.83).
   MEASURE per grid point: TOTAL cost = gate/router + dispatch + memory-load (NOT just FLOPs -- the memory-FLOPs
      decoupling tax is the drill's verified failure axis) vs the dense baseline -> NET speedup ratio; AND the achieved
      perf at that point. The break-even boundary = where NET speedup crosses 1.0 (net-win -> net-loss) AND/OR where
      perf drops below the bar.
   METRIC: the (B, L, k/N) -> {net_speedup, perf} surface; the boundary frontier.

SECONDARY (Candidate A -- Bayesian-surprise per-token compute gate; SDT-style arXiv:2511.21408):
   swap the top-k-error gate for an epistemic-Bayesian-surprise gate; test compute-reduction at iso-quality vs a
   softmax-entropy (BranchyNet) baseline + a noisy-TV stochastic-input ablation. Mechanism-explore arm (bridges 8a<->8b).

SEEDS: >=3 (>=5 for the secondary stochastic arm). COMPUTE: the regime SWEEP is instrumentation-heavy (many grid points x
   model runs) -> REMOTE (R4 Day-N; not laptop). Smoke = tiny grid on laptop to verify the boundary-detection + the
   degenerate-regime guard work.
```

## Pre-registered bands (from drill (B)/(A))
```
PRIMARY (Candidate B):
   HARD-PASS: a SHARP MONOTONE break-even boundary is found -- exists B* and/or L* below which active-gating is net-LOSS
      (net_speedup < 1.0) OR the perf bar fails; report the (batch, seq-len, sparsity) net-win frontier. (Recaptures 8a as
      a bounded, honest regime map -- the 13.8x holds INSIDE the frontier, fails OUTSIDE = the ceiling-fail explained.)
   HARD-FAIL: no monotone boundary; net-savings flat (or absent) across the regime sweep -> active-gating has no
      characterizable net-win regime here (claim does not hold even as bounded).
SECONDARY (Candidate A):
   HARD-PASS: epistemic-surprise gate >= 20% compute reduction at iso-quality vs softmax-entropy baseline AND stable under
      stochastic-input ablation (noisy-TV: gate-rate on stochastic injection < 2x).
   HARD-FAIL: gate collapses to < 5% entropy by training end OR noisy-TV trap (>= 2x gate-rate on stochastic injection).
```

## DISCRIMINATING-REGIME / SELECTIVE-DEADLOCK guard (Skunkworks-required; the drill's verified failure mode)
```
The dominant 2024-25 active-gating failure mode is SELECTIVE-DEADLOCK (aux-loss-resistant; ~1/3 of layers collapse to a
single expert/slot). REQUIRED: at each grid point, record per-cell EXPERT/GATE-USAGE ENTROPY traces. DISTINGUISH:
   "active-gating net-loss because the regime is past break-even" (a REAL boundary point; score it) vs
   "net-loss because the gate DEGENERATED (selective-deadlock: usage-entropy collapsed -> single expert)" (a DEGENERATE
    NON-TEST -- the gate didn't run, it deadlocked; report it, do NOT score it as a break-even boundary point).
Do NOT pre-register on AGGREGATED quality metrics that hide degenerate-regime (drill: WEAK-bucket avoid). The break-even
boundary verdict requires usage-entropy IN a non-degenerate range at the boundary points. (DEGENERATE-REGIME-NOT-
REFUTATION class, active-gating instance; composes with 18/8b/ARCH-A/B discriminating-regime guards.)
```

## Provenance (recapture_of populated per Skunkworks ruling B)
- recapture_of = scorecard_claim_8a_active_gating_13.8x (FLAGSHIP -> PARTIAL; ceiling_followup HARD_FAIL @perf 0.83; B3a
  top-k-error gate, b3axb3b family)
- failing_config_avoided = an UNCONDITIONAL single-point 13.8x active-gating speedup claim with NO perf-cost break-even
  characterization -> fails at the perf ceiling because the net-benefit is regime-dependent (memory/dispatch tax + perf drop)
- method_delta = replace the single-point speedup claim with a DETERMINISTIC break-even REGIME MAP (Candidate B; total-cost
  incl. memory/dispatch, not just FLOPs; perf at each point; selective-deadlock entropy guard) + a secondary Bayesian-
  surprise mechanism arm (Candidate A). Same active-gating mechanism as the anchor (perf-cost) -> anchor-match holds.
- FULL >=3 seeds -> CERT_CHAIN_GRADE. measured-bounds: the result IS the (batch,seq,sparsity) envelope, explicitly.
- P_deflated: 0.45 (Candidate B; survey-gap, instrumentation-heavy) / 0.40 (Candidate A; unverified primary SDT).

## Cert-chain next steps
1. Skunkworks SCHEMA-VET WITH the new ANCHOR-MECHANISM-MATCH check (confirm Candidate B's perf-cost characterization
   matches the active-gating perf-cost anchor -- documented above) + falsifiable bands + no-Goodhart (boundary map IS the
   claim, not a proxy) + selective-deadlock discriminating-regime guard + measured-bounds framing.
2. Director STEP-2 LOCK.
3. Exp-Dev cell-author (break-even sweep harness + entropy traces; Bayesian-surprise arm) + smoke (tiny grid, laptop) ->
   FULL (REMOTE R4 Day-N) -> verdict -> re-atomize (Skunkworks per-batch VET + Testbed invariant).

## Batch note
8a is the 3rd efficiency-batch component. SIBLINGS: 18 efficiency-composition = DE-SCOPED (mechanism-mismatch; honest
documented MIDDLE; Option-1 gate-orthogonalization queued on USER strategic-value confirm). 8b surprise-gating = cell
authored but RE-DESIGN required (failure-mode-instantiation as arm-fixable knobs; ratified). 8a (this) = anchor-matched,
drillable, draftable. All HEAVY -> REMOTE Day-N (R4 Day-2 has NOTHING FULL-ready per the honest re-plan).

-- Exp-Dev (Prover) [DRAFT]
