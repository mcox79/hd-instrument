# Routing -- Bundle F combined-everything architecture at trigram (complexity-bound test)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical complexity-theory bound test (4 cells; CPU)
**Source:** de-linguistification 2x drill landed 2026-06-04 (TC0 vs NC1 complexity-class separation result); user pushback on substrate's frontier limits

---

## Capability question

Does substrate's FULL COMBINED ARCHITECTURE (cf-RPE + Drosophila sparse coding + STDP-asymmetric + position-binding + modern Hopfield p=4) outperform any individual variant at K=3 trigram task at substrate-class N=4096, V=70 char-LM?

This is the empirical test of the COMPLEXITY-THEORY BOUND. Per de-linguistification drill: TC0 vs NC1 separation predicts K>=3 LM at V>=70 is OUTSIDE substrate's complexity class regardless of architectural combinations. Even all known W-modifying + capacity-boosting primitives combined cannot bypass TC0 ceiling under TC0 != NC1 conjecture.

**Pre-reg expectation: HARD-FAIL** (confirms complexity-theory bound at substrate-class scale)
**Pre-reg surprise: HARD-PASS** (would refute Merrill-Sabharwal 2022 at this scale; publishable result)

This test is informative either way.

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_combined_everything_trigram_complexity_bound_v1_n4096`

**Cells:**
- Cell F1: K=1 Hebbian baseline (control) at trigram V=70 N=4096
- Cell F2: Full combined architecture at trigram V=70 N=4096 -- cf-RPE + Drosophila sparse f=0.05 + W_total = W_Hebbian + 0.5*W_STDP + position-binding via multi-bank addressing + modern Hopfield p=4 retrieval
- Cell F3: Cell F2 architecture + scale to N=16384 (higher capacity per modern Hopfield p=4 + sparse predictions)
- Cell F4: Cell F2 architecture + reduced vocabulary V=16 (well-below K* ceiling per algebraic prediction K*_sparse_combined ~ 4-5 at V=16)

**HARD-PASS:** Cell F2 or F3 achieves trigram BPC < uniform_baseline - 1.0 nat AND 3/3 seeds converge. Would REFUTE TC0 bound at substrate-class scale; publishable surprise.

**MIDDLE:** Cell F2/F3 BPC in [uniform - 0.3, uniform - 1.0] nats. Combined architecture provides some gain but not full substrate-as-training-mechanism at K=3.

**HARD-FAIL:** Cell F2/F3 BPC >= uniform - 0.3 nats (no meaningful gain). Confirms TC0 complexity bound at substrate-class scale.

Cell F4 (V=16 reduced vocab) serves as POSITIVE CONTROL: if combined architecture works at all, it should work at V=16 (K*_combined ~ 5+; well above K=3). If F4 also HF, combined architecture has implementation issues independent of complexity bound.

## Resource

Local CPU. Reuses Bundle A + Bundle E scaffolds (cf-RPE + sparse + STDP + position-binding all exist or are in Bundle E scope).

## Cost ceiling

$0 CPU. Per-seed wall ~2-3 min for combined-architecture cell (heavier than baselines). Total ~30-45 min for 12 measurements.

## P_deflated (per today's methodology)

**Updated per de-linguistification drill complexity-theory result:**

**P_algebraic = 0.10**: TC0 vs NC1 conjecture predicts substrate cannot reach K=3 LM at V=70 regardless of architectural combinations

**P_implementation:**
- P_no_subsumption = 0.90 (combined architecture is W-modifying)
- P_convergence = 0.55 (combined architecture has many interacting parts)
- P_budget = 0.60 (N=4096 substrate-class)
- P_task_match = 0.15 (trigram V=70 is OUTSIDE TC0; complexity-class binding)
- Joint P_implementation ~ 0.045

**P_joint = 0.10 * 0.045 ~ 0.005 for HP**

This is VERY LOW. HP would be a publishable surprise refuting Merrill-Sabharwal 2022 at this scale.

MIDDLE: ~0.20 (combined architecture provides some gain via capacity-boost; not full task capability)
HF: ~0.75 (most likely; confirms complexity bound)
F4 V=16 HP: ~0.55 (positive control at vocabulary BELOW complexity boundary)

## Engineering scope

~2-3h:
- Integrate position-binding (multi-bank addressing) into Bundle A combined scaffold
- Add modern Hopfield p=4 retrieval head
- Trigram task generator at V=70 (Shakespeare-class)
- Reduced-vocab task generator at V=16 (positive control)

Reuses substantial Bundle A + Bundle E + earlier polynomial-p engineering.

## Strategic outcome

### If HP at F2 or F3 (publishable surprise)

- Refutes TC0 bound at substrate-class scale
- Combined architecture provides ADAPTIVE serial-equivalent computation
- Substrate's role expands from System 1 -> possibly System 1+ at substrate-class scale
- MAJOR cap_map update; potentially flagship product narrative

### If MIDDLE (architecture provides some gain at trigram)

- Combined architecture partially mitigates TC0 bound
- Identifies WHICH combination provides the gain (cf-RPE + sparse most likely)
- Substrate remains primarily System 1 with marginal System 2 capacity

### If HF (complexity bound confirmed)

- TC0 bound empirically validated at substrate-class scale
- Substrate is structurally System 1 (matches de-linguistification drill prediction)
- Product positioning: substrate as System 1 component in System 1+2 hybrid (NOT substrate-replaces-LLM)
- Cell F4 V=16 positive control checks: if F4 HP and F2 HF, implementation is correct and complexity bound holds. If F4 also HF, debug architecture before further interpretation.

---

## What this is (plain language)

Substrate has been shown algebraically (today's de-linguistification drill) to be in complexity class TC0. LLMs with chain-of-thought reach NC1+ which is provably above TC0. This means substrate fundamentally cannot match LLM at multi-step reasoning, no matter what architectural tricks we use.

Bundle F tests this empirically. Throw every substrate trick we have (cf-RPE, sparse coding, STDP, position-binding, modern Hopfield) at the trigram task. If substrate STILL fails, the complexity bound is confirmed at substrate-class scale. If substrate succeeds, we've discovered something genuinely new (would refute published theory at this scale).

Plus Cell F4 at V=16 is a positive control: with vocabulary REDUCED below the complexity boundary, the same architecture should work. If F4 works and F2 doesn't, the complexity bound is the binding constraint. If F4 also fails, there's an implementation bug.

This is the EMPIRICAL TEST of the theoretical bound. Most likely outcome: HF at F2 + HP at F4 -> complexity bound empirically validated -> substrate's role as System 1 in System 1+2 hybrid is the right product positioning.

---

## Strategic context

Connects to:
1. De-linguistification drill (landed; TC0 vs NC1 result)
2. System 1+2 hybrid architecture drill (in flight)
3. Hierarchical training architecture drill (in flight)
4. 5-corpus hierarchical empirical test (in flight)
5. Multi-modal substrate primitives drill (landed; modality-agnostic confirmed)

Bundle F is the COMPLEXITY-BOUND test that anchors all these theoretical findings empirically.

---

## What this is NOT

- NOT a final test of substrate as a training mechanism (already tested at Bundle A bigram; HP for cf-RPE + sparse)
- NOT a refutation of substrate's value (substrate's value is at System 1 + audit primitives; not at System 2)
- NOT a cancellation of Bundle B / E (those test other capability questions)
- NOT a cloud GPU test ($0 CPU only)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: tests specific complexity-bound hypothesis; 4 cells discriminate the bound
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-small-scale-first-methodology]]: rung-1 substrate-class N=4096
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF + positive control pre-registered; HF expected; HP would be publishable surprise
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** ~2-3h engineering + ~30-45 min CPU wall. Reuses Bundle A + Bundle E scaffolds. Verdict drives complexity-bound empirical confirmation OR publishable refutation.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Research session:** holds for verdict; ships System 1+2 hybrid + complexity-bound interpretation in capability-implication note.
