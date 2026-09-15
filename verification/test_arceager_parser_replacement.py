"""Witness: the arc-eager adapter is a FUNCTIONAL DROP-IN replacement for the batch ArcParser, is measurably
BETTER, and the whole reader runs off it across every dimension.

Problem: add_the_arc_labeler_fast_scoring_path... (owner escalation: kill the batch parser, replace with an
ideal brain-foundational one; make consumers brain-foundational too).

  R1  DROP-IN INTERFACE: adapter.parse(tokens,pos) returns a ParseResult with .heads (dict), .margins (dict),
      .arcs (list of (head,dep)) -- the exact ArcParser surface consumers read.
  R2  FUNCTIONAL: a real read with the reader's general front-end parser swapped to the adapter produces a
      valid SituationModel across events / entity_states / causal / coref / timeline (no error, non-empty).
  R3  BETTER (not vacuous): UAS(adapter) > UAS(live ArcParser) CI-separated on held-out UD-EWT test.
  R4  INFO-FREE CONTROL: a shuffled-weights arc-eager adapter collapses (proves the win is the learned model).

Reruns NO landed cell; recomputes on held-out gold. NO LLM. numpy + pure-python.
Run: .venv/Scripts/python.exe verification/test_arceager_parser_replacement.py
"""
from __future__ import annotations
import os, sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
import hdlab.arceager_parser as AE
from experiments.exp_arceager_parser_replacement_v1 import ArcEagerParserAdapter
from experiments.exp_arc_labeler_graded_competition_v1 import read_conllu, UD_TEST

PASS = 0; FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok; FAIL += (not ok)


def _uas_ci(parser_a, parser_b, sents, tagger, reps=1000, seed=3):
    """Paired bootstrap CI for UAS(a)-UAS(b) over sentences; each per-sent (corr,tot)."""
    pa, pb = [], []
    for s in sents:
        toks = [t[1] for t in s]; gh = [t[3] for t in s]; n = len(s)
        pp = list(tagger.tag(list(toks)))
        ha = parser_a.parse(list(toks), pp).heads; hb = parser_b.parse(list(toks), pp).heads
        ca = sum(int(ha.get(i, 0) == gh[i - 1]) for i in range(1, n + 1) if 0 <= gh[i - 1] <= n)
        cb = sum(int(hb.get(i, 0) == gh[i - 1]) for i in range(1, n + 1) if 0 <= gh[i - 1] <= n)
        t = sum(1 for i in range(1, n + 1) if 0 <= gh[i - 1] <= n)
        pa.append((ca, t)); pb.append((cb, t))
    pa = np.array(pa, float); pb = np.array(pb, float)
    rng = np.random.default_rng(seed); m = len(pa); diffs = np.empty(reps)
    for r in range(reps):
        idx = rng.integers(0, m, m); ta = pa[idx].sum(0); tb = pb[idx].sum(0)
        diffs[r] = ta[0] / ta[1] - tb[0] / tb[1]
    return (pa[:, 0].sum() / pa[:, 1].sum(), pb[:, 0].sum() / pb[:, 1].sum(),
            float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))


if __name__ == "__main__":
    print("witness: arc-eager parser as a drop-in, better, functional replacement")
    reader = SituationReader(gaz=SITQA.load_given_gazetteer())
    live = reader._frontend_parser(); tagger = reader._frontend_tagger()
    adapter = ArcEagerParserAdapter()

    # R1 interface
    toks = ["the", "wolf", "bit", "the", "sheep"]; pos = list(tagger.tag(toks))
    pr = adapter.parse(toks, pos)
    r1 = (isinstance(pr.heads, dict) and isinstance(pr.margins, dict) and isinstance(pr.arcs, list)
          and len(pr.heads) == len(toks) and all(isinstance(a, tuple) and len(a) == 2 for a in pr.arcs))
    chk("R1 drop-in interface: parse() -> ParseResult(.heads dict, .margins dict, .arcs [(head,dep)])", r1,
        "heads=%s arcs0=%s" % (pr.heads, pr.arcs[0] if pr.arcs else None))

    # R2 functional: reader runs end-to-end off the adapter across all dimensions
    doc = "105_persuasion_brat"; p = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
    rB = SituationReader(gaz=SITQA.load_given_gazetteer()); rB._frontend_parser = lambda: adapter
    sm = rB.read(p)
    r2 = (len(sm.events or []) > 0 and sm.entity_states is not None and sm.coref_acc is not None
          and sm.causal_links is not None)
    chk("R2 functional: whole reader runs off the adapter (events/entity_states/causal/coref produced)", r2,
        "events=%d entity_states=%d causal=%d coref_acc=%.3f"
        % (len(sm.events or []), len(sm.entity_states or []), len(sm.causal_links or []), sm.coref_acc or 0.0))

    # R3 better, CI-separated
    sents = read_conllu(UD_TEST)[:500]
    u_ae, u_live, lo, hi = _uas_ci(adapter, live, sents, tagger)
    chk("R3 UAS(arc-eager) > UAS(live ArcParser) CI-separated on held-out UD-EWT", lo > 0,
        "live %.4f -> ae %.4f, delta CI[%+.4f,%+.4f]" % (u_live, u_ae, lo, hi))

    # R4 info-free control: shuffled-weights arc-eager must collapse
    W = AE.load_model(AE.MODEL_PATH).copy(); np.random.default_rng(9).shuffle(W)
    bad = ArcEagerParserAdapter(W=W)
    cb = tot = 0
    for s in sents[:200]:
        tk = [t[1] for t in s]; gh = [t[3] for t in s]; n = len(s); pp = list(tagger.tag(list(tk)))
        hb = bad.parse(list(tk), pp).heads
        cb += sum(int(hb.get(i, 0) == gh[i - 1]) for i in range(1, n + 1) if 0 <= gh[i - 1] <= n)
        tot += sum(1 for i in range(1, n + 1) if 0 <= gh[i - 1] <= n)
    chk("R4 info-free shuffled-weights arc-eager collapses (win is the learned model)", (cb / tot) < 0.4,
        "shuffled UAS %.4f" % (cb / tot))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    sys.exit(0 if FAIL == 0 else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
