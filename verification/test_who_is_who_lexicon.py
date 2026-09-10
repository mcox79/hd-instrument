"""Witness: the promoted `hdlab.who_is_who_lexicon` durable knowledge asset is BYTE-IDENTICAL to the name-bridge
solver's original inline lexicons, and the experiment now imports it (grown-knowledge incorporation, 2026-09-10).

Guards the incorporation invariant: promoting the grown who-is-who relational lexicon to a durable, registered
hdlab asset must not change any value the generative type-file accrues from. If this passes, the two name-bridge
reverify witnesses (test_namebridge_generative.py 11/11, test_namebridge_worldknowledge.py 9/9) are unaffected.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab import who_is_who_lexicon as L

# The ORIGINAL values, transcribed from the solver cell BEFORE the repoint (the ground truth the asset must match).
_ORIG_TITLE_ROLE = {"professor": "professor", "prof": "professor", "dr": "doctor", "president": "president",
                    "senator": "senator", "saint": "saint", "st": "saint", "pope": "pope", "king": "king",
                    "queen": "queen", "emperor": "emperor", "governor": "governor", "mayor": "mayor",
                    "captain": "captain", "general": "general", "judge": "judge", "chief": "chief",
                    "duke": "duke", "earl": "earl", "lord": "man", "lady": "woman", "abba": "monk", "apa": "monk",
                    "sir": "man", "dame": "woman", "father": "priest", "reverend": "priest", "rabbi": "rabbi",
                    "sheikh": "leader", "sultan": "ruler", "tsar": "ruler", "prince": "prince",
                    "princess": "princess"}
_ORIG_TITLES = set(_ORIG_TITLE_ROLE) | {"mr", "mrs", "ms", "miss"}

_ORIG_POSSESSED = {}
def _add(words, types):
    for w in words.split():
        _ORIG_POSSESSED[w] = tuple(types)
_add("capital border boundary president government parliament senate economy population citizen coast army "
     "flag currency province governor territory constitution", ("country", "nation", "state", "location"))
_add("ceo founder cofounder headquarters employee staff board chairman spokesman spokesperson revenue "
     "profit subsidiary branch division membership", ("organization", "company", "institution"))
_add("member chapter congregation", ("organization", "group"))
_add("album song single symphony concerto sonata composition band tour discography", ("musician", "composer", "artist"))
_add("book novel poem essay memoir writings prose poetry", ("writer", "author"))
_add("painting portrait sculpture artwork mural fresco", ("painter", "artist"))
_add("film movie documentary screenplay", ("director", "filmmaker"))
_add("wife husband mother father son daughter brother sister widow parents child children family", ("person",))


def main():
    checks = []

    # 1-3: byte-identical maps
    checks.append(("T1 TITLE_ROLE identical", L.TITLE_ROLE == _ORIG_TITLE_ROLE))
    checks.append(("T2 TITLES identical", L.TITLES == _ORIG_TITLES))
    checks.append(("T3 POSSESSED_TYPE identical", L.POSSESSED_TYPE == _ORIG_POSSESSED))

    # 4: expected sizes (78-entry relational lexicon per the solver note)
    checks.append(("T4 sizes 33/37/78", len(L.TITLE_ROLE) == 33 and len(L.TITLES) == 37 and len(L.POSSESSED_TYPE) == 78))

    # 5: accessors agree with the maps
    checks.append(("T5 possessed_type accessor", L.possessed_type("Capital") == L.POSSESSED_TYPE["capital"]
                   and L.possessed_type("nope") == ()))
    checks.append(("T6 title_role accessor", L.title_role("President") == "president" and L.title_role("nope") == ""))
    checks.append(("T7 is_title accessor", L.is_title("MR") and not L.is_title("banana")))

    # 8: the experiment now imports the SAME objects (single source of truth, not a copy)
    import experiments.exp_namebridge_generative_typefile_v1 as E
    checks.append(("T8 experiment imports the asset (is-identity)",
                   E._TITLE_ROLE is L.TITLE_ROLE and E._POSSESSED_TYPE is L.POSSESSED_TYPE and E._TITLES is L.TITLES))

    npass = sum(1 for _, ok in checks if ok)
    print("PASS %d/%d witnesses:" % (npass, len(checks)))
    for name, ok in checks:
        print("  [%s] %s" % ("OK" if ok else "XX", name))
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
