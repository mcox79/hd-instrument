/-
Copyright (c) 2026 hd-instrument.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import Mathlib.Analysis.InnerProductSpace.Basic

/-!
# Cauchy-Schwarz in real inner product spaces

For u, v in a real inner product space, the absolute value of their inner
product is bounded by the product of their norms:
|inner u v| <= |u| * |v|.

This holds unconditionally (no orthogonality or other hypothesis).

Bucket A cert-stream Lean batch (proof 2 of 3) per USER-ratified 6h plan
2026-06-18. Pattern mirrors pythagoras_ip.
-/

theorem cauchy_schwarz_ip {F : Type*} [NormedAddCommGroup F] [InnerProductSpace ℝ F]
    (u v : F) :
    |@inner ℝ F _ u v| ≤ ‖u‖ * ‖v‖ := by
  exact abs_real_inner_le_norm u v
