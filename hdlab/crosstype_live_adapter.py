"""hdlab/crosstype_live_adapter.py -- DE-LEAK PART 2: the LIVE, GOLD-FREE crosstype definite->name BRIDGE adapter.

Promoted 2026-09-09 from the owner-DONE de-leak
(`replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering`, Q111). PART 1
(`hdlab/online_entity_cluster.online_cluster`) replaced the reader's GOLD-coref-inherited entity layer with a
brain-faithful ONLINE cue-based clustering; PART 2 (this module) makes the landed-latent crosstype bridge
(`hdlab/crosstype_bridge`) LOAD-BEARING on that honest layer -- it supplies the cross-type common->name link the
gold peek used to FAKE (the +0.0838 CI-sep experiencer gain the peek was hiding, twin losing, live-parse ~0.86 prec).

WHAT IT DOES: given the reader's `role_mentions` (the parse_litbank_conll / _gum_to_live dict shape), the ONLINE-cluster
label dict `{midx: int}`, the reader's per-sentence tokens (`sents`), and the name gazetteer, it (a) builds a crosstype
`Doc` from the reader's OWN live parse (attachment-arm heads + category-organ UPOS + BOTH arms of the labels rung --
reused via the reader's per-read cache, else reparsed by the same hdlab frontend), (b) runs `crosstype_bridge_links` (the
deployable cue_conf config, conf_thr swept), and (c) MERGES each bound role mention into its bound NAME's online label.
Returns a NEW merged label dict; `role_mentions` and the input labels are never mutated.

GOLD-FREE ROUTING (the whole point of the de-leak): each Doc mention's `.eid` is set to the mention's ONLINE cluster
label (names grouped by the aliaser inside online_cluster -- gold-free), NEVER the gold `m["cluster"]`/`_gold_eid`. So
`crosstype_bridge_links` returns `{role_midx: name_ONLINE_label}` and the merge is trivially
`merged[role_midx] = name_online_label` -- a promoted, gold-free variant of the harness's `_merge`
(experiments/exp_crosstype_live_wire_gum_v1._merge), which keyed the name by `_gold_eid` FOR SCORING ONLY. NO gold column
is read in ANY clustering/bridge decision (`gated_binds(restrict_gold=False)` reads `m.eid` only for grouping and for the
DISCARDED `correct` counter -- with `.eid` = the online label this is fully gold-free; `crosstype_bridge_links` returns
only the binds). NAME files and the pronoun coref column are untouched (the bridge/online touch only non-pronoun midx).

WIRE NOTE (situation_reader.read, online_entity_cluster block): the merged label of a bridged common is a NAME's online
int label, so the downstream negative-int scheme `-(int(label)+1)` stays an INT (downstream `rc >= 0` consumers crash on a
str). The bridge only ever REASSIGNS a common's online label to a NAME's online label -- both are ints.

SELF-CONTAINED: imports ONLY hdlab (crosstype_bridge, coref, frontend, graded_role_assigner, attachment_arm). ZERO
experiments/ imports (the self-containment invariant). NO external LLM at inference, and since pri 134 no supervised
stand-in on ANY path through this module (the standalone frontend used to load pos_tagger + arceager + arc_labeler).

Do NOT wire the part-whole type route at the identity entity layer (located negative: meronymy is BRIDGING, not
identity -- online_cluster keeps type_route="exact"); this adapter only adds the cross-type NAME bind the online layer
cannot express.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-09 de-leak landing (strategy first-hand)"
__bf_note__ = "adapter/plumbing (not a standalone brain mechanism): builds a crosstype Doc from the reader's OWN live parse with mention .eid = the ONLINE cluster label (NEVER gold), runs crosstype_bridge, merges; inherits crosstype_bridge's BF_SPIRIT"
__bf_corrections__ = []

import os

from hdlab.coref import name_content_tokens
from hdlab.crosstype_bridge import crosstype_bridge_links

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# reader gender space ("masc"/"fem"/"neuter"/"any"/None) -> the crosstype Doc's GUM code space ("m"/"f"/"n"/"")
# the bridge tests `m.gender in {"m","f"}` (person cue) and sets name_gender from "m"/"f".
_G2CODE = {"masc": "m", "fem": "f", "neuter": "n"}

# pri 134 (2026-09-16) -- THE NON-ARGUMENT ARM IS ON.  pri 129 routed this adapter to the ONE role competition, which
# labels ARGUMENT relations only, so every non-argument token read `dep` and the four name-linking cues this bridge is
# built on (`appos` "Elizabeth, the doctor", `flat`/`compound` "Mary Smith", `nmod:poss` "her brother") plus the copular
# `cop` path could not fire at all.  `graded_role_assigner.all_relations` restores them from the SAME organ, with count
# validities and an observe path.  Flipped ON per the no-default-off rule, and inert (byte-identical to pri 129) when the
# validity asset is absent.  FINE_CONSTRUCTION_HEADS: the construction also names its own governor -- measured on GUM,
# that is what makes the name link survive an attachment error (UD-EWT test governor accuracy on the five constructions
# 0.6145 -> 0.6660; the bridge name-link recall reaches the GOLD-deprel ceiling with it).
# AND THE SECOND, LARGER LOSS ON THE SAME CHAIN, REPAIRED IN `_can_build` / `_mention_gtok` BELOW: this adapter
# demanded a GLOBAL token index on every non-pronoun mention, and the reader's DEFAULT mention source
# (`referent_per_np`, :104 / :192) sets `gtok_start = gtok_end = -1` BY CONSTRUCTION -- so `merge_crosstype_bridge`
# returned its input unchanged on EVERY live read and `precise_constructs` was never entered at all (measured on a
# GUM document through the real reader: 1 call, `_can_build` False, 292 of 292 non-pronoun mentions out of range,
# 0 predication edges). The mention was always locatable -- sent_idx + wtok_start + span_toks put it in the SAME
# `sents` the Doc is built from. THIS IS A LIVE BEHAVIOUR FLIP: the bridge starts firing where it never has, so the
# reader-driven board must be run at integration (HDLAB_FINE_RELATIONS=0 reverts only the relations arm; the
# coverage repair is in `_can_build` and is the thing to revert if the board moves the wrong way).
FINE_RELATIONS = os.environ.get("HDLAB_FINE_RELATIONS", "1") == "1"
FINE_CONSTRUCTION_HEADS = os.environ.get("HDLAB_FINE_CONSTRUCTION_HEADS", "1") == "1"


class _Tok:
    __slots__ = ("gidx", "sent", "idx", "head", "deprel", "upos", "xpos", "form", "lemma")


class _Ment:
    __slots__ = ("eid", "mtype", "start_g", "end_g", "head_g", "gender", "text", "lemma_head")


class _Doc:
    __slots__ = ("toks", "mentions")


# ------------------------------------------------------------------ frontend (standalone fallback; else reader cache)
_FRONTEND = {}


def _standalone_frontend():
    """Lazily load the SAME hdlab frontend the reader uses -- `hdlab.frontend` (the ONE switchboard: the count-based
    category organ + the attachment arm).  Used only when no `reader` is passed; with a reader we reuse its per-read
    parse cache so the Doc parse is byte-identical to the reader own parse of those sentences.

    pri 134 (2026-09-16): this path used to load `pos_tagger` + `arceager_parser` + the RETIRED `arc_labeler`, so the
    one entry point that did not come through the reader still ran two supervised stand-ins and the NOT_BF relation
    labeler pri 129 removed from the live read.  It now runs the same brain-foundational organs the reader does."""
    if not _FRONTEND:
        from hdlab.frontend import Tagger, Parser
        _FRONTEND["tag"] = Tagger()
        _FRONTEND["parse"] = Parser()
    return _FRONTEND


def _fine_sites(forms, pos, reader):
    """The graded PREDICATE-SLOT read for this sentence (pri 110/117) -- the cue the apposition (a reduced
    predication) and the copula are recognised by.  Silent ({}) under a category inventory that cannot
    provide it, exactly as `predicate_sites` is specified to be."""
    try:
        from hdlab.attachment_arm import predicate_sites
        from hdlab import lexical_categories as _LC
        mat = reader._cached_tag_matrix(list(forms)) if reader is not None else _LC.get().posterior(list(forms))
        if mat is None:
            return {}
        return predicate_sites(list(forms), list(pos), mat, _LC.get().tags)
    except Exception:
        return {}


def _parse_sentence(forms, reader):
    """(upos, heads, deprels) for one sentence. heads = 1-based child->head (0=root); deprels = {1-based idx: deprel}.
    reader!=None -> the reader's OWN per-read cache (byte-identical to its live parse); else the SAME frontend
    organs loaded standalone.  EVERY rung here is brain-foundational since pri 134: categories from the count-based
    category organ, heads from the attachment arm, and the relations from the ONE labels rung -- its ARGUMENT arm
    (`coarse_roles`, the Competition-Model role competition) plus its NON-ARGUMENT arm (`all_relations`: the name-run
    chunk, the reduced predication, the genitive case marker and the copula's tense-carrying), which is what restores
    this bridge's `appos` / `flat` / `compound` / `nmod:poss` / `cop` name-linking cues after pri 129 retired the
    supervised relation labeler.  With no fine-validity asset on disk the non-argument arm abstains and this is
    byte-identical to the pri-129 behaviour."""
    from hdlab.graded_role_assigner import all_relations as _all_relations, coarse_roles as _coarse_roles
    if reader is not None:
        pos = reader._cached_tag(list(forms))
        heads = reader._cached_parse_heads(list(forms), pos)
    else:
        f = _standalone_frontend()
        pos, dist = f["tag"].tag_with_posterior(list(forms))
        po = f["parse"].parse(list(forms), list(pos), dist)
        heads = dict(po.heads)
    coarse = dict(_coarse_roles(list(forms), list(pos), dict(heads)))
    if not FINE_RELATIONS:
        return pos, heads, coarse
    fr = _all_relations(list(forms), list(pos), dict(heads), sites=_fine_sites(forms, pos, reader),
                        coarse=coarse, with_heads=FINE_CONSTRUCTION_HEADS)
    if not fr:
        return pos, heads, coarse                     # no asset -> the argument arm alone (pri-129 behaviour)
    if FINE_CONSTRUCTION_HEADS:
        # THE CONSTRUCTION NAMES ITS OWN GOVERNOR (pri 134).  A construction is a form/GOVERNOR pairing, so a
        # name run's `flat` points at the run's first token and a copula's `cop` at the token it carries tense
        # for, even where the attachment arm put the arc elsewhere -- that is what makes the bridge's name link
        # survive an attachment error.  This rewrites ONLY the Doc this adapter hands the bridge; the reader's
        # own parse cache is untouched.
        heads = dict(heads)
        heads.update({i: int(v[1]) for i, v in fr.items()})
        fr = {i: v[0] for i, v in fr.items()}
    return pos, heads, dict(fr)


def _build_toks(sents, reader):
    """Build the crosstype Doc `.toks` from the reader's per-sentence tokens (`parse_conll_sentences`, RAW-CASED
    since pri-116 -- the SAME tokens the reader tags/parses). Global gidx increments per token across sentences, matching
    parse_litbank_conll's gtok scheme (identical token filter) -> mention gtok_start/gtok_end/head_g line up."""
    toks = []
    gidx = 0
    for sent_i, forms in enumerate(sents):
        forms = list(forms)
        if not forms:
            continue
        pos, heads, deprels = _parse_sentence(forms, reader)
        for p, form in enumerate(forms):
            t = _Tok()
            t.gidx = gidx
            t.sent = sent_i
            t.idx = p + 1                                    # 1-based within-sentence (heads/deprels are 1-based)
            t.form = form
            t.lemma = None                                   # bridge does head_lemma(lemma or form) -> lemmatizes form
            t.upos = pos[p] if p < len(pos) else "X"
            t.head = int(heads.get(p + 1, 0))                # 1-based child->head, 0=root
            t.deprel = deprels.get(p + 1, "dep")
            t.xpos = ""                                      # UPOS-only frontend; xpos is used ONLY by cue_novelty (not cue_conf)
            toks.append(t)
            gidx += 1
    return toks


def _build_mention(m, eid, span_g=None):
    """One gold-free crosstype Doc mention from a reader role-mention dict. eid = the ONLINE cluster label (int) for a
    non-pronoun with a label, else a unique per-mention sentinel (pronoun / unlabelled -- never a name bind target).
    mtype is derived GOLD-FREE from name_content_tokens (capitalization) -- the same name signal online_cluster uses;
    head_g = gtok_end (the reader's own last-token head convention, == m["head"]); lemma_head = the surface head."""
    span = m.get("span_toks", [m["head"]])
    men = _Ment()
    men.eid = eid
    if m.get("is_pronoun"):
        men.mtype = "pronoun"
    else:
        men.mtype = "name" if name_content_tokens(span, upos=m.get("span_upos")) else "common"
    men.start_g = span_g[0] if span_g else m.get("gtok_start")
    men.end_g = span_g[1] if span_g else m.get("gtok_end")
    men.head_g = m.get("head_g", men.end_g)                  # reader head = span_toks[-1] -> last global token
    g = m.get("gender") or m.get("name_gender")
    men.gender = _G2CODE.get(g, "")
    men.text = " ".join(span)
    men.lemma_head = m["head"]
    return men


def _global_offsets(sents):
    """(per-sentence global start offset, total token count) for the reader's own sentence list."""
    offs = []
    n = 0
    for s in sents:
        offs.append(n)
        n += len(s)
    return offs, n


def _mention_gtok(m, offs, ntok):
    """THE GLOBAL SPAN OF ONE MENTION, recovered rather than required (pri 134, 2026-09-16).

    The adapter used to demand `gtok_start` / `gtok_end` and abstain on the whole document when any mention
    lacked them -- and the reader's DEFAULT mention source (`referent_per_np`, :104 / :192) sets them to -1 BY
    CONSTRUCTION, so `merge_crosstype_bridge` returned its input unchanged on EVERY live read and the bridge's
    predication detector was never entered (measured: 292 of 292 non-pronoun mentions out of range, 0 edges).
    The information was never missing -- `sent_idx` + `wtok_start` (0-based inside the sentence) + `span_toks`
    locate the mention exactly in the SAME `sents` the Doc is built from.  Returns (start_g, end_g) or None."""
    s, e = m.get("gtok_start"), m.get("gtok_end")
    if s is not None and e is not None and 0 <= s <= e < ntok:
        return int(s), int(e)
    si, w = m.get("sent_idx"), m.get("wtok_start")
    if si is None or w is None or not (0 <= int(si) < len(offs)):
        return None
    g = offs[int(si)] + int(w)
    if not (0 <= g < ntok):
        return None
    span = m.get("span_toks") or []
    return g, min(ntok - 1, g + max(0, len(span) - 1))


def _can_build(role_mentions, sents):
    """The Doc needs a locatable global span for every NON-pronoun mention. Since pri 134 the span is RECOVERED
    from sent_idx + wtok_start when the mention does not carry one (see `_mention_gtok`), so the reader's own
    default mention source no longer silences the whole bridge; a mention that still cannot be located at all
    abstains the document, exactly as before."""
    if not sents or not role_mentions:
        return False
    offs, ntok = _global_offsets(sents)
    for m in role_mentions:
        if m.get("is_pronoun"):
            continue
        if _mention_gtok(m, offs, ntok) is None:
            return False
    return True


def build_gold_free_doc(role_mentions, online_labels, sents, *, reader=None):
    """Build the crosstype `Doc` (.toks + .mentions) from the reader's live state, GOLD-FREE (mention.eid = the ONLINE
    label). `.mentions` is enumerated in the SAME order as `role_mentions` (position i <-> role_mentions[i]) so
    crosstype_bridge_links' returned midx == position i. Returns None if a Doc cannot be built from the live state."""
    if not _can_build(role_mentions, sents):
        return None
    doc = _Doc()
    doc.toks = _build_toks(sents, reader)
    offs, ntok = _global_offsets(sents)
    mentions = []
    _pron = 0
    for m in role_mentions:
        if m.get("is_pronoun"):
            eid = ("__pron__", _pron); _pron += 1            # unique sentinel: never a name bind target
        else:
            lab = online_labels.get(m["midx"])
            eid = lab if lab is not None else ("__nolabel__", m["midx"])
        mentions.append(_build_mention(m, eid, _mention_gtok(m, offs, ntok)))
    doc.mentions = mentions
    return doc


def apply_binds(role_mentions, online_labels, binds):
    """Merge `binds` ({position_i: name_online_label} from crosstype_bridge_links over the gold-free Doc) into a NEW
    label dict: each bound role mention takes its bound NAME's ONLINE label (files under the named record). GOLD-FREE
    (the bind values ARE online labels -- no _gold_eid translation). Non-mutating."""
    merged = dict(online_labels)
    for i, name_label in binds.items():
        if 0 <= i < len(role_mentions):
            merged[role_mentions[i]["midx"]] = name_label
    return merged


def merge_crosstype_bridge(role_mentions, online_labels, gaz, sents, *, reader=None, conf_thr=-3.0):
    """THE live entry (situation_reader.read online_entity_cluster block, PART 2). Build the gold-free Doc from the
    reader's own parse, run the deployable cue_conf crosstype bridge at `conf_thr`, and return a NEW online-label dict
    with each bound definite role mention re-filed under its bound NAME's online label. Byte-safe: if no Doc can be
    built from the live state, returns online_labels unchanged (abstain -- the honest online layer, no bridge)."""
    doc = build_gold_free_doc(role_mentions, online_labels, sents, reader=reader)
    if doc is None:
        return dict(online_labels)
    # Q111 consolidation (2026-09-11): the definite->name bridge folds into the ONE hdlab.entity_resolver
    # (== crosstype_bridge_links byte-identical, verification/test_entity_resolver_unified.py W3). The module-level
    # `crosstype_bridge_links` import above is retained as provenance + the substitution witness's patch target.
    from hdlab.entity_resolver import EntityResolver
    binds = EntityResolver().bridge_links(doc, gaz, conf_thr=conf_thr)
    return apply_binds(role_mentions, online_labels, binds)


def _selftest() -> int:
    """Corpus-free structural self-test: 'Elizabeth is a doctor . The doctor arrived .' -- online labels file the two
    'doctor' commons under one file (1) and Elizabeth under another (0). Tests the DETERMINISTIC pieces: the merge
    logic (apply_binds), non-mutation, int labels, and the GOLD-FREE Doc construction (mention.eid == the ONLINE labels,
    NOT the gold cluster) -- none of which depend on the real parser. A tolerant end-to-end smoke exercises the full
    merge_crosstype_bridge over the live frontend. The full CI-separated experiencer lift is proven on GUM by
    verification/test_deleak_crosstype_live_adapter.py + the SOLVED's downstream harness."""
    def rm(midx, head, span, gs, ge, sent, gender, pron=False, rank=0, cluster=999):
        return {"midx": midx, "head": head, "span_toks": span, "gtok_start": gs, "gtok_end": ge,
                "sent_idx": sent, "is_pronoun": pron, "gender": gender, "name_gender": None,
                "number": "singular", "sent_role_rank": rank, "cluster": cluster}
    role_mentions = [
        rm(0, "elizabeth", ["Elizabeth"], 0, 0, 0, None, rank=0, cluster=1),
        rm(1, "doctor", ["a", "doctor"], 2, 3, 0, None, rank=1, cluster=1),
        rm(2, "doctor", ["The", "doctor"], 4, 5, 1, None, rank=0, cluster=1),
    ]
    sents = [["elizabeth", "is", "a", "doctor", "."], ["the", "doctor", "arrived", "."]]
    online = {0: 0, 1: 1, 2: 1}   # Elizabeth -> file 0 ; both 'doctor' commons -> file 1 (online_cluster exact-head)
    fails = []
    # W1 MERGE LOGIC (deterministic): a bind {position 2 -> name online label 0} re-files midx2 under label 0.
    merged = apply_binds(role_mentions, online, {2: 0})
    ok1 = merged.get(2) == 0 and merged.get(0) == 0 and merged.get(1) == 1
    print("  %s W1 apply_binds re-files the bound common under the name's online label: %s"
          % ("PASS" if ok1 else "FAIL", merged))
    if not ok1:
        fails.append("W1")
    # W2 NON-MUTATING: the input label dict is unchanged.
    ok2 = online == {0: 0, 1: 1, 2: 1} and merged is not online
    print("  %s W2 apply_binds is non-mutating (input online preserved)" % ("PASS" if ok2 else "FAIL"))
    if not ok2:
        fails.append("W2")
    # W3 INT LABELS: merged values stay ints (the -(int+1) wire stays safe).
    ok3 = all(isinstance(v, int) for v in merged.values())
    print("  %s W3 merged labels are ints (%s)" % ("PASS" if ok3 else "FAIL", sorted(set(merged.values()))))
    if not ok3:
        fails.append("W3")
    # W4 GOLD-FREE Doc: mention eids == the ONLINE labels, NOT the gold cluster (1/999); mtypes derived gold-free.
    doc = build_gold_free_doc(role_mentions, online, sents)
    eids = [men.eid for men in doc.mentions]
    mtypes = [men.mtype for men in doc.mentions]
    ok4 = eids == [0, 1, 1] and mtypes == ["name", "common", "common"]
    print("  %s W4 gold-free Doc: eids==online labels %s ; mtypes (name_content_tokens) %s"
          % ("PASS" if ok4 else "FAIL", eids, mtypes))
    if not ok4:
        fails.append("W4")
    # W5 END-TO-END SMOKE (tolerant of real-parser quality): merge_crosstype_bridge runs, returns int labels, and
    # only ever moves midx2 to 0 (bridged) or leaves it 1 (abstain) -- never a gold value or a crash.
    try:
        e2e = merge_crosstype_bridge(role_mentions, online, {"elizabeth": "fem"}, sents, conf_thr=0.0)
        ok5 = all(isinstance(v, int) for v in e2e.values()) and e2e.get(2) in (0, 1) and e2e.get(0) == 0
    except Exception as ex:
        e2e = repr(ex); ok5 = False
    print("  %s W5 end-to-end merge_crosstype_bridge over the live frontend: %s" % ("PASS" if ok5 else "FAIL", e2e))
    if not ok5:
        fails.append("W5")
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
