"""test_labeled_patient_landing -- LANDING WITNESS for the labeled who-did-what PATIENT readout
(owner-DONE improve_the_parser_verb_argument_attachment_for_who_did_what, Q111 strategy landing 2026-09-04).

Asserts the PROMOTED hdlab.predicate_argument_frontend.structural_patient_pick is BYTE-FAITHFUL to the
validated experiment drop-in (exp_valency_labeled_live_reader_v1.improved_structural_patient_pick =
exp_valency_labeled_patient_v1.labeled_pick + precise voice + net-safe hybrid fallback), and reproduces the
+0.086 patient lift over the prior position readout on clean UD-EWT. Glass-box, NO LLM. ASCII.

  W1  byte-identity: landed pick == reference drop-in pick on EVERY UD-EWT test gold item (0 mismatches).
  W2  the landed readout beats the prior position/robust_passive floor CI-consistent (>= +0.05) toward 0.831.

Run: .venv/Scripts/python.exe verification/test_labeled_patient_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.predicate_argument_frontend as PAF
import experiments.exp_valency_labeled_patient_v1 as VLP
import experiments.exp_whodidwhat_ud_structural_v1 as UD
from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.arc_labeler import ArcLabeler
from hdlab.relcl_resolver import precise_passive, _cands
from hdlab.graded_role_assigner import hybrid_role_patient

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
LAB_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")

_LAB = ArcLabeler.load(LAB_ASSET)


def _ref_pick(toks, pos, heads, v):
    """The validated drop-in reference (improved_structural_patient_pick body), independent of hdlab."""
    labels = _LAB.label(list(toks), list(pos), heads)
    pp = precise_passive(toks, pos, v)
    pick = VLP.labeled_pick(toks, pos, v, heads, labels, pp, valency=True)
    if pick is None:
        pick = hybrid_role_patient(toks, pos, v, cands=_cands(pos), np_head_reduce=False)
    return pick


def _prior_position_pick(toks, pos, heads, v):
    """The prior deployed floor: position readout + robust_passive (via the frozen exp reference)."""
    return VLP._deployed_structural_patient_pick(toks, pos, heads, v)


def main():
    tagger = PosTagger.load(POS_ASSET)
    arc = ArcParser.load(ARC_ASSET)
    sents = UD.load_ud(UD_TEST)
    mism = 0; n = 0
    land_hits = 0; prior_hits = 0
    for s in sents:
        toks = [t["form"] for t in s]
        pos = tagger.tag(list(toks))
        try:
            heads = arc.parse(toks, pos).heads
        except Exception:
            heads = {}
        gold = []
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]; deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
            pat = None
            for d in deps:
                if not passive and d["dep"] == "obj":
                    pat = d["id"]; break
                if passive and d["deprel"].startswith("nsubj:pass"):
                    pat = d["id"]; break
            if pat is not None:
                gold.append((v, pat))
        for (v, pat) in gold:
            landed = PAF.structural_patient_pick(toks, pos, heads, v)
            ref = _ref_pick(toks, pos, heads, v)
            prior = _prior_position_pick(toks, pos, heads, v)
            mism += int(landed != ref)
            n += 1
            land_hits += int(landed == pat)
            prior_hits += int(prior == pat)

    land_acc = land_hits / max(1, n)
    prior_acc = prior_hits / max(1, n)
    print("=== labeled patient landing witness (UD-EWT test, n=%d) ===" % n, flush=True)
    print("W1 byte-identity landed-vs-drop-in mismatches: %d" % mism, flush=True)
    print("W2 landed patient acc %.4f  vs prior position floor %.4f  (delta +%.4f)" % (
        land_acc, prior_acc, land_acc - prior_acc), flush=True)
    assert mism == 0, "landed structural_patient_pick diverges from the validated drop-in on %d items" % mism
    assert land_acc - prior_acc >= 0.05, "landed lift %.4f < +0.05" % (land_acc - prior_acc)
    assert land_acc >= 0.80, "landed acc %.4f below 0.80" % land_acc
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
