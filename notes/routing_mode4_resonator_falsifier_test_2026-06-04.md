# Routing -- Mode 4 resonator falsifier test at substrate scale

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical decisive falsifier (1 cell + parameter sweep; CPU)
**Source:** Operating-modes-beyond-single-pass 2x drill landed 2026-06-04 (research_drill_substrate_operating_modes_beyond_single_pass_2x_2026-06-04.md)

---

## Capability question

Does substrate's Mode 4 (resonator network coordinate-descent unbinding) achieve K=5 factor-recovery at N=4096 with >= 85% accuracy within 50 iterations? This is the published Frady-Sommer 2020 benchmark for resonator NC1 capability. If yes: substrate's Mode 4 NC1 escape from single-pass TC0 is empirically validated at substrate-class scale. If no: Frady-Sommer 2020 results don't extend to N=4096 substrate-class scale; Mode 4 questionable.

This is the SINGLE LOAD-BEARING EMPIRICAL TEST for substrate's published NC1 escape mode.

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_resonator_k5_factor_recovery_n4096_v1`

**Cells:**
- Cell R1: K=5 factor recovery at N=4096 via resonator coordinate-descent; 50 iter max; 5 seeds
- Cell R2: K=3 factor recovery at N=4096 (control; should HP cleanly per Frady-Sommer 2020)
- Cell R3: K=8 factor recovery at N=4096 (stress test; expected MIDDLE per Frady-Sommer 2020 scaling)

**HARD-PASS:** Cell R1 achieves >= 85% recovery within 50 iterations across 4/5 seeds. Mode 4 NC1 validated empirically at substrate-class scale.

**MIDDLE:** 60-85% recovery within 50 iterations on average. Mode 4 partial; possibly needs larger N or more iterations.

**HARD-FAIL:** < 60% recovery within 50 iterations OR divergence (oscillating estimates) across 3+/5 seeds. Frady-Sommer 2020 results don't extend to N=4096 substrate-class scale.

Cell R2 (K=3 control) MUST HP cleanly (~95%+) for the experiment to be valid. If R2 HF: implementation issues; debug before interpreting R1.

## Implementation specification

Per Frady-Sommer 2020 (Neural Computation):

```
Compositional vector: c = bind(A1, K1) + bind(A2, K2) + ... + bind(AK, KK)
where Ai are unknown factors drawn from V codebooks; Ki are known keys.

Resonator iteration:
  For each factor i:
    estimate_i^(t+1) = sign( cleanup(unbind(c, key_i) * product(estimate_j^(t) for j != i)) )
  where cleanup projects onto nearest codebook entry.

Converged when all estimates stable across 2 successive iterations.
Recovery success: all K factors recovered correctly.
```

Codebook size V per factor: V=512 (per Frady-Sommer benchmark)

## Resource

Local CPU. Resonator at N=4096, K=5, V=512 is matmul-light + cleanup.

## Cost ceiling

$0 CPU. Per-seed wall ~30-60s. Total ~30-60 min for 15 measurements (3 cells x 5 seeds).

## P_deflated (per today's methodology)

**P_algebraic = 0.65**: Frady-Sommer 2020 published convergence guarantees at N=512-1024; substrate-class N=4096 is within published regime extension

**P_implementation:**
- P_convergence = 0.70 (resonator coordinate-descent is well-characterized; convergence proofs exist)
- P_budget = 0.85 (K=5 factors at N=4096 with V=512 codebook fits comfortably)
- P_no_subsumption = 0.95 (resonator is W-modifying; not subject to NESS subsumption)
- P_task_match = 0.65 (factor-recovery is exactly Frady-Sommer 2020's benchmark)
- Joint P_implementation ~ 0.36

**P_joint = 0.65 * 0.36 ~ 0.23 for HP**

This is the cleanest substrate-NC1-escape test we can run. P=0.23 with strong lit precedent.

## Engineering scope

~2-3h:
- Resonator coordinate-descent loop (reuse Frady-Sommer 2020 reference impl from GitHub)
- Codebook generation (V=512 random bipolar vectors per factor; K=5 factors)
- Cleanup operation (nearest-codebook-entry projection)
- Convergence monitor + iteration counter
- Recovery rate measurement (compare to ground-truth factors)

Reuses substrate's existing bipolar primitives + binding operations.

## Strategic outcome

### If HP (Mode 4 resonator NC1 escape validated)

- Substrate's published NC1 capability empirically confirmed at substrate-class scale
- Mode 4 becomes priority engineering target for substrate-as-System-1.5 (substrate handles NC1 tasks at iteration cost)
- Combined with Mode 2 adaptive composition and Mode 5 substrate+working-memory: substrate has explicit Turing-complete path
- Cap_map: NEW sub-property founding for "substrate Mode 4 resonator network achieves NC1 capability at N=4096"
- Product narrative: substrate is "auditable System 1 PLUS NC1 escape via resonator mode at iteration cost"

### If MIDDLE

- Mode 4 partial; resonator converges slowly OR with reduced accuracy at N=4096
- Investigate: more iterations? larger N? modified resonator architecture?
- Substrate's NC1 path remains plausible but needs scale extension

### If HF

- Frady-Sommer 2020 doesn't extend to N=4096; Mode 4 questionable at substrate-class scale
- Mode 2 adaptive composition becomes primary substrate-NC1 path
- Mode 5 substrate-as-NTM remains Turing-complete via external memory
- Combined modes still reach NC1+; Mode 4 alone refuted

---

## What this is (plain language)

Resonator networks are a published technique (Frady-Sommer 2020 Neural Computation) for recovering individual factors from a compositional binding via iterative coordinate-descent. They reach NC1 complexity-class capability (multi-step inference) through iterated substrate queries.

This test asks: does the published technique work at N=4096 (substrate-class scale)?

- If yes: substrate has a CONFIRMED escape from the single-pass TC0 bound; can do NC1 tasks at iteration cost
- If no: resonator doesn't scale to substrate-class; need different NC1 path

This is the cheapest decisive validation of substrate's most-published NC1 escape mode.

---

## Strategic context

Connects to:
1. Operating-modes-beyond-single-pass 2x drill (landed; identified Mode 4 as priority target)
2. De-linguistification 2x drill (TC0 vs NC1 separation; Mode 4 is THE escape)
3. Pressure-test-negative-findings memory (alternate operating modes escape single-pass bounds)
4. Bundle F augmentation Cells F5 + F6 (iterated mode tests; resonator IS an iterated mode)

Mode 4 falsifier test is the empirical anchor for substrate's most-published NC1 escape.

---

## What this is NOT

- NOT a complete characterization of substrate's NC1 capability (only Mode 4; Modes 2 + 5 separate)
- NOT a substrate-vs-LLM comparison (factor-recovery, not language modeling)
- NOT a cloud test ($0 CPU)
- NOT a substitute for Bundle F augmentation (different test; Bundle F is task-level; this is primitive-level)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-pressure-test-negative-findings]]: empirical validation of alternate operating mode (Mode 4) escaping single-pass TC0
- Per [[feedback-no-padding-experiments]]: 1 load-bearing cell + 2 controls
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-small-scale-first-methodology]]: substrate-class N=4096; published Frady-Sommer 2020 benchmark
- Per [[feedback-verify-implementations]]: validate against Frady-Sommer 2020 reference implementation
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** ~2-3h engineering (reuse Frady-Sommer 2020 reference impl) + ~30-60 min CPU wall. Verdict drives Mode 4 NC1 escape empirical validation -- the load-bearing test for substrate's most-published alternate operating mode.

**Research session:** holds for verdict + cross-domain interference drill landing; ships consolidated operating-modes cap_map note per outcomes.
