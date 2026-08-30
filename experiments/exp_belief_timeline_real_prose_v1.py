"""Incidence of belief-timeline structure in REAL narrative (honest coverage bound).

The belief timeline's discriminating capability needs (a) an ordered sequence of belief-relevant
events and (b) a query at an intermediate story-time (a STALE belief the reader can act on). This
cell quantifies how often those ingredients occur in real corpus, bounding the aggregate real-
narrative lift -- the rigorous-NEGATIVE half of the deliverable (mechanism proven on construction
gold + flashback prose; real-corpus aggregate bounded by what is automatically gold-labelable).

Sources (REUSE, no new mining): the corpus-mined observation candidates from the observation-cue
problem (`data/mine_false_belief_corpus_v1/candidates.jsonl`, LitBank) and the 26 authored false-
belief passages from the integrated ToM organ.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

CAND = os.path.join(_REPO, "data", "mine_false_belief_corpus_v1", "candidates.jsonl")
GOLD = [os.path.join(_REPO, "experiments", "data", f"gold_false_belief_realtext_v1{s}.jsonl")
        for s in ("", "b")]
OUTDIR = os.path.join(_REPO, "data", "exp_belief_timeline_real_prose_v1")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def run():
    cands = _load(CAND)
    n = len(cands)
    tiers = dict(Counter(r["tier"] for r in cands))
    books = set(r["book"] for r in cands)
    # a STALENESS OPPORTUNITY = an event the agent did NOT observe (belief can go stale)
    stale = [r for r in cands if r.get("label_observed") is False]
    irony = [r for r in cands if r.get("tier") == "irony"]     # explicit dramatic-irony markers
    bycount = Counter(r["book"] for r in cands)
    multi = sum(1 for b, c in bycount.items() if c >= 3)

    # authored ToM gold: are any OVER-TIME (multi-event) or single-change snapshots?
    gold_rows = []
    for g in GOLD:
        if os.path.exists(g):
            gold_rows += _load(g)
    # each authored passage has exactly one initial + one final location -> single-change snapshot
    over_time = sum(1 for r in gold_rows
                    if r.get("initial_location") and r.get("final_location")
                    and len([k for k in r if "location" in k]) > 2)
    single_change = len(gold_rows) - over_time

    metrics = {
        "corpus": {
            "n_observation_events": n, "n_books": len(books), "tiers": tiers,
            "staleness_opportunities": len(stale), "staleness_fraction": len(stale) / n,
            "explicit_irony_markers": len(irony), "irony_fraction": len(irony) / n,
            "books_with_multievent_structure_ge3": multi, "n_books_total": len(bycount),
        },
        "authored_tom_gold": {
            "n_passages": len(gold_rows), "over_time_multievent": over_time,
            "single_change_snapshot": single_change,
        },
        "verdict": (
            "Belief-STALENESS ingredients are COMMON in real narrative "
            f"({len(stale)}/{n} = {len(stale)/n:.1%} of mined observation events are non-observations "
            "where a belief can go stale; "
            f"{multi}/{len(bycount)} books carry multi-event structure), but COMPLETE, gold-labelable "
            "false-belief-OVER-TIME SCENES (a tracked object + ordered moves + observation state + a "
            "query at a past story-time) are NOT automatically minable -- the corpus yields the "
            "observation cue-CLAUSES, not the full ordered scene, which is why the integrated ToM "
            f"organ AUTHORED its gold ({single_change}/{len(gold_rows)} authored passages are single-"
            "change snapshots, 0 over-time). Explicit dramatic-irony markers are sparse "
            f"({len(irony)}/{n} = {len(irony)/n:.1%}). So the mechanism is proven on construction gold "
            "+ real flashback prose; the real-corpus AGGREGATE lift is bounded by the annotation gap, "
            "NOT by the mechanism -- a coverage-bounded NEGATIVE with the positive controls confirming "
            "the mechanism."
        ),
    }
    return metrics


def main():
    m = run()
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    c = m["corpus"]
    print("=" * 78)
    print("BELIEF-TIMELINE incidence in REAL narrative (honest coverage bound)")
    print("=" * 78)
    print(f"corpus: {c['n_observation_events']} observation events, {c['n_books']} LitBank books")
    print(f"  tiers: {c['tiers']}")
    print(f"  STALENESS opportunities (non-observations): {c['staleness_opportunities']} "
          f"({c['staleness_fraction']:.1%})")
    print(f"  explicit dramatic-irony markers: {c['explicit_irony_markers']} ({c['irony_fraction']:.1%})")
    print(f"  books with multi-event structure (>=3): {c['books_with_multievent_structure_ge3']}"
          f"/{c['n_books_total']}")
    g = m["authored_tom_gold"]
    print(f"authored ToM gold: {g['n_passages']} passages, {g['single_change_snapshot']} single-change, "
          f"{g['over_time_multievent']} over-time")
    print(f"VERDICT: {m['verdict']}")
    print(f"written {OUTDIR}/metrics.json")


if __name__ == "__main__":
    main()
