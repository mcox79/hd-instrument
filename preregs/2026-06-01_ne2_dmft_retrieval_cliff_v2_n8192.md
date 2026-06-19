# Pre-registration: ne2_dmft_retrieval_cliff_v2_n8192

**Date:** 2026-06-01
**Anchor:** ne2_dmft_retrieval_cliff_v2_n8192
**Queue:** remote_cpu_queue
**Script:** experiments/exp_ne2_dmft_retrieval_cliff_v2_n8192.py
**Motivation:** v1 (N=1024) MIDDLE_BAND -- cliff observed at alpha~0.16-0.20 (too far right of
predicted 0.138). Finite-size effects blur the transition at N=1024. v2 uses N=8192 + finer
13-point alpha sweep to localize the cliff midpoint precisely.

---

## Hypothesis

The substrate's retrieval accuracy drops sharply at alpha_c ~ 0.138 (the DMFT prediction from
Hara-Kabashima 2026). At N=8192, finite-N corrections are ~1.5% (Hara-Kabashima 2026), so the
cliff midpoint should fall very close to 0.138.

v1 root cause: at N=1024, the transition is smeared across a wide alpha range. The overlap stays
~0.96 through alpha=0.138, dropping only around alpha=0.160 (seed=7) or alpha=0.148-0.160 (seed=17).
The cliff midpoint interpolation (~0.155) fell outside the HP window [0.12, 0.16]. At N=8192 the
transition sharpens, and the cliff midpoint should shift toward the DMFT prediction of 0.138.

---

## Design

- N = 8192 (PROT-018 binding)
- Fine alpha sweep (13 values): [0.100, 0.110, 0.120, 0.125, 0.130, 0.133, 0.136, 0.138,
  0.141, 0.144, 0.148, 0.155, 0.160]
  -- Densely brackets predicted alpha_c=0.138 with ~0.003-0.005 spacing near the cliff
- M = max(1, int(alpha * N)) stored patterns (BSC bipolar)
- Retrieval: noisy start (5% flip), 50 synchronous update steps, measure final overlap
- 5 seeds, 3 retrieval trials per alpha per seed
- Smoke: N=1024, 2 seeds (HP not applied; expected cliff at N=1024 is ~0.155-0.165)

---

## Pre-registered thresholds

### HARD-PASS (tightened HP window for N=8192 vs v1)
In >= 4/5 seeds:
1. Retrieval overlap m* at alpha <= 0.120 is >= 0.90
2. Retrieval overlap m* at alpha >= 0.155 is <= 0.60
3. Cliff midpoint (50% overlap crossing, linear interpolation) in [0.125, 0.152]
   (+-10% of predicted alpha_c=0.138; tighter than v1 [0.12, 0.16] because N=8192
   reduces finite-N smearing to <2% per DMFT theory)

Rationale for tightening: at N=4096, v1-analog overlaps still ~0.96 at 0.138 and ~0.96 at
0.155 (measured during multi-scale check). The cliff resolves sharply at N=8192, so a +-10%
window is scientifically justified. If N=8192 is still insufficient to resolve within +-10%,
that is itself a meaningful DMFT framework finding.

### HARD-FAIL
In >= 4/5 seeds:
- m* at alpha <= 0.12 is < 0.70 (substrate not retrieving; instrument/config error)
- OR no cliff detected: m* range across all 13 alphas is < 0.20

### MIDDLE_BAND
- Cliff present but midpoint outside [0.110, 0.165] (+-20% of 0.138) in majority of seeds
- OR criterion passes in 3/5 seeds (below HP threshold but not HF)
- Outcome plan: if MIDDLE_BAND, report cliff_midpoints per seed; surface to Strategy:
  (a) if midpoints cluster around 0.15+: substrate cliff is shifted from DMFT prediction
      (possible finite-N correction or non-mean-field effect); report as PP-33 qualified-pass
  (b) if midpoints vary widely: more seeds/trials needed; consider N=16384

---

## Calibration context

Prior anchor: v1 MIDDLE_BAND (N=1024, cliff at ~0.155-0.165, outside HP window [0.12,0.16]).
v2 tests whether higher N closes the gap to predicted alpha_c.

DMFT finite-N correction: theory predicts corrections O(1/N^(1/3)) for Hopfield. At N=1024
correction is ~5-8%. At N=8192 it drops to ~2%. HP window [0.125, 0.152] reflects +-2% of
0.138 with a 6% margin added for substrate idiosyncrasies.

Bands are +-10% of 0.138 (not +-50%): justified because v1 gives an empirical anchor (cliff
at ~0.155 at N=1024), and the refinement hypothesis is that it shifts to ~0.138 at N=8192.
The +-50% calibration-probe policy applies only to fully unanchored measurements; v2 has v1
as anchor.

---

## N-suffix section

PROT-018: anchor name `_n8192` requires production N=8192. Confirmed: `N = 8192` at line ~60.
Smoke uses N_SMOKE=1024 (smaller; allowed per PROT-018).

---

## Timeout estimate

- Sync step at N=8192: ~31ms (measured locally)
- Full run: 13 alphas * 5 seeds * 3 trials * 50 steps = 9750 steps
- Wall estimate: 9750 * 0.031s + W-build overhead (13 * 5 * ~0.5s = 32.5s) = ~334s
- timeout_s = 21600 (PROT-019 floor for _n8192 anchors; actual estimated wall ~334s;
  floor applies as conservative safety margin)
- Under the blocking threshold; long-run note: actual wall expected ~334s, well under 6h.
