# Pre-reg: substrate_multihop_pointer_chain_hybrid_v1

**Authored:** 2026-06-25 by exp_dev (coordinated blitz Agent 1 of 3 — Cell C).
**Cell:** `experiments/exp_substrate_multihop_pointer_chain_hybrid_v1.py`
**Lane:** 1 (substrate-native; pure numpy).
**Routing intent:** local_cpu_queue (CPU-feasible; ~20min wall estimated for 3 seeds).
**Director spec:** `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`

## Why this cell

Last night's beta-sweep confirmed Barrier-1 diagnosis: at ALL betas {0.5, 2, 10,
50, 500, 8192} top1 ≤ baseline 0.65 for 2-hop retrieval. The multi-hop ceiling is
**upstream of the decoder**. META gap-map drill predicted this; category-theory
explains it: HRR bind is a quotient map; composing two quotient maps multiplies
information loss. At N=8192 V_P=10 K=2, substrate sits BELOW the
retraction-existence threshold (N >> V·K). No decoder cleanup can recover what
the storage primitive lost.

The META drill named two escape hatches:
1. Anisotropic encoder (Wave D hub-spoke v3)
2. **External pointer chains** (non-compositional; this cell)

Pointer-chain hybrid: substrate stores triples via HRR bind for 1-hop retrieval
BUT maintains pointer-index (substrate atoms, NOT Python dict) for multi-hop
traversal. Per-step argmax + cleanup avoids compounding HRR error.

## Strategic intent

Test whether non-compositional pointer-chain transfers to apples-to-apples Lane-1
synthetic random-bipolar regime. Closes Barrier-1 if HARD_PASS via the
escape-hatch path.

## Config

| Param | Value | Reason |
|---|---|---|
| N_DIM | 8192 | matches beta-sweep regime |
| V_CONCEPTS | 200 | Director spec |
| V_PREDICATES | 10 | Director spec |
| K_SET | 20 | Director spec |
| N_CHAINS | 300 | Director spec (per arm) |
| SEEDS | [7, 17, 23] | 3 seeds for cv check |
| HOP_DEPTHS | [2, 5, 10] | depth retention test |

## Arms (5)

1. **ARM_BASELINE_HRR_2HOP**: pure HRR cascaded chain (control; reproduces ~0.65)
2. **ARM_POINTER_CHAIN_2HOP**: pointer-index for routing; per-step argmax cleanup
3. **ARM_POINTER_CHAIN_5HOP**: 5-hop depth retention
4. **ARM_POINTER_CHAIN_10HOP**: 10-hop depth retention
5. **ARM_POINTER_HRR_HYBRID**: pointer-chain routing + HRR bind for content cleanup
   at retrieval node (substrate-product mode)

## Substrate-native discipline (load-bearing)

The pointer-index is implemented as substrate atoms encoded via HRR bind
(`E[s] * R[p]` keys → `E[target]` values in a SINGLE W matrix), with per-step
nearest-atom cleanup via `argmax_o (E @ scores)`. This is NOT a Python dict
lookup. Verify in code: `arm_pointer_chain()` uses only numpy matrix ops on
the bipolar atom matrix E and the Hebbian W; no dict structures.

## HARD bands (LOCKED prospectively)

- **HARD_PASS_BREAK_CEILING (PRIMARY)**:
  - ARM_POINTER_CHAIN_2HOP top1 ≥ 0.95
  - AND ARM_POINTER_HRR_HYBRID top1 ≥ 0.85
  - AND CV ≤ 0.05
- **HARD_PASS_DEPTH_RETENTION**: ARM_POINTER_CHAIN_10HOP top1 ≥ 0.80
  (proves pointer-chain doesn't compound errors at depth)
- **MIDDLE_BAND**: 0.75 < PRIMARY ≤ 0.95
- **HARD_FAIL**: PRIMARY ≤ 0.75 (pointer-chain doesn't help; substrate multi-hop
  limit is more fundamental than chaining mechanism)

## Sanity rails

- ARM_BASELINE_HRR_2HOP reproduces 0.65 ± 0.02 of last night's beta-sweep
  baseline (provenance check; same regime)

## Honest scope flags

- **WHAT THIS DOES**: tests whether non-compositional pointer-chain (Store cell
  `exp_pointer_chain` proved at depth=100 in a DIFFERENT regime) transfers to
  apples-to-apples Lane-1 synthetic regime
- **WHAT THIS DOES NOT DO**: prove pure-HRR composition works at multi-hop. The
  compositional path (Barrier-4 anisotropic encoder) still requires hub-spoke v3
  + Resonator together
- **WHAT COULD KILL IT**:
  - (a) verify-the-referent — Skunkworks must confirm Store `exp_pointer_chain`
    verdict=HARD_PASS (not MIDDLE_BAND framing); this v1 dispatch does not
    block on that (testing the mechanism on its own)
  - (b) pointer-chain at depth ≥ 5 may show step-product decay since per-step
    accuracy ≈ 0.65 → 0.65^N decay; depth-retention band probes this
  - (c) substrate-native vs Python-dict discriminator: pointer-chain that uses
    HRR for content IS substrate-native; pure external index without HRR
    retrieval is NOT (audited in code)
- **APPLES-TO-APPLES**: same encoder / N / K_SET / chains as beta-sweep so any
  lift is comparable

## Substrate-product framing

If HARD_PASS, the substrate-product story is:
- 1-hop content retrieval: HRR exact, chain-grade
- Multi-hop traversal: pointer-chain index (substrate atoms holding next-hop pointers)
- Per-step cleanup: HRR at retrieval node (nearest-atom argmax)

This is brain-aligned: hippocampus does pattern-completion via attractor
dynamics (HRR analog) but place cells + grid cells provide INDEX structure
(pointer-chain analog). The two systems aren't redundant; they're complementary.

## Phase-diagram scan

Depths tested: 2, 5, 10. Defines the retention curve. If 10-hop top1 ≥ 0.80,
the pointer mechanism survives compounding; if 10-hop collapses to chance,
per-step cleanup is insufficient.

## Q discipline

- All bands physically achievable: at N=8192/V_C=200 the per-step 1-hop ceiling
  is well above 0.95; cascading 2 of these via cleanup-attractor approaches
  0.95^2 ≈ 0.90 → 0.85 plausible for HYBRID
- 10-hop band 0.80 is AMBITIOUS — per-step 0.98 would give 0.98^10 ≈ 0.82;
  this is the genuine retention probe
- All bands locked BEFORE smoke or full data collected

## Fix #28 discipline

- Per-arm metrics reported (5 arms; depth-retention curves per-step); verdict_msg
  cites per-arm numerics + per-step accuracies
- Multi-seed CV computed and gated

## Pre-registered expectation (Q-discipline)

- ARM_BASELINE_HRR_2HOP reproduces ~0.65 ± 0.02 (regime-match sanity)
- P(POINTER_CHAIN_2HOP lifts 0.65 → 0.95): **0.55** (brain prior +0.10; Store
  precedent +0.10; calibration penalty -0.20)
- P(POINTER_HRR_HYBRID ≥ 0.85 AND 10HOP ≥ 0.80): **0.40** (stronger claim;
  both depth retention AND HRR cleanup at retrieval node)

## Disposition

- HARD_PASS_BREAK_CEILING_WITH_DEPTH → Skunkworks for landed-VET; cert as
  Barrier-1 closure via pointer-chain escape hatch
- HARD_PASS_BREAK_CEILING only (no depth retention) → cert + research drill
  on per-step cleanup primitive for depth retention
- HARD_FAIL → route NEGATIVE to Research for 2x revival drill (the
  pointer-chain mechanism doesn't help; investigate Barrier-4 anisotropic
  encoder path independently)

## Operational disciplines

- D1 roofline (CPU): pure numpy on N=8192/V_C=200; ~10-20min total for 3 seeds
- D2 atexit + per-seed checkpoint mandatory
- Self-test PASS gate (verified)
- LOCAL SMOKE PASS gate
- ASCII only
- Substrate-only (`_LLM_CALL_COUNTER = [0]`)

## Cites

- `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md` (Director spec)
- `notes/director_multihop_composition_store_scour_2026-06-24.md`
  (confirms `exp_pointer_chain` HARD_PASS depth=100 in Store)
- `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`
  (L5 category theory: pointer-chain is non-compositional escape hatch)
- Last night's `substrate_resonator_softchain_beta_sweep_v1` HARD_FAIL
  (closes decoder-side rescue path; pointer-chain is the alternative)
