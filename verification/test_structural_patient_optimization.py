"""WITNESS: the structure-first PATIENT optimization beats the live cue-heuristic on clean gold AND does not
regress other consumers through the live reader.

Problem: consume_the_graded_pos_posterior_... (the who-did-what drill). The live reader assigns the core patient by
a flat cue/position heuristic (the agrammatic route). Reading the patient off the parse's grammatical relations +
voice remapping (the brain's structural route) -- with a heuristic fallback -- is measurably better and generalizes
(zero tuned parameters). This gate asserts, scaffold-free:
  (1) on CLEAN UD-EWT gold (patient := obj|nsubj:pass off the GOLD relations), the HYBRID structure-first patient
      beats the live heuristic by a clear margin (>= +0.03), on held-out UD test sentences;
  (2) the structural route reaches a HIGH ceiling with a perfect parse (>= 0.85) -- so the residual is parser quality;
  (3) NO-REGRESS: wiring structural patient into the LIVE reader leaves every NON-role output (events, entities,
      coref_acc, causal, timeline, targets) byte-stable on a real doc.

Run: .venv/Scripts/python.exe verification/test_structural_patient_optimization.py
Glass-box, NO LLM. Writes nothing. ASCII.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
import experiments.exp_structural_patient_noregress_v1 as OPT

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")


def main():
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    checks = []

    ev = OPT.eval_patient(UD_TEST, tagger, W, parse_with_conf, max_sents=600)
    margin = (ev["hybrid"] or 0) - (ev["heuristic"] or 0)
    checks.append(("(1) HYBRID structure-first patient beats live heuristic by >= 0.03 (clean UD gold)",
                   margin >= 0.03, "hybrid %.4f vs heuristic %.4f (+%.4f), n=%d" %
                   (ev["hybrid"], ev["heuristic"], margin, ev["n"])))
    checks.append(("(2) structural ceiling (gold parse) >= 0.85 -> residual is parser quality",
                   (ev["ceiling_goldparse"] or 0) >= 0.85, "ceiling %.4f" % ev["ceiling_goldparse"]))

    nr = OPT.no_regress()
    checks.append(("(3) NO-REGRESS: live reader non-role outputs stable under structural patient",
                   nr["completed"] and nr["non_role_outputs_stable"],
                   "stable=%s, themes changed=%d/%d events" % (nr["stable_detail"], nr["n_themes_changed"], nr["n_events"])))

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
