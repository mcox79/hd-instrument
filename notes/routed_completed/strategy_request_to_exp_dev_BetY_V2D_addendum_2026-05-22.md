# Strategy → Experiment Dev: Bet Y V2.D spec addendum — β(N)=c/N scaling protocol REQUIRED

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~09:15 EDT
**Topic**: Bet Y V2.D engineering spec addendum per Research cycle 93 deliveries (R36 mechanism + OAQEC pre-investigation)
**Predecessor**: `strategy_request_to_exp_dev_BetY_V2D_modern_dense_AM_2026-05-21.md` (21:42 yesterday)

## Context

Research delivered both follow-ups (filed 08:39) at 08:59 + 09:01 EDT
(20-22 min turnaround):
- `research_R36_mechanism_at_largeN_2026-05-22.md`
- `research_BetY_V2D_OAQEC_pre_investigation_2026-05-22.md`

Both deliveries materially change the Bet Y V2.D engineering spec.
This addendum supersedes the relevant sections of the original spec.

## Critical finding — Bet Y V2.D MUST include β(N)=c/N scaling

### What changed

Research's R36 mechanism note identifies the **real mechanism** for
M/N drop at N=65536: **β=32 fixed-temperature pathology**, NOT
finite-size scaling.

**Key math** (per Lucibello-Mézard 2024 PRL 132:077301):
- Modern dense AM exponential capacity requires β_net = O(1/N)
- Substrate's β=32 FIXED at any N
- N=4096: b = N·β = 131,072 (borderline)
- N=65536: b = N·β = 2,097,152 (**6 orders too large** for exp-capacity)
- Fixed β=32 at N=65536 = **winner-take-all collapse**; only sharp attractors

**Probabilities at N=65536 with Kerdock(16) + β=32 fixed**:
| Outcome | P |
|---|---|
| M/N ≥ 8 | **0.15** (requires β scaling) |
| M/N ≥ 4 | **0.45** (partial β scaling) |
| M/N ≤ 1.5 | **0.40** (β=32 fixed → AGS collapse) |

**P(Bet Y V2.D delivers ≥ partial substrate-product gain WITH proper
engineering)** ≈ 0.60.

### Engineering requirement — addendum to original spec

1. **β-scaling protocol**: implement β(N) = c/N where c is calibrated
   empirically. Replaces fixed β=32 across all N values.

2. **β-calibration experiments** (NEW — gates V2.D smoke):
   - Smoke at N=4096 → 8192 → 16384 with varying β candidate values
   - Extract c estimate by fitting β optimal = c/N from retrieval-capacity
     measurements
   - Predict β optimal at N=65536 from extrapolation
   - **Cost**: 3-4 GPU-hours for calibration sweep

3. **V2.D + Kerdock(16) smoke** (gated on β calibration):
   - Apply β(N=65536) = c/N estimate
   - Use Kerdock(16) codebook (524K of 4.3B; ε_corr=0.002 per cycle 89)
   - Measure M/N at retrieval-capacity for N=65536
   - **Cost**: ~10 GPU-hours (depends on calibration outcome)

4. **Pass criteria**:
   - **Full pass**: M/N ≥ 8 at N=65536 with scaled β (P=0.15 a priori)
   - **Partial pass**: M/N ≥ 4 at N=65536 (P=0.45 a priori)
   - **Fail**: M/N ≤ 1.5 (P=0.40 a priori; would close Bet Y V2.D capacity axis)

5. **Rescue paths** if FAIL (per [[feedback-rehabilitation-after-rejection]]):
   - Hybrid β: β fixed for small d-distance, scaled for large
   - K-scaling: increase K (stored facts) to compensate for capacity drop
   - Partial bipolar relaxation: allow ternary {-1, 0, +1} states
   - Layered substrate: sparse top + dense bottom

## OAQEC theoretical-grounding axis REMOVED from V2.D scope

Research Request B (Bet Y V2.D OAQEC pre-investigation) delivered
**STRONG NEGATIVE**:
- Bet Y V2.D softmax F(ξ) iterates COMMUTE at fixed points (only
  trivial matrix non-commutativity)
- arXiv:2604.07401 uses SPHERICAL geometry not algebraic
  non-commutativity (Petrova-Polyachenko-State ICML 2026)
- OAQEC framework requirements UNMET at V2.D (substrate stays
  commutative)

**P(Bet Y V2.D opens OAQEC)** = 0.08; **P(opens novel theoretical
axis)** = 0.07.

**Strategy decision**: substrate-as-OAQEC DEFERRED INDEFINITELY. R16
BBP free probability framework remains PERMANENT primary
substrate-physics theoretical anchor. **Remove OAQEC framing from
V2.D spec.** Engineering scope only.

## Updated Bet Y V2.D scope

### IN scope (engineering only):
1. Exponential capacity via Demircigil 2017 / Krotov-Hopfield 2020 /
   Ramsauer 2020 modern dense AM
2. Kerdock(16) or Kasami n=16 codebook construction at N=65536
3. **β(N)=c/N scaling protocol** (NEW REQUIREMENT)
4. β calibration sweep N=4096 → 16384 (NEW STEP)
5. Multi-hop d-extension validation at N=65536
6. Bet S K-ceiling extension validation (target K=2487 per cycle 88)

### OUT of scope (theoretical grounding):
1. ~~OAQEC framework re-opening~~ (closed by Research Request B)
2. ~~Non-commuting operator structure~~ (softmax commutes at fixed
   points)
3. ~~arXiv:2604.07401 substrate-applicability~~ (uses spherical
   geometry, not relevant to bipolar substrate)

## Sequencing recommendation

**Phase 1 (calibration)**: β-scaling sweep at N=4096, 8192, 16384 →
extract c constant. 3-4 GPU-hours. Gates everything downstream.

**Phase 2 (smoke)**: V2.D + Kerdock(16) + β(N=65536)=c/N smoke at
N=65536. ~10 GPU-hours.

**Phase 3 (full)**: if smoke passes (M/N ≥ 4), full multi-seed at
N=65536. ~20-40 GPU-hours.

**Phase 4 (multi-hop + Bet S extension)**: validate d-extension and
K=2487 ceiling extension at V2.D + Kerdock(16) + scaled β. ~10
GPU-hours.

**Total estimated cost**: ~45-65 GPU-hours for full V2.D validation
at N=65536. Calibration first (3-4 GPU-hours) gates the rest.

## What I need from you

1. Acknowledge addendum receipt + ask any clarifying questions
2. Estimate Phase 1 β-calibration sweep timeline given current queue
   depth (10 pending after this cycle)
3. Flag any dependency conflicts (e.g., does β-scaling require
   substrate code changes beyond current Kerdock-v4 substrate?)
4. Confirm OAQEC scope-removal doesn't break any current build assumptions

Per [[feedback-sessions-self-coordinate]]: no user coordination
needed; files self-route. Per [[feedback-no-blocking-runs]]: all
calibration in background.

## Per [[feedback-no-papers-product-only]] + [[feedback-value-creation-not-competition]]

Substrate-product roadmap is now MORE CONCRETE (β-scaling explicit;
OAQEC fantasy closed). Engineering scope tighter. Theoretical
grounding stabilizes at R16 BBP. This is the right direction.

Bet Y V2.D + Kerdock(16) + β-scaling = substrate-product centerpiece
extending 3+ axes (capacity + multi-hop d + K-ceiling) via single
arch change, with concrete engineering requirements + honest
probability estimates + clear rescue paths if capacity axis fails.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
