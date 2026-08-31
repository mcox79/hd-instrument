"""Witness for the VERB-SUBCATEGORIZATION patient-gate landing into the canonical SituationReader (2026-08-31).

Wires the promoted hdlab/verb_subcat.py (the p2 who-did-what PRESENCE lever) into the live reader behind a
DEFAULT-OFF `verb_subcat_gate` flag: a post-read pass that SUPPRESSES a bound patient on low-transitivity
(intransitive) verbs ("the man arrived at noon" -> patient=noon is spurious). This is the SIMPLE lexical-
propensity gate (transitivity < thr) -- the version VALIDATED END-TO-END through read() (the experiment's
SubcatGateReader). The stronger GRADED Competition-Model gate (verb_subcat.patient_present) is a queued
refinement (needs the reader to expose POS + the patient token index).

  (1) DEFAULT-OFF byte-identical: verb_subcat_gate OFF == the default -- identical events AND patients, and
      hdlab.verb_subcat is NOT imported on the off path (no new hard dependency).
  (2) GATE FIRES + SUPPRESS-ONLY: on real narrative, events are HELD (recall unchanged) and the gate ONLY
      suppresses patients (never adds); at least one spurious patient on a low-transitivity verb is removed.
  (3) FAITHFUL WIRING: the landed verb_subcat_gate=True output EQUALS the validated SubcatGateReader
      (subcat_thr=0.35) byte-for-byte on (sent_idx, global_idx, predicate, patient) -- no new logic.
ASCII-only, deterministic, CPU-only; a truncated real LitBank doc (real coref mentions, fast).
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "experiments"))

import tempfile
from hdlab.situation_reader import SituationReader, _write_temp_conll

_SRC = os.path.join(_REPO, "data", "litbank", "coref", "conll", "1023_bleak_house_brat.conll")


def _truncate_conll(src, n_sents):
    """Copy the header + first n_sents blank-line-terminated sentences to a temp conll (real coref markers,
    fast). Cutting at a sentence boundary keeps within-sentence coref mentions intact."""
    out_lines, blanks = [], 0
    with open(src, encoding="utf-8") as f:
        for line in f:
            out_lines.append(line)
            if line.strip() == "":
                blanks += 1
                if blanks >= n_sents:
                    break
    fd, path = tempfile.mkstemp(suffix=".conll")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.writelines(out_lines)
        if not out_lines or out_lines[-1].strip() != "":
            f.write("\n")
    return path


def _ev(sm):
    return [(e.sent_idx, e.global_idx, str(e.predicate).lower(), str(e.patient)) for e in sm.events]


def _pats(sm):
    return sum(1 for e in sm.events if e.patient not in ("?", None))


def test_verb_subcat_gate_landing():
    # (1) DEFAULT-OFF byte-identical (fast synthetic).
    rows = []
    for si, toks in enumerate(["The dog chased the cat .".split(), "The man arrived at the station .".split()]):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    syn = _write_temp_conll(rows)
    assert "hdlab.verb_subcat" not in sys.modules, "verb_subcat must not be imported before a gated reader runs"
    sm_def = SituationReader(tense_agnostic_events=True).read(syn)
    sm_off = SituationReader(tense_agnostic_events=True, verb_subcat_gate=False).read(syn)
    assert _ev(sm_def) == _ev(sm_off), "verb_subcat_gate=False must be byte-identical to the default"
    assert "hdlab.verb_subcat" not in sys.modules, "verb_subcat must NOT be imported on the gate-OFF path"
    print("[1] DEFAULT-OFF byte-identical: %d events identical; verb_subcat not imported" % len(sm_def.events))

    # Real (truncated) doc -> real coref mentions -> the binder actually assigns patients.
    doc = _truncate_conll(_SRC, n_sents=60)
    off = SituationReader(tense_agnostic_events=True).read(doc)
    on = SituationReader(tense_agnostic_events=True, verb_subcat_gate=True).read(doc)

    # (2) events held + suppress-only + at least one fire.
    assert len(off.events) == len(on.events), "event recall must be unchanged (detection is upstream of the gate)"
    off_pat = {(e.global_idx): e.patient for e in off.events}
    n_supp = 0
    for e in on.events:
        op = off_pat[e.global_idx]
        if e.patient != op:
            assert op not in ("?", None) and e.patient == "?", "gate may ONLY suppress (op->'?'), not change/add"
            n_supp += 1
    p_off, p_on = _pats(off), _pats(on)
    assert p_on < p_off and n_supp > 0, ("gate must FIRE on real prose: patients %d->%d (suppressed %d)"
                                         % (p_off, p_on, n_supp))
    print("[2] GATE FIRES + suppress-only: events %d held; patients %d->%d (suppressed %d spurious on low-trans verbs)"
          % (len(off.events), p_off, p_on, n_supp))

    # (3) FAITHFUL WIRING == the validated SubcatGateReader byte-for-byte.
    import exp_verb_subcat_supply_through_reader_v1 as TR
    asset = TR.V2.load_final_asset()
    ref = TR.SubcatGateReader(subcat_asset=asset, subcat_thr=0.35, tense_agnostic_events=True).read(doc)
    assert _ev(on) == _ev(ref), "landed verb_subcat_gate must EQUAL the validated SubcatGateReader byte-for-byte"
    print("[3] FAITHFUL WIRING: landed verb_subcat_gate=True == the validated SubcatGateReader (byte-for-byte)")

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_verb_subcat_gate_landing()
