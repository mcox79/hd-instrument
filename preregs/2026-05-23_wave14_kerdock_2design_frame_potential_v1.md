# Pre-registration: wave14_kerdock_2design_frame_potential_v1

**Date filed:** 2026-05-23
**Anchor of:** Section 3.A of `notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md`
**Lens:** Clifford-2-design / Kerdock-PSL(2, F_{2^m}) isomorphism check

## Hypothesis

The substrate's Kerdock-derived unitary group is isomorphic (up to global
phase) to the canonical PSL(2, F_{2^m}) Clifford-2-design lift
(Calderbank-Cameron-Kantor-Seidel 1997; Klappenecker-Roetteler 2003).
Under this isomorphism, the 4th frame moment

    F_4(G) = E_{U ~ G} |Tr(U)|^4

should land in the band [2, 3]: 2-design (Haar) would give 2; full
Clifford 3-design (Webb 2016) gives 3; the Kerdock subgroup (a strict
subgroup of Clifford with the PSL(2, q) structure) inherits one of these
two profiles depending on whether the 4-coset enumeration captures the
full Clifford 4-defect.

## Quantity

    F_4(Kerdock) := E_{U ~ U_Kerdock} |Tr(U)|^4

estimated by sample-mean over N_samples = 10000 dense d x d unitaries
drawn from the Kerdock subgroup. Comparison populations: Haar measure
on U(d) and the full Clifford group on m qubits (d = 2^m). All three F_4
values are estimated by the same Monte Carlo with shared seed and
sample size.

## Predictions

- 2-design baseline (Haar): F_4(Haar) = 2 - 1/d^2 (Mezzadri 2007).
- Clifford 3-design baseline: F_4(Cliff) = 2 + (d^2 - d) / (d^2 + 3d + 2)
  (Webb 2016 / Zhu 2017). At d = 64: F_4(Cliff) approx 2.940; large-d
  asymptote: 3.0.
- Kerdock-PSL(2, F_{2^m}): F_4(Kerdock) in [2, 3], asymptote depending on
  whether the bipolar/Hadamard-coset construction inherits the full
  Clifford 4-defect.

## HARD PASS (Clifford-2-design isomorphism CONFIRMED)

F_4(Kerdock) within +/-5% of either:
- Haar value 2.0  (band [1.90, 2.10])
- Clifford asymptote 3.0  (band [2.85, 3.15])

A pass on either band confirms the substrate's Kerdock subgroup matches
the standard 2-design or 3-design profile in the literature.

## HARD FAIL (Clifford-2-design isomorphism BROKEN)

F_4(Kerdock) outside BOTH bands above (i.e., neither in [1.90, 2.10] NOR
in [2.85, 3.15]).

Either outcome is informative:
- A bug-flag interpretation: our bipolar/Kerdock construction is
  non-canonical (e.g., the F_2-Gray-map encoding shifts us off the
  standard PSL embedding).
- A novel-finding interpretation: the substrate's Kerdock-MM 4-coset
  structure is a strict variant of the canonical Klappenecker-Roetteler
  lift; F_4 outside [2, 3] would mean either a sub-design (F_4 > 3) OR
  a super-design (F_4 < 2), both substrate-novel.

## Sampling-validity gate (this prereg)

Both empirical baselines must reach their theoretical values within a
generous band, else verdict is KERDOCK_2DESIGN_INCONCLUSIVE:
- |F_4(Haar) - 2.0| < 0.30 -- Mezzadri QR sampler must work.
- |F_4(Cliff) - F_4(Cliff, theoretical)| < 0.40 -- Clifford sampler must
  have mixed to (approximately) uniform on the group.

If either gate fails, no conclusion about Kerdock is drawn this run.

## Procedure

1. Build the Kerdock subgroup generators: H_all = H^{otimes m} (PSL "swap")
   and the m diagonal phase gates diag(q_b) for b in F_{2^m} (PSL
   "translations"), per the trace-self-dual basis Klappenecker-Roetteler
   lift.
2. Sample 10000 elements of each of {Haar, Clifford, Kerdock} via:
   - Haar: Mezzadri 2007 QR construction
   - Clifford: random words in {H_k, S_k, CNOT_jk} of length >= 50 m^2
   - Kerdock: random words in {H_all, diag(q_b)} of length >= 20 m
3. For each sample, compute trace and accumulate |Tr|^4.
4. Apply the verdict policy above.
5. Write metrics.json with F_4 values + standard errors + deviation
   summary + verdict + verdict_msg.

## Dimensionality

Spec'd at d = 4096 (m = 12). For tractability of dense unitary
construction we cap at d <= 256 (m = 8) on remote CPU. Smoke runs at
d = 16 (m = 4) with 200 samples per group.

## Falsifiable verdict vocabulary

- KERDOCK_2DESIGN_MATCH_HAAR     -- F_4(Kerdock) within +/-5% of 2.0
- KERDOCK_3DESIGN_MATCH_CLIFFORD -- F_4(Kerdock) within +/-5% of 3.0
- KERDOCK_ISOMORPHISM_BROKEN     -- outside both bands (HARD FAIL)
- KERDOCK_2DESIGN_INCONCLUSIVE   -- sampling-validity gate failed

## Implementation status (2026-05-23)

v1 random-word implementation has known issues with both the Clifford and
Kerdock subgroup samplers (mixing is incomplete at budgeted word lengths).
Filing upstream-push to Strategy
(`notes/exp_dev_to_strategy_kerdock_2design_frame_potential_2026-05-23.md`)
for re-implementation via:
- Option B: symplectic-rank trace formula (Hostens-Dehaene-De Moor 2005),
  sidestepping dense unitary construction.

This prereg remains valid for v2 reuse; only the sampler block changes.
