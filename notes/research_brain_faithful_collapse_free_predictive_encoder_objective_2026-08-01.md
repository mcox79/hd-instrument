# Brain-faithful, collapse-free objective for the causal predictive-coding encoder (2026-08-01)

Director synthesis of a 3-way lit-scan drill (parent agent parked; synthesized here from the
landed sub-agent findings). Question: is there a BETTER / slightly-modified, more
brain-foundational + more small-scale-stable way to train our causal predictive-coding encoder
than the current BYOL/I-JEPA EMA-self-distillation + VICReg-variance-hinge recipe, which COLLAPSES
at small proxy scale (causal rep_std 0.0128 -> 0.0180 w/ var_coef 2x, still under 0.020 floor;
bidirectional trains clean at the identical budget)?

Calibration: P deflated per lit-scan discipline; CITED@ vs REASONED@ tagged; ESTABLISHED/CONTESTED
flagged. Citations are search-snippet-confirmed, not full-PDF-verified.

## ROOT-CAUSE DIAGNOSIS (why our causal arm collapses)
Our recipe predicts the encoder's OWN EMA-averaged latent (BYOL/I-JEPA self-distillation). Its
anti-collapse rests on architectural asymmetry (predictor + stop-grad) + a bolted-on VICReg
variance hinge. This target has NO external entropy anchor -- it co-adapts with the student, which
opens a degenerate constant fixed point. CITED (SimSiam 2011.10566; BYOL 2011.10944; CMU ECCV22
collapse analysis; Tian et al. ICML21): collapse-avoidance here is an ARCHITECTURAL TRICK, and it
is empirically FRAGILE at small model/batch scale -- "EMA instability with very few parameters,
where the target network cannot diverge meaningfully from the online network." That is EXACTLY our
regime, and exactly why the harder causal arm collapses while the easier bidirectional arm (more
context per position) survives at the same budget.

## THE BIOLOGY (why cortex does NOT collapse) -- ESTABLISHED
- Cortical predictive coding (Rao & Ballard 1999; Friston free-energy, Nat Rev Neurosci 2010; V1
  JNeurosci 2010): each level predicts the activity of the level BELOW, grounding out in REAL
  sensory input; only residual prediction ERROR propagates up. The target is ALWAYS an
  externally-grounded signal with its OWN independent entropy -- NEVER a self-distilled/EMA copy of
  the predicting unit. No cortical model uses a self-copy teacher.
- The brain's anti-collapse is STRUCTURAL, not a hinge loss: lateral inhibition performs
  DECORRELATION (Barlow redundancy-reduction; Olshausen & Field 1996), and SPARSE coding / k-WTA
  competition structurally forbids all units collapsing to one value (arXiv:1409.2752). Higher
  sparseness <-> more decorrelated responses (ESTABLISHED V1 finding).

## THE CONVERGENCE (the key insight)
The MORE brain-faithful choice is ALSO the MORE collapse-robust one: predict a REAL external target
(cortical predictive coding) instead of a self-copy. A constant output can trivially match a
self-copy target that collapses with it, but CANNOT minimize error against a varying,
information-rich real target (cross-entropy/regression 101). So switching to a real target removes
the collapse CAUSE rather than fighting the SYMPTOM with more budget/regularization.

## RANKED RECOMMENDATION (minimal-change first)

**RANK 1 (TOP PICK) -- predict a REAL target: regression-to-next-token-embedding.**
- CHANGE (one axis): replace the EMA-latent target with the ACTUAL next token's own input
  embedding as the regression target (a real, data-determined target with real entropy). Keep the
  causal mask, keep the d_model->d_model head (STILL OOM-safe -- no [B,L,vocab] logits). Remove the
  EMA target + self-distillation loop. CITED@ arXiv:1902.11269 (continuous-output / regress-to-
  embedding, "Efficient Contextual Representation Learning Without Softmax Layer") = ESTABLISHED,
  memory-cheap, sidesteps vocab-size OOM entirely.
- BRAIN-FIDELITY: HIGH -- this IS cortical predictive coding (predict the real next signal, learn
  by error), not a self-copy.
- STABILITY: collapse-proof by construction at small scale (no co-adapting EMA loop).
- COST: minimal one-axis change, same arch/budget.
- WEAKEST LINK: the next-token INPUT embedding is itself learned (mildly self-referential). Fully-
  external fallback = predict token IDENTITY via sampled/adaptive softmax (CITED@ 2203.16868,
  standard, memory-cheap) -- a fully external target if regress-to-embedding still drifts.
- P_deflated(real-target more collapse-robust at our scale) ~0.7 (REASONED from first principles +
  SSL-collapse literature framing; not directly tested at our causal small scale).

**RANK 2 (cheapest control, bundle it) -- drop EMA, keep stop-gradient (SimSiam).**
- One-line change: remove the momentum/EMA encoder; stop-grad on a shared encoder. CITED@ SimSiam
  2011.10566 ESTABLISHED: stop-grad ALONE prevents collapse; EMA is a throughput convenience, NOT
  the load-bearing anti-collapse ingredient -- and it is the small-scale fragility source. Weaker
  on brain-fidelity (still self-distillation), but near-zero cost => run as a control arm to
  isolate "is EMA the culprit."

**RANK 3 (brain-faithful anti-collapse, complementary) -- decorrelation instead of the VICReg
variance hinge. NOW CITED (3rd scan landed).**
- METHOD-COMPARISON SCAN (CITED, small-batch collapse-robustness, most->least robust): (1) Barlow
  Twins -- CITED/ESTABLISHED, "does not rely on batch size"; ablation shows the off-diagonal
  redundancy term is a STRUCTURAL anti-collapse mechanism; AND the MOST brain-faithful of the five
  (named for Horace Barlow's redundancy-reduction = the lateral-inhibition analog). (2) VICReg --
  variance-hinge ALONE is a REASONED weak point at small batch (noisier std estimate -> weaker
  repulsion; the paper itself borrows Barlow's covariance term to patch it) = EXACTLY our fragile
  recipe. (3) W-MSE/whitening -- strongest guarantee but MOST batch-size-hungry. (4) DINO --
  documented plateau at small model scale. (5) SimSiam -- small-scale behavior untested. => Barlow
  Twins is BOTH the most small-batch-robust AND the most brain-faithful; replace the VICReg variance
  hinge with it. Combine with Rank 1 = the full brain-faithful package: real target (signal) +
  Barlow decorrelation (structural anti-collapse).

## PROXY-LIMIT FINDING (iter-3, MEASURED, changes the strategic read)
The fixed voice-role probe on the EXISTING lite ckpts shows ARM_LPC_BIDIR = 0.000/0.000 and
ARM_RANDOM = 0.000/0.000 (BOTH fully inverted) vs the full-budget frozen MLM's 0.179/0.163. So at
the cheap lite budget the voice-invariant role-reading CAPABILITY does NOT emerge for ANY arm -- not
just the collapse-prone causal one. => the small proxy is at/below the budget where the target
capability appears at all, so it fundamentally cannot answer "does causal de-invert" via downstream
probe scores at this budget. The proxy's honest yield = the COLLAPSE/rep_std axis (bidir stable,
causal fragile) + this drill's mechanism diagnosis, NOT a downstream de-inversion number. Spec risk
#3 (insufficient scale) is biting: a clean downstream read needs the fuller build budget REGARDLESS
of objective.

## CAN-FAIL TEST (top pick)
Re-run the causal arm with Rank 1 (real-target regression), everything else at the SAME small
proxy budget that collapsed the EMA recipe (rep_std 0.0180). HARD-PASS: causal rep_std clears the
0.020 floor AND the voice-role probe shows the causal arm REDUCES the directional inversion vs the
bidirectional control (brain-metric: voice-invariant role reading). HARD-FAIL: still collapses
(rep_std < 0.020) with a real target => the collapse is scale/data, not the target framing, and the
fuller build budget is genuinely required. Bundle Rank 2 (drop-EMA) as a control arm to attribute.

## IMPLICATION
This SUPERSEDES the "just bump budget" iter-3 approach: instead of fighting the collapse with
compute, remove its cause with a more brain-faithful objective. It is also a design input for the
15h BUILD itself, not just the proxy -- the causal encoder should very plausibly predict a REAL
target, not a self-distilled latent. Recommend adopting Rank 1 for the encoder objective and
re-running the small proxy to confirm before the full build.

Weakest link overall: no source makes the exact cortex-vs-EMA collapse comparison explicitly (it is
a REASONED synthesis); and the real-target-at-our-causal-small-scale claim is an extrapolation, not
a measured result -- which is precisely what the can-fail test above settles cheaply.
