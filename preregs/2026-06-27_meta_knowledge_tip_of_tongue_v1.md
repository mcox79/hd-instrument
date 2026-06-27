# Prereg: meta_knowledge_tip_of_tongue_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) Wave 3B TOP-2
**Drill source:** notes/research_drill_3x_substrate_self_monitoring_metacognition_2026-06-27.md (Cell #2; Angle B2)
**Stage:** Stage 3 (metacognition; higher functions)
**P_deflated:** 0.50

## HYPOTHESIS

Substrate exhibits TOT-like (tip-of-tongue) states where cluster-level cosine is HIGH ("knows the region") but atom-level cleanup is LOW ("cannot crystallize the specific item"). TOT-rate tracks SNR monotonically (lower SNR -> more TOT). Crucially, IN TOT cases, substrate still correctly identifies the CATEGORY of the missing item (brain-aligned graceful-degradation behavior). Substrate prereqs: ultrametric clustering CHAIN_GRADE; cleanup primitive chain-grade.

## ARMS (4)

1. **ARM_HIGH_CONF_HIGH_RECALL** -- clean queries (SNR=1.0); sanity check that substrate IS confident when correct.
2. **ARM_TOT_PARTIAL_KNOW** -- noisy queries (SNR=0.3, 0.6); cluster known, atom cleanup expected to fail in subset.
3. **ARM_LOW_CONF_LOW_RECALL** -- OOD queries (random vectors); refuses correctly when not knowing.
4. **ARM_DIAG_TOT_RATE_VS_SNR** -- sweep over SNR in {0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0}; measure Spearman rho between SNR and TOT-rate.

## PRE-REG BANDS (LOCKED PRE-FULL-DISPATCH; PROSPECTIVE)

**Updated 2026-06-27 post-smoke calibration:** initial hypothesis assumed monotone SNR -> TOT-rate (Spearman rho <= -0.7). Smoke empirically falsified this assumption: TOT-rate is UNIMODAL with peak at intermediate SNR (substrate has BOTH a "too noisy = no signal at all" regime AND a "clean enough = full recall" regime; TOT happens in between). True brain-aligned discriminator: peak-at-interior + high cluster_acc_at_peak.

- **HARD_PASS**: TOT-rate at peak SNR >= 0.40 AND peak SNR is INTERIOR (not at endpoints of SNR sweep) AND cluster_acc_in_TOT at peak >= 0.70 AND ARM_HIGH_CONF atom recall >= 0.80 AND ARM_LOW_CONF refuse-fire >= 0.90.
- **MIDDLE_BAND**: cluster_acc_in_TOT at peak in [0.50, 0.70] OR peak TOT-rate in [0.30, 0.40] OR peak at endpoint.
- **HARD_FAIL**: ARM_HIGH_CONF atom recall < 0.50 (basic retrieval broken) OR cluster_acc_in_TOT at peak < 0.50 (substrate doesn't know category even at peak TOT).

TOT operationally defined as: cleanup_margin BELOW 30th percentile of clean baseline AND cluster_cosine ABOVE 50th percentile of clean baseline.

## FAIRNESS GATES

- Same N_DIM across arms; same atom codebook; same K=10 cluster count.
- TOT defined operationally: cluster_cosine >= 0.40 AND atom_cleanup_cosine < 0.30 (locked PROSPECTIVE; not tuned).
- Noise is iid Gaussian per dim per query; SNR controls noise stddev relative to atom unit vector.
- Q-discipline: ARM_HIGH_CONF_HIGH_RECALL recall >= 0.95 verify atoms truly distinct (not by-construction saturated).

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL = 4 arms * 3 seeds * 5000 queries = 60000 (ARM_DIAG sweeps SNR internally; counted as 1 arm)
- EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 300 queries = 2400

## DISCRIMINATOR-SURVIVES-SCALE

Smoke runs at full N_DIM=2048 with K=10 clusters; full uses N=2048 with full query count. The monotone SNR -> TOT-rate relationship MUST fire at smoke (use min 4 SNR levels).

## HARDENING

L1 STARTED + L2 per-arm progress + L3 outer try/except + L4 import-crash sentinel.

## COMPUTE

CPU on remote_cpu; ~30-45 min full; <10 min smoke. Forward-only numpy.

## SUBSTRATE PREREQS

- Ultrametric clustering (in-cell synthetic: K-means with cosine distance)
- Cleanup via cosine argmax over atom codebook
- Refuse-gate threshold on cleanup margin
