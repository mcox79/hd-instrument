"""WHO-IS-WHO relational lexicon -- a DURABLE, brain-foundational KNOWLEDGE ASSET (grown-knowledge incorporation).

PROVENANCE. Grown + curated by the `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual` solver
(owner-DONE 2026-09-09, STRONG). It is the offline, static, glass-box relational lexicon that the online
GENERATIVE WHO-IS-WHO identity file accrues fine per-entity type/role evidence FROM -- the piece that let the
generative situation-model cross the name-bridge residual CI-separated on the document-local subslice
(+0.072/+0.080, witness `verification/test_namebridge_generative.py` 11/11).

WHAT IT IS (three offline maps, NO external tool/LLM at inference -- a static FOUNDATION asset, owner-authorised
"foundation FREE to build"):
  - POSSESSED_TYPE: possessed-noun -> the fine TYPE its possessor most likely is ("X's capital"->country,
    "X's CEO"->organization, "X's album"->musician). Relational world-knowledge, FrameNet/selectional style.
  - TITLE_ROLE:   an honorific/title -> the fine ROLE-IDENTITY it names ("President Chao"->president, not just
    "person"). A title IS a stored role-identity node (Bruce-Young: occupation/role is identity knowledge).
  - TITLES:       the honorific set (TITLE_ROLE keys + generic mr/mrs/ms/miss -> person+gender only).

BRAIN-FOUNDATIONAL BASIS. Heim 1982 file-change semantics (each entity is an online file that accrues who-is-who
predicates); Bruce-Young/IAC identity nodes (role/occupation is stored identity knowledge, retrieved by title);
relational/selectional semantics (a possessed noun is type-diagnostic of its possessor). GLASS-BOX + OFFLINE:
the fine type is FINE (not the coarse PLACE/PERSON flag that over-licenses -- a measured located negative) and is
consumed as GRADED soft evidence, never a hard flag.

CONSUMER. The online generative who-is-who identity file (the generative-world-model program's entity layer);
fed THROUGH the `safe_kb_gate` familiarity gate when composed with any broad KB. This module is the SINGLE source
of truth for the two lexicons -- `experiments/exp_namebridge_generative_typefile_v1.py` imports them from here
(byte-identical to the original inline definitions; witness `verification/test_who_is_who_lexicon.py`).

INVARIANT: pure data + pure accessors. No I/O, no model, no import of a heavy dependency. Additive: importing this
module changes nothing that does not opt in to it.
"""

from __future__ import annotations

from typing import Dict, Sequence, Tuple

__all__ = ["POSSESSED_TYPE", "TITLE_ROLE", "TITLES", "possessed_type", "title_role", "is_title"]

# --- TITLE -> the FINE ROLE it identifies (who-is-who, not just "person"): a title IS a role-identity node
# (Bruce-Young: occupation/role is stored identity knowledge). Generic honorifics (mr/mrs/...) -> person+gender only.
TITLE_ROLE: Dict[str, str] = {
    "professor": "professor", "prof": "professor", "dr": "doctor", "president": "president",
    "senator": "senator", "saint": "saint", "st": "saint", "pope": "pope", "king": "king",
    "queen": "queen", "emperor": "emperor", "governor": "governor", "mayor": "mayor",
    "captain": "captain", "general": "general", "judge": "judge", "chief": "chief",
    "duke": "duke", "earl": "earl", "lord": "man", "lady": "woman", "abba": "monk", "apa": "monk",
    "sir": "man", "dame": "woman", "father": "priest", "reverend": "priest", "rabbi": "rabbi",
    "sheikh": "leader", "sultan": "ruler", "tsar": "ruler", "prince": "prince", "princess": "princess",
}
TITLES = set(TITLE_ROLE) | {"mr", "mrs", "ms", "miss"}

# --- POSSESSED-NOUN -> the fine TYPE the possessor most likely is (relational world-knowledge; FrameNet/selectional
# style; offline curated lexicon of what predicates apply to what kinds). Maps to WordNet anchor lemmas.
POSSESSED_TYPE: Dict[str, Tuple[str, ...]] = {}


def _add(words: str, types: Tuple[str, ...]) -> None:
    for w in words.split():
        POSSESSED_TYPE[w] = tuple(types)


_add("capital border boundary president government parliament senate economy population citizen coast army "
     "flag currency province governor territory constitution", ("country", "nation", "state", "location"))
_add("ceo founder cofounder headquarters employee staff board chairman spokesman spokesperson revenue "
     "profit subsidiary branch division membership", ("organization", "company", "institution"))
_add("member chapter congregation", ("organization", "group"))
_add("album song single symphony concerto sonata composition band tour discography", ("musician", "composer", "artist"))
_add("book novel poem essay memoir writings prose poetry", ("writer", "author"))
_add("painting portrait sculpture artwork mural fresco", ("painter", "artist"))
_add("film movie documentary screenplay", ("director", "filmmaker"))
_add("wife husband mother father son daughter brother sister widow parents child children family",
     ("person",))


def possessed_type(noun: str) -> Tuple[str, ...]:
    """The fine type-tuple a possessed noun is diagnostic of (empty tuple if none). Case-insensitive."""
    return POSSESSED_TYPE.get(noun.lower(), ())


def title_role(title: str) -> str:
    """The fine role-identity a title names (empty string if the title is a generic honorific/unknown)."""
    return TITLE_ROLE.get(title.lower(), "")


def is_title(word: str) -> bool:
    """True if `word` is an honorific/title (incl. generic mr/mrs/ms/miss)."""
    return word.lower() in TITLES


__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-10 grown-knowledge incorporation from the name-bridge world-knowledge solver "
                   "(owner-DONE, STRONG); promoted byte-identical, witness test_who_is_who_lexicon.py 8/8, "
                   "name-bridge reverify unaffected 11/11+9/9; strategy first-hand")
__bf_note__ = (
    "BF_SPIRIT (static offline FOUNDATION asset). Heim file-change + Bruce-Young role-identity + relational/"
    "selectional semantics: a possessed noun is type-diagnostic of its possessor; a title is a stored role node. "
    "Curated offline (NO external tool/LLM at inference); consumed as GRADED fine evidence (never a hard flag -- "
    "the coarse-flag variant is a measured located negative). Grown by the name-bridge world-knowledge solver; "
    "the SINGLE source of truth for these lexicons (the experiment imports from here, byte-identical)."
)


if __name__ == "__main__":
    assert len(TITLE_ROLE) == 33, len(TITLE_ROLE)
    assert len(TITLES) == 37, len(TITLES)
    assert len(POSSESSED_TYPE) == 78, len(POSSESSED_TYPE)
    assert possessed_type("capital") == ("country", "nation", "state", "location")
    assert possessed_type("album") == ("musician", "composer", "artist")
    assert title_role("president") == "president"
    assert title_role("lord") == "man"
    assert is_title("mr") and not is_title("banana")
    print("SELFTEST PASS: who_is_who_lexicon  TITLE_ROLE=%d TITLES=%d POSSESSED_TYPE=%d"
          % (len(TITLE_ROLE), len(TITLES), len(POSSESSED_TYPE)), flush=True)
