"""Witness: the tagger cache-unification sweep (perf #2) is BYTE-IDENTICAL and eliminates redundant tagging.

Problem (strategy optimization, owner "always work to optimize; keep it general"): the reader tagged each
sentence ~4.5x per read() because three organs (tense-agnostic event detection, referent_per_np_source,
the predict-revise candidate path) each carried a PRIVATE PosTagger loaded from the SAME _FRONTEND_POS_ASSET,
bypassing the shared per-read _cached_tag memo. This sweep routes all three through _cached_tag (and passes a
_CachedTagShim into referent_per_np_source), leaving only the different-source forward-prediction tagger.

The guarantee is byte-identity: _cached_tag uses the SAME asset the private taggers loaded, so tags are
deterministically identical. This witness proves:
  1. INVARIANT: reader._cached_tag(toks) == a freshly-loaded private PosTagger(_FRONTEND_POS_ASSET).tag(toks),
     for every held-out sentence (the exact guarantee the sweep relies on).
  2. REDUCED REDUNDANCY: a full default read makes <= 2.0x n_sentences PosTagger.tag calls (was ~4.5x), and
     the eliminated bypass sites (_tense_agnostic_extract / cands_for / referent_per_np_source) no longer tag.
  3. NO-REGRESSION: the reader reads the default doc without error and the shim path (referent_per_np ON) works.

Self-contained (hdlab only). Deterministic. NO LLM. numpy + pure-python.
Run: .venv/Scripts/python.exe verification/test_tagger_cache_unification_sweep.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
import hdlab.situation_reader as SR
from hdlab.situation_reader import SituationReader, _FRONTEND_POS_ASSET

_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")
_DOC = "11_alices_adventures_in_wonderland_brat.conll"

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok
    FAIL += (not ok)
    return ok


def main():
    path = os.path.join(_CONLL, _DOC)
    sents = [list(t) for t in parse_conll_sentences(path)][:71]
    n_sent = len(sents)

    # 1) INVARIANT: shared _cached_tag == a fresh private tagger on the same asset, every sentence
    private = PosTagger.load(_FRONTEND_POS_ASSET)
    r = SituationReader()
    r._read_parse_cache = {}
    mism = 0
    for toks in sents:
        if r._cached_tag(toks) != list(private.tag(toks)):
            mism += 1
    chk("reader._cached_tag == fresh private PosTagger(_FRONTEND_POS_ASSET).tag, every sentence",
        mism == 0, "%d/%d mismatched" % (mism, n_sent))

    # 2) REDUCED REDUNDANCY: full default read makes <= 2.0x n_sentences tag calls (was ~4.5x)
    import collections
    calls = collections.Counter()
    n_total = [0]
    _orig = PosTagger.tag

    def counting_tag(self, toks):
        n_total[0] += 1
        import traceback
        for fr in reversed(traceback.extract_stack()):
            if fr.filename.endswith("situation_reader.py"):
                calls["sr:%s" % fr.name] += 1
                break
            if fr.filename.endswith("referent_per_np.py"):
                calls["rnp:%s" % fr.name] += 1
                break
        return _orig(self, toks)

    PosTagger.tag = counting_tag
    try:
        r2 = SituationReader()
        _, n_doc_sents = __import__("hdlab.coref", fromlist=["parse_litbank_conll"]).parse_litbank_conll(path, name_gender_map=r2.gaz)
        sm = r2.read(path)
    finally:
        PosTagger.tag = _orig
    ratio = n_total[0] / max(n_doc_sents, 1)
    chk("full read tag calls <= 2.0x n_sentences (redundant private-tagger passes eliminated)",
        ratio <= 2.0, "%d calls / %d sents = %.2fx" % (n_total[0], n_doc_sents, ratio))
    # the three eliminated bypass sites must no longer tag
    eliminated = {"sr:_tense_agnostic_extract", "sr:cands_for", "rnp:referent_per_np_source"}
    still = {k: v for k, v in calls.items() if k in eliminated}
    chk("the eliminated bypass sites make ZERO tag calls (routed through the shared cache)",
        not still, "leftover: %s" % (still or "none"))

    # 3) NO-REGRESSION: the read produced a sane situation model through the shim path (referent_per_np ON)
    ok3 = (r2.referent_per_np and len(getattr(sm, "events", []) or []) > 0
           and 0.0 <= float(getattr(sm, "coref_acc", -1)) <= 1.0)
    chk("default read (referent_per_np ON, _CachedTagShim path) produced a sane situation model",
        ok3, "events=%d coref_acc=%.4f" % (len(sm.events or []), getattr(sm, "coref_acc", float("nan"))))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
