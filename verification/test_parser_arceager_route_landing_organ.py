"""Scaffold-free witness for the LANDING of the improved ARC-EAGER parser route into the live reader.

The default-off `parser_arceager` flag routes the WIRED who-did-what front end (`_router_roles`) through the
promoted `hdlab.arceager_parser` (UD-EWT UAS 0.775->0.842) instead of the richfeat `hdlab.arc_parser` -- swapping
ONLY the head source that feeds `predicate_argument_frontend` (matrix_verbs / route_predicate_arguments). Proves
it is additive/byte-identical when off, and that ON it genuinely routes through the arc-eager parser (changes the
who-did-what role assignment) while producing VALID roles. Recomputes from source on a REAL LitBank passage.

  [1] DEFAULT-OFF byte-identical: parser_arceager=False produces the SAME events (predicate/agent/patient/tense)
      as a reader built WITHOUT the flag -- the default reader is the pre-wire wired reader.
  [2] FLAG-ON is LIVE (arc-eager heads change who-did-what): >=1 event's (agent,patient) differs off-vs-on -- the
      only thing that differs is the parse head source, so a change proves the arc-eager route fired.
  [3] FLAG-ON is VALID (not a broken parse): the flag-on patient-fill rate is within a sane band of the flag-off
      rate (the arc-eager route yields valid roles, it does not collapse who-did-what to '?').
  [4] ORGAN sanity: the promoted arc-eager operator loads + parses a sentence into a valid 1-based head dict.

Brain frame (PINNED): a better incremental structure builder (arc-eager + rich non-local structural features;
Zhang-Nivre 2011) supplies more accurate attachment to the SAME downstream role reader (head source is the ONE
variable). Glass-box, NO external LLM. The improved parser is a promoted organ, not an inference-time LLM.

Run: .venv/Scripts/python.exe verification/test_parser_arceager_route_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as QA  # noqa: E402
from hdlab.situation_reader import SituationReader  # noqa: E402

# the arc-eager route refines the WIRED who-did-what path (role_route='wired')
CAPABLE = dict(tense_agnostic_events=True, preserve_tense=True, timeline_register=True,
               track_space=True, verb_subcat_gate=True, role_route="wired",
               spacy_pred_gate=False, causation_typed=False)


def _sig(sm):
    return [(e.global_idx, str(e.predicate), str(e.agent), str(e.patient), str(e.tense)) for e in sm.events]


def _fill_rate(sm):
    n = len(sm.events)
    filled = sum(1 for e in sm.events if e.patient not in ("?", None))
    return (filled / n) if n else 0.0


def main():
    gaz = QA.load_given_gazetteer()
    reader_stock = SituationReader(gaz=gaz, **CAPABLE)                       # no flag = pre-wire wired reader
    reader_off = SituationReader(gaz=gaz, parser_arceager=False, **CAPABLE)
    reader_on = SituationReader(gaz=gaz, parser_arceager=True, **CAPABLE)

    doc = next((d for d in QA.load_docs(6) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))), None)
    assert doc is not None, "no LitBank doc found"
    path = os.path.join(QA.CONLL_DIR, doc + ".conll")
    stock = reader_stock.read(path)
    off = reader_off.read(path)
    on = reader_on.read(path)

    checks = []

    # [1] DEFAULT-OFF byte-identical.
    off_ok = (_sig(off) == _sig(stock))
    checks.append((off_ok,
                   "[1] DEFAULT-OFF byte-identical: parser_arceager=False events (%d) == the no-flag wired reader "
                   "(the default reader is the pre-wire path)" % len(off.events)))

    # [2] FLAG-ON is LIVE.
    changed = [(o, n) for o, n in zip(off.events, on.events)
               if (o.agent, o.patient) != (n.agent, n.patient)]
    on_live = (len(off.events) == len(on.events) and len(changed) >= 1)
    checks.append((on_live,
                   "[2] FLAG-ON LIVE: the arc-eager route changed who-did-what on %d/%d events (only the parse head "
                   "source differs, so a change proves the arc-eager parser fired)" % (len(changed), len(on.events))))

    # [3] FLAG-ON VALID.
    r_off, r_on = _fill_rate(off), _fill_rate(on)
    on_valid = (r_on >= r_off - 0.10)   # arc-eager must not COLLAPSE who-did-what (a broken parse would)
    checks.append((on_valid,
                   "[3] FLAG-ON VALID: patient-fill rate off=%.3f on=%.3f (arc-eager yields valid roles, does not "
                   "collapse who-did-what to '?')" % (r_off, r_on)))

    # [4] ORGAN sanity.
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    from hdlab.pos_tagger import PosTagger
    W = load_model(MODEL_PATH)
    tg = PosTagger.load(os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    toks = ["The", "dog", "chased", "the", "ball", "."]
    heads = parse_with_conf(toks, tg.tag(toks), W)[0]
    organ_ok = (isinstance(heads, dict) and all(0 <= h <= len(toks) for h in heads.values())
                and any(h == 0 for h in heads.values()))
    checks.append((organ_ok,
                   "[4] ORGAN sanity: arceager parse -> valid 1-based head dict with a ROOT (heads=%s)" % heads))

    print("=== witness: arc-eager parser route LANDING (doc '%s', %d events, %d changed) ==="
          % (doc, len(on.events), len(changed)))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
