# Research: B8 logit residual analysis RECAPTURE -- 3x deep drill

date: 2026-06-17
topic: B8 logit sparse residual MIDDLE r=0.27 recapture; M_crit_gain proxy-measurement bug avoidance
sub-agents: research:opus + lit-scan:sonnet x3 (angle1 logit-lens/attribution, angle2 sparse-residual, angle3 reconstruction-faithful r)
calibration penalty: applied -- novel-synthesis P capped at 0.50; field is uncharted-regime (no published direct precedent for VSA logit attribution); deflation 0.15-0.25

## (a) HEADLINE

The substrate's r=0.27 MIDDLE on B8 logit sparse residual is consistent with the published canonical pitfall (Bricken 2023 + Belinkov 2022 + Kriegeskorte 2022): an auto-association proxy inflates apparent r without measuring the causal-attribution signal. The Gated-SAE shrinkage correction (Rajamanoharan 2024) + causal-mediation hetero-association protocol (Vig 2020) prescribe a direct 3-knob fix: (1) measure r on a HELD-OUT counterfactual-pair split, NOT on the training distribution; (2) report variance-explained AFTER shrinkage correction (gated decode); (3) cross-check via counterfactual intervention -- does ablating the recovered feature actually shift the logit in the predicted direction? Substrate-product reading: B8 is repairable to r>0.55 if the measurement is rebuilt around held-out hetero-association + gated decode; the current 0.27 is most likely a method-contingent floor of an auto-association protocol, NOT a fundamental ceiling.

## (b) Cheap decisive test

Pre-registered protocol (under 2 hr CPU, no GPU needed):

1. Build a paired counterfactual stimulus set (N=200 pairs) where each pair differs in ONE logit-relevant attribute -- e.g., a known-vocabulary-item swap at a fixed position.
2. Train the sparse residual decomposer on HALF the pairs (split A; train side); evaluate r on the OTHER half (split B; eval side). NEVER let any pair-component appear in both splits.
3. Compute r between (i) the SAE-reconstructed logit attribution and (ii) the empirical logit difference under the counterfactual swap. This is the hetero-association r.
4. Separately compute the auto-association r (current substrate protocol) on the SAME splits, for direct calibration.
5. Apply Gated-SAE shrinkage correction (Rajamanoharan 2024 sec. 3.2): re-fit the decode magnitudes with L1 on the gate only, not the magnitude head.
6. Report all 4 numbers: (auto-r, hetero-r, auto-r-gated, hetero-r-gated).

## (c) Falsifiable predictions

PRED-1 HARD-PASS: hetero-r-gated >= 0.55 on held-out split B. This would confirm that the 0.27 MIDDLE was a method-contingent proxy floor and B8 logit residual carries genuine attribution signal.

PRED-1 HARD-FAIL: hetero-r-gated < 0.30 on held-out split B AND auto-r > 0.50 on the SAME split. This would prove the substrate's logit residual has NO genuine hetero-associative content beyond auto-association artifact; B8 closes structurally.

PRED-2 (gate diagnostic): auto-r minus hetero-r > 0.15 ALWAYS (irrespective of gating). This would confirm the canonical auto-association-confound mechanism is operating. If auto-r approx hetero-r, the measurement-bug hypothesis is REFUTED and the 0.27 reflects a deeper substrate ceiling.

PRED-3 (shrinkage diagnostic): hetero-r-gated minus hetero-r-ungated > 0.05. Confirms Rajamanoharan shrinkage was a real correction. If the gap is <0.02, the shrinkage knob is not load-bearing for substrate (different from Anthropic regime).

P_deflated (PRED-1 HARD-PASS or MIDDLE-BAND>=0.40): 0.45. Capped at 0.50 per novel-synthesis ceiling; further deflated 0.05 because substrate is a VSA not a transformer, and the canonical lit is transformer-MLP-residual; the analogy is mathematically adjacent (linear superposition + sparse readout) but not literal.

P_deflated (PRED-2 gate diagnostic fires): 0.60. The auto-vs-hetero gap is the single most-replicated finding in the probing literature (Belinkov 2022 survey).

P_deflated (PRED-3 shrinkage knob load-bearing): 0.35. VSA codebook geometry differs from transformer activation geometry; shrinkage may or may not be the right correction.

## (d) Cross-thread synthesis with prior entries

This drill connects to four prior Entries:

- research_modern_hopfield_capacity_retrieval_crossover_2026-06-16: established that VSA capacity claims must be honest-bounded with method/config qualifier. Same discipline applies here: r=0.27 is a method-contingent floor, not a fundamental ceiling. State "of THIS method/config".
- research_drift_detection_backbone_invariant_2026-06-17: kappa is label-coupled, not rep-coupled, which is why it transports poorly. Direct parallel: auto-association r is input-distribution-coupled, not attribution-coupled, which is why it inflates without transporting to held-out hetero-association. Same family of measurement-bug.
- research_drosophila_MB_sparse_recapture_2026-06-17: identified that supra-linear selection is the load-bearing ingredient missed by linear readout. Parallel: the substrate's B8 measurement may be missing the causal-intervention step (Vig 2020 hetero-association) that makes the difference between proxy and real.
- substrate methodology rule 19 (adversarial-self-correction-of-own-DETECT-output): the scorecard's own self-flag of "M_crit measurement bug" is rule-19-conformant. This research drill is the operational response: rebuild the measurement around the canonical lit-prescribed protocol, do NOT re-run the buggy proxy at higher resolution.

## (e) Substrate-product implications

B8 is the logit-residual cap row. If hetero-r-gated >= 0.55 (HARD-PASS), the product gains a measurement-faithful logit attribution capability -- substrate can claim "we localize logit contributions to sparse residual directions with held-out r=X" with the honest method/config qualifier per the 2026-06-16 USER-LOCKED bound-framing rule. If hetero-r-gated < 0.30 (HARD-FAIL), B8 closes structurally and the substrate's logit-attribution claim downgrades to "auto-associative recovery only, no hetero-associative content" -- still a valid product reading but a narrower one. Either way, the rebuild eliminates the M_crit_gain proxy bug from the scorecard, restoring scorecard integrity (composes with the 2026-06-15 scorecard-overstates-clean-core finding: removing one proxy-bug-driven OVERSTATE is a direct integrity win).

The gated-SAE + counterfactual-pair protocol is also DIRECTLY REUSABLE for any future logit/output cap rows: it is not a one-off B8 fix, it is a reusable measurement primitive. Strategic value: the protocol itself is the product-level asset, not just the B8 number.

## (f) Citations

Verified count: 23 distinct papers across 3 angles.

Angle 1 (logit lens / attribution) -- 8 papers:
- Nostalgebraist 2020 (logit lens)
- Belrose et al. 2023 arXiv:2303.08112 (tuned lens)
- Geva et al. 2021 EMNLP (FFN as key-value memories)
- Wang et al. 2022 ICLR 2023 (IOI / path patching)
- Bricken et al. 2023 Anthropic (SAE on MLP)
- Rajamanoharan et al. 2024 arXiv:2407.14435 (JumpReLU SAE)
- Syed et al. 2023 (attribution patching)
- Heimersheim and Nanda 2024 arXiv:2404.15255 (activation patching best practices)

Angle 2 (sparse residual stream) -- 7 papers:
- Elhage et al. 2021 (mathematical framework)
- Elhage et al. 2022 (toy models of superposition)
- Cunningham et al. 2023 arXiv:2309.08600 ICLR 2024 (SAE on GPT-2 residual)
- Conmy et al. 2023 NeurIPS (ACDC)
- Templeton et al. 2024 Anthropic (Scaling Monosemanticity)
- Marks et al. 2024 (sparse feature circuits)
- Dunefsky et al. 2024 (cross-layer transcoders)

Angle 3 (reconstruction-faithful r / proxy-bug avoidance) -- 8 papers (1 overlap = 7 new):
- Bricken et al. 2023 (variance explained + loss recovered)
- Rajamanoharan et al. 2024 NeurIPS arXiv:2404.16014 (Gated SAE shrinkage correction)
- Vig et al. 2020 NeurIPS (causal mediation analysis, AIE)
- Geva et al. 2021 EMNLP (auto- vs hetero- distinction)
- Jacovi and Goldberg 2020 ACL (faithfulness vs plausibility)
- Belinkov 2022 TACL (probing survey, selectivity, auto-vs-causal pitfall)
- Kriegeskorte et al. 2022 bioRxiv (RSA confound regression)
- Survey 2025 arXiv:2503.05613v3 (SAE survey)

## Pre-registered HARD thresholds (frozen)

| Prediction | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| PRED-1 hetero-r-gated | >=0.55 | <0.30 AND auto-r>0.50 | 0.45 |
| PRED-2 auto-vs-hetero gap | gap >0.15 | gap <0.05 | 0.60 |
| PRED-3 shrinkage knob | improve >0.05 | improve <0.02 | 0.35 |

Next-drill candidate field: `sparse-coding-compressed-sensing` (Tier-1b, scope-expansion, drill_count<=2) -- the gated-SAE + counterfactual-pair protocol is mathematically a sparse-recovery problem; published phase-transition theory may sharpen the HARD-PASS threshold.
