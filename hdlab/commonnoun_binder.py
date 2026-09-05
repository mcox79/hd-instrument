"""hdlab/commonnoun_binder.py -- the DEPLOYABLE situation-gated common-noun discourse-referent FORMER,
promoted VERBATIM (2026-09-04) from the owner-DONE
`form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref`
(experiments/exp_commonnoun_situation_gated_binder_v1.situation_predict + the DIAG/LK helpers it reuses).

WHAT THIS IS (the LANDABLE WIN of a LOCATED NEGATIVE). A faithful cue-based common-noun former does NOT
beat the reader's surface-head grouping (the +0.43 gold-coref headroom is world-knowledge-bound: head-match
recall 0.341, 91% of over-merges content-identical). But ONE recipe is a small, CI-separated, no-regress
optimization over surface-head, worth landing: the incremental discourse-referent former with
  (i)   per-mention HEAD-MATCH-GATED linking (net-safe recall, like surface_head),
  (ii)  MODIFIER-SPLIT ("the old man" != "the young man"),
  (iii) a wide recency WINDOW (W=16), and
  (iv)  the EVENT-CENTRALITY SITUATION gate for >=2 head-match candidates (reuse the LANDED
        hdlab.event_centrality_coref HD event-memory: the scene-central antecedent wins the tie,
        extended from pronouns to definite descriptions).
Measured on LitBank gold coref (100 docs, CoNLL avg of MUC/B3/CEAFe, character-cluster population):
  situation_predict(headmatch_gate=True, window=16) = 0.6174 -> BEATS surface_head +0.0128
  CI[+0.0061,+0.0197] CI-sep (CEAFe 0.469->0.510), info-free twin LOSES (+0.258 CI-sep),
  NO-REGRESS on named coref (+0.0000). Generalizes (zero fitted params, even/odd halves).

The RELATIONAL situation-model prototype (relational=True) is carried VERBATIM (the possessor-keyed role
binder) but recovers only ~1% of the kinship slice (+0.0006) -- kept for provenance, not deployed.

REUSE (matching organs, not reinvented): hdlab.coref.EntityAliaser (proper-name aliasing),
hdlab.event_centrality_coref.{EventMemory, hd_centrality} (the Cowan-4 HD event-bundle memory),
hdlab.graded_coref_pick.{ROLE_W, DEFAULT_ACTR_D} (the PINNED ACT-R base-level activation constants).
The DIAG/LK helper bodies (head_lemma / is_name / modifiers / definiteness / person_synset / _actr /
_gender_ok / _number_ok / _num_of / Ref / KINSHIP_ROLE) are ported VERBATIM so hdlab carries NO
experiments/ dependency (same discipline as hdlab.goal_register).

Returns a predicted cluster label per NON-PRONOUN mention (drop-in for the reader's common-noun
clustering, replacing the blind transitive same-head merge). Glass-box, deterministic, NO external LLM.
WordNet person-typing is a static offline lexical foundation (nltk, no inference-time LLM). ASCII.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import re
from typing import Dict, List, Optional

import numpy as np

from hdlab.coref import EntityAliaser, name_content_tokens
from hdlab.event_centrality_coref import EventMemory, hd_centrality
from hdlab.graded_coref_pick import ROLE_W, DEFAULT_ACTR_D   # PINNED ACT-R constants (reuse the organ)


# =========================== ported lexical helpers (VERBATIM from DIAG) ==============================
DEF_DET = {"the", "this", "that", "these", "those", "his", "her", "my", "your", "our", "their", "its"}
INDEF_DET = {"a", "an", "some", "any", "another", "no", "each", "every", "one"}
_IRREG = {"men": "man", "women": "woman", "children": "child", "people": "person", "gentlemen": "gentleman",
          "gentlewomen": "gentlewoman", "wives": "wife", "ladies": "lady", "brothers": "brother",
          "sisters": "sister", "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse"}


def head_lemma(head: str) -> str:
    """Light noun lemma: irregular map, then regular plural strip (ies->y, ses/xes/ches->s.., s)."""
    h = re.sub(r"[^a-z]+", "", str(head).lower())
    if not h:
        return ""
    if h in _IRREG:
        return _IRREG[h]
    if len(h) > 4 and h.endswith("ies"):
        return h[:-3] + "y"
    if len(h) > 4 and h.endswith(("ses", "xes", "zes", "ches", "shes")):
        return h[:-2]
    if len(h) > 3 and h.endswith("s") and not h.endswith("ss"):
        return h[:-1]
    return h


def is_name(m, gaz) -> bool:
    """A clean proper name (aliasable) -- reuse the coref organ's own name test on the raw span."""
    return bool(name_content_tokens(m.get("span_toks", [m["head"]])))


def modifiers(m) -> set:
    """Non-determiner, non-head alphabetic modifier tokens of the span (lowercased)."""
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    hl = head_lemma(m["head"])
    return {w for w in span[:-1] if w.isalpha() and w not in DEF_DET and w not in INDEF_DET
            and head_lemma(w) != hl}


def definiteness(m) -> str:
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    if not span:
        return "bare"
    d = span[0]
    if d in INDEF_DET:
        return "indef"
    if d in DEF_DET:
        return "def"
    return "bare"


# a compact STATIC kinship / social-role person lexicon (VERBATIM from DEC.KINSHIP_ROLE; a buildable
# foundation asset, general English + 19c prose -- NOT derived from LitBank characters). These are person
# nouns whose reference is RELATIONAL. Used ONLY by the relational=True prototype (not the deployed recipe).
KINSHIP_ROLE = frozenset("""
father mother son daughter brother sister husband wife parent child uncle aunt cousin nephew niece
grandfather grandmother grandson granddaughter widow widower stepfather stepmother
master mistress servant maid maidservant manservant butler footman valet nurse governess housekeeper
cook groom coachman steward tenant landlord landlady
lord lady sir madam gentleman gentlewoman king queen prince princess duke duchess earl countess baron
squire knight parson vicar rector curate priest doctor captain colonel major general sergeant
friend companion lover mistress neighbour neighbor stranger guest visitor
""".split())
RELATIONAL_ROLE = KINSHIP_ROLE

# possessive-pronoun possessor -> gender of the POSSESSOR (for relational-role binding); VERBATIM.
POSS_GENDER = {"her": "fem", "hers": "fem", "his": "masc"}


# =========================== WordNet person-typing (VERBATIM from LK) =================================
_WN = None
_PERSON_SYN = None
_person_cache: Dict[str, object] = {}


def _wn():
    global _WN, _PERSON_SYN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
        _PERSON_SYN = wn.synset("person.n.01")
    return _WN


def person_synset(lemma):
    """The most-common PERSON-denoting noun synset of `lemma` (person.n.01 in its hypernym paths), or None."""
    if lemma in _person_cache:
        return _person_cache[lemma]
    wn = _wn()
    best = None
    for s in wn.synsets(lemma, "n"):
        paths = s.hypernym_paths()
        if any(_PERSON_SYN in p for p in paths):
            best = s
            break
    _person_cache[lemma] = best
    return best


# =========================== the incremental discourse referent (VERBATIM from LK) ===================
class Ref:
    __slots__ = ("key", "hls", "gender", "number", "mods", "last_sent", "last_midx", "count",
                 "is_name", "person", "hist")

    def __init__(self, key, hl, gender, number, mods, sent, midx, is_name, person, role):
        self.key = key; self.hls = {hl}; self.gender = gender; self.number = number; self.mods = set(mods)
        self.last_sent = sent; self.last_midx = midx; self.count = 1; self.is_name = is_name
        self.person = person; self.hist = [(sent, role)]      # (sentence, role_rank) for ACT-R activation

    def update(self, hl, gender, mods, sent, midx, role):
        self.hls.add(hl); self.mods |= mods; self.last_sent = sent; self.last_midx = midx
        self.count += 1; self.hist.append((sent, role))
        if self.gender is None:
            self.gender = gender


def _actr(ref, cur_sent, d=DEFAULT_ACTR_D):
    """PINNED ACT-R base-level activation A = ln(sum_k w_role(k) * dt_k^-d) over the referent's past
    mentions (recency x frequency x grammatical-role prominence; Anderson-Schooler; Lewis-Vasishth).
    Copied verbatim from hdlab.graded_coref_pick; dt >= 1 (sentence distance)."""
    s = 0.0
    for (sent, role) in ref.hist:
        rw = ROLE_W["SUBJECT"] if role == 0 else ROLE_W["OTHER"]
        dt = float(max(1, cur_sent - sent + 1))
        s += rw * (dt ** (-d))
    return np.log(s) if s > 0 else -1e9


def _gender_ok(g1, g2):
    if g1 in ("masc", "fem") and g2 in ("masc", "fem"):
        return g1 == g2
    return True


def _number_ok(n1, n2):
    if n1 in ("sing", "plur") and n2 in ("sing", "plur"):
        return n1 == n2
    return True


def _num_of(m):
    n = m.get("number")
    if n in ("singular", "sing"):
        return "sing"
    if n in ("plural", "plur"):
        return "plur"
    h = head_lemma(m["head"])
    raw = m["head"].lower()
    if raw != h and raw.endswith("s"):
        return "plur"
    return "sing"


# =========================== the situation-gated former (VERBATIM situation_predict) =================
def situation_predict(mentions, gaz, *, window=8, n_dim=4096, mem_seed=7, headmatch_gate=False,
                      relational=False):
    """Incremental referent former + HD event-memory situation gate on definite common-noun descriptions.
    headmatch_gate=True = the DEPLOYABLE recipe: restrict candidates to head-lemma matches (net-safe recall,
    like surface_head) + modifier-split + the situation-gate tie-break among >=2 head-match candidates.
    relational=True = the RELATIONAL SITUATION MODEL (prototype of the Phase-1 lever): a role-relational
    description with a possessive-pronoun possessor ("her father", "his wife") is bound by the brain's rule
    SAME-RELATION+SAME-RELATUM: resolve the possessor to a discourse referent and key the role-referent by
    (role_lemma, possessor_ref) -- so 'her father' ... 'her father' (same 'her') co-refer, overriding the
    head-match link. Extracts + uses relations from the narrative, no lexicon of who-is-whose.

    Returns {midx -> cluster_label(str)} for every NON-PRONOUN mention (drop-in replacement for the
    reader's common-noun clustering / the surface-head blind transitive merge)."""
    aliaser = EntityAliaser()
    refs = []                       # Ref
    name_key_to_ref = {}
    head_group = {}
    labels = {}
    rel_map = {}                    # (role_lemma, possessor_ref_key) -> Ref  (the relational graph)
    ln = 0

    def resolve_possessor(pg, si):
        """most-recent active person referent gender-compatible with the possessive pronoun's gender."""
        cands = [r for r in refs if r.person and (not window or (si - r.last_sent) <= window)
                 and _gender_ok(pg, r.gender)]
        return max(cands, key=lambda r: r.last_midx).key if cands else None
    mem = EventMemory(n_dim=n_dim, capacity=4, fanout=2, seed=mem_seed)
    cur_sent = None
    sent_buf = []                   # (ref_key, role_rank, is_person) for the current sentence

    def emit_event():
        if not sent_buf:
            return
        agent = next((k for (k, r, p) in sent_buf if p and r == 0), None)
        if agent is None:
            return
        patient = next((k for (k, r, p) in sent_buf if p and k != agent), None)
        mem.push_event(agent, patient, cur_sent)

    for m in sorted([x for x in mentions if not x["is_pronoun"]], key=lambda x: x["midx"]):
        si = m["sent_idx"]; role = m.get("sent_role_rank", 99)
        if cur_sent is None:
            cur_sent = si
        if si != cur_sent:
            emit_event(); sent_buf = []; cur_sent = si
        span = m.get("span_toks", [m["head"]])
        g = m.get("gender") or m.get("name_gender"); num = _num_of(m); mods = modifiers(m)
        if is_name(m, gaz):
            canon = aliaser.assign(span, g)
            if canon is not None and canon in name_key_to_ref:
                r = name_key_to_ref[canon]; r.update(head_lemma(m["head"]), g, mods, si, m["midx"], role)
            else:
                r = Ref("R%d" % ln, head_lemma(m["head"]), g, num, mods, si, m["midx"], True, True, role); ln += 1
                refs.append(r)
                if canon is not None:
                    name_key_to_ref[canon] = r
            labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); continue
        hl = head_lemma(m["head"])
        person = person_synset(hl) is not None
        if not person:
            if hl not in head_group:
                head_group[hl] = "H%d" % ln; ln += 1
            labels[m["midx"]] = head_group[hl]; sent_buf.append((head_group[hl], role, False)); continue
        defn = definiteness(m)
        # RELATIONAL SITUATION MODEL: a possessed role-relational description binds by (role, possessor).
        rel_key = None
        if relational and hl in RELATIONAL_ROLE:
            span0 = (span[0].lower() if span else "")
            pg = POSS_GENDER.get(span0)
            if pg is not None:
                poss_key = resolve_possessor(pg, si)
                if poss_key is not None:
                    rel_key = (hl, poss_key)
                    if rel_key in rel_map:
                        r = rel_map[rel_key]
                        r.update(hl, g, mods, si, m["midx"], role)
                        labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); continue
        cand_refs = []
        if not defn == "indef":
            for r in refs:
                if not r.person or (window and (si - r.last_sent) > window):
                    continue
                if not _gender_ok(g, r.gender) or not _number_ok(num, r.number):
                    continue
                if headmatch_gate and hl not in r.hls:
                    continue                  # DEPLOYABLE: link only on head-lemma match (net-safe recall)
                if headmatch_gate and hl in r.hls and mods and r.mods and mods.isdisjoint(r.mods):
                    continue                  # modifier-split: 'the old man' != 'the young man'
                cand_refs.append(r)
        chosen = None
        if len(cand_refs) == 1:
            chosen = cand_refs[0]
        elif len(cand_refs) >= 2:
            # SITUATION-MODEL GATE: which candidate referent is most central in recent events?
            pool = {r.key for r in cand_refs}
            scores, _detail = hd_centrality(mem, pool, "event_role")
            mx = max(scores.values()) if scores else 0.0
            if mx > 0.0:
                # among top-centrality, prefer head-lemma match then ACT-R activation (tie-break)
                top = [r for r in cand_refs if scores.get(r.key, 0.0) == mx]
                chosen = max(top, key=lambda r: (hl in r.hls, _actr(r, si)))
            else:
                # degenerate (no recent event mentions any candidate) -> ACT-R + head-match bonus
                chosen = max(cand_refs, key=lambda r: _actr(r, si) + (1.5 if hl in r.hls else 0.0))
            # modifier guard on a head-identical merge
            if hl in chosen.hls and mods and chosen.mods and mods.isdisjoint(chosen.mods):
                chosen = None
        if chosen is not None:
            chosen.update(hl, g, mods, si, m["midx"], role); labels[m["midx"]] = chosen.key
            sent_buf.append((chosen.key, role, True)); assigned = chosen
        else:
            r = Ref("R%d" % ln, hl, g, num, mods, si, m["midx"], False, person, role); ln += 1
            refs.append(r); labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); assigned = r
        if rel_key is not None:
            rel_map[rel_key] = assigned          # register the role+possessor -> referent relation
    emit_event()
    return labels


def _selftest() -> None:
    """Byte-identity witness: the LANDED former reproduces the experiments former's labels on a small
    LitBank sample (verbatim promotion), and the deployable recipe runs. Requires experiments/ + nltk +
    the LitBank conll corpus; skipped gracefully if unavailable."""
    try:
        import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
        import experiments.exp_commonnoun_situation_gated_binder_v1 as SB
    except Exception as e:  # pragma: no cover
        print("[commonnoun_binder selftest] SKIP (experiments/corpus unavailable: %s)" % e)
        return
    docs, gaz = DIAG.load_docs(n=6)
    for _doc, ms in docs:
        for kw in (dict(window=8), dict(window=16, headmatch_gate=True),
                   dict(window=16, headmatch_gate=True, relational=True)):
            a = situation_predict(ms, gaz, **kw)
            b = SB.situation_predict(ms, gaz, **kw)
            assert a == b, ("landed former diverged from experiments former (%s)" % kw)
    print("[commonnoun_binder selftest] PASS (landed == experiments on 6 docs)")


if __name__ == "__main__":
    _selftest()
