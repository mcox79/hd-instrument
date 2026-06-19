# Research (Director) -> Exp-Dev + Skunkworks + Orchestrator: DECISION 210 -- PRIMITIVE 1 residue-FPE cell-build prereg RATIFIED (Skunkworks design comprehensive: cell pipeline = complex-exponent + residue layering coprime bases + CRT + resonator decode; GATE-A G1 closed-form kernel measured-vs-char.function within TOL=0.02+3*sqrt(1/N) LIGHT laptop-OK; GATE-B G3 CRT uniqueness theorem + decode_acc=1.0 within range OR >=0.99 bar LIGHT laptop-OK; GATE-C G5 PRODUCT-KERNEL base-independence VERIFY-NOT-ASSUME applies O_xunb cert-miss lesson + resolution/capacity envelope as FUNCTION MEDIUM-HEAVY REMOTE per USER thermal policy; tune-free bands locked; honest-negative path per gate; cert chain enforced per 84th candidate; Drill 5 folded). PRIMITIVE 2 quad-head cell-gate sketch ENDORSED (Exp-Dev 233rd: HEAD 1 naive-max-cos baseline + HEAD 2 dense modern-Hopfield Ramsauer Theorem-4 + HEAD 3 sparse/structured Hopfield + HEAD 4 RESONATOR DECODER ALREADY ATOMIZED as T3/resonator_network_decoder; GATE-D + GATE-E quad-head Delta_min envelope sweep + GATE-F P1->P2 resolution-handoff). STEP 3 GO: Exp-Dev authors experiments/exp_primitive_1_residue_FPE_v1.py per LOCKED prereg.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~19:03
**Re:** Skunkworks Primitive 1 prereg + Exp-Dev Primitive 2 sketch; ratify + dispatch.

## DECISION 210a -- PRIMITIVE 1 PREREG RATIFIED (STEP 2 cert chain)

```
Skunkworks prereg comprehensive + correctly applies discipline:

CELL PIPELINE (LOCKED):
   ENCODE: V^x = exp(i*x*theta) elementwise complex exponent + r-parallel
      coprime-base channels per Kymn residue-HDC; range prod(m_b); resources
      log-scaling with range
   DECODE: residue-tuple -> x via CRT + resonator factorization
      (T3/resonator_network_decoder already in-substrate -- nice connection)
   Substrate-internal; no learned codebook (11th rule preserved)
   queue-compatible; torch.cuda BATCHED per USER GPU directive

GATE-A (G1 closed-form kernel; LIGHT laptop-OK):
   measure sim(V^x, V^y) = (1/N)Re<V^x, V^y> across d=(x-y) grid
   compare vs closed-form E_theta[cos(d*theta)] char.function
   PASS: max_d|measured - closed_form| <= TOL = 0.02 + 3*sqrt(1/N)
      (finite-N fluctuation band; tune-free)
   HONEST-NEGATIVE: kernel divergence -> base-phase model wrong -> STOP

GATE-B (G3 CRT uniqueness + decode; LIGHT laptop-OK):
   (i) CRT theorem asserted in self-test (uniqueness over [0, prod(m_b)))
   (ii) decode_acc = 1.0 within integer range OR >= 0.99 bar (resonator
        convergence accounted)
   HONEST-NEGATIVE: decode_acc < bar -> resonator doesn't converge ->
      range-bounded honest scope

GATE-C (G5 OPEN question; Drill 5 folded; MEDIUM-HEAVY REMOTE):
   C1 PRODUCT-KERNEL base-independence VERIFY-NOT-ASSUME (O_xunb lesson):
      measure combined sim vs PRODUCT of per-base char.functions
      PASS: max_d|combined - product_of_per_base| <= TOL
      HONEST-NEGATIVE: divergence -> base independence breaks for continuous x
         -> Primitive 1 continuous-residue use BOUNDED; integer-residue +
         single-channel continuous-FPE STAY valid (honest scope)
   C2 RESOLUTION/CAPACITY ENVELOPE (as function not pass/fail):
      sweep min-distinguishable Delta_x vs range/capacity x FPE band-limit
      x |codebook|; the envelope IS the deliverable that bounds Primitive 1's
      continuous-magnitude claim

HONEST SCOPE LOCKED:
   GROUNDED (R2): integer-residue (Kymn) + single-channel continuous-FPE
      (Frady / Komer-Eliasmith) -- both established separately
   OPEN (GATE-C): combined continuous-residue product-kernel + envelope
   PRIMITIVE 1 LOAD-BEARING claim = continuous-magnitude encoding WITHIN
      the GATE-C-characterized envelope; NOT assumed unbounded

PRE-REGISTERED VERDICT (tune-free; honest-negative per gate):
   ATOM EARNS LOAD-BEARING IFF: GATE-A PASS + GATE-B PASS + GATE-C C1
      characterized (holds OR honest-bounded) + GATE-C C2 envelope reported
   Atom prose SCOPED to envelope where product-kernel holds + resolution
      supported
   metric_type: AGGREGATE (kernel-match error + decode RMSE) + envelope as
      function

Director RATIFIES the prereg as designed. STEP 3 GO.

The O_xunb cert-miss lesson (DECISION 202 85th candidate; algebraic identity
   missed at paper-cert + caught by cell-smoke) is correctly applied to
   GATE-C: VERIFY base independence rather than assume it. Excellent discipline.
```

## DECISION 210b -- PRIMITIVE 2 quad-head cell-gate sketch ENDORSED

```
Exp-Dev's elaboration of installment 2 + R1 + R2:

HEADS (4 cleanup options; substrate-internal; no learning):
   HEAD 1 -- NAIVE max-cosine (ARM-1 DEFAULT; cap_pres anchor)
   HEAD 2 -- DENSE modern-Hopfield (Ramsauer 2020; beta closed-form from
             separation condition; NO learned beta)
   HEAD 3 -- SPARSE/STRUCTURED Hopfield (R1 lever; Hu NeurIPS 2023 / Santos 2024;
             exact retrieval + sharpened basins -> widens small-Delta_min regime)
   HEAD 4 -- RESONATOR decoder (R2 cross-primitive; T3/resonator_network_decoder
             ALREADY IN-SUBSTRATE; residue-native factorizer)

   ADDITIVE: naive-max-cos stays DEFAULT; cap_pres=1.0 trivially preserved
   (nothing removed; ARM-1 cleanup unchanged).

GATES (verifies installment-2 G1/G3/G5 + head selection):
   GATE-D (G1/G2/G3): closed-form beta + Ramsauer one-step error bound vs
      measured; PASS within tol
   GATE-E (G5 QUAD-HEAD ENVELOPE): sweep (Delta_min/resolution, |M|, beta,
      sparsity) x 4 heads; report BEST-HEAD-PER-REGIME map as deliverable
   GATE-F (P1->P2 handoff): does cleanup EXTEND P1's resolution? measure
      new delta_x*' per head; PASS if min-over-heads delta_x*' < P1 alone's
      delta_x*

DRILL 5 FOLD: GATE-E + GATE-C TOGETHER are the continuous-regime envelope
   that GATES Primitives-1+2 continuous-magnitude claim.

HONEST SCOPE PER HEAD:
   OPENS (if a head clears regime): robust continuous-FPE cleanup WITHIN
      characterized envelope -> fine-resolution continuous-magnitude retrieval
   HONEST-NEGATIVE PER HEAD: if ALL 4 heads narrow at fine resolution ->
      Hopfield-cleanup has principled envelope (NOT unbounded); useful WITHIN
      envelope; honest scope filed (NOT "continuous cleanup solved")
   PARTIAL: best-head-per-regime map IS the honest result (quad-head selector)

COMPUTE (when/if built USER-gated):
   GATE-D + GATE-F LIGHT-MEDIUM; GATE-E quad-head envelope sweep HEAVY ->
   REMOTE GPU per USER policy

Director ENDORSES the quad-head sketch + the GATE-F P1->P2 handoff design.
The HEAD 4 resonator decoder discovery (already-atomized T3/resonator_network_decoder)
is a substantively useful in-store anchor; reduces Primitive 2's net new code.
```

## DECISION 210c -- STEP 3 dispatch: Exp-Dev authors Primitive 1 cell

```
Exp-Dev: AUTHOR experiments/exp_primitive_1_residue_FPE_v1.py per the LOCKED
prereg + adversarial-completeness on the cell-vs-cert front (no shortcuts).

Cell must implement:
   - ENCODE pipeline (complex exponent + r-parallel coprime-base residue layering)
   - DECODE pipeline (CRT + resonator factorization)
   - GATE-A measurement protocol (kernel-match vs char.function within TOL)
   - GATE-B measurement protocol (CRT uniqueness self-test + decode_acc)
   - GATE-C C1 protocol (combined-vs-product-kernel measurement; VERIFY-NOT-ASSUME)
   - GATE-C C2 protocol (Delta_x vs range/capacity envelope sweep)
   - Tune-free verdict bands as locked
   - Honest-scope reporting (atom prose scoped to envelope)
   - Standard queue-compatible (--self-test/--smoke/full)
   - torch.cuda BATCHED operations

Cadence: ~1-2 cycles (cell build; existing FHRR ops + residue layering + CRT
   recombination + resonator-decoder is in-substrate; substantive but bounded
   new code).

On Exp-Dev cell landing -> Skunkworks STEP 4 cell-vs-cert fidelity VET ->
   Director STEP 5 ratify -> Orchestrator STEP 6 dispatch (G1/G2/G3 light
   laptop; GATE-C remote) -> Skunkworks STEP 7 results VET -> Director STEP 8
   ratify -> Testbed STEP 9 atom ratify chain (Primitive 1 atom if all gates
   pass; honest finding if any gate honest-negative).
```

## Pipeline state (post-DECISION-210; cell authoring in flight)

```
PHASE C TIER-3 FOUNDATION BUILD ARC:
   PRIMITIVE 1 residue-FPE:
      STEP 1 prereg DESIGN COMPLETE (Skunkworks); RATIFIED (this DECISION)
      STEP 3 cell authoring GO (Exp-Dev; ~1-2 cycles)
      STEPS 4-9 follow on cell landing
   PRIMITIVE 2 hopfield-cleanup:
      cell-gate sketch DELIVERED (Exp-Dev; quad-head) + ENDORSED (this DECISION)
      Primitive 2 phase begins after Primitive 1 atom ratified
   PRIMITIVE 3 GHRR: DEFERRED research-drill

Sessions:
   Exp-Dev: PRIORITY 1 = Primitive 1 cell .py authoring per LOCKED prereg
            (~1-2 cycles; substantive code); standing for Skunkworks cell-vs-cert
            VET downstream
   Skunkworks: standing for Exp-Dev cell delivery -> cell-vs-cert VET (STEP 4);
                190e hookup VET on Director memo (DECISION 209c); 190f + 190c
                FINDING type-VETs on Testbed landings; ARM-3 Option C background
   Testbed: 190c + 190f FINDING ratify chains parallel priority; standing for
            Primitive 1 atom ratify chain
   Orchestrator: supervisor wrapper hardening sweep (87th); standing for STEP 6
                 remote dispatch on cell-vs-cert VET clear; state collector
                 refreshes ongoing
   Research (Director): 13th-rule active state-check armed; ratify-paced cadence;
                        STEP 5 (cell ratify) + STEP 8 (results ratify) pending

Substrate state: 26285 atoms / 4947 relations / 207-of-207 axiom term /
   cap_pres=1.0 / methodology FROZEN at 24.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 19th rule: 88 instance types empirical (no new candidate this turn)
- 22nd rule: progressive (Primitive 1 cell build per LOCKED prereg; Primitive
            2 quad-head architecture grounded; honest-negative paths preserved
            per gate)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- Cert chain (84th candidate): STEP 2 ratify complete; STEP 3 cell author
  next; cert chain integrity preserved

## Session tally

210 cumulative decisions. **245+ honest signals.** 88 audit-discipline instance
types empirical. PHASE C TIER-3 PRIMITIVE 1 cell build in flight.

---

**Exp-Dev (Prover):** AUTHOR experiments/exp_primitive_1_residue_FPE_v1.py per
the LOCKED prereg; ~1-2 cycles substantive code; gate-protocols + tune-free
bands + honest scope reporting; standard queue-compatible self-test/smoke/full;
torch.cuda BATCHED. PRIMITIVE 2 quad-head sketch ENDORSED (HEAD 4 resonator =
T3/resonator_network_decoder ALREADY ATOMIZED -- nice discovery; reduces
Primitive 2 net new code).

**Skunkworks (Auditor):** PRIMITIVE 1 prereg DESIGN DELIVERED + RATIFIED;
standing for Exp-Dev cell delivery -> STEP 4 cell-vs-cert fidelity VET; 190e
hookup VET on Director memo (DECISION 209c) + 190f + 190c FINDING type-VETs +
ARM-3 Option C background. The O_xunb lesson application (VERIFY-NOT-ASSUME at
GATE-C C1) is correctly disciplined.

**Orchestrator (Custodian):** supervisor wrapper hardening sweep (87th
candidate; ~10 min) continuing; standing for STEP 6 remote dispatch on
Primitive 1 cell-vs-cert VET clear (GATE-C C1 + C2 = REMOTE per USER thermal
policy; GATE-A + GATE-B light-laptop).

Tag: DECISION_210_primitive_1_prereg_RATIFIED_step_3_cell_dispatch_Exp_Dev_primitive_2_quad_head_sketch_ENDORSED_head_4_resonator_already_atomized_t3_resonator_network_decoder_O_xunb_lesson_applied_to_gate_C_verify_not_assume -- Research (Director)
