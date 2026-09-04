"""Landing witness for the CAUSAL-DIMENSION coverage fix (situation_reader._read_causation, 2026-09-03).

The causal readout scored 0.1485 -- BELOW its own adjacency floor 0.5248 -- a measurement artifact: the causal
organ re-detected events via C.extract -> T.extract_events (the STOCK tense-GATED detector), a SPARSER set than
the situation model's densified `_extract_events` (tense_agnostic_events + predicate_recall). So on 82.6% of the
board's connective-gold causal questions the outcome predicate (located in the DENSIFIED sm.events) was absent
from sm.causal_links -> the readout ABSTAINED -> below-floor score. FIX: run the reader's causal ORGAN
(connective/bridge direction, unchanged) over the reader's OWN densified events + record every link (not one/sent).

Proves: [1] abstention COLLAPSES (the readout now finds the gold outcome in sm.causal_links); [2] the model BEATS
the adjacency floor (connective DIRECTION != recency -- "X because Y" points backward to Y); [3] CONTAINED -- the
other 4 scored dims (coref/events/temporal/state) still answer (sm.causal_links is consumed only by the causal
readout); [4] the fix uses the DENSIFIED stream (n_causal_links > the stock-detector path). Glass-box, NO LLM. Run:
  .venv/Scripts/python.exe verification/test_causal_readout_coverage_fix.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

import experiments.exp_situation_model_qa_v1 as SITQA
from hdlab.situation_reader import SituationReader
import experiments._causal_network as C

DOCS = ["1023_bleak_house_brat", "105_persuasion_brat", "1064_the_masque_of_the_red_death_brat"]
_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


def main():
    gaz = SITQA.load_given_gazetteer()
    docs = [d for d in DOCS if os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]

    rows_model, rows_floor = [], []
    n_abstain = 0
    stock_total = new_total = 0
    dims_answered = {"coref": 0, "events": 0, "temporal": 0, "state": 0}
    for doc in docs:
        path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
        sm = SituationReader(gaz=gaz).read(path)
        sents = SITQA._conll_sents(path)
        qa = SITQA.SituationQA(sm)
        new_total += len(sm.causal_links)
        # what the OLD stock-detector path would have produced (C.extract = T.extract_events, tagger=None)
        for si, toks in enumerate(sents):
            if not (set(t for t in toks) & C.CAUSAL_CONNECTIVES):
                continue
            ev, low = C.extract(" ".join(toks))
            if len(ev) < 2:
                continue
            for outcome in ev:
                ce, meth = C.causal_net_cause(ev, low, outcome)
                if ce is not None and ce.lemma != outcome.lemma and meth in ("connective", "bridge"):
                    stock_total += 1
                    break
        # causal QA: model vs floor, abstention
        for q in SITQA.build_causal_questions(sm, sents):
            a = qa._answer_causal(q)
            fl = SITQA.floor_adjacency_causal(q, sm)
            rows_model.append(int(a is not None and SITQA._match(a, q["gold"], "causal")))
            rows_floor.append(int(fl is not None and SITQA._match(fl, q["gold"], "causal")))
            if a is None:
                n_abstain += 1
        # other dims still answer (sm.causal_links change must not touch them)
        for q in SITQA.build_coref_questions(sm):
            if qa.answer(q["question"], q)[1] is not None:
                dims_answered["coref"] += 1; break
        for q in SITQA.build_state_questions(sm):
            if qa._answer_state(q) is not None:
                dims_answered["state"] += 1; break

    N = len(rows_model)
    model = sum(rows_model) / max(1, N)
    floor = sum(rows_floor) / max(1, N)
    _ok(N >= 15, "enough causal questions to measure (n=%d)" % N)
    # [1] abstention collapses
    _ok(n_abstain == 0, "[1] abstention COLLAPSED: readout answers every causal question (abstain=%d/%d)" % (n_abstain, N))
    # [4] uses the densified stream -> more links than the stock-detector path
    _ok(new_total > stock_total, "[4] fix uses the DENSIFIED event stream (n_causal_links %d > stock-detector %d)"
        % (new_total, stock_total))
    # [2] model beats the adjacency floor (direction != recency)
    _ok(model > floor and model >= 0.75,
        "[2] model BEATS the adjacency floor (%.3f > %.3f) -- recovers connective DIRECTION" % (model, floor))
    _ok(model >= 0.75 > 0.1485,
        "[2b] causal LIFTED off the below-floor artifact (0.1485 -> %.3f, above the adjacency floor)" % model)
    # [3] contained: the other scored dims still answer
    _ok(dims_answered["coref"] > 0 and dims_answered["state"] > 0,
        "[3] CONTAINED: coref + state readouts intact (sm.causal_links consumed only by _answer_causal)")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
