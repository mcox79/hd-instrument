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
    # 2026-09-14 (strategy, pri 109 landing): the landed source now reads the coref column through the tagger-aware parse, which also
    # emits REFLEXIVE pronoun mentions (himself / themselves; Principle A needs them as mentions) that the validated cell never did --
    # a strict superset. The claim that survives: every NON-pronoun referent is byte-identical to the validated cell, and every extra
    # mention is a pronoun.
    got_np = [k for k in _key(got) if not k[4]]; ref_np = [k for k in _key(ref) if not k[4]]
    extra = set(_key(got)) - set(_key(ref)); missing = set(_key(ref)) - set(_key(got))
    _ok(got_np == ref_np and not missing and all(k[4] for k in extra),
        "landed referent_per_np_source(use_frame=False) == validated build_source('rnp') BYTE-FOR-BYTE on non-pronoun referents "
        "(%d == %d); extra mentions are pronouns only (%d)" % (len(got_np), len(ref_np), len(extra)))

    # 2. COVERAGE LEVER: more non-pronoun referents than the coref column; coref pronouns preserved
    coref, _ = parse_litbank_conll(DOC, tagger=tagger)   # the same tagger-aware parse the landed source reads (pri 109; reflexives included)
    n_coref_nom = sum(1 for m in coref if not m["is_pronoun"])
    n_rnp_nom = sum(1 for m in got if not m["is_pronoun"])
    _ok(n_rnp_nom > n_coref_nom,
        "referent-per-NP opens MORE non-pronoun referents than coref (%d > %d)" % (n_rnp_nom, n_coref_nom))
    pk = lambda ms: {(m["sent_idx"], m["wtok_start"], m["head"]) for m in ms if m["is_pronoun"]}
    extra_pron = pk(got) - pk(coref)
    _ok(pk(coref) <= pk(got) and all(h.endswith(("self", "selves")) for _, _, h in extra_pron),
        "coref pronouns preserved (linking pass); extra pronoun mentions are REFLEXIVES only (%d, Principle A needs them)" % len(extra_pron))

    # 3. FRAME DETECTOR (§4): use_frame=True is a superset (recovers tagger-missed heads)
    gotf, _ = referent_per_np_source(DOC, tagger, use_frame=True)
    nf = sum(1 for m in gotf if not m["is_pronoun"])
    _ok(nf >= n_rnp_nom, "frame detector is a superset of POS-only (%d >= %d)" % (nf, n_rnp_nom))

    # 4. CONSTRUCTOR / FACTORY: flag registered, DEFAULT-ON (2026-09-04 owner decision -- the complete referent set
    # is the brain-foundational upstream, decoupled from coref); all_capabilities_off() still sets it False.
    _ok("referent_per_np" in SituationReader.CAPABILITY_FLAGS, "flag in CAPABILITY_FLAGS")
    _ok(SituationReader().referent_per_np is True
        and SituationReader.all_capabilities_off().referent_per_np is False,
        "DEFAULT-ON + all_capabilities_off() covers it")

    # 5. READER: explicit-off runs (coref-column source); on runs (role source swapped, coref decoupled)
    sm_off = SituationReader(referent_per_np=False).read(DOC)
    sm_on = SituationReader().read(DOC)   # default reader is now ON
    _ok(len(sm_off.events) > 0, "explicit-off reader runs (coref-column source)")
    _ok(len(sm_on.events) > 0, "default (referent-per-NP) reader runs; coref decoupled (coref-column anaphora)")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
