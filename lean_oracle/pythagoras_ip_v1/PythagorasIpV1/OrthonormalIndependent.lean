/-
Copyright (c) 2026 hd-instrument.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import Mathlib.Analysis.InnerProductSpace.Orthonormal

/-!
# Orthonormal families are linearly independent (real inner product spaces)

For an orthonormal family v : iota -> F in a real inner product space, v is
linearly independent.

This is a genuinely inner-product-STRUCTURAL result (it uses orthonormality, an
inner-product notion, to conclude a linear-algebra property) -- distinct from the
norm-identity/inequality batch (Pythagoras / Cauchy-Schwarz / triangle / parallelogram).

Bucket A cert-stream Lean batch (PROOF_RECORD #5) per USER "get everyone moving"
directive 2026-06-18.
-/

theorem orthonormal_linear_independent {F : Type*} [NormedAddCommGroup F] [InnerProductSpace ℝ F]
    {ι : Type*} {v : ι → F} (hv : Orthonormal ℝ v) :
    LinearIndependent ℝ v := by
  exact hv.linearIndependent
