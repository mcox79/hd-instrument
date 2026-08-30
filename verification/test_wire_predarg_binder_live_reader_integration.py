"""Scaffold-free witness: the proposed diff DEMONSTRATED in the LIVE hdlab.situation_reader.read() code path
(not a standalone mirror), with NO regression. Runs the REAL read() pipeline via a WiredSituationReader
subclass. Asserts: role_route=positional is byte-identical to the stock reader; the wiring leaves the NON-role
dimensions (entities/coref/timeline/causation/memory) byte-identical + event recall unchanged; quotative
inversion is fixed live ("... said John" -> John=AGENT); a richer RECIPIENT role is emitted live.

Run: .venv/Scripts/python.exe verification/test_wire_predarg_binder_live_reader_integration.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.exp_wire_predarg_binder_live_reader_integration_v1 as ITG  # noqa: E402


def main():
    # the cell's self_test runs the REAL read() and asserts all four claims (byte-identical OFF, non-role dims
    # unchanged, quotative fixed, recipient emitted); it raises AssertionError on any failure.
    checks = []
    try:
        ITG.self_test()
        checks.append(("live read() path: byte-identical OFF; non-role dims unchanged; quotative fixed; "
                       "recipient emitted (no regression)", True))
    except AssertionError as e:
        checks.append((f"live read() integration self-test: {e}", False))

    # the honest close: the role LIFT reproduced THROUGH the live SituationReader.read() class at scale.
    res = ITG.run_scale(n_boot=800)
    d = res["wired_minus_stock"]
    checks.append((f"role LIFT measured THROUGH live read() at scale (57 McGuffey-as-CoNLL, n={res['wired']['n']}): "
                   f"wired {res['wired']['acc']:.3f} vs stock {res['stock_positional']['acc']:.3f} = "
                   f"{d['delta']:+.3f} [{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] {d['band']}", d["band"] == "ABOVE"))

    npass = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        npass += int(ok)
    print(f"\n{npass}/{len(checks)} checks PASS (the diff demonstrated + the lift reproduced IN the live reader class)")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
