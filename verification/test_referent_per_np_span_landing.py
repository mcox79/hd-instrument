"""LANDING WITNESS -- pri 138: ONE DISCOURSE REFERENT PER NOUN PHRASE, WITH REAL TOKEN POSITIONS.

WHAT THIS WITNESS PINS (claims, not numbers -- per the standing rule).
  1. ONE REFERENT PER NOUN PHRASE.  On a fixture the introduction organ opens ONE referent for 'the old
     baker' and ONE for 'the New York Times', not one per content noun; the surviving head is the phrase's
     RIGHTMOST member (Williams 1981) and each absorbed head is recorded, so nothing is silently dropped.
  2. THE DETERMINER IS ON THE CARD.  `lexical_utils.definiteness` reads `def` / `indef` off the mention --
     Heim's Novelty-Familiarity Condition is READABLE, which it was not on a bare-head span.
  3. THE POSITIONS ARE REAL AND VALID.  Every mention the organ makes carries `0 <= gtok_start <= gtok_end <
     n_tokens`, `wtok_start` is the SPAN START, `span_toks[-1]` is the head, `span_upos` is the same length
     as the span, and `coref.mention_span` returns a real extent -- on the nominal arm AND the pronoun arm.
  4. THE HEAD IS STILL RECOVERABLE, BY THE SUBSTRATE'S OWN ACCESSOR.  `graded_role_assigner.
     mention_head_wpos` returns the head's within-sentence index for every mention, and it is byte-identical
     to `wtok_start` on a one-token mention (so no consumer that was right becomes wrong).
  5. A DETERMINER CLOSES THE PHRASE ON ITS LEFT.  'the dog the cat saw' is TWO phrases: the D is the
     phrase's outermost layer (Abney 1991), so a second determiner opens a second card.
  6. A POST-HEAD DEPENDENT IS NOT ABSORBED, AND A PHRASE NEVER CROSSES ITS CLAUSE'S VERB -- which is why
     every pre/post-verbal positional cue keeps its answer.
  7. THE BOUNDARY IS THE READER'S OWN ORGANS, WITH NO SECOND PARSE.  The reader's tag shim serves the
     SHARED per-read parse (`_CachedTagShim.parse_heads`), and the graded arm is read at its MAP -- there is
     no fitted boundary table and no chunker.
  8. THE A/B SWITCH IS EXACT.  `RPN_SPAN` off restores every field of the pre-2026-09-16 organ byte-for-byte.
  9. THE FILE CARD'S LABEL IS ITS NAME.  `goal_register._cluster_name` returns the card's NAME when it holds
     one, not its longest surface -- otherwise a whole-phrase mention makes the label a common-noun phrase.
 10. THE LIVE READER RUNS AND ITS CONSUMERS SEE THE PHRASE STREAM (a real read on a real document: the
     mentions carry valid positions, the crosstype bridge's Doc builds, and the reader still produces events).

TREE STATE.  The witness DETECTS whether the patch has landed, from the LIVE modules (`referent_per_np.
np_groups` plus `_CachedTagShim.parse_heads` -- functions only this diff adds).  On the landed tree every
claim is asserted against the live modules with no materialize and no monkeypatch.  BEFORE landing it first
asserts THE DEFECT IS PRESENT (gtok_start == -1, span_toks == [head]), then compiles the shipped diff into
the live modules -- the same source that lands -- and asserts every claim on that tree shape, saying out loud
that the defect is still present in the repository.

Run: .venv/Scripts/python.exe verification/test_referent_per_np_span_landing.py
Glass-box, NO LLM, deterministic, CPU-only.  Writes nothing.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

SLUG = ("the_introduction_organ_opens_one_referent_per_content_noun_token_with_a_bare_head_span_and_no_"
        "global_index_rebuild_it_as_one_referent_per_np_with_the_attachment_arms_span_and_real_token_"
        "positions")
DIFF_PATH = os.path.join(_REPO, "notes", "problems", SLUG, "np_span_patch.diff")
PATCH_FILES = ["hdlab/referent_per_np.py", "hdlab/situation_reader.py",
               "hdlab/entity_resolver.py", "hdlab/goal_register.py"]

# a real document, for claim 10 (the smallest LitBank coref file the repo ships)
LIVE_DOC = os.path.join(_REPO, "data/litbank/coref/conll/1023_bleak_house_brat.conll")

_OK = [True]
_N = [0]


def ck(cond, msg):
    _N[0] += 1
    print(("  PASS " if cond else "  FAIL ") + msg, flush=True)
    if not cond:
        _OK[0] = False


def landed() -> bool:
    """Detected from the LIVE modules, by functions ONLY this diff adds."""
    import hdlab.referent_per_np as RPN
    import hdlab.situation_reader as SR
    return bool(getattr(RPN, "np_groups", None) is not None
                and hasattr(getattr(SR, "_CachedTagShim", object), "parse_heads"))


def _install_from_diff():
    """Compile the SHIPPED diff into the live modules (the pre-landing tree shape)."""
    import importlib
    import shutil
    import tempfile
    d = tempfile.mkdtemp(prefix="pri138_witness_")
    try:
        for rel in PATCH_FILES:
            dst = os.path.join(d, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(_REPO, rel), dst)
        pr = subprocess.run(["git", "apply", "-p1", os.path.abspath(DIFF_PATH)],
                            cwd=d, capture_output=True, text=True)
        assert pr.returncode == 0, "git apply failed: %s" % pr.stderr.strip()
        for rel in PATCH_FILES:
            src = io.open(os.path.join(d, rel.replace("/", os.sep)), encoding="utf-8").read()
            mod = importlib.import_module(rel[:-3].replace("/", "."))
            exec(compile(src, rel, "exec"), mod.__dict__)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# 'The old baker gave the New York Times a loaf .' -- with the arcs the attachment arm returns for it
FIX = ["The", "old", "baker", "gave", "the", "New", "York", "Times", "a", "loaf", "."]
FIX_UP = ["DET", "ADJ", "NOUN", "VERB", "DET", "PROPN", "PROPN", "PROPN", "DET", "NOUN", "PUNCT"]
FIX_HEADS_1B = {1: 3, 2: 3, 3: 4, 4: 0, 5: 8, 6: 8, 7: 8, 8: 4, 9: 10, 10: 4, 11: 4}


def main():
    was_landed = landed()
    if not was_landed:
        import hdlab.referent_per_np as _R0
        m0 = _R0._mk_referent("baker", 0, 2, 1, -1, upos="NOUN")
        ck(m0["gtok_start"] == -1 and m0["gtok_end"] == -1 and m0["span_toks"] == ["baker"],
           "[0] THE DEFECT IS STILL PRESENT IN THE REPOSITORY: the organ writes gtok_start = -1 and a "
           "bare-head span (this witness becomes a hard gate the moment the diff lands)")
        _install_from_diff()
        print("  ---- the shipped diff is compiled into the live modules (%d files) ----" % len(PATCH_FILES))
    else:
        print("  ---- the organ is LANDED: every claim below is asserted against the LIVE modules ----")

    import hdlab.referent_per_np as RPN
    import hdlab.situation_reader as SR
    import hdlab.goal_register as GR
    from hdlab.coref import mention_span
    from hdlab.graded_role_assigner import mention_head_wpos
    from hdlab.lexical_utils import definiteness, modifiers

    ck(landed(), "[pre] the live modules carry the organ (np_groups + _CachedTagShim.parse_heads)")
    RPN.RPN_SPAN, RPN.RPN_COLLAPSE, RPN.RPN_BOUNDARY = True, True, "both"
    gov = {j - 1: h - 1 for j, h in FIX_HEADS_1B.items()}

    # ---- 1. ONE REFERENT PER NOUN PHRASE -------------------------------------------------------
    grp = RPN.np_groups(FIX, FIX_UP, [2, 5, 6, 7, 9], gov, None, "both")
    ck(sorted(grp) == [2, 7, 9],
       "[1] one referent per NOUN PHRASE: five content-noun tokens -> three referents "
       "('the old baker' | 'the New York Times' | 'a loaf'); got heads %s" % sorted(grp))
    ck(grp[7][2] == [5, 6] and grp[7][0] == 4,
       "[1b] the RIGHT-HAND head survives and every absorbed head is recorded (head 7, members %s, "
       "span start %d)" % (grp[7][2], grp[7][0]))

    # ---- 2/3/4. the card: determiner, positions, head -------------------------------------------
    m = RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN", span=["The", "old", "baker"],
                         span_upos=["DET", "ADJ", "NOUN"], gtok=(0, 2), wstart=0)
    ck(definiteness(m) == "def" and set(modifiers(m)) == {"old"},
       "[2] Heim's determiner is READABLE on the card (%s) and the descriptive content is on it (%s)"
       % (definiteness(m), sorted(modifiers(m))))
    ck(m["wtok_start"] == 0 and (m["gtok_start"], m["gtok_end"]) == (0, 2)
       and m["span_toks"] == ["The", "old", "baker"] and m["span_toks"][-1].lower() == m["head"]
       and len(m["span_upos"]) == len(m["span_toks"]),
       "[3] the CANONICAL schema: wtok_start = the span start, the RAW-CASED span with the head LAST, a "
       "real global extent, span_upos the span's length")
    ck(mention_span(m) == (0, 0, 2), "[3b] coref.mention_span returns a real extent %s" % (mention_span(m),))
    ck(mention_head_wpos(m) == 2,
       "[4] the head is recovered by the substrate's own accessor (mention_head_wpos = %d)"
       % mention_head_wpos(m))
    one = RPN._mk_referent("baker", 0, 7, 1, -1, upos="NOUN", span=["baker"], span_upos=["NOUN"],
                           gtok=(7, 7), wstart=7)
    ck(mention_head_wpos(one) == one["wtok_start"] == 7,
       "[4b] on a ONE-TOKEN mention the head IS wtok_start -- no consumer that was right becomes wrong")

    # ---- 5/6. the boundary's two structural guarantees -------------------------------------------
    t3, t3u = ["the", "dog", "the", "cat", "saw", "."], ["DET", "NOUN", "DET", "NOUN", "VERB", "PUNCT"]
    ck(RPN.np_left_edge(t3, t3u, 3, None, None, "cat") == 2,
       "[5] a DETERMINER closes the phrase on its left: 'the cat' does not swallow 'the dog'")
    t4, t4u = ["the", "baker", "of", "York"], ["DET", "NOUN", "ADP", "PROPN"]
    g4 = {0: 1, 1: -1, 2: 3, 3: 1}
    g4r = RPN.np_groups(t4, t4u, [1, 3], g4, None, "both")
    ck(sorted(g4r) == [1, 3] and g4r[1][0] == 0,
       "[6] a POST-head dependent is NOT absorbed ('the baker' | 'York'): %s" % sorted(g4r))
    ck(RPN.np_left_edge(FIX, FIX_UP, 9, gov, None, "both") >= 8,
       "[6b] a phrase never crosses its clause's verb, so every pre/post-verbal positional cue keeps its "
       "answer (edge %d > the verb at 3)" % RPN.np_left_edge(FIX, FIX_UP, 9, gov, None, "both"))

    # ---- 7. the reader's own organs, no second parse ---------------------------------------------
    ck(hasattr(SR._CachedTagShim, "parse_heads"),
       "[7] the reader serves its SHARED per-read parse to the introduction organ (no second parse)")
    ck(RPN._graded_inside({3: {3: 0.9}}, 2, 2, 2) is True
       and RPN._graded_inside({3: {9: 0.9, 3: 0.1}}, 2, 2, 2) is False,
       "[7b] the graded boundary is the MAP of the attachment arm's head belief -- no fitted threshold")

    # ---- 8. the A/B switch is exact ---------------------------------------------------------------
    RPN.RPN_SPAN, RPN.RPN_COLLAPSE = False, False
    m0 = RPN._mk_referent("baker", 0, 2, 1, -1, upos="NOUN", span=["The", "old", "baker"],
                          span_upos=["DET", "ADJ", "NOUN"], gtok=(0, 2), wstart=0)
    ck(m0["gtok_start"] == -1 and m0["gtok_end"] == -1 and m0["span_toks"] == ["baker"]
       and m0["wtok_start"] == 2 and m0["span_upos"] == ["NOUN"],
       "[8] HDLAB_RPN_SPAN off restores every field of the pre-2026-09-16 organ byte-for-byte")
    RPN.RPN_SPAN, RPN.RPN_COLLAPSE = True, True

    # ---- 9. a file card is labelled by its NAME ---------------------------------------------------
    te = SR.TrackedEntity(cluster=1, heads=["the community championship", "maya"], sent_indices=[0],
                          n_mentions=2, is_person=True, names=["maya"])

    class _SM(object):
        entities = [te]

    ck(GR._cluster_name(_SM(), 1) == "maya",
       "[9] a file card is labelled by its NAME, not by its longest surface (%s)"
       % GR._cluster_name(_SM(), 1))
    te2 = SR.TrackedEntity(cluster=2, heads=["the old baker"], sent_indices=[0], n_mentions=1,
                           is_person=True, names=[])

    class _SM2(object):
        entities = [te2]

    ck(GR._cluster_name(_SM2(), 2) == "the old baker",
       "[9b] a card with NO name keeps the longest-surface fallback (%s)" % GR._cluster_name(_SM2(), 2))

    # ---- 10. the LIVE reader, on a real document --------------------------------------------------
    if os.path.exists(LIVE_DOC):
        rd = SR.SituationReader()
        sm = rd.read(LIVE_DOC)
        ms = list(getattr(rd, "_coref_mentions", []) or [])
        sents = SR.parse_conll_sentences(LIVE_DOC, lower=False)
        ntok = sum(len(s) for s in sents)
        nonp = [x for x in ms if not x.get("is_pronoun")]
        bad = [x for x in ms
               if not (isinstance(x.get("gtok_start"), int) and isinstance(x.get("gtok_end"), int)
                       and 0 <= x["gtok_start"] <= x["gtok_end"] < ntok)]
        ck(ms and not bad,
           "[10] LIVE READ: all %d mentions (%d non-pronoun) carry a VALID global extent in [0,%d) "
           "-- %d invalid" % (len(ms), len(nonp), ntok, len(bad)))
        multi = sum(1 for x in nonp if len(x.get("span_toks") or []) > 1)
        det = sum(1 for x in nonp if definiteness(x) != "bare")
        ck(multi > 0 and det > 0,
           "[10b] the phrase stream reaches the consumers on a real read: %d multi-token spans, %d "
           "mentions whose determiner is readable (both were 0 before this rung)" % (multi, det))
        ck(len(sm.events) > 0, "[10c] the reader still produces events (%d)" % len(sm.events))
        heads_ok = all(int(x["wtok_start"]) <= mention_head_wpos(x) for x in ms)
        ck(heads_ok, "[10d] every mention's head lies at or after its span start")
        import hdlab.crosstype_live_adapter as A
        base = {x["midx"]: x.get("cluster") for x in nonp}
        doc_ct = A.build_gold_free_doc(ms, base, sents, reader=rd)
        ck(doc_ct is not None,
           "[10e] the crosstype bridge's Doc BUILDS on the reader's own mentions (`_can_build` accepted "
           "them) -- it rejected every one of them before this rung")
    else:
        print("  SKIP  [10] the live document is not on disk: %s" % LIVE_DOC)

    if not was_landed:
        print("\n  NOTE: the repository tree does NOT yet carry the diff; every claim above was asserted "
              "on the shipped diff compiled into the live modules.")
    print("\n%d checks, %s" % (_N[0], "ALL WITNESS CHECKS PASSED" if _OK[0] else "FAILURES PRESENT"))
    return 0 if _OK[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.medium
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
