# PRE-REG: stc_tag_and_capture_v2_two_phase_continual_learning

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** B3 (consolidation under saturation) - Wave 2 redesign
**Skunkworks audit:** notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3) Wave 2E
**Predecessor:** experiments/exp_stc_tag_and_capture_v1.py

## TRIGGERS v2 OVER v1

v1 single-phase readout (mean cosine over orthogonal bipolar prototypes) saturated all arms at 0.93-0.94 cor_score. The STC tag-mechanism never had room to demonstrate its load-bearing benefit (interference resistance during sequential learning).

Skunkworks Wave 2E exp_dev recommendation: 2-phase continual-learning rewrite where STC's benefit emerges as PROTECTION of an OLD pattern against NEW interference, not as raw acquisition.

Bonus fix: v1 had `tag_fraction=0.535` (THETA_TAG_PCT=90 + direction-novelty rule gave ~half-of-W). v2 tightens to THETA_TAG_PCT=92.0 -> ~8% sparse (in [0.05, 0.15] selectivity band).

## HYPOTHESIS

Phase 1: all arms write pattern A; STC tags ~8% of synapses, captures tagged into W_slow.
Phase 2: all arms write pattern B (interference). For STC arms, A's captured-into-W_slow synapses are PROTECTED (unprotected_mask = W_slow==0 enforces B writes only go to A-untouched entries).
- BASELINE: B's writes overwrite W_slow globally -> A is forgotten
- STC: B's tagged writes preserve A's captured synapses -> A is preserved

DISCRIMINATOR: `STC.recall_A_after - BASELINE.recall_A_after >= 0.30`
Density control: RANDOM_TAG_MATCHED has same tag density but random selection. If RANDOM == STC, density was the lever (not selection).

## ARMS (4)

1. ARM_BASELINE_NO_STC -- Hebbian + global capture; expected to forget A under B
2. ARM_STC_TAGGED -- PRIMARY: tag-based selective capture; protects W_slow
3. ARM_RANDOM_TAG_MATCHED -- same tag density as STC, random selection
4. ARM_DIAG_STC_DECAY -- STC with tag decay (verify decay doesn't break protection)

## PRE-REG BANDS

**HARD_PASS:**
- STC.recall_A_after - BASELINE.recall_A_after >= 0.30 (preservation lift)
- AND STC.recall_A_after >= 0.50 (A actually preserved)
- AND STC.recall_B_after >= 0.40 (B still acquired, not just A-locked)
- AND BASELINE.recall_A_after < 0.30 (interference regime real)
- AND STC.recall_A_after - RANDOM_TAG.recall_A_after >= 0.10 (selection load-bearing)
- AND tag_fraction in [0.05, 0.15] (sparse selective)
- AND cv across seeds < 0.10 (full only)

**MIDDLE_BAND:**
- A-preservation lift in [0.15, 0.30) OR tag-band miss but mechanism trending right

**HARD_FAIL:**
- BASELINE.recall_A_after > 0.30 (interference regime broken; B didn't overwrite A)
- OR STC.recall_A_after <= BASELINE.recall_A_after (STC doesn't protect)
- OR STC.recall_A_after <= RANDOM_TAG.recall_A_after (tag selection irrelevant)
- OR tag_fraction outside [0.02, 0.50] (over/under-tagged)
- OR cardinality breach

## REGIME

N_DIM=2048 (full) / 1024 (smoke)
N_CAT=20 (full) / 10 (smoke) -- background distractor prototypes for orthogonality
N_NOISY_VARIANTS=10 (full) / 5 (smoke) -- noisy training samples of A and B
PROTO_NOISE=0.85
THETA_TAG_PCT=92.0 (~8% tag fraction)
J_CAPTURE=10 (full) / 5 (smoke); K_TAG_DECAY=5 (full) / 3 (smoke)
ETA_FAST=1.0, ETA_CAPTURE=0.20

Seeds: full=[11,13,19,23,29]; smoke=[11,13].

## CARDINALITY_OK

EXPECTED_N_UNITS = n_seeds * 4 arms.
Full=20; smoke=8.

## FAIRNESS (META_RULE_AA)

- All arms read SAME SURFACE: mean cosine of W_total @ noisy_query against target_prototype
- Phase 1 / Phase 2 split applied identically across all arms
- RANDOM_TAG_MATCHED is the discriminator control: same density, different selection
- Smoke selftest verifies tag fraction in [0.02, 0.50] band

## DISPATCH

Queue: remote_cpu_queue (~3 CPU-hr full at N=2048).
Timeout: 10800s.

## EXPECTED OUTCOMES

- HARD_PASS: STC tag-and-capture mechanism load-bearing for continual learning
- HARD_FAIL via baseline doesn't forget: regime mismatched (need stronger interference)
- HARD_FAIL via RANDOM>=STC: density was the lever, selection irrelevant
- HARD_FAIL via STC<=BASELINE: protection mechanism doesn't work in our substrate
