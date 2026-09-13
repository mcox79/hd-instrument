#!/usr/bin/env python3
"""hdlab/morphology.py -- the ONE glass-box morphological-decomposition organ (LANDED 2026-09-12 from the owner-DONE
problem the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition; verbatim from
experiments/glassbox_morphology.py; reverified 4/4 first-hand). Every read-path morphy call in hdlab now routes here.

BRAIN STRUCTURE (PINNED, one structure): visual-word-form morphological decomposition. The written form is
segmented into stem + affix EARLY and form-based (Rastle & Davis 2008, morpho-orthographic segmentation), the
candidate stem is CHECKED against the lexicon (Taft 1979 affix-stripping + lexical decision), and irregulars are
STORED whole on a separate route (Pinker-Ullman words-and-rules dual-route: went->go, mice->mouse). That is EXACTLY
the computation WordNet `morphy` performs -- an exception STORE + affix-detachment RULES + a lexical CHECK -- so this
organ copies morphy's COMPUTATION verbatim and reads the DATA (WordNet's exception lists + lemma-pos membership)
from a one-time offline export (data/frontend_assets/morphology/, built by build_glassbox_morphology_asset_v1.py).

NO nltk / NO WordNet / NO external tool is imported at inference. This removes the last non-glass-box rung on the
meaning chain (FULL_CHAIN_BF_AUDIT rung 1). Output is BYTE-IDENTICAL to `wn.morphy` (proven exhaustively by
exp_glassbox_morphy_byte_identity_v1.py). ASCII, glass-box, deterministic.
"""
from __future__ import annotations
import json
import os
from typing import Dict, List, Optional, Set

__bf_status__ = "BF"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-12 strategy landing of the owner-DONE glass-box morphology solution: exception store + affix-detachment "
                   "rules + lexical check (Rastle-Davis morpho-orthographic segmentation; Taft affix stripping; Pinker-Ullman dual route) "
                   "from a one-time offline WordNet export; 0 divergences vs nltk morphy over 6.3M comparisons; no nltk at inference")
__bf_note__ = "the dual-route OPTIMUM (exceeds morphy +0.023 on human gold lemmas) is a recorded follow-on: enable only with the lemma-keyed stores rebuilt"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSET_DIR = os.path.join(_REPO, "data", "frontend_assets", "morphology")

# nltk POS_LIST -- the order morphy tries when pos=None (noun, verb, adj, adv). Snapshotted + self-tested.
POS_LIST = ["n", "v", "a", "r"]

# morphy's affix-detachment RULES, copied VERBATIM from nltk 3.9.4 wordnet.MORPHOLOGICAL_SUBSTITUTIONS. This is the
# COMPUTATION (the brain's suffix-stripping rule set), not fitted data. _self_test_rules() verifies it still matches
# the vendored nltk snapshot in the asset, so an nltk upgrade cannot silently diverge the algorithm.
MORPHOLOGICAL_SUBSTITUTIONS: Dict[str, List] = {
    "n": [("s", ""), ("ses", "s"), ("ves", "f"), ("xes", "x"), ("zes", "z"),
          ("ches", "ch"), ("shes", "sh"), ("men", "man"), ("ies", "y")],
    "v": [("s", ""), ("ies", "y"), ("es", "e"), ("es", ""), ("ed", "e"),
          ("ed", ""), ("ing", "e"), ("ing", "")],
    "a": [("er", ""), ("est", ""), ("er", "e"), ("est", "e")],
    "r": [],
}


class GlassBoxMorphology:
    """Pure-python byte-identical replica of nltk WordNet's morphy (exception store + detachment rules + lexical
    check), reading a static offline export. No nltk at inference."""

    # WordNet POS constants -- so this instance is a drop-in for the `wn` object the call sites use
    # (they write wn.morphy(x, wn.NOUN)); only the morphy subset is provided, by design.
    NOUN = "n"
    VERB = "v"
    ADJ = "a"
    ADV = "r"

    def __init__(self, asset_dir: str = _ASSET_DIR):
        self.asset_dir = asset_dir
        self._exc: Optional[Dict[str, Dict[str, List[str]]]] = None
        self._members: Optional[Dict[str, Set[str]]] = None

    # -- lazy asset load (pay nothing until first morphy call, mirroring the current lazy WordNet load) -----------
    def _ensure(self):
        if self._members is not None:
            return
        with open(os.path.join(self.asset_dir, "morph_exceptions.json"), encoding="ascii") as fh:
            self._exc = json.load(fh)
        members: Dict[str, Set[str]] = {}
        for pos in POS_LIST:
            with open(os.path.join(self.asset_dir, "lemmas_%s.txt" % pos), encoding="ascii") as fh:
                txt = fh.read()
            members[pos] = set(txt.split("\n")) if txt else set()
        self._members = members

    # -- EXACT port of nltk 3.9.4 WordNetCorpusReader._morphy -----------------------------------------------------
    def _morphy(self, form: str, pos: str, check_exceptions: bool = True) -> List[str]:
        self._ensure()
        exceptions = self._exc[pos]
        substitutions = MORPHOLOGICAL_SUBSTITUTIONS[pos]
        members = self._members[pos]

        def apply_rules(forms: List[str]) -> List[str]:
            return [f[: -len(old)] + new for f in forms for (old, new) in substitutions if f.endswith(old)]

        def filter_forms(forms: List[str]) -> List[str]:
            result: List[str] = []
            seen: Set[str] = set()
            for f in forms:
                if f in members and f not in seen:
                    result.append(f)
                    seen.add(f)
            return result

        if check_exceptions and form in exceptions:
            forms = exceptions[form]
        else:
            forms = apply_rules([form])
        return filter_forms([form] + forms)

    # -- EXACT port of nltk 3.9.4 WordNetCorpusReader.morphy ------------------------------------------------------
    def morphy(self, form: str, pos: Optional[str] = None, check_exceptions: bool = True) -> Optional[str]:
        for p in ([pos] if pos else POS_LIST):
            analyses = self._morphy(form, p, check_exceptions)
            if analyses:
                return analyses[0]
        return None

    # -- self-test: the hardcoded rules must equal the vendored nltk snapshot exported into the asset -------------
    def self_test_rules(self) -> bool:
        with open(os.path.join(self.asset_dir, "morph_substitutions.json"), encoding="ascii") as fh:
            snap = json.load(fh)
        assert snap["POS_LIST"] == POS_LIST, ("POS_LIST drift", snap["POS_LIST"], POS_LIST)
        for pos in POS_LIST:
            snap_rules = [tuple(pair) for pair in snap["MORPHOLOGICAL_SUBSTITUTIONS"][pos]]
            assert snap_rules == MORPHOLOGICAL_SUBSTITUTIONS[pos], ("rule drift", pos, snap_rules,
                                                                    MORPHOLOGICAL_SUBSTITUTIONS[pos])
        return True


# module-level default instance + free functions mirroring `wn.morphy`
_DEFAULT: Optional[GlassBoxMorphology] = None


def default_morphology() -> GlassBoxMorphology:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = GlassBoxMorphology()
    return _DEFAULT


def morphy(form: str, pos: Optional[str] = None, check_exceptions: bool = True) -> Optional[str]:
    """Drop-in for wn.morphy: surface form -> base lemma (or None), byte-identical to nltk WordNet 3.0 morphy."""
    return default_morphology().morphy(form, pos, check_exceptions)


if __name__ == "__main__":
    m = default_morphology()
    assert m.self_test_rules()
    for f, p in [("dogs", "n"), ("went", "v"), ("mice", "n"), ("running", "v"), ("axes", "n"),
                 ("leaves", "n"), ("leaves", "v"), ("men", "n"), ("better", "a"), ("test", None)]:
        print("%-10s %-4s -> %s" % (f, p, m.morphy(f, p)))
    print("self_test_rules: OK")
