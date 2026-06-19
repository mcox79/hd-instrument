/-
Copyright (c) 2026 hd-instrument.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import Mathlib.Analysis.InnerProductSpace.Basic

/-!
# Triangle inequality in real inner product spaces

For u, v in a real inner product space, the norm of their sum is bounded by
the sum of their norms: |u + v| <= |u| + |v|.

This inequality holds in any normed space; it is certified here for the real
inner-product-space setting (framing A, canonical norm_add_le). The genuinely
inner-product-specific identity is the parallelogram law (see Parallelogram).

Bucket A cert-stream Lean batch (proof 3 of 3) per USER-ratified 6h plan
2026-06-18.
-/

theorem triangle_ip {F : Type*} [NormedAddCommGroup F] [InnerProductSpace ℝ F]
    (u v : F) :
    ‖u + v‖ ≤ ‖u‖ + ‖v‖ := by
  exact norm_add_le u v
