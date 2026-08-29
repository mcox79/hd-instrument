"""Scaffold-free witness for the_register_write_path_has_a_hard_capacity_wall.

Asserts the load-bearing claims without the full sweep:

  WRITE PATH (exp_register_leaky_write_capacity_v1):
  1. CAPACITY LIFT over the STRONGEST floor: at overload (N=192, D=256) the write-time leaky/recency gain
     recovers the RECENT events where the flat sum collapses BOTH under argmax AND under the landed serial
     crosstalk-cancellation readout (decode_serial) -- the strong floor, not a strawman.
  2. THE FUNDAMENTAL TRADE: the leaky write buys recent recovery by DECAYING OLD events (uniform recovery
     collapses) -> a second store is genuinely needed (not an artifact).
  3. INFO-FREE TWIN (shuffled keys) collapses to chance.
  4. FORM FIDELITY: the leaky recency curve is GRADED/monotonic (the primate 66/45/39 gradient shape,
     newest>middle>oldest), where a hard bounded QUEUE is a STEP.
  5. POSITIVE CONTROL moves (leaky recovers the newest event at high load; flat -- argmax or serial -- cannot).

  SECOND STORE (exp_register_salience_gated_handoff):
  6. The salience-gated commit into the REAL HDFactStore recovers salient OLD events the leaky buffer loses,
     and the weighted-OR gate (commit-most-salient) beats the FIFO/eviction-order floor.
  7. The weighted-OR (both U-shape extremes) >= each single channel; the info-free random-commit twin loses.
  8. The SELF-derived gate (on-disk HARD_FAIL negative control) does NOT CI-beat FIFO -- the salience signal
     must come from an INDEPENDENT channel.

Run: .venv/Scripts/python.exe verification/test_register_leaky_write.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import cleanup_argmax, decode_serial_slots  # noqa: E402
from experiments.exp_register_leaky_write_capacity_v1 import (  # noqa: E402
    _write_store, _argmax_decode, _acc_recent, _acc_uniform, graded_vs_step, positive_control, BASE_SEED,
)
from experiments.exp_register_salience_gated_handoff_v1 import (  # noqa: E402
    handoff_sweep, positive_control as handoff_pc,
)
from experiments.exp_register_multitimescale_cascade_v1 import cascade_sweep  # noqa: E402


def main():
    checks = []

    # 1. capacity lift over the STRONG floor (flat+serial), at overload
    n = 192
    Sf, evf, keys, rm, truth = _write_store(n, BASE_SEED, "flat")
    Sl, evl, kl, rml, trl = _write_store(n, BASE_SEED, "leaky", leak=0.25)
    fa = _acc_recent(_argmax_decode(Sf, keys, rm), truth, 4)
    fs = _acc_recent(decode_serial_slots(torch.stack(evf).sum(0), keys, rm, n_iter=6), truth, 4)
    la = _acc_recent(_argmax_decode(Sl, kl, rml), trl, 4)
    checks.append((f"leaky recent-recovery {la:.3f} beats flat+argmax {fa:.3f} AND flat+SERIAL floor {fs:.3f} "
                   f"at overload N={n}", la > fa + 0.3 and la > fs + 0.3))

    # 2. the fundamental trade (old decays -> 2nd store needed)
    lu = _acc_uniform(_argmax_decode(Sl, kl, rml), trl)
    checks.append((f"leaky UNIFORM recovery {lu:.3f} << its recent {la:.3f}: old decays out (2nd store needed)",
                   lu < la - 0.3))

    # 3. info-free twin collapses
    rng = np.random.default_rng(BASE_SEED + 7); perm = list(rng.permutation(n))
    tw = _acc_recent(_argmax_decode(Sl, [kl[p] for p in perm], rml), trl, 4)
    checks.append((f"info-free twin (shuffled keys) collapses {tw:.3f} << leaky {la:.3f}", tw < la - 0.3))

    # 4. FORM fidelity: graded monotonic gradient vs step
    gv = graded_vs_step(n_trials=40)
    lb = gv["leak_3bin_newest_mid_oldest"]; qb = gv["queue_3bin_newest_mid_oldest"]
    checks.append((f"leaky recency curve is GRADED/monotonic (3-bin newest/mid/oldest {lb}) -- the primate "
                   f"66/45/39 shape; queue is a STEP ({qb})",
                   gv["leak_is_graded"] and gv["leak_monotonic_graded"] and gv["queue_is_step"]))

    # 5. positive control (write path)
    pc = positive_control(n_trials=20)
    checks.append((f"positive control moves: leaky recovers newest {pc['leaky_recovers_newest']:.3f} vs "
                   f"flat(argmax|serial) {pc['flat_recovers_newest']:.3f} at N={pc['n']}", pc["moves"]))

    # 6-8. second store
    hs = handoff_sweep(n_trials=20, n_boot=1000)
    arms = hs["arms"]
    checks.append((f"salience-gated store: weighted-OR {arms['OR']['mean']:.3f} beats FIFO/eviction-order floor "
                   f"{arms['FIFO']['mean']:.3f} (commit-most-salient, not oldest-evicted)",
                   arms["OR"]["mean"] > arms["FIFO"]["mean"] + 0.05))
    checks.append((f"weighted-OR (both U-shape extremes) >= each single channel PE {arms['PE']['mean']:.3f} / "
                   f"CONG {arms['CONG']['mean']:.3f}; info-free twin {arms['TWIN']['mean']:.3f} loses",
                   arms["OR"]["mean"] >= arms["PE"]["mean"] - 1e-6
                   and arms["OR"]["mean"] >= arms["CONG"]["mean"] - 1e-6
                   and arms["TWIN"]["mean"] < arms["OR"]["mean"] - 0.05))
    sc = hs["contrasts"]["SELF_minus_FIFO"]
    checks.append((f"SELF-derived gate does NOT CI-beat FIFO (on-disk HARD_FAIL neg-control; salience must be an "
                   f"INDEPENDENT channel): delta {sc['delta']:+.3f} sep={sc['sep']}", not sc["sep"]))
    hpc = handoff_pc(n_trials=20)
    checks.append((f"2nd-store positive control: OR recall {hpc['OR_recall']:.3f} vs leaky-only "
                   f"{hpc['leaky_only_recall']:.3f} -> rescues salient-old", hpc["moves"]))

    # 10-11. FIDELITY DEEPENING: the multi-timescale CASCADE (Fusi/Benna-Fusi) extends the recoverable window
    # ~3x past a single geometric leak, with a graded gradient, WITHOUT sacrificing recent -- but reach stays
    # finite so the 2nd store is still needed (the cascade EXTENDS the buffer, does not replace consolidation).
    cs = cascade_sweep(loads=(256,), n_trials=16, n_boot=800)["rows"]["n=256"]
    checks.append((f"multi-timescale cascade extends the recoverable window CI-separated (reach {cs['cascade_reach']} "
                   f"vs single {cs['single_reach']}; +{cs['cascade_minus_single_window']['delta']} events) without "
                   f"sacrificing recent (cascade recent-4 {cs['cascade_recent4']:.3f})",
                   cs["cascade_reach"] > cs["single_reach"] + 5
                   and cs["cascade_minus_single_window"]["sep"] and cs["cascade_recent4"] > 0.9))
    checks.append((f"cascade reach is FINITE ({cs['cascade_reach']} < 256) -> the salience-gated 2nd store is STILL "
                   f"needed for far-old events (cascade extends the buffer, does not replace consolidation)",
                   cs["cascade_reach"] < 256))

    print()
    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
