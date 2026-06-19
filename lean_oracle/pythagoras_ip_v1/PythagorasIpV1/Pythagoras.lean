/-
Copyright (c) 2026 hd-instrument.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import Mathlib.Analysis.InnerProductSpace.Basic

/-!
# Pythagoras in real inner product spaces

For u, v in a real inner product space, if u and v are orthogonal,
then |u + v|^2 = |u|^2 + |v|^2.

PHASE II Lean first proof per Director + Skunkworks consensus 2026-06-17.
-/

theorem pythagoras_ip {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    (u v : V) (h : @inner ℝ V _ u v = 0) :
    ‖u + v‖ ^ 2 = ‖u‖ ^ 2 + ‖v‖ ^ 2 := by
  rw [norm_add_sq_real, h]
  ring
