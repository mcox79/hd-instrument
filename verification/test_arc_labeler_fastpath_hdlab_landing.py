"""LANDED-hdlab witness: hdlab/arc_labeler.py ArcLabeler.label() now routes through the byte-identical
_FastLabelPlan (Q111 landing of add_the_arc_labeler_fast_scoring_path). Confirms the LANDED code path (not the
experiment's) is byte-identical to the retained reference _predict_label, and the opt-in graded readout is byte-safe.

  L1  the landed ArcLabeler builds a _FastLabelPlan lazily via _ensure_fast (idempotent).
  L2  label() (fast path) == per-arc _predict_label (the retained reference) on HELD-OUT LitBank arcs
      (reader live frontend, predicted heads) -- 0 mismatches.
  L3  label() == reference on HELD-OUT UD-EWT TEST arcs (gold heads) -- a second disjoint population.
  L4  label_graded() argmax == label() (MAP-optimality: the graded readout regresses nothing, byte-safe).

Run: .venv/Scripts/python.exe verification/test_arc_labeler_fastpath_hdlab_landing.py
"""
from __future__ import annotations
import os, sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
import hdlab.arc_labeler as AL
from experiments.exp_arc_labeler_graded_competition_v1 import read_conllu, UD_TEST

PASS = 0; FAIL = 0
_HELD = ["105_persuasion_brat", "113_the_secret_garden_brat", "120_treasure_island_brat"]
_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json")


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok; FAIL += (not ok)
    return ok


def _reference_labels(ref: AL.ArcLabeler, toks, pos, heads, n):
    """Labels via the retained stock reference _predict_label (NOT the fast path)."""
    out = {}
    for i in range(1, n + 1):
        h = heads.get(i, 0)
        if h is None or h < 0 or h > n:
            h = 0
        out[i] = ref._predict_label(AL.arc_features(toks, pos, i, h))
    return out


def main():
    print("witness: arc-labeler fast path LANDED in hdlab -- label() byte-identical to the reference")
    lab = AL.ArcLabeler.load(_ASSET)
    # L1 -- lazy fast plan
    before = lab._fast
    plan = lab._ensure_fast()
    chk("L1 _ensure_fast builds a _FastLabelPlan lazily + idempotent",
        before is None and isinstance(plan, AL._FastLabelPlan) and lab._ensure_fast() is plan)

    # L2 -- held-out LitBank arcs via the reader's live frontend (predicted heads)
    gaz = SITQA.load_given_gazetteer()
    reader = SituationReader(gaz=gaz)
    tagger = reader._frontend_tagger(); parser = reader._frontend_parser()
    mism = ntot = 0
    for doc in _HELD:
        p = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(p):
            continue
        for toks in SITQA._conll_sents(p):
            if not toks or len(toks) > 60:
                continue
            up = tagger.tag(list(toks)); heads = parser.parse(list(toks), up).heads
            fast = lab.label(list(toks), up, heads)                       # LANDED fast path
            ref = _reference_labels(lab, list(toks), up, heads, len(toks))  # retained reference
            for i in ref:
                ntot += 1; mism += int(fast.get(i) != ref[i])
    chk("L2 landed label() == reference _predict_label on held-out LitBank arcs", mism == 0,
        "%d mismatches / %d arcs" % (mism, ntot))

    # L3 -- held-out UD-EWT TEST (gold heads)
    sents = read_conllu(UD_TEST)[:1500]
    m2 = n2 = 0
    for s in sents:
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        heads = {}
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            heads[i] = gh if 0 <= gh <= len(s) else 0
        fast = lab.label(toks, pos, heads)
        ref = _reference_labels(lab, toks, pos, heads, len(s))
        for i in ref:
            n2 += 1; m2 += int(fast.get(i) != ref[i])
    chk("L3 landed label() == reference on held-out UD-EWT TEST arcs (gold heads)", m2 == 0,
        "%d mismatches / %d arcs" % (m2, n2))

    # L4 -- graded readout argmax == label() (byte-safe MAP-optimality); entropy a sane normalized value
    toks = ["the", "wolf", "bit", "the", "sheep"]; pos = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    heads = {1: 2, 2: 3, 3: 0, 4: 5, 5: 3}
    hard = lab.label(toks, pos, heads)
    graded = lab.label_graded(toks, pos, heads)
    argmatch = sum(1 for i in hard if graded[i][0] == hard[i])
    ents = [graded[i][2] for i in hard]
    ent_ok = all((-1e-9 <= e <= 1.0 + 1e-6) for e in ents)
    ok = (argmatch == len(hard)) and ent_ok
    chk("L4 label_graded argmax == label (MAP-optimality byte-safe); entropy normalized", ok,
        "argmax %d/%d; entropy=[%s] in[0,1]=%s" % (argmatch, len(hard),
        ",".join("%.3f" % e for e in ents), ent_ok))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
