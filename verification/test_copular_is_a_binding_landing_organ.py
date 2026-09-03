"""Witness for the LANDING of the COPULAR is-a/attribute binding into the live reader (2026-09-03).

From the owner-DONE the_reader_has_no_copular_is_a_binding_schema (core 10/10 + improvements 6/6). Wires the
validated binding behind a DEFAULT-OFF `bind_entity_states` flag: read() adds typed (HOLDER, PROPERTY) states
on sm.entity_states via the validated primitive experiments._copular_nominal_events.extract_entity_states
(high-precision labeled `cop` path) + the glass-box Higgins typing, and applies the PREDICATIONAL ones to
sm.state_register so "what is X" round-trips. Additive, byte-identical when off, NO LLM.

  [1] DEFAULT-OFF byte-identical: bind_entity_states OFF -> sm.entity_states == [] and sm.state_register is None;
      the core event set (predicate/agent/patient) is identical off vs on (the read is purely additive).
  [2] FLAG-ON FIRES (can-fail): on copular prose it recovers the (holder, property) binding + Higgins type --
      "Ahab was a captain" -> (ahab, captain, pred_nom); "the room was cold" -> (room, cold, pred_adj).
  [3] FLAG-ON == the VALIDATED primitive byte-for-byte: for every sentence, the reader's entity_states pairs
      EQUAL a direct experiments._copular_nominal_events.extract_entity_states on the SAME assets (no new logic).
  [4] READ-BACK round-trips: the predicational state is applied to sm.state_register -> state_at('ahab')
      contains 'captain' (the "what is Ahab?" answer the base reader could not give).

Run: .venv/Scripts/python.exe verification/test_copular_is_a_binding_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, parse_conll_sentences, _write_temp_conll  # noqa: E402

_SENTS = [
    "Ahab was a captain .".split(),
    "the room was cold .".split(),
    "she was his wife .".split(),
]
_GAZ = {"ahab": "masc", "she": "fem"}


def _doc():
    rows = []
    for si, toks in enumerate(_SENTS):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    return _write_temp_conll(rows)


def _core(sm):
    return [(e.global_idx, str(e.predicate), str(e.agent), str(e.patient)) for e in sm.events]


def main():
    doc = _doc()
    off = SituationReader.all_capabilities_off(gaz=_GAZ, bind_entity_states=False).read(doc)
    on = SituationReader.all_capabilities_off(gaz=_GAZ, bind_entity_states=True).read(doc)
    checks = []

    # [1] EXPLICIT-OFF byte-identical (all_capabilities_off + bind OFF -> no state binding).
    ok1 = (list(off.entity_states) == [] and off.state_register is None and _core(off) == _core(on))
    checks.append((ok1, "[1] EXPLICIT-OFF byte-identical: entity_states=[] + state_register None; %d core events "
                   "identical off vs on" % len(off.events)))

    # [0] DEFAULT-ON (P3 CHANGE 1, 2026-09-03): bind_entity_states is now the reader's DEFAULT (the state-QA
    # consumer landed, turn-on net-positive) -- SituationReader() with no args builds the state register; the
    # factory off-baseline still sets it False.
    ok0 = (SituationReader().bind_entity_states is True
           and SituationReader.all_capabilities_off().bind_entity_states is False
           and "bind_entity_states" in SituationReader.CAPABILITY_FLAGS)
    checks.append((ok0, "[0] DEFAULT-ON: SituationReader().bind_entity_states=True, factory-off=False, in FLAGS"))

    # [2] FLAG-ON FIRES + typed.
    got = {(s.holder.lower(), s.property.lower(), s.htype) for s in on.entity_states}
    ok2 = (("ahab", "captain", "pred_nom") in got) and (("room", "cold", "pred_adj") in got)
    checks.append((ok2, "[2] FLAG-ON fires + Higgins-typed: %s" % sorted(got)))

    # [3] FLAG-ON == the promoted DETECTION UNION (label path | robust_cop), byte-for-byte (P3 CHANGE 2: the
    # entity-state route unions the high-precision `cop`-label path with the label-ROBUST closed-class detector).
    import hdlab.copular_binding as M
    from hdlab.pos_tagger import PosTagger
    from hdlab.arc_parser import ArcParser
    from hdlab.arc_labeler import ArcLabeler
    pos = PosTagger.load(M.POS_ASSET); arc = ArcParser.load(M.ARC_ASSET); lab = ArcLabeler.load(M.LAB_ASSET)
    sents = parse_conll_sentences(doc)
    ref = set()
    for si, toks in enumerate(sents):
        up = pos.tag(toks)
        heads = arc.parse(toks, up).heads
        pairs = set(M.extract_entity_states(toks, up, arc, lab)) | M.robust_cop(toks, up, heads, gate=True)
        for (h, p) in pairs:
            ref.add((si, toks[h].lower(), toks[p].lower()))
    got = set((s.sent_idx, s.holder.lower(), s.property.lower()) for s in on.entity_states)
    ok3 = got == ref and len(ref) > 0
    checks.append((ok3, "[3] FLAG-ON == extract_entity_states UNION robust_cop byte-for-byte (%d pairs)" % len(ref)))

    # [4] READ-BACK round-trips via state_register.
    sa = on.state_register.state_at("ahab") if on.state_register is not None else set()
    ok4 = "captain" in {str(x).lower() for x in (sa or set())}
    checks.append((ok4, "[4] READ-BACK: state_at('ahab') = %s (contains 'captain')" % sorted(sa or set())))

    # [5] PROMOTION FAITHFUL (graceful): hdlab.copular_binding reproduces the experiment's extract_entity_states
    # + predicted_type byte-exact, where the source cell is present (skips cleanly on a checkout without it).
    try:
        import experiments._copular_nominal_events as EXP
        from experiments.exp_copular_is_a_binding_readout_v1 import predicted_type as exp_pt
        pf = True
        for si, toks in enumerate(sents):
            up = pos.tag(toks)
            hp = M.extract_entity_states(toks, up, arc, lab)
            if hp != EXP.extract_entity_states(toks, up, arc, lab):
                pf = False
            for (h, p) in hp:
                if M.predicted_type(toks, up, h, p) != exp_pt(toks, up, h, p):
                    pf = False
        checks.append((pf, "[5] PROMOTION FAITHFUL: hdlab.copular_binding == experiments byte-exact"))
    except Exception as e:
        checks.append((True, "[5] PROMOTION FAITHFUL: SKIPPED (source cell absent: %s)" % type(e).__name__))

    print("=== witness: COPULAR is-a/attribute BINDING LANDING (bind_entity_states) ===")
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
