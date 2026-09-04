"""psych_verb_frames: a BRAIN-FOUNDATIONAL upstream component for EXPERIENCER-role linking.

THE WALL it breaks: WHO feels the emotion. English psych verbs split the experiencer between the
SUBJECT and the OBJECT, and getting it backwards binds the emotion to the WRONG character:
  "Mary FEARED the dog"      -> experiencer = SUBJECT (Mary)   [fear-type / VerbNet admire-31.2]
  "The dog FRIGHTENED Mary"  -> experiencer = OBJECT  (Mary)   [frighten-type / VerbNet amuse-31.1]
A naive subject=experiencer rule mis-binds the entire (high-frequency) frighten-class.

THE BRAIN'S MECHANISM (PINNED -- research_experiencer_psych_verb_brain_mechanism_2026-09-04.md):
experiencer-role assignment is a LEXICALLY STORED, per-verb linking fact, retrieved and applied
incrementally by constraint-based lexicalist parsing (MacDonald, Pearlmutter & Seidenberg 1994;
Belletti & Rizzi 1988 theta-theory; Pesetsky 1995 causal decomposition; Landau 2010 locative syntax
of experiencers). The mapping is encoded PER VERB in the gold argument-structure resources:
  VerbNet admire-31.2 = Experiencer subject, Stimulus object   (subject-experiencer)
  VerbNet amuse-31.1   = Cause/Stimulus subject, Experiencer object   (object-experiencer)
  VerbNet marvel-31.3  = Experiencer subject, Stimulus in a PP        (subject-experiencer, oblique stim)
  VerbNet appeal-31.4  = Stimulus subject, Experiencer object-of-"to" (dative/oblique experiencer)
  PropBank cross-check: fear = Arg0(Exp)/Arg1(Stim); frighten = Arg0(Stim)/Arg1(Exp).
The one documented HARD case is the ALTERNATING class (worry/concern/grieve/anger): the SAME lemma is
subject-experiencer intransitive+PP ("Mary worries about the dog") and object-experiencer transitive
("The dog worries Mary"). These are resolved PER OCCURRENCE by FRAME SHAPE (a transitive NP-V-NP frame
-> object-experiencer; intransitive/+PP -> subject-experiencer) -- the constraint-satisfaction the
lexicalist model predicts. Novel/unknown verbs default to SUBJECT-experiencer (the cross-linguistic
"elsewhere" case; the standing surface preference for Experiencer-in-subject-position).

WHY THIS IS FOUNDATION, NOT TEST-FITTING: the psych-verb class membership is a general lexical-semantic
universal established from Italian (Belletti-Rizzi), English (Levin 1993), and the VerbNet/PropBank
NLP resources -- all INDEPENDENT of the LitBank narrative test set (no leakage), exactly as the goal
problem's GOAL_VERBS came from the Levin desiderative classes. The per-verb TRANSITIVITY PRIOR (the
frame-shape backstop for alternating verbs) is DERIVED offline from the UD-EWT GOLD treebank -- a
static foundation asset (owner 2026-08-16), NOT the test set.

Glass-box, deterministic, NO spaCy / NO LLM at inference (a json/dict lookup). ASCII.
Build the transitivity prior:  .venv/Scripts/python.exe hdlab/psych_verb_frames.py --build

LANDED into hdlab (Q111, the_situation_model_has_no_affect_emotion_dimension). Promoted VERBATIM from
experiments/psych_verb_frames.py; the ONLY change is the runtime asset path -- the transitivity prior
is read from the SHIPPED frontend asset (data/frontend_assets/psych_verb_transitivity_ud_ewt.json),
mirroring the goal register's verb_subcat_frames landing. stdlib only -- NO experiments/ dependency.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, Optional

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu  (offline build input only)
UD_TRAIN = os.path.join(REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
# runtime asset: the SHIPPED frontend asset (strategy ships it to data/frontend_assets/ at the Q111 landing)
ASSET = os.path.join(REPO, "data/frontend_assets/psych_verb_transitivity_ud_ewt.json")

# ---------------------------------------------------------------------------
# THE PINNED EXPERIENCER-LINKING LEXICON (VerbNet classes + PropBank rolesets, cross-verified;
# see the research note SS1). Class membership is a gold lexical universal, independent of LitBank.
# Stored as the base lemma; the register lemmatizes surface forms before lookup.
# ---------------------------------------------------------------------------
# admire-31.2 + marvel-31.3: EXPERIENCER = SUBJECT (stimulus is object or a PP)
SUBJ_EXP_VERBS = {
    "admire", "adore", "appreciate", "cherish", "esteem", "exalt", "favor", "favour", "idolize",
    "prize", "relish", "respect", "revere", "savor", "savour", "treasure", "value", "venerate",
    "worship", "abhor", "detest", "despise", "disdain", "dislike", "distrust", "dread", "envy",
    "execrate", "hate", "loathe", "mistrust", "resent", "deplore", "enjoy", "fear", "lament",
    "like", "love", "miss", "mourn", "pity", "regret", "rue", "tolerate", "trust", "adore",
    # marvel-31.3 (subject-experiencer, stimulus in a PP)
    "marvel", "wonder", "rejoice", "despair", "delight_in", "gloat", "grieve",
}
# amuse-31.1: EXPERIENCER = OBJECT (stimulus/cause is subject)
OBJ_EXP_VERBS = {
    "amuse", "charm", "delight", "entertain", "fascinate", "frighten", "offend", "perplex",
    "sadden", "terrify", "horrify", "torment", "enchant", "thrill", "bother", "annoy", "cheer",
    "comfort", "amaze", "disgust", "interest", "entice", "scare", "confuse", "shock", "upset",
    "surprise", "satisfy", "excite", "inspire", "impress", "trouble", "embarrass", "humiliate",
    "irritate", "exasperate", "distress", "alarm", "appall", "appal", "astonish", "astound",
    "dismay", "disturb", "unsettle", "unnerve", "stun", "overwhelm", "gratify", "relieve",
    "reassure", "soothe", "calm", "please", "disappoint", "depress", "discourage", "encourage",
    "intrigue", "agitate", "madden", "infuriate", "repel", "revolt", "nauseate", "disquiet",
    "haunt", "devastate", "gladden", "tickle", "startle", "spook", "worry",
}
# appeal-31.4: EXPERIENCER = OBJECT-of-"to" (dative/oblique)
OBLIQUE_EXP_VERBS = {"appeal", "matter", "occur", "seem"}
# genuinely alternating (subject-exp intransitive+PP vs object-exp transitive) -> resolve per occurrence
ALTERNATING_VERBS = {"worry", "concern", "grieve", "anger", "please", "delight", "rejoice", "despair"}


def is_psych_lexeme(verb: str) -> bool:
    """Is `verb` a gold psych-verb lexeme (any class)? Arm-INDEPENDENT membership check over the VerbNet/
    PropBank class sets -- needs no transitivity asset, so the naive A/B baseline gates on the SAME set
    as the frame arm (only the experiencer POSITION differs between arms)."""
    for v in PsychVerbFrames._candidates(verb):
        if v in OBJ_EXP_VERBS or v in SUBJ_EXP_VERBS or v in OBLIQUE_EXP_VERBS or v in ALTERNATING_VERBS:
            return True
    return False


class PsychVerbFrames:
    """Runtime lexicalist experiencer-linking frame (dict lookup, no parse). experiencer_position(verb,
    has_object) returns 'subject' | 'object' | 'oblique' | 'subject'(default). For an ALTERNATING verb,
    has_object decides (transitive -> object-experiencer; intransitive/PP -> subject-experiencer); when
    has_object is unknown (None), the offline UD-EWT transitivity PRIOR breaks the tie."""
    _cache = None

    def __init__(self, transitivity: Optional[dict] = None):
        self.trans = (transitivity or {}).get("p_transitive", {}) if transitivity else {}

    @classmethod
    def load(cls, path: str = ASSET) -> "PsychVerbFrames":
        if cls._cache is None:
            data = None
            try:
                with open(path, encoding="ascii") as f:
                    data = json.load(f)
            except Exception:
                data = None
            cls._cache = cls(data)
        return cls._cache

    @staticmethod
    def _candidates(verb: str):
        """Inflection-robust lemma candidates for a surface verb form (loved->love, amazed->amaze,
        scared->scare, frightened->frighten, terrified->terrify, worries->worry). A closed-class lookup
        needs to match past/3sg/gerund forms; a plain suffix strip alone gives amaz/scar/pleas."""
        v = verb.lower()
        c = [v]
        if v.endswith("ied") and len(v) > 4:
            c.append(v[:-3] + "y")
        if v.endswith("ing") and len(v) > 5:
            c.append(v[:-3]); c.append(v[:-3] + "e")
        if v.endswith("ed") and len(v) > 3:
            c.append(v[:-2]); c.append(v[:-1])           # strip 'ed' and strip only 'd' (amazed->amaze)
        if v.endswith("es") and len(v) > 3:
            c.append(v[:-2]); c.append(v[:-1])
        if v.endswith("s") and len(v) > 3:
            c.append(v[:-1])
        seen = []
        for x in c:
            if x not in seen:
                seen.append(x)
        return seen

    def klass(self, verb: str) -> Optional[str]:
        for v in self._candidates(verb):
            if v in OBLIQUE_EXP_VERBS:
                return "oblique"
            if v in ALTERNATING_VERBS:
                return "alternating"
            if v in OBJ_EXP_VERBS:
                return "object"
            if v in SUBJ_EXP_VERBS:
                return "subject"
        return None

    def is_psych_verb(self, verb: str) -> bool:
        return self.klass(verb) is not None

    def experiencer_position(self, verb: str, has_object: Optional[bool] = None,
                             tau: float = 0.5) -> str:
        """Where the experiencer sits for THIS occurrence. Non-alternating -> the stored class.
        Alternating -> frame shape (has_object) if known, else the UD-EWT transitivity prior, else
        the subject-experiencer default (the elsewhere case)."""
        k = self.klass(verb)
        if k == "object":
            return "object"
        if k == "oblique":
            return "oblique"
        if k == "subject":
            return "subject"
        if k == "alternating":
            if has_object is True:
                return "object"          # transitive NP-V-NP -> object-experiencer (amuse-type)
            if has_object is False:
                return "subject"         # intransitive/+PP -> subject-experiencer (admire-type)
            p = self.p_transitive(verb)          # unknown frame shape -> corpus transitivity prior
            if p is not None:
                return "object" if p >= tau else "subject"
            return "subject"
        # unknown verb -> subject-experiencer default (PINNED elsewhere case)
        return "subject"

    def p_transitive(self, verb: str) -> Optional[float]:
        for v in self._candidates(verb):
            if v in self.trans:
                return self.trans[v]
        return None


# ---------------------------------------------------------------------------
# OFFLINE BUILD: per-verb P(transitive) from UD-EWT gold (the frame-shape prior for alternating verbs)
# ---------------------------------------------------------------------------
def _iter_sentences(path: str):
    sent = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            continue
        if not line.strip():
            if sent:
                yield sent
                sent = []
            continue
        c = line.split("\t")
        if len(c) < 8 or "-" in c[0] or "." in c[0]:
            continue
        sent.append({"id": int(c[0]), "form": c[1].lower(), "lemma": c[2].lower(),
                     "upos": c[3], "head": int(c[6]), "deprel": c[7].split(":")[0]})
    if sent:
        yield sent


def build(path: str = UD_TRAIN) -> dict:
    """P(transitive | the verb has a core argument) per verb = obj / (obj + obl/nmod-PP), from UD-EWT
    gold. A verb heading a direct object (obj/dobj) counts transitive; one heading only an oblique/PP
    (obl, or an advmod/nmod 'about'/'over'/'for' dependent) counts intransitive-with-PP."""
    trans = defaultdict(int)
    intrans = defaultdict(int)
    for sent in _iter_sentences(path):
        children = defaultdict(list)
        for t in sent:
            children[t["head"]].append(t)
        for t in sent:
            if t["upos"] != "VERB":
                continue
            deps = [c["deprel"] for c in children.get(t["id"], [])]
            has_obj = any(d in ("obj", "dobj", "iobj") for d in deps)
            has_obl = any(d in ("obl", "nmod") for d in deps)
            if has_obj:
                trans[t["lemma"]] += 1
            elif has_obl:
                intrans[t["lemma"]] += 1
    p_transitive = {}
    for v in set(list(trans) + list(intrans)):
        a, b = trans[v], intrans[v]
        if a + b >= 2:
            p_transitive[v] = round(a / (a + b), 4)
    return {"source": "UD-EWT gold train (offline foundation asset; not the LitBank test set)",
            "n_verbs": len(p_transitive), "p_transitive": p_transitive}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args()
    if args.build or not os.path.exists(ASSET):
        data = build()
        os.makedirs(os.path.dirname(ASSET), exist_ok=True)
        with open(ASSET, "w", encoding="ascii") as f:
            json.dump(data, f, indent=1)
        print("built %s: %d verbs with a transitivity prior" % (os.path.relpath(ASSET, REPO), data["n_verbs"]))
        pvf = PsychVerbFrames(data)
        for v in ("worry", "concern", "grieve", "anger"):
            print("  alternating %-8s p_transitive=%s -> unknown-frame position=%s" % (
                v, pvf.p_transitive(v), pvf.experiencer_position(v)))
        return
    if args.self_test:
        pvf = PsychVerbFrames.load()
        assert pvf.experiencer_position("fear") == "subject"
        assert pvf.experiencer_position("frighten") == "object"
        assert pvf.experiencer_position("appeal") == "oblique"
        assert pvf.experiencer_position("worry", has_object=True) == "object"
        assert pvf.experiencer_position("worry", has_object=False) == "subject"
        assert pvf.experiencer_position("zqxwv") == "subject"   # unknown -> default subject
        print("SELF-TEST PASS")


if __name__ == "__main__":
    main()
