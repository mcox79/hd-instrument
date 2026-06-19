# Exp-Dev -> Research: HP-7 core design VALIDATED (beta* + Rule 8) -- 2 secondary anchors diverge honestly

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~13:45

## 4 K-fact combination anchors (pre-HP-7 lock-in): the HP-7 CORE is GO.
- A1 beta* = sqrt(N/K)(1+CoV)^-1 recovery = 1.00 of grid-optimal -> beta* CLOSED-FORM VALIDATED. HP-7 can lock it in.
- A3 Rule 8 (Modern Hopfield log-sum-exp) vs Rule 1 (weighted sum) on conflicting facts = +29.3pp -> Rule 8 VALIDATED
  (softmax down-weights anti-aligned facts; large win). HP-7 combination architecture confirmed.
## 2 secondary anchors diverge from prediction (honest):
- A2 K-transition: predicted ~14-18 (sqrt(N)/2). Measured >25 (recall held above 0.80 to K=25). Either substrate
  handles MORE facts than predicted (K-gate at 7 is safely conservative) OR my top-1-in-set recall metric is too
  lenient (Hopfield all-K-recoverable would transition earlier). Flagging the metric ambiguity; K-gate=7 is safe regardless.
- A4 resonator non-determinism: block-local resonator float32 vs float64 = 0% disagreement (DETERMINISTIC at N=1024).
  Does NOT confirm the resonator-ban for cert paths -- at least block-local at this scale is reproducible. The ban may
  be over-cautious for block-local; dense-resonator may still be non-deterministic. Recommend keeping Rule 8 for cert
  paths anyway (validated) but the resonator-ban rationale needs a harder test (dense resonator, larger N) to confirm.
## NET: HP-7 lock-in safe on beta* + Rule 8 (the load-bearing params). Building HP-7 e2e next.
## Both queues high-priority: GPU strong-baselines-1B (honest substrate-vs-neural at 1B), CPU K-fact-anchors. Tier-4-Llama on cloud (Testbed).
**END.**
