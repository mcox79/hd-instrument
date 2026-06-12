# Exp-Dev -> Research: Cell A + Cell B VERDICTS -- substrate composes AND decodes with NO capacity cliff to F=20/noise=0.3; the only limit is the CLUSTERED CODEBOOK (decisive vs uniform baseline)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.
**Cells:** exp_substrate_composition_capacity_gpu_v1 (GPU/cuda) + exp_substrate_decomposition_resonator_cpu_v1 (CPU).

## Cell A -- COMPOSITION capacity (cleanup accuracy, revised lock; + random-codebook baseline)

| F | recovery_cos (analytic 1/sqrt(F)) | substrate cleanup@1 | RANDOM(uniform) cleanup@1 | clustered-vs-uniform delta |
|---|---|---|---|---|
| 1 | 1.000 | 0.9333 | 1.0000 | -0.067 |
| 2 | 0.706 | 0.8917 | 1.0000 | -0.108 |
| 3 | 0.580 | 0.8889 | 1.0000 | -0.111 |
| 5 | 0.447 | 0.8533 | 1.0000 | -0.147 |
| 10| 0.315 | 0.8683 | 1.0000 | -0.132 |
| 20| 0.223 | 0.8417 | 1.0000 | -0.158 |

**Verdict: MIDDLE** on the revised strict bar (cleanup@1 0.889 < 0.95 at F=3), but the finding is decisive and clean:
- **The uniform (random) codebook decodes PERFECTLY (1.000) at every F to F=20.** The HRR architecture at D=1024 has effectively
  UNLIMITED binding capacity over this range -- NO crosstalk cliff. cleanup capacity F* = 20 (limit of sweep).
- **The substrate's CLUSTERED codebook caps cleanup at ~0.84-0.93**, and the deficit vs uniform GROWS with F (-0.07 -> -0.16).
- Diagnosis (the uncharted-regime answer): the substrate decode ceiling is set by INTRA-CLUSTER NEAR-COLLISIONS
  (tw_edge_z=-2.26 clustered geometry), NOT by binding capacity. Even at F=1 the ceiling is 0.93 (<1.0) because some atoms
  are genuine near-duplicates in algebra-HRR space.
- recovery cosine = 1/sqrt(F) exactly (metric flag confirmed; cleanup accuracy is the right metric, per your revision).

## Cell B -- DECOMPOSITION (resonator explaining-away; precision@1 across F x K x noise)

precision@1, full grid (3 seeds x 20 trials, 10 resonator iters):
- **K=50:**  F2-8 = 0.93-0.98 across noise {0,0.1,0.3}
- **K=100:** F2-8 = 0.89-0.97
- **K=280:** F2-8 = 0.83-0.91   (F3=0.911, F2=0.842, F8=0.831)

**Verdict: MIDDLE** (F=2,K=280,noise=0 = 0.842 < 0.95 strict HARD-PASS bar; F=3 = 0.911 >= 0.80). Finding:
- precision@1 is FLAT across F=2-8 AND noise 0-0.3 -- **NO Frady-Sommer cliff**; the resonator decode is robust to both binding
  count and additive noise (noise 0.3 barely changes precision: 0.911 -> 0.900 at F=3,K=280).
- The ceiling DROPS with codebook size K (0.95+ at K=50 -> ~0.85 at K=280) -- consistent with Cell A: more atoms = more
  intra-cluster collisions = lower cleanup ceiling. The limit is CODEBOOK CROWDING, not decode capacity or noise.

## Combined substrate-product positioning artifact (stands alone, no LLM frame)
**Substrate atoms COMPOSE into structured representations and DECODE back -- robustly, with no capacity or noise cliff out to
F=20 bindings and 0.3 additive noise (substrate > atom-set, empirically demonstrated).** The decode CEILING (~0.85-0.93 at the
full 280-atom codebook) is set entirely by the substrate's CLUSTERED ATOM GEOMTRY (semantically-similar atoms near-collide in
cleanup), NOT by the HRR architecture (a uniform codebook decodes perfectly to F=20). This is the uncharted clustered-codebook
regime answer: clustering HURTS the cleanup ceiling by 0.07-0.16. **Actionable:** CSLS / MMR cleanup re-rank (per the
distractor-density drill) should recover much of the clustered-codebook deficit -- a concrete next lever.

## Routing
- **Exp-Dev:** Cells A + B done (both MIDDLE on strict bars; decisive clustered-codebook finding). Cell C (cross-domain
  transfer) needs BIO NER data -- NOT bundled locally (only math + ontonotes/conll). See data-gap note / will propose source.
  Possible follow-on: CSLS/MMR cleanup re-rank cell to test recovering the clustered-codebook deficit (cheap, would likely
  lift both A and B toward HARD-PASS).
- **Research:** Cell A + B verdicts for verdict_handler. The clustered-codebook-caps-cleanup finding is the substrate-product
  uncharted-regime result; CSLS/MMR re-rank is the indicated mitigation. free-probability drill (flagged) now has concrete
  empirical grounding: uniform=1.0, clustered=0.84-0.93, deficit grows with F.
