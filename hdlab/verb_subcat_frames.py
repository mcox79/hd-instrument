"""verb_subcat_frames: a BRAIN-FOUNDATIONAL upstream component for infinitive attachment.

THE WALL it breaks: distinguishing a PURPOSE ADJUNCT ("she went [to buy bread]") from a COMPLEMENT /
raising / extraposed infinitive ("began [to rain]", "wonderful [to meet]") -- the parse-gated slice
where a POS-only heuristic over-fires (goal-register bare-purpose precision 0.33 vs a spaCy oracle).

THE BRAIN'S MECHANISM (PINNED -- research_infinitive_attachment_brain_mechanism_2026-09-04.md): the brain
resolves infinitive attachment by LEXICALIST CONSTRAINT-BASED parsing -- the VERB's stored
SUBCATEGORIZATION FRAME probability drives whether a following "to VP" unifies as a COMPLEMENT or is
reanalyzed as an ADJUNCT (MacDonald, Pearlmutter & Seidenberg 1994 Psych Rev; Trueswell 1996 JML;
Garnsey et al. 1997; Vosse & Kempen 2000 competitive unification; Hale 2001 / Levy 2008 expectation).
A verb whose frame has an open infinitival-complement slot (want/begin/try/seem) takes "to VP" as a
COMPLEMENT (low surprisal); a verb with NO such slot (go/come/stand) forces the "to VP" to attach as an
ADJUNCT (purpose). This module builds that lexical knowledge as a corpus-derived per-verb frame from the
UD-EWT GOLD dependency treebank (a static, offline-built FOUNDATION asset -- owner 2026-08-16; NOT the
LitBank test set, so no leakage), plus the extraposition predicate set (expletive-it hosts).

Glass-box, deterministic, NO spaCy / NO LLM at inference (the frame is a json lookup). ASCII.
Build: .venv/Scripts/python.exe experiments/verb_subcat_frames.py --build
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
UD_TRAIN = os.path.join(REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
# solver-owned location (strategy ships it to data/frontend_assets/ at the Q111 landing)
ASSET = os.path.join(REPO, "data/frontend_assets/verb_subcat_frames_ud_ewt.json")


def _iter_sentences(path: str):
    """Yield lists of token dicts {id, form, lemma, upos, head, deprel} per sentence (skip MWT/empty)."""
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
        if sent and line == "":
            pass
    if sent:
        yield sent


def build(path: str = UD_TRAIN) -> dict:
    """Derive per-verb infinitival subcategorization frames from UD-EWT gold parses."""
    xcomp_inf = defaultdict(int)     # verb heads an infinitival xcomp (complement-taker)
    advcl_inf = defaultdict(int)     # verb heads an infinitival advcl (purpose/adjunct host)
    verb_total = defaultdict(int)    # total VERB occurrences of the lemma
    extrap_pred = defaultdict(int)   # ADJ/NOUN lemma hosts an infinitival csubj/subject (extraposition)
    extrap_total = defaultdict(int)
    n_sents = 0
    for sent in _iter_sentences(path):
        n_sents += 1
        by_id = {t["id"]: t for t in sent}
        # index children with a 'to' mark/aux (infinitival) per head
        for t in sent:
            if t["upos"] == "VERB":
                verb_total[t["lemma"]] += 1
            if t["upos"] in ("ADJ", "NOUN"):
                extrap_total[t["lemma"]] += 1
        for t in sent:
            # is t an infinitival clause? a VERB with a child 'to' (mark or aux)
            has_to = any(ch["form"] == "to" and ch["deprel"] in ("mark", "aux") and ch["head"] == t["id"]
                         for ch in sent)
            if t["upos"] != "VERB" or not has_to:
                continue
            head = by_id.get(t["head"])
            if head is None:
                continue
            dep = t["deprel"]
            # EXCLUDE the grammaticalized "BE going to VINF" FUTURE from go's complement frame: it is a
            # future auxiliary (a distinct lexical item), NOT motion-"go" subcategorizing for an infinitive.
            # Counting it inflates go's P(complement) and wrongly filters real "went to buy" purpose adjuncts.
            if head["lemma"] == "go" and head["form"] == "going":
                continue
            if dep == "xcomp" and head["upos"] in ("VERB", "AUX"):
                xcomp_inf[head["lemma"]] += 1
            elif dep == "advcl" and head["upos"] in ("VERB", "AUX"):
                advcl_inf[head["lemma"]] += 1
            elif dep in ("csubj", "ccomp") and head["upos"] in ("ADJ", "NOUN"):
                extrap_pred[head["lemma"]] += 1   # 'it is hard to say' / 'a way to go' style host
            elif dep in ("xcomp", "advcl", "acl") and head["upos"] in ("ADJ", "NOUN"):
                extrap_pred[head["lemma"]] += 1
    # per-verb frame: P(complement | takes an infinitive) = xcomp / (xcomp + advcl)
    frames = {}
    for v in set(list(xcomp_inf) + list(advcl_inf)):
        x, a = xcomp_inf[v], advcl_inf[v]
        frames[v] = {"xcomp_inf": x, "advcl_inf": a, "total": verb_total.get(v, x + a),
                     "p_complement": round(x / (x + a), 4) if (x + a) else 0.0}
    # extraposition predicates: ADJ/NOUN lemmas that host an infinitival subject/complement often enough
    extrap = {p: {"n": extrap_pred[p], "total": extrap_total.get(p, extrap_pred[p]),
                  "rate": round(extrap_pred[p] / max(1, extrap_total.get(p, extrap_pred[p])), 4)}
              for p in extrap_pred if extrap_pred[p] >= 2}
    return {"n_sents": n_sents, "n_verbs": len(frames), "frames": frames, "extrap_predicates": extrap,
            "source": "UD-EWT gold train (foundation asset, offline-built; not the LitBank test set)"}


# ---------------------------------------------------------------------------
# the runtime lexicalist API (json lookup, no parse) -- used by the goal extractor
# ---------------------------------------------------------------------------
class SubcatFrames:
    _cache = None

    def __init__(self, data: dict):
        self.frames = data["frames"]
        self.extrap = set(data["extrap_predicates"].keys())
        # a strong extraposition predicate set (ADJ/NOUN that frequently host an infinitival subject)
        self.strong_extrap = {p for p, v in data["extrap_predicates"].items()
                              if v["n"] >= 3 or v.get("rate", 0) >= 0.15}

    @classmethod
    def load(cls, path: str = ASSET) -> "SubcatFrames":
        if cls._cache is None:
            with open(path, encoding="ascii") as f:
                cls._cache = cls(json.load(f))
        return cls._cache

    def p_complement(self, verb: str) -> Optional[float]:
        fr = self.frames.get(verb.lower())
        return fr["p_complement"] if fr else None

    def is_complement_taker(self, verb: str, tau: float = 0.5, min_count: int = 2) -> bool:
        """Does `verb` subcategorize FOR an infinitival complement (so a following 'to VP' is a
        COMPLEMENT, not a purpose adjunct)? Lexicalist frame: P(complement) >= tau with enough evidence.
        A verb we have never seen with an infinitive is NOT a complement-taker (default: adjunct-host)."""
        fr = self.frames.get(verb.lower())
        if fr is None:
            return False
        if (fr["xcomp_inf"] + fr["advcl_inf"]) < min_count:
            return fr["xcomp_inf"] > fr["advcl_inf"]   # sparse: go with the majority
        return fr["p_complement"] >= tau

    def is_extraposition_predicate(self, word: str) -> bool:
        return word.lower() in self.strong_extrap


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
        print("built %s: %d verbs, %d sents, %d extrap predicates" % (
            os.path.relpath(ASSET, REPO), data["n_verbs"], data["n_sents"], len(data["extrap_predicates"])))
        # sanity: complement-takers vs adjunct-hosts
        sf = SubcatFrames(data)
        print("\ncomplement-takers (P_complement high, expect want/try/begin/seem):")
        for v in ("want", "try", "begin", "seem", "intend", "hope", "decide", "need", "expect", "manage"):
            print("  %-10s p_complement=%s complement_taker=%s" % (v, sf.p_complement(v), sf.is_complement_taker(v)))
        print("\nadjunct-hosts (P_complement low, expect go/come/stop/stand/return):")
        for v in ("go", "come", "stop", "stand", "return", "run", "sit", "turn", "look", "wait"):
            print("  %-10s p_complement=%s complement_taker=%s" % (v, sf.p_complement(v), sf.is_complement_taker(v)))
        print("\nsample extraposition predicates:", sorted(list(sf.strong_extrap))[:25])
        return
    if args.self_test:
        sf = SubcatFrames.load()
        assert sf.is_complement_taker("want") and sf.is_complement_taker("try")
        assert not sf.is_complement_taker("go") and not sf.is_complement_taker("come")
        print("SELF-TEST PASS")


if __name__ == "__main__":
    main()
