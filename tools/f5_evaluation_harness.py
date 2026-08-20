"""Score ANY anomaly-detector against the replicated floor -- **and refuse to report if the
mandatory diagnostics fail.**

**WHY A HARNESS RATHER THAN A CHECKLIST.** `F5_EVALUATION_DESIGN_...md` lists four diagnostics that
must print BEFORE any verdict is read. **Every caution written as prose in this repo has eventually
been violated; every control written as code has caught something** -- so the diagnostics are
preconditions in a function, not items in a document. `score_detector()` RAISES rather than
returning a number when the instrument is not in a state where a number would mean anything.

**THE INTERFACE THE F5 CELL IMPLEMENTS IS ONE FUNCTION:**

    detector(tokens: list[str], position: int) -> float     # HIGHER = more anomalous

That is all. The harness owns the items, the leak control, the pairing, the CIs, the floor and the
replication gate, so a cell cannot accidentally re-implement any of them differently.

**THE READ-OUT IS THE PAIRED DIFFERENCE, NOT THE RANK.** Measured 2026-08-21: second-order counting
ranks the anomalous slot FIRST on a median item -- and ranks the SAME slot first **42.6% of the time
when the word is CORRECT.** Absolute rank is inflated by the slot for EVERY arm, so
`hit@1(anomalous) - hit@1(original)` on the same items and slots is the only metric slot effects
cannot game.

**THE BAR, both counting floors replicated across four independently-built sets, measured THROUGH
THIS HARNESS:** first-order `+23.3/+23.5/+22.5/+25.2`, second-order `+28.3/+29.4/+35.0/+29.4`, both
`REPLICATED`. Per-set CI upper bounds peak at **+44.2 pp**, and the standing rule gates on the
floor's UPPER bound, never its point value.

**WHAT THIS FILE DOES NOT DO: implement F5.** It cannot say whether a coherence monitor works; it
can only say whether a given detector beats counting on a fair, controlled task.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FLOOR_BAR_PP = 44.2
# Max per-set CI UPPER bound across BOTH counting floors, 4 sets each, measured THROUGH THIS HARNESS
# by tools/measure_counting_floors_through_the_harness.py. First-order: +23.3/+23.5/+22.5/+25.2.
# Second-order: +28.3/+29.4/+35.0/+29.4. Both REPLICATED; second-order is the stronger floor, as
# this project's standing position predicted.
# THE BAR HAS MOVED THREE TIMES AND EVERY MOVE WAS UPWARD, each from a defect found in my own
# instrument: rank-4.0 -> +18.8 (wrong metric: rank is slot-inflated) -> +20.7 (single set, not
# replicated) -> +44.2 (surface-vs-lemma lookup bug deflating both floors). Never weaken a gate.
MIN_DISTINCT_SCORES = 8      # G2 shipped a sign()-quantised residual; no threshold could work
MIN_ITEMS = 40


class DiagnosticFailure(RuntimeError):
    """Raised INSTEAD OF returning a score. The instrument is not in a state where a number means
    anything, and a number returned anyway is how a dead gate got reported as a null."""


def _word(tok):
    return "".join(c for c in tok.lower() if c.isalpha())


def _load(set_path):
    return json.load(open(set_path, encoding="utf-8"))["items"]


class _ContentWords:
    """Membership test for 'is this token a content word', via the repo's own `content_lemmas`.

    Arm-independent by construction: the slate every detector is ranked over comes from the
    tokeniser the substrate itself uses, not from any detector's vocabulary."""

    def __init__(self):
        self._cache = {}

    def __contains__(self, w):
        if not w:
            return False
        hit = self._cache.get(w)
        if hit is None:
            from hdlab.reading_grounding_loop import content_lemmas
            hit = bool(content_lemmas(w))
            self._cache[w] = hit
        return hit


_content = _ContentWords()


def check_diagnostics(scores_by_item, name="detector"):
    """The four mandatory diagnostics, as PRECONDITIONS. Returns a report dict or raises.

    These exist because G2 shipped without them and **a gate that fired zero times was reported as
    a null result** -- the most expensive shape of error available here."""
    flat = [s for row in scores_by_item for s in row]
    if not flat:
        raise DiagnosticFailure("%s produced NO scores at all" % name)
    distinct = len(set(round(float(s), 12) for s in flat))
    rep = {"n_items": len(scores_by_item), "n_scores": len(flat), "distinct_values": distinct}

    # 1. THE ERROR DISTRIBUTION -- a sign-quantised signal collapses to a handful of values
    if distinct < MIN_DISTINCT_SCORES:
        raise DiagnosticFailure(
            "%s: only %d DISTINCT score values across %d scores. A quantised or constant signal "
            "cannot support any threshold; this is a reachability failure, not a null. "
            "(G2 shipped exactly this and its gate fired 0.00 times.)" % (name, distinct, len(flat)))

    # 2. THE FIRING RATE at the item level must not be degenerate
    top = [int(np.argmax(row)) for row in scores_by_item if len(row) > 1]
    n_distinct_top = len(set(top))
    rep["distinct_argmax_positions"] = n_distinct_top
    rep["n_scored_items"] = len(top)
    # Scale with the item count rather than a magic fraction: a detector reading POSITION rather
    # than content puts the arg-max on the same INDEX every time, so the distinct count stays ~1
    # however many items there are. (The first version used `spread < 0.02` and a 50-item
    # all-same-index fixture landed on EXACTLY 0.02 and slipped through -- caught by the
    # self-test, which is the entire reason the self-test constructs the failures rather than
    # asserting the healthy case.)
    if top and n_distinct_top <= max(1, 0.05 * len(top)):
        raise DiagnosticFailure(
            "%s: the arg-max lands on only %d distinct position index(es) across %d items -- the "
            "detector is reading POSITION, not content." % (name, n_distinct_top, len(top)))

    # 3. TIE MASS, treatment included -- non-zero is not non-degenerate
    ties = [sum(1 for s in row if abs(s - max(row)) < 1e-12) / len(row)
            for row in scores_by_item if row]
    rep["mean_tie_mass"] = round(float(np.mean(ties)), 4)
    if rep["mean_tie_mass"] > 0.5:
        raise DiagnosticFailure(
            "%s: mean tie mass %.3f. A rank/hit metric over a score column with mass on one value "
            "counts every tie as beaten -- the LESS the arm knows, the better it scores. "
            "(A 10-sparse random arm beat a real one this way.)" % (name, rep["mean_tie_mass"]))
    return rep


def positive_control(detector, items):
    """**PROVE THE DETECTOR CAN FIRE AT ALL** before believing any null from it.

    A grotesque swap MUST score above the word it replaced. *An instrument never shown to fire
    cannot support a negative result.*

    **BUILT FROM THE ITEM SET, NOT FROM A HAND-WRITTEN SENTENCE.** The first version used
    "the cat sat on the warm mat" -> "bulldozer", and the KNOWN-GOOD floor failed it -- because
    `bulldozer` does not occur in the 8,000-sentence sample, so the detector could not score it at
    all. **A control whose probe lies outside the detector's world tests the corpus, not the
    detector.** Every word in the item set is corpus-present by construction, so drawing the swap
    from distant items removes that whole failure mode. Majority vote over several probes, because
    any single sentence can happen to accept an odd word.
    """
    trials, wins = [], 0
    n = len(items)
    # PROBE ONLY THE FIRST HALF. With `donor = (k + n//2) % n` over the WHOLE range, hosts and
    # donors SWAP ROLES on the back half -- item A donates to B and B donates to A -- so any
    # detector that scores a word the same way in both directions gets EXACTLY 50% and can never
    # pass a majority vote, however good it is. On a 120-item set the probes never reach the wrap
    # so it never showed; that is luck, not design. Caught by the self-test on a small fixture.
    for k in range(min(9, n // 2)):
        host = items[k]
        donor = items[k + n // 2]                 # a topically distant item, never a host here
        toks = host["sentence_original"].split()
        i = host["anomaly_token_index"]
        if i >= len(toks):
            continue
        swapped = list(toks)
        swapped[i] = donor["target"]
        s_ok, s_bad = float(detector(toks, i)), float(detector(swapped, i))
        trials.append({"coherent": s_ok, "swapped": s_bad, "word": donor["target"]})
        wins += (s_bad > s_ok)
    if not trials:
        raise DiagnosticFailure("POSITIVE CONTROL could not be constructed from the item set")
    if wins * 2 <= len(trials):
        raise DiagnosticFailure(
            "POSITIVE CONTROL FAILED: an out-of-context word scored higher than the correct word in "
            "only %d of %d probes. The detector has not been shown to fire, so it cannot support a "
            "null. Sample: %s" % (wins, len(trials), trials[:3]))
    return {"probes": len(trials), "fired": wins, "examples": trials[:3]}


def score_detector(detector, set_path, *, seed=17, n_boot=20000, name="detector", verbose=True):
    """Paired hit@1 discrimination for `detector` on one item set. Raises on any diagnostic failure.

    Returns {'discrimination_pp', 'ci', 'hit_anom', 'hit_orig', 'n', 'diagnostics', ...}."""
    from rank_with_ties import rank_with_ties

    items = _load(set_path)
    if len(items) < MIN_ITEMS:
        raise DiagnosticFailure("only %d items -- UNDERPOWERED, refusing to score" % len(items))
    pc = positive_control(detector, items)

    per_field, hits = {}, {}
    for field in ("sentence_anomalous", "sentence_original"):
        rows, hit = [], []
        for it in items:
            toks = it[field].split()
            # CANDIDATES ARE CHOSEN BY THE HARNESS, NOT BY THE DETECTOR, and by the repo's own
            # content-word test so every arm is ranked over an IDENTICAL slate. Letting a detector
            # define its own candidates would let it duck the words it cannot score.
            # The first version used "any token with letters", which put FUNCTION words on the
            # slate -- ~20 candidates instead of ~9 -- and the known-good floor scored 0.0%
            # with a ZERO-WIDTH CI, which is a reachability failure, not a null.
            cand = sorted({j for j, t in enumerate(toks) if _word(t) in _content}
                          | {it["anomaly_token_index"]})
            if len(cand) < 3:
                continue
            sc = [float(detector(toks, j)) for j in cand]
            rows.append(sc)
            r = rank_with_ties(sc, cand.index(it["anomaly_token_index"]))
            hit.append(r.pessimistic == 1)      # PESSIMISTIC: ties count AGAINST the detector
        per_field[field] = check_diagnostics(rows, "%s/%s" % (name, field))
        hits[field] = hit

    A, B = hits["sentence_anomalous"], hits["sentence_original"]
    n = min(len(A), len(B))
    A, B = A[:n], B[:n]
    ha, hb = 100.0 * sum(A) / n, 100.0 * sum(B) / n
    rng = random.Random(seed)
    pairs = list(zip(A, B))
    d = []
    for _ in range(n_boot):
        smp = [pairs[rng.randrange(n)] for _ in range(n)]
        d.append(100.0 * (sum(a for a, _ in smp) - sum(b for _, b in smp)) / n)
    lo, hi = (float(x) for x in np.percentile(d, [2.5, 97.5]))
    out = {"set": os.path.basename(set_path), "n": n, "hit_anom_pct": round(ha, 2),
           "hit_orig_pct": round(hb, 2), "discrimination_pp": round(ha - hb, 2),
           "ci": [round(lo, 2), round(hi, 2)], "positive_control": pc,
           "diagnostics": per_field, "beats_floor_upper_bound": (ha - hb) > FLOOR_BAR_PP,
           "floor_bar_pp": FLOOR_BAR_PP}
    if verbose:
        print("[%s] %s: anom %.1f%% - orig %.1f%% = %+.1f pp, CI [%+.1f, %+.1f]  (bar %+.1f) -> %s"
              % (name, out["set"], ha, hb, ha - hb, lo, hi, FLOOR_BAR_PP,
                 "CLEARS" if out["beats_floor_upper_bound"] else "does not clear"))
    return out


def score_across_sets(detector, set_paths, *, name="detector"):
    """Run every set and put the effects through `replication_gate`. **A single set is a hypothesis.**"""
    from replication_gate import replication_verdict
    res = [score_detector(detector, p, name=name) for p in set_paths]
    eff = [r["discrimination_pp"] for r in res]
    v = replication_verdict(eff, lower_is_better=False)
    worst_ub = max(r["ci"][1] for r in res)
    print("\nreplication: %s" % v.verdict)
    print("  per-set discrimination: %s" % ", ".join("%+.1f" % e for e in eff))
    print("  BAR (floor's max per-set CI upper bound): %+.1f pp" % FLOOR_BAR_PP)
    verdict = ("CLEARS THE FLOOR" if (v.verdict == "REPLICATED" and min(eff) > FLOOR_BAR_PP)
               else "DOES NOT CLEAR")
    print("  VERDICT: %s  (detector's own worst CI upper bound %+.1f)" % (verdict, worst_ub))
    return {"per_set": res, "replication": v.verdict, "verdict": verdict, "effects": eff}


def compare_detectors_paired(det_a, det_b, set_paths, *, name_a="A", name_b="B", seed=23,
                             n_boot=20000):
    """Is arm A's discrimination different from arm B's, **on the same items**?

    **THIS ANSWERS A QUESTION `score_across_sets` CANNOT.** Two arms can each have a CI, and those
    CIs can OVERLAP, without that meaning the arms are indistinguishable -- overlapping marginal
    intervals are not a test of a difference. Reporting "we lose to counting" from two separate runs
    would be the scorer-crossing this repo's rules forbid.

    The paired quantity per item is `(anom_A - orig_A) - (anom_B - orig_B)`, each term a 0/1 hit, so
    it lives in {-2,-1,0,1,2} and every item contributes its own difference. Bootstrap over ITEMS."""
    from rank_with_ties import rank_with_ties

    per_item = []
    for sp in set_paths:
        items = _load(sp)
        hits = {}
        for label, det in ((name_a, det_a), (name_b, det_b)):
            for field in ("sentence_anomalous", "sentence_original"):
                row = []
                for it in items:
                    toks = it[field].split()
                    cand = sorted({j for j, t in enumerate(toks) if _word(t) in _content}
                                  | {it["anomaly_token_index"]})
                    if len(cand) < 3:
                        row.append(None)
                        continue
                    sc = [float(det(toks, j)) for j in cand]
                    r = rank_with_ties(sc, cand.index(it["anomaly_token_index"]))
                    row.append(r.pessimistic == 1)
                hits[(label, field)] = row
        for k in range(len(items)):
            v = [hits[(lab, f)][k] for lab in (name_a, name_b)
                 for f in ("sentence_anomalous", "sentence_original")]
            if any(x is None for x in v):
                continue
            per_item.append((int(v[0]) - int(v[1])) - (int(v[2]) - int(v[3])))

    n = len(per_item)
    if n < MIN_ITEMS:
        raise DiagnosticFailure("only %d paired items -- UNDERPOWERED" % n)
    mean = float(np.mean(per_item))
    rng = random.Random(seed)
    boot = [float(np.mean([per_item[rng.randrange(n)] for _ in range(n)])) for _ in range(n_boot)]
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    sep = lo > 0 or hi < 0
    print("PAIRED %s - %s over %d items: %+.3f per item, 95%% CI [%+.3f, %+.3f]"
          % (name_a, name_b, n, mean, lo, hi))
    print("  -> %s" % ("SEPARATED: the CI excludes zero, so the arms differ" if sep else
                       "NOT SEPARATED: the CI includes zero. **This is a null, not a tie** -- it "
                       "says the difference is unresolved at this n, not that the arms are equal."))
    return {"n": n, "mean_diff": round(mean, 4), "ci": [round(lo, 4), round(hi, 4)],
            "separated": sep, "a": name_a, "b": name_b}


def _self_test():
    """Positive AND negative controls on the HARNESS ITSELF.

    A harness that only ever passes is not a harness. Each fake detector below is a failure this
    repo has actually shipped."""
    fails = []

    def const(toks, i):
        return 1.0

    def signish(toks, i):
        return 1.0 if len(_word(toks[i])) > 4 else -1.0

    def positional(toks, i):
        return float(i)

    def perfect(toks, i):
        return 0.0

    for fn, label, expect in ((const, "CONSTANT (no distinct values)", "distinct"),
                              (signish, "SIGN-QUANTISED (2 values)", "distinct")):
        try:
            check_diagnostics([[fn(["a", "bb", "ccc"], j) for j in range(3)] for _ in range(50)],
                              label)
            fails.append("%s was NOT caught" % label)
        except DiagnosticFailure as e:
            if expect.lower() not in str(e).lower() and "tie" not in str(e).lower():
                fails.append("%s caught with the wrong reason: %s" % (label, e))

    # a POSITION-only detector must be caught by the arg-max spread rule
    try:
        check_diagnostics([[positional(["a"] * 9, j) for j in range(9)] for _ in range(50)],
                          "POSITIONAL")
        fails.append("POSITIONAL detector was NOT caught")
    except DiagnosticFailure:
        pass

    # the positive control must reject a detector that cannot fire, and ACCEPT one that plainly
    # can. Fake items so the control has probes to build from.
    words = ["brown","green","red","blue","grey","zebra","comet","anvil","fjord","tuba"]
    fake = [{"sentence_original": "the quick %s fox jumps over lazy dogs today" % w,
             "anomaly_token_index": 2, "target": w} for w in words]
    odd = set(words[len(words)//2:])   # only the DONOR half is "odd" to the working detector
    try:
        positive_control(perfect, fake)
        fails.append("positive_control accepted a detector that never fires")
    except DiagnosticFailure:
        pass
    try:
        positive_control(lambda toks, i: 1.0 if _word(toks[i]) in odd else 0.0, fake)
    except DiagnosticFailure as e:
        fails.append("positive_control REJECTED a working detector: %s" % e)

    # a healthy score field must NOT raise
    rng = random.Random(3)
    try:
        check_diagnostics([[rng.random() for _ in range(9)] for _ in range(50)], "HEALTHY")
    except DiagnosticFailure as e:
        fails.append("a healthy detector was flagged: %s" % e)

    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print("   -", f)
        return 1
    print("self-test PASS: catches constant, sign-quantised, positional and never-firing detectors; "
          "accepts a working positive control and a healthy score field")
    return 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
