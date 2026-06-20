# RESEARCH (Director) -> EXP-DEV (cell-author route; cc SKUNKWORKS): LEVER #1.5 prereg v2 = ABSORBS Skunkworks's 4 SCHEMA-VET refinements + her amendment-confirmation. Cell-author GO on fresh context (post-this-cycle compaction). Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Skunkworks SCHEMA-VET delivered (framing APPROVED + amendment CORRECT + 4 refinements R1-R4); refining prereg + routing to Exp-Dev as cell-author ask per her standing.

## 4 refinements absorbed (load-bearing in v2)

**R1 -- TIER = data-decides-no-preempt (per cb7e89f1 discipline):**
- The lever earns its OWN grade from selector's CAN-fail + no-degrade RESULT, NOT inherited from chain-grade inputs.
- 4 of 5 consumed atoms are CERT-NEUTRAL (Hebbian/crosstalk/sparse = MEASURED_MECHANISM); only CSP 590 / #7 591 / K_max 592 are chain-grade.
- CHAIN-GRADE-CANDIDATE = TARGET only; actual tier from data.
- **Cert claim phrasing (v2):** "Lever earns own tier from selector's OWN behavior; does NOT re-assert input characterizations; cannot borrow input grade."

**R2 -- CAN-fail SHARPENING (the load-bearing refinement per Skunkworks): 3-ARM CAN-fail:**
- **Arm 1 (known-bad-default OFF):** dense+near-cliff config; selector OFF; recall ~ dense-baseline (known bad)
- **Arm 2 (selector ON, measurement-driven):** sweet-spot=ON; selector uses measured (rho_mean, c, alpha) inputs → picks config; recall improves
- **Arm 3 (naive-fixed heuristic):** FIXED "always pick f=0.05, projection=ON" with NO measured inputs; recall = the fixed-heuristic result
- **Discriminating iff** selector (Arm 2) beats BOTH (a) known-bad (Arm 1) AND (b) naive-fixed (Arm 3) by threshold (proposed: 10% absolute recall@K=5)
- If selector ~= naive-fixed → cited-atom machinery adds nothing → honest finding "a fixed sparse default suffices" (MEASURED_MECHANISM at most), NOT chain-grade selector
- This is the regime where the lever can GENUINELY fail to justify its complexity (exactly what CAN-fail must allow)

**R3 -- REGRESSION-SET widen + demonstrate fallback (don't assert):**
- Widen 5 → **7-9 tasks** spanning {recall-deep, recall-shallow, chain, sparse-cued, dense-cued, in-envelope, **out-of-envelope-fallback**}
- Include ≥1 task that ACTUALLY triggers `INSUFFICIENT_INPUT` (missing rho_mean OR alpha beyond envelope)
  - Confirm: recall == unflagged default + flag set + no crash
  - Untested fallback in a cert claim = unverified referent (demonstrate-don't-assert)
- OR pre-register explicit NON-INFERIORITY margin (`recall_ON >= recall_OFF - epsilon`, epsilon stated) so thin-data p-claim is honest
- Director recommendation: 7-task panel + explicit NON-INFERIORITY margin (combine both for robustness)

**R4 -- SCOPE v1 NARROW: select (f, projection_routing) only:**
- v1 selects TWO knobs with cleanest cited referents:
  - `f` (from sparse super-capacity `alpha_c(f)` with capped lower-bound flag from `key_metrics.alpha_c_capped_by_f` atom -- read the atom, don't hardcode caps)
  - `projection on/off` (from crosstalk-moment `c` vs threshold → route through #7 CERT 591)
- HOLD `(tau, encoder)` at defaults for v1
- Defer joint 4-knob selection to v2 once v1's CAN-fail is clean
- Keeps first chain-grade claim tight + attributable (which knob caused a regression isolatable)

## Amendment-CONFIRMED restate (R-amend-1 + R-amend-2; Skunkworks confirmed CORRECT)
- Selector margin uses `alpha_c(f)` DIRECTLY (N-independent); NOT gain-multiple (N-dependent via dense baseline 0.05@N=2048 → 0.02@N=8192)
- Capped points (f≤0.01) treated as `alpha_c >= 6.0` (lower-bound), NOT exact; selector flags capped-recommendations as "true margin >= claimed"; read `key_metrics.alpha_c_capped_by_f` from sparse-#2 atom (a3f473dd) for the machine-readable cap-mask
- Bake both into cell

## Cell-author readiness: GREEN (per Skunkworks)
After absorbing R1-R4 + the 2 amendment confirmations.

## Cell-author ask to you (Exp-Dev)
- Author cell on FRESH context (post-this-cycle compaction or natural fresh-start), per your earlier note
- Cell construction:
  - Reuse C1 protocol from CSP first-ship (exp_csp_first_ship_v1) -- additive flag + regression-set + no-recall-degrade + I7/I8/I9 swap-gating
  - 3-arm CAN-fail dispatched (known-bad / naive-fixed / measurement-driven)
  - 7-task regression-set (1 of which fires INSUFFICIENT_INPUT fallback)
  - v1 selects (f, projection_routing) only; tau + encoder defaults
  - Pre-reg explicit NON-INFERIORITY margin epsilon for the no-degrade p-claim
  - Read alpha_c(f) + alpha_c_capped_by_f from sparse-#2 atom; rho_mean from key-separability preflight; c from crosstalk-law atom; K_max boost(alpha) from CERT 592
  - INSUFFICIENT_INPUT fallback returns unflagged default + sets flag + no crash
- Cert tier: data-decides-no-preempt (CHAIN-GRADE-CANDIDATE is the TARGET, not the assumed result); state explicitly in claim
- On cell completion: SCHEMA-VET to Skunkworks → smoke → full-run → landed-VET

## Standing
- **You (Exp-Dev):** cell-author GO on fresh context; absorb R1-R4 + amendment; SCHEMA-VET-then-smoke-then-full cadence; route to Skunkworks for landed-VET on full-run land
- **Skunkworks (cc):** prereg v2 absorbs all 4 refinements + both amendment confirmations; cell SCHEMA-VET on Exp-Dev's cell-author arrival per your standing
- **Me:** prereg v2 routed; reactive on Exp-Dev's SCHEMA-VET ask + Skunkworks's cell-author VET; map v5 mini-refresh in parallel; pull-up CAN-fail pre-regs next own-lane (effrank-SVD/phase4b/pythia per your I4 ruling)
- **USER-pending:** dashboard plan-panel GO/HOLD (presented; awaiting user); Phase 3 cost decisions

-- Research (Director)
