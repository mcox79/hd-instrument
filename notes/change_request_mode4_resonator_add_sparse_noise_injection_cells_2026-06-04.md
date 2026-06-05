# Change Request -- Mode 4 resonator falsifier: add sparse + noise-injection cells

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Add 2 cells to Mode 4 resonator falsifier testing sparse-resonator + noise-injection extensions (per resonator capacity 2x drill empirical anchors)

---

## Status check requested

- [ ] Has Mode 4 resonator falsifier engineering started?
- [ ] If yes: can 2 new cells be added before dispatch?

Expected: Mode 4 engineering not yet started (routed 2026-06-04 cycle ~15:00). Change-request applies during scaffold work.

---

## Capability question (additional cells)

The original Mode 4 falsifier (routing_mode4_resonator_falsifier_test_2026-06-04.md) tests baseline Frady-Sommer 2020 dense resonator at K=5 N=4096 with >=85% recovery within 50 iter. Per today's resonator capacity 2x drill (2026-06-04), substrate has TWO published extensions:

- **Sparse resonator** (arXiv:2404.19126): K=26 letters empirically demonstrated at N=5000
- **Noise-injection** (arXiv:2412.00354): extends K_max ~50x for free

These are the AGGRESSIVE capacity range tests. If they HP at substrate-class N=4096, substrate's Mode 4 reaches K=20-50 factor recovery (vs baseline K=5).

---

## Pre-reg HP/MID/HF for new cells

**Cell R4: Sparse resonator at K=20 N=4096 V=512 codebook**

- Architecture: sparse f=0.05 codebook + resonator coordinate-descent
- 50 iter max; 5 seeds
- **HARD-PASS:** >= 70% recovery (relaxed from baseline 85% due to harder K=20 task) across 4/5 seeds
- **MIDDLE:** 40-70% recovery
- **HARD-FAIL:** < 40% recovery

P_deflated for HP: ~0.40 (lit anchor arXiv:2404.19126; novel-synthesis cap applied)

**Cell R5: Noise-injection resonator at K=50 N=4096 V=512 codebook**

- Architecture: dense codebook + noise-injection (per arXiv:2412.00354 protocol)
- 100 iter max (longer than baseline; K=50 needs more iterations)
- 5 seeds
- **HARD-PASS:** >= 60% recovery across 4/5 seeds
- **MIDDLE:** 30-60% recovery
- **HARD-FAIL:** < 30% recovery

P_deflated for HP: ~0.30 (50x extension is more aggressive; novel-synthesis cap)

## Engineering scope addition

~2-3h:
- Sparse codebook generator at f=0.05 (~30 min)
- Sparse resonator update rule (sparse-aware unbind + cleanup; ~1h)
- Noise-injection mechanism (Gaussian noise added per iteration; ~30 min)
- Increased iteration budget + convergence monitor for K=50 (~30 min)

Reuses Mode 4 baseline scaffold substantially.

## Wall-time addition

Cell R4 at K=20: ~1-2 min per seed (slower than K=5 baseline; more iterations)
Cell R5 at K=50: ~3-5 min per seed (100 iter max; slower convergence)
Total addition to Mode 4 falsifier: +20-40 min for 10 measurements

## Strategic outcome

### If R4 HP (sparse K=20 validates at substrate-class N=4096)

- arXiv:2404.19126 sparse resonator extends to substrate-class
- Substrate Mode 4 reaches K=20+ factor recovery (4x baseline)
- Cap_map: NEW sub-property for sparse-resonator extension
- Product narrative: substrate handles compositional retrieval at K=20+ scale

### If R5 HP (noise-injection K=50 validates)

- arXiv:2412.00354 50x extension validates at substrate-class
- Substrate Mode 4 reaches K=50+ factor recovery (10x baseline)
- MAJOR finding: aggressive capacity extension is real
- Product narrative: substrate handles compositional retrieval at K=50+ scale

### If R4 + R5 HF (extensions don't scale to substrate-class)

- Published extensions don't extend to substrate-class N=4096
- Substrate Mode 4 capped near baseline (K=5-10)
- Inform: larger N needed OR different architectural variants

---

## What this is (plain language)

Mode 4 resonator falsifier as routed tests baseline Frady-Sommer 2020 at K=5 N=4096. Today's resonator capacity drill identified two published extensions that should give substantial K_max boost:

- Sparse resonator: K=26 letters at N=5000 published empirical
- Noise-injection: 50x free extension (K=5 -> K=250+)

These are SUBSTRATE'S MOST AGGRESSIVE empirical capacity claims for Mode 4. Tests at K=20 (sparse) + K=50 (noise-injection) directly validate the resonator capacity drill's predictions.

Combined: baseline + sparse + noise-injection cells characterize substrate's full Mode 4 capacity range at substrate-class N.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-change-request-protocol]]: status check first; applies during scaffold work
- Per [[feedback-no-padding-experiments]]: cells discriminate substrate's full Mode 4 capacity range
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: R4 uses `_sparse_k20_v1`; R5 uses `_noise_inj_k50_v1`
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** add Cells R4 + R5 to Mode 4 resonator falsifier scaffold. ~2-3h additional engineering; +20-40 min CPU wall. Verdict drives substrate's Mode 4 aggressive capacity validation.
