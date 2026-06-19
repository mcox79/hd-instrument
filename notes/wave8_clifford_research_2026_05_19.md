# Wave 8 Clifford G(2,0) failure — research synthesis

Returned 2026-05-19. Unbiased deep research on the closed Wave 8
negative (3.06 bpc, +0.55 worse than BSC).

## Bottom line

**G(2,0) is dead for byte-LM in our pipeline. Clifford-as-a-class
is NOT falsified.** The audit's "grades act as multi-heads" claim
had no literature support — that was a metaphor, not a citation.

## Where Clifford NNs actually win

Native O(n)/E(n)/Lorentz **symmetry** in the task:
- CGENN (Ruhe-Brandstetter NeurIPS 2023): n-body 3D, Lorentz HEP, 5D convex hull
- GCAN (Ruhe ICML 2023): 3D rigid-body, fluid dynamics
- STAResNet 2024: Maxwell PDE in G(3,1) — wins BECAUSE EM is Lorentz-covariant
- Quaternion RNN (Parcollet 2018): wins on SPEECH (multi-dim internal correlations), NOT bytes

**No published wins on byte-level / character-level language modeling.**

## Why G(2,0) was wrong for byte-LM

1. **Slot is 4D, too coarse.** With N=4096, 1024 slots x 4 components.
   The 4 components are forced into roles (scalar/e1/e2/e1e2) but
   nothing in delta-rule training pushes bytes into bivector vs scalar.
   No per-grade loss or readout. Flat W: (N,N) collapses across grades.
2. **G(2,0) is small.** Cl(2,0) is isomorphic to M_2(R). The audit
   overhyped "non-commutativity"; same non-commutativity exists in
   any matrix algebra. Without O(2)-equivariance constraint, it's an
   awkwardly-shaped real bilinear form.
3. **Bytes have no native geometry.** Assigning byte_atom uniformly
   across 4 grades destroys grade meaning.
4. **Position already gives order.** Our K=4 has explicit pos_atoms.
   Non-commutative geometric product gives redundant order signal that
   conflicts with positional binding.
5. **Bundling kills the structure.** L2-norm sum across K terms
   collapses grade information; no resonator/grade-projection cleanup.

## Larger algebras don't fix this

- **G(0,3) quaternions**: Parcollet wins on speech (channel
  correlation); bytes have no such structure. Cheapest test.
- **G(3,1) Lorentz (16-dim slot)**: more capacity but multi-head claim
  still has no mechanism. Slot count drops 4x.
- **G(4,1) conformal (32-dim slot)**: same critique.

**None match the inductive-bias criterion.** Going larger just
rearranges the same 4096 numbers under richer Cayley table.

## Is non-commutativity useful for byte-LM at all?

Likely NO. Wang-Karaletsos C3-factored gave +0.098 bpc using
**commutative** binding. The gain came from cubic capacity outside
additive span, not from order. Permutation-based position encoding
(non-commutative when composed with binding) is standard in VSA and
adequate. Geometric-product non-commutativity is structurally
redundant with pos_atom scheme.

## Five rescues (each <2h GPU)

| # | Rescue | Falsifier |
|---|--------|-----------|
| R1 | **Cl(0,2) quaternion at N=4096** | bpc within ±0.05 of G(2,0) → signature irrelevant; Clifford class dead with delta-rule |
| R2 | **G(3,1) Lorentz, 256 slots x 16D** | bpc > 2.50 → not slot size, algebra-task mismatch |
| R3 | **Mixed-grade separate channels** (scalar/vector/bivector readout heads, separate W per grade, predictions averaged) | bpc > BSC 2.4817 → audit "grades=multi-heads" hypothesis FALSIFIED even when properly implemented |
| R4 | **Learned grade weights** (CGENN-style: per-grade scalar gain) | bpc within ±0.05 of R3 → grade structure doesn't help |
| R5 | **Sparse grade-2 bivector concept atoms** (B3 from basis_modification_alternatives, PPMI-active byte pairs as bivectors) | gain < +0.01 → algebra provides no benefit even when deliberately placed by grade |

**R3 is the critical experiment**: directly tests the audit's
hypothesis. If R3 fails, "grades = multi-heads" is dead.

## Honest bottom line

Clifford-as-a-class is not yet falsified, but burden of proof has
shifted. To rehabilitate, need:
- (a) Explicit grade-projected readout (R3/R4)
- AND (b) Structural prior placing bytes by grade (R5)

If R3 + R5 both fail to beat BSC by >=0.05 bpc, "Clifford geometric
algebra adds capacity beyond commutative BSC for byte-LM at our scale"
is empirically dead.

**Deeper lesson** (consistent with geometric-ML literature): algebraic
richness without a task-matched symmetry is decoration, not capacity.
Bytes have no continuous symmetry to be equivariant to; this is the
same reason Clifford NNs have no published wins on discrete-symbol LM.

## Sources

- [Clifford Group Equivariant NN Ruhe et al. 2023 NeurIPS](https://arxiv.org/abs/2305.11141)
- [Geometric Clifford Algebra Networks Brandstetter et al. ICML 2023](https://arxiv.org/abs/2302.06594)
- [CliffordLayers Microsoft research portal](https://microsoft.github.io/cliffordlayers/research/)
- [CliffordNet All You Need is Geometric Algebra 2026](https://arxiv.org/abs/2601.06793)
- [Aerts/Czachor Geometric Algebra rep of BSC 2006](https://arxiv.org/abs/cs/0610075)
- [Patyk-Lonska Geometric Analogue of HRR 2007](https://ar5iv.labs.arxiv.org/html/0710.2611)
- [Parcollet Quaternion RNN 2018](https://arxiv.org/abs/1806.04418)
- [Tay et al. Lightweight Quaternion Networks for NLP 2019](https://arxiv.org/abs/1906.04393)
- [Lorentz Group Equivariant NN for particle physics](https://arxiv.org/pdf/2006.04780)
- [STAResNet Spacetime Algebra for Maxwell PDE](https://arxiv.org/pdf/2408.13619)
- [Resonator Networks for factoring distributed reps](https://arxiv.org/pdf/2007.03748)
- [VSA comparison Schlegel et al.](https://arxiv.org/pdf/2001.11797v2)
