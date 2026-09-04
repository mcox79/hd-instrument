"""LANDING WITNESS: the structure-first PATIENT is wired into the hdlab substrate behind the (default-OFF)
`structural_patient` flag, reproduces the clean-UD-gold win THROUGH THE LANDED hdlab path, and is byte-safe
through the live reader (only the patient moves; the AGENT / P2 cm_agent competition and every non-role
dimension are byte-identical ON vs OFF).

Problem: consume_the_graded_pos_posterior_... (the who-did-what drill). The stock THEME/patient is a flat
cue/position selector (the brain's DAMAGED-BACKUP / agrammatic route). The landed fix reads the patient off the
parse's grammatical relations + voice remapping (predicate_argument_frontend.structural_patient_pick), gated by
`structural_patient` (default OFF). This gate asserts, scaffold-free, through the LANDED hdlab path only:
  (a) on CLEAN UD-EWT gold (patient := obj|nsubj:pass off the GOLD relations), the LANDED router with
      structural_patient=True beats the same router with structural_patient=False by a clear margin (>= +0.03);
  (b) NO-REGRESS: a live SituationReader read with structural_patient ON vs OFF leaves every NON-role output
      byte-identical (n_events / n_entities / coref_acc / n_causal / n_timeline / n_targets), while the PATIENT
      set actually changes (the intended effect -- proves the flag is live);
  (c) the AGENT is byte-identical structural_patient ON vs OFF (P2's cm_agent AGENT competition untouched).

Run: .venv/Scripts/python.exe verification/test_structural_patient_landing_organ.py
Glass-box, NO LLM. Writes nothing. ASCII.
"""
from __future__ import annotations
import glob
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.predicate_argument_frontend import route_predicate_arguments, _cands
import experiments.exp_whodidwhat_ud_structural_v1 as UD

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
LB = os.path.join(_REPO, "data/litbank/coref_conll")


def eval_landed_router(path, tagger, W, parse, max_sents=None):
    """Clean-UD-gold patient accuracy of the LANDED router's THEME, structural_patient OFF vs ON. Goes through
    hdlab.predicate_argument_frontend.route_predicate_arguments (the wired primitive) -- NOT the experiment
    helper -- so this witnesses the SHIPPED code path. quotative=False matches the wired reader's call."""
    sents = UD.load_ud(path)
    if max_sents:
        sents = sents[:max_sents]
    heur = []
    struct = []
    for toks_l, v, pat, passive in UD.gold_items(sents):
        pos = tagger.tag(list(toks_l))
        cands = _cands(pos)
        if not cands:
            continue
        try:
            oh = parse(list(toks_l), pos, W)[0]
        except Exception:
            oh = {}
        off = route_predicate_arguments(toks_l, pos, oh, v, quotative=False, structural_patient=False)["theme"]
        on = route_predicate_arguments(toks_l, pos, oh, v, quotative=False, structural_patient=True)["theme"]
        heur.append(1 if off == pat else 0)
        struct.append(1 if on == pat else 0)
    m = lambda d: (sum(d) / len(d)) if d else 0.0
    return {"n": len(heur), "heuristic": m(heur), "hybrid": m(struct)}


def _summ(sm):
    """(non-role dict, agent signatures, patient signatures) for one read."""
    evs = getattr(sm, "events", []) or []
    agents = tuple((int(getattr(e, "global_idx", -1)), str(getattr(e, "predicate", "")),
                    str(getattr(e, "agent", ""))) for e in evs)
    patients = tuple((int(getattr(e, "global_idx", -1)), str(getattr(e, "predicate", "")),
                      str(getattr(e, "patient", ""))) for e in evs)
    nonrole = {"n_events": len(evs),
               "n_entities": len(getattr(sm, "entities", []) or []),
               "coref_acc": round(float(getattr(sm, "coref_acc", 0.0) or 0.0), 6),
               "n_causal": len(getattr(sm, "causal_links", []) or []),
               "n_timeline": len(getattr(sm, "timeline_frames", []) or []),
               "n_targets": getattr(sm, "n_targets", None)}
    return nonrole, agents, patients


def live_off_vs_on():
    """Read a real LitBank doc through the FULL default reader (cm_agent + referent_per_np + the whole
    default-ON stack), structural_patient OFF vs ON. Only the flag differs."""
    from hdlab.situation_reader import SituationReader
    from hdlab.coref import load_name_gender
    gaz = load_name_gender()
    doc = sorted(glob.glob(os.path.join(LB, "*.conll")))[0]
    off_sm = SituationReader(gaz=gaz, structural_patient=False).read(doc)
    on_sm = SituationReader(gaz=gaz, structural_patient=True).read(doc)
    off_nr, off_ag, off_pt = _summ(off_sm)
    on_nr, on_ag, on_pt = _summ(on_sm)
    n_pat_changed = sum(1 for a, b in zip(off_pt, on_pt) if a != b)
    n_ag_changed = sum(1 for a, b in zip(off_ag, on_ag) if a != b)
    return {"doc": os.path.basename(doc),
            "nonrole_identical": off_nr == on_nr, "off_nr": off_nr, "on_nr": on_nr,
            "agents_identical": off_ag == on_ag, "n_agent_changed": n_ag_changed,
            "n_patient_changed": n_pat_changed, "n_events": off_nr["n_events"]}


def main():
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    checks = []

    # (a) the LANDED router reproduces the clean-UD-gold win
    ev = eval_landed_router(UD_TEST, tagger, W, parse_with_conf, max_sents=600)
    margin = ev["hybrid"] - ev["heuristic"]
    checks.append(("(a) LANDED router structural_patient ON beats OFF by >= 0.03 on clean UD gold",
                   margin >= 0.03,
                   "ON %.4f vs OFF %.4f (+%.4f), n=%d" % (ev["hybrid"], ev["heuristic"], margin, ev["n"])))

    # (b)+(c) live no-regress: non-role byte-identical + AGENT byte-identical; PATIENT changes (flag is live)
    lv = live_off_vs_on()
    checks.append(("(b) live reader NON-role outputs byte-identical ON vs OFF",
                   lv["nonrole_identical"],
                   "off=%s on=%s" % (lv["off_nr"], lv["on_nr"])))
    checks.append(("(b') the PATIENT set actually changes ON vs OFF (the flag is live)",
                   lv["n_patient_changed"] > 0,
                   "patients changed=%d/%d events" % (lv["n_patient_changed"], lv["n_events"])))
    checks.append(("(c) AGENT byte-identical ON vs OFF (P2 cm_agent competition untouched)",
                   lv["agents_identical"],
                   "agents changed=%d/%d events (doc %s)" % (lv["n_agent_changed"], lv["n_events"], lv["doc"])))

    npass = 0
    print("=" * 78)
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed" % (npass, len(checks)))
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
