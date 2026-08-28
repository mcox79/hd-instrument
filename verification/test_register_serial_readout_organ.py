"""Witness for the LANDED AccumulateRegister.decode_serial theta-gamma serial-readout organ.

Landed 2026-08-28 from the integrated `the_register_reads_by_argmax_not_recurrent_completion`
(SOLVED/EXCELLENT, owner-DONE). Confirms, scaffold-free on the ACTUAL hdlab organ, the mechanism the
experiment measured (experiments/exp_register_completion_readout_v1.py): on ONE overloaded entity the
raw-linear-sum SERIAL decode-and-suppress recovers capacity that the register's per-slot argmax cleanup
loses to crosstalk, while an info-free shuffled-key twin does NOT.

Asserts (deterministic, D=256, V=100):
  1. OVERLOAD M=64: serial >> argmax (a large CI-free gap) -- the +0.454 mechanism reproduced on the organ.
  2. INFO-FREE TWIN (serial with SHUFFLED keys) LOSES badly -> the gain is known-key crosstalk cancellation,
     not generic completion.
  3. LOW LOAD M=4: serial does NOT regress the easy case (both high).
  4. ADDITIVE / default-safe: decode() (the per-slot argmax path) is byte-unchanged (a plain 1-event decode
     still round-trips exactly).

Run: .venv/Scripts/python.exe verification/test_register_serial_readout_organ.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402

D = 256
V = 100          # role vocabulary; chance = 1/V = 0.01
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _one_entity_acc(m: int, seed: int):
    """Build ONE entity with m events (role truth[s] bound at event-slot s) on the ACTUAL organ; return
    per-slot accuracy for: the organ's decode() argmax (reads the renorm register) and decode_serial (raw sum),
    plus a shuffled-key serial twin."""
    role_vocab = [f"r{i}" for i in range(V)]
    reg = AccumulateRegister(role_vocab, D, _gen(seed), max_event_slots=m)
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(m)]
    ent = "e"
    for s in range(m):
        reg.add_event(ent, role_vocab[truth[s]], s)

    # argmax arm: the organ's existing per-slot decode() (reads register() = the renorm bundle).
    argmax_hits = sum(1 for s in range(m) if reg.decode(ent, s)[0] == role_vocab[truth[s]])

    # serial arm: the new organ method on the raw linear sum.
    serial_names = reg.decode_serial(ent)
    serial_hits = sum(1 for s in range(m) if serial_names[s] == role_vocab[truth[s]])

    # info-free twin: serial with SHUFFLED event-slot keys (decode using the wrong keys) -> destroys the
    # known-key crosstalk cancellation while keeping the identical trace + algebra.
    perm = list(rr.permutation(m))
    twin_names = reg.decode_serial(ent, event_idxs=perm)
    twin_hits = sum(1 for s in range(m) if twin_names[s] == role_vocab[truth[s]])

    return argmax_hits / m, serial_hits / m, twin_hits / m


def main() -> int:
    checks = []

    # (1)+(2) overload M=64: serial >> argmax; twin loses.
    a64, s64, t64 = _one_entity_acc(64, SEED)
    checks.append((s64 - a64 > 0.20, f"[1] OVERLOAD M=64: serial {s64:.3f} >> argmax {a64:.3f} (gap {s64 - a64:+.3f} > 0.20)"))
    checks.append((s64 > 0.80, f"[1b] serial recovers overload: {s64:.3f} > 0.80"))
    checks.append((a64 < 0.70, f"[1c] argmax collapses at overload: {a64:.3f} < 0.70 (the readout artifact)"))
    checks.append((s64 - t64 > 0.30, f"[2] INFO-FREE TWIN (shuffled keys) loses: serial {s64:.3f} vs twin {t64:.3f} (gap {s64 - t64:+.3f} > 0.30)"))

    # (3) low load M=4: serial does not regress the easy case.
    a4, s4, _t4 = _one_entity_acc(4, SEED)
    checks.append((s4 >= 0.99 and a4 >= 0.99, f"[3] LOW LOAD M=4: serial {s4:.3f} & argmax {a4:.3f} both ~1.0 (no regression)"))

    # (4) additive / default-safe: a plain 1-event decode still round-trips (decode() unchanged).
    reg = AccumulateRegister(["A", "B", "C"], D, _gen(SEED), max_event_slots=3)
    reg.add_event("x", "B", 1)
    ok_decode = reg.decode("x", 1)[0] == "B"
    checks.append((ok_decode, f"[4] ADDITIVE: decode() 1-event round-trip unchanged -> {reg.decode('x', 1)[0]!r} == 'B'"))

    print("=== witness: AccumulateRegister.decode_serial (theta-gamma serial readout organ) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} "
          f"({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
