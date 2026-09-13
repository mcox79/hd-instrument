"""hdlab/typed_selectional_preference.py -- TYPE-GENERALIZED selectional preference: Resnik (1996) class-based
selectional association over the WordNet noun-supersense cut, built from the reading-grown selectional store.

Promoted 2026-09-12 by strategy from the owner-DONE solver `type_generalized_selectional_preference_densifies_coverage_but_
the_who_affected_wall_is_ambiguity` (witness 5/5, reverified first-hand; verbatim computation from
experiments/exp_typed_selectional_preference_v1.TypedSelectionalPreference).

WHAT IT COMPUTES. For a verb v and a noun class c (one of the 26 WordNet noun supersenses, a clean mutually-exclusive
partition), the selectional association
    A(v, c) = P(c | v) * log( P(c | v) / P(c) ) / SPS(v),      SPS(v) = sum_c P(c|v) log(P(c|v)/P(c))
(Resnik 1996, Cognition 61) -- the share of the verb's selectional-preference strength (a KL divergence from the class
base rate) carried by class c. P(c|v) comes from the OBJ fillers of v in the reading-grown selectional store
(data/selectional_preferences_v1, grown by reading), each filler mapped to its most-frequent-sense supersense.

BRAIN BASIS, HONESTLY LABELLED (RESEARCH_harm_help_and_selectional_math_2026-09-12; registry BF_SPIRIT):
  * Thematic roles are graded, typed expectations, not lexical-item slots: McRae, Ferretti & Amyote 1997 (role-as-
    feature-bundle, verb-specific typicality); Warren & Paczynski 2010 (an animacy/TYPE tier in the N400) -- the TYPE
    generalization is the brain-faithful move the lexical store lacked (coverage on hard pairs 40% -> 85%).
  * The KL/information-theoretic FORM is a COMPUTATIONAL-LEVEL model (Resnik validated it against human plausibility
    judgements), and it is FIELD-SUPERSEDED: Bicknell et al. 2010 show patient expectations depend on AGENT+VERB jointly
    ("the journalist checked ..." vs "the mechanic checked ..."), which a per-verb class table cannot express. The
    successor is the EVENT-level expectation of the generative world-model (pri-1), which should consume this organ's
    class profiles as a prior, not replace them with another table.
MEASURED (solver; reverified): densifies coverage 40% -> 85% on the hard mis-attachment pairs; a margin-gated rerank
helps ONLY where the signal is discriminating (clean-signal subset +0.07..+0.16) and NEVER beats syntax (0.471) on the
full hard set -- the residual is selectional AMBIGUITY (~70%), not sparsity. The scramble control (each verb's profile
reassigned to a random verb) does not beat the real oracle; prior-lesion falls back to syntax (no phantom lift).
STATUS IN THE SUBSTRATE: a KNOWLEDGE ORGAN, LATENT -- its named consumer is the pri-1 world-model reranker (a graded
discriminative consumer). It is NOT wired into the live reader as a default because its measured live effect through a
margin gate is neutral on the full population (no-more-default-off policy: measure impact, turn on if net-positive --
it is not). It ships with a persisted asset + a rebuild tool so the consumer can read it the day it exists.
Glass-box. WordNet supersense lookup at read-time is an admissible foundation asset (the pri-12 residual class).
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-12 strategy promotion of the owner-DONE typed selectional-preference organ (witness 5/5 reverified); "
                   "Resnik class association = computational-level model of typed thematic-fit expectation "
                   "(RESEARCH_harm_help_and_selectional_math_2026-09-12: field-superseded by joint agent-verb expectation -> pri-1)")
__bf_note__ = ("Resnik 1996 class-based selectional association over WordNet noun supersenses from the reading-grown selectional "
               "store; TYPE generalization (McRae-Ferretti role-as-feature-bundle; Warren-Paczynski N400 type tier) = the BF move; "
               "KL form = computational-level, superseded by Bicknell 2010 joint agent-verb expectations (successor = pri-1 world model). "
               "LATENT knowledge organ: gated rerank measured neutral on the full hard set (ambiguity wall), so no live default consumer.")
__bf_corrections__ = []

import json
import math
import os
import pickle
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from hdlab import morphology as _gbm   # glass-box morphy (byte-identical; no nltk on the lemma path)

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORE = os.path.join(_REPO, "data", "selectional_preferences_v1", "selectional_slots_v1.pkl")
ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_selectional_preference_v1.json")

_STOP = {"it", "them", "him", "her", "us", "me", "you", "one", "thing", "someone", "something", "anyone",
         "way", "part", "lot", "kind", "sort", "type", "number", "amount", "bit", "day", "time", "year"}
_PRON_PERSON = {"him", "her", "them", "me", "us", "himself", "herself", "themselves", "who", "whom", "he", "she", "they"}
_ss_cache: Dict[str, Optional[str]] = {}


def _vlemma(w: str) -> str:
    try:
        from hdlab.patient_tendency import lemmatize_verb
        return lemmatize_verb(w.lower())
    except Exception:
        return w.lower()


def noun_supersense(word: str) -> Optional[str]:
    """Most-frequent-sense WordNet noun supersense (lexname, e.g. 'noun.person'); pronouns -> noun.person; None if unknown."""
    wl = word.lower().strip(".,;:'\"")
    if wl in _ss_cache:
        return _ss_cache[wl]
    if wl in _PRON_PERSON:
        _ss_cache[wl] = "noun.person"
        return "noun.person"
    ss = None
    try:
        from nltk.corpus import wordnet as wn
        lem = _gbm.morphy(wl, "n") or wl
        syns = wn.synsets(lem, pos=wn.NOUN)
        ss = syns[0].lexname() if syns else None
    except Exception:
        ss = None
    _ss_cache[wl] = ss
    return ss


class TypedSelectionalPreference:
    """A(v, c) table + selectional preference strength per verb. `load()` reads the persisted asset; `fit()` rebuilds it
    from the selectional store (offline)."""

    def __init__(self) -> None:
        self._A: Dict[str, Dict[str, float]] = {}
        self.SPS: Dict[str, float] = {}
        self.n_fillers: Dict[str, float] = {}

    # ---- offline build (the consolidation step) ----------------------------------------------------
    def fit(self, store_path: str = STORE, exclude_pairs=None, scramble: bool = False, seed: int = 20260910):
        exclude_pairs = exclude_pairs or set()
        with open(store_path, "rb") as f:
            SF = pickle.load(f)["slot_filler"]
        Vc: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        Nv: Dict[str, float] = defaultdict(float)
        Gc: Dict[str, float] = defaultdict(float)
        G = 0.0
        for (verb, role), fillers in SF.items():
            if role != "OBJ":
                continue
            vl = _vlemma(verb)
            for fw, c in fillers.items():
                fl = fw.lower().strip(".,;:'\"")
                if fl in _STOP or len(fl) < 3 or (vl, fl) in exclude_pairs:
                    continue
                ss = noun_supersense(fl)
                if ss is None:
                    continue
                Vc[vl][ss] += c; Nv[vl] += c; Gc[ss] += c; G += c
        if scramble:
            import random
            rng = random.Random(seed)
            verbs = list(Vc.keys())
            donor = {v: rng.choice(verbs) for v in verbs}
            Vc = {v: Vc[donor[v]] for v in verbs}
            Nv = {v: Nv[donor[v]] for v in verbs}
        self._A, self.SPS, self.n_fillers = {}, {}, {}
        for v in Vc:
            if Nv[v] <= 0:
                continue
            sps = 0.0
            terms: Dict[str, float] = {}
            for c, f in Vc[v].items():
                pcv = f / Nv[v]
                pc = Gc[c] / G
                if pcv > 0 and pc > 0:
                    t = pcv * math.log(pcv / pc)
                    terms[c] = t
                    sps += t
            self.SPS[v] = sps
            self.n_fillers[v] = float(Nv[v])
            self._A[v] = {c: (t / sps if sps > 1e-9 else 0.0) for c, t in terms.items()}
        return self

    def save(self, path: str = ASSET) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"A": self._A, "SPS": self.SPS, "n_fillers": self.n_fillers,
                       "computation": "Resnik 1996 A(v,c)=P(c|v)log(P(c|v)/P(c))/SPS(v) over WordNet noun supersenses; "
                                      "OBJ fillers of the reading-grown selectional store (MFS supersense)"}, f)

    @classmethod
    def load(cls, path: str = ASSET) -> "TypedSelectionalPreference":
        self = cls()
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            self._A, self.SPS, self.n_fillers = d["A"], d["SPS"], d.get("n_fillers", {})
        return self

    # ---- the read --------------------------------------------------------------------------------
    def covers(self, verb: str) -> bool:
        return _vlemma(verb) in self._A

    def score(self, verb: str, noun: str) -> Optional[float]:
        """A(v, class(noun)); None if the verb has no profile or the noun no supersense; 0.0 = covered verb that does not
        prefer this type."""
        v = _vlemma(verb)
        if v not in self._A:
            return None
        ss = noun_supersense(noun)
        if ss is None:
            return None
        return self._A[v].get(ss, 0.0)

    def top_types(self, verb: str, k: int = 3) -> List[Tuple[str, float]]:
        v = _vlemma(verb)
        if v not in self._A:
            return []
        return sorted(self._A[v].items(), key=lambda kv: kv[1], reverse=True)[:k]


_INST: Optional[TypedSelectionalPreference] = None


def get() -> TypedSelectionalPreference:
    global _INST
    if _INST is None:
        _INST = TypedSelectionalPreference.load()
    return _INST


def build_asset() -> dict:
    """Offline rebuild: store -> asset. ~1 min. Run: python -m hdlab.typed_selectional_preference build"""
    m = TypedSelectionalPreference().fit()
    m.save()
    return {"n_verbs": len(m._A), "asset": os.path.relpath(ASSET, _REPO)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # build [--store <slots.pkl>] [--out <asset.json>] -- e.g. the store GROWN by the substrate's own chain
        # (tools/grow_selectional_store_bf.py) fitted into a separate asset for the A/B against the parser-extracted one.
        store = sys.argv[sys.argv.index("--store") + 1] if "--store" in sys.argv else STORE
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else ASSET
        m = TypedSelectionalPreference().fit(store_path=store); m.save(out)
        print({"n_verbs": len(m._A), "store": os.path.relpath(store, _REPO), "asset": os.path.relpath(out, _REPO)})
    else:
        m = get()
        print("verbs profiled:", len(m._A), "| eat/bread:", m.score("eat", "bread"), "eat/idea:", m.score("eat", "idea"),
              "| top(eat):", m.top_types("eat"))
