# Research drill 3x: surprise-driven gating B3b RECAPTURE (lift MIDDLE/HF to VALIDATED grade)

Date: 2026-06-17
Topic: surprise-gating-B3b-recapture
Mode: 3x DEEP DRILL (3 parallel Sonnet lit-scans + Opus synthesis)
Cap_map row: B3b surprise-gating (cell MIDDLE/HF verdict)

## (a) HEADLINE

Surprise-gating ceilings in B3b are likely driven by ONE OR MORE of three named failure modes from the MoE/curiosity literature: (1) router/specialization COLLAPSE (Chi 2022 XMoE; Zoph 2022 ST-MoE), (2) raw-softmax MIS-CALIBRATION conflating aleatoric + epistemic surprise (Guo 2017; Kendall-Gal 2017; Depeweg 2018), (3) NOISY-TV trap where the gate chases irreducible noise (Burda 2018b RND; Savinov 2019 reachability). All three have NAMED, CHEAP interventions; the bet is that the MIDDLE/HF verdict in B3b is one of these three, not a fundamental surprise-gating ceiling.

## (b) Cheap decisive test

Three-arm ablation on existing B3b cell, each ~2-4 hours laptop or 1 cell remote:

ARM 1 (COLLAPSE diagnostic): measure router-logit norm + per-expert token-share entropy across last 100 batches of the failing run. If max-share > 0.40 OR token-share entropy < 0.7 * uniform: COLLAPSE confirmed; LIFT = L2-normalize hidden state + low-dim projection before routing (Chi 2022) + add router z-loss (Zoph 2022; coef 1e-3).

ARM 2 (MIS-CALIBRATION diagnostic): on held-out, compute ECE of the surprise-gate score (binned by quantile) vs the true gating-relevant outcome. If ECE > 0.05: MIS-CAL confirmed; LIFT = temperature-scale the gate (1-parameter fit on val), then re-evaluate. Cheap because no retrain.

ARM 3 (NOISY-TV diagnostic): inject 5% irreducible-noise samples into the gating distribution and measure gate-firing rate on noise vs signal. If gate fires on noise at >= signal rate: NOISY-TV confirmed; LIFT = swap the surprise estimator from forward-error (ICM-style) to frozen-target distillation (RND, Burda 2018b) which converges to 0 on aleatoric states.

## (c) Falsifiable predictions

HARD-PASS thresholds (any ONE arm lifts B3b cell to VALIDATED grade):
- ARM 1 LIFT (L2 + z-loss + low-dim route): expected +8 to +15 pp on the B3b cell metric vs MIDDLE baseline. HARD-PASS = >= +6 pp, p<0.05, n>=5 seeds.
- ARM 2 LIFT (temperature scaling, one parameter): expected +3 to +8 pp; cheap-no-retrain. HARD-PASS = >= +4 pp, p<0.05.
- ARM 3 LIFT (forward-error -> RND distillation): expected +5 to +12 pp IF NOISY-TV is the dominant failure. HARD-PASS = >= +5 pp, p<0.05.

HARD-FAIL thresholds (B3b RECAPTURE refuted; cell goes structural-closure):
- ALL THREE arms deliver < +3 pp combined (i.e. stacked LIFT < +3 pp): the MIDDLE/HF verdict is NOT one of the three named failure modes; B3b is hitting a substrate-novel ceiling not addressed by the public MoE/curiosity literature.
- Router diagnostics show no collapse (max-share < 0.30, entropy near uniform) AND ECE < 0.03 AND gate fires on noise at < 0.5x signal rate: all three named modes refuted; cap_map B3b -> structural-closure with rescue dispatch to a DIFFERENT field per Trigger D.

Calibration penalty applied: per [[feedback-lit-scan-calibration-penalty]], B3b is in an uncharted regime (hyperdimensional substrate, not transformer-MoE). P_naive = 0.65 that one named lift applies. Deflated P_deflated = 0.45 (deflation 0.20; cap-novel-synthesis 0.50 not binding because this is recombination of known lifts, not novel derivation).

## (d) Cross-thread synthesis

ANGLE 1 (surprise-as-residual): predictive coding (Rao-Ballard 1999; Friston 2010), IB (Alemi 2016), RIMs (Goyal 2019), MoE routing (Roller 2021 hash; Lewis 2021 BASE), curiosity (Pathak 2017 ICM; Burda 2018 RND) all operationalize surprise as a prediction-vs-observation residual or compression residual, and route capacity to highest-residual signal. The substrate B3b gate is in this family.

ANGLE 2 (gating spectrum): Shazeer 2017 (top-k hard), Fedus 2022 (Switch top-1), Roller 2021 (hash, fixed), Zhou 2022 (expert-choice flip), Puigcerver 2023 (Soft MoE), Raposo 2024 (Mixture-of-Depths), Graves 2016 (ACT), Jang 2017 (Gumbel-Softmax). Load-balance is the dominant tradeoff axis. Soft gates avoid collapse but lose conditional-compute savings; hard gates need aux losses; expert-choice / hash sidestep balance. B3b probably uses hard top-k -- soft mixing (Puigcerver 2023) is a 4th candidate LIFT if ARM 1 partial.

ANGLE 3 (named ceilings + lifts): Guo 2017 temp-scaling, Kendall-Gal 2017 aleatoric/epistemic split, Depeweg 2018 latent-variable BNN decomposition, Burda 2018ab curiosity-scale + RND, Savinov 2019 episodic reachability, Zoph 2022 ST-MoE (z-loss + capacity factor), Chi 2022 XMoE (L2-norm + low-dim route). Three named failure modes have NAMED interventions.

Cross-thread synthesis with prior B3b drills: this is the FIRST drill explicitly targeting RECAPTURE via named-failure-mode triage rather than searching for a new gating mechanism. The 3-arm diagnostic separates "fix what you have" from "swap mechanism" -- if all three arms hard-fail, dispatch a rescue drill into an ADJACENT field (modern-Hopfield surprise-energy; spin-glass non-self-averaging q(x) overlap as alternative gating prior) per Trigger D.

## (e) Substrate-product implications

If ANY arm hits HARD-PASS: B3b cap_map row VALIDATED, surprise-driven gating becomes a load-bearing primitive for product-tier conditional-compute (cheaper inference, longer effective context, expert-specialization for domain-shift retention). Direct product-relevant: same lift mechanism (L2-norm + z-loss + epistemic-only gating) generalizes to any substrate row that uses confidence-gated routing.

If ALL arms HARD-FAIL: B3b -> structural closure; product positioning must NOT claim surprise-driven gating as a primitive; downgrade to "explored, structural ceiling at <named regime>"; honest negative result -- valuable per cross-domain probe discipline.

Either way the drill closes the cell with a NAMED outcome (validated-via-known-lift OR structural-closure-with-rescue-dispatch) rather than persistent MIDDLE/HF status.

## (f) Citations (verified count = 24)

Angle 1 (8): Rao-Ballard 1999; Friston 2010; Alemi 2016; Goyal 2019 RIMs; Roller 2021 Hash Layers; Lewis 2021 BASE Layers; Pathak 2017 ICM; Burda 2018a RND.

Angle 2 (8): Shazeer 2017 sparsely-gated MoE; Fedus 2022 Switch Transformer; Roller 2021 Hash Layers; Zhou 2022 expert-choice routing; Puigcerver 2023 Soft MoE; Raposo 2024 Mixture-of-Depths; Graves 2016 ACT; Jang 2017 Gumbel-Softmax.

Angle 3 (8): Guo 2017 temperature scaling; Kendall-Gal 2017 aleatoric/epistemic; Depeweg 2018 BNN decomposition; Burda 2018a large-scale curiosity; Burda 2018b RND; Savinov 2019 episodic reachability; Zoph 2022 ST-MoE (z-loss + capacity factor); Chi 2022 XMoE (representation collapse + L2-norm low-dim route).

(Roller 2021 and Burda 2018 appear in two angles; unique-paper count = 22.)

## Method-contingent framing (per [[feedback-measured-bounds-are-method-config-contingent-not-fundamental]])

The HARD-PASS/HARD-FAIL above are for the CURRENT B3b method/config. They do NOT prove "surprise-gating cannot work for the substrate"; they prove "for this method/config + these 3 named lifts, RECAPTURE succeeds or fails." Extension via softer-gate (Puigcerver Soft MoE), or non-residual surprise priors (modern-Hopfield energy, spin-glass q(x) overlap) UNTESTED here.

## Next-drill candidate (if all arms HF)

`modern-hopfield` (Tier-1 fruit-bearing, surprise-energy as alternative gating prior; Krotov-Hopfield dense Hopfield exponential capacity gives a non-residual surprise definition that may avoid all three named failure modes).
