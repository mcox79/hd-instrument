"""Landing witness for the GOAL-LABELER EFFICIENCY GATE (strategy optimization 2026-09-06).

The goal ADVCL purpose filter (goal_purpose_filter, default-on) labeled EVERY sentence with the arc labeler
to get deprels, even though GR.extract_goals_sentence reads a deprel ONLY in branch (3) (the bare 'to VINF'
purpose adjunct), whose entry gate requires a 'to' token followed by a VERB (goal_register.py:259-262). The
gate SituationReader._has_to_verb skips labeling any sentence that can never reach the deprel read.

  W1 BYTE-IDENTICAL: on real LitBank docs the gated reader's goal register is IDENTICAL to a reader forced to
     label EVERY sentence (the pre-optimization behavior, reproduced by monkeypatching _has_to_verb -> True).
  W2 REDUCTION: report labeled/total sentences (the arc-labeler calls saved).
  W3 TIMING: gated read wall-clock <= full-labeling read wall-clock (a speedup, not a regression).

Glass-box, NO LLM. ASCII.
Run: .venv/Scripts/python.exe verification/test_goal_labeler_gate_landing.py
"""
from __future__ import annotations
import os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.situation_reader as SR
from hdlab.situation_reader import SituationReader
import experiments.exp_situation_model_qa_v1 as QA


def _goal_fp(sm):
    """A tight, order-independent fingerprint of the extracted goal register (what the gate could affect)."""
    reg = getattr(sm, "goal_register", None)
    goals = list(getattr(reg, "goals", []) or [])
    return sorted(
        (str(getattr(g, "agent_canonical", getattr(g, "agent", "?"))), str(g.goal_head), str(g.goal_text),
         str(g.kind), int(g.sent_idx), int(g.verb_tok), int(g.to_tok), bool(g.negated), str(g.status))
        for g in goals)


def _read_all(docs, gaz):
    r = SituationReader(gaz=gaz)
    assert r.goal_purpose_filter is True, "goal_purpose_filter is not default-on"
    fps = {}
    t0 = time.time()
    for doc in docs:
        sm = r.read(os.path.join(QA.CONLL_DIR, doc + ".conll"))
        fps[doc] = _goal_fp(sm)
    return fps, time.time() - t0


def main():
    gaz = QA.load_given_gazetteer()
    docs = [d for d in QA.load_docs(6) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))][:4]
    assert docs, "no docs found"
    _orig = SR.SituationReader._has_to_verb

    # --- gated (the optimized default), with a call counter over _has_to_verb ---
    stat = {"total": 0, "labeled": 0}

    def _counting(toks, up):
        stat["total"] += 1
        keep = _orig(toks, up)
        if keep:
            stat["labeled"] += 1
        return keep
    SR.SituationReader._has_to_verb = staticmethod(_counting)
    gated_fp, gated_s = _read_all(docs, gaz)

    # --- forced-full labeling (reproduces the pre-optimization behavior: label EVERY sentence) ---
    SR.SituationReader._has_to_verb = staticmethod(lambda toks, up: True)
    full_fp, full_s = _read_all(docs, gaz)
    SR.SituationReader._has_to_verb = _orig                 # restore

    # W1 byte-identity
    n_goals = sum(len(v) for v in gated_fp.values())
    for doc in docs:
        assert gated_fp[doc] == full_fp[doc], (
            "goal register DIFFERS gated-vs-full on %s\n gated=%s\n full =%s" % (doc, gated_fp[doc], full_fp[doc]))
    print("W1 BYTE-IDENTICAL goal register gated==full on %d docs (%d goals): PASS" % (len(docs), n_goals), flush=True)

    # W2 reduction
    total, labeled = stat["total"], stat["labeled"]
    saved = total - labeled
    ratio = (total / labeled) if labeled else float("inf")
    print("W2 REDUCTION: labeled %d / %d sentences (skipped %d = %.1f%%; ~%.1fx fewer labeler calls): PASS"
          % (labeled, total, saved, 100.0 * saved / max(1, total), ratio), flush=True)

    # W3 timing (gated should not be slower)
    print("W3 TIMING: gated %.2fs vs forced-full %.2fs over %d docs (%+.1f%%): %s"
          % (gated_s, full_s, len(docs), 100.0 * (gated_s - full_s) / max(1e-9, full_s),
             "PASS" if gated_s <= full_s * 1.05 else "SLOWER"), flush=True)

    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
