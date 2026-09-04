"""THE referent->coref LINKING PASS for wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on.

DIAGNOSIS (exp_referent_coref_linking_diagnosis_v1): turning `referent_per_np` ON collapses coref_acc
0.60 -> 0.04 because referent_per_np_source opens a discourse referent for EVERY content-noun NP but
leaves the file-card's CONCEPTUAL FEATURES BLANK -- it lowercases the head (so a real name fails
name_content_tokens -> is_named=False), sets gender=None, and never types animacy. So (a) the hard
agreement filter compatible() -- which excludes a candidate only on a KNOWN conflict -- lets every
gender-None inanimate noun ("table","letter","door") be a candidate for "he"/"she", (b) the
GenericDistractorFilter's "keep any NAMED or gender-cued specific character" guard misfires, and (c)
name aliasing cannot fire. The pool floods and the pronoun binds a NON-co-referent (514/539 of the
wrong targets resolve the WRONG entity -- derailment, not a scoring artifact).

THE BRAIN (PINNED). A discourse referent (Kamp 1981 DRT / Heim 1982 FCS) is a FILE CARD that carries
the entity's features; anaphora is CONTENT-ADDRESSABLE cue-based retrieval (Lewis & Vasishth 2005
ACT-R) where "he" cues [+masculine, +singular, +ANIMATE/person] -- an inanimate "table" is not
retrievable by "he" because the ANIMACY cue mismatches (Garnham 2001; the animacy constraint on
pronoun interpretation). So the missing "linking pass" is ENTITY TYPING + agreement/animacy-gated
retrieval + merging co-referring cards (Centering Cf salience; Grosz-Joshi-Weinstein 1995).

THIS CELL restores the file-card features the source discarded (gender via infer_nominal_gender +
the name gazetteer; animacy via the glass-box animacy lexicon; raw casing so is_named/aliasing work),
adds the brain's ANIMACY GATE to the pronoun-antecedent pool (a strict narrowing -- never empties the
pool, exactly _agreement_preferred's expects_animate tier), and OPTIONALLY merges co-referring
referents (Heim familiarity: same canonical entity -> shared cluster, inheriting the coref cluster).
NO external LLM. Glass-box. who-did-what is untouched (it reads positional nominal heads, not features).

Run: .venv/Scripts/python.exe experiments/exp_referent_coref_linking_v1.py
"""
import json
import math
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SUP_KW, LOCAL_WINDOW, _FRONTEND_POS_ASSET
from hdlab.coref import (parse_litbank_conll, build_pronoun_targets, name_gender_for_span,
                         name_content_tokens, build_merge_map)
from hdlab.scene_segment import parse_conll_sentences
from hdlab.state_of_mind import infer_nominal_gender, WorkingOverlay
from hdlab.animacy_lexicon import lookup_animacy
from hdlab.event_centrality_coref import EventCentralityReader
from hdlab.referent_per_np import (referent_per_np_source, _content_head_positions,
                                    frame_heads, _mk_referent, _finalize)
import experiments.exp_name_entity_clustering_v1 as NC
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer

SEED = 20260903


# ---------------------------------------------------------------------------
# The animacy-gated retrieval overlay + reader (the brain's ANIMACY cue on the pool).
# ---------------------------------------------------------------------------
class AnimacyGatedOverlay(WorkingOverlay):
    """WorkingOverlay whose antecedent pool for a GENDERED pronoun (he/she) is narrowed to ANIMATE
    entities when any exist -- the brain's animacy cue on cue-based retrieval (Garnham 2001). Strict:
    if no animate candidate exists the tier is a no-op, so a purely inanimate/unknown pool falls back
    to the validated behavior (never-confidently-empty). animacy_of maps lowercased head -> animacy."""
    animacy_of = {}
    established_pref = False

    def _compatible_entities(self, gender, number):
        base = super()._compatible_entities(gender, number)
        if gender in ("masc", "fem") and self.animacy_of:
            animate = [e for e in base if self.animacy_of.get(e.head) == "animate"]
            if animate:
                base = animate
            if self.established_pref:
                # Centering Cf: prefer an ESTABLISHED discourse entity (re-mentioned or named) over a
                # brand-new one-off; strict (no-op if none established, so a just-introduced antecedent
                # "A man came in. He..." still resolves).
                est = [e for e in base if e.count >= 2 or e.is_named]
                if est:
                    base = est
        return base


class GatedECReader(EventCentralityReader):
    """EventCentralityReader with the animacy gate injected via the overlay (no resolve_stream copy).
    Set _pending_animacy (head->animacy) + _gate before each resolve_stream call."""
    _pending_animacy = {}
    _gate = True
    _established = False

    def _new_overlay(self):
        if not self._gate:
            return super()._new_overlay()
        ov = AnimacyGatedOverlay(base=self._base, beta=self._beta, lam=self._lam,
                                 window_k=self._window_k)
        ov.animacy_of = self._pending_animacy
        ov.established_pref = self._established
        return ov


# ---------------------------------------------------------------------------
# THE LINKED SOURCE: referent-per-NP + restored file-card features (+ optional merge).
# ---------------------------------------------------------------------------
def _animacy_of_head(raw, upos):
    a = lookup_animacy(raw, pos_tag=upos)
    return (a["animacy"], a["category"]) if a else (None, None)


def build_linked(conll_path, tagger, gaz, *, enrich=True, merge=False, use_frame=True, entity_key=False):
    """referent-per-NP mentions with the discourse-referent FEATURES restored (enrich) and optionally
    co-referring referents merged into shared clusters (merge). enrich=False, merge=False == the landed
    referent_per_np_source byte-for-byte."""
    if not enrich and not merge:
        return referent_per_np_source(conll_path, tagger, name_gender_map=gaz, use_frame=use_frame)

    coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=gaz)
    sents = parse_conll_sentences(conll_path)
    coref_head_wpos = {}
    pron = [m for m in coref if m["is_pronoun"]]
    for m in coref:
        if m["is_pronoun"]:
            continue
        span = max(0, m["gtok_end"] - m["gtok_start"])
        coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    next_cluster = max([m["cluster"] for m in coref], default=-1) + 1

    out = []
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        base = _content_head_positions(toks, up)
        heads = sorted(set(base) | frame_heads(toks, up, set(base))) if use_frame else base
        for hw in heads:
            raw = toks[hw]
            low = raw.lower()
            cl = coref_head_wpos.get((si, hw))
            fresh = cl is None
            if fresh:
                cl = next_cluster
                next_cluster += 1
            m = _mk_referent(low, si, hw, cl, -1)
            # RESTORE the discourse-referent file-card features the source discarded:
            m["span_toks"] = [raw]                                   # raw-cased -> is_named/aliasing work
            g = infer_nominal_gender([raw])                          # cue-based gender
            ng = name_gender_for_span([raw], gaz) if g is None else None
            m["gender"] = g
            m["name_gender"] = ng
            anim, cat = _animacy_of_head(raw, up[hw])
            # PERSON-HOOD for the animacy retrieval cue: a KNOWN gender (a gendered name via the
            # gazetteer, or a gendered common noun woman/king) implies an ANIMATE person -- the
            # animacy lexicon returns None for PROPN, so gender is the reliable person signal here.
            person_like = (g in ("masc", "fem") or ng in ("masc", "fem")
                           or anim == "animate" or cat == "person")
            m["animacy"] = "animate" if person_like else anim
            m["category"] = cat
            m["_fresh"] = fresh
            out.append(m)

    mentions = _finalize(pron + out)
    if merge:
        mentions = _link_merge(mentions, gaz)
    if entity_key:
        # unify the OVERLAY entity by the (linked) cluster so a protagonist fragmented across
        # single-token name variants (Elizabeth / Bennet / Darcy) accumulates salience on ONE entity
        # -- the brief's "merge co-referring referents into shared clusters" at the resolution level.
        for m in mentions:
            if not m["is_pronoun"]:
                m["head"] = "e%d" % m["cluster"]
    return mentions, n_sents


def _link_merge(mentions, gaz):
    """HEIM-FAMILIARITY LINKING: merge co-referring referents into ONE discourse entity so salience
    ACCUMULATES on the unified referent (Centering Cf) and head_to_cluster is consistent. Two
    glass-box rules:
      (1) PROPER-NAME variant aliasing (Elizabeth / Miss Bennet / Bennet) -> build_merge_map. The
          merged mentions are RE-KEYED to a shared canonical HEAD so the resolver's overlay (which
          groups entities by surface head) accumulates their salience on ONE entity instead of
          fragmenting it across variants -- the missing piece: a minor character was out-saliencing a
          protagonist split across name forms.
      (2) same-surface-head re-mention -> already ONE overlay entity; we only harmonize its cluster id.
    Each merged group ADOPTS the smallest coref-covered (non-fresh) cluster id present, else its own
    min id -- so a fresh singleton that co-refers with a gold-covered referent INHERITS the gold
    linkage (preserving the pronoun's cross-reference), never the reverse."""
    midx_to_canon, _c2m, _ = build_merge_map(mentions, use_gazetteer=True)
    groups = {}
    for m in mentions:
        if m["is_pronoun"]:
            continue
        key = midx_to_canon.get(m["midx"]) or ("head::" + m["head"])
        groups.setdefault(key, []).append(m)
    for key, ms in groups.items():
        nonfresh = [mm["cluster"] for mm in ms if not mm.get("_fresh", False)]
        canon_cl = min(nonfresh) if nonfresh else min(mm["cluster"] for mm in ms)
        # a name-aliased group (a real cross-variant merge) shares ONE overlay head so salience
        # accumulates; a bare same-head group keeps its head (it is already one overlay entity).
        rekey = key.startswith("~") and len(ms) >= 1
        canon_head = "~e:" + key if rekey else None
        for mm in ms:
            mm["cluster"] = canon_cl
            if canon_head is not None:
                mm["head"] = canon_head
    return mentions


# ---------------------------------------------------------------------------
# Resolve + score (mirrors the reader's _read_entities call exactly).
# ---------------------------------------------------------------------------
def _resolve(reader, mentions, n_sents, *, gate, qmem=True):
    targets = build_pronoun_targets(mentions)
    if not targets:
        return []
    reader._gate = gate
    reader._pending_animacy = {m["head"].lower(): m.get("animacy")
                               for m in mentions if not m["is_pronoun"]}
    sid = [i // LOCAL_WINDOW for i in range(n_sents)]
    return reader.reader_resolve(mentions, targets, sid, qmem)


class _R(GatedECReader):
    def reader_resolve(self, mentions, targets, sid, qmem=True):
        return self.resolve_stream(mentions, targets, scene_ids=sid, topical_mode="rolemass",
                                   query_memory=qmem, centrality_mode="event_role", **SUP_KW)


def _docs(n):
    wdw = json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    out = []
    for r in wdw:
        p = os.path.join(NC.CONLL_DIR, r["doc"] + ".conll")
        if os.path.exists(p):
            out.append((r["doc"], p))
        if len(out) >= n:
            break
    return out


def _acc(recs):
    n = len(recs)
    return (sum(r["correct"] for r in recs) / n) if n else float("nan")


def run(n_docs=8):
    from hdlab.pos_tagger import PosTagger
    gaz = load_given_gazetteer()
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    reader = _R(n_dim=4096, mem_seed=7)
    docs = _docs(n_docs)

    arms = {
        "OFF coref-column (floor)": [],
        "ON rnp raw (regression)": [],
        "ON +features (no gate)": [],
        "ON +features +animacy-gate": [],
        "ON +features +merge (no gate)": [],
        "ON +features +merge +gate (LINKER)": [],
    }
    for doc, p in docs:
        # OFF floor
        mo, ns = parse_litbank_conll(p, name_gender_map=gaz)
        arms["OFF coref-column (floor)"] += _resolve(reader, mo, ns, gate=False)
        # ON raw (current regression)
        mr, ns = build_linked(p, tagger, gaz, enrich=False, merge=False)
        arms["ON rnp raw (regression)"] += _resolve(reader, mr, ns, gate=False)
        # ON + features, no gate
        mf, ns = build_linked(p, tagger, gaz, enrich=True, merge=False)
        arms["ON +features (no gate)"] += _resolve(reader, mf, ns, gate=False)
        # ON + features + animacy gate
        arms["ON +features +animacy-gate"] += _resolve(reader, mf, ns, gate=True)
        # ON + features + merge (isolate merge, no gate)
        mm, ns = build_linked(p, tagger, gaz, enrich=True, merge=True)
        arms["ON +features +merge (no gate)"] += _resolve(reader, mm, ns, gate=False)
        # ON + features + merge + gate  (the full linker)
        arms["ON +features +merge +gate (LINKER)"] += _resolve(reader, mm, ns, gate=True)
        # ON + features + merge + gate + ENTITY-KEY (unify overlay by linked cluster)
        me, ns = build_linked(p, tagger, gaz, enrich=True, merge=True, entity_key=True)
        arms.setdefault("ON +LINKER +entity-key", [])
        arms["ON +LINKER +entity-key"] += _resolve(reader, me, ns, gate=True)
        # ON + LINKER + entity-key + established-preference (Centering Cf)
        reader._established = True
        arms.setdefault("ON +LINKER +entity-key +estab", [])
        arms["ON +LINKER +entity-key +estab"] += _resolve(reader, me, ns, gate=True)
        # ... + event-centrality memory OFF (tuned on the sparse coref stream -> may misfire on rnp)
        arms.setdefault("ON +LINKER +estab, mem OFF", [])
        arms["ON +LINKER +estab, mem OFF"] += _resolve(reader, me, ns, gate=True, qmem=False)
        reader._established = False
        # REFERENCE ceiling: OFF coref-column WITH entity-key (fair upper bound of the same lever)
        moe, ns = parse_litbank_conll(p, name_gender_map=gaz)
        for m in moe:
            if not m["is_pronoun"]:
                m["head"] = "e%d" % m["cluster"]
        arms.setdefault("OFF +entity-key (ref ceiling)", [])
        arms["OFF +entity-key (ref ceiling)"] += _resolve(reader, moe, ns, gate=False)

    print("=" * 78)
    print("REFERENT->COREF LINKING PASS  (pooled over %d docs)" % len(docs))
    print("-" * 78)
    for name, recs in arms.items():
        print("  %-38s coref_acc = %.4f   (n=%d)" % (name, _acc(recs), len(recs)))
    print("=" * 78)
    return {k: _acc(v) for k, v in arms.items()}


def _gold_head_clusters(conll_path, gaz):
    mentions, _ = parse_litbank_conll(conll_path, name_gender_map=gaz)
    hc = {}
    for m in mentions:
        hc.setdefault(m["head"].lower(), set()).add(m["cluster"])
    return hc


def diagnose_linker(n_docs=8):
    """Categorize the LINKER arm's remaining FAILURES so the next lever is chosen from evidence:
      abstain / inanimate distractor / wrong-gender / wrong-PERSON (real ambiguity) / pollution."""
    from hdlab.pos_tagger import PosTagger
    gaz = load_given_gazetteer()
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    reader = _R(n_dim=4096, mem_seed=7)
    docs = _docs(n_docs)
    from hdlab.coref import PRONOUN_SCOPE
    cats = {"correct": 0, "abstain": 0, "inanimate_distractor": 0, "wrong_gender": 0,
            "wrong_person": 0, "pollution": 0}
    pool_sizes = []
    for doc, p in docs:
        mm, ns = build_linked(p, tagger, gaz, enrich=True, merge=True, entity_key=True)
        anim_of = {m["head"].lower(): m.get("animacy") for m in mm if not m["is_pronoun"]}
        gen_of = {m["head"].lower(): (m.get("gender") or m.get("name_gender")) for m in mm if not m["is_pronoun"]}
        recs = _resolve(reader, mm, ns, gate=True)
        for r in recs:
            if r["correct"]:
                cats["correct"] += 1
                continue
            rh = (r.get("resolved_head") or "").lower()
            pron = r.get("pronoun") or ""
            tg = PRONOUN_SCOPE.get(pron, {}).get("gender")
            if not rh:
                cats["abstain"] += 1
            elif anim_of.get(rh) != "animate":
                cats["inanimate_distractor"] += 1
            elif gen_of.get(rh) in ("masc", "fem") and tg in ("masc", "fem") and gen_of.get(rh) != tg:
                cats["wrong_gender"] += 1
            else:
                cats["wrong_person"] += 1        # entity-keyed: resolved a DIFFERENT animate entity
            pool_sizes.append(r.get("n_pool", 0))
    tot = sum(cats.values())
    print("=" * 78)
    print("LINKER FAILURE DIAGNOSIS (%d targets over %d docs)" % (tot, len(docs)))
    for k, v in cats.items():
        print("  %-22s %4d  (%.3f)" % (k, v, v / max(1, tot)))
    if pool_sizes:
        print("  mean he/she pool size on FAILURES: %.1f" % (sum(pool_sizes) / len(pool_sizes)))
    print("=" * 78)
    return cats


def _enrich_existing(mentions, *, entity_key=True, animacy=True, shuffle=False, seed=SEED):
    """Apply the LINKING-PASS levers to an already-curated coref-mention set (the deployed coref
    column): add the animacy feature + unify the overlay entity by cluster. Isolates whether the
    linking levers improve coref ABOVE the deployed baseline (which lacks animacy gating + entity
    unification), independent of the referent-per-NP single-token span loss.

    shuffle=True -> the INFO-FREE TWIN: keep the SAME machinery/counts but scramble WHICH referents
    link (permute the entity-key cluster labels across nominals) and WHICH are animate (permute the
    animacy labels). If the +delta survives the twin, the machinery not the LINK carried it."""
    import random
    rng = random.Random(seed)
    noms = [m for m in mentions if not m["is_pronoun"]]
    key_src = [m["cluster"] for m in noms]
    anim_src = []
    for m in noms:
        g = m.get("gender") or m.get("name_gender")
        a = lookup_animacy(m["head"], pos_tag=None)
        anan = a["animacy"] if a else None
        anim_src.append("animate" if (g in ("masc", "fem") or anan == "animate"
                                       or (a and a["category"] == "person")) else anan)
    if shuffle:
        rng.shuffle(key_src)
        rng.shuffle(anim_src)
    out = []
    j = 0
    for m in mentions:
        m = dict(m)
        if not m["is_pronoun"]:
            if animacy:
                m["animacy"] = anim_src[j]
            if entity_key:
                m["head"] = "e%d" % key_src[j]
            j += 1
        out.append(m)
    return _finalize(out)


def _alias_rekey(mentions):
    """NON-GOLD entity unification: unify the overlay entity by NAME-VARIANT aliasing (build_merge_map:
    Elizabeth / Miss Bennet / Bennet -> one key) WITHOUT touching the gold cluster labels. Isolates
    whether the coref improvement is a legitimate (name-aliasing) linking win or an artifact of using
    the gold clusters as entity keys (entity-key). Adds the animacy feature the same way."""
    midx_to_canon, _c2m, _ = build_merge_map(mentions, use_gazetteer=True)
    out = []
    for m in mentions:
        m = dict(m)
        if not m["is_pronoun"]:
            g = m.get("gender") or m.get("name_gender")
            a = lookup_animacy(m["head"], pos_tag=None)
            anim = a["animacy"] if a else None
            m["animacy"] = "animate" if (g in ("masc", "fem") or anim == "animate"
                                         or (a and a["category"] == "person")) else anim
            canon = midx_to_canon.get(m["midx"])
            if canon is not None:
                m["head"] = "~a:" + canon
        out.append(m)
    return _finalize(out)


def _coref_view(mentions):
    """The pronoun-anaphora antecedent view: pronouns + ESTABLISHED (coref-covered, non-fresh)
    nominal referents only. Brain-faithful decoupling -- referent-per-NP's fresh one-off referents
    are who-did-what ROLE candidates but not tracked discourse entities a pronoun binds to (Centering
    Cf = the forward-looking-center list, not every fleeting NP). who-did-what still sees the FULL
    referent set; only the coref antecedent overlay is curated."""
    keep = [m for m in mentions if m["is_pronoun"] or not m.get("_fresh", False)]
    return _finalize(keep)


def _boot_delta(per_doc_a, per_doc_b, n_boot=1000, seed=SEED):
    """Doc-level cluster bootstrap on pooled_acc(a) - pooled_acc(b). per_doc_* = list of (correct,n)."""
    import random
    rng = random.Random(seed)
    k = len(per_doc_a)
    idx = list(range(k))

    def pooled(pd, sel):
        c = sum(pd[i][0] for i in sel)
        n = sum(pd[i][1] for i in sel)
        return (c / n) if n else 0.0
    base = pooled(per_doc_a, idx) - pooled(per_doc_b, idx)
    deltas = []
    for _ in range(n_boot):
        sel = [rng.randrange(k) for _ in range(k)]
        deltas.append(pooled(per_doc_a, sel) - pooled(per_doc_b, sel))
    deltas.sort()
    lo = deltas[int(0.025 * n_boot)]
    hi = deltas[int(0.975 * n_boot)]
    null = sorted(abs(d - base) for d in deltas)
    return {"delta": base, "lo": lo, "hi": hi, "hw": (hi - lo) / 2,
            "null_p95": null[int(0.95 * n_boot)], "ci_sep": (lo > 0 or hi < 0)}


def headline(n_docs=25, n_boot=1000, verbose=True):
    """The real headline: OFF (deployed baseline) vs ON-raw (regression) vs LINKER (full pass), pooled
    over N docs with a DOC-LEVEL bootstrap CI on the recovery delta."""
    from hdlab.pos_tagger import PosTagger
    gaz = load_given_gazetteer()
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    reader = _R(n_dim=4096, mem_seed=7)
    docs = _docs(n_docs)
    pd = {"OFF": [], "OFF_ek": [], "OFF_alias": [], "OFF_levers": [], "OFF_twin": [],
          "ON_raw": [], "LINKER": [], "DECOUPLE": []}
    for _doc, p in docs:
        mo, ns = parse_litbank_conll(p, name_gender_map=gaz)
        ro = _resolve(reader, mo, ns, gate=False)
        pd["OFF"].append((sum(r["correct"] for r in ro), len(ro)))
        # entity-key alone (unify overlay by discourse entity; no animacy gate/estab) -- biggest lever
        rek = _resolve(reader, _enrich_existing(mo, animacy=False), ns, gate=False)
        pd["OFF_ek"].append((sum(r["correct"] for r in rek), len(rek)))
        # NON-GOLD name-alias unification + animacy gate + estab (defensible, no cluster labels used)
        reader._established = True
        ral = _resolve(reader, _alias_rekey(mo), ns, gate=True)
        reader._established = False
        pd["OFF_alias"].append((sum(r["correct"] for r in ral), len(ral)))
        # OFF + linking levers (animacy + entity-key + estab) on the deployed coref column
        reader._established = True
        rol = _resolve(reader, _enrich_existing(mo), ns, gate=True)
        # INFO-FREE TWIN: same machinery, scrambled link + animacy labels
        rtw = _resolve(reader, _enrich_existing(mo, shuffle=True), ns, gate=True)
        reader._established = False
        pd["OFF_levers"].append((sum(r["correct"] for r in rol), len(rol)))
        pd["OFF_twin"].append((sum(r["correct"] for r in rtw), len(rtw)))
        mr, ns = build_linked(p, tagger, gaz, enrich=False, merge=False)
        rr = _resolve(reader, mr, ns, gate=False)
        pd["ON_raw"].append((sum(r["correct"] for r in rr), len(rr)))
        me, ns = build_linked(p, tagger, gaz, enrich=True, merge=True, entity_key=True)
        reader._established = True
        rl = _resolve(reader, me, ns, gate=True)
        reader._established = False
        pd["LINKER"].append((sum(r["correct"] for r in rl), len(rl)))
        # DECOUPLE: enriched + merged + entity-key, antecedent overlay curated to established entities
        mf, ns = build_linked(p, tagger, gaz, enrich=True, merge=True, entity_key=True)
        reader._established = True
        rv = _resolve(reader, _coref_view(mf), ns, gate=True)
        reader._established = False
        pd["DECOUPLE"].append((sum(r["correct"] for r in rv), len(rv)))

    def acc(pdl):
        c = sum(x[0] for x in pdl); n = sum(x[1] for x in pdl)
        return c / n, n
    accs = {k: acc(pd[k])[0] for k in pd}
    ns_ = {k: acc(pd[k])[1] for k in pd}
    pairs = (("OFF_ek", "OFF"), ("OFF_alias", "OFF"), ("OFF_levers", "OFF"),
             ("OFF_levers", "OFF_twin"), ("OFF_twin", "OFF"), ("DECOUPLE", "OFF"),
             ("DECOUPLE", "ON_raw"), ("LINKER", "OFF"), ("ON_raw", "OFF"))
    deltas = {"%s-%s" % (a, b): _boot_delta(pd[a], pd[b], n_boot) for a, b in pairs}
    if verbose:
        print("=" * 82)
        print("HEADLINE  coref_acc  (pooled, %d docs, doc-level bootstrap)" % len(docs))
        for k in ("OFF", "OFF_ek", "OFF_alias", "OFF_levers", "OFF_twin", "ON_raw", "LINKER", "DECOUPLE"):
            print("  %-11s %.4f   (n=%d)" % (k, accs[k], ns_[k]))
        print("-" * 82)
        for a, b in pairs:
            d = deltas["%s-%s" % (a, b)]
            print("  %-10s - %-10s : %+.4f  CI[%+.4f,%+.4f] hw=%.4f null_p95=%.4f  ci_sep=%s"
                  % (a, b, d["delta"], d["lo"], d["hi"], d["hw"], d["null_p95"], d["ci_sep"]))
        print("=" * 82)
    return {"accs": accs, "n": ns_, "deltas": deltas, "n_docs": len(docs)}


def probe(n_docs=8):
    """Quantify the POOL inflation (OFF vs LINKER) and ablate the frame detector, to localize the
    wrong-person residual: is it extra candidates, and are they frame-detector noise?"""
    from hdlab.pos_tagger import PosTagger
    gaz = load_given_gazetteer()
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    reader = _R(n_dim=4096, mem_seed=7)
    docs = _docs(n_docs)

    def pool_and_acc(builder, gate):
        recs = []
        for _doc, p in docs:
            ms, ns = builder(p)
            recs += _resolve(reader, ms, ns, gate=gate)
        pools = [r.get("n_pool", 0) for r in recs]
        return _acc(recs), (sum(pools) / len(pools) if pools else 0), len(recs)

    off = pool_and_acc(lambda p: parse_litbank_conll(p, name_gender_map=gaz), False)
    link = pool_and_acc(lambda p: build_linked(p, tagger, gaz, enrich=True, merge=True), True)
    link_nf = pool_and_acc(lambda p: build_linked(p, tagger, gaz, enrich=True, merge=True, use_frame=False), True)
    print("=" * 78)
    print("POOL INFLATION PROBE (%d docs)" % len(docs))
    print("  %-32s acc=%.4f  mean he/she pool=%.2f  n=%d" % ("OFF coref-column", *off))
    print("  %-32s acc=%.4f  mean he/she pool=%.2f  n=%d" % ("LINKER (frame ON)", *link))
    print("  %-32s acc=%.4f  mean he/she pool=%.2f  n=%d" % ("LINKER (frame OFF)", *link_nf))
    print("=" * 78)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if mode == "diag":
        diagnose_linker(n)
    elif mode == "probe":
        probe(n)
    elif mode == "headline":
        headline(n if len(sys.argv) > 2 else 25)
    else:
        run(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8)
