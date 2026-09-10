"""hdlab/typed_coref.py -- TYPED common-noun coreference organ.

Promoted from experiments/exp_commonnoun_typed_identity_gum_v1.py (class TypedResolver -- the reference win) so the
load-bearing algorithm is version-controlled, reproducible from a fresh checkout, and wireable into the live reader.
Self-contained: ZERO experiments/ imports, ZERO frozen-asset dependency (the typed-spokes lever reads only nltk-WordNet
via hdlab.typed_spokes.coref_type_license). Reuses hdlab.salience_binder (ACT-R), hdlab.coref (EntityAliaser),
hdlab.typed_spokes (coref_type_license).

THE WIN (board common_noun_coref instrument, GUM modern TEST, n=2855 anaphoric common-noun mentions):
  TypedCorefResolver(bridge=True, bridge_write=False, type_comparator="typed_spokes")  common=0.5671
  vs same-head string-identity 0.5412 (+0.0259 CI-sep), +0.0792 over the URG incumbent; info-free twin LOSES;
  pronoun/kb byte-identical; name +0.024.

The four brain-faithful levers (each unearthed by diagnosing WHY the naive fix failed):
  1. TYPED CARD IDENTITY -- score common/name coref on the card's NOMINAL dominant (name+common only); pronouns still
     write to the FULL card (all_eids) and are scored there, so pronoun scoring is byte-identical. A referent's
     descriptive identity is anchored on its naming/nominal descriptions; pronouns are transient deictic pointers
     (Ariel: pronouns mark high accessibility, they do not RE-DESCRIBE the entity). ~47%-accurate pronoun binding was
     polluting the shared DRT card; the nominal view de-pollutes it.
  2. NON-WRITING (Nref) different-head TYPE bridge (bridge_write=False) -- a definite with no same-head antecedent
     resolves to the most-salient TYPE-compatible antecedent for THIS reference but does NOT commit the merge. The
     WRITE (not the resolution) is the cost: committing corrupts the same-head chain (0.769->0.694). Nieuwland
     hold-under-uncertainty.
  3. TYPED-SPOKES SEED (type_comparator="typed_spokes") -- seed the bridge from the landed
     hdlab.typed_spokes.coref_type_license organ (sense-resolved synonym + is-a both dirs + part-whole; Lambon-Ralph
     typed spokes) instead of crude WordNet-MFS. The SAME organ is net-NEGATIVE as a WRITING filter but net-POSITIVE
     here as a NON-writing candidate SEED -- the write was the cost, confirmed both directions.
  4. CONSUMER-SPECIFIC MERGE VIEW (kb_eids) -- a third read-only card view exposes the common->named-entity resolution
     ("the company"->Google) to the entity-KB consumer without corrupting the common-noun same-head chain.

INPUT SCHEMA: resolve_doc(doc) consumes the gum_coref.Doc shape -- doc.toks (.gidx/.deprel/.head/.idx/.sent/.lemma/
.upos) and doc.mentions (.eid/.order/.mtype/.text/.lemma_head/.gender/.number/.head_g). The eval harness (gum_coref
parser + the verification/ witnesses) remains experiment-side; re-porting resolve_doc onto the live
hdlab.coref.parse_litbank_conll dict stream (for live-reader deployment) is a separate, fidelity-risky follow-on.

Glass-box, CPU, numpy + nltk-WordNet only, NO external LLM.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (reader CATALOG owner-DONE + BRAIN_FOUNDATIONAL_AUDIT §2b; strategy first-hand cross-ref)'
__bf_note__ = 'Ariel accessibility + DRT type-cards + Nref non-writing type bridge; BFA 09-07 promotion (fidelity preserved)'
__bf_corrections__ = []

import random
from collections import Counter

import numpy as np

from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.coref import EntityAliaser
from hdlab.typed_spokes import coref_type_license

# --- constants (verbatim from experiments/gum_coref.py) ---
THIRD_PERSON = {"he", "him", "his", "himself", "she", "her", "hers", "herself",
                "it", "its", "itself", "they", "them", "their", "theirs", "themselves"}
GENDERED_PRON = {"he": "m", "him": "m", "his": "m", "himself": "m",
                 "she": "f", "her": "f", "hers": "f", "herself": "f"}
TITLES = {"mr", "mrs", "ms", "miss", "dr", "sir", "lady", "lord", "prof", "professor",
          "the", "a", "an", "st", "saint", "uncle", "aunt", "president", "king", "queen", "captain"}

# memoized sense-resolved typed-spokes coref_type_license (symmetric key; pure) -- ~7x on the different-head bridge.
# The type-compatibility closure over the head vocabulary warms once; a deployment can precompute it OFFLINE as a
# static asset (foundation-building, invariant-safe) so the bridge is O(set-lookup), zero WordNet work.
_TYPE_CACHE = {}
_SYN = {}   # wn_related (crude comparator control) memo


# --- lexical helpers (inlined verbatim from exp_unified_referent_gum_v1) ---
def _role(deprel):
    d = (deprel or "").lower()
    if d.startswith("nsubj") or d.startswith("csubj"):
        return "SUBJECT"
    if "poss" in d:
        return "POSSESSIVE"
    if d.startswith("obj") or d.startswith("iobj") or d.startswith("obl"):
        return "OBJECT"
    return "OTHER"


def _pron_gn(low):
    """gender,number for a pronoun surface form."""
    g = GENDERED_PRON.get(low, "")
    if low in ("it", "its", "itself"):
        g = "n"
    num = "plur" if low in ("they", "them", "their", "theirs", "themselves", "these", "those", "we", "us") else ""
    if low in ("he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself"):
        num = "sing"
    return g, num


def _gn_compatible(ref, mg, mn, recall_safe=True):
    """recall-safe agreement: unknown never excludes; known mismatch excludes (gender & number)."""
    if mg and ref.gender:
        if mg != ref.gender:
            return False
    if mn and ref.number:
        if mn != ref.number:
            return False
    return True


def _surface_key(m):
    return m.lemma_head


def _name_tokens(m):
    """content tokens of a NAME mention (drop titles/determiners) for variant aliasing."""
    return {w.lower() for w in m.text.split() if w.lower() not in TITLES and any(c.isalpha() for c in w)}


def _wn_related(h1, h2):
    """crude WordNet 2-hop-hypernym MFS relatedness -- the 'wordnet' comparator control ONLY (the winning path uses
    type_comparator='typed_spokes'). Inlined from exp_commonnoun_recallsafe_bridge_resolver_gum_v1.wn_related."""
    if h1 == h2:
        return True
    k = (h1, h2) if h1 < h2 else (h2, h1)
    v = _SYN.get(k)
    if v is not None:
        return v
    from nltk.corpus import wordnet as wn
    s1 = wn.synsets(h1, pos="n"); s2 = wn.synsets(h2, pos="n")
    r = False
    if s1 and s2:
        if set(s1) & set(s2):
            r = True
        else:
            a, b = s1[0], s2[0]
            ua = {a} | set(a.hypernyms()) | {h for x in a.hypernyms() for h in x.hypernyms()}
            ub = {b} | set(b.hypernyms()) | {h for x in b.hypernyms() for h in x.hypernyms()}
            r = (b in ua) or (a in ub)
    _SYN[k] = r
    return r


def appos_copula_isa(doc):
    """glass-box text-stated is-a edges: (a) apposition (deprel appos) between a common head and a name/common;
    (b) copula 'X is/are a Y' (nsubj ... cop ... Y). Returns a map lemma-> set of co-typed lemmas within the doc.
    This is IN-TEXT, not world knowledge. Moved verbatim from exp_commonnoun_diffhead_anatomy_gum_v1._appos_copula_isa
    (an output-inert dead first pass over doc.toks was dropped -- it only computed an unused local)."""
    toks = doc.toks
    links = set()
    sent_tokens = {}
    for t in toks:
        sent_tokens.setdefault(t.sent, []).append(t)
    for s, ts in sent_tokens.items():
        idx2g = {t.idx: t.gidx for t in ts}
        lemma_by_idx = {t.idx: t.lemma.lower() for t in ts}
        upos_by_idx = {t.idx: t.upos for t in ts}
        for t in ts:
            if t.deprel and t.deprel.startswith("appos") and t.head in lemma_by_idx:
                a, b = t.lemma.lower(), lemma_by_idx[t.head]
                if upos_by_idx.get(t.idx) in ("NOUN", "PROPN") and upos_by_idx.get(t.head) in ("NOUN", "PROPN"):
                    links.add(frozenset((a, b)))
            # copula: t is 'be' with cop deprel; its head is the predicate nominal, whose nsubj is the subject
            if t.lemma.lower() == "be" and t.deprel == "cop" and t.head in lemma_by_idx:
                pred = t.head
                subj = None
                for u in ts:
                    if u.head == pred and u.deprel.startswith("nsubj"):
                        subj = u.idx
                if subj is not None and upos_by_idx.get(pred) in ("NOUN", "PROPN") and upos_by_idx.get(subj) in ("NOUN", "PROPN"):
                    links.add(frozenset((lemma_by_idx[pred], lemma_by_idx[subj])))
    typed = {}
    for l in links:
        a, b = tuple(l) if len(l) == 2 else (next(iter(l)), next(iter(l)))
        typed.setdefault(a, set()).add(b)
        typed.setdefault(b, set()).add(a)
    return typed


class TypedRef:
    """A discourse referent with a TYPED identity view: nominal_eids (name+common) vs all_eids (+pronoun) vs kb_eids
    (nominal+pronoun own mentions + INBOUND non-writing bridges, for the entity-KB consumer)."""
    __slots__ = ("rid", "nominal_eids", "all_eids", "kb_eids", "history", "heads", "name_tokens", "gender",
                 "number", "has_name", "last_time", "last_role")

    def __init__(self, rid):
        self.rid = rid
        self.nominal_eids = []
        self.all_eids = []
        self.kb_eids = []          # THIRD (entity-merge) view: nominal+pronoun own mentions + INBOUND non-writing bridges
        self.history = []
        self.heads = set()
        self.name_tokens = set()
        self.gender = ""
        self.number = ""
        self.has_name = False
        self.last_time = -1
        self.last_role = "OTHER"

    def nominal_dominant(self):
        return Counter(self.nominal_eids).most_common(1)[0][0] if self.nominal_eids else None

    def all_dominant(self):
        return Counter(self.all_eids).most_common(1)[0][0] if self.all_eids else None

    def kb_dominant(self):
        return Counter(self.kb_eids).most_common(1)[0][0] if self.kb_eids else None

    def write(self, m, role, nominal):
        self.history.append((m.order, role)); self.last_time = m.order; self.last_role = role
        self.all_eids.append(m.eid); self.kb_eids.append(m.eid)
        if nominal:
            self.nominal_eids.append(m.eid)
        if m.gender in ("m", "f", "n") and not self.gender:
            self.gender = m.gender
        if m.number and not self.number:
            self.number = m.number
        if m.mtype == "name":
            self.has_name = True
            self.name_tokens |= _name_tokens(m)
        elif m.mtype == "common":
            self.heads.add(m.lemma_head)


class TypedCorefResolver:
    def __init__(self, *, decay=DEFAULT_DECAY, bridge=False, bridge_write=True, intext_isa=True,
                 twin=False, rng=None, twin_mode="random_bridge", binding="incumbent", type_comparator="wordnet",
                 commit_gate=False, bridge_select="actr"):
        self.decay = decay
        # bridge candidate SELECTOR among type-compatible antecedents: 'actr' (salience, the pronoun currency),
        #   'recent' (most-recent), 'old' (least-recent), 'first' (first-introduced). Ariel: a DEFINITE marks a
        #   LOWER-accessibility antecedent than a pronoun -> the faithful selector may NOT be max-salience.
        self.bridge_select = bridge_select
        # GRADED Nref (Nieuwland: hold-under-uncertainty is graded, not all-or-nothing): commit_gate=True MERGES the
        #   UNAMBIGUOUS/high-precision bridges (text-stated apposition/copula is-a, OR a single type-compatible
        #   candidate) into the card -- recovering clustering value -- while HOLDING the ambiguous (>=2 candidate)
        #   WordNet bridges. commit_gate=False = always hold (the resolution-accuracy-only win).
        self.commit_gate = commit_gate
        # bridge type comparator: 'wordnet' = the crude WordNet 2-hop-hypernym MFS (_wn_related); 'typed_spokes' =
        #   the substrate's sense-resolved, directed C5 is-a + part-whole organ (hdlab.typed_spokes.coref_type_license;
        #   Lambon-Ralph typed spokes) -- strictly more brain-foundational + REUSES the landed organ.
        self.type_comparator = type_comparator
        # common-noun same-head binding: 'incumbent' mirrors URG EXACTLY (hard-gn filter + most-recent) so the referent
        #   structure -- and thus the pronoun picks that read it -- are byte-identical (pronoun no-regress by construction);
        #   'recall_safe' uses soft agreement + ACT-R salience (an ablation).
        self.binding = binding
        self.bridge = bridge
        self.bridge_write = bridge_write     # False = Nref non-writing (resolve but do not merge)
        self.intext_isa = intext_isa
        self.twin = twin
        # info-free twin: 'random_bridge' = when a TYPE bridge would fire, instead resolve to a RANDOM gn-compatible
        #   prior referent (destroys the TYPE signal, keeps the reach structure) -> isolates the type information.
        #   'type_shuffle' = random WITHIN the type-compatible set (tests only the selection, weaker control).
        self.twin_mode = twin_mode
        self.rng = rng or random.Random(0)

    def _act(self, ref, now):
        a = actr_activation(ref.history, float(now), decay=self.decay, role_prominence=ROLE_PROMINENCE)
        return a if a != float("-inf") else -1e9

    def _type_rel(self, ha, hb):
        if self.type_comparator != "typed_spokes":
            return _wn_related(ha, hb)              # crude WordNet 2-hop-hypernym MFS (already cached)
        # EFFICIENCY: memoize the sense-resolved typed-spokes comparator (symmetric key) -- it is pure, and the bridge
        # re-queries the same (anaphor-head, referent-head) pairs across mentions/docs. Cuts the bridge cost ~5x.
        key = (ha, hb) if ha <= hb else (hb, ha)
        c = _TYPE_CACHE.get(key)
        if c is None:
            c = coref_type_license(ha, hb)        # sense-resolved synonym + is-a (both dirs) + part-whole
            _TYPE_CACHE[key] = c
        return c

    def resolve_doc(self, doc):
        deprel_by_g = {t.gidx: t.deprel for t in doc.toks}
        typed = appos_copula_isa(doc) if (self.bridge and self.intext_isa) else {}
        refs = []
        aliaser = EntityAliaser(); canon2ref = {}; name_surf = {}
        results = []; gold_first = {}; named = set()
        for m in doc.mentions:
            gold_first.setdefault(m.eid, m.order)
            if m.mtype == "name":
                named.add(m.eid)
        for m in doc.mentions:
            low = m.text.lower().split()[0] if m.text else ""
            role = _role(deprel_by_g.get(m.head_g, "OTHER"))
            is_ana = gold_first[m.eid] < m.order
            mg, mn = (m.gender, m.number)
            if m.mtype == "pronoun":
                mg, mn = _pron_gn(low)
                cands = [r for r in refs if r.last_time < m.order and _gn_compatible(r, mg, mn, True)]
                picked = None
                if cands:
                    acts = [self._act(r, m.order) for r in cands]
                    picked = cands[int(np.argmax(acts))]
                if is_ana and low in THIRD_PERSON:
                    results.append(("pronoun", True, bool(picked is not None and picked.all_dominant() == m.eid)))
                    if m.eid in named:
                        results.append(("kb_hardlink", True,
                                        bool(picked is not None and picked.has_name and picked.all_dominant() == m.eid)))
                if picked is not None:
                    picked.write(m, role, nominal=False)   # pronoun writes to FULL card only -> no nominal pollution
                continue
            if m.mtype == "name":
                canon = aliaser.assign(m.text.split(), mg or None); hk = _surface_key(m)
                if canon is not None and canon in canon2ref:
                    picked = canon2ref[canon]; opened = False
                elif hk in name_surf:
                    picked = name_surf[hk]; opened = False
                else:
                    picked = TypedRef(len(refs)); refs.append(picked); opened = True
                    if canon is not None:
                        canon2ref[canon] = picked
                    name_surf[hk] = picked
                if is_ana:
                    results.append(("name", False, bool((not opened) and picked.nominal_eids and picked.nominal_dominant() == m.eid)))
                picked.write(m, role, nominal=True)
                continue
            # COMMON: same-head pick, scored on the NOMINAL dominant (the de-pollution lever)
            if self.binding == "incumbent":
                # mirror URG EXACTLY: hard gn-filter + most-recent same-head -> ref structure byte-identical for pronouns
                same = [r for r in refs if r.last_time < m.order and m.lemma_head in r.heads
                        and _gn_compatible(r, mg, mn, True)]
            else:
                same = [r for r in refs if r.last_time < m.order and m.lemma_head in r.heads]
            picked = None; opened = True; nowrite_target = None
            if same:
                if self.twin:
                    picked = self.rng.choice(same)
                elif self.binding == "incumbent":
                    picked = max(same, key=lambda r: r.last_time)
                else:
                    def sc(r):
                        a = self._act(r, m.order)
                        if mg and r.gender and mg != r.gender:
                            a -= 3.0
                        if mn and r.number and mn != r.number:
                            a -= 3.0
                        return a
                    picked = max(same, key=sc)
                opened = False
            elif self.bridge:
                tset = typed.get(m.lemma_head, set())
                prior_gn = [r for r in refs if r.last_time < m.order and _gn_compatible(r, mg, mn, True)]
                br = [r for r in prior_gn if (r.heads & tset)
                      or (r.has_name and any(t in r.name_tokens for t in tset))
                      or any(self._type_rel(m.lemma_head, h) for h in r.heads)]
                if br:
                    if self.twin and self.twin_mode == "random_bridge":
                        # info-free: a bridge FIRES (same reach structure) but to a RANDOM gn-compatible prior
                        # referent -> destroys the TYPE signal. If this loses, the type information is load-bearing.
                        tgt = self.rng.choice(prior_gn) if prior_gn else None
                    elif self.twin:
                        tgt = self.rng.choice(br)
                    elif self.bridge_select == "recent":
                        tgt = max(br, key=lambda r: r.last_time)
                    elif self.bridge_select == "old":
                        tgt = min(br, key=lambda r: r.last_time)
                    elif self.bridge_select == "first":
                        tgt = min(br, key=lambda r: r.history[0][0] if r.history else r.last_time)
                    else:
                        tgt = max(br, key=lambda r: self._act(r, m.order))
                    if tgt is not None:
                        # GRADED Nref: commit (merge) only the UNAMBIGUOUS / high-precision bridges; else hold.
                        unambiguous = bool(tset and (tgt.heads & tset or (tgt.has_name and any(t in tgt.name_tokens for t in tset)))) \
                            or (len(br) == 1)
                        do_write = self.bridge_write or (self.commit_gate and unambiguous and not self.twin)
                        if do_write:
                            picked = tgt; opened = False
                        else:
                            nowrite_target = tgt   # Nref: resolve for scoring, do NOT merge
            # score
            was_samehead = bool(same)
            was_bridge = bool(not same and (nowrite_target is not None or (self.bridge and not opened)))
            if is_ana:
                if nowrite_target is not None:
                    correct = bool(nowrite_target.nominal_eids and nowrite_target.nominal_dominant() == m.eid)
                    results.append(("common", False, correct))
                else:
                    correct = bool((not opened) and picked is not None and picked.nominal_eids
                                   and picked.nominal_dominant() == m.eid)
                    results.append(("common", False, correct))
                if getattr(self, "_debug", False):
                    self._tags.append(("samehead" if was_samehead else ("bridge" if was_bridge else "new"), correct))
                # CONSUMER-SPECIFIC MERGE VIEW: expose the common->NAMED-ENTITY resolution to the entity-KB consumer
                # ("the company"->Google) via the bridge, WITHOUT corrupting the common-noun same-head chain (hold).
                if getattr(self, "_kb_debug", False) and m.eid in named:
                    tgt = nowrite_target if nowrite_target is not None else (picked if not opened else None)
                    ok_clean = bool(tgt is not None and tgt.has_name and tgt.nominal_dominant() == m.eid)
                    ok_merge = bool(tgt is not None and tgt.has_name and tgt.kb_dominant() == m.eid)
                    self._kb_tags.append((ok_clean, ok_merge))
                # inbound bridge -> the entity-merge (kb) view of the target (the third view); heads/nominal untouched
                if nowrite_target is not None:
                    nowrite_target.kb_eids.append(m.eid)
            # write: bridged-nowrite mentions open their OWN referent (no pollution, no stealing)
            if picked is None:
                picked = TypedRef(len(refs)); refs.append(picked)
            picked.write(m, role, nominal=True)
        return results


# Back-compat alias: the reference cell / witnesses may import the reference class name.
TypedResolver = TypedCorefResolver


def _self_test():
    """Corpus-free structural self-test (nltk-WordNet only): proves the three-view card de-pollution (lever 1) and the
    non-writing typed bridge (levers 2+3) FUNCTION on a fresh checkout, without the GUM corpus. The full accuracy win
    (common 0.5671 vs string-identity 0.5412) is proven by verification/test_commonnoun_typed_identity.py on GUM."""
    from types import SimpleNamespace as NS

    # 1) LEVER 1 -- TYPED CARD IDENTITY: a pronoun write (nominal=False) must NOT pollute the nominal view.
    ref = TypedRef(0)
    ref.write(NS(order=0, role=None, eid=1, gender="", number="sing", mtype="common", text="car", lemma_head="car"), "SUBJECT", nominal=True)
    for o in (1, 2):  # two WRONG pronoun merges carrying a different eid
        ref.write(NS(order=o, role=None, eid=2, gender="", number="", mtype="pronoun", text="it", lemma_head="it"), "OBJECT", nominal=False)
    assert ref.nominal_dominant() == 1, "nominal view polluted by pronoun (de-pollution lever broken)"
    assert ref.all_dominant() == 2, "all view should reflect the pronoun writes"
    assert ref.kb_dominant() == 2, "kb view should reflect all own mentions"

    # 2) LEVERS 2+3 -- NON-WRITING TYPED BRIDGE: a definite with no same-head antecedent resolves to the type-compatible
    #    prior referent (car <-> vehicle licensed by coref_type_license), and the bridge is load-bearing.
    def tok(gidx, deprel="root", sent=0, idx=1, lemma="x", upos="NOUN", head=0):
        return NS(gidx=gidx, deprel=deprel, sent=sent, idx=idx, lemma=lemma, upos=upos, head=head)

    def men(eid, order, mtype, text, lemma_head, head_g):
        return NS(eid=eid, order=order, mtype=mtype, text=text, lemma_head=lemma_head,
                  gender="", number=("sing" if mtype != "pronoun" else ""), head_g=head_g)

    toks = [tok(1, "nsubj", 0, 1, "car"), tok(2, "nsubj", 1, 1, "it"),
            tok(3, "nsubj", 2, 1, "car"), tok(4, "nsubj", 3, 1, "vehicle")]
    mentions = [men(1, 0, "common", "a car", "car", 1),
                men(1, 1, "pronoun", "it", "it", 2),
                men(1, 2, "common", "the car", "car", 3),
                men(1, 3, "common", "the vehicle", "vehicle", 4)]
    doc = NS(toks=toks, mentions=mentions)

    def common_correct(resolver):
        res = resolver.resolve_doc(doc)
        return [c for (mt, _p, c) in res if mt == "common"]  # anaphoric common results in order

    with_bridge = common_correct(TypedCorefResolver(bridge=True, bridge_write=False, type_comparator="typed_spokes"))
    no_bridge = common_correct(TypedCorefResolver(bridge=False))
    # anaphoric commons here are m2 (same-head car) and m3 (different-head vehicle)
    assert with_bridge == [True, True], "bridge arm should resolve both the same-head car and the vehicle bridge: %s" % with_bridge
    assert no_bridge[0] is True and no_bridge[-1] is False, "no-bridge arm must FAIL the vehicle (bridge is load-bearing): %s" % no_bridge
    print("SELFTEST PASS: three-view de-pollution + non-writing typed bridge function (car<->vehicle licensed).")


if __name__ == "__main__":
    _self_test()
