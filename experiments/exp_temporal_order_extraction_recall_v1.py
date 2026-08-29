"""Quantify the TENSE-EXTRACTION wall for the temporal-order register (the real-prose precision cap).

The ordering LOGIC is provably correct on clean cues (construction gold 1.000); the real-prose residual is
TENSE EXTRACTION -- the shared extractor's fixed 3-token had-window misses pluperfects whose participle is
far from 'had' (inversion / long subjects / adverbs). The brain binds 'had' to its participle via a
CLAUSE-LEVEL syntactic dependency. This cell measures HOW BIG the wall is and HOW MUCH the brain-faithful
clause-binder closes it, against a dependency-parse REFERENCE (spaCy en_core_web_sm: a participle whose
'had' is an aux child == a pluperfect).

Arms compared for PLUPERFECT RECALL vs the spaCy reference (on real LitBank prose):
  WINDOW   the shared fixed 3-token had-lookback (experiments/_temporal_ordering[_multiframe])
  CLAUSE   + promote_clause_pluperfect (brain-faithful clause-level aux->participle binding)

CAVEAT (stated, not hidden): spaCy is a MODERN parser and itself ERRS on archaic 19th-century syntax
(e.g. it mis-parses "had the paragraph originally stood" -- the inverted pluperfect -- as a ccomp, which
the CLAUSE binder actually gets). So this is agreement-with-an-imperfect-reference, a LOWER bound on the
true wall, not ground truth. spaCy runs LOCALLY only (remote has no spaCy) -> inline, bounded novel count.

ASCII-only. Deterministic. Diagnostic (no HARD_PASS gate) -- reports the recall numbers.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_order_register as R           # noqa: E402
from experiments import _temporal_ordering_multiframe as M       # noqa: E402

ANCHOR = "temporal_order_extraction_recall_v1"


def _spacy_pluperfects(nlp, text):
    """Return spaCy pluperfects split into EVENT vs COPULAR/stative. A pluperfect = a participle whose
    child is an aux 'had'. COPULAR/stative = 'had been X' (been / a be-lemma participle / an auxpass
    child) -- a prior STATE, not an orderable event (the dropped perfect-aspect resultant-state channel).
    EVENT = a genuine event participle (the ordering-relevant subset). Returns (event_set, copular_set)."""
    doc = nlp(text)
    events, copular = [], []
    for t in doc:
        aux_had = any((c.dep_ == "aux" and c.text.lower() == "had") for c in t.children)
        if not (aux_had and t.tag_ in ("VBN", "VBD")):
            continue
        p = t.text.lower().strip(".,;:'\"!?")
        is_cop = (p == "been") or (t.lemma_ == "be") or any(c.dep_ == "auxpass" for c in t.children)
        (copular if is_cop else events).append(p)
    return events, copular


def _my_pp(text, clause):
    """Lemmas my extractor marks past-perfect (clause=False: fixed window; True: + clause binder)."""
    ev, tg = M.extract_events_punct(text)
    if clause:
        ev = R.promote_clause_pluperfect(ev, tg)
    return {e.lemma for e in ev if e.is_pp}


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def main(max_files=10, max_sents_per_file=1500):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    from hdlab.scene_segment import parse_conll_sentences
    files = sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "litbank_coref_conll", "*.conll")))[:max_files]

    t0 = time.perf_counter()
    n_event = n_copular = 0                 # spaCy-reference pluperfects, split
    hit_event_w = hit_event_c = 0           # EVENT-pluperfect recall (the ordering-relevant subset)
    n_clause_only = 0                        # clause binder catches an EVENT the window misses
    n_sents = 0
    examples_closed, examples_copular = [], []
    for fp in files:
        try:
            sents = parse_conll_sentences(fp)
        except Exception:
            continue
        for toks in sents[:max_sents_per_file]:
            if "had" not in [t.lower() for t in toks]:
                continue
            text = " ".join(toks)
            n_sents += 1
            ev_ref, cop_ref = _spacy_pluperfects(nlp, text)
            n_copular += len(cop_ref)
            if cop_ref and len(examples_copular) < 12:
                examples_copular.append({"text": text[:160], "stative_pp": sorted(set(cop_ref))})
            if not ev_ref:
                continue
            mw = _my_pp(text, False)
            mc = _my_pp(text, True)
            for p in ev_ref:
                n_event += 1
                inw, inc = p in mw, p in mc
                hit_event_w += int(inw)
                hit_event_c += int(inc)
                if inc and not inw:
                    n_clause_only += 1
                    if len(examples_closed) < 12:
                        examples_closed.append({"text": text[:160], "participle": p})
    elapsed = time.perf_counter() - t0
    n_ref = n_event + n_copular
    rec_w = hit_event_w / n_event if n_event else 0.0
    rec_c = hit_event_c / n_event if n_event else 0.0
    copular_frac = n_copular / n_ref if n_ref else 0.0
    metrics = {
        "verdict": "MEASURED",
        "summary": (f"On {n_sents} real LitBank 'had'-sentences ({n_ref} spaCy-reference pluperfects): "
                    f"{copular_frac:.0%} are COPULAR/stative 'had been X' (a prior STATE, not an orderable event "
                    f"-- the DROPPED perfect-aspect resultant-state channel). EVENT-pluperfect recall (the "
                    f"ordering-relevant {n_event}): fixed-WINDOW {rec_w:.3f}, +CLAUSE-binder {rec_c:.3f} "
                    f"(+{rec_c - rec_w:.3f}; clause closes {n_clause_only} window-misses). So the tense-EXTRACTION "
                    f"wall for EVENT ordering is small (~{1 - rec_c:.0%} residual); the big 'had' opportunity is "
                    f"the stative resultant-state channel (an ADJACENT dimension, not TIME)."),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "n_files": len(files), "n_had_sentences": n_sents, "n_reference_pluperfects": n_ref,
        "copular_stative_pluperfect_frac": round(copular_frac, 4), "n_copular": n_copular, "n_event": n_event,
        "event_pluperfect_recall_fixed_window": round(rec_w, 4),
        "event_pluperfect_recall_clause_binder": round(rec_c, 4),
        "recall_gain_from_clause_binder": round(rec_c - rec_w, 4),
        "n_event_window_misses_closed_by_clause": n_clause_only,
        "examples_window_miss_closed_by_clause": examples_closed,
        "examples_copular_stative_dropped_channel": examples_copular,
        "caveat": ("spaCy en_core_web_sm errs on archaic 19c syntax (it mis-parses some inverted pluperfects the "
                   "clause binder gets) -> EVENT recall vs this reference is a LOWER bound. The dropped "
                   "copular/stative pluperfect ('had been an excellent woman') is the perfect-ASPECT resultant/"
                   "prior-STATE channel -- feeds the ENTITY/STATE dimension, a mapped NEXT-PROBLEM, not TIME."),
    }
    _atomic_write(_out_dir(), metrics)
    print(metrics["summary"])
    print(f"elapsed={elapsed:.1f}s -> {os.path.join(_out_dir(), 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        # tiny self-test: the clause binder must recall the inverted pluperfect the window misses
        w = _my_pp("precisely such had the paragraph originally stood from the printer hands", False)
        c = _my_pp("precisely such had the paragraph originally stood from the printer hands", True)
        assert "stood" not in w and "stood" in c, f"clause binder should close the window miss: w={w} c={c}"
        print("[self-test] PASS"); sys.exit(0)
    smoke = "--smoke" in sys.argv
    try:
        main(max_files=(2 if smoke else 12), max_sents_per_file=(300 if smoke else 1500))
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
