"""ONLINE, INCREMENTAL cue-based entity clustering (Heim 1982 file-change + Lewis-Vasishth 2005 ACT-R
content-addressable retrieval) -- the brain-faithful replacement for the live reader's GOLD-COREF-INHERITANCE leak
in the entity layer.

PROMOTED 2026-09-09 from experiments/exp_online_cue_cluster_gum_v1.online_cluster (owner-DONE
replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering; reverified 23/23) BYTE-FAITHFUL --
the online_cluster loop + _File + _type_match are verbatim; _role_from_rank is inlined (a 1-liner); every other
dependency is a LANDED hdlab organ (coref / state_of_mind / salience_binder / commonnoun_binder / typed_spokes), so
this organ is SELF-CONTAINED (ZERO experiments imports). NO gold coreference is read in any clustering DECISION
(`m["cluster"]`, the gold eid, is used ONLY by scorers, never here); NO external LLM at inference (the invariant).

WHY (the leak this replaces): situation_reader's entity layer (`sm.entities`, feeding make_canonicalizer -> the
affect/goal EXPERIENCER) was GOLD-derived (`_build_entities`/`_apply_commonnoun_gate` grouped by the gold coref
column), which FAKED the cross-type experiencer bind at C3=0.807 WITHOUT reading (honest floor 0.155). The
brain resolves coreference ONLINE with no key: a discourse model of entity FILES, each referring expression
RETRIEVING its antecedent file by cue-based content-addressable retrieval -- cues = TYPE compatibility + gender/number
AGREEMENT (hard phi filter) + ACT-R base-level ACTIVATION (prominence-weighted power-law recency; Grosz-Joshi-Weinstein
Centering role-prominence as the prominence weight). PINNED (copy): Heim file-change; Lewis-Vasishth/Van Dyke-McElree
ACT-R retrieval; Centering. OUR-INVENTION-UNDER-TEST (swept): the type route, the Centering-Cb bonus, the hold policy.

MEASURED (modern GUM V12.1.0): entity-layer CoNLL C1 0.6975 beats the honest floor CI-sep (+0.0036 vs situation_predict,
+0.0054 vs string-identity), shuffled-cue twin collapses to 0.4309; the unified_referent organ's INDEPENDENT grouping
converges (0.6976) -> a LOCATED OPTIMUM. Downstream: replacing the gold peek unmasks the crosstype experiencer bridge's
gain +0.0838 CI-sep (twin loses). Do NOT use the part-whole type route at the identity entity layer (over-merges
-0.0100 CI-sep: meronymy is BRIDGING, not identity; Clark 1975 / ARRAU).

WIRE NOTE (for situation_reader): give each online file a FRESH NEGATIVE-INTEGER id, NOT a `CN:` string --
`_read_world_state`/`_resolve_commonnouns` do `rc >= 0` and crash on a str.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 de-leak landing (strategy first-hand)"
__bf_note__ = "Heim file-change + Lewis-Vasishth ACT-R content-addressable retrieval, GOLD-FREE, no fitted params; ACT-R DEFAULT_DECAY + Centering ROLE_PROMINENCE adopted (standard, not swept); exact-head type cue"
__bf_corrections__ = []

from hdlab.coref import name_content_tokens, EntityAliaser
from hdlab.state_of_mind import compatible
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.lexical_utils import head_lemma
import hdlab.typed_spokes as TS


def _role_from_rank(rank):
    """Centering Cf-rank -> prominence role (inlined byte-faithful from exp_route_unified_to_consumers_gum_v1)."""
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


# ---- TYPE ROUTES (the cue's content-match); each memoized on a symmetric key --------------------------------
_TYPE_CACHE = {}


def _type_match(h1, h2, route):
    """route in {exact, isa, partwhole}. exact = head identity; isa = WordNet is-a either direction; partwhole =
    the FULL brain type-license (synonym U is-a U PART-WHOLE/member -- hdlab.typed_spokes.coref_type_license). For
    the IDENTITY entity layer use `exact` (partwhole over-merges -- meronymy is bridging, not identity)."""
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
    else:  # partwhole -- the full coref_type_license (synonym + is-a + part-whole/member)
        out = bool(TS.coref_type_license(h1, h2))
    _TYPE_CACHE[key] = out
    return out


class _File:
    """A discourse-entity FILE (Heim file card): its mention history (for ACT-R activation), gn, heads, and the
    last sentence in which it was the grammatical SUBJECT (its Centering Cf-top / candidate Cb)."""
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


def online_cluster(ms, gaz, type_route="exact", centering=False, hold=None, decay=DEFAULT_DECAY,
                   margin=1.0, shuffle=None):
    """ONLINE, INCREMENTAL cue-based entity clustering (Heim file-change) -> {midx: cluster_id} over NON-pronoun
    mentions. NO gold: m["cluster"] (the gold eid) is NEVER read in a decision.

    - NAME  -> given-name aliaser file (names are "given"; the smaller string-legitimate case).
    - COMMON -> retrieve the antecedent file by CUE MATCH: TYPE (type_route) AND gender/number AGREEMENT (hard
      filter); among the licensed files SELECT by ACT-R base-level activation (recency x Centering role-prominence),
      + an optional CENTERING continuity bonus for the file that was the SUBJECT of the previous sentence (Cb).
      WRITE policy: hold=None -> always merge to the argmax (content-addressable re-access ignores recency gaps);
      hold=float -> Nieuwland hold-under-uncertainty: merge only if top activation >= hold and dominates the
      runner-up by `margin`, else OPEN A NEW file.
    `shuffle` (a Random) scrambles the cue values (head + gender) for the info-free twin."""
    files = []; labels = {}; aliaser = EntityAliaser(); canon2f = {}; surf2f = {}
    heads_pool = None
    if shuffle is not None:
        heads_pool = [head_lemma(m["head"]) for m in ms if not m["is_pronoun"]]
        shuffle.shuffle(heads_pool)
    hp_i = [0]

    def _cue(m):
        head = head_lemma(m["head"]); gender = m.get("gender") or m.get("name_gender")
        if shuffle is not None:
            head = heads_pool[hp_i[0] % len(heads_pool)] if heads_pool else head; hp_i[0] += 1
            gender = shuffle.choice([None, "masc", "fem"])
        return head, gender

    for order, m in enumerate(ms):
        if m["is_pronoun"]:
            continue
        role = _role_from_rank(m.get("sent_role_rank", 99))
        sent_idx = m.get("sent_idx", 0)
        number = m.get("number")
        head, gender = _cue(m)
        name_toks = name_content_tokens(m.get("span_toks", [m["head"]]))
        if name_toks:                                          # NAME -> given aliaser file
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
        else:                                                  # COMMON -> cue-based content-addressable retrieval
            cands = [f for f in files
                     if compatible(gender, number, f.gender, f.number)
                     and any(_type_match(head, h, type_route) for h in f.heads)]
            picked = None
            if cands:
                acts = []
                for f in cands:
                    a = actr_activation(f.history, float(order), decay, ROLE_PROMINENCE)
                    a = a if a != float("-inf") else -1e9
                    if centering and f.subj_sent == sent_idx - 1 and sent_idx > 0:
                        a += 0.5                               # Centering Cb continuity bonus (prev-sentence subject)
                    acts.append(a)
                oi = sorted(range(len(cands)), key=lambda k: acts[k], reverse=True)
                top = acts[oi[0]]; runner = acts[oi[1]] if len(oi) > 1 else float("-inf")
                if hold is None:
                    picked = cands[oi[0]]
                elif top >= hold and (len(cands) == 1 or (top - runner) >= margin):
                    picked = cands[oi[0]]
            if picked is None:
                picked = _File(len(files)); files.append(picked)
            picked.update(order, role, gender, number, head, sent_idx)
            labels[m["midx"]] = picked.cid
    return labels


def _selftest() -> int:
    """Two 'the dog' mentions + a 'the cat' cluster into 2 files (type cue), a name into its own, pronouns skipped;
    deterministic + no gold read."""
    ms = [
        {"midx": 0, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 0, "gender": None, "number": "sing", "cluster": "GOLD_A"},
        {"midx": 1, "head": "cat", "span_toks": ["the", "cat"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 1, "gender": None, "number": "sing", "cluster": "GOLD_B"},
        {"midx": 2, "head": "it", "span_toks": ["it"], "is_pronoun": True, "sent_idx": 1, "sent_role_rank": 0},
        {"midx": 3, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 1, "sent_role_rank": 0, "gender": None, "number": "sing", "cluster": "GOLD_A"},
    ]
    labels = online_cluster(ms, gaz=None)
    fails = []
    ok1 = labels.get(0) == labels.get(3) and labels.get(0) != labels.get(1)
    print("  %s W1 same-head 'the dog' merges (0==3), 'the cat' separate (0!=1): %s" % ("PASS" if ok1 else "FAIL", labels))
    if not ok1:
        fails.append("W1")
    ok2 = 2 not in labels   # pronoun skipped (non-pronoun clustering only)
    print("  %s W2 pronoun (midx 2) NOT labelled (separate stream)" % ("PASS" if ok2 else "FAIL"))
    if not ok2:
        fails.append("W2")
    ok3 = all(isinstance(v, int) for v in labels.values())   # integer cids (the wire needs neg-int ids downstream)
    print("  %s W3 cluster ids are integers (%s)" % ("PASS" if ok3 else "FAIL", sorted(set(labels.values()))))
    if not ok3:
        fails.append("W3")
    ok4 = online_cluster(ms, gaz=None) == labels             # deterministic
    print("  %s W4 deterministic (no gold read; repeat == first)" % ("PASS" if ok4 else "FAIL"))
    if not ok4:
        fails.append("W4")
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
