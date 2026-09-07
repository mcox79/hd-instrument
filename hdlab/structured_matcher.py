"""structured_matcher: the STRUCTURED SEMANTIC-MATCHING organ (standalone, reusable) -- the SIGN/TYPE store that
COMPLEMENTS the polarity-blind ATL distributional hub (hdlab/bridging_inference).

BRAIN FRAME (PINNED): semantic memory is a TWO-store split. The ATL hub supplies GRADED distributional relatedness
(Lambon Ralph hub-and-spoke) -- good at "how related", BLIND to "which relation / which direction" (rel(win,lose) ~=
rel(sell,buy)). The COMBINATORIAL / relational reading -- the specific TYPE and SIGN of a relation (is-a, part-of,
converse, antonym) -- is a SEPARATE computation on the structured relational network (angular gyrus / TPJ
combinatorial semantics; Binder & Desai 2011). Polarity/direction is a STRUCTURAL fact, not a similarity magnitude.
This organ is that structured store. It reads SIGNED edges from FREE static assets and ABSTAINS to the hub's fuzzy
relatedness only below a margin.

Assets (all glass-box, NO external LLM; static offline KBs are foundation-admissible):
  - WordNet (nltk): verb/adj ANTONYMY (the sign flip; Fellbaum 1998), noun HYPERNYMY (is-a/type), MERONYMY (part-of).
  - FrameNet (nltk): Perspective_on frame pairs -> CONVERSE lexical-unit pairs (buy/sell, lend/borrow -- the SAME event
    from opposite participant PERSPECTIVES; Cruse 1986 converseness). Seeded from the RESOURCE, not a hand-list.
  - ConceptNet (on disk: data/datasets/conceptnet5_en_100k.jsonl + data/conceptnet_gold_v1/edges.jsonl): IsA /
    AtLocation / PartOf / Antonym edges (the commonsense type/location tail WordNet lacks).
  - a small closed-class CONVERSE seed (reused from _occ_upstream_goal_status; FrameNet coverage is partial).
  - the BRAIN'S EVALUATIVE-DIMENSION antonymy (use_valence=True): opposite Warriner valence poles among high-related
    pairs via hdlab.affect_lexicon (Osgood evaluative axis / vmPFC valence). Unioned into antonym(); opt-in.

OUR-INVENTION-UNDER-TEST (sweep, don't adopt): the abstain margin, the hub-fusion weight, the type-similarity
threshold, the valence relatedness floor. All are parameters over PINNED operations.

The organ is READ-ONLY over the assets and holds no per-eval state (seed disjoint from eval -> not circular). It takes
hdlab.bridging_inference as an INJECTED fuzzy fallback (it does NOT rebuild the ATL hub), and WRITES NOTHING to hdlab
at runtime. ASCII, deterministic, glass-box. NO external LLM at inference.

LANDED into hdlab (Q111, structured_semantic_matching_for_event_goal_and_type_converse_role_filler_knowledge_not_the
_hub). Promoted VERBATIM from experiments/_structured_matcher.py -- the module has no experiments/ dependency (it imports
only stdlib + nltk + hdlab.bridging_inference [injected] + hdlab.affect_lexicon), so the ONLY change from the reference
organ is this header note. Validated (relatedness-matched modern golds, held out from the hand-seed): event<->goal
congruence STRUCTURED 0.975 vs hub 0.492 (+0.483 CI-separated, shuffled-KB twin at chance); the SAME organ transfers to
spatial type-membership 0.917 vs hub 0.500 (+0.417 CI-separated); the hub is at/below chance on the antonym / sibling
slices. See verification/test_structured_matcher_{event_goal,type_transfer,core_noregress,valence_antonym}.py.
"""
from __future__ import annotations
import gzip
import json
import os
import re
from typing import Dict, Optional, Set, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CN_100K = os.path.join(_REPO, "data", "datasets", "conceptnet5_en_100k.jsonl")
_CN_ATLOC = os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl")

# ---- closed-class CONVERSE seed (FrameNet Perspective_on partial; Cruse converseness). REUSED, not eval-fit. ----
_CONVERSE_SEED = {
    "sell": {"buy", "purchase"}, "buy": {"sell"}, "lend": {"borrow"}, "borrow": {"lend"},
    "teach": {"learn"}, "learn": {"teach"}, "give": {"receive", "accept", "get", "take"},
    "receive": {"give", "send"}, "rent": {"rent", "lease"}, "lease": {"rent"}, "offer": {"accept", "take"},
    "send": {"receive", "get"}, "supply": {"receive", "get"}, "pay": {"charge", "receive"},
}


def _lemma(w: str) -> str:
    return re.sub(r"[^a-z]", "", str(w).lower())


class StructuredMatcher:
    """Signed structured-relation lookup with an ATL-hub fuzzy fallback below a margin."""

    def __init__(self, hub=None, margin: float = 0.35, use_conceptnet: bool = True,
                 use_framenet: bool = True, use_valence: bool = False, valence_rel_floor: float = 0.10):
        self.hub = hub                      # a hdlab.bridging_inference.BridgeInference (the fuzzy fallback)
        self.margin = float(margin)
        self.use_conceptnet = use_conceptnet
        self.use_framenet = use_framenet
        self.use_valence = use_valence      # brain's evaluative-dimension antonymy (signed axis, not a symbolic edge)
        self.valence_rel_floor = float(valence_rel_floor)
        self._affect = None
        self._wn = None
        self._anto_cache: Dict[str, Set[str]] = {}
        self._hyper_cache: Dict[str, Set[str]] = {}
        self._cn: Dict[str, Dict[str, Set[str]]] = {}   # rel -> subj -> {obj}
        self._fn_conv: Optional[Dict[str, Set[str]]] = None
        self._cn_loaded = False

    # ---------- assets ----------
    def _wordnet(self):
        if self._wn is None:
            from nltk.corpus import wordnet as wn
            self._wn = wn
        return self._wn

    def _load_conceptnet(self):
        if self._cn_loaded:
            return
        self._cn_loaded = True
        rels = {"IsA", "AtLocation", "PartOf", "Antonym"}
        cn = {r: {} for r in rels}
        # 100k english subset ({subject, predicate, object})
        if os.path.exists(_CN_100K):
            with open(_CN_100K, "r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    p = d.get("predicate", "")
                    if p in rels:
                        s, o = _lemma(d.get("subject", "")), _lemma(d.get("object", ""))
                        if s and o:
                            cn[p].setdefault(s, set()).add(o)
        # curated AtLocation gold ({subj, rel:/r/AtLocation, obj})
        if os.path.exists(_CN_ATLOC):
            with open(_CN_ATLOC, "r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if "AtLocation" in d.get("rel", ""):
                        s, o = _lemma(d.get("subj", "")), _lemma(d.get("obj", ""))
                        if s and o:
                            cn["AtLocation"].setdefault(s, set()).add(o)
        self._cn = cn

    def _framenet_converse(self) -> Dict[str, Set[str]]:
        """Perspective_on: frames sharing a neutral super-frame are converse PERSPECTIVES; their lexical units are
        mutual converses (Commerce_buy <-> Commerce_sell). Seeded from the resource. Cached."""
        if self._fn_conv is not None:
            return self._fn_conv
        conv: Dict[str, Set[str]] = {}
        try:
            from nltk.corpus import framenet as fn
            groups: Dict[str, list] = {}
            for fr in fn.frame_relations():
                tname = ""
                try:
                    tname = fr.type.name
                except Exception:
                    tname = str(getattr(fr, "type", ""))
                if "Perspective" not in tname:
                    continue
                try:
                    sup = fr.superFrame.name
                    sub = fr.subFrame.name
                except Exception:
                    continue
                groups.setdefault(sup, []).append(sub)
            for sup, subs in groups.items():
                # lexical units of each perspectivized sub-frame
                lus_by_sub = []
                for sub in subs:
                    try:
                        f = fn.frame(sub)
                        lus = {_lemma(lu.split(".")[0]) for lu in f.lexUnit.keys()}
                        lus_by_sub.append({l for l in lus if l})
                    except Exception:
                        lus_by_sub.append(set())
                for i in range(len(lus_by_sub)):
                    for j in range(len(lus_by_sub)):
                        if i == j:
                            continue
                        for a in lus_by_sub[i]:
                            conv.setdefault(a, set()).update(lus_by_sub[j])
        except Exception:
            pass
        self._fn_conv = conv
        return conv

    # ---------- structured edges (signed) ----------
    def _affect_lex(self):
        if self._affect is None:
            try:
                from hdlab.affect_lexicon import AffectLexicon
                self._affect = AffectLexicon.load()
            except Exception:
                self._affect = False
        return self._affect

    def valence_antonym(self, a: str, b: str) -> bool:
        """BRAIN'S EVALUATIVE-DIMENSION antonymy (more brain-faithful than a symbolic edge; Osgood evaluative axis /
        vmPFC valence): two words are functional antonyms if they are HIGH-RELATED (same semantic field, per the ATL
        hub) AND carry OPPOSITE valence sign (opposite poles of the shared dimension). Generalizes beyond WordNet's
        antonym LIST -- any high-related opposite-valence pair (Warriner norms) is a signed opposition."""
        if not self.use_valence:
            return False
        lex = self._affect_lex()
        if not lex or self.hub is None:
            return False
        r = self._hub_rel(a, b)
        if r is None or r < self.valence_rel_floor:
            return False
        va, vb = lex.valence_sign(a), lex.valence_sign(b)
        return va is not None and vb is not None and va != 0 and vb != 0 and va != vb

    def antonym(self, a: str, b: str) -> bool:
        a, b = _lemma(a), _lemma(b)
        if not a or not b:
            return False
        if b in self._wn_antonyms(a) or a in self._wn_antonyms(b):
            return True
        if self.use_conceptnet:
            self._load_conceptnet()
            if b in self._cn["Antonym"].get(a, ()) or a in self._cn["Antonym"].get(b, ()):
                return True
        if self.valence_antonym(a, b):      # evaluative-dimension antonymy (coverage + fidelity), opt-in
            return True
        return False

    def _wn_antonyms(self, head: str) -> Set[str]:
        if head in self._anto_cache:
            return self._anto_cache[head]
        wn = self._wordnet()
        out: Set[str] = set()
        try:
            for pos in ("v", "a", "s", "n"):
                for syn in wn.synsets(head, pos=pos):
                    for lem in syn.lemmas():
                        for anto in lem.antonyms():
                            out.add(_lemma(anto.name()))
        except Exception:
            pass
        self._anto_cache[head] = out
        return out

    def converse(self, a: str, b: str) -> bool:
        a, b = _lemma(a), _lemma(b)
        if not a or not b:
            return False
        if b in _CONVERSE_SEED.get(a, set()) or a in _CONVERSE_SEED.get(b, set()):
            return True
        if self.use_framenet:
            fc = self._framenet_converse()
            if b in fc.get(a, set()) or a in fc.get(b, set()):
                return True
        return False

    def is_a(self, x: str, y: str) -> bool:
        """x IS-A y (type-membership): WordNet hypernym closure OR ConceptNet IsA."""
        x, y = _lemma(x), _lemma(y)
        if not x or not y or x == y:
            return x == y
        if y in self._wn_hypernyms(x):
            return True
        if self.use_conceptnet:
            self._load_conceptnet()
            # transitive-ish: 1 or 2 hops in ConceptNet IsA
            isa = self._cn["IsA"]
            if y in isa.get(x, set()):
                return True
            for mid in isa.get(x, set()):
                if y in isa.get(mid, set()):
                    return True
        return False

    def _wn_hypernyms(self, x: str) -> Set[str]:
        if x in self._hyper_cache:
            return self._hyper_cache[x]
        wn = self._wordnet()
        out: Set[str] = set()
        try:
            for s in wn.synsets(x, pos="n"):
                for path in s.hypernym_paths():
                    for h in path:
                        for lem in h.lemmas():
                            out.add(_lemma(lem.name()))
        except Exception:
            pass
        self._hyper_cache[x] = out
        return out

    def cohyponym(self, x: str, y: str) -> bool:
        """x and y share a hypernym but NEITHER is-a the other -> taxonomic SIBLINGS -> a STRUCTURAL 'not a kind of'
        signal (a kitchen is not a kind of bedroom; the brain knows this from the taxonomy, Collins & Quillian 1969).
        This is the signed NEGATIVE edge the hub cannot supply (kitchen ~ bedroom is HIGH-related)."""
        x, y = _lemma(x), _lemma(y)
        if not x or not y or x == y:
            return False
        hx, hy = self._wn_hypernyms(x), self._wn_hypernyms(y)
        if not hx or not hy:
            return False
        if y in hx or x in hy:      # one subsumes the other -> is-a, not siblings
            return False
        return bool(hx & hy)        # a shared ancestor, neither subsumes -> siblings

    def at_location(self, x: str, y: str) -> bool:
        if not self.use_conceptnet:
            return False
        x, y = _lemma(x), _lemma(y)
        self._load_conceptnet()
        return y in self._cn["AtLocation"].get(x, set())

    def part_of(self, x: str, y: str) -> bool:
        x, y = _lemma(x), _lemma(y)
        wn = self._wordnet()
        try:
            for s in wn.synsets(x, pos="n"):
                for hol in s.part_holonyms() + s.member_holonyms() + s.substance_holonyms():
                    for lem in hol.lemmas():
                        if _lemma(lem.name()) == y:
                            return True
        except Exception:
            pass
        if self.use_conceptnet:
            self._load_conceptnet()
            if y in self._cn["PartOf"].get(x, set()):
                return True
        return False

    # ---------- unified signed decisions ----------
    def congruence(self, goal_head: str, outcome_head: str) -> Tuple[int, str, float]:
        """EVENT<->GOAL: does the outcome SATISFY (+1) or THWART (-1) the goal? abstain (0) -> hub fuzzy.
        Returns (sign, source, confidence). SATISFY = same head OR converse (same transfer, goal-holder keeps role);
        THWART = antonym (the goal-holder's own opposite outcome). Below both -> hub relatedness above margin -> +1
        (weak satisfy) else abstain."""
        g, o = _lemma(goal_head), _lemma(outcome_head)
        if not g or not o:
            return (0, "empty", 0.0)
        if g == o:
            return (1, "identity", 1.0)
        # CONVERSE first: a frame-mate role-swap (sell/buy, lend/borrow) SATISFIES the goal (same event, the
        # goal-holder keeps their valued role). Only a PURE antonym (not a converse frame-mate) -- the goal-holder's
        # OWN opposite outcome (win/lose) -- is a THWART. Order matters: WordNet lists buy as an antonym of sell, but
        # for GOAL congruence sell/buy is converse-satisfy, not antonym-thwart. (Cruse: converseness != antonymy.)
        if self.converse(g, o):
            return (1, "converse", 1.0)
        if self.antonym(g, o):
            return (-1, "antonym", 1.0)
        # fuzzy fallback: the hub can only say "related", not "signed" -> treat high relatedness as weak-satisfy
        rel = self._hub_rel(g, o)
        if rel is not None and rel >= self.margin:
            return (1, "hub_fuzzy", float(rel))
        return (0, "abstain", 0.0 if rel is None else float(rel))

    def type_match(self, x: str, y: str) -> Tuple[int, str, float]:
        """TYPE/SPATIAL: is x a member/instance/part/location-filler of y? +1 structured, else hub-fuzzy, else abstain."""
        if self.is_a(x, y):
            return (1, "is_a", 1.0)
        if self.at_location(x, y):
            return (1, "at_location", 1.0)
        if self.part_of(x, y):
            return (1, "part_of", 1.0)
        if self.cohyponym(x, y):       # structured NEGATIVE: siblings are NOT a kind-of each other
            return (-1, "cohyponym", 1.0)
        rel = self._hub_rel(x, y)
        if rel is not None and rel >= self.margin:
            return (1, "hub_fuzzy", float(rel))
        return (0, "abstain", 0.0 if rel is None else float(rel))

    def _hub_rel(self, a: str, b: str) -> Optional[float]:
        if self.hub is None:
            return None
        try:
            return self.hub.relatedness(a, b)
        except Exception:
            return None


if __name__ == "__main__":
    m = StructuredMatcher(hub=None, use_conceptnet=True, use_framenet=True)
    print("ANTONYM  win/lose:", m.antonym("win", "lose"), "| pass/fail:", m.antonym("pass", "fail"),
          "| win/win:", m.antonym("win", "win"))
    print("CONVERSE sell/buy:", m.converse("sell", "buy"), "| lend/borrow:", m.converse("lend", "borrow"),
          "| win/lose:", m.converse("win", "lose"))
    print("IS-A     kitchen/room:", m.is_a("kitchen", "room"), "| sedan/car:", m.is_a("sedan", "car"),
          "| dog/room:", m.is_a("dog", "room"))
    print("ATLOC    car/garage:", m.at_location("car", "garage"), "| book/shelf:", m.at_location("book", "shelf"))
    print("CONGRUENCE goal=win outcome=lose:", m.congruence("win", "lose"))
    print("CONGRUENCE goal=sell outcome=buy:", m.congruence("sell", "buy"))
    fc = m._framenet_converse()
    print("FrameNet converse pairs loaded:", len(fc), "e.g. sell->", sorted(fc.get("sell", set()))[:6])
