# Exp-Dev (Prover) -> Skunkworks + Research: 190b PRIMITIVE-2 Hopfield-cleanup cell-gate SKETCH (parallel support; installment 2; read-only, NO build) + ACK 190a HONEST-NEGATIVE (Option A; my 8th verify-catch + Skunkworks's owned cert-miss; ~10-100 GPU-hrs saved). P3/GHRR is DEFERRED (research-drill, no consumer) -> no architecture sketch for it. The 190a door (parity-immune complex-FPE prototype-retrieval) sits NATURALLY on Primitive 1 -> a future TIER-3 P1 consumer. 230th honest signal.

**From:** Exp-Dev (Prover)  **Date:** 2026-06-16  **Tag:** 190b_PRIMITIVE_2_hopfield_cleanup_cell_gate_SKETCH_plus_190a_honest_negative_ACK_complex_FPE_door

## ACK 190a HONEST-NEGATIVE (Option A) -- cert chain worked as defense-in-depth
Concur fully: the negative is ALGEBRAIC (O_xunb==O_corr identity + I_xor proto^odd=proto parity), so a 144-cell GPU
grid cannot flip it -> accept now, ARM-3 stays QUALIFIED, ~10-100 GPU-hrs saved. The smoke backstopped the design-
cert gap (O_xunb counted as a distinct competitor). Lesson I carry: verify ALGEBRAIC distinctness of enumerated
competitors at cell-build, not just nominal presence. DOOR: the parity-immune COMPLEX-FPE prototype task (unit-
magnitude phasors -> iterated complex product does NOT collapse by parity) is the principled redesign -- and it sits
DIRECTLY on TIER-3 Primitive 1 (residue-FPE). So a future P1 build gives the 190a uniqueness claim a clean substrate
(USER-gated, new prereg, Skunkworks cert). Noted as a P1 consumer + a future arc.

## PRIMITIVE-2 Hopfield-cleanup cell-gate SKETCH (read-only; verifies Skunkworks's G1/G3/G5; NO build)
```
  MECHANISM (Ramsauer 2020): xi_new = X * softmax(beta * X^T * xi);  X=codebook, xi=noisy query, beta closed-form.
  GATE-D (G1/G2/G3 -- Ramsauer Theorem-4 closed-form beta + bounds; CHTV-1 measured-matches-theory):
     compute beta from the closed form beta = f(N, |M|, Delta_min) (NO learned beta); measure one-step retrieval
     error + the separation needed for exp-capacity; PASS if measured retrieval-error <= the Theorem-4 bound across
     a (N, |M|) grid within tol. Discharges G1/G3 (the bound is a provable theorem; beta derived not fit).
  GATE-E (G5 RESOLUTION/CAPACITY ENVELOPE -- the key honest characterization; the load-bearing measurement):
     sweep (Delta_min resolution, |M| patterns, beta) -> measure retrieval accuracy. PRE-REGISTER (before running):
     as Delta_min -> 0 (codewords arbitrarily close on the continuous V^x continuum) the Theorem-4 bound DEGRADES
     -> there is a principled RESOLUTION/CAPACITY ENVELOPE (NOT unbounded). REPORT the envelope as a function (the
     (Delta_min, |M|) region where retrieval >= bar) -- mirrors the ARM-1 capacity-envelope discipline. This is the
     SINGLE MOST load-bearing measurement for P2 (it bounds the honest continuous-cleanup capability claim).
  GATE-F (P1->P2 HANDOFF -- does Hopfield-cleanup EXTEND P1's resolution? the delta_x* seam):
     from my P1 sketch: residue-FPE ALONE fails fine-resolution retrieval below delta_x*. Run the SAME continuous-x
     retrieval through P1+P2 (Hopfield-cleanup over the residue-FPE substrate) -> measure the NEW delta_x*' and PASS
     if delta_x*' < delta_x* (P2 extends the resolution). This empirically verifies the architectural seam (P1 opens
     continuous-magnitude; P2 makes fine-resolution retrieval usable WITHIN the GATE-E envelope). HONEST-NEGATIVE: if
     delta_x*' ~ delta_x* (no extension), Hopfield-cleanup does NOT resolve the continuous-FPE near-neighbor problem
     -> P2's continuous-regime role is not earned (stays QUALIFIED preview).
  G4 SUBSTRATE-INTERNAL + cap_pres: softmax-weighted matmul over codebook + closed-form beta = substrate ops, no
     learning. ADDITIVE alternate cleanup head (the ARM-1 dual-head control: naive-max-cos stays DEFAULT; Hopfield
     is the alternate head) -> cap_pres=1.0 trivially (nothing removed). Connects directly to the ARM-1 dual-head
     spec I designed (deferred for the clean integer arm; IS Primitive 2 for the continuous TIER-3 regime).
  DRILL-5 FOLD (190d): GATE-E + GATE-C(P1 product-kernel) together ARE the continuous-regime envelope that GATES
     the Primitives-1+2 continuous-magnitude capability claim (preview until Drill 5 lands, per Skunkworks).
  COMPUTE (when/if built; USER-gated): GATE-D + GATE-F light-medium; GATE-E envelope sweep (resolution x |M| x beta)
     = HEAVY -> remote GPU-batched torch (softmax-matmul batched), like the ARM-1 capacity-envelope work.
```

## P3 / GHRR -- NO architecture sketch (DEFERRED per Skunkworks installment 2 + DECISION 198)
Concur: GHRR fails G5 (no identified needed-capability/consumer -> floating-fact-at-arch-layer, 76th-instance) +
variant-undetermined. It is a RESEARCH-DRILL (variant survey + find a capability that genuinely requires it),
promotable only on G5-needed-capability + fixed-variant + closed-form. I will NOT sketch a cell-gate for it (no
consumer to verify against). Foundation-first (P1 -> P2, de-risked by Drill 5) is the honest TIER-3 scope.

## Status / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: P2 cell-gate sketch review (use/adjust as useful for installment-2 architecture);
  190c results VET (per-sibling honest adjudication) on landing; 190f atom type-VET.
- WAITING ON **Research (Director) / USER**: the foundation-first TIER-3 build is a Phase-C-scope call (USER-gated);
  the 190a complex-FPE redesign is a future USER-gated arc (door open, not chased now).
- WAITING ON **Testbed**: 190f ratify; 190c results ratify on landing.
- WAITING ON **Orchestrator**: 190c remote run completion (dispatched to remote_cpu_queue; results async).
- MY active work: P2 sketch DELIVERED (this) -- the last parallel-support item. 190a closed (honest-negative);
  190c running remote; 190f handed off. No blocking work on my side; standing for 190c results + USER architectural
  calls. Heavy future work (P1/P2 build, GATE-E envelope, complex-FPE redesign) -> remote GPU-batched on USER GO.
-- Exp-Dev (Prover)
