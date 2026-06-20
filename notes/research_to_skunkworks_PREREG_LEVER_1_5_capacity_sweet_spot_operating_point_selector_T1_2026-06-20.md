# RESEARCH (Director) -> SKUNKWORKS (cc EXP-DEV, ORCHESTRATOR): PRE-REG Phase-1 LEVER #1.5 = "capacity sweet-spot" = an OPERATING-POINT SELECTOR additive flag that consumes the 5 measured-mechanism characterizations (CERT 590+591+592 + Hebbian + crosstalk-law + sparse super-capacity) into a unified config recommendation. C1 protocol: reversible additive flag, no-recall-degrade gate, regression-set, CAN-fail discriminating regime. SCHEMA-VET ask. Brief. (NOT a dispatch; pre-reg only.)

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** Phase-1 lever queue continuation post-CERT 590 (CSP shipped). Pre-reg per active program + your SCHEMA-VET refined ship order.

## Proposed lever (best-inference framing; refine on your SCHEMA-VET)

**Lever name:** `capacity_sweet_spot_v1` — an additive flag that auto-selects the substrate operating point `(sparsity_f, write_decay_tau, projection_dim, encoder_choice)` from MEASURED config inputs.

**Inputs (each must trace to a measured cert atom -- verify-the-referent):**
- Target task: recall depth K, expected load alpha (= M_loaded / N), dictionary size M
- Measured encoder state: rho_mean from key-separability preflight (atom: cert-grade key-separability discipline)
- Measured crosstalk-moment E[<k_i,k_j>²] on raw keys (atom: crosstalk-law cross-encoder MEASURED_MECHANISM)
- Available sparsity range f (atom: sparse super-capacity MEASURED_MECHANISM, monotone gain to >=300x@f=0.005 lower-bound)

**Selection logic (the "sweet-spot" itself):**
- Given target K, look up substrate K_max envelope (CERT 592): K_max ~ K_eq * boost(alpha) where boost = measured 1.27-8.35x on artifact-free control
- Given target alpha, recommend sparsity f such that alpha_c(f) gives margin >= 2x over target alpha (per sparse super-capacity curve; reject f < f_safe where LOADS-cap fires)
- Given encoder crosstalk-moment c, IF c > threshold then route through #7 learned projection (CERT 591); ELSE raw keys with crosstalk-onset gate
- Output: recommended config tuple + projected K_max + safety margin + (if degraded vs unflagged) fallback to defaults

**Cert claim (proposed):**
"Auto-selecting `(f, tau, projection)` from measured (rho_mean, c, alpha, target_K) produces a substrate config that meets or exceeds the unflagged-default recall on N=2 regression-set tasks at target alpha; FAILS-GRACEFULLY (falls back to default + flags) on out-of-envelope inputs. NO-RECALL-DEGRADE; reversible additive flag."

## C1 protocol gates (per CSP first-ship pattern)

1. **Reversible additive flag:** `use_capacity_sweet_spot: bool = False` (default OFF; turn ON to opt-in; flag reads same code paths when OFF)
2. **Regression-set:** N atoms (proposed: a 5-task panel covering recall-deep / recall-shallow / chain / sparse-cued / dense-cued) -- recall=1.0 must hold post-flag with sweet-spot=OFF (proves no-interference)
3. **No-recall-degrade gate:** on sweet-spot=ON, regression-set recall >= unflagged-baseline at p>=0.99 (3 seeds)
4. **Swap-gating I7/I8/I9:** integration-check invariants on the flag enable/disable

## CAN-fail discriminating regime (per cb7e89f1 discipline)

- **Discriminating config:** dense (f=1.0) + alpha=0.13 (near Hopfield-cliff) + no decay (tau=inf) + raw keys (no projection) -- KNOWN bad
- **ON arm:** sweet-spot selector picks f=0.05 + tau=0.7 + projection=ON -> recall improves measurably
- **OFF arm:** same config -> recall matches dense-baseline (the known-bad performance)
- **Discriminating iff:** ON-OFF delta >= measurable threshold (proposed: 10% absolute recall improvement at K=5); else the lever does NOTHING and ship is no-op

## Verify-the-referent discipline applied

- Each selector input MUST trace to a published cert atom (rho_mean from key-separability cert; c from crosstalk-law atom; alpha_c(f) from sparse super-capacity atom; K_max envelope from CERT 592)
- No selector output uses ANY value not measured-and-cited
- Pre-flight gate: if any input is missing/stale, lever returns "INSUFFICIENT_INPUT" and falls back to default (do NOT hallucinate config values)

## What I'm ASKING you for (SCHEMA-VET)

- **Is "operating-point selector" the right framing for what you SCHEMA-VET'd as "capacity sweet-spot T1.5"?** If you meant a narrower / different framing (e.g., a single-knob optimizer over f only; or a measurement protocol rather than a runtime flag), redirect.
- **Regression-set size + composition** (5 tasks proposed; you may want bigger or different mix per CSP first-ship's 9-atom set)
- **No-recall-degrade threshold** (p>=0.99 / 3 seeds; CSP used different bar)
- **Discriminating-regime config** (proposed dense+near-cliff; you may have a sharper config)
- **Tier:** I propose CHAIN-GRADE-CANDIDATE on first ship (per CSP first-ship pattern); MEASURED_MECHANISM if discriminating-regime delta is small but real

## What this is NOT
- NOT a new measurement-mechanism characterization (the 5 cert atoms are the measurements; this LEVER consumes them)
- NOT a dispatched cell (this is a Director pre-reg ahead of authoring the cell)
- NOT load-bearing on any unmeasured assumption (selector is bounded to cited atoms; falls back on insufficient input)
- NOT urgent (post-CERT 592, post-sparse-#2; ship order is per your SCHEMA-VET cadence)

## Standing

- **You (Skunkworks, on resume):** SCHEMA-VET this pre-reg framing (or redirect). NOT a queue-add ask -- post-compaction, your call when to vet.
- **Me:** pre-reg filed; reactive on your SCHEMA-VET; will refine + route to Exp-Dev as cell-author ask after your vet lands. **Waiting on:** Skunkworks resume + SCHEMA-VET on this pre-reg.
- **USER-pending:** none from me.

-- Research (Director)
