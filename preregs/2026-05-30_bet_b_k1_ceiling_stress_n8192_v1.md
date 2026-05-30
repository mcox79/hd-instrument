# Pre-registration: Bet-B K=1 Ceiling Stress Test N=8192

**Anchor:** bet_b_k1_ceiling_stress_n8192_v1
**Date:** 2026-05-30
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_bet_b_k1_ceiling_stress_n8192_v1.py
**N-suffix binding (PROT-018):** _n8192 -> N_FULL = 8192 in script.

---

## Scientific Context

### Agent 4 Forensic Finding (v272)

Bet B substrate is Fusi-Drew-Abbott K=1 cascade synapse class. K=1 imposes a
THEORETICAL ret_A ceiling of ~0.80 under overwrite stress. 8x convergent
confirmations across v265-v272 anchors.

Key citation: Fusi & Abbott (2007) cascade synapse model. K=1 means a single
synaptic state variable; when a new memory overwrites W positions, the original
memory's representation degrades toward the K=1 retention bound.

### Verdict-Handler Batch (commit 919a901) -- Label-vs-Honest #140

Three rescue architectures from the 2026-05-30 batch:

| Anchor | ret_A | Architecture change |
|--------|-------|---------------------|
| bet_b_cl_wide_phaseA_v1 | 1.000 | Phase A runs at N=8192 (2x capacity) |
| bet_b_cl_frozen_phaseA_v1 | 1.000 | W_A frozen; B/C/D train separate W |
| bet_b_cls_dual_w_smoke | 1.000 | Two W matrices; Phase A memory isolated |

Three independent perfect rescues at ret_A=1.000 is the warning sign. The flag
filed was: ARCHITECTURE_CLASS_SWITCH_MASQUERADING.

All three rescue architectures trivialize the K=1 stress test:
- Wide phase A: Phase A runs at N=8192 (higher-capacity representation) -- not
  a K=1 single-W test.
- Frozen phase A: W_A is frozen after Phase A; Phases B/C/D NEVER overwrite W_A
  -- no overwrite stress.
- Dual-W: two separate weight matrices; Phase A memory stored in dedicated W --
  no overwrite stress.

### The Disambiguation Question

Does ret_A=1.000 in the rescue trio reflect:
  (a) Genuine architecture class change (interesting): these architectures escape
      K=1 by providing Phase A with overwrite protection.
  (b) Test trivialization (uninteresting): the architectures simply avoid exposing
      Phase A to any overwrite -- which means K=1 framework is still intact.

To disambiguate: run the CANONICAL K=1 protocol. Single W, no protection, real
overwrite stress. If ret_A falls below 0.80 under canonical protocol, K=1 ceiling
is respected and rescue trio is genuinely different class (answer a).

---

## K=1 Protocol Mapping

| Stage | Action | K=1 Mechanism |
|-------|--------|---------------|
| Phase A | Store corpus A into W | W encodes corpus A; K=1 synaptic state set |
| Phase B | Add corpus B with A replay; SAME W | W positions partially overwritten; K=1 cascade erodes A |
| Phase C | Add corpus C with A+B replay; SAME W | Further overwrite; more K=1 cascade erosion |
| Phase D | Add corpus D with A+B+C replay; SAME W | Maximum overwrite stress; K=1 ceiling should manifest |

Single W matrix throughout. No width advantage, no freezing, no dual-W. This is
the canonical Fusi-Drew-Abbott K=1 overwrite scenario.

---

## Pre-Registered Thresholds

### HARD_PASS (K=1 ceiling RESPECTED)

    ret_A_after_D < 0.80 in >= 4/5 seeds

**Interpretation:** K=1 ceiling is binding under canonical overwrite stress.
The rescue trio (wide/frozen/dual-W) genuinely changes architecture class --
they escape K=1 by providing overwrite protection to Phase A. This confirms
Agent 4 forensic finding. cap_map action: mark K=1 ceiling row as confirmed.

### HARD_FAIL (K=1 ceiling VIOLATED)

    ret_A_after_D >= 0.95 in >= 4/5 seeds

**Interpretation:** Substrate maintains high ret_A even under canonical single-W
overwrite stress. Agent 4's Fusi-Drew-Abbott K=1 framework is wrong. Substrate
is NOT K=1 limited -- either the replay mechanism is strong enough to prevent
K=1 cascade, or the synapse class is not K=1 at all.
**Action:** Framework recalculation trigger. Research drill on alternative
synapse models (K>1, continuous-state, or non-cascade).

### MIDDLE_BAND (Partial ceiling)

    0.80 <= ret_A_after_D < 0.95 in >= 3/5 seeds

**Interpretation:** Substrate shows partial K=1 ceiling. Stress is partially
effective. Investigate:
  - Replay fraction (REPLAY_FRAC=0.50 may be too strong; increase stress by
    reducing replay fraction)
  - Phase A epochs (more Phase A training -> stronger initial encoding)
  - Epoch count per phase (B/C/D epochs control overwrite depth)

---

## Formula Self-Tests

1. retention = bpc_baseline / bpc_after_phase (capped at 1.0)
   - Perfect retention: ratio = 1.0
   - Complete forgetting: ratio -> 0.0 (bpc_after_phase >> bpc_baseline)

2. HARD_PASS check: ret_A_vals = [0.70, 0.72, 0.74, 0.68, 0.75]
   - count(< 0.80) = 5 >= 4 -> K1_STRESS_HARD_PASS (VERIFIED in script selftest)

3. HARD_FAIL check: ret_A_vals = [0.96, 0.97, 0.95, 0.98, 0.96]
   - count(>= 0.95) = 5 >= 4 -> K1_STRESS_HARD_FAIL (VERIFIED in script selftest)

4. MIDDLE_BAND check: ret_A_vals = [0.82, 0.85, 0.81, 0.79, 0.90]
   - count(< 0.80) = 1 < 4 (not HARD_PASS)
   - count(>= 0.95) = 0 < 4 (not HARD_FAIL)
   - count(in [0.80, 0.95)) = 4 >= 3 -> K1_STRESS_MIDDLE_BAND (VERIFIED in script selftest)

---

## Smoke Run Result

**Smoke config:** N=1024, 1 seed (seed=17), EPOCHS_SMOKE=1, PHASE_A_EPOCHS_SMOKE=2
**Smoke elapsed:** 71.1s
**Smoke result:**
  - ret_A_after_B = 0.864
  - ret_A_after_C = 0.814
  - ret_A_after_D = 0.840

**Smoke verdict:** K1_STRESS_INCONCLUSIVE (1 seed; bands require >= 3-4 seeds)

**Interpretation:** Smoke ret_A_D = 0.840 is in the middle band, consistent with
K=1 partial ceiling at smoke scale. Progression curve (B=0.864, C=0.814, D=0.840)
shows non-monotone decay -- Phase D slightly recovers from Phase C minimum, which
is expected since Phase D replay includes A+B+C combined. Metrics are non-null,
non-constant, non-sentinel. Instrumentation OK.

**Walk-back gate note:** smoke ret_A_D = 0.840 is within 5% of HARD_PASS threshold
(0.80). However, FULL run uses N=8192 (8x larger) + 5 seeds, which provides
sufficient statistical power. Doubling to N=16384 would be a different anchor;
the 5-seed N=8192 FULL is the appropriate resolution for this disambiguation.

---

## Timeout Estimate

Smoke elapsed: 71.1s (N=1024, 1 seed)
Formula: timeout = max(PROT019_floor, ceil(1.5 * smoke_s * (N_FULL/N_SMOKE)^1.5 * seeds))
       = max(21600, ceil(1.5 * 71.1 * (8192/1024)^1.5 * 5))
       = max(21600, ceil(1.5 * 71.1 * 8^1.5 * 5))
       = max(21600, ceil(1.5 * 71.1 * 22.627 * 5))
       = max(21600, ceil(12047))
       = max(21600, 12047)
       = 21600s (PROT-019 floor for _n8192)

**timeout_s = 21600** (6 hours; PROT-019 floor applies)
Flag: long run (>2h). Justified by disambiguation importance (label-vs-honest #140).

---

## OOM Pre-Check

- W at N=8192 float32: 8192^2 * 4 = 268MB (single W)
- 2 W snapshots: 536MB
- Pool tensors (4x 1024*8192*4): 128MB
- Total peak: ~700MB. Well under 6GB. Ship allowed.

---

## Justification

Routing: 2026-05-30 verdict_handler batch (commit 919a901) left open:
"does the trio escape K=1 (interesting) or trivialize the test (uninteresting)?"
This anchor is the single required disambiguation experiment.

Priority: HIGH -- resolves the ARCHITECTURE_CLASS_SWITCH_MASQUERADING flag and
determines whether K=1 framework (8x convergent confirmations) holds or fails.
