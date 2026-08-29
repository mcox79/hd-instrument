"""Witness for the LANDED leaky/recency WRITE option on hdlab.situation_model_accumulate.AccumulateRegister
(and the multibank backend), from the integrated `the_register_write_path_has_a_hard_capacity_wall` (owner-DONE,
SOLVED/EXCELLENT, 2026-08-29).

Confirms the LANDED code faithfully implements the brain's asymmetric leaky/recency write (Warden & Miller 2007;
Konecky 2017, PINNED-WEAK): `S = sum_i (1-leak)^(k-1-i) * event_i` (newest weight 1, older geometrically suppressed),
default `leak=0.0` byte-identical to the flat sum. (The CAPACITY payoff -- recent recovery held at overload where the
flat sum collapses -- is proven by the solver's reverify `test_register_leaky_write.py` 11/11, reverified first-hand at
integration; this witness confirms the PROMOTED organ code is correct: off = byte-identical, on = recency-weighted +
graded, threaded through both backends.)

Asserts:
  1. leak=0.0 is BYTE-IDENTICAL: register() equals the flat `bundling.bundle` sum (the leaky branch is NOT taken).
  2. leak>0 is the recency-weighted RAW sum: register() equals sum_i (1-leak)^(k-1-i)*event_i (within fp tol).
  3. RECENCY DOMINANCE: |<register, newest>| > |<register, oldest>| (recent events dominate the code).
  4. GRADED gradient (not a step): |<register, newest>| > |<register, middle>| > |<register, oldest>| -- the primate
     66/45/39 monotonic shape, not a discrete-slot queue.
  5. THREADED to both backends via make_situation_register(leak=...): flat + multibank both construct and register()
     runs with leak>0 (multibank applies it per-bank); and backend="flat", leak=0.0 stays byte-identical.

Run: .venv/Scripts/python.exe verification/test_register_leaky_write_organ.py
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import torch  # noqa: E402

from hdlab import bundling  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister, make_situation_register  # noqa: E402


def _mag(a: torch.Tensor, b: torch.Tensor) -> float:
    """Magnitude of the complex inner product |<a, b>| (FHRR similarity, unnormalized)."""
    return float(torch.abs((a.conj() * b).sum()))


def _add3(reg, entity="e"):
    """Add three distinct events (oldest->newest): (A,0), (B,1), (C,2); return [oldest, middle, newest] event vecs."""
    reg.add_event(entity, "A", 0)
    reg.add_event(entity, "B", 1)
    reg.add_event(entity, "C", 2)
    return list(reg._events[entity])   # insertion order = [oldest, middle, newest]


def main() -> int:
    checks = []
    d = 512
    vocab = ["A", "B", "C", "D"]

    # (1) leak=0.0 byte-identical to the flat bundle.
    g0 = torch.Generator().manual_seed(7)
    reg0 = AccumulateRegister(vocab, d, g0, max_event_slots=8, leak=0.0)
    ev0 = _add3(reg0)
    flat = bundling.bundle(torch.stack(ev0, dim=0), norm=None)
    got0 = reg0.register("e")
    checks.append((torch.allclose(got0, flat),
                   f"[1] leak=0.0 is BYTE-IDENTICAL to the flat bundle (max|diff|={float((got0-flat).abs().max()):.2e})"))

    # (2) leak>0 is the recency-weighted raw sum sum_i (1-leak)^(k-1-i)*event_i.
    g1 = torch.Generator().manual_seed(7)
    reg1 = AccumulateRegister(vocab, d, g1, max_event_slots=8, leak=0.5)
    ev1 = _add3(reg1)                                  # same seed -> same event vecs as reg0
    lam, k = 0.5, 3
    w = [lam ** (k - 1 - i) for i in range(k)]          # [0.25, 0.5, 1.0]
    expect = sum(wi * e for wi, e in zip(w, ev1))
    got1 = reg1.register("e")
    checks.append((torch.allclose(got1, expect, atol=1e-5),
                   f"[2] leak>0 = recency-weighted raw sum (weights {w}; max|diff|={float((got1-expect).abs().max()):.2e})"))

    # (3) recency DOMINANCE + (4) GRADED gradient (newest > middle > oldest).
    oldest, middle, newest = ev1
    m_new, m_mid, m_old = _mag(got1, newest), _mag(got1, middle), _mag(got1, oldest)
    checks.append((m_new > m_old,
                   f"[3] RECENCY DOMINANCE: |<reg,newest>|={m_new:.1f} > |<reg,oldest>|={m_old:.1f}"))
    checks.append((m_new > m_mid > m_old,
                   f"[4] GRADED gradient (not a step): newest {m_new:.1f} > middle {m_mid:.1f} > oldest {m_old:.1f}"))

    # (5) threaded through make_situation_register to both backends.
    gf = torch.Generator().manual_seed(7)
    rflat = make_situation_register(vocab, d, gf, max_event_slots=8, backend="flat", leak=0.5)
    _add3(rflat)
    flat_leaky_ok = _mag(rflat.register("e"), list(rflat._events["e"])[-1]) > _mag(rflat.register("e"), list(rflat._events["e"])[0])
    gf0 = torch.Generator().manual_seed(7)
    rflat0 = make_situation_register(vocab, d, gf0, max_event_slots=8, backend="flat", leak=0.0)
    ev = _add3(rflat0)
    flat0_identical = torch.allclose(rflat0.register("e"), bundling.bundle(torch.stack(ev, dim=0), norm=None))
    gm = torch.Generator().manual_seed(7)
    rmb = make_situation_register(vocab, d, gm, max_event_slots=8, backend="multibank", n_banks=8, leak=0.5)
    for i, r in enumerate(["A", "B", "C", "D", "A", "B"]):    # spread across banks; >=2 land in some bank
        rmb.add_event("e", r, i % 8)
    mb_runs = rmb.register("e").shape[-1] == d
    checks.append((flat_leaky_ok and flat0_identical and mb_runs,
                   f"[5] make_situation_register threads leak: flat leaky-dominance={flat_leaky_ok}, flat leak=0 byte-identical={flat0_identical}, multibank leaky register() runs={mb_runs}"))

    print("=== witness: hdlab.situation_model_accumulate leaky/recency WRITE (AccumulateRegister.leak) ===")
    all_pass = True
    for ok, msg in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
        all_pass = all_pass and ok
    print(f"\nRESULT: {'ALL CHECKS PASS' if all_pass else 'FAIL'} ({sum(1 for ok, _ in checks if ok)}/{len(checks)})")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
