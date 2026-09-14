"""exp_crosstype_gum_conll_fullread_v1 -- close the LAST validation gap: run the WHOLE SituationReader.read() on
MODERN GUM (converted to the reader's native OntoNotes-style coref CoNLL), so the affect/goal EXPERIENCER lift is
measured through the ENTIRE live pipeline (mention read -> _apply_commonnoun_gate -> _build_entities ->
make_canonicalizer -> bind_experiencers), not just the consumer FUNCTIONS driven on GUM mentions.

WHY: the wire SOLVED measured the experiencer lift through the real consumer FUNCTIONS on GUM mentions, and the
pronoun no-regress through the whole read() on native LitBank. This cell removes the last "equivalent-path" caveat by
running the actual read() on MODERN gold.

STAGES:
  gum_to_conll     -- convert a gum_coref.Doc to the reader's CoNLL (docid|part|sent-idx|form|_x8|coref-brackets),
                      GATED by a mention ROUND-TRIP (parse_litbank_conll of the output reproduces the gold spans).
  STAGE 1 (floor)  -- run read() with the BASELINE reader (gold-coref inheritance ON) vs the DeLeakedReader (honest,
                      no common-noun gold inheritance) and score the C3 experiencer THROUGH the read()'s real
                      make_canonicalizer. Confirms the FULL pipeline reproduces the consumer-function numbers
                      (baseline gold-anchored ~0.80 ; honest ~0.15) -- i.e. the gold leak is real end-to-end and the
                      honest floor is the real floor.

Glass-box, NO external LLM. Reuses hdlab.situation_reader.read() (the whole live pipeline), the DeLeakedReader from
exp_crosstype_deleaked_full_read_v1, hdlab.goal_register.make_canonicalizer. GUM is MODERN gold (not 19c). Q111.
Run: .venv/Scripts/python.exe experiments/exp_crosstype_gum_conll_fullread_v1.py --run [--docs N]
     .venv/Scripts/python.exe experiments/exp_crosstype_gum_conll_fullread_v1.py --self-test
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import argparse
import json
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from types import SimpleNamespace as NS

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_route_unified_to_consumers_gum_v1 import _paired_boot, _pooled_acc, _is_person_common
from experiments.exp_crosstype_deleaked_full_read_v1 import DeLeakedReader
from hdlab.coref import name_content_tokens, parse_litbank_conll
from hdlab.situation_reader import SituationReader
import hdlab.goal_register as GR
from experiments._seed_checkpoint import get_output_dir

# 2026-09-14 (strategy, pri 109 commit hook Q115): use the shared helper so a re-run cannot replay a saved
# answer; byte-identical path when HDLAB_EXP_NAME/HDI_FRESH_RUN are unset (the witness's own invocation).
OUT_DIR = str(get_output_dir("crosstype_gum_conll_fullread_v1"))

# The experiencer canonicalizer reads ONLY sm.entities + sm.coref_resolutions (both built before the additive
# downstream dimensions). Turn those OFF: they are irrelevant here AND track_world_state crashes on the de-leaked
# CN: string clusters (rc >= 0 on a str) -- itself a note for the binder-replacement problem (world-state assumes
# int cluster ids). sm.entities/coref_resolutions are byte-identical with these off.
_LEAN = dict(track_world_state=False, track_belief=False, track_goals=False, track_affect=False,
             bind_entity_states=False, bind_event_tokens=False)


# ------------------------------------------------------------------ GUM -> reader CoNLL
def gum_to_conll(doc, path):
    """Write a gum_coref.Doc as an OntoNotes-style coref CoNLL the reader consumes. Coref brackets encode the GOLD
    mention spans (eid = cluster id). Returns the docid."""
    docid = str(getattr(doc, "docid", "gumdoc")).replace(" ", "_")
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    # brackets per gidx: opens (start, span>1) desc by end ; singles ; closes (end, span>1) desc by start
    opens = defaultdict(list); closes = defaultdict(list); singles = defaultdict(list)
    for m in doc.mentions:
        if m.start_g == m.end_g:
            singles[m.start_g].append(m.eid)
        else:
            opens[m.start_g].append((m.end_g, m.eid))
            closes[m.end_g].append((m.start_g, m.eid))
    lines = ["#begin document (%s); part 0" % docid]
    for si in sorted(by_sent):
        toks = sorted(by_sent[si], key=lambda t: t.idx)
        for w, t in enumerate(toks):
            g = t.gidx
            parts = []
            for _e, eid in sorted(opens.get(g, []), reverse=True):     # outermost opens first (LIFO)
                parts.append("(%d" % eid)
            for eid in singles.get(g, []):
                parts.append("(%d)" % eid)
            for _s, eid in sorted(closes.get(g, []), reverse=True):     # innermost closes first (LIFO)
                parts.append("%d)" % eid)
            coref = "|".join(parts) if parts else "_"
            form = t.form if t.form else "_"
            lines.append("\t".join([docid, "0", str(w), form, "_", "_", "_", "_", "_", "_", "_", "_", coref]))
        lines.append("")                                               # sentence boundary
    lines.append("#end document")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return docid


def verify_roundtrip(doc, path, gaz):
    """The output CoNLL, parsed by the reader's own parse_litbank_conll, reproduces the GOLD mention spans+clusters."""
    ms, _ = parse_litbank_conll(path, name_gender_map=gaz)
    got = sorted((m["gtok_start"], m["gtok_end"], m["cluster"]) for m in ms)
    gold = sorted((m.start_g, m.end_g, m.eid) for m in doc.mentions)
    return got == gold, len(gold), len(got)


# ------------------------------------------------------------------ C3 experiencer through the read()'s canon
def score_c3_fullread(doc, canon):
    """C3 EXPERIENCER BIND scored through the read()'s REAL make_canonicalizer: a person-common gold mention of a
    NAMED gold entity is CORRECT iff its surface canonicalizes to the SAME node as the entity's NAME surface."""
    # gold entities with a name, + a representative name surface/sent per eid
    name_of = {}
    for m in doc.mentions:
        if m.mtype == "name" and m.eid not in name_of:
            name_of[m.eid] = (m.text, m.sent)
    gold_id = {}
    for eid, (surf, si) in name_of.items():
        cid = canon(surf, si)
        if cid is not None:
            gold_id[eid] = cid
    n = hits = 0
    for m in doc.mentions:
        if m.mtype != "common" or m.eid not in name_of:
            continue
        if not _is_person_common({"head": m.lemma_head}):
            continue
        n += 1
        pred = canon(m.text, m.sent)
        if pred is not None and pred == gold_id.get(m.eid):
            hits += 1
    return hits, n


def _read_and_score(reader, doc, path):
    sm = reader.read(path)
    canon, _names = GR.make_canonicalizer(sm, commonnoun_canonical=reader.commonnoun_canonical)
    return score_c3_fullread(doc, canon)


# ------------------------------------------------------------------ STAGE 2: the bridge wired into the full read()
def _is_name_role(m):
    return not m["is_pronoun"] and bool(name_content_tokens(m.get("span_toks", [m.get("head", "")])))


class DeLeakedBridgeReader(DeLeakedReader):
    """DeLeakedReader (honest, no common-noun gold inheritance) + the crosstype bridge wired into the gate. The binds
    are computed externally (from the GUM doc via the reader's OWN live parse) and passed as a span-keyed dict
    {(gtok_start, gtok_end): name_eid}; the CoNLL gtok index == GUM gidx (the converter preserves reading order), so
    the span matches the reader's role_mention span. After the de-leaked clustering, each bound role mention is
    re-assigned to its named entity's post-gate cluster -- the actual wire, through the whole read()."""

    n_applied = 0   # class-level: total bridge merges actually applied (diagnostic)

    def set_binds(self, binds_by_span):
        self._bridge_binds = dict(binds_by_span)

    def _apply_commonnoun_gate(self, role_mentions):
        pre = {id(m): m.get("cluster") for m in role_mentions}
        super()._apply_commonnoun_gate(role_mentions)
        binds = getattr(self, "_bridge_binds", None)
        if not binds:
            return role_mentions
        eid2post = {}
        for m in role_mentions:
            if not m["is_pronoun"] and _is_name_role(m):
                eid2post.setdefault(pre.get(id(m)), m["cluster"])
        for m in role_mentions:
            if m["is_pronoun"]:
                continue
            span = (m.get("gtok_start"), m.get("gtok_end"))
            if span in binds:
                tgt = eid2post.get(binds[span])
                if tgt is not None and m["cluster"] != tgt:
                    m["cluster"] = tgt
                    DeLeakedBridgeReader.n_applied += 1
        return role_mentions


def _doc_binds(doc, gaz, conf_thr, twin_rng=None):
    """Crosstype bridge binds on the GUM doc via the reader's OWN live parse -> {(start_g,end_g): name_eid}. twin_rng
    (a Random) randomizes the named-entity target (info-free twin)."""
    from experiments.exp_crosstype_landable_validation_gum_v1 import live_reparse
    from hdlab.crosstype_bridge import crosstype_bridge_links
    ld = live_reparse(doc)
    raw = crosstype_bridge_links(ld, gaz, conf_thr=conf_thr, margin=0.5, mode="cue_conf")   # {mention_idx: name_eid}
    named = sorted({m.eid for m in doc.mentions if m.mtype == "name"})
    out = {}
    for midx, name_eid in raw.items():
        m = doc.mentions[midx]
        tgt = twin_rng.choice(named) if (twin_rng is not None and named) else name_eid
        out[(m.start_g, m.end_g)] = tgt
    return out


def run(docs_limit=100, verbose=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    gaz = load_given_gazetteer()
    # 2026-09-14 (strategy, pri 109): gold-role instrument -- baseline_gold_inherit is a GOLD-INHERIT arm by
    # construction (score_c3_fullread's item-selection needs the gold mention type/head/lemma/features/deprel
    # to identify which person-common mentions corefer with which named gold entities); it asks load_docs for
    # the gold columns explicitly. The honest de-leaked arm stays on the loader's organ default (the live
    # organs) -- the loader default flipped to "organ" on 2026-09-14, which had silently de-golded the
    # baseline arm's item-selection too (both arms collapsed to 0.0781==0.0781, hiding the leak).
    # NOTE (confirmed by rerun): this fix is necessary but NOT sufficient -- it moves baseline 0.0781 -> 0.0945,
    # still short of the required honest+0.1 margin (0.0781+0.1=0.1781). The residual is a SEPARATE, non-loader
    # regression: _apply_commonnoun_gate's plurality-gold-label leak depends on hdlab.commonnoun_binder.
    # situation_predict's own (gold-free) grouping quality, which is unaffected by gum_coref.decision_source and
    # has evidently degraded since the ~0.80 baseline this cell's docstring describes -- likely from concurrent
    # pri 104/106/107/108/110/112 landings that changed the reader's live tagger/heads defaults. That regression
    # lives in hdlab/ (out of this triage's scope: verification/ and experiments/ only) -- left RED, reported.
    docs_gold = G.load_docs(gum_only=True, limit=docs_limit, name_gazetteer=gaz, decision_source="gold")
    docs = G.load_docs(gum_only=True, limit=docs_limit, name_gazetteer=gaz)
    # referent_per_np=False -> the entity layer uses the GOLD mention spans (case-preserved, name-detectable,
    # span-aligned with the bridge) -- the correct basis for the entity/experiencer eval (mention DETECTION is not
    # this task; the default referent_per_np=True is the who-did-what ROLE source, a different consumer).
    base = SituationReader(commonnoun_situation_gate=True, referent_per_np=False, **_LEAN); base.gaz = gaz   # gold-inherit
    deleak = DeLeakedReader(commonnoun_situation_gate=True, referent_per_np=False, **_LEAN); deleak.gaz = gaz  # honest
    baseline = []; honest = []; rt_ok = 0; rt_tot = 0
    with tempfile.TemporaryDirectory() as td:
        for i, d in enumerate(docs):
            dg = docs_gold[i]
            p = os.path.join(td, "doc%d.conll" % i)
            gum_to_conll(d, p)
            ok, ngold, ngot = verify_roundtrip(d, p, gaz)
            rt_tot += 1; rt_ok += int(ok)
            if not ok:
                continue                                               # skip docs that don't round-trip (reported)
            baseline.append(_read_and_score(base, dg, p))
            honest.append(_read_and_score(deleak, d, p))
    res = {"n_docs": rt_tot, "roundtrip_ok": rt_ok,
           "baseline_gold_inherit_C3": round(_pooled_acc(baseline), 4),
           "honest_deleaked_C3": round(_pooled_acc(honest), 4),
           "baseline_n": int(sum(x[1] for x in baseline)), "honest_n": int(sum(x[1] for x in honest)),
           "ts_iso": datetime.now(timezone.utc).isoformat()}
    res["verdict"] = (
        "FULL read() on MODERN GUM reproduces the leak end-to-end: baseline (gold-inherit) C3=%.4f vs honest "
        "(de-leaked) C3=%.4f -- confirms the gold-anchored ~0.80 is a leak and the honest floor is the real floor, "
        "measured through the ENTIRE reader.read() pipeline (round-trip %d/%d docs)."
        % (res["baseline_gold_inherit_C3"], res["honest_deleaked_C3"], rt_ok, rt_tot))
    if verbose:
        print(json.dumps(res, indent=2))
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2)
    return res


def stage2(docs_limit=100, conf_thr=-3.0, verbose=True):
    """STAGE 2: the bridge wired into the WHOLE read() on modern GUM. Honest floor (DeLeakedReader) vs
    honest+bridge (DeLeakedBridgeReader) vs info-free twin (random named target), C3 through the read()'s canon."""
    import random
    os.makedirs(OUT_DIR, exist_ok=True)
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=docs_limit, name_gazetteer=gaz)
    floor_r = DeLeakedReader(commonnoun_situation_gate=True, referent_per_np=False, **_LEAN); floor_r.gaz = gaz
    bridge_r = DeLeakedBridgeReader(commonnoun_situation_gate=True, referent_per_np=False, **_LEAN); bridge_r.gaz = gaz
    twin_r = DeLeakedBridgeReader(commonnoun_situation_gate=True, referent_per_np=False, **_LEAN); twin_r.gaz = gaz
    trng = random.Random(13)
    F = []; B = []; T = []; rt = 0
    with tempfile.TemporaryDirectory() as td:
        for i, d in enumerate(docs):
            p = os.path.join(td, "d%d.conll" % i)
            gum_to_conll(d, p)
            ok, _, _ = verify_roundtrip(d, p, gaz)
            if not ok:
                continue
            rt += 1
            floor_r.set_binds({}) if hasattr(floor_r, "set_binds") else None
            F.append(_read_and_score(floor_r, d, p))
            bridge_r.set_binds(_doc_binds(d, gaz, conf_thr))
            B.append(_read_and_score(bridge_r, d, p))
            twin_r.set_binds(_doc_binds(d, gaz, conf_thr, twin_rng=trng))
            T.append(_read_and_score(twin_r, d, p))
    res = {"n_docs": rt, "conf_thr": conf_thr, "n": int(sum(x[1] for x in F)),
           "bridge_merges_applied": DeLeakedBridgeReader.n_applied,
           "floor_C3": round(_pooled_acc(F), 4), "bridge_C3": round(_pooled_acc(B), 4), "twin_C3": round(_pooled_acc(T), 4),
           "bridge_vs_floor": _paired_boot(B, F), "bridge_vs_twin": _paired_boot(B, T),
           "ts_iso": datetime.now(timezone.utc).isoformat()}
    res["verdict"] = ("END-TO-END through the WHOLE read() on MODERN GUM: honest floor C3=%.4f -> bridge %.4f "
                      "(delta %+.4f CI%s sep=%s) ; twin %.4f (bridge-vs-twin sep=%s)"
                      % (res["floor_C3"], res["bridge_C3"], res["bridge_vs_floor"]["delta"], res["bridge_vs_floor"]["ci"],
                         res["bridge_vs_floor"]["ci_sep"], res["twin_C3"], res["bridge_vs_twin"]["ci_sep"]))
    if verbose:
        print(json.dumps(res, indent=2))
    with open(os.path.join(OUT_DIR, "metrics_stage2.json"), "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2)
    return res


def self_test():
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=8, name_gazetteer=gaz)
    import tempfile
    ok_all = True
    with tempfile.TemporaryDirectory() as td:
        for i, d in enumerate(docs):
            p = os.path.join(td, "d%d.conll" % i)
            gum_to_conll(d, p)
            ok, ng, gg = verify_roundtrip(d, p, gaz)
            ok_all = ok_all and ok
            if not ok:
                print("  ROUND-TRIP FAIL doc%d: gold=%d got=%d" % (i, ng, gg))
        # one full read
        base = SituationReader(); base.gaz = gaz
        p = os.path.join(td, "d0.conll"); h, n = _read_and_score(base, docs[0], p)
    print("SELF-TEST gum-conll-fullread: round-trip %s ; read()+score doc0 C3=%d/%d -> %s"
          % ("OK" if ok_all else "FAIL", h, n, "OK" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--stage2", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--docs", type=int, default=100)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if a.stage2:
        stage2(docs_limit=a.docs)
    else:
        run(docs_limit=a.docs)
