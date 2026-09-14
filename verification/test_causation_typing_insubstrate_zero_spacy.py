"""VERIFY the proposed ZERO-spaCy causation_typing fix.

Three proofs for the owner 2026-09-08 rule (no external tool at inference; spaCy must not exist in the
substrate at all, even dormant):

  A. IMPORT PURITY -- importing the in-substrate candidate + hdlab.situation_reader loads NO spaCy.
  B. TYPED-PATH END-TO-END -- read_typed_causation_insubstrate parses real modern docs with the
     in-substrate frontend and emits TypedCausalLinks, with a TRIPWIRE that makes any spacy.load() raise;
     it must run WITHOUT tripping (proves the typed path no longer reaches spaCy).
  C. BYTE-IDENTICAL DEFAULT READ -- SituationReader().read() on 20 modern docs is byte-identical with
     spaCy available vs. with a spaCy tripwire armed (both dormant paths default-off), and the tripwire
     never fires on a default read (proves removing/replacing both paths is byte-identical).

Run: .venv/Scripts/python.exe verification/test_causation_typing_insubstrate_zero_spacy.py
"""
from __future__ import annotations

import glob
import os
import re
import sys

_ADDR = re.compile(r"0x[0-9a-fA-F]+")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

MODERN = sorted(glob.glob("data/exp_fd_harm_help_live_modern_v1/gold_*.conll"))[:20]


class _TripSpacy:
    """A fake `spacy` module: importing is fine, but any .load()/.blank() TRIPS -- proving the code path
    that reached it. `tripped` records the first offending call."""
    tripped = []

    def load(self, *a, **k):
        _TripSpacy.tripped.append(("spacy.load", a))
        raise RuntimeError("SPACY TRIPWIRE: spacy.load reached")

    def blank(self, *a, **k):
        _TripSpacy.tripped.append(("spacy.blank", a))
        raise RuntimeError("SPACY TRIPWIRE: spacy.blank reached")


def _arm_tripwire():
    _TripSpacy.tripped = []
    sys.modules["spacy"] = _TripSpacy()


def _disarm_tripwire():
    sys.modules.pop("spacy", None)


def _digest(sm) -> str:
    """Stable repr of every stored SituationModel dimension (callables like believes/knows skipped;
    unstable object-identity memory addresses `0x...` normalized -- they differ even between two identical
    reads of a default reader, so they are NOT a dimension value; the register CONTENTS are compared)."""
    parts = []
    for k in sorted(vars(sm).keys()):
        v = getattr(sm, k)
        if callable(v):
            parts.append(f"{k}=<callable>")
            continue
        try:
            parts.append(f"{k}={_ADDR.sub('0xADDR', repr(v))}")
        except Exception as e:
            parts.append(f"{k}=<unrepr:{e}>")
    return "\n".join(parts)


def part_a_import_purity():
    # child process: clean interpreter, import candidate + reader, assert no spacy loaded
    code = (
        "import sys;"
        "import experiments.exp_causation_typing_insubstrate_v1 as C;"
        "import hdlab.situation_reader as R;"
        "import hdlab.causation_typing as CT;"
        "print('SPACY_LOADED' if 'spacy' in sys.modules else 'NO_SPACY')"
    )
    import subprocess
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    tail = (out.stdout + out.stderr).strip().splitlines()[-1] if (out.stdout or out.stderr) else ""
    ok = tail == "NO_SPACY"
    print(f"[A] import purity: {tail!r} -> {'PASS' if ok else 'FAIL'}")
    return ok


def part_b_typed_path():
    from experiments.exp_causation_typing_insubstrate_v1 import read_typed_causation_insubstrate
    _arm_tripwire()
    total = 0
    docs = MODERN[:6]
    try:
        for d in docs:
            links = read_typed_causation_insubstrate(None, d, None, use_gate=True)
            total += len(links)
    finally:
        tripped = list(_TripSpacy.tripped)
        _disarm_tripwire()
    typed = sum(1 for _ in range(0))  # placeholder
    ok = (not tripped) and total > 0
    # show a couple of sample links from the last doc
    sample = read_typed_causation_insubstrate(None, docs[-1], None, use_gate=True)[:3]
    print(f"[B] typed path over {len(docs)} modern docs: {total} TypedCausalLinks, tripwire={tripped} "
          f"-> {'PASS' if ok else 'FAIL'}")
    for lk in sample:
        print(f"      {lk.ctype:12} {lk.affector!r}-{lk.verb}->{lk.patient!r} "
              f"end={lk.endstate_reached} src={lk.source} lbl={lk.engage_label}")
    return ok


def part_c_byte_identical():
    from hdlab.situation_reader import SituationReader
    docs = MODERN
    assert len(docs) >= 20, f"need >=20 modern docs, found {len(docs)}"

    # baseline: spaCy AVAILABLE (real environment), default reader
    r1 = SituationReader()
    base = [(_digest(r1.read(d))) for d in docs]

    # candidate world: spaCy TRIPWIRED + both hdlab dormant spaCy entrypoints forced to raise. A default
    # read must neither trip nor change output (both paths are default-off).
    import hdlab.situation_reader as R
    import hdlab.causation_typing as CT
    # 2026-09-14 (strategy): R._build_spacy_pred_gate was REMOVED on 2026-09-08 (zero spaCy in hdlab) -- an absent entrypoint is the
    # stronger guarantee; trip it only if it still exists.
    orig_pred = getattr(R, "_build_spacy_pred_gate", None)
    orig_nlp = getattr(CT, "_nlp_or_load", None)   # also removed since (zero spaCy); guard the same way

    def _no_pred():
        _TripSpacy.tripped.append(("_build_spacy_pred_gate", None))
        raise RuntimeError("TRIP: _build_spacy_pred_gate reached")

    def _no_nlp(nlp):
        _TripSpacy.tripped.append(("_nlp_or_load", None))
        raise RuntimeError("TRIP: _nlp_or_load reached")

    _arm_tripwire()
    if orig_pred is not None:
        R._build_spacy_pred_gate = _no_pred
    if orig_nlp is not None:
        CT._nlp_or_load = _no_nlp
    try:
        r2 = SituationReader()
        cand = [(_digest(r2.read(d))) for d in docs]
        tripped = list(_TripSpacy.tripped)
    finally:
        if orig_pred is not None:
            R._build_spacy_pred_gate = orig_pred
        if orig_nlp is not None:
            CT._nlp_or_load = orig_nlp
        _disarm_tripwire()

    n_ident = sum(1 for a, b in zip(base, cand) if a == b)
    first_diff = next((docs[i] for i, (a, b) in enumerate(zip(base, cand)) if a != b), None)
    ok = (n_ident == len(docs)) and (not tripped)
    print(f"[C] byte-identical default read: {n_ident}/{len(docs)} docs identical, tripwire={tripped}, "
          f"first_diff={first_diff} -> {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    a = part_a_import_purity()
    b = part_b_typed_path()
    c = part_c_byte_identical()
    allok = a and b and c
    print(f"\nRESULT: {'ALL PASS' if allok else 'FAIL'} (A={a} B={b} C={c})")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
