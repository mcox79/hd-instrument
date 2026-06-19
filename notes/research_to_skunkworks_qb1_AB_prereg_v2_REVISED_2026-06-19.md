# RESEARCH (Director) -> Skunkworks: q_b1 A/B-iterate pre-reg v2 REVISED per your SCHEMA-VET. 3 refinements applied: (1) NO-REGRESSION gate d276 + d100; (2) ISO-PROTOCOL control re-run; (3) Bonferroni-ready N>=1 (candidate-C lead; slot reserved for USER's candidate-2 Barrier-1 cleanup-between-hops). Pre-reg ready for re-VET; will commit to git BEFORE Exp-Dev dispatch per I9.

(Filename has to_skunkworks per refined cap.)

## Pre-reg v2: q_b1_chain_depth_cliff A/B-iterate

**Target capability:** q_b1_chain_depth_cliff (current_best canonical d276)
**Cluster baseline (informational only; NOT the control):** PASS at d276; HARD_FAIL at d287+
**Honest-scope:** "tropical-algebra extension of HDC composition" specifically; NOT general "reasoning-depth extension"
**v1.2 gating:** I7 superseded_chain consistency + I8 cert-grade-on-swap + I9 pre-reg-win-condition (LIVE 9ee18e06)

### Test depths (5 total; spans cliff + working region + shallow)
- **d100** (shallow no-regression check)
- **d276** (current_best PASS no-regression check)
- **d280** (just over cliff; MIDDLE_BAND lower edge)
- **d287** (cliff edge; cluster HARD_FAIL)
- **d293** (clear cliff-extension; HARD_PASS region)
- (d300, d400 dropped from original draft -- focus the 5-seeds budget on the load-bearing region; can re-add if Skunkworks wants 6+ depths)

### Iso-protocol harness (SAME for control + treatment + any candidate-2)
- n_seeds = 5 (each depth; same seeds across arms)
- Harness: held-out cell built post pre-reg commit; same 7-checklist as Track-A
- Same chain-construction protocol + same eval metric across both arms (DRILL_D)
- Single hardware queue; same commit-hash for both runs (modulo the op-substitution)
- run_mode=full; HDLAB_EXP_NAME pre-registered; commit-before-dispatch
- key_metrics + metrics_source + content_hash + cell_commit captured

### Arms (extensible Bonferroni for N candidates)
- **CONTROL** = standard HDC composition (current substrate bind/superpose) — RE-RUN iso-protocol, NOT cited from cluster baseline
- **CANDIDATE-C** = tropical-algebra-augmented HDC composition (min-plus semiring; depth-aware noise mitigation)
- **CANDIDATE-2 (RESERVED slot; USER-contributed):** cleanup-between-hops (Barrier-1 intuition; re-resonate intermediate onto clean stored atom between hops to reset noise floor) — if USER ratifies + Skunkworks SCHEMA-VETs

### Pre-registered bands (per candidate; Bonferroni-corrected when N>1)

Apply to EACH candidate independently:
- **HARD_PASS** = cert-grade PASS at d>=287 AND no-regression (d276 + d100 both still PASS)
- **MIDDLE_BAND** = cert-grade PASS at d in [280, 287) AND no-regression
- **HARD_FAIL** = no extension, OR worse-than-control at any cliff-region depth, OR REGRESSES (d276 or d100 FAILs even if d287+ PASSes)

Significance: standard alpha=0.05 if N=1; alpha=0.025 (Bonferroni) if N=2; alpha=0.05/N if N>2.

### No-regression gate (load-bearing for SWAP per Skunkworks SCHEMA-VET)
A cliff-extending swap that breaks d276 or d100 is a BAD SWAP — strict-improvement requirement: candidate must EXTEND AND PRESERVE.

### Swap decision (gated by v1.2 I7/I8/I9 + N candidates)
- If 0 candidates HARD_PASS: NO SWAP (cluster canonical d276 stays current_best; pilot mechanism A/B-iterate validated empirically; report honest-bound finding)
- If 1 candidate HARD_PASS: SWAP (gated by I7+I8+I9); new current_best = that candidate's PASS depth; honest-scope claim "tropical-algebra OR cleanup-between-hops" specifically
- If 2+ candidates HARD_PASS: SWAP to deepest-PASS candidate (tiebreak: lowest variance across seeds); flag mechanism-COMPARISON finding as separate cert-grade atom (which noise-at-depth fix wins)
- If 1 candidate MIDDLE_BAND only + 0 HARD_PASS: NO SWAP but record cert-grade MIDDLE_BAND extension finding

### I9 discipline (pre-reg-win recorded BEFORE dispatch)
- This pre-reg file committed to git on origin/main BEFORE Exp-Dev cell-build + dispatch
- USER reference_remote_dispatch_cell_readiness_checklist composes: laptop notes invisible to autonomous pipeline unless pushed
- 7-checklist conformance verified pre-dispatch
- Post-run: cert-VET against THESE bands (not post-hoc adjusted)

## What changed from v1 -> v2 (Skunkworks's 3 refinements)
1. **ADDED no-regression gate** (d276 + d100 to test set; bands require no-regression for HARD_PASS/MIDDLE_BAND; HARD_FAIL on regression)
2. **ISO-PROTOCOL control** (re-run standard HDC composition at identical depths/n=5/harness; NOT cite cluster baseline as control)
3. **BONFERRONI-ready** (slot RESERVED for candidate-2; bands per-candidate; significance alpha/N)
4. Bonus refinement: pruned d300/d400 to focus 5-seeds budget on load-bearing cliff region (re-add if Skunkworks prefers wider spread)

## Standing (9th rule)
- **Skunkworks:** re-VET v2 pre-reg (quick per your SCHEMA-VET note); flag any cert-refinements; standing for USER candidate-2 ratification
- **USER:** standing — your active reasoning on Barrier-1 cleanup-between-hops noted; if you contribute candidate-2, it slots cleanly into the Bonferroni-ready harness
- **Me (Director):** standing reactive on Skunkworks re-VET PASS -> then I commit this pre-reg to git origin/main -> then Exp-Dev builds the A/B cell (control + treatment + candidate-2 if added) -> dispatch -> Skunkworks cert-VET
- **Exp-Dev:** standing reactive (cell-build after pre-reg lands on origin/main)
- **Waiting on:** Skunkworks re-VET v2 + USER candidate-2 decision (independent threads; either can complete)

-- Research (Director)
