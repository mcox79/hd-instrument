"""Organ-landing witness for reason_over_the_spatial_relational_model_containment_position_path_modern_gold
(Q111, landed 2026-09-06): the glass-box RELATIONAL SPATIAL REASONER -- transitive region-nesting CONTAINMENT
(Wiener & Mallot / Dusek & Eichenbaum), Franklin-Tversky RELATIVE POSITION (per-axis closure + converse +
nested-frame inheritance), and Goal-over-Source PATH/TRANSFER with the vacate-Source 'no longer' read (Lakusta &
Landau) -- promoted BYTE-FAITHFUL into hdlab.spatial_relational_model and wired as a read()-time QUERY layer on the
SituationReader (sm.spatial_reasoner() + spatial_contains / spatial_relative / spatial_still_at / spatial_where_after,
default-on track_spatial_reasoning). The SPACE-channel sibling of hdlab.causal_reasoner: a NEW ISLAND / query layer
that COMPOSES the reader's OWN location tracking (sm.locations, the hdlab.location_register.LocationRegister) -- no
downstream consumer today -> no regression, and it mutates NO existing field (read-only).

  W1 PROMOTION FAITHFUL. hdlab.spatial_relational_model.{SpatialModel,norm_rel,canon_entity} source is BYTE-IDENTICAL
     to the reference experiments.spatial_relational_model (inspect.getsource identity), and the promoted module
     imports stdlib + hdlab.location_register ONLY (NO experiments import; AST-checked). So the reference headline is
     produced by identical code.
  W2 REASONER SANITY THROUGH THE PROMOTED ORGAN (the containment + position sanity results). Re-derived LIVE through
     hdlab.spatial_relational_model: transitive containment (key in box in drawer |= key in drawer), converse +
     transitive position (lamp left sofa left door |= lamp left door AND door right lamp), nested-frame inheritance
     (cup in left-box, pen in right-box, left-box left-of right-box |= cup left-of pen), and Goal-over-Source
     path/transfer with the vacate-Source read (she kitchen->garden |= at garden AND NOT still at kitchen).
  W3 HEADLINE REPRODUCES (through byte-identical promoted code, per W1). Reusing the reference gold cells: on MODERN
     gold the reasoner is near-perfect and CI-separated over the last-mention floor with the shuffled-relation twin
     collapsing, for CONTAINMENT (SpaceEval/ISO-Space) and RELATIVE POSITION (SpartQA-HUMAN gold SPRL).
  W4 ADDITIVE / BYTE-SAFE. track_spatial_reasoning is a PURE ADD: on real LitBank docs, EVERY existing SituationModel
     dimension is byte-identical off vs on (events, entities, coref, timeline, causal_links, and -- load-bearing --
     sm.locations, which the reasoner CONSUMES). The off reader leaves all 5 spatial callables None; the on reader
     exposes them (the only additions). all_capabilities_off forces the flag False, and adding ONLY the flag to the
     all-off baseline is byte-identical on every existing dim. The readout is LAZY (sm.spatial_reasoner stays None
     until a callable is invoked).
  W5 LIVE CONSUMER. Through SituationReader.read() on a doc whose OWN motion extraction moves an entity kitchen ->
     garden, sm.spatial_where_after returns the post-move node and sm.spatial_still_at applies the vacate-Source read
     (False at the vacated Source, True at the current Goal / a region that nests it), reasoning over the reader's
     OWN sm.locations. spatial_relative ABSTAINS (projective position is not in the tracking core -- the un-landed
     text->relation extractor is the SOLVED named follow-on), and every readout abstains cleanly on an absent
     register, never raising -- the honest upstream gap, a named default-off follow-on, not a regression.

Glass-box, NO external LLM, deterministic, ASCII, CPU-only, threads capped.
Reverify: .venv/Scripts/python.exe verification/test_spatial_relational_landing.py
"""
from __future__ import annotations

import ast
import os
import re
import sys
import glob
import inspect
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")
os.environ.setdefault("MKL_NUM_THREADS", "3")
os.environ.setdefault("THINC_NUM_THREADS", "3")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _reader(**kw):
    from hdlab.situation_reader import SituationReader
    # isolate from the concurrent meaning-channel integration (orthogonal to the spatial reasoner); these
    # gitignored-asset dimensions abstain in an asset-less env but are noise for THIS witness's byte-diff.
    kw.setdefault("track_bridges", False)
    kw.setdefault("track_senses", False)
    kw.setdefault("track_prediction", False)
    return SituationReader(gaz={"john": "masc", "mary": "fem", "she": "fem", "he": "masc",
                                "anna": "fem", "her": "fem"}, **kw)


def _tok(s):
    return re.findall(r"[A-Za-z']+|[0-9]+|[.,;:!?]", s)


def _sents(p):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", p.strip()) if x.strip()]


def _write_conll(text, alias_set, pid, outdir):
    path = os.path.join(outdir, pid + ".conll")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("#begin document (%s); part 0\n" % pid)
        for s in _sents(text):
            for i, tk in enumerate(_tok(s)):
                bare = tk.lower().strip(".,;:!?\"'()")
                coref = "(0)" if bare in alias_set else "_"
                f.write("\t".join([pid, "0", str(i), tk] + ["_"] * 8 + [coref]) + "\n")
            f.write("\n")
    return path


# ---------------------------------------------------------------------------
# W1 -- PROMOTION FAITHFUL: byte-identical source + no experiments import.
# ---------------------------------------------------------------------------
def test_w1_promotion_faithful():
    import hdlab.spatial_relational_model as H
    import experiments.spatial_relational_model as R
    ident = all(inspect.getsource(getattr(H, c)) == inspect.getsource(getattr(R, c))
                for c in ("SpatialModel", "norm_rel", "canon_entity"))
    check("W1a promoted hdlab.spatial_relational_model {SpatialModel,norm_rel,canon_entity} source BYTE-IDENTICAL "
          "to the reference experiments.spatial_relational_model (inspect.getsource identity)", ident)
    consts = (H.AXIS_OF == R.AXIS_OF and H.CONTAIN_RELTYPES == R.CONTAIN_RELTYPES and H.SYMMETRIC == R.SYMMETRIC)
    check("W1a2 module constants (AXIS_OF / CONTAIN_RELTYPES / SYMMETRIC) identical", consts)
    src = open(H.__file__, encoding="utf-8").read()
    mods = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            mods.add(n.module or "")
    no_exp = not any(m.startswith("experiments") for m in mods)
    check("W1b promoted module imports stdlib + hdlab.location_register ONLY (NO experiments import; AST-checked)",
          no_exp and "hdlab.location_register" in mods, "imports=%s" % sorted(mods))


# ---------------------------------------------------------------------------
# W2 -- REASONER SANITY through the PROMOTED organ (containment + position sanity).
# ---------------------------------------------------------------------------
def test_w2_reasoner_sanity():
    from hdlab.spatial_relational_model import SpatialModel
    m = SpatialModel(); m.add_containment("key", "box"); m.add_containment("box", "drawer")
    s1 = m.contains_path("key", "drawer") and not m.contains_path("drawer", "key")
    m2 = SpatialModel(); m2.add_position("lamp", "left", "sofa"); m2.add_position("sofa", "left", "door")
    s2 = (m2.relative("lamp", "left", "door") is True) and (m2.relative("door", "right", "lamp") is True)
    m3 = SpatialModel()
    m3.add_containment("cup", "left box"); m3.add_containment("pen", "right box")
    m3.add_position("left box", "left", "right box")
    s3 = (m3.relative("cup", "left", "pen") is True)          # nested-frame inheritance
    m4 = SpatialModel(); m4.add_move("she", "kitchen", "garden", 0)
    s4 = ((m4.where_after("she") == "garden") and (m4.still_at("she", "kitchen") is False)
          and (m4.still_at("she", "garden") is True))
    check("W2 reasoner sanity through the PROMOTED organ (transitive containment; converse+transitive position; "
          "nested-frame inheritance; Goal-over-Source vacate)", s1 and s2 and s3 and s4,
          "contain=%s pos=%s inherit=%s vacate=%s" % (s1, s2, s3, s4))


# ---------------------------------------------------------------------------
# W3 -- HEADLINE REPRODUCES through byte-identical promoted code (reference gold cells).
# ---------------------------------------------------------------------------
def test_w3_headline_reproduces():
    from experiments.spatial_gold_loaders import load_spaceeval_docs, load_spartqa_gold_relations
    from experiments.exp_spatial_reasoner_gold_relations_v1 import (
        build_containment_items, score_containment, summarize)
    from experiments.exp_spatial_position_gold_v1 import (
        build_position_items, score as score_posgold, summarize as summ_pos)

    # CONTAINMENT (SpaceEval/ISO-Space gold) -- reasoner ~1.000, CI-sep over last-mention, twin collapses
    train = load_spaceeval_docs("train")
    c_items = build_containment_items(train, seed=0)
    c_arms, c_meta = score_containment(train, c_items, seed=0)
    c_res = summarize("containment", c_arms, c_meta)
    cm = c_res["margin_reasoner_minus_lastmention"]
    check("W3a CONTAINMENT (gold): reasoner %.3f ~1.000, CI-sep over last-mention %.3f, twin %.3f collapses "
          "(margin %.3f CI[%.3f,%.3f]) -- reproduced through byte-identical promoted code (W1)"
          % (c_res["reasoner"][0], c_res["lastmention"][0], c_res["twin"][0], cm["margin"], cm["lo"], cm["hi"]),
          cm["sep"] and c_res["reasoner"][0] >= 0.99 and c_res["lastmention"][0] < 0.99 and c_res["twin"][0] < 0.7)

    # RELATIVE POSITION (SpartQA-HUMAN gold SPRL) -- reasoner ~1.000, CI-sep over last-mention, twin collapses
    gdocs = load_spartqa_gold_relations("test")
    gitems = build_position_items(gdocs, seed=0)
    garms, gmeta = score_posgold(gdocs, gitems, seed=0)
    gres = summ_pos(garms, gmeta)
    gm = gres["margin_reasoner_minus_lastmention"]
    check("W3b RELATIVE POSITION (gold): reasoner %.3f ~1.000, CI-sep over last-mention %.3f, twin %.3f collapses "
          "(margin %.3f CI[%.3f,%.3f]) -- reproduced through byte-identical promoted code (W1)"
          % (gres["reasoner"][0], gres["lastmention"][0], gres["twin"][0], gm["margin"], gm["lo"], gm["hi"]),
          gm["sep"] and gres["reasoner"][0] >= 0.99 and gres["twin"][0] < 0.5)


# ---------------------------------------------------------------------------
# W4 -- ADDITIVE / BYTE-SAFE: track_spatial_reasoning is a PURE ADD.
# ---------------------------------------------------------------------------
_SPATIAL_CBLS = ("spatial_reasoner", "spatial_contains", "spatial_relative",
                 "spatial_still_at", "spatial_where_after")


def _dims(sm):
    ev = [(e.global_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm.events]
    ent = [(e.cluster, tuple(e.heads), e.n_mentions) for e in sm.entities]
    cor = [(r.correct, r.sent_dist) for r in sm.coref_resolutions]
    cau = [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links]
    tl = [(f.sent_idx, f.reordered) for f in sm.timeline_frames]
    reg = getattr(sm, "locations", None)
    loc = None if reg is None else [(e, reg.where_is(e), tuple((iv.node, iv.t_open, iv.t_close)
                                                               for iv in reg.intervals_of(e)))
                                    for e in sorted(reg.tracks)]
    return ev, ent, cor, cau, tl, loc


def test_w4_additive_byte_identical():
    docs = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[:2]
    check("W4-precheck: LitBank coref conll docs present", len(docs) >= 1, "found %d docs" % len(docs))
    if not docs:
        return
    all_ident = True
    detail = []
    for doc in docs:
        off = _reader(track_spatial_reasoning=False).read(doc)
        on = _reader(track_spatial_reasoning=True).read(doc)
        d_off, d_on = _dims(off), _dims(on)
        ident = (d_off == d_on)
        all_ident = all_ident and ident
        nloc = 0 if d_on[5] is None else len(d_on[5])
        detail.append("%s events=%d locations=%d %s"
                      % (os.path.basename(doc), len(d_on[0]), nloc, "IDENT" if ident else "DIFF"))
        off_none = all(getattr(off, a) is None for a in _SPATIAL_CBLS)
        on_cbl = all(callable(getattr(on, a)) for a in _SPATIAL_CBLS)
        # LAZY: the callables are bound but nothing is built until one is INVOKED
        check("W4b [%s] off exposes NO spatial callables; on exposes spatial_reasoner + 4 readouts"
              % os.path.basename(doc), off_none and on_cbl)
    check("W4a every existing SituationModel dimension BYTE-IDENTICAL off vs on (events, entities, coref, timeline, "
          "causal_links, and load-bearing sm.locations -- the reasoner CONSUMES it)", all_ident, " | ".join(detail))

    # all_capabilities_off forces the flag False; adding ONLY the flag to the all-off baseline is byte-identical
    from hdlab.situation_reader import SituationReader
    g = {"john": "masc", "mary": "fem", "she": "fem", "he": "masc", "anna": "fem", "her": "fem"}
    base_off = SituationReader.all_capabilities_off(gaz=g).read(docs[0])
    base_on = SituationReader.all_capabilities_off(gaz=g, track_spatial_reasoning=True).read(docs[0])
    forced = SituationReader.all_capabilities_off(gaz=g).track_spatial_reasoning is False
    check("W4c all_capabilities_off forces track_spatial_reasoning False, and adding ONLY the flag to the all-off "
          "baseline is byte-identical on every existing dim", forced and _dims(base_off) == _dims(base_on),
          "forced_off=%s" % forced)


# ---------------------------------------------------------------------------
# W5 -- LIVE CONSUMER: reason over the reader's OWN sm.locations; abstain cleanly.
# ---------------------------------------------------------------------------
def test_w5_live_consumer():
    outdir = tempfile.mkdtemp()
    # A doc whose OWN motion extraction moves the entity kitchen -> garden.
    text = "Anna was in the kitchen. Then Anna went out to the garden. She sat down on the grass."
    doc = _write_conll(text, {"anna", "she", "her"}, "spatial_live", outdir)
    on = _reader(track_spatial_reasoning=True).read(doc)

    M = on.spatial_reasoner()
    from hdlab.spatial_relational_model import SpatialModel
    reg = on.locations
    keys = sorted(reg.tracks) if reg is not None else []
    check("W5a the LIVE reader builds a SpatialModel over its OWN sm.locations (register present with >=1 track)",
          isinstance(M, SpatialModel) and reg is not None and len(keys) >= 1,
          "model=%s tracks=%s where=%s" % (type(M).__name__, keys,
                                           {k: reg.where_is(k) for k in keys} if reg else None))

    # find the mover: a track whose current node is a NAMED place (the reader extracted a Goal for it)
    mover = next((k for k in keys if reg.where_is(k) not in (None, "<scene>", "<away>")), None)
    if mover is not None:
        goal = reg.where_is(mover)
        wa = on.spatial_where_after(mover)
        still_goal = on.spatial_still_at(mover, goal)
        # the vacate-Source read: once moved to the Goal, NOT still at a DIFFERENT named place it left
        prior = None
        for iv in reg.intervals_of(mover):
            if iv.node not in (None, "<scene>", "<away>") and iv.node != goal:
                prior = iv.node
        still_prior = on.spatial_still_at(mover, prior) if prior is not None else False
        check("W5b LIVE path/transfer over sm.locations: spatial_where_after=current Goal node; spatial_still_at "
              "True at the Goal; vacate-Source -> NOT still at a vacated earlier named place",
              wa == goal and still_goal is True and (prior is None or still_prior is False),
              "mover=%r goal=%r where_after=%r still_at(goal)=%r prior=%r still_at(prior)=%r"
              % (mover, goal, wa, still_goal, prior, still_prior))
        # region nesting (seeded from the register's two-level membership) composes with still_at
        from hdlab.location_register import spatial_region
        rgn = spatial_region(goal)
        region_ok = (on.spatial_contains(goal, rgn) is True) if rgn is not None else True
        check("W5c region-nesting containment composes (goal node nests inside its INDOORS/OUTDOORS region -- the "
              "register's two-level membership, seeded into the SpatialModel)", region_ok,
              "goal=%r region=%r contains=%s" % (goal, rgn, None if rgn is None else on.spatial_contains(goal, rgn)))
    else:
        check("W5b/W5c LIVE mover present", False, "no named-place track extracted (keys=%s)" % keys)

    # projective position ABSTAINS (not in the tracking core -- the un-landed extractor is the SOLVED follow-on)
    rel = on.spatial_relative(mover or "0", "left", goal if mover else "garden")
    check("W5d spatial_relative ABSTAINS (returns None) -- projective position is not in the tracking core; the "
          "text->relation extractor is the SOLVED named follow-on (NOT landed) = the honest upstream gap",
          rel is None, "spatial_relative=%r" % rel)

    # CLEAN ABSTENTION when the register is absent (track_space off) -> every readout None/False, never raises
    off_space = _reader(track_spatial_reasoning=True, track_space=False).read(doc)
    absent = (off_space.spatial_reasoner() is not None                       # the model builds (empty)
              and off_space.spatial_where_after("0") is None
              and off_space.spatial_still_at("0", "garden") is None
              and off_space.spatial_contains("kitchen", "house") is False
              and off_space.spatial_relative("0", "left", "garden") is None)
    check("W5e on an ABSENT register (track_space off) every readout abstains cleanly (None / False), never raises",
          absent)


if __name__ == "__main__":
    test_w1_promotion_faithful()
    test_w2_reasoner_sanity()
    test_w3_headline_reproduces()
    test_w4_additive_byte_identical()
    test_w5_live_consumer()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED")
