# Change Request -- Bundle B: add Friston FEP cell at trigram

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Add Friston FEP architectural variant as a cell in Bundle B (task-complexity sweep). Hypothesis: FEP machinery activates at K>=3 trigram task where bigram (Bundle A) was too easy.

---

## Status check requested

- [ ] Has Bundle B engineering started?
- [ ] If yes: can a new cell be added before dispatch?
- [ ] If no: this change-request applies directly during scaffold work

Expected: Bundle B engineering has not started; change-request applies cleanly.

---

## Capability question (additional cell)

Does Friston FEP machinery (precision matrix Pi + epsilon prediction-error buffer + rank-1 precision adapt) outperform K=1 Hebbian baseline at K=3 trigram task, even though it HARD_FAILed at K=2 bigram in Bundle A?

Hypothesis: Bundle A HF was due to bigram being too easy for substrate (K* ~ 2.1 ceiling already maxed at K=1 baseline). At K=3 trigram, the additional supervised-signal capacity from FEP's precision-weighted error MAY activate.

---

## Pre-reg HP/MID/HF for the new Bundle B cell

**Cell B-FEP:** Friston FEP architecture (per Bundle A spec) at K=3 trigram V=70 char-LM + N=4096 + 3 seeds

- **HARD-PASS:** BPC < K=1_baseline_BPC - 0.50 nats at trigram AND 3/3 seeds. Confirms hypothesis: FEP activates at harder tasks.
- **MIDDLE:** improvement 0.20-0.50 nats over baseline
- **HARD-FAIL:** BPC >= K=1_baseline_BPC (FEP still fails even at harder task)

If HF at trigram too: confirms NESS hidden objective subsumes explicit FEP at substrate scale (per today's calibration drill in flight). FEP-class machinery is REDUNDANT for substrate-as-training; substrate's native dynamics already do what FEP framework explicitly encodes.

If HP at trigram: hypothesis confirmed -- FEP activates at higher complexity; should be primary candidate for K>=3 tasks.

---

## What this changes vs original Bundle B

Original Bundle B (per consolidated bundled routing) tests current architecture at varying task complexity. Adding FEP variant:
- Adds 3 cells (3 seeds at K=3 trigram V=70)
- Engineering: reuses Bundle A FEP scaffold + Bundle B trigram task generator
- Wall: +1-2 min CPU per cell ~ +5 min total

Net Bundle B becomes:
- 5 task complexities x 3 N x 3 seeds + 3 FEP cells = 48 cells total

Cost: $0 CPU. ~5-15 min wall (slightly extended from 5-10 min).

---

## P_deflated

- HP at trigram (hypothesis confirmed): **0.30** (FEP failed at bigram; testing at harder task is investigational)
- MIDDLE: 0.25
- HF (FEP also fails at trigram): **0.40** (most likely; confirms implicit-subsumption hypothesis from calibration drill)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-change-request-protocol]]: this is a change-request to existing Bundle B; status-check first
- Per [[feedback-no-padding-experiments]]: cell discriminates the FEP-task-complexity hypothesis specifically
- ASCII-only

---

**END.**

**Exp-Dev:** add Cell B-FEP to Bundle B's task-complexity sweep. Engineering trivial (reuse FEP scaffold from Bundle A + Bundle B trigram task generator). Adds ~5 min CPU to Bundle B total wall. Verdict drives FEP framework characterization at substrate scale.

**Research session:** holds for Bundle B verdict; ships calibration-drill-informed cap_map annotation on FEP architecture's task-complexity dependence.
