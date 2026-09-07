"""gender_organ -- a brain-foundational, GLASS-BOX natural-gender inference organ (NO gold, NO LLM).

Promoted 2026-09-07 from exp_gender_organ_gum_v1.GenderOrganizer (owner-DONE p12
compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain, Finding 5).

WHY: English pronominal gender is a NATURAL-gender system (Quirk 1985; Corbett 1991) -- gender tracks the
referent's real-world properties via NAME, LEXICAL, and MORPHOLOGICAL cues, not grammatical class. The coref
agreement-narrow needs each entity's gender; the p12 drill discovered the established GUM eval harness fed
entity gender from GUM's GOLD `Gender` feat (gold at inference -- a hidden leak). This organ replaces that with
a glass-box source. On the full +0.082 coref stack it MATCHES the gold-gender leak (delta +0.003, 100%
agreement where both fire, coverage 5.8% vs gold 5.2%) -> the whole stack runs with NO gold at inference.

CAP (quantified, honest): gender is SPARSE on modern nominals -- only ~6% carry ANY gender cue; the other ~94%
are genuinely genderless common nouns (person / teacher / writer / friend). So this is a leak-removal / fidelity
win, NOT a big accuracy lever. Do NOT wire confidence-gated coreferent gender PROPAGATION (measured net-negative
even gated: the graded pick is not confident-enough-often-enough for propagating its 35-40%-wrong gender to pay).

LIVE-PATH NOTE (2026-09-07): the deployed reader (hdlab.situation_reader) already sources gender GLASS-BOX --
hdlab.coref.parse_litbank_conll derives nominal gender from state_of_mind.infer_nominal_gender (title/kinship
cues) + the name->gender gazetteer, NEVER a gold Gender feat. So there is NO gold leak in the live path to
remove; this organ is a RICHER superset of those cues (adds an occupational/role lexicon + gendered morphology)
promoted here for the GUM eval / a future modern board coref instrument to consume in place of the harness's
gold-gender bridge. It is a strict superset of infer_nominal_gender's cues (a name-in-gazetteer or a title/
kinship head resolves identically), so a consumer may swap it in without a recall loss.

Reuse: hdlab.state_of_mind.MASC_CUES / FEM_CUES / POSSESSIVE_DETERMINER_CUES; hdlab.coref.name_content_tokens.
GLASS-BOX: pure symbolic; NO torch, NO external LLM, NO network. ASCII-only, no em-dash.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from hdlab.coref import name_content_tokens
from hdlab.state_of_mind import MASC_CUES, FEM_CUES, POSSESSIVE_DETERMINER_CUES

# Curated role/occupational noun gender lexicon (lexical-semantic gender facts; NOT tuned to any document).
MASC_ROLES = frozenset("""waiter businessman chairman spokesman congressman policeman fireman salesman mailman
postman fisherman gunman monk priest groom bachelor boyfriend stepfather godfather headmaster emperor duke earl
baron count knight nephew widower stepson grandson landlord wizard prince husband monk friar bishop pope
gentleman lad manservant""".split())
FEM_ROLES = frozenset("""waitress actress hostess heroine businesswoman chairwoman spokeswoman congresswoman
policewoman saleswoman nun priestess bride spinster girlfriend stepmother godmother headmistress goddess countess
duchess empress niece stepdaughter granddaughter landlady witch queen stewardess heiress seamstress governess
gentlewoman lass maidservant mistress abbess""".split())
FEM_ESS = frozenset("""actress waitress hostess princess countess duchess goddess stewardess heiress seamstress
governess mistress empress headmistress lioness tigress priestess patroness enchantress murderess adventuress
abbess""".split())

# Gendered cue sets (drop the plain pronoun forms -- a pronoun is not a nominal gender cue on a nominal span).
_MASC = (MASC_CUES | MASC_ROLES) - {"he", "him", "his", "himself"}
_FEM = (FEM_CUES | FEM_ROLES) - {"she", "her", "hers", "herself"}


class GenderOrganizer:
    """Glass-box natural-gender inference: name gazetteer + lexical role lexicon + gendered morphology.

    infer(span_toks, is_name) -> 'masc' | 'fem' | None (unknown). Precedence:
      1. NAME  -> given-name gazetteer (a static offline asset; the caller supplies it).
      2. LEXICAL -> title/kinship cues (state_of_mind) + curated role/occupational lexicon; the possessive
         DETERMINER is stripped so "his mother" -> head 'mother' (fem), the possessor's gender does not leak.
      3. MORPHOLOGY -> gendered compounds/suffixes on the head token (-woman/-man, -girl/-boy, -ess,
         -master/-mistress/-lord).
    NO gold, NO LLM.
    """

    def __init__(self, name_gaz: Optional[Dict[str, str]] = None) -> None:
        self.name_gaz = name_gaz or {}

    def infer(self, span_toks: Sequence[str], is_name: bool) -> Optional[str]:
        toks = [t.lower().strip(".,'\"!?;:") for t in (span_toks or [])]
        if is_name:                                            # NAME -> given-name gazetteer
            for t in name_content_tokens(list(span_toks or [])):
                if t in self.name_gaz:
                    return self.name_gaz[t]
        cue = set(toks) - POSSESSIVE_DETERMINER_CUES           # "his mother" -> head 'mother', ignore 'his'
        if not cue:
            cue = set(toks)
        m = bool(cue & _MASC)
        f = bool(cue & _FEM)
        if m and not f:
            return "masc"
        if f and not m:
            return "fem"
        return self._morph(toks[-1] if toks else "")           # morphology on the head token

    @staticmethod
    def _morph(w: str) -> Optional[str]:
        if not w:
            return None
        if w.endswith("woman") or w.endswith("women") or w.endswith("girl") or w.endswith("lady") or w in FEM_ESS:
            return "fem"
        if (w.endswith("man") or w.endswith("men") or w.endswith("boy") or w.endswith("master")
                or w.endswith("lord")) and not (w.endswith("woman") or w.endswith("women")):
            return "masc"
        return None


# ===================== formula self-tests ==========================================

def _selftest_spot_checks() -> None:
    """Glass-box spot-checks (name gazetteer + lexical + morphology + the possessive-determiner guard)."""
    org = GenderOrganizer({"elizabeth": "fem", "john": "masc"})
    assert org.infer(["Elizabeth"], True) == "fem"
    assert org.infer(["John"], True) == "masc"
    assert org.infer(["the", "waitress"], False) == "fem"
    assert org.infer(["a", "businessman"], False) == "masc"
    assert org.infer(["his", "mother"], False) == "fem"        # possessive-determiner guard
    assert org.infer(["her", "father"], False) == "masc"       # possessor gender must not leak
    assert org.infer(["the", "spokeswoman"], False) == "fem"   # morphology
    assert org.infer(["the", "table"], False) is None          # genderless common noun
    assert org.infer(["a", "person"], False) is None           # the ~94% genderless case (the sparsity cap)


def _selftest_superset_of_infer_nominal_gender() -> None:
    """The organ is a strict SUPERSET of state_of_mind.infer_nominal_gender's title/kinship cues: wherever
    that resolves a (non-name) span, the organ agrees (so a live consumer can swap it in without a recall loss)."""
    from hdlab.state_of_mind import infer_nominal_gender
    org = GenderOrganizer({})
    for span in (["mr", "bennet"], ["the", "lady"], ["his", "father"], ["her", "sister"], ["the", "king"],
                 ["the", "widow"], ["a", "gentleman"], ["the", "street"], ["the", "idea"]):
        base = infer_nominal_gender(span)
        if base is not None:
            assert org.infer(span, False) == base, (span, base, org.infer(span, False))


def _run_all_selftests() -> dict:
    _selftest_spot_checks()
    _selftest_superset_of_infer_nominal_gender()
    return {"masc_roles": len(MASC_ROLES), "fem_roles": len(FEM_ROLES), "fem_ess": len(FEM_ESS),
            "reuse": ["state_of_mind.MASC_CUES/FEM_CUES/POSSESSIVE_DETERMINER_CUES", "coref.name_content_tokens"]}


if __name__ == "__main__":
    r = _run_all_selftests()
    print("[gender_organ selftest] PASS %s" % r)
