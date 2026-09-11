"""Landing witness -- the who_was_affected read()-time wire (sm.affected_entity).

Asserts the additive AFFECTED-ENTITY dimension (owner-DONE who_was_affected...forward_salience_prior):
  W1  byte-identical off vs on (events / coref_acc / commonnoun_resolution unchanged) -- PURE ADD.
  W2  OFF arm leaves sm.affected_entity == [] (the field default).
  W3  ON arm RESOLVES a pronoun undergoer to the salient discourse entity via hdlab.affected_entity_resolver
      (salience prior x Principle-B x role/thematic parallelism): "He greeted HIM" -> him resolves to Peter
      (the OBJECT-parallelism pick == gold), NOT the subject John.

Glass-box; NO external LLM. The mentions come from the CoNLL mention column (parse_litbank_conll), like every
reader dimension; the RESOLUTION is gold-free. The rigorous SCORED proof is the board arm
board_affected_entity_dimension (the deployment number on the predicted parse).
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll

_fail = []


def _ck(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        _fail.append(msg)


def main():
    # "John met Peter . He greeted him warmly ." with a coref column: John/He = cluster 0, Peter/him = cluster 1.
    rows = [
        (1, 1, "John", "(0)"), (1, 2, "met", "-"), (1, 3, "Peter", "(1)"), (1, 4, ".", "-"),
        (2, 1, "He", "(0)"), (2, 2, "greeted", "-"), (2, 3, "him", "(1)"), (2, 4, "warmly", "-"), (2, 5, ".", "-"),
    ]
    path = _write_temp_conll(rows)
    on = SituationReader()
    off = SituationReader()
    off.track_affected_entity = False
    a = on.read(path)
    b = off.read(path)

    def ev(sm):
        return [(e.predicate, e.agent, e.patient, e.sent_idx) for e in (sm.events or [])]

    _ck(ev(a) == ev(b), "W1 events byte-identical off vs on (n=%d)" % len(ev(a)))
    _ck(a.coref_acc == b.coref_acc, "W1 coref_acc byte-identical off vs on")
    _ck((a.commonnoun_resolution or []) == (b.commonnoun_resolution or []),
        "W1 commonnoun_resolution byte-identical off vs on")
    _ck(list(getattr(b, "affected_entity", []) or []) == [], "W2 OFF arm leaves sm.affected_entity == []")

    ae = list(getattr(a, "affected_entity", []) or [])
    _ck(len(ae) >= 1, "W3 ON arm populates sm.affected_entity (n=%d)" % len(ae))
    if ae:
        r = ae[0]
        _ck(r["undergoer"] == "him" and r["resolved"] == "peter",
            "W3 undergoer 'him' resolves to 'peter' (OBJECT parallelism == gold, not subject 'john'); got %s->%s"
            % (r["undergoer"], r["resolved"]))


if __name__ == "__main__":
    main()
    print("\nRESULT: %s" % ("PASS" if not _fail else "FAIL (%d)" % len(_fail)))
    sys.exit(1 if _fail else 0)
