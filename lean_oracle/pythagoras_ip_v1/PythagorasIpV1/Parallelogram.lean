/-
Copyright (c) 2026 hd-instrument.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import Mathlib.Analysis.InnerProductSpace.Basic

/-!
# Parallelogram law in real inner product spaces

For u, v in a real inner product space:
|u + v|^2 + |u - v|^2 = 2 * (|u|^2 + |v|^2).

Unlike the triangle inequality, the parallelogram law is genuinely
inner-product-specific: it FAILS in general normed spaces and characterises
norms that come from an inner product.

Bucket A cert-stream Lean batch (batch proof 3 of 3 = PROOF_RECORD #4) per
USER-ratified 6h plan 2026-06-18.
-/

theorem parallelogram_law_ip {F : Type*} [NormedAddCommGroup F] [InnerProductSpace ℝ F]
    (u v : F) :
    ‖u + v‖ ^ 2 + ‖u - v‖ ^ 2 = 2 * (‖u‖ ^ 2 + ‖v‖ ^ 2) := by
  exact parallelogram_law_with_norm (𝕜 := ℝ) u v
