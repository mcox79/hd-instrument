"""Witness for bundle_norm="divnorm" + decode_serial_bank on the DEFAULT (multibank) situation register.

Landed 2026-08-28 from the integrated `the_register_bundle_renorm_breaks_the_serial_readout` (SOLVED/EXCELLENT,
owner-DONE). MultiBankAccumulateRegister is what make_situation_register() returns by DEFAULT, so this completes the
pooled-divisive-norm fix on the default backend (the AccumulateRegister half landed 2026-08-28). Confirms, scaffold-free
on the ACTUAL organ, that an OVERLOADED per-bank bundle normalized with a pooled divisive gain is recovered by the
gain-matched serial readout, where the per-component store is not.

Asserts (deterministic, D=256, V=100):
  1. OVERLOAD (n_banks=1 -> one bank holds M=64 events): divnorm bank recovered by decode_serial_bank >> per-component
     bank (same readout).
  2. POSITIVE CONTROL: the per-component bank CANNOT be recovered even by the gain-matched readout.
  3. INFO-FREE TWIN (divnorm bank, SHUFFLED keys) LOSES.
  4. ARGMAX NO-REGRESSION: decode() (per-slot argmax) on the divnorm bank >= on the per-component bank.
  5. ADDITIVE / default-safe: bundle_norm="percomp" register()/_bank_register() BIT-IDENTICAL to the default (no-arg),
     and a real multi-bank (n_banks=8) default register decodes unchanged.

Run: .venv/Scripts/python.exe verification/test_multibank_divisive_norm_organ.py
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

from hdlab.situation_model_multibank import MultiBankAccumulateRegister  # noqa: E402

D = 256
V = 100
SEED = 20260828


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2**31))


def _build(m: int, seed: int, bundle_norm: str, n_banks: int = 1):
    role_vocab = [f"r{i}" for i in range(V)]
    reg = MultiBankAccumulateRegister(role_vocab, D, _gen(seed), max_event_slots=m, n_banks=n_banks,
                                      bundle_norm=bundle_norm)
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(m)]
    for s in range(m):
        reg.add_event("e", role_vocab[truth[s]], s)
    return reg, [f"r{t}" for t in truth]


def _acc(names, truth):
    return sum(1 for a, b in zip(names, truth) if a == b) / len(truth)


def main() -> int:
    checks = []

    # (1)+(2)+(3) overload: n_banks=1 -> all M=64 events land in bank 0.
    reg_dn, truth = _build(64, SEED, "divnorm", n_banks=1)
    reg_pc, _ = _build(64, SEED, "percomp", n_banks=1)
    s_dn = _acc(reg_dn.decode_serial_bank("e", 0), truth)
    s_pc = _acc(reg_pc.decode_serial_bank("e", 0), truth)
    checks.append((s_dn - s_pc > 0.30, f"[1] OVERLOAD (1 bank, M=64): divnorm {s_dn:.3f} >> per-component {s_pc:.3f} (gap {s_dn - s_pc:+.3f} > 0.30)"))
    checks.append((s_dn > 0.80, f"[1b] divnorm recovers the overloaded bank: {s_dn:.3f} > 0.80"))
    checks.append((s_pc < 0.65, f"[2] POSITIVE CONTROL: per-component bank NOT recoverable by the gain-matched readout: {s_pc:.3f} < 0.65"))

    # twin: manually decode with shuffled keys via the module's decode_serial_pooled_slots on the bank register.
    from hdlab.situation_model_accumulate import decode_serial_pooled_slots
    rr = np.random.default_rng(SEED + 99)
    perm = list(rr.permutation(64))
    trace = reg_dn._bank_register("e", 0)
    role_mat = torch.stack([reg_dn.role_vecs[r] for r in reg_dn.role_vocab], dim=0)
    keys_shuf = [reg_dn.idx_vecs[i] for i in perm]
    est_twin = decode_serial_pooled_slots(trace, keys_shuf, role_mat)
    s_twin = _acc([reg_dn.role_vocab[i] for i in est_twin], truth)
    checks.append((s_dn - s_twin > 0.30, f"[3] INFO-FREE TWIN (shuffled keys) loses: {s_dn:.3f} vs {s_twin:.3f} (gap {s_dn - s_twin:+.3f} > 0.30)"))

    # (4) argmax no-regression (decode() per slot).
    a_dn = _acc([reg_dn.decode("e", s)[0] for s in range(64)], truth)
    a_pc = _acc([reg_pc.decode("e", s)[0] for s in range(64)], truth)
    checks.append((a_dn >= a_pc - 1e-9, f"[4] ARGMAX NO-REGRESSION: divnorm decode() {a_dn:.3f} >= per-component {a_pc:.3f}"))

    # (5a) bundle_norm="percomp" _bank_register BIT-IDENTICAL to default (no-arg).
    reg_default, _ = _build(32, SEED, "percomp", n_banks=1)
    role_vocab = [f"r{i}" for i in range(V)]
    reg_noarg = MultiBankAccumulateRegister(role_vocab, D, _gen(SEED), max_event_slots=32, n_banks=1)
    rr2 = np.random.default_rng(SEED + 1)
    truth32 = [int(rr2.integers(0, V)) for _ in range(32)]
    for s in range(32):
        reg_noarg.add_event("e", role_vocab[truth32[s]], s)
    bit_identical = bool(torch.equal(reg_default._bank_register("e", 0), reg_noarg._bank_register("e", 0)))
    checks.append((bit_identical, f"[5a] ADDITIVE: bundle_norm='percomp' bank BIT-IDENTICAL to default -> {bit_identical}"))

    # (5b) a real multi-bank (n_banks=8) default register decodes unchanged (no crash, correct round-trip at low load).
    reg8, truth8 = _build(8, SEED, "percomp", n_banks=8)
    ok8 = _acc([reg8.decode("e", s)[0] for s in range(8)], truth8) >= 0.99
    checks.append((ok8, f"[5b] ADDITIVE: default n_banks=8 register decode() round-trips at low load ({'OK' if ok8 else 'FAIL'})"))

    print("=== witness: MultiBank bundle_norm='divnorm' + decode_serial_bank (pooled divisive norm on the DEFAULT backend) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} "
          f"({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
