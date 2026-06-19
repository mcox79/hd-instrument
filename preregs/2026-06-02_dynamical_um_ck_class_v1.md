# Prereg: dynamical_um_ck_class_v1

**Date:** 2026-06-02
**Anchor:** dynamical_um_ck_class_v1
**Queue:** remote_cpu_queue
**Research source:** notes/research_ultrametricity_revival_consolidation_2026-06-01.md, Q-F1

## Scientific question

Does the substrate's existing Glauber dynamics exhibit dynamical 1-step ultrametricity
at the CK-class predicted value M_dyn in [0.85, 0.95], cleanly separable from the
static-UM-refuted value 0.583?

This is a DECISIVE test: if M_dyn >= 0.75, substrate's trajectory space IS ultrametric
(CK aging class), and the v324 static-UM=0.583 HARD_FAIL was a wrong-probe. v330
strategy decisions already established this framing; Q-F1 empirically confirms it for
the dynamical observable.

## Protocol

CK protocol (Castillo-Chamon-Cugliandolo 2002):
- Three time points t_1 < t_2 < t_3; R=200 replica pairs; quench from random init.
- C_ij = (1/N) * dot(s(t_i), s(t_j)) for each replica.
- Dynamical ratio per replica: C_13 / min(C_12, C_23).
- M_dyn = mean ratio over R replicas.
- Test at triplets: (8,64,512), (16,128,1024), (32,256,2048) [full].
- HARD_PASS if M_dyn >= HP in >= 2/3 triplets.

## Pre-registered thresholds

- **HARD_PASS:** M_dyn >= 0.75 in >= 2/3 triplets
- **HARD_FAIL:** M_dyn <= 0.65 in >= 2/3 triplets
- **MIDDLE_BAND:** 0.65 < M_dyn < 0.75 (escalate to FULL with larger R)

These are calibration probe bands (first empirical M_dyn measurement for this
substrate). CK theory predicts M_dyn in [0.85, 0.95] from Iniguez 1999 3D EA.
Bands set within +-15% of theoretical center 0.88. Separation from static-UM=0.583
is the key discrimination.

## Smoke result

- N=512, R=100, 1 seed, 2 triplets
- M_dyn triplet (8,64,512) = 0.8928
- M_dyn triplet (16,128,1024) = 0.9565
- global_mean_M_dyn = 0.9246 HARD_PASS (both triplets pass)
- Wall: 371.8s
- Verdict: HARD_PASS decisive (well above HP=0.75)
- Effect size: observed 0.9246 vs HP=0.75 => margin = 0.17, >> 0.15 walk-back threshold.
  No walk-back needed.

## Multi-scale note

N is not the primary sweep axis (sweep = triplet choice). Multi-scale smoke not
required per role contract. Smoke at N=512 passes HARD_PASS decisively.

## N-suffix declaration

No _nN suffix; production N=1024 per PROT-018 rule 3. N=1024, rationale: CK
protocol is CPU-bound at R=200 replica pairs; 1024 gives ample statistics with
3 seeds; main scaling axis is R and T_MAX, not N.

## Timeout estimate

- smoke_wall_s = 371.8
- FULL_N/smoke_N = 2 (1024/512)
- FULL_seeds/smoke_seeds = 3 (3/1)
- scaling_exp = 1.5 (Glauber: N ops per step, R replicas per seed)
- timeout = ceil(1.5 * 371.8 * 2^1.5 * 3) = ceil(1.5 * 371.8 * 2.828 * 3) = ceil(4741) = 4800s
- 4800s < 7200s (no long-run flag required)

## Cap_map impact

- v330 PP-33 framework-class row at 0.50-0.65 (Q19 RESCUE-SUCCESS lift)
- Q-F1 HARD_PASS: lift PP-33 further to 0.60-0.75 range; confirm CK dynamical-class
- Q-F1 HARD_FAIL: reopen static-RSB shelf; major strategic reassessment
- New row candidate: dynamical-1-step-ultrametricity (currently 0.40 P_deflated)
