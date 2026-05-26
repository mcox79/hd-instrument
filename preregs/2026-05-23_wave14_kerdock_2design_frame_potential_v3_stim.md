# Prereg — wave14_kerdock_2design_frame_potential_v3_stim

**Date filed:** 2026-05-23
**Routing source:** notes/strategy_to_exp_dev_F4_v3_stim_2026-05-23.md
**Drill source:** notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md (test 3.A)
**Counterpart prereg:** preregs/2026-05-23_wave14_kerdock_mub_distinguishability_v1.md (3.B)
**Predecessors:** v1 (rejected — silent unitary bug), v2 (rejected — spec formula error caught by d=8 enumeration; see "v2 retrospective" below).

## Hypothesis

The Clifford ambient group (containing the substrate's Kerdock-PSL anchor)
is a unitary 2-design at production d. By Gross / Bravyi-Maslov, conditional
on the symplectic part S of a Clifford U_S and averaging over Pauli signs:

```
E_p[|Tr(U_S)|^4 | S] = d^2 / 2^{rank_{F_2}(S - I)}
```

so the frame potential decomposes as a symplectic-rank expectation:

```
F_4 = E_{S ~ Clifford symplectic part} [ d^2 / 2^{rank(S - I)} ]
```

(NOTE: exponent is `rank`, not `2*rank`. See v2 retrospective.)

## Hard pass / hard fail

- **HARD PASS (2-design):** F_4 in [1.90, 2.10] (Haar; within +/-5% of 2.0).
- **HARD FAIL:** F_4 outside band.
- **INCONCLUSIVE:** Self-test agreement gap (formula vs direct at d=8) > 5*SE.

Single band only: the Clifford group is exactly a 2-design AND a 3-design,
but F_4 = E|Tr(U)|^4 is the 4th-MOMENT and the 2-design property fixes it
at 2.0. The "3-design defect" appears at F_6, not F_4. Strategy spec's
"3.0 band" was a theoretical error; we drop it.

## Algorithm

1. Sample U via `stim.Tableau.random(m)` — verified-correct uniform sampler
   over the Clifford group on m qubits.
2. Extract the 2m x 2m F_2 symplectic matrix S = `[[x2x, x2z], [z2x, z2z]]`
   from `t.to_numpy()`.
3. Compute rank_F_2(S - I) by Gaussian elimination (same routine as v2).
4. Accumulate d^2 / 2^{rank(S-I)} into a running mean.

n=10000 samples at m=12 (d=4096) for production. Benchmark: 3.3s for n=10000
at d=4096 on local CPU.

## Self-test gate (MANDATORY — caught v2's bug, kept)

1. f2_rank correctness on 5 hand-constructed test cases (same as v2).
2. Identity tableau gives identity symplectic matrix at m=4.
3. **d=8 formula-vs-direct cross-check at n=2000**:
   - Sample 2000 random Cliffords on m=3 qubits via stim.
   - Compute F_4 two ways: (a) formula d^2/2^rank(S-I); (b) direct |Tr(U)|^4.
   - GATE 1: |formula - direct| < 5 * sqrt(SE_formula^2 + SE_direct^2).
   - GATE 2: formula F_4 in [1.90, 2.10] (Haar band).

If d=8 gate fails → defer to Option G (file upstream-push to Strategy;
DO NOT queue d=4096). Per strategy spec.

## v2 retrospective

v2 reported d=8 "FAIL" with F_4 = 0.265625 using formula `d^2/2^{2*rank}`.

The d=8 enumeration rank histogram for PSL(2, F_8) was {0: 1, 3: 63, 6: 440}.

Applying the **correct** formula `d^2 / 2^rank` (exponent 1) to this histogram:

```
F_4 = (1*64/2^0 + 63*64/2^3 + 440*64/2^6) / 504
    = (64 + 504 + 440) / 504
    = 1008 / 504
    = 2.000000  exactly
```

So **PSL(2, F_8) IS a 2-design at d=8 — exact integer value F_4 = 2**.

v2's code was correct; the strategy spec had a formula typo (`2*rank`
where it should have been `rank`). The structural gate caught it cleanly.

v3 uses stim's verified random Clifford sampler as an INDEPENDENT
cross-check on the FULL Clifford group (which is the ambient group
containing the PSL subgroup). The v2 exact-enumeration result for the
PSL subgroup specifically, with the corrected formula, anchors the
PSL-restriction case at exactly F_4 = 2.0. Together with v3's stim-based
estimate for the full Clifford group, we have both layers verified.

## Sample sizes / runtime

- d=4096 (m=12), n=10000 stim Clifford samples.
- Per-sample: 24x24 F_2 matrix construction + rank via F_2 Gaussian elim.
- Total: ~3.3 s on local CPU (benchmarked). Generous budget on remote.
- Lane: remote_cpu_queue.
- Timeout: 1800 s (very conservative for a 3.3 s job; allows for any
  remote-machine slowness or first-run stim import overhead).

## Dependencies

- `stim >= 1.0` — Google quantumlib Clifford simulator. Installed locally
  (verified 1.16.0 on 2026-05-23). MUST be installed on remote_cpu_queue
  runner. If install fails on remote, the queue runner will report
  ImportError and we defer to Option G per strategy spec.

## What v3 keeps from v2

- Mandatory d=8 self-test gate (now formula-vs-direct cross-check via stim).
- F_2 Gaussian-elimination rank routine (passes unit tests; not bug class).
- Decision-log + prereg discipline.
- Honest upstream-push pattern.

## What v3 drops from v2

- Hand-rolled `mat_mul_in_basis` + trace-form matrix T + conjugation C
  construction. Replaced by stim's verified Clifford sampler.
- The PSL(2, F_{2^m}) explicit sampler (stim doesn't expose this restriction;
  Path A in spec).
- The exponent-2 formula error from strategy spec (corrected to exponent 1).

## Decision log

`notes/exp_dev_decisions_2026-05-23.md` via `append_decision_log.py`.
