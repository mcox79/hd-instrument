"""reader_capabilities.py -- the DERIVED "what can the live reader do, and is it ON by default?" view.

WHY THIS EXISTS (2026-08-31): the assembly wires validated dimensions into hdlab.situation_reader
behind DEFAULT-OFF flags (byte-identical when off). So the DEFAULT reader -- SituationReader() --
is materially WEAKER than the reader with the flags ON. A solver (or strategy) who measures a floor/
baseline against the DEFAULT reader is measuring an artificially weak reader and can (a) understate a
floor, (b) re-derive a capability that already exists behind a flag, or (c) fail to compose with it.
This tool is the single canonical, ROT-PROOF answer: it INTROSPECTS the reader's constructor for every
capability flag + its default, and cross-references the capability registry for what each does + its
witness. Run it before measuring anything against "the reader".

  python tools/reader_capabilities.py            # the manifest table
  python tools/reader_capabilities.py --enable    # the exact kwargs to build the FULLY-ON reader

Glass-box, no deps beyond stdlib + inspect on the reader signature. ASCII-only.
"""
from __future__ import annotations

import inspect
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

REG = os.path.join(_REPO, "data", "capability_registry.jsonl")

# The capability FLAGS (as opposed to tuning params). Each names the reader kwarg that turns a
# validated dimension ON. Descriptions are one-line; the AUTHORITATIVE detail is the registry entry
# (id) + the witness, both printed. Keeping the flag->id map here is the ONLY hand-maintained bit;
# everything else (default state, capability text, witness) is DERIVED.
CAP_FLAGS = {
    "tense_agnostic_events": "extraction_frontend_tense_agnostic_detector_v1",
    "preserve_tense": "preserve_tense_live_reader_v1",          # refines tense_agnostic_events (composed tense)
    "causation_typed": "causation_typed_live_reader_v1",
    "timeline_register": "timeline_register_live_reader_v1",
    "track_space": "track_space_live_reader_v1",                # SPACE dimension -> sm.locations
    "verb_subcat_gate": "verb_subcat_gate_live_reader_v1",      # who-did-what PRESENCE (suppress spurious patients)
    # role_route is a string ("positional" = off; "wired"/other = the assembly who-did-what path)
    "role_route": None,
    "spacy_pred_gate": None,
}


def _reg_by_id():
    out = {}
    if not os.path.exists(REG):
        return out
    with open(REG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[e.get("id")] = e   # last wins
    return out


def _reader_defaults():
    from hdlab.situation_reader import SituationReader
    sig = inspect.signature(SituationReader.__init__)
    return {n: p.default for n, p in sig.parameters.items()
            if p.default is not inspect.Parameter.empty}


def manifest():
    defaults = _reader_defaults()
    reg = _reg_by_id()
    rows = []
    for flag, cap_id in CAP_FLAGS.items():
        if flag not in defaults:
            continue
        default = defaults[flag]
        # "off" = the byte-identical default; for role_route the off value is "positional"
        is_off = (default in (False, "positional", None))
        e = reg.get(cap_id) if cap_id else None
        cap = (e.get("name") if e else "(string mode flag; see role_route in situation_reader)") or ""
        witness = (e.get("witness") if e else "") or ""
        rows.append((flag, repr(default), "OFF" if is_off else "ON", cap_id or "-", cap, witness))
    return rows


def print_manifest():
    rows = manifest()
    print("=" * 100)
    print("LIVE READER CAPABILITY FLAGS -- default state (SituationReader() = every capability OFF)")
    print("=" * 100)
    for flag, default, state, cid, cap, witness in rows:
        print("\n[%s]  default=%s  -> %s" % (flag, default, state))
        print("   capability : %s" % (cap[:140]))
        if cid != "-":
            print("   registry   : %s" % cid)
        if witness:
            print("   witness    : %s" % witness)
    n_off = sum(1 for r in rows if r[2] == "OFF")
    print("\n" + "-" * 100)
    print("SUMMARY: %d of %d capability flags are OFF by default. `SituationReader()` is the DEFAULT/WEAK reader." % (n_off, len(rows)))
    print("BEFORE MEASURING a floor/baseline against 'the reader', decide whether the fair baseline is the")
    print("DEFAULT reader or the FULLY-ON reader for the dimension you touch. Enable: python tools/reader_capabilities.py --enable")
    print("NOTE: no full-system end-to-end run turns ALL of these on together yet (see the assembly harness problem).")


def print_enable():
    print("# The FULLY-ON reader (all validated dimension flags enabled).")
    print("# ⚠️ MEASURED 2026-08-31 (the_assembled_reader_is_never_tested_as_a_whole, owner-DONE): the fully-on reader")
    print("# is N PARALLEL SILOS, not one integrated situation model -- turning flags on COMPOSES but does not BIND")
    print("# (interaction byte-exactly 0). No dimension flag should be flipped default-ON yet (only role_route is")
    print("# aggregate-positive + instrument-safe). And the QA capstone is INSTRUMENT-COUPLED: its temporal/causal")
    print("# golds derive from sm.events, which tense_agnostic_events rewrites -- score temporal Qs off sm.timeline_order")
    print("# (answers 0.98 at 0.91), NOT the naive sm.events readout. The integration fix is the TIERED bound-event-token")
    print("# backbone (its own problem), NOT more flags.")
    print("SituationReader(")
    print("    tense_agnostic_events=True,   # event recall 0.33->0.95 (extraction keystone)")
    print("    preserve_tense=True,          # composed Reichenbach tense/is_pp (refines tense_agnostic_events; feeds TIME)")
    print("    causation_typed=True,         # typed CAUSE/ENABLE/PREVENT (sm.typed_causal_links)")
    print("    timeline_register=True,       # whole-passage chronological order (sm.timeline_order)")
    print("    track_space=True,             # SPACE / WHERE dimension (sm.locations; where_is/present_in_scene)")
    print("    verb_subcat_gate=True,        # who-did-what PRESENCE (suppress spurious patients on intransitives)")
    print("    role_route='wired',           # assembly who-did-what role routing (the one aggregate-positive flag)")
    print("    spacy_pred_gate=True,         # supplied-grammar predicate gate (changes the event set; measure it)")
    print(")")


if __name__ == "__main__":
    if "--enable" in sys.argv:
        print_enable()
    else:
        print_manifest()
