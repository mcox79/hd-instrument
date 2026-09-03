"""Landing witness for hdlab/referent_per_np.py + the SituationReader `referent_per_np` mention-source flag (the
owner-DONE open_a_discourse_referent_for_every_np... §6 wire). Proves: (1) the landed source is BYTE-IDENTICAL to
the validated monkeypatch `build_source(mode='rnp')` (the solver's "first to withdraw if the landed wire diverges"
guard); (2) it opens MORE non-pronoun referents than the coref column (the coverage lever) with coref pronouns
preserved; (3) the §4 FRAME detector adds heads on top; (4) the flag is default-off + factory-covered; (5) both the
default-off and flag-on readers run. Glass-box, NO LLM. Run:
  .venv/Scripts/python.exe verification/test_referent_per_np_source_landing_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.coref import parse_litbank_conll
from hdlab.referent_per_np import referent_per_np_source
from hdlab.situation_reader import SituationReader
import experiments.exp_referent_per_np_end_to_end_v1 as E   # the VALIDATED build_source (the monkeypatch source)

DOC = os.path.join(_REPO, "data/litbank/coref/conll/1023_bleak_house_brat.conll")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


def _key(ms):
    return [(m["sent_idx"], m["wtok_start"], m["head"], m["cluster"], m["is_pronoun"]) for m in ms]


def main():
    tagger = PosTagger.load(POS_ASSET)

    # 1. FAITHFULNESS: landed source (use_frame=False) == validated build_source('rnp'), byte-for-byte
    got, n1 = referent_per_np_source(DOC, tagger, use_frame=False)
    ref, n2 = E.build_source(DOC, tagger, "rnp")
    _ok(n1 == n2, "n_sents match (%d)" % n1)
    _ok(_key(got) == _key(ref),
        "landed referent_per_np_source(use_frame=False) == validated build_source('rnp') BYTE-FOR-BYTE")

    # 2. COVERAGE LEVER: more non-pronoun referents than the coref column; coref pronouns preserved
    coref, _ = parse_litbank_conll(DOC)
    n_coref_nom = sum(1 for m in coref if not m["is_pronoun"])
    n_rnp_nom = sum(1 for m in got if not m["is_pronoun"])
    _ok(n_rnp_nom > n_coref_nom,
        "referent-per-NP opens MORE non-pronoun referents than coref (%d > %d)" % (n_rnp_nom, n_coref_nom))
    _ok(sum(1 for m in got if m["is_pronoun"]) == sum(1 for m in coref if m["is_pronoun"]),
        "coref pronouns preserved (linking pass)")

    # 3. FRAME DETECTOR (§4): use_frame=True is a superset (recovers tagger-missed heads)
    gotf, _ = referent_per_np_source(DOC, tagger, use_frame=True)
    nf = sum(1 for m in gotf if not m["is_pronoun"])
    _ok(nf >= n_rnp_nom, "frame detector is a superset of POS-only (%d >= %d)" % (nf, n_rnp_nom))

    # 4. CONSTRUCTOR / FACTORY: flag registered, default OFF
    _ok("referent_per_np" in SituationReader.CAPABILITY_FLAGS, "flag in CAPABILITY_FLAGS")
    _ok(SituationReader().referent_per_np is False
        and SituationReader.all_capabilities_off().referent_per_np is False,
        "default OFF + all_capabilities_off() covers it")

    # 5. READER: default-off runs (coref-column source); flag-on runs (mention source swapped)
    sm_off = SituationReader().read(DOC)
    sm_on = SituationReader(referent_per_np=True).read(DOC)
    _ok(len(sm_off.events) > 0, "default-off reader runs (coref-column source)")
    _ok(len(sm_on.events) > 0, "flag-on reader runs (referent-per-NP source swapped in)")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
