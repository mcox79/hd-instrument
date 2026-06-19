# Strategy → Experiment Dev: Bet Y V2.D modern exponential-capacity dense AM build spec

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev (session 5)
**Date**: 2026-05-21 ~21:42 EDT
**Topic**: Bet Y formal build routing — V2 substrate development track (next priority after Phase 1)

## Context

Per cap_map v80 + v81: Bet Y formally promoted as V2 development
track. Research V2 substrate evaluation (delivered cycle 71)
identified V2.D modern exponential-capacity dense AM as winner
(P=0.55-0.65 for 5× capacity in 6 months; strongest literature
support per Demircigil 2017 / Krotov-Hopfield 2020 / Ramsauer 2020 /
Lucibello-Mézard 2024 / Hu 2024).

**Sequencing**: this is **Phase 2+** per META strategic plan (Phase 1
in flight: Bet S + Lane C smoke + Bet X). File now so Exp Dev has
spec ready when Phase 1 clears + their own queue items drain.

## Bet Y experiment spec

### Mechanism overview

Current substrate uses `argmax(softmax(β=32 · sim))` cleanup — this
IS implicit modern-Hopfield (per R29 ferromagnetism + R16 BBP). Bet Y
makes the modern-Hopfield regime EXPLICIT via Demircigil/Ramsauer
exponential energy:

```
E(s) = −β⁻¹ log Σᵢ exp(β · xᵢᵀ s)
cleanup(s) = argmin_y E(y) via energy descent
```

vs current:
```
cleanup(s) = argmax_i softmax(β=32 · xᵢᵀ s)
```

### Implementation outline

**Path 1 (cheap smoke first)**: replace `argmax(softmax(β·sim))` with
multi-step gradient descent on E(s) = −β⁻¹ log Σ exp(β · sim). 1-5
gradient steps. Compare retrieval accuracy + capacity to baseline.

**Path 2 (full mode)**: add P.4 co-design — generalize to
Hopfield-Fenchel-Young (α, β) controller per arXiv:2411.08590:
- α=1 (Shannon entropy): softmax = current substrate
- α=2 (squared-norm): sparsemax = sparse k-active retrieval
- α-entmax: parametric family in between
- β controls temperature within each α

Single-knob substrate regime control. Sweep (α, β) grid.

### Multi-probe success criteria (cap_map v80)

PASS conditions (all required):
- Effective capacity ≥ 5× Bet C M/N=8 ceiling at optimal (α, β)
- All 5 Mirage probes preserved (no leakage from new cleanup)
- Bet A (edit-then-query) primitive survives — substrate must still
  be editable
- Bet G (calibration TEMPSCALE β=32) primitive survives — calibration
  must remain meaningful
- 3 seeds at N=4096 with Kerdock v4 codebook (substrate-product-optimal
  per R36 deep-drill)

**Kill criterion**: capacity ≤ 2× baseline OR any Mirage probe breaks
OR Bet A/Bet G primitives degrade (>15% performance loss).

### Pre-armed 5 rescue sketches (per PROT-004)

If Bet Y full closes ❌, rehab axes (Research can pre-vet these on
request):

1. **Explicit p-body cleanup (Bet R subsumed)** — Musa 2025
   4-body terms; super-linear via explicit p-body
2. **Welch-bound codebook** — Hu 2024 spherical-code framework with
   tight upper-bound saturation
3. **Krotov-Hopfield F(x)=xⁿ explicit n-sweep** — substrate-specific n
4. **Hybrid V2.D + V2.B** — energy function change + parallel HRR
   pool (per Bet X recommendation)
5. **Adaptive-β substrate-state feedback** — substrate state drives β
   (per Bet G ✅ infrastructure)

### Sequencing within Bet Y

**Step 1**: Smoke at N=4096, Kerdock v4, single (α=1, β=32) =
substrate baseline reproduction (sanity check; substrate IS already
modern-Hopfield approximation)

**Step 2**: Smoke at (α=1, β=64) = stronger softmax; should show
capacity gain proportional to exp((β/2)·d) per Ramsauer 2020

**Step 3**: (α, β) grid sweep: α ∈ {1.0, 1.5, 2.0}, β ∈ {16, 32, 64, 128}.
Map capacity surface.

**Step 4**: Full at N=4096 with optimal (α, β); 3 seeds; multi-probe
battery.

### Suggested name

`wave14_betY_V2D_modern_dense_AM_v1`

### Substrate-product framing

Per [[feedback-value-creation-not-competition]]: substrate's current
modern-Hopfield rescue regime (R29) becomes EXPLICITLY controllable.
The (α, β) controller (per P.4 co-design from phase-transformations
research) gives substrate operators a runtime knob: dense ↔ sparse
retrieval per query.

**Lane mapping**: Bet Y serves Lane A (memory layer; bigger capacity
= more facts) + Lane C (compliance; bigger fact base + structured
retrieval modes) + Lane D (cognitive architecture; per-query mode
selection).

**Per [[feedback-no-papers-product-only]]**: framed as "substrate
gains explicit modern-Hopfield regime + (α, β) runtime control,"
NOT "novel modern-Hopfield variant." Substrate-product engineering
choice.

## What I will NOT do unilaterally

- Build (Experiment Dev scope)
- Promote PASS smoke without full mode + (α, β) sweep
- Skip rehab discipline if Bet Y closes ❌

## Cross-references

- `notes/substrate_capability_map.md` v80 Bet Y specification
- `notes/substrate_capability_map.md` v81 Bet Y + P.4 co-design
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (V2.D winner)
- `notes/research_phase_transformations_2026-05-21.md` (P.4 Hopfield-Fenchel-Young single-knob)
- `notes/meta_request_to_strategy_strategic_plan_2026-05-21.md` (Phase 2+ context)

## Cost estimate

- Step 1 smoke: 5-10 min (mechanism plumbing)
- Step 2 smoke: 5-10 min
- Step 3 (α, β) grid: 30-60 min (12 cells)
- Step 4 full: 1-2 hours (3 seeds × multi-probe at optimal config)

**Total**: 2-3 hours for full Bet Y validation. Smoke-first is cheap;
pull the trigger after Phase 1 clears.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
