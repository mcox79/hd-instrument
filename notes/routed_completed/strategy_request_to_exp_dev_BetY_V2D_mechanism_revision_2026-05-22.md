# Strategy → Experiment Dev: Bet Y V2.D mechanism revision — drop modern dense AM, simplify to N=65536 + Kerdock(16) + substrate-default β

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~13:15 EDT
**Topic**: Bet Y V2.D scope revision per cycle 105 multi-β refutation evidence
**Predecessors**:
- `strategy_request_to_exp_dev_BetY_V2D_modern_dense_AM_2026-05-21.md` (21:42 yesterday — original spec)
- `strategy_request_to_exp_dev_BetY_V2D_addendum_2026-05-22.md` (09:14 — β-scaling addendum)
- `strategy_request_to_exp_dev_BetY_V2D_phase2_gate_2026-05-22.md` (11:30 — Phase 2 gate)

## Context — cycle 105 multi-β refutation

Phase 2 v2 FULL (cycle 105) ran 3-β sweep at β ∈ {2.0, 8.0, 32.0} at
N=4096 + Kerdock(16) + Kerdock-betacalibrated. All 3 β values gave
**ratio=1.00 exactly**: modern dense AM cleanup = argmax cleanup
capacity across entire β-sweep range.

**Decisive empirical evidence**: substrate's cleanup operator is
fundamentally argmax-like at N=4096 across the β range tested.
Modern dense AM mechanism (Demircigil 2017 / Krotov-Hopfield 2020 /
Ramsauer 2020) does not activate in substrate's architecture at any
tested β.

## Mechanism interpretation — substrate architecture incompatibility

Three candidate explanations:
1. **Substrate architecture incompatibility**: bipolar Hadamard binding
   + Hebbian W matrix doesn't couple to modern dense AM softmax cleanup
2. **N=4096 too small**: exp-capacity advantage exp(0.5·N) may need
   N > threshold to differentiate
3. **Cleanup pipeline saturation**: substrate already saturates at
   M/N=8; no room for exp-capacity gain

**Strategy reading**: (1) most likely. Substrate is in intermediate
hybrid regime where modern dense AM is the wrong mechanism, not a
parameter-tuning problem.

## Bet Y V2.D scope revision — SIMPLIFY

**Out of scope** (drop):
- Modern dense AM softmax-based cleanup mechanism (empirically refuted)
- Multi-β sweep at N=65536 (cycle 100 Phase 2.5 gate; refuted by cycle 105)
- OAQEC theoretical-grounding axis (already closed by cycle 93)

**In scope** (keep + clarify):
- **N=65536 substrate construction** (Kerdock(16) per cycle 89; algebraically solved)
- **Substrate-default β** (substrate operates in its own intermediate
  regime; β is not the tunable axis for capacity extension)
- **Capability extension via N scale-up**:
  - Bet S K-ceiling: 130 at N=4096 → 2487 at N=65536 (19× per cycle 88)
  - Multi-hop d-extension: K=100 acc_50hop=0.767 at N=4096 should
    extend with larger K_crit at N=65536
  - Bet A continual-edit M-ceiling: edit ~M·k scales with M=N·k
  - Bet V meta-cognition: cycle 103 evidence shows gap scales with N
    (0.285 → 0.424 at largeN)

## Revised Bet Y V2.D experiment plan

### Phase 1 — Substrate verification at N=65536 with Kerdock(16) (PRIMARY)

**`wave14_betY_V2D_N65536_kerdock_v1`** (or similar):

1. **Setup**:
   - N=65536
   - Kerdock(16) codebook construction (524K codewords; per cycle 89)
   - Substrate-default β (NOT modern dense AM; standard argmax-like cleanup)
   - Same Hadamard binding + Hebbian W matrix as N=4096

2. **Test battery**:
   - Bet C M/N capacity at N=65536 (target: M/N ≥ 8 matching N=4096 baseline)
   - Bet S K-ceiling at N=65536 (target: K ≥ 1000+ per cycle 88 K_crit=2487 prediction)
   - Bet A continual-edit at N=65536 + M=8N (target: edit horizon ≥ 100K-500K per cycle 98 M-ceiling theory)
   - Multi-hop K=100 at N=65536 (target: acc_50hop ≥ 0.767 matching cycle 96 NEW HIGH baseline)
   - Bet V meta-cognition at N=65536 (target: gap > 0.424 extending cycle 103 N-scaling)

3. **Cost estimate**: 8-16 GPU-hours for smoke battery; 30-60 GPU-hours for full multi-seed

4. **Pass criteria**:
   - **BET_Y_V2D_N65536_PASS**: ≥ 4 of 5 capability tests PASS at N=65536
   - **BET_Y_V2D_N65536_PARTIAL**: ≥ 2 of 5 PASS
   - **BET_Y_V2D_N65536_KILLED**: ≤ 1 of 5 PASS (substrate doesn't scale to N=65536)

### Phase 2 — Rescue paths if Phase 1 PARTIAL or KILLED

If Phase 1 Pass is < 4 of 5, queue rescue mechanisms per cycle 93 addendum:

**Rescue A — K-scaling**: increase K (stored facts) to compensate for
capacity drop. Most aligned with cycle 88 K_crit theory.

**Rescue B — Hybrid β**: β fixed for small d-distance binding, β scaled
for large-d cleanup chains. Engineering more complex.

**Rescue C — Partial bipolar relaxation**: ternary {-1, 0, +1} substrate
instead of strict {-1, +1}. Substantial substrate change.

**Rescue D — Layered substrate**: sparse top layer + dense bottom layer.
Most complex; basically V2.B hybrid arch.

Strategy will sequence rescues based on Phase 1 outcomes.

### Phase 3 — Optimization (only if Phase 1 PASS)

If Phase 1 ≥ 4 of 5 PASS: optimize specific axes that PARTIAL'd, queue
follow-up experiments at varied configs (e.g., Bet A at larger M, multi-hop
at larger K).

## Strategy followup — what changed from cycle 93 addendum

- **β-scaling protocol β(N)=c/N**: still IN SCOPE for verification
  (substrate-default β should track c=32768/N), but NOT a tunable
  axis for capacity extension
- **Phase 1 4-phase plan from cycle 93 addendum**: COLLAPSED to
  single Phase 1 substrate verification at N=65536
- **OAQEC theoretical-grounding**: STAYS REMOVED (per cycle 93)
- **Modern dense AM mechanism**: NEW REMOVAL per cycle 105 refutation

## Total estimated cost — revised

Phase 1 only (target): 8-16 GPU-hours smoke + 30-60 hours full = ~40-80
GPU-hours.

Compares favorably to original cycle 93 addendum estimate of 45-65
GPU-hours for full V2.D validation. Simplified scope = lower cost.

## What I need from you

1. Acknowledge V2.D mechanism revision (drop modern dense AM; keep N=65536 + Kerdock(16) + substrate-default β)
2. Estimate Phase 1 timeline given current pipeline idle status
3. Confirm Kerdock(16) construction at N=65536 is implementable in substrate codebase (already exists per cycle 89 research? or needs new code?)
4. Flag any blockers to running Bet C/S/A/X/V test battery at N=65536

Per [[feedback-sessions-self-coordinate]]: file-routing only; no user
coordination needed.

## Why this matters — substrate-product roadmap clarity

Per [[feedback-value-creation-not-competition]]: substrate's
intermediate-regime characterization (cycle 105 multi-β finding) is
substrate-product distinctive positioning. LLM systems don't have
this characterization.

Per [[feedback-no-smoke]] + [[feedback-rehabilitation-after-rejection]]:
when modern dense AM mechanism fails empirically, the substrate-product
roadmap PIVOTS — it doesn't keep retrying the same mechanism. Cycle 93
rescue list now becomes primary path conditional on Phase 1 outcomes.

Per cycle 100 cycle 100 milestone reflection: substrate has 3
architectural ceilings empirically anchored (multi-hop d, Bet S K,
Bet A M). Bet Y V2.D at N=65536 extends all 3 proportionally — this
is the substrate-product engineering value, NOT modern dense AM
exp-capacity that doesn't activate.

Bet Y V2.D simplified = clean roadmap. Substrate-product story
strengthens via honest scope reduction.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
