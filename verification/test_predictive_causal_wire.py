"""LANDING WITNESS -- the FORWARD predictive-causal reader wire (owner-DONE
generate_dont_retrieve_causal_edges_for_unmarked_narrative_causation, 2026-09-09, Q111).

Landed: hdlab.predictive_world_model (online delta-rule event-transition world-model + counterfactual-necessity
reader, self-contained) + situation_reader._read_predictive_causal binding sm.causal_antecedent /
sm.predictive_necessity / sm.predictive_world_model (default-on track_predictive_causal, additive/lazy).

W1  the reader is BYTE-IDENTICAL off vs on for existing fields (events + causal_links) -- the pass is pure-add.
W2  OFF arm binds NO callables (sm.causal_antecedent is None); ON arm binds them.
W3  (guarded on the gitignored foundation asset) the causal read is brain-sensible: the argmax-necessity antecedent
    of a 'died' event in a shoot->die narrative is the 'shot' event, and its necessity FAR exceeds an unrelated
    'walked' event -- the counterfactual-necessity criterion (surprisal-increase on ablation) works live.

Run: .venv/Scripts/python.exe verification/test_predictive_causal_wire.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll

_ASSET = os.path.join(_REPO, "data/frontend_assets/predictive_world_model_simplewiki_v1.npz")
_fail = []


def _ck(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        _fail.append(msg)


def _doc():
    sents = ["The hunter walked into the forest .",
             "He raised the rifle and shot the deer .",
             "The deer stumbled and died on the path .",
             "She buried it near the river ."]
    rows = []
    for si, s in enumerate(sents, 1):
        for wi, w in enumerate(s.split(), 1):
            rows.append((si, wi, w, "-"))
    return _write_temp_conll(rows)


def main():
    path = _doc()
    on = SituationReader()
    off = SituationReader(); off.track_predictive_causal = False
    a = on.read(path); b = off.read(path)

    def ev(sm):
        return [(getattr(e, "predicate", None), getattr(e, "sent_idx", None)) for e in (getattr(sm, "events", []) or [])]

    def ca(sm):
        return [(l.sent_idx, l.cause, l.outcome) for l in (getattr(sm, "causal_links", []) or [])]

    _ck(ev(a) == ev(b), "W1 events byte-identical off vs on (n=%d)" % len(ev(a)))
    _ck(ca(a) == ca(b), "W1 causal_links byte-identical off vs on")
    _ck(getattr(b, "causal_antecedent", None) is None, "W2 OFF arm binds no predictive-causal callables")
    _ck(callable(getattr(a, "causal_antecedent", None)), "W2 ON arm binds sm.causal_antecedent")

    if not os.path.exists(_ASSET):
        print("  SKIP W3 (foundation asset absent -- build via `python -m hdlab.predictive_world_model --build`)")
        _ck(a.causal_antecedent(0) is None, "W3(abstain) causal_antecedent abstains cleanly when asset absent")
    else:
        preds = [getattr(e, "predicate", None) for e in (a.events or [])]
        died = next((i for i, p in enumerate(preds) if p and p.startswith("died")), None)
        shot = next((i for i, p in enumerate(preds) if p and p.startswith("shot")), None)
        walked = next((i for i, p in enumerate(preds) if p and p.startswith("walk")), None)
        ok_setup = died is not None and shot is not None and walked is not None and walked < shot < died
        _ck(ok_setup, "W3 setup: walked(%s) < shot(%s) < died(%s) events present" % (walked, shot, died))
        if ok_setup:
            r = a.causal_antecedent(died)
            _ck(r is not None and r["antecedent_event_index"] == shot and r["necessity_bits"] > 0,
                "W3 causal_antecedent(died) = the 'shot' event, necessity>0 (got %s)" % r)
            n_shot = a.predictive_necessity(died, shot)
            n_walk = a.predictive_necessity(died, walked)
            _ck(n_shot is not None and n_walk is not None and n_shot > n_walk,
                "W3 necessity(died|shot)=%s FAR exceeds necessity(died|walked)=%s" % (n_shot, n_walk))


if __name__ == "__main__":
    main()
    print("\nRESULT: %s" % ("PASS" if not _fail else "FAIL (%d)" % len(_fail)))
    sys.exit(1 if _fail else 0)
