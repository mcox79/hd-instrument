# Change Request -- Bundle F: add iterated-mode cells F5 + F6

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Subject:** Add 2 cells (F5 + F6) to Bundle F testing substrate's ITERATED retrieval mode at trigram (escapes single-pass TC0 bound; potentially produces HP where F2 single-pass HF)

---

## Status check requested

- [ ] Has Bundle F engineering started?
- [ ] If yes: can 2 new cells be added before dispatch?

Expected: Bundle F engineering not started (just shipped 2026-06-04). Change-request applies cleanly during scaffold work.

---

## Capability question (additional cells)

Bundle F as originally specified tests SINGLE-PASS combined architecture at trigram (Cell F2). Per [[feedback-pressure-test-negative-findings]] and today's complexity-class analysis: single-pass substrate is TC0; substrate ITERATED retrieval reaches depth K via K iterations.

Cells F5 + F6 add iterated-mode tests:

- **Cell F5:** Substrate iterated retrieval at trigram. Combined architecture from F2 + iterated query mode (2-step retrieval: predict bigram, re-inject with prior context, predict next bigram). Tests whether iterated mode escapes single-pass TC0 at substrate-class scale.

- **Cell F6:** Substrate iterated + position-binding for context state. Combined architecture + 2-step retrieval + position-bound context state maintained across iterations. Maximum-aggressive iterated mode test.

---

## Pre-reg HP/MID/HF for new cells

**Cell F5 (substrate iterated, 2-step retrieval, trigram V=70, N=4096):**

- HARD-PASS: trigram BPC < uniform_baseline - 1.0 nat AND 3/3 seeds. Substantive iterated learning at K=3 confirms iterated mode escapes TC0.
- MIDDLE: BPC in [uniform - 0.3, uniform - 1.0] nat
- HARD-FAIL: BPC >= uniform - 0.3 nat

**Cell F6 (substrate iterated + position-bound context state, trigram V=70, N=4096):**

Same HP/MID/HF bands as F5 (more aggressive architecture; should HP if F5 MID).

## P_deflated (per today's methodology)

**Updated per pressure-test-negative-findings stance:**

**Cell F5 (iterated mode):**
- P_algebraic = 0.55 (substrate iterated retrieval reaches NC1 per Frady-Sommer 2020 resonator network precedent; trigram is NC1 for V>=70 per Merrill-Sabharwal 2022; substrate iterated could match)
- P_implementation:
  - P_no_subsumption = 0.85 (W-modifying iterated mode)
  - P_convergence = 0.65 (iterated retrieval has clean convergence per Frady 2020)
  - P_budget = 0.55 (iterated mode adds compute but not memory; fits substrate-class)
  - P_task_match = 0.45 (trigram at V=70 is right at NC1 boundary; iterated reaches but may degrade)
- Joint P_implementation ~ 0.13
- P_joint = 0.55 * 0.13 ~ **0.07 for HP**

LOW joint P but the test is INFORMATIVE either way: HP confirms iterated mode escape from TC0; HF + Cell F2 HF + Cell F4 V=16 HP confirms iterated mode insufficient at substrate-class scale (next direction: hierarchical iterated).

**Cell F6 (iterated + position-binding):**
- Similar P_implementation; slightly higher P_algebraic (~0.60) due to combined architecture
- P_joint ~ 0.08 for HP

## Wall-time

Cell F5: ~3-5 min per seed (2 iterations per inference; modest overhead vs F2 single-pass)
Cell F6: ~3-5 min per seed (similar)
Total addition to Bundle F wall: +20-30 min for 6 measurements

## Engineering scope addition

~2-3h:
- Iterated retrieval wrapper around F2 combined architecture (2-step query loop)
- Context state encoding via position-binding (reuses Bundle E position-binding scaffold)
- Eval harness for iterated mode (different prediction loop than single-pass)

Reuses F2 + Bundle E scaffolds.

---

## Strategic outcome

### If F5 or F6 HP (substrate iterated escapes TC0)

- MAJOR finding: substrate iterated mode reaches NC1 at substrate-class scale
- Supports user's pushback: substrate is NOT bound by single-pass TC0
- Cap_map: NEW sub-property founding for "substrate iterated retrieval reaches NC1 per Frady 2020 + Merrill-Sabharwal complexity bounds"
- Product positioning: substrate has BROADER capability than single-pass analysis suggested

### If F5 + F6 MIDDLE

- Iterated mode provides partial gain; doesn't fully escape TC0 at substrate-class scale
- Need to test at larger N or hierarchical iterated mode

### If F5 + F6 HF (alongside F2 HF; F4 V=16 HP)

- Iterated mode insufficient at substrate-class scale ALONE
- Combined with hierarchical aggregation (today's drills) may still escape
- Inform: next test is hierarchical iterated (3 substrates each iterated; meta composes)

---

## What this is (plain language)

Bundle F as originally specified tested whether substrate (with all its tricks combined) could match LLM at trigram task in ONE forward pass. The de-linguistification drill predicted NO (complexity bound TC0 vs NC1).

But substrate has another mode: query itself MULTIPLE TIMES, each query conditioned on previous result. This is "substrate chain-of-thought." It reaches higher complexity class than single-pass substrate.

Cells F5 + F6 test substrate's iterated mode at trigram. If F5/F6 HP and F2 HF: confirms iterated mode is the escape from single-pass limits.

This connects to user's pushback that I was anchoring conservatively. Substrate's capability range depends on operating mode, not just architecture.

---

## What this is NOT

- NOT a replacement for F2 single-pass test (F2 still informative for TC0 bound)
- NOT a definitive test of substrate-vs-LLM at frontier (still small scale)
- NOT a cloud test ($0 CPU)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-pressure-test-negative-findings]]: testing alternate operating mode (iterated) escapes single-pass bound
- Per [[feedback-change-request-protocol]]: status check first; applies during scaffold work
- Per [[feedback-no-padding-experiments]]: cells discriminate the iterated-mode-escapes-TC0 hypothesis
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchor F5 uses `_iterated_v1`; F6 uses `_iter_posbind_v1`
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** add Cells F5 + F6 to Bundle F scaffold. ~2-3h additional engineering; +20-30 min CPU wall. Verdict drives "substrate iterated mode escapes TC0" capability characterization.

**Research session:** holds for verdict; ships pressure-tested capability map per outcome.
