"""Witness for the LANDED bundle_norm="divnorm" store option + AccumulateRegister.decode_serial_pooled readout.

Landed 2026-08-28 from the integrated `the_register_bundle_renorm_breaks_the_serial_readout` (SOLVED/EXCELLENT,
owner-DONE). Confirms, scaffold-free on the ACTUAL hdlab organ, the mechanism the experiment measured
(experiments/exp_register_divisive_norm_v1.py): swapping the register's per-component bundle renorm for a POOLED
divisive normalization (bundle_norm="divnorm", Carandini-Heeger) -- read by the gain-matched serial readout
(decode_serial_pooled) -- recovers an overloaded register to the raw-sum ceiling, where the per-component store cannot
be recovered even by the same gain-matched readout (the positive control isolating the STORE norm).

Asserts (deterministic, D=256, V=100):
  1. OVERLOAD M=64: divnorm store (pooled readout) RECOVERS >> per-component store (same pooled readout).
  2. POSITIVE CONTROL: the per-component store CANNOT be recovered even by the gain-matched readout (isolates the
     STORE norm, not the readout).
  3. INFO-FREE TWIN (divnorm store, SHUFFLED keys) LOSES badly.
  4. ARGMAX NO-REGRESSION: decode() (per-slot argmax) on the divnorm store >= on the per-component store (scale-invariant).
  5. LOW LOAD M=4: divnorm recovers (no easy-case regression).
  6. ADDITIVE / default-safe: bundle_norm="percomp" register() is BIT-IDENTICAL to the default (no-arg) register().

Run: .venv/Scripts/python.exe verification/test_register_divisive_norm_organ.py
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


def _build(m: int, seed: int, bundle_norm: str):
    """One entity with m events (role truth[s] at slot s) on the organ with the given bundle_norm; SAME codebook +
    truth for any bundle_norm (same seed), so the ONLY variable is the store normalization."""
    role_vocab = [f"r{i}" for i in range(V)]
    reg = AccumulateRegister(role_vocab, D, _gen(seed), max_event_slots=m, bundle_norm=bundle_norm)
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(m)]
    for s in range(m):
        reg.add_event("e", role_vocab[truth[s]], s)
    return reg, [f"r{t}" for t in truth]


def _acc(names, truth):
    return sum(1 for a, b in zip(names, truth) if a == b) / len(truth)


def main() -> int:
    checks = []

    # (1)+(2)+(3) overload M=64.
    reg_dn, truth = _build(64, SEED, "divnorm")
    reg_pc, _ = _build(64, SEED, "percomp")
    s_dn = _acc(reg_dn.decode_serial_pooled("e"), truth)         # divnorm store, gain-matched readout
    s_pc = _acc(reg_pc.decode_serial_pooled("e"), truth)         # per-component store, SAME readout (positive control)
    rr = np.random.default_rng(SEED + 99)
    perm = list(rr.permutation(64))
    s_twin = _acc(reg_dn.decode_serial_pooled("e", event_idxs=perm), truth)
    checks.append((s_dn - s_pc > 0.30, f"[1] OVERLOAD M=64: divnorm store {s_dn:.3f} >> per-component store {s_pc:.3f} (gap {s_dn - s_pc:+.3f} > 0.30)"))
    checks.append((s_dn > 0.80, f"[1b] divnorm recovers overload: {s_dn:.3f} > 0.80"))
    checks.append((s_pc < 0.65, f"[2] POSITIVE CONTROL: per-component store NOT recoverable even by the gain-matched readout: {s_pc:.3f} < 0.65"))
    checks.append((s_dn - s_twin > 0.30, f"[3] INFO-FREE TWIN (shuffled keys) loses: {s_dn:.3f} vs {s_twin:.3f} (gap {s_dn - s_twin:+.3f} > 0.30)"))

    # (4) argmax no-regression (decode() per slot): divnorm >= per-component (scale-invariant).
    a_dn = _acc([reg_dn.decode("e", s)[0] for s in range(64)], truth)
    a_pc = _acc([reg_pc.decode("e", s)[0] for s in range(64)], truth)
    checks.append((a_dn >= a_pc - 1e-9, f"[4] ARGMAX NO-REGRESSION: divnorm decode() {a_dn:.3f} >= per-component {a_pc:.3f}"))

    # (5) low load M=4.
    reg_dn4, truth4 = _build(4, SEED, "divnorm")
    s_dn4 = _acc(reg_dn4.decode_serial_pooled("e"), truth4)
    checks.append((s_dn4 >= 0.99, f"[5] LOW LOAD M=4: divnorm {s_dn4:.3f} ~1.0 (no regression)"))

    # (6) additive / default-safe: bundle_norm="percomp" register() BIT-IDENTICAL to the default (no-arg).
    reg_default, _ = _build(32, SEED, "percomp")               # explicit percomp
    role_vocab = [f"r{i}" for i in range(V)]
    reg_noarg = AccumulateRegister(role_vocab, D, _gen(SEED), max_event_slots=32)   # DEFAULT (no bundle_norm)
    rr2 = np.random.default_rng(SEED + 1)
    truth32 = [int(rr2.integers(0, V)) for _ in range(32)]
    for s in range(32):
        reg_noarg.add_event("e", role_vocab[truth32[s]], s)
    bit_identical = bool(torch.equal(reg_default.register("e"), reg_noarg.register("e")))
    checks.append((bit_identical, f"[6] ADDITIVE: bundle_norm='percomp' register() BIT-IDENTICAL to default -> {bit_identical}"))

    print("=== witness: bundle_norm='divnorm' + AccumulateRegister.decode_serial_pooled (pooled divisive-norm organ) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} "
          f"({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
