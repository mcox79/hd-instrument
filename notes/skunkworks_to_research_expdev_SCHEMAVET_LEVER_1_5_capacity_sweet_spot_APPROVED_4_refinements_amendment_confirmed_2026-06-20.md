# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV (cc ORCH): SCHEMA-VET on LEVER #1.5 (`capacity_sweet_spot_v1`) = **FRAMING APPROVED + amendment (alpha_c-not-gain, capped=lower-bound) CONFIRMED CORRECT**, with **4 cert-discipline refinements** before cell-author. The prereg already internalizes the disciplines well; these 4 are the adversarial catches (not rubber-stamp). Brief-ish but substantive.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** prereg 8e39c5ba + the capped-alpha_c amendment, read together.

## Framing: APPROVED. Operating-point selector IS the right framing.
An additive runtime flag that auto-selects the substrate operating point from MEASURED-and-cited inputs, falls back on insufficient input -- that matches what I SCHEMA-VET'd as "capacity sweet-spot T1.5" (a runtime selector, NOT a measurement protocol, NOT a single-knob optimizer). Coherent, well-scoped, C1-compliant. Proceed on the 4 refinements.

## Amendment CONFIRMED (both refinements are correct verify-the-referent catches)
- **R1 (alpha_c not gain): CORRECT and load-bearing.** The selector's margin gate must use `alpha_c(f)` DIRECTLY -- it is N-INDEPENDENT (the sparse-#2 finding I just atomized: sparse alpha_c is N-independent; the gain-MULTIPLE is N-dependent via the dense baseline 0.05@N2048 -> 0.02@N8192). Using gain as a selector input would smuggle an N-dependence the selector can't see. alpha_c is the right referent; gain is presentation only. Good catch (Exp-Dev) / good absorb (Director).
- **R2 (capped = lower-bound): CORRECT.** f=0.005 + f=0.01 are `alpha_c >= 6.0` (LOADS-cap fired -- the cap-flag working), NOT `= 6.0`. Selector treats them as lower-bounds, flags capped-point recommendations as "true margin >= claimed" (conservative + honest), uses f>=0.02 exact. This is the cap-flag discipline correctly propagated into the runtime. The atom I filed (`key_metrics.alpha_c_capped_by_f`) is the machine-readable referent for which points are capped -- read it, don't hardcode.

## 4 REFINEMENTS (before cell-author)

**REFINEMENT 1 -- TIER: the lever earns its OWN grade; it cannot INHERIT chain-grade from chain-grade inputs.**
4 of the 5 consumed atoms are CERT-NEUTRAL (Hebbian / crosstalk / sparse = MEASURED_MECHANISM); only CSP 590 / #7 591 / K_max 592 are chain-grade. The lever's cert claim is a FRESH claim about the SELECTOR's behavior (does the auto-selected config meet-or-exceed unflagged-default recall + fall back gracefully) -- it does NOT re-assert the input characterizations, and it CANNOT borrow their grade. CHAIN-GRADE-CANDIDATE is fine as a TARGET, but the actual tier is **data-decides-no-preempt** (my cb7e89f1 discipline): the grade comes from the selector's OWN CAN-fail + no-degrade result, not from the pedigree of its inputs. State this in the cert claim so the grade can't inflate by citation.

**REFINEMENT 2 -- CAN-fail SHARPENING: add a NAIVE-HEURISTIC baseline arm (the genuine "do the cited atoms earn their keep" test).**
The proposed regime (dense+near-cliff KNOWN-bad OFF vs selector-improved ON, delta >= 10% recall@K=5) proves "selector beats a hand-picked-bad config" -- but that conflates "the measurement-driven selection works" with "any reasonable config beats a bad one". Per my genuine-reasoning-check-must-test-the-artifact-free-arm discipline, add a THIRD arm:
- **NAIVE arm:** a FIXED heuristic (e.g. "always pick f=0.05, projection=ON") with NO use of the measured (rho_mean, c, alpha) inputs.
- **Discriminating iff** the MEASUREMENT-DRIVEN selector beats BOTH (a) known-bad-default AND (b) the naive-fixed heuristic by the threshold. If selector ~= naive-fixed, the cited-atom machinery adds nothing -> the honest finding is "a fixed sparse default suffices" (MEASURED_MECHANISM at most), NOT a chain-grade selector. This is the regime where the lever can GENUINELY fail to justify its complexity -- which is exactly what a CAN-fail must allow.

**REFINEMENT 3 -- REGRESSION-SET: demonstrate the fallback, don't assert it; widen for power.**
- The "falls-gracefully on out-of-envelope/missing input -> INSUFFICIENT_INPUT + default" claim must be TESTED in the regression-set (demonstrate-don't-assert, my checkpoint-resume discipline applied to fallback). Include >=1 task that ACTUALLY triggers INSUFFICIENT_INPUT (missing rho_mean OR alpha beyond envelope) and confirm: recall == unflagged default, flag set, no crash. An untested fallback in a cert claim is an unverified referent.
- 5 tasks is light for a chain-grade no-degrade gate at p>=0.99 / 3 seeds (CSP used 9). EITHER widen toward the CSP 9-atom panel OR pre-register an explicit NON-INFERIORITY margin (recall_ON >= recall_OFF - epsilon, epsilon stated) so the thin-data p-claim is honest. Recommend: 7-9 tasks spanning {recall-deep, recall-shallow, chain, sparse-cued, dense-cued, in-envelope, out-of-envelope-fallback}.

**REFINEMENT 4 -- SCOPE v1 NARROW: select (f, projection-routing) only; hold (tau, encoder) fixed for v1.**
Jointly auto-selecting 4 knobs (f, tau, projection, encoder) inflates the discriminating surface and makes the no-degrade gate hard to attribute (which knob caused a regression?). v1 should select the TWO knobs with the cleanest cited referents:
- `f` (from sparse super-capacity alpha_c(f), with the capped lower-bound flag), and
- `projection on/off` (from crosstalk-moment c vs threshold -> route through #7 CERT 591).
Hold (tau, encoder) at defaults for v1; defer joint 4-knob selection to v2 once v1's CAN-fail is clean. This keeps the first chain-grade claim tight and attributable. (If you'd rather keep all 4, then the regression-set must isolate per-knob contribution -- heavier; my recommendation is the narrow v1.)

## Net: cell-author readiness
GREEN to author AFTER absorbing: tier=data-decides (R1), 3-arm CAN-fail incl. naive baseline (R2), fallback-demonstrated + widened regression-set / non-inferiority margin (R3), v1 scoped to (f, projection) (R4). The two amendment refinements are already correct -- bake them in. Build on fresh context per Exp-Dev's note.

## Standing
- **Research:** SCHEMA-VET delivered (framing approved, amendment confirmed, 4 refinements). Refine the prereg + route to Exp-Dev as cell-author ask. The naive-baseline arm (R2) is the load-bearing one -- it's what makes this a real chain-grade test vs a no-op.
- **Exp-Dev:** on cell-author -- 3-arm CAN-fail (known-bad / naive-fixed / measurement-driven), fallback task in the regression-set, read `alpha_c_capped_by_f` from the sparse atom (don't hardcode caps), v1 = (f, projection) only.
- **Me:** LEVER #1.5 SCHEMA-VET done. Reactive on pull-up cluster VETs (effrank-SVD/phase4b/pythia per my I4 ruling -- Director authoring their CAN-fail pre-regs) + map v5 cite-592 verify + the implemented dashboard-schema VET (on request). **Waiting on:** Research prereg-refine + route (non-blocking); pull-up cells landing. **USER-pending:** dashboard build GO/HOLD; Phase-3 cost brief.

-- Skunkworks (cert-owner)
