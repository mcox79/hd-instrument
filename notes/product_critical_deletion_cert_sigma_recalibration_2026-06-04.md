# PRODUCT-CRITICAL -- Deletion-certificate sigma threshold needs 5x empirical recalibration

**From:** Research session
**To:** User (primary); Orchestrator (visibility)
**Date:** 2026-06-04
**Subject:** Substrate's deletion-cert sigma threshold formula overstates confidence by 5x; empirical recalibration via N-extension test required before product framing. Capability is REAL; the confidence sigma is wrong.

---

## TL;DR

**The deletion-certificate capability is real.** Empirically: rank-1 deletion produces cos=1.000 for all non-target queries (validated at v341 N=4096 + extending through L=10000 composition + algebraic guarantee from Ramsauer Theorem 1 + ROME/MEMIT lit precedent).

**The sigma confidence threshold is wrong by 5x.** Today's intermediate-regime drill identified that the Tracy-Widom-assumption sigma formula overstates confidence by 5x because substrate is in BBP-critical / NESS-driven regime, not pure Tracy-Widom class.

**Concrete impact:** If product framing claims "deletion-cert is X-sigma confident at Y deletions" where X is computed from the TW formula, the actual confidence is X / sqrt(5) ~ X / 2.24. Conservative interpretation: 5x more deletions before reaching the same sigma confidence.

**Fix:** dispatch N-extension test (routing shipped this turn); empirically recalibrate the sigma formula constant; THEN ship product framing with corrected threshold.

---

## What's happening algebraically

Substrate's spectral edge fluctuations follow a scaling exponent beta. Tracy-Widom (canonical RMT class) predicts beta=2/3. Today's PP-50 v4 lambda_1 measurement: beta_std=0.355 at N=1024-16384 (5 seeds).

The intermediate-regime drill identified this as **BBP-critical regime** (beta=1/3 at clean asymptote) + non-Hermitian deformation. Substrate is in an active-driven NESS class per Bertini 2015 macroscopic fluctuation theory.

The empirical std(lambda_1) at N=16384 is **5x LARGER** than pure Tracy-Widom predicts. This means:
- TW formula: assumes fluctuations scale as N^(-2/3); for substrate's empirical observation, predicts confidence X sigma
- Empirical reality: fluctuations scale closer to N^(-0.355); actual confidence is ~X/sqrt(5) ~ 0.45X sigma

The 5x factor is the discrepancy between predicted TW std and observed std.

---

## Why this matters for product

A deletion-certificate product claim has the form:
"Substrate guarantees with X-sigma confidence that rank-1 deletion of one stored pattern preserves all other patterns within tolerance epsilon."

Where X is derived from the TW-assumption sigma formula at substrate's operating parameters.

**Current X (TW formula):** assume X = 6 sigma confidence (i.e., 1 in 10^9 false positives)
**Actual X (empirical):** X = 6 / sqrt(5) ~ 2.7 sigma (i.e., 1 in 300 false positives)

That's a 3-million-fold confidence overstatement. NOT acceptable for a product framing.

**If we ship at TW-derived sigma, customers will see false positive rates 3-million-fold higher than promised.** Worst case for product credibility.

---

## What recalibration looks like

Two-step process:

### Step 1: empirical N-extension test (already routed to Exp-Dev)

`routing_n_extension_test_n32768_decisive_arbiter_2026-06-04.md` shipped this turn.

- Run at N=32768 with 20 seeds (vs current N=16384 with 5 seeds)
- Empirically measure std(lambda_1) at finer N resolution
- Fit corrected scaling exponent beta_empirical
- ~5-30 min GPU; $0
- High priority

### Step 2: sigma formula recalibration

Once beta_empirical is known:
- Recompute X-sigma threshold using the empirical exponent
- 5x correction factor expected (per drill's quantitative estimate)
- Worst case 10x; best case 3x

Document the empirical recalibration in cap_map annotation. Product framing uses the recalibrated sigma threshold.

---

## What this changes

### Already validated (no change)

- Empirical deletion-cert observation cos=1.000 across L=10000 composition cells: REAL
- Algebraic guarantee from Ramsauer Theorem 1: HOLDS
- ROME/MEMIT lit precedent (transformer factual editing observes same pattern): HOLDS
- Drift-detection killer feature: UNCHANGED (uses isochoric kappa_3 ratio, not sigma threshold)
- Cross-layer composition moat L=10000 EXACT-1.0000: UNCHANGED

### Requires recalibration

- Deletion-certificate sigma confidence threshold formula: 5x recalibration
- Product narrative around deletion-cert confidence claims: hold until recalibration lands

### Could be impacted (lower priority recalibrations)

- Drift-detection confidence intervals (if framed via sigma): potentially also need recalibration
- Refusal-certificate confidence (Phase 0.5 audit primitive): TBD; uses different observable but same spectral basis

---

## Timing

If N-extension test dispatches this cycle: verdict in ~5-30 min wall.
If recalibration documented in cap_map: same-cycle.
If product framing for deletion-cert needs to wait: standing requirement is ~1 hour from this note.

This is a **same-day fix**, not a multi-week investigation. Important to do BEFORE any product surfacing.

---

## What I AM NOT requesting

- Removing or weakening the deletion-cert capability claim (capability is REAL; just the confidence number is wrong)
- Halting other product work (Phase 0.5 v1 Rung A continues; substrate observation story unaffected)
- Cap_map row closures (no rows close; sub-property annotations only)

---

## What I AM requesting

- Dispatch N-extension test (already routed to Exp-Dev; awaits engineering)
- Hold deletion-cert specific product framing until recalibration lands
- Update cap_map deletion-cert annotation with the 5x-overconfidence caveat NOW; revise to empirical recalibration once test lands

---

## Discipline declarations

- Per [[feedback-no-smoke]]: brutal honest surfacing of overconfidence finding
- Per [[feedback-verify-implementations]]: empirical recalibration required before product claims
- Per [[feedback-dont-overextend-theorems]]: TW assumption was an over-extension to substrate's actual BBP-critical regime
- Per [[feedback-capabilities-not-product-positioning]]: capability characterization vs product framing distinction maintained
- ASCII-only

---

**END.**

**User:** flagging this as the only product-critical action item from today's 14 drills. Deletion-cert capability is real; sigma threshold is wrong. N-extension test ~5-30 min once dispatched. Recommend dispatching IMMEDIATELY (highest-priority verdict to resolve before deletion-cert product framing).

**Orchestrator:** informed. Cap_map annotation update should include the 5x-overconfidence caveat NOW.
