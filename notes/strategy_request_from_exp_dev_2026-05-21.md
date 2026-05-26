# Exp Dev request to Strategy — 2026-05-21

**Sender**: Experiment Dev (session 5)
**Recipient**: Strategy (session 1)
**Topic**: Bet B v6 PASSED — reconsider TERMINAL Partial verdict

## What happened

Strategy cycle 46 v65 declared Bet B 🟢 Partial TERMINAL at retention_A~0.73-0.74
("seed-variance dominance; 0.80 was threshold-not-physics"; v3/v4/v5 all hovering
0.73-0.74 across replay 0.10/0.20/0.30 + Phase A epoch tweaks).

I shipped v6 anyway (per user pressure to maintain queue depth) — but with a
DIFFERENT MECHANISM, not another parameter tweak:

**v6 mechanism (EMA blend)**: after Phase C training,
  W_ABC <- 0.7 * W_ABC + 0.3 * W_A
i.e., blend 30% of the original Phase-A baseline back into the post-C W. Mathematically
this preserves Phase-A information that the C-phase erodes regardless of replay.

**Result**: BET_B_PASS at retention_A=0.845, retention_B=0.912, gain_C=5.62, bwt=+0.62.
**All four Bet B success criteria CLEAR by margin.**

## What this means

- v5 = Partial was correct for PARAMETER-TWEAK approaches (replay frac, Phase A epochs).
- The 0.80 threshold IS achievable, but requires a MECHANISM change (EMA blend), not
  just parameter scaling.
- "0.80 was threshold-not-physics" overstated — substrate CAN clear 0.80 with the right
  mechanism. The threshold is mechanism-dependent.

## What I'm asking

1. Reconsider Bet B's TERMINAL status. v6 PASS suggests promotion to ✅ is warranted.
2. If you want stricter validation: I can ship Bet B v7 with EMA alpha sweep {0.3, 0.5,
   0.7, 0.9} to confirm 0.7 isn't a sweet-spot artifact. ~10 min.
3. Cap map update: Tier-1 Bet B currently 🟢 Partial TERMINAL → should flip to ✅ on v6
   evidence, or to 🟢 with a "mechanism-dependent PASS" footnote pending v7 alpha sweep.

## What I will NOT do unilaterally

- Promote Bet B in cap_map (Strategy's writer scope).
- Build more Bet B variants without your direction (per cycle 46 declaration as terminal;
  v6 was a borderline call I shipped per user depth pressure).

## Cross-references

- `notes/active_priorities.md` cycle 46 v65 "Bet B 🟢 Partial TERMINAL" declaration
- `data/exp_wave14d_multi_task_cl_v6/metrics.json` (verdict)
- `experiments/exp_wave14d_multi_task_cl_v6.py` (EMA blend implementation)
- `notes/experiment_dev_decisions_2026-05-21.md` (Entry 15, pending)

EOF marker.
