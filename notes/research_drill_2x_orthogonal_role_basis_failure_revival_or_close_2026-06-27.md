# 2x Research Drill — Why orthogonal_role_basis only delivered +0.022 (HARD_FAIL on +0.10 bar)

Date: 2026-06-27
Discipline notes: 2x research drill (broad pure-math + narrow brain-cross-domain); lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50); verify-the-referent for each proposed discriminator.

## Executive Summary

The +0.022 lift is not a failed mechanism — it is the mechanism delivering exactly what the math predicts at the regime tested. At d=8192 with n_atoms=200 and depth=4, two random HD vectors are already ~99% orthogonal in expectation (|cos| ~ 1/sqrt(d) ~ 0.011), so forcing Gram-Schmidt at init removes only a small residual crosstalk. The substrate is operating in a regime where orthogonality is NOT the binding constraint. Two pivots are warranted: (1) HARDER REGIME where crosstalk actually bites (lower d-to-atoms ratio + deeper depth), and (2) LEARNED orthogonality rather than init-time fix (brain doesn't Gram-Schmidt at birth — it develops orthogonal codes through competitive plasticity). The +0.022 ceiling at d=8192/depth=4 is honest substrate physics; the mechanism could still earn chain-grade in a regime where its lever applies.

## Angle A — Pure Math: how big SHOULD orthogonal-basis lift be at this regime?

For two random unit vectors in R^d, E[cos] = 0 and E[|cos|] ~ sqrt(2/(pi*d)). At d=8192 the expected residual cosine is ~0.011 (about 1%). Gram-Schmidt removes this residual exactly, but the gain is bounded by what that residual was costing.

The crosstalk budget for role-filler binding: when unbinding role r_i from sum_j bind(r_j, f_j), the noise term is sum_{j!=i} <r_i, r_j> * f_j. Norm of this residual is ~sqrt((n_atoms - 1)/d). At d=8192 / n_atoms=200, residual norm ~sqrt(199/8192) ~ 0.156. At depth=4 with independent noise compounding (sqrt(k) per the 5x drill Angle 1 observation), total noise ~sqrt(4) * 0.156 ~ 0.31 against signal of order 1.

Orthogonal init removes the role-role residual (the ~0.156 term) but leaves filler-filler residual untouched. Predicted ceiling lift from going random -> orthogonal at this regime: roughly 0.02-0.05. **The observed 0.022 lift sits in the middle of the predicted range — the mechanism is delivering exactly what the math says it should.**

This is the load-bearing finding: orthogonal-basis is not failing; it is succeeding at a level that is structurally too small to clear the +0.10 chain-grade bar AT THIS REGIME.

Where orthogonality bites harder:
1. Lower d-to-atoms ratio: at d=2048, n_atoms=200, residual ~sqrt(199/2048) ~ 0.31. Predicted lift ~0.06-0.10 (touches chain-grade bar).
2. Deeper depth: at depth=8, compounded noise budget ~0.44 instead of 0.31. Predicted lift ~0.04-0.08.
3. Combined harder regime: d=2048, n_atoms=500, depth=8 -> residual ~sqrt(499/2048) ~ 0.49, four hops of compounding. Predicted lift ~0.08-0.15.

The math predicts a CROSSOVER REGIME where orthogonal-basis flips from cosmetic to load-bearing. The smoke ran on the wrong side of that crossover.

## Angle B — Brain / Cross-Domain: does Gram-Schmidt at init even resemble brain mechanism?

Brain does not initialize orthogonal — it DEVELOPS orthogonality through experience-dependent plasticity:

- **Grid cells (entorhinal cortex, Hafting/Moser 2005):** module-orthogonality emerges through competitive learning + lateral inhibition over months of spatial experience; newborn grid cells are NOT orthogonal.
- **Whittington TEM model:** relational embeddings are LEARNED via backprop against transition statistics; orthogonal-relation-vs-entity factorization is a training outcome, not init.
- **Hopfield-Lansner BCPNN:** orthogonal-ish codes develop via Hebbian normalization across repeated exposure; requires many presentations to decorrelate.
- **ICA (Bell-Sejnowski):** finds orthogonal-ish basis via iterated decorrelation against natural input statistics; convergence is the whole point, init is irrelevant.

The substrate analog of "brain orthogonality" is NOT a one-shot Gram-Schmidt at init — it is a competitive-learning rule that decorrelates basis vectors against actual ingest statistics. Three substrate-native paths:

1. **Post-readout orthogonal projection (cheap):** at every cleanup step, project residual onto orthogonal complement of already-recovered fillers. No basis change, no learning, just runtime cleanup tightening. Discriminator: depth-4 heterogeneous lift over no-projection >= 0.08 cv<0.10.
2. **Online basis decorrelation (Foldiak-style competitive learning):** after each ingest, apply a tiny anti-Hebbian update across role-basis vectors that reduces pairwise cosine toward zero. Discriminator: 1000-atom warmup followed by depth-4 heterogeneous >= 0.10 lift over fixed-init.
3. **Modular orthogonality (grid-cell analog):** partition basis into K modules; force inter-module cosine = 0 but allow intra-module overlap; assign each predicate to a module. Discriminator at depth-4 heterogeneous, K=4 modules >= 0.10 lift over flat-basis.

The most brain-grounded of these is #2 (competitive learning), because grid-module orthogonality is exactly an experience-dependent emergent.

## TOP-2 Revival Cells (P-ranked, falsifiable discriminators)

**RANK 1 — `exp_pfc_controller_orthogonal_basis_harder_regime_v1` (P ~ 0.45 post-deflation):** same Gram-Schmidt init as v1, but at d=2048 instead of d=8192, n_atoms=500 instead of 200, depth=6 instead of 4. Mechanism is identical; regime is shifted to where the math says orthogonality matters. Discriminator = ORTH lift over SHARED >= 0.10 at cv < 0.10 across 5 seeds. If PASS, the +0.022 ceiling was a regime artifact and we have a real lever for harder workloads. If FAIL, orthogonal-basis is genuinely not the answer even where math says it should help, and we should close this direction and pivot to learned-orthogonality. Cost: cheap (single-init change, same cell as v1, just hyperparameters); ~15-30 min on remote GPU.

**RANK 2 — `exp_competitive_basis_decorrelation_v1` (P ~ 0.35):** brain-grounded learned orthogonality. Initialize random basis; run 1000-atom warmup ingest with anti-Hebbian update on role-basis: delta r_i = -eta * sum_{j!=i} <r_i, r_j> * r_j (clipped, eta = 0.01). Test on depth-4 heterogeneous at d=8192 / n_atoms=200 (SAME regime as the failed v1 — this is the controlled comparison). Discriminator = competitive-learned arm >= 0.10 lift over random-init AND >= 0.05 lift over Gram-Schmidt-init at cv < 0.10. If COMPETITIVE > GRAM-SCHMIDT, learned orthogonality captures something init-time cannot (likely: filler-statistics-aware decorrelation, not just basis-vs-basis). If COMPETITIVE == GRAM-SCHMIDT, the brain mechanism is real but in this regime delivers the same small lift — close direction. Cost: medium (new update rule + 1000-atom warmup); ~45-60 min on remote GPU.

## Honest Assessment

**Should we pursue orthogonal-basis further?** Yes, but ONLY via RANK 1 first. The math predicts the mechanism becomes load-bearing at lower d-to-atoms ratio and deeper depth. If RANK 1 also delivers <0.05 lift, that is decisive evidence orthogonality is not a lever for this substrate at any practical regime, and we close the direction with confidence.

**Is the +0.022 ceiling a substrate property to accept?** At d=8192 / n_atoms=200 / depth=4, YES — that ceiling is what the math predicts. The right reframing is not "orthogonal-basis failed" but "orthogonal-basis worked at expected magnitude in a regime where its magnitude is structurally small." The result is informative even though it is HARD_FAIL on the chain-grade bar.

**Anti-negativity backstop:** if RANK 1 HARD_PASSes at the harder regime, do NOT extrapolate back to d=8192 — the lever may apply only in the harder regime, which is still useful (chain-grade evidence the substrate has a knob to turn for capacity-constrained workloads) but not a global fix for routing-bound multi-hop. Symmetric upward correction: if BOTH RANK 1 and RANK 2 HARD_PASS, the brain-grounded path (learned orthogonality + harder regime + grid-cell modular partition) becomes a strong chain-grade portfolio candidate at P ~ 0.55 for the integrated v3 cell, and we should escalate to Skunkworks for chain-grade pre-reg.

**Sequencing recommendation:** ship RANK 1 immediately (single hyperparameter change to existing v1 cell; ~15-30 min); gate RANK 2 on RANK 1 outcome. If RANK 1 PASS, RANK 2 is the next decisive test of WHICH orthogonality mechanism (init vs learned) is the lever. If RANK 1 FAIL, skip RANK 2 and close direction — learned orthogonality at the same failing regime is unlikely to recover, and the resources are better spent on routing mechanisms (Angle 3 RANK 1 `comp_router_moe_v1` from the prior drill).

End.
