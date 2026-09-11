"""hdlab/entity_resolver.py -- ONE cue-based `entity_resolver`: a single ACT-R content-addressable
retrieval CORE with pluggable, MENTION-TYPE-ROUTED cue-arms, SUBSUMING the six live coreference resolvers.

LANDED 2026-09-11 (owner-DONE consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver, Q111):
promoted VERBATIM (byte-identical behavior) from experiments/exp_entity_resolver_unified_v1.EntityResolver. The
reader's four default-on coref entry points route through this ONE organ: online_entity_cluster.online_cluster ->
`cluster`, crosstype_live_adapter's bridge -> `bridge_links`, world_state_entity_binding.EntityBinder ->
`new_stage1_binder`, situation_reader._resolve_commonnouns -> `resolve_commonnouns`. Proven byte-identical by
verification/test_entity_resolver_{unified,typed_commonnoun,reader_substitution}.py (12/12 + 2/2 + 3/3). The BF
lexical helpers this organ needs are imported from hdlab.lexical_utils (split out of the NOT_BF commonnoun_binder).

============================================================================================================
BRAIN-FOUNDATIONAL THESIS (what one structure, replicating or substituting?)
============================================================================================================
PINNED-BY-EVIDENCE. Antecedent/reference resolution is ONE content-addressable, cue-based retrieval mechanism
(Lewis & Vasishth 2005; Parker, Shvartsman & Van Dyke: "binding in comprehension is mediated by a
content-addressable memory system"). A memory chunk's retrieval strength is its ACT-R activation
    A_i = B_i(base-level: recency x frequency x role-prominence)  +  sum_cue W_cue * match_cue(i)
and the anaphor RETRIEVES the argmax. B_i is `hdlab.salience_binder.actr_activation` -- and CRUCIALLY every one
of the six organs ALREADY calls that ONE function for the base term. So the retrieval MATH is not fragmented;
the WRAPPERS are (each organ re-implements the same "assemble candidates by a cue, score by ACT-R activation,
pick argmax under a write/abstain policy" loop with a different cue set + write policy + I/O schema).

PINNED-BY-EVIDENCE, and it is why a NAIVE "one resolver, one cue" merge is WRONG (measured, refuted on disk:
form_the_unified_discourse_referent -> common nouns REGRESS, twin beats it; route_the_unified_referent ->
C2 -0.0089, C3 -0.0780). Ariel 1990 Accessibility Hierarchy: the CUE SET is mention-type-specific --
    PRONOUN (high accessibility)     -> phi-agreement + base-level salience/prominence
    DEFINITE COMMON (low access.)    -> type-compatibility + recency (a NON-writing bridge; salience is wrong)
    DEFINITE -> NAME                 -> in-text descriptive PREDICATION + confidence (Almor desc-content boost)
    NAME                             -> identity (given-name aliasing)
    INDEXICAL (I/me/my)              -> O(1) deixis to the NARRATOR origo (Buehler) -- NOT retrieval at all
So the correct consolidation is exactly "ONE STRUCTURE WITH ARMS": one retrieval CORE, and a MENTION-TYPE ROUTER
that selects the cue-arm set per Ariel. That removes the fragmentation WITHOUT re-committing the refuted merge.

KEEP-SEPARATE (audit, respected here): SALIENCE (salience_binder / event_centrality_coref = the base-level B_i
term) and DRT REFERENT CONSTRUCTION (referent_per_np) are UPSTREAM of retrieval, not the retrieval step. This
module IMPORTS actr_activation; it never re-implements it.

WHAT IS GENUINELY DISTINCT (located negatives, kept as ROUTING arms / cue-PRODUCERS, not retrieval cue-arms):
  * The INDEXICAL/PLEONASTIC dispatch (world_state_entity_binding) is deixis + expletive detection -- an O(1)
    speech-role lookup, NOT O(n) content-addressable search. It ROUTES anaphoric cases INTO the core; it is a
    routing arm, not a cue-arm.
  * The PRECISE-CONSTRUCTS predication detector (crosstype_bridge) is in-text relation EXTRACTION over UD syntax
    -- a cue-PRODUCER feeding the definite->name arm's descriptive-content license, not a retrieval itself.

============================================================================================================
WHAT THIS CELL PROVES (Q111: proposal + proof, not a landing)
============================================================================================================
`EntityResolver` below owns ONE retrieval core (`_retrieve`) + ONE write-policy engine + the Ariel router, and
exposes the SAME entry points the six organs expose, each a declarative arm config. The witnesses
(verification/test_entity_resolver_unified.py) prove -- on real GUM mentions -- that the unified core reproduces
the LIVE-wired resolvers BYTE-IDENTICALLY:
  * `cluster(ms, gaz)`            == hdlab.online_entity_cluster.online_cluster          (sm.entities producer)
  * `bridge_links(doc, gaz, ...)` == hdlab.crosstype_bridge.crosstype_bridge_links       (definite->name bridge)
  * `bind_participant`/`bind_theme` == hdlab.world_state_entity_binding.EntityBinder      (world-state Stage-1)
  * `typed_common_pick(...)`      == the typed_coref common/pronoun retrieval step (shared core)

Glass-box, CPU, nltk-WordNet only, NO external LLM at inference. Self-contained hdlab imports (the shared
primitives the organs already share); ZERO experiments/ imports at module load.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-11 consolidation landing (strategy first-hand; byte-identical port of the owner-DONE unified organ)"
__bf_note__ = ("ONE ACT-R content-addressable retrieval CORE (salience_binder.actr_activation base-level, PINNED) + the "
               "Ariel Accessibility mention-type ROUTER over pluggable cue-arms (type / name-bridge / morphosyntactic / "
               "KB-prior). Composes pinned math under one dispatcher; the single SHARED deviation is the HARD phi/type "
               "FILTER-then-rank vs L&V GRADED parallel cue-combination -- now single-point (a separate behavior-changing "
               "problem: strengthen_the_cue_based_pronoun_coreference_resolver). No NEW convenience stand-in introduced.")
__bf_corrections__ = []

import math
from collections import Counter, defaultdict
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# -- the SHARED primitives every organ already calls (the retrieval math + cues live here; not re-implemented) --
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.coref import EntityAliaser, name_content_tokens
from hdlab.state_of_mind import compatible
from hdlab.lexical_utils import head_lemma, person_synset   # BF lexical foundation (split from the NOT_BF commonnoun_binder)
import hdlab.typed_spokes as TS


NEG_INF = -1e9   # the finite floor every organ substitutes for actr_activation's -inf (empty history)


# ==========================================================================================================
# THE ONE RETRIEVAL CORE  --  content-addressable, cue-based, ACT-R-scored argmax under a write policy.
# ==========================================================================================================
def _base_activation(history, now, decay, role_prominence) -> float:
    """B_i = ACT-R base-level activation (salience_binder), with the organs' shared -inf -> -1e9 floor."""
    a = actr_activation(history, float(now), decay, role_prominence)
    return a if a != float("-inf") else NEG_INF


def retrieve(files: Sequence, now: float, *,
             license: Callable, bonus: Optional[Callable] = None,
             decay: float = DEFAULT_DECAY, role_prominence: Optional[Dict[str, float]] = None,
             policy: str = "argmax", threshold: float = 0.0, margin: float = 0.0,
             abstain_below: Optional[Callable] = None, key_of: Optional[Callable] = None,
             score_of: Optional[Callable] = None,
             history_of: Callable = lambda f: f.history) -> Tuple[Optional[object], list, list]:
    """THE ONE content-addressable cue-based retrieval used by every resolver arm.

    * candidate set  = the files a cue LICENSES (parallel cue match; hard phi/type filter -- see the FIDELITY
      note in the module docstring: L&V is graded cue-combination, our organs hard-filter; that deviation is
      SHARED by all six and is preserved here so a future graded upgrade is single-point).
    * activation     = base-level B_i (ACT-R) + optional cue BONUS (e.g. Almor descriptive-content boost).
    * pick           = argmax, under a WRITE POLICY:
        'argmax'  : take the top (always-merge; online_entity_cluster default).
        'hold'    : Nieuwland hold-under-uncertainty -- merge only if top >= threshold AND it dominates the
                    runner-up by `margin` (else return None -> caller opens a new file).
        'compete' : Heim/DRT full-referent competition -- take the top only if it dominates by `margin`; an
                    `abstain_below(top_score)` predicate can veto (McElree low-activation = novel -> abstain).
    Returns (picked_file_or_None, licensed_files, activations) -- the caller does the write/open bookkeeping."""
    cands = [f for f in files if license(f)]
    if not cands:
        return None, [], []
    acts = []
    for f in cands:
        # base score: ACT-R base-level (default) OR a caller-supplied selector (e.g. pure RECENCY for a definite's
        # same-head incumbent -- Ariel: low-accessibility markers retrieve by recency, a special case of base-level).
        a = score_of(f) if score_of is not None else _base_activation(history_of(f), now, decay, role_prominence)
        if bonus is not None:
            a += bonus(f)
        acts.append(a)
    # primary key = activation (desc); optional secondary tie-break key (e.g. crosstype breaks A-ties by eid desc,
    # online_cluster uses stable/lowest-index == secondary constant). This is a per-ARM policy detail, not the core.
    if key_of is None:
        order = sorted(range(len(cands)), key=lambda k: acts[k], reverse=True)
    else:
        order = sorted(range(len(cands)), key=lambda k: (acts[k], key_of(cands[k])), reverse=True)
    top_i = order[0]
    top = acts[top_i]
    runner = acts[order[1]] if len(order) > 1 else float("-inf")
    if policy == "argmax":
        picked = cands[top_i]
    elif policy == "hold":
        picked = cands[top_i] if (top >= threshold and (len(cands) == 1 or (top - runner) >= margin)) else None
    elif policy == "compete":
        dominates = (len(cands) == 1) or ((top - runner) >= margin)
        if abstain_below is not None and abstain_below(top):
            dominates = False
        picked = cands[top_i] if dominates else None
    else:
        raise ValueError("unknown policy %r" % policy)
    return picked, cands, acts


# ==========================================================================================================
# CUE-ARM primitives (the pluggable content-match cues; each licenses a candidate given a query).
# ==========================================================================================================
_TYPE_CACHE: Dict[tuple, bool] = {}


def type_match(h1: str, h2: str, route: str) -> bool:
    """TYPE cue. route in {exact, isa, partwhole}: head identity / WordNet is-a either dir / full coref license
    (synonym U is-a U part-whole). Byte-faithful to online_entity_cluster._type_match (same memo, same routes)."""
    if h1 == h2:
        return True
    if route == "exact":
        return False
    key = (route, h1, h2) if h1 <= h2 else (route, h2, h1)
    c = _TYPE_CACHE.get(key)
    if c is not None:
        return c
    if route == "isa":
        s1 = TS._mfs_synset(h1); s2 = TS._mfs_synset(h2)
        out = bool(s1 and s2 and ((s2 in TS.isa_ancestors(s1)) or (s1 in TS.isa_ancestors(s2))))
    else:
        out = bool(TS.coref_type_license(h1, h2))
    _TYPE_CACHE[key] = out
    return out


def _role_from_rank(rank) -> str:
    """Centering Cf-rank -> prominence role (byte-faithful to online_entity_cluster._role_from_rank)."""
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


# ==========================================================================================================
# THE FILE (Heim file card) -- one discourse-entity's mention history + agreement + heads + Centering subj-sent.
# ==========================================================================================================
class _File:
    __slots__ = ("cid", "history", "gender", "number", "heads", "subj_sent")

    def __init__(self, cid):
        self.cid = cid; self.history = []; self.gender = None; self.number = None
        self.heads = set(); self.subj_sent = -1

    def update(self, order, role, gender, number, head, sent_idx):
        self.history.append((float(order), role))
        if gender and self.gender is None:
            self.gender = gender
        if number and self.number is None:
            self.number = number
        if head:
            self.heads.add(head)
        if role == "SUBJECT":
            self.subj_sent = sent_idx


# ==========================================================================================================
# THE UNIFIED RESOLVER  --  one core, one write engine, the Ariel mention-type router; the six organs' entries.
# ==========================================================================================================
class EntityResolver:
    """ONE cue-based entity resolver. Every public method is a declarative config of {router selects arm-set,
    retrieve() scores by the shared ACT-R core, write policy commits}. The methods reproduce the six organs'
    live entry points byte-identically (proof: verification/test_entity_resolver_unified.py)."""

    def __init__(self, *, decay: float = DEFAULT_DECAY, role_prominence: Optional[Dict[str, float]] = None):
        self.decay = decay
        self.role_prominence = ROLE_PROMINENCE if role_prominence is None else role_prominence

    # ---------------------------------------------------------------------------------------------------
    # ARM 1 (default-on live) -- ONLINE CLUSTERING of names + definite commons  == online_entity_cluster
    #   Router: NAME -> identity (aliaser); COMMON -> [phi, type_exact] cue, base-level argmax, always-merge.
    # ---------------------------------------------------------------------------------------------------
    def cluster(self, ms, gaz, *, type_route: str = "exact", centering: bool = False,
                hold: Optional[float] = None, margin: float = 1.0) -> Dict[int, int]:
        """{midx: cluster_id} over NON-pronoun mentions -- reproduces online_entity_cluster.online_cluster.
        NAME -> given-name aliaser file (identity). COMMON -> retrieve() over the phi-compatible, type-licensed
        prior files, scored by the shared ACT-R base-level (+ optional Centering-Cb continuity bonus), committed
        by the write policy (always-merge, or hold-under-uncertainty)."""
        files: List[_File] = []
        labels: Dict[int, int] = {}
        aliaser = EntityAliaser(); canon2f: Dict[object, _File] = {}; surf2f: Dict[str, _File] = {}
        for order, m in enumerate(ms):
            if m["is_pronoun"]:
                continue
            role = _role_from_rank(m.get("sent_role_rank", 99))
            sent_idx = m.get("sent_idx", 0)
            number = m.get("number")
            head = head_lemma(m["head"]); gender = m.get("gender") or m.get("name_gender")
            name_toks = name_content_tokens(m.get("span_toks", [m["head"]]))
            if name_toks:                                           # NAME -> identity (given-name file)
                canon = aliaser.assign(m.get("span_toks", [m["head"]]), gender)
                key = canon if canon is not None else ("surf:" + m["head"])
                f = canon2f.get(key) or surf2f.get(m["head"])
                if f is None:
                    f = _File(len(files)); files.append(f)
                    if canon is not None:
                        canon2f[key] = f
                    surf2f[m["head"]] = f
                f.update(order, role, gender, number, None, sent_idx)
                labels[m["midx"]] = f.cid
            else:                                                   # COMMON -> ONE cue-based retrieval
                def _license(f, _h=head, _g=gender, _n=number, _r=type_route):
                    return compatible(_g, _n, f.gender, f.number) and any(type_match(_h, h, _r) for h in f.heads)

                def _bonus(f, _si=sent_idx):
                    return 0.5 if (centering and f.subj_sent == _si - 1 and _si > 0) else 0.0

                policy = "argmax" if hold is None else "hold"
                picked, _c, _a = retrieve(files, order, license=_license,
                                          bonus=_bonus if centering else None,
                                          decay=self.decay, role_prominence=self.role_prominence,
                                          policy=policy, threshold=(hold or 0.0), margin=margin)
                if picked is None:
                    picked = _File(len(files)); files.append(picked)
                picked.update(order, role, gender, number, head, sent_idx)
                labels[m["midx"]] = picked.cid
        return labels

    # ---------------------------------------------------------------------------------------------------
    # ARM 0 (GENERALIZE: the pronoun arm) -- PRONOUN pick (Ariel high-accessibility)  == salience_binder.bind
    #   Router: PRONOUN. Cue: phi-agreement (applied by the caller -> it supplies the phi-compatible candidate
    #   HISTORIES) + base-level ACT-R salience. Retrieve: argmax activation (the pinned pronoun pick). This shows
    #   the ONE core serves ALL FOUR Ariel mention types; the SALIENCE MATH (actr_activation) stays in
    #   salience_binder (KEEP-separate) -- only the argmax RETRIEVAL is the shared core.
    # ---------------------------------------------------------------------------------------------------
    def pronoun_pick(self, candidates, now, *, decay=None, role_prominence=None) -> int:
        """Return the index of the retrieved antecedent for a pronoun -- reproduces salience_binder.bind (argmax
        ACT-R base-level activation over the caller's phi-compatible candidate histories; ties -> lowest index).
        `candidates` is a sequence of mention HISTORIES [(time, role), ...]. -1 if empty."""
        n = len(candidates)
        if n == 0:
            return -1
        _p, cands, acts = retrieve(list(candidates), now, license=lambda f: True,
                                   decay=(self.decay if decay is None else decay),
                                   role_prominence=(self.role_prominence if role_prominence is None else role_prominence),
                                   policy="argmax", history_of=lambda h: h)
        # cands preserves input order (license all-True) -> reproduce np.argmax first-max (lowest-index) tie-break.
        best = 0
        for i in range(1, len(acts)):
            if acts[i] > acts[best]:
                best = i
        return best

    # ---------------------------------------------------------------------------------------------------
    # ARM 2 (default-on live) -- DEFINITE -> NAME cross-type BRIDGE  == crosstype_bridge.crosstype_bridge_links
    #   Router: definite person role-noun. Cue-PRODUCER: precise_constructs (in-text predication, imported).
    #   Retrieve: [predication-desc-boost + phi] over the NAME cards, base-level ACT-R, compete + confidence.
    # ---------------------------------------------------------------------------------------------------
    def bridge_links(self, doc, gaz, *, conf_thr: float, margin: float = 0.5, mode: str = "cue_conf") -> Dict[int, int]:
        """{role_midx: name_eid} -- reproduces crosstype_bridge.crosstype_bridge_links for ALL FIVE cue modes
        (cue_retrieval / cue_gated / cue_competed / cue_novelty / cue_conf), restrict_gold=False, salience='actr'.
        LIVE reader uses mode='cue_conf' @ conf_thr=-3.0 (via crosstype_live_adapter); the board experiencer
        instrument uses mode='cue_competed'. The predication detector (precise_constructs) is a cue-PRODUCER
        (imported, not re-implemented -- a genuinely distinct in-text extraction); the RETRIEVAL/competition stage
        is the shared core with a descriptive-content boost bonus + a per-mode gate/abstain policy."""
        from hdlab.crosstype_bridge import (precise_constructs, head_lemma as _hl,
                                            _AGE_GENDER, _ART, _NONPERSON_STOP, _DESC_BOOST, _ORD_SUP, _mention_role)
        licensed, ent_person = precise_constructs(doc, gaz)
        ms = doc.mentions
        by_gidx = {t.gidx: t for t in doc.toks}
        # children index (by head gidx) -- needed only by the cue_novelty establishing-modifier gate.
        _bysi = {(t.sent, t.idx): t.gidx for t in doc.toks}
        _children = defaultdict(list)
        for _t in doc.toks:
            _hg = _bysi.get((_t.sent, _t.head))
            if _hg is not None:
                _children[_hg].append(_t)

        def _establishing_modifier(head_g):
            """Hawkins/Bean-Riloff: a restrictive establishing modifier (relcl, post-head nmod, superlative,
            ordinal) marks a definite as first-mention -> abstain. Byte-faithful to crosstype_bridge."""
            h = by_gidx.get(head_g)
            if h is None:
                return False
            for c in _children.get(head_g, ()):
                full = (c.deprel or ""); dep = full.split(":")[0]
                if full == "acl:relcl" or dep == "acl":
                    return True
                if dep == "nmod" and c.idx > h.idx:
                    return True
                if dep == "amod" and (c.xpos == "JJS" or (c.form or "").lower() in _ORD_SUP):
                    return True
                if dep == "nummod" or (c.form or "").lower() in _ORD_SUP:
                    return True
            return False

        def _person_def(L):
            return L not in _NONPERSON_STOP and person_synset(L) is not None

        firstname: Dict[object, int] = {}
        name_gender_order: List[tuple] = []
        name_gender: Dict[object, str] = {}
        name_hist = defaultdict(list)
        common_head_orders = defaultdict(list)
        for i, m in enumerate(ms):
            if m.mtype == "common":
                common_head_orders[_hl(m.lemma_head)].append(i)
            if m.mtype == "name" and m.eid in ent_person:
                firstname.setdefault(m.eid, i)
                name_gender_order.append((i, m.eid, m.gender))
                name_hist[m.eid].append((i, _mention_role(by_gidx, m)))
                if m.gender in ("m", "f") and m.eid not in name_gender:
                    name_gender[m.eid] = "masc" if m.gender == "m" else "fem"
        binds: Dict[int, int] = {}
        for i, m in enumerate(ms):
            if m.mtype != "common":
                continue
            L = _hl(m.lemma_head); toks = m.text.lower().split()
            if not toks or toks[0] not in _ART or not _person_def(L):
                continue
            if not any(o < i for (o, _e, _g) in name_gender_order):     # DEPLOYMENT population (restrict_gold=False)
                continue
            named = licensed.get(L, set())
            ag = _AGE_GENDER.get(L)
            # per-mode ANAPHORICITY gate (byte-faithful to gated_binds):
            #  cue_gated  -> fire only on predication-licensed OR age/gender re-mention;
            #  cue_competed/cue_novelty/cue_conf -> full-referent competition (a same-head prior common wins);
            #  cue_novelty -> also abstain on a Hawkins establishing modifier;
            #  cue_retrieval -> no gate.
            gate_ok = not (mode == "cue_gated" and not named and ag is None)
            if mode in ("cue_competed", "cue_novelty", "cue_conf"):
                prior_common = any(o < i for o in common_head_orders.get(L, ()))
                if not named and prior_common:
                    gate_ok = False
            if mode == "cue_novelty" and not named and _establishing_modifier(m.head_g):
                gate_ok = False

            # candidate NAME cards, phi(age/gender)-filtered; retrieved by the shared core over their name-mention
            # histories, with the Almor descriptive-content boost for predication-licensed names.
            class _NameCard:
                __slots__ = ("eid", "history")

                def __init__(self, eid, history):
                    self.eid = eid; self.history = history

            cards = []
            for e, hist in (name_hist.items() if gate_ok else ()):
                priors = [(o, r) for (o, r) in hist if o < i]
                if not priors:
                    continue
                if ag is not None and ag != "any":
                    g = name_gender.get(e)
                    if g is not None and g != ag:
                        continue
                cards.append(_NameCard(e, priors))

            def _license(c):
                return True                                             # phi already applied; predication is a bonus

            def _bonus(c, _named=named, _boost=_DESC_BOOST):
                return _boost if c.eid in _named else 0.0

            def _abstain_below(top, _thr=conf_thr, _boost=_DESC_BOOST, _mode=mode):
                # cue_conf ONLY: abstain when the best NON-predicated candidate's activation < conf_thr (McElree novel).
                return _mode == "cue_conf" and top < _boost and top < _thr

            picked, _c, _a = retrieve(cards, i, license=_license, bonus=_bonus,
                                      decay=DEFAULT_DECAY, role_prominence=ROLE_PROMINENCE,
                                      policy="compete", margin=margin, abstain_below=_abstain_below,
                                      key_of=lambda c: c.eid)
            if picked is not None:
                binds[i] = picked.eid
        return binds

    # ---------------------------------------------------------------------------------------------------
    # ARM 1b (default-on live) -- TYPED COMMON-NOUN RESOLUTION  == situation_reader._resolve_commonnouns
    #   The typed_coref binding on the reader's own dict stream (Ariel low-accessibility definite):
    #     NAME    -> identity (aliaser / concept-key);
    #     COMMON same-head -> RECENCY incumbent (score_of=last_midx through the ONE core);
    #     COMMON diff-head -> NON-WRITING type/appos/C8/conceptual/coarse bridge, ACT-R argmax (the ONE core);
    #     PRONOUN -> phi + ACT-R argmax (writes the salience card only; Ariel/Nieuwland de-pollution).
    #   The 5 bridge CUES (in-text appos is-a, typed-spokes license, C8 encyclopedic, conceptual, coarse-focus)
    #   are cue-PRODUCERS supplied by the reader/organs -- feature extractors, not retrieval; the retrieval loop
    #   folds into the ONE core. Reproduces reader._resolve_commonnouns BYTE-IDENTICALLY (takes `reader` for its
    #   cue-producers + bridge flags; the hdlab landing repoints the reader method to call this).
    # ---------------------------------------------------------------------------------------------------
    def resolve_commonnouns(self, role_mentions, sents, reader) -> list:
        """{per non-pronoun mention: midx/mtype/own_ref/resolved_ref} -- byte-identical to
        situation_reader._resolve_commonnouns. `reader` supplies the cue-producers (_commonnoun_appos_map,
        _cn_type_rel) and the bridge flags (conceptual_bridge / focus_bridge / uniqueness_bridge / uniq_window)."""
        import hdlab.typed_coref as _TC
        from hdlab.lexical_utils import concept_lemma, is_name, _num_of, DEF_DET, coarse_class
        from hdlab.coref import EntityAliaser
        from hdlab.typed_spokes import type_licenses as _c8_type_licenses, available_entity_type as _c8_available
        from hdlab.situation_reader import _pron_gn
        _c8_on = _c8_available(); _c8_cache = {}

        def _c8_lic(head, surface):
            if not _c8_on:
                return False
            k = (head, surface); v = _c8_cache.get(k)
            if v is None:
                v = _c8_type_licenses(head, surface); _c8_cache[k] = v
            return v

        appos_map = reader._commonnoun_appos_map(sents)
        _g2mfn = {"masc": "m", "fem": "f", "neut": "n"}

        class _Ref:
            __slots__ = ("rid", "history", "heads", "name_tokens", "name_surfaces", "gender", "number",
                         "has_name", "last_midx")

            def __init__(self, rid):
                self.rid = rid; self.history = []; self.heads = set(); self.name_tokens = set()
                self.name_surfaces = set(); self.gender = ""; self.number = ""; self.has_name = False
                self.last_midx = -1

            def write(self, order, role, mtype, hl, mg, mn, ntoks_):
                self.history.append((order, role)); self.last_midx = order
                if mg and not self.gender:
                    self.gender = mg
                if mn and not self.number:
                    self.number = mn
                if mtype == "name":
                    self.has_name = True; self.name_tokens |= ntoks_
                elif mtype == "common":
                    self.heads.add(hl)

        def mfn(m):
            return _g2mfn.get(m.get("gender") or m.get("name_gender") or "", "")

        def gn_ok(rg, rn, mg, mn):
            if mg and rg and mg != rg:
                return False
            if mn and rn and mn != rn:
                return False
            return True

        def ntoks(span):
            return {w.lower() for w in span if w.lower() not in _TC.TITLES and any(c.isalpha() for c in w)}

        aliaser = EntityAliaser(); canon2ref = {}; name_surf = {}
        refs = []; out = []; nid = [0]

        def new_ref():
            r = _Ref(nid[0]); nid[0] += 1; refs.append(r); return r

        _conc_ch = [None]; _conc_cache = {}

        def _coarse_compat(a, heads):
            ca = coarse_class(a)
            return ca is not None and any(coarse_class(h) == ca for h in heads)

        def _conc_bridge(a, b):
            if a == b:
                return True
            k = (a, b) if a <= b else (b, a); v = _conc_cache.get(k)
            if v is None:
                if _conc_ch[0] is None:
                    from hdlab.conceptual_meaning import ConceptualChannel
                    _conc_ch[0] = ConceptualChannel()
                try:
                    s = _conc_ch[0].similarity(a, "N", b, "N")
                except Exception:
                    s = None
                v = (s is not None and s >= 0.40); _conc_cache[k] = v
            return v

        for m in sorted(role_mentions, key=lambda x: x["midx"]):
            order = m["midx"]
            role = "SUBJECT" if m.get("sent_role_rank", 99) == 0 else "OTHER"
            span = m.get("span_toks", [m["head"]])
            if m["is_pronoun"]:
                mg, mn = _pron_gn(m["head"].lower())
                cands = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
                if cands:                                           # PRONOUN: phi + ACT-R argmax (the ONE core)
                    picked, _c, _a = retrieve(cands, order, license=lambda f: True,
                                              decay=self.decay, role_prominence=self.role_prominence, policy="argmax")
                    picked.write(order, role, "pronoun", "", mg, mn, set())
                continue
            hl = concept_lemma(m["head"]); mg, mn = mfn(m), _num_of(m)
            if is_name(m, None):                                     # NAME: identity (aliaser / concept-key)
                canon = aliaser.assign(span, (m.get("gender") or m.get("name_gender")) or None)
                if canon is not None and canon in canon2ref:
                    r = canon2ref[canon]; opened = False
                elif hl in name_surf:
                    r = name_surf[hl]; opened = False
                else:
                    r = new_ref(); opened = True
                    if canon is not None:
                        canon2ref[canon] = r
                    name_surf[hl] = r
                out.append({"midx": order, "mtype": "name", "own_ref": r.rid,
                            "resolved_ref": (None if opened else r.rid)})
                r.write(order, role, "name", hl, mg, mn, ntoks(span))
                r.name_surfaces.add(" ".join(span))
                continue
            same = [r for r in refs if r.last_midx < order and hl in r.heads and gn_ok(r.gender, r.number, mg, mn)]
            picked = None; opened = True; nowrite = None
            definite = bool(span) and span[0].lower() in DEF_DET
            if same:                                                 # SAME-HEAD: RECENCY incumbent (the ONE core, score_of=last_midx)
                picked, _c, _a = retrieve(same, order, license=lambda f: True,
                                          score_of=lambda r: r.last_midx, policy="argmax"); opened = False
            else:                                                    # DIFF-HEAD: non-writing type/appos/C8/conceptual/coarse bridge
                tset = appos_map.get(hl, set())
                prior_gn = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
                br = [r for r in prior_gn if (r.heads & tset)
                      or (r.has_name and any(t in r.name_tokens for t in tset))
                      or any(reader._cn_type_rel(hl, h) for h in r.heads)
                      or (r.has_name and any(_c8_lic(hl, ns) for ns in r.name_surfaces))
                      or (reader.conceptual_bridge and any(_conc_bridge(hl, h) for h in r.heads))
                      or (reader.focus_bridge and definite and _coarse_compat(hl, r.heads))]
                if br:                                               # ACT-R argmax over the licensed bridge set (the ONE core)
                    nowrite, _c, _a = retrieve(br, order, license=lambda f: True,
                                               decay=self.decay, role_prominence=self.role_prominence, policy="argmax")
                elif reader.uniqueness_bridge and definite:
                    infocus = [r for r in prior_gn if r.last_midx >= order - reader.uniq_window]
                    if len(infocus) == 1:
                        nowrite = infocus[0]
            if picked is None:
                picked = new_ref()
            resolved = (nowrite.rid if nowrite is not None else (None if opened else picked.rid))
            out.append({"midx": order, "mtype": "common", "own_ref": picked.rid, "resolved_ref": resolved})
            picked.write(order, role, "common", hl, mg, mn, set())
        return out

    # ---------------------------------------------------------------------------------------------------
    # ARM 3 (default-on live) -- WORLD-STATE STAGE-1 DISPATCH  == world_state_entity_binding.EntityBinder
    #   A DEICTIC ROUTER (indexical -> narrator O(1); pleonastic-it filter; anaphoric -> consume core output;
    #   nominal -> canonical head). Located negative: the deictic routes are NOT content-addressable retrieval.
    # ---------------------------------------------------------------------------------------------------
    def new_stage1_binder(self, narrator_key: str = "~NARRATOR"):
        """Return an EntityBinder-equivalent Stage-1 dispatcher (the output-normalisation + deixis arm). It
        ROUTES: indexical (I/me/my) -> narrator (O(1) deixis, not retrieval); anaphoric (he/she) -> consume the
        core's coref cluster; object-anaphora (it/them) -> the salient recent nominal theme (Centering-lite);
        nominal -> canonical head. This is a routing arm around the retrieval core, kept distinct because deixis
        is an O(1) speech-role lookup, not O(n) content-addressable search."""
        return _Stage1Dispatcher(narrator_key)

    # ---------------------------------------------------------------------------------------------------
    # ARM 4 (DORMANT) -- KB-PRIOR cue-arm  == entity_world_model_resolver (role/kinship/scenario prior)
    #   The sixth organ folds into the ONE resolver as its KB-PRIOR arm. It is DORMANT (reader flag
    #   entity_kb_resolver=False) -> there is NO live behavior to reproduce byte-identically; it is folded
    #   PROVEN-IN-KIND: a curated role/kinship world-knowledge prior is a `bonus` cue over the shared core,
    #   the SAME `bonus` slot the crosstype descriptive-content boost (`_DESC_BOOST`) already uses byte-identically.
    #   When activated, its role/kinship/scenario prior enters retrieve() as an additive activation bonus (it does
    #   NOT introduce a new retrieval STRUCTURE). Kept as a lazy delegation so this module carries NO experiments/
    #   import at load (self-containment); the dormant chain's own experiments-import debt is a filed follow-on.
    # ---------------------------------------------------------------------------------------------------
    def kb_prior_cluster(self, mentions, gaz, *, reader_coref=None, window: int = 8) -> Dict[int, object]:
        """{midx: label} via the DORMANT role/kinship/scenario KB-prior arm (entity_world_model_resolver). Folds
        the sixth organ into the ONE resolver as a KB-prior cue-arm (a `bonus` over the shared retrieval core --
        the same slot crosstype's descriptive-content boost uses). DORMANT: not on any default live path
        (entity_kb_resolver=False); reachable only when a caller opts into the KB prior. Lazy delegation keeps
        this organ free of experiments/ imports at module load."""
        from hdlab.entity_world_model_resolver import resolve_common_noun
        return resolve_common_noun(mentions, gaz, reader_coref=reader_coref, window=window)


# ==========================================================================================================
# ARM 3 impl -- byte-faithful reproduction of world_state_entity_binding.EntityBinder (the deictic router).
# ==========================================================================================================
_FIRST_SG = {"i", "me", "my", "mine", "myself"}
_HE_SHE = {"he", "him", "his", "she", "her", "hers"}
_OBJ_PRON = {"it", "them", "they", "its"}
_SCOPE_OUT = {"we", "us", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves"}
_PLEONASTIC_VERBS = {"take", "takes", "took", "give", "gives", "gave", "cost", "costs", "require", "requires"}


class _Stage1Dispatcher:
    def __init__(self, narrator_key="~NARRATOR"):
        self.narrator = narrator_key
        self.recent_nominal_theme: Optional[str] = None
        self.stats = Counter()

    @staticmethod
    def route_of(head: Optional[str]) -> str:
        if head is None:
            return "none"
        h = head.lower()
        if h in _FIRST_SG:
            return "indexical"
        if h in _HE_SHE:
            return "anaphoric"
        if h in _OBJ_PRON:
            return "object_anaphora"
        if h in _SCOPE_OUT:
            return "scope_out"
        return "nominal"

    def is_pleonastic_it(self, head, verb, role) -> bool:
        if head.lower() != "it":
            return False
        if role == "agent" and verb and verb.lower() in _PLEONASTIC_VERBS:
            return True
        if role in ("theme", "object") and self.recent_nominal_theme is None:
            return True
        return False

    def bind_participant(self, head, coref_cluster=None, verb=None, coref_entropy=None, abstain_tau=None) -> tuple:
        r = self.route_of(head)
        if r == "indexical":
            self.stats["indexical"] += 1
            return self.narrator, "indexical"
        if r == "anaphoric":
            if coref_cluster is None:
                self.stats["anaphoric_unresolved"] += 1
                return None, "anaphoric_abstain"
            if abstain_tau is not None and coref_entropy is not None and coref_entropy > abstain_tau:
                self.stats["anaphoric_low_conf_abstain"] += 1
                return None, "anaphoric_low_conf_abstain"
            self.stats["anaphoric_resolved"] += 1
            return "C%s" % coref_cluster, "anaphoric"
        if r == "object_anaphora":
            self.stats["participant_objpron_abstain"] += 1
            return None, "abstain"
        if r == "scope_out":
            self.stats["scope_out_abstain"] += 1
            return None, "scope_out"
        if r == "nominal":
            self.stats["nominal"] += 1
            return head.lower(), "nominal"
        return None, "none"

    def bind_theme(self, head, verb=None) -> tuple:
        if head is None:
            return None, "none"
        r = self.route_of(head)
        if r == "object_anaphora":
            if self.is_pleonastic_it(head, verb, "theme"):
                self.stats["pleonastic_it_abstain"] += 1
                return None, "pleonastic_abstain"
            if self.recent_nominal_theme is not None:
                self.stats["object_anaphora_resolved"] += 1
                return self.recent_nominal_theme, "object_anaphora"
            self.stats["object_anaphora_noantecedent"] += 1
            return head.lower(), "object_raw"
        if r == "nominal":
            self.recent_nominal_theme = head.lower()
            self.stats["theme_nominal"] += 1
            return head.lower(), "nominal"
        if r == "indexical":
            return self.narrator, "indexical"
        return (head.lower() if head else None), r


# ==========================================================================================================
# module self-test (corpus-free): the ONE core reproduces each arm's decision on a small deterministic case.
# ==========================================================================================================
def _selftest() -> int:
    fails = []
    R = EntityResolver()

    # ARM 1: two 'the dog' + one 'the cat' -> two files; name -> own; pronoun skipped (== online_cluster).
    ms = [
        {"midx": 0, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 0, "gender": None, "number": "sing"},
        {"midx": 1, "head": "cat", "span_toks": ["the", "cat"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 1, "gender": None, "number": "sing"},
        {"midx": 2, "head": "it", "span_toks": ["it"], "is_pronoun": True, "sent_idx": 1, "sent_role_rank": 0},
        {"midx": 3, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 1, "sent_role_rank": 0, "gender": None, "number": "sing"},
    ]
    lab = R.cluster(ms, gaz=None)
    ok1 = lab.get(0) == lab.get(3) and lab.get(0) != lab.get(1) and 2 not in lab and all(isinstance(v, int) for v in lab.values())
    print("  %s A1 cluster: same-head merges (0==3), cat separate, pronoun skipped, int ids: %s" % ("PASS" if ok1 else "FAIL", lab))
    if not ok1:
        fails.append("A1")

    # ARM 3: indexical collapse, anaphoric consume, object-anaphora Centering, pleonastic + scope-out abstain.
    b = R.new_stage1_binder()
    ok3 = (b.bind_participant("I")[0] == b.bind_participant("me")[0] == "~NARRATOR"
           and b.bind_participant("he", coref_cluster=5) == ("C5", "anaphoric")
           and b.bind_participant("she", coref_cluster=None)[1] == "anaphoric_abstain"
           and b.bind_participant("we")[0] is None)
    b2 = R.new_stage1_binder()
    ok3b = (b2.bind_theme("it")[1] == "pleonastic_abstain" and b2.bind_theme("cup")[0] == "cup"
            and b2.bind_theme("it") == ("cup", "object_anaphora"))
    print("  %s A3 stage1 dispatch: indexical/anaphoric/object-anaphora/pleonastic routes: %s" % ("PASS" if ok3 and ok3b else "FAIL", ok3 and ok3b))
    if not (ok3 and ok3b):
        fails.append("A3")

    # core: the write policies behave (argmax vs hold-under-uncertainty).
    class _F:
        def __init__(self, cid, hist):
            self.cid = cid; self.history = hist
    files = [_F(0, [(0.0, "SUBJECT")]), _F(1, [(1.0, "OTHER")])]
    p_arg, _, _ = retrieve(files, 3.0, license=lambda f: True, policy="argmax")
    p_hold, _, _ = retrieve(files, 3.0, license=lambda f: True, policy="hold", threshold=100.0, margin=1.0)
    okc = p_arg is files[0] and p_hold is None
    print("  %s CORE policies: argmax picks top; hold-under-high-threshold opens new: %s" % ("PASS" if okc else "FAIL", okc))
    if not okc:
        fails.append("CORE")

    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
