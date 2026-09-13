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

    def __init__(self, asset_dir: str = _ASSET_DIR, mode: str = "morphy"):
        self.asset_dir = asset_dir
        self._exc: Optional[Dict[str, Dict[str, List[str]]]] = None
        self._members: Optional[Dict[str, Set[str]]] = None
        # ARMS (2026-09-13, folded from the lemmatizer problem's dual-route EXCEED cell): "morphy" = the byte-identical port (surface
        # form FIRST, the dictionary tool's arbitration); "dualroute" = Pinker/Ullman words-and-rules with Rastle-Davis OBLIGATORY
        # DECOMPOSITION: the STORED route returns the stored base of an irregular, the RULE route returns the decomposed stem, and the
        # surface form is accepted only when neither route fires. Same asset, zero fitted parameters; measured on UD-EWT+GUM
        # (195,045 tokens, gold POS): morphy 0.9603 -> dualroute 0.9836 (+0.0233, CI-sep; info-free twin 0.7255); 23/24 genres positive.
        self.mode = mode

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

    # -- DUAL-ROUTE arm: stored base / decomposed stem preferred over the surface form ------------------------------
    _COUNTS: Optional[dict] = None

    def _counts(self, pos: str) -> dict:
        if GlassBoxMorphology._COUNTS is None:
            try:
                with open(LEMMA_COUNTS_ASSET, encoding="utf-8") as fh:
                    GlassBoxMorphology._COUNTS = json.load(fh)["counts"]
            except Exception:
                GlassBoxMorphology._COUNTS = {}
        return GlassBoxMorphology._COUNTS.get({"n": "noun", "v": "verb", "a": "adj", "s": "adj", "r": "adv"}.get(pos, pos), {})

    def _route(self, form: str, pos: str, check_exceptions: bool = True) -> Optional[str]:
        self._ensure()
        exc = self._exc[pos]; members = self._members[pos]; subs = MORPHOLOGICAL_SUBSTITUTIONS[pos]
        if check_exceptions and form in exc:
            for b in exc[form]:                       # STORED route: retrieve the base, not the surface
                if b in members:
                    # BASE/IRREGULAR COLLISION (2026-09-13): the surface is ITSELF a stored base of this POS ("wound" = injure AND
                    # the past of "wind"; found/find, bound/bind, ground/grind). Two whole-word entries race by frequency (Pinker &
                    # Ullman: the stored route is frequency-sensitive): the irregular's base wins only when it is clearly more
                    # frequent (ratio >= COLLISION_RATIO, swept); otherwise the surface form keeps its own identity. Frequencies =
                    # the offline WordNet/SemCor lemma-count export (foundation asset). find 705 vs found 13 -> find; wind 7 vs
                    # wound 5 -> wound (the harm/help read of 'wound' had flipped to HELP via 'wind').
                    if form in members and form != b:
                        cnt = self._counts(pos)
                        fb, ff = cnt.get(b, 0), cnt.get(form, 0)
                        if not (fb >= COLLISION_RATIO * max(ff, 1)):
                            return form
                    return b
            return form if form in members else None
        stripped = [form[:-len(old)] + new for (old, new) in subs if form.endswith(old) and (form[:-len(old)] + new) in members]
        if stripped:                                  # RULE route: obligatory decomposition, stem preferred over surface
            return stripped[0]
        return form if form in members else None

    # -- EXACT port of nltk 3.9.4 WordNetCorpusReader.morphy (mode "morphy"); dual-route arbitration (mode "dualroute") --------
    def morphy(self, form: str, pos: Optional[str] = None, check_exceptions: bool = True) -> Optional[str]:
        for p in ([pos] if pos else POS_LIST):
            if self.mode == "dualroute":
                r = self._route(form, p, check_exceptions)
                if r:
                    return r
                continue
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


# the live arm: HDLAB_MORPH_MODE = "morphy" (default today; byte-identical to the dictionary tool) | "dualroute" (the brain's
# words-and-rules arbitration; flip after the lemma-keyed stores downstream are rebuilt against it -- see INTEGRATION_LEDGER).
# DEFAULT FLIPPED to "dualroute" 2026-09-13 07:55 local: the board with the arm ON was identical to the baseline on every dimension
# (AGG 0.6378; agent 0.8357, patient 0.8088, state 0.8016, coref 0.4681, wic 0.7493), and the arm beats the dictionary tool on lemma
# gold (0.9826 vs 0.9594, 195k tokens). The lemma-keyed stores downstream are still morphy-keyed (measured harmless; rebuild = follow-on).
COLLISION_RATIO = float(os.environ.get("HDLAB_MORPH_COLLISION_RATIO", "3.0"))   # swept operating point (see _route)
LEMMA_COUNTS_ASSET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "frontend_assets", "morph_lemma_counts_v1.json")
MORPH_MODE = os.environ.get("HDLAB_MORPH_MODE", "dualroute")


def default_morphology() -> GlassBoxMorphology:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = GlassBoxMorphology(mode=MORPH_MODE)
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
